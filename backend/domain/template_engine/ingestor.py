"""
Universal Template Ingestor - Single entry point for all template creation.

Handles templates from:
- Manual UI entry
- LLM batch generation
- File import (JSON/YAML)

All paths produce the same Universal Schema format and go through
the same validation and storage pipeline.
"""

import re
import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.models.templates import QuestionTemplate, Misconception, TemplateOptionMisconception
from domain.template_engine.universal_schema import (
    UniversalTemplate,
    UniversalTemplateBatch,
    IngestResult,
    BatchIngestResult,
    GenerationTestResult,
    QuestionType,
    TemplateSource,
)
from domain.template_engine.lean_template_engine import VariableGenerator
from domain.template_engine.formula_sandbox import FormulaSandbox, get_sandbox
# Import new two-phase constraint generator
from domain.template_engine.variable_generator import variable_generator as new_variable_generator
from domain.template_engine.template_renderer import template_renderer

logger = logging.getLogger(__name__)


class UniversalTemplateIngestor:
    """
    Universal template ingestion service.
    
    Validates and stores templates regardless of their source.
    All templates are transformed into the internal DB format.
    
    Usage:
        ingestor = UniversalTemplateIngestor(db_session)
        result = await ingestor.ingest(template_dict, source="MANUAL")
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self._sandbox: Optional[FormulaSandbox] = None
    
    @property
    def sandbox(self) -> FormulaSandbox:
        """Lazy-load formula sandbox."""
        if self._sandbox is None:
            self._sandbox = get_sandbox()
        return self._sandbox
    
    async def ingest(
        self,
        template_data: Dict[str, Any],
        source: str = "MANUAL",
        created_by: str = "system"
    ) -> IngestResult:
        """
        Ingest a template in Universal Schema format.
        
        Args:
            template_data: Template data matching UniversalTemplate schema
            source: Creation source (MANUAL, LLM_BATCH, FILE_IMPORT)
            created_by: User or system that created the template
            
        Returns:
            IngestResult with success/failure status
        """
        errors: List[str] = []
        warnings: List[str] = []
        name = template_data.get('name', 'Unknown')
        
        # Step 1: Schema validation
        try:
            template = UniversalTemplate.model_validate(template_data)
            name = template.name
        except Exception as e:
            logger.warning(f"Schema validation failed for '{name}': {e}")
            return IngestResult(
                success=False,
                name=name,
                errors=[f"Schema validation failed: {str(e)}"]
            )
        
        # Step 2: Formula validation
        formula_result = self._validate_formulas(template)
        if not formula_result[0]:
            return IngestResult(
                success=False,
                name=name,
                errors=formula_result[1]
            )
        warnings.extend(formula_result[2])
        
        # Step 3: Test generation (generate 10 questions to verify)
        test_result = self._test_generation(template, count=10)
        if not test_result[0]:
            return IngestResult(
                success=False,
                name=name,
                errors=test_result[1],
                test_generations=test_result[2]
            )
        
        # Step 4: Transform to internal DB format
        try:
            db_template = self._transform_to_db_model(template, source, created_by)
        except Exception as e:
            logger.error(f"Failed to transform template '{name}': {e}")
            return IngestResult(
                success=False,
                name=name,
                errors=[f"Transform failed: {str(e)}"]
            )
        
        # Step 5: Store in database
        try:
            self.db.add(db_template)
            await self.db.commit()
            await self.db.refresh(db_template)
            
            # Process misconceptions if provided
            await self._process_misconceptions(db_template, template)
            
            logger.info(f"✅ Ingested template '{name}' (ID: {db_template.id})")
            
            return IngestResult(
                success=True,
                template_id=db_template.id,
                name=name,
                status=db_template.status,
                warnings=warnings,
                test_generations=test_result[2]
            )
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to store template '{name}': {e}")
            return IngestResult(
                success=False,
                name=name,
                errors=[f"Database error: {str(e)}"]
            )
    
    async def ingest_batch(
        self,
        batch_data: Dict[str, Any],
        source: str = "LLM_BATCH",
        created_by: str = "system"
    ) -> BatchIngestResult:
        """
        Ingest multiple templates at once.
        
        Args:
            batch_data: Batch data matching UniversalTemplateBatch schema
            source: Creation source
            created_by: User or system that created the templates
            
        Returns:
            BatchIngestResult with per-template results
        """
        # Validate batch structure
        try:
            batch = UniversalTemplateBatch.model_validate(batch_data)
        except Exception as e:
            return BatchIngestResult(
                total=0,
                successful=0,
                failed=1,
                results=[IngestResult(
                    success=False,
                    name="Batch",
                    errors=[f"Invalid batch format: {str(e)}"]
                )]
            )
        
        results: List[IngestResult] = []
        successful = 0
        failed = 0
        
        for template_dict in batch_data.get('templates', []):
            result = await self.ingest(template_dict, source, created_by)
            results.append(result)
            
            if result.success:
                successful += 1
            else:
                failed += 1
        
        return BatchIngestResult(
            total=len(results),
            successful=successful,
            failed=failed,
            results=results
        )
    
    async def preview_generation(
        self,
        template_data: Dict[str, Any],
        count: int = 5
    ) -> List[GenerationTestResult]:
        """
        Preview question generation without saving.
        
        Useful for testing templates before committing them.
        
        Args:
            template_data: Template data in Universal Schema format
            count: Number of questions to generate
            
        Returns:
            List of generated questions
        """
        try:
            template = UniversalTemplate.model_validate(template_data)
        except Exception as e:
            return [GenerationTestResult(
                success=False,
                error=f"Schema validation failed: {str(e)}"
            )]
        
        results = []
        for i in range(count):
            result = self._generate_single_question(template)
            results.append(result)
        
        return results
    
    def _validate_formulas(
        self,
        template: UniversalTemplate
    ) -> Tuple[bool, List[str], List[str]]:
        """
        Validate all formulas in computed variables are executable.
        
        Returns:
            Tuple of (is_valid, errors, warnings)
        """
        errors = []
        warnings = []
        
        computed = template.variables.computed or {}
        
        for var_name, var_def in computed.items():
            # Handle both string shorthand and dict format
            if isinstance(var_def, str):
                formula = var_def
            else:
                formula = var_def.formula if hasattr(var_def, 'formula') else var_def.get('formula', '')
            
            if not formula:
                errors.append(f"Empty formula for variable '{var_name}'")
                continue
            
            # Try to compile the formula
            try:
                compile(formula, '<string>', 'eval')
            except SyntaxError as e:
                errors.append(f"Syntax error in '{var_name}': {e}")
                continue
            
            # Check for function calls and validate they exist
            func_calls = self._extract_function_calls(formula)
            safe_funcs = VariableGenerator._get_safe_functions()
            
            for func in func_calls:
                if func not in safe_funcs:
                    # Check if it's a Python builtin allowed in sandbox
                    if func not in FormulaSandbox.SAFE_BUILTINS:
                        warnings.append(
                            f"Function '{func}' in variable '{var_name}' may not be available. "
                            f"Ensure it's a built-in or custom formula."
                        )
        
        # Validate constraints
        for constraint in template.variables.constraints:
            try:
                compile(constraint, '<string>', 'eval')
            except SyntaxError as e:
                errors.append(f"Syntax error in constraint '{constraint}': {e}")
        
        return (len(errors) == 0, errors, warnings)
    
    def _test_generation(
        self,
        template: UniversalTemplate,
        count: int = 10
    ) -> Tuple[bool, List[str], int]:
        """
        Generate test questions to verify template works.
        
        Returns:
            Tuple of (is_valid, errors, success_count)
        """
        errors = []
        generated = 0
        
        for i in range(count):
            result = self._generate_single_question(template)
            
            if result.success:
                generated += 1
            else:
                errors.append(f"Generation {i+1}: {result.error}")
        
        # Require at least 80% success rate
        min_required = int(count * 0.8)
        if generated < min_required:
            errors.append(f"Only {generated}/{count} generations succeeded (need {min_required})")
            return (False, errors, generated)
        
        return (True, [], generated)
    
    def _generate_single_question(
        self,
        template: UniversalTemplate
    ) -> GenerationTestResult:
        """
        Generate a single question from template.
        
        Uses two-phase constraint validation:
        1. Generate base variables → check base-only constraints
        2. Compute derived variables → check ALL constraints (including computed)
        
        This ensures constraints like "n1 < 300" on computed variables are properly enforced.
        """
        try:
            # Build variable schema for the new generator
            variable_schema = self._build_variable_schema_v2(template)
            
            # Use the new two-phase constraint generator
            gen_result = new_variable_generator.generate(variable_schema)
            
            if not gen_result.success:
                return GenerationTestResult(
                    success=False,
                    error=gen_result.error or "Failed to satisfy constraints"
                )
            
            variables = gen_result.variables
            
            # Render question
            question_text = ""
            if template.question_pattern:
                question_text = self._render_pattern(template.question_pattern, variables)
            elif template.parts:
                # For multi-part questions, join parts
                parts_text = []
                for part in template.parts:
                    rendered = self._render_pattern(part.pattern, variables)
                    if part.label:
                        parts_text.append(f"{part.label}: {rendered}")
                    else:
                        parts_text.append(rendered)
                question_text = "\n".join(parts_text)
            
            # Render options
            options = []
            correct_answer = None
            correct_answers = []  # For MCQ_MULTI
            
            for opt in template.options:
                rendered = self._render_pattern(opt.pattern, variables)
                options.append(rendered)
                
                # Check if correct
                is_correct = opt.is_correct
                if isinstance(is_correct, str):
                    # Dynamic correctness
                    try:
                        formula = is_correct.strip()
                        if formula.startswith("{{") and formula.endswith("}}"):
                            formula = formula[2:-2].strip()
                        
                        safe_funcs = VariableGenerator._get_safe_functions()
                        eval_context = {**variables, **safe_funcs}
                        is_correct = eval(formula, {"__builtins__": {}}, eval_context)
                    except Exception:
                        is_correct = False
                
                if is_correct:
                    correct_answer = rendered
                    correct_answers.append(rendered)
            
            # For MCQ_MULTI, use all correct answers
            if template.question_type.value == "MCQ_MULTI" and len(correct_answers) > 1:
                correct_answer = correct_answers
            
            # Check for duplicate options
            if len(options) != len(set(options)):
                return GenerationTestResult(
                    success=False,
                    error="Duplicate options detected"
                )
            
            return GenerationTestResult(
                success=True,
                question=question_text,
                options=options,
                correct_answer=correct_answer,
                variables=variables
            )
            
        except Exception as e:
            return GenerationTestResult(
                success=False,
                error=str(e)
            )
    
    def _build_variable_schema_v2(self, template: UniversalTemplate) -> Dict[str, Any]:
        """
        Build variable schema in the format expected by the new two-phase generator.
        
        Format:
        {
            "base": {...},
            "computed": {...},
            "constraints": [...],
            "custom_functions": {...}
        }
        """
        from domain.template_engine.function_library import get_library_functions
        
        schema = {
            "base": {},
            "computed": {},
            "constraints": template.variables.constraints or [],
            "custom_functions": {}
        }
        
        # Import functions from libraries first
        use_libraries = template.variables.use_libraries or []
        if use_libraries:
            library_funcs = get_library_functions(use_libraries)
            schema["custom_functions"].update(library_funcs)
        
        # Convert base variables
        # Note: BaseVariable model uses 'minimum'/'maximum', not 'min'/'max'
        for var_name, var_def in template.variables.base.items():
            prop = {"type": var_def.type}
            
            if var_def.enum:
                prop["enum"] = var_def.enum
            else:
                if var_def.minimum is not None:
                    prop["min"] = var_def.minimum
                if var_def.maximum is not None:
                    prop["max"] = var_def.maximum
            
            schema["base"][var_name] = prop
        
        # Convert computed variables
        computed = template.variables.computed or {}
        for var_name, var_def in computed.items():
            if isinstance(var_def, str):
                schema["computed"][var_name] = {"formula": var_def}
            else:
                # Handle Pydantic models and dicts differently
                if hasattr(var_def, 'formula'):
                    # It's a ComputedVariable Pydantic model
                    formula = var_def.formula
                    default = getattr(var_def, 'default', None)
                elif isinstance(var_def, dict):
                    # It's a raw dict
                    formula = var_def.get('formula', '')
                    default = var_def.get('default')
                else:
                    formula = str(var_def)
                    default = None
                
                schema["computed"][var_name] = {
                    "formula": formula,
                    "default": default
                }
        
        # Convert custom functions (these override library functions with same name)
        custom_funcs = template.variables.custom_functions or {}
        for func_name, func_def in custom_funcs.items():
            schema["custom_functions"][func_name] = {
                "params": func_def.params,
                "body": func_def.body
            }
        
        return schema
    
    def _build_variable_schema(self, template: UniversalTemplate) -> Dict[str, Any]:
        """Build JSON schema for VariableGenerator from Universal Schema."""
        schema = {
            "type": "object",
            "properties": {},
            "computed": {}
        }
        
        # Convert base variables
        for var_name, var_def in template.variables.base.items():
            prop = {"type": var_def.type}
            
            if var_def.enum:
                prop["enum"] = var_def.enum
            else:
                if var_def.minimum is not None:
                    prop["minimum"] = var_def.minimum
                if var_def.maximum is not None:
                    prop["maximum"] = var_def.maximum
            
            schema["properties"][var_name] = prop
        
        # Convert computed variables
        for var_name, var_def in template.variables.computed.items():
            if isinstance(var_def, str):
                formula = var_def
            else:
                formula = var_def.formula if hasattr(var_def, 'formula') else var_def.get('formula', '')
            
            schema["computed"][var_name] = {"formula": formula}
        
        return schema
    
    def _check_constraints(
        self,
        constraints: List[str],
        variables: Dict[str, Any]
    ) -> bool:
        """Check if variables satisfy all constraints."""
        safe_funcs = VariableGenerator._get_safe_functions()
        eval_context = {**variables, **safe_funcs}
        
        for constraint in constraints:
            try:
                result = eval(constraint, {"__builtins__": {}}, eval_context)
                if not result:
                    return False
            except Exception:
                return False
        
        return True
    
    def _render_pattern(
        self,
        pattern: str,
        variables: Dict[str, Any]
    ) -> str:
        """Render a pattern with variable substitution."""
        result = pattern
        
        # Handle {{variable}} and {{expression}} patterns
        def replace_var(match):
            expr = match.group(1).strip()
            try:
                # Try direct variable lookup first
                if expr in variables:
                    return str(variables[expr])
                
                # Otherwise, evaluate as expression
                safe_funcs = VariableGenerator._get_safe_functions()
                eval_context = {**variables, **safe_funcs}
                value = eval(expr, {"__builtins__": {}}, eval_context)
                return str(value)
            except Exception:
                return match.group(0)  # Return original if evaluation fails
        
        result = re.sub(r'\{\{([^}]+)\}\}', replace_var, result)
        return result
    
    def _transform_to_db_model(
        self,
        template: UniversalTemplate,
        source: str,
        created_by: str
    ) -> QuestionTemplate:
        """Transform Universal Schema to internal DB model."""
        
        # Build template_code from computed variables
        template_code_lines = []
        for var_name, var_def in template.variables.computed.items():
            if isinstance(var_def, str):
                formula = var_def
            else:
                formula = var_def.formula if hasattr(var_def, 'formula') else var_def.get('formula', '')
            template_code_lines.append(f"{var_name} = {formula}")
        template_code = "\n".join(template_code_lines) if template_code_lines else "pass"
        
        # Build answer_logic (find correct option pattern)
        correct_options = [opt for opt in template.options if opt.is_correct is True]
        if correct_options:
            answer_logic = correct_options[0].pattern
        else:
            # Dynamic correctness - use first option's formula
            answer_logic = "# Dynamic correctness based on variables"
        
        # Build option_patterns
        option_patterns = [
            {
                "pattern": opt.pattern,
                "is_correct": opt.is_correct if isinstance(opt.is_correct, bool) else f"eval:{opt.is_correct}",
                "misconception_id": opt.misconception_id,
                "student_thinking": opt.student_thinking,
                "remediation": opt.remediation
            }
            for opt in template.options
        ]
        
        # Build variable_schema in internal format
        variable_schema = {
            "type": "object",
            "properties": {
                var_name: {
                    "type": var_def.type,
                    **({"enum": var_def.enum} if var_def.enum else {}),
                    **({"minimum": var_def.minimum} if var_def.minimum else {}),
                    **({"maximum": var_def.maximum} if var_def.maximum else {}),
                }
                for var_name, var_def in template.variables.base.items()
            },
            "computed": {
                var_name: {
                    "formula": var_def.formula if hasattr(var_def, 'formula') else var_def
                } if isinstance(var_def, str) else {
                    "formula": var_def.formula if hasattr(var_def, 'formula') else var_def.get('formula', '')
                }
                for var_name, var_def in template.variables.computed.items()
            },
            "constraints": template.variables.constraints
        }
        
        # Build solution pattern
        solution_pattern = None
        if template.solution and template.solution.steps:
            solution_steps = "\n".join([
                f"Step {step.number}: {step.text}"
                for step in template.solution.steps
            ])
            solution_pattern = solution_steps
        
        # Build hint pattern
        hint_pattern = None
        if template.hints:
            hint_pattern = "\n---\n".join(template.hints)
        
        # Build diagram config
        diagram_config = None
        if template.diagram:
            diagram_config = {
                "type": template.diagram.type,
                "parameters": template.diagram.parameters,
                "custom_svg": template.diagram.custom_svg
            }
        
        # Get question pattern
        question_pattern = template.question_pattern or ""
        if template.parts:
            # For multi-part questions, store parts in a structured format
            parts_data = [
                {
                    "type": part.type,
                    "label": part.label,
                    "pattern": part.pattern,
                    "is_true": part.is_true,
                    "options": [
                        {"pattern": opt.pattern, "is_correct": opt.is_correct}
                        for opt in (part.options or [])
                    ] if part.options else None
                }
                for part in template.parts
            ]
            question_pattern = json.dumps({
                "type": template.question_type.value,
                "parts": parts_data
            })
        
        # Create DB model
        db_template = QuestionTemplate(
            concept_id=template.concept_id,
            template_code=template_code,
            question_pattern=question_pattern,
            variable_schema=variable_schema,
            answer_logic=answer_logic,
            option_patterns=option_patterns,
            solution_pattern=solution_pattern,
            hint_pattern=hint_pattern,
            diagram_config=diagram_config,
            difficulty=template.difficulty,
            bloom_level=template.bloom_level,
            estimated_time=template.estimated_time,
            status=template.status.value if source == TemplateSource.MANUAL.value else "DRAFT",
            validation_passed=True,
            created_by=created_by
        )
        
        return db_template
    
    async def _process_misconceptions(
        self,
        db_template: QuestionTemplate,
        template: UniversalTemplate
    ) -> None:
        """Process and link misconceptions for template options."""
        for i, opt in enumerate(template.options):
            if opt.misconception_id and not opt.is_correct:
                # Find or create misconception
                result = await self.db.execute(
                    select(Misconception).where(Misconception.code == opt.misconception_id)
                )
                misconception = result.scalar_one_or_none()
                
                if not misconception:
                    # Create a new misconception entry
                    misconception = Misconception(
                        code=opt.misconception_id,
                        title=opt.misconception_id.replace("_", " ").title(),
                        description=opt.student_thinking or f"Misconception: {opt.misconception_id}",
                        teaching_point=opt.remediation or "Review the concept carefully.",
                        subject="math",  # Default to math for now
                        concept_tags=[template.concept_id]
                    )
                    self.db.add(misconception)
                    await self.db.flush()  # Get ID without committing
                
                # Link misconception to template option
                link = TemplateOptionMisconception(
                    template_id=db_template.id,
                    misconception_id=misconception.id,
                    option_index=i,
                    custom_explanation=opt.student_thinking
                )
                self.db.add(link)
        
        await self.db.commit()
    
    def _extract_function_calls(self, formula: str) -> List[str]:
        """Extract function names from formula string."""
        return re.findall(r'(\w+)\s*\(', formula)


# ============================================================
# SYNC VERSION FOR COMPATIBILITY
# ============================================================

class UniversalTemplateIngestorSync:
    """
    Synchronous version of the ingestor for non-async contexts.
    
    Used by CLI tools and batch jobs.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self._sandbox: Optional[FormulaSandbox] = None
    
    @property
    def sandbox(self) -> FormulaSandbox:
        if self._sandbox is None:
            self._sandbox = get_sandbox()
        return self._sandbox
    
    def ingest(
        self,
        template_data: Dict[str, Any],
        source: str = "MANUAL",
        created_by: str = "system"
    ) -> IngestResult:
        """Synchronous template ingestion."""
        # Reuse validation logic from async version
        errors: List[str] = []
        warnings: List[str] = []
        name = template_data.get('name', 'Unknown')
        
        try:
            template = UniversalTemplate.model_validate(template_data)
            name = template.name
        except Exception as e:
            return IngestResult(
                success=False,
                name=name,
                errors=[f"Schema validation failed: {str(e)}"]
            )
        
        # Build async-like methods inline for sync execution
        # (Simplified - just validates and stores)
        
        # Formula validation
        formula_errors, formula_warnings = self._validate_formulas_sync(template)
        if formula_errors:
            return IngestResult(
                success=False,
                name=name,
                errors=formula_errors
            )
        warnings.extend(formula_warnings)
        
        # Test generation
        test_errors, test_count = self._test_generation_sync(template)
        if test_errors:
            return IngestResult(
                success=False,
                name=name,
                errors=test_errors,
                test_generations=test_count
            )
        
        # Transform and store
        try:
            db_template = self._transform_to_db_model_sync(template, source, created_by)
            self.db.add(db_template)
            self.db.commit()
            self.db.refresh(db_template)
            
            return IngestResult(
                success=True,
                template_id=db_template.id,
                name=name,
                status=db_template.status,
                warnings=warnings,
                test_generations=test_count
            )
        except Exception as e:
            self.db.rollback()
            return IngestResult(
                success=False,
                name=name,
                errors=[f"Database error: {str(e)}"]
            )
    
    def _validate_formulas_sync(self, template: UniversalTemplate) -> Tuple[List[str], List[str]]:
        """Sync formula validation."""
        errors = []
        warnings = []
        
        computed = template.variables.computed or {}
        
        for var_name, var_def in computed.items():
            if isinstance(var_def, str):
                formula = var_def
            else:
                formula = var_def.formula if hasattr(var_def, 'formula') else var_def.get('formula', '')
            
            try:
                compile(formula, '<string>', 'eval')
            except SyntaxError as e:
                errors.append(f"Syntax error in '{var_name}': {e}")
        
        return (errors, warnings)
    
    def _test_generation_sync(self, template: UniversalTemplate, count: int = 10) -> Tuple[List[str], int]:
        """
        Sync test generation using two-phase constraint validation.
        """
        try:
            # Build schema for the new two-phase generator
            schema = {
                "base": {},
                "computed": {},
                "constraints": template.variables.constraints or []
            }
            
            # Convert base variables
            # Note: BaseVariable model uses 'minimum'/'maximum', not 'min'/'max'
            for var_name, var_def in template.variables.base.items():
                prop = {"type": var_def.type}
                if var_def.enum:
                    prop["enum"] = var_def.enum
                else:
                    if var_def.minimum is not None:
                        prop["min"] = var_def.minimum
                    if var_def.maximum is not None:
                        prop["max"] = var_def.maximum
                schema["base"][var_name] = prop
            
            # Convert computed variables
            computed = template.variables.computed or {}
            for var_name, var_def in computed.items():
                if isinstance(var_def, str):
                    schema["computed"][var_name] = {"formula": var_def}
                else:
                    formula = var_def.formula if hasattr(var_def, 'formula') else var_def.get('formula', '')
                    schema["computed"][var_name] = {"formula": formula}
            
            # Use the new two-phase constraint generator
            generated = 0
            for _ in range(count):
                result = new_variable_generator.generate(schema)
                if result.success:
                    generated += 1
            
            if generated < count * 0.8:
                return ([f"Only {generated}/{count} generations succeeded"], generated)
            
            return ([], generated)
        except Exception as e:
            return ([str(e)], 0)
    
    def _build_variable_schema_sync(self, template: UniversalTemplate) -> Dict[str, Any]:
        """Build variable schema for sync context."""
        schema = {
            "type": "object",
            "properties": {},
            "computed": {}
        }
        
        for var_name, var_def in template.variables.base.items():
            prop = {"type": var_def.type}
            if var_def.enum:
                prop["enum"] = var_def.enum
            else:
                if var_def.minimum is not None:
                    prop["minimum"] = var_def.minimum
                if var_def.maximum is not None:
                    prop["maximum"] = var_def.maximum
            schema["properties"][var_name] = prop
        
        for var_name, var_def in template.variables.computed.items():
            if isinstance(var_def, str):
                formula = var_def
            else:
                formula = var_def.formula if hasattr(var_def, 'formula') else var_def.get('formula', '')
            schema["computed"][var_name] = {"formula": formula}
        
        return schema
    
    def _transform_to_db_model_sync(
        self,
        template: UniversalTemplate,
        source: str,
        created_by: str
    ) -> QuestionTemplate:
        """Transform to DB model (sync version)."""
        # Same logic as async version
        template_code_lines = []
        for var_name, var_def in template.variables.computed.items():
            if isinstance(var_def, str):
                formula = var_def
            else:
                formula = var_def.formula if hasattr(var_def, 'formula') else var_def.get('formula', '')
            template_code_lines.append(f"{var_name} = {formula}")
        template_code = "\n".join(template_code_lines) if template_code_lines else "pass"
        
        correct_options = [opt for opt in template.options if opt.is_correct is True]
        answer_logic = correct_options[0].pattern if correct_options else "# Dynamic"
        
        option_patterns = [
            {
                "pattern": opt.pattern,
                "is_correct": opt.is_correct if isinstance(opt.is_correct, bool) else f"eval:{opt.is_correct}",
                "misconception_id": opt.misconception_id,
            }
            for opt in template.options
        ]
        
        variable_schema = {
            "type": "object",
            "properties": {
                var_name: {
                    "type": var_def.type,
                    **({"enum": var_def.enum} if var_def.enum else {}),
                    **({"minimum": var_def.minimum} if var_def.minimum else {}),
                    **({"maximum": var_def.maximum} if var_def.maximum else {}),
                }
                for var_name, var_def in template.variables.base.items()
            },
            "computed": {
                var_name: {"formula": var_def.formula if hasattr(var_def, 'formula') else var_def}
                if isinstance(var_def, str) else {"formula": var_def.formula if hasattr(var_def, 'formula') else var_def.get('formula', '')}
                for var_name, var_def in template.variables.computed.items()
            },
            "constraints": template.variables.constraints
        }
        
        question_pattern = template.question_pattern or ""
        if template.parts:
            parts_data = [
                {"type": p.type, "label": p.label, "pattern": p.pattern}
                for p in template.parts
            ]
            question_pattern = json.dumps({"type": template.question_type.value, "parts": parts_data})
        
        return QuestionTemplate(
            concept_id=template.concept_id,
            template_code=template_code,
            question_pattern=question_pattern,
            variable_schema=variable_schema,
            answer_logic=answer_logic,
            option_patterns=option_patterns,
            difficulty=template.difficulty,
            bloom_level=template.bloom_level,
            estimated_time=template.estimated_time,
            status="DRAFT",
            validation_passed=True,
            created_by=created_by
        )

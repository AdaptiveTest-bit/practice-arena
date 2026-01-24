"""
Function Library API endpoints.

Allows content writers to:
1. List available function libraries
2. Get function documentation
3. Upload custom function libraries
4. Test functions before using in templates
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field, field_validator
from typing import Dict, Any, List, Optional
import re

from domain.template_engine.function_library import (
    function_library_registry,
    FunctionLibrary,
    FunctionDefinition,
    get_library_functions
)


# Pydantic models for API
class FunctionDefInput(BaseModel):
    """Input model for a single function definition."""
    params: List[str] = Field(..., description="Parameter names")
    body: str = Field(..., description="Python expression (single line)")
    description: Optional[str] = Field(None, description="Human-readable description")
    examples: List[str] = Field(default_factory=list, description="Usage examples")
    
    @field_validator('params')
    @classmethod
    def validate_params(cls, v):
        for param in v:
            if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', param):
                raise ValueError(f"Invalid parameter name: {param}")
        return v
    
    @field_validator('body')
    @classmethod
    def validate_body(cls, v):
        # Basic validation - body must be a valid Python expression
        try:
            compile(v, '<string>', 'eval')
        except SyntaxError as e:
            raise ValueError(f"Invalid expression: {e}")
        return v


class LibraryInput(BaseModel):
    """Input model for creating a function library."""
    name: str = Field(..., min_length=1, max_length=50, description="Library name (snake_case)")
    description: str = Field(..., description="Library description")
    subject: str = Field(..., description="Subject area (math, physics, chemistry, etc.)")
    functions: Dict[str, FunctionDefInput] = Field(..., min_length=1, description="Function definitions")
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not re.match(r'^[a-z][a-z0-9_]*$', v):
            raise ValueError("Library name must be snake_case (lowercase letters, numbers, underscores)")
        return v


class FunctionTestRequest(BaseModel):
    """Request model for testing a function."""
    body: str = Field(..., description="Function body expression")
    params: List[str] = Field(..., description="Parameter names")
    test_values: Dict[str, Any] = Field(..., description="Test values for parameters")


class FunctionTestResponse(BaseModel):
    """Response model for function test."""
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None
    execution_time_ms: float = 0


class LibraryResponse(BaseModel):
    """Response model for library info."""
    name: str
    description: str
    subject: str
    function_count: int
    functions: Dict[str, Dict[str, Any]]


# Create router
router = APIRouter(prefix="/api/function-libraries", tags=["function-libraries"])


@router.get("", response_model=List[str])
async def list_libraries():
    """
    List all available function libraries.
    
    Returns names of all registered libraries that can be used in templates.
    """
    return function_library_registry.list_libraries()


@router.get("/{library_name}", response_model=LibraryResponse)
async def get_library(library_name: str):
    """
    Get details of a specific function library.
    
    Returns all functions in the library with their documentation.
    """
    library = function_library_registry.get_library(library_name)
    if not library:
        raise HTTPException(status_code=404, detail=f"Library '{library_name}' not found")
    
    functions = {}
    for func_name, func_def in library.functions.items():
        functions[func_name] = {
            "params": func_def.params,
            "body": func_def.body,
            "description": func_def.description,
            "examples": func_def.examples
        }
    
    return LibraryResponse(
        name=library.name,
        description=library.description,
        subject=library.subject,
        function_count=len(library.functions),
        functions=functions
    )


@router.get("/{library_name}/docs")
async def get_library_documentation(library_name: str):
    """
    Get markdown documentation for a library.
    
    Returns formatted documentation suitable for display.
    """
    docs = function_library_registry.get_library_documentation(library_name)
    if not docs:
        raise HTTPException(status_code=404, detail=f"Library '{library_name}' not found")
    
    return {"documentation": docs}


@router.post("", response_model=LibraryResponse)
async def create_library(library_input: LibraryInput):
    """
    Create a new function library.
    
    Content writers can upload their own reusable function libraries.
    Libraries are validated before being registered.
    
    **Security:** Function bodies are validated to only allow safe operations.
    """
    # Check if library already exists
    if function_library_registry.get_library(library_input.name):
        raise HTTPException(
            status_code=409, 
            detail=f"Library '{library_input.name}' already exists. Use PUT to update."
        )
    
    # Create library
    library = FunctionLibrary(
        name=library_input.name,
        description=library_input.description,
        subject=library_input.subject
    )
    
    # Add functions with validation
    for func_name, func_def in library_input.functions.items():
        # Validate function name
        if not re.match(r'^[a-z_][a-z0-9_]*$', func_name):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid function name: {func_name}. Must be snake_case."
            )
        
        # Validate function body is safe (no imports, exec, eval, etc.)
        dangerous_patterns = [
            r'\bimport\b', r'\bexec\b', r'\beval\b', r'\bopen\b',
            r'\b__\w+__\b', r'\bos\b', r'\bsys\b', r'\bsubprocess\b'
        ]
        for pattern in dangerous_patterns:
            if re.search(pattern, func_def.body):
                raise HTTPException(
                    status_code=400,
                    detail=f"Function '{func_name}' contains disallowed operation"
                )
        
        library.functions[func_name] = FunctionDefinition(
            name=func_name,
            params=func_def.params,
            body=func_def.body,
            description=func_def.description,
            examples=func_def.examples
        )
    
    # Test all functions compile correctly
    for func_name, func_def in library.functions.items():
        try:
            # Test compile
            compile(func_def.body, '<string>', 'eval')
        except SyntaxError as e:
            raise HTTPException(
                status_code=400,
                detail=f"Function '{func_name}' has invalid syntax: {e}"
            )
    
    # Register the library
    function_library_registry.register_library(library)
    
    # Return response
    functions = {}
    for func_name, func_def in library.functions.items():
        functions[func_name] = {
            "params": func_def.params,
            "body": func_def.body,
            "description": func_def.description,
            "examples": func_def.examples
        }
    
    return LibraryResponse(
        name=library.name,
        description=library.description,
        subject=library.subject,
        function_count=len(library.functions),
        functions=functions
    )


@router.post("/test-function", response_model=FunctionTestResponse)
async def test_function(request: FunctionTestRequest):
    """
    Test a function expression with given values.
    
    Useful for content writers to validate their custom functions
    before adding them to a library or template.
    """
    import time
    import math
    from domain.template_engine.safe_functions import safe_functions
    
    start_time = time.time()
    
    # Safe builtins for expressions
    SAFE_BUILTINS = {
        'abs': abs, 'min': min, 'max': max, 'sum': sum, 'len': len,
        'int': int, 'float': float, 'str': str, 'bool': bool,
        'round': round, 'pow': pow, 'divmod': divmod,
        'range': range, 'list': list, 'tuple': tuple, 'set': set,
        'sorted': sorted, 'reversed': reversed, 'enumerate': enumerate, 'zip': zip,
        'True': True, 'False': False, 'None': None,
        'all': all, 'any': any, 'filter': filter, 'map': map,
    }
    
    try:
        # Build namespace with safe functions, safe builtins, and parameters
        namespace = {**SAFE_BUILTINS, **safe_functions.get_all()}
        
        # Add math module functions
        namespace['math'] = math
        
        for param, value in request.test_values.items():
            if param in request.params:
                namespace[param] = value
        
        # Execute the expression with builtins in globals to support generator expressions
        result = eval(request.body, {"__builtins__": SAFE_BUILTINS}, namespace)
        
        execution_time = (time.time() - start_time) * 1000
        
        return FunctionTestResponse(
            success=True,
            result=result,
            execution_time_ms=round(execution_time, 3)
        )
        
    except Exception as e:
        execution_time = (time.time() - start_time) * 1000
        return FunctionTestResponse(
            success=False,
            error=str(e),
            execution_time_ms=round(execution_time, 3)
        )


@router.get("/by-subject/{subject}", response_model=List[str])
async def get_libraries_by_subject(subject: str):
    """
    Get all libraries for a specific subject.
    
    Useful for filtering libraries by subject area.
    """
    libraries = function_library_registry.get_libraries_by_subject(subject)
    return [lib.name for lib in libraries]


@router.get("/functions/search")
async def search_functions(query: str):
    """
    Search for functions across all libraries.
    
    Searches function names and descriptions.
    """
    results = []
    query_lower = query.lower()
    
    for lib_name in function_library_registry.list_libraries():
        library = function_library_registry.get_library(lib_name)
        if library:
            for func_name, func_def in library.functions.items():
                # Search in name
                if query_lower in func_name.lower():
                    results.append({
                        "library": lib_name,
                        "function": func_name,
                        "params": func_def.params,
                        "body": func_def.body,
                        "description": func_def.description,
                        "match_type": "name"
                    })
                # Search in description
                elif func_def.description and query_lower in func_def.description.lower():
                    results.append({
                        "library": lib_name,
                        "function": func_name,
                        "params": func_def.params,
                        "body": func_def.body,
                        "description": func_def.description,
                        "match_type": "description"
                    })
    
    return {"query": query, "results": results, "count": len(results)}


@router.delete("/{library_name}")
async def delete_library(library_name: str):
    """
    Delete a custom library.
    
    Note: Built-in libraries cannot be deleted.
    """
    builtin_libraries = [
        "math_helpers", "number_theory", "geometry_helpers",
        "chemistry_basics", "physics_basics", "percentage_ratio"
    ]
    
    if library_name in builtin_libraries:
        raise HTTPException(
            status_code=403,
            detail=f"Cannot delete built-in library '{library_name}'"
        )
    
    library = function_library_registry.get_library(library_name)
    if not library:
        raise HTTPException(status_code=404, detail=f"Library '{library_name}' not found")
    
    # Remove from registry
    del function_library_registry._libraries[library_name]
    
    return {"message": f"Library '{library_name}' deleted successfully"}

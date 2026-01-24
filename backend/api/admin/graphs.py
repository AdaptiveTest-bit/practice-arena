"""
Admin API endpoints for Concept Graph and Coverage Management.

Phase B Implementation per CONTENT_MANAGEMENT_ARCHITECTURE.md:
- Graph management endpoints (/api/admin/graphs/*)
- Coverage report endpoints (/api/admin/coverage/*)
- Taxonomy read endpoints (/api/admin/taxonomy/*)

These extend the existing template admin API (api/admin/templates.py).
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Path
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from core.database import get_db
from db.models import QuestionTemplate
from domain.adaptation.concept_graph import ConceptGraph
from domain.content_validation import TaxonomyValidator


# Pydantic models for Graph API
class ConceptNodeResponse(BaseModel):
    """Response model for a concept node in the graph."""
    concept_id: str
    name: str
    description: Optional[str] = None
    bloom_targets: List[str]
    difficulty_default: int
    template_count: int = 0
    published_count: int = 0
    draft_count: int = 0
    status: str = "no_content"  # no_content, draft, published


class ConceptEdgeResponse(BaseModel):
    """Response model for a concept edge (prerequisite)."""
    from_concept: str
    to_concept: str
    kind: str  # prerequisite, co_requisite
    reason: Optional[str] = None


class ConceptGraphResponse(BaseModel):
    """Full concept graph response."""
    subject: str
    grade: int
    chapter_id: str
    chapter_name: str
    description: Optional[str] = None
    total_concepts: int
    total_edges: int
    nodes: List[ConceptNodeResponse]
    edges: List[ConceptEdgeResponse]


class CoverageGapItem(BaseModel):
    """A single coverage gap item."""
    concept_id: str
    concept_name: str
    published_count: int
    draft_count: int
    needed: int
    severity: str  # critical, warning, ok


class CoverageReportResponse(BaseModel):
    """Full coverage report for a chapter."""
    subject: str
    grade: int
    chapter_id: str
    total_concepts: int
    concepts_with_content: int
    concepts_without_content: int
    total_templates: int
    published_templates: int
    draft_templates: int
    coverage_percentage: float
    ready_to_publish: bool
    gaps: List[CoverageGapItem]


class TaxonomyConceptResponse(BaseModel):
    """Response model for a taxonomy concept."""
    id: str
    name: str
    grades: List[int]
    bloom_level: str
    difficulty_range: List[int]
    prerequisites: List[str] = []


class TaxonomyResponse(BaseModel):
    """Full taxonomy response for a subject."""
    subject: str
    version: int
    total_concepts: int
    concepts: List[TaxonomyConceptResponse]


# Create router for graphs/coverage
graphs_router = APIRouter(prefix="/graphs", tags=["admin-graphs"])
coverage_router = APIRouter(prefix="/coverage", tags=["admin-coverage"])
taxonomy_router = APIRouter(prefix="/taxonomy", tags=["admin-taxonomy"])


# =============================================================================
# Graph Management Endpoints
# =============================================================================

@graphs_router.get("/{subject}/{grade}/{chapter}", response_model=ConceptGraphResponse)
async def get_concept_graph(
    subject: str = Path(..., description="Subject (e.g., math)"),
    grade: int = Path(..., ge=1, le=12, description="Grade level 1-12"),
    chapter: str = Path(..., description="Chapter key (e.g., factors_multiples)"),
    db: Session = Depends(get_db)
):
    """
    Get the concept graph for a chapter.
    
    Returns the DAG of concepts with prerequisite edges, enriched with
    template counts from the database.
    
    Per Architecture Doc Section 3.1:
    - Node = micro-concept (atomic learning unit)
    - Edge = dependency (prerequisite relationship)
    """
    try:
        graph = ConceptGraph.load(subject, grade, chapter)
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Graph not found: {subject}/class{grade}/{chapter}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error loading graph: {str(e)}"
        )
    
    MIN_TEMPLATES_FOR_PUBLISH = 5  # Per architecture spec
    
    # Build enriched nodes with template counts
    nodes = []
    for concept_id, node in graph.nodes.items():
        # Count templates by status
        published_count = db.query(QuestionTemplate).filter(
            QuestionTemplate.concept_id == concept_id,
            QuestionTemplate.status == "PUBLISHED"
        ).count()
        
        draft_count = db.query(QuestionTemplate).filter(
            QuestionTemplate.concept_id == concept_id,
            QuestionTemplate.status.in_(["DRAFT", "REVIEW", "APPROVED"])
        ).count()
        
        total = published_count + draft_count
        
        # Determine status per architecture spec
        if published_count >= MIN_TEMPLATES_FOR_PUBLISH:
            status = "published"
        elif total > 0:
            status = "draft"
        else:
            status = "no_content"
        
        nodes.append(ConceptNodeResponse(
            concept_id=concept_id,
            name=node.description or concept_id.split('.')[-1],
            description=node.description,
            bloom_targets=node.bloom_targets,
            difficulty_default=node.difficulty_default,
            template_count=total,
            published_count=published_count,
            draft_count=draft_count,
            status=status
        ))
    
    # Build edges
    edges = [
        ConceptEdgeResponse(
            from_concept=edge.from_concept,
            to_concept=edge.to_concept,
            kind=edge.kind,
            reason=edge.reason
        )
        for edge in graph.edges
    ]
    
    return ConceptGraphResponse(
        subject=subject,
        grade=grade,
        chapter_id=chapter,
        chapter_name=graph.chapter_id,
        description=getattr(graph, 'description', None),
        total_concepts=len(nodes),
        total_edges=len(edges),
        nodes=nodes,
        edges=edges
    )


# Pydantic models for Graph Update
class ConceptNodeInput(BaseModel):
    """Input model for creating/updating a concept node."""
    concept_id: Optional[str] = Field(None, description="Full concept ID")
    id: Optional[str] = Field(None, description="Alternative field for concept_id")
    name: Optional[str] = None
    label: Optional[str] = Field(None, description="Alternative for name (frontend uses this)")
    description: Optional[str] = None
    bloom_targets: List[str] = Field(default_factory=lambda: ["understand"])
    bloomTargets: Optional[List[str]] = Field(None, description="CamelCase alternative for bloom_targets")
    difficulty_default: int = 2
    difficultyDefault: Optional[int] = Field(None, description="CamelCase alternative for difficulty_default")
    position: Optional[dict] = Field(None, description="UI position {x, y}")
    
    class Config:
        extra = "allow"  # Allow extra fields like conceptId, templateCount, status


class ConceptEdgeInput(BaseModel):
    """Input model for creating/updating an edge."""
    from_concept: Optional[str] = Field(None, alias="from")
    to_concept: Optional[str] = Field(None, alias="to")
    source: Optional[str] = None  # Alternative for from_concept
    target: Optional[str] = None  # Alternative for to_concept
    kind: str = "prerequisite"
    reason: Optional[str] = None


class GraphUpdateRequest(BaseModel):
    """Request body for updating a concept graph."""
    nodes: List[ConceptNodeInput]
    edges: List[ConceptEdgeInput]


class GraphUpdateResponse(BaseModel):
    """Response after updating a graph."""
    success: bool
    message: str
    path: Optional[str] = None
    nodes_count: int
    edges_count: int


@graphs_router.put("/{subject}/{grade}/{chapter}", response_model=GraphUpdateResponse)
async def save_concept_graph(
    request: GraphUpdateRequest,
    subject: str = Path(..., description="Subject (e.g., math)"),
    grade: int = Path(..., ge=1, le=12, description="Grade level 1-12"),
    chapter: str = Path(..., description="Chapter key (e.g., factors_multiples)"),
    db: Session = Depends(get_db)
):
    """
    Save/update the concept graph for a chapter.
    
    Creates or updates the YAML file at:
    backend/config/content/graphs/{subject}/class{grade}/{chapter}.yaml
    
    This enables content writers to add/modify concepts via Admin UI.
    """
    try:
        # Try to load existing graph or create new one
        try:
            graph = ConceptGraph.load(subject, grade, chapter)
        except FileNotFoundError:
            graph = ConceptGraph.create_new(subject, grade, chapter)
        
        # Convert request to dict format expected by update_from_dict
        update_data = {
            "nodes": [],
            "edges": []
        }
        
        for node in request.nodes:
            concept_id = node.concept_id or node.id
            if not concept_id:
                continue
            update_data["nodes"].append({
                "concept_id": concept_id,
                "description": node.description or node.name or concept_id.split(".")[-1],
                "bloom_targets": node.bloom_targets,
                "difficulty_default": node.difficulty_default,
            })
        
        for edge in request.edges:
            from_c = edge.from_concept or edge.source
            to_c = edge.to_concept or edge.target
            if not from_c or not to_c:
                continue
            update_data["edges"].append({
                "from": from_c,
                "to": to_c,
                "kind": edge.kind,
                "reason": edge.reason or "",
            })
        
        # Update graph
        graph.update_from_dict(update_data)
        
        # Validate - check for cycles
        try:
            graph.get_topological_order()
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid graph: cycle detected or invalid structure. {str(e)}"
            )
        
        # Save to YAML
        saved_path = graph.save()
        
        return GraphUpdateResponse(
            success=True,
            message=f"Graph saved successfully with {len(graph.nodes)} concepts and {len(graph.edges)} edges",
            path=str(saved_path),
            nodes_count=len(graph.nodes),
            edges_count=len(graph.edges)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error saving graph: {str(e)}"
        )


@graphs_router.post("/{subject}/{grade}/{chapter}/nodes", response_model=Dict[str, Any])
async def add_concept_node(
    node: ConceptNodeInput,
    subject: str = Path(...),
    grade: int = Path(..., ge=1, le=12),
    chapter: str = Path(...)
):
    """
    Add a single concept node to an existing graph.
    """
    try:
        graph = ConceptGraph.load(subject, grade, chapter)
    except FileNotFoundError:
        graph = ConceptGraph.create_new(subject, grade, chapter)
    
    concept_id = node.concept_id or node.id
    if not concept_id:
        raise HTTPException(status_code=400, detail="concept_id is required")
    
    try:
        graph.add_node(
            concept_id=concept_id,
            bloom_targets=node.bloom_targets,
            difficulty_default=node.difficulty_default,
            description=node.description or ""
        )
        graph.save()
        
        return {
            "success": True,
            "concept_id": concept_id,
            "message": f"Node {concept_id} added successfully"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@graphs_router.delete("/{subject}/{grade}/{chapter}/nodes/{concept_id:path}")
async def delete_concept_node(
    subject: str = Path(...),
    grade: int = Path(..., ge=1, le=12),
    chapter: str = Path(...),
    concept_id: str = Path(...)
):
    """
    Delete a concept node from the graph.
    """
    try:
        graph = ConceptGraph.load(subject, grade, chapter)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Graph not found")
    
    if graph.remove_node(concept_id):
        graph.save()
        return {"success": True, "message": f"Node {concept_id} removed"}
    else:
        raise HTTPException(status_code=404, detail=f"Node {concept_id} not found")


@graphs_router.get("/{subject}/{grade}/{chapter}/ready-concepts")
async def get_ready_concepts(
    subject: str = Path(..., description="Subject"),
    grade: int = Path(..., ge=1, le=12, description="Grade level"),
    chapter: str = Path(..., description="Chapter key"),
    student_id: Optional[str] = Query(None, description="Student ID for mastery check"),
    db: Session = Depends(get_db)
):
    """
    Get concepts that are ready to practice.
    
    Per Architecture Doc Section 4.1 (Frontier Algorithm):
    - All STRICT prerequisites must be MASTERED
    - Concept must NOT already be MASTERED
    - Ordered by difficulty_tier
    """
    try:
        graph = ConceptGraph.load(subject, grade, chapter)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Graph not found")
    
    # Get ready concepts (those with no prerequisites or all prerequisites mastered)
    if student_id:
        ready = graph.get_ready_concepts(student_id)
    else:
        # Without student ID, return concepts with no prerequisites (entry points)
        ready = [
            concept_id for concept_id in graph.nodes
            if not graph.get_prerequisites(concept_id)
        ]
    
    return {
        "subject": subject,
        "grade": grade,
        "chapter": chapter,
        "ready_concepts": ready,
        "count": len(ready)
    }


@graphs_router.get("/{subject}/{grade}/{chapter}/prerequisites/{concept_id}")
async def get_concept_prerequisites(
    subject: str,
    grade: int,
    chapter: str,
    concept_id: str = Path(..., description="Full concept ID")
):
    """
    Get prerequisites for a specific concept.
    """
    try:
        graph = ConceptGraph.load(subject, grade, chapter)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Graph not found")
    
    prerequisites = graph.get_prerequisites(concept_id)
    
    return {
        "concept_id": concept_id,
        "prerequisites": prerequisites,
        "count": len(prerequisites)
    }


@graphs_router.get("/{subject}/{grade}/{chapter}/dependents/{concept_id}")
async def get_concept_dependents(
    subject: str,
    grade: int,
    chapter: str,
    concept_id: str = Path(..., description="Full concept ID")
):
    """
    Get concepts that depend on this concept (reverse lookup).
    """
    try:
        graph = ConceptGraph.load(subject, grade, chapter)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Graph not found")
    
    dependents = graph.get_dependents(concept_id)
    
    return {
        "concept_id": concept_id,
        "dependents": dependents,
        "count": len(dependents)
    }


# =============================================================================
# Coverage Report Endpoints
# =============================================================================

@coverage_router.get("/{subject}/{grade}/{chapter}", response_model=CoverageReportResponse)
async def get_coverage_report(
    subject: str = Path(..., description="Subject"),
    grade: int = Path(..., ge=1, le=12, description="Grade level"),
    chapter: str = Path(..., description="Chapter key"),
    db: Session = Depends(get_db)
):
    """
    Get template coverage report for a chapter.
    
    Per Architecture Doc Section 12.2:
    - Minimum 10 templates per concept recommended
    - Minimum 5 templates required for publishing
    - Must cover all specified Bloom levels
    """
    try:
        graph = ConceptGraph.load(subject, grade, chapter)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Graph not found")
    
    MIN_TEMPLATES = 5  # Per architecture spec (Section 5.5 Validation Rules)
    RECOMMENDED_TEMPLATES = 10  # Per architecture spec (Section 12.2)
    
    total_concepts = len(graph.nodes)
    concepts_with_content = 0
    concepts_without_content = 0
    total_templates = 0
    published_templates = 0
    draft_templates = 0
    gaps = []
    all_ready = True
    
    for concept_id, node in graph.nodes.items():
        published_count = db.query(QuestionTemplate).filter(
            QuestionTemplate.concept_id == concept_id,
            QuestionTemplate.status == "PUBLISHED"
        ).count()
        
        draft_count = db.query(QuestionTemplate).filter(
            QuestionTemplate.concept_id == concept_id,
            QuestionTemplate.status.in_(["DRAFT", "REVIEW", "APPROVED"])
        ).count()
        
        total = published_count + draft_count
        total_templates += total
        published_templates += published_count
        draft_templates += draft_count
        
        if total > 0:
            concepts_with_content += 1
        else:
            concepts_without_content += 1
        
        # Determine gap severity
        if published_count == 0:
            severity = "critical"
            all_ready = False
        elif published_count < MIN_TEMPLATES:
            severity = "warning"
            all_ready = False
        else:
            severity = "ok"
        
        if severity != "ok":
            gaps.append(CoverageGapItem(
                concept_id=concept_id,
                concept_name=node.description or concept_id.split('.')[-1],
                published_count=published_count,
                draft_count=draft_count,
                needed=max(0, MIN_TEMPLATES - published_count),
                severity=severity
            ))
    
    coverage_pct = (concepts_with_content / total_concepts * 100) if total_concepts > 0 else 0
    
    # Sort gaps: critical first, then by needed count
    gaps.sort(key=lambda x: (0 if x.severity == "critical" else 1, -x.needed))
    
    return CoverageReportResponse(
        subject=subject,
        grade=grade,
        chapter_id=chapter,
        total_concepts=total_concepts,
        concepts_with_content=concepts_with_content,
        concepts_without_content=concepts_without_content,
        total_templates=total_templates,
        published_templates=published_templates,
        draft_templates=draft_templates,
        coverage_percentage=round(coverage_pct, 2),
        ready_to_publish=all_ready,
        gaps=gaps
    )


@coverage_router.get("/{subject}/{grade}/{chapter}/summary")
async def get_coverage_summary(
    subject: str,
    grade: int,
    chapter: str,
    db: Session = Depends(get_db)
):
    """
    Get a quick coverage summary (for dashboard widgets).
    """
    try:
        graph = ConceptGraph.load(subject, grade, chapter)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Graph not found")
    
    total_concepts = len(graph.nodes)
    
    # Quick aggregation
    published = db.query(QuestionTemplate).filter(
        QuestionTemplate.concept_id.like(f"{subject}.class{grade}.{chapter}.%"),
        QuestionTemplate.status == "PUBLISHED"
    ).count()
    
    draft = db.query(QuestionTemplate).filter(
        QuestionTemplate.concept_id.like(f"{subject}.class{grade}.{chapter}.%"),
        QuestionTemplate.status.in_(["DRAFT", "REVIEW", "APPROVED"])
    ).count()
    
    pending_review = db.query(QuestionTemplate).filter(
        QuestionTemplate.concept_id.like(f"{subject}.class{grade}.{chapter}.%"),
        QuestionTemplate.status == "REVIEW"
    ).count()
    
    return {
        "subject": subject,
        "grade": grade,
        "chapter": chapter,
        "total_concepts": total_concepts,
        "published_templates": published,
        "draft_templates": draft,
        "pending_review": pending_review,
        "total_templates": published + draft
    }


# =============================================================================
# Taxonomy Endpoints (Read-only)
# =============================================================================

@taxonomy_router.get("/{subject}", response_model=TaxonomyResponse)
async def get_taxonomy(
    subject: str = Path(..., description="Subject (e.g., math)")
):
    """
    Get all concepts from taxonomy for a subject.
    
    Reads from config/content/taxonomy/{subject}.yaml
    """
    validator = TaxonomyValidator()
    
    try:
        concepts = validator.get_concepts_by_subject(subject)
        
        concept_responses = []
        for concept in concepts:
            concept_responses.append(TaxonomyConceptResponse(
                id=concept.get('id', ''),
                name=concept.get('name', ''),
                grades=concept.get('grades', []),
                bloom_level=concept.get('bloom_level', 'REMEMBER'),
                difficulty_range=concept.get('difficulty_range', [1, 3]),
                prerequisites=concept.get('prerequisites', [])
            ))
        
        return TaxonomyResponse(
            subject=subject,
            version=1,
            total_concepts=len(concept_responses),
            concepts=concept_responses
        )
        
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Taxonomy not found: {str(e)}")


@taxonomy_router.get("/{subject}/validate/{concept_id}")
async def validate_concept_id(
    subject: str,
    concept_id: str = Path(..., description="Full concept ID to validate")
):
    """
    Validate that a concept ID exists in the taxonomy.
    """
    validator = TaxonomyValidator()
    
    is_valid, error = validator.validate_concept_id(concept_id)
    
    return {
        "concept_id": concept_id,
        "valid": is_valid,
        "error": error if not is_valid else None
    }


# Export router that combines all admin sub-routers
# Note: templates_router is in api/admin/templates.py
router = APIRouter(prefix="/api/admin")
router.include_router(graphs_router)
router.include_router(coverage_router)
router.include_router(taxonomy_router)

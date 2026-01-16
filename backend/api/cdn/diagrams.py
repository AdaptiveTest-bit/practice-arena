"""
CDN API endpoints for Phase 6 implementation.

Provides dynamic diagram rendering and CDN management endpoints.
Integrates with the diagram service for efficient content delivery.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from fastapi.responses import Response, JSONResponse
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
import asyncio

from db.base import get_db
from domain.cdn.diagram_service import DiagramCDNService


# Pydantic models for request/response
class DiagramRenderRequest(BaseModel):
    """Request model for diagram rendering."""
    diagram_type: str = Field(..., description="Type of diagram to render")
    parameters: Dict[str, Any] = Field(..., description="Parameters for diagram generation")


class DiagramRenderResponse(BaseModel):
    """Response model for diagram rendering."""
    success: bool
    diagram_url: str = Field(..., description="CDN URL of the rendered diagram")
    diagram_key: str = Field(..., description="Unique diagram key")
    cache_status: str = Field(..., description="Cache status: 'hit' or 'miss'")


class MigrationResponse(BaseModel):
    """Response model for diagram migration."""
    total: int = Field(..., description="Total diagrams to migrate")
    migrated: int = Field(..., description="Successfully migrated diagrams")
    failed: int = Field(..., description="Failed migrations")
    errors: List[Dict[str, Any]] = Field(default=[], description="Migration errors")


# Create router
router = APIRouter(prefix="/api/cdn", tags=["cdn"])

# Global CDN service instance
cdn_service = DiagramCDNService()


def get_cdn_service() -> DiagramCDNService:
    """Dependency injection for CDN service."""
    return cdn_service


@router.post("/diagrams/render", response_model=DiagramRenderResponse)
async def render_diagram(
    request: DiagramRenderRequest,
    background_tasks: BackgroundTasks,
    service: DiagramCDNService = Depends(get_cdn_service)
):
    """
    Render a diagram dynamically with CDN caching.
    
    - Generates SVG content based on diagram type and parameters
    - Stores rendered diagram in CDN storage
    - Returns CDN URL for efficient delivery
    - Implements caching for repeated requests
    """
    try:
        # Check if this is a cache hit or miss
        diagram_key = service.generate_diagram_key(request.diagram_type, request.parameters)
        existing_diagram = await service.get_pre_rendered_diagram(diagram_key)
        
        cache_status = "hit" if existing_diagram else "miss"
        
        # Render or retrieve diagram
        diagram_url = await service.render_diagram_dynamically(
            request.diagram_type, 
            request.parameters
        )
        
        return DiagramRenderResponse(
            success=True,
            diagram_url=diagram_url,
            diagram_key=diagram_key,
            cache_status=cache_status
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Diagram rendering failed: {str(e)}")


@router.get("/diagrams/{diagram_key}")
async def get_diagram(
    diagram_key: str,
    service: DiagramCDNService = Depends(get_cdn_service)
):
    """
    Get a diagram by its key.
    
    Returns the raw SVG content for direct serving.
    """
    try:
        svg_content = await service.get_pre_rendered_diagram(diagram_key)
        
        if svg_content is None:
            raise HTTPException(status_code=404, detail="Diagram not found")
        
        return Response(
            content=svg_content,
            media_type="image/svg+xml",
            headers={"Cache-Control": "public, max-age=3600"}  # Cache for 1 hour
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve diagram: {str(e)}")


@router.post("/diagrams/migrate", response_model=MigrationResponse)
async def migrate_diagrams(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    service: DiagramCDNService = Depends(get_cdn_service)
):
    """
    Migrate existing template diagrams to CDN.
    
    - Processes all template diagrams in the database
    - Renders and stores diagrams in CDN storage
    - Updates database records with CDN URLs
    - Returns migration statistics
    """
    try:
        # Run migration in background
        results = await service.migrate_template_diagrams(db)
        
        return MigrationResponse(**results)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Migration failed: {str(e)}")


@router.get("/diagrams/types")
async def list_diagram_types():
    """
    List available diagram types.
    
    Returns the supported diagram types and their parameter schemas.
    """
    diagram_types = {
        "factors": {
            "description": "Factor tree visualization",
            "parameters": {
                "target_number": "int - The number to find factors for",
                "factors": "list[int] - List of all factors"
            }
        },
        "multiples": {
            "description": "Multiples sequence visualization",
            "parameters": {
                "number": "int - Base number for multiples",
                "multiples": "list[int] - List of multiples"
            }
        },
        "gcd": {
            "description": "GCD visualization using prime factors",
            "parameters": {
                "num1": "int - First number",
                "num2": "int - Second number",
                "gcd_result": "int - GCD result",
                "factors1": "list[int] - Prime factors of first number (optional)",
                "factors2": "list[int] - Prime factors of second number (optional)"
            }
        },
        "lcm": {
            "description": "LCM visualization",
            "parameters": {
                "num1": "int - First number",
                "num2": "int - Second number",
                "lcm_result": "int - LCM result"
            }
        },
        "divisibility": {
            "description": "Divisibility test visualization",
            "parameters": {
                "number": "int - Number to test",
                "divisor": "int - Divisor",
                "is_divisible": "bool - Whether divisible",
                "quotient": "int - Quotient result",
                "remainder": "int - Remainder result"
            }
        },
        "prime_composite": {
            "description": "Prime/composite number visualization",
            "parameters": {
                "number": "int - Number to classify",
                "factors": "list[int] - List of factors",
                "is_prime": "bool - Whether number is prime"
            }
        },
        "factor_pairs": {
            "description": "Factor pairs visualization",
            "parameters": {
                "number": "int - Number to find factor pairs for",
                "factor_pairs": "list[tuple] - List of factor pairs"
            }
        },
        "prime_factorization": {
            "description": "Prime factorization tree",
            "parameters": {
                "number": "int - Number to factorize",
                "prime_factors": "list[int] - List of prime factors"
            }
        }
    }
    
    return {"diagram_types": diagram_types}


@router.get("/diagrams/cache/stats")
async def get_cache_stats(service: DiagramCDNService = Depends(get_cdn_service)):
    """
    Get cache statistics.
    
    Returns information about cache hit rates and storage usage.
    """
    cache_stats = {
        "cached_diagrams": len(service._render_cache),
        "cache_ttl_hours": service._cache_ttl.total_seconds() / 3600,
        "storage_path": str(service.local_storage_path),
        "cdn_base_url": service.cdn_base_url
    }
    
    # Count stored diagrams
    try:
        stored_diagrams = list(service.local_storage_path.glob("*.svg"))
        cache_stats["stored_diagrams"] = len(stored_diagrams)
        
        # Calculate total storage size
        total_size = sum(f.stat().st_size for f in stored_diagrams)
        cache_stats["storage_size_bytes"] = total_size
        cache_stats["storage_size_mb"] = round(total_size / (1024 * 1024), 2)
        
    except Exception:
        cache_stats["stored_diagrams"] = 0
        cache_stats["storage_size_bytes"] = 0
        cache_stats["storage_size_mb"] = 0
    
    return cache_stats


@router.delete("/diagrams/cache")
async def clear_cache(service: DiagramCDNService = Depends(get_cdn_service)):
    """
    Clear the diagram cache.
    
    Removes all cached diagrams from memory and optionally from storage.
    """
    try:
        # Clear memory cache
        service._render_cache.clear()
        
        # Optionally clear storage (commented out for safety)
        # import shutil
        # if service.local_storage_path.exists():
        #     shutil.rmtree(service.local_storage_path)
        #     service.local_storage_path.mkdir(parents=True, exist_ok=True)
        
        return {"message": "Cache cleared successfully", "cached_diagrams": 0}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear cache: {str(e)}")


@router.get("/diagrams/{diagram_key}/metadata")
async def get_diagram_metadata(
    diagram_key: str,
    service: DiagramCDNService = Depends(get_cdn_service)
):
    """
    Get metadata for a specific diagram.
    
    Returns the stored metadata if available.
    """
    try:
        metadata_path = service.local_storage_path / f"{diagram_key}.json"
        
        if not metadata_path.exists():
            raise HTTPException(status_code=404, detail="Diagram metadata not found")
        
        import json
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        
        return metadata
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve metadata: {str(e)}")


@router.post("/diagrams/batch", response_model=List[DiagramRenderResponse])
async def render_batch_diagrams(
    requests: List[DiagramRenderRequest],
    service: DiagramCDNService = Depends(get_cdn_service)
):
    """
    Render multiple diagrams in batch.
    
    Efficiently processes multiple diagram requests.
    """
    try:
        results = []
        
        for request in requests:
            diagram_key = service.generate_diagram_key(request.diagram_type, request.parameters)
            existing_diagram = await service.get_pre_rendered_diagram(diagram_key)
            cache_status = "hit" if existing_diagram else "miss"
            
            diagram_url = await service.render_diagram_dynamically(
                request.diagram_type, 
                request.parameters
            )
            
            results.append(DiagramRenderResponse(
                success=True,
                diagram_url=diagram_url,
                diagram_key=diagram_key,
                cache_status=cache_status
            ))
        
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch rendering failed: {str(e)}")

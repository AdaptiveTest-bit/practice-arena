"""
CDN API endpoints for Phase 6 implementation.

Provides dynamic diagram rendering and CDN management endpoints.
Integrates with the diagram service for efficient content delivery.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Query, Depends
from fastapi.responses import Response, JSONResponse
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
import asyncio

from core.database import get_db
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


# NOTE: The /diagrams/{diagram_key} route is moved to the END of this file
# to prevent it from matching specific paths like /diagrams/types before they are checked


@router.post("/diagrams/preview")
async def preview_diagram(
    request: DiagramRenderRequest,
    service: DiagramCDNService = Depends(get_cdn_service)
):
    """
    Preview a diagram without storing it.
    
    Returns raw SVG content for immediate display.
    Useful for template editor preview.
    """
    try:
        # Render the SVG directly without storing
        svg_content = service._render_svg_content(request.diagram_type, request.parameters)
        
        return Response(
            content=svg_content,
            media_type="image/svg+xml"
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Diagram preview failed: {str(e)}")


@router.get("/diagrams/types")
async def get_diagram_types():
    """
    Get list of supported diagram types with parameters.
    
    Useful for building UI forms.
    """
    return {
        "types": [
            {
                "type": "triangle",
                "name": "Triangle",
                "category": "geometry",
                "parameters": [
                    {"name": "base", "type": "number", "required": True, "description": "Base length in cm"},
                    {"name": "height", "type": "number", "required": True, "description": "Height in cm"},
                    {"name": "show_labels", "type": "boolean", "default": True},
                    {"name": "show_height_line", "type": "boolean", "default": True}
                ]
            },
            {
                "type": "rectangle",
                "name": "Rectangle",
                "category": "geometry",
                "parameters": [
                    {"name": "length", "type": "number", "required": True},
                    {"name": "width", "type": "number", "required": True},
                    {"name": "show_labels", "type": "boolean", "default": True}
                ]
            },
            {
                "type": "circle",
                "name": "Circle",
                "category": "geometry",
                "parameters": [
                    {"name": "radius", "type": "number", "required": True},
                    {"name": "show_labels", "type": "boolean", "default": True},
                    {"name": "show_radius", "type": "boolean", "default": True},
                    {"name": "show_diameter", "type": "boolean", "default": False}
                ]
            },
            {
                "type": "number_line",
                "name": "Number Line",
                "category": "arithmetic",
                "parameters": [
                    {"name": "start", "type": "integer", "default": 0},
                    {"name": "end", "type": "integer", "default": 10},
                    {"name": "highlight", "type": "array", "description": "Numbers to highlight"}
                ]
            },
            {
                "type": "factors",
                "name": "Factors Diagram",
                "category": "arithmetic",
                "parameters": [
                    {"name": "target_number", "type": "integer", "required": True},
                    {"name": "factors", "type": "array", "required": True}
                ]
            },
            {
                "type": "gcd",
                "name": "GCD Diagram",
                "category": "arithmetic",
                "parameters": [
                    {"name": "num1", "type": "integer", "required": True},
                    {"name": "num2", "type": "integer", "required": True},
                    {"name": "gcd_result", "type": "integer", "required": True}
                ]
            },
            {
                "type": "lcm",
                "name": "LCM Diagram",
                "category": "arithmetic",
                "parameters": [
                    {"name": "num1", "type": "integer", "required": True},
                    {"name": "num2", "type": "integer", "required": True},
                    {"name": "lcm_result", "type": "integer", "required": True}
                ]
            },
            {
                "type": "prime_factorization",
                "name": "Prime Factorization Tree",
                "category": "arithmetic",
                "parameters": [
                    {"name": "number", "type": "integer", "required": True},
                    {"name": "prime_factors", "type": "array", "required": True}
                ]
            },
            # ==================== DATA VISUALIZATION ====================
            {
                "type": "bar_chart",
                "name": "Bar Chart",
                "category": "data_visualization",
                "description": "Vertical bar chart with customizable colors and labels",
                "parameters": [
                    {"name": "title", "type": "string", "default": "Bar Chart"},
                    {"name": "labels", "type": "array", "required": True, "description": "Category labels (e.g., ['Jan', 'Feb', 'Mar'])"},
                    {"name": "values", "type": "array", "required": True, "description": "Numeric values (e.g., [10, 25, 15])"},
                    {"name": "colors", "type": "array", "required": False, "description": "Custom colors for bars"},
                    {"name": "show_values", "type": "boolean", "default": True}
                ],
                "examples": [
                    {
                        "name": "Student Marks",
                        "parameters": {"title": "Student Marks", "labels": "Math,Science,English", "values": "85,92,78"}
                    }
                ]
            },
            {
                "type": "pie_chart",
                "name": "Pie Chart",
                "category": "data_visualization",
                "description": "Circular chart showing proportional data",
                "parameters": [
                    {"name": "title", "type": "string", "default": "Pie Chart"},
                    {"name": "labels", "type": "array", "required": True},
                    {"name": "values", "type": "array", "required": True},
                    {"name": "colors", "type": "array", "required": False},
                    {"name": "show_percentages", "type": "boolean", "default": True}
                ],
                "examples": [
                    {
                        "name": "Budget Distribution",
                        "parameters": {"title": "Monthly Budget", "labels": "Food,Rent,Transport,Entertainment", "values": "300,500,150,100"}
                    }
                ]
            },
            {
                "type": "coordinate_plane",
                "name": "Coordinate Plane",
                "category": "geometry",
                "description": "X-Y coordinate system with optional points and lines",
                "parameters": [
                    {"name": "title", "type": "string", "default": "Coordinate Plane"},
                    {"name": "x_min", "type": "integer", "default": -10},
                    {"name": "x_max", "type": "integer", "default": 10},
                    {"name": "y_min", "type": "integer", "default": -10},
                    {"name": "y_max", "type": "integer", "default": 10},
                    {"name": "points", "type": "array", "description": 'Array of point objects: [{"x": 3, "y": 4, "label": "A"}]'},
                    {"name": "show_grid", "type": "boolean", "default": True},
                    {"name": "draw_line", "type": "boolean", "default": False, "description": "Connect points with line"}
                ],
                "examples": [
                    {
                        "name": "Plot Points",
                        "parameters": {"x_min": -5, "x_max": 5, "y_min": -5, "y_max": 5, "points": '[{"x": 2, "y": 3, "label": "A"}, {"x": -1, "y": 4, "label": "B"}]'}
                    }
                ]
            },
            {
                "type": "line_graph",
                "name": "Line Graph",
                "category": "data_visualization",
                "description": "Line chart with multiple series support",
                "parameters": [
                    {"name": "title", "type": "string", "default": "Line Graph"},
                    {"name": "x_labels", "type": "array", "required": True, "description": "X-axis labels"},
                    {"name": "series", "type": "array", "required": True, "description": 'Array: [{"name": "Sales", "values": [10,20,30], "color": "#4CAF50"}]'},
                    {"name": "show_points", "type": "boolean", "default": True}
                ]
            },
            {
                "type": "fraction_visual",
                "name": "Fraction Visual",
                "category": "arithmetic",
                "description": "Visual representation of fractions (circle or bar)",
                "parameters": [
                    {"name": "numerator", "type": "integer", "required": True},
                    {"name": "denominator", "type": "integer", "required": True},
                    {"name": "style", "type": "string", "enum": ["circle", "bar"], "default": "circle"},
                    {"name": "show_label", "type": "boolean", "default": True}
                ],
                "examples": [
                    {
                        "name": "Three Quarters",
                        "parameters": {"numerator": 3, "denominator": 4, "style": "circle"}
                    }
                ]
            },
            {
                "type": "angle_diagram",
                "name": "Angle Diagram",
                "category": "geometry",
                "description": "Angle with two rays, arc, and degree measurement",
                "parameters": [
                    {"name": "angle", "type": "number", "required": True, "description": "Angle in degrees (0-360)"},
                    {"name": "label", "type": "string", "description": "Custom label (e.g., '∠ABC')"},
                    {"name": "ray_length", "type": "integer", "default": 100},
                    {"name": "show_arc", "type": "boolean", "default": True},
                    {"name": "arc_radius", "type": "integer", "default": 30},
                    {"name": "color", "type": "string", "default": "#2196F3"},
                    {"name": "title", "type": "string", "description": "Diagram title"}
                ],
                "examples": [
                    {
                        "name": "45 Degree Angle",
                        "parameters": {"angle": 45, "label": "∠ABC = 45°"}
                    },
                    {
                        "name": "Right Angle",
                        "parameters": {"angle": 90, "label": "90°", "title": "Right Angle"}
                    }
                ]
            },
            # ==================== CUSTOM SVG ====================
            {
                "type": "custom_svg",
                "name": "Custom SVG Template",
                "category": "custom",
                "description": "User-provided SVG with variable substitution. Use {{variable_name}} syntax for dynamic values.",
                "parameters": [
                    {"name": "svg_template", "type": "string", "required": True, "description": "Full SVG markup with {{variable}} placeholders"},
                    {"name": "variables", "type": "object", "required": False, "description": "Key-value pairs for variable substitution"}
                ],
                "examples": [
                    {
                        "name": "Simple Circle",
                        "svg_template": "<svg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'><circle cx='100' cy='100' r='{{radius}}' fill='{{color}}'/><text x='100' y='105' text-anchor='middle' font-size='14'>r = {{radius}}</text></svg>",
                        "variables": {"radius": "50", "color": "#4F46E5"}
                    }
                ]
            }
        ]
    }


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


# NOTE: The main /diagrams/types endpoint is defined earlier in this file (around line 120)
# It includes both geometry types (triangle, rectangle, circle) and arithmetic types
# (factors, gcd, lcm, etc.)


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


# This route MUST be at the end to prevent matching specific paths like /diagrams/types
@router.get("/diagrams/{diagram_key}")
async def get_diagram(
    diagram_key: str,
    service: DiagramCDNService = Depends(get_cdn_service)
):
    """
    Get a diagram by its key.
    
    Returns the raw SVG content for direct serving.
    This route is placed at the END to prevent it from matching
    specific paths like /diagrams/types, /diagrams/preview, etc.
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

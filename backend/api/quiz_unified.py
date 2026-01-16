"""
Unified quiz router for Phase 8 gradual rollout.

Handles traffic routing between v1 and v2 endpoints based on feature flags.
Provides seamless canary deployment without breaking frontend.
"""

from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional
import asyncio
from sqlalchemy.orm import Session

from db.base import Base
from core.database import get_db
from core.feature_flags import feature_flag_service, should_use_v2, get_user_id
from api.quiz_v2 import LeanQuizServiceV2, router as v2_router


# Import v1 endpoints (existing ones)
# We'll need to import the existing session adapter for v1
try:
    from core.session_adapter import get_session_adapter
    V1_AVAILABLE = True
except ImportError:
    V1_AVAILABLE = False
    print("Warning: V1 session adapter not available, only v2 will be served")


# Create unified router
unified_router = APIRouter(prefix="/api/quiz", tags=["quiz-unified"])


class UnifiedQuizService:
    """
    Unified service that routes requests to v1 or v2 based on feature flags.
    
    Provides seamless transition between legacy and lean endpoints.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.v2_service = LeanQuizServiceV2(db)
        
        if V1_AVAILABLE:
            self.v1_adapter = get_session_adapter()
        else:
            self.v1_adapter = None
    
    def _get_service_for_request(self, request: Request):
        """Get the appropriate service (v1 or v2) for this request."""
        if should_use_v2(request):
            return self.v2_service, "v2"
        elif self.v1_adapter:
            return self.v1_adapter, "v1"
        else:
            # Fallback to v2 if v1 is not available
            return self.v2_service, "v2"
    
    async def start_session(self, request: Request, session_data: Dict[str, Any]):
        """Start session using appropriate service version."""
        service, version = self._get_service_for_request(request)
        
        # Transform request format based on version
        if version == "v2":
            # Use v2 service directly
            from api.quiz_v2 import SessionStartRequestV2
            v2_request = SessionStartRequestV2(**session_data)
            result = await service.start_session(v2_request)
            return result, version
        else:
            # Use v1 adapter
            result = service.start_session(**session_data)
            return result, version
    
    async def get_question(self, request: Request, session_id: str):
        """Get question using appropriate service version."""
        service, version = self._get_service_for_request(request)
        
        if version == "v2":
            result = await service.get_next_question(session_id)
            return result, version
        else:
            result = service.get_next_question(session_id)
            return result, version
    
    async def submit_answer(self, request: Request, session_id: str, answer_data: Dict[str, Any]):
        """Submit answer using appropriate service version."""
        service, version = self._get_service_for_request(request)
        
        if version == "v2":
            from api.quiz_v2 import AnswerSubmitRequestV2
            v2_request = AnswerSubmitRequestV2(**answer_data)
            result = await service.submit_answer(session_id, v2_request)
            return result, version
        else:
            result = service.submit_answer(session_id, **answer_data)
            return result, version
    
    async def end_session(self, request: Request, session_id: str, end_data: Dict[str, Any]):
        """End session using appropriate service version."""
        service, version = self._get_service_for_request(request)
        
        if version == "v2":
            from api.quiz_v2 import SessionEndRequestV2
            v2_request = SessionEndRequestV2(**end_data)
            result = await service.end_session(session_id, v2_request)
            return result, version
        else:
            # V1 might not have explicit end session, create a simple response
            result = {"success": True, "message": "Session ended"}
            return result, version


# Service dependency
def get_unified_service(db: Session = Depends(get_db)) -> UnifiedQuizService:
    """Dependency injection for unified quiz service."""
    return UnifiedQuizService(db)


# Unified endpoints that route to v1 or v2
@unified_router.post("/session/start")
async def start_session_unified(
    request: Request,
    session_data: Dict[str, Any],
    service: UnifiedQuizService = Depends(get_unified_service)
):
    """
    Start quiz session with automatic version routing.
    
    Routes to v1 or v2 based on feature flags and user targeting.
    """
    try:
        result, version = await service.start_session(request, session_data)
        
        # Add routing information to response
        if hasattr(result, 'dict'):
            response_data = result.dict()
        else:
            response_data = result
        
        response_data["_routing"] = {
            "version": version,
            "feature_flag_percentage": feature_flag_service.flags["lean_api_v2"]["percentage"],
            "user_id": get_user_id(request)
        }
        
        return JSONResponse(content=response_data)
        
    except Exception as e:
        # Log error and provide fallback
        print(f"Error in unified session start: {e}")
        raise HTTPException(status_code=500, detail="Failed to start session")


@unified_router.get("/{session_id}/question")
async def get_question_unified(
    request: Request,
    session_id: str,
    service: UnifiedQuizService = Depends(get_unified_service)
):
    """
    Get next question with automatic version routing.
    
    Returns lean payload if routed to v2, legacy payload if routed to v1.
    """
    try:
        result, version = await service.get_question(request, session_id)
        
        # Add routing information
        if hasattr(result, 'dict'):
            response_data = result.dict()
        else:
            response_data = result
        
        response_data["_routing"] = {
            "version": version,
            "feature_flag_percentage": feature_flag_service.flags["lean_api_v2"]["percentage"]
        }
        
        return JSONResponse(content=response_data)
        
    except Exception as e:
        print(f"Error in unified question endpoint: {e}")
        raise HTTPException(status_code=500, detail="Failed to get question")


@unified_router.post("/{session_id}/answer")
async def submit_answer_unified(
    request: Request,
    session_id: str,
    answer_data: Dict[str, Any],
    service: UnifiedQuizService = Depends(get_unified_service)
):
    """
    Submit answer with automatic version routing.
    
    Routes to appropriate service version based on feature flags.
    """
    try:
        result, version = await service.submit_answer(request, session_id, answer_data)
        
        # Add routing information
        if hasattr(result, 'dict'):
            response_data = result.dict()
        else:
            response_data = result
        
        response_data["_routing"] = {
            "version": version,
            "feature_flag_percentage": feature_flag_service.flags["lean_api_v2"]["percentage"]
        }
        
        return JSONResponse(content=response_data)
        
    except Exception as e:
        print(f"Error in unified answer endpoint: {e}")
        raise HTTPException(status_code=500, detail="Failed to submit answer")


@unified_router.post("/{session_id}/end")
async def end_session_unified(
    request: Request,
    session_id: str,
    end_data: Dict[str, Any],
    service: UnifiedQuizService = Depends(get_unified_service)
):
    """
    End session with automatic version routing.
    
    Provides session summary regardless of version used.
    """
    try:
        result, version = await service.end_session(request, session_id, end_data)
        
        # Add routing information
        if hasattr(result, 'dict'):
            response_data = result.dict()
        else:
            response_data = result
        
        response_data["_routing"] = {
            "version": version,
            "feature_flag_percentage": feature_flag_service.flags["lean_api_v2"]["percentage"]
        }
        
        return JSONResponse(content=response_data)
        
    except Exception as e:
        print(f"Error in unified session end: {e}")
        raise HTTPException(status_code=500, detail="Failed to end session")


# Management endpoints for feature flags
@unified_router.get("/admin/feature-flags")
async def get_feature_flags():
    """
    Get current feature flag configuration.
    
    Returns the current state of all feature flags.
    """
    return {
        "flags": feature_flag_service.flags,
        "metrics": feature_flag_service.get_metrics()
    }


@unified_router.post("/admin/feature-flags/{flag_name}")
async def update_feature_flag(flag_name: str, updates: Dict[str, Any]):
    """
    Update a feature flag configuration.
    
    Allows gradual rollout control and percentage adjustments.
    """
    success = feature_flag_service.update_flag(flag_name, updates)
    
    if not success:
        raise HTTPException(status_code=404, detail=f"Feature flag '{flag_name}' not found")
    
    return {
        "success": True,
        "flag_name": flag_name,
        "updated_flags": feature_flag_service.flags[flag_name],
        "metrics": feature_flag_service.get_metrics()
    }


@unified_router.get("/admin/routing-metrics")
async def get_routing_metrics():
    """
    Get routing metrics for monitoring.
    
    Provides insights into traffic distribution and performance.
    """
    metrics = feature_flag_service.get_metrics()
    recent_decisions = feature_flag_service.get_recent_routing_decisions(50)
    
    return {
        "metrics": metrics,
        "recent_decisions": recent_decisions,
        "recommendations": _generate_routing_recommendations(metrics)
    }


def _generate_routing_recommendations(metrics: Dict[str, Any]) -> list:
    """Generate recommendations based on routing metrics."""
    recommendations = []
    
    total = metrics["total_requests"]
    if total == 0:
        return ["Start with 1-5% traffic to v2 for initial testing"]
    
    v2_percentage = metrics["v2_percentage"]
    flag_percentage = metrics["current_flag_percentage"]
    
    if v2_percentage == 0 and flag_percentage > 0:
        recommendations.append("No traffic reaching v2 despite flag being enabled - check routing logic")
    elif v2_percentage > 0 and flag_percentage == 0:
        recommendations.append("Traffic reaching v2 despite flag being disabled - check configuration")
    elif abs(v2_percentage - flag_percentage) > 10:
        recommendations.append(f"Traffic distribution ({v2_percentage}%) differs from flag setting ({flag_percentage}%) - investigate")
    elif v2_percentage >= 95 and flag_percentage < 100:
        recommendations.append("High v2 adoption - consider increasing flag percentage to 100%")
    elif v2_percentage >= 50 and flag_percentage == 100:
        recommendations.append("Full rollout successful - consider removing v1 endpoints")
    elif total < 100:
        recommendations.append("Low traffic volume - gather more data before making decisions")
    
    if not recommendations:
        recommendations.append("Routing is working as expected")
    
    return recommendations


@unified_router.get("/health")
async def health_check_unified():
    """
    Health check for unified endpoints.
    
    Returns status of both v1 and v2 services.
    """
    return {
        "success": True,
        "unified_router": "active",
        "v1_available": V1_AVAILABLE,
        "v2_available": True,
        "feature_flags": "active",
        "routing_metrics": feature_flag_service.get_metrics(),
        "timestamp": asyncio.get_event_loop().time()
    }


# Include v2 router for direct v2 access
unified_router.include_router(v2_router, prefix="/v2")

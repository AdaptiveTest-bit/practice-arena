"""
Feature flag system for Phase 8 gradual rollout.

Handles percentage-based routing between v1 and v2 endpoints.
Provides monitoring and control for canary deployments.
"""

import os
import json
import hashlib
from typing import Dict, Any, Optional
from datetime import datetime
from fastapi import Request, HTTPException
from fastapi.routing import APIRoute


class FeatureFlagService:
    """
    Service for managing feature flags and traffic routing.
    
    Supports percentage-based rollouts and user targeting.
    """
    
    def __init__(self):
        self.flags = self._load_default_flags()
        self._metrics = {
            "v1_requests": 0,
            "v2_requests": 0,
            "total_requests": 0,
            "routing_decisions": []
        }
    
    def _load_default_flags(self) -> Dict[str, Any]:
        """Load default feature flag configuration."""
        return {
            "lean_api_v2": {
                "enabled": True,
                "percentage": 0,  # Start at 0%, gradually increase
                "user_whitelist": [],
                "user_blacklist": [],
                "description": "Enable lean API v2 endpoints"
            },
            "cdn_diagrams": {
                "enabled": True,
                "percentage": 100,
                "description": "Use CDN for diagram delivery"
            },
            "lean_payloads": {
                "enabled": True,
                "percentage": 100,
                "description": "Use lean payloads without inline HTML"
            }
        }
    
    def is_enabled(self, flag_name: str, user_id: Optional[str] = None) -> bool:
        """
        Check if a feature flag is enabled for a user.
        
        Args:
            flag_name: Name of the feature flag
            user_id: Optional user identifier for targeting
            
        Returns:
            Whether the feature is enabled
        """
        if flag_name not in self.flags:
            return False
        
        flag = self.flags[flag_name]
        
        # Check if flag is globally enabled
        if not flag["enabled"]:
            return False
        
        # Check whitelist (always enabled for these users)
        if user_id and user_id in flag.get("user_whitelist", []):
            return True
        
        # Check blacklist (never enabled for these users)
        if user_id and user_id in flag.get("user_blacklist", []):
            return False
        
        # Check percentage-based rollout
        if flag["percentage"] >= 100:
            return True
        elif flag["percentage"] <= 0:
            return False
        else:
            # Use consistent hashing for percentage-based routing
            if user_id:
                hash_value = int(hashlib.md5(f"{flag_name}:{user_id}".encode()).hexdigest(), 16)
                return (hash_value % 100) < flag["percentage"]
            else:
                # For anonymous users, use random distribution
                import random
                return random.randint(1, 100) <= flag["percentage"]
    
    def get_routing_decision(self, user_id: Optional[str] = None) -> str:
        """
        Decide whether to route to v1 or v2 endpoints.
        
        Args:
            user_id: Optional user identifier
            
        Returns:
            "v1" or "v2" indicating which version to use
        """
        self._metrics["total_requests"] += 1
        
        if self.is_enabled("lean_api_v2", user_id):
            self._metrics["v2_requests"] += 1
            decision = "v2"
        else:
            self._metrics["v1_requests"] += 1
            decision = "v1"
        
        # Record routing decision for monitoring
        self._metrics["routing_decisions"].append({
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "decision": decision,
            "v2_percentage": self.flags["lean_api_v2"]["percentage"]
        })
        
        # Keep only last 1000 decisions to prevent memory growth
        if len(self._metrics["routing_decisions"]) > 1000:
            self._metrics["routing_decisions"] = self._metrics["routing_decisions"][-1000:]
        
        return decision
    
    def update_flag(self, flag_name: str, updates: Dict[str, Any]) -> bool:
        """
        Update a feature flag configuration.
        
        Args:
            flag_name: Name of the flag to update
            updates: Dictionary of updates to apply
            
        Returns:
            Whether the update was successful
        """
        if flag_name not in self.flags:
            return False
        
        # Validate updates
        if "percentage" in updates:
            percentage = updates["percentage"]
            if not isinstance(percentage, int) or not (0 <= percentage <= 100):
                raise ValueError("Percentage must be an integer between 0 and 100")
        
        # Apply updates
        self.flags[flag_name].update(updates)
        return True
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current routing metrics."""
        total = self._metrics["total_requests"]
        if total == 0:
            return {
                "total_requests": 0,
                "v1_requests": 0,
                "v2_requests": 0,
                "v1_percentage": 0,
                "v2_percentage": 0,
                "current_flag_percentage": self.flags["lean_api_v2"]["percentage"]
            }
        
        return {
            "total_requests": total,
            "v1_requests": self._metrics["v1_requests"],
            "v2_requests": self._metrics["v2_requests"],
            "v1_percentage": round(self._metrics["v1_requests"] / total * 100, 2),
            "v2_percentage": round(self._metrics["v2_requests"] / total * 100, 2),
            "current_flag_percentage": self.flags["lean_api_v2"]["percentage"]
        }
    
    def get_recent_routing_decisions(self, limit: int = 100) -> list:
        """Get recent routing decisions for monitoring."""
        return self._metrics["routing_decisions"][-limit:]


# Global feature flag service instance
feature_flag_service = FeatureFlagService()


class FeatureFlagMiddleware:
    """
    Middleware to add feature flag information to requests.
    """
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            request = Request(scope, receive)
            
            # Extract user ID from headers or query params
            user_id = request.headers.get("X-User-ID")
            if not user_id:
                user_id = request.query_params.get("user_id")
            
            # Add routing decision to request state
            routing_decision = feature_flag_service.get_routing_decision(user_id)
            request.state.user_id = user_id
            request.state.routing_decision = routing_decision
            request.state.use_v2 = (routing_decision == "v2")
        
        await self.app(scope, receive, send)


class VersionedAPIRoute(APIRoute):
    """
    Custom route class that supports version-based routing.
    """
    
    def __init__(self, *args, **kwargs):
        self.version = kwargs.pop("version", "v1")
        super().__init__(*args, **kwargs)
    
    def get_route_handler(self):
        original_handler = super().get_route_handler()
        
        async def custom_route_handler(request):
            # Check if this request should use v2
            if hasattr(request.state, 'use_v2') and request.state.use_v2:
                if self.version == "v1":
                    # This is a v1 route but request should go to v2
                    # Let the request fall through to v2 routes
                    pass
                else:
                    # This is a v2 route and request should use v2
                    return await original_handler(request)
            else:
                # Request should use v1
                if self.version == "v1":
                    return await original_handler(request)
                else:
                    # This is a v2 route but request should use v1
                    pass
            
            # If we get here, the request doesn't match the routing decision
            # Let it continue to the next route
            return None
        
        return custom_route_handler


def should_use_v2(request: Request) -> bool:
    """
    Helper function to check if a request should use v2 endpoints.
    
    Args:
        request: FastAPI request object
        
    Returns:
        Whether to use v2 endpoints
    """
    return getattr(request.state, 'use_v2', False)


def get_user_id(request: Request) -> Optional[str]:
    """
    Helper function to extract user ID from request.
    
    Args:
        request: FastAPI request object
        
    Returns:
        User ID if available
    """
    return getattr(request.state, 'user_id', None)


# Configuration management
def load_flags_from_config(config_path: str) -> bool:
    """
    Load feature flags from a configuration file.
    
    Args:
        config_path: Path to JSON configuration file
        
    Returns:
        Whether the load was successful
    """
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        feature_flag_service.flags.update(config.get("flags", {}))
        return True
    except Exception:
        return False


def save_flags_to_config(config_path: str) -> bool:
    """
    Save current feature flags to a configuration file.
    
    Args:
        config_path: Path to save configuration
        
    Returns:
        Whether the save was successful
    """
    try:
        config = {
            "flags": feature_flag_service.flags,
            "last_updated": datetime.utcnow().isoformat()
        }
        
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        return True
    except Exception:
        return False


# Environment variable overrides
def apply_environment_overrides():
    """Apply feature flag overrides from environment variables."""
    # Example: LEAN_API_V2_PERCENTAGE=50
    if "LEAN_API_V2_PERCENTAGE" in os.environ:
        try:
            percentage = int(os.environ["LEAN_API_V2_PERCENTAGE"])
            feature_flag_service.update_flag("lean_api_v2", {"percentage": percentage})
        except ValueError:
            pass
    
    # Example: LEAN_API_V2_ENABLED=true
    if "LEAN_API_V2_ENABLED" in os.environ:
        enabled = os.environ["LEAN_API_V2_ENABLED"].lower() in ("true", "1", "yes")
        feature_flag_service.update_flag("lean_api_v2", {"enabled": enabled})


# Initialize environment overrides
apply_environment_overrides()

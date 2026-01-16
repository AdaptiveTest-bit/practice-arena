"""
CDN Service for Phase 6 implementation.

Manages diagram storage, rendering, and CDN integration.
Removes inline rich HTML/SVG from core API payloads.
"""

import hashlib
import json
import os
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import aiofiles
import asyncio
from datetime import datetime, timedelta

from sqlalchemy.orm import Session
from db.models import TemplateDiagram


class DiagramCDNService:
    """
    Service for managing diagram CDN operations.
    
    Handles both pre-rendered diagrams (stored files) and dynamic rendering
    with edge caching for parameterized diagrams.
    """
    
    def __init__(self, cdn_base_url: str = "https://cdn.example.com", local_storage_path: str = "cdn/diagrams"):
        self.cdn_base_url = cdn_base_url.rstrip('/')
        self.local_storage_path = Path(local_storage_path)
        self.local_storage_path.mkdir(parents=True, exist_ok=True)
        
        # Cache for dynamic rendering (in production, use Redis)
        self._render_cache = {}
        self._cache_ttl = timedelta(hours=1)
    
    def generate_diagram_key(self, diagram_type: str, parameters: Dict[str, Any]) -> str:
        """
        Generate a unique key for a diagram based on type and parameters.
        
        Args:
            diagram_type: Type of diagram (factors, multiples, gcd, etc.)
            parameters: Diagram parameters
            
        Returns:
            Unique key string
        """
        # Create deterministic key from type and parameters
        param_str = json.dumps(parameters, sort_keys=True)
        key_hash = hashlib.sha256(param_str.encode()).hexdigest()[:16]
        return f"{diagram_type}_{key_hash}"
    
    def get_cdn_url(self, diagram_key: str, file_extension: str = "svg") -> str:
        """
        Get the CDN URL for a diagram.
        
        Args:
            diagram_key: Unique diagram key
            file_extension: File extension (svg, png, etc.)
            
        Returns:
            Full CDN URL
        """
        return f"{self.cdn_base_url}/diagrams/{diagram_key}.{file_extension}"
    
    async def store_pre_rendered_diagram(self, diagram_key: str, svg_content: str, metadata: Dict[str, Any] = None) -> str:
        """
        Store a pre-rendered diagram to local storage (for development).
        
        In production, this would upload to S3/CloudFront.
        
        Args:
            diagram_key: Unique diagram key
            svg_content: SVG content to store
            metadata: Optional metadata
            
        Returns:
            CDN URL for the stored diagram
        """
        file_path = self.local_storage_path / f"{diagram_key}.svg"
        
        # Store SVG content
        async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
            await f.write(svg_content)
        
        # Store metadata if provided
        if metadata:
            metadata_path = self.local_storage_path / f"{diagram_key}.json"
            async with aiofiles.open(metadata_path, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(metadata, indent=2))
        
        return self.get_cdn_url(diagram_key)
    
    async def get_pre_rendered_diagram(self, diagram_key: str) -> Optional[str]:
        """
        Retrieve a pre-rendered diagram from local storage.
        
        Args:
            diagram_key: Unique diagram key
            
        Returns:
            SVG content or None if not found
        """
        file_path = self.local_storage_path / f"{diagram_key}.svg"
        
        if not file_path.exists():
            return None
        
        async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
            return await f.read()
    
    def is_cache_valid(self, cache_entry: Dict[str, Any]) -> bool:
        """Check if a cache entry is still valid."""
        return datetime.utcnow() - cache_entry['timestamp'] < self._cache_ttl
    
    async def render_diagram_dynamically(self, diagram_type: str, parameters: Dict[str, Any]) -> str:
        """
        Render a diagram dynamically with caching.
        
        Args:
            diagram_type: Type of diagram to render
            parameters: Parameters for the diagram
            
        Returns:
            CDN URL for the rendered diagram
        """
        diagram_key = self.generate_diagram_key(diagram_type, parameters)
        
        # Check cache first
        if diagram_key in self._render_cache:
            cache_entry = self._render_cache[diagram_key]
            if self.is_cache_valid(cache_entry):
                return cache_entry['url']
        
        # Render the diagram
        svg_content = self._render_svg_content(diagram_type, parameters)
        
        # Store the rendered diagram
        cdn_url = await self.store_pre_rendered_diagram(diagram_key, svg_content, {
            'type': diagram_type,
            'parameters': parameters,
            'rendered_at': datetime.utcnow().isoformat()
        })
        
        # Cache the result
        self._render_cache[diagram_key] = {
            'url': cdn_url,
            'timestamp': datetime.utcnow()
        }
        
        return cdn_url
    
    def _render_svg_content(self, diagram_type: str, parameters: Dict[str, Any]) -> str:
        """
        Render SVG content based on diagram type and parameters.
        
        This contains the migrated rendering logic from the generators.
        """
        if diagram_type == "factors":
            return self._render_factors_svg(parameters)
        elif diagram_type == "multiples":
            return self._render_multiples_svg(parameters)
        elif diagram_type == "gcd":
            return self._render_gcd_svg(parameters)
        elif diagram_type == "lcm":
            return self._render_lcm_svg(parameters)
        elif diagram_type == "divisibility":
            return self._render_divisibility_svg(parameters)
        elif diagram_type == "prime_composite":
            return self._render_prime_composite_svg(parameters)
        elif diagram_type == "factor_pairs":
            return self._render_factor_pairs_svg(parameters)
        elif diagram_type == "prime_factorization":
            return self._render_prime_factorization_svg(parameters)
        else:
            raise ValueError(f"Unknown diagram type: {diagram_type}")
    
    def _render_factors_svg(self, params: Dict[str, Any]) -> str:
        """Render factors diagram SVG."""
        target_number = params['target_number']
        factors = params['factors']
        
        return f"""
        <svg width="500" height="300" xmlns="http://www.w3.org/2000/svg">
            <rect width="500" height="300" fill="white" stroke="#ddd" stroke-width="1"/>
            <text x="250" y="30" text-anchor="middle" font-size="18" font-weight="bold">{target_number}</text>
            <line x1="250" y1="35" x2="250" y2="60" stroke="black" stroke-width="2"/>
            <circle cx="250" cy="80" r="20" fill="lightblue" stroke="black" stroke-width="2"/>
            <text x="250" y="85" text-anchor="middle" font-size="12">{target_number}</text>
            <text x="250" y="120" text-anchor="middle" font-size="14" fill="#2196F3">{', '.join(map(str, factors))}</text>
            <text x="250" y="140" text-anchor="middle" font-size="12">Total: {len(factors)} factors</text>
        </svg>
        """
    
    def _render_multiples_svg(self, params: Dict[str, Any]) -> str:
        """Render multiples diagram SVG."""
        number = params['number']
        multiples = params['multiples']
        multiples_str = ' → '.join(map(str, multiples[:6]))
        if len(multiples) > 6:
            multiples_str += " → ..."
        
        return f"""
        <svg width="500" height="150" xmlns="http://www.w3.org/2000/svg">
            <rect width="500" height="150" fill="white" stroke="#ddd" stroke-width="1"/>
            <text x="10" y="30" font-size="14" font-weight="bold">Multiples of {number}:</text>
            <text x="10" y="60" font-size="14" fill="#2196F3">{multiples_str}</text>
            <line x1="10" y1="75" x2="490" y2="75" stroke="#ccc" stroke-width="1"/>
            <text x="10" y="100" font-size="12">Each is {number} times a whole number</text>
        </svg>
        """
    
    def _render_gcd_svg(self, params: Dict[str, Any]) -> str:
        """Render GCD diagram SVG."""
        num1 = params['num1']
        num2 = params['num2']
        gcd_result = params['gcd_result']
        factors1 = params.get('factors1', [])
        factors2 = params.get('factors2', [])
        
        return f"""
        <svg width="500" height="250" xmlns="http://www.w3.org/2000/svg">
            <rect width="500" height="250" fill="white" stroke="#ddd" stroke-width="1"/>
            <text x="250" y="25" text-anchor="middle" font-size="16" font-weight="bold">Prime Factorization</text>
            <text x="50" y="70" font-size="13"><tspan font-weight="bold">{num1} =</tspan> {' × '.join(map(str, factors1))}</text>
            <text x="50" y="100" font-size="13"><tspan font-weight="bold">{num2} =</tspan> {' × '.join(map(str, factors2))}</text>
            <line x1="20" y1="120" x2="480" y2="120" stroke="#ccc" stroke-width="1"/>
            <text x="50" y="155" font-size="13" fill="#4CAF50"><tspan font-weight="bold">GCD =</tspan> {gcd_result}</text>
        </svg>
        """
    
    def _render_lcm_svg(self, params: Dict[str, Any]) -> str:
        """Render LCM diagram SVG."""
        num1 = params['num1']
        num2 = params['num2']
        lcm_result = params['lcm_result']
        
        return f"""
        <svg width="500" height="280" xmlns="http://www.w3.org/2000/svg">
            <rect width="500" height="280" fill="white" stroke="#ddd" stroke-width="1"/>
            <text x="250" y="25" text-anchor="middle" font-size="16" font-weight="bold">Least Common Multiple</text>
            <text x="30" y="65" font-size="13" font-weight="bold">Multiples of {num1}:</text>
            <text x="30" y="90" font-size="12" fill="#2196F3">{', '.join(map(str, [num1*i for i in range(1, 6)]))}, ...</text>
            <text x="30" y="135" font-size="13" font-weight="bold">Multiples of {num2}:</text>
            <text x="30" y="160" font-size="12" fill="#FF9800">{', '.join(map(str, [num2*i for i in range(1, 6)]))}, ...</text>
            <line x1="20" y1="185" x2="480" y2="185" stroke="#ccc" stroke-width="1"/>
            <text x="30" y="220" font-size="13" fill="#FF5722"><tspan font-weight="bold">LCM =</tspan> {lcm_result}</text>
        </svg>
        """
    
    def _render_divisibility_svg(self, params: Dict[str, Any]) -> str:
        """Render divisibility test diagram SVG."""
        number = params['number']
        divisor = params['divisor']
        is_divisible = params['is_divisible']
        quotient = params['quotient']
        remainder = params['remainder']
        status = "✓ DIVISIBLE" if is_divisible else "✗ NOT DIVISIBLE"
        status_color = "#4CAF50" if is_divisible else "#F44336"
        
        return f"""
        <svg width="500" height="250" xmlns="http://www.w3.org/2000/svg">
            <rect width="500" height="250" fill="white" stroke="#ddd" stroke-width="1"/>
            <text x="250" y="30" text-anchor="middle" font-size="18" font-weight="bold">{number} ÷ {divisor}</text>
            <rect x="100" y="60" width="150" height="80" fill="lightblue" stroke="black" stroke-width="2"/>
            <text x="175" y="110" text-anchor="middle" font-size="16" font-weight="bold">{quotient}</text>
            <text x="175" y="125" text-anchor="middle" font-size="12">quotient</text>
            <text x="300" y="100" font-size="14" font-weight="bold">R {remainder}</text>
            <text x="300" y="120" font-size="11">remainder</text>
            <line x1="50" y1="175" x2="450" y2="175" stroke="#ccc" stroke-width="1"/>
            <text x="250" y="210" text-anchor="middle" font-size="16" font-weight="bold" fill="{status_color}">{status}</text>
        </svg>
        """
    
    def _render_prime_composite_svg(self, params: Dict[str, Any]) -> str:
        """Render prime/composite diagram SVG."""
        number = params['number']
        factors = params['factors']
        is_prime = params['is_prime']
        status = "PRIME" if is_prime else "COMPOSITE"
        status_color = "#4CAF50" if is_prime else "#2196F3"
        factors_display = ', '.join(map(str, factors))
        
        return f"""
        <svg width="500" height="200" xmlns="http://www.w3.org/2000/svg">
            <rect width="500" height="200" fill="white" stroke="#ddd" stroke-width="1"/>
            <circle cx="250" cy="80" r="50" fill="{status_color}" opacity="0.3" stroke="{status_color}" stroke-width="3"/>
            <text x="250" y="90" text-anchor="middle" font-size="24" font-weight="bold">{number}</text>
            <text x="250" y="160" text-anchor="middle" font-size="16" font-weight="bold" fill="{status_color}">{status}</text>
            <text x="250" y="185" text-anchor="middle" font-size="12" fill="#666">Factors: {factors_display}</text>
        </svg>
        """
    
    def _render_factor_pairs_svg(self, params: Dict[str, Any]) -> str:
        """Render factor pairs diagram SVG."""
        number = params['number']
        factor_pairs = params['factor_pairs']
        
        # Build SVG elements for factor pairs (max 4 shown)
        pair_elements = []
        for i, (a, b) in enumerate(factor_pairs[:4]):
            x_offset = 50 + i * 100
            pair_elements.append(f'''
                <g transform="translate({x_offset}, 70)">
                    <rect width="80" height="60" fill="lightblue" stroke="#2196F3" stroke-width="2" rx="5"/>
                    <text x="40" y="25" text-anchor="middle" font-size="14" font-weight="bold">{a}×{b}</text>
                    <text x="40" y="45" text-anchor="middle" font-size="12">=</text>
                    <text x="40" y="55" text-anchor="middle" font-size="12">{number}</text>
                </g>''')
        svg_pairs = ''.join(pair_elements)
        
        return f"""
        <svg width="500" height="220" xmlns="http://www.w3.org/2000/svg">
            <rect width="500" height="220" fill="white" stroke="#ddd" stroke-width="1"/>
            <text x="250" y="30" text-anchor="middle" font-size="16" font-weight="bold">Finding pairs that multiply to {number}</text>
            {svg_pairs}
            <text x="250" y="170" text-anchor="middle" font-size="14" fill="#4CAF50"><tspan font-weight="bold">{len(factor_pairs)}</tspan> factor pair(s)</text>
        </svg>
        """
    
    def _render_prime_factorization_svg(self, params: Dict[str, Any]) -> str:
        """Render prime factorization diagram SVG."""
        number = params['number']
        prime_factors = params['prime_factors']
        from collections import Counter
        factor_counts = Counter(prime_factors)
        factorization_str = ' × '.join([f'{p}^{e}' if e > 1 else str(p) for p, e in sorted(factor_counts.items())])
        
        return f"""
        <svg width="500" height="220" xmlns="http://www.w3.org/2000/svg">
            <rect width="500" height="220" fill="white" stroke="#ddd" stroke-width="1"/>
            <text x="250" y="30" text-anchor="middle" font-size="18" font-weight="bold">{number}</text>
            <line x1="250" y1="35" x2="250" y2="55" stroke="black" stroke-width="2"/>
            <text x="250" y="80" text-anchor="middle" font-size="14">↓ Factor Tree ↓</text>
            <text x="250" y="120" text-anchor="middle" font-size="16" fill="#4CAF50">{factorization_str}</text>
            <text x="250" y="145" text-anchor="middle" font-size="12">Prime factors: {', '.join(map(str, prime_factors))}</text>
        </svg>
        """
    
    async def migrate_template_diagrams(self, db: Session) -> Dict[str, Any]:
        """
        Migrate existing template diagrams to CDN.
        
        Args:
            db: Database session
            
        Returns:
            Migration results
        """
        diagrams = db.query(TemplateDiagram).all()
        results = {
            'total': len(diagrams),
            'migrated': 0,
            'failed': 0,
            'errors': []
        }
        
        for diagram in diagrams:
            try:
                # Parse render pattern to extract parameters
                if diagram.render_pattern and diagram.variables:
                    parameters = diagram.variables
                    
                    # Generate diagram key
                    diagram_key = self.generate_diagram_key(diagram.diagram_type, parameters)
                    
                    # Render and store diagram
                    svg_content = self._render_svg_content(diagram.diagram_type, parameters)
                    cdn_url = await self.store_pre_rendered_diagram(diagram_key, svg_content)
                    
                    # Update diagram record with CDN URL
                    diagram.cdn_url = cdn_url
                    diagram.file_path = f"diagrams/{diagram_key}.svg"
                    db.commit()
                    
                    results['migrated'] += 1
                    
            except Exception as e:
                results['failed'] += 1
                results['errors'].append({
                    'diagram_id': diagram.id,
                    'error': str(e)
                })
        
        return results

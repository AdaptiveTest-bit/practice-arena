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
        # New diagram types for data visualization
        elif diagram_type == "bar_chart":
            return self._render_bar_chart_svg(parameters)
        elif diagram_type == "pie_chart":
            return self._render_pie_chart_svg(parameters)
        elif diagram_type == "coordinate_plane":
            return self._render_coordinate_plane_svg(parameters)
        elif diagram_type == "line_graph":
            return self._render_line_graph_svg(parameters)
        elif diagram_type == "fraction_visual":
            return self._render_fraction_visual_svg(parameters)
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
        # Geometry diagrams
        elif diagram_type == "triangle":
            return self._render_triangle_svg(parameters)
        elif diagram_type == "rectangle":
            return self._render_rectangle_svg(parameters)
        elif diagram_type == "circle":
            return self._render_circle_svg(parameters)
        elif diagram_type == "quadrilateral":
            return self._render_quadrilateral_svg(parameters)
        elif diagram_type == "number_line":
            return self._render_number_line_svg(parameters)
        elif diagram_type == "angle_diagram":
            return self._render_angle_diagram_svg(parameters)
        # User-provided custom SVG template
        elif diagram_type == "custom_svg":
            return self._render_custom_svg(parameters)
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
    
    # ============================================================
    # GEOMETRY DIAGRAMS
    # ============================================================
    
    def _render_triangle_svg(self, params: Dict[str, Any]) -> str:
        """Render triangle diagram SVG with dynamic base and height."""
        # Parse parameters (they come as strings from template)
        base = float(params.get('base', 10))
        height = float(params.get('height', 8))
        show_labels = str(params.get('show_labels', 'true')).lower() == 'true'
        show_height_line = str(params.get('show_height_line', 'true')).lower() == 'true'
        
        # Scale for display (max base width ~300px)
        scale = min(300 / base, 200 / height, 30)
        scaled_base = base * scale
        scaled_height = height * scale
        
        # SVG dimensions
        svg_width = 400
        svg_height = 300
        padding = 50
        
        # Triangle vertices (isoceles triangle for clarity)
        # A = left vertex, B = right vertex, C = top vertex
        ax = (svg_width - scaled_base) / 2
        ay = svg_height - padding
        bx = ax + scaled_base
        by = ay
        cx = svg_width / 2
        cy = svg_height - padding - scaled_height
        
        # Height line endpoint (perpendicular from C to AB)
        hx = cx
        hy = ay
        
        # Build SVG
        height_line = ""
        if show_height_line:
            height_line = f'''
            <line x1="{cx}" y1="{cy}" x2="{hx}" y2="{hy}" stroke="#2196F3" stroke-width="2" stroke-dasharray="5,5"/>
            <circle cx="{hx}" cy="{hy}" r="4" fill="#2196F3"/>
            <text x="{cx + 10}" y="{(cy + hy) / 2}" font-size="14" fill="#2196F3">h = {height} cm</text>'''
        
        base_label = ""
        if show_labels:
            base_label = f'''
            <text x="{(ax + bx) / 2}" y="{ay + 25}" text-anchor="middle" font-size="14" fill="#333">base = {base} cm</text>'''
        
        return f"""
        <svg width="{svg_width}" height="{svg_height}" xmlns="http://www.w3.org/2000/svg">
            <rect width="{svg_width}" height="{svg_height}" fill="#fafafa" stroke="#ddd" stroke-width="1"/>
            
            <!-- Title -->
            <text x="{svg_width/2}" y="25" text-anchor="middle" font-size="16" font-weight="bold" fill="#333">Triangle</text>
            
            <!-- Triangle -->
            <polygon points="{ax},{ay} {bx},{by} {cx},{cy}" fill="#E3F2FD" stroke="#1976D2" stroke-width="3"/>
            
            <!-- Vertices -->
            <circle cx="{ax}" cy="{ay}" r="4" fill="#1976D2"/>
            <circle cx="{bx}" cy="{by}" r="4" fill="#1976D2"/>
            <circle cx="{cx}" cy="{cy}" r="4" fill="#1976D2"/>
            
            <!-- Height line -->
            {height_line}
            
            <!-- Base label -->
            {base_label}
            
            <!-- Right angle marker if height line shown -->
            {f'<path d="M {hx-10} {hy} L {hx-10} {hy-10} L {hx} {hy-10}" fill="none" stroke="#666" stroke-width="1"/>' if show_height_line else ''}
        </svg>
        """
    
    def _render_rectangle_svg(self, params: Dict[str, Any]) -> str:
        """Render rectangle diagram SVG with dynamic length and width."""
        length = float(params.get('length', 12))
        width = float(params.get('width', 8))
        show_labels = str(params.get('show_labels', 'true')).lower() == 'true'
        
        # Scale for display
        scale = min(280 / length, 180 / width, 25)
        scaled_length = length * scale
        scaled_width = width * scale
        
        svg_width = 400
        svg_height = 280
        
        # Rectangle position (centered)
        rx = (svg_width - scaled_length) / 2
        ry = (svg_height - scaled_width) / 2 + 20
        
        labels = ""
        if show_labels:
            labels = f'''
            <text x="{rx + scaled_length/2}" y="{ry + scaled_width + 25}" text-anchor="middle" font-size="14" fill="#333">length = {length} cm</text>
            <text x="{rx - 15}" y="{ry + scaled_width/2}" text-anchor="middle" font-size="14" fill="#333" transform="rotate(-90 {rx - 15} {ry + scaled_width/2})">width = {width} cm</text>'''
        
        return f"""
        <svg width="{svg_width}" height="{svg_height}" xmlns="http://www.w3.org/2000/svg">
            <rect width="{svg_width}" height="{svg_height}" fill="#fafafa" stroke="#ddd" stroke-width="1"/>
            <text x="{svg_width/2}" y="25" text-anchor="middle" font-size="16" font-weight="bold" fill="#333">Rectangle</text>
            <rect x="{rx}" y="{ry}" width="{scaled_length}" height="{scaled_width}" fill="#E8F5E9" stroke="#388E3C" stroke-width="3"/>
            {labels}
        </svg>
        """
    
    def _render_circle_svg(self, params: Dict[str, Any]) -> str:
        """Render circle diagram SVG with dynamic radius."""
        radius = float(params.get('radius', 7))
        show_labels = str(params.get('show_labels', 'true')).lower() == 'true'
        show_radius = str(params.get('show_radius', 'true')).lower() == 'true'
        show_diameter = str(params.get('show_diameter', 'false')).lower() == 'true'
        
        # Scale for display
        scale = min(100 / radius, 15)
        scaled_radius = radius * scale
        
        svg_width = 350
        svg_height = 300
        cx = svg_width / 2
        cy = svg_height / 2 + 10
        
        radius_line = ""
        if show_radius:
            radius_line = f'''
            <line x1="{cx}" y1="{cy}" x2="{cx + scaled_radius}" y2="{cy}" stroke="#D32F2F" stroke-width="2"/>
            <text x="{cx + scaled_radius/2}" y="{cy - 10}" text-anchor="middle" font-size="14" fill="#D32F2F">r = {radius} cm</text>'''
        
        diameter_line = ""
        if show_diameter:
            diameter_line = f'''
            <line x1="{cx - scaled_radius}" y1="{cy}" x2="{cx + scaled_radius}" y2="{cy}" stroke="#1976D2" stroke-width="2"/>
            <text x="{cx}" y="{cy + scaled_radius + 25}" text-anchor="middle" font-size="14" fill="#1976D2">d = {radius * 2} cm</text>'''
        
        return f"""
        <svg width="{svg_width}" height="{svg_height}" xmlns="http://www.w3.org/2000/svg">
            <rect width="{svg_width}" height="{svg_height}" fill="#fafafa" stroke="#ddd" stroke-width="1"/>
            <text x="{svg_width/2}" y="25" text-anchor="middle" font-size="16" font-weight="bold" fill="#333">Circle</text>
            <circle cx="{cx}" cy="{cy}" r="{scaled_radius}" fill="#FFF3E0" stroke="#F57C00" stroke-width="3"/>
            <circle cx="{cx}" cy="{cy}" r="4" fill="#F57C00"/>
            {radius_line}
            {diameter_line}
        </svg>
        """
    
    def _render_quadrilateral_svg(self, params: Dict[str, Any]) -> str:
        """Render quadrilateral (square, parallelogram, etc.) SVG."""
        quad_type = params.get('type', 'square')
        side = float(params.get('side', 10))
        show_labels = str(params.get('show_labels', 'true')).lower() == 'true'
        
        scale = min(200 / side, 20)
        scaled_side = side * scale
        
        svg_width = 350
        svg_height = 280
        
        if quad_type == 'square':
            sx = (svg_width - scaled_side) / 2
            sy = (svg_height - scaled_side) / 2 + 15
            shape = f'<rect x="{sx}" y="{sy}" width="{scaled_side}" height="{scaled_side}" fill="#F3E5F5" stroke="#7B1FA2" stroke-width="3"/>'
            label = f'<text x="{sx + scaled_side/2}" y="{sy + scaled_side + 25}" text-anchor="middle" font-size="14" fill="#333">side = {side} cm</text>' if show_labels else ''
        else:
            # Generic parallelogram
            shape = f'<polygon points="..." fill="#F3E5F5" stroke="#7B1FA2" stroke-width="3"/>'
            label = ''
        
        return f"""
        <svg width="{svg_width}" height="{svg_height}" xmlns="http://www.w3.org/2000/svg">
            <rect width="{svg_width}" height="{svg_height}" fill="#fafafa" stroke="#ddd" stroke-width="1"/>
            <text x="{svg_width/2}" y="25" text-anchor="middle" font-size="16" font-weight="bold" fill="#333">{quad_type.title()}</text>
            {shape}
            {label}
        </svg>
        """
    
    def _render_number_line_svg(self, params: Dict[str, Any]) -> str:
        """Render number line diagram SVG."""
        start = int(params.get('start', 0))
        end = int(params.get('end', 10))
        highlight = params.get('highlight', [])
        if isinstance(highlight, str):
            highlight = [int(x) for x in highlight.split(',') if x.strip().isdigit()]
        
        svg_width = 500
        svg_height = 150
        line_y = 80
        padding = 50
        
        # Calculate positions
        range_size = end - start
        tick_spacing = (svg_width - 2 * padding) / range_size
        
        # Build tick marks
        ticks = []
        for i in range(range_size + 1):
            x = padding + i * tick_spacing
            num = start + i
            is_highlighted = num in highlight
            tick_color = "#D32F2F" if is_highlighted else "#333"
            tick_height = 15 if is_highlighted else 10
            font_weight = "bold" if is_highlighted else "normal"
            ticks.append(f'''
                <line x1="{x}" y1="{line_y - tick_height}" x2="{x}" y2="{line_y + tick_height}" stroke="{tick_color}" stroke-width="2"/>
                <text x="{x}" y="{line_y + 35}" text-anchor="middle" font-size="14" fill="{tick_color}" font-weight="{font_weight}">{num}</text>
                {f'<circle cx="{x}" cy="{line_y}" r="6" fill="#D32F2F"/>' if is_highlighted else ''}''')
        
        return f"""
        <svg width="{svg_width}" height="{svg_height}" xmlns="http://www.w3.org/2000/svg">
            <rect width="{svg_width}" height="{svg_height}" fill="#fafafa" stroke="#ddd" stroke-width="1"/>
            <text x="{svg_width/2}" y="25" text-anchor="middle" font-size="16" font-weight="bold" fill="#333">Number Line</text>
            <line x1="{padding - 20}" y1="{line_y}" x2="{svg_width - padding + 20}" y2="{line_y}" stroke="#333" stroke-width="3" marker-end="url(#arrowhead)"/>
            <defs>
                <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
                    <polygon points="0 0, 10 3.5, 0 7" fill="#333"/>
                </marker>
            </defs>
            {''.join(ticks)}
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

    # ============================================================
    # DATA VISUALIZATION DIAGRAMS
    # ============================================================
    
    def _render_bar_chart_svg(self, params: Dict[str, Any]) -> str:
        """Render bar chart SVG with dynamic data."""
        import math
        
        title = params.get('title', 'Bar Chart')
        labels = params.get('labels', [])
        values = params.get('values', [])
        colors = params.get('colors', ['#4CAF50', '#2196F3', '#FF9800', '#9C27B0', '#F44336', '#00BCD4'])
        show_values = str(params.get('show_values', 'true')).lower() == 'true'
        
        # Parse if strings
        if isinstance(labels, str):
            labels = [l.strip() for l in labels.split(',')]
        if isinstance(values, str):
            values = [float(v.strip()) for v in values.split(',')]
        
        if not labels or not values:
            return self._render_empty_diagram("No data provided for bar chart")
        
        # Ensure same length
        min_len = min(len(labels), len(values))
        labels = labels[:min_len]
        values = values[:min_len]
        
        svg_width = 500
        svg_height = 350
        padding = 60
        chart_width = svg_width - 2 * padding
        chart_height = svg_height - 2 * padding - 30
        
        max_value = max(values) if values else 1
        bar_width = chart_width / len(values) * 0.7
        gap = chart_width / len(values) * 0.3
        
        bars = []
        for i, (label, value) in enumerate(zip(labels, values)):
            bar_height = (value / max_value) * chart_height if max_value > 0 else 0
            x = padding + i * (bar_width + gap) + gap / 2
            y = svg_height - padding - bar_height
            color = colors[i % len(colors)]
            
            bars.append(f'''
                <rect x="{x}" y="{y}" width="{bar_width}" height="{bar_height}" fill="{color}" rx="3"/>
                <text x="{x + bar_width/2}" y="{svg_height - padding + 20}" text-anchor="middle" font-size="11" fill="#333">{label}</text>
                {f'<text x="{x + bar_width/2}" y="{y - 5}" text-anchor="middle" font-size="12" fill="#333">{value}</text>' if show_values else ''}
            ''')
        
        # Y-axis labels
        y_labels = []
        for i in range(5):
            y_val = max_value * (4 - i) / 4
            y_pos = padding + 30 + i * (chart_height / 4)
            y_labels.append(f'<text x="{padding - 10}" y="{y_pos + 4}" text-anchor="end" font-size="10" fill="#666">{y_val:.0f}</text>')
            y_labels.append(f'<line x1="{padding}" y1="{y_pos}" x2="{svg_width - padding}" y2="{y_pos}" stroke="#eee" stroke-width="1"/>')
        
        return f"""
        <svg width="{svg_width}" height="{svg_height}" xmlns="http://www.w3.org/2000/svg">
            <rect width="{svg_width}" height="{svg_height}" fill="#fafafa" stroke="#ddd" stroke-width="1"/>
            <text x="{svg_width/2}" y="25" text-anchor="middle" font-size="16" font-weight="bold" fill="#333">{title}</text>
            {''.join(y_labels)}
            <line x1="{padding}" y1="{svg_height - padding}" x2="{svg_width - padding}" y2="{svg_height - padding}" stroke="#333" stroke-width="2"/>
            <line x1="{padding}" y1="{padding + 30}" x2="{padding}" y2="{svg_height - padding}" stroke="#333" stroke-width="2"/>
            {''.join(bars)}
        </svg>
        """
    
    def _render_pie_chart_svg(self, params: Dict[str, Any]) -> str:
        """Render pie chart SVG with dynamic data."""
        import math
        
        title = params.get('title', 'Pie Chart')
        labels = params.get('labels', [])
        values = params.get('values', [])
        colors = params.get('colors', ['#4CAF50', '#2196F3', '#FF9800', '#9C27B0', '#F44336', '#00BCD4', '#795548', '#607D8B'])
        show_percentages = str(params.get('show_percentages', 'true')).lower() == 'true'
        
        # Parse if strings
        if isinstance(labels, str):
            labels = [l.strip() for l in labels.split(',')]
        if isinstance(values, str):
            values = [float(v.strip()) for v in values.split(',')]
        
        if not labels or not values:
            return self._render_empty_diagram("No data provided for pie chart")
        
        svg_width = 450
        svg_height = 350
        cx, cy = svg_width / 2 - 50, svg_height / 2 + 10
        radius = 100
        
        total = sum(values) if values else 1
        
        # Generate pie slices
        slices = []
        legend = []
        start_angle = -90  # Start from top
        
        for i, (label, value) in enumerate(zip(labels, values)):
            percentage = (value / total * 100) if total > 0 else 0
            angle = (value / total * 360) if total > 0 else 0
            end_angle = start_angle + angle
            
            # Calculate arc path
            start_rad = math.radians(start_angle)
            end_rad = math.radians(end_angle)
            
            x1 = cx + radius * math.cos(start_rad)
            y1 = cy + radius * math.sin(start_rad)
            x2 = cx + radius * math.cos(end_rad)
            y2 = cy + radius * math.sin(end_rad)
            
            large_arc = 1 if angle > 180 else 0
            color = colors[i % len(colors)]
            
            # Create slice path
            path = f"M {cx} {cy} L {x1} {y1} A {radius} {radius} 0 {large_arc} 1 {x2} {y2} Z"
            slices.append(f'<path d="{path}" fill="{color}" stroke="white" stroke-width="2"/>')
            
            # Label position (at midpoint of arc)
            mid_angle = math.radians(start_angle + angle / 2)
            label_radius = radius * 0.65
            lx = cx + label_radius * math.cos(mid_angle)
            ly = cy + label_radius * math.sin(mid_angle)
            if show_percentages and percentage >= 5:
                slices.append(f'<text x="{lx}" y="{ly}" text-anchor="middle" font-size="11" fill="white" font-weight="bold">{percentage:.0f}%</text>')
            
            # Legend entry
            legend_y = 60 + i * 22
            legend.append(f'''
                <rect x="{svg_width - 140}" y="{legend_y}" width="15" height="15" fill="{color}" rx="2"/>
                <text x="{svg_width - 120}" y="{legend_y + 12}" font-size="11" fill="#333">{label}</text>
            ''')
            
            start_angle = end_angle
        
        return f"""
        <svg width="{svg_width}" height="{svg_height}" xmlns="http://www.w3.org/2000/svg">
            <rect width="{svg_width}" height="{svg_height}" fill="#fafafa" stroke="#ddd" stroke-width="1"/>
            <text x="{cx}" y="25" text-anchor="middle" font-size="16" font-weight="bold" fill="#333">{title}</text>
            {''.join(slices)}
            {''.join(legend)}
        </svg>
        """
    
    def _render_coordinate_plane_svg(self, params: Dict[str, Any]) -> str:
        """Render coordinate plane with optional points and lines."""
        title = params.get('title', 'Coordinate Plane')
        x_min = int(params.get('x_min', -10))
        x_max = int(params.get('x_max', 10))
        y_min = int(params.get('y_min', -10))
        y_max = int(params.get('y_max', 10))
        points = params.get('points', [])  # List of {"x": 3, "y": 4, "label": "A"}
        show_grid = str(params.get('show_grid', 'true')).lower() == 'true'
        draw_line = str(params.get('draw_line', 'false')).lower() == 'true'
        
        # Parse points if string
        if isinstance(points, str):
            import json
            try:
                points = json.loads(points)
            except:
                points = []
        
        svg_width = 400
        svg_height = 400
        padding = 40
        
        # Scale factors
        x_range = x_max - x_min
        y_range = y_max - y_min
        scale_x = (svg_width - 2 * padding) / x_range
        scale_y = (svg_height - 2 * padding) / y_range
        
        # Origin position
        origin_x = padding + (-x_min) * scale_x
        origin_y = svg_height - padding - (-y_min) * scale_y
        
        # Grid lines
        grid_lines = []
        if show_grid:
            for x in range(x_min, x_max + 1):
                px = padding + (x - x_min) * scale_x
                grid_lines.append(f'<line x1="{px}" y1="{padding}" x2="{px}" y2="{svg_height - padding}" stroke="#eee" stroke-width="1"/>')
            for y in range(y_min, y_max + 1):
                py = svg_height - padding - (y - y_min) * scale_y
                grid_lines.append(f'<line x1="{padding}" y1="{py}" x2="{svg_width - padding}" y2="{py}" stroke="#eee" stroke-width="1"/>')
        
        # Axes
        axes = f'''
            <line x1="{padding}" y1="{origin_y}" x2="{svg_width - padding}" y2="{origin_y}" stroke="#333" stroke-width="2" marker-end="url(#arrow)"/>
            <line x1="{origin_x}" y1="{svg_height - padding}" x2="{origin_x}" y2="{padding}" stroke="#333" stroke-width="2" marker-end="url(#arrow)"/>
            <text x="{svg_width - padding + 15}" y="{origin_y + 5}" font-size="14" fill="#333">x</text>
            <text x="{origin_x + 5}" y="{padding - 10}" font-size="14" fill="#333">y</text>
        '''
        
        # Axis labels (every 2 units)
        axis_labels = []
        for x in range(x_min, x_max + 1, 2):
            if x != 0:
                px = padding + (x - x_min) * scale_x
                axis_labels.append(f'<text x="{px}" y="{origin_y + 15}" text-anchor="middle" font-size="10" fill="#666">{x}</text>')
        for y in range(y_min, y_max + 1, 2):
            if y != 0:
                py = svg_height - padding - (y - y_min) * scale_y
                axis_labels.append(f'<text x="{origin_x - 10}" y="{py + 4}" text-anchor="end" font-size="10" fill="#666">{y}</text>')
        
        # Points
        point_elements = []
        sorted_points = sorted(points, key=lambda p: p.get('x', 0)) if points else []
        for point in sorted_points:
            px = padding + (point.get('x', 0) - x_min) * scale_x
            py = svg_height - padding - (point.get('y', 0) - y_min) * scale_y
            label = point.get('label', '')
            color = point.get('color', '#D32F2F')
            point_elements.append(f'''
                <circle cx="{px}" cy="{py}" r="5" fill="{color}"/>
                <text x="{px + 8}" y="{py - 8}" font-size="12" fill="{color}" font-weight="bold">{label}</text>
                <text x="{px + 8}" y="{py + 15}" font-size="10" fill="#666">({point.get('x', 0)}, {point.get('y', 0)})</text>
            ''')
        
        # Line connecting points
        line_path = ""
        if draw_line and len(sorted_points) >= 2:
            path_points = []
            for point in sorted_points:
                px = padding + (point.get('x', 0) - x_min) * scale_x
                py = svg_height - padding - (point.get('y', 0) - y_min) * scale_y
                path_points.append(f"{px},{py}")
            line_path = f'<polyline points="{" ".join(path_points)}" fill="none" stroke="#2196F3" stroke-width="2"/>'
        
        return f"""
        <svg width="{svg_width}" height="{svg_height}" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">
                    <polygon points="0 0, 10 3, 0 6" fill="#333"/>
                </marker>
            </defs>
            <rect width="{svg_width}" height="{svg_height}" fill="#fafafa" stroke="#ddd" stroke-width="1"/>
            <text x="{svg_width/2}" y="20" text-anchor="middle" font-size="14" font-weight="bold" fill="#333">{title}</text>
            {''.join(grid_lines)}
            {axes}
            {''.join(axis_labels)}
            {line_path}
            {''.join(point_elements)}
        </svg>
        """
    
    def _render_line_graph_svg(self, params: Dict[str, Any]) -> str:
        """Render line graph SVG with multiple series support."""
        title = params.get('title', 'Line Graph')
        x_labels = params.get('x_labels', [])
        series = params.get('series', [])  # [{"name": "Sales", "values": [10,20,30], "color": "#4CAF50"}]
        show_points = str(params.get('show_points', 'true')).lower() == 'true'
        
        # Parse if strings
        if isinstance(x_labels, str):
            x_labels = [l.strip() for l in x_labels.split(',')]
        if isinstance(series, str):
            import json
            try:
                series = json.loads(series)
            except:
                series = []
        
        if not x_labels or not series:
            return self._render_empty_diagram("No data provided for line graph")
        
        svg_width = 500
        svg_height = 350
        padding = 60
        
        chart_width = svg_width - 2 * padding
        chart_height = svg_height - 2 * padding - 40
        
        # Find max value across all series
        all_values = []
        for s in series:
            all_values.extend(s.get('values', []))
        max_value = max(all_values) if all_values else 1
        
        # X spacing
        x_spacing = chart_width / (len(x_labels) - 1) if len(x_labels) > 1 else chart_width
        
        # Y-axis
        y_labels = []
        for i in range(5):
            y_val = max_value * (4 - i) / 4
            y_pos = padding + 20 + i * (chart_height / 4)
            y_labels.append(f'<text x="{padding - 10}" y="{y_pos + 4}" text-anchor="end" font-size="10" fill="#666">{y_val:.0f}</text>')
            y_labels.append(f'<line x1="{padding}" y1="{y_pos}" x2="{svg_width - padding}" y2="{y_pos}" stroke="#eee" stroke-width="1"/>')
        
        # X-axis labels
        x_label_elements = []
        for i, label in enumerate(x_labels):
            x = padding + i * x_spacing
            x_label_elements.append(f'<text x="{x}" y="{svg_height - padding + 20}" text-anchor="middle" font-size="11" fill="#333">{label}</text>')
        
        # Series lines
        series_elements = []
        default_colors = ['#4CAF50', '#2196F3', '#FF9800', '#9C27B0', '#F44336']
        legend = []
        
        for idx, s in enumerate(series):
            color = s.get('color', default_colors[idx % len(default_colors)])
            values = s.get('values', [])
            name = s.get('name', f'Series {idx + 1}')
            
            points = []
            point_circles = []
            for i, val in enumerate(values):
                x = padding + i * x_spacing
                y = svg_height - padding - (val / max_value) * chart_height if max_value > 0 else svg_height - padding
                points.append(f"{x},{y}")
                if show_points:
                    point_circles.append(f'<circle cx="{x}" cy="{y}" r="4" fill="{color}"/>')
            
            if points:
                series_elements.append(f'<polyline points="{" ".join(points)}" fill="none" stroke="{color}" stroke-width="2"/>')
                series_elements.extend(point_circles)
            
            # Legend
            legend_y = 30 + idx * 18
            legend.append(f'''
                <line x1="{svg_width - 130}" y1="{legend_y}" x2="{svg_width - 110}" y2="{legend_y}" stroke="{color}" stroke-width="2"/>
                <text x="{svg_width - 105}" y="{legend_y + 4}" font-size="11" fill="#333">{name}</text>
            ''')
        
        return f"""
        <svg width="{svg_width}" height="{svg_height}" xmlns="http://www.w3.org/2000/svg">
            <rect width="{svg_width}" height="{svg_height}" fill="#fafafa" stroke="#ddd" stroke-width="1"/>
            <text x="{svg_width/2 - 50}" y="25" text-anchor="middle" font-size="16" font-weight="bold" fill="#333">{title}</text>
            {''.join(y_labels)}
            {''.join(x_label_elements)}
            <line x1="{padding}" y1="{svg_height - padding}" x2="{svg_width - padding}" y2="{svg_height - padding}" stroke="#333" stroke-width="2"/>
            <line x1="{padding}" y1="{padding + 20}" x2="{padding}" y2="{svg_height - padding}" stroke="#333" stroke-width="2"/>
            {''.join(series_elements)}
            {''.join(legend)}
        </svg>
        """
    
    def _render_fraction_visual_svg(self, params: Dict[str, Any]) -> str:
        """Render visual representation of a fraction (circle or bar)."""
        numerator = int(params.get('numerator', 1))
        denominator = int(params.get('denominator', 4))
        style = params.get('style', 'circle')  # 'circle' or 'bar'
        show_label = str(params.get('show_label', 'true')).lower() == 'true'
        
        svg_width = 300
        svg_height = 200
        
        if style == 'bar':
            # Bar representation
            bar_width = 200
            bar_height = 40
            segment_width = bar_width / denominator
            bx = (svg_width - bar_width) / 2
            by = 70
            
            segments = []
            for i in range(denominator):
                color = '#4CAF50' if i < numerator else '#E0E0E0'
                segments.append(f'<rect x="{bx + i * segment_width}" y="{by}" width="{segment_width - 2}" height="{bar_height}" fill="{color}" stroke="#333" stroke-width="1"/>')
            
            label = f'<text x="{svg_width/2}" y="{by + bar_height + 35}" text-anchor="middle" font-size="18" fill="#333">{numerator}/{denominator}</text>' if show_label else ''
            
            return f"""
            <svg width="{svg_width}" height="{svg_height}" xmlns="http://www.w3.org/2000/svg">
                <rect width="{svg_width}" height="{svg_height}" fill="#fafafa" stroke="#ddd" stroke-width="1"/>
                <text x="{svg_width/2}" y="30" text-anchor="middle" font-size="14" font-weight="bold" fill="#333">Fraction Visual</text>
                {''.join(segments)}
                {label}
            </svg>
            """
        else:
            # Circle (pie) representation
            import math
            cx, cy = svg_width / 2, 90
            radius = 50
            
            # Filled portion
            angle = (numerator / denominator) * 360
            end_angle = -90 + angle
            start_rad = math.radians(-90)
            end_rad = math.radians(end_angle)
            
            x1 = cx + radius * math.cos(start_rad)
            y1 = cy + radius * math.sin(start_rad)
            x2 = cx + radius * math.cos(end_rad)
            y2 = cy + radius * math.sin(end_rad)
            
            large_arc = 1 if angle > 180 else 0
            
            filled_path = f"M {cx} {cy} L {x1} {y1} A {radius} {radius} 0 {large_arc} 1 {x2} {y2} Z"
            
            # Segment lines
            segment_lines = []
            for i in range(denominator):
                seg_angle = -90 + i * (360 / denominator)
                rad = math.radians(seg_angle)
                lx = cx + radius * math.cos(rad)
                ly = cy + radius * math.sin(rad)
                segment_lines.append(f'<line x1="{cx}" y1="{cy}" x2="{lx}" y2="{ly}" stroke="#333" stroke-width="1"/>')
            
            label = f'<text x="{svg_width/2}" y="{cy + radius + 35}" text-anchor="middle" font-size="18" fill="#333">{numerator}/{denominator}</text>' if show_label else ''
            
            return f"""
            <svg width="{svg_width}" height="{svg_height}" xmlns="http://www.w3.org/2000/svg">
                <rect width="{svg_width}" height="{svg_height}" fill="#fafafa" stroke="#ddd" stroke-width="1"/>
                <text x="{svg_width/2}" y="25" text-anchor="middle" font-size="14" font-weight="bold" fill="#333">Fraction Visual</text>
                <circle cx="{cx}" cy="{cy}" r="{radius}" fill="#E0E0E0" stroke="#333" stroke-width="2"/>
                <path d="{filled_path}" fill="#4CAF50"/>
                {''.join(segment_lines)}
                {label}
            </svg>
            """

    # ============================================================
    # CUSTOM SVG TEMPLATE SUPPORT
    # ============================================================
    
    def _render_custom_svg(self, params: Dict[str, Any]) -> str:
        """
        Render a user-provided SVG template with variable substitution.
        
        This allows content writers to create ANY diagram by providing
        SVG markup with {{variable}} placeholders.
        
        This is SAFE because:
        - No code execution, just string replacement
        - SVG is sanitized (script tags, event handlers removed)
        - Variables are HTML-escaped to prevent XSS
        
        Args:
            params: Must contain 'svg_template' and optionally 'variables' dict
                    Variables can also be passed directly in params.
            
        Returns:
            Rendered SVG string
        """
        import html
        import re
        
        svg_template = params.get('svg_template', '')
        
        if not svg_template:
            return self._render_empty_diagram("No SVG template provided")
        
        result = svg_template
        
        # Collect all variables to substitute
        # First, add any direct params (except svg_template and variables)
        variables_to_substitute = {}
        for key, value in params.items():
            if key not in ('svg_template', 'variables'):
                variables_to_substitute[key] = value
        
        # Then, add from nested 'variables' object (takes precedence)
        if 'variables' in params and isinstance(params['variables'], dict):
            variables_to_substitute.update(params['variables'])
        
        # Substitute all {{variable}} placeholders with their values
        for key, value in variables_to_substitute.items():
            # HTML escape to prevent XSS attacks
            safe_value = html.escape(str(value))
            # Replace both {{var}} and {{ var }} (with spaces)
            result = re.sub(
                rf'\{{\{{\s*{re.escape(key)}\s*\}}\}}',
                safe_value,
                result
            )
        
        # Sanitize the final SVG
        result = self._sanitize_svg(result)
        
        return result
    
    def _sanitize_svg(self, svg: str) -> str:
        """
        Remove potentially dangerous elements from SVG.
        
        This prevents XSS attacks when rendering user-provided SVG.
        """
        import re
        
        # Remove script tags and their content
        svg = re.sub(r'<script[^>]*>.*?</script>', '', svg, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove event handlers (onclick, onload, onerror, etc.)
        svg = re.sub(r'\s+on\w+\s*=\s*["\'][^"\']*["\']', '', svg, flags=re.IGNORECASE)
        
        # Remove javascript: URLs
        svg = re.sub(r'javascript\s*:', '', svg, flags=re.IGNORECASE)
        
        # Remove data: URLs that could contain scripts
        svg = re.sub(r'data\s*:\s*text/html', 'data:blocked', svg, flags=re.IGNORECASE)
        
        # Remove foreignObject elements (can contain HTML)
        svg = re.sub(r'<foreignObject[^>]*>.*?</foreignObject>', '', svg, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove use elements pointing to external resources
        svg = re.sub(r'<use[^>]*xlink:href\s*=\s*["\']http[^"\']*["\'][^>]*/>', '', svg, flags=re.IGNORECASE)
        
        return svg
    
    def _render_angle_diagram_svg(self, params: Dict[str, Any]) -> str:
        """Render an angle diagram with two rays, arc, and degree label."""
        import math
        
        angle_degrees = float(params.get('angle', 45))
        label = params.get('label', f'{angle_degrees}°')
        ray_length = int(params.get('ray_length', 100))
        show_arc = str(params.get('show_arc', 'true')).lower() == 'true'
        arc_radius = int(params.get('arc_radius', 30))
        color = params.get('color', '#2196F3')
        
        svg_width = 300
        svg_height = 250
        cx = 150  # Vertex x
        cy = 180  # Vertex y (lower to leave room for label above)
        
        # Calculate ray endpoints
        # First ray is horizontal to the right
        ray1_end_x = cx + ray_length
        ray1_end_y = cy
        
        # Second ray at the specified angle (measured counterclockwise from horizontal)
        angle_rad = math.radians(angle_degrees)
        ray2_end_x = cx + ray_length * math.cos(angle_rad)
        ray2_end_y = cy - ray_length * math.sin(angle_rad)  # Negative because SVG y increases downward
        
        # Arc path
        arc_path = ""
        if show_arc:
            arc_start_x = cx + arc_radius
            arc_start_y = cy
            arc_end_x = cx + arc_radius * math.cos(angle_rad)
            arc_end_y = cy - arc_radius * math.sin(angle_rad)
            
            # Determine if we need a large arc (angle > 180)
            large_arc = 1 if angle_degrees > 180 else 0
            
            arc_path = f'''
                <path d="M {arc_start_x},{arc_start_y} A {arc_radius},{arc_radius} 0 {large_arc},0 {arc_end_x},{arc_end_y}" 
                      fill="none" stroke="{color}" stroke-width="2"/>
            '''
        
        # Angle label position (midpoint of arc)
        label_angle_rad = math.radians(angle_degrees / 2)
        label_radius = arc_radius + 15
        label_x = cx + label_radius * math.cos(label_angle_rad)
        label_y = cy - label_radius * math.sin(label_angle_rad)
        
        # Title/description
        title = params.get('title', f'Angle: {angle_degrees}°')
        
        return f"""
        <svg width="{svg_width}" height="{svg_height}" xmlns="http://www.w3.org/2000/svg">
            <rect width="{svg_width}" height="{svg_height}" fill="#fafafa" stroke="#ddd" stroke-width="1"/>
            <text x="{svg_width/2}" y="25" text-anchor="middle" font-size="14" font-weight="bold" fill="#333">{title}</text>
            
            <!-- Vertex point -->
            <circle cx="{cx}" cy="{cy}" r="4" fill="#333"/>
            
            <!-- Ray 1 (horizontal) -->
            <line x1="{cx}" y1="{cy}" x2="{ray1_end_x}" y2="{ray1_end_y}" 
                  stroke="#333" stroke-width="2" marker-end="url(#arrow)"/>
            
            <!-- Ray 2 (at angle) -->
            <line x1="{cx}" y1="{cy}" x2="{ray2_end_x}" y2="{ray2_end_y}" 
                  stroke="#333" stroke-width="2" marker-end="url(#arrow)"/>
            
            <!-- Arc showing the angle -->
            {arc_path}
            
            <!-- Angle label -->
            <text x="{label_x}" y="{label_y}" text-anchor="middle" font-size="14" fill="{color}" font-weight="bold">{label}</text>
            
            <!-- Arrow marker definition -->
            <defs>
                <marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">
                    <polygon points="0 0, 10 3, 0 6" fill="#333"/>
                </marker>
            </defs>
        </svg>
        """
    
    def _render_empty_diagram(self, message: str) -> str:
        """Render a placeholder diagram with an error/info message."""
        import html
        safe_message = html.escape(message)
        return f'''
        <svg width="400" height="200" xmlns="http://www.w3.org/2000/svg">
            <rect width="400" height="200" fill="#f5f5f5" stroke="#ddd" stroke-width="2"/>
            <text x="200" y="90" text-anchor="middle" font-family="Arial" font-size="14" fill="#999">📋</text>
            <text x="200" y="115" text-anchor="middle" font-family="Arial" font-size="12" fill="#666">{safe_message}</text>
        </svg>
        '''

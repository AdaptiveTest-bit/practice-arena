"""
Function Library - Reusable function collections for templates.

Allows content writers to:
1. Define reusable function libraries (e.g., "chemistry_basics", "geometry_helpers")
2. Import libraries into templates
3. Share functions across multiple templates

Usage in templates:
{
    "variables": {
        "use_libraries": ["chemistry_basics", "geometry_helpers"],
        "custom_functions": {
            "my_local_func": {"params": ["x"], "body": "x * 2"}
        }
    }
}
"""

import json
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class FunctionDefinition:
    """A single function definition."""
    name: str
    params: List[str]
    body: str
    description: Optional[str] = None
    examples: List[str] = field(default_factory=list)


@dataclass
class FunctionLibrary:
    """A collection of related functions."""
    name: str
    description: str
    subject: str  # math, chemistry, physics, etc.
    functions: Dict[str, FunctionDefinition] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "description": self.description,
            "subject": self.subject,
            "functions": {
                name: {
                    "params": func.params,
                    "body": func.body,
                    "description": func.description,
                    "examples": func.examples
                }
                for name, func in self.functions.items()
            }
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FunctionLibrary":
        """Create from dictionary."""
        library = cls(
            name=data["name"],
            description=data.get("description", ""),
            subject=data.get("subject", "general")
        )
        for name, func_data in data.get("functions", {}).items():
            library.functions[name] = FunctionDefinition(
                name=name,
                params=func_data.get("params", []),
                body=func_data.get("body", ""),
                description=func_data.get("description"),
                examples=func_data.get("examples", [])
            )
        return library


class FunctionLibraryRegistry:
    """
    Registry for managing function libraries.
    
    Libraries can be:
    1. Built-in (defined in code)
    2. Loaded from YAML/JSON files
    3. Stored in database (future)
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize with built-in libraries."""
        self._libraries: Dict[str, FunctionLibrary] = {}
        self._register_builtin_libraries()
    
    def _register_builtin_libraries(self):
        """Register built-in function libraries."""
        
        # =====================================================================
        # MATH HELPERS
        # =====================================================================
        math_helpers = FunctionLibrary(
            name="math_helpers",
            description="Common math helper functions for K-12",
            subject="math"
        )
        math_helpers.functions = {
            "is_even": FunctionDefinition(
                name="is_even",
                params=["n"],
                body="n % 2 == 0",
                description="Check if a number is even",
                examples=["is_even(4) → True", "is_even(7) → False"]
            ),
            "is_odd": FunctionDefinition(
                name="is_odd",
                params=["n"],
                body="n % 2 != 0",
                description="Check if a number is odd"
            ),
            "is_multiple_of": FunctionDefinition(
                name="is_multiple_of",
                params=["n", "m"],
                body="n % m == 0",
                description="Check if n is a multiple of m"
            ),
            "digit_sum": FunctionDefinition(
                name="digit_sum",
                params=["n"],
                body="sum(int(d) for d in str(abs(int(n))))",
                description="Sum of digits of a number"
            ),
            "digit_count": FunctionDefinition(
                name="digit_count",
                params=["n"],
                body="len(str(abs(int(n))))",
                description="Count of digits in a number"
            ),
            "reverse_digits": FunctionDefinition(
                name="reverse_digits",
                params=["n"],
                body="int(str(abs(int(n)))[::-1]) * (1 if n >= 0 else -1)",
                description="Reverse the digits of a number"
            ),
            "is_palindrome_number": FunctionDefinition(
                name="is_palindrome_number",
                params=["n"],
                body="str(abs(int(n))) == str(abs(int(n)))[::-1]",
                description="Check if number is palindrome"
            ),
            "next_multiple": FunctionDefinition(
                name="next_multiple",
                params=["n", "m"],
                body="((n // m) + 1) * m",
                description="Find next multiple of m after n"
            ),
            "prev_multiple": FunctionDefinition(
                name="prev_multiple",
                params=["n", "m"],
                body="(n // m) * m",
                description="Find previous multiple of m before or at n"
            ),
        }
        self._libraries["math_helpers"] = math_helpers
        
        # =====================================================================
        # NUMBER THEORY
        # =====================================================================
        number_theory = FunctionLibrary(
            name="number_theory",
            description="Number theory functions for olympiad prep",
            subject="math"
        )
        number_theory.functions = {
            "is_perfect_square": FunctionDefinition(
                name="is_perfect_square",
                params=["n"],
                body="n >= 0 and int(sqrt(n)) ** 2 == n",
                description="Check if n is a perfect square"
            ),
            "is_perfect_cube": FunctionDefinition(
                name="is_perfect_cube",
                params=["n"],
                body="round(abs(n) ** (1/3)) ** 3 == abs(n)",
                description="Check if n is a perfect cube"
            ),
            "count_divisors": FunctionDefinition(
                name="count_divisors",
                params=["n"],
                body="len([i for i in range(1, int(n) + 1) if n % i == 0])",
                description="Count of divisors of n"
            ),
            "sum_divisors": FunctionDefinition(
                name="sum_divisors",
                params=["n"],
                body="sum(i for i in range(1, int(n) + 1) if n % i == 0)",
                description="Sum of divisors of n"
            ),
            "is_perfect_number": FunctionDefinition(
                name="is_perfect_number",
                params=["n"],
                body="sum(i for i in range(1, int(n)) if n % i == 0) == n",
                description="Check if n equals sum of its proper divisors"
            ),
            "euler_phi": FunctionDefinition(
                name="euler_phi",
                params=["n"],
                body="len([i for i in range(1, int(n) + 1) if gcd(i, n) == 1])",
                description="Euler's totient function"
            ),
        }
        self._libraries["number_theory"] = number_theory
        
        # =====================================================================
        # GEOMETRY HELPERS
        # =====================================================================
        geometry = FunctionLibrary(
            name="geometry_helpers",
            description="Geometry helper functions",
            subject="math"
        )
        geometry.functions = {
            "is_right_triangle": FunctionDefinition(
                name="is_right_triangle",
                params=["a", "b", "c"],
                body="a*a + b*b == c*c or b*b + c*c == a*a or a*a + c*c == b*b",
                description="Check if sides form a right triangle"
            ),
            "is_valid_triangle": FunctionDefinition(
                name="is_valid_triangle",
                params=["a", "b", "c"],
                body="a + b > c and b + c > a and a + c > b",
                description="Check if sides can form a valid triangle"
            ),
            "triangle_type": FunctionDefinition(
                name="triangle_type",
                params=["a", "b", "c"],
                body="'equilateral' if a == b == c else ('isosceles' if a == b or b == c or a == c else 'scalene')",
                description="Get type of triangle: equilateral, isosceles, or scalene"
            ),
            "heron_area": FunctionDefinition(
                name="heron_area",
                params=["a", "b", "c"],
                body="sqrt((a+b+c)/2 * ((a+b+c)/2-a) * ((a+b+c)/2-b) * ((a+b+c)/2-c))",
                description="Calculate triangle area using Heron's formula"
            ),
            "diagonal_rectangle": FunctionDefinition(
                name="diagonal_rectangle",
                params=["l", "w"],
                body="sqrt(l*l + w*w)",
                description="Diagonal of a rectangle"
            ),
            "diagonal_cube": FunctionDefinition(
                name="diagonal_cube",
                params=["s"],
                body="s * sqrt(3)",
                description="Space diagonal of a cube"
            ),
            "circle_area": FunctionDefinition(
                name="circle_area",
                params=["r"],
                body="3.14159265359 * r * r",
                description="Area of a circle (π * r²)"
            ),
            "circle_circumference": FunctionDefinition(
                name="circle_circumference",
                params=["r"],
                body="2 * 3.14159265359 * r",
                description="Circumference of a circle (2πr)"
            ),
            "rectangle_area": FunctionDefinition(
                name="rectangle_area",
                params=["l", "w"],
                body="l * w",
                description="Area of a rectangle"
            ),
            "rectangle_perimeter": FunctionDefinition(
                name="rectangle_perimeter",
                params=["l", "w"],
                body="2 * (l + w)",
                description="Perimeter of a rectangle"
            ),
            "square_area": FunctionDefinition(
                name="square_area",
                params=["s"],
                body="s * s",
                description="Area of a square"
            ),
            "square_perimeter": FunctionDefinition(
                name="square_perimeter",
                params=["s"],
                body="4 * s",
                description="Perimeter of a square"
            ),
            "triangle_area": FunctionDefinition(
                name="triangle_area",
                params=["base", "height"],
                body="0.5 * base * height",
                description="Area of a triangle (½ × base × height)"
            ),
            "cylinder_volume": FunctionDefinition(
                name="cylinder_volume",
                params=["r", "h"],
                body="3.14159265359 * r * r * h",
                description="Volume of a cylinder (πr²h)"
            ),
            "cone_volume": FunctionDefinition(
                name="cone_volume",
                params=["r", "h"],
                body="(1/3) * 3.14159265359 * r * r * h",
                description="Volume of a cone (⅓πr²h)"
            ),
            "sphere_volume": FunctionDefinition(
                name="sphere_volume",
                params=["r"],
                body="(4/3) * 3.14159265359 * r * r * r",
                description="Volume of a sphere (⁴⁄₃πr³)"
            ),
            "cube_volume": FunctionDefinition(
                name="cube_volume",
                params=["s"],
                body="s * s * s",
                description="Volume of a cube (s³)"
            ),
            "cuboid_volume": FunctionDefinition(
                name="cuboid_volume",
                params=["l", "w", "h"],
                body="l * w * h",
                description="Volume of a cuboid (l × w × h)"
            ),
        }
        self._libraries["geometry_helpers"] = geometry
        
        # =====================================================================
        # CHEMISTRY BASICS
        # =====================================================================
        chemistry = FunctionLibrary(
            name="chemistry_basics",
            description="Basic chemistry functions for Class 8-10",
            subject="chemistry"
        )
        chemistry.functions = {
            "molar_mass_water": FunctionDefinition(
                name="molar_mass_water",
                params=[],
                body="18",
                description="Molar mass of H2O in g/mol"
            ),
            "molar_mass_co2": FunctionDefinition(
                name="molar_mass_co2",
                params=[],
                body="44",
                description="Molar mass of CO2 in g/mol"
            ),
            "moles_from_mass": FunctionDefinition(
                name="moles_from_mass",
                params=["mass", "molar_mass"],
                body="mass / molar_mass",
                description="Calculate moles from mass and molar mass"
            ),
            "mass_from_moles": FunctionDefinition(
                name="mass_from_moles",
                params=["moles", "molar_mass"],
                body="moles * molar_mass",
                description="Calculate mass from moles and molar mass"
            ),
            "water_from_h2_o2": FunctionDefinition(
                name="water_from_h2_o2",
                params=["h2_moles", "o2_moles"],
                body="min(h2_moles, o2_moles * 2)",
                description="H2O produced: 2H2 + O2 → 2H2O"
            ),
            "limiting_reagent_h2o": FunctionDefinition(
                name="limiting_reagent_h2o",
                params=["h2_moles", "o2_moles"],
                body="'H2' if h2_moles < o2_moles * 2 else 'O2'",
                description="Find limiting reagent for water synthesis"
            ),
        }
        self._libraries["chemistry_basics"] = chemistry
        
        # =====================================================================
        # PHYSICS BASICS
        # =====================================================================
        physics = FunctionLibrary(
            name="physics_basics",
            description="Basic physics functions for Class 8-10",
            subject="physics"
        )
        physics.functions = {
            "speed": FunctionDefinition(
                name="speed",
                params=["distance", "time"],
                body="distance / time if time != 0 else 0",
                description="Calculate speed = distance / time"
            ),
            "distance": FunctionDefinition(
                name="distance",
                params=["speed", "time"],
                body="speed * time",
                description="Calculate distance = speed × time"
            ),
            "time_taken": FunctionDefinition(
                name="time_taken",
                params=["distance", "speed"],
                body="distance / speed if speed != 0 else 0",
                description="Calculate time = distance / speed"
            ),
            "kinetic_energy": FunctionDefinition(
                name="kinetic_energy",
                params=["mass", "velocity"],
                body="0.5 * mass * velocity * velocity",
                description="KE = ½mv²"
            ),
            "potential_energy": FunctionDefinition(
                name="potential_energy",
                params=["mass", "height", "g"],
                body="mass * g * height",
                description="PE = mgh"
            ),
            "momentum": FunctionDefinition(
                name="momentum",
                params=["mass", "velocity"],
                body="mass * velocity",
                description="p = mv"
            ),
            "force": FunctionDefinition(
                name="force",
                params=["mass", "acceleration"],
                body="mass * acceleration",
                description="F = ma"
            ),
            "work_done": FunctionDefinition(
                name="work_done",
                params=["force", "displacement"],
                body="force * displacement",
                description="W = F × d"
            ),
            "power": FunctionDefinition(
                name="power",
                params=["work", "time"],
                body="work / time if time != 0 else 0",
                description="P = W / t"
            ),
            "density": FunctionDefinition(
                name="density",
                params=["mass", "volume"],
                body="mass / volume if volume != 0 else 0",
                description="ρ = m / V"
            ),
            "pressure": FunctionDefinition(
                name="pressure",
                params=["force", "area"],
                body="force / area if area != 0 else 0",
                description="P = F / A"
            ),
        }
        self._libraries["physics_basics"] = physics
        
        # =====================================================================
        # PERCENTAGE & RATIO
        # =====================================================================
        percentage = FunctionLibrary(
            name="percentage_ratio",
            description="Percentage and ratio calculations",
            subject="math"
        )
        percentage.functions = {
            "percentage": FunctionDefinition(
                name="percentage",
                params=["part", "whole"],
                body="(part / whole) * 100 if whole != 0 else 0",
                description="Calculate percentage"
            ),
            "percentage_of": FunctionDefinition(
                name="percentage_of",
                params=["percent", "total"],
                body="(percent / 100) * total",
                description="Find percentage of a number"
            ),
            "percent_increase": FunctionDefinition(
                name="percent_increase",
                params=["old_val", "new_val"],
                body="((new_val - old_val) / old_val) * 100 if old_val != 0 else 0",
                description="Calculate percentage increase"
            ),
            "percent_decrease": FunctionDefinition(
                name="percent_decrease",
                params=["old_val", "new_val"],
                body="((old_val - new_val) / old_val) * 100 if old_val != 0 else 0",
                description="Calculate percentage decrease"
            ),
            "ratio_simplify_gcd": FunctionDefinition(
                name="ratio_simplify_gcd",
                params=["a", "b"],
                body="gcd(int(a), int(b))",
                description="Get GCD to simplify ratio a:b"
            ),
            "profit_percent": FunctionDefinition(
                name="profit_percent",
                params=["cp", "sp"],
                body="((sp - cp) / cp) * 100 if cp != 0 else 0",
                description="Calculate profit percentage"
            ),
            "loss_percent": FunctionDefinition(
                name="loss_percent",
                params=["cp", "sp"],
                body="((cp - sp) / cp) * 100 if cp != 0 else 0",
                description="Calculate loss percentage"
            ),
            "simple_interest": FunctionDefinition(
                name="simple_interest",
                params=["principal", "rate", "time"],
                body="(principal * rate * time) / 100",
                description="SI = PRT/100"
            ),
            "compound_amount": FunctionDefinition(
                name="compound_amount",
                params=["principal", "rate", "time"],
                body="principal * ((1 + rate/100) ** time)",
                description="A = P(1 + R/100)^T"
            ),
        }
        self._libraries["percentage_ratio"] = percentage
        
        logger.info(f"Registered {len(self._libraries)} built-in function libraries")
    
    def get_library(self, name: str) -> Optional[FunctionLibrary]:
        """Get a library by name."""
        return self._libraries.get(name)
    
    def list_libraries(self) -> List[str]:
        """List all available library names."""
        return list(self._libraries.keys())
    
    def list_libraries_by_subject(self, subject: str) -> List[str]:
        """List libraries for a specific subject."""
        return [
            name for name, lib in self._libraries.items()
            if lib.subject == subject
        ]
    
    def get_functions_from_libraries(
        self,
        library_names: List[str]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Get all functions from specified libraries.
        
        Returns functions in the format expected by VariableGenerator.
        """
        functions = {}
        
        for lib_name in library_names:
            library = self.get_library(lib_name)
            if library:
                for func_name, func_def in library.functions.items():
                    functions[func_name] = {
                        "params": func_def.params,
                        "body": func_def.body
                    }
            else:
                logger.warning(f"Library '{lib_name}' not found")
        
        return functions
    
    def register_library(self, library: FunctionLibrary):
        """Register a new library."""
        self._libraries[library.name] = library
        logger.info(f"Registered library: {library.name}")
    
    def load_library_from_file(self, file_path: str) -> Optional[FunctionLibrary]:
        """Load a library from a JSON/YAML file."""
        path = Path(file_path)
        
        if not path.exists():
            logger.error(f"Library file not found: {file_path}")
            return None
        
        try:
            with open(path) as f:
                if path.suffix in ('.yaml', '.yml'):
                    import yaml
                    data = yaml.safe_load(f)
                else:
                    data = json.load(f)
            
            library = FunctionLibrary.from_dict(data)
            self.register_library(library)
            return library
            
        except Exception as e:
            logger.error(f"Failed to load library from {file_path}: {e}")
            return None
    
    def get_library_documentation(self, name: str) -> Optional[str]:
        """Get documentation for a library."""
        library = self.get_library(name)
        if not library:
            return None
        
        lines = [
            f"# {library.name}",
            f"Subject: {library.subject}",
            f"Description: {library.description}",
            "",
            "## Functions",
            ""
        ]
        
        for func_name, func_def in library.functions.items():
            params_str = ", ".join(func_def.params)
            lines.append(f"### {func_name}({params_str})")
            lines.append(f"```")
            lines.append(f"{func_def.body}")
            lines.append(f"```")
            if func_def.description:
                lines.append(f"{func_def.description}")
            if func_def.examples:
                lines.append("Examples:")
                for ex in func_def.examples:
                    lines.append(f"  - {ex}")
            lines.append("")
        
        return "\n".join(lines)


# Singleton instance
function_library_registry = FunctionLibraryRegistry()


def get_library_functions(library_names: List[str]) -> Dict[str, Dict[str, Any]]:
    """Convenience function to get functions from libraries."""
    return function_library_registry.get_functions_from_libraries(library_names)

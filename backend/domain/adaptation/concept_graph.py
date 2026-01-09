"""
Concept Graph - Loads and queries prerequisite relationships from YAML configs.

This module provides:
- Loading concept graphs from backend/config/content/graphs/
- Querying prerequisites for a concept
- Finding ready-to-learn concepts based on mastered prerequisites
- Topological ordering for optimal learning paths
"""

import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
from pathlib import Path

import yaml


@dataclass
class ConceptNode:
    """A concept in the learning graph."""
    concept_id: str
    bloom_targets: List[str] = field(default_factory=list)
    difficulty_default: int = 2
    description: str = ""


@dataclass  
class ConceptEdge:
    """A prerequisite relationship between concepts."""
    from_concept: str
    to_concept: str
    kind: str  # "prerequisite" or "co_requisite"
    reason: str = ""


class ConceptGraph:
    """
    Loads and queries concept prerequisite graphs.
    
    Usage:
        graph = ConceptGraph.load("math", 5, "factors_multiples")
        prereqs = graph.get_prerequisites("math.class5.factors_multiples.gcd")
        ready = graph.get_ready_concepts(mastered={"divisibility", "factors"})
    """
    
    def __init__(self):
        self.nodes: Dict[str, ConceptNode] = {}
        self.edges: List[ConceptEdge] = []
        self.chapter_id: str = ""
        self.subject: str = ""
        self.grade: int = 0
        
        # Adjacency lists for graph traversal
        self._prerequisites: Dict[str, Set[str]] = {}  # concept -> set of prerequisites
        self._dependents: Dict[str, Set[str]] = {}      # concept -> set of concepts that depend on it
    
    @classmethod
    def load(cls, subject: str, grade: int, chapter_id: str) -> "ConceptGraph":
        """
        Load concept graph from YAML config file.
        
        Args:
            subject: e.g., "math"
            grade: e.g., 5
            chapter_id: e.g., "factors_multiples"
        
        Returns:
            ConceptGraph instance populated from YAML
        """
        graph = cls()
        graph.subject = subject
        graph.grade = grade
        graph.chapter_id = chapter_id
        
        # Construct path to YAML file
        config_base = Path(__file__).parent.parent.parent / "config" / "content"
        graph_path = config_base / "graphs" / subject / f"class{grade}" / f"{chapter_id}.yaml"
        
        if not graph_path.exists():
            raise FileNotFoundError(f"Concept graph not found: {graph_path}")
        
        with open(graph_path, 'r') as f:
            data = yaml.safe_load(f)
        
        # Parse nodes
        for node_data in data.get("nodes", []):
            concept_id = node_data["concept_id"]
            node = ConceptNode(
                concept_id=concept_id,
                bloom_targets=node_data.get("bloom_targets", []),
                difficulty_default=node_data.get("difficulty_default", 2),
                description=node_data.get("description", ""),
            )
            graph.nodes[concept_id] = node
            graph._prerequisites[concept_id] = set()
            graph._dependents[concept_id] = set()
        
        # Parse edges
        for edge_data in data.get("edges", []):
            edge = ConceptEdge(
                from_concept=edge_data["from"],
                to_concept=edge_data["to"],
                kind=edge_data.get("kind", "prerequisite"),
                reason=edge_data.get("reason", ""),
            )
            graph.edges.append(edge)
            
            # Build adjacency lists for prerequisite edges
            if edge.kind == "prerequisite":
                if edge.to_concept in graph._prerequisites:
                    graph._prerequisites[edge.to_concept].add(edge.from_concept)
                if edge.from_concept in graph._dependents:
                    graph._dependents[edge.from_concept].add(edge.to_concept)
        
        return graph
    
    def get_concept_key(self, concept_id: str) -> str:
        """Extract short concept key from full concept_id."""
        # e.g., "math.class5.factors_multiples.gcd" -> "gcd"
        return concept_id.split(".")[-1]
    
    def get_full_concept_id(self, concept_key: str) -> Optional[str]:
        """Find full concept_id from short key."""
        for concept_id in self.nodes:
            if concept_id.endswith(f".{concept_key}"):
                return concept_id
        return None
    
    def get_prerequisites(self, concept_id: str) -> Set[str]:
        """Get direct prerequisites for a concept."""
        return self._prerequisites.get(concept_id, set())
    
    def get_all_prerequisites(self, concept_id: str, visited: Set[str] = None) -> Set[str]:
        """Get all prerequisites (transitive closure) for a concept."""
        if visited is None:
            visited = set()
        
        direct = self.get_prerequisites(concept_id)
        all_prereqs = set(direct)
        
        for prereq in direct:
            if prereq not in visited:
                visited.add(prereq)
                all_prereqs.update(self.get_all_prerequisites(prereq, visited))
        
        return all_prereqs
    
    def get_dependents(self, concept_id: str) -> Set[str]:
        """Get concepts that depend on this concept."""
        return self._dependents.get(concept_id, set())
    
    def get_ready_concepts(self, mastered: Set[str]) -> List[str]:
        """
        Get concepts that are ready to learn (all prerequisites mastered).
        
        Args:
            mastered: Set of concept_ids that student has mastered
        
        Returns:
            List of concept_ids ready for learning (not yet mastered, but prereqs met)
        """
        ready = []
        
        for concept_id in self.nodes:
            if concept_id in mastered:
                continue  # Already mastered
            
            prereqs = self.get_prerequisites(concept_id)
            if prereqs.issubset(mastered):
                ready.append(concept_id)
        
        return ready
    
    def get_foundation_concepts(self) -> List[str]:
        """Get concepts with no prerequisites (good starting points)."""
        return [
            concept_id for concept_id, prereqs in self._prerequisites.items()
            if len(prereqs) == 0
        ]
    
    def get_topological_order(self) -> List[str]:
        """
        Get concepts in topological order (prerequisites before dependents).
        
        Useful for creating optimal learning paths.
        """
        visited = set()
        order = []
        
        def visit(concept_id: str):
            if concept_id in visited:
                return
            visited.add(concept_id)
            
            for prereq in self.get_prerequisites(concept_id):
                visit(prereq)
            
            order.append(concept_id)
        
        for concept_id in self.nodes:
            visit(concept_id)
        
        return order
    
    def get_node(self, concept_id: str) -> Optional[ConceptNode]:
        """Get concept node by ID."""
        return self.nodes.get(concept_id)
    
    def get_all_concept_ids(self) -> List[str]:
        """Get all concept IDs in the graph."""
        return list(self.nodes.keys())
    
    def get_all_concept_keys(self) -> List[str]:
        """Get all short concept keys."""
        return [self.get_concept_key(cid) for cid in self.nodes.keys()]
    
    def __repr__(self) -> str:
        return f"ConceptGraph({self.subject}/class{self.grade}/{self.chapter_id}, {len(self.nodes)} concepts, {len(self.edges)} edges)"

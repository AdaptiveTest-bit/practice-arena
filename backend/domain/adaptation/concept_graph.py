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

    def save(self) -> Path:
        """
        Save concept graph back to YAML config file.
        
        Returns:
            Path to the saved YAML file
        """
        config_base = Path(__file__).parent.parent.parent / "config" / "content"
        graph_dir = config_base / "graphs" / self.subject / f"class{self.grade}"
        graph_path = graph_dir / f"{self.chapter_id}.yaml"
        
        # Ensure directory exists
        graph_dir.mkdir(parents=True, exist_ok=True)
        
        # Build YAML structure
        data = {
            "chapter_id": self.chapter_id,
            "subject": self.subject,
            "grade": self.grade,
            "nodes": [],
            "edges": []
        }
        
        # Serialize nodes
        for concept_id, node in self.nodes.items():
            node_data = {
                "concept_id": node.concept_id,
                "bloom_targets": node.bloom_targets,
                "difficulty_default": node.difficulty_default,
            }
            if node.description:
                node_data["description"] = node.description
            data["nodes"].append(node_data)
        
        # Serialize edges
        for edge in self.edges:
            edge_data = {
                "from": edge.from_concept,
                "to": edge.to_concept,
                "kind": edge.kind,
            }
            if edge.reason:
                edge_data["reason"] = edge.reason
            data["edges"].append(edge_data)
        
        # Write YAML
        with open(graph_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        return graph_path

    def add_node(self, concept_id: str, bloom_targets: List[str] = None, 
                 difficulty_default: int = 2, description: str = "") -> ConceptNode:
        """
        Add a new concept node to the graph.
        
        Args:
            concept_id: Full concept ID (e.g., math.class5.factors_multiples.new_concept)
            bloom_targets: List of Bloom's taxonomy targets
            difficulty_default: Default difficulty (1-5)
            description: Optional description
        
        Returns:
            The created ConceptNode
        """
        if concept_id in self.nodes:
            raise ValueError(f"Concept {concept_id} already exists")
        
        node = ConceptNode(
            concept_id=concept_id,
            bloom_targets=bloom_targets or ["understand"],
            difficulty_default=difficulty_default,
            description=description,
        )
        self.nodes[concept_id] = node
        self._prerequisites[concept_id] = set()
        self._dependents[concept_id] = set()
        return node

    def add_edge(self, from_concept: str, to_concept: str, 
                 kind: str = "prerequisite", reason: str = "") -> ConceptEdge:
        """
        Add an edge (prerequisite relationship) to the graph.
        
        Args:
            from_concept: Source concept ID
            to_concept: Target concept ID (this concept requires from_concept)
            kind: Edge type ("prerequisite" or "co_requisite")
            reason: Optional explanation
        
        Returns:
            The created ConceptEdge
        """
        if from_concept not in self.nodes:
            raise ValueError(f"Source concept {from_concept} not found in graph")
        if to_concept not in self.nodes:
            raise ValueError(f"Target concept {to_concept} not found in graph")
        
        edge = ConceptEdge(
            from_concept=from_concept,
            to_concept=to_concept,
            kind=kind,
            reason=reason,
        )
        self.edges.append(edge)
        
        # Update adjacency lists
        if kind == "prerequisite":
            self._prerequisites[to_concept].add(from_concept)
            self._dependents[from_concept].add(to_concept)
        
        return edge

    def remove_node(self, concept_id: str) -> bool:
        """
        Remove a concept node and all its edges.
        
        Args:
            concept_id: Concept to remove
        
        Returns:
            True if removed, False if not found
        """
        if concept_id not in self.nodes:
            return False
        
        # Remove all edges involving this concept
        self.edges = [e for e in self.edges 
                      if e.from_concept != concept_id and e.to_concept != concept_id]
        
        # Remove from adjacency lists
        del self._prerequisites[concept_id]
        del self._dependents[concept_id]
        
        # Remove from other concepts' adjacency
        for prereqs in self._prerequisites.values():
            prereqs.discard(concept_id)
        for deps in self._dependents.values():
            deps.discard(concept_id)
        
        # Remove node
        del self.nodes[concept_id]
        return True

    def update_from_dict(self, data: dict) -> None:
        """
        Update graph from dictionary (typically from API request).
        
        Args:
            data: Dict with 'nodes' and 'edges' lists
        """
        # Clear existing data
        self.nodes.clear()
        self.edges.clear()
        self._prerequisites.clear()
        self._dependents.clear()
        
        # Parse nodes
        for node_data in data.get("nodes", []):
            concept_id = node_data.get("concept_id") or node_data.get("id")
            if not concept_id:
                continue
            
            # Handle both camelCase (frontend) and snake_case (backend)
            bloom_targets = (
                node_data.get("bloom_targets") or 
                node_data.get("bloomTargets") or 
                ["understand"]
            )
            difficulty_default = (
                node_data.get("difficulty_default") or 
                node_data.get("difficultyDefault") or 
                2
            )
            name = node_data.get("name") or node_data.get("label") or concept_id
            description = node_data.get("description", "")
            
            node = ConceptNode(
                concept_id=concept_id,
                bloom_targets=bloom_targets,
                difficulty_default=difficulty_default,
                description=description,
            )
            # Store name as optional metadata if provided
            if name != concept_id:
                node.name = name
            self.nodes[concept_id] = node
            self._prerequisites[concept_id] = set()
            self._dependents[concept_id] = set()
        
        # Parse edges
        for edge_data in data.get("edges", []):
            from_concept = edge_data.get("from") or edge_data.get("from_concept") or edge_data.get("source")
            to_concept = edge_data.get("to") or edge_data.get("to_concept") or edge_data.get("target")
            
            if not from_concept or not to_concept:
                continue
            if from_concept not in self.nodes or to_concept not in self.nodes:
                continue  # Skip invalid edges
            
            edge = ConceptEdge(
                from_concept=from_concept,
                to_concept=to_concept,
                kind=edge_data.get("kind", "prerequisite"),
                reason=edge_data.get("reason", ""),
            )
            self.edges.append(edge)
            
            if edge.kind == "prerequisite":
                self._prerequisites[to_concept].add(from_concept)
                self._dependents[from_concept].add(to_concept)

    @classmethod
    def create_new(cls, subject: str, grade: int, chapter_id: str) -> "ConceptGraph":
        """
        Create a new empty concept graph.
        
        Args:
            subject: e.g., "math"
            grade: e.g., 5
            chapter_id: e.g., "new_chapter"
        
        Returns:
            Empty ConceptGraph instance ready for population
        """
        graph = cls()
        graph.subject = subject
        graph.grade = grade
        graph.chapter_id = chapter_id
        return graph

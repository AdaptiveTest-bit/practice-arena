"""Tests for the adaptation module."""

import pytest
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestConceptGraph:
    """Tests for ConceptGraph loading and querying."""
    
    def test_load_factors_multiples_graph(self):
        """Test loading the factors_multiples concept graph."""
        from domain.adaptation.concept_graph import ConceptGraph
        
        graph = ConceptGraph.load("math", 5, "factors_multiples")
        
        assert graph.subject == "math"
        assert graph.grade == 5
        assert graph.chapter_id == "factors_multiples"
        assert len(graph.nodes) > 0
        assert len(graph.edges) > 0
    
    def test_graph_has_expected_concepts(self):
        """Test that the graph contains expected concepts."""
        from domain.adaptation.concept_graph import ConceptGraph
        
        graph = ConceptGraph.load("math", 5, "factors_multiples")
        
        concept_keys = graph.get_all_concept_keys()
        
        expected = ["divisibility", "factors", "multiples", "gcd", "lcm"]
        for expected_key in expected:
            assert expected_key in concept_keys, f"Missing concept: {expected_key}"
    
    def test_get_prerequisites(self):
        """Test getting prerequisites for a concept."""
        from domain.adaptation.concept_graph import ConceptGraph
        
        graph = ConceptGraph.load("math", 5, "factors_multiples")
        
        # GCD should have prerequisites
        gcd_id = graph.get_full_concept_id("gcd")
        if gcd_id:
            prereqs = graph.get_prerequisites(gcd_id)
            assert isinstance(prereqs, set)
    
    def test_get_foundation_concepts(self):
        """Test finding foundation concepts (no prerequisites)."""
        from domain.adaptation.concept_graph import ConceptGraph
        
        graph = ConceptGraph.load("math", 5, "factors_multiples")
        
        foundations = graph.get_foundation_concepts()
        
        assert len(foundations) > 0, "Should have at least one foundation concept"
        
        # Foundation concepts should have no prerequisites
        for concept_id in foundations:
            prereqs = graph.get_prerequisites(concept_id)
            assert len(prereqs) == 0, f"{concept_id} should have no prerequisites"
    
    def test_topological_order(self):
        """Test topological ordering of concepts."""
        from domain.adaptation.concept_graph import ConceptGraph
        
        graph = ConceptGraph.load("math", 5, "factors_multiples")
        
        order = graph.get_topological_order()
        
        assert len(order) == len(graph.nodes), "All concepts should be in order"
        
        # Prerequisites should come before dependents
        for concept_id in order:
            prereqs = graph.get_prerequisites(concept_id)
            concept_idx = order.index(concept_id)
            for prereq in prereqs:
                prereq_idx = order.index(prereq)
                assert prereq_idx < concept_idx, f"{prereq} should come before {concept_id}"
    
    def test_get_ready_concepts(self):
        """Test finding concepts ready to learn."""
        from domain.adaptation.concept_graph import ConceptGraph
        
        graph = ConceptGraph.load("math", 5, "factors_multiples")
        
        # With no mastery, only foundations should be ready
        ready = graph.get_ready_concepts(mastered=set())
        foundations = graph.get_foundation_concepts()
        
        for concept_id in ready:
            prereqs = graph.get_prerequisites(concept_id)
            assert len(prereqs) == 0 or all(p in set() for p in prereqs)


class TestMasteryTracker:
    """Tests for MasteryTracker."""
    
    def test_initial_state(self):
        """Test initial tracker state."""
        from domain.adaptation.mastery import MasteryTracker, MasteryLevel
        
        tracker = MasteryTracker(student_id="test_student")
        
        mastery = tracker.get_mastery("gcd")
        assert mastery.total_attempts == 0
        assert mastery.correct_attempts == 0
        assert mastery.level == MasteryLevel.NOT_STARTED
    
    def test_record_attempt(self):
        """Test recording attempts."""
        from domain.adaptation.mastery import MasteryTracker
        
        tracker = MasteryTracker(student_id="test_student")
        
        tracker.record_attempt("gcd", is_correct=True, difficulty=2)
        tracker.record_attempt("gcd", is_correct=False, difficulty=2)
        tracker.record_attempt("gcd", is_correct=True, difficulty=2)
        
        mastery = tracker.get_mastery("gcd")
        assert mastery.total_attempts == 3
        assert mastery.correct_attempts == 2
        assert abs(mastery.accuracy - 0.667) < 0.01
    
    def test_mastery_levels(self):
        """Test mastery level progression."""
        from domain.adaptation.mastery import MasteryTracker, MasteryLevel
        
        tracker = MasteryTracker(student_id="test_student")
        
        # Learning level (< 50% correct)
        tracker.record_attempt("concept1", is_correct=False, difficulty=2)
        tracker.record_attempt("concept1", is_correct=False, difficulty=2)
        tracker.record_attempt("concept1", is_correct=True, difficulty=2)
        assert tracker.get_mastery_level("concept1") == MasteryLevel.LEARNING
        
        # Practiced level (50-79% correct)
        tracker.record_attempt("concept2", is_correct=True, difficulty=2)
        tracker.record_attempt("concept2", is_correct=True, difficulty=2)
        tracker.record_attempt("concept2", is_correct=False, difficulty=2)
        assert tracker.get_mastery_level("concept2") == MasteryLevel.PRACTICED
        
        # Mastered level (>= 80% correct with 5+ attempts)
        for _ in range(5):
            tracker.record_attempt("concept3", is_correct=True, difficulty=2)
        assert tracker.get_mastery_level("concept3") == MasteryLevel.MASTERED
    
    def test_get_mastered_concepts(self):
        """Test getting list of mastered concepts."""
        from domain.adaptation.mastery import MasteryTracker
        
        tracker = MasteryTracker(student_id="test_student")
        
        # Master "gcd"
        for _ in range(5):
            tracker.record_attempt("gcd", is_correct=True, difficulty=2)
        
        # Don't master "lcm"
        tracker.record_attempt("lcm", is_correct=False, difficulty=2)
        
        mastered = tracker.get_mastered_concepts()
        assert "gcd" in mastered
        assert "lcm" not in mastered
    
    def test_recommended_difficulty(self):
        """Test difficulty recommendation."""
        from domain.adaptation.mastery import MasteryTracker
        
        tracker = MasteryTracker(student_id="test_student")
        
        # Should start at medium (2)
        assert tracker.get_recommended_difficulty("new_concept") == 2
        
        # High accuracy should increase difficulty
        for _ in range(5):
            tracker.record_attempt("easy_concept", is_correct=True, difficulty=2)
        assert tracker.get_recommended_difficulty("easy_concept") >= 2
        
        # Low accuracy should decrease difficulty
        for _ in range(5):
            tracker.record_attempt("hard_concept", is_correct=False, difficulty=2)
        assert tracker.get_recommended_difficulty("hard_concept") <= 2
    
    def test_export_import_state(self):
        """Test state export and import."""
        from domain.adaptation.mastery import MasteryTracker
        
        tracker = MasteryTracker(student_id="test_student", chapter_id="factors_multiples")
        tracker.record_attempt("gcd", is_correct=True, difficulty=2)
        tracker.record_attempt("gcd", is_correct=True, difficulty=3)
        
        # Export
        state = tracker.export_state()
        assert state["student_id"] == "test_student"
        assert "gcd" in state["mastery"]
        
        # Import
        restored = MasteryTracker.from_state(state)
        assert restored.student_id == "test_student"
        assert restored.get_mastery("gcd").total_attempts == 2


class TestSequencer:
    """Tests for Sequencer."""
    
    def test_sequencer_initialization(self):
        """Test sequencer initialization."""
        from domain.adaptation.concept_graph import ConceptGraph
        from domain.adaptation.mastery import MasteryTracker
        from domain.adaptation.sequencer import Sequencer
        
        graph = ConceptGraph.load("math", 5, "factors_multiples")
        tracker = MasteryTracker(student_id="test_student")
        sequencer = Sequencer(graph, tracker)
        
        assert sequencer.graph == graph
        assert sequencer.tracker == tracker
    
    def test_get_next_target(self):
        """Test getting next target."""
        from domain.adaptation.concept_graph import ConceptGraph
        from domain.adaptation.mastery import MasteryTracker
        from domain.adaptation.sequencer import Sequencer, SequencingTarget
        
        graph = ConceptGraph.load("math", 5, "factors_multiples")
        tracker = MasteryTracker(student_id="test_student")
        sequencer = Sequencer(graph, tracker)
        
        target = sequencer.get_next_target()
        
        assert isinstance(target, SequencingTarget)
        assert target.concept_key in graph.get_all_concept_keys()
        assert 1 <= target.difficulty <= 5
        assert target.bloom_level is not None
    
    def test_foundation_concepts_first(self):
        """Test that foundation concepts are prioritized for new students."""
        from domain.adaptation.concept_graph import ConceptGraph
        from domain.adaptation.mastery import MasteryTracker
        from domain.adaptation.sequencer import Sequencer, SequencingStrategy
        
        graph = ConceptGraph.load("math", 5, "factors_multiples")
        tracker = MasteryTracker(student_id="test_student")
        sequencer = Sequencer(graph, tracker, strategy=SequencingStrategy.MASTERY_FIRST)
        
        # Get several targets
        targets = [sequencer.get_next_target() for _ in range(5)]
        concept_keys = [t.concept_key for t in targets]
        
        # Should include foundation concepts
        foundations = [graph.get_concept_key(c) for c in graph.get_foundation_concepts()]
        assert any(c in foundations for c in concept_keys), "Should include foundation concepts"
    
    def test_struggling_concepts_prioritized(self):
        """Test that struggling concepts get higher priority."""
        from domain.adaptation.concept_graph import ConceptGraph
        from domain.adaptation.mastery import MasteryTracker
        from domain.adaptation.sequencer import Sequencer, SequencingStrategy
        
        graph = ConceptGraph.load("math", 5, "factors_multiples")
        tracker = MasteryTracker(student_id="test_student")
        
        # Create struggling record for "divisibility"
        for _ in range(5):
            tracker.record_attempt("divisibility", is_correct=False, difficulty=2)
        
        sequencer = Sequencer(graph, tracker, strategy=SequencingStrategy.STRUGGLING_FOCUS)
        
        # Get targets
        targets = [sequencer.get_next_target() for _ in range(3)]
        concept_keys = [t.concept_key for t in targets]
        
        # Divisibility should appear (struggling)
        assert "divisibility" in concept_keys, "Struggling concept should be prioritized"
    
    def test_session_plan(self):
        """Test session plan generation."""
        from domain.adaptation.concept_graph import ConceptGraph
        from domain.adaptation.mastery import MasteryTracker
        from domain.adaptation.sequencer import Sequencer
        
        graph = ConceptGraph.load("math", 5, "factors_multiples")
        tracker = MasteryTracker(student_id="test_student")
        sequencer = Sequencer(graph, tracker)
        
        plan = sequencer.get_session_plan(question_count=10)
        
        assert len(plan) == 10
        assert all(t.concept_key in graph.get_all_concept_keys() for t in plan)
    
    def test_progress_summary(self):
        """Test progress summary."""
        from domain.adaptation.concept_graph import ConceptGraph
        from domain.adaptation.mastery import MasteryTracker
        from domain.adaptation.sequencer import Sequencer
        
        graph = ConceptGraph.load("math", 5, "factors_multiples")
        tracker = MasteryTracker(student_id="test_student")
        
        # Master one concept
        for _ in range(5):
            tracker.record_attempt("divisibility", is_correct=True, difficulty=1)
        
        sequencer = Sequencer(graph, tracker)
        summary = sequencer.get_progress_summary()
        
        assert summary["total_concepts"] > 0
        assert summary["mastered_count"] >= 1
        assert "divisibility" in summary["mastered_concepts"]
    
    def test_variety_in_session(self):
        """Test that sequencer provides variety (doesn't repeat same concept)."""
        from domain.adaptation.concept_graph import ConceptGraph
        from domain.adaptation.mastery import MasteryTracker
        from domain.adaptation.sequencer import Sequencer
        
        graph = ConceptGraph.load("math", 5, "factors_multiples")
        tracker = MasteryTracker(student_id="test_student")
        sequencer = Sequencer(graph, tracker)
        
        targets = [sequencer.get_next_target() for _ in range(6)]
        concept_keys = [t.concept_key for t in targets]
        
        # Should have at least 3 different concepts in 6 questions
        unique_concepts = set(concept_keys)
        assert len(unique_concepts) >= 3, "Should have variety in concepts"


class TestAdaptiveQuestionSelector:
    """Tests for the full adaptive question selection flow."""
    
    def test_selector_initialization(self):
        """Test that the selector initializes correctly."""
        from domain.adaptation.selector import get_adaptive_selector
        
        selector = get_adaptive_selector("factors_multiples")
        
        assert selector.chapter_key == "factors_multiples"
        assert selector.graph is not None
        assert selector.generator is not None
    
    def test_select_question_returns_question_and_metadata(self):
        """Test that select_question returns a valid question and metadata."""
        from domain.adaptation.selector import get_adaptive_selector
        from api.models.quiz import Question
        
        selector = get_adaptive_selector("factors_multiples")
        question, metadata = selector.select_question(student_id="test_student_001")
        
        # Check question
        assert isinstance(question, Question)
        assert question.question_text is not None
        assert len(question.options) > 0
        
        # Check metadata structure
        assert "selection" in metadata
        assert "mastery" in metadata
        assert "progress" in metadata
        
        # Check selection metadata
        assert "concept_id" in metadata["selection"]
        assert "difficulty" in metadata["selection"]
        assert "reason" in metadata["selection"]
    
    def test_record_attempt_updates_mastery(self):
        """Test that recording an attempt updates mastery state."""
        from domain.adaptation.selector import get_adaptive_selector
        
        selector = get_adaptive_selector("factors_multiples")
        
        # Select a question first
        question, metadata = selector.select_question(student_id="test_student_002")
        concept_id = metadata["selection"]["concept_id"]
        
        # Record a correct attempt
        result = selector.record_attempt(
            student_id="test_student_002",
            concept_id=concept_id,
            is_correct=True
        )
        
        assert result["concept_id"] == concept_id
        assert result["attempts"] == 1
        assert result["correct"] == 1
    
    def test_adaptive_selection_changes_with_mastery(self):
        """Test that selection adapts as student masters concepts."""
        from domain.adaptation.selector import get_adaptive_selector
        
        selector = get_adaptive_selector("factors_multiples")
        student_id = "test_student_003"
        
        # Get initial question
        q1, meta1 = selector.select_question(student_id=student_id)
        concept1 = meta1["selection"]["concept_id"]
        
        # Master this concept (5 correct in a row)
        for _ in range(5):
            selector.record_attempt(student_id, concept1, is_correct=True)
        
        # Get next few questions - should tend to move to new concepts
        concepts_seen = {concept1}
        for _ in range(5):
            q, meta = selector.select_question(student_id=student_id)
            concepts_seen.add(meta["selection"]["concept_id"])
        
        # Should explore at least 2 concepts total
        assert len(concepts_seen) >= 2, "Should explore new concepts after mastering one"
    
    def test_get_student_progress(self):
        """Test getting student progress report."""
        from domain.adaptation.selector import get_adaptive_selector
        
        selector = get_adaptive_selector("factors_multiples")
        student_id = "test_student_004"
        
        # Make some attempts
        q, meta = selector.select_question(student_id=student_id)
        concept_id = meta["selection"]["concept_id"]
        selector.record_attempt(student_id, concept_id, is_correct=True)
        selector.record_attempt(student_id, concept_id, is_correct=False)
        
        # Get progress
        progress = selector.get_student_progress(student_id)
        
        assert progress["student_id"] == student_id
        assert progress["chapter"] == "factors_multiples"
        assert "progress" in progress
        assert "concepts" in progress
        assert progress["progress"]["total_concepts"] > 0


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])

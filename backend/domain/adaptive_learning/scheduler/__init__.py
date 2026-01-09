"""Leitner Scheduling System

This package implements the Leitner spaced repetition algorithm.

Main Components:
- leitner: SchedulerService with 5-box system
- concept_sequencer: Determines optimal concept ordering

Features:
- 5 boxes with exponential spacing (0.5d, 1d, 3d, 7d, 14d)
- Automatic promotion on correct answers
- Demotion to Box 0 on wrong answers
- Concept-level tracking per student
"""

__all__ = []

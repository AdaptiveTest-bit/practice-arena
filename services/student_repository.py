"""Student Progress Repository - Persistence Layer for StudentProgress Data

Manages storage and retrieval of student progress data.
Supports in-memory storage (development) and database backends (production).
"""

from typing import Dict, Optional, List
from datetime import datetime
import json
import uuid
from models.student_progress import StudentProgress, AttemptResult, MisconceptionEncounter
from models.distractor import MisconceptionType
from models.cognitive_levels import BloomLevel


class StudentRepository:
    """Repository for StudentProgress data persistence."""
    
    def __init__(self, storage_type: str = "memory"):
        """
        Initialize repository with specified storage backend.
        
        Args:
            storage_type: "memory" (in-memory), "file" (JSON), or "database" (future)
        """
        self.storage_type = storage_type
        
        if storage_type == "memory":
            self._student_store: Dict[str, StudentProgress] = {}
            self._attempt_log: List[AttemptResult] = []
        elif storage_type == "file":
            self._data_file = "student_data.json"
            self._load_from_file()
        else:
            raise ValueError(f"Unknown storage type: {storage_type}")
    
    # ============================================================================
    # STUDENT PROFILE OPERATIONS
    # ============================================================================
    
    def create_student(self, student_name: str, chapter: str = "Ch1: The Fish Tale") -> str:
        """
        Create a new student profile.
        
        Args:
            student_name: Name of the student
            chapter: Starting chapter (default: Ch1)
            
        Returns:
            student_id (UUID string)
        """
        student_id = str(uuid.uuid4())
        student = StudentProgress(
            student_id=student_id,
            chapter=chapter
        )
        
        if self.storage_type == "memory":
            self._student_store[student_id] = student
        elif self.storage_type == "file":
            self._save_to_file()
        
        print(f"✓ Created student: {student_name} ({student_id})")
        return student_id
    
    def get_student(self, student_id: str) -> Optional[StudentProgress]:
        """Retrieve student progress by ID."""
        if self.storage_type == "memory":
            return self._student_store.get(student_id)
        elif self.storage_type == "file":
            return self._load_student_from_file(student_id)
        return None
    
    def get_or_create_student(self, student_id: str, student_name: str = "Student") -> StudentProgress:
        """Get existing student or create new one."""
        student = self.get_student(student_id)
        if student is None:
            self.create_student(student_name)
            student = self.get_student(student_id)
        return student
    
    def save_student(self, student: StudentProgress) -> None:
        """Save/update student progress."""
        if self.storage_type == "memory":
            self._student_store[student.student_id] = student
        elif self.storage_type == "file":
            self._save_to_file()
    
    def list_all_students(self) -> List[StudentProgress]:
        """List all students."""
        if self.storage_type == "memory":
            return list(self._student_store.values())
        elif self.storage_type == "file":
            return list(self._student_store.values())
        return []
    
    # ============================================================================
    # ATTEMPT RECORDING
    # ============================================================================
    
    def record_attempt(self, attempt: AttemptResult) -> None:
        """
        Record a question attempt and update student progress.
        
        Args:
            attempt: AttemptResult with all question/response details
        """
        # Store attempt in log
        if self.storage_type == "memory":
            self._attempt_log.append(attempt)
        elif self.storage_type == "file":
            pass  # Will be saved with student data
        
        # Update student progress
        student = self.get_student(attempt.student_id)
        if student:
            student.record_attempt(attempt)
            self.save_student(student)
            
            # Log the update
            print(f"✓ Recorded attempt for student {attempt.student_id}")
            print(f"  Question: {attempt.question_id} | Correct: {attempt.is_correct}")
            if attempt.misconception_revealed:
                print(f"  Misconception detected: {attempt.misconception_revealed}")
    
    def get_student_attempts(self, student_id: str) -> List[AttemptResult]:
        """Get all attempts for a student."""
        if self.storage_type == "memory":
            return [a for a in self._attempt_log if a.student_id == student_id]
        return []
    
    def get_attempts_by_chapter(self, student_id: str, chapter: str) -> List[AttemptResult]:
        """Get all attempts in a specific chapter."""
        if self.storage_type == "memory":
            return [
                a for a in self._attempt_log 
                if a.student_id == student_id and a.chapter == chapter
            ]
        return []
    
    # ============================================================================
    # ANALYTICS & QUERIES
    # ============================================================================
    
    def get_class_statistics(self, student_ids: List[str]) -> Dict:
        """Get aggregate statistics for a class."""
        if not student_ids:
            return {}
        
        students = [self.get_student(sid) for sid in student_ids if self.get_student(sid)]
        
        if not students:
            return {}
        
        return {
            "class_size": len(students),
            "average_accuracy": sum(s.overall_percentage for s in students) / len(students),
            "students_by_status": {
                "struggling": len([s for s in students if s.overall_percentage < 50]),
                "developing": len([s for s in students if 50 <= s.overall_percentage < 70]),
                "proficient": len([s for s in students if 70 <= s.overall_percentage < 85]),
                "advanced": len([s for s in students if s.overall_percentage >= 85]),
            },
            "common_misconceptions": self._get_class_misconceptions(students)
        }
    
    def _get_class_misconceptions(self, students: List[StudentProgress]) -> List[Dict]:
        """Identify most common misconceptions in class."""
        misconception_counts: Dict[str, int] = {}
        
        for student in students:
            for misc_type, encounter in student.misconceptions.items():
                key = misc_type
                misconception_counts[key] = misconception_counts.get(key, 0) + encounter.encounter_count
        
        # Return sorted by frequency
        return [
            {
                "misconception": misc_type,
                "total_encounters": count,
                "affected_students": len([
                    s for s in students 
                    if misc_type in s.misconceptions and s.misconceptions[misc_type].encounter_count > 0
                ])
            }
            for misc_type, count in sorted(
                misconception_counts.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:10]
        ]
    
    def get_misconception_analysis(self, student_id: str) -> Dict:
        """Detailed misconception analysis for a student."""
        student = self.get_student(student_id)
        if not student:
            return {}
        
        return {
            "student_id": student_id,
            "total_misconceptions": len(student.misconceptions),
            "misconceptions_needing_remediation": [
                {
                    "type": misc_type,
                    "encounters": misc.encounter_count,
                    "first_encountered": misc.first_encountered.isoformat() if misc.first_encountered else None,
                    "last_encountered": misc.last_encountered.isoformat() if misc.last_encountered else None,
                    "remediation_provided": misc.remediation_provided,
                    "remediation_effective": misc.remediation_effective,
                }
                for misc_type, misc in student.misconceptions.items()
                if misc.encounter_count >= 2 and not misc.remediation_effective
            ]
        }
    
    # ============================================================================
    # FILE PERSISTENCE (for development)
    # ============================================================================
    
    def _save_to_file(self) -> None:
        """Save all student data to JSON file."""
        if self.storage_type != "file":
            return
        
        data = {
            "students": {
                sid: json.loads(student.json())
                for sid, student in self._student_store.items()
            },
            "attempts": [
                json.loads(attempt.json())
                for attempt in self._attempt_log
            ]
        }
        
        with open(self._data_file, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def _load_from_file(self) -> None:
        """Load all student data from JSON file."""
        if self.storage_type != "file":
            return
        
        self._student_store = {}
        self._attempt_log = []
        
        try:
            with open(self._data_file, 'r') as f:
                data = json.load(f)
                
                # Load students
                for sid, student_data in data.get("students", {}).items():
                    self._student_store[sid] = StudentProgress(**student_data)
                
                # Load attempts
                for attempt_data in data.get("attempts", []):
                    self._attempt_log.append(AttemptResult(**attempt_data))
                
                print(f"✓ Loaded {len(self._student_store)} students from file")
        except FileNotFoundError:
            print(f"✓ No existing student data file found (will create on first save)")
    
    def _load_student_from_file(self, student_id: str) -> Optional[StudentProgress]:
        """Load a specific student from file."""
        self._load_from_file()
        return self._student_store.get(student_id)
    
    # ============================================================================
    # DEBUGGING & INSPECTION
    # ============================================================================
    
    def print_student_summary(self, student_id: str) -> None:
        """Print human-readable student summary."""
        student = self.get_student(student_id)
        if not student:
            print(f"Student {student_id} not found")
            return
        
        summary = student.get_mastery_summary()
        
        print(f"\n{'='*60}")
        print(f"STUDENT: {student_id}")
        print(f"{'='*60}")
        print(f"Overall Accuracy: {summary['overall_percentage']:.1f}%")
        print(f"Total Attempts: {summary['total_attempts']}")
        print(f"Current Chapter: {student.chapter}")
        print(f"Current Difficulty: {student.current_difficulty}")
        print(f"Current Bloom Level: {student.current_bloom_level}")
        
        print(f"\n--- DIFFICULTY PROGRESSION ---")
        for level, mastery in summary['difficulty_levels'].items():
            status = "✓ MASTERED" if mastery['mastered'] else f"{mastery['percentage']:.0f}%"
            print(f"  Level {level}: {status} ({mastery['attempts']} attempts)")
        
        print(f"\n--- BLOOM'S PROGRESSION ---")
        for level, mastery in summary['bloom_levels'].items():
            status = "✓ MASTERED" if mastery['mastered'] else f"{mastery['percentage']:.0f}%"
            print(f"  {level}: {status} ({mastery['attempts']} attempts)")
        
        if summary['problem_misconceptions']:
            print(f"\n--- MISCONCEPTIONS NEEDING REMEDIATION ---")
            for misc in summary['problem_misconceptions']:
                print(f"  • {misc['type']}: {misc['count']} encounters")
        
        print(f"{'='*60}\n")


# Global repository instance (can be swapped for database later)
_repository: Optional[StudentRepository] = None


def get_repository(storage_type: str = "memory") -> StudentRepository:
    """Get or create the global repository instance."""
    global _repository
    if _repository is None:
        _repository = StudentRepository(storage_type=storage_type)
    return _repository


def set_repository(repo: StudentRepository) -> None:
    """Set custom repository instance (for testing)."""
    global _repository
    _repository = repo

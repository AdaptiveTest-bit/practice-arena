"""Initialize Curriculum Data

Seed the database with chapters, topics, concepts, and sample questions
based on the existing question generator system.
"""

from database import SessionLocal, Chapter, Topic, Concept, CurriculumQuestion, Base, engine
from sqlalchemy import text
import json


def seed_curriculum():
    """Seed curriculum data into database"""
    db = SessionLocal()
    
    try:
        # Define curriculum structure based on existing system
        curriculum_data = {
            "Boxes & Sketches": {
                "order": 1,
                "topics": {
                    "Dice Logic": {
                        "description": "Understanding opposite faces and dice configurations",
                        "concepts": [
                            "Opposite Faces Sum",
                            "Dice Orientations",
                            "Dice Patterns"
                        ]
                    },
                    "Cube Counting": {
                        "description": "3D spatial reasoning and counting cubes",
                        "concepts": [
                            "Visible Cubes",
                            "Hidden Cubes",
                            "Total Cubes"
                        ]
                    },
                    "Nets": {
                        "description": "Mental folding and net visualization",
                        "concepts": [
                            "Net Unfolding",
                            "Net Folding",
                            "Surface Recognition"
                        ]
                    }
                }
            },
            "Data & Analytics": {
                "order": 2,
                "topics": {
                    "Data Handling": {
                        "description": "Reading and interpreting data",
                        "concepts": [
                            "Data Interpretation",
                            "Graph Reading",
                            "Data Analysis"
                        ]
                    },
                    "Data Patterns": {
                        "description": "Finding patterns in data sequences",
                        "concepts": [
                            "Number Patterns",
                            "Sequence Recognition",
                            "Pattern Prediction"
                        ]
                    }
                }
            },
            "Geometry & Measurement": {
                "order": 3,
                "topics": {
                    "Clock Angles": {
                        "description": "Calculating angles on clock faces",
                        "concepts": [
                            "Hour Hand Angles",
                            "Minute Hand Angles",
                            "Angle Calculation"
                        ]
                    },
                    "Symmetry": {
                        "description": "Understanding symmetry in shapes",
                        "concepts": [
                            "Line Symmetry",
                            "Rotational Symmetry",
                            "Symmetry Recognition"
                        ]
                    },
                    "Rotation": {
                        "description": "Understanding rotations and transformations",
                        "concepts": [
                            "Rotation Direction",
                            "Rotation Angles",
                            "Rotational Position"
                        ]
                    },
                    "Geometry & Measurement": {
                        "description": "Basic geometry and measurements",
                        "concepts": [
                            "Length and Width",
                            "Area Calculation",
                            "Perimeter"
                        ]
                    }
                }
            },
            "Numbers & Operations": {
                "order": 4,
                "topics": {
                    "Large Numbers": {
                        "description": "Understanding and working with large numbers",
                        "concepts": [
                            "Place Value",
                            "Number Comparison",
                            "Number Representation"
                        ]
                    },
                    "Factors & Multiples": {
                        "description": "Understanding factors and multiples",
                        "concepts": [
                            "Factor Identification",
                            "Multiple Identification",
                            "LCM and GCD"
                        ]
                    },
                    "Fractions & Decimals": {
                        "description": "Working with fractions and decimals",
                        "concepts": [
                            "Fraction Operations",
                            "Decimal Operations",
                            "Fraction-Decimal Conversion"
                        ]
                    }
                }
            }
        }
        
        # Create chapters and topics
        chapter_count = 0
        topic_count = 0
        concept_count = 0
        
        for chapter_name, chapter_info in curriculum_data.items():
            # Check if chapter already exists
            existing_chapter = db.query(Chapter).filter(Chapter.name == chapter_name).first()
            
            if existing_chapter:
                chapter = existing_chapter
                print(f"⏭️  Chapter already exists: {chapter_name}")
            else:
                chapter = Chapter(
                    name=chapter_name,
                    sequence_order=chapter_info['order'],
                    unit_tag=chapter_name.upper().replace(' & ', '_').replace(' ', '_')
                )
                db.add(chapter)
                db.flush()  # Flush to get the chapter ID
                chapter_count += 1
                print(f"✅ Chapter created: {chapter_name}")
            
            # Create topics
            for topic_name, topic_info in chapter_info['topics'].items():
                existing_topic = db.query(Topic).filter(
                    Topic.chapter_id == chapter.id,
                    Topic.name == topic_name
                ).first()
                
                if existing_topic:
                    topic = existing_topic
                    print(f"   ⏭️  Topic already exists: {topic_name}")
                else:
                    topic = Topic(
                        chapter_id=chapter.id,
                        name=topic_name,
                        description=topic_info.get('description', '')
                    )
                    db.add(topic)
                    db.flush()
                    topic_count += 1
                    print(f"   ✅ Topic created: {topic_name}")
                
                # Create concepts
                for concept_name in topic_info['concepts']:
                    existing_concept = db.query(Concept).filter(
                        Concept.topic_id == topic.id,
                        Concept.name == concept_name
                    ).first()
                    
                    if existing_concept:
                        print(f"      ⏭️  Concept already exists: {concept_name}")
                    else:
                        concept = Concept(
                            topic_id=topic.id,
                            name=concept_name,
                            misconception_guide=f"Common misconceptions in {concept_name}"
                        )
                        db.add(concept)
                        db.flush()
                        concept_count += 1
                        print(f"      ✅ Concept created: {concept_name}")
        
        db.commit()
        
        print("\n" + "=" * 60)
        print(f"✅ Curriculum seeded successfully!")
        print(f"   - Chapters: {chapter_count}")
        print(f"   - Topics: {topic_count}")
        print(f"   - Concepts: {concept_count}")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding curriculum: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


def verify_curriculum():
    """Verify that curriculum was seeded correctly"""
    db = SessionLocal()
    
    try:
        chapters = db.query(Chapter).count()
        topics = db.query(Topic).count()
        concepts = db.query(Concept).count()
        
        print("\n📊 Curriculum Status:")
        print(f"   - Total Chapters: {chapters}")
        print(f"   - Total Topics: {topics}")
        print(f"   - Total Concepts: {concepts}")
        
        return chapters > 0 and topics > 0 and concepts > 0
        
    except Exception as e:
        print(f"❌ Error verifying curriculum: {e}")
        return False
    finally:
        db.close()


if __name__ == "__main__":
    import sys
    
    print("=" * 60)
    print("🌱 EdTech MVP Curriculum Initialization")
    print("=" * 60)
    print()
    
    if seed_curriculum():
        if verify_curriculum():
            print("\n✅ Curriculum initialization completed!")
            sys.exit(0)
    
    print("\n❌ Curriculum initialization failed!")
    sys.exit(1)

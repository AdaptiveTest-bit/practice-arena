from flask import Flask, render_template, jsonify, request
from question_generator import (
    DiceLogicGenerator,
    CubeCountingGenerator,
    NetsGenerator,
    DataHandlingGenerator,
    ClockAnglesGenerator,
    SymmetryGenerator,
    RotationGenerator,
    LargeNumbersGenerator,
    FactorsMultiplesGenerator,
    FractionsDecimalsGenerator,
    GeometryMeasurementGenerator,
    DataPatternsGenerator
)
import random

app = Flask(__name__)

# Initialize generators
GENERATORS = {
    # Boxes & Sketches (3D Geometry)
    'dice': DiceLogicGenerator(),
    'cube': CubeCountingGenerator(),
    'nets': NetsGenerator(),
    # Data Handling
    'data': DataHandlingGenerator(),
    # Shapes & Angles
    'angles': ClockAnglesGenerator(),
    'symmetry': SymmetryGenerator(),
    'rotation': RotationGenerator(),
    # Number Systems & Algebra
    'numbers': LargeNumbersGenerator(),
    'factors': FactorsMultiplesGenerator(),
    # Fractions & Decimals
    'fractions': FractionsDecimalsGenerator(),
    # Geometry & Measurement
    'geometry': GeometryMeasurementGenerator(),
    # Data & Patterns
    'patterns': DataPatternsGenerator()
}

GENERATOR_NAMES = {
    'dice': 'Dice Logic',
    'cube': 'Cube Counting',
    'nets': 'Nets',
    'data': 'Data Handling',
    'angles': 'Clock Angles',
    'symmetry': 'Symmetry',
    'rotation': 'Rotations',
    'numbers': 'Large Numbers',
    'factors': 'Factors & Multiples',
    'fractions': 'Fractions & Decimals',
    'geometry': 'Geometry & Measurement',
    'patterns': 'Data & Patterns'
}

# Store generated questions for session
questions_cache = {}


@app.route('/')
def index():
    """Render the main dashboard."""
    return render_template('index.html')


@app.route('/api/question', methods=['POST'])
def get_question():
    """
    Fetch a new question.
    Request body: {
        "category": "dice|cube|nets|data",  # Optional, random if not provided
        "difficulty": "easy|medium|hard"     # Optional, for future use
    }
    """
    data = request.get_json() or {}
    category = data.get('category', None)
    
    # If no category specified, choose randomly
    if not category or category not in GENERATORS:
        category = random.choice(list(GENERATORS.keys()))
    
    # Generate question
    generator = GENERATORS[category]
    question = generator.generate()
    
    # Store question for reveal answer
    question_id = random.randint(100000, 999999)
    questions_cache[question_id] = question
    
    # Return question data with MCQ options
    return jsonify({
        'success': True,
        'questionId': question_id,
        'category': category,
        'categoryName': GENERATOR_NAMES[category],
        'topic': question.topic,
        'logicalTrap': question.logical_trap,
        'dataRepresentation': question.data_representation,
        'question': question.question_text,
        'options': question.options if question.options else None,
        'correctOptionIndex': question.correct_option_index if question.correct_option_index is not None else None
    })


@app.route('/api/check-answer/<int:question_id>', methods=['POST'])
def check_answer(question_id):
    """Check if the selected MCQ option is correct."""
    if question_id not in questions_cache:
        return jsonify({
            'success': False,
            'error': 'Question not found'
        }), 404
    
    question = questions_cache[question_id]
    data = request.get_json() or {}
    selected_index = data.get('selectedIndex', None)
    
    if selected_index is None:
        return jsonify({
            'success': False,
            'error': 'No option selected'
        })
    
    is_correct = selected_index == question.correct_option_index
    
    return jsonify({
        'success': True,
        'isCorrect': is_correct,
        'correctIndex': question.correct_option_index,
        'solutionSteps': question.solution_steps,
        'answer': question.answer
    })


@app.route('/api/reveal/<int:question_id>', methods=['GET'])
def reveal_answer(question_id):
    """Reveal the solution and answer for a question."""
    if question_id not in questions_cache:
        return jsonify({
            'success': False,
            'error': 'Question not found'
        }), 404
    
    question = questions_cache[question_id]
    
    return jsonify({
        'success': True,
        'solutionSteps': question.solution_steps,
        'answer': question.answer
    })


@app.route('/api/categories', methods=['GET'])
def get_categories():
    """Get list of available categories."""
    return jsonify({
        'success': True,
        'categories': [
            # Boxes & Sketches (3D Geometry)
            {
                'id': 'dice',
                'name': 'Dice Logic',
                'icon': '🎲',
                'chapter': 'Boxes & Sketches',
                'description': 'Opposite faces sum to 7'
            },
            {
                'id': 'cube',
                'name': 'Cube Counting',
                'icon': '📦',
                'chapter': 'Boxes & Sketches',
                'description': '3D spatial reasoning'
            },
            {
                'id': 'nets',
                'name': 'Nets',
                'icon': '📐',
                'chapter': 'Boxes & Sketches',
                'description': 'Mental folding exercises'
            },
            # Data Handling
            {
                'id': 'data',
                'name': 'Data Handling',
                'icon': '📊',
                'chapter': 'Data Handling',
                'description': 'Tables, scales & comparisons'
            },
            # Shapes & Angles
            {
                'id': 'angles',
                'name': 'Clock Angles',
                'icon': '🕐',
                'chapter': 'Shapes & Angles',
                'description': 'Angles & fractions of rotation'
            },
            {
                'id': 'symmetry',
                'name': 'Symmetry',
                'icon': '🪞',
                'chapter': 'Shapes & Angles',
                'description': 'Letter & word symmetry'
            },
            {
                'id': 'rotation',
                'name': 'Rotations',
                'icon': '🔄',
                'chapter': 'Shapes & Angles',
                'description': 'Turns & direction changes'
            },
            # Number Systems & Algebra
            {
                'id': 'numbers',
                'name': 'Large Numbers',
                'icon': '🔢',
                'chapter': 'Number Systems',
                'description': 'Place value, profit & loss'
            },
            {
                'id': 'factors',
                'name': 'Factors & Multiples',
                'icon': '🎯',
                'chapter': 'Number Systems',
                'description': 'HCF, LCM & divisibility'
            },
            # Fractions & Decimals
            {
                'id': 'fractions',
                'name': 'Fractions & Decimals',
                'icon': '📏',
                'chapter': 'Fractions & Decimals',
                'description': 'The "remaining" trap & conversions'
            },
            # Geometry & Measurement
            {
                'id': 'geometry',
                'name': 'Geometry & Measurement',
                'icon': '📐',
                'chapter': 'Geometry & Measurement',
                'description': 'Area vs Perimeter, volume, scale'
            },
            # Data & Patterns
            {
                'id': 'patterns',
                'name': 'Data & Patterns',
                'icon': '🧩',
                'chapter': 'Data & Patterns',
                'description': 'Sequences, missing data & pictographs'
            }
        ]
    })


if __name__ == '__main__':
    app.run(debug=True, port=5002)

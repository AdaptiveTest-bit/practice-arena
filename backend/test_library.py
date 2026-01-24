"""Test function library integration."""
from domain.template_engine.universal_schema import UniversalTemplate
from domain.template_engine.ingestor import UniversalTemplateIngestorSync
import yaml

template_yaml = '''
template_id: physics_kinematic_test
name: Kinematic Energy Calculator
concept_id: physics_kinetic_energy
version: "2.0"
metadata:
  title: Kinematic Energy Problem
  subject: physics
  grade_level: 9
  learning_objectives:
    - Calculate kinetic energy
variables:
  use_libraries:
    - physics_basics
    - math_helpers
  base:
    mass:
      type: integer
      minimum: 1
      maximum: 20
    velocity:
      type: integer
      minimum: 5
      maximum: 30
  computed:
    kinetic_energy:
      formula: kinetic_energy(mass, velocity)
    momentum:
      formula: momentum(mass, velocity)
  constraints:
    - kinetic_energy > 100
question_pattern: "A ball of mass {{mass}} kg moves at {{velocity}} m/s. Find its kinetic energy."
options:
  - pattern: "{kinetic_energy} J"
    is_correct: true
  - pattern: "{momentum} J"
    is_correct: false
    student_thinking: Confused with momentum formula
  - pattern: "{mass} × {velocity} J"
    is_correct: false
    student_thinking: Forgot the 0.5 coefficient
answer:
  correct_formula: kinetic_energy
  unit: J
'''

data = yaml.safe_load(template_yaml)
template = UniversalTemplate(**data)

print('✅ Template created successfully')
print(f'   Libraries: {template.variables.use_libraries}')

# Test via VariableGenerator directly with library functions
from domain.template_engine.function_library import get_library_functions
from domain.template_engine.variable_generator import VariableGenerator

# Build schema from template
schema = {
    'base': {},
    'computed': {},
    'constraints': template.variables.constraints or [],
    'custom_functions': {}
}

# Load library functions
for lib_name in template.variables.use_libraries or []:
    funcs = get_library_functions([lib_name])
    schema['custom_functions'].update(funcs)

# Convert base variables
for var_name, var_def in template.variables.base.items():
    schema['base'][var_name] = {
        'type': var_def.type,
        'min': var_def.minimum,
        'max': var_def.maximum
    }

# Convert computed variables
for var_name, var_def in (template.variables.computed or {}).items():
    if isinstance(var_def, str):
        schema['computed'][var_name] = {'formula': var_def}
    else:
        schema['computed'][var_name] = {
            'formula': var_def.formula,
            'default': getattr(var_def, 'default', None)
        }

print(f'\n🔧 Schema built with {len(schema["custom_functions"])} library functions')

# Generate variables
gen = VariableGenerator()
result = gen.generate(schema)

print(f'\n📊 Generated Variables:')
for k, v in result.variables.items():
    print(f'   {k}: {v}')

# Render question
question = template.question_pattern
for var, val in result.variables.items():
    question = question.replace('{{' + var + '}}', str(val))

print(f'\n📝 Question: {question}')

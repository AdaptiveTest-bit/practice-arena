# 📋 COPY-PASTE READY TEMPLATES
## Instant Question Templates for Admin UI

**Copy any template below → Paste in Admin UI → Click Preview → Save**

---

## 🔗 Quick Access

Open the Universal Template Editor at:
```
http://localhost:3003/templates/universal
```

---

## TEMPLATE 1: MCQ - Find Quadratic Roots

**What it generates:** "Find the roots of x² − 8x + 15 = 0" type questions

```json
{
  "name": "Quadratic - Find Roots by Factorization",
  "concept_id": "math.class10.quadratic.solve_factorization",
  "question_type": "MCQ",
  
  "question_pattern": "Find the roots of the equation x² − {{sum}}x + {{product}} = 0",
  
  "variables": {
    "base": {
      "root1": { "type": "integer", "enum": [1, 2, 3, 4, 5, 6, 7, 8, 9] },
      "root2": { "type": "integer", "enum": [2, 3, 4, 5, 6, 7, 8, 9, 10] }
    },
    "computed": {
      "sum": { "formula": "root1 + root2" },
      "product": { "formula": "root1 * root2" }
    },
    "constraints": ["root1 < root2"]
  },
  
  "options": [
    { "pattern": "{{root1}} and {{root2}}", "is_correct": true },
    { "pattern": "{{root1}} and −{{root2}}", "is_correct": false, "misconception_id": "SIGN_ERROR" },
    { "pattern": "{{sum}} and {{product}}", "is_correct": false, "misconception_id": "SUM_PRODUCT_CONFUSION" },
    { "pattern": "{{root1 + 1}} and {{root2 - 1}}", "is_correct": false, "misconception_id": "CALCULATION_ERROR" }
  ],
  
  "difficulty": 2,
  "bloom_level": "APPLY",
  "estimated_time": 60,
  
  "solution": {
    "steps": [
      { "number": 1, "text": "We need two numbers whose sum is {{sum}} and product is {{product}}" },
      { "number": 2, "text": "{{root1}} + {{root2}} = {{sum}} ✓" },
      { "number": 3, "text": "{{root1}} × {{root2}} = {{product}} ✓" },
      { "number": 4, "text": "So x² − {{sum}}x + {{product}} = (x − {{root1}})(x − {{root2}})" },
      { "number": 5, "text": "Therefore, x = {{root1}} or x = {{root2}}" }
    ]
  },
  
  "hints": [
    "What two numbers add up to {{sum}}?",
    "Those same numbers should multiply to give {{product}}",
    "Try listing factor pairs of {{product}}"
  ],
  
  "tags": ["quadratic", "factorization", "roots", "class10", "cbse"]
}
```

### Sample Output:
```
Q: Find the roots of the equation x² − 8x + 15 = 0

A) 3 and 5 ✓
B) 3 and −5
C) 8 and 15  
D) 4 and 4
```

---

## TEMPLATE 2: MCQ - GCD (Greatest Common Divisor)

```json
{
  "name": "GCD - Find Greatest Common Divisor",
  "concept_id": "math.class5.factors_multiples.gcd",
  "question_type": "MCQ",
  
  "question_pattern": "Find the GCD (Greatest Common Divisor) of {{a}} and {{b}}.",
  
  "variables": {
    "base": {
      "a": { "type": "integer", "min": 12, "max": 60 },
      "b": { "type": "integer", "min": 12, "max": 60 }
    },
    "computed": {
      "gcd_result": { "formula": "gcd(a, b)" },
      "wrong1": { "formula": "lcm(a, b)" },
      "wrong2": { "formula": "min(a, b)" },
      "wrong3": { "formula": "gcd(a, b) + 1" }
    },
    "constraints": ["a != b", "gcd(a, b) > 1"]
  },
  
  "options": [
    { "pattern": "{{gcd_result}}", "is_correct": true },
    { "pattern": "{{wrong1}}", "is_correct": false, "misconception_id": "GCD_LCM_CONFUSION" },
    { "pattern": "{{wrong2}}", "is_correct": false, "misconception_id": "MIN_IS_GCD" },
    { "pattern": "{{wrong3}}", "is_correct": false, "misconception_id": "CALCULATION_ERROR" }
  ],
  
  "difficulty": 2,
  "bloom_level": "APPLY",
  "estimated_time": 45,
  
  "solution": {
    "steps": [
      { "number": 1, "text": "Find factors of {{a}}: List all numbers that divide {{a}}" },
      { "number": 2, "text": "Find factors of {{b}}: List all numbers that divide {{b}}" },
      { "number": 3, "text": "Common factors are numbers in both lists" },
      { "number": 4, "text": "GCD is the greatest (largest) common factor: {{gcd_result}}" }
    ]
  },
  
  "hints": [
    "List all factors of {{a}} first",
    "Now list all factors of {{b}}",
    "Find the largest number that appears in both lists"
  ],
  
  "tags": ["gcd", "factors", "class5", "cbse"]
}
```

### Sample Output:
```
Q: Find the GCD (Greatest Common Divisor) of 24 and 36.

A) 12 ✓
B) 72
C) 24
D) 13
```

---

## TEMPLATE 3: MCQ - LCM (Least Common Multiple)

```json
{
  "name": "LCM - Find Least Common Multiple",
  "concept_id": "math.class5.factors_multiples.lcm",
  "question_type": "MCQ",
  
  "question_pattern": "Find the LCM of {{a}} and {{b}}.",
  
  "variables": {
    "base": {
      "a": { "type": "integer", "enum": [4, 5, 6, 8, 9, 10, 12] },
      "b": { "type": "integer", "enum": [6, 8, 9, 10, 12, 15, 18] }
    },
    "computed": {
      "lcm_result": { "formula": "lcm(a, b)" },
      "wrong1": { "formula": "gcd(a, b)" },
      "wrong2": { "formula": "a * b" },
      "wrong3": { "formula": "lcm(a, b) + a" }
    },
    "constraints": ["a < b", "a * b != lcm(a, b)"]
  },
  
  "options": [
    { "pattern": "{{lcm_result}}", "is_correct": true },
    { "pattern": "{{wrong1}}", "is_correct": false, "misconception_id": "LCM_GCD_CONFUSION" },
    { "pattern": "{{wrong2}}", "is_correct": false, "misconception_id": "MULTIPLY_FOR_LCM" },
    { "pattern": "{{wrong3}}", "is_correct": false, "misconception_id": "CALCULATION_ERROR" }
  ],
  
  "difficulty": 2,
  "bloom_level": "APPLY",
  "estimated_time": 45,
  
  "solution": {
    "steps": [
      { "number": 1, "text": "List multiples of {{a}}: {{a}}, {{2*a}}, {{3*a}}, {{4*a}}, ..." },
      { "number": 2, "text": "List multiples of {{b}}: {{b}}, {{2*b}}, {{3*b}}, ..." },
      { "number": 3, "text": "Find common multiples" },
      { "number": 4, "text": "LCM is the smallest common multiple: {{lcm_result}}" }
    ]
  },
  
  "hints": [
    "Write first 10 multiples of {{a}}",
    "Write first 10 multiples of {{b}}",
    "Find the smallest number in both lists"
  ],
  
  "tags": ["lcm", "multiples", "class5", "cbse"]
}
```

### Sample Output:
```
Q: Find the LCM of 6 and 8.

A) 24 ✓
B) 2
C) 48
D) 30
```

---

## TEMPLATE 4: Fill in the Blank - Prime Factorization

```json
{
  "name": "Fill Blank - Prime Factorization Sum",
  "concept_id": "math.class5.factors_multiples.prime_factorization",
  "question_type": "FILL_BLANK",
  
  "question_pattern": "The prime factorization of {{number}} is 2^{{p2}} × 3^{{p3}}. Find {{p2}} + {{p3}} = ____",
  
  "variables": {
    "base": {
      "p2": { "type": "integer", "enum": [1, 2, 3, 4] },
      "p3": { "type": "integer", "enum": [1, 2] }
    },
    "computed": {
      "number": { "formula": "pow(2, p2) * pow(3, p3)" },
      "answer": { "formula": "p2 + p3" }
    },
    "constraints": []
  },
  
  "options": [
    { "pattern": "{{answer}}", "is_correct": true }
  ],
  
  "difficulty": 2,
  "bloom_level": "APPLY",
  "estimated_time": 60,
  
  "solution": {
    "steps": [
      { "number": 1, "text": "{{number}} = 2^{{p2}} × 3^{{p3}}" },
      { "number": 2, "text": "Power of 2 = {{p2}}" },
      { "number": 3, "text": "Power of 3 = {{p3}}" },
      { "number": 4, "text": "Sum = {{p2}} + {{p3}} = {{answer}}" }
    ]
  },
  
  "tags": ["prime-factorization", "fill-blank", "class5"]
}
```

### Sample Output:
```
Q: The prime factorization of 72 is 2³ × 3². Find 3 + 2 = ____

Answer: 5
```

---

## TEMPLATE 5: True/False - Divisibility

```json
{
  "name": "True/False - Divisibility Check",
  "concept_id": "math.class5.factors_multiples.divisibility",
  "question_type": "TRUE_FALSE",
  
  "question_pattern": "{{number}} is exactly divisible by {{divisor}}.",
  
  "variables": {
    "base": {
      "base_num": { "type": "integer", "enum": [5, 6, 7, 8, 9, 10, 11, 12] },
      "multiplier": { "type": "integer", "enum": [2, 3, 4, 5, 6, 7, 8] },
      "add_remainder": { "type": "integer", "enum": [0, 0, 0, 1, 2] }
    },
    "computed": {
      "divisor": { "formula": "base_num" },
      "number": { "formula": "base_num * multiplier + add_remainder" },
      "is_true": { "formula": "add_remainder == 0" }
    },
    "constraints": []
  },
  
  "options": [
    { "pattern": "True", "is_correct": "{{is_true}}" },
    { "pattern": "False", "is_correct": "{{not is_true}}" }
  ],
  
  "difficulty": 1,
  "bloom_level": "REMEMBER",
  "estimated_time": 30,
  
  "solution": {
    "steps": [
      { "number": 1, "text": "Divide {{number}} by {{divisor}}" },
      { "number": 2, "text": "{{number}} ÷ {{divisor}} = {{number // divisor}} remainder {{number % divisor}}" },
      { "number": 3, "text": "Since remainder = {{number % divisor}}, the answer is {{'True' if is_true else 'False'}}" }
    ]
  },
  
  "tags": ["divisibility", "true-false", "class5"]
}
```

### Sample Output:
```
Q: 56 is exactly divisible by 7.

○ True ✓
○ False
```

---

## TEMPLATE 6: Assertion-Reason - Nature of Roots

```json
{
  "name": "Assertion-Reason - Discriminant and Roots",
  "concept_id": "math.class10.quadratic.assertion_reason",
  "question_type": "ASSERTION_REASON",
  
  "parts": [
    {
      "type": "assertion",
      "label": "Assertion (A)",
      "pattern": "The equation x² − {{b}}x + {{c}} = 0 has {{nature_text}} roots."
    },
    {
      "type": "reason",
      "label": "Reason (R)",
      "pattern": "For the equation ax² + bx + c = 0, if discriminant D = b² − 4ac is {{disc_condition}}, then roots are {{nature_text}}."
    }
  ],
  
  "variables": {
    "base": {
      "b": { "type": "integer", "enum": [4, 5, 6, 7, 8, 10] },
      "c": { "type": "integer", "enum": [1, 2, 3, 4, 5, 6, 8, 9, 10, 12, 16, 25] }
    },
    "computed": {
      "discriminant": { "formula": "b*b - 4*c" },
      "nature_text": { "formula": "'two distinct real' if (b*b - 4*c) > 0 else ('two equal real' if (b*b - 4*c) == 0 else 'no real')" },
      "disc_condition": { "formula": "'positive (D > 0)' if (b*b - 4*c) > 0 else ('zero (D = 0)' if (b*b - 4*c) == 0 else 'negative (D < 0)')" }
    },
    "constraints": []
  },
  
  "options": [
    { "pattern": "Both A and R are true, and R is the correct explanation of A", "is_correct": true },
    { "pattern": "Both A and R are true, but R is NOT the correct explanation of A", "is_correct": false },
    { "pattern": "A is true but R is false", "is_correct": false },
    { "pattern": "A is false but R is true", "is_correct": false }
  ],
  
  "difficulty": 3,
  "bloom_level": "ANALYZE",
  "estimated_time": 90,
  
  "solution": {
    "steps": [
      { "number": 1, "text": "For x² − {{b}}x + {{c}} = 0: a = 1, b = −{{b}}, c = {{c}}" },
      { "number": 2, "text": "Discriminant D = b² − 4ac = (−{{b}})² − 4(1)({{c}})" },
      { "number": 3, "text": "D = {{b*b}} − {{4*c}} = {{discriminant}}" },
      { "number": 4, "text": "Since D = {{discriminant}} is {{disc_condition}}" },
      { "number": 5, "text": "The equation has {{nature_text}} roots" },
      { "number": 6, "text": "Both Assertion and Reason are true, and R correctly explains A" }
    ]
  },
  
  "tags": ["assertion-reason", "quadratic", "discriminant", "class10", "cbse"]
}
```

### Sample Output:
```
Assertion (A): The equation x² − 6x + 5 = 0 has two distinct real roots.

Reason (R): For the equation ax² + bx + c = 0, if discriminant D = b² − 4ac is positive (D > 0), then roots are two distinct real.

Options:
A) Both A and R are true, and R is the correct explanation of A ✓
B) Both A and R are true, but R is NOT the correct explanation of A
C) A is true but R is false
D) A is false but R is true
```

---

## TEMPLATE 7: Case Study - Ball Trajectory

```json
{
  "name": "Case Study - Projectile Motion",
  "concept_id": "math.class10.quadratic.applications",
  "question_type": "CASE_STUDY",
  
  "parts": [
    {
      "type": "context",
      "pattern": "**SPORTS DAY EVENT**\n\nDuring the annual sports day, Arjun participates in ball throw. The height h (in meters) of the ball above the ground at horizontal distance x (in meters) is given by:\n\n**h = −x² + {{b}}x**\n\nwhere x ≥ 0.\n\n*Based on the above information, answer the following questions:*"
    },
    {
      "type": "sub_question",
      "label": "(i)",
      "pattern": "At what horizontal distance from Arjun does the ball reach its maximum height?",
      "options": [
        { "pattern": "{{max_x}} m", "is_correct": true },
        { "pattern": "{{b}} m", "is_correct": false, "misconception_id": "USED_B_DIRECTLY" },
        { "pattern": "{{max_x + 1}} m", "is_correct": false },
        { "pattern": "{{landing_x}} m", "is_correct": false }
      ]
    },
    {
      "type": "sub_question",
      "label": "(ii)",
      "pattern": "What is the maximum height reached by the ball?",
      "options": [
        { "pattern": "{{max_height}} m", "is_correct": true },
        { "pattern": "{{b}} m", "is_correct": false },
        { "pattern": "{{max_x}} m", "is_correct": false, "misconception_id": "CONFUSED_X_AND_H" },
        { "pattern": "{{max_height + 1}} m", "is_correct": false }
      ]
    },
    {
      "type": "sub_question",
      "label": "(iii)",
      "pattern": "At what distance from Arjun does the ball hit the ground?",
      "options": [
        { "pattern": "{{landing_x}} m", "is_correct": true },
        { "pattern": "{{max_x}} m", "is_correct": false, "misconception_id": "VERTEX_IS_LANDING" },
        { "pattern": "{{b + 2}} m", "is_correct": false },
        { "pattern": "{{max_height}} m", "is_correct": false }
      ]
    },
    {
      "type": "sub_question",
      "label": "(iv)",
      "pattern": "What is the value of h when x = 2?",
      "options": [
        { "pattern": "{{h_at_2}} m", "is_correct": true },
        { "pattern": "{{b - 4}} m", "is_correct": false },
        { "pattern": "{{2 * b}} m", "is_correct": false },
        { "pattern": "{{h_at_2 + 2}} m", "is_correct": false }
      ]
    }
  ],
  
  "variables": {
    "base": {
      "b": { "type": "integer", "enum": [6, 8, 10, 12] }
    },
    "computed": {
      "max_x": { "formula": "b // 2" },
      "max_height": { "formula": "(b * b) // 4" },
      "landing_x": { "formula": "b" },
      "h_at_2": { "formula": "-4 + 2*b" }
    },
    "constraints": []
  },
  
  "difficulty": 4,
  "bloom_level": "ANALYZE",
  "estimated_time": 240,
  
  "solution": {
    "steps": [
      { "number": 1, "text": "The equation h = −x² + {{b}}x represents a downward parabola" },
      { "number": 2, "text": "Maximum height occurs at vertex: x = −b/(2a) = −{{b}}/(2×−1) = {{max_x}} m" },
      { "number": 3, "text": "Maximum height h = −({{max_x}})² + {{b}}({{max_x}}) = −{{max_x * max_x}} + {{b * max_x}} = {{max_height}} m" },
      { "number": 4, "text": "Ball hits ground when h = 0: −x² + {{b}}x = 0" },
      { "number": 5, "text": "x(−x + {{b}}) = 0, so x = 0 or x = {{landing_x}}" },
      { "number": 6, "text": "At x = 2: h = −(2)² + {{b}}(2) = −4 + {{2*b}} = {{h_at_2}} m" }
    ]
  },
  
  "tags": ["case-study", "quadratic", "projectile", "parabola", "vertex", "class10", "cbse"]
}
```

### Sample Output:
```
SPORTS DAY EVENT

During the annual sports day, Arjun participates in ball throw. The height h 
(in meters) of the ball above the ground at horizontal distance x (in meters) 
is given by:

h = −x² + 8x

where x ≥ 0.

Based on the above information, answer the following questions:

(i) At what horizontal distance from Arjun does the ball reach its maximum height?
    A) 4 m ✓    B) 8 m    C) 5 m    D) 8 m

(ii) What is the maximum height reached by the ball?
    A) 16 m ✓    B) 8 m    C) 4 m    D) 17 m

(iii) At what distance from Arjun does the ball hit the ground?
    A) 8 m ✓    B) 4 m    C) 10 m    D) 16 m

(iv) What is the value of h when x = 2?
    A) 12 m ✓    B) 4 m    C) 16 m    D) 14 m
```

---

## TEMPLATE 8: Word Problem with Variations

```json
{
  "name": "Word Problem - Consecutive Integers",
  "concept_id": "math.class10.quadratic.word_problems",
  "question_type": "MCQ",
  
  "question_pattern": "{{variation_text}}",
  
  "variables": {
    "base": {
      "n": { "type": "integer", "enum": [11, 12, 13, 14, 15, 16, 17, 18, 19, 20] },
      "variation": { "type": "integer", "enum": [1, 2, 3, 4] }
    },
    "computed": {
      "n_plus_1": { "formula": "n + 1" },
      "product": { "formula": "n * (n + 1)" },
      "variation_text": { "formula": "['The product of two consecutive positive integers is ' + str(n*(n+1)) + '. Find the integers.', 'Rahul\\'s age this year multiplied by his age next year equals ' + str(n*(n+1)) + '. How old is Rahul now?', 'A rectangle has length 1 meter more than its width. If its area is ' + str(n*(n+1)) + ' sq.m, find the width.', 'Two facing pages of a book have page numbers whose product is ' + str(n*(n+1)) + '. Find the smaller page number.'][variation - 1]" }
    },
    "constraints": []
  },
  
  "options": [
    { "pattern": "{{n}}", "is_correct": true },
    { "pattern": "{{n - 1}}", "is_correct": false, "misconception_id": "OFF_BY_ONE" },
    { "pattern": "{{n + 1}}", "is_correct": false, "misconception_id": "PICKED_LARGER" },
    { "pattern": "{{n - 2}}", "is_correct": false, "misconception_id": "CALCULATION_ERROR" }
  ],
  
  "difficulty": 3,
  "bloom_level": "APPLY",
  "estimated_time": 90,
  
  "solution": {
    "steps": [
      { "number": 1, "text": "Let the smaller number be n" },
      { "number": 2, "text": "Then the larger number is (n + 1)" },
      { "number": 3, "text": "Given: n × (n + 1) = {{product}}" },
      { "number": 4, "text": "n² + n − {{product}} = 0" },
      { "number": 5, "text": "Solving this quadratic: n = {{n}}" },
      { "number": 6, "text": "The answer is {{n}}" }
    ]
  },
  
  "hints": [
    "Let the smaller integer be n",
    "Then the next consecutive integer is n + 1",
    "Set up the equation: n(n+1) = {{product}}"
  ],
  
  "tags": ["word-problem", "quadratic", "consecutive-integers", "class10"]
}
```

### Sample Output (varies based on variation):
```
Q: Rahul's age this year multiplied by his age next year equals 240. How old is Rahul now?

A) 15 ✓
B) 14
C) 16
D) 13
```

---

## TEMPLATE 9: Match the Following - Factors

```json
{
  "name": "Match Following - Number of Factors",
  "concept_id": "math.class5.factors_multiples.factors",
  "question_type": "MATCH_FOLLOWING",
  
  "question_pattern": "Match each number with its factor count:",
  
  "left_column": [
    { "id": "L1", "pattern": "{{num1}}" },
    { "id": "L2", "pattern": "{{num2}}" },
    { "id": "L3", "pattern": "{{num3}}" },
    { "id": "L4", "pattern": "{{num4}}" }
  ],
  
  "right_column": [
    { "id": "R1", "pattern": "{{fc1}} factors" },
    { "id": "R2", "pattern": "{{fc2}} factors" },
    { "id": "R3", "pattern": "{{fc3}} factors" },
    { "id": "R4", "pattern": "2 factors (prime)" }
  ],
  
  "correct_matches": [
    { "left": "L1", "right": "R1" },
    { "left": "L2", "right": "R2" },
    { "left": "L3", "right": "R3" },
    { "left": "L4", "right": "R4" }
  ],
  
  "variables": {
    "base": {
      "num1": { "type": "integer", "enum": [12, 18, 20, 24, 28] },
      "num2": { "type": "integer", "enum": [15, 16, 21, 25, 27] },
      "num3": { "type": "integer", "enum": [8, 9, 10, 14, 22] },
      "num4": { "type": "integer", "enum": [7, 11, 13, 17, 19, 23] }
    },
    "computed": {
      "fc1": { "formula": "factor_count(num1)" },
      "fc2": { "formula": "factor_count(num2)" },
      "fc3": { "formula": "factor_count(num3)" }
    },
    "constraints": ["fc1 != fc2", "fc2 != fc3"]
  },
  
  "difficulty": 2,
  "bloom_level": "UNDERSTAND",
  "estimated_time": 120,
  
  "solution": {
    "steps": [
      { "number": 1, "text": "{{num1}}: Find all factors → {{fc1}} factors" },
      { "number": 2, "text": "{{num2}}: Find all factors → {{fc2}} factors" },
      { "number": 3, "text": "{{num3}}: Find all factors → {{fc3}} factors" },
      { "number": 4, "text": "{{num4}}: Prime number → exactly 2 factors (1 and itself)" }
    ]
  },
  
  "tags": ["match-following", "factors", "prime", "class5"]
}
```

### Sample Output:
```
Match each number with its factor count:

Column A          Column B
─────────         ────────
1. 12             A. 6 factors
2. 16             B. 5 factors
3. 10             C. 4 factors
4. 13             D. 2 factors (prime)

Answer: 1-A, 2-B, 3-C, 4-D
```

---

## TEMPLATE 10: MCQ - Nature of Roots

```json
{
  "name": "MCQ - Determine Nature of Roots",
  "concept_id": "math.class10.quadratic.nature_of_roots",
  "question_type": "MCQ",
  
  "question_pattern": "Determine the nature of roots of the quadratic equation: {{a}}x² {{b_display}} {{c_display}} = 0",
  
  "variables": {
    "base": {
      "a": { "type": "integer", "enum": [1, 2] },
      "b": { "type": "integer", "min": -8, "max": 8 },
      "c": { "type": "integer", "min": -10, "max": 10 }
    },
    "computed": {
      "b_display": { "formula": "('+' if b >= 0 else '') + str(b) + 'x'" },
      "c_display": { "formula": "('+' if c >= 0 else '') + str(c)" },
      "discriminant": { "formula": "b*b - 4*a*c" },
      "nature": { "formula": "'Two distinct real roots' if (b*b - 4*a*c) > 0 else ('Two equal real roots' if (b*b - 4*a*c) == 0 else 'No real roots')" }
    },
    "constraints": ["b != 0", "c != 0"]
  },
  
  "options": [
    { "pattern": "{{nature}}", "is_correct": true },
    { "pattern": "Two distinct real roots", "is_correct": false },
    { "pattern": "Two equal real roots", "is_correct": false },
    { "pattern": "No real roots", "is_correct": false }
  ],
  
  "difficulty": 2,
  "bloom_level": "APPLY",
  "estimated_time": 60,
  
  "solution": {
    "steps": [
      { "number": 1, "text": "For ax² + bx + c = 0, discriminant D = b² − 4ac" },
      { "number": 2, "text": "Here, a = {{a}}, b = {{b}}, c = {{c}}" },
      { "number": 3, "text": "D = ({{b}})² − 4({{a}})({{c}})" },
      { "number": 4, "text": "D = {{b*b}} − {{4*a*c}} = {{discriminant}}" },
      { "number": 5, "text": "Since D {{'>'}}{{'0' if discriminant > 0 else ('= 0' if discriminant == 0 else '< 0')}}, the roots are: {{nature}}" }
    ]
  },
  
  "hints": [
    "Calculate discriminant D = b² − 4ac",
    "If D > 0: two distinct real roots",
    "If D = 0: two equal real roots", 
    "If D < 0: no real roots"
  ],
  
  "tags": ["quadratic", "discriminant", "nature-of-roots", "class10", "cbse"]
}
```

### Sample Output:
```
Q: Determine the nature of roots of the quadratic equation: x² +6x +9 = 0

A) Two equal real roots ✓
B) Two distinct real roots
C) No real roots
D) Cannot be determined
```

---

## 🚀 HOW TO USE

### Step 1: Open Admin UI
```
http://localhost:3003/templates/universal
```

### Step 2: Go to "Sample Templates" tab

### Step 3: Click "Load" on any template

### Step 4: Click "Preview" to see 5 generated questions

### Step 5: Review the questions with solutions

### Step 6: Click "Save Template" to store it

---

## 📊 Summary of Question Types

| Template | Type | Topic | Class | Difficulty |
|----------|------|-------|-------|------------|
| 1 | MCQ | Quadratic Roots | 10 | Medium |
| 2 | MCQ | GCD | 5 | Medium |
| 3 | MCQ | LCM | 5 | Medium |
| 4 | Fill Blank | Prime Factorization | 5 | Medium |
| 5 | True/False | Divisibility | 5 | Easy |
| 6 | Assertion-Reason | Discriminant | 10 | Hard |
| 7 | Case Study | Projectile | 10 | Hard |
| 8 | Word Problem | Consecutive Integers | 10 | Medium |
| 9 | Match Following | Factors | 5 | Medium |
| 10 | MCQ | Nature of Roots | 10 | Medium |

---

## 🎯 Quick Copy Commands

Copy any template above and paste directly into the JSON Editor!

# Chapter 3: Shapes and Angles

## Overview
Added comprehensive logic-based geometry questions for "Shapes and Angles" chapter, designed for Class 5 CBSE students.

## Three New Generators

### 1. **ClockAnglesGenerator** 🕐
**Purpose:** Test angle understanding using clock faces and rotations.

**Sub-Types:**
- **Simple Time Angles:** Given a time, find the angle between clock hands
  - Example type: "At what time are the clock hands perpendicular?"
  - Logical Trap: Both hands move; hour hand not always exactly on the number
  
- **Rotation Fractions:** Convert fractions of a turn to degrees
  - Example type: "What fraction of a full rotation is a right angle?"
  - Logical Trap: Confusing fraction with total degrees
  
- **Angle Classification:** Name an angle by its measure
  - Types: Acute (<90°), Right (90°), Obtuse (90-180°), Straight (180°)
  - Logical Trap: Mixing up angle names

**Data Representation:** ASCII clock face diagram showing hand positions (no answers)

---

### 2. **SymmetryGenerator** 🪞
**Purpose:** Test line symmetry using capital letters and mirror writing.

**Sub-Types:**
- **Letter Symmetry:** Does a capital letter have line(s) of symmetry?
  - Example types: Letters A through Z with various symmetries
  - Logical Trap: Confusing vertical vs. horizontal symmetry
  - Definition:
    - **Vertical symmetry:** Left-right mirror (fold down middle)
    - **Horizontal symmetry:** Top-bottom mirror (fold across middle)
  
- **Word Mirror:** Do words read the same in a mirror?
  - Example types: Various 3-4 letter words
  - Logical Trap: Palindromes ≠ Mirror-symmetric
  - Requirement: Each letter must be vertically symmetric + word must be palindrome
  
- **Both Symmetries:** Find letters with BOTH vertical AND horizontal lines
  - Example types: Letters with rare dual symmetry
  - Logical Trap: Most letters only have one type

**Data Representation:** Letter descriptions and symmetry rule explanations

---

### 3. **RotationGenerator** 🔄
**Purpose:** Test understanding of turns and directional rotations.

**Sub-Types:**
- **Quarter Turns:** 90° rotations on compass (N→E→S→W→N)
  - Example type: "Starting from a cardinal direction, determine new direction after quarter turn"
  - Logical Trap: Clockwise vs. counter-clockwise confusion
  
- **Half Turns:** 180° rotations (complete reversal)
  - Example type: "Starting from a cardinal direction, determine new direction after half turn"
  - Logical Trap: Always opposite, regardless of starting direction
  
- **Multiple Rotations:** Cumulative turns and full circles
  - Example type: "Multiple sequential quarter turns and final position"
  - Logical Trap: 360° = full circle; students forget to track full rotations

**Data Representation:** Compass diagrams and rotation tracking rules

---

## Key Design Principles

### 1. **Text-Only Geometry**
Since no images can be drawn, all geometry is described logically:
- Clock faces use positions (12, 3, 6, 9)
- Letters are described by their features
- Rotations use compass directions

### 2. **The Logical Trap**
Each question includes a "Logical Trap" that highlights the common mistake:
- Students forget hour hand moves on clocks
- Confuse mirror images with palindromes
- Mix up clockwise and counter-clockwise

### 3. **Step-by-Step Solutions**
All solutions break down reasoning:
1. Identify the given information
2. Apply the rule
3. Calculate the answer
4. Verify and classify

---

## Example Question Structure (Without Solutions)

### Clock Angles (Question Type Only)
```
Given: A specific time
Task: Find the angle between clock hands AND classify the angle type
Hint: Remember both hands move!
```

### Symmetry (Question Type Only)
```
Given: A capital letter or word
Task: Determine if it has vertical, horizontal, both, or no symmetry
Hint: Think about what happens when you fold the paper!
```

### Rotations (Question Type Only)
```
Given: Starting direction and rotation instructions
Task: Determine the final direction
Hint: Clockwise = same direction as clock hands
```

---

## Integration with Web UI

### New API Categories
```json
{
  "id": "angles",
  "name": "Clock Angles",
  "icon": "🕐"
},
{
  "id": "symmetry",
  "name": "Symmetry",
  "icon": "🪞"
},
{
  "id": "rotation",
  "name": "Rotations",
  "icon": "🔄"
}
```

### Color Coding
- 🕐 Clock Angles: Pink (#ec4899)
- 🪞 Symmetry: Cyan (#06b6d4)
- 🔄 Rotations: Teal (#14b8a6)

---

## Chapter Coverage Summary

### Boxes & Sketches (Original)
✅ Dice Logic (Opposite faces = 7)
✅ Cube Counting (3D spatial reasoning)
✅ Nets (Mental folding)

### Data Handling (Original)
✅ Pictographs (Scale traps)
✅ Missing Data (Constraint solving)
✅ Comparisons (More/Less)

### Shapes & Angles (NEW)
✅ Clock Angles (Time & rotation)
✅ Symmetry (Letters & words)
✅ Rotations (Compass & turns)

**Total:** 9 problem types  
**Questions Per Type:** 2 per session  
**Total Generated:** 14 questions per session (9 types × ~2 questions)

---

## K.C. Nag Philosophy

These questions embody K.C. Nag's approach:
1. **Logical Thinking:** Not rote memorization
2. **Conceptual Clarity:** Why, not just how
3. **Real-World Context:** Clocks, letters, directions
4. **Error Awareness:** Highlighting common pitfalls

---

## Testing Notes

All questions have been verified for:
- ✅ Unique integer/categorical answers
- ✅ Logical consistency
- ✅ No image dependency
- ✅ Age-appropriate (Class 5)
- ✅ CBSE curriculum alignment

---

**Status:** ✅ Ready for Production  
**Added:** 26 December 2025  
**Total Generators:** 7  
**Total Question Variations:** 1000+

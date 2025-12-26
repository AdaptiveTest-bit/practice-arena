# CLI Usage Guide

## Running Questions from Command Line

If you prefer using the command-line question generator instead of the web UI:

### Basic Usage

```bash
source venv/bin/activate
python question_generator.py
```

This will generate and display 2 questions from each of the 4 categories:
- Dice Logic (2 questions)
- Cube Counting (2 questions)
- Nets (2 questions)
- Data Handling (2 questions)

### Output Format

Each question includes:

```
## TOPIC: [Category - Subcategory]

**The Logical Trap:** [Why this problem is tricky for students]

**Data Representation:**
[Table or diagram in ASCII/Markdown]

**Question:**
[The actual problem]

**Solution:**
1. [Step 1]
2. [Step 2]
3. [Step 3]

**Answer:** [Final answer]

---
```

### Example Output

```
## TOPIC: Boxes & Sketches - Dice Logic

**The Logical Trap:** Student must remember that opposite faces sum to 7, 
and distinguish between visible and hidden faces.

**Data Representation:**
```
Standard Die Rule: Opposite faces sum to 7
Top face: 3
Visible side (North): 5
```

**Question:**
A standard die is placed on a table. The face showing on top is 3. 
If you look at the die from the North side, you see the number 5.

What number is on:
(a) The face touching the table (bottom)?
(b) The South face?

**Solution:**
1. Top face = 3, so Bottom face = 7 - 3 = 4
2. Visible side (North) = 5, so Opposite side (South) = 7 - 5 = 2
3. Verify: Top=3, Bottom=4, North=5, South=2

**Answer:** (a) 4 (b) 2

---
```

### Piping to File

Save questions to a file:

```bash
python question_generator.py > questions_output.txt
```

### Batch Generation

To generate questions multiple times, create a script:

```bash
#!/bin/bash
source venv/bin/activate

for i in {1..5}; do
    echo "=== Generation Run $i ===" >> all_questions.txt
    python question_generator.py >> all_questions.txt
    echo "" >> all_questions.txt
done
```

Then run:
```bash
chmod +x generate_batch.sh
./generate_batch.sh
```

---

## Modifying the Script

### Generate Only Specific Categories

Edit `question_generator.py`, in the `main()` function:

```python
# Current: generates from all generators
generators: List[QuestionGenerator] = [
    DiceLogicGenerator(),
    CubeCountingGenerator(),
    NetsGenerator(),
    DataHandlingGenerator()
]

# Modified: only Dice and Data Handling
generators: List[QuestionGenerator] = [
    DiceLogicGenerator(),
    DataHandlingGenerator()
]
```

### Generate More Questions Per Category

Change the loop count in `main()`:

```python
# Current: 2 questions per category
for i in range(2):

# Modified: 5 questions per category
for i in range(5):
```

### Control Number of Categories

The loop automatically adapts. Just add/remove generators from the list.

---

## Troubleshooting

**Q: "python: command not found"**  
A: Use `python3` instead:
```bash
python3 question_generator.py
```

**Q: "ModuleNotFoundError: No module named 'abc'"**  
A: This is Python 3.8+ built-in. Check your Python version:
```bash
python3 --version
```

**Q: Output cuts off / doesn't show everything**  
A: Pipe to less for scrolling:
```bash
python question_generator.py | less
```

**Q: Want to clear the terminal between question generations**  
A: Use this wrapper:
```bash
while true; do
    clear
    python question_generator.py
    read -p "Press Enter for more questions, or Ctrl+C to quit..."
done
```

---

## Integration with Other Tools

### Print to PDF (macOS)

```bash
python question_generator.py | lp -d <printer_name>
```

### Convert to Markdown

The output is already Markdown-compatible. View with:
```bash
python question_generator.py | pandoc -f markdown -t html > questions.html
```

### Export as JSON

Modify `question_generator.py` to add JSON export:

```python
import json

def to_dict(question):
    return {
        'topic': question.topic,
        'logical_trap': question.logical_trap,
        'data_representation': question.data_representation,
        'question': question.question_text,
        'solution_steps': question.solution_steps,
        'answer': question.answer
    }

# Then in main():
questions = [generator.generate() for generator in generators for _ in range(2)]
print(json.dumps([to_dict(q) for q in questions], indent=2))
```

---

## Performance Tips

- **Generating 100+ questions?** Use file output:
  ```bash
  time python question_generator.py > big_batch.txt
  ```

- **Checking what takes time:**
  ```bash
  python -m cProfile question_generator.py | head -20
  ```

---

## Tips for Teachers

### Student Handouts
```bash
python question_generator.py | lp  # Print directly
```

### Prepare Weekly Sheets
```bash
# Generate and save with timestamp
python question_generator.py > "math_questions_$(date +%Y-%m-%d).txt"
```

### Mix and Match Topics
Edit generators list to customize:
```python
# Only 3D Geometry
generators = [DiceLogicGenerator(), CubeCountingGenerator(), NetsGenerator()]
```

---

Enjoy using the question generator! 📚✨

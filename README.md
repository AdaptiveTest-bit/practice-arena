# CBSE Class 5 Mathematics Question Generator
## Strict Logic-Based Questions (K.C. Nag Style)

**Target:** Class 5 CBSE Students  
**Status:** ✅ Production Ready (3 Chapters, 7 Generators)

---

## 📚 Chapters Covered

### 1. **Boxes & Sketches** (3D Geometry)
- **Dice Logic:** Opposite faces rule (sum = 7)
- **Cube Counting:** 3D spatial reasoning with removal scenarios
- **Nets:** Mental folding exercises for visualization

### 2. **Data Handling** (Tables, Graphs, Pictographs)
- **Scale Trap:** Non-unitary pictograph scales (1 symbol ≠ 1 item)
- **Missing Data:** Calculate missing values using totals
- **Comparison:** "How many MORE/LESS" problems

### 3. **Shapes and Angles** (NEW! ✨)
- **Clock Angles:** Time-based angles and rotation fractions
- **Symmetry:** Letter and word mirror writing logic
- **Rotations:** Quarter turns, half turns, compass directions

---

## ✨ Features

✅ **Rigorous Mathematics:** All problems have unique integer solutions  
✅ **K.C. Nag Style:** Emphasizes logical traps and reasoning  
✅ **Interactive UI:** Modern web interface with question cards  
✅ **Real-time Generation:** Fetch new questions on demand  
✅ **Visual Feedback:** Animations, color coding, progress tracking  
✅ **Mobile-Friendly:** Responsive design for all devices  

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Installation & Setup

1. **Create Virtual Environment** (recommended)
```bash
cd /Users/kunalranjan/edtech/question-generator
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
```

2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the Web Server**
```bash
python app.py
```

4. **Open in Browser**
Navigate to: `http://127.0.0.1:5001`

---

## 📁 Project Structure

```
question-generator/
├── app.py                      # Flask backend server
├── question_generator.py       # Question generation logic
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── templates/
│   └── index.html             # Main HTML template
├── static/
│   ├── styles.css             # Beautiful UI styling
│   └── script.js              # Frontend interactions
└── venv/                       # Virtual environment
```

---

## 🎯 How It Works

### Architecture

```
┌─────────────────────────────────────────┐
│         Browser (Frontend)              │
│  - Question Cards                       │
│  - Interactive UI                       │
│  - Solution Display                     │
└────────────────┬────────────────────────┘
                 │ HTTP/JSON
┌────────────────▼────────────────────────┐
│      Flask Server (app.py)              │
│  - /api/question (GET new question)     │
│  - /api/reveal/:id (GET solution)       │
│  - /api/categories (GET topics)         │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│   Question Generator (question_generator.py)
│  - DiceLogicGenerator                   │
│  - CubeCountingGenerator                │
│  - NetsGenerator                        │
│  - DataHandlingGenerator                │
└─────────────────────────────────────────┘
```

### API Endpoints

#### 1. **Get Categories**
```
GET /api/categories
Response: {
  "success": true,
  "categories": [
    {
      "id": "dice",
      "name": "Dice Logic",
      "icon": "🎲",
      "description": "Opposite faces sum to 7"
    },
    ...
  ]
}
```

#### 2. **Fetch Question**
```
POST /api/question
Body: { "category": "dice" }  # Optional
Response: {
  "success": true,
  "questionId": 123456,
  "category": "dice",
  "categoryName": "Dice Logic",
  "topic": "Boxes & Sketches - Dice Logic",
  "logicalTrap": "Student must remember...",
  "dataRepresentation": "...",
  "question": "..."
}
```

#### 3. **Reveal Solution**
```
GET /api/reveal/:questionId
Response: {
  "success": true,
  "solutionSteps": ["Step 1", "Step 2", ...],
  "answer": "Final answer"
}
```

---

## 🎨 Interactive Features

### Question Card Components

1. **Topic Badge** - Color-coded by category
2. **Question Title** - Clear problem statement
3. **Logical Trap** (⚠️) - Highlights why this is tricky
4. **Data Representation** (📊) - Tables, diagrams, code blocks
5. **Question Text** - The problem to solve
6. **Reveal Button** - Click to show solution
7. **Solution Steps** - Step-by-step derivation
8. **Statistics** - Track questions generated

### Category Colors
- 🎲 Dice Logic: **Red** (#ef4444)
- 📦 Cube Counting: **Amber** (#f59e0b)
- 📐 Nets: **Purple** (#8b5cf6)
- 📊 Data Handling: **Blue** (#2563eb)

---

## 💻 Running in Development Mode

The Flask development server includes:
- ✅ Auto-reload on code changes
- ✅ Interactive debugger
- ✅ Detailed error messages

```bash
source venv/bin/activate
python app.py
# Server runs on http://127.0.0.1:5000
```

### For Production

Use Gunicorn (WSGI server):
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

---

## 📊 Example Questions

### Type 1: Dice Logic
**Question:** A standard die shows 3 on top, 5 on North side. What's on bottom and South?
**Solution:** Bottom = 7-3 = 4, South = 7-5 = 2

### Type 2: Cube Counting
**Question:** 3×3×3 block with one corner removed. How many cubes remain?
**Solution:** 27 - 1 = 26

### Type 3: Nets
**Question:** Which square becomes opposite in a folded cube net?
**Solution:** Trace folding path; opposite = 3 edges away

### Type 4: Data Handling (Scale Trap)
**Question:** 1 symbol = 8 items. Shows 5 symbols. How many items?
**Solution:** 5 × 8 = 40 items ⚠️ (NOT just 5!)

---

## 🔧 Customization

### Add New Question Types

Edit `question_generator.py`:

```python
class YourCustomGenerator(QuestionGenerator):
    def generate(self) -> Question:
        return Question(
            topic="Your Topic",
            logical_trap="Why it's tricky...",
            data_representation="...",
            question_text="...",
            solution_steps=["Step 1", "Step 2"],
            answer="..."
        )
```

Then update `app.py`:
```python
GENERATORS['custom'] = YourCustomGenerator()
```

---

## 🐛 Troubleshooting

### "Module not found: Flask"
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### "Port 5000 already in use"
```bash
# Use different port
python -c "from app import app; app.run(port=5001)"
```

### Questions not loading
- Check browser console (F12) for errors
- Verify Flask server is running
- Check `/api/question` endpoint in terminal

---

## 📝 Notes

- All questions generated have **unique integer solutions**
- Opposite faces on a die **always sum to 7**
- Pictograph scale is **always non-unitary** (1 ≠ 1)
- Missing data problems use **subtraction from total**

---

## 📚 References

- **K.C. Nag:** Mathematics pedagogy expert for Indian CBSE curriculum
- **CBSE Class 5:** Official curriculum standards
- **Educational Psychology:** Emphasis on logical thinking, not rote learning

---

## 📄 License

Educational resource for CBSE Class 5 students.

---

## 🤝 Contributing

To add more question variations, edit the generator classes in `question_generator.py`.

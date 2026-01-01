# Quick Start - Run the Full System

**Date:** January 1, 2026

## Prerequisites

✅ Python 3.9+ (for backend)  
✅ Node.js 18+ (for frontend)  
✅ npm or yarn (for frontend packages)

## Step 1: Backend Setup (Terminal 1)

```bash
# Navigate to backend directory
cd /Users/kunalranjan/edtech/question-generator/backend

# Install Python dependencies (first time only)
pip install -r requirements.txt

# Start the backend
python app_main.py
```

**Expected Output:**
```
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:5002 (Press CTRL+C to quit)
```

✅ **Backend is ready when you see:** "Application startup complete"

## Step 2: Frontend Setup (Terminal 2)

```bash
# Navigate to frontend directory
cd /Users/kunalranjan/edtech/question-generator/frontend

# Install dependencies (first time only)
npm install

# Start the development server
npm run dev
```

**Expected Output:**
```
> next dev
  ▲ Next.js 16.1.1
  - ready started server on 0.0.0.0:3000
  - event compiled client and server successfully
```

✅ **Frontend is ready when you see:** "compiled client and server successfully"

## Step 3: Access the Application

Open your browser and go to:

```
http://localhost:3000
```

You should see the quiz application!

---

## Testing the Connection

### Test 1: Register a Student

1. Open http://localhost:3000
2. Click "Register" or go to registration page
3. Fill in student details
4. Submit

**Success Indicator:** No error message, registration completes

### Test 2: Start a Quiz

1. After registration, click "Start Quiz"
2. Select a chapter
3. Click "Begin"

**Success Indicator:** Question appears on screen

### Test 3: Answer a Question

1. Select an option
2. Click "Submit"

**Success Indicator:** Feedback appears, next question loads

---

## Troubleshooting

### Issue: "Connection refused" on port 5002

**Solution:**
1. Make sure backend is running in Terminal 1
2. Check output says "Uvicorn running on http://0.0.0.0:5002"
3. If not, backend might be on different port - check the log

```bash
# Verify backend is running
curl http://localhost:5002/health
# Should return: {"status":"ok"}
```

### Issue: "Cannot find module" in frontend

**Solution:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### Issue: Port 3000 already in use

**Solution:**
```bash
# Kill the process using port 3000
lsof -i :3000
kill -9 <PID>

# Then restart frontend
npm run dev
```

### Issue: Port 5002 already in use

**Solution:**
```bash
# Kill the process using port 5002
lsof -i :5002
kill -9 <PID>

# Then restart backend
python app_main.py
```

### Issue: API returns 404 errors

**Cause:** Frontend and backend endpoints mismatched  
**Solution:** Make sure you have the latest code (API fixes applied)

```bash
# Check quizClient.ts uses /api/quiz/ paths (not /practice/)
grep -n "api/quiz" frontend/lib/api/quizClient.ts
# Should show multiple matches
```

---

## System Architecture

```
┌─────────────────────────┐
│   Browser (Port 3000)   │
│   http://localhost:3000 │
└────────────┬────────────┘
             │
             │ HTTP REST API
             │
┌────────────▼────────────┐
│   Backend (Port 5002)   │
│ http://localhost:5002   │
│   FastAPI + SQLAlchemy  │
└────────────┬────────────┘
             │
             │ SQL
             │
┌────────────▼────────────┐
│  PostgreSQL Database    │
└─────────────────────────┘
```

---

## Common URLs

| Component | URL | Purpose |
|-----------|-----|---------|
| **Frontend** | http://localhost:3000 | Quiz UI |
| **Backend** | http://localhost:5002 | API server |
| **Health Check** | http://localhost:5002/health | Verify backend running |
| **API Base** | http://localhost:5002/api | All API endpoints |

---

## Stopping Services

### Stop Backend (Terminal 1)
```
Press CTRL+C
```

### Stop Frontend (Terminal 2)
```
Press CTRL+C
```

---

## Development Tips

**Hot Reload:**
- Frontend automatically reloads on code changes ✅
- Backend requires manual restart on code changes

**Debugging:**
- Frontend console: Open DevTools (F12) → Console
- Backend logs: Check Terminal 1 output
- API logs: See request/response in Terminal 1

**Database:**
- PostgreSQL data persists between runs
- Tables created automatically on first run
- Check `backend/ARCHITECTURE.md` for schema details

---

## Next Steps

1. ✅ Run the system (this guide)
2. 📖 Read `/README.md` - Project overview
3. 📖 Read `/backend/ARCHITECTURE.md` - System details
4. 🧪 Test all features
5. 🚀 Deploy to production (see ARCHITECTURE.md)

---

## Getting Help

**For Questions About:**

- **Running the system** → Read this file
- **System architecture** → Read `/backend/ARCHITECTURE.md`
- **Frontend setup** → Read `/frontend/README.md`
- **API endpoints** → Read `API_ENDPOINT_FIX_LOG.md`
- **Project structure** → Read `/README.md`

---

**Status:** ✅ Ready to use  
**Last Updated:** January 1, 2026


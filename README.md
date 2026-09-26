# Smart AI Study Planner — Full Step-by-Step Guide

A simple GenAI project: you enter your subjects, exam date, and daily study hours,
and an AI (OpenAI GPT) generates a personalized day-by-day study plan, which gets
saved in a database.

**Stack:** Python + FastAPI (backend) → OpenAI API (the "AI" part) → SQLite (database) → HTML/CSS/JS (frontend)

This stack is chosen because it's the simplest possible GenAI project you can
honestly explain in an interview: one API call to an LLM, one database table,
one form.

---

## 1. Install the required software

| Software | Why | Download link |
|---|---|---|
| Python 3.10+ | Runs the backend | https://www.python.org/downloads/ |
| VS Code | Code editor | https://code.visualstudio.com/download |
| Git (optional but recommended) | Version control | https://git-scm.com/downloads |

**Windows install check** — open Command Prompt and run:
```
python --version
```
If it shows a version number (e.g. `Python 3.11.5`), you're good. If not, reinstall
Python and make sure you tick **"Add Python to PATH"** during setup.

You do **not** need to install Node.js — the frontend here is plain HTML/CSS/JS,
opened directly in the browser.

---

## 2. Get an OpenAI API key (the "AI" part)

1. Go to https://platform.openai.com/signup and create an account.
2. Go to https://platform.openai.com/api-keys → **Create new secret key**.
3. Copy the key (starts with `sk-...`). You won't be able to see it again later.
4. Add a small amount of billing credit (a few dollars is enough for testing) at
   https://platform.openai.com/account/billing — the API does not work on a
   completely empty balance.

Keep this key private — never put it directly in code you upload to GitHub.

---

## 3. Project folder structure

```
study-planner/
├── backend/
│   ├── main.py          → API server + AI logic
│   ├── database.py       → SQLite database setup
│   ├── requirements.txt  → Python packages needed
│   └── .env              → your API key (you create this)
└── frontend/
    ├── index.html         → the form the user sees
    ├── style.css          → styling
    └── script.js          → connects frontend to backend
```

---

## 4. Backend setup (step by step)

Open VS Code → open the `study-planner` folder → open a terminal (`` Ctrl + ` ``).

**Step 1 — go into the backend folder:**
```
cd backend
```

**Step 2 — create a virtual environment** (keeps this project's packages separate
from other Python projects on your system):
```
python -m venv venv
```

**Step 3 — activate it:**
- Windows: `venv\Scripts\activate`
- Mac/Linux: `source venv/bin/activate`

You'll see `(venv)` appear at the start of your terminal line when it's active.

**Step 4 — install the required packages:**
```
pip install -r requirements.txt
```

**Step 5 — add your API key.**
Copy `.env.example` to a new file named `.env` in the same `backend` folder, and
paste your real key in:
```
OPENAI_API_KEY=sk-your-real-key-here
```

**Step 6 — start the backend server:**
```
uvicorn main:app --reload
```

If it worked, you'll see something like:
```
Uvicorn running on http://127.0.0.1:8000
```
Open that link in your browser — you should see:
```json
{"status": "Smart AI Study Planner backend is running"}
```

That confirms: Python is working, FastAPI is running, and the database file
(`study_planner.db`) has been auto-created inside `backend/`.

---

## 5. Frontend setup (step by step)

The frontend is plain HTML/CSS/JS, so there's nothing to install.

**Step 1 —** go to the `frontend` folder.

**Step 2 —** double-click `index.html` to open it in your browser
(or right-click → "Open with" → your browser).

**Step 3 —** Keep the backend terminal (from Section 4) running in the
background — the frontend needs it to generate plans.

---

## 6. How the frontend and backend connect (the important part)

This is the part interviewers usually ask about, so understand it:

1. `index.html` has a form (subjects, exam date, hours/day).
2. When you click **Generate Study Plan**, `script.js` runs.
3. `script.js` sends a `fetch()` POST request to
   `http://127.0.0.1:8000/generate-plan` with your form data as JSON.
4. `main.py` (FastAPI) receives that request, builds a prompt, and sends it to
   OpenAI's API using the `openai` Python library.
5. OpenAI's model generates the study plan as text.
6. `main.py` saves that plan into the SQLite database (`database.py` defines
   the table) and sends the plan back to the browser as a JSON response.
7. `script.js` receives the response and displays it on the page.

This request → AI → database → response loop **is** the GenAI project.

---

## 7. Test it end-to-end

1. Make sure the backend terminal shows `Uvicorn running on http://127.0.0.1:8000`.
2. Open `frontend/index.html` in your browser.
3. Fill in: Subjects = `Maths, Physics, DBMS`, pick an exam date a few weeks out,
   Hours/day = `4`.
4. Click **Generate Study Plan**.
5. Within a few seconds, a day-by-day plan should appear on the page.

If you get an error: check the backend terminal — it usually prints the exact
reason (wrong/missing API key, no billing credit, etc).

---

## 8. What to say about this on your resume / in an interview

Be accurate — this is what makes it a real, defensible project:

- "Built a full-stack GenAI study planner: FastAPI backend, SQLite database,
  vanilla JS frontend, integrated with the OpenAI API to generate personalized
  study schedules from user input."
- Mention you understand: prompt construction, REST API design between
  frontend/backend, and basic database persistence (SQLAlchemy models).
- Be ready to explain the request flow described in Section 6 — that's the
  most common interview question for a project like this.

---

## 9. Optional next steps (if you want to go further)

- Deploy the backend on **Render** (free tier) and the frontend on
  **Netlify/Vercel**, so you have a live link to share.
- Add a `/plans` history page on the frontend showing past plans (the
  `GET /plans` endpoint already exists in `main.py`).
- Swap OpenAI for a free alternative (e.g. Google Gemini API free tier) if you
  don't want to add billing.
"# study-planner" 

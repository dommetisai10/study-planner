"""
main.py
-------
The backend "brain" of the Smart AI Study Planner.

What it does:
1. Exposes a POST /generate-plan endpoint.
2. Takes subjects + exam date + hours/day from the frontend.
3. Sends a prompt to an LLM (OpenAI) to generate a day-by-day study plan.
4. Saves the result in the SQLite database.
5. Also exposes GET /plans to fetch past plans (so the frontend has "history").

Run this with:  uvicorn main:app --reload
"""

import os
import json
import re
from datetime import datetime
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from openai import OpenAI

from database import init_db, get_db, StudyPlan

load_dotenv()  # reads variables from the .env file (like your API key)

app = FastAPI(title="Smart AI Study Planner")

# Allows the frontend (running on a different port/file) to call this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()  # creates study_planner.db and the table, first time it runs

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)


class PlanRequest(BaseModel):
    subjects: str            # "Maths, Physics, DBMS"
    exam_date: str            # "2026-11-15"
    hours_per_day: int        # 4
    syllabus: str = ""        # optional — pasted topic list / syllabus text


@app.get("/")
def health_check():
    return {"status": "Smart AI Study Planner backend is running"}


def extract_json(raw_text: str) -> dict:
    """The model sometimes wraps JSON in ```json ... ``` fences or adds stray
    text around it. This pulls out just the {...} block and parses it."""
    cleaned = raw_text.strip()
    cleaned = re.sub(r"^```(json)?", "", cleaned.strip())
    cleaned = re.sub(r"```$", "", cleaned.strip())
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if match:
        cleaned = match.group(0)
    return json.loads(cleaned)


@app.post("/generate-plan")
def generate_plan(request: PlanRequest, db: Session = Depends(get_db)):
    days_left = (datetime.strptime(request.exam_date, "%Y-%m-%d") - datetime.now()).days

    syllabus_block = (
        f"""
    Syllabus / topics to cover (use these EXACT topics when filling "topics" for
    each day — do not invent generic topics, only schedule what's listed here):
    {request.syllabus}
    """
        if request.syllabus.strip()
        else "No syllabus was provided — use your best judgement for standard topics per subject."
    )

    prompt = f"""
    You are a study planning assistant. Create a day-by-day study plan and
    return ONLY valid JSON (no markdown fences, no commentary) in this exact
    shape:

    {{
      "total_days": <number>,
      "summary": "<one short sentence overview of the strategy>",
      "days": [
        {{
          "day": 1,
          "label": "<e.g. 'Day 1 - Oct 1'>",
          "focus": "<subject(s) covered that day, short>",
          "topics": "<specific topics for that day, short>",
          "hours": <number>
        }}
      ]
    }}

    Subjects: {request.subjects}
    Exam date: {request.exam_date}
    Days left: {days_left}
    Study hours available per day: {request.hours_per_day}

    {syllabus_block}

    Rules:
    - Create one entry per day, covering every day up to and including the exam.
    - Split time fairly across all subjects.
    - If a syllabus was given, make sure every topic in it is scheduled at least
      once before the exam, and don't repeat/pad with topics not in the list.
    - Add revision-only days in the final stretch before the exam.
    - Keep "focus" and "topics" short (a few words), suitable for a table cell.
    - Return raw JSON only — it will be parsed directly by a program.
    """

    response = client.chat.completions.create(
        model="gemini-3.8-flash",
        messages=[
            {"role": "system", "content": "You are a study planning assistant that replies only with valid JSON, never prose or markdown fences."},
            {"role": "user", "content": prompt},
        ],
    )

    raw_text = response.choices[0].message.content
    plan_json = extract_json(raw_text)

    # Save the structured plan (as a JSON string) in the database
    new_plan = StudyPlan(
        subjects=request.subjects,
        exam_date=request.exam_date,
        hours_per_day=request.hours_per_day,
        plan_text=json.dumps(plan_json),
    )
    db.add(new_plan)
    db.commit()
    db.refresh(new_plan)

    return {"id": new_plan.id, "plan": plan_json}


@app.get("/plans")
def get_plans(db: Session = Depends(get_db)):
    plans = db.query(StudyPlan).order_by(StudyPlan.id.desc()).all()
    return [
        {
            "id": p.id,
            "subjects": p.subjects,
            "exam_date": p.exam_date,
            "hours_per_day": p.hours_per_day,
            "plan": p.plan_text,
            "created_at": p.created_at.isoformat(),
        }
        for p in plans
    ]

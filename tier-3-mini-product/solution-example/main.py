import os
import datetime
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
import httpx
from dotenv import load_dotenv

# Load local environment variables from .env
load_dotenv()

from database import init_db, save_engineers, get_all_engineers
from core import parse_and_validate_csv, calculate_dashboard_metrics

app = FastAPI(title="Training Compliance Dashboard")

# Initialize SQLite database on startup
@app.on_event("startup")
def startup_event():
    init_db()

# Mount static files folder
# We will create static folder containing HTML/CSS/JS
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
def get_index():
    # Helper to serve static/index.html directly at root
    try:
        with open("static/index.html", "r") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Dashboard Frontend under construction...</h1><p>Please build static/index.html</p>")

@app.post("/api/upload")
async def upload_csv(file: UploadFile = File(...)):
    # Validate content type
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed.")
        
    try:
        content = await file.read()
        csv_text = content.decode("utf-8")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read file content: {str(e)}")

    valid_rows, rejected_rows = parse_and_validate_csv(csv_text)
    
    # Save valid rows to DB if any exist
    if valid_rows:
        try:
            save_engineers(valid_rows)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database save failed: {str(e)}")
            
    return {
        "success": True,
        "summary": {
            "total_processed": len(valid_rows) + len(rejected_rows),
            "valid_imported": len(valid_rows),
            "rejected_count": len(rejected_rows)
        },
        "rejected_rows": rejected_rows
    }

@app.get("/api/dashboard")
def get_dashboard_data():
    try:
        engineers = get_all_engineers()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to query database: {str(e)}")
        
    metrics = calculate_dashboard_metrics(engineers)
    return metrics

class ReminderRequest(BaseModel):
    name: str
    email: str
    course: str
    deadline: str

@app.post("/api/reminders/generate")
async def generate_reminder(req: ReminderRequest):
    # Retrieve optional API key from env variable
    openai_key = os.environ.get("OPENAI_API_KEY")
    gemini_key = os.environ.get("GEMINI_API_KEY")
    
    # Simple template-based message
    template_msg = (
        f"Hi {req.name},\n\n"
        f"This is a friendly reminder that you are currently registered for the course "
        f"'{req.course}', which had a compliance deadline of {req.deadline}.\n"
        f"Our records show this training is still pending completion. Please log in to your "
        f"learning portal and complete the course as soon as possible.\n\n"
        f"Best regards,\nLearning & Development Team"
    )
    
    # If a Gemini API Key is provided, use it to generate a personalized message
    if gemini_key:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_key}"
            prompt = (
                f"Write a polite, professional, and friendly reminder email to {req.name} regarding "
                f"their overdue training course '{req.course}' which was due on {req.deadline}. Keep it short (under 100 words)."
            )
            payload = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }]
            }
            async with httpx.AsyncClient() as client:
                res = await client.post(url, json=payload, timeout=5.0)
                if res.status_code == 200:
                    data = res.json()
                    ai_msg = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                    return {"msg": ai_msg, "generated_by": "Gemini AI"}
        except Exception:
            # Fall back to template on failure
            pass
            
    # If an OpenAI API Key is provided, use it to generate a message
    elif openai_key:
        try:
            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {openai_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": "You are a helpful L&D compliance assistant. Keep reminders short, polite, and professional."},
                    {"role": "user", "content": f"Generate a polite reminder email to {req.name} for their overdue '{req.course}' course (due {req.deadline}). Max 4 sentences."}
                ]
            }
            async with httpx.AsyncClient() as client:
                res = await client.post(url, headers=headers, json=payload, timeout=5.0)
                if res.status_code == 200:
                    data = res.json()
                    ai_msg = data["choices"][0]["message"]["content"].strip()
                    return {"msg": ai_msg, "generated_by": "OpenAI Chat Completion"}
        except Exception:
            # Fall back to template on failure
            pass

    # Default template response
    return {"msg": template_msg, "generated_by": "Local System Template"}

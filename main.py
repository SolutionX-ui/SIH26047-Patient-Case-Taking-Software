# for handling mongodb data and convert to string

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

app = FastAPI(title="SIH26047 Medical Triage API")

# Allow your frontend to talk to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 1. SCHEMAS (Data Structures) ---

class ChatTranscript(BaseModel):
    role: str
    message: str

class AIDraft(BaseModel):
    primary_symptoms: List[str]
    duration: str
    current_medications: List[str]

class DoctorPrescription(BaseModel):
    medication: str
    dosage: str
    frequency: str

class DoctorSection(BaseModel):
    clinical_diagnosis: str
    prescriptions: List[DoctorPrescription]
    lifestyle_suggestions: str

class ReportSubmission(BaseModel):
    patient_id: str
    chat_transcript: List[ChatTranscript]

# --- 2. IN-MEMORY DATABASE (For Hackathon Demo) ---
# We will store our reports here instead of a real database
database = {}

# --- 3. ENDPOINTS ---

@app.post("/api/patient/submit-chat")
async def process_chat_and_create_draft(submission: ReportSubmission):
    """
    Patient Side: Submits the chat. The AI generates a draft and sets status to PENDING_REVIEW.
    """
    
    # ⚠️ HACKATHON SHORTCUT: We are mocking the AI response here. 
    # In the final version, this is where you pass the chat to Gemini/OpenAI.
    mock_ai_draft = AIDraft(
        primary_symptoms=["headache", "mild nausea"],
        duration="3 days",
        current_medications=["None"]
    )
    
    # Create the database record
    report_id = f"report_{len(database) + 1}"
    database[report_id] = {
        "report_id": report_id,
        "patient_id": submission.patient_id,
        "status": "PENDING_REVIEW",
        "created_at": datetime.now().isoformat(),
        "chat_transcript": [chat.dict() for chat in submission.chat_transcript],
        "ai_draft": mock_ai_draft.dict(),
        "doctor_section": None
    }
    
    return {"message": "Draft created and sent to doctor.", "report": database[report_id]}


@app.get("/api/doctor/pending-reports")
async def get_pending_reports():
    """
    Doctor Side: Fetches all reports waiting for the doctor's review.
    """
    pending = [report for report in database.values() if report["status"] == "PENDING_REVIEW"]
    return {"pending_reports": pending}


@app.post("/api/doctor/finalize/{report_id}")
async def finalize_report(report_id: str, doctor_section: DoctorSection):
    """
    Doctor Side: Doctor submits their diagnosis and prescriptions.
    """
    if report_id not in database:
        raise HTTPException(status_code=404, detail="Report not found")
        
    # Update the report
    database[report_id]["doctor_section"] = doctor_section.dict()
    database[report_id]["status"] = "FINALIZED"
    database[report_id]["finalized_at"] = datetime.now().isoformat()
    
    return {"message": "Report finalized!", "report": database[report_id]}

#
# models.py
from pydantic import BaseModel, Field
from typing import List

# 1. This tells the LLM how to format the JSON
class AIDraft(BaseModel):
    primary_symptoms: List[str] = Field(description="List of main symptoms mentioned")
    duration: str = Field(description="How long the symptoms have been present")
    current_medications: List[str] = Field(description="Medications the patient is currently taking")
    allergies: str = Field(description="Any allergies mentioned, or 'None mentioned'")
    patient_notes: str = Field(description="Any other relevant details from the patient")

# 2. This formats the incoming request from the frontend
class ChatMessage(BaseModel):
    role: str
    message: str
    time: str

class DraftRequest(BaseModel):
    patient_id: str
    chat_transcript: List[ChatMessage]

class FinalizeRequest(BaseModel):
    diagnosis: str
    prescriptions: List[dict]
    lifestyle_suggestions: str
    follow_up_required: bool
    follow_up_days: int | None = None
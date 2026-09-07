from datetime import datetime
from enum import Enum
from typing import Optional, List
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

# ===== ENUMS =====
class UserRole(str, Enum):
    PATIENT = "patient"
    DOCTOR = "doctor"

class TriageStatus(str, Enum):
    IN_PROGRESS = "in_progress"
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    FINALIZED = "finalized"

class MessageSender(str, Enum):
    PATIENT = "patient"
    AI = "ai"

# ===== MODELS =====
class Medication(BaseModel):
    medication_name: str
    dosage: str
    frequency: str
    duration: str
    instructions: Optional[str] = None

class Vitals(BaseModel):
    temperature_f: Optional[float] = None
    heart_rate_bpm: Optional[int] = None
    blood_pressure: Optional[str] = None
    oxygen_saturation: Optional[int] = Field(default=None, ge=0, le=100)

class PatientProfile(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    patient_code: str  # Example: PT-20481
    full_name: str
    email: str
    phone: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    allergies: List[str] = []
    current_medications: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    model_config = ConfigDict(from_attributes=True)

class DoctorProfile(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    full_name: str
    email: str
    license_number: str
    specialization: Optional[str] = None
    qualifications: Optional[str] = None
    clinic_name: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class TriageMessage(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    sender: MessageSender
    message: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class TriageDraft(BaseModel):
    primary_symptoms: List[str]
    duration: Optional[str] = None
    current_medications: List[str] = []
    allergies: List[str] = []
    vitals: Optional[Vitals] = None
    ai_summary: Optional[str] = None
    generated_at: datetime = Field(default_factory=datetime.utcnow)

class TriageSession(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    patient_id: UUID
    status: TriageStatus = TriageStatus.IN_PROGRESS
    messages: List[TriageMessage] = []
    draft: Optional[TriageDraft] = None
    started_at: datetime = Field(default_factory=datetime.utcnow)
    submitted_at: Optional[datetime] = None
    finalized_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

class ClinicalReview(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    triage_session_id: UUID
    doctor_id: UUID
    clinical_diagnosis: str
    prescriptions: List[Medication] = []
    lifestyle_suggestions: Optional[str] = None
    follow_up_required: bool = False
    follow_up_days: Optional[int] = Field(default=None, gt=0)
    reviewed_at: datetime = Field(default_factory=datetime.utcnow)
    finalized_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

class FinalizedReport(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    report_number: str  # Example: MF-20481
    patient_id: UUID
    doctor_id: UUID
    triage_session_id: UUID
    review: ClinicalReview
    status: TriageStatus = TriageStatus.FINALIZED
    pdf_url: Optional[str] = None
    sent_to_patient_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    model_config = ConfigDict(from_attributes=True)
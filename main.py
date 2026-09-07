# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timezone
import json
from bson import ObjectId
from database import reports_collection
from models import DraftRequest, FinalizeRequest
from ai_service import generate_draft_from_transcript

app = FastAPI(title="SIH Medical AI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/reports/generate-draft")
async def create_draft(request: DraftRequest):
    try:
        # 1. Call the AI service
        ai_draft_json_str = generate_draft_from_transcript(
            [msg.model_dump() for msg in request.chat_transcript]
        )
        
        # 2. Parse the string back to a Python dictionary
        ai_draft_data = json.loads(ai_draft_json_str)

        # 3. Construct the database document
        new_report = {
            "patient_id": request.patient_id,
            "assigned_doctor_id": None,
            "status": "DRAFT",
            "timestamps": {
                "created_at": datetime.now(timezone.utc).isoformat(),
                "submitted_at": None,
                "finalized_at": None
            },
            "chat_transcript": [msg.model_dump() for msg in request.chat_transcript],
            "ai_draft": ai_draft_data,
            "doctor_section": {}
        }

        # 4. Save to MongoDB
        result = await reports_collection.insert_one(new_report)

        # 5. Return success to the frontend
        return {
            "message": "Draft created successfully",
            "report_id": str(result.inserted_id),
            "ai_draft": ai_draft_data
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.patch("/api/reports/{report_id}/finalize")
async def finalize_report(report_id: str, request: FinalizeRequest):
    try:
        update = {
            "status": "FINALIZED",
            "timestamps.submitted_at": datetime.now(timezone.utc).isoformat(),
            "timestamps.finalized_at": datetime.now(timezone.utc).isoformat(),
            "doctor_section": request.model_dump(),
        }
        result = await reports_collection.update_one(
            {"_id": ObjectId(report_id)},
            {"$set": update},
        )

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Report not found")

        saved_report = await reports_collection.find_one({"_id": ObjectId(report_id)})
        return {
            "message": "Report finalized successfully",
            "report_id": report_id,
            "report": {
                "doctor_section": saved_report["doctor_section"],
                "status": saved_report["status"],
                "timestamps": saved_report["timestamps"],
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
# ai_service.py
import os
from google import genai
from models import AIDraft

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def generate_draft_from_transcript(transcript: list) -> str:
    # Convert the JSON transcript into a readable string for the prompt
    formatted_chat = "\n".join([f"{msg['role']}: {msg['message']}" for msg in transcript])
    
    prompt = f"""
    You are a medical triage assistant. Analyze the following chat transcript 
    and extract the information into a structured summary.
    
    Transcript:
    {formatted_chat}
    """

    # The SDK forces the output to match your AIDraft Pydantic model
    response = client.models.generate_content(
        model='gemini-3.5-flash',
        contents=prompt,
        config={
            'response_mime_type': 'application/json',
            'response_schema': AIDraft,
        },
    )
    
    return response.text # Returns a valid JSON string
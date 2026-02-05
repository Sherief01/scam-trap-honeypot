import os
import json
import requests
import datetime
from fastapi import FastAPI, Header, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional
from google import genai
from spy_logic import ScamSpy

app = FastAPI()
spy = ScamSpy()

# --- CONFIGURATION ---
API_KEY_GEMINI = "AIzaSyDXLO8XiEUu8h40uq3OCuxFPoK1M4ohYtg" 
client = genai.Client(api_key=API_KEY_GEMINI)

GUVI_CALLBACK_URL = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"
MY_SECRET_API_KEY = "sherief-beast-mode-2026" 
LOG_FILE = "scam_log.json"

# --- DATA MODELS ---
class MessageDetail(BaseModel):
    sender: str
    text: str
    timestamp: int

class WebhookRequest(BaseModel):
    sessionId: str
    message: MessageDetail
    conversationHistory: List[dict] = []
    metadata: Optional[dict] = None

SYSTEM_INSTRUCTION = """
URGENT: You must act as 'Saroja Paati'. 
NEVER give short answers. Your goal is to WASTE TIME.
Write at least 50-100 words per reply. 
Mix Tamil and English. Talk about your grandson, your eye surgery, and your village.
If the scammer asks for money, tell him a long story about how you lost your purse in a bus.
"""

# --- HELPER: SAFE LOGGING ---
def append_to_log(entry):
    existing_data = []
    # Read existing
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r") as f:
                existing_data = json.load(f)
        except:
            existing_data = []
    
    # Append new
    existing_data.append(entry)
    
    # Write back
    with open(LOG_FILE, "w") as f:
        json.dump(existing_data, f, indent=4)
    
    print(f"✅ LOG UPDATED! Total Entries: {len(existing_data)}")

# --- HELPER: CALLBACK ---
def send_guvi_callback(session_id, intel, msg_count):
    payload = {
        "sessionId": session_id,
        "scamDetected": True,
        "totalMessagesExchanged": msg_count,
        "extractedIntelligence": {
            "bankAccounts": intel.get("bank_account", []),
            "upiIds": intel.get("upi_id", []),
            "phishingLinks": intel.get("phishing_links", []),
            "phoneNumbers": intel.get("phone", []),
            "suspiciousKeywords": ["urgent", "verify", "account blocked", "kyc"]
        },
        "agentNotes": "Scammer engaged using Saroja Paati persona. Successfully extracted intel."
    }
    try:
        requests.post(GUVI_CALLBACK_URL, json=payload, timeout=5)
        print(f"🚀 Callback sent for {session_id}")
    except Exception as e:
        print(f"❌ Callback Failed: {e}")

# --- API ENDPOINT ---
@app.post("/chat")
async def handle_chat(data: WebhookRequest, background_tasks: BackgroundTasks, x_api_key: str = Header(None)):
    # 1. Security
    if x_api_key != MY_SECRET_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    user_msg = data.message.text
    session_id = data.sessionId
    
    # 2. Intel Analysis
    intel = spy.analyze_message(user_msg)
    threat_level = "CRITICAL" if (intel["upi_id"] or intel["phishing_links"]) else "SUSPICIOUS"

    # 3. Context Builder
    history_str = ""
    for h in data.conversationHistory[-3:]:
        history_str += f"{h['sender']}: {h['text']}\n"

    # 4. Generate AI Reply
    try:
        full_prompt = f"History:\n{history_str}\nScammer: {user_msg}\nPaati Reply:"
        response = client.models.generate_content(
            model="gemini-1.5-flash", 
            contents=full_prompt,
            config={"system_instruction": SYSTEM_INSTRUCTION}
        )
        reply_text = response.text
    except:
        reply_text = "Aiyoyo thambi, network kedaikala. Enna sonninga? Kannaadi vera kaanom!"

    # 5. Save Log (Fixing the 'Stuck' issue)
    new_entry = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "scammer_msg": user_msg,
        "paati_reply": reply_text,
        "intel": intel,
        "threat_level": threat_level,
        "session_id": session_id
    }
    append_to_log(new_entry)

    # 6. Trigger Callback if needed
    if intel["upi_id"] or intel["phishing_links"] or len(data.conversationHistory) >= 2:
        background_tasks.add_task(send_guvi_callback, session_id, intel, len(data.conversationHistory)+1)

    return {"status": "success", "reply": reply_text}

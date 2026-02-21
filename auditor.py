import sqlite3
import requests
import os
import base64
import time

# =============================
# PATH CONFIG
# =============================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")
IMAGE_DIR = os.path.join(BASE_DIR, "static", "captures")

# =============================
# AI CONFIG (QWEN3-VL)
# =============================
OLLAMA_GEN_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen3-vl:2b-instruct-q4_K_M"

def encode_image_to_base64(image_path):
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        print(f"[AI AUDITOR] ❌ Image error: {e}")
        return None

def process_pending_events():
    """Analisa eventos PENDING e desliga o modelo após o uso."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM events WHERE status = 'PENDING'")
        pending_events = cursor.fetchall()

        if not pending_events:
            conn.close()
            return

        print(f"\n[AI AUDITOR] 🔍 Found {len(pending_events)} pending events...")

        for event in pending_events:
            event_id = event['id']
            image_name = event['image_path']
            yolo_hint = event['event_type']
            full_path = os.path.join(IMAGE_DIR, image_name)

            if not os.path.exists(full_path):
                cursor.execute("UPDATE events SET status = 'IMG_NOT_FOUND' WHERE id = ?", (event_id,))
                conn.commit()
                continue

            img_b64 = encode_image_to_base64(full_path)
            
            # Improved Safety Auditor Prompt (Ignores home office background)
            prompt = (
                f"Context: YOLO detected '{yolo_hint}'. "
                "ACT AS A FLEET SAFETY AUDITOR. Ignore the background (office/home). "
                "Assume the person is a professional truck driver during a shift. "
                "1. Specifically describe what the driver is holding or doing with their hands. "
                "2. State the final verdict as 'Confirmed' or 'False Positive'. "
                "Be extremely concise (max 15 words)."
            )


            # O segredo: keep_alive: 0 desliga o modelo após a resposta
            payload = {
                "model": MODEL_NAME,
                "prompt": prompt,
                "images": [img_b64],
                "stream": False,
                "keep_alive": 0 
            }

            try:
                print(f"[AI AUDITOR] 🧠 Requesting {MODEL_NAME} for ID {event_id} (Auto-Off enabled)...")
                response = requests.post(OLLAMA_GEN_URL, json=payload, timeout=90)
                
                if response.status_code == 200:
                    ai_response = response.json().get("response", "").strip()
                    cursor.execute("UPDATE events SET ai_analysis = ?, status = 'AI_REVIEWED' WHERE id = ?", (ai_response, event_id))
                    conn.commit()
                    print(f"[AI AUDITOR] ✅ Done: {ai_response}")
                else:
                    print(f"[AI AUDITOR] ❌ API Error {response.status_code}")

            except Exception as e:
                print(f"[AI AUDITOR] ❌ Connection failed: {e}")

    finally:
        conn.close()
        print("[AI AUDITOR] 💤 Auditor finished. Model should be unloaded.")

if __name__ == "__main__":
    process_pending_events()
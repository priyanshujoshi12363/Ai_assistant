# main.py - COMPLETE PRODUCTION SERVER
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
import tempfile
import os
import wave
import asyncio
import time
import shutil
from pathlib import Path

from stt import speech_to_text
from ai import ask_ai
from tts import text_to_speech

TEMP_DIR = "temp_audio"
MAX_FILE_AGE = 3600  
os.makedirs(TEMP_DIR, exist_ok=True)

app = FastAPI(title="Voice Assistant API", version="1.0.0")

@app.get("/")
@app.get("/health")
async def health_check():
    """Main health check endpoint"""
    return {
        "status": "healthy",
        "service": "Voice Assistant",
        "timestamp": time.time(),
        "components": {
            "stt": await check_stt(),
            "tts": await check_tts(),
            "ai": await check_ai()
        }
    }

@app.get("/health/stt")
async def check_stt():
    """Check STT component health"""
    try:
        test_text = speech_to_text(None)  
        return {"status": "healthy", "component": "STT"}
    except Exception as e:
        return {"status": "unhealthy", "component": "STT", "error": str(e)}

@app.get("/health/tts")
async def check_tts():
    """Check TTS component health"""
    try:
        test_file = text_to_speech("test")
        if test_file and os.path.exists(test_file):
            os.remove(test_file) 
            return {"status": "healthy", "component": "TTS"}
        return {"status": "unhealthy", "component": "TTS"}
    except Exception as e:
        return {"status": "unhealthy", "component": "TTS", "error": str(e)}

@app.get("/health/ai")
async def check_ai():
    """Check AI/ML model health"""
    try:
        response = ask_ai("test")
        return {"status": "healthy", "component": "AI"}
    except Exception as e:
        return {"status": "unhealthy", "component": "AI", "error": str(e)}

@app.post("/chat")
async def chat(text: str):
    """Direct text chat with AI (no STT/TTS)"""
    try:
        response = ask_ai(text)
        return {
            "status": "success",
            "input": text,
            "response": response,
            "timestamp": time.time()
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )

def cleanup_old_files():
    """Delete old temporary files"""
    try:
        current_time = time.time()
        for file in Path(TEMP_DIR).glob("*"):
            if file.is_file():
                file_age = current_time - file.stat().st_mtime
                if file_age > MAX_FILE_AGE:
                    file.unlink()
                    print(f"🧹 Deleted old file: {file}")
        
        if os.path.exists("response.wav"):
            os.remove("response.wav")
    except Exception as e:
        print(f"⚠️ Cleanup error: {e}")
        
        
@app.websocket("/voice")
async def voice_assistant(websocket: WebSocket):
    await websocket.accept()
    client_id = id(websocket)

    print(f"🔌 ESP32 connected (ID: {client_id})")

    audio_data = bytearray()
    temp_files = []

    try:
        while True:
            try:
                message = await websocket.receive()
            except RuntimeError:
                # Happens if client disconnects
                print(f"⚠️ Client {client_id} disconnected unexpectedly")
                return

            if message["type"] == "websocket.disconnect":
                print(f"🔌 Client {client_id} disconnected")
                return

            if message.get("bytes"):
                chunk = message["bytes"]
                audio_data.extend(chunk)

                print(f"📦 Received {len(chunk)} bytes (total: {len(audio_data)})")

            if message.get("text") == "STOP":
                break

        # ---------- AUDIO PROCESSING ----------
        if len(audio_data) < 200:
            print("⚠️ Audio too small")
            try:
                await websocket.send_text("ERROR: Audio too small")
            except:
                pass
            return

        print(f"🎤 Processing {len(audio_data)} bytes")

        temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=".wav", dir=TEMP_DIR)
        temp_audio_path = temp_audio.name
        temp_audio.close()

        temp_files.append(temp_audio_path)

        with wave.open(temp_audio_path, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(16000)
            wf.writeframes(audio_data)

        # ---------- STT ----------
        print("🗣️ Running STT")
        text = speech_to_text(temp_audio_path)

        print(f"📝 User said: {text}")

        # ---------- AI ----------
        print("🧠 AI thinking")
        response = ask_ai(text)

        print(f"🤖 AI response: {response}")

        # ---------- TTS ----------
        print("🔊 Generating speech")
        audio_file = text_to_speech(response)

        if not audio_file or not os.path.exists(audio_file):
            raise Exception("TTS failed")

        temp_files.append(audio_file)

        # ---------- STREAM RESPONSE ----------
        print("📤 Streaming audio")

        bytes_sent = 0

        with open(audio_file, "rb") as f:
            f.seek(44)

            while True:
                chunk = f.read(4096)
                if not chunk:
                    break

                try:
                    await websocket.send_bytes(chunk)
                except:
                    print("⚠️ Client disconnected during audio streaming")
                    return

                bytes_sent += len(chunk)

                await asyncio.sleep(0.01)

        try:
            await websocket.send_bytes(b"END")
        except:
            pass

        print(f"✅ Sent {bytes_sent} bytes")

    except WebSocketDisconnect:
        print(f"🔌 ESP32 disconnected (ID: {client_id})")

    except Exception as e:
        print(f"❌ Error: {e}")

        try:
            await websocket.send_text(f"ERROR: {str(e)}")
        except:
            pass

    finally:
        print("🧹 Cleaning temp files")

        for file_path in temp_files:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except:
                pass

        cleanup_old_files()
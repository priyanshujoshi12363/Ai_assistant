from fastapi import FastAPI, WebSocket
import tempfile
import os

from stt import speech_to_text
from ai import ask_ai
from tts import text_to_speech

app = FastAPI()


@app.get("/")
async def health_check():
    return {"status": "ok", "message": "Voice assistant server running"}


@app.websocket("/voice")
async def voice_assistant(websocket: WebSocket):

    await websocket.accept()
    print("ESP32 connected")

    audio_data = b""

    try:

        while True:

            chunk = await websocket.receive_bytes()

            if chunk == b"STOP":
                break

            audio_data += chunk

        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
            f.write(audio_data)
            audio_path = f.name

        text = speech_to_text(audio_path)
        print("User:", text)

        os.remove(audio_path)

        response = ask_ai(text)
        print("AI:", response)

    
        audio_file = text_to_speech(response)

        with open(audio_file, "rb") as f:
            while True:
                chunk = f.read(1024)
                if not chunk:
                    break
                await websocket.send_bytes(chunk)

        await websocket.send_bytes(b"END")

        os.remove(audio_file)

    except Exception as e:
        print("Error:", e)

    finally:
        await websocket.close()
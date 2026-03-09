from fastapi import FastAPI, WebSocket
import tempfile
import os
import wave
import asyncio

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

            message = await websocket.receive()

            if "bytes" in message:
                audio_data += message["bytes"]

            elif "text" in message:
                if message["text"] == "STOP":
                    break

        print("Audio size:", len(audio_data))

        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
            audio_path = f.name

        with wave.open(audio_path, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(16000)
            wf.writeframes(audio_data)

        text = speech_to_text(audio_path)

        print("User:", text)

        os.remove(audio_path)

        response = ask_ai(text)

        print("AI:", response)

        audio_file = text_to_speech(response)

        with open(audio_file, "rb") as f:

            while True:

                chunk = f.read(4096)

                if not chunk:
                    break

                await websocket.send_bytes(chunk)

                await asyncio.sleep(0.01)

        await websocket.send_bytes(b"END")

        os.remove(audio_file)

    except Exception as e:

        print("Server error:", e)

    finally:

        await websocket.close()
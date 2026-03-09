from fastapi import FastAPI, WebSocket, WebSocketDisconnect
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

            # audio chunks
            if "bytes" in message:
                audio_data += message["bytes"]

            # stop signal
            elif "text" in message and message["text"] == "STOP":
                break

        print("Audio received:", len(audio_data), "bytes")

        if len(audio_data) < 100:
            print("Audio too small, ignoring")
            return

        # save PCM as wav
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

        if not text:
            await websocket.send_bytes(b"END")
            return

        response = ask_ai(text)

        print("AI:", response)

        audio_file = text_to_speech(response)

        # send PCM audio (skip WAV header)
        with open(audio_file, "rb") as f:

            f.seek(44)  # skip wav header

            while True:

                chunk = f.read(4096)

                if not chunk:
                    break

                print("Sending audio:", len(chunk))

                await websocket.send_bytes(chunk)

                await asyncio.sleep(0.005)

        await websocket.send_bytes(b"END")

        os.remove(audio_file)

    except WebSocketDisconnect:
        print("ESP32 disconnected")

    except Exception as e:
        print("Server error:", e)
from fastapi import FastAPI, WebSocket
import tempfile

from stt import speech_to_text
from ai import ask_ai
from tts import text_to_speech

app = FastAPI()

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

        # save recorded audio
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
            f.write(audio_data)
            audio_path = f.name

        # speech → text
        text = speech_to_text(audio_path)

        print("User:", text)

        # AI response
        response = ask_ai(text)

        print("AI:", response)

        # text → speech
        audio_file = text_to_speech(response)

        # send audio to ESP32
        with open(audio_file, "rb") as f:

            while True:

                chunk = f.read(1024)

                if not chunk:
                    break

                await websocket.send_bytes(chunk)

        await websocket.send_bytes(b"END")

    except Exception as e:
        print(e)

    finally:
        await websocket.close()
# ESP32 AI Voice Assistant Backend

This project is a backend server for an **ESP32 AI voice assistant**.
It processes voice input, generates AI responses, and returns speech audio.

The system pipeline:

```
ESP32 Microphone
        ↓
Speech-to-Text (Whisper)
        ↓
AI Model (OpenRouter / Llama 3)
        ↓
Text-to-Speech (Piper)
        ↓
Audio Response
        ↓
ESP32 Speaker
```

---

# Features

* Speech recognition using Faster Whisper
* AI responses using OpenRouter (Llama 3)
* Text-to-speech using Piper TTS
* WebSocket communication with ESP32
* Automatic model download for STT and TTS

---

# Project Structure

```
voice_assistant
│
├── ai.py           # AI API integration
├── stt.py          # Speech-to-text module
├── tts.py          # Text-to-speech module
├── server.py       # FastAPI WebSocket server
├── requirements.txt
├── .gitignore
└── README.md
```

---

# Installation

Clone the repository:

```
git clone https://github.com/priyanshujoshi12363/Ai_assistant.git
cd voice_assistant
```

Create a virtual environment:

```
python -m venv venv
```

Activate it:

Windows:

```
venv\Scripts\activate
```

Linux / Mac:

```
source venv/bin/activate
```

Install dependencies:

```
pip install -r requirements.txt
```

---

# Environment Variables

Create a `.env` file:

```
OPENROUTER_API_KEY=your_api_key_here
```

Do not upload `.env` to GitHub.

---

# Run the Server

Start the backend server:

```
uvicorn server:app --host 0.0.0.0 --port 8000
```

WebSocket endpoint:

```
ws://localhost:8000/voice
```

---

# Deployment

The backend can be deployed on platforms like:

* Render
* Railway
* VPS

Render start command:

```
uvicorn server:app --host 0.0.0.0 --port 10000
```

---

# AI Pipeline

```
Audio Input
     ↓
Whisper STT
     ↓
AI Model
     ↓
Piper TTS
     ↓
Audio Output
```

---

# Technologies Used

* Python
* FastAPI
* Faster Whisper
* OpenRouter API
* Piper TTS
* WebSockets
* ESP-IDF (ESP32 firmware)

---

# Future Improvements

* Real-time streaming speech recognition
* Conversation memory
* Noise suppression
* Faster response latency
* Edge inference

---

# License

MIT License

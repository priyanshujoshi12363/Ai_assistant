import os
import requests
import subprocess

VOICE_DIR = "voices"

MODEL_PATH = os.path.join(VOICE_DIR, "en_US-lessac-medium.onnx")
CONFIG_PATH = os.path.join(VOICE_DIR, "en_US-lessac-medium.onnx.json")

MODEL_URL = "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx"
CONFIG_URL = "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json"


def download_voice():

    os.makedirs(VOICE_DIR, exist_ok=True)

    if not os.path.exists(MODEL_PATH):
        print("Downloading voice model...")
        r = requests.get(MODEL_URL)
        open(MODEL_PATH, "wb").write(r.content)

    if not os.path.exists(CONFIG_PATH):
        print("Downloading voice config...")
        r = requests.get(CONFIG_URL)
        open(CONFIG_PATH, "wb").write(r.content)


download_voice()


def text_to_speech(text):

    output_file = "response.wav"

    command = [
        "piper",
        "--model", MODEL_PATH,
        "--config", CONFIG_PATH,
        "--output_file", output_file
    ]

    process = subprocess.Popen(command, stdin=subprocess.PIPE)

    process.communicate(input=text.encode())

    return output_file
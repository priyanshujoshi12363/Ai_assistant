import os
import subprocess

VOICE_DIR = "voices"

MODEL_PATH = os.path.join(VOICE_DIR, "en_US-lessac-medium.onnx")
CONFIG_PATH = os.path.join(VOICE_DIR, "en_US-lessac-medium.onnx.json")


def text_to_speech(text):

    output_file = "response.wav"

    command = [
        "python",
        "-m",
        "piper",
        "--model", MODEL_PATH,
        "--config", CONFIG_PATH,
        "--output_file", output_file
    ]

    process = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    stdout, stderr = process.communicate(input=text.encode())

    if process.returncode != 0:
        raise RuntimeError(stderr.decode())

    return output_file

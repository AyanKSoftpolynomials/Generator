"""One Sarvam AI chat completion call. Run: python scripts/sarvam_hello.py"""
import os
import sys
from pathlib import Path

from sarvamai import SarvamAI

# Load .env from the project root (no python-dotenv dependency).
env_file = Path(__file__).resolve().parent.parent / ".env"
if env_file.exists():
    for line in env_file.read_text(encoding="utf-8").splitlines():
        key, sep, value = line.partition("=")
        if sep and not key.strip().startswith("#"):
            os.environ.setdefault(key.strip(), value.strip().strip("\"'"))

api_key = os.environ.get("SARVAM_API_KEY")
if not api_key:
    sys.exit("SARVAM_API_KEY is not set. Paste your key into .env first.")

client = SarvamAI(api_subscription_key=api_key)
response = client.chat.completions(
    model="sarvam-105b-conversations",
    messages=[{"role": "user", "content": "Say hello in Hindi and English, in one sentence."}],
)
print(response.choices[0].message.content)

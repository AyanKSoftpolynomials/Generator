"""Text-to-speech engines. XTTS v2 (Coqui, local) is the default; Sarvam AI
(hosted API, Indian languages) is selected with audio.engine = "sarvam".

The XTTS v2 model is licensed under the Coqui Public Model License
(non-commercial use). See README > Voice cloning.
"""

from __future__ import annotations

import base64
import io
import json
import logging
import os
import re
import shutil
import textwrap
import time
import warnings
from abc import ABC, abstractmethod
from pathlib import Path

from src.audio.speech_check import SpeechChecker
from src.audio.voice_manager import VoiceProfile
from src.utils.errors import LMSError

XTTS_MODEL = "tts_models/multilingual/multi-dataset/xtts_v2"
MAX_ATTEMPTS = 4       # tries per clip until the speech matches the text

# Languages XTTS v2 can speak.
XTTS_LANGUAGES = {"en", "es", "fr", "de", "it", "pt", "pl", "tr", "ru", "nl", "cs", "ar", "zh-cn", "ja", "hu", "ko", "hi"}

# Languages Sarvam Bulbul can speak (sent as <code>-IN) and the sample rate requested.
SARVAM_LANGUAGES = {"bn", "en", "gu", "hi", "kn", "ml", "mr", "od", "pa", "ta", "te"}
SARVAM_SAMPLE_RATE = 24000
SARVAM_ATTEMPTS = 8    # tries per request while the API answers "rate limit exceeded"


class TTSEngine(ABC):
    """Turns text into speech in a given voice."""

    name: str

    @abstractmethod
    def synthesize(self, text: str, voice: VoiceProfile, language: str, out_path: Path) -> None:
        """Write speech for ``text`` to ``out_path`` (WAV)."""

    def fingerprint(self) -> str:
        """Settings that change the sound; part of the audio cache key."""
        return self.name

    def voice_fingerprint(self, voice_id: str) -> str:
        """``fingerprint()`` for one library voice (engines whose settings differ per voice)."""
        return self.fingerprint()

    @property
    def settings(self) -> dict:
        return {"engine": self.name, "fingerprint": self.fingerprint()}


class XTTSEngine(TTSEngine):
    """Coqui XTTS v2 voice cloning. Uses every reference sample of a voice."""

    name = "xtts_v2"

    def __init__(self, device: str = "cpu"):
        self.device = device
        self._tts = None
        self._checker = SpeechChecker(device)      # Whisper model loads on the first clip
        self.last_check: dict | None = None

    def _model(self):
        if self._tts is None:
            # The user accepted the CPML licence during setup; skip the interactive prompt.
            os.environ.setdefault("COQUI_TOS_AGREED", "1")
            # Keep the generator's progress output readable.
            logging.getLogger("TTS").setLevel(logging.WARNING)
            warnings.filterwarnings("ignore", category=UserWarning, module="torchaudio")
            warnings.filterwarnings("ignore", category=FutureWarning)
            try:
                from TTS.api import TTS
            except ImportError as exc:
                raise LMSError(
                    "The XTTS text-to-speech package (coqui-tts) is not installed.",
                    "Run: python scripts/setup.py",
                ) from exc
            self._tts = TTS(XTTS_MODEL).to(self.device)
        return self._tts

    @property
    def builtin_speakers(self) -> list[str]:
        """Synthetic studio speakers shipped with the model (used for test voices)."""
        return list(self._model().speakers or [])

    def synthesize(self, text: str, voice: VoiceProfile, language: str, out_path: Path) -> None:
        """Speak ``text`` and check the result against it (src/audio/speech_check.py).

        XTTS sometimes adds or garbles words, so a clip that does not match its
        text is generated again (the model is random: a retry usually comes out
        right), up to MAX_ATTEMPTS times; the closest attempt is kept.
        ``last_check`` describes the clip that was kept (None: not checked).
        """
        if language not in XTTS_LANGUAGES:
            raise LMSError(f"XTTS v2 cannot speak language '{language}'.", f"Supported: {', '.join(sorted(XTTS_LANGUAGES))}")
        out_path = Path(out_path)
        spare = out_path.with_name(out_path.name + ".best")     # closest attempt so far
        best = None
        try:
            for attempt in range(1, MAX_ATTEMPTS + 1):
                self._model().tts_to_file(
                    text=text,
                    speaker_wav=[str(s) for s in voice.samples],
                    language=language,
                    file_path=str(out_path),
                )
                check = self._checker.check(out_path, text, language)
                if check is None:
                    break
                check["attempts"] = attempt
                if best is None or check["errors"] < best["errors"]:
                    best = check
                    if not check["ok"]:
                        shutil.copy2(out_path, spare)
                if check["ok"]:
                    break
            if best is not None and not best["ok"]:
                best["attempts"] = MAX_ATTEMPTS
                shutil.copy2(spare, out_path)
        finally:
            spare.unlink(missing_ok=True)
        self.last_check = best

    def synthesize_builtin(self, text: str, speaker: str, language: str, out_path: Path) -> None:
        """Speak with one of the model's built-in synthetic speakers."""
        self._model().tts_to_file(text=text, speaker=speaker, language=language, file_path=str(out_path))

    def fingerprint(self) -> str:
        # Read the version from package metadata: importing TTS itself takes
        # ~7 s, which a fully cached run should never pay.
        from importlib.metadata import version

        # "checked-v1": clips are verified against their text; older, unverified clips are not reused.
        return f"{self.name}:{XTTS_MODEL}:coqui-tts-{version('coqui-tts')}:checked-v1"

    @property
    def settings(self) -> dict:
        """Everything about generation that changes the sound (recorded in audio/*.meta.json)."""
        return {"engine": self.name, "model": XTTS_MODEL, "fingerprint": self.fingerprint()}


class SarvamEngine(TTSEngine):
    """Sarvam AI Bulbul (hosted API; needs SARVAM_API_KEY in the environment or .env).

    Stock speakers, no cloning: a library voice maps to a Sarvam speaker in
    settings.json > audio.sarvam.voices; unmapped voices use audio.sarvam.speaker.
    """

    name = "sarvam"

    def __init__(self, config: dict | None = None):
        if config is None:
            from src.config.settings import load_settings

            config = load_settings()["audio"]["sarvam"]
        self.config = config
        self._client = None
        self.last_check = None      # clips are not checked against their text (XTTS only)

    def _api(self):
        if self._client is None:
            try:
                from sarvamai import SarvamAI
            except ImportError as exc:
                raise LMSError("The Sarvam AI package (sarvamai) is not installed.", "Run: pip install sarvamai") from exc
            self._client = SarvamAI(api_subscription_key=_sarvam_key())
        return self._client

    def speaker(self, voice_id: str) -> str:
        return self.config.get("voices", {}).get(voice_id) or self.config["speaker"]

    def synthesize(self, text: str, voice: VoiceProfile, language: str, out_path: Path) -> None:
        import numpy as np
        import soundfile as sf
        from sarvamai.core.api_error import ApiError

        if language.split("-")[0] not in SARVAM_LANGUAGES:
            raise LMSError(f"Sarvam cannot speak language '{language}'.", f"Supported: {', '.join(sorted(SARVAM_LANGUAGES))}")
        model = self.config["model"]
        parts, rate = [], SARVAM_SAMPLE_RATE
        # Longer narrations are sent sentence by sentence (API limit per request) and joined.
        for chunk in split_text(text, 1500 if model == "bulbul:v2" else 2500):
            for attempt in range(1, SARVAM_ATTEMPTS + 1):
                try:
                    reply = self._api().text_to_speech.convert(
                        text=chunk, language_code=f"{language.split('-')[0]}-IN", speaker=self.speaker(voice.id),
                        model=model, pace=float(self.config.get("pace", 1.0)),
                        speech_sample_rate=SARVAM_SAMPLE_RATE, output_audio_codec="wav",
                    )
                    break
                except ApiError as exc:
                    # Rate limit (several videos generating at once): wait and ask again.
                    if exc.status_code == 429 and attempt < SARVAM_ATTEMPTS:
                        time.sleep(5 * attempt)
                        continue
                    raise LMSError(
                        f"Sarvam text-to-speech failed ({exc.status_code}): {exc.body}",
                        "Check the speaker and model in settings.json > audio.sarvam, and your Sarvam credits.",
                    ) from exc
            for audio in reply.audios:
                data, rate = sf.read(io.BytesIO(base64.b64decode(audio)))
                parts.append(data)
        sf.write(str(out_path), np.concatenate(parts), rate)

    def fingerprint(self) -> str:
        return f"{self.name}:{SARVAM_SAMPLE_RATE}:{json.dumps(self.config, sort_keys=True)}"

    def voice_fingerprint(self, voice_id: str) -> str:
        # Only this voice's speaker counts, so mapping one voice never invalidates another's clips.
        config = {**self.config, "speaker": self.speaker(voice_id), "voices": {}}
        return f"{self.name}:{SARVAM_SAMPLE_RATE}:{json.dumps(config, sort_keys=True)}"

    @property
    def settings(self) -> dict:
        return {"engine": self.name, **self.config, "fingerprint": self.fingerprint()}


def _sarvam_key() -> str:
    """SARVAM_API_KEY from the environment, else from .env in the project root."""
    from src.config.video_config import PROJECT_ROOT

    key = os.environ.get("SARVAM_API_KEY", "")
    env_file = PROJECT_ROOT / ".env"
    if not key and env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            name, _, value = line.partition("=")
            if name.strip() == "SARVAM_API_KEY":
                key = value.strip().strip("\"'")
    if not key:
        raise LMSError("SARVAM_API_KEY is not set.", "Add SARVAM_API_KEY=<your key> to .env in the project root.")
    return key


def split_text(text: str, limit: int) -> list[str]:
    """``text`` in pieces of at most ``limit`` characters, broken between sentences where possible."""
    chunks, current = [], ""
    for sentence in re.split(r"(?<=[.!?।])\s+", text.strip()):
        for piece in textwrap.wrap(sentence, limit) if len(sentence) > limit else [sentence]:
            if current and len(current) + 1 + len(piece) > limit:
                chunks.append(current)
                current = piece
            else:
                current = f"{current} {piece}".strip()
    return chunks + [current] if current else chunks


def create_engine(name: str, device: str, settings: dict | None = None) -> TTSEngine:
    if name == "xtts_v2":
        return XTTSEngine(device)
    if name == "sarvam":
        return SarvamEngine(settings["audio"]["sarvam"] if settings else None)
    raise LMSError(f"Unknown TTS engine '{name}'.", 'Set audio.engine to "xtts_v2" or "sarvam" in settings.json.')


def engine_fingerprint(name: str, settings: dict | None = None, voice_id: str = "") -> str:
    """The configured engine's fingerprint for a voice (audio cache key) without loading a model."""
    if name == "xtts_v2":
        return XTTSEngine().fingerprint()
    if name == "sarvam":
        return SarvamEngine(settings["audio"]["sarvam"] if settings else None).voice_fingerprint(voice_id)
    return name

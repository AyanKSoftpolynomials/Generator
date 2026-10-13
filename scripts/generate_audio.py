"""Preview a lesson's narration without rendering video.

    python scripts/generate_audio.py lessons/whole_numbers

Same as ``generate_video.py <lesson> --audio-only``: one WAV per narration
block in lessons/<name>/audio/ plus audio/narration_track.wav.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.generate_video import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main([*sys.argv[1:], "--audio-only"]))

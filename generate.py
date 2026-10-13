"""Generate a lesson video. Shortcut for scripts/generate_video.py.

    python generate.py lessons/integers/animation.py            # preview
    python generate.py lessons/integers/animation.py --final    # Full HD
    python generate.py lessons/integers --dry-run               # a lesson folder works too

Run ``python generate.py --help`` for every option.
"""

import sys

from scripts.generate_video import main

if __name__ == "__main__":
    sys.exit(main())

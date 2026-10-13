"""Start the API: ``python -m backend`` (listens on 127.0.0.1 only).

    python -m backend --port 8765
"""

import argparse
import sys

for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, "reconfigure"):
        stream.reconfigure(encoding="utf-8", errors="replace")


def main() -> None:
    import uvicorn

    parser = argparse.ArgumentParser(description="LMS Video Generator API")
    parser.add_argument("--host", default="127.0.0.1",
                        help="interface to bind (default 127.0.0.1: this computer only; the API runs lesson code)")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    uvicorn.run("backend.app:app", host=args.host, port=args.port, log_level="warning")


if __name__ == "__main__":
    main()

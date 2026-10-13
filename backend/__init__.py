"""Web API around the existing video generator (used by the frontend/ app).

The API never renders anything itself: analysis uses the generator's own
narration extraction, and every generation job runs ``VideoGenerator`` —
the same engine as ``python generate.py`` — in a background process.
"""

# Line prefix for the JSON progress events a job process prints (see job_runner.py).
EVENT_PREFIX = "@@LMS "

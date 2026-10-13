"""``from lms_video_generator.core import LMSScene`` — alias of ``src.animation``.

Lessons pasted from other tools often use this import. ``LMSScene`` here is
the camera-capable narrated scene (``LMSMovingCameraScene``), because such
lessons commonly zoom with ``self.camera.frame``; without camera moves it
renders exactly like the plain ``LMSScene``.
"""

from src.animation import LMS3DScene, LMSMovingCameraScene, Narration
from src.animation import LMSScene as LMSPlainScene

LMSScene = LMSMovingCameraScene

__all__ = ["LMSScene", "LMS3DScene", "LMSMovingCameraScene", "LMSPlainScene", "Narration"]

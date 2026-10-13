"""Blender: optional 3D animation engine next to Manim.

Manim stays the default engine (2D maths and concepts). A lesson section can
be rendered by Blender instead, for things where 3D has real teaching value:
3D objects and diagrams, coordinate space, scientific models, simulations,
camera moves around a structure.

    from src.animation import LMSScene, BLENDER
    from src.blender import BlenderScene

    class Cube3D(BlenderScene):
        def construct(self, b, t): ...

    class MyLesson(LMSScene):
        def construct(self):
            self.scene_start("space", title="Points in space", engine=BLENDER)
            n = self.narrate("space_01", "A point in space needs three numbers...")
            self.blender(Cube3D, narration=n)

The generator renders every ``self.blender(...)`` clip headlessly
(``blender -b``, see render.py) and splices it into the video at its exact
frames; narration, WhisperX timing, subtitles, caching and the final FFmpeg
step are the same as for Manim.
"""

from src.blender.scene import BlenderScene, Timing

__all__ = ["BlenderScene", "Timing"]

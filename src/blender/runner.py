"""Runs INSIDE Blender (headless) to render one 3D clip of a lesson:

    blender -b --factory-startup --python src/blender/runner.py -- job.json

job.json (written by src/blender/render.py) names the lesson's animation.py,
the BlenderScene class, the clip's frames/fps/size, the narration word timings
and where to write the PNG frames.

animation.py is loaded as a normal module so its BlenderScene classes (and
module-level constants) are available. Its Manim parts cannot run in
Blender's own Python, so ``manim`` and the Manim-based ``src.*`` modules are
replaced by inert stand-ins while it loads; only ``construct(b, t)`` of the
chosen BlenderScene is executed.
"""

from __future__ import annotations

import importlib.abc
import importlib.machinery
import json
import sys
import time
import traceback
import types
from pathlib import Path


class _Inert:
    """Stand-in for anything Manim: accepts every call/attribute/operation and does nothing."""

    def __init__(self, *args, **kwargs):
        pass

    def __call__(self, *args, **kwargs):
        return _Inert()

    def __getattr__(self, name):
        if name.startswith("__") and name.endswith("__"):
            raise AttributeError(name)
        return _Inert()

    def __getitem__(self, key):
        return _Inert()

    def __setitem__(self, key, value):
        pass

    def __iter__(self):
        return iter(())

    def __len__(self):
        return 0

    def __bool__(self):
        return True

    def __str__(self):
        return ""

    __repr__ = __str__

    def __format__(self, spec):
        return ""

    def _op(self, *args):
        return _Inert()

    __add__ = __radd__ = __sub__ = __rsub__ = __mul__ = __rmul__ = __truediv__ = __rtruediv__ = _op
    __neg__ = __pos__ = __pow__ = __rpow__ = __matmul__ = __floordiv__ = __mod__ = _op
    __or__ = __ror__ = __and__ = __rand__ = _op


class _InertFinder(importlib.abc.MetaPathFinder, importlib.abc.Loader):
    """Serve inert modules for Manim and the Manim-based parts of this project."""

    def __init__(self, manim_names: list[str]):
        self.manim_names = manim_names

    @staticmethod
    def _inert(fullname: str) -> bool:
        top = fullname.split(".")[0]
        if top in ("manim", "manimlib", "moderngl", "pydub", "cairo"):
            return True
        return top == "src" and fullname != "src" and not fullname.startswith("src.blender")

    def find_spec(self, fullname, path, target=None):
        if self._inert(fullname):
            return importlib.machinery.ModuleSpec(fullname, self, is_package=True)
        return None

    def create_module(self, spec):
        module = types.ModuleType(spec.name)
        module.__path__ = []
        module.__getattr__ = lambda name: _Inert()
        if spec.name == "manim":
            for name in self.manim_names:
                setattr(module, name, _Inert())
            module.__all__ = list(self.manim_names)
        if spec.name == "src.animation":
            module.MANIM, module.BLENDER = "MANIM", "BLENDER"
        return module

    def exec_module(self, module):
        pass


def main(job_path: str) -> None:
    job = json.loads(Path(job_path).read_text(encoding="utf-8"))
    root = job["project_root"]
    if root not in sys.path:
        sys.path.insert(0, root)
    sys.meta_path.insert(0, _InertFinder(job["manim_names"]))

    import importlib.util

    import bpy

    from src.blender.scene import Timing
    from src.blender.toolkit import Toolkit, rgba

    spec = importlib.util.spec_from_file_location("lms_lesson_animation", job["animation"])
    lesson = importlib.util.module_from_spec(spec)
    sys.modules["lms_lesson_animation"] = lesson
    spec.loader.exec_module(lesson)
    scene_cls = getattr(lesson, job["scene_class"], None)
    if scene_cls is None or not isinstance(scene_cls, type):
        raise SystemExit(f"LMS-BLENDER-ERROR: animation.py has no BlenderScene class '{job['scene_class']}'")

    # Empty scene, our render settings.
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    fps, frames = job["fps"], job["frames"]
    scene.render.fps = int(round(fps))
    scene.render.fps_base = scene.render.fps / fps
    scene.frame_start, scene.frame_end = 1, frames
    scene.render.resolution_x, scene.render.resolution_y = job["width"], job["height"]
    scene.render.resolution_percentage = 100
    _set_engine(scene, job["engine"], job.get("samples", 16))
    scene.view_settings.view_transform = "Standard"          # colours as authored (no filmic tone mapping)
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.filepath = str(Path(job["frames_dir"]) / "frame_")

    b = Toolkit(fps, frames)
    instance = scene_cls()
    b.background(getattr(instance, "background", "#0E1726"))
    t = Timing(duration=frames / fps, fps=fps, frames=frames, narrations=job["narrations"], params=job["params"])
    instance.construct(b, t)

    if scene.camera is None:
        b.camera()
    if not any(o.type == "LIGHT" for o in scene.objects):
        b.default_lighting()
    for text in b._face_camera:                                 # labels stay readable while the camera moves
        c = text.constraints.new("TRACK_TO")
        c.target = scene.camera
        c.track_axis = "TRACK_Z"
        c.up_axis = "UP_Y"

    started = time.time()
    bpy.ops.render.render(animation=True)
    print(f"LMS-BLENDER-DONE {frames} frames in {time.time() - started:.1f}s", flush=True)


def _set_engine(scene, name: str, samples: int) -> None:
    wanted = {"EEVEE": ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE"), "CYCLES": ("CYCLES",),
              "WORKBENCH": ("BLENDER_WORKBENCH",)}.get(name.upper(), (name,))
    for identifier in wanted:
        try:
            scene.render.engine = identifier
            break
        except TypeError:
            continue
    if scene.render.engine.startswith("BLENDER_EEVEE"):
        scene.eevee.taa_render_samples = samples
    elif scene.render.engine == "CYCLES":
        scene.cycles.samples = samples
        scene.cycles.device = "CPU"


if __name__ == "__main__":
    try:
        main(sys.argv[sys.argv.index("--") + 1])
    except SystemExit:
        raise
    except BaseException:
        print("LMS-BLENDER-ERROR:\n" + traceback.format_exc(), flush=True)
        sys.exit(1)

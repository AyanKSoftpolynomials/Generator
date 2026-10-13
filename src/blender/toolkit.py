"""Reusable 3D building blocks for lessons (runs inside Blender only: imports bpy).

Every ``construct(self, b, t)`` of a ``BlenderScene`` receives a ``Toolkit`` as
``b``. Positions are (x, y, z) in Blender units (z is up); colours are
"#RRGGBB" strings (the theme's colours, e.g. from src/themes); all times are
SECONDS from the start of the clip (use ``t.word("...")`` to hit a spoken word).

Objects:     sphere cube cylinder cone torus plane text line arrow polyline
Diagrams:    axes  surface  function_curve  parametric_curve  point_label
Scene:       background  camera  look_at  light  default_lighting  material
Animation:   keyframe  move  rotate  grow_in  shrink_out  fade_in  fade_out
             appear  orbit  orbit_camera
"""

from __future__ import annotations

import math

import bpy
from mathutils import Vector

Vec3 = tuple[float, float, float]


def srgb_to_linear(c: float) -> float:
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def rgba(color: str | tuple, alpha: float = 1.0) -> tuple[float, float, float, float]:
    """"#RRGGBB" (as seen on screen) -> Blender's linear RGBA."""
    if isinstance(color, str):
        h = color.lstrip("#")
        r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
        return (srgb_to_linear(r), srgb_to_linear(g), srgb_to_linear(b), alpha)
    return (*color[:3], alpha)


class Toolkit:
    def __init__(self, fps: float, frames: int):
        self.fps = fps
        self.frames = frames
        self.scene = bpy.context.scene
        self._count = 0
        self._face_camera: list = []           # text objects kept turned towards the camera

    # ------------------------------------------------------------ helpers

    def frame(self, seconds: float) -> int:
        return 1 + int(round(max(0.0, seconds) * self.fps))

    def _name(self, kind: str) -> str:
        self._count += 1
        return f"{kind}_{self._count:03d}"

    def _finish(self, obj, color=None, material=None, emission: float = 0.0, name: str | None = None):
        obj.name = name or self._name(obj.name.split(".")[0].lower())
        if material is None and color is not None:
            material = self.material(color, emission=emission)
        if material is not None and hasattr(obj.data, "materials"):
            obj.data.materials.clear()
            obj.data.materials.append(material)
        return obj

    # ------------------------------------------------------------ materials

    def material(self, color: str = "#FFFFFF", emission: float = 0.0, metallic: float = 0.0,
                 roughness: float = 0.45, alpha: float = 1.0, name: str | None = None):
        """Principled material. ``emission`` > 0 makes it glow (good for labels and highlights)."""
        mat = bpy.data.materials.new(name or self._name("mat"))
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        col = rgba(color)
        _set_input(bsdf, ("Base Color",), col)
        _set_input(bsdf, ("Metallic",), metallic)
        _set_input(bsdf, ("Roughness",), roughness)
        _set_input(bsdf, ("Alpha",), alpha)
        if emission > 0:
            _set_input(bsdf, ("Emission Color", "Emission"), col)
            _set_input(bsdf, ("Emission Strength",), emission)
        _allow_transparency(mat)
        return mat

    # ------------------------------------------------------------ primitives

    def sphere(self, radius: float = 0.5, location: Vec3 = (0, 0, 0), color: str | None = "#38BDF8",
               material=None, segments: int = 48, emission: float = 0.0, name: str | None = None):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, location=location, segments=segments,
                                             ring_count=max(8, segments // 2))
        bpy.ops.object.shade_smooth()
        return self._finish(bpy.context.object, color, material, emission, name)

    def cube(self, size: float = 1.0, location: Vec3 = (0, 0, 0), color: str | None = "#38BDF8",
             material=None, rotation: Vec3 = (0, 0, 0), emission: float = 0.0, name: str | None = None):
        bpy.ops.mesh.primitive_cube_add(size=size, location=location, rotation=_radians(rotation))
        return self._finish(bpy.context.object, color, material, emission, name)

    def cylinder(self, radius: float = 0.5, depth: float = 1.0, location: Vec3 = (0, 0, 0),
                 color: str | None = "#38BDF8", material=None, rotation: Vec3 = (0, 0, 0),
                 vertices: int = 48, emission: float = 0.0, name: str | None = None):
        bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, location=location,
                                            rotation=_radians(rotation), vertices=vertices)
        bpy.ops.object.shade_smooth()
        return self._finish(bpy.context.object, color, material, emission, name)

    def cone(self, radius: float = 0.5, depth: float = 1.0, location: Vec3 = (0, 0, 0),
             color: str | None = "#38BDF8", material=None, rotation: Vec3 = (0, 0, 0),
             emission: float = 0.0, name: str | None = None):
        bpy.ops.mesh.primitive_cone_add(radius1=radius, depth=depth, location=location,
                                        rotation=_radians(rotation), vertices=48)
        bpy.ops.object.shade_smooth()
        return self._finish(bpy.context.object, color, material, emission, name)

    def torus(self, major_radius: float = 1.0, minor_radius: float = 0.25, location: Vec3 = (0, 0, 0),
              color: str | None = "#38BDF8", material=None, rotation: Vec3 = (0, 0, 0), name: str | None = None):
        bpy.ops.mesh.primitive_torus_add(major_radius=major_radius, minor_radius=minor_radius,
                                         location=location, rotation=_radians(rotation))
        bpy.ops.object.shade_smooth()
        return self._finish(bpy.context.object, color, material, 0.0, name)

    def plane(self, size: float = 10.0, location: Vec3 = (0, 0, 0), color: str | None = "#111A2D",
              material=None, name: str | None = None):
        bpy.ops.mesh.primitive_plane_add(size=size, location=location)
        return self._finish(bpy.context.object, color, material, 0.0, name)

    def text(self, body: str, location: Vec3 = (0, 0, 0), size: float = 0.5, color: str = "#F5F7FA",
             extrude: float = 0.02, align: str = "CENTER", emission: float = 1.0, face_camera: bool = True,
             rotation: Vec3 = (90, 0, 0), name: str | None = None):
        """3D text. ``face_camera=True`` keeps it turned to the active camera (readable while orbiting)."""
        curve = bpy.data.curves.new(self._name("text"), type="FONT")
        curve.body = body
        curve.size = size
        curve.extrude = extrude
        curve.align_x = align
        curve.align_y = "CENTER"
        obj = bpy.data.objects.new(curve.name, curve)
        obj.location = location
        obj.rotation_euler = _radians(rotation)
        self.scene.collection.objects.link(obj)
        obj = self._finish(obj, color, None, emission, name)
        if face_camera:
            self._face_camera.append(obj)
        return obj

    # ------------------------------------------------------------ lines & arrows

    def line(self, start: Vec3, end: Vec3, thickness: float = 0.03, color: str = "#F5F7FA",
             emission: float = 0.0, name: str | None = None):
        """A straight rod from ``start`` to ``end``."""
        a, b = Vector(start), Vector(end)
        length = (b - a).length
        obj = self.cylinder(radius=thickness, depth=length, location=tuple((a + b) / 2), color=color,
                            vertices=16, emission=emission, name=name or self._name("line"))
        obj.rotation_mode = "QUATERNION"
        obj.rotation_quaternion = (b - a).to_track_quat("Z", "Y")
        return obj

    def arrow(self, start: Vec3, end: Vec3, thickness: float = 0.04, color: str = "#FFD166",
              head_length: float = 0.25, emission: float = 0.3, name: str | None = None):
        """Rod + cone head, pointing from ``start`` to ``end``. Returns the parent (empty) object."""
        a, b = Vector(start), Vector(end)
        direction = (b - a).normalized()
        shaft_end = b - direction * head_length
        root = bpy.data.objects.new(name or self._name("arrow"), None)
        self.scene.collection.objects.link(root)
        shaft = self.line(tuple(a), tuple(shaft_end), thickness, color, emission)
        head = self.cone(radius=thickness * 3, depth=head_length, location=tuple(shaft_end + direction * head_length / 2),
                         color=color, emission=emission)
        head.rotation_mode = "QUATERNION"
        head.rotation_quaternion = direction.to_track_quat("Z", "Y")
        for part in (shaft, head):
            part.parent = root
        return root

    def polyline(self, points: list[Vec3], thickness: float = 0.03, color: str = "#38BDF8",
                 emission: float = 0.5, name: str | None = None):
        """A smooth tube through ``points`` (graphs, orbits, paths). Draw it gradually with ``appear``/``grow_path``."""
        curve = bpy.data.curves.new(self._name("curve"), type="CURVE")
        curve.dimensions = "3D"
        curve.bevel_depth = thickness
        curve.bevel_resolution = 4
        spline = curve.splines.new("POLY")
        spline.points.add(len(points) - 1)
        for p, co in zip(spline.points, points):
            p.co = (*co, 1.0)
        obj = bpy.data.objects.new(curve.name, curve)
        self.scene.collection.objects.link(obj)
        return self._finish(obj, color, None, emission, name)

    # ------------------------------------------------------------ diagrams

    def axes(self, length: float = 4.0, thickness: float = 0.025, ticks: int = 4, labels: bool = True,
             colors: tuple[str, str, str] = ("#FF6B6B", "#51CF66", "#38BDF8"), negative: bool = True):
        """x (red), y (green), z (blue) axes with arrow heads, unit ticks and labels."""
        made = {}
        dirs = {"x": Vector((1, 0, 0)), "y": Vector((0, 1, 0)), "z": Vector((0, 0, 1))}
        for (axis, d), color in zip(dirs.items(), colors):
            start = -d * length if negative else Vector((0, 0, 0))
            arrow = self.arrow(tuple(start), tuple(d * (length + 0.3)), thickness, color, emission=0.4)
            parts = [arrow]
            for i in range(1, ticks + 1):
                step = length / ticks
                for sign in ((-1, 1) if negative else (1,)):
                    c = d * (i * step * sign)
                    tick = self.sphere(radius=thickness * 2.2, location=tuple(c), color=color, segments=12)
                    parts.append(tick)
            if labels:
                parts.append(self.text(axis, location=tuple(d * (length + 0.7)), size=0.45, color=color))
            made[axis] = parts
        return made

    def surface(self, f, x_range: tuple[float, float] = (-2, 2), y_range: tuple[float, float] = (-2, 2),
                resolution: int = 40, color: str = "#8B5CF6", alpha: float = 0.9, name: str | None = None):
        """Mesh of z = f(x, y) (e.g. a paraboloid for multivariable functions)."""
        verts, faces = [], []
        for i in range(resolution + 1):
            for j in range(resolution + 1):
                x = x_range[0] + (x_range[1] - x_range[0]) * i / resolution
                y = y_range[0] + (y_range[1] - y_range[0]) * j / resolution
                verts.append((x, y, f(x, y)))
        n = resolution + 1
        for i in range(resolution):
            for j in range(resolution):
                a = i * n + j
                faces.append((a, a + 1, a + n + 1, a + n))
        mesh = bpy.data.meshes.new(self._name("surface"))
        mesh.from_pydata(verts, [], faces)
        mesh.update()
        obj = bpy.data.objects.new(mesh.name, mesh)
        self.scene.collection.objects.link(obj)
        for poly in mesh.polygons:
            poly.use_smooth = True
        return self._finish(obj, None, self.material(color, alpha=alpha, roughness=0.35), 0.0, name)

    def function_curve(self, f, x_range: tuple[float, float] = (-3, 3), samples: int = 120, plane: str = "xz",
                       thickness: float = 0.03, color: str = "#38BDF8", name: str | None = None):
        """Graph of y = f(x) drawn in a plane of the 3D scene (default: the upright x-z plane)."""
        pts = []
        for i in range(samples + 1):
            x = x_range[0] + (x_range[1] - x_range[0]) * i / samples
            y = f(x)
            pts.append((x, 0, y) if plane == "xz" else (x, y, 0))
        return self.polyline(pts, thickness, color, name=name)

    def parametric_curve(self, fn, t_range: tuple[float, float] = (0, 2 * math.pi), samples: int = 200,
                         thickness: float = 0.03, color: str = "#38BDF8", name: str | None = None):
        """Curve through fn(s) -> (x, y, z) for s in t_range (helix, orbit, trajectory...)."""
        pts = [fn(t_range[0] + (t_range[1] - t_range[0]) * i / samples) for i in range(samples + 1)]
        return self.polyline(pts, thickness, color, name=name)

    def point_label(self, body: str, at: Vec3, offset: Vec3 = (0.45, 0, 0.6), size: float = 0.35,
                    color: str = "#F5F7FA"):
        """Small label next to a point."""
        return self.text(body, location=tuple(Vector(at) + Vector(offset)), size=size, color=color)

    # ------------------------------------------------------------ scene setup

    def background(self, color: str = "#0E1726", strength: float = 1.0):
        world = self.scene.world or bpy.data.worlds.new("World")
        self.scene.world = world
        world.use_nodes = True
        bg = world.node_tree.nodes.get("Background")
        bg.inputs[0].default_value = rgba(color)
        bg.inputs[1].default_value = strength

    def camera(self, location: Vec3 = (9, -9, 6), look_at: Vec3 = (0, 0, 0), lens: float = 35.0):
        """Create (or move) the active camera, aimed at ``look_at``."""
        cam = self.scene.camera
        if cam is None:
            data = bpy.data.cameras.new("Camera")
            cam = bpy.data.objects.new("Camera", data)
            self.scene.collection.objects.link(cam)
            self.scene.camera = cam
        cam.data.lens = lens
        cam.location = location
        self.look_at(cam, look_at)
        return cam

    def look_at(self, obj, target: Vec3 | object):
        """Keep ``obj`` (camera, light, text) pointed at a point or another object."""
        for c in [c for c in obj.constraints if c.type == "TRACK_TO"]:
            obj.constraints.remove(c)
        if isinstance(target, tuple) or isinstance(target, list):
            empty = bpy.data.objects.new(self._name("target"), None)
            empty.location = target
            self.scene.collection.objects.link(empty)
            target = empty
        c = obj.constraints.new("TRACK_TO")
        c.target = target
        c.track_axis = "TRACK_NEGATIVE_Z"
        c.up_axis = "UP_Y"
        return target

    def light(self, kind: str = "AREA", location: Vec3 = (4, -4, 8), energy: float = 800.0,
              color: str = "#FFFFFF", size: float = 5.0, look_at: Vec3 = (0, 0, 0)):
        data = bpy.data.lights.new(self._name("light"), type=kind)
        data.energy = energy
        data.color = rgba(color)[:3]
        if kind == "AREA":
            data.size = size
        obj = bpy.data.objects.new(data.name, data)
        obj.location = location
        self.scene.collection.objects.link(obj)
        if kind in ("AREA", "SPOT", "SUN"):
            self.look_at(obj, look_at)
        return obj

    def default_lighting(self):
        """Soft three-point lighting that suits dark educational backgrounds."""
        self.light("AREA", (6, -6, 8), 900, size=6)
        self.light("AREA", (-7, -3, 5), 350, color="#A5B4FC", size=6)
        self.light("AREA", (0, 8, 6), 450, color="#67E8F9", size=5)

    # ------------------------------------------------------------ animation (times in seconds)

    def keyframe(self, obj, at: float, location: Vec3 | None = None, rotation: Vec3 | None = None,
                 scale: Vec3 | float | None = None):
        """Set values at time ``at`` and keyframe them (Blender interpolates between keys)."""
        f = self.frame(at)
        if location is not None:
            obj.location = location
            obj.keyframe_insert("location", frame=f)
        if rotation is not None:
            obj.rotation_mode = "XYZ"
            obj.rotation_euler = _radians(rotation)
            obj.keyframe_insert("rotation_euler", frame=f)
        if scale is not None:
            obj.scale = (scale, scale, scale) if isinstance(scale, (int, float)) else scale
            obj.keyframe_insert("scale", frame=f)

    def move(self, obj, to: Vec3, start: float, duration: float = 1.0):
        self.keyframe(obj, start, location=tuple(obj.location))
        self.keyframe(obj, start + duration, location=to)

    def rotate(self, obj, by: Vec3, start: float, duration: float = 1.0):
        """Rotate by ``by`` degrees around x, y, z."""
        obj.rotation_mode = "XYZ"
        begin = tuple(math.degrees(a) for a in obj.rotation_euler)
        self.keyframe(obj, start, rotation=begin)
        self.keyframe(obj, start + duration, rotation=tuple(b + d for b, d in zip(begin, by)))

    def grow_in(self, obj, start: float, duration: float = 0.6):
        """Scale up from nothing (objects stay invisible until ``start``)."""
        final = tuple(obj.scale)
        self.keyframe(obj, 0, scale=(0, 0, 0))
        self.keyframe(obj, start, scale=(0, 0, 0))
        self.keyframe(obj, start + duration, scale=final)

    def shrink_out(self, obj, start: float, duration: float = 0.5):
        self.keyframe(obj, start, scale=tuple(obj.scale))
        self.keyframe(obj, start + duration, scale=(0, 0, 0))

    def appear(self, obj, at: float):
        """Hidden before ``at``, visible from then on (children included)."""
        for o in [obj, *obj.children_recursive]:
            o.hide_render = True
            o.keyframe_insert("hide_render", frame=1)
            o.hide_render = False
            o.keyframe_insert("hide_render", frame=self.frame(at))

    def fade_in(self, obj, start: float, duration: float = 0.6):
        self._fade(obj, start, duration, 0.0, 1.0)

    def fade_out(self, obj, start: float, duration: float = 0.6):
        self._fade(obj, start, duration, 1.0, 0.0)

    def _fade(self, obj, start: float, duration: float, a: float, b: float):
        for o in [obj, *obj.children_recursive]:
            for slot in getattr(o, "material_slots", []):
                mat = slot.material
                if not mat or not mat.use_nodes:
                    continue
                bsdf = mat.node_tree.nodes.get("Principled BSDF")
                alpha = bsdf.inputs.get("Alpha") if bsdf else None
                if alpha is None:
                    continue
                if mat.users > 1:               # own copy, so fading one object leaves the others alone
                    mat = mat.copy()
                    slot.material = mat
                    alpha = mat.node_tree.nodes.get("Principled BSDF").inputs["Alpha"]
                alpha.default_value = a
                alpha.keyframe_insert("default_value", frame=1)
                alpha.keyframe_insert("default_value", frame=self.frame(start))
                alpha.default_value = b
                alpha.keyframe_insert("default_value", frame=self.frame(start + duration))

    def orbit(self, obj, center: Vec3 = (0, 0, 0), radius: float = 3.0, start: float = 0.0,
              end: float | None = None, turns: float = 1.0, height: float = 0.0, start_angle: float = 0.0):
        """Move ``obj`` around ``center`` in a horizontal circle (planets, electrons...)."""
        end = self.frames / self.fps if end is None else end
        steps = max(8, int(abs(turns) * 48))
        for i in range(steps + 1):
            a = math.radians(start_angle) + 2 * math.pi * turns * i / steps
            self.keyframe(obj, start + (end - start) * i / steps,
                          location=(center[0] + radius * math.cos(a), center[1] + radius * math.sin(a), center[2] + height))
        _linear(obj)

    def orbit_camera(self, radius: float = 12.0, height: float = 6.0, start: float = 0.0, end: float | None = None,
                     start_angle: float = -45.0, end_angle: float = 45.0, look_at: Vec3 = (0, 0, 0)):
        """Swing the camera around the scene: the depth cue that makes 3D readable."""
        cam = self.camera(look_at=look_at)
        end = self.frames / self.fps if end is None else end
        steps = 24
        for i in range(steps + 1):
            a = math.radians(start_angle + (end_angle - start_angle) * i / steps)
            self.keyframe(cam, start + (end - start) * i / steps,
                          location=(radius * math.sin(a), -radius * math.cos(a), height))
        return cam


def _radians(deg: Vec3) -> tuple[float, float, float]:
    return tuple(math.radians(d) for d in deg)


def _set_input(node, names: tuple[str, ...], value) -> None:
    for name in names:
        socket = node.inputs.get(name)
        if socket is not None:
            socket.default_value = value
            return


def _allow_transparency(mat) -> None:
    # Blender 4.2+: surface_render_method; older: blend_method.
    if hasattr(mat, "surface_render_method"):
        mat.surface_render_method = "DITHERED"
    elif hasattr(mat, "blend_method"):
        mat.blend_method = "BLEND"


def _linear(obj) -> None:
    anim = obj.animation_data
    if anim and anim.action:
        for fcurve in _fcurves(anim.action):
            for kp in fcurve.keyframe_points:
                kp.interpolation = "LINEAR"


def _fcurves(action):
    # Blender 4.4+ "layered" actions keep F-curves in channelbags; older ones on the action.
    if hasattr(action, "fcurves") and len(action.fcurves):
        return list(action.fcurves)
    curves = []
    for layer in getattr(action, "layers", []):
        for strip in layer.strips:
            for bag in getattr(strip, "channelbags", []):
                curves.extend(bag.fcurves)
    return curves

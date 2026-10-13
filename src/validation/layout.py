"""Layout validation for Manim scenes: catches text overflowing its box, objects
leaving the frame, colliding text and unreadably small text, using the real
mobject geometry (bounding boxes of the actual glyphs and shapes).

It runs inside the scene process. ``LMSScene`` creates one validator per scene
(``self.validator``) and calls ``checkpoint()`` after every ``play()``/``wait()``
during the generator's extraction dry run, so problems are reported before any
audio is generated or any frame is rendered. Old lessons need no changes.

Automatic checks (every checkpoint, whole scene):

* text_overflow / text_too_large / tight_fit: a text whose centre lies in a box
  (Rectangle, RoundedRectangle, Square, Circle, Ellipse) is treated as that
  box's content and must fit inside it;
* frame_overflow / off_screen / safe_area: text (and other objects) must stay
  inside the camera frame, text also inside the safe margin;
* overlap: texts of different top-level objects must not collide (glyph level),
  boxes of different top-level objects must not partly cover each other;
* text_too_small: effective font size (after scaling and camera zoom).

Objects of the same top-level group (``VGroup(box, label)``) are one design
and never reported as colliding with each other.

Explicit checks (optional, from animation.py):

    card = RoundedRectangle(width=4, height=1.5)
    label = Text("A long explanation", font_size=36).move_to(card)
    self.validator.check_fit(label, card, margin=0.2)   # shrinks label if it must

Only ``check_fit`` changes anything, and only in the deterministic case: text
larger than its box is scaled down (never below ``min_font_size``) and moved
inside. It runs identically during extraction and rendering, so the rendered
video shows the fitted text. Everything else is reported, never guessed.
"""

from __future__ import annotations

import inspect
import sys
from dataclasses import asdict, dataclass, field

import numpy as np

ERROR, WARNING, INFO = "ERROR", "WARNING", "INFO"
SEVERITY_ORDER = {ERROR: 0, WARNING: 1, INFO: 2}

DEFAULT_CONFIG: dict = {
    "enabled": True,            # automatic checks during extraction
    "fail_on_error": False,     # True: stop generation (before TTS/render) when an ERROR is found
    "auto_fit": True,           # check_fit() may shrink/move text that does not fit its box
    "safe_margin": 0.25,        # scene units text should keep from the frame edge (frame: 14.2 x 8)
    "max_overflow": 0.05,       # how far (scene units) an edge may cross a boundary: touching is fine
    "min_font_size": 14,        # WARNING below this effective font size; auto-fit never goes below it
    "min_font_size_error": 10,  # ERROR below this
    "overlap_tolerance": 0.1,   # share of the smaller glyph/box that may overlap before it counts
    "max_fill": 0.97,           # text wider/taller than this share of its box: suspiciously large
    "min_padding": 0.04,        # gap to the box edge below which a fit is reported as tight (INFO)
}


@dataclass
class Issue:
    severity: str
    code: str
    message: str
    scene: str | None = None     # lesson section (scene_start id)
    time: float | None = None    # video seconds (estimated during extraction)
    line: int | None = None      # animation.py line of the play()/check call
    objects: list[str] = field(default_factory=list)
    boxes: dict = field(default_factory=dict)   # object -> [xmin, ymin, xmax, ymax]
    fix: str | None = None
    count: int = 1               # checkpoints at which the same problem was seen
    similar: int = 0             # more objects with the same problem at the same place (grouped)
    refs: tuple = ()             # ids of the objects (deduplication; not reported)

    def to_dict(self) -> dict:
        return {k: v for k, v in asdict(self).items()
                if v not in (None, [], {}) and k != "refs" and not (k == "similar" and v == 0)}


# ----------------------------------------------------------------- geometry

def _manim():
    import manim

    return manim


def is_text(mob) -> bool:
    m = _manim()
    return isinstance(mob, (m.Text, m.MarkupText, m.Paragraph, m.SingleStringMathTex, m.DecimalNumber))


def is_container(mob) -> bool:
    m = _manim()
    if isinstance(mob, (m.BackgroundRectangle, m.Dot)):
        return False
    return isinstance(mob, (m.Rectangle, m.Circle))


def is_round(mob) -> bool:
    return isinstance(mob, _manim().Circle)       # Circle and Ellipse


def bbox(mob) -> np.ndarray | None:
    points = mob.get_all_points()
    if len(points) == 0:
        return None
    lo, hi = points.min(axis=0), points.max(axis=0)
    return np.array([lo[0], lo[1], hi[0], hi[1]])


def visible(mob) -> bool:
    m = _manim()
    for part in mob.get_family():
        if isinstance(part, m.VMobject):
            if not part.has_points():
                continue
            if part.get_fill_opacity() > 0.01:
                return True
            if part.get_stroke_opacity() > 0.01 and part.get_stroke_width() > 0:
                return True
        elif isinstance(part, m.Mobject) and part.has_points() and not isinstance(part, m.Group):
            return True
    return False


def glyph_boxes(mob) -> np.ndarray:
    boxes = [bbox(p) for p in mob.family_members_with_points()]
    boxes = [b for b in boxes if b is not None and b[2] - b[0] > 1e-4 and b[3] - b[1] > 1e-4]
    return np.array(boxes) if boxes else np.zeros((0, 4))


def area(box) -> float:
    return max(0.0, box[2] - box[0]) * max(0.0, box[3] - box[1])


def intersection(a, b) -> float:
    return max(0.0, min(a[2], b[2]) - max(a[0], b[0])) * max(0.0, min(a[3], b[3]) - max(a[1], b[1]))


def overflow(inner, outer) -> dict[str, float]:
    """How far ``inner`` crosses each side of ``outer`` (only sides it crosses)."""
    sides = {"left": outer[0] - inner[0], "bottom": outer[1] - inner[1],
             "right": inner[2] - outer[2], "top": inner[3] - outer[3]}
    return {side: round(float(d), 3) for side, d in sides.items() if d > 0}


def ellipse_distance(points, outer) -> np.ndarray:
    """Distance of ``points`` from the centre of the ellipse inscribed in ``outer`` (1 = on its edge)."""
    cx, cy = (outer[0] + outer[2]) / 2, (outer[1] + outer[3]) / 2
    a, b = max((outer[2] - outer[0]) / 2, 1e-6), max((outer[3] - outer[1]) / 2, 1e-6)
    points = np.atleast_2d(points)
    return np.hypot((points[:, 0] - cx) / a, (points[:, 1] - cy) / b)


def round_overflow(mob, outer) -> float:
    """How far the outline of ``mob`` (its glyphs, not its bounding box) sticks out of a round box."""
    worst = float(ellipse_distance(mob.get_all_points(), outer).max())
    return max(0.0, (worst - 1) * min(outer[2] - outer[0], outer[3] - outer[1]) / 2)


def inside(point, box) -> bool:
    return box[0] <= point[0] <= box[2] and box[1] <= point[1] <= box[3]


def shrink(box, margin: float) -> np.ndarray:
    return np.array([box[0] + margin, box[1] + margin, box[2] - margin, box[3] - margin])


def font_size(mob) -> float | None:
    try:
        size = float(mob.font_size)
    except (AttributeError, ZeroDivisionError, TypeError, ValueError):
        return None                  # e.g. Paragraph: no font size to measure
    return size if np.isfinite(size) and size > 0 else None


def describe(mob) -> str:
    kind = type(mob).__name__
    text = getattr(mob, "original_text", None) or getattr(mob, "text", None) or getattr(mob, "tex_string", None)
    if text is None and hasattr(mob, "number"):
        text = str(mob.number)
    if text is None and kind == "Paragraph":
        text = " / ".join("".join(getattr(c, "text", "") for c in line.submobjects) for line in mob.submobjects)
        text = text if text.strip(" /") else None
    if text:
        text = " ".join(str(text).split())
        text = text if len(text) <= 48 else text[:45] + "..."
        return f'{kind} "{text}"'
    return kind


def _round_box(box) -> list[float]:
    return [round(float(v), 3) for v in box]


# ---------------------------------------------------------------- validator

class LayoutValidator:
    """Collects layout issues for one scene. See the module docstring."""

    def __init__(self, scene=None, config: dict | None = None, automatic: bool = True, record: bool = True):
        self.scene = scene
        self.config = {**DEFAULT_CONFIG, **(config or {})}
        self.automatic = automatic and bool(self.config["enabled"])
        self.record = record           # False while rendering: explicit fits still apply, nothing is logged
        self.issues: list[Issue] = []
        self._seen: dict[tuple, Issue] = {}
        self._fits: list[tuple] = []   # (text, container, margin) registered with check_fit
        self._ignored: set[int] = set()
        self._source = None
        self._scene_attrs = set(vars(scene)) if scene is not None else set()   # Manim's own attributes
        if scene is not None:
            try:
                self._source = inspect.getsourcefile(type(scene))
            except TypeError:
                self._source = None
        if self.automatic and scene is not None and isinstance(scene, _manim().ThreeDScene):
            self.automatic = False
            self._add(Issue(INFO, "skipped_3d", "3D scene: automatic layout checks are skipped (the camera "
                            "projects the geometry); explicit self.validator checks still run."))

    # -- explicit API ---------------------------------------------------------

    def check_fit(self, text, container, margin: float = 0.1, auto_fit: bool | None = None) -> bool:
        """``text`` must lie inside ``container`` with ``margin`` on every side.

        If it does not and auto-fit is on, it is scaled down (never below
        ``min_font_size``) and moved inside. Returns True when it fits
        (after fitting). The pair is re-checked at every later checkpoint.
        """
        auto_fit = self.config["auto_fit"] if auto_fit is None else auto_fit
        self._fits.append((text, container, float(margin)))
        line, frame = self._caller()
        inner = shrink(bbox(container), margin)
        box = bbox(text)
        if box is None or inner[2] <= inner[0] or inner[3] <= inner[1]:
            self._add(Issue(ERROR, "text_overflow", f"{describe(container)} is too small for a margin of {margin}.",
                            **self._objs(frame, container), line=line, **self._where()))
            return False
        over = overflow(box, inner)
        if not over or max(over.values()) <= self.config["max_overflow"]:
            return True
        if auto_fit:
            fitted = self._fit(text, box, inner)
            if fitted is not None:
                self._add(Issue(INFO, "auto_fit", f"{self._name(text, frame)} did not fit {self._name(container, frame)} "
                                f"(over by {self._sides(over)}); scaled to {fitted:.0%} and moved inside.",
                                **self._objs(frame, text, container), line=line,
                                boxes={"text": _round_box(bbox(text)), "container": _round_box(bbox(container))},
                                **self._where()))
                return True
        size = font_size(text)
        needed = min((inner[2] - inner[0]) / (box[2] - box[0]), (inner[3] - inner[1]) / (box[3] - box[1]))
        reason = (f"; fitting would need font size {size * needed:.0f}, below the readable minimum "
                  f"{self.config['min_font_size']}" if auto_fit and size else "")
        self._add(Issue(ERROR, "text_overflow",
                        f"{self._name(text, frame)} does not fit {self._name(container, frame)} "
                        f"(over by {self._sides(over)}){reason}.",
                        **self._objs(frame, text, container), line=line,
                        boxes={"text": _round_box(box), "container": _round_box(bbox(container))},
                        fix="Shorten the text, split it over two lines, or make the box bigger.", **self._where()))
        return False

    def check_in_frame(self, *mobs, margin: float | None = None) -> bool:
        """Every mobject inside the camera frame, ``margin`` (default: safe_margin) from the edge."""
        margin = self.config["safe_margin"] if margin is None else margin
        line, frame = self._caller()
        safe = shrink(self._frame_box(), margin)
        ok = True
        for mob in mobs:
            box = bbox(mob)
            over = overflow(box, safe) if box is not None else {}
            if over and max(over.values()) > self.config["max_overflow"]:
                ok = False
                self._add(Issue(ERROR, "frame_overflow", f"{self._name(mob, frame)} is outside the frame's safe "
                                f"area (margin {margin}) by {self._sides(over)}.", **self._objs(frame, mob),
                                line=line, boxes={"object": _round_box(box)}, **self._where()))
        return ok

    def check_no_overlap(self, *mobs, tolerance: float | None = None) -> bool:
        """No two of ``mobs`` overlap by more than ``tolerance`` of the smaller one's area."""
        tolerance = self.config["overlap_tolerance"] if tolerance is None else tolerance
        line, frame = self._caller()
        ok = True
        for i, a in enumerate(mobs):
            for b in mobs[i + 1:]:
                share = self._overlap_share(a, b)
                if share > tolerance:
                    ok = False
                    self._add(Issue(ERROR, "overlap", f"{self._name(a, frame)} and {self._name(b, frame)} "
                                    f"overlap ({share:.0%} of the smaller one).",
                                    **self._objs(frame, a, b), line=line,
                                    boxes={"a": _round_box(bbox(a)), "b": _round_box(bbox(b))}, **self._where()))
        return ok

    def check_spacing(self, a, b, min_gap: float = 0.0, max_gap: float | None = None) -> bool:
        """The empty space between ``a`` and ``b`` (bounding boxes) is within [min_gap, max_gap]."""
        line, frame = self._caller()
        ba, bb = bbox(a), bbox(b)
        dx = max(bb[0] - ba[2], ba[0] - bb[2], 0.0)
        dy = max(bb[1] - ba[3], ba[1] - bb[3], 0.0)
        gap = float(np.hypot(dx, dy))
        if gap + 1e-9 >= min_gap and (max_gap is None or gap <= max_gap + 1e-9):
            return True
        wanted = f"at least {min_gap}" if gap < min_gap else f"at most {max_gap}"
        self._add(Issue(ERROR, "spacing", f"Gap between {self._name(a, frame)} and {self._name(b, frame)} is "
                        f"{gap:.2f}, expected {wanted}.", **self._objs(frame, a, b),
                        line=line, boxes={"a": _round_box(ba), "b": _round_box(bb)}, **self._where()))
        return False

    def check_size(self, mob, max_width: float | None = None, max_height: float | None = None,
                   min_width: float | None = None, min_height: float | None = None) -> bool:
        """Width/height of ``mob`` within the given limits (scene units)."""
        line, frame = self._caller()
        box = bbox(mob)
        width, height = box[2] - box[0], box[3] - box[1]
        problems = [f"{label} {value:.2f} {cmp} {limit:.2f}" for label, value, cmp, limit, bad in (
            ("width", width, ">", max_width, max_width is not None and width > max_width + 1e-9),
            ("height", height, ">", max_height, max_height is not None and height > max_height + 1e-9),
            ("width", width, "<", min_width, min_width is not None and width < min_width - 1e-9),
            ("height", height, "<", min_height, min_height is not None and height < min_height - 1e-9)) if bad]
        if problems:
            self._add(Issue(ERROR, "size", f"{self._name(mob, frame)}: {', '.join(problems)}.",
                            **self._objs(frame, mob), line=line, boxes={"object": _round_box(box)},
                            **self._where()))
        return not problems

    def ignore(self, *mobs) -> None:
        """Leave these mobjects (and their parts) out of the automatic checks."""
        for mob in mobs:
            self._ignored.update(id(part) for part in mob.get_family())

    # -- automatic checks -----------------------------------------------------

    def checkpoint(self) -> None:
        """Check the whole scene as it looks now (called after every play/wait)."""
        if not self.record or self.scene is None:
            return
        _, frame = self._caller()
        for text, container, margin in self._fits:
            if self._on_screen(text) and self._on_screen(container):
                self._recheck_fit(text, container, margin, frame)
        if not self.automatic:
            return
        texts, containers, others = self._collect()
        self._check_containers(texts, containers, frame)
        self._check_frame(texts, others, frame)
        self._check_text_overlaps(texts, frame)
        self._check_box_overlaps(containers, frame)
        self._check_font_sizes(texts, frame)

    def _collect(self):
        """(text, top) and (box, top) pairs of what is visible now, plus visible top-level non-text objects."""
        texts, containers, others = [], [], []

        def walk(mob, top):
            if id(mob) in self._ignored or not visible(mob):
                return
            if is_text(mob):
                texts.append((mob, top))
                return                   # a text's glyphs are part of it, not separate texts
            if is_container(mob):
                containers.append((mob, top))
            for child in mob.submobjects:
                walk(child, top)

        for top in self.scene.mobjects:
            walk(top, top)
            if id(top) not in self._ignored and not is_text(top) and visible(top):
                others.append(top)
        return texts, containers, others

    def _check_containers(self, texts, containers, frame) -> None:
        explicit = {id(t) for t, _, _ in self._fits}
        for text, _ in texts:
            if id(text) in explicit:
                continue
            box = bbox(text)
            center = ((box[0] + box[2]) / 2, (box[1] + box[3]) / 2)
            candidates = []
            for shape, _ in containers:
                sbox = bbox(shape)
                if sbox is None or not inside(center, sbox) or area(sbox) < 0.5 * area(box):
                    continue                 # not this text's box (or too small to tell)
                if is_round(shape) and ellipse_distance(center, sbox)[0] > 0.5:
                    continue                 # a label on a circle's rim, not inside it
                candidates.append((area(sbox), shape, sbox))
            if not candidates:
                continue
            _, shape, sbox = min(candidates, key=lambda c: c[0])      # innermost box around the text
            self._judge_fit(text, box, shape, sbox, 0.0, frame, explicit=False)

    def _recheck_fit(self, text, container, margin, frame) -> None:
        self._judge_fit(text, bbox(text), container, bbox(container), margin, frame, explicit=True)

    def _judge_fit(self, text, box, shape, sbox, margin, frame, explicit: bool) -> None:
        cfg = self.config
        inner = shrink(sbox, margin)
        names = self._objs(frame, text, shape)
        boxes = {"text": _round_box(box), "container": _round_box(sbox)}
        if is_round(shape) and not explicit:
            amount = round_overflow(text, inner)
            over = {"edge": round(amount, 3)} if amount > 0 else {}
        else:
            over = overflow(box, inner)
        if over and max(over.values()) > cfg["max_overflow"]:
            self._add(Issue(ERROR, "text_overflow",
                            f"{self._name(text, frame)} overflows its box {self._name(shape, frame)} "
                            f"by {self._sides(over)}.", **names, boxes=boxes, line=self._line(frame),
                            fix=f"Make the box bigger, shorten the text, or let the generator fit it:\n"
                                f"    self.validator.check_fit({_variable_name(text, frame, self.scene, self._scene_attrs) or 'text'}, "
                                f"{_variable_name(shape, frame, self.scene, self._scene_attrs) or 'box'}, margin=0.2)",
                            **self._where()))
            return
        width_fill = (box[2] - box[0]) / max(sbox[2] - sbox[0], 1e-6)
        height_fill = (box[3] - box[1]) / max(sbox[3] - sbox[1], 1e-6)
        if max(width_fill, height_fill) > cfg["max_fill"] and not is_round(shape):
            self._add(Issue(WARNING, "text_too_large",
                            f"{self._name(text, frame)} fills {max(width_fill, height_fill):.0%} of its box "
                            f"{self._name(shape, frame)}: no breathing room.", **names, boxes=boxes,
                            line=self._line(frame), fix="Leave some padding: smaller font or a bigger box.",
                            **self._where()))
            return
        gap = min(box[0] - sbox[0], sbox[2] - box[2], box[1] - sbox[1], sbox[3] - box[3])
        if gap < cfg["min_padding"] and not is_round(shape):
            self._add(Issue(INFO, "tight_fit", f"{self._name(text, frame)} nearly touches the edge of "
                            f"{self._name(shape, frame)} (gap {max(gap, 0):.2f}).", **names, boxes=boxes,
                            line=self._line(frame), **self._where()))

    def _check_frame(self, texts, others, frame) -> None:
        cfg = self.config
        texts = _without_copies(texts)
        fbox = self._frame_box()
        moved = self._camera_moved()
        safe = shrink(fbox, cfg["safe_margin"])
        for text, _ in texts:
            box = bbox(text)
            over = overflow(box, fbox)
            names, boxes = self._objs(frame, text), {"object": _round_box(box), "frame": _round_box(fbox)}
            if over and max(over.values()) > cfg["max_overflow"]:
                if intersection(box, fbox) <= 0:
                    self._add(Issue(INFO, "off_screen", f"{self._name(text, frame)} is completely outside the "
                                    "camera frame (not visible).", **names, boxes=boxes,
                                    line=self._line(frame), **self._where()), group=("off_screen", self._line(frame)))
                else:
                    self._add(Issue(WARNING if moved else ERROR, "frame_overflow",
                                    f"{self._name(text, frame)} is cut off by the frame edge "
                                    f"({self._sides(over)} outside).", **names, boxes=boxes,
                                    line=self._line(frame), fix="Move or scale it inside the frame, e.g. "
                                    ".scale_to_fit_width(config.frame_width - 1) or .to_edge(...)", **self._where()))
                continue
            over = overflow(box, safe)
            if over and max(over.values()) > cfg["max_overflow"]:
                self._add(Issue(WARNING, "safe_area", f"{self._name(text, frame)} is within {cfg['safe_margin']} "
                                f"of the frame edge ({self._sides(over)} into the margin).", **names,
                                boxes=boxes, line=self._line(frame), **self._where()))
        fw, fh = fbox[2] - fbox[0], fbox[3] - fbox[1]
        for mob in others:
            box = bbox(mob)
            if box is None or box[2] - box[0] > fw + 1e-3 or box[3] - box[1] > fh + 1e-3:
                continue                    # backgrounds, planes: bigger than the frame by design
            over = overflow(box, fbox)
            if over and max(over.values()) > cfg["max_overflow"] and intersection(box, fbox) > 0:
                self._add(Issue(WARNING, "frame_overflow", f"{self._name(mob, frame)} is partly outside the "
                                f"frame ({self._sides(over)}).", **self._objs(frame, mob),
                                boxes={"object": _round_box(box), "frame": _round_box(fbox)},
                                line=self._line(frame), **self._where()))

    def _check_text_overlaps(self, texts, frame) -> None:
        tolerance = self.config["overlap_tolerance"]
        boxes = [bbox(t) for t, _ in texts]
        for i, (a, top_a) in enumerate(texts):
            for j in range(i + 1, len(texts)):
                b, top_b = texts[j]
                if top_a is top_b or intersection(boxes[i], boxes[j]) <= 0:
                    continue                 # same design group, or nowhere near each other
                share = self._overlap_share(a, b, copies_ok=True)
                if share > tolerance:
                    self._add(Issue(WARNING, "overlap", f"{self._name(a, frame)} and {self._name(b, frame)} "
                                    f"overlap ({share:.0%} of a letter covered).",
                                    **self._objs(frame, a, b),
                                    boxes={"a": _round_box(boxes[i]), "b": _round_box(boxes[j])},
                                    line=self._line(frame),
                                    fix="Move one of them, FadeOut the old text first, or group them on purpose.",
                                    **self._where()))

    def _check_box_overlaps(self, containers, frame) -> None:
        m = _manim()
        tolerance = self.config["overlap_tolerance"]
        rects = [(s, top, bbox(s)) for s, top in containers if isinstance(s, m.Rectangle)]
        for i, (a, top_a, ba) in enumerate(rects):
            for b, top_b, bb in rects[i + 1:]:
                if top_a is top_b:
                    continue
                shared = intersection(ba, bb)
                smaller = min(area(ba), area(bb))
                if smaller <= 0 or shared <= tolerance * smaller or shared >= (1 - tolerance) * smaller:
                    continue                 # apart, touching, or one inside the other
                self._add(Issue(INFO, "box_overlap", f"{self._name(a, frame)} and {self._name(b, frame)} partly "
                                f"cover each other ({shared / smaller:.0%}).",
                                **self._objs(frame, a, b),
                                boxes={"a": _round_box(ba), "b": _round_box(bb)}, line=self._line(frame),
                                **self._where()))

    def _check_font_sizes(self, texts, frame) -> None:
        cfg = self.config
        texts = _without_copies(texts)
        zoom = _manim().config.frame_width / max(self._frame_box()[2] - self._frame_box()[0], 1e-6)
        for text, _ in texts:
            size = font_size(text)
            if size is None:
                continue
            effective = size * zoom
            if effective < cfg["min_font_size_error"] - 0.05:
                severity = ERROR
            elif effective < cfg["min_font_size"] - 0.05:
                severity = WARNING
            else:
                continue
            self._add(Issue(severity, "text_too_small", f"{self._name(text, frame)} is shown at font size "
                            f"{effective:.1f} (readable minimum {cfg['min_font_size']}).",
                            **self._objs(frame, text), boxes={"object": _round_box(bbox(text))},
                            line=self._line(frame), fix="Use a bigger font_size or scale it up; abbreviate if space is short.",
                            **self._where()), group=("text_too_small", self._line(frame), round(effective, 1)))

    # -- helpers --------------------------------------------------------------

    def _fit(self, text, box, inner) -> float | None:
        """Scale ``text`` into ``inner`` and move it inside. None if that would make it unreadable."""
        factor = min(1.0, (inner[2] - inner[0]) / (box[2] - box[0]), (inner[3] - inner[1]) / (box[3] - box[1]))
        size = font_size(text)
        if size is not None and size * factor < self.config["min_font_size"] - 1e-6:
            return None
        if factor < 1.0:
            text.scale(factor)
        fitted = bbox(text)
        dx = max(inner[0] - fitted[0], 0) - max(fitted[2] - inner[2], 0)
        dy = max(inner[1] - fitted[1], 0) - max(fitted[3] - inner[3], 0)
        if dx or dy:
            text.shift(np.array([dx, dy, 0.0]))
        return factor

    def _overlap_share(self, a, b, copies_ok: bool = False) -> float:
        """Largest share of a glyph/part of ``a`` or ``b`` that the other one covers.

        ``copies_ok``: 0 when one text lies exactly on top of glyphs of the other
        (a glow, halo or shadow layer is a copy, not a collision)."""
        ga, gb = glyph_boxes(a), glyph_boxes(b)
        if not len(ga) or not len(gb):
            return 0.0
        w = np.clip(np.minimum(ga[:, None, 2], gb[None, :, 2]) - np.maximum(ga[:, None, 0], gb[None, :, 0]), 0, None)
        h = np.clip(np.minimum(ga[:, None, 3], gb[None, :, 3]) - np.maximum(ga[:, None, 1], gb[None, :, 1]), 0, None)
        shared = w * h
        area_a = (ga[:, 2] - ga[:, 0]) * (ga[:, 3] - ga[:, 1])
        area_b = (gb[:, 2] - gb[:, 0]) * (gb[:, 3] - gb[:, 1])
        if copies_ok:
            iou = shared / np.maximum(area_a[:, None] + area_b[None, :] - shared, 1e-12)
            if (iou.max(axis=1) > 0.8).all() or (iou.max(axis=0) > 0.8).all():
                return 0.0
        smaller = np.minimum(area_a[:, None], area_b[None, :])
        return float((shared / smaller).max())

    def _frame_box(self) -> np.ndarray:
        m = _manim()
        cam_frame = getattr(getattr(self.scene, "camera", None), "frame", None)
        if cam_frame is not None:
            cx, cy = cam_frame.get_center()[:2]
            w, h = cam_frame.width, cam_frame.height
        else:
            cx, cy, w, h = 0.0, 0.0, m.config.frame_width, m.config.frame_height
        return np.array([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2])

    def _camera_moved(self) -> bool:
        m = _manim()
        fbox = self._frame_box()
        return (abs((fbox[2] - fbox[0]) - m.config.frame_width) > 1e-3
                or abs(fbox[0] + fbox[2]) > 1e-3 or abs(fbox[1] + fbox[3]) > 1e-3)

    def _on_screen(self, mob) -> bool:
        return any(mob in top.get_family() for top in self.scene.mobjects)

    def _caller(self):
        """(line, frame) of the animation.py code that led here."""
        if self._source is None:
            return None, None
        frame = sys._getframe(1)
        while frame is not None:
            if frame.f_code.co_filename == self._source:
                return frame.f_lineno, frame
            frame = frame.f_back
        return None, None

    def _line(self, frame) -> int | None:
        return frame.f_lineno if frame is not None else None

    def _name(self, mob, frame) -> str:
        """Variable name in animation.py (when there is one) + what the object is."""
        name = _variable_name(mob, frame, self.scene, self._scene_attrs)
        return f"{name} ({describe(mob)})" if name else describe(mob)

    def _objs(self, frame, *mobs) -> dict:
        return {"objects": [self._name(m, frame) for m in mobs], "refs": tuple(id(m) for m in mobs)}

    @staticmethod
    def _sides(over: dict) -> str:
        return ", ".join(f"{amount:.2f} {side}" for side, amount in over.items())

    def _where(self) -> dict:
        scene = self.scene
        return {"scene": getattr(scene, "_scene_id", None),
                "time": round(float(scene.now), 2) if hasattr(scene, "now") else None}

    def _add(self, issue: Issue, group: tuple | None = None) -> None:
        """Record ``issue`` once per object(s) and problem. ``group``: key under which issues
        of different objects are merged into one (e.g. a row of equally small labels)."""
        if not self.record:
            return
        key = (issue.code, issue.refs or tuple(issue.objects))     # same object(s), same problem: once
        if key in self._seen:
            self._seen[key].count += 1
            return
        if group is not None and group in self._seen:
            self._seen[key] = first = self._seen[group]
            first.similar += 1
            return
        if group is not None:
            self._seen[group] = issue
        self._seen[key] = issue
        self.issues.append(issue)

    # -- results --------------------------------------------------------------

    def results(self) -> dict:
        """Machine-readable result (stored in the extraction output)."""
        issues = sorted(self.issues, key=lambda i: (SEVERITY_ORDER[i.severity], i.time or 0))
        counts = {s: sum(1 for i in issues if i.severity == s) for s in (ERROR, WARNING, INFO)}
        return {"summary": counts, "issues": [i.to_dict() for i in issues],
                "config": {k: self.config[k] for k in sorted(self.config)}}


def _without_copies(texts):
    """Drop texts lying exactly on an earlier text (glow/halo layers): reported once."""
    kept = []
    for text, top in texts:
        box = bbox(text)
        if not any(describe(t) == describe(text) and np.allclose(bbox(t), box, atol=0.02) for t, _ in kept):
            kept.append((text, top))
    return kept


def _variable_name(mob, frame, scene, skip: set = frozenset()) -> str | None:
    """Find what animation.py calls ``mob``: a local, an item of a local list/group, or a self attribute."""
    spaces = []
    if frame is not None:
        spaces.append(("", frame.f_locals))
    if scene is not None:
        spaces.append(("self.", {k: v for k, v in vars(scene).items() if not k.startswith("_") and k not in skip}))
    for prefix, space in spaces:
        for key, value in space.items():
            if value is mob and key != "self":
                return prefix + key
    m = _manim()
    for prefix, space in spaces:
        for key, value in space.items():
            items = value.submobjects if isinstance(value, m.Mobject) else value if isinstance(value, (list, tuple)) else None
            if items is None or key == "self":
                continue
            for index, item in enumerate(items):
                if item is mob:
                    return f"{prefix}{key}[{index}]"
    return None

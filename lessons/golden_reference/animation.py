"""
GOLDEN REFERENCE animation.py for the LMS video generator.

Demo topic: the Pythagorean theorem. The topic is only demonstration
content; what matters is the PATTERN. Copy the architecture, not the maths.

----------------------------------------------------------------------------
RULES THIS FILE DEMONSTRATES
----------------------------------------------------------------------------

1. ONE narrated class, whose base is written literally as ``LMSScene``.
   The generator finds it by reading the source, so ``class X(MyBase)`` with
   ``MyBase(LMSScene)`` is NOT detected.

2. Every ``self.narrate(...)`` is written out in full, in the section that
   uses it:

       n = self.narrate(
           id="unique_id",          # unique in the lesson, never reused
           text="...",              # exactly what the learner hears
           voice="default",         # alias in settings.json > voice.aliases
           subtitle=True,
       )

   Narration must be deterministic: same ids, same texts, same order on
   every run (no randomness, clocks or file reads around narrate()).

3. NARRATION IS THE TIMELINE. Every idea follows the same three beats:

       n = self.narrate(...)        # 1. what the learner HEARS
       self.play(...)               # 2. the visual for exactly that idea
       self.wait_for_narration(n)   # 3. hold it until the idea is spoken

   Timing tools, from coarse to fine:
       self.wait_for_narration(n)          hold until n (plus its pause) ends
       self.play_with(n, anim, fraction=f) spread a build over f of what is left of n
       self.at_word(n, "word")             land a visual on a spoken word
       narrate(..., pause_after=s)         silent thinking time
   Never time narrated content with self.wait(seconds).
   at_word() phrases must appear in that narration's text; use plain words
   (write numbers as words in the text, e.g. "six", and pick those).

4. SECTIONS. Each teaching section is one method:

       self.scene_start("S03_concept", title="Concept")
       ... narration + visuals ...
       self.clear_stage()           # fade the section's visuals away
       self.scene_end("S03_concept")

5. LAYOUT SAFETY. Nothing is placed by guesswork:
   * all positions come from the zone constants (LEFT_ZONE, RIGHT_ZONE, ...)
     inside SAFE_W x SAFE_H;
   * text is made with ``fitted_text`` (wraps, then shrinks a little, never
     below MIN_FONT, and raises if it cannot fit readably);
   * containers grow to their content (``self.card``) or fit content into a
     fixed size and register it with ``self.validator.check_fit``;
   * labels are placed outward from the shape they name
     (``RightTriangle.side_label``), so they never sit on the diagram;
   * ``self.validator.check_in_frame`` guards the tallest layouts.

6. TEXT. Narration explains; visuals show. On-screen text is labels,
   keywords, equations and short results, never paragraphs.
"""

import math

import numpy as np
from manim import *

from src.animation import LMSScene

# ============================================================== style ====

BG = "#0B1020"
INK = "#E6EAF2"
MUTED = "#8B95A7"
PANEL = "#151C2E"
SCENERY = "#3A4257"

# Semantic colours: one meaning each, used the same way in every section.
LEG_A = "#4FC3F7"      # side a
LEG_B = "#81C784"      # side b
HYP = "#FFB74D"        # hypotenuse c
RIGHT_MARK = "#F06292" # the right angle
FOCUS = "#FFD54F"      # "look here"
GOOD = "#66BB6A"       # confirmed result

FONT = "Segoe UI"
MIN_FONT = 22          # readable floor: text is never shrunk below this
TITLE = 46
BODY = 30
LABEL = 28
SMALL = 24
MATH = 44

# ============================================================= layout ====

FRAME_W = config.frame_width
FRAME_H = config.frame_height
SAFE = 0.45                                   # margin kept clear on every side
SAFE_W = FRAME_W - 2 * SAFE
SAFE_H = FRAME_H - 2 * SAFE

ZONE_W = 6.2                                  # width of each half-screen zone
LEFT_ZONE = LEFT * 3.35                       # centre of the left half
RIGHT_ZONE = RIGHT * 3.35                     # centre of the right half
TOP_Y = FRAME_H / 2 - SAFE - 0.9              # first row under the section tag
BOTTOM_Y = -FRAME_H / 2 + SAFE + 0.45         # caption / tracker row


# ======================================================= text helpers ====

def text(s, size=BODY, color=INK, weight=NORMAL):
    return Text(s, font=FONT, font_size=size, color=color, weight=weight)


def fit_width(mob, max_width):
    """Scale ``mob`` down (never up) to at most ``max_width``."""
    if mob.width > max_width:
        mob.scale_to_fit_width(max_width)
    return mob


def fit_height(mob, max_height):
    """Scale ``mob`` down (never up) to at most ``max_height``."""
    if mob.height > max_height:
        mob.scale_to_fit_height(max_height)
    return mob


def fit_within(mob, max_width, max_height):
    return fit_height(fit_width(mob, max_width), max_height)


def wrap_words(s, max_chars):
    """Greedy word wrap into lines of at most ``max_chars`` characters."""
    lines, line = [], ""
    for word in s.split():
        if line and len(line) + 1 + len(word) > max_chars:
            lines.append(line)
            line = word
        else:
            line = f"{line} {word}".strip()
    lines.append(line)
    return "\n".join(lines)


def wrap_lines(s, n_lines):
    """Wrap ``s`` into at most ``n_lines`` lines that are as even as possible."""
    for max_chars in range(math.ceil(len(s) / n_lines), len(s) + 1):
        wrapped = wrap_words(s, max_chars)
        if wrapped.count("\n") < n_lines:
            return wrapped
    return s


def fitted_text(s, max_width, size=BODY, color=INK, weight=NORMAL, max_lines=3):
    """Readable text no wider than ``max_width``.

    Order of preference: as written > slightly smaller (to 85 %) > wrapped
    over more lines > wrapped and smaller (never below MIN_FONT). If none of
    that fits, fail loudly: the author must shorten the text or widen the
    container. Tiny text is never an acceptable fix.
    """
    floor = max(MIN_FONT, 0.85 * size)
    for lines in range(1, max_lines + 1):
        body = s if lines == 1 else wrap_lines(s, lines)
        mob = text(body, size, color, weight)
        if mob.width <= max_width:
            return mob
        if size * max_width / mob.width >= floor:
            return mob.scale(max_width / mob.width)
        floor = MIN_FONT
    if size * max_width / mob.width >= MIN_FONT:
        return mob.scale(max_width / mob.width)
    raise ValueError(f"Text {s!r} cannot fit {max_width:.2f} units at a readable size; "
                     "shorten it or give it a wider container.")


def math_line(*parts, colors=None, size=MATH):
    """MathTex split into ``parts`` (so TransformMatchingTex can match them),
    each part coloured from ``colors`` = {part: colour}."""
    colors = colors or {}
    line = MathTex(*parts, font_size=size, color=INK)
    for part, sub in zip(parts, line):
        if part in colors:
            sub.set_color(colors[part])
    return line


def pill(label, color=FOCUS, size=SMALL, fill_opacity=0.14):
    """Short keyword tag. The box is sized from the text, so text cannot escape."""
    t = text(label, size, color, BOLD)
    box = RoundedRectangle(corner_radius=(t.height + 0.26) / 2, width=t.width + 0.5, height=t.height + 0.26,
                           stroke_color=color, stroke_width=2, fill_color=color, fill_opacity=fill_opacity)
    t.move_to(box)
    return VGroup(box, t)


def keep_in_frame(mob, margin=SAFE):
    """Shrink (if needed) and shift ``mob`` so it lies inside the safe area."""
    fit_within(mob, FRAME_W - 2 * margin, FRAME_H - 2 * margin)
    x_min, x_max = -FRAME_W / 2 + margin, FRAME_W / 2 - margin
    y_min, y_max = -FRAME_H / 2 + margin, FRAME_H / 2 - margin
    dx = max(0, x_min - mob.get_left()[0]) - max(0, mob.get_right()[0] - x_max)
    dy = max(0, y_min - mob.get_bottom()[1]) - max(0, mob.get_top()[1] - y_max)
    return mob.shift(RIGHT * dx + UP * dy)


# ==================================================== diagram helpers ====

class RightTriangle(VGroup):
    """Right triangle with the right angle at the bottom-left corner.

    ``side_a`` is the vertical leg, ``side_b`` the horizontal leg and
    ``side_c`` the hypotenuse. Vertices are read from the lines, so they stay
    correct after the triangle is moved or scaled.
    """

    def __init__(self, a, b, unit=0.5, stroke_width=6):
        super().__init__()
        corner, top, right = ORIGIN, UP * a * unit, RIGHT * b * unit
        self.side_a = Line(corner, top, color=LEG_A, stroke_width=stroke_width)
        self.side_b = Line(corner, right, color=LEG_B, stroke_width=stroke_width)
        self.side_c = Line(top, right, color=HYP, stroke_width=stroke_width)
        s = float(np.clip(min(a, b) * unit * 0.2, 0.15, 0.32))
        self.marker = VMobject(stroke_color=RIGHT_MARK, stroke_width=4).set_points_as_corners(
            [corner + UP * s, corner + UP * s + RIGHT * s, corner + RIGHT * s])
        self.add(self.side_a, self.side_b, self.side_c, self.marker)

    @property
    def C(self):  # the right-angle vertex
        return self.side_a.get_start()

    @property
    def A(self):  # top of side a
        return self.side_a.get_end()

    @property
    def B(self):  # end of side b
        return self.side_b.get_end()

    def centroid(self):
        return (self.A + self.B + self.C) / 3

    def outward(self, side):
        """Unit vector from the triangle's inside, through ``side``, to the outside."""
        v = side.get_center() - self.centroid()
        return v / np.linalg.norm(v)

    def side_label(self, side, mob, buff=0.22):
        """Place ``mob`` just outside ``side``, never on top of the diagram."""
        d = self.outward(side)
        reach = abs(d[0]) * mob.width / 2 + abs(d[1]) * mob.height / 2
        return mob.move_to(side.get_center() + d * (buff + reach))


def cells_on_side(p, q, n, color, away_from):
    """An n x n grid of unit cells standing on segment p-q, built outward
    (away from the point ``away_from``). Cell size = |pq| / n."""
    e = (q - p) / n
    f = np.array([-e[1], e[0], 0.0])
    if np.dot(away_from - (p + q) / 2, f) > 0:
        f = -f
    cells = VGroup()
    for i in range(n):
        for j in range(n):
            o = p + i * e + j * f
            cells.add(Polygon(o, o + e, o + e + f, o + f, stroke_color=BG, stroke_width=1.5,
                              fill_color=color, fill_opacity=0.85))
    return cells


# ============================================================= lesson ====

class PythagoreanTheoremVideo(LMSScene):
    lesson_title = "The Pythagorean Theorem"

    def construct(self):
        self.camera.background_color = BG
        self.section_tag = None

        self.hook()
        self.introduction()
        self.concept()
        self.visual_explanation()
        self.step_by_step()
        self.worked_example()
        self.practice()
        self.answer()
        self.summary()
        self.closing()

    # ---------------------------------------------------- scene helpers --

    def show_section_tag(self, label):
        """Small tag in the top-left corner naming the current section."""
        tag = pill(label.upper(), MUTED, size=18, fill_opacity=0.08)
        tag.to_corner(UL, buff=SAFE)
        if self.section_tag is None:
            self.play(FadeIn(tag), run_time=0.4)
        else:
            self.play(FadeTransform(self.section_tag, tag), run_time=0.4)
        self.section_tag = tag

    def clear_stage(self, run_time=0.6):
        """Scene transition: fade out everything except the section tag."""
        others = [m for m in self.mobjects if m is not self.section_tag]
        if others:
            self.play(FadeOut(Group(*others)), run_time=run_time)

    def card(self, content, width=None, height=None, color=MUTED, pad=0.3):
        """Container-aware card.

        No size given: the box grows to fit ``content``.
        Size given: ``content`` is scaled down to fit inside it, and the pair
        is registered with the layout validator so the fit is re-checked.
        """
        if width is not None or height is not None:
            fit_within(content, (width or 99) - 2 * pad, (height or 99) - 2 * pad)
        w = width if width is not None else content.width + 2 * pad
        h = height if height is not None else content.height + 2 * pad
        box = RoundedRectangle(corner_radius=0.18, width=w, height=h, stroke_color=color,
                               stroke_width=2.5, fill_color=PANEL, fill_opacity=1)
        box.move_to(content)
        self.validator.check_fit(content, box, margin=0.1)
        return VGroup(box, content)

    def caption(self, s, color=INK):
        """One-line keyword caption in a fixed-width bar at the bottom of the frame."""
        t = fitted_text(s, SAFE_W - 1.0, BODY, color)
        bar = self.card(t, width=SAFE_W - 0.4, height=t.height + 0.9)   # height = text + 2 x pad + margin
        return bar.move_to(UP * BOTTOM_Y)

    def step_tracker(self, labels):
        tracker = VGroup(*[pill(f"{i + 1}  {label}", MUTED, fill_opacity=0.05)
                           for i, label in enumerate(labels)]).arrange(RIGHT, buff=0.3)
        return fit_width(tracker, SAFE_W).move_to(UP * BOTTOM_Y)

    def focus_step(self, tracker, index):
        """Light step ``index``, mark earlier steps done, dim later ones."""
        anims = []
        for i, (box, label) in enumerate(tracker):
            color = FOCUS if i == index else GOOD if i < index else MUTED
            opacity = 0.2 if i == index else 0.05
            anims += [box.animate.set_stroke(color).set_fill(color, opacity), label.animate.set_color(color)]
        return AnimationGroup(*anims)

    def derivation_start(self, line, y=TOP_Y - 0.3):
        """First line of a worked derivation: left-aligned in the right zone."""
        line.move_to(RIGHT_ZONE + UP * y)
        return line.align_to(RIGHT_ZONE + LEFT * (ZONE_W / 2 - 0.4), LEFT)

    def derivation_next(self, prev, *parts, colors=None):
        """Next derivation line, directly below ``prev`` and left-aligned with it."""
        return math_line(*parts, colors=colors).next_to(prev, DOWN, buff=0.38, aligned_edge=LEFT)

    def countdown(self, seconds):
        """Thinking-time ring that empties over ``seconds`` (for pause_after)."""
        centre = RIGHT * (FRAME_W / 2 - SAFE - 0.5) + DOWN * (FRAME_H / 2 - SAFE - 0.5)
        tracker = ValueTracker(1.0)
        track = Circle(radius=0.38, stroke_color=MUTED, stroke_width=3).move_to(centre)
        ring = always_redraw(lambda: Arc(radius=0.38, start_angle=PI / 2, angle=max(TAU * tracker.get_value(), 1e-3),
                                         arc_center=centre, stroke_color=FOCUS, stroke_width=8))
        label = pill("Think", FOCUS).next_to(track, LEFT, buff=0.3)
        self.play(FadeIn(track), FadeIn(label), run_time=0.3)
        self.add(ring)
        self.play(tracker.animate.set_value(0.0), run_time=max(0.5, seconds - 0.3), rate_func=linear)
        self.remove(ring)
        self.play(FadeOut(track), FadeOut(label), run_time=0.3)

    def ladder_picture(self):
        """Wall, ground and ladder. The ladder is the hypotenuse of ``pic.tri``."""
        tri = RightTriangle(8, 6, unit=0.36)
        wall = Rectangle(width=0.5, height=tri.side_a.get_length() + 0.4, stroke_width=0,
                         fill_color=SCENERY, fill_opacity=1)
        wall.move_to(tri.C, aligned_edge=DR)
        bricks = VGroup(*[Line(wall.get_left(), wall.get_right(), stroke_color=BG, stroke_width=2)
                          .shift(UP * y) for y in np.linspace(-wall.height / 2 + 0.3, wall.height / 2 - 0.3, 6)])
        ground = Rectangle(width=tri.side_b.get_length() + 1.2, height=0.16, stroke_width=0,
                           fill_color=SCENERY, fill_opacity=1)
        ground.next_to(tri.C, DOWN, buff=0).align_to(wall, LEFT)
        direction = (tri.B - tri.A) / np.linalg.norm(tri.B - tri.A)
        normal = tri.outward(tri.side_c) * 0.22
        rail = tri.side_c.copy().shift(normal).set_stroke(HYP, width=4)
        rungs = VGroup(*[Line(tri.A + direction * d, tri.A + direction * d + normal, stroke_color=HYP, stroke_width=3)
                         for d in np.linspace(0.3, tri.side_c.get_length() - 0.3, 8)])
        pic = VGroup(VGroup(wall, bricks), ground, tri, VGroup(rail, rungs))
        pic.tri, pic.scenery = tri, VGroup(pic[0], ground, pic[3])
        return pic

    # ================================================= 1. HOOK ==========
    # Purpose: a concrete question the learner cannot answer yet.

    def hook(self):
        self.scene_start("S01_hook", title="Hook")
        self.show_section_tag("Hook")

        pic = self.ladder_picture().move_to(DOWN * 0.4)
        tri = pic.tri
        wall_label = tri.side_label(tri.side_a, text("8 m", LABEL, LEG_A, BOLD), buff=0.75)
        ground_label = tri.side_label(tri.side_b, text("6 m", LABEL, LEG_B, BOLD), buff=0.35)

        # HEAR: the situation.  SEE: wall, ground, then the ladder; each length
        # appears on the word that names it.
        n = self.narrate(
            id="hook_01",
            text="A ladder leans against a wall. Its foot is six metres from the wall, "
                 "and its top reaches eight metres up the wall.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(pic.scenery[0]), FadeIn(pic.scenery[1]), run_time=0.8)
        self.play(Create(tri.side_c), FadeIn(pic.scenery[2]), run_time=1.0)
        self.add(tri.side_a, tri.side_b)
        self.at_word(n, "six")
        self.play(Indicate(tri.side_b, color=LEG_B), FadeIn(ground_label, shift=UP * 0.2))
        self.at_word(n, "eight")
        self.play(Indicate(tri.side_a, color=LEG_A), FadeIn(wall_label, shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        # HEAR: the question.  SEE: the unknown length, marked on the ladder.
        unknown = tri.side_label(tri.side_c, MathTex("?", font_size=64, color=FOCUS), buff=0.55)
        n = self.narrate(
            id="hook_02",
            text="How long is the ladder? You cannot measure it from the ground, but you can calculate it.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(unknown, scale=1.5), Indicate(pic.scenery[2], color=FOCUS))
        self.wait_for_narration(n)

        self.hook_picture = VGroup(pic, wall_label, ground_label, unknown)   # reused by the introduction
        self.scene_end("S01_hook")

    # ========================================= 2. INTRODUCTION ==========
    # Purpose: turn the real object into the abstract shape, and name the topic.

    def introduction(self):
        self.scene_start("S02_introduction", title="Introduction")
        self.show_section_tag("Introduction")
        pic, wall_label, ground_label, unknown = self.hook_picture
        tri = pic.tri

        # HEAR: the picture is a triangle with a square corner.
        # SEE: the scenery fades, the bare triangle stays, the corner pulses.
        n = self.narrate(
            id="intro_01",
            text="Notice that the wall, the ground and the ladder form a triangle, "
                 "with a perfect square corner where the wall meets the ground.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(pic.scenery), FadeOut(VGroup(wall_label, ground_label, unknown)), run_time=0.8)
        self.at_word(n, "corner")
        self.play(Indicate(tri.marker, color=RIGHT_MARK, scale_factor=1.8))
        self.wait_for_narration(n)

        # HEAR: the name of the rule.  SEE: the title, next to the shape it is about.
        title = fitted_text("The Pythagorean Theorem", ZONE_W - 0.4, TITLE, FOCUS, BOLD)
        subtitle = fitted_text("connects the three sides of a right triangle", ZONE_W - 0.4, SMALL, MUTED)
        heading = VGroup(title, subtitle).arrange(DOWN, buff=0.25).move_to(RIGHT_ZONE)
        n = self.narrate(
            id="intro_02",
            text="One rule connects the three sides of every triangle like this. "
                 "It is called the Pythagorean theorem.",
            voice="default",
            subtitle=True,
        )
        self.play(tri.animate.move_to(LEFT_ZONE), run_time=0.8)
        self.at_word(n, "Pythagorean")
        self.play(Write(title), FadeIn(subtitle, shift=UP * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_introduction")

    # ============================================== 3. CONCEPT ==========
    # Purpose: definitions. Each term lights up the exact part it names.

    def concept(self):
        self.scene_start("S03_concept", title="Concept")
        self.show_section_tag("Concept")

        tri = RightTriangle(3, 4, unit=0.75).move_to(UP * 0.5)
        angle = MathTex(r"90^\circ", font_size=32, color=RIGHT_MARK).move_to(tri.C + UR * 0.55)
        label_a = VGroup(MathTex("a", font_size=48, color=LEG_A), text("leg", SMALL, LEG_A)).arrange(DOWN, buff=0.08)
        label_b = VGroup(MathTex("b", font_size=48, color=LEG_B), text("leg", SMALL, LEG_B)).arrange(RIGHT, buff=0.2)
        label_c = VGroup(MathTex("c", font_size=48, color=HYP), text("hypotenuse", SMALL, HYP)).arrange(RIGHT, buff=0.2)
        tri.side_label(tri.side_a, label_a)
        tri.side_label(tri.side_b, label_b)
        tri.side_label(tri.side_c, label_c)

        # HEAR: what a right angle is.  SEE: the triangle drawn, then the
        # corner square and "90°" on the word "square".
        n = self.narrate(
            id="concept_01",
            text="A right triangle has one angle of exactly ninety degrees, called the right angle. "
                 "We mark it with a small square.",
            voice="default",
            subtitle=True,
        )
        self.play(Create(VGroup(tri.side_a, tri.side_b, tri.side_c)), run_time=1.2)
        cap = self.caption("Right angle: exactly 90°", RIGHT_MARK)
        self.play(FadeIn(cap, shift=UP * 0.2))
        self.at_word(n, "square")
        self.play(Create(tri.marker), FadeIn(angle))
        self.wait_for_narration(n)

        # HEAR: the legs.  SEE: both legs pulse and get their names.
        n = self.narrate(
            id="concept_02",
            text="The two sides that form the right angle are called the legs. We will call them a and b.",
            voice="default",
            subtitle=True,
        )
        new_cap = self.caption("Legs: the two sides that form the right angle")
        self.play(FadeTransform(cap, new_cap), Indicate(tri.side_a, color=LEG_A), Indicate(tri.side_b, color=LEG_B))
        cap = new_cap
        self.play(FadeIn(label_a, shift=LEFT * 0.2), FadeIn(label_b, shift=DOWN * 0.2))
        self.wait_for_narration(n)

        # HEAR: the hypotenuse.  SEE: it glows on the word, then gets its name.
        n = self.narrate(
            id="concept_03",
            text="The side opposite the right angle is the hypotenuse. It is always the longest side.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "hypotenuse")
        new_cap = self.caption("Hypotenuse: opposite the right angle, the longest side", HYP)
        self.play(FadeTransform(cap, new_cap), tri.side_c.animate.set_stroke(width=10))
        self.play(FadeIn(label_c, shift=UR * 0.2), tri.side_c.animate.set_stroke(width=6))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_concept")

    # ===================================== 4. VISUAL EXPLANATION ==========
    # Purpose: show WHY the rule is true, with areas, before any formula.

    def visual_explanation(self):
        self.scene_start("S04_visual", title="Visual explanation")
        self.show_section_tag("Why it works")

        u = 0.42
        tri = RightTriangle(3, 4, unit=u, stroke_width=4)
        square_a = cells_on_side(tri.C, tri.A, 3, LEG_A, tri.centroid())
        square_b = cells_on_side(tri.C, tri.B, 4, LEG_B, tri.centroid())
        square_c = cells_on_side(tri.A, tri.B, 5, HYP, tri.centroid())
        figure = VGroup(square_a, square_b, square_c, tri)
        figure.move_to(LEFT_ZONE + DOWN * 0.2)
        self.validator.check_in_frame(figure)

        def area_label(cells, value):
            return MathTex(value, font_size=40, color=BG).move_to(cells)

        self.play(Create(tri), run_time=0.8)

        # HEAR: square on a = 9.  SEE: 9 cells build on side a, then "9".
        n = self.narrate(
            id="visual_01",
            text="Build a square on each side. Side a is three units long, so its square holds nine small squares.",
            voice="default",
            subtitle=True,
        )
        self.play_with(n, LaggedStart(*[FadeIn(c, scale=0.6) for c in square_a], lag_ratio=0.15), fraction=0.6)
        nine = area_label(square_a, "9")
        self.play(FadeIn(nine))
        self.wait_for_narration(n)

        # HEAR: square on b = 16.  SEE: 16 cells build on side b, then "16".
        n = self.narrate(
            id="visual_02",
            text="Side b is four units long, so its square holds sixteen.",
            voice="default",
            subtitle=True,
        )
        self.play_with(n, LaggedStart(*[FadeIn(c, scale=0.6) for c in square_b], lag_ratio=0.1), fraction=0.6)
        sixteen = area_label(square_b, "16")
        self.play(FadeIn(sixteen))
        self.wait_for_narration(n)

        # HEAR: square on c = 25.  SEE: 25 cells build on the hypotenuse, then "25".
        n = self.narrate(
            id="visual_03",
            text="The hypotenuse is five units long, so its square holds twenty-five.",
            voice="default",
            subtitle=True,
        )
        self.play_with(n, LaggedStart(*[FadeIn(c, scale=0.6) for c in square_c], lag_ratio=0.06), fraction=0.6)
        twenty_five = area_label(square_c, "25")
        self.play(FadeIn(twenty_five))
        self.wait_for_narration(n)

        # HEAR: move the small squares.  SEE: copies of the 9 + 16 cells slide
        # into one 5 x 5 block on the right.
        block = VGroup(*[Square(u) for _ in range(25)]).arrange_in_grid(rows=5, cols=5, buff=0)
        block.move_to(RIGHT_ZONE + UP * 1.0)
        pieces = VGroup(*[c.copy() for c in square_a], *[c.copy() for c in square_b])
        n = self.narrate(
            id="visual_04",
            text="Now take the nine small squares and the sixteen small squares, and slide them into one block.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "slide")
        moves = [Transform(p, Square(u, stroke_color=BG, stroke_width=1.5, fill_color=p.get_fill_color(),
                                     fill_opacity=0.85).move_to(target))
                 for p, target in zip(pieces, block)]
        self.play_with(n, LaggedStart(*moves, lag_ratio=0.04), fraction=0.9)
        self.wait_for_narration(n)

        # HEAR: the block matches the big square.  SEE: both outlined in the
        # hypotenuse colour, and the sum written under the block.
        outline = SurroundingRectangle(pieces, color=HYP, buff=0.05, stroke_width=4)
        sums = math_line("9", "+", "16", "=", "25", colors={"9": LEG_A, "16": LEG_B, "25": HYP})
        sums.next_to(block, DOWN, buff=0.45)
        n = self.narrate(
            id="visual_05",
            text="They fill a five by five block exactly, the same area as the square on the hypotenuse.",
            voice="default",
            subtitle=True,
        )
        # Indicate the square WITH its label: indicating only the cells would redraw them over "25".
        self.play(Create(outline), Indicate(VGroup(square_c, twenty_five), color=FOCUS, scale_factor=1.03))
        self.play(Write(sums))
        self.wait_for_narration(n)

        # HEAR: the general rule.  SEE: the numbers become letters.
        rule = math_line("a^2", "+", "b^2", "=", "c^2", colors={"a^2": LEG_A, "b^2": LEG_B, "c^2": HYP}, size=56)
        rule.next_to(sums, DOWN, buff=0.45)
        n = self.narrate(
            id="visual_06",
            text="So the two smaller squares always add up to the biggest square: "
                 "a squared plus b squared equals c squared.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "squared")
        self.play(TransformFromCopy(sums, rule), run_time=1.2)
        self.play(Circumscribe(rule, color=FOCUS))
        self.validator.check_in_frame(VGroup(block, sums, rule))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_visual")

    # ========================================= 5. STEP-BY-STEP ==========
    # Purpose: the procedure. A tracker shows where we are; each step
    # changes the formula itself instead of listing text.

    def step_by_step(self):
        self.scene_start("S05_steps", title="Step by step")
        self.show_section_tag("Step by step")

        tri = RightTriangle(3, 4, unit=0.42, stroke_width=5)
        tri.move_to(LEFT_ZONE + UP * 0.6)
        la = tri.side_label(tri.side_a, MathTex("a", font_size=40, color=LEG_A))
        lb = tri.side_label(tri.side_b, MathTex("b", font_size=40, color=LEG_B))
        lc = tri.side_label(tri.side_c, MathTex("c", font_size=40, color=HYP))
        colors = {"a^2": LEG_A, "b^2": LEG_B, "c^2": HYP, "c": HYP, r"\sqrt{a^2+b^2}": FOCUS}
        formula = math_line("a^2", "+", "b^2", "=", "c^2", colors=colors, size=60).move_to(RIGHT_ZONE + UP * 1.0)
        tracker = self.step_tracker(["Square the legs", "Add", "Square root"])

        # HEAR: three steps.  SEE: the triangle, the formula, and the tracker.
        n = self.narrate(
            id="steps_01",
            text="To find the hypotenuse, we follow three steps.",
            voice="default",
            subtitle=True,
        )
        self.play(Create(tri), FadeIn(VGroup(la, lb, lc)), Write(formula))
        self.play(FadeIn(tracker, shift=UP * 0.2))
        self.wait_for_narration(n)

        # HEAR: step one.  SEE: squares grow on both legs; a² and b² are boxed.
        square_a = cells_on_side(tri.C, tri.A, 3, LEG_A, tri.centroid())
        square_b = cells_on_side(tri.C, tri.B, 4, LEG_B, tri.centroid())
        boxes = VGroup(SurroundingRectangle(formula[0], color=LEG_A), SurroundingRectangle(formula[2], color=LEG_B))
        n = self.narrate(
            id="steps_02",
            text="Step one: square each leg.",
            voice="default",
            subtitle=True,
        )
        self.play(self.focus_step(tracker, 0), FadeOut(VGroup(la, lb)))
        self.play(FadeIn(square_a), FadeIn(square_b), Create(boxes))
        self.wait_for_narration(n)

        # HEAR: step two.  SEE: a brace joins a² + b² and points at c².
        brace = Brace(formula[0:3], DOWN, color=FOCUS)
        brace_label = text("add", SMALL, FOCUS, BOLD).next_to(brace, DOWN, buff=0.12)
        n = self.narrate(
            id="steps_03",
            text="Step two: add the two squares. That sum is c squared.",
            voice="default",
            subtitle=True,
        )
        self.play(self.focus_step(tracker, 1), FadeOut(boxes))
        self.play(GrowFromCenter(brace), FadeIn(brace_label))
        self.at_word(n, "sum")
        self.play(Indicate(formula[4], color=HYP, scale_factor=1.3))
        self.wait_for_narration(n)

        # HEAR: step three, on the word "root".  SEE: the formula rearranges
        # into c = √(a² + b²), and c glows on the triangle.
        solved = math_line("c", "=", r"\sqrt{a^2+b^2}", colors=colors, size=60).move_to(formula)
        n = self.narrate(
            id="steps_04",
            text="Step three: take the square root to undo the squaring, and you have c.",
            voice="default",
            subtitle=True,
        )
        self.play(self.focus_step(tracker, 2), FadeOut(VGroup(brace, brace_label)))
        self.at_word(n, "root")
        self.play(TransformMatchingTex(formula, solved), run_time=1.2)
        self.play(Indicate(tri.side_c, color=HYP), Indicate(lc, color=HYP))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_steps")

    # ========================================= 6. WORKED EXAMPLE ==========
    # Purpose: apply the steps to the hook's question. Every spoken step
    # makes exactly one visual change: highlight > substitute > compute > reveal.
    # The derivation stays on screen as a trail of reasoning.

    def worked_example(self):
        self.scene_start("S06_example", title="Worked example")
        self.show_section_tag("Worked example")

        pic = self.ladder_picture().move_to(LEFT_ZONE + DOWN * 0.3)
        tri = pic.tri
        wall_label = tri.side_label(tri.side_a, MathTex("a = 8", font_size=38, color=LEG_A), buff=0.75)
        ground_label = tri.side_label(tri.side_b, MathTex("b = 6", font_size=38, color=LEG_B), buff=0.35)
        ladder_label = tri.side_label(tri.side_c, MathTex("c", font_size=46, color=HYP), buff=0.55)
        colors = {"a^2": LEG_A, "b^2": LEG_B, "8^2": LEG_A, "6^2": LEG_B, "64": LEG_A, "36": LEG_B,
                  "c^2": HYP, "c": HYP, "10": GOOD}
        self.play(FadeIn(pic), run_time=0.8)

        # HEAR: first, identify the legs.  SEE: wall and ground pulse, labelled a and b.
        n = self.narrate(
            id="example_01",
            text="Let's solve the ladder problem. First, identify the sides. The wall and the ground "
                 "meet at the right angle, so they are the legs: eight and six.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "wall", occurrence=1)
        self.play(Indicate(tri.marker, color=RIGHT_MARK, scale_factor=1.8))
        self.at_word(n, "legs")
        self.play(Indicate(tri.side_a, color=LEG_A), Indicate(tri.side_b, color=LEG_B),
                  FadeIn(wall_label), FadeIn(ground_label))
        self.wait_for_narration(n)

        # HEAR: the ladder is c.  SEE: the ladder glows and gets the label c.
        n = self.narrate(
            id="example_02",
            text="The ladder is opposite the right angle, so it is the hypotenuse, c.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "hypotenuse")
        self.play(Indicate(pic.scenery[2], color=HYP), FadeIn(ladder_label, scale=1.4))
        self.wait_for_narration(n)

        # HEAR: write the theorem, then substitute.  SEE: line 1, then line 2
        # grows out of it with the numbers in place of the letters.
        line1 = self.derivation_start(math_line("a^2", "+", "b^2", "=", "c^2", colors=colors))
        line2 = self.derivation_next(line1, "8^2", "+", "6^2", "=", "c^2", colors=colors)
        n = self.narrate(
            id="example_03",
            text="Now write the theorem and substitute: eight squared plus six squared equals c squared.",
            voice="default",
            subtitle=True,
        )
        self.play(Write(line1))
        self.at_word(n, "substitute")
        self.play(TransformMatchingTex(line1.copy(), line2), run_time=1.2)
        self.wait_for_narration(n)

        # HEAR: compute each square.  SEE: 64, then 36, each on its own beat.
        line3 = self.derivation_next(line2, "64", "+", "36", "=", "c^2", colors=colors)
        n = self.narrate(
            id="example_04",
            text="Eight squared is sixty-four, and six squared is thirty-six.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(line3[1:]), ReplacementTransform(line2[0].copy(), line3[0]))
        self.play(ReplacementTransform(line2[2].copy(), line3[2]))
        self.wait_for_narration(n)

        # HEAR: add.  SEE: the sum 100.
        line4 = self.derivation_next(line3, "c^2", "=", "100", colors=colors)
        n = self.narrate(
            id="example_05",
            text="Add them, and c squared is one hundred.",
            voice="default",
            subtitle=True,
        )
        self.play(TransformMatchingTex(line3.copy(), line4), run_time=1.0)
        self.wait_for_narration(n)

        # HEAR: therefore c = 10.  SEE: the root, the boxed result, and the
        # label on the ladder turning from "c" into "10 m" on the word "ladder".
        line5 = self.derivation_next(line4, "c", "=", r"\sqrt{100}", "=", "10", colors=colors)
        result_box = SurroundingRectangle(line5, color=GOOD, buff=0.15, stroke_width=3)
        answer_label = tri.side_label(tri.side_c, text("10 m", LABEL + 4, GOOD, BOLD), buff=0.55)
        n = self.narrate(
            id="example_06",
            text="Therefore c is the square root of one hundred, which is ten. The ladder is ten metres long.",
            voice="default",
            subtitle=True,
        )
        self.play(TransformMatchingTex(line4.copy(), line5), run_time=1.0)
        self.play(Create(result_box))
        self.at_word(n, "ladder")
        self.play(ReplacementTransform(ladder_label, answer_label), Indicate(pic.scenery[2], color=GOOD))
        self.validator.check_in_frame(VGroup(line1, line5, result_box))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_example")

    # ============================================= 7. PRACTICE ==========
    # Purpose: the learner tries it. The question is a DIAGRAM with a "?",
    # not a slide of text; pause_after gives silent thinking time.

    def practice(self):
        self.scene_start("S07_practice", title="Practice")
        self.show_section_tag("Your turn")

        tri = RightTriangle(5, 12, unit=0.34).move_to(LEFT_ZONE + UP * 0.2)
        la = tri.side_label(tri.side_a, MathTex("5", font_size=44, color=LEG_A))
        lb = tri.side_label(tri.side_b, MathTex("?", font_size=56, color=FOCUS))
        lc = tri.side_label(tri.side_c, MathTex("13", font_size=44, color=HYP))
        prompt = VGroup(
            fitted_text("Find the missing leg", ZONE_W - 0.6, BODY, INK, BOLD),
            math_line("5", ",", r"\;13", r"\;\rightarrow\;", "?", colors={"?": FOCUS}, size=48),
        ).arrange(DOWN, buff=0.35)
        prompt_card = self.card(prompt, color=FOCUS).move_to(RIGHT_ZONE + UP * 0.2)

        # HEAR: the question.  SEE: the triangle is drawn, each given length
        # appears as it is spoken, and the unknown flashes.
        n = self.narrate(
            id="practice_01",
            text="Your turn. A right triangle has a hypotenuse of thirteen and one leg of five. "
                 "How long is the other leg? Pause and work it out.",
            voice="default",
            subtitle=True,
            pause_after=6.0,
        )
        self.play(Create(tri), run_time=1.0)
        self.at_word(n, "thirteen")
        self.play(FadeIn(lc), Indicate(tri.side_c, color=HYP))
        self.at_word(n, "five")
        self.play(FadeIn(la), Indicate(tri.side_a, color=LEG_A))
        self.at_word(n, "other")
        self.play(FadeIn(lb, scale=1.6), FadeIn(prompt_card, shift=LEFT * 0.3))
        self.wait_for_narration(n, include_pause=False)

        # SILENCE (pause_after): countdown ring while the learner thinks.
        self.countdown(n.pause_after)

        self.practice_parts = (tri, la, lb, lc, prompt_card)   # the answer builds on this picture
        self.scene_end("S07_practice")

    # =============================================== 8. ANSWER ==========
    # Purpose: solve it visibly, then check it with a second representation
    # (a number line of perfect squares).

    def answer(self):
        self.scene_start("S08_answer", title="Answer")
        self.show_section_tag("Answer")
        tri, la, lb, lc, prompt_card = self.practice_parts
        colors = {"b^2": LEG_B, "a^2": LEG_A, "c^2": HYP, "13^2": HYP, "5^2": LEG_A, "169": HYP, "25": LEG_A,
                  "144": FOCUS, "b": LEG_B, "12": GOOD}

        # HEAR: the missing side is a leg, so rearrange.  SEE: the picture moves
        # up and left, and the rearranged formula appears.
        line1 = self.derivation_start(math_line("b^2", "=", "c^2", "-", "a^2", colors=colors), y=TOP_Y - 0.1)
        n = self.narrate(
            id="answer_01",
            text="This time the missing side is a leg, not the hypotenuse. So we rearrange: "
                 "b squared equals c squared minus a squared.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(prompt_card), VGroup(tri, la, lb, lc).animate.scale(0.85).move_to(LEFT_ZONE + UP * 1.3))
        self.at_word(n, "rearrange")
        self.play(Write(line1))
        self.wait_for_narration(n)

        # HEAR: substitute and subtract.  SEE: two lines, one per spoken result.
        line2 = self.derivation_next(line1, "b^2", "=", "13^2", "-", "5^2", colors=colors)
        line3 = self.derivation_next(line2, "b^2", "=", "169", "-", "25", colors=colors)
        result = math_line("=", "144", colors=colors).next_to(line3, RIGHT, buff=0.2)
        n = self.narrate(
            id="answer_02",
            text="Substitute: thirteen squared minus five squared is one hundred sixty-nine minus twenty-five, "
                 "which is one hundred forty-four.",
            voice="default",
            subtitle=True,
        )
        self.play(TransformMatchingTex(line1.copy(), line2))
        self.at_word(n, "minus", occurrence=2)
        self.play(TransformMatchingTex(line2.copy(), line3))
        self.at_word(n, "which")
        self.play(FadeIn(result, shift=LEFT * 0.2))
        self.wait_for_narration(n)

        # HEAR: which number squared is 144?  SEE: a number line of perfect squares.
        axis = NumberLine(x_range=[100, 170, 10], length=SAFE_W - 1.2, color=MUTED, include_numbers=True,
                          font_size=26, include_tip=False).move_to(DOWN * 2.3)
        marks = VGroup()
        for k in (10, 11, 12, 13):
            dot = Dot(axis.n2p(k * k), radius=0.09, color=INK)
            tag = MathTex(f"{k}^2", font_size=34, color=INK).next_to(dot, UP, buff=0.18)
            marks.add(VGroup(dot, tag))
        n = self.narrate(
            id="answer_03",
            text="Which number squared gives one hundred forty-four? Look at the perfect squares on this number line.",
            voice="default",
            subtitle=True,
        )
        self.play(Create(axis), run_time=1.0)
        self.at_word(n, "perfect")
        self.play(LaggedStart(*[FadeIn(m, shift=DOWN * 0.15) for m in marks], lag_ratio=0.3))
        self.wait_for_narration(n)

        # HEAR: twelve squared is 144.  SEE: the 12² mark lights up, the final
        # line is boxed, and the "?" on the triangle becomes 12.
        hit = marks[2]
        line4 = self.derivation_next(line3, "b", "=", "12", colors=colors)
        result_box = SurroundingRectangle(line4, color=GOOD, buff=0.15, stroke_width=3)
        answer_label = tri.side_label(tri.side_b, MathTex("12", font_size=40, color=GOOD))
        n = self.narrate(
            id="answer_04",
            text="Twelve squared is exactly one hundred forty-four, so the missing leg is twelve.",
            voice="default",
            subtitle=True,
        )
        self.play(hit.animate.set_color(GOOD), Flash(hit[0], color=GOOD))
        self.play(TransformFromCopy(VGroup(line3, result), line4), Create(result_box))
        self.play(ReplacementTransform(lb, answer_label), Indicate(tri.side_b, color=GOOD))
        self.validator.check_in_frame(VGroup(line1, line4, result_box, axis, marks))
        self.wait_for_narration(n)

        # HEAR: sanity check.  SEE: the hypotenuse and its 13 pulse.
        n = self.narrate(
            id="answer_05",
            text="Quick check: thirteen is still the longest side, just as the hypotenuse must be.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "longest")
        self.play(Indicate(tri.side_c, color=HYP), Indicate(lc, color=HYP, scale_factor=1.4))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S08_answer")

    # ============================================== 9. SUMMARY ==========
    # Purpose: three takeaways, one card each, each card appearing with the
    # sentence that states it. Cards are fixed-size and content is fitted.

    def summary(self):
        self.scene_start("S09_summary", title="Summary")
        self.show_section_tag("Summary")
        card_w, card_h = 4.1, 3.3

        mini = RightTriangle(3, 4, unit=0.38, stroke_width=4)
        mini_c = mini.side_label(mini.side_c, MathTex("c", font_size=36, color=HYP))
        card1 = self.card(VGroup(VGroup(mini, mini_c), fitted_text("right triangles only", card_w - 0.8, SMALL))
                          .arrange(DOWN, buff=0.35), width=card_w, height=card_h, color=RIGHT_MARK)
        card2 = self.card(VGroup(math_line("a^2", "+", "b^2", "=", "c^2",
                                           colors={"a^2": LEG_A, "b^2": LEG_B, "c^2": HYP}, size=48),
                                 fitted_text("small squares add up", card_w - 0.8, SMALL))
                          .arrange(DOWN, buff=0.45), width=card_w, height=card_h, color=HYP)
        card3 = self.card(VGroup(math_line("c", "=", r"\sqrt{a^2+b^2}", colors={"c": HYP}, size=40),
                                 math_line("b", "=", r"\sqrt{c^2-a^2}", colors={"b": LEG_B}, size=40),
                                 fitted_text("side or hypotenuse", card_w - 0.8, SMALL))
                          .arrange(DOWN, buff=0.3), width=card_w, height=card_h, color=GOOD)
        cards = VGroup(card1, card2, card3).arrange(RIGHT, buff=0.35)
        fit_width(cards, SAFE_W).move_to(DOWN * 0.2)
        self.validator.check_in_frame(cards)

        n = self.narrate(
            id="summary_01",
            text="Let's summarise. The theorem only works for right triangles, and c is always the hypotenuse, "
                 "opposite the right angle.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(card1, shift=UP * 0.3))
        self.at_word(n, "hypotenuse")
        self.play(Indicate(mini.side_c, color=HYP), Indicate(mini_c, color=HYP))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_02",
            text="The two smaller squares add up to the biggest square: a squared plus b squared equals c squared.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(card2, shift=UP * 0.3))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_03",
            text="To find the hypotenuse, add and take the root. To find a leg, subtract and take the root.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(card3[0]), FadeIn(card3[1][0]), FadeIn(card3[1][2]))
        self.at_word(n, "leg")
        self.play(FadeIn(card3[1][1], shift=UP * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S09_summary")

    # ============================================== 10. CLOSING ==========
    # Purpose: return to the opening picture, now solved, and close warmly.

    def closing(self):
        self.scene_start("S10_closing", title="Closing")
        self.show_section_tag("Closing")

        pic = self.ladder_picture().scale(0.8).move_to(LEFT_ZONE + DOWN * 0.2)
        ladder = pic.tri.side_label(pic.tri.side_c, text("10 m", LABEL, GOOD, BOLD), buff=0.5)
        rule = math_line("a^2", "+", "b^2", "=", "c^2", colors={"a^2": LEG_A, "b^2": LEG_B, "c^2": HYP}, size=64)
        rule.move_to(RIGHT_ZONE + UP * 0.2)
        arrow = Arrow(pic.get_right(), rule.get_left(), buff=0.4, color=FOCUS, stroke_width=6)

        n = self.narrate(
            id="closing_01",
            text="From a ladder against a wall to any right triangle, you now have one rule that finds the missing side.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(pic), FadeIn(ladder))
        self.at_word(n, "rule")
        self.play(GrowArrow(arrow), Write(rule))
        self.wait_for_narration(n)

        n = self.narrate(
            id="closing_02",
            text="Try it on a few triangles of your own. See you in the next lesson.",
            voice="default",
            subtitle=True,
        )
        self.play(Circumscribe(rule, color=FOCUS, run_time=1.5))
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S10_closing")

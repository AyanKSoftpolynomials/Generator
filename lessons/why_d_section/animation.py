"""
animation.py for the LMS video generator.

Course : C-CAT Preparation (Pre C-CAT) - D. Computer Fundamentals and Concepts of Programming
Video  : Why Computer Fundamentals and Concepts of Programming is in the Pre C-CAT  (section introduction, before Module 1)
Source : written for this video on 27 Oct 2026 (no source script); same structure and look as the module and lesson
         introductions in "All introductions".

Exam facts used (C-DAC C-CAT, as listed by the usual exam guides): three sections A, B and C; Section A is taken by
  every candidate and covers English, quantitative aptitude, reasoning, and computer fundamentals with concepts of
  programming; 50 questions in 60 minutes; +3 for a right answer, -1 for a wrong one. 60 min / 50 = 72 s a question;
  a blind guess among four options is worth 0.25 x 3 - 0.75 x 1 = 0 on average, with one option ruled out
  1/3 x 3 - 2/3 x 1 = +1/3.

Roles (no speaker labels are spoken): NARRATOR self.N, TEACHER self.T / self.Q, STUDENT self.S.
Sarvam voices (voice ids from assets/voices), as in the other introductions:
    narrator        -> "narrator"         (shubh)
    teacher         -> "aditya_mp3_mpeg"  (aditya)
    student         -> "priya"            (priya)

Look (as the other introductions): near-black background, white text, blue and brown accents; yellow only for a
  passing highlight, green / red only for right / wrong. Latin Modern Roman (Cambria if missing).

Section map: S00 Welcome  S01 A first question  S02 Where it sits in C-CAT  S03 What this section trains
  S04 The modules ahead  S05 By the end of this section  S14 Up next
"""

import math
import os
import types

import numpy as np
from manim import (BOLD, DOWN, ITALIC, LEFT, NORMAL, PI, RIGHT, UL, UP, UR, DL, DR, AnimationGroup, Arc,
                   ArcBetweenPoints, Arrow, Circle, Circumscribe, Create, CurvedArrow, DashedLine, DashedVMobject,
                   DoubleArrow, Dot, Ellipse, FadeIn, FadeOut,
                   Group, GrowArrow, Indicate, ORIGIN, LaggedStart, Line, Rectangle, ReplacementTransform, RoundedRectangle, Square,
                   SurroundingRectangle, Text, Transform, Uncreate, VGroup, VMobject, config, linear)

from src.animation import LMSScene

# ============================================================== style ====

BG = "#101010"
FILL = "#1B1B1B"           # inside of boxes
INK = "#F5F5F5"            # main text
MUTED = "#9A9A9A"          # supporting text
BLUE = "#58C4DD"           # accent 1: key terms, data
BROWN = "#CD853F"          # accent 2: clues, things to remember
FLASH = "#FFFF00"          # a passing highlight only
GOOD = "#83C167"           # the right answer / always true
BAD = "#FC6255"            # wrong / can be false

LM_DIR = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "MiKTeX", "fonts", "opentype", "public", "lm")


def serif_font():
    """Latin Modern Roman when MiKTeX has it (registered for this run only), else Cambria."""
    try:
        import manimpango

        files = [os.path.join(LM_DIR, f"lmroman10-{style}.otf") for style in ("regular", "bold", "italic")]
        if all(os.path.exists(f) for f in files) and all(manimpango.register_font(f) for f in files):
            if "Latin Modern Roman 10" in manimpango.list_fonts():
                return "Latin Modern Roman 10"
    except Exception:
        pass
    return "Cambria"


FONT = serif_font()
MONO = "Consolas"
MIN_FONT = 22              # readable floor
TITLE = 54
HEAD = 38
BODY = 32
LABEL = 28
SMALL = 24
CODE = 24

# ============================================================= layout ====

FRAME_W = config.frame_width
FRAME_H = config.frame_height
SAFE = 0.45                                   # margin kept clear on every side
EDGE_X = FRAME_W / 2 - SAFE                   # furthest x any content may reach
TOP = FRAME_H / 2 - SAFE
FLOOR = -FRAME_H / 2 + SAFE + 0.1             # lowest y any content may reach

FACE_R = 0.36
CAST_W = 2.6 * FACE_R                         # width of one character (ring and shoulders)
HEAD_Y = 3.02                                 # centre of the scene heading
HEAD_W = FRAME_W - 2 * (SAFE + CAST_W + 0.35)        # the heading stays centred between the teacher and the student
TIMER_Y = 2.58                                # the thinking-time bar
STRIP_TOP, STRIP_BOTTOM = 2.42, 1.48          # the spoken-line strip
STRIP_Y = (STRIP_TOP + STRIP_BOTTOM) / 2
STRIP_W = 11.0
BOARD_TOP = 1.32                              # top of the board (the strip sits above it)
Q_LEFT = -EDGE_X + 0.3                        # left edge of a question on the board
ZONE_L = 0.4                                  # left edge of the diagram zone beside a question
ZONE_X = (ZONE_L + EDGE_X) / 2                # centre of that zone
WORK_X = -EDGE_X + 4.4                        # where the board starts while the side panel is pinned

NARRATOR_VOICE = "narrator"                   # Sarvam shubh_en_narration
TEACHER_VOICE = "aditya_mp3_mpeg"             # Sarvam aditya
STUDENT_VOICE = "priya"                       # Sarvam priya
VOICES = {"N": NARRATOR_VOICE, "T": TEACHER_VOICE, "S": STUDENT_VOICE}
TURN_PAUSE = 0.6               # silence after each block, so the voices never run together
STRICT_CUES = os.environ.get("LMS_STRICT_CUES") == "1"     # a check run: a cue word missing from its line is an error


# ======================================================= text helpers ====

def text(s, size=BODY, color=INK, weight=NORMAL, slant=NORMAL, font=FONT):
    return Text(s, font=font, font_size=size, color=color, weight=weight, slant=slant, disable_ligatures=True)


def code(s, size=CODE, color=INK, weight=NORMAL):
    """Program text."""
    return text(s, size, color, weight, NORMAL, MONO)


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


def fit_w(mob, max_width):
    """Layout guard: ``mob`` is never wider than ``max_width`` (its left edge stays where it is)."""
    if mob.width > max_width:
        mob.scale(max_width / mob.width, about_edge=LEFT)
    return mob


def fitted_text(s, max_width, size=BODY, color=INK, weight=NORMAL, max_lines=3, slant=NORMAL):
    """Readable text no wider than ``max_width``: as written, else wrapped, else a little smaller."""
    s = cap(s)
    for lines in range(1, max_lines + 1):
        mob = text(s if lines == 1 else wrap_lines(s, lines), size, color, weight, slant)
        if mob.width <= max_width:
            return mob
    return mob.scale(max_width / mob.width)


def phrase(*parts, buff=0.22):
    """Pieces on one line."""
    return VGroup(*parts).arrange(RIGHT, buff=buff)


def place(mob, left=None, top=None, x=None, y=None):
    """Put ``mob`` by its left edge / top edge, or by its centre."""
    if x is not None:
        mob.set_x(x)
    if y is not None:
        mob.set_y(y)
    if left is not None:
        mob.shift(RIGHT * (left - mob.get_left()[0]))
    if top is not None:
        mob.shift(UP * (top - mob.get_top()[1]))
    return mob


def line_at(s, left=0.0, y=0.0, size=LABEL, color=INK, weight=NORMAL, slant=NORMAL, font=FONT):
    """A piece of text whose LINE (not its ink) is centred on ``y``, so pieces set this way share a baseline.

    ``line_end`` is where the next piece of the same line starts."""
    mob = text(s + "|", size, color, weight, slant, font)        # the bar gives every piece the same height
    mob.shift(RIGHT * (left - mob.get_left()[0]) + UP * (y - mob.get_y()))
    bar = mob[-1]
    mob.line_end = bar.get_left()[0]
    bar.set_opacity(0.0)        # the invisible bar keeps the line height, so every piece keeps its real font size
    return mob


def para(*lines, size=LABEL, step=None, color=INK):
    """Lines of text made of pieces, so single words can be coloured or pointed at later.

    A line is a list of pieces; a piece is a string, (string, colour) or (string, colour, weight).
    Returns VGroup(lines); every line is a VGroup of its pieces."""
    step = step or size * 0.0185
    gap = size * 0.0033
    out = VGroup()
    for k, parts in enumerate(lines):
        row, x = VGroup(), 0.0
        for part in ([parts] if isinstance(parts, (str, tuple)) else parts):
            s, c, w = (part, color, NORMAL) if isinstance(part, str) else (tuple(part) + (NORMAL,))[:3]
            piece = line_at(s, x, -k * step, size, c, w)
            x = piece.line_end + gap
            row.add(piece)
        out.add(row)
    return out


def hl(mob, scale=1.12, color=FLASH):
    """Highlight a text or a shape for a moment."""
    return Indicate(mob, color=color, scale_factor=scale)


def ring(mob):
    """Highlight a block for a moment (a frame that draws itself and fades)."""
    return Circumscribe(mob, color=FLASH, buff=0.1, fade_out=True, stroke_width=5)


def up(mob):
    """Fade in, rising a little."""
    return FadeIn(mob, shift=UP * 0.15)


def side(mob):
    """Fade in, sliding in from the left."""
    return FadeIn(mob, shift=RIGHT * 0.2)


def under(mob, color=BLUE, gap=0.07):
    """A line under ``mob`` (a student's pick, a key line)."""
    return Line(mob.get_corner(DL) + DOWN * gap, mob.get_corner(DR) + DOWN * gap, color=color, stroke_width=4)


def tick(size=0.3, color=GOOD):
    t = VMobject(stroke_color=color, stroke_width=6)
    t.set_points_as_corners([np.array([-0.5, 0.0, 0.0]), np.array([-0.12, -0.4, 0.0]), np.array([0.5, 0.45, 0.0])])
    return t.scale(size)


def cross(size=0.26, color=BAD):
    return VGroup(Line(UL, DR, color=color, stroke_width=6), Line(UR, DL, color=color, stroke_width=6)).scale(size / 2)


def bullets(items, size=LABEL, buff=0.3, color=INK, max_width=None):
    """Rows of a blue dot and one line each (each row kept inside ``max_width``)."""
    rows = VGroup()
    for item in items:
        body = text(item, size, color) if isinstance(item, str) else item
        row = VGroup(Dot(radius=0.07, color=BLUE), body).arrange(RIGHT, buff=0.3)
        rows.add(fit_w(row, max_width) if max_width else row)
    return rows.arrange(DOWN, buff=buff, aligned_edge=LEFT)


def mark(label, good, size=SMALL):
    """A short verdict: a tick (green) or a cross (red), then its label."""
    sign = tick(0.24) if good else cross(0.22)
    return phrase(sign, text(label, size, GOOD if good else BAD, BOLD), buff=0.16)


def card_box(title, rows, width=9.6, color=BLUE, top=BOARD_TOP - 0.25):
    """A titled card in a frame that grows with its rows. ``card.head``, ``card.rows`` are its parts."""
    head = fit_w(text(title, LABEL, color, BOLD), width - 0.8)
    body = VGroup(*[fit_w(text(r, SMALL) if isinstance(r, str) else r, width - 0.8) for r in rows])
    body.arrange(DOWN, buff=0.3, aligned_edge=LEFT)
    inner = VGroup(head, body).arrange(DOWN, buff=0.4, aligned_edge=LEFT)
    frame = RoundedRectangle(width=width, height=inner.height + 0.8, corner_radius=0.14, stroke_color=color,
                             stroke_width=3, fill_color=FILL, fill_opacity=1.0)
    inner.move_to(frame)
    card = place(VGroup(frame, inner), x=0.0, top=top)
    card.frame, card.head, card.rows = frame, head, list(body)
    return card


# ==================================================== diagram pieces ====

class Grid(VGroup):
    """A plain table: left-aligned columns of the given widths, an optional header row with a rule.

    ``rows`` are lists of strings ("" leaves a cell empty). ``styles`` gives (colour, weight) per
    column for the body rows. ``cell(r, c)``, ``col(c)`` and ``row(r)`` return the parts."""

    def __init__(self, rows, widths, size=LABEL, row_h=0.6, header=True, styles=None, head_color=BLUE):
        super().__init__()
        self.cells = []
        total = sum(widths)
        for r, cells in enumerate(rows):
            x, line = -total / 2, []
            for c, s in enumerate(cells):
                mob = None
                if s:
                    if header and r == 0:
                        style = (head_color, BOLD)
                    else:
                        style = styles[c] if styles else (INK, NORMAL)
                    mob = fit_w(line_at(s, x, -r * row_h, size, *style), widths[c] - 0.25)
                    self.add(mob)
                line.append(mob)
                x += widths[c]
            self.cells.append(line)
        self.rule = None
        if header:
            self.rule = Line(LEFT * total / 2, RIGHT * total / 2, color=MUTED, stroke_width=2).move_to(
                DOWN * row_h * 0.52)
            self.add(self.rule)

    def cell(self, r, c):
        return self.cells[r][c]

    def col(self, c, head=True):
        return VGroup(*[row[c] for k, row in enumerate(self.cells) if row[c] is not None and (head or k)])

    def row(self, r):
        return VGroup(*[m for m in self.cells[r] if m is not None])


class Listing(VGroup):
    """A program listing: one Text per line, indentation kept, blank lines as half gaps."""

    def __init__(self, src, size=CODE, color=INK):
        super().__init__()
        unit = code("M" * 10, size).width / 10
        step, y = size * 0.0175, 0.0
        self.base, self.lit = color, None
        for raw in src.strip("\n").split("\n"):
            if not raw.strip():
                y -= step / 2
                continue
            line = code(raw.strip() + "|", size, color)        # the bar gives every line the same height
            line.move_to(UP * y).align_to(RIGHT * (len(raw) - len(raw.lstrip())) * unit, LEFT)
            line.remove(line[-1])
            self.add(line)
            y -= step
        self.lines = list(self.submobjects)

    def focus(self, i, color=FLASH):
        """Animations that light line ``i`` (None: no line) and put the last lit line back."""
        anims = []
        if self.lit is not None and self.lit != i:
            anims.append(self.lines[self.lit].animate.set_color(self.base))
        if i is not None and self.lit != i:
            anims.append(self.lines[i].animate.set_color(color))
        self.lit = i
        return anims


class Options(VGroup):
    """Answer options (a) to (d): in a row (``across``) or one under another. ``items`` are (letter, words)."""

    def __init__(self, items, size=LABEL, across=False, gap=0.7):
        super().__init__()
        self.rows = {}
        x, step = 0.0, size * 0.0195
        for k, (letter, words) in enumerate(items):
            y = 0.0 if across else -k * step
            tag = line_at(f"({letter})", x if across else 0.0, y, size, BLUE, BOLD)
            body = line_at(words, tag.line_end + size * 0.004, y, size, INK)
            row = VGroup(tag, body)
            self.rows[letter] = row
            self.add(row)
            x = row.get_right()[0] + gap

    def out(self, *letters):
        """These options go grey."""
        return [self.rows[letter].animate.set_color(MUTED) for letter in letters]


class Question(VGroup):
    """A practice question: its label, the ask (lines of pieces, see ``para``) and the options."""

    def __init__(self, label, lines, options, size=SMALL, across=True):
        super().__init__()
        self.label = text(label, SMALL, MUTED, BOLD)
        self.body = para(*lines, size=size)
        self.opts = Options(options, size, across)
        self.add(self.label, self.body, self.opts)
        self.arrange(DOWN, buff=0.16, aligned_edge=LEFT)


def side_panel(title, rows, width=4.0, color=BROWN):
    """The rule panel that stays on the left while an example is worked on the right."""
    head = fit_w(text(title, SMALL, color, BOLD), width - 0.5)
    body = VGroup(*[fit_w(text(s, SMALL), width - 0.5) for s in rows]).arrange(DOWN, buff=0.2, aligned_edge=LEFT)
    inner = VGroup(head, body).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
    frame = RoundedRectangle(width=width, height=inner.height + 0.6, corner_radius=0.12, stroke_color=color,
                             stroke_width=3, fill_color=FILL, fill_opacity=1.0)
    inner.move_to(frame)
    panel = place(VGroup(frame, inner), left=-EDGE_X, top=BOARD_TOP - 0.2)
    panel.rows = list(body)
    return panel


# ============================================================ the cast ====

SKIN = "#F2D0B0"               # characters use neutral tones plus their shirt colour
HAIR = "#4E3B2A"
LIPS = "#3A1F1F"
SHIRT_T = "#8C6239"            # the teacher wears brown
SHIRT_S = "#1C758A"            # the student wears blue
RING_ON = INK
RING_OFF = "#3A3A3A"


class Face(VGroup):
    """A drawn character: head, hair, eyes, brows, mouth and shoulders.

    ``look_to(name)`` returns the animations for a change of expression;
    ``talk(on)`` lights the ring of the speaker."""

    LOOKS = {"neutral": ("soft", "flat"), "smile": ("smile", "flat"), "happy": ("open", "up"),
             "ask": ("small", "one_up"), "think": ("flat", "down"), "confused": ("wavy", "tilt"),
             "surprised": ("o", "up"), "oops": ("frown", "tilt")}

    def __init__(self, r=FACE_R, shirt=SHIRT_T, hair="short", glasses=False, look="neutral"):
        super().__init__()
        self.r = r
        self.head = Circle(radius=r, stroke_color="#B89A7C", stroke_width=2, fill_color=SKIN, fill_opacity=1)
        self.body = Arc(radius=r * 1.3, start_angle=0, angle=PI, stroke_color=shirt, stroke_width=2,
                        fill_color=shirt, fill_opacity=1)
        self.body.next_to(self.head, DOWN, buff=-r * 0.3)
        self.ring = Circle(radius=r * 1.2, stroke_color=RING_OFF, stroke_width=3)
        extras = VGroup(Arc(radius=r, start_angle=PI * 0.1, angle=PI * 0.8, stroke_width=0, fill_color=HAIR,
                            fill_opacity=1))
        if hair == "pony":
            extras.add(Ellipse(width=r * 0.5, height=r * 0.95, stroke_width=0, fill_color=HAIR,
                               fill_opacity=1).move_to(self.at(0.95, 0.35)))
        if glasses:
            for sx in (-1, 1):
                extras.add(Circle(radius=r * 0.2, stroke_color=HAIR, stroke_width=2).move_to(self.at(sx * 0.34, 0.06)))
            extras.add(Line(self.at(-0.14, 0.06), self.at(0.14, 0.06), stroke_color=HAIR, stroke_width=2))
        self.eyes = VGroup(*[Dot(self.at(sx * 0.34, 0.06), radius=r * 0.085, color=LIPS) for sx in (-1, 1)])
        self.mouth = self._mouth("soft")
        self.brow_l, self.brow_r = self._brows("flat")
        self.add(self.body, self.ring, self.head, extras, self.eyes, self.brow_l, self.brow_r, self.mouth)
        self.now = None
        self.play_look(look)

    def at(self, x, y):
        """A point on the face, in head radii from its centre."""
        return self.head.get_center() + self.r * np.array([x, y, 0.0])

    def _mouth(self, kind):
        a, b = self.at(-0.32, -0.42), self.at(0.32, -0.42)
        if kind == "smile":
            m = ArcBetweenPoints(a, b, angle=PI / 2)
        elif kind == "soft":
            m = ArcBetweenPoints(self.at(-0.22, -0.44), self.at(0.22, -0.44), angle=PI / 4)
        elif kind == "open":
            m = ArcBetweenPoints(a, b, angle=PI * 0.85).set_fill(LIPS, 1)
        elif kind == "frown":
            m = ArcBetweenPoints(self.at(-0.26, -0.56), self.at(0.26, -0.56), angle=-PI / 2)
        elif kind == "o":
            m = Circle(radius=self.r * 0.15).move_to(self.at(0, -0.5)).set_fill(LIPS, 1)
        elif kind == "wavy":
            m = VMobject().set_points_smoothly([a, self.at(-0.1, -0.36), self.at(0.1, -0.5), b])
        elif kind == "small":
            m = Line(self.at(-0.14, -0.46), self.at(0.14, -0.46))
        else:
            m = Line(self.at(-0.24, -0.46), self.at(0.24, -0.46))
        return m.set_stroke(LIPS, 3)

    def _brows(self, kind):
        lift = 0.12 if kind == "up" else 0.0
        inner = {"down": -0.08, "tilt": 0.1}.get(kind, 0.0)
        y = 0.4 + lift
        left = Line(self.at(-0.52, y), self.at(-0.18, y + inner))
        right = Line(self.at(0.18, y + inner + (0.06 if kind == "one_up" else 0)),
                     self.at(0.52, y + (0.2 if kind == "one_up" else 0)))
        return left.set_stroke(HAIR, 3), right.set_stroke(HAIR, 3)

    def play_look(self, name):
        """Set the expression at once (before the face is on screen)."""
        mouth, brows = self.LOOKS[name]
        left, right = self._brows(brows)
        self.mouth.become(self._mouth(mouth))
        self.brow_l.become(left)
        self.brow_r.become(right)
        self.now = name
        return self

    def look_to(self, name):
        if self.now == name:
            return []
        mouth, brows = self.LOOKS[name]
        left, right = self._brows(brows)
        self.now = name
        return [self.mouth.animate.become(self._mouth(mouth)), self.brow_l.animate.become(left),
                self.brow_r.animate.become(right)]

    def talk(self, on):
        return self.ring.animate.set_stroke(RING_ON if on else RING_OFF, width=6 if on else 3)


# ====================================================== diagram pieces ====

def pill(s, color=BROWN, size=SMALL):
    """A word in a rounded frame that grows with it."""
    word = text(s, size, color, BOLD)
    frame = RoundedRectangle(width=word.width + 0.5, height=word.height + 0.36, corner_radius=0.18,
                             stroke_color=color, stroke_width=3, fill_color=FILL, fill_opacity=1.0).move_to(word)
    return VGroup(frame, word)


def node(title, color=BLUE, sub=None, width=None, size=SMALL):
    """A box of a diagram: a title (and an optional second line) in a frame that grows with them.

    ``n.frame`` is the frame, ``n.title`` the title."""
    lines = [text(title, size, color, BOLD)] + ([text(sub, MIN_FONT, INK)] if sub else [])
    body = VGroup(*lines).arrange(DOWN, buff=0.1)
    w = max(width or 0.0, body.width + 0.5)
    frame = RoundedRectangle(width=w, height=body.height + 0.4, corner_radius=0.12, stroke_color=color,
                             stroke_width=3, fill_color=FILL, fill_opacity=1.0).move_to(body)
    n = VGroup(frame, body)
    n.frame, n.title = frame, lines[0]
    return n


def link(a, b, direction=RIGHT, color=MUTED, buff=0.1, shift=0.0):
    """An arrow from the ``direction`` side of ``a`` to the facing side of ``b`` (moved sideways by ``shift``)."""
    side_shift = np.array([-direction[1], direction[0], 0.0]) * shift
    return Arrow(a.get_edge_center(direction) + side_shift, b.get_edge_center(-direction) + side_shift, buff=buff,
                 color=color, stroke_width=4, tip_length=0.18)


def cap(s):
    """On-screen labels start with a capital letter."""
    return s[:1].upper() + s[1:] if s[:1].islower() else s


def chip(s, color=BLUE, size=SMALL, width=None):
    """A short fact in a rounded frame that grows with it (left-aligned when ``width`` is given)."""
    words = text(cap(s), size, color, BOLD)
    w = width or words.width + 0.5
    frame = RoundedRectangle(width=w, height=words.height + 0.36, corner_radius=0.16, stroke_color=color,
                             stroke_width=3, fill_color=FILL, fill_opacity=1.0)
    if width:
        words.move_to(frame).align_to(frame, LEFT).shift(RIGHT * 0.25)
    else:
        words.move_to(frame)
    return VGroup(frame, words)


def roadmap(stops, top=0.95, size=MIN_FONT, row=False):
    """The stops of a lesson (or the lessons of a module), joined by arrows: up to three (or all, with ``row``) in a
    row, more in two columns that read down the left, then down the right. ``road.stops``, ``road.links``."""
    chips = VGroup(*[chip(s, BLUE, size) for s in stops])
    links = VGroup()
    if len(stops) <= 3 or row:
        chips.arrange(RIGHT, buff=0.9)
        fit_w(chips, 2 * EDGE_X - 0.4)
        links.add(*[Arrow(a.get_right(), b.get_left(), buff=0.06, color=MUTED, stroke_width=3, tip_length=0.14)
                    for a, b in zip(chips[:-1], chips[1:])])
        place(VGroup(chips, links), top=top, x=0.0)
    else:
        ncols = 2 if len(stops) <= 8 else 3
        per = -(-len(stops) // ncols)
        cols = VGroup(*[VGroup(*chips[k:k + per]).arrange(DOWN, buff=0.4, aligned_edge=LEFT)
                        for k in range(0, len(stops), per)])
        cols.arrange(RIGHT, buff=1.4 if ncols == 2 else 0.8, aligned_edge=UP)
        fit_w(cols, 2 * EDGE_X - 0.4)
        place(cols, top=top, x=0.0)
        for col in cols:
            links.add(*[Arrow(a.get_bottom(), b.get_top(), buff=0.04, color=MUTED, stroke_width=3, tip_length=0.12)
                        for a, b in zip(col[:-1], col[1:])])
        for a, b in zip(cols[:-1], cols[1:]):
            links.add(Arrow(a[-1].get_right(), b[0].get_left(), buff=0.08, color=MUTED, stroke_width=3,
                            tip_length=0.14))
    road = VGroup(chips, links)
    road.stops, road.links = chips, links
    return road


class Problem(VGroup):
    """A question card without options: its label and the ask (lines of pieces, see ``para``)."""

    def __init__(self, label, lines, size=SMALL):
        super().__init__()
        self.label = text(label, SMALL, MUTED, BOLD)
        self.body = para(*lines, size=size)
        self.opts = None
        self.add(self.label, self.body)
        self.arrange(DOWN, buff=0.16, aligned_edge=LEFT)


def card_q(lines, options=None, label="Question card", size=SMALL, across=True, letters="abcde"):
    """The exam card of scene 3: an ask of one or more lines and, if given, the options (a) to (d)."""
    lines = [[(s, BLUE)] if isinstance(s, str) else s for s in lines]
    if options:
        return Question(label, lines, list(zip(letters, options)), size, across=across)
    return Problem(label, lines, size)


def work_line(s, color=INK, size=SMALL):
    """A line of working under a card, in program text when it is mostly figures."""
    return text(s, size, color)


def tag_text(s, color=BROWN, size=MIN_FONT):
    """A short note in a frame, for a trap or a key point."""
    return chip(s, color, size)



def line_card(parts, width=6.4, size=SMALL, color=MUTED):
    """A sentence on a strip of paper: ``parts`` are the pieces of one line (see ``para``).
    ``card.frame`` is the strip, ``card.words`` the row of pieces."""
    words = para(parts, size=size)
    frame = RoundedRectangle(width=width, height=words.height + 0.34, corner_radius=0.1, stroke_color=color,
                             stroke_width=2.5, fill_color=FILL, fill_opacity=1.0)
    fit_w(words, width - 0.5)
    words.move_to(frame).align_to(frame, LEFT).shift(RIGHT * 0.25)
    card = VGroup(frame, words)
    card.frame, card.words = frame, words[0]
    return card


def slots(n, left, top, step):
    """Left-edge positions (x, y of the centre line) of ``n`` strips stacked from ``top`` down, ``step`` apart."""
    return [np.array([left, top - k * step, 0.0]) for k in range(n)]


def to_slot(card, slot):
    """The animation that moves ``card`` so its left edge and centre line sit on ``slot``."""
    return card.animate.shift(slot - np.array([card.get_left()[0], card.get_y(), 0.0]))


def text_block(n=6, width=4.8, step=0.3, color=MUTED, stroke=5):
    """A passage drawn as grey lines of text (the words are not needed): ``block[k]`` is line k."""
    widths = [1.0, 0.94, 0.98, 0.9, 0.96, 0.7, 0.92, 0.85]
    return VGroup(*[Line(ORIGIN, RIGHT * width * widths[k % len(widths)], color=color, stroke_width=stroke).shift(
        DOWN * step * k) for k in range(n)])


def clock_icon(r=0.32, color=INK):
    """A small clock face with two hands."""
    face = Circle(radius=r, stroke_color=color, stroke_width=3)
    hands = VGroup(Line(ORIGIN, UP * r * 0.7, color=color, stroke_width=3),
                   Line(ORIGIN, RIGHT * r * 0.5, color=color, stroke_width=3))
    return VGroup(face, hands)

CRUMB = "C-CAT Preparation  ›  Computer Fundamentals and Concepts of Programming"
TITLE_TEXT = "Why Computer Fundamentals and Concepts of Programming is in the Pre C-CAT"

AREAS = ["English", "Quantitative aptitude", "Reasoning", "Computer fundamentals"]
ME = 3                                        # this section's area in AREAS

STOPS = ["1. Introduction and computer organisation", "2. Number systems and data representation",
         "3. Processor, memory and storage", "4. Programming concepts"]

D = dict(
    s0_01="Welcome to the Pre C-CAT course. Before the first module of computer fundamentals and concepts of "
          "programming, one question deserves an answer: why is this subject in the course at all? The answer starts "
          "with the exam. C-CAT has three sections, A, B and C. Section A is the one every candidate takes, whatever "
          "course they apply for, and it covers four areas. Computer fundamentals is one of them.",
    hook=dict(
        heading="Same digits, different number",
        card=["What is the decimal value of the binary number 1011?"],
        shown="What is the decimal value of the binary number 1011?",
        wrong="Read as decimal: one thousand and eleven",
        work=["Place values:   8    4    2    1", "1011  =  8 + 0 + 2 + 1"],
        right="1011 in binary = 11 in decimal",
        lesson="Understand the machine before you program it",
        s1_01="A question to begin. What is the decimal value of the binary number one zero one one?",
        s1_02="Is it one thousand and eleven?",
        s1_03="That is reading it as a decimal number. In binary, each place is worth double the one to its right: "
              "eight, four, two, one. So one zero one one is eight, plus zero, plus two, plus one, which makes eleven.",
        s1_04="So the same digits mean a different number in a different system.",
        s1_05="Exactly. How a computer stores and handles data is what C-CAT checks here. This section makes sure you "
              "understand the machine before you program it.",
        cues=("binary", "thousand", "double", "plus", "eleven", "system", "machine"),
    ),
    s2_03="Seventy-two seconds, to be exact. And computer fundamentals questions are often direct, a fact, a term or a "
          "short conversion. They are quick marks, if you know them.",
    fast_cue="direct",
    fast_chip="Computer fundamentals: quick marks, if you know them",
    skills=[("Organisation", "processor, memory, storage"), ("Data", "number systems and codes"),
            ("Planning", "algorithms and flowcharts")],
    s3_01="This section builds three kinds of knowledge. How a computer is organised, its processor, memory and "
          "storage. How it represents data, in number systems and codes. And how we plan a program, with algorithms, "
          "pseudocode and flowcharts.",
    skill_cues=("organised", "represents", "plan"),
    s3_02="But Section B of the exam already has C programming. Why learn this as well?",
    uses=["What memory is", "How numbers are stored", "How to plan logic"],
    s3_03="Because this is the ground Section B stands on. Before you write C, you need to know what memory is, how "
          "numbers are stored, and how to plan your logic. The marks come first, but this ground stays with you.",
    use_cues=("memory", "stored", "logic"),
    s4_01="The section has four modules. First, introduction and computer organisation: computer basics, types of "
          "computers, and input and output. Then number systems and data representation, with conversions and computer "
          "codes. Next, processor, memory and storage. And finally, programming concepts: languages, algorithms and "
          "pseudocode, and flowcharts.",
    stop_cues=("First", "Then", "Next", "finally"),
    s4_02="So programming concepts come only at the end?",
    foot="The machine and the data first, then planning logic",
    s4_03="Yes, because by then you know the machine and the data. Planning logic is the natural last step before real "
          "programming in Section B.",
    foot_cues=("machine", "natural"),
    goals=["Explain how a computer runs a program", "Convert between number systems",
           "Trace the logic of an algorithm by hand"],
    s5_01="By the end of this section, you should be able to explain how a computer runs a program, convert between "
          "number systems with confidence, and trace the logic of an algorithm by hand, all within the time the exam "
          "allows.",
    goal_cues=("explain", "convert", "trace"),
    goal_ring="time",
    advice="Ask what each new term does inside the machine",
    s5_02="My one piece of advice: whenever you meet a new term, ask what it does inside the machine. A term you can "
          "explain is a term you will not forget.",
    first_module="Module 1, Introduction and Computer Organisation",
    next_title="Module 1: Introduction and Computer Organisation",
    next_rows=["A computer is a set of parts working together", "Input, processing, memory and output"],
    s6_01="In the next lecture, we open the first module, Introduction and Computer Organisation. Its key idea: a "
          "computer is a set of parts working together, input, processing, memory and output.",
    next_cues=("lecture", "parts", "processing"),
)


class SectionWhyVideo(LMSScene):
    lesson_title = TITLE_TEXT

    def construct(self):
        self.reset()
        for scene in (self.welcome, self.hook, self.exam, self.trains, self.journey, self.direction, self.up_next):
            scene()

    # ------------------------------------------------------ scene shortcuts --

    def reset(self):
        """State of the stage at the start of the video."""
        self.camera.background_color = BG
        self.cast = self.title_bar = self.spoken = self.talking = None
        self.faces = {}
        self.pinned = []
        self.q_now, self.q_marks = None, []

    def points(self, items, size=BODY, buff=0.4, top=BOARD_TOP - 0.4):
        """A list of bullet points, placed on the board (not shown yet)."""
        pts = bullets(items, size, buff, max_width=2 * EDGE_X - 0.4)
        place(pts, x=0.0, top=top)
        return self.fit(pts)

    def reveal(self, mobs, anchors):
        """Cues that bring ``mobs`` in one after another, each at its anchor word."""
        return [(anchor, (lambda m=m: side(m))) for anchor, m in zip(anchors, mobs)]

    def foot(self, s, color=BROWN, y=-3.05, size=LABEL, x=0.0, width=None):
        """A one-line conclusion at the bottom of the board (not shown yet)."""
        mob = fit_w(text(s, size, color, BOLD), width or 2 * EDGE_X - 0.4)
        return mob.move_to(np.array([x, y, 0.0]))

    def check(self, *mobs):
        """Layout guard for a major layout: everything inside the frame's safe area."""
        self.validator.check_in_frame(*mobs)

    # ------------------------------------------------------ stage helpers --

    def kept(self):
        """Family of what stays through a scene change: the characters, the heading and the pinned panel."""
        keep = set()
        for mob in (self.cast, self.title_bar, *self.pinned):
            if mob is not None:
                keep.update(mob.get_family())
        return keep

    def wipe(self, run_time=0.6):
        """Clear the board and the spoken line (the pinned panel stays)."""
        keep = self.kept()
        parts = [p for m in self.mobjects for p in m.family_members_with_points() if p not in keep]
        if parts:
            self.play(FadeOut(Group(*parts)), run_time=run_time)
        for mob in list(self.mobjects):
            if mob not in keep and not any(p in keep for p in mob.get_family()):
                self.remove(mob)
        self.spoken = None
        self.q_now, self.q_marks = None, []

    def heading(self, s):
        """The scene heading: a title with a blue rule, between the teacher and the student."""
        title = fit_w(text(s, HEAD, INK, BOLD), HEAD_W)
        rule = Line(LEFT, RIGHT, color=BLUE, stroke_width=3).set_width(title.width).next_to(title, DOWN, buff=0.14)
        bar = VGroup(title, rule).move_to(UP * HEAD_Y)
        anims = [FadeIn(bar, shift=DOWN * 0.2)]
        if self.title_bar is not None:
            anims.append(FadeOut(self.title_bar, shift=DOWN * 0.2))
        self.play(*anims, run_time=0.6)
        self.title_bar = bar

    def begin(self, sid, title, head):
        self.scene_start(sid, title=title)
        self.heading(head)

    def finish(self, sid):
        self.wipe()
        self.scene_end(sid)

    def the_end(self, sid):
        """The last scene: the characters and the heading leave with everything else."""
        self.cast = self.title_bar = None
        self.pinned = []
        if self.mobjects:
            self.play(FadeOut(Group(*self.mobjects)), run_time=1.0)
        self.scene_end(sid)

    def fit(self, *mobs, top=BOARD_TOP):
        """Layout guard: bring every mobject onto the board (made smaller only if it is larger than the board)."""
        width, height = 2 * EDGE_X, top - FLOOR
        for mob in mobs:
            if mob.width > width or mob.height > height:
                mob.scale(min(width / mob.width, height / mob.height))
            dx = max(0.0, -EDGE_X - mob.get_left()[0]) - max(0.0, mob.get_right()[0] - EDGE_X)
            dy = max(0.0, FLOOR - mob.get_bottom()[1]) - max(0.0, mob.get_top()[1] - top)
            mob.shift(RIGHT * dx + UP * dy)
        return mobs[0]

    # ------------------------------------------------------------ the cast --

    def opening(self, title, previous):
        """The silent opening card (where we are, what came before); then the cast comes in."""
        crumb = fit_w(text(CRUMB, SMALL, MUTED), 2 * EDGE_X)
        name = text(title, TITLE, INK, BOLD)
        fit_w(name, 2 * EDGE_X - 1.0)
        rule = Line(LEFT * 1.3, RIGHT * 1.3, color=BLUE, stroke_width=4)
        before = text(previous if previous.startswith("First") else f"Previous topic:  {previous}", LABEL, BROWN)
        card = VGroup(crumb, name, rule, before).arrange(DOWN, buff=0.4).move_to(DOWN * 0.6)
        self.fit(card)
        self.check(card)
        self.play(FadeIn(crumb), FadeIn(name, shift=UP * 0.2), Create(rule), run_time=1.0)
        self.play(FadeIn(before, shift=UP * 0.15), run_time=0.6)
        self.enter_cast()
        return card

    def enter_cast(self):
        """The teacher (top left) and the student (top right) come in and stay for the whole video."""
        t = Face(FACE_R, SHIRT_T, "short", glasses=True)
        s = Face(FACE_R, SHIRT_S, "pony")
        t.shift(UP * (TOP - t.get_top()[1]) + RIGHT * (-EDGE_X - t.get_left()[0]))
        s.shift(UP * (TOP - s.get_top()[1]) + RIGHT * (EDGE_X - s.get_right()[0]))
        self.faces = {"T": t, "S": s}
        self.cast = VGroup(t, s)
        self.play(FadeIn(t, shift=RIGHT * 0.4), FadeIn(s, shift=LEFT * 0.4), run_time=0.6)

    def speaker(self, who, look=None, other=None):
        """Show who speaks: "N" narrator (everyone listens), "T" teacher, "S" the student."""
        anims = []
        for name, face in self.faces.items():
            if name == who:
                want = look or "smile"
            elif who != "N":
                want = other or "neutral"
            else:
                want = "neutral"
            anims += face.look_to(want)
        if self.talking != who:
            anims += [self.faces[name].talk(name == who) for name in (self.talking, who) if name in self.faces]
            self.talking = who
        if anims:
            self.play(*anims, run_time=0.25)

    def show_line(self, who, s):
        """The strip under the heading: a teacher question or a student line (None clears it)."""
        new = None
        if s:
            new = fitted_text(s, STRIP_W, LABEL, INK, max_lines=2, slant=NORMAL if who == "T" else ITALIC)
            if new.height > STRIP_TOP - STRIP_BOTTOM:
                new.scale((STRIP_TOP - STRIP_BOTTOM) / new.height)
            new.move_to(UP * STRIP_Y)
        anims = ([FadeOut(self.spoken)] if self.spoken is not None else []) + ([FadeIn(new)] if new is not None else [])
        if anims:
            self.play(*anims, run_time=0.3)
        self.spoken = new

    def countdown(self, seconds):
        """Thinking / reading time: a bar under the heading runs out."""
        bar = Line(LEFT * 1.6, RIGHT * 1.6, color=FLASH, stroke_width=5).move_to(UP * TIMER_Y)
        self.play(FadeIn(bar), run_time=0.3)
        self.play(Uncreate(bar), run_time=max(0.5, seconds - 0.3), rate_func=linear)

    # -------------------------------------------- questions on the board --

    def show_question(self, q):
        """Put question ``q`` on the board, in place of the question (and its marks) that is there.

        Only what is on screen fades out: a mark registered with ``keep`` but not shown yet stays hidden and
        waits for its own cue (fading out an unseen mobject would first draw it)."""
        old = [m for m in (self.q_now, *self.q_marks) if m is not None]
        on_screen = {id(f) for m in self.mobjects for f in m.get_family()}
        shown, seen = [], set()
        for m in old:
            for f in m.get_family():
                if id(f) in on_screen and f.has_points() and id(f) not in seen:
                    seen.add(id(f))
                    shown.append(f)
        pending = [m for m in self.q_marks if not any(id(f) in on_screen for f in m.get_family())]
        self.check(q)
        anims = [FadeIn(q, shift=UP * 0.15)] + ([FadeOut(Group(*shown))] if shown else [])
        self.play(*anims, run_time=0.6)
        self.q_now, self.q_marks = q, pending

    def keep(self, mob):
        """A mark that belongs to the question on the board: it leaves with the question."""
        self.q_marks = self.q_marks + [mob]
        return mob

    def pick(self, q, letter, color=BLUE):
        """A choice: a line under the option; it leaves with the question."""
        line = self.keep(under(q.opts.rows[letter], color))
        return Create(line)

    def yes(self, q, letter):
        """The answer: green, with a tick; the other options go grey. The tick leaves with its question."""
        row = q.opts.rows[letter]
        sign = self.keep(tick(0.24).next_to(row, RIGHT, buff=0.14))
        others = [k for k in q.opts.rows if k != letter]
        return [row.animate.set_color(GOOD), FadeIn(sign, scale=0.6), *q.opts.out(*others)]

    # ------------------------------------------------- narration drivers --

    def cue(self, n, word):
        """Wait for ``word`` (or ``(word, occurrence)``) in narration ``n``."""
        spoken, occ = (word, 1) if isinstance(word, str) else word
        try:
            self.at_word(n, spoken, occ)
        except ValueError:
            if STRICT_CUES:
                raise
            # the aligner may hear a word differently: carry on

    def run(self, n, cues, think=0.0):
        """Play ``(word, what)`` pairs in spoken order, then hold until ``n`` ends.

        ``what`` is an animation, a list of animations, or a function that returns
        one (or plays things itself and returns None). ``think`` seconds of the
        pause after ``n`` are shown as a countdown."""
        for word, what in cues:
            if word:
                self.cue(n, word)
            if isinstance(what, (types.FunctionType, types.MethodType)):
                what = what()
            anims = self.flat(what) if what is not None else []
            if anims:
                self.play(*anims)
        if think:
            self.wait_for_narration(n, include_pause=False)
            self.countdown(think)
        self.wait_for_narration(n)
        return n

    @classmethod
    def flat(cls, what):
        """Animations from a single animation or a (nested) list of them."""
        if what is None:
            return []                   # a cue function that played its own animation
        if not isinstance(what, (list, tuple)):
            return [what]
        return [a for item in what for a in cls.flat(item)]

    def say(self, who, nid, spoken, cues, look=None, other=None, shown=None, think=0.0):
        self.speaker(who, look, other)
        self.show_line(who, shown)
        n = self.narrate(id=nid, text=spoken, voice=VOICES[who], subtitle=True,
                         pause_after=think if think else TURN_PAUSE)
        return self.run(n, cues, think)

    def N(self, nid, spoken, *cues):
        """Narrator: introduces, connects, sums up. Everyone listens."""
        return self.say("N", nid, spoken, cues)

    def T(self, nid, spoken, *cues, look="smile", other=None, think=0.0, shown=None):
        """Teacher statement (``shown``: also put a line in the strip)."""
        return self.say("T", nid, spoken, cues, look, other, shown, think)

    def Q(self, nid, spoken, *cues, shown=None, look="ask", other="think", think=0.0):
        """Teacher question: spoken, and shown in the strip."""
        return self.say("T", nid, spoken, cues, look, other, shown or spoken, think)

    def S(self, nid, spoken, *cues, shown=None, look="smile", other=None):
        """A student line: the student's own voice, shown in the strip."""
        return self.say("S", nid, spoken, cues, look, other, shown or spoken)

    def recap_scene(self, previous, card_title, rows, nid, spoken, anchors, width=10.0):
        """S00: the opening card, then the recap card of the previous lecture, row by row at its anchors."""
        self.scene_start("S00_previously", title="Previously")
        card = self.opening(self.lesson_title, previous)
        self.heading("Previously")
        recap = card_box(card_title, rows, width=width, top=BOARD_TOP - 0.45)
        self.check(recap)
        cues = [(anchors[0], lambda: [FadeOut(card), FadeIn(recap.frame), up(recap.head)])]
        cues += [(a, (lambda r=r: side(r))) for a, r in zip(anchors[1:-1], recap.rows)]
        cues += [(anchors[-1], lambda: FadeOut(recap, shift=LEFT * 1.5))]
        self.N(nid, spoken, *cues)
        self.finish("S00_previously")

    def up_next_scene(self, title, rows, nid, spoken, anchors, width=10.4):
        """The closing card of the next lecture: it slides in, then its rows appear at their anchors."""
        self.begin("S14_up_next", "Up Next", "Up next")
        nxt = card_box(title, rows, width=width, top=BOARD_TOP - 0.5)
        self.check(nxt)
        cues = [(anchors[0], lambda: [FadeIn(nxt.frame, shift=LEFT * 1.5), FadeIn(nxt.head, shift=LEFT * 1.5)])]
        cues += [(a, (lambda r=r: side(r))) for a, r in zip(anchors[1:], nxt.rows)]
        self.N(nid, spoken, *cues)
        self.the_end("S14_up_next")

    def start_scene(self, section, nid, spoken, anchors):
        """S00 for the first lecture of a section: no recap, a blank section road with this lecture as its first stop."""
        self.scene_start("S00_previously", title="Section Start")
        card = self.opening(self.lesson_title, "First lecture of this section")
        self.heading("Section start")
        label = fit_w(text(section, LABEL, BLUE, BOLD), 2 * EDGE_X - 0.4)
        first = chip(self.lesson_title, GOOD, SMALL)
        blanks = VGroup(*[chip("?", MUTED, SMALL) for _ in range(3)])
        row = VGroup(first, *blanks).arrange(RIGHT, buff=0.7)
        fit_w(row, 2 * EDGE_X - 0.4)
        place(row, x=0.0, y=-0.5)
        place(label, x=0.0, y=0.6)
        links = VGroup(*[Arrow(a.get_right(), b.get_left(), buff=0.06, color=MUTED, stroke_width=3, tip_length=0.14)
                         for a, b in zip(row[:-1], row[1:])])
        self.check(label, row)
        self.N(nid, spoken,
               (anchors[0], lambda: [FadeOut(card), FadeIn(label, shift=DOWN * 0.1), FadeIn(blanks), Create(links)]),
               (anchors[1], lambda: [FadeIn(first, scale=0.9)]),
               (anchors[2], lambda: ring(first)))
        self.finish("S00_previously")

    def light(self, road, k=0):
        """Stop ``k`` of a road turns green (frame and words); the others dim."""
        stop = road.stops[k]
        return [stop[0].animate.set_stroke(GOOD, width=4), stop[1].animate.set_color(GOOD),
                *[s.animate.set_opacity(0.35) for j, s in enumerate(road.stops) if j != k]]

    def show_card(self, q):
        """The exam card comes onto the board (it leaves with the next wipe)."""
        self.show_question(q)

    def board(self, *mobs):
        """Layout guard for the pieces of a scene: on the board and inside the frame."""
        for mob in mobs:
            self.fit(mob)
        self.check(*mobs)
        return mobs


    # ========================================================== 0. WELCOME ==

    def welcome(self):
        self.scene_start("S00_welcome", title="Section Start")
        card = self.opening(self.lesson_title, "First lecture of this section")
        self.heading("Why this section")
        secs = VGroup(*[node(f"Section {k}", BLUE if k == "A" else MUTED, width=2.8, size=LABEL) for k in "ABC"])
        secs.arrange(RIGHT, buff=0.9)
        place(secs, x=0.0, top=BOARD_TOP - 0.2)
        every = chip("Every candidate takes Section A", BROWN, MIN_FONT)
        place(every, x=0.0, y=-0.45)
        covers = text("Section A covers four areas", SMALL, MUTED, BOLD)
        place(covers, x=0.0, y=-1.35)
        areas = VGroup(*[chip(s, MUTED, MIN_FONT) for s in AREAS]).arrange(RIGHT, buff=0.35)
        place(areas, x=0.0, y=-2.25)
        lit = chip(AREAS[ME], BROWN, MIN_FONT).move_to(areas[ME])
        self.board(secs, every, covers, areas)
        self.check(lit)

        self.N("s0_01", D["s0_01"],
               ("three", lambda: [FadeOut(card), LaggedStart(*[FadeIn(s, shift=UP * 0.15) for s in secs], lag_ratio=0.3)]),
               ("every", lambda: [ring(secs[0]), up(every)]),
               ("covers", lambda: [FadeIn(covers), LaggedStart(*[FadeIn(a) for a in areas], lag_ratio=0.2)]),
               ("them", lambda: [ReplacementTransform(areas[ME], lit)]))
        self.finish("S00_welcome")

    # ============================================================ 1. HOOK ====

    def hook(self):
        h = D["hook"]
        self.begin("S01_hook", "A First Question", h["heading"])
        q = place(card_q(h["card"], label="Question card"), left=Q_LEFT, top=BOARD_TOP - 0.1)
        wrong = phrase(cross(0.22), chip(h["wrong"], BAD, MIN_FONT), buff=0.18)
        place(wrong, left=Q_LEFT, y=-0.55)
        work = VGroup(*[text(s, SMALL, INK) for s in h["work"]]).arrange(DOWN, buff=0.25, aligned_edge=LEFT)
        place(work, left=Q_LEFT + 0.1, top=-1.05)
        right = phrase(tick(0.24), chip(h["right"], GOOD, MIN_FONT), buff=0.18)
        place(right, left=Q_LEFT, y=-2.45)
        lesson = chip(h["lesson"], BROWN, MIN_FONT)
        place(lesson, left=Q_LEFT, y=-3.12)
        self.board(q, wrong, work, right, lesson)

        self.Q("s1_01", h["s1_01"], (h["cues"][0], lambda: self.show_card(q)), shown=h["shown"])
        self.S("s1_02", h["s1_02"], (h["cues"][1], lambda: side(wrong)), look="smile")
        self.T("s1_03", h["s1_03"],
               (h["cues"][2], lambda: [wrong.animate.set_opacity(0.4), side(work[0])]),
               (h["cues"][3], lambda: side(work[1])),
               (h["cues"][4], lambda: side(right)), look="smile")
        self.S("s1_04", h["s1_04"], (h["cues"][5], lambda: hl(right, 1.06)), look="think")
        self.T("s1_05", h["s1_05"], (h["cues"][6], lambda: up(lesson)), look="happy")
        self.finish("S01_hook")

    # ===================================================== 2. THE EXAM ====

    def exam(self):
        self.begin("S02_exam", "Where It Sits in C-CAT", "Where it sits in C-CAT")
        panel = side_panel("C-CAT Section A", ["50 questions", "60 minutes", "+3 for a right answer",
                                                "-1 for a wrong answer"], width=4.4, color=BLUE)
        frame, inner = panel
        head, rows = inner[0], panel.rows
        col = -1.5
        clock = phrase(clock_icon(0.26, BROWN), text("72 seconds per question", SMALL, BROWN, BOLD), buff=0.25)
        place(clock, left=col, top=BOARD_TOP - 0.25)
        fast = fit_w(chip(D["fast_chip"], BLUE, MIN_FONT), EDGE_X - col)
        place(fast, left=col, y=-0.35)
        blind = fit_w(chip("Blind guess among four: nothing gained on average", MUTED, MIN_FONT), EDGE_X - col)
        place(blind, left=col, y=-1.6)
        odds = fit_w(chip("Rule out one option: the odds turn your way", GOOD, MIN_FONT), EDGE_X - col)
        place(odds, left=col, y=-2.5)
        self.board(panel, clock, fast, blind, odds)

        self.T("s2_01", "In C-CAT, Section A has fifty questions to be answered in sixty minutes. Every right answer earns "
                        "three marks, and every wrong answer takes one mark away.",
               ("Section", lambda: [FadeIn(frame), FadeIn(head)]), ("fifty", lambda: side(rows[0])),
               ("sixty", lambda: side(rows[1])), ("three", lambda: side(rows[2])), ("away", lambda: side(rows[3])))
        self.S("s2_02", "Sixty minutes for fifty questions. That is barely more than a minute each.",
               ("minute", lambda: up(clock)), look="surprised")
        self.T("s2_03", D["s2_03"], ("exact", lambda: ring(clock)), (D["fast_cue"], lambda: side(fast)))
        self.S("s2_04", "And if I am not sure of an answer, should I just guess?", look="ask")
        self.T("s2_05", "A blind guess among four options gains nothing on average. Rule out even one wrong option, and the "
                        "odds turn in your favour. That is why real knowledge of this section pays.",
               ("blind", lambda: side(blind)), ("Rule", lambda: side(odds)), ("pays", lambda: ring(odds)), look="happy")
        self.finish("S02_exam")

    # ================================================== 3. WHAT IT TRAINS ==

    def trains(self):
        self.begin("S03_trains", "What This Section Trains", "What this section trains")
        nodes = VGroup(*[node(t, BLUE, sub=s, size=SMALL) for t, s in D["skills"]]).arrange(RIGHT, buff=0.45)
        fit_w(nodes, 2 * EDGE_X)
        place(nodes, x=0.0, top=BOARD_TOP - 0.25)
        beyond = text("Beyond the exam", SMALL, BROWN, BOLD)
        place(beyond, x=0.0, y=-1.0)
        uses = VGroup(*[chip(s, BROWN, MIN_FONT) for s in D["uses"]]).arrange(RIGHT, buff=0.35)
        place(uses, x=0.0, y=-1.9)
        self.board(nodes, beyond, uses)

        self.T("s3_01", D["s3_01"], *[(w, (lambda n=n: up(n))) for w, n in zip(D["skill_cues"], nodes)])
        self.S("s3_02", D["s3_02"], ("exam", lambda: up(beyond)), look="ask")
        self.T("s3_03", D["s3_03"], *[(w, (lambda u=u: side(u))) for w, u in zip(D["use_cues"], uses)],
               ("stays", lambda: ring(uses)), look="happy")
        self.finish("S03_trains")

    # ================================================ 4. THE MODULES =======

    def journey(self):
        self.begin("S04_journey", "The Modules Ahead", "The modules ahead")
        road = roadmap(STOPS, top=BOARD_TOP - 0.3)
        stops = road.stops
        foot = chip(D["foot"], BROWN, MIN_FONT)
        place(foot, x=0.0, y=-3.0)
        self.board(road, foot)

        self.T("s4_01", D["s4_01"], ("modules", lambda: Create(road.links)), *self.reveal(stops, D["stop_cues"]))
        self.S("s4_02", D["s4_02"], look="think")
        self.T("s4_03", D["s4_03"], (D["foot_cues"][0], lambda: up(foot)), (D["foot_cues"][1], lambda: ring(road)),
               look="happy")
        self.finish("S04_journey")

    # ================================================ 5. BY THE END =========

    def direction(self):
        self.begin("S05_direction", "By the End of This Section", "By the end of this section")
        goals = bullets(D["goals"], LABEL, 0.35, max_width=2 * EDGE_X - 0.4)
        place(goals, left=-EDGE_X + 0.6, top=BOARD_TOP - 0.3)
        advice = chip(D["advice"], BROWN, MIN_FONT)
        place(advice, x=0.0, y=-1.55)
        first = chip("Next: " + D["first_module"], BLUE, MIN_FONT)
        place(first, x=0.0, y=-2.6)
        self.board(goals, advice, first)

        self.T("s5_01", D["s5_01"], *self.reveal(goals, D["goal_cues"]), (D["goal_ring"], lambda: ring(goals)))
        self.T("s5_02", D["s5_02"], ("advice", lambda: up(advice)))
        self.T("s5_03", "So let us begin where every skill in this section begins, with the first module.",
               ("first", lambda: up(first)), look="happy")
        self.finish("S05_direction")

    # =============================================== UP NEXT ===============

    def up_next(self):
        self.up_next_scene(D["next_title"], D["next_rows"], "s6_01", D["s6_01"], D["next_cues"], width=12.6)

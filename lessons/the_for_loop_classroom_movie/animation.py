"""
animation.py for the LMS video generator.

Course : CDAC C-CAT Preparation
Video  : The for Loop - The Classroom Movie
Source : C:/New folder/for-loop-classroom-script.md

Look (same system as "Lists - The Classroom Movie"):
  - near-black background, white text, ONE blue and ONE brown accent;
    yellow only for a passing highlight, green / red only for right / wrong
  - the three parts of a for header keep one colour each in every scene, as the script names them:
    initialization green, condition blue, update orange (the brown accent)
  - text in Latin Modern Roman (from the MiKTeX folder on this machine; Cambria if it is missing),
    code in Consolas
  - sizes: title 54, heading 38, body 32, label 28, small 24, code 24 (28 for a hero line),
    pinned code 22; nothing below 22

Roles (the script has no speaker labels on most lines; every line was assigned by meaning):
  NARRATOR  transitions only                      self.N   voice "vijay"
  TEACHER   Ms. Rao: teaches, asks, guides        self.T   voice "ritu"
  STUDENT   Aarav: quick, answers first           self.A   voice "aditya"
  STUDENT   Meera: methodical, traces on paper    self.M   voice "kavya"
  STUDENT   Kabir: quiet, asks the real question  self.K   voice "prasad"
  The role is carried by the method and by VOICES / ROLES; the text handed to narrate() is the
  dialogue only. Stage directions are not spoken: they are the visuals.
  Spoken text uses words ("i less than or equal to n"); the board shows the code.

Screen zones:
  left column   Ms. Rao standing by the board (her desk is below; she sits there when a student
                has the marker)
  top band      scene heading
  board         the teaching space (BOARD_L..BOARD_R, BOARD_BOTTOM..BOARD_TOP)
  right column  the pinned panel: parked questions and the rules still in use; it survives scene changes
  bottom band   Aarav, Meera and Kabir at their desks

Section map:
  S01 One Row Too Many   S02 One Line   S03 What the Exam Does With One Line   S04 Four Different Answers
  S05 Three Parts and a Body   S06 The Order Nobody Reads Correctly   S07 Counting Without Tracing
  S08 What Exactly Is the Body?   S09 Back to the Board   S10 Choosing the Loop   S11 One Line, Three Habits
"""

import math
import os
import types

import numpy as np
from manim import *

from src.animation import LMSScene

# ============================================================== style ====

BG = "#101010"
FILL = "#1B1B1B"           # inside of boxes
INK = "#F5F5F5"            # main text
MUTED = "#9A9A9A"          # supporting text
EDGE = "#3A3A3A"           # quiet lines
FAINT = "#5A5A5A"          # placeholder lines
BLUE = "#58C4DD"           # accent 1: the condition, key terms
BROWN = "#CD853F"          # accent 2: the update (the script's "orange"), things to remember
GREEN = "#83C167"          # the initialization; also "right"
FLASH = "#FFFF00"          # a passing highlight only
GOOD = GREEN               # the right answer, a value that passes
BAD = "#FC6255"            # wrong, false, the value that fails

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
MIN_FONT = 22              # readable floor: text is never shrunk below this
TITLE = 54
HEAD = 38
BODY = 32
LABEL = 28
SMALL = 24
CODE = 24
CODE_BIG = 28              # a hero line of code
PIN_CODE = 22              # code inside a pinned card

# ============================================================= layout ====

FRAME_W = config.frame_width
FRAME_H = config.frame_height
SAFE = 0.45                                   # margin kept clear on every side
EDGE_X = FRAME_W / 2 - SAFE                   # furthest x any content may reach
TOP = FRAME_H / 2 - SAFE
FLOOR = -FRAME_H / 2 + SAFE + 0.1             # lowest y any content may reach

BOARD_L, BOARD_R = -5.1, 2.3                  # the board, while the pinned panel is in use
BOARD_X = (BOARD_L + BOARD_R) / 2
BOARD_TOP, BOARD_BOTTOM = 2.75, -1.5
CODE_X = BOARD_L + 0.2                        # usual left edge of code on the board
HEAD_Y = 3.2                                  # centre of the scene heading
HEAD_W = BOARD_R - BOARD_L - 0.2
TIMER_Y = 2.81                                # the thinking-time bar

PANEL_L, PANEL_R = 2.55, EDGE_X               # the pinned panel (right column)
PIN_W = PANEL_R - PANEL_L
PIN_PAD = 0.1
PIN_GAP = 0.14

STAGE_Y = -1.72                               # floor line of the board platform (Ms. Rao's feet)
TEACHER_X = -6.0
SEATS = {"A": -3.75, "M": -1.4, "K": 0.95}

# ============================================================== roles ====

ROLES = {"N": "narrator", "T": "teacher", "A": "student", "M": "student", "K": "student"}
VOICES = {"N": "vijay", "T": "ritu", "A": "aditya", "M": "kavya", "K": "prasad"}
TURN_PAUSE = 0.6               # silence after each block, so the voices never run together

SKIN = "#F2D0B0"               # characters use neutral tones plus their shirt colour
SKIN_EDGE = "#B89A7C"
HAIR = "#4E3B2A"
LIPS = "#3A1F1F"
CLOTH = "#5B544C"
SHOE = "#8A8178"
WOOD = "#241F1B"
WOOD_EDGE = "#7A6A58"
CAST = {
    "T": {"name": "Ms. Rao", "shirt": "#8C6239", "hair": "bun", "glasses": True, "r": 0.27, "torso": 3.9, "desk": 4.6},
    "A": {"name": "Aarav", "shirt": "#1C758A", "hair": "tuft", "r": 0.26},
    "M": {"name": "Meera", "shirt": "#8E5572", "hair": "pony", "r": 0.26},
    "K": {"name": "Kabir", "shirt": "#6B6FA8", "hair": "curls", "r": 0.26},
}


# ======================================================= text helpers ====

def text(s, size=BODY, color=INK, weight=NORMAL, slant=NORMAL, font=FONT):
    return Text(s, font=font, font_size=size, color=color, weight=weight, slant=slant, disable_ligatures=True)


def code(s, size=CODE, color=INK, weight=NORMAL):
    """Program text, variable names and values."""
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


def fitted_text(s, max_width, size=BODY, color=INK, weight=NORMAL, max_lines=3, slant=NORMAL):
    """Readable text no wider than ``max_width``: as written, else wrapped, else a little smaller.

    Never below MIN_FONT; if that is not enough it fails loudly."""
    for lines in range(1, max_lines + 1):
        mob = text(s if lines == 1 else wrap_lines(s, lines), size, color, weight, slant)
        if mob.width <= max_width:
            return mob
    if size * max_width / mob.width >= MIN_FONT:
        return mob.scale(max_width / mob.width)
    raise ValueError(f"Text {s!r} cannot fit {max_width:.2f} units at a readable size; shorten it.")


def phrase(*parts, buff=0.22):
    """Text and code pieces on one line."""
    return VGroup(*parts).arrange(RIGHT, buff=buff)


def column(*mobs, buff=0.25):
    """Mobjects under one another, left edges aligned."""
    return VGroup(*mobs).arrange(DOWN, buff=buff, aligned_edge=LEFT)


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


def hl(mob, scale=1.12):
    """Highlight a text or an arrow for a moment."""
    return Indicate(mob, color=FLASH, scale_factor=scale)


def ring(mob, color=FLASH):
    """Highlight a box for a moment (a frame that draws itself and fades)."""
    return Circumscribe(mob, color=color, buff=0.1, fade_out=True, stroke_width=5)


def tick(size=0.3, color=GOOD):
    t = VMobject(stroke_color=color, stroke_width=6)
    t.set_points_as_corners([np.array([-0.5, 0.0, 0.0]), np.array([-0.12, -0.4, 0.0]), np.array([0.5, 0.45, 0.0])])
    return t.scale(size)


def cross(size=0.3, color=BAD):
    return VGroup(Line(UL, DR, color=color, stroke_width=6), Line(UR, DL, color=color, stroke_width=6)).scale(size / 2)


def strike(mob, color=BAD):
    """A line through ``mob`` (draw it with Create)."""
    return Line(mob.get_left() + LEFT * 0.08, mob.get_right() + RIGHT * 0.08, color=color, stroke_width=3)


def arrow(a, b, color=MUTED, width=4, tip=0.2):
    return Arrow(np.array(a, dtype=float), np.array(b, dtype=float), buff=0, color=color, stroke_width=width,
                 tip_length=tip)


def tag(s, color=BLUE, size=SMALL, mono=False):
    """A short label in a rounded outline."""
    label = (code if mono else text)(s, size, color)
    box = RoundedRectangle(width=label.width + 0.36, height=label.height + 0.26, corner_radius=0.1, stroke_color=color,
                           stroke_width=2, fill_color=FILL, fill_opacity=1)
    return VGroup(box, label.move_to(box))


def bullets(items, size=LABEL, buff=0.25):
    """Rows of a blue dot and one line each. ``items`` are strings or ready-made mobjects."""
    rows = VGroup()
    for item in items:
        body = text(item, size) if isinstance(item, str) else item
        rows.add(VGroup(Dot(radius=0.07, color=BLUE), body).arrange(RIGHT, buff=0.3))
    return rows.arrange(DOWN, buff=buff, aligned_edge=LEFT)


def numbered(items, size=BODY, buff=0.4):
    """Rows of a blue number and one line each."""
    return column(*[phrase(text(f"{k}.", size, BLUE, BOLD), text(s, size)) for k, s in enumerate(items, 1)], buff=buff)


def pin_card(*rows, color=MUTED, buff=0.08):
    """A card of the pinned panel: rows in a frame of the panel's width (``.frame``, ``.body``)."""
    body = VGroup(*rows).arrange(DOWN, buff=buff, aligned_edge=LEFT)
    if body.width > PIN_W - 2 * PIN_PAD + 1e-6:
        raise ValueError(f"Pinned card is {body.width:.2f} wide; the panel holds {PIN_W - 2 * PIN_PAD:.2f}.")
    frame = RoundedRectangle(width=PIN_W, height=body.height + 2 * PIN_PAD, corner_radius=0.1, stroke_color=color,
                             stroke_width=2, fill_color=FILL, fill_opacity=1)
    body.move_to(frame).shift(RIGHT * (frame.get_left()[0] + PIN_PAD - body.get_left()[0]))
    card = VGroup(frame, body)
    card.frame, card.body = frame, body
    return card


# ==================================================== diagram pieces ====

class Listing(VGroup):
    """A program listing: one Text per line, indentation kept, blank lines as half gaps.

    ``part(i, "i <= n")`` is the piece of line ``i`` that shows that text."""

    def __init__(self, src, size=CODE, color=INK):
        super().__init__()
        unit = code("M" * 10, size).width / 10
        step, y = size * 0.0175, 0.0
        self.base, self.lit, self.unit = color, None, unit
        self.raws = []
        for raw in src.strip("\n").split("\n"):
            if not raw.strip():
                y -= step / 2
                continue
            line = code(raw.strip() + "|", size, color)        # the bar gives every line the same height
            line.move_to(UP * y).align_to(RIGHT * (len(raw) - len(raw.lstrip())) * unit, LEFT)
            line.remove(line[-1])
            self.add(line)
            self.raws.append(raw.strip())
            y -= step
        self.lines = list(self.submobjects)

    def part(self, i, sub, nth=1):
        """The glyphs of the ``nth`` ``sub`` in line ``i`` (the whole line if the glyphs cannot be counted)."""
        raw, line = self.raws[i], self.lines[i]
        at = -1
        for _ in range(nth):
            at = raw.index(sub, at + 1)
        if len(line.submobjects) == len(raw):                       # one glyph per character, spaces included
            return line[at:at + len(sub)]
        if len(line.submobjects) == len(raw.replace(" ", "")):      # spaces carry no glyph
            a = len(raw[:at].replace(" ", ""))
            return line[a:a + len(sub.replace(" ", ""))]
        return line

    def paint_for(self, i, init, cond, step):
        """Colour the three parts of the for header on line ``i``; returns them."""
        parts = (self.part(i, init), self.part(i, cond), self.part(i, step))
        for piece, color in zip(parts, (GREEN, BLUE, BROWN)):
            piece.set_color(color)
        return parts

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
    """Answer options A to D. ``items`` are (letter, value, is_code)."""

    def __init__(self, items, size=LABEL, across=False, buff=0.3):
        super().__init__()
        self.rows = {}
        for letter, value, is_code in items:
            row = VGroup(text(letter + ".", size, BLUE, BOLD), (code if is_code else text)(value, size, INK))
            row.arrange(RIGHT, buff=0.3)
            self.rows[letter] = row
            self.add(row)
        self.across = across
        if across:
            self.arrange(RIGHT, buff=0.8)
        else:
            self.arrange(DOWN, buff=buff, aligned_edge=LEFT)

    def right(self, letter):
        """The answer turns green with a tick; the other options go grey."""
        row = self.rows[letter]
        mark = tick().next_to(row, UP, buff=0.14) if self.across else tick().next_to(row, RIGHT, buff=0.22)
        return ([row.animate.set_color(GOOD), FadeIn(mark, scale=0.6)]
                + [r.animate.set_color(MUTED) for name, r in self.rows.items() if name != letter])

    def strike(self, letter):
        return Create(strike(self.rows[letter]))


class Table(VGroup):
    """A trace table: column heads above a rule. ``put(r, c, mob)`` centres ``mob`` in a cell."""

    def __init__(self, heads, widths, left, top, row_h=0.48):
        super().__init__()
        self.widths, self.left, self.top, self.row_h = widths, left, top, row_h
        for c, head in enumerate(heads):
            self.add(head.move_to(self.spot(-1, c)))
        y = top - row_h
        self.add(Line([left, y, 0], [left + sum(widths), y, 0], color=MUTED, stroke_width=2))

    def spot(self, r, c):
        x = self.left + sum(self.widths[:c]) + self.widths[c] / 2
        return np.array([x, self.top - self.row_h * (r + 1.5), 0.0])

    def put(self, r, c, mob):
        return mob.move_to(self.spot(r, c))


class Question(VGroup):
    """A practice question at full board width: the program on the left, the options on the right."""

    def __init__(self, number, src, options):
        super().__init__()
        self.prog = place(Listing(src), left=CODE_X, top=BOARD_TOP - 0.05)
        self.label = phrase(text(f"Practice question {number}", SMALL, BLUE, BOLD), text("C-CAT style", SMALL, MUTED))
        self.ask = text("What is the output?", BODY, INK, BOLD)
        self.opts = Options(options, BODY)
        self.side = column(self.label, self.ask, self.opts, buff=0.35)
        place(self.side, left=self.prog.get_right()[0] + 0.7, y=(BOARD_TOP + BOARD_BOTTOM) / 2)
        self.picks = VGroup()                    # what the students add: their names, a ring, an arrow
        self.add(self.prog, self.side)

    def everything(self):
        return VGroup(self.prog, self.side, self.picks)


# ============================================================ the cast ====

def slab(width, top, bottom, color, radius=0.0):
    """A filled block between two points (top centre, bottom centre)."""
    height = top[1] - bottom[1]
    shape = (RoundedRectangle(width=width, height=height, corner_radius=radius) if radius
             else Rectangle(width=width, height=height))
    return shape.set_stroke(width=0).set_fill(color, 1).move_to((top + bottom) / 2)


class Person(VGroup):
    """A full-body character: head, hair, face, torso, two arms, two legs. Seated ones have a desk
    with their name on it.

    ``look_to(name)`` changes the expression, ``pose_to(name)`` moves the arms (both return
    animations); ``voice_mark()`` is the mark drawn beside whoever is speaking."""

    LOOKS = {"neutral": ("soft", "flat"), "talk": ("say", "flat"), "smile": ("smile", "flat"),
             "happy": ("open", "up"), "ask": ("say", "one_up"), "think": ("flat", "down"),
             "confused": ("wavy", "tilt"), "surprised": ("o", "up"), "oops": ("frown", "tilt")}
    # hands (left, right), in head radii from the centre of the head
    SIT = {"rest": ((-0.85, -2.15), (0.85, -2.15)), "raise": ((-1.75, 0.8), (0.85, -2.15)),
           "point": ((-2.0, 0.2), (0.85, -2.15)), "think": ((-0.85, -2.15), (0.5, -1.08)),
           "write": ((-0.45, -2.15), (0.35, -2.15))}
    STAND = {"rest": ((-1.45, -4.0), (1.45, -4.0)), "point": ((-1.45, -4.0), (3.1, 0.0)),
             "low": ((-1.45, -4.0), (3.0, -1.6)), "offer": ((-1.45, -4.0), (2.6, -2.0)),
             "open": ((-2.0, -2.6), (2.0, -2.6))}

    def __init__(self, who, stance="stand", look="neutral"):
        super().__init__()
        spec = CAST[who]
        r, shirt = spec["r"], spec["shirt"]
        self.who, self.r, self.seated = who, r, stance == "sit"
        self.side = 1 if self.seated else -1          # side of the head where the voice mark goes
        self.poses, self.pose, self.now = (self.SIT if self.seated else self.STAND), "rest", None
        self.head = Circle(radius=r, stroke_color=SKIN_EDGE, stroke_width=2, fill_color=SKIN, fill_opacity=1)
        P = self.at

        if self.seated:
            half = spec.get("desk", 6.0) / 2
            torso = slab(2.3 * r, P(0, -0.9), P(0, -3.2), shirt, 0.3 * r)
            legs = VGroup(*[slab(0.6 * r, P(sx * 0.6, -3.5), P(sx * 0.6, -5.05), CLOTH) for sx in (-1, 1)],
                          *[Ellipse(width=0.95 * r, height=0.32 * r, stroke_width=0, fill_color=SHOE,
                                    fill_opacity=1).move_to(P(sx * 0.7, -5.15)) for sx in (-1, 1)])
            beam = Rectangle(width=2 * half * r, height=1.15 * r, stroke_color=WOOD_EDGE, stroke_width=2,
                             fill_color=WOOD, fill_opacity=1).move_to(P(0, -2.975))
            posts = VGroup(*[Line(P(sx * (half - 0.2), -3.55), P(sx * (half - 0.2), -5.31), color=WOOD_EDGE,
                                  stroke_width=3) for sx in (-1, 1)])
            self.desk = VGroup(posts, beam, text(spec["name"], MIN_FONT, MUTED).move_to(beam))
        else:
            low = -0.9 - spec.get("torso", 3.3)
            torso = slab(2.3 * r, P(0, -0.9), P(0, low), shirt, 0.3 * r)
            legs = VGroup(*[slab(0.75 * r, P(sx * 0.5, low + 0.2), P(sx * 0.5, low - 2.7), CLOTH) for sx in (-1, 1)],
                          *[Ellipse(width=1.05 * r, height=0.34 * r, stroke_width=0, fill_color=SHOE,
                                    fill_opacity=1).move_to(P(sx * 0.62, low - 2.8)) for sx in (-1, 1)])
            self.desk = VGroup()

        self.arms, self.hands = [], []
        for k, sx in enumerate((-1, 1)):
            end = P(*self.poses["rest"][k])
            arm = Line(P(sx, -1.3), end, color=shirt, stroke_width=13)
            arm.set_cap_style(CapStyleType.ROUND)
            self.arms.append(arm)
            self.hands.append(Dot(end, radius=0.3 * r, color=SKIN))

        def dark(shape):
            return shape.set_stroke(width=0).set_fill(HAIR, 1)

        hair = [dark(Arc(radius=r, start_angle=PI * 0.08, angle=PI * 0.84))]
        style = spec["hair"]
        if style == "bun":
            hair.append(dark(Circle(radius=0.36 * r)).move_to(P(-0.78, 0.72)))
        elif style == "tuft":
            hair.append(dark(Polygon(P(-0.25, 0.9), P(0.3, 1.25), P(0.55, 0.8))))
        elif style == "pony":
            hair.append(dark(Ellipse(width=0.5 * r, height=0.95 * r)).move_to(P(0.98, 0.32)))
        elif style == "curls":
            hair += [dark(Circle(radius=0.27 * r)).move_to(P(x, y))
                     for x, y in ((-0.62, 0.7), (-0.22, 0.92), (0.22, 0.92), (0.62, 0.7))]
        if spec.get("glasses"):
            hair += [Circle(radius=r * 0.2, stroke_color=HAIR, stroke_width=2).move_to(P(sx * 0.34, 0.06))
                     for sx in (-1, 1)]
            hair.append(Line(P(-0.14, 0.06), P(0.14, 0.06), stroke_color=HAIR, stroke_width=2))
        self.eyes = VGroup(*[Dot(P(sx * 0.34, 0.06), radius=r * 0.085, color=LIPS) for sx in (-1, 1)])
        self.mouth = self._mouth("soft")
        self.brow_l, self.brow_r = self._brows("flat")

        # layers: legs and torso behind the desk, arms and head in front of it
        self.back = VGroup(legs, torso).set_z_index(1)
        self.desk.set_z_index(2)
        self.front = VGroup(*self.arms, *self.hands, self.head, *hair, self.eyes, self.brow_l, self.brow_r,
                            self.mouth).set_z_index(3)
        self.add(self.back, self.desk, self.front)
        self.play_look(look)

    def at(self, x, y):
        """A point on the figure, in head radii from the centre of the head."""
        return self.head.get_center() + self.r * np.array([x, y, 0.0])

    def stand_on(self, x, y):
        """Move the figure so the head is at ``x`` and the feet rest on ``y``."""
        return self.shift(RIGHT * (x - self.head.get_x()) + UP * (y - self.get_bottom()[1]))

    def body(self):
        """What comes and goes when the character moves: a seated student leaves the desk behind."""
        return VGroup(self.back, self.front) if (self.seated and self.who != "T") else self

    # -- face --

    def _mouth(self, kind):
        a, b = self.at(-0.32, -0.42), self.at(0.32, -0.42)
        if kind == "smile":
            m = ArcBetweenPoints(a, b, angle=PI / 2)
        elif kind == "soft":
            m = ArcBetweenPoints(self.at(-0.22, -0.44), self.at(0.22, -0.44), angle=PI / 4)
        elif kind == "open":
            m = ArcBetweenPoints(a, b, angle=PI * 0.85).set_fill(LIPS, 1)
        elif kind == "say":
            m = Ellipse(width=self.r * 0.42, height=self.r * 0.3).move_to(self.at(0, -0.48)).set_fill(LIPS, 1)
        elif kind == "frown":
            m = ArcBetweenPoints(self.at(-0.26, -0.56), self.at(0.26, -0.56), angle=-PI / 2)
        elif kind == "o":
            m = Circle(radius=self.r * 0.15).move_to(self.at(0, -0.5)).set_fill(LIPS, 1)
        elif kind == "wavy":
            m = VMobject().set_points_smoothly([a, self.at(-0.1, -0.36), self.at(0.1, -0.5), b])
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
        """Set the expression at once (while the figure is not on screen)."""
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

    # -- arms --

    def _reach(self, name):
        return [(arm, hand, self.at(sx, -1.3), self.at(*xy))
                for arm, hand, sx, xy in zip(self.arms, self.hands, (-1, 1), self.poses[name])]

    def pose_to(self, name):
        """Animations that move the arms to pose ``name`` (an unknown pose means "rest")."""
        name = name if name in self.poses else "rest"
        if name == self.pose:
            return []
        self.pose = name
        anims = []
        for arm, hand, start, end in self._reach(name):
            if np.linalg.norm(hand.get_center() - end) > 1e-3:
                anims += [arm.animate.put_start_and_end_on(start, end), hand.animate.move_to(end)]
        return anims

    def set_pose(self, name):
        """Set the pose at once (while the figure is not on screen)."""
        self.pose = name
        for arm, hand, start, end in self._reach(name):
            arm.put_start_and_end_on(start, end)
            hand.move_to(end)
        return self

    def voice_mark(self):
        """Three short arcs beside the mouth: this character is speaking."""
        c = self.at(self.side * 1.25, -0.4)
        arcs = VGroup(*[Arc(radius=self.r * k, start_angle=-PI / 5, angle=2 * PI / 5, arc_center=c, color=INK,
                            stroke_width=3) for k in (0.35, 0.65, 0.95)])
        if self.side < 0:
            arcs.rotate(PI, about_point=c)
        return arcs.set_z_index(3)


# ============================================================= lesson ====

YESTERDAY = """
do {
    body
} while (condition);
"""

DO_WHILE = r"""
int i = 1, n;
scanf("%d", &n);
do {
    printf("%d\n", 7 * i);
    i++;
} while (i <= n);
"""

WHILE = r"""
int i = 1, n;
scanf("%d", &n);
while (i <= n) {
    printf("%d\n", 7 * i);
    i++;
}
"""

FOR_SEVEN = r"""
for (i = 1; i <= n; i++)
    printf("%d\n", 7 * i);
"""

FOR_ZERO = r"""
for (i = 1; i <= 0; i++)
    printf("%d\n", 7 * i);
"""

Q1 = r"""
#include <stdio.h>

int main(void)
{
    int i, sum = 0;
    for (i = 1; i <= 5; i++)
        sum += i;
    printf("%d %d", sum, i);
    return 0;
}
"""
Q1_FOR, Q1_SUM, Q1_PRINT = 4, 5, 6            # line numbers in Q1 (blank lines not counted)

Q2 = r"""
#include <stdio.h>

int main(void)
{
    int i;
    for (i = 0; i < 5; i++);
        printf("%d ", i);
    return 0;
}
"""
Q2_FOR, Q2_PRINT = 4, 5

Q1_CORE = r"""
for (i = 1; i <= 5; i++)
    sum += i;
printf("%d %d", sum, i);
"""

Q1_PIN = r"""
for (i = 1; i <= 5; i++)
printf("%d %d", sum, i);
"""

Q2_CORE = r"""
for (i = 0; i < 5; i++);
    printf("%d ", i);
"""

GENERAL = """
for (init; condition; update)
    statement
"""

TRACE3 = r"""
for (i = 1; i <= 3; i++)
    printf("%d ", i);
"""

DOWN3 = r"""
for (i = 10; i > 0; i -= 3)
    printf("%d ", i);
"""

AB = r"""
for (i = 1; i <= 3; i++)
    printf("A ");
    printf("B ");
"""

C99 = r"""
for (int i = 1; i <= 5; i++)
    sum += i;
printf("%d %d", sum, i);
"""

MARKS = [72, 85, 64, 90, 58]

# the questions and the examples, worked out
_sum, _i = 0, 1
while _i <= 5:
    _sum, _i = _sum + _i, _i + 1
assert (_sum, _i) == (15, 6)                                    # question 1: option B
_i = 0
while _i < 5:
    _i += 1
assert _i == 5                                                  # question 2: the body is the lone ";", option C
assert len(range(1, 101)) == 100 and len(range(0, 100)) == 100 and len(range(5, 13)) == 12 - 5 + 1 == 8
_seen, _i = [], 10
while _i > 0:
    _seen.append(_i)
    _i -= 3
assert _seen == [10, 7, 4, 1] and _i == -2


class ForLoopClassroomMovie(LMSScene):
    lesson_title = "The for Loop - The Classroom Movie"

    def construct(self):
        self.camera.background_color = BG
        self.figs = {}             # (who, stance) -> every figure built so far
        self.fig = {}              # who -> the figure on screen now
        self.pins = {}             # key -> card of the pinned panel, top to bottom
        self.title_bar = None
        self.stage = None
        self.voice = None          # the mark beside the speaker
        self.talking = None
        self.carry = types.SimpleNamespace()     # what one scene hands to the next
        self.problems = []         # what the layout guards found (all reported together at the end)

        self.one_row_too_many()
        self.one_line()
        self.exam()
        self.four_answers()
        self.three_parts()
        self.the_order()
        self.counting()
        self.the_body()
        self.back_to_the_board()
        self.choosing()
        self.three_habits()
        if self.problems:
            raise ValueError(f"{len(self.problems)} layout problem(s):\n" + "\n".join(self.problems))

    # ------------------------------------------------------ stage helpers --

    def kept(self):
        """Family of what stays through a scene change: the cast, the heading, the pinned panel."""
        keep = set()
        for mob in (*self.figs.values(), *self.pins.values(), self.title_bar, self.stage, self.voice):
            if mob is not None:
                keep.update(mob.get_family())
        return keep

    def wipe(self, *with_anims, keep=(), run_time=0.6):
        """Clear the board. ``with_anims`` play alongside; ``keep`` are board mobjects that stay."""
        stay = self.kept()
        for mob in keep:
            stay.update(mob.get_family())
        parts = [p for m in self.mobjects for p in m.family_members_with_points() if p not in stay]
        anims = ([FadeOut(Group(*parts))] if parts else []) + list(with_anims)
        if anims:
            self.play(*anims, run_time=run_time)
        for mob in list(self.mobjects):
            if mob not in stay and not any(p in stay for p in mob.get_family()):
                self.remove(mob)

    def heading(self, s):
        """The scene heading: a title with a blue rule, above the board."""
        title = text(s, HEAD, INK, BOLD)
        if title.width > HEAD_W:
            raise ValueError(f"Heading {s!r} is {title.width:.2f} wide; the top band has {HEAD_W:.2f}.")
        rule = Line(LEFT, RIGHT, color=BLUE, stroke_width=3).set_width(title.width).next_to(title, DOWN, buff=0.14)
        bar = VGroup(title, rule).move_to([BOARD_X, HEAD_Y, 0])
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

    def fit(self, *mobs, left=BOARD_L, right=BOARD_R, top=BOARD_TOP, bottom=BOARD_BOTTOM):
        """Layout guard: every mobject must lie on the board."""
        for mob in mobs:
            if (mob.get_left()[0] < left - 1e-6 or mob.get_right()[0] > right + 1e-6
                    or mob.get_bottom()[1] < bottom - 1e-6 or mob.get_top()[1] > top + 1e-6):
                self.problem(f"{self.what(mob)} leaves the board: x {mob.get_left()[0]:.2f}..{mob.get_right()[0]:.2f}, "
                             f"y {mob.get_bottom()[1]:.2f}..{mob.get_top()[1]:.2f} "
                             f"(allowed x {left:.2f}..{right:.2f}, y {bottom:.2f}..{top:.2f}).")
        return mobs[0]

    def apart(self, *mobs, gap=0.05):
        """Layout guard: the bounding boxes of ``mobs`` must not touch."""
        for i, a in enumerate(mobs):
            for b in mobs[i + 1:]:
                if (a.get_right()[0] + gap > b.get_left()[0] and b.get_right()[0] + gap > a.get_left()[0]
                        and a.get_top()[1] + gap > b.get_bottom()[1] and b.get_top()[1] + gap > a.get_bottom()[1]):
                    self.problem(f"{self.what(a)} and {self.what(b)} overlap.")

    def problem(self, message):
        """Note a layout problem with the line of the scene code that led to it."""
        import inspect

        line = next((f.lineno for f in inspect.stack()[2:] if f.function not in ("fit", "apart", "pick")), 0)
        self.problems.append(f"  line {line}: {message}")

    @staticmethod
    def what(mob):
        """A readable name for a mobject in a guard message."""
        texts = [m.text for m in mob.get_family() if isinstance(m, Text)]
        return f"{type(mob).__name__}({' / '.join(texts[:3])!r})" if texts else repr(mob)

    def frame(self, mob, color=BLUE, buff=0.1):
        """An outline around a piece of the board (not a container: the layout check leaves it out)."""
        box = SurroundingRectangle(mob, color=color, buff=buff, corner_radius=0.08, stroke_width=3)
        self.validator.ignore(box)
        return box

    def circle(self, mob, radius=0.22, color=FLASH):
        """A small circle around one character of code."""
        loop = Circle(radius=radius, color=color, stroke_width=4).move_to(mob)
        self.validator.ignore(loop)
        return loop

    def countdown(self, seconds):
        """Thinking time: a bar under the heading runs out."""
        self.quiet()
        bar = Line(LEFT * 1.6, RIGHT * 1.6, color=FLASH, stroke_width=5).move_to([BOARD_X, TIMER_Y, 0])
        self.play(FadeIn(bar), run_time=0.3)
        self.play(Uncreate(bar), run_time=max(0.5, seconds - 0.3), rate_func=linear)

    # ------------------------------------------------------ pinned panel --

    def pin(self, key, card, source=None, run_time=0.7):
        """Add ``card`` under the pinned cards. ``source``: board content that flies into it."""
        top = TOP - sum(c.height + PIN_GAP for c in self.pins.values())
        place(card, left=PANEL_L, top=top)
        if card.get_bottom()[1] < FLOOR - 1e-6:
            raise ValueError(f"The pinned panel is full: '{key}' would end at y {card.get_bottom()[1]:.2f}.")
        self.pins[key] = card
        if source is not None:
            self.play(FadeOut(source, target_position=card.get_center(), scale=0.5), FadeIn(card), run_time=run_time)
        else:
            self.play(FadeIn(card, shift=LEFT * 0.3), run_time=run_time)

    def unpin(self, key, *with_anims, run_time=0.6):
        """Take a card off the panel; the cards under it move up."""
        card = self.pins.pop(key)
        anims, top = [FadeOut(card, shift=RIGHT * 0.3)], TOP
        for other in self.pins.values():
            rise = top - other.get_top()[1]
            if abs(rise) > 1e-6:
                anims.append(other.animate.shift(UP * rise))
            top -= other.height + PIN_GAP
        self.play(*anims, *with_anims, run_time=run_time)

    def pinned(self, key):
        """A passing highlight on a pinned card."""
        return ring(self.pins[key].frame)

    def q_card(self, n, guess, src):
        """A parked question: its number, a question mark, the two guesses and its loop."""
        head = phrase(text(f"Q{n}", SMALL, BLUE, BOLD), text("?", SMALL, FLASH, BOLD), text(guess, SMALL, MUTED), buff=0.2)
        listing = Listing(src, PIN_CODE)
        card = pin_card(head, listing)
        card.code = listing
        return card

    def done_card(self, n, answer):
        """A solved question: the question mark has become a tick."""
        row = VGroup(text(f"Q{n}", SMALL, BLUE, BOLD), tick(0.22), code(answer, PIN_CODE, GOOD)).arrange(RIGHT, buff=0.2)
        return pin_card(row, color=GOOD)

    # ------------------------------------------------------------ the cast --

    def figure(self, who, stance):
        """The figure of ``who`` standing at the board or sitting at a desk (built once)."""
        if (who, stance) not in self.figs:
            p = Person(who, stance)
            if stance == "stand":
                p.stand_on(TEACHER_X, STAGE_Y)
            else:
                p.stand_on(TEACHER_X if who == "T" else SEATS[who], FLOOR)
            self.validator.ignore(p)
            self.figs[who, stance] = p
        return self.figs[who, stance]

    def enter_cast(self):
        """The classroom: three students at their desks, then Ms. Rao walks in."""
        self.stage = Line([-EDGE_X, STAGE_Y, 0], [BOARD_R + 0.1, STAGE_Y, 0], color=EDGE, stroke_width=2)
        for who in "AMK":
            self.fig[who] = self.figure(who, "sit")
        self.fig["T"] = self.figure("T", "stand")
        self.play(Create(self.stage), *[FadeIn(self.fig[w], shift=UP * 0.2) for w in "AMK"], run_time=0.8)
        self.play(FadeIn(self.fig["T"], shift=RIGHT * 0.5), run_time=0.7)

    def quiet(self):
        """Nobody is speaking: the voice mark goes."""
        if self.voice is not None:
            self.play(FadeOut(self.voice), run_time=0.2)
        self.voice = self.talking = None

    def change_places(self, moves, run_time=0.5):
        """``moves`` is {who: "stand" or "sit"}: those figures leave and come back in the new place."""
        self.quiet()
        old = [self.fig[w] for w in moves]
        new = [self.figure(w, stance) for w, stance in moves.items()]
        self.play(*[FadeOut(p.body()) for p in old], run_time=run_time)
        for p in new:
            p.play_look("neutral").set_pose("rest")
        self.play(*[FadeIn(p.body()) for p in new], run_time=run_time)
        for w, p in zip(moves, new):
            self.fig[w] = p

    def to_board(self, who):
        """``who`` walks to the board with the marker; Ms. Rao sits at her desk."""
        self.change_places({who: "stand", "T": "sit"})

    def to_seat(self, who):
        self.change_places({who: "sit", "T": "stand"})

    def react(self, who, look):
        """Animations that change one character's expression (use inside a cue)."""
        return self.fig[who].look_to(look)

    def gesture(self, who, pose):
        """Animations that move one character's arms (use inside a cue)."""
        return self.fig[who].pose_to(pose)

    def speaker(self, who, look=None, pose=None, others=None):
        """Show who speaks: "N" narrator (everyone listens), "T" teacher, "A" / "M" / "K" a student.

        ``look`` and ``pose`` are the speaker's; ``others`` is {who: look} for listeners who react."""
        others = others or {}
        anims = []
        for w, p in self.fig.items():
            if w == who:
                anims += p.look_to(look or "talk") + p.pose_to(pose or "rest")
            else:
                anims += p.look_to(others.get(w, "neutral")) + p.pose_to("rest")
        mark = self.voice
        if who != self.talking:
            if self.voice is not None:
                anims.append(FadeOut(self.voice))
            mark = None if who == "N" else self.fig[who].voice_mark()
            if mark is not None:
                anims.append(FadeIn(mark))
        if anims:
            self.play(*anims, run_time=0.3)
        self.voice, self.talking = mark, who

    # ------------------------------------------------- narration drivers --

    def cue(self, n, word):
        """Wait for ``word`` (or ``(word, occurrence)``) in narration ``n``."""
        spoken, occ = (word, 1) if isinstance(word, str) else word
        if n.estimated and not spoken.replace(" ", "").isalpha():
            raise ValueError(f"Anchor {spoken!r} must be plain words (no apostrophes, hyphens or digits).")
        try:
            self.at_word(n, spoken, occ)
        except ValueError:
            if n.estimated:
                raise                     # dry run: a wrong anchor is a bug in this file
            # with real audio the aligner may spell a word differently: just carry on

    def run(self, n, cues, think=0.0):
        """Play ``(word, what)`` or ``(word, what, run_time)`` cues in spoken order, then hold until ``n`` ends.

        ``what`` is an animation, a list of animations, or a function that returns
        one (or plays things itself and returns None). ``think`` seconds of the
        pause after ``n`` are shown as a countdown."""
        for item in cues:
            word, what = item[0], item[1]
            if word:
                self.cue(n, word)
            if isinstance(what, (types.FunctionType, types.MethodType)):
                what = what()
            anims = self.flat(what) if what is not None else []
            if anims:
                self.play(*anims, **({"run_time": item[2]} if len(item) > 2 else {}))
        if think:
            self.wait_for_narration(n, include_pause=False)
            self.countdown(think)
        self.wait_for_narration(n)
        return n

    @classmethod
    def flat(cls, what):
        """Animations from a single animation or a (nested) list of them."""
        if not isinstance(what, (list, tuple)):
            return [what]
        return [a for item in what for a in cls.flat(item)]

    def say(self, who, nid, spoken, cues, look=None, pose=None, others=None, think=0.0):
        """One spoken block. ``who`` is the role key (see ROLES); only ``spoken`` reaches the voice."""
        self.speaker(who, look, pose, others)
        n = self.narrate(id=nid, text=spoken, voice=VOICES[who], subtitle=True,
                         pause_after=think if think else TURN_PAUSE)
        return self.run(n, cues, think)

    def N(self, nid, spoken, *cues, **how):
        """Narrator: transitions. Everyone listens."""
        return self.say("N", nid, spoken, cues, **how)

    def T(self, nid, spoken, *cues, **how):
        """Teacher, Ms. Rao."""
        return self.say("T", nid, spoken, cues, **how)

    def A(self, nid, spoken, *cues, **how):
        """Student, Aarav."""
        return self.say("A", nid, spoken, cues, **how)

    def M(self, nid, spoken, *cues, **how):
        """Student, Meera."""
        return self.say("M", nid, spoken, cues, **how)

    def K(self, nid, spoken, *cues, **how):
        """Student, Kabir."""
        return self.say("K", nid, spoken, cues, **how)

    def show_q(self, q):
        """A practice question appears: the program line by line, then the question and its options."""
        self.play(LaggedStart(*[FadeIn(l, shift=RIGHT * 0.1) for l in q.prog.lines], lag_ratio=0.12, run_time=2.0))
        self.play(FadeIn(q.label), FadeIn(q.ask), run_time=0.5)
        self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.15) for r in q.opts], lag_ratio=0.3, run_time=1.4))

    def swap_q(self, old, new):
        self.play(FadeOut(old.everything()), run_time=0.4)
        self.play(FadeIn(new.everything()), run_time=0.5)

    # ============================================ 1. ONE ROW TOO MANY ======

    def one_row_too_many(self):
        self.scene_start("S01_one_row_too_many", title="One Row Too Many")

        crumb = text("CDAC C-CAT Preparation", SMALL, MUTED)
        title = text("The for Loop", TITLE, INK, BOLD)
        rule = Line(LEFT * 1.6, RIGHT * 1.6, color=BLUE, stroke_width=4)
        before = text("Previous topic:  The do-while Loop", LABEL, BROWN)
        card = VGroup(crumb, title, rule, before).arrange(DOWN, buff=0.4)
        self.play(FadeIn(crumb), FadeIn(title, shift=UP * 0.2), Create(rule), run_time=1.0)
        self.play(FadeIn(before, shift=UP * 0.15), run_time=0.6)
        self.wait(1.4)
        self.play(FadeOut(card), run_time=0.5)
        self.enter_cast()
        self.heading("One row too many")

        # yesterday's notes, left on the side of the board
        notes = Listing(YESTERDAY, PIN_CODE)
        self.pin("yesterday", pin_card(text("Yesterday's loop", SMALL, MUTED, BOLD), notes,
                                       text("Runs first, asks later", SMALL, BROWN)))

        left = BOARD_L + 0.4
        dw = place(Listing(DO_WHILE), left=left, top=2.55)
        wh = place(Listing(WHILE), left=left, top=2.55)
        cur = list(dw.lines)                         # the six lines on the board now
        side = 1.45                                  # centre of the narrow column right of the code
        in_l = place(text("Input", SMALL, MUTED), x=side, y=2.4)
        n10 = place(code("n = 10", LABEL), x=side, y=1.95)
        n0 = place(code("n = 0", LABEL), x=side, y=1.95)
        out_l = place(text("Output", SMALL, MUTED), x=side, y=1.4)
        outs = VGroup(*[code(str(7 * k), CODE) for k in range(1, 11)])
        for k, m in enumerate(outs):
            m.move_to([side - 0.4 + 0.8 * (k // 5), 0.9 - 0.42 * (k % 5), 0])
        rows10 = place(text("10 rows", SMALL, BLUE), x=side, y=-1.25)
        one7 = place(code("7", CODE_BIG, BAD), x=side, y=0.9)
        asked0 = place(VGroup(text("asked for", SMALL, BAD), text("0 rows", SMALL, BAD)).arrange(DOWN, buff=0.08),
                       x=side, y=0.25)
        none0 = place(text("0 rows", LABEL, GOOD), x=side - 0.3, y=0.9)
        fixed = tick().next_to(none0, RIGHT, buff=0.2)
        self.fit(dw, wh, in_l, n10, out_l, outs, rows10, asked0, none0, fixed)
        self.apart(dw, VGroup(in_l, n10, out_l, outs, rows10))

        # the body grows to "forty lines": placeholders push i++ far down, then the duster hides it
        drop = 1.45
        bar_x, bar_y = dw.lines[3].get_left()[0], dw.lines[3].get_bottom()[1] - 0.18
        bars = VGroup(*[Line([bar_x, bar_y - 0.15 * k, 0], [bar_x + w, bar_y - 0.15 * k, 0], color=FAINT, stroke_width=5)
                        for k, w in enumerate((2.0, 2.6, 1.5, 2.3, 2.6, 1.8, 2.4, 2.1))])
        brace = Brace(bars, RIGHT, buff=0.12).set_color(MUTED)
        forty = VGroup(brace, text("40 lines", SMALL, MUTED).next_to(brace, RIGHT, buff=0.12))
        duster = VGroup(RoundedRectangle(width=1.5, height=0.44, corner_radius=0.08, stroke_color=WOOD_EDGE,
                                         stroke_width=2, fill_color=CAST["T"]["shirt"], fill_opacity=1),
                        Line(LEFT * 0.6, RIGHT * 0.6, color=WOOD, stroke_width=4))
        duster.move_to(dw.lines[4].get_center() + DOWN * drop)
        self.validator.ignore(duster)
        sevens = VGroup(*[code("7", CODE, BAD) for _ in range(18)]).arrange_in_grid(rows=6, cols=3, buff=(0.35, 0.12))
        place(sevens, x=side, y=0.75)
        endless = place(text("never stops", SMALL, BAD), x=side, y=-1.1)
        self.fit(forty, sevens, endless)

        i1, cond, step = dw.part(0, "i = 1"), wh.part(2, "i <= n"), dw.part(4, "i++")
        colours = ((i1, GREEN), (cond, BLUE), (step, BROWN))
        made = {}

        def to_while():
            self.play(ReplacementTransform(dw.lines[5], wh.lines[2], path_arc=-PI / 3),
                      ReplacementTransform(dw.lines[2], wh.lines[5], path_arc=-PI / 3), run_time=1.4)
            cur[2], cur[5] = wh.lines[2], wh.lines[5]

        def stretch():
            self.play(cur[4].animate.shift(DOWN * drop), cur[5].animate.shift(DOWN * drop), run_time=0.9)
            self.play(LaggedStart(*[Create(b) for b in bars], lag_ratio=0.12), FadeIn(forty), run_time=1.2)

        def mark():
            made["boxes"] = [self.frame(piece, color, 0.08) for piece, color in colours]
            return [Create(b) for b in made["boxes"]] + [piece.animate.set_color(color) for piece, color in colours]

        def spans():
            x = left - 0.22
            ys = [piece.get_y() for piece, _ in colours]
            made["spans"] = [DoubleArrow([x, a - 0.1, 0], [x, b + 0.1, 0], buff=0, color=MUTED, stroke_width=3,
                                         tip_length=0.15) for a, b in zip(ys, ys[1:])]
            return [GrowFromCenter(s) for s in made["spans"]]

        self.T("s1_01", "Before anyone opens a notebook, look at the board. Yesterday's loop is still there. Aarav, "
                        "what was special about it?",
               ("board", lambda: self.gesture("T", "point")),
               ("loop", lambda: self.pinned("yesterday")), look="ask")
        self.A("s1_02", "It runs first and asks later. The body executes once, and only then is the condition checked.",
               ("body", lambda: hl(notes.lines[1])),
               ("condition", lambda: hl(notes.lines[2])), look="smile")
        self.T("s1_03", "Good. Then this should be easy. Print the table of seven, but let the user decide how many rows.",
               ("Print", lambda: LaggedStart(*[FadeIn(l, shift=RIGHT * 0.1) for l in dw.lines], lag_ratio=0.25,
                                             run_time=2.6)),
               ("user", lambda: hl(dw.lines[1])), look="smile", pose="point")
        self.T("s1_04", "The user types ten. What do we see?",
               ("ten", lambda: [FadeIn(in_l), FadeIn(n10, shift=UP * 0.15)]), look="ask")
        self.A("s1_05", "Seven, fourteen, twenty-one, all the way to seventy. Ten rows.",
               ("Seven", lambda: [FadeIn(out_l), LaggedStart(*[FadeIn(m, shift=UP * 0.1) for m in outs], lag_ratio=0.2,
                                                             run_time=2.4)]),
               ("rows", lambda: FadeIn(rows10, shift=UP * 0.1)), look="happy")
        self.T("s1_06", "And if the user types zero?",
               ("zero", lambda: [FadeOut(VGroup(n10, outs, rows10)), FadeIn(n0)]),
               look="ask", others={"A": "think", "M": "think", "K": "think"}, think=3.0)
        self.M("s1_07", "It still prints seven. One row. The body runs before the check ever happens.",
               ("seven", lambda: FadeIn(one7, scale=1.3)),
               ("row", lambda: FadeIn(asked0, shift=UP * 0.1)),
               ("body", lambda: dw.focus(3)),
               ("check", lambda: dw.focus(5)), look="surprised", pose="write")
        self.T("s1_08", "The user asked for nothing and got something. How do we fix that?",
               ("nothing", lambda: [dw.focus(None), hl(n0)]),
               ("something", lambda: hl(one7, 1.4)), look="ask")
        self.A("s1_09", "Use a while loop. Check first, then run.",
               ("while", to_while), look="happy", pose="raise")
        self.T("s1_10", "Zero rows for zero. Fixed. Now watch what I do to your loop.",
               ("Zero", lambda: [FadeOut(VGroup(one7, asked0)), FadeIn(none0)]),
               ("Fixed", lambda: FadeIn(fixed, scale=0.6)),
               ("watch", lambda: [FadeOut(VGroup(in_l, n0, out_l, none0, fixed)), self.gesture("T", "point")]),
               look="smile")
        self.T("s1_11", "Imagine this body is forty lines long. And somewhere around line thirty-eight, I forget this one.",
               ("forty", stretch),
               ("forget", lambda: [FadeIn(duster, shift=LEFT * 0.5), FadeOut(cur[4])]), pose="point")
        self.A("s1_12", "Then it never stops. i stays at one forever. Seven, seven, seven, seven.",
               ("never", lambda: FadeIn(endless, shift=UP * 0.1)),
               ("Seven", lambda: LaggedStart(*[FadeIn(s, shift=UP * 0.15) for s in sevens], lag_ratio=0.12,
                                             run_time=2.4)), look="surprised")
        # Ms. Rao lifts the duster and the scrolling stops
        self.play(FadeOut(duster, shift=UP * 0.4), FadeIn(cur[4]), FadeOut(VGroup(sevens, endless)), run_time=0.7)
        self.K("s1_13", "Ma'am, this loop is only counting. So why is the counting spread all over the place? The "
                        "start is up there, the stopping rule is in the brackets, and the step is hiding at the bottom.",
               ("start", lambda: hl(i1, 1.3)),
               ("stopping", lambda: hl(cond, 1.3)),
               ("step", lambda: hl(step, 1.3)), look="confused", pose="raise")
        self.T("s1_14", "Say that again, Kabir. Louder.", look="smile")
        self.K("s1_15", "Three things control this loop, and they live at three different addresses.",
               ("Three", mark),
               ("addresses", spans), pose="point")
        self.T("s1_16", "So what would you want instead?", look="ask")
        self.K("s1_17", "All three in one place. On one line. Where I can see them together and cannot forget one.",
               ("together", lambda: [Indicate(b, color=FLASH, scale_factor=1.15) for b in made["boxes"]]),
               look="smile")

        self.carry.pieces = (i1, cond, step)
        self.scene_end("S01_one_row_too_many")

    # ====================================================== 2. ONE LINE ====

    def one_line(self):
        old_init, old_cond, old_step = self.carry.pieces
        self.scene_start("S02_one_line", title="One Line")
        self.heading("One line")
        self.quiet()
        self.unpin("yesterday")

        loop = place(Listing(FOR_SEVEN, CODE_BIG), x=BOARD_X, y=1.2)
        init, cond, step = loop.paint_for(0, "i = 1", "i <= n", "i++")
        painted = {id(g) for piece in (init, cond, step) for g in piece}
        rest = VGroup(*[g for g in loop.lines[0] if id(g) not in painted])
        names = [text(s, SMALL, color).next_to(piece, UP, buff=0.2)
                 for s, color, piece in (("start", GREEN, init), ("stop", BLUE, cond), ("step", BROWN, step))]
        called = place(text("The for loop", BODY, BLUE, BOLD), x=BOARD_X, y=-0.2)
        ask0 = place(phrase(code("n = 0", LABEL), text("how many rows?", LABEL, BROWN)), x=BOARD_X, y=-1.0)
        note = pin_card(phrase(code("n = 0", PIN_CODE), text("how many rows?", SMALL, BROWN)), color=BROWN)
        self.fit(loop, called, ask0, *names)

        # the three pieces lift off the old loop and settle side by side in one pair of brackets
        self.wipe(TransformFromCopy(old_init, init), TransformFromCopy(old_cond, cond),
                  TransformFromCopy(old_step, step), keep=(init, cond, step), run_time=1.6)
        self.play(FadeIn(rest), FadeIn(loop.lines[1], shift=UP * 0.15), run_time=0.7)

        self.N("s2_01", "The language already had what Kabir asked for. The start, the stopping rule, and the step, "
                        "sitting side by side in a single header. It is called the for loop.",
               ("start", lambda: [FadeIn(names[0], shift=DOWN * 0.1), hl(init, 1.2)]),
               ("stopping", lambda: [FadeIn(names[1], shift=DOWN * 0.1), hl(cond, 1.2)]),
               ("step", lambda: [FadeIn(names[2], shift=DOWN * 0.1), hl(step, 1.2)]),
               ("header", lambda: ring(loop.lines[0])),
               ("called", lambda: FadeIn(called, shift=UP * 0.15)), others={"K": "happy"})
        self.T("s2_02", "This is today. It does the same job as the while loop you just wrote, but the whole counting "
                        "plan sits on one line, where you can read it in a single glance.",
               ("today", lambda: self.gesture("T", "point")),
               ("plan", lambda: ring(loop.lines[0])), look="smile")
        self.M("s2_03", "Ma'am, does this one also give zero rows when the user types zero?",
               ("zero", lambda: FadeIn(ask0, shift=UP * 0.15)), look="ask", pose="raise")
        self.T("s2_04", "Hold on to that question, Meera. In ten minutes you will answer it yourself.",
               ("Hold", lambda: self.pin("note", note, source=ask0)), look="smile")

        self.finish("S02_one_line")

    # =============================== 3. WHAT THE EXAM DOES WITH ONE LINE ====

    def exam(self):
        self.begin("S03_exam", "What the Exam Does With One Line", "What the exam asks")

        sect = text("C-CAT  Section B", LABEL, MUTED, BOLD)
        lines = VGroup(*[Line(ORIGIN, RIGHT * w, color=MUTED, stroke_width=6) for w in (2.6, 1.8, 3.4, 2.9, 2.2, 0.6)])
        lines.arrange(DOWN, buff=0.2, aligned_edge=LEFT)
        quest = text("What is the output?", LABEL)
        letters = VGroup(*[tag(s, MUTED) for s in "ABCD"]).arrange(RIGHT, buff=0.3)
        mock = place(column(sect, lines, quest, letters, buff=0.35), left=CODE_X + 0.1, top=2.5)
        loop_l = code("for (...)", SMALL, BLUE).next_to(lines[2], RIGHT, buff=0.2)
        trap = text("the trap", SMALL, BAD, BOLD).next_to(loop_l, RIGHT, buff=0.25)
        asks = place(numbered(["What is printed?", "How many times?", "What is left in the variable?"], BODY, 0.45),
                     x=BOARD_X, y=0.6)
        self.fit(mock, loop_l, trap, asks)

        q1 = Question(1, Q1, [("A", "15 5", True), ("B", "15 6", True), ("C", "10 5", True), ("D", "10 6", True)])
        q2 = Question(2, Q2, [("A", "0 1 2 3 4", True), ("B", "1 2 3 4 5", True), ("C", "5", True),
                              ("D", "Compilation error", False)])
        for q in (q1, q2):
            self.fit(q.prog, q.side, right=EDGE_X)        # the panel holds one small note: the full width is free
            self.apart(q.prog, q.side)

        self.T("s3_01", "Now let me tell you what C-CAT does with this. In Section B, nobody asks you to define a for "
                        "loop. You get five or six lines of C, four options, and one question. The loop is always "
                        "short. The trap is always inside it.",
               ("Section", lambda: FadeIn(sect, shift=UP * 0.15)),
               ("lines", lambda: LaggedStart(*[Create(l) for l in lines], lag_ratio=0.2)),
               ("options", lambda: FadeIn(letters, shift=UP * 0.15)),
               ("question", lambda: FadeIn(quest, shift=UP * 0.15)),
               ("short", lambda: [lines[2].animate.set_color(BLUE), FadeIn(loop_l)]),
               ("trap", lambda: FadeIn(trap, scale=1.2)), look="smile")
        self.T("s3_02", "And it usually comes down to one of three things. What gets printed. How many times the body "
                        "ran. Or what the variable is holding after the loop is finished.",
               ("three", self.wipe),
               ("printed", lambda: FadeIn(asks[0], shift=RIGHT * 0.2)),
               ("times", lambda: FadeIn(asks[1], shift=RIGHT * 0.2)),
               ("holding", lambda: FadeIn(asks[2], shift=RIGHT * 0.2)))
        self.T("s3_03", "So here are two practice questions. I am not going to teach you anything first. Just look.",
               ("two", self.wipe),
               ("look", lambda: self.show_q(q1)), look="smile",
               others={"A": "think", "M": "think", "K": "think"})
        self.countdown(6.0)
        self.play(FadeOut(q1.everything()), run_time=0.4)
        self.show_q(q2)
        self.countdown(6.0)

        self.carry.q1, self.carry.q2 = q1, q2
        self.scene_end("S03_exam")

    # ======================================= 4. FOUR DIFFERENT ANSWERS =====

    def four_answers(self):
        q1, q2 = self.carry.q1, self.carry.q2
        self.scene_start("S04_four_answers", title="Four Different Answers")
        self.heading("Four different answers")

        semi_ring = self.circle(q2.prog.part(Q2_FOR, ";", 3))
        for_line, printf_line = q2.prog.lines[Q2_FOR], q2.prog.lines[Q2_PRINT]
        indent = arrow([for_line.get_left()[0], printf_line.get_y(), 0],
                       [printf_line.get_left()[0] - 0.06, printf_line.get_y(), 0], MUTED, 3, 0.15)
        facts = column(text("Two missing facts", BODY, BLUE, BOLD),
                       *numbered(["When does each part run?", "What counts as the body?"], BODY), buff=0.45)
        place(facts, x=BOARD_X, y=0.9)
        self.fit(facts)

        def pick(q, letter, who):
            """A student chooses an option: it flashes and the name appears beside it."""
            row = q.opts.rows[letter]
            name = text(CAST[who]["name"], SMALL, MUTED).next_to(row, RIGHT, buff=0.35)
            self.fit(name, right=EDGE_X)
            q.picks.add(name)
            return [hl(row), FadeIn(name, shift=LEFT * 0.15)]

        def add(q, mob, anim):
            q.picks.add(mob)
            return anim

        self.T("s4_01", "Do not calculate yet. I want your first instinct. Question one.",
               ("Question", lambda: self.swap_q(q2, q1)), look="smile")
        self.A("s4_02", "A. Fifteen and five. One plus two plus three plus four plus five is fifteen, and the loop "
                        "stops at five.",
               ("Fifteen", lambda: pick(q1, "A", "A")),
               ("plus", lambda: q1.prog.focus(Q1_SUM)),
               ("stops", lambda: q1.prog.focus(Q1_FOR)), look="happy", pose="raise")
        self.M("s4_03", "Fifteen, yes. But I am not sure about the five. Something happens to i after the last "
                        "addition. I think it is B. I just cannot prove it.",
               ("sure", lambda: q1.prog.focus(None)),
               ("Something", lambda: hl(q1.prog.part(Q1_FOR, "i++"), 1.4)),
               ("B", lambda: pick(q1, "B", "M")), look="think", pose="think")
        self.T("s4_04", "Question two.",
               ("Question", lambda: self.swap_q(q1, q2)), look="smile")
        self.A("s4_05", "A again. Zero to four. That is the most standard loop there is.",
               ("Zero", lambda: pick(q2, "A", "A")), look="happy")
        self.K("s4_06", "There is a semicolon right after the bracket. Is that even allowed? I would say D. It should "
                        "not compile.",
               ("semicolon", lambda: add(q2, semi_ring, Create(semi_ring))),
               ("D", lambda: pick(q2, "D", "K")), look="confused", pose="point")
        self.M("s4_07", "But the printf is indented under the loop. It looks like it belongs inside.",
               ("indented", lambda: [hl(printf_line), add(q2, indent, GrowArrow(indent))]), look="think")
        self.T("s4_08", "Three students, two questions, four different answers. And none of you is being careless. You "
                        "are missing exactly two facts. The first is when each of the three parts actually runs. The "
                        "second is what counts as the body of the loop. Find those two facts, and both questions fall.",
               ("four", lambda: [hl(name) for name in q2.picks if isinstance(name, Text)]),
               ("missing", self.wipe),
               ("facts", lambda: FadeIn(facts[0], shift=UP * 0.15)),
               ("first", lambda: FadeIn(facts[1], shift=RIGHT * 0.2)),
               ("second", lambda: FadeIn(facts[2], shift=RIGHT * 0.2)), look="smile")

        def park():
            self.pin("q1", self.q_card(1, "A or B", Q1_PIN))
            self.pin("q2", self.q_card(2, "A or D", Q2_CORE))

        self.T("s4_09", "So I am leaving them up there. We will come back for them.",
               ("leaving", park), pose="point")

        self.finish("S04_four_answers")

    # ======================================= 5. THREE PARTS AND A BODY =====

    def three_parts(self):
        self.begin("S05_three_parts", "Three Parts and a Body", "Three parts and a body")

        form = place(Listing(GENERAL, CODE_BIG), x=BOARD_X, top=2.15)
        init, cond, step = form.paint_for(0, "init", "condition", "update")
        body = form.lines[1]
        jobs = (("initialization", GREEN, "where counting starts"), ("condition", BLUE, "a yes-or-no question"),
                ("update", BROWN, "the next value of i"), ("statement", INK, "the body: repeated work"))
        rows = [VGroup(place(text(name, LABEL, color, BOLD), left=CODE_X, y=0.75 - 0.55 * k),
                       place(text(job, LABEL), left=-1.95, y=0.75 - 0.55 * k))
                for k, (name, color, job) in enumerate(jobs)]
        once = tag("runs once", GREEN).next_to(init, UP, buff=0.15)
        back = CurvedArrow(step.get_top() + UP * 0.1, init.get_top() + UP * 0.1, angle=PI / 4, color=MUTED,
                           stroke_width=4, tip_length=0.2)
        defn = column(text("A for loop is an entry-controlled loop.", LABEL),
                      text("It tests its condition", LABEL),
                      phrase(text("before every execution", LABEL, BLUE, BOLD), text("of the body,", LABEL)),
                      text("and repeats the body for as long as", LABEL),
                      text("the condition is true.", LABEL), buff=0.14)
        place(defn, x=BOARD_X, top=0.95)
        self.fit(form, once, defn, *rows)
        for row in rows:
            self.apart(*row, gap=0.2)

        self.play(FadeIn(form, shift=UP * 0.2), run_time=0.8)
        self.T("s5_01", "You already found these three in your own while loop. Give them their jobs. Green.",
               ("three", lambda: [hl(init, 1.2), hl(cond, 1.2), hl(step, 1.2)]),
               ("Green", lambda: ring(init)), look="smile", pose="point")
        self.K("s5_02", "That is where the counting starts. It gives i its first value.",
               ("counting", lambda: FadeIn(rows[0], shift=RIGHT * 0.2)))
        self.T("s5_03", "How many times does it run?", look="ask")
        self.A("s5_04", "Every round?", look="ask")
        self.M("s5_05", "It cannot. If i went back to one on every round, the loop would never finish.",
               ("back", lambda: Create(back)),
               ("never", lambda: back.animate.set_color(BAD)), others={"A": "oops"})
        self.T("s5_06", "So?", look="ask")
        self.A("s5_07", "Once. Only at the very beginning.",
               ("Once", lambda: [FadeOut(back), FadeIn(once, shift=DOWN * 0.1)]), look="oops")
        self.T("s5_08", "Blue.", ("Blue", lambda: ring(cond)), pose="point")
        self.M("s5_09", "The condition. A yes-or-no question. If the answer is yes, keep going.",
               ("question", lambda: FadeIn(rows[1], shift=RIGHT * 0.2)))
        self.T("s5_10", "Orange.", ("Orange", lambda: ring(step)), pose="point")
        self.A("s5_11", "The update. It moves i to the next value.",
               ("moves", lambda: FadeIn(rows[2], shift=RIGHT * 0.2)))
        self.T("s5_12", "And the line underneath?",
               ("underneath", lambda: ring(body)), look="ask", pose="low")
        self.K("s5_13", "The body. The work that gets repeated.",
               ("work", lambda: FadeIn(rows[3], shift=RIGHT * 0.2)))

        # Ms. Rao writes one sentence under the diagram
        self.speaker("T", "smile", "low")
        self.play(FadeOut(VGroup(*rows)), run_time=0.4)
        self.play(LaggedStart(*[FadeIn(line, shift=RIGHT * 0.15) for line in defn], lag_ratio=0.3), run_time=2.4)
        self.wait(2.5)
        self.T("s5_14", "Before every execution. Remember those three words. They are about to matter.",
               ("execution", lambda: hl(defn[2][0])),
               ("three", lambda: ring(defn[2][0])), look="smile")
        self.pin("entry", pin_card(text("Entry-controlled loop", SMALL, BLUE, BOLD), text("Check, then the body", SMALL)),
                 source=defn)

        self.finish("S05_three_parts")

    # ============================ 6. THE ORDER NOBODY READS CORRECTLY ======

    def flow(self, dy=0.0):
        """The run order of a for loop: 1 once, then 2, 3, 4 round and round; out when 2 says false."""

        def node(n, s, color, x, y):
            label = phrase(text(str(n), SMALL, color, BOLD), text(s, SMALL), buff=0.15)
            box = RoundedRectangle(width=label.width + 0.4, height=0.6, corner_radius=0.12, stroke_color=color,
                                   stroke_width=3, fill_color=FILL, fill_opacity=1)
            return VGroup(box, label.move_to(box)).move_to([x, y + dy, 0])

        n1 = node(1, "Initialization", GREEN, -3.6, 0.85)
        n2 = node(2, "Condition", BLUE, -0.35, 0.85)
        n3 = node(3, "Body", INK, 1.0, -0.75)
        n4 = node(4, "Update", BROWN, -2.1, -0.75)
        g = VGroup(n1, n2, n3, n4)
        g.nodes = [n1, n2, n3, n4]
        g.a12 = arrow(n1.get_right() + RIGHT * 0.05, n2.get_left() + LEFT * 0.05, MUTED, 4, 0.18)
        g.a23 = arrow(n2.get_bottom() + RIGHT * 0.6 + DOWN * 0.05, n3.get_top() + UP * 0.05, MUTED, 4, 0.18)
        g.a34 = arrow(n3.get_left() + LEFT * 0.05, n4.get_right() + RIGHT * 0.05, MUTED, 4, 0.18)
        g.a42 = arrow(n4.get_top() + UP * 0.05, n2.get_bottom() + LEFT * 0.6 + DOWN * 0.05, MUTED, 4, 0.18)
        g.out = arrow(n2.get_right() + RIGHT * 0.05, n2.get_right() + RIGHT * 0.85, BAD, 4, 0.18)
        g.yes = text("true", SMALL).next_to(g.a23.get_center(), RIGHT, buff=0.2)
        g.no = text("false", SMALL, BAD).next_to(g.out, UP, buff=0.08)
        g.end = text("exit", SMALL, MUTED).next_to(g.out, RIGHT, buff=0.12)
        g.add(g.a12, g.a23, g.a34, g.a42, g.out, g.yes, g.no, g.end)
        return g

    def the_order(self):
        self.begin("S06_order", "The Order Nobody Reads Correctly", "The real order")

        ex = place(Listing(TRACE3), left=CODE_X, top=2.45)
        init, cond, step = ex.paint_for(0, "i = 1", "i <= 3", "i++")
        body = ex.lines[1]
        read = arrow([CODE_X, 2.58, 0], [ex.lines[0].get_right()[0], 2.58, 0], MUTED)
        read_l = text("you read", SMALL, MUTED).next_to(read, RIGHT, buff=0.25)
        no_read = cross(0.3).move_to(read)
        back = CurvedArrow(step.get_top() + UP * 0.08, cond.get_top() + UP * 0.08, angle=PI / 3, color=BROWN,
                           stroke_width=4, tip_length=0.18)

        tb = Table([code("i", CODE, INK, BOLD), code("i <= 3", CODE, BLUE), text("printed", SMALL)], (1.2, 2.2, 1.8),
                   left=CODE_X, top=1.5)
        cell = {}
        for r, i in enumerate((1, 2, 3, 4)):
            cell[r, 0] = tb.put(r, 0, code(str(i)))
            cell[r, 1] = tb.put(r, 1, code("true") if i <= 3 else code("false", CODE, BAD))
            if i <= 3:
                cell[r, 2] = tb.put(r, 2, code(str(i)))
        y2, y3 = tb.spot(2, 0)[1], tb.spot(3, 0)[1]
        exit_a = arrow([cell[3, 1].get_right()[0] + 0.2, y3, 0], [0.5, y3, 0], BAD)
        exit_l = text("exit", SMALL, BAD).next_to(exit_a, RIGHT, buff=0.15)
        runs3 = text("3 runs", SMALL).move_to([tb.spot(0, 2)[0], -1.2, 0])
        checks4 = text("4 checks", SMALL, BLUE).move_to([tb.spot(0, 1)[0], -1.2, 0])
        good_l = text("last good", SMALL, GOOD).move_to([1.3, y2, 0])
        bad_l = text("first bad", SMALL, BAD).move_to([1.3, y3, 0])
        self.fit(ex, tb, exit_l, runs3, checks4, good_l, bad_l, *cell.values())
        shown = [tb]                                 # the pieces of the trace that are on screen

        def show(*mobs):
            shown.extend(mobs)
            return [FadeIn(m) for m in mobs]

        def fill_rest():
            """Rows two and three fill in; then i becomes four."""
            for r in (1, 2):
                self.play(hl(cond, 1.3), *show(cell[r, 1]), run_time=0.55)
                self.play(hl(body), *show(cell[r, 2]), run_time=0.55)
                self.play(hl(step, 1.3), *show(cell[r + 1, 0]), run_time=0.55)

        fl = self.flow()
        self.fit(fl, top=ex.get_bottom()[1] - 0.1)

        def lap():
            for n in fl.nodes[1:]:
                self.play(Indicate(n[0], color=FLASH, scale_factor=1.08), run_time=0.45)

        rules_full = column(text("Two rules", BODY, BLUE, BOLD),
                            bullets([fitted_text("The condition is checked one more time than the body runs.", 6.4, LABEL),
                                     fitted_text("After the loop, the variable holds the first value that failed "
                                                 "the condition.", 6.4, LABEL)], buff=0.4), buff=0.45)
        place(rules_full, x=BOARD_X, y=0.6)
        rules_card = pin_card(text("Checks = body runs + 1", SMALL), text("After the loop, i holds", SMALL),
                              text("the first failing value", SMALL))

        zero = place(Listing(FOR_ZERO, CODE_BIG), x=BOARD_X, top=2.3)
        z_init, z_cond, _ = zero.paint_for(0, "i = 1", "i <= 0", "i++")
        s1 = code("i = 1", LABEL, GREEN)
        s2, s2b = phrase(code("1 <= 0", LABEL, BLUE), text("?", LABEL)), code("false", LABEL, BAD)
        s3 = text("The body never runs", LABEL)
        s4 = phrase(text("Output:", LABEL), text("0 rows", LABEL, GOOD, BOLD))
        place(column(s1, phrase(s2, s2b), s3, s4, buff=0.25), left=zero.get_left()[0], top=0.95)

        def side_card(title, color, how, least, x):
            inner = VGroup(code(title, CODE_BIG, color, BOLD), text(how, LABEL),
                           text(least, LABEL, color, BOLD)).arrange(DOWN, buff=0.3)
            box = RoundedRectangle(width=3.4, height=inner.height + 0.7, corner_radius=0.12, stroke_color=color,
                                   stroke_width=3, fill_color=FILL, fill_opacity=1)
            return VGroup(box, inner.move_to(box)).move_to([x, 0.7, 0])

        was = side_card("do-while", BROWN, "body, then check", "minimum 1 time", BOARD_X - 1.85)
        now = side_card("for", BLUE, "check, then body", "minimum 0 times", BOARD_X + 1.85)
        self.fit(rules_full, zero, s1, s2b, s3, s4, was, now)

        self.play(FadeIn(ex, shift=UP * 0.2), run_time=0.7)
        self.T("s6_01", "Here is the problem. You read this line from left to right. The computer does not run it from "
                        "left to right.",
               ("read", lambda: [GrowArrow(read), FadeIn(read_l)]),
               ("computer", lambda: [read.animate.set_color(BAD), read_l.animate.set_color(BAD),
                                     FadeIn(no_read, scale=0.6)]), pose="point")
        self.K("s6_02", "So it does not go start, condition, update, and then the body?",
               ("start", lambda: hl(init, 1.3), 0.4),
               ("condition", lambda: hl(cond, 1.3), 0.4),
               ("update", lambda: hl(step, 1.3), 0.4),
               ("body", lambda: hl(body), 0.4), look="confused")
        self.T("s6_03", "Let us find out. I will be the computer. You tell me what to do.",
               ("find", lambda: FadeOut(VGroup(read, read_l, no_read))),
               ("computer", lambda: FadeIn(tb, shift=UP * 0.15)), look="smile")
        self.T("s6_04", "First?", look="ask")
        self.K("s6_05", "Set i to one.",
               ("one", lambda: [hl(init, 1.3), *show(cell[0, 0])]))
        self.T("s6_06", "Next?", look="ask")
        self.A("s6_07", "Print it?", look="ask")
        self.M("s6_08", "No. Ask first. Is one less than or equal to three? Yes.",
               ("Ask", lambda: hl(cond, 1.3)),
               ("Yes", lambda: show(cell[0, 1])), others={"A": "oops"})
        self.T("s6_09", "Now print.",
               ("print", lambda: [hl(body), *show(cell[0, 2])]))
        self.T("s6_10", "And only now?", look="ask")
        self.A("s6_11", "The update. i becomes two.",
               ("update", lambda: hl(step, 1.3)),
               ("two", lambda: show(cell[1, 0])))
        self.T("s6_12", "Where does it go next? Back to the start?",
               ("start", lambda: hl(init, 1.3)), look="ask")
        self.M("s6_13", "Back to the question. Is two less than or equal to three?",
               ("question", lambda: [Create(back), hl(cond, 1.3)]))
        shown.append(back)
        self.quiet()
        fill_rest()
        self.T("s6_14", "i is four. Is four less than or equal to three?",
               ("four", lambda: ring(cell[3, 0])), look="ask")
        self.K("s6_15", "No.")
        self.T("s6_16", "So the loop is over.",
               ("over", lambda: [*show(cell[3, 1], exit_l), GrowArrow(exit_a)]))
        shown.append(exit_a)

        # the table steps aside for the run order as a cycle
        self.quiet()
        self.play(FadeOut(VGroup(*shown)), run_time=0.5)
        self.T("s6_17", "Start once. Then check, body, update. Check, body, update. Until the check says no.",
               ("Start", lambda: [FadeIn(fl.nodes[0]), GrowArrow(fl.a12)]),
               ("check", lambda: FadeIn(fl.nodes[1])),
               ("body", lambda: [GrowArrow(fl.a23), FadeIn(fl.yes), FadeIn(fl.nodes[2])]),
               ("update", lambda: [GrowArrow(fl.a34), FadeIn(fl.nodes[3]), GrowArrow(fl.a42)]),
               (("check", 2), lap),
               ("no", lambda: [GrowArrow(fl.out), FadeIn(fl.no), FadeIn(fl.end)]), pose="low")
        self.M("s6_18", "So the update is written before the body, but it runs after the body.",
               ("written", lambda: hl(step, 1.4)),
               ("runs", lambda: Indicate(fl.nodes[3][0], color=FLASH, scale_factor=1.1)), look="think")
        self.T("s6_19", "Exactly that. Now, two questions about the table. How many times did the body run?",
               ("table", lambda: [FadeOut(fl), FadeIn(VGroup(*shown))]), look="ask")
        self.K("s6_20", "Three.",
               (None, lambda: [*[hl(cell[r, 2], 1.3) for r in range(3)], FadeIn(runs3)]))
        self.T("s6_21", "How many times was the condition checked?", look="ask")
        self.A("s6_22", "Three.", look="smile")
        self.M("s6_23", "Four. There are four rows. The last check is the one that fails.",
               ("Four", lambda: [LaggedStart(*[hl(cell[r, 1], 1.2) for r in range(4)], lag_ratio=0.3), FadeIn(checks4)]),
               ("fails", lambda: ring(cell[3, 1], BAD)), others={"A": "oops"}, pose="write")
        self.T("s6_24", "And what is i holding at that moment?", look="ask")
        self.K("s6_25", "Four.",
               (None, lambda: [ring(cell[3, 0], BAD), cell[3, 0].animate.set_color(BAD)]))
        self.A("s6_26", "Oh. The loop does not stop at the last good value. It stops at the first bad one.",
               ("Oh", lambda: self.pinned("q1")),
               ("good", lambda: [cell[2, 0].animate.set_color(GOOD), FadeIn(good_l)]),
               ("bad", lambda: [FadeOut(VGroup(exit_a, exit_l)), FadeIn(bad_l)]), look="surprised")

        # the two rules, in full; then they are pinned for the rest of the lesson
        self.quiet()
        self.wipe()
        self.play(FadeIn(rules_full, shift=UP * 0.2), run_time=0.8)
        self.T("s6_27", "Do not touch question one yet, Aarav. But keep that thought.",
               ("question", lambda: self.pinned("q1")), look="smile", others={"A": "happy"})
        self.wait(1.5)
        self.pin("rules", rules_card, source=rules_full)

        self.T("s6_28", "Meera. Your question. The user types zero.",
               ("question", lambda: self.pinned("note")),
               ("zero", lambda: FadeIn(zero, shift=UP * 0.2)), look="smile", pose="point")
        self.M("s6_29", "i becomes one. Then the check. Is one less than or equal to zero? No. So it leaves "
                        "immediately. The body never runs. Zero rows.",
               ("one", lambda: [hl(z_init, 1.2), FadeIn(s1, shift=RIGHT * 0.2)]),
               ("check", lambda: hl(z_cond, 1.2)),
               ("equal", lambda: FadeIn(s2, shift=RIGHT * 0.2)),
               ("No", lambda: FadeIn(s2b, scale=1.2)),
               ("leaves", lambda: zero.lines[1].animate.set_color(MUTED)),
               ("never", lambda: FadeIn(s3, shift=RIGHT * 0.2)),
               ("rows", lambda: FadeIn(s4, shift=RIGHT * 0.2)), look="think", pose="write")

        def compare():
            self.wipe()
            self.play(FadeIn(was, shift=RIGHT * 0.2), FadeIn(now, shift=LEFT * 0.2), run_time=0.8)

        self.T("s6_30", "That is what entry-controlled means. The loop asks at the door.",
               ("means", lambda: self.pinned("entry")),
               ("door", compare), look="smile", others={"M": "happy"})
        done = tick(0.25).next_to(self.pins["note"].body, RIGHT, buff=0.3)
        self.play(FadeIn(done, scale=0.6), ring(now[0], BLUE), run_time=0.8)
        self.unpin("note", FadeOut(done))
        self.wait(1.2)

        self.finish("S06_order")

    # ==================================== 7. COUNTING WITHOUT TRACING ======

    def counting(self):
        self.begin("S07_counting", "Counting Without Tracing", "Counting without tracing")

        long_rows = VGroup(*[Line(ORIGIN, RIGHT * 3.0, color=FAINT, stroke_width=4) for _ in range(14)])
        place(long_rows.arrange(DOWN, buff=0.16), x=BOARD_X - 0.8, y=0.7)
        long_l = text("100 rows?", LABEL, BAD).next_to(long_rows, RIGHT, buff=0.4)

        heads = [place(code(s), left=CODE_X, y=y) for s, y in (("for (i = 1; i <= 100; i++)", 2.15),
                                                                ("for (i = 0; i < 100; i++)", 1.5),
                                                                ("for (i = 5; i <= 12; i++)", 0.85))]
        blank_x = 1.45
        blanks = [Rectangle(width=1.3, height=0.5, stroke_color=MUTED, stroke_width=2).move_to([blank_x, h.get_y(), 0])
                  for h in heads]
        runs_head = place(text("body runs", SMALL, MUTED), x=blank_x, y=2.6)
        ans = [code("100", CODE, GOOD).move_to(blanks[0]), code("100", CODE, GOOD).move_to(blanks[1])]
        wrong7 = code("7", CODE, MUTED).move_to(blanks[2]).shift(LEFT * 0.3)
        right8 = code("8", CODE, GOOD).move_to(blanks[2]).shift(RIGHT * 0.3)

        # five to twelve: eight values, seven gaps
        xs = [-4.6 + 0.62 * k for k in range(8)]
        dots = [Dot([x, -0.2, 0], radius=0.08, color=INK) for x in xs]
        stops = [VGroup(d, code(str(v)).move_to([x, -0.65, 0])) for d, v, x in zip(dots, range(5, 13), xs)]
        arcs = [ArcBetweenPoints(a.get_center() + UP * 0.1, b.get_center() + UP * 0.1, angle=-PI / 2, color=BROWN,
                                 stroke_width=3) for a, b in zip(dots, dots[1:])]
        gaps_l = place(text("7 gaps", SMALL, BROWN), x=0.55, y=0.0)
        vals_l = place(text("8 values", SMALL, BLUE), x=0.8, y=-0.65)
        formula = place(code("12 - 5 + 1 = 8", LABEL), x=-2.4, y=-1.2)
        self.fit(long_rows, long_l, runs_head, gaps_l, vals_l, formula, *heads, *blanks, *stops)
        self.apart(VGroup(*heads), VGroup(*blanks))
        self.apart(stops[-1], vals_l)

        def count_row(head, expr):
            runs = phrase(text("the body runs", LABEL), code(expr, CODE_BIG, BLUE), text("times", LABEL))
            row = column(code(head), runs, buff=0.15)
            runs.shift(RIGHT * 0.6)
            return row

        rule_full = column(text("Counting the runs", BODY, BLUE, BOLD),
                           count_row("for (i = a; i <= b; i++)", "b - a + 1"),
                           count_row("for (i = a; i < b; i++)", "b - a"),
                           fitted_text("If the condition is false at the very start, the body runs 0 times.", 6.6,
                                       LABEL), buff=0.3)
        place(rule_full, x=BOARD_X, y=0.6)
        count_card = pin_card(phrase(code("i <= b", PIN_CODE), code("b - a + 1", PIN_CODE, BLUE), text("times", SMALL)),
                              phrase(code("i < b", PIN_CODE), code("b - a", PIN_CODE, BLUE), text("times", SMALL)),
                              text("False at start: 0 times", SMALL))

        # Kabir's loop: the step is not one, so he lists the values
        dn = place(Listing(DOWN3, CODE_BIG), left=-4.6, top=2.5)
        dn.paint_for(0, "i = 10", "i > 0", "i -= 3")
        vals = [place(code(s, BODY), x=-4.2 + 1.25 * k, y=0.6) for k, s in enumerate(("10", "7", "4", "1", "-2"))]
        hops = []
        for a, b in zip(vals, vals[1:]):
            hop = CurvedArrow(a.get_top() + UP * 0.1, b.get_top() + UP * 0.1, angle=-PI / 3, color=MUTED,
                              stroke_width=3, tip_length=0.15)
            hops.append(VGroup(hop, code("-3", PIN_CODE, MUTED).next_to(hop, UP, buff=0.05)))
        check = place(phrase(code("-2 > 0", LABEL), code("false", LABEL, BAD)), x=1.0, y=-0.25)
        fail_l = place(text("first failing value", SMALL, BAD), x=1.0, y=-0.75)
        out_line = place(phrase(text("Output:", LABEL), code("10 7 4 1", CODE_BIG, GOOD), text("4 values", SMALL, MUTED)),
                         left=-4.6, y=-1.25)
        tip = place(text("Unusual step?  List the values.", LABEL, BLUE, BOLD), x=BOARD_X, y=-0.5)
        self.fit(rule_full, dn, check, fail_l, out_line, tip, *vals, *hops)
        self.apart(dn, VGroup(*hops))
        self.apart(fail_l, out_line)

        def start_count():
            self.wipe()
            self.play(LaggedStart(*[FadeIn(h, shift=RIGHT * 0.2) for h in heads], lag_ratio=0.3), FadeIn(runs_head),
                      *[Create(b) for b in blanks], run_time=1.4)

        self.T("s7_01", "Tracing is safe, but it is slow. In the exam you will not trace a loop that runs a hundred "
                        "times. So let us learn to count.",
               ("slow", lambda: LaggedStart(*[Create(l) for l in long_rows], lag_ratio=0.1, run_time=1.5)),
               ("hundred", lambda: FadeIn(long_l, shift=LEFT * 0.2)),
               ("count", start_count), look="smile")
        self.T("s7_02", "First one.", ("First", lambda: ring(heads[0])), look="ask", pose="point")
        self.K("s7_03", "A hundred.", ("hundred", lambda: FadeIn(ans[0], scale=1.2)))
        self.T("s7_04", "Second.", ("Second", lambda: ring(heads[1])), look="ask", pose="point")
        self.M("s7_05", "Also a hundred. Zero to ninety-nine.", ("hundred", lambda: FadeIn(ans[1], scale=1.2)))
        self.T("s7_06", "Third.", ("Third", lambda: ring(heads[2])), look="ask", pose="point")
        self.A("s7_07", "Seven. Twelve minus five.",
               ("Seven", lambda: FadeIn(wrong7, scale=1.2)), look="happy", pose="raise")
        self.M("s7_08", "Five, six, seven, eight, nine, ten, eleven, twelve. That is eight.",
               *[(word, (lambda k=k: FadeIn(stops[k], shift=UP * 0.1)), 0.25)
                 for k, word in enumerate(("Five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve"))],
               (("eight", 2), lambda: [Create(strike(wrong7)), FadeIn(right8, scale=1.2)]),
               look="think", pose="write", others={"A": "confused"})
        self.A("s7_09", "Eight. I dropped one.", look="oops")
        self.T("s7_10", "You subtracted. Subtraction counts the gaps between the values, not the values themselves. "
                        "When both ends are included, you add one back.",
               ("gaps", lambda: [LaggedStart(*[Create(a) for a in arcs], lag_ratio=0.15), FadeIn(gaps_l)]),
               (("values", 2), lambda: [*[d.animate.set_color(BLUE) for d in dots], FadeIn(vals_l)]),
               ("add", lambda: FadeIn(formula, shift=UP * 0.15)), look="smile")

        # the rule card, in full; then it is pinned
        self.quiet()
        self.wipe()
        self.play(LaggedStart(*[FadeIn(row, shift=RIGHT * 0.15) for row in rule_full], lag_ratio=0.35), run_time=2.2)
        self.wait(3.5)
        self.unpin("entry")
        self.pin("count", count_card, source=rule_full)

        self.K("s7_11", "Ma'am, what if it does not go up by one?", look="ask", pose="raise")
        self.T("s7_12", "Then put the formula away and write the values down. Try this one, Kabir.",
               ("Try", lambda: FadeIn(dn, shift=UP * 0.2)), look="smile", pose="point")
        self.to_board("K")
        self.K("s7_13", "Ten. Then seven. Then four. Then one. Then minus two, and minus two is not greater than "
                        "zero, so it stops.",
               ("Ten", lambda: FadeIn(vals[0], scale=1.2), 0.4),
               ("seven", lambda: [FadeIn(hops[0]), FadeIn(vals[1], scale=1.2)], 0.4),
               ("four", lambda: [FadeIn(hops[1]), FadeIn(vals[2], scale=1.2)], 0.4),
               ("one", lambda: [FadeIn(hops[2]), FadeIn(vals[3], scale=1.2)], 0.4),
               ("minus", lambda: [FadeIn(hops[3]), FadeIn(vals[4], scale=1.2)], 0.4),
               ("not", lambda: FadeIn(check, shift=UP * 0.1)),
               ("stops", lambda: vals[4].animate.set_color(BAD)), pose="point")
        self.T("s7_14", "Output?", look="ask")
        self.K("s7_15", "Ten, seven, four, one. Four values.",
               ("Ten", lambda: [*[v.animate.set_color(GOOD) for v in vals[:4]], FadeIn(out_line[:2])]),
               ("values", lambda: FadeIn(out_line[2])), pose="low")
        self.T("s7_16", "And what is i holding after the loop?", look="ask")
        self.K("s7_17", "Minus two. The first value that failed.",
               ("Minus", lambda: [ring(vals[4], BAD), FadeIn(fail_l)]),
               ("first", lambda: self.pinned("rules")), pose="point")
        self.to_seat("K")
        self.T("s7_18", "Four values took you five seconds. When the step is unusual, listing is faster and safer "
                        "than any formula.",
               ("listing", lambda: [FadeOut(VGroup(check, fail_l)), FadeIn(tip, shift=UP * 0.15)]),
               look="smile", others={"K": "happy"})

        self.finish("S07_counting")

    # ================================ 8. WHAT EXACTLY IS THE BODY? =========

    def the_body(self):
        self.begin("S08_body", "What Exactly Is the Body?", "What exactly is the body?")

        fact1 = VGroup(tick(), text("Fact 1:  when each part runs", BODY)).arrange(RIGHT, buff=0.3)
        fact2 = phrase(text("Fact 2:", BODY, BLUE, BOLD), text("what counts as the body?", BODY))
        place(column(fact1, fact2, buff=0.5), x=BOARD_X, y=0.9)

        # one statement, or one block
        ab = place(Listing(AB, CODE_BIG), left=-4.7, top=2.5)
        ab.paint_for(0, "i = 1", "i <= 3", "i++")
        four = 4 * ab.unit                                      # one step of indentation
        guess_a = place(phrase(text("Aarav:", SMALL, MUTED), code("A B A B A B")), left=-4.7, y=0.3)
        guess_m = place(phrase(text("Meera:", SMALL, MUTED), code("A A A B")), left=-4.7, y=-0.25)
        open_at = ab.lines[0].get_right() + RIGHT * 0.3
        close_at = np.array([-4.7 + 0.1, ab.lines[2].get_y() - 0.49, 0.0])
        ghosts = VGroup(code("{", CODE_BIG, MUTED).move_to(open_at), code("}", CODE_BIG, MUTED).move_to(close_at))
        braces = VGroup(code("{", CODE_BIG).move_to(open_at), code("}", CODE_BIG).move_to(close_at))
        out_ab = place(phrase(text("Output:", LABEL), code("A A A B", CODE_BIG, GOOD)), left=-4.7, y=-0.95)
        m_tick = tick(0.25).next_to(guess_m, RIGHT, buff=0.3)
        a_strike = strike(guess_a[1])
        body_box = self.frame(ab.lines[1], BLUE)
        body_l = text("the body", SMALL, BLUE, BOLD).next_to(body_box, RIGHT, buff=0.25)
        block_box = self.frame(VGroup(ab.lines[1], ab.lines[2]), BLUE)
        block_l = text("one block", SMALL, BLUE, BOLD).next_to(block_box, RIGHT, buff=0.25)
        flat_l = place(text("The compiler sees no indentation", LABEL, BROWN, BOLD), x=BOARD_X, y=0.3)
        self.fit(fact1, fact2, ab, guess_a, guess_m, ghosts, out_ab, body_l, block_l, flat_l)
        self.apart(ghosts[1], guess_a)

        # the null statement
        semi = code(";", 72).move_to([-3.6, 1.1, 0])
        semi_box = Square(1.3, stroke_color=BLUE, stroke_width=3).move_to(semi)
        self.validator.ignore(semi_box)
        about = column(text("the null statement", BODY, BLUE, BOLD),
                       VGroup(tick(), text("perfectly legal C", LABEL)).arrange(RIGHT, buff=0.25),
                       text("it does nothing", LABEL, MUTED), buff=0.35).next_to(semi_box, RIGHT, buff=0.7)

        # question 2, large
        q2b = place(Listing(Q2_CORE, CODE_BIG), left=-4.7, top=2.3)
        k_ring = self.circle(q2b.part(0, ";", 3), 0.24)
        k_body = text("the body", SMALL, BLUE, BOLD).next_to(k_ring, RIGHT, buff=0.4)
        k_arrow = arrow(k_body.get_left() + LEFT * 0.1, k_ring.get_right() + RIGHT * 0.05, BLUE, 3, 0.15)
        not_in = text("not in the loop", SMALL, BROWN).next_to(q2b.lines[1], RIGHT, buff=0.4).shift(LEFT * 4 * q2b.unit)
        warn = place(tag("warning: empty loop body", BROWN), x=BOARD_X, y=0.5)
        valid = place(VGroup(tick(), text("Valid C: it compiles and runs", LABEL)).arrange(RIGHT, buff=0.25),
                      x=BOARD_X, y=-0.2)
        owns = place(text("A loop owns exactly one statement.", LABEL, BLUE, BOLD), x=BOARD_X, y=-0.95)
        body_card = pin_card(text("Body = one statement", SMALL),
                             phrase(code(";", PIN_CODE, FLASH), text("alone is a statement", SMALL)))
        self.fit(semi_box, about, q2b, k_body, not_in, warn, valid, owns)

        # the three parts can be left empty
        hdr = place(Listing("for (i = 1; i <= n; i++)", BODY), x=BOARD_X, y=1.6)
        h_parts = hdr.paint_for(0, "i = 1", "i <= n", "i++")
        semis = [self.circle(hdr.part(0, ";", k), 0.26) for k in (1, 2)]
        always = text("always true", SMALL, BLUE).next_to(h_parts[1], DOWN, buff=0.55)
        always_a = arrow(always.get_top() + UP * 0.05, h_parts[1].get_bottom() + DOWN * 0.12, BLUE, 3, 0.15)
        forever = VGroup(Arc(radius=0.32, start_angle=PI / 2, angle=-1.6 * PI, color=BAD,
                             stroke_width=4).add_tip(tip_length=0.18),
                         text("never ends on its own", LABEL, BAD, BOLD)).arrange(RIGHT, buff=0.3)
        place(forever, x=BOARD_X, y=-0.6)

        # a variable declared inside the brackets
        c99 = place(Listing(C99, CODE_BIG), left=-4.8, top=2.05)
        scope = self.frame(VGroup(c99.lines[0], c99.lines[1]), BLUE)
        scope_l = text("i exists only in here", SMALL, BLUE, BOLD).next_to(scope, UP, buff=0.12).align_to(scope, LEFT)
        bad_i = c99.part(2, "i", 2)
        err = place(text("i does not exist here: compilation error", SMALL, BAD), left=-4.8, y=0.0)
        err_a = arrow([bad_i.get_x(), err.get_top()[1] + 0.05, 0], [bad_i.get_x(), bad_i.get_bottom()[1] - 0.08, 0],
                      BAD, 3, 0.15)
        allowed = place(VGroup(tick(), text("Allowed from C99 onward", LABEL)).arrange(RIGHT, buff=0.25),
                        left=-4.8, y=-0.7)
        self.fit(hdr, always, forever, c99, scope_l, err, allowed)

        def test():
            self.wipe()
            self.play(FadeIn(ab, shift=UP * 0.2), run_time=0.7)

        def show_q2():
            self.wipe(TransformFromCopy(self.pins["q2"].code, q2b), keep=(q2b,), run_time=1.0)

        def show_header():
            self.wipe()
            self.play(FadeIn(hdr, shift=UP * 0.2), run_time=0.6)

        def show_c99():
            self.wipe()
            self.play(FadeIn(c99, shift=UP * 0.2), run_time=0.6)

        self.T("s8_01", "That was the first missing fact. Now the second. Kabir, you asked whether that semicolon is "
                        "allowed. To answer that, tell me first: how much does a for loop own?",
               ("first", lambda: FadeIn(fact1, shift=RIGHT * 0.2)),
               ("second", lambda: FadeIn(fact2, shift=RIGHT * 0.2)),
               ("semicolon", lambda: self.pinned("q2")),
               ("own", lambda: hl(fact2[1], 1.06)), look="ask")
        self.K("s8_02", "Everything under it?", look="ask")
        self.T("s8_03", "Let us test that.", ("test", test), look="smile", pose="point")
        self.T("s8_04", "What is printed?", look="ask")
        self.A("s8_05", "A B, A B, A B.",
               (None, lambda: FadeIn(guess_a, shift=RIGHT * 0.2)), look="happy", pose="raise")
        self.M("s8_06", "There are no braces.",
               ("braces", lambda: FadeIn(ghosts)), look="think")
        self.T("s8_07", "And?", look="ask")
        self.M("s8_08", "Then I think only the first printf repeats. A, A, A, and then B once.",
               ("first", lambda: [FadeOut(ghosts), hl(ab.lines[1])]),
               ("A", lambda: FadeIn(guess_m, shift=RIGHT * 0.2)), look="think", pose="write")
        self.quiet()
        self.play(FadeIn(out_ab, shift=UP * 0.15), run_time=0.6)
        self.play(FadeIn(m_tick, scale=0.6), Create(a_strike), *self.react("A", "oops"), *self.react("M", "happy"),
                  run_time=0.6)
        self.T("s8_09", "A for loop owns exactly one statement. The one that comes immediately after the closing "
                        "bracket. If you want it to own more, you wrap them in braces, and the braces make them one "
                        "block.",
               ("one", lambda: [Create(body_box), FadeIn(body_l)]),
               ("immediately", lambda: ab.lines[2].animate.shift(LEFT * four)),
               ("braces", lambda: [ab.lines[2].animate.shift(RIGHT * four), FadeIn(braces),
                                   Transform(body_box, block_box), Transform(body_l, block_l)]), pose="point")
        self.A("s8_10", "But the indentation.",
               (None, lambda: FadeOut(VGroup(braces, body_box, body_l, guess_a, guess_m, a_strike, m_tick, out_ab))),
               look="confused")
        self.T("s8_11", "Indentation is for humans, Aarav. The compiler does not read it. The examiner knows that, and "
                        "uses it against you.",
               ("humans", lambda: [hl(ab.lines[1]), hl(ab.lines[2])]),
               ("compiler", lambda: [ab.lines[1].animate.shift(LEFT * four), ab.lines[2].animate.shift(LEFT * four),
                                     FadeIn(flat_l, shift=UP * 0.15)]),
               ("examiner", lambda: self.pinned("q2")), look="smile")
        self.T("s8_12", "Now, one more fact about C. A semicolon standing by itself is a complete statement. It is "
                        "called the null statement. It is perfectly legal, and it does nothing.",
               (None, self.wipe),
               ("semicolon", lambda: [FadeIn(semi, scale=1.3), Create(semi_box)]),
               ("null", lambda: FadeIn(about[0], shift=RIGHT * 0.2)),
               ("legal", lambda: FadeIn(about[1], shift=RIGHT * 0.2)),
               ("nothing", lambda: FadeIn(about[2], shift=RIGHT * 0.2)), pose="point")
        self.K("s8_13", "So the one statement after the bracket is the semicolon.",
               ("statement", show_q2),
               ("semicolon", lambda: Create(k_ring)), look="think", pose="point")
        self.T("s8_14", "Go on.", look="smile")
        self.K("s8_15", "So the body of that loop is nothing. The loop runs, but it repeats nothing.",
               ("body", lambda: [FadeIn(k_body), GrowArrow(k_arrow)]),
               (("nothing", 2), lambda: [q2b.lines[1].animate.shift(LEFT * 4 * q2b.unit), FadeIn(not_in)]),
               look="surprised")
        self.M("s8_16", "So it is not a compilation error?", look="ask")
        self.T("s8_17", "It is not. Some compilers will warn you, because it is so often a mistake. But it is valid C, "
                        "and it runs.",
               ("warn", lambda: FadeIn(warn, shift=UP * 0.15)),
               ("valid", lambda: FadeIn(valid, shift=UP * 0.15)), look="smile")
        self.quiet()
        self.play(FadeIn(owns, shift=UP * 0.15), run_time=0.6)
        self.wait(1.2)
        self.pin("body", body_card, source=owns)

        self.K("s8_18", "Then are all three parts inside the brackets compulsory?", look="ask", pose="raise")
        self.T("s8_19", "Good question. No. Any of the three can be left empty. What cannot be left out are the two "
                        "semicolons that separate them.",
               ("No", show_header),
               ("empty", lambda: LaggedStart(*[FadeOut(p) for p in h_parts], lag_ratio=0.4, run_time=1.5)),
               ("semicolons", lambda: [Create(c) for c in semis]), look="smile", pose="point")
        self.T("s8_20", "And if the condition is missing, C treats it as always true. So that header, with nothing "
                        "inside, is a loop that never ends on its own.",
               ("always", lambda: [FadeIn(always), GrowArrow(always_a)]),
               ("never", lambda: FadeIn(forever, shift=UP * 0.15)))
        self.M("s8_21", "Ma'am, I have seen code where the variable is declared inside the brackets. For, int i equals "
                        "one.",
               ("declared", show_c99),
               ("int", lambda: hl(c99.part(0, "int i"), 1.3)), look="ask", pose="raise")
        self.T("s8_22", "That is allowed in modern C, from the C ninety-nine standard onward. But it changes one thing. A "
                        "variable declared there exists only inside the loop.",
               ("allowed", lambda: FadeIn(allowed, shift=UP * 0.15)),
               ("only", lambda: [Create(scope), FadeIn(scope_l)]), look="smile")
        self.quiet()
        self.play(bad_i.animate.set_color(BAD), FadeIn(err), GrowArrow(err_a), run_time=0.8)
        self.wait(1.5)
        self.A("s8_23", "So in question one, the examiner declared i outside the loop on purpose.",
               ("outside", lambda: self.pinned("q1")), look="think")
        self.T("s8_24", "Precisely so they could ask you about it afterwards.", look="smile")

        self.finish("S08_body")

    # ========================================= 9. BACK TO THE BOARD ========

    def back_to_the_board(self):
        self.begin("S09_back", "Back to the Board", "Back to the board")

        # question 1: Aarav traces it
        core = place(Listing(Q1_CORE), left=CODE_X, top=2.7)
        core.paint_for(0, "i = 1", "i <= 5", "i++")
        q_l = place(text("Question 1", LABEL, BLUE, BOLD), left=0.1, y=2.35)
        n_checks = place(text("6 checks", SMALL, BLUE), left=0.1, y=1.9)
        n_adds = place(text("5 additions", SMALL), left=0.1, y=1.55)
        opts = place(Options([("A", "15 5", True), ("B", "15 6", True), ("C", "10 5", True), ("D", "10 6", True)], BODY),
                     left=0.1, y=0.0)
        tb = Table([code("i", CODE, INK, BOLD), code("i <= 5", CODE, BLUE), code("sum", CODE, INK, BOLD)],
                   (1.1, 1.7, 1.2), left=CODE_X, top=1.42, row_h=0.4)
        c = {}
        for r, (i, total) in enumerate(zip(range(1, 7), (1, 3, 6, 10, 15, None))):
            c[r, 0] = tb.put(r, 0, code(str(i), CODE, INK if i <= 5 else BAD))
            c[r, 1] = tb.put(r, 1, code("true") if i <= 5 else code("false", CODE, BAD))
            c[r, 2] = tb.put(r, 2, code(str(total)) if total else code("-", CODE, MUTED))
        self.fit(core, q_l, n_checks, n_adds, opts, tb, *c.values())
        self.apart(core, tb)
        self.apart(VGroup(core, tb), VGroup(q_l, n_checks, n_adds, opts))

        def fill(*keys):
            return lambda: [FadeIn(c[k]) for k in keys]

        self.unpin("q1", FadeIn(VGroup(core, q_l, opts), shift=UP * 0.15))
        self.T("s9_01", "Aarav. You said A. Come and check your own answer.",
               ("A", lambda: hl(opts.rows["A"])), look="smile", pose="offer")
        self.to_board("A")
        self.play(FadeIn(tb, shift=UP * 0.15), run_time=0.5)
        self.A("s9_02", "i is one. One is less than or equal to five, so sum becomes one. Then i becomes two. Sum is "
                        "three. i is three, sum is six. i is four, sum is ten. i is five, and five is still less than "
                        "or equal to five, so sum becomes fifteen.",
               ("one", fill((0, 0)), 0.35),
               ("less", fill((0, 1)), 0.35),
               ("becomes", fill((0, 2)), 0.35),
               ("two", fill((1, 0), (1, 1)), 0.35),
               ("three", fill((1, 2)), 0.35),
               (("three", 2), fill((2, 0), (2, 1)), 0.35),
               ("six", fill((2, 2)), 0.35),
               ("four", fill((3, 0), (3, 1)), 0.35),
               ("ten", fill((3, 2)), 0.35),
               (("five", 2), fill((4, 0)), 0.35),
               ("still", fill((4, 1)), 0.35),
               ("fifteen", fill((4, 2)), 0.35), pose="point")
        self.T("s9_03", "And then?", look="ask")
        self.A("s9_04", "Then the update runs once more. i becomes six. Six is less than or equal to five is false. "
                        "The loop ends.",
               ("update", lambda: hl(core.part(0, "i++"), 1.4)),
               ("six", fill((5, 0))),
               ("false", fill((5, 1), (5, 2))), pose="point")
        self.A("s9_05", "So the printf prints fifteen and six. It is B.",
               ("printf", lambda: core.focus(2)),
               ("fifteen", lambda: ring(c[4, 2])),
               ("six", lambda: ring(c[5, 0], BAD)),
               ("B", lambda: [core.focus(None), hl(opts.rows["B"])]), look="happy", pose="low")
        self.T("s9_06", "Why did A look right to you?",
               ("A", lambda: hl(opts.rows["A"])), look="ask")
        self.A("s9_07", "Because I stopped at the last good value. The loop stops at the first bad one.",
               ("good", lambda: [c[4, 0].animate.set_color(GOOD), ring(c[4, 0], GOOD)]),
               ("bad", lambda: [ring(c[5, 0], BAD), self.pinned("rules")]), look="smile")
        self.T("s9_08", "And C and D?", look="ask")
        self.A("s9_09", "Ten would be the sum if the condition were only less than five. Then the loop would stop one "
                        "step earlier. But the question says less than or equal to.",
               ("Ten", lambda: ring(c[3, 2])),
               ("earlier", lambda: [hl(opts.rows["C"]), hl(opts.rows["D"])]),
               ("equal", lambda: hl(core.part(0, "<="), 1.6)), pose="point")
        self.play(*opts.right("B"), run_time=0.7)
        self.T("s9_10", "Six checks, five additions. One more check than body. Exactly as the rule says.",
               ("Six", lambda: FadeIn(n_checks, shift=RIGHT * 0.2)),
               ("five", lambda: FadeIn(n_adds, shift=RIGHT * 0.2)),
               ("rule", lambda: self.pinned("rules")), look="smile", others={"A": "happy"})
        self.to_seat("A")
        self.wipe()
        self.pin("q1_done", self.done_card(1, "B.  15 6"))

        # question 2: Kabir finds the body first
        core2 = place(Listing(Q2_CORE, CODE_BIG), left=-4.8, top=2.6)
        core2.paint_for(0, "i = 0", "i < 5", "i++")
        four = 4 * core2.unit
        c_ring = self.circle(core2.part(0, ";", 3), 0.24)
        c_body = text("the body", SMALL, BLUE, BOLD).next_to(c_ring, RIGHT, buff=0.4)
        c_arrow = arrow(c_body.get_left() + LEFT * 0.1, c_ring.get_right() + RIGHT * 0.05, BLUE, 3, 0.15)
        outside = text("outside the loop", SMALL, BROWN).next_to(core2.lines[1], RIGHT, buff=0.4).shift(LEFT * four)
        i_lab = place(code("i :", LABEL, MUTED), left=-4.8, y=1.2)
        vals = [place(code(str(k), BODY, GOOD if k < 5 else BAD), x=-3.6 + 0.8 * k, y=1.2) for k in range(6)]
        rounds = place(text("5 rounds of nothing", SMALL, MUTED), x=-2.0, y=0.65)
        fail = place(text("first failing", SMALL, BAD), x=0.6, y=0.65)
        out2 = place(phrase(text("Output:", LABEL), code("5", CODE_BIG, GOOD)), left=-4.8, y=0.05)
        opts2 = Options([("A", "0 1 2 3 4", True), ("B", "1 2 3 4 5", True), ("C", "5", True),
                         ("D", "Compilation error", False)], LABEL)
        for letter, x, y in (("A", -4.8, -0.75), ("B", -1.4, -0.75), ("C", -4.8, -1.25), ("D", -1.4, -1.25)):
            place(opts2.rows[letter], left=x, y=y)
        self.fit(core2, c_body, outside, i_lab, rounds, fail, out2, opts2, *vals)
        self.apart(core2, VGroup(i_lab, *vals))
        self.apart(rounds, fail)
        self.apart(opts2.rows["A"], opts2.rows["B"])
        self.apart(opts2.rows["C"], opts2.rows["D"])
        self.apart(out2, opts2)

        def step_in(k):
            return lambda: FadeIn(vals[k], scale=1.2)

        self.unpin("q2", FadeIn(VGroup(core2, opts2), shift=UP * 0.15))
        self.T("s9_11", "Kabir. This one is yours.", look="smile", pose="offer")
        self.to_board("K")
        self.K("s9_12", "Find the body first. The body is this semicolon. So the loop repeats nothing.",
               ("body", lambda: self.pinned("body")),
               ("semicolon", lambda: [Create(c_ring), FadeIn(c_body), GrowArrow(c_arrow)]),
               ("nothing", lambda: [core2.lines[1].animate.shift(LEFT * four), FadeIn(outside)]), pose="point")
        self.K("s9_13", "i starts at zero. It passes the check for zero, one, two, three and four. Five rounds of "
                        "doing nothing. Then i becomes five, and five is not less than five, so the loop ends.",
               ("zero", lambda: [FadeIn(i_lab), FadeIn(vals[0], scale=1.2)], 0.4),
               ("one", step_in(1), 0.3),
               ("two", step_in(2), 0.3),
               ("three", step_in(3), 0.3),
               ("four", step_in(4), 0.3),
               ("rounds", lambda: FadeIn(rounds, shift=UP * 0.1)),
               (("five", 2), step_in(5)),
               ("not", lambda: FadeIn(fail, shift=UP * 0.1)), pose="low")
        self.K("s9_14", "Now the printf. It was never inside the loop. It runs once, and i is five.",
               ("printf", lambda: hl(core2.lines[1])),
               ("once", lambda: hl(outside)),
               ("five", lambda: FadeIn(out2, shift=RIGHT * 0.2)), pose="point")
        self.K("s9_15", "It prints five. The answer is C.",
               ("C", lambda: hl(opts2.rows["C"])), look="happy")
        self.T("s9_16", "And the other three?", look="ask")
        self.K("s9_17", "A is what the indentation wants me to believe. B, nothing in this program prints one to "
                        "five. And D was my own answer, and it is wrong, because a semicolon alone is a legal "
                        "statement.",
               ("A", lambda: opts2.strike("A")),
               ("B", lambda: opts2.strike("B")),
               ("D", lambda: opts2.strike("D")),
               ("legal", lambda: self.pinned("body")), pose="low")
        self.play(*opts2.right("C"), run_time=0.7)
        self.wait(0.8)
        self.to_seat("K")
        self.wipe()
        self.pin("q2_done", self.done_card(2, "C.  5"))

        # the method, in three lines
        check_t = text("Reading a for loop in the exam", BODY, BLUE, BOLD)
        steps = numbered(["Find the body.", "Count or list.", "First failing value."], BODY)
        place(column(check_t, steps, buff=0.5), x=BOARD_X, y=0.6)
        self.fit(check_t, steps)
        self.T("s9_18", "That is the method for every for loop question you will meet. One. Find the body first. Look "
                        "for braces, and look for a stray semicolon. Two. Count the rounds, or list the values. "
                        "Three. Remember that the variable leaves the loop holding the first value that failed.",
               ("method", lambda: FadeIn(check_t, shift=UP * 0.15)),
               ("One", lambda: [FadeIn(steps[0], shift=RIGHT * 0.2), self.pinned("body")]),
               ("Two", lambda: [FadeIn(steps[1], shift=RIGHT * 0.2), self.pinned("count")]),
               ("Three", lambda: [FadeIn(steps[2], shift=RIGHT * 0.2), self.pinned("rules")]), pose="point")

        self.finish("S09_back")

    # ========================================= 10. CHOOSING THE LOOP =======

    def choosing(self):
        self.begin("S10_choosing", "Choosing the Loop", "Choosing the loop")
        self.change_places({"T": "sit"})             # Ms. Rao sits down at her desk

        def loop_card(name, when, x):
            box = RoundedRectangle(width=2.3, height=2.7, corner_radius=0.12, stroke_color=MUTED, stroke_width=2,
                                   fill_color=FILL, fill_opacity=1).move_to([x, -0.15, 0])
            card = VGroup(box, code(name, CODE_BIG, BLUE, BOLD).move_to(box.get_top() + DOWN * 0.4),
                          text(wrap_words(when, 12), SMALL).move_to(box.get_center() + DOWN * 0.35))
            card.box, card.title, card.why = card
            return card

        cards = [loop_card("do-while", "must happen at least once", BOARD_X - 2.5),
                 loop_card("while", "repeat until something changes; count unknown", BOARD_X),
                 loop_card("for", "count known before the loop starts", BOARD_X + 2.5)]
        cases = [place(text(s, LABEL, BROWN), x=BOARD_X, y=2.2)
                 for s in ("Show the menu, then ask: continue?", "Read numbers until the user types -1",
                           "Enter the marks of 60 students", "Same work, three ways?")]
        self.fit(*cards, *cases)

        def answer(k):
            return lambda: [FadeIn(cards[k].why), cards[k].box.animate.set_stroke(BLUE, 3)]

        plan = place(Listing("for (i = 1; i <= n; i++)", BODY), x=BOARD_X, y=1.9)
        parts = plan.paint_for(0, "i = 1", "i <= n", "i++")
        names = [text(s, SMALL, color).next_to(piece, DOWN, buff=0.25)
                 for s, color, piece in zip(("start", "stop", "step"), (GREEN, BLUE, BROWN), parts)]

        def becomes():
            return arrow(LEFT * 0.3, RIGHT * 0.3, MUTED, 3, 0.15)

        trap1 = place(phrase(code("i < 5", CODE_BIG), becomes(), code("i <= 5", CODE_BIG, BLUE),
                             text("one more round", LABEL, MUTED)), x=BOARD_X, y=0.3)
        trap2 = place(phrase(code("i++)", CODE_BIG), becomes(), code("i++);", CODE_BIG, BAD),
                             text("an empty body", LABEL, MUTED)), x=BOARD_X, y=-0.45)
        closing = place(text("You now know where to look", LABEL, BLUE, BOLD), x=BOARD_X, y=-1.2)
        self.fit(plan, trap1, trap2, closing, *names)

        def show_plan():
            self.wipe()
            self.play(FadeIn(plan, shift=UP * 0.2), run_time=0.6)

        self.T("s10_01", "You now know three loops. So when do you reach for which? I will give you a situation, you "
                         "give me the loop.",
               ("three", lambda: [FadeIn(VGroup(card.box, card.title), shift=UP * 0.15) for card in cards]),
               look="smile")
        self.T("s10_02", "A cash machine must show its menu, and then ask whether you want to continue.",
               ("menu", lambda: FadeIn(cases[0], shift=DOWN * 0.1)), look="ask")
        self.A("s10_03", "Do-while. The menu has to appear at least once.",
               ("once", answer(0)), look="happy", pose="raise")
        self.T("s10_04", "Keep reading numbers until the user types minus one.",
               ("reading", lambda: [FadeOut(cases[0]), FadeIn(cases[1], shift=DOWN * 0.1)]), look="ask")
        self.M("s10_05", "While. We do not know how many numbers there will be.",
               ("know", answer(1)), look="smile")
        self.T("s10_06", "Enter the marks of sixty students.",
               ("marks", lambda: [FadeOut(cases[1]), FadeIn(cases[2], shift=DOWN * 0.1)]), look="ask")
        self.K("s10_07", "For. We know the count before we begin.",
               ("count", answer(2)), look="smile")
        self.T("s10_08", "Can the same work be done with any of the three?",
               ("same", lambda: [FadeOut(cases[2]), FadeIn(cases[3], shift=DOWN * 0.1)]), look="ask")
        self.M("s10_09", "It can. We wrote the table of seven with all three this morning.",
               ("seven", lambda: [hl(card.title) for card in cards]), look="smile")
        self.T("s10_10", "Then why choose?", look="ask")
        self.K("s10_11", "Because with for, the plan is on one line. I can see where it starts, where it stops, and "
                         "how it moves. And I cannot bury the update forty lines down.",
               ("plan", show_plan),
               ("starts", lambda: [hl(parts[0], 1.2), FadeIn(names[0])]),
               ("stops", lambda: [hl(parts[1], 1.2), FadeIn(names[1])]),
               ("moves", lambda: [hl(parts[2], 1.2), FadeIn(names[2])]), look="smile")
        self.T("s10_12", "That is the reason programmers like it. It is also the reason examiners like it. When the "
                         "whole plan sits on one line, changing a single character changes the entire answer. Less "
                         "than becomes less than or equal to. A semicolon appears where it should not. You now know "
                         "where to look.",
               ("single", lambda: ring(plan.lines[0])),
               ("Less", lambda: FadeIn(trap1, shift=RIGHT * 0.2)),
               ("semicolon", lambda: FadeIn(trap2, shift=RIGHT * 0.2)),
               ("look", lambda: FadeIn(closing, shift=UP * 0.15)), look="smile")

        self.change_places({"T": "stand"})
        self.finish("S10_choosing")

    # ===================================== 11. ONE LINE, THREE HABITS ======

    def three_habits(self):
        self.begin("S11_habits", "One Line, Three Habits", "One line, three habits")

        # the board keeps only the cycle and the checklist
        fl = self.flow(dy=1.35)
        habits = place(numbered(["Find the body.", "Count or list.", "First failing value."], LABEL, 0.14),
                       x=BOARD_X, top=0.05)
        self.fit(fl, habits)
        self.apart(fl, habits)

        # five marks, visited with a counter
        boxes = VGroup(*[Square(0.95, stroke_color=BLUE, stroke_width=3, fill_color=FILL, fill_opacity=1)
                         for _ in MARKS]).arrange(RIGHT, buff=0).move_to([BOARD_X, 1.3, 0])
        marks = VGroup(*[code(str(m), BODY).move_to(b) for m, b in zip(MARKS, boxes)])
        marks_l = code("marks", LABEL, MUTED).next_to(boxes, UP, buff=0.18)
        walk = place(Listing("for (i = 0; i < 5; i++)", CODE_BIG), x=BOARD_X, y=-1.0)
        w_init, w_cond, w_step = walk.paint_for(0, "i = 0", "i < 5", "i++")
        under = boxes[0].get_bottom()
        counter = VGroup(arrow(under + DOWN * 0.6, under + DOWN * 0.08, FLASH, 4, 0.18),
                         code("i", LABEL, FLASH).move_to(under + DOWN * 0.85))
        nxt = VGroup(text("NEXT", LABEL, MUTED, BOLD), text("The foreach Loop", TITLE, BLUE, BOLD),
                     Line(LEFT * 1.8, RIGHT * 1.8, color=BROWN, stroke_width=4)).arrange(DOWN, buff=0.3)
        nxt.move_to([BOARD_X, -0.55, 0])
        self.fit(boxes, marks_l, walk, counter, nxt)
        self.apart(counter, walk)
        self.apart(boxes, nxt)

        def hop_along():
            for _ in MARKS[1:]:
                self.play(counter.animate(path_arc=PI / 2).shift(RIGHT * 0.95), run_time=0.4)

        def five_boxes():
            self.wipe()
            self.play(LaggedStart(*[FadeIn(VGroup(b, m), shift=UP * 0.15) for b, m in zip(boxes, marks)], lag_ratio=0.2),
                      FadeIn(marks_l), run_time=1.4)

        self.play(FadeIn(fl), FadeIn(habits), run_time=0.8)
        self.T("s11_01", "Close your notebooks. One sentence each. What do you take home?", look="smile")
        self.M("s11_02", "Initialization runs once. Then it is check, body, update, again and again, and the check "
                         "comes first, so the body can run zero times.",
               ("once", lambda: Indicate(fl.nodes[0][0], color=FLASH, scale_factor=1.08)),
               ("check", lambda: Indicate(fl.nodes[1][0], color=FLASH, scale_factor=1.08), 0.4),
               ("body", lambda: Indicate(fl.nodes[2][0], color=FLASH, scale_factor=1.08), 0.4),
               ("update", lambda: Indicate(fl.nodes[3][0], color=FLASH, scale_factor=1.08), 0.4),
               ("zero", lambda: [hl(fl.no), hl(fl.end)]), look="smile")
        self.A("s11_03", "The loop ends on the first value that fails, and the variable keeps that value. Fifteen and "
                         "six, not fifteen and five.",
               ("first", lambda: hl(habits[2], 1.06)),
               ("Fifteen", lambda: self.pinned("q1_done")), look="smile")
        self.K("s11_04", "The loop owns one statement. A semicolon alone is a statement. So find the body before "
                         "anything else.",
               ("one", lambda: self.pinned("body")),
               ("find", lambda: hl(habits[0], 1.06)), look="smile")
        self.T("s11_05", "That is the whole lesson. And none of you needed me to say it.",
               look="happy", others={"A": "happy", "M": "happy", "K": "happy"})
        self.T("s11_06", "One last thing before you go. Five marks. To visit each one, we set up a counter, we choose "
                         "where it starts, we choose where it stops, and we step it forward.",
               ("Five", five_boxes),
               ("counter", lambda: [FadeIn(walk, shift=UP * 0.15), FadeIn(counter, shift=UP * 0.15)]),
               ("starts", lambda: hl(w_init, 1.3)),
               ("stops", lambda: hl(w_cond, 1.3)),
               ("step", lambda: hl(w_step, 1.3)),
               (None, hop_along), pose="point")
        self.T("s11_07", "Now think about every mistake we met today. Where it starts. Where it stops. What it holds "
                         "at the end. Every one of them came from the counter.",
               ("starts", lambda: Indicate(w_init, color=BAD, scale_factor=1.3)),
               ("stops", lambda: Indicate(w_cond, color=BAD, scale_factor=1.3)),
               ("holds", lambda: counter.animate.shift(RIGHT * 0.95).set_color(BAD)),
               ("counter", lambda: Indicate(counter, color=BAD, scale_factor=1.2)))
        self.T("s11_08", "So what if a loop needed no counter at all? What if you could simply say, for each mark in "
                         "this list, do this?",
               ("no", lambda: FadeOut(VGroup(counter, walk))),
               ("each", lambda: LaggedStart(*[Indicate(b, color=FLASH, scale_factor=1.1) for b in boxes],
                                            lag_ratio=0.3, run_time=1.8)), look="ask")
        self.K("s11_09", "Is that possible?", look="think")
        self.T("s11_10", "Next class.", look="smile")
        self.N("s11_11", "A loop with nothing to count, and nothing to get wrong by one. Next time: the foreach loop.",
               ("Next", lambda: [FadeIn(nxt[0]), FadeIn(nxt[1], scale=1.1), Create(nxt[2])]))

        # fade out: the class, the panel and the board leave together
        self.wait(1.0)
        self.voice = None
        if self.mobjects:
            self.play(FadeOut(Group(*self.mobjects)), run_time=1.0)
        self.scene_end("S11_habits")

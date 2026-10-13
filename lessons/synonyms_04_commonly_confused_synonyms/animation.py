"""
animation.py for the LMS video generator.

Course : C-CAT Preparation - Section A: English Language and Verbal Ability
Module : 1 Vocabulary   Lesson : 1 Synonyms (Session 2)
Video  : 04 - Commonly Confused Synonyms   (previous: Context-based synonyms;  next: Exam-oriented synonyms)
Source : C:/Final scripts/Scipts/04 - Commonly confused synonyms.pdf

Note: the two questions are practice questions written for the class, not past-paper questions.

Look (3Blue1Brown style):
  - near-black background, white text, ONE blue and ONE brown accent;
    yellow only for a passing highlight, green / red only for right / wrong (and for up / down on the timelines)
  - text in Latin Modern Roman (from the MiKTeX folder on this machine; Cambria if it is missing)
  - sizes: title 54, heading 38, body 32, label 28, small 24

Roles (the script has no speaker labels; every line was assigned by meaning, and no label is spoken):
  NARRATOR   voice-over, connects the scenes          self.N              voice "vijay"
  TEACHER    teaches, asks, guides                    self.T / self.Q     voice "aditya"
  STUDENT A  the confident one, near the window       self.S("A", ...)    voice "prasad"
  STUDENT B  the cautious one, front row              self.S("B", ...)    voice "kavya"
  STUDENT C  the second student                       self.S("C", ...)    voice "ritu"
  STUDENT D  at the back                              self.S("D", ...)    voice "student_a"
  Stage directions are not spoken: they are the visuals. The drill sentences and the method box are
  shown, not read out (the script gives them no spoken line); a thinking bar gives time to read them.

Sarvam AI voices: the ids above are voice-library ids. With the Sarvam engine each id is turned into a
  Sarvam speaker by settings.json > audio.sarvam.voices. Six different voices need this map:
    "vijay": "vijay", "aditya": "aditya", "prasad": "kabir", "kavya": "kavya", "ritu": "ritu", "student_a": "rahul"

Screen zones:
  top band   teacher (left corner), scene heading, the four students (right corner)
  strip      the question being asked or the student's line
  board      everything else (BOARD_TOP down to FLOOR)

Section map:
  S01 Continuous or continual?   S02 How C-CAT tests it   S03 Attempts   S04 WHAT: the precise difference
  S05 HOW: a rapid drill   S06 HOW: a method for new pairs   S07 WHY: the cost of a near miss   S08 Payoff
  S09 Summary   S10 What comes next
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
BLUE = "#58C4DD"           # accent 1: key terms, the word in question
BROWN = "#CD853F"          # accent 2: clues, things to remember
FLASH = "#FFFF00"          # a passing highlight only
GOOD = "#83C167"           # the right answer
BAD = "#FC6255"            # wrong / dangerous

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
STUDENT_R = 0.28                              # the four students are drawn a little smaller
STUDENT_GAP = 0.1
STUDENTS_W = 4 * 2.6 * STUDENT_R + 3 * STUDENT_GAP
HEAD_Y = 3.02                                 # centre of the scene heading
HEAD_W = FRAME_W - 2 * (SAFE + STUDENTS_W + 0.35)     # the heading stays centred between the cast
TIMER_Y = 2.58                                # the thinking-time bar
STRIP_TOP, STRIP_BOTTOM = 2.42, 1.48          # the spoken-line strip
STRIP_Y = (STRIP_TOP + STRIP_BOTTOM) / 2
STRIP_W = 11.0
BOARD_TOP = 1.32                              # top of the board (the strip sits above it)

NARRATOR_VOICE = "vijay"
TEACHER_VOICE = "aditya"
VOICES = {"N": NARRATOR_VOICE, "T": TEACHER_VOICE, "A": "prasad", "B": "kavya", "C": "ritu", "D": "student_a"}
TURN_PAUSE = 0.6               # silence after each block, so the voices never run together
CRUMB = "C-CAT Preparation  ›  English  ›  Vocabulary  ›  Synonyms"


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
    for lines in range(1, max_lines + 1):
        mob = text(s if lines == 1 else wrap_lines(s, lines), size, color, weight, slant)
        if mob.width <= max_width:
            return mob
    return mob.scale(max_width / mob.width)


def phrase(*parts, buff=0.22):
    """Pieces on one line."""
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


def line_at(s, left=0.0, y=0.0, size=LABEL, color=INK, weight=NORMAL, slant=NORMAL, font=FONT):
    """A piece of text whose LINE (not its ink) is centred on ``y``, so pieces set this way share a baseline.

    ``line_end`` is where the next piece of the same line starts."""
    mob = text(s + "|", size, color, weight, slant, font)        # the bar gives every piece the same height
    mob.shift(RIGHT * (left - mob.get_left()[0]) + UP * (y - mob.get_y()))
    bar = mob[-1]
    mob.line_end = bar.get_left()[0]
    mob.remove(bar)
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
    """Highlight a text or an arrow for a moment."""
    return Indicate(mob, color=color, scale_factor=scale)


def ring(mob):
    """Highlight a block for a moment (a frame that draws itself and fades)."""
    return Circumscribe(mob, color=FLASH, buff=0.1, fade_out=True, stroke_width=5)


def under(mob, color=BLUE, gap=0.07):
    """A line under ``mob`` (a student's pick, a key word)."""
    return Line(mob.get_corner(DL) + DOWN * gap, mob.get_corner(DR) + DOWN * gap, color=color, stroke_width=4)


def tick(size=0.3, color=GOOD):
    t = VMobject(stroke_color=color, stroke_width=6)
    t.set_points_as_corners([np.array([-0.5, 0.0, 0.0]), np.array([-0.12, -0.4, 0.0]), np.array([0.5, 0.45, 0.0])])
    return t.scale(size)


def cross(size=0.26, color=BAD):
    return VGroup(Line(UL, DR, color=color, stroke_width=6), Line(UR, DL, color=color, stroke_width=6)).scale(size / 2)


def small_arrow(color=BROWN, length=0.8):
    return Arrow(LEFT * length / 2, RIGHT * length / 2, buff=0, color=color, stroke_width=4, tip_length=0.18)


def bullets(items, size=LABEL, buff=0.3, color=INK):
    """Rows of a blue dot and one line each."""
    rows = VGroup()
    for item in items:
        body = text(item, size, color) if isinstance(item, str) else item
        rows.add(VGroup(Dot(radius=0.07, color=BLUE), body).arrange(RIGHT, buff=0.3))
    return rows.arrange(DOWN, buff=buff, aligned_edge=LEFT)


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
    """Answer options (a) to (d): in a row (``across``) or one under another. ``items`` are (letter, word)."""

    def __init__(self, items, size=LABEL, across=False, gap=0.7):
        super().__init__()
        self.rows, self.across = {}, across
        x, step = 0.0, size * 0.0195
        for k, (letter, word) in enumerate(items):
            y = 0.0 if across else -k * step
            tag = line_at(f"({letter})", x if across else 0.0, y, size, BLUE, BOLD)
            body = line_at(word, tag.line_end + size * 0.004, y, size, INK)
            row = VGroup(tag, body)
            self.rows[letter] = row
            self.add(row)
            x = row.get_right()[0] + gap

    def right(self, letter):
        """The answer turns green and gets a tick."""
        row = self.rows[letter]
        return [row.animate.set_color(GOOD), FadeIn(tick(0.26).next_to(row, RIGHT, buff=0.16), scale=0.6)]

    def out(self, *letters):
        """These options go grey."""
        return [self.rows[letter].animate.set_color(MUTED) for letter in letters]

    def note(self, letter, s, color=MUTED, size=SMALL):
        """A short reason beside an option (below it when the options are in a row)."""
        row = self.rows[letter]
        if self.across:
            return text(s, size, color).next_to(row, DOWN, buff=0.16)
        x = max(r.get_right()[0] for r in self.rows.values()) + 0.9
        return fit_w(place(text(s, size, color), left=x, y=row.get_y()), EDGE_X - x)


class Question(VGroup):
    """A practice question: its label, the sentence (lines of pieces, see ``para``) and the options."""

    def __init__(self, label, lines, options, size=LABEL, across=True):
        super().__init__()
        self.label = text(label, SMALL, MUTED, BOLD)
        self.body = para(*lines, size=size)
        self.opts = Options(options, size, across)
        self.add(self.label, self.body, self.opts)
        self.arrange(DOWN, buff=size * 0.0085, aligned_edge=LEFT)


def fan(word, leaves, word_y=0.72, leaf_y=-0.9, spread=4.5, size=LABEL):
    """One word with an arrow to each of its sentences. The group has ``.word``, ``.arrows`` and ``.leaves``."""
    top = text(word, TITLE, BLUE, BOLD).move_to(UP * word_y)
    n = len(leaves)
    items = VGroup(*[text(s, size).move_to(RIGHT * spread * (k - (n - 1) / 2) + UP * leaf_y)
                     for k, s in enumerate(leaves)])
    arrows = VGroup(*[Arrow(top.get_bottom() + DOWN * 0.12, m.get_top() + UP * 0.12, buff=0, color=BROWN,
                            stroke_width=4, tip_length=0.2) for m in items])
    group = VGroup(top, arrows, items)
    group.word, group.arrows, group.leaves = top, arrows, items
    return group


# ============================================================ the cast ====

SKIN = "#F2D0B0"               # characters use neutral tones plus their shirt colour
HAIR = "#4E3B2A"
LIPS = "#3A1F1F"
SHIRT_T = "#8C6239"            # the teacher wears brown
RING_ON = INK
RING_OFF = "#3A3A3A"
SHIRTS = ("#1C758A", "#2B5F8A", "#3A8A7A", "#4A6FA5")     # students A, B, C, D wear shades of blue


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
        elif hair == "bun":
            extras.add(Circle(radius=r * 0.3, stroke_width=0, fill_color=HAIR, fill_opacity=1).move_to(self.at(0, 1.05)))
        elif hair == "curly":
            for dx in (-0.55, 0.0, 0.55):
                extras.add(Circle(radius=r * 0.24, stroke_width=0, fill_color=HAIR,
                                  fill_opacity=1).move_to(self.at(dx, 0.92 - 0.2 * abs(dx))))
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

# ============================================================= lesson ====

Q1_LINES = [['"The server suffered ________ outages last week:'],
            ["it went down", ("every few hours.\"", INK)]]
Q1_OPTIONS = [("a", "continuous"), ("b", "continual"), ("c", "contiguous"), ("d", "continuum")]
Q2_LINES = [['"Moving the analytics workload to spot instances proved far more'],
            ["________,", ("cutting the monthly cloud bill", INK), 'by 40 percent."']]
Q2_OPTIONS = [("a", "economic"), ("b", "economical"), ("c", "economics"), ("d", "economy")]

PAIRS = [["continuous", "without any break", "a continuous power supply"],
         ["continual", "repeated, with breaks", "continual crashes"],
         ["economic", "related to the economy", "economic policy"],
         ["economical", "saving money, efficient", "an economical cloud plan"]]

# the rapid drill: sentence, the choices, which choices are right
DRILL = [("1.  The audit team pulled six months of ________ logs.", ("historic", "historical"), (1,)),
         ("2.  The database is backed up on ________ days.", ("alternate", "alternative"), (0,)),
         ("3.  Code review helps ________ that bugs are caught early.", ("ensure", "assure", "insure"), (0,)),
         ("4.  The new build has ________ bugs and uses ________ memory.", ("fewer", "less"), (0, 1)),
         ("5.  The test suite ________ forty unit tests.", ("comprises", "comprises of"), (0,))]
LEARNED = [["historic / historical", "important in history  /  related to the past"],
           ["alternate / alternative", "every other one  /  another option"],
           ["ensure / assure / insure", "make certain  /  remove doubt  /  protect with money"],
           ["fewer / less", "countable  /  uncountable"],
           ["comprise / compose", "whole comprises parts  /  parts compose whole"]]

CLOUD = ["candid", "abate", "lucid", "terse", "novel", "frugal", "ardent", "placid", "rigid", "astute", "benign",
         "brisk", "futile", "hasty", "vivid", "wary", "zeal", "tacit", "ample", "blunt", "coarse", "docile", "eager",
         "feeble"]
GLOW = (2, 5, 9, 14, 18, 22)                # the handful of cloud words that light up

assert all(len(row) == 3 for row in PAIRS) and len(DRILL) == len(LEARNED) == 5 and len(CLOUD) == 24


def timelines(top, left=-3.1, right=6.3, gap=0.85):
    """Last week twice: down all the time (one solid bar), and down, up, down, up (short blocks).

    The group has ``.solid`` and ``.broken`` (each: label + bar) and ``.days``."""
    y1, y2 = top - 0.2, top - 0.2 - gap
    width = right - left
    solid = VGroup(text("Down all the time", SMALL, MUTED).move_to([left - 1.75, y1, 0]),
                   Rectangle(width=width, height=0.3, stroke_width=0, fill_color=BAD, fill_opacity=1).move_to(
                       [(left + right) / 2, y1, 0]))
    cycle = width / 8
    blocks = VGroup(*[Rectangle(width=0.3, height=0.3, stroke_width=0, fill_color=BAD, fill_opacity=1).move_to(
        [left + 0.15 + k * cycle, y2, 0]) for k in range(8)])
    broken = VGroup(text("Down, up, down, up", SMALL, MUTED).move_to([left - 1.75, y2, 0]),
                    Line([left, y2, 0], [right, y2, 0], color=GOOD, stroke_width=5), blocks)
    days = VGroup(*[text(d, MIN_FONT, MUTED).move_to([left + (k + 0.5) * width / 7, y2 - 0.45, 0])
                    for k, d in enumerate(("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"))])
    group = VGroup(solid, broken, days)
    group.solid, group.broken, group.days = solid, broken, days
    return group


class CommonlyConfusedSynonyms(LMSScene):
    lesson_title = "Commonly Confused Synonyms"

    def construct(self):
        self.camera.background_color = BG
        self.cast = None
        self.title_bar = None
        self.spoken = None
        self.talking = None
        self.faces = {}

        self.hook()
        self.exam()
        self.attempts()
        self.what()
        self.drill()
        self.method()
        self.why()
        self.payoff()
        self.summary()
        self.next_session()

    # ------------------------------------------------------ stage helpers --

    def kept(self):
        """Family of what stays through a scene change: the characters and the heading."""
        keep = set()
        for mob in (self.cast, self.title_bar):
            if mob is not None:
                keep.update(mob.get_family())
        return keep

    def wipe(self, run_time=0.6):
        """Clear the board and the spoken line."""
        keep = self.kept()
        parts = [p for m in self.mobjects for p in m.family_members_with_points() if p not in keep]
        if parts:
            self.play(FadeOut(Group(*parts)), run_time=run_time)
        for mob in list(self.mobjects):
            if mob not in keep and not any(p in keep for p in mob.get_family()):
                self.remove(mob)
        self.spoken = None

    def heading(self, s):
        """The scene heading: a title with a blue rule, between the teacher and the students."""
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
        rule = Line(LEFT * 1.3, RIGHT * 1.3, color=BLUE, stroke_width=4)
        before = text(f"Previous topic:  {previous}", LABEL, BROWN)
        card = VGroup(crumb, name, rule, before).arrange(DOWN, buff=0.4).move_to(DOWN * 0.6)
        self.fit(card)
        self.play(FadeIn(crumb), FadeIn(name, shift=UP * 0.2), Create(rule), run_time=1.0)
        self.play(FadeIn(before, shift=UP * 0.15), run_time=0.6)
        self.enter_cast()
        return card

    def enter_cast(self):
        """The teacher (top left) and the four students (top right) come in and stay for the whole video."""
        t = Face(FACE_R, SHIRT_T, "short", glasses=True)
        a = Face(STUDENT_R, SHIRTS[0], "short")                    # A: confident, near the window
        b = Face(STUDENT_R, SHIRTS[1], "pony", glasses=True)       # B: cautious, front row
        c = Face(STUDENT_R, SHIRTS[2], "bun")                      # C: the second student
        d = Face(STUDENT_R, SHIRTS[3], "curly")                    # D: at the back
        t.shift(UP * (TOP - t.get_top()[1]) + RIGHT * (-EDGE_X - t.get_left()[0]))
        students = VGroup(a, b, c, d).arrange(RIGHT, buff=STUDENT_GAP, aligned_edge=DOWN)
        students.shift(UP * (TOP - students.get_top()[1]) + RIGHT * (EDGE_X - students.get_right()[0]))
        self.faces = {"T": t, "A": a, "B": b, "C": c, "D": d}
        self.cast = VGroup(t, a, b, c, d)
        self.play(FadeIn(t, shift=RIGHT * 0.4), FadeIn(students, shift=LEFT * 0.4), run_time=0.6)

    def react(self, who, look):
        """Animations that change the expression of one character, or of several ("ABCD")."""
        return [anim for name in who for anim in self.faces[name].look_to(look)]

    def speaker(self, who, look=None, other=None):
        """Show who speaks: "N" narrator (everyone listens), "T" teacher, "A" to "D" a student.

        ``look`` is the speaker's expression. ``other`` is the listeners': the students
        while the teacher speaks, the teacher while a student speaks."""
        anims = []
        for name, face in self.faces.items():
            if name == who:
                want = look or "smile"
            elif who != "N" and "T" in (who, name):
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
        """The strip under the heading: a teacher question or a student line (None clears it).

        No speaker label: the lit ring shows who is speaking. Student lines are in italics."""
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
        """Thinking time: a bar under the heading runs out."""
        bar = Line(LEFT * 1.6, RIGHT * 1.6, color=FLASH, stroke_width=5).move_to(UP * TIMER_Y)
        self.play(FadeIn(bar), run_time=0.3)
        self.play(Uncreate(bar), run_time=max(0.5, seconds - 0.3), rate_func=linear)

    # ------------------------------------------------- narration drivers --

    def cue(self, n, word):
        """Wait for ``word`` (or ``(word, occurrence)``) in narration ``n``."""
        spoken, occ = (word, 1) if isinstance(word, str) else word
        try:
            self.at_word(n, spoken, occ)
        except ValueError:
            pass                          # the aligner may hear a word differently: carry on

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

    def T(self, nid, spoken, *cues, look="smile", other=None, think=0.0):
        """Teacher statement."""
        return self.say("T", nid, spoken, cues, look, other, None, think)

    def Q(self, nid, spoken, *cues, shown=None, look="ask", other="think", think=0.0):
        """Teacher question: spoken, and shown in the strip."""
        return self.say("T", nid, spoken, cues, look, other, shown or spoken, think)

    def S(self, who, nid, spoken, *cues, shown=None, look="smile", other=None):
        """A line of student "A", "B", "C" or "D": own voice, shown in the strip."""
        return self.say(who, nid, spoken, cues, look, other, shown or spoken)

    # ==================================== 1. CONTINUOUS OR CONTINUAL? ======

    def hook(self):
        self.scene_start("S01_hook", title="Continuous or Continual?")
        card = self.opening("Commonly Confused Synonyms", "Context-based synonyms")
        self.heading("Continuous or continual?")

        sent = para(['"The server suffered ________ outages last week:'], ["it went down", ("every few hours.\"", INK)])
        place(sent, x=0.0, top=BOARD_TOP - 0.15)
        clue = sent[1][1]
        pair = phrase(text("continuous", BODY, BLUE, BOLD), text("/", BODY, MUTED), text("continual", BODY, BROWN, BOLD),
                      buff=0.5).move_to(DOWN * 0.45)
        tl = timelines(-1.2)
        trap = text("Very close in meaning: in an exam, that is the trap", LABEL, BROWN, BOLD).move_to(DOWN * 3.15)
        self.fit(sent, pair, tl, trap)

        name = text("Commonly confused synonyms", BODY, BLUE, BOLD).move_to(UP * 0.4)
        casual = phrase(text("Casual speech:", LABEL, MUTED), text("used as if they were synonyms", LABEL), buff=0.3)
        formal = phrase(text("Formal English and exams:", LABEL, MUTED), text("a precise difference", LABEL, BROWN, BOLD),
                        buff=0.3)
        casual.move_to(DOWN * 0.8)
        formal.move_to(DOWN * 1.6)
        self.fit(name, casual, formal)

        self.N("s1_01", "Context was the hero of the last lesson. Today context is right there on the board, and the "
                        "class still can't agree.",
               ("hero", lambda: [FadeOut(card), FadeIn(sent, shift=UP * 0.2)]),
               ("board", lambda: FadeIn(pair, shift=UP * 0.15)),
               ("agree", lambda: [self.react("AC", "confused"), self.react("BD", "think")]))
        self.Q("s1_02", "So. Which one?", (None, lambda: [hl(pair[0]), hl(pair[2])]))
        self.S("A", "s1_03", "Continuous. They mean the same thing anyway.",
               ("Continuous", lambda: hl(pair[0])))
        self.S("B", "s1_04", "I think there's a difference. I just can't explain it.",
               ("difference", lambda: hl(pair[2])), look="think")
        self.S("D", "s1_05", "If it were continuous, the server would be down the whole week. But the sentence says "
                             "every few hours.",
               ("whole", lambda: FadeIn(tl.solid, shift=RIGHT * 0.3)),
               ("every", lambda: [clue.animate.set_color(BROWN), FadeIn(VGroup(tl.broken, tl.days), shift=RIGHT * 0.3)]),
               look="think")
        self.Q("s1_06", "Look at these two timelines. Which one is the sentence describing?",
               ("timelines", lambda: [hl(tl.solid[0], 1.06), hl(tl.broken[0], 1.06)]))
        self.T("s1_07", "So the words aren't interchangeable after all. They sit very close in meaning, but in an exam "
                        "that closeness is exactly the trap.",
               (None, lambda: [ring(tl.broken), self.react("ABCD", "happy")]),
               ("close", lambda: [hl(pair[0], 1.06), hl(pair[2], 1.06)]),
               ("trap", lambda: FadeIn(trap, shift=UP * 0.15)))
        self.T("s1_08", "These are pairs of words that people treat as synonyms, and even use as synonyms in casual "
                        "speech, but which have a precise difference that formal English and examiners respect.",
               ("pairs", self.wipe),
               ("treat", lambda: FadeIn(name, shift=UP * 0.15)),
               ("casual", lambda: FadeIn(casual, shift=UP * 0.15)),
               ("precise", lambda: FadeIn(formal, shift=UP * 0.15)))

        self.finish("S01_hook")

    # ======================================== 2. HOW C-CAT TESTS IT ========

    def exam(self):
        self.begin("S02_exam", "How C-CAT Tests It", "How C-CAT tests it")

        kinds = bullets(["Synonym questions", "Fill in the blank questions", "Error spotting questions (later)"],
                        BODY, 0.4)
        place(kinds, x=0.0, y=-0.6)
        self.fit(kinds)

        self.q1 = Question("Practice question 1", Q1_LINES, Q1_OPTIONS, SMALL)
        self.q2 = Question("Practice question 2", Q2_LINES, Q2_OPTIONS, SMALL)
        self.both = VGroup(self.q1, self.q2).arrange(DOWN, buff=0.5, aligned_edge=LEFT)
        place(self.both, x=0.0, top=BOARD_TOP - 0.1)
        self.fit(self.both)
        q1, q2 = self.q1, self.q2

        self.N("s2_01", "These pairs show up in synonym questions, in fill in the blank questions, and in error "
                        "spotting questions later in this course. Here are two practice questions written for this "
                        "class.",
               ("synonym", lambda: FadeIn(kinds[0], shift=RIGHT * 0.2)),
               ("fill", lambda: FadeIn(kinds[1], shift=RIGHT * 0.2)),
               ("error", lambda: FadeIn(kinds[2], shift=RIGHT * 0.2)),
               ("practice", lambda: [FadeOut(kinds), FadeIn(q1, shift=UP * 0.2)]),
               ("class", lambda: FadeIn(q2, shift=UP * 0.2)))
        self.T("s2_02", "Forty-five seconds.",
               (None, lambda: [hl(q1.label), hl(q2.label)]), look="ask", other="think", think=45.0)

        self.scene_end("S02_exam")          # the two questions stay on the board for the next scene

    # ================================================== 3. ATTEMPTS ========

    def attempts(self):
        self.begin("S03_attempts", "Attempts", "First attempts")

        q2 = self.q2
        pick = under(q2.opts.rows["a"], BLUE)
        test = para(['"India\'s', ("economic", BLUE, BOLD), 'growth slowed last quarter."'],
                    ['"India\'s', ("economical", BROWN, BOLD), 'growth slowed last quarter."'], step=0.95)
        place(test, x=0.0, y=-0.4)
        self.fit(test)
        ok = tick(0.28).next_to(test[0], RIGHT, buff=0.4)
        no = cross(0.28).next_to(test[1], RIGHT, buff=0.4)
        cheap = text("Sounds as if the growth was cheap", SMALL, BAD).next_to(test[1], DOWN, buff=0.3)

        self.Q("s3_01", "Question two first. Who has what?",
               ("two", lambda: hl(q2.label)), shown="Question 2 first. Who has what?")
        self.S("C", "s3_02", "Economic. It's about money, and economics is about money.",
               ("Economic", lambda: Create(pick)))
        self.S("B", "s3_03", "But the sentence is saying the workload became cheaper, not that it became related to "
                             "the economy.",
               ("cheaper", lambda: hl(q2.body[1][1], 1.06)),
               shown="But the sentence says the workload became cheaper, not 'related to the economy'.", look="think")
        self.S("A", "s3_04", "Is economic related to the economy?", look="confused")
        self.Q("s3_05", "Let's find out. Here's a pair of sentences. Does each one sound right to you?",
               ("find", lambda: FadeOut(VGroup(self.both, pick))),
               ("pair", lambda: LaggedStart(FadeIn(test[0], shift=UP * 0.15), FadeIn(test[1], shift=UP * 0.15),
                                            lag_ratio=0.5, run_time=1.6)),
               shown="Here is a pair of sentences. Does each one sound right to you?")
        self.S("D", "s3_06", "The first one. The second one sounds like the growth was cheap.",
               ("first", lambda: FadeIn(ok, scale=0.6)),
               ("cheap", lambda: [FadeIn(no, scale=0.6), FadeIn(cheap), self.react("ABC", "happy")]))
        self.T("s3_07", "That's exactly the distinction.",
               (None, lambda: [hl(test[0][1]), hl(test[1][1])]), look="happy")

        self.finish("S03_attempts")

    # ============================ 4. WHAT: THE PRECISE DIFFERENCE ==========

    def what(self):
        self.begin("S04_what", "WHAT: The Precise Difference", "The precise difference")

        g = Grid(PAIRS, (2.6, 4.4, 5.0), row_h=0.6, header=False,
                 styles=[(BLUE, BOLD), (INK, NORMAL), (MUTED, NORMAL)])
        place(g, x=0.0, top=BOARD_TOP - 0.2)
        roots = para([("continu", BLUE, BOLD), ("-ous", BROWN, BOLD), ("/", MUTED), ("continu", BLUE, BOLD),
                      ("-al", BROWN, BOLD)],
                     [("econom", BLUE, BOLD), ("-ic", BROWN, BOLD), ("/", MUTED), ("econom", BLUE, BOLD),
                      ("-ical", BROWN, BOLD)], step=0.58)
        place(roots, x=0.0, top=-1.5)
        rule = text("Same root, same family. The suffix shifts the job.", LABEL, BROWN, BOLD).move_to(DOWN * 3.0)
        self.fit(g, roots, rule)
        suffixes = VGroup(roots[0][1], roots[0][4], roots[1][1], roots[1][4])
        stems = VGroup(roots[0][0], roots[0][3], roots[1][0], roots[1][3])

        self.play(LaggedStart(*[FadeIn(g.row(r), shift=RIGHT * 0.2) for r in range(4)], lag_ratio=0.4), run_time=2.4)
        self.T("s4_01", "Here's the rule underneath both. Both words share a root, and they both belong to the same "
                        "family of meaning. But the suffix shifts the job.",
               ("root", lambda: [FadeIn(roots, shift=UP * 0.15)]),
               ("family", lambda: hl(stems, 1.06)),
               ("suffix", lambda: [hl(suffixes, 1.15), FadeIn(rule, shift=UP * 0.15)]))
        self.S("C", "s4_02", "So when two words share a root, I should check the suffix?",
               ("suffix", lambda: hl(suffixes, 1.15)), look="ask")
        self.T("s4_03", "Very often, yes. Let me show you more pairs. Tell me which word fits before I reveal it.",
               ("pairs", lambda: self.react("ABCD", "smile")))

        self.finish("S04_what")

    # ======================================= 5. HOW: A RAPID DRILL =========

    def drill(self):
        self.begin("S05_drill", "HOW: A Rapid Drill", "A rapid drill")

        items = []
        for sentence, choices, right in DRILL:
            parts = []
            for k, word in enumerate(choices):
                parts += ([("/", MUTED)] if k else []) + [(word, INK)]
            item = VGroup(text(sentence, LABEL), para(parts, size=LABEL, color=INK))
            item.arrange(DOWN, buff=0.3, aligned_edge=LEFT)
            place(item, left=-EDGE_X + 0.3, top=BOARD_TOP - 0.15)
            self.fit(item)
            item.words = [item[1][0][2 * k] for k in range(len(choices))]
            item.correct = right
            items.append(item)
        table = Grid(LEARNED, (4.3, 8.9), size=SMALL, row_h=0.5, header=False, styles=[(BLUE, BOLD), (INK, NORMAL)])
        place(table, x=0.0, top=-0.75)
        self.fit(table)
        strike = Line(items[4].words[1].get_left() + LEFT * 0.05, items[4].words[1].get_right() + RIGHT * 0.05,
                      color=BAD, stroke_width=4)
        hint = text("comprise = consist of", SMALL, BROWN, BOLD).next_to(items[4][1], RIGHT, buff=0.9)

        def show(k):
            """The next drill sentence, then a moment to choose."""
            anims = [FadeIn(items[k], shift=UP * 0.15)]
            if k:
                anims.append(FadeOut(items[k - 1]))
            self.play(*anims, run_time=0.6)
            self.countdown(3.5)

        def pick(k):
            item = items[k]
            return [w.animate.set_color(GOOD if j in item.correct else MUTED) for j, w in enumerate(item.words)]

        def learned(r):
            return FadeIn(table.row(r), shift=RIGHT * 0.2)

        show(0)
        self.S("A", "s5_01", "Historical. Logs from the past.", ("Historical", lambda: pick(0)))
        self.Q("s5_02", "And historic?")
        self.S("B", "s5_03", "Something important in history. Like a historic launch.",
               ("important", lambda: learned(0)), look="think")

        show(1)
        self.S("C", "s5_04", "Alternate. Every other day.", ("Alternate", lambda: pick(1)), look="think")
        self.Q("s5_05", "Then what's an alternative?", shown="Then what is an 'alternative'?")
        self.S("C", "s5_06", "Another option. An alternative database.", ("option", lambda: learned(1)))

        show(2)
        self.S("D", "s5_07", "Ensure. Make sure something happens.", ("Ensure", lambda: pick(2)))
        self.Q("s5_08", "And the other two?")
        self.S("B", "s5_09", "Assure is when you tell a person something, so their doubt goes away. Insure is money. "
                             "Insurance.",
               ("doubt", lambda: hl(items[2].words[1])),
               ("money", lambda: [hl(items[2].words[2]), learned(2)]), look="think")

        show(3)
        self.S("A", "s5_10", "Fewer bugs, less memory. Bugs can be counted, memory can't. Well, not as items.",
               ("Fewer", lambda: pick(3)),
               ("counted", lambda: learned(3)))

        show(4)
        self.S("C", "s5_11", "Comprises of?", (None, lambda: hl(items[4].words[1])), look="ask")
        self.T("s5_12", "Read it with the meaning in mind. Comprise already means consists of.",
               ("consists", lambda: FadeIn(hint, shift=LEFT * 0.2)))
        self.S("C", "s5_13", "So comprises of is like saying consists of of.",
               ("like", lambda: [Create(strike), *pick(4), learned(4), self.react("ABD", "happy")]),
               look="happy", other="happy")

        self.finish("S05_drill")

    # ============================ 6. HOW: A METHOD FOR NEW PAIRS ===========

    def method(self):
        self.begin("S06_method", "HOW: A Method for Pairs You Haven't Seen", "A method for new pairs")

        title = text("Confused-pair check", LABEL, BLUE, BOLD)
        steps = [para(["1.  Spot the shared root:", ("continu-,  econom-,  histor-", BLUE, BOLD)]),
                 para(["2.  Ask what the suffix adds:", ("-ous / -al,   -ic / -ical", BROWN, BOLD)]),
                 para(["3.  Build a test sentence where only one of them can work"]),
                 para(["4.  Read the target sentence for the deciding clue:"]),
                 para([('"every few hours",   "cutting the bill",   "six months ago"', BROWN)])]
        box = VGroup(title, *steps).arrange(DOWN, buff=0.32, aligned_edge=LEFT)
        steps[4].shift(RIGHT * 0.6)
        place(box, x=0.0, top=BOARD_TOP - 0.2)
        tip = text("The examiner plants a clue. Your job is to find it.", LABEL, BROWN, BOLD).move_to(DOWN * 3.05)
        self.fit(box, tip)

        self.T("s6_01", "You won't remember every pair. So here's how to reason through one you haven't studied.",
               ("reason", lambda: LaggedStart(FadeIn(title), *[FadeIn(s, shift=RIGHT * 0.2) for s in steps],
                                              lag_ratio=0.45, run_time=3.5)))
        self.countdown(6.0)                 # time to read the four steps: the script does not read them out
        self.S("B", "s6_02", "So the deciding clue is always somewhere in the sentence.",
               ("clue", lambda: [hl(steps[3], 1.04), hl(steps[4], 1.04)]), look="think")
        self.T("s6_03", "Almost always. The examiner has to make the question answerable, so they plant a clue. Your "
                        "job is to find it.",
               ("plant", lambda: FadeIn(tip, shift=UP * 0.15)), look="happy")

        self.finish("S06_method")

    # ============================== 7. WHY: THE COST OF A NEAR MISS ========

    def why(self):
        self.begin("S07_why", "WHY: The Cost of a Near Miss", "A costly near miss")

        head = text("Service-level agreement", SMALL, MUTED, BOLD)
        sla = para(['"The provider guarantees', ("continuous", BLUE, BOLD), 'availability."'])
        fact = text("Then the service goes down for 1 minute every day", LABEL, MUTED)
        v1 = phrase(text("continuous", LABEL, BLUE, BOLD), text("= no breaks at all:", LABEL),
                    text("agreement broken", LABEL, BAD, BOLD), buff=0.25)
        sla2 = para(['"The provider guarantees', ("continual", BROWN, BOLD), 'availability."'])
        v2 = phrase(text("continual", LABEL, BROWN, BOLD), text("= it keeps coming back:", LABEL),
                    text("a terrible guarantee", LABEL, BAD, BOLD), buff=0.25)
        board = VGroup(head, sla, fact, v1, sla2, v2).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        sla2.shift(DOWN * 0.25)
        v2.shift(DOWN * 0.25)
        place(board, x=0.0, top=BOARD_TOP - 0.15)
        moral = text("A near miss can change what you have promised", LABEL, BROWN, BOLD).move_to(DOWN * 3.1)
        self.fit(board, moral)

        self.Q("s7_01", "Imagine signing an agreement that promises continuous availability. Then the service goes "
                        "down for one minute every day. Did the vendor break the agreement?",
               (None, lambda: [FadeIn(head), FadeIn(sla, shift=UP * 0.15)]),
               ("continuous", lambda: hl(sla[0][1])),
               ("minute", lambda: FadeIn(fact, shift=UP * 0.15)),
               shown="Did the vendor break the agreement?")
        self.S("D", "s7_02", "Yes. Continuous means no breaks at all.",
               ("breaks", lambda: FadeIn(v1, shift=UP * 0.15)))
        self.Q("s7_03", "And if the agreement had said continual?",
               ("continual", lambda: FadeIn(sla2, shift=UP * 0.15)))
        self.S("A", "s7_04", "Then it only promised that it keeps coming back. That's a terrible guarantee.",
               ("keeps", lambda: FadeIn(v2, shift=UP * 0.15)),
               ("terrible", lambda: self.react("BCD", "happy")), look="think", other="happy")
        self.T("s7_05", "That's why precise writing matters. In contracts, documentation and your own emails, a near "
                        "miss can change what you've actually promised.",
               ("near", lambda: FadeIn(moral, shift=UP * 0.15)))

        self.finish("S07_why")

    # ============================ 8. PAYOFF: SOLVING BOTH QUESTIONS ========

    def payoff(self):
        self.begin("S08_payoff", "Payoff: Solving Both Questions", "Solving both questions")

        q1 = Question("Practice question 1", Q1_LINES, Q1_OPTIONS, LABEL, across=False)
        place(q1, left=-EDGE_X + 0.3, top=BOARD_TOP - 0.1)
        self.fit(q1)
        n1 = {k: q1.opts.note(k, s, c) for k, s, c in (("a", "no gap at all", BAD),
                                                         ("b", "repeated, with breaks", GOOD),
                                                         ("c", "adjacent, as in contiguous memory", BAD),
                                                         ("d", "a noun: wrong part of speech", BAD))}
        y = -3.05
        blocks = VGroup(*[Rectangle(width=0.3, height=0.26, stroke_width=0, fill_color=BAD, fill_opacity=1).move_to(
            [-2.75 + k * 1.1, y, 0]) for k in range(8)])
        broken = VGroup(text("Down, up, down, up", SMALL, MUTED).move_to([-4.8, y, 0]),
                        Line([-2.9, y, 0], [5.9, y, 0], color=GOOD, stroke_width=5), blocks)
        self.fit(broken)

        q2 = Question("Practice question 2", Q2_LINES, Q2_OPTIONS, LABEL, across=False)
        place(q2, left=-EDGE_X + 0.3, top=BOARD_TOP - 0.1)
        self.fit(q2)
        n2 = {k: q2.opts.note(k, s, c) for k, s, c in (("a", "related to the economy", BAD),
                                                         ("b", "saving money", GOOD),
                                                         ("c", "a noun", BAD), ("d", "a noun", BAD))}
        need = text("After 'more', the blank needs an adjective", SMALL, BROWN, BOLD)
        place(need, left=q2.get_left()[0], y=-3.1)
        self.fit(need)

        self.T("s8_01", "Question one.", (None, lambda: FadeIn(q1, shift=UP * 0.2)), look="ask")
        self.S("B", "s8_02", "The clue is every few hours, so there are breaks. That's continual, option B. "
                             "Continuous would mean no gap at all. Contiguous means touching or adjacent, like "
                             "contiguous memory blocks. Continuum is a noun, so it doesn't even fit the slot.",
               ("clue", lambda: q1.body[1][1].animate.set_color(BROWN)),
               ("breaks", lambda: FadeIn(broken, shift=UP * 0.15)),
               ("continual", lambda: [*q1.opts.right("b"), FadeIn(n1["b"], shift=RIGHT * 0.2)]),
               ("Continuous", lambda: [*q1.opts.out("a"), FadeIn(n1["a"], shift=RIGHT * 0.2)]),
               ("Contiguous", lambda: [*q1.opts.out("c"), FadeIn(n1["c"], shift=RIGHT * 0.2)]),
               ("Continuum", lambda: [*q1.opts.out("d"), FadeIn(n1["d"], shift=RIGHT * 0.2)]),
               shown="The clue is 'every few hours': there are breaks. So (b) continual.",
               look="think", other="happy")

        self.wipe()
        self.T("s8_03", "Nice use of contiguous memory. Question two.",
               ("two", lambda: FadeIn(q2, shift=UP * 0.2)), look="happy")
        self.S("C", "s8_04", "The clue is cutting the monthly cloud bill. That's about saving money, so option B, "
                             "economical. Economic means related to the economy. Economics and economy are nouns, "
                             "and the blank needs an adjective after more.",
               ("clue", lambda: q2.body[1][1].animate.set_color(BROWN)),
               ("option", lambda: [*q2.opts.right("b"), FadeIn(n2["b"], shift=RIGHT * 0.2)]),
               ("Economic", lambda: [*q2.opts.out("a"), FadeIn(n2["a"], shift=RIGHT * 0.2)]),
               ("nouns", lambda: [*q2.opts.out("c", "d"), FadeIn(VGroup(n2["c"], n2["d"]), shift=RIGHT * 0.2)]),
               ("adjective", lambda: FadeIn(need, shift=UP * 0.15)),
               shown="The clue is 'cutting the monthly cloud bill': saving money. So (b) economical.",
               other="happy")

        self.finish("S08_payoff")

    # ================================================== 9. SUMMARY =========

    def summary(self):
        self.begin("S09_summary", "Summary", "Summary")

        top = text("Some synonyms are only near synonyms", BODY, INK, BOLD)
        checks = bullets(["Check the root", "Check the suffix", "Find the clue in the sentence"], BODY, 0.35)
        step = column(text("Synonym method, step 7", SMALL, BROWN, BOLD),
                      text("Look-alike pair? Find the deciding clue in the sentence.", LABEL), buff=0.2)
        board = column(top, checks, step, buff=0.55)
        place(board, x=0.0, top=BOARD_TOP - 0.2)
        self.fit(board)

        self.Q("s9_01", "What's the takeaway?", shown="What is the takeaway?")
        self.S("D", "s9_02", "Some synonyms are only near synonyms. Check the root, the suffix, and the clue in the "
                             "sentence.",
               ("near", lambda: FadeIn(top, shift=UP * 0.15)),
               ("root", lambda: FadeIn(checks[0], shift=RIGHT * 0.2)),
               ("suffix", lambda: FadeIn(checks[1], shift=RIGHT * 0.2)),
               ("clue", lambda: [FadeIn(checks[2], shift=RIGHT * 0.2), FadeIn(step, shift=UP * 0.15)]),
               other="happy")

        self.finish("S09_summary")

    # ========================================= 10. WHAT COMES NEXT =========

    def next_session(self):
        self.begin("S10_next", "What Comes Next", "What comes next?")

        done = VGroup(*[VGroup(tick(0.26), text(s, BODY)).arrange(RIGHT, buff=0.3)
                        for s in ("Context", "Attributes", "Confused pairs")]).arrange(DOWN, buff=0.4,
                                                                                      aligned_edge=LEFT)
        place(done, x=0.0, y=-0.3)
        left_q = text("One problem is still left", BODY, BROWN, BOLD).move_to(DOWN * 2.3)

        hard = VGroup(*[text(s, BODY, INK, BOLD) for s in ("EPHEMERAL", "UBIQUITOUS", "OBDURATE")])
        hard.arrange(RIGHT, buff=0.9).move_to(DOWN * 0.85)
        self.fit(done, left_q, hard)
        xs = np.linspace(-5.4, 5.4, 6)
        cloud = VGroup(*[text(w, SMALL, MUTED).set_opacity(0.45).move_to([xs[k % 6], (0.95, 0.25, -1.95, -2.6)[k // 6], 0])
                         for k, w in enumerate(CLOUD)])
        nxt = text("Next session:  Exam-oriented synonyms", LABEL, BROWN, BOLD).move_to(DOWN * 3.2)

        self.N("s10_01", "The class can now handle context, attributes and confused pairs. But one problem is still "
                         "left.",
               ("context", lambda: FadeIn(done[0], shift=RIGHT * 0.2)),
               ("attributes", lambda: FadeIn(done[1], shift=RIGHT * 0.2)),
               ("confused", lambda: FadeIn(done[2], shift=RIGHT * 0.2)),
               ("problem", lambda: FadeIn(left_q, shift=UP * 0.15)))
        self.wipe()
        self.Q("s10_02", "How many of you could give me a synonym for any of these right now?",
               (None, lambda: LaggedStart(*[FadeIn(m, shift=UP * 0.15) for m in hard], lag_ratio=0.4, run_time=1.5)),
               ("right", lambda: [self.react("A", "ask"), self.react("BCD", "confused")]),
               (None, lambda: self.react("A", "oops")),
               shown="Could you give me a synonym for any of these right now?", other="confused")
        self.T("s10_03", "English has hundreds of thousands of words. You can't learn them all before the exam. So "
                         "which ones should you learn, and how do you remember them?",
               ("thousands", lambda: LaggedStart(*[FadeIn(m) for m in cloud], lag_ratio=0.08, run_time=2.5)),
               ("which", lambda: [cloud[k].animate.set_color(BLUE).set_opacity(1.0) for k in GLOW]),
               look="ask", other="think")
        self.T("s10_04", "Next session.", (None, lambda: FadeIn(nxt, shift=UP * 0.15)))

        self.the_end("S10_next")

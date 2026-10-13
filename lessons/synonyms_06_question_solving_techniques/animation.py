"""
animation.py for the LMS video generator.

Course : C-CAT Preparation - Section A: English Language and Verbal Ability
Module : 1 Vocabulary   Lesson : 1 Synonyms (Session 2)
Video  : 06 - Synonym Question-Solving Techniques   (previous: Exam-oriented synonyms;  next: Word substitution in
         a sentence with a synonym)
Source : C:/Final scripts/Scipts/06 - Synonym question-solving techniques.pdf

Note: the two questions are practice questions written for the class, not past-paper questions. The marking
scheme (+3 / -1) is the one the script uses; the teacher says to check the current official notification.

Look (3Blue1Brown style):
  - near-black background, white text, ONE blue and ONE brown accent;
    yellow only for a passing highlight, green / red only for right / wrong
  - text in Latin Modern Roman (from the MiKTeX folder on this machine; Cambria if it is missing)
  - sizes: title 54, heading 38, body 32, label 28, small 24

Roles (the script has no speaker labels; every line was assigned by meaning, and no label is spoken):
  NARRATOR   voice-over, connects the scenes          self.N              voice "vijay"
  TEACHER    teaches, asks, guides                    self.T / self.Q     voice "aditya"
  STUDENT A  the confident one, near the window       self.S("A", ...)    voice "prasad"
  STUDENT B  the cautious one, front row              self.S("B", ...)    voice "kavya"
  STUDENT C  the second student                       self.S("C", ...)    voice "ritu"
  STUDENT D  at the back, arms folded                 self.S("D", ...)    voice "student_a"
  Stage directions are not spoken: they are the visuals. The seven steps of the routine are shown, not
  read out (the script gives them no spoken line); a thinking bar gives time to read them.

Sarvam AI voices: the ids above are voice-library ids. With the Sarvam engine each id is turned into a
  Sarvam speaker by settings.json > audio.sarvam.voices. Six different voices need this map:
    "vijay": "vijay", "aditya": "aditya", "prasad": "kabir", "kavya": "kavya", "ritu": "ritu", "student_a": "rahul"

Screen zones:
  top band   teacher (left corner), scene heading, the four students (right corner)
  strip      the question being asked or the student's line
  board      everything else (BOARD_TOP down to FLOOR)

Section map:
  S01 Guess or skip?   S02 The topic   S03 How C-CAT tests it   S04 Attempts   S05 WHAT: the routine
  S06 HOW: context signal words   S07 HOW: roots, and when they mislead   S08 WHY: the routine beats memory
  S09 Payoff: running the routine   S10 Summary   S11 What comes next
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

RIGHT_MARKS, WRONG_MARKS = 3, -1


def expected(options_left):
    """Average marks from one guess among ``options_left`` options."""
    return (RIGHT_MARKS + (options_left - 1) * WRONG_MARKS) / options_left


assert expected(4) == 0 and abs(expected(3) - 1 / 3) < 1e-9 and expected(2) == 1        # the napkin, checked

GUESS = [["4 options:", "(1/4)(+3) + (3/4)(-1)", "= 0.75 - 0.75", "= 0"],
         ["3 options left:", "(1/3)(+3) + (2/3)(-1)", "= 1 - 0.67", "= +0.33"],
         ["2 options left:", "(1/2)(+3) + (1/2)(-1)", "= 1.5 - 0.5", "= +1.00"]]

Q1_LINES = [["Choose the word most nearly SIMILAR in meaning to:", ("OBDURATE", BLUE, BOLD)]]
Q1_OPTIONS = [("a", "Obedient"), ("b", "Obscure"), ("c", "Stubborn"), ("d", "Durable")]
Q2_LINES = [[('"Despite', INK), "the", ("PLAUDITS", BLUE, BOLD), "from industry analysts, the product"],
            ['failed to win customers in its first year."'],
            [("The word closest in meaning to PLAUDITS is:", MUTED)]]
Q2_OPTIONS = [("a", "Criticism"), ("b", "Praise"), ("c", "Funding"), ("d", "Predictions")]

ROUTINE = [["Step 1", "Cover the options. Predict a meaning from the word or the sentence."],
           ["Step 2", "Fix the part of speech."],
           ["Step 3", "Read the charge: positive, negative or neutral?"],
           ["Step 4", "Use clues: roots, context signals, the cluster."],
           ["Step 5", "Eliminate: look-alikes, opposites, merely related, wrong part of speech."],
           ["Step 6", "Substitute the survivors into a sentence."],
           ["Step 7", "Decide: answer, guess (if at least one option is eliminated), or skip."]]
SIGNALS = [["Contrast", "(meaning flips)", "despite, although, but, however, yet, whereas"],
           ["Cause", "(meaning follows)", "because, since, so, therefore, hence"],
           ["Same way", "(meaning matches)", "and, also, similarly, as well as, i.e."]]


class SynonymQuestionSolvingTechniques(LMSScene):
    lesson_title = "Synonym Question-Solving Techniques"

    def construct(self):
        self.camera.background_color = BG
        self.cast = None
        self.title_bar = None
        self.spoken = None
        self.talking = None
        self.faces = {}

        self.hook()
        self.topic()
        self.exam()
        self.attempts()
        self.what()
        self.signals()
        self.roots()
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
        one_line = text(title, TITLE, INK, BOLD).width <= 2 * EDGE_X - 1.0
        name = VGroup(*[text(s, TITLE, INK, BOLD) for s in (title if one_line else wrap_lines(title, 2)).split("\n")])
        name.arrange(DOWN, buff=0.22)                 # a long title goes on two centred lines
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

    # ============================================ 1. GUESS OR SKIP? ========

    def hook(self):
        self.scene_start("S01_hook", title="Guess or Skip?")
        card = self.opening("Synonym Question-Solving Techniques", "Exam-oriented synonyms")
        self.heading("Guess or skip?")

        marks = phrase(text("+3 correct", LABEL, GOOD, BOLD), text("-1 wrong", LABEL, BAD, BOLD),
                       text("0 skipped ?", LABEL, MUTED, BOLD), buff=0.9)
        place(marks, x=0.0, top=BOARD_TOP - 0.15)
        check = text("Always check the current official notification", SMALL, MUTED).next_to(marks, DOWN, buff=0.2)
        g = Grid(GUESS, (3.0, 4.4, 2.9, 1.9), row_h=0.55, header=False,
                 styles=[(MUTED, NORMAL), (INK, NORMAL), (INK, NORMAL), (BLUE, BOLD)])
        place(g, x=0.0, top=0.05)
        base = -2.95
        chart = VGroup()
        for k, n in enumerate((4, 3, 2)):
            value = expected(n)
            height = max(0.05, 0.8 * value)
            bar = Rectangle(width=0.9, height=height, stroke_width=0, fill_color=BLUE if value else MUTED,
                            fill_opacity=1).move_to([-2.2 + 2.2 * k, base + height / 2, 0])
            chart.add(VGroup(bar, text(GUESS[k][3][2:], SMALL, INK, BOLD).next_to(bar, UP, buff=0.12),
                             text(f"{n} options", MIN_FONT, MUTED).move_to([-2.2 + 2.2 * k, base - 0.3, 0])))
        axis = text("Expected marks", SMALL, MUTED).move_to([-5.0, base + 0.4, 0])
        self.fit(VGroup(marks, check), g, VGroup(chart, axis))

        self.N("s1_01", "The confident student has spent the break doing arithmetic on a napkin. Today the class finds "
                        "out whether that napkin is worth a few marks.",
               ("arithmetic", lambda: [FadeOut(card), FadeIn(marks, shift=UP * 0.2)]),
               ("napkin", lambda: self.react("A", "happy")))
        self.Q("s1_02", "C-CAT has used plus three for a correct answer and minus one for a wrong one. Always check "
                        "the current official notification, but let's use that scheme. You have no idea what the word "
                        "means and four options to choose from. Do you guess?",
               ("plus", lambda: hl(marks[0])),
               ("minus", lambda: hl(marks[1])),
               ("official", lambda: FadeIn(check, shift=UP * 0.1)),
               ("four", lambda: FadeIn(g.cell(0, 0), shift=RIGHT * 0.2)),
               shown="No idea what the word means, and four options to choose from. Do you guess?")
        self.S("A", "s1_03", "I worked it out. If I guess randomly, there's a one in four chance of plus three and a "
                             "three in four chance of minus one.",
               ("chance", lambda: FadeIn(g.cell(0, 1), shift=RIGHT * 0.2)),
               ("minus", lambda: FadeIn(g.cell(0, 2), shift=RIGHT * 0.2)),
               shown="I worked it out: a one in four chance of +3, and a three in four chance of -1.", look="happy")
        self.T("s1_04", "Zero. On average, guessing blindly gains you nothing.",
               ("Zero", lambda: FadeIn(g.cell(0, 3), scale=1.3)),
               ("nothing", lambda: hl(g.cell(0, 3), 1.3)))
        self.S("B", "s1_05", "So we should never guess?", look="confused")
        self.Q("s1_06", "What if you can eliminate one option with real confidence?")
        self.speaker("A", "think")
        self.show_line("A", None)
        self.play(LaggedStart(*[FadeIn(m, shift=RIGHT * 0.2) for m in g.row(1)], lag_ratio=0.5), run_time=2.0)
        self.play(LaggedStart(*[FadeIn(m, shift=RIGHT * 0.2) for m in g.row(2)], lag_ratio=0.5), run_time=2.0)
        self.S("D", "s1_07", "So every option you can eliminate turns a guess into an investment.",
               ("eliminate", lambda: [FadeIn(axis)] + [FadeIn(c[2]) for c in chart]),
               ("investment", lambda: LaggedStart(*[AnimationGroup(GrowFromEdge(c[0], DOWN), FadeIn(c[1]))
                                                    for c in chart], lag_ratio=0.4, run_time=2.0)),
               look="think", other="happy")
        self.T("s1_08", "Exactly. Which means the real skill isn't knowing every word. It's eliminating options "
                        "reliably. Let's put together everything from the last five lessons into one technique.",
               ("eliminating", lambda: [hl(c[1], 1.2) for c in chart[1:]]),
               ("technique", lambda: self.react("ABCD", "smile")), look="happy")

        self.finish("S01_hook")

    # ================================================== 2. THE TOPIC =======

    def topic(self):
        self.begin("S02_topic", "The Topic", "Rules need an order")

        name = text("Synonym question-solving techniques", BODY, BLUE, BOLD)
        place(name, x=0.0, top=BOARD_TOP - 0.2)
        spots = [(-5.0, 0.0), (-2.8, -1.5), (-0.9, 0.1), (1.2, -1.1), (3.4, 0.0), (5.2, -1.4), (-4.2, -2.4),
                 (2.6, -2.5)]
        rules = VGroup(*[text(f"Rule {k + 1}", LABEL).move_to([x, y, 0]) for k, (x, y) in enumerate(spots)])
        routine = text("One fixed order: a routine you can run in under a minute", LABEL, BROWN, BOLD)
        routine.move_to(DOWN * 2.1)
        self.fit(name, rules, routine)

        self.T("s2_01", "So far you've collected eight separate rules. Under time pressure, eight separate rules are "
                        "useless. You need them in a fixed order, a routine you can run in under a minute.",
               (None, lambda: FadeIn(name, shift=UP * 0.15)),
               ("eight", lambda: LaggedStart(*[FadeIn(m, scale=1.2) for m in rules], lag_ratio=0.15, run_time=1.6)),
               ("useless", lambda: [rules.animate.set_color(MUTED), self.react("ABCD", "confused")]),
               ("order", lambda: [m.animate.move_to([-5.6 + 1.6 * k, -0.7, 0]).set_color(INK)
                                  for k, m in enumerate(rules)]),
               ("minute", lambda: FadeIn(routine, shift=UP * 0.15)))

        self.finish("S02_topic")

    # ======================================== 3. HOW C-CAT TESTS IT ========

    def exam(self):
        self.begin("S03_exam", "How C-CAT Tests It", "How C-CAT tests it")

        unseen = text("A word you have genuinely never seen", BODY, BLUE, BOLD).move_to(DOWN * 0.3)
        self.q1 = Question("Practice question 1", Q1_LINES, Q1_OPTIONS, SMALL)
        self.q2 = Question("Practice question 2", Q2_LINES, Q2_OPTIONS, SMALL)
        self.both = VGroup(self.q1, self.q2).arrange(DOWN, buff=0.6, aligned_edge=LEFT)
        place(self.both, x=0.0, top=BOARD_TOP - 0.15)
        self.fit(unseen, self.both)
        q1, q2 = self.q1, self.q2

        self.N("s3_01", "The hardest synonym questions give you a word you've genuinely never seen. Here are two "
                        "practice questions written for this class, chosen to be unfamiliar on purpose.",
               ("never", lambda: FadeIn(unseen, shift=UP * 0.15)),
               ("practice", lambda: [FadeOut(unseen), FadeIn(q1, shift=UP * 0.2)]),
               ("unfamiliar", lambda: FadeIn(q2, shift=UP * 0.2)))
        self.T("s3_02", "Forty-five seconds. If you don't know the word, don't panic. Work with what you do know.",
               ("panic", lambda: [hl(q1.body[0][1]), hl(q2.body[0][2])]), look="ask", other="think", think=45.0)

        self.scene_end("S03_exam")          # the two questions stay on the board for the next scene

    # ================================================== 4. ATTEMPTS ========

    def attempts(self):
        self.begin("S04_attempts", "Attempts", "First attempts")

        q1, q2 = self.q1, self.q2
        despite = q2.body[0][0]
        pick_1d = under(q1.opts.rows["d"], BLUE)
        pick_2b = under(q2.opts.rows["b"], BROWN)
        worth = text("2 options left: +1.00 on average", SMALL, BROWN, BOLD).next_to(q1.label, RIGHT, buff=0.8)
        flips = text("Despite: the meaning flips", SMALL, BROWN, BOLD).next_to(q2.label, RIGHT, buff=0.8)
        self.fit(worth, flips)

        self.Q("s4_01", "Honestly, who knew obdurate?",
               ("obdurate", lambda: [hl(q1.body[0][1]), self.react("A", "ask"), self.react("BCD", "oops")]),
               shown="Honestly, who knew 'obdurate'?")
        self.Q("s4_02", "So how did you choose?")
        self.S("C", "s4_03", "Durable. It has dur in it.",
               ("Durable", lambda: Create(pick_1d)), shown="Durable. It has 'dur' in it.")
        self.S("B", "s4_04", "I eliminated obedient and obscure. They start with ob, and that felt like a trap. Then I "
                             "was stuck between stubborn and durable.",
               ("eliminated", lambda: q1.opts.out("a", "b")),
               ("stuck", lambda: [hl(q1.opts.rows["c"]), hl(q1.opts.rows["d"])]),
               shown="I eliminated obedient and obscure. Then I was stuck between stubborn and durable.",
               look="think")
        self.T("s4_05", "That's a two option guess, worth plus one on average. Not bad. But can we do better?",
               ("plus", lambda: FadeIn(worth, shift=LEFT * 0.2)), look="smile")
        self.S("D", "s4_06", "I don't know plaudits either. But despite means the next part goes against it. The "
                             "product failed, so the plaudits must have been good. Praise?",
               ("despite", lambda: [despite.animate.set_color(BROWN), FadeIn(flips, shift=LEFT * 0.2)]),
               ("failed", lambda: hl(q2.body[1][0], 1.04)),
               ("Praise", lambda: Create(pick_2b)),
               shown="'Despite' means the next part goes against it. The product failed, so plaudits were good.",
               look="think")
        self.Q("s4_07", "Did you all notice what just happened? A word nobody knew got solved using a word everybody "
                        "knows: despite.",
               ("despite", lambda: [hl(despite, 1.3), self.react("ABCD", "happy")]),
               shown="A word nobody knew got solved using a word everybody knows: 'despite'.", look="happy",
               other="happy")

        self.finish("S04_attempts")

    # ========================================== 5. WHAT: THE ROUTINE =======

    def what(self):
        self.begin("S05_what", "WHAT: The Routine", "The synonym routine")

        g = Grid(ROUTINE, (1.5, 11.6), size=SMALL, row_h=0.5, header=False, styles=[(BLUE, BOLD), (INK, NORMAL)])
        place(g, x=0.0, top=BOARD_TOP - 0.15)
        note = text("Understand first, then eliminate", LABEL, BROWN, BOLD).move_to(DOWN * 3.0)
        self.fit(g, note)

        self.play(LaggedStart(*[FadeIn(g.row(r), shift=RIGHT * 0.2) for r in range(7)], lag_ratio=0.45), run_time=5.0)
        self.countdown(6.0)                 # time to read the seven steps: the script does not read them out
        self.T("s5_01", "Notice that elimination comes after understanding, not before. If you eliminate before you "
                        "understand the word, you're only judging how the options look.",
               ("elimination", lambda: hl(g.row(4), 1.03)),
               ("understanding", lambda: [g.cell(r, 0).animate.set_color(BROWN) for r in range(4)]),
               ("judging", lambda: FadeIn(note, shift=UP * 0.15)))

        self.finish("S05_what")

    # ================================ 6. HOW: CONTEXT SIGNAL WORDS =========

    def signals(self):
        self.begin("S06_signals", "HOW: Context Signal Words", "Context signal words")

        g = Grid(SIGNALS, (2.0, 3.0, 8.0), size=SMALL, row_h=0.5, header=False,
                 styles=[(BLUE, BOLD), (MUTED, NORMAL), (INK, NORMAL)])
        place(g, x=0.0, top=BOARD_TOP - 0.15)
        var = para(['"The new hire was', ("PUNCTILIOUS;", BLUE, BOLD), "every commit message followed"],
                   ['the style guide exactly."'])
        place(var, x=0.0, top=-0.7)
        self.fit(g, var)
        word = var[0][1]
        clause = VGroup(var[0][2], var[1][0])
        back = Arrow(RIGHT * 0.4, LEFT * 0.4, buff=0, color=BROWN, stroke_width=4, tip_length=0.18)
        explains = VGroup(back, text("explains the first part", SMALL, BROWN, BOLD)).arrange(RIGHT, buff=0.25)
        explains.next_to(var[1][0], RIGHT, buff=0.5)
        means = text("punctilious = extremely careful about details", LABEL).move_to(DOWN * 2.3)
        same = text("A semicolon or a colon often works like 'that is'", LABEL, BROWN, BOLD).move_to(DOWN * 3.0)
        self.fit(explains, means, same)

        self.T("s6_01", "The second question was solved by a signal word. These words tell you how two parts of a "
                        "sentence relate to each other.",
               ("signal", lambda: LaggedStart(*[FadeIn(g.row(r), shift=RIGHT * 0.2) for r in range(3)], lag_ratio=0.4,
                                              run_time=2.0)),
               ("relate", lambda: hl(g.col(1), 1.05)))
        self.Q("s6_02", "There's no signal word. Just a semicolon. What does the semicolon tell you?",
               (None, lambda: FadeIn(var, shift=UP * 0.2)),
               ("semicolon", lambda: hl(word)))
        self.S("A", "s6_03", "The second part explains the first. So punctilious means extremely careful about "
                             "details.",
               ("explains", lambda: [clause.animate.set_color(BROWN), FadeIn(explains, shift=LEFT * 0.2)]),
               ("careful", lambda: FadeIn(means, shift=UP * 0.15)), look="think", other="happy")
        self.T("s6_04", "Right. A semicolon or a colon often works like that is. Now, roots. Back to obdurate.",
               ("colon", lambda: FadeIn(same, shift=UP * 0.15)),
               ("roots", lambda: self.react("ABCD", "smile")), look="happy")

        self.finish("S06_signals")

    # ======================= 7. HOW: ROOTS, AND WHEN THEY MISLEAD ==========

    def roots(self):
        self.begin("S07_roots", "HOW: Roots, and When They Mislead", "Roots and their traps")

        whole = text("OBDURATE", TITLE, INK, BOLD)
        split = para([("OB", MUTED, BOLD), ("DUR", BROWN, BOLD), ("ATE", MUTED, BOLD)], size=TITLE)
        place(whole, x=0.0, top=BOARD_TOP - 0.15)
        split.move_to(whole)
        family = phrase(text("dur = hard, lasting:", LABEL, BROWN, BOLD), text("durable,  endure", LABEL), buff=0.35)
        family.move_to(DOWN * 0.15)
        latin = text("From a Latin verb, 'to harden': a heart that has been hardened", SMALL, MUTED).move_to(DOWN * 0.8)
        left = column(text("Durable laptop", LABEL, BLUE, BOLD), text("a hard-wearing object", SMALL), buff=0.18)
        right = column(text("Obdurate manager", LABEL, BROWN, BOLD), text("a hardened attitude", SMALL), buff=0.18)
        place(left, left=-5.2, top=-1.45)
        place(right, left=0.8, top=-1.45)
        trap = text("Root trap: same root, different job", SMALL, BAD, BOLD).next_to(left, DOWN, buff=0.2,
                                                                                     aligned_edge=LEFT)
        answer = text("= stubborn", LABEL, GOOD, BOLD).next_to(right[0], RIGHT, buff=0.35)
        rule = text("A root is a clue, not an answer", BODY, INK, BOLD).move_to(DOWN * 3.1)
        self.fit(whole, family, latin, VGroup(left, right, trap, answer), rule)

        self.T("s7_01", "The root dur comes from Latin and is linked to hardness and lasting. You see it in durable and "
                        "endure. Obdurate comes from a Latin verb meaning to harden. So the image is a heart that has "
                        "been hardened.",
               (None, lambda: FadeIn(whole, shift=UP * 0.2)),
               ("root", lambda: [FadeOut(whole), FadeIn(split)]),
               ("durable", lambda: FadeIn(family, shift=UP * 0.15)),
               ("harden", lambda: FadeIn(latin, shift=UP * 0.15)))
        self.S("C", "s7_02", "So durable is right after all.",
               (None, lambda: hl(family[1], 1.06)), look="happy")
        self.Q("s7_03", "Careful. Durable means long-lasting, and we use it for objects, like a durable laptop. "
                        "Obdurate is used for people, and it means hardened in attitude. What's the word for a person "
                        "with a hardened attitude?",
               ("objects", lambda: [FadeIn(left, shift=UP * 0.15), self.react("C", "oops")]),
               ("people", lambda: FadeIn(right, shift=UP * 0.15)),
               shown="What is the word for a person with a hardened attitude?")
        self.S("B", "s7_04", "Stubborn.", (None, lambda: FadeIn(answer, shift=LEFT * 0.2)))
        self.T("s7_05", "So the root got you to the right neighbourhood. The part of speech and the kind of thing the "
                        "word describes took you to the right house. Durable is the root trap: the same root, but a "
                        "different job. Remember verbal and verbose.",
               ("neighbourhood", lambda: hl(split[0][1])),
               ("house", lambda: hl(right, 1.05)),
               ("trap", lambda: [left[0].animate.set_color(BAD), FadeIn(trap, shift=UP * 0.1)]))
        self.S("D", "s7_06", "So a root is a clue, not an answer.",
               ("clue", lambda: FadeIn(rule, shift=UP * 0.15)), look="think", other="happy")
        self.T("s7_07", "Exactly. Roots narrow down the meaning. Substitution confirms it.",
               ("narrow", lambda: hl(split[0][1])),
               ("Substitution", lambda: hl(answer)), look="happy")

        self.finish("S07_roots")

    # ============================ 8. WHY: THE ROUTINE BEATS MEMORY =========

    def why(self):
        self.begin("S08_why", "WHY: The Routine Beats Memory", "Routine beats memory")

        left = column(text("1,000 words, no routine", LABEL, MUTED, BOLD), text("Unfamiliar word: a blind guess", LABEL),
                      text("Expected gain: 0", LABEL, BAD, BOLD), buff=0.4)
        right = column(text("500 words and a routine", LABEL, BLUE, BOLD), text("Unfamiliar word: eliminate first", LABEL),
                       text("Expected gain: +0.33 to +1.00", LABEL, GOOD, BOLD), buff=0.4)
        place(left, left=-EDGE_X + 0.4, top=BOARD_TOP - 0.4)
        place(right, left=0.5, top=BOARD_TOP - 0.4)
        total = text("Over 50 questions: real marks and real ranks", BODY, BROWN, BOLD).move_to(DOWN * 2.4)
        self.fit(VGroup(left, right), total)

        self.N("s8_01", "A student who knows a thousand words but has no routine guesses blindly whenever a word is "
                        "unfamiliar. A student who knows five hundred words and has a routine eliminates first, and "
                        "turns every unfamiliar word into an expected gain. Over fifty questions, that difference "
                        "adds up to real marks and real ranks.",
               ("thousand", lambda: FadeIn(left[0], shift=UP * 0.15)),
               ("blindly", lambda: [FadeIn(left[1], shift=UP * 0.15), FadeIn(left[2], shift=UP * 0.15)]),
               ("five", lambda: FadeIn(right[0], shift=UP * 0.15)),
               ("eliminates", lambda: FadeIn(right[1], shift=UP * 0.15)),
               ("gain", lambda: FadeIn(right[2], shift=UP * 0.15)),
               ("fifty", lambda: FadeIn(total, shift=UP * 0.15)))

        self.finish("S08_why")

    # ============================== 9. PAYOFF: RUNNING THE ROUTINE =========

    def payoff(self):
        self.begin("S09_payoff", "Payoff: Running the Routine", "Running the routine")

        q1 = Question("Practice question 1", Q1_LINES, Q1_OPTIONS, LABEL, across=False)
        place(q1, left=-EDGE_X + 0.3, top=BOARD_TOP - 0.1)
        self.fit(q1)
        n1 = {k: q1.opts.note(k, s, c) for k, s, c in (("a", "nearly the opposite", BAD),
                                                         ("b", "look-alike: it means unclear", BAD),
                                                         ("c", "a hardened attitude", GOOD),
                                                         ("d", "root trap: objects that last", BAD))}
        log = column(phrase(text("1  Predict: hardened", SMALL, BROWN), text("2  An adjective", SMALL, BROWN),
                            text("3  Charge: negative", SMALL, BROWN), buff=0.6),
                     phrase(text("4  Root 'dur': hard, used for people", SMALL, BROWN),
                            text("5  Eliminate", SMALL, BROWN), buff=0.6),
                     text('6  "The manager remained stubborn about the deadline."', SMALL, BROWN), buff=0.14)
        place(log, left=q1.get_left()[0], top=-2.25)
        self.fit(log)
        steps = [*log[0], *log[1], log[2]]

        q2 = Question("Practice question 2", Q2_LINES[:2], Q2_OPTIONS, LABEL, across=False)
        place(q2, left=-EDGE_X + 0.3, top=BOARD_TOP - 0.1)
        self.fit(q2)
        despite = q2.body[0][0]
        n2 = {k: q2.opts.note(k, s, c) for k, s, c in (("a", "the opposite", BAD),
                                                         ("b", "enthusiastic praise", GOOD),
                                                         ("c", "does not fit the contrast", BAD),
                                                         ("d", "does not fit the contrast", BAD))}
        signal = text("4  Despite = contrast: the product failed, so plaudits are positive", SMALL, BROWN)
        place(signal, left=q2.get_left()[0], y=-3.05)
        decide = text("7  Decide: answer (no guess needed)", SMALL, GOOD, BOLD).next_to(q2.label, RIGHT, buff=0.8)
        self.fit(signal, decide)

        self.T("s9_01", "Let's run the routine on question one.", (None, lambda: FadeIn(q1, shift=UP * 0.2)))
        self.S("B", "s9_02", "Step one: predict. From the root, something like hardened. Step two: it's an adjective. "
                             "Step three: the charge is probably negative. Hard-hearted isn't a compliment.",
               ("predict", lambda: FadeIn(steps[0], shift=UP * 0.1)),
               ("adjective", lambda: FadeIn(steps[1], shift=UP * 0.1)),
               ("negative", lambda: FadeIn(steps[2], shift=UP * 0.1)),
               shown="Step 1: something like 'hardened'. Step 2: an adjective. Step 3: probably negative.",
               look="think")
        self.S("C", "s9_03", "Step four: the root dur means hard, used for people. Step five: eliminate. Obedient is "
                             "close to the opposite. Obscure means unclear, so it's a look-alike. Durable is the root "
                             "trap, because it's about objects lasting.",
               ("root", lambda: FadeIn(steps[3], shift=UP * 0.1)),
               ("eliminate", lambda: FadeIn(steps[4], shift=UP * 0.1)),
               ("Obedient", lambda: [*q1.opts.out("a"), FadeIn(n1["a"], shift=RIGHT * 0.2)]),
               ("Obscure", lambda: [*q1.opts.out("b"), FadeIn(n1["b"], shift=RIGHT * 0.2)]),
               ("Durable", lambda: [*q1.opts.out("d"), FadeIn(n1["d"], shift=RIGHT * 0.2)]),
               shown="Step 4: 'dur' means hard, for people. Step 5: eliminate obedient, obscure and durable.",
               look="think")
        self.S("A", "s9_04", "Step six: substitute. The manager remained stubborn about the deadline. That works. So "
                             "the answer is option C, stubborn.",
               ("substitute", lambda: FadeIn(steps[5], shift=UP * 0.1)),
               ("answer", lambda: [*q1.opts.right("c"), FadeIn(n1["c"], shift=RIGHT * 0.2)]),
               shown="Step 6: 'The manager remained stubborn about the deadline.' That works. So (c) stubborn.",
               other="happy")

        self.wipe()
        self.T("s9_05", "Question two.", (None, lambda: FadeIn(q2, shift=UP * 0.2)), look="ask")
        self.S("D", "s9_06", "Step four: the context signal despite means contrast. The product failed, so plaudits "
                             "are positive. Step five: criticism is the opposite. Funding and predictions don't fit "
                             "the contrast with failing. Plaudits means enthusiastic praise, so the answer is option "
                             "B, praise.",
               ("despite", lambda: [despite.animate.set_color(BROWN), FadeIn(signal, shift=UP * 0.1)]),
               ("criticism", lambda: [*q2.opts.out("a"), FadeIn(n2["a"], shift=RIGHT * 0.2)]),
               ("Funding", lambda: [*q2.opts.out("c", "d"), FadeIn(VGroup(n2["c"], n2["d"]), shift=RIGHT * 0.2)]),
               ("answer", lambda: [*q2.opts.right("b"), FadeIn(n2["b"], shift=RIGHT * 0.2)]),
               shown="'Despite' signals a contrast: the product failed, so plaudits are positive. So (b) praise.",
               look="think", other="happy")
        self.Q("s9_07", "And the strategy decision?")
        self.S("B", "s9_08", "Answer. We didn't need to guess.",
               ("Answer", lambda: FadeIn(decide, shift=LEFT * 0.2)), look="happy", other="happy")

        self.finish("S09_payoff")

    # ================================================= 10. SUMMARY =========

    def summary(self):
        self.begin("S10_summary", "Summary", "Summary")

        points = bullets(["Run the routine in order", "Unsure? Guess only after eliminating at least one option"],
                         BODY, 0.4)
        line = column(text("Blind guess = 0 expected marks", LABEL, BROWN, BOLD),
                      text("Each elimination turns a guess into a gain", LABEL, BROWN, BOLD), buff=0.25)
        board = column(points, line, buff=0.8)
        place(board, x=0.0, top=BOARD_TOP - 0.4)
        self.fit(board)

        self.Q("s10_01", "Today in one sentence?")
        self.S("A", "s10_02", "Run the routine in order, and when you're unsure, guess only after eliminating at least "
                              "one option.",
               ("routine", lambda: FadeIn(points[0], shift=RIGHT * 0.2)),
               ("guess", lambda: FadeIn(points[1], shift=RIGHT * 0.2)),
               ("option", lambda: FadeIn(line, shift=UP * 0.15)), other="happy")

        self.finish("S10_summary")

    # ========================================= 11. WHAT COMES NEXT =========

    def next_session(self):
        self.begin("S11_next", "What Comes Next", "What comes next?")

        can = text("The class can now find a synonym", BODY).move_to(UP * 0.1)
        harder = text("Harder: replace a word so the sentence still works", BODY, BROWN).move_to(DOWN * 0.8)
        sent = para(['"All employees must', ("COMPLY WITH", BLUE, BOLD), 'the security policy."'], size=BODY)
        place(sent, x=0.0, top=BOARD_TOP - 0.4)
        choice = para([("Replace the capitalised words:", MUTED), ("obey", INK, BOLD), ("/", MUTED),
                       ("adhere", INK, BOLD)])
        place(choice, x=0.0, y=-0.5)
        trial = text('"All employees must adhere the security policy" ?', LABEL, BAD).move_to(DOWN * 1.6)
        nxt = text("Next session:  Word substitution in a sentence with a synonym", LABEL, BROWN, BOLD)
        nxt.move_to(DOWN * 2.9)
        self.fit(can, harder, sent, choice, trial, nxt)
        adhere = choice[0][3]

        self.N("s11_01", "The class can now find a synonym. But the exam sometimes asks for something harder: "
                         "replacing a word inside a sentence so that the sentence still works.",
               ("synonym", lambda: FadeIn(can, shift=UP * 0.15)),
               ("replacing", lambda: FadeIn(harder, shift=UP * 0.15)))
        self.wipe()
        self.Q("s11_02", "Both mean follow the rules. So why does one of them break the sentence?",
               (None, lambda: [FadeIn(sent, shift=UP * 0.2), FadeIn(choice, shift=UP * 0.2)]),
               ("break", lambda: [FadeIn(trial, shift=UP * 0.15), hl(adhere, 1.2, BAD), self.react("C", "oops")]),
               other="confused")
        self.T("s11_03", "Next session.", (None, lambda: FadeIn(nxt, shift=UP * 0.15)))

        self.the_end("S11_next")

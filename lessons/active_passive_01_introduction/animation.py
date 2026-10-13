"""
animation.py for the LMS video generator.

Course : C-CAT Preparation - Section A: English Language and Verbal Ability
Module : 2 Grammar   Lesson : 6 Active and Passive Voice (Session 11)
Video  : 01 - Introduction to Active and Passive Voice   (previous: Exam practice (Articles);  next: Active vs passive)
Source : C:/Final scripts/Scipts/Second/01 - Introduction.pdf

Note: the two questions are practice questions written for the class, not past-paper questions.

Look (3Blue1Brown style): near-black background, white text, ONE blue and ONE brown accent; yellow only for a
  passing highlight, green / red only for right / wrong. Latin Modern Roman (Cambria if it is missing).
  Sizes: title 54, heading 38, body 32, label 28, small 24.

Roles (the script has no speaker labels; every line was assigned by meaning, and no label is spoken):
  NARRATOR   voice-over, connects the scenes          self.N              voice "vijay"
  TEACHER    teaches, asks, guides                    self.T / self.Q     voice "aditya"
  STUDENT A  the confident one, near the window       self.S("A", ...)    voice "prasad"
  STUDENT B  the cautious one, front row              self.S("B", ...)    voice "kavya"
  STUDENT C  the second student                       self.S("C", ...)    voice "ritu"
  STUDENT D  at the back, arms folded                 self.S("D", ...)    voice "student_a"
  Stage directions are not spoken: they are the visuals. Board text that the script does not speak
  (rule cards, steps) is shown with a thinking bar that gives time to read it.

Sarvam AI voices (settings.json > audio.sarvam.voices, or --speaker VOICE=SPEAKER):
    "vijay": "vijay", "aditya": "aditya", "prasad": "kabir", "kavya": "kavya", "ritu": "ritu", "student_a": "rahul"

The two questions have whole sentences as options, so they are shown one at a time; the thinking time
is split between them.

Section map:
  S01 Deleted by whom?   S02 Naming the idea   S03 How C-CAT tests it   S04 Attempts
  S05 WHAT: the passive needs an object   S06 HOW: three moves   S07 WHY: choosing the voice
  S08 Payoff   S09 Summary   S10 What comes next
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


def up(mob):
    """Fade in, rising a little."""
    return FadeIn(mob, shift=UP * 0.15)


def side(mob):
    """Fade in, sliding in from the left."""
    return FadeIn(mob, shift=RIGHT * 0.2)


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

    def __init__(self, items, size=LABEL, across=False, gap=0.7, roomy=False):
        super().__init__()
        self.rows, self.across, self.roomy = {}, across, roomy
        x, step = 0.0, size * (0.033 if roomy else 0.0195)       # roomy: space for a note under every option
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
        if self.roomy:
            return text(s, MIN_FONT, color).next_to(row[1], DOWN, buff=0.12, aligned_edge=LEFT)
        x = max(r.get_right()[0] for r in self.rows.values()) + 0.9
        return fit_w(place(text(s, size, color), left=x, y=row.get_y()), EDGE_X - x)


class Question(VGroup):
    """A practice question: its label, the sentence (lines of pieces, see ``para``) and the options."""

    def __init__(self, label, lines, options, size=LABEL, across=True, roomy=False):
        super().__init__()
        self.label = text(label, SMALL, MUTED, BOLD)
        self.body = para(*lines, size=size)
        self.opts = Options(options, size, across, roomy=roomy)
        self.add(self.label, self.body, self.opts)
        self.arrange(DOWN, buff=size * 0.0085, aligned_edge=LEFT)


def sentence_question(label, stem, options, letters="abcd", size=SMALL):
    """A question whose options are whole sentences: one under another, with room for a note under each."""
    q = Question(label, stem, list(zip(letters, options)), size, across=False, roomy=True)
    return place(q, left=-EDGE_X + 0.3, top=BOARD_TOP - 0.1)


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

CRUMB = "C-CAT Preparation  ›  English  ›  Grammar  ›  Active and Passive Voice"

Q1 = ("Practice question 1",
      [[("Choose the correct passive form of:", MUTED)], ['"The QA team tested the new login module."']],
      ["The new login module is tested by the QA team.", "The new login module was tested by the QA team.",
       "The new login module was test by the QA team.", "The QA team was tested by the new login module."])
Q2 = ("Practice question 2",
      [[("Which sentence CANNOT be changed into the passive voice?", MUTED)]],
      ["The admin reset the password.", "The server crashed at midnight.", "The script generated a report.",
       "The client approved the budget."])

RULES = ["1.  The passive is formed with BE (in the original tense) + the past participle (V3)",
         "2.  The object of the active sentence becomes the subject of the passive",
         "3.  The original subject moves to a 'by' phrase, or disappears",
         "4.  So only verbs that take an object (transitive verbs) have a passive"]
MOVES = [["Step 1", "Find the object", '"the new login module"'],
         ["Step 2", "Move it to the front", '"The new login module ..."'],
         ["Step 3", "Verb: BE in the same tense + V3", '"was tested"'],
         ["", "Add 'by' + the old subject, if useful", '"by the QA team."']]
USES = [("Lab report", '"The samples were heated to 80 degrees C."', "Who heated them does not matter"),
        ("Status page", '"The issue has been resolved."', "The focus is on the system, not the person"),
        ("Bug report", '"The test suite deleted the staging data."', "The doer is the key information")]


class IntroductionToActiveAndPassiveVoice(LMSScene):
    lesson_title = "Introduction to Active and Passive Voice"

    def construct(self):
        self.camera.background_color = BG
        self.cast = None
        self.title_bar = None
        self.spoken = None
        self.talking = None
        self.faces = {}
        self.q_now, self.q_marks, self.picked = None, [], {}

        self.hook()
        self.naming()
        self.exam()
        self.attempts()
        self.what()
        self.how()
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
        self.q_now, self.q_marks, self.picked = None, [], {}

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

    # -------------------------------------------- questions on the board --

    def show_question(self, q):
        """Put question ``q`` on the board, in place of the question (and its marks) that is there."""
        old = [m for m in (getattr(self, "q_now", None), *getattr(self, "q_marks", [])) if m is not None]
        anims = [FadeIn(q, shift=UP * 0.15)] + ([FadeOut(VGroup(*old))] if old else [])
        self.play(*anims, run_time=0.6)
        self.q_now, self.q_marks, self.picked = q, [], {}

    def keep(self, mob):
        """A mark that belongs to the question on the board: it leaves with the question."""
        self.q_marks = getattr(self, "q_marks", []) + [mob]
        return mob

    def pick(self, q, letter, color=BLUE):
        """A student's choice: a line under the option."""
        line = self.keep(under(q.opts.rows[letter], color))
        self.picked = {**getattr(self, "picked", {}), letter: line}
        return Create(line)

    def repick(self, letter, color=BAD):
        """The line under a choice changes colour (the choice turned out wrong)."""
        return self.picked[letter].animate.set_color(color)

    def tag(self, q, letter, s, color=BROWN):
        """A short note for one option."""
        return FadeIn(self.keep(q.opts.note(letter, s, color)), shift=RIGHT * 0.2)

    def yes(self, q, letter, s=None):
        """The answer: green, with a tick and an optional note. The tick leaves with its question."""
        row = q.opts.rows[letter]
        mark = self.keep(tick(0.26).next_to(row, RIGHT, buff=0.16))
        return [row.animate.set_color(GOOD), FadeIn(mark, scale=0.6)] + ([self.tag(q, letter, s, GOOD)] if s else [])

    def no(self, q, letters, s=None):
        """Wrong options go grey; each gets the same optional note."""
        return q.opts.out(*letters) + ([self.tag(q, letter, s, BAD) for letter in letters] if s else [])

    def timed(self, nid, spoken, q2, seconds, *cues):
        """The teacher gives the time: half of it runs on the question on the board, half on ``q2``."""
        self.T(nid, spoken, *cues, look="ask", other="think", think=seconds / 2)
        self.show_question(q2)
        self.countdown(seconds / 2)

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

    # ============================================ 1. DELETED BY WHOM? ======

    def hook(self):
        self.scene_start("S01_hook", title="Deleted by Whom?")
        card = self.opening("Introduction to Active and Passive Voice", "Exam practice (Articles)")
        self.heading("Deleted by whom?")

        head = text("Incident report", SMALL, MUTED, BOLD)
        s1 = para(['"At 2:07 AM,', ("the production database", INK), ("was deleted.\"", BLUE, BOLD)])
        s2 = para(['"At 2:07 AM,', ("Ravi", BROWN, BOLD), ("deleted", BLUE, BOLD), 'the production database."'])
        board = VGroup(head, s1, s2).arrange(DOWN, buff=0.35, aligned_edge=LEFT)
        s2.shift(DOWN * 0.75)
        place(board, x=-0.8, top=BOARD_TOP - 0.15)
        ghost = text("by whom?", LABEL, MUTED).next_to(s1, RIGHT, buff=0.4)
        tag1 = text("The database is at the front: the doer can hide", SMALL, BLUE)
        tag2 = text("Ravi is at the front: he is responsible", SMALL, BROWN)
        tag1.next_to(s1, DOWN, buff=0.2, aligned_edge=LEFT)
        tag2.next_to(s2, DOWN, buff=0.2, aligned_edge=LEFT)
        focus = text("Same fact, a different focus", BODY, INK, BOLD).move_to(DOWN * 2.8)
        self.fit(VGroup(board, ghost, tag1, tag2), focus)

        self.N("s1_01", "One sentence in an incident report. It tells you what happened and when. It leaves out the "
                        "one thing everyone wants to know.",
               ("sentence", lambda: [FadeOut(card), FadeIn(head), up(s1)]),
               ("leaves", lambda: FadeIn(ghost, shift=LEFT * 0.2)))
        self.Q("s1_02", "Who deleted the database?", (None, lambda: hl(ghost)))
        self.S("A", "s1_03", "It doesn't say.")
        self.Q("s1_04", "Is the sentence grammatically wrong?")
        self.S("B", "s1_05", "No. It's correct. It just leaves out the person.",
               ("person", lambda: hl(ghost)), look="think")
        self.Q("s1_06", "Same event. How does this one feel?", (None, lambda: up(s2)))
        self.S("D", "s1_07", "Like Ravi's in trouble.",
               ("trouble", lambda: [hl(s2[0][1], 1.3), self.react("ABC", "happy")]), other="happy")
        self.T("s1_08", "Both sentences describe exactly the same event. But the first puts the database at the front "
                        "and can hide who did it. The second puts Ravi at the front and makes him responsible.",
               ("first", lambda: [hl(s1[0][1], 1.05), FadeIn(tag1)]),
               ("second", lambda: [hl(s2[0][1], 1.3), FadeIn(tag2)]))
        self.S("C", "s1_09", "So it's the same fact, just a different focus.",
               ("focus", lambda: up(focus)), look="think", other="happy")

        self.finish("S01_hook")

    # ============================================ 2. NAMING THE IDEA =======

    def naming(self):
        self.begin("S02_naming", "Naming the Idea", "Active and passive")

        xs = (-6.0, -3.4, 0.5, 3.6)

        def row(y, cells, roles, colors):
            top = VGroup(*[line_at(s, x, y, BODY, c, BOLD if k == 0 else NORMAL)
                           for k, (s, x, c) in enumerate(zip(cells, xs, colors))])
            under_ = VGroup(*[line_at(s, x, y - 0.5, SMALL, MUTED) for s, x in zip(roles, xs[1:])])
            return top, under_

        act, act_r = row(0.7, ("Active", "Ravi", "deleted", "the database."), ("(doer)", "(action)", "(receiver)"),
                         (MUTED, BROWN, BLUE, INK))
        pas, pas_r = row(-1.2, ("Passive", "The database", "was deleted", "(by Ravi)."),
                         ("(receiver)", "(be + V3)", "(doer, optional)"), (MUTED, INK, BLUE, BROWN))
        self.fit(VGroup(act, act_r, pas, pas_r))

        self.T("s2_01", "In the active voice, the subject performs the action. Ravi deleted the database. In the "
                        "passive voice, the subject receives the action. The database was deleted, with or without "
                        "by Ravi.",
               ("active", lambda: up(act)),
               ("performs", lambda: up(act_r)),
               ("passive", lambda: up(pas)),
               ("receives", lambda: up(pas_r)),
               ("without", lambda: hl(pas[3])))

        self.finish("S02_naming")

    # ======================================== 3. HOW C-CAT TESTS IT ========

    def exam(self):
        self.begin("S03_exam", "How C-CAT Tests It", "How C-CAT tests it")

        traps = bullets(["Wrong tense", "Wrong form of BE", "Wrong verb form"], BODY, 0.4)
        place(traps, x=0.0, y=-0.7)
        self.q1, self.q2 = self.fit(sentence_question(*Q1)), self.fit(sentence_question(*Q2))

        self.N("s3_01", "Voice questions usually ask you to choose the correct passive or active form of a sentence. "
                        "The traps are wrong tense, wrong form of be, and the wrong verb form. Two practice "
                        "questions, written for this class.",
               ("tense", lambda: side(traps[0])),
               ("be", lambda: side(traps[1])),
               ("verb", lambda: side(traps[2])),
               ("practice", lambda: FadeOut(traps)),
               (None, lambda: self.show_question(self.q1)))
        self.timed("s3_02", "Forty seconds.", self.q2, 40.0)

        self.scene_end("S03_exam")          # a question stays on the board for the next scene

    # ================================================== 4. ATTEMPTS ========

    def attempts(self):
        self.begin("S04_attempts", "Attempts", "First attempts")
        q1, q2 = self.q1, self.q2

        self.show_question(q1)
        self.Q("s4_01", "Question one?", shown="Question 1?")
        self.S("C", "s4_02", "Option B. Tested is past, so was tested.",
               ("past", lambda: self.pick(q1, "b")), shown="(b). 'Tested' is past, so 'was tested'.")
        self.Q("s4_03", "Why not option A?", shown="Why not (a)?")
        self.S("C", "s4_04", "Is tested is present. The original is past. The tense has to stay the same.",
               ("present", lambda: self.tag(q1, "a", "present: the tense changed")),
               shown="'Is tested' is present. The original is past. The tense has to stay the same.")
        self.Q("s4_05", "And option D?", shown="And (d)?")
        self.S("B", "s4_06", "That reverses who did what. The module tested the team.",
               ("module", lambda: [self.tag(q1, "d", "the roles are reversed"), self.react("ACD", "happy")]),
               look="happy")

        self.show_question(q2)
        self.Q("s4_07", "Question two. This is the interesting one.", shown="Question 2. This is the interesting one.")
        self.S("D", "s4_08", "Option B. The server crashed. Crashed what? There's nothing that received the action.",
               ("crashed", lambda: self.pick(q2, "b")),
               ("nothing", lambda: self.tag(q2, "b", "no object: nothing received the action")),
               shown="(b). 'The server crashed.' Crashed what? Nothing received the action.", look="think")

        self.finish("S04_attempts")

    # ======================= 5. WHAT: THE PASSIVE NEEDS AN OBJECT ==========

    def what(self):
        self.begin("S05_what", "WHAT: The Passive Needs an Object", "It needs an object")

        rules = column(*[text(s, SMALL) for s in RULES], buff=0.24)
        place(rules, x=0.0, top=BOARD_TOP - 0.15)
        no = phrase(text("crash   arrive   happen   sleep", LABEL, BAD, BOLD),
                    text("intransitive: no receiver, no passive", SMALL, MUTED), buff=0.6)
        yes = phrase(text("reset   generate   approve   test", LABEL, GOOD, BOLD),
                     text("transitive: there is a receiver", SMALL, MUTED), buff=0.6)
        place(no, left=rules.get_left()[0], y=-1.35)
        place(yes, left=rules.get_left()[0], y=-2.0)
        error = VGroup(cross(0.24), text('"The accident was happened."', LABEL, BAD), tick(0.24),
                       text('"The accident happened."', LABEL, GOOD)).arrange(RIGHT, buff=0.3)
        place(error, left=rules.get_left()[0], y=-2.9)
        self.fit(VGroup(rules, no, yes, error))

        self.play(LaggedStart(*[side(m) for m in rules], lag_ratio=0.5), run_time=3.0)
        self.countdown(6.0)                 # time to read the four rules: the script does not read them out
        self.S("A", "s5_01", "So crash, arrive, happen and sleep can't be passive.",
               ("crash", lambda: [up(no[0]), hl(rules[3], 1.03)]), look="think")
        self.T("s5_02", "Right. They're intransitive. They don't act on anything. The accident was happened is a "
                        "classic error, because happen has no object to promote.",
               ("intransitive", lambda: up(no[1])),
               ("accident", lambda: up(VGroup(error[0], error[1]))),
               ("object", lambda: [up(VGroup(error[2], error[3])), up(yes)]), look="happy")

        self.finish("S05_what")

    # ============================================ 6. HOW: THREE MOVES ======

    def how(self):
        self.begin("S06_how", "HOW: Three Moves", "Three moves")

        active = para([("Active", MUTED, BOLD), ('"The QA team', BROWN, BOLD), ("tested", BLUE, BOLD),
                       'the new login module."'])
        g = Grid(MOVES, (1.5, 6.6, 4.8), size=SMALL, row_h=0.52, header=False,
                 styles=[(BLUE, BOLD), (INK, NORMAL), (BROWN, NORMAL)])
        result = para([("Passive", MUTED, BOLD), '"The new login module', ("was tested", BLUE, BOLD),
                       ("by the QA team.\"", BROWN, BOLD)])
        board = VGroup(active, g, result).arrange(DOWN, buff=0.45, aligned_edge=LEFT)
        place(board, x=0.0, top=BOARD_TOP - 0.15)
        core = phrase(text("Tense lives in BE", LABEL, BLUE, BOLD), text("Meaning lives in V3", LABEL, BROWN, BOLD),
                      buff=1.2).move_to(DOWN * 3.05)
        self.fit(board, core)

        self.play(up(active), run_time=0.6)
        self.play(LaggedStart(*[side(g.row(r)) for r in range(4)], lag_ratio=0.5), run_time=3.5)
        self.play(up(result), run_time=0.6)
        self.countdown(4.0)                 # time to read the steps: the script does not read them out
        self.S("B", "s6_01", "So be carries the tense, and the main verb is always the third form.",
               ("tense", lambda: hl(result[0][2])), look="think",
               shown="So 'be' carries the tense, and the main verb is always the third form.")
        self.T("s6_02", "Exactly. Tense lives in be. Meaning lives in V three. Next sessions we'll go through every "
                        "tense, but that core never changes.",
               ("Tense", lambda: up(core[0])),
               ("Meaning", lambda: up(core[1])), look="happy")

        self.finish("S06_how")

    # =========================== 7. WHY: CHOOSING THE VOICE DELIBERATELY ===

    def why(self):
        self.begin("S07_why", "WHY: Choosing the Voice Deliberately", "Choosing the voice")

        blocks = VGroup(*[para([(name, BLUE, BOLD), s], [(note, MUTED)], step=0.45) for name, s, note in USES])
        blocks.arrange(DOWN, buff=0.36, aligned_edge=LEFT)
        place(blocks, x=0.0, top=BOARD_TOP - 0.15)
        hide = phrase(text('"Mistakes were made."', LABEL), text("by whom?", LABEL, BAD, BOLD), buff=0.5)
        hide.move_to(DOWN * 2.45)
        notice = text("Voice shows what the writer emphasises, and what they hide", SMALL, BROWN, BOLD)
        notice.move_to(DOWN * 3.1)
        self.fit(blocks, hide, notice)

        self.T("s7_01", "The passive is useful when the receiver matters more than the doer, or when the doer is "
                        "unknown or irrelevant. The active is better when the doer matters, or when you need clear "
                        "responsibility.",
               (None, lambda: LaggedStart(*[up(b) for b in blocks], lag_ratio=0.4, run_time=2.0)),
               ("receiver", lambda: hl(blocks[0][0][0])),
               ("unknown", lambda: hl(blocks[1][0][0])),
               ("active", lambda: hl(blocks[2][0][0])))
        self.S("D", "s7_02", "And sometimes the passive is used to hide responsibility. Mistakes were made.",
               ("Mistakes", lambda: up(hide)), look="think")
        self.T("s7_03", "Exactly. That's why careful readers notice voice. It tells you what the writer chose to "
                        "emphasise, and sometimes what they chose to hide.",
               ("emphasise", lambda: up(notice)), look="happy")

        self.finish("S07_why")

    # ============================ 8. PAYOFF: SOLVING BOTH QUESTIONS ========

    def payoff(self):
        self.begin("S08_payoff", "Payoff: Solving Both Questions", "Solving both questions")
        q1, q2 = self.fit(sentence_question(*Q1)), self.fit(sentence_question(*Q2))

        self.T("s8_01", "Question one.", (None, lambda: self.show_question(q1)), look="ask")
        self.S("C", "s8_02", "Object: the new login module, moved to the front. The tense is simple past, so was. Then "
                             "the V three form, tested. Then by the QA team. The answer is option B. Option A changes "
                             "the tense. In option C, test isn't V three. And option D reverses the roles.",
               ("answer", lambda: self.yes(q1, "b", "object first, 'was' (simple past), V3, then the agent")),
               ("changes", lambda: self.no(q1, "a", "the tense changed")),
               ("test", lambda: self.no(q1, "c", "'test' is not V3")),
               ("reverses", lambda: self.no(q1, "d", "the roles are reversed")),
               shown="Object to the front, 'was' for simple past, then the V3 'tested'. The answer is (b).",
               look="think", other="happy")

        self.T("s8_03", "Question two.", (None, lambda: self.show_question(q2)), look="ask")
        self.S("D", "s8_04", "Option B, the server crashed at midnight. Crash is intransitive here, so there's no "
                             "object to move to the front. The others all have objects: the password, a report, the "
                             "budget.",
               ("intransitive", lambda: self.yes(q2, "b", "intransitive: no object, so no passive")),
               ("password", lambda: self.tag(q2, "a", "object: the password", MUTED)),
               ("report", lambda: self.tag(q2, "c", "object: a report", MUTED)),
               ("budget", lambda: self.tag(q2, "d", "object: the budget", MUTED)),
               shown="(b). 'Crash' is intransitive here: there is no object to move to the front.",
               other="happy")

        self.finish("S08_payoff")

    # ================================================== 9. SUMMARY =========

    def summary(self):
        self.begin("S09_summary", "Summary", "Summary")

        points = bullets(["Active: the subject does the action", "Passive: the subject receives the action",
                          "Passive = BE (in the same tense) + V3", "Only transitive verbs have a passive"], BODY, 0.4)
        place(points, x=0.0, top=BOARD_TOP - 0.4)
        self.fit(points)

        self.Q("s9_01", "Summary?")
        self.S("B", "s9_02", "In the active voice, the subject does the action. In the passive, the subject receives "
                             "it. The passive is be in the same tense plus V three. Only transitive verbs have a "
                             "passive.",
               ("active", lambda: side(points[0])),
               ("receives", lambda: side(points[1])),
               ("tense", lambda: side(points[2])),
               ("transitive", lambda: side(points[3])),
               shown="Active: the subject does the action. Passive: the subject receives it.", other="happy")

        self.finish("S09_summary")

    # ========================================= 10. WHAT COMES NEXT =========

    def next_session(self):
        self.begin("S10_next", "What Comes Next", "What comes next?")

        pair = para(['"The report', ("was submitted", BLUE, BOLD), 'on time."'],
                    ['"The report', ("was ready", BROWN, BOLD), 'on time."'], size=BODY, step=0.9)
        place(pair, x=0.0, top=BOARD_TOP - 0.5)
        mark = text("Only one is passive. Which one?", LABEL, INK, BOLD).move_to(DOWN * 1.6)
        nxt = text("Next session:  Active vs passive", LABEL, BROWN, BOLD).move_to(DOWN * 2.9)
        self.fit(pair, mark, nxt)

        self.N("s10_01", "That's the core. But knowing when to use each voice, and recognising which one a sentence "
                         "is in, takes more practice.",
               ("recognising", lambda: LaggedStart(up(pair[0]), up(pair[1]), lag_ratio=0.5, run_time=1.5)))
        self.Q("s10_02", "Both have was, followed by another word. Only one of them is passive. Which one?",
               ("was", lambda: [hl(pair[0][1], 1.06), hl(pair[1][1], 1.06)]),
               ("Which", lambda: [up(mark), self.react("C", "ask")]),
               shown="Both have 'was', followed by another word. Only one of them is passive. Which one?",
               other="confused")
        self.T("s10_03", "Next session.", (None, lambda: up(nxt)))

        self.the_end("S10_next")

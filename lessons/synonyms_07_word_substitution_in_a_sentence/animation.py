"""
animation.py for the LMS video generator.

Course : C-CAT Preparation - Section A: English Language and Verbal Ability
Module : 1 Vocabulary   Lesson : 1 Synonyms (Session 2)
Video  : 07 - Word Substitution in a Sentence with a Synonym   (previous: Synonym question-solving techniques;
         next: Introduction to antonyms, Lesson 2)
Source : C:/Final scripts/Scipts/07 - Word substitution in a sentence with a synonym.pdf

Note: the two questions are practice questions written for the class, not past-paper questions.

Look (3Blue1Brown style):
  - near-black background, white text, ONE blue and ONE brown accent;
    yellow only for a passing highlight, green / red only for right / wrong
  - text in Latin Modern Roman (from the MiKTeX folder on this machine; Cambria if it is missing), code in Consolas
  - sizes: title 54, heading 38, body 32, label 28, small 24

Roles (the script has no speaker labels; every line was assigned by meaning, and no label is spoken):
  NARRATOR   voice-over, connects the scenes          self.N              voice "vijay"
  TEACHER    teaches, asks, guides                    self.T / self.Q     voice "aditya"
  STUDENT A  the confident one, near the window       self.S("A", ...)    voice "prasad"
  STUDENT B  the cautious one, front row              self.S("B", ...)    voice "kavya"
  STUDENT C  the second student                       self.S("C", ...)    voice "ritu"
  STUDENT D  at the back, arms folded                 self.S("D", ...)    voice "student_a"
  Stage directions are not spoken: they are the visuals.
  "The class answers in pieces" (the meaning, the part of speech, ...) is spoken as five short lines.

Sarvam AI voices: the ids above are voice-library ids. With the Sarvam engine each id is turned into a
  Sarvam speaker by settings.json > audio.sarvam.voices. Six different voices need this map:
    "vijay": "vijay", "aditya": "aditya", "prasad": "kabir", "kavya": "kavya", "ritu": "ritu", "student_a": "rahul"

Screen zones:
  top band   teacher (left corner), scene heading, the four students (right corner)
  strip      the question being asked or the student's line
  board      everything else (BOARD_TOP down to FLOOR)

Section map:
  S01 Why "adhere" breaks the sentence   S02 The topic   S03 How C-CAT tests it   S04 Attempts
  S05 WHAT: what has to match   S06 HOW: patterns and common traps   S07 WHY: your writing gets judged
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

SIGNATURES = """
comply(with: Policy)   -> verb
obey(Policy)           -> verb
adhere(to: Policy)     -> verb
"""
L_COMPLY, L_OBEY, L_ADHERE = range(3)

Q1_LINES = [['"All employees must', ("COMPLY WITH", BLUE, BOLD), 'the security policy."'],
            [("Choose the option that can replace the capitalised part:", MUTED)]]
Q1_OPTIONS = [("a", "obey"), ("b", "adhere"), ("c", "obey to"), ("d", "follow with")]
Q2_LINES = [['"The developer', ("HASTENED", BLUE, BOLD), 'to fix the bug before the client demo."'],
            [("Choose the option that can replace the capitalised word:", MUTED)]]
Q2_OPTIONS = [("a", "hurry"), ("b", "hurried"), ("c", "hurrying"), ("d", "quickened")]

CHECKLIST = [["1.", "Meaning", "the same sense in this context"],
             ["2.", "Part of speech", "noun for noun, verb for verb"],
             ["3.", "Form", "same tense, number and person:  hastened / hurried"],
             ["4.", "Pattern", "same preposition or structure:  comply with / adhere to"],
             ["5.", "Fit", "natural collocation and the same register"]]
PATTERNS = [["Takes a preposition", "Takes a direct object"],
            ["comply with the rules", "obey the rules"],
            ["adhere to the standard", "follow the standard"],
            ["abide by the decision", "accept the decision"],
            ["conform to the format", "match the format"],
            ["depend on the library", "need the library"]]
EXTRA = [["discuss about", "discuss"], ["return back", "return"], ["revert back", "revert"]]


def version(word, color):
    """The opening sentence with ``word`` in the slot."""
    return para(['"All employees must', (word, color, BOLD), 'the security policy."'])


class WordSubstitutionWithASynonym(LMSScene):
    lesson_title = "Word Substitution in a Sentence with a Synonym"

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

    # ========================== 1. WHY "ADHERE" BREAKS THE SENTENCE ========

    def hook(self):
        self.scene_start("S01_hook", title='Why "Adhere" Breaks the Sentence')
        card = self.opening("Word Substitution in a Sentence with a Synonym", "Synonym question-solving techniques")
        self.heading("Why adhere breaks it")

        sent = version("COMPLY WITH", BLUE)
        choice = para([("Replace with:", MUTED), ("obey", INK, BOLD), ("/", MUTED), ("adhere", INK, BOLD)])
        v_obey, v_bad, v_fix = version("obey", GOOD), version("adhere", BAD), version("adhere to", GOOD)
        board = VGroup(sent, choice, v_obey, v_bad, v_fix).arrange(DOWN, buff=0.34, aligned_edge=LEFT)
        place(board, x=-0.5, top=BOARD_TOP - 0.15)
        marks = [tick(0.26).next_to(v_obey, RIGHT, buff=0.35), cross(0.26).next_to(v_bad, RIGHT, buff=0.35),
                 tick(0.26).next_to(v_fix, RIGHT, buff=0.35)]
        grammar = text("What failed: the grammar around the word", LABEL, BROWN, BOLD).move_to(DOWN * 2.9)
        first = VGroup(board, *marks, grammar)
        self.fit(first)

        sig = Listing(SIGNATURES, LABEL)
        place(sig, x=0.0, top=BOARD_TOP - 0.2)
        takes = Grid([["comply", "takes", "with"], ["adhere", "takes", "to"], ["obey", "takes", "its object directly"]],
                     (2.4, 1.6, 4.4), row_h=0.58, header=False,
                     styles=[(BLUE, BOLD), (MUTED, NORMAL), (BROWN, BOLD)])
        place(takes, x=0.0, top=-0.75)
        same = text("Same job, different signatures", BODY, INK, BOLD).move_to(DOWN * 3.0)
        self.fit(sig, takes, same)

        self.N("s1_01", "Two words with the same meaning, and one of them breaks the sentence. The class left with that "
                        "puzzle last time.",
               ("meaning", lambda: [FadeOut(card), FadeIn(sent, shift=UP * 0.2)]),
               ("breaks", lambda: FadeIn(choice, shift=UP * 0.15)),
               ("puzzle", lambda: hl(choice[0][3], 1.2, BAD)))
        self.T("s1_02", "Read both versions out loud.", (None, lambda: [hl(choice[0][1]), hl(choice[0][3])]))
        self.S("A", "s1_03", "All employees must obey the security policy. That's fine.",
               ("obey", lambda: FadeIn(v_obey, shift=RIGHT * 0.2)),
               ("fine", lambda: FadeIn(marks[0], scale=0.6)))
        self.S("A", "s1_04", "All employees must adhere the security policy. That sounds wrong, but adhere does mean "
                             "follow the rules.",
               ("adhere", lambda: FadeIn(v_bad, shift=RIGHT * 0.2)),
               ("wrong", lambda: [FadeIn(marks[1], scale=0.6), self.react("A", "confused")]),
               shown="'...must adhere the security policy.' That sounds wrong, but adhere does mean follow the rules.")
        self.S("B", "s1_05", "It needs something after it. Adhere to. Adhere to the policy.",
               ("to", lambda: [FadeIn(v_fix, shift=RIGHT * 0.2), FadeIn(marks[2], scale=0.6)]), look="think",
               other="happy")
        self.Q("s1_06", "So the meaning was fine, but the sentence still broke. What failed?")
        self.S("D", "s1_07", "The grammar around the word.",
               ("grammar", lambda: FadeIn(grammar, shift=UP * 0.15)))
        self.Q("s1_08", "Programmers, here's another way to see it. You want to replace one function with another that "
                        "does the same job. What do you check before you swap them?",
               ("Programmers", lambda: FadeOut(first)),
               ("function", lambda: FadeIn(VGroup(sig.lines[L_COMPLY], sig.lines[L_OBEY]), shift=UP * 0.15)),
               shown="You replace one function with another that does the same job. What do you check first?")
        self.S("C", "s1_09", "The signature. The parameters and the return type. Otherwise every caller breaks.",
               ("signature", lambda: FadeIn(sig.lines[L_ADHERE], shift=UP * 0.15)),
               ("parameters", lambda: [hl(line, 1.03) for line in sig.lines]))
        self.T("s1_10", "Words have signatures too. Comply takes with. Adhere takes to. Obey takes its object directly, "
                        "with no preposition at all. Same job, different signatures.",
               ("Comply", lambda: [*sig.focus(L_COMPLY), FadeIn(takes.row(0), shift=UP * 0.15)]),
               ("Adhere", lambda: [*sig.focus(L_ADHERE), FadeIn(takes.row(1), shift=UP * 0.15)]),
               ("Obey", lambda: [*sig.focus(L_OBEY), FadeIn(takes.row(2), shift=UP * 0.15)]),
               ("job", lambda: [*sig.focus(None), FadeIn(same, shift=UP * 0.15)]), look="happy")

        self.finish("S01_hook")

    # ================================================== 2. THE TOPIC =======

    def topic(self):
        self.begin("S02_topic", "The Topic", "Substitution questions")

        name = text("Word substitution with a synonym", BODY, BLUE, BOLD)
        sent = para(['"All employees must', ("COMPLY WITH", BLUE, BOLD), 'the security policy."'])
        keep = phrase(VGroup(tick(0.26), text("Keep the meaning", LABEL)).arrange(RIGHT, buff=0.25),
                      VGroup(tick(0.26), text("Keep the grammar", LABEL)).arrange(RIGHT, buff=0.25), buff=1.2)
        slot = text("A synonym is half the job: it also has to fit the slot", LABEL, BROWN, BOLD)
        board = VGroup(name, sent, keep, slot).arrange(DOWN, buff=0.65)
        place(board, x=0.0, top=BOARD_TOP - 0.25)
        self.fit(board)
        marked = under(sent[0][1], BLUE)

        self.T("s2_01", "In these questions, part of a sentence is marked, and you have to choose the replacement that "
                        "keeps both the meaning and the grammar intact. Finding a synonym is only half of the job. The "
                        "replacement also has to fit the slot.",
               (None, lambda: FadeIn(name, shift=UP * 0.15)),
               ("marked", lambda: [FadeIn(sent, shift=UP * 0.15), Create(marked)]),
               ("meaning", lambda: FadeIn(keep[0], shift=UP * 0.15)),
               ("grammar", lambda: FadeIn(keep[1], shift=UP * 0.15)),
               ("half", lambda: FadeIn(slot, shift=UP * 0.15)))

        self.finish("S02_topic")

    # ======================================== 3. HOW C-CAT TESTS IT ========

    def exam(self):
        self.begin("S03_exam", "How C-CAT Tests It", "How C-CAT tests it")

        line1 = text("The options are often all near synonyms", BODY, BLUE, BOLD).move_to(UP * 0.1)
        line2 = text("Only one fits the grammar of the sentence", BODY).move_to(DOWN * 0.7)
        intro = VGroup(line1, line2)
        self.q1 = Question("Practice question 1", Q1_LINES, Q1_OPTIONS, SMALL)
        self.q2 = Question("Practice question 2", Q2_LINES, Q2_OPTIONS, SMALL)
        self.both = VGroup(self.q1, self.q2).arrange(DOWN, buff=0.55, aligned_edge=LEFT)
        place(self.both, x=0.0, top=BOARD_TOP - 0.1)
        self.fit(line1, line2, self.both)
        q1, q2 = self.q1, self.q2

        self.N("s3_01", "Here the options are often all near synonyms. Only one of them fits the sentence's grammar. "
                        "Two practice questions, written for this class.",
               ("near", lambda: FadeIn(line1, shift=UP * 0.15)),
               ("fits", lambda: FadeIn(line2, shift=UP * 0.15)),
               ("practice", lambda: [FadeOut(intro), FadeIn(q1, shift=UP * 0.2)]),
               ("class", lambda: FadeIn(q2, shift=UP * 0.2)))
        self.T("s3_02", "Forty seconds.", (None, lambda: [hl(q1.label), hl(q2.label)]), look="ask", other="think",
               think=40.0)

        self.scene_end("S03_exam")          # the two questions stay on the board for the next scene

    # ================================================== 4. ATTEMPTS ========

    def attempts(self):
        self.begin("S04_attempts", "Attempts", "First attempts")

        q1, q2 = self.q1, self.q2
        pick_a = under(q2.opts.rows["a"], BLUE)
        pick_b = under(q2.opts.rows["b"], BROWN)
        pick_d = under(q2.opts.rows["d"], BLUE)
        trial = text('"The developer quickened to fix the bug." ?', SMALL, BAD).next_to(q2.label, RIGHT, buff=0.8)
        pat1 = text("quicken + one's pace / pulse", SMALL, BROWN, BOLD).next_to(q1.label, RIGHT, buff=0.8)
        pat2 = text("hurry / hasten + to do something", SMALL, BROWN, BOLD).next_to(q2.label, RIGHT, buff=0.8)
        self.fit(trial, pat1, pat2)
        fails = bullets(["The wrong form", "The wrong preposition", "The wrong pattern"], BODY, 0.45)
        head = text("Three ways a substitution can fail", BODY, BROWN, BOLD)
        three = column(head, fails, buff=0.6)
        place(three, x=0.0, y=-1.0)
        self.fit(three)

        self.Q("s4_01", "Question two first.", ("two", lambda: hl(q2.label)), shown="Question 2 first.")
        self.S("C", "s4_02", "Hurry. It's the synonym of hasten.", ("Hurry", lambda: Create(pick_a)))
        self.S("B", "s4_03", "But the developer hurry to fix the bug? It has to be past tense, like hastened. So "
                             "hurried.",
               ("past", lambda: [pick_a.animate.set_color(BAD), hl(q2.body[0][1]), self.react("C", "oops")]),
               ("hurried", lambda: Create(pick_b)), look="think")
        self.S("A", "s4_04", "What about quickened? That's past tense too.",
               ("quickened", lambda: Create(pick_d)), look="ask")
        self.T("s4_05", "Read it.", (None, lambda: FadeIn(trial, shift=LEFT * 0.2)))
        self.S("A", "s4_06", "The developer quickened to fix the bug.", (None, lambda: hl(trial, 1.04)),
               look="confused")
        self.S("A", "s4_07", "That's strange. You quicken your pace. You don't quicken to do something.",
               ("pace", lambda: [FadeIn(pat1, shift=LEFT * 0.2), pick_d.animate.set_color(BAD)]),
               ("something", lambda: [FadeOut(trial), FadeIn(pat2, shift=LEFT * 0.2)]), look="think")
        self.T("s4_08", "Good ear. Now we know three ways a substitution can fail: the wrong form, the wrong "
                        "preposition, and the wrong pattern.",
               ("three", self.wipe),
               (None, lambda: FadeIn(head, shift=UP * 0.15)),
               ("form", lambda: FadeIn(fails[0], shift=RIGHT * 0.2)),
               ("preposition", lambda: FadeIn(fails[1], shift=RIGHT * 0.2)),
               ("pattern", lambda: FadeIn(fails[2], shift=RIGHT * 0.2)), look="happy")

        self.finish("S04_attempts")

    # ==================================== 5. WHAT: WHAT HAS TO MATCH =======

    def what(self):
        self.begin("S05_what", "WHAT: What Has to Match", "What has to match")

        title = text("Substitution checklist", LABEL, BLUE, BOLD)
        g = Grid(CHECKLIST, (0.6, 2.9, 9.0), size=SMALL, row_h=0.56, header=False,
                 styles=[(MUTED, NORMAL), (INK, BOLD), (INK, NORMAL)])
        board = VGroup(title, g).arrange(DOWN, buff=0.4, aligned_edge=LEFT)
        place(board, x=-0.2, top=BOARD_TOP - 0.15)
        self.fit(board)
        ticks = VGroup(*[tick(0.22).move_to([g.get_right()[0] + 0.35, g.cell(r, 1).get_y(), 0]) for r in range(5)])
        new = text("New today: the form and the pattern", LABEL, BROWN, BOLD).move_to(DOWN * 2.5)
        back = text("The fit: connotation, register, collocation", SMALL, MUTED).move_to(DOWN * 3.1)
        self.fit(ticks, new, back)

        self.play(FadeIn(title), LaggedStart(*[AnimationGroup(FadeIn(g.row(r), shift=RIGHT * 0.2), FadeIn(ticks[r]))
                                               for r in range(5)], lag_ratio=0.45), run_time=3.5)
        self.T("s5_01", "The first two you already know from earlier sessions. Today's new rules are three and four. "
                        "Rule five ties back to types of synonyms.",
               ("first", lambda: [hl(g.cell(0, 1)), hl(g.cell(1, 1))]),
               ("three", lambda: [g.cell(2, 1).animate.set_color(BROWN), g.cell(3, 1).animate.set_color(BROWN),
                                  FadeIn(new, shift=UP * 0.15)]),
               ("five", lambda: [hl(g.cell(4, 1)), FadeIn(back, shift=UP * 0.15)]))

        self.finish("S05_what")

    # ============================ 6. HOW: PATTERNS AND COMMON TRAPS ========

    def how(self):
        self.begin("S06_how", "HOW: Patterns and Common Traps", "Patterns and traps")

        g = Grid(PATTERNS, (6.0, 5.4), row_h=0.52)
        place(g, x=0.0, top=BOARD_TOP - 0.15)
        trick = VGroup(cross(0.24), text("obey to the rules", LABEL, BAD),
                       text("the new word, with the old preposition", SMALL, MUTED)).arrange(RIGHT, buff=0.3)
        trick.move_to(DOWN * 2.6)
        self.fit(g, trick)

        head = text("Variation: the reverse trap", SMALL, MUTED, BOLD)
        vsent = para(['"The team', ("DISCUSSED", BLUE, BOLD), 'the outage in the retrospective."'])
        vopts = para([("Replace DISCUSSED:", MUTED), ("(a) talked", INK), ("(b) talked about", INK)])
        var = VGroup(head, vsent, vopts).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        place(var, x=-1.0, top=BOARD_TOP - 0.15)
        opt_a, opt_b = vopts[0][1], vopts[0][2]
        no = VGroup(cross(0.22), text('"talked the outage"', SMALL, BAD)).arrange(RIGHT, buff=0.2)
        no.next_to(vopts, RIGHT, buff=0.6)
        direct = text("discuss + object: no preposition", LABEL, BROWN, BOLD)
        place(direct, left=var.get_left()[0], y=-0.95)
        extra = Grid(EXTRA, (3.6, 2.6), row_h=0.55, header=False, styles=[(BAD, NORMAL), (GOOD, BOLD)])
        place(extra, left=var.get_left()[0], top=-1.65)
        self.fit(VGroup(var, no, direct, extra))
        strikes = [Line(extra.cell(r, 0).get_left() + LEFT * 0.06, extra.cell(r, 0).get_right() + RIGHT * 0.06,
                        color=BAD, stroke_width=3) for r in range(3)]

        def wrong(r):
            return [FadeIn(extra.row(r), shift=RIGHT * 0.2), Create(strikes[r])]

        self.T("s6_01", "Some verbs always bring a particular preposition. Others take no preposition at all. You "
                        "don't need to memorise a dictionary, but you do need to know the ones that come up often.",
               ("preposition", lambda: FadeIn(VGroup(g.col(0), g.rule), shift=UP * 0.2)),
               ("Others", lambda: FadeIn(g.col(1), shift=LEFT * 0.3)),
               ("often", lambda: hl(g.col(0, head=False), 1.03)))
        self.S("D", "s6_02", "So a common trick is to replace a word from the left column with one from the right, and "
                             "keep the old preposition.",
               ("left", lambda: hl(g.cell(1, 0), 1.06)),
               ("right", lambda: hl(g.cell(1, 1), 1.06)),
               ("old", lambda: FadeIn(trick, shift=UP * 0.15)),
               shown="A common trick: swap in a word from the right column, and keep the old preposition.",
               look="think")
        self.T("s6_03", "Exactly. That's how obey to in option C was built. There's a reverse trap as well. Look at "
                        "this one.",
               ("obey", lambda: hl(trick[1], 1.1, BAD)),
               ("reverse", self.wipe),
               ("Look", lambda: FadeIn(var, shift=UP * 0.2)), look="happy")
        self.S("B", "s6_04", "Talked about. Talked the outage doesn't work.",
               ("about", lambda: opt_b.animate.set_color(GOOD)),
               ("outage", lambda: [opt_a.animate.set_color(MUTED), FadeIn(no, shift=LEFT * 0.2)]))
        self.T("s6_05", "Right. Here the replacement needs to add a preposition that the original didn't have. Discuss "
                        "takes a direct object.",
               ("Discuss", lambda: FadeIn(direct, shift=UP * 0.15)))
        self.S("C", "s6_06", "So discuss about is wrong too? I say that all the time.",
               ("about", lambda: wrong(0)), look="oops")
        self.T("s6_07", "Very common in Indian English, and very commonly tested. Same with return back and revert "
                        "back. Return already means go back.",
               ("return", lambda: wrong(1)),
               ("revert", lambda: wrong(2)),
               ("already", lambda: hl(extra.col(1), 1.06)))

        self.finish("S06_how")

    # ====================== 7. WHY: YOUR WRITING GETS JUDGED ON THIS =======

    def why(self):
        self.begin("S07_why", "WHY: Your Writing Gets Judged on This", "Your writing is judged")

        def draft(a, b, c, color, weight):
            return para(['"Kindly', (a, color, weight), "on the below points. We need to", (b, color, weight)],
                        ["the timeline and ensure all teams", (c, color, weight), 'new process."'])

        bad = draft("revert back", "discuss about", "adhere the", INK, NORMAL)
        good = draft("revert", "discuss", "adhere to the", GOOD, BOLD)
        head_b, head_g = text("Email draft", SMALL, MUTED, BOLD), text("Edited", SMALL, MUTED, BOLD)
        board = VGroup(head_b, bad, head_g, good).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        place(board, x=0.0, top=BOARD_TOP - 0.15)
        where = text("Emails, reports and documentation: more precise", LABEL, BROWN, BOLD).move_to(DOWN * 2.9)
        self.fit(board, where)
        slips = [bad[0][1], bad[0][3], bad[1][1]]

        job = text("It does the same job", BODY).move_to(UP * 0.1)
        fits = text("And it fits the interface", BODY, BROWN, BOLD).move_to(DOWN * 0.8)

        self.play(FadeIn(head_b), FadeIn(bad, shift=UP * 0.2), run_time=0.8)
        self.countdown(3.5)                 # a moment to read the draft before anyone speaks
        self.S("A", "s7_01", "Three mistakes in two lines.",
               ("mistakes", lambda: [m.animate.set_color(BAD) for m in slips]), look="oops")
        self.T("s7_02", "An interviewer, a client, or a manager abroad notices these straight away. Substitution "
                        "questions are training you to edit your own writing. Every pattern you learn here makes your "
                        "emails, reports and documentation more precise.",
               ("notices", lambda: [hl(m, 1.1, BAD) for m in slips]),
               ("edit", lambda: [FadeIn(head_g), FadeIn(good, shift=UP * 0.2)]),
               ("emails", lambda: FadeIn(where, shift=UP * 0.15)))
        self.N("s7_03", "The same discipline applies whenever you swap one component for another in software. It isn't "
                        "enough for the replacement to do the same job. It also has to fit the interface.",
               ("discipline", self.wipe),
               ("job", lambda: FadeIn(job, shift=UP * 0.15)),
               ("interface", lambda: FadeIn(fits, shift=UP * 0.15)))

        self.finish("S07_why")

    # ============================ 8. PAYOFF: SOLVING BOTH QUESTIONS ========

    def payoff(self):
        self.begin("S08_payoff", "Payoff: Solving Both Questions", "Solving both questions")

        def checks(rows, top):
            block = column(*[phrase(*[text(s, SMALL, BROWN) for s in row], buff=0.7) for row in rows], buff=0.16)
            return fit_w(place(block, left=-EDGE_X + 0.3, top=top), 2 * EDGE_X - 0.6)

        q1 = Question("Practice question 1", Q1_LINES[:1], Q1_OPTIONS, LABEL, across=False)
        place(q1, left=-EDGE_X + 0.3, top=BOARD_TOP - 0.1)
        self.fit(q1)
        n1 = {k: q1.opts.note(k, s, c) for k, s, c in (("a", "obey + object: it works", GOOD),
                                                         ("b", "needs 'to'", BAD),
                                                         ("c", "an extra preposition", BAD),
                                                         ("d", "wrong pattern: the meaning changes", BAD))}
        c1 = checks([["Meaning: all about following rules", "Part of speech: all verbs"],
                     ["Form: the base form after 'must'", "Pattern: must take 'the security policy'"]], -2.35)
        marks1 = [*c1[0], *c1[1]]

        q2 = Question("Practice question 2", Q2_LINES[:1], Q2_OPTIONS, LABEL, across=False)
        place(q2, left=-EDGE_X + 0.3, top=BOARD_TOP - 0.1)
        self.fit(q2)
        n2 = {k: q2.opts.note(k, s, c) for k, s, c in (("a", "wrong tense", BAD),
                                                         ("b", "past tense, and 'hurried to fix' works", GOOD),
                                                         ("c", "wrong form", BAD),
                                                         ("d", "wrong pattern: quicken + pace / pulse", BAD))}
        c2 = checks([["Meaning: to act quickly", "Form: past tense, to match 'hastened'"]], -2.6)

        self.T("s8_01", "Question one. Run the checklist.", (None, lambda: FadeIn(q1, shift=UP * 0.2)))
        self.S("D", "s8_02", "Meaning: all four options are about following rules. Part of speech: all verbs. Form: "
                             "the base form after must, which they all are. Pattern: the original comply with is "
                             "replaced in full, so the new phrase has to take the security policy correctly.",
               ("Meaning", lambda: FadeIn(marks1[0], shift=UP * 0.1)),
               ("Part", lambda: FadeIn(marks1[1], shift=UP * 0.1)),
               ("Form", lambda: FadeIn(marks1[2], shift=UP * 0.1)),
               ("Pattern", lambda: [FadeIn(marks1[3], shift=UP * 0.1), hl(q1.body[0][2], 1.05)]),
               shown="Meaning, part of speech and form all match. The pattern must take 'the security policy'.",
               look="think")
        self.S("B", "s8_03", "Adhere the policy is missing to. Obey to the policy adds a preposition that obey "
                             "doesn't take. Follow with the policy changes the meaning, as if you followed up with "
                             "the policy. Only obey the security policy works. So the answer is option A.",
               ("Adhere", lambda: [*q1.opts.out("b"), FadeIn(n1["b"], shift=RIGHT * 0.2)]),
               ("Obey", lambda: [*q1.opts.out("c"), FadeIn(n1["c"], shift=RIGHT * 0.2)]),
               ("Follow", lambda: [*q1.opts.out("d"), FadeIn(n1["d"], shift=RIGHT * 0.2)]),
               ("answer", lambda: [*q1.opts.right("a"), FadeIn(n1["a"], shift=RIGHT * 0.2)]),
               shown="Only 'obey the security policy' works. So the answer is (a).", other="happy")

        self.wipe()
        self.T("s8_04", "Question two.", (None, lambda: FadeIn(q2, shift=UP * 0.2)), look="ask")
        self.S("A", "s8_05", "Meaning: to act quickly. Form: past tense, to match hastened. That rules out hurry and "
                             "hurrying. Pattern: hurried to fix works, but quickened to fix doesn't. Quicken goes with "
                             "things like pace or pulse. So the answer is option B, hurried.",
               ("Meaning", lambda: FadeIn(c2[0][0], shift=UP * 0.1)),
               ("Form", lambda: FadeIn(c2[0][1], shift=UP * 0.1)),
               ("rules", lambda: [*q2.opts.out("a", "c"), FadeIn(VGroup(n2["a"], n2["c"]), shift=RIGHT * 0.2)]),
               ("quickened", lambda: [*q2.opts.out("d"), FadeIn(n2["d"], shift=RIGHT * 0.2)]),
               ("answer", lambda: [*q2.opts.right("b"), FadeIn(n2["b"], shift=RIGHT * 0.2)]),
               shown="Past tense rules out hurry and hurrying; 'quickened to fix' is the wrong pattern. So (b).",
               other="happy")

        self.finish("S08_payoff")

    # ================================================== 9. SUMMARY =========

    def summary(self):
        self.begin("S09_summary", "Summary", "Summary")

        items = VGroup(*[VGroup(tick(0.26), text(s, BODY)).arrange(RIGHT, buff=0.35)
                         for s in ("The meaning", "The part of speech", "The form", "The pattern", "The fit")])
        items.arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        place(items, x=0.0, top=BOARD_TOP - 0.2)
        banner = text("Lesson 1: Synonyms, complete", BODY, GOOD, BOLD).move_to(DOWN * 2.85)
        self.fit(items, banner)

        self.Q("s9_01", "Close out the lesson. What does a substitute have to match?",
               shown="What does a substitute have to match?")
        self.S("A", "s9_02", "The meaning.", (None, lambda: FadeIn(items[0], shift=RIGHT * 0.2)))
        self.S("B", "s9_03", "The part of speech.", (None, lambda: FadeIn(items[1], shift=RIGHT * 0.2)))
        self.S("C", "s9_04", "The form.", (None, lambda: FadeIn(items[2], shift=RIGHT * 0.2)))
        self.S("D", "s9_05", "The pattern.", (None, lambda: FadeIn(items[3], shift=RIGHT * 0.2)))
        self.S("B", "s9_06", "And the fit.",
               (None, lambda: FadeIn(items[4], shift=RIGHT * 0.2)),
               (None, lambda: [FadeIn(banner, scale=1.1), self.react("ACD", "happy")]), look="happy", other="happy")

        self.finish("S09_summary")

    # ========================================= 10. WHAT COMES NEXT =========

    def next_session(self):
        self.begin("S10_next", "What Comes Next", "What comes next?")

        kit = text("The synonym toolkit: the routine and the checklist", BODY).move_to(UP * 0.1)
        trap = text("One trap left: the exact opposite", BODY, BAD, BOLD).move_to(DOWN * 0.8)
        pairs = Grid([["mitigate", "aggravate"], ["verbose", "concise"], ["transient", "permanent"]], (3.6, 2.8),
                     row_h=0.62, header=False, styles=[(INK, NORMAL), (BROWN, BOLD)])
        place(pairs, left=-5.6, top=BOARD_TOP - 0.3)
        arrows = VGroup(*[small_arrow().move_to([pairs.cell(0, 1).get_left()[0] - 0.95, pairs.cell(r, 0).get_y(), 0])
                          for r in range(3)])
        turn = text("Next: the opposite is the answer", LABEL, BROWN, BOLD)
        place(turn, left=-5.6, y=-1.3)
        hot = Grid([["hot", "cold ?"], ["hot", "not hot ?"]], (2.3, 2.6), size=BODY, row_h=0.8, header=False,
                   styles=[(INK, BOLD), (BLUE, BOLD)])
        place(hot, left=1.6, top=BOARD_TOP - 0.45)
        hot_arrows = VGroup(*[small_arrow(BLUE).move_to([hot.cell(0, 1).get_left()[0] - 0.9, hot.cell(r, 0).get_y(), 0])
                              for r in range(2)])
        nxt = text("Next session:  Introduction to antonyms (Lesson 2)", LABEL, BROWN, BOLD).move_to(DOWN * 2.9)
        self.fit(kit, trap, VGroup(pairs, arrows, turn, hot, hot_arrows), nxt)

        self.N("s10_01", "That completes the synonym toolkit. But there's one trap the class has met again and again "
                         "without examining it properly: the option that means the exact opposite.",
               ("toolkit", lambda: FadeIn(kit, shift=UP * 0.15)),
               ("opposite", lambda: FadeIn(trap, shift=UP * 0.15)))
        self.wipe()
        self.T("s10_02", "So far, opposites were the traps we avoided. Next time, the exam turns that around. The "
                         "opposite becomes the answer it's asking for.",
               (None, lambda: LaggedStart(*[AnimationGroup(FadeIn(pairs.row(r)), GrowArrow(arrows[r]))
                                            for r in range(3)], lag_ratio=0.4, run_time=1.8)),
               ("turns", lambda: hl(pairs.col(1), 1.06)),
               ("answer", lambda: FadeIn(turn, shift=UP * 0.15)))
        self.S("C", "s10_03", "Isn't that easier? You just find the opposite.", look="ask")
        self.Q("s10_04", "Is not hot the same as cold?",
               (None, lambda: [FadeIn(hot.row(0)), GrowArrow(hot_arrows[0])]),
               ("not", lambda: [FadeIn(hot.row(1)), GrowArrow(hot_arrows[1])]),
               shown="Is 'not hot' the same as cold?", look="smile", other="confused")
        self.T("s10_05", "Next session.", (None, lambda: FadeIn(nxt, shift=UP * 0.15)))

        self.the_end("S10_next")

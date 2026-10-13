"""
animation.py for the LMS video generator.

Course : C-CAT Preparation - Section A: English Language and Verbal Ability
Module : 1 Vocabulary   Lesson : 1 Synonyms (Session 1)
Video  : 02 - Types of Synonyms   (previous: Introduction to synonyms;  next: Context-based synonyms)
Source : C:/Final scripts/Scipts/02 - Types of synonyms.pdf

Note: the two questions are practice questions written for the class, not past-paper questions.

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
  Stage directions are not spoken: they are the visuals.

Sarvam AI voices: the ids above are voice-library ids. With the Sarvam engine each id is turned into a
  Sarvam speaker by settings.json > audio.sarvam.voices. Six different voices need this map:
    "vijay": "vijay", "aditya": "aditya", "prasad": "kabir", "kavya": "kavya", "ritu": "ritu", "student_a": "rahul"

Screen zones:
  top band   teacher (left corner), scene heading, the four students (right corner)
  strip      the question being asked or the student's line
  board      everything else (BOARD_TOP down to FLOOR)

Section map:
  S01 Slim or skinny?   S02 Words carry more than meaning   S03 How C-CAT tests this   S04 The class splits again
  S05 WHAT: the attributes   S06 HOW: matching the attributes   S07 WHY: precision   S08 Payoff
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

Q1_LINES = [["In her annual review, the manager", ("praised", INK), "Ananya for being ______"],
            ["with the project budget; she consistently spent well below the limit."]]
Q1_OPTIONS = [("a", "stingy"), ("b", "frugal"), ("c", "miserly"), ("d", "tight-fisted")]
Q2_LINES = [['"The client was', ("ANNOYED", BLUE, BOLD), 'by the repeated delay in the release."'],
            [("Choose the word closest in meaning to ANNOYED:", MUTED)]]
Q2_OPTIONS = [("a", "Furious"), ("b", "Irritated"), ("c", "Devastated"), ("d", "Indifferent")]

ATTRIBUTES = [["1.", "Connotation", "(feeling)", "slim (+)    thin (0)    skinny (-)"],
              ["2.", "Degree", "(intensity)", "annoyed  <  angry  <  furious"],
              ["3.", "Register", "(formality)", "start  /  begin  /  commence"],
              ["4.", "Collocation", "(word partners)", "heavy traffic, not strong traffic"],
              ["5.", "Region", "(dialect)", "lift (British)  /  elevator (American)"]]


def degree_bar(y, left=-4.2, right=4.2):
    """The intensity line: annoyed (mild) on the left, furious (strong) on the right."""
    third = (right - left) / 3
    line = VGroup(*[Line([left + k * third, y, 0], [left + (k + 1) * third, y, 0], color=c, stroke_width=8)
                    for k, c in enumerate((FLASH, BROWN, BAD))])
    marks = VGroup()
    for word, x, c in (("annoyed", left + 0.9, FLASH), ("angry", (left + right) / 2, BROWN),
                       ("furious", right - 0.9, BAD)):
        dot = Dot([x, y, 0], radius=0.11, color=c)
        marks.add(VGroup(dot, text(word, LABEL).next_to(dot, DOWN, buff=0.2)))
    group = VGroup(line, marks)
    group.line, group.marks = line, marks
    return group


class TypesOfSynonyms(LMSScene):
    lesson_title = "Types of Synonyms"

    def construct(self):
        self.camera.background_color = BG
        self.cast = None
        self.title_bar = None
        self.spoken = None
        self.talking = None
        self.faces = {}

        self.hook()
        self.record()
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

    # ============================================ 1. SLIM OR SKINNY? =======

    def hook(self):
        self.scene_start("S01_hook", title="Slim or Skinny?")
        card = self.opening("Types of Synonyms", "Introduction to synonyms")
        self.heading("Slim or skinny?")

        slim = text("SLIM", TITLE, BROWN, BOLD)
        skinny = text("SKINNY", TITLE, BLUE, BOLD)
        words = VGroup(slim, skinny).arrange(RIGHT, buff=3.2).move_to(UP * 0.2)
        eq = text("=", TITLE, MUTED).move_to((slim.get_right() + skinny.get_left()) / 2)
        feel_a = text("Sounds like a compliment", LABEL, BROWN).next_to(slim, DOWN, buff=0.35)
        feel_b = text("Sounds like an insult", LABEL, BLUE).next_to(skinny, DOWN, buff=0.35)
        same = text("Same meaning:  thin", BODY).move_to(DOWN * 1.9)
        self.fit(VGroup(words, eq, feel_a, feel_b, same))

        mail_head = text("Deployment notice to a client", SMALL, MUTED, BOLD)
        mail = para([("Version A", MUTED, BOLD), "The database migration will", ("kick off", BROWN, BOLD), "at 2 AM."],
                    [("Version B", MUTED, BOLD), "The database migration will", ("commence", BLUE, BOLD),
                     "at 2:00 AM."], step=1.15)
        block = VGroup(mail_head, mail).arrange(DOWN, buff=0.5, aligned_edge=LEFT).move_to(DOWN * 0.8)
        self.fit(block)
        kick, comm = mail[0][2], mail[1][2]
        tag_a = text("Casual", SMALL, BROWN).next_to(kick, DOWN, buff=0.15)
        tag_b = text("Formal", SMALL, BLUE).next_to(comm, DOWN, buff=0.15)
        what = text("?", TITLE, FLASH, BOLD).move_to(DOWN * 3.0)

        self.N("s1_01", "Last session ended on a question nobody could quite answer. If two words mean the same thing, "
                        "why does one sound like a compliment and the other like an insult?",
               ("question", lambda: [FadeOut(card), FadeIn(words, shift=UP * 0.2)]),
               ("same", lambda: [FadeIn(eq), FadeIn(same, shift=UP * 0.15)]),
               ("compliment", lambda: [hl(slim), FadeIn(feel_a, shift=UP * 0.1)]),
               ("insult", lambda: [hl(skinny), FadeIn(feel_b, shift=UP * 0.1)]))
        self.Q("s1_02", "So. Slim or skinny. Which would you put in a message to a colleague?",
               ("Slim", lambda: hl(slim)), ("skinny", lambda: hl(skinny)),
               shown="Slim or skinny: which would you put in a message to a colleague?")
        self.S("A", "s1_03", "Slim. Skinny sounds like you're criticising them.",
               ("Slim", lambda: ring(slim)),
               ("criticising", lambda: [hl(feel_b, 1.06), self.react("B", "think")]))
        self.Q("s1_04", "But both mean thin. By our definition from last time, they're synonyms. So where does the "
                        "difference come from?",
               ("thin", lambda: hl(same, 1.06)),
               ("difference", lambda: [hl(feel_a, 1.06), hl(feel_b, 1.06)]),
               shown="Both mean 'thin', so they are synonyms. Where does the difference come from?")
        self.S("B", "s1_05", "The meaning is the same. The feeling isn't.",
               ("meaning", lambda: same.animate.set_color(GOOD)),
               ("feeling", lambda: [hl(feel_a, 1.06), hl(feel_b, 1.06)]), look="think", other="smile")
        self.T("s1_06", "Let me make it more serious. You're writing a deployment notice to a client.",
               ("serious", self.wipe),
               ("deployment", lambda: FadeIn(mail_head, shift=UP * 0.15)),
               (None, lambda: LaggedStart(FadeIn(mail[0], shift=RIGHT * 0.2), FadeIn(mail[1], shift=RIGHT * 0.2),
                                          lag_ratio=0.5, run_time=1.6)))
        self.Q("s1_07", "Same meaning?")
        self.S("D", "s1_08", "Same meaning. But version A sounds like a WhatsApp message to a friend, and version B "
                             "sounds like a bank.",
               ("WhatsApp", lambda: [hl(kick), FadeIn(tag_a)]),
               ("bank", lambda: [hl(comm), FadeIn(tag_b), self.react("AC", "happy")]),
               shown="Same meaning. But A sounds like a WhatsApp message to a friend, and B sounds like a bank.")
        self.Q("s1_09", "So kick off and commence are synonyms, and so are slim and skinny. But in each pair, something "
                        "besides meaning is different. What is it?",
               ("kick", lambda: [hl(kick), hl(comm)]),
               ("besides", lambda: FadeIn(what, scale=1.3)),
               shown="In each pair, something besides meaning is different. What is it?", other="confused")

        self.finish("S01_hook")

    # ============================ 2. WORDS CARRY MORE THAN MEANING =========

    def record(self):
        self.begin("S02_record", "Words Carry More Than Meaning", "More than meaning")

        grid = Grid([["Word", "Meaning", "Connotation", "Intensity", "Formality"],
                     ["slim", "thin", "positive", "normal", "neutral"],
                     ["skinny", "thin", "negative", "normal", "informal"]], (2.0, 2.1, 2.9, 2.2, 2.3), row_h=0.7)
        place(grid, x=0.0, top=BOARD_TOP - 0.3)
        note = text("Same meaning: that makes them synonyms", LABEL, BLUE).move_to(DOWN * 1.5)
        note2 = text("Different attributes: that makes the types", LABEL, BROWN).move_to(DOWN * 2.15)
        self.fit(VGroup(grid, note, note2))

        box_a = Rectangle(width=3.8, height=2.0, stroke_color=BLUE, stroke_width=3)
        box_n = Rectangle(width=7.4, height=3.2, stroke_color=BROWN, stroke_width=3)
        boxes = VGroup(box_a, box_n).arrange(RIGHT, buff=0.9, aligned_edge=DOWN)
        place(boxes, x=0.0, top=0.45)
        title_a = text("Absolute synonyms", LABEL, BLUE, BOLD).next_to(box_a, UP, buff=0.2)
        title_n = text("Near (partial) synonyms", LABEL, BROWN, BOLD).next_to(box_n, UP, buff=0.2)
        sub_a = fit_w(text("Every column matches", SMALL), 3.4)
        rare = text("Very rare", SMALL, MUTED)
        VGroup(sub_a, rare).arrange(DOWN, buff=0.3).move_to(box_a)
        sub_n = VGroup(text("Same core meaning,", BODY), text("different attributes", BODY),
                       text("Almost every exam question", SMALL, MUTED)).arrange(DOWN, buff=0.28).move_to(box_n)
        drift = text("One word drifts and picks up a different flavour", SMALL, MUTED).next_to(boxes, DOWN, buff=0.25)
        self.fit(VGroup(boxes, title_a, title_n, drift))

        self.T("s2_01", "You all work with data, so think of a word as a record in a table.",
               ("record", lambda: FadeIn(VGroup(grid.col(0), grid.col(1), grid.rule), shift=UP * 0.2)))
        self.T("s2_02", "The meaning column is the same. That's what makes them synonyms. But a word also carries "
                        "attributes. Those attributes are what put synonyms into different types.",
               ("same", lambda: [hl(grid.col(1, head=False)), FadeIn(note, shift=UP * 0.15)]),
               ("attributes", lambda: LaggedStart(*[FadeIn(grid.col(c), shift=LEFT * 0.3) for c in (2, 3, 4)],
                                                  lag_ratio=0.4, run_time=1.6)),
               ("types", lambda: [grid.cell(1, 2).animate.set_color(BROWN), grid.cell(2, 2).animate.set_color(BLUE),
                                  FadeIn(note2, shift=UP * 0.15)]))
        self.S("C", "s2_03", "So are there synonyms where every column matches?",
               ("every", lambda: [hl(grid.row(1), 1.05), hl(grid.row(2), 1.05)]), look="ask")
        self.T("s2_04", "Good question. Those are called absolute synonyms, or complete synonyms. They can replace "
                        "each other in every sentence with no change at all.",
               ("question", self.wipe),
               ("absolute", lambda: [Create(box_a), FadeIn(title_a)]),
               ("replace", lambda: FadeIn(sub_a)), look="happy")
        self.T("s2_05", "They're very rare. Languages don't like keeping two words that do exactly the same job. "
                        "Usually one of them drifts and picks up a slightly different flavour. Almost everything "
                        "you'll meet in the exam is the other type.",
               ("rare", lambda: FadeIn(rare)),
               ("drifts", lambda: FadeIn(drift, shift=UP * 0.1)),
               ("other", lambda: [Create(box_n), FadeIn(title_n)]),
               (None, lambda: FadeIn(sub_n)))

        self.finish("S02_record")

    # ====================================== 3. HOW C-CAT TESTS THIS ========

    def exam(self):
        self.begin("S03_exam", "How C-CAT Tests This", "How C-CAT tests this")

        line1 = text("Two options, one core meaning", BODY, BLUE, BOLD).move_to(UP * 0.1)
        line2 = text("Which attribute fits the sentence?", BODY).move_to(DOWN * 0.7)
        intro = VGroup(line1, line2)

        self.q1 = Question("Practice question 1", Q1_LINES, Q1_OPTIONS, SMALL)
        self.q2 = Question("Practice question 2", Q2_LINES, Q2_OPTIONS, SMALL)
        self.both = VGroup(self.q1, self.q2).arrange(DOWN, buff=0.5, aligned_edge=LEFT)
        place(self.both, x=0.0, top=BOARD_TOP - 0.1)
        self.fit(self.both)
        q1, q2 = self.q1, self.q2
        line = under(q2.body[0][1], BLUE)

        self.N("s3_01", "The exam rarely asks you to name a type. Instead, it puts two options with the same core "
                        "meaning side by side and expects you to spot which attribute fits. Here are two practice "
                        "questions written for this class, not taken from a past paper.",
               ("options", lambda: FadeIn(line1, shift=UP * 0.15)),
               ("attribute", lambda: FadeIn(line2, shift=UP * 0.15)),
               ("practice", lambda: [FadeOut(intro), FadeIn(q1, shift=UP * 0.2)]),
               ("past", lambda: [FadeIn(q2, shift=UP * 0.2), Create(line)]))
        self.T("s3_02", "Thirty seconds. Use the method from last time.",
               ("method", lambda: [hl(q1.label), hl(q2.label)]), look="ask", other="think", think=30.0)

        self.scene_end("S03_exam")          # the two questions stay on the board for the next scene

    # ==================================== 4. THE CLASS SPLITS AGAIN ========

    def attempts(self):
        self.begin("S04_attempts", "The Class Splits Again", "The class splits")

        q1, q2 = self.q1, self.q2
        praised = q1.body[0][1]
        pick_1a = under(q1.opts.rows["a"], BLUE)
        pick_2a = under(q2.opts.rows["a"], BLUE)
        pick_2b = under(q2.opts.rows["b"], BROWN)
        warn = phrase(text("Warning", SMALL, BROWN, BOLD), text("is not", SMALL, MUTED), text("Error", SMALL, BAD, BOLD))
        warn.next_to(q2.label, RIGHT, buff=1.0)

        self.Q("s4_01", "Question one?", (None, lambda: hl(q1.label)), shown="Question 1?")
        self.S("A", "s4_02", "Honestly, all four mean doesn't spend much. I just picked stingy because it's the most "
                             "common word.",
               ("four", lambda: hl(q1.opts, 1.04)),
               ("stingy", lambda: Create(pick_1a)),
               shown="All four mean 'doesn't spend much'. I just picked stingy: it's the most common word.")
        self.S("B", "s4_03", "But the manager is praising her. Stingy sounds like a complaint.",
               ("praising", lambda: hl(praised, 1.25)),
               ("complaint", lambda: [hl(q1.opts.rows["a"]), self.react("A", "confused")]), look="think")
        self.Q("s4_04", "So does that matter, if all four options mean spends little?",
               shown="Does that matter, if all four options mean 'spends little'?")
        self.S("D", "s4_05", "It matters. Praised her for being stingy is a contradiction.",
               ("Praised", lambda: praised.animate.set_color(GOOD)),
               ("contradiction", lambda: [pick_1a.animate.set_color(BAD), self.react("A", "oops")]),
               shown="It matters. 'Praised her for being stingy' is a contradiction.")
        self.Q("s4_06", "Hold that thought. Question two?",
               ("two", lambda: hl(q2.label)), shown="Question 2?")
        self.S("C", "s4_07", "Furious. If a client is annoyed, they're angry, and furious means angry.",
               ("Furious", lambda: Create(pick_2a)))
        self.S("B", "s4_08", "I said irritated. Furious feels like too much.",
               ("irritated", lambda: Create(pick_2b)), look="think")
        self.Q("s4_09", "Too much how?")
        self.S("B", "s4_10", "Like the difference between a warning and an error.",
               ("warning", lambda: FadeIn(warn, shift=LEFT * 0.2)), other="happy")
        self.T("s4_11", "Nice. Let's turn that instinct into rules.",
               ("rules", lambda: hl(warn, 1.06)), look="happy")

        self.finish("S04_attempts")

    # ================== 5. WHAT: THE ATTRIBUTES OF NEAR SYNONYMS ===========

    def what(self):
        self.begin("S05_what", "WHAT: The Attributes That Separate Near Synonyms", "Five attributes")

        g = Grid(ATTRIBUTES, (0.6, 2.6, 3.0, 6.7), row_h=0.56, header=False,
                 styles=[(MUTED, NORMAL), (BLUE, BOLD), (MUTED, NORMAL), (INK, NORMAL)])
        place(g, x=0.0, top=BOARD_TOP - 0.15)
        self.fit(g)

        def trio(items, colors):
            return VGroup(*[VGroup(text(w, LABEL, c, BOLD), text(sub, SMALL, MUTED)).arrange(DOWN, buff=0.15)
                            for (w, sub), c in zip(items, colors)]).arrange(RIGHT, buff=1.5).move_to(DOWN * 2.55)

        con = trio((("slim", "positive"), ("thin", "neutral"), ("skinny", "negative")), (BROWN, INK, BLUE))
        bar = degree_bar(-2.3)
        reg = trio((("start", "anywhere"), ("commence", "formal notices"), ("kick off", "team chat")),
                   (BLUE, BLUE, BLUE))
        col_ok = VGroup(*[VGroup(tick(0.24), text(s, LABEL)).arrange(RIGHT, buff=0.25)
                          for s in ("heavy traffic", "strong coffee", "heavy rain")]).arrange(RIGHT, buff=1.0)
        col_ok.move_to(DOWN * 2.2)
        col_bad = VGroup(cross(0.26), text("strong traffic", LABEL, BAD)).arrange(RIGHT, buff=0.25).move_to(DOWN * 2.95)
        var = para([("British:", MUTED), ("lift", BLUE, BOLD), ("/", MUTED), ("flat", BLUE, BOLD)],
                   [("American:", MUTED), ("elevator", BROWN, BOLD), ("/", MUTED), ("apartment", BROWN, BOLD)],
                   step=0.62).move_to(DOWN * 2.5)
        self.fit(con, bar, reg, col_ok, col_bad, var)

        def row(r):
            return [hl(g.cell(r, 1)), FadeIn(g.cell(r, 3), shift=LEFT * 0.2)]

        self.T("s5_01", "There are five attributes worth checking.",
               ("five", lambda: LaggedStart(*[FadeIn(VGroup(g.cell(r, 0), g.cell(r, 1), g.cell(r, 2)), shift=RIGHT * 0.2)
                                              for r in range(5)], lag_ratio=0.25, run_time=1.8)))
        self.T("s5_02", "Connotation is the emotional charge. Positive, neutral or negative. That's slim and skinny.",
               ("Connotation", lambda: row(0)),
               ("Positive", lambda: FadeIn(con, shift=UP * 0.15)),
               ("slim", lambda: [hl(con[0], 1.06), hl(con[2], 1.06)]))
        self.T("s5_03", "Degree is how strong the word is. Annoyed, angry, furious. They all sit on the same line, "
                        "just at different points.",
               ("Degree", lambda: [FadeOut(con), *row(1)]),
               ("Annoyed", lambda: [Create(bar.line), FadeIn(bar.marks[0])]),
               ("angry", lambda: FadeIn(bar.marks[1])),
               ("furious", lambda: FadeIn(bar.marks[2])),
               ("line", lambda: hl(bar.line, 1.03)))
        self.S("C", "s5_04", "So furious is on the scale. It just isn't at the same point as annoyed.",
               ("scale", lambda: hl(bar.marks[2])),
               ("annoyed", lambda: hl(bar.marks[0])), look="think")
        self.T("s5_05", "Exactly.", look="happy")
        self.T("s5_06", "Register is how formal the word is. Start works anywhere, commence belongs in formal notices, "
                        "and kick off belongs in a team chat.",
               ("Register", lambda: [FadeOut(bar), *row(2)]),
               ("Start", lambda: FadeIn(reg[0], shift=UP * 0.15)),
               ("commence", lambda: FadeIn(reg[1], shift=UP * 0.15)),
               ("kick", lambda: FadeIn(reg[2], shift=UP * 0.15)))
        self.T("s5_07", "Collocation is about which words naturally go together. Heavy and strong are close in "
                        "meaning, but English says heavy traffic, strong coffee and heavy rain. Change the partner and "
                        "the phrase sounds wrong, even though the meaning is close.",
               ("Collocation", lambda: [FadeOut(reg), *row(3)]),
               ("traffic", lambda: FadeIn(col_ok[0], shift=UP * 0.15)),
               ("coffee", lambda: FadeIn(col_ok[1], shift=UP * 0.15)),
               ("rain", lambda: FadeIn(col_ok[2], shift=UP * 0.15)),
               ("wrong", lambda: FadeIn(col_bad, shift=UP * 0.15)))
        self.S("A", "s5_08", "Strong traffic sounds like a Google Translate bug.",
               ("bug", lambda: [hl(col_bad, 1.06), self.react("BCD", "happy")]), look="happy", other="happy")
        self.T("s5_09", "And region. Lift and elevator, flat and apartment. Same thing, but different varieties of "
                        "English.",
               ("region", lambda: [FadeOut(VGroup(col_ok, col_bad)), *row(4)]),
               ("Lift", lambda: FadeIn(VGroup(var[0][0], var[0][1], var[1][0], var[1][1]), shift=UP * 0.15)),
               ("flat", lambda: FadeIn(VGroup(var[0][2], var[0][3], var[1][2], var[1][3]), shift=UP * 0.15)))

        self.finish("S05_what")

    # ============================ 6. HOW: MATCHING THE ATTRIBUTES ==========

    def how(self):
        self.begin("S06_how", "HOW: Matching the Attributes, Not Just the Meaning", "Match the attributes")

        grid = Grid([["Word", "Meaning", "Connotation"], ["stingy", "spends less", "negative"],
                     ["frugal", "spends less", "positive / neutral"], ["miserly", "spends less", "strongly negative"],
                     ["tight-fisted", "spends less", "negative, informal"]], (2.7, 2.7, 3.8), row_h=0.56)
        place(grid, x=0.0, top=0.1)
        rule = text("Match the meaning first, then the attributes", LABEL, BLUE, BOLD).move_to(DOWN * 3.05)
        clue = para(["The manager", ("praised", GOOD, BOLD), "Ananya for being ______"])
        place(clue, y=0.95)
        clue.shift(RIGHT * (grid.cell(0, 2).get_x() - clue[0][1].get_x()))
        self.fit(VGroup(grid, rule), clue)
        arrow = Arrow(clue[0][1].get_bottom() + DOWN * 0.06, grid.cell(0, 2).get_top() + UP * 0.08, buff=0,
                      color=GOOD, stroke_width=4, tip_length=0.18)

        clue2 = para(['"The client was', ("ANNOYED", BLUE, BOLD), 'by the repeated delay in the release."'])
        place(clue2, x=0.0, y=0.9)
        bar = degree_bar(-1.0)
        keep = text("Degree: keep the same intensity", LABEL, BROWN, BOLD).move_to(DOWN * 2.2)
        self.fit(clue2, bar, keep)
        arrow2 = Arrow(clue2[0][1].get_bottom() + DOWN * 0.08, bar.marks[0][0].get_top() + UP * 0.1, buff=0,
                       color=BLUE, stroke_width=4, tip_length=0.2)

        self.T("s6_01", "So the method gets one extra layer. First match the meaning, then match the attributes the "
                        "sentence demands.",
               ("meaning", lambda: FadeIn(VGroup(grid.col(0), grid.col(1), grid.rule), shift=UP * 0.2)),
               ("attributes", lambda: FadeIn(grid.col(2), shift=LEFT * 0.3)),
               (None, lambda: FadeIn(rule, shift=UP * 0.15)))
        self.S("B", "s6_02", "So the meaning column doesn't help at all. Every row says the same thing.",
               ("meaning", lambda: hl(grid.col(1, head=False), 1.06)), look="think")
        self.T("s6_03", "Right. When the meaning column can't separate the options, the attribute columns have to. "
                        "And the sentence tells you which attribute to look at.",
               ("separate", lambda: grid.col(1, head=False).animate.set_color(MUTED)),
               ("attribute", lambda: hl(grid.col(2), 1.05)),
               ("sentence", lambda: FadeIn(clue, shift=DOWN * 0.15)))
        self.Q("s6_04", "Praised demands a positive connotation. In question two, there's no praise or criticism to "
                        "match. What does the sentence give you instead?",
               ("Praised", lambda: [GrowArrow(arrow), hl(clue[0][1])]),
               ("positive", lambda: grid.cell(2, 2).animate.set_color(GOOD)),
               ("two", lambda: [FadeOut(VGroup(grid, arrow, clue)), FadeIn(clue2, shift=UP * 0.2)]),
               shown="In question 2 there is no praise or criticism. What does the sentence give you instead?")
        self.S("D", "s6_05", "The word itself. Annoyed. So we keep the same intensity.",
               ("Annoyed", lambda: hl(clue2[0][1])),
               ("intensity", lambda: [FadeIn(bar, shift=UP * 0.2), GrowArrow(arrow2), FadeIn(keep, shift=UP * 0.15)]),
               look="think", other="happy")

        self.finish("S06_how")

    # ==================== 7. WHY: PRECISION IN PROFESSIONAL WRITING ========

    def why(self):
        self.begin("S07_why", "WHY: Precision in Professional Writing", "Why precision matters")

        head = text("Code review comment", SMALL, MUTED, BOLD)
        drafts = para([("Draft 1", MUTED, BOLD), '"This function is stupid and bloated."'],
                      [("Draft 2", MUTED, BOLD), '"This function is too long; let\'s split it."'], step=0.75)
        top = VGroup(head, drafts).arrange(DOWN, buff=0.35, aligned_edge=LEFT)
        place(top, x=-0.6, top=BOARD_TOP - 0.15)
        harsh = text("Harsh", SMALL, BAD, BOLD).next_to(drafts[0], RIGHT, buff=0.4)
        ok = tick(0.26).next_to(drafts[1], RIGHT, buff=0.35)
        jobs = VGroup(*[VGroup(Dot(radius=0.07, color=BLUE), text(s, LABEL)).arrange(RIGHT, buff=0.25)
                        for s in ("Interview answers", "Emails to recruiters", "Bug reports")])
        jobs.arrange(RIGHT, buff=0.8).move_to(DOWN * 1.55)
        skill = text("The exam checks the same skill in 30 seconds", LABEL, BROWN, BOLD).move_to(DOWN * 2.6)
        self.fit(VGroup(top, harsh, ok), jobs, skill)

        agree = text("The right answer agrees with its sentence", BODY, INK, BOLD).move_to(UP * 0.1)
        parts = phrase(text("Meaning", BODY, BLUE, BOLD), text("+", BODY, MUTED), text("Attributes", BODY, BROWN, BOLD),
                       buff=0.5).move_to(DOWN * 1.2)
        self.fit(agree, parts)

        self.Q("s7_01", "Both comments flag the same problem. Which one gets the code fixed without starting an "
                        "argument in the team?",
               (None, lambda: FadeIn(top, shift=UP * 0.2)),
               shown="Which one gets the code fixed without starting an argument?")
        self.T("s7_02", "That's connotation and register, used on the job. Your interview answers, your emails to "
                        "recruiters, your bug reports. People judge you by how precisely you choose between near "
                        "synonyms. The exam is checking the same skill in thirty seconds.",
               (None, lambda: [FadeIn(ok, scale=0.6), FadeIn(harsh), drafts[0][1].animate.set_color(MUTED),
                               self.react("ABCD", "happy")]),
               ("interview", lambda: FadeIn(jobs[0], shift=UP * 0.15)),
               ("emails", lambda: FadeIn(jobs[1], shift=UP * 0.15)),
               ("bug", lambda: FadeIn(jobs[2], shift=UP * 0.15)),
               ("exam", lambda: FadeIn(skill, shift=UP * 0.15)), look="happy")
        self.N("s7_03", "In a vocabulary question, the right answer is the word that agrees with its sentence. "
                        "Agreement means both the meaning and the attributes.",
               ("vocabulary", self.wipe),
               ("agrees", lambda: FadeIn(agree, shift=UP * 0.15)),
               ("meaning", lambda: FadeIn(parts[0], shift=UP * 0.15)),
               ("attributes", lambda: FadeIn(VGroup(parts[1], parts[2]), shift=UP * 0.15)))

        self.finish("S07_why")

    # ============================ 8. PAYOFF: SOLVING BOTH QUESTIONS ========

    def payoff(self):
        self.begin("S08_payoff", "Payoff: Solving Both Questions", "Solving both questions")

        q1 = Question("Practice question 1", Q1_LINES, Q1_OPTIONS, LABEL, across=False)
        place(q1, left=-EDGE_X + 0.3, top=BOARD_TOP - 0.1)
        self.fit(q1)
        praised = q1.body[0][1]
        n_a = q1.opts.note("a", "negative: contradicts 'praised'", BAD)
        n_b = q1.opts.note("b", "positive: it fits 'praised'", GOOD)
        n_c = q1.opts.note("c", "strongly negative", BAD)
        n_d = q1.opts.note("d", "negative, informal", BAD)
        core = text("Core meaning: spending very little (all four match)", SMALL, BLUE, BOLD)
        place(core, left=q1.get_left()[0], y=-3.1)
        self.fit(core)

        q2 = Question("Practice question 2", Q2_LINES, Q2_OPTIONS, LABEL, across=True)
        place(q2, x=0.0, top=BOARD_TOP - 0.1)
        self.fit(q2)
        y, x0, x1 = -2.1, -3.6, 5.2
        third = (x1 - x0) / 3
        line = VGroup(*[Line([x0 + k * third, y, 0], [x0 + (k + 1) * third, y, 0], color=c, stroke_width=8)
                        for k, c in enumerate((FLASH, BROWN, BAD))],
                      Line([x0, y - 0.18, 0], [x0, y + 0.18, 0], color=MUTED, stroke_width=4))
        dot_a = Dot([-2.0, y, 0], radius=0.11, color=FLASH)
        annoyed = VGroup(dot_a, text("annoyed", LABEL, BLUE, BOLD).next_to(dot_a, UP, buff=0.2))
        irritated = text("irritated", LABEL, GOOD, BOLD).next_to(dot_a, DOWN, buff=0.2)
        dot_f = Dot([4.2, y, 0], radius=0.11, color=BAD)
        furious = VGroup(dot_f, text("furious", LABEL).next_to(dot_f, UP, buff=0.2),
                         text("wrong degree", SMALL, BAD).next_to(dot_f, DOWN, buff=0.2))
        indiff = VGroup(text("indifferent", LABEL), text("opposite", SMALL, BAD)).arrange(DOWN, buff=0.2)
        indiff.move_to([-5.35, y - 0.1, 0])
        dev = phrase(text("devastated", LABEL), text("a different meaning: grief, not anger", SMALL, BAD), buff=0.4)
        dev.move_to(DOWN * 3.15)
        self.fit(VGroup(line, annoyed, irritated, furious, indiff, dev))

        self.T("s8_01", "Question one. Core meaning?", (None, lambda: FadeIn(q1, shift=UP * 0.2)), look="ask")
        self.S("A", "s8_02", "Spending very little. All four options match.",
               ("four", lambda: [FadeIn(core, shift=UP * 0.15), hl(q1.opts, 1.03)]), look="think")
        self.Q("s8_03", "Attribute the sentence demands?", shown="Which attribute does the sentence demand?")
        self.S("A", "s8_04", "Positive connotation, because she's being praised. So stingy, miserly and tight-fisted "
                             "are out. They all criticise. The answer is option B, frugal.",
               ("praised", lambda: [praised.animate.set_color(GOOD)]),
               ("stingy", lambda: [*q1.opts.out("a", "c", "d"), FadeIn(VGroup(n_a, n_c, n_d), shift=RIGHT * 0.2)]),
               ("answer", lambda: [*q1.opts.right("b"), FadeIn(n_b, shift=RIGHT * 0.2)]),
               shown="Positive connotation: she is being praised. So the answer is (b) frugal.", other="happy")

        self.wipe()
        self.T("s8_05", "Question two.", (None, lambda: FadeIn(q2, shift=UP * 0.2)), look="ask")
        self.S("C", "s8_06", "Core meaning is mild anger. Furious has the right meaning but the wrong degree. It's too "
                             "strong. Devastated is about grief, not anger. Indifferent means not caring at all, "
                             "which is nearly the opposite. So the answer is option B, irritated.",
               ("mild", lambda: [Create(line), FadeIn(annoyed)]),
               ("Furious", lambda: FadeIn(furious, shift=UP * 0.15)),
               ("Devastated", lambda: FadeIn(dev, shift=UP * 0.15)),
               ("Indifferent", lambda: FadeIn(indiff, shift=RIGHT * 0.2)),
               ("answer", lambda: [*q2.opts.right("b"), *q2.opts.out("a", "c", "d"), FadeIn(irritated, shift=UP * 0.1)]),
               shown="Mild anger. Furious is too strong. So the answer is (b) irritated.", other="happy")
        self.S("B", "s8_07", "Warning, not error.",
               (None, lambda: [hl(irritated), self.react("C", "happy")]), look="happy", other="happy")

        self.finish("S08_payoff")

    # ================================================== 9. SUMMARY =========

    def summary(self):
        self.begin("S09_summary", "Summary", "Summary")

        left = column(text("Absolute synonyms", LABEL, BLUE, BOLD), text("Match in every way", SMALL),
                      text("Very rare", SMALL, MUTED), buff=0.22)
        names = column(phrase(text("Connotation", LABEL), text("Degree", LABEL), text("Register", LABEL), buff=0.6),
                       phrase(text("Collocation", LABEL), text("Region", LABEL), buff=0.6), buff=0.25)
        right = column(text("Near (partial) synonyms", LABEL, BROWN, BOLD),
                       text("Same core meaning, but they differ in:", SMALL), names, buff=0.22)
        place(left, left=-EDGE_X + 0.3, top=BOARD_TOP - 0.15)
        place(right, left=-1.2, top=BOARD_TOP - 0.15)
        rule = text("First match the meaning, then the attribute", LABEL, BLUE, BOLD).move_to(DOWN * 1.35)
        step = column(text("Synonym method, step 5", SMALL, BROWN, BOLD),
                      fitted_text("If several options share the meaning, match the attribute the sentence demands.",
                                  11.5, LABEL, max_lines=2), buff=0.2)
        place(step, x=0.0, y=-2.55)
        self.fit(VGroup(left, right), rule, step)

        self.Q("s9_01", "So, today in one breath?")
        self.S("D", "s9_02", "Absolute synonyms match in every way, and they're rare. Near synonyms share the core "
                             "meaning but differ in connotation, degree, register, collocation or region.",
               ("Absolute", lambda: FadeIn(left, shift=UP * 0.15)),
               ("Near", lambda: FadeIn(VGroup(right[0], right[1]), shift=UP * 0.15)),
               ("connotation", lambda: LaggedStart(*[FadeIn(m, shift=UP * 0.1) for m in (*names[0], *names[1])],
                                                   lag_ratio=0.35, run_time=3.0)),
               shown="Absolute: match in every way, and rare. Near: same core meaning, different attributes.")
        self.S("B", "s9_03", "And in the exam, first match the meaning, then match whatever attribute the sentence "
                             "demands.",
               ("meaning", lambda: FadeIn(rule, shift=UP * 0.15)),
               ("attribute", lambda: FadeIn(step, shift=UP * 0.15)), other="happy")

        self.finish("S09_summary")

    # ========================================= 10. WHAT COMES NEXT =========

    def next_session(self):
        self.begin("S10_next", "What Comes Next", "What comes next?")

        one = text("So far: one word, one clear meaning", BODY).move_to(UP * 0.1)
        real = text("Real sentences are not always that kind", BODY, BROWN).move_to(DOWN * 0.8)
        tree = fan("EXECUTE", ("execute the script", "execute the strategy", "execute the prisoner"))
        subs = VGroup(*[text(s, SMALL, c, BOLD).next_to(leaf, DOWN, buff=0.2)
                        for s, c, leaf in zip(("run", "carry out", "put to death"), (BLUE, BLUE, MUTED), tree.leaves)])
        mark = text("?", TITLE, FLASH, BOLD).next_to(tree.word, RIGHT, buff=0.4)
        nxt = text("Next session:  Context-based synonyms", LABEL, BROWN, BOLD).move_to(DOWN * 2.9)
        self.fit(VGroup(tree, subs, mark), nxt)

        self.N("s10_01", "So far, every question has handed the class a word with one clear meaning. Real sentences "
                         "aren't always that kind.",
               ("meaning", lambda: FadeIn(one, shift=UP * 0.15)),
               ("Real", lambda: FadeIn(real, shift=UP * 0.15)))
        self.wipe()
        self.Q("s10_02", "Quick one. What's the synonym of execute?",
               ("execute", lambda: FadeIn(tree.word, scale=1.15)),
               shown="Quick one. What is the synonym of 'execute'?")
        self.S("A", "s10_03", "Run. You execute a program, you run a program.",
               ("Run", lambda: [GrowArrow(tree.arrows[0]), FadeIn(tree.leaves[0]), FadeIn(subs[0])]))
        self.S("C", "s10_04", "Or carry out. You execute a plan.",
               ("carry", lambda: [GrowArrow(tree.arrows[1]), FadeIn(tree.leaves[1]), FadeIn(subs[1])]), look="think")
        self.S("D", "s10_05", "Or something much darker, in a history book.",
               ("darker", lambda: [GrowArrow(tree.arrows[2]), FadeIn(tree.leaves[2]), FadeIn(subs[2])]), look="think")
        self.Q("s10_06", "One word, three different correct answers. So which one does the exam want?",
               ("three", lambda: [hl(m, 1.06) for m in tree.leaves]),
               ("which", lambda: FadeIn(mark, scale=1.3)), other="confused")
        self.T("s10_07", "That depends entirely on the sentence around it. Next session.",
               ("sentence", lambda: [hl(m, 1.06) for m in tree.leaves]),
               ("Next", lambda: FadeIn(nxt, shift=UP * 0.15)))

        self.the_end("S10_next")

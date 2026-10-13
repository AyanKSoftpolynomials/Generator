"""
animation.py for the LMS video generator.

Course : C-CAT Preparation - Section A: English Language and Verbal Ability
Module : 1 Vocabulary   Lesson : 1 Synonyms (Session 1)
Video  : 03 - Context-Based Synonyms   (previous: Types of synonyms;  next: Commonly confused synonyms)
Source : C:/Final scripts/Scipts/03 - Context-based synonyms.pdf

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
  "Several students answer together" (Review. Discuss. Consider.) is spoken as three one-word lines.

Sarvam AI voices: the ids above are voice-library ids. With the Sarvam engine each id is turned into a
  Sarvam speaker by settings.json > audio.sarvam.voices. Six different voices need this map:
    "vijay": "vijay", "aditya": "aditya", "prasad": "kabir", "kavya": "kavya", "ritu": "ritu", "student_a": "rahul"

Screen zones:
  top band   teacher (left corner), scene heading, the four students (right corner)
  strip      the question being asked or the student's line
  board      everything else (BOARD_TOP down to FLOOR)

Section map:
  S01 One word, three answers   S02 You already do this in code   S03 How C-CAT tests it
  S04 The first-meaning trap   S05 WHAT: words with several senses   S06 HOW: find the arguments
  S07 WHY: machines struggle too   S08 Payoff   S09 Summary   S10 What comes next
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

OVERLOADS = """
void execute(Script s)    { /* runs the script    */ }
void execute(Contract c)  { /* signs the contract */ }
void execute(Strategy p)  { /* carries out a plan */ }

Script nightlyBackup;
execute(nightlyBackup);   // which version is called?
"""
L_SCRIPT, L_CONTRACT, L_STRATEGY, L_DECL, L_CALL = range(5)

Q1_LINES = [['"The QA team will', ("EXECUTE", BLUE, BOLD), 'the full regression suite tonight."'],
            [("The word closest in meaning to EXECUTE in this sentence is:", MUTED)]]
Q1_OPTIONS = [("a", "put to death"), ("b", "run"), ("c", "sign formally"), ("d", "perform artistically")]
Q2_LINES = [['"The steering committee will', ("ENTERTAIN", BLUE, BOLD), "the vendor's proposal"],
            ['at next week\'s meeting."'],
            [("The word closest in meaning to ENTERTAIN in this sentence is:", MUTED)]]
Q2_OPTIONS = [("a", "amuse"), ("b", "host"), ("c", "consider"), ("d", "reject")]

SENSES = [["Sense 1", "amuse", '"The band entertained the audience."'],
          ["Sense 2", "host, receive", '"They entertained clients at dinner."'],
          ["Sense 3", "consider", '"We will entertain the proposal."']]
ISSUE = [["issue", "give out", '"The library will issue a card."'],
         ["issue", "problem", '"There is an issue in production."'],
         ["issue", "edition", '"The magazine\'s latest issue."']]
SENSE_W = (1.7, 2.7, 6.6)
SENSE_STYLE = [(MUTED, NORMAL), (BLUE, BOLD), (INK, NORMAL)]


class ContextBasedSynonyms(LMSScene):
    lesson_title = "Context-Based Synonyms"

    def construct(self):
        self.camera.background_color = BG
        self.cast = None
        self.title_bar = None
        self.spoken = None
        self.talking = None
        self.faces = {}

        self.hook()
        self.in_code()
        self.exam()
        self.trap()
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

    # ===================================== 1. ONE WORD, THREE ANSWERS ======

    def hook(self):
        self.scene_start("S01_hook", title="One Word, Three Answers")
        card = self.opening("Context-Based Synonyms", "Types of synonyms")
        self.heading("Which synonym?")

        tree = fan("EXECUTE", ("execute the script", "execute the strategy", "execute the prisoner"))
        subs = VGroup(*[text(s, SMALL, BLUE, BOLD).next_to(leaf, DOWN, buff=0.2)
                        for s, leaf in zip(("run", "carry out", "put to death"), tree.leaves)])
        mark = text("?", TITLE, FLASH, BOLD).next_to(tree.word, RIGHT, buff=0.4)
        last = text("Last time: same meaning, different attributes", LABEL, MUTED).move_to(DOWN * 2.4)
        today = text("Today: the core meaning itself changes", LABEL, BROWN, BOLD).move_to(DOWN * 3.0)
        law = phrase(text("A lawyer:", LABEL, MUTED), text("execute the contract", LABEL),
                     text("=  sign", LABEL, BLUE, BOLD), buff=0.3).move_to(DOWN * 2.7)
        self.fit(VGroup(tree, subs, mark), last, today, law)

        big = text("The sentence chooses the meaning", BODY, INK, BOLD).move_to(UP * 0.5)
        flow = phrase(text("Sentence", BODY), small_arrow(), text("Active meaning", BODY), small_arrow(),
                      text("Synonym", BODY, BLUE, BOLD), buff=0.35).move_to(DOWN * 0.8)
        term = text("Context-based synonyms", BODY, BLUE, BOLD).move_to(DOWN * 2.3)
        self.fit(big, flow, term)

        self.N("s1_01", "The class ended last time with one word and three different correct synonyms. Today they "
                        "find out which one the examiner wants.",
               ("word", lambda: [FadeOut(card), FadeIn(tree.word, scale=1.15)]),
               ("three", lambda: LaggedStart(*[AnimationGroup(GrowArrow(a), FadeIn(m))
                                               for a, m in zip(tree.arrows, tree.leaves)], lag_ratio=0.4,
                                             run_time=1.8)),
               ("examiner", lambda: FadeIn(mark, scale=1.3)))
        self.Q("s1_02", "Last time we matched attributes: connotation, degree, register. Today the problem is bigger. "
                        "Here the core meaning itself changes. So which synonym of execute is correct?",
               ("attributes", lambda: FadeIn(last, shift=UP * 0.15)),
               ("meaning", lambda: FadeIn(today, shift=UP * 0.15)),
               ("execute", lambda: hl(tree.word)),
               shown="Which synonym of 'execute' is correct?")
        self.S("A", "s1_03", "Run. That's the most common one.",
               ("Run", lambda: [FadeIn(subs[0]), hl(tree.leaves[0], 1.06)]))
        self.Q("s1_04", "Most common for whom?")
        self.S("A", "s1_05", "For us, I guess. We write code all day.",
               ("code", lambda: hl(tree.leaves[0], 1.06)), look="think")
        self.S("D", "s1_06", "A lawyer would say sign. You execute a contract.",
               ("sign", lambda: [FadeOut(VGroup(last, today)), FadeIn(law, shift=UP * 0.15)]))
        self.S("B", "s1_07", "So the word doesn't have one synonym. It has a different synonym for each sentence.",
               ("different", lambda: [FadeIn(subs[1]), FadeIn(subs[2])]), look="think", other="happy")
        self.T("s1_08", "That's it. When a word has several meanings, the sentence around it decides which meaning is "
                        "active, and that decides the synonym. Choosing a synonym this way is what we call "
                        "context-based synonyms.",
               ("several", self.wipe),
               ("sentence", lambda: FadeIn(big, shift=UP * 0.15)),
               ("active", lambda: LaggedStart(*[FadeIn(m, shift=RIGHT * 0.15) for m in flow], lag_ratio=0.3,
                                              run_time=2.0)),
               ("call", lambda: FadeIn(term, shift=UP * 0.15)), look="happy")

        self.finish("S01_hook")

    # ================================ 2. YOU ALREADY DO THIS IN CODE =======

    def in_code(self):
        self.begin("S02_code", "You Already Do This in Code", "You do this in code")

        lst = Listing(OVERLOADS)
        place(lst, x=0.4, top=BOARD_TOP - 0.2)
        self.fit(lst)
        call, first = lst.lines[L_CALL], lst.lines[L_SCRIPT]
        x = lst.get_left()[0] - 0.25
        arc = CurvedArrow(np.array([x, call.get_y(), 0.0]), np.array([x, first.get_y(), 0.0]), angle=-PI / 2,
                          color=GOOD, stroke_width=4, tip_length=0.2)
        over = text("Function overloading", LABEL, BLUE, BOLD).move_to(DOWN * 1.65)
        mapping = Grid([["The word", "=", "the function name"], ["The words around it", "=", "the arguments"]],
                       (4.0, 0.8, 4.2), row_h=0.58, header=False,
                       styles=[(INK, NORMAL), (MUTED, NORMAL), (BROWN, BOLD)])
        place(mapping, x=0.0, top=-2.2)
        self.fit(over, mapping)

        self.Q("s2_01", "Programmers, you've seen this before. One function name with three versions. How does the "
                        "compiler know which one to call?",
               ("seen", lambda: LaggedStart(*[FadeIn(lst.lines[k], shift=RIGHT * 0.1) for k in (0, 1, 2)],
                                            lag_ratio=0.3, run_time=1.8)),
               ("compiler", lambda: [FadeIn(lst.lines[L_DECL]), FadeIn(call)]),
               ("call", lambda: lst.focus(L_CALL)),
               shown="How does the compiler know which version to call?")
        self.S("C", "s2_02", "From the argument type. It's function overloading.",
               ("argument", lambda: lst.focus(L_DECL)),
               ("overloading", lambda: [Create(arc), first.animate.set_color(GOOD), FadeIn(over, shift=UP * 0.15)]))
        self.T("s2_03", "English works exactly the same way. The word is the function name. The words around it are "
                        "the arguments. The words around it decide which meaning gets called.",
               ("word", lambda: FadeIn(mapping.row(0), shift=UP * 0.15)),
               ("around", lambda: FadeIn(mapping.row(1), shift=UP * 0.15)),
               ("decide", lambda: [hl(mapping.cell(1, 2), 1.06), self.react("ABCD", "happy")]), look="happy")

        self.finish("S02_code")

    # ======================================== 3. HOW C-CAT TESTS IT ========

    def exam(self):
        self.begin("S03_exam", "How C-CAT Tests It", "How C-CAT tests it")

        line1 = text("Every option is a real synonym of the word", BODY, BLUE, BOLD).move_to(UP * 0.1)
        line2 = text("The trap: the dictionary's first meaning", BODY, BAD).move_to(DOWN * 0.7)
        intro = VGroup(line1, line2)
        self.fit(line1, line2)

        self.q1 = Question("Practice question 1", Q1_LINES, Q1_OPTIONS, SMALL)
        self.q2 = Question("Practice question 2", Q2_LINES, Q2_OPTIONS, SMALL)
        self.both = VGroup(self.q1, self.q2).arrange(DOWN, buff=0.4, aligned_edge=LEFT)
        place(self.both, x=0.0, top=BOARD_TOP - 0.1)
        self.fit(self.both)
        q1, q2 = self.q1, self.q2

        self.N("s3_01", "In this kind of question, every option is usually a genuine synonym of the word, just in a "
                        "different context. If you pick the dictionary's first meaning, you fall straight into the "
                        "trap. Two practice questions, written for this class.",
               ("genuine", lambda: FadeIn(line1, shift=UP * 0.15)),
               ("first", lambda: FadeIn(line2, shift=UP * 0.15)),
               ("practice", lambda: [FadeOut(intro), FadeIn(q1, shift=UP * 0.2)]),
               ("class", lambda: FadeIn(q2, shift=UP * 0.2)))
        self.T("s3_02", "Forty-five seconds for both.",
               ("both", lambda: [hl(q1.label), hl(q2.label)]), look="ask", other="think", think=45.0)

        self.scene_end("S03_exam")          # the two questions stay on the board for the next scene

    # ===================================== 4. THE FIRST-MEANING TRAP =======

    def trap(self):
        self.begin("S04_trap", "The First-Meaning Trap", "The first-meaning trap")

        q1, q2 = self.q1, self.q2
        pick_1b = under(q1.opts.rows["b"], GOOD)
        hands = text("Almost every hand goes up", SMALL, MUTED).next_to(q1.label, RIGHT, buff=0.8)
        domain = text("Software testing", SMALL, BROWN, BOLD).next_to(q1.label, RIGHT, buff=0.8)
        pick_2a = under(q2.opts.rows["a"], BLUE)
        pick_2b = under(q2.opts.rows["b"], BLUE)
        pick_2c = under(q2.opts.rows["c"], BROWN)
        bad = phrase(cross(0.24), text("amuse the proposal", SMALL, BAD), cross(0.24),
                     text("host the proposal", SMALL, BAD), buff=0.25).next_to(q2.label, RIGHT, buff=0.8)
        self.fit(hands, domain, bad)

        self.Q("s4_01", "Question one is fairly safe, I think. Show of hands for run.",
               ("run", lambda: [Create(pick_1b), FadeIn(hands), self.react("ABCD", "happy")]),
               shown="Question 1 is fairly safe. Show of hands for 'run'.", other="smile")
        self.Q("s4_02", "What gave it away?")
        self.S("B", "s4_03", "QA team and regression suite. That's testing, so it's software.",
               ("QA", lambda: hl(q1.body[0][0], 1.06)),
               ("regression", lambda: hl(q1.body[0][2], 1.06)),
               ("software", lambda: [FadeOut(hands), FadeIn(domain)]))
        self.Q("s4_04", "Good. Question two?", ("two", lambda: hl(q2.label)), shown="Question 2?")
        self.S("A", "s4_05", "Amuse. Entertain means entertain, like a show.",
               ("Amuse", lambda: Create(pick_2a)))
        self.S("C", "s4_06", "I thought host. You entertain guests.",
               ("host", lambda: Create(pick_2b)), look="think")
        self.S("D", "s4_07", "But a committee doesn't amuse a proposal. And it doesn't host one either.",
               ("amuse", lambda: [pick_2a.animate.set_color(BAD), FadeIn(VGroup(bad[0], bad[1])),
                                  self.react("A", "oops")]),
               ("host", lambda: [pick_2b.animate.set_color(BAD), FadeIn(VGroup(bad[2], bad[3])),
                                 self.react("C", "oops")]), look="think")
        self.Q("s4_08", "So what does a committee actually do with a proposal?")
        self.S("B", "s4_09", "It thinks about it. It considers it.",
               ("considers", lambda: Create(pick_2c)), look="think")
        self.T("s4_10", "Interesting. Let's make sure that isn't just a lucky guess.",
               ("lucky", lambda: ring(q2.opts.rows["c"])), look="ask")

        self.finish("S04_trap")

    # ========================== 5. WHAT: WORDS WITH SEVERAL SENSES =========

    def what(self):
        self.begin("S05_what", "WHAT: Words With Several Senses", "Words with many senses")

        g = Grid(SENSES, SENSE_W, row_h=0.62, header=False, styles=SENSE_STYLE)
        place(g, x=0.5, top=0.42)
        x0 = g.get_left()[0] - 0.4
        word = text("ENTERTAIN", BODY, BLUE, BOLD)
        place(word, left=x0 - 0.15, top=BOARD_TOP - 0.15)
        ys = [g.cell(r, 0).get_y() for r in range(3)]
        trunk = VGroup(Line([x0, word.get_bottom()[1] - 0.1, 0], [x0, ys[-1], 0], color=MUTED, stroke_width=3),
                       *[Line([x0, y, 0], [x0 + 0.28, y, 0], color=MUTED, stroke_width=3) for y in ys])
        poly = column(phrase(text("Polysemous:", LABEL, BROWN, BOLD), text("a word with several related senses", LABEL)),
                      phrase(text("poly = many", LABEL), text("sem = meaning", LABEL), buff=0.9), buff=0.3)
        place(poly, x=0.0, top=-1.6)
        commons = VGroup(*[text(s, LABEL, MUTED) for s in ("run", "hold", "address", "charge", "issue")])
        commons.arrange(RIGHT, buff=0.8).move_to(DOWN * 3.05)
        issue = Grid(ISSUE, SENSE_W, row_h=0.56, header=False, styles=SENSE_STYLE)
        place(issue, x=0.5, top=-1.75)
        self.fit(VGroup(g, word, trunk), poly, commons, issue)

        self.play(FadeIn(word, shift=DOWN * 0.15), Create(trunk), run_time=0.8)
        self.play(LaggedStart(*[FadeIn(g.row(r), shift=RIGHT * 0.2) for r in range(3)], lag_ratio=0.4), run_time=1.6)
        self.T("s5_01", "A word with several related senses is called polysemous. Poly means many and sem means "
                        "meaning. Most common English words are like this: run, hold, address, charge, issue.",
               ("several", lambda: [hl(g.col(1), 1.05)]),
               ("polysemous", lambda: FadeIn(poly[0], shift=UP * 0.15)),
               ("Poly", lambda: FadeIn(poly[1], shift=UP * 0.15)),
               ("run", lambda: LaggedStart(*[FadeIn(m, shift=UP * 0.1) for m in commons], lag_ratio=0.5,
                                           run_time=3.0)))
        self.S("C", "s5_02", "Issue too?",
               (None, lambda: hl(commons[4], 1.3)), look="surprised")
        self.T("s5_03", "Think about it. The library will issue a card. There is an issue in production. The "
                        "magazine's latest issue.",
               ("Think", lambda: FadeOut(VGroup(poly, commons))),
               ("library", lambda: FadeIn(issue.row(0), shift=RIGHT * 0.2)),
               ("production", lambda: FadeIn(issue.row(1), shift=RIGHT * 0.2)),
               ("latest", lambda: FadeIn(issue.row(2), shift=RIGHT * 0.2)))
        self.S("A", "s5_04", "So a production issue and the latest issue are two completely different things.",
               ("production", lambda: hl(issue.cell(1, 1))),
               ("latest", lambda: hl(issue.cell(2, 1))), look="happy", other="happy")

        self.finish("S05_what")

    # ======================================= 6. HOW: FIND THE ARGUMENTS ====

    def how(self):
        self.begin("S06_how", "HOW: Find the Arguments", "Find the arguments")

        sent = para(['"The', ("steering committee", INK), "will", ("ENTERTAIN", BLUE, BOLD)],
                    [("the vendor's proposal", INK), 'at next week\'s meeting."'])
        place(sent, left=-EDGE_X + 0.3, top=BOARD_TOP - 0.15)
        subject, word, obj = sent[0][1], sent[0][3], sent[1][0]
        blank = Line(word.get_corner(DL), word.get_corner(DR), color=BLUE, stroke_width=4)
        pred = para([("review", INK), ("/", MUTED), ("discuss", INK), ("/", MUTED), ("consider", INK)], size=SMALL)
        place(pred, left=word.get_right()[0] + 0.6, y=word.get_y())
        opts = Options(Q2_OPTIONS, SMALL, across=True)
        place(opts, left=sent.get_left()[0], top=sent.get_bottom()[1] - 0.35)

        title = text("Context check", LABEL, BLUE, BOLD)
        g = Grid([["1.  Who or what is the subject?", "the steering committee"],
                  ["2.  What is the object?", "the vendor's proposal"],
                  ["3.  What is the domain?", "meetings, decisions"]], (5.3, 4.4), size=SMALL, row_h=0.42,
                 header=False, styles=[(INK, NORMAL), (BROWN, BOLD)])
        step4 = text("4.  Cover the word and fill the blank with your own word", SMALL)
        step5 = text("5.  Match your word to the options", SMALL)
        check = VGroup(title, g, step4, step5).arrange(DOWN, buff=0.17, aligned_edge=LEFT)
        place(check, left=sent.get_left()[0], top=opts.get_bottom()[1] - 0.4)
        self.fit(VGroup(sent, blank, pred, opts, check))

        self.T("s6_01", "So how do you find the active sense quickly? Look for the arguments, the words the target "
                        "word is attached to.",
               ("active", lambda: FadeIn(sent, shift=UP * 0.2)),
               ("arguments", lambda: LaggedStart(FadeIn(title), *[FadeIn(m, shift=RIGHT * 0.15) for m in
                                                                  (g.cell(0, 0), g.cell(1, 0), g.cell(2, 0), step4,
                                                                   step5)], lag_ratio=0.25, run_time=2.4)),
               look="ask")
        self.Q("s6_02", "Cover the word. The steering committee will blank the vendor's proposal at next week's "
                        "meeting. What would you naturally write there?",
               ("Cover", lambda: [FadeOut(word), Create(blank), hl(step4, 1.04)]),
               ("committee", lambda: [subject.animate.set_color(BROWN), FadeIn(g.cell(0, 1), shift=LEFT * 0.2)]),
               ("proposal", lambda: [obj.animate.set_color(BROWN), FadeIn(g.cell(1, 1), shift=LEFT * 0.2)]),
               ("meeting", lambda: FadeIn(g.cell(2, 1), shift=LEFT * 0.2)),
               shown="Cover the word. What would you naturally write there?")
        self.S("A", "s6_03", "Review.", (None, lambda: FadeIn(pred[0][0], shift=UP * 0.1)))
        self.S("C", "s6_04", "Discuss.", (None, lambda: FadeIn(VGroup(pred[0][1], pred[0][2]), shift=UP * 0.1)))
        self.S("B", "s6_05", "Consider.", (None, lambda: FadeIn(VGroup(pred[0][3], pred[0][4]), shift=UP * 0.1)))
        self.Q("s6_06", "Now look at the options. Which one is in your list?",
               ("options", lambda: FadeIn(opts, shift=UP * 0.15)),
               ("list", lambda: [hl(opts.rows["c"]), hl(pred[0][4])]))
        self.T("s6_07", "Notice the order. You predict first, and only then look at the options. If you read the "
                        "options first, the dictionary's first meaning gets planted in your head before you've "
                        "understood the sentence.",
               ("predict", lambda: hl(step4, 1.04)),
               ("options", lambda: hl(step5, 1.04)),
               ("planted", lambda: hl(opts.rows["a"], 1.15, BAD)))
        self.S("D", "s6_08", "That's exactly what happened with amuse.",
               ("amuse", lambda: [hl(opts.rows["a"], 1.15, BAD), self.react("A", "oops")]), look="think")
        self.N("s6_09", "Step four is the key. Covering the word forces you to read the sentence, not just the word.",
               ("four", lambda: step4.animate.set_color(BLUE)),
               ("Covering", lambda: hl(blank, 1.2)),
               ("sentence", lambda: [hl(subject, 1.06), hl(obj, 1.06)]))

        self.finish("S06_how")

    # ============================== 7. WHY: MACHINES STRUGGLE TOO ==========

    def why(self):
        self.begin("S07_why", "WHY: Machines Struggle With This Too", "Machines struggle too")

        box = RoundedRectangle(width=6.0, height=0.7, corner_radius=0.35, stroke_color=MUTED, stroke_width=3)
        box.move_to(UP * 0.8)
        query = code("python issue", LABEL).move_to(box)
        snake = column(text("Snake care", LABEL, BROWN, BOLD), text("Feeding a pet python", SMALL),
                       text("Common python health issues", SMALL), buff=0.18)
        bugs = column(text("Programming", LABEL, BLUE, BOLD), text("Python issue tracker", SMALL),
                      text("Bug report: crash on start", SMALL), buff=0.18)
        place(snake, left=-5.6, top=0.1)
        place(bugs, left=1.0, top=0.1)
        what = text("Which sense does the word have here?", LABEL).move_to(DOWN * 1.9)
        term = text("Word-sense disambiguation", BODY, BLUE, BOLD).move_to(DOWN * 2.5)
        byhand = text("Reading comprehension: the same job, done by hand", LABEL, BROWN, BOLD).move_to(DOWN * 3.15)
        self.fit(VGroup(box, query, snake, bugs), what, term, byhand)

        self.T("s7_01", "Search engines and language models face the same problem. Deciding which sense a word has "
                        "from its context is a whole research area in language processing, called word-sense "
                        "disambiguation.",
               (None, lambda: [Create(box), FadeIn(query)]),
               ("problem", lambda: [FadeIn(snake, shift=UP * 0.15), FadeIn(bugs, shift=UP * 0.15)]),
               ("sense", lambda: FadeIn(what, shift=UP * 0.15)),
               ("called", lambda: FadeIn(term, shift=UP * 0.15)))
        self.S("B", "s7_02", "So reading comprehension in the exam is really doing that same job by hand.",
               ("hand", lambda: FadeIn(byhand, shift=UP * 0.15)), look="think", other="happy")
        self.T("s7_03", "Exactly. And this isn't only about synonym questions. Vocabulary in context appears in "
                        "reading comprehension too. Get this habit right now and it pays off three modules later.",
               ("comprehension", lambda: hl(byhand, 1.04)),
               ("pays", lambda: self.react("ABCD", "happy")), look="happy")

        self.finish("S07_why")

    # ============================ 8. PAYOFF: SOLVING BOTH QUESTIONS ========

    def payoff(self):
        self.begin("S08_payoff", "Payoff: Solving Both Questions", "Solving both questions")

        def clues(*items):
            row = fit_w(phrase(*[text(s, SMALL, BROWN) for s in items], buff=0.6), 2 * EDGE_X - 0.6)
            return place(row, left=-EDGE_X + 0.3, y=-3.1)

        q1 = Question("Practice question 1", Q1_LINES, Q1_OPTIONS, LABEL, across=False)
        place(q1, left=-EDGE_X + 0.3, top=BOARD_TOP - 0.1)
        self.fit(q1)
        n1 = {k: q1.opts.note(k, s, c) for k, s, c in (("a", 'fits "execute the prisoner"', MUTED),
                                                         ("b", "software testing: run the suite", GOOD),
                                                         ("c", 'fits "execute the contract"', MUTED),
                                                         ("d", 'fits "execute the pirouette"', MUTED))}
        ctx1 = clues("Subject: the QA team", "Object: the regression suite", "Domain: software testing")

        q2 = Question("Practice question 2", Q2_LINES[:2], Q2_OPTIONS, LABEL, across=False)
        place(q2, left=-EDGE_X + 0.3, top=BOARD_TOP - 0.1)
        self.fit(q2)
        n2 = {k: q2.opts.note(k, s, c) for k, s, c in (("a", "another sense of entertain", MUTED),
                                                         ("b", "another sense of entertain", MUTED),
                                                         ("c", "what a committee does with a proposal", GOOD),
                                                         ("d", "a possible result, not the meaning", BAD))}
        ctx2 = clues("Subject: the committee", "Object: the proposal", "Domain: decision-making")

        self.T("s8_01", "Question one, properly.", (None, lambda: FadeIn(q1, shift=UP * 0.2)))
        self.S("A", "s8_02", "Subject: the QA team. Object: the regression suite. Domain: software testing. With the "
                             "word covered, I'd write run. So option B.",
               ("Subject", lambda: FadeIn(ctx1[0], shift=UP * 0.1)),
               ("Object", lambda: FadeIn(ctx1[1], shift=UP * 0.1)),
               ("Domain", lambda: FadeIn(ctx1[2], shift=UP * 0.1)),
               ("covered", lambda: hl(q1.body[0][1])),
               ("option", lambda: [*q1.opts.right("b"), FadeIn(n1["b"], shift=RIGHT * 0.2)]),
               shown="Subject: QA team. Object: regression suite. Domain: software testing. So (b) run.",
               look="think", other="happy")
        self.Q("s8_03", "And why are the others there?")
        self.S("A", "s8_04", "They're all real meanings of execute. Put to death, sign a legal document, perform a "
                             "dance step. They're correct in some other sentence, just not this one.",
               ("Put", lambda: [*q1.opts.out("a"), FadeIn(n1["a"], shift=RIGHT * 0.2)]),
               ("sign", lambda: [*q1.opts.out("c"), FadeIn(n1["c"], shift=RIGHT * 0.2)]),
               ("perform", lambda: [*q1.opts.out("d"), FadeIn(n1["d"], shift=RIGHT * 0.2)]),
               shown="They are all real meanings of 'execute': correct in some other sentence, not this one.")

        self.wipe()
        self.T("s8_05", "Question two.", (None, lambda: FadeIn(q2, shift=UP * 0.2)), look="ask")
        self.S("C", "s8_06", "Subject: committee. Object: proposal. Domain: decision-making. Covered word: review, "
                             "consider. So option C, consider. Amuse and host are other senses of entertain, and "
                             "reject is a possible outcome of considering it, not the meaning of the word.",
               ("Subject", lambda: FadeIn(ctx2[0], shift=UP * 0.1)),
               ("Object", lambda: FadeIn(ctx2[1], shift=UP * 0.1)),
               ("Domain", lambda: FadeIn(ctx2[2], shift=UP * 0.1)),
               ("option", lambda: [*q2.opts.right("c"), FadeIn(n2["c"], shift=RIGHT * 0.2)]),
               ("Amuse", lambda: [*q2.opts.out("a", "b"), FadeIn(VGroup(n2["a"], n2["b"]), shift=RIGHT * 0.2)]),
               ("reject", lambda: [*q2.opts.out("d"), FadeIn(n2["d"], shift=RIGHT * 0.2)]),
               shown="Subject: committee. Object: proposal. Domain: decision-making. So (c) consider.",
               look="think", other="happy")
        self.T("s8_07", "Nice catch on reject. The exam loves options that are logically possible but semantically "
                        "wrong.",
               ("reject", lambda: hl(n2["d"], 1.06)), look="happy")

        self.finish("S08_payoff")

    # ================================================== 9. SUMMARY =========

    def summary(self):
        self.begin("S09_summary", "Summary", "Summary")

        word = phrase(text("ENTERTAIN", LABEL, BLUE, BOLD), text("amuse  /  host  /  consider", LABEL, MUTED), buff=0.5)
        points = bullets(["Many words have several senses, and the sentence picks one",
                          "Cover the word, predict your own, then match"], buff=0.35)
        step = column(text("Synonym method, step 6", SMALL, BROWN, BOLD),
                      text("Polysemous word? Cover it, predict from the context, then match.", LABEL), buff=0.2)
        board = column(word, points, step, buff=0.6)
        place(board, x=0.0, top=BOARD_TOP - 0.2)
        self.fit(board)

        self.Q("s9_01", "One line each. What did we learn?", (None, lambda: FadeIn(word, shift=UP * 0.15)))
        self.S("B", "s9_02", "Many words have several senses, and the sentence picks one.",
               ("senses", lambda: FadeIn(points[0], shift=RIGHT * 0.2)))
        self.S("D", "s9_03", "Cover the word, predict your own, then match.",
               ("Cover", lambda: FadeIn(points[1], shift=RIGHT * 0.2)),
               ("match", lambda: FadeIn(step, shift=UP * 0.15)), other="happy")

        self.finish("S09_summary")

    # ========================================= 10. WHAT COMES NEXT =========

    def next_session(self):
        self.begin("S10_next", "What Comes Next", "What comes next?")

        ok = text("Context tells you which meaning is active", BODY).move_to(UP * 0.1)
        but = text("But some pairs trip people up anyway", BODY, BROWN).move_to(DOWN * 0.8)
        sent = para(['"The server suffered ________ outages last week:'], ['it went down every few hours."'])
        place(sent, x=0.0, top=BOARD_TOP - 0.35)
        pair = phrase(text("continuous", BODY, BLUE, BOLD), text("/", BODY, MUTED), text("continual", BODY, BROWN, BOLD),
                      buff=0.5).move_to(DOWN * 1.1)
        gap = text("Down all week, with no gap at all?", LABEL, MUTED).move_to(DOWN * 2.0)
        nxt = text("Next session:  Commonly confused synonyms", LABEL, BROWN, BOLD).move_to(DOWN * 3.0)
        self.fit(ok, but, sent, pair, gap, nxt)

        self.N("s10_01", "Context tells you which meaning is active. But some pairs of words trip people up even when "
                         "the context is completely clear.",
               ("active", lambda: FadeIn(ok, shift=UP * 0.15)),
               ("pairs", lambda: FadeIn(but, shift=UP * 0.15)))
        self.wipe()
        self.T("s10_02", "These two look almost identical. Most people think they're perfect synonyms. One of them is "
                         "right here, and the other would mean the server was down all week, with no gap at all.",
               (None, lambda: FadeIn(sent, shift=UP * 0.2)),
               ("two", lambda: FadeIn(pair, shift=UP * 0.15)),
               ("perfect", lambda: [hl(pair[0], 1.06), hl(pair[2], 1.06)]),
               ("week", lambda: FadeIn(gap, shift=UP * 0.15)), other="think")
        self.Q("s10_03", "Which one?",
               (None, lambda: [hl(pair[0]), self.react("A", "surprised")]),
               (None, lambda: hl(pair[2])), other="confused")
        self.T("s10_04", "Next session.", (None, lambda: FadeIn(nxt, shift=UP * 0.15)))

        self.the_end("S10_next")

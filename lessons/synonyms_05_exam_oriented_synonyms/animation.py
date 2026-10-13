"""
animation.py for the LMS video generator.

Course : C-CAT Preparation - Section A: English Language and Verbal Ability
Module : 1 Vocabulary   Lesson : 1 Synonyms (Session 2)
Video  : 05 - Exam-Oriented Synonyms   (previous: Commonly confused synonyms;  next: Synonym question-solving
         techniques)
Source : C:/Final scripts/Scipts/05 - Exam-oriented synonyms.pdf

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

Sarvam AI voices: the ids above are voice-library ids. With the Sarvam engine each id is turned into a
  Sarvam speaker by settings.json > audio.sarvam.voices. Six different voices need this map:
    "vijay": "vijay", "aditya": "aditya", "prasad": "kabir", "kavya": "kavya", "ritu": "ritu", "student_a": "rahul"

Screen zones:
  top band   teacher (left corner), scene heading, the four students (right corner)
  strip      the question being asked or the student's line
  board      everything else (BOARD_TOP down to FLOOR)

Section map:
  S01 You know more than you think   S02 The exam-oriented word bank   S03 How C-CAT tests it
  S04 Attempts and traps   S05 WHAT: clusters, not lists   S06 HOW: three habits   S07 WHY: compression
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

Q1_LINES = [["Choose the word most nearly SIMILAR in meaning to:", ("EPHEMERAL", BLUE, BOLD)]]
Q1_OPTIONS = [("a", "Eternal"), ("b", "Transient"), ("c", "Ethereal"), ("d", "Evident")]
Q2_LINES = [['"The API documentation was so', ("VERBOSE", BLUE, BOLD), "that developers stopped"],
            ['reading it and went straight to the examples."'],
            [("The word closest in meaning to VERBOSE is:", MUTED)]]
Q2_OPTIONS = [("a", "Wordy"), ("b", "Verbal"), ("c", "Vivid"), ("d", "Concise")]

BANK = [["Formal word", "Everyday word"], ["ephemeral", "short-lived"], ["verbose", "wordy"],
        ["ubiquitous", "everywhere"], ["obdurate", "stubborn"]]
CLUSTERS = [["SHORT-LIVED", "ephemeral, transient, fleeting, evanescent"],
            ["TOO WORDY", "verbose, loquacious, garrulous, prolix"],
            ["EVERYWHERE", "ubiquitous, omnipresent, pervasive"],
            ["STUBBORN", "obdurate, obstinate, intransigent, adamant"],
            ["VERY CAREFUL", "meticulous, scrupulous, painstaking"],
            ["OUTDATED", "obsolete, archaic, antiquated, outmoded"],
            ["UNNECESSARY", "redundant, superfluous, extraneous"],
            ["MAKE LESS BAD", "mitigate, alleviate, allay, assuage"],
            ["FRANK", "candid, forthright, blunt"],
            ["HARD-WORKING", "diligent, industrious, assiduous"],
            ["PRAISE", "commend, laud, extol, acclaim"]]
C_UNNECESSARY = 6
ROOTS = [["Root", "Meaning", "Family"],
         ["chron", "time", "chronic, chronological, synchronous"],
         ["loqu / locu", "speak", "loquacious, eloquent, colloquial"],
         ["verb", "word", "verbose, verbatim, verbal"],
         ["omni", "all", "omnipresent, omniscient, omnivorous"],
         ["bene / mal", "good / bad", "benevolent, beneficial / malicious, malfunction"],
         ["epi + hemera", "on + day", "ephemeral: lasting only a day"]]
CLOUD = ["candid", "abate", "lucid", "terse", "novel", "frugal", "ardent", "placid", "rigid", "astute", "benign",
         "brisk", "futile", "hasty", "vivid", "wary", "tacit", "ample"]
GLOW = (1, 4, 8, 11, 15)                    # the smaller set that lights up

assert len(CLUSTERS) == 11 and CLUSTERS[C_UNNECESSARY][0] == "UNNECESSARY" and len(CLOUD) == 18


def mono(*parts, size=CODE):
    """One line of terminal text made of pieces (a string, or (string, colour))."""
    row, x = VGroup(), 0.0
    for part in parts:
        s, c = (part, INK) if isinstance(part, str) else part
        piece = line_at(s, x, 0.0, size, c, NORMAL, NORMAL, MONO)
        x = piece.line_end + size * 0.005
        row.add(piece)
    return row


class ExamOrientedSynonyms(LMSScene):
    lesson_title = "Exam-Oriented Synonyms"

    def construct(self):
        self.camera.background_color = BG
        self.cast = None
        self.title_bar = None
        self.spoken = None
        self.talking = None
        self.faces = {}

        self.hook()
        self.bank()
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

    # ============================= 1. YOU KNOW MORE THAN YOU THINK =========

    def hook(self):
        self.scene_start("S01_hook", title="You Know More Than You Think")
        card = self.opening("Exam-Oriented Synonyms", "Commonly confused synonyms")
        self.heading("You already know it")

        hard = VGroup(*[text(s, BODY, MUTED, BOLD) for s in ("EPHEMERAL", "UBIQUITOUS", "OBDURATE")])
        hard.arrange(RIGHT, buff=0.9)
        place(hard, x=0.0, top=BOARD_TOP - 0.2)
        tag_e = text("short-lived", SMALL, BROWN, BOLD).next_to(hard[0], DOWN, buff=0.15)
        t1 = mono("$ git clone", ("--verbose", INK), "https://example.com/repo.git")
        t2 = mono("$ kubectl describe pod web-1", ("# ...", MUTED), ("ephemeral-storage:", INK), "1Gi")
        place(t1, left=-5.6, y=-0.35)
        place(t2, left=-5.6, y=-1.3)
        self.fit(hard, VGroup(t1, t2))
        verbose, storage = t1[1], t2[2]
        tag_v = text("wordy: it prints more output", SMALL, BROWN, BOLD).next_to(verbose, DOWN, buff=0.15)
        tag_s = text("the storage that disappears with the pod", SMALL, BROWN, BOLD).next_to(storage, DOWN, buff=0.15)
        self.fit(tag_v, tag_s)
        xs = np.linspace(-5.4, 5.4, 6)
        cloud = VGroup(*[text(w, SMALL, MUTED).set_opacity(0.45).move_to([xs[k % 6], (-2.35, -2.8, -3.25)[k // 6], 0])
                         for k, w in enumerate(CLOUD)])

        self.N("s1_01", "Three words, and almost no hands went up. But some of these students have used one of them in "
                        "a terminal that very week.",
               ("words", lambda: [FadeOut(card), FadeIn(hard, shift=UP * 0.2)]),
               ("hands", lambda: self.react("ABCD", "confused")),
               ("terminal", lambda: self.react("AB", "think")))
        self.Q("s1_02", "Last time almost nobody could give me a synonym for these. Let me try a different question. "
                        "Has anyone here ever typed this?",
               ("synonym", lambda: hl(hard, 1.05)),
               ("typed", lambda: LaggedStart(FadeIn(t1, shift=RIGHT * 0.2), FadeIn(t2, shift=RIGHT * 0.2),
                                             lag_ratio=0.5, run_time=1.6)),
               shown="Has anyone here ever typed this?")
        self.S("A", "s1_03", "Verbose I know. It prints more output. It's wordy.",
               ("Verbose", lambda: verbose.animate.set_color(BLUE)),
               ("wordy", lambda: FadeIn(tag_v, shift=UP * 0.1)), look="happy")
        self.S("B", "s1_04", "Ephemeral storage. In Kubernetes, it's the storage that disappears when the pod dies.",
               ("Ephemeral", lambda: storage.animate.set_color(BLUE)),
               ("disappears", lambda: FadeIn(tag_s, shift=UP * 0.1)))
        self.Q("s1_05", "So what does ephemeral mean?", (None, lambda: hl(hard[0])),
               shown="So what does 'ephemeral' mean?")
        self.S("B", "s1_06", "Short-lived. Temporary.",
               (None, lambda: [hard[0].animate.set_color(BLUE), FadeIn(tag_e, shift=UP * 0.1)]),
               look="happy", other="happy")
        self.T("s1_07", "You knew it all along. You'd just never seen it inside an English question.",
               ("knew", lambda: hl(hard[0])), look="happy")
        self.S("D", "s1_08", "But there are still hundreds of thousands of words. We can't learn them all.",
               ("thousands", lambda: LaggedStart(*[FadeIn(m) for m in cloud], lag_ratio=0.1, run_time=2.0)),
               look="ask")
        self.T("s1_09", "You don't have to. Exams lean on a much smaller set of words, the ones that turn up again and "
                        "again in aptitude tests. Today is about how to build that set efficiently.",
               ("smaller", lambda: [cloud[k].animate.set_color(BLUE).set_opacity(1.0) for k in GLOW]),
               ("build", lambda: [hl(cloud[k], 1.2) for k in GLOW]))

        self.finish("S01_hook")

    # ============================ 2. THE EXAM-ORIENTED WORD BANK ===========

    def bank(self):
        self.begin("S02_bank", "The Exam-Oriented Word Bank", "The exam word bank")

        g = Grid(BANK, (5.0, 3.6), row_h=0.56)
        place(g, x=0.0, top=BOARD_TOP - 0.2)
        arrows = VGroup(*[small_arrow().move_to([g.cell(0, 1).get_left()[0] - 1.1, g.cell(r, 1).get_y(), 0])
                          for r in range(1, 5)])
        no_list = text("C-CAT publishes no official word list", LABEL, MUTED).move_to(DOWN * 2.2)
        method = text("Build a method that works on any formal word", LABEL, BROWN, BOLD).move_to(DOWN * 2.85)
        self.fit(VGroup(g, arrows), no_list, method)

        self.T("s2_01", "Aptitude-style vocabulary tends to come from a pool of formal, slightly academic words. These "
                        "words have common, everyday synonyms. The test checks whether you can connect the formal "
                        "word to the everyday one.",
               ("formal", lambda: FadeIn(VGroup(g.col(0), g.rule), shift=UP * 0.2)),
               ("everyday", lambda: FadeIn(g.col(1), shift=LEFT * 0.3)),
               ("connect", lambda: LaggedStart(*[GrowArrow(a) for a in arrows], lag_ratio=0.3, run_time=1.5)))
        self.N("s2_02", "C-CAT doesn't publish an official word list. So the goal isn't to memorise a rumoured list. "
                        "The goal is to build a method that works on any formal word.",
               ("official", lambda: FadeIn(no_list, shift=UP * 0.15)),
               ("method", lambda: FadeIn(method, shift=UP * 0.15)))

        self.finish("S02_bank")

    # ======================================== 3. HOW C-CAT TESTS IT ========

    def exam(self):
        self.begin("S03_exam", "How C-CAT Tests It", "How C-CAT tests it")

        self.q1 = Question("Practice question 1", Q1_LINES, Q1_OPTIONS, SMALL)
        self.q2 = Question("Practice question 2", Q2_LINES, Q2_OPTIONS, SMALL)
        self.both = VGroup(self.q1, self.q2).arrange(DOWN, buff=0.6, aligned_edge=LEFT)
        place(self.both, x=0.0, top=BOARD_TOP - 0.15)
        self.fit(self.both)
        q1, q2 = self.q1, self.q2

        self.T("s3_01", "Two practice questions, written for this class.",
               ("practice", lambda: FadeIn(q1, shift=UP * 0.2)),
               ("class", lambda: FadeIn(q2, shift=UP * 0.2)))
        self.T("s3_02", "Forty-five seconds. And yes, even though we just discussed both words, watch the options.",
               ("options", lambda: [hl(q1.opts, 1.04), hl(q2.opts, 1.04)]), look="ask", other="think", think=45.0)

        self.scene_end("S03_exam")          # the two questions stay on the board for the next scene

    # ======================================== 4. ATTEMPTS AND TRAPS ========

    def attempts(self):
        self.begin("S04_attempts", "Attempts and Traps", "Attempts and traps")

        q1, q2 = self.q1, self.q2
        pick_1c = under(q1.opts.rows["c"], BLUE)
        pick_1b = under(q1.opts.rows["b"], BROWN)
        pick_2b = under(q2.opts.rows["b"], BLUE)
        alike = text("Look-alike: same sounds, different meaning", SMALL, BAD, BOLD).next_to(q1.label, RIGHT, buff=0.8)
        root = text("verbose / verbal: same root, different job", SMALL, BAD, BOLD).next_to(q2.label, RIGHT, buff=0.8)
        self.fit(alike, root)

        self.Q("s4_01", "Question one.", (None, lambda: hl(q1.label)), shown="Question 1?")
        self.S("C", "s4_02", "Ethereal. It sounds almost the same as ephemeral, and both sound like something floating "
                             "in the air.",
               ("Ethereal", lambda: Create(pick_1c)))
        self.S("A", "s4_03", "But we just said ephemeral means short-lived. Ethereal means, light? Heavenly?",
               ("light", lambda: hl(q1.opts.rows["c"])), look="confused")
        self.S("B", "s4_04", "Transient. Like a transient error, one that goes away by itself.",
               ("Transient", lambda: Create(pick_1b)), look="think")
        self.T("s4_05", "You just found the most common trap in exam vocabulary. The look-alike. Ephemeral and "
                        "ethereal share sounds, not meaning.",
               ("trap", lambda: [pick_1c.animate.set_color(BAD), self.react("C", "oops")]),
               ("sounds", lambda: FadeIn(alike, shift=LEFT * 0.2)))
        self.Q("s4_06", "Question two?", (None, lambda: hl(q2.label)), shown="Question 2?")
        self.S("D", "s4_07", "Verbal. Verb is in both words.",
               ("Verbal", lambda: Create(pick_2b)))
        self.S("D", "s4_08", "Wait. Verbal means spoken, in words, not too many words.",
               ("spoken", lambda: [pick_2b.animate.set_color(BAD), FadeIn(root, shift=LEFT * 0.2)]), look="oops")
        self.T("s4_09", "So we have a word we understand, and we still want to pick the look-alike. Let's fix that.",
               ("pick", lambda: [hl(alike, 1.04), hl(root, 1.04)]))

        self.finish("S04_attempts")

    # ====================== 5. WHAT: LEARN WORDS IN CLUSTERS, NOT LISTS ====

    def what(self):
        self.begin("S05_what", "WHAT: Learn Words in Clusters, Not Lists", "Clusters, not lists")

        g = Grid(CLUSTERS, (3.4, 8.4), size=SMALL, row_h=0.4, header=False, styles=[(BLUE, BOLD), (INK, NORMAL)])
        place(g, x=0.0, top=BOARD_TOP - 0.12)
        self.fit(g)

        word = text("redundant", TITLE, BLUE, BOLD).move_to(UP * 0.5)
        senses = Grid([["Everyday English", "not needed"],
                       ["System design", "duplicated on purpose, so the system stays reliable"]], (3.3, 9.9),
                      row_h=0.7, header=False, styles=[(MUTED, NORMAL), (INK, NORMAL)])
        place(senses, x=0.0, top=-0.6)
        decides = text("The sentence decides", BODY, BROWN, BOLD).move_to(DOWN * 2.7)
        self.fit(word, senses, decides)

        self.play(LaggedStart(*[FadeIn(g.row(r), shift=RIGHT * 0.2) for r in range(len(CLUSTERS))], lag_ratio=0.25),
                  run_time=3.5)
        self.T("s5_01", "A flat list of five hundred words is hard to remember. A cluster turns each new word into one "
                        "more member of a group you already know. Learn the cluster's everyday meaning first. Then "
                        "every formal word is just another name for it.",
               ("cluster", lambda: [hl(g.row(0), 1.04)]),
               ("everyday", lambda: hl(g.col(0), 1.04)),
               ("formal", lambda: hl(g.col(1), 1.03)))
        self.S("A", "s5_02", "But redundant in our field is a good thing. Redundant servers are backups.",
               ("redundant", lambda: [hl(g.row(C_UNNECESSARY), 1.06)]), look="ask")
        self.T("s5_03", "Excellent. That's context-based synonyms again. In everyday English, redundant means not "
                        "needed. In system design, it means duplicated on purpose so the system stays reliable. The "
                        "sentence decides.",
               ("Excellent", self.wipe),
               ("everyday", lambda: [FadeIn(word, scale=1.1), FadeIn(senses.row(0), shift=UP * 0.15)]),
               ("system", lambda: FadeIn(senses.row(1), shift=UP * 0.15)),
               ("decides", lambda: FadeIn(decides, shift=UP * 0.15)), look="happy")

        self.finish("S05_what")

    # ===================== 6. HOW: THREE HABITS THAT GROW THE BANK =========

    def how(self):
        self.begin("S06_how", "HOW: Three Habits That Grow the Bank", "Three habits")

        g = Grid(ROOTS, (2.5, 2.1, 8.2), size=SMALL, row_h=0.45, styles=[(BROWN, BOLD), (INK, NORMAL), (INK, NORMAL)])
        place(g, x=0.0, top=BOARD_TOP - 0.15)
        self.fit(g)
        horizon = Line([-1.6, -3.2, 0], [1.6, -3.2, 0], color=MUTED, stroke_width=3)
        path = ArcBetweenPoints(np.array([-1.3, -3.08, 0.0]), np.array([1.3, -3.08, 0.0]), angle=-PI / 2)
        sun = Dot(path.get_start(), radius=0.15, color=FLASH)
        day = text("One day, then gone", SMALL, BROWN, BOLD).move_to([-4.3, -2.85, 0])

        def one_day():
            self.play(FadeIn(horizon), FadeIn(sun), FadeIn(day), run_time=0.4)
            self.play(MoveAlongPath(sun, path), run_time=1.6)
            self.play(FadeOut(sun), run_time=0.4)

        title2 = text("Habit 2: use the word in a technical sentence of your own", LABEL, BROWN, BOLD)
        mine = para(['"The cache is', ("ephemeral.\"", BLUE, BOLD)],
                    ['"Global variables are', ("ubiquitous", BLUE, BOLD), 'in this legacy code."'],
                    ['"The vendor is', ("obdurate", BLUE, BOLD), 'about the deadline."'], size=BODY, step=0.75)
        second = column(title2, mine, buff=0.6)
        place(second, x=0.0, top=BOARD_TOP - 0.3)

        title3 = text("Habit 3: learn each word with its opposite", LABEL, BROWN, BOLD)
        pairs = Grid([["verbose", "concise"], ["ephemeral", "permanent"], ["obdurate", "flexible"]], (4.2, 3.0),
                     size=BODY, row_h=0.75, header=False, styles=[(BLUE, BOLD), (INK, NORMAL)])
        third = VGroup(title3, pairs).arrange(DOWN, buff=0.6)
        place(third, x=0.0, top=BOARD_TOP - 0.3)
        links = VGroup(*[DoubleArrow(LEFT * 0.45, RIGHT * 0.45, buff=0, color=BROWN, stroke_width=4, tip_length=0.16)
                       .move_to([pairs.cell(0, 1).get_left()[0] - 0.95, pairs.cell(r, 0).get_y(), 0])
                       for r in range(3)])
        anchor = text("The opposite is a second anchor", LABEL).move_to(DOWN * 2.7)

        four = VGroup(*[text(s, BODY, BLUE, BOLD) for s in ("Clusters", "Roots", "Your sentences", "Opposites")])
        four.arrange(RIGHT, buff=0.9).move_to(DOWN * 0.3)
        over = text("Four connections for every word", LABEL, MUTED).next_to(four, UP, buff=0.6)
        revisit = text("Revisit them over a few days, and the words stay", LABEL, BROWN, BOLD).next_to(four, DOWN, buff=0.8)
        self.fit(second, VGroup(third, links), anchor, VGroup(four, over, revisit))

        self.T("s6_01", "First habit: roots. One root can unlock a whole family of words.",
               ("roots", lambda: LaggedStart(FadeIn(g.rule), *[FadeIn(g.row(r), shift=RIGHT * 0.2) for r in range(6)],
                                             lag_ratio=0.25, run_time=2.4)),
               ("family", lambda: hl(g.col(2, head=False), 1.03)))
        self.S("C", "s6_02", "So ephemeral literally means lasting a day? That's actually easy to remember.",
               ("ephemeral", lambda: FadeIn(g.row(6), shift=RIGHT * 0.2)),
               ("day", one_day), look="happy", other="happy")
        self.T("s6_03", "Second habit: put every new word into a technical sentence of your own. The cache is "
                        "ephemeral. Global variables are ubiquitous in this legacy code. The vendor is obdurate about "
                        "the deadline. A word you've used yourself is much harder to forget.",
               ("Second", self.wipe),
               ("technical", lambda: FadeIn(title2, shift=UP * 0.15)),
               ("cache", lambda: FadeIn(mine[0], shift=RIGHT * 0.2)),
               ("Global", lambda: FadeIn(mine[1], shift=RIGHT * 0.2)),
               ("vendor", lambda: FadeIn(mine[2], shift=RIGHT * 0.2)),
               ("forget", lambda: self.react("B", "happy")))
        self.T("s6_04", "Third habit: learn each word with an antonym. Verbose, concise. Ephemeral, permanent. "
                        "Obdurate, flexible. The opposite gives you a second anchor, and as you'll see, antonym "
                        "questions are coming soon anyway.",
               ("Third", self.wipe),
               ("antonym", lambda: FadeIn(title3, shift=UP * 0.15)),
               ("Verbose", lambda: [FadeIn(pairs.row(0)), GrowFromCenter(links[0])]),
               ("Ephemeral", lambda: [FadeIn(pairs.row(1)), GrowFromCenter(links[1])]),
               ("Obdurate", lambda: [FadeIn(pairs.row(2)), GrowFromCenter(links[2])]),
               ("anchor", lambda: FadeIn(anchor, shift=UP * 0.15)))
        self.N("s6_05", "Clusters, roots, your own sentences and opposites. Four connections for every word. Revisit "
                        "them over a few days, and the words stay with you.",
               ("Clusters", self.wipe),
               (None, lambda: FadeIn(four[0], shift=UP * 0.15)),
               ("roots", lambda: FadeIn(four[1], shift=UP * 0.15)),
               ("sentences", lambda: FadeIn(four[2], shift=UP * 0.15)),
               ("opposites", lambda: FadeIn(four[3], shift=UP * 0.15)),
               ("Four", lambda: FadeIn(over)),
               ("Revisit", lambda: FadeIn(revisit, shift=UP * 0.15)))

        self.finish("S06_how")

    # =========================== 7. WHY: VOCABULARY AS COMPRESSION =========

    def why(self):
        self.begin("S07_why", "WHY: Vocabulary as Compression", "Words as compression")

        long = column(text("Long", SMALL, MUTED, BOLD),
                      fit_w(text('"The outage lasted only a short time and then went away by itself."', LABEL),
                            2 * EDGE_X - 1.0), buff=0.2)
        short = column(text("Short", SMALL, MUTED, BOLD),
                       para(['"The outage was', ("transient.\"", BLUE, BOLD)], size=BODY), buff=0.2)
        top = column(long, short, buff=0.55)
        place(top, x=0.0, top=BOARD_TOP - 0.15)
        where = VGroup(*[VGroup(Dot(radius=0.07, color=BLUE), text(s, LABEL)).arrange(RIGHT, buff=0.25)
                         for s in ("Code reviews", "Interviews", "Design documents")])
        where.arrange(RIGHT, buff=0.9).move_to(DOWN * 1.75)
        saved = text("In the exam: one recognised word = 30 seconds saved", LABEL, BROWN, BOLD).move_to(DOWN * 2.8)
        self.fit(top, where, saved)
        word = short[1][0][1]

        self.T("s7_01", "A strong vocabulary works like compression. One precise word carries a whole sentence of "
                        "meaning. In code reviews, interviews and design documents, that precision makes you sound "
                        "like an engineer who knows exactly what they mean.",
               (None, lambda: FadeIn(long, shift=UP * 0.2)),
               ("compression", lambda: FadeIn(short, shift=UP * 0.2)),
               ("precise", lambda: hl(word)),
               ("code", lambda: LaggedStart(*[FadeIn(m, shift=UP * 0.15) for m in where], lag_ratio=0.5,
                                            run_time=2.0)))
        self.S("D", "s7_02", "And in the exam, one recognised word is thirty seconds saved.",
               ("thirty", lambda: FadeIn(saved, shift=UP * 0.15)), other="happy")
        self.T("s7_03", "Exactly.", look="happy")

        self.finish("S07_why")

    # ============================ 8. PAYOFF: SOLVING BOTH QUESTIONS ========

    def payoff(self):
        self.begin("S08_payoff", "Payoff: Solving Both Questions", "Solving both questions")

        def cluster(k, y):
            name, words = CLUSTERS[k]
            first, rest = words.split(", ", 1)
            second, tail = rest.split(", ", 1)
            row = para([(name + ":", BLUE, BOLD), (first + ",", INK), (second + ",", INK), (tail, MUTED)], size=SMALL)
            return fit_w(place(row, left=-EDGE_X + 0.3, y=y), 2 * EDGE_X - 0.6)

        q1 = Question("Practice question 1", Q1_LINES, Q1_OPTIONS, LABEL, across=False)
        place(q1, left=-EDGE_X + 0.3, top=BOARD_TOP - 0.1)
        self.fit(q1)
        n1 = {k: q1.opts.note(k, s, c) for k, s, c in (("a", "the opposite", BAD),
                                                         ("b", "same cluster: short-lived", GOOD),
                                                         ("c", "the look-alike: light and delicate", BAD),
                                                         ("d", "unrelated: obvious", BAD))}
        c1 = cluster(0, -2.8)

        q2 = Question("Practice question 2", Q2_LINES[:2], Q2_OPTIONS, LABEL, across=False)
        place(q2, left=-EDGE_X + 0.3, top=BOARD_TOP - 0.1)
        self.fit(q2)
        n2 = {k: q2.opts.note(k, s, c) for k, s, c in (("a", "same cluster: too wordy", GOOD),
                                                         ("b", "same root, but it means spoken", BAD),
                                                         ("c", "bright or lively", BAD),
                                                         ("d", "the antonym: a useful anchor", BAD))}
        c2 = cluster(1, -3.1)

        self.T("s8_01", "Question one.", (None, lambda: FadeIn(q1, shift=UP * 0.2)), look="ask")
        self.S("C", "s8_02", "Ephemeral is in the short-lived cluster. Transient is also in that cluster, so the "
                             "answer is option B. Eternal is the opposite. Ethereal is the look-alike, it means light "
                             "and delicate. Evident means obvious.",
               ("cluster", lambda: FadeIn(c1, shift=UP * 0.15)),
               ("Transient", lambda: [hl(c1[0][1]), hl(c1[0][2])]),
               ("answer", lambda: [*q1.opts.right("b"), FadeIn(n1["b"], shift=RIGHT * 0.2)]),
               ("Eternal", lambda: [*q1.opts.out("a"), FadeIn(n1["a"], shift=RIGHT * 0.2)]),
               ("Ethereal", lambda: [*q1.opts.out("c"), FadeIn(n1["c"], shift=RIGHT * 0.2)]),
               ("Evident", lambda: [*q1.opts.out("d"), FadeIn(n1["d"], shift=RIGHT * 0.2)]),
               shown="Ephemeral and transient are in the same cluster: short-lived. So the answer is (b).",
               look="think", other="happy")

        self.wipe()
        self.T("s8_03", "Question two.", (None, lambda: FadeIn(q2, shift=UP * 0.2)), look="ask")
        self.S("D", "s8_04", "Verbose is in the too wordy cluster, so option A, wordy. Verbal shares the root but "
                             "means spoken. Vivid means bright or lively. Concise is the opposite, which also explains "
                             "why developers jumped to the examples.",
               ("cluster", lambda: FadeIn(c2, shift=UP * 0.15)),
               ("option", lambda: [*q2.opts.right("a"), FadeIn(n2["a"], shift=RIGHT * 0.2)]),
               ("Verbal", lambda: [*q2.opts.out("b"), FadeIn(n2["b"], shift=RIGHT * 0.2)]),
               ("Vivid", lambda: [*q2.opts.out("c"), FadeIn(n2["c"], shift=RIGHT * 0.2)]),
               ("Concise", lambda: [*q2.opts.out("d"), FadeIn(n2["d"], shift=RIGHT * 0.2)]),
               shown="Verbose is in the 'too wordy' cluster. So the answer is (a) wordy.", other="happy")

        self.finish("S08_payoff")

    # ================================================== 9. SUMMARY =========

    def summary(self):
        self.begin("S09_summary", "Summary", "Summary")

        points = bullets(["Learn words in clusters", "Decode them with roots", "Use them in your own sentences",
                          "Pair them with opposites"], BODY, 0.32)
        step = column(text("Synonym method, step 8", SMALL, BROWN, BOLD),
                      text("Unknown formal word? Find its cluster, or decode its root.", LABEL), buff=0.2)
        board = column(points, step, buff=0.7)
        place(board, x=0.0, top=BOARD_TOP - 0.2)
        self.fit(board)

        self.Q("s9_01", "What's the system?", shown="What is the system?")
        self.S("B", "s9_02", "Learn words in clusters, decode them with roots, use them in your own sentences and pair "
                             "them with opposites.",
               ("clusters", lambda: FadeIn(points[0], shift=RIGHT * 0.2)),
               ("roots", lambda: FadeIn(points[1], shift=RIGHT * 0.2)),
               ("sentences", lambda: FadeIn(points[2], shift=RIGHT * 0.2)),
               ("opposites", lambda: [FadeIn(points[3], shift=RIGHT * 0.2), FadeIn(step, shift=UP * 0.15)]),
               other="happy")

        self.finish("S09_summary")

    # ========================================= 10. WHAT COMES NEXT =========

    def next_session(self):
        self.begin("S10_next", "What Comes Next", "What comes next?")

        unknown = text("A word in no cluster, with no root you know", BODY).move_to(UP * 0.6)
        marks = phrase(text("+3 correct", BODY, GOOD, BOLD), text("-1 wrong", BODY, BAD, BOLD),
                       text("0 skipped ?", BODY, MUTED, BOLD), buff=0.9).move_to(DOWN * 0.5)
        two = text("2 options left: guess or skip?", LABEL).move_to(DOWN * 1.5)
        three = text("3 options left: guess or skip?", LABEL).move_to(DOWN * 2.05)
        value = text("Expected marks = ?", LABEL, BROWN, BOLD).move_to(DOWN * 2.7)
        nxt = text("Next session:  Synonym question-solving techniques", SMALL, BROWN, BOLD).move_to(DOWN * 3.25)
        self.fit(unknown, marks, two, three, value, nxt)

        self.N("s10_01", "But on exam day, a word will turn up that isn't in any cluster and has no root you "
                         "recognise. And the exam has negative marking.",
               ("cluster", lambda: FadeIn(unknown, shift=UP * 0.15)),
               ("negative", lambda: FadeIn(marks, shift=UP * 0.15)))
        self.Q("s10_02", "Here's a question for next time. You've narrowed a question down to two options. Should you "
                         "guess or skip? And what if you're down to three options? Is there a point where guessing "
                         "actually becomes the smart move?",
               ("two", lambda: FadeIn(two, shift=UP * 0.15)),
               ("three", lambda: FadeIn(three, shift=UP * 0.15)),
               ("smart", lambda: [FadeIn(value, shift=UP * 0.15), self.react("A", "think")]),
               shown="Two options left: guess or skip? And with three options left?", other="confused")
        self.T("s10_03", "Next session, we'll find out.",
               ("Next", lambda: FadeIn(nxt, shift=UP * 0.15)))

        self.the_end("S10_next")

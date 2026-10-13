"""
animation.py for the LMS video generator.

Course : C-CAT Preparation - Section A: English Language and Verbal Ability
Module : 3 Verbal Ability   Lesson : 8 Arrangement of Sentences (Session 16)
Video  : 08 - Exam Practice: Sentence Construction (Arrangement of Sentences)
         (previous: Logical sequencing;  next: Lesson 9, Sentence completion)
Source : C:/Final scripts/Scipts/Lesson 8 - Arrangement of Sentences/08 - Exam practice.pdf

Note: the questions are practice questions written for the class, not past-paper questions.

Look (3Blue1Brown style): near-black background, white text, one blue and one brown accent; yellow only for a
  passing highlight, green / red only for right / wrong. Latin Modern Roman (Cambria if it is missing).

Roles (the script has no speaker labels; every line was assigned by meaning, and no label is spoken):
  NARRATOR self.N "vijay"   TEACHER self.T / self.Q "aditya"   STUDENTS self.S: A confident "prasad",
  B cautious "kavya", C the second student "ritu", D at the back "student_a".
  Stage directions are the visuals. Board text that the script does not speak (the flow card) is shown with a
  thinking bar that gives time to read it.

Sarvam AI voices (settings.json > audio.sarvam.voices, or --speaker VOICE=SPEAKER):
    "vijay": "vijay", "aditya": "aditya", "prasad": "kabir", "kavya": "kavya", "ritu": "ritu", "student_a": "rahul"

The two main questions are shown one at a time; the ninety seconds are split between them.
"2FA" is spoken as "two F A"; "S1" and "S6" as "S one" and "S six".

Section map: S01 Ninety seconds  S02 The topic  S03 The two main questions  S04 Thinking out loud: question 1
  S05 Thinking out loud: question 2  S06 Format three: the odd one out  S07 Rapid pair checks
  S08 The complete arrangement flow  S09 Payoff recap  S10 What comes next
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


def lines(strings, size=SMALL, buff=0.24, color=INK):
    """Lines of text under one another (each kept inside the board width)."""
    return column(*[fit_w(text(s, size, color), 2 * EDGE_X - 0.4) for s in strings], buff=buff)


def fixed(wrong, right):
    """Pieces of one example line: the wrong form, then the right one."""
    return [(wrong, BAD), ("correct:", MUTED), (right, GOOD)]


def family(title, *rows):
    """A rule with its example lines under it (each row is a list of ``para`` pieces)."""
    return para([(title, BLUE, BOLD)], *rows, size=SMALL, step=0.4)


def stack(blocks, buff=0.36):
    """Blocks under one another, left edges aligned."""
    return VGroup(*blocks).arrange(DOWN, buff=buff, aligned_edge=LEFT)


def checklist(items):
    """Linter lines, each with an empty check box."""
    return VGroup(*[VGroup(Square(0.24, stroke_color=MUTED, stroke_width=3),
                           fit_w(text(s, SMALL), 2 * EDGE_X - 1.2)).arrange(RIGHT, buff=0.3)
                    for s in items]).arrange(DOWN, buff=0.26, aligned_edge=LEFT)


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


def jumble(label, stem, sentences, options, letters="PQRS", size=SMALL):
    """An arrangement question: lettered sentences, and four orders as options in one row.

    ``q.sent[letter]`` is the line of one sentence: its letter tag, then its piece(s) of text."""
    rows = [[(stem, MUTED)]] + [[(f"{letter}.", BLUE, BOLD)] + (s if isinstance(s, list) else [s])
                                for letter, s in zip(letters, sentences)]       # a sentence may be a list of pieces
    q = Question(label, rows, list(zip("abcd", options)), size, across=True)
    q.sent = {letter: q.body[k + 1] for k, letter in enumerate(letters)}
    return place(q, left=-EDGE_X + 0.3, top=BOARD_TOP - 0.1)


def order_chain(steps, y=-2.9, size=LABEL, gap=0.3):
    """An order shown as a chain: (letter, note) steps joined by arrows. ``chain.steps`` are the steps."""
    items = [VGroup(text(letter, size, BLUE, BOLD), text(note, MIN_FONT, MUTED)).arrange(DOWN, buff=0.12)
             for letter, note in steps]
    parts = []
    for k, item in enumerate(items):
        parts += ([small_arrow(BROWN, 0.6)] if k else []) + [item]
    chain = VGroup(*parts).arrange(RIGHT, buff=gap).move_to(UP * y)
    fit_w(chain, 2 * EDGE_X - 0.6)
    chain.set_x(0.0)
    chain.steps, chain.arrows = items, [m for m in parts if m not in items]
    return chain


def link(chain, k):
    """Animations that bring in step ``k`` of an order chain, with the arrow that leads to it."""
    return [up(chain.steps[k])] + ([GrowArrow(chain.arrows[k - 1])] if k else [])


def links(chain, run_time=2.5):
    """The whole chain, step by step."""
    return LaggedStart(*[AnimationGroup(*link(chain, k)) for k in range(len(chain.steps))], lag_ratio=0.5,
                       run_time=run_time)


def funnel(rows, top=BOARD_TOP - 0.3, x=1.3, widest=10.0, narrowest=4.6, h=0.72, gap=0.16):
    """A narrowing funnel: (label, text) rows, widest at the top. Each row is VGroup(bar, text, label)."""
    out = VGroup()
    for k, (label, s) in enumerate(rows):
        w = widest - (widest - narrowest) * k / max(1, len(rows) - 1)
        bar = Rectangle(width=w, height=h, stroke_color=BLUE, stroke_width=3, fill_color=FILL, fill_opacity=1.0)
        bar.move_to([x, top - h / 2 - k * (h + gap), 0])
        body = fit_w(text(s, SMALL), w - 0.4).move_to(bar)
        tag = text(label, SMALL, BROWN, BOLD)
        tag.move_to([x - widest / 2 - 0.3 - tag.width / 2, bar.get_y(), 0])
        out.add(VGroup(bar, body, tag))
    return out


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

CRUMB = "C-CAT Preparation  ›  English  ›  Verbal Ability  ›  Arrangement of Sentences"
TOOLKIT = ["Opener signals", "Closer signals", "The reference table", "Connector families", "Logic templates"]
FLOW = ["1.  Read all the sentences for the topic thread",
        "2.  Opener: no backward pointers, most general   ›   eliminate options",
        "3.  Closer: a conclusion, an outcome, 'now'   ›   eliminate options",
        "4.  Mandatory pairs: pronouns, this / such, the former, connectors",
        "5.  No signals? Use logic templates: process, chronology, problem to solution",
        "6.  Verify the surviving option once, end to end",
        "Odd one out: find the thread; the sentence outside it goes"]


def make_question(k):
    if k == 1:
        return jumble("Practice question 1", "Arrange the sentences to form a coherent paragraph.",
                      [["An index", "works like the index at the back of a book."],
                       ["Databases often store", "millions of rows", "in a single table."],
                       ["Without help, finding one row would mean scanning all of", "them."],
                       ["However,", "every index must be updated whenever the data changes."],
                       ["It", "lets the database jump directly to the rows it needs."]],
                      ["QRPTS", "QPRTS", "RQPTS", "QRPST"], letters="PQRST")
    if k == 2:
        return jumble("Practice question 2", "S1 and S6 are fixed. Arrange P, Q, R.",
                      ["Passwords alone are no longer considered sufficient protection.",
                       "Even strong passwords can be stolen through phishing or data breaches.",
                       ["This second factor", "might be a code from an app or a hardware key."],
                       ["Two-factor authentication", "adds", "a second check", "after the password."],
                       ["As a result, many companies now require", "it", "for all employees."]],
                      ["PRQ", "RPQ", "RQP", "PQR"], letters=["S1", "P", "Q", "R", "S6"])
    return sentence_question("Rapid 1", [[("Which sentence does not belong in the paragraph?", MUTED)]],
                             ["Docker packages an application together with its dependencies.",
                              "Containers start in seconds because they share the host's kernel.",
                              "The Python language was named after a British comedy group.",
                              "This makes deployments consistent across different machines."])


def chain_1():
    return order_chain([("Q", "opens"), ("R", "them: the rows"), ("P", "an index"), ("T", "it: the index"),
                        ("S", "however: the cost")], y=-2.95, gap=0.2)


def chain_2():
    return order_chain([("S1", "the problem"), ("P", "why"), ("R", "the solution: 2FA"), ("Q", "this second factor"),
                        ("S6", "require it")], y=-2.95, gap=0.2)


class ExamPracticeArrangementOfSentences(LMSScene):
    lesson_title = "Exam Practice: Arrangement of Sentences"

    def construct(self):
        self.reset()
        for scene in (self.hook, self.topic, self.exam, self.first, self.second, self.odd_one, self.pairs,
                      self.full_flow, self.recap, self.next_session):
            scene()

    # ------------------------------------------------------ scene shortcuts --

    def reset(self):
        """State of the stage at the start of the video."""
        self.camera.background_color = BG
        self.cast = self.title_bar = self.spoken = self.talking = None
        self.faces = {}
        self.q_now, self.q_marks, self.picked = None, [], {}

    def points(self, items, size=BODY, buff=0.4, top=BOARD_TOP - 0.4):
        """A list of bullet points, placed on the board (not shown yet)."""
        pts = bullets(items, size, buff)
        place(pts, x=0.0, top=top)
        return self.fit(pts)

    def reveal(self, mobs, anchors):
        """Cues that bring ``mobs`` in one after another, each at its anchor word."""
        return [(anchor, (lambda m=m: side(m))) for anchor, m in zip(anchors, mobs)]

    def foot(self, s, color=BROWN, y=-3.05, size=LABEL):
        """A one-line conclusion at the bottom of the board (not shown yet)."""
        return fit_w(text(s, size, color, BOLD), 2 * EDGE_X - 0.4).move_to(UP * y)

    def card(self, title, body, read=5.0, top=BOARD_TOP - 0.15):
        """A titled card (rules, a table) that the script shows but does not speak:
        it appears line by line, then a thinking bar gives time to read it."""
        head = [text(title, LABEL, BLUE, BOLD)] if title else []
        board = VGroup(*head, body).arrange(DOWN, buff=0.32, aligned_edge=LEFT)
        place(board, x=0.0, top=top)
        self.fit(board)
        rows = [body.row(r) for r in range(len(body.cells))] if isinstance(body, Grid) else list(body)
        extra = [FadeIn(body.rule)] if isinstance(body, Grid) and body.rule is not None else []
        self.play(*[up(m) for m in head], *extra, LaggedStart(*[side(m) for m in rows], lag_ratio=0.5),
                  run_time=min(6.0, 1.0 + 0.6 * len(rows)))
        if read:
            self.countdown(read)
        return board

    def new_q(self, k):
        """A fresh copy of practice question 1 or 2 (Q1 / Q2 and LETTERS are defined with the lesson)."""
        maker = globals().get("make_question")          # a lesson may build its questions its own way
        if maker is not None:
            return self.fit(maker(k))
        g = globals()
        return self.fit(sentence_question(*g["Q1" if k == 1 else "Q2"], letters=g["LETTERS"]))

    def exam_scene(self, sid, nid_intro, intro, nid_time, time_line, seconds, cue="practice"):
        """The two practice questions: the narrator introduces them, the teacher gives the time."""
        self.begin(sid, "How C-CAT Tests It", "How C-CAT tests it")
        self.q1, self.q2 = self.new_q(1), self.new_q(2)
        self.N(nid_intro, intro, (cue, lambda: self.show_question(self.q1)))
        self.timed(nid_time, time_line, self.q2, seconds)
        self.scene_end(sid)                 # a question stays on the board for the next scene

    def ask_q(self, nid, spoken, q):
        """The teacher names the next question, and it comes onto the board."""
        self.T(nid, spoken, (None, lambda: self.show_question(q)), look="ask")

    def summary_scene(self, sid, who, nid_q, nid_a, spoken, items, anchors, shown=None, size=LABEL):
        """"Summary?", and one student answers while the points appear."""
        self.begin(sid, "Summary", "Summary")
        pts = self.points(items, size, 0.36, BOARD_TOP - 0.3)
        self.Q(nid_q, "Summary?")
        self.S(who, nid_a, spoken, *self.reveal(pts, anchors), shown=shown, other="happy")
        self.finish(sid)

    def err(self, q, letter, fix):
        """Error spotting: this part has the error (red); the correction goes under it (green)."""
        return [q.opts.rows[letter].animate.set_color(BAD), self.tag(q, letter, fix, GOOD)]

    def passes(self, q, letters, s=None):
        """These parts pass their rule check: a small tick, and an optional note."""
        anims = []
        for letter in letters:
            mark = self.keep(tick(0.2).next_to(q.opts.rows[letter], RIGHT, buff=0.2))
            anims.append(FadeIn(mark, scale=0.6))
            if s:
                anims.append(self.tag(q, letter, s, MUTED))
        return anims

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

    # ============================================= 1. NINETY SECONDS =======

    def hook(self):
        self.scene_start("S01_hook", title="Ninety Seconds")
        card = self.opening("Exam Practice: Sentence Construction", "Logical sequencing")
        self.heading("Ninety seconds")

        kit = bullets(TOOLKIT, LABEL, 0.28)
        kit_head = text("The arrangement toolkit", SMALL, MUTED, BOLD)
        left = column(kit_head, kit, buff=0.3)
        place(left, left=-EDGE_X + 0.8, top=BOARD_TOP - 0.3)
        clock = VGroup(text("90 seconds", TITLE, BLUE, BOLD),
                       text("for a five-sentence question", SMALL, MUTED)).arrange(DOWN, buff=0.25)
        clock.move_to(RIGHT * 3.3 + UP * 0.1)
        clues = self.foot("Two solid clues, then let the options do the rest", y=-2.8)
        self.fit(left, clock)

        self.N("s1_01", "Five lessons of clues. Today the class uses all of them together, in three different "
                        "question formats, against the clock.",
               ("clues", lambda: [FadeOut(card), FadeIn(kit_head), LaggedStart(*[side(m) for m in kit], lag_ratio=0.25)]))
        self.T("s1_02", "Para jumbles take longer than error spotting, so give yourself about ninety seconds for a "
                        "five-sentence question. The aim isn't to build the order from scratch. It's to find two "
                        "solid clues and let the options do the rest.",
               ("ninety", lambda: up(clock)),
               ("solid", lambda: up(clues)))
        self.S("B", "s1_03", "Bookends and mandatory pairs, then eliminate.",
               ("eliminate", lambda: FadeOut(left)), look="happy")

        self.finish("S01_hook")

    # ================================================== 2. THE TOPIC =======

    def topic(self):
        self.begin("S02_topic", "The Topic", "Three formats")
        pts = self.points(["Format 1:  a full jumble", "Format 2:  the first and last sentences are fixed",
                           "Format 3:  find the sentence that doesn't belong"])
        self.T("s2_01", "Format one: a full jumble. Format two: first and last sentences fixed. Format three: find "
                        "the sentence that doesn't belong.",
               *self.reveal(pts, ("jumble", "fixed", "belong")))
        self.finish("S02_topic")

    # ====================================== 3. THE TWO MAIN QUESTIONS ======

    def exam(self):
        self.begin("S03_exam", "The Two Main Questions", "The two main questions")
        self.q1, self.q2 = self.new_q(1), self.new_q(2)
        self.N("s3_01", "Both are practice questions written for this class.",
               ("practice", lambda: self.show_question(self.q1)))
        self.timed("s3_02", "Ninety seconds for both.", self.q2, 90.0)
        self.scene_end("S03_exam")              # a question stays on the board for the next scene

    # ========================= 4. THINKING OUT LOUD: QUESTION 1 ============

    def first(self):
        self.begin("S04_first", "Thinking Out Loud: Question 1", "Question 1, out loud")
        q1 = self.new_q(1)
        chain = chain_1()

        self.Q("s4_01", "Question one. Two clues, then eliminate.", (None, lambda: self.show_question(q1)),
               shown="Question 1. Two clues, then eliminate.")
        self.keep(chain)
        self.S("A", "s4_02", "Opener: Q. It names databases in full and has no pointers. R can't open, because "
                             "them points back, and without help implies a problem already set up. That rules out "
                             "option C.",
               ("names", lambda: [link(chain, 0), hl(q1.sent["Q"], 1.02)]),
               ("them", lambda: q1.sent["R"][2].animate.set_color(BROWN)),
               ("rules", lambda: self.no(q1, "c")), look="think",
               shown="Opener: Q. It names databases in full. R can't open: 'them' points back. That rules out (c).")
        self.S("D", "s4_03", "Mandatory pair: T's it needs a singular thing that does the jumping. That's the index "
                             "from P. So P then T. Option D puts S between P and T. Eliminated.",
               ("singular", lambda: q1.sent["T"][1].animate.set_color(BROWN)),
               ("index", lambda: q1.sent["P"][1].animate.set_color(BROWN)),
               ("Eliminated", lambda: self.no(q1, "d")), look="think",
               shown="Mandatory pair: T's 'it' needs a singular thing that jumps: the index from P. (d) is out.")
        self.S("C", "s4_04", "Q then R, or Q then P? R's them refers to the millions of rows in Q, so R follows Q "
                             "directly. That's option A. And S, however, the index must be updated, is the cost, "
                             "so it closes.",
               ("millions", lambda: q1.sent["Q"][2].animate.set_color(BROWN)),
               ("directly", lambda: link(chain, 1)),
               ("option", lambda: [self.yes(q1, "a"), self.no(q1, "b"), link(chain, 2), link(chain, 3)]),
               ("closes", lambda: link(chain, 4)), look="think", other="happy",
               shown="R's 'them' refers to the millions of rows in Q, so R follows Q: (a). S, 'however', closes.")

        self.finish("S04_first")

    # ========================= 5. THINKING OUT LOUD: QUESTION 2 ============

    def second(self):
        self.begin("S05_second", "Thinking Out Loud: Question 2", "Question 2, out loud")
        q2 = self.new_q(2)
        chain = chain_2()

        self.Q("s5_01", "Question two. The bookends are given. How does that change your approach?",
               (None, lambda: self.show_question(q2)),
               shown="Question 2. The bookends are given. How does that change your approach?")
        self.keep(chain)
        self.S("B", "s5_02", "S one says passwords aren't enough. S six says require it, where it must be "
                             "two-factor authentication. So the sentence right before S six has to keep two F A as "
                             "the topic.",
               ("enough", lambda: hl(q2.sent["S1"], 1.02)),
               ("require", lambda: q2.sent["S6"][2].animate.set_color(BROWN)),
               ("before", lambda: hl(q2.sent["S6"], 1.02)), look="think",
               shown="S1: passwords aren't enough. S6: 'require it', and 'it' must be 2FA. 2FA stays the topic.")
        self.T("s5_03", "Next.", look="ask")
        self.S("B", "s5_04", "P explains why passwords aren't enough. They get stolen. That follows S one "
                             "naturally. R introduces two F A as the solution. Q's this second factor needs R, "
                             "which mentions the second check. So P, R, Q. And S six's it points to two F A, which "
                             "Q is still describing.",
               ("explains", lambda: [link(chain, 0), link(chain, 1)]),
               ("introduces", lambda: link(chain, 2)),
               ("needs", lambda: [link(chain, 3), hl(q2.sent["Q"][1], 1.06), hl(q2.sent["R"][3], 1.06)]),
               ("points", lambda: [link(chain, 4), self.yes(q2, "a")]), look="think", other="happy",
               shown="P: why passwords aren't enough. R introduces 2FA. Q's 'this second factor' needs R. PRQ: (a).")
        self.Q("s5_05", "Why not option C, R, Q, P?", (None, lambda: hl(q2.opts.rows["c"], 1.08)),
               shown="Why not (c), RQP?")
        self.S("D", "s5_06", "Then P, about passwords being stolen, would sit right before S six, and require it "
                             "would seem to mean requiring passwords. The pointer would land on the wrong thing.",
               ("wrong", lambda: self.no(q2, "bcd")),
               shown="Then P would sit right before S6, and 'require it' would seem to mean requiring passwords.")

        self.finish("S05_second")

    # ========================= 6. FORMAT THREE: THE ODD ONE OUT ============

    def odd_one(self):
        self.begin("S06_odd", "Format Three: The Odd One Out", "The odd one out")
        q3 = self.new_q(3)
        outside = self.foot("Find the thread; the sentence outside it goes", y=-3.15)

        self.show_question(q3)
        self.T("s6_01", "Thirty seconds.", look="ask", other="think", think=30.0)
        self.S("C", "s6_02", "Option C. It's true, but it's off-topic. Everything else is about Docker and "
                             "containers.",
               ("true", lambda: self.yes(q3, "c", "True, but off-topic")),
               shown="(c). It's true, but it's off-topic. Everything else is about Docker and containers.")
        self.Q("s6_03", "What makes this format tricky?")
        self.S("B", "s6_04", "The odd sentence is sometimes on the same topic, but it breaks the thread. Like a "
                             "sentence about the history of Docker in a paragraph about how to use it.",
               look="think",
               shown="The odd sentence is sometimes on the same topic, but it breaks the thread.")
        self.T("s6_05", "Exactly. Find the thread, then find the sentence that doesn't connect to the sentences "
                        "around it.",
               ("thread", lambda: [self.tag(q3, "a", "The thread: packaging"), self.tag(q3, "b", "The thread: speed"),
                                   self.tag(q3, "d", "The thread: consistency")]),
               ("connect", lambda: up(outside)), look="happy")

        self.finish("S06_odd")

    # ======================================== 7. RAPID PAIR CHECKS =========

    def pair(self, n, first, second, good, rule):
        """One rapid item: two sentences in the order given, fifteen seconds to judge it.

        Returns the card, the verdict mark and the rule tag (the last two are not shown yet)."""
        body = para([("First:", MUTED), first], [("Then:", MUTED), second], size=LABEL, step=0.75)
        card = VGroup(text(f"{n}.", LABEL, BLUE, BOLD), body).arrange(RIGHT, buff=0.4, aligned_edge=UP)
        card.move_to(UP * 0.2)
        self.fit(card)
        mark = (tick(0.4) if good else cross(0.36)).next_to(card, RIGHT, buff=0.5)
        note = fit_w(text(rule, LABEL, GOOD if good else BAD, BOLD), 2 * EDGE_X - 0.6).move_to(DOWN * 1.9)
        self.play(up(card), run_time=0.6)
        self.countdown(15.0)
        return card, mark, note

    def pairs(self):
        self.begin("S07_pairs", "Rapid Pair Checks", "Rapid pair checks")

        self.Q("s7_01", "Fifteen seconds each. Is the order right or wrong, and why?")
        card, mark, note = self.pair(2, '"Moreover, it is open source."', '"Linux runs on most of the world\'s servers."',
                                     False, "'Moreover' cannot come before the point it adds to")
        self.S("D", "s7_02", "Wrong. Moreover can't come before the point it adds to. Linux first, then moreover.",
               ("Wrong", lambda: [FadeIn(mark, scale=0.6), up(note)]),
               shown="Wrong. 'Moreover' can't come before the point it adds to. Linux first, then 'moreover'.")
        self.play(FadeOut(VGroup(card, mark, note)), run_time=0.5)

        card, mark, note = self.pair(3, '"A recursive function calls itself."',
                                     '"Such functions need a base case to stop."', True,
                                     "'Such functions' refers back to recursive functions")
        self.S("A", "s7_03", "Right. Such functions refers back to recursive functions.",
               ("Right", lambda: [FadeIn(mark, scale=0.6), up(note)]),
               shown="Right. 'Such functions' refers back to recursive functions.")
        self.play(FadeOut(VGroup(card, mark, note)), run_time=0.5)

        card, mark, note = self.pair(4, '"The former is faster; the latter is safer."',
                                     '"C and Java take different approaches."', False,
                                     "'The former' and 'the latter' need the two items named first")
        self.S("C", "s7_04", "Wrong. The former and the latter need the two items named first.",
               ("Wrong", lambda: [FadeIn(mark, scale=0.6), up(note)]),
               shown="Wrong. 'The former' and 'the latter' need the two items named first.")

        self.finish("S07_pairs")

    # ============================ 8. THE COMPLETE ARRANGEMENT FLOW =========

    def full_flow(self):
        self.begin("S08_flow", "The Complete Arrangement Flow", "The arrangement flow")

        board = self.card("Arrangement flow", lines(FLOW, SMALL, 0.28), read=8.0)
        steps = board[1]
        self.N("s8_01", "Five lessons, one flow, and usually only two clues needed to reach the answer.",
               ("flow", lambda: hl(board[0], 1.05)),
               ("two", lambda: [hl(steps[1], 1.02), hl(steps[3], 1.02)]))

        self.finish("S08_flow")

    # ================================================ 9. PAYOFF RECAP ======

    def recap(self):
        self.begin("S09_recap", "Payoff Recap", "Final answers")
        q1, q2 = self.new_q(1), self.new_q(2)
        c1, c2 = chain_1(), chain_2()

        self.T("s9_01", "Final answers.", (None, lambda: self.show_question(q1)), look="ask")
        self.keep(c1)
        self.S("A", "s9_02", "Question one: option A, Q, R, P, T, S. Q opens. R's them refers to rows. P introduces "
                             "the index. T's it refers to the index. S, however, gives the cost.",
               ("option", lambda: [self.yes(q1, "a"), self.no(q1, "bcd")]),
               ("opens", lambda: link(c1, 0)),
               ("rows", lambda: link(c1, 1)),
               ("introduces", lambda: link(c1, 2)),
               (("index", 2), lambda: link(c1, 3)),
               ("cost", lambda: link(c1, 4)), other="happy",
               shown="Question 1: (a) QRPTS. Q opens. R: 'them', the rows. P: the index. T: 'it'. S: the cost.")
        self.show_question(q2)
        self.keep(c2)
        self.S("B", "s9_03", "Question two: option A, P, R, Q. P explains the problem. R introduces two F A. Q's "
                             "this second factor refers to R. Then S six's require it lands on two F A.",
               ("option", lambda: [self.yes(q2, "a"), self.no(q2, "bcd")]),
               ("explains", lambda: [link(c2, 0), link(c2, 1)]),
               ("introduces", lambda: link(c2, 2)),
               ("refers", lambda: link(c2, 3)),
               ("lands", lambda: link(c2, 4)), other="happy",
               shown="Question 2: (a) PRQ. P: the problem. R introduces 2FA. Q: 'this second factor'. S6: 'require it'.")
        self.wipe()
        done = VGroup(text("Lesson 8: Arrangement of Sentences", BODY, INK, BOLD),
                      text("Complete", BODY, GOOD, BOLD)).arrange(DOWN, buff=0.4).move_to(DOWN * 0.6)
        self.play(up(done), run_time=1.2)
        self.countdown(2.0)

        self.finish("S09_recap")

    # ========================================= 10. WHAT COMES NEXT =========

    def next_session(self):
        self.begin("S10_next", "What Comes Next", "What comes next?")

        order = text("Arrangement was about order", BODY).move_to(UP * 0.1)
        gaps = text("Next: gaps, where everything around is a clue", BODY, BROWN, BOLD).move_to(DOWN * 0.8)
        sent = para(['"Although', "the new framework", "promised", "faster builds, in practice"],
                    ['the build times were ________."'], size=LABEL, step=0.6)
        opts = Options(list(zip("abcd", ["negligible", "disappointing", "remarkable", "instantaneous"])), LABEL,
                       across=True)
        board = VGroup(sent, opts).arrange(DOWN, buff=0.7)
        place(board, x=0.0, top=BOARD_TOP - 0.5)
        nxt = self.foot("Next lesson:  Sentence completion", y=-2.7)
        self.fit(order, gaps, board)

        self.N("s10_01", "Arrangement was about order. The next lesson is about gaps: sentences with a word "
                         "missing, where everything around the gap is a clue.",
               ("order", lambda: up(order)),
               ("gaps", lambda: up(gaps)))
        self.wipe()
        self.play(up(sent), up(opts), run_time=1.0)
        self.S("D", "s10_02", "Although and promised. So the result went against the promise.",
               ("Although", lambda: sent[0][0].animate.set_color(BROWN)),
               ("promised", lambda: sent[0][2].animate.set_color(BROWN)), look="think",
               shown="'Although' and 'promised'. So the result went against the promise.")
        self.S("C", "s10_03", "Disappointing.", (None, lambda: opts.right("b")), look="happy")
        self.Q("s10_04", "So you can fill a blank without knowing anything about this framework. How?")
        self.T("s10_05", "Next session. Sentence completion.", (None, lambda: up(nxt)))

        self.the_end("S10_next")

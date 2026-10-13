"""
animation.py for the LMS video generator.

Course : C-CAT Preparation - Section A: English Language and Verbal Ability
Module : 3 Verbal Ability   Lesson : 8 Arrangement of Sentences (Session 15)
Video  : 02 - Understanding Sentence Flow
         (previous: Introduction to arrangement of sentences;  next: Identifying the opening sentence)
Source : C:/Final scripts/Scipts/Lesson 8 - Arrangement of Sentences/02 - Understanding sentence flow.pdf

Note: the questions are practice questions written for the class, not past-paper questions.

Look (3Blue1Brown style): near-black background, white text, one blue and one brown accent; yellow only for a
  passing highlight, green / red only for right / wrong. Latin Modern Roman (Cambria if it is missing).

Roles (the script has no speaker labels; every line was assigned by meaning, and no label is spoken):
  NARRATOR self.N "vijay"   TEACHER self.T / self.Q "aditya"   STUDENTS self.S: A confident "prasad",
  B cautious "kavya", C the second student "ritu", D at the back "student_a".
  Stage directions are the visuals. Board text that the script does not speak (the cards) is shown with a
  thinking bar that gives time to read it.

Sarvam AI voices (settings.json > audio.sarvam.voices, or --speaker VOICE=SPEAKER):
    "vijay": "vijay", "aditya": "aditya", "prasad": "kabir", "kavya": "kavya", "ritu": "ritu", "student_a": "rahul"

The two questions are shown one at a time; the thinking time is split between them.

Section map: S01 Smooth or jumpy?  S02 The topic  S03 How C-CAT tests it  S04 Attempts
  S05 WHAT: the three flow principles  S06 HOW: tracing the thread  S07 WHY: flow is how readers keep up
  S08 Payoff  S09 Summary  S10 What comes next
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
POINTS = ["Given before new", "General before specific", "One thread: definitions before use",
          "Trace a key word from sentence to sentence"]


def make_question(k):
    if k == 1:
        return jumble("Practice question 1", "Arrange the sentences to form a coherent paragraph.",
                      ["A branch is an independent line of development.",
                       "Once the feature is complete, the branch is merged back into the main line.",
                       "Developers create a branch to work on a new feature without disturbing stable code.",
                       "Version control systems like Git let teams work on many changes at once."],
                      ["SPRQ", "PSRQ", "SRPQ", "RSPQ"])
    return jumble("Practice question 2", "The first sentence (1) is fixed. Arrange P, Q, R.",
                  ["Our API response times doubled after the last release.",
                   ["Profiling showed that most of the time was spent in", "a single database query."],
                   ["Adding an index to", "that column", "brought", "response times", "back to normal."],
                   ["That query", "was scanning the entire orders table on every request."]],
                  ["PQR", "PRQ", "RPQ", "QPR"], letters="1PQR")


def principles():
    """The three flow principles, as the script's cards."""
    return stack([family("1.  Given, then new", ["Each sentence starts with something already mentioned (given),"],
                         ["and adds something new, which the next sentence picks up."]),
                  family("2.  General, then specific",
                         ["A broad claim or topic first; then a definition, a detail, an example."],
                         [("Version control  ›  branch  ›  why a branch  ›  after the branch", MUTED)]),
                  family("3.  One topic thread",
                         ["Every sentence connects to the same thread; no sentence floats alone."],
                         ["Definitions come before the terms are used."])])


def reading(y, smooth):
    """Three sentences in a row, and the path of the reader's eye over them."""
    bars = VGroup(*[Rectangle(width=2.6, height=0.4, stroke_color=MUTED, stroke_width=2, fill_color=FILL,
                              fill_opacity=1.0) for _ in range(3)]).arrange(RIGHT, buff=0.5).move_to([1.2, y, 0])
    name = text("Flows" if smooth else "Jumps", LABEL, GOOD if smooth else BAD, BOLD)
    name.next_to(bars, LEFT, buff=0.6)
    if smooth:
        path = VGroup(Arrow(bars.get_left() + UP * 0.5, bars.get_right() + UP * 0.5, buff=0, color=GOOD,
                            stroke_width=4, tip_length=0.2))
    else:
        path = VGroup(*[CurvedArrow(b.get_top() + UP * 0.1, a.get_top() + UP * 0.1, angle=PI / 2, color=BAD,
                                    stroke_width=4, tip_length=0.18) for a, b in zip(bars[:-1], bars[1:])])
    return VGroup(name, bars), path


class UnderstandingSentenceFlow(LMSScene):
    lesson_title = "Understanding Sentence Flow"

    def construct(self):
        self.reset()
        for scene in (self.hook, self.topic, self.exam, self.attempts, self.what, self.how, self.why, self.payoff,
                      self.summary, self.next_session):
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

    # ============================================ 1. SMOOTH OR JUMPY? ======

    def hook(self):
        self.scene_start("S01_hook", title="Smooth or Jumpy?")
        card = self.opening("Understanding Sentence Flow", "Introduction to arrangement of sentences")
        self.heading("Smooth or jumpy?")

        a = para(["Caching reduces", "database load."], ["Redis", "is a popular in-memory store."],
                 ["Many teams use", "it", "as a cache."], size=SMALL, step=0.8)
        b = para(["Redis is a popular", "in-memory store."], ["Many teams use", "it", "as a cache."],
                 ["Caching", "reduces database load."], size=SMALL, step=0.8)
        place(a, left=-EDGE_X + 0.5, top=BOARD_TOP - 0.9)
        place(b, left=0.9, top=BOARD_TOP - 0.9)
        la = text("Paragraph A", SMALL, BLUE, BOLD).next_to(a, UP, buff=0.3, aligned_edge=LEFT)
        lb = text("Paragraph B", SMALL, BLUE, BOLD).next_to(b, UP, buff=0.3, aligned_edge=LEFT)

        def hop(src, dst, color):
            return Arrow(src.get_bottom(), dst.get_top(), buff=0.06, color=color, stroke_width=4, tip_length=0.16)

        jump = hop(a[0][1], a[1][0], BAD)
        no_link = text("no link", MIN_FONT, BAD).next_to(jump, RIGHT, buff=0.15)
        hop1, hop2 = hop(b[0][1], b[1][1], GOOD), hop(b[1][2], b[2][0], GOOD)
        note = text("Each sentence starts with something known, and ends with something new", SMALL, MUTED)
        note.move_to(DOWN * 2.0)
        name = self.foot("The given-new pattern", y=-2.8)
        self.fit(VGroup(la, a), VGroup(lb, b), note)

        self.N("s1_01", "The same three sentences in two orders. Both are grammatical, but only one of them reads "
                        "smoothly.",
               ("three", lambda: [FadeOut(card), up(la), up(a), up(lb), up(b)]))
        self.Q("s1_02", "Read A. Where does it jump?", ("jump", lambda: hl(la, 1.06)))
        self.S("C", "s1_03", "Caching reduces database load. Redis is a popular in-memory store. There. It jumps "
                             "from caching to Redis with no connection.",
               ("There", lambda: [GrowArrow(jump), FadeIn(no_link)]),
               shown="'Caching reduces database load. Redis is ...' There. It jumps from caching to Redis.")
        self.Q("s1_04", "And B?", (None, lambda: hl(lb, 1.06)))
        self.S("B", "s1_05", "Redis is a popular in-memory store. Many teams use it as a cache. Caching reduces "
                             "database load. Each sentence picks up something from the one before. It picks up "
                             "Redis. Caching picks up cache.",
               (("picks", 2), lambda: [GrowArrow(hop1), b[1][1].animate.set_color(GOOD)]),
               (("picks", 3), lambda: [GrowArrow(hop2), b[2][0].animate.set_color(GOOD)]),
               shown="Each sentence picks up something from the one before. 'It': Redis. 'Caching': 'cache'.")
        self.S("D", "s1_06", "So each sentence starts with something we already know and ends with something new. "
                             "The next sentence picks up that new thing.",
               ("starts", lambda: up(note)), look="think",
               shown="So each sentence starts with something we know and ends with something new, which the next picks up.")
        self.T("s1_07", "That's the principle. Linguists call it the given-new pattern.",
               ("Linguists", lambda: up(name)), look="happy")

        self.finish("S01_hook")

    # ================================================== 2. THE TOPIC =======

    def topic(self):
        self.begin("S02_topic", "The Topic", "Sentence flow")
        pts = self.points(["Given before new", "General before specific", "One topic thread throughout"])
        self.T("s2_01", "Before learning individual clues, you need to understand what makes a paragraph flow. "
                        "Three principles cover most of it: given before new, general before specific, and one "
                        "topic thread throughout.",
               *self.reveal(pts, ("given", "general", "thread")))
        self.finish("S02_topic")

    # ======================================== 3. HOW C-CAT TESTS IT ========

    def exam(self):
        self.exam_scene("S03_exam", "s3_01", "Two practice questions, written for this class.", "s3_02",
                        "Sixty seconds.", 60.0)

    # ================================================== 4. ATTEMPTS ========

    def attempts(self):
        self.begin("S04_attempts", "Attempts", "First attempts")
        q1 = self.new_q(1)
        chain = order_chain([("S", "introduces"), ("P", "defines a branch"), ("R", "why: uses the word"),
                             ("Q", "when it is done")])

        self.Q("s4_01", "Question one. Who picked option C, S, R, P, Q?", (None, lambda: self.show_question(q1)),
               shown="Question 1. Who picked (c), SRPQ?")
        self.keep(chain)
        self.S("A", "s4_02", "S is general, about version control. Then R, developers create a branch. Then P "
                             "defines what a branch is.",
               ("general", lambda: self.pick(q1, "c")))
        self.Q("s4_03", "Does that order feel right? You use the word branch in R and then define it in P.",
               ("R", lambda: hl(q1.sent["R"], 1.02)),
               ("define", lambda: hl(q1.sent["P"], 1.02)),
               shown="Does that order feel right? You use the word 'branch' in R, and then define it in P.")
        self.S("A", "s4_04", "That's backwards. You'd define it first, then use it.",
               ("backwards", lambda: self.repick("c")), look="oops")
        self.S("B", "s4_05", "S introduces version control. P defines a branch. R explains why developers create "
                             "one. Q explains what happens when they're done. S, P, R, Q.",
               ("introduces", lambda: link(chain, 0)),
               ("defines", lambda: link(chain, 1)),
               ("why", lambda: link(chain, 2)),
               ("happens", lambda: link(chain, 3)), look="think", other="happy",
               shown="S introduces version control. P defines a branch. R: why. Q: when they're done. SPRQ.")

        self.finish("S04_attempts")

    # =========================== 5. WHAT: THE THREE FLOW PRINCIPLES ========

    def what(self):
        self.begin("S05_what", "WHAT: The Three Flow Principles", "Three flow principles")

        board = self.card(None, principles(), read=7.0)
        f = funnel([("Problem", "Response times doubled"), ("Investigation", "Profiling: one query"),
                    ("Cause", "The query scanned the whole table"), ("Fix", "An index fixed it")])
        name = self.foot("A narrowing funnel", y=-2.9)
        self.fit(f)

        self.S("C", "s5_01", "So in question two, sentence one is the general problem, and the rest narrows it down "
                             "to the specific cause and fix.",
               ("general", lambda: [FadeOut(board), up(f[0])]),
               ("narrows", lambda: LaggedStart(*[up(m) for m in f[1:]], lag_ratio=0.4, run_time=1.8)), look="think",
               shown="So in question 2, sentence 1 is the general problem, and the rest narrows it down.")
        self.T("s5_02", "Exactly. Problem, investigation, cause, fix. That's a narrowing funnel.",
               ("Problem", lambda: hl(f[0][2], 1.1)),
               ("investigation", lambda: hl(f[1][2], 1.1)),
               ("cause", lambda: hl(f[2][2], 1.1)),
               ("fix", lambda: hl(f[3][2], 1.1)),
               ("funnel", lambda: up(name)), look="happy")

        self.finish("S05_what")

    # =================================== 6. HOW: TRACING THE THREAD ========

    def how(self):
        self.begin("S06_how", "HOW: Tracing the Thread", "Tracing the thread")

        th = para([("1.", BLUE, BOLD), "Our API", ("response times", BLUE, BOLD), "doubled after the last release."],
                  [("P.", BLUE, BOLD), "Profiling showed that most of the time was spent in",
                   ("a single database query.", BROWN, BOLD)],
                  [("R.", BLUE, BOLD), ("That query", BROWN, BOLD), "was scanning the entire orders table on every request."],
                  [("Q.", BLUE, BOLD), "Adding an index to", ("that column", BROWN, BOLD), "brought",
                   ("response times", BLUE, BOLD), "back to normal."], size=SMALL, step=0.88)
        place(th, x=0.0, top=BOARD_TOP - 0.2)
        self.fit(th)
        notes = VGroup(*[text(s, MIN_FONT, MUTED).next_to(row, DOWN, buff=0.1, aligned_edge=LEFT)
                         for s, row in zip(("The problem is stated", "A new item is introduced",
                                            "Given: it picks up P.   New: scanning the entire table",
                                            "It picks up the table scan; 'response times' returns to sentence 1"), th)])
        target = self.foot("'That' is a pointer: its target must come before it", y=-3.0)

        self.T("s6_01", "Here's a practical technique. Pick a key word in one sentence and trace where it shows up "
                        "next.",
               ("technique", lambda: LaggedStart(*[up(m) for m in th], lag_ratio=0.3, run_time=2.0)),
               ("trace", lambda: LaggedStart(*[FadeIn(m) for m in notes], lag_ratio=0.3, run_time=2.0)))
        self.countdown(4.0)
        self.S("D", "s6_02", "R has to come right after P, because that query needs P's single database query. And "
                             "Q closes the loop back to response times.",
               ("after", lambda: [hl(th[2][1], 1.08), hl(th[1][2], 1.08)]),
               ("loop", lambda: [hl(th[3][4], 1.08), hl(th[0][2], 1.08)]), look="think",
               shown="R must come right after P: 'that query' needs P's 'single database query'. Q closes the loop.")
        self.T("s6_03", "Right. That is a pointer, and pointers need a target that comes before them.",
               ("pointer", lambda: up(target)), look="happy")

        self.finish("S06_how")

    # ========================= 7. WHY: FLOW IS HOW READERS KEEP UP =========

    def why(self):
        self.begin("S07_why", "WHY: Flow Is How Readers Keep Up", "How readers keep up")

        smooth, straight = reading(0.3, True)
        jumpy, loops = reading(-1.3, False)
        reread = text("reread", MIN_FONT, BAD).next_to(loops, UP, buff=0.1)
        tool = self.foot("Given, then new: for clear writing, and for para jumbles", y=-2.8)
        self.fit(VGroup(smooth, straight), VGroup(jumpy, loops, reread))

        self.T("s7_01", "When a paragraph flows, readers don't have to go back. When it jumps, they reread, lose "
                        "track and lose trust. The given-new pattern is one of the most reliable tools for clear "
                        "technical writing, and it's also the main tool for solving para jumbles.",
               ("flows", lambda: [up(smooth), GrowArrow(straight[0])]),
               ("jumps", lambda: up(jumpy)),
               ("reread", lambda: [LaggedStart(*[Create(m) for m in loops], lag_ratio=0.4, run_time=1.2),
                                   FadeIn(reread)]),
               ("reliable", lambda: up(tool)))

        self.finish("S07_why")

    # ============================ 8. PAYOFF: SOLVING BOTH QUESTIONS ========

    def payoff(self):
        self.begin("S08_payoff", "Payoff: Solving Both Questions", "Solving both questions")
        q1, q2 = self.new_q(1), self.new_q(2)
        c1 = order_chain([("S", "general"), ("P", "definition"), ("R", "purpose"), ("Q", "completion")])
        c2 = order_chain([("1", "the problem"), ("P", "the investigation"), ("R", "the cause: that query"),
                          ("Q", "the fix: that column")])

        self.ask_q("s8_01", "Question one.", q1)
        self.keep(c1)
        self.S("B", "s8_02", "General to specific: S introduces version control. Definition before use: P defines "
                             "branch before R uses it. Then Q, once the feature is complete, comes last. S, P, R, "
                             "Q, option A. Option B opens with a definition that has no context. Option C uses "
                             "branch before defining it. Option D opens with R, which uses an undefined term.",
               ("General", lambda: link(c1, 0)),
               ("Definition", lambda: link(c1, 1)),
               ("uses", lambda: link(c1, 2)),
               ("last", lambda: link(c1, 3)),
               ("option", lambda: self.yes(q1, "a")),
               (("Option", 2), lambda: self.no(q1, "b")),
               (("Option", 3), lambda: self.no(q1, "c")),
               (("Option", 4), lambda: self.no(q1, "d")),
               shown="General to specific: S. Definition before use: P before R. Then Q comes last. SPRQ: (a).",
               look="think", other="happy")

        self.ask_q("s8_03", "Question two.", q2)
        self.keep(c2)
        self.S("C", "s8_04", "Sentence one is the problem. P is the investigation and introduces a single database "
                             "query. R, that query, picks it up and gives the cause. Q, that column and index, is "
                             "the fix. So one, P, R, Q, option B.",
               ("problem", lambda: link(c2, 0)),
               ("investigation", lambda: [link(c2, 1), hl(q2.sent["P"][2], 1.06)]),
               ("cause", lambda: [link(c2, 2), hl(q2.sent["R"][1], 1.06)]),
               ("fix", lambda: [link(c2, 3), hl(q2.sent["Q"][2], 1.06)]),
               ("option", lambda: self.yes(q2, "b")),
               shown="1: the problem. P: the investigation. R, 'that query': the cause. Q: the fix. 1-P-R-Q: (b).",
               look="think", other="happy")

        self.finish("S08_payoff")

    # ================================================== 9. SUMMARY =========

    def summary(self):
        self.summary_scene("S09_summary", "D", "s9_01", "s9_02",
                           "Given before new. General before specific. One thread, with definitions before use. "
                           "Trace a key word from sentence to sentence.",
                           POINTS, ("Given", "General", "thread", "Trace"), size=BODY)

    # ========================================= 10. WHAT COMES NEXT =========

    def next_session(self):
        self.begin("S10_next", "What Comes Next", "What comes next?")

        first = text("Every paragraph needs a first sentence", BODY).move_to(UP * 0.1)
        half = text("The right one can remove half the options", BODY, BROWN, BOLD).move_to(DOWN * 0.8)
        four = para([("P.", BLUE, BOLD), "However,", "it also introduces new failure modes."],
                    [("Q.", BLUE, BOLD), "Microservices architecture splits an application into small services."],
                    [("R.", BLUE, BOLD), "This", "makes each service easier to deploy independently."],
                    [("S.", BLUE, BOLD), "For example, a network call can fail where a function call never would."],
                    size=SMALL, step=0.6)
        place(four, x=0.0, top=BOARD_TOP - 0.4)
        cannot = text("Can't start", SMALL, BAD, BOLD).move_to(DOWN * 1.9)
        nxt = self.foot("Next session:  Identifying the opening sentence", y=-2.8)
        self.fit(first, half, four)

        self.N("s10_01", "Every paragraph needs a first sentence. Choosing it correctly often eliminates half the "
                         "options in one move.",
               ("first", lambda: up(first)),
               ("half", lambda: up(half)))
        self.wipe()
        self.Q("s10_02", "Which one opens the paragraph? And which can never open it?",
               (None, lambda: LaggedStart(*[up(m) for m in four], lag_ratio=0.3, run_time=1.8)),
               ("never", lambda: [four[0][1].animate.set_color(BAD), four[2][1].animate.set_color(BAD),
                                  FadeIn(cannot), hl(four[1], 1.02, GOOD)]), other="happy")
        self.T("s10_03", "Next session.", (None, lambda: up(nxt)))

        self.the_end("S10_next")

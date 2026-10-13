"""
animation.py for the LMS video generator.

Course : C-CAT Preparation - Section A: English Language and Verbal Ability
Module : 3 Verbal Ability   Lesson : 8 Arrangement of Sentences (Session 16)
Video  : 06 - Connector-Based Arrangement
         (previous: Pronoun and reference clues;  next: Logical sequencing)
Source : C:/Final scripts/Scipts/Lesson 8 - Arrangement of Sentences/06 - Connector-based arrangement.pdf

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
"O(1)" is spoken as "O of one".

Section map: S01 Every connector points backwards  S02 The topic  S03 How C-CAT tests it  S04 Attempts
  S05 WHAT: connector families  S06 HOW: connectors as mandatory pairs
  S07 HOW: contrast words inside sentences  S08 WHY: connectors are logic gates  S09 Payoff  S10 Summary
  S11 What comes next
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
FAMILIES = [["Family", "Connectors", "Needs before it"],
            ["Addition", "also, moreover, furthermore, in addition", "A point going the same way"],
            ["Contrast", "however, but, yet, on the other hand,", "An opposing point"],
            ["", "nevertheless, whereas", ""],
            ["Cause to effect", "therefore, thus, hence, as a result,", "A cause"],
            ["", "consequently, so", ""],
            ["Example", "for example, for instance, such as", "A general claim"],
            ["Clarification", "in other words, that is, namely", "A statement to restate"],
            ["Sequence", "first, then, next, after that, finally", "An earlier step"],
            ["Conclusion", "in short, in conclusion, overall", "The whole argument"]]
METHOD = ["1.  Circle every connector at the start of a sentence",
          "2.  For each, name what it needs before it: a cause, an opposite, a claim",
          "3.  Find the sentence that supplies it: a mandatory pair",
          "4.  Test the pair in both directions: does it make sense only in that order?",
          "5.  Eliminate options that break any pair"]
POINTS = ["Every connector expects something before it", "A cause, an opposite, a claim or a step",
          "Circle the connectors; find what they need", "Test each pair in both directions"]


def make_question(k):
    if k == 1:
        return jumble("Practice question 1", "Arrange the sentences to form a coherent paragraph.",
                      [["However,", "they consume more memory than simpler structures."],
                       "Hash tables offer average-case O(1) lookups.",
                       ["For example,", "a table may reserve many empty slots to keep collisions rare."],
                       ["As a result,", "they are popular for caches and symbol tables."]],
                      ["QSPR", "QPRS", "QPSR", "QRSP"])
    return jumble("Practice question 2", "The first sentence (1) is fixed. Arrange P, Q, R.",
                  ["Unit tests check individual functions in isolation.",
                   ["In other words,", "they verify that the pieces work together."],
                   ["Integration tests,", "on the other hand,", "check how components interact."],
                   ["Both kinds", "are needed for reliable software."]],
                  ["QPR", "PQR", "RQP", "QRP"], letters="1PQR")


class ConnectorBasedArrangement(LMSScene):
    lesson_title = "Connector-Based Arrangement"

    def construct(self):
        self.reset()
        for scene in (self.hook, self.topic, self.exam, self.attempts, self.what, self.how, self.inside,
                      self.why, self.payoff, self.summary, self.next_session):
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

    # ========================= 1. EVERY CONNECTOR POINTS BACKWARDS =========

    def hook(self):
        self.scene_start("S01_hook", title="Every Connector Points Backwards")
        card = self.opening("Connector-Based Arrangement", "Pronoun and reference clues")
        self.heading("Connectors point back")

        four = para([("P.", BLUE, BOLD), "However,", "they consume more memory."],
                    [("Q.", BLUE, BOLD), "Hash tables offer average O(1) lookups."],
                    [("R.", BLUE, BOLD), "For example,", "a table of a million entries may reserve extra empty slots."],
                    [("S.", BLUE, BOLD), "As a result,", "they are popular for caches and symbol tables."],
                    size=SMALL, step=0.8)
        place(four, x=0.0, top=BOARD_TOP - 0.3)
        self.fit(four)
        p, q, r, s = four

        def needs(row, note):
            return text(note, MIN_FONT, BROWN).next_to(row, DOWN, buff=0.1, aligned_edge=LEFT)

        tag_p = needs(p, "Needs: something positive to contrast with")
        tag_s = needs(s, "Needs: a cause   (Q: fast lookups)")
        tag_r = needs(r, "Needs: a claim to illustrate   (P: more memory)")
        chain = order_chain([("Q", "fast lookups"), ("S", "as a result"), ("P", "however"), ("R", "for example")], y=-3.0)

        self.N("s1_01", "A pronoun tells you what came before. A connector tells you how the next sentence relates "
                        "to it.",
               ("connector", lambda: [FadeOut(card), LaggedStart(*[up(m) for m in four], lag_ratio=0.3)]))
        self.Q("s1_02", "However, they consume more memory. What must come right before a however?",
               ("before", lambda: hl(p[1], 1.1)),
               shown="'However, they consume more memory.' What must come right before a 'however'?")
        self.S("A", "s1_03", "Something positive. However contrasts with it.",
               ("positive", lambda: [p[1].animate.set_color(BROWN), FadeIn(tag_p)]),
               shown="Something positive. 'However' contrasts with it.")
        self.Q("s1_04", "S: As a result, they're popular for caches.", (None, lambda: hl(s[1], 1.1)),
               shown="S: 'As a result, they're popular for caches.'")
        self.S("B", "s1_05", "A cause. Something that makes them popular. That's Q, O of one lookups.",
               ("cause", lambda: [s[1].animate.set_color(BROWN), FadeIn(tag_s)]),
               ("lookups", lambda: hl(q, 1.03)), look="think",
               shown="A cause. Something that makes them popular. That's Q: O(1) lookups.")
        self.Q("s1_06", "R: For example, a table of a million entries may reserve extra empty slots.",
               (None, lambda: hl(r[1], 1.1)),
               shown="R: 'For example, a table of a million entries may reserve extra empty slots.'")
        self.S("D", "s1_07", "An example of something. Of what? Of using more memory. So R follows P.",
               ("memory", lambda: [r[1].animate.set_color(BROWN), FadeIn(tag_r)]))
        self.S("C", "s1_08", "Q, fast lookups. S, as a result, popular. P, however, more memory. R, for example, "
                             "empty slots. Q, S, P, R.",
               ("fast", lambda: link(chain, 0)),
               ("popular", lambda: link(chain, 1)),
               ("however", lambda: link(chain, 2)),
               ("example", lambda: link(chain, 3)), other="happy",
               shown="Q, fast lookups. S, as a result, popular. P, however, more memory. R, for example. QSPR.")

        self.finish("S01_hook")

    # ================================================== 2. THE TOPIC =======

    def topic(self):
        self.begin("S02_topic", "The Topic", "Connectors")
        pts = self.points(["Connectors = transition words", "They mark the logical relationship between sentences",
                           "Each type expects a kind of sentence before it",
                           "Read the connector: you know what to look for"])
        self.T("s2_01", "Connectors, also called transition words, mark the logical relationship between "
                        "sentences. Each type expects a particular kind of sentence before it. Read the connector "
                        "and you know what to look for.",
               *self.reveal(pts, ("transition", "relationship", "expects", "Read")))
        self.finish("S02_topic")

    # ======================================== 3. HOW C-CAT TESTS IT ========

    def exam(self):
        self.exam_scene("S03_exam", "s3_01", "Two practice questions, written for this class.", "s3_02",
                        "Sixty seconds.", 60.0)

    # ================================================== 4. ATTEMPTS ========

    def attempts(self):
        self.begin("S04_attempts", "Attempts", "First attempts")
        q1, q2 = self.new_q(1), self.new_q(2)
        chain = order_chain([("1", "unit tests"), ("Q", "on the other hand"), ("P", "in other words"),
                             ("R", "both kinds")])

        self.Q("s4_01", "Question one. Someone defend option B, Q, P, R, S.", (None, lambda: self.show_question(q1)),
               shown="Question 1. Someone defend (b), QPRS.")
        self.S("C", "s4_02", "Q, the benefit. P, however, the cost. R, an example of the cost. Then S, as a result, "
                             "popular.",
               ("benefit", lambda: self.pick(q1, "b")))
        self.Q("s4_03", "What is S the result of in that order?", ("result", lambda: hl(q1.sent["S"][1], 1.1)))
        self.S("C", "s4_04", "Of using a lot of memory. As a result of using more memory, they're popular. That "
                             "doesn't make sense.",
               ("sense", lambda: [self.repick("b"), self.tag(q1, "b", "A drawback can't cause popularity", BAD)]),
               look="oops",
               shown="Of using a lot of memory. 'As a result of using more memory, they're popular.' No sense.")
        self.S("B", "s4_05", "So as a result has to follow a cause that makes sense, which is fast lookups.",
               ("cause", lambda: hl(q1.sent["Q"], 1.02)), look="think",
               shown="So 'as a result' has to follow a cause that makes sense, which is fast lookups.")
        self.Q("s4_06", "Question two?", (None, lambda: self.show_question(q2)), shown="Question 2?")
        self.keep(chain)
        self.S("D", "s4_07", "Q contrasts with sentence one, on the other hand. P, in other words, restates Q: "
                             "interaction means the pieces working together. R, both kinds, needs two types "
                             "already mentioned. One, Q, P, R.",
               ("contrasts", lambda: [link(chain, 0), link(chain, 1), hl(q2.sent["Q"][2], 1.08)]),
               ("restates", lambda: [link(chain, 2), hl(q2.sent["P"][1], 1.08)]),
               ("needs", lambda: [link(chain, 3), hl(q2.sent["R"][1], 1.08)]), look="think", other="happy",
               shown="Q contrasts with sentence 1: 'on the other hand'. P restates Q. R: 'both kinds'. 1-Q-P-R.")

        self.finish("S04_attempts")

    # ================================== 5. WHAT: CONNECTOR FAMILIES ========

    def what(self):
        self.begin("S05_what", "WHAT: Connector Families", "Connector families")

        g = Grid(FAMILIES, (2.5, 6.3, 4.4), size=MIN_FONT, row_h=0.42,
                 styles=[(BLUE, BOLD), (INK, NORMAL), (BROWN, NORMAL)])
        self.card(None, g, read=8.0)

        self.S("A", "s5_01", "So when I see however, I look for the sentence it's arguing against.",
               ("however", lambda: [hl(g.row(2), 1.02), hl(g.row(3), 1.02)]), look="think",
               shown="So when I see 'however', I look for the sentence it's arguing against.")
        self.T("s5_02", "Exactly. And with moreover, you look for a sentence going in the same direction. That's "
                        "often how you tell apart two sentences that both look like they could come next.",
               ("moreover", lambda: hl(g.row(1), 1.02)), look="happy")

        self.finish("S05_what")

    # ==================== 6. HOW: CONNECTORS AS MANDATORY PAIRS ============

    def how(self):
        self.begin("S06_how", "HOW: Connectors as Mandatory Pairs", "Mandatory pairs")

        board = self.card("Connector pairing method", lines(METHOD, SMALL, 0.36), read=7.0)
        ok = phrase(text("Q, then S:", LABEL, BLUE, BOLD), text("Fast lookups.  As a result, popular.", LABEL, GOOD),
                    tick(0.26), buff=0.3)
        bad = phrase(text("S, then Q:", LABEL, BLUE, BOLD), text("Popular.  As a result, fast lookups.", LABEL, BAD),
                     cross(0.26), buff=0.3)
        both = column(ok, bad, buff=0.7)
        place(both, x=0.0, y=0.0)
        why_not = text("Effect before cause", SMALL, BAD).next_to(bad, DOWN, buff=0.15)
        proof = self.foot("The direction proves the pair", y=-2.6)
        self.fit(both)

        self.S("B", "s6_01", "Test both directions?", (None, lambda: hl(board[1][3], 1.03)), look="confused")
        self.T("s6_02", "Yes. Q, as a result S, makes sense. S, as a result Q, doesn't. The direction proves the "
                        "pair.",
               (None, lambda: FadeOut(board)),
               ("sense", lambda: up(ok)),
               (("result", 2), lambda: [up(bad), FadeIn(why_not)]),
               ("direction", lambda: up(proof)))

        self.finish("S06_how")

    # =================== 7. HOW: CONTRAST WORDS INSIDE SENTENCES ===========

    def inside(self):
        self.begin("S07_inside", "HOW: Contrast Words Inside Sentences", "Inside the sentence")

        var = para([("P.", BLUE, BOLD), "Python is easy to read and quick to write."],
                   [("Q.", BLUE, BOLD), "C,", "by contrast,", "gives the programmer direct control over memory."],
                   [("R.", BLUE, BOLD), "This control", "comes at the cost of more complex code."],
                   size=LABEL, step=0.65)
        place(var, x=0.0, top=BOARD_TOP - 0.3)
        chain = order_chain([("P", "Python"), ("Q", "by contrast"), ("R", "this control")], y=-1.6, gap=0.5)
        where = self.foot("Connectors can sit in the middle: look anywhere in the sentence", y=-2.9)
        self.fit(var)

        self.play(LaggedStart(*[up(m) for m in var], lag_ratio=0.3), run_time=1.5)
        self.S("C", "s7_01", "By contrast is in the middle of Q, not at the start. But it still means Q contrasts "
                             "with something before it. So P, then Q. R, this control, follows Q. P, Q, R.",
               ("middle", lambda: var[1][2].animate.set_color(BROWN)),
               ("then", lambda: [link(chain, 0), link(chain, 1)]),
               ("follows", lambda: [link(chain, 2), var[2][1].animate.set_color(BROWN)]), look="think", other="happy",
               shown="'By contrast' is in the middle of Q. It still contrasts with something before it. PQR.")
        self.T("s7_02", "Right. Connectors aren't always at the start. On the other hand, by contrast, however and "
                        "too can sit in the middle. Look for them anywhere in the sentence.",
               ("middle", lambda: up(where)))

        self.finish("S07_inside")

    # ======================== 8. WHY: CONNECTORS ARE LOGIC GATES ===========

    def why(self):
        self.begin("S08_why", "WHY: Connectors Are Logic Gates", "Logic gates")

        g = Grid([["however", "The logic turns: an opposite point"], ["therefore", "A consequence follows"],
                  ["moreover", "The same direction: one more point"]], (3.0, 8.0), size=BODY, row_h=0.95, header=False,
                 styles=[(BLUE, BOLD), (INK, NORMAL)])
        place(g, x=0.0, top=BOARD_TOP - 0.5)
        test = self.foot("Arrangement questions test whether you can read these signals", y=-2.7)
        self.fit(g)

        self.T("s8_01", "Connectors tell the reader which way the logic is going. In technical writing, a missing "
                        "however can make two contradictory claims look like a single argument. A wrong therefore "
                        "claims a cause that doesn't exist. Arrangement questions test whether you can read these "
                        "signals.",
               ("way", lambda: LaggedStart(*[up(g.row(k)) for k in range(3)], lag_ratio=0.4, run_time=1.8)),
               ("however", lambda: hl(g.row(0), 1.04)),
               ("therefore", lambda: hl(g.row(1), 1.04)),
               ("signals", lambda: up(test)))

        self.finish("S08_why")

    # ============================ 9. PAYOFF: SOLVING BOTH QUESTIONS ========

    def payoff(self):
        self.begin("S09_payoff", "Payoff: Solving Both Questions", "Solving both questions")
        q1, q2 = self.new_q(1), self.new_q(2)
        c1 = order_chain([("Q", "opens"), ("S", "as a result"), ("P", "however"), ("R", "for example")])
        c2 = order_chain([("1", "unit tests"), ("Q", "on the other hand"), ("P", "in other words"),
                          ("R", "both kinds")])

        self.ask_q("s9_01", "Question one.", q1)
        self.keep(c1)
        self.S("A", "s9_02", "Q opens. As a result needs a sensible cause, fast lookups, so Q then S. However "
                             "contrasts with the benefits, so P comes after S. For example illustrates the memory "
                             "cost, so R follows P. Q, S, P, R, option A.",
               ("opens", lambda: link(c1, 0)),
               ("cause", lambda: [link(c1, 1), hl(q1.sent["S"][1], 1.08)]),
               ("contrasts", lambda: [link(c1, 2), hl(q1.sent["P"][1], 1.08)]),
               ("illustrates", lambda: [link(c1, 3), hl(q1.sent["R"][1], 1.08)]),
               ("option", lambda: [self.yes(q1, "a"), self.no(q1, "bcd")]),
               shown="Q opens. 'As a result' needs a cause: Q, S. 'However': P. 'For example': R. QSPR: (a).",
               look="think", other="happy")

        self.ask_q("s9_03", "Question two.", q2)
        self.keep(c2)
        self.S("B", "s9_04", "On the other hand contrasts integration tests with sentence one's unit tests, so Q "
                             "comes first. In other words restates Q, so P follows. Both kinds needs two kinds "
                             "already mentioned, so R comes last. One, Q, P, R, option A.",
               ("contrasts", lambda: [link(c2, 0), link(c2, 1), hl(q2.sent["Q"][2], 1.08)]),
               ("restates", lambda: [link(c2, 2), hl(q2.sent["P"][1], 1.08)]),
               ("needs", lambda: [link(c2, 3), hl(q2.sent["R"][1], 1.08)]),
               ("option", lambda: [self.yes(q2, "a"), self.no(q2, "bcd")]),
               shown="'On the other hand': Q first. 'In other words' restates Q: P. 'Both kinds': R. 1-Q-P-R: (a).",
               look="think", other="happy")

        self.finish("S09_payoff")

    # ================================================= 10. SUMMARY =========

    def summary(self):
        self.summary_scene("S10_summary", "D", "s10_01", "s10_02",
                           "Every connector expects something before it: a cause, an opposite, a claim or a step. "
                           "Circle the connectors, find what they need, and test each pair in both directions.",
                           POINTS, ("expects", "cause", "Circle", "test"), size=BODY,
                           shown="Every connector expects something before it: a cause, an opposite, a claim or a step.")

    # ========================================= 11. WHAT COMES NEXT =========

    def next_session(self):
        self.begin("S11_next", "What Comes Next", "What comes next?")

        tools = text("Openers, closers, pronouns, connectors", BODY).move_to(UP * 0.1)
        none = text("And when there are no signal words at all?", BODY, BROWN, BOLD).move_to(DOWN * 0.8)
        four = para([("P.", BLUE, BOLD), "The compiler translates the source code into object code."],
                    [("Q.", BLUE, BOLD), "The programmer writes the source code in a text editor."],
                    [("R.", BLUE, BOLD), "The linker combines object files into an executable."],
                    [("S.", BLUE, BOLD), "The operating system loads the executable into memory and runs it."],
                    size=SMALL, step=0.65)
        place(four, x=0.0, top=BOARD_TOP - 0.4)
        nxt = self.foot("Next session:  Logical sequencing", y=-2.7)
        self.fit(tools, none, four)

        self.N("s11_01", "Openers, closers, pronouns, connectors. But some para jumbles have no signal words at "
                         "all. The sentences can only be ordered by the logic of the content.",
               ("connectors", lambda: up(tools)),
               ("signal", lambda: up(none)))
        self.wipe()
        self.play(LaggedStart(*[up(m) for m in four], lag_ratio=0.3), run_time=1.8)
        self.S("C", "s11_02", "No however, no this, no therefore. Just steps.", look="confused",
               shown="No 'however', no 'this', no 'therefore'. Just steps.")
        self.Q("s11_03", "So how do you order them? And how sure can you be?", ("sure", lambda: hl(four, 1.02)))
        self.T("s11_04", "Next session.", (None, lambda: up(nxt)))

        self.the_end("S11_next")

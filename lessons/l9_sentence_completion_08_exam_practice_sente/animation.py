"""
animation.py for the LMS video generator.

Course : C-CAT Preparation - Section A: English Language and Verbal Ability
Module : 3 Verbal Ability   Lesson : 9 Sentence Completion (Session 17)
Video  : 08 - Exam Practice: Fill in the Blanks, Sentence Fillers and Cloze Test
         (previous: Elimination techniques;  next: Module 4, Lesson 10, Reading comprehension)
Source : C:/Final scripts/Scipts/Lesson 9 - Sentence Completion/08 - Exam practice.pdf

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

The two main questions are shown one at a time; the two minutes are split between them.
Scene 7 (the flow card) has no spoken line in the script: it is shown with a reading bar.

Section map: S01 Three formats  S02 The topic  S03 The two main questions  S04 Question 1: sentence filler
  S05 Question 2: the cloze passage  S06 Rapid-fire round  S07 The sentence-completion flow
  S08 Why this skill transfers  S09 Payoff recap  S10 What comes next
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


def slot(n=8):
    """The blank of a sentence-completion question (long enough for an ``n``-letter answer)."""
    return "_" * n


def blank_question(label, rows, options, across=True, size=LABEL):
    """A sentence-completion question: the sentence (rows of pieces, see ``para``) and four options.

    ``q.blanks`` are the blank pieces, in reading order. Short options go in a row; long ones under each other."""
    q = Question(label, rows, list(zip("abcd", options)), size, across=across)
    q.blanks = [q.body[i][j] for i, row in enumerate(rows) for j, part in enumerate(row)
                if (part if isinstance(part, str) else part[0]).strip("_") == ""]
    return place(q, left=-EDGE_X + 0.3, top=BOARD_TOP - 0.1)


def fill(blank, word, size=LABEL, color=GOOD):
    """The word that goes into a blank: written on the blank's line."""
    mob = text(word, size, color, BOLD)
    if mob.width > blank.width:
        mob.scale(blank.width / mob.width)
    return mob.next_to(blank, UP, buff=0.05)


def tone_scale(names, y=-1.5, spread=1.3):
    """Words from one end of a scale to the other, on a line, with a needle: ``scale.words``, ``scale.needle``."""
    words = VGroup(*[text(s, LABEL) for s in names]).arrange(RIGHT, buff=spread).move_to(UP * y)
    bar = Line(words.get_left(), words.get_right()).next_to(words, DOWN, buff=0.25)
    bar.set_stroke(color=[GOOD, BAD], width=6)
    needle = Triangle(color=FLASH, fill_opacity=1.0, stroke_width=0).scale(0.14).rotate(PI)
    needle.next_to(words[0], UP, buff=0.15)
    scale = VGroup(words, bar, needle)
    scale.words, scale.needle = words, needle
    return scale


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

CRUMB = "C-CAT Preparation  ›  English  ›  Verbal Ability  ›  Sentence Completion"
FORMATS = [("Fill in the blanks", "One or two words"), ("Sentence fillers", "A phrase or a clause"),
           ("Cloze test", "A passage: linked blanks")]
CHOICES = [["(1)", "(a)  despite", "(b)  instead of", "(c)  because of", "(d)  as well as"],
           ["(2)", "(a)  raises", "(b)  reduces", "(c)  hides", "(d)  delays"],
           ["(3)", "(a)  so", "(b)  and", "(c)  but", "(d)  because"],
           ["(4)", "(a)  optional", "(b)  essential", "(c)  impossible", "(d)  expensive"]]
FLOW = ["1.  Read the whole sentence or passage first   (cloze: get the gist)",
        "2.  Predict the blank in plain words",
        "3.  Filter:  grammar  ›  direction  ›  degree  ›  aspect  ›  collocation",
        "4.  Double blank: the easier blank first",
        "5.  Sentence filler: the phrase must fit the meaning and attach to the subject",
        "6.  Cloze: use later blanks to confirm earlier ones"]
# the rapid round: (sentence pieces, options)
RAPID = {3: ([['"The API returned', "an", slot(10), "error code that wasn't"], ['in the documentation."']],
             ["unexpected", "strange", "weird", "sudden"]),
         4: ([['"Despite', "months of testing, the release still", slot(9), 'several critical bugs."']],
             ["eliminated", "contained", "prevented", "fixed"]),
         5: ([['"The fix was', slot(8), ":", 'a single line changed, and the crash disappeared."']],
             ["elaborate", "trivial", "costly", "risky"]),
         6: ([['"Logs should be rotated regularly;', slot(10), ","], ['they will eventually fill the disk."']],
             ["therefore", "moreover", "otherwise", "similarly"])}


def cloze():
    """The cloze question: the passage with four numbered blanks, and a row of options for each blank.

    ``q.blanks`` are the blanks, ``q.grid`` the options (row = blank, column 1 to 4 = (a) to (d))."""
    label = text("Practice question 2  (cloze test)", SMALL, MUTED, BOLD)
    passage = para(['"Cloud computing lets companies rent computing power', "(1) ________", "buying"],
                   ["their own servers. This", "(2) ________", "upfront costs,", "(3) ________", "it can become"],
                   ["expensive if resources are left running. Careful monitoring is"],
                   ["therefore", "(4) ________", '."'], size=SMALL, step=0.44)
    grid = Grid(CHOICES, (1.0, 2.8, 2.8, 2.8, 2.8), size=SMALL, row_h=0.45, header=False,
                styles=[(BLUE, BOLD)] + [(INK, NORMAL)] * 4)
    q = VGroup(label, passage, grid).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
    q.passage, q.grid = passage, grid
    q.blanks = [passage[0][1], passage[1][1], passage[1][3], passage[3][1]]
    return place(q, left=-EDGE_X + 0.3, top=BOARD_TOP - 0.1)


def make_question(k):
    if k == 1:
        return sentence_question("Practice question 1  (sentence filler)",
                                 [['"', slot(18), ",", "the team", "decided to postpone the release until the"],
                                  ["security audit was complete", '."']],
                                 ["Despite the audit being finished", "Concerned about the unresolved vulnerabilities",
                                  "Because the release was already live", "Having deployed the release yesterday"])
    if k == 2:
        return cloze()
    rows, options = RAPID[k]
    return blank_question(f"Rapid {k - 2}", rows, options)


def panel(title, sub, x):
    box = Rectangle(width=3.9, height=1.7, stroke_color=BLUE, stroke_width=3, fill_color=FILL, fill_opacity=1.0)
    box.move_to([x, 0.1, 0])
    head = fit_w(text(title, LABEL, INK, BOLD), 3.5).move_to(box).shift(UP * 0.35)
    note = fit_w(text(sub, SMALL, MUTED), 3.5).move_to(box).shift(DOWN * 0.35)
    return VGroup(box, head, note)


def chain_of(*steps):
    """Steps joined by small arrows, on one line."""
    parts = []
    for k, s in enumerate(steps):
        parts += ([small_arrow(MUTED, 0.5)] if k else []) + [text(s, LABEL)]
    return fit_w(VGroup(*parts).arrange(RIGHT, buff=0.25), 2 * EDGE_X - 0.6)


class ExamPracticeSentenceCompletion(LMSScene):
    lesson_title = "Exam Practice: Sentence Completion"

    def construct(self):
        self.reset()
        for scene in (self.hook, self.topic, self.exam, self.filler, self.passage, self.rapid, self.full_flow,
                      self.transfer, self.recap, self.next_session):
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

    def fill_in(self, q, word, k=0):
        """The answer goes into blank ``k`` of the question on the board."""
        return FadeIn(self.keep(fill(q.blanks[k], word)), shift=UP * 0.1)

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

    def answer(self, q, k, col, word):
        """Cloze: blank ``k`` takes ``word``, and the chosen option turns green."""
        blank = q.blanks[k]
        mob = self.keep(fit_w(text(word, SMALL, GOOD, BOLD), blank.width).move_to(blank))
        return [blank.animate.set_opacity(0.0), FadeIn(mob), q.grid.cell(k, col).animate.set_color(GOOD)]

    # ============================================== 1. THREE FORMATS =======

    def hook(self):
        self.scene_start("S01_hook", title="Three Formats")
        card = self.opening("Exam Practice: Sentence Completion", "Elimination techniques")
        self.heading("Three formats")

        panels = [panel(title, sub, x) for (title, sub), x in zip(FORMATS, (-4.3, 0.0, 4.3))]
        once = text("Cloze: read the whole passage once, before filling anything", LABEL, BLUE).move_to(DOWN * 1.7)
        method = self.foot("Predict,   filter,   match", y=-2.8)
        self.fit(once)

        self.N("s1_01", "One skill, three formats. Today the class tests the sentence-completion toolkit on every "
                        "format the exam might use.",
               ("three", lambda: [FadeOut(card), LaggedStart(*[FadeIn(VGroup(p[0], p[1])) for p in panels],
                                                             lag_ratio=0.3)]))
        self.T("s1_02", "Fill in the blanks you know: one or two words. Sentence fillers give you a phrase or a "
                        "clause for the blank. And the cloze test gives you a passage with several blanks that "
                        "depend on each other. The method doesn't change. Predict, filter, match.",
               ("words", lambda: FadeIn(panels[0][2])),
               ("phrase", lambda: FadeIn(panels[1][2])),
               ("passage", lambda: FadeIn(panels[2][2])),
               ("Predict", lambda: up(method)))
        self.S("B", "s1_03", "Does the cloze test take longer?", look="ask")
        self.T("s1_04", "More reading, but each blank is usually simpler, because the passage gives you lots of "
                        "context. The trick is to read the whole passage once before filling anything.",
               ("trick", lambda: [hl(panels[2], 1.03), up(once)]))

        self.finish("S01_hook")

    # ================================================== 2. THE TOPIC =======

    def topic(self):
        self.begin("S02_topic", "The Topic", "Today's practice")
        pts = self.points(["One sentence-filler question", "One full cloze passage", "A rapid round of single blanks"])
        self.T("s2_01", "One sentence-filler question, one full cloze passage, then a rapid round of single "
                        "blanks.",
               *self.reveal(pts, ("question", "passage", "rapid")))
        self.finish("S02_topic")

    # ====================================== 3. THE TWO MAIN QUESTIONS ======

    def exam(self):
        self.begin("S03_exam", "The Two Main Questions", "The two main questions")
        self.q1, self.q2 = self.new_q(1), self.new_q(2)
        self.N("s3_01", "Both are practice questions written for this class.",
               ("practice", lambda: self.show_question(self.q1)))
        self.timed("s3_02", "Two minutes for both.", self.q2, 120.0)
        self.scene_end("S03_exam")              # a question stays on the board for the next scene

    # ================================ 4. QUESTION 1: SENTENCE FILLER =======

    def filler(self):
        self.begin("S04_filler", "Question 1: Sentence Filler", "The sentence filler")
        q1 = self.new_q(1)
        team, audit = q1.body[0][3], q1.body[1][0]

        self.Q("s4_01", "Question one. A sentence filler. What's the blank's job?",
               (None, lambda: self.show_question(q1)),
               shown="Question 1. A sentence filler. What's the blank's job?")
        self.S("D", "s4_02", "It gives the reason for postponing. So it has to be something that would make you "
                             "delay a release until an audit is done.",
               ("reason", lambda: hl(q1.body[0][1], 1.04)), look="think",
               shown="It gives the reason for postponing: something that would make you delay a release.")
        self.T("s4_03", "Filter.", look="ask")
        self.S("C", "s4_04", "Option A: despite the audit being finished. But the sentence says until the audit "
                             "was complete, so it isn't finished yet. That contradicts it. Option C: because the "
                             "release was already live. You can't postpone something that's already live. Option "
                             "D: having deployed the release yesterday. Same problem. Option B: concerned about "
                             "unresolved vulnerabilities. That's a sensible reason to wait for a security audit.",
               ("until", lambda: audit.animate.set_color(BROWN)),
               ("contradicts", lambda: self.no(q1, "a", "Contradicts 'until the audit was complete'")),
               ("postpone", lambda: self.no(q1, "c", "Already live: nothing to postpone")),
               ("Same", lambda: self.no(q1, "d", "The same problem")),
               ("sensible", lambda: self.yes(q1, "b", "A sensible reason to wait")),
               shown="(a), (c) and (d) contradict the main clause. (b) is a sensible reason to wait for an audit.")
        self.S("B", "s4_05", "And option B is a participle phrase. Concerned describes the team, the subject right "
                             "after the comma. No dangling modifier.",
               ("team", lambda: [team.animate.set_color(BLUE), hl(team, 1.1)]), look="think",
               shown="And (b) is a participle phrase. 'Concerned' describes the team. No dangling modifier.")
        self.T("s4_06", "Good. You checked the meaning and the grammar together.", look="happy")

        self.finish("S04_filler")

    # ============================== 5. QUESTION 2: THE CLOZE PASSAGE =======

    def passage(self):
        self.begin("S05_cloze", "Question 2: The Cloze Passage", "The cloze passage")
        q2 = self.new_q(2)

        self.Q("s5_01", "Question two. How did you start?", (None, lambda: self.show_question(q2)),
               shown="Question 2. How did you start?")
        self.S("A", "s5_02", "I read the whole passage first. It's about cloud computing: cheaper to start, but it "
                             "can get expensive, so monitoring matters.",
               ("whole", lambda: hl(q2.passage, 1.01)),
               shown="I read the whole passage first: cheaper to start, but it can get expensive, so monitoring matters.")
        self.T("s5_03", "Now blank by blank.", look="ask")
        self.S("A", "s5_04", "Blank one: rent computing power, blank, buying servers. Renting replaces buying, so "
                             "instead of, option B.",
               ("instead", lambda: self.answer(q2, 0, 2, "instead of")),
               shown="(1): rent computing power ___ buying servers. Renting replaces buying: 'instead of', (b).")
        self.S("B", "s5_05", "Blank two: this, blank, upfront costs. Renting means you don't buy servers, so "
                             "upfront costs go down. Reduces, option B.",
               ("Reduces", lambda: self.answer(q2, 1, 2, "reduces")),
               shown="(2): 'This ___ upfront costs.' You don't buy servers, so the costs go down: 'reduces', (b).")
        self.S("C", "s5_06", "Blank three: reduces costs, blank, it can become expensive. That's a contrast, so "
                             "but, option C.",
               ("contrast", lambda: self.answer(q2, 2, 3, "but")),
               shown="(3): 'reduces costs, ___ it can become expensive.' That's a contrast: 'but', (c).")
        self.S("D", "s5_07", "Blank four: careful monitoring is therefore, blank. Since it can get expensive, "
                             "monitoring is necessary. Essential, option B.",
               ("Essential", lambda: self.answer(q2, 3, 2, "essential")),
               shown="(4): 'Careful monitoring is therefore ___.' It can get expensive, so: 'essential', (b).")
        self.T("s5_08", "Notice that blank four depended on blank three. Therefore points back to it can become "
                        "expensive. In a cloze test, the blanks are linked, so later blanks often confirm earlier "
                        "ones.",
               ("Therefore", lambda: [hl(q2.passage[3][0], 1.1), hl(q2.passage[1][4], 1.06)]),
               ("linked", lambda: hl(q2.passage, 1.01)))

        self.finish("S05_cloze")

    # ========================================= 6. RAPID-FIRE ROUND =========

    def rapid_item(self, k):
        """Put rapid item ``k`` on the board and give fifteen seconds for it."""
        q = self.new_q(k + 2)
        self.show_question(q)
        self.countdown(15.0)
        return q

    def rapid(self):
        self.begin("S06_rapid", "Rapid-Fire Round", "Rapid-fire round")

        self.Q("s6_01", "Fifteen seconds each. Give the answer and the filter.")
        q = self.rapid_item(1)
        self.S("B", "s6_02", "Option A, unexpected. Grammar: an needs a vowel sound.",
               ("unexpected", lambda: [self.yes(q, "a", "Grammar: 'an'"), self.fill_in(q, "unexpected")]),
               ("vowel", lambda: q.body[0][1].animate.set_color(BROWN)),
               shown="(a), 'unexpected'. Grammar: 'an' needs a vowel sound.")
        q = self.rapid_item(2)
        self.S("C", "s6_03", "Option B, contained. Direction: despite months of testing means the result was bad, "
                             "so bugs remained.",
               ("contained", lambda: [self.yes(q, "b", "Direction: 'despite'"), self.fill_in(q, "contained")]),
               ("despite", lambda: q.body[0][0].animate.set_color(BROWN)),
               shown="(b), 'contained'. Direction: 'despite months of testing' means the result was bad.")
        q = self.rapid_item(3)
        self.S("D", "s6_04", "Option B, trivial. Definition after the colon: one line.",
               ("trivial", lambda: [self.yes(q, "b", "Definition: the colon"), self.fill_in(q, "trivial")]),
               ("colon", lambda: q.body[0][2].animate.set_color(BROWN)),
               shown="(b), 'trivial'. Definition after the colon: one line.")
        q = self.rapid_item(4)
        self.S("A", "s6_05", "Option C, otherwise. Condition: if they're not rotated, the disk fills up.",
               ("otherwise", lambda: [self.yes(q, "c", "A condition"), self.fill_in(q, "otherwise")]),
               shown="(c), 'otherwise'. Condition: if they're not rotated, the disk fills up.")

        self.finish("S06_rapid")

    # ============================ 7. THE SENTENCE-COMPLETION FLOW ==========

    def full_flow(self):
        self.begin("S07_flow", "The Sentence-Completion Flow", "The completion flow")
        self.card("Sentence-completion flow", lines(FLOW, SMALL, 0.34), read=9.0)
        self.finish("S07_flow")

    # ================================ 8. WHY THIS SKILL TRANSFERS ==========

    def transfer(self):
        self.begin("S08_why", "Why This Skill Transfers", "The skill transfers")

        code_way = chain_of("An unknown function", "guess from how it is used", "check")
        word_way = chain_of("A missing word", "infer from the context", "check")
        pair = column(code_way, word_way, buff=0.9)
        place(pair, x=0.0, top=BOARD_TOP - 0.7)
        built = self.foot("Reading comprehension is built on this", y=-2.5)
        self.fit(pair)

        self.S("B", "s8_01", "This is basically what we did in reading code we hadn't written. Guess what a "
                             "function returns from how it's used, then check.",
               ("code", lambda: up(code_way)), look="think",
               shown="This is what we did with code we hadn't written: guess what a function returns, then check.")
        self.T("s8_02", "Exactly. Inferring something missing from its context is what reading comprehension is "
                        "built on. That's where we go next.",
               ("missing", lambda: up(word_way)),
               ("built", lambda: up(built)), look="happy")

        self.finish("S08_why")

    # ================================================ 9. PAYOFF RECAP ======

    def recap(self):
        self.begin("S09_recap", "Payoff Recap", "Final answers")
        q1, q2 = self.new_q(1), self.new_q(2)

        self.T("s9_01", "Final answers.", (None, lambda: self.show_question(q1)), look="ask")
        self.S("D", "s9_02", "Question one: option B. Concerned about the unresolved vulnerabilities gives a "
                             "sensible reason for waiting, and it correctly describes the team. The others "
                             "contradict the main clause.",
               ("option", lambda: self.yes(q1, "b", "A sensible reason, and it describes the team")),
               ("others", lambda: self.no(q1, "acd")), other="happy",
               shown="Question 1: (b). A sensible reason for waiting, and it correctly describes the team.")
        self.show_question(q2)
        self.S("A", "s9_03", "Question two: blank one, instead of. Blank two, reduces. Blank three, but. Blank "
                             "four, essential.",
               ("instead", lambda: self.answer(q2, 0, 2, "instead of")),
               ("reduces", lambda: self.answer(q2, 1, 2, "reduces")),
               ("but", lambda: self.answer(q2, 2, 3, "but")),
               ("essential", lambda: self.answer(q2, 3, 2, "essential")), other="happy",
               shown="Question 2: (1) instead of, (2) reduces, (3) but, (4) essential.")
        self.wipe()
        done = VGroup(text("Module 3: Verbal Ability", BODY, INK, BOLD),
                      text("Complete", BODY, GOOD, BOLD)).arrange(DOWN, buff=0.4).move_to(DOWN * 0.6)
        self.play(up(done), run_time=1.2)
        self.countdown(2.0)

        self.finish("S09_recap")

    # ========================================= 10. WHAT COMES NEXT =========

    def next_session(self):
        self.begin("S10_next", "What Comes Next", "What comes next?")

        so_far = text("Words, grammar, sentences and their order", BODY).move_to(UP * 0.1)
        last = text("The last module: full passages, under time pressure", BODY, BROWN, BOLD).move_to(DOWN * 0.8)
        text_block = lines(['"The team\'s first attempt at migrating to microservices failed. Services',
                            "were split along team boundaries rather than business capabilities, and",
                            "every feature required changes to five repositories. The second attempt",
                            'began with a single question: what can change independently?"'], SMALL, 0.2)
        place(text_block, x=0.0, top=BOARD_TOP - 0.3)
        topic = text("Topic:  microservices", LABEL, BLUE, BOLD).move_to(DOWN * 1.2)
        idea = text("Main idea:  split by what changes independently", LABEL, BROWN, BOLD).move_to(DOWN * 1.9)
        nxt = self.foot("Next:  Module 4, Reading comprehension", y=-2.9)
        self.fit(so_far, last, text_block, idea)

        self.N("s10_01", "Words, then grammar, then whole sentences and their order. The last module puts it all "
                         "together: full passages, read under time pressure, with questions about what they say "
                         "and what they imply.",
               ("order", lambda: up(so_far)),
               ("passages", lambda: up(last)))
        self.wipe()
        self.play(LaggedStart(*[up(m) for m in text_block], lag_ratio=0.3), run_time=1.8)
        self.Q("s10_02", "What is this passage really about?")
        self.S("C", "s10_03", "Microservices.", (None, lambda: up(topic)))
        self.S("D", "s10_04", "I think it's about how to decide where to split a system.",
               ("split", lambda: up(idea)), look="think")
        self.Q("s10_05", "Two answers to one question. Which would the exam call the main idea?",
               ("Which", lambda: [hl(topic, 1.04), hl(idea, 1.04)]))
        self.T("s10_06", "Next session. Module four: Reading Comprehension.", (None, lambda: up(nxt)))

        self.the_end("S10_next")

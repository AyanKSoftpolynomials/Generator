"""
animation.py for the LMS video generator.

Course : C-CAT Preparation - Section B: Quantitative Aptitude
Module : 1 Number Foundations   Lesson : 2 LCM and HCF (Session 2)
Video  : 06 - Remainder Problems (LCM and HCF)
         (previous: Word problems: bells, lights, tiles;  next: Speed tricks, LCM and HCF)
Source : C:/Final scripts/Scipts/Quantitative Aptitude/Module 1 - Number Foundations/Lesson 2 - LCM and HCF/
         06 - Remainder problems.pdf

Note: the questions are practice questions written for the class, not past-paper questions.

Look (3Blue1Brown style): near-black background, white text, one blue and one brown accent; yellow only for a
  passing highlight, green / red only for right / wrong. Latin Modern Roman (Cambria if it is missing).
Roles (no speaker labels in the script; lines assigned by meaning, no label is spoken): NARRATOR self.N "vijay",
  TEACHER self.T / self.Q "aditya", STUDENTS self.S: A confident "prasad", B cautious "kavya",
  C the second student "ritu", D at the back "student_a". Stage directions are the visuals.
Sarvam AI voices (settings.json > audio.sarvam.voices, or --speaker VOICE=SPEAKER):
    "vijay": "vijay", "aditya": "aditya", "prasad": "kabir", "kavya": "kavya", "ritu": "ritu", "student_a": "rahul"

The two questions are shown one at a time; the thinking time (60 seconds) is split between them. Worked
examples keep the rule in a panel on the left and the working on the right. "LCM" and "HCF" are spoken letter
by letter.

Section map: S01 LCM plus the remainder  S02 The topic  S03 How C-CAT tests it  S04 Attempts
  S05 WHAT: the four patterns  S06 HOW: pattern 4 and the divisor check  S07 HOW: combining patterns
  S08 WHY: synchronisation with offsets  S09 Payoff  S10 Summary  S11 What comes next
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

SYMBOL_FONT = "Segoe UI Symbol"       # draws the symbols Latin Modern Roman lacks (they came out as boxes)
SYMBOLS = "π≠≡≤≥≈∴∵∠△∑θαβγλμσφω∈∉⊂∪∩⇒⇔↔⁴ⁿ₁₂₃′″∝∥⊥≅∼"


def text(s, size=BODY, color=INK, weight=NORMAL, slant=NORMAL, font=FONT):
    other = {ch: ("Segoe UI" if ch == "₹" else SYMBOL_FONT) for ch in set(s)
             if ch in SYMBOLS or ch == "₹"} if font == FONT else {}
    return Text(s, font=font, font_size=size, color=color, weight=weight, slant=slant, disable_ligatures=True,
                **({"t2f": other} if other else {}))


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


mcq = blank_question            # any question with four options (a sentence with a blank, or not)

WORK_X = -EDGE_X + 4.4          # where the working starts while a side panel is pinned on the left


def side_panel(title, rows, width=4.0):
    """The formula panel that stays on the left while an example is worked on the right."""
    head = fit_w(text(title, SMALL, BROWN, BOLD), width - 0.5)
    body = VGroup(*[fit_w(text(s, SMALL), width - 0.5) for s in rows]).arrange(DOWN, buff=0.22, aligned_edge=LEFT)
    inner = VGroup(head, body).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
    frame = RoundedRectangle(width=width, height=inner.height + 0.6, corner_radius=0.12, stroke_color=BROWN,
                             stroke_width=3, fill_color=FILL, fill_opacity=1.0)
    inner.move_to(frame)
    return place(VGroup(frame, inner), left=-EDGE_X, top=BOARD_TOP - 0.2)


def working(steps, size=LABEL, buff=0.36, left=WORK_X, top=BOARD_TOP - 0.25):
    """Lines of working (strings, or lists of ``para`` pieces) under one another; beside a side panel by default."""
    rows = VGroup(*[para(s if isinstance(s, list) else [s], size=size)[0] for s in steps])
    rows.arrange(DOWN, buff=buff, aligned_edge=LEFT)
    for row in rows:
        fit_w(row, EDGE_X - left)
        row.align_to(rows, LEFT)
    return place(rows, left=left, top=top)


def power(base, exp, size=BODY, color=INK, weight=NORMAL):
    """``base`` with a raised exponent (both strings)."""
    b = text(base, size, color, weight)
    e = text(exp, size * 0.6, color, weight)
    e.next_to(b, RIGHT, buff=0.04).align_to(b, UP).shift(UP * b.height * 0.3)
    return VGroup(b, e)


def dial(digits, x=3.6, y=-0.5, r=1.05):
    """A cycle as a dial: the values round a circle (clockwise from the top), and a pointer on the first.

    ``d.centre`` and ``d.pointer`` are for turning it; d[1] holds the values."""
    centre = np.array([x, y, 0.0])
    ring = Circle(radius=r, stroke_color=MUTED, stroke_width=3).move_to(centre)
    turn = 2 * PI / len(digits)
    marks = VGroup(*[text(d, BODY, BROWN, BOLD).move_to(centre + (r + 0.45) * np.array(
        [np.sin(k * turn), np.cos(k * turn), 0.0])) for k, d in enumerate(digits)])
    pointer = Arrow(centre, centre + UP * (r - 0.1), buff=0, color=FLASH, stroke_width=5, tip_length=0.22)
    out = VGroup(ring, marks, pointer)
    out.centre, out.pointer = centre, pointer
    return out


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

CRUMB = "C-CAT Preparation  ›  Quantitative Aptitude  ›  Number Foundations  ›  LCM and HCF"
HOOK = ["÷ 6, 8 and 12 :    remainder 5 each time", "N − 5 is a multiple of 6, 8 and 12",
        "N − 5 = 24k,    so    N = 24k + 5", [("k = 1 :    N = 29", GOOD, BOLD)],
        [("29 = 6 × 4 + 5 = 8 × 3 + 5 = 12 × 2 + 5", MUTED)]]
POINTS = ["Same remainder: LCM + the remainder", "Same deficit: LCM − the deficit",
          "Same unknown remainder: the HCF of the differences", "Given remainders: the HCF of (numbers − remainders)",
          "The divisor is bigger than every remainder"]


def make_question(k):
    if k == 1:
        return mcq("Practice question 1",
                   [["The smallest number greater than 5 which, when divided by 6, 8 and 12,"],
                    ["leaves a remainder of 5 in each case is:"]], ["24", "29", "53", "19"])
    return mcq("Practice question 2",
               [["The largest number that divides 1305, 4665 and 6905, leaving the same"],
                ["remainder in each case, is:"]], ["1120", "560", "2240", "185"])


def pattern_cards():
    small = family("Smallest number    (use the LCM)",
                   ["1.  The same remainder r:      N = LCM × k + r          smallest:  LCM + r"],
                   ["2.  The same deficit d   (each remainder = divisor − d):"],
                   ["N = LCM × k − d          smallest:  LCM − d"],
                   [("÷ 6, 8, 12 leaves 5, 7, 11:   each is divisor − 1,   so   N = 24 − 1 = 23", MUTED)])
    large = family("Largest divisor    (use the HCF)",
                   ["3.  The same unknown remainder, dividing x, y, z:      HCF(y − x, z − y)"],
                   ["4.  Given remainders r1, r2, dividing x, y:      HCF(x − r1, y − r2)"],
                   [("The divisor must be bigger than every remainder", BROWN)])
    return stack([small, large], 0.5)


class RemainderProblemsLcmAndHcf(LMSScene):
    lesson_title = "Remainder Problems (LCM and HCF)"

    def construct(self):
        self.reset()
        for scene in (self.hook, self.topic, self.exam, self.attempts, self.what, self.how, self.combine, self.why,
                      self.payoff, self.summary, self.next_session):
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

    # ================================= 1. LCM PLUS THE REMAINDER ===========

    def hook(self):
        self.scene_start("S01_hook", title="LCM Plus the Remainder")
        card = self.opening("Remainder Problems (LCM and HCF)", "Word problems: bells, lights, tiles")
        self.heading("LCM plus the remainder")

        panel = side_panel("The same remainder r", ["N − r is a common", "multiple of the divisors", "N = LCM × k + r"])
        steps = working(HOOK, buff=0.42)
        mean = self.foot("Exams mean the smallest number larger than the remainder", y=-3.05, size=SMALL)

        self.N("s1_01", "24 divides cleanly by all three. The question wants 5 left over every time. That means "
                        "moving 5 steps past a common multiple.",
               ("divides", lambda: [FadeOut(card), FadeIn(panel), up(steps[0])]))
        self.Q("s1_02", "If N leaves 5 when divided by 6, what does N minus 5 do?")
        self.S("B", "s1_03", "It divides exactly by 6. And by 8 and 12 too, since the remainder is 5 in each case.",
               ("exactly", lambda: side(steps[1])), look="think")
        self.T("s1_04", "So N minus 5 is a common multiple of 6, 8 and 12.")
        self.S("D", "s1_05", "So N minus 5 is a multiple of 24. N is 24 k plus 5. Smallest is 29.",
               ("plus", lambda: side(steps[2])),
               ("Smallest", lambda: [side(steps[3]), side(steps[4])]),
               shown="So N − 5 is a multiple of 24. N is 24k + 5. Smallest is 29.")
        self.S("C", "s1_06", "What about k equals 0? Then N is 5. 5 divided by 6 is 0 remainder 5. That also works.",
               look="ask", shown="What about k = 0? Then N is 5. 5 ÷ 6 is 0 remainder 5. That also works.")
        self.T("s1_07", "Technically, you're right. 5 satisfies the condition, with a quotient of 0. Exams mean the "
                        "smallest number larger than the remainder, which is why careful questions say greater "
                        "than 5. If an option list contains both 5 and 29, the question almost certainly intends "
                        "29. When the wording is careful, follow it exactly.",
               ("larger", lambda: up(mean)), look="happy")

        self.finish("S01_hook")

    # ================================================== 2. THE TOPIC =======

    def topic(self):
        self.begin("S02_topic", "The Topic", "Four patterns")
        pts = self.points(["Four patterns cover nearly all of these questions",
                           "Two use the LCM: the smallest number with given remainders",
                           "Two use the HCF: the largest divisor leaving given remainders"], size=LABEL)
        self.T("s2_01", "Four patterns cover nearly all of these questions. Two use the L C M, for the smallest "
                        "number with given remainders. Two use the H C F, for the largest divisor that leaves "
                        "given remainders.",
               *self.reveal(pts, ("patterns", "smallest", "largest")))
        self.finish("S02_topic")

    # ======================================== 3. HOW C-CAT TESTS IT ========

    def exam(self):
        self.exam_scene("S03_exam", "s3_01", "Two practice questions, written for this class.", "s3_02",
                        "Sixty seconds.", 60.0)

    # ================================================== 4. ATTEMPTS ========

    def attempts(self):
        self.begin("S04_attempts", "Attempts", "First attempts")
        q2 = self.q2
        w = working(["1305 − r,    4665 − r,    6905 − r    are all divisible by it",
                     "4665 − 1305 = 3360,      6905 − 4665 = 2240      (r cancels)",
                     "3360 − 2240 = 1120,      2240 = 2 × 1120", [("HCF(3360, 2240) = 1120", GOOD, BOLD)]],
                    size=SMALL, buff=0.26, left=-EDGE_X + 0.3, top=-1.45)
        for row in w:
            self.keep(row)

        self.Q("s4_01", "Question 2. This one is harder. Where do you start?")
        self.S("A", "s4_02", "If the remainder is the same, say r, then 1305 minus r, 4665 minus r and 6905 minus "
                             "r are all divisible by the number.",
               ("divisible", lambda: side(w[0])),
               shown="If the remainder is the same, say r, then each number minus r is divisible by the number.")
        self.T("s4_03", "And you don't know r.", look="ask")
        self.S("D", "s4_04", "Subtract them from each other. The r cancels. 4665 minus 1305 is 3360. 6905 minus "
                             "4665 is 2240. The number has to divide both differences.",
               ("cancels", lambda: side(w[1])), look="think",
               shown="Subtract them from each other: the r cancels. 3360 and 2240. It has to divide both differences.")
        self.S("B", "s4_05", "So the largest such number is the H C F of 3360 and 2240. 3360 minus 2240 is 1120. "
                             "2240 is 2 times 1120. So the H C F is 1120.",
               ("minus", lambda: side(w[2])),
               ("times", lambda: [side(w[3]), self.pick(q2, "a", GOOD)]),
               shown="So it is the HCF of 3360 and 2240. 3360 − 2240 is 1120. 2240 is 2 × 1120. The HCF is 1120.")

        self.finish("S04_attempts")

    # ===================================== 5. WHAT: THE FOUR PATTERNS ======

    def what(self):
        self.begin("S05_what", "WHAT: The Four Patterns", "The four patterns")

        self.card(None, pattern_cards(), read=10.0, top=BOARD_TOP - 0.25)
        short = self.foot("23 = 24 − 1 :  one short of each divisor", y=-3.15, size=SMALL)

        self.S("C", "s5_01", "So 23 divided by 6 is 3 remainder 5, divided by 8 is 2 remainder 7, and divided by "
                             "12 is 1 remainder 11.", look="think",
               shown="So 23 ÷ 6 is 3 remainder 5, ÷ 8 is 2 remainder 7, and ÷ 12 is 1 remainder 11.")
        self.T("s5_02", "Exactly. 23 is one short of being a multiple of all three, so it's always one short of "
                        "each divisor.",
               ("short", lambda: up(short)))

        self.finish("S05_what")

    # ==================== 6. HOW: PATTERN 4 AND THE DIVISOR CHECK ==========

    def how(self):
        self.begin("S06_how", "HOW: Pattern 4 and the Divisor Check", "The divisor check")

        panel = side_panel("Pattern 4", ["Divisor =", "HCF(x − r1, y − r2)", "It must be bigger", "than every remainder"])
        steps = working(["Divides 62 and 132, leaving 2 and 6", "62 − 2 = 60,       132 − 6 = 126", "HCF(60, 126) = 6",
                         [("Is 6 bigger than the remainders 2 and 6?   No", BAD, BOLD)],
                         [("Factors of 6:   1, 2, 3, 6 :    none is bigger than 6", MUTED)]], buff=0.42)

        self.play(FadeIn(panel), LaggedStart(*[side(m) for m in steps[:4]], lag_ratio=0.6), run_time=3.0)
        self.countdown(5.0)
        self.S("B", "s6_01", "So 6 doesn't work. A remainder can't equal the divisor.", look="think")
        self.T("s6_02", "Right. A remainder must always be smaller than the divisor. If the H C F fails that check, "
                        "use the largest factor of it that's bigger than every remainder. Here, the factors of 6 "
                        "are 1, 2, 3 and 6. None of them is bigger than 6, so no such number exists.",
               ("factors", lambda: side(steps[4])))
        self.S("D", "s6_03", "So there's a built-in check. The divisor has to be bigger than every remainder.",
               ("bigger", lambda: hl(panel, 1.02)))

        self.finish("S06_how")

    # ==================================== 7. HOW: COMBINING PATTERNS =======

    def combine(self):
        self.begin("S07_combine", "HOW: Combining Patterns", "Combining patterns")

        panel = side_panel("Combine", ["Pattern 1:", "N = LCM × k + r", "Then choose k to meet", "the extra condition"])
        steps = working(["÷ 5, 6, 7, 8 leaves 3;    ÷ 9 leaves 0", "LCM(5, 6, 7, 8) = 840,    so    N = 840k + 3",
                         "840 leaves 3 (mod 9) :    N leaves 3k + 3", "3k + 3 = 9,    so    k = 2",
                         [("N = 1,683          (1 + 6 + 8 + 3 = 18)", GOOD, BOLD)]], buff=0.42)

        self.play(FadeIn(panel), up(steps[0]), run_time=1.0)
        self.S("A", "s7_01", "Pattern 1. L C M of 5, 6, 7 and 8 is 840. N is 840 k plus 3. Then find k so that N is "
                             "divisible by 9.",
               ("plus", lambda: side(steps[1])),
               shown="Pattern 1. LCM of 5, 6, 7 and 8 is 840. N is 840k + 3. Then find k so that 9 divides N.")
        self.S("B", "s7_02", "840 has a digit sum of 12, so it leaves remainder 3 when divided by 9. 840 k plus 3 "
                             "leaves 3 k plus 3. That has to be a multiple of 9, so 3 k plus 3 is 9, and k is 2. "
                             "The number is 1,683.",
               ("remainder", lambda: side(steps[2])),
               ("multiple", lambda: side(steps[3])),
               ("number", lambda: side(steps[4])), look="think",
               shown="840 leaves 3 when divided by 9. 840k + 3 leaves 3k + 3. So 3k + 3 = 9, k = 2. N = 1,683.")
        self.T("s7_03", "Check: 1 plus 6 plus 8 plus 3 is 18, divisible by 9.", look="happy")

        self.finish("S07_combine")

    # ========================== 8. WHY: SYNCHRONISATION WITH OFFSETS =======

    def why(self):
        self.begin("S08_why", "WHY: Synchronisation with Offsets", "Schedules with offsets")

        a = text("Jobs every 6, 8 and 12 minutes, each starting 5 minutes late", LABEL).move_to(UP * 0.5)
        b = text("They line up at  0:05,   0:29,   0:53,   ...", LABEL, BLUE, BOLD).move_to(DOWN * 0.5)
        offset = self.foot("LCM + the offset", y=-2.0, size=BODY)
        self.fit(a)

        self.T("s8_01", "Real schedules often have an offset: a job that runs every 6 minutes, starting 5 minutes "
                        "past the hour. Finding when several offset schedules align is exactly pattern 1. L C M "
                        "plus the offset.",
               ("job", lambda: up(a)),
               ("align", lambda: up(b)),
               ("plus", lambda: up(offset)))

        self.finish("S08_why")

    # ============================ 9. PAYOFF: SOLVING BOTH QUESTIONS ========

    def payoff(self):
        self.begin("S09_payoff", "Payoff: Solving Both Questions", "Solving both questions")
        q1, q2 = self.new_q(1), self.new_q(2)
        w1 = working(["LCM(6, 8, 12) = 24,      N = 24k + 5", [("Smallest above 5 :    29", GOOD, BOLD)]],
                     buff=0.35, left=-EDGE_X + 0.3, top=-1.8)
        w2 = working(["Differences:    3360 and 2240.      HCF = 1120",
                      [("1305 = 1120 × 1 + 185,     4665 = 1120 × 4 + 185,     6905 = 1120 × 6 + 185", MUTED)]],
                     size=SMALL, buff=0.3, left=-EDGE_X + 0.3, top=-1.9)

        self.ask_q("s9_01", "Question 1.", q1)
        for row in w1:
            self.keep(row)
        self.S("C", "s9_02", "Pattern 1: L C M of 6, 8 and 12 is 24. N is 24 k plus 5. The smallest number greater "
                             "than 5 is 29. The answer is option B. Option A forgets the remainder. Option C is "
                             "the next one, k equals 2. Option D isn't of the form 24 k plus 5.",
               ("plus", lambda: side(w1[0])),
               ("greater", lambda: side(w1[1])),
               ("answer", lambda: self.yes(q1, "b")),
               (("Option", 2), lambda: self.no(q1, "a")),
               (("Option", 3), lambda: self.no(q1, "c", "k = 2")),
               (("Option", 4), lambda: self.no(q1, "d", "Not 24k + 5")), other="happy",
               shown="Pattern 1: LCM = 24. N = 24k + 5. The smallest number greater than 5 is 29. The answer is (b).")

        self.ask_q("s9_03", "Question 2.", q2)
        for row in w2:
            self.keep(row)
        self.S("A", "s9_04", "Pattern 3: the differences are 3360 and 2240. Their H C F is 1120. Check: 1305 is "
                             "1120 times 1 plus 185, 4665 is 1120 times 4 plus 185, 6905 is 1120 times 6 plus 185. "
                             "Same remainder, 185. The answer is option A. Option B also works, but it isn't the "
                             "largest. Option D is the remainder, not the divisor.",
               ("differences", lambda: side(w2[0])),
               ("Check", lambda: side(w2[1])),
               ("answer", lambda: self.yes(q2, "a")),
               (("Option", 2), lambda: self.no(q2, "b", "Works, not largest")),
               (("Option", 3), lambda: [self.no(q2, "d", "The remainder"), self.no(q2, "c")]), other="happy",
               shown="Pattern 3: the differences are 3360 and 2240. HCF 1120. Same remainder, 185. The answer is (a).")

        self.finish("S09_payoff")

    # ================================================= 10. SUMMARY =========

    def summary(self):
        self.summary_scene("S10_summary", "B", "s10_01", "s10_02",
                           "For the smallest number with the same remainder, use L C M plus the remainder. With "
                           "the same deficit, use L C M minus the deficit. For the largest divisor with the same "
                           "unknown remainder, use the H C F of the differences. For given remainders, use the "
                           "H C F of the numbers minus their remainders. Always check that the divisor is bigger "
                           "than every remainder.",
                           POINTS, ("plus", "minus", "differences", "given", "bigger"),
                           shown="Same remainder: LCM plus the remainder. Same deficit: LCM minus the deficit.")

    # ========================================= 11. WHAT COMES NEXT =========

    def next_session(self):
        self.begin("S11_next", "What Comes Next", "What comes next?")

        title = text("Speed tricks: LCM and HCF", TITLE, INK, BOLD).move_to(UP * 0.4)
        clock = text("15 seconds per question", BODY, BLUE, BOLD).move_to(DOWN * 0.6)
        more = text("Every pattern, and a couple of new shortcuts", LABEL, MUTED).move_to(DOWN * 1.5)
        nxt = self.foot("Next session:  Speed tricks", y=-2.8)
        self.fit(title)

        self.N("s11_01", "One session remains for L C M and H C F, the speed round.", ("speed", lambda: up(title)))
        self.T("s11_02", "Next time, every pattern from this lesson at exam speed, including a couple of shortcuts "
                         "we haven't seen yet.",
               ("speed", lambda: up(clock)),
               ("shortcuts", lambda: FadeIn(more)))
        self.S("C", "s11_03", "Fifteen seconds for an L C M of three numbers?", look="surprised",
               shown="Fifteen seconds for an LCM of three numbers?")
        self.T("s11_04", "Next session.", (None, lambda: up(nxt)))

        self.the_end("S11_next")

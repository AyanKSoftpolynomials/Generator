"""
animation.py for the LMS video generator.

Course : C-CAT Computer Fundamentals
Lesson : Lesson 4 - Number System Conversions and Objective Practice
Video  : 03 Video 1 - Converting to Decimal

Source script:
  CCAT_Computer_Fundamentals_Scripts_Lessons_1-5/PDF/Lesson 4 - Number System Conversions and Objective Practice/03 Video 1 - Converting to Decimal.pdf
  The script has no speaker labels. Every line was labelled as below:
    TEACHER  spoken by the teacher: ``self.tell`` / ``self.ask`` / ``self.answer`` (TEACHER_VOICE).
             Drives the board. The teacher stands at the bottom left; the pointer is up while speaking.
    STUDENT  spoken by a student: ``self.reply`` (STUDENT_VOICE). Every student line is its own
             narration; the student comes up at the bottom right with a speech balloon (hand raised
             first when the student asks, a notebook when she reads from her notes).
    STAGE    stage direction: not narrated, it becomes the visuals.
    BOARD    what the board shows: on screen, not spoken.
  The wording is the script's. Only the spelling for the voice differs: spoken text uses words
  ("one zero one one"); the balloons and the board show digits ("1011").

Speaker split:
  01 TITLE   Converting to Decimal: The Expansion Method and the Double-and-Add Shortcut
  02 STAGE   The board still shows a table of weights from the last lesson.
  03 TEACHER Last time we said that the value of a number is the sum of each digit multiplied by its
             weight. Today we turn that sentence into a method. Let us take the binary number 110101.
             What is the first thing we write?
  04 STUDENT The weights.
  05 STAGE   The teacher writes them above the digits, from the right.
  06 BOARD   weight 32 16 8 4 2 1 / digit 1 1 0 1 0 1 / product 32 + 16 + 0 + 4 + 0 + 1 = 53
  07 TEACHER So (110101) in binary is 53 in decimal. Now let us do it again with a different system.
             Octal 725. What are the weights?
  08 STUDENT 1, 8, 64.
  09 TEACHER Reading from the right.                                        [REVIEW: see notes]
  10 STAGE   The board shows:
  11 BOARD   weight 64 8 1 / digit 7 2 5 / product 448 + 16 + 5 = 469
  12 TEACHER Hexadecimal 3A7. The first thing to do before multiplying is to look for letters. What is A?
  13 STUDENT Ten.
  14 STAGE   The board shows:
  15 BOARD   weight 256 16 1 / digit 3 10 7 (A = 10) / product 768 + 160 + 7 = 935
  16 STAGE   A student asks:
  17 STUDENT Why do we write the weights from the right?
  18 TEACHER Because the rightmost digit is always position 0 and has weight 1. If you start from the
             left you will misplace weights as soon as the number has a different number of digits
             from the one you practised on. Always start from the right.
  19 TEACHER Now what about numbers with a point? Look at 1011.101 in binary. The integer part works
             as before. For the fractional part, the weights continue to the right of the point as
             negative powers. What is the weight of the first place after the point?
  20 STUDENT One half.
  21 STAGE   The board shows the full number.
  22 BOARD   1011 . 101 / 8 4 2 1 . 1/2 1/4 1/8 / integer 11 / fraction 0.625 / total = 11.625
  23 TEACHER Hexadecimal works the same way. Take 1A.8 in hexadecimal. The integer part is 1 times 16
             plus A, which is 26. The fraction 8 is worth 8 sixteenths, which is 0.5. So the answer
             is 26.5.
  24 TEACHER Now here is a faster way. The expansion method is reliable but slow when numbers are
             long. Suppose I take 110101 again. I start with the first digit. Then for each next
             digit I double what I have and add the new digit.
  25 STAGE   The teacher writes.
  26 BOARD   1 -> 1 / 1 -> 1 x 2 + 1 = 3 / 0 -> 3 x 2 + 0 = 6 / ... / 1 -> 26 x 2 + 1 = 53
  27 TEACHER Same answer, 53, with no weights to remember. For octal, multiply by 8 instead of 2. For
             725, start with 7, then 7 times 8 plus 2 is 58, then 58 times 8 plus 5 is 469. For
             hexadecimal, multiply by 16. For 3A7, we start with 3, then 3 times 16 plus 10 is 58,
             then 58 times 16 plus 7 is 935.
  28 TEACHER Which method should we use?                                    [REVIEW: see notes]
  29 STUDENT Whichever one we make fewer mistakes with.
  30 TEACHER Exactly. For short binary numbers, the weights are easy. For long numbers,
             double-and-add is easier. Practise both, and then choose.
  31 TEACHER Let us look at the typical mistakes. What goes wrong?
  32 STAGE   The teacher lists them.
  33 BOARD   1. weights assigned from the left instead of the right / 2. forgetting that a letter has
             a value (A = 10, not 1) / 3. using weight 10 for a non-decimal number / 4. skipping a
             zero digit and shifting the weights
  34 TEACHER The fourth one is subtle. A zero contributes nothing, but it still occupies a position.
             If you skip it in your table, every weight to its left will be wrong.
  35 TEACHER A quick test. What is (1001)2?
  36 STUDENT 8 plus 1, so 9.
  37 TEACHER What is (17)8?
  38 STUDENT 8 plus 7, which is 15.
  39 TEACHER What is (1F)16?
  40 STUDENT 16 plus 15, which is 31.
  41 TEACHER Good. Summarise.
  42 STAGE   A student reads from her notes.
  43 STUDENT To convert to decimal, write the weights from the right, multiply, and add. Letters
             become numbers first. For fractions, use negative powers after the point. For long
             numbers, double-and-add is faster.
  44 STAGE   The board holds the final picture.
  45 BOARD   sum of (digit x weight)    or    double-and-add
  46 TEACHER What about the reverse? If I give you 45 in decimal, how would you write it in binary?
  47 STAGE   The board changes to:
  48 BOARD   NEXT: CONVERTING FROM DECIMAL

Notes:
  - REVIEW 09 "Reading from the right." follows a student answer with no stage direction. It is
    given to the TEACHER (the lines alternate, and the teacher is the one who adds remarks to
    answers); it could also be the student finishing the answer.
  - REVIEW 28 "Which method should we use?" is given to the TEACHER, because the reply to line 29
    starts with "Exactly.", which is how the teacher confirms student answers everywhere else. If
    line 28 is meant as a student question, lines 28 and 29 swap speakers.
  - Nothing is added to the script: the opening is a silent breadcrumb, and the script's own first
    two sentences are the recap. Long teacher lines are split into several narrations at sentence
    ends (a statement, then its question), with no words changed.
  - (1001)2, (17)8 and (1F)16 are spoken as "base two", "base eight" and "base sixteen".
  - Every worked answer in the script was recomputed in the data block; the script has no errors.
    Two illustrations use numbers from the script: 101 with weights taken from the left of a
    six-digit pattern (32 + 8 = 40, not 5), and 1011 with its zero skipped (7, not 11).

Style: 2D, three colours (blue main, grey support, gold highlight). The key object, 110101, is
drawn as raised digit boxes. Pinned KEY IDEAS panel and the teacher from the first scene to the end.

Section map:
  S00 Opening   S01 The expansion method   S02 Octal and hexadecimal   S03 Why from the right
  S04 Numbers with a point   S05 Double-and-add   S06 Typical mistakes   S07 A quick test
  S08 Summary   S09 Next
"""

import math
import types
from fractions import Fraction

import numpy as np
from manim import *

from src.animation import LMSScene

# ============================================================== style ====
# Three colours for the whole video: blue (main), grey (support), gold (highlight).

BG = "#0B1020"
INK = "#E6EAF2"
MUTED = "#8B95A7"
PANEL = "#151C2E"
MAIN = "#4FC3F7"
GOLD = "#FFD54F"

FONT = "Segoe UI"
MONO = "Consolas"      # digits, bit patterns and tables
MIN_FONT = 22          # readable floor: text is never shrunk below this
TITLE = 46
BODY = 30
LABEL = 28
SMALL = 24

# ============================================================= layout ====
# Zone map (the pinned panel and the teacher are docked on the left for the whole lesson body):
#
#   +-----------+--------------------------------------------+
#   |  PANEL    |  heading card                               |
#   |  (pinned  |  question card  (Q_TOP .. Q_TOP - Q_H)      |
#   |   ideas)  |  board: LEFT column        | RIGHT column   |
#   |           |  (notes, tables; may run   | (short items)  |
#   |           |   down to the floor)       +----------------+
#   |  teacher  |                            | speech balloon |
#   |           |                            |        student |
#   +-----------+----------------------------+----------------+
#
# The student always comes up bottom right; notes always go in the left
# column, so the two never collide.

FRAME_W = config.frame_width
FRAME_H = config.frame_height
SAFE = 0.45                                   # margin kept clear on every side
SAFE_W = FRAME_W - 2 * SAFE

CARD_TOP = FRAME_H / 2 - SAFE - 0.2           # top edge of a heading card
FLOOR_Y = -FRAME_H / 2 + SAFE + 0.15          # lowest y any content may reach
DEPTH_DIR = np.array([0.5, 0.32, 0.0])        # screen direction of "into the page"

PANEL_W = 3.3
PANEL_X = -FRAME_W / 2 + SAFE + PANEL_W / 2
STAGE_LEFT = PANEL_X + PANEL_W / 2 + 0.35
STAGE_RIGHT = FRAME_W / 2 - SAFE
STAGE_W = STAGE_RIGHT - STAGE_LEFT
STAGE_X = (STAGE_LEFT + STAGE_RIGHT) / 2

Q_TOP = CARD_TOP - 0.98                       # top of the question slot (under the heading)
Q_H = 1.45                                    # tallest question card allowed
BOARD_TOP = Q_TOP - Q_H - 0.15                # top of the board when a question is on screen
BOARD_HIGH = Q_TOP                            # top of the board when no question is on screen
STU_TEXT_W = 3.2                              # widest text in the speech balloon
STU_W = STU_TEXT_W + 0.4                      # student zone width
STU_TOP = -0.65                               # the speech balloon never rises above this
COL_GAP = 0.3

TEACHER_SCALE = 1.05                          # size of the teacher figure
ARM_REST = -60 * DEGREES                      # pointer down: the teacher is listening
ARM_SWING = 90 * DEGREES                      # pointer up to the board: the teacher is speaking
KID_SCALE = 1.2                               # size of the student figure
KID_H = 0.85 * KID_SCALE                      # its height
KID_HALF = 0.45 * KID_SCALE                   # half the width kept for it


# ======================================================= text helpers ====

def text(s, size=BODY, color=INK, weight=NORMAL, font=FONT):
    return Text(s, font=font, font_size=size, color=color, weight=weight, disable_ligatures=True)


def mono(s, size=BODY, color=INK, weight=BOLD):
    """Digits and bit patterns in a fixed-width face."""
    return text(s, size, color, weight, MONO)


def fit_width(mob, max_width):
    """Scale ``mob`` down (never up) to at most ``max_width``."""
    if mob.width > max_width:
        mob.scale_to_fit_width(max_width)
    return mob


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


def fitted_text(s, max_width, size=BODY, color=INK, weight=NORMAL, max_lines=3, font=FONT):
    """Readable text no wider than ``max_width``.

    Order of preference: as written > slightly smaller (to 85 %) > wrapped
    over more lines > wrapped and smaller (never below MIN_FONT). If none of
    that fits, fail loudly.
    """
    floor = max(MIN_FONT, 0.85 * size)
    for lines in range(1, max_lines + 1):
        body = s if lines == 1 else wrap_lines(s, lines)
        mob = text(body, size, color, weight, font)
        if mob.width <= max_width:
            return mob
        if size * max_width / mob.width >= floor:
            return mob.scale(max_width / mob.width)
        floor = MIN_FONT
    if size * max_width / mob.width >= MIN_FONT:
        return mob.scale(max_width / mob.width)
    raise ValueError(f"Text {s!r} cannot fit {max_width:.2f} units at a readable size; "
                     "shorten it or give it a wider container.")


def pill(label, color=GOLD, size=SMALL, fill_opacity=0.14, font=FONT):
    """Short keyword tag. The box is sized from the text, so text cannot escape."""
    t = text(label, size, color, BOLD, font)
    box = RoundedRectangle(corner_radius=(t.height + 0.26) / 2, width=t.width + 0.5, height=t.height + 0.26,
                           stroke_color=color, stroke_width=2, fill_color=color, fill_opacity=fill_opacity)
    t.move_to(box)
    return VGroup(box, t)


def num(s, base, size=BODY, color=INK):
    """A number with its base as a small subscript: 1011 with a little 2."""
    body = mono(s, size, color)
    sub = text(str(base), max(18, round(size * 0.62)), MUTED, BOLD)
    sub.next_to(body, RIGHT, buff=0.05).align_to(body, DOWN).shift(DOWN * 0.1)
    return VGroup(body, sub)


def result(s, base, value, size=BODY):
    """A finished conversion: the number with its base, an equals sign and the decimal value in gold."""
    return VGroup(num(s, base, size), mono("=", size, MUTED), mono(value, size, GOLD)).arrange(RIGHT, buff=0.25)


def verdict(s, tick, color):
    """A value with a tick or a cross after it."""
    return VGroup(mono(s, LABEL, color), text(tick, LABEL, color, BOLD)).arrange(RIGHT, buff=0.2)


def table(rows, widths, row_h=0.5, size=LABEL, head=True, font=MONO, color=INK):
    """A text grid without cell boxes (so nothing can overlap a box).

    ``rows`` is a list of lists of strings; an empty string leaves the cell
    blank. Returns VGroup(row, row, ...) with ``.rows`` (one VGroup per row),
    ``.cell[(r, c)]`` and ``.col(c)``. With ``head`` the first row is a grey
    heading with a rule under it."""
    xs, x = [], 0.0
    for w in widths:
        xs.append(x + w / 2)
        x += w
    grid = VGroup()
    grid.cell, grid.rows = {}, []
    for r, row in enumerate(rows):
        line = VGroup()
        is_head = head and r == 0
        for c, s in enumerate(row):
            if not s:
                continue
            t = text(s, SMALL if is_head else size, MUTED if is_head else color, BOLD, FONT if is_head else font)
            room = widths[c] - 0.16
            if t.width > room:
                if t.font_size * room / t.width < MIN_FONT - 2:
                    raise ValueError(f"Table cell {s!r} does not fit a column of {widths[c]:.2f}.")
                t.scale(room / t.width)
            t.move_to(RIGHT * xs[c] + DOWN * r * row_h)
            grid.cell[(r, c)] = t
            line.add(t)
        if is_head:
            line.add(Line(LEFT * 0.0, RIGHT * x, color=MUTED, stroke_width=2).move_to(
                RIGHT * x / 2 + DOWN * (r + 0.5) * row_h + UP * 0.03))
        grid.rows.append(line)
        grid.add(line)
    grid.col = lambda c: VGroup(*[t for (r_, c_), t in grid.cell.items() if c_ == c and not (head and r_ == 0)])
    return grid


def stack(*mobs, buff=0.22, edge=LEFT):
    """Mobjects under one another, left edges aligned."""
    return VGroup(*mobs).arrange(DOWN, buff=buff, aligned_edge=edge)


def bit_cells(digits, size=0.7, color=MAIN, raised=False, font_size=BODY):
    """A row of digit cells. ``raised`` draws them as slabs (only for the key object).

    Each cell is VGroup(box, digit); ``cell.box`` is the flat front face."""
    cells = VGroup()
    for k, d in enumerate(digits):
        if raised:
            slab = Slab(size, size, color, depth=0.16)
            box, holder = slab.front, slab
        else:
            box = Square(size, stroke_color=color, stroke_width=2.5, fill_color=PANEL, fill_opacity=1)
            holder = box
        cell = VGroup(holder, mono(d, font_size, INK).move_to(box)).shift(RIGHT * k * size)
        cell.box = box
        cells.add(cell)
    return cells


def point_cells(whole, frac, size=0.72):
    """Digit cells on both sides of a radix point: (whole cells, fraction cells, the point)."""
    a, b = bit_cells(whole, size), bit_cells(frac, size)
    b.next_to(a, RIGHT, buff=0.4)
    dot = Dot(radius=0.07, color=GOLD).move_to((a.get_corner(DR) + b.get_corner(DL)) / 2 + UP * 0.1)
    return a, b, dot


def above(cells, labels, size=SMALL, color=GOLD, buff=0.15):
    """One small label over each cell (weights, values)."""
    return VGroup(*[mono(s, size, color).next_to(c, UP, buff=buff) for s, c in zip(labels, cells)])


def below(cells, labels, size=SMALL, color=MUTED, buff=0.15):
    """One small label under each cell (positions, digits)."""
    return VGroup(*[mono(s, size, color).next_to(c, DOWN, buff=buff) for s, c in zip(labels, cells)])


def mark(cell, color=GOLD):
    """Highlight a digit cell."""
    return cell.box.animate.set_stroke(color, 5)


def unmark(cell, color=MAIN):
    """Back to the normal outline."""
    return cell.box.animate.set_stroke(color, 2.5)


def expansion(digits, base, size=0.72, raised=False):
    """Board block for the expansion method: one cell per digit, its weight above, its product below.

    Returns VGroup(cells, weights, products, plus, names); the same five are attributes.
    ``names`` are the row names (weight, digit, product), ``plus`` the signs between the products."""
    n = len(digits)
    ws = [base ** (n - 1 - k) for k in range(n)]
    cells = bit_cells(digits, size, raised=raised)
    weights = above(cells, [str(w) for w in ws])
    products = below(cells, [str(int(d, base) * w) for d, w in zip(digits, ws)], color=INK)
    plus = VGroup(*[mono("+", SMALL, MUTED).move_to((a.get_center() + b.get_center()) / 2)
                    for a, b in zip(products, products[1:])])
    names = VGroup(*[text(s, MIN_FONT, MUTED).next_to(cells, LEFT, buff=0.3).set_y(row.get_center()[1])
                     for s, row in (("weight", weights), ("digit", cells), ("product", products))])
    block = VGroup(cells, weights, products, plus, names)
    block.cells, block.weights, block.products, block.plus, block.names = cells, weights, products, plus, names
    return block


def chain(s, base):
    """Double-and-add for ``s`` written out: a heading and one line per digit.

    Returns the stack with ``.head`` and ``.lines``."""
    head = VGroup(num(s, base, BODY), text(f"multiply by {base}", SMALL, MUTED)).arrange(RIGHT, buff=0.4)
    lines = VGroup(*[mono(x, LABEL, INK) for x in chain_lines(s, base)])
    lines[-1].set_color(GOLD)
    block = stack(head, *lines, buff=0.25)
    block.head, block.lines = head, lines
    return block


# ================================================== 3D-look helpers ====

def tint(color, amount, towards=BLACK):
    """``color`` moved ``amount`` of the way towards ``towards``."""
    return interpolate_color(ManimColor(color), ManimColor(towards), amount)


class Slab(VGroup):
    """A box drawn with depth: front face, lit top, shaded right side and a
    soft shadow. Labels go on ``front`` so text stays flat and readable.
    Used only for the key object of a video."""

    def __init__(self, width, height, color, depth=0.28, fill=PANEL):
        super().__init__()
        d = DEPTH_DIR * depth
        self.front = Rectangle(width=width, height=height, stroke_color=color, stroke_width=2.5,
                               fill_color=fill, fill_opacity=1)
        ul, ur, dr = self.front.get_corner(UL), self.front.get_corner(UR), self.front.get_corner(DR)
        self.top = Polygon(ul, ur, ur + d, ul + d, stroke_color=color, stroke_width=2,
                           fill_color=tint(color, 0.55), fill_opacity=1)
        self.side = Polygon(ur, dr, dr + d, ur + d, stroke_color=color, stroke_width=2,
                            fill_color=tint(color, 0.75), fill_opacity=1)
        self.shadow = Polygon(self.front.get_corner(DL) + DOWN * 0.05, dr + DOWN * 0.05, dr + d * 0.6 + DOWN * 0.1,
                              self.front.get_corner(DL) + d * 0.6 + DOWN * 0.1, stroke_width=0,
                              fill_color=BLACK, fill_opacity=0.4)
        self.add(self.shadow, self.side, self.top, self.front)


# ======================================================== characters ====
# Drawn with polygons, lines and circles only (no rectangles), so they never
# count as boxes for the layout check. Both are built with their base on y = 0.

def teacher_figure(scale=1.0):
    """The teacher, waist up, turned towards the board.

    ``fig.arm`` (arm and pointer) swings about its first point, the shoulder.
    ``fig.voice`` (speech arcs) is placed with the figure but is not part of
    it, so it can come and go."""
    body = Polygon([-0.55, 0, 0], [0.55, 0, 0], [0.4, 0.95, 0], [-0.4, 0.95, 0], stroke_color=MAIN,
                   stroke_width=2.5, fill_color=tint(MAIN, 0.6), fill_opacity=1).round_corners(0.12)
    head = Circle(radius=0.3, stroke_color=INK, stroke_width=2.5, fill_color=PANEL, fill_opacity=1)
    head.move_to([0.04, 1.3, 0])
    c = head.get_center()
    hair = Arc(radius=0.3, start_angle=40 * DEGREES, angle=170 * DEGREES, arc_center=c, stroke_color=MUTED,
               stroke_width=8)
    lenses = [Circle(radius=0.075, stroke_color=INK, stroke_width=2).move_to(c + np.array([x, 0.03, 0]))
              for x in (0.02, 0.2)]
    specs = VGroup(*lenses, Line(lenses[0].get_right(), lenses[1].get_left(), stroke_color=INK, stroke_width=2))
    mouth = Line(c + np.array([0.08, -0.14, 0]), c + np.array([0.2, -0.14, 0]), stroke_color=INK, stroke_width=2.5)
    shoulder = np.array([0.34, 0.78, 0.0])
    arm = VGroup(Line(shoulder, shoulder + RIGHT * 0.55, stroke_color=MAIN, stroke_width=9),
                 Line(shoulder + RIGHT * 0.5, shoulder + RIGHT * 1.0, stroke_color=INK, stroke_width=3),
                 Dot(shoulder + RIGHT * 0.55, radius=0.07, color=INK))
    arm.rotate(ARM_REST, about_point=shoulder)
    voice = VGroup(*[Arc(radius=r, start_angle=-35 * DEGREES, angle=70 * DEGREES,
                         arc_center=c + np.array([0.3, -0.12, 0]), stroke_color=GOLD, stroke_width=3)
                     for r in (0.13, 0.24)])
    fig = VGroup(body, head, hair, specs, mouth, arm)
    VGroup(fig, voice).scale(scale, about_point=ORIGIN)
    fig.arm, fig.voice = arm, voice
    return fig


def student_figure(scale=1.0):
    """A student, head and shoulders, turned towards the teacher.

    ``fig.arm`` (a raised hand) and ``fig.book`` (her notes) are placed with
    the figure but are not part of it: they are shown only when needed."""
    body = Polygon([-0.4, 0, 0], [0.4, 0, 0], [0.3, 0.42, 0], [-0.3, 0.42, 0], stroke_color=MUTED,
                   stroke_width=2.5, fill_color=tint(MUTED, 0.6), fill_opacity=1).round_corners(0.1)
    head = Circle(radius=0.23, stroke_color=INK, stroke_width=2.5, fill_color=PANEL, fill_opacity=1)
    head.move_to([-0.03, 0.62, 0])
    c = head.get_center()
    tail = Line(c + np.array([0.18, 0.1, 0]), c + np.array([0.36, -0.14, 0]), stroke_color=MUTED, stroke_width=7)
    hair = Arc(radius=0.23, start_angle=-30 * DEGREES, angle=170 * DEGREES, arc_center=c, stroke_color=MUTED,
               stroke_width=7)
    eyes = VGroup(*[Dot(c + np.array([x, 0.02, 0]), radius=0.025, color=INK) for x in (-0.13, 0.0)])
    mouth = Line(c + np.array([-0.12, -0.1, 0]), c + np.array([-0.02, -0.1, 0]), stroke_color=INK, stroke_width=2.5)
    fig = VGroup(body, tail, head, hair, eyes, mouth)
    fig.arm = VGroup(Line([-0.3, 0.34, 0], [-0.5, 0.95, 0], stroke_color=MUTED, stroke_width=8),
                     Dot([-0.5, 0.98, 0], radius=0.07, color=INK))
    fig.book = VGroup(Polygon([-0.42, 0.04, 0], [0.0, 0.04, 0], [0.0, 0.32, 0], [-0.42, 0.32, 0], stroke_color=GOLD,
                              stroke_width=2, fill_color=tint(GOLD, 0.55), fill_opacity=1),
                      Line([-0.21, 0.04, 0], [-0.21, 0.32, 0], stroke_color=GOLD, stroke_width=2))
    VGroup(fig, fig.arm, fig.book).scale(scale, about_point=ORIGIN)
    return fig


# ===================================================== this video ====

CRUMB_MODULE = "Computer Fundamentals"
CRUMB_LESSON = "Lesson 4: Number System Conversions"
CRUMB_VIDEO = "Video 1 of 5"
VIDEO_TITLE = "Converting to Decimal"
BEFORE_LABEL = "From the last lesson"
BEFORE_IDEA = "Value = sum of (digit × weight)"
TODAY_IDEA = "The expansion method and the double-and-add shortcut"

TEACHER_VOICE = "aditya"       # the INSTRUCTOR: every self.tell / self.ask / self.answer block
STUDENT_VOICE = "kavya"        # the STUDENT: every self.reply block (own voice, own narration)
TEACHER_PAUSE = 0.7            # silence after each teacher block (seconds), so speakers never run together
STUDENT_PAUSE = 0.6            # silence after each student block

IDEAS = [("Weights from the right", GOLD), ("Letters become numbers", MAIN),
         ("After the point: negative powers", MAIN), ("Long number: double and add", MAIN)]
P_EXPAND, P_LETTERS, P_FRACTION, P_DOUBLE = range(4)

YES, NO = "✓", "✗"


def value(s, base):
    """The value of ``s`` (which may have a radix point) in ``base``, as an exact fraction."""
    whole, _, frac = s.partition(".")
    v = Fraction(int(whole, base))
    for k, ch in enumerate(frac, 1):
        v += Fraction(int(ch, base), base ** k)
    return v


def double_and_add(s, base):
    """The running totals of the double-and-add method, one per digit."""
    totals, acc = [], 0
    for ch in s:
        acc = acc * base + int(ch, base)
        totals.append(acc)
    return totals


def chain_lines(s, base):
    """Double-and-add written out: "7", "7 × 8 + 2 = 58", "58 × 8 + 5 = 469"."""
    acc = double_and_add(s, base)
    return [str(acc[0])] + [f"{acc[k - 1]} × {base} + {int(s[k], base)} = {acc[k]}" for k in range(1, len(s))]


assert value("110101", 2) == 53 == 32 + 16 + 0 + 4 + 0 + 1
assert value("725", 8) == 469 == 448 + 16 + 5
assert value("3A7", 16) == 935 == 768 + 160 + 7 and int("A", 16) == 10
assert value("1011", 2) == 11 and value("0.101", 2) == Fraction(5, 8) and value("1011.101", 2) == 11.625
assert value("1A", 16) == 26 and value("0.8", 16) == 0.5 and value("1A.8", 16) == 26.5
assert double_and_add("110101", 2) == [1, 3, 6, 13, 26, 53]
assert double_and_add("725", 8) == [7, 58, 469] and double_and_add("3A7", 16) == [3, 58, 935]
assert value("1001", 2) == 9 == 8 + 1 and value("17", 8) == 15 == 8 + 7 and value("1F", 16) == 31 == 16 + 15
assert value("101", 2) == 5 and 1 * 32 + 0 * 16 + 1 * 8 == 40      # weights taken from the left
assert value("111", 2) == 7                                        # 1011 with its zero skipped


class ConvertingToDecimalVideo(LMSScene):
    lesson_title = "Converting to Decimal"

    def construct(self):
        self.setup_board()
        self.opening()
        self.open_panel("Key ideas", IDEAS)
        self.expand_binary()
        self.other_bases()
        self.from_the_right()
        self.with_a_point()
        self.double_add()
        self.mistakes()
        self.quick_test()
        self.summary()
        self.next_video()

    # ---------------------------------------------------- scene helpers --

    def setup_board(self):
        self.camera.background_color = BG
        self.pinned = []
        self.panel = None
        self.shown = set()            # panel rows already on screen
        self.prof = None              # the teacher figure
        self.talking = False          # the teacher's pointer is up
        self.kid = None               # the student figure
        self.bubble = None            # the student's speech balloon
        self.q = None

    def clear_stage(self, run_time=0.6):
        """Scene transition: fade out everything except pinned mobjects."""
        keep = set()
        for p in self.pinned:
            keep.update(p.get_family())
        others = [m for m in self.mobjects
                  if m not in keep and any(p not in keep for p in m.family_members_with_points())]
        if others:
            self.play(FadeOut(Group(*others)), run_time=run_time)

    def wipe(self):
        self.clear_stage()
        self.kid = None
        self.bubble = None
        self.q = None

    def card(self, content, width=None, height=None, color=MUTED, pad=0.3):
        """Container-aware card (grows to content, or fits content to a fixed width)."""
        if width is not None:
            fit_width(content, width - 2 * pad)
        w = width if width is not None else content.width + 2 * pad
        h = max(height or 0, content.height + 2 * pad)
        box = RoundedRectangle(corner_radius=0.18, width=w, height=h, stroke_color=color,
                               stroke_width=2.5, fill_color=PANEL, fill_opacity=1)
        box.move_to(content)
        self.validator.check_fit(content, box, margin=0.1)
        return VGroup(box, content)

    def stage(self):
        """(centre x, width) of the free area: full frame, or right of the pinned panel."""
        if self.panel is not None and self.panel in self.pinned:
            return STAGE_X, STAGE_W
        return 0.0, SAFE_W

    def zone(self, col):
        """(left x, right x, lowest y) of a board column.

        left  : the tall column; may run down to the floor
        right : above the student
        full  : the whole stage width, above the student
        wide  : the whole stage down to the floor (only while no student speaks)"""
        x, w = self.stage()
        lo, hi = x - w / 2, x + w / 2
        split = hi - STU_W - COL_GAP
        return {"left": (lo, split, FLOOR_Y), "right": (split + COL_GAP, hi, STU_TOP + 0.1),
                "full": (lo, hi, STU_TOP + 0.1), "wide": (lo, hi, FLOOR_Y)}[col]

    def put(self, mob, col="left", top=None, align="c", under=None, buff=0.3):
        """Place ``mob`` in a board column and fail loudly if it does not fit there.

        ``top`` is the y of its top edge (default: under the question slot), or
        give ``under`` to stack it below another mobject."""
        lo, hi, floor = self.zone(col)
        if mob.width > hi - lo + 1e-6:
            if (hi - lo) / mob.width < 0.8:           # a small squeeze is fine; more would hurt readability
                raise ValueError(f"{mob!r} is {mob.width:.2f} wide; column '{col}' is {hi - lo:.2f}.")
            mob.scale((hi - lo) / mob.width)
        if under is not None:
            top = under.get_bottom()[1] - buff
        elif top is None:
            top = BOARD_TOP
        x = {"c": (lo + hi) / 2, "l": lo + mob.width / 2, "r": hi - mob.width / 2}[align]
        mob.move_to(RIGHT * x + UP * (top - mob.height / 2))
        if mob.get_bottom()[1] < floor - 1e-6:
            raise ValueError(f"{mob!r} ends at y={mob.get_bottom()[1]:.2f}; column '{col}' ends at {floor:.2f}.")
        return mob

    def heading(self, s, color=MAIN):
        """A heading card under the top edge of the free area."""
        x, w = self.stage()
        t = fitted_text(s, w - 1.0, BODY, INK, BOLD, max_lines=1)
        c = self.card(t, color=color, pad=0.2)
        return c.move_to(RIGHT * x + UP * (CARD_TOP - c.height / 2))

    def begin(self, sid, title, head, color=MAIN):
        """Start a scene: section marker plus its heading card."""
        self.scene_start(sid, title=title)
        h = self.heading(head, color)
        self.play(FadeIn(h, shift=DOWN * 0.3), run_time=0.6)
        return h

    def finish(self, sid):
        self.wipe()
        self.scene_end(sid)

    # ---------------------------------------------- pinned side panel --

    def compact_panel(self, title, items, color=MUTED):
        """A docked checklist on the left; rows are filled in as ideas are defined."""
        rows = VGroup()
        for name, c in items:
            chip = Square(0.2, stroke_width=0, fill_color=c, fill_opacity=0.9)
            label = self.card_text(name, PANEL_W - 1.0, c, BOLD)
            row = VGroup(chip, label).arrange(RIGHT, buff=0.2, aligned_edge=UP)
            row.label, row.color = label, c
            rows.add(row)
        rows.arrange(DOWN, buff=0.28, aligned_edge=LEFT)
        content = VGroup(text(title, SMALL, MUTED, BOLD), rows).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        panel = self.card(content, width=PANEL_W, color=color, pad=0.25)
        panel.move_to(RIGHT * PANEL_X + UP * (CARD_TOP - panel.height / 2))
        panel.rows = rows
        return panel

    def open_panel(self, title, items, color=GOLD):
        """Dock the empty panel frame with the teacher under it and pin both; rows come with ``add_row``."""
        self.panel = self.compact_panel(title, items, color)
        self.prof = teacher_figure(TEACHER_SCALE)
        VGroup(self.prof, self.prof.voice).shift(RIGHT * (PANEL_X - 0.35) + UP * FLOOR_Y)
        if self.prof.get_top()[1] > self.panel.get_bottom()[1] - 0.15:
            raise ValueError("The key ideas panel leaves no room for the teacher; shorten the ideas.")
        self.play(FadeIn(self.panel[0]), FadeIn(self.panel[1][0]), FadeIn(self.prof, shift=UP * 0.15), run_time=0.8)
        self.pinned += [self.panel, self.prof, self.prof.voice]
        self.validator.check_in_frame(self.panel, self.prof)

    def add_row(self, k):
        """Panel row ``k`` appears: the idea has just been defined."""
        row = self.panel.rows[k]
        self.shown.add(k)
        self.play(FadeIn(row, shift=LEFT * 0.3), run_time=0.5)
        self.play(Indicate(row, color=row.color, scale_factor=1.06), run_time=0.6)

    def light(self, *ks):
        """Light panel rows ``ks``; dim the others. Rows not yet defined stay hidden."""
        anims = []
        for i, row in enumerate(self.panel.rows):
            if i not in self.shown:
                continue
            if i in ks:
                row.label.set_color(row.color)
                anims.append(Indicate(row, color=row.color, scale_factor=1.06))
            else:
                anims.append(row.label.animate.set_color(MUTED))
        return anims

    def all_lit(self):
        return [row.label.animate.set_color(row.color) for i, row in enumerate(self.panel.rows) if i in self.shown]

    def undock(self):
        """Release the panel and the teacher (end of the video)."""
        leaving = [self.panel, self.prof] + ([self.prof.voice] if self.talking else [])
        self.pinned.clear()
        self.play(*[FadeOut(m) for m in leaving], run_time=0.6)
        self.panel = self.prof = None
        self.talking = False

    # ------------------------------------------------------- text fitting --

    @staticmethod
    def flex_text(s, width, color=INK, weight=NORMAL):
        """Body text that steps down in size and up in lines rather than failing."""
        for sz, lines in [(BODY, 1), (LABEL, 2), (SMALL, 2), (SMALL, 3), (MIN_FONT, 4)]:
            try:
                return fitted_text(s, width, sz, color, weight, max_lines=lines)
            except ValueError:
                continue
        return fitted_text(s, width, MIN_FONT, color, NORMAL, max_lines=8)

    @staticmethod
    def card_text(s, width, color, weight=NORMAL):
        """Text for a narrow card: 24 pt in up to three lines, else a little smaller."""
        for sz, wt, lines in [(SMALL, weight, 3), (MIN_FONT, weight, 4), (20, weight, 4)]:
            try:
                return fitted_text(s, width, sz, color, wt, max_lines=lines)
            except ValueError:
                continue
        return fitted_text(s, width, MIN_FONT, color, NORMAL, max_lines=8)

    def note(self, s, color=MAIN, col="left", size=LABEL, font=FONT):
        """A note pill, sized to its column (one line, or two if it must). Place it with ``put``."""
        lo, hi, _ = self.zone(col)
        for sz in (size, SMALL):
            p = pill(s, color, sz, font=font)
            if p.width <= hi - lo:
                return p
        t = fitted_text(s, hi - lo - 0.6, SMALL, color, BOLD, max_lines=3, font=font)
        box = RoundedRectangle(corner_radius=0.22, width=t.width + 0.6, height=t.height + 0.32, stroke_color=color,
                               stroke_width=2, fill_color=color, fill_opacity=0.14)
        return VGroup(box, t.move_to(box))

    def ticks(self, items, col="full", size=LABEL, marks=None, color=GOLD):
        """Summary rows: a gold tick (or the given marks, e.g. "1.") and one line each."""
        lo, hi, _ = self.zone(col)
        marks = marks or ["✓"] * len(items)
        rows = VGroup(*[VGroup(text(m, size + 2 if m == "✓" else size, color, BOLD),
                               fitted_text(s, hi - lo - 0.9, size, INK, max_lines=2)).arrange(RIGHT, buff=0.3)
                        for m, s in zip(marks, items)])
        return rows.arrange(DOWN, buff=0.28, aligned_edge=LEFT)

    # ---------------------------------------------------------- the teacher --

    def speak(self):
        """Animations for the teacher starting to speak: pointer up to the board, speech arcs on."""
        if self.prof is None or self.talking:
            return []
        self.talking = True
        return [Rotate(self.prof.arm, ARM_SWING, about_point=self.prof.arm[0].get_start()), FadeIn(self.prof.voice)]

    def listen(self):
        """Animations for the teacher turning to listen: pointer down, speech arcs off."""
        if self.prof is None or not self.talking:
            return []
        self.talking = False
        return [Rotate(self.prof.arm, -ARM_SWING, about_point=self.prof.arm[0].get_start()), FadeOut(self.prof.voice)]

    def hush(self, stay=False):
        """The student stops speaking (and sits down, unless ``stay``); the teacher takes over."""
        anims = self.speak()
        if self.bubble is not None:
            anims.append(FadeOut(self.bubble))
            self.bubble = None
        if self.kid is not None and not stay:
            anims.append(FadeOut(self.kid))
            self.kid = None
        if anims:
            self.play(*anims, run_time=0.3)

    def teacher(self, nid, s, stay=False):
        """A teacher block: the student's balloon (if any) leaves, then the teacher speaks."""
        self.hush(stay)
        return self.narrate(id=nid, text=s, voice=TEACHER_VOICE, subtitle=True, pause_after=TEACHER_PAUSE)

    # ---------------------------------------------------------- the student --

    def student(self, nid, spoken, shown=None, hand=False, notes=False):
        """A student block: the student comes up and speaks in their own voice."""
        self.say(None if notes else (shown or spoken), hand, notes)
        return self.narrate(id=nid, text=spoken, voice=STUDENT_VOICE, subtitle=True, pause_after=STUDENT_PAUSE)

    def say(self, s=None, hand=False, notes=False):
        """The student at the bottom right, with what they say in a speech balloon.

        ``hand``  : the hand goes up first (the student is asking, not answering).
        ``notes`` : she holds her notebook. With ``s`` None there is no balloon."""
        x, w = self.stage()
        right = x + w / 2
        anims = self.listen()
        arm = None
        if self.kid is None:
            fig = student_figure(KID_SCALE)
            VGroup(fig, fig.arm, fig.book).shift(RIGHT * (right - KID_HALF) + UP * FLOOR_Y)
            self.kid = VGroup(fig, fig.book) if notes else fig
            anims.append(FadeIn(self.kid, shift=UP * 0.15))
            if hand:
                arm = fig.arm
                anims.append(FadeIn(arm, shift=UP * 0.15))
        balloon = None
        if s is not None:
            card = self.card(fitted_text(s, STU_TEXT_W, LABEL, INK, max_lines=3), color=MUTED, pad=0.2)
            card.move_to(RIGHT * (right - card.width / 2) + UP * (FLOOR_Y + KID_H + 0.22 + card.height / 2))
            if card.get_top()[1] > STU_TOP + 1e-6:
                raise ValueError(f"Speech balloon {s!r} is too tall ({card.get_top()[1]:.2f} > {STU_TOP}); shorten it.")
            tip = np.array([right - KID_HALF - 0.05, card.get_bottom()[1], 0.0])
            tail = Polygon(tip + LEFT * 0.12, tip + RIGHT * 0.12, tip + RIGHT * 0.05 + DOWN * 0.17, stroke_width=0,
                           fill_color=MUTED, fill_opacity=1)
            balloon = VGroup(card, tail)
        area = VGroup(*[m for m in (self.kid, balloon) if m is not None])
        self.validator.check_in_frame(area)
        self.keep_clear(area, f"student ({s!r})", skip=(self.kid, self.bubble))
        if arm is not None:                       # hand up first, then the question
            self.play(*anims, run_time=0.5)
            anims = [FadeOut(arm)]
        if balloon is not None:
            anims.append(FadeIn(balloon, shift=UP * 0.1))
        if self.bubble is not None:
            anims.append(FadeOut(self.bubble))
        self.bubble = balloon
        if anims:
            self.play(*anims, run_time=0.4)

    def keep_clear(self, mob, what, skip=()):
        """Fail if anything on screen (other than ``skip``) reaches into ``mob``'s area."""
        l, r = mob.get_left()[0], mob.get_right()[0]
        b, t = mob.get_bottom()[1], mob.get_top()[1]
        ours = set()
        for m in skip:
            if m is not None:
                ours.update(m.get_family())
        for top in self.mobjects:
            for part in top.family_members_with_points():
                if part in ours:
                    continue
                if (part.get_right()[0] > l + 0.02 and part.get_left()[0] < r - 0.02
                        and part.get_top()[1] > b + 0.02 and part.get_bottom()[1] < t - 0.02):
                    raise ValueError(f"The {what} would cover {part!r} (inside {top!r}).")

    # --------------------------------------------------------- questions --

    def show_q(self, s):
        """Every teacher question is on screen: a card in the question slot under the heading."""
        x, w = self.stage()
        row = VGroup(text("Q", BODY, GOLD, BOLD), self.flex_text(s, w - 1.6)).arrange(RIGHT, buff=0.3)
        c = self.card(row, width=w - 0.1, color=GOLD, pad=0.22)
        c.move_to(RIGHT * x + UP * (Q_TOP - c.height / 2))
        if c.height > Q_H + 1e-6:
            raise ValueError(f"Question {s!r} is too tall for the question slot ({c.height:.2f}); shorten it.")
        if self.q is None:
            self.keep_clear(c, f"question {s!r}")
            self.play(FadeIn(c, shift=UP * 0.15), run_time=0.4)
        else:
            self.play(FadeOut(self.q), FadeIn(c), run_time=0.4)
        self.q = c

    def drop_q(self):
        """Clear the question slot (the board may then use it)."""
        if self.q is not None:
            self.play(FadeOut(self.q), run_time=0.3)
            self.q = None

    # ------------------------------------------------- narration drivers --

    def cue(self, n, word):
        """Wait for ``word`` (or ``(word, occurrence)``) in narration ``n``."""
        phrase, occ = (word, 1) if isinstance(word, str) else word
        if n.estimated and not phrase.replace(" ", "").isalpha():
            raise ValueError(f"Anchor {phrase!r} must be plain words (no apostrophes, hyphens or digits).")
        try:
            self.at_word(n, phrase, occ)
        except ValueError:
            if n.estimated:
                raise                     # dry run: a wrong anchor is a bug in this file
            # with real audio the aligner may spell a word differently: just carry on

    def run(self, n, cues):
        """Play ``(word, what)`` pairs in spoken order, then hold until ``n`` ends.

        ``what`` is an animation, a list of animations, or a function that
        returns one (or plays things itself and returns None)."""
        for word, what in cues:
            if word:
                self.cue(n, word)
            if isinstance(what, (types.FunctionType, types.MethodType)):
                what = what()
            if what is None:
                continue
            self.play(*self.flat(what))
        self.wait_for_narration(n)
        return n

    @classmethod
    def flat(cls, what):
        """Animations from a single animation or a (nested) list of them."""
        if not isinstance(what, (list, tuple)):
            return [what]
        return [a for item in what for a in cls.flat(item)]

    def tell(self, nid, s, *cues):
        """Teacher statement with its visuals."""
        return self.run(self.teacher(nid, s), cues)

    def ask(self, nid, s, shown=None, *cues):
        """Teacher question: spoken, and shown in the question slot."""
        n = self.teacher(nid, s)
        self.show_q(shown or s)
        return self.run(n, cues)

    def answer(self, nid, s, *cues):
        """Teacher answering a student's question: the student stays up, listening."""
        return self.run(self.teacher(nid, s, stay=True), cues)

    def reply(self, nid, spoken, shown=None, *cues, hand=False, notes=False):
        """Student line: figure and balloon at the bottom right, own voice, own narration."""
        return self.run(self.student(nid, spoken, shown, hand, notes), cues)

    # ============================================== 0. OPENING ==========

    def opening(self):
        """Where we are (silent breadcrumb); the script's first two sentences are the recap."""
        self.scene_start("S00_opening", title="Opening")
        crumb = fit_width(text(f"{CRUMB_MODULE}  ›  {CRUMB_LESSON}  ›  {CRUMB_VIDEO}", SMALL, MUTED), SAFE_W - 1.0)
        title = fitted_text(VIDEO_TITLE, SAFE_W - 2.0, TITLE, INK, BOLD, max_lines=2)
        rule = Line(LEFT * 1.4, RIGHT * 1.4, color=GOLD, stroke_width=4)
        weights = table([["System", "Weights, from the right"], ["Binary", "…  32  16  8  4  2  1"],
                         ["Octal", "…  512  64  8  1"], ["Hexadecimal", "…  4096  256  16  1"]], [2.6, 4.6],
                        row_h=0.45, font=FONT)
        formula = text(BEFORE_IDEA, LABEL, MAIN, BOLD)
        before = VGroup(text(BEFORE_LABEL, SMALL, MUTED, BOLD), weights, formula).arrange(DOWN, buff=0.25)
        today = VGroup(text("In this video", SMALL, MUTED, BOLD),
                       fitted_text(TODAY_IDEA, SAFE_W - 3.0, LABEL, GOLD, BOLD, max_lines=2)).arrange(DOWN, buff=0.15)
        g = VGroup(crumb, title, rule, before, today).arrange(DOWN, buff=0.36)
        self.validator.check_in_frame(g)

        self.play(FadeIn(crumb), FadeIn(title, shift=UP * 0.2), Create(rule), run_time=0.9)
        self.play(FadeIn(before[0]), FadeIn(weights, shift=UP * 0.15), run_time=0.7)
        n = self.teacher("open_01", "Last time we said that the value of a number is the sum of each digit multiplied "
                                    "by its weight. Today we turn that sentence into a method.")
        self.cue(n, "sum")
        self.play(FadeIn(formula, shift=UP * 0.15))
        self.cue(n, "Today")
        self.play(FadeIn(today, shift=UP * 0.15))
        self.wait_for_narration(n)
        self.finish("S00_opening")

    # ============================================== 1. EXPANSION ========

    def expand_binary(self):
        self.begin("S01_expand", "The Expansion Method", "The expansion method")

        ex = self.put(expansion("110101", 2, raised=True), "left", BOARD_TOP)
        res = self.put(result("110101", 2, "53"), "left", under=ex, buff=0.4)

        self.tell("exp_01", "Let us take the binary number one one zero one zero one.",
                  ("binary", [FadeIn(ex.cells, shift=UP * 0.15), FadeIn(ex.names[1])]))
        self.ask("exp_02", "What is the first thing we write?")
        self.reply("exp_03", "The weights.", None,
                   (None, [FadeIn(ex.names[0]),
                           LaggedStart(*[FadeIn(w, shift=DOWN * 0.15) for w in reversed(ex.weights)], lag_ratio=0.35,
                                       run_time=1.6)]))
        self.hush()
        self.play(FadeIn(ex.names[2]),
                  LaggedStart(*[FadeIn(p, shift=DOWN * 0.15) for p in ex.products], lag_ratio=0.3), run_time=1.6)
        self.play(FadeIn(ex.plus), run_time=0.5)
        self.tell("exp_04", "So one one zero one zero one in binary is fifty-three in decimal.",
                  ("is", FadeIn(res, shift=UP * 0.1)), ("decimal", lambda: self.add_row(P_EXPAND)))

        self.finish("S01_expand")

    # ============================================== 2. OTHER BASES ======

    def other_bases(self):
        self.begin("S02_bases", "Octal and Hexadecimal", "Same method, other bases")

        oc = self.put(expansion("725", 8, size=0.9), "left", BOARD_TOP - 0.5)
        way = Arrow(oc.weights.get_right() + UP * 0.4 + RIGHT * 0.1, oc.weights.get_left() + UP * 0.4 + LEFT * 0.1,
                    color=GOLD, stroke_width=4, buff=0)
        oc_res = self.put(result("725", 8, "469", LABEL), "right", BOARD_TOP)

        hx = expansion("3A7", 16, size=0.9)
        a_is = mono("A = 10", LABEL, GOLD).next_to(hx.cells, RIGHT, buff=0.45)
        self.put(VGroup(hx, a_is), "left", BOARD_TOP - 0.5)
        hx_res = self.put(result("3A7", 16, "935", LABEL), "right", under=oc_res, buff=0.3)

        self.tell("oct_01", "Now let us do it again with a different system. Octal seven two five.",
                  ("Octal", [FadeIn(oc.cells, shift=UP * 0.15), FadeIn(oc.names[1])]))
        self.ask("oct_02", "What are the weights?")
        self.reply("oct_03", "One, eight, sixty-four.", "1, 8, 64.",
                   ("One", [FadeIn(oc.names[0], run_time=0.35), FadeIn(oc.weights[2], shift=DOWN * 0.15, run_time=0.35)]),
                   ("eight", FadeIn(oc.weights[1], shift=DOWN * 0.15, run_time=0.35)),
                   (None, FadeIn(oc.weights[0], shift=DOWN * 0.15, run_time=0.35)))
        self.tell("oct_04", "Reading from the right.", (None, GrowArrow(way)))
        self.play(FadeIn(oc.names[2]),
                  LaggedStart(*[FadeIn(p, shift=DOWN * 0.15) for p in oc.products], lag_ratio=0.3), run_time=1.2)
        self.play(FadeIn(oc.plus), FadeIn(oc_res, shift=UP * 0.1), run_time=0.6)

        self.drop_q()
        self.play(FadeOut(VGroup(oc, way)), run_time=0.5)
        self.tell("hex_01", "Hexadecimal three A seven. The first thing to do before multiplying is to look for "
                            "letters.",
                  ("Hexadecimal", [FadeIn(hx.cells, shift=UP * 0.15), FadeIn(hx.names[1])]),
                  ("letters", mark(hx.cells[1])))
        self.ask("hex_02", "What is A?")
        self.reply("hex_03", "Ten.", None, (None, FadeIn(a_is, shift=LEFT * 0.15, run_time=0.5)))
        self.hush()
        self.play(FadeIn(hx.names[0]),
                  LaggedStart(*[FadeIn(w, shift=DOWN * 0.15) for w in reversed(hx.weights)], lag_ratio=0.35),
                  run_time=1.2)
        self.play(FadeIn(hx.names[2]),
                  LaggedStart(*[FadeIn(p, shift=DOWN * 0.15) for p in hx.products], lag_ratio=0.3), run_time=1.2)
        self.play(FadeIn(hx.plus), FadeIn(hx_res, shift=UP * 0.1), run_time=0.6)
        self.add_row(P_LETTERS)

        self.finish("S02_bases")

    # ============================================== 3. FROM THE RIGHT ===

    def from_the_right(self):
        self.begin("S03_right", "Why From the Right", "Why from the right?")

        six = bit_cells("110101", 0.62)
        three = bit_cells("101", 0.62)
        three.next_to(six, DOWN, buff=1.0).align_to(six, RIGHT)
        w_six = above(six, ["32", "16", "8", "4", "2", "1"])
        w_three = above(three, ["4", "2", "1"])
        w_wrong = above(three, ["32", "16", "8"], color=MUTED)      # the weights she practised, from the left
        bad = verdict("= 40", NO, MUTED).next_to(three, RIGHT, buff=0.4)
        good = verdict("= 5", YES, GOLD).next_to(three, RIGHT, buff=0.4)
        board = self.put(VGroup(six, w_six, three, w_three, w_wrong, bad, good), "left", BOARD_HIGH)
        rule = self.put(self.note("Rightmost digit: position 0, weight 1", GOLD), "left", under=board, buff=0.45)

        self.play(FadeIn(six, shift=UP * 0.15), FadeIn(w_six), run_time=0.8)
        self.reply("q_01", "Why do we write the weights from the right?", hand=True)
        self.answer("q_02", "Because the rightmost digit is always position zero and has weight one. If you start "
                            "from the left you will misplace weights as soon as the number has a different number "
                            "of digits from the one you practised on. Always start from the right.",
                    ("rightmost", [mark(six[-1]), FadeIn(rule, shift=UP * 0.1)]),
                    ("left", [FadeIn(three, shift=UP * 0.15), FadeIn(w_wrong)]),
                    ("misplace", FadeIn(bad, shift=LEFT * 0.15)),
                    ("Always", [FadeOut(w_wrong), FadeOut(bad), FadeIn(w_three), FadeIn(good), mark(three[-1])]))

        self.finish("S03_right")

    # ============================================== 4. WITH A POINT =====

    def with_a_point(self):
        self.begin("S04_point", "Numbers With a Point", "Numbers with a point")

        whole, frac, dot = point_cells("1011", "101")
        w_whole = above(whole, ["8", "4", "2", "1"])
        w_frac = above(frac, ["1/2", "1/4", "1/8"])
        powers = VGroup(*[text(s, MIN_FONT, MUTED).next_to(c, DOWN, buff=0.12)
                          for s, c in zip(("2⁻¹", "2⁻²", "2⁻³"), frac)])
        parts = table([["integer", "8 + 0 + 2 + 1", "= 11"], ["fraction", "1/2 + 0 + 1/8", "= 0.625"]],
                      [1.6, 2.6, 1.5], row_h=0.5, size=SMALL, head=False)
        parts.col(0).set_color(MUTED)
        parts.col(2).set_color(GOLD)
        number = VGroup(whole, frac, dot, w_whole, w_frac, powers)
        parts.next_to(number, DOWN, buff=0.35)
        total = result("1011.101", 2, "11.625").next_to(parts, DOWN, buff=0.35)
        block = self.put(VGroup(number, parts, total), "left", BOARD_TOP)
        kept = self.put(result("1011.101", 2, "11.625", LABEL), "right", BOARD_TOP)

        h_whole, h_frac, h_dot = point_cells("1A", "8", 0.8)
        hw_whole = above(h_whole, ["16", "1"])
        hw_frac = above(h_frac, ["1/16"])
        h_parts = table([["integer", "1 × 16 + 10", "= 26"], ["fraction", "8 × 1/16", "= 0.5"]],
                        [1.6, 2.6, 1.5], row_h=0.5, size=SMALL, head=False)
        h_parts.col(0).set_color(MUTED)
        h_parts.col(2).set_color(GOLD)
        h_number = VGroup(h_whole, h_frac, h_dot, hw_whole, hw_frac)
        h_parts.next_to(h_number, DOWN, buff=0.4)
        h_total = result("1A.8", 16, "26.5").next_to(h_parts, DOWN, buff=0.4)
        self.put(VGroup(h_number, h_parts, h_total), "left", BOARD_TOP)

        self.tell("frac_01", "Now what about numbers with a point? Look at one zero one one point one zero one in "
                             "binary. The integer part works as before. For the fractional part, the weights "
                             "continue to the right of the point as negative powers.",
                  ("Look", FadeIn(VGroup(whole, frac, dot), shift=UP * 0.15)),
                  ("integer", LaggedStart(*[FadeIn(w, shift=DOWN * 0.15) for w in reversed(w_whole)], lag_ratio=0.3)),
                  ("negative", LaggedStart(*[FadeIn(p, shift=UP * 0.1) for p in powers], lag_ratio=0.3)))
        self.ask("frac_02", "What is the weight of the first place after the point?", None, (None, mark(frac[0])))
        self.reply("frac_03", "One half.", None, (None, FadeIn(w_frac[0], shift=DOWN * 0.15, run_time=0.5)))
        self.hush()
        self.play(FadeIn(w_frac[1], shift=DOWN * 0.15), FadeIn(w_frac[2], shift=DOWN * 0.15), run_time=0.6)
        self.play(LaggedStart(FadeIn(parts.rows[0], shift=RIGHT * 0.15), FadeIn(parts.rows[1], shift=RIGHT * 0.15),
                              lag_ratio=0.6), run_time=1.8)
        self.play(FadeIn(total, shift=UP * 0.1), run_time=0.6)

        self.drop_q()
        self.play(FadeOut(block), FadeIn(kept), run_time=0.6)
        self.tell("frac_04", "Hexadecimal works the same way. Take one A point eight in hexadecimal. The integer "
                             "part is one times sixteen plus A, which is twenty-six. The fraction eight is worth "
                             "eight sixteenths, which is zero point five. So the answer is twenty-six point five.",
                  ("Take", FadeIn(VGroup(h_whole, h_frac, h_dot), shift=UP * 0.15)),
                  ("integer", [FadeIn(hw_whole, shift=DOWN * 0.15), FadeIn(h_parts.rows[0], shift=RIGHT * 0.15)]),
                  ("fraction", [FadeIn(hw_frac, shift=DOWN * 0.15), FadeIn(h_parts.rows[1], shift=RIGHT * 0.15)]),
                  ("answer", FadeIn(h_total, shift=UP * 0.1)))
        self.add_row(P_FRACTION)

        self.finish("S04_point")

    # ============================================== 5. DOUBLE-AND-ADD ===

    def double_add(self):
        self.begin("S05_double", "Double-and-Add", "A faster way: double-and-add")

        digits = "110101"
        cells = self.put(bit_cells(digits, 0.72, raised=True), "left", BOARD_HIGH)
        steps = table([[d, "→", line] for d, line in zip(digits, chain_lines(digits, 2))], [0.6, 0.7, 3.6],
                      row_h=0.46, head=False)
        steps.col(1).set_color(MUTED)
        self.put(steps, "left", under=cells, buff=0.4)
        rule = self.put(self.note("Double, then add the next digit", GOLD, "right", SMALL), "right", BOARD_HIGH)

        octal, hexa = chain("725", 8), chain("3A7", 16)
        self.put(VGroup(octal, hexa).arrange(RIGHT, buff=1.0, aligned_edge=UP), "wide", BOARD_HIGH)

        short = self.put(self.note("Short binary number: the weights", MAIN), "left", BOARD_TOP)
        long_ = self.put(self.note("Long number: double-and-add", GOLD), "left", under=short, buff=0.3)

        self.tell("dbl_01", "Now here is a faster way. The expansion method is reliable but slow when numbers are "
                            "long. Suppose I take one one zero one zero one again. I start with the first digit. "
                            "Then for each next digit I double what I have and add the new digit.",
                  ("Suppose", FadeIn(cells, shift=UP * 0.15)),
                  ("first", [mark(cells[0]), FadeIn(steps.rows[0], shift=RIGHT * 0.15)]),
                  ("double", FadeIn(rule, shift=UP * 0.1)))
        for k in range(1, len(digits)):           # the teacher writes: one digit, one line
            self.play(unmark(cells[k - 1]), mark(cells[k]), FadeIn(steps.rows[k], shift=RIGHT * 0.15), run_time=0.6)
        self.tell("dbl_02", "Same answer, fifty-three, with no weights to remember.",
                  ("answer", Indicate(steps.rows[-1], color=GOLD, scale_factor=1.08)))

        self.play(FadeOut(VGroup(cells, steps, rule)), run_time=0.5)
        self.tell("dbl_03", "For octal, multiply by eight instead of two. For seven two five, start with seven, "
                            "then seven times eight plus two is fifty-eight, then fifty-eight times eight plus five "
                            "is four hundred and sixty-nine.",
                  ("octal", FadeIn(octal.head, shift=UP * 0.1)), ("start", FadeIn(octal.lines[0], shift=RIGHT * 0.15)),
                  ("times", FadeIn(octal.lines[1], shift=RIGHT * 0.15)),
                  (("times", 2), FadeIn(octal.lines[2], shift=RIGHT * 0.15)))
        self.tell("dbl_04", "For hexadecimal, multiply by sixteen. For three A seven, we start with three, then "
                            "three times sixteen plus ten is fifty-eight, then fifty-eight times sixteen plus seven "
                            "is nine hundred and thirty-five.",
                  ("hexadecimal", FadeIn(hexa.head, shift=UP * 0.1)), ("start", FadeIn(hexa.lines[0], shift=RIGHT * 0.15)),
                  ("times", FadeIn(hexa.lines[1], shift=RIGHT * 0.15)),
                  (("times", 2), FadeIn(hexa.lines[2], shift=RIGHT * 0.15)))

        self.play(FadeOut(VGroup(octal, hexa)), run_time=0.5)
        self.ask("dbl_05", "Which method should we use?")
        self.reply("dbl_06", "Whichever one we make fewer mistakes with.")
        self.tell("dbl_07", "Exactly. For short binary numbers, the weights are easy. For long numbers, "
                            "double-and-add is easier. Practise both, and then choose.",
                  ("short", FadeIn(short, shift=UP * 0.1)), ("long", FadeIn(long_, shift=UP * 0.1)),
                  ("choose", lambda: self.add_row(P_DOUBLE)))

        self.finish("S05_double")

    # ============================================== 6. MISTAKES =========

    def mistakes(self):
        self.begin("S06_mistakes", "Typical Mistakes", "Typical mistakes")

        rows = self.put(self.ticks(["Weights assigned from the left instead of the right",
                                    "Forgetting that a letter has a value (A = 10, not 1)",
                                    "Using weight 10 for a non-decimal number",
                                    "Skipping a zero digit and shifting the weights"], "wide",
                                   marks=["1.", "2.", "3.", "4."]), "wide", BOARD_HIGH, "l")

        cells = bit_cells("1011", 0.7)
        w_ok = above(cells, ["8", "4", "2", "1"])
        w_bad = below(cells, ["4", "–", "2", "1"])                   # the zero skipped: every weight to its left shifts
        ok = verdict("= 11", YES, GOLD).next_to(cells, RIGHT, buff=0.5).set_y(w_ok.get_center()[1])
        bad = verdict("= 7", NO, MUTED).next_to(cells, RIGHT, buff=0.5).set_y(w_bad.get_center()[1])
        self.put(VGroup(cells, w_ok, w_bad, ok, bad), "wide", under=rows, buff=0.5)

        self.tell("mis_01", "Let us look at the typical mistakes. What goes wrong?",
                  ("wrong", LaggedStart(*[FadeIn(r, shift=RIGHT * 0.2) for r in rows], lag_ratio=0.5, run_time=2.4)))
        self.tell("mis_02", "The fourth one is subtle. A zero contributes nothing, but it still occupies a position. "
                            "If you skip it in your table, every weight to its left will be wrong.",
                  ("fourth", Indicate(rows[3], color=GOLD, scale_factor=1.04)),
                  ("zero", FadeIn(cells, shift=UP * 0.15)), ("nothing", mark(cells[1])),
                  ("position", [FadeIn(w_ok, shift=DOWN * 0.15), FadeIn(ok)]),
                  ("skip", [FadeIn(w_bad, shift=UP * 0.15), FadeIn(bad)]),
                  ("wrong", Indicate(bad, color=GOLD, scale_factor=1.15)))

        self.finish("S06_mistakes")

    # ============================================== 7. A QUICK TEST =====

    def quick_test(self):
        self.begin("S07_test", "A Quick Test", "A quick test")

        lines = stack(*[VGroup(num(s, b, BODY), mono(working, BODY, GOLD)).arrange(RIGHT, buff=0.3)
                        for s, b, working in (("1001", 2, "= 8 + 1 = 9"), ("17", 8, "= 8 + 7 = 15"),
                                              ("1F", 16, "= 16 + 15 = 31"))], buff=0.45)
        self.put(lines, "left", BOARD_TOP)

        self.ask("qt_01", "A quick test. What is one zero zero one, base two?", "What is (1001)₂?")
        self.reply("qt_02", "Eight plus one, so nine.", "8 plus 1, so 9.", (None, FadeIn(lines[0], shift=UP * 0.1)))
        self.ask("qt_03", "What is one seven, base eight?", "What is (17)₈?")
        self.reply("qt_04", "Eight plus seven, which is fifteen.", "8 plus 7, which is 15.",
                   (None, FadeIn(lines[1], shift=UP * 0.1)))
        self.ask("qt_05", "What is one F, base sixteen?", "What is (1F)₁₆?")
        self.reply("qt_06", "Sixteen plus fifteen, which is thirty-one.", "16 plus 15, which is 31.",
                   (None, FadeIn(lines[2], shift=UP * 0.1)))

        self.finish("S07_test")

    # ============================================== 8. SUMMARY ==========

    def summary(self):
        self.begin("S08_summary", "Summary", "Summary", GOLD)

        rows = self.put(self.ticks(["Write the weights from the right, multiply, and add",
                                    "Letters become numbers first",
                                    "Fractions: negative powers after the point",
                                    "Long numbers: double-and-add is faster"]), "full", BOARD_HIGH, "l")

        self.tell("sum_01", "Good. Summarise.")
        self.reply("sum_02", "To convert to decimal, write the weights from the right, multiply, and add. Letters "
                             "become numbers first. For fractions, use negative powers after the point. For long "
                             "numbers, double-and-add is faster.", None,
                   ("weights", lambda: [FadeIn(rows[0], shift=RIGHT * 0.2), self.light(P_EXPAND)]),
                   ("Letters", lambda: [FadeIn(rows[1], shift=RIGHT * 0.2), self.light(P_LETTERS)]),
                   ("fractions", lambda: [FadeIn(rows[2], shift=RIGHT * 0.2), self.light(P_FRACTION)]),
                   ("long", lambda: [FadeIn(rows[3], shift=RIGHT * 0.2), self.light(P_DOUBLE)]),
                   notes=True)
        self.hush()
        self.play(*self.all_lit())
        self.finish("S08_summary")

    # ============================================== 9. NEXT =============

    def next_video(self):
        self.scene_start("S09_next", title="Next: Converting from Decimal")
        final = VGroup(pill("Sum of (digit × weight)", MAIN, LABEL), text("or", LABEL, MUTED),
                       pill("Double-and-add", MAIN, LABEL)).arrange(RIGHT, buff=0.35)
        self.put(final, "wide", BOARD_TOP)
        nxt = self.put(self.note("Next: Converting from decimal", GOLD, "wide", BODY), "wide", under=final, buff=0.7)
        self.play(LaggedStart(*[FadeIn(p, shift=UP * 0.1) for p in final], lag_ratio=0.3), run_time=1.0)
        self.ask("next_01", "What about the reverse? If I give you forty-five in decimal, how would you write it in "
                            "binary?", "If I give you 45 in decimal, how would you write it in binary?",
                 ("binary", FadeIn(nxt, scale=1.1)))
        self.undock()
        self.finish("S09_next")

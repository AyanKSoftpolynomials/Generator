"""
animation.py for the LMS video generator.

Course : C-CAT Computer Fundamentals
Lesson : Lesson 4 - Number System Conversions and Objective Practice
Video  : 04 Video 2 - Converting from Decimal

Source script:
  CCAT_Computer_Fundamentals_Scripts_Lessons_1-5/PDF/Lesson 4 - Number System Conversions and Objective Practice/04 Video 2 - Converting from Decimal.pdf
  The script has no speaker labels. Every line was labelled as below:
    TEACHER  spoken by the teacher: ``self.tell`` / ``self.ask`` (TEACHER_VOICE). Drives the board.
    STUDENT  spoken by a student: ``self.reply`` (STUDENT_VOICE). Every student answer is its own
             narration and appears as a card at the bottom right.
    STAGE    stage direction: not narrated, it becomes the visuals (or the name on the student card).
    BOARD    what the board shows: on screen, not spoken.
  Spoken text uses words ("one zero one one"); the cards and the board show digits ("1011").

Speaker split:
  01 TITLE   Converting from Decimal: Repeated Division and Repeated Multiplication
  02 STAGE   The board shows 45.
  03 TEACHER We want 45 in binary. Think about what the lowest bit tells us. If we divide 45 by 2, what does
             the remainder tell us?
  04 STUDENT Whether the number is odd or even.
  05 TEACHER Exactly. The remainder is the lowest bit, since the lowest bit of a binary number says whether
             it is odd or even. So we take the remainder as the last bit, and then repeat the process on the
             quotient, which has lost its lowest bit. We peel off one bit at a time.
  06 STAGE   The teacher writes.
  07 BOARD   45 / 2 = 22  remainder 1
  08 BOARD   22 / 2 = 11  remainder 0
  09 BOARD   11 / 2 =  5  remainder 1
  10 BOARD    5 / 2 =  2  remainder 1
  11 BOARD    2 / 2 =  1  remainder 0
  12 BOARD    1 / 2 =  0  remainder 1
  13 TEACHER We stop when the quotient is 0. Now the important question. In which direction do we read the
             remainders?
  14 STUDENT From the top?
  15 TEACHER Think. The first remainder was the lowest bit. So the first remainder goes at the right end. We
             must read from the bottom up.
  16 STAGE   The board shows:
  17 BOARD   read upward:  1 0 1 1 0 1   ->   (101101) in binary
  18 TEACHER Can we check it? 32 plus 8 plus 4 plus 1 is 45. Yes.
  19 TEACHER The same method works for any base. Divide by the base instead of 2. Let us convert 156 into
             octal.
  20 STAGE   The board shows:
  21 BOARD   156 / 8 = 19  remainder 4
  22 BOARD    19 / 8 =  2  remainder 3
  23 BOARD     2 / 8 =  0  remainder 2
  24 BOARD   read upward: 234   ->   (234) in octal
  25 TEACHER Now the same number in hexadecimal. This time we divide by 16.
  26 BOARD   156 / 16 = 9  remainder 12
  27 BOARD     9 / 16 = 0  remainder 9
  28 STAGE   A student asks:
  29 STUDENT Remainder 12. What do we write?
  30 TEACHER We write the hexadecimal symbol for 12, which is C. So the answer is 9C. Always convert a
             remainder of 10 or more into a letter before writing it.
  31 TEACHER Let us try one with three hexadecimal digits. 500.
  32 BOARD   500 / 16 = 31  remainder 4
  33 BOARD    31 / 16 =  1  remainder 15  (F)
  34 BOARD     1 / 16 =  0  remainder 1
  35 BOARD   read upward: 1 F 4   ->   (1F4) in hexadecimal
  36 TEACHER Check. 1 times 256 is 256, F times 16 is 240, and 4. Total 500.
  37 TEACHER Now fractions. Take 0.625 in decimal. For the fractional part, the method changes. We multiply
             by the base, and the integer part that appears is the next digit.
  38 STAGE   The board shows:
  39 BOARD   0.625 x 2 = 1.25   digit 1
  40 BOARD   0.25  x 2 = 0.5    digit 0
  41 BOARD   0.5   x 2 = 1.0    digit 1    (fraction is now 0, stop)
  42 BOARD   read downward: .101
  43 TEACHER Here we read downward. Why do you think the direction is different?
  44 STUDENT Because the first digit we get is the one closest to the point.
  45 TEACHER Exactly. The first digit is the most significant of the fraction, so it is written first.
  46 TEACHER What about a number with both parts, such as 12.25? Convert each part separately. 12 gives 1100
             by division. 0.25 gives 0.01 by multiplication. So 12.25 in binary is 1100.01.
  47 TEACHER One important caution. Some decimal fractions never end in binary. For example, 0.1 becomes
             0.000110011 and keeps repeating. If a C-CAT question includes a fraction like this, it will tell
             you to stop after a stated number of places. Do not try to finish it.
  48 TEACHER Let us summarise the two procedures.
  49 STAGE   The board shows:
  50 BOARD   INTEGER PART    divide by base repeatedly, read remainders UP
  51 BOARD   FRACTION PART   multiply by base repeatedly, read integers DOWN
  52 TEACHER Now the common mistakes.
  53 STAGE   The teacher lists them.
  54 BOARD   1. reading the remainders from the top
  55 BOARD   2. stopping before the quotient reaches 0
  56 BOARD   3. writing 10, 11, 12 instead of A, B, C
  57 BOARD   4. using the integer-part method on the fraction
  58 TEACHER Quick test. What is 25 in binary?
  59 STUDENT 25, 12 r 1, 6 r 0, 3 r 0, 1 r 1, 0 r 1. Reading upward: 11001.
  60 TEACHER What is 8 in octal?
  61 STUDENT 10.
  62 TEACHER What is 255 in hexadecimal?
  63 STUDENT FF.
  64 TEACHER Good.
  65 STAGE   A student reads from her notes.
  66 STUDENT Divide repeatedly for the whole part and read upward. Multiply repeatedly for the fraction and
             read downward. Convert remainders of 10 or more into letters.
  67 TEACHER But dividing is slow when the numbers get large. Is there some trick for the conversions that go
             between binary, octal and hexadecimal, so that we can avoid all this arithmetic?
  68 STAGE   The board changes to:
  69 BOARD   NEXT: CONVERSION BY GROUPING

Notes:
  - Opening block ``open_01`` is not in the script: it is the usual breadcrumb opening
    (where we are, what came before, what this video covers).
  - Long teacher lines are split into two narrations where a statement is followed by a question.
  - Every worked answer is computed and asserted in the data block: 45 = 101101 (base 2),
    156 = 234 (base 8) = 9C (base 16), 500 = 1F4 (base 16), 0.625 = .101 (base 2),
    12.25 = 1100.01 (base 2), 0.1 = 0.000110011... (base 2), 25 = 11001 (base 2), 8 = 10 (base 8),
    255 = FF (base 16). The script's answers are all correct.

Style: 2D, three colours (blue main, grey support, gold highlight). The only drawn element is
the arrow that shows the reading direction. No raised boxes are needed in this video.
Pinned KEY IDEAS panel from the first scene to the end.

Section map:
  S00 Opening   S01 Decimal to binary   S02 Any base   S03 Three hexadecimal digits
  S04 Fractions   S05 Two procedures and the mistakes   S06 Quick test   S07 Summary   S08 Next
"""

import math
import types

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
# Zone map (the pinned panel is docked on the left for the whole lesson body):
#
#   +-----------+--------------------------------------------+
#   |  PANEL    |  heading card                               |
#   |  (pinned  |  question card  (Q_TOP .. Q_TOP - Q_H)      |
#   |   ideas)  |  board: LEFT column        | RIGHT column   |
#   |           |  (notes, tables; may run   | (short items)  |
#   |           |   down to the floor)       +----------------+
#   |           |                            | student card   |
#   +-----------+----------------------------+----------------+
#
# The student card always sits bottom right; notes always go in the left
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
STU_TEXT_W = 3.2                              # widest text on the student card
STU_W = STU_TEXT_W + 0.4                      # student card zone width
STU_TOP = -1.5                                # the student card never rises above this
COL_GAP = 0.3


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


def above(cells, labels, size=SMALL, color=GOLD, buff=0.15):
    """One small label over each cell (weights, values)."""
    return VGroup(*[mono(s, size, color).next_to(c, UP, buff=buff) for s, c in zip(labels, cells)])


def below(cells, labels, size=SMALL, color=MUTED, buff=0.15):
    """One small label under each cell (positions, digits)."""
    return VGroup(*[mono(s, size, color).next_to(c, DOWN, buff=buff) for s, c in zip(labels, cells)])


def mark(cell, color=GOLD):
    """Highlight a digit cell."""
    return cell.box.animate.set_stroke(color, 5)


def split(cells, group, gap, hidden=()):
    """Animations that pull ``cells`` apart into groups of ``group``, counted from the right.

    Cells listed in ``hidden`` are not on screen yet: they are moved at once."""
    n, anims = len(cells), []
    for i, c in enumerate(cells):
        g = (n - 1 - i) // group
        if g and c in hidden:
            c.shift(LEFT * g * gap)
        elif g:
            anims.append(c.animate.shift(LEFT * g * gap))
    return anims


def group_values(cells, group, gap, labels, size=BODY, color=GOLD, drop=0.45):
    """One label under each group, for the layout the row has after ``split``.

    Build this before the split is played. Labels run left to right."""
    n, out = len(cells), VGroup()
    count = math.ceil(n / group)
    for g in range(count - 1, -1, -1):
        members = VGroup(*[cells[i] for i in range(n) if (n - 1 - i) // group == g])
        x = members.get_center()[0] - g * gap
        out.add(mono(labels[count - 1 - g], size, color).move_to([x, cells.get_bottom()[1] - drop, 0]))
    return out


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


# ===================================================== this video ====

CRUMB_MODULE = "Computer Fundamentals"
CRUMB_LESSON = "Lesson 4: Number System Conversions"
CRUMB_VIDEO = "Video 2 of 5"
VIDEO_TITLE = "Converting from Decimal"
BEFORE_LABEL = "Last video"
BEFORE_IDEA = "To decimal: sum of (digit × weight)"
TODAY_IDEA = "Repeated division, and repeated multiplication for fractions"

TEACHER_VOICE = "vijay"
STUDENT_VOICE = "kavya"        # students speak in their own voice, in their own blocks
TEACHER_PAUSE = 0.7            # silence after each teacher block (seconds), so speakers never run together
STUDENT_PAUSE = 0.6            # silence after each student block

IDEAS = [("Divide by the base, keep the remainders", GOLD), ("Stop when the quotient is 0", MAIN),
         ("Integer part: read UP", MAIN), ("Remainder 10 or more: a letter", MAIN),
         ("Fraction: multiply, read DOWN", MAIN)]
P_DIV, P_STOP, P_UP, P_LETTER, P_DOWN = range(5)

SYMBOLS = "0123456789ABCDEF"


def div_steps(n, base):
    """(number, quotient, remainder) for each step of repeated division."""
    steps = []
    while n:
        steps.append((n, n // base, n % base))
        n //= base
    return steps


def read_up(steps):
    return "".join(SYMBOLS[r] for _, _, r in reversed(steps))


def mul_steps(numerator, denominator, base, places):
    """(fraction, product, digit) for repeated multiplication, on an exact fraction."""
    steps = []
    for _ in range(places):
        if numerator == 0:
            break
        product = numerator * base
        steps.append((numerator / denominator, product / denominator, product // denominator))
        numerator = product % denominator
    return steps


S45, S156_8, S156_16, S500, S25 = (div_steps(45, 2), div_steps(156, 8), div_steps(156, 16), div_steps(500, 16),
                                   div_steps(25, 2))
F625 = mul_steps(625, 1000, 2, 8)

assert read_up(S45) == "101101" and [q for _, q, _ in S45] == [22, 11, 5, 2, 1, 0] and 32 + 8 + 4 + 1 == 45
assert read_up(S156_8) == "234" and [(q, r) for _, q, r in S156_8] == [(19, 4), (2, 3), (0, 2)]
assert read_up(S156_16) == "9C" and [(q, r) for _, q, r in S156_16] == [(9, 12), (0, 9)]
assert read_up(S500) == "1F4" and [(q, r) for _, q, r in S500] == [(31, 4), (1, 15), (0, 1)]
assert 1 * 256 + 15 * 16 + 4 == 500 and 15 * 16 == 240
assert F625 == [(0.625, 1.25, 1), (0.25, 0.5, 0), (0.5, 1.0, 1)]
assert format(12, "b") == "1100" and [d for _, _, d in mul_steps(25, 100, 2, 8)] == [0, 1]
assert "".join(str(d) for _, _, d in mul_steps(1, 10, 2, 9)) == "000110011"
assert read_up(S25) == "11001" and [(q, r) for _, q, r in S25] == [(12, 1), (6, 0), (3, 0), (1, 1), (0, 1)]
assert format(8, "o") == "10" and format(255, "X") == "FF"


class ConvertingFromDecimalVideo(LMSScene):
    lesson_title = "Converting from Decimal"

    def construct(self):
        self.setup_board()
        self.opening("open_01", "Last time we converted binary, octal and hexadecimal numbers to decimal. In this "
                                "video we go the other way, from decimal to any base, by repeated division, and for "
                                "fractions by repeated multiplication.", "video")
        self.open_panel("Key ideas", IDEAS)
        self.to_binary()
        self.any_base()
        self.three_hex_digits()
        self.fractions()
        self.procedures()
        self.quick_test()
        self.summary()
        self.next_video()

    # ---------------------------------------------------- scene helpers --

    def setup_board(self):
        self.camera.background_color = BG
        self.pinned = []
        self.panel = None
        self.shown = set()            # panel rows already on screen
        self.bubble = None
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
        right : above the student card
        full  : the whole stage width, above the student card
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
        """Dock the empty panel frame and pin it; rows are added later with ``add_row``."""
        self.panel = self.compact_panel(title, items, color)
        self.play(FadeIn(self.panel[0]), FadeIn(self.panel[1][0]), run_time=0.8)
        self.pinned.append(self.panel)
        self.validator.check_in_frame(self.panel)

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
        """Release the panel (end of the video)."""
        self.pinned.clear()
        self.play(FadeOut(self.panel), run_time=0.6)
        self.panel = None

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

    def para(self, s, col="left", color=INK, size=LABEL, weight=NORMAL, max_lines=3, font=FONT):
        """Plain text fitted to a column."""
        lo, hi, _ = self.zone(col)
        return fitted_text(s, hi - lo - 0.1, size, color, weight, max_lines=max_lines, font=font)

    def ticks(self, items, col="full", size=LABEL, marks=None, color=GOLD):
        """Summary rows: a gold tick (or the given marks, e.g. "1.") and one line each."""
        lo, hi, _ = self.zone(col)
        marks = marks or ["✓"] * len(items)
        rows = VGroup(*[VGroup(text(m, size + 2 if m == "✓" else size, color, BOLD),
                               fitted_text(s, hi - lo - 0.9, size, INK, max_lines=2)).arrange(RIGHT, buff=0.3)
                        for m, s in zip(marks, items)])
        return rows.arrange(DOWN, buff=0.28, aligned_edge=LEFT)

    # ------------------------------------------------------ speaker blocks --

    def teacher(self, nid, s):
        """A teacher block: the student card (if any) leaves, then the teacher speaks."""
        self.hush()
        return self.narrate(id=nid, text=s, voice=TEACHER_VOICE, subtitle=True, pause_after=TEACHER_PAUSE)

    def student(self, nid, spoken, shown=None, who="Student"):
        """A student block: the answer appears as a card, then the student speaks it."""
        self.say(shown or spoken, who)
        return self.narrate(id=nid, text=spoken, voice=STUDENT_VOICE, subtitle=True, pause_after=STUDENT_PAUSE)

    def say(self, s, who="Student"):
        """The student card at the bottom right (replaces the previous one)."""
        x, w = self.stage()
        body = VGroup(text(who, SMALL, MUTED, BOLD), fitted_text(s, STU_TEXT_W, LABEL, INK, max_lines=3))
        body.arrange(DOWN, buff=0.1, aligned_edge=LEFT)
        card = self.card(body, color=MUTED, pad=0.2)
        card.move_to(RIGHT * (x + w / 2 - card.width / 2) + UP * (FLOOR_Y + card.height / 2))
        if card.get_top()[1] > STU_TOP + 1e-6:
            raise ValueError(f"Student card {s!r} is too tall ({card.get_top()[1]:.2f} > {STU_TOP}); shorten it.")
        self.validator.check_in_frame(card)
        self.keep_clear(card, f"student card {s!r}")
        anims = [FadeIn(card, shift=UP * 0.15)]
        if self.bubble is not None:
            anims.append(FadeOut(self.bubble))
        self.bubble = card
        self.play(*anims, run_time=0.4)

    def hush(self):
        """Remove the student card, if any."""
        if self.bubble is not None:
            self.play(FadeOut(self.bubble), run_time=0.3)
            self.bubble = None

    def keep_clear(self, mob, what):
        """Fail if anything on screen (other than the old student card) reaches into ``mob``'s area."""
        l, r = mob.get_left()[0], mob.get_right()[0]
        b, t = mob.get_bottom()[1], mob.get_top()[1]
        skip = set(self.bubble.get_family()) if self.bubble is not None else set()
        for top in self.mobjects:
            for part in top.family_members_with_points():
                if part in skip:
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

    def reply(self, nid, spoken, shown=None, *cues, who="Student"):
        """Student answer: card at the bottom right, own voice, own narration."""
        return self.run(self.student(nid, spoken, shown, who), cues)

    # ------------------------------------------------------ shared scenes --

    def opening(self, nid, spoken, word):
        """Where we are (breadcrumb), what came before, what this video covers."""
        self.scene_start("S00_opening", title="Opening")
        crumb = fit_width(text(f"{CRUMB_MODULE}  ›  {CRUMB_LESSON}  ›  {CRUMB_VIDEO}", SMALL, MUTED), SAFE_W - 1.0)
        title = fitted_text(VIDEO_TITLE, SAFE_W - 2.0, TITLE, INK, BOLD, max_lines=2)
        rule = Line(LEFT * 1.4, RIGHT * 1.4, color=GOLD, stroke_width=4)
        before = VGroup(text(BEFORE_LABEL, SMALL, MUTED, BOLD),
                        fitted_text(BEFORE_IDEA, SAFE_W - 3.0, LABEL, MAIN, BOLD, max_lines=2)).arrange(DOWN, buff=0.15)
        today = VGroup(text("In this video", SMALL, MUTED, BOLD),
                       fitted_text(TODAY_IDEA, SAFE_W - 3.0, LABEL, GOLD, BOLD, max_lines=2)).arrange(DOWN, buff=0.15)
        g = VGroup(crumb, title, rule, before, today).arrange(DOWN, buff=0.42)
        self.validator.check_in_frame(g)
        self.play(FadeIn(crumb), FadeIn(title, shift=UP * 0.2), Create(rule), run_time=0.9)
        n = self.teacher(nid, spoken)
        self.play(FadeIn(before, shift=UP * 0.15))
        self.cue(n, word)
        self.play(FadeIn(today, shift=UP * 0.15))
        self.wait_for_narration(n)
        self.finish("S00_opening")

    def next_up(self, s):
        """The closing 'next' card, centred in the left column."""
        return self.note(s, GOLD, "full", BODY)

    # ------------------------------------------------------ this video --

    def ladder(self, steps, base, row_h=0.45):
        """Repeated division as rows: number ÷ base, quotient, remainder (gold)."""
        tb = table([[f"{n} ÷ {base}", f"= {q}", f"r {r}"] for n, q, r in steps], [1.9, 1.2, 1.1], row_h=row_h,
                   head=False)
        tb.col(2).set_color(GOLD)
        return tb

    def reading(self, tb, upward=True):
        """The arrow beside the last column: read the digits upward (or downward)."""
        x = tb.get_right()[0] + 0.35
        lo, hi = tb.get_bottom()[1], tb.get_top()[1]
        a, b = (lo, hi) if upward else (hi, lo)
        return Arrow(RIGHT * x + UP * a, RIGHT * x + UP * b, color=GOLD, stroke_width=6, buff=0)

    # ===================================== 1. DECIMAL TO BINARY =========

    def to_binary(self):
        self.begin("S01_binary", "Decimal to Binary", "Decimal to binary: repeated division")

        tb = self.put(self.ladder(S45, 2), "left", BOARD_TOP)
        arrow = self.reading(tb)
        result = self.put(mono("Read upward: 101101 in binary", SMALL, GOLD), "left", under=tb, buff=0.3)
        check = self.put(mono("Check: 32 + 8 + 4 + 1 = 45", SMALL, MAIN), "left", under=result, buff=0.2)

        self.ask("div_01", "We want forty-five in binary. Think about what the lowest bit tells us. If we divide "
                           "forty-five by two, what does the remainder tell us?",
                 "If we divide 45 by 2, what does the remainder tell us?",
                 ("divide", lambda: [FadeIn(tb.cell[(0, 0)], shift=UP * 0.1), FadeIn(tb.cell[(0, 1)], shift=UP * 0.1)]))
        self.reply("div_02", "Whether the number is odd or even.", None,
                   (None, FadeIn(tb.cell[(0, 2)], scale=1.3)))
        self.tell("div_03", "Exactly. The remainder is the lowest bit, since the lowest bit of a binary number says "
                            "whether it is odd or even. So we take the remainder as the last bit, and then repeat "
                            "the process on the quotient, which has lost its lowest bit. We peel off one bit at a "
                            "time.",
                  ("lowest", Indicate(tb.cell[(0, 2)], color=GOLD, scale_factor=1.4)),
                  ("repeat", LaggedStart(*[FadeIn(r, shift=RIGHT * 0.15) for r in tb.rows[1:]], lag_ratio=0.6,
                                         run_time=4.0)),
                  (None, lambda: self.add_row(P_DIV)))
        self.tell("div_04", "We stop when the quotient is zero.",
                  ("quotient", Indicate(tb.cell[(5, 1)], color=GOLD, scale_factor=1.4)),
                  (None, lambda: self.add_row(P_STOP)))
        self.ask("div_05", "Now the important question. In which direction do we read the remainders?",
                 "In which direction do we read the remainders?")
        self.reply("div_06", "From the top?")
        self.tell("div_07", "Think. The first remainder was the lowest bit. So the first remainder goes at the "
                            "right end. We must read from the bottom up.",
                  ("first", Indicate(tb.cell[(0, 2)], color=GOLD, scale_factor=1.4)),
                  ("bottom", GrowArrow(arrow)), (None, FadeIn(result, shift=UP * 0.1)),
                  (None, lambda: self.add_row(P_UP)))
        self.tell("div_08", "Can we check it? Thirty-two plus eight plus four plus one is forty-five. Yes.",
                  ("check", FadeIn(check, shift=UP * 0.1)))

        self.finish("S01_binary")

    # ===================================== 2. ANY BASE ==================

    def any_base(self):
        self.begin("S02_any_base", "Any Base", "Any base: divide by the base")

        t8 = self.put(self.ladder(S156_8, 8), "left", BOARD_HIGH - 0.1)
        a8 = self.reading(t8)
        r8 = self.put(mono("Read upward: 234 in octal", SMALL, GOLD), "left", under=t8, buff=0.25)
        t16 = self.put(self.ladder(S156_16, 16), "left", under=r8, buff=0.55)
        a16 = self.reading(t16)
        c_tag = mono("= C", LABEL, GOLD).next_to(t16.cell[(0, 2)], RIGHT, buff=0.75)
        r16 = self.put(mono("Read upward: 9C in hexadecimal", SMALL, GOLD), "left", under=t16, buff=0.25)

        self.tell("ob_01", "The same method works for any base. Divide by the base instead of two. Let us convert "
                           "one hundred and fifty-six into octal.",
                  ("convert", LaggedStart(*[FadeIn(r, shift=RIGHT * 0.15) for r in t8.rows], lag_ratio=0.5,
                                          run_time=2.0)),
                  (None, GrowArrow(a8)), (None, FadeIn(r8, shift=UP * 0.1)))
        self.tell("ob_02", "Now the same number in hexadecimal. This time we divide by sixteen.",
                  ("divide", LaggedStart(*[FadeIn(r, shift=RIGHT * 0.15) for r in t16.rows], lag_ratio=0.5,
                                         run_time=1.6)))
        self.reply("ob_03", "Remainder twelve. What do we write?", "Remainder 12. What do we write?",
                   (None, Indicate(t16.cell[(0, 2)], color=GOLD, scale_factor=1.4)), who="A student asks")
        self.tell("ob_04", "We write the hexadecimal symbol for twelve, which is C. So the answer is nine C. Always "
                           "convert a remainder of ten or more into a letter before writing it.",
                  ("symbol", FadeIn(c_tag, shift=LEFT * 0.1)),
                  ("answer", lambda: [GrowArrow(a16), FadeIn(r16, shift=UP * 0.1)]),
                  ("letter", lambda: self.add_row(P_LETTER)))

        self.finish("S02_any_base")

    # ===================================== 3. THREE HEX DIGITS ==========

    def three_hex_digits(self):
        self.begin("S03_500", "Three Hexadecimal Digits", "Three hexadecimal digits: 500")

        tb = self.put(self.ladder(S500, 16, 0.55), "left", BOARD_HIGH - 0.1)
        f_tag = mono("= F", LABEL, GOLD).next_to(tb.cell[(1, 2)], RIGHT, buff=0.75)
        arrow = self.reading(tb)
        result = self.put(mono("Read upward: 1F4 in hexadecimal", SMALL, GOLD), "left", under=tb, buff=0.3)
        check = self.put(mono("Check: 256 + 240 + 4 = 500", SMALL, MAIN), "left", under=result, buff=0.25)

        self.tell("h5_01", "Let us try one with three hexadecimal digits. Five hundred.",
                  ("Five", LaggedStart(*[FadeIn(r, shift=RIGHT * 0.15) for r in tb.rows], lag_ratio=0.6,
                                       run_time=2.4)),
                  (None, FadeIn(f_tag, shift=LEFT * 0.1)), (None, GrowArrow(arrow)),
                  (None, FadeIn(result, shift=UP * 0.1)))
        self.tell("h5_02", "Check. One times two hundred and fifty-six is two hundred and fifty-six, F times "
                           "sixteen is two hundred and forty, and four. Total five hundred.",
                  ("Total", FadeIn(check, shift=UP * 0.1)), (None, lambda: self.light(P_UP, P_LETTER)))

        self.finish("S03_500")

    # ===================================== 4. FRACTIONS =================

    def fractions(self):
        self.begin("S04_fractions", "Fractions", "Fractions: repeated multiplication")

        tb = table([[f"{f:g} × 2", f"= {p:g}" if p != 1 else "= 1.0", f"digit {d}"] for f, p, d in F625],
                   [2.0, 1.4, 1.6], row_h=0.5, head=False)
        self.put(tb, "left", BOARD_TOP)
        tb.col(2).set_color(GOLD)
        arrow = self.reading(tb, upward=False)
        result = self.put(mono("Read downward: .101", SMALL, GOLD), "left", under=tb, buff=0.3)
        stop = self.put(text("Fraction is now 0: stop", SMALL, MUTED), "left", under=result, buff=0.2)
        both = stack(mono("12   → 1100  (division)", SMALL, INK), mono("0.25 → .01   (multiplication)", SMALL, INK),
                     mono("12.25 = 1100.01 in binary", SMALL, GOLD), buff=0.25)
        self.put(both, "left", BOARD_TOP, "l")
        never = self.put(mono("0.1 = 0.000110011… in binary", SMALL, MAIN), "left", under=both, buff=0.5, align="l")
        caution = self.put(self.note("It never ends: stop where the question says", GOLD), "left", under=never,
                           buff=0.25, align="l")

        self.tell("fr_01", "Now fractions. Take zero point six two five in decimal. For the fractional part, the "
                           "method changes. We multiply by the base, and the integer part that appears is the next "
                           "digit.",
                  ("multiply", FadeIn(tb.rows[0], shift=RIGHT * 0.15)),
                  ("next", LaggedStart(FadeIn(tb.rows[1], shift=RIGHT * 0.15), FadeIn(tb.rows[2], shift=RIGHT * 0.15),
                                       lag_ratio=0.6, run_time=1.6)),
                  (None, lambda: [FadeIn(result, shift=UP * 0.1), FadeIn(stop)]))
        self.ask("fr_02", "Here we read downward. Why do you think the direction is different?",
                 "Here we read downward. Why is the direction different?", ("downward", GrowArrow(arrow)))
        self.reply("fr_03", "Because the first digit we get is the one closest to the point.",
                   "The first digit we get is the one closest to the point.",
                   (None, Indicate(tb.cell[(0, 2)], color=GOLD, scale_factor=1.3)))
        self.tell("fr_04", "Exactly. The first digit is the most significant of the fraction, so it is written "
                           "first.", ("written", lambda: self.add_row(P_DOWN)))

        self.play(FadeOut(VGroup(tb, arrow, result, stop)), run_time=0.5)
        self.ask("fr_05", "What about a number with both parts, such as twelve point two five?",
                 "What about a number with both parts, such as 12.25?")
        self.tell("fr_06", "Convert each part separately. Twelve gives one one zero zero by division. Zero point "
                           "two five gives zero point zero one by multiplication. So twelve point two five in "
                           "binary is one one zero zero point zero one.",
                  ("division", FadeIn(both[0], shift=RIGHT * 0.15)),
                  ("multiplication", FadeIn(both[1], shift=RIGHT * 0.15)),
                  ("binary", FadeIn(both[2], shift=RIGHT * 0.15)))
        self.tell("fr_07", "One important caution. Some decimal fractions never end in binary. For example, zero "
                           "point one becomes zero point zero zero zero one one zero zero one one and keeps "
                           "repeating. If a C-CAT question includes a fraction like this, it will tell you to stop "
                           "after a stated number of places. Do not try to finish it.",
                  ("example", FadeIn(never, shift=UP * 0.1)), ("stop", FadeIn(caution, shift=UP * 0.1)))

        self.finish("S04_fractions")

    # ========================= 5. TWO PROCEDURES AND THE MISTAKES =======

    def procedures(self):
        self.begin("S05_procedures", "Two Procedures and the Mistakes", "Two procedures")

        tb = table([["Integer part", "Divide by the base", "Read remainders UP"],
                    ["Fraction part", "Multiply by the base", "Read integers DOWN"]], [2.5, 3.5, 3.5], row_h=0.6,
                   head=False, font=FONT)
        self.put(tb, "wide", BOARD_HIGH - 0.05)
        tb.col(0).set_color(GOLD)
        tb.col(2).set_color(MAIN)
        tag = text("Common mistakes", SMALL, MUTED, BOLD)
        rows = self.ticks(["Reading the remainders from the top", "Stopping before the quotient reaches 0",
                           "Writing 10, 11, 12 instead of A, B, C", "Using the integer-part method on the fraction"],
                          "wide", LABEL, ["1.", "2.", "3.", "4."])
        errors = self.put(stack(tag, rows, buff=0.3), "wide", under=tb, buff=0.55, align="l")

        self.tell("pr_01", "Let us summarise the two procedures.",
                  ("procedures", LaggedStart(FadeIn(tb.rows[0], shift=RIGHT * 0.15),
                                             FadeIn(tb.rows[1], shift=RIGHT * 0.15), lag_ratio=0.6, run_time=1.6)))
        self.tell("pr_02", "Now the common mistakes.",
                  ("mistakes", FadeIn(tag)),
                  (None, LaggedStart(*[FadeIn(r, shift=RIGHT * 0.2) for r in rows], lag_ratio=0.5, run_time=3.0)))
        self.play(Indicate(errors[1][0], color=GOLD, scale_factor=1.03), run_time=1.0)

        self.finish("S05_procedures")

    # ===================================== 6. QUICK TEST ================

    def quick_test(self):
        self.begin("S06_test", "Quick Test", "Quick test")

        tb = self.put(self.ladder(S25, 2, 0.42), "left", BOARD_TOP)
        arrow = self.reading(tb)
        result = self.put(mono("25 = 11001 in binary", SMALL, GOLD), "left", under=tb, buff=0.3)
        octal = self.put(mono("8 = 10 in octal", SMALL, GOLD), "right", BOARD_TOP)
        hexa = self.put(mono("255 = FF in hex", SMALL, GOLD), "right", under=octal, buff=0.35)

        self.ask("qt_01", "Quick test. What is twenty-five in binary?", "What is 25 in binary?")
        self.reply("qt_02", "Twenty-five, twelve remainder one, six remainder zero, three remainder zero, one "
                            "remainder one, zero remainder one. Reading upward: one one zero zero one.",
                   "Reading upward: 11001.",
                   ("twelve", FadeIn(tb.rows[0], shift=RIGHT * 0.15)), ("six", FadeIn(tb.rows[1], shift=RIGHT * 0.15)),
                   ("three", FadeIn(tb.rows[2], shift=RIGHT * 0.15)),
                   (("one", 2), FadeIn(tb.rows[3], shift=RIGHT * 0.15)),
                   (("zero", 3), FadeIn(tb.rows[4], shift=RIGHT * 0.15)),
                   ("upward", lambda: [GrowArrow(arrow), FadeIn(result, shift=UP * 0.1)]))
        self.ask("qt_03", "What is eight in octal?", "What is 8 in octal?")
        self.reply("qt_04", "One zero.", "10.", (None, FadeIn(octal, shift=UP * 0.1)))
        self.ask("qt_05", "What is two hundred and fifty-five in hexadecimal?", "What is 255 in hexadecimal?")
        self.reply("qt_06", "F F.", "FF.", (None, FadeIn(hexa, shift=UP * 0.1)))
        self.tell("qt_07", "Good.")

        self.finish("S06_test")

    # ============================================== 7. SUMMARY ==========

    def summary(self):
        self.begin("S07_summary", "Summary", "Summary", GOLD)

        rows = self.put(self.ticks(["Whole part: divide repeatedly, read upward",
                                    "Fraction: multiply repeatedly, read downward",
                                    "Remainders of 10 or more become letters"]), "full", BOARD_HIGH, "l")

        self.reply("sum_01", "Divide repeatedly for the whole part and read upward. Multiply repeatedly for the "
                             "fraction and read downward. Convert remainders of ten or more into letters.",
                   "Reading from her notes",
                   ("Divide", lambda: [FadeIn(rows[0], shift=RIGHT * 0.2), self.light(P_DIV, P_STOP, P_UP)]),
                   ("Multiply", lambda: [FadeIn(rows[1], shift=RIGHT * 0.2), self.light(P_DOWN)]),
                   ("Convert", lambda: [FadeIn(rows[2], shift=RIGHT * 0.2), self.light(P_LETTER)]),
                   who="A student")
        self.hush()
        self.play(*self.all_lit())
        self.finish("S07_summary")

    # ============================================== 8. NEXT =============

    def next_video(self):
        self.scene_start("S08_next", title="Next: Conversion by Grouping")
        three = VGroup(pill("Binary", MAIN, LABEL), text("↔", BODY, MUTED, BOLD), pill("Octal", MAIN, LABEL),
                       text("↔", BODY, MUTED, BOLD), pill("Hexadecimal", MAIN, LABEL)).arrange(RIGHT, buff=0.3)
        self.put(three, "full", BOARD_TOP)
        nxt = self.put(self.next_up("Next: Conversion by grouping"), "full", under=three, buff=0.7)
        self.tell("next_01", "But dividing is slow when the numbers get large.")
        self.ask("next_02", "Is there some trick for the conversions that go between binary, octal and hexadecimal, "
                            "so that we can avoid all this arithmetic?",
                 "Is there a trick for conversions between binary, octal and hexadecimal?",
                 ("binary", LaggedStart(*[FadeIn(p, shift=UP * 0.1) for p in three], lag_ratio=0.3)),
                 ("avoid", FadeIn(nxt, scale=1.1)))
        self.undock()
        self.finish("S08_next")

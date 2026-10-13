"""
animation.py for the LMS video generator.

Course : C-CAT Computer Fundamentals
Lesson : Lesson 3 - Number Systems Concepts and Representation
Video  : 04 Video 2 - Decimal and Binary

Source script:
  CCAT_Computer_Fundamentals_Scripts_Lessons_1-5/PDF/Lesson 3 - Number Systems Concepts and Representation/04 Video 2 - Decimal and Binary.pdf
  The script has no speaker labels. Every line was labelled as below:
    TEACHER  spoken by the teacher: ``self.tell`` / ``self.ask`` (TEACHER_VOICE). Drives the board.
    STUDENT  spoken by a student: ``self.reply`` (STUDENT_VOICE). Every student answer is its own
             narration and appears as a card at the bottom right.
    STAGE    stage direction: not narrated, it becomes the visuals (or the name on the student card).
    BOARD    what the board shows: on screen, not spoken.
  Spoken text uses words ("one zero one one"); the cards and the board show digits ("1011").

Speaker split:
  01 TITLE   Decimal and Binary: Place Values, Counting and the Meaning of n Bits
  02 STAGE   The board shows the number 5326.
  03 TEACHER We begin with a system you already know. What are the weights of each digit in this number?
  04 STUDENT 1, 10, 100 and 1000.
  05 STAGE   The teacher writes.
  06 BOARD   5326 = 5 x 10^3 + 3 x 10^2 + 2 x 10^1 + 6 x 10^0
  07 BOARD        = 5000 + 300 + 20 + 6
  08 TEACHER Now let us use exactly the same rule for a binary number. Look at 1011 in the binary system. We
             write the base as a small subscript, 1011 base 2, to show which system we are using. What are
             the weights here?
  09 STUDENT Powers of 2.
  10 TEACHER Yes. 1, 2, 4, 8.
  11 STAGE   The board shows:
  12 BOARD   position     3     2     1     0
  13 BOARD   weight      2^3   2^2   2^1   2^0
  14 BOARD                8     4     2     1
  15 BOARD   1011 (base 2) = 1 x 8 + 0 x 4 + 1 x 2 + 1 x 1
  16 BOARD                 = 8 + 0 + 2 + 1 = 11 in decimal
  17 TEACHER So 1011 in binary is the same quantity that we call eleven. The quantity did not change. Only
             the way of writing it changed.
  18 TEACHER Which is the largest weight in this number?
  19 STUDENT 8.
  20 TEACHER The leftmost bit, which carries the largest weight, is called the most significant bit, or MSB.
             The rightmost bit, with the smallest weight, is the least significant bit, or LSB.
  21 TEACHER Now let me ask you to count in binary. We begin at 0.
  22 STUDENT 0, 1.
  23 TEACHER And now? What comes after 1?
  24 STUDENT There is no 2.
  25 TEACHER Right. We have run out of digits, just as we run out at 9 in decimal. What do we do in decimal
             after 9?
  26 STUDENT Write 0 and carry 1.
  27 TEACHER Do the same in binary after 1.
  28 STUDENT 10.
  29 STAGE   The board fills in.
  30 BOARD   DECIMAL   BINARY
  31 BOARD      0         0
  32 BOARD      1         1
  33 BOARD      2        10
  34 BOARD      3        11
  35 BOARD      4       100
  36 BOARD      5       101
  37 BOARD      6       110
  38 BOARD      7       111
  39 BOARD      8      1000
  40 STAGE   A student frowns.
  41 STUDENT Is 10 in binary the number ten?
  42 TEACHER No. It is read one-zero, and it means two. This is the first major trap. Whenever you see a
             number made of 0s and 1s, check which system it is in.
  43 TEACHER Look at the table. What do you notice about the last digit of even numbers?
  44 STUDENT It is always 0.
  45 TEACHER Exactly. In binary, a number ends in 0 if it is even and 1 if it is odd. Another pattern. What
             happens to 101 when I add a zero at the end?
  46 STUDENT It becomes 1010.
  47 TEACHER What is 101?
  48 STUDENT Five.
  49 TEACHER And 1010?
  50 STUDENT Ten. It doubled!
  51 TEACHER Exactly. Adding a 0 on the right of a binary number doubles it, just as adding a 0 on the right
             of a decimal number multiplies it by ten. That is a quick way to check your work later.
  52 TEACHER Now an important question. How many different patterns can n bits make?
  53 STAGE   The teacher writes the case of one bit, two bits, and three.
  54 BOARD   1 bit  : 0, 1                       = 2 patterns
  55 BOARD   2 bits : 00, 01, 10, 11             = 4 patterns
  56 BOARD   3 bits : 000, 001, 010, 011,
  57 BOARD            100, 101, 110, 111         = 8 patterns
  58 TEACHER Every time we add a bit, the number of patterns doubles. So n bits give 2^n patterns. Four bits
             give 16. Eight bits, a byte, give 256.
  59 TEACHER Why is that useful?
  60 STUDENT Because it tells us how many different things we can represent with a given number of bits.
  61 TEACHER Exactly. With eight bits we can represent 256 different values, from 0 to 255. Notice that the
             largest value is one less than the number of patterns, because we start counting from 0. This
             will matter very much when we study codes.
  62 TEACHER Let us check understanding. What is the weight of the fifth bit from the right?
  63 STUDENT 2^4, which is 16.
  64 TEACHER How many patterns can six bits make?
  65 STUDENT 64.
  66 TEACHER What is the largest value that four bits can hold?
  67 STUDENT 15, which is 1111.
  68 TEACHER Good. Let us summarise.
  69 STAGE   A student reads from her notes.
  70 STUDENT The same rule works everywhere: the value is the sum of digit times base to the power of
             position. In binary the weights are powers of 2. With n bits there are 2 to the power n
             patterns, and the largest value is that number minus one.
  71 STAGE   The board holds the final picture.
  72 BOARD   weights   128   64   32   16   8   4   2   1
  73 BOARD   n bits  ->  2^n patterns   ->  largest value = 2^n - 1
  74 TEACHER Binary is perfect for machines but difficult for people. A long string of zeros and ones is hard
             to read and easy to copy wrongly. What can we do?
  75 STAGE   The board changes to:
  76 BOARD   NEXT: OCTAL AND HEXADECIMAL

Notes:
  - Opening block ``open_01`` is not in the script: it is the usual breadcrumb opening
    (where we are, what came before, what this video covers).
  - Long teacher lines are split into two narrations where a statement is followed by a question.
  - Facts checked in the data block: 5326 expanded; 1011 (base 2) = 11; binary of 0 to 8;
    101 = 5 and 1010 = 10; n bits give 2^n patterns (1, 2, 3, 4, 6, 8 bits); weight of the fifth
    bit = 16; largest 4-bit value = 15 = 1111; 8 bits hold 0 to 255.

Style: 2D, three colours (blue main, grey support, gold highlight). Raised boxes only for the key
object, the bits of 1011. Pinned KEY IDEAS panel from the first scene to the end.

Section map:
  S00 Opening   S01 Decimal place values   S02 The same rule in binary   S03 Counting in binary
  S04 What n bits can hold   S05 Check   S06 Summary   S07 Next
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
CRUMB_LESSON = "Lesson 3: Number Systems"
CRUMB_VIDEO = "Video 2 of 4"
VIDEO_TITLE = "Decimal and Binary"
BEFORE_LABEL = "Last video"
BEFORE_IDEA = "Value = sum of (digit × weight)"
TODAY_IDEA = "Place values, counting in binary, and what n bits can hold"

TEACHER_VOICE = "vijay"
STUDENT_VOICE = "kavya"        # students speak in their own voice, in their own blocks
TEACHER_PAUSE = 0.7            # silence after each teacher block (seconds), so speakers never run together
STUDENT_PAUSE = 0.6            # silence after each student block

IDEAS = [("Same rule in every base", GOLD), ("Binary weights: 1, 2, 4, 8 …", MAIN), ("MSB left, LSB right", MAIN),
         ("Ends in 0: even. Add a 0: double", MAIN), ("n bits: 2ⁿ patterns, largest 2ⁿ − 1", MAIN)]
P_RULE, P_WEIGHTS, P_MSB, P_EVEN, P_NBITS = range(5)

COUNT = [(k, format(k, "b")) for k in range(9)]

assert 5 * 10 ** 3 + 3 * 10 ** 2 + 2 * 10 ** 1 + 6 * 10 ** 0 == 5326 == 5000 + 300 + 20 + 6
assert int("1011", 2) == 1 * 8 + 0 * 4 + 1 * 2 + 1 * 1 == 11
assert [b for _, b in COUNT] == ["0", "1", "10", "11", "100", "101", "110", "111", "1000"]
assert all(b.endswith("0") == (k % 2 == 0) for k, b in COUNT)
assert int("101", 2) == 5 and int("1010", 2) == 10 == 2 * 5
assert [2 ** n for n in (1, 2, 3, 4, 6, 8)] == [2, 4, 8, 16, 64, 256]
assert 2 ** 4 == 16 and 2 ** 4 - 1 == 15 == int("1111", 2) and 2 ** 8 - 1 == 255


class DecimalAndBinaryVideo(LMSScene):
    lesson_title = "Decimal and Binary"

    def construct(self):
        self.setup_board()
        self.opening("open_01", "Last time we saw that the value of a number is the sum of each digit times its "
                                "weight. In this video we use that rule on decimal and binary, we count in binary, "
                                "and we see what n bits can hold.", "video")
        self.open_panel("Key ideas", IDEAS)
        self.decimal()
        self.binary()
        self.counting()
        self.n_bits()
        self.check()
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

    # ============================================== 1. DECIMAL ==========

    def decimal(self):
        self.begin("S01_decimal", "Decimal Place Values", "A system you already know")

        cells = self.put(bit_cells("5326", 0.8), "left", BOARD_TOP - 0.55)
        weights = above(cells, ["1000", "100", "10", "1"])
        line1 = self.put(mono("5326 = 5×10³ + 3×10² + 2×10¹ + 6×10⁰", LABEL, INK), "left", under=cells, buff=0.45)
        line2 = self.put(mono("= 5000 + 300 + 20 + 6", LABEL, MAIN), "left", under=line1, buff=0.25)

        self.play(FadeIn(cells, shift=UP * 0.1), run_time=0.5)
        self.ask("dec_01", "We begin with a system you already know. What are the weights of each digit in this "
                           "number?", "What are the weights of each digit in 5326?")
        self.reply("dec_02", "One, ten, one hundred and one thousand.", "1, 10, 100 and 1000.",
                   (None, LaggedStart(*[FadeIn(w, shift=DOWN * 0.1) for w in reversed(weights)], lag_ratio=0.4)))
        self.hush()
        self.play(FadeIn(line1, shift=UP * 0.1), run_time=0.8)
        self.play(FadeIn(line2, shift=UP * 0.1), run_time=0.8)
        self.tell("dec_03", "Now let us use exactly the same rule for a binary number.",
                  ("same", Indicate(line1, color=GOLD, scale_factor=1.04)), (None, lambda: self.add_row(P_RULE)))

        self.finish("S01_decimal")

    # ===================================== 2. THE SAME RULE IN BINARY ===

    def binary(self):
        self.begin("S02_binary", "The Same Rule in Binary", "The same rule in binary")

        cells = self.put(bit_cells("1011", 0.8, raised=True), "left", BOARD_TOP - 0.55)
        sub = text("base 2", SMALL, MUTED, BOLD).next_to(cells, RIGHT, buff=0.75).align_to(cells, DOWN)
        weights = above(cells, ["8", "4", "2", "1"])
        places = below(cells, ["3", "2", "1", "0"])
        msb = text("MSB", SMALL, GOLD, BOLD).next_to(cells[0], LEFT, buff=0.3)
        lsb = text("LSB", SMALL, MAIN, BOLD).next_to(cells[-1], RIGHT, buff=0.3)
        line1 = self.put(mono("1011 = 1×8 + 0×4 + 1×2 + 1×1", LABEL, INK), "left", under=places, buff=0.35)
        line2 = self.put(mono("= 8 + 0 + 2 + 1 = 11 in decimal", LABEL, MAIN), "left", under=line1, buff=0.25)
        same = self.put(self.note("Same quantity, written two ways", GOLD), "left", under=line2, buff=0.35)

        self.tell("bin_01", "Look at one zero one one in the binary system. We write the base as a small subscript, "
                            "one zero one one base two, to show which system we are using.",
                  ("Look", FadeIn(cells, shift=UP * 0.1)), ("subscript", FadeIn(sub, shift=LEFT * 0.1)))
        self.ask("bin_02", "What are the weights here?", "What are the weights in 1011 (base 2)?")
        self.reply("bin_03", "Powers of two.", "Powers of 2.")
        self.tell("bin_04", "Yes. One, two, four, eight.",
                  ("One", FadeIn(weights[3], shift=DOWN * 0.1)), ("two", FadeIn(weights[2], shift=DOWN * 0.1)),
                  ("four", FadeIn(weights[1], shift=DOWN * 0.1)), ("eight", FadeIn(weights[0], shift=DOWN * 0.1)),
                  (None, lambda: self.add_row(P_WEIGHTS)))
        self.play(FadeOut(sub), FadeIn(places, shift=UP * 0.1), run_time=0.6)
        self.play(FadeIn(line1, shift=UP * 0.1), run_time=0.8)
        self.play(FadeIn(line2, shift=UP * 0.1), run_time=0.8)
        self.tell("bin_05", "So one zero one one in binary is the same quantity that we call eleven. The quantity "
                            "did not change. Only the way of writing it changed.",
                  ("eleven", Indicate(line2, color=GOLD, scale_factor=1.05)),
                  ("writing", FadeIn(same, shift=UP * 0.1)))
        self.ask("bin_06", "Which is the largest weight in this number?")
        self.reply("bin_07", "Eight.", "8.", (None, Indicate(weights[0], color=GOLD, scale_factor=1.5)))
        self.tell("bin_08", "The leftmost bit, which carries the largest weight, is called the most significant bit, "
                            "or M S B. The rightmost bit, with the smallest weight, is the least significant bit, "
                            "or L S B.",
                  ("leftmost", lambda: [mark(cells[0]), FadeIn(msb, shift=RIGHT * 0.1)]),
                  ("rightmost", lambda: [mark(cells[-1], MAIN), FadeIn(lsb, shift=LEFT * 0.1)]),
                  ("least", lambda: self.add_row(P_MSB)))

        self.finish("S02_binary")

    # ===================================== 3. COUNTING IN BINARY ========

    def counting(self):
        self.begin("S03_counting", "Counting in Binary", "Counting in binary")

        tb = table([["Decimal", "Binary"]] + [[str(k), b] for k, b in COUNT], [1.7, 1.9], row_h=0.4)
        self.put(tb, "left", BOARD_TOP)
        carry = self.put(self.note("Out of digits: write 0, carry 1", MAIN, "right", SMALL), "right", BOARD_TOP)
        nine = self.put(mono("9 → 10", LABEL, MUTED), "right", under=carry, buff=0.3)
        one = self.put(mono("1 → 10", LABEL, GOLD), "right", under=nine, buff=0.25)
        trap = self.put(self.note("10 in binary is one-zero: it means two", GOLD, "right", SMALL), "right",
                        BOARD_TOP)
        base = self.put(self.note("Trap: check the base", MAIN, "right", SMALL), "right", under=trap, buff=0.3)
        even = self.put(self.note("Ends in 0: even. Ends in 1: odd", MAIN, "right", SMALL), "right", BOARD_TOP)
        five = self.put(mono("101  = 5", LABEL, INK), "right", BOARD_TOP)
        tenb = self.put(mono("1010 = 10", LABEL, INK), "right", under=five, buff=0.2)
        dbl = self.put(self.note("Add a 0 on the right: doubles", GOLD, "right", SMALL), "right", under=tenb,
                       buff=0.3)
        evens = [tb.cell[(r, 1)] for r in (1, 3, 5, 7, 9)]

        self.play(FadeIn(tb.rows[0]), run_time=0.5)
        self.ask("cnt_01", "Now let me ask you to count in binary. We begin at zero.",
                 "Count in binary. We begin at 0.")
        self.reply("cnt_02", "Zero, one.", "0, 1.",
                   (None, LaggedStart(FadeIn(tb.rows[1]), FadeIn(tb.rows[2]), lag_ratio=0.6)))
        self.ask("cnt_03", "And now? What comes after one?", "What comes after 1?")
        self.reply("cnt_04", "There is no two.", "There is no 2.")
        self.tell("cnt_05", "Right. We have run out of digits, just as we run out at nine in decimal.",
                  ("digits", FadeIn(carry, shift=UP * 0.1)))
        self.ask("cnt_06", "What do we do in decimal after nine?", "What do we do in decimal after 9?")
        self.reply("cnt_07", "Write zero and carry one.", "Write 0 and carry 1.", (None, FadeIn(nine, shift=UP * 0.1)))
        self.ask("cnt_08", "Do the same in binary after one.", "Do the same in binary after 1.")
        self.reply("cnt_09", "One zero.", "10.",
                   (None, lambda: [FadeIn(one, shift=UP * 0.1), FadeIn(tb.rows[3], shift=RIGHT * 0.15)]))
        self.hush()
        self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.15) for r in tb.rows[4:]], lag_ratio=0.35), run_time=2.4)
        self.reply("cnt_10", "Is one zero in binary the number ten?", "Is 10 in binary the number ten?",
                   (None, Indicate(tb.rows[3], color=GOLD, scale_factor=1.15)), who="A student frowns")
        self.tell("cnt_11", "No. It is read one zero, and it means two. This is the first major trap. Whenever you "
                            "see a number made of zeros and ones, check which system it is in.",
                  ("read", lambda: [FadeOut(VGroup(carry, nine, one)), FadeIn(trap, shift=UP * 0.1)]),
                  ("check", FadeIn(base, shift=UP * 0.1)))

        # two patterns in the same table
        self.ask("pat_01", "Look at the table. What do you notice about the last digit of even numbers?",
                 "What do you notice about the last digit of even numbers?",
                 ("even", lambda: [FadeOut(VGroup(trap, base))] + [e.animate.set_color(GOLD) for e in evens]))
        self.reply("pat_02", "It is always zero.", "It is always 0.")
        self.tell("pat_03", "Exactly. In binary, a number ends in zero if it is even and one if it is odd.",
                  ("ends", FadeIn(even, shift=UP * 0.1)))
        self.ask("pat_04", "Another pattern. What happens to one zero one when I add a zero at the end?",
                 "What happens to 101 when I add a 0 at the end?",
                 ("pattern", lambda: [FadeOut(even)] + [e.animate.set_color(INK) for e in evens]))
        self.reply("pat_05", "It becomes one zero one zero.", "It becomes 1010.")
        self.ask("pat_06", "What is one zero one?", "What is 101?")
        self.reply("pat_07", "Five.", "5.",
                   (None, lambda: [FadeIn(five, shift=UP * 0.1),
                                   Indicate(tb.rows[6], color=GOLD, scale_factor=1.1)]))
        self.ask("pat_08", "And one zero one zero?", "And 1010?")
        self.reply("pat_09", "Ten. It doubled!", "10. It doubled!", (None, FadeIn(tenb, shift=UP * 0.1)))
        self.tell("pat_10", "Exactly. Adding a zero on the right of a binary number doubles it, just as adding a "
                            "zero on the right of a decimal number multiplies it by ten. That is a quick way to "
                            "check your work later.",
                  ("doubles", FadeIn(dbl, shift=UP * 0.1)), ("check", lambda: self.add_row(P_EVEN)))

        self.finish("S03_counting")

    # ===================================== 4. WHAT n BITS CAN HOLD ======

    def n_bits(self):
        self.begin("S04_n_bits", "What n Bits Can Hold", "How many patterns?")

        tb = table([["1 bit", "0  1", "2 patterns"], ["2 bits", "00  01  10  11", "4 patterns"],
                    ["3 bits", "000 001 010 011 100 101 110 111", "8 patterns"]],
                   [1.4, 5.5, 2.5], row_h=0.55, head=False)
        self.put(tb, "full", BOARD_TOP)
        power = self.put(self.note("n bits give 2ⁿ patterns", GOLD), "left", under=tb, buff=0.35, align="l")
        byte = self.put(self.note("8 bits (1 byte): 256 values, 0 to 255", MAIN), "left", under=power, buff=0.2,
                        align="l")
        largest = self.put(self.note("Largest value = 2ⁿ − 1", GOLD), "left", under=tb, buff=0.35, align="l")

        self.ask("bits_01", "Now an important question. How many different patterns can n bits make?",
                 "How many different patterns can n bits make?")
        self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.15) for r in tb.rows], lag_ratio=0.5), run_time=2.4)
        self.tell("bits_02", "Every time we add a bit, the number of patterns doubles. So n bits give two to the "
                             "power n patterns. Four bits give sixteen. Eight bits, a byte, give two hundred and "
                             "fifty-six.",
                  ("doubles", Indicate(tb.col(2), color=GOLD, scale_factor=1.08)),
                  ("power", FadeIn(power, shift=UP * 0.1)))
        self.ask("bits_03", "Why is that useful?")
        self.reply("bits_04", "Because it tells us how many different things we can represent with a given number "
                              "of bits.", "It tells us how many things we can represent.")
        self.tell("bits_05", "Exactly. With eight bits we can represent two hundred and fifty-six different values, "
                             "from zero to two hundred and fifty-five. Notice that the largest value is one less "
                             "than the number of patterns, because we start counting from zero. This will matter "
                             "very much when we study codes.",
                  ("eight", FadeIn(byte, shift=UP * 0.1)),
                  ("largest", lambda: [FadeOut(power), FadeIn(largest, shift=UP * 0.1)]),
                  ("codes", lambda: self.add_row(P_NBITS)))

        self.finish("S04_n_bits")

    # ============================================== 5. CHECK ============

    def check(self):
        self.begin("S05_check", "Check", "Check your understanding")

        tb = table([["128", "64", "32", "16", "8", "4", "2", "1"]], [0.72] * 8, head=False)
        self.put(tb, "left", BOARD_TOP)
        tag = self.put(text("Binary weights", SMALL, MUTED, BOLD), "left", under=tb, buff=0.15)
        six = self.put(mono("6 bits: 2⁶ = 64 patterns", LABEL, INK), "left", under=tag, buff=0.45)
        four = self.put(mono("4 bits: 2⁴ − 1 = 15 = 1111", LABEL, INK), "left", under=six, buff=0.3)

        self.play(FadeIn(tb, shift=UP * 0.1), FadeIn(tag), run_time=0.6)
        self.ask("chk_01", "Let us check understanding. What is the weight of the fifth bit from the right?",
                 "What is the weight of the fifth bit from the right?")
        self.reply("chk_02", "Two to the power four, which is sixteen.", "2⁴, which is 16.",
                   (None, lambda: [tb.cell[(0, 3)].animate.set_color(GOLD),
                                   Indicate(tb.cell[(0, 3)], color=GOLD, scale_factor=1.4)]))
        self.ask("chk_03", "How many patterns can six bits make?")
        self.reply("chk_04", "Sixty-four.", "64.", (None, FadeIn(six, shift=UP * 0.1)))
        self.ask("chk_05", "What is the largest value that four bits can hold?")
        self.reply("chk_06", "Fifteen, which is one one one one.", "15, which is 1111.",
                   (None, FadeIn(four, shift=UP * 0.1)))

        self.finish("S05_check")

    # ============================================== 6. SUMMARY ==========

    def summary(self):
        self.begin("S06_summary", "Summary", "Summary", GOLD)

        rows = self.put(self.ticks(["Value = sum of (digit × weight), in every base",
                                    "In binary the weights are powers of 2",
                                    "n bits give 2ⁿ patterns",
                                    "Largest value = 2ⁿ − 1"]), "full", BOARD_HIGH, "l")
        final = stack(mono("128  64  32  16  8  4  2  1", SMALL, MAIN),
                      text("n bits  →  2ⁿ patterns", SMALL, GOLD, BOLD),
                      text("Largest value = 2ⁿ − 1", SMALL, GOLD, BOLD), buff=0.18)
        final_card = self.put(self.card(final, color=GOLD, pad=0.25), "left", under=rows, buff=0.45, align="l")

        self.tell("sum_01", "Good. Let us summarise.")
        self.reply("sum_02", "The same rule works everywhere: the value is the sum of digit times base to the power "
                             "of position. In binary the weights are powers of two. With n bits there are two to "
                             "the power n patterns, and the largest value is that number minus one.",
                   "Reading from her notes",
                   ("rule", lambda: [FadeIn(rows[0], shift=RIGHT * 0.2), self.light(P_RULE)]),
                   ("weights", lambda: [FadeIn(rows[1], shift=RIGHT * 0.2), self.light(P_WEIGHTS, P_MSB)]),
                   ("bits", lambda: [FadeIn(rows[2], shift=RIGHT * 0.2), self.light(P_NBITS)]),
                   ("largest", FadeIn(rows[3], shift=RIGHT * 0.2)),
                   ("minus", lambda: [FadeIn(final_card, shift=UP * 0.1), self.all_lit()]), who="A student")
        self.finish("S06_summary")

    # ============================================== 7. NEXT =============

    def next_video(self):
        self.scene_start("S07_next", title="Next: Octal and Hexadecimal")
        bits = self.put(mono("110101101011010011100101", BODY, MAIN), "full", BOARD_TOP - 0.3)
        nxt = self.put(self.next_up("Next: Octal and hexadecimal"), "full", under=bits, buff=0.6)
        self.tell("next_01", "Binary is perfect for machines but difficult for people. A long string of zeros and "
                             "ones is hard to read and easy to copy wrongly.",
                  ("string", FadeIn(bits, shift=UP * 0.1)))
        self.ask("next_02", "What can we do?", "A long binary string is hard to read. What can we do?",
                 (None, FadeIn(nxt, scale=1.1)))
        self.undock()
        self.finish("S07_next")

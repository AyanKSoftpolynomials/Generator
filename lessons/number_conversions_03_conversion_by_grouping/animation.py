"""
animation.py for the LMS video generator.

Course : C-CAT Computer Fundamentals
Lesson : Lesson 4 - Number System Conversions and Objective Practice
Video  : 05 Video 3 - Conversion by Grouping

Source script:
  CCAT_Computer_Fundamentals_Scripts_Lessons_1-5/PDF/Lesson 4 - Number System Conversions and Objective Practice/05 Video 3 - Conversion by Grouping.pdf
  The script has no speaker labels. Every line was labelled as below:
    TEACHER  spoken by the teacher: ``self.tell`` / ``self.ask`` (TEACHER_VOICE). Drives the board.
    STUDENT  spoken by a student: ``self.reply`` (STUDENT_VOICE). Every student answer is its own
             narration and appears as a card at the bottom right.
    STAGE    stage direction: not narrated, it becomes the visuals (or the name on the student card).
    BOARD    what the board shows: on screen, not spoken.
  Spoken text uses words ("one zero one one"); the cards and the board show digits ("1011").

Speaker split:
  01 TITLE   Binary, Octal and Hexadecimal by Grouping: No Arithmetic Required
  02 STAGE   The board shows the relationship from Lesson 3.
  03 BOARD   1 octal digit = 3 bits        1 hex digit = 4 bits
  04 TEACHER In Lesson 3 we saw that these systems are shorthand for binary. Today we use that fact to
             convert without any arithmetic. Let us start with a binary number, 101101110. How would we write
             it in octal?
  05 STUDENT Group it in threes?
  06 TEACHER From which end?
  07 STUDENT From the right.
  08 STAGE   The teacher writes.
  09 BOARD   101   101   110
  10 BOARD    5     5     6      ->   (556) in octal
  11 TEACHER Each group of three bits is read as one digit. 101 is 5 and 110 is 6. Now the same number in
             hexadecimal. The groups are of four bits. The number has nine bits. What happens at the left
             end?
  12 STUDENT Only one bit is left over.
  13 TEACHER We pad it with zeros on the left. This does not change the value, because leading zeros are
             worthless.
  14 STAGE   The board shows:
  15 BOARD   0001   0110   1110
  16 BOARD     1      6      E      ->   (16E) in hexadecimal
  17 TEACHER Let me check the consistency. 556 in octal is 5 times 64 plus 5 times 8 plus 6, which is 366.
             And 16E in hexadecimal is 256 plus 96 plus 14, which is 366. The same number, reached by two
             different groupings.
  18 TEACHER Now the reverse direction. Convert (9C) in hexadecimal to binary. Each hexadecimal digit expands
             into four bits.
  19 STAGE   The board shows:
  20 BOARD    9      C
  21 BOARD   1001   1100   ->   (10011100) in binary
  22 TEACHER And now convert this to octal. Which method do we use?
  23 STUDENT Group the binary into threes, from the right.
  24 STAGE   The teacher writes.
  25 BOARD   10011100  ->  010   011   100   ->   (234) in octal
  26 TEACHER We padded the left with a zero. And 234 in octal is the same as 156 in decimal, which is the
             number we converted by division last time. Remember 156?
  27 STUDENT It was 9C in hexadecimal too.
  28 TEACHER That is right. Look how neatly the results match. 156 in decimal is 234 in octal, 9C in
             hexadecimal and 10011100 in binary.
  29 TEACHER This leads to a very important technique. What if I ask you to convert (475) in octal to
             hexadecimal?
  30 STUDENT Convert it to decimal first?
  31 TEACHER You could, but there is a faster route. Binary is the common language, so go through it.
  32 STAGE   The board shows:
  33 BOARD   475 octal  ->  100 111 101   (3 bits each)
  34 BOARD              ->  0001 0011 1101   (regroup in 4s, pad left)
  35 BOARD              ->  1    3    D     =  (13D) in hexadecimal
  36 TEACHER Octal to hexadecimal, or hexadecimal to octal, always goes through binary.
  37 TEACHER Now what about fractions? The rule for the integer part is to group from the right. For the
             fractional part, which side do you think we start from?
  38 STUDENT The left, next to the point.
  39 TEACHER Exactly. Start next to the point and move right. Pad zeros on the right, at the end.
  40 STAGE   The board shows:
  41 BOARD   110.01 in binary
  42 BOARD   integer part:  110        ->  6
  43 BOARD   fraction part: 01 -> 010  ->  2     (padded on the right)
  44 BOARD   answer: (6.2) in octal
  45 TEACHER Check. 6.2 in octal is 6 plus 2 eighths, which is 6.25. And 110.01 in binary is 4 plus 2 plus a
             quarter, which is 6.25.
  46 STAGE   A student raises a hand.
  47 STUDENT What goes wrong most often?
  48 TEACHER There are three typical mistakes.
  49 BOARD   1. grouping from the left for the integer part
  50 BOARD   2. padding zeros on the wrong side
  51 BOARD   3. writing a digit of three bits for hexadecimal, or four for octal
  52 TEACHER Padding is the one to watch. For the integer part, pad on the left. For the fraction part, pad
             on the right. If you pad a fraction on the left, you change its value.
  53 TEACHER Let us try a few. 1011.101 in binary to hexadecimal.
  54 STUDENT The integer part is 1011, which is B. The fraction 101 is padded to 1010, which is A. So B.A.
  55 TEACHER And in octal?
  56 STUDENT 001 011 for the integer part, which is 13. The fraction 101 is 5. So 13.5.
  57 TEACHER Both answers equal 11.625, which we saw earlier.
  58 TEACHER Summary.
  59 STAGE   A student reads from her notes.
  60 STUDENT Binary to octal in groups of three and to hexadecimal in groups of four. Octal and hexadecimal
             back to binary by expanding each digit. Octal to hexadecimal, and the other way, through binary.
             For fractions, group from the point outwards and pad on the outer side.
  61 STAGE   The board holds the final picture.
  62 BOARD   bits <-> octal (3)     bits <-> hex (4)     octal <-> hex via bits
  63 TEACHER Now we have three families of methods. But in an examination, you do not have time to try them
             all. How do we choose, and how do we check?
  64 STAGE   The board changes to:
  65 BOARD   NEXT: FAST METHODS AND SELF-CHECKS

Notes:
  - Opening block ``open_01`` is not in the script: it is the usual breadcrumb opening
    (where we are, what came before, what this video covers).
  - Long teacher lines are split into two narrations where a statement is followed by a question.
  - Every worked answer is computed and asserted in the data block: 101101110 (base 2) = 556 (base 8)
    = 16E (base 16) = 366; 9C (base 16) = 10011100 (base 2) = 234 (base 8) = 156; 475 (base 8) = 13D
    (base 16); 110.01 (base 2) = 6.2 (base 8) = 6.25; 1011.101 (base 2) = B.A (base 16) = 13.5 (base 8)
    = 11.625. The script's answers are all correct.

Style: 2D, three colours (blue main, grey support, gold highlight). No drawings and no raised
boxes are needed in this video. Pinned KEY IDEAS panel from the first scene to the end.

Section map:
  S00 Opening   S01 Binary to octal and hexadecimal   S02 Hexadecimal to binary to octal
  S03 Octal to hexadecimal through binary   S04 Fractions   S05 Typical mistakes
  S06 Let us try a few   S07 Summary   S08 Next
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
CRUMB_VIDEO = "Video 3 of 5"
VIDEO_TITLE = "Conversion by Grouping"
BEFORE_LABEL = "Last video"
BEFORE_IDEA = "From decimal: divide by the base, read the remainders up"
TODAY_IDEA = "Binary, octal and hexadecimal by grouping bits: no arithmetic"

TEACHER_VOICE = "vijay"
STUDENT_VOICE = "kavya"        # students speak in their own voice, in their own blocks
TEACHER_PAUSE = 0.7            # silence after each teacher block (seconds), so speakers never run together
STUDENT_PAUSE = 0.6            # silence after each student block

IDEAS = [("Binary to octal: groups of 3", GOLD), ("Binary to hex: groups of 4", GOLD),
         ("Octal and hex: through binary", MAIN), ("Integer: from the right, pad left", MAIN),
         ("Fraction: from the point, pad right", MAIN)]
P_THREE, P_FOUR, P_VIA, P_INT, P_FRAC = range(5)

BITS = "101101110"

assert int(BITS, 2) == 366 == int("556", 8) == int("16E", 16)
assert [int(g, 2) for g in ("101", "101", "110")] == [5, 5, 6]
assert [format(int(g, 2), "X") for g in ("0001", "0110", "1110")] == ["1", "6", "E"]
assert 5 * 64 + 5 * 8 + 6 == 320 + 40 + 6 == 366 and 256 + 96 + 14 == 366 and 6 * 16 == 96
assert format(0x9, "04b") + format(0xC, "04b") == "10011100" and int("10011100", 2) == 156 == int("234", 8)
assert [int(g, 2) for g in ("010", "011", "100")] == [2, 3, 4]
assert "".join(format(int(d), "03b") for d in "475") == "100111101"
assert [format(int(g, 2), "X") for g in ("0001", "0011", "1101")] == ["1", "3", "D"] and int("475", 8) == 0x13D
assert int("110", 2) == 6 and int("010", 2) == 2 and 6 + 2 / 8 == 6.25 == 4 + 2 + 1 / 4
assert format(int("1011", 2), "X") == "B" and format(int("1010", 2), "X") == "A"
assert [int(g, 2) for g in ("001", "011")] == [1, 3] and int("101", 2) == 5
assert 11 + 10 / 16 == 11.625 == 8 + 3 + 5 / 8 == int("1011101", 2) / 8


class ConversionByGroupingVideo(LMSScene):
    lesson_title = "Conversion by Grouping"

    def construct(self):
        self.setup_board()
        self.opening("open_01", "Last time we converted from decimal by repeated division. In this video we "
                                "convert between binary, octal and hexadecimal by grouping bits, with no arithmetic "
                                "at all.", "video")
        self.open_panel("Key ideas", IDEAS)
        self.binary_to_both()
        self.hex_to_binary_to_octal()
        self.octal_to_hex()
        self.fractions()
        self.mistakes()
        self.try_a_few()
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

    # ========================= 1. BINARY TO OCTAL AND HEXADECIMAL =======

    def binary_to_both(self):
        self.begin("S01_binary", "Binary to Octal and Hexadecimal", "Binary to octal and hexadecimal")

        rel = stack(self.note("1 octal digit = 3 bits", MAIN), self.note("1 hex digit = 4 bits", MAIN), buff=0.25)
        self.put(rel, "left", BOARD_TOP)
        gap = 0.35
        cells = self.put(bit_cells(BITS, 0.55, font_size=LABEL), "left", BOARD_TOP, "r")
        vals = group_values(cells, 3, gap, ["5", "5", "6"])
        octal = self.put(mono("101101110 = 556 in octal", SMALL, GOLD), "left", under=cells, buff=0.95)

        self.tell("g_01", "In Lesson three we saw that these systems are shorthand for binary. Today we use that "
                          "fact to convert without any arithmetic.",
                  ("shorthand", LaggedStart(*[FadeIn(r, shift=UP * 0.1) for r in rel], lag_ratio=0.5)))
        self.play(FadeOut(rel), run_time=0.4)
        self.ask("g_02", "Let us start with a binary number, one zero one one zero one one one zero. How would we "
                         "write it in octal?", "How would we write 101101110 in octal?",
                 ("binary", FadeIn(cells, shift=UP * 0.1)))
        self.reply("g_03", "Group it in threes?")
        self.ask("g_04", "From which end?")
        self.reply("g_05", "From the right.", None, (None, lambda: split(cells, 3, gap)))
        self.hush()
        self.play(LaggedStart(*[FadeIn(v, shift=UP * 0.1) for v in vals], lag_ratio=0.5), run_time=1.5)
        self.play(FadeIn(octal, shift=UP * 0.1), run_time=0.7)
        self.tell("g_06", "Each group of three bits is read as one digit. One zero one is five and one one zero is "
                          "six.",
                  ("five", lambda: [Indicate(vals[0], color=GOLD, scale_factor=1.4),
                                    Indicate(vals[1], color=GOLD, scale_factor=1.4)]),
                  ("six", Indicate(vals[2], color=GOLD, scale_factor=1.4)), (None, lambda: self.add_row(P_THREE)))

        # the same number in groups of four
        self.drop_q()
        self.play(FadeOut(VGroup(cells, vals, octal)), run_time=0.5)
        gap4 = 0.4
        wide = self.put(bit_cells("000" + BITS, 0.55, font_size=LABEL), "full", BOARD_TOP, "r")
        wide.shift(LEFT * 1.6)
        pads = VGroup(*wide[:3])
        for p in pads:
            p[1].set_color(MUTED)
        hexv = group_values(wide, 4, gap4, ["1", "6", "E"])
        hexa = self.put(mono("101101110 = 16E in hexadecimal", SMALL, GOLD), "left", under=wide, buff=0.95)
        checks = stack(mono("556 in octal = 320 + 40 + 6 = 366", SMALL, INK),
                       mono("16E in hex   = 256 + 96 + 14 = 366", SMALL, INK), buff=0.2)
        self.put(checks, "left", under=hexa, buff=0.4)
        same = self.put(self.note("Same number, two groupings", GOLD), "left", under=checks, buff=0.3)

        self.play(FadeIn(VGroup(*wide[3:]), shift=UP * 0.1), run_time=0.5)
        self.tell("g_07", "Now the same number in hexadecimal. The groups are of four bits. The number has nine "
                          "bits.", ("four", lambda: split(wide, 4, gap4, hidden=list(pads))))
        self.ask("g_08", "What happens at the left end?")
        self.reply("g_09", "Only one bit is left over.", None,
                   (None, Indicate(wide[3], color=GOLD, scale_factor=1.3)))
        self.tell("g_10", "We pad it with zeros on the left. This does not change the value, because leading zeros "
                          "are worthless.",
                  ("pad", LaggedStart(*[FadeIn(p, shift=DOWN * 0.15) for p in pads], lag_ratio=0.3)),
                  ("value", LaggedStart(*[FadeIn(v, shift=UP * 0.1) for v in hexv], lag_ratio=0.4)),
                  (None, FadeIn(hexa, shift=UP * 0.1)), (None, lambda: self.add_row(P_FOUR)))
        self.drop_q()
        self.tell("g_11", "Let me check the consistency. Five five six in octal is five times sixty-four plus five "
                          "times eight plus six, which is three hundred and sixty-six. And one six E in hexadecimal "
                          "is two hundred and fifty-six plus ninety-six plus fourteen, which is three hundred and "
                          "sixty-six. The same number, reached by two different groupings.",
                  ("octal", FadeIn(checks[0], shift=RIGHT * 0.15)),
                  ("hexadecimal", FadeIn(checks[1], shift=RIGHT * 0.15)), ("same", FadeIn(same, shift=UP * 0.1)))

        self.finish("S01_binary")

    # ========================= 2. HEXADECIMAL TO BINARY TO OCTAL ========

    def hex_to_binary_to_octal(self):
        self.begin("S02_reverse", "Hexadecimal to Binary to Octal", "The reverse: expand each digit")

        tb = table([["9", "C"], ["1001", "1100"]], [1.6, 1.6], row_h=0.6, head=False)
        self.put(tb, "left", BOARD_TOP)
        tb.rows[0].set_color(GOLD)
        binary = self.put(mono("9C in hex = 10011100 in binary", SMALL, GOLD), "left", under=tb, buff=0.3)
        groups = self.put(mono("010 011 100  →  234 in octal", SMALL, MAIN), "left", under=binary, buff=0.35)
        match = table([["Decimal", "156"], ["Octal", "234"], ["Hex", "9C"], ["Binary", "10011100"]], [1.5, 1.9],
                      row_h=0.48, size=SMALL, head=False)
        self.put(match, "right", BOARD_TOP)
        match.col(0).set_color(MUTED)

        self.tell("r_01", "Now the reverse direction. Convert nine C in hexadecimal to binary. Each hexadecimal "
                          "digit expands into four bits.",
                  ("Convert", FadeIn(tb.rows[0], shift=UP * 0.1)),
                  ("expands", LaggedStart(*[FadeIn(tb.cell[(1, c)], shift=DOWN * 0.15) for c in range(2)],
                                          lag_ratio=0.5)),
                  (None, FadeIn(binary, shift=UP * 0.1)))
        self.ask("r_02", "And now convert this to octal. Which method do we use?",
                 "Now convert 10011100 to octal. Which method do we use?")
        self.reply("r_03", "Group the binary into threes, from the right.", None,
                   (None, FadeIn(groups, shift=UP * 0.1)))
        self.tell("r_04", "We padded the left with a zero. And two three four in octal is the same as one hundred "
                          "and fifty-six in decimal, which is the number we converted by division last time.",
                  ("padded", Indicate(groups, color=GOLD, scale_factor=1.04)),
                  ("decimal", lambda: [FadeIn(match.rows[0], shift=LEFT * 0.1),
                                       FadeIn(match.rows[1], shift=LEFT * 0.1)]))
        self.ask("r_05", "Remember one hundred and fifty-six?", "Remember 156?")
        self.reply("r_06", "It was nine C in hexadecimal too.", "It was 9C in hexadecimal too.",
                   (None, FadeIn(match.rows[2], shift=LEFT * 0.1)))
        self.tell("r_07", "That is right. Look how neatly the results match. One hundred and fifty-six in decimal "
                          "is two three four in octal, nine C in hexadecimal and one zero zero one one one zero "
                          "zero in binary.",
                  ("binary", FadeIn(match.rows[3], shift=LEFT * 0.1)),
                  (None, Indicate(match, color=GOLD, scale_factor=1.04)))

        self.finish("S02_reverse")

    # ========================= 3. OCTAL TO HEXADECIMAL ==================

    def octal_to_hex(self):
        self.begin("S03_via_binary", "Octal to Hexadecimal through Binary", "Octal to hexadecimal: through binary")

        lines = stack(mono("475 in octal", LABEL, MAIN), mono("→ 100 111 101      3 bits each", SMALL, INK),
                      mono("→ 0001 0011 1101   regroup in 4s, pad left", SMALL, INK),
                      mono("→ 1 3 D  =  13D in hexadecimal", SMALL, GOLD), buff=0.28)
        self.put(lines, "full", BOARD_TOP, "l")
        via = self.put(self.note("Octal and hex always go through binary", GOLD), "left", under=lines, buff=0.4,
                       align="l")

        self.ask("v_01", "This leads to a very important technique. What if I ask you to convert four seven five "
                         "in octal to hexadecimal?", "How do we convert 475 in octal to hexadecimal?",
                 ("convert", FadeIn(lines[0], shift=UP * 0.1)))
        self.reply("v_02", "Convert it to decimal first?")
        self.tell("v_03", "You could, but there is a faster route. Binary is the common language, so go through it.",
                  ("faster", FadeIn(lines[1], shift=RIGHT * 0.15)), ("common", FadeIn(lines[2], shift=RIGHT * 0.15)),
                  (None, FadeIn(lines[3], shift=RIGHT * 0.15)))
        self.tell("v_04", "Octal to hexadecimal, or hexadecimal to octal, always goes through binary.",
                  ("always", FadeIn(via, shift=UP * 0.1)), (None, lambda: self.add_row(P_VIA)))

        self.finish("S03_via_binary")

    # ========================= 4. FRACTIONS =============================

    def fractions(self):
        self.begin("S04_fractions", "Fractions", "Fractions: group from the point")

        lines = stack(mono("110.01 in binary", LABEL, MAIN), mono("Integer : 110 → 6", SMALL, INK),
                      mono("Fraction: 01 → 010 → 2   padded on the right", SMALL, INK),
                      mono("Answer  : 6.2 in octal", SMALL, GOLD), buff=0.25)
        self.put(lines, "wide", BOARD_TOP, "l")
        checks = stack(mono("6.2 in octal     = 6 + 2/8     = 6.25", SMALL, MUTED),
                       mono("110.01 in binary = 4 + 2 + 1/4 = 6.25", SMALL, MUTED), buff=0.2)
        self.put(checks, "wide", under=lines, buff=0.45, align="l")

        self.ask("f_01", "Now what about fractions? The rule for the integer part is to group from the right. For "
                         "the fractional part, which side do you think we start from?",
                 "For the fractional part, which side do we start grouping from?",
                 ("fractions", FadeIn(lines[0], shift=UP * 0.1)), ("integer", FadeIn(lines[1], shift=RIGHT * 0.15)))
        self.reply("f_02", "The left, next to the point.")
        self.tell("f_03", "Exactly. Start next to the point and move right. Pad zeros on the right, at the end.",
                  ("Start", lambda: self.add_row(P_INT)), ("Pad", FadeIn(lines[2], shift=RIGHT * 0.15)),
                  (None, FadeIn(lines[3], shift=RIGHT * 0.15)), (None, lambda: self.add_row(P_FRAC)))
        self.tell("f_04", "Check. Six point two in octal is six plus two eighths, which is six point two five. And "
                          "one one zero point zero one in binary is four plus two plus a quarter, which is six "
                          "point two five.",
                  ("octal", FadeIn(checks[0], shift=RIGHT * 0.15)), ("binary", FadeIn(checks[1], shift=RIGHT * 0.15)))

        self.finish("S04_fractions")

    # ========================= 5. TYPICAL MISTAKES ======================

    def mistakes(self):
        self.begin("S05_mistakes", "Typical Mistakes", "What goes wrong most often?")

        rows = self.ticks(["Grouping from the left for the integer part", "Padding zeros on the wrong side",
                           "Three bits for a hex digit, or four for an octal digit"], "full", LABEL,
                          ["1.", "2.", "3."])
        self.put(rows, "full", BOARD_HIGH, "l")
        tb = table([["Integer part", "pad on the LEFT"], ["Fraction part", "pad on the RIGHT"]], [2.6, 3.0],
                   row_h=0.55, head=False, font=FONT)
        self.put(tb, "left", under=rows, buff=0.5, align="l")
        tb.col(0).set_color(MUTED)
        tb.col(1).set_color(GOLD)

        self.reply("m_01", "What goes wrong most often?", None, who="A student raises a hand")
        self.tell("m_02", "There are three typical mistakes.",
                  ("three", LaggedStart(*[FadeIn(r, shift=RIGHT * 0.2) for r in rows], lag_ratio=0.5, run_time=2.4)))
        self.tell("m_03", "Padding is the one to watch. For the integer part, pad on the left. For the fraction "
                          "part, pad on the right. If you pad a fraction on the left, you change its value.",
                  ("Padding", Indicate(rows[1], color=GOLD, scale_factor=1.04)),
                  ("integer", FadeIn(tb.rows[0], shift=RIGHT * 0.15)),
                  ("fraction", FadeIn(tb.rows[1], shift=RIGHT * 0.15)),
                  ("change", lambda: self.light(P_INT, P_FRAC)))

        self.finish("S05_mistakes")

    # ========================= 6. LET US TRY A FEW ======================

    def try_a_few(self):
        self.begin("S06_try", "Let Us Try a Few", "Let us try a few")

        hexa = stack(mono("1011 → B", LABEL, INK), mono("101 → 1010 → A", LABEL, INK),
                     mono("= B.A in hexadecimal", LABEL, GOLD), buff=0.25)
        self.put(hexa, "left", BOARD_TOP, "l")
        octal = stack(mono("001 011 → 13", SMALL, INK), mono("101 → 5", SMALL, INK),
                      mono("= 13.5 in octal", SMALL, GOLD), buff=0.25)
        self.put(octal, "right", BOARD_TOP, "l")
        both = self.put(self.note("Both answers equal 11.625", GOLD), "left", under=hexa, buff=0.5, align="l")

        self.ask("t_01", "Let us try a few. One zero one one point one zero one in binary to hexadecimal.",
                 "Convert 1011.101 in binary to hexadecimal.")
        self.reply("t_02", "The integer part is one zero one one, which is B. The fraction one zero one is padded "
                           "to one zero one zero, which is A. So B point A.",
                   "1011 is B. 101 padded to 1010 is A. So B.A",
                   ("B", FadeIn(hexa[0], shift=RIGHT * 0.15)), ("padded", FadeIn(hexa[1], shift=RIGHT * 0.15)),
                   ("So", FadeIn(hexa[2], shift=RIGHT * 0.15)))
        self.ask("t_03", "And in octal?", "And 1011.101 in octal?")
        self.reply("t_04", "Zero zero one, zero one one for the integer part, which is one three. The fraction one "
                           "zero one is five. So one three point five.", "001 011 is 13. 101 is 5. So 13.5",
                   ("integer", FadeIn(octal[0], shift=RIGHT * 0.15)), ("five", FadeIn(octal[1], shift=RIGHT * 0.15)),
                   ("So", FadeIn(octal[2], shift=RIGHT * 0.15)))
        self.tell("t_05", "Both answers equal eleven point six two five, which we saw earlier.",
                  ("equal", FadeIn(both, shift=UP * 0.1)))

        self.finish("S06_try")

    # ============================================== 7. SUMMARY ==========

    def summary(self):
        self.begin("S07_summary", "Summary", "Summary", GOLD)

        rows = self.put(self.ticks(["Binary to octal: groups of 3. To hexadecimal: groups of 4",
                                    "Back to binary: expand each digit",
                                    "Octal and hexadecimal: through binary",
                                    "Fractions: group from the point, pad the outer side"]), "full", BOARD_HIGH, "l")

        self.tell("sum_01", "Summary.")
        self.reply("sum_02", "Binary to octal in groups of three and to hexadecimal in groups of four. Octal and "
                             "hexadecimal back to binary by expanding each digit. Octal to hexadecimal, and the "
                             "other way, through binary. For fractions, group from the point outwards and pad on "
                             "the outer side.", "Reading from her notes",
                   ("Binary", lambda: [FadeIn(rows[0], shift=RIGHT * 0.2), self.light(P_THREE, P_FOUR)]),
                   ("expanding", FadeIn(rows[1], shift=RIGHT * 0.2)),
                   ("through", lambda: [FadeIn(rows[2], shift=RIGHT * 0.2), self.light(P_VIA)]),
                   ("fractions", lambda: [FadeIn(rows[3], shift=RIGHT * 0.2), self.light(P_INT, P_FRAC)]),
                   who="A student")
        self.hush()
        self.play(*self.all_lit())
        self.finish("S07_summary")

    # ============================================== 8. NEXT =============

    def next_video(self):
        self.scene_start("S08_next", title="Next: Fast Methods and Self-Checks")
        final = VGroup(*[pill(s, MAIN, SMALL) for s in ("Bits ↔ octal (3)", "Bits ↔ hex (4)",
                                                        "Octal ↔ hex via bits")]).arrange(RIGHT, buff=0.3)
        self.put(final, "full", BOARD_TOP)
        nxt = self.put(self.next_up("Next: Fast methods and self-checks"), "full", under=final, buff=0.7)
        self.tell("next_01", "Now we have three families of methods. But in an examination, you do not have time to "
                             "try them all.",
                  ("three", LaggedStart(*[FadeIn(p, shift=UP * 0.1) for p in final], lag_ratio=0.3)))
        self.ask("next_02", "How do we choose, and how do we check?", None, ("check", FadeIn(nxt, scale=1.1)))
        self.undock()
        self.finish("S08_next")

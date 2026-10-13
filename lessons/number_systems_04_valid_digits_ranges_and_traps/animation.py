"""
animation.py for the LMS video generator.

Course : C-CAT Computer Fundamentals
Lesson : Lesson 3 - Number Systems Concepts and Representation
Video  : 06 Video 4 - Valid Digits, Ranges and Traps

Source script:
  CCAT_Computer_Fundamentals_Scripts_Lessons_1-5/PDF/Lesson 3 - Number Systems Concepts and Representation/06 Video 4 - Valid Digits, Ranges and Traps.pdf
  The script has no speaker labels. Every line was labelled as below:
    TEACHER  spoken by the teacher: ``self.tell`` / ``self.ask`` (TEACHER_VOICE). Drives the board.
    STUDENT  spoken by a student: ``self.reply`` (STUDENT_VOICE). Every student answer is its own
             narration and appears as a card at the bottom right.
    STAGE    stage direction: not narrated, it becomes the visuals (or the name on the student card).
    BOARD    what the board shows: on screen, not spoken.
  Spoken text uses words ("one zero one one"); the cards and the board show digits ("1011").

Speaker split:
  01 TITLE   Valid Digits, Ranges and Common Base-System Traps
  02 STAGE   The teacher writes four numbers on the board.
  03 BOARD   1012      789      3G      BAD
  04 TEACHER I will ask you something simple. One of these can be a binary number, one can be octal, and so
             on. Let us see how fast you can decide. Is 1012 a valid binary number?
  05 STUDENT No. It has a 2.
  06 TEACHER Why does that rule it out?
  07 STUDENT Binary only has 0 and 1.
  08 TEACHER Is it valid in octal?
  09 STUDENT Yes, because 2 is below 8.
  10 TEACHER Is 789 valid in octal?
  11 STUDENT No, because of the 8 and the 9.
  12 TEACHER In decimal?
  13 STUDENT Yes.
  14 TEACHER What about 3G?
  15 STUDENT G is not a digit in hexadecimal. The letters stop at F.
  16 TEACHER And BAD?
  17 STUDENT Valid in hexadecimal.
  18 TEACHER Notice the rule behind every answer. In any base, every digit must be smaller than the base.
  19 STAGE   The board shows the first trap.
  20 BOARD   TRAP 1: every digit must be LESS THAN the base
  21 BOARD   smallest possible base for a number = largest digit + 1
  22 TEACHER So the smallest base in which 1752 can be written is?
  23 STUDENT 8, because the largest digit is 7.
  24 TEACHER And for 4B?
  25 STUDENT B is 11, so the base must be at least 12.
  26 TEACHER Now the second trap. Look at this.
  27 STAGE   The teacher writes.
  28 BOARD   10 (base 2)   10 (base 8)   10 (base 10)   10 (base 16)
  29 TEACHER The same two symbols. What do they mean?
  30 STUDENT Two, eight, ten and sixteen.
  31 TEACHER Exactly. The symbols alone mean nothing. The base decides. A multiple-choice question will often
             give you a number without a subscript and rely on you assuming decimal. Read the base carefully
             every time.
  32 TEACHER Here is a puzzle. Which is the largest: 1010 in binary, 12 in octal, or A in hexadecimal?
  33 STAGE   The students work it out.
  34 STUDENT 1010 is ten. 12 in octal is one eight plus two, so ten. And A is ten.
  35 TEACHER All equal. The question sets a trap by making them look very different, while they are all the
             same. Never judge by the look of a number.
  36 TEACHER Now the third trap, about ranges. With n digits in base b, how many different numbers can you
             write?
  37 STUDENT b to the power n?
  38 TEACHER Yes. And what is the largest?
  39 STUDENT b to the power n, minus one.
  40 STAGE   The board shows the rule and examples.
  41 BOARD   n digits in base b : b^n values, largest = b^n - 1
  42 BOARD   4 bits         :  2^4 = 16 values   largest 15
  43 BOARD   8 bits         :  2^8 = 256 values  largest 255
  44 BOARD   3 octal digits :  8^3 = 512 values  largest 511 (777 in octal)
  45 BOARD   2 hex digits   : 16^2 = 256 values  largest 255 (FF in hex)
  46 TEACHER Notice that 2 hexadecimal digits and 8 bits give the same count. Why?
  47 STUDENT Because each hex digit is four bits.
  48 TEACHER Perfect. This is why a byte is often written as two hexadecimal digits.
  49 TEACHER One last trap, which is about counting. What follows 7 in octal?
  50 STUDENT 10.
  51 TEACHER What follows 9 in hexadecimal?
  52 STUDENT A.
  53 TEACHER Examiners love this: they ask for the next number after 17 in octal, or the next number after 1F
             in hexadecimal. Do not think in decimal. What is next after 17 in octal?
  54 STUDENT 20, because 7 is the last digit, so we carry.
  55 TEACHER And after 1F in hexadecimal?
  56 STUDENT 20.
  57 TEACHER Exactly. You have understood the rule.
  58 TEACHER Let us run a short drill.
  59 TEACHER Which of these are valid octal numbers? 345, 678, 1070.
  60 STUDENT 345 and 1070. 678 has an 8.
  61 TEACHER How many values can 5 bits represent?
  62 STUDENT 32.
  63 TEACHER What is the largest decimal value of a 2-digit octal number?
  64 STUDENT 63, which is 77 in octal.
  65 STAGE   The teacher nods.
  66 TEACHER Excellent. Notice 8 squared is 64, minus one is 63.
  67 TEACHER Let us summarise.
  68 STAGE   A student reads from her notes.
  69 STUDENT Every digit must be smaller than the base. The smallest possible base is the largest digit plus
             one. The same symbols mean different things in different bases. N digits in base b give b to the
             power n values, with the largest value one less than that. And carrying happens when the digits
             run out.
  70 STAGE   The board holds the final picture.
  71 BOARD   digit < base     |     b^n values     |     carry at the last digit
  72 TEACHER You now know the representation. Next time we put it to work. How do we actually convert a
             number from one system to another, quickly and without error?
  73 STAGE   The board changes to:
  74 BOARD   NEXT LESSON: NUMBER SYSTEM CONVERSIONS

Notes:
  - Opening block ``open_01`` is not in the script: it is the usual breadcrumb opening
    (where we are, what came before, what this video covers).
  - Long teacher lines are split into two narrations where a statement is followed by a question.
  - Facts checked in the data block: which of 1012, 789, 3G, BAD are valid in which base;
    smallest base of 1752 is 8 and of 4B is 12; "10" is 2, 8, 10, 16 in the four bases;
    1010 (base 2) = 12 (base 8) = A (base 16) = 10; the range examples (16/15, 256/255, 512/511 = 777
    octal, 256/255 = FF); 17 + 1 = 20 in octal and 1F + 1 = 20 in hexadecimal; 345 and 1070 are valid
    octal, 678 is not; 5 bits give 32 values; the largest 2-digit octal number is 77 = 63.

Style: 2D, three colours (blue main, grey support, gold highlight). No drawings and no raised
boxes are needed in this video. Pinned KEY IDEAS panel from the first scene to the end.

Section map:
  S00 Opening   S01 Valid or not (trap 1)   S02 The base decides (trap 2)   S03 Ranges (trap 3)
  S04 Counting (trap 4)   S05 A short drill   S06 Summary   S07 Next
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
CRUMB_VIDEO = "Video 4 of 4"
VIDEO_TITLE = "Valid Digits, Ranges and Traps"
BEFORE_LABEL = "Last video"
BEFORE_IDEA = "1 octal digit = 3 bits, 1 hex digit = 4 bits"
TODAY_IDEA = "Four traps examiners build around number systems"

TEACHER_VOICE = "vijay"
STUDENT_VOICE = "kavya"        # students speak in their own voice, in their own blocks
TEACHER_PAUSE = 0.7            # silence after each teacher block (seconds), so speakers never run together
STUDENT_PAUSE = 0.6            # silence after each student block

IDEAS = [("Every digit is less than the base", GOLD), ("Smallest base = largest digit + 1", MAIN),
         ("The base decides the value", MAIN), ("n digits in base b: bⁿ values, largest bⁿ − 1", MAIN),
         ("Carry at the last digit", MAIN)]
P_DIGIT, P_MIN, P_BASE, P_RANGE, P_CARRY = range(5)

YES, NO = "✓", "✗"


def valid_in(s, base):
    """True if every digit of ``s`` is less than ``base``."""
    return all(int(ch, 36) < base for ch in s)


def smallest_base(s):
    return max(int(ch, 36) for ch in s) + 1


assert not valid_in("1012", 2) and valid_in("1012", 8)
assert not valid_in("789", 8) and valid_in("789", 10)
assert not valid_in("3G", 16) and valid_in("BAD", 16)
assert smallest_base("1752") == 8 and smallest_base("4B") == 12
assert [int("10", b) for b in (2, 8, 10, 16)] == [2, 8, 10, 16]
assert int("1010", 2) == int("12", 8) == int("A", 16) == 10
assert (2 ** 4, 2 ** 8, 8 ** 3, 16 ** 2) == (16, 256, 512, 256)
assert int("777", 8) == 511 and int("FF", 16) == 255
assert format(int("17", 8) + 1, "o") == "20" and format(int("1F", 16) + 1, "X") == "20"
assert format(7 + 1, "o") == "10" and format(9 + 1, "X") == "A"
assert [valid_in(s, 8) for s in ("345", "678", "1070")] == [True, False, True]
assert 2 ** 5 == 32 and int("77", 8) == 63 == 8 ** 2 - 1


class ValidDigitsRangesTrapsVideo(LMSScene):
    lesson_title = "Valid Digits, Ranges and Traps"

    def construct(self):
        self.setup_board()
        self.opening("open_01", "Last time we met octal and hexadecimal, where one digit stands for three or four "
                                "bits. In this last video of the lesson, we learn to catch four traps that "
                                "examiners build around number systems.", "video")
        self.open_panel("Key ideas", IDEAS)
        self.valid_or_not()
        self.base_decides()
        self.ranges()
        self.counting()
        self.drill()
        self.summary()
        self.next_lesson()

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

    # ============================================== 1. VALID OR NOT =====

    def valid_or_not(self):
        self.begin("S01_valid", "Valid or Not", "Trap 1: valid or not?")

        tb = table([["Number", "Bin", "Oct", "Dec", "Hex"], ["1012", NO, YES, "", ""], ["789", "", NO, YES, ""],
                    ["3G", "", "", "", NO], ["BAD", "", "", "", YES]], [1.5, 0.95, 0.95, 0.95, 0.95], row_h=0.45,
                   font=FONT)
        self.put(tb, "left", BOARD_TOP)
        for (r, c), t in tb.cell.items():
            if r and c:
                t.set_color(GOLD if t.text == YES else MUTED)
        numbers = VGroup(*[tb.cell[(r, 0)] for r in range(1, 5)])
        rule = self.put(self.note("Every digit must be LESS THAN the base", GOLD), "left", under=tb, buff=0.25)
        least = self.put(self.note("Smallest base = largest digit + 1", MAIN), "left", under=rule, buff=0.2)
        ex1 = self.put(mono("1752: 7 + 1 = 8", LABEL, INK), "right", BOARD_TOP)
        ex2 = self.put(mono("4B: 11 + 1 = 12", LABEL, INK), "right", under=ex1, buff=0.3)

        def verdict(r, c):
            return FadeIn(tb.cell[(r, c)], scale=1.4)

        self.play(FadeIn(tb.rows[0]), LaggedStart(*[FadeIn(t, shift=RIGHT * 0.15) for t in numbers], lag_ratio=0.3),
                  run_time=1.4)
        self.tell("val_01", "I will ask you something simple. One of these can be a binary number, one can be octal, "
                            "and so on. Let us see how fast you can decide.",
                  ("binary", Indicate(numbers, color=GOLD, scale_factor=1.05)))
        self.ask("val_02", "Is one zero one two a valid binary number?", "Is 1012 a valid binary number?")
        self.reply("val_03", "No. It has a two.", "No. It has a 2.", (None, verdict(1, 1)))
        self.ask("val_04", "Why does that rule it out?")
        self.reply("val_05", "Binary only has zero and one.", "Binary only has 0 and 1.")
        self.ask("val_06", "Is it valid in octal?", "Is 1012 valid in octal?")
        self.reply("val_07", "Yes, because two is below eight.", "Yes, because 2 is below 8.", (None, verdict(1, 2)))
        self.ask("val_08", "Is seven eight nine valid in octal?", "Is 789 valid in octal?")
        self.reply("val_09", "No, because of the eight and the nine.", "No, because of the 8 and the 9.",
                   (None, verdict(2, 2)))
        self.ask("val_10", "In decimal?", "Is 789 valid in decimal?")
        self.reply("val_11", "Yes.", None, (None, verdict(2, 3)))
        self.ask("val_12", "What about three G?", "What about 3G?")
        self.reply("val_13", "G is not a digit in hexadecimal. The letters stop at F.",
                   "G is not a hex digit. The letters stop at F.", (None, verdict(3, 4)))
        self.ask("val_14", "And B A D?", "And BAD?")
        self.reply("val_15", "Valid in hexadecimal.", None, (None, verdict(4, 4)))
        self.tell("val_16", "Notice the rule behind every answer. In any base, every digit must be smaller than the "
                            "base.",
                  ("every", FadeIn(rule, shift=UP * 0.1)), ("smaller", lambda: self.add_row(P_DIGIT)))

        self.play(FadeIn(least, shift=UP * 0.1), run_time=0.6)
        self.ask("min_01", "So the smallest base in which one seven five two can be written is?",
                 "Smallest base in which 1752 can be written?")
        self.reply("min_02", "Eight, because the largest digit is seven.", "8, because the largest digit is 7.",
                   (None, FadeIn(ex1, shift=UP * 0.1)))
        self.ask("min_03", "And for four B?", "And for 4B?")
        self.reply("min_04", "B is eleven, so the base must be at least twelve.",
                   "B is 11, so the base is at least 12.", (None, FadeIn(ex2, shift=UP * 0.1)))
        self.hush()
        self.add_row(P_MIN)

        self.finish("S01_valid")

    # ============================================== 2. THE BASE DECIDES =

    def base_decides(self):
        self.begin("S02_base", "The Base Decides", "Trap 2: the base decides")

        tens = VGroup(*[num("10", b, TITLE - 6) for b in (2, 8, 10, 16)]).arrange(RIGHT, buff=1.2)
        self.put(tens, "full", BOARD_TOP)
        means = VGroup(*[mono(f"= {b}", LABEL, GOLD).next_to(t, DOWN, buff=0.25)
                         for t, b in zip(tens, (2, 8, 10, 16))])
        decides = self.put(self.note("The symbols mean nothing alone: the base decides", GOLD), "left", under=means,
                           buff=0.45)
        read = self.put(self.note("No subscript? Do not assume decimal", MAIN), "left", under=decides, buff=0.2)

        three = VGroup(num("1010", 2, TITLE - 6), num("12", 8, TITLE - 6), num("A", 16, TITLE - 6))
        three.arrange(RIGHT, buff=1.2)
        self.put(three, "full", BOARD_TOP)
        vals = VGroup(*[mono("= 10", LABEL, GOLD).next_to(t, DOWN, buff=0.25) for t in three])
        equal = self.put(self.note("All equal 10: never judge a number by its look", GOLD), "left", under=vals,
                         buff=0.45)

        self.tell("t2_01", "Now the second trap. Look at this.",
                  ("Look", LaggedStart(*[FadeIn(t, shift=UP * 0.1) for t in tens], lag_ratio=0.3)))
        self.ask("t2_02", "The same two symbols. What do they mean?")
        self.reply("t2_03", "Two, eight, ten and sixteen.", "2, 8, 10 and 16.",
                   ("Two", FadeIn(means[0], shift=UP * 0.1)), ("eight", FadeIn(means[1], shift=UP * 0.1)),
                   ("ten", FadeIn(means[2], shift=UP * 0.1)), ("sixteen", FadeIn(means[3], shift=UP * 0.1)))
        self.tell("t2_04", "Exactly. The symbols alone mean nothing. The base decides. A multiple-choice question "
                           "will often give you a number without a subscript and rely on you assuming decimal. Read "
                           "the base carefully every time.",
                  ("decides", FadeIn(decides, shift=UP * 0.1)), ("subscript", FadeIn(read, shift=UP * 0.1)),
                  ("carefully", lambda: self.add_row(P_BASE)))

        self.drop_q()
        self.play(FadeOut(VGroup(tens, means, decides, read)), run_time=0.5)
        self.play(LaggedStart(*[FadeIn(t, shift=UP * 0.1) for t in three], lag_ratio=0.3), run_time=1.0)
        self.ask("t2_05", "Here is a puzzle. Which is the largest: one zero one zero in binary, one two in octal, or "
                          "A in hexadecimal?",
                 "Which is the largest: 1010 in binary, 12 in octal, or A in hexadecimal?")
        self.reply("t2_06", "One zero one zero is ten. One two in octal is one eight plus two, so ten. And A is "
                            "ten.", "1010 is 10. 12 in octal is 8 + 2 = 10. A is 10.",
                   ("ten", FadeIn(vals[0], shift=UP * 0.1)), (("ten", 2), FadeIn(vals[1], shift=UP * 0.1)),
                   (("ten", 3), FadeIn(vals[2], shift=UP * 0.1)), who="Students")
        self.tell("t2_07", "All equal. The question sets a trap by making them look very different, while they are "
                           "all the same. Never judge by the look of a number.",
                  ("equal", Indicate(vals, color=GOLD, scale_factor=1.15)), ("Never", FadeIn(equal, shift=UP * 0.1)))

        self.finish("S02_base")

    # ============================================== 3. RANGES ===========

    def ranges(self):
        self.begin("S03_ranges", "Ranges", "Trap 3: ranges")

        tb = table([["n digits in base b", "bⁿ values", "Largest = bⁿ − 1"],
                    ["4 bits", "2⁴ = 16", "15"], ["8 bits", "2⁸ = 256", "255"],
                    ["3 octal digits", "8³ = 512", "511 (777 in octal)"],
                    ["2 hex digits", "16² = 256", "255 (FF in hex)"]], [3.3, 2.6, 3.6], row_h=0.45, font=FONT)
        self.put(tb, "full", BOARD_TOP)
        byte = self.put(self.note("1 byte = 8 bits = 2 hex digits", GOLD), "left", under=tb, buff=0.4)

        self.ask("t3_01", "Now the third trap, about ranges. With n digits in base b, how many different numbers "
                          "can you write?", "With n digits in base b, how many different numbers can you write?")
        self.reply("t3_02", "b to the power n?", "bⁿ?")
        self.ask("t3_03", "Yes. And what is the largest?", "And what is the largest?")
        self.reply("t3_04", "b to the power n, minus one.", "bⁿ − 1.",
                   (None, FadeIn(tb.rows[0], shift=UP * 0.1)))
        self.hush()
        self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.15) for r in tb.rows[1:]], lag_ratio=0.5), run_time=2.4)
        self.ask("t3_05", "Notice that two hexadecimal digits and eight bits give the same count. Why?",
                 "2 hex digits and 8 bits give the same count. Why?",
                 ("hexadecimal", Indicate(tb.rows[4], color=GOLD, scale_factor=1.04)),
                 ("eight", Indicate(tb.rows[2], color=GOLD, scale_factor=1.04)))
        self.reply("t3_06", "Because each hex digit is four bits.")
        self.tell("t3_07", "Perfect. This is why a byte is often written as two hexadecimal digits.",
                  ("byte", FadeIn(byte, shift=UP * 0.1)), ("digits", lambda: self.add_row(P_RANGE)))

        self.finish("S03_ranges")

    # ============================================== 4. COUNTING =========

    def counting(self):
        self.begin("S04_counting", "Counting", "Trap 4: counting")

        tb = table([["Octal", "7", "→", "10"], ["Hexadecimal", "9", "→", "A"], ["Octal", "17", "→", "20"],
                    ["Hexadecimal", "1F", "→", "20"]], [2.6, 0.9, 0.7, 0.9], row_h=0.55, head=False)
        self.put(tb, "left", BOARD_TOP)
        for r in range(4):
            tb.cell[(r, 0)].set_color(MUTED)
            tb.cell[(r, 3)].set_color(GOLD)
        think = self.put(self.note("Do not think in decimal", GOLD), "left", under=tb, buff=0.45)

        def row(r):
            return LaggedStart(*[FadeIn(tb.cell[(r, c)], shift=RIGHT * 0.1) for c in range(4)], lag_ratio=0.25)

        self.ask("t4_01", "One last trap, which is about counting. What follows seven in octal?",
                 "What follows 7 in octal?")
        self.reply("t4_02", "One zero.", "10.", (None, row(0)))
        self.ask("t4_03", "What follows nine in hexadecimal?", "What follows 9 in hexadecimal?")
        self.reply("t4_04", "A.", None, (None, row(1)))
        self.tell("t4_05", "Examiners love this: they ask for the next number after one seven in octal, or the next "
                           "number after one F in hexadecimal. Do not think in decimal.",
                  ("think", FadeIn(think, shift=UP * 0.1)))
        self.ask("t4_06", "What is next after one seven in octal?", "What is next after 17 in octal?")
        self.reply("t4_07", "Two zero, because seven is the last digit, so we carry.",
                   "20, because 7 is the last digit, so we carry.", (None, row(2)))
        self.ask("t4_08", "And after one F in hexadecimal?", "And after 1F in hexadecimal?")
        self.reply("t4_09", "Two zero.", "20.", (None, row(3)))
        self.tell("t4_10", "Exactly. You have understood the rule.", ("rule", lambda: self.add_row(P_CARRY)))

        self.finish("S04_counting")

    # ============================================== 5. A SHORT DRILL ====

    def drill(self):
        self.begin("S05_drill", "A Short Drill", "A short drill")

        tb = table([["345", "678", "1070"], [YES, NO, YES]], [1.5, 1.5, 1.5], row_h=0.55, head=False, font=FONT)
        self.put(tb, "left", BOARD_TOP)
        tb.cell[(1, 0)].set_color(GOLD)
        tb.cell[(1, 1)].set_color(MUTED)
        tb.cell[(1, 2)].set_color(GOLD)
        five = self.put(mono("5 bits: 2⁵ = 32 values", LABEL, INK), "left", under=tb, buff=0.5)
        octal = self.put(mono("77 in octal = 63", LABEL, INK), "left", under=five, buff=0.3)
        square = self.put(mono("8² − 1 = 64 − 1 = 63", LABEL, GOLD), "left", under=octal, buff=0.3)

        self.tell("dr_01", "Let us run a short drill.")
        self.ask("dr_02", "Which of these are valid octal numbers? Three four five, six seven eight, one zero seven "
                          "zero.", "Which of these are valid octal numbers? 345, 678, 1070",
                 ("Three", FadeIn(tb.rows[0], shift=UP * 0.1)))
        self.reply("dr_03", "Three four five and one zero seven zero. Six seven eight has an eight.",
                   "345 and 1070. 678 has an 8.",
                   (None, LaggedStart(*[FadeIn(tb.cell[(1, c)], scale=1.4) for c in (0, 2, 1)], lag_ratio=0.5)))
        self.ask("dr_04", "How many values can five bits represent?", "How many values can 5 bits represent?")
        self.reply("dr_05", "Thirty-two.", "32.", (None, FadeIn(five, shift=UP * 0.1)))
        self.ask("dr_06", "What is the largest decimal value of a two digit octal number?",
                 "What is the largest decimal value of a 2-digit octal number?")
        self.reply("dr_07", "Sixty-three, which is seven seven in octal.", "63, which is 77 in octal.",
                   (None, FadeIn(octal, shift=UP * 0.1)))
        self.tell("dr_08", "Excellent. Notice eight squared is sixty-four, minus one is sixty-three.",
                  ("squared", FadeIn(square, shift=UP * 0.1)), ("minus", lambda: self.light(P_RANGE)))

        self.finish("S05_drill")

    # ============================================== 6. SUMMARY ==========

    def summary(self):
        self.begin("S06_summary", "Summary", "Summary", GOLD)

        rows = self.put(self.ticks(["Every digit is smaller than the base",
                                    "Smallest base = largest digit + 1",
                                    "Same symbols, different base, different value",
                                    "n digits in base b: bⁿ values, largest bⁿ − 1",
                                    "Carry when the digits run out"]), "full", BOARD_HIGH, "l")

        self.tell("sum_01", "Let us summarise.")
        self.reply("sum_02", "Every digit must be smaller than the base. The smallest possible base is the largest "
                             "digit plus one. The same symbols mean different things in different bases. N digits "
                             "in base b give b to the power n values, with the largest value one less than that. "
                             "And carrying happens when the digits run out.", "Reading from her notes",
                   ("digit", lambda: [FadeIn(rows[0], shift=RIGHT * 0.2), self.light(P_DIGIT)]),
                   ("smallest", lambda: [FadeIn(rows[1], shift=RIGHT * 0.2), self.light(P_MIN)]),
                   ("symbols", lambda: [FadeIn(rows[2], shift=RIGHT * 0.2), self.light(P_BASE)]),
                   ("power", lambda: [FadeIn(rows[3], shift=RIGHT * 0.2), self.light(P_RANGE)]),
                   ("carrying", lambda: [FadeIn(rows[4], shift=RIGHT * 0.2), self.light(P_CARRY)]),
                   who="A student")
        self.hush()
        self.play(*self.all_lit())
        self.finish("S06_summary")

    # ============================================== 7. NEXT =============

    def next_lesson(self):
        self.scene_start("S07_next", title="Next Lesson: Number System Conversions")
        final = VGroup(*[pill(s, MAIN, LABEL) for s in ("Digit < base", "bⁿ values", "Carry at the last digit")])
        final.arrange(RIGHT, buff=0.3)
        self.put(final, "full", BOARD_TOP)
        nxt = self.put(self.next_up("Next lesson: Number system conversions"), "full", under=final, buff=0.7)
        self.tell("next_01", "You now know the representation. Next time we put it to work.",
                  ("representation", LaggedStart(*[FadeIn(p, shift=UP * 0.1) for p in final], lag_ratio=0.3)))
        self.ask("next_02", "How do we actually convert a number from one system to another, quickly and without "
                            "error?", "How do we convert a number from one system to another, quickly and without "
                                      "error?", ("convert", FadeIn(nxt, scale=1.1)))
        self.undock()
        self.finish("S07_next")

"""
animation.py for the LMS video generator.

Course : C-CAT Computer Fundamentals
Lesson : Lesson 3 - Number Systems Concepts and Representation
Video  : 05 Video 3 - Octal and Hexadecimal

Source script:
  CCAT_Computer_Fundamentals_Scripts_Lessons_1-5/PDF/Lesson 3 - Number Systems Concepts and Representation/05 Video 3 - Octal and Hexadecimal.pdf
  The script has no speaker labels. Every line was labelled as below:
    TEACHER  spoken by the teacher: ``self.tell`` / ``self.ask`` (TEACHER_VOICE). Drives the board.
    STUDENT  spoken by a student: ``self.reply`` (STUDENT_VOICE). Every student answer is its own
             narration and appears as a card at the bottom right.
    STAGE    stage direction: not narrated, it becomes the visuals (or the name on the student card).
    BOARD    what the board shows: on screen, not spoken.
  Spoken text uses words ("one zero one one"); the cards and the board show digits ("1011").

Speaker split:
  01 TITLE   Octal and Hexadecimal: Compact Ways to Write Binary
  02 STAGE   The board shows a long binary number.
  03 BOARD   110101101
  04 TEACHER Read this aloud to me.
  05 STUDENT One one zero one zero one one zero one.
  06 TEACHER How long did that take?
  07 STUDENT Quite long. And I am not sure I would copy it correctly.
  08 TEACHER That is the problem. Programmers and engineers deal with long binary strings every day. We need
             something shorter that still maps neatly back to binary. Let us try something. I will split the
             number into groups of three bits, starting from the right.
  09 STAGE   The teacher writes.
  10 BOARD   110   101   101
  11 TEACHER Each group of three bits can only be one of eight patterns, from 000 to 111. What values do
             those groups have?
  12 STUDENT 6, 5 and 5.
  13 TEACHER So the number can be written as 655. We have compressed nine bits into three digits. This is the
             octal system.
  14 STAGE   The board shows:
  15 BOARD   OCTAL       base 8      digits 0 to 7      weights 1, 8, 64, 512
  16 TEACHER Why group by three bits?
  17 STUDENT Because three bits make eight patterns, and eight is the base of octal.
  18 TEACHER Exactly. That is not a coincidence. 8 is 2 to the power 3, so one octal digit corresponds to
             exactly three bits.
  19 TEACHER Now let me try a different grouping on the same number. Groups of four bits, from the right. We
             pad the left with zeros.
  20 STAGE   The board shows:
  21 BOARD   0001   1010   1101
  22 TEACHER Four bits make sixteen patterns, so one digit has to represent values from 0 to 15. But we only
             have ten digit symbols. What can we do?
  23 STUDENT Use letters?
  24 TEACHER We borrow the first six letters of the alphabet.
  25 BOARD   A = 10   B = 11   C = 12   D = 13   E = 14   F = 15
  26 TEACHER The groups have values 1, 10 and 13. So the number is 1AD. This is the hexadecimal system.
  27 STAGE   The board shows:
  28 BOARD   HEXADECIMAL  base 16   digits 0-9, A-F   weights 1, 16, 256, 4096
  29 TEACHER Because 16 is 2 to the power 4, one hexadecimal digit corresponds to exactly four bits. So two
             hexadecimal digits represent a full byte.
  30 STAGE   A student asks:
  31 STUDENT Are 655 in octal and 1AD in hexadecimal the same number?
  32 TEACHER Yes. They are the same quantity as the binary 110101101. In decimal, all of them equal 429. We
             will practise the arithmetic in the next lesson. For now, the point is the relationship. Binary,
             octal and hexadecimal are three ways of writing the same bit pattern, with different amounts of
             compression.
  33 TEACHER Here is the table you should know by heart.
  34 STAGE   The board shows the table.
  35 BOARD   DEC   BIN    OCT   HEX
  36 BOARD    0    0000    0     0
  37 BOARD    1    0001    1     1
  38 BOARD    2    0010    2     2
  39 BOARD    3    0011    3     3
  40 BOARD    4    0100    4     4
  41 BOARD    5    0101    5     5
  42 BOARD    6    0110    6     6
  43 BOARD    7    0111    7     7
  44 BOARD    8    1000   10     8
  45 BOARD    9    1001   11     9
  46 BOARD   10    1010   12     A
  47 BOARD   11    1011   13     B
  48 BOARD   12    1100   14     C
  49 BOARD   13    1101   15     D
  50 BOARD   14    1110   16     E
  51 BOARD   15    1111   17     F
  52 TEACHER Look at row 8. After 7 in octal, what comes next?
  53 STUDENT 10.
  54 TEACHER Because there is no digit 8 in octal. And what comes after 9 in hexadecimal?
  55 STUDENT A.
  56 TEACHER And after F?
  57 STUDENT 10, which is sixteen.
  58 TEACHER Exactly. Each system carries when it runs out of digits.
  59 TEACHER Where do you see hexadecimal in real life?
  60 STUDENT Colour codes in web pages?
  61 TEACHER Yes, such as the code for red, FF0000. Also in memory addresses and in the addresses of network
             devices. Wherever people need to read or write a long binary pattern, hexadecimal is the usual
             choice.
  62 TEACHER Let us test. How many bits does one octal digit represent?
  63 STUDENT Three.
  64 TEACHER And one hexadecimal digit?
  65 STUDENT Four.
  66 TEACHER What is the weight of the second position from the right in hexadecimal?
  67 STUDENT 16.
  68 TEACHER Good. Let us summarise.
  69 STAGE   A student reads from her notes.
  70 STUDENT Octal has base 8 and digits 0 to 7, and each digit equals three bits. Hexadecimal has base 16
             and digits 0 to 9 and A to F, and each digit equals four bits. They are compact ways to write
             binary.
  71 STAGE   The board holds the final picture.
  72 BOARD   1 octal digit = 3 bits        1 hex digit = 4 bits
  73 TEACHER Now that you know the four systems, you also need to know how to catch the traps that examiners
             build around them. That is next.
  74 STAGE   The board changes to:
  75 BOARD   NEXT: VALID DIGITS, RANGES AND TRAPS

Notes:
  - Opening block ``open_01`` is not in the script: it is the usual breadcrumb opening
    (where we are, what came before, what this video covers).
  - Long teacher lines are split into two narrations where a statement is followed by a question.
  - Facts checked in the data block: 110101101 (base 2) = 655 (base 8) = 1AD (base 16) = 429;
    the groups 110 101 101 = 6 5 5 and 0001 1010 1101 = 1 10 13 = 1 A D; the 0 to 15 table in
    all four systems; 8 = 2^3 and 16 = 2^4; hexadecimal weights 1, 16, 256, 4096.

Style: 2D, three colours (blue main, grey support, gold highlight). No drawings and no raised
boxes are needed in this video. Pinned KEY IDEAS panel from the first scene to the end.

Section map:
  S00 Opening   S01 Groups of three: octal   S02 Groups of four: hexadecimal
  S03 One pattern, three ways   S04 The table to know   S05 Uses and a quick test
  S06 Summary   S07 Next
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
CRUMB_VIDEO = "Video 3 of 4"
VIDEO_TITLE = "Octal and Hexadecimal"
BEFORE_LABEL = "Last video"
BEFORE_IDEA = "n bits give 2ⁿ patterns"
TODAY_IDEA = "Two compact ways to write a long binary number"

TEACHER_VOICE = "vijay"
STUDENT_VOICE = "kavya"        # students speak in their own voice, in their own blocks
TEACHER_PAUSE = 0.7            # silence after each teacher block (seconds), so speakers never run together
STUDENT_PAUSE = 0.6            # silence after each student block

IDEAS = [("Octal: base 8, digits 0 to 7", GOLD), ("1 octal digit = 3 bits", MAIN),
         ("Hex: base 16, digits 0 to 9, A to F", GOLD), ("1 hex digit = 4 bits", MAIN),
         ("Same bit pattern, three ways", MAIN)]
P_OCT, P_OCT3, P_HEX, P_HEX4, P_SAME = range(5)

BITS = "110101101"
ROWS16 = [[str(k), format(k, "04b"), format(k, "o"), format(k, "X")] for k in range(16)]

assert int(BITS, 2) == 429 == int("655", 8) == int("1AD", 16)
assert [int(g, 2) for g in ("110", "101", "101")] == [6, 5, 5]
assert [int(g, 2) for g in ("0001", "1010", "1101")] == [1, 10, 13] and "A D".split() == ["A", "D"]
assert format(10, "X") == "A" and format(13, "X") == "D" and format(15, "X") == "F"
assert 2 ** 3 == 8 and 2 ** 4 == 16 and [16 ** k for k in range(4)] == [1, 16, 256, 4096]
assert [8 ** k for k in range(4)] == [1, 8, 64, 512]
assert ROWS16[8] == ["8", "1000", "10", "8"] and ROWS16[10] == ["10", "1010", "12", "A"]
assert format(int("F", 16) + 1, "X") == "10" and int("10", 16) == 16


class OctalAndHexadecimalVideo(LMSScene):
    lesson_title = "Octal and Hexadecimal"

    def construct(self):
        self.setup_board()
        self.opening("open_01", "Last time we counted in binary, and saw that n bits give two to the power n "
                                "patterns. In this video we meet octal and hexadecimal, two compact ways to write a "
                                "long binary number.", "video")
        self.open_panel("Key ideas", IDEAS)
        self.octal()
        self.hexadecimal()
        self.same_number()
        self.the_table()
        self.uses_and_test()
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

    # ===================================== 1. GROUPS OF THREE: OCTAL ====

    def octal(self):
        self.begin("S01_octal", "Groups of Three: Octal", "A shorter way to write binary")

        gap = 0.35
        cells = self.put(bit_cells(BITS, 0.55, font_size=LABEL), "left", BOARD_TOP)
        vals = group_values(cells, 3, gap, ["6", "5", "5"])
        need = self.put(self.note("Needed: shorter, but maps back to binary", MAIN), "left", under=cells, buff=0.5)
        result = self.put(mono("110101101 in binary = 655 in octal", SMALL, INK), "left", under=cells, buff=0.95)
        info = self.put(self.note("Octal: base 8, digits 0 to 7, weights 1, 8, 64, 512", MAIN), "left",
                        under=result, buff=0.35)
        why = self.put(self.note("8 = 2³, so 1 octal digit = 3 bits", GOLD), "left", under=result, buff=0.35)

        self.play(FadeIn(cells, shift=UP * 0.1), run_time=0.6)
        self.ask("oct_01", "Read this aloud to me.", "Read 110101101 aloud.")
        self.reply("oct_02", "One one zero one zero one one zero one.", "1 1 0 1 0 1 1 0 1",
                   (None, LaggedStart(*[Indicate(c, color=GOLD, scale_factor=1.15) for c in cells], lag_ratio=0.5,
                                      run_time=3.0)))
        self.ask("oct_03", "How long did that take?")
        self.reply("oct_04", "Quite long. And I am not sure I would copy it correctly.",
                   "Quite long. I might copy it wrongly.")
        self.tell("oct_05", "That is the problem. Programmers and engineers deal with long binary strings every "
                            "day. We need something shorter that still maps neatly back to binary.",
                  ("shorter", FadeIn(need, shift=UP * 0.1)))
        self.drop_q()
        self.tell("oct_06", "Let us try something. I will split the number into groups of three bits, starting from "
                            "the right.",
                  ("split", lambda: [FadeOut(need)] + split(cells, 3, gap)))
        self.ask("oct_07", "Each group of three bits can only be one of eight patterns, from zero zero zero to one "
                           "one one. What values do those groups have?", "What values do the three groups have?")
        self.reply("oct_08", "Six, five and five.", "6, 5 and 5.",
                   (None, LaggedStart(*[FadeIn(v, shift=UP * 0.1) for v in vals], lag_ratio=0.5)))
        self.tell("oct_09", "So the number can be written as six five five. We have compressed nine bits into three "
                            "digits. This is the octal system.",
                  ("written", FadeIn(result, shift=UP * 0.1)),
                  ("compressed", Indicate(vals, color=GOLD, scale_factor=1.15)),
                  ("octal", FadeIn(info, shift=UP * 0.1)), (None, lambda: self.add_row(P_OCT)))
        self.ask("oct_10", "Why group by three bits?")
        self.reply("oct_11", "Because three bits make eight patterns, and eight is the base of octal.",
                   "3 bits make 8 patterns: the base of octal.")
        self.tell("oct_12", "Exactly. That is not a coincidence. Eight is two to the power three, so one octal digit "
                            "corresponds to exactly three bits.",
                  ("power", lambda: [FadeOut(info), FadeIn(why, shift=UP * 0.1)]),
                  ("exactly", lambda: self.add_row(P_OCT3)))

        self.finish("S01_octal")

    # ================================= 2. GROUPS OF FOUR: HEXADECIMAL ===

    def hexadecimal(self):
        self.begin("S02_hex", "Groups of Four: Hexadecimal", "The same number in groups of four")

        gap = 0.4
        cells = self.put(bit_cells("000" + BITS, 0.55, font_size=LABEL), "full", BOARD_TOP, "r")
        cells.shift(LEFT * 1.6)
        pads = VGroup(*cells[:3])
        for p in pads:
            p[1].set_color(MUTED)
        vals = group_values(cells, 4, gap, ["1", "10", "13"], LABEL, MUTED)
        digits = group_values(cells, 4, gap, ["1", "A", "D"], BODY, GOLD, drop=0.95)
        letters = self.put(mono("A=10 B=11 C=12 D=13 E=14 F=15", LABEL, MAIN), "left", under=cells, buff=1.5)
        info = self.put(self.note("Hexadecimal: base 16, digits 0-9 and A-F, weights 1, 16, 256, 4096", MAIN),
                        "left", under=letters, buff=0.3)
        why = self.put(self.note("16 = 2⁴, so 1 hex digit = 4 bits. 2 hex digits = 1 byte", GOLD), "left",
                       under=letters, buff=0.3)

        self.play(FadeIn(VGroup(*cells[3:]), shift=UP * 0.1), run_time=0.6)
        self.tell("hex_01", "Now let me try a different grouping on the same number. Groups of four bits, from the "
                            "right. We pad the left with zeros.",
                  ("four", lambda: split(cells, 4, gap, hidden=list(pads))),
                  ("pad", LaggedStart(*[FadeIn(p, shift=DOWN * 0.15) for p in pads], lag_ratio=0.3)))
        self.ask("hex_02", "Four bits make sixteen patterns, so one digit has to represent values from zero to "
                           "fifteen. But we only have ten digit symbols. What can we do?",
                 "One digit must show 0 to 15, but we have only ten digit symbols. What can we do?")
        self.reply("hex_03", "Use letters?")
        self.tell("hex_04", "We borrow the first six letters of the alphabet.",
                  ("letters", FadeIn(letters, shift=UP * 0.1)))
        self.drop_q()
        self.tell("hex_05", "The groups have values one, ten and thirteen. So the number is one A D. This is the "
                            "hexadecimal system.",
                  ("values", LaggedStart(*[FadeIn(v, shift=UP * 0.1) for v in vals], lag_ratio=0.5)),
                  ("number", LaggedStart(*[FadeIn(d, shift=UP * 0.1) for d in digits], lag_ratio=0.4)),
                  ("hexadecimal", FadeIn(info, shift=UP * 0.1)), (None, lambda: self.add_row(P_HEX)))
        self.tell("hex_06", "Because sixteen is two to the power four, one hexadecimal digit corresponds to exactly "
                            "four bits. So two hexadecimal digits represent a full byte.",
                  ("power", lambda: [FadeOut(info), FadeIn(why, shift=UP * 0.1)]),
                  ("byte", lambda: self.add_row(P_HEX4)))

        self.finish("S02_hex")

    # ================================= 3. ONE PATTERN, THREE WAYS =======

    def same_number(self):
        self.begin("S03_same", "One Pattern, Three Ways", "One bit pattern, three ways to write it")

        tb = table([["Binary", BITS], ["Octal", "655"], ["Hexadecimal", "1AD"], ["Decimal", "429"]], [2.7, 2.6],
                   row_h=0.6, head=False)
        self.put(tb, "left", BOARD_HIGH - 0.1)
        for r in range(4):
            tb.cell[(r, 0)].set_color(MUTED)
        tb.cell[(3, 1)].set_color(GOLD)
        same = self.put(self.note("Same quantity: more or less compression", GOLD), "left", under=tb, buff=0.45)

        self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.15) for r in tb.rows[:3]], lag_ratio=0.3), run_time=1.2)
        self.reply("same_01", "Are six five five in octal and one A D in hexadecimal the same number?",
                   "Are 655 in octal and 1AD in hex the same number?", who="A student asks")
        self.tell("same_02", "Yes. They are the same quantity as the binary one one zero one zero one one zero one. "
                             "In decimal, all of them equal four hundred and twenty-nine. We will practise the "
                             "arithmetic in the next lesson.",
                  ("binary", Indicate(tb.rows[0], color=GOLD, scale_factor=1.05)),
                  ("decimal", FadeIn(tb.rows[3], shift=RIGHT * 0.15)))
        self.tell("same_03", "For now, the point is the relationship. Binary, octal and hexadecimal are three ways "
                             "of writing the same bit pattern, with different amounts of compression.",
                  ("three", FadeIn(same, shift=UP * 0.1)), ("compression", lambda: self.add_row(P_SAME)))

        self.finish("S03_same")

    # ================================= 4. THE TABLE TO KNOW =============

    def the_table(self):
        self.begin("S04_table", "The Table to Know", "The table to know by heart")

        head = ["Dec", "Bin", "Oct", "Hex"]
        widths = [0.78, 0.95, 0.75, 0.75]
        ta = table([head] + ROWS16[:8], widths, row_h=0.42, size=SMALL)
        tb = table([head] + ROWS16[8:], widths, row_h=0.42, size=SMALL)
        both = VGroup(ta, tb).arrange(RIGHT, buff=0.3, aligned_edge=UP)
        self.put(both, "left", BOARD_TOP)
        after_f = self.put(mono("F → 10", LABEL, GOLD), "right", BOARD_TOP)
        carry = self.put(self.note("Out of digits: carry", GOLD, "right", SMALL), "right", under=after_f, buff=0.3)

        self.tell("tab_01", "Here is the table you should know by heart.",
                  ("table", LaggedStart(*[FadeIn(r, shift=RIGHT * 0.1) for r in ta.rows + tb.rows], lag_ratio=0.15,
                                        run_time=3.0)))
        self.ask("tab_02", "Look at row eight. After seven in octal, what comes next?",
                 "After 7 in octal, what comes next?",
                 ("seven", lambda: [ta.cell[(8, 2)].animate.set_color(GOLD),
                                    Indicate(ta.rows[8], color=GOLD, scale_factor=1.08)]))
        self.reply("tab_03", "One zero.", "10.",
                   (None, lambda: [tb.cell[(1, 2)].animate.set_color(GOLD),
                                   Indicate(tb.cell[(1, 2)], color=GOLD, scale_factor=1.5)]))
        self.tell("tab_04", "Because there is no digit eight in octal.",
                  ("digit", Indicate(ta.col(2), color=GOLD, scale_factor=1.05)))
        self.ask("tab_05", "And what comes after nine in hexadecimal?", "What comes after 9 in hexadecimal?",
                 ("nine", lambda: [tb.cell[(2, 3)].animate.set_color(GOLD),
                                   Indicate(tb.rows[2], color=GOLD, scale_factor=1.08)]))
        self.reply("tab_06", "A.", "A.",
                   (None, lambda: [tb.cell[(3, 3)].animate.set_color(GOLD),
                                   Indicate(tb.cell[(3, 3)], color=GOLD, scale_factor=1.5)]))
        self.ask("tab_07", "And after F?", "And after F in hexadecimal?",
                 (None, lambda: [tb.cell[(8, 3)].animate.set_color(GOLD),
                                 Indicate(tb.cell[(8, 3)], color=GOLD, scale_factor=1.5)]))
        self.reply("tab_08", "One zero, which is sixteen.", "10, which is sixteen.",
                   (None, FadeIn(after_f, shift=UP * 0.1)))
        self.tell("tab_09", "Exactly. Each system carries when it runs out of digits.",
                  ("carries", FadeIn(carry, shift=UP * 0.1)))

        self.finish("S04_table")

    # ================================= 5. USES AND A QUICK TEST =========

    def uses_and_test(self):
        self.begin("S05_uses", "Uses and a Quick Test", "Where hexadecimal is used")

        uses = stack(self.note("Colour codes: FF0000 is red", GOLD), self.note("Memory addresses", MAIN),
                     self.note("Addresses of network devices", MAIN), buff=0.25)
        self.put(uses, "left", BOARD_TOP, "l")
        oct3 = self.put(mono("1 octal digit = 3 bits", LABEL, INK), "left", BOARD_TOP)
        hex4 = self.put(mono("1 hex digit   = 4 bits", LABEL, INK), "left", under=oct3, buff=0.3)
        wt = table([["4096", "256", "16", "1"]], [1.1, 1.0, 0.9, 0.8], head=False)
        self.put(wt, "left", under=hex4, buff=0.55)
        wt_tag = self.put(text("Hexadecimal weights", SMALL, MUTED, BOLD), "left", under=wt, buff=0.15)

        self.ask("use_01", "Where do you see hexadecimal in real life?")
        self.reply("use_02", "Colour codes in web pages?")
        self.tell("use_03", "Yes, such as the code for red, F F zero zero zero zero. Also in memory addresses and in "
                            "the addresses of network devices. Wherever people need to read or write a long binary "
                            "pattern, hexadecimal is the usual choice.",
                  ("red", FadeIn(uses[0], shift=UP * 0.1)), ("memory", FadeIn(uses[1], shift=UP * 0.1)),
                  ("network", FadeIn(uses[2], shift=UP * 0.1)), ("usual", lambda: self.light(P_HEX, P_HEX4)))

        self.play(FadeOut(uses), run_time=0.4)
        self.ask("tst_01", "Let us test. How many bits does one octal digit represent?",
                 "How many bits does one octal digit represent?")
        self.reply("tst_02", "Three.", "3.", (None, lambda: [FadeIn(oct3, shift=UP * 0.1), self.light(P_OCT3)]))
        self.ask("tst_03", "And one hexadecimal digit?", "And one hexadecimal digit?")
        self.reply("tst_04", "Four.", "4.", (None, lambda: [FadeIn(hex4, shift=UP * 0.1), self.light(P_HEX4)]))
        self.ask("tst_05", "What is the weight of the second position from the right in hexadecimal?",
                 "Weight of the second position from the right in hexadecimal?",
                 ("weight", lambda: [FadeIn(wt, shift=UP * 0.1), FadeIn(wt_tag)]))
        self.reply("tst_06", "Sixteen.", "16.",
                   (None, lambda: [wt.cell[(0, 2)].animate.set_color(GOLD),
                                   Indicate(wt.cell[(0, 2)], color=GOLD, scale_factor=1.4)]))

        self.finish("S05_uses")

    # ============================================== 6. SUMMARY ==========

    def summary(self):
        self.begin("S06_summary", "Summary", "Summary", GOLD)

        rows = self.put(self.ticks(["Octal: base 8, digits 0 to 7",
                                    "1 octal digit = 3 bits",
                                    "Hexadecimal: base 16, digits 0 to 9 and A to F",
                                    "1 hex digit = 4 bits",
                                    "Both are compact ways to write binary"]), "full", BOARD_HIGH, "l")

        self.tell("sum_01", "Good. Let us summarise.")
        self.reply("sum_02", "Octal has base eight and digits zero to seven, and each digit equals three bits. "
                             "Hexadecimal has base sixteen and digits zero to nine and A to F, and each digit "
                             "equals four bits. They are compact ways to write binary.", "Reading from her notes",
                   ("Octal", lambda: [FadeIn(rows[0], shift=RIGHT * 0.2), self.light(P_OCT)]),
                   ("three", lambda: [FadeIn(rows[1], shift=RIGHT * 0.2), self.light(P_OCT3)]),
                   ("Hexadecimal", lambda: [FadeIn(rows[2], shift=RIGHT * 0.2), self.light(P_HEX)]),
                   ("four", lambda: [FadeIn(rows[3], shift=RIGHT * 0.2), self.light(P_HEX4)]),
                   ("compact", lambda: [FadeIn(rows[4], shift=RIGHT * 0.2), self.all_lit()]), who="A student")
        self.hush()
        self.play(Indicate(rows[1], color=GOLD, scale_factor=1.05), Indicate(rows[3], color=GOLD, scale_factor=1.05))
        self.finish("S06_summary")

    # ============================================== 7. NEXT =============

    def next_video(self):
        self.scene_start("S07_next", title="Next: Valid Digits, Ranges and Traps")
        four = VGroup(*[pill(s, MAIN, LABEL) for s in ("Decimal", "Binary", "Octal", "Hexadecimal")])
        four.arrange(RIGHT, buff=0.3)
        self.put(four, "full", BOARD_TOP)
        nxt = self.put(self.next_up("Next: Valid digits, ranges and traps"), "full", under=four, buff=0.7)
        self.tell("next_01", "Now that you know the four systems, you also need to know how to catch the traps that "
                             "examiners build around them. That is next.",
                  ("four", LaggedStart(*[FadeIn(p, shift=UP * 0.1) for p in four], lag_ratio=0.3)),
                  ("traps", FadeIn(nxt, scale=1.1)))
        self.undock()
        self.finish("S07_next")

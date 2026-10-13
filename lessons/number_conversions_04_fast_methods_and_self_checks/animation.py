"""
animation.py for the LMS video generator.

Course : C-CAT Computer Fundamentals
Lesson : Lesson 4 - Number System Conversions and Objective Practice
Video  : 06 Video 4 - Fast Methods and Self-Checks

Source script:
  CCAT_Computer_Fundamentals_Scripts_Lessons_1-5/PDF/Lesson 4 - Number System Conversions and Objective Practice/06 Video 4 - Fast Methods and Self-Checks.pdf
  The script has no speaker labels. Every line was labelled as below:
    TEACHER  spoken by the teacher: ``self.tell`` / ``self.ask`` (TEACHER_VOICE). Drives the board.
    STUDENT  spoken by a student: ``self.reply`` (STUDENT_VOICE). Every student answer is its own
             narration and appears as a card at the bottom right.
    STAGE    stage direction: not narrated, it becomes the visuals (or the name on the student card).
    BOARD    what the board shows: on screen, not spoken.
  Spoken text uses words ("one zero one one"); the cards and the board show digits ("1011").

Speaker split:
  01 TITLE   Fast Methods and Self-Checks: Choosing the Right Route and Catching Mistakes
  02 STAGE   The teacher writes the heading on the board: Which method is fastest?
  03 TEACHER In an objective paper, the right answer is not enough. You also need it quickly. Let us build a
             decision table. If the question says convert binary to octal, what do we use?
  04 STUDENT Grouping.
  05 TEACHER Convert decimal to hexadecimal?
  06 STUDENT Division by 16.
  07 TEACHER Convert hexadecimal to decimal?
  08 STUDENT Expansion.
  09 STAGE   The board shows the table.
  10 BOARD   FROM -> TO                  FASTEST METHOD
  11 BOARD   binary -> octal or hex      group bits in 3s or 4s
  12 BOARD   octal or hex -> binary      expand each digit into 3 or 4 bits
  13 BOARD   octal <-> hex               go through binary
  14 BOARD   any base -> decimal         expansion or double-and-add
  15 BOARD   decimal -> any base         repeated division
  16 BOARD   fraction part from decimal  repeated multiplication
  17 BOARD   small decimal -> binary     subtract powers of 2
  18 TEACHER The last row is new. Look at 200. Instead of dividing, we use the powers of 2 we memorised. What
             is the largest power of 2 that is not more than 200?
  19 STUDENT 128.
  20 TEACHER We write a 1 at 128, and we subtract. 200 minus 128 leaves 72. Is 64 not more than 72?
  21 STUDENT Yes.
  22 TEACHER A 1 at 64. 72 minus 64 leaves 8. What about 32 and 16?
  23 STUDENT They are too large, so 0 and 0.
  24 TEACHER Then 8 fits.
  25 STAGE   The board shows the pattern.
  26 BOARD   128  64  32  16   8   4   2   1
  27 BOARD    1    1   0   0   1   0   0   0    =  (11001000) in binary
  28 TEACHER 128 plus 64 plus 8 is 200. For numbers up to a few hundred, this method is the fastest of all,
             provided you know the powers of 2. For 100, we get 64 plus 32 plus 4, which is 1100100.
  29 TEACHER There are also numbers worth knowing by heart.
  30 BOARD   2^n - 1 is all ones:   15 = 1111    255 = 11111111
  31 BOARD   2^n is a one and zeros: 16 = 10000   256 = 100000000
  32 TEACHER So if a question asks for 255 in binary, you do not need any method at all.
  33 TEACHER Now the second half of the lesson: how do we know we are right? We do not have a calculator, and
             we cannot afford to redo the whole problem. We use three quick checks.
  34 STAGE   The teacher writes them.
  35 BOARD   CHECK 1  parity     last bit is 0 if the number is even
  36 BOARD   CHECK 2  size       n bits means the value is at least
  37 BOARD                       2^(n-1) and less than 2^n
  38 BOARD   CHECK 3  go back    convert the answer back; do you reach the start?
  39 TEACHER Let us apply them. Suppose someone says that 500 in binary is 11111010. Is that even or odd?
  40 STUDENT Even.
  41 TEACHER Is 500 even?
  42 STU+TEA Yes. So it passes the first check. How many bits does it have?
  43 STUDENT Eight.
  44 TEACHER And 2^8 is 256. The largest value for eight bits is 255. So 500 cannot fit in eight bits. The
             answer is wrong.
  45 TEACHER That is the size check at work. Now, the correct answer is nine bits, 111110100. From
             hexadecimal, 1F4. We expand 1, F, 4 into 0001, 1111, 0100, and drop the leading zeros, which
             gives 111110100. Check 3 confirms: 256 plus 128 plus 64 plus 32 plus 16 plus 4 is 500.
  46 STAGE   A student asks:
  47 STUDENT How do I use these checks when I am choosing from multiple-choice options?
  48 TEACHER Brilliantly. Often you do not need to compute the whole answer. If the number is odd, any binary
             option ending in 0 is wrong. If it is small, any option with too many bits is wrong. You can
             eliminate two options in a few seconds, and then do the full calculation only for the remaining
             two.
  49 STAGE   The board shows an example.
  50 BOARD   Which is (27) in binary?
  51 BOARD     A. 11010    B. 11011    C. 101101    D. 10111
  52 TEACHER 27 is odd, so A, which ends in 0, is eliminated. 27 is less than 32, so it needs at most five
             bits, so C, with six, is eliminated. Between B and D, 16 plus 8 plus 2 plus 1 is 27, which is
             11011.
  53 STUDENT So the answer is B.
  54 TEACHER Exactly.
  55 TEACHER Let us summarise.
  56 STAGE   A student reads from her notes.
  57 STUDENT Choose the method by the type of conversion. Memorise powers of 2. Check parity, size and
             reverse conversion. Use the checks to eliminate options in multiple-choice questions.
  58 STAGE   The board holds the final picture.
  59 BOARD   choose the route  ->  calculate  ->  check once  ->  move on
  60 TEACHER Now it is time to put all of this under pressure with questions in the style of the examination,
             and to learn from every mistake we make.
  61 STAGE   The board changes to:
  62 BOARD   NEXT: TIMED PRACTICE AND ERROR ANALYSIS

Notes:
  - Opening block ``open_01`` is not in the script: it is the usual breadcrumb opening
    (where we are, what came before, what this video covers).
  - Line 42 (STU+TEA) holds two speakers in one paragraph: "Yes." is the student's answer to
    "Is 500 even?", and "So it passes the first check. How many bits does it have?" is the teacher.
    It is split into a student block (ck_05) and two teacher blocks (ck_06, ck_07).
  - Line 44 ("And 2^8 is 256 ... The answer is wrong.") is labelled TEACHER: it follows the
    student's "Eight." and the scripts never give a student two lines in a row. If it should be
    the student, change ``self.tell("ck_09", ...)`` to ``self.reply``.
  - Long teacher lines are split into two narrations where a statement is followed by a question.
  - Every worked answer is computed and asserted in the data block: 200 = 128 + 64 + 8 = 11001000;
    100 = 64 + 32 + 4 = 1100100; 15, 255, 16, 256 in binary; 11111010 is 250, even, 8 bits;
    500 = 111110100 = 1F4 (base 16) = 256 + 128 + 64 + 32 + 16 + 4; 27 = 11011 (option B), with
    A = 26, C = 45, D = 23. The script's answers are all correct.

Style: 2D, three colours (blue main, grey support, gold highlight). No drawings and no raised
boxes are needed in this video. Pinned KEY IDEAS panel from the first scene to the end.

Section map:
  S00 Opening   S01 Which method is fastest   S02 Subtract powers of 2   S03 Known by heart
  S04 Three quick checks   S05 Applying the checks   S06 Checks on options   S07 Summary   S08 Next
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
CRUMB_VIDEO = "Video 4 of 5"
VIDEO_TITLE = "Fast Methods and Self-Checks"
BEFORE_LABEL = "Last video"
BEFORE_IDEA = "Binary, octal and hexadecimal by grouping bits"
TODAY_IDEA = "Choosing the fastest route, and checking an answer in seconds"

TEACHER_VOICE = "vijay"
STUDENT_VOICE = "kavya"        # students speak in their own voice, in their own blocks
TEACHER_PAUSE = 0.7            # silence after each teacher block (seconds), so speakers never run together
STUDENT_PAUSE = 0.6            # silence after each student block

IDEAS = [("Pick the method by the conversion", GOLD), ("Know the powers of 2", MAIN),
         ("Check 1: parity, the last bit", MAIN), ("Check 2: size, the number of bits", MAIN),
         ("Check 3: convert back", MAIN)]
P_PICK, P_POWERS, P_PARITY, P_SIZE, P_BACK = range(5)

POWERS = [128, 64, 32, 16, 8, 4, 2, 1]
ROUTES = [("Binary → octal or hex", "Group bits in 3s or 4s"),
          ("Octal or hex → binary", "Expand each digit into 3 or 4 bits"),
          ("Octal ↔ hex", "Go through binary"),
          ("Any base → decimal", "Expansion or double-and-add"),
          ("Decimal → any base", "Repeated division"),
          ("Fraction part from decimal", "Repeated multiplication"),
          ("Small decimal → binary", "Subtract powers of 2")]
OPTIONS = [("A.", "11010"), ("B.", "11011"), ("C.", "101101"), ("D.", "10111")]


def by_powers(n):
    """Bits of ``n`` found by subtracting powers of 2, largest first."""
    bits = []
    for p in POWERS:
        bits.append("1" if p <= n else "0")
        n -= p if p <= n else 0
    return bits


BITS200 = by_powers(200)

assert "".join(BITS200) == "11001000" == format(200, "b") and 200 - 128 == 72 and 72 - 64 == 8 and 128 + 64 + 8 == 200
assert 64 + 32 + 4 == 100 and format(100, "b") == "1100100"
assert [format(n, "b") for n in (15, 255, 16, 256)] == ["1111", "11111111", "10000", "100000000"]
assert int("11111010", 2) == 250 and len("11111010") == 8 and 2 ** 8 == 256 and 500 > 255
assert format(500, "b") == "111110100" and format(500, "X") == "1F4" and len(format(500, "b")) == 9
assert "".join(format(int(d, 16), "04b") for d in "1F4").lstrip("0") == "111110100"
assert 256 + 128 + 64 + 32 + 16 + 4 == 500 and 2 ** 8 <= 500 < 2 ** 9
assert [int(b, 2) for _, b in OPTIONS] == [26, 27, 45, 23] and 16 + 8 + 2 + 1 == 27 < 32


class FastMethodsSelfChecksVideo(LMSScene):
    lesson_title = "Fast Methods and Self-Checks"

    def construct(self):
        self.setup_board()
        self.opening("open_01", "Last time we converted between binary, octal and hexadecimal by grouping bits. In "
                                "this video we learn to pick the fastest method for each question, and to check an "
                                "answer in seconds.", "video")
        self.open_panel("Key ideas", IDEAS)
        self.fastest_method()
        self.powers_of_two()
        self.by_heart()
        self.three_checks()
        self.apply_checks()
        self.on_options()
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

    # ===================================== 1. WHICH METHOD IS FASTEST ===

    def fastest_method(self):
        self.begin("S01_fastest", "Which Method Is Fastest", "Which method is fastest?")

        mini = table([["Binary → octal", "Grouping"], ["Decimal → hexadecimal", "Division by 16"],
                      ["Hexadecimal → decimal", "Expansion"]], [3.4, 2.3], row_h=0.6, size=SMALL, head=False,
                     font=FONT)
        self.put(mini, "left", BOARD_TOP)
        mini.col(1).set_color(GOLD)
        tb = table([["From → to", "Fastest method"]] + [list(r) for r in ROUTES], [4.3, 5.2], row_h=0.45,
                   size=SMALL, font=FONT)
        self.put(tb, "wide", BOARD_HIGH - 0.05)
        tb.col(1).set_color(MAIN)

        def answer(r):
            return [FadeIn(mini.cell[(r, 1)], shift=LEFT * 0.1)]

        self.tell("fm_01", "In an objective paper, the right answer is not enough. You also need it quickly. Let us "
                           "build a decision table.")
        self.ask("fm_02", "If the question says convert binary to octal, what do we use?",
                 "Convert binary to octal: what do we use?", ("binary", FadeIn(mini.cell[(0, 0)], shift=UP * 0.1)))
        self.reply("fm_03", "Grouping.", None, (None, answer(0)))
        self.ask("fm_04", "Convert decimal to hexadecimal?", None,
                 ("decimal", FadeIn(mini.cell[(1, 0)], shift=UP * 0.1)))
        self.reply("fm_05", "Division by sixteen.", "Division by 16.", (None, answer(1)))
        self.ask("fm_06", "Convert hexadecimal to decimal?", None,
                 ("hexadecimal", FadeIn(mini.cell[(2, 0)], shift=UP * 0.1)))
        self.reply("fm_07", "Expansion.", None, (None, answer(2)))
        self.hush()
        self.drop_q()
        self.play(FadeOut(mini), run_time=0.4)
        self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.15) for r in tb.rows], lag_ratio=0.35), run_time=3.2)
        self.tell("fm_08", "The last row is new.",
                  ("last", lambda: [tb.rows[7].animate.set_color(GOLD)]), (None, lambda: self.add_row(P_PICK)))

        self.finish("S01_fastest")

    # ===================================== 2. SUBTRACT POWERS OF 2 ======

    def powers_of_two(self):
        self.begin("S02_powers", "Subtract Powers of 2", "Small numbers: subtract powers of 2")

        tb = table([[str(p) for p in POWERS], BITS200], [0.85] * 8, row_h=0.6, head=False)
        self.put(tb, "full", BOARD_TOP)
        tb.rows[0].set_color(GOLD)
        steps = stack(mono("200 − 128 = 72", SMALL, INK), mono(" 72 −  64 =  8", SMALL, INK),
                      mono("  8 −   8 =  0", SMALL, INK), buff=0.2)
        self.put(steps, "left", under=tb, buff=0.4, align="l")
        result = self.put(mono("200 = 11001000 in binary", SMALL, GOLD), "left", under=steps, buff=0.35, align="l")
        check = stack(mono("128 + 64 + 8 = 200", SMALL, MAIN), mono("100 = 64 + 32 + 4 = 1100100", SMALL, MAIN),
                      buff=0.2)
        self.put(check, "left", under=tb, buff=0.4, align="l")

        def bit(c):
            return FadeIn(tb.cell[(1, c)], scale=1.4)

        def weight(c):
            return Indicate(tb.cell[(0, c)], color=GOLD, scale_factor=1.4)

        self.ask("sp_01", "Look at two hundred. Instead of dividing, we use the powers of two we memorised. What is "
                          "the largest power of two that is not more than two hundred?",
                 "What is the largest power of 2 that is not more than 200?",
                 ("powers", LaggedStart(*[FadeIn(t, shift=DOWN * 0.1) for t in tb.rows[0]], lag_ratio=0.15)))
        self.reply("sp_02", "One hundred and twenty-eight.", "128.", (None, weight(0)))
        self.tell("sp_03", "We write a one at one hundred and twenty-eight, and we subtract. Two hundred minus one "
                           "hundred and twenty-eight leaves seventy-two.",
                  ("write", bit(0)), ("subtract", FadeIn(steps[0], shift=RIGHT * 0.15)))
        self.ask("sp_04", "Is sixty-four not more than seventy-two?", "Is 64 not more than 72?", (None, weight(1)))
        self.reply("sp_05", "Yes.")
        self.tell("sp_06", "A one at sixty-four. Seventy-two minus sixty-four leaves eight.",
                  ("one", bit(1)), ("leaves", FadeIn(steps[1], shift=RIGHT * 0.15)))
        self.ask("sp_07", "What about thirty-two and sixteen?", "What about 32 and 16?",
                 (None, lambda: [weight(2), weight(3)]))
        self.reply("sp_08", "They are too large, so zero and zero.", "They are too large, so 0 and 0.",
                   ("zero", bit(2)), (("zero", 2), bit(3)))
        self.tell("sp_09", "Then eight fits.", ("eight", bit(4)), (None, FadeIn(steps[2], shift=RIGHT * 0.15)))
        self.play(LaggedStart(*[bit(c) for c in (5, 6, 7)], lag_ratio=0.3), run_time=1.0)
        self.play(FadeIn(result, shift=UP * 0.1), run_time=0.6)
        self.drop_q()
        self.tell("sp_10", "One hundred and twenty-eight plus sixty-four plus eight is two hundred. For numbers up "
                           "to a few hundred, this method is the fastest of all, provided you know the powers of "
                           "two. For one hundred, we get sixty-four plus thirty-two plus four, which is one one "
                           "zero zero one zero zero.",
                  ("plus", lambda: [FadeOut(VGroup(steps, result)), FadeIn(check[0], shift=RIGHT * 0.15)]),
                  ("fastest", lambda: self.add_row(P_POWERS)), ("get", FadeIn(check[1], shift=RIGHT * 0.15)))

        self.finish("S02_powers")

    # ===================================== 3. KNOWN BY HEART ============

    def by_heart(self):
        self.begin("S03_by_heart", "Known by Heart", "Numbers worth knowing by heart")

        tb = table([["2ⁿ − 1 is all ones", "15 = 1111", "255 = 11111111"],
                    ["2ⁿ is a one and zeros", "16 = 10000", "256 = 100000000"]], [3.9, 2.3, 3.3], row_h=0.7,
                   head=False, font=FONT)
        self.put(tb, "full", BOARD_HIGH - 0.1)
        tb.col(0).set_color(MAIN)
        none = self.put(self.note("255 in binary: eight ones, no method needed", GOLD), "left", under=tb, buff=0.5)

        self.tell("bh_01", "There are also numbers worth knowing by heart.",
                  ("numbers", LaggedStart(FadeIn(tb.rows[0], shift=RIGHT * 0.15),
                                          FadeIn(tb.rows[1], shift=RIGHT * 0.15), lag_ratio=0.6, run_time=1.6)))
        self.tell("bh_02", "So if a question asks for two hundred and fifty-five in binary, you do not need any "
                           "method at all.",
                  ("binary", lambda: [tb.cell[(0, 2)].animate.set_color(GOLD),
                                      Indicate(tb.cell[(0, 2)], color=GOLD, scale_factor=1.08)]),
                  ("method", FadeIn(none, shift=UP * 0.1)), (None, lambda: self.light(P_POWERS)))

        self.finish("S03_by_heart")

    # ===================================== 4. THREE QUICK CHECKS ========

    def three_checks(self):
        self.begin("S04_checks", "Three Quick Checks", "How do we know we are right?")

        tb = table([["Check 1", "Parity", "The last bit is 0 if the number is even"],
                    ["Check 2", "Size", "n bits: at least 2ⁿ⁻¹ and less than 2ⁿ"],
                    ["Check 3", "Go back", "Convert the answer back to the start"]], [1.6, 1.7, 6.2],
                   row_h=0.75, size=SMALL, head=False, font=FONT)
        self.put(tb, "wide", BOARD_HIGH - 0.2)
        tb.col(0).set_color(MUTED)
        tb.col(1).set_color(GOLD)

        self.tell("ck_01", "Now the second half of the lesson: how do we know we are right? We do not have a "
                           "calculator, and we cannot afford to redo the whole problem. We use three quick checks.",
                  ("three", FadeIn(tb.rows[0], shift=RIGHT * 0.15)), (None, lambda: self.add_row(P_PARITY)),
                  (None, FadeIn(tb.rows[1], shift=RIGHT * 0.15)), (None, lambda: self.add_row(P_SIZE)),
                  (None, FadeIn(tb.rows[2], shift=RIGHT * 0.15)), (None, lambda: self.add_row(P_BACK)))

        self.finish("S04_checks")

    # ===================================== 5. APPLYING THE CHECKS =======

    def apply_checks(self):
        self.begin("S05_apply", "Applying the Checks", "Is 500 = 11111010 in binary?")

        lines = stack(mono("Claim  : 500 = 11111010", SMALL, MAIN),
                      mono("Check 1: ends in 0, even: passes", SMALL, INK),
                      mono("Check 2: 8 bits hold at most 255", SMALL, INK),
                      mono("         500 cannot fit: WRONG", SMALL, GOLD),
                      mono("Correct: 1F4 → 0001 1111 0100", SMALL, INK),
                      mono("         → 111110100 (9 bits)", SMALL, GOLD),
                      mono("Check 3: 256+128+64+32+16+4 = 500", SMALL, INK), buff=0.2)
        self.put(lines, "left", BOARD_TOP, "l")

        def line(k):
            return FadeIn(lines[k], shift=RIGHT * 0.15)

        self.play(line(0), run_time=0.6)
        self.ask("ck_02", "Let us apply them. Suppose someone says that five hundred in binary is one one one one "
                          "one zero one zero. Is that even or odd?",
                 "Someone says 500 in binary is 11111010. Is that even or odd?")
        self.reply("ck_03", "Even.")
        self.ask("ck_04", "Is five hundred even?", "Is 500 even?")
        self.reply("ck_05", "Yes.")
        self.tell("ck_06", "So it passes the first check.",
                  ("passes", line(1)), (None, lambda: self.light(P_PARITY)))
        self.ask("ck_07", "How many bits does it have?", "How many bits does 11111010 have?")
        self.reply("ck_08", "Eight.", "8.")
        self.tell("ck_09", "And two to the power eight is two hundred and fifty-six. The largest value for eight "
                           "bits is two hundred and fifty-five. So five hundred cannot fit in eight bits. The "
                           "answer is wrong.",
                  ("largest", line(2)), ("cannot", line(3)), (None, lambda: self.light(P_SIZE)))
        self.tell("ck_10", "That is the size check at work. Now, the correct answer is nine bits, one one one one "
                           "one zero one zero zero. From hexadecimal, one F four. We expand one, F, four into zero "
                           "zero zero one, one one one one, zero one zero zero, and drop the leading zeros, which "
                           "gives one one one one one zero one zero zero.",
                  ("expand", line(4)), ("drop", line(5)))
        self.tell("ck_11", "Check three confirms: two hundred and fifty-six plus one hundred and twenty-eight plus "
                           "sixty-four plus thirty-two plus sixteen plus four is five hundred.",
                  ("confirms", line(6)), (None, lambda: self.light(P_BACK)))

        self.finish("S05_apply")

    # ===================================== 6. CHECKS ON OPTIONS =========

    def on_options(self):
        self.begin("S06_options", "Checks on Options", "Using the checks on options")

        tips = stack(self.note("Odd number: options ending in 0 are wrong", MAIN),
                     self.note("Small number: options with too many bits are wrong", MAIN), buff=0.25)
        self.put(tips, "left", BOARD_HIGH - 0.1, "l")
        stem = self.put(text("Which is 27 in binary?", LABEL, INK, BOLD), "left", BOARD_HIGH - 0.1, "l")
        tb = table([[k, b, r] for (k, b), r in zip(OPTIONS, ["ends in 0", "", "6 bits", "= 23"])], [0.6, 1.7, 2.3],
                   row_h=0.5, head=False)
        self.put(tb, "left", under=stem, buff=0.3, align="l")
        tb.col(2).set_color(MUTED)
        work = self.put(mono("16 + 8 + 2 + 1 = 27 = 11011", SMALL, GOLD), "left", under=tb, buff=0.35, align="l")

        def out(r):
            return [tb.cell[(r, 0)].animate.set_color(MUTED), tb.cell[(r, 1)].animate.set_color(MUTED),
                    FadeIn(tb.cell[(r, 2)], shift=LEFT * 0.1)]

        self.reply("mc_01", "How do I use these checks when I am choosing from multiple-choice options?",
                   "How do I use these checks on the options?", who="A student asks")
        self.tell("mc_02", "Brilliantly. Often you do not need to compute the whole answer. If the number is odd, "
                           "any binary option ending in zero is wrong. If it is small, any option with too many "
                           "bits is wrong. You can eliminate two options in a few seconds, and then do the full "
                           "calculation only for the remaining two.",
                  ("odd", FadeIn(tips[0], shift=UP * 0.1)), ("small", FadeIn(tips[1], shift=UP * 0.1)))
        self.play(FadeOut(tips), run_time=0.4)
        self.play(FadeIn(stem), LaggedStart(*[AnimationGroup(FadeIn(tb.cell[(r, 0)]), FadeIn(tb.cell[(r, 1)]))
                                              for r in range(4)], lag_ratio=0.3), run_time=1.6)
        self.tell("mc_03", "Twenty-seven is odd, so A, which ends in zero, is eliminated. Twenty-seven is less than "
                           "thirty-two, so it needs at most five bits, so C, with six, is eliminated. Between B and "
                           "D, sixteen plus eight plus two plus one is twenty-seven, which is one one zero one one.",
                  ("odd", lambda: out(0)), ("six", lambda: out(2)), ("Between", FadeIn(work, shift=UP * 0.1)),
                  (("which", 2), lambda: out(3)))
        self.reply("mc_04", "So the answer is B.", None,
                   (None, lambda: [tb.cell[(1, 0)].animate.set_color(GOLD), tb.cell[(1, 1)].animate.set_color(GOLD)]))
        self.tell("mc_05", "Exactly.", (None, Indicate(tb.cell[(1, 1)], color=GOLD, scale_factor=1.2)))

        self.finish("S06_options")

    # ============================================== 7. SUMMARY ==========

    def summary(self):
        self.begin("S07_summary", "Summary", "Summary", GOLD)

        rows = self.put(self.ticks(["Choose the method by the type of conversion",
                                    "Memorise the powers of 2",
                                    "Check parity, size and reverse conversion",
                                    "Use the checks to eliminate options"]), "full", BOARD_HIGH, "l")

        self.tell("sum_01", "Let us summarise.")
        self.reply("sum_02", "Choose the method by the type of conversion. Memorise powers of two. Check parity, "
                             "size and reverse conversion. Use the checks to eliminate options in multiple-choice "
                             "questions.", "Reading from her notes",
                   ("Choose", lambda: [FadeIn(rows[0], shift=RIGHT * 0.2), self.light(P_PICK)]),
                   ("Memorise", lambda: [FadeIn(rows[1], shift=RIGHT * 0.2), self.light(P_POWERS)]),
                   ("Check", lambda: [FadeIn(rows[2], shift=RIGHT * 0.2), self.light(P_PARITY, P_SIZE, P_BACK)]),
                   ("eliminate", FadeIn(rows[3], shift=RIGHT * 0.2)), who="A student")
        self.hush()
        self.play(*self.all_lit())
        self.finish("S07_summary")

    # ============================================== 8. NEXT =============

    def next_video(self):
        self.scene_start("S08_next", title="Next: Timed Practice and Error Analysis")
        chain = VGroup()
        for k, s in enumerate(["Choose the route", "Calculate", "Check once", "Move on"]):
            if k:
                chain.add(text("→", LABEL, MUTED, BOLD))
            chain.add(pill(s, MAIN, SMALL))
        chain.arrange(RIGHT, buff=0.2)
        self.put(chain, "full", BOARD_TOP)
        nxt = self.put(self.next_up("Next: Timed practice and error analysis"), "full", under=chain, buff=0.7)
        self.tell("next_01", "Now it is time to put all of this under pressure with questions in the style of the "
                             "examination, and to learn from every mistake we make.",
                  ("time", LaggedStart(*[FadeIn(p, shift=UP * 0.1) for p in chain], lag_ratio=0.25)),
                  ("examination", FadeIn(nxt, scale=1.1)))
        self.undock()
        self.finish("S08_next")

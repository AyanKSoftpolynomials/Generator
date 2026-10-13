"""
animation.py for the LMS video generator.

Course : C-CAT Computer Fundamentals
Lesson : Lesson 4 - Number System Conversions and Objective Practice
Video  : 07 Video 5 - Timed Practice and Error Analysis

Source script:
  CCAT_Computer_Fundamentals_Scripts_Lessons_1-5/PDF/Lesson 4 - Number System Conversions and Objective Practice/07 Video 5 - Timed Practice and Error Analysis.pdf
  The script has no speaker labels. Every line was labelled as below:
    TEACHER  spoken by the teacher: ``self.tell`` / ``self.ask`` (TEACHER_VOICE). Drives the board.
    STUDENT  spoken by a student: ``self.reply`` (STUDENT_VOICE). Every student answer is its own
             narration and appears as a card at the bottom right.
    STAGE    stage direction: not narrated, it becomes the visuals (or the name on the student card).
    BOARD    what the board shows: on screen, not spoken.
  Spoken text uses words ("one zero one one"); the cards and the board show digits ("1011").

Speaker split:
  01 TITLE   Timed Objective Practice and Error Analysis
  02 STAGE   The teacher puts a stopwatch on the table.
  03 TEACHER Today is a working session. I will give you a question, and you will solve it as you would in
             the examination. After each question we will discuss the quickest route and the trap. Ready?
  04 STAGE   The first question appears on the board.
  05 BOARD   Q1.  (101101) in binary  =  ?  in decimal
  06 BOARD        A. 43    B. 45    C. 47    D. 51
  07 TEACHER We want a quick method. Double-and-add: 1, 2, 5, 11, 22, 45. The answer is B, 45. Now the trap.
             The wrong options are what you would get from a single slip in one weight, so a five-second re-
             check with the weights written out is worth it.
  08 TEACHER Next.
  09 BOARD   Q2.  (65) in octal  =  ?  in decimal
  10 BOARD        A. 41    B. 51    C. 53    D. 65
  11 TEACHER 6 times 8 plus 5. 48 plus 5 is 53, option C. Notice that option D, 65, is tempting for anyone
             who forgets to convert at all. Interesting thing: 53 is also the value of 110101 in binary, from
             the first video.
  12 TEACHER Next.
  13 BOARD   Q3.  (75) in decimal  =  ?  in binary
  14 BOARD        A. 1001011    B. 1101001    C. 1001101    D. 1010011
  15 TEACHER 75 is odd, so every option ends in 1. That check does not help. Size: 64 is not more than 75, so
             we need seven bits. All options have seven bits. We must calculate. 64, then 75 minus 64 is 11.
             8, then 3. 2 and 1. Writing the positions: 64 is 1, 32 is 0, 16 is 0, 8 is 1, 4 is 0, 2 is 1, 1
             is 1. That gives 1001011, option A.
  16 STAGE   The teacher glances at the stopwatch.
  17 TEACHER That took me under a minute. Your target for a simple conversion is about a minute.
  18 TEACHER Next.
  19 BOARD   Q4.  (111101) in binary  =  ?  in hexadecimal
  20 BOARD        A. 2D    B. 3D    C. 3E    D. 6D
  21 TEACHER No arithmetic is needed. Group in fours from the right and pad on the left. The number has six
             bits. The right group is 1101, which is D. The left group is 11, padded to 0011, which is 3. The
             answer is 3D, option B. If you grouped from the left you would get 1111 and 01, which gives a
             wrong answer.
  22 TEACHER Next.
  23 BOARD   Q5.  (3E) in hexadecimal  =  ?  in binary
  24 BOARD        A. 111110    B. 111100    C. 101110    D. 111011
  25 TEACHER 3 is 0011 and E is 1110, so the full pattern is 00111110. Dropping the leading zeros gives
             111110, option A. You may drop zeros only at the very left end. Every digit in the middle of a
             number must keep its full four bits.
  26 TEACHER Next.
  27 BOARD   Q6.  Which is the greatest?
  28 BOARD        A. (1F) in hex    B. (35) in octal    C. (11010) in binary
  29 TEACHER Here the trap is in comparison. Never compare numbers in different bases by looking at them.
             Bring all to decimal. 1F is 31. 35 in octal is 3 times 8 plus 5, which is 29. 11010 in binary is
             16 plus 8 plus 2, which is 26. So 1F is greatest, option A.
  30 STAGE   A student asks:
  31 STUDENT How do we handle the time?
  32 TEACHER Do not spend more than a minute on one question. If a question is taking longer, mark your best
             guess, move on and return if you have time.
  33 TEACHER Now, the second half of today's work. When you make a mistake, we do not just correct it. We
             classify it. Where did the error come from?
  34 STAGE   The teacher lists the four types.
  35 BOARD   CONCEPT ERROR       wrong method or rule
  36 BOARD                       (reading remainders from the top)
  37 BOARD   CALCULATION ERROR   right method, arithmetic slip
  38 BOARD                       (6 x 8 + 5 written as 51)
  39 BOARD   READING ERROR       misread the question
  40 BOARD                       (missed the base, or the direction asked)
  41 BOARD   TIME-PRESSURE ERROR knew it, rushed it, did not check
  42 TEACHER Each one needs a different cure. A concept error needs you to go back to the video and redo the
             method. A calculation error needs a slower, tidier layout, and a check. A reading error needs
             you to underline the bases and the direction of the conversion before you start. And a time-
             pressure error needs the habit of one quick check.
  43 TEACHER Let us look at how to keep the log. For each mistake write the question, the type of error and
             one sentence on what you will do differently.
  44 STAGE   The board shows a sample entry.
  45 BOARD   Q4 | READING | wrote answer for hex -> binary, not binary -> hex
  46 BOARD      |         | next time: underline FROM and TO before starting
  47 TEACHER After a week, count how many mistakes you have of each kind. The largest count is where you will
             gain the most marks.
  48 TEACHER Let me ask you to summarise today.
  49 STAGE   A student reads from her notes.
  50 STUDENT Choose the method, calculate, check once and move on. Never compare numbers in different bases
             without converting. Aim for about a minute for each simple conversion. Classify every mistake as
             concept, calculation, reading or time-pressure, and fix the cause rather than just the answer.
  51 TEACHER Exactly. You now have every tool for the number systems. But numbers are not the only things a
             computer stores. Letters, symbols, even the characters on this board have to be stored as bits.
             How?
  52 STAGE   The board changes to:
  53 BOARD   NEXT LESSON: DATA REPRESENTATION AND COMPUTER CODES

Notes:
  - Opening block ``open_01`` is not in the script: it is the usual breadcrumb opening
    (where we are, what came before, what this video covers).
  - This script is mostly the teacher working through questions; the two student lines
    (the time question and the summary) are their own blocks in the student voice.
  - Long teacher lines are split into two narrations where the board changes in between.
  - Every answer is computed and asserted in the data block: Q1 101101 (base 2) = 45, option B;
    Q2 65 (base 8) = 53, option C; Q3 75 = 1001011, option A; Q4 111101 (base 2) = 3D, option B;
    Q5 3E (base 16) = 111110, option A; Q6 1F = 31, 35 (base 8) = 29, 11010 (base 2) = 26, so
    option A is the greatest. The script's answer key is correct for all six.

Style: 2D, three colours (blue main, grey support, gold highlight). One drawn stopwatch (the
script is built around it: timing each question). No raised boxes are needed in this video.
Pinned KEY IDEAS panel from the first scene to the end.

Section map:
  S00 Opening   S01 A working session   S02-S07 Questions 1 to 6   S08 Handling the time
  S09 Classify every mistake   S10 The error log   S11 Summary   S12 Next
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
CRUMB_VIDEO = "Video 5 of 5"
VIDEO_TITLE = "Timed Practice and Error Analysis"
BEFORE_LABEL = "Last video"
BEFORE_IDEA = "Choose the route, calculate, check once, move on"
TODAY_IDEA = "Six timed questions, then how to learn from every mistake"

TEACHER_VOICE = "vijay"
STUDENT_VOICE = "kavya"        # students speak in their own voice, in their own blocks
TEACHER_PAUSE = 0.7            # silence after each teacher block (seconds), so speakers never run together
STUDENT_PAUSE = 0.6            # silence after each student block

IDEAS = [("Choose, calculate, check once, move on", GOLD), ("About a minute per conversion", MAIN),
         ("Never compare across bases by look", MAIN), ("Classify every mistake", MAIN),
         ("Fix the cause, not just the answer", MAIN)]
P_FLOW, P_MINUTE, P_COMPARE, P_CLASSIFY, P_CAUSE = range(5)

Q1 = [("A", "43"), ("B", "45"), ("C", "47"), ("D", "51")]
Q2 = [("A", "41"), ("B", "51"), ("C", "53"), ("D", "65")]
Q3 = [("A", "1001011"), ("B", "1101001"), ("C", "1001101"), ("D", "1010011")]
Q4 = [("A", "2D"), ("B", "3D"), ("C", "3E"), ("D", "6D")]
Q5 = [("A", "111110"), ("B", "111100"), ("C", "101110"), ("D", "111011")]
Q6 = [("A", "1F (hex)"), ("B", "35 (octal)"), ("C", "11010 (binary)")]
BITS75 = list(format(75, "07b"))


def horner(digits, base):
    total, steps = 0, []
    for d in digits:
        total = total * base + d
        steps.append(total)
    return steps


assert horner([1, 0, 1, 1, 0, 1], 2) == [1, 2, 5, 11, 22, 45] and dict(Q1)["B"] == "45" and 32 + 8 + 4 + 1 == 45
assert 6 * 8 + 5 == 48 + 5 == 53 == int("65", 8) == int("110101", 2) and dict(Q2)["C"] == "53"
assert format(75, "b") == "1001011" == dict(Q3)["A"] and 75 - 64 == 11 and 11 - 8 == 3 and 3 - 2 == 1
assert all(b.endswith("1") and len(b) == 7 for _, b in Q3) and [int(b, 2) for _, b in Q3] == [75, 105, 77, 83]
assert format(int("111101", 2), "X") == "3D" == dict(Q4)["B"] and int("0011", 2) == 3 and int("1101", 2) == 13
assert format(0x3, "04b") + format(0xE, "04b") == "00111110" and "00111110".lstrip("0") == "111110" == dict(Q5)["A"]
assert (int("1F", 16), int("35", 8), int("11010", 2)) == (31, 29, 26) and 3 * 8 + 5 == 29 and 16 + 8 + 2 == 26


class TimedPracticeErrorAnalysisVideo(LMSScene):
    lesson_title = "Timed Practice and Error Analysis"

    def construct(self):
        self.setup_board()
        self.opening("open_01", "Last time we learned to choose the fastest method and to check an answer in "
                                "seconds. In this last video of the lesson, we practise against the clock, and we "
                                "learn from every mistake.", "video")
        self.open_panel("Key ideas", IDEAS)
        self.working_session()
        self.question_one()
        self.question_two()
        self.question_three()
        self.question_four()
        self.question_five()
        self.question_six()
        self.the_time()
        self.classify()
        self.error_log()
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

    # ------------------------------------------------------ this video --

    def stopwatch(self):
        """The teacher's stopwatch: the one drawing this video needs."""
        face = Circle(radius=0.5, stroke_color=MAIN, stroke_width=4, fill_color=PANEL, fill_opacity=1)
        crown = Rectangle(width=0.18, height=0.16, stroke_width=0, fill_color=MAIN, fill_opacity=1)
        crown.next_to(face, UP, buff=0)
        hand = Line(ORIGIN, UP * 0.36, color=GOLD, stroke_width=5)
        g = VGroup(crown, face, hand)
        g.face, g.hand = face, hand
        return g

    def tick(self, watch, turns=1.0, run_time=2.0):
        return Rotate(watch.hand, -TAU * turns, about_point=watch.face.get_center(), run_time=run_time,
                      rate_func=linear)

    def question(self, number, stem, options):
        """A question as it appears in the paper: number, wording, options in one row."""
        lo, hi, _ = self.zone("wide")
        head = VGroup(text(f"Q{number}", LABEL, GOLD, BOLD),
                      fitted_text(stem, hi - lo - 1.4, LABEL, INK, BOLD, max_lines=1, font=MONO)).arrange(RIGHT,
                                                                                                         buff=0.35)
        opts = table([[f"{k}. {v}" for k, v in options]], [(hi - lo - 0.3) / len(options)] * len(options),
                     head=False, font=FONT if len(options) == 3 else MONO)
        g = stack(head, opts, buff=0.35)
        self.put(g, "wide", BOARD_HIGH - 0.05, "l")
        g.options = [opts.cell[(0, c)] for c in range(len(options))]
        return g

    def show_question(self, q):
        self.play(FadeIn(q[0], shift=UP * 0.1), run_time=0.6)
        self.play(LaggedStart(*[FadeIn(o, shift=UP * 0.1) for o in q.options], lag_ratio=0.25), run_time=1.0)

    def pick(self, q, k):
        """The correct option turns gold; the others go grey."""
        return [o.animate.set_color(GOLD if i == k else MUTED) for i, o in enumerate(q.options)] + [
            Indicate(q.options[k], color=GOLD, scale_factor=1.15)]

    def working(self, q, *lines, buff=0.45):
        """Working lines under the question."""
        return self.put(stack(*[mono(s, SMALL, INK) for s in lines], buff=0.22), "wide", under=q, buff=buff,
                        align="l")

    # ===================================== 1. A WORKING SESSION =========

    def working_session(self):
        self.begin("S01_session", "A Working Session", "A working session")

        watch = self.put(self.stopwatch(), "wide", BOARD_TOP)
        chain = VGroup()
        for k, s in enumerate(["A question", "The quickest route", "The trap"]):
            if k:
                chain.add(text("→", LABEL, MUTED, BOLD))
            chain.add(pill(s, GOLD if k == 2 else MAIN, LABEL))
        chain.arrange(RIGHT, buff=0.25)
        self.put(chain, "wide", under=watch, buff=0.5)

        self.play(FadeIn(watch, shift=DOWN * 0.2), run_time=0.6)
        self.tell("in_01", "Today is a working session. I will give you a question, and you will solve it as you "
                           "would in the examination. After each question we will discuss the quickest route and "
                           "the trap.",
                  ("question", FadeIn(chain[0], shift=UP * 0.1)),
                  ("quickest", lambda: [FadeIn(chain[1]), FadeIn(chain[2], shift=UP * 0.1)]),
                  ("trap", lambda: [FadeIn(chain[3]), FadeIn(chain[4], shift=UP * 0.1)]))
        self.ask("in_02", "Ready?", None, (None, lambda: self.tick(watch, 1.0, 1.2)))

        self.finish("S01_session")

    # ===================================== 2. QUESTION 1 ================

    def question_one(self):
        self.scene_start("S02_q1", title="Question 1")
        q = self.question(1, "101101 in binary = ? in decimal", Q1)
        work = self.working(q, "Double-and-add: 1 → 2 → 5 → 11 → 22 → 45")
        trap = self.put(self.note("Trap: one slipped weight gives a wrong option", GOLD, "wide"), "wide",
                        under=work, buff=0.4, align="l")
        check = self.put(mono("Re-check: 32 + 8 + 4 + 1 = 45", SMALL, MAIN), "wide", under=trap, buff=0.3, align="l")

        self.show_question(q)
        self.tell("q1_01", "We want a quick method. Double-and-add: one, two, five, eleven, twenty-two, forty-five. "
                           "The answer is B, forty-five.",
                  ("quick", FadeIn(work, shift=RIGHT * 0.15)), ("answer", lambda: self.pick(q, 1)))
        self.tell("q1_02", "Now the trap. The wrong options are what you would get from a single slip in one "
                           "weight, so a five-second re-check with the weights written out is worth it.",
                  ("trap", FadeIn(trap, shift=UP * 0.1)), ("weights", FadeIn(check, shift=UP * 0.1)),
                  (None, lambda: self.add_row(P_FLOW)))
        self.finish("S02_q1")

    # ===================================== 3. QUESTION 2 ================

    def question_two(self):
        self.scene_start("S03_q2", title="Question 2")
        q = self.question(2, "65 in octal = ? in decimal", Q2)
        work = self.working(q, "6 × 8 + 5 = 48 + 5 = 53")
        trap = self.put(self.note("Trap: D is the number with no conversion at all", GOLD, "wide"), "wide",
                        under=work, buff=0.4, align="l")
        also = self.put(mono("53 is also 110101 in binary", SMALL, MAIN), "wide", under=trap, buff=0.3, align="l")

        self.tell("q2_01", "Next.", (None, lambda: self.show_question(q)))
        self.tell("q2_02", "Six times eight plus five. Forty-eight plus five is fifty-three, option C. Notice that "
                           "option D, sixty-five, is tempting for anyone who forgets to convert at all. Interesting "
                           "thing: fifty-three is also the value of one one zero one zero one in binary, from the "
                           "first video.",
                  ("times", FadeIn(work, shift=RIGHT * 0.15)), ("option", lambda: self.pick(q, 2)),
                  ("tempting", FadeIn(trap, shift=UP * 0.1)), ("also", FadeIn(also, shift=UP * 0.1)))
        self.finish("S03_q2")

    # ===================================== 4. QUESTION 3 ================

    def question_three(self):
        self.scene_start("S04_q3", title="Question 3")
        q = self.question(3, "75 in decimal = ? in binary", Q3)
        checks = self.working(q, "Parity: 75 is odd, every option ends in 1", "Size  : every option has 7 bits")
        must = self.put(self.note("The checks do not help: calculate", GOLD, "wide"), "wide", under=checks,
                        buff=0.35, align="l")
        tb = table([["64", "32", "16", "8", "4", "2", "1"], BITS75], [0.85] * 7, row_h=0.55, head=False)
        self.put(tb, "wide", under=q, buff=0.5, align="l")
        tb.rows[0].set_color(GOLD)
        steps = mono("75 − 64 = 11,  11 − 8 = 3,  3 − 2 = 1", SMALL, MAIN)
        self.put(steps, "wide", under=tb, buff=0.35, align="l")
        watch = self.stopwatch().next_to(tb, RIGHT, buff=1.0)
        minute = self.put(self.note("Target: about a minute for a simple conversion", GOLD, "wide"), "wide",
                          under=steps, buff=0.4, align="l")

        self.tell("q3_01", "Next.", (None, lambda: self.show_question(q)))
        self.tell("q3_02", "Seventy-five is odd, so every option ends in one. That check does not help. Size: "
                           "sixty-four is not more than seventy-five, so we need seven bits. All options have seven "
                           "bits. We must calculate.",
                  ("odd", FadeIn(checks[0], shift=RIGHT * 0.15)), ("Size", FadeIn(checks[1], shift=RIGHT * 0.15)),
                  ("calculate", FadeIn(must, shift=UP * 0.1)))
        self.play(FadeOut(VGroup(checks, must)), run_time=0.4)
        self.tell("q3_03", "Sixty-four, then seventy-five minus sixty-four is eleven. Eight, then three. Two and "
                           "one. Writing the positions: sixty-four is one, thirty-two is zero, sixteen is zero, "
                           "eight is one, four is zero, two is one, one is one. That gives one zero zero one zero "
                           "one one, option A.",
                  (None, LaggedStart(*[FadeIn(t, shift=DOWN * 0.1) for t in tb.rows[0]], lag_ratio=0.15)),
                  ("minus", FadeIn(steps, shift=UP * 0.1)),
                  ("Writing", LaggedStart(*[FadeIn(t, scale=1.4) for t in tb.rows[1]], lag_ratio=0.9, run_time=6.0)),
                  ("option", lambda: self.pick(q, 0)))
        self.tell("q3_04", "That took me under a minute. Your target for a simple conversion is about a minute.",
                  (None, FadeIn(watch, shift=LEFT * 0.2)), (None, lambda: self.tick(watch, 1.0, 1.5)),
                  ("target", FadeIn(minute, shift=UP * 0.1)), (None, lambda: self.add_row(P_MINUTE)))
        self.finish("S04_q3")

    # ===================================== 5. QUESTION 4 ================

    def question_four(self):
        self.scene_start("S05_q4", title="Question 4")
        q = self.question(4, "111101 in binary = ? in hexadecimal", Q4)
        work = self.working(q, "111101  →  0011 1101     fours from the right, pad left",
                            "1101 = D,  0011 = 3     →     3D")
        trap = self.put(self.note("Trap: grouping from the left gives 1111 and 01, a wrong answer", GOLD, "wide"),
                        "wide", under=work, buff=0.4, align="l")

        self.tell("q4_01", "Next.", (None, lambda: self.show_question(q)))
        self.tell("q4_02", "No arithmetic is needed. Group in fours from the right and pad on the left. The number "
                           "has six bits. The right group is one one zero one, which is D. The left group is one "
                           "one, padded to zero zero one one, which is three. The answer is three D, option B. If "
                           "you grouped from the left you would get one one one one and zero one, which gives a "
                           "wrong answer.",
                  ("Group", FadeIn(work[0], shift=RIGHT * 0.15)), ("right", FadeIn(work[1], shift=RIGHT * 0.15)),
                  ("option", lambda: self.pick(q, 1)), ("grouped", FadeIn(trap, shift=UP * 0.1)))
        self.finish("S05_q4")

    # ===================================== 6. QUESTION 5 ================

    def question_five(self):
        self.scene_start("S06_q5", title="Question 5")
        q = self.question(5, "3E in hexadecimal = ? in binary", Q5)
        work = self.working(q, "3 → 0011,  E → 1110", "0011 1110  →  111110     leading zeros dropped")
        rule = self.put(self.note("Drop zeros only at the very left end", GOLD, "wide"), "wide", under=work,
                        buff=0.4, align="l")
        keep = self.put(self.note("Every digit in the middle keeps its full four bits", MAIN, "wide"), "wide",
                        under=rule, buff=0.25, align="l")

        self.tell("q5_01", "Next.", (None, lambda: self.show_question(q)))
        self.tell("q5_02", "Three is zero zero one one and E is one one one zero, so the full pattern is zero zero "
                           "one one one one one zero. Dropping the leading zeros gives one one one one one zero, "
                           "option A. You may drop zeros only at the very left end. Every digit in the middle of a "
                           "number must keep its full four bits.",
                  ("Three", FadeIn(work[0], shift=RIGHT * 0.15)), ("Dropping", FadeIn(work[1], shift=RIGHT * 0.15)),
                  ("option", lambda: self.pick(q, 0)), ("only", FadeIn(rule, shift=UP * 0.1)),
                  ("middle", FadeIn(keep, shift=UP * 0.1)))
        self.finish("S06_q5")

    # ===================================== 7. QUESTION 6 ================

    def question_six(self):
        self.scene_start("S07_q6", title="Question 6")
        q = self.question(6, "Which is the greatest?", Q6)
        work = self.working(q, "1F in hex       = 16 + 15    = 31", "35 in octal     = 3 × 8 + 5  = 29",
                            "11010 in binary = 16 + 8 + 2 = 26")
        trap = self.put(self.note("Trap: never compare different bases by look. Bring all to decimal", GOLD,
                                  "wide"), "wide", under=work, buff=0.4, align="l")

        self.tell("q6_01", "Next.", (None, lambda: self.show_question(q)))
        self.tell("q6_02", "Here the trap is in comparison. Never compare numbers in different bases by looking at "
                           "them. Bring all to decimal. One F is thirty-one. Three five in octal is three times "
                           "eight plus five, which is twenty-nine. One one zero one zero in binary is sixteen plus "
                           "eight plus two, which is twenty-six. So one F is greatest, option A.",
                  ("Never", FadeIn(trap, shift=UP * 0.1)), ("F", FadeIn(work[0], shift=RIGHT * 0.15)),
                  ("octal", FadeIn(work[1], shift=RIGHT * 0.15)), ("binary", FadeIn(work[2], shift=RIGHT * 0.15)),
                  ("greatest", lambda: self.pick(q, 0)), (None, lambda: self.add_row(P_COMPARE)))
        self.finish("S07_q6")

    # ===================================== 8. HANDLING THE TIME =========

    def the_time(self):
        self.begin("S08_time", "Handling the Time", "Handling the time")

        watch = self.put(self.stopwatch(), "left", BOARD_HIGH - 0.2)
        limit = self.put(self.note("At most a minute on one question", GOLD), "left", under=watch, buff=0.4)
        stuck = self.put(self.note("Taking longer? Best guess, move on, return later", MAIN), "left", under=limit,
                         buff=0.25)

        self.play(FadeIn(watch, shift=DOWN * 0.2), run_time=0.5)
        self.reply("tm_01", "How do we handle the time?", None, who="A student asks")
        self.tell("tm_02", "Do not spend more than a minute on one question. If a question is taking longer, mark "
                           "your best guess, move on and return if you have time.",
                  ("minute", lambda: [FadeIn(limit, shift=UP * 0.1), self.tick(watch, 1.0, 1.5)]),
                  ("guess", FadeIn(stuck, shift=UP * 0.1)), (None, lambda: self.light(P_FLOW, P_MINUTE)))

        self.finish("S08_time")

    # ===================================== 9. CLASSIFY EVERY MISTAKE ====

    def classify(self):
        self.begin("S09_classify", "Classify Every Mistake", "Classify every mistake")

        kinds = ["Concept error", "Calculation error", "Reading error", "Time-pressure error"]
        what = ["Wrong method or rule", "Right method, arithmetic slip", "Missed the base, or the direction asked",
                "Knew it, rushed it, did not check"]
        cure = ["Go back to the video and redo the method", "A slower, tidier layout, and a check",
                "Underline the bases and the direction first", "The habit of one quick check"]
        tb = table([list(r) for r in zip(kinds, what)], [2.9, 6.7], row_h=0.55, size=SMALL, head=False, font=FONT)
        self.put(tb, "wide", BOARD_TOP)
        tb.col(0).set_color(GOLD)
        tc = table([list(r) for r in zip(kinds, cure)], [2.9, 6.7], row_h=0.55, size=SMALL, head=False, font=FONT)
        tc.move_to(tb)
        tc.col(1).set_color(MAIN)
        examples = text("Examples: remainders read from the top; 6 × 8 + 5 written as 51", SMALL, MUTED)
        self.put(examples, "wide", under=tb, buff=0.35)
        cure_tag = self.put(text("Each one needs a different cure", SMALL, MUTED, BOLD), "wide", under=tb, buff=0.35)

        def cured(r):
            return FadeIn(tc.cell[(r, 1)], shift=RIGHT * 0.15)

        self.ask("er_01", "Now, the second half of today's work. When you make a mistake, we do not just correct "
                          "it. We classify it. Where did the error come from?", "Where did the error come from?")
        self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.15) for r in tb.rows], lag_ratio=0.5), run_time=3.0)
        self.play(FadeIn(examples), run_time=0.5)
        self.add_row(P_CLASSIFY)
        self.tell("er_02", "Each one needs a different cure. A concept error needs you to go back to the video and "
                           "redo the method. A calculation error needs a slower, tidier layout, and a check. A "
                           "reading error needs you to underline the bases and the direction of the conversion "
                           "before you start. And a time-pressure error needs the habit of one quick check.",
                  ("cure", lambda: [FadeOut(VGroup(tb.col(1), examples)), FadeIn(cure_tag)]),
                  ("concept", cured(0)), ("calculation", cured(1)), ("reading", cured(2)), ("habit", cured(3)))

        self.finish("S09_classify")

    # ===================================== 10. THE ERROR LOG ============

    def error_log(self):
        self.begin("S10_log", "The Error Log", "Keeping an error log")

        cols = VGroup(*[pill(s, MAIN, SMALL) for s in ("The question", "The type of error",
                                                       "What I will do differently")]).arrange(RIGHT, buff=0.3)
        self.put(cols, "wide", BOARD_HIGH - 0.1, "l")
        entry = stack(mono("Q4  |  READING", SMALL, GOLD),
                      text("Wrote the answer for hex → binary, not binary → hex", SMALL, INK),
                      text("Next time: underline FROM and TO before starting", SMALL, MAIN, BOLD), buff=0.22)
        card = self.put(self.card(entry, color=MUTED, pad=0.3), "wide", under=cols, buff=0.5, align="l")
        count = self.put(self.note("After a week: the largest count is where the marks are", GOLD, "wide"), "wide",
                         under=card, buff=0.45, align="l")

        self.tell("lg_01", "Let us look at how to keep the log. For each mistake write the question, the type of "
                           "error and one sentence on what you will do differently.",
                  ("question", FadeIn(cols[0], shift=UP * 0.1)), ("type", FadeIn(cols[1], shift=UP * 0.1)),
                  ("sentence", FadeIn(cols[2], shift=UP * 0.1)), (None, FadeIn(card, shift=UP * 0.15)))
        self.tell("lg_02", "After a week, count how many mistakes you have of each kind. The largest count is where "
                           "you will gain the most marks.",
                  ("largest", FadeIn(count, shift=UP * 0.1)), (None, lambda: self.add_row(P_CAUSE)))

        self.finish("S10_log")

    # ============================================== 11. SUMMARY =========

    def summary(self):
        self.begin("S11_summary", "Summary", "Summary", GOLD)

        rows = self.put(self.ticks(["Choose the method, calculate, check once, move on",
                                    "Never compare different bases without converting",
                                    "About a minute for each simple conversion",
                                    "Classify every mistake: concept, calculation, reading, time",
                                    "Fix the cause, not just the answer"]), "full", BOARD_HIGH, "l")

        self.tell("sum_01", "Let me ask you to summarise today.")
        self.reply("sum_02", "Choose the method, calculate, check once and move on. Never compare numbers in "
                             "different bases without converting. Aim for about a minute for each simple "
                             "conversion. Classify every mistake as concept, calculation, reading or time-pressure, "
                             "and fix the cause rather than just the answer.", "Reading from her notes",
                   ("Choose", lambda: [FadeIn(rows[0], shift=RIGHT * 0.2), self.light(P_FLOW)]),
                   ("Never", lambda: [FadeIn(rows[1], shift=RIGHT * 0.2), self.light(P_COMPARE)]),
                   ("Aim", lambda: [FadeIn(rows[2], shift=RIGHT * 0.2), self.light(P_MINUTE)]),
                   ("Classify", lambda: [FadeIn(rows[3], shift=RIGHT * 0.2), self.light(P_CLASSIFY)]),
                   ("fix", lambda: [FadeIn(rows[4], shift=RIGHT * 0.2), self.light(P_CAUSE)]), who="A student")
        self.hush()
        self.play(*self.all_lit())
        self.finish("S11_summary")

    # ============================================== 12. NEXT ============

    def next_lesson(self):
        self.scene_start("S12_next", title="Next Lesson: Data Representation and Computer Codes")
        things = VGroup(*[pill(s, MAIN, LABEL) for s in ("Numbers", "Letters", "Symbols")]).arrange(RIGHT, buff=0.3)
        self.put(things, "full", BOARD_TOP)
        nxt = self.put(self.next_up("Next lesson: Data representation and computer codes"), "full", under=things,
                       buff=0.7)
        self.tell("next_01", "Exactly. You now have every tool for the number systems. But numbers are not the only "
                             "things a computer stores. Letters, symbols, even the characters on this board have to "
                             "be stored as bits.",
                  ("numbers", FadeIn(things[0], shift=UP * 0.1)), ("Letters", FadeIn(things[1], shift=UP * 0.1)),
                  ("symbols", FadeIn(things[2], shift=UP * 0.1)))
        self.ask("next_02", "How?", "How are letters and symbols stored as bits?", (None, FadeIn(nxt, scale=1.1)))
        self.undock()
        self.finish("S12_next")

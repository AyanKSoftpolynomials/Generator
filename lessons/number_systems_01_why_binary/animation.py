"""
animation.py for the LMS video generator.

Course : C-CAT Computer Fundamentals
Lesson : Lesson 3 - Number Systems Concepts and Representation
Video  : 03 Video 1 - Why Binary

Source script:
  CCAT_Computer_Fundamentals_Scripts_Lessons_1-5/PDF/Lesson 3 - Number Systems Concepts and Representation/03 Video 1 - Why Binary.pdf
  The script has no speaker labels. Every line was labelled as below:
    TEACHER  spoken by the teacher: ``self.tell`` / ``self.ask`` (TEACHER_VOICE). Drives the board.
    STUDENT  spoken by a student: ``self.reply`` (STUDENT_VOICE). Every student answer is its own
             narration and appears as a card at the bottom right.
    STAGE    stage direction: not narrated, it becomes the visuals (or the name on the student card).
    BOARD    what the board shows: on screen, not spoken.
  Spoken text uses words ("one zero one one"); the cards and the board show digits ("1011").

Speaker split:
  01 TITLE   Why Computers Use Binary: Number Systems and Positional Notation
  02 STAGE   The teacher walks in and switches the classroom light on and off a few times.
  03 TEACHER What did the light just do?
  04 STUDENT It was on, and then off.
  05 TEACHER How many states does this switch have?
  06 STUDENT Two.
  07 TEACHER Keep that in mind. Now tell me, why do we count in tens?
  08 STUDENT Because we have ten fingers.
  09 TEACHER That is a very good answer, and probably the true one. Our number system came from our bodies.
             Now think about a computer. It has no fingers. It has electronic circuits. What states can a
             circuit easily have?
  10 STUDENT On and off.
  11 TEACHER Exactly. A circuit can be on, with current flowing or a high voltage, or off, with no current or
             a low voltage. Two states are easy to build, easy to distinguish and very reliable. If we asked
             a circuit to hold ten different voltage levels, small disturbances would blur one level into the
             next, and the computer would make mistakes. With two states, there is almost no confusion.
  12 TEACHER So the computer uses two symbols, 0 and 1. This is the binary system, and each of these symbols
             is called a bit, short for binary digit.
  13 STAGE   The board shows:
  14 BOARD   BIT    = one binary digit    (0 or 1)
  15 BOARD   BYTE   = a group of 8 bits
  16 TEACHER Let us step back and ask a more basic question. What is a number system?
  17 STUDENT A way of writing numbers?
  18 TEACHER Yes. It is a set of symbols together with rules for writing numbers. The number of different
             digits it uses is called its base, or radix.
  19 BOARD   NUMBER SYSTEM    BASE    DIGITS USED
  20 BOARD   Decimal           10     0 to 9
  21 BOARD   Binary             2     0, 1
  22 BOARD   Octal              8     0 to 7
  23 BOARD   Hexadecimal       16     0 to 9, A to F
  24 TEACHER Notice that the digits in every system go from 0 up to one less than the base. The largest digit
             is always the base minus one. Remember this, because it will help you decide in seconds whether
             a number is valid.
  25 TEACHER Now there are two kinds of number systems. Look at the Roman numeral XXX. What is its value?
  26 STUDENT Thirty.
  27 TEACHER What does each X mean?
  28 STUDENT Ten.
  29 TEACHER Is each X worth ten no matter where it sits?
  30 STUDENT Yes.
  31 TEACHER That is a non-positional system. A symbol has a fixed value wherever it appears. Now look at the
             number 505 in the decimal system. Are the two 5s worth the same?
  32 STUDENT No. One is five hundred and the other is five.
  33 TEACHER That is a positional system. The value of a digit depends on its position, which is why it is
             much easier to calculate with.
  34 STAGE   The board shows the idea.
  35 BOARD   505  =  5 x 100  +  0 x 10  +  5 x 1
  36 BOARD   position 2        position 1    position 0
  37 TEACHER Positions are counted from the right, starting at 0. Each position has a weight, which is the
             base raised to the position number. For decimal the weights are 1, 10, 100, 1000. For any system
             the rule is the same.
  38 BOARD   VALUE  =  sum of ( digit x base^position )
  39 STAGE   A student asks:
  40 STUDENT So the only thing that changes from one system to another is the base?
  41 TEACHER Exactly. The rule never changes. Only the base changes, and therefore the weights change. That
             is the central idea of this whole topic.
  42 TEACHER Let me test you. In a number system with base 5, what digits would you expect?
  43 STUDENT 0, 1, 2, 3 and 4.
  44 TEACHER And what would the weights of the first four places be?
  45 STUDENT 1, 5, 25 and 125.
  46 TEACHER Excellent. You have just derived the rule without me telling you.
  47 TEACHER Let us summarise.
  48 STAGE   A student reads from her notes.
  49 STUDENT Computers use binary because two states are easy and reliable to build. A number system has a
             base and a set of digits from 0 to base minus one. In a positional system the value of a digit
             depends on its position, and each position has a weight equal to the base raised to its position
             number.
  50 TEACHER Perfect. In the next video we put this rule to work on the two systems that matter most, decimal
             and binary.
  51 STAGE   The board changes to:
  52 BOARD   NEXT: DECIMAL AND BINARY

Notes:
  - Opening block ``open_01`` is not in the script: it is the usual breadcrumb opening
    (where we are, what came before, what this video covers).
  - Long teacher lines are split into two narrations where the board changes in between.
  - Facts checked in the data block: 505 = 5 x 100 + 0 x 10 + 5 x 1; base 5 has the digits
    0 to 4 and the weights 1, 5, 25, 125; the largest digit of every base is base - 1.

Style: 2D, three colours (blue main, grey support, gold highlight). One drawn lamp (the script
opens with the light switch) and raised boxes only for the key object, the bit.
Pinned KEY IDEAS panel from the first scene to the end.

Section map:
  S00 Opening   S01 Two states   S02 Number system and base   S03 Positional or not
  S04 Only the base changes   S05 Summary   S06 Next
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
CRUMB_VIDEO = "Video 1 of 4"
VIDEO_TITLE = "Why Computers Use Binary"
BEFORE_LABEL = "Before this"
BEFORE_IDEA = "Lesson 2: how a computer is organised"
TODAY_IDEA = "Why binary, what a base is, and how position gives value"

TEACHER_VOICE = "vijay"
STUDENT_VOICE = "kavya"        # students speak in their own voice, in their own blocks
TEACHER_PAUSE = 0.7            # silence after each teacher block (seconds), so speakers never run together
STUDENT_PAUSE = 0.6            # silence after each student block

IDEAS = [("Two states: binary, 0 and 1", GOLD), ("Bit = binary digit", MAIN), ("Base = number of digits", MAIN),
         ("Largest digit = base − 1", MAIN), ("Value = sum of digit × weight", MAIN)]
P_BINARY, P_BIT, P_BASE, P_LARGEST, P_VALUE = range(5)

SYSTEMS = [("Decimal", 10, "0 to 9"), ("Binary", 2, "0, 1"), ("Octal", 8, "0 to 7"),
           ("Hexadecimal", 16, "0 to 9, A to F")]

assert 5 * 100 + 0 * 10 + 5 * 1 == 505
assert [5 ** k for k in range(4)] == [1, 5, 25, 125]
assert list(range(5)) == [0, 1, 2, 3, 4]
assert 10 + 10 + 10 == 30


class WhyBinaryVideo(LMSScene):
    lesson_title = "Why Computers Use Binary"

    def construct(self):
        self.setup_board()
        self.opening("open_01", "This is lesson three, number systems. Lesson two showed how a computer is "
                                "organised. In this first video, we see why computers use binary, and how position "
                                "gives a digit its value.", "first")
        self.open_panel("Key ideas", IDEAS)
        self.two_states()
        self.number_system()
        self.positional()
        self.base_five()
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

    def lamp(self):
        """The classroom light: the one drawing this video needs."""
        glass = Circle(radius=0.5, stroke_color=GOLD, stroke_width=3, fill_color=GOLD, fill_opacity=0.9)
        cap = Rectangle(width=0.36, height=0.26, stroke_color=MUTED, stroke_width=2, fill_color=MUTED,
                        fill_opacity=1).next_to(glass, DOWN, buff=0)
        rays = VGroup(*[Line(ORIGIN, UP * 0.22, color=GOLD, stroke_width=4).shift(UP * 0.68).rotate(
            a, about_point=ORIGIN) for a in (-1.2, -0.6, 0, 0.6, 1.2)])
        g = VGroup(glass, cap, rays)
        g.glass, g.rays = glass, rays
        return g

    def lamp_off(self, lamp):
        return [lamp.glass.animate.set_fill(PANEL, 1), lamp.rays.animate.set_opacity(0)]

    def lamp_on(self, lamp):
        return [lamp.glass.animate.set_fill(GOLD, 0.9), lamp.rays.animate.set_opacity(1)]

    # ============================================== 1. TWO STATES =======

    def two_states(self):
        self.begin("S01_two_states", "Two States", "A switch has two states")

        lamp = self.put(self.lamp(), "right", BOARD_TOP - 0.1)
        states = self.put(self.note("2 states: ON and OFF", GOLD), "left", BOARD_TOP)
        digits = self.put(mono("0 1 2 3 4 5 6 7 8 9", BODY, MAIN), "left", under=states, buff=0.45)
        ten = self.put(self.para("Decimal: 10 digits, like our 10 fingers", size=SMALL, color=MUTED), "left",
                       under=digits, buff=0.2)
        circuit = self.put(self.note("A computer has circuits, not fingers", MAIN), "left", under=ten, buff=0.45)

        self.play(FadeIn(lamp), run_time=0.5)
        for _ in range(2):
            self.play(*self.lamp_off(lamp), run_time=0.3)
            self.play(*self.lamp_on(lamp), run_time=0.3)
        self.ask("two_01", "What did the light just do?", None,
                 ("light", lambda: self.lamp_off(lamp)), (None, lambda: self.lamp_on(lamp)))
        self.reply("two_02", "It was on, and then off.")
        self.ask("two_03", "How many states does this switch have?")
        self.reply("two_04", "Two.", None, (None, FadeIn(states, shift=UP * 0.1)))
        self.ask("two_05", "Keep that in mind. Now tell me, why do we count in tens?", "Why do we count in tens?")
        self.reply("two_06", "Because we have ten fingers.", None, (None, FadeIn(digits, shift=UP * 0.1)))
        self.tell("two_07", "That is a very good answer, and probably the true one. Our number system came from our "
                            "bodies. Now think about a computer. It has no fingers. It has electronic circuits.",
                  ("bodies", FadeIn(ten)), ("circuits", FadeIn(circuit, shift=UP * 0.1)))
        self.ask("two_08", "What states can a circuit easily have?")
        self.reply("two_09", "On and off.", None, (None, Indicate(states, color=GOLD, scale_factor=1.08)))

        # the bit: the key object, drawn raised
        self.hush()
        self.drop_q()
        self.play(FadeOut(VGroup(lamp, states, digits, ten, circuit)), run_time=0.5)
        on_bit, off_bit = bit_cells("1", 0.85, GOLD, raised=True), bit_cells("0", 0.85, MAIN, raised=True)
        lo, hi, _ = self.zone("left")
        on_row = VGroup(on_bit, fitted_text("ON: current flows, high voltage", hi - lo - 1.6, LABEL, INK,
                                            max_lines=2)).arrange(RIGHT, buff=0.45)
        off_row = VGroup(off_bit, fitted_text("OFF: no current, low voltage", hi - lo - 1.6, LABEL, INK,
                                              max_lines=2)).arrange(RIGHT, buff=0.45)
        rows = self.put(stack(on_row, off_row, buff=0.4), "left", BOARD_HIGH - 0.15, "l")
        blur = self.put(self.note("10 voltage levels: they blur", MUTED), "left", under=rows, buff=0.5, align="l")
        clear = self.put(self.note("2 states: almost no confusion", GOLD), "left", under=blur, buff=0.25, align="l")
        bit = stack(text("BIT = one binary digit (0 or 1)", LABEL, GOLD, BOLD),
                    text("BYTE = a group of 8 bits", LABEL, MAIN, BOLD), buff=0.2)
        bit_card = self.put(self.card(bit, color=GOLD, pad=0.25), "left", under=rows, buff=0.5, align="l")

        self.tell("two_10", "Exactly. A circuit can be on, with current flowing or a high voltage, or off, with no "
                            "current or a low voltage. Two states are easy to build, easy to distinguish and very "
                            "reliable.",
                  ("on", FadeIn(on_row, shift=RIGHT * 0.2)), ("off", FadeIn(off_row, shift=RIGHT * 0.2)),
                  ("reliable", lambda: [Indicate(on_bit, color=GOLD), Indicate(off_bit, color=MAIN)]))
        self.tell("two_11", "If we asked a circuit to hold ten different voltage levels, small disturbances would "
                            "blur one level into the next, and the computer would make mistakes. With two states, "
                            "there is almost no confusion.",
                  ("blur", FadeIn(blur, shift=UP * 0.1)), ("almost", FadeIn(clear, shift=UP * 0.1)))
        self.tell("two_12", "So the computer uses two symbols, zero and one. This is the binary system, and each of "
                            "these symbols is called a bit, short for binary digit.",
                  ("symbols", lambda: [Indicate(off_bit, color=GOLD), Indicate(on_bit, color=GOLD)]),
                  ("binary", lambda: self.add_row(P_BINARY)),
                  ("bit", lambda: [FadeOut(VGroup(blur, clear)), FadeIn(bit_card, shift=UP * 0.1)]),
                  (None, lambda: self.add_row(P_BIT)))

        self.finish("S01_two_states")

    # ===================================== 2. NUMBER SYSTEM AND BASE ====

    def number_system(self):
        self.begin("S02_base", "Number System and Base", "What is a number system?")

        defn = self.put(self.note("Symbols + rules for writing numbers", MAIN), "left", BOARD_TOP)
        base = self.put(self.note("Base (radix) = how many digits it uses", GOLD), "left", under=defn)
        tb = table([["Number system", "Base", "Digits used"]] + [[n_, str(b), d] for n_, b, d in SYSTEMS],
                   [3.3, 1.5, 3.9], row_h=0.55, font=FONT)
        self.put(tb, "full", BOARD_HIGH - 0.05)
        largest = self.put(self.note("Largest digit = base − 1", GOLD), "left", under=tb, buff=0.4)

        self.ask("base_01", "Let us step back and ask a more basic question. What is a number system?",
                 "What is a number system?")
        self.reply("base_02", "A way of writing numbers?")
        self.tell("base_03", "Yes. It is a set of symbols together with rules for writing numbers. The number of "
                             "different digits it uses is called its base, or radix.",
                  ("symbols", FadeIn(defn, shift=UP * 0.1)), ("base", FadeIn(base, shift=UP * 0.1)),
                  (None, lambda: self.add_row(P_BASE)))

        self.drop_q()
        self.play(FadeOut(VGroup(defn, base)), run_time=0.4)
        self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.15) for r in tb.rows], lag_ratio=0.3), run_time=2.0)
        self.tell("base_04", "Notice that the digits in every system go from zero up to one less than the base. The "
                             "largest digit is always the base minus one. Remember this, because it will help you "
                             "decide in seconds whether a number is valid.",
                  ("digits", Indicate(tb.col(2), color=GOLD, scale_factor=1.05)),
                  ("largest", FadeIn(largest, shift=UP * 0.1)), (None, lambda: self.add_row(P_LARGEST)))

        self.finish("S02_base")

    # ===================================== 3. POSITIONAL OR NOT =========

    def positional(self):
        self.begin("S03_positional", "Positional or Not", "Two kinds of number systems")

        roman = self.put(text("X  X  X", TITLE, MAIN, BOLD), "left", BOARD_TOP)
        tens = self.put(mono("10 + 10 + 10 = 30", LABEL, INK), "left", under=roman)
        nonpos = self.put(self.note("Non-positional: same value anywhere", MAIN), "left", under=tens, buff=0.4)

        self.play(FadeIn(roman, shift=UP * 0.1), run_time=0.5)
        self.ask("pos_01", "Now there are two kinds of number systems. Look at the Roman numeral X X X. What is its "
                           "value?", "Roman numeral XXX: what is its value?")
        self.reply("pos_02", "Thirty.", "30.")
        self.ask("pos_03", "What does each X mean?")
        self.reply("pos_04", "Ten.", "10.", (None, FadeIn(tens, shift=UP * 0.1)))
        self.ask("pos_05", "Is each X worth ten no matter where it sits?")
        self.reply("pos_06", "Yes.")
        self.tell("pos_07", "That is a non-positional system. A symbol has a fixed value wherever it appears.",
                  ("fixed", FadeIn(nonpos, shift=UP * 0.1)))

        cells = self.put(bit_cells("505", 0.8), "left", BOARD_TOP - 0.5)
        worth = VGroup(*[mono(s, SMALL, GOLD).next_to(c, UP, buff=0.15) for s, c in zip(["500", "0", "5"], cells)])
        places = VGroup(*[text(str(2 - k), SMALL, MUTED, BOLD).next_to(c, DOWN, buff=0.15)
                          for k, c in enumerate(cells)])
        place_tag = text("position", SMALL, MUTED).next_to(places, LEFT, buff=0.35)
        posn = self.put(self.note("Positional: value depends on position", GOLD), "left", under=places, buff=0.35)
        expand = self.put(mono("505 = 5×100 + 0×10 + 5×1", LABEL, INK), "left", under=places, buff=0.4)
        rule = stack(text("Weight = base raised to the position", SMALL, MAIN, BOLD),
                     text("Value = sum of (digit × weight)", LABEL, GOLD, BOLD), buff=0.18)
        rule_card = self.put(self.card(rule, color=GOLD, pad=0.25), "left", under=expand, buff=0.4)

        self.hush()
        self.play(FadeOut(VGroup(roman, tens, nonpos)), run_time=0.4)
        self.play(FadeIn(cells, shift=UP * 0.1), run_time=0.5)
        self.ask("pos_08", "Now look at the number five zero five in the decimal system. Are the two fives worth the "
                           "same?", "Look at 505 in decimal. Are the two 5s worth the same?",
                 ("fives", lambda: [Indicate(cells[0], color=GOLD), Indicate(cells[2], color=GOLD)]))
        self.reply("pos_09", "No. One is five hundred and the other is five.", "No. One is 500 and the other is 5.",
                   (None, FadeIn(worth, shift=DOWN * 0.1)))
        self.tell("pos_10", "That is a positional system. The value of a digit depends on its position, which is why "
                            "it is much easier to calculate with.",
                  ("positional", FadeIn(posn, shift=UP * 0.1)),
                  ("depends", Indicate(worth, color=GOLD, scale_factor=1.1)))
        self.drop_q()
        self.tell("pos_11", "Positions are counted from the right, starting at zero. Each position has a weight, "
                            "which is the base raised to the position number. For decimal the weights are one, ten, "
                            "hundred, thousand. For any system the rule is the same.",
                  ("right", lambda: [FadeIn(place_tag), LaggedStart(*[FadeIn(p, shift=UP * 0.1)
                                                                    for p in reversed(places)], lag_ratio=0.4)]),
                  ("weight", lambda: [FadeOut(posn), FadeIn(expand, shift=UP * 0.1)]),
                  ("rule", FadeIn(rule_card, shift=UP * 0.1)), (None, lambda: self.add_row(P_VALUE)))

        self.finish("S03_positional")

    # ===================================== 4. ONLY THE BASE CHANGES =====

    def base_five(self):
        self.begin("S04_base_five", "Only the Base Changes", "Same rule, different base")

        rule = stack(text("Weight = base raised to the position", SMALL, MAIN, BOLD),
                     text("Value = sum of (digit × weight)", LABEL, GOLD, BOLD), buff=0.18)
        rule_card = self.put(self.card(rule, color=GOLD, pad=0.25), "left", BOARD_TOP)
        only = self.put(self.note("Only the base changes", GOLD), "left", under=rule_card)
        five = stack(mono("Base 5 digits : 0 1 2 3 4", LABEL, INK), mono("Base 5 weights: 125 25 5 1", LABEL, INK))
        self.put(five, "left", under=only, buff=0.4)

        self.play(FadeIn(rule_card, shift=UP * 0.1), run_time=0.5)
        self.reply("five_01", "So the only thing that changes from one system to another is the base?",
                   "So the only thing that changes is the base?", who="A student asks")
        self.tell("five_02", "Exactly. The rule never changes. Only the base changes, and therefore the weights "
                             "change. That is the central idea of this whole topic.",
                  ("Only", FadeIn(only, shift=UP * 0.1)), ("central", lambda: self.light(P_BASE, P_VALUE)))
        self.ask("five_03", "Let me test you. In a number system with base five, what digits would you expect?",
                 "Base 5: what digits would you expect?")
        self.reply("five_04", "Zero, one, two, three and four.", "0, 1, 2, 3 and 4.",
                   (None, FadeIn(five[0], shift=UP * 0.1)))
        self.ask("five_05", "And what would the weights of the first four places be?",
                 "Base 5: what are the weights of the first four places?")
        self.reply("five_06", "One, five, twenty-five and one hundred and twenty-five.", "1, 5, 25 and 125.",
                   (None, FadeIn(five[1], shift=UP * 0.1)))
        self.tell("five_07", "Excellent. You have just derived the rule without me telling you.",
                  ("derived", lambda: [Indicate(five, color=GOLD, scale_factor=1.05), self.all_lit()]))

        self.finish("S04_base_five")

    # ============================================== 5. SUMMARY ==========

    def summary(self):
        self.begin("S05_summary", "Summary", "Summary", GOLD)

        rows = self.put(self.ticks(["Binary: two states are easy and reliable to build",
                                    "A base, and digits from 0 to base − 1",
                                    "Positional: value depends on position",
                                    "Weight = base raised to the position"]), "full", BOARD_HIGH, "l")

        self.tell("sum_01", "Let us summarise.")
        self.reply("sum_02", "Computers use binary because two states are easy and reliable to build. A number "
                             "system has a base and a set of digits from zero to base minus one. In a positional "
                             "system the value of a digit depends on its position, and each position has a weight "
                             "equal to the base raised to its position number.", "Reading from her notes",
                   ("Computers", lambda: [FadeIn(rows[0], shift=RIGHT * 0.2), self.light(P_BINARY, P_BIT)]),
                   ("system", lambda: [FadeIn(rows[1], shift=RIGHT * 0.2), self.light(P_BASE, P_LARGEST)]),
                   ("positional", lambda: [FadeIn(rows[2], shift=RIGHT * 0.2), self.light(P_VALUE)]),
                   ("weight", FadeIn(rows[3], shift=RIGHT * 0.2)), who="A student")
        self.hush()
        self.scene_end("S05_summary")

    # ============================================== 6. NEXT =============

    def next_video(self):
        self.scene_start("S06_next", title="Next: Decimal and Binary")
        nxt = self.put(self.next_up("Next: Decimal and binary"), "wide", -1.9)
        self.tell("next_01", "Perfect. In the next video we put this rule to work on the two systems that matter "
                             "most, decimal and binary.",
                  ("Perfect", lambda: self.all_lit()), ("next", FadeIn(nxt, scale=1.1)))
        self.undock()
        self.finish("S06_next")

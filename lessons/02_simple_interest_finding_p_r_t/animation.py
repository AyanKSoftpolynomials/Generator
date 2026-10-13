"""
animation.py for the LMS video generator.

Course : Pre-C-CAT - Section A - Quantitative Aptitude
Video  : Lesson 11 - Simple & Compound Interest - 02 - Simple Interest: Finding P, R, T

Source script:
  C:\\Scripts\\Section A\\Module_2_Section_A_Quantitative_Aptitude_Part_1\\Aptitude_Scripts\\Sessions 1-4 - Interest, Profit & Loss, Time & Work\\Lesson 11 - Simple & Compound Interest\\02 - Simple Interest - Finding P, R, T.pdf

Built on the golden-reference pattern:
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``;
  * layouts stacked with next_to and guarded with ``no_overlap``; nothing is
    ever animated onto or into another box.

Lesson 11, Video 2 of 7. Not the first video of the lesson: a silent breadcrumb, a one-line recap of Video 1, then today's topic. No spoken course welcome.
The narration follows the script section by section, with numbers written as words for the voice. Tables and lists are spoken one row at a time; the six exam patterns, nine practice questions and nine answers are split over two screens each so the text stays readable. Every answer on screen is computed from the question's numbers and asserted.
Pauses: 10 s on the hook ("in about ten seconds"), the script's 10-second countdown at the checkpoint, 12 s after each practice screen.
"""

import math

import numpy as np
from manim import *

from src.animation import LMSScene

# ============================================================== style ====

BG = "#0B1020"
INK = "#E6EAF2"
MUTED = "#8B95A7"
PANEL = "#151C2E"
CELL = "#1B2440"

TERM = INK             # series terms
DIFF = "#4FC3F7"       # first differences
SECOND = "#CE93D8"     # second differences / pattern of the differences
RATIO = "#FFB74D"      # ratios (the next topic's tool)
FOCUS = "#FFD54F"      # "look here" / predicted value
GOOD = "#66BB6A"       # confirmed answer
BAD = "#EF5350"        # wrong / trap

FONT = "Segoe UI"
MIN_FONT = 22          # readable floor: text is never shrunk below this
TITLE = 46
BODY = 30
LABEL = 28
SMALL = 24

# ============================================================= layout ====

FRAME_W = config.frame_width
FRAME_H = config.frame_height
SAFE = 0.45                                   # margin kept clear on every side
SAFE_W = FRAME_W - 2 * SAFE
SAFE_H = FRAME_H - 2 * SAFE

ZONE_W = 6.2                                  # width of each half-screen zone
LEFT_ZONE = LEFT * 3.35                       # centre of the left half
RIGHT_ZONE = RIGHT * 3.35                     # centre of the right half
TOP_Y = FRAME_H / 2 - SAFE - 0.9              # first row under the top edge
BOTTOM_Y = -FRAME_H / 2 + SAFE + 0.45         # caption / tracker row

CARD_TOP = FRAME_H / 2 - SAFE - 0.2           # top edge of a question card


# ======================================================= text helpers ====

def text(s, size=BODY, color=INK, weight=NORMAL, t2c=None):
    return Text(s, font=FONT, font_size=size, color=color, weight=weight, t2c=t2c or {})


def fit_width(mob, max_width):
    """Scale ``mob`` down (never up) to at most ``max_width``."""
    if mob.width > max_width:
        mob.scale_to_fit_width(max_width)
    return mob


def fit_height(mob, max_height):
    """Scale ``mob`` down (never up) to at most ``max_height``."""
    if mob.height > max_height:
        mob.scale_to_fit_height(max_height)
    return mob


def fit_within(mob, max_width, max_height):
    return fit_height(fit_width(mob, max_width), max_height)


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


def fitted_text(s, max_width, size=BODY, color=INK, weight=NORMAL, max_lines=3, t2c=None):
    """Readable text no wider than ``max_width`` (never below MIN_FONT)."""
    floor = max(MIN_FONT, 0.85 * size)
    for lines in range(1, max_lines + 1):
        body = s if lines == 1 else wrap_lines(s, lines)
        mob = text(body, size, color, weight, t2c)
        if mob.width <= max_width:
            return mob
        if size * max_width / mob.width >= floor:
            return mob.scale(max_width / mob.width)
        floor = MIN_FONT
    if size * max_width / mob.width >= MIN_FONT:
        return mob.scale(max_width / mob.width)
    raise ValueError(f"Text {s!r} cannot fit {max_width:.2f} units at a readable size; "
                     "shorten it or give it a wider container.")


def pill(label, color=FOCUS, size=SMALL, fill_opacity=0.14):
    """Short keyword tag. The box is sized from the text, so text cannot escape."""
    t = text(label, size, color, BOLD)
    box = RoundedRectangle(corner_radius=(t.height + 0.26) / 2, width=t.width + 0.5, height=t.height + 0.26,
                           stroke_color=color, stroke_width=2, fill_color=color, fill_opacity=fill_opacity)
    t.move_to(box)
    return VGroup(box, t)



# ================================================== vocabulary helpers ====

WORD = "#4FC3F7"          # the question word
OPTION = INK              # option text
TRAP = BAD                # eliminated options
KEY = GOOD                # the answer
STEP_COLS = {"READ": "#4FC3F7", "PREDICT": "#CE93D8", "ELIMINATE": "#EF5350", "CONFIRM": "#66BB6A"}


def process_strip(size=LABEL):
    """READ → PREDICT → ELIMINATE → CONFIRM as four chips."""
    parts = []
    for i, (name, col) in enumerate(STEP_COLS.items()):
        if i:
            parts.append(text("→", size, MUTED))
        parts.append(pill(name, col, size=size))
    return VGroup(*parts).arrange(RIGHT, buff=0.2)


def step_chip(strip, name):
    """The chip for one step inside a process strip."""
    return strip[2 * list(STEP_COLS).index(name)]


class OptionQuestion:
    """WORD: (a) … (b) … (c) … (d) …, with elimination and confirmation effects.
    ``key`` is the letter of the answer; ``traps`` maps letters to the reason
    each wrong option is removed."""

    def __init__(self, word, options, key, traps, width=6.0, word_size=TITLE):
        assert key in "abcd"[:len(options)] and set(traps) | {key} == set("abcd"[:len(options)])
        self.key, self.traps = key, traps
        self.word = pill(word, WORD, size=word_size)
        self.rows = VGroup(*[VGroup(text(f"({l})", LABEL, MUTED), fitted_text(o, width - 1.0, BODY, OPTION))
                             .arrange(RIGHT, buff=0.25) for l, o in zip("abcd", options)])
        self.rows.arrange(DOWN, buff=0.28, aligned_edge=LEFT)
        self.group = VGroup(self.word, self.rows).arrange(DOWN, buff=0.45, aligned_edge=LEFT)

    def row(self, letter):
        return self.rows["abcd".index(letter)]

    def strike(self, letter, reason_color=TRAP):
        """Animations: strike through a wrong option, dim it, and tag the reason."""
        r = self.row(letter)
        line = Line(r.get_left() + LEFT * 0.05, r.get_right() + RIGHT * 0.05, color=TRAP, stroke_width=3)
        tag = pill(self.traps[letter], reason_color, size=SMALL).next_to(r, RIGHT, buff=0.35)
        return VGroup(line, tag), [Create(line), r.animate.set_opacity(0.4), FadeIn(tag, shift=LEFT * 0.1)]

    def confirm(self):
        r = self.row(self.key)
        box = SurroundingRectangle(r, color=KEY, buff=0.12, corner_radius=0.1)
        return box, [Create(box), r[1].animate.set_color(KEY)]


def meaning_circles(words, centres, radii, colors, label_size=LABEL):
    """Each word's meaning as a translucent circle with its label inside."""
    out = VGroup()
    for w, c, r, col in zip(words, centres, radii, colors):
        circ = Circle(radius=r, color=col, stroke_width=3, fill_color=col, fill_opacity=0.15).move_to(c)
        out.add(VGroup(circ, text(w, label_size, col, BOLD).move_to(c)))
    return out


def pair_chip(a, b, color, note=None, size=LABEL):
    """'a ≈ b' chip, optionally with a small note underneath."""
    chip = pill(f"{a}  ≈  {b}", color, size=size)
    if note:
        return VGroup(chip, text(note, SMALL, MUTED)).arrange(DOWN, buff=0.12)
    return chip


# ============================================================= lesson ====

from fractions import Fraction


def dec(x):
    return f"{float(x):g}"


def rs(x):
    return f"₹{int(x):,}"


def simple_interest(p, r, t):
    """I = P × R × T ÷ 100."""
    return Fraction(p) * Fraction(r) * Fraction(t) / 100


def find_rate(p, i, t):
    return Fraction(100 * i, p * t)


def find_time(p, i, r):
    return Fraction(100 * i, p * r)


def find_principal(i, r, t):
    return Fraction(100 * i, r * t)


def two_amounts(a1, t1, a2, t2):
    """Two amounts at two times (simple interest) -> (interest per year, principal, rate)."""
    per_year = Fraction(a2 - a1, t2 - t1)
    p = a1 - per_year * t1
    return per_year, p, per_year / p * 100


def n_times_years(n, known_n, known_years):
    """A sum becomes ``known_n`` times in ``known_years``; years to become ``n`` times (interest is linear)."""
    return Fraction(known_years, known_n - 1) * (n - 1)


# ---- the hook ----
LOAN, REPAID, YEARS = 40000, 52800, 4
HOOK_I = REPAID - LOAN
HOOK_R = find_rate(LOAN, HOOK_I, YEARS)
HOOK_YEARLY = simple_interest(LOAN, HOOK_R, 1)
assert (HOOK_I, HOOK_R, HOOK_YEARLY, HOOK_YEARLY * YEARS) == (12800, 8, 3200, 12800)

# ---- second worked example: two amounts ----
EX_PER_YEAR, EX_P, EX_R = two_amounts(8400, 4, 9600, 6)
assert (EX_PER_YEAR, EX_P, EX_R) == (600, 6000, 10)

# ---- the straight line, on one illustration: 1,000 at 10% ----
LINE_P, LINE_R = 1000, 10
LINE_STEP = int(simple_interest(LINE_P, LINE_R, 1))
LINE = [LINE_P + LINE_STEP * t for t in range(5)]
assert LINE == [1000, 1100, 1200, 1300, 1400]

# ---- exam patterns (answers computed) ----
PAT_T = find_time(12500, 15000 - 12500, 8)
PAT_PER_YEAR, PAT_P, PAT_R = two_amounts(1120, 3, 1200, 5)
PAT_TRIPLE = n_times_years(3, 2, 5)
PAT_RATE_CHANGE = find_principal(360, 2, 3)
PAT_SPLIT = Fraction(8 * 10000 - 65000, 8 - 5)             # 5x + 8(10,000 − x) = 65,000
assert (PAT_T, PAT_PER_YEAR, PAT_P, PAT_R, PAT_TRIPLE, PAT_RATE_CHANGE, PAT_SPLIT) == (Fraction("2.5"), 40, 1000, 4, 10, 6000, 5000)
PATTERNS_A = [("Find R from P and A", "₹40,000 becomes ₹52,800 in 4 years", "I = A − P, then R = 100I/(PT)", f"{HOOK_R}%"),
              ("Find T", "When does ₹12,500 become ₹15,000 at 8%?", "T = 100 × 2,500/(12,500 × 8)", f"{dec(PAT_T)} years"),
              ("Two amounts", "₹1,120 in 3 years, ₹1,200 in 5 years", f"₹{PAT_PER_YEAR} a year; P = 1,120 − 120",
               f"P = {rs(PAT_P)}, R = {PAT_R}%")]
PATTERNS_B = [("Becomes n times", "Doubles in 5 years; when does it triple?", "Doubling adds P in 5 years; tripling adds 2P",
               f"{PAT_TRIPLE} years"),
              ("Rate change", "2% higher rate gives ₹360 more in 3 years; find P", "P × 2 × 3/100 = 360", rs(PAT_RATE_CHANGE)),
              ("Split investment", "₹10,000 split at 5% and 8%; one year's interest ₹650", "5x + 8(10,000 − x) = 65,000",
               f"{rs(PAT_SPLIT)} each")]

# ---- traps: (title, question, wrong, right, rule) ----
T1_WRONG = find_rate(LOAN, REPAID, YEARS)
T3_WRONG, T3_RIGHT = Fraction(4 * 100, 15), Fraction((4 - 1) * 100, 15)
assert T1_WRONG == 33 and T3_RIGHT == 20 and Fraction(5) * Fraction("1.5") == Fraction("7.5")
TRAPS = [("Trap 1  ·  the total used as interest", "₹40,000 becomes ₹52,800 in 4 years.  Rate?",
          f"I = 52,800  →  {T1_WRONG}%", f"I = {HOOK_I:,}  →  {HOOK_R}%",
          "Subtract the principal first:  I = A − P."),
         ("Trap 2  ·  “triples” taken as 1.5 × “doubles”", "A sum doubles in 5 years at simple interest.  When does it triple?",
          "1.5 × 5  =  7.5 years", f"{PAT_TRIPLE} years",
          "Doubling: I = P.  Tripling: I = 2P.  Twice the interest takes twice the time."),
         ("Trap 3  ·  “becomes n times” read as n × 100", "A sum becomes 4 times itself in 15 years.  Rate?",
          f"4 × 100 ÷ 15  ≈  {float(T3_WRONG):.1f}%", f"(4 − 1) × 100 ÷ 15  =  {T3_RIGHT}%",
          "The interest is (n − 1) times P, not n times.")]

# ---- checkpoint ----
CP_I = simple_interest(6000, 5, 4)
assert CP_I == 1200 == 60 * 20

# ---- practice (answers computed) ----
PRACTICE_A = [("L1", "In what time will ₹8,000 earn ₹1,200 of simple interest at 5% per year?"),
              ("L1", "What sum earns ₹900 of simple interest in 3 years at 6% per year?"),
              ("L1", "A sum doubles itself in 5 years at simple interest.  What is the rate?"),
              ("L2", "A sum becomes ₹7,200 in 2 years and ₹8,100 in 3 years at SI.  Find the sum and the rate."),
              ("L2", "At what rate per year will ₹5,000 earn ₹1,500 in 4 years?"),
              ("L2", "In how many years will ₹12,500 amount to ₹15,000 at 8% simple interest?")]
PRACTICE_B = [("L3", "A sum becomes 4 times itself in 15 years at SI.  In how many years will it become 7 times itself?"),
              ("L3", "₹10,000 is split into two parts at 5% and 8% SI.  Total interest in one year is ₹650.  Find the parts."),
              ("L3", "If the rate had been 2% higher, a sum would have earned ₹360 more in 3 years.  Find the sum.")]
A1 = find_time(8000, 1200, 5)
A2 = find_principal(900, 6, 3)
A3 = Fraction((2 - 1) * 100, 5)
A4_PER_YEAR, A4_P, A4_R = two_amounts(7200, 2, 8100, 3)
A5 = find_rate(5000, 1500, 4)
A7 = n_times_years(7, 4, 15)
assert (A1, A2, A3, A4_PER_YEAR, A4_P, A4_R, A5, A7) == (3, 5000, 20, 900, 5400, Fraction(50, 3), Fraction("7.5"), 30)
assert A4_P + 3 * A4_PER_YEAR == 8100
ANSWERS_A = [("T = 100 × 1,200 ÷ (8,000 × 5)", f"{A1} years"),
             ("P = 100 × 900 ÷ (6 × 3)", rs(A2)),
             ("R = (2 − 1) × 100 ÷ 5", f"{A3}% per year"),
             ("one year adds 900;  P = 7,200 − 1,800;  R = 900/5,400", f"{rs(A4_P)};  16 2/3 %"),
             ("R = 100 × 1,500 ÷ (5,000 × 4)", f"{dec(A5)}% per year")]
ANSWERS_B = [("I = 2,500;  T = 100 × 2,500 ÷ (12,500 × 8)", f"{dec(PAT_T)} years"),
             ("4 times: interest 3P in 15 years, so P every 5 years;  7 times needs 6P", f"{A7} years"),
             ("0.05x + 0.08(10,000 − x) = 650;  800 − 0.03x = 650", f"{rs(PAT_SPLIT)} and {rs(10000 - PAT_SPLIT)}"),
             ("only the extra 2% matters:  P × 2 × 3 ÷ 100 = 360", rs(PAT_RATE_CHANGE))]

OBJECTIVES = [("Derive and use SI = PRT/100", "built up from the meaning of R%"),
              ("Rearrange it", "to find the principal, the rate or the time"),
              ("Use two amounts at two times", "to find both P and R")]
BUILD = [("Start from the meaning of R%", "R% per year  =  ₹R for every ₹100, every year"),
         ("Scale to the principal", "P = P/100 hundreds   →   one year's interest = (P/100) × R = PR/100"),
         ("Repeat for T years", "on the original principal only: every year adds the same PR/100")]
LENS = [("Recognition cue", "two amounts at two times  →  take the difference first: one year's interest"),
        ("Target time", "30 to 45 seconds"),
        ("Sanity check", "amount after 2T years  =  P + 2 × (interest for T years)")]


def two_line_blocks(items, color, detail_size=SMALL):
    """Numbered blocks: a bold title line with a detail line under it.  block[0] = title line, block[1] = detail line."""
    blocks = VGroup()
    for i, (title, detail) in enumerate(items):
        top = VGroup(pill(str(i + 1), color, size=SMALL), text(title, LABEL, color, BOLD)).arrange(RIGHT, buff=0.3)
        indent = Rectangle(width=0.75, height=0.1).set_stroke(width=0)                    # never shown
        blocks.add(VGroup(top, VGroup(indent, text(detail, detail_size, INK)).arrange(RIGHT, buff=0))
                   .arrange(DOWN, buff=0.16, aligned_edge=LEFT))
    return blocks.arrange(DOWN, buff=0.5, aligned_edge=LEFT)


def given_chips(p, r, t):
    return VGroup(pill(f"P = {p}", "#4FC3F7", size=LABEL), pill(f"R = {r}", "#FFB74D", size=LABEL),
                  pill(f"T = {t}", "#CE93D8", size=LABEL)).arrange(RIGHT, buff=0.35)


class SimpleInterestFindingPRTVideo(LMSScene):
    lesson_title = "Simple Interest: Finding P, R, T"

    def construct(self):
        self.camera.background_color = BG

        self.intro()
        self.hook()
        self.objectives()
        self.why_this_matters()
        self.build_the_formula()
        self.straight_line()
        self.rearrange()
        self.analogy()
        self.hook_solved()
        self.second_example()
        self.exam_patterns()
        self.traps()
        self.checkpoint()
        self.practice()
        self.answers()
        self.exam_lens()
        self.summary()

    # ---------------------------------------------------- scene helpers --

    def clear_stage(self, run_time=0.6):
        """Scene transition: fade out everything on screen."""
        if self.mobjects:
            self.play(FadeOut(Group(*self.mobjects)), run_time=run_time)

    def card(self, content, width=None, height=None, color=MUTED, pad=0.3):
        """Container-aware card (grows to content; a fixed height is a minimum)."""
        # A fixed height is a minimum: the card grows to its content and never
        # shrinks text (shrinking pushed labels below the readable minimum).
        if width is not None:
            fit_width(content, width - 2 * pad)
        w = width if width is not None else content.width + 2 * pad
        h = max(height or 0, content.height + 2 * pad)
        box = RoundedRectangle(corner_radius=0.18, width=w, height=h, stroke_color=color,
                               stroke_width=2.5, fill_color=PANEL, fill_opacity=1)
        box.move_to(content)
        self.validator.check_fit(content, box, margin=0.1)
        return VGroup(box, content)

    def caption(self, s, color=INK):
        """One-line keyword caption in a fixed-width bar at the bottom of the frame."""
        t = fitted_text(s, SAFE_W - 1.0, BODY, color)
        bar = self.card(t, width=SAFE_W - 0.4, height=t.height + 0.9)
        return bar.move_to(UP * BOTTOM_Y)

    def breadcrumb(self, *parts):
        """Silent 'where are we' trail: Module > Lesson > Topic."""
        colors = [DIFF, "#F48FB1", RATIO]
        items = []
        for i, p in enumerate(parts):
            if i:
                items.append(text("›", LABEL, MUTED))
            items.append(pill(p, colors[i % 3], size=SMALL))
        return fit_width(VGroup(*items).arrange(RIGHT, buff=0.25), SAFE_W)

    def verdict_card(self, good, s, width):
        """A ✓ (green) or ✗ (red) card with fitted text."""
        color = GOOD if good else BAD
        body = VGroup(text("✓" if good else "✗", 34, color, BOLD),
                      fitted_text(s, width - 1.3, SMALL, color, max_lines=2)).arrange(RIGHT, buff=0.25)
        return self.card(body, width=width, height=1.2, color=color)

    def countdown(self, seconds):
        """Thinking-time ring that empties over ``seconds`` (for pause_after)."""
        centre = RIGHT * (FRAME_W / 2 - SAFE - 0.5) + DOWN * (FRAME_H / 2 - SAFE - 0.5)
        tracker = ValueTracker(1.0)
        track = Circle(radius=0.38, stroke_color=MUTED, stroke_width=3).move_to(centre)
        ring = always_redraw(lambda: Arc(radius=0.38, start_angle=PI / 2, angle=max(TAU * tracker.get_value(), 1e-3),
                                         arc_center=centre, stroke_color=FOCUS, stroke_width=8))
        label = pill("Think", FOCUS).next_to(track, LEFT, buff=0.3)
        self.play(FadeIn(track), FadeIn(label), run_time=0.3)
        self.add(ring)
        self.play(tracker.animate.set_value(0.0), run_time=max(0.5, seconds - 0.3), rate_func=linear)
        self.remove(ring)
        self.play(FadeOut(track), FadeOut(label), run_time=0.3)

    def table_rows(self, header, rows, widths, size=SMALL):
        """A small table as a VGroup of rows (header first). Each cell is fitted
        to its column and left-aligned at the column's left edge."""
        lefts, x = [], -sum(widths) / 2
        for w in widths:
            lefts.append(x)
            x += w
        out = VGroup()
        for i, cells in enumerate([header] + rows):
            color, weight = (FOCUS, BOLD) if i == 0 else (INK, NORMAL)
            row = VGroup(*[fitted_text(c, w - 0.3, size, color, weight, max_lines=2) for c, w in zip(cells, widths)])
            for cell, left in zip(row, lefts):
                cell.set_x(left + cell.width / 2)
            out.add(row)
        out.arrange(DOWN, buff=0.3)
        for row in out:                      # arrange() recentres rows; restore column alignment
            for cell, left in zip(row, lefts):
                cell.set_x(left + cell.width / 2)
        return out

    def recap_card(self, title, rows):
        """'Recap Card': term on the left, one-line meaning on the right."""
        table = self.table_rows([title, "what it means"], rows, [3.4, 8.0], size=LABEL)
        table[0][0].set_color(INK)
        card = self.card(table, width=SAFE_W - 0.4)
        return card, table

    def no_overlap(self, *mobs, gap=0.05):
        """Layout guard: the bounding boxes of the given blocks must not intersect
        (checked before anything is played, so a layout change can't silently overlap)."""
        for i, a in enumerate(mobs):
            for b in mobs[i + 1:]:
                apart_x = a.get_right()[0] + gap <= b.get_left()[0] or b.get_right()[0] + gap <= a.get_left()[0]
                apart_y = a.get_bottom()[1] >= b.get_top()[1] + gap or b.get_bottom()[1] >= a.get_top()[1] + gap
                if not (apart_x or apart_y):
                    raise ValueError(f"overlapping blocks: {a.__class__.__name__} at {a.get_center()} and "
                                     f"{b.__class__.__name__} at {b.get_center()}")

    # ----------------------------------------------------- pinned panel --
    PIN_W = 3.4                                   # width of the pinned reference panel

    def pin(self, card, corner=UR):
        """Animation: park a reference card in a corner. It stays on screen across scenes
        (``clear_stage`` leaves it) until ``unpin``."""
        fit_within(card, self.PIN_W, SAFE_H - 1.0)
        card.to_corner(corner, buff=SAFE)
        self.pinned = card
        return FadeIn(card, shift=LEFT * 0.2)

    def unpin(self):
        card, self.pinned = getattr(self, "pinned", None), None
        return FadeOut(card) if card is not None else Wait(0.01)

    def free_area(self):
        """(centre_x, width) of the stage left free by the pinned panel (full safe width if none)."""
        card = getattr(self, "pinned", None)
        left = -FRAME_W / 2 + SAFE
        right = (card.get_left()[0] - 0.3) if card is not None else FRAME_W / 2 - SAFE
        return (left + right) / 2, right - left

    def place_free(self, mob, y=None):
        """Fit ``mob`` into the free area (beside the pinned panel) and centre it there."""
        cx, w = self.free_area()
        fit_width(mob, w)
        mob.set_x(cx)
        if y is not None:
            mob.set_y(y)
        if getattr(self, "pinned", None) is not None:
            self.no_overlap(mob, self.pinned)
        return mob

    def clear_stage(self, run_time=0.6):
        """Scene transition: fade out everything except the pinned panel."""
        keep = getattr(self, "pinned", None)
        mobs = [m for m in self.mobjects if m is not keep]
        if mobs:
            self.play(FadeOut(Group(*mobs)), run_time=run_time)

    def steps_pin(self, title, steps):
        """A compact numbered-steps card for the pinned panel. ``steps`` = [(text, colour), ...]."""
        rows = VGroup(*[VGroup(pill(str(i + 1), c, size=SMALL), text(t, SMALL, INK)).arrange(RIGHT, buff=0.2)
                        for i, (t, c) in enumerate(steps)]).arrange(DOWN, buff=0.18, aligned_edge=LEFT)
        return self.card(VGroup(text(title, SMALL, MUTED, BOLD), rows).arrange(DOWN, buff=0.2, aligned_edge=LEFT),
                         color=FOCUS)

    def pin_step(self, i, color=FOCUS):
        """Animation: light up row i of the pinned steps card."""
        return Indicate(self.pinned[1][1][i], color=color, scale_factor=1.08)

    def heading(self, s, color=FOCUS):
        head = pill(s, color, size=LABEL)
        return head.move_to(UP * (CARD_TOP - head.height / 2))

    def stack(self, head, items, buff=0.45, top=0.5, align=None):
        """Stack ``items`` under ``head`` (fitted to the frame, guarded against overlap).  Returns the group."""
        body = VGroup(*items)
        if align is None:
            body.arrange(DOWN, buff=buff)
        else:
            body.arrange(DOWN, buff=buff, aligned_edge=align)
        fit_within(body, SAFE_W, SAFE_H - head.height - top - 0.3)
        body.next_to(head, DOWN, buff=top)
        self.no_overlap(head, *items)
        self.validator.check_in_frame(VGroup(head, body))
        return body

    def placed_table(self, head, header, rows, widths, size=SMALL, room=0.8):
        """A table fitted under ``head``.  Returns (table, body rows)."""
        table = self.table_rows(header, rows, widths, size=size)
        fit_within(table, SAFE_W, SAFE_H - head.height - room)
        table.next_to(head, DOWN, buff=0.45)
        self.no_overlap(head, table)
        self.no_overlap(*table)
        self.validator.check_in_frame(VGroup(head, table))
        return table, table[1:]

    def verdict_pair(self, wrong, right):
        """A ✗ card and a ✓ card of the same height, side by side."""
        contents = [VGroup(text(mark, 34, c, BOLD), text(s, LABEL, c)).arrange(RIGHT, buff=0.25)
                    for mark, s, c in [("✗", wrong, BAD), ("✓", right, GOOD)]]
        tallest = max(c.height for c in contents) + 0.6
        return VGroup(*[self.card(c, width=6.2, height=tallest, color=col) for c, col in zip(contents, (BAD, GOOD))])\
            .arrange(RIGHT, buff=0.5)

    def show_trap(self, trap):
        """Lay out one trap.  Returns (head, question, wrong card, right card, rule)."""
        title, question, wrong, right, rule = trap
        head = self.heading(title, BAD)
        q = fitted_text(question, SAFE_W - 1.0, BODY, INK, NORMAL, max_lines=2)
        pair = self.verdict_pair(wrong, right)
        rule_pill = fit_width(pill(rule, FOCUS, size=LABEL), SAFE_W)
        self.stack(head, [q, pair, rule_pill], buff=0.7, top=0.8)
        self.no_overlap(pair[0], pair[1])
        return head, q, pair[0], pair[1], rule_pill

    def solve_steps(self, steps, color=WORD):
        """Numbered solution rows.  Each row = (number chip, working, result)."""
        rows = VGroup(*[VGroup(pill(str(i + 1), color, size=SMALL), text(what, LABEL, INK), text(result, LABEL, GOOD, BOLD))
                        .arrange(RIGHT, buff=0.3) for i, (what, result) in enumerate(steps)])
        return rows.arrange(DOWN, buff=0.5, aligned_edge=LEFT)

    # ================================================== 0. INTRO ==========
    # Not the first video: silent breadcrumb, a one-line recap of Video 1, then today's topic.

    def intro(self):
        self.scene_start("S00_intro", title="Intro")

        crumb = self.breadcrumb("Quantitative Aptitude", "Lesson 11 · Simple & Compound Interest", "Video 2 of 7")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        recap = VGroup(text("last video", SMALL, MUTED),
                       VGroup(pill("P  R  T  I  A   ·   A = P + I", WORD, size=LABEL), pill("match the units first", FOCUS, size=LABEL))
                       .arrange(RIGHT, buff=0.4)).arrange(DOWN, buff=0.25)
        title = text("Simple Interest: Finding P, R, T", TITLE, INK, BOLD)
        today = text("today: one formula, rearranged for whichever quantity is hidden", LABEL, FOCUS)
        block = VGroup(recap, title, today).arrange(DOWN, buff=0.7)
        fit_within(block, SAFE_W, SAFE_H - crumb.height - 0.9)
        block.next_to(crumb, DOWN, buff=0.7)
        self.no_overlap(crumb, recap, title, today)
        self.no_overlap(*recap[1])
        self.validator.check_in_frame(VGroup(crumb, block))

        n = self.narrate(
            id="intro_01",
            text="In the last video, you met the five words of interest, and the habit of matching units.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.at_word(n, "five")
        self.play(FadeIn(recap[0]), FadeIn(recap[1][0], shift=UP * 0.1))
        self.at_word(n, "matching")
        self.play(FadeIn(recap[1][1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="intro_02",
            text="Today: simple interest, and how to find the principal, the rate or the time.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "simple")
        self.play(FadeIn(title, shift=UP * 0.1))
        self.at_word(n, "find")
        self.play(FadeIn(today, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_intro")

    # =================================================== 1. HOOK ==========

    def hook(self):
        self.scene_start("S01_hook", title="Hook")

        head = self.heading("A repayment slip")
        lines = VGroup(VGroup(text("Loan taken", LABEL, MUTED), text(rs(LOAN), BODY, INK, BOLD)).arrange(RIGHT, buff=0.5),
                       VGroup(text(f"Repaid after {YEARS} years", LABEL, MUTED), text(rs(REPAID), BODY, INK, BOLD))
                       .arrange(RIGHT, buff=0.5),
                       VGroup(text("Interest", LABEL, MUTED), text(f"simple: on the original {rs(LOAN)} only", LABEL, WORD))
                       .arrange(RIGHT, buff=0.5),
                       VGroup(text("Rate", LABEL, MUTED), text("?  % per year", BODY, FOCUS, BOLD)).arrange(RIGHT, buff=0.5))\
            .arrange(DOWN, buff=0.4, aligned_edge=LEFT)
        slip = self.card(lines, width=9.0, color=WORD, pad=0.45)
        ten = pill("can you find it in about 10 seconds?", FOCUS, size=LABEL)
        self.stack(head, [slip, ten], buff=0.6, top=0.6)

        n = self.narrate(
            id="hook_01",
            text="Four years ago, a relative lent you forty thousand rupees for your laptop and a certification course.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Four")
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(slip[0]))
        self.at_word(n, "forty")
        self.play(FadeIn(lines[0], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_02",
            text="You've now repaid fifty-two thousand eight hundred rupees in total, and the interest was simple: charged on "
                 "the original forty thousand only.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "repaid")
        self.play(FadeIn(lines[1], shift=RIGHT * 0.2))
        self.at_word(n, "simple")
        self.play(FadeIn(lines[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_03",
            text="Nobody ever told you the rate. Can you work it out in about ten seconds?",
            voice="default",
            subtitle=True,
            pause_after=10.0,
        )
        self.at_word(n, "rate")
        self.play(FadeIn(lines[3], shift=RIGHT * 0.2))
        self.at_word(n, "ten")
        self.play(FadeIn(ten, shift=UP * 0.1))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        self.clear_stage()
        self.scene_end("S01_hook")

    # ============================================== 2. OBJECTIVES ==========

    def objectives(self):
        self.scene_start("S02_objectives", title="Objectives")

        head = self.heading("By the end of this video")
        blocks = two_line_blocks(OBJECTIVES, WORD)
        self.stack(head, list(blocks), buff=0.55, top=0.7, align=LEFT)

        n = self.narrate(
            id="obj_01",
            text="By the end of this video, you will be able to do three things.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "three")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="obj_02",
            text="First, derive and use the formula: simple interest equals P R T over a hundred.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "derive")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "equals")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="obj_03",
            text="Second, rearrange it to find the principal, the rate or the time.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "rearrange")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "principal")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="obj_04",
            text="Third, use two amounts at two different times to find both P and R.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "amounts")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "both")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_objectives")

    # ========================================== 3. WHY THIS MATTERS ==========

    def why_this_matters(self):
        self.scene_start("S03_why_this_matters", title="Why This Matters")

        head = self.heading("Why this matters")
        four = VGroup(*[pill(q, WORD, size=BODY) for q in ["I", "P", "R", "T"]]).arrange(RIGHT, buff=0.4)
        hide = text("four quantities: an exam can hide any one of them", LABEL, INK)
        tools = VGroup(pill("rearrange the formula", RATIO, size=LABEL), pill("see a straight line", GOOD, size=LABEL))\
            .arrange(RIGHT, buff=0.5)
        costume = text("every simple-interest question: the same question in a different costume", LABEL, FOCUS)
        self.stack(head, [four, hide, tools, costume], buff=0.6, top=0.7)

        n = self.narrate(
            id="why_01",
            text="Simple interest has four quantities, and an exam can hide any one of them.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "four")
        self.play(FadeIn(head, shift=DOWN * 0.2), LaggedStart(*[FadeIn(q, scale=0.7) for q in four], lag_ratio=0.15))
        self.at_word(n, "hide")
        self.play(FadeIn(hide, shift=UP * 0.1), LaggedStart(*[Indicate(q, color=FOCUS, scale_factor=1.2) for q in four],
                                                             lag_ratio=0.3))
        self.wait_for_narration(n)

        n = self.narrate(
            id="why_02",
            text="Once you can rearrange the formula and see simple interest as a straight line, every simple-interest question "
                 "is the same question in a different costume.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "rearrange")
        self.play(FadeIn(tools[0], shift=UP * 0.1))
        self.at_word(n, "straight")
        self.play(FadeIn(tools[1], shift=UP * 0.1))
        self.at_word(n, "costume")
        self.play(FadeIn(costume, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_why_this_matters")

    # ================================ 4. CONCEPT: BUILDING THE FORMULA ==========

    def build_the_formula(self):
        self.scene_start("S04_build_the_formula", title="Concept - Building SI = PRT/100")

        head = self.heading("Where the formula comes from")
        blocks = two_line_blocks(BUILD, WORD)
        formula = pill("Over T years:   I = P × R × T / 100", GOOD, size=BODY)
        self.stack(head, [*blocks, formula], buff=0.5, top=0.6, align=LEFT)

        n = self.narrate(
            id="build_01",
            text="Start from the meaning of R percent. R percent per year means R rupees for every hundred rupees, every year.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "meaning")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "rupees", occurrence=1)
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="build_02",
            text="Scale to the principal. P rupees is P over a hundred hundreds, so one year's interest is P over a hundred, "
                 "times R: P R over a hundred.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Scale")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "hundreds")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="build_03",
            text="Repeat for T years. Simple interest is charged on the original principal only, so each year adds the same P "
                 "R over a hundred.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Repeat")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "original")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="build_04",
            text="Over T years, I equals P R T over a hundred.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "equals")
        self.play(FadeIn(formula, scale=1.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_build_the_formula")

    # ==================================== 5. CONCEPT: A STRAIGHT LINE ==========

    def straight_line(self):
        self.scene_start("S05_straight_line", title="Concept - See It as a Straight Line")

        head = self.heading("See it as a straight line")
        labels = ["P"] + [f"P + {'' if t == 1 else t}I" for t in range(1, len(LINE))]
        cols = VGroup(*[VGroup(text(f"{v:,}", SMALL, INK),
                               Rectangle(width=1.1, height=1.6 * v / LINE_P, color=WORD, fill_color=WORD, fill_opacity=0.45),
                               text(label, SMALL, WORD, BOLD)).arrange(DOWN, buff=0.14) for v, label in zip(LINE, labels)])\
            .arrange(RIGHT, buff=0.7, aligned_edge=DOWN)
        note = text(f"example: {rs(LINE_P)} at {LINE_R}%   ·   I = one year's interest = {rs(LINE_STEP)}", SMALL, MUTED)
        ap = pill("an arithmetic progression: the same step every year", RATIO, size=LABEL)
        equal = text("equal time gaps  →  equal interest", LABEL, GOOD, BOLD)
        self.stack(head, [cols, note, ap, equal], buff=0.35, top=0.45)
        self.no_overlap(*cols)

        n = self.narrate(
            id="line_01",
            text="See it as a straight line. The amount grows by the same step every year.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "line")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "step")
        self.play(LaggedStart(*[FadeIn(c, shift=UP * 0.2) for c in cols], lag_ratio=0.25), FadeIn(note), run_time=1.6)
        self.wait_for_narration(n)

        n = self.narrate(
            id="line_02",
            text="P, then P plus one year's interest, then P plus two years' interest, and so on: an arithmetic progression.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "plus", occurrence=1)
        self.play(LaggedStart(*[Indicate(c[2], color=FOCUS, scale_factor=1.2) for c in cols], lag_ratio=0.35), run_time=1.8)
        self.at_word(n, "arithmetic")
        self.play(FadeIn(ap, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="line_03",
            text="That is why equal time gaps always give equal interest.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "equal", occurrence=1)
        self.play(FadeIn(equal, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_straight_line")

    # ============================ 6. CONCEPT: REARRANGE + FORMULA BOX ==========

    def rearrange(self):
        self.scene_start("S06_rearrange", title="Concept - Rearrange Once, Use Forever (Formula Box)")

        head = self.heading("Rearrange once, use forever")
        base = text("100 × I  =  P × R × T", BODY, INK, BOLD)
        three = VGroup(pill("P = 100I / (R × T)", WORD, size=LABEL), pill("R = 100I / (P × T)", RATIO, size=LABEL),
                       pill("T = 100I / (P × R)", "#CE93D8", size=LABEL)).arrange(RIGHT, buff=0.4)
        extra = VGroup(text("Formula box: two more lines", SMALL, GOOD, BOLD),
                       text("a sum becomes n times in T years:   R × T = (n − 1) × 100", LABEL, INK),
                       text("two amounts:   interest per year = difference of amounts ÷ difference of times", LABEL, INK))\
            .arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        box = self.card(extra, width=SAFE_W - 0.4, color=GOOD)
        self.stack(head, [base, three, box], buff=0.55, top=0.6)
        self.no_overlap(*three)

        n = self.narrate(
            id="rearr_01",
            text="Rearrange once, use forever. From one hundred times I equals P times R times T, any unknown is one hundred "
                 "I divided by the other two.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Rearrange")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "equals")
        self.play(FadeIn(base, shift=UP * 0.1))
        self.at_word(n, "divided")
        self.play(LaggedStart(*[FadeIn(p, shift=UP * 0.1) for p in three], lag_ratio=0.25))
        self.wait_for_narration(n)

        n = self.narrate(
            id="rearr_02",
            text="Two more lines for the formula box. If a sum becomes n times itself in T years, R times T equals n minus one, "
                 "times a hundred.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "box")
        self.play(FadeIn(box[0]), FadeIn(extra[0]))
        self.at_word(n, "becomes")
        self.play(FadeIn(extra[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="rearr_03",
            text="And with two amounts, the interest per year is the difference of the amounts, divided by the difference of the "
                 "times.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "two")
        self.play(FadeIn(extra[2], shift=RIGHT * 0.2))
        self.at_word(n, "divided")
        self.play(Indicate(extra[2], color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_rearrange")

    # ============================================== 7. THE ANALOGY ==========

    def analogy(self):
        self.scene_start("S07_analogy", title="The Analogy - A Fixed Rent")

        head = self.heading("Think of a fixed rent")
        slips = VGroup(*[VGroup(text(year, LABEL, MUTED), text("₹5,000 a month", LABEL, INK, BOLD)).arrange(RIGHT, buff=0.4)
                         for year in ["Year 1", "Year 10"]]).arrange(RIGHT, buff=1.2)
        tied = VGroup(text("the rent is tied to the flat", LABEL, WORD, BOLD), text("not to what you have already paid", LABEL, MUTED))\
            .arrange(RIGHT, buff=0.5)
        same = pill("simple interest is tied to the original principal, the same way", GOOD, size=LABEL)
        stops = VGroup(text("Where the analogy stops", LABEL, BAD, BOLD),
                       text("rent stops when you leave", LABEL, MUTED),
                       text("interest keeps accruing on the full principal until it is repaid", LABEL, INK))\
            .arrange(DOWN, buff=0.22)
        self.stack(head, [slips, tied, same, stops], buff=0.55, top=0.6)
        self.no_overlap(*slips)
        self.no_overlap(*tied)

        n = self.narrate(
            id="analogy_01",
            text="Think of a fixed rent.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "fixed")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_02",
            text="If a flat costs five thousand rupees a month, you pay five thousand in the first year and five thousand in "
                 "the tenth.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "first")
        self.play(FadeIn(slips[0], shift=UP * 0.1))
        self.at_word(n, "tenth")
        self.play(FadeIn(slips[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_03",
            text="The rent is tied to the flat, not to what you have already paid.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "tied")
        self.play(FadeIn(tied[0], shift=UP * 0.1))
        self.at_word(n, "not")
        self.play(FadeIn(tied[1], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_04",
            text="Simple interest is tied to the original principal in exactly the same way.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "original")
        self.play(FadeIn(same, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_05",
            text="Where the analogy stops: rent stops when you leave.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "analogy")
        self.play(FadeIn(stops[0], shift=UP * 0.1))
        self.at_word(n, "leave")
        self.play(FadeIn(stops[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_06",
            text="Interest keeps accruing on the full principal until the principal itself is repaid.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "accruing")
        self.play(FadeIn(stops[2], shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S07_analogy")

    # ================================ 8. WORKED EXAMPLE: CLOSING THE HOOK ==========

    def hook_solved(self):
        self.scene_start("S08_hook_solved", title="Worked Example - Closing the Hook")

        head = self.heading(f"The slip:  {rs(LOAN)}  →  {rs(REPAID)} in {YEARS} years")
        steps = self.solve_steps([
            (f"Interest  =  52,800 − 40,000", f"=  {rs(HOOK_I)} over {YEARS} years"),
            (f"R  =  100 × 12,800 ÷ (40,000 × {YEARS})", f"=  {HOOK_R}% per year"),
            (f"Check:  {HOOK_R}% of {rs(LOAN)} = {rs(HOOK_YEARLY)} a year", f"× {YEARS}  =  {rs(HOOK_YEARLY * YEARS)}")])
        rate = pill(f"the hidden rate:  {HOOK_R}% per year", GOOD, size=BODY)
        self.stack(head, [steps, rate], buff=0.8, top=0.8)
        self.no_overlap(*steps)

        n = self.narrate(
            id="solved_01",
            text="First, separate the interest: fifty-two thousand eight hundred minus forty thousand is twelve thousand eight "
                 "hundred rupees, over four years.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "minus")
        self.play(FadeIn(steps[0][:2], shift=RIGHT * 0.1))
        self.at_word(n, "twelve")
        self.play(FadeIn(steps[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_02",
            text="Then R is one hundred times twelve thousand eight hundred, divided by forty thousand times four, which is "
                 "exactly eight percent per year.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "divided")
        self.play(FadeIn(steps[1][:2], shift=RIGHT * 0.1))
        self.at_word(n, "exactly")
        self.play(FadeIn(steps[1][2], shift=LEFT * 0.1), FadeIn(rate, scale=1.05))
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_03",
            text="Check: eight percent of forty thousand is three thousand two hundred a year, and times four gives twelve "
                 "thousand eight hundred.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Check")
        self.play(FadeIn(steps[2][:2], shift=RIGHT * 0.1))
        self.at_word(n, "times")
        self.play(FadeIn(steps[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S08_hook_solved")

    # ============================ 9. SECOND WORKED EXAMPLE: TWO AMOUNTS ==========

    def second_example(self):
        self.scene_start("S09_second_example", title="A Second Worked Example - Two Amounts")

        head = self.heading("Two amounts at two times  ·  simple interest")
        given = VGroup(pill("₹8,400 in 4 years", WORD, size=LABEL), pill("₹9,600 in 6 years", RATIO, size=LABEL),
                       pill("find the sum and the rate", FOCUS, size=LABEL)).arrange(RIGHT, buff=0.4)
        steps = self.solve_steps([
            ("extra 2 years:  9,600 − 8,400 = ₹1,200", f"→  {rs(EX_PER_YEAR)} a year"),
            (f"4 years of interest = {rs(EX_PER_YEAR * 4)}", f"P  =  8,400 − 2,400  =  {rs(EX_P)}"),
            ("R  =  600 ÷ 6,000 × 100", f"=  {EX_R}% per year")])
        self.stack(head, [given, steps], buff=0.8, top=0.8)
        self.no_overlap(*given)
        self.no_overlap(*steps)

        n = self.narrate(
            id="two_01",
            text="A sum becomes eight thousand four hundred rupees in four years, and nine thousand six hundred in six years, "
                 "at simple interest. Find the sum and the rate.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "eight")
        self.play(FadeIn(given[0], shift=UP * 0.1))
        self.at_word(n, "nine")
        self.play(FadeIn(given[1], shift=UP * 0.1))
        self.at_word(n, "Find")
        self.play(FadeIn(given[2], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="two_02",
            text="The extra two years earned nine thousand six hundred minus eight thousand four hundred, which is twelve "
                 "hundred rupees, so the interest per year is six hundred.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "minus")
        self.play(FadeIn(steps[0][:2], shift=RIGHT * 0.1))
        self.at_word(n, "per")
        self.play(FadeIn(steps[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="two_03",
            text="Four years of interest is two thousand four hundred, so P is eight thousand four hundred minus two thousand "
                 "four hundred: six thousand rupees.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Four")
        self.play(FadeIn(steps[1][:2], shift=RIGHT * 0.1))
        self.at_word(n, "six")
        self.play(FadeIn(steps[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="two_04",
            text="And R is six hundred divided by six thousand, times a hundred: ten percent per year.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "divided")
        self.play(FadeIn(steps[2][:2], shift=RIGHT * 0.1))
        self.at_word(n, "ten")
        self.play(FadeIn(steps[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S09_second_example")

    # ============================================ 10. EXAM PATTERNS ==========

    def pattern_table(self, head, patterns):
        table, rows = self.placed_table(head, ["Pattern", "Example", "Method", "Answer"], [list(p) for p in patterns],
                                        [2.4, 4.4, 3.8, 2.6], room=1.2)
        for row in rows:
            row[0].set_color(WORD)
            row[3].set_color(GOOD)
        return table, rows

    def exam_patterns(self):
        self.scene_start("S10_exam_patterns", title="Exam Patterns - How This Is Asked")

        head = self.heading("Exam patterns  ·  1 to 3 of 6")
        table, rows = self.pattern_table(head, PATTERNS_A)

        n = self.narrate(
            id="patterns_01",
            text="Exams ask this in six ways.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "six")
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.wait_for_narration(n)

        n = self.narrate(
            id="patterns_02",
            text="Find the rate from the principal and the amount: subtract first, then use the formula. That was the hook: "
                 "eight percent.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "rate")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "subtract")
        self.play(FadeIn(rows[0][2], shift=RIGHT * 0.2))
        self.at_word(n, "eight")
        self.play(FadeIn(rows[0][3], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="patterns_03",
            text="Find the time: twelve thousand five hundred becomes fifteen thousand at eight percent in two point five years.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "time")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "point")
        self.play(FadeIn(rows[1][2:], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="patterns_04",
            text="Two amounts: eleven hundred and twenty in three years and twelve hundred in five years means forty rupees a "
                 "year, so P is one thousand and R is four percent.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "amounts")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "forty")
        self.play(FadeIn(rows[2][2], shift=RIGHT * 0.2))
        self.at_word(n, "four")
        self.play(FadeIn(rows[2][3], shift=RIGHT * 0.2))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Exam patterns  ·  4 to 6 of 6")
        table, rows = self.pattern_table(head, PATTERNS_B)

        n = self.narrate(
            id="patterns_05",
            text="Becomes n times: if a sum doubles in five years, tripling adds twice the interest, so it takes ten years.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "Becomes")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "tripling")
        self.play(FadeIn(rows[0][2], shift=RIGHT * 0.2))
        self.at_word(n, "ten")
        self.play(FadeIn(rows[0][3], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="patterns_06",
            text="A rate change: a two percent higher rate gives three hundred and sixty rupees more in three years, so P is "
                 "six thousand.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "change")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "so")
        self.play(FadeIn(rows[1][2:], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="patterns_07",
            text="A split investment: ten thousand split at five and eight percent earns six hundred and fifty in a year, so "
                 "each part is five thousand.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "split", occurrence=1)
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "each")
        self.play(FadeIn(rows[2][2:], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S10_exam_patterns")

    # ================================ 11. TRAPS AND CONFUSING QUESTIONS ==========

    def traps(self):
        self.scene_start("S11_traps", title="Traps and Confusing Questions")

        head, q, wrong, right, rule = self.show_trap(TRAPS[0])

        n = self.narrate(
            id="trap1_01",
            text="Trap one: the total used as the interest. Forty thousand rupees becomes fifty-two thousand eight hundred in "
                 "four years; find the rate.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "total")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "Forty")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="trap1_02",
            text="The wrong instinct puts fifty-two thousand eight hundred into the formula as the interest, giving thirty-three "
                 "percent. Correctly, the interest is twelve thousand eight hundred, so the rate is eight percent.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "wrong")
        self.play(FadeIn(wrong, shift=UP * 0.1))
        self.at_word(n, "Correctly")
        self.play(FadeIn(right, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="trap1_03",
            text="The rule: subtract the principal first. I equals A minus P.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "rule")
        self.play(FadeIn(rule, shift=UP * 0.1))
        self.at_word(n, "equals")
        self.play(Indicate(rule, color=FOCUS, scale_factor=1.04))
        self.wait_for_narration(n)
        self.clear_stage()

        head, q, wrong, right, rule = self.show_trap(TRAPS[1])

        n = self.narrate(
            id="trap2_01",
            text="Trap two: triples taken as one and a half times doubles. A sum doubles in five years at simple interest. When "
                 "does it triple?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "triples")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "sum")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.at_word(n, "triple")
        self.play(Indicate(q, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="trap2_02",
            text="The wrong instinct is seven point five years. The correct answer is ten years.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "wrong")
        self.play(FadeIn(wrong, shift=UP * 0.1))
        self.at_word(n, "correct")
        self.play(FadeIn(right, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="trap2_03",
            text="The rule: doubling means the interest equals P, and tripling means the interest equals two P. Simple interest "
                 "is linear, so twice the interest takes twice the time.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "rule")
        self.play(FadeIn(rule, shift=UP * 0.1))
        self.at_word(n, "linear")
        self.play(Indicate(rule, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)
        self.clear_stage()

        head, q, wrong, right, rule = self.show_trap(TRAPS[2])

        n = self.narrate(
            id="trap3_01",
            text="Trap three: becomes n times, read as n times a hundred. A sum becomes four times itself in fifteen years; find "
                 "the rate.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "read")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "four")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="trap3_02",
            text="The wrong instinct is four hundred divided by fifteen. Correctly, it is four minus one, times a hundred, "
                 "divided by fifteen: twenty percent.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "wrong")
        self.play(FadeIn(wrong, shift=UP * 0.1))
        self.at_word(n, "Correctly")
        self.play(FadeIn(right, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="trap3_03",
            text="The rule: the interest is n minus one times P, not n times.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "rule")
        self.play(FadeIn(rule, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S11_traps")

    # =============================================== 12. CHECKPOINT ==========

    def checkpoint(self):
        self.scene_start("S12_checkpoint", title="Checkpoint")

        head = self.heading("Checkpoint  ·  your turn")
        given = given_chips("₹6,000", "5% per year", "4 years")
        hint = pill("simple interest = ?   cancel zeros before you multiply", FOCUS, size=LABEL)
        work = VGroup(text("6,000 × 5 × 4 ÷ 100", BODY, INK), text(f"=  {rs(CP_I)}", BODY, GOOD, BOLD)).arrange(RIGHT, buff=0.5)
        quick = text(f"quick route:  60 × 20  =  {int(CP_I):,}", LABEL, RATIO, BOLD)
        self.stack(head, [given, hint, work, quick], buff=0.6, top=0.7)
        self.no_overlap(*work)

        n = self.narrate(
            id="check_01",
            text="Your turn. Find the simple interest on six thousand rupees at five percent per year for four years. Pause, "
                 "and cancel zeros before you multiply.",
            voice="default",
            subtitle=True,
            pause_after=10.0,
        )
        self.at_word(n, "turn")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "six")
        self.play(FadeIn(given[0], shift=UP * 0.1))
        self.at_word(n, "five")
        self.play(FadeIn(given[1], shift=UP * 0.1))
        self.at_word(n, "four")
        self.play(FadeIn(given[2], shift=UP * 0.1))
        self.at_word(n, "cancel")
        self.play(FadeIn(hint, shift=UP * 0.1))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="check_02",
            text="Six thousand times five times four, divided by a hundred, is twelve hundred rupees.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "times", occurrence=1)
        self.play(FadeIn(work[0], shift=UP * 0.1))
        self.at_word(n, "twelve")
        self.play(FadeIn(work[1], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="check_03",
            text="The quick route: sixty times twenty is twelve hundred.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "quick")
        self.play(FadeIn(quick, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S12_checkpoint")

    # ======================================== 13. PRACTICE QUESTIONS ==========

    def practice_table(self, head, questions, first):
        table, rows = self.placed_table(head, ["Level", "Question"],
                                        [[f"{level}  ·  {first + i}", q] for i, (level, q) in enumerate(questions)],
                                        [1.6, 11.0], room=1.3)
        level_cols = {"L1": GOOD, "L2": RATIO, "L3": BAD}
        for row, (level, _) in zip(rows, questions):
            row[0].set_color(level_cols[level])
        return table, rows

    def practice(self):
        self.scene_start("S13_practice", title="Practice Questions")

        head = self.heading("Practice  ·  Levels 1 and 2")
        table, rows = self.practice_table(head, PRACTICE_A, 1)

        n = self.narrate(
            id="practice_01",
            text="Level one, question one: in what time will eight thousand rupees earn twelve hundred rupees of simple "
                 "interest at five percent per year? Question two: what sum earns nine hundred rupees of simple interest in "
                 "three years at six percent per year? Question three: a sum doubles itself in five years at simple interest; "
                 "what is the rate?",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "time")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "sum", occurrence=1)
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.at_word(n, "doubles")
        self.play(FadeIn(rows[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="practice_02",
            text="Level two, question four: a sum becomes seven thousand two hundred rupees in two years and eight thousand one "
                 "hundred in three years; find the sum and the rate. Question five: at what rate per year will five thousand "
                 "rupees earn fifteen hundred in four years? Question six: in how many years will twelve thousand five "
                 "hundred rupees amount to fifteen thousand at eight percent?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "becomes")
        self.play(FadeIn(rows[3], shift=RIGHT * 0.2))
        self.at_word(n, "earn")
        self.play(FadeIn(rows[4], shift=RIGHT * 0.2))
        self.at_word(n, "amount")
        self.play(FadeIn(rows[5], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="practice_03",
            text="Pause the video and solve these six.",
            voice="default",
            subtitle=True,
            pause_after=12.0,
        )
        self.at_word(n, "Pause")
        self.play(Indicate(head, color=FOCUS, scale_factor=1.05))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)
        self.clear_stage()

        head = self.heading("Practice  ·  Level 3")
        table, rows = self.practice_table(head, PRACTICE_B, 7)

        n = self.narrate(
            id="practice_04",
            text="Level three, question seven: a sum becomes four times itself in fifteen years at simple interest; in how many "
                 "years will it become seven times itself? Question eight: ten thousand rupees is split into two parts, "
                 "invested at five percent and eight percent simple interest; the total interest in one year is six hundred "
                 "and fifty rupees; find the two parts. Question nine: if the rate had been two percent higher, a sum would "
                 "have earned three hundred and sixty rupees more in three years; find the sum.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "becomes")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "split")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.at_word(n, "higher")
        self.play(FadeIn(rows[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="practice_05",
            text="Pause again and solve these three.",
            voice="default",
            subtitle=True,
            pause_after=12.0,
        )
        self.at_word(n, "Pause")
        self.play(Indicate(head, color=FOCUS, scale_factor=1.05))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        self.clear_stage()
        self.scene_end("S13_practice")

    # ================================================= 14. ANSWERS ==========

    def answer_table(self, head, answers, first):
        table, rows = self.placed_table(head, ["#", "Reasoning", "Answer"],
                                        [[str(first + i), how, ans] for i, (how, ans) in enumerate(answers)], [0.8, 8.6, 3.6])
        for row in rows:
            row[0].set_color(MUTED)
            row[2].set_color(GOOD)
        return table, rows

    def answers(self):
        self.scene_start("S14_answers", title="Answer Key, with Reasoning")

        head = self.heading("Answer key  ·  1 to 5", GOOD)
        table, rows = self.answer_table(head, ANSWERS_A, 1)

        n = self.narrate(
            id="answers_01",
            text="One: T is one hundred times twelve hundred, divided by eight thousand times five: three years.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "divided")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "three")
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_02",
            text="Two: P is one hundred times nine hundred, divided by six times three: five thousand rupees.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "divided")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "five")
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_03",
            text="Three: doubling means n is two, so R is one times a hundred, divided by five: twenty percent per year.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "doubling")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "twenty")
        self.play(FadeIn(rows[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_04",
            text="Four: one extra year adds nine hundred rupees, so two years of interest is eighteen hundred, and P is five "
                 "thousand four hundred. R is nine hundred over five thousand four hundred: sixteen and two thirds percent.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "extra")
        self.play(FadeIn(rows[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "sixteen")
        self.play(FadeIn(rows[3][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_05",
            text="Five: R is one hundred times fifteen hundred, divided by five thousand times four: seven point five percent.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "divided")
        self.play(FadeIn(rows[4][:2], shift=RIGHT * 0.2))
        self.at_word(n, "seven")
        self.play(FadeIn(rows[4][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Answer key  ·  6 to 9", GOOD)
        table, rows = self.answer_table(head, ANSWERS_B, 6)

        n = self.narrate(
            id="answers_06",
            text="Six: the interest is two thousand five hundred, so T is two point five years.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "interest")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "point")
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_07",
            text="Seven: four times means interest of three P in fifteen years, so one P every five years. Seven times needs six "
                 "P: thirty years.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "means")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "thirty")
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_08",
            text="Eight: let x be the part at five percent. Solving gives x equal to five thousand, so the parts are five "
                 "thousand each.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "let")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "each")
        self.play(FadeIn(rows[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_09",
            text="Nine: the extra interest comes only from the extra two percent, so P times two times three over a hundred is "
                 "three hundred and sixty, and P is six thousand rupees.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "extra", occurrence=1)
        self.play(FadeIn(rows[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "six")
        self.play(FadeIn(rows[3][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S14_answers")

    # =============================================== 15. EXAM LENS ==========

    def exam_lens(self):
        self.scene_start("S15_exam_lens", title="Exam Lens - Recognise and Move")

        head = self.heading("Exam lens: recognise and move", RATIO)
        blocks = two_line_blocks(LENS, RATIO)
        self.stack(head, list(blocks), buff=0.6, top=0.8, align=LEFT)

        n = self.narrate(
            id="lens_01",
            text="Recognise and move. The recognition cue: two amounts at two times. Take the difference first; it gives one "
                 "year's interest instantly.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Recognise")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "cue")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "difference")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="lens_02",
            text="The target time: thirty to forty-five seconds.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "target")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "thirty")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="lens_03",
            text="The sanity check: with simple interest, the amount after twice the time is always P plus twice the interest.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "sanity")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "twice", occurrence=1)
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S15_exam_lens")

    # ==================================== 16. QUICK REVISION + SUMMARY ==========

    def summary(self):
        self.scene_start("S16_summary", title="Quick Revision and Summary")

        head = self.heading("Quick revision")
        linear = VGroup(pill("linear: the same interest every year", WORD, size=LABEL),
                        pill("tied to the original principal", RATIO, size=LABEL)).arrange(RIGHT, buff=0.4)
        box = VGroup(text("SI = PRT/100    →    P = 100I/(RT)    R = 100I/(PT)    T = 100I/(PR)", LABEL, INK),
                     text("two amounts:  difference of amounts ÷ difference of times  =  yearly interest", LABEL, INK),
                     text("becomes n times:  R × T = (n − 1) × 100", LABEL, INK)).arrange(DOWN, buff=0.28, aligned_edge=LEFT)
        trap = VGroup(pill("total given?", BAD, size=LABEL), pill("subtract the principal first:  I = A − P", FOCUS, size=LABEL))\
            .arrange(RIGHT, buff=0.4)
        nxt = self.breadcrumb("Next", "Video 3 · Compound Interest: Annual")
        self.stack(head, [linear, box, trap, nxt], buff=0.55, top=0.6)
        self.no_overlap(*linear)
        self.no_overlap(*box)
        self.no_overlap(*trap)

        n = self.narrate(
            id="summary_01",
            text="Simple interest is linear: the same interest every year, tied to the original principal.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "linear")
        self.play(FadeIn(linear[0], shift=UP * 0.1))
        self.at_word(n, "original")
        self.play(FadeIn(linear[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_02",
            text="Rearrange the formula for whichever quantity is hidden, use the difference of two amounts to get one year's "
                 "interest, and remember that n times means n minus one times P of interest.",
            voice="default",
            subtitle=True,
        )
        for line, spoken in zip(box, ["Rearrange", "difference", "minus"]):
            self.at_word(n, spoken)
            self.play(FadeIn(line, shift=RIGHT * 0.2), run_time=0.5)
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_03",
            text="Remember the trap: if the question gives the total, subtract the principal before using the formula.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "trap")
        self.play(FadeIn(trap[0], shift=UP * 0.1))
        self.at_word(n, "subtract")
        self.play(FadeIn(trap[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_04",
            text="Next: compound interest, annual.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Next")
        self.play(FadeIn(nxt, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S16_summary")

"""
animation.py for the LMS video generator.

Course : Pre-C-CAT - Section A - Quantitative Aptitude
Video  : Lesson 11 - Simple & Compound Interest - 04 - Half-Yearly, Quarterly & Changing Rates

Source script:
  C:\\Scripts\\Section A\\Module_2_Section_A_Quantitative_Aptitude_Part_1\\Aptitude_Scripts\\Sessions 1-4 - Interest, Profit & Loss, Time & Work\\Lesson 11 - Simple & Compound Interest\\04 - Half-Yearly, Quarterly & Changing Rates.pdf

Built on the golden-reference pattern:
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``;
  * layouts stacked with next_to and guarded with ``no_overlap``; nothing is
    ever animated onto or into another box.

Lesson 11, Video 4 of 7. Not the first video of the lesson: a silent breadcrumb, a one-line recap of Video 3, then today's topic. No spoken course welcome.
The narration follows the script section by section, with numbers written as words for the voice. Tables and lists are spoken one row at a time; the exam patterns, practice questions and answers are split over two screens each. Every figure on screen is computed from the question's numbers and asserted.
Pauses: 3 s on the hook question, the script's 10-second countdown at the checkpoint, 12 s after each practice screen.
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
    """Rupees in the Indian grouping the script uses: ₹1,08,243 (rounded to the rupee)."""
    digits = str(round(x))
    head, tail = digits[:-3], digits[-3:]
    groups = []
    while len(head) > 2:
        groups.insert(0, head[-2:])
        head = head[:-2]
    if head:
        groups.insert(0, head)
    return "₹" + ",".join(groups + [tail])


def period_multiplier(yearly_rate, periods_per_year):
    """The multiplier for ONE period: the yearly rate is divided by the periods per year."""
    return 1 + Fraction(yearly_rate) / periods_per_year / 100


def compound(p, yearly_rate, periods_per_year, periods):
    return p * period_multiplier(yearly_rate, periods_per_year) ** periods


def effective_rate(yearly_rate, periods_per_year):
    """Effective annual rate in percent."""
    return (period_multiplier(yearly_rate, periods_per_year) ** periods_per_year - 1) * 100


def changing(p, *rates):
    for r in rates:
        p = p * (1 + Fraction(r) / 100)
    return p


def fractional(p, rate, whole_years, fraction):
    """Exam convention: CI for the whole years, then SI for the fraction on the amount reached."""
    reached = compound(p, rate, 1, whole_years)
    extra = reached * Fraction(rate) * Fraction(fraction) / 100
    return reached, extra, reached + extra


# ---- the hook: two banks ----
DEPOSIT = 100000
BANK_A = compound(DEPOSIT, 8, 4, 4)
BANK_B = compound(DEPOSIT, "8.2", 1, 1)
EFF_A = effective_rate(8, 4)
assert rs(BANK_A) == "₹1,08,243" and BANK_B == 108200 and round(float(EFF_A), 2) == 8.24 and round(BANK_A - BANK_B) == 43
assert period_multiplier(8, 4) == Fraction("1.02")

# ---- concept figures ----
assert period_multiplier(10, 2) ** 2 == Fraction("1.1025") and effective_rate(10, 2) == Fraction("10.25")
assert changing(1, 10, 20) == Fraction("1.32")

# ---- second worked example: fractional years ----
EX_REACHED, EX_EXTRA, EX_AMOUNT = fractional(8000, 10, 2, Fraction(1, 2))
assert (EX_REACHED, EX_EXTRA, EX_AMOUNT) == (9680, 484, 10164)

# ---- exam patterns (answers computed) ----
P1, P2, P3 = compound(16000, 10, 2, 2), compound(20000, 8, 4, 2), changing(25000, 4, 5)
P5 = effective_rate(12, 2)
assert (P1, P2, P3, P5) == (17640, 20808, 27300, Fraction("12.36")) and P5 > Fraction("12.3")
PATTERNS_A = [("Half-yearly", "₹16,000 at 10% p.a., 1 year", "5% for 2 periods: × 1.1025", rs(P1)),
              ("Quarterly", "₹20,000 at 8% p.a., 6 months", "2% for 2 periods: × 1.0404", rs(P2)),
              ("Changing rates", "₹25,000 at 4% then 5%", "× 1.04 × 1.05", rs(P3))]
PATTERNS_B = [("Fractional years", "₹8,000 at 10% for 2½ years", "CI 2 years, SI ½ year", rs(EX_AMOUNT)),
              ("Compare offers", "12% half-yearly vs 12.3% yearly", "1.06² = 1.1236: half-yearly wins", f"{dec(P5)}%")]

# ---- traps: (title, question, wrong, right, rule) ----
T1 = compound(5000, 8, 4, 2)
assert T1 == 5202
TRAPS = [("Trap 1  ·  rate changed, periods not (or the reverse)", "₹5,000 at 8% p.a. compounded quarterly for 6 months.",
          "8% × 2 periods,  or  2% × 1 period", f"2% × 2 periods  →  {rs(T1)}",
          "Divide the rate and multiply the periods in the same step."),
         ("Trap 2  ·  headline rate compared directly", "Which pays more:  8% quarterly  or  8.2% yearly?",
          "8.2% yearly", f"8% quarterly  (effective ≈ {float(EFF_A):.2f}%)",
          "Convert both to effective annual rates before comparing."),
         ("Trap 3  ·  compounding the half year", "₹8,000 at 10% for 2½ years, CI for whole years and SI for the rest.",
          "8,000 × 1.1^2.5", f"{rs(EX_AMOUNT)} by the convention",
          "Whole years compound; the fraction is simple, unless the question says otherwise.")]

# ---- checkpoint ----
CP = compound(16000, 20, 2, 2)
assert CP == 19360

# ---- practice (answers computed) ----
PRACTICE_A = [("L1", "Find the amount on ₹5,000 at 8% per year, compounded quarterly, for 6 months."),
              ("L1", "Find the compound interest on ₹5,000 at 12% per year for 1 year, compounded half-yearly."),
              ("L2", "Find the amount on ₹10,000 at 20% per year, compounded half-yearly, for 1½ years."),
              ("L2", "₹1,000 is invested at 10% for the first year and 20% for the second, compounded yearly.  Find the amount."),
              ("L2", "Find the amount on ₹8,000 at 10% per year for 2½ years, using CI for whole years and SI for the half year.")]
PRACTICE_B = [("L3", "Which is the better deposit: 12% per year compounded half-yearly, or 12.3% per year compounded yearly?  "
                     "By how much per ₹1,00,000 in one year?"),
              ("L3", "Find the effective annual rate for 10% per year compounded half-yearly."),
              ("L3", "₹25,000 is invested at 4% in year 1 and 5% in year 2, compounded yearly.  Find the compound interest.")]
A2, A3, A4 = compound(5000, 12, 2, 2), compound(10000, 20, 2, 3), changing(1000, 10, 20)
A6_HALF, A6_YEAR = compound(DEPOSIT, 12, 2, 2), compound(DEPOSIT, "12.3", 1, 1)
assert (A2, A3, A4, A6_HALF, A6_YEAR, P3 - 25000) == (5618, 13310, 1320, 112360, 112300, 2300)
ANSWERS_A = [("2% per quarter, 2 quarters:  5,000 × 1.0404", rs(T1)),
             (f"6% per half-year, 2 periods:  5,000 × 1.1236 = {rs(A2)}", f"CI = {rs(A2 - 5000)}"),
             ("10% per half-year, 3 periods:  10,000 × 1.331", rs(A3)),
             ("1,000 × 1.1 × 1.2", rs(A4)),
             ("8,000 × 1.21 = 9,680;   then 9,680 × 0.05 = 484", rs(EX_AMOUNT))]
ANSWERS_B = [(f"half-yearly: 1.06² = 1.1236  →  {rs(A6_HALF)};   yearly: {rs(A6_YEAR)}", f"half-yearly, by {rs(A6_HALF - A6_YEAR)}"),
             ("1.05² = 1.1025", f"{dec(effective_rate(10, 2))}%"),
             (f"25,000 × 1.04 × 1.05 = {rs(P3)}", f"CI = {rs(P3 - 25000)}")]

OBJECTIVES = [("Adjust the rate and the periods", "for half-yearly and quarterly compounding"),
              ("Handle changing rates and fractional years", "a different rate each year; 2½ years"),
              ("Compare offers", "using the effective annual rate")]
LENS = [("Recognition cue", "“half-yearly”, “quarterly”, “every six months”  →  adjust rate and periods together"),
        ("Target time", "45 seconds;  60 seconds for fractional years"),
        ("Sanity check", "more frequent compounding: slightly more than yearly, never less, never a lot more")]
FORMULAS = ["Half-yearly:  A = P (1 + R/200)²ⁿ          Quarterly:  A = P (1 + R/400)⁴ⁿ",
            "Changing rates:  A = P × (1 + R1/100) × (1 + R2/100) × …",
            "Fractional year:  CI for the whole years, then SI on that amount for the fraction",
            "Effective annual rate  =  (period multiplier)^(periods per year) − 1"]


def journey(stops, color):
    """A year's journey as a line with ``stops`` evenly spaced stops."""
    line = Line(LEFT * 2.5, RIGHT * 2.5, color=MUTED, stroke_width=4)
    dots = VGroup(*[Dot(line.point_from_proportion((k + 1) / stops), radius=0.11, color=color) for k in range(stops)])
    return VGroup(line, dots)


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


class HalfYearlyQuarterlyChangingRatesVideo(LMSScene):
    lesson_title = "Half-Yearly, Quarterly & Changing Rates"

    def construct(self):
        self.camera.background_color = BG

        self.intro()
        self.hook()
        self.objectives()
        self.why_this_matters()
        self.rate_per_period()
        self.more_often_earns_more()
        self.changing_and_fractional()
        self.formula_box()
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

    def pattern_table(self, head, patterns):
        table, rows = self.placed_table(head, ["Pattern", "Example", "Method", "Answer"], [list(p) for p in patterns],
                                        [2.6, 4.6, 4.2, 1.8], room=1.2)
        for row in rows:
            row[0].set_color(WORD)
            row[3].set_color(GOOD)
        return table, rows

    def practice_table(self, head, questions, first):
        table, rows = self.placed_table(head, ["Level", "Question"],
                                        [[f"{level}  ·  {first + i}", q] for i, (level, q) in enumerate(questions)],
                                        [1.6, 11.0], room=1.3)
        level_cols = {"L1": GOOD, "L2": RATIO, "L3": BAD}
        for row, (level, _) in zip(rows, questions):
            row[0].set_color(level_cols[level])
        return table, rows

    def answer_table(self, head, answers, first):
        table, rows = self.placed_table(head, ["#", "Reasoning", "Answer"],
                                        [[str(first + i), how, ans] for i, (how, ans) in enumerate(answers)], [0.8, 8.6, 3.6])
        for row in rows:
            row[0].set_color(MUTED)
            row[2].set_color(GOOD)
        return table, rows

    def two_cards(self, lines_a, lines_b):
        """Two cards of the same height.  Returns (cards, contents)."""
        contents = [VGroup(*[text(s, size, c, w) for s, size, c, w in lines]).arrange(DOWN, buff=0.25)
                    for lines in (lines_a, lines_b)]
        tallest = max(c.height for c in contents) + 0.7
        cards = VGroup(*[self.card(c, width=6.2, height=tallest, color=col) for c, col in zip(contents, (WORD, RATIO))])\
            .arrange(RIGHT, buff=0.6)
        return cards, contents

    # ================================================== 0. INTRO ==========
    # Not the first video: silent breadcrumb, a one-line recap of Video 3, then today's topic.

    def intro(self):
        self.scene_start("S00_intro", title="Intro")

        crumb = self.breadcrumb("Quantitative Aptitude", "Lesson 11 · Simple & Compound Interest", "Video 4 of 7")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        recap = VGroup(text("last video", SMALL, MUTED),
                       VGroup(pill("A = P (1 + R/100)ⁿ", WORD, size=LABEL), pill("one multiplier, once per year", GOOD, size=LABEL))
                       .arrange(RIGHT, buff=0.4)).arrange(DOWN, buff=0.25)
        title = fit_width(text("Half-Yearly, Quarterly & Changing Rates", TITLE, INK, BOLD), SAFE_W)
        today = text("today: interest added more often, and rates that change", LABEL, FOCUS)
        block = VGroup(recap, title, today).arrange(DOWN, buff=0.7)
        fit_within(block, SAFE_W, SAFE_H - crumb.height - 0.9)
        block.next_to(crumb, DOWN, buff=0.7)
        self.no_overlap(crumb, recap, title, today)
        self.no_overlap(*recap[1])
        self.validator.check_in_frame(VGroup(crumb, block))

        n = self.narrate(
            id="intro_01",
            text="In the last video, compound interest multiplied by the same multiplier, once a year.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.at_word(n, "multiplied")
        self.play(FadeIn(recap[0]), FadeIn(recap[1][0], shift=UP * 0.1))
        self.at_word(n, "once")
        self.play(FadeIn(recap[1][1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="intro_02",
            text="Today: what happens when interest is added more often, or when the rate itself changes.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "often")
        self.play(FadeIn(title, shift=UP * 0.1))
        self.at_word(n, "itself")
        self.play(FadeIn(today, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_intro")

    # =================================================== 1. HOOK ==========

    def hook(self):
        self.scene_start("S01_hook", title="Hook")

        head = self.heading("Two banks, one bonus")
        bonus = pill(f"your bonus:  {rs(DEPOSIT)} for 1 year", FOCUS, size=LABEL)
        cards, (a, b) = self.two_cards(
            [("Bank A", BODY, WORD, BOLD), ("8% a year", BODY, INK, BOLD), ("compounded quarterly", LABEL, INK, NORMAL)],
            [("Bank B", BODY, RATIO, BOLD), ("8.2% a year", BODY, INK, BOLD), ("compounded yearly", LABEL, INK, NORMAL)])
        ask = pill("8.2 is bigger:  so Bank B pays more?", BAD, size=LABEL)
        goals = VGroup(text("why a smaller headline rate can win", SMALL, GOOD, BOLD),
                       text("compare any two offers in under a minute", SMALL, GOOD, BOLD)).arrange(RIGHT, buff=0.8)
        self.stack(head, [bonus, cards, ask, goals], buff=0.4, top=0.45)
        self.no_overlap(cards[0], cards[1])
        self.no_overlap(*goals)

        n = self.narrate(
            id="hook_01",
            text="You've got your first bonus, one lakh rupees, and two banks want it for one year.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "lakh")
        self.play(FadeIn(bonus, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_02",
            text="Bank A offers eight percent a year, compounded quarterly.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "eight")
        self.play(FadeIn(cards[0][0]), FadeIn(a[0]), FadeIn(a[1], shift=UP * 0.1))
        self.at_word(n, "quarterly")
        self.play(FadeIn(a[2], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_03",
            text="Bank B offers a higher headline rate: eight point two percent a year, compounded yearly.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "higher")
        self.play(FadeIn(cards[1][0]), FadeIn(b[0]), FadeIn(b[1], shift=UP * 0.1))
        self.at_word(n, "yearly")
        self.play(FadeIn(b[2], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_04",
            text="One number is clearly bigger. So Bank B pays more, right?",
            voice="default",
            subtitle=True,
            pause_after=3.0,
        )
        self.at_word(n, "bigger")
        self.play(Indicate(b[1], color=RATIO, scale_factor=1.15))
        self.at_word(n, "more")
        self.play(FadeIn(ask, shift=UP * 0.1))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="hook_05",
            text="By the end of this video you'll know why a smaller headline rate can win, and how to compare any two offers "
                 "in under a minute.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "smaller")
        self.play(FadeIn(goals[0], shift=UP * 0.1))
        self.at_word(n, "compare")
        self.play(FadeIn(goals[1], shift=UP * 0.1))
        self.wait_for_narration(n)

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
            text="First, adjust the rate and the number of periods for half-yearly and quarterly compounding.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "adjust")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "half-yearly")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="obj_03",
            text="Second, handle changing yearly rates and fractional years.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "handle")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "fractional")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="obj_04",
            text="Third, compare offers using the effective annual rate.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "compare")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "effective")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_objectives")

    # ========================================== 3. WHY THIS MATTERS ==========

    def why_this_matters(self):
        self.scene_start("S03_why_this_matters", title="Why This Matters")

        head = self.heading("Why this matters")
        once = pill("compounding is not always once a year", WORD, size=LABEL)
        differ = text("same numbers, different answers: it depends how often interest is added", LABEL, INK)
        error = pill("the most common error in this lesson: mixing up the period", BAD, size=LABEL)
        method = pill("the method you already know, with one adjustment", GOOD, size=LABEL)
        self.stack(head, [once, differ, error, method], buff=0.65, top=0.8)

        n = self.narrate(
            id="why_01",
            text="Compounding doesn't have to happen once a year.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "once")
        self.play(FadeIn(once, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="why_02",
            text="The same numbers give different answers depending on how often interest is added, and mixing up the period "
                 "is the most common error in this lesson.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "different")
        self.play(FadeIn(differ, shift=UP * 0.1))
        self.at_word(n, "mixing")
        self.play(FadeIn(error, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="why_03",
            text="The method is the one you already know, with one adjustment.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "adjustment")
        self.play(FadeIn(method, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_why_this_matters")

    # ================================ 4. CONCEPT: THE RATE PER PERIOD ==========

    def rate_per_period(self):
        self.scene_start("S04_rate_per_period", title="Concept - The Rate Is per Year, the Multiplier Is per Period")

        head = self.heading("Rate per year, multiplier per period")
        table, rows = self.placed_table(head, ["Interest added", "Rate per period", "Periods in n years"],
                                        [["yearly", "R", "n"], ["half-yearly", "R / 2", "2n"], ["quarterly", "R / 4", "4n"]],
                                        [4.2, 4.0, 4.4], size=LABEL, room=2.4)
        for row in rows:
            row[0].set_color(WORD)
        together = pill("divide the rate and multiply the periods, together", GOOD, size=LABEL)
        together.next_to(table, DOWN, buff=0.7)
        self.no_overlap(table, together)
        self.validator.check_in_frame(together)

        n = self.narrate(
            id="period_01",
            text="The stated rate is per year, but the multiplier is per period.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "stated")
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "period")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="period_02",
            text="If interest is added every half-year, each period earns half the yearly rate.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "half-year")
        self.play(FadeIn(rows[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "half")
        self.play(FadeIn(rows[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="period_03",
            text="Divide the rate and multiply the periods, together. Half-yearly: R over two per period, and two n periods.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "together")
        self.play(FadeIn(together, shift=UP * 0.1))
        self.at_word(n, "two", occurrence=2)
        self.play(FadeIn(rows[1][2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="period_04",
            text="Quarterly: R over four per period, and four n periods.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Quarterly")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "four", occurrence=2)
        self.play(FadeIn(rows[2][2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_rate_per_period")

    # ====================== 5. CONCEPT: MORE FREQUENT COMPOUNDING EARNS MORE ==========

    def more_often_earns_more(self):
        self.scene_start("S05_more_often", title="Concept - More Frequent Compounding Earns Slightly More")

        head = self.heading("More frequent compounding earns slightly more")
        sooner = text("interest added sooner starts earning its own interest sooner", LABEL, INK)
        split = text("10% a year, half-yearly   =   5% per period, 2 periods", LABEL, WORD, BOLD)
        square = text(f"1.05²  =  {dec(period_multiplier(10, 2) ** 2)}", BODY, INK, BOLD)
        eff = pill(f"effective annual rate  =  {dec(effective_rate(10, 2))}%", GOOD, size=BODY)
        self.stack(head, [sooner, split, square, eff], buff=0.65, top=0.8)

        n = self.narrate(
            id="more_01",
            text="More frequent compounding earns slightly more.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "slightly")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="more_02",
            text="Interest added sooner starts earning its own interest sooner.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "sooner", occurrence=1)
        self.play(FadeIn(sooner, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="more_03",
            text="Ten percent a year, compounded half-yearly, is one point zero five squared: one point one zero two five.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "half-yearly")
        self.play(FadeIn(split, shift=UP * 0.1))
        self.at_word(n, "squared")
        self.play(FadeIn(square, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="more_04",
            text="That is an effective annual rate of ten point two five percent.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "effective")
        self.play(FadeIn(eff, scale=1.05))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_more_often")

    # ====================== 6. CONCEPT: CHANGING RATES AND FRACTIONAL YEARS ==========

    def changing_and_fractional(self):
        self.scene_start("S06_changing_and_fractional", title="Concept - Changing Rates and Fractional Years")

        head = self.heading("Changing rates and fractional years")
        change = VGroup(text("changing rates: multiply the different multipliers, in order", LABEL, WORD, BOLD),
                        VGroup(text("year 1: 10%     year 2: 20%", LABEL, INK), text("→", LABEL, MUTED),
                               text(f"× 1.1 × 1.2  =  × {dec(changing(1, 10, 20))}", LABEL, GOOD, BOLD)).arrange(RIGHT, buff=0.4))\
            .arrange(DOWN, buff=0.3)
        frac = VGroup(text("fractional years: the exam convention", LABEL, RATIO, BOLD),
                      VGroup(pill("1   compound the whole years", RATIO, size=LABEL),
                             pill("2   simple interest for the fraction, on that amount", RATIO, size=LABEL))
                      .arrange(DOWN, buff=0.25),
                      text("use this unless the question says otherwise", SMALL, MUTED)).arrange(DOWN, buff=0.3)
        self.stack(head, [change, frac], buff=0.8, top=0.7)
        self.no_overlap(*change[1])

        n = self.narrate(
            id="change_01",
            text="Changing rates: multiply the different multipliers, in order.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "order")
        self.play(FadeIn(change[0], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="change_02",
            text="Ten percent in year one, then twenty percent in year two, is times one point one, times one point two.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Ten")
        self.play(FadeIn(change[1][0], shift=RIGHT * 0.1))
        self.at_word(n, "times", occurrence=1)
        self.play(FadeIn(change[1][1:], shift=RIGHT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="change_03",
            text="Fractional years follow an exam convention: compound the whole years, then apply simple interest for the "
                 "fraction, on the amount reached.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "convention")
        self.play(FadeIn(frac[0], shift=UP * 0.1))
        self.at_word(n, "compound")
        self.play(FadeIn(frac[1][0], shift=RIGHT * 0.1))
        self.at_word(n, "simple")
        self.play(FadeIn(frac[1][1], shift=RIGHT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="change_04",
            text="Use this unless the question says otherwise.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "unless")
        self.play(FadeIn(frac[2], shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_changing_and_fractional")

    # ============================================== 7. FORMULA BOX ==========

    def formula_box(self):
        self.scene_start("S07_formula_box", title="Formula Box")

        head = self.heading("Formula box", GOOD)
        lines = VGroup(*[text(f, LABEL, INK) for f in FORMULAS]).arrange(DOWN, buff=0.5, aligned_edge=LEFT)
        box = self.card(lines, width=SAFE_W - 0.4, color=GOOD, pad=0.5)
        self.stack(head, [box], top=0.8)

        n = self.narrate(
            id="formula_01",
            text="Here is the formula box. Half-yearly uses R over two hundred and two n periods; quarterly uses R over four "
                 "hundred and four n periods.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "box")
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(box[0]))
        self.at_word(n, "Half-yearly")
        self.play(FadeIn(lines[0], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_02",
            text="Changing rates multiply one multiplier per year.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Changing")
        self.play(FadeIn(lines[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_03",
            text="A fractional year is compound interest for the whole years, then simple interest on that amount.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "fractional")
        self.play(FadeIn(lines[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_04",
            text="And the effective annual rate is the period multiplier, raised to the periods per year, minus one.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "effective")
        self.play(FadeIn(lines[3], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S07_formula_box")

    # ============================================== 8. THE ANALOGY ==========

    def analogy(self):
        self.scene_start("S08_analogy", title="The Analogy - A Journey with More Stops")

        head = self.heading("Think of a journey with more stops")
        every = text("at every stop: collect a small profit and reinvest it immediately", LABEL, INK)
        four = VGroup(journey(4, RATIO), text("4 stops a year:  4 reinvestments", LABEL, RATIO, BOLD)).arrange(RIGHT, buff=0.6)
        one = VGroup(journey(1, WORD), text("1 stop a year:  1 reinvestment", LABEL, WORD, BOLD)).arrange(RIGHT, buff=0.6)
        often = text("same journey: reinvest more often, and the profit itself earns more", LABEL, GOOD, BOLD)
        stops = VGroup(text("Where the analogy stops", LABEL, BAD, BOLD),
                       text("the extra gain from more stops shrinks fast", LABEL, MUTED),
                       text("yearly → half-yearly helps more than monthly → daily", LABEL, INK)).arrange(DOWN, buff=0.22)
        self.stack(head, [every, four, one, often, stops], buff=0.45, top=0.55)
        self.no_overlap(*four)
        self.no_overlap(*one)

        n = self.narrate(
            id="analogy_01",
            text="Think of a journey with more stops.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "stops")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_02",
            text="At every stop you collect a small profit and reinvest it immediately.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "collect")
        self.play(FadeIn(every, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_03",
            text="Four stops a year means four reinvestments; one stop means one.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Four")
        self.play(FadeIn(four, shift=RIGHT * 0.1))
        self.at_word(n, "one")
        self.play(FadeIn(one, shift=RIGHT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_04",
            text="Same journey, but the more often you reinvest, the more your profit itself earns.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "often")
        self.play(FadeIn(often, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_05",
            text="Where the analogy stops: the extra gain from more stops shrinks fast.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "analogy")
        self.play(FadeIn(stops[0], shift=UP * 0.1))
        self.at_word(n, "shrinks")
        self.play(FadeIn(stops[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_06",
            text="Going from yearly to half-yearly helps more than going from monthly to daily.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "half-yearly")
        self.play(FadeIn(stops[2], shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S08_analogy")

    # ================================ 9. WORKED EXAMPLE: CLOSING THE HOOK ==========

    def hook_solved(self):
        self.scene_start("S09_hook_solved", title="Worked Example - Closing the Hook")

        head = self.heading(f"The two banks:  {rs(DEPOSIT)} for 1 year")
        cards, (a, b) = self.two_cards(
            [("Bank A  ·  8% quarterly", LABEL, WORD, BOLD), ("2% per quarter, 4 quarters", LABEL, INK, NORMAL),
             (f"1,00,000 × 1.02⁴  ≈  {rs(BANK_A)}", LABEL, INK, BOLD), (f"effective ≈ {float(EFF_A):.2f}%", LABEL, GOOD, BOLD)],
            [("Bank B  ·  8.2% yearly", LABEL, RATIO, BOLD), ("one period", LABEL, INK, NORMAL),
             (f"1,00,000 × 1.082  =  {rs(BANK_B)}", LABEL, INK, BOLD), ("effective = 8.2%", LABEL, MUTED, BOLD)])
        wins = text(f"Bank A wins by about ₹{round(BANK_A - BANK_B)}, even with the smaller headline rate", LABEL, FOCUS, BOLD)
        moral = pill("always compare effective rates, never headline rates", GOOD, size=LABEL)
        self.stack(head, [cards, wins, moral], buff=0.55, top=0.55)
        self.no_overlap(cards[0], cards[1])

        n = self.narrate(
            id="solved_01",
            text="Bank A: eight percent quarterly is two percent per quarter, for four quarters.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "quarterly")
        self.play(FadeIn(cards[0][0]), FadeIn(a[0]))
        self.at_word(n, "quarter")
        self.play(FadeIn(a[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_02",
            text="The amount is one lakh times one point zero two to the power four, about one lakh eight thousand two hundred "
                 "and forty-three. The effective rate is about eight point two four percent.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "power")
        self.play(FadeIn(a[2], shift=UP * 0.1))
        self.at_word(n, "effective")
        self.play(FadeIn(a[3], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_03",
            text="Bank B: one lakh times one point zero eight two is one lakh eight thousand two hundred.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Bank")
        self.play(FadeIn(cards[1][0]), FadeIn(b[0]), FadeIn(b[1], shift=UP * 0.1))
        self.at_word(n, "times")
        self.play(FadeIn(b[2], shift=UP * 0.1), FadeIn(b[3], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_04",
            text="Bank A wins by about forty-three rupees, even with the smaller headline rate.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "wins")
        self.play(FadeIn(wins, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_05",
            text="Always compare effective rates, never headline rates.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "effective")
        self.play(FadeIn(moral, scale=1.05))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S09_hook_solved")

    # ====================== 10. SECOND WORKED EXAMPLE: FRACTIONAL YEARS ==========

    def second_example(self):
        self.scene_start("S10_second_example", title="A Second Worked Example - Fractional Years")

        head = self.heading("Fractional years  ·  2½ years")
        given = given_chips("₹8,000", "10% per year", "2½ years")
        note = text("CI for the whole years, SI for the half year", SMALL, RATIO, BOLD)
        steps = self.solve_steps([
            ("two full years:  8,000 × 1.21", f"=  {rs(EX_REACHED)}"),
            (f"half a year, simple, on {rs(EX_REACHED)}:  9,680 × 10% × ½", f"=  {rs(EX_EXTRA)}"),
            ("Amount  =  9,680 + 484", f"=  {rs(EX_AMOUNT)}")])
        self.stack(head, [given, note, steps], buff=0.6, top=0.7)
        self.no_overlap(*steps)

        n = self.narrate(
            id="frac_01",
            text="Find the amount on eight thousand rupees at ten percent per year for two and a half years: compound interest "
                 "for the whole years, simple interest for the half year.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "eight")
        self.play(FadeIn(given[0], shift=UP * 0.1))
        self.at_word(n, "ten")
        self.play(FadeIn(given[1], shift=UP * 0.1))
        self.at_word(n, "half", occurrence=1)
        self.play(FadeIn(given[2], shift=UP * 0.1))
        self.at_word(n, "simple")
        self.play(FadeIn(note, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="frac_02",
            text="Two full years: eight thousand times one point two one is nine thousand six hundred and eighty.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "full")
        self.play(FadeIn(steps[0][:2], shift=RIGHT * 0.1))
        self.at_word(n, "nine")
        self.play(FadeIn(steps[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="frac_03",
            text="Half a year at simple interest on that amount: nine thousand six hundred and eighty, times ten percent, times "
                 "one half, is four hundred and eighty-four.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "simple")
        self.play(FadeIn(steps[1][:2], shift=RIGHT * 0.1))
        self.at_word(n, "four")
        self.play(FadeIn(steps[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="frac_04",
            text="The amount is nine thousand six hundred and eighty plus four hundred and eighty-four: ten thousand one hundred "
                 "and sixty-four rupees.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "plus")
        self.play(FadeIn(steps[2][:2], shift=RIGHT * 0.1))
        self.at_word(n, "sixty-four")
        self.play(FadeIn(steps[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S10_second_example")

    # ============================================ 11. EXAM PATTERNS ==========

    def exam_patterns(self):
        self.scene_start("S11_exam_patterns", title="Exam Patterns - How This Is Asked")

        head = self.heading("Exam patterns  ·  1 to 3 of 5")
        table, rows = self.pattern_table(head, PATTERNS_A)

        n = self.narrate(
            id="patterns_01",
            text="Exams ask this in five ways.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "five")
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.wait_for_narration(n)

        n = self.narrate(
            id="patterns_02",
            text="Half-yearly: sixteen thousand at ten percent for one year is five percent for two periods, seventeen thousand "
                 "six hundred and forty.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Half-yearly")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "periods")
        self.play(FadeIn(rows[0][2:], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="patterns_03",
            text="Quarterly: twenty thousand at eight percent for six months is two percent for two periods, twenty thousand "
                 "eight hundred and eight.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Quarterly")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "periods")
        self.play(FadeIn(rows[1][2:], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="patterns_04",
            text="Changing rates: twenty-five thousand at four percent, then five percent, is times one point zero four, times "
                 "one point zero five: twenty-seven thousand three hundred.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Changing")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "times", occurrence=1)
        self.play(FadeIn(rows[2][2:], shift=RIGHT * 0.2))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Exam patterns  ·  4 and 5 of 5")
        table, rows = self.pattern_table(head, PATTERNS_B)

        n = self.narrate(
            id="patterns_05",
            text="Fractional years: compound interest for two years, simple interest for the half year, ten thousand one "
                 "hundred and sixty-four.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "Fractional")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "simple")
        self.play(FadeIn(rows[0][2:], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="patterns_06",
            text="Compare offers: twelve percent half-yearly is one point zero six squared, an effective twelve point three six "
                 "percent, which beats twelve point three percent yearly.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Compare")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "squared")
        self.play(FadeIn(rows[1][2:], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S11_exam_patterns")

    # ================================ 12. TRAPS AND CONFUSING QUESTIONS ==========

    def traps(self):
        self.scene_start("S12_traps", title="Traps and Confusing Questions")

        head, q, wrong, right, rule = self.show_trap(TRAPS[0])

        n = self.narrate(
            id="trap1_01",
            text="Trap one: the rate changed but the periods not, or the reverse. Five thousand rupees at eight percent per "
                 "annum, compounded quarterly, for six months.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "reverse")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "Five")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="trap1_02",
            text="The wrong instinct is eight percent for two periods, or two percent for one period. Correctly, it is two "
                 "percent for two periods: five thousand two hundred and two rupees.",
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
            text="The rule: divide the rate and multiply the periods in the same step.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "rule")
        self.play(FadeIn(rule, shift=UP * 0.1))
        self.wait_for_narration(n)
        self.clear_stage()

        head, q, wrong, right, rule = self.show_trap(TRAPS[1])

        n = self.narrate(
            id="trap2_01",
            text="Trap two: the headline rate compared directly. Which pays more: eight percent quarterly, or eight point two "
                 "percent yearly?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "headline")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "Which")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="trap2_02",
            text="The wrong instinct is eight point two percent. The correct answer is eight percent quarterly, with an "
                 "effective rate of about eight point two four percent.",
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
            text="The rule: convert both to effective annual rates before comparing.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "rule")
        self.play(FadeIn(rule, shift=UP * 0.1))
        self.wait_for_narration(n)
        self.clear_stage()

        head, q, wrong, right, rule = self.show_trap(TRAPS[2])

        n = self.narrate(
            id="trap3_01",
            text="Trap three: compounding the half year. Eight thousand rupees at ten percent for two and a half years, with "
                 "compound interest for whole years and simple interest for the rest.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "compounding")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "Eight")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="trap3_02",
            text="The wrong instinct raises one point one to the power two point five. The correct answer, by the convention, "
                 "is ten thousand one hundred and sixty-four rupees.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "wrong")
        self.play(FadeIn(wrong, shift=UP * 0.1))
        self.at_word(n, "correct")
        self.play(FadeIn(right, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="trap3_03",
            text="The rule: follow the convention stated, or the standard one: whole years compound, the fraction is simple.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "rule")
        self.play(FadeIn(rule, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S12_traps")

    # =============================================== 13. CHECKPOINT ==========

    def checkpoint(self):
        self.scene_start("S13_checkpoint", title="Checkpoint")

        head = self.heading("Checkpoint  ·  your turn")
        given = given_chips("₹16,000", "20% per year", "1 year")
        hint = pill("compounded half-yearly:   amount = ?", FOCUS, size=LABEL)
        work = VGroup(text("10% per half-year, 2 periods", LABEL, INK),
                      text(f"16,000 × 1.21  =  {rs(CP)}", LABEL, GOOD, BOLD)).arrange(RIGHT, buff=0.8)
        self.stack(head, [given, hint, work], buff=0.7, top=0.8)
        self.no_overlap(*work)

        n = self.narrate(
            id="check_01",
            text="Your turn. Find the amount on sixteen thousand rupees at twenty percent per year, compounded half-yearly, "
                 "for one year.",
            voice="default",
            subtitle=True,
            pause_after=10.0,
        )
        self.at_word(n, "turn")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "sixteen")
        self.play(FadeIn(given[0], shift=UP * 0.1))
        self.at_word(n, "twenty")
        self.play(FadeIn(given[1], shift=UP * 0.1))
        self.at_word(n, "half-yearly")
        self.play(FadeIn(hint, shift=UP * 0.1))
        self.at_word(n, "one")
        self.play(FadeIn(given[2], shift=UP * 0.1))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="check_02",
            text="Ten percent per half-year, for two periods: sixteen thousand times one point two one is nineteen thousand "
                 "three hundred and sixty rupees.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "periods")
        self.play(FadeIn(work[0], shift=UP * 0.1))
        self.at_word(n, "nineteen")
        self.play(FadeIn(work[1], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S13_checkpoint")

    # ======================================== 14. PRACTICE QUESTIONS ==========

    def practice(self):
        self.scene_start("S14_practice", title="Practice Questions")

        head = self.heading("Practice  ·  Levels 1 and 2")
        table, rows = self.practice_table(head, PRACTICE_A, 1)

        n = self.narrate(
            id="practice_01",
            text="Level one, question one: find the amount on five thousand rupees at eight percent per year, compounded "
                 "quarterly, for six months. Question two: find the compound interest on five thousand rupees at twelve "
                 "percent per year for one year, compounded half-yearly.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "quarterly")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "half-yearly")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="practice_02",
            text="Level two, question three: find the amount on ten thousand rupees at twenty percent per year, compounded "
                 "half-yearly, for one and a half years. Question four: one thousand rupees is invested at ten percent for "
                 "the first year and twenty percent for the second, compounded yearly; find the amount. Question five: find "
                 "the amount on eight thousand rupees at ten percent per year for two and a half years, using compound "
                 "interest for whole years and simple interest for the half year.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "half-yearly")
        self.play(FadeIn(rows[2], shift=RIGHT * 0.2))
        self.at_word(n, "invested")
        self.play(FadeIn(rows[3], shift=RIGHT * 0.2))
        self.at_word(n, "simple")
        self.play(FadeIn(rows[4], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="practice_03",
            text="Pause the video and solve these five.",
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
        table, rows = self.practice_table(head, PRACTICE_B, 6)

        n = self.narrate(
            id="practice_04",
            text="Level three, question six: which is the better deposit: twelve percent per year compounded half-yearly, or "
                 "twelve point three percent compounded yearly, and by how much per one lakh rupees in one year? Question "
                 "seven: find the effective annual rate for ten percent per year compounded half-yearly. Question eight: "
                 "twenty-five thousand rupees is invested at four percent in year one and five percent in year two, "
                 "compounded yearly; find the compound interest.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "better")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "effective")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.at_word(n, "invested")
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
        self.scene_end("S14_practice")

    # ================================================= 15. ANSWERS ==========

    def answers(self):
        self.scene_start("S15_answers", title="Answer Key, with Reasoning")

        head = self.heading("Answer key  ·  1 to 5", GOOD)
        table, rows = self.answer_table(head, ANSWERS_A, 1)

        n = self.narrate(
            id="answers_01",
            text="One: two percent per quarter for two quarters, so five thousand times one point zero four zero four: five "
                 "thousand two hundred and two rupees.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "quarter")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "rupees")
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_02",
            text="Two: six percent per half-year for two periods gives five thousand six hundred and eighteen, so the interest "
                 "is six hundred and eighteen rupees.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "periods")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "interest")
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_03",
            text="Three: ten percent per half-year for three periods, so ten thousand times one point three three one: thirteen "
                 "thousand three hundred and ten.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "periods")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "thirteen")
        self.play(FadeIn(rows[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_04",
            text="Four: one thousand times one point one times one point two is one thousand three hundred and twenty.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "times", occurrence=1)
        self.play(FadeIn(rows[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "twenty")
        self.play(FadeIn(rows[3][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_05",
            text="Five: two full years give nine thousand six hundred and eighty, the half year adds four hundred and "
                 "eighty-four, so the total is ten thousand one hundred and sixty-four.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "full")
        self.play(FadeIn(rows[4][:2], shift=RIGHT * 0.2))
        self.at_word(n, "total")
        self.play(FadeIn(rows[4][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Answer key  ·  6 to 8", GOOD)
        table, rows = self.answer_table(head, ANSWERS_B, 6)

        n = self.narrate(
            id="answers_06",
            text="Six: half-yearly gives one lakh twelve thousand three hundred and sixty, yearly gives one lakh twelve thousand "
                 "three hundred, so half-yearly is better by sixty rupees.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "gives", occurrence=1)
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "better")
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_07",
            text="Seven: one point zero five squared is one point one zero two five, so ten point two five percent.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "squared")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "percent")
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_08",
            text="Eight: twenty-five thousand times one point zero four times one point zero five is twenty-seven thousand "
                 "three hundred, so the interest is two thousand three hundred.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "times", occurrence=1)
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "interest")
        self.play(FadeIn(rows[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S15_answers")

    # =============================================== 16. EXAM LENS ==========

    def exam_lens(self):
        self.scene_start("S16_exam_lens", title="Exam Lens - Recognise and Move")

        head = self.heading("Exam lens: recognise and move", RATIO)
        blocks = two_line_blocks(LENS, RATIO)
        self.stack(head, list(blocks), buff=0.6, top=0.8, align=LEFT)

        n = self.narrate(
            id="lens_01",
            text="Recognise and move. The recognition cue: half-yearly, quarterly, or every six months, means adjust the rate "
                 "and the periods together.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Recognise")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "cue")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "adjust")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="lens_02",
            text="The target time: forty-five seconds, or sixty seconds for fractional years.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "target")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "sixty")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="lens_03",
            text="The sanity check: more frequent compounding gives slightly more than yearly compounding, never less, and "
                 "never a lot more for short periods.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "sanity")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "slightly")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S16_exam_lens")

    # ==================================== 17. QUICK REVISION + SUMMARY ==========

    def summary(self):
        self.scene_start("S17_summary", title="Quick Revision and Summary")

        head = self.heading("Quick revision")
        box = VGroup(text("Half-yearly:  R/2, 2n periods          Quarterly:  R/4, 4n periods", LABEL, INK, BOLD),
                     text("Changing rates:  multiply the multipliers, in order", LABEL, INK),
                     text("Fractional years:  compound the whole years, then simple interest on the rest", LABEL, INK))\
            .arrange(DOWN, buff=0.35, aligned_edge=LEFT)
        eff = pill(f"compare effective rates:   10% half-yearly  =  {dec(effective_rate(10, 2))}%", GOOD, size=LABEL)
        nxt = self.breadcrumb("Next", "Video 5 · SI vs CI Difference")
        self.stack(head, [box, eff, nxt], buff=0.7, top=0.7)
        self.no_overlap(*box)

        n = self.narrate(
            id="summary_01",
            text="For more frequent compounding, divide the rate and multiply the periods together.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "divide")
        self.play(FadeIn(box[0], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_02",
            text="Changing rates multiply in order.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "order")
        self.play(FadeIn(box[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_03",
            text="Fractional years: compound the whole years, then simple interest on the remainder.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "remainder")
        self.play(FadeIn(box[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_04",
            text="Compare offers through effective rates.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "effective")
        self.play(FadeIn(eff, scale=1.05))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_05",
            text="Next: the difference between simple and compound interest.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Next")
        self.play(FadeIn(nxt, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S17_summary")

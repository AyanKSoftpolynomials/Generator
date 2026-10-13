"""
animation.py for the LMS video generator.

Course : Pre-C-CAT - Section A - Quantitative Aptitude
Video  : Lesson 11 - Simple & Compound Interest - 06 - Growth & Depreciation

Source script:
  C:\\Scripts\\Section A\\Module_2_Section_A_Quantitative_Aptitude_Part_1\\Aptitude_Scripts\\Sessions 1-4 - Interest, Profit & Loss, Time & Work\\Lesson 11 - Simple & Compound Interest\\06 - Growth & Depreciation.pdf

Built on the golden-reference pattern:
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``;
  * layouts stacked with next_to and guarded with ``no_overlap``; nothing is
    ever animated onto or into another box.

Lesson 11, Video 6 of 7. Not the first video of the lesson: a silent breadcrumb, a one-line recap of Video 5, then today's topic. No spoken course welcome.
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


def num(x):
    """A whole number in the Indian grouping the script uses: 1,25,000."""
    digits = str(round(x))
    head, tail = digits[:-3], digits[-3:]
    groups = []
    while len(head) > 2:
        groups.insert(0, head[-2:])
        head = head[:-2]
    if head:
        groups.insert(0, head)
    return ",".join(groups + [tail])


def rs(x):
    return "₹" + num(x)


def mult(pct):
    """The multiplier for one period: +10 -> 1.1, −10 -> 0.9."""
    return 1 + Fraction(pct) / 100


def chain(value, *pcts):
    """Apply one percentage change per period, each on the current value."""
    for pct in pcts:
        value = value * mult(pct)
    return value


def back(value, *pcts):
    """Go back in time: divide by the total multiplier."""
    return value / chain(Fraction(1), *pcts)


def first_year_below(value, pct, limit):
    years = 0
    while value >= limit:
        value, years = value * mult(pct), years + 1
    return years


assert num(125000) == "1,25,000" and num(99000) == "99,000" and rs(648000) == "₹6,48,000"

# ---- the hook: the phone ----
PHONE, FALL = 50000, -10
GUESS = PHONE * (100 + 2 * FALL) // 100
YEAR_1, YEAR_2 = chain(PHONE, FALL), chain(PHONE, FALL, FALL)
assert (GUESS, YEAR_1, YEAR_2) == (40000, 45000, 40500) and (PHONE - YEAR_1, YEAR_1 - YEAR_2) == (5000, 4500)

# ---- concept figures ----
assert chain(1, -10, -10) == Fraction("0.81") and chain(1, 10, -10) == Fraction("0.99") == chain(1, -10, 10)

# ---- second worked example ----
EX_TOTAL = chain(Fraction(1), 20, -10)
EX_START = back(54000, 20, -10)
assert (EX_TOTAL, EX_START) == (Fraction("1.08"), 50000)

# ---- exam patterns (answers computed) ----
P1, P2, P3, P4 = chain(20000, 10, 10), chain(800000, -10, -10), chain(100000, 10, -10), back(14400, 20, 20)
P6 = first_year_below(100000, -10, 70000)
assert (P1, P2, P3, P4, P6) == (24200, 648000, 99000, 10000, 4) and Fraction(64800, 80000) == mult(-10) ** 2
assert (chain(100000, -10, -10, -10), chain(100000, -10, -10, -10, -10)) == (72900, 65610)
PATTERNS_A = [("Growth", "20,000 grows 10% a year for 2 years", "× 1.21", num(P1)),
              ("Depreciation", "₹8,00,000 car loses 10% a year, 2 years", "× 0.81", rs(P2)),
              ("Mixed", "1,00,000:  +10%, then −10%", "× 0.99", num(P3))]
PATTERNS_B = [("Backwards", "14,400 after 20% growth for 2 years", "÷ 1.44", num(P4)),
              ("Find the rate", "₹80,000 falls to ₹64,800 in 2 years", "0.81 = 0.9²", "10%"),
              ("Find the years", "₹1,00,000 loses 10% a year; first below ₹70,000?", "0.9³ = 0.729,  0.9⁴ = 0.6561", f"{P6} years")]

# ---- traps: (title, question, wrong, right, rule) ----
T3_WRONG = chain(14400, -20, -20)
assert T3_WRONG == 9216
TRAPS = [("Trap 1  ·  percentages added across years", "A machine loses 10% a year.  Loss over 2 years?",
          "10% + 10%  =  20%", "0.9 × 0.9 = 0.81:  a 19% fall",
          "Every year has a new base: multiply the multipliers."),
         ("Trap 2  ·  +x% and −x% cancelling", "A population rises 10% and then falls 10%.  Net change?",
          "no change", "1.1 × 0.9 = 0.99:  a 1% fall",
          "An equal rise and fall always leave a net fall of x²/100 percent."),
         ("Trap 3  ·  going back by subtracting the percentage", "A town of 14,400 grew 20% a year for 2 years.  Population 2 years ago?",
          f"14,400 × 0.8 × 0.8  =  {num(T3_WRONG)}", f"14,400 ÷ 1.44  =  {num(P4)}",
          "A 20% rise is undone by dividing by 1.2, not by taking 20% off.")]

# ---- checkpoint ----
CP = chain(8000, -25, -25)
assert CP == 4500 and mult(-25) ** 2 == Fraction("0.5625") and 8000 * Fraction(3, 4) * Fraction(3, 4) == CP

# ---- practice (answers computed) ----
PRACTICE_A = [("L1", "A town's population is 20,000 and grows 10% per year.  What is it after 2 years?"),
              ("L1", "A machine bought for ₹1,25,000 loses 20% of its value each year.  Find its value after 2 years."),
              ("L2", "A population of 1,00,000 increases 10% in year 1 and decreases 10% in year 2.  Find the final population."),
              ("L2", "A machine's value falls from ₹80,000 to ₹64,800 in 2 years, at the same rate each year.  Find the rate."),
              ("L2", "A town's population is 14,400 after growing 20% per year for 2 years.  What was it 2 years ago?")]
PRACTICE_B = [("L3", "A product's users grew 20% in year 1 and fell 10% in year 2, ending at 54,000.  Find the starting number."),
              ("L3", "Equipment worth ₹1,00,000 loses 10% of its value each year.  After how many full years is it first worth "
                     "less than ₹70,000?"),
              ("L3", "A population of 50,000 grows 4% per year.  Find it after 2 years.")]
A2, A8 = chain(125000, -20, -20), chain(50000, 4, 4)
assert (A2, A8) == (80000, 54080) and mult(4) ** 2 == Fraction("1.0816")
ANSWERS_A = [("20,000 × 1.21", num(P1)),
             ("1,25,000 × 0.64", rs(A2)),
             ("1,00,000 × 0.99", num(P3)),
             ("64,800 ÷ 80,000 = 0.81 = 0.9²", "10% per year"),
             ("14,400 ÷ 1.44", num(P4))]
ANSWERS_B = [("54,000 ÷ (1.2 × 0.9)  =  54,000 ÷ 1.08", num(EX_START)),
             ("after 3 years: ₹72,900;    after 4 years: ₹65,610", f"{P6} years"),
             ("50,000 × 1.0816", num(A8))]

OBJECTIVES = [("Apply growth and depreciation multipliers", "over several periods"),
              ("Combine rises and falls", "in one chain"),
              ("Work backwards in time", "and find the rate or the number of years")]
LENS = [("Recognition cue", "“depreciates”, “decreases by x% every year”, “population grows”  →  a multiplier chain"),
        ("Target time", "35 seconds"),
        ("Sanity check", "two equal falls of R%: a little less than 2R%;   two equal rises: a little more")]
FORMULAS = ["Growth:  P (1 + R/100)ⁿ            Depreciation:  P (1 − R/100)ⁿ",
            "Mixed:  P × (1 + R1/100) × (1 − R2/100) × …",
            "Going back in time:  divide by the multiplier",
            "Two equal changes of R%:  net change = ±2R + R²/100     (for a fall, use −R)"]
BOUNCES = [100, 90, 81]
assert [int(chain(100, *[-10] * k)) for k in range(3)] == BOUNCES


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


class GrowthAndDepreciationVideo(LMSScene):
    lesson_title = "Growth & Depreciation"

    def construct(self):
        self.camera.background_color = BG

        self.intro()
        self.hook()
        self.objectives()
        self.why_this_matters()
        self.each_period_is_a_multiplier()
        self.mixed_backwards_rate()
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

    def titled(self, title, color, *lines):
        """A small titled group: bold title with its lines underneath."""
        return VGroup(text(title, LABEL, color, BOLD), *lines).arrange(DOWN, buff=0.22)

    # ================================================== 0. INTRO ==========
    # Not the first video: silent breadcrumb, a one-line recap of Video 5, then today's topic.

    def intro(self):
        self.scene_start("S00_intro", title="Intro")

        crumb = self.breadcrumb("Quantitative Aptitude", "Lesson 11 · Simple & Compound Interest", "Video 6 of 7")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        recap = VGroup(text("last video", SMALL, MUTED),
                       VGroup(pill("CI − SI  =  P (R/100)²", WORD, size=LABEL), pill("the interest on interest", GOOD, size=LABEL))
                       .arrange(RIGHT, buff=0.4)).arrange(DOWN, buff=0.25)
        title = text("Growth & Depreciation", TITLE, INK, BOLD)
        today = text("today: the same multipliers, for anything that grows or loses value", LABEL, FOCUS)
        block = VGroup(recap, title, today).arrange(DOWN, buff=0.7)
        fit_within(block, SAFE_W, SAFE_H - crumb.height - 0.9)
        block.next_to(crumb, DOWN, buff=0.7)
        self.no_overlap(crumb, recap, title, today)
        self.no_overlap(*recap[1])
        self.validator.check_in_frame(VGroup(crumb, block))

        n = self.narrate(
            id="intro_01",
            text="In the last video, the gap between compound and simple interest turned out to be the interest on interest.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.at_word(n, "gap")
        self.play(FadeIn(recap[0]), FadeIn(recap[1][0], shift=UP * 0.1))
        self.at_word(n, "turned")
        self.play(FadeIn(recap[1][1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="intro_02",
            text="Today: the same multipliers, for anything that grows or loses value.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "multipliers")
        self.play(FadeIn(title, shift=UP * 0.1))
        self.at_word(n, "loses")
        self.play(FadeIn(today, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_intro")

    # =================================================== 1. HOOK ==========

    def hook(self):
        self.scene_start("S01_hook", title="Hook")

        head = self.heading("A resale app listing")
        lines = VGroup(text(f"Phone  ·  bought at {rs(PHONE)}", BODY, INK, BOLD),
                       text("loses 10% of its value every year", LABEL, INK),
                       text("after 2 years:   ₹ ?", BODY, FOCUS, BOLD)).arrange(DOWN, buff=0.35)
        listing = self.card(lines, width=7.4, color=WORD, pad=0.45)
        answers = VGroup(pill(f"your guess:  50,000 − 20%  =  {rs(GUESS)}", MUTED, size=LABEL),
                         pill(f"the app says:  {rs(YEAR_2)}", RATIO, size=LABEL)).arrange(RIGHT, buff=0.5)
        who = pill("who is wrong: you, or the app?", FOCUS, size=LABEL)
        goal = text("goal: any growth or falling-value question, in one line", SMALL, GOOD, BOLD)
        self.stack(head, [listing, answers, who, goal], buff=0.45, top=0.5)
        self.no_overlap(*answers)

        n = self.narrate(
            id="hook_01",
            text="You bought a phone for fifty thousand rupees.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "fifty")
        self.play(FadeIn(listing[0]), FadeIn(lines[0], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_02",
            text="Resale data says it loses ten percent of its value each year.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "loses")
        self.play(FadeIn(lines[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_03",
            text="So after two years it's worth fifty thousand minus twenty percent, which is forty thousand. Right?",
            voice="default",
            subtitle=True,
            pause_after=3.0,
        )
        self.at_word(n, "after")
        self.play(FadeIn(lines[2], shift=UP * 0.1))
        self.at_word(n, "forty")
        self.play(FadeIn(answers[0], shift=UP * 0.1))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="hook_04",
            text="The app says forty thousand five hundred. Who's wrong, you or the app?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "app")
        self.play(FadeIn(answers[1], shift=UP * 0.1))
        self.at_word(n, "wrong")
        self.play(FadeIn(who, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_05",
            text="By the end of this video you'll know, and you'll handle any growth or falling-value question, from user bases "
                 "to machines, in one line.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "growth")
        self.play(FadeIn(goal, shift=UP * 0.1))
        self.at_word(n, "line")
        self.play(Indicate(goal, color=GOOD, scale_factor=1.04))
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
            text="First, apply growth and depreciation multipliers over several periods.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "apply")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "several")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="obj_03",
            text="Second, combine rises and falls in one chain.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "combine")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "chain")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="obj_04",
            text="Third, work backwards in time, and find the rate or the number of years.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "backwards")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "rate")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_objectives")

    # ========================================== 3. WHY THIS MATTERS ==========

    def why_this_matters(self):
        self.scene_start("S03_why_this_matters", title="Why This Matters")

        head = self.heading("Why this matters")
        kinds = VGroup(pill("growth:  population  ·  user base  ·  salary", GOOD, size=LABEL),
                       pill("depreciation:  machine  ·  car  ·  phone", BAD, size=LABEL)).arrange(DOWN, buff=0.3)
        sign = text("compound interest, with a plus or a minus sign", LABEL, INK, BOLD)
        often = text("exams use them constantly", LABEL, MUTED)
        wrong = pill("adding or subtracting the percentages is always wrong", BAD, size=LABEL)
        self.stack(head, [kinds, sign, often, wrong], buff=0.55, top=0.7)

        n = self.narrate(
            id="why_01",
            text="Growth, like a population, a user base or a salary, and depreciation, like a machine, a car or a phone, are "
                 "compound interest with a plus or a minus sign.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "Growth")
        self.play(FadeIn(kinds[0], shift=UP * 0.1))
        self.at_word(n, "depreciation")
        self.play(FadeIn(kinds[1], shift=UP * 0.1))
        self.at_word(n, "sign")
        self.play(FadeIn(sign, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="why_02",
            text="Exams use them constantly, and the shortcut most people reach for, adding or subtracting the percentages, is "
                 "always wrong.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "constantly")
        self.play(FadeIn(often, shift=UP * 0.1))
        self.at_word(n, "wrong")
        self.play(FadeIn(wrong, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_why_this_matters")

    # ================================ 4. CONCEPT: EACH PERIOD IS A MULTIPLIER ==========

    def each_period_is_a_multiplier(self):
        self.scene_start("S04_each_period_is_a_multiplier", title="Concept - Each Period Is a Multiplier")

        head = self.heading("Each period changes the current value")
        left = text("a 10% fall in year 2  =  10% of what is left after year 1", LABEL, INK)
        each = text("so each period is a multiplier", LABEL, MUTED, BOLD)
        mults = VGroup(pill("growth by R%:   × (1 + R/100)", GOOD, size=LABEL), pill("depreciation by R%:   × (1 − R/100)", BAD, size=LABEL))\
            .arrange(RIGHT, buff=0.5)
        chain_title = text("chain the multipliers:  two years of 10% depreciation", LABEL, WORD, BOLD)
        result = VGroup(text(f"0.9 × 0.9  =  {dec(chain(1, -10, -10))}", BODY, INK, BOLD), pill("a 19% fall", GOOD, size=LABEL),
                        pill("not 20%", BAD, size=LABEL)).arrange(RIGHT, buff=0.5)
        self.stack(head, [left, each, mults, chain_title, result], buff=0.5, top=0.6)
        self.no_overlap(*mults)
        self.no_overlap(*result)

        n = self.narrate(
            id="mult_01",
            text="Each period changes the current value, not the original. A ten percent fall in year two is ten percent of "
                 "what is left after year one.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "current")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "left")
        self.play(FadeIn(left, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="mult_02",
            text="So each period is a multiplier. Growth by R percent is times one plus R over a hundred. Depreciation by R "
                 "percent is times one minus R over a hundred.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "multiplier")
        self.play(FadeIn(each, shift=UP * 0.1))
        self.at_word(n, "plus")
        self.play(FadeIn(mults[0], shift=UP * 0.1))
        self.at_word(n, "minus")
        self.play(FadeIn(mults[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="mult_03",
            text="Chain the multipliers. Two years of ten percent depreciation: zero point nine times zero point nine is zero "
                 "point eight one.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Chain")
        self.play(FadeIn(chain_title, shift=UP * 0.1))
        self.at_word(n, "times")
        self.play(FadeIn(result[0], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="mult_04",
            text="That is a nineteen percent fall, not twenty.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "nineteen")
        self.play(FadeIn(result[1], shift=LEFT * 0.1))
        self.at_word(n, "twenty")
        self.play(FadeIn(result[2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_each_period_is_a_multiplier")

    # ====================== 5. CONCEPT: MIXED CHANGES, BACKWARDS, THE RATE ==========

    def mixed_backwards_rate(self):
        self.scene_start("S05_mixed_backwards_rate", title="Concept - Mixed Changes, Going Back, Finding the Rate")

        head = self.heading("Mixed changes, going back, finding the rate")
        mixed_line = text(f"+10% then −10%:   1.1 × 0.9  =  {dec(chain(1, 10, -10))}", LABEL, INK)
        mixed_fall = text("a 1% fall", LABEL, GOOD, BOLD)
        mixed_note = text("order doesn't matter, but the signs do", SMALL, MUTED)
        mixed = self.titled("mixed changes chain too", WORD, VGroup(mixed_line, mixed_fall).arrange(RIGHT, buff=0.5), mixed_note)
        back_line = text("earlier value  =  today ÷ m", LABEL, INK)
        backwards = self.titled("backwards in time: divide", RATIO, back_line)
        rate_line = text("0.81  =  0.9²    →    10% per year", LABEL, INK)
        rate = self.titled("to find the rate: take the root of the total multiplier", GOOD, rate_line)
        self.stack(head, [mixed, backwards, rate], buff=0.6, top=0.6)
        self.no_overlap(mixed_line, mixed_fall)

        n = self.narrate(
            id="mixed_01",
            text="Mixed changes chain too. Plus ten percent, then minus ten percent: one point one times zero point nine is zero "
                 "point nine nine, a one percent fall.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "Mixed")
        self.play(FadeIn(mixed[0], shift=UP * 0.1))
        self.at_word(n, "times")
        self.play(FadeIn(mixed_line, shift=UP * 0.1))
        self.at_word(n, "fall")
        self.play(FadeIn(mixed_fall, shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="mixed_02",
            text="Order doesn't matter, but the signs do.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "signs")
        self.play(FadeIn(mixed_note, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="mixed_03",
            text="Backwards in time, divide. If today's value came after a multiplier m, the earlier value is today divided by "
                 "m.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Backwards")
        self.play(FadeIn(backwards[0], shift=UP * 0.1))
        self.at_word(n, "divided")
        self.play(FadeIn(back_line, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="mixed_04",
            text="To find the rate, take the root of the total multiplier. Zero point eight one is zero point nine squared, so "
                 "ten percent per year.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "root")
        self.play(FadeIn(rate[0], shift=UP * 0.1))
        self.at_word(n, "squared")
        self.play(FadeIn(rate_line, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_mixed_backwards_rate")

    # ============================================== 6. FORMULA BOX ==========

    def formula_box(self):
        self.scene_start("S06_formula_box", title="Formula Box")

        head = self.heading("Formula box", GOOD)
        lines = VGroup(*[text(f, LABEL, INK) for f in FORMULAS]).arrange(DOWN, buff=0.5, aligned_edge=LEFT)
        box = self.card(lines, width=SAFE_W - 0.4, color=GOOD, pad=0.5)
        self.stack(head, [box], top=0.8)

        n = self.narrate(
            id="formula_01",
            text="Here is the formula box. Growth multiplies by one plus R over a hundred each period; depreciation by one "
                 "minus R over a hundred.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "box")
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(box[0]))
        self.at_word(n, "Growth")
        self.play(FadeIn(lines[0], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_02",
            text="Mixed changes multiply in one chain.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Mixed")
        self.play(FadeIn(lines[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_03",
            text="To go back in time, divide by the multiplier.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "divide")
        self.play(FadeIn(lines[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_04",
            text="And two equal changes of R percent give a net change of two R plus R squared over a hundred; for a fall, use "
                 "minus R.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "equal")
        self.play(FadeIn(lines[3], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_formula_box")

    # ============================================== 7. THE ANALOGY ==========

    def analogy(self):
        self.scene_start("S07_analogy", title="The Analogy - A Bouncing Ball")

        head = self.heading("A ball that rebounds to 90% of its height")
        cols = VGroup(*[VGroup(Rectangle(width=0.9, height=1.8 * h / 100, color=WORD, fill_color=WORD, fill_opacity=0.45),
                               text(f"{h} cm", SMALL, INK, BOLD)).arrange(DOWN, buff=0.14) for h in BOUNCES])\
            .arrange(RIGHT, buff=0.6, aligned_edge=DOWN)
        not_80 = pill("81, not 80", BAD, size=LABEL)
        share = text("each bounce takes a share of what is left", LABEL, INK)
        same = pill("depreciation works exactly the same way", GOOD, size=LABEL)
        side = VGroup(not_80, share, same).arrange(DOWN, buff=0.4, aligned_edge=LEFT)
        row = VGroup(cols, side).arrange(RIGHT, buff=0.9)
        stops = VGroup(text("Where the analogy stops", LABEL, BAD, BOLD),
                       text("a real ball also loses energy to air and surface", LABEL, MUTED),
                       text("depreciation follows the stated percentage exactly", LABEL, INK)).arrange(DOWN, buff=0.22)
        self.stack(head, [row, stops], buff=0.7, top=0.6)
        self.no_overlap(*cols)
        self.no_overlap(cols, side)

        n = self.narrate(
            id="analogy_01",
            text="A ball that rebounds to ninety percent of its previous height goes one hundred centimetres, ninety "
                 "centimetres, then eighty-one centimetres, not eighty.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "ball")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "hundred")
        self.play(FadeIn(cols[0], shift=UP * 0.2))
        self.at_word(n, "ninety", occurrence=2)
        self.play(FadeIn(cols[1], shift=UP * 0.2))
        self.at_word(n, "eighty-one")
        self.play(FadeIn(cols[2], shift=UP * 0.2))
        self.at_word(n, "eighty")
        self.play(FadeIn(not_80, shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_02",
            text="Each bounce takes a share of what is left.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "share")
        self.play(FadeIn(share, shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_03",
            text="Depreciation works exactly the same way.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "same")
        self.play(FadeIn(same, shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_04",
            text="Where the analogy stops: a real ball also loses energy to air and surface.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "stops")
        self.play(FadeIn(stops[0], shift=UP * 0.1))
        self.at_word(n, "energy")
        self.play(FadeIn(stops[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_05",
            text="Depreciation follows the stated percentage exactly.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "stated")
        self.play(FadeIn(stops[2], shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S07_analogy")

    # ================================ 8. WORKED EXAMPLE: CLOSING THE HOOK ==========

    def hook_solved(self):
        self.scene_start("S08_hook_solved", title="Worked Example - Closing the Hook")

        head = self.heading(f"The phone:  {rs(PHONE)}, losing 10% a year")
        steps = self.solve_steps([("Year 1:   50,000 × 0.9", f"=  {rs(YEAR_1)}"), ("Year 2:   45,000 × 0.9", f"=  {rs(YEAR_2)}")])
        right = pill("the app is right", GOOD, size=LABEL)
        losses = VGroup(text(f"year 1:  −{rs(PHONE - YEAR_1)}", LABEL, INK), text(f"year 2:  only −{rs(YEAR_1 - YEAR_2)}", LABEL, INK))\
            .arrange(RIGHT, buff=0.9)
        why = text("the second 10% is taken from a smaller value", LABEL, FOCUS, BOLD)
        self.stack(head, [steps, right, losses, why], buff=0.55, top=0.7)
        self.no_overlap(*steps)
        self.no_overlap(*losses)

        n = self.narrate(
            id="solved_01",
            text="Year one: fifty thousand times zero point nine is forty-five thousand.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "times")
        self.play(FadeIn(steps[0][:2], shift=RIGHT * 0.1))
        self.at_word(n, "forty-five")
        self.play(FadeIn(steps[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_02",
            text="Year two: forty-five thousand times zero point nine is forty thousand five hundred. The app is right.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "times")
        self.play(FadeIn(steps[1][:2], shift=RIGHT * 0.1))
        self.at_word(n, "forty")
        self.play(FadeIn(steps[1][2], shift=LEFT * 0.1))
        self.at_word(n, "right")
        self.play(FadeIn(right, scale=1.05))
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_03",
            text="You lose five thousand in year one but only four thousand five hundred in year two, because the second ten "
                 "percent is taken from a smaller value.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "five")
        self.play(FadeIn(losses[0], shift=UP * 0.1))
        self.at_word(n, "four")
        self.play(FadeIn(losses[1], shift=UP * 0.1))
        self.at_word(n, "smaller")
        self.play(FadeIn(why, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S08_hook_solved")

    # ====================== 9. SECOND WORKED EXAMPLE: BACKWARDS, MIXED ==========

    def second_example(self):
        self.scene_start("S09_second_example", title="A Second Worked Example - Backwards with Mixed Changes")

        head = self.heading("Backwards with mixed changes")
        given = VGroup(pill("year 1:  +20%", GOOD, size=LABEL), pill("year 2:  −10%", BAD, size=LABEL),
                       pill("ends at 54,000 users", WORD, size=LABEL), pill("start = ?", FOCUS, size=LABEL)).arrange(RIGHT, buff=0.35)
        steps = self.solve_steps([("total multiplier  =  1.2 × 0.9", f"=  {dec(EX_TOTAL)}"),
                                  ("start  =  54,000 ÷ 1.08", f"=  {num(EX_START)} users")])
        self.stack(head, [given, steps], buff=0.9, top=0.9)
        self.no_overlap(*given)
        self.no_overlap(*steps)

        n = self.narrate(
            id="users_01",
            text="A product's active users grew twenty percent in year one and fell ten percent in year two, ending at "
                 "fifty-four thousand. How many users did it start with?",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "grew")
        self.play(FadeIn(given[0], shift=UP * 0.1))
        self.at_word(n, "fell")
        self.play(FadeIn(given[1], shift=UP * 0.1))
        self.at_word(n, "fifty-four")
        self.play(FadeIn(given[2], shift=UP * 0.1))
        self.at_word(n, "start")
        self.play(FadeIn(given[3], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="users_02",
            text="The total multiplier is one point two times zero point nine: one point zero eight.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "times")
        self.play(FadeIn(steps[0][:2], shift=RIGHT * 0.1))
        self.at_word(n, "eight")
        self.play(FadeIn(steps[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="users_03",
            text="So the start is fifty-four thousand divided by one point zero eight: fifty thousand users.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "divided")
        self.play(FadeIn(steps[1][:2], shift=RIGHT * 0.1))
        self.at_word(n, "users")
        self.play(FadeIn(steps[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S09_second_example")

    # ============================================ 10. EXAM PATTERNS ==========

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
            text="Growth: twenty thousand growing ten percent a year for two years is times one point two one, twenty-four "
                 "thousand two hundred.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Growth")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "times")
        self.play(FadeIn(rows[0][2:], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="patterns_03",
            text="Depreciation: an eight lakh car losing ten percent a year for two years is times zero point eight one, six "
                 "lakh forty-eight thousand.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Depreciation")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "times")
        self.play(FadeIn(rows[1][2:], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="patterns_04",
            text="Mixed: one lakh, up ten percent then down ten percent, is times zero point nine nine, ninety-nine thousand.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Mixed")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "times")
        self.play(FadeIn(rows[2][2:], shift=RIGHT * 0.2))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Exam patterns  ·  4 to 6 of 6")
        table, rows = self.pattern_table(head, PATTERNS_B)

        n = self.narrate(
            id="patterns_05",
            text="Backwards: fourteen thousand four hundred after twenty percent growth for two years means divide by one point "
                 "four four, ten thousand.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "Backwards")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "divide")
        self.play(FadeIn(rows[0][2:], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="patterns_06",
            text="Find the rate: eighty thousand falling to sixty-four thousand eight hundred in two years is zero point eight "
                 "one, which is zero point nine squared, so ten percent a year.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "rate")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "squared")
        self.play(FadeIn(rows[1][2:], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="patterns_07",
            text="Find the years: one lakh losing ten percent a year is seventy-two thousand nine hundred after three years and "
                 "sixty-five thousand six hundred and ten after four, so it first drops below seventy thousand after four "
                 "years.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "years")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "drops")
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
            text="Trap one: percentages added across years. A machine loses ten percent a year; what is the loss over two years?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "added")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "machine")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="trap1_02",
            text="The wrong instinct is twenty percent. The correct answer is nineteen percent.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "wrong")
        self.play(FadeIn(wrong, shift=UP * 0.1))
        self.at_word(n, "correct")
        self.play(FadeIn(right, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="trap1_03",
            text="The rule: every year has a new base, so multiply the multipliers.",
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
            text="Trap two: a rise and an equal fall cancelling. A population rises ten percent and then falls ten percent; "
                 "what is the net change?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "cancelling")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "population")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="trap2_02",
            text="The wrong instinct is no change. The correct answer is a one percent fall, because one point one times zero "
                 "point nine is zero point nine nine.",
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
            text="The rule: an equal rise and fall always leave a net fall of x squared over a hundred percent.",
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
            text="Trap three: going back by subtracting the percentage. A town of fourteen thousand four hundred grew twenty "
                 "percent a year for two years; what was the population two years ago?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "subtracting")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "town")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="trap3_02",
            text="The wrong instinct takes twenty percent off twice, giving nine thousand two hundred and sixteen. Correctly, "
                 "fourteen thousand four hundred divided by one point four four is ten thousand.",
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
            text="The rule: a twenty percent rise is undone by dividing by one point two, not by taking twenty percent off.",
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
        given = VGroup(pill("machine:  ₹8,000", WORD, size=LABEL), pill("depreciates 25% per year", BAD, size=LABEL),
                       pill("2 years", "#CE93D8", size=LABEL)).arrange(RIGHT, buff=0.35)
        hint = pill("value after 2 years = ?", FOCUS, size=LABEL)
        work = VGroup(text(f"0.75 × 0.75  =  {dec(mult(-25) ** 2)}", LABEL, INK),
                      text(f"8,000 × 0.5625  =  {rs(CP)}", LABEL, GOOD, BOLD)).arrange(RIGHT, buff=0.9)
        fractions = text(f"with fractions:   8,000 × 3/4 × 3/4  =  {rs(CP)}", LABEL, RATIO, BOLD)
        self.stack(head, [given, hint, work, fractions], buff=0.6, top=0.7)
        self.no_overlap(*given)
        self.no_overlap(*work)

        n = self.narrate(
            id="check_01",
            text="Your turn. A machine worth eight thousand rupees depreciates twenty-five percent per year. What is it worth "
                 "after two years?",
            voice="default",
            subtitle=True,
            pause_after=10.0,
        )
        self.at_word(n, "turn")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "eight")
        self.play(FadeIn(given[0], shift=UP * 0.1))
        self.at_word(n, "twenty-five")
        self.play(FadeIn(given[1], shift=UP * 0.1))
        self.at_word(n, "after")
        self.play(FadeIn(hint, shift=UP * 0.1))
        self.at_word(n, "two")
        self.play(FadeIn(given[2], shift=UP * 0.1))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="check_02",
            text="Eight thousand times zero point five six two five is four thousand five hundred rupees.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "times")
        self.play(FadeIn(work[0], shift=UP * 0.1))
        self.at_word(n, "four")
        self.play(FadeIn(work[1], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="check_03",
            text="With fractions: eight thousand times three fourths times three fourths is four thousand five hundred.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "fractions")
        self.play(FadeIn(fractions, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S12_checkpoint")

    # ======================================== 13. PRACTICE QUESTIONS ==========

    def practice(self):
        self.scene_start("S13_practice", title="Practice Questions")

        head = self.heading("Practice  ·  Levels 1 and 2")
        table, rows = self.practice_table(head, PRACTICE_A, 1)

        n = self.narrate(
            id="practice_01",
            text="Level one, question one: a town's population is twenty thousand and grows ten percent per year; what is it "
                 "after two years? Question two: a machine bought for one lakh twenty-five thousand rupees loses twenty "
                 "percent of its value each year; find its value after two years.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "population")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "machine")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="practice_02",
            text="Level two, question three: a population of one lakh increases ten percent in year one and decreases ten "
                 "percent in year two; find the final population. Question four: a machine's value falls from eighty thousand "
                 "rupees to sixty-four thousand eight hundred in two years, at the same rate each year; find the rate. "
                 "Question five: a town's population is fourteen thousand four hundred after growing twenty percent per year "
                 "for two years; what was it two years ago?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "increases")
        self.play(FadeIn(rows[2], shift=RIGHT * 0.2))
        self.at_word(n, "falls")
        self.play(FadeIn(rows[3], shift=RIGHT * 0.2))
        self.at_word(n, "ago")
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
            text="Level three, question six: a product's users grew twenty percent in year one and fell ten percent in year "
                 "two, ending at fifty-four thousand; find the starting number. Question seven: equipment worth one lakh "
                 "rupees loses ten percent of its value each year; after how many full years is it first worth less than "
                 "seventy thousand? Question eight: a population of fifty thousand grows four percent per year; find it after "
                 "two years.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "grew")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "equipment")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.at_word(n, "grows")
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

    def answers(self):
        self.scene_start("S14_answers", title="Answer Key, with Reasoning")

        head = self.heading("Answer key  ·  1 to 5", GOOD)
        table, rows = self.answer_table(head, ANSWERS_A, 1)

        n = self.narrate(
            id="answers_01",
            text="One: twenty thousand times one point two one is twenty-four thousand two hundred.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "times")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "twenty-four")
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_02",
            text="Two: one lakh twenty-five thousand times zero point six four is eighty thousand rupees.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "times")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "eighty")
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_03",
            text="Three: one lakh times zero point nine nine is ninety-nine thousand.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "times")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "ninety-nine")
        self.play(FadeIn(rows[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_04",
            text="Four: sixty-four thousand eight hundred divided by eighty thousand is zero point eight one, which is zero "
                 "point nine squared, so ten percent per year.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "divided")
        self.play(FadeIn(rows[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "ten")
        self.play(FadeIn(rows[3][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_05",
            text="Five: fourteen thousand four hundred divided by one point four four is ten thousand.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "divided")
        self.play(FadeIn(rows[4][:2], shift=RIGHT * 0.2))
        self.at_word(n, "ten")
        self.play(FadeIn(rows[4][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Answer key  ·  6 to 8", GOOD)
        table, rows = self.answer_table(head, ANSWERS_B, 6)

        n = self.narrate(
            id="answers_06",
            text="Six: fifty-four thousand divided by one point zero eight is fifty thousand.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "divided")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "fifty")
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_07",
            text="Seven: after three years it is seventy-two thousand nine hundred, and after four years sixty-five thousand "
                 "six hundred and ten, so the answer is four years.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "after", occurrence=1)
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "answer")
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_08",
            text="Eight: fifty thousand times one point zero eight one six is fifty-four thousand and eighty.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "times")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "fifty-four")
        self.play(FadeIn(rows[2][2], shift=LEFT * 0.1))
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
            text="Recognise and move. The recognition cue: depreciates, decreases by a percentage every year, or population "
                 "grows, means a multiplier chain.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Recognise")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "cue")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "chain")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="lens_02",
            text="The target time: thirty-five seconds.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "target")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "thirty-five")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="lens_03",
            text="The sanity check: after two equal falls of R percent, the total fall is a little less than two R percent; "
                 "after two equal rises, a little more.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "sanity")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "less")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S15_exam_lens")

    # ==================================== 16. QUICK REVISION + SUMMARY ==========

    def summary(self):
        self.scene_start("S16_summary", title="Quick Revision and Summary")

        head = self.heading("Quick revision")
        mults = VGroup(pill("growth:   × (1 + R/100)ⁿ", GOOD, size=LABEL), pill("depreciation:   × (1 − R/100)ⁿ", BAD, size=LABEL))\
            .arrange(RIGHT, buff=0.5)
        box = VGroup(text("mixed changes: one chain of multipliers", LABEL, INK),
                     text("back in time:   ÷ multiplier", LABEL, INK),
                     text("find a rate:   the root of the total multiplier", LABEL, INK)).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        nxt = self.breadcrumb("Next", "Video 7 · Speed Tricks for Interest")
        self.stack(head, [mults, box, nxt], buff=0.7, top=0.7)
        self.no_overlap(*mults)
        self.no_overlap(*box)

        n = self.narrate(
            id="summary_01",
            text="Growth and depreciation are compound changes: multiply by one plus R over a hundred, or one minus R over a "
                 "hundred, once per period.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "plus")
        self.play(FadeIn(mults[0], shift=UP * 0.1))
        self.at_word(n, "minus")
        self.play(FadeIn(mults[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_02",
            text="Mixed changes chain in one line.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "chain")
        self.play(FadeIn(box[0], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_03",
            text="To go back in time, divide; to find a rate, take the root of the total multiplier.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "divide")
        self.play(FadeIn(box[1], shift=RIGHT * 0.2))
        self.at_word(n, "root")
        self.play(FadeIn(box[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_04",
            text="Next: speed tricks for interest.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Next")
        self.play(FadeIn(nxt, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S16_summary")

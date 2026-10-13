"""
animation.py for the LMS video generator.

Course : Pre-C-CAT - Section A - Quantitative Aptitude
Video  : Lesson 11 - Simple & Compound Interest - 01 - Introduction to Interest

Source script:
  C:\\Scripts\\Section A\\Module_2_Section_A_Quantitative_Aptitude_Part_1\\Aptitude_Scripts\\Sessions 1-4 - Interest, Profit & Loss, Time & Work\\Lesson 11 - Simple & Compound Interest\\01 - Introduction to Interest.pdf

Built on the golden-reference pattern:
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``;
  * layouts stacked with next_to and guarded with ``no_overlap``; nothing is
    ever animated onto or into another box.

Lesson 11, Video 1 of 7. First video of a new lesson: a silent breadcrumb, "now we start Lesson 11", a one-line recap of the Module Introduction (READ > MODEL > SOLVE > CHECK) and today's topic. No spoken course welcome.
The narration follows the script section by section, with numbers written as words for the voice. Tables and lists are spoken one row at a time. Every figure on screen (24%, 12,000, 62,000, 13,412, the pattern, trap, checkpoint and practice answers) is computed from the question's numbers and asserted.
Pauses: 3 s after the hook guess, the script's 10-second countdown at the checkpoint, 12 s before the practice answers.
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

METHOD = [("READ", "#4FC3F7"), ("MODEL", "#CE93D8"), ("SOLVE", "#FFB74D"), ("CHECK", "#66BB6A")]


def dec(x):
    return f"{float(x):g}"


def rs(x):
    return f"₹{int(x):,}"


def simple_interest(p, r, t):
    """I = P × R × T ÷ 100 (r in percent per period, t in the same period)."""
    return Fraction(p) * Fraction(r) * Fraction(t) / 100


# ---- the hook: ₹50,000 at 2% per month ----
LOAN, MONTHLY = 50000, 2
YEARLY = MONTHLY * 12
GUESS = LOAN * MONTHLY // 100
HUNDREDS = LOAN // 100
CHARGE = HUNDREDS * YEARLY
REPAY = LOAN + CHARGE
COMPOUNDED = round(LOAN * (Fraction(100 + MONTHLY, 100) ** 12 - 1))
assert (YEARLY, GUESS, HUNDREDS, CHARGE, REPAY, COMPOUNDED) == (24, 1000, 500, 12000, 62000, 13412)
assert simple_interest(LOAN, MONTHLY, 12) == CHARGE

# ---- second worked example: Priya ----
PRIYA_P, PRIYA_R, PRIYA_T = 15000, 8, Fraction(2) + Fraction(6, 12)
PRIYA_I = simple_interest(PRIYA_P, PRIYA_R, PRIYA_T)
PRIYA_A = PRIYA_P + PRIYA_I
assert (PRIYA_T, PRIYA_I, PRIYA_A) == (Fraction("2.5"), 3000, 18000)

# ---- the five words ----
WORDS = [("P", "Principal", "the money at the start"),
         ("R", "Rate", "the charge per ₹100 for one period"),
         ("T", "Time", "how long"),
         ("I", "Interest", "the total charge"),
         ("A", "Amount", "what you end with")]

# ---- exam patterns (answers computed) ----
PAT_1 = simple_interest(6000, "7.5", 4)
PAT_2 = simple_interest(9125, 8, Fraction(73, 365))
PAT_3 = Fraction(2, 5) * 100 / 4                         # I/P = R × T / 100, T = 4
assert (PAT_1, PAT_2, PAT_3) == (1800, 146, 10) and Fraction(73, 365) == Fraction(1, 5)
PATTERNS = [("Find I or A directly", "₹6,000 at 7.5% p.a. for 4 years", "6,000 × 7.5 × 4 ÷ 100", f"I = {rs(PAT_1)}"),
            ("Units differ", "₹9,125 at 8% p.a. for 73 days", "73 days = 1/5 year", f"I = {rs(PAT_2)}"),
            ("Interest as a fraction of P", "Interest is 2/5 of P in 4 years; find R", "R × T = 40", f"R = {PAT_3}%")]

# ---- traps: (title, question, wrong, right, rule) ----
T2_WRONG, T2_RIGHT = simple_interest(10000, 10, "2.6"), simple_interest(10000, 10, "2.5")
T3_I = 7500 - 6000
assert (T2_WRONG, T2_RIGHT) == (2600, 2500) and Fraction(7500, 6000) == Fraction(5, 4) and Fraction(T3_I, 6000) == Fraction(1, 4)
TRAPS = [("Trap 1  ·  monthly rate used as yearly", f"{rs(LOAN)} at {MONTHLY}% per month for a year.  Interest?",
          f"{MONTHLY}% of 50,000 = {rs(GUESS)}", f"{YEARLY}% of 50,000 = {rs(CHARGE)}",
          "Ask “per what?” for every rate, and “in what unit?” for every time."),
         ("Trap 2  ·  months written as a decimal", "Interest on ₹10,000 at 10% p.a. for 2 years 6 months.",
          f"T = 2.6  →  {rs(T2_WRONG)}", f"T = 2.5  →  {rs(T2_RIGHT)}",
          "6 months is half a year, not 0.6 of one.  Divide months by 12."),
         ("Trap 3  ·  amount mistaken for interest", "A = ₹7,500 and P = ₹6,000.  What fraction of P is the interest?",
          "7,500 / 6,000 = 5/4", f"I = {T3_I:,},  so 1/4",
          "The total repaid is the amount.  Subtract P first.")]

# ---- checkpoint ----
CP_P, CP_R, CP_T = 20000, Fraction("1.5"), 6
CP_PCT = CP_R * CP_T
CP_I = CP_P * CP_PCT / 100
assert (CP_PCT, CP_I) == (9, 1800)

# ---- practice (answers computed) ----
PRACTICE = [("L1", "P = ₹2,000 and I = ₹300.  Find the amount."),
            ("L1", "A shop charges 3% per month.  What is the equivalent yearly rate?"),
            ("L2", "Find the simple interest on ₹8,000 at 12% per year for 9 months."),
            ("L2", "A = ₹7,500 and P = ₹6,000.  Find the interest, and what fraction of P it is."),
            ("L2", "Find the simple interest on ₹9,125 at 8% per year for 73 days."),
            ("L3", "The SI on a sum for 4 years is 2/5 of the sum.  Find the rate per year."),
            ("L3", "₹50,000 at 1.25% per month SI for 1 year 3 months.  Interest?")]
A3 = simple_interest(8000, 12, Fraction(9, 12))
A7_PCT = Fraction("1.25") * 15
A7 = LOAN * A7_PCT / 100
assert (2000 + 300, 3 * 12, A3, A7_PCT, A7) == (2300, 36, 720, Fraction("18.75"), 9375)
ANSWERS = [("A = P + I = 2,000 + 300", rs(2300)),
           ("3% × 12", "36% per year"),
           ("9 months = 0.75 yr;  8,000 × 12 × 0.75 ÷ 100", rs(A3)),
           ("I = 7,500 − 6,000 = 1,500;  1,500 / 6,000", f"{rs(T3_I)} = 1/4 of P"),
           ("73 days = 1/5 yr;  9,125 × 8 × 1/5 ÷ 100", rs(PAT_2)),
           ("I/P = 2/5 = 40%;  R × 4 = 40", f"R = {PAT_3}% per year"),
           (f"15 months;  1.25% × 15 = {dec(A7_PCT)}% of 50,000", rs(A7))]

OBJECTIVES = [("Define P, R, T, I and A", "principal, rate, time, interest, amount: connected by A = P + I"),
              ("Convert to matching units", "rates and times, before you calculate"),
              ("Recognise three exam patterns", "the three ways exams test these basics")]
LENS = [("Recognition cue", "any rate quoted “per month”; any time in months or days"),
        ("Target time", "30 seconds for a direct question"),
        ("Sanity check", "a yearly rate is always 12 × the monthly rate")]
FORMULAS = ["A = P + I      (Amount = Principal + Interest)",
            "Monthly rate × 12 = yearly rate",
            "Months ÷ 12 = years      Days ÷ 365 = years",
            "73 days = 1/5 year"]


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


class IntroductionToInterestVideo(LMSScene):
    lesson_title = "Introduction to Interest"

    def construct(self):
        self.camera.background_color = BG

        self.intro()
        self.hook()
        self.objectives()
        self.why_this_matters()
        self.five_words()
        self.rate_has_a_period()
        self.units_must_match()
        self.per_annum_default()
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

    # ================================================== 0. INTRO ==========
    # First video of a new lesson: silent breadcrumb, "now we start Lesson 11", a one-line recap
    # of the Module Introduction, and today's topic.  No spoken course welcome.

    def intro(self):
        self.scene_start("S00_intro", title="Intro")

        crumb = self.breadcrumb("Quantitative Aptitude", "Lesson 11 · Simple & Compound Interest", "Video 1 of 7")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        lesson = pill("Lesson 11  ·  Simple & Compound Interest", RATIO, size=LABEL)
        recap = text("from the Module Introduction", SMALL, MUTED)
        method = VGroup()
        for i, (name, c) in enumerate(METHOD):
            if i:
                method.add(text("→", LABEL, MUTED))
            method.add(pill(name, c, size=LABEL))
        method.arrange(RIGHT, buff=0.3)
        title = text("Introduction to Interest", TITLE, INK, BOLD)
        today = text("today: the five words of interest, and matching units", LABEL, FOCUS)
        block = VGroup(lesson, VGroup(recap, method).arrange(DOWN, buff=0.25), title, today).arrange(DOWN, buff=0.6)
        fit_within(block, SAFE_W, SAFE_H - crumb.height - 0.9)
        block.next_to(crumb, DOWN, buff=0.6)
        self.no_overlap(crumb, lesson, recap, method, title, today)
        self.validator.check_in_frame(VGroup(crumb, block))

        n = self.narrate(
            id="intro_01",
            text="Now we start lesson eleven: simple and compound interest.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.at_word(n, "eleven")
        self.play(FadeIn(lesson, scale=1.05))
        self.wait_for_narration(n)

        n = self.narrate(
            id="intro_02",
            text="In the module introduction, you met the method: read, model, solve, check.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "introduction")
        self.play(FadeIn(recap, shift=UP * 0.1))
        self.at_word(n, "read")
        self.play(LaggedStart(*[FadeIn(m, shift=RIGHT * 0.1) for m in method], lag_ratio=0.25), run_time=1.6)
        self.wait_for_narration(n)

        n = self.narrate(
            id="intro_03",
            text="This first video introduces interest: the five words every problem uses, and the habit of matching units.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "introduces")
        self.play(FadeIn(title, shift=UP * 0.1))
        self.at_word(n, "five")
        self.play(FadeIn(today, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_intro")

    # =================================================== 1. HOOK ==========

    def hook(self):
        self.scene_start("S01_hook", title="Hook")

        head = self.heading("A loan app ad")
        track = Line(LEFT * 2.0, RIGHT * 2.0, color=MUTED, stroke_width=6)
        knob = Circle(radius=0.14, color=FOCUS, fill_color=FOCUS, fill_opacity=1).move_to(track.point_from_proportion(0.7))
        amount = VGroup(text("you need", SMALL, MUTED), text(rs(LOAN), BODY, FOCUS, BOLD)).arrange(RIGHT, buff=0.25)
        slider = VGroup(amount, VGroup(track, knob)).arrange(DOWN, buff=0.25)
        banner = text("Instant cash!", BODY, GOOD, BOLD)
        offer = text(f"Just {MONTHLY}% interest per month", LABEL, INK, BOLD)
        ad = self.card(VGroup(banner, offer, slider).arrange(DOWN, buff=0.4), width=5.8, color=GOOD)
        notes = VGroup(text(f"“{MONTHLY}%” sounds like nothing", LABEL, MUTED),
                       pill("extra paid in a year = ?", FOCUS, size=LABEL),
                       VGroup(text("most people guess", SMALL, MUTED), pill(rs(GUESS), BAD, size=LABEL)).arrange(RIGHT, buff=0.25),
                       text(f"{MONTHLY}% of 50,000 = {GUESS:,}:  feels too small to matter", SMALL, MUTED),
                       pill("what is the ad hiding?", RATIO, size=LABEL),
                       text("goal: read any interest offer in 10 seconds", SMALL, GOOD, BOLD))\
            .arrange(DOWN, buff=0.32, aligned_edge=LEFT)
        row = VGroup(ad, notes).arrange(RIGHT, buff=0.8)
        self.stack(head, [row], top=0.6)
        self.no_overlap(ad, notes)

        n = self.narrate(
            id="hook_01",
            text="A loan app flashes an ad: instant cash, just two percent interest per month.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "ad")
        self.play(FadeIn(ad[0]), FadeIn(banner, scale=1.1))
        self.at_word(n, "two")
        self.play(FadeIn(offer, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_02",
            text="You need fifty thousand rupees for a new laptop before your internship starts, and two percent sounds like "
                 "nothing.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "fifty")
        self.play(FadeIn(slider, shift=UP * 0.1))
        self.at_word(n, "nothing")
        self.play(FadeIn(notes[0], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_03",
            text="So roughly how much extra will you pay in a year? Take a guess before we go on.",
            voice="default",
            subtitle=True,
            pause_after=3.0,
        )
        self.at_word(n, "extra")
        self.play(FadeIn(notes[1], shift=LEFT * 0.1))
        self.at_word(n, "guess")
        self.play(Indicate(notes[1], color=FOCUS, scale_factor=1.06))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="hook_04",
            text="Most people say around one thousand rupees, because two percent of fifty thousand is one thousand, and it "
                 "feels small enough to ignore.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "thousand", occurrence=1)
        self.play(FadeIn(notes[2], shift=LEFT * 0.1))
        self.at_word(n, "because")
        self.play(FadeIn(notes[3], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_05",
            text="Hold that guess. By the end of this video you'll know exactly what that ad is hiding, and you'll be able to "
                 "read any interest offer in about ten seconds.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Hold")
        self.play(Indicate(notes[2][1], color=BAD, scale_factor=1.15))
        self.at_word(n, "hiding")
        self.play(FadeIn(notes[4], shift=LEFT * 0.1))
        self.at_word(n, "ten")
        self.play(FadeIn(notes[5], shift=LEFT * 0.1))
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
            text="Define principal, rate, time, interest and amount, and connect them with A equals P plus I.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Define")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "connect")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="obj_03",
            text="Convert rates and times into matching units before you calculate.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Convert")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "before")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="obj_04",
            text="Recognise the three ways exams test these basics.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Recognise")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "exams")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_objectives")

    # ========================================== 3. WHY THIS MATTERS ==========

    def why_this_matters(self):
        self.scene_start("S03_why_this_matters", title="Why This Matters")

        head = self.heading("Interest")
        letters = VGroup(*[pill(l, WORD, size=BODY) for l, _, _ in WORDS]).arrange(RIGHT, buff=0.35)
        price = pill("the price of using someone else's money for a period of time", FOCUS, size=LABEL)
        uses = VGroup(*[pill(u, RATIO) for u in ["loans", "deposits", "EMIs", "credit cards"]]).arrange(RIGHT, buff=0.3)
        repeated = text("one of the most repeated topics in aptitude papers", LABEL, INK)
        mistake = pill("the early mistake: mixing up the units of the rate and the time", BAD, size=LABEL)
        self.stack(head, [letters, price, uses, repeated, mistake], buff=0.5, top=0.6)

        n = self.narrate(
            id="why_01",
            text="Interest is the price of using someone else's money for a period of time.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Interest")
        self.play(FadeIn(head, shift=DOWN * 0.2), LaggedStart(*[FadeIn(l, scale=0.7) for l in letters], lag_ratio=0.12))
        self.at_word(n, "price")
        self.play(FadeIn(price, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="why_02",
            text="Loans, deposits, EMIs and credit cards all run on it.",
            voice="default",
            subtitle=True,
        )
        for chip, spoken in zip(uses, ["Loans", "deposits", "EMIs", "credit"]):
            self.at_word(n, spoken)
            self.play(FadeIn(chip, shift=UP * 0.1), run_time=0.4)
        self.wait_for_narration(n)

        n = self.narrate(
            id="why_03",
            text="In aptitude papers it is one of the most repeated topics, and nearly every early mistake comes from one "
                 "place: mixing up the units of the rate and the time.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "repeated")
        self.play(FadeIn(repeated, shift=UP * 0.1))
        self.at_word(n, "mixing")
        self.play(FadeIn(mistake, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_why_this_matters")

    # ================================ 4. CONCEPT 1: THE FIVE WORDS ==========

    def five_words(self):
        self.scene_start("S04_five_words", title="Concept 1 - Five Words Describe Every Interest Problem")

        head = self.heading("Five words describe every interest problem")
        table, rows = self.placed_table(head, ["Letter", "Word", "What it is"], [list(w) for w in WORDS], [1.7, 3.0, 7.4],
                                        size=LABEL, room=2.2)
        for row in rows:
            row[0].set_color(WORD)
            row[1].set_color(WORD)
        formula = pill("A = P + I", GOOD, size=BODY).next_to(table, DOWN, buff=0.5)
        self.no_overlap(table, formula)
        self.validator.check_in_frame(formula)

        n = self.narrate(
            id="words_01",
            text="Five words describe every interest problem.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Five")
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.wait_for_narration(n)

        n = self.narrate(
            id="words_02",
            text="Principal, P, is the money at the start.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Principal")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "start")
        self.play(FadeIn(rows[0][2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="words_03",
            text="Rate, R, is the charge per hundred rupees for one period.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Rate")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "charge")
        self.play(FadeIn(rows[1][2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="words_04",
            text="Time, T, is how long.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Time")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "long")
        self.play(FadeIn(rows[2][2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="words_05",
            text="Interest, I, is the total charge.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Interest")
        self.play(FadeIn(rows[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "total")
        self.play(FadeIn(rows[3][2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="words_06",
            text="Amount, A, is what you end with: A equals P plus I.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Amount")
        self.play(FadeIn(rows[4][:2], shift=RIGHT * 0.2))
        self.at_word(n, "end")
        self.play(FadeIn(rows[4][2], shift=RIGHT * 0.2))
        self.at_word(n, "equals")
        self.play(FadeIn(formula, scale=1.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_five_words")

    # ============================ 5. CONCEPT 2: A RATE HAS A PERIOD ==========

    def rate_has_a_period(self):
        self.scene_start("S05_rate_has_a_period", title="Concept 2 - A Rate Always Has a Period Attached")

        head = self.heading("A rate always has a period attached")
        number, period = text(f"{MONTHLY}%", TITLE, FOCUS, BOLD), text("per month", TITLE, RATIO, BOLD)
        rate = VGroup(number, period).arrange(RIGHT, buff=0.3, aligned_edge=DOWN)
        hundred = Rectangle(width=6.0, height=0.45, color=MUTED, fill_color=MUTED, fill_opacity=0.25)
        charge = Rectangle(width=6.0 * MONTHLY / 100, height=0.45, color=FOCUS, fill_color=FOCUS, fill_opacity=0.9)
        bar = VGroup(hundred, charge).arrange(RIGHT, buff=0.12)
        meaning = text(f"₹{MONTHLY} for every ₹100, every month", LABEL, INK)
        like = VGroup(text("the period is part of the number", LABEL, RATIO, BOLD),
                      text("just as “per second” is part of a speed:  40 MB per second", SMALL, MUTED)).arrange(DOWN, buff=0.2)
        self.stack(head, [rate, bar, meaning, like], buff=0.5, top=0.7)

        n = self.narrate(
            id="period_01",
            text="A rate always has a period attached.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "period")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="period_02",
            text="Two percent per month means two rupees for every hundred rupees, every month.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "percent")
        self.play(FadeIn(rate, shift=UP * 0.1))
        self.at_word(n, "rupees", occurrence=1)
        self.play(FadeIn(hundred), GrowFromEdge(charge, LEFT), FadeIn(meaning, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="period_03",
            text="The period is part of the number, just as per second is part of a speed.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "part", occurrence=1)
        self.play(Indicate(period, color=RATIO, scale_factor=1.1), FadeIn(like[0], shift=UP * 0.1))
        self.at_word(n, "speed")
        self.play(FadeIn(like[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_rate_has_a_period")

    # ================================ 6. CONCEPT 3: UNITS MUST MATCH ==========

    def units_must_match(self):
        self.scene_start("S06_units_must_match", title="Concept 3 - Units Must Match Before Any Calculation")

        head = self.heading("Units must match before any calculation")
        months = VGroup(*[pill(f"₹{MONTHLY}", MUTED) for _ in range(12)]).arrange(RIGHT, buff=0.1)
        total = text(f"12 months × ₹{MONTHLY}  =  ₹{YEARLY} for every ₹100", LABEL, INK)
        same = pill(f"{MONTHLY}% per month  =  {YEARLY}% per year", GOOD, size=BODY)
        convert = VGroup(text("months ÷ 12  =  years", LABEL, WORD, BOLD), text("days ÷ 365  =  years", LABEL, RATIO, BOLD))\
            .arrange(RIGHT, buff=1.0)
        self.stack(head, [months, total, same, convert], buff=0.5, top=0.7)

        n = self.narrate(
            id="match_01",
            text="Units must match before any calculation.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "match")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="match_02",
            text="Over twelve months, two rupees per hundred per month becomes twenty-four rupees per hundred.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "twelve")
        self.play(LaggedStart(*[FadeIn(m, shift=UP * 0.1) for m in months], lag_ratio=0.08), run_time=1.4)
        self.at_word(n, "twenty-four")
        self.play(FadeIn(total, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="match_03",
            text="So two percent per month equals twenty-four percent per year.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "equals")
        self.play(FadeIn(same, scale=1.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="match_04",
            text="To convert time, divide months by twelve, and days by three hundred and sixty-five.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "months")
        self.play(FadeIn(convert[0], shift=UP * 0.1))
        self.at_word(n, "days")
        self.play(FadeIn(convert[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_units_must_match")

    # ============================== 7. CONCEPT 4: "P.A." IS THE DEFAULT ==========

    def per_annum_default(self):
        self.scene_start("S07_per_annum_default", title="Concept 4 - Per Annum Is the Default")

        head = self.heading("“p.a.” is the default")
        meaning = pill("p.a.  =  per annum  =  per year", FOCUS, size=BODY)
        no_period = VGroup(text("rate with no period:", LABEL, MUTED), text("“at 8%”", LABEL, INK, BOLD), text("→", LABEL, MUTED),
                           text("8% per year", LABEL, GOOD, BOLD)).arrange(RIGHT, buff=0.3)
        in_months = VGroup(text("time in months:", LABEL, MUTED), text("9 months", LABEL, INK, BOLD), text("→", LABEL, MUTED),
                           text(f"{dec(Fraction(9, 12))} year", LABEL, GOOD, BOLD)).arrange(RIGHT, buff=0.3)
        in_days = VGroup(text("time in days:", LABEL, MUTED), text("73 days", LABEL, INK, BOLD), text("→", LABEL, MUTED),
                         text("1/5 year", LABEL, GOOD, BOLD)).arrange(RIGHT, buff=0.3)
        self.stack(head, [meaning, no_period, in_months, in_days], buff=0.6, top=0.8)

        n = self.narrate(
            id="pa_01",
            text="Per annum, written p.a., is the default.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "annum")
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(meaning, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="pa_02",
            text="If a question gives a rate with no period, treat it as per annum, per year.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "no")
        self.play(FadeIn(no_period[:2], shift=RIGHT * 0.1))
        self.at_word(n, "annum")
        self.play(FadeIn(no_period[2:], shift=RIGHT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="pa_03",
            text="If it gives time in months or days, convert to years.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "months")
        self.play(FadeIn(in_months[:2], shift=RIGHT * 0.1), FadeIn(in_days[:2], shift=RIGHT * 0.1))
        self.at_word(n, "convert")
        self.play(FadeIn(in_months[2:], shift=RIGHT * 0.1), FadeIn(in_days[2:], shift=RIGHT * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S07_per_annum_default")

    # ============================================== 8. FORMULA BOX ==========

    def formula_box(self):
        self.scene_start("S08_formula_box", title="Formula Box")

        head = self.heading("Formula box", GOOD)
        lines = VGroup(*[text(f, BODY, INK if i else GOOD, BOLD if i == 0 else NORMAL) for i, f in enumerate(FORMULAS)])\
            .arrange(DOWN, buff=0.45, aligned_edge=LEFT)
        box = self.card(lines, width=11.0, color=GOOD, pad=0.5)
        self.stack(head, [box], top=0.8)

        n = self.narrate(
            id="formula_01",
            text="Here is the formula box. Amount equals principal plus interest.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "box")
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(box[0]))
        self.at_word(n, "Amount")
        self.play(FadeIn(lines[0], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_02",
            text="Monthly rate times twelve is the yearly rate.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "twelve")
        self.play(FadeIn(lines[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_03",
            text="Months divided by twelve, or days divided by three hundred and sixty-five, give years. So seventy-three days "
                 "is one fifth of a year.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Months")
        self.play(FadeIn(lines[2], shift=RIGHT * 0.2))
        self.at_word(n, "seventy-three")
        self.play(FadeIn(lines[3], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S08_formula_box")

    # ============================================== 9. THE ANALOGY ==========

    def analogy(self):
        self.scene_start("S09_analogy", title="The Analogy - Rent for Money")

        head = self.heading("Interest is rent, for money instead of a flat")
        table, rows = self.placed_table(head, ["Renting a flat", "Borrowing money"],
                                        [["the flat", "Principal: the money you borrow"],
                                         ["the rent, quoted per month", "Interest: quoted per period"],
                                         ["stay longer, pay more rent", "Amount: total paid over time"]],
                                        [5.2, 6.6], size=LABEL, room=2.9)
        for row in rows:
            row[1].set_color(WORD)
        stops = VGroup(text("Where the analogy stops", LABEL, BAD, BOLD),
                       text("rent: a fixed rupee figure", LABEL, MUTED),
                       text("interest: a percentage, so it scales with how much you borrow", LABEL, INK))\
            .arrange(DOWN, buff=0.22)
        stops.next_to(table, DOWN, buff=0.6)
        self.no_overlap(table, stops)
        self.validator.check_in_frame(stops)

        n = self.narrate(
            id="analogy_01",
            text="Think of interest as rent, but for money instead of a flat.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "rent")
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_02",
            text="The money you borrow is the flat.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "flat")
        self.play(FadeIn(rows[0][0], shift=RIGHT * 0.2), FadeIn(rows[0][1], shift=LEFT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_03",
            text="The rent you pay for using it is the interest, quoted per period.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "rent")
        self.play(FadeIn(rows[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "interest")
        self.play(FadeIn(rows[1][1], shift=LEFT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_04",
            text="The longer you stay, the more rent you pay.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "longer")
        self.play(FadeIn(rows[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "more")
        self.play(FadeIn(rows[2][1], shift=LEFT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_05",
            text="Where the analogy stops: a flat's rent is a fixed rupee figure.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "stops")
        self.play(FadeIn(stops[0], shift=UP * 0.1))
        self.at_word(n, "fixed")
        self.play(FadeIn(stops[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_06",
            text="Interest is quoted as a percentage, so it scales with how much you borrow.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "percentage")
        self.play(FadeIn(stops[2], shift=UP * 0.1))
        self.at_word(n, "scales")
        self.play(Indicate(stops[2], color=FOCUS, scale_factor=1.04))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S09_analogy")

    # ================================ 10. WORKED EXAMPLE: CLOSING THE HOOK ==========

    def hook_solved(self):
        self.scene_start("S10_hook_solved", title="Worked Example - Closing the Hook")

        head = self.heading(f"The ad:  {rs(LOAN)} at {MONTHLY}% per month")
        work = VGroup(text(f"{MONTHLY}% per month × 12  =  {YEARLY}% per year", LABEL, INK),
                      text(f"₹{YEARLY} for every ₹100", LABEL, FOCUS, BOLD),
                      text(f"{rs(LOAN)}  =  {HUNDREDS} hundreds", LABEL, INK),
                      text(f"{HUNDREDS} × ₹{YEARLY}  =  {rs(CHARGE)} a year", LABEL, GOOD, BOLD),
                      text(f"you repay {rs(REPAY)}", LABEL, INK)).arrange(DOWN, buff=0.35, aligned_edge=LEFT)
        guess = VGroup(text("the guess", SMALL, MUTED), pill(rs(GUESS), BAD, size=LABEL)).arrange(RIGHT, buff=0.25)
        real = VGroup(text("the real charge", SMALL, MUTED), pill(rs(CHARGE), GOOD, size=BODY)).arrange(RIGHT, buff=0.25)
        verdict = VGroup(guess, real,
                         text("rate quoted in the smallest unit", SMALL, RATIO, BOLD),
                         text("compounded monthly (Video 3):", SMALL, MUTED),
                         text(f"about {rs(COMPOUNDED)}", LABEL, BAD, BOLD)).arrange(DOWN, buff=0.32, aligned_edge=LEFT)
        row = VGroup(work, verdict).arrange(RIGHT, buff=0.9, aligned_edge=UP)
        self.stack(head, [row], top=0.7)
        self.no_overlap(work, verdict)
        strike = Line(guess[1].get_left() + LEFT * 0.05, guess[1].get_right() + RIGHT * 0.05, color=BAD, stroke_width=4)

        n = self.narrate(
            id="solved_01",
            text="Two percent per month is twenty-four percent per year: twenty-four rupees for every hundred rupees.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "twenty-four", occurrence=1)
        self.play(FadeIn(work[0], shift=RIGHT * 0.1))
        self.at_word(n, "rupees", occurrence=1)
        self.play(FadeIn(work[1], shift=RIGHT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_02",
            text="You've borrowed fifty thousand rupees, which is five hundred hundreds.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "hundreds")
        self.play(FadeIn(work[2], shift=RIGHT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_03",
            text="So the yearly charge is five hundred times twenty-four rupees, which is twelve thousand rupees, and you "
                 "repay sixty-two thousand.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "times")
        self.play(FadeIn(work[3], shift=RIGHT * 0.1))
        self.at_word(n, "sixty-two")
        self.play(FadeIn(work[4], shift=RIGHT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_04",
            text="Not one thousand rupees extra. Twelve thousand.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Not")
        self.play(FadeIn(guess, shift=LEFT * 0.1))
        self.play(Create(strike), run_time=0.4)
        self.at_word(n, "Twelve")
        self.play(FadeIn(real, scale=1.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_05",
            text="The ad wasn't lying; it quoted the rate in the smallest unit so it sounds small.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "smallest")
        self.play(FadeIn(verdict[2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_06",
            text="And if the app compounds monthly, which you'll learn in video three, the charge is even higher: about "
                 "thirteen thousand four hundred and twelve rupees.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "compounds")
        self.play(FadeIn(verdict[3], shift=LEFT * 0.1))
        self.at_word(n, "thirteen")
        self.play(FadeIn(verdict[4], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S10_hook_solved")

    # ================================ 11. A SECOND WORKED EXAMPLE ==========

    def second_example(self):
        self.scene_start("S11_second_example", title="A Second Worked Example")

        head = self.heading("Priya's deposit  ·  simple interest")
        given = given_chips(rs(PRIYA_P), f"{PRIYA_R}% per year", "2 years 6 months")
        ask = pill("find I and A", FOCUS, size=LABEL)
        top = VGroup(given, ask).arrange(RIGHT, buff=0.6)
        steps = VGroup()
        for i, (what, result) in enumerate([
                ("convert the time:  2 years 6 months", f"=  {dec(PRIYA_T)} years"),
                (f"Interest  =  15,000 × {PRIYA_R} × {dec(PRIYA_T)} ÷ 100", f"=  {rs(PRIYA_I)}"),
                (f"Amount  =  15,000 + {int(PRIYA_I):,}", f"=  {rs(PRIYA_A)}")]):
            steps.add(VGroup(pill(str(i + 1), WORD, size=SMALL), text(what, LABEL, INK), text(result, LABEL, GOOD, BOLD))
                      .arrange(RIGHT, buff=0.3))
        steps.arrange(DOWN, buff=0.5, aligned_edge=LEFT)
        self.stack(head, [top, steps], buff=0.8, top=0.7)
        self.no_overlap(given, ask)
        self.no_overlap(*steps)

        n = self.narrate(
            id="priya_01",
            text="Priya deposits fifteen thousand rupees at eight percent per year simple interest. Find the interest for two "
                 "years six months, and the amount.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "fifteen")
        self.play(FadeIn(given[0], shift=UP * 0.1))
        self.at_word(n, "eight")
        self.play(FadeIn(given[1], shift=UP * 0.1))
        self.at_word(n, "six")
        self.play(FadeIn(given[2], shift=UP * 0.1))
        self.at_word(n, "amount")
        self.play(FadeIn(ask, shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="priya_02",
            text="Step one: convert the time. Two years six months is two point five years.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "convert")
        self.play(FadeIn(steps[0][:2], shift=RIGHT * 0.1))
        self.at_word(n, "point")
        self.play(FadeIn(steps[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="priya_03",
            text="Step two: interest is fifteen thousand times eight times two point five, divided by a hundred, which is "
                 "three thousand rupees.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "interest")
        self.play(FadeIn(steps[1][:2], shift=RIGHT * 0.1))
        self.at_word(n, "three")
        self.play(FadeIn(steps[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="priya_04",
            text="Step three: amount is fifteen thousand plus three thousand, which is eighteen thousand rupees.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "plus")
        self.play(FadeIn(steps[2][:2], shift=RIGHT * 0.1))
        self.at_word(n, "eighteen")
        self.play(FadeIn(steps[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S11_second_example")

    # ============================================ 12. EXAM PATTERNS ==========

    def exam_patterns(self):
        self.scene_start("S12_exam_patterns", title="Exam Patterns - How This Is Asked")

        head = self.heading("Exam patterns: how this is asked")
        table, rows = self.placed_table(head, ["Pattern", "Example", "Method", "Answer"], [list(p) for p in PATTERNS],
                                        [3.4, 4.6, 3.3, 1.9], room=1.2)
        for row in rows:
            row[0].set_color(WORD)
            row[3].set_color(GOOD)

        n = self.narrate(
            id="patterns_01",
            text="Exams ask this in three ways.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "three")
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.wait_for_narration(n)

        n = self.narrate(
            id="patterns_02",
            text="First, find the interest or amount directly. Six thousand rupees at seven point five percent for four years "
                 "gives interest of one thousand eight hundred rupees.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "directly")
        self.play(FadeIn(rows[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "Six")
        self.play(FadeIn(rows[0][1], shift=RIGHT * 0.2))
        self.at_word(n, "gives")
        self.play(FadeIn(rows[0][2], shift=RIGHT * 0.2), FadeIn(rows[0][3], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="patterns_03",
            text="Second, the units differ. For seventy-three days, use one fifth of a year: the interest on nine thousand one "
                 "hundred and twenty-five rupees at eight percent is one hundred and forty-six rupees.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "differ")
        self.play(FadeIn(rows[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "seventy-three")
        self.play(FadeIn(rows[1][1], shift=RIGHT * 0.2), FadeIn(rows[1][2], shift=RIGHT * 0.2))
        self.at_word(n, "forty-six")
        self.play(FadeIn(rows[1][3], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="patterns_04",
            text="Third, interest as a fraction of the principal. If the interest is two fifths of P in four years, then R "
                 "times T is forty, so R is ten percent.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "fraction")
        self.play(FadeIn(rows[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "fifths")
        self.play(FadeIn(rows[2][1], shift=RIGHT * 0.2))
        self.at_word(n, "forty")
        self.play(FadeIn(rows[2][2], shift=RIGHT * 0.2))
        self.at_word(n, "ten")
        self.play(FadeIn(rows[2][3], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S12_exam_patterns")

    # ================================ 13. TRAPS AND CONFUSING QUESTIONS ==========

    def show_trap(self, trap):
        """Lay out one trap.  Returns (head, question, wrong card, right card, rule)."""
        title, question, wrong, right, rule = trap
        head = self.heading(title, BAD)
        q = fitted_text(question, SAFE_W - 1.0, BODY, INK, NORMAL, max_lines=2)
        pair = self.verdict_pair(wrong, right)
        rule_pill = pill(rule, FOCUS, size=LABEL)
        self.stack(head, [q, pair, rule_pill], buff=0.7, top=0.8)
        self.no_overlap(pair[0], pair[1])
        return head, q, pair[0], pair[1], rule_pill

    def traps(self):
        self.scene_start("S13_traps", title="Traps and Confusing Questions")

        head, q, wrong, right, rule = self.show_trap(TRAPS[0])

        n = self.narrate(
            id="trap1_01",
            text="Trap one: a monthly rate used as a yearly rate. Fifty thousand rupees at two percent per month for a year.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "monthly")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "Fifty")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="trap1_02",
            text="The wrong instinct is one thousand rupees. The correct answer is twelve thousand.",
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
            text="The rule: ask per what, for every rate, and in what unit, for every time.",
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
            text="Trap two: months written as a decimal. Interest on ten thousand rupees at ten percent per annum for two years "
                 "six months.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "decimal")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "Interest")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="trap2_02",
            text="The wrong instinct uses T as two point six, giving two thousand six hundred rupees. The correct T is two "
                 "point five, giving two thousand five hundred.",
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
            text="The rule: six months is half a year, not zero point six of one. Convert months by dividing by twelve.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "rule")
        self.play(FadeIn(rule, shift=UP * 0.1))
        self.at_word(n, "dividing")
        self.play(Indicate(rule, color=FOCUS, scale_factor=1.04))
        self.wait_for_narration(n)
        self.clear_stage()

        head, q, wrong, right, rule = self.show_trap(TRAPS[2])

        n = self.narrate(
            id="trap3_01",
            text="Trap three: the amount mistaken for the interest. A is seven thousand five hundred rupees and P is six "
                 "thousand. What fraction of P is the interest?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "mistaken")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "seven")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.at_word(n, "fraction")
        self.play(Indicate(q, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="trap3_02",
            text="The wrong instinct divides seven thousand five hundred by six thousand, giving five fourths. Correctly, the "
                 "interest is one thousand five hundred, so the fraction is one fourth.",
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
            text="The rule: the total repaid is the amount, so subtract P first.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "rule")
        self.play(FadeIn(rule, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S13_traps")

    # =============================================== 14. CHECKPOINT ==========

    def checkpoint(self):
        self.scene_start("S14_checkpoint", title="Checkpoint")

        head = self.heading("Checkpoint  ·  your turn")
        given = given_chips(rs(CP_P), f"{dec(CP_R)}% per month", f"{CP_T} months")
        ask = pill("interest = ?   match the units first", FOCUS, size=LABEL)
        match = text("rate per month  ↔  time in months:  the units already match", LABEL, GOOD)
        work = VGroup(text(f"{dec(CP_R)}% × {CP_T}  =  {dec(CP_PCT)}%", BODY, INK),
                      text(f"{dec(CP_PCT)}% of {rs(CP_P)}  =  {rs(CP_I)}", BODY, GOOD, BOLD)).arrange(RIGHT, buff=0.9)
        self.stack(head, [given, ask, match, work], buff=0.6, top=0.7)

        n = self.narrate(
            id="check_01",
            text="Your turn. You borrow twenty thousand rupees at one point five percent per month for six months. How much "
                 "interest do you pay? Pause and match the units first.",
            voice="default",
            subtitle=True,
            pause_after=10.0,
        )
        self.at_word(n, "turn")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "twenty")
        self.play(FadeIn(given[0], shift=UP * 0.1))
        self.at_word(n, "point")
        self.play(FadeIn(given[1], shift=UP * 0.1))
        self.at_word(n, "six")
        self.play(FadeIn(given[2], shift=UP * 0.1))
        self.at_word(n, "interest")
        self.play(FadeIn(ask, shift=UP * 0.1))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="check_02",
            text="The rate is per month and the time is in months, so they already match.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "match")
        self.play(FadeIn(match, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="check_03",
            text="One point five percent times six is nine percent, and nine percent of twenty thousand is one thousand eight "
                 "hundred rupees.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "times")
        self.play(FadeIn(work[0], shift=UP * 0.1))
        self.at_word(n, "eight")
        self.play(FadeIn(work[1], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S14_checkpoint")

    # ======================================== 15. PRACTICE QUESTIONS ==========

    def practice(self):
        self.scene_start("S15_practice", title="Practice Questions")

        head = self.heading("Practice  ·  seven questions")
        steps = pill("use the four steps", MUTED).next_to(head, RIGHT, buff=0.4)
        table, rows = self.placed_table(head, ["Level", "Question"],
                                        [[f"{level}  ·  {i + 1}", q] for i, (level, q) in enumerate(PRACTICE)], [1.6, 11.0],
                                        room=1.3)
        table.to_edge(LEFT, buff=SAFE)
        level_cols = {"L1": GOOD, "L2": RATIO, "L3": BAD}
        for row, (level, _) in zip(rows, PRACTICE):
            row[0].set_color(level_cols[level])
        self.no_overlap(head, steps)
        self.validator.check_in_frame(VGroup(head, steps, table))

        n = self.narrate(
            id="practice_01",
            text="Try each one with the four steps before you look at the key.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "four")
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(steps, shift=LEFT * 0.1), FadeIn(table[0]))
        self.wait_for_narration(n)

        n = self.narrate(
            id="practice_02",
            text="Level one, question one: P is two thousand rupees and I is three hundred; find the amount. Question two: a "
                 "shop charges three percent per month; what is the equivalent yearly rate?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "amount")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "shop")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="practice_03",
            text="Level two, question three: find the simple interest on eight thousand rupees at twelve percent per year for "
                 "nine months. Question four: A is seven thousand five hundred and P is six thousand; find the interest, and "
                 "what fraction of P it is. Question five: find the simple interest on nine thousand one hundred and "
                 "twenty-five rupees at eight percent per year for seventy-three days.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "months")
        self.play(FadeIn(rows[2], shift=RIGHT * 0.2))
        self.at_word(n, "fraction")
        self.play(FadeIn(rows[3], shift=RIGHT * 0.2))
        self.at_word(n, "days")
        self.play(FadeIn(rows[4], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="practice_04",
            text="Level three, question six: the simple interest on a sum for four years is two fifths of the sum; find the "
                 "rate per year. Question seven: a loan of fifty thousand rupees is taken at one point two five percent per "
                 "month simple interest, for one year three months; find the interest.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "fifths")
        self.play(FadeIn(rows[5], shift=RIGHT * 0.2))
        self.at_word(n, "loan")
        self.play(FadeIn(rows[6], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="practice_05",
            text="Pause the video and solve all seven.",
            voice="default",
            subtitle=True,
            pause_after=12.0,
        )
        self.at_word(n, "Pause")
        self.play(Indicate(steps, color=FOCUS, scale_factor=1.05))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        self.clear_stage()
        self.scene_end("S15_practice")

    # ================================================= 16. ANSWERS ==========

    def answers(self):
        self.scene_start("S16_answers", title="Answer Key, with Reasoning")

        head = self.heading("Answer key, with reasoning", GOOD)
        table, rows = self.placed_table(head, ["#", "Reasoning", "Answer"],
                                        [[str(i + 1), how, ans] for i, (how, ans) in enumerate(ANSWERS)], [0.8, 8.3, 3.6])
        for row in rows:
            row[0].set_color(MUTED)
            row[2].set_color(GOOD)

        n = self.narrate(
            id="answers_01",
            text="One: amount is principal plus interest, two thousand plus three hundred: two thousand three hundred rupees.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "plus", occurrence=1)
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "rupees")
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_02",
            text="Two: three percent times twelve is thirty-six percent per year.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "times")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "thirty-six")
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_03",
            text="Three: nine months is zero point seven five of a year, so the interest is seven hundred and twenty rupees.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "months")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "twenty")
        self.play(FadeIn(rows[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_04",
            text="Four: interest is seven thousand five hundred minus six thousand, which is one thousand five hundred: one "
                 "fourth of P, or twenty-five percent.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "minus")
        self.play(FadeIn(rows[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "fourth")
        self.play(FadeIn(rows[3][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_05",
            text="Five: seventy-three days is one fifth of a year, so the interest is one hundred and forty-six rupees.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "days")
        self.play(FadeIn(rows[4][:2], shift=RIGHT * 0.2))
        self.at_word(n, "forty-six")
        self.play(FadeIn(rows[4][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_06",
            text="Six: the interest is forty percent of P, so R times four is forty, and R is ten percent per year.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "forty", occurrence=1)
        self.play(FadeIn(rows[5][:2], shift=RIGHT * 0.2))
        self.at_word(n, "ten")
        self.play(FadeIn(rows[5][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_07",
            text="Seven: one year three months is fifteen months, one point two five percent times fifteen is eighteen point "
                 "seven five percent, and that of fifty thousand is nine thousand three hundred and seventy-five rupees.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "fifteen", occurrence=1)
        self.play(FadeIn(rows[6][:2], shift=RIGHT * 0.2))
        self.at_word(n, "seventy-five")
        self.play(FadeIn(rows[6][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S16_answers")

    # =============================================== 17. EXAM LENS ==========

    def exam_lens(self):
        self.scene_start("S17_exam_lens", title="Exam Lens - Before You Calculate")

        head = self.heading("Exam lens: before you calculate", RATIO)
        blocks = two_line_blocks(LENS, RATIO)
        wrong_period = text("annual interest close to one month's?  You used the wrong period.", SMALL, BAD, BOLD)
        self.stack(head, [*blocks, wrong_period], buff=0.5, top=0.7, align=LEFT)

        n = self.narrate(
            id="lens_01",
            text="Before you calculate, three checks. The recognition cue: any rate quoted per month, and any time in months "
                 "or days.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "three")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "cue")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "quoted")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="lens_02",
            text="The target time: thirty seconds for a direct question.",
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
            text="The sanity check: a yearly rate is always twelve times the monthly rate. If your annual interest is close to "
                 "one month's, you used the wrong period.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "sanity")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "twelve")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.at_word(n, "wrong")
        self.play(FadeIn(wrong_period, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S17_exam_lens")

    # ==================================== 18. QUICK REVISION + SUMMARY ==========

    def summary(self):
        self.scene_start("S18_summary", title="Quick Revision and Summary")

        head = self.heading("Quick revision")
        learned = VGroup(pill("five words:  P  R  T  I  A", WORD, size=LABEL), pill("A = P + I", GOOD, size=LABEL),
                         pill("match the units first", FOCUS, size=LABEL)).arrange(RIGHT, buff=0.4)
        trap = VGroup(pill("monthly rate  ≠  yearly rate", BAD, size=LABEL), pill("ask:  “per what?”", FOCUS, size=LABEL))\
            .arrange(RIGHT, buff=0.5)
        box = VGroup(text("monthly rate × 12 = yearly rate", LABEL, INK), text("months ÷ 12 = years", LABEL, INK),
                     text("days ÷ 365 = years", LABEL, INK)).arrange(RIGHT, buff=0.7)
        nxt = self.breadcrumb("Next", "Video 2 · Simple Interest: Finding P, R, T")
        self.stack(head, [learned, trap, box, nxt], buff=0.7, top=0.7)
        self.no_overlap(*learned)
        self.no_overlap(*trap)
        self.no_overlap(*box)

        n = self.narrate(
            id="summary_01",
            text="You learned the five words of interest, A equals P plus I, and the most important habit in this lesson: "
                 "match the period of the rate with the unit of the time before doing anything else.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        for chip, spoken in zip(learned, ["five", "equals", "match"]):
            self.at_word(n, spoken)
            self.play(FadeIn(chip, shift=UP * 0.1), run_time=0.45)
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_02",
            text="Remember the trap: a monthly rate is not a yearly rate. Ask per what, every time.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "trap")
        self.play(FadeIn(trap[0], shift=UP * 0.1))
        self.at_word(n, "Ask")
        self.play(FadeIn(trap[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_03",
            text="For revision: monthly rate times twelve is the yearly rate, months divided by twelve are years, and days "
                 "divided by three hundred and sixty-five are years.",
            voice="default",
            subtitle=True,
        )
        for line, spoken in zip(box, ["times", "months", "days"]):
            self.at_word(n, spoken)
            self.play(FadeIn(line, shift=UP * 0.1), run_time=0.45)
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_04",
            text="Next: simple interest, finding P, R and T.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Next")
        self.play(FadeIn(nxt, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S18_summary")

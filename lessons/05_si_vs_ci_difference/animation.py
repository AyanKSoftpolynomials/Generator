"""
animation.py for the LMS video generator.

Course : Pre-C-CAT - Section A - Quantitative Aptitude
Video  : Lesson 11 - Simple & Compound Interest - 05 - SI vs CI Difference

Source script:
  C:\\Scripts\\Section A\\Module_2_Section_A_Quantitative_Aptitude_Part_1\\Aptitude_Scripts\\Sessions 1-4 - Interest, Profit & Loss, Time & Work\\Lesson 11 - Simple & Compound Interest\\05 - SI vs CI Difference.pdf

Built on the golden-reference pattern:
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``;
  * layouts stacked with next_to and guarded with ``no_overlap``; nothing is
    ever animated onto or into another box.

Lesson 11, Video 5 of 7. Not the first video of the lesson: a silent breadcrumb, a one-line recap of Video 4, then today's topic. No spoken course welcome.
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
    """Rupees in the Indian grouping the script uses."""
    digits = str(round(x))
    head, tail = digits[:-3], digits[-3:]
    groups = []
    while len(head) > 2:
        groups.insert(0, head[-2:])
        head = head[:-2]
    if head:
        groups.insert(0, head)
    return "₹" + ",".join(groups + [tail])


def diff_2(p, r):
    """2 years: CI − SI = P (R/100)²."""
    return p * (Fraction(r) / 100) ** 2


def diff_3(p, r):
    """3 years: CI − SI = P (R/100)² × (300 + R)/100."""
    return diff_2(p, r) * (300 + Fraction(r)) / 100


def by_definition(p, r, n):
    """CI − SI computed the long way, to check the formulas."""
    r = Fraction(r)
    return p * ((1 + r / 100) ** n - 1) - p * r * n / 100


assert all(diff_2(1000, r) == by_definition(1000, r, 2) and diff_3(1000, r) == by_definition(1000, r, 3) for r in (4, 5, 8, 10, 20))

# ---- the hook ----
HOOK_DIFF, HOOK_R = 100, 10
HOOK_P = HOOK_DIFF / (Fraction(HOOK_R) / 100) ** 2
HOOK_SI = HOOK_P * HOOK_R * 2 / 100
HOOK_CI = HOOK_SI + HOOK_DIFF
assert (HOOK_P, HOOK_SI, HOOK_CI) == (10000, 2000, 2100) and HOOK_P * Fraction("1.21") - HOOK_P == HOOK_CI

# ---- second worked example: both P and R ----
EX_YEARLY = Fraction(480, 2)
EX_R = Fraction(48) / EX_YEARLY * 100
EX_P = 100 * EX_YEARLY / EX_R
assert (EX_YEARLY, EX_R, EX_P) == (240, 20, 1200) and diff_2(EX_P, EX_R) == 48

# ---- exam patterns (answers computed) ----
P1 = diff_2(8000, 5)
P2 = 96 / (Fraction(8) / 100) ** 2
P3 = 31 / (diff_3(1, 10))
P4 = Fraction(160, 4000)                                   # (R/100)²
P5_PCT = 2 * 5 + Fraction(5 * 5, 100)
P5_P = 410 / (P5_PCT / 100)
P5_SI = P5_P * 5 * 2 / 100
assert (P1, P2, P3, P4, P5_PCT, P5_P, P5_SI) == (20, 15000, 1000, Fraction("0.04"), Fraction("10.25"), 4000, 400)
assert Fraction(2, 10) ** 2 == P4 and (2 * 10 + 1, 2 * 10) == (21, 20)
PATTERNS_A = [("Find the difference", "₹8,000 at 5%, 2 years", "8,000 × 0.0025", rs(P1)),
              ("Find P (2 years)", "Difference ₹96 at 8%", "96 ÷ 0.0064", rs(P2)),
              ("Find P (3 years)", "Difference ₹31 at 10%", "31 ÷ (0.01 × 3.1)", rs(P3))]
PATTERNS_B = [("Find R", "₹4,000, 2 years, difference ₹160", "(R/100)² = 0.04", "20%"),
              ("From CI to SI", "CI ₹410 for 2 years at 5%", f"CI% = {dec(P5_PCT)}%, so P = {rs(P5_P)}", f"SI = {rs(P5_SI)}"),
              ("Ratio CI : SI", "2 years at 10%", "CI% = 21, SI% = 20", "21 : 20")]

# ---- traps: (title, question, wrong, right, rule) ----
T1_WRONG, T1_RIGHT = diff_2(20000, 10), diff_3(20000, 10)
assert (T1_WRONG, T1_RIGHT) == (200, 620)
TRAPS = [("Trap 1  ·  the 2-year formula used for 3 years", "CI − SI on ₹20,000 for 3 years at 10%?",
          f"20,000 × 0.01  =  {rs(T1_WRONG)}", f"20,000 × 0.01 × 3.1  =  {rs(T1_RIGHT)}",
          "Check the years first: three years needs the extra factor (300 + R)/100."),
         ("Trap 2  ·  R squared instead of R/100 squared", "Difference at 8% for 2 years is ₹96.  Find P.",
          "96 ÷ 64", f"96 ÷ 0.0064  =  {rs(P2)}",
          "Convert R to a decimal before squaring.")]

# ---- checkpoint ----
CP = diff_2(8000, 5)
assert CP == 20 and Fraction("0.05") ** 2 == Fraction("0.0025")

# ---- practice (answers computed) ----
PRACTICE_A = [("L1", "For 2 years at 20%, CI − SI is ₹200.  Find the principal."),
              ("L1", "Find CI − SI on ₹5,000 for 2 years at 4% per year."),
              ("L2", "Find CI − SI on ₹20,000 for 3 years at 10%."),
              ("L2", "The compound interest on a sum for 2 years at 5% is ₹410.  Find the simple interest."),
              ("L2", "CI − SI on ₹4,000 for 2 years is ₹160.  Find the rate.")]
PRACTICE_B = [("L3", "CI − SI on a sum for 3 years at 10% is ₹31.  Find the sum."),
              ("L3", "The SI on a sum for 2 years is ₹480, and CI − SI for 2 years is ₹48.  Find the rate and the sum."),
              ("L3", "Find the ratio of CI to SI on any sum for 2 years at 10%.")]
A1 = 200 / (Fraction(20) / 100) ** 2
A2 = diff_2(5000, 4)
assert (A1, A2) == (5000, 8)
ANSWERS_A = [("P × 0.04 = 200", rs(A1)),
             ("5,000 × 0.0016", rs(A2)),
             ("20,000 × 0.01 × 3.1", rs(T1_RIGHT)),
             (f"2-year CI% = 10 + 0.25 = {dec(P5_PCT)}%;   P = 410 ÷ 0.1025 = {rs(P5_P)}", f"SI = {rs(P5_SI)}"),
             ("(R/100)² = 160 ÷ 4,000 = 0.04;   R/100 = 0.2", "R = 20%")]
ANSWERS_B = [("31 = P × 0.01 × 3.1 = 0.031 P", rs(P3)),
             ("one year's SI = ₹240;   48 = 240 × R/100;   P = 100 × 240 ÷ 20", f"{EX_R}%;  {rs(EX_P)}"),
             ("CI% = 21,   SI% = 20", "21 : 20")]

OBJECTIVES = [("Derive and use the CI − SI formulas", "for 2 years and for 3 years"),
              ("Work backwards from the difference", "to the principal or the rate"),
              ("Link the difference to one year's SI", "2-year difference = one year's SI × R/100")]
LENS = [("Recognition cue", "“difference between compound and simple interest”  →  never compute both interests"),
        ("Target time", "30 seconds"),
        ("Sanity check", "the 2-year difference is a small fraction of P;  at 10% it is exactly 1% of P")]
FORMULAS = ["2 years:      CI − SI  =  P (R/100)²",
            "3 years:      CI − SI  =  P (R/100)² × (300 + R)/100",
            "2-year link:      CI − SI  =  (one year's SI) × R/100",
            "Write R/100 as a decimal first:      10% → 0.1,   so (0.1)² = 0.01"]


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


class SIvsCIDifferenceVideo(LMSScene):
    lesson_title = "SI vs CI Difference"

    def construct(self):
        self.camera.background_color = BG

        self.intro()
        self.hook()
        self.objectives()
        self.why_this_matters()
        self.two_years()
        self.algebra_and_three_years()
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

    # ================================================== 0. INTRO ==========
    # Not the first video: silent breadcrumb, a one-line recap of Video 4, then today's topic.

    def intro(self):
        self.scene_start("S00_intro", title="Intro")

        crumb = self.breadcrumb("Quantitative Aptitude", "Lesson 11 · Simple & Compound Interest", "Video 5 of 7")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        recap = VGroup(text("last video", SMALL, MUTED),
                       VGroup(pill("divide the rate, multiply the periods", WORD, size=LABEL),
                              pill("compare effective rates", GOOD, size=LABEL)).arrange(RIGHT, buff=0.4)).arrange(DOWN, buff=0.25)
        title = text("SI vs CI Difference", TITLE, INK, BOLD)
        today = text("today: the gap between compound and simple interest, in one line", LABEL, FOCUS)
        block = VGroup(recap, title, today).arrange(DOWN, buff=0.7)
        fit_within(block, SAFE_W, SAFE_H - crumb.height - 0.9)
        block.next_to(crumb, DOWN, buff=0.7)
        self.no_overlap(crumb, recap, title, today)
        self.no_overlap(*recap[1])
        self.validator.check_in_frame(VGroup(crumb, block))

        n = self.narrate(
            id="intro_01",
            text="In the last video, you adjusted the rate and the periods, and compared offers by their effective rates.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.at_word(n, "adjusted")
        self.play(FadeIn(recap[0]), FadeIn(recap[1][0], shift=UP * 0.1))
        self.at_word(n, "effective")
        self.play(FadeIn(recap[1][1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="intro_02",
            text="Today: the gap between compound and simple interest, and its one-line formulas.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "gap")
        self.play(FadeIn(title, shift=UP * 0.1))
        self.at_word(n, "formulas")
        self.play(FadeIn(today, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_intro")

    # =================================================== 1. HOOK ==========

    def hook(self):
        self.scene_start("S01_hook", title="Hook")

        head = self.heading("A finance app summary")
        lines = VGroup(VGroup(text("Deposit", LABEL, MUTED), text("₹  ?", BODY, FOCUS, BOLD)).arrange(RIGHT, buff=0.5),
                       VGroup(text("Term", LABEL, MUTED), text(f"2 years at {HOOK_R}%", BODY, INK, BOLD)).arrange(RIGHT, buff=0.5),
                       VGroup(text("CI − SI", LABEL, MUTED), text(rs(HOOK_DIFF), BODY, INK, BOLD)).arrange(RIGHT, buff=0.5))\
            .arrange(DOWN, buff=0.4, aligned_edge=LEFT)
        app = self.card(lines, width=7.0, color=WORD, pad=0.45)
        ask = pill("find the deposit without computing either interest", FOCUS, size=LABEL)
        notes = VGroup(text("it takes one line", LABEL, GOOD, BOLD),
                       text("one of the most-asked shortcuts in this lesson", LABEL, MUTED)).arrange(RIGHT, buff=0.7)
        self.stack(head, [app, ask, notes], buff=0.55, top=0.6)
        self.no_overlap(*notes)

        n = self.narrate(
            id="hook_01",
            text="Your finance app shows a curious summary: for your two-year deposit at ten percent, compound interest minus "
                 "simple interest is one hundred rupees.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "summary")
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(app[0]))
        self.at_word(n, "ten")
        self.play(FadeIn(lines[1], shift=RIGHT * 0.2))
        self.at_word(n, "minus")
        self.play(FadeIn(lines[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_02",
            text="It has hidden the deposit amount.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "hidden")
        self.play(FadeIn(lines[0], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_03",
            text="Can you find the deposit without computing either interest?",
            voice="default",
            subtitle=True,
            pause_after=3.0,
        )
        self.at_word(n, "without")
        self.play(FadeIn(ask, shift=UP * 0.1))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="hook_04",
            text="It takes one line, and it is one of the most-asked shortcuts in this lesson.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "line")
        self.play(FadeIn(notes[0], shift=UP * 0.1))
        self.at_word(n, "most-asked")
        self.play(FadeIn(notes[1], shift=UP * 0.1))
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
            text="First, derive and use the two-year and three-year formulas for compound interest minus simple interest.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "derive")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "three-year")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="obj_03",
            text="Second, work backwards from the difference to the principal or the rate.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "backwards")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "principal")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="obj_04",
            text="Third, link the difference to one year's simple interest.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "link")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "simple")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_objectives")

    # ========================================== 3. WHY THIS MATTERS ==========

    def why_this_matters(self):
        self.scene_start("S03_why_this_matters", title="Why This Matters")

        head = self.heading("Why this matters")
        gap = pill("CI − SI  =  exactly the interest earned on interest", RATIO, size=LABEL)
        tidy = text("a small, tidy quantity with its own formulas", LABEL, INK)
        one = pill("a long-looking question collapses into one multiplication", GOOD, size=LABEL)
        self.stack(head, [gap, tidy, one], buff=0.8, top=0.9)

        n = self.narrate(
            id="why_01",
            text="The gap between compound and simple interest is exactly the interest earned on interest.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "exactly")
        self.play(FadeIn(gap, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="why_02",
            text="It is a small, tidy quantity with its own formulas, so a long-looking question collapses into one "
                 "multiplication.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "tidy")
        self.play(FadeIn(tidy, shift=UP * 0.1))
        self.at_word(n, "collapses")
        self.play(FadeIn(one, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_why_this_matters")

    # ==================================== 4. CONCEPT: TWO YEARS ==========

    def two_years(self):
        self.scene_start("S04_two_years", title="Concept - Where SI and CI Part")

        head = self.heading("Year 1 is identical; year 2 is where they part")
        table, rows = self.placed_table(head, ["Year", "Simple interest", "Compound interest"],
                                        [["1", "PR/100", "PR/100"], ["2", "PR/100", "PR/100  +  (PR/100) × (R/100)"]],
                                        [1.8, 3.6, 6.8], size=LABEL, room=3.0)
        for row in rows:
            row[0].set_color(MUTED)
            row[1].set_color(WORD)
            row[2].set_color(RATIO)
        piece = VGroup(text("the difference is that one extra piece", LABEL, MUTED),
                       pill("2 years:   CI − SI  =  P (R/100)²", GOOD, size=BODY)).arrange(DOWN, buff=0.3)
        piece.next_to(table, DOWN, buff=0.7)
        self.no_overlap(table, piece)
        self.validator.check_in_frame(piece)

        n = self.narrate(
            id="two_01",
            text="Year one is identical. Simple and compound interest both give P R over a hundred in the first year.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "identical")
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]), FadeIn(rows[0][0]))
        self.at_word(n, "both")
        self.play(FadeIn(rows[0][1:], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="two_02",
            text="Year two is where they part. Simple interest gives another P R over a hundred.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "part")
        self.play(FadeIn(rows[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "another")
        self.play(FadeIn(rows[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="two_03",
            text="Compound interest also earns interest on year one's interest: P R over a hundred, times R over a hundred.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "also")
        self.play(FadeIn(rows[1][2], shift=RIGHT * 0.2))
        self.at_word(n, "times")
        self.play(Indicate(rows[1][2], color=FOCUS, scale_factor=1.05))
        self.wait_for_narration(n)

        n = self.narrate(
            id="two_04",
            text="So for two years, the difference is that one piece: P times R over a hundred, squared.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "piece")
        self.play(FadeIn(piece[0], shift=UP * 0.1))
        self.at_word(n, "squared")
        self.play(FadeIn(piece[1], scale=1.05))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_two_years")

    # ====================== 5. CONCEPT: ALGEBRA, THREE YEARS, THE LINK ==========

    def algebra_and_three_years(self):
        self.scene_start("S05_algebra_and_three_years", title="Concept - Algebra, Three Years and a Useful Link")

        head = self.heading("Algebra confirms it")
        two = text("with r = R/100:      P[(1 + r)² − 1] − P(2r)  =  P r²", LABEL, INK)
        three = text("3 years:      P[(1 + r)³ − 1] − P(3r)  =  P(3r² + r³)  =  P r² (3 + r)", LABEL, INK)
        three_pill = pill("3 years:   CI − SI  =  P (R/100)² × (300 + R)/100", GOOD, size=LABEL)
        link = VGroup(text("a useful link:  one year's SI = PR/100", LABEL, RATIO, BOLD),
                      pill("2-year difference  =  (one year's SI) × R/100", RATIO, size=LABEL)).arrange(DOWN, buff=0.25)
        self.stack(head, [two, three, three_pill, link], buff=0.6, top=0.7)

        n = self.narrate(
            id="alg_01",
            text="Algebra confirms it. With small r equal to R over a hundred, P times one plus r squared minus one, minus P "
                 "times two r, is P r squared.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "confirms")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "minus", occurrence=1)
        self.play(FadeIn(two, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="alg_02",
            text="Three years adds more interest on interest: the difference is P r squared, times three plus r.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Three")
        self.play(FadeIn(three, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="alg_03",
            text="That is P times R over a hundred squared, times three hundred plus R, over a hundred.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "squared")
        self.play(FadeIn(three_pill, scale=1.05))
        self.wait_for_narration(n)

        n = self.narrate(
            id="alg_04",
            text="A useful link: one year's simple interest is P R over a hundred, so the two-year difference is one year's "
                 "simple interest times R over a hundred.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "link")
        self.play(FadeIn(link[0], shift=UP * 0.1))
        self.at_word(n, "times")
        self.play(FadeIn(link[1], scale=1.05))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_algebra_and_three_years")

    # ============================================== 6. FORMULA BOX ==========

    def formula_box(self):
        self.scene_start("S06_formula_box", title="Formula Box")

        head = self.heading("Formula box", GOOD)
        lines = VGroup(*[text(f, LABEL, INK) for f in FORMULAS]).arrange(DOWN, buff=0.5, aligned_edge=LEFT)
        box = self.card(lines, width=SAFE_W - 1.0, color=GOOD, pad=0.5)
        self.stack(head, [box], top=0.8)

        n = self.narrate(
            id="formula_01",
            text="Here is the formula box. Two years: P times R over a hundred, squared.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "box")
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(box[0]))
        self.at_word(n, "squared")
        self.play(FadeIn(lines[0], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_02",
            text="Three years: the same, times three hundred plus R, over a hundred.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Three")
        self.play(FadeIn(lines[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_03",
            text="The two-year link: one year's simple interest, times R over a hundred.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "link")
        self.play(FadeIn(lines[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_04",
            text="And write R over a hundred as a decimal first: ten percent is zero point one, so its square is zero point "
                 "zero one.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "decimal")
        self.play(FadeIn(lines[3], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_formula_box")

    # ============================================== 7. THE ANALOGY ==========

    def analogy(self):
        self.scene_start("S07_analogy", title="The Analogy - Two Runners")

        head = self.heading("Two runners start together")

        def laps(color, boost):
            parts = [Rectangle(width=2.2, height=0.4, color=color, fill_color=color, fill_opacity=0.4) for _ in range(2)]
            if boost:
                parts.append(Rectangle(width=0.3, height=0.4, color=FOCUS, fill_color=FOCUS, fill_opacity=0.9))
            return VGroup(*parts).arrange(RIGHT, buff=0.06)

        s_label, s_laps = text("Runner S  ·  steady pace", LABEL, WORD, BOLD), laps(WORD, False)
        c_label, c_laps = text("Runner C  ·  a small boost each lap", LABEL, RATIO, BOLD), laps(RATIO, True)
        runners = VGroup(s_label, s_laps, c_label, c_laps).arrange(DOWN, buff=0.22, aligned_edge=LEFT)
        after = VGroup(text("after lap 1: level", LABEL, INK), text("after lap 2: C is ahead, by the boost", LABEL, FOCUS, BOLD))\
            .arrange(RIGHT, buff=0.8)
        boost = pill("CI − SI  is that boost", GOOD, size=LABEL)
        stops = VGroup(text("Where the analogy stops", LABEL, BAD, BOLD),
                       text("the runners' gap can be any shape", LABEL, MUTED),
                       text("the interest gap follows an exact formula", LABEL, INK)).arrange(DOWN, buff=0.2)
        self.stack(head, [runners, after, boost, stops], buff=0.45, top=0.5)
        self.no_overlap(s_label, s_laps, c_label, c_laps)
        self.no_overlap(*after)

        n = self.narrate(
            id="analogy_01",
            text="Two runners start together.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "runners")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_02",
            text="Runner S keeps a steady pace.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "steady")
        self.play(FadeIn(s_label, shift=RIGHT * 0.1), LaggedStart(*[GrowFromEdge(l, LEFT) for l in s_laps], lag_ratio=0.5))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_03",
            text="Runner C gets a small boost each lap, proportional to the distance already covered.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "boost")
        self.play(FadeIn(c_label, shift=RIGHT * 0.1), LaggedStart(*[GrowFromEdge(l, LEFT) for l in c_laps], lag_ratio=0.5))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_04",
            text="After lap one they are level; after lap two, C is slightly ahead, and that gap is entirely the boost.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "level")
        self.play(FadeIn(after[0], shift=UP * 0.1))
        self.at_word(n, "ahead")
        self.play(FadeIn(after[1], shift=UP * 0.1), Indicate(c_laps[2], color=FOCUS, scale_factor=1.3))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_05",
            text="Compound interest minus simple interest is that boost.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "boost")
        self.play(FadeIn(boost, scale=1.05))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_06",
            text="Where the analogy stops: the runners' gap can be any shape. The interest gap follows an exact formula.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "stops")
        self.play(FadeIn(stops[0], shift=UP * 0.1))
        self.at_word(n, "shape")
        self.play(FadeIn(stops[1], shift=UP * 0.1))
        self.at_word(n, "exact")
        self.play(FadeIn(stops[2], shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S07_analogy")

    # ================================ 8. WORKED EXAMPLE: CLOSING THE HOOK ==========

    def hook_solved(self):
        self.scene_start("S08_hook_solved", title="Worked Example - Closing the Hook")

        head = self.heading(f"The app:  2 years, {HOOK_R}%, CI − SI = {rs(HOOK_DIFF)}")
        steps = self.solve_steps([
            ("P × (0.1)²  =  100", "→   P × 0.01  =  100"),
            ("P  =  100 ÷ 0.01", f"=  {rs(HOOK_P)}"),
            (f"check:  SI = {rs(HOOK_SI)},   CI = 10,000 × 1.21 − 10,000 = {rs(HOOK_CI)}", f"difference {rs(HOOK_DIFF)}")])
        deposit = pill(f"the hidden deposit:  {rs(HOOK_P)}", GOOD, size=BODY)
        self.stack(head, [steps, deposit], buff=0.8, top=0.8)
        self.no_overlap(*steps)

        n = self.narrate(
            id="solved_01",
            text="Two years, ten percent, difference one hundred rupees: so P times zero point one squared is one hundred.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "squared")
        self.play(FadeIn(steps[0][:2], shift=RIGHT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_02",
            text="That is P times zero point zero one equals one hundred, so P is ten thousand rupees.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "equals")
        self.play(FadeIn(steps[0][2], shift=LEFT * 0.1))
        self.at_word(n, "ten")
        self.play(FadeIn(steps[1], shift=RIGHT * 0.1), FadeIn(deposit, scale=1.05))
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_03",
            text="Check: simple interest is two thousand, compound interest is two thousand one hundred, and the difference is "
                 "one hundred.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Check")
        self.play(FadeIn(steps[2][:2], shift=RIGHT * 0.1))
        self.at_word(n, "difference")
        self.play(FadeIn(steps[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S08_hook_solved")

    # ====================== 9. SECOND WORKED EXAMPLE: BOTH P AND R ==========

    def second_example(self):
        self.scene_start("S09_second_example", title="A Second Worked Example - Finding Both P and R")

        head = self.heading("Finding both P and R")
        given = VGroup(pill("SI for 2 years = ₹480", WORD, size=LABEL), pill("CI − SI for 2 years = ₹48", RATIO, size=LABEL),
                       pill("find R and P", FOCUS, size=LABEL)).arrange(RIGHT, buff=0.4)
        steps = self.solve_steps([
            ("one year's SI  =  480 ÷ 2", f"=  {rs(EX_YEARLY)}"),
            ("CI − SI = one year's SI × R/100:    48 = 240 × R/100", f"R = {EX_R}%"),
            ("P  =  100 × 240 ÷ 20", f"=  {rs(EX_P)}")])
        check = text(f"check:  1,200 × (0.2)²  =  {diff_2(EX_P, EX_R)}", SMALL, MUTED, BOLD)
        self.stack(head, [given, steps, check], buff=0.65, top=0.7)
        self.no_overlap(*given)
        self.no_overlap(*steps)

        n = self.narrate(
            id="both_01",
            text="The simple interest on a sum for two years is four hundred and eighty rupees, and compound interest minus "
                 "simple interest for the same two years is forty-eight rupees. Find the rate and the sum.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "eighty")
        self.play(FadeIn(given[0], shift=UP * 0.1))
        self.at_word(n, "forty-eight")
        self.play(FadeIn(given[1], shift=UP * 0.1))
        self.at_word(n, "Find")
        self.play(FadeIn(given[2], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="both_02",
            text="One year's simple interest is four hundred and eighty divided by two: two hundred and forty rupees.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "divided")
        self.play(FadeIn(steps[0][:2], shift=RIGHT * 0.1))
        self.at_word(n, "forty")
        self.play(FadeIn(steps[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="both_03",
            text="The difference is one year's simple interest times R over a hundred, so forty-eight equals two hundred and "
                 "forty times R over a hundred, giving R as twenty percent.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "equals")
        self.play(FadeIn(steps[1][:2], shift=RIGHT * 0.1))
        self.at_word(n, "twenty")
        self.play(FadeIn(steps[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="both_04",
            text="Then P is one hundred times two hundred and forty, divided by twenty: twelve hundred rupees. Check: twelve "
                 "hundred times zero point two squared is forty-eight.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "divided")
        self.play(FadeIn(steps[2][:2], shift=RIGHT * 0.1))
        self.at_word(n, "twelve")
        self.play(FadeIn(steps[2][2], shift=LEFT * 0.1))
        self.at_word(n, "Check")
        self.play(FadeIn(check, shift=UP * 0.1))
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
            text="Find the difference: eight thousand at five percent for two years is eight thousand times zero point zero "
                 "zero two five, twenty rupees.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "difference")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "times")
        self.play(FadeIn(rows[0][2:], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="patterns_03",
            text="Find P for two years: a difference of ninety-six at eight percent means ninety-six divided by zero point "
                 "zero zero six four, fifteen thousand.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "years")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "divided")
        self.play(FadeIn(rows[1][2:], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="patterns_04",
            text="Find P for three years: a difference of thirty-one at ten percent means thirty-one divided by zero point "
                 "zero three one, one thousand.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "three")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "divided")
        self.play(FadeIn(rows[2][2:], shift=RIGHT * 0.2))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Exam patterns  ·  4 to 6 of 6")
        table, rows = self.pattern_table(head, PATTERNS_B)

        n = self.narrate(
            id="patterns_05",
            text="Find the rate: four thousand, two years, difference one hundred and sixty, so R over a hundred squared is "
                 "zero point zero four, and R is twenty percent.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "rate")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "squared")
        self.play(FadeIn(rows[0][2:], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="patterns_06",
            text="From compound interest to simple interest: compound interest of four hundred and ten for two years at five "
                 "percent is ten point two five percent of P, so P is four thousand and the simple interest is four hundred.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "From")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "point")
        self.play(FadeIn(rows[1][2:], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="patterns_07",
            text="The ratio of compound to simple interest for two years at ten percent is twenty-one to twenty.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "ratio")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "twenty-one")
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
            text="Trap one: the two-year formula used for three years. Find compound interest minus simple interest on twenty "
                 "thousand rupees for three years at ten percent.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "formula")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "twenty")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="trap1_02",
            text="The wrong instinct is twenty thousand times zero point zero one, two hundred rupees. Correctly, it is twenty "
                 "thousand times zero point zero one times three point one: six hundred and twenty rupees.",
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
            text="The rule: check the years first; three years needs the extra factor, three hundred plus R, over a hundred.",
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
            text="Trap two: R squared, instead of R over a hundred squared. The difference at eight percent for two years is "
                 "ninety-six rupees; find P.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "instead")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "ninety-six")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="trap2_02",
            text="The wrong instinct is ninety-six divided by sixty-four. Correctly, it is ninety-six divided by zero point zero "
                 "zero six four: fifteen thousand rupees.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "wrong")
        self.play(FadeIn(wrong, shift=UP * 0.1))
        self.at_word(n, "Correctly")
        self.play(FadeIn(right, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="trap2_03",
            text="The rule: convert R to a decimal before squaring.",
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
        given = given_chips("₹8,000", "5% per year", "2 years")
        hint = pill("CI − SI = ?", FOCUS, size=BODY)
        work = VGroup(text("(0.05)²  =  0.0025", LABEL, INK), text(f"8,000 × 0.0025  =  {rs(CP)}", LABEL, GOOD, BOLD))\
            .arrange(RIGHT, buff=0.9)
        self.stack(head, [given, hint, work], buff=0.7, top=0.8)
        self.no_overlap(*work)

        n = self.narrate(
            id="check_01",
            text="Your turn. On eight thousand rupees at five percent per year for two years, find compound interest minus "
                 "simple interest.",
            voice="default",
            subtitle=True,
            pause_after=10.0,
        )
        self.at_word(n, "turn")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "eight")
        self.play(FadeIn(given[0], shift=UP * 0.1))
        self.at_word(n, "five")
        self.play(FadeIn(given[1], shift=UP * 0.1))
        self.at_word(n, "two")
        self.play(FadeIn(given[2], shift=UP * 0.1))
        self.at_word(n, "minus")
        self.play(FadeIn(hint, shift=UP * 0.1))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="check_02",
            text="Zero point zero five squared is zero point zero zero two five, and eight thousand times that is twenty "
                 "rupees.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "squared")
        self.play(FadeIn(work[0], shift=UP * 0.1))
        self.at_word(n, "twenty")
        self.play(FadeIn(work[1], shift=LEFT * 0.1))
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
            text="Level one, question one: for two years at twenty percent, compound interest minus simple interest is two "
                 "hundred rupees; find the principal. Question two: find compound interest minus simple interest on five "
                 "thousand rupees for two years at four percent per year.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "principal")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "five")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="practice_02",
            text="Level two, question three: find compound interest minus simple interest on twenty thousand rupees for three "
                 "years at ten percent. Question four: the compound interest on a sum for two years at five percent is four "
                 "hundred and ten rupees; find the simple interest. Question five: compound interest minus simple interest on "
                 "four thousand rupees for two years is one hundred and sixty rupees; find the rate.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "twenty")
        self.play(FadeIn(rows[2], shift=RIGHT * 0.2))
        self.at_word(n, "sum")
        self.play(FadeIn(rows[3], shift=RIGHT * 0.2))
        self.at_word(n, "rate")
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
            text="Level three, question six: compound interest minus simple interest on a sum for three years at ten percent "
                 "is thirty-one rupees; find the sum. Question seven: the simple interest on a sum for two years is four "
                 "hundred and eighty rupees, and compound interest minus simple interest for two years is forty-eight rupees; "
                 "find the rate and the sum. Question eight: find the ratio of compound interest to simple interest on any "
                 "sum for two years at ten percent.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "thirty-one")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "forty-eight")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.at_word(n, "ratio")
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
            text="One: P times zero point zero four is two hundred, so P is five thousand rupees.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "times")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "five")
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_02",
            text="Two: five thousand times zero point zero zero one six is eight rupees.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "times")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "eight")
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_03",
            text="Three: twenty thousand times zero point zero one times three point one is six hundred and twenty rupees.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "times", occurrence=1)
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "six")
        self.play(FadeIn(rows[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_04",
            text="Four: the two-year compound interest is ten point two five percent of P, so P is four hundred and ten "
                 "divided by zero point one zero two five, four thousand. The simple interest is four hundred rupees.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "divided")
        self.play(FadeIn(rows[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "simple")
        self.play(FadeIn(rows[3][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_05",
            text="Five: R over a hundred squared is one hundred and sixty divided by four thousand, zero point zero four, so R "
                 "is twenty percent.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "divided")
        self.play(FadeIn(rows[4][:2], shift=RIGHT * 0.2))
        self.at_word(n, "twenty")
        self.play(FadeIn(rows[4][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Answer key  ·  6 to 8", GOOD)
        table, rows = self.answer_table(head, ANSWERS_B, 6)

        n = self.narrate(
            id="answers_06",
            text="Six: thirty-one equals zero point zero three one times P, so P is one thousand rupees.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "equals")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "thousand")
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_07",
            text="Seven: one year's simple interest is two hundred and forty, so forty-eight equals two hundred and forty times "
                 "R over a hundred, giving twenty percent. Then P is twelve hundred rupees.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "equals")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "twelve")
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_08",
            text="Eight: compound interest is twenty-one percent and simple interest is twenty percent, so the ratio is "
                 "twenty-one to twenty.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "twenty-one", occurrence=1)
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "ratio")
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
            text="Recognise and move. The recognition cue: the difference between compound and simple interest. Never compute "
                 "both interests.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Recognise")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "cue")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "Never")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="lens_02",
            text="The target time: thirty seconds.",
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
            text="The sanity check: the two-year difference is always a small fraction of P; at ten percent it is exactly one "
                 "percent of P.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "sanity")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "small")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S15_exam_lens")

    # ==================================== 16. QUICK REVISION + SUMMARY ==========

    def summary(self):
        self.scene_start("S16_summary", title="Quick Revision and Summary")

        head = self.heading("Quick revision")
        only = pill("CI − SI  =  only the interest on interest", RATIO, size=LABEL)
        box = VGroup(text("2 years:      P (R/100)²", LABEL, INK, BOLD),
                     text("3 years:      P (R/100)² × (300 + R)/100", LABEL, INK, BOLD),
                     text("work backwards by dividing", LABEL, INK),
                     text("SI given:      CI − SI  =  (one year's SI) × R/100", LABEL, INK)).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        nxt = self.breadcrumb("Next", "Video 6 · Growth & Depreciation")
        self.stack(head, [only, box, nxt], buff=0.7, top=0.7)
        self.no_overlap(*box)

        n = self.narrate(
            id="summary_01",
            text="Compound interest minus simple interest is only the interest on interest.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "only")
        self.play(FadeIn(only, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_02",
            text="It is P times R over a hundred squared for two years, with an extra factor of three hundred plus R, over a "
                 "hundred, for three.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "squared")
        self.play(FadeIn(box[0], shift=RIGHT * 0.2))
        self.at_word(n, "extra")
        self.play(FadeIn(box[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_03",
            text="Work backwards by dividing, and use one year's simple interest times R over a hundred when the simple "
                 "interest is given.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "dividing")
        self.play(FadeIn(box[2], shift=RIGHT * 0.2))
        self.at_word(n, "times")
        self.play(FadeIn(box[3], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_04",
            text="Next: growth and depreciation.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Next")
        self.play(FadeIn(nxt, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S16_summary")

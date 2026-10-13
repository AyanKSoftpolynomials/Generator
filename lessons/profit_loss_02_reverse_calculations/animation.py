"""
animation.py for the LMS video generator.

Course : Pre-C-CAT - Section A - Quantitative Aptitude
Video  : Lesson 12 - Profit & Loss - 02 - Reverse Calculations

Source script:
  C:\\Scripts\\Section A\\Module_2_Section_A_Quantitative_Aptitude_Part_1\\Aptitude_Scripts\\Sessions 1-4 - Interest, Profit & Loss, Time & Work\\Lesson 12 - Profit & Loss\\02 - Reverse Calculations.pdf

Built on the golden-reference pattern:
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``;
  * layouts stacked with next_to and guarded with ``no_overlap``; nothing is
    ever animated onto or into another box.

Lesson 12, Video 2 of 8. Not the first video of the lesson: a silent breadcrumb, a one-line recap of Video 1, then today's topic. No spoken course welcome.
The narration follows the script section by section, with numbers written as words for the voice and CP / SP / MP spoken as "cost price", "selling price" and "marked price". Tables and lists are spoken one row at a time; the exam patterns, practice questions and answers are split over two screens each. Every percentage on screen is computed from the question's numbers and asserted.
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
    """A whole number in the Indian grouping the script uses: 1,32,000."""
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
    """Multiplier for a profit (+) or loss (−) percentage on CP."""
    return 1 + Fraction(pct) / 100


def sp_from_cp(cp, pct):
    """Forwards: multiply."""
    return cp * mult(pct)


def cp_from_sp(sp, pct):
    """Backwards: divide."""
    return sp / mult(pct)


def cp_from_gap(gap, loss, gain):
    """Two prices that give an L% loss and a G% gain differ by (L + G)% of CP."""
    return Fraction(gap) * 100 / (loss + gain)


assert rs(132000) == "₹1,32,000" and rs(1200) == "₹1,200"

# ---- the hook: the laptop ----
HOOK_SP, HOOK_PCT = 132000, 10
HOOK_CP = cp_from_sp(HOOK_SP, HOOK_PCT)
HOOK_TENTH = HOOK_SP * HOOK_PCT // 100
HOOK_WRONG = HOOK_SP - HOOK_TENTH
assert (HOOK_CP, HOOK_TENTH, HOOK_WRONG) == (120000, 13200, 118800) and HOOK_CP + HOOK_CP * HOOK_PCT / 100 == HOOK_SP
WEIGHT = Fraction(HOOK_SP, 110)
assert WEIGHT == 1200 and WEIGHT * 100 == HOOK_CP

# ---- concept figures ----
assert Fraction(100, 110) == Fraction(10, 11) and mult(10) == Fraction("1.1") and mult(-20) == Fraction("0.8")

# ---- second worked example: loss to gain ----
EX_CP = cp_from_sp(2340, -10)
EX_NEW = sp_from_cp(EX_CP, 10)
assert (EX_CP, EX_NEW, EX_NEW - 2340) == (2600, 2860, 520) and (EX_NEW - 2340) / EX_CP * 100 == 20

# ---- exam patterns (answers computed) ----
P1 = cp_from_sp(1500, 25)
P3 = cp_from_gap(90, 10, 5)
P4 = cp_from_sp(cp_from_sp(1500, 25), 20)
P5 = Fraction(1040 + 880, 2)
assert (P1, P3, P4, P5) == (1200, 600, 1000, 960)
PATTERNS_A = [("CP from SP", "Sold at 25% profit for ₹1,500", "1,500 ÷ 1.25", rs(P1)),
              ("Loss to gain", "10% loss at ₹2,340; price for 10% gain?", "CP = 2,600;  × 1.1", rs(EX_NEW)),
              ("Price difference", "10% loss; ₹90 more would give 5% gain", "15% of CP = 90", rs(P3))]
PATTERNS_B = [("Chain of sales", "A → B at 20% profit, B → C at 25% profit for ₹1,500", "÷ 1.25,  ÷ 1.2", rs(P4)),
              ("Equal % at two prices", "Same % profit at ₹1,040 as % loss at ₹880", "CP = the average", rs(P5))]

# ---- traps: (title, question, wrong, right, rule) ----
T2_WRONG = Fraction(90) * 100 / 5
assert T2_WRONG == 1800
TRAPS = [("Trap 1  ·  subtracting the percentage from SP", "Sold for ₹1,32,000 at 10% profit.  CP?",
          f"1,32,000 − 10%  =  {rs(HOOK_WRONG)}", f"1,32,000 ÷ 1.1  =  {rs(HOOK_CP)}",
          "A percentage taken on CP is undone only by dividing by the multiplier."),
         ("Trap 2  ·  the price difference split wrongly", "At a 10% loss, he would gain 5% by selling for ₹90 more.  CP?",
          f"5% of CP = 90  →  {rs(T2_WRONG)}", f"15% of CP = 90  →  {rs(P3)}",
          "Going from −10% to +5% is a 15-point swing on the same CP."),
         ("Trap 3  ·  chain solved in the wrong order", "A → B at 20% profit;  B → C at 25% profit for ₹1,500.  A's cost?",
          "1,500 ÷ 1.45", f"1,500 ÷ 1.25 ÷ 1.2  =  {rs(P4)}",
          "Each sale has its own CP: divide back one step at a time.")]

# ---- checkpoint ----
CP_ANSWER = cp_from_sp(640, -20)
assert CP_ANSWER == 800

# ---- practice (answers computed) ----
PRACTICE_A = [("L1", "An article is sold for ₹1,140 at a 5% loss.  Find the cost price."),
              ("L1", "An article costs ₹500.  At what price must it be sold for a 12% profit?"),
              ("L1", "An article sold at an 8% profit fetches ₹1,080.  Find the cost price."),
              ("L2", "A trader gains 20% on an article sold at ₹360.  At what price would he have lost 30%?"),
              ("L2", "A sells to B at a 20% profit.  B sells to C at a 25% profit for ₹1,500.  Find A's cost price."),
              ("L2", "An article sold at a 25% profit fetches ₹1,500.  Find the cost price.")]
PRACTICE_B = [("L3", "An article is sold at a 10% loss.  Had it been sold for ₹90 more, there would have been a 5% gain.  "
                     "Find the cost price."),
              ("L3", "A sells to B at a 10% profit, and B sells to C at a 20% loss.  C pays ₹1,320.  Find A's cost price."),
              ("L3", "The profit % when an article is sold for ₹1,040 equals the loss % when it is sold for ₹880.  Find the "
                     "cost price and that percentage.")]
A1, A2, A3 = cp_from_sp(1140, -5), sp_from_cp(500, 12), cp_from_sp(1080, 8)
A4_CP = cp_from_sp(360, 20)
A4 = sp_from_cp(A4_CP, -30)
A8_B = cp_from_sp(1320, -20)
A8 = cp_from_sp(A8_B, 10)
A9_PCT = (1040 - P5) / P5 * 100
assert (A1, A2, A3, A4_CP, A4, A8_B, A8, A9_PCT) == (1200, 560, 1000, 300, 210, 1650, 1500, Fraction(25, 3))
assert (sp_from_cp(P3, -10), sp_from_cp(P3, 5)) == (540, 630)
ANSWERS_A = [("CP = 1,140 ÷ 0.95", rs(A1)),
             ("SP = 500 × 1.12", rs(A2)),
             ("CP = 1,080 ÷ 1.08", rs(A3)),
             (f"CP = 360 ÷ 1.2 = {rs(A4_CP)};   at a 30% loss: 300 × 0.7", rs(A4)),
             (f"B's cost = 1,500 ÷ 1.25 = {rs(P1)};   A's cost = 1,200 ÷ 1.2", rs(P4))]
ANSWERS_B = [("CP = 1,500 ÷ 1.25", rs(P1)),
             ("−10% to +5% = 15% of CP = ₹90    (540 and 630 differ by 90)", rs(P3)),
             (f"B's cost = 1,320 ÷ 0.8 = {rs(A8_B)};   A's cost = 1,650 ÷ 1.1", rs(A8)),
             ("CP = (1,040 + 880)/2;   percentage = 80/960", f"{rs(P5)};  8 1/3 %")]

OBJECTIVES = [("Find CP from SP, and SP from CP", "using multipliers"),
              ("Move between a loss and a gain", "at different prices"),
              ("Trace a chain of sales backwards", "A → B → C")]
LENS = [("Recognition cue", "“sold for ₹X at y% profit (or loss); find the cost”  →  divide"),
        ("Target time", "30 seconds;  40 seconds for loss-to-gain"),
        ("Sanity check", "profit: CP is below SP, by less than that % of SP;    loss: CP is above SP")]
FORMULAS = ["SP = CP × (100 + P)/100              CP = SP × 100/(100 + P)",
            "Loss:  use (100 − L)              forwards ×,   backwards ÷",
            "Price difference between L% loss and G% gain   =   (L + G)% of CP",
            "Same % profit at S1 as % loss at S2    →    CP = (S1 + S2)/2"]


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


class ReverseCalculationsVideo(LMSScene):
    lesson_title = "Reverse Calculations"

    def construct(self):
        self.camera.background_color = BG

        self.intro()
        self.hook()
        self.objectives()
        self.why_this_matters()
        self.parts_and_ratio()
        self.multiply_and_divide()
        self.two_prices()
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
    # Not the first video: silent breadcrumb, a one-line recap of Video 1, then today's topic.

    def intro(self):
        self.scene_start("S00_intro", title="Intro")

        crumb = self.breadcrumb("Quantitative Aptitude", "Lesson 12 · Profit & Loss", "Video 2 of 8")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        recap = VGroup(text("last video", SMALL, MUTED), pill("profit % and loss %:  always measured on CP", WORD, size=LABEL))\
            .arrange(DOWN, buff=0.25)
        title = text("Reverse Calculations", TITLE, INK, BOLD)
        today = text("today: going backwards, from the selling price to the cost price", LABEL, FOCUS)
        block = VGroup(recap, title, today).arrange(DOWN, buff=0.7)
        fit_within(block, SAFE_W, SAFE_H - crumb.height - 0.9)
        block.next_to(crumb, DOWN, buff=0.7)
        self.no_overlap(crumb, recap, title, today)
        self.validator.check_in_frame(VGroup(crumb, block))

        n = self.narrate(
            id="intro_01",
            text="In the last video, profit and loss percentages were always measured on cost price.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.at_word(n, "always")
        self.play(FadeIn(recap, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="intro_02",
            text="Today: going backwards, from the selling price to the cost price.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "backwards")
        self.play(FadeIn(title, shift=UP * 0.1))
        self.at_word(n, "selling")
        self.play(FadeIn(today, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_intro")

    # =================================================== 1. HOOK ==========

    def hook(self):
        self.scene_start("S01_hook", title="Hook")

        head = self.heading("A laptop shop invoice")
        lines = VGroup(VGroup(text("Sold", LABEL, MUTED), text(rs(HOOK_SP), BODY, INK, BOLD)).arrange(RIGHT, buff=0.5),
                       VGroup(text("Profit", LABEL, MUTED), text(f"{HOOK_PCT}%", BODY, INK, BOLD)).arrange(RIGHT, buff=0.5),
                       VGroup(text("Cost to the shop", LABEL, MUTED), text("₹  ?", BODY, FOCUS, BOLD)).arrange(RIGHT, buff=0.5))\
            .arrange(DOWN, buff=0.35, aligned_edge=LEFT)
        invoice = self.card(lines, width=6.4, color=WORD, pad=0.45)
        tenth = text(f"most people:  {HOOK_PCT}% of 1,32,000 = {num(HOOK_TENTH)}", LABEL, MUTED)
        guess = pill(f"so the cost is {rs(HOOK_WRONG)}", BAD, size=LABEL)
        wrong = text("it feels right, and it is wrong", LABEL, BAD, BOLD)
        goal = text("goal: from SP back to CP in five seconds", SMALL, GOOD, BOLD)
        side = VGroup(tenth, guess, wrong, goal).arrange(DOWN, buff=0.4, aligned_edge=LEFT)
        row = VGroup(invoice, side).arrange(RIGHT, buff=0.7)
        self.stack(head, [row], top=0.9)
        self.no_overlap(invoice, side)

        n = self.narrate(
            id="hook_01",
            text="A shop sells a workstation laptop for one lakh thirty-two thousand rupees, and says it made a ten percent "
                 "profit.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "lakh")
        self.play(FadeIn(invoice[0]), FadeIn(lines[0], shift=RIGHT * 0.2))
        self.at_word(n, "ten")
        self.play(FadeIn(lines[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_02",
            text="What did the laptop cost the shop?",
            voice="default",
            subtitle=True,
            pause_after=3.0,
        )
        self.at_word(n, "cost")
        self.play(FadeIn(lines[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="hook_03",
            text="Most people take ten percent off one lakh thirty-two thousand, which is thirteen thousand two hundred, and "
                 "say one lakh eighteen thousand eight hundred.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "off")
        self.play(FadeIn(tenth, shift=LEFT * 0.1))
        self.at_word(n, "eighteen")
        self.play(FadeIn(guess, shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_04",
            text="It feels right, and it's wrong.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "wrong")
        self.play(FadeIn(wrong, shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_05",
            text="By the end of this video you'll go from selling price back to cost price in five seconds.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "five")
        self.play(FadeIn(goal, shift=LEFT * 0.1))
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
            text="First, find cost price from selling price, and selling price from cost price, using multipliers.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "find")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "multipliers")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="obj_03",
            text="Second, move between a loss and a gain at different prices.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "move")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "different")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="obj_04",
            text="Third, trace a chain of sales backwards.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "trace")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "backwards")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_objectives")

    # ========================================== 3. WHY THIS MATTERS ==========

    def why_this_matters(self):
        self.scene_start("S03_why_this_matters", title="Why This Matters")

        head = self.heading("Why this matters")
        half = pill("half the questions give the selling price and ask for the cost", WORD, size=LABEL)
        base = text("going backwards is where the base matters most", LABEL, INK)
        unknown = pill("the % was calculated on CP: the one number you don't know", BAD, size=LABEL)
        self.stack(head, [half, base, unknown], buff=0.8, top=0.9)

        n = self.narrate(
            id="why_01",
            text="Half the questions in this lesson give the selling price and ask for the cost.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "Half")
        self.play(FadeIn(half, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="why_02",
            text="Going backwards is where the base matters most, because the percentage was calculated on cost price, and "
                 "cost price is exactly what you don't know.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "base")
        self.play(FadeIn(base, shift=UP * 0.1))
        self.at_word(n, "exactly")
        self.play(FadeIn(unknown, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_why_this_matters")

    # ================================ 4. CONCEPT: 100 PARTS, A FIXED RATIO ==========

    def parts_and_ratio(self):
        self.scene_start("S04_parts_and_ratio", title="Concept - CP as 100 Parts; a Fixed Ratio")

        head = self.heading("Fix CP as 100 parts")
        rules = VGroup(pill("P% profit:   SP = (100 + P) parts", GOOD, size=LABEL), pill("L% loss:   SP = (100 − L) parts", BAD, size=LABEL))\
            .arrange(RIGHT, buff=0.5)
        unit = 0.07
        cp_bar = Rectangle(width=100 * unit, height=0.45, color=WORD, fill_color=WORD, fill_opacity=0.45)
        cp_row = VGroup(text("CP", LABEL, WORD, BOLD), cp_bar, text("100 parts", SMALL, WORD)).arrange(RIGHT, buff=0.3)
        sp_base = Rectangle(width=100 * unit, height=0.45, color=GOOD, fill_color=GOOD, fill_opacity=0.45)
        sp_extra = Rectangle(width=10 * unit, height=0.45, color=FOCUS, fill_color=FOCUS, fill_opacity=0.9)
        sp_bar = VGroup(sp_base, sp_extra).arrange(RIGHT, buff=0)
        sp_row = VGroup(text("SP", LABEL, GOOD, BOLD), sp_bar, text("110 parts", SMALL, GOOD)).arrange(RIGHT, buff=0.3)
        bars = VGroup(cp_row, sp_row).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        fixed = text("so CP and SP are in a fixed ratio", LABEL, MUTED, BOLD)
        ratio = pill("at 10% profit:   CP : SP  =  100 : 110  =  10 : 11", FOCUS, size=LABEL)
        self.stack(head, [rules, bars, fixed, ratio], buff=0.5, top=0.6)
        self.no_overlap(*rules)
        self.no_overlap(cp_row, sp_row)

        n = self.narrate(
            id="parts_01",
            text="Fix the cost price as one hundred parts. A P percent profit makes the selling price one hundred plus P parts; "
                 "an L percent loss makes it one hundred minus L parts.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Fix")
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(cp_row, shift=RIGHT * 0.2))
        self.at_word(n, "plus")
        self.play(FadeIn(rules[0], shift=UP * 0.1))
        self.at_word(n, "minus")
        self.play(FadeIn(rules[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="parts_02",
            text="So cost price and selling price are in a fixed ratio. At ten percent profit, cost price to selling price is "
                 "one hundred to one hundred and ten: ten to eleven.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "ratio")
        self.play(FadeIn(fixed, shift=UP * 0.1))
        self.at_word(n, "ten", occurrence=1)
        self.play(FadeIn(sp_row[0]), FadeIn(sp_base), FadeIn(sp_row[2]))
        self.play(GrowFromEdge(sp_extra, LEFT), run_time=0.5)
        self.at_word(n, "eleven")
        self.play(FadeIn(ratio, scale=1.05))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_parts_and_ratio")

    # ================================ 5. CONCEPT: MULTIPLY FORWARDS, DIVIDE BACK ==========

    def multiply_and_divide(self):
        self.scene_start("S05_multiply_and_divide", title="Concept - Forwards Multiply, Backwards Divide")

        head = self.heading("Forwards multiply, backwards divide")
        profit = VGroup(pill("SP  =  CP × 1.1", GOOD, size=BODY), pill("CP  =  SP ÷ 1.1", FOCUS, size=BODY)).arrange(RIGHT, buff=0.6)
        loss = VGroup(text("20% loss:", LABEL, MUTED), text("SP  =  CP × 0.8", LABEL, INK, BOLD), text("CP  =  SP ÷ 0.8", LABEL, INK, BOLD))\
            .arrange(RIGHT, buff=0.6)
        why = text("why subtraction fails", LABEL, BAD, BOLD)
        bigger = text("10% of SP is 10% of a bigger number than CP", LABEL, INK)
        too_much = pill("subtracting it removes too much", BAD, size=LABEL)
        self.stack(head, [profit, loss, why, bigger, too_much], buff=0.5, top=0.7)
        self.no_overlap(*profit)
        self.no_overlap(*loss)

        n = self.narrate(
            id="muldiv_01",
            text="Forwards multiply, backwards divide. Selling price is cost price times one point one; cost price is selling "
                 "price divided by one point one.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Forwards")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "times")
        self.play(FadeIn(profit[0], shift=UP * 0.1))
        self.at_word(n, "divided")
        self.play(FadeIn(profit[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="muldiv_02",
            text="For a twenty percent loss, selling price is cost price times zero point eight, and cost price is selling "
                 "price divided by zero point eight.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "times")
        self.play(FadeIn(loss[:2], shift=UP * 0.1))
        self.at_word(n, "divided")
        self.play(FadeIn(loss[2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="muldiv_03",
            text="Why does subtraction fail? Ten percent of the selling price is ten percent of a bigger number than the cost "
                 "price, so subtracting it removes too much.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "subtraction")
        self.play(FadeIn(why, shift=UP * 0.1))
        self.at_word(n, "bigger")
        self.play(FadeIn(bigger, shift=UP * 0.1))
        self.at_word(n, "too")
        self.play(FadeIn(too_much, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_multiply_and_divide")

    # ================================ 6. CONCEPT: TWO PRICES, ONE DIFFERENCE ==========

    def two_prices(self):
        self.scene_start("S06_two_prices", title="Concept - Two Prices, Two Percentages, One Difference")

        head = self.heading("Two prices, two percentages, one difference")
        line = VGroup(pill("price at an L% loss", BAD, size=LABEL), text("←  L%  →", SMALL, MUTED), pill("CP", WORD, size=LABEL),
                      text("←  G%  →", SMALL, MUTED), pill("price at a G% gain", GOOD, size=LABEL)).arrange(RIGHT, buff=0.3)
        gap = pill("the two prices differ by (L + G)% of CP", FOCUS, size=BODY)
        swing = VGroup(text("from a 10% loss to a 5% gain:", LABEL, MUTED), text("a 15% swing on the same CP", LABEL, INK, BOLD))\
            .arrange(RIGHT, buff=0.4)
        equal = VGroup(text("same % profit at S1 as % loss at S2:", LABEL, MUTED), pill("CP = (S1 + S2)/2", GOOD, size=LABEL))\
            .arrange(RIGHT, buff=0.4)
        self.stack(head, [line, gap, swing, equal], buff=0.6, top=0.7)
        self.no_overlap(*line)
        self.no_overlap(*swing)
        self.no_overlap(*equal)

        n = self.narrate(
            id="twoprices_01",
            text="Two prices and two percentages give one difference. If one price gives an L percent loss and another gives a "
                 "G percent gain, the two prices differ by L plus G percent of the cost price.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "difference")
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(line[2], scale=1.1))
        self.at_word(n, "loss")
        self.play(FadeIn(line[:2], shift=RIGHT * 0.1))
        self.at_word(n, "gain")
        self.play(FadeIn(line[3:], shift=LEFT * 0.1))
        self.at_word(n, "plus")
        self.play(FadeIn(gap, scale=1.05))
        self.wait_for_narration(n)

        n = self.narrate(
            id="twoprices_02",
            text="For example, from a ten percent loss to a five percent gain is a fifteen percent swing.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "ten")
        self.play(FadeIn(swing[0], shift=UP * 0.1))
        self.at_word(n, "fifteen")
        self.play(FadeIn(swing[1], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="twoprices_03",
            text="And if the profit percent at one price equals the loss percent at another, the cost price is the average of "
                 "the two prices.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "equals")
        self.play(FadeIn(equal[0], shift=UP * 0.1))
        self.at_word(n, "average")
        self.play(FadeIn(equal[1], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_two_prices")

    # ============================================== 7. FORMULA BOX ==========

    def formula_box(self):
        self.scene_start("S07_formula_box", title="Formula Box")

        head = self.heading("Formula box", GOOD)
        lines = VGroup(*[text(f, LABEL, INK) for f in FORMULAS]).arrange(DOWN, buff=0.5, aligned_edge=LEFT)
        box = self.card(lines, width=SAFE_W - 0.8, color=GOOD, pad=0.5)
        self.stack(head, [box], top=0.8)

        n = self.narrate(
            id="formula_01",
            text="Here is the formula box. Selling price is cost price times one hundred plus P, over a hundred; cost price is "
                 "selling price times a hundred, over one hundred plus P.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "box")
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(box[0]))
        self.at_word(n, "Selling")
        self.play(FadeIn(lines[0], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_02",
            text="For a loss, use one hundred minus L. Forwards multiply, backwards divide.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "loss")
        self.play(FadeIn(lines[1], shift=RIGHT * 0.2))
        self.at_word(n, "Forwards")
        self.play(Indicate(lines[1], color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_03",
            text="The price difference between an L percent loss and a G percent gain is L plus G percent of cost price.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "difference")
        self.play(FadeIn(lines[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_04",
            text="And the same percentage profit at one price as loss at another means cost price is their average.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "average")
        self.play(FadeIn(lines[3], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S07_formula_box")

    # ============================================== 8. THE ANALOGY ==========

    def analogy(self):
        self.scene_start("S08_analogy", title="The Analogy - 100 Equal Weights")

        head = self.heading("Think of CP as 100 equal weights")
        sides = VGroup(pill("CP  =  100 weights", WORD, size=BODY), text("+ 10", BODY, FOCUS, BOLD), pill("SP  =  110 weights", GOOD, size=BODY))\
            .arrange(RIGHT, buff=0.5)
        worth = VGroup(text(f"110 weights  =  {rs(HOOK_SP)}", LABEL, INK), text(f"1 weight  =  {rs(WEIGHT)}", LABEL, INK),
                       text(f"100 weights (CP)  =  {rs(HOOK_CP)}", LABEL, GOOD, BOLD)).arrange(RIGHT, buff=0.7)
        stops = VGroup(text("Where the analogy stops", LABEL, BAD, BOLD),
                       text("the weights only work when the percentage is on CP", LABEL, MUTED),
                       text("“profit is 10% of SP”: the 100 weights belong to SP instead", LABEL, INK)).arrange(DOWN, buff=0.22)
        self.stack(head, [sides, worth, stops], buff=0.8, top=0.8)
        self.no_overlap(*sides)
        self.no_overlap(*worth)

        n = self.narrate(
            id="analogy_01",
            text="Think of cost price as one hundred equal weights.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "weights")
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(sides[0], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_02",
            text="A ten percent profit adds ten more, so selling price is one hundred and ten weights.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "adds")
        self.play(FadeIn(sides[1], shift=UP * 0.1))
        self.at_word(n, "weights")
        self.play(FadeIn(sides[2], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_03",
            text="If the one hundred and ten weights are worth one lakh thirty-two thousand rupees, one weight is twelve hundred "
                 "rupees, and the one hundred weights of cost price are one lakh twenty thousand.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "worth")
        self.play(FadeIn(worth[0], shift=UP * 0.1))
        self.at_word(n, "twelve")
        self.play(FadeIn(worth[1], shift=UP * 0.1))
        self.at_word(n, "twenty")
        self.play(FadeIn(worth[2], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_04",
            text="Where the analogy stops: the weights only work when the percentage is on cost price.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "stops")
        self.play(FadeIn(stops[0], shift=UP * 0.1))
        self.at_word(n, "only")
        self.play(FadeIn(stops[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_05",
            text="If a question says profit is ten percent of selling price, the one hundred weights belong to the selling "
                 "price instead.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "instead")
        self.play(FadeIn(stops[2], shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S08_analogy")

    # ================================ 9. WORKED EXAMPLE: CLOSING THE HOOK ==========

    def hook_solved(self):
        self.scene_start("S09_hook_solved", title="Worked Example - Closing the Hook")

        head = self.heading(f"The laptop:  sold {rs(HOOK_SP)} at {HOOK_PCT}% profit")
        steps = self.solve_steps([("CP  =  1,32,000 ÷ 1.1", f"=  {rs(HOOK_CP)}"),
                                  (f"check:  10% of 1,20,000 = {num(HOOK_CP * HOOK_PCT / 100)}", "1,20,000 + 12,000  =  1,32,000")])
        instinct = text(f"the instinct answer, {rs(HOOK_WRONG)}, took 10% of the wrong base", LABEL, BAD, BOLD)
        self.stack(head, [steps, instinct], buff=0.9, top=0.9)
        self.no_overlap(*steps)

        n = self.narrate(
            id="solved_01",
            text="Cost price is one lakh thirty-two thousand divided by one point one: one lakh twenty thousand rupees.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "divided")
        self.play(FadeIn(steps[0][:2], shift=RIGHT * 0.1))
        self.at_word(n, "twenty")
        self.play(FadeIn(steps[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_02",
            text="Check: ten percent of one lakh twenty thousand is twelve thousand, and adding it back gives one lakh "
                 "thirty-two thousand.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Check")
        self.play(FadeIn(steps[1][:2], shift=RIGHT * 0.1))
        self.at_word(n, "adding")
        self.play(FadeIn(steps[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_03",
            text="The instinct answer, one lakh eighteen thousand eight hundred, took ten percent of the wrong base.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "instinct")
        self.play(FadeIn(instinct, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S09_hook_solved")

    # ====================== 10. SECOND WORKED EXAMPLE: LOSS TO GAIN ==========

    def second_example(self):
        self.scene_start("S10_second_example", title="A Second Worked Example - Loss to Gain")

        head = self.heading("From a loss to a gain")
        given = VGroup(pill("sold for ₹2,340", WORD, size=LABEL), pill("loses 10%", BAD, size=LABEL),
                       pill("price for a 10% gain = ?", FOCUS, size=LABEL)).arrange(RIGHT, buff=0.4)
        steps = self.solve_steps([("CP  =  2,340 ÷ 0.9", f"=  {rs(EX_CP)}"),
                                  ("new SP  =  2,600 × 1.1", f"=  {rs(EX_NEW)}"),
                                  (f"check:  the gap 2,860 − 2,340 = {rs(EX_NEW - 2340)}", "=  20% of 2,600")])
        self.stack(head, [given, steps], buff=0.8, top=0.8)
        self.no_overlap(*given)
        self.no_overlap(*steps)

        n = self.narrate(
            id="gain_01",
            text="By selling an article for two thousand three hundred and forty rupees, a trader loses ten percent. At what "
                 "price should he sell it to gain ten percent?",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "forty")
        self.play(FadeIn(given[0], shift=UP * 0.1))
        self.at_word(n, "loses")
        self.play(FadeIn(given[1], shift=UP * 0.1))
        self.at_word(n, "gain")
        self.play(FadeIn(given[2], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="gain_02",
            text="Cost price is two thousand three hundred and forty divided by zero point nine: two thousand six hundred.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "divided")
        self.play(FadeIn(steps[0][:2], shift=RIGHT * 0.1))
        self.at_word(n, "six")
        self.play(FadeIn(steps[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="gain_03",
            text="The new selling price is two thousand six hundred times one point one: two thousand eight hundred and sixty.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "times")
        self.play(FadeIn(steps[1][:2], shift=RIGHT * 0.1))
        self.at_word(n, "sixty")
        self.play(FadeIn(steps[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="gain_04",
            text="Check: the gap of five hundred and twenty rupees is twenty percent of two thousand six hundred.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "gap")
        self.play(FadeIn(steps[2][:2], shift=RIGHT * 0.1))
        self.at_word(n, "percent")
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
            text="Cost price from selling price: sold at twenty-five percent profit for fifteen hundred, so fifteen hundred "
                 "divided by one point two five, twelve hundred rupees.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "sold")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "divided")
        self.play(FadeIn(rows[0][2:], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="patterns_03",
            text="Loss to gain: a ten percent loss at two thousand three hundred and forty means a cost of two thousand six "
                 "hundred, and times one point one gives two thousand eight hundred and sixty.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Loss")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "times")
        self.play(FadeIn(rows[1][2:], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="patterns_04",
            text="Price difference: a ten percent loss, and ninety rupees more would give a five percent gain, so fifteen "
                 "percent of cost price is ninety, and cost price is six hundred.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "difference")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "fifteen")
        self.play(FadeIn(rows[2][2:], shift=RIGHT * 0.2))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Exam patterns  ·  4 and 5 of 5")
        table, rows = self.pattern_table(head, PATTERNS_B)

        n = self.narrate(
            id="patterns_05",
            text="A chain of sales: A sells to B at twenty percent profit, and B sells to C at twenty-five percent profit for "
                 "fifteen hundred. Divide by one point two five, then by one point two: A's cost is one thousand.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "chain")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "Divide")
        self.play(FadeIn(rows[0][2:], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="patterns_06",
            text="Equal percentages at two prices: the same percent profit at one thousand and forty as percent loss at eight "
                 "hundred and eighty means cost price is the average, nine hundred and sixty.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Equal")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "average")
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
            text="Trap one: subtracting the percentage from the selling price. Sold for one lakh thirty-two thousand at ten "
                 "percent profit; find the cost price.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "subtracting")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "Sold")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="trap1_02",
            text="The wrong instinct is one lakh eighteen thousand eight hundred. The correct answer is one lakh twenty "
                 "thousand.",
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
            text="The rule: a percentage taken on cost price is undone only by dividing by the multiplier.",
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
            text="Trap two: the price difference split wrongly. At a ten percent loss, he would gain five percent by selling "
                 "for ninety rupees more; find the cost price.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "split")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "ninety")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="trap2_02",
            text="The wrong instinct says five percent of cost price is ninety, so eighteen hundred. Correctly, fifteen percent "
                 "of cost price is ninety, so six hundred.",
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
            text="The rule: going from minus ten to plus five is a fifteen-point swing on the same cost price.",
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
            text="Trap three: a chain solved in the wrong order. A sells to B at twenty percent profit, and B sells to C at "
                 "twenty-five percent profit for fifteen hundred; find A's cost.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "order")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "sells")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="trap3_02",
            text="The wrong instinct divides fifteen hundred by one point four five. Correctly, divide by one point two five, "
                 "then by one point two: one thousand rupees.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "divides")
        self.play(FadeIn(wrong, shift=UP * 0.1))
        self.at_word(n, "Correctly")
        self.play(FadeIn(right, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="trap3_03",
            text="The rule: each sale has its own cost price, so divide back one step at a time.",
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
        given = VGroup(pill("a shirt, sold for ₹640", WORD, size=LABEL), pill("at a 20% loss", BAD, size=LABEL)).arrange(RIGHT, buff=0.5)
        hint = pill("what did it cost?", FOCUS, size=BODY)
        work = VGroup(text("CP  =  640 ÷ 0.8", BODY, INK), text(f"=  {rs(CP_ANSWER)}", BODY, GOOD, BOLD)).arrange(RIGHT, buff=0.5)
        self.stack(head, [given, hint, work], buff=0.8, top=0.9)
        self.no_overlap(*given)
        self.no_overlap(*work)

        n = self.narrate(
            id="check_01",
            text="Your turn. A shirt is sold at a twenty percent loss for six hundred and forty rupees. What did it cost?",
            voice="default",
            subtitle=True,
            pause_after=10.0,
        )
        self.at_word(n, "turn")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "loss")
        self.play(FadeIn(given[1], shift=UP * 0.1))
        self.at_word(n, "forty")
        self.play(FadeIn(given[0], shift=UP * 0.1))
        self.at_word(n, "cost")
        self.play(FadeIn(hint, shift=UP * 0.1))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="check_02",
            text="Cost price is six hundred and forty divided by zero point eight: eight hundred rupees.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "divided")
        self.play(FadeIn(work[0], shift=UP * 0.1))
        self.at_word(n, "rupees")
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
            text="Level one, question one: an article is sold for eleven hundred and forty rupees at a five percent loss; find "
                 "the cost price. Question two: an article costs five hundred rupees; at what price must it be sold for a "
                 "twelve percent profit? Question three: an article sold at an eight percent profit fetches one thousand and "
                 "eighty rupees; find the cost price.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "loss")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "costs")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.at_word(n, "fetches")
        self.play(FadeIn(rows[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="practice_02",
            text="Level two, question four: a trader gains twenty percent on an article sold at three hundred and sixty rupees; "
                 "at what price would he have lost thirty percent? Question five: A sells to B at a twenty percent profit, "
                 "and B sells to C at a twenty-five percent profit for fifteen hundred rupees; find A's cost price. Question "
                 "six: an article sold at a twenty-five percent profit fetches fifteen hundred rupees; find the cost price.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "gains")
        self.play(FadeIn(rows[3], shift=RIGHT * 0.2))
        self.at_word(n, "sells")
        self.play(FadeIn(rows[4], shift=RIGHT * 0.2))
        self.at_word(n, "fetches")
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
            text="Level three, question seven: an article is sold at a ten percent loss; had it been sold for ninety rupees "
                 "more, there would have been a five percent gain; find the cost price. Question eight: A sells to B at a ten "
                 "percent profit, and B sells to C at a twenty percent loss; C pays thirteen hundred and twenty rupees; find "
                 "A's cost price. Question nine: the profit percent when an article is sold for one thousand and forty rupees "
                 "equals the loss percent when it is sold for eight hundred and eighty; find the cost price and that "
                 "percentage.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "ninety")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "pays")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.at_word(n, "equals")
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
            text="One: cost price is eleven hundred and forty divided by zero point nine five, twelve hundred rupees.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "divided")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "twelve")
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_02",
            text="Two: selling price is five hundred times one point one two, five hundred and sixty rupees.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "times")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "sixty")
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_03",
            text="Three: cost price is one thousand and eighty divided by one point zero eight, one thousand rupees.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "divided")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "rupees")
        self.play(FadeIn(rows[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_04",
            text="Four: cost price is three hundred and sixty divided by one point two, three hundred. At a thirty percent "
                 "loss, three hundred times zero point seven is two hundred and ten.",
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
            text="Five: B's cost is fifteen hundred divided by one point two five, twelve hundred, which is A's selling price. "
                 "A's cost is twelve hundred divided by one point two: one thousand.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "divided", occurrence=1)
        self.play(FadeIn(rows[4][:2], shift=RIGHT * 0.2))
        self.at_word(n, "thousand")
        self.play(FadeIn(rows[4][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Answer key  ·  6 to 9", GOOD)
        table, rows = self.answer_table(head, ANSWERS_B, 6)

        n = self.narrate(
            id="answers_06",
            text="Six: cost price is fifteen hundred divided by one point two five, twelve hundred rupees.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "divided")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "twelve")
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_07",
            text="Seven: from minus ten to plus five is fifteen percent of cost price, which is ninety, so cost price is six "
                 "hundred. Check: five hundred and forty and six hundred and thirty differ by ninety.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "fifteen")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "six")
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_08",
            text="Eight: B's cost is thirteen hundred and twenty divided by zero point eight, sixteen hundred and fifty. A's "
                 "cost is sixteen hundred and fifty divided by one point one: fifteen hundred.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "divided", occurrence=1)
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "fifteen")
        self.play(FadeIn(rows[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_09",
            text="Nine: the gaps above and below cost price are equal, so cost price is the average, nine hundred and sixty. "
                 "The percentage is eighty over nine hundred and sixty: eight and one third percent.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "average")
        self.play(FadeIn(rows[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "percentage")
        self.play(FadeIn(rows[3][2], shift=LEFT * 0.1))
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
            text="Recognise and move. The recognition cue: sold for a price at some percent profit or loss, find the cost. "
                 "Divide.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Recognise")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "cue")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "Divide")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="lens_02",
            text="The target time: thirty seconds, or forty seconds for loss to gain.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "target")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "forty")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="lens_03",
            text="The sanity check: with a profit, cost price is below selling price, but by less than that percentage of "
                 "selling price; with a loss, cost price is above selling price.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "sanity")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "below")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S16_exam_lens")

    # ==================================== 17. QUICK REVISION + SUMMARY ==========

    def summary(self):
        self.scene_start("S17_summary", title="Quick Revision and Summary")

        head = self.heading("Quick revision")
        ways = VGroup(pill("CP → SP:   multiply", GOOD, size=LABEL), pill("SP → CP:   divide     CP = SP ÷ (1 ± P/100)", FOCUS, size=LABEL))\
            .arrange(RIGHT, buff=0.5)
        box = VGroup(text("price gap between L% loss and G% gain   =   (L + G)% of CP", LABEL, INK),
                     text("chains of sales: undo one step at a time", LABEL, INK)).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        trap = pill("never subtract the percentage from the selling price", BAD, size=LABEL)
        nxt = self.breadcrumb("Next", "Video 3 · Discount: Single & Successive")
        self.stack(head, [ways, box, trap, nxt], buff=0.65, top=0.7)
        self.no_overlap(*ways)
        self.no_overlap(*box)

        n = self.narrate(
            id="summary_01",
            text="Multiply to go from cost price to selling price; divide to go back.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "Multiply")
        self.play(FadeIn(ways[0], shift=UP * 0.1))
        self.at_word(n, "divide")
        self.play(FadeIn(ways[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_02",
            text="Price differences between a loss and a gain are L plus G percent of cost price, and chains are undone one "
                 "step at a time.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "plus")
        self.play(FadeIn(box[0], shift=RIGHT * 0.2))
        self.at_word(n, "chains")
        self.play(FadeIn(box[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_03",
            text="Remember the trap: never subtract the percentage from the selling price.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "never")
        self.play(FadeIn(trap, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_04",
            text="Next: discounts, single and successive.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Next")
        self.play(FadeIn(nxt, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S17_summary")

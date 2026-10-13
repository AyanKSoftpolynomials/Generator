"""
animation.py for the LMS video generator.

Course : Pre-C-CAT - Section A - Quantitative Aptitude
Video  : Lesson 12 - Profit & Loss - 07 - Partial Sales & Break-Even

Source script:
  C:\\Scripts\\Section A\\Module_2_Section_A_Quantitative_Aptitude_Part_1\\Aptitude_Scripts\\Sessions 1-4 - Interest, Profit & Loss, Time & Work\\Lesson 12 - Profit & Loss\\07 - Partial Sales & Break-Even.pdf

Built on the golden-reference pattern:
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``;
  * layouts stacked with next_to and guarded with ``no_overlap``; nothing is
    ever animated onto or into another box.

Lesson 12, Video 7 of 8. Not the first video of the lesson: a silent breadcrumb, a one-line recap of Video 6, then today's topic. No spoken course welcome.
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


def pct(x):
    return f"{round(float(x), 2):g}"


def rs(x):
    return f"₹{round(x):,}"


def price_for_rest(total_cost, sales_so_far, items_left, target_pct=0):
    """(target sales, money still needed, price each for the items left)."""
    target = Fraction(total_cost) * (100 + target_pct) / 100
    needed = target - sales_so_far
    return target, needed, needed / items_left


def weighted(*parts):
    """Overall % = Σ (cost share × part %).  parts = (share, percent), shares adding to 1."""
    assert sum(Fraction(s) for s, _ in parts) == 1
    return sum(Fraction(s) * Fraction(p) for s, p in parts)


# ---- the hook: 100 shirts ----
QTY, COST, SOLD, PRICE = 100, 500, 60, 600
TOTAL_COST, SALES = QTY * COST, SOLD * PRICE
_, NEEDED, REST_PRICE = price_for_rest(TOTAL_COST, SALES, QTY - SOLD)
DISCOUNT = Fraction(PRICE - REST_PRICE, PRICE) * 100
REST_LOSS = Fraction(COST - REST_PRICE, COST) * 100
assert (TOTAL_COST, SALES, NEEDED, REST_PRICE, pct(DISCOUNT), REST_LOSS) == (50000, 36000, 14000, 350, "41.67", 30)

# ---- second worked example: a profit target ----
EX_COST, EX_SALES = 50 * 40, 30 * 50
EX_TARGET, EX_NEEDED, EX_PRICE = price_for_rest(EX_COST, EX_SALES, 20, 20)
assert (EX_COST, EX_TARGET, EX_SALES, EX_NEEDED, EX_PRICE) == (2000, 2400, 1500, 900, 45)

# ---- exam patterns (answers computed) ----
P1 = price_for_rest(100 * 10, 60 * 12, 40)[2]
P2 = price_for_rest(80 * 20, 50 * 25, 30, 25)
P3 = weighted((Fraction(1, 3), 24), (Fraction(2, 3), -6))
P4 = (16 - Fraction("0.4") * 10) / Fraction("0.6")
P5 = price_for_rest(120 * 50, 0, 100, 20)
assert (P1, P2, P3, P4, P5) == (7, (2000, 750, 25), 4, 20, (7200, 7200, 72))
PATTERNS_A = [("Break-even price", "100 items at ₹10; 60 sold at ₹12", "(1,000 − 720) ÷ 40", f"{rs(P1)} each"),
              ("Target profit price", "80 at ₹20; 50 sold at ₹25; 25% overall", "(2,000 − 1,250) ÷ 30", f"{rs(P2[2])} each"),
              ("Weighted %", "1/3 at 24% profit, rest at 6% loss", "(24 − 12)/3", f"{P3}% profit")]
PATTERNS_B = [("Required % on the rest", "40% at 10% profit; 16% overall wanted", "0.4 × 10 + 0.6x = 16", f"{P4}%"),
              ("Damaged stock", "120 at ₹50; 20 unsellable; 20% profit", "7,200 ÷ 100", f"{rs(P5[2])} each")]

# ---- traps: (title, question, wrong, right, rule) ----
TRAPS = [("Trap 1  ·  mirroring the percentage", "60 shirts sold at 20% profit.  Loss % on the other 40 to break even?",
          "20%", f"{REST_LOSS}%    (₹150 on each ₹500 shirt)",
          "The gains on 60 items must be absorbed by only 40 items."),
         ("Trap 2  ·  unweighted average of percentages", "1/3 of the goods at 24% profit, the rest at 6% loss.  Overall?",
          "(24 − 6)/2  =  9%", f"8 − 4  =  {P3}%",
          "Weight each percentage by its share of the cost."),
         ("Trap 3  ·  damaged items left out of the cost", "120 items at ₹50; 20 are damaged.  Price on the rest for a 20% profit?",
          "50 × 1.2  =  ₹60", f"7,200 ÷ 100  =  {rs(P5[2])}",
          "Unsold or damaged items still count in the total cost.")]

# ---- checkpoint ----
CP_ANSWER = weighted((Fraction(1, 2), 30), (Fraction(1, 2), -10))
assert CP_ANSWER == 10

# ---- practice (answers computed) ----
PRACTICE_A = [("L1", "100 items cost ₹10 each.  60 are sold at ₹12 each.  At what price must the rest be sold to break even?"),
              ("L1", "Half the goods are sold at a 25% profit and half at a 15% loss, each half with the same cost.  Find the overall result."),
              ("L2", "A trader buys 40 kg of rice at ₹30/kg and sells 25 kg at ₹36/kg.  At what price per kg must he sell the "
                     "remaining 15 kg for a 10% overall profit?"),
              ("L2", "One-third of the goods (by cost) is sold at a 24% profit and the rest at a 6% loss.  Find the overall result."),
              ("L2", "80 articles cost ₹20 each.  50 are sold at ₹25 each.  At what price must the rest be sold to gain 25% overall?")]
PRACTICE_B = [("L3", "A trader sells 40% of his stock (by cost) at a 10% profit.  At what profit % must he sell the rest to make 16% overall?"),
              ("L3", "120 items are bought at ₹50 each.  20 are damaged and cannot be sold.  At what price must each remaining "
                     "item be sold to make a 20% profit overall?"),
              ("L3", "Three-quarters of the goods (by cost) are sold at a 20% profit and the rest at cost price.  Find the overall profit %.")]
A2 = weighted((Fraction(1, 2), 25), (Fraction(1, 2), -15))
A3 = price_for_rest(40 * 30, 25 * 36, 15, 10)
A8 = weighted((Fraction(3, 4), 20), (Fraction(1, 4), 0))
assert (A2, A3, A8) == (5, (1320, 420, 28), 15) and (100 * Fraction("1.24"), 200 * Fraction("0.94")) == (124, 188)
ANSWERS_A = [("total cost ₹1,000;   collected ₹720;   needed ₹280 from 40 items", f"{rs(P1)} each"),
             ("(25 − 15)/2", f"{A2}% profit"),
             ("target = 1,200 × 1.1 = ₹1,320;   collected ₹900;   needed ₹420 from 15 kg", f"{rs(A3[2])} per kg"),
             ("on a cost of ₹300:   ₹100 → ₹124,   ₹200 → ₹188;   total ₹312", f"{P3}% profit"),
             ("cost ₹1,600;   target ₹2,000;   collected ₹1,250;   needed ₹750 from 30", f"{rs(P2[2])} each")]
ANSWERS_B = [("0.4 × 10 + 0.6x = 16;   0.6x = 12", f"x = {P4}%"),
             ("cost ₹6,000;   target ₹7,200 from 100 items", f"{rs(P5[2])} each"),
             ("0.75 × 20 + 0.25 × 0", f"{A8}% profit")]

OBJECTIVES = [("Find the overall profit or loss", "when parts of the stock sell at different prices"),
              ("Find the price for the remaining stock", "to break even, or to reach a target"),
              ("Average percentages correctly", "weighted by cost")]
LENS = [("Recognition cue", "“the rest”, “remaining”, “to break even”, “overall”  →  totals in rupees"),
        ("Target time", "60 seconds"),
        ("Sanity check", "the overall % always lies between the smallest and the largest part %")]
FORMULAS = ["Overall result  =  Total SP − Total CP",
            "Price for the rest  =  (Target sales − sales so far) ÷ items left",
            "Target sales  =  Total CP × (1 + P/100)            (P = 0 for break-even)",
            "Overall %  =  Σ (cost share × part %)"]


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


class PartialSalesAndBreakEvenVideo(LMSScene):
    lesson_title = "Partial Sales & Break-Even"

    def construct(self):
        self.camera.background_color = BG

        self.intro()
        self.hook()
        self.objectives()
        self.why_this_matters()
        self.work_in_totals()
        self.weighted_average()
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
    # Not the first video: silent breadcrumb, a one-line recap of Video 6, then today's topic.

    def intro(self):
        self.scene_start("S00_intro", title="Intro")

        crumb = self.breadcrumb("Quantitative Aptitude", "Lesson 12 · Profit & Loss", "Video 7 of 8")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        recap = VGroup(text("last video", SMALL, MUTED), pill("same SP, ±x%:  always a loss of x²/100 %", WORD, size=LABEL))\
            .arrange(DOWN, buff=0.25)
        title = text("Partial Sales & Break-Even", TITLE, INK, BOLD)
        today = text("today: stock that sells in parts, at different prices", LABEL, FOCUS)
        block = VGroup(recap, title, today).arrange(DOWN, buff=0.7)
        fit_within(block, SAFE_W, SAFE_H - crumb.height - 0.9)
        block.next_to(crumb, DOWN, buff=0.7)
        self.no_overlap(crumb, recap, title, today)
        self.validator.check_in_frame(VGroup(crumb, block))

        n = self.narrate(
            id="intro_01",
            text="In the last video, two articles sold at the same price, at plus and minus x percent, always gave a loss.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.at_word(n, "loss")
        self.play(FadeIn(recap, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="intro_02",
            text="Today: stock that sells in parts, at different prices.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "parts")
        self.play(FadeIn(title, shift=UP * 0.1))
        self.at_word(n, "different")
        self.play(FadeIn(today, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_intro")

    # =================================================== 1. HOOK ==========

    def hook(self):
        self.scene_start("S01_hook", title="Hook")

        head = self.heading("A stockroom")
        lines = VGroup(text(f"{QTY} shirts  ·  cost {rs(COST)} each", BODY, INK, BOLD),
                       text(f"{SOLD} sold at {rs(PRICE)}  (a 20% markup)", LABEL, GOOD, BOLD),
                       text(f"{QTY - SOLD} still on the shelf", LABEL, BAD, BOLD)).arrange(DOWN, buff=0.3)
        stock = self.card(lines, width=7.6, color=WORD, pad=0.45)
        asks = VGroup(pill(f"price for the remaining {QTY - SOLD}, to avoid a loss = ?", FOCUS, size=LABEL),
                      pill(f"discount off the {rs(PRICE)} tag = ?", RATIO, size=LABEL)).arrange(DOWN, buff=0.3)
        worry = text("this is why inventory managers worry about unsold stock", SMALL, GOOD, BOLD)
        self.stack(head, [stock, asks, worry], buff=0.55, top=0.6)

        n = self.narrate(
            id="hook_01",
            text="A retailer buys one hundred shirts at five hundred rupees each, and sells sixty of them at six hundred, a "
                 "twenty percent markup.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "hundred")
        self.play(FadeIn(stock[0]), FadeIn(lines[0], shift=UP * 0.1))
        self.at_word(n, "sixty")
        self.play(FadeIn(lines[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_02",
            text="The other forty aren't moving.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "forty")
        self.play(FadeIn(lines[2], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_03",
            text="To avoid a loss overall, what must he charge for the remaining forty? And how big a discount is that, off his "
                 "six hundred rupee tag?",
            voice="default",
            subtitle=True,
            pause_after=3.0,
        )
        self.at_word(n, "charge")
        self.play(FadeIn(asks[0], shift=UP * 0.1))
        self.at_word(n, "discount")
        self.play(FadeIn(asks[1], shift=UP * 0.1))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="hook_04",
            text="The answer shows why inventory managers worry about unsold stock.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "unsold")
        self.play(FadeIn(worry, shift=UP * 0.1))
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
            text="First, find the overall profit or loss when parts of the stock sell at different prices.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "overall")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "parts")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="obj_03",
            text="Second, find the price needed on the remaining stock, to break even or reach a target.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "remaining")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "target")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="obj_04",
            text="Third, use cost-weighted averages of percentages correctly.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "cost-weighted")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "correctly")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_objectives")

    # ========================================== 3. WHY THIS MATTERS ==========

    def why_this_matters(self):
        self.scene_start("S03_why_this_matters", title="Why This Matters")

        head = self.heading("Why this matters")
        never = text("real stock never sells at one price", LABEL, INK)
        rupees = pill("to judge the whole: add rupees, not percentages", GOOD, size=LABEL)
        rest = pill("“at what price must the rest be sold?”:  a standard exam question", WORD, size=LABEL)
        totals = text("it rewards anyone who works in totals", LABEL, FOCUS, BOLD)
        self.stack(head, [never, rupees, rest, totals], buff=0.65, top=0.8)

        n = self.narrate(
            id="why_01",
            text="Real stock never sells at one price. To judge the whole, you add rupees, not percentages.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "never")
        self.play(FadeIn(never, shift=UP * 0.1))
        self.at_word(n, "rupees")
        self.play(FadeIn(rupees, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="why_02",
            text="At what price must the rest be sold is a standard exam question, and it rewards anyone who works in totals.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "rest")
        self.play(FadeIn(rest, shift=UP * 0.1))
        self.at_word(n, "totals")
        self.play(FadeIn(totals, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_why_this_matters")

    # ==================================== 4. CONCEPT: WORK IN TOTALS ==========

    def work_in_totals(self):
        self.scene_start("S04_work_in_totals", title="Concept - Total Cost Is the Target Line")

        head = self.heading("Total cost is the target line")
        cost = text("Total CP  =  quantity × cost each     (plus any overheads)", LABEL, INK)
        sales = text("sales so far  =  every part's rupee sales, added up", LABEL, INK)
        even = pill("break-even:  total sales = total cost", GOOD, size=LABEL)
        needed = text("still needed  =  total CP − sales so far", LABEL, INK)
        each = pill("price each  =  still needed ÷ items left", FOCUS, size=LABEL)
        raise_line = VGroup(text("for a profit target, raise the line first:", LABEL, MUTED),
                            pill("target sales  =  total CP × (1 + P/100)", RATIO, size=LABEL)).arrange(RIGHT, buff=0.4)
        self.stack(head, [cost, sales, even, needed, each, raise_line], buff=0.38, top=0.5)
        self.no_overlap(*raise_line)

        n = self.narrate(
            id="totals_01",
            text="Total cost is the target line. Total cost price is the quantity times the cost of each, plus any overheads.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "target")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "times")
        self.play(FadeIn(cost, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="totals_02",
            text="Sales accumulate part by part: add every part's rupee sales.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "add")
        self.play(FadeIn(sales, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="totals_03",
            text="Break-even means total sales equal total cost. The money still needed is total cost minus sales so far. "
                 "Divide by the items left to get the price each.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Break-even")
        self.play(FadeIn(even, shift=UP * 0.1))
        self.at_word(n, "minus")
        self.play(FadeIn(needed, shift=UP * 0.1))
        self.at_word(n, "Divide")
        self.play(FadeIn(each, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="totals_04",
            text="For a profit target, raise the line first: target sales are total cost times one plus P over a hundred.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "raise")
        self.play(FadeIn(raise_line[0], shift=UP * 0.1))
        self.at_word(n, "times")
        self.play(FadeIn(raise_line[1], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_work_in_totals")

    # ==================================== 5. CONCEPT: THE WEIGHTED AVERAGE ==========

    def weighted_average(self):
        self.scene_start("S05_weighted_average", title="Concept - Percentages Average Only When Weighted by Cost")

        head = self.heading("Percentages average only when weighted by cost")
        rule = pill("overall %  =  Σ (cost share × part %)", GOOD, size=BODY)
        example = VGroup(text("1/3 at 24% profit,  2/3 at 6% loss:", LABEL, MUTED), text("1/3 × 24  +  2/3 × (−6)", LABEL, INK, BOLD),
                         text(f"=  8 − 4  =  {P3}%", LABEL, GOOD, BOLD)).arrange(RIGHT, buff=0.4)
        equal = text("with equal cost shares, that is a simple average", LABEL, RATIO, BOLD)
        self.stack(head, [rule, example, equal], buff=0.9, top=1.0)
        self.no_overlap(*example)

        n = self.narrate(
            id="weighted_01",
            text="Percentages can be averaged only when weighted by cost.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "weighted")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="weighted_02",
            text="The overall percent is the sum, over the parts, of cost share times part percent.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "sum")
        self.play(FadeIn(rule, scale=1.05))
        self.wait_for_narration(n)

        n = self.narrate(
            id="weighted_03",
            text="For example, one third at twenty-four percent profit, and two thirds at six percent loss, gives eight minus "
                 "four: four percent.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "third")
        self.play(FadeIn(example[:2], shift=UP * 0.1))
        self.at_word(n, "minus")
        self.play(FadeIn(example[2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="weighted_04",
            text="With equal cost shares, that is a simple average.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "equal")
        self.play(FadeIn(equal, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_weighted_average")

    # ============================================== 6. FORMULA BOX ==========

    def formula_box(self):
        self.scene_start("S06_formula_box", title="Formula Box")

        head = self.heading("Formula box", GOOD)
        lines = VGroup(*[text(f, LABEL, INK) for f in FORMULAS]).arrange(DOWN, buff=0.5, aligned_edge=LEFT)
        box = self.card(lines, width=SAFE_W - 0.8, color=GOOD, pad=0.5)
        self.stack(head, [box], top=0.8)

        n = self.narrate(
            id="formula_01",
            text="Here is the formula box. The overall result is total selling price minus total cost price.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "box")
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(box[0]))
        self.at_word(n, "overall")
        self.play(FadeIn(lines[0], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_02",
            text="The price for the rest is target sales minus sales so far, divided by the items left.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "rest")
        self.play(FadeIn(lines[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_03",
            text="Target sales are total cost times one plus P over a hundred, with P equal to zero for break-even.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Target")
        self.play(FadeIn(lines[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_04",
            text="And the overall percent is the sum of cost share times part percent.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "sum")
        self.play(FadeIn(lines[3], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_formula_box")

    # ============================================== 7. THE ANALOGY ==========

    def analogy(self):
        self.scene_start("S07_analogy", title="The Analogy - A Team Chasing a Target")

        head = self.heading("Think of a team chasing a target")
        batters = VGroup(pill("batter 1:  scores heavily", GOOD, size=LABEL), pill("batter 2:  scores barely", BAD, size=LABEL),
                         pill("batter 3:  hasn't batted yet", MUTED, size=LABEL)).arrange(RIGHT, buff=0.4)
        judge = VGroup(text("not any one batter's strike rate", LABEL, BAD), text("the team total against the target", LABEL, GOOD, BOLD))\
            .arrange(RIGHT, buff=0.7)
        last = pill("what does the last batter need?", FOCUS, size=LABEL)
        stops = VGroup(text("Where the analogy stops", LABEL, BAD, BOLD),
                       text("runs are all worth the same", LABEL, MUTED),
                       text("a percentage on a big cost share counts for more: weights matter", LABEL, INK)).arrange(DOWN, buff=0.22)
        self.stack(head, [batters, judge, last, stops], buff=0.55, top=0.6)
        self.no_overlap(*batters)
        self.no_overlap(*judge)

        n = self.narrate(
            id="analogy_01",
            text="Think of a team chasing a target.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "target")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_02",
            text="One batter scores heavily, another barely, and one hasn't batted yet.",
            voice="default",
            subtitle=True,
        )
        for chip, spoken in zip(batters, ["heavily", "barely", "yet"]):
            self.at_word(n, spoken)
            self.play(FadeIn(chip, shift=UP * 0.1), run_time=0.45)
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_03",
            text="You don't judge the chase by any one batter's strike rate; you compare the team total with the target, and "
                 "ask what the last batter needs.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "strike")
        self.play(FadeIn(judge[0], shift=UP * 0.1))
        self.at_word(n, "total")
        self.play(FadeIn(judge[1], shift=LEFT * 0.1))
        self.at_word(n, "needs")
        self.play(FadeIn(last, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_04",
            text="Where the analogy stops: runs are all worth the same.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "stops")
        self.play(FadeIn(stops[0], shift=UP * 0.1))
        self.at_word(n, "same")
        self.play(FadeIn(stops[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_05",
            text="In stock problems, a percentage on a big cost share counts for more than the same percentage on a small one, "
                 "which is why weights matter.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "weights")
        self.play(FadeIn(stops[2], shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S07_analogy")

    # ================================ 8. WORKED EXAMPLE: CLOSING THE HOOK ==========

    def hook_solved(self):
        self.scene_start("S08_hook_solved", title="Worked Example - Closing the Hook")

        head = self.heading(f"The shirts:  {QTY} at {rs(COST)},  {SOLD} sold at {rs(PRICE)}")
        steps = self.solve_steps([("total cost  =  100 × 500", f"=  {rs(TOTAL_COST)}"),
                                  ("sales so far  =  60 × 600", f"=  {rs(SALES)}"),
                                  (f"still needed:  {rs(NEEDED)} from {QTY - SOLD} shirts", f"=  {rs(REST_PRICE)} each")])
        cost_of_it = VGroup(text(f"{rs(PRICE - REST_PRICE)} off the {rs(PRICE)} tag:  a {pct(DISCOUNT)}% discount", LABEL, INK),
                            text(f"a {REST_LOSS}% loss on cost", LABEL, BAD, BOLD)).arrange(RIGHT, buff=0.7)
        moral = pill("a healthy margin on part of the stock forces a deep markdown on the rest", FOCUS, size=LABEL)
        self.stack(head, [steps, cost_of_it, moral], buff=0.6, top=0.6)
        self.no_overlap(*steps)
        self.no_overlap(*cost_of_it)

        n = self.narrate(
            id="solved_01",
            text="Total cost is one hundred times five hundred: fifty thousand rupees.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "times")
        self.play(FadeIn(steps[0][:2], shift=RIGHT * 0.1))
        self.at_word(n, "fifty")
        self.play(FadeIn(steps[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_02",
            text="Sales so far are sixty times six hundred: thirty-six thousand.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "times")
        self.play(FadeIn(steps[1][:2], shift=RIGHT * 0.1))
        self.at_word(n, "thirty-six")
        self.play(FadeIn(steps[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_03",
            text="So fourteen thousand is still needed from forty shirts: three hundred and fifty rupees each.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "fourteen")
        self.play(FadeIn(steps[2][:2], shift=RIGHT * 0.1))
        self.at_word(n, "each")
        self.play(FadeIn(steps[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_04",
            text="That is two hundred and fifty rupees off the six hundred rupee tag, a forty-one point six seven percent "
                 "discount, and a thirty percent loss on cost.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "discount")
        self.play(FadeIn(cost_of_it[0], shift=UP * 0.1))
        self.at_word(n, "thirty")
        self.play(FadeIn(cost_of_it[1], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_05",
            text="A healthy margin on part of the stock forces a deep markdown on the rest, just to break even.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "markdown")
        self.play(FadeIn(moral, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S08_hook_solved")

    # ====================== 9. SECOND WORKED EXAMPLE: A PROFIT TARGET ==========

    def second_example(self):
        self.scene_start("S09_second_example", title="A Second Worked Example - A Profit Target")

        head = self.heading("A profit target  ·  rice")
        given = VGroup(pill("buys 50 kg at ₹40/kg", WORD, size=LABEL), pill("sells 30 kg at ₹50/kg", GOOD, size=LABEL),
                       pill("wants 20% profit overall", RATIO, size=LABEL), pill("price for the last 20 kg = ?", FOCUS, size=LABEL))\
            .arrange_in_grid(rows=2, cols=2, buff=0.3)
        steps = self.solve_steps([(f"total cost = {rs(EX_COST)};    target sales = 2,000 × 1.2", f"=  {rs(EX_TARGET)}"),
                                  (f"collected = 30 × 50 = {rs(EX_SALES)};    needed {rs(EX_NEEDED)} from 20 kg", f"=  {rs(EX_PRICE)} per kg")])
        self.stack(head, [given, steps], buff=0.8, top=0.7)
        self.no_overlap(*given)
        self.no_overlap(*steps)

        n = self.narrate(
            id="rice_01",
            text="A trader buys fifty kilograms of rice at forty rupees a kilogram, and sells thirty kilograms at fifty rupees a "
                 "kilogram. At what price must he sell the remaining twenty kilograms, for a twenty percent profit overall?",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "fifty")
        self.play(FadeIn(given[0], shift=UP * 0.1))
        self.at_word(n, "thirty")
        self.play(FadeIn(given[1], shift=UP * 0.1))
        self.at_word(n, "remaining")
        self.play(FadeIn(given[3], shift=UP * 0.1))
        self.at_word(n, "profit")
        self.play(FadeIn(given[2], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="rice_02",
            text="Total cost is two thousand rupees, so target sales are two thousand times one point two: two thousand four "
                 "hundred.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "times")
        self.play(FadeIn(steps[0][:2], shift=RIGHT * 0.1))
        self.at_word(n, "four")
        self.play(FadeIn(steps[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="rice_03",
            text="He has collected thirty times fifty, fifteen hundred, so he needs nine hundred from twenty kilograms: "
                 "forty-five rupees a kilogram.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "collected")
        self.play(FadeIn(steps[1][:2], shift=RIGHT * 0.1))
        self.at_word(n, "forty-five")
        self.play(FadeIn(steps[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S09_second_example")

    # ============================================ 10. EXAM PATTERNS ==========

    def exam_patterns(self):
        self.scene_start("S10_exam_patterns", title="Exam Patterns - How This Is Asked")

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
            text="A break-even price: one hundred items at ten rupees, sixty sold at twelve. One thousand minus seven hundred "
                 "and twenty, divided by forty, is seven rupees each.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "break-even")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "divided")
        self.play(FadeIn(rows[0][2:], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="patterns_03",
            text="A target profit price: eighty items at twenty rupees, fifty sold at twenty-five, twenty-five percent "
                 "overall. Two thousand minus twelve hundred and fifty, divided by thirty, is twenty-five rupees each.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "target")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "divided")
        self.play(FadeIn(rows[1][2:], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="patterns_04",
            text="A weighted percentage: one third at twenty-four percent profit and the rest at six percent loss is "
                 "twenty-four minus twelve, over three: four percent profit.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "weighted")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "over")
        self.play(FadeIn(rows[2][2:], shift=RIGHT * 0.2))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Exam patterns  ·  4 and 5 of 5")
        table, rows = self.pattern_table(head, PATTERNS_B)

        n = self.narrate(
            id="patterns_05",
            text="The required percentage on the rest: forty percent of the stock at ten percent profit, sixteen percent wanted "
                 "overall, so the rest must make twenty percent.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "required")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "must")
        self.play(FadeIn(rows[0][2:], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="patterns_06",
            text="Damaged stock: one hundred and twenty items at fifty rupees, twenty unsellable, twenty percent profit wanted. "
                 "Seven thousand two hundred divided by one hundred is seventy-two rupees each.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Damaged")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "divided")
        self.play(FadeIn(rows[1][2:], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S10_exam_patterns")

    # ================================ 11. TRAPS AND CONFUSING QUESTIONS ==========

    def traps(self):
        self.scene_start("S11_traps", title="Traps and Confusing Questions")

        head, q, wrong, right, rule = self.show_trap(TRAPS[0])

        n = self.narrate(
            id="trap1_01",
            text="Trap one: mirroring the percentage. Sixty shirts are sold at twenty percent profit; what loss percent on the "
                 "other forty breaks even?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "mirroring")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "Sixty")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="trap1_02",
            text="The wrong instinct is twenty percent. The correct answer is thirty percent: one hundred and fifty rupees on "
                 "each five hundred rupee shirt.",
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
            text="The rule: the gains on sixty items must be absorbed by only forty items.",
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
            text="Trap two: an unweighted average of percentages. One third of the goods at twenty-four percent profit, the "
                 "rest at six percent loss; what is the overall result?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "unweighted")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "third")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="trap2_02",
            text="The wrong instinct is twenty-four minus six, over two: nine percent. The correct answer is four percent.",
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
            text="The rule: weight each percentage by its share of the cost.",
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
            text="Trap three: damaged items left out of the cost. One hundred and twenty items at fifty rupees, twenty are "
                 "damaged; what price on the rest gives a twenty percent profit?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "damaged")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "fifty")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="trap3_02",
            text="The wrong instinct is fifty times one point two, sixty rupees. The correct answer is seventy-two rupees.",
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
            text="The rule: unsold or damaged items still count in the total cost.",
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
        given = VGroup(pill("half the goods (by cost):  30% profit", GOOD, size=LABEL), pill("the other half:  10% loss", BAD, size=LABEL))\
            .arrange(RIGHT, buff=0.5)
        hint = pill("overall % = ?", FOCUS, size=BODY)
        work = VGroup(text("equal cost shares: a simple average", LABEL, MUTED),
                      text(f"(30 − 10)/2  =  a {CP_ANSWER}% profit", BODY, GOOD, BOLD)).arrange(RIGHT, buff=0.6)
        self.stack(head, [given, hint, work], buff=0.8, top=0.9)
        self.no_overlap(*given)
        self.no_overlap(*work)

        n = self.narrate(
            id="check_01",
            text="Your turn. Half the goods, by cost, are sold at a thirty percent profit, and half at a ten percent loss. What "
                 "is the overall percent?",
            voice="default",
            subtitle=True,
            pause_after=10.0,
        )
        self.at_word(n, "turn")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "thirty")
        self.play(FadeIn(given[0], shift=UP * 0.1))
        self.at_word(n, "ten")
        self.play(FadeIn(given[1], shift=UP * 0.1))
        self.at_word(n, "overall")
        self.play(FadeIn(hint, shift=UP * 0.1))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="check_02",
            text="The cost shares are equal, so it is a simple average: thirty minus ten, over two, is a ten percent profit.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "equal")
        self.play(FadeIn(work[0], shift=UP * 0.1))
        self.at_word(n, "over")
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
            text="Level one, question one: one hundred items cost ten rupees each; sixty are sold at twelve rupees each; at "
                 "what price must the rest be sold to break even? Question two: half the goods are sold at a twenty-five "
                 "percent profit and half at a fifteen percent loss, each half with the same cost; find the overall result.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "items")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "half")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="practice_02",
            text="Level two, question three: a trader buys forty kilograms of rice at thirty rupees a kilogram, and sells "
                 "twenty-five kilograms at thirty-six rupees a kilogram; at what price per kilogram must he sell the remaining "
                 "fifteen kilograms, for a ten percent overall profit? Question four: one third of the goods, by cost, is sold "
                 "at a twenty-four percent profit, and the rest at a six percent loss; find the overall result. Question "
                 "five: eighty articles cost twenty rupees each; fifty are sold at twenty-five rupees each; at what price must "
                 "the rest be sold to gain twenty-five percent overall?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "rice")
        self.play(FadeIn(rows[2], shift=RIGHT * 0.2))
        self.at_word(n, "third")
        self.play(FadeIn(rows[3], shift=RIGHT * 0.2))
        self.at_word(n, "articles")
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
            text="Level three, question six: a trader sells forty percent of his stock, by cost, at a ten percent profit; at "
                 "what profit percent must he sell the rest, to make sixteen percent overall? Question seven: one hundred and "
                 "twenty items are bought at fifty rupees each; twenty are damaged and cannot be sold; at what price must "
                 "each remaining item be sold, to make a twenty percent profit overall? Question eight: three quarters of the "
                 "goods, by cost, are sold at a twenty percent profit, and the rest at cost price; find the overall profit "
                 "percent.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "stock")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "damaged")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.at_word(n, "quarters")
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
            text="One: the total cost is one thousand, seven hundred and twenty is collected, so two hundred and eighty is "
                 "needed from forty items: seven rupees each.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "collected")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "each")
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_02",
            text="Two: twenty-five minus fifteen, over two, is a five percent profit.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "minus")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "profit")
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_03",
            text="Three: the target is twelve hundred times one point one, thirteen hundred and twenty. Nine hundred is "
                 "collected, so four hundred and twenty is needed from fifteen kilograms: twenty-eight rupees a kilogram.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "target")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "twenty-eight")
        self.play(FadeIn(rows[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_04",
            text="Four: on a cost of three hundred, one hundred becomes one hundred and twenty-four, and two hundred becomes "
                 "one hundred and eighty-eight. The total is three hundred and twelve: a four percent profit.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "becomes", occurrence=1)
        self.play(FadeIn(rows[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "profit")
        self.play(FadeIn(rows[3][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_05",
            text="Five: the cost is sixteen hundred and the target is two thousand. Twelve hundred and fifty is collected, so "
                 "seven hundred and fifty is needed from thirty: twenty-five rupees each.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "target")
        self.play(FadeIn(rows[4][:2], shift=RIGHT * 0.2))
        self.at_word(n, "each")
        self.play(FadeIn(rows[4][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Answer key  ·  6 to 8", GOOD)
        table, rows = self.answer_table(head, ANSWERS_B, 6)

        n = self.narrate(
            id="answers_06",
            text="Six: zero point four times ten, plus zero point six x, equals sixteen, so zero point six x is twelve, and x "
                 "is twenty percent.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "equals")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "twenty")
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_07",
            text="Seven: the cost is six thousand, so the target is seven thousand two hundred from one hundred items: "
                 "seventy-two rupees each.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "target")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "seventy-two")
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_08",
            text="Eight: zero point seven five times twenty, plus zero point two five times zero, is a fifteen percent profit.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "times", occurrence=1)
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "fifteen")
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
            text="Recognise and move. The recognition cue: the rest, remaining, to break even, or overall, means totals in "
                 "rupees.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Recognise")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "cue")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "totals")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="lens_02",
            text="The target time: sixty seconds.",
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
            text="The sanity check: the overall percent always lies between the smallest and the largest part percent.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "sanity")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "between")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S15_exam_lens")

    # ==================================== 16. QUICK REVISION + SUMMARY ==========

    def summary(self):
        self.scene_start("S16_summary", title="Quick Revision and Summary")

        head = self.heading("Quick revision")
        totals = pill("work in rupee totals: total cost is the target line", WORD, size=LABEL)
        box = VGroup(text("price for the rest  =  (Total CP × (1 + P/100) − sales so far) ÷ items left", LABEL, INK, BOLD),
                     text("overall %  =  Σ (cost share × part %)", LABEL, INK, BOLD)).arrange(DOWN, buff=0.4, aligned_edge=LEFT)
        nxt = self.breadcrumb("Next", "Video 8 · Speed Tricks for Profit & Loss")
        self.stack(head, [totals, box, nxt], buff=0.8, top=0.8)
        self.no_overlap(*box)

        n = self.narrate(
            id="summary_01",
            text="Work in rupee totals: total cost is the target line, and the unsold stock must make up the gap.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "totals")
        self.play(FadeIn(totals, shift=UP * 0.1))
        self.at_word(n, "gap")
        self.play(FadeIn(box[0], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_02",
            text="Percentages average only when weighted by cost.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "weighted")
        self.play(FadeIn(box[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_03",
            text="Next: speed tricks for profit and loss.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Next")
        self.play(FadeIn(nxt, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S16_summary")

"""
animation.py for the LMS video generator.

Course : Pre-C-CAT - Section A - Quantitative Aptitude
Video  : Lesson 12 - Profit & Loss - 03 - Discount - Single & Successive

Source script:
  C:\\Scripts\\Section A\\Module_2_Section_A_Quantitative_Aptitude_Part_1\\Aptitude_Scripts\\Sessions 1-4 - Interest, Profit & Loss, Time & Work\\Lesson 12 - Profit & Loss\\03 - Discount - Single & Successive.pdf

Built on the golden-reference pattern:
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``;
  * layouts stacked with next_to and guarded with ``no_overlap``; nothing is
    ever animated onto or into another box.

Lesson 12, Video 3 of 8. Not the first video of the lesson: a silent breadcrumb, a one-line recap of Video 2, then today's topic. No spoken course welcome.
The narration follows the script section by section, with numbers written as words for the voice and CP / SP / MP spoken as "cost price", "selling price" and "marked price". Tables and lists are spoken one row at a time; the exam patterns, practice questions and answers are split over two screens each. Every percentage on screen is computed from the question's numbers and asserted.
Pauses: 10 s on the hook ("work out what you would pay"), the script's 10-second countdown at the checkpoint, 12 s after each practice screen.
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
    return f"₹{round(x):,}"


def retain(*discounts):
    """Retention multiplier after successive discounts: the fraction of MP still paid."""
    out = Fraction(1)
    for d in discounts:
        out *= 1 - Fraction(d) / 100
    return out


def net_discount(*discounts):
    """Single discount (in percent) equal to the successive discounts."""
    return (1 - retain(*discounts)) * 100


def two_discounts(a, b):
    """a + b − ab/100."""
    return Fraction(a) + Fraction(b) - Fraction(a) * Fraction(b) / 100


def free_offer(buy, free):
    """Buy x, get y free: discount = y/(x + y), in percent."""
    return Fraction(free, buy + free) * 100


assert all(two_discounts(a, b) == net_discount(a, b) for a, b in [(20, 10), (30, 20), (15, 10), (25, 20)])

# ---- the hook: the banner ----
TAG = 2000
AFTER_1, AFTER_2 = TAG * retain(20), TAG * retain(20, 10)
FLAT_30 = TAG * retain(30)
assert (AFTER_1, AFTER_2, FLAT_30, AFTER_2 - FLAT_30, net_discount(20, 10)) == (1600, 1440, 1400, 40, 28)
assert retain(20, 10) == retain(10, 20) == Fraction("0.72") and free_offer(3, 1) == 25

# ---- second worked example ----
EX_RETAIN = retain(30, 20)
EX_SP = 5000 * EX_RETAIN
assert (EX_RETAIN, EX_SP, net_discount(30, 20)) == (Fraction("0.56"), 2800, 44)

# ---- exam patterns (answers computed) ----
P1 = 2000 * retain(15)
P3 = net_discount(20, 10, 5)
P4 = 1026 / retain(10, 5)
P5 = (1 - Fraction("0.72") / Fraction("0.8")) * 100
assert (P1, net_discount(20, 25), retain(20, 10, 5), P3, P4, P5, free_offer(4, 1)) == (1700, 40, Fraction("0.684"), Fraction("31.6"), 1200, 10, 20)
PATTERNS_A = [("Single discount", "₹2,000 fan at 15% off", "× 0.85", rs(P1)),
              ("Net of two", "20% and 25%", "20 + 25 − 5", "40%"),
              ("Net of three", "20%, 10% and 5%", "0.8 × 0.9 × 0.95 = 0.684", f"{dec(P3)}%")]
PATTERNS_B = [("MP from SP", "₹1,026 after 10% and 5%", "1,026 ÷ 0.855", rs(P4)),
              ("Missing discount", "First 20%, net 28%; second?", "0.72 ÷ 0.8 = 0.9", f"{P5}%"),
              ("Free items", "Buy 4, get 1 free", "1/(4 + 1)", f"{free_offer(4, 1)}%")]

# ---- traps: (title, question, wrong, right, rule) ----
assert (1000 * retain(25), 1400 * retain(25)) == (750, 1050)
TRAPS = [("Trap 1  ·  adding successive discounts", "20% then 10% off.  Net discount?",
          "20 + 10  =  30%", f"0.8 × 0.9 = 0.72  →  {net_discount(20, 10)}%",
          "“And then”, “extra”, “further”:  multiply the retention multipliers."),
         ("Trap 2  ·  free items divided by the paid quantity", "“Buy 3, get 1 free.”  Discount %?",
          "1/3  =  33 1/3 %", f"1/4  =  {free_offer(3, 1)}%",
          "The discount is the free value over the total value received."),
         ("Trap 3  ·  discount taken on CP", "CP ₹1,000, MP ₹1,400, 25% discount.  SP?",
          f"1,000 × 0.75  =  {rs(1000 * retain(25))}", f"1,400 × 0.75  =  {rs(1400 * retain(25))}",
          "A discount never touches CP directly.")]

# ---- practice (answers computed) ----
PRACTICE_A = [("L1", "Find the single discount equal to successive discounts of 10% and 10%."),
              ("L1", "A fan marked ₹2,000 is sold at a 15% discount.  Find the selling price."),
              ("L1", "Find the single discount equal to successive discounts of 15% and 10%."),
              ("L2", "An article marked ₹2,500 is sold with successive discounts of 20% and 10%.  Find the selling price."),
              ("L2", "Find the single discount equal to successive discounts of 25% and 20%."),
              ("L2", "An article marked ₹1,200 is sold with successive discounts of 10% and 5%.  Find the selling price.")]
PRACTICE_B = [("L3", "A store offers “buy 4, get 1 free”.  What discount % is this?"),
              ("L3", "An item marked ₹800 sells for ₹576 after two successive discounts, the first of which is 20%.  "
                     "Find the second."),
              ("L3", "Which is the better deal: three successive discounts of 10%, or a single discount of 27%?")]
A4, A6 = 2500 * retain(20, 10), 1200 * retain(10, 5)
A8 = (1 - Fraction(576, 800) / retain(20)) * 100
A9 = net_discount(10, 10, 10)
assert (net_discount(10, 10), net_discount(15, 10), A4, net_discount(25, 20), A6, A8, A9) == (19, Fraction("23.5"), 1800, 40, 1026, 10, Fraction("27.1"))
assert A9 > 27
ANSWERS_A = [("10 + 10 − 1", f"{net_discount(10, 10)}%"),
             ("2,000 × 0.85", rs(P1)),
             ("15 + 10 − 1.5", f"{dec(net_discount(15, 10))}%"),
             ("2,500 × 0.72", rs(A4)),
             ("0.75 × 0.8 = 0.6", f"{net_discount(25, 20)}%")]
ANSWERS_B = [("1,200 × 0.9 × 0.95", rs(A6)),
             ("pay for 4, receive 5:   1/5", f"{free_offer(4, 1)}%"),
             ("576 ÷ 800 = 0.72;   0.72 ÷ 0.8 = 0.9", f"{A8}%"),
             (f"0.9³ = 0.729:  a {dec(A9)}% discount", "three 10% discounts")]

OBJECTIVES = [("Find the price after a single discount", "on the marked price"),
              ("Find the net discount", "after two or more successive discounts"),
              ("Convert free-item offers", "“buy x, get y free” as a discount percentage")]
LENS = [("Recognition cue", "two or more discounts in one sentence  →  retention multipliers"),
        ("Target time", "20 seconds"),
        ("Sanity check", "net discount: less than the sum of the discounts, more than the largest single one")]
FORMULAS = ["SP = MP × (100 − d)/100              (d is on MP)",
            "Two successive discounts a%, b%:      net = a + b − ab/100",
            "Any number of discounts:      multiply the retention multipliers",
            "Buy x, get y free:      discount = y/(x + y)"]


def labelled_bar(parts, unit, label_above=False):
    """A bar made of labelled segments: parts = [(percent, label, colour, opacity), ...]."""
    cols = []
    for pct, label, color, opacity in parts:
        rect = Rectangle(width=pct * unit, height=0.5, color=color, fill_color=color, fill_opacity=opacity)
        tag = text(label, SMALL, color, BOLD)
        cols.append(VGroup(tag, rect).arrange(DOWN, buff=0.12) if label_above else VGroup(rect, tag).arrange(DOWN, buff=0.12))
    return VGroup(*cols).arrange(RIGHT, buff=0, aligned_edge=DOWN if label_above else UP)


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


class DiscountSingleAndSuccessiveVideo(LMSScene):
    lesson_title = "Discount: Single & Successive"

    def construct(self):
        self.camera.background_color = BG

        self.intro()
        self.hook()
        self.objectives()
        self.why_this_matters()
        self.on_marked_price()
        self.retention_multiplies()
        self.free_items()
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
    # Not the first video: silent breadcrumb, a one-line recap of Video 2, then today's topic.

    def intro(self):
        self.scene_start("S00_intro", title="Intro")

        crumb = self.breadcrumb("Quantitative Aptitude", "Lesson 12 · Profit & Loss", "Video 3 of 8")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        recap = VGroup(text("last video", SMALL, MUTED), pill("SP → CP:  divide by the multiplier", WORD, size=LABEL))\
            .arrange(DOWN, buff=0.25)
        title = text("Discount: Single & Successive", TITLE, INK, BOLD)
        today = text("today: discounts on the marked price, single and stacked", LABEL, FOCUS)
        block = VGroup(recap, title, today).arrange(DOWN, buff=0.7)
        fit_within(block, SAFE_W, SAFE_H - crumb.height - 0.9)
        block.next_to(crumb, DOWN, buff=0.7)
        self.no_overlap(crumb, recap, title, today)
        self.validator.check_in_frame(VGroup(crumb, block))

        n = self.narrate(
            id="intro_01",
            text="In the last video, you went backwards from selling price to cost price by dividing by the multiplier.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.at_word(n, "dividing")
        self.play(FadeIn(recap, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="intro_02",
            text="Today: discounts, single and stacked.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "discounts")
        self.play(FadeIn(title, shift=UP * 0.1))
        self.at_word(n, "stacked")
        self.play(FadeIn(today, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_intro")

    # =================================================== 1. HOOK ==========

    def hook(self):
        self.scene_start("S01_hook", title="Hook")

        head = self.heading("A store banner")
        lines = VGroup(text("20% off  +  extra 10% off at billing", BODY, INK, BOLD), text("=  FLAT 30% OFF!", TITLE, FOCUS, BOLD))\
            .arrange(DOWN, buff=0.3)
        banner = self.card(lines, width=9.6, color=FOCUS, pad=0.45)
        tag = pill(f"noise-cancelling headphones  ·  tag {rs(TAG)}", WORD, size=LABEL)
        really = pill("is it really 30% off?", BAD, size=LABEL)
        compare = text("work out what you pay, and compare with a genuine 30% off", LABEL, MUTED)
        goal = text("goal: see through any stacked offer in five seconds", SMALL, GOOD, BOLD)
        self.stack(head, [banner, tag, really, compare, goal], buff=0.4, top=0.45)

        n = self.narrate(
            id="hook_01",
            text="A store's banner reads: twenty percent off, plus an extra ten percent off at billing. That's a flat thirty "
                 "percent off!",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "banner")
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(banner[0]))
        self.at_word(n, "twenty")
        self.play(FadeIn(lines[0], shift=UP * 0.1))
        self.at_word(n, "flat")
        self.play(FadeIn(lines[1], scale=1.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_02",
            text="The tag on the noise-cancelling headphones says two thousand rupees.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "tag")
        self.play(FadeIn(tag, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_03",
            text="Is it really thirty percent off? Work out what you'd pay, and compare it with a genuine thirty percent off.",
            voice="default",
            subtitle=True,
            pause_after=10.0,
        )
        self.at_word(n, "really")
        self.play(FadeIn(really, shift=UP * 0.1))
        self.at_word(n, "compare")
        self.play(FadeIn(compare, shift=UP * 0.1))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="hook_04",
            text="By the end of this video you'll see through any stacked offer in five seconds.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "five")
        self.play(FadeIn(goal, shift=UP * 0.1))
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
            text="First, calculate the selling price after a single discount on the marked price.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "calculate")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "marked")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="obj_03",
            text="Second, find the net discount after two or more successive discounts.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "net")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "successive")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="obj_04",
            text="Third, convert buy x, get y free offers into a discount percentage.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "convert")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "percentage")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_objectives")

    # ========================================== 3. WHY THIS MATTERS ==========

    def why_this_matters(self):
        self.scene_start("S03_why_this_matters", title="Why This Matters")

        head = self.heading("Why this matters")
        stores = pill("stores advertise stacked offers constantly", WORD, size=LABEL)
        add = pill("exams test whether you know they don't simply add", BAD, size=LABEL)
        idea = pill("the multiplier idea from Lesson 11, in a new costume", GOOD, size=LABEL)
        self.stack(head, [stores, add, idea], buff=0.8, top=0.9)

        n = self.narrate(
            id="why_01",
            text="Stores advertise stacked offers constantly, and exams test whether you know they don't simply add.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "constantly")
        self.play(FadeIn(stores, shift=UP * 0.1))
        self.at_word(n, "add")
        self.play(FadeIn(add, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="why_02",
            text="It is also the multiplier idea from lesson eleven, in a new costume.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "multiplier")
        self.play(FadeIn(idea, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_why_this_matters")

    # ================================ 4. CONCEPT: ON THE MARKED PRICE ==========

    def on_marked_price(self):
        self.scene_start("S04_on_marked_price", title="Concept - Discount Is on the Marked Price; Think in What You Pay")

        head = self.heading("Discount is always on the marked price")
        formula = pill("SP  =  MP × (1 − d/100)", GOOD, size=BODY)
        think = text("think in what you still pay", LABEL, RATIO, BOLD)
        bar = labelled_bar([(80, "you pay 80%", GOOD, 0.45), (20, "20% off", BAD, 0.45)], 0.08)
        keep = pill("a 20% discount:  retention multiplier = 0.8", FOCUS, size=LABEL)
        self.stack(head, [formula, think, bar, keep], buff=0.6, top=0.7)
        self.no_overlap(*[part[1] for part in bar])          # the segments touch by design; the labels must not

        n = self.narrate(
            id="marked_01",
            text="Discount is always on the marked price. Selling price is marked price times one minus d over a hundred.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "always")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "times")
        self.play(FadeIn(formula, scale=1.05))
        self.wait_for_narration(n)

        n = self.narrate(
            id="marked_02",
            text="Think in what you still pay. A twenty percent discount means you pay eighty percent: the retention "
                 "multiplier is zero point eight.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "still")
        self.play(FadeIn(think, shift=UP * 0.1))
        self.at_word(n, "eighty")
        self.play(FadeIn(bar[1], shift=LEFT * 0.1), FadeIn(bar[0], shift=RIGHT * 0.1))
        self.at_word(n, "retention")
        self.play(FadeIn(keep, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_on_marked_price")

    # ================================ 5. CONCEPT: RETENTION MULTIPLIERS MULTIPLY ==========

    def retention_multiplies(self):
        self.scene_start("S05_retention_multiplies", title="Concept - The Second Discount Acts on the Reduced Price")

        head = self.heading("The second discount acts on the reduced price")
        product = text(f"retention multipliers multiply:   0.8 × 0.9  =  {dec(retain(20, 10))}", LABEL, INK, BOLD)
        result = VGroup(pill("you pay 72%", GOOD, size=LABEL), pill(f"net discount {net_discount(20, 10)}%", FOCUS, size=LABEL))\
            .arrange(RIGHT, buff=0.5)
        one_line = VGroup(pill("a + b − ab/100", GOOD, size=BODY), text(f"20 + 10 − 2  =  {two_discounts(20, 10)}%", LABEL, INK, BOLD))\
            .arrange(RIGHT, buff=0.6)
        bite = text("the − ab/100 is the second discount's “missing” bite on the first", SMALL, MUTED)
        order = text("order doesn't matter:   0.8 × 0.9  =  0.9 × 0.8", LABEL, RATIO, BOLD)
        self.stack(head, [product, result, one_line, bite, order], buff=0.5, top=0.6)
        self.no_overlap(*result)
        self.no_overlap(*one_line)

        n = self.narrate(
            id="retain_01",
            text="The second discount acts on the reduced price. So retention multipliers multiply: zero point eight times "
                 "zero point nine is zero point seven two.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "reduced")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "times")
        self.play(FadeIn(product, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="retain_02",
            text="You pay seventy-two percent, a net discount of twenty-eight percent.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "seventy-two")
        self.play(FadeIn(result[0], shift=UP * 0.1))
        self.at_word(n, "twenty-eight")
        self.play(FadeIn(result[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="retain_03",
            text="A one-line formula for two discounts: a plus b minus a b over a hundred. Twenty plus ten minus two is "
                 "twenty-eight percent.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "formula")
        self.play(FadeIn(one_line[0], scale=1.05))
        self.at_word(n, "Twenty")
        self.play(FadeIn(one_line[1], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="retain_04",
            text="The minus a b over a hundred is the second discount's missing bite on the first discount.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "missing")
        self.play(FadeIn(bite, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="retain_05",
            text="Order doesn't matter: twenty then ten equals ten then twenty.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Order")
        self.play(FadeIn(order, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_retention_multiplies")

    # ==================================== 6. CONCEPT: FREE ITEMS ==========

    def free_items(self):
        self.scene_start("S06_free_items", title="Concept - Free Items Are Discounts")

        head = self.heading("Free items are discounts")
        offer = text("“Buy 3, get 1 free”", BODY, INK, BOLD)
        paid = VGroup(*[Square(side_length=0.8, color=WORD, fill_color=WORD, fill_opacity=0.45) for _ in range(3)]).arrange(RIGHT, buff=0.15)
        free = Square(side_length=0.8, color=GOOD, fill_color=GOOD, fill_opacity=0.7)
        items = VGroup(VGroup(paid, text("pay for 3", SMALL, WORD, BOLD)).arrange(DOWN, buff=0.15),
                       VGroup(free, text("1 free", SMALL, GOOD, BOLD)).arrange(DOWN, buff=0.15)).arrange(RIGHT, buff=0.4, aligned_edge=UP)
        quarter = pill(f"receive 4:   discount = 1/4 = {free_offer(3, 1)}%", FOCUS, size=BODY)
        general = pill("buy x, get y free:   discount = y / (x + y)", GOOD, size=LABEL)
        self.stack(head, [offer, items, quarter, general], buff=0.55, top=0.7)
        self.no_overlap(*items)

        n = self.narrate(
            id="free_01",
            text="Free items are discounts. Buy three, get one free means you pay for three and receive four: a discount of "
                 "one fourth, twenty-five percent.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Free")
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(offer, shift=UP * 0.1))
        self.at_word(n, "pay")
        self.play(FadeIn(items[0], shift=UP * 0.1))
        self.at_word(n, "receive")
        self.play(FadeIn(items[1], shift=UP * 0.1))
        self.at_word(n, "fourth")
        self.play(FadeIn(quarter, scale=1.05))
        self.wait_for_narration(n)

        n = self.narrate(
            id="free_02",
            text="In general, buy x and get y free is a discount of y over x plus y.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "over")
        self.play(FadeIn(general, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_free_items")

    # ============================================== 7. FORMULA BOX ==========

    def formula_box(self):
        self.scene_start("S07_formula_box", title="Formula Box")

        head = self.heading("Formula box", GOOD)
        lines = VGroup(*[text(f, LABEL, INK) for f in FORMULAS]).arrange(DOWN, buff=0.5, aligned_edge=LEFT)
        box = self.card(lines, width=SAFE_W - 1.0, color=GOOD, pad=0.5)
        self.stack(head, [box], top=0.8)

        n = self.narrate(
            id="formula_01",
            text="Here is the formula box. Selling price is marked price times one hundred minus d, over a hundred.",
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
            text="Two successive discounts net to a plus b minus a b over a hundred.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "net")
        self.play(FadeIn(lines[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_03",
            text="For any number of discounts, multiply the retention multipliers.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "multiply")
        self.play(FadeIn(lines[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_04",
            text="And buy x, get y free is a discount of y over x plus y.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "free")
        self.play(FadeIn(lines[3], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S07_formula_box")

    # ============================================== 8. THE ANALOGY ==========

    def analogy(self):
        self.scene_start("S08_analogy", title="The Analogy - Cutting a Cake")

        head = self.heading("Think of cutting a cake")
        second_cut = Fraction(80 * 10, 100)
        cake = labelled_bar([(20, "20%", BAD, 0.5), (int(second_cut), f"{second_cut}%", FOCUS, 0.9),
                             (100 - 20 - int(second_cut), "72% left", WORD, 0.4)], 0.085, label_above=True)
        whole = text("first cut: 20% of the whole cake", LABEL, BAD, BOLD)
        left = text(f"second cut: 10% of what is left  =  {second_cut}% of the whole", LABEL, FOCUS, BOLD)
        less = pill(f"together the cuts remove {20 + second_cut}%: less than 30%", GOOD, size=LABEL)
        stops = VGroup(text("Where the analogy stops", LABEL, BAD, BOLD),
                       text("with a cake you can see the pieces", LABEL, MUTED),
                       text("with prices, multiply the retention multipliers", LABEL, INK)).arrange(DOWN, buff=0.2)
        self.stack(head, [cake, whole, left, less, stops], buff=0.42, top=0.5)
        self.no_overlap(*[part[0] for part in cake])         # the segments touch by design; the labels must not

        n = self.narrate(
            id="analogy_01",
            text="Think of cutting a cake. The first cut removes twenty percent of the whole cake.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "cake")
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(cake[2], shift=UP * 0.1))
        self.at_word(n, "first")
        self.play(FadeIn(cake[0], shift=UP * 0.1), FadeIn(whole, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_02",
            text="The second removes ten percent of what is left, not of the whole.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "second")
        self.play(FadeIn(cake[1], shift=UP * 0.1))
        self.at_word(n, "not")
        self.play(FadeIn(left, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_03",
            text="A slice of a smaller piece is smaller, so together the cuts remove less than thirty percent.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "less")
        self.play(FadeIn(less, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_04",
            text="Where the analogy stops: with a cake you can see the pieces.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "stops")
        self.play(FadeIn(stops[0], shift=UP * 0.1))
        self.at_word(n, "see")
        self.play(FadeIn(stops[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_05",
            text="With prices, the only reliable way to see them is to multiply the retention multipliers.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "multiply")
        self.play(FadeIn(stops[2], shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S08_analogy")

    # ================================ 9. WORKED EXAMPLE: CLOSING THE HOOK ==========

    def hook_solved(self):
        self.scene_start("S09_hook_solved", title="Worked Example - Closing the Hook")

        head = self.heading(f"The banner:  tag {rs(TAG)}")
        steps = self.solve_steps([("20% off ₹2,000:   2,000 × 0.8", f"=  {rs(AFTER_1)}"),
                                  ("then 10% off ₹1,600:   1,600 × 0.9", f"=  {rs(AFTER_2)}"),
                                  ("a true 30% off:   2,000 × 0.7", f"=  {rs(FLAT_30)}")])
        verdict = pill(f"the banner overstates the deal by {rs(AFTER_2 - FLAT_30)}:  the real net discount is {net_discount(20, 10)}%",
                       FOCUS, size=LABEL)
        self.stack(head, [steps, verdict], buff=0.8, top=0.8)
        self.no_overlap(*steps)

        n = self.narrate(
            id="solved_01",
            text="Twenty percent off two thousand leaves sixteen hundred.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "off")
        self.play(FadeIn(steps[0][:2], shift=RIGHT * 0.1))
        self.at_word(n, "sixteen")
        self.play(FadeIn(steps[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_02",
            text="Then ten percent off sixteen hundred leaves fourteen hundred and forty.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Then")
        self.play(FadeIn(steps[1][:2], shift=RIGHT * 0.1))
        self.at_word(n, "fourteen")
        self.play(FadeIn(steps[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_03",
            text="A true thirty percent off would be fourteen hundred.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "true")
        self.play(FadeIn(steps[2][:2], shift=RIGHT * 0.1))
        self.at_word(n, "fourteen")
        self.play(FadeIn(steps[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_04",
            text="The banner overstates the deal by forty rupees: the real net discount is twenty-eight percent.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "overstates")
        self.play(FadeIn(verdict, shift=UP * 0.1))
        self.at_word(n, "twenty-eight")
        self.play(Indicate(verdict, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S09_hook_solved")

    # ====================== 10. SECOND WORKED EXAMPLE ==========

    def second_example(self):
        self.scene_start("S10_second_example", title="A Second Worked Example - Successive Discounts")

        head = self.heading("Successive discounts of 30% and 20%")
        given = VGroup(pill("MP ₹5,000", WORD, size=LABEL), pill("30% off, then 20% off", RATIO, size=LABEL),
                       pill("SP and single discount = ?", FOCUS, size=LABEL)).arrange(RIGHT, buff=0.4)
        steps = self.solve_steps([("retention:   0.7 × 0.8", f"=  {dec(EX_RETAIN)}"),
                                  ("SP  =  5,000 × 0.56", f"=  {rs(EX_SP)}"),
                                  ("single discount  =  100 − 56", f"=  {net_discount(30, 20)}%    (not 50%)")])
        self.stack(head, [given, steps], buff=0.8, top=0.8)
        self.no_overlap(*given)
        self.no_overlap(*steps)

        n = self.narrate(
            id="second_01",
            text="An article marked five thousand rupees has successive discounts of thirty percent and twenty percent. Find "
                 "the selling price and the single equivalent discount.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "five")
        self.play(FadeIn(given[0], shift=UP * 0.1))
        self.at_word(n, "thirty")
        self.play(FadeIn(given[1], shift=UP * 0.1))
        self.at_word(n, "Find")
        self.play(FadeIn(given[2], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_02",
            text="Retention: zero point seven times zero point eight is zero point five six.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "times")
        self.play(FadeIn(steps[0][:2], shift=RIGHT * 0.1))
        self.at_word(n, "six")
        self.play(FadeIn(steps[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_03",
            text="Selling price is five thousand times zero point five six: two thousand eight hundred rupees.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "times")
        self.play(FadeIn(steps[1][:2], shift=RIGHT * 0.1))
        self.at_word(n, "eight")
        self.play(FadeIn(steps[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_04",
            text="The single discount is one hundred minus fifty-six: forty-four percent, not fifty.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "minus")
        self.play(FadeIn(steps[2][:2], shift=RIGHT * 0.1))
        self.at_word(n, "forty-four")
        self.play(FadeIn(steps[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S10_second_example")

    # ============================================ 11. EXAM PATTERNS ==========

    def exam_patterns(self):
        self.scene_start("S11_exam_patterns", title="Exam Patterns - How This Is Asked")

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
            text="A single discount: a two thousand rupee fan at fifteen percent off is times zero point eight five, seventeen "
                 "hundred.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "single")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "times")
        self.play(FadeIn(rows[0][2:], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="patterns_03",
            text="The net of two: twenty percent and twenty-five percent is twenty plus twenty-five minus five, forty percent.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "net")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "minus")
        self.play(FadeIn(rows[1][2:], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="patterns_04",
            text="The net of three: twenty, ten and five percent multiply to zero point six eight four, a thirty-one point six "
                 "percent discount.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "three")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "multiply")
        self.play(FadeIn(rows[2][2:], shift=RIGHT * 0.2))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Exam patterns  ·  4 to 6 of 6")
        table, rows = self.pattern_table(head, PATTERNS_B)

        n = self.narrate(
            id="patterns_05",
            text="Marked price from selling price: one thousand and twenty-six after ten percent and five percent, divided by "
                 "zero point eight five five, is twelve hundred.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "Marked")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "divided")
        self.play(FadeIn(rows[0][2:], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="patterns_06",
            text="A missing discount: the first is twenty percent and the net is twenty-eight, so zero point seven two divided "
                 "by zero point eight is zero point nine: the second is ten percent.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "missing")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "divided")
        self.play(FadeIn(rows[1][2:], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="patterns_07",
            text="Free items: buy four, get one free is one over five, twenty percent.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Free")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "over")
        self.play(FadeIn(rows[2][2:], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S11_exam_patterns")

    # ================================ 12. TRAPS AND CONFUSING QUESTIONS ==========

    def traps(self):
        self.scene_start("S12_traps", title="Traps and Confusing Questions")

        head, q, wrong, right, rule = self.show_trap(TRAPS[0])

        n = self.narrate(
            id="trap1_01",
            text="Trap one: adding successive discounts. Twenty percent, then ten percent off; what is the net discount?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "adding")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "Twenty")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="trap1_02",
            text="The wrong instinct is thirty percent. The correct answer is twenty-eight percent.",
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
            text="The rule: and then, extra, or further, means multiply the retention multipliers.",
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
            text="Trap two: free items divided by the paid quantity. Buy three, get one free; what is the discount percent?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "paid")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "Buy")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="trap2_02",
            text="The wrong instinct is one third, thirty-three and a third percent. The correct answer is one fourth, "
                 "twenty-five percent.",
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
            text="The rule: the discount is the free value over the total value received.",
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
            text="Trap three: the discount taken on cost price. Cost price one thousand, marked price fourteen hundred, "
                 "twenty-five percent discount; find the selling price.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "taken")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "marked")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="trap3_02",
            text="The wrong instinct is one thousand times zero point seven five, seven hundred and fifty. Correctly, fourteen "
                 "hundred times zero point seven five is one thousand and fifty.",
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
            text="The rule: a discount never touches cost price directly.",
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
        given = VGroup(pill("30% off", WORD, size=BODY), text("then", LABEL, MUTED), pill("20% off", RATIO, size=BODY)).arrange(RIGHT, buff=0.4)
        hint = pill("single equivalent discount = ?", FOCUS, size=LABEL)
        work = VGroup(text(f"0.7 × 0.8  =  {dec(EX_RETAIN)}", LABEL, INK), text(f"→   {net_discount(30, 20)}%", LABEL, GOOD, BOLD))\
            .arrange(RIGHT, buff=0.5)
        check = text(f"check:   30 + 20 − 6  =  {two_discounts(30, 20)}", LABEL, MUTED)
        self.stack(head, [given, hint, work, check], buff=0.6, top=0.8)
        self.no_overlap(*given)
        self.no_overlap(*work)

        n = self.narrate(
            id="check_01",
            text="Your turn. What single discount equals successive discounts of thirty percent and twenty percent?",
            voice="default",
            subtitle=True,
            pause_after=10.0,
        )
        self.at_word(n, "turn")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "single")
        self.play(FadeIn(hint, shift=UP * 0.1))
        self.at_word(n, "thirty")
        self.play(FadeIn(given[0], shift=UP * 0.1))
        self.at_word(n, "twenty")
        self.play(FadeIn(given[1:], shift=UP * 0.1))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="check_02",
            text="Zero point seven times zero point eight is zero point five six, so forty-four percent.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "times")
        self.play(FadeIn(work[0], shift=UP * 0.1))
        self.at_word(n, "forty-four")
        self.play(FadeIn(work[1], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="check_03",
            text="Check: thirty plus twenty minus six is forty-four.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Check")
        self.play(FadeIn(check, shift=UP * 0.1))
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
            text="Level one, question one: find the single discount equal to successive discounts of ten percent and ten "
                 "percent. Question two: a fan marked two thousand rupees is sold at a fifteen percent discount; find the "
                 "selling price. Question three: find the single discount equal to successive discounts of fifteen percent "
                 "and ten percent.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "single", occurrence=1)
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "fan")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.at_word(n, "three")
        self.play(FadeIn(rows[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="practice_02",
            text="Level two, question four: an article marked two thousand five hundred rupees is sold with successive "
                 "discounts of twenty percent and ten percent; find the selling price. Question five: find the single "
                 "discount equal to successive discounts of twenty-five percent and twenty percent. Question six: an article "
                 "marked twelve hundred rupees is sold with successive discounts of ten percent and five percent; find the "
                 "selling price.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "marked", occurrence=1)
        self.play(FadeIn(rows[3], shift=RIGHT * 0.2))
        self.at_word(n, "single")
        self.play(FadeIn(rows[4], shift=RIGHT * 0.2))
        self.at_word(n, "twelve")
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
            text="Level three, question seven: a store offers buy four, get one free; what discount percent is this? Question "
                 "eight: an item marked eight hundred rupees sells for five hundred and seventy-six after two successive "
                 "discounts, the first of which is twenty percent; find the second. Question nine: which is the better deal: "
                 "three successive discounts of ten percent, or a single discount of twenty-seven percent?",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "store")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "item")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.at_word(n, "better")
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
            text="One: ten plus ten minus one is nineteen percent.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "minus")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "nineteen")
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_02",
            text="Two: two thousand times zero point eight five is seventeen hundred rupees.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "times")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "seventeen")
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_03",
            text="Three: fifteen plus ten minus one point five is twenty-three point five percent.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "minus")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "twenty-three")
        self.play(FadeIn(rows[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_04",
            text="Four: two thousand five hundred times zero point seven two is eighteen hundred rupees.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "times")
        self.play(FadeIn(rows[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "eighteen")
        self.play(FadeIn(rows[3][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_05",
            text="Five: zero point seven five times zero point eight is zero point six, so forty percent.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "times")
        self.play(FadeIn(rows[4][:2], shift=RIGHT * 0.2))
        self.at_word(n, "forty")
        self.play(FadeIn(rows[4][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Answer key  ·  6 to 9", GOOD)
        table, rows = self.answer_table(head, ANSWERS_B, 6)

        n = self.narrate(
            id="answers_06",
            text="Six: twelve hundred times zero point nine times zero point nine five is one thousand and twenty-six rupees.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "times", occurrence=1)
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "twenty-six")
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_07",
            text="Seven: you pay for four and receive five, so one fifth, twenty percent.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "receive")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "twenty")
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_08",
            text="Eight: five hundred and seventy-six over eight hundred is zero point seven two, and zero point seven two "
                 "divided by zero point eight is zero point nine, so the second discount is ten percent.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "divided")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "ten")
        self.play(FadeIn(rows[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_09",
            text="Nine: zero point nine cubed is zero point seven two nine, a twenty-seven point one percent discount, so the "
                 "three ten percent discounts are very slightly better.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "cubed")
        self.play(FadeIn(rows[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "better")
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
            text="Recognise and move. The recognition cue: two or more discounts in one sentence means retention multipliers.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Recognise")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "cue")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "retention")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="lens_02",
            text="The target time: twenty seconds.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "target")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "twenty")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="lens_03",
            text="The sanity check: the net discount is always less than the sum of the discounts, and more than the largest "
                 "single one.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "sanity")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "less")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S16_exam_lens")

    # ==================================== 17. QUICK REVISION + SUMMARY ==========

    def summary(self):
        self.scene_start("S17_summary", title="Quick Revision and Summary")

        head = self.heading("Quick revision")
        on_mp = pill("discount is on the marked price", WORD, size=LABEL)
        box = VGroup(text("successive discounts: multiply the retention multipliers", LABEL, INK),
                     text("net of a% and b%   =   a + b − ab/100", LABEL, INK, BOLD),
                     text("buy x, get y free   =   y/(x + y)", LABEL, INK, BOLD)).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        nxt = self.breadcrumb("Next", "Video 4 · Marked Price Problems")
        self.stack(head, [on_mp, box, nxt], buff=0.75, top=0.8)
        self.no_overlap(*box)

        n = self.narrate(
            id="summary_01",
            text="Discount is on the marked price.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "marked")
        self.play(FadeIn(on_mp, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_02",
            text="Successive discounts multiply as retention multipliers, giving a plus b minus a b over a hundred for two.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "multiply")
        self.play(FadeIn(box[0], shift=RIGHT * 0.2))
        self.at_word(n, "minus")
        self.play(FadeIn(box[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_03",
            text="Free-item offers are discounts of y over x plus y.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "over")
        self.play(FadeIn(box[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_04",
            text="Next: marked price problems.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Next")
        self.play(FadeIn(nxt, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S17_summary")

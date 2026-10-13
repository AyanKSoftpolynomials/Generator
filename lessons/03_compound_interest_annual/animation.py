"""
animation.py for the LMS video generator.

Course : Pre-C-CAT - Section A - Quantitative Aptitude
Video  : Lesson 12 - Profit & Loss - 06 - Two Articles, Same SP

Source script:
  C:\\Scripts\\Section A\\Module_2_Section_A_Quantitative_Aptitude_Part_1\\Aptitude_Scripts\\Sessions 1-4 - Interest, Profit & Loss, Time & Work\\Lesson 12 - Profit & Loss\\06 - Two Articles, Same SP.pdf

Built on the golden-reference pattern:
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``;
  * layouts stacked with next_to and guarded with ``no_overlap``; nothing is
    ever animated onto or into another box.

Lesson 12, Video 6 of 8. Not the first video of the lesson: a silent breadcrumb, a one-line recap of Video 5, then today's topic. No spoken course welcome.
The narration follows the script section by section, with numbers written as words for the voice and CP / SP / MP spoken as "cost price", "selling price" and "marked price". Tables and lists are spoken one row at a time; the practice questions and answers are split over two screens each. Every percentage on screen is computed from the question's numbers and asserted.
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


def num(x):
    """A whole number in the Indian grouping the script uses: 1,00,000."""
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


def same_sp(sp, profit, loss):
    """Two articles sold at the same SP, one at ``profit``% and one at ``loss``% loss.
    Returns (cp of the profit article, cp of the loss article, rupee loss, loss % on total cost)."""
    cp_gain = Fraction(sp) / (1 + Fraction(profit) / 100)
    cp_loss = Fraction(sp) / (1 - Fraction(loss) / 100)
    total_cp = cp_gain + cp_loss
    lost = total_cp - 2 * sp
    return cp_gain, cp_loss, lost, lost / total_cp * 100


def shortcut_pct(x):
    """Same SP, x% profit and x% loss: overall loss of x²/100 %."""
    return Fraction(x) ** 2 / 100


def shortcut_rupees(sp, x):
    """Rupee loss = 2 × SP × x² / (100² − x²)."""
    return Fraction(2 * sp * x * x, 100 * 100 - x * x)


assert all(same_sp(1000, x, x)[3] == shortcut_pct(x) and same_sp(1000, x, x)[2] == shortcut_rupees(1000, x) for x in (5, 10, 15, 20, 25))

# ---- the hook: two phones ----
PHONE_SP, X = 12000, 20
CP_GAIN, CP_LOSS, HOOK_LOST, HOOK_PCT = same_sp(PHONE_SP, X, X)
assert (CP_GAIN, CP_LOSS, CP_GAIN + CP_LOSS, HOOK_LOST, HOOK_PCT) == (10000, 15000, 25000, 1000, 4)
assert (CP_GAIN * X / 100, CP_LOSS * X / 100) == (2000, 3000)

# ---- second worked example: unequal percentages ----
EX_GAIN, EX_LOSS, EX_LOST, EX_PCT = same_sp(1200, 20, 25)
assert (EX_GAIN, EX_LOSS, EX_GAIN + EX_LOSS, EX_LOST, pct(EX_PCT)) == (1000, 1600, 2600, 200, "7.69")

# ---- exam patterns (answers computed) ----
COW_GAIN, COW_LOSS, COW_LOST, _ = same_sp(19800, 10, 10)
assert (COW_GAIN, COW_LOSS, COW_LOST) == (18000, 22000, 400) and 500 * Fraction("1.2") + 500 * Fraction("0.8") == 1000
PATTERNS = [("Loss % only", "Same SP, ±15%", "15²/100", f"{dec(shortcut_pct(15))}% loss"),
            ("Rupee loss", "Two cows at ₹19,800, ±10%", "CPs 18,000 and 22,000", f"{rs(COW_LOST)} loss"),
            ("Same CP", "Each costs ₹500, ±20%", "the gains cancel", "no gain, no loss"),
            ("Unequal %", "₹1,200 each, +20% and −25%", "CPs 1,000 and 1,600", f"{pct(EX_PCT)}% loss")]

# ---- traps: (title, question, wrong, right, rule) ----
TRAPS = [("Trap 1  ·  equal percentages assumed to cancel", "Same SP, 20% profit on one and 20% loss on the other.  Result?",
          "+20 − 20  =  break-even", f"20²/100  =  a {HOOK_PCT}% loss",
          "Percentages cancel only on equal bases.  Same SP means unequal CPs."),
         ("Trap 2  ·  the shortcut used for the same CP", "Two articles each cost ₹500; one sold at 20% profit, the other at 20% loss.  Result?",
          "a 4% loss", "600 + 400 = 1,000:  no gain, no loss",
          "x²/100 needs the same selling price.")]

# ---- practice (answers computed) ----
PRACTICE_A = [("L1", "Two articles are sold at the same price, one at a 15% profit and one at a 15% loss.  Find the overall result."),
              ("L1", "Two articles are sold at the same price, one at a 5% profit and one at a 5% loss.  Find the overall loss %."),
              ("L1", "Two articles have the same SP, one at a 25% gain and one at a 25% loss.  Find the overall result."),
              ("L2", "Two cows are each sold for ₹19,800, one at a 10% gain and the other at a 10% loss.  Find the total loss in rupees."),
              ("L2", "Two articles each cost ₹500.  One is sold at a 20% profit and the other at a 20% loss.  Find the overall result."),
              ("L2", "Two articles are sold at ₹990 each, one at a 10% profit and one at a 10% loss.  Find the net loss in rupees.")]
PRACTICE_B = [("L3", "Two articles are sold at ₹1,200 each, one at a 20% profit and one at a 25% loss.  Find the overall loss %."),
              ("L3", "Two laptops are sold at ₹48,000 each, one at a 20% profit and one at a 20% loss.  Find the rupee loss."),
              ("L3", "Two items are sold at ₹4,950 each, one at a 10% profit and one at a 10% loss.  Use the rupee-loss formula, "
                     "then verify with CPs.")]
A6 = same_sp(990, 10, 10)
A8 = same_sp(48000, 20, 20)
A9 = same_sp(4950, 10, 10)
assert (A6[:3], A8[:3], A9[:3]) == ((900, 1100, 20), (40000, 60000, 4000), (4500, 5500, 100)) and shortcut_rupees(4950, 10) == 100
ANSWERS_A = [("15²/100", f"{dec(shortcut_pct(15))}% loss"),
             ("5²/100", f"{dec(shortcut_pct(5))}% loss"),
             ("25²/100", f"{dec(shortcut_pct(25))}% loss"),
             ("CPs 18,000 and 22,000: total 40,000;   sales 39,600", f"{rs(COW_LOST)} loss"),
             ("SPs 600 and 400: total 1,000 = total CP", "no gain, no loss")]
ANSWERS_B = [("CPs 900 and 1,100: total 2,000;   sales 1,980", f"{rs(A6[2])} loss"),
             ("CPs 1,000 and 1,600: total 2,600;   sales 2,400;   200/2,600", f"{pct(EX_PCT)}% loss"),
             (f"CPs 40,000 and 60,000: total {num(100000)};   sales 96,000", f"{rs(A8[2])} loss  (4%)"),
             ("2 × 4,950 × 100/9,900;    check: CPs 4,500 + 5,500 = 10,000, sales 9,900", f"{rs(A9[2])} loss")]

OBJECTIVES = [("Find the overall result", "two articles, the same SP, equal profit % and loss %"),
              ("Explain why it is always a loss", "and when it is not"),
              ("Handle unequal percentages", "on the same selling price")]
LENS = [("Recognition cue", "“each sold at the same price”, with equal ± percentages  →  an x²/100 % loss"),
        ("Target time", "20 seconds"),
        ("Sanity check", "always a loss, and small:  1% at ±10%,  4% at ±20%")]
FORMULAS = ["Same SP, x% profit and x% loss    →    an overall LOSS of x²/100 %",
            "Rupee loss  =  2 × SP × x² / (100² − x²)",
            "Same CP, x% profit and x% loss    →    no gain, no loss",
            "Unequal percentages:    find each CP, then compare the totals"]


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


class TwoArticlesSameSPVideo(LMSScene):
    lesson_title = "Two Articles, Same SP"

    def construct(self):
        self.camera.background_color = BG

        self.intro()
        self.hook()
        self.objectives()
        self.why_this_matters()
        self.different_cps()
        self.general_result()
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

    def two_cards(self, lines_a, lines_b, colors=(GOOD, BAD), width=5.8):
        """Two cards of the same height.  Returns (cards, contents)."""
        contents = [VGroup(*[text(s, size, c, w) for s, size, c, w in lines]).arrange(DOWN, buff=0.22)
                    for lines in (lines_a, lines_b)]
        tallest = max(c.height for c in contents) + 0.7
        cards = VGroup(*[self.card(c, width=width, height=tallest, color=col) for c, col in zip(contents, colors)])\
            .arrange(RIGHT, buff=0.6)
        return cards, contents

    # ================================================== 0. INTRO ==========
    # Not the first video: silent breadcrumb, a one-line recap of Video 5, then today's topic.

    def intro(self):
        self.scene_start("S00_intro", title="Intro")

        crumb = self.breadcrumb("Quantitative Aptitude", "Lesson 12 · Profit & Loss", "Video 6 of 8")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        recap = VGroup(text("last video", SMALL, MUTED), pill("false weights:  the base is what is actually handed over", WORD, size=LABEL))\
            .arrange(DOWN, buff=0.25)
        title = text("Two Articles, Same SP", TITLE, INK, BOLD)
        today = text("today: one selling price, an equal profit % and loss %", LABEL, FOCUS)
        block = VGroup(recap, title, today).arrange(DOWN, buff=0.7)
        fit_within(block, SAFE_W, SAFE_H - crumb.height - 0.9)
        block.next_to(crumb, DOWN, buff=0.7)
        self.no_overlap(crumb, recap, title, today)
        self.validator.check_in_frame(VGroup(crumb, block))

        n = self.narrate(
            id="intro_01",
            text="In the last video, the base for a false weight was the weight actually handed over.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.at_word(n, "base")
        self.play(FadeIn(recap, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="intro_02",
            text="Today: two articles sold at the same price, one at a profit and one at a loss.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "same")
        self.play(FadeIn(title, shift=UP * 0.1))
        self.at_word(n, "profit")
        self.play(FadeIn(today, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_intro")

    # =================================================== 1. HOOK ==========

    def hook(self):
        self.scene_start("S01_hook", title="Hook")

        head = self.heading("Two used phones")
        cards, (a, b) = self.two_cards(
            [("Phone 1", LABEL, GOOD, BOLD), (f"sold for {rs(PHONE_SP)}", BODY, INK, BOLD), (f"{X}% profit", LABEL, GOOD, BOLD)],
            [("Phone 2", LABEL, BAD, BOLD), (f"sold for {rs(PHONE_SP)}", BODY, INK, BOLD), (f"{X}% loss", LABEL, BAD, BOLD)])
        ask = VGroup(pill("did you break even?", FOCUS, size=LABEL), text("almost everyone says yes:  +20 − 20 = 0", LABEL, MUTED))\
            .arrange(RIGHT, buff=0.5)
        bank = text("your bank balance disagrees", LABEL, BAD, BOLD)
        goal = text("goal: exactly how much you lost, and why, in one line", SMALL, GOOD, BOLD)
        self.stack(head, [cards, ask, bank, goal], buff=0.5, top=0.55)
        self.no_overlap(cards[0], cards[1])
        self.no_overlap(*ask)

        n = self.narrate(
            id="hook_01",
            text="You sell two used phones for twelve thousand rupees each.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "twelve")
        self.play(FadeIn(cards[0][0]), FadeIn(cards[1][0]), FadeIn(a[:2], shift=UP * 0.1), FadeIn(b[:2], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_02",
            text="On one you made a twenty percent profit; on the other, a twenty percent loss.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "profit")
        self.play(FadeIn(a[2], shift=UP * 0.1))
        self.at_word(n, "loss")
        self.play(FadeIn(b[2], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_03",
            text="Did you break even? Almost everyone says yes: plus twenty, minus twenty, zero.",
            voice="default",
            subtitle=True,
            pause_after=3.0,
        )
        self.at_word(n, "break")
        self.play(FadeIn(ask[0], shift=UP * 0.1))
        self.at_word(n, "zero")
        self.play(FadeIn(ask[1], shift=LEFT * 0.1))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="hook_04",
            text="Your bank balance disagrees.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "disagrees")
        self.play(FadeIn(bank, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_05",
            text="By the end of this video you'll know exactly how much you lost, and why, in one line.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "exactly")
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
            text="First, find the overall result when two articles share a selling price but have equal profit and loss "
                 "percentages.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "overall")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "equal")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="obj_03",
            text="Second, explain why the result is always a loss, and when it is not.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "explain")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "when")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="obj_04",
            text="Third, handle unequal percentages on the same selling price.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "unequal")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "same")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_objectives")

    # ========================================== 3. WHY THIS MATTERS ==========

    def why_this_matters(self):
        self.scene_start("S03_why_this_matters", title="Why This Matters")

        head = self.heading("Why this matters")
        favourite = pill("a favourite exam question", WORD, size=LABEL)
        neat = VGroup(text("the instinct is strong", LABEL, MUTED), text("the answer is neat:  a loss of x²/100 %", LABEL, FOCUS, BOLD))\
            .arrange(RIGHT, buff=0.7)
        protects = pill("knowing why protects you whenever percentages sit on different bases", GOOD, size=LABEL)
        self.stack(head, [favourite, neat, protects], buff=0.8, top=0.9)
        self.no_overlap(*neat)

        n = self.narrate(
            id="why_01",
            text="This is a favourite exam question, because the instinct is so strong and the answer is so neat: a loss of x "
                 "squared over a hundred percent.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "favourite")
        self.play(FadeIn(favourite, shift=UP * 0.1))
        self.at_word(n, "instinct")
        self.play(FadeIn(neat[0], shift=UP * 0.1))
        self.at_word(n, "neat")
        self.play(FadeIn(neat[1], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="why_02",
            text="Understanding why also protects you in every question where percentages sit on different bases.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "protects")
        self.play(FadeIn(protects, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_why_this_matters")

    # ================================ 4. CONCEPT: SAME SP, DIFFERENT CPs ==========

    def different_cps(self):
        self.scene_start("S04_different_cps", title="Concept - Same SP Means Different CPs")

        head = self.heading("Same SP means different CPs")
        table = self.table_rows(["Article", "Sold for", "Cost price", f"{X}% of that cost"],
                                [["at 20% profit", rs(PHONE_SP), f"12,000 ÷ 1.2 = {rs(CP_GAIN)}", f"+ {rs(CP_GAIN * X / 100)}"],
                                 ["at 20% loss", rs(PHONE_SP), f"12,000 ÷ 0.8 = {rs(CP_LOSS)}", f"− {rs(CP_LOSS * X / 100)}"]],
                                [2.9, 2.2, 4.8, 3.0], size=LABEL)
        rows = table[1:]
        rows[0][0].set_color(GOOD)
        rows[0][3].set_color(GOOD)
        rows[1][0].set_color(BAD)
        rows[1][3].set_color(BAD)
        larger = text("the loss sits on the larger cost", LABEL, RATIO, BOLD)
        totals = VGroup(text(f"total CP {rs(CP_GAIN + CP_LOSS)}", LABEL, INK), text(f"total SP {rs(2 * PHONE_SP)}", LABEL, INK),
                        pill(f"a {rs(HOOK_LOST)} loss  =  {HOOK_PCT}% of cost", BAD, size=LABEL)).arrange(RIGHT, buff=0.6)
        self.stack(head, [table, larger, totals], buff=0.7, top=0.7)
        self.no_overlap(*table)
        self.no_overlap(*totals)

        n = self.narrate(
            id="cps_01",
            text="The same selling price means different cost prices. At twenty percent profit, the cost is twelve thousand "
                 "divided by one point two: ten thousand.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "different")
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "divided")
        self.play(FadeIn(rows[0][:3], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="cps_02",
            text="At twenty percent loss, the cost is twelve thousand divided by zero point eight: fifteen thousand.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "divided")
        self.play(FadeIn(rows[1][:3], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="cps_03",
            text="The loss sits on the larger cost. Plus twenty percent of ten thousand is two thousand; minus twenty percent "
                 "of fifteen thousand is three thousand.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "larger")
        self.play(FadeIn(larger, shift=UP * 0.1))
        self.at_word(n, "two")
        self.play(FadeIn(rows[0][3], shift=LEFT * 0.1))
        self.at_word(n, "three")
        self.play(FadeIn(rows[1][3], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="cps_04",
            text="So the net is a loss. Total cost twenty-five thousand, total sales twenty-four thousand: a one thousand rupee "
                 "loss, which is four percent of cost.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "twenty-five")
        self.play(FadeIn(totals[0], shift=UP * 0.1))
        self.at_word(n, "twenty-four")
        self.play(FadeIn(totals[1], shift=UP * 0.1))
        self.at_word(n, "four")
        self.play(FadeIn(totals[2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_different_cps")

    # ==================================== 5. CONCEPT: THE GENERAL RESULT ==========

    def general_result(self):
        self.scene_start("S05_general_result", title="Concept - The General Result, and When It Cancels")

        head = self.heading("The general result")
        rule = pill("same SP,  x% profit and x% loss   →   an overall loss of x²/100 %", BAD, size=LABEL)
        twenty = text(f"for x = {X}:   400/100  =  {shortcut_pct(X)}%", LABEL, INK, BOLD)
        cancels = text("when it cancels", LABEL, GOOD, BOLD)
        same_cp = pill("equal CPs:   +x% and −x% cancel exactly: no profit, no loss", GOOD, size=LABEL)
        self.stack(head, [rule, twenty, cancels, same_cp], buff=0.7, top=0.8)

        n = self.narrate(
            id="general_01",
            text="The general result: with the same selling price, and x percent profit and x percent loss, the overall loss "
                 "is always x squared over a hundred percent.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "general")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "squared")
        self.play(FadeIn(rule, scale=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="general_02",
            text="For x equal to twenty: four hundred over a hundred is four percent.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "twenty")
        self.play(FadeIn(twenty, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="general_03",
            text="When does it cancel? If the cost prices are equal instead, plus x percent and minus x percent exactly cancel: "
                 "no profit, no loss.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "cancel")
        self.play(FadeIn(cancels, shift=UP * 0.1))
        self.at_word(n, "equal")
        self.play(FadeIn(same_cp, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_general_result")

    # ============================================== 6. FORMULA BOX ==========

    def formula_box(self):
        self.scene_start("S06_formula_box", title="Formula Box")

        head = self.heading("Formula box", GOOD)
        lines = VGroup(*[text(f, LABEL, INK) for f in FORMULAS]).arrange(DOWN, buff=0.5, aligned_edge=LEFT)
        box = self.card(lines, width=SAFE_W - 0.8, color=GOOD, pad=0.5)
        self.stack(head, [box], top=0.8)

        n = self.narrate(
            id="formula_01",
            text="Here is the formula box. The same selling price, with x percent profit and x percent loss, gives an overall "
                 "loss of x squared over a hundred percent.",
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
            text="The rupee loss is two times the selling price, times x squared, over one hundred squared minus x squared.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "rupee")
        self.play(FadeIn(lines[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_03",
            text="The same cost price, with x percent profit and x percent loss, gives no gain and no loss.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "cost")
        self.play(FadeIn(lines[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_04",
            text="For unequal percentages, find each cost price, then compare the totals.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "unequal")
        self.play(FadeIn(lines[3], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_formula_box")

    # ============================================== 7. THE ANALOGY ==========

    def analogy(self):
        self.scene_start("S07_analogy", title="The Analogy - Two Bets")

        head = self.heading("Think of two bets")
        cards, (win, lose) = self.two_cards(
            [("a small stake", LABEL, GOOD, BOLD), ("you win 20%", BODY, INK, BOLD)],
            [("a bigger stake", LABEL, BAD, BOLD), ("you lose 20%", BODY, INK, BOLD)])
        bigger = text("the loss is 20% of a bigger number: in rupees it beats the win", LABEL, INK)
        bases = pill("same percentages, different bases: they can't cancel", FOCUS, size=LABEL)
        stops = VGroup(text("Where the analogy stops", LABEL, BAD, BOLD),
                       text("in betting you choose your stakes", LABEL, MUTED),
                       text("here the “stakes”, the CPs, are forced by the common selling price", LABEL, INK)).arrange(DOWN, buff=0.2)
        self.stack(head, [cards, bigger, bases, stops], buff=0.45, top=0.5)
        self.no_overlap(cards[0], cards[1])

        n = self.narrate(
            id="analogy_01",
            text="Think of two bets. You win twenty percent on a small stake, and lose twenty percent on a bigger stake.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "bets")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "win")
        self.play(FadeIn(cards[0], shift=UP * 0.1))
        self.at_word(n, "lose")
        self.play(FadeIn(cards[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_02",
            text="The loss is twenty percent of a bigger number, so in rupees it beats the win.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "bigger")
        self.play(FadeIn(bigger, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_03",
            text="Same percentages, different bases, so they can't cancel.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "different")
        self.play(FadeIn(bases, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_04",
            text="Where the analogy stops: in betting you choose your stakes.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "stops")
        self.play(FadeIn(stops[0], shift=UP * 0.1))
        self.at_word(n, "choose")
        self.play(FadeIn(stops[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_05",
            text="Here the stakes, the cost prices, are forced by the common selling price.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "forced")
        self.play(FadeIn(stops[2], shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S07_analogy")

    # ================================ 8. WORKED EXAMPLE: CLOSING THE HOOK ==========

    def hook_solved(self):
        self.scene_start("S08_hook_solved", title="Worked Example - Closing the Hook")

        head = self.heading(f"The two phones:  {rs(PHONE_SP)} each, ±{X}%")
        steps = self.solve_steps([(f"CPs:   {rs(CP_GAIN)} and {rs(CP_LOSS)}", f"total  {rs(CP_GAIN + CP_LOSS)}"),
                                  (f"sales  {rs(2 * PHONE_SP)}", f"loss  {rs(HOOK_LOST)}  =  {HOOK_PCT}%"),
                                  ("one line:   20²/100  =  4%", f"2 × 12,000 × 400/9,600  =  {rs(shortcut_rupees(PHONE_SP, X))}")])
        self.stack(head, [steps], top=1.0)
        self.no_overlap(*steps)

        n = self.narrate(
            id="solved_01",
            text="The cost prices are ten thousand and fifteen thousand: twenty-five thousand in total.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "ten")
        self.play(FadeIn(steps[0][:2], shift=RIGHT * 0.1))
        self.at_word(n, "twenty-five")
        self.play(FadeIn(steps[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_02",
            text="The sales are twenty-four thousand, so the loss is one thousand rupees, which is four percent.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "sales")
        self.play(FadeIn(steps[1][:2], shift=RIGHT * 0.1))
        self.at_word(n, "loss")
        self.play(FadeIn(steps[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_03",
            text="In one line: twenty squared over a hundred is four percent, and the rupee loss is two times twelve thousand, "
                 "times four hundred, over nine thousand six hundred: one thousand rupees.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "squared")
        self.play(FadeIn(steps[2][:2], shift=RIGHT * 0.1))
        self.at_word(n, "rupee")
        self.play(FadeIn(steps[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S08_hook_solved")

    # ====================== 9. SECOND WORKED EXAMPLE: UNEQUAL PERCENTAGES ==========

    def second_example(self):
        self.scene_start("S09_second_example", title="A Second Worked Example - Unequal Percentages")

        head = self.heading("Unequal percentages on the same SP")
        given = VGroup(pill("each sold at ₹1,200", WORD, size=LABEL), pill("one at 20% profit", GOOD, size=LABEL),
                       pill("one at 25% loss", BAD, size=LABEL), pill("overall result = ?", FOCUS, size=LABEL)).arrange(RIGHT, buff=0.35)
        steps = self.solve_steps([
            (f"CPs:   1,200 ÷ 1.2 = {rs(EX_GAIN)},    1,200 ÷ 0.75 = {rs(EX_LOSS)}", f"total  {rs(EX_GAIN + EX_LOSS)}"),
            ("sales  ₹2,400", f"loss  {rs(EX_LOST)}"),
            ("loss %  =  200/2,600", f"=  {pct(EX_PCT)}%")])
        totals = text("no shortcut here: totals always work", SMALL, RATIO, BOLD)
        self.stack(head, [given, steps, totals], buff=0.6, top=0.7)
        self.no_overlap(*given)
        self.no_overlap(*steps)

        n = self.narrate(
            id="unequal_01",
            text="Two articles are sold at twelve hundred rupees each, one at a twenty percent profit and the other at a "
                 "twenty-five percent loss. Find the overall result.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "twelve")
        self.play(FadeIn(given[0], shift=UP * 0.1))
        self.at_word(n, "profit")
        self.play(FadeIn(given[1], shift=UP * 0.1))
        self.at_word(n, "loss")
        self.play(FadeIn(given[2], shift=UP * 0.1))
        self.at_word(n, "Find")
        self.play(FadeIn(given[3], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="unequal_02",
            text="The cost prices are twelve hundred divided by one point two, one thousand, and twelve hundred divided by zero "
                 "point seven five, sixteen hundred: two thousand six hundred in total.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "divided", occurrence=1)
        self.play(FadeIn(steps[0][:2], shift=RIGHT * 0.1))
        self.at_word(n, "total")
        self.play(FadeIn(steps[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="unequal_03",
            text="The sales are two thousand four hundred, so the loss is two hundred rupees.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "sales")
        self.play(FadeIn(steps[1][:2], shift=RIGHT * 0.1))
        self.at_word(n, "loss")
        self.play(FadeIn(steps[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="unequal_04",
            text="The loss percent is two hundred over two thousand six hundred: seven point six nine percent. There is no "
                 "shortcut here; totals always work.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "over")
        self.play(FadeIn(steps[2][:2], shift=RIGHT * 0.1))
        self.at_word(n, "seven")
        self.play(FadeIn(steps[2][2], shift=LEFT * 0.1))
        self.at_word(n, "shortcut")
        self.play(FadeIn(totals, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S09_second_example")

    # ============================================ 10. EXAM PATTERNS ==========

    def exam_patterns(self):
        self.scene_start("S10_exam_patterns", title="Exam Patterns - How This Is Asked")

        head = self.heading("Exam patterns: how this is asked")
        table, rows = self.placed_table(head, ["Pattern", "Example", "Method", "Answer"], [list(p) for p in PATTERNS],
                                        [2.4, 4.4, 3.8, 2.6], room=1.2)
        for row in rows:
            row[0].set_color(WORD)
            row[3].set_color(GOOD)

        n = self.narrate(
            id="patterns_01",
            text="Exams ask this in four ways.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "four")
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.wait_for_narration(n)

        n = self.narrate(
            id="patterns_02",
            text="The loss percent only: the same price with plus and minus fifteen percent is fifteen squared over a hundred, "
                 "a two point two five percent loss.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "only")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "squared")
        self.play(FadeIn(rows[0][2:], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="patterns_03",
            text="The rupee loss: two cows at nineteen thousand eight hundred each, plus and minus ten percent, cost eighteen "
                 "thousand and twenty-two thousand, so the loss is four hundred rupees.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "rupee")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "cost")
        self.play(FadeIn(rows[1][2:], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="patterns_04",
            text="The same cost price: each costs five hundred, plus and minus twenty percent, so the gains cancel: no gain, no "
                 "loss.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "same")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "cancel")
        self.play(FadeIn(rows[2][2:], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="patterns_05",
            text="Unequal percentages: twelve hundred each, plus twenty and minus twenty-five percent, cost one thousand and "
                 "sixteen hundred, so a seven point six nine percent loss.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Unequal")
        self.play(FadeIn(rows[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "cost")
        self.play(FadeIn(rows[3][2:], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S10_exam_patterns")

    # ================================ 11. TRAPS AND CONFUSING QUESTIONS ==========

    def traps(self):
        self.scene_start("S11_traps", title="Traps and Confusing Questions")

        head, q, wrong, right, rule = self.show_trap(TRAPS[0])

        n = self.narrate(
            id="trap1_01",
            text="Trap one: equal percentages assumed to cancel. The same selling price, twenty percent profit on one and "
                 "twenty percent loss on the other; what is the result?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "cancel")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "same")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="trap1_02",
            text="The wrong instinct is break-even. The correct answer is a four percent loss.",
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
            text="The rule: percentages cancel only on equal bases. The same selling price means unequal cost prices.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "rule")
        self.play(FadeIn(rule, shift=UP * 0.1))
        self.at_word(n, "unequal")
        self.play(Indicate(rule, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)
        self.clear_stage()

        head, q, wrong, right, rule = self.show_trap(TRAPS[1])

        n = self.narrate(
            id="trap2_01",
            text="Trap two: the shortcut used for the same cost price. Two articles each cost five hundred rupees; one is sold "
                 "at twenty percent profit, the other at twenty percent loss. What is the result?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "shortcut")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "articles")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.at_word(n, "result")
        self.play(Indicate(q, color=FOCUS, scale_factor=1.02))
        self.wait_for_narration(n)

        n = self.narrate(
            id="trap2_02",
            text="The wrong instinct is a four percent loss. The correct answer is no gain, no loss: six hundred plus four "
                 "hundred is one thousand.",
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
            text="The rule: x squared over a hundred needs the same selling price.",
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
        given = VGroup(pill("two articles, the same selling price", WORD, size=LABEL), pill("one at 10% profit", GOOD, size=LABEL),
                       pill("one at 10% loss", BAD, size=LABEL)).arrange(RIGHT, buff=0.35)
        hint = pill("overall result = ?", FOCUS, size=BODY)
        work = VGroup(text("10²/100", BODY, INK), text(f"=  a {shortcut_pct(10)}% loss", BODY, GOOD, BOLD)).arrange(RIGHT, buff=0.5)
        self.stack(head, [given, hint, work], buff=0.8, top=0.9)
        self.no_overlap(*given)
        self.no_overlap(*work)

        n = self.narrate(
            id="check_01",
            text="Your turn. Two articles sell at the same price, one at ten percent profit and one at ten percent loss. What "
                 "is the overall result?",
            voice="default",
            subtitle=True,
            pause_after=10.0,
        )
        self.at_word(n, "turn")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "same")
        self.play(FadeIn(given[0], shift=UP * 0.1))
        self.at_word(n, "profit")
        self.play(FadeIn(given[1], shift=UP * 0.1))
        self.at_word(n, "loss")
        self.play(FadeIn(given[2], shift=UP * 0.1))
        self.at_word(n, "overall")
        self.play(FadeIn(hint, shift=UP * 0.1))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="check_02",
            text="Ten squared over a hundred: a one percent loss.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "squared")
        self.play(FadeIn(work[0], shift=UP * 0.1))
        self.at_word(n, "loss")
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
            text="Level one, question one: two articles are sold at the same price, one at a fifteen percent profit and one at "
                 "a fifteen percent loss; find the overall result. Question two: the same, at five percent profit and five "
                 "percent loss; find the overall loss percent. Question three: two articles have the same selling price, one "
                 "at a twenty-five percent gain and one at a twenty-five percent loss; find the overall result.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "fifteen")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "five")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.at_word(n, "twenty-five")
        self.play(FadeIn(rows[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="practice_02",
            text="Level two, question four: two cows are each sold for nineteen thousand eight hundred rupees, one at a ten "
                 "percent gain and the other at a ten percent loss; find the total loss in rupees. Question five: two "
                 "articles each cost five hundred rupees; one is sold at a twenty percent profit and the other at a twenty "
                 "percent loss; find the overall result. Question six: two articles are sold at nine hundred and ninety "
                 "rupees each, one at a ten percent profit and one at a ten percent loss; find the net loss in rupees.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "cows")
        self.play(FadeIn(rows[3], shift=RIGHT * 0.2))
        self.at_word(n, "cost")
        self.play(FadeIn(rows[4], shift=RIGHT * 0.2))
        self.at_word(n, "ninety")
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
            text="Level three, question seven: two articles are sold at twelve hundred rupees each, one at a twenty percent "
                 "profit and one at a twenty-five percent loss; find the overall loss percent. Question eight: two laptops "
                 "are sold at forty-eight thousand rupees each, one at a twenty percent profit and one at a twenty percent "
                 "loss; find the rupee loss. Question nine: two items are sold at four thousand nine hundred and fifty rupees "
                 "each, one at a ten percent profit and one at a ten percent loss; use the rupee-loss formula, then verify "
                 "with the cost prices.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "twelve")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "laptops")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.at_word(n, "items")
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
            text="One: fifteen squared over a hundred is a two point two five percent loss.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "squared")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "loss")
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_02",
            text="Two: five squared over a hundred is a zero point two five percent loss.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "squared")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "loss")
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_03",
            text="Three: twenty-five squared over a hundred is a six point two five percent loss.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "squared")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "loss")
        self.play(FadeIn(rows[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_04",
            text="Four: the cost prices are eighteen thousand and twenty-two thousand, forty thousand in total, against sales "
                 "of thirty-nine thousand six hundred: a loss of four hundred rupees.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "cost")
        self.play(FadeIn(rows[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "loss")
        self.play(FadeIn(rows[3][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_05",
            text="Five: the selling prices are six hundred and four hundred, one thousand in total, the same as the total "
                 "cost: no gain, no loss.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "selling")
        self.play(FadeIn(rows[4][:2], shift=RIGHT * 0.2))
        self.at_word(n, "gain")
        self.play(FadeIn(rows[4][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Answer key  ·  6 to 9", GOOD)
        table, rows = self.answer_table(head, ANSWERS_B, 6)

        n = self.narrate(
            id="answers_06",
            text="Six: the cost prices are nine hundred and eleven hundred, two thousand in total, against sales of nineteen "
                 "hundred and eighty: a loss of twenty rupees.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "cost")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "loss")
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_07",
            text="Seven: the cost prices are one thousand and sixteen hundred, two thousand six hundred in total, against "
                 "sales of two thousand four hundred: a loss of seven point six nine percent.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "cost")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "loss")
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_08",
            text="Eight: the cost prices are forty thousand and sixty thousand, one lakh in total, against sales of ninety-six "
                 "thousand: a loss of four thousand rupees, four percent.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "cost")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "loss")
        self.play(FadeIn(rows[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_09",
            text="Nine: two times four thousand nine hundred and fifty, times one hundred, over nine thousand nine hundred, is "
                 "one hundred rupees. Check: the cost prices are four thousand five hundred and five thousand five hundred, "
                 "ten thousand in total, against sales of nine thousand nine hundred.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "times", occurrence=1)
        self.play(FadeIn(rows[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "Check")
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
            text="Recognise and move. The recognition cue: each sold at the same price, with equal plus and minus percentages, "
                 "means a loss of x squared over a hundred percent.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Recognise")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "cue")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "squared")
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
            text="The sanity check: the answer is always a loss, and small: one percent at plus and minus ten, four percent at "
                 "plus and minus twenty.",
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
        box = VGroup(text("same SP, ±x%    →    a loss of x²/100 %      (the loss sits on the larger cost)", LABEL, INK),
                     text("rupee loss  =  2 × SP × x² / (100² − x²)", LABEL, INK),
                     text("same CP, ±x%    →    cancels exactly", LABEL, INK),
                     text("unequal percentages:    find each CP, compare the totals", LABEL, INK)).arrange(DOWN, buff=0.32, aligned_edge=LEFT)
        nxt = self.breadcrumb("Next", "Video 7 · Partial Sales & Break-Even")
        self.stack(head, [box, nxt], buff=0.9, top=0.8)
        self.no_overlap(*box)

        n = self.narrate(
            id="summary_01",
            text="The same selling price, with x percent profit and x percent loss, always loses x squared over a hundred "
                 "percent, because the loss sits on the larger cost.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "squared")
        self.play(FadeIn(box[0], shift=RIGHT * 0.2))
        self.at_word(n, "larger")
        self.play(FadeIn(box[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_02",
            text="The same cost price cancels exactly.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "cancels")
        self.play(FadeIn(box[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_03",
            text="For unequal percentages, find each cost price and compare the totals.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "unequal")
        self.play(FadeIn(box[3], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_04",
            text="Next: partial sales and break-even.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Next")
        self.play(FadeIn(nxt, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S16_summary")

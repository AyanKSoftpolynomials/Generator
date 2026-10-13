"""
animation.py for the LMS video generator.

Course : Pre-C-CAT - Section A - Quantitative Aptitude
Video  : Lesson 25 - Alligation & Mixtures - 02 - Alligation Rule

Source script:
  C:\\Scripts\\Section A\\Module2\\S21-25_Ratio_Age_Clock_Mixtures_Mensuration\\Lesson 25 - Allegation & Mixtures\\05 - Alligation Rule.pdf

Built on the golden-reference pattern:
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``;
  * layouts stacked with next_to and guarded with ``no_overlap``; nothing is
    ever animated onto or into another box.

Lesson 25, Video 2 of 7 (the lesson's own order, from its Pre-Lesson Brief). Not the first video of the lesson: a silent
breadcrumb, a one-line recap of Video 1, then today's topic. No spoken course welcome.
The seven source scripts of this lesson are identical apart from their titles, so, as agreed with the course owner, each video was
written for its own topic. This one uses the script's hook (rice at 40 and 60 making 48), its formula  L : H = (H - M) : (M - L),
its balance-scale analogy, its checkpoint and its alligation practice questions, and adds further verified questions.
The main formula stays in a panel on the left while each worked example is solved on the right.
Text colours: white and grey, one blue accent, green and red only for right and wrong.
Pauses: 3 seconds on the hook question, 10 seconds on the checkpoint, 12 seconds on each practice screen.
"""

import math

import numpy as np
from manim import *

from src.animation import LMSScene

# ============================================================== style ====

BG = "#0B1020"
INK = "#F1F5F9"
MUTED = "#94A3B8"
PANEL = "#151C2E"
CELL = "#1B2440"

TERM = INK             # series terms
DIFF = "#7FB2E5"       # first differences
SECOND = "#7FB2E5"     # second differences / pattern of the differences
RATIO = "#7FB2E5"      # ratios (the next topic's tool)
FOCUS = "#7FB2E5"      # "look here" / predicted value
GOOD = "#7FC8A0"       # confirmed answer
BAD = "#E08080"        # wrong / trap

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

SHORT_WORDS = {"a", "an", "as", "at", "be", "by", "do", "he", "if", "in", "is", "it", "no", "of", "on", "or", "so", "to", "up", "we"}


def cap_first(s):
    """Start on-screen text with a capital letter when it starts with a word (not a variable, unit or number)."""
    start = 0
    while start < len(s) and s[start] in "“\"'(":
        start += 1
    words = s[start:].split()
    if not words:
        return s
    first = words[0].rstrip(".,;:?!”’")
    plain = first.replace("'", "").replace("’", "").replace("-", "")
    if not (plain.isalpha() and plain.islower()):
        return s
    if len(plain) == 1:
        follower = words[1].rstrip(".,;:?!") if len(words) > 1 else ""
        if not (plain == "a" and len(follower) >= 2 and follower.replace("-", "").isalpha()):
            return s
    elif len(plain) == 2 and plain not in SHORT_WORDS:
        return s
    return s[:start] + s[start].upper() + s[start + 1:]

def text(s, size=BODY, color=INK, weight=NORMAL, t2c=None):
    return Text(cap_first(s), font=FONT, font_size=size, color=color, weight=weight, t2c=t2c or {})


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

WORD = "#7FB2E5"          # the question word
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

from fractions import Fraction as F
from math import gcd


def cross(low, high, m):
    """Alligation: ratio (quantity at the low value) : (quantity at the high value) for a mean m."""
    a, b = F(high) - F(m), F(m) - F(low)
    assert a > 0 and b > 0
    scale = a.denominator * b.denominator // gcd(a.denominator, b.denominator)
    a, b = int(a * scale), int(b * scale)
    g = gcd(a, b)
    return a // g, b // g


def mean(q1, v1, q2, v2):
    return F(q1 * v1 + q2 * v2, q1 + q2)


# ---- hook, examples, patterns ----
assert cross(40, 60, 48) == (3, 2) and mean(3, 40, 2, 60) == 48 and cross(20, 50, 30) == (2, 1) and mean(2, 20, 1, 50) == 30
assert cross(0, 60, 45) == (1, 3) and F(66, 1) / F(110, 100) == 60 and cross(50, 65, 60) == (1, 2)
assert cross(70, 85, 76) == (3, 2) and cross(20, 40, 30) == (1, 1)
# ---- traps and checkpoint ----
assert cross(30, 50, 38) == (3, 2) and mean(2, 40, 3, 60) == 52 and cross(50, 65, 60) != cross(50, 70, 66)
# ---- practice ----
assert cross(10, 40, 25) == (1, 1) and cross(30, 50, 42) == (2, 3) and cross(0, 48, 40) == (1, 5) and cross(15, 40, 30) == (2, 3)
assert F(69, 1) / F(115, 100) == 60 and cross(52, 72, 60) == (3, 2) and cross(60, 75, 65) == (2, 1)

OBJECTIVES = [("Set up the alligation cross", "for two values and the mean of their mixture"),
              ("Read the ratio off the cross", "cheaper : dearer  =  (H − M) : (M − L)"),
              ("Use it for prices, concentrations and averages", "and know when it does not apply")]
STEPS_A = [("It comes from the balance of a weighted average", "qL × (M − L)  =  qH × (H − M),   so   qL : qH  =  (H − M) : (M − L)"),
           ("Write the cross:  L and H on top, M in the middle", "subtract along the diagonals:   H − M  under L,    M − L  under H"),
           ("Each quantity takes the other value's distance", "the cheaper one gets the distance from the dearer value to the mean"),
           ("The mean must lie between the two values", "if M is outside L and H, no mixture of the two can reach it")]
STEPS_B = [("Use the same units on both sides", "₹ a kg with ₹ a kg,   % with %;    the answer is a ratio of quantities"),
           ("It works for anything that is averaged", "prices, percentages, average marks, average speeds"),
           ("Water is 0;  a pure ingredient is 100%", "water and milk worth ₹60 a litre making ₹45:    15 : 45  =  1 : 3"),
           ("With profit, first find the cost price of the mixture", "the mean in the cross is always a cost, never a selling price")]
FORMULAS = ["Quantity at L : quantity at H   =   (H − M) : (M − L)",
            "The cross:      L        H            M in the middle,   differences along the diagonals",
            "Check:      (qL × L + qH × H)/(qL + qH)   =   M",
            "Water  =  0;        pure  =  100%;        M lies between L and H",
            "Sold at a profit:      M  =  selling price ÷ (1 + profit rate)"]
PATTERNS = [("Two prices", "₹40 and ₹60 to make ₹48", "(60 − 48) : (48 − 40)  =  12 : 8", "3 : 2"),
            ("Two strengths", "20% and 50% to make 30%", "(50 − 30) : (30 − 20)  =  20 : 10", "2 : 1"),
            ("Water", "water and milk at ₹60 a litre to make ₹45", "(60 − 45) : (45 − 0)  =  15 : 45", "1 : 3"),
            ("Sold at a profit", "₹50 and ₹65 tea, sold at ₹66 with 10% profit", "cost 60:    (65 − 60) : (60 − 50)", "1 : 2"),
            ("Averages", "boys average 70, girls 85, class 76", "(85 − 76) : (76 − 70)  =  9 : 6", "3 : 2"),
            ("Mean in the middle", "₹20 and ₹40 to make ₹30", "10 : 10", "1 : 1")]
TRAPS = [("Trap 1  ·  the differences on the wrong side",
          "Rice at ₹40 and ₹60 a kg is mixed to make ₹48 a kg.  Find the ratio cheaper : dearer.",
          "(48 − 40) : (60 − 48)  =  2 : 3", "(60 − 48) : (48 − 40)  =  3 : 2",
          "Cross over: the cheaper takes H − M.  The mean is nearer 40, so more of it."),
         ("Trap 2  ·  the selling price used as the mean",
          "Tea at ₹50 and ₹65 a kg is mixed and sold at ₹66 a kg with 10% profit.  Find the ratio.",
          "Mean 66:  not between 50 and 65", "Cost 66 ÷ 1.1 = 60:   1 : 2",
          "Remove the profit first.  The mean in the cross is the cost price."),
         ("Trap 3  ·  the cross used when quantities are given",
          "2 kg at ₹40 a kg is mixed with 3 kg at ₹60 a kg.  Find the price of the mixture.",
          "A cross with no mean to use", "(80 + 180)/5  =  ₹52 a kg",
          "Alligation finds a ratio from a mean.  For a mean from quantities, use the average.")]
PRACTICE_A = [("L1", "In what ratio must ₹20 and ₹40 a kg varieties be mixed to make ₹30 a kg?"),
              ("L1", "In what ratio must 10% and 40% solutions be mixed to make a 25% solution?"),
              ("L2", "Sugar at ₹30 and ₹50 a kg is mixed to make ₹42 a kg.  Find the ratio cheaper : dearer."),
              ("L2", "Rice at ₹40 and ₹60 a kg is mixed to make ₹48 a kg.  Find the ratio cheaper : dearer."),
              ("L2", "In what ratio must water be mixed with milk worth ₹48 a litre to make a mixture worth ₹40 a litre?")]
PRACTICE_B = [("L3", "In what ratio must 15% and 40% acid solutions be mixed to make a 30% solution?"),
              ("L3", "Tea at ₹52 and ₹72 a kg is mixed and sold at ₹69 a kg, a profit of 15%.  Find the ratio cheaper : dearer."),
              ("L3", "Boys average 60 marks, girls average 75, and the whole class averages 65.  Find the ratio of boys to girls.")]
ANSWERS_A = [("(40 − 30) : (30 − 20)  =  10 : 10", "1 : 1"),
             ("(40 − 25) : (25 − 10)  =  15 : 15", "1 : 1"),
             ("(50 − 42) : (42 − 30)  =  8 : 12", "2 : 3"),
             ("(60 − 48) : (48 − 40)  =  12 : 8", "3 : 2")]
ANSWERS_B = [("Water is 0:    (48 − 40) : (40 − 0)  =  8 : 40", "1 : 5"),
             ("(40 − 30) : (30 − 15)  =  10 : 15", "2 : 3"),
             ("Cost  69 ÷ 1.15 = 60;      (72 − 60) : (60 − 52)  =  12 : 8", "3 : 2"),
             ("(75 − 65) : (65 − 60)  =  10 : 5", "2 : 1")]
LENS = [("Recognition cue", "“in what ratio must … be mixed”, with two values and the value of the mixture given"),
        ("Target time", "20 to 30 seconds"),
        ("Sanity check", "more of the ingredient whose value is nearer the mean;  put the ratio back into the average")]


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


class AlligationRuleVideo(LMSScene):
    lesson_title = "Alligation Rule"

    def construct(self):
        self.camera.background_color = BG

        self.intro()
        self.hook()
        self.objectives()
        self.why_this_matters()
        self.the_cross()
        self.using_it()
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
        colors = [DIFF, MUTED, RATIO]
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
        self.side = None                         # the formula panel leaves with its screen
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
        side = getattr(self, "side", None)
        fit_within(body, self.body_w(), SAFE_H - head.height - top - 0.3)
        body.next_to(head, DOWN, buff=top)
        if side is not None:                     # the formula panel keeps the left; the example works on the right
            body.set_x(FRAME_W / 2 - SAFE - self.body_w() / 2)
            side.next_to(head, DOWN, buff=top).to_edge(LEFT, buff=SAFE)
            self.no_overlap(side, body)
            self.no_overlap(head, side)
            self.validator.check_in_frame(side)
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
        if getattr(self, "side", None) is None:
            rows = VGroup(*[VGroup(pill(str(i + 1), color, size=SMALL), text(what, LABEL, INK), text(result, LABEL, GOOD, BOLD))
                            .arrange(RIGHT, buff=0.3) for i, (what, result) in enumerate(steps)])
            return rows.arrange(DOWN, buff=0.5, aligned_edge=LEFT)
        rows = VGroup()                          # beside a formula panel: long lines wrap, a long result drops below
        for i, (what, result) in enumerate(steps):
            chip = pill(str(i + 1), color, size=SMALL)
            row = VGroup(chip, fitted_text(what, self.body_w() - chip.width - 0.3, LABEL, INK, max_lines=2),
                         text(result, LABEL, GOOD, BOLD)).arrange(RIGHT, buff=0.3)
            if row.width > self.body_w():
                row[1].align_to(chip, UP)
                row[2].next_to(row[1], DOWN, buff=0.15, aligned_edge=LEFT)
            rows.add(row)
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
        level_cols = {"L1": WORD, "L2": WORD, "L3": WORD}
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

    SIDE_W = 4.3                                  # width of the formula panel kept on the left of an example

    def side_panel(self, lines, title="Formula"):
        """The main formula(s) for the example on screen, in a panel that stays on the left
        while the working builds up on the right.  ``stack`` lays the example out beside it."""
        # a line that already has its own line breaks is kept as written (formulas break at the operators)
        rows = VGroup(*[text(s, LABEL, INK, BOLD) if chr(10) in s else
                        fitted_text(s, self.SIDE_W - 0.7, LABEL, INK, BOLD, max_lines=4) for s in lines])
        scale = min(1.0, *[(self.SIDE_W - 0.7) / r.width for r in rows])
        for r in rows:                           # every formula line at the same size
            r.scale(scale)
        rows.arrange(DOWN, buff=0.35, aligned_edge=LEFT)
        content = VGroup(text(title, SMALL, MUTED, BOLD), rows).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        panel = self.card(content, width=self.SIDE_W, color=FOCUS)
        panel.to_edge(LEFT, buff=SAFE).set_y(CARD_TOP - 1.3 - panel.height / 2)
        self.side = panel
        return panel

    def body_w(self):
        """Width left for the content of the screen (narrower beside a formula panel)."""
        return SAFE_W if getattr(self, "side", None) is None else SAFE_W - self.SIDE_W - 0.4
    def step_rows(self, items, color=WORD):
        """Numbered concept steps.  Each row = (number chip, the step[, a short note in green])."""
        rows = VGroup()
        for i, (what, note) in enumerate(items):
            row = VGroup(pill(str(i + 1), color, size=SMALL), text(what, LABEL, INK, BOLD))
            if note:
                row.add(text(note, LABEL, GOOD, BOLD))
            rows.add(row.arrange(RIGHT, buff=0.35))
        return fit_width(rows.arrange(DOWN, buff=0.5, aligned_edge=LEFT), SAFE_W - 0.6)

    def pattern_blocks(self, patterns):
        """Each exam pattern as two lines: name + example, then method + answer.  block[0], block[1]."""
        blocks = VGroup()
        for name, example, method, answer in patterns:
            first = VGroup(text(name, LABEL, WORD, BOLD), text(example, LABEL, INK)).arrange(RIGHT, buff=0.5)
            second = VGroup(text(method, LABEL, MUTED), text(answer, LABEL, GOOD, BOLD)).arrange(RIGHT, buff=0.6)
            blocks.add(fit_width(VGroup(first, second).arrange(DOWN, buff=0.2, aligned_edge=LEFT), SAFE_W - 0.8))
        return blocks

    def cross_diagram(self, low, high, mid, d_low, d_high):
        """The alligation cross: the two values on top, the mean in the middle, the differences below.
        Returns VGroup(top row, mean, bottom row)."""
        top = VGroup(pill(low, WORD, size=BODY), pill(high, WORD, size=BODY)).arrange(RIGHT, buff=2.6)
        mean = pill(mid, FOCUS, size=BODY)
        bottom = VGroup(text(d_low, BODY, GOOD, BOLD), text(d_high, BODY, GOOD, BOLD)).arrange(RIGHT, buff=2.6)
        group = VGroup(top, mean, bottom).arrange(DOWN, buff=0.35)
        bottom[0].set_x(top[0].get_x())
        bottom[1].set_x(top[1].get_x())
        self.no_overlap(top, mean, bottom)
        return group

    # ============================================== 0. INTRO ==========
    # Not the first video: silent breadcrumb, a one-line recap of the previous video, then today's topic.

    def intro(self):
        self.scene_start("S00_intro", title="Intro")

        crumb = self.breadcrumb("Quantitative Aptitude", "Lesson 25 · Alligation & Mixtures", "Video 2 of 7")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        recap = VGroup(text("last video", SMALL, MUTED), pill("value of a mixture  =  total value ÷ total quantity", WORD, size=LABEL)).arrange(DOWN, buff=0.25)
        title = fit_width(text("Alligation Rule", TITLE, INK, BOLD), SAFE_W - 0.4)
        today = text("today: from the mean back to the ratio, in one cross", LABEL, FOCUS)
        block = VGroup(recap, title, today).arrange(DOWN, buff=0.7)
        fit_within(block, SAFE_W, SAFE_H - crumb.height - 0.9)
        block.next_to(crumb, DOWN, buff=0.7)
        self.no_overlap(crumb, recap, title, today)
        self.validator.check_in_frame(VGroup(crumb, block))

        n = self.narrate(
            id="intro_01",
            text="In the last video, the value of a mixture was its total value divided by its total quantity.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.at_word(n, "divided")
        self.play(FadeIn(recap, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="intro_02",
            text="Today: the alligation rule, which goes from the mean back to the ratio, in one cross.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "alligation")
        self.play(FadeIn(title, shift=UP * 0.1))
        self.at_word(n, "cross")
        self.play(FadeIn(today, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_intro")

    # ============================================== 1. HOOK ==========

    def hook(self):
        self.scene_start("S01_hook", title="Hook")

        head = self.heading("The rice blend")
        packs = VGroup(pill("rice at ₹40 a kg", WORD, size=LABEL), pill("rice at ₹60 a kg", WORD, size=LABEL)).arrange(RIGHT, buff=0.5)
        ask = pill("In what ratio should they be mixed to make ₹48 a kg?", FOCUS, size=BODY)
        slow = text("you could let the quantities be x and y and solve an equation", LABEL, MUTED)
        fast = text("the alligation rule gives the ratio with two subtractions", LABEL, INK, BOLD)
        self.stack(head, [packs, ask, slow, fast], buff=0.6, top=0.8)
        self.no_overlap(*packs)

        n = self.narrate(
            id="hook_01",
            text="A shopkeeper has rice at forty rupees a kilogram and rice at sixty rupees a kilogram.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "forty")
        self.play(FadeIn(packs[0], shift=UP * 0.1))
        self.at_word(n, "sixty")
        self.play(FadeIn(packs[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_02",
            text="In what ratio should they be mixed to make a blend worth forty-eight rupees a kilogram?",
            voice="default",
            subtitle=True,
            pause_after=3.0,
        )
        self.at_word(n, "ratio")
        self.play(FadeIn(ask, scale=1.03))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="hook_03",
            text="You could let the quantities be x and y and solve an equation. The alligation rule gives the ratio with "
                 "two subtractions.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "equation")
        self.play(FadeIn(slow, shift=UP * 0.1))
        self.at_word(n, "subtractions")
        self.play(FadeIn(fast, shift=UP * 0.1))
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
            id="objectives_01",
            text="By the end of this video, you will be able to do three things.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "three")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="objectives_02",
            text="First, set up the alligation cross for two values and the mean of their mixture.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "cross")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "mean")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="objectives_03",
            text="Second, read the ratio off the cross: cheaper to dearer is H minus M to M minus L.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "read")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "cheaper")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="objectives_04",
            text="Third, use it for prices, concentrations and averages, and know when it does not apply.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "prices")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "apply")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_objectives")

    # ============================================== 3. WHY THIS MATTERS ==========

    def why_this_matters(self):
        self.scene_start("S03_why_this_matters", title="Why This Matters")

        head = self.heading("Why this matters")
        short = pill("alligation is a shortcut for balancing two quantities around a target average", FOCUS, size=LABEL)
        pair = VGroup(text("the cheaper item is paired with the target's distance from the dearer one", LABEL, INK),
                      text("and the dearer item with the target's distance from the cheaper one", LABEL, INK)).arrange(DOWN, buff=0.3)
        often = text("“in what ratio must they be mixed” is the most common mixture question", LABEL, MUTED)
        self.stack(head, [short, pair, often], buff=0.9, top=1.1)

        n = self.narrate(
            id="why_this_matters_01",
            text="Alligation is a shortcut for balancing two quantities around a target average.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "shortcut")
        self.play(FadeIn(short, scale=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="why_this_matters_02",
            text="The cheaper item is paired with the target's distance from the dearer one, and the dearer item with the "
                 "distance from the cheaper one.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "cheaper")
        self.play(FadeIn(pair[0], shift=UP * 0.1))
        self.at_word(n, "dearer", occurrence=2)
        self.play(FadeIn(pair[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="why_this_matters_03",
            text="In what ratio must they be mixed is the most common mixture question in the exam.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "common")
        self.play(FadeIn(often, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_why_this_matters")

    # ============================================== 4. CONCEPT - THE CROSS ==========

    def the_cross(self):
        self.scene_start("S04_the_cross", title="Concept - The Cross")

        head = self.heading("The alligation cross")
        blocks = two_line_blocks(STEPS_A, WORD)
        self.stack(head, list(blocks), buff=0.5, top=0.7, align=LEFT)

        n = self.narrate(
            id="the_cross_01",
            text="The rule comes from the balance of a weighted average. The quantity at L times M minus L equals the "
                 "quantity at H times H minus M, so the quantities are in the ratio H minus M to M minus L.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "balance")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "ratio")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="the_cross_02",
            text="Write the cross: L and H on top, M in the middle. Subtract along the diagonals: H minus M goes under L, "
                 "and M minus L goes under H.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "cross")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "diagonals")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="the_cross_03",
            text="Each quantity takes the other value's distance. The cheaper one gets the distance from the dearer value "
                 "to the mean.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "takes")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "gets")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="the_cross_04",
            text="The mean must lie between the two values. If it is outside them, no mixture of the two can reach it.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "between")
        self.play(FadeIn(blocks[3][0], shift=RIGHT * 0.2))
        self.at_word(n, "outside")
        self.play(FadeIn(blocks[3][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_the_cross")

    # ============================================== 5. CONCEPT - WHERE IT WORKS ==========

    def using_it(self):
        self.scene_start("S05_using_it", title="Concept - Where It Works")

        head = self.heading("Where the cross works")
        blocks = two_line_blocks(STEPS_B, WORD)
        self.stack(head, list(blocks), buff=0.5, top=0.7, align=LEFT)

        n = self.narrate(
            id="using_it_01",
            text="Use the same units on both sides: rupees a kilogram with rupees a kilogram, percent with percent. The "
                 "answer is a ratio of quantities.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "units")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "answer")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="using_it_02",
            text="It works for anything that is averaged: prices, percentages, average marks, average speeds.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "averaged")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "prices")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="using_it_03",
            text="Water is zero, and a pure ingredient is one hundred percent. Water and milk worth sixty rupees a litre, "
                 "making forty-five: fifteen to forty-five, one to three.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "zero")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "fifteen")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="using_it_04",
            text="With profit, first find the cost price of the mixture. The mean in the cross is always a cost, never a "
                 "selling price.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "profit")
        self.play(FadeIn(blocks[3][0], shift=RIGHT * 0.2))
        self.at_word(n, "never")
        self.play(FadeIn(blocks[3][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_using_it")

    # ============================================== 6. FORMULA BOX ==========

    def formula_box(self):
        self.scene_start("S06_formula_box", title="Formula Box")

        head = self.heading("Formula box", GOOD)
        lines = VGroup(*[text(f, LABEL, INK) for f in FORMULAS]).arrange(DOWN, buff=0.45, aligned_edge=LEFT)
        fit_width(lines, SAFE_W - 1.6)
        box = self.card(lines, width=SAFE_W - 0.4, color=GOOD, pad=0.5)
        self.stack(head, [box], top=0.7)

        n = self.narrate(
            id="formula_box_01",
            text="Here is the formula box. The quantity at L to the quantity at H is H minus M to M minus L.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "box")
        self.play(FadeIn(box[0]))
        self.at_word(n, "quantity")
        self.play(FadeIn(lines[0], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_box_02",
            text="In the cross, L and H are on top, M is in the middle, and the differences run along the diagonals.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "cross")
        self.play(FadeIn(lines[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_box_03",
            text="Check by putting the ratio back into the weighted average.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Check")
        self.play(FadeIn(lines[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_box_04",
            text="Water is zero, pure is one hundred percent, and M lies between L and H.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Water")
        self.play(FadeIn(lines[3], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_box_05",
            text="And when the mixture is sold at a profit, M is the selling price divided by one plus the profit rate.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "profit")
        self.play(FadeIn(lines[4], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_formula_box")

    # ============================================== 7. THE ANALOGY - A BALANCE SCALE ==========

    def analogy(self):
        self.scene_start("S07_analogy", title="The Analogy - A Balance Scale")

        head = self.heading("A balance scale")
        beam = VGroup(pill("₹40", WORD, size=BODY), text("8 away", LABEL, MUTED), pill("pivot:  ₹48", FOCUS, size=BODY),
                      text("12 away", LABEL, MUTED), pill("₹60", WORD, size=BODY)).arrange(RIGHT, buff=0.45)
        rule = text("the weight that hangs nearer the pivot must be the heavier one", LABEL, INK, BOLD)
        nums = text("so the weights are 12 on the ₹40 side and 8 on the ₹60 side:    3 : 2", LABEL, GOOD, BOLD)
        stops = VGroup(text("Where the analogy stops", LABEL, BAD, BOLD),
                       text("a scale can balance with the pivot anywhere on the beam", LABEL, INK),
                       text("a mixture cannot:  the mean is always between the two values", LABEL, MUTED)).arrange(DOWN, buff=0.2)
        self.stack(head, [beam, rule, nums, stops], buff=0.55, top=0.7)
        self.no_overlap(*beam)

        n = self.narrate(
            id="analogy_01",
            text="Alligation is a balance scale. The target, forty-eight, is the pivot; forty hangs eight away on one "
                 "side, and sixty hangs twelve away on the other.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "scale")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "pivot")
        self.play(FadeIn(beam, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_02",
            text="A target between two values can be reached only by putting more weight on the side nearer the target. So "
                 "the weights are twelve on the forty side and eight on the sixty side: three to two.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "weight")
        self.play(FadeIn(rule, shift=UP * 0.1))
        self.at_word(n, "twelve")
        self.play(FadeIn(nums, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_03",
            text="Where the analogy stops: a scale can balance with the pivot anywhere on the beam. A mixture cannot: the "
                 "mean is always between the two values.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "stops")
        self.play(FadeIn(stops[0], shift=UP * 0.1))
        self.at_word(n, "anywhere")
        self.play(FadeIn(stops[1], shift=UP * 0.1))
        self.at_word(n, "always")
        self.play(FadeIn(stops[2], shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S07_analogy")

    # ============================================== 8. WORKED EXAMPLE - CLOSING THE HOOK ==========

    def hook_solved(self):
        self.scene_start("S08_hook_solved", title="Worked Example - Closing the Hook")

        head = self.heading("Rice at ₹40 and ₹60, making ₹48")
        panel = self.side_panel(["Cheaper : dearer  =\n(H − M) : (M − L)", "L = 40,   H = 60,   M = 48"])
        diagram = self.cross_diagram("₹40", "₹60", "₹48", "60 − 48 = 12", "48 − 40 = 8")
        steps = self.solve_steps([("Cheaper : dearer  =  12 : 8", "=  3 : 2"),
                                  ("Check:    (3 × 40 + 2 × 60)/5  =  240/5", "=  ₹48")])
        self.stack(head, [diagram, steps], buff=0.6, top=0.6)
        self.no_overlap(*steps)

        n = self.narrate(
            id="hook_solved_01",
            text="Write forty and sixty on top, and the mean, forty-eight, in the middle.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(panel, shift=RIGHT * 0.2))
        self.at_word(n, "forty")
        self.play(FadeIn(diagram[0], shift=UP * 0.1))
        self.at_word(n, "mean")
        self.play(FadeIn(diagram[1], scale=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_solved_02",
            text="Subtract along the diagonals: sixty minus forty-eight is twelve, under the forty; forty-eight minus "
                 "forty is eight, under the sixty.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "twelve")
        self.play(FadeIn(diagram[2][0], shift=UP * 0.1))
        self.at_word(n, "eight")
        self.play(FadeIn(diagram[2][1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_solved_03",
            text="So cheaper to dearer is twelve to eight: three to two.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "cheaper")
        self.play(FadeIn(steps[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "three")
        self.play(FadeIn(steps[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_solved_04",
            text="Check: three times forty plus two times sixty is two hundred and forty, and divided by five that is "
                 "forty-eight.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Check")
        self.play(FadeIn(steps[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "divided")
        self.play(FadeIn(steps[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S08_hook_solved")

    # ============================================== 9. A SECOND WORKED EXAMPLE - TWO STRENGTHS ==========

    def second_example(self):
        self.scene_start("S09_second_example", title="A Second Worked Example - Two Strengths")

        head = self.heading("20% and 50%, making 30%")
        panel = self.side_panel(["Weaker : stronger  =\n(H − M) : (M − L)", "L = 20%,   H = 50%,\nM = 30%"])
        ask = fitted_text("in what ratio must a 20% solution and a 50% solution be mixed to make a 30% solution?", self.body_w() - 0.2, LABEL, MUTED, max_lines=3)
        diagram = self.cross_diagram("20%", "50%", "30%", "50 − 30 = 20", "30 − 20 = 10")
        steps = self.solve_steps([("Weaker : stronger  =  20 : 10", "=  2 : 1"),
                                  ("Check:    (2 × 20 + 1 × 50)/3  =  90/3", "=  30%")])
        self.stack(head, [ask, diagram, steps], buff=0.5, top=0.6)
        self.no_overlap(*steps)

        n = self.narrate(
            id="second_example_01",
            text="In what ratio must a twenty percent solution and a fifty percent solution be mixed to make a thirty "
                 "percent solution?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "ratio")
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(panel, shift=RIGHT * 0.2))
        self.at_word(n, "mixed")
        self.play(FadeIn(ask, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_02",
            text="Twenty and fifty go on top, thirty in the middle.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "top")
        self.play(FadeIn(diagram[0], shift=UP * 0.1))
        self.at_word(n, "middle")
        self.play(FadeIn(diagram[1], scale=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_03",
            text="Fifty minus thirty is twenty, under the weaker; thirty minus twenty is ten, under the stronger.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "weaker")
        self.play(FadeIn(diagram[2][0], shift=UP * 0.1))
        self.at_word(n, "stronger")
        self.play(FadeIn(diagram[2][1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_04",
            text="So weaker to stronger is twenty to ten: two to one.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "So")
        self.play(FadeIn(steps[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "two")
        self.play(FadeIn(steps[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_05",
            text="Check: two times twenty plus fifty is ninety, and divided by three that is thirty percent.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Check")
        self.play(FadeIn(steps[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "divided")
        self.play(FadeIn(steps[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S09_second_example")

    # ============================================== 10. EXAM PATTERNS - HOW THIS IS ASKED ==========

    def exam_patterns(self):
        self.scene_start("S10_exam_patterns", title="Exam Patterns - How This Is Asked")

        head = self.heading("Exam patterns  ·  1 to 3 of 6")
        blocks = self.pattern_blocks(PATTERNS[0:3])
        self.stack(head, list(blocks), buff=0.6, top=0.8, align=LEFT)

        n = self.narrate(
            id="exam_patterns_01",
            text="Exams ask this in six ways.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "six")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_02",
            text="Two prices: forty and sixty rupees, making forty-eight. Twelve to eight: three to two.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "prices")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "Twelve")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_03",
            text="Two strengths: twenty percent and fifty percent, making thirty. Twenty to ten: two to one.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "strengths")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "ten")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_04",
            text="Water: water and milk at sixty rupees a litre, making forty-five. Fifteen to forty-five: one to three.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "milk")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "Fifteen")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Exam patterns  ·  4 to 6 of 6")
        blocks = self.pattern_blocks(PATTERNS[3:6])
        self.stack(head, list(blocks), buff=0.6, top=0.8, align=LEFT)

        n = self.narrate(
            id="exam_patterns_05",
            text="Sold at a profit: tea at fifty and sixty-five rupees, sold at sixty-six with ten percent profit. The "
                 "cost is sixty, so five to ten: one to two.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "profit")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "cost")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_06",
            text="Averages: boys average seventy, girls eighty-five, and the class seventy-six. Nine to six: three to two.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Averages")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "Nine")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_07",
            text="The mean in the middle: twenty and forty rupees, making thirty. Ten to ten: one to one.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "middle")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "Ten")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S10_exam_patterns")

    # ============================================== 11. TRAPS AND CONFUSING QUESTIONS ==========

    def traps(self):
        self.scene_start("S11_traps", title="Traps and Confusing Questions")

        head, q, wrong, right, rule = self.show_trap(TRAPS[0])

        n = self.narrate(
            id="traps_01",
            text="Trap one: the differences on the wrong side. Rice at forty and sixty rupees is mixed to make "
                 "forty-eight: find the ratio of cheaper to dearer.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "wrong")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "mixed")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_02",
            text="The wrong instinct writes eight to twelve, two to three. The correct answer crosses over: twelve to "
                 "eight, three to two.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "instinct")
        self.play(FadeIn(wrong, shift=UP * 0.1))
        self.at_word(n, "correct")
        self.play(FadeIn(right, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_03",
            text="The rule: cross over, so the cheaper takes H minus M. The mean is nearer forty, so there must be more of "
                 "it.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "rule")
        self.play(FadeIn(rule, shift=UP * 0.1))
        self.at_word(n, "nearer")
        self.play(Indicate(rule, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)
        self.clear_stage()

        head, q, wrong, right, rule = self.show_trap(TRAPS[1])

        n = self.narrate(
            id="traps_04",
            text="Trap two: the selling price used as the mean. Tea at fifty and sixty-five rupees is mixed and sold at "
                 "sixty-six rupees with ten percent profit: find the ratio.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "selling")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "mixed")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_05",
            text="The wrong instinct uses sixty-six as the mean, which is not even between fifty and sixty-five. The "
                 "correct working finds the cost, sixty-six divided by one point one, sixty, and gets one to two.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "wrong")
        self.play(FadeIn(wrong, shift=UP * 0.1))
        self.at_word(n, "correct")
        self.play(FadeIn(right, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_06",
            text="The rule: remove the profit first. The mean in the cross is the cost price.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "rule")
        self.play(FadeIn(rule, shift=UP * 0.1))
        self.at_word(n, "cost")
        self.play(Indicate(rule, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)
        self.clear_stage()

        head, q, wrong, right, rule = self.show_trap(TRAPS[2])

        n = self.narrate(
            id="traps_07",
            text="Trap three: the cross used when the quantities are given. Two kilograms at forty rupees is mixed with "
                 "three kilograms at sixty: find the price of the mixture.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "quantities")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "mixed")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_08",
            text="The wrong instinct reaches for a cross, with no mean to put in it. The correct answer is eighty plus one "
                 "hundred and eighty, over five: fifty-two rupees.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "wrong")
        self.play(FadeIn(wrong, shift=UP * 0.1))
        self.at_word(n, "correct")
        self.play(FadeIn(right, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_09",
            text="The rule: alligation finds a ratio from a mean. To find a mean from quantities, use the weighted "
                 "average.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "rule")
        self.play(FadeIn(rule, shift=UP * 0.1))
        self.at_word(n, "weighted")
        self.play(Indicate(rule, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S11_traps")

    # ============================================== 12. CHECKPOINT ==========

    def checkpoint(self):
        self.scene_start("S12_checkpoint", title="Checkpoint")

        head = self.heading("Checkpoint  ·  your turn")
        given = pill("mix ₹30 a kg and ₹50 a kg to make ₹38 a kg:   ratio of cheaper to dearer?", FOCUS, size=LABEL)
        work = VGroup(text("(50 − 38) : (38 − 30)  =  12 : 8", BODY, INK, BOLD), text("=  3 : 2", BODY, GOOD, BOLD)).arrange(RIGHT, buff=0.6)
        self.stack(head, [given, work], buff=1.0, top=1.0)
        self.no_overlap(*work)

        n = self.narrate(
            id="checkpoint_01",
            text="Your turn. Mix thirty rupees a kilogram and fifty rupees a kilogram to make thirty-eight. What is the "
                 "ratio of cheaper to dearer?",
            voice="default",
            subtitle=True,
            pause_after=10.0,
        )
        self.at_word(n, "turn")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "Mix")
        self.play(FadeIn(given, scale=1.03))
        self.at_word(n, "ratio")
        self.play(Indicate(given, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="checkpoint_02",
            text="Fifty minus thirty-eight is twelve, and thirty-eight minus thirty is eight: twelve to eight, three to "
                 "two.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "minus")
        self.play(FadeIn(work[0], shift=UP * 0.1))
        self.at_word(n, "three")
        self.play(FadeIn(work[1], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S12_checkpoint")

    # ============================================== 13. PRACTICE QUESTIONS ==========

    def practice(self):
        self.scene_start("S13_practice", title="Practice Questions")

        head = self.heading("Practice  ·  Levels 1 and 2")
        table, rows = self.practice_table(head, PRACTICE_A, 1)

        n = self.narrate(
            id="practice_01",
            text="Level one, question one: in what ratio must twenty and forty rupee varieties be mixed to make thirty? "
                 "Question two: in what ratio must ten percent and forty percent solutions be mixed to make twenty-five "
                 "percent?",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "varieties")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "solutions")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="practice_02",
            text="Level two, question three: sugar at thirty and fifty rupees is mixed to make forty-two; find cheaper to "
                 "dearer. Question four: rice at forty and sixty rupees is mixed to make forty-eight; find cheaper to "
                 "dearer. Question five: in what ratio must water be mixed with milk worth forty-eight rupees a litre to "
                 "make a mixture worth forty?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "sugar")
        self.play(FadeIn(rows[2], shift=RIGHT * 0.2))
        self.at_word(n, "rice")
        self.play(FadeIn(rows[3], shift=RIGHT * 0.2))
        self.at_word(n, "water")
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
        self.play(Indicate(head, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)
        self.clear_stage()

        head = self.heading("Practice  ·  Level 3")
        table, rows = self.practice_table(head, PRACTICE_B, 6)

        n = self.narrate(
            id="practice_04",
            text="Level three, question six: in what ratio must fifteen percent and forty percent acid be mixed to make "
                 "thirty percent? Question seven: tea at fifty-two and seventy-two rupees is mixed and sold at sixty-nine "
                 "rupees, a profit of fifteen percent; find cheaper to dearer. Question eight: boys average sixty marks, "
                 "girls average seventy-five, and the whole class averages sixty-five; find the ratio of boys to girls.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "acid")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "tea")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.at_word(n, "boys")
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
        self.play(Indicate(head, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        self.clear_stage()
        self.scene_end("S13_practice")

    # ============================================== 14. ANSWER KEY, WITH REASONING ==========

    def answers(self):
        self.scene_start("S14_answers", title="Answer Key, with Reasoning")

        head = self.heading("Answer key  ·  1 to 4", GOOD)
        table, rows = self.answer_table(head, ANSWERS_A, 1)

        n = self.narrate(
            id="answers_01",
            text="One: forty minus thirty to thirty minus twenty, ten to ten: one to one.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "minus")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "one", occurrence=2)
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_02",
            text="Two: fifteen to fifteen: one to one.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "fifteen")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "one")
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_03",
            text="Three: fifty minus forty-two to forty-two minus thirty, eight to twelve: two to three.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "minus")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "two")
        self.play(FadeIn(rows[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_04",
            text="Four: the hook again, twelve to eight: three to two.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "hook")
        self.play(FadeIn(rows[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "three")
        self.play(FadeIn(rows[3][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Answer key  ·  5 to 8", GOOD)
        table, rows = self.answer_table(head, ANSWERS_B, 5)

        n = self.narrate(
            id="answers_05",
            text="Five: water is zero, so forty-eight minus forty to forty minus zero, eight to forty: one to five.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "zero")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "five", occurrence=2)
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_06",
            text="Six: forty minus thirty to thirty minus fifteen, ten to fifteen: two to three.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "minus")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "two")
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_07",
            text="Seven: the cost is sixty-nine divided by one point one five, sixty. Seventy-two minus sixty to sixty "
                 "minus fifty-two, twelve to eight: three to two.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "cost")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "three")
        self.play(FadeIn(rows[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_08",
            text="Eight: seventy-five minus sixty-five to sixty-five minus sixty, ten to five: two boys to one girl.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "minus")
        self.play(FadeIn(rows[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "boys")
        self.play(FadeIn(rows[3][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S14_answers")

    # ============================================== 15. EXAM LENS - RECOGNISE AND MOVE ==========

    def exam_lens(self):
        self.scene_start("S15_exam_lens", title="Exam Lens - Recognise and Move")

        head = self.heading("Exam lens: recognise and move")
        blocks = two_line_blocks(LENS, RATIO)
        self.stack(head, list(blocks), buff=0.6, top=0.8, align=LEFT)

        n = self.narrate(
            id="exam_lens_01",
            text="Recognise and move. The recognition cue: in what ratio must they be mixed, with two values and the value "
                 "of the mixture given.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "cue")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "ratio")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_lens_02",
            text="The target time: twenty to thirty seconds.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "target")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "seconds")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_lens_03",
            text="The sanity check: there is more of the ingredient whose value is nearer the mean; put the ratio back "
                 "into the average.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "sanity")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "more")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S15_exam_lens")

    # ============================================== 16. QUICK REVISION AND SUMMARY ==========

    def summary(self):
        self.scene_start("S16_summary", title="Quick Revision and Summary")

        head = self.heading("Quick revision")
        main = pill("quantity at L : quantity at H   =   (H − M) : (M − L)", GOOD, size=LABEL)
        row = VGroup(pill("cross over the differences", WORD, size=SMALL), pill("water = 0,  pure = 100%", WORD, size=SMALL),
                     pill("the mean is a cost price", WORD, size=SMALL)).arrange(RIGHT, buff=0.3)
        fit_width(row, SAFE_W - 0.4)
        scale = text("the balance scale:  more weight on the side nearer the mean", LABEL, MUTED)
        nxt = self.breadcrumb("Next", "Video 3 · Mixing Two Quantities")
        self.stack(head, [main, row, scale, nxt], buff=0.75, top=0.9)
        self.no_overlap(*row)

        n = self.narrate(
            id="summary_01",
            text="The quantity at L to the quantity at H is H minus M to M minus L.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "quantity")
        self.play(FadeIn(main, scale=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_02",
            text="Cross over the differences, treat water as zero and pure as one hundred percent, and always use a cost "
                 "price as the mean.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Cross")
        self.play(FadeIn(row[0], shift=UP * 0.1))
        self.at_word(n, "water")
        self.play(FadeIn(row[1], shift=UP * 0.1))
        self.at_word(n, "cost")
        self.play(FadeIn(row[2], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_03",
            text="Remember the balance scale: more weight on the side nearer the mean.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "scale")
        self.play(FadeIn(scale, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_04",
            text="Next: mixing two quantities.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Next")
        self.play(FadeIn(nxt, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S16_summary")

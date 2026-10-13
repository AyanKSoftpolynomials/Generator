"""
animation.py for the LMS video generator.

Course : Pre-C-CAT - Section A - Quantitative Aptitude
Video  : Lesson 25 - Alligation & Mixtures - 04 - Replacement Problems

Source script:
  C:\\Scripts\\Section A\\Module2\\S21-25_Ratio_Age_Clock_Mixtures_Mensuration\\Lesson 25 - Allegation & Mixtures\\02 - Replacement Problems.pdf

Built on the golden-reference pattern:
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``;
  * layouts stacked with next_to and guarded with ``no_overlap``; nothing is
    ever animated onto or into another box.

Lesson 25, Video 4 of 7 (the lesson's own order, from its Pre-Lesson Brief). Not the first video of the lesson: a silent
breadcrumb, a one-line recap of Video 3, then today's topic. No spoken course welcome.
The seven source scripts of this lesson are identical apart from their titles, so, as agreed with the course owner, each video was
written for its own topic. This one covers a single removal and refill: the script's rule "after removing fraction r of a mixture,
original fraction left = 1 - r", its examples (10 L tank, remove 2 L: 4/5;  20 L, remove 5 L: 3/4) and its trap about using the
removed fraction, with further verified questions. Repeated replacement is the next video.
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


def left(total, removed):
    """Fraction of every ingredient that stays when ``removed`` is drawn from ``total``."""
    return 1 - F(removed, total)


# ---- hook, examples, patterns ----
assert left(20, 5) == F(3, 4) and 20 * left(20, 5) == 15 and left(10, 2) == F(4, 5)
MILK, WATER = 30 * left(40, 8), 10 * left(40, 8) + 8
assert (MILK, WATER) == (24, 16) and F(MILK, WATER) == F(3, 2)
assert 60 * F(80, 100) == 48 and 60 - 48 == 12 and left(60, 12) == F(4, 5)
assert 10 * left(40, 8) == 8 and 30 * left(40, 8) + 8 == 32 and F(32, 8) == 4
assert F(30, 40) == left(50, F(25, 2)) and 50 * F(3, 5) == 30 and 40 * left(25, 5) == 32
# ---- traps and checkpoint ----
assert 30 - 8 == 22 and 30 * left(30, 6) == 24 and F(24, 30) == F(4, 5) and F(15, 15) == 1
# ---- practice ----
assert 50 * left(50, 10) == 40 and 50 * left(60, 15) == F(75, 2)
assert 60 * left(80, 20) == 45 and 80 - 45 == 35 and F(45, 35) == F(9, 7)
assert 40 * F(70, 100) == 28 and 40 - 28 == 12
assert 6 * left(36, 12) == 4 and 36 - 4 == 32 and F(32, 4) == 8
assert left(100, 20) * 30 == 24
V = 63
assert F(7, 12) * V * left(V, 9) == F(V, 2)

OBJECTIVES = [("Find what is left of each ingredient", "after part of a mixture is removed"),
              ("Handle a refill with water, or with one of the ingredients", "and give the new ratio or strength"),
              ("Work backwards", "to the amount that must be replaced to reach a target")]
STEPS_A = [("A removed part takes every ingredient in the same proportion", "draw 8 L from 40 L and you remove 1/5 of the milk and 1/5 of the water"),
           ("Fraction left  =  1 − removed/total", "remove 5 L from 20 L:    1 − 5/20  =  3/4 of every ingredient stays"),
           ("Refilling brings the volume back to full", "but only the ingredient you pour in gains anything"),
           ("Refilled with water:  the original liquid only falls", "amount left  =  starting amount × (1 − removed/total)")]
STEPS_B = [("Start from a mixture:  apply the fraction to each ingredient", "40 L with milk : water 3 : 1;   8 L out:    milk 30 × 4/5 = 24,   water 10 × 4/5 = 8"),
           ("Then add the refill to the right ingredient", "refilled with water:    water 8 + 8 = 16;    milk : water  =  24 : 16  =  3 : 2"),
           ("Strength falls by the same fraction", "25 L of 40% acid, 5 L replaced by water:    40% × 4/5  =  32%"),
           ("Backwards:  fraction left  =  target ÷ start", "60 L of pure milk down to 80%:    4/5 stays, so 1/5 of 60 L  =  12 L is replaced")]
FORMULAS = ["Fraction left of every ingredient   =   1 − removed/total",
            "Refilled with water:      liquid left  =  starting amount × (1 − removed/total)",
            "Refilled with an ingredient:      it becomes  (its amount × fraction left) + the refill",
            "New strength   =   old strength × (1 − removed/total)        (refilled with water)",
            "Backwards:      1 − removed/total   =   target ÷ start"]
PATTERNS = [("Pure liquid, replaced once", "10 L tank;  2 L removed and refilled with water", "1 − 2/10", "4/5 is left"),
            ("Mixture, refilled with water", "40 L, milk : water 3 : 1;  8 L replaced by water", "milk 24,  water 8 + 8 = 16", "3 : 2"),
            ("Mixture, refilled with milk", "40 L, milk : water 3 : 1;  8 L replaced by milk", "water 8,  milk 24 + 8 = 32", "4 : 1"),
            ("Strength", "25 L of 40% acid;  5 L replaced by water", "40% × 4/5", "32%"),
            ("Find the amount replaced", "60 L of pure milk;  how much replaced to get 80%?", "4/5 stays;    1/5 of 60 L", "12 L"),
            ("Reach a ratio", "50 L, milk : water 4 : 1;  replace with water to get 3 : 2", "milk 40 to 30:   3/4 stays", "12.5 L")]
TRAPS = [("Trap 1  ·  the removed fraction used as the fraction left",
          "5 L is removed from a 20 L tank of juice and replaced with water.  What fraction is juice?",
          "5/20  =  1/4", "1 − 5/20  =  3/4",
          "The question asks what stays.  Use the fraction left, 1 − removed/total."),
         ("Trap 2  ·  the whole removal taken from one ingredient",
          "8 L is drawn from 40 L of milk and water in the ratio 3 : 1.  How much milk is left?",
          "30 − 8  =  22 L", "30 × 4/5  =  24 L",
          "A removed part is a mixture too.  Take the same fraction from each ingredient."),
         ("Trap 3  ·  the refill forgotten",
          "5 L is removed from 20 L of pure juice and replaced with water.  What percent is juice now?",
          "15 L of 15 L:  100%", "15 L of 20 L:  75%",
          "After the refill the vessel is full again.  Divide by the full volume.")]
PRACTICE_A = [("L1", "5 L is removed from a 20 L mixture and replaced with water.  What fraction of the original mixture is left?"),
              ("L1", "10 L is removed from 50 L of pure milk and replaced with water.  How much milk is left?"),
              ("L2", "15 L is removed from 60 L of a 50% acid solution and replaced with water.  Find the new strength."),
              ("L2", "80 L of milk and water is in the ratio 3 : 1.  20 L is removed and replaced with water.  Find the new ratio."),
              ("L2", "How much of 40 L of pure milk must be replaced with water to leave a mixture that is 70% milk?")]
PRACTICE_B = [("L3", "36 L of milk and water is in the ratio 5 : 1.  12 L is removed and replaced with milk.  Find the new ratio."),
              ("L3", "How much of 100 L of a 30% acid solution must be replaced with water to make it 24%?"),
              ("L3", "Milk : water is 7 : 5 in a full vessel.  9 L is drawn and replaced with water, making them equal.  Find its capacity.")]
ANSWERS_A = [("1 − 5/20", "3/4"),
             ("50 × (1 − 10/50)  =  50 × 4/5", "40 L"),
             ("50% × (1 − 15/60)  =  50% × 3/4", "37.5%"),
             ("Milk  60 × 3/4 = 45;      water  80 − 45 = 35", "9 : 7")]
ANSWERS_B = [("Milk must be 28 L:    40 − 28", "12 L"),
             ("Water  6 × 2/3 = 4;      milk  36 − 4 = 32", "8 : 1"),
             ("Fraction left  =  24 ÷ 30  =  4/5;      1/5 of 100 L", "20 L"),
             ("Milk 7/12 × (1 − 9/V)  =  1/2;      1 − 9/V = 6/7;      9/V = 1/7", "63 L")]
LENS = [("Recognition cue", "“drawn off”, “taken out and replaced with water”, “removed and refilled”, done once"),
        ("Target time", "30 to 45 seconds"),
        ("Sanity check", "the ingredient you did not pour back only goes down;  the vessel ends full, so the parts add to the capacity")]


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


class ReplacementProblemsVideo(LMSScene):
    lesson_title = "Replacement Problems"

    def construct(self):
        self.camera.background_color = BG

        self.intro()
        self.hook()
        self.objectives()
        self.why_this_matters()
        self.fraction_left()
        self.mixtures_and_targets()
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

    # ============================================== 0. INTRO ==========
    # Not the first video: silent breadcrumb, a one-line recap of the previous video, then today's topic.

    def intro(self):
        self.scene_start("S00_intro", title="Intro")

        crumb = self.breadcrumb("Quantitative Aptitude", "Lesson 25 · Alligation & Mixtures", "Video 4 of 7")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        recap = VGroup(text("last video", SMALL, MUTED), pill("find the ratio with the cross, then scale it to amounts", WORD, size=LABEL)).arrange(DOWN, buff=0.25)
        title = fit_width(text("Replacement Problems", TITLE, INK, BOLD), SAFE_W - 0.4)
        today = text("today: take some out, pour something else in", LABEL, FOCUS)
        block = VGroup(recap, title, today).arrange(DOWN, buff=0.7)
        fit_within(block, SAFE_W, SAFE_H - crumb.height - 0.9)
        block.next_to(crumb, DOWN, buff=0.7)
        self.no_overlap(crumb, recap, title, today)
        self.validator.check_in_frame(VGroup(crumb, block))

        n = self.narrate(
            id="intro_01",
            text="In the last video, you found the ratio with the cross and then scaled it to actual amounts.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.at_word(n, "scaled")
        self.play(FadeIn(recap, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="intro_02",
            text="Today: replacement problems, where you take some out and pour something else in.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "replacement")
        self.play(FadeIn(title, shift=UP * 0.1))
        self.at_word(n, "pour")
        self.play(FadeIn(today, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_intro")

    # ============================================== 1. HOOK ==========

    def hook(self):
        self.scene_start("S01_hook", title="Hook")

        head = self.heading("The juice counter")
        tank = pill("a dispenser holds 20 L of pure juice", WORD, size=LABEL)
        act = pill("5 L is served, and the staff top it up with 5 L of water", WORD, size=LABEL)
        ask = pill("How much of the dispenser is still juice?", FOCUS, size=BODY)
        note = text("one subtraction answers it, and the same fraction works for any mixture", LABEL, INK, BOLD)
        self.stack(head, [tank, act, ask, note], buff=0.6, top=0.8)

        n = self.narrate(
            id="hook_01",
            text="A dispenser holds twenty litres of pure juice. Five litres is served, and the staff top it up with five "
                 "litres of water.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "dispenser")
        self.play(FadeIn(tank, shift=UP * 0.1))
        self.at_word(n, "served")
        self.play(FadeIn(act, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_02",
            text="How much of the dispenser is still juice?",
            voice="default",
            subtitle=True,
            pause_after=3.0,
        )
        self.at_word(n, "still")
        self.play(FadeIn(ask, scale=1.03))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="hook_03",
            text="One subtraction answers it, and the same fraction works for any mixture.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "subtraction")
        self.play(FadeIn(note, shift=UP * 0.1))
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
            text="First, find what is left of each ingredient after part of a mixture is removed.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "left")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "removed")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="objectives_03",
            text="Second, handle a refill with water, or with one of the ingredients, and give the new ratio or strength.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "refill")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "ratio")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="objectives_04",
            text="Third, work backwards to the amount that must be replaced to reach a target.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "backwards")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "target")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_objectives")

    # ============================================== 3. WHY THIS MATTERS ==========

    def why_this_matters(self):
        self.scene_start("S03_why_this_matters", title="Why This Matters")

        head = self.heading("Why this matters")
        diff = pill("replacement questions are different from mixing questions", FOCUS, size=LABEL)
        why = text("nothing is averaged:  part of the old mixture leaves, and something new comes in", LABEL, INK)
        key = text("everything depends on one number:  the fraction that stays", LABEL, INK, BOLD)
        nxt = text("it is also the base for repeated replacement, in the next video", LABEL, MUTED)
        self.stack(head, [diff, why, key, nxt], buff=0.8, top=1.1)

        n = self.narrate(
            id="why_this_matters_01",
            text="Replacement questions are different from mixing questions.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "different")
        self.play(FadeIn(diff, scale=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="why_this_matters_02",
            text="Nothing is averaged: part of the old mixture leaves, and something new comes in.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "averaged")
        self.play(FadeIn(why, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="why_this_matters_03",
            text="Everything depends on one number, the fraction that stays, and it is also the base for repeated "
                 "replacement in the next video.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "fraction")
        self.play(FadeIn(key, shift=UP * 0.1))
        self.at_word(n, "repeated")
        self.play(FadeIn(nxt, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_why_this_matters")

    # ============================================== 4. CONCEPT - THE FRACTION LEFT ==========

    def fraction_left(self):
        self.scene_start("S04_fraction_left", title="Concept - The Fraction Left")

        head = self.heading("The fraction left")
        blocks = two_line_blocks(STEPS_A, WORD)
        self.stack(head, list(blocks), buff=0.5, top=0.7, align=LEFT)

        n = self.narrate(
            id="fraction_left_01",
            text="A removed part takes every ingredient in the same proportion. Draw eight litres from forty litres, and "
                 "you remove one fifth of the milk and one fifth of the water.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "proportion")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "fifth")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="fraction_left_02",
            text="The fraction left is one minus the removed amount over the total. Remove five litres from twenty, and "
                 "three quarters of every ingredient stays.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "minus")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "quarters")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="fraction_left_03",
            text="Refilling brings the volume back to full, but only the ingredient you pour in gains anything.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Refilling")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "gains")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="fraction_left_04",
            text="So when the refill is water, the original liquid only falls: the amount left is the starting amount "
                 "times the fraction left.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "falls")
        self.play(FadeIn(blocks[3][0], shift=RIGHT * 0.2))
        self.at_word(n, "times")
        self.play(FadeIn(blocks[3][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_fraction_left")

    # ============================================== 5. CONCEPT - MIXTURES, STRENGTH AND TARGETS ==========

    def mixtures_and_targets(self):
        self.scene_start("S05_mixtures_and_targets", title="Concept - Mixtures, Strength and Targets")

        head = self.heading("Mixtures, strength, and targets")
        blocks = two_line_blocks(STEPS_B, WORD)
        self.stack(head, list(blocks), buff=0.5, top=0.7, align=LEFT)

        n = self.narrate(
            id="mixtures_and_targets_01",
            text="Starting from a mixture, apply the fraction to each ingredient. Forty litres with milk to water three to "
                 "one, and eight litres taken out: the milk is thirty times four fifths, twenty-four, and the water is ten "
                 "times four fifths, eight.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "each")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "twenty-four")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="mixtures_and_targets_02",
            text="Then add the refill to the right ingredient. Refilled with water, the water is eight plus eight, "
                 "sixteen, so milk to water is twenty-four to sixteen: three to two.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "refill")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "sixteen")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="mixtures_and_targets_03",
            text="Strength falls by the same fraction. Twenty-five litres of forty percent acid, with five litres replaced "
                 "by water: forty percent times four fifths is thirty-two percent.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Strength")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "thirty-two")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="mixtures_and_targets_04",
            text="Backwards, the fraction left is the target divided by the start. To bring sixty litres of pure milk down "
                 "to eighty percent, four fifths stays, so one fifth of sixty, twelve litres, is replaced.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Backwards")
        self.play(FadeIn(blocks[3][0], shift=RIGHT * 0.2))
        self.at_word(n, "twelve")
        self.play(FadeIn(blocks[3][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_mixtures_and_targets")

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
            text="Here is the formula box. The fraction left of every ingredient is one minus the removed amount over the "
                 "total.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "box")
        self.play(FadeIn(box[0]))
        self.at_word(n, "fraction")
        self.play(FadeIn(lines[0], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_box_02",
            text="Refilled with water, the liquid left is its starting amount times that fraction.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "water")
        self.play(FadeIn(lines[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_box_03",
            text="Refilled with an ingredient, that ingredient becomes its amount times the fraction left, plus the "
                 "refill.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "plus")
        self.play(FadeIn(lines[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_box_04",
            text="The new strength is the old strength times the fraction left.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "strength")
        self.play(FadeIn(lines[3], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_box_05",
            text="And backwards, the fraction left equals the target divided by the start.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "backwards")
        self.play(FadeIn(lines[4], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_formula_box")

    # ============================================== 7. THE ANALOGY - A BUS AT A STOP ==========

    def analogy(self):
        self.scene_start("S07_analogy", title="The Analogy - A Bus at a Stop")

        head = self.heading("A bus at a stop")
        bus = pill("a full bus of 40 people:  30 adults and 10 students", WORD, size=LABEL)
        off = text("a fifth of the passengers get off, adults and students alike:    24 adults and 8 students stay", LABEL, INK)
        on = text("8 new students get on:    24 adults and 16 students, and the bus is full again", LABEL, GOOD, BOLD)
        stops = VGroup(text("Where the analogy stops", LABEL, BAD, BOLD),
                       text("real passengers choose who gets off;  a stirred liquid cannot choose", LABEL, INK),
                       text("so in a mixture the proportion removed is always the same for each ingredient", LABEL, MUTED)).arrange(DOWN, buff=0.2)
        fit_width(off, SAFE_W - 0.6)
        self.stack(head, [bus, off, on, stops], buff=0.55, top=0.7)

        n = self.narrate(
            id="analogy_01",
            text="Think of a full bus of forty people: thirty adults and ten students. At a stop, a fifth of the "
                 "passengers get off, adults and students alike, so twenty-four adults and eight students stay.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "bus")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "forty")
        self.play(FadeIn(bus, shift=UP * 0.1))
        self.at_word(n, "fifth")
        self.play(FadeIn(off, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_02",
            text="Then eight new students get on: twenty-four adults and sixteen students, and the bus is full again.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "new")
        self.play(FadeIn(on, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_03",
            text="Where the analogy stops: real passengers choose who gets off, but a stirred liquid cannot choose. In a "
                 "mixture, the proportion removed is always the same for each ingredient.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "stops")
        self.play(FadeIn(stops[0], shift=UP * 0.1))
        self.at_word(n, "choose")
        self.play(FadeIn(stops[1], shift=UP * 0.1))
        self.at_word(n, "same")
        self.play(FadeIn(stops[2], shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S07_analogy")

    # ============================================== 8. WORKED EXAMPLE - CLOSING THE HOOK ==========

    def hook_solved(self):
        self.scene_start("S08_hook_solved", title="Worked Example - Closing the Hook")

        head = self.heading("20 L of juice;  5 L replaced with water")
        panel = self.side_panel(["Fraction left  =\n1 − removed/total", "Amount left  =\nstart × fraction left"])
        steps = self.solve_steps([("Fraction left:    1 − 5/20", "=  3/4"),
                                  ("Juice left:    20 × 3/4", "=  15 L"),
                                  ("The dispenser is full again:    15 L of 20 L", "=  75% juice"),
                                  ("Water:    20 − 15", "=  5 L")])
        self.stack(head, [steps], top=1.0)
        self.no_overlap(*steps)

        n = self.narrate(
            id="hook_solved_01",
            text="The fraction left is one minus five over twenty: three quarters.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(panel, shift=RIGHT * 0.2))
        self.at_word(n, "minus")
        self.play(FadeIn(steps[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "quarters")
        self.play(FadeIn(steps[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_solved_02",
            text="The juice left is twenty times three quarters: fifteen litres.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "times")
        self.play(FadeIn(steps[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "fifteen")
        self.play(FadeIn(steps[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_solved_03",
            text="The dispenser is full again, so fifteen litres in twenty: seventy-five percent juice.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "full")
        self.play(FadeIn(steps[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "seventy-five")
        self.play(FadeIn(steps[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_solved_04",
            text="And the water is twenty minus fifteen: five litres.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "water")
        self.play(FadeIn(steps[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "five")
        self.play(FadeIn(steps[3][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S08_hook_solved")

    # ============================================== 9. A SECOND WORKED EXAMPLE - STARTING FROM A MIXTURE ==========

    def second_example(self):
        self.scene_start("S09_second_example", title="A Second Worked Example - Starting from a Mixture")

        head = self.heading("Starting from a mixture")
        panel = self.side_panel(["Fraction left  =\n1 − removed/total", "Apply it to each\ningredient, then add\nthe refill"])
        ask = fitted_text("40 L of milk and water in the ratio 3 : 1;   8 L is removed and replaced with water:    the new ratio?", self.body_w() - 0.2, LABEL, MUTED, max_lines=3)
        steps = self.solve_steps([("Start:    milk 30 L,  water 10 L;      fraction left  1 − 8/40", "=  4/5"),
                                  ("Milk left:    30 × 4/5", "=  24 L"),
                                  ("Water left:    10 × 4/5 = 8 L;      plus the refill of 8 L", "=  16 L"),
                                  ("Milk : water  =  24 : 16", "=  3 : 2")])
        self.stack(head, [ask, steps], buff=0.7, top=0.7)
        self.no_overlap(*steps)

        n = self.narrate(
            id="second_example_01",
            text="Forty litres of milk and water is in the ratio three to one. Eight litres is removed and replaced with "
                 "water. What is the new ratio?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Forty")
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(panel, shift=RIGHT * 0.2))
        self.at_word(n, "removed")
        self.play(FadeIn(ask, shift=UP * 0.1))
        self.at_word(n, "new")
        self.play(Indicate(ask, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_02",
            text="Start with thirty litres of milk and ten of water. The fraction left is one minus eight over forty: four "
                 "fifths.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Start")
        self.play(FadeIn(steps[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "fifths")
        self.play(FadeIn(steps[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_03",
            text="The milk left is thirty times four fifths: twenty-four litres.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "times")
        self.play(FadeIn(steps[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "twenty-four")
        self.play(FadeIn(steps[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_04",
            text="The water left is ten times four fifths, eight litres, plus the refill of eight: sixteen litres.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "water")
        self.play(FadeIn(steps[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "sixteen")
        self.play(FadeIn(steps[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_05",
            text="So milk to water is twenty-four to sixteen: three to two.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "milk")
        self.play(FadeIn(steps[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "three")
        self.play(FadeIn(steps[3][2], shift=LEFT * 0.1))
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
            text="A pure liquid, replaced once: a ten litre tank, with two litres removed and refilled with water. One "
                 "minus two tenths: four fifths is left.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "pure")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "minus")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_03",
            text="A mixture refilled with water: forty litres at three to one, with eight litres replaced by water. Milk "
                 "twenty-four, water sixteen: three to two.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "water")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "twenty-four")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_04",
            text="A mixture refilled with milk: the same forty litres, with eight litres replaced by milk. Water eight, "
                 "milk thirty-two: four to one.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "milk")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "thirty-two")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Exam patterns  ·  4 to 6 of 6")
        blocks = self.pattern_blocks(PATTERNS[3:6])
        self.stack(head, list(blocks), buff=0.6, top=0.8, align=LEFT)

        n = self.narrate(
            id="exam_patterns_05",
            text="Strength: twenty-five litres of forty percent acid, with five litres replaced by water. Forty percent "
                 "times four fifths: thirty-two percent.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "Strength")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "times")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_06",
            text="Find the amount replaced: sixty litres of pure milk, brought down to eighty percent. Four fifths stays, "
                 "so one fifth of sixty: twelve litres.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "amount")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "stays")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_07",
            text="Reach a ratio: fifty litres at four to one, replaced with water to get three to two. The milk goes from "
                 "forty to thirty, so three quarters stays: twelve and a half litres are replaced.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "ratio")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "quarters")
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
            text="Trap one: the removed fraction used as the fraction left. Five litres is removed from a twenty litre "
                 "tank of juice and replaced with water: what fraction is juice?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "removed")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "tank")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_02",
            text="The wrong instinct says five over twenty, one quarter. The correct answer is one minus five over twenty: "
                 "three quarters.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "wrong")
        self.play(FadeIn(wrong, shift=UP * 0.1))
        self.at_word(n, "correct")
        self.play(FadeIn(right, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_03",
            text="The rule: the question asks what stays. Use the fraction left, one minus removed over total.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "rule")
        self.play(FadeIn(rule, shift=UP * 0.1))
        self.at_word(n, "left")
        self.play(Indicate(rule, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)
        self.clear_stage()

        head, q, wrong, right, rule = self.show_trap(TRAPS[1])

        n = self.narrate(
            id="traps_04",
            text="Trap two: the whole removal taken from one ingredient. Eight litres is drawn from forty litres of milk "
                 "and water in the ratio three to one: how much milk is left?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "whole")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "drawn")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_05",
            text="The wrong instinct subtracts eight from thirty: twenty-two litres. The correct answer is thirty times "
                 "four fifths: twenty-four litres.",
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
            text="The rule: a removed part is a mixture too. Take the same fraction from each ingredient.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "rule")
        self.play(FadeIn(rule, shift=UP * 0.1))
        self.at_word(n, "same")
        self.play(Indicate(rule, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)
        self.clear_stage()

        head, q, wrong, right, rule = self.show_trap(TRAPS[2])

        n = self.narrate(
            id="traps_07",
            text="Trap three: the refill forgotten. Five litres is removed from twenty litres of pure juice and replaced "
                 "with water: what percent is juice now?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "forgotten")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "replaced")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_08",
            text="The wrong instinct sees fifteen litres of juice in fifteen litres: one hundred percent. The correct "
                 "answer is fifteen litres in twenty: seventy-five percent.",
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
            text="The rule: after the refill the vessel is full again. Divide by the full volume.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "rule")
        self.play(FadeIn(rule, shift=UP * 0.1))
        self.at_word(n, "full", occurrence=2)
        self.play(Indicate(rule, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S11_traps")

    # ============================================== 12. CHECKPOINT ==========

    def checkpoint(self):
        self.scene_start("S12_checkpoint", title="Checkpoint")

        head = self.heading("Checkpoint  ·  your turn")
        given = pill("6 L of 30 L of pure milk is replaced with water:   milk left, and its percent?", FOCUS, size=LABEL)
        work = VGroup(text("30 × (1 − 6/30)  =  30 × 4/5", BODY, INK, BOLD), text("=  24 L,  80%", BODY, GOOD, BOLD)).arrange(RIGHT, buff=0.6)
        self.stack(head, [given, work], buff=1.0, top=1.0)
        self.no_overlap(*work)

        n = self.narrate(
            id="checkpoint_01",
            text="Your turn. Six litres is removed from thirty litres of pure milk and replaced with water. How much milk "
                 "is left, and what percent is that?",
            voice="default",
            subtitle=True,
            pause_after=10.0,
        )
        self.at_word(n, "turn")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "Six")
        self.play(FadeIn(given, scale=1.03))
        self.at_word(n, "much")
        self.play(Indicate(given, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="checkpoint_02",
            text="Thirty times four fifths is twenty-four litres, which is eighty percent.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "times")
        self.play(FadeIn(work[0], shift=UP * 0.1))
        self.at_word(n, "eighty")
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
            text="Level one, question one: five litres is removed from a twenty litre mixture and replaced with water; "
                 "what fraction of the original mixture is left? Question two: ten litres is removed from fifty litres of "
                 "pure milk and replaced with water; how much milk is left?",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "mixture")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "milk")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="practice_02",
            text="Level two, question three: fifteen litres is removed from sixty litres of fifty percent acid and "
                 "replaced with water; find the new strength. Question four: eighty litres of milk and water is in the "
                 "ratio three to one, and twenty litres is replaced with water; find the new ratio. Question five: how "
                 "much of forty litres of pure milk must be replaced with water to leave a mixture that is seventy percent "
                 "milk?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "acid")
        self.play(FadeIn(rows[2], shift=RIGHT * 0.2))
        self.at_word(n, "eighty")
        self.play(FadeIn(rows[3], shift=RIGHT * 0.2))
        self.at_word(n, "much")
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
            text="Level three, question six: thirty-six litres of milk and water is in the ratio five to one, and twelve "
                 "litres is replaced with milk; find the new ratio. Question seven: how much of one hundred litres of "
                 "thirty percent acid must be replaced with water to make it twenty-four percent? Question eight: milk to "
                 "water is seven to five in a full vessel; nine litres is drawn and replaced with water, making them "
                 "equal; find the capacity of the vessel.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "thirty-six")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "acid")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.at_word(n, "vessel")
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
            text="One: one minus five over twenty: three quarters.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "minus")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "quarters")
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_02",
            text="Two: fifty times four fifths: forty litres.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "times")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "forty")
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_03",
            text="Three: fifty percent times three quarters: thirty-seven and a half percent.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "times")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "thirty-seven")
        self.play(FadeIn(rows[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_04",
            text="Four: the milk is sixty times three quarters, forty-five, and the water is the other thirty-five: nine "
                 "to seven.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "milk")
        self.play(FadeIn(rows[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "nine")
        self.play(FadeIn(rows[3][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Answer key  ·  5 to 8", GOOD)
        table, rows = self.answer_table(head, ANSWERS_B, 5)

        n = self.narrate(
            id="answers_05",
            text="Five: the milk must be twenty-eight litres, so forty minus twenty-eight, twelve litres, is replaced.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "milk")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "twelve")
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_06",
            text="Six: the water is six times two thirds, four litres, and the milk is the other thirty-two: eight to one.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "water")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "eight")
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_07",
            text="Seven: the fraction left is twenty-four over thirty, four fifths, so one fifth of one hundred, twenty "
                 "litres, is replaced.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "fraction")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "twenty")
        self.play(FadeIn(rows[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_08",
            text="Eight: seven twelfths times the fraction left must be one half, so the fraction left is six sevenths. "
                 "Nine litres is one seventh of the vessel: sixty-three litres.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "twelfths")
        self.play(FadeIn(rows[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "sixty-three")
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
            text="Recognise and move. The recognition cue: drawn off, taken out and replaced with water, or removed and "
                 "refilled, done once.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "cue")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "drawn")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_lens_02",
            text="The target time: thirty to forty-five seconds.",
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
            text="The sanity check: the ingredient you did not pour back only goes down, and the vessel ends full, so the "
                 "parts add to the capacity.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "sanity")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "down")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S15_exam_lens")

    # ============================================== 16. QUICK REVISION AND SUMMARY ==========

    def summary(self):
        self.scene_start("S16_summary", title="Quick Revision and Summary")

        head = self.heading("Quick revision")
        main = pill("fraction left of every ingredient  =  1 − removed/total", GOOD, size=LABEL)
        row = VGroup(pill("apply it to each ingredient", WORD, size=SMALL), pill("then add the refill", WORD, size=SMALL),
                     pill("the vessel ends full", WORD, size=SMALL)).arrange(RIGHT, buff=0.3)
        fit_width(row, SAFE_W - 0.4)
        back = pill("backwards:   fraction left  =  target ÷ start", RATIO, size=LABEL)
        bus = text("the bus:  a fifth of everyone gets off, then new passengers get on", LABEL, MUTED)
        nxt = self.breadcrumb("Next", "Video 5 · Repeated Replacement")
        self.stack(head, [main, row, back, bus, nxt], buff=0.6, top=0.7)
        self.no_overlap(*row)

        n = self.narrate(
            id="summary_01",
            text="The fraction left of every ingredient is one minus the removed amount over the total.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "fraction")
        self.play(FadeIn(main, scale=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_02",
            text="Apply it to each ingredient, then add the refill, and remember that the vessel ends full.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "each")
        self.play(FadeIn(row[0], shift=UP * 0.1))
        self.at_word(n, "refill")
        self.play(FadeIn(row[1], shift=UP * 0.1))
        self.at_word(n, "full")
        self.play(FadeIn(row[2], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_03",
            text="Backwards, the fraction left is the target divided by the start.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Backwards")
        self.play(FadeIn(back, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_04",
            text="Remember the bus: a fifth of everyone gets off, then new passengers get on.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "bus")
        self.play(FadeIn(bus, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_05",
            text="Next: repeated replacement.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Next")
        self.play(FadeIn(nxt, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S16_summary")

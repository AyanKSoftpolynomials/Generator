"""
animation.py for the LMS video generator.

Course : Pre-C-CAT - Section A - Quantitative Aptitude
Video  : Lesson 12 - Profit & Loss - 05 - Dishonest Dealers & False Weights

Source script:
  C:\\Scripts\\Section A\\Module_2_Section_A_Quantitative_Aptitude_Part_1\\Aptitude_Scripts\\Sessions 1-4 - Interest, Profit & Loss, Time & Work\\Lesson 12 - Profit & Loss\\05 - Dishonest Dealers & False Weights.pdf

Built on the golden-reference pattern:
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``;
  * layouts stacked with next_to and guarded with ``no_overlap``; nothing is
    ever animated onto or into another box.

Lesson 12, Video 5 of 8. Not the first video of the lesson: a silent breadcrumb, a one-line recap of Video 4, then today's topic. No spoken course welcome.
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
    """A percentage to at most two decimals: 11.11, 5.26, 20."""
    return f"{round(float(x), 2):g}"


def rs(x):
    return f"₹{round(x):,}"


def overall_factor(given, claimed=1000, price_factor=1):
    """SP/CP for a dealer: price factor × (claimed weight ÷ weight actually given)."""
    return Fraction(price_factor) * Fraction(claimed, given)


def gain_pct(given, claimed=1000, price_factor=1):
    return (overall_factor(given, claimed, price_factor) - 1) * 100


def weight_for_gain(gain, claimed=1000):
    """Weight given so that the false weight alone gains ``gain`` percent."""
    return Fraction(claimed) / (1 + Fraction(gain) / 100)


# ---- the hook: the grocer ----
STONE = 900
HOOK_GAIN = gain_pct(STONE)
assert HOOK_GAIN == Fraction(100, 9) and pct(HOOK_GAIN) == "11.11" and Fraction(1000 - STONE, 1000) * 100 == 10
assert (100 * Fraction(STONE, 1000), Fraction(10, 90) * 100) == (90, HOOK_GAIN)

# ---- concept: weight with a markup ----
MARKUP_FACTOR = overall_factor(900, price_factor="1.1")
assert MARKUP_FACTOR == Fraction(11, 9) and pct(gain_pct(900, price_factor="1.1")) == "22.22"

# ---- second worked example: false weight with a loss ----
EX_FACTOR = overall_factor(800, price_factor="0.96")
assert (Fraction(1000, 800), EX_FACTOR, gain_pct(800, price_factor="0.96")) == (Fraction("1.25"), Fraction("1.2"), 20)
assert (96 - 80, Fraction(16, 80) * 100) == (16, 20)

# ---- exam patterns (answers computed) ----
P1, P4, P5 = gain_pct(950), weight_for_gain(25), gain_pct(750, price_factor="0.8")
P6 = gain_pct(900, claimed=1100)
assert (pct(P1), P4, P5, pct(P6)) == ("5.26", 800, Fraction(20, 3), "22.22")
PATTERNS_A = [("False weight at cost", "950 g for 1 kg", "50/950", f"{pct(P1)}% gain"),
              ("Weight + markup", "900 g, priced 10% above cost", "1.1 × 10/9", "22.22% gain"),
              ("Weight + loss", "800 g, sold at 4% loss", "0.96 × 1.25", "20% gain")]
PATTERNS_B = [("Find the weight", "25% gain by weight alone", "error/(1,000 − error) = 1/4", f"{P4} g"),
              ("Weight + discount", "750 g, sold at 20% loss", "0.8 × 4/3", "6 2/3 % gain"),
              ("Double cheating", "Takes 10% extra when buying, gives 10% less when selling", "1,100/900", f"{pct(P6)}% gain")]

# ---- traps: (title, question, wrong, right, rule) ----
TRAPS = [("Trap 1  ·  dividing by the claimed weight", "900 g used for 1 kg, sold at cost.  Gain?",
          "100/1,000  =  10%", f"100/900  =  {pct(HOOK_GAIN)}%",
          "The base is what he actually handed over."),
         ("Trap 2  ·  adding the two cheats", "10% markup and a 900 g kilo.  Gain?",
          "10% + 11.11%  =  21.11%", "1.1 × 10/9  =  22.22%",
          "Price and weight factors multiply."),
         ("Trap 3  ·  double cheating taken as 20%", "He takes 10% extra when buying and gives 10% less when selling.  Gain?",
          "10% + 10%  =  20%", f"1,100/900  =  {pct(P6)}%",
          "Compare grams received per rupee with grams given per rupee.")]

# ---- checkpoint ----
CP_GAIN = gain_pct(800)
assert CP_GAIN == 25

# ---- practice (answers computed) ----
PRACTICE_A = [("L1", "A dealer sells at cost price but uses a 950 g weight for 1 kg.  Find his gain %."),
              ("L1", "A dealer sells at cost price but uses a 750 g weight for a kilogram.  Find his gain %."),
              ("L2", "A dealer uses a 900 g weight for 1 kg and also charges 10% above cost.  Find his overall gain %."),
              ("L2", "A dealer sells at a 4% loss but uses an 800 g weight for 1 kg.  Find his profit %."),
              ("L2", "A dealer gains 25% by false weight alone.  How many grams does he give for 1 kg?")]
PRACTICE_B = [("L3", "A dealer gains 100% by false weight alone.  What weight does he use for a kilogram?"),
              ("L3", "A shopkeeper sells at a 20% loss but uses a 750 g weight for 1 kg.  Find his gain or loss %."),
              ("L3", "A trader takes 10% extra weight when buying and gives 10% less weight when selling, at the same price "
                     "per kg.  Find his gain %.")]
assert (gain_pct(750), weight_for_gain(100)) == (Fraction(100, 3), 500)
ANSWERS_A = [("50/950 × 100", f"{pct(P1)}%"),
             ("250/750 × 100", "33 1/3 %"),
             ("1.1 × 1,000/900 = 1.2222    (₹110 received for goods worth ₹90)", "22.22% gain"),
             ("0.96 × 1,000/800 = 1.2", "20% profit"),
             ("error/(1,000 − error) = 1/4;   error = 200 g", f"{P4} g")]
ANSWERS_B = [("(1,000 − w)/w = 1", f"{weight_for_gain(100)} g"),
             ("0.8 × 1,000/750 = 1.0667", "6 2/3 % gain"),
             ("receives 1,100 g per ₹100 paid;  gives 900 g per ₹100 charged:   1,100/900", f"{pct(P6)}% gain")]

OBJECTIVES = [("Find the gain from a false weight", "on the correct base"),
              ("Combine weight with price", "a markup, a discount or a loss, in one line"),
              ("Handle double cheating", "when buying and when selling")]
LENS = [("Recognition cue", "“uses a weight of”, “gives x g for a kg”, “false balance”  →  weight factor = claimed ÷ given"),
        ("Target time", "30 seconds"),
        ("Sanity check", "the gain is always a little more than the missing fraction of the claimed weight")]
FORMULAS = ["Gain %  =  error / (weight given) × 100              error = claimed − given",
            "Overall factor  =  (price factor) × (claimed weight ÷ weight given)",
            "Price factor:      at cost = 1        10% above = 1.1        4% loss = 0.96",
            "Double cheating:      factor = (weight received when buying) ÷ (weight given when selling)"]


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


class DishonestDealersVideo(LMSScene):
    lesson_title = "Dishonest Dealers & False Weights"

    def construct(self):
        self.camera.background_color = BG

        self.intro()
        self.hook()
        self.objectives()
        self.why_this_matters()
        self.per_gram()
        self.rule_and_factor()
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

    def two_cards(self, lines_a, lines_b, colors=(WORD, RATIO), width=5.6):
        """Two cards of the same height.  Returns (cards, contents)."""
        contents = [VGroup(*[text(s, size, c, w) for s, size, c, w in lines]).arrange(DOWN, buff=0.22)
                    for lines in (lines_a, lines_b)]
        tallest = max(c.height for c in contents) + 0.7
        cards = VGroup(*[self.card(c, width=width, height=tallest, color=col) for c, col in zip(contents, colors)])\
            .arrange(RIGHT, buff=0.6)
        return cards, contents

    # ================================================== 0. INTRO ==========
    # Not the first video: silent breadcrumb, a one-line recap of Video 4, then today's topic.

    def intro(self):
        self.scene_start("S00_intro", title="Intro")

        crumb = self.breadcrumb("Quantitative Aptitude", "Lesson 12 · Profit & Loss", "Video 5 of 8")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        recap = VGroup(text("last video", SMALL, MUTED), pill("markup and discount chain:  net % = x − d − xd/100", WORD, size=LABEL))\
            .arrange(DOWN, buff=0.25)
        title = fit_width(text("Dishonest Dealers & False Weights", TITLE, INK, BOLD), SAFE_W)
        today = text("today: dealers who cheat on the weight, not the price", LABEL, FOCUS)
        block = VGroup(recap, title, today).arrange(DOWN, buff=0.7)
        fit_within(block, SAFE_W, SAFE_H - crumb.height - 0.9)
        block.next_to(crumb, DOWN, buff=0.7)
        self.no_overlap(crumb, recap, title, today)
        self.validator.check_in_frame(VGroup(crumb, block))

        n = self.narrate(
            id="intro_01",
            text="In the last video, a markup and a discount chained into one multiplier.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.at_word(n, "chained")
        self.play(FadeIn(recap, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="intro_02",
            text="Today: dealers who cheat on the weight, not the price.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "weight")
        self.play(FadeIn(title, shift=UP * 0.1))
        self.at_word(n, "price")
        self.play(FadeIn(today, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_intro")

    # =================================================== 1. HOOK ==========

    def hook(self):
        self.scene_start("S01_hook", title="Hook")

        head = self.heading("A grocer's scale")
        sign_text = text("“We sell at cost price.  No profit!”", BODY, INK, BOLD)
        sign = self.card(sign_text, width=8.6, color=GOOD, pad=0.45)
        stone = VGroup(pill("the stone is marked:  1 kg", MUTED, size=LABEL), pill(f"it really weighs:  {STONE} g", BAD, size=LABEL))\
            .arrange(RIGHT, buff=0.5)
        claim = VGroup(text("claimed profit:  0%", LABEL, MUTED), pill("real profit %  =  ?", FOCUS, size=LABEL)).arrange(RIGHT, buff=0.6)
        most = VGroup(pill("most people say 10%", BAD, size=LABEL), text("it isn't: it is the same base question again", SMALL, GOOD, BOLD))\
            .arrange(RIGHT, buff=0.5)
        self.stack(head, [sign, stone, claim, most], buff=0.5, top=0.6)
        self.no_overlap(*stone)
        self.no_overlap(*claim)
        self.no_overlap(*most)

        n = self.narrate(
            id="hook_01",
            text="A grocer displays a sign: we sell at cost price, no profit.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "sign")
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(sign[0]))
        self.at_word(n, "cost")
        self.play(FadeIn(sign_text, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_02",
            text="But the stone he weighs with, marked one kilogram, actually weighs nine hundred grams.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "marked")
        self.play(FadeIn(stone[0], shift=UP * 0.1))
        self.at_word(n, "nine")
        self.play(FadeIn(stone[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_03",
            text="He claims zero profit. What is his real profit percent?",
            voice="default",
            subtitle=True,
            pause_after=3.0,
        )
        self.at_word(n, "zero")
        self.play(FadeIn(claim[0], shift=UP * 0.1))
        self.at_word(n, "real")
        self.play(FadeIn(claim[1], shift=LEFT * 0.1))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="hook_04",
            text="Most people say ten percent. It isn't, and the reason is the same base question you have been asking all "
                 "lesson.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "ten")
        self.play(FadeIn(most[0], shift=UP * 0.1))
        self.at_word(n, "base")
        self.play(FadeIn(most[1], shift=LEFT * 0.1))
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
            text="First, find the gain from a false weight on the correct base.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "gain")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "base")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="obj_03",
            text="Second, combine a false weight with a markup, a discount or a loss, in one line.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "combine")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "line")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="obj_04",
            text="Third, handle double cheating, when buying and when selling.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "double")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "buying")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_objectives")

    # ========================================== 3. WHY THIS MATTERS ==========

    def why_this_matters(self):
        self.scene_start("S03_why_this_matters", title="Why This Matters")

        head = self.heading("Why this matters")
        hidden = pill("the profit hides inside the quantity, not the price", WORD, size=LABEL)
        same = text("the method is identical to everything so far: compare", LABEL, INK)
        compare = VGroup(pill("what the dealer receives", GOOD, size=LABEL), text("with", LABEL, MUTED),
                         pill("what the goods he hands over cost him", RATIO, size=LABEL)).arrange(RIGHT, buff=0.4)
        self.stack(head, [hidden, same, compare], buff=0.8, top=0.9)
        self.no_overlap(*compare)

        n = self.narrate(
            id="why_01",
            text="False-weight questions hide the profit inside the quantity instead of the price.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "quantity")
        self.play(FadeIn(hidden, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="why_02",
            text="The method is identical to everything so far: compare what the dealer receives with what the goods he hands "
                 "over actually cost him.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "identical")
        self.play(FadeIn(same, shift=UP * 0.1))
        self.at_word(n, "receives")
        self.play(FadeIn(compare[0], shift=UP * 0.1))
        self.at_word(n, "cost")
        self.play(FadeIn(compare[1:], shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_why_this_matters")

    # ================================ 4. CONCEPT: PRICE IT PER GRAM ==========

    def per_gram(self):
        self.scene_start("S04_per_gram", title="Concept - Price Everything per Gram of Real Goods")

        head = self.heading("Price everything per gram of real goods")
        say = text("say 1 kg costs the dealer ₹100", LABEL, MUTED)
        cards, (charges, gives) = self.two_cards(
            [("He charges for", LABEL, GOOD, BOLD), ("1,000 g", BODY, INK, BOLD), ("receives ₹100", LABEL, INK, NORMAL)],
            [("He gives", LABEL, BAD, BOLD), (f"{STONE} g", BODY, INK, BOLD), ("worth ₹90 to him", LABEL, INK, NORMAL)],
            colors=(GOOD, BAD))
        real = text("profit ₹10, measured on his real cost of ₹90", LABEL, INK)
        result = pill(f"10/90  =  {pct(HOOK_GAIN)}%", FOCUS, size=BODY)
        self.stack(head, [say, cards, real, result], buff=0.5, top=0.6)
        self.no_overlap(cards[0], cards[1])

        n = self.narrate(
            id="gram_01",
            text="Price everything per gram of real goods. Say one kilogram costs the dealer one hundred rupees.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "gram")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "hundred")
        self.play(FadeIn(say, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="gram_02",
            text="He receives the price of one thousand grams, one hundred rupees, but hands over nine hundred grams, worth "
                 "ninety rupees to him.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "receives")
        self.play(FadeIn(cards[0], shift=UP * 0.1))
        self.at_word(n, "hands")
        self.play(FadeIn(cards[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="gram_03",
            text="Profit is measured on his real cost, the nine hundred grams: ten over ninety, eleven point one one percent.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "real")
        self.play(FadeIn(real, shift=UP * 0.1))
        self.at_word(n, "eleven")
        self.play(FadeIn(result, scale=1.05))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_per_gram")

    # ====================== 5. CONCEPT: THE GENERAL RULE, ONE MULTIPLIER ==========

    def rule_and_factor(self):
        self.scene_start("S05_rule_and_factor", title="Concept - The General Rule and One Multiplier for Everything")

        head = self.heading("The general rule")
        rule = pill("gain %  =  error ÷ (weight actually given) × 100", GOOD, size=LABEL)
        error = text("error  =  claimed weight − weight given", LABEL, MUTED)
        one = text("one multiplier for everything", LABEL, RATIO, BOLD)
        factor = pill("overall SP/CP  =  price factor × (claimed weight ÷ weight given)", FOCUS, size=LABEL)
        example = VGroup(text("10% markup, 900 g kilo:   1.1 × 1,000/900  =  1.222", LABEL, INK),
                         pill("a 22.2% gain", GOOD, size=LABEL)).arrange(RIGHT, buff=0.5)
        self.stack(head, [rule, error, one, factor, example], buff=0.5, top=0.6)
        self.no_overlap(*example)

        n = self.narrate(
            id="rule_01",
            text="The general rule: gain percent is the error, divided by the weight actually given, times a hundred.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "general")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "divided")
        self.play(FadeIn(rule, scale=1.05))
        self.wait_for_narration(n)

        n = self.narrate(
            id="rule_02",
            text="The error is the claimed weight minus the weight given.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "minus")
        self.play(FadeIn(error, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="rule_03",
            text="One multiplier handles everything. The overall factor is the price factor, times the claimed weight divided "
                 "by the weight given.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "everything")
        self.play(FadeIn(one, shift=UP * 0.1))
        self.at_word(n, "times")
        self.play(FadeIn(factor, scale=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="rule_04",
            text="A ten percent markup with a nine hundred gram kilo: one point one times one thousand over nine hundred is one "
                 "point two two two, a twenty-two point two percent gain.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "times")
        self.play(FadeIn(example[0], shift=UP * 0.1))
        self.at_word(n, "gain")
        self.play(FadeIn(example[1], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_rule_and_factor")

    # ============================================== 6. FORMULA BOX ==========

    def formula_box(self):
        self.scene_start("S06_formula_box", title="Formula Box")

        head = self.heading("Formula box", GOOD)
        lines = VGroup(*[text(f, LABEL, INK) for f in FORMULAS]).arrange(DOWN, buff=0.5, aligned_edge=LEFT)
        box = self.card(lines, width=SAFE_W - 0.4, color=GOOD, pad=0.5)
        self.stack(head, [box], top=0.8)

        n = self.narrate(
            id="formula_01",
            text="Here is the formula box. Gain percent is the error over the weight given, times a hundred.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "box")
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(box[0]))
        self.at_word(n, "error")
        self.play(FadeIn(lines[0], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_02",
            text="The overall factor is the price factor times claimed weight over weight given.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "overall")
        self.play(FadeIn(lines[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_03",
            text="The price factor is one at cost, one point one for ten percent above, and zero point nine six for a four "
                 "percent loss.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "price")
        self.play(FadeIn(lines[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_04",
            text="For double cheating, the factor is the weight received when buying, over the weight given when selling.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "double")
        self.play(FadeIn(lines[3], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_formula_box")

    # ============================================== 7. THE ANALOGY ==========

    def analogy(self):
        self.scene_start("S07_analogy", title="The Analogy - A Short-Filled Bottle")

        head = self.heading("A bottle labelled 1 litre")
        bottle = VGroup(pill("the label:  1 litre", MUTED, size=LABEL), pill("inside:  900 ml", BAD, size=LABEL),
                        text("you pay for the full litre", LABEL, INK)).arrange(RIGHT, buff=0.5)
        cost = text("the seller's cost is only the 900 ml he actually gave", LABEL, INK)
        base = pill("his profit is measured against 900 ml, not 1,000", GOOD, size=LABEL)
        stops = VGroup(text("Where the analogy stops", LABEL, BAD, BOLD),
                       text("the bottle cheats once", LABEL, MUTED),
                       text("exam dealers often cheat on price and weight together: use the combined factor", LABEL, INK))\
            .arrange(DOWN, buff=0.22)
        self.stack(head, [bottle, cost, base, stops], buff=0.6, top=0.7)
        self.no_overlap(*bottle)

        n = self.narrate(
            id="analogy_01",
            text="A bottle labelled one litre holds nine hundred millilitres, but you pay for a litre.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "labelled")
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(bottle[0], shift=UP * 0.1))
        self.at_word(n, "holds")
        self.play(FadeIn(bottle[1], shift=UP * 0.1))
        self.at_word(n, "pay")
        self.play(FadeIn(bottle[2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_02",
            text="The seller's cost is only the nine hundred millilitres he actually gave, so his profit is measured against "
                 "nine hundred, not one thousand.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "cost")
        self.play(FadeIn(cost, shift=UP * 0.1))
        self.at_word(n, "measured")
        self.play(FadeIn(base, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_03",
            text="Where the analogy stops: the bottle cheats once.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "stops")
        self.play(FadeIn(stops[0], shift=UP * 0.1))
        self.at_word(n, "once")
        self.play(FadeIn(stops[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_04",
            text="Dealers in exam questions often cheat on price and weight together, so you need the combined factor.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "combined")
        self.play(FadeIn(stops[2], shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S07_analogy")

    # ================================ 8. WORKED EXAMPLE: CLOSING THE HOOK ==========

    def hook_solved(self):
        self.scene_start("S08_hook_solved", title="Worked Example - Closing the Hook")

        head = self.heading(f"The grocer:  a {STONE} g stone for 1 kg, sold at cost")
        steps = self.solve_steps([("error  =  1,000 − 900  =  100 g", f"weight given  =  {STONE} g"),
                                  ("gain  =  100/900 × 100", f"=  {pct(HOOK_GAIN)}%")])
        about = pill("the “no profit” grocer makes about 11% on every sale", FOCUS, size=LABEL)
        self.stack(head, [steps, about], buff=0.9, top=0.9)
        self.no_overlap(*steps)

        n = self.narrate(
            id="solved_01",
            text="The error is one hundred grams, and the weight given is nine hundred grams.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "error")
        self.play(FadeIn(steps[0][:2], shift=RIGHT * 0.1))
        self.at_word(n, "nine")
        self.play(FadeIn(steps[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_02",
            text="The gain is one hundred over nine hundred, times a hundred: eleven point one one percent.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "over")
        self.play(FadeIn(steps[1][:2], shift=RIGHT * 0.1))
        self.at_word(n, "eleven")
        self.play(FadeIn(steps[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_03",
            text="The no-profit grocer makes about eleven percent on every sale.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "about")
        self.play(FadeIn(about, scale=1.05))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S08_hook_solved")

    # ====================== 9. SECOND WORKED EXAMPLE: FALSE WEIGHT WITH A LOSS ==========

    def second_example(self):
        self.scene_start("S09_second_example", title="A Second Worked Example - False Weight with a Loss")

        head = self.heading("A false weight with a loss")
        given = VGroup(pill("sells at a 4% loss on the price of 1 kg", BAD, size=LABEL), pill("uses an 800 g weight", WORD, size=LABEL),
                       pill("gain or loss = ?", FOCUS, size=LABEL)).arrange(RIGHT, buff=0.35)
        steps = self.solve_steps([
            ("price factor = 0.96;    weight factor = 1,000/800", f"=  {dec(Fraction(1000, 800))}"),
            ("overall factor  =  0.96 × 1.25", f"=  {dec(EX_FACTOR)}:  a {gain_pct(800, price_factor='0.96')}% gain"),
            ("check, at ₹100 per kg:  charges ₹96, gives goods worth ₹80", "₹16 on ₹80  =  20%")])
        self.stack(head, [given, steps], buff=0.8, top=0.8)
        self.no_overlap(*given)
        self.no_overlap(*steps)

        n = self.narrate(
            id="loss_01",
            text="A dealer sells at a four percent loss on the price of a kilogram, but uses an eight hundred gram weight. Find "
                 "his gain or loss.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "four")
        self.play(FadeIn(given[0], shift=UP * 0.1))
        self.at_word(n, "eight")
        self.play(FadeIn(given[1], shift=UP * 0.1))
        self.at_word(n, "Find")
        self.play(FadeIn(given[2], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="loss_02",
            text="The price factor is zero point nine six. The weight factor is one thousand over eight hundred: one point two "
                 "five.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "price")
        self.play(FadeIn(steps[0][:2], shift=RIGHT * 0.1))
        self.at_word(n, "five")
        self.play(FadeIn(steps[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="loss_03",
            text="The overall factor is zero point nine six times one point two five, which is one point two: a twenty percent "
                 "gain.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "times")
        self.play(FadeIn(steps[1][:2], shift=RIGHT * 0.1))
        self.at_word(n, "twenty")
        self.play(FadeIn(steps[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="loss_04",
            text="Check with one hundred rupees per kilogram: he charges ninety-six rupees, and hands over eight hundred grams "
                 "worth eighty rupees. Sixteen rupees of profit on eighty is twenty percent.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Check")
        self.play(FadeIn(steps[2][:2], shift=RIGHT * 0.1))
        self.at_word(n, "Sixteen")
        self.play(FadeIn(steps[2][2], shift=LEFT * 0.1))
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
            text="A false weight at cost: nine hundred and fifty grams for a kilogram is fifty over nine hundred and fifty, a "
                 "five point two six percent gain.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "false")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "over")
        self.play(FadeIn(rows[0][2:], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="patterns_03",
            text="Weight plus markup: nine hundred grams, priced ten percent above cost, is one point one times ten ninths, a "
                 "twenty-two point two two percent gain.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "markup")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "times")
        self.play(FadeIn(rows[1][2:], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="patterns_04",
            text="Weight plus loss: eight hundred grams, sold at a four percent loss, is zero point nine six times one point "
                 "two five, a twenty percent gain.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "loss", occurrence=1)
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "times")
        self.play(FadeIn(rows[2][2:], shift=RIGHT * 0.2))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Exam patterns  ·  4 to 6 of 6")
        table, rows = self.pattern_table(head, PATTERNS_B)

        n = self.narrate(
            id="patterns_05",
            text="Find the weight: for a twenty-five percent gain by weight alone, the error over the weight given is one "
                 "fourth, so he gives eight hundred grams.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "Find")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "fourth")
        self.play(FadeIn(rows[0][2:], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="patterns_06",
            text="Weight plus discount: seven hundred and fifty grams, sold at a twenty percent loss, is zero point eight times "
                 "four thirds, a gain of six and two thirds percent.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "discount")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "times")
        self.play(FadeIn(rows[1][2:], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="patterns_07",
            text="Double cheating: he takes ten percent extra when buying and gives ten percent less when selling, so eleven "
                 "hundred over nine hundred, a twenty-two point two two percent gain.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Double")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "over")
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
            text="Trap one: dividing by the claimed weight. Nine hundred grams used for a kilogram, sold at cost; what is the "
                 "gain?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "claimed")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "Nine")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="trap1_02",
            text="The wrong instinct is one hundred over one thousand, ten percent. The correct answer is one hundred over nine "
                 "hundred, eleven point one one percent.",
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
            text="The rule: the base is what he actually handed over.",
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
            text="Trap two: adding the two cheats. A ten percent markup and a nine hundred gram kilo; what is the gain?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "adding")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "markup")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="trap2_02",
            text="The wrong instinct adds ten percent and eleven point one one percent. Correctly, one point one times ten "
                 "ninths is one point two two two two: twenty-two point two two percent.",
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
            text="The rule: price and weight factors multiply.",
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
            text="Trap three: double cheating taken as twenty percent. He takes ten percent extra when buying, and gives ten "
                 "percent less when selling; what is the gain?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "double")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "takes")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="trap3_02",
            text="The wrong instinct is twenty percent. The correct answer is eleven hundred over nine hundred: twenty-two "
                 "point two two percent.",
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
            text="The rule: compare the grams received per rupee with the grams given per rupee.",
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
        given = VGroup(pill("sells at cost price", WORD, size=LABEL), pill("gives only 800 g for 1 kg", BAD, size=LABEL)).arrange(RIGHT, buff=0.5)
        hint = pill("gain % = ?", FOCUS, size=BODY)
        work = VGroup(text("200/800 × 100", BODY, INK), text(f"=  {CP_GAIN}%", BODY, GOOD, BOLD)).arrange(RIGHT, buff=0.5)
        self.stack(head, [given, hint, work], buff=0.8, top=0.9)
        self.no_overlap(*given)
        self.no_overlap(*work)

        n = self.narrate(
            id="check_01",
            text="Your turn. A dealer sells at cost price, but gives only eight hundred grams for a kilogram. What is the gain "
                 "percent?",
            voice="default",
            subtitle=True,
            pause_after=10.0,
        )
        self.at_word(n, "turn")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "cost")
        self.play(FadeIn(given[0], shift=UP * 0.1))
        self.at_word(n, "eight")
        self.play(FadeIn(given[1], shift=UP * 0.1))
        self.at_word(n, "gain")
        self.play(FadeIn(hint, shift=UP * 0.1))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="check_02",
            text="Two hundred over eight hundred, times a hundred, is twenty-five percent.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "over")
        self.play(FadeIn(work[0], shift=UP * 0.1))
        self.at_word(n, "twenty-five")
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
            text="Level one, question one: a dealer sells at cost price but uses a nine hundred and fifty gram weight for a "
                 "kilogram; find his gain percent. Question two: a dealer sells at cost price but uses a seven hundred and "
                 "fifty gram weight for a kilogram; find his gain percent.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "nine")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "seven")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="practice_02",
            text="Level two, question three: a dealer uses a nine hundred gram weight for a kilogram and also charges ten "
                 "percent above cost; find his overall gain percent. Question four: a dealer sells at a four percent loss but "
                 "uses an eight hundred gram weight for a kilogram; find his profit percent. Question five: a dealer gains "
                 "twenty-five percent by false weight alone; how many grams does he give for a kilogram?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "charges")
        self.play(FadeIn(rows[2], shift=RIGHT * 0.2))
        self.at_word(n, "loss")
        self.play(FadeIn(rows[3], shift=RIGHT * 0.2))
        self.at_word(n, "alone")
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
            text="Level three, question six: a dealer gains one hundred percent by false weight alone; what weight does he use "
                 "for a kilogram? Question seven: a shopkeeper sells at a twenty percent loss but uses a seven hundred and "
                 "fifty gram weight for a kilogram; find his gain or loss percent. Question eight: a trader takes ten percent "
                 "extra weight when buying and gives ten percent less weight when selling, at the same price per kilogram; "
                 "find his gain percent.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "alone")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "shopkeeper")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.at_word(n, "trader")
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
            text="One: fifty over nine hundred and fifty, times a hundred, is five point two six percent.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "over")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "point")
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_02",
            text="Two: two hundred and fifty over seven hundred and fifty is one third: thirty-three and a third percent.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "over")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "thirty-three")
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_03",
            text="Three: one point one times one thousand over nine hundred is one point two two two two, a twenty-two point "
                 "two two percent gain. He receives one hundred and ten rupees for goods worth ninety.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "times")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "gain")
        self.play(FadeIn(rows[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_04",
            text="Four: zero point nine six times one thousand over eight hundred is one point two: a twenty percent profit.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "times")
        self.play(FadeIn(rows[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "twenty")
        self.play(FadeIn(rows[3][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_05",
            text="Five: the error over the weight given is one fourth, so five times the error is one thousand, and the error "
                 "is two hundred grams. He gives eight hundred grams.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "fourth")
        self.play(FadeIn(rows[4][:2], shift=RIGHT * 0.2))
        self.at_word(n, "gives")
        self.play(FadeIn(rows[4][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Answer key  ·  6 to 8", GOOD)
        table, rows = self.answer_table(head, ANSWERS_B, 6)

        n = self.narrate(
            id="answers_06",
            text="Six: one thousand minus w, over w, equals one, so w is five hundred grams.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "equals")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "five")
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_07",
            text="Seven: zero point eight times one thousand over seven hundred and fifty is one point zero six six seven: a "
                 "gain of six and two thirds percent.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "times")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "gain")
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_08",
            text="Eight: for each hundred rupees he pays, he receives eleven hundred grams; for each hundred rupees he charges, "
                 "he gives nine hundred grams. The factor is eleven hundred over nine hundred: a twenty-two point two two "
                 "percent gain.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "receives")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "factor")
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
            text="Recognise and move. The recognition cue: uses a weight of, gives so many grams for a kilogram, or false "
                 "balance, means a weight factor of claimed over given.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Recognise")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "cue")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "factor")
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
            text="The sanity check: the gain from a false weight is always a little more than the missing fraction of the "
                 "claimed weight.",
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

    # ==================================== 16. QUICK REVISION + SUMMARY ==========

    def summary(self):
        self.scene_start("S16_summary", title="Quick Revision and Summary")

        head = self.heading("Quick revision")
        box = VGroup(text("Gain %   =   error / (weight given) × 100", BODY, INK, BOLD),
                     text("Overall factor   =   price factor × claimed/given", BODY, INK, BOLD)).arrange(DOWN, buff=0.45, aligned_edge=LEFT)
        base = pill("the base is the weight actually handed over", FOCUS, size=LABEL)
        nxt = self.breadcrumb("Next", "Video 6 · Two Articles, Same SP")
        self.stack(head, [box, base, nxt], buff=0.8, top=0.9)
        self.no_overlap(*box)

        n = self.narrate(
            id="summary_01",
            text="A false weight's gain is the missing weight divided by the weight actually given.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "divided")
        self.play(FadeIn(box[0], shift=RIGHT * 0.2))
        self.at_word(n, "actually")
        self.play(FadeIn(base, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_02",
            text="When price and weight both cheat, multiply the price factor by claimed over given.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "multiply")
        self.play(FadeIn(box[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_03",
            text="Next: two articles sold at the same price.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Next")
        self.play(FadeIn(nxt, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S16_summary")

"""
animation.py for the LMS video generator.

Course : Pre-C-CAT - Section A - Quantitative Aptitude
Video  : Lesson 25 - Alligation & Mixtures - 01 - Mixtures as Weighted Averages

Source script:
  C:\\Scripts\\Section A\\Module2\\S21-25_Ratio_Age_Clock_Mixtures_Mensuration\\Lesson 25 - Allegation & Mixtures\\06 - Mixtures as Weighted Averages.pdf

Built on the golden-reference pattern:
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``;
  * layouts stacked with next_to and guarded with ``no_overlap``; nothing is
    ever animated onto or into another box.

Lesson 25, Video 1 of 7 (the lesson's own order, from its Pre-Lesson Brief; the source folder numbers its files differently, and the PDFs call it Lesson 29).
First video of the lesson: a silent breadcrumb, "Now we start lesson twenty-five", a recap of Lesson 24, then today's topic.
The seven source scripts of this lesson are identical apart from their titles, so, as agreed with the course owner, each video was
written for its own topic. This one keeps the script's formula  Mean = (q1v1 + q2v2)/(q1 + q2)  and builds the hook, examples,
patterns, traps and practice around it. Every answer is computed with exact fractions in the data block.
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


def mean(*parts):
    """Weighted mean of (quantity, value) pairs."""
    return F(sum(F(q) * F(v) for q, v in parts), sum(F(q) for q, _ in parts))


# ---- hook, examples, patterns ----
assert mean((3, 200), (2, 300)) == 240 and F(200 + 300, 2) == 250
assert mean((8, 20), (12, 45)) == 35 and F(8 * 20, 100) + F(12 * 45, 100) == 7
assert mean((40, 60), (10, 80)) == 64
assert mean((5, 40), (3, 60)) == F(95, 2) and mean((4, 30), (4, 50)) == 40 and mean((30, 40), (10, 0)) == 30
assert mean((20, 50), (10, 80)) == 60 and mean((2, 30), (3, 40), (5, 60)) == 48
# ---- traps and checkpoint ----
assert mean((1, 20), (4, 70)) == 60 and F(20 + 70, 2) == 45 and mean((10, 20), (10, 40)) == 30 and mean((20, 50), (5, 0)) == 40
assert mean((4, 30), (6, 50)) == 42
# ---- practice ----
assert mean((5, 40), (5, 60)) == 50 and mean((2, 10), (3, 20)) == 16 and mean((6, 25), (4, 50)) == 35
assert mean((15, 30), (5, 0)) == F(45, 2) and mean((10, 40), (30, 60)) == 55 and mean((12, 60), (6, 90)) == 70
assert F(20 * 3, 4) + F(30 * 4, 5) == 39 and F(39, 50) == F(78, 100)
COST = 26 * 20 + 30 * 36
assert COST == 1600 and 56 * 30 == 1680 and F(1680 - COST, COST) == F(5, 100)

OBJECTIVES = [("Find the value of a mixture", "as total value divided by total quantity"),
              ("Use the same idea for price and for concentration", "by turning percentages into actual amounts"),
              ("Find a missing quantity", "when the mean of the mixture is given")]
STEPS_A = [("Mean value  =  total value ÷ total quantity", "M  =  (q1 × v1 + q2 × v2)/(q1 + q2);    each value is weighted by its quantity"),
           ("The mean always lies between the two values", "and it sits closer to the value that has the larger quantity"),
           ("Equal quantities:  the simple average works", "4 kg at ₹30 and 4 kg at ₹50:    (30 + 50)/2 = ₹40"),
           ("Unequal quantities:  the simple average fails", "5 kg at ₹40 and 3 kg at ₹60:    (200 + 180)/8 = ₹47.50,  not ₹50")]
STEPS_B = [("Concentration:  count the actual amount", "20% of 8 L is 1.6 L of acid;    percentages are never added directly"),
           ("Add the amounts, then divide by the total volume", "strength of the mixture  =  total pure amount ÷ total volume"),
           ("Water is 0%;  a pure ingredient is 100%", "adding water adds volume but no acid, so the strength falls"),
           ("A missing quantity:  balance the two sides", "q1 × (M − L)  =  q2 × (H − M);    the loss on one side equals the gain on the other")]
FORMULAS = ["Mean   =   (q1 × v1 + q2 × v2)/(q1 + q2)",
            "The mean lies between the two values, nearer the larger quantity",
            "Equal quantities:      mean  =  (v1 + v2)/2",
            "Strength   =   total pure amount ÷ total volume;        water = 0%,   pure = 100%",
            "Balance:      q1 × (M − L)   =   q2 × (H − M)"]
PATTERNS = [("Two prices", "5 kg at ₹40 and 3 kg at ₹60", "(200 + 180)/8", "₹47.50 a kg"),
            ("Equal quantities", "4 kg at ₹30 and 4 kg at ₹50", "(30 + 50)/2", "₹40 a kg"),
            ("Concentration", "8 L of 20% and 12 L of 45%", "(1.6 + 5.4)/20", "35%"),
            ("Adding water", "30 L of 40% acid and 10 L of water", "12/40", "30%"),
            ("Missing quantity", "x kg at ₹50 with 10 kg at ₹80 to make ₹60", "x × 10 = 10 × 20", "20 kg"),
            ("Three parts", "2 kg at ₹30, 3 kg at ₹40, 5 kg at ₹60", "(60 + 120 + 300)/10", "₹48 a kg")]
TRAPS = [("Trap 1  ·  the simple average with unequal quantities",
          "1 L of 20% juice is mixed with 4 L of 70% juice.  Find the strength of the mixture.",
          "(20 + 70)/2  =  45%", "(0.2 + 2.8)/5  =  60%",
          "Weight every value by its quantity; average the values only when quantities are equal."),
         ("Trap 2  ·  adding the percentages",
          "10 L of 20% syrup is mixed with 10 L of 40% syrup.  Find the strength of the mixture.",
          "20% + 40%  =  60%", "(2 + 4)/20  =  30%",
          "Percentages are not added.  Add the actual amounts, then divide by the total."),
         ("Trap 3  ·  the old volume after adding water",
          "5 L of water is added to 20 L of 50% acid.  Find the new strength.",
          "10/20  =  50%,  unchanged", "10/25  =  40%",
          "Water adds no acid but it adds volume.  Divide by the new total volume.")]
PRACTICE_A = [("L1", "5 kg of rice at ₹40 a kg is mixed with 5 kg at ₹60 a kg.  Find the price of the mixture."),
              ("L1", "2 L of 10% sugar solution is mixed with 3 L of 20% sugar solution.  Find the strength of the mixture."),
              ("L2", "6 kg of dal at ₹25 a kg is mixed with 4 kg at ₹50 a kg.  Find the price of the mixture."),
              ("L2", "5 L of water is added to 15 L of 30% alcohol.  Find the new strength."),
              ("L2", "10 L of 40% acid is mixed with 30 L of 60% acid.  Find the strength of the mixture.")]
PRACTICE_B = [("L3", "How many kg of tea at ₹90 a kg must be mixed with 12 kg at ₹60 a kg to make a mixture worth ₹70 a kg?"),
              ("L3", "20 L of milk and water in the ratio 3 : 1 is mixed with 30 L in the ratio 4 : 1.  Find the percentage of milk."),
              ("L3", "26 kg of rice at ₹20 a kg is mixed with 30 kg at ₹36 a kg and sold at ₹30 a kg.  Find the profit percent.")]
ANSWERS_A = [("Equal quantities:    (40 + 60)/2", "₹50 a kg"),
             ("Sugar:   0.2 + 0.6 = 0.8 L   in 5 L", "16%"),
             ("(150 + 200)/10", "₹35 a kg"),
             ("Alcohol:   4.5 L   in 20 L", "22.5%")]
ANSWERS_B = [("Acid:   4 + 18 = 22 L   in 40 L", "55%"),
             ("12 × (70 − 60)  =  x × (90 − 70);      120 = 20x", "6 kg"),
             ("Milk:   15 + 24 = 39 L   in 50 L", "78%"),
             ("Cost  520 + 1,080 = ₹1,600;    sale  56 × 30 = ₹1,680;    80/1,600", "5% profit")]
LENS = [("Recognition cue", "“mixed”, “mixture worth”, “price of the mixture”, “strength of the mixture”, with both quantities given"),
        ("Target time", "30 to 40 seconds"),
        ("Sanity check", "the mean lies between the two values, and nearer the one with the larger quantity")]


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


class MixturesAsWeightedAveragesVideo(LMSScene):
    lesson_title = "Mixtures as Weighted Averages"

    def construct(self):
        self.camera.background_color = BG

        self.intro()
        self.hook()
        self.objectives()
        self.why_this_matters()
        self.weighted_average()
        self.concentration()
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
    # First video of the lesson: silent breadcrumb, the lesson announcement, a recap of the previous lesson, then today's topic.

    def intro(self):
        self.scene_start("S00_intro", title="Intro")

        crumb = self.breadcrumb("Quantitative Aptitude", "Lesson 25 · Alligation & Mixtures", "Video 1 of 7")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        lesson = pill("Lesson 25  ·  Alligation & Mixtures", RATIO, size=LABEL)
        recap = VGroup(text("from Lesson 24  ·  Clock & Calendar", SMALL, MUTED),
                       fit_width(VGroup(pill("hands close at 5.5° a minute", WORD, size=LABEL), pill("calendars:  count the odd days", GOOD, size=LABEL)).arrange(RIGHT, buff=0.4), SAFE_W - 0.6)).arrange(DOWN, buff=0.25)
        title = fit_width(text("Mixtures as Weighted Averages", TITLE, INK, BOLD), SAFE_W - 0.4)
        today = text("today: the one idea every mixture question rests on", LABEL, FOCUS)
        block = VGroup(lesson, recap, title, today).arrange(DOWN, buff=0.55)
        fit_within(block, SAFE_W, SAFE_H - crumb.height - 0.9)
        block.next_to(crumb, DOWN, buff=0.6)
        self.no_overlap(crumb, lesson, recap, title, today)
        self.no_overlap(*recap[1])
        self.validator.check_in_frame(VGroup(crumb, block))

        n = self.narrate(
            id="intro_01",
            text="Now we start lesson twenty-five: alligation and mixtures.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.at_word(n, "twenty-five")
        self.play(FadeIn(lesson, scale=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="intro_02",
            text="In lesson twenty-four, the minute hand gained five and a half degrees a minute on the hour hand, and "
                 "calendars were solved by counting odd days.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "gained")
        self.play(FadeIn(recap[0]), FadeIn(recap[1][0], shift=UP * 0.1))
        self.at_word(n, "odd")
        self.play(FadeIn(recap[1][1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="intro_03",
            text="This first video is mixtures as weighted averages: the one idea every mixture question rests on.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "weighted")
        self.play(FadeIn(title, shift=UP * 0.1))
        self.at_word(n, "idea")
        self.play(FadeIn(today, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_intro")

    # ============================================== 1. HOOK ==========

    def hook(self):
        self.scene_start("S01_hook", title="Hook")

        head = self.heading("The tea blend")
        packs = VGroup(pill("3 kg of tea at ₹200 a kg", WORD, size=LABEL), pill("2 kg of tea at ₹300 a kg", WORD, size=LABEL)).arrange(RIGHT, buff=0.5)
        ask = pill("What does 1 kg of the blend cost?", FOCUS, size=BODY)
        guess = text("the quick guess:  halfway, ₹250", LABEL, MUTED)
        wrong = text("that guess is wrong, and the shop would overcharge on every packet", LABEL, INK, BOLD)
        self.stack(head, [packs, ask, guess, wrong], buff=0.6, top=0.8)
        self.no_overlap(*packs)

        n = self.narrate(
            id="hook_01",
            text="A shop blends three kilograms of tea costing two hundred rupees a kilogram with two kilograms costing "
                 "three hundred rupees a kilogram.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "three")
        self.play(FadeIn(packs[0], shift=UP * 0.1))
        self.at_word(n, "two", occurrence=2)
        self.play(FadeIn(packs[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_02",
            text="What does one kilogram of the blend cost?",
            voice="default",
            subtitle=True,
            pause_after=3.0,
        )
        self.at_word(n, "blend")
        self.play(FadeIn(ask, scale=1.03))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="hook_03",
            text="The quick guess is halfway, two hundred and fifty rupees. That guess is wrong, and the shop would "
                 "overcharge on every packet.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "halfway")
        self.play(FadeIn(guess, shift=UP * 0.1))
        self.at_word(n, "wrong")
        self.play(FadeIn(wrong, shift=UP * 0.1))
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
            text="First, find the value of a mixture as total value divided by total quantity.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "value")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "divided")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="objectives_03",
            text="Second, use the same idea for price and for concentration, by turning percentages into actual amounts.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "same")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "turning")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="objectives_04",
            text="Third, find a missing quantity when the mean of the mixture is given.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "missing")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "mean")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_objectives")

    # ============================================== 3. WHY THIS MATTERS ==========

    def why_this_matters(self):
        self.scene_start("S03_why_this_matters", title="Why This Matters")

        head = self.heading("Why this matters")
        kinds = VGroup(pill("price of a blend", WORD, size=LABEL), pill("strength of a solution", WORD, size=LABEL),
                       pill("purity of an alloy", WORD, size=LABEL)).arrange(RIGHT, buff=0.4)
        same = pill("each one is a weighted average", FOCUS, size=BODY)
        later = text("alligation and replacement, later in this lesson, are shortcuts built on it", LABEL, INK)
        self.stack(head, [kinds, same, later], buff=0.9, top=1.1)
        self.no_overlap(*kinds)

        n = self.narrate(
            id="why_this_matters_01",
            text="The price of a blend, the strength of a solution and the purity of an alloy look like three different "
                 "questions.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "price")
        self.play(FadeIn(kinds[0], shift=UP * 0.1))
        self.at_word(n, "strength")
        self.play(FadeIn(kinds[1], shift=UP * 0.1))
        self.at_word(n, "purity")
        self.play(FadeIn(kinds[2], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="why_this_matters_02",
            text="Each one is a weighted average.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "weighted")
        self.play(FadeIn(same, scale=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="why_this_matters_03",
            text="Alligation and replacement, later in this lesson, are shortcuts built on it.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "shortcuts")
        self.play(FadeIn(later, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_why_this_matters")

    # ============================================== 4. CONCEPT - THE WEIGHTED AVERAGE ==========

    def weighted_average(self):
        self.scene_start("S04_weighted_average", title="Concept - The Weighted Average")

        head = self.heading("The weighted average")
        blocks = two_line_blocks(STEPS_A, WORD)
        self.stack(head, list(blocks), buff=0.5, top=0.7, align=LEFT)

        n = self.narrate(
            id="weighted_average_01",
            text="The mean value of a mixture is its total value divided by its total quantity. Each value is weighted by "
                 "its quantity.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "total")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "weighted")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="weighted_average_02",
            text="The mean always lies between the two values, and it sits closer to the value that has the larger "
                 "quantity.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "between")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "closer")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="weighted_average_03",
            text="With equal quantities, the simple average works: four kilograms at thirty rupees and four at fifty give "
                 "forty rupees.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "equal")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "forty")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="weighted_average_04",
            text="With unequal quantities, the simple average fails. Five kilograms at forty and three at sixty cost two "
                 "hundred plus one hundred and eighty, divided by eight: forty-seven rupees fifty, not fifty.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "fails")
        self.play(FadeIn(blocks[3][0], shift=RIGHT * 0.2))
        self.at_word(n, "divided")
        self.play(FadeIn(blocks[3][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_weighted_average")

    # ============================================== 5. CONCEPT - CONCENTRATION AND MISSING QUANTITIES ==========

    def concentration(self):
        self.scene_start("S05_concentration", title="Concept - Concentration and Missing Quantities")

        head = self.heading("Concentration, and a missing quantity")
        blocks = two_line_blocks(STEPS_B, WORD)
        self.stack(head, list(blocks), buff=0.5, top=0.7, align=LEFT)

        n = self.narrate(
            id="concentration_01",
            text="For concentration, count the actual amount. Twenty percent of eight litres is one point six litres of "
                 "acid; percentages are never added directly.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "actual")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "litres")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="concentration_02",
            text="Add the amounts, then divide by the total volume: that is the strength of the mixture.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Add")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "strength")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="concentration_03",
            text="Water counts as zero percent, and a pure ingredient as one hundred percent. Adding water adds volume but "
                 "no acid, so the strength falls.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "zero")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "falls")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="concentration_04",
            text="For a missing quantity, balance the two sides. The cheaper part is below the mean, the dearer part is "
                 "above it, and the loss on one side equals the gain on the other.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "balance")
        self.play(FadeIn(blocks[3][0], shift=RIGHT * 0.2))
        self.at_word(n, "equals")
        self.play(FadeIn(blocks[3][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_concentration")

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
            text="Here is the formula box. The mean is the first quantity times its value, plus the second quantity times "
                 "its value, over the total quantity.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "box")
        self.play(FadeIn(box[0]))
        self.at_word(n, "mean")
        self.play(FadeIn(lines[0], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_box_02",
            text="The mean lies between the two values, nearer the larger quantity.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "between")
        self.play(FadeIn(lines[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_box_03",
            text="For equal quantities, it is the simple average.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "equal")
        self.play(FadeIn(lines[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_box_04",
            text="Strength is the total pure amount over the total volume, with water as zero percent and pure as one "
                 "hundred percent.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Strength")
        self.play(FadeIn(lines[3], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_box_05",
            text="And the balance: the first quantity times its distance from the mean equals the second quantity times "
                 "its distance.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "balance")
        self.play(FadeIn(lines[4], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_formula_box")

    # ============================================== 7. THE ANALOGY - TWO CLASS SECTIONS ==========

    def analogy(self):
        self.scene_start("S07_analogy", title="The Analogy - Two Class Sections")

        head = self.heading("Two sections of one class")
        secs = VGroup(pill("Section A:  40 students, average 60 marks", WORD, size=LABEL),
                      pill("Section B:  10 students, average 80 marks", WORD, size=LABEL)).arrange(RIGHT, buff=0.5)
        whole = text("the whole class:    (40 × 60 + 10 × 80)/50  =  64 marks", BODY, GOOD, BOLD)
        pull = text("not 70:  the bigger section pulls the average towards itself", LABEL, INK, BOLD)
        stops = VGroup(text("Where the analogy stops", LABEL, BAD, BOLD),
                       text("students are counted exactly; liquids are assumed to add up exactly too", LABEL, INK),
                       text("exam questions always assume that 2 L and 3 L make 5 L", LABEL, MUTED)).arrange(DOWN, buff=0.2)
        self.stack(head, [secs, whole, pull, stops], buff=0.55, top=0.7)
        self.no_overlap(*secs)

        n = self.narrate(
            id="analogy_01",
            text="Think of two sections of one class. Section A has forty students averaging sixty marks; section B has "
                 "ten students averaging eighty.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "sections")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "forty")
        self.play(FadeIn(secs[0], shift=UP * 0.1))
        self.at_word(n, "ten")
        self.play(FadeIn(secs[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_02",
            text="The whole class averages sixty-four marks, not seventy: the bigger section pulls the average towards "
                 "itself.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "sixty-four")
        self.play(FadeIn(whole, shift=UP * 0.1))
        self.at_word(n, "pulls")
        self.play(FadeIn(pull, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_03",
            text="Where the analogy stops: students are counted exactly, and liquids are assumed to add up exactly too. "
                 "Exam questions always assume that two litres and three litres make five litres.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "stops")
        self.play(FadeIn(stops[0], shift=UP * 0.1))
        self.at_word(n, "exactly")
        self.play(FadeIn(stops[1], shift=UP * 0.1))
        self.at_word(n, "assume")
        self.play(FadeIn(stops[2], shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S07_analogy")

    # ============================================== 8. WORKED EXAMPLE - CLOSING THE HOOK ==========

    def hook_solved(self):
        self.scene_start("S08_hook_solved", title="Worked Example - Closing the Hook")

        head = self.heading("The tea blend")
        panel = self.side_panel(["Mean  =\ntotal value ÷ total quantity", "M  =  (q1 × v1 + q2 × v2)\n÷ (q1 + q2)"])
        steps = self.solve_steps([("Total value:    3 × 200 + 2 × 300", "=  ₹1,200"),
                                  ("Total quantity:    3 + 2", "=  5 kg"),
                                  ("Price of the blend:    1,200 ÷ 5", "=  ₹240 a kg"),
                                  ("Not ₹250:    there is more of the ₹200 tea", "so the mean is nearer 200")])
        self.stack(head, [steps], top=1.0)
        self.no_overlap(*steps)

        n = self.narrate(
            id="hook_solved_01",
            text="The total value is three times two hundred plus two times three hundred: twelve hundred rupees.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(panel, shift=RIGHT * 0.2))
        self.at_word(n, "value")
        self.play(FadeIn(steps[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "twelve")
        self.play(FadeIn(steps[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_solved_02",
            text="The total quantity is three plus two, five kilograms.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "quantity")
        self.play(FadeIn(steps[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "five")
        self.play(FadeIn(steps[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_solved_03",
            text="So the blend costs twelve hundred divided by five: two hundred and forty rupees a kilogram.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "divided")
        self.play(FadeIn(steps[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "forty")
        self.play(FadeIn(steps[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_solved_04",
            text="It is not two hundred and fifty, because there is more of the cheaper tea, so the mean is nearer two "
                 "hundred.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "not")
        self.play(FadeIn(steps[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "nearer")
        self.play(FadeIn(steps[3][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S08_hook_solved")

    # ============================================== 9. A SECOND WORKED EXAMPLE - TWO ACID SOLUTIONS ==========

    def second_example(self):
        self.scene_start("S09_second_example", title="A Second Worked Example - Two Acid Solutions")

        head = self.heading("Two acid solutions")
        panel = self.side_panel(["Strength  =\ntotal pure amount\n÷ total volume", "Amount  =  % × volume"])
        ask = fitted_text("8 L of 20% acid is mixed with 12 L of 45% acid:    what is the strength of the mixture?", self.body_w() - 0.2, LABEL, MUTED, max_lines=3)
        steps = self.solve_steps([("Acid in the first:    20% of 8 L", "=  1.6 L"),
                                  ("Acid in the second:    45% of 12 L", "=  5.4 L"),
                                  ("Total acid 7 L in 20 L:    7 ÷ 20", "=  35%"),
                                  ("Check:    35% is between 20% and 45%", "nearer 45%, the larger part")])
        self.stack(head, [ask, steps], buff=0.7, top=0.7)
        self.no_overlap(*steps)

        n = self.narrate(
            id="second_example_01",
            text="Eight litres of twenty percent acid is mixed with twelve litres of forty-five percent acid. What is the "
                 "strength of the mixture?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Eight")
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(panel, shift=RIGHT * 0.2))
        self.at_word(n, "strength")
        self.play(FadeIn(ask, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_02",
            text="The acid in the first is twenty percent of eight litres: one point six litres.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "first")
        self.play(FadeIn(steps[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "point")
        self.play(FadeIn(steps[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_03",
            text="The acid in the second is forty-five percent of twelve litres: five point four litres.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "second")
        self.play(FadeIn(steps[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "point")
        self.play(FadeIn(steps[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_04",
            text="That is seven litres of acid in twenty litres: thirty-five percent.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "seven")
        self.play(FadeIn(steps[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "thirty-five")
        self.play(FadeIn(steps[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_05",
            text="Check: thirty-five lies between twenty and forty-five, nearer forty-five, the larger part.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Check")
        self.play(FadeIn(steps[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "nearer")
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
            text="Two prices: five kilograms at forty rupees and three at sixty. Two hundred plus one hundred and eighty, "
                 "over eight: forty-seven rupees fifty.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "prices")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "over")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_03",
            text="Equal quantities: four kilograms at thirty and four at fifty. The simple average: forty rupees.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Equal")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "simple")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_04",
            text="Concentration: eight litres of twenty percent and twelve litres of forty-five percent. Seven litres in "
                 "twenty: thirty-five percent.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Concentration")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "Seven")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Exam patterns  ·  4 to 6 of 6")
        blocks = self.pattern_blocks(PATTERNS[3:6])
        self.stack(head, list(blocks), buff=0.6, top=0.8, align=LEFT)

        n = self.narrate(
            id="exam_patterns_05",
            text="Adding water: thirty litres of forty percent acid and ten litres of water. Twelve litres of acid in "
                 "forty: thirty percent.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "water")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "Twelve")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_06",
            text="A missing quantity: how much at fifty rupees goes with ten kilograms at eighty to make sixty? X times "
                 "ten equals ten times twenty: twenty kilograms.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "missing")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "equals")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_07",
            text="Three parts: two kilograms at thirty, three at forty and five at sixty. Sixty plus one hundred and "
                 "twenty plus three hundred, over ten: forty-eight rupees.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "parts")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "over")
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
            text="Trap one: the simple average with unequal quantities. One litre of twenty percent juice is mixed with "
                 "four litres of seventy percent juice: find the strength.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "simple")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "mixed")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_02",
            text="The wrong instinct averages twenty and seventy: forty-five percent. The correct answer is zero point two "
                 "plus two point eight, over five: sixty percent.",
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
            text="The rule: weight every value by its quantity; average the values only when the quantities are equal.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "rule")
        self.play(FadeIn(rule, shift=UP * 0.1))
        self.wait_for_narration(n)
        self.clear_stage()

        head, q, wrong, right, rule = self.show_trap(TRAPS[1])

        n = self.narrate(
            id="traps_04",
            text="Trap two: adding the percentages. Ten litres of twenty percent syrup is mixed with ten litres of forty "
                 "percent syrup: find the strength.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "adding")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "mixed")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_05",
            text="The wrong instinct adds them: sixty percent. The correct answer is two plus four litres, in twenty: "
                 "thirty percent.",
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
            text="The rule: percentages are not added. Add the actual amounts, then divide by the total.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "rule")
        self.play(FadeIn(rule, shift=UP * 0.1))
        self.at_word(n, "divide")
        self.play(Indicate(rule, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)
        self.clear_stage()

        head, q, wrong, right, rule = self.show_trap(TRAPS[2])

        n = self.narrate(
            id="traps_07",
            text="Trap three: the old volume after adding water. Five litres of water is added to twenty litres of fifty "
                 "percent acid: find the new strength.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "old")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "added")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_08",
            text="The wrong instinct keeps ten over twenty: fifty percent, unchanged. The correct answer is ten over "
                 "twenty-five: forty percent.",
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
            text="The rule: water adds no acid, but it adds volume. Divide by the new total volume.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "rule")
        self.play(FadeIn(rule, shift=UP * 0.1))
        self.at_word(n, "new")
        self.play(Indicate(rule, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S11_traps")

    # ============================================== 12. CHECKPOINT ==========

    def checkpoint(self):
        self.scene_start("S12_checkpoint", title="Checkpoint")

        head = self.heading("Checkpoint  ·  your turn")
        given = pill("4 kg of sugar at ₹30 a kg is mixed with 6 kg at ₹50 a kg:   price of the mixture?", FOCUS, size=LABEL)
        work = VGroup(text("(120 + 300)/10", BODY, INK, BOLD), text("=  ₹42 a kg", BODY, GOOD, BOLD)).arrange(RIGHT, buff=0.6)
        self.stack(head, [given, work], buff=1.0, top=1.0)
        self.no_overlap(*work)

        n = self.narrate(
            id="checkpoint_01",
            text="Your turn. Four kilograms of sugar at thirty rupees a kilogram is mixed with six kilograms at fifty "
                 "rupees. Find the price of the mixture.",
            voice="default",
            subtitle=True,
            pause_after=10.0,
        )
        self.at_word(n, "turn")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "Four")
        self.play(FadeIn(given, scale=1.03))
        self.at_word(n, "price")
        self.play(Indicate(given, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="checkpoint_02",
            text="One hundred and twenty plus three hundred, over ten, is forty-two rupees a kilogram.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "over")
        self.play(FadeIn(work[0], shift=UP * 0.1))
        self.at_word(n, "forty-two")
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
            text="Level one, question one: five kilograms of rice at forty rupees a kilogram is mixed with five kilograms "
                 "at sixty; find the price of the mixture. Question two: two litres of ten percent sugar solution is mixed "
                 "with three litres of twenty percent; find the strength.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "rice")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "sugar")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="practice_02",
            text="Level two, question three: six kilograms of dal at twenty-five rupees is mixed with four kilograms at "
                 "fifty; find the price. Question four: five litres of water is added to fifteen litres of thirty percent "
                 "alcohol; find the new strength. Question five: ten litres of forty percent acid is mixed with thirty "
                 "litres of sixty percent acid; find the strength.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "dal")
        self.play(FadeIn(rows[2], shift=RIGHT * 0.2))
        self.at_word(n, "water")
        self.play(FadeIn(rows[3], shift=RIGHT * 0.2))
        self.at_word(n, "acid")
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
            text="Level three, question six: how many kilograms of tea at ninety rupees must be mixed with twelve "
                 "kilograms at sixty to make a mixture worth seventy? Question seven: twenty litres of milk and water in "
                 "the ratio three to one is mixed with thirty litres in the ratio four to one; find the percentage of "
                 "milk. Question eight: twenty-six kilograms of rice at twenty rupees is mixed with thirty kilograms at "
                 "thirty-six and sold at thirty rupees a kilogram; find the profit percent.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "tea")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "milk")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.at_word(n, "sold")
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
            text="One: equal quantities, so the simple average: fifty rupees a kilogram.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "equal")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "fifty")
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_02",
            text="Two: zero point two plus zero point six is zero point eight litres of sugar in five litres: sixteen "
                 "percent.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "plus")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "sixteen")
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_03",
            text="Three: one hundred and fifty plus two hundred, over ten: thirty-five rupees a kilogram.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "plus")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "thirty-five")
        self.play(FadeIn(rows[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_04",
            text="Four: four point five litres of alcohol in twenty litres: twenty-two point five percent.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "alcohol")
        self.play(FadeIn(rows[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "twenty-two")
        self.play(FadeIn(rows[3][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Answer key  ·  5 to 8", GOOD)
        table, rows = self.answer_table(head, ANSWERS_B, 5)

        n = self.narrate(
            id="answers_05",
            text="Five: four plus eighteen is twenty-two litres of acid in forty: fifty-five percent.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "plus")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "fifty-five")
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_06",
            text="Six: balance the sides. Twelve times ten equals x times twenty, so x is six kilograms.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "balance")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "six", occurrence=2)
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_07",
            text="Seven: the milk is fifteen plus twenty-four, thirty-nine litres in fifty: seventy-eight percent.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "milk")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "seventy-eight")
        self.play(FadeIn(rows[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_08",
            text="Eight: the cost is five hundred and twenty plus one thousand and eighty, sixteen hundred rupees. The "
                 "sale is fifty-six times thirty, sixteen hundred and eighty: a profit of eighty on sixteen hundred, five "
                 "percent.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "cost")
        self.play(FadeIn(rows[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "profit")
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
            text="Recognise and move. The recognition cue: mixed, mixture worth, price of the mixture or strength of the "
                 "mixture, with both quantities given.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "cue")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "mixed")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_lens_02",
            text="The target time: thirty to forty seconds.",
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
            text="The sanity check: the mean lies between the two values, and nearer the one with the larger quantity.",
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

    # ============================================== 16. QUICK REVISION AND SUMMARY ==========

    def summary(self):
        self.scene_start("S16_summary", title="Quick Revision and Summary")

        head = self.heading("Quick revision")
        main = pill("value of a mixture  =  total value ÷ total quantity", GOOD, size=LABEL)
        row = VGroup(pill("between the two values", WORD, size=SMALL), pill("nearer the larger quantity", WORD, size=SMALL),
                     pill("equal quantities:  simple average", WORD, size=SMALL)).arrange(RIGHT, buff=0.3)
        fit_width(row, SAFE_W - 0.4)
        conc = pill("concentration:   add the actual amounts, divide by the total volume", RATIO, size=LABEL)
        sections = text("remember the two class sections:  the bigger one pulls the average", LABEL, MUTED)
        nxt = self.breadcrumb("Next", "Video 2 · Alligation Rule")
        self.stack(head, [main, row, conc, sections, nxt], buff=0.6, top=0.7)
        self.no_overlap(*row)

        n = self.narrate(
            id="summary_01",
            text="The value of a mixture is its total value divided by its total quantity.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "total")
        self.play(FadeIn(main, scale=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_02",
            text="It lies between the two values, nearer the larger quantity, and equal quantities give the simple "
                 "average.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "between")
        self.play(FadeIn(row[0], shift=UP * 0.1))
        self.at_word(n, "nearer")
        self.play(FadeIn(row[1], shift=UP * 0.1))
        self.at_word(n, "equal")
        self.play(FadeIn(row[2], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_03",
            text="For concentration, add the actual amounts and divide by the total volume.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "amounts")
        self.play(FadeIn(conc, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_04",
            text="Remember the two class sections: the bigger one pulls the average.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "sections")
        self.play(FadeIn(sections, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_05",
            text="Next: the alligation rule.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Next")
        self.play(FadeIn(nxt, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S16_summary")

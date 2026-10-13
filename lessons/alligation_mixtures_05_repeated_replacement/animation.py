"""
animation.py for the LMS video generator.

Course : Pre-C-CAT - Section A - Quantitative Aptitude
Video  : Lesson 25 - Alligation & Mixtures - 05 - Repeated Replacement

Source script:
  C:\\Scripts\\Section A\\Module2\\S21-25_Ratio_Age_Clock_Mixtures_Mensuration\\Lesson 25 - Allegation & Mixtures\\01 - Repeated Replacement.pdf

Built on the golden-reference pattern:
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``;
  * layouts stacked with next_to and guarded with ``no_overlap``; nothing is
    ever animated onto or into another box.

Lesson 25, Video 5 of 7 (the lesson's own order, from its Pre-Lesson Brief). Not the first video of the lesson: a silent
breadcrumb, a one-line recap of Video 4, then today's topic. No spoken course welcome.
The seven source scripts of this lesson are identical apart from their titles, so, as agreed with the course owner, each video was
written for its own topic. This one covers the script's rule "after n replacements, original fraction = (1 - r)^n", its questions
(20 L, 5 L replaced twice: 9/16;  50 L, 10 L replaced twice: 16/25) and its trap "forgetting repeated replacement compounds",
with further verified questions. Powers are written with ^ on screen and spoken as "squared" or "cubed".
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


def after(total, removed, times):
    """Original liquid left after ``times`` rounds of removing ``removed`` and refilling with water."""
    return total * (1 - F(removed, total)) ** times


# ---- hook, examples, patterns ----
assert after(50, 10, 2) == 32 and (1 - F(10, 50)) ** 2 == F(16, 25) and 50 - 10 - 10 == 30
assert after(40, 4, 3) == F(729, 25) and float(after(40, 4, 3)) == 29.16
assert F(32, 50 - 32) == F(16, 9) and after(80, 20, 2) == 45 and F(45, 80) == F(9, 16)
assert (1 - F(8, 40)) ** 2 == F(16, 25) and F(16, 25 - 16) == F(16, 9)
assert 60 * (1 - F(12, 60)) * (1 - F(15, 60)) == 36
# ---- traps and checkpoint ----
assert F(1, 5) ** 2 == F(1, 25) and after(20, 5, 2) == F(45, 4) and (1 - F(5, 20)) ** 2 == F(9, 16)
# ---- practice ----
assert 1 - F(5, 20) == F(3, 4) and after(100, 10, 3) == F(729, 10)
assert after(64, 16, 2) == 36 and F(36, 64 - 36) == F(9, 7)
assert after(45, 15, 2) == 20 and (1 - F(6, 36)) ** 2 == F(25, 36) and F(25, 36 - 25) == F(25, 11)
assert 80 * (1 - F(16, 80)) * (1 - F(20, 80)) == 48

OBJECTIVES = [("Find what is left after the same replacement is done n times", "with the fraction left raised to the power n"),
              ("Give the final ratio of the two liquids", "from the fraction of the original that remains"),
              ("Work backwards", "to the amount drawn each time, or to the size of the vessel")]
STEPS_A = [("Each round keeps the same fraction", "50 L, 10 L replaced:    every round keeps  1 − 10/50  =  4/5  of the milk"),
           ("The rounds multiply", "after two rounds  4/5 × 4/5 = 16/25;    after three rounds  (4/5)^3 = 64/125"),
           ("Original left  =  V × (1 − x/V)^n", "V = volume of the vessel,   x = amount replaced each time,   n = number of rounds"),
           ("It compounds, like depreciation", "each round removes a fifth of what is there then, which is less milk every time")]
STEPS_B = [("The other liquid is the rest of the vessel", "50 L with 32 L of milk left:    water  =  50 − 32  =  18 L"),
           ("Fraction to ratio:  the rest is the other part", "16/25 milk  means  milk : water  =  16 : 9,   not 16 : 25"),
           ("Different amounts each round:  multiply different fractions", "60 L;  12 L, then 15 L replaced:    60 × 4/5 × 3/4  =  36 L"),
           ("Backwards:  take the root of the final fraction", "two rounds leave 9/16:    one round keeps 3/4,  so a quarter is drawn each time")]
FORMULAS = ["Original liquid left   =   V × (1 − x/V)^n",
            "Fraction of the original left   =   (1 − x/V)^n",
            "The other liquid   =   V − (original left)",
            "Final ratio   =   (fraction left) : (1 − fraction left)",
            "Backwards:      1 − x/V   =   the n-th root of the final fraction"]
PATTERNS = [("Twice", "50 L of milk;  10 L replaced with water, twice", "50 × (4/5)^2", "32 L"),
            ("Three times", "40 L of milk;  4 L replaced with water, three times", "40 × (9/10)^3", "29.16 L"),
            ("Final ratio", "50 L of milk;  10 L replaced twice;  milk : water?", "32 L and 18 L", "16 : 9"),
            ("Find the amount drawn", "80 L of milk;  after two equal rounds 45 L of milk is left", "(1 − x/80)^2 = 9/16;    3/4 stays", "20 L"),
            ("Find the vessel", "8 L replaced twice leaves milk : water 16 : 9", "(1 − 8/V)^2 = 16/25;    8/V = 1/5", "40 L"),
            ("Different amounts", "60 L of milk;  12 L, then 15 L replaced with water", "60 × 4/5 × 3/4", "36 L")]
TRAPS = [("Trap 1  ·  subtracting instead of compounding",
          "10 L of a 50 L vessel of milk is replaced with water, twice.  How much milk is left?",
          "50 − 10 − 10  =  30 L", "50 × (4/5)^2  =  32 L",
          "The second 10 L is not all milk.  Multiply by the fraction left each round."),
         ("Trap 2  ·  the removed fraction raised to the power",
          "10 L of a 50 L vessel of milk is replaced with water, twice.  What fraction is milk?",
          "(1/5)^2  =  1/25", "(4/5)^2  =  16/25",
          "Raise the fraction that stays, 1 − x/V, to the power, never the fraction removed."),
         ("Trap 3  ·  the fraction left read as the ratio",
          "After two rounds, 16/25 of a vessel is milk.  Find the ratio of milk to water.",
          "16 : 25", "16 : 9",
          "A fraction compares with the whole; a ratio compares the two parts.  Water is 9/25.")]
PRACTICE_A = [("L1", "5 L of a 20 L mixture is removed and replaced with water.  What fraction of the original is left?"),
              ("L1", "5 L of a 20 L mixture is removed and replaced with water, twice.  What fraction of the original is left?"),
              ("L2", "10 L of a 50 L vessel of milk is removed and replaced with water, twice.  How much milk is left?"),
              ("L2", "10 L of a 100 L vessel of acid is removed and replaced with water, three times.  How much acid is left?"),
              ("L2", "16 L of a 64 L vessel of milk is removed and replaced with water, twice.  Find the ratio of milk to water.")]
PRACTICE_B = [("L3", "A 45 L vessel is full of milk.  The same amount is replaced with water twice, leaving 20 L of milk.  How much each time?"),
              ("L3", "6 L of a vessel full of wine is replaced with water, twice.  Wine : water is now 25 : 11.  Find the capacity."),
              ("L3", "From an 80 L vessel of milk, 16 L is replaced with water, and then 20 L is replaced with water.  How much milk is left?")]
ANSWERS_A = [("1 − 5/20", "3/4"),
             ("(3/4)^2", "9/16"),
             ("50 × (4/5)^2  =  50 × 16/25", "32 L"),
             ("100 × (9/10)^3  =  100 × 729/1,000", "72.9 L")]
ANSWERS_B = [("Milk  64 × (3/4)^2 = 36 L;      water  64 − 36 = 28 L", "9 : 7"),
             ("(1 − x/45)^2  =  20/45  =  4/9;      2/3 stays;      x = 1/3 of 45", "15 L"),
             ("Wine is 25/36;      1 − 6/V = 5/6;      6/V = 1/6", "36 L"),
             ("80 × (1 − 16/80) × (1 − 20/80)  =  80 × 4/5 × 3/4", "48 L")]
LENS = [("Recognition cue", "“the process is repeated”, “done twice”, “three times”, “again replaced with water”"),
        ("Target time", "40 seconds;  60 seconds when working backwards"),
        ("Sanity check", "more is left than by plain subtraction (32 L, not 30 L), and the fraction left is below 1")]


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


class RepeatedReplacementVideo(LMSScene):
    lesson_title = "Repeated Replacement"

    def construct(self):
        self.camera.background_color = BG

        self.intro()
        self.hook()
        self.objectives()
        self.why_this_matters()
        self.the_power()
        self.ratio_and_backwards()
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

        crumb = self.breadcrumb("Quantitative Aptitude", "Lesson 25 · Alligation & Mixtures", "Video 5 of 7")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        recap = VGroup(text("last video", SMALL, MUTED), pill("one replacement:  fraction left  =  1 − removed/total", WORD, size=LABEL)).arrange(DOWN, buff=0.25)
        title = fit_width(text("Repeated Replacement", TITLE, INK, BOLD), SAFE_W - 0.4)
        today = text("today: the same replacement, again and again", LABEL, FOCUS)
        block = VGroup(recap, title, today).arrange(DOWN, buff=0.7)
        fit_within(block, SAFE_W, SAFE_H - crumb.height - 0.9)
        block.next_to(crumb, DOWN, buff=0.7)
        self.no_overlap(crumb, recap, title, today)
        self.validator.check_in_frame(VGroup(crumb, block))

        n = self.narrate(
            id="intro_01",
            text="In the last video, one replacement left one minus removed over total of every ingredient.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.at_word(n, "minus")
        self.play(FadeIn(recap, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="intro_02",
            text="Today: repeated replacement, where the same replacement is done again and again.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "repeated")
        self.play(FadeIn(title, shift=UP * 0.1))
        self.at_word(n, "again")
        self.play(FadeIn(today, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_intro")

    # ============================================== 1. HOOK ==========

    def hook(self):
        self.scene_start("S01_hook", title="Hook")

        head = self.heading("The milk can")
        can = pill("a can holds 50 L of pure milk", WORD, size=LABEL)
        act = pill("10 L is sold and replaced with water;  then the same is done again", WORD, size=LABEL)
        ask = pill("How much milk is left in the can?", FOCUS, size=BODY)
        guess = text("the quick answer, 50 − 10 − 10 = 30 L, is wrong", LABEL, INK, BOLD)
        self.stack(head, [can, act, ask, guess], buff=0.6, top=0.8)

        n = self.narrate(
            id="hook_01",
            text="A can holds fifty litres of pure milk. Ten litres is sold and replaced with water, and then the same is "
                 "done again.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "can")
        self.play(FadeIn(can, shift=UP * 0.1))
        self.at_word(n, "sold")
        self.play(FadeIn(act, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_02",
            text="How much milk is left in the can?",
            voice="default",
            subtitle=True,
            pause_after=3.0,
        )
        self.at_word(n, "left")
        self.play(FadeIn(ask, scale=1.03))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="hook_03",
            text="The quick answer, fifty minus ten minus ten, thirty litres, is wrong.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "wrong")
        self.play(FadeIn(guess, shift=UP * 0.1))
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
            text="First, find what is left after the same replacement is done n times, with the fraction left raised to "
                 "the power n.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "left")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "power")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="objectives_03",
            text="Second, give the final ratio of the two liquids from the fraction of the original that remains.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "ratio")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "remains")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="objectives_04",
            text="Third, work backwards to the amount drawn each time, or to the size of the vessel.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "backwards")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "amount")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_objectives")

    # ============================================== 3. WHY THIS MATTERS ==========

    def why_this_matters(self):
        self.scene_start("S03_why_this_matters", title="Why This Matters")

        head = self.heading("Why this matters")
        second = text("the second time, you are not removing pure milk any more", LABEL, INK)
        mixed = pill("you remove a mixture, so less milk leaves each round", FOCUS, size=LABEL)
        power = text("that is why the answer is a power, not a subtraction", LABEL, INK, BOLD)
        fav = text("it is one of the most repeated mixture questions in aptitude tests", LABEL, MUTED)
        self.stack(head, [second, mixed, power, fav], buff=0.8, top=1.1)

        n = self.narrate(
            id="why_this_matters_01",
            text="The second time, you are not removing pure milk any more. You remove a mixture, so less milk leaves each "
                 "round.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "second")
        self.play(FadeIn(second, shift=UP * 0.1))
        self.at_word(n, "mixture")
        self.play(FadeIn(mixed, scale=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="why_this_matters_02",
            text="That is why the answer is a power, not a subtraction.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "power")
        self.play(FadeIn(power, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="why_this_matters_03",
            text="It is one of the most repeated mixture questions in aptitude tests.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "repeated")
        self.play(FadeIn(fav, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_why_this_matters")

    # ============================================== 4. CONCEPT - THE FRACTION LEFT, TO A POWER ==========

    def the_power(self):
        self.scene_start("S04_the_power", title="Concept - The Fraction Left, to a Power")

        head = self.heading("The fraction left, to a power")
        blocks = two_line_blocks(STEPS_A, WORD)
        self.stack(head, list(blocks), buff=0.5, top=0.7, align=LEFT)

        n = self.narrate(
            id="the_power_01",
            text="Each round keeps the same fraction. With fifty litres and ten litres replaced, every round keeps one "
                 "minus ten over fifty, four fifths, of the milk.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "keeps")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "fifths")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="the_power_02",
            text="The rounds multiply. After two rounds, four fifths times four fifths is sixteen twenty-fifths; after "
                 "three rounds, four fifths cubed is sixty-four over one hundred and twenty-five.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "multiply")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "sixteen")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="the_power_03",
            text="So the original liquid left is V times one minus x over V, to the power n. V is the volume of the "
                 "vessel, x is the amount replaced each time, and n is the number of rounds.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "original")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "volume")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="the_power_04",
            text="It compounds, like depreciation. Each round removes a fifth of what is there then, which is less milk "
                 "every time.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "compounds")
        self.play(FadeIn(blocks[3][0], shift=RIGHT * 0.2))
        self.at_word(n, "less")
        self.play(FadeIn(blocks[3][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_the_power")

    # ============================================== 5. CONCEPT - THE RATIO, AND WORKING BACKWARDS ==========

    def ratio_and_backwards(self):
        self.scene_start("S05_ratio_and_backwards", title="Concept - The Ratio, and Working Backwards")

        head = self.heading("The ratio, and working backwards")
        blocks = two_line_blocks(STEPS_B, WORD)
        self.stack(head, list(blocks), buff=0.5, top=0.7, align=LEFT)

        n = self.narrate(
            id="ratio_and_backwards_01",
            text="The other liquid is the rest of the vessel. Fifty litres with thirty-two litres of milk left has "
                 "eighteen litres of water.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "rest")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "eighteen")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="ratio_and_backwards_02",
            text="From a fraction to a ratio, the rest is the other part. Sixteen twenty-fifths milk means milk to water "
                 "is sixteen to nine, not sixteen to twenty-five.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "ratio")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "nine")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="ratio_and_backwards_03",
            text="With different amounts each round, multiply different fractions. Sixty litres, with twelve and then "
                 "fifteen litres replaced, leaves sixty times four fifths times three quarters: thirty-six litres.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "different")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "leaves")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="ratio_and_backwards_04",
            text="Backwards, take the root of the final fraction. If two rounds leave nine sixteenths, one round keeps "
                 "three quarters, so a quarter is drawn each time.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "root")
        self.play(FadeIn(blocks[3][0], shift=RIGHT * 0.2))
        self.at_word(n, "keeps")
        self.play(FadeIn(blocks[3][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_ratio_and_backwards")

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
            text="Here is the formula box. The original liquid left is V times one minus x over V, to the power n.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "box")
        self.play(FadeIn(box[0]))
        self.at_word(n, "original")
        self.play(FadeIn(lines[0], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_box_02",
            text="The fraction of the original left is one minus x over V, to the power n.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "fraction")
        self.play(FadeIn(lines[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_box_03",
            text="The other liquid is V minus the original left.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "other")
        self.play(FadeIn(lines[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_box_04",
            text="The final ratio is the fraction left to one minus the fraction left.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "ratio")
        self.play(FadeIn(lines[3], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_box_05",
            text="And backwards, one minus x over V is the n-th root of the final fraction.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "root")
        self.play(FadeIn(lines[4], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_formula_box")

    # ============================================== 7. THE ANALOGY - A CAR LOSING VALUE ==========

    def analogy(self):
        self.scene_start("S07_analogy", title="The Analogy - A Car Losing Value")

        head = self.heading("A car losing value")
        car = pill("a ₹5,00,000 car loses a fifth of its value every year", WORD, size=LABEL)
        years = text("after one year  ₹4,00,000;    after two years  ₹3,20,000,  not ₹3,00,000", LABEL, GOOD, BOLD)
        why = text("the second year takes a fifth of the smaller value;  the second 10 L takes a fifth of the weaker milk", LABEL, INK)
        stops = VGroup(text("Where the analogy stops", LABEL, BAD, BOLD),
                       text("a car's value just disappears;  here the lost milk is replaced by water", LABEL, INK),
                       text("so the can stays full, and the water is what the milk has lost", LABEL, MUTED)).arrange(DOWN, buff=0.2)
        fit_width(why, SAFE_W - 0.6)
        self.stack(head, [car, years, why, stops], buff=0.55, top=0.7)

        n = self.narrate(
            id="analogy_01",
            text="Think of a car worth five lakh rupees that loses a fifth of its value every year. After one year it is "
                 "worth four lakh; after two years, three lakh twenty thousand, not three lakh.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "car")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "fifth")
        self.play(FadeIn(car, shift=UP * 0.1))
        self.at_word(n, "twenty")
        self.play(FadeIn(years, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_02",
            text="The second year takes a fifth of the smaller value, just as the second ten litres takes a fifth of the "
                 "weaker milk.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "smaller")
        self.play(FadeIn(why, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_03",
            text="Where the analogy stops: a car's value just disappears, but here the lost milk is replaced by water. So "
                 "the can stays full, and the water is exactly what the milk has lost.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "stops")
        self.play(FadeIn(stops[0], shift=UP * 0.1))
        self.at_word(n, "disappears")
        self.play(FadeIn(stops[1], shift=UP * 0.1))
        self.at_word(n, "full")
        self.play(FadeIn(stops[2], shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S07_analogy")

    # ============================================== 8. WORKED EXAMPLE - CLOSING THE HOOK ==========

    def hook_solved(self):
        self.scene_start("S08_hook_solved", title="Worked Example - Closing the Hook")

        head = self.heading("50 L of milk;  10 L replaced, twice")
        panel = self.side_panel(["Original left  =\nV × (1 − x/V)^n", "V = 50,   x = 10,   n = 2"])
        steps = self.solve_steps([("Fraction left each round:    1 − 10/50", "=  4/5"),
                                  ("After two rounds:    (4/5)^2", "=  16/25"),
                                  ("Milk left:    50 × 16/25", "=  32 L"),
                                  ("Water:    50 − 32 = 18 L;      milk : water", "=  16 : 9"),
                                  ("Round by round:    50  →  40  →  32", "the second round took only 8 L of milk")])
        self.stack(head, [steps], top=0.8)
        self.no_overlap(*steps)

        n = self.narrate(
            id="hook_solved_01",
            text="The fraction left each round is one minus ten over fifty: four fifths.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(panel, shift=RIGHT * 0.2))
        self.at_word(n, "minus")
        self.play(FadeIn(steps[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "fifths")
        self.play(FadeIn(steps[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_solved_02",
            text="After two rounds, four fifths squared is sixteen twenty-fifths.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "squared")
        self.play(FadeIn(steps[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "sixteen")
        self.play(FadeIn(steps[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_solved_03",
            text="So the milk left is fifty times sixteen twenty-fifths: thirty-two litres.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "times")
        self.play(FadeIn(steps[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "thirty-two")
        self.play(FadeIn(steps[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_solved_04",
            text="The water is fifty minus thirty-two, eighteen litres, so milk to water is sixteen to nine.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "water")
        self.play(FadeIn(steps[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "nine")
        self.play(FadeIn(steps[3][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_solved_05",
            text="Round by round, the milk goes fifty, forty, thirty-two: the second round took only eight litres of milk.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Round")
        self.play(FadeIn(steps[4][:2], shift=RIGHT * 0.2))
        self.at_word(n, "only")
        self.play(FadeIn(steps[4][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S08_hook_solved")

    # ============================================== 9. A SECOND WORKED EXAMPLE - THREE ROUNDS ==========

    def second_example(self):
        self.scene_start("S09_second_example", title="A Second Worked Example - Three Rounds")

        head = self.heading("Three rounds")
        panel = self.side_panel(["Original left  =\nV × (1 − x/V)^n", "V = 40,   x = 4,   n = 3"])
        ask = fitted_text("4 L of a 40 L vessel of milk is replaced with water, three times:    how much milk is left?", self.body_w() - 0.2, LABEL, MUTED, max_lines=3)
        steps = self.solve_steps([("Fraction left each round:    1 − 4/40", "=  9/10"),
                                  ("After three rounds:    (9/10)^3", "=  729/1,000"),
                                  ("Milk left:    40 × 729/1,000", "=  29.16 L"),
                                  ("Plain subtraction would give 40 − 12 = 28 L", "too low")])
        self.stack(head, [ask, steps], buff=0.7, top=0.7)
        self.no_overlap(*steps)

        n = self.narrate(
            id="second_example_01",
            text="Four litres of a forty litre vessel of milk is replaced with water, three times. How much milk is left?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Four")
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(panel, shift=RIGHT * 0.2))
        self.at_word(n, "replaced")
        self.play(FadeIn(ask, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_02",
            text="The fraction left each round is one minus four over forty: nine tenths.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "minus")
        self.play(FadeIn(steps[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "tenths")
        self.play(FadeIn(steps[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_03",
            text="After three rounds, nine tenths cubed is seven hundred and twenty-nine over one thousand.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "cubed")
        self.play(FadeIn(steps[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "over")
        self.play(FadeIn(steps[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_04",
            text="So the milk left is forty times that: twenty-nine point one six litres.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "times")
        self.play(FadeIn(steps[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "point")
        self.play(FadeIn(steps[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_05",
            text="Plain subtraction would give forty minus twelve, twenty-eight litres, which is too low.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "subtraction")
        self.play(FadeIn(steps[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "low")
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
            text="Twice: fifty litres of milk, with ten litres replaced with water, twice. Fifty times four fifths "
                 "squared: thirty-two litres.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Twice")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "squared")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_03",
            text="Three times: forty litres of milk, with four litres replaced three times. Forty times nine tenths cubed: "
                 "twenty-nine point one six litres.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Three")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "cubed")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_04",
            text="The final ratio: fifty litres, ten replaced twice. Thirty-two litres of milk and eighteen of water: "
                 "sixteen to nine.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "ratio")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "eighteen")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Exam patterns  ·  4 to 6 of 6")
        blocks = self.pattern_blocks(PATTERNS[3:6])
        self.stack(head, list(blocks), buff=0.6, top=0.8, align=LEFT)

        n = self.narrate(
            id="exam_patterns_05",
            text="Find the amount drawn: eighty litres of milk, and after two equal rounds forty-five litres is left. The "
                 "fraction left is nine sixteenths, so three quarters stays each time: twenty litres are drawn.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "drawn")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "stays")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_06",
            text="Find the vessel: eight litres replaced twice leaves milk to water sixteen to nine. Sixteen twenty-fifths "
                 "is left, so four fifths stays, and eight litres is one fifth: forty litres.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "vessel")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "stays")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_07",
            text="Different amounts: sixty litres of milk, with twelve and then fifteen litres replaced. Sixty times four "
                 "fifths times three quarters: thirty-six litres.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Different")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "times")
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
            text="Trap one: subtracting instead of compounding. Ten litres of a fifty litre vessel of milk is replaced "
                 "with water, twice: how much milk is left?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "subtracting")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "replaced")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_02",
            text="The wrong instinct subtracts ten twice: thirty litres. The correct answer is fifty times four fifths "
                 "squared: thirty-two litres.",
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
            text="The rule: the second ten litres is not all milk. Multiply by the fraction left each round.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "rule")
        self.play(FadeIn(rule, shift=UP * 0.1))
        self.at_word(n, "Multiply")
        self.play(Indicate(rule, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)
        self.clear_stage()

        head, q, wrong, right, rule = self.show_trap(TRAPS[1])

        n = self.narrate(
            id="traps_04",
            text="Trap two: the removed fraction raised to the power. The same vessel, replaced twice: what fraction is "
                 "milk?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "removed")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "fraction", occurrence=2)
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_05",
            text="The wrong instinct squares one fifth: one twenty-fifth. The correct answer squares four fifths: sixteen "
                 "twenty-fifths.",
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
            text="The rule: raise the fraction that stays to the power, never the fraction removed.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "rule")
        self.play(FadeIn(rule, shift=UP * 0.1))
        self.wait_for_narration(n)
        self.clear_stage()

        head, q, wrong, right, rule = self.show_trap(TRAPS[2])

        n = self.narrate(
            id="traps_07",
            text="Trap three: the fraction left read as the ratio. After two rounds, sixteen twenty-fifths of a vessel is "
                 "milk: find the ratio of milk to water.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "read")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "rounds")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_08",
            text="The wrong instinct writes sixteen to twenty-five. The correct answer is sixteen to nine.",
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
            text="The rule: a fraction compares with the whole; a ratio compares the two parts. The water is nine "
                 "twenty-fifths.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "rule")
        self.play(FadeIn(rule, shift=UP * 0.1))
        self.at_word(n, "water")
        self.play(Indicate(rule, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S11_traps")

    # ============================================== 12. CHECKPOINT ==========

    def checkpoint(self):
        self.scene_start("S12_checkpoint", title="Checkpoint")

        head = self.heading("Checkpoint  ·  your turn")
        given = pill("5 L of a 20 L vessel of juice is replaced with water, twice:   juice left?", FOCUS, size=LABEL)
        work = VGroup(text("20 × (3/4)^2  =  20 × 9/16", BODY, INK, BOLD), text("=  11.25 L", BODY, GOOD, BOLD)).arrange(RIGHT, buff=0.6)
        self.stack(head, [given, work], buff=1.0, top=1.0)
        self.no_overlap(*work)

        n = self.narrate(
            id="checkpoint_01",
            text="Your turn. Five litres of a twenty litre vessel of juice is replaced with water, twice. How much juice "
                 "is left?",
            voice="default",
            subtitle=True,
            pause_after=10.0,
        )
        self.at_word(n, "turn")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "Five")
        self.play(FadeIn(given, scale=1.03))
        self.at_word(n, "much")
        self.play(Indicate(given, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="checkpoint_02",
            text="Twenty times three quarters squared is twenty times nine sixteenths: eleven and a quarter litres.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "squared")
        self.play(FadeIn(work[0], shift=UP * 0.1))
        self.at_word(n, "eleven")
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
            text="Level one, question one: five litres of a twenty litre mixture is removed and replaced with water; what "
                 "fraction of the original is left? Question two: the same replacement is done twice; what fraction of the "
                 "original is left?",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "mixture")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "twice")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="practice_02",
            text="Level two, question three: ten litres of a fifty litre vessel of milk is replaced with water, twice; how "
                 "much milk is left? Question four: ten litres of a one hundred litre vessel of acid is replaced with "
                 "water, three times; how much acid is left? Question five: sixteen litres of a sixty-four litre vessel of "
                 "milk is replaced with water, twice; find the ratio of milk to water.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "milk")
        self.play(FadeIn(rows[2], shift=RIGHT * 0.2))
        self.at_word(n, "acid")
        self.play(FadeIn(rows[3], shift=RIGHT * 0.2))
        self.at_word(n, "sixteen")
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
            text="Level three, question six: a forty-five litre vessel is full of milk, and the same amount is replaced "
                 "with water twice, leaving twenty litres of milk; how much is replaced each time? Question seven: six "
                 "litres of a vessel full of wine is replaced with water, twice, and wine to water is now twenty-five to "
                 "eleven; find the capacity. Question eight: from an eighty litre vessel of milk, sixteen litres is "
                 "replaced with water, and then twenty litres; how much milk is left?",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "forty-five")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "wine")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.at_word(n, "eighty")
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
            text="Two: three quarters squared: nine sixteenths.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "squared")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "nine")
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_03",
            text="Three: fifty times sixteen twenty-fifths: thirty-two litres.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "times")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "thirty-two")
        self.play(FadeIn(rows[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_04",
            text="Four: one hundred times nine tenths cubed: seventy-two point nine litres.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "cubed")
        self.play(FadeIn(rows[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "seventy-two")
        self.play(FadeIn(rows[3][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Answer key  ·  5 to 8", GOOD)
        table, rows = self.answer_table(head, ANSWERS_B, 5)

        n = self.narrate(
            id="answers_05",
            text="Five: the milk is sixty-four times nine sixteenths, thirty-six litres, and the water twenty-eight: nine "
                 "to seven.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "milk")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "seven")
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_06",
            text="Six: the fraction left is twenty over forty-five, four ninths, so two thirds stays each time. One third "
                 "of forty-five is fifteen litres.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "fraction")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "fifteen")
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_07",
            text="Seven: the wine is twenty-five thirty-sixths, so five sixths stays each time. Six litres is one sixth of "
                 "the vessel: thirty-six litres.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "wine")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "thirty-six")
        self.play(FadeIn(rows[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_08",
            text="Eight: eighty times four fifths times three quarters: forty-eight litres.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "times")
        self.play(FadeIn(rows[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "forty-eight")
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
            text="Recognise and move. The recognition cue: the process is repeated, done twice, three times, or again "
                 "replaced with water.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "cue")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "repeated")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_lens_02",
            text="The target time: forty seconds, or sixty seconds when working backwards.",
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
            text="The sanity check: more is left than by plain subtraction, and the fraction left is below one.",
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
        main = pill("original liquid left  =  V × (1 − x/V)^n", GOOD, size=LABEL)
        row = VGroup(pill("the rounds multiply", WORD, size=SMALL), pill("the rest of the vessel is the other liquid", WORD, size=SMALL),
                     pill("backwards:  take the root", WORD, size=SMALL)).arrange(RIGHT, buff=0.3)
        fit_width(row, SAFE_W - 0.4)
        never = pill("never subtract x again and again", BAD, size=LABEL)
        car = text("the car:  a fifth of what is left, every year", LABEL, MUTED)
        nxt = self.breadcrumb("Next", "Video 6 · Price, Purity & Concentration")
        self.stack(head, [main, row, never, car, nxt], buff=0.6, top=0.7)
        self.no_overlap(*row)

        n = self.narrate(
            id="summary_01",
            text="The original liquid left is V times one minus x over V, to the power n.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "original")
        self.play(FadeIn(main, scale=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_02",
            text="The rounds multiply, the rest of the vessel is the other liquid, and backwards you take the root.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "multiply")
        self.play(FadeIn(row[0], shift=UP * 0.1))
        self.at_word(n, "rest")
        self.play(FadeIn(row[1], shift=UP * 0.1))
        self.at_word(n, "root")
        self.play(FadeIn(row[2], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_03",
            text="Never subtract x again and again.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Never")
        self.play(FadeIn(never, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_04",
            text="Remember the car: a fifth of what is left, every year.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "car")
        self.play(FadeIn(car, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_05",
            text="Next: price, purity and concentration.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Next")
        self.play(FadeIn(nxt, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S16_summary")

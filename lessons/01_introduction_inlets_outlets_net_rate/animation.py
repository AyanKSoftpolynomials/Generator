"""
animation.py for the LMS video generator.

Course : Pre-C-CAT - Section A - Quantitative Aptitude
Video  : Lesson 18 - Pipes & Cistern - 01 - Introduction - Inlets, Outlets & Net Rate

Source script:
  C:\\Scripts\\Section A\\Aptitude\\Sessions 13-18 - Pipes, Time Distance, Partnership\\Lesson 18 - Pipes & Cistern\\01 - Introduction - Inlets, Outlets & Net Rate.pdf

Built on the golden-reference pattern:
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``;
  * layouts stacked with next_to and guarded with ``no_overlap``; nothing is
    ever animated onto or into another box.

Lesson 18, Video 1 of 5. First video of the lesson: a silent breadcrumb, "Now we start lesson eighteen", a one-line recap of Lesson 17, then today's topic. No spoken course welcome.
The narration follows the script section by section. The seven concept steps are split over two screens. The six exam patterns are shown as two-line blocks (the answers are too long for a table column).
Text colours: white and grey, one blue accent, green and red only for right and wrong.
The script has eight practice questions (2 + 3 + 3): five on the first screen, three on the second.
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

from fractions import Fraction
from math import lcm


def units(*times):
    """LCM method.  times: full-tank times, negative for an outlet.  Returns (tank units, units per unit time for each pipe, net)."""
    tank = lcm(*[abs(t) for t in times])
    each = [tank // t for t in times]
    return tank, each, sum(each)


# ---- the hook: fill in 12 min, empty in 20 min ----
HOOK = units(12, -20)
assert HOOK == (60, [5, -3], 2) and Fraction(60, 2) == 30 and 30 - 12 == 18
assert Fraction(12 * 20, 12 + 20) == Fraction(15, 2) and 20 - 12 == 8                     # the two wrong instincts
assert Fraction(1, 12) - Fraction(1, 20) == Fraction(1, 30) and Fraction(12 * 20, 20 - 12) == 30

# ---- second worked example: half full, fill 10 h, empty 15 h ----
assert units(10, -15) == (30, [3, -2], 1) and Fraction(30, 2) / 1 == 15 and units(15, -10)[2] == -1

# ---- exam patterns, traps, checkpoint, practice (answers computed) ----
assert units(8, -12) == (24, [3, -2], 1) and units(10, 12, -15) == (60, [6, 5, -4], 7) and Fraction(60, 7) == 8 + Fraction(4, 7)
assert units(20, -30) == (60, [3, -2], 1) and Fraction(12, 60) == Fraction(1, 5) and units(20, -15) == (60, [3, -4], -1)
assert units(15, -15)[2] == 0 and units(6, -9) == (18, [3, -2], 1)
assert 6 * Fraction(1, 15) == Fraction(2, 5) and units(6, -10) == (30, [5, -3], 2) and units(12, 15, -20) == (60, [5, 4, -3], 6)
assert units(20, -12) == (60, [3, -5], -2) and units(8, -12) == (24, [3, -2], 1) and 24 - 24 // 3 == 16
assert Fraction(1, 9) - Fraction(1, 36) == Fraction(1, 12) and units(16, -8) == (16, [1, -2], -1) and 16 * 3 // 4 == 12

OBJECTIVES = [("Write every pipe as a signed rate", "plus for filling, minus for emptying"),
              ("Find the net rate and the time", "and decide whether the tank fills at all"),
              ("Find the part filled in t minutes", "and the time from a partly filled tank")]
FORMULAS = ["Inlet (fills in x):   rate +1/x              Outlet (empties in y):   rate −1/y",
            "Net rate   =   sum of inlet rates  −  sum of outlet rates",
            "Time   =   (amount to move) ÷ net rate",
            "Part filled in t   =   t × net rate",
            "Fill in x and empty in y together  (y > x):      T  =  xy/(y − x)"]
PATTERNS = [("Fill and empty together", "fill 8 h, empty 12 h", "24 units:   3 − 2 = 1", "24 h"),
            ("Two inlets, one outlet", "fill 10 and 12 min;  empty 15 min", "60 units:   6 + 5 − 4 = 7", "8 4/7 min"),
            ("Part filled in t", "fill 20 min, empty 30 min;  after 12 min", "60 units:   net 1;   12 units", "1/5 of the tank"),
            ("Partly full start", "half full;  fill 10 h, empty 15 h", "30 units:   15 to go at net 1", "15 h"),
            ("Net negative", "full tank;  fill 20 h, empty 15 h", "60 units:   3 − 4 = −1", "empties in 60 h"),
            ("Net zero", "fill 15 min, empty 15 min", "net rate 0", "never fills; the level stays")]
TRAPS = [("Trap 1  ·  the outlet treated as a helper", "Fill in 12 min, empty in 20 min, both open.  Time to fill?",
          "7.5 min  (or 20 − 12 = 8 min)", "30 minutes",
          "An outlet's rate is subtracted: the tank always takes longer than the inlet alone."),
         ("Trap 2  ·  the starting level ignored", "A tank is half full.  Fill in 10 h, empty in 15 h, both open.  Time to fill?",
          "30 hours  (the time from empty)", "15 hours",
          "Time = amount still to move ÷ net rate.  Read the starting level first."),
         ("Trap 3  ·  a negative net rate answered as a fill time",
          "Empty tank; inlet fills in 20 min, outlet empties in 15 min.  When is it full?",
          "20 × 15/(20 − 15)  =  60 min", "never:  the outlet is faster",
          "Check the sign of the net rate before dividing.")]
PRACTICE_A = [("L1", "A pipe fills a tank in 15 minutes.  What fraction of the tank does it fill in 6 minutes?"),
              ("L1", "One pipe fills a tank in 6 h, another empties the full tank in 10 h; both open, tank empty.  Time to fill?"),
              ("L2", "Pipes fill in 12 and 15 min; a third empties in 20 min.  All open on an empty tank.  Time to fill?"),
              ("L2", "A fills in 20 min, B empties in 30 min; both open, tank empty.  Fraction full after 12 min?"),
              ("L2", "Full tank; inlet fills in 20 h, outlet empties in 12 h, both open.  How long until it is empty?")]
PRACTICE_B = [("L3", "Tank one-third full; inlet fills in 8 h, outlet empties in 12 h, both open.  Time until full?"),
              ("L3", "A pipe fills in 9 min; with an outlet open it takes 36 min.  Outlet alone: time to empty?"),
              ("L3", "Tank three-quarters full; A fills in 16 min, B empties in 8 min, both open.  Time until empty?")]
ANSWERS_A = [("6 × 1/15", "2/5"),
             ("30 units:    +5 − 3 = +2 an hour", "15 hours"),
             ("60 units:    +5 + 4 − 3 = +6 a minute", "10 minutes"),
             ("60 units:    +3 − 2 = +1 a minute;    12 of 60", "1/5")]
ANSWERS_B = [("60 units:    +3 − 5 = −2 an hour", "30 hours"),
             ("24 units:    8 in, 16 to go;    net +3 − 2 = +1", "16 hours"),
             ("outlet rate  =  1/9 − 1/36  =  1/12", "12 minutes"),
             ("16 units:    12 in the tank;    net +1 − 2 = −1", "12 minutes")]
LENS = [("Recognition cue", "“fills”, “empties”, “outlet”, “waste pipe”, “drain”:  give every pipe a sign, then add"),
        ("Target time", "25 seconds"),
        ("Sanity check", "outlet open: longer than the inlet alone;  a faster outlet: the tank never fills")]


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


class IntroductionInletsOutletsAndNetRateVideo(LMSScene):
    lesson_title = "Introduction: Inlets, Outlets & Net Rate"

    def construct(self):
        self.camera.background_color = BG

        self.intro()
        self.hook()
        self.objectives()
        self.why_this_matters()
        self.signed_rates()
        self.time_and_part()
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

        crumb = self.breadcrumb("Quantitative Aptitude", "Lesson 18 · Pipes & Cistern", "Video 1 of 5")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        lesson = pill("Lesson 18  ·  Pipes & Cistern", RATIO, size=LABEL)
        recap = VGroup(text("from Lesson 17  ·  Average", SMALL, MUTED),
                       fit_width(VGroup(pill("average = total ÷ count", WORD, size=LABEL), pill("total = average × count", GOOD, size=LABEL)).arrange(RIGHT, buff=0.4), SAFE_W - 0.6)).arrange(DOWN, buff=0.25)
        title = fit_width(text("Introduction: Inlets, Outlets & Net Rate", TITLE, INK, BOLD), SAFE_W - 0.4)
        today = text("today: inlets, outlets and one minus sign", LABEL, FOCUS)
        block = VGroup(lesson, recap, title, today).arrange(DOWN, buff=0.55)
        fit_within(block, SAFE_W, SAFE_H - crumb.height - 0.9)
        block.next_to(crumb, DOWN, buff=0.6)
        self.no_overlap(crumb, lesson, recap, title, today)
        self.no_overlap(*recap[1])
        self.validator.check_in_frame(VGroup(crumb, block))

        n = self.narrate(
            id="intro_01",
            text="Now we start lesson eighteen: pipes and cistern.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.at_word(n, "eighteen")
        self.play(FadeIn(lesson, scale=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="intro_02",
            text="In lesson seventeen, the average was the total divided by the count, and the total was the average times "
                 "the count.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "divided")
        self.play(FadeIn(recap[0]), FadeIn(recap[1][0], shift=UP * 0.1))
        self.at_word(n, "times")
        self.play(FadeIn(recap[1][1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="intro_03",
            text="This first video is the introduction: inlets, outlets and the net rate.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "introduction")
        self.play(FadeIn(title, shift=UP * 0.1))
        self.at_word(n, "net")
        self.play(FadeIn(today, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_intro")

    # ============================================== 1. HOOK ==========

    def hook(self):
        self.scene_start("S01_hook", title="Hook")

        head = self.heading("A rooftop water tank")
        motor = pill("motor pipe:  fills the empty tank alone in 12 min", GOOD, size=LABEL)
        tap = pill("outlet tap, left open:  drains a full tank alone in 20 min", BAD, size=LABEL)
        ask = pill("motor on, tap open:   when does the tank overflow?", FOCUS, size=LABEL)
        wrongs = VGroup(text("Lesson 13 reflex:  12 × 20/32 = 7.5 min", LABEL, BAD), text("subtract the times:  8 min", LABEL, BAD))\
            .arrange(RIGHT, buff=0.8)
        far = text("both are wrong: the correct answer is far longer than either", LABEL, INK, BOLD)
        self.stack(head, [motor, tap, ask, wrongs, far], buff=0.55, top=0.7)
        self.no_overlap(*wrongs)

        n = self.narrate(
            id="hook_01",
            text="The motor fills an empty rooftop tank in twelve minutes.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "motor")
        self.play(FadeIn(motor, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_02",
            text="Someone has left the outlet tap at the bottom open; on its own it would drain a full tank in twenty "
                 "minutes.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "outlet")
        self.play(FadeIn(tap, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_03",
            text="You switch the motor on and walk away. When does the tank overflow?",
            voice="default",
            subtitle=True,
            pause_after=3.0,
        )
        self.at_word(n, "switch")
        self.play(Indicate(motor, color=FOCUS, scale_factor=1.03))
        self.at_word(n, "overflow")
        self.play(FadeIn(ask, scale=1.03))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="hook_04",
            text="The lesson thirteen reflex gives twelve times twenty over thirty-two: seven and a half minutes; and "
                 "subtracting the times gives eight.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "reflex")
        self.play(FadeIn(wrongs[0], shift=UP * 0.1))
        self.at_word(n, "subtracting")
        self.play(FadeIn(wrongs[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_05",
            text="Both are wrong, and the correct answer is far longer than either.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "wrong")
        self.play(FadeIn(far, shift=UP * 0.1))
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
            text="First, write every pipe as a signed rate: plus for filling, minus for emptying.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "signed")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "plus")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="objectives_03",
            text="Second, find the net rate, decide whether the tank fills at all, and find the time.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "net")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "decide")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="objectives_04",
            text="Third, find the part filled in t minutes, and the time from a partly filled tank.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "part")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "partly")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_objectives")

    # ============================================== 3. WHY THIS MATTERS ==========

    def why_this_matters(self):
        self.scene_start("S03_why_this_matters", title="Why This Matters")

        head = self.heading("Why this matters")
        same = pill("Pipes & Cistern  =  Lesson 13 (Time & Work), with one new idea", WORD, size=LABEL)
        undo = text("some “workers” undo the work", BODY, BAD, BOLD)
        carry = text("every rate, LCM and stage method carries over unchanged", LABEL, INK)
        minus = pill("only the minus sign is new: it is where most marks are lost", FOCUS, size=LABEL)
        self.stack(head, [same, undo, carry, minus], buff=0.7, top=0.9)

        n = self.narrate(
            id="why_this_matters_01",
            text="Pipes and cistern is lesson thirteen, time and work, with one new idea: some workers undo the work.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "thirteen")
        self.play(FadeIn(same, shift=UP * 0.1))
        self.at_word(n, "undo")
        self.play(FadeIn(undo, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="why_this_matters_02",
            text="Every rate, L C M and stage method from lesson thirteen carries over unchanged; only the minus sign is "
                 "new, and it is where most marks are lost.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "carries")
        self.play(FadeIn(carry, shift=UP * 0.1))
        self.at_word(n, "minus")
        self.play(FadeIn(minus, scale=1.03))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_why_this_matters")

    # ============================================== 4. CONCEPT - EVERY PIPE IS A SIGNED RATE ==========

    def signed_rates(self):
        self.scene_start("S04_signed_rates", title="Concept - Every Pipe Is a Signed Rate")

        head = self.heading("Every pipe is a signed rate")
        inlet = VGroup(text("fills in x minutes", LABEL, INK, BOLD), pill("rate  +1/x  of the tank per minute", GOOD, size=LABEL)).arrange(RIGHT, buff=0.5)
        outlet = VGroup(text("empties in y minutes", LABEL, INK, BOLD), pill("rate  −1/y:   “negative work”", BAD, size=LABEL)).arrange(RIGHT, buff=0.5)
        netr = pill("net rate  =  sum of inlet rates − sum of outlet rates", FOCUS, size=LABEL)
        eg = text("motor +1/12,   tap −1/20:    net +1/30", LABEL, INK, BOLD)
        signs = VGroup(text("net > 0:  fills", LABEL, GOOD, BOLD), text("net < 0:  empties", LABEL, BAD, BOLD),
                       text("net = 0:  the level never changes", LABEL, MUTED, BOLD)).arrange(RIGHT, buff=0.7)
        self.stack(head, [inlet, outlet, netr, eg, signs], buff=0.55, top=0.7)
        self.no_overlap(*inlet)
        self.no_overlap(*outlet)
        self.no_overlap(*signs)

        n = self.narrate(
            id="signed_rates_01",
            text="The rate logic is lesson thirteen's: a pipe that fills a tank in x minutes fills one over x of it per "
                 "minute. The tank is the job; the pipe is the worker.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "fills")
        self.play(FadeIn(inlet[0], shift=RIGHT * 0.2))
        self.at_word(n, "over")
        self.play(FadeIn(inlet[1], shift=LEFT * 0.1))
        self.at_word(n, "worker")
        self.play(Indicate(inlet, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="signed_rates_02",
            text="The new idea: an emptying pipe has a negative rate. An outlet that empties a full tank in y minutes has "
                 "rate minus one over y; it does negative work.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "emptying")
        self.play(FadeIn(outlet[0], shift=RIGHT * 0.2))
        self.at_word(n, "minus")
        self.play(FadeIn(outlet[1], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="signed_rates_03",
            text="The net rate is the sum of the inlet rates minus the sum of the outlet rates. All open pipes act at the "
                 "same time, so their signed rates add.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "net")
        self.play(FadeIn(netr, scale=1.03))
        self.at_word(n, "add")
        self.play(FadeIn(eg, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="signed_rates_04",
            text="The sign decides what happens. Net rate positive: the tank fills. Net rate negative: the tank empties, "
                 "and an empty tank simply stays empty. Net rate zero: the level never changes.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "sign")
        self.play(Indicate(netr, color=FOCUS, scale_factor=1.03))
        self.at_word(n, "positive")
        self.play(FadeIn(signs[0], shift=UP * 0.1))
        self.at_word(n, "negative")
        self.play(FadeIn(signs[1], shift=UP * 0.1))
        self.at_word(n, "zero")
        self.play(FadeIn(signs[2], shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_signed_rates")

    # ============================================== 5. CONCEPT - TIME, PART FILLED AND THE LCM METHOD ==========

    def time_and_part(self):
        self.scene_start("S05_time_and_part", title="Concept - Time, Part Filled and the LCM Method")

        head = self.heading("Time, part filled, and the LCM method")
        time = VGroup(pill("time  =  amount to move ÷ net rate", FOCUS, size=LABEL),
                      text("empty to full: 1 tank;    half full to full: 1/2", LABEL, MUTED)).arrange(RIGHT, buff=0.5)
        part = pill("part filled in t minutes  =  t × net rate", WORD, size=LABEL)
        method = VGroup(text("LCM method, unchanged:    12 and 20 min  →  60 units", LABEL, INK, BOLD),
                        text("motor +5 a minute,  tap −3", LABEL, GOOD, BOLD)).arrange(RIGHT, buff=0.5)
        fit_width(method, SAFE_W - 0.4)
        conv = text("conventions:  the tank starts empty unless stated;  constant rates;  never below empty", SMALL, MUTED)
        self.stack(head, [time, part, method, conv], buff=0.75, top=0.9)
        self.no_overlap(*time)
        self.no_overlap(*method)

        n = self.narrate(
            id="time_and_part_01",
            text="Time is the amount to be moved, divided by the net rate. From empty to full, the amount is one tank; "
                 "from half full to full, it is one half.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "divided")
        self.play(FadeIn(time[0], shift=UP * 0.1))
        self.at_word(n, "half")
        self.play(FadeIn(time[1], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="time_and_part_02",
            text="The part filled in t minutes is t times the net rate: the level changes by the net rate every minute.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "times")
        self.play(FadeIn(part, scale=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="time_and_part_03",
            text="The L C M method works unchanged. Take the tank as the L C M of all the times, in units: for twelve and "
                 "twenty minutes, sixty units; the motor adds five a minute and the tap removes three.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "unchanged")
        self.play(FadeIn(method[0], shift=UP * 0.1))
        self.at_word(n, "adds")
        self.play(FadeIn(method[1], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="time_and_part_04",
            text="Conventions for this lesson: the tank starts empty unless stated, every pipe flows at a constant rate, "
                 "and an outlet cannot take a tank below empty.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Conventions")
        self.play(FadeIn(conv, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_time_and_part")

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
            text="Here is the formula box. An inlet that fills in x has rate plus one over x; an outlet that empties in y "
                 "has rate minus one over y.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "box")
        self.play(FadeIn(box[0]))
        self.at_word(n, "inlet")
        self.play(FadeIn(lines[0], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_box_02",
            text="The net rate is the sum of the inlet rates minus the sum of the outlet rates.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "net")
        self.play(FadeIn(lines[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_box_03",
            text="Time is the amount to move, divided by the net rate.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "divided")
        self.play(FadeIn(lines[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_box_04",
            text="The part filled in t is t times the net rate.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "part")
        self.play(FadeIn(lines[3], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_box_05",
            text="And for fill in x with empty in y together, where y is bigger than x, the time is x y over y minus x.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "together")
        self.play(FadeIn(lines[4], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_formula_box")

    # ============================================== 7. THE ANALOGY - A BANK ACCOUNT ==========

    def analogy(self):
        self.scene_start("S07_analogy", title="The Analogy - A Bank Account")

        head = self.heading("A bank account")
        flows = VGroup(pill("salary credit:  +5 a minute", GOOD, size=LABEL), pill("auto-debit:  −3 a minute", BAD, size=LABEL),
                       pill("balance climbs at +2", FOCUS, size=LABEL)).arrange(RIGHT, buff=0.4)
        moves = text("the balance moves by credit minus debit, however large each one is", LABEL, INK, BOLD)
        falls = text("if the debit is larger, the balance falls", LABEL, MUTED)
        stops = VGroup(text("Where the analogy stops", LABEL, BAD, BOLD),
                       text("a balance can go negative; a tank cannot", LABEL, INK),
                       text("it has a floor (empty) and a ceiling (full): a question ends at one of them", LABEL, MUTED)).arrange(DOWN, buff=0.2)
        self.stack(head, [flows, moves, falls, stops], buff=0.6, top=0.7)
        self.no_overlap(*flows)

        n = self.narrate(
            id="analogy_01",
            text="Think of an account with a credit and a debit running at the same time.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "credit")
        self.play(FadeIn(flows[0], shift=UP * 0.1))
        self.at_word(n, "debit")
        self.play(FadeIn(flows[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_02",
            text="The balance does not care how large each one is; it moves by credit minus debit.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "moves")
        self.play(FadeIn(flows[2], shift=UP * 0.1), FadeIn(moves, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_03",
            text="If the debit is larger, the balance falls, however generous the credit looks.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "falls")
        self.play(FadeIn(falls, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_04",
            text="Where the analogy stops: a balance can go negative; a tank cannot.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "stops")
        self.play(FadeIn(stops[0], shift=UP * 0.1))
        self.at_word(n, "cannot")
        self.play(FadeIn(stops[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_05",
            text="It has a floor, empty, and a ceiling, full, and a question ends when the tank reaches one of them.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "floor")
        self.play(FadeIn(stops[2], shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S07_analogy")

    # ============================================== 8. WORKED EXAMPLE - CLOSING THE HOOK ==========

    def hook_solved(self):
        self.scene_start("S08_hook_solved", title="Worked Example - Closing the Hook")

        head = self.heading("Fill in 12 min, empty in 20 min")
        steps = self.solve_steps([("Tank = 60 units:    motor +5 a minute,  tap −3 a minute", "net +2 a minute"),
                                  ("Time:    60 ÷ 2", "=  30 minutes"),
                                  ("Motor alone 12 min:    the open tap costs", "18 extra minutes"),
                                  ("Check:    1/12 − 1/20  =  5/60 − 3/60", "=  1/30 per minute")])
        self.stack(head, [steps], top=1.0)
        self.no_overlap(*steps)

        n = self.narrate(
            id="hook_solved_01",
            text="Take the tank as sixty units. The motor adds five units a minute, the tap removes three, so the net is "
                 "plus two units a minute.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "sixty")
        self.play(FadeIn(steps[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "net")
        self.play(FadeIn(steps[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_solved_02",
            text="The time is sixty divided by two: thirty minutes.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "divided")
        self.play(FadeIn(steps[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "thirty")
        self.play(FadeIn(steps[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_solved_03",
            text="The motor alone would take twelve; the open tap costs eighteen extra minutes.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "alone")
        self.play(FadeIn(steps[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "eighteen")
        self.play(FadeIn(steps[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_solved_04",
            text="Check with fractions: one twelfth minus one twentieth is five sixtieths minus three sixtieths, one "
                 "thirtieth per minute.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Check")
        self.play(FadeIn(steps[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "thirtieth")
        self.play(FadeIn(steps[3][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S08_hook_solved")

    # ============================================== 9. A SECOND WORKED EXAMPLE - STARTING HALF FULL ==========

    def second_example(self):
        self.scene_start("S09_second_example", title="A Second Worked Example - Starting Half Full")

        head = self.heading("Starting half full")
        ask = text("inlet A fills in 10 h, outlet B empties in 15 h, both open:   how long until full?", LABEL, MUTED)
        steps = self.solve_steps([("Tank = 30 units:    A +3 an hour,  B −2 an hour", "net +1 an hour"),
                                  ("Half full:    15 units already in", "15 units to fill"),
                                  ("Time:    15 ÷ 1", "=  15 hours"),
                                  ("Swapped (fill in 15, empty in 10):    net −1", "empties in 15 hours")])
        self.stack(head, [ask, steps], buff=0.7, top=0.7)
        self.no_overlap(*steps)

        n = self.narrate(
            id="second_example_01",
            text="A tank is half full. Inlet A fills a tank in ten hours and outlet B empties a full tank in fifteen "
                 "hours. Both are opened: how long until the tank is full?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "half")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "Inlet")
        self.play(FadeIn(ask, shift=UP * 0.1))
        self.at_word(n, "long")
        self.play(Indicate(ask, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_02",
            text="Take the tank as thirty units: A adds three an hour, B removes two, so the net is plus one an hour.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "thirty")
        self.play(FadeIn(steps[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "net")
        self.play(FadeIn(steps[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_03",
            text="Half full means fifteen units are already in, and fifteen units are still to fill.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "already")
        self.play(FadeIn(steps[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "still")
        self.play(FadeIn(steps[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_04",
            text="The time is fifteen divided by one: fifteen hours.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "divided")
        self.play(FadeIn(steps[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "hours")
        self.play(FadeIn(steps[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_05",
            text="Had A and B been swapped, filling in fifteen and emptying in ten, the net would be minus one an hour, "
                 "and the half-full tank would empty in fifteen hours instead.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "swapped")
        self.play(FadeIn(steps[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "instead")
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
            text="Fill and empty together: fill in eight hours, empty in twelve. Twenty-four units, three minus two is "
                 "one: twenty-four hours.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "together")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "minus")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_03",
            text="Two inlets and one outlet: fill in ten and twelve minutes, empty in fifteen. Sixty units, six plus five "
                 "minus four is seven: eight and four sevenths minutes.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "outlet")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "plus")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_04",
            text="Part filled in a given time: fill in twenty minutes, empty in thirty, after twelve minutes. Sixty units "
                 "at net one gives twelve units: one fifth of the tank.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Part")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "gives")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Exam patterns  ·  4 to 6 of 6")
        blocks = self.pattern_blocks(PATTERNS[3:6])
        self.stack(head, list(blocks), buff=0.6, top=0.8, align=LEFT)

        n = self.narrate(
            id="exam_patterns_05",
            text="A partly full start: half full, fill in ten hours, empty in fifteen. Thirty units, fifteen to go at net "
                 "one: fifteen hours.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "start")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "go")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_06",
            text="Net negative: a full tank, fill in twenty hours, empty in fifteen. Sixty units, three minus four is "
                 "minus one: it empties in sixty hours.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "negative")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "minus")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_07",
            text="Net zero: fill in fifteen minutes, empty in fifteen minutes. The net rate is zero: it never fills, and "
                 "the level stays.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "zero")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "never")
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
            text="Trap one: the outlet treated as a helper. Fill in twelve minutes, empty in twenty minutes, both open: "
                 "what is the time to fill?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "helper")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "Fill")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_02",
            text="The wrong instinct gives seven and a half minutes, or eight minutes by subtracting. The correct answer "
                 "is thirty minutes.",
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
            text="The rule: an outlet's rate is subtracted. With an outlet open, the tank always takes longer than the "
                 "inlet alone.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "rule")
        self.play(FadeIn(rule, shift=UP * 0.1))
        self.at_word(n, "longer")
        self.play(Indicate(rule, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)
        self.clear_stage()

        head, q, wrong, right, rule = self.show_trap(TRAPS[1])

        n = self.narrate(
            id="traps_04",
            text="Trap two: the starting level ignored. A tank is half full; fill in ten hours, empty in fifteen hours, "
                 "both open: what is the time to fill?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "ignored")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "half")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_05",
            text="The wrong instinct says thirty hours, the time from empty. The correct answer is fifteen hours.",
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
            text="The rule: time is the amount still to move, divided by the net rate. Read the starting level first.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "rule")
        self.play(FadeIn(rule, shift=UP * 0.1))
        self.at_word(n, "Read")
        self.play(Indicate(rule, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)
        self.clear_stage()

        head, q, wrong, right, rule = self.show_trap(TRAPS[2])

        n = self.narrate(
            id="traps_07",
            text="Trap three: a negative net rate answered as a fill time. An empty tank; the inlet fills in twenty "
                 "minutes and the outlet empties in fifteen minutes, both open: when is it full?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "negative")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "inlet")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_08",
            text="The wrong instinct computes twenty times fifteen over five: sixty minutes. The correct answer is never: "
                 "the outlet is faster, so the tank stays empty.",
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
            text="The rule: check the sign of the net rate before dividing.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "rule")
        self.play(FadeIn(rule, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S11_traps")

    # ============================================== 12. CHECKPOINT ==========

    def checkpoint(self):
        self.scene_start("S12_checkpoint", title="Checkpoint")

        head = self.heading("Checkpoint  ·  your turn")
        given = fit_width(pill("fills in 6 h, empties in 9 h, both open on an empty tank:   time to fill?", FOCUS, size=LABEL),
                          SAFE_W - 0.4)
        work = VGroup(text("18 units:    +3 − 2  =  +1 an hour", BODY, INK, BOLD), text("18 ÷ 1  =  18 hours", BODY, GOOD, BOLD)).arrange(RIGHT, buff=0.7)
        self.stack(head, [given, work], buff=1.0, top=1.0)
        self.no_overlap(*work)

        n = self.narrate(
            id="checkpoint_01",
            text="Your turn. One pipe fills a tank in six hours; another empties it in nine hours. Both are opened on an "
                 "empty tank: how long to fill it?",
            voice="default",
            subtitle=True,
            pause_after=10.0,
        )
        self.at_word(n, "turn")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "fills")
        self.play(FadeIn(given, scale=1.03))
        self.at_word(n, "long")
        self.play(Indicate(given, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="checkpoint_02",
            text="Eighteen units: plus three minus two is plus one an hour, so eighteen divided by one is eighteen hours.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "minus")
        self.play(FadeIn(work[0], shift=UP * 0.1))
        self.at_word(n, "divided")
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
            text="Level one, question one: a pipe fills a tank in fifteen minutes; what fraction of the tank does it fill "
                 "in six minutes? Question two: one pipe fills a tank in six hours and another empties the full tank in "
                 "ten hours; both are opened on an empty tank; how long does it take to fill?",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "fraction")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "another")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="practice_02",
            text="Level two, question three: two pipes fill a tank in twelve and fifteen minutes, and a third empties the "
                 "full tank in twenty minutes; all three are opened on an empty tank; how long does it take to fill? "
                 "Question four: pipe A fills a tank in twenty minutes and pipe B empties it in thirty minutes; both are "
                 "opened on an empty tank; what fraction is full after twelve minutes? Question five: a full tank has an "
                 "inlet that fills it in twenty hours and an outlet that empties it in twelve hours; both are opened; how "
                 "long until the tank is empty?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "third")
        self.play(FadeIn(rows[2], shift=RIGHT * 0.2))
        self.at_word(n, "after")
        self.play(FadeIn(rows[3], shift=RIGHT * 0.2))
        self.at_word(n, "until")
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
            text="Level three, question six: a tank is one-third full; an inlet fills a tank in eight hours and an outlet "
                 "empties a full tank in twelve hours; both are opened; how long until the tank is full? Question seven: a "
                 "pipe fills a tank in nine minutes; with an outlet also open, the empty tank fills in thirty-six minutes; "
                 "how long would the outlet alone take to empty the full tank? Question eight: a tank is three-quarters "
                 "full; pipe A fills a tank in sixteen minutes and pipe B empties a full tank in eight minutes; both are "
                 "opened; how long until the tank is empty?",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "one-third")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "alone")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.at_word(n, "three-quarters")
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
            text="One: six minutes at one fifteenth a minute is two fifths.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "at")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "fifths")
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_02",
            text="Two: thirty units, plus five minus three is plus two an hour, so thirty divided by two is fifteen hours.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "minus")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "divided")
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_03",
            text="Three: sixty units, plus five plus four minus three is plus six a minute, so sixty divided by six is ten "
                 "minutes.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "minus")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "divided")
        self.play(FadeIn(rows[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_04",
            text="Four: sixty units, plus three minus two is plus one a minute, so twelve minutes is twelve units of "
                 "sixty: one fifth.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "minus")
        self.play(FadeIn(rows[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "fifth")
        self.play(FadeIn(rows[3][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Answer key  ·  5 to 8", GOOD)
        table, rows = self.answer_table(head, ANSWERS_B, 5)

        n = self.narrate(
            id="answers_05",
            text="Five: sixty units, plus three minus five is minus two an hour, so sixty divided by two is thirty hours.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "minus")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "divided")
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_06",
            text="Six: twenty-four units, eight already in and sixteen to go; the net is plus three minus two, plus one an "
                 "hour: sixteen hours.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "already")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "hours")
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_07",
            text="Seven: the outlet's rate is one ninth minus one thirty-sixth, which is one twelfth, so the outlet alone "
                 "takes twelve minutes.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "minus")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "alone")
        self.play(FadeIn(rows[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_08",
            text="Eight: sixteen units with twelve in the tank; the net is plus one minus two, minus one a minute: twelve "
                 "minutes.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "tank")
        self.play(FadeIn(rows[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "minutes")
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
            text="Recognise and move. The recognition cue: fills, empties, outlet, waste pipe or drain; give every pipe a "
                 "sign, then add.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "cue")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "sign")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_lens_02",
            text="The target time: twenty-five seconds.",
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
            text="The sanity check: with an outlet open, the fill time must be longer than the inlet's time alone; if the "
                 "outlet is faster, the tank never fills.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "sanity")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "longer")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S15_exam_lens")

    # ============================================== 16. QUICK REVISION AND SUMMARY ==========

    def summary(self):
        self.scene_start("S16_summary", title="Quick Revision and Summary")

        head = self.heading("Quick revision")
        rate = pill("every pipe is a rate:   plus if it fills, minus if it empties", GOOD, size=LABEL)
        method = VGroup(pill("add the signed rates", WORD, size=SMALL), pill("check the sign", FOCUS, size=SMALL),
                        pill("amount still to move ÷ net rate", RATIO, size=SMALL)).arrange(RIGHT, buff=0.35)
        same = text("the LCM method from Lesson 13 works unchanged", LABEL, INK, BOLD)
        bank = text("the bank account: the balance moves by credit minus debit", LABEL, MUTED)
        box = fit_width(pill("net = inlets − outlets          time = amount ÷ net          T = xy/(y − x),  y > x", GOOD, size=SMALL), SAFE_W - 0.4)
        nxt = self.breadcrumb("Next", "Video 2 · Multiple Pipes & the LCM Method")
        self.stack(head, [rate, method, same, bank, box, nxt], buff=0.45, top=0.6)
        self.no_overlap(*method)

        n = self.narrate(
            id="summary_01",
            text="Every pipe is a rate: plus if it fills, minus if it empties.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "rate")
        self.play(FadeIn(rate, scale=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_02",
            text="Add the signed rates to get the net rate, check its sign, and divide the amount still to move by it.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Add")
        self.play(FadeIn(method[0], shift=UP * 0.1))
        self.at_word(n, "check")
        self.play(FadeIn(method[1], shift=UP * 0.1))
        self.at_word(n, "divide")
        self.play(FadeIn(method[2], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_03",
            text="The L C M method from lesson thirteen works unchanged.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "unchanged")
        self.play(FadeIn(same, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_04",
            text="Remember the bank account, and the formula box.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "bank")
        self.play(FadeIn(bank, shift=UP * 0.1))
        self.at_word(n, "box")
        self.play(FadeIn(box, scale=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_05",
            text="Next: multiple pipes and the L C M method.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Next")
        self.play(FadeIn(nxt, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S16_summary")

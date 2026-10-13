"""
animation.py for the LMS video generator.

Course : Pre-C-CAT - Section A - Quantitative Aptitude
Video  : Lesson 18 - Pipes & Cistern - 02 - Multiple Pipes & the LCM Method

Source script:
  C:\\Scripts\\Section A\\Aptitude\\Sessions 13-18 - Pipes, Time Distance, Partnership\\Lesson 18 - Pipes & Cistern\\02 - Multiple Pipes & the LCM Method.pdf

Built on the golden-reference pattern:
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``;
  * layouts stacked with next_to and guarded with ``no_overlap``; nothing is
    ever animated onto or into another box.

Lesson 18, Video 2 of 5. Not the first video of the lesson: a silent breadcrumb, a one-line recap of Video 1, then today's topic. No spoken course welcome.
The narration follows the script section by section. The seven concept steps are split over two screens. The six exam patterns are shown as two-line blocks.
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
    """LCM method.  times: full-tank times, negative for an outlet.  Returns (tank units, units per unit time for each, net)."""
    tank = lcm(*[abs(t) for t in times])
    each = [tank // t for t in times]
    return tank, each, sum(each)


# ---- the hook: A 12 h, B 15 h, all three 20 h ----
SUMP = lcm(12, 15, 20)
C_RATE = SUMP // 20 - SUMP // 12 - SUMP // 15
assert (SUMP, SUMP // 12, SUMP // 15, SUMP // 20, C_RATE) == (60, 5, 4, 3, -6) and SUMP // abs(C_RATE) == 10

# ---- second worked example: pairs 10, 18, 15 h ----
PAIRS = lcm(10, 18, 15)
AB, BC, CA = PAIRS // 10, PAIRS // 18, PAIRS // 15
ALL = (AB + BC + CA) // 2
assert (PAIRS, AB, BC, CA, ALL) == (90, 9, 5, 6, 10) and PAIRS // ALL == 9 and ALL - AB == 1
assert [Fraction(PAIRS, ALL - pair) for pair in (BC, CA, AB)] == [18, Fraction(45, 2), 90]        # A, B, C alone

# ---- exam patterns, traps, checkpoint, practice (answers computed) ----
assert units(12, 18, 36) == (36, [3, 2, 1], 6) and 60 // 5 - 5 - 4 == 3 and 60 // 3 == 20
assert 3 * 20 == 60 and (60 // 2, 60 // 1) == (30, 60) and Fraction(900, 12 + 18 - 10) == 45
assert 60 // 12 - (60 // 10 + 60 // 15) == -5 and 60 // 5 == 12 and 30 // 2 == 15           # traps 1 and 2
assert 600 // 60 == 10 and Fraction(1200, 30 - 10) == 60                                    # trap 3
assert units(20, 30, 60) == (60, [3, 2, 1], 6) and units(10, 15, -30) == (30, [3, 2, -1], 4) and Fraction(30, 4) == Fraction(15, 2)
assert 24 // 6 - (24 // 8 + 24 // 12) == -1 and units(6, 9)[:2] == (18, [3, 2]) and 50 * 60 == 3000 and 3000 // 5 * 18 == 10800

OBJECTIVES = [("Solve three-or-more-pipe problems", "with LCM units and signed rates"),
              ("Find a missing pipe's time", "and tell from the sign whether it fills or empties"),
              ("Handle pairs and “n times as fast”", "and capacities given in litres per minute")]
STEPS_A = [("Total = LCM of every time in the question, fill and empty alike", "for 12, 15 and 20 hours:  60 units"),
           ("Sign each pipe's units:  inlets add, outlets subtract", "A = +5,   B = +4 units an hour"),
           ("The missing pipe = all together − the known pipes", "all three:  60 ÷ 20 = +3;     C = 3 − 5 − 4 = −6"),
           ("Read the sign:  positive is an inlet, negative is an outlet", "C = −6 empties 60 units in 10 hours")]
STEPS_B = [("Pairs given:  add and halve", "(A + B) + (B + C) + (C + A)  =  2 × (A + B + C),  exactly as in Lesson 13"),
           ("“n times as fast” gives units directly", "A twice as fast as B:  A = 2 units, B = 1;    total = combined units × combined time"),
           ("Litres per minute:  the capacity is the total", "capacity = flow × time;    time = capacity ÷ net flow;    one time unit for every flow")]
FORMULAS = ["Total   =   LCM of all fill and empty times    (or the capacity in litres)",
            "Units per hour:     inlet  =  +total ÷ time;       outlet  =  −total ÷ time",
            "Missing pipe   =   (all-together units) − (known pipes' units);      its sign shows inlet or outlet",
            "Pairs:     A + B + C   =   (sum of pair units) ÷ 2",
            "Capacity   =   flow × time;         time   =   capacity ÷ net flow"]
PATTERNS = [("Three inlets", "12, 18, 36 min", "36 units:   3 + 2 + 1 = 6", "6 min"),
            ("Missing inlet", "all three 5 h;   A 12 h, B 15 h", "60 units:   12 − 5 − 4 = 3", "C fills in 20 h"),
            ("Missing outlet", "all three 20 h;   A 12 h, B 15 h", "60 units:   3 − 5 − 4 = −6", "C empties in 10 h"),
            ("Pairs given", "A + B 10 h,   B + C 18 h,   C + A 15 h", "90 units:   (9 + 5 + 6) ÷ 2 = 10", "9 h"),
            ("n times as fast", "A twice as fast as B;   together 20 min", "A 2, B 1;   total 3 × 20 = 60", "A 30 min,  B 60 min"),
            ("Flows in litres", "inlets 12 and 18 L/min, outlet 10 L/min;   900 L", "900 ÷ (12 + 18 − 10)", "45 min")]
TRAPS = [("Trap 1  ·  a negative result misread",
          "A fills in 10 min, B in 15.  With C also open the tank fills in 12 min.  What does C do?",
          "“C fills the tank in 12 min”", "C = −5:  empties it in 12 min",
          "The sign of the missing pipe's units says inlet or outlet.  Report it that way."),
         ("Trap 2  ·  faster read as more time", "A fills twice as fast as B.  B alone takes 30 minutes.  How long does A take?",
          "60 minutes", "15 minutes",
          "Twice the rate means half the time: the time ratio is the inverse of the rate ratio."),
         ("Trap 3  ·  flows in different time units", "A 1,200-litre tank: inlet 30 L/min, outlet 600 L/h.  Time to fill?",
          "30 − 600 < 0:  never fills", "600 L/h = 10 L/min:  60 min",
          "Convert every flow to the same unit before adding.")]
PRACTICE_A = [("L1", "Three pipes fill a tank in 12, 18 and 36 minutes.  How long do they take together?"),
              ("L1", "Two pipes fill in 10 and 15 h; a third empties the full tank in 30 h.  All open, tank empty.  Time to fill?"),
              ("L2", "A fills in 12 h, B in 15 h; with C also open the tank fills in 5 h.  C alone: how long, and fill or empty?"),
              ("L2", "A fills twice as fast as B.  Together they fill the tank in 20 minutes.  How long would each take alone?"),
              ("L2", "Inlets deliver 12 and 18 L/min; an outlet removes 10 L/min.  Time to fill an empty 900-litre tank?")]
PRACTICE_B = [("L3", "A + B fill a tank in 10 h, B + C in 18 h, C + A in 15 h.  How long would each pipe take alone?"),
              ("L3", "A fills in 8 min, B in 12 min; with C also open the tank fills in 6 min.  Describe pipe C."),
              ("L3", "A fills a tank in 6 h and B in 9 h.  Together they deliver 50 litres a minute.  Find the capacity.")]
ANSWERS_A = [("36 units:    3 + 2 + 1 = 6 a minute", "6 minutes"),
             ("30 units:    +3 + 2 − 1 = +4 an hour;    30 ÷ 4", "7.5 hours"),
             ("60 units:    all three 12,  A + B = 9,  so C = +3", "inlet:  20 hours"),
             ("A = 2, B = 1 unit a minute;    total 3 × 20 = 60", "A 30 min,  B 60 min")]
ANSWERS_B = [("net flow 12 + 18 − 10 = 20 L/min;    900 ÷ 20", "45 minutes"),
             ("90 units:    A + B + C = 10;    A = 5,  B = 4,  C = 1", "18 h,  22.5 h,  90 h"),
             ("24 units:    A + B = 5,  all three 4,  so C = −1", "outlet:  24 minutes"),
             ("18 units:  5 an hour = 3,000 L;    1 unit = 600 L", "10,800 litres")]
LENS = [("Recognition cue", "three or more pipes, a missing pipe, pairs, or flows in litres:  LCM units with signs"),
        ("Target time", "35 seconds;  45 seconds for pairs or litres"),
        ("Sanity check", "whole-number units;  the missing pipe's sign must agree with the story")]


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


class MultiplePipesAndTheLCMMethodVideo(LMSScene):
    lesson_title = "Multiple Pipes & the LCM Method"

    def construct(self):
        self.camera.background_color = BG

        self.intro()
        self.hook()
        self.objectives()
        self.why_this_matters()
        self.units_with_signs()
        self.pairs_speed_litres()
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
    # Not the first video: silent breadcrumb, a one-line recap of the previous video, then today's topic.

    def intro(self):
        self.scene_start("S00_intro", title="Intro")

        crumb = self.breadcrumb("Quantitative Aptitude", "Lesson 18 · Pipes & Cistern", "Video 2 of 5")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        recap = VGroup(text("last video", SMALL, MUTED), pill("every pipe is a signed rate:  + fills,  − empties", WORD, size=LABEL)).arrange(DOWN, buff=0.25)
        title = fit_width(text("Multiple Pipes & the LCM Method", TITLE, INK, BOLD), SAFE_W - 0.4)
        today = text("today: three or more pipes, and not one fraction", LABEL, FOCUS)
        block = VGroup(recap, title, today).arrange(DOWN, buff=0.7)
        fit_within(block, SAFE_W, SAFE_H - crumb.height - 0.9)
        block.next_to(crumb, DOWN, buff=0.7)
        self.no_overlap(crumb, recap, title, today)
        self.validator.check_in_frame(VGroup(crumb, block))

        n = self.narrate(
            id="intro_01",
            text="In the last video, every pipe became a signed rate: plus if it fills, minus if it empties.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.at_word(n, "signed")
        self.play(FadeIn(recap, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="intro_02",
            text="Today: multiple pipes and the L C M method, three or more pipes without a single fraction.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "multiple")
        self.play(FadeIn(title, shift=UP * 0.1))
        self.at_word(n, "fraction")
        self.play(FadeIn(today, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_intro")

    # ============================================== 1. HOOK ==========

    def hook(self):
        self.scene_start("S01_hook", title="Hook")

        head = self.heading("A housing-society sump")
        pipes = VGroup(pill("A fills alone in 12 h", GOOD, size=LABEL), pill("B fills alone in 15 h", GOOD, size=LABEL),
                       pill("C draws water to the building", BAD, size=LABEL)).arrange(RIGHT, buff=0.4)
        log = pill("all three running:   the empty sump is full in 20 h", FOCUS, size=LABEL)
        ask = pill("how long would C alone take to drain a full sump?", FOCUS, size=LABEL)
        note = text("two inlets, one unknown outlet, and not one fraction needed", LABEL, INK)
        promise = text("by the end of this video: a four-line answer", LABEL, INK, BOLD)
        self.stack(head, [pipes, log, ask, note, promise], buff=0.6, top=0.7)
        self.no_overlap(*pipes)

        n = self.narrate(
            id="hook_01",
            text="A housing-society sump has two inlets: A fills it alone in twelve hours and B in fifteen hours.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "twelve")
        self.play(FadeIn(pipes[0], shift=UP * 0.1))
        self.at_word(n, "fifteen")
        self.play(FadeIn(pipes[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_02",
            text="A third pipe, C, draws water to the building.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "draws")
        self.play(FadeIn(pipes[2], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_03",
            text="With all three running, the empty sump fills in twenty hours.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "running")
        self.play(FadeIn(log, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_04",
            text="How long would C alone take to drain a full sump?",
            voice="default",
            subtitle=True,
            pause_after=3.0,
        )
        self.at_word(n, "drain")
        self.play(FadeIn(ask, scale=1.03))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="hook_05",
            text="Two inlets, one unknown outlet, and not one fraction needed. By the end of this video it is a four-line "
                 "answer.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "fraction")
        self.play(FadeIn(note, shift=UP * 0.1))
        self.at_word(n, "four-line")
        self.play(FadeIn(promise, shift=UP * 0.1))
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
            text="First, solve three-or-more-pipe problems with L C M units and signed rates.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "solve")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "signed")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="objectives_03",
            text="Second, find a missing pipe's time, and tell from the sign whether it fills or empties.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "missing")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "sign")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="objectives_04",
            text="Third, handle pairs, n times as fast, and capacities given in litres per minute.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "pairs")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "litres")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_objectives")

    # ============================================== 3. WHY THIS MATTERS ==========

    def why_this_matters(self):
        self.scene_start("S03_why_this_matters", title="Why This Matters")

        head = self.heading("Why this matters")
        method = pill("the LCM method (Lesson 13, Video 2) removes fractions from the working", WORD, size=LABEL)
        signs = text("with outlets in the picture, it also makes the signs visible", LABEL, INK, BOLD)
        outlet = pill("a missing pipe that comes out negative is an outlet", FOCUS, size=LABEL)
        self.stack(head, [method, signs, outlet], buff=0.9, top=1.1)

        n = self.narrate(
            id="why_this_matters_01",
            text="The L C M method from lesson thirteen, video two, removes fractions from the working.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "removes")
        self.play(FadeIn(method, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="why_this_matters_02",
            text="With outlets in the picture, it also makes the signs visible: a missing pipe that comes out negative is "
                 "an outlet, and the arithmetic tells you so.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "visible")
        self.play(FadeIn(signs, shift=UP * 0.1))
        self.at_word(n, "negative")
        self.play(FadeIn(outlet, scale=1.03))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_why_this_matters")

    # ============================================== 4. CONCEPT - LCM UNITS WITH SIGNS ==========

    def units_with_signs(self):
        self.scene_start("S04_units_with_signs", title="Concept - LCM Units with Signs")

        head = self.heading("LCM units with signs")
        blocks = two_line_blocks(STEPS_A, WORD)
        self.stack(head, list(blocks), buff=0.5, top=0.7, align=LEFT)

        n = self.narrate(
            id="units_with_signs_01",
            text="The total is the L C M of every time in the question, fill times and empty times alike. For twelve, "
                 "fifteen and twenty hours: sixty units.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "every")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "sixty")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="units_with_signs_02",
            text="Sign each pipe's units. Inlets add units per hour; outlets subtract them: A is plus five, B is plus "
                 "four.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Sign")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "plus")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="units_with_signs_03",
            text="The missing pipe is all together, minus the known pipes. All three: sixty divided by twenty is plus "
                 "three an hour, so C is three minus five minus four: minus six.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "missing")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "divided")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="units_with_signs_04",
            text="Read the sign. A positive result is an inlet; a negative result is an outlet. C, at minus six, empties "
                 "sixty units in ten hours.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Read")
        self.play(FadeIn(blocks[3][0], shift=RIGHT * 0.2))
        self.at_word(n, "positive")
        self.play(Indicate(blocks[3][0], color=FOCUS, scale_factor=1.03))
        self.at_word(n, "empties")
        self.play(FadeIn(blocks[3][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_units_with_signs")

    # ============================================== 5. CONCEPT - PAIRS, N TIMES AS FAST, AND LITRES ==========

    def pairs_speed_litres(self):
        self.scene_start("S05_pairs_speed_litres", title="Concept - Pairs, n Times as Fast, and Litres")

        head = self.heading("Pairs, “n times as fast”, and litres")
        blocks = two_line_blocks(STEPS_B, WORD)
        self.stack(head, list(blocks), buff=0.75, top=1.0, align=LEFT)

        n = self.narrate(
            id="pairs_speed_litres_01",
            text="Pairs given: add and halve. A plus B, plus B plus C, plus C plus A, is two times A plus B plus C, "
                 "exactly as in lesson thirteen.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "halve")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "times")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="pairs_speed_litres_02",
            text="N times as fast gives units directly. A twice as fast as B means A is two units and B is one unit a "
                 "minute, and the total is the combined units times the combined time.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "directly")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "twice")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="pairs_speed_litres_03",
            text="Litres per minute: the capacity is the total. If flows are in litres, work in litres: capacity is flow "
                 "times time, and time is capacity divided by net flow. Keep every flow in the same time unit.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "capacity")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "work")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.at_word(n, "Keep")
        self.play(Indicate(blocks[2][1], color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_pairs_speed_litres")

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
            text="Here is the formula box. The total is the L C M of all the fill and empty times, or the capacity in "
                 "litres.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "box")
        self.play(FadeIn(box[0]))
        self.at_word(n, "total")
        self.play(FadeIn(lines[0], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_box_02",
            text="Units per hour: an inlet is plus the total divided by its time; an outlet is minus the total divided by "
                 "its time.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "inlet")
        self.play(FadeIn(lines[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_box_03",
            text="The missing pipe is the all-together units minus the known pipes' units, and its sign shows inlet or "
                 "outlet.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "missing")
        self.play(FadeIn(lines[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_box_04",
            text="For pairs, A plus B plus C is the sum of the pair units divided by two.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "pairs")
        self.play(FadeIn(lines[3], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_box_05",
            text="And capacity is flow times time, so time is capacity divided by net flow.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "capacity")
        self.play(FadeIn(lines[4], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_formula_box")

    # ============================================== 7. THE ANALOGY - A WAREHOUSE ==========

    def analogy(self):
        self.scene_start("S07_analogy", title="The Analogy - A Warehouse")

        head = self.heading("A warehouse")
        docks = VGroup(pill("receiving docks:  add stock", GOOD, size=LABEL), pill("dispatch dock:  removes stock", BAD, size=LABEL),
                       pill("stock changes by  in − out  each hour", FOCUS, size=LABEL)).arrange(RIGHT, buff=0.35)
        fit_width(docks, SAFE_W - 0.4)
        third = text("know the total change and two docks: the third dock is a subtraction", LABEL, INK, BOLD)
        ships = text("a negative count simply means it ships out", LABEL, MUTED)
        stops = VGroup(text("Where the analogy stops", LABEL, BAD, BOLD),
                       text("a warehouse can schedule its docks", LABEL, INK),
                       text("here every open pipe runs nonstop at its fixed rate", LABEL, MUTED)).arrange(DOWN, buff=0.2)
        self.stack(head, [docks, third, ships, stops], buff=0.6, top=0.7)
        self.no_overlap(*docks)

        n = self.narrate(
            id="analogy_01",
            text="Think of a warehouse. Docks that receive pallets add stock; the dispatch dock removes it.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "warehouse")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "receive")
        self.play(FadeIn(docks[0], shift=UP * 0.1))
        self.at_word(n, "dispatch")
        self.play(FadeIn(docks[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_02",
            text="If you know the total change per hour and two of the docks, the third dock's count is a subtraction, and "
                 "a negative count simply means it ships out.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "change")
        self.play(FadeIn(docks[2], shift=UP * 0.1))
        self.at_word(n, "subtraction")
        self.play(FadeIn(third, shift=UP * 0.1))
        self.at_word(n, "negative")
        self.play(FadeIn(ships, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_03",
            text="Where the analogy stops: a warehouse can schedule its docks; in these questions every open pipe runs "
                 "nonstop at its fixed rate.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "stops")
        self.play(FadeIn(stops[0], shift=UP * 0.1))
        self.at_word(n, "schedule")
        self.play(FadeIn(stops[1], shift=UP * 0.1))
        self.at_word(n, "nonstop")
        self.play(FadeIn(stops[2], shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S07_analogy")

    # ============================================== 8. WORKED EXAMPLE - CLOSING THE HOOK ==========

    def hook_solved(self):
        self.scene_start("S08_hook_solved", title="Worked Example - Closing the Hook")

        head = self.heading("The sump:   A 12 h,  B 15 h,  all three 20 h")
        steps = self.solve_steps([("Sump  =  LCM(12, 15, 20)", "=  60 units"),
                                  ("A = +5,   B = +4;      all three:  60 ÷ 20", "=  +3 an hour"),
                                  ("C  =  3 − 5 − 4", "=  −6 units an hour"),
                                  ("C is an outlet:    60 ÷ 6", "=  10 hours to drain")])
        self.stack(head, [steps], top=1.0)
        self.no_overlap(*steps)

        n = self.narrate(
            id="hook_solved_01",
            text="The sump is the L C M of twelve, fifteen and twenty: sixty units.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "sump")
        self.play(FadeIn(steps[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "sixty")
        self.play(FadeIn(steps[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_solved_02",
            text="A is plus five and B is plus four. All three together: sixty divided by twenty is plus three an hour.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "plus")
        self.play(FadeIn(steps[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "divided")
        self.play(FadeIn(steps[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_solved_03",
            text="So C is three minus five minus four: minus six units an hour.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "minus")
        self.play(FadeIn(steps[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "six")
        self.play(FadeIn(steps[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_solved_04",
            text="C is an outlet, and alone it drains the full sump in sixty divided by six: ten hours.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "outlet")
        self.play(FadeIn(steps[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "ten")
        self.play(FadeIn(steps[3][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S08_hook_solved")

    # ============================================== 9. A SECOND WORKED EXAMPLE - PAIRS GIVEN ==========

    def second_example(self):
        self.scene_start("S09_second_example", title="A Second Worked Example - Pairs Given")

        head = self.heading("Pairs given")
        ask = text("A + B fill in 10 h,   B + C in 18 h,   C + A in 15 h:    all three together?    C alone?", LABEL, MUTED)
        fit_width(ask, SAFE_W - 0.6)
        steps = self.solve_steps([("Total  =  LCM(10, 18, 15)", "=  90 units"),
                                  ("A + B = 9,   B + C = 5,   C + A = 6;      2(A + B + C) = 20", "A + B + C = 10"),
                                  ("All three:    90 ÷ 10", "=  9 hours"),
                                  ("C  =  10 − (A + B)  =  10 − 9  =  1 unit an hour", "C alone:  90 hours")])
        self.stack(head, [ask, steps], buff=0.7, top=0.7)
        self.no_overlap(*steps)

        n = self.narrate(
            id="second_example_01",
            text="Pipes A and B together fill a tank in ten hours, B and C in eighteen hours, and C and A in fifteen "
                 "hours. How long do all three take together, and how long does C take alone?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Pipes")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "fill")
        self.play(FadeIn(ask, shift=UP * 0.1))
        self.at_word(n, "alone")
        self.play(Indicate(ask, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_02",
            text="The total is the L C M of ten, eighteen and fifteen: ninety units.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "total")
        self.play(FadeIn(steps[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "ninety")
        self.play(FadeIn(steps[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_03",
            text="A plus B is nine, B plus C is five, and C plus A is six units an hour. Adding, twice the sum is twenty, "
                 "so A plus B plus C is ten.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "nine")
        self.play(FadeIn(steps[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "ten")
        self.play(FadeIn(steps[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_04",
            text="All three take ninety divided by ten: nine hours.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "divided")
        self.play(FadeIn(steps[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "nine")
        self.play(FadeIn(steps[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_05",
            text="C is ten minus A plus B, which is ten minus nine: one unit an hour, so C alone takes ninety hours.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "minus")
        self.play(FadeIn(steps[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "alone")
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
            text="Three inlets: twelve, eighteen and thirty-six minutes. Thirty-six units, three plus two plus one is six: "
                 "six minutes.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "inlets")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "plus")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_03",
            text="A missing inlet: all three take five hours; A twelve, B fifteen. Sixty units, twelve minus five minus "
                 "four is three: C fills in twenty hours.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "missing")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "minus")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_04",
            text="A missing outlet: all three take twenty hours; A twelve, B fifteen. Sixty units, three minus five minus "
                 "four is minus six: C empties in ten hours.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "outlet")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "minus")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Exam patterns  ·  4 to 6 of 6")
        blocks = self.pattern_blocks(PATTERNS[3:6])
        self.stack(head, list(blocks), buff=0.6, top=0.8, align=LEFT)

        n = self.narrate(
            id="exam_patterns_05",
            text="Pairs given: ten, eighteen and fifteen hours. Ninety units, nine plus five plus six, halved, is ten: "
                 "nine hours.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "Pairs")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "halved")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_06",
            text="N times as fast: A is twice as fast as B, and together they take twenty minutes. A two, B one, so the "
                 "total is three times twenty, sixty: A takes thirty minutes and B sixty.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "twice")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "total")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_07",
            text="Flows in litres: inlets of twelve and eighteen litres a minute, an outlet of ten, and a nine hundred "
                 "litre tank. Nine hundred divided by twenty: forty-five minutes.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "litres")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "divided")
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
            text="Trap one: a negative result misread. A fills a tank in ten minutes and B in fifteen; with a third pipe C "
                 "also open, the tank fills in twelve minutes: what does C do?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "misread")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "third")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_02",
            text="The wrong instinct says C fills the tank in twelve minutes. The correct working: sixty units, all three "
                 "make five, A plus B make ten, so C is minus five, and C empties a full tank in twelve minutes.",
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
            text="The rule: the sign of the missing pipe's units tells you whether it is an inlet or an outlet. Report it "
                 "that way.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "rule")
        self.play(FadeIn(rule, shift=UP * 0.1))
        self.at_word(n, "Report")
        self.play(Indicate(rule, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)
        self.clear_stage()

        head, q, wrong, right, rule = self.show_trap(TRAPS[1])

        n = self.narrate(
            id="traps_04",
            text="Trap two: faster read as more time. A fills twice as fast as B, and B alone takes thirty minutes: how "
                 "long does A take?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "faster")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "twice")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_05",
            text="The wrong instinct says sixty minutes. The correct answer is fifteen minutes.",
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
            text="The rule: twice the rate means half the time. The time ratio is the inverse of the rate ratio.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "rule")
        self.play(FadeIn(rule, shift=UP * 0.1))
        self.at_word(n, "inverse")
        self.play(Indicate(rule, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)
        self.clear_stage()

        head, q, wrong, right, rule = self.show_trap(TRAPS[2])

        n = self.narrate(
            id="traps_07",
            text="Trap three: flows in different time units. A twelve hundred litre tank has an inlet of thirty litres a "
                 "minute and an outlet of six hundred litres an hour: what is the time to fill?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "units")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "inlet")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_08",
            text="The wrong instinct says thirty minus six hundred is negative, so it never fills. The correct working: "
                 "six hundred litres an hour is ten litres a minute, so the net is twenty litres a minute: sixty minutes.",
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
            text="The rule: convert every flow to the same unit before adding.",
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
        given = pill("three pipes fill a tank in 20, 30 and 60 minutes:   how long together?", FOCUS, size=LABEL)
        work = VGroup(text("60 units:    3 + 2 + 1  =  6 a minute", BODY, INK, BOLD), text("60 ÷ 6  =  10 minutes", BODY, GOOD, BOLD)).arrange(RIGHT, buff=0.7)
        self.stack(head, [given, work], buff=1.0, top=1.0)
        self.no_overlap(*work)

        n = self.narrate(
            id="checkpoint_01",
            text="Your turn. Three pipes fill a tank in twenty, thirty and sixty minutes. How long do they take together?",
            voice="default",
            subtitle=True,
            pause_after=10.0,
        )
        self.at_word(n, "turn")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "pipes")
        self.play(FadeIn(given, scale=1.03))
        self.at_word(n, "together")
        self.play(Indicate(given, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="checkpoint_02",
            text="Sixty units: three plus two plus one is six a minute, so sixty divided by six is ten minutes.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "plus")
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
            text="Level one, question one: three pipes fill a tank in twelve, eighteen and thirty-six minutes; how long do "
                 "they take together? Question two: two pipes fill a tank in ten and fifteen hours, and a third empties "
                 "the full tank in thirty hours; all three are opened on an empty tank; how long does it take to fill?",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "together")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "third")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="practice_02",
            text="Level two, question three: pipe A fills a tank in twelve hours and pipe B in fifteen hours; with a third "
                 "pipe C also open, the tank fills in five hours; how long would C alone take, and does it fill or empty? "
                 "Question four: pipe A fills a tank twice as fast as pipe B, and together they fill it in twenty minutes; "
                 "how long would each take alone? Question five: two inlets deliver twelve and eighteen litres a minute, "
                 "and an outlet removes ten litres a minute; how long will they take to fill an empty nine hundred litre "
                 "tank?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "third")
        self.play(FadeIn(rows[2], shift=RIGHT * 0.2))
        self.at_word(n, "twice")
        self.play(FadeIn(rows[3], shift=RIGHT * 0.2))
        self.at_word(n, "inlets")
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
            text="Level three, question six: pipes A and B together fill a tank in ten hours, B and C in eighteen hours, "
                 "and C and A in fifteen hours; how long would each pipe take alone? Question seven: pipe A fills a tank "
                 "in eight minutes and pipe B in twelve minutes; with a third pipe C also open, the tank fills in six "
                 "minutes; describe pipe C. Question eight: pipe A fills a tank in six hours and pipe B in nine hours, and "
                 "together they deliver fifty litres a minute; find the capacity of the tank.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "each")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "describe")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.at_word(n, "capacity")
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
            text="One: thirty-six units, three plus two plus one is six a minute: six minutes.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "plus")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "minutes")
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_02",
            text="Two: thirty units, plus three plus two minus one is plus four an hour, and thirty divided by four is "
                 "seven and a half hours.",
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
            text="Three: sixty units, all three make twelve and A plus B make nine, so C is plus three: an inlet that "
                 "fills the tank alone in twenty hours.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "units")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "inlet")
        self.play(FadeIn(rows[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_04",
            text="Four: A is two units and B is one unit a minute, so the total is three times twenty, sixty units: A "
                 "alone takes thirty minutes and B sixty.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "total")
        self.play(FadeIn(rows[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "alone")
        self.play(FadeIn(rows[3][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Answer key  ·  5 to 8", GOOD)
        table, rows = self.answer_table(head, ANSWERS_B, 5)

        n = self.narrate(
            id="answers_05",
            text="Five: the net flow is twelve plus eighteen minus ten, twenty litres a minute, and nine hundred divided "
                 "by twenty is forty-five minutes.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "net")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "divided")
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_06",
            text="Six: ninety units, and A plus B plus C is ten; so A is five, eighteen hours; B is four, twenty-two and a "
                 "half hours; and C is one, ninety hours.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "units")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "eighteen")
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_07",
            text="Seven: twenty-four units, A plus B make five and all three make four, so C is minus one: an outlet that "
                 "empties a full tank in twenty-four minutes.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "units")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "outlet")
        self.play(FadeIn(rows[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_08",
            text="Eight: eighteen units; A three and B two, so five units an hour is three thousand litres; one unit is "
                 "six hundred litres, and the capacity is ten thousand eight hundred litres.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "units")
        self.play(FadeIn(rows[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "capacity")
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
            text="Recognise and move. The recognition cue: three or more pipes, a missing pipe, pairs, or flows in litres; "
                 "use L C M units with signs, or litres as the units.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "cue")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "pairs")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_lens_02",
            text="The target time: thirty-five seconds, or forty-five seconds for pairs or litres.",
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
            text="The sanity check: every pipe's units are whole numbers, and a missing pipe's sign must agree with the "
                 "story; a tank that fills more slowly with C open means C is an outlet.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "sanity")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "agree")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S15_exam_lens")

    # ============================================== 16. QUICK REVISION AND SUMMARY ==========

    def summary(self):
        self.scene_start("S16_summary", title="Quick Revision and Summary")

        head = self.heading("Quick revision")
        total = pill("total = LCM of every time;    signed whole units for each pipe;    add", GOOD, size=LABEL)
        missing = pill("missing pipe = all together − known:    its sign says inlet or outlet", WORD, size=LABEL)
        more = VGroup(pill("pairs add to twice the total rate", RATIO, size=SMALL), pill("litre flows: the capacity is the total", FOCUS, size=SMALL))\
            .arrange(RIGHT, buff=0.4)
        docks = text("the warehouse: the third dock is a subtraction", LABEL, MUTED)
        nxt = self.breadcrumb("Next", "Video 3 · Pipes Opened & Closed at Different Times")
        self.stack(head, [total, missing, more, docks, nxt], buff=0.6, top=0.7)
        self.no_overlap(*more)

        n = self.narrate(
            id="summary_01",
            text="Take the L C M of every time as the total, give each pipe signed whole units, and add.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "total")
        self.play(FadeIn(total, scale=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_02",
            text="A missing pipe is the all-together units minus the known ones, and its sign says inlet or outlet.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "missing")
        self.play(FadeIn(missing, scale=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_03",
            text="Pairs add to twice the total rate, and litre flows make the capacity the total.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Pairs")
        self.play(FadeIn(more[0], shift=UP * 0.1))
        self.at_word(n, "litre")
        self.play(FadeIn(more[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_04",
            text="Remember the warehouse docks.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "warehouse")
        self.play(FadeIn(docks, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_05",
            text="Next: pipes opened and closed at different times.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Next")
        self.play(FadeIn(nxt, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S16_summary")

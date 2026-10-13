"""
animation.py for the LMS video generator.

Course : Pre-C-CAT - Section A - Quantitative Aptitude
Video  : Lesson 19 - Time & Distance - 02 - Speed Changes - Late, Early & Ratios

Source script:
  C:\\Scripts\\Section A\\Aptitude\\Sessions 13-18 - Pipes, Time Distance, Partnership\\Lesson 19 - Time & Distance\\02 - Speed Changes - Late, Early & Ratios.pdf

Built on the golden-reference pattern:
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``;
  * layouts stacked with next_to and guarded with ``no_overlap``; nothing is
    ever animated onto or into another box.

Lesson 19, Video 2 of 7. Not the first video of the lesson: a silent breadcrumb, a one-line recap of Video 1, then today's topic. No spoken course welcome.
The narration follows the script section by section. The eight concept steps are split over two screens. The six exam patterns are shown as two-line blocks. The script's subscripted speeds are written as s (slow) and f (fast), and the two gaps as p and q.
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


def usual_from_delay(frac, delay):
    """At ``frac`` of the usual speed the trip is ``delay`` longer (negative: shorter).  Returns the usual time."""
    return delay / (1 / Fraction(frac) - 1)


def distance(slow, fast, gap_minutes):
    """Same distance at two speeds whose trip times differ by the gap."""
    d = slow * fast * Fraction(gap_minutes, 60) / (fast - slow)
    assert (d / slow - d / fast) * 60 == gap_minutes
    return d


# ---- the hook: 3/4 of the usual speed, 20 minutes late ----
USUAL = usual_from_delay(Fraction(3, 4), 20)
assert USUAL == 60 and USUAL + 20 == 80 and 1 / Fraction(3, 4) - 1 == Fraction(1, 3)

# ---- second worked example: 4 km/h 10 late, 5 km/h 5 early ----
OFFICE = distance(4, 5, 10 + 5)
assert OFFICE == 5 and (OFFICE / 4 * 60, OFFICE / 5 * 60) == (75, 60) and 75 - 10 == 65 == 60 + 5

# ---- exam patterns, traps, checkpoint, practice (answers computed) ----
assert usual_from_delay(Fraction(4, 5), 15) == 60 and usual_from_delay(Fraction(5, 4), -12) == 60
assert distance(3, 4, 10 + 5) == 3 and distance(40, 50, 30 - 6) == 80 and 40 * 50 == 2000 and Fraction(24, 60) == Fraction(2, 5)
assert (6 * 10, 5 * 10) == (60, 50) and Fraction(300, 50) - Fraction(300, 60) == 1
assert usual_from_delay(Fraction(5, 6), 10) == 50 and usual_from_delay(Fraction(7, 8), 10) == 70 and 2 * Fraction(5, 4) == Fraction(5, 2)
assert distance(6, 8, 15) == 6 and (60, 45) == (6 * 60 // 6, 6 * 60 // 8) and distance(40, 48, 20 - 5) == 60
assert usual_from_delay(Fraction(6, 5), -10) == 60 and Fraction(240, 60) - Fraction(240, 80) == 1 and 60 * 80 == 4800
assert Fraction(40, 12) - Fraction(40, 15) == Fraction(2, 3) == Fraction(40, 10) - Fraction(40, 12)          # practice 7: S = 12, D = 40
assert Fraction(2, 3) * Fraction(1, 3) == Fraction(2, 9) and 40 / Fraction(2, 9) == 180                       # practice 8

OBJECTIVES = [("Convert a change in speed into a change in time", "over the same distance"),
              ("Find the distance", "when a journey is late at one speed and early at another"),
              ("Solve “had he gone x km/h faster” questions", "with one equation, or by testing the options")]
STEPS_A = [("Same distance:  time is the inverse of speed", "multiply the speed by a/b and the time is multiplied by b/a"),
           ("Slower than usual:  at a/b of the usual speed  (a < b)", "new time = b/a of usual;    extra time = (b − a)/a of the usual time"),
           ("Faster than usual:  at b/a of the usual speed", "time becomes a/b of usual;    time saved = (b − a)/b of the usual time"),
           ("Speed ratio to time ratio:  speeds a : b give times b : a", "a known time difference equals the difference in parts")]
STEPS_B = [("Late at one speed, early at another:  gap = late + early", "both trips late:  the gap is the difference of the two delays"),
           ("The gap gives the distance", "D/s − D/f = gap,   so   D = s × f × gap ÷ (f − s)         (s slow, f fast)"),
           ("“Had he gone x km/h faster, he would have taken t less”", "write  D/S − D/(S + x) = t  and solve, or test the options"),
           ("Convert minutes to hours", "before putting them next to km/h")]
FORMULAS = ["New time   =   usual time × (usual speed / new speed)",
            "At a/b of the usual speed:      extra time  =  usual time × (b − a)/a",
            "Late by p at speed s, early by q at speed f  (s < f):      D  =  s × f × (p + q) ÷ (f − s)",
            "Both late  (p at s, q at f):      D  =  s × f × (p − q) ÷ (f − s)"]
PATTERNS = [("Fraction of usual speed", "at 4/5 of usual speed, 15 min late", "extra = 1/4 of usual", "usual 60 min"),
            ("Faster than usual", "at 5/4 of usual speed, 12 min early", "saved = 1/5 of usual", "usual 60 min"),
            ("Late and early", "3 km/h: 10 min late;   4 km/h: 5 min early", "12 × 1/4 ÷ 1", "3 km"),
            ("Both late", "40 km/h: 30 min late;   50 km/h: 6 min late", "2,000 × 2/5 ÷ 10", "80 km"),
            ("Speed ratio", "speeds 5 : 6;   the slower takes 10 min more", "times 6 : 5;   1 part = 10 min", "60 min and 50 min"),
            ("x km/h faster", "300 km;   10 km/h faster saves 1 h", "300/S − 300/(S + 10) = 1", "50 km/h")]
TRAPS = [("Trap 1  ·  the speed fraction used for the delay", "At 3/4 of usual speed, 20 minutes late.  Usual time?",
          "delay = 1/4 of usual:  80 min", "delay = 1/3 of usual:  60 min",
          "The time becomes 4/3, so the extra is 1/3; the 80 minutes is today's trip."),
         ("Trap 2  ·  late and early subtracted", "4 km/h: 10 minutes late;   5 km/h: 5 minutes early.  Time gap?",
          "10 − 5  =  5 minutes", "10 + 5  =  15 minutes",
          "Late and early are on opposite sides of the right time: add.  Both late: subtract."),
         ("Trap 3  ·  minutes left in the formula", "D = 4 × 5 × gap ÷ 1,  with a gap of 15 minutes.",
          "4 × 5 × 15  =  300 km", "4 × 5 × 1/4  =  5 km",
          "With km/h, the gap must be in hours.")]
PRACTICE_A = [("L1", "A train runs at 7/8 of its usual speed and arrives 10 minutes late.  Find its usual time."),
              ("L1", "Two cars cover the same route with speeds in the ratio 4 : 5.  The faster takes 2 hours.  The slower?"),
              ("L2", "Walking at 6 km/h, a man is 10 minutes late; at 8 km/h, he is 5 minutes early.  Find the distance."),
              ("L2", "A bus running at 40 km/h is 20 minutes late; at 48 km/h it is 5 minutes late.  Find the distance."),
              ("L2", "By increasing her speed by 20%, a commuter saves 10 minutes.  Find her usual time.")]
PRACTICE_B = [("L3", "A car covers 240 km.  If its speed were 20 km/h more, it would take 1 hour less.  Find its speed."),
              ("L3", "3 km/h faster: 40 minutes less.   2 km/h slower: 40 minutes more.   Find the distance."),
              ("L3", "A train covers the first 1/3 of its journey at usual speed, the rest at 3/4 of it; 40 min late.  Usual time?")]
ANSWERS_A = [("time × 8/7;   the extra 1/7 of the usual time is 10 min", "70 minutes"),
             ("times 5 : 4;    2 × 5/4", "2.5 hours"),
             ("gap 15 min = 1/4 h;   6 × 8 × 1/4 ÷ 2     (60 and 45 min)", "6 km"),
             ("both late:  gap 20 − 5 = 15 min;   40 × 48 × 1/4 ÷ 8", "60 km")]
ANSWERS_B = [("speed × 6/5, time × 5/6;   the saving is 1/6 of usual", "60 minutes"),
             ("240/S − 240/(S + 20) = 1;    S(S + 20) = 4,800", "60 km/h"),
             ("3/(S + 3) = 2/(S − 2):    S = 12 km/h", "40 km"),
             ("the last 2T/3 stretches by 1/3:    2T/9 = 40 min", "180 min  =  3 hours")]
LENS = [("Recognition cue", "“of his usual speed”, “late”, “early”, “would have taken … less”:  same distance, time inverse to speed"),
        ("Target time", "30 seconds;  40 seconds for late-and-early"),
        ("Sanity check", "the slower trip takes longer;  recompute both trip times and confirm the late and early minutes")]


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


class SpeedChangesLateEarlyAndRatiosVideo(LMSScene):
    lesson_title = "Speed Changes: Late, Early & Ratios"

    def construct(self):
        self.camera.background_color = BG

        self.intro()
        self.hook()
        self.objectives()
        self.why_this_matters()
        self.inverse_of_speed()
        self.gap_gives_distance()
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

        crumb = self.breadcrumb("Quantitative Aptitude", "Lesson 19 · Time & Distance", "Video 2 of 7")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        recap = VGroup(text("last video", SMALL, MUTED), pill("D = S × T;    km/h → m/s:  × 5/18", WORD, size=LABEL)).arrange(DOWN, buff=0.25)
        title = fit_width(text("Speed Changes: Late, Early & Ratios", TITLE, INK, BOLD), SAFE_W - 0.4)
        today = text("today: a change in speed tells you the change in time", LABEL, FOCUS)
        block = VGroup(recap, title, today).arrange(DOWN, buff=0.7)
        fit_within(block, SAFE_W, SAFE_H - crumb.height - 0.9)
        block.next_to(crumb, DOWN, buff=0.7)
        self.no_overlap(crumb, recap, title, today)
        self.validator.check_in_frame(VGroup(crumb, block))

        n = self.narrate(
            id="intro_01",
            text="In the last video, D was S times T with matching units, and five over eighteen turned kilometres per "
                 "hour into metres per second.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.at_word(n, "matching")
        self.play(FadeIn(recap, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="intro_02",
            text="Today: speed changes, late, early and ratios, where a change in speed alone tells you the change in "
                 "time.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "speed")
        self.play(FadeIn(title, shift=UP * 0.1))
        self.at_word(n, "alone")
        self.play(FadeIn(today, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_intro")

    # ============================================== 1. HOOK ==========

    def hook(self):
        self.scene_start("S01_hook", title="Hook")

        head = self.heading("A rainy morning")
        row = VGroup(pill("speed today:  3/4 of usual", BAD, size=BODY), pill("standup started 20 minutes ago", BAD, size=BODY)).arrange(RIGHT, buff=0.6)
        ask = pill("how long does the trip normally take?", FOCUS, size=BODY)
        none = text("neither the speed nor the distance is given, and you don't need either", LABEL, MUTED)
        alone = text("the change in speed alone tells you the change in time", LABEL, INK, BOLD)
        self.stack(head, [row, ask, none, alone], buff=0.75, top=0.9)
        self.no_overlap(*row)

        n = self.narrate(
            id="hook_01",
            text="Heavy rain. Your cab crawls along the usual route at three-quarters of its normal speed, and you walk "
                 "into the morning standup twenty minutes late.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "rain")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "three-quarters")
        self.play(FadeIn(row[0], shift=UP * 0.1))
        self.at_word(n, "late")
        self.play(FadeIn(row[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_02",
            text="How long does the trip normally take?",
            voice="default",
            subtitle=True,
            pause_after=3.0,
        )
        self.at_word(n, "normally")
        self.play(FadeIn(ask, scale=1.03))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="hook_03",
            text="Neither the speed nor the distance is given, and you don't need either. The change in speed alone tells "
                 "you the change in time.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Neither")
        self.play(FadeIn(none, shift=UP * 0.1))
        self.at_word(n, "alone")
        self.play(FadeIn(alone, shift=UP * 0.1))
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
            text="First, convert a change in speed into a change in time over the same distance.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "convert")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "same")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="objectives_03",
            text="Second, find the distance when a journey is late at one speed and early at another.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "distance")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "late")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="objectives_04",
            text="Third, solve had he gone x kilometres per hour faster questions, with one equation or by testing the "
                 "options.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "solve")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "equation")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_objectives")

    # ============================================== 3. WHY THIS MATTERS ==========

    def why_this_matters(self):
        self.scene_start("S03_why_this_matters", title="Why This Matters")

        head = self.heading("Why this matters")
        data = fit_width(pill("almost no direct data:  a fraction of a speed, a few minutes late or early", WORD, size=LABEL), SAFE_W - 0.4)
        quick = text("quick marks, once you see that the same distance makes time the inverse of speed", LABEL, INK, BOLD)
        fit_width(quick, SAFE_W - 0.6)
        guess = text("slow guesswork if you don't", LABEL, MUTED)
        self.stack(head, [data, quick, guess], buff=0.9, top=1.1)

        n = self.narrate(
            id="why_this_matters_01",
            text="These questions give almost no direct data: a fraction of a speed, a few minutes late, a few minutes "
                 "early.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "data")
        self.play(FadeIn(data, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="why_this_matters_02",
            text="They are quick marks once you see that the same distance makes time the inverse of speed, and slow "
                 "guesswork if you don't.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "quick")
        self.play(FadeIn(quick, shift=UP * 0.1))
        self.at_word(n, "guesswork")
        self.play(FadeIn(guess, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_why_this_matters")

    # ============================================== 4. CONCEPT - TIME IS THE INVERSE OF SPEED ==========

    def inverse_of_speed(self):
        self.scene_start("S04_inverse_of_speed", title="Concept - Time Is the Inverse of Speed")

        head = self.heading("Time is the inverse of speed")
        blocks = two_line_blocks(STEPS_A, WORD)
        self.stack(head, list(blocks), buff=0.5, top=0.7, align=LEFT)

        n = self.narrate(
            id="inverse_of_speed_01",
            text="Over the same distance, time is the inverse of speed: multiply the speed by a over b, and the time is "
                 "multiplied by b over a.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "inverse")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "multiplied")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="inverse_of_speed_02",
            text="Slower than usual: at a over b of the usual speed, the new time is b over a of the usual time, so the "
                 "extra time is b minus a, over a, of the usual time.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Slower")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "extra")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="inverse_of_speed_03",
            text="Faster than usual: at b over a of the usual speed, the time becomes a over b of the usual, so the time "
                 "saved is b minus a, over b, of the usual time.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Faster")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "saved")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="inverse_of_speed_04",
            text="Speed ratio to time ratio: speeds a to b give times b to a. If the time difference is known, it equals "
                 "the difference in parts.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "give")
        self.play(FadeIn(blocks[3][0], shift=RIGHT * 0.2))
        self.at_word(n, "parts")
        self.play(FadeIn(blocks[3][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_inverse_of_speed")

    # ============================================== 5. CONCEPT - THE GAP GIVES THE DISTANCE ==========

    def gap_gives_distance(self):
        self.scene_start("S05_gap_gives_distance", title="Concept - The Gap Gives the Distance")

        head = self.heading("The gap gives the distance")
        blocks = two_line_blocks(STEPS_B, WORD)
        self.stack(head, list(blocks), buff=0.5, top=0.7, align=LEFT)

        n = self.narrate(
            id="gap_gives_distance_01",
            text="Late at one speed, early at another: between the two trips, the time gap is late plus early. If both "
                 "trips are late, the gap is the difference of the two delays.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "plus")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "difference")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="gap_gives_distance_02",
            text="The gap gives the distance: D over the slow speed, minus D over the fast speed, is the gap, so D is slow "
                 "times fast times the gap, divided by fast minus slow.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "gives")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "divided")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="gap_gives_distance_03",
            text="Had he gone x kilometres per hour faster, he would have taken t less: write D over S, minus D over S "
                 "plus x, equals t, and solve, or test the options.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "faster")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "write")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="gap_gives_distance_04",
            text="And convert minutes to hours before putting them next to kilometres per hour.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "convert")
        self.play(FadeIn(blocks[3][0], shift=RIGHT * 0.2))
        self.at_word(n, "before")
        self.play(FadeIn(blocks[3][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_gap_gives_distance")

    # ============================================== 6. FORMULA BOX ==========

    def formula_box(self):
        self.scene_start("S06_formula_box", title="Formula Box")

        head = self.heading("Formula box", GOOD)
        lines = VGroup(*[text(f, LABEL, INK) for f in FORMULAS]).arrange(DOWN, buff=0.55, aligned_edge=LEFT)
        fit_width(lines, SAFE_W - 1.6)
        box = self.card(lines, width=SAFE_W - 0.4, color=GOOD, pad=0.5)
        self.stack(head, [box], top=0.7)

        n = self.narrate(
            id="formula_box_01",
            text="Here is the formula box. The new time is the usual time, times the usual speed over the new speed.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "box")
        self.play(FadeIn(box[0]))
        self.at_word(n, "new")
        self.play(FadeIn(lines[0], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_box_02",
            text="At a over b of the usual speed, the extra time is the usual time times b minus a, over a.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "extra")
        self.play(FadeIn(lines[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_box_03",
            text="Late at the slow speed and early at the fast speed: the distance is slow times fast, times the sum of "
                 "the two gaps, divided by the difference of the speeds.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "sum")
        self.play(FadeIn(lines[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_box_04",
            text="If both trips are late, use the difference of the two delays instead.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "both")
        self.play(FadeIn(lines[3], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_formula_box")

    # ============================================== 7. THE ANALOGY - A FILE DOWNLOAD ==========

    def analogy(self):
        self.scene_start("S07_analogy", title="The Analogy - A File Download")

        head = self.heading("A file download")
        fixed = pill("a fixed-size file  =  a journey of fixed distance", WORD, size=LABEL)
        drop = VGroup(pill("bandwidth drops to 3/4", BAD, size=LABEL), pill("the download takes 4/3 as long", FOCUS, size=LABEL)).arrange(RIGHT, buff=0.5)
        predict = text("predict the delay from the bandwidth ratio alone, without knowing the file size", LABEL, INK, BOLD)
        fit_width(predict, SAFE_W - 0.6)
        stops = VGroup(text("Where the analogy stops", LABEL, BAD, BOLD),
                       text("real bandwidth fluctuates second by second", LABEL, INK),
                       text("exam questions assume a constant new speed for the trip, or the stated part of it", LABEL, MUTED)).arrange(DOWN, buff=0.2)
        self.stack(head, [fixed, drop, predict, stops], buff=0.6, top=0.7)
        self.no_overlap(*drop)

        n = self.narrate(
            id="analogy_01",
            text="Downloading a fixed-size file is a journey of fixed distance.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "file")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "journey")
        self.play(FadeIn(fixed, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_02",
            text="If the bandwidth drops to three-quarters, the download takes four-thirds as long.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "drops")
        self.play(FadeIn(drop[0], shift=UP * 0.1))
        self.at_word(n, "takes")
        self.play(FadeIn(drop[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_03",
            text="You can predict the delay from the bandwidth ratio alone, without knowing the file size.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "predict")
        self.play(FadeIn(predict, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_04",
            text="Where the analogy stops: real bandwidth fluctuates second by second. Exam questions assume the new speed "
                 "is constant for the whole trip, or for the stated part of it.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "stops")
        self.play(FadeIn(stops[0], shift=UP * 0.1))
        self.at_word(n, "fluctuates")
        self.play(FadeIn(stops[1], shift=UP * 0.1))
        self.at_word(n, "constant")
        self.play(FadeIn(stops[2], shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S07_analogy")

    # ============================================== 8. WORKED EXAMPLE - CLOSING THE HOOK ==========

    def hook_solved(self):
        self.scene_start("S08_hook_solved", title="Worked Example - Closing the Hook")

        head = self.heading("At 3/4 of the usual speed, 20 minutes late")
        bar = VGroup(*[Rectangle(width=1.6, height=0.35, color=WORD, fill_color=WORD, fill_opacity=0.45) for _ in range(3)],
                     Rectangle(width=1.6, height=0.35, color=BAD, fill_color=BAD, fill_opacity=0.55)).arrange(RIGHT, buff=0)
        steps = self.solve_steps([("At 3/4 of the speed:    the time", "=  4/3 of the usual"),
                                  ("The extra 1/3 of the usual time", "=  20 minutes"),
                                  ("Usual trip:    3 × 20", "=  60 minutes"),
                                  ("Today's trip:    60 + 20", "=  80 minutes")])
        self.stack(head, [bar, steps], buff=0.7, top=0.8)
        self.no_overlap(*steps)

        n = self.narrate(
            id="hook_solved_01",
            text="At three-quarters of the speed, the time is four-thirds of the usual.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "time")
        self.play(FadeIn(steps[0][:2], shift=RIGHT * 0.2), FadeIn(bar[:3]))
        self.at_word(n, "four-thirds")
        self.play(FadeIn(steps[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_solved_02",
            text="The extra one third of the usual time is twenty minutes, so the usual trip takes sixty minutes.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "extra")
        self.play(FadeIn(steps[1], shift=RIGHT * 0.2), FadeIn(bar[3]))
        self.at_word(n, "sixty")
        self.play(FadeIn(steps[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_solved_03",
            text="Today's trip took eighty minutes.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "eighty")
        self.play(FadeIn(steps[3], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S08_hook_solved")

    # ============================================== 9. A SECOND WORKED EXAMPLE - LATE AND EARLY ==========

    def second_example(self):
        self.scene_start("S09_second_example", title="A Second Worked Example - Late and Early")

        head = self.heading("Late and early")
        ask = text("at 4 km/h she is 10 minutes late; at 5 km/h, 5 minutes early:   how far is the office, and what time should she allow?",
                   LABEL, MUTED)
        fit_width(ask, SAFE_W - 0.6)
        steps = self.solve_steps([("Time gap between the two walks:    10 + 5 = 15 minutes", "=  1/4 h"),
                                  ("D  =  4 × 5 × 1/4 ÷ (5 − 4)", "=  5 km"),
                                  ("Check:    5 ÷ 4 = 75 min;      5 ÷ 5 = 60 min", "right time:  75 − 10 = 65 min"),
                                  ("60 minutes is", "indeed 5 minutes early")])
        self.stack(head, [ask, steps], buff=0.7, top=0.7)
        self.no_overlap(*steps)

        n = self.narrate(
            id="second_example_01",
            text="Walking at four kilometres per hour, an employee reaches the office ten minutes late. Walking at five "
                 "kilometres per hour, she is five minutes early. How far is the office, and what is the right time to "
                 "allow?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Walking")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "early")
        self.play(FadeIn(ask, shift=UP * 0.1))
        self.at_word(n, "far")
        self.play(Indicate(ask, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_02",
            text="The time gap between the two walks is ten plus five, fifteen minutes, which is a quarter of an hour.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "plus")
        self.play(FadeIn(steps[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "quarter")
        self.play(FadeIn(steps[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_03",
            text="The distance is four times five times a quarter, divided by five minus four: five kilometres.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "divided")
        self.play(FadeIn(steps[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "kilometres")
        self.play(FadeIn(steps[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_04",
            text="Check: five divided by four is seventy-five minutes, and five divided by five is sixty minutes. The "
                 "right time is seventy-five minus ten, sixty-five minutes, and sixty is indeed five minutes early.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Check")
        self.play(FadeIn(steps[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "right")
        self.play(FadeIn(steps[2][2], shift=LEFT * 0.1))
        self.at_word(n, "indeed")
        self.play(FadeIn(steps[3], shift=RIGHT * 0.2))
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
            text="A fraction of the usual speed: at four fifths of the usual speed, fifteen minutes late. The extra is one "
                 "quarter of the usual time: the usual time is sixty minutes.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "fraction")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "extra")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_03",
            text="Faster than usual: at five quarters of the usual speed, twelve minutes early. The saving is one fifth of "
                 "the usual time: sixty minutes.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Faster")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "saving")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_04",
            text="Late and early: at three kilometres per hour, ten minutes late; at four, five minutes early. Twelve "
                 "times a quarter, divided by one: three kilometres.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "early")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "divided")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Exam patterns  ·  4 to 6 of 6")
        blocks = self.pattern_blocks(PATTERNS[3:6])
        self.stack(head, list(blocks), buff=0.6, top=0.8, align=LEFT)

        n = self.narrate(
            id="exam_patterns_05",
            text="Both late: at forty kilometres per hour, thirty minutes late; at fifty, six minutes late. Two thousand "
                 "times two fifths, divided by ten: eighty kilometres.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "Both")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "divided")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_06",
            text="Speed ratio: speeds five to six, and the slower takes ten minutes more. The times are six to five, and "
                 "one part is ten minutes: sixty minutes and fifty minutes.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "ratio")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "part")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_07",
            text="X kilometres per hour faster: three hundred kilometres, and ten kilometres per hour faster saves one "
                 "hour. Three hundred over S, minus three hundred over S plus ten, is one: fifty kilometres per hour.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "saves")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "minus")
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
            text="Trap one: the speed fraction used for the delay. At three-quarters of the usual speed, twenty minutes "
                 "late: what is the usual time?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "fraction")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "late")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_02",
            text="The wrong instinct says the delay is one quarter of the usual time, so eighty minutes. The correct "
                 "answer: the delay is one third of the usual time, so sixty minutes.",
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
            text="The rule: the time becomes four-thirds, so the extra is one third; the eighty minutes is today's trip.",
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
            text="Trap two: late and early subtracted. At four kilometres per hour, ten minutes late; at five, five "
                 "minutes early: what is the time gap?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "subtracted")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "gap")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_05",
            text="The wrong instinct says ten minus five, five minutes. The correct answer is ten plus five, fifteen "
                 "minutes.",
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
            text="The rule: late and early lie on opposite sides of the right time, so add them. Subtract only when both "
                 "trips are late, or both early.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "rule")
        self.play(FadeIn(rule, shift=UP * 0.1))
        self.at_word(n, "Subtract")
        self.play(Indicate(rule, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)
        self.clear_stage()

        head, q, wrong, right, rule = self.show_trap(TRAPS[2])

        n = self.narrate(
            id="traps_07",
            text="Trap three: minutes left in the formula. The distance is four times five times the gap, divided by one, "
                 "with a gap of fifteen minutes.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "minutes")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "distance")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_08",
            text="The wrong instinct multiplies four by five by fifteen: three hundred kilometres. The correct answer uses "
                 "a quarter of an hour: five kilometres.",
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
            text="The rule: with kilometres per hour, the gap must be in hours.",
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
        given = pill("walking at 5/6 of his usual speed, a man is 10 minutes late:   his usual time?", FOCUS, size=LABEL)
        work = VGroup(text("time × 6/5:    the extra is 1/5 of the usual time", LABEL, INK, BOLD),
                      text("usual time  =  50 minutes", BODY, GOOD, BOLD)).arrange(DOWN, buff=0.4)
        self.stack(head, [given, work], buff=0.9, top=1.0)
        self.no_overlap(*work)

        n = self.narrate(
            id="checkpoint_01",
            text="Your turn. Walking at five sixths of his usual speed, a man is ten minutes late. What is his usual time?",
            voice="default",
            subtitle=True,
            pause_after=10.0,
        )
        self.at_word(n, "turn")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "Walking")
        self.play(FadeIn(given, scale=1.03))
        self.at_word(n, "usual", occurrence=2)
        self.play(Indicate(given, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="checkpoint_02",
            text="The time is multiplied by six fifths, so the extra is one fifth of the usual time, and the usual time is "
                 "fifty minutes.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "extra")
        self.play(FadeIn(work[0], shift=UP * 0.1))
        self.at_word(n, "fifty")
        self.play(FadeIn(work[1], shift=UP * 0.1))
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
            text="Level one, question one: a train runs at seven eighths of its usual speed and arrives ten minutes late; "
                 "find its usual time. Question two: two cars cover the same route with speeds in the ratio four to five; "
                 "the faster takes two hours; how long does the slower take?",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "train")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "cars")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="practice_02",
            text="Level two, question three: walking at six kilometres per hour, a man is ten minutes late; at eight "
                 "kilometres per hour, he is five minutes early; find the distance. Question four: a bus running at forty "
                 "kilometres per hour is twenty minutes late; at forty-eight kilometres per hour it is five minutes late; "
                 "find the distance. Question five: by increasing her speed by twenty percent, a commuter saves ten "
                 "minutes; find her usual time.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "walking")
        self.play(FadeIn(rows[2], shift=RIGHT * 0.2))
        self.at_word(n, "bus")
        self.play(FadeIn(rows[3], shift=RIGHT * 0.2))
        self.at_word(n, "commuter")
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
            text="Level three, question six: a car covers two hundred and forty kilometres; if its speed were twenty "
                 "kilometres per hour more, it would take one hour less; find its speed. Question seven: had a man walked "
                 "three kilometres per hour faster, he would have taken forty minutes less; had he walked two kilometres "
                 "per hour slower, he would have taken forty minutes more; find the distance. Question eight: a train "
                 "covers the first third of its journey at its usual speed, and the rest at three-quarters of its usual "
                 "speed; it arrives forty minutes late; find its usual journey time.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "car")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "walked")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.at_word(n, "train")
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
            text="One: the time is multiplied by eight sevenths; the extra one seventh of the usual time is ten minutes, "
                 "so the usual time is seventy minutes.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "multiplied")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "seventy")
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_02",
            text="Two: the times are five to four, so two times five quarters is two and a half hours.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "times")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "half")
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_03",
            text="Three: the gap is fifteen minutes, a quarter of an hour, so six times eight times a quarter, divided by "
                 "two, is six kilometres. Check: sixty minutes and forty-five minutes, either side of fifty.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "gap")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "kilometres")
        self.play(FadeIn(rows[2][2], shift=LEFT * 0.1))
        self.at_word(n, "Check")
        self.play(Indicate(rows[2][1], color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_04",
            text="Four: both are late, so the gap is twenty minus five, fifteen minutes. Forty times forty-eight times a "
                 "quarter, divided by eight, is sixty kilometres.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "gap")
        self.play(FadeIn(rows[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "sixty")
        self.play(FadeIn(rows[3][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Answer key  ·  5 to 8", GOOD)
        table, rows = self.answer_table(head, ANSWERS_B, 5)

        n = self.narrate(
            id="answers_05",
            text="Five: the speed is multiplied by six fifths, so the time by five sixths: the saving is one sixth of the "
                 "usual time, and ten times six is sixty minutes.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "saving")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "sixty")
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_06",
            text="Six: two hundred and forty over S, minus two hundred and forty over S plus twenty, is one; so S times S "
                 "plus twenty is four thousand eight hundred, and S is sixty kilometres per hour.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "minus")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "sixty")
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_07",
            text="Seven: the two conditions give three over S plus three equal to two over S minus two, so S is twelve "
                 "kilometres per hour, and the distance is forty kilometres.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "conditions")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "forty")
        self.play(FadeIn(rows[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_08",
            text="Eight: the last two thirds of the usual time stretches to four-thirds of itself. The extra, two ninths "
                 "of the usual time, is forty minutes, so the usual time is one hundred and eighty minutes, three hours.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "stretches")
        self.play(FadeIn(rows[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "eighty")
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
            text="Recognise and move. The recognition cue: of his usual speed, late, early, or would have taken less; it "
                 "is the same distance, so time is the inverse of speed.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "cue")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "inverse")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_lens_02",
            text="The target time: thirty seconds, or forty seconds for late and early.",
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
            text="The sanity check: the slower trip must take longer; recompute both trip times from your distance, and "
                 "confirm the stated late and early minutes.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "sanity")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "recompute")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S15_exam_lens")

    # ============================================== 16. QUICK REVISION AND SUMMARY ==========

    def summary(self):
        self.scene_start("S16_summary", title="Quick Revision and Summary")

        head = self.heading("Quick revision")
        inv = pill("same distance:   time is the inverse of speed", GOOD, size=BODY)
        delay = pill("at a/b of the usual speed:    delay = (b − a)/a of the usual time", WORD, size=LABEL)
        gap = fit_width(pill("late + early:   add the minutes, convert to hours;    D = s × f × gap ÷ (f − s)", RATIO, size=LABEL), SAFE_W - 0.4)
        bar = text("the download: the bandwidth ratio predicts the delay", LABEL, MUTED)
        nxt = self.breadcrumb("Next", "Video 3 · Relative Speed: Meeting & Chasing")
        self.stack(head, [inv, delay, gap, bar, nxt], buff=0.6, top=0.7)

        n = self.narrate(
            id="summary_01",
            text="Over the same distance, time is the inverse of speed.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "inverse")
        self.play(FadeIn(inv, scale=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_02",
            text="At a over b of the usual speed, the delay is b minus a, over a, of the usual time.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "delay")
        self.play(FadeIn(delay, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_03",
            text="Late at one speed and early at another: add the minutes, convert to hours, and the distance is slow "
                 "times fast times the gap, divided by the difference of the speeds.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "add")
        self.play(FadeIn(gap, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_04",
            text="Remember the download bar.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "download")
        self.play(FadeIn(bar, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_05",
            text="Next: relative speed: meeting and chasing.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Next")
        self.play(FadeIn(nxt, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S16_summary")

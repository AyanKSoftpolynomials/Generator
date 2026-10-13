"""
animation.py for the LMS video generator.

Course : Pre-C-CAT - Section A - Quantitative Aptitude
Video  : Lesson 19 - Time & Distance - 06 - Races & Circular Tracks

Source script:
  C:\\Scripts\\Section A\\Aptitude\\Sessions 13-18 - Pipes, Time Distance, Partnership\\Lesson 19 - Time & Distance\\06 - Races & Circular Tracks.pdf

Built on the golden-reference pattern:
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``;
  * layouts stacked with next_to and guarded with ``no_overlap``; nothing is
    ever animated onto or into another box.

Lesson 19, Video 6 of 7. Not the first video of the lesson: a silent breadcrumb, a one-line recap of Video 5, then today's topic. No spoken course welcome.
The narration follows the script section by section. The eight concept steps are split over two screens. The six exam patterns are shown as two-line blocks.
Practice question 4 in the PDF text has lost its fraction ("A runs 1 ? times as fast as B"); the answer key (A : B = 4 : 3) fixes it as 1 1/3 times. Practice question 5 refers back to question 2, so the track and speeds are repeated on screen.
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


def chain(length, ab, bc):
    """A beats B by ab and B beats C by bc over ``length``: by how much does A beat C?"""
    c_run = Fraction(length - ab) * Fraction(length - bc, length)
    return length - c_run


# ---- the hook: 100 m, 10 m and 10 m ----
assert chain(100, 10, 10) == 19 and Fraction(9, 10) * 90 == 81

# ---- second worked example: 600 m track, 5 and 3 m/s ----
assert Fraction(600, 5 + 3) == 75 and Fraction(600, 5 - 3) == 300 and (600 // 5, 600 // 3) == (120, 200) and lcm(120, 200) == 600

# ---- exam patterns, traps, checkpoint, practice (answers computed) ----
assert Fraction(1000, 950) == Fraction(20, 19) and Fraction(50, 10) == 5 and 1000 // 5 == 200 and 200 - 10 == 190
assert 200 * Fraction(4, 5) == 160 and 200 - 160 == 40 and chain(500, 20, 25) == 44 and Fraction(480 * 475, 500) == 456
assert Fraction(400, 6 + 4) == 40 and lcm(40, 60, 90) == 360 and chain(1000, 100, 100) == 190
assert Fraction(100, 80) == Fraction(5, 4) and Fraction(500, 7 + 3) == 50 and Fraction(20, 5) == 4 and 500 // 4 - 5 == 120
assert Fraction(4, 3) == 1 + Fraction(1, 3) and 200 * Fraction(3, 4) == 150 and Fraction(500, 7 - 3) == 125
assert chain(400, 40, 20) == 58 and Fraction(360 * 380, 400) == 342 and lcm(2, 3, 4) == 12 and 12 // 2 == 6
assert Fraction(180, 162) == Fraction(10, 9) and 200 - 200 * Fraction(9, 10) == 20

OBJECTIVES = [("Turn “beats by x metres”, “beats by t seconds” and “gives a start”", "into speed ratios"),
              ("Combine two race results into a third", "and find the start needed for a dead heat"),
              ("Find the first meeting on a circular track", "and the first meeting at the starting point")]
STEPS_A = [("Same time, so distance ratio = speed ratio", "race of length L, A beats B by x m:  A runs L while B runs L − x,  so A : B = L : (L − x)"),
           ("Beats by seconds:  B finishes t seconds after A", "if both “x m” and “t s” are given, B covers the last x m in t s:  B's speed = x/t"),
           ("Giving a start:  “A gives B a start of x m”", "B starts x m ahead and runs only L − x"),
           ("Dead heat:  both reach the line together", "the start needed = the distance A would otherwise win by;    B runs L × (B's speed ÷ A's speed)")]
STEPS_B = [("Three runners:  chain the ratios", "A : C = (A : B) × (B : C);    never add the margins"),
           ("Circular track, opposite directions", "starting together from one point, they first meet after  track length ÷ (sum of speeds)"),
           ("Circular track, same direction", "the faster must gain one full lap:  track length ÷ (difference of speeds)"),
           ("First meeting at the starting point", "each must complete a whole number of laps:  the LCM of their lap times")]
FORMULAS = ["A beats B by x m in a race of L:       A : B  =  L : (L − x)",
            "Beats by x m or t s:       B's speed  =  x/t",
            "Three runners:       A : C  =  (A : B) × (B : C)",
            "Circular track of length C:     opposite  C ÷ (sum of speeds);      same direction  C ÷ (difference of speeds)",
            "Together at the start again:       LCM of the lap times"]
PATTERNS = [("Beats by metres", "1 km race;   A beats B by 50 m", "1,000 : 950", "speeds 20 : 19"),
            ("Beats by seconds", "1 km;   A beats B by 50 m or 10 s", "B's speed = 5 m/s;   B's time 200 s", "A's time 190 s"),
            ("Start for a dead heat", "200 m;   A at 5 m/s, B at 4 m/s", "B runs 200 × 4/5 = 160", "40 m start"),
            ("Three runners", "500 m;   A beats B by 20 m, B beats C by 25 m", "C runs 480 × 475/500 = 456", "A beats C by 44 m"),
            ("Opposite on a track", "400 m track;   6 and 4 m/s", "400 ÷ 10", "40 s"),
            ("Back at the start", "lap times 40 s, 60 s and 90 s", "LCM", "360 s  =  6 min")]
TRAPS = [("Trap 1  ·  margins added", "A beats B by 10 m and B beats C by 10 m in 100 m races.  A beats C by?",
          "20 m", "19 m",
          "When A finishes, B has run only 90 m, so C trails B by 9 m.  Multiply the ratios."),
         ("Trap 2  ·  speeds added on a same-direction track", "600 m track, 5 m/s and 3 m/s, same direction.  First meeting?",
          "600 ÷ 8  =  75 s", "600 ÷ 2  =  300 s",
          "The same direction needs a full lap of gain, at the difference of the speeds."),
         ("Trap 3  ·  “first meeting” confused with “at the starting point”",
          "600 m track, 5 and 3 m/s, opposite directions.  When are they first together at the start?",
          "75 s  (the first meeting)", "600 s  =  LCM(120, 200)",
          "At the starting point, each runner must have completed whole laps.")]
PRACTICE_A = [("L1", "In a 100 m race, A beats B by 20 m.  Find the ratio of their speeds."),
              ("L1", "A and B start together on a 500 m circular track, in opposite directions, at 7 and 3 m/s.  When do they first meet?"),
              ("L2", "In a 500 m race, A beats B by 20 m or by 5 seconds.  Find A's time."),
              ("L2", "A runs 1 1/3 times as fast as B.  In a 200 m race, what start must A give B for a dead heat?"),
              ("L2", "The runners of question 2 (500 m track, 7 and 3 m/s) run in the same direction.  When do they first meet?")]
PRACTICE_B = [("L3", "In a 400 m race, A beats B by 40 m, and B beats C by 20 m.  By how much does A beat C?"),
              ("L3", "Three cyclists lap a track in 2, 3 and 4 min, starting together.  Together at the start when?  Laps of the fastest?"),
              ("L3", "In a 200 m race, A beats B by 20 m and beats C by 38 m.  By how much would B beat C in a 200 m race?")]
ANSWERS_A = [("100 : 80", "5 : 4"),
             ("500 ÷ (7 + 3)", "50 s"),
             ("B's last 20 m in 5 s:  4 m/s;   B's time 500 ÷ 4 = 125 s", "125 − 5  =  120 s"),
             ("A : B = 4 : 3;    when A runs 200 m, B runs 150 m", "50 m start")]
ANSWERS_B = [("500 ÷ (7 − 3)", "125 s"),
             ("A runs 400, B runs 360;    C runs 360 × 380/400 = 342", "58 m"),
             ("LCM(2, 3, 4) = 12 minutes;     12 ÷ 2", "12 min,  6 laps"),
             ("A 200, B 180, C 162:   B : C = 10 : 9;   B runs 200, C 180", "20 m")]
LENS = [("Recognition cue", "“beats by”, “start”, “dead heat”:  distances in the same time;    “circular track”, “laps”:  relative speed or LCM"),
        ("Target time", "40 seconds"),
        ("Sanity check", "in a chain A beats B beats C, A's margin over C is a little less than the sum of the two margins")]


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


class RacesAndCircularTracksVideo(LMSScene):
    lesson_title = "Races & Circular Tracks"

    def construct(self):
        self.camera.background_color = BG

        self.intro()
        self.hook()
        self.objectives()
        self.why_this_matters()
        self.race_language()
        self.chains_and_tracks()
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

        crumb = self.breadcrumb("Quantitative Aptitude", "Lesson 19 · Time & Distance", "Video 6 of 7")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        recap = VGroup(text("last video", SMALL, MUTED), pill("downstream  u + v;    upstream  u − v", WORD, size=LABEL)).arrange(DOWN, buff=0.25)
        title = fit_width(text("Races & Circular Tracks", TITLE, INK, BOLD), SAFE_W - 0.4)
        today = text("today: ratio and relative speed, in race language", LABEL, FOCUS)
        block = VGroup(recap, title, today).arrange(DOWN, buff=0.7)
        fit_within(block, SAFE_W, SAFE_H - crumb.height - 0.9)
        block.next_to(crumb, DOWN, buff=0.7)
        self.no_overlap(crumb, recap, title, today)
        self.validator.check_in_frame(VGroup(crumb, block))

        n = self.narrate(
            id="intro_01",
            text="In the last video, downstream added the stream speed and upstream subtracted it.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.at_word(n, "downstream")
        self.play(FadeIn(recap, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="intro_02",
            text="Today: races and circular tracks, which are ratio and relative-speed questions in race language.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "races")
        self.play(FadeIn(title, shift=UP * 0.1))
        self.at_word(n, "language")
        self.play(FadeIn(today, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_intro")

    # ============================================== 1. HOOK ==========

    def hook(self):
        self.scene_start("S01_hook", title="Hook")

        head = self.heading("A 100 m sprint")
        races = VGroup(pill("heat 1:  A beats B by 10 m", WORD, size=BODY), pill("heat 2:  B beats C by 10 m", WORD, size=BODY)).arrange(RIGHT, buff=0.6)
        ask = pill("A against C:   by how much will A win?", FOCUS, size=BODY)
        guess = text("almost everyone says 20 m", LABEL, BAD, BOLD)
        real = text("the answer is 19 m: the missing metre is the key to every race question", LABEL, INK, BOLD)
        self.stack(head, [races, ask, guess, real], buff=0.75, top=0.9)
        self.no_overlap(*races)

        n = self.narrate(
            id="hook_01",
            text="At a company sports day, A beats B by ten metres in a one hundred metre sprint.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "beats")
        self.play(FadeIn(races[0], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_02",
            text="In the next heat, B beats C by ten metres over the same one hundred metres.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "beats")
        self.play(FadeIn(races[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_03",
            text="If A and C race each other, by how much will A win?",
            voice="default",
            subtitle=True,
            pause_after=3.0,
        )
        self.at_word(n, "win")
        self.play(FadeIn(ask, scale=1.03))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="hook_04",
            text="Almost everyone says twenty metres. The answer is nineteen metres, and the missing metre is the key to "
                 "every race question.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "twenty")
        self.play(FadeIn(guess, shift=UP * 0.1))
        self.at_word(n, "nineteen")
        self.play(FadeIn(real, shift=UP * 0.1))
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
            text="First, turn beats by x metres, beats by t seconds and gives a start into speed ratios.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "turn")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "ratios")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="objectives_03",
            text="Second, combine two race results into a third, and find the start needed for a dead heat.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "combine")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "heat")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="objectives_04",
            text="Third, find the first meeting on a circular track, and the first meeting at the starting point.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "circular")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "starting")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_objectives")

    # ============================================== 3. WHY THIS MATTERS ==========

    def why_this_matters(self):
        self.scene_start("S03_why_this_matters", title="Why This Matters")

        head = self.heading("Why this matters")
        look = text("races and circular tracks look like special topics", LABEL, MUTED)
        really = pill("they are ratio and relative-speed questions in disguise", WORD, size=LABEL)
        two = text("translate the race language, and each one takes two lines", LABEL, INK, BOLD)
        self.stack(head, [look, really, two], buff=0.9, top=1.1)

        n = self.narrate(
            id="why_this_matters_01",
            text="Races and circular tracks look like special topics, but they are ratio and relative-speed questions in "
                 "disguise.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "special")
        self.play(FadeIn(look, shift=UP * 0.1))
        self.at_word(n, "disguise")
        self.play(FadeIn(really, scale=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="why_this_matters_02",
            text="Once you translate the race language, each one takes two lines.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "translate")
        self.play(FadeIn(two, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_why_this_matters")

    # ============================================== 4. CONCEPT - RACE LANGUAGE ==========

    def race_language(self):
        self.scene_start("S04_race_language", title="Concept - Race Language")

        head = self.heading("Race language")
        conv = text("constant speeds;   “A beats B by x m”:  when A finishes, B is still x m short of the line", SMALL, MUTED)
        blocks = two_line_blocks(STEPS_A, WORD)
        self.stack(head, [conv] + list(blocks), buff=0.42, top=0.55, align=LEFT)

        n = self.narrate(
            id="race_language_01",
            text="Runners keep constant speeds, and A beats B by x metres means that when A finishes, B is still x metres "
                 "short of the line.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "constant")
        self.play(FadeIn(conv, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="race_language_02",
            text="They run for the same time, so the distance ratio is the speed ratio. In a race of length L, when A "
                 "beats B by x metres, A runs L while B runs L minus x, so A to B is L to L minus x.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "ratio")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "minus")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="race_language_03",
            text="Beats by seconds: A beats B by t seconds means B finishes t seconds after A. If both the metres and the "
                 "seconds are given, B covers the last x metres in t seconds, so B's speed is x over t.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "seconds")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "last")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="race_language_04",
            text="Giving a start: A gives B a start of x metres means B starts x metres ahead, and runs only L minus x.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "start")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "ahead")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="race_language_05",
            text="A dead heat: both reach the line together. The start that produces a dead heat equals the distance A "
                 "would otherwise beat B by, so B must run L times B's speed over A's speed.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "heat")
        self.play(FadeIn(blocks[3][0], shift=RIGHT * 0.2))
        self.at_word(n, "equals")
        self.play(FadeIn(blocks[3][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_race_language")

    # ============================================== 5. CONCEPT - THREE RUNNERS, AND CIRCULAR TRACKS ==========

    def chains_and_tracks(self):
        self.scene_start("S05_chains_and_tracks", title="Concept - Three Runners, and Circular Tracks")

        head = self.heading("Three runners, and circular tracks")
        blocks = two_line_blocks(STEPS_B, WORD)
        self.stack(head, list(blocks), buff=0.5, top=0.7, align=LEFT)

        n = self.narrate(
            id="chains_and_tracks_01",
            text="Three runners: chain the ratios. A to C is A to B, times B to C. Never add the margins.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "chain")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "times")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.at_word(n, "Never")
        self.play(Indicate(blocks[0][1], color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="chains_and_tracks_02",
            text="On a circular track in opposite directions, starting together from one point, they first meet after the "
                 "track length divided by the sum of the speeds.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "opposite")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "divided")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="chains_and_tracks_03",
            text="In the same direction, the faster must gain one full lap: the track length divided by the difference of "
                 "the speeds.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "same")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "lap")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="chains_and_tracks_04",
            text="For the first meeting at the starting point, each must complete a whole number of laps: the L C M of "
                 "their lap times.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "starting")
        self.play(FadeIn(blocks[3][0], shift=RIGHT * 0.2))
        self.at_word(n, "whole")
        self.play(FadeIn(blocks[3][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_chains_and_tracks")

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
            text="Here is the formula box. A beats B by x metres in a race of L: A to B is L to L minus x.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "box")
        self.play(FadeIn(box[0]))
        self.at_word(n, "beats")
        self.play(FadeIn(lines[0], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_box_02",
            text="Beats by x metres or t seconds: B's speed is x over t.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "seconds")
        self.play(FadeIn(lines[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_box_03",
            text="Three runners: A to C is A to B times B to C.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "times")
        self.play(FadeIn(lines[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_box_04",
            text="On a circular track: opposite directions, the length over the sum of the speeds; the same direction, the "
                 "length over the difference.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "circular")
        self.play(FadeIn(lines[3], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_box_05",
            text="And together at the start again: the L C M of the lap times.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "start")
        self.play(FadeIn(lines[4], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_formula_box")

    # ============================================== 7. THE ANALOGY - THE HANDS OF A CLOCK ==========

    def analogy(self):
        self.scene_start("S07_analogy", title="The Analogy - The Hands of a Clock")

        head = self.heading("The hands of a clock")
        hands = pill("the minute hand catches the hour hand only after gaining a full circle", WORD, size=LABEL)
        gain = text("it gains at the difference of their speeds", LABEL, INK, BOLD)
        same = pill("two runners going the same way round a track behave like those hands", FOCUS, size=LABEL)
        later = text("you will meet the clock version later in the module", LABEL, MUTED)
        stops = VGroup(text("Where the analogy stops", LABEL, BAD, BOLD),
                       text("clock hands always move the same way", LABEL, INK),
                       text("on a track, runners may go in opposite directions: then their speeds add", LABEL, MUTED)).arrange(DOWN, buff=0.2)
        self.stack(head, [hands, gain, same, later, stops], buff=0.45, top=0.6)

        n = self.narrate(
            id="analogy_01",
            text="On a clock, the minute hand catches the hour hand again only after gaining a full circle on it, at the "
                 "difference of their speeds.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "clock")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "catches")
        self.play(FadeIn(hands, shift=UP * 0.1))
        self.at_word(n, "difference")
        self.play(FadeIn(gain, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_02",
            text="Two runners going the same way round a track behave exactly like those hands.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "runners")
        self.play(FadeIn(same, scale=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_03",
            text="You will meet the clock version later in the module.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "later")
        self.play(FadeIn(later, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_04",
            text="Where the analogy stops: clock hands always move the same way. On a track, runners may go in opposite "
                 "directions, and then their speeds add.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "stops")
        self.play(FadeIn(stops[0], shift=UP * 0.1))
        self.at_word(n, "always")
        self.play(FadeIn(stops[1], shift=UP * 0.1))
        self.at_word(n, "opposite")
        self.play(FadeIn(stops[2], shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S07_analogy")

    # ============================================== 8. WORKED EXAMPLE - CLOSING THE HOOK ==========

    def hook_solved(self):
        self.scene_start("S08_hook_solved", title="Worked Example - Closing the Hook")

        head = self.heading("A beats B by 10 m;   B beats C by 10 m")
        steps = self.solve_steps([("A : B = 100 : 90", "B : C = 100 : 90"),
                                  ("When A finishes 100 m:    B has run", "90 m"),
                                  ("C has run 9/10 of B's distance:    9/10 × 90", "=  81 m"),
                                  ("A beats C by    100 − 81", "=  19 m")])
        self.stack(head, [steps], top=1.0)
        self.no_overlap(*steps)

        n = self.narrate(
            id="hook_solved_01",
            text="A to B is one hundred to ninety, and B to C is one hundred to ninety.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "ninety")
        self.play(FadeIn(steps[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "ninety", occurrence=2)
        self.play(FadeIn(steps[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_solved_02",
            text="When A finishes one hundred metres, B has run ninety metres, and C has run nine tenths of B's distance: "
                 "eighty-one metres.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "finishes")
        self.play(FadeIn(steps[1], shift=RIGHT * 0.2))
        self.at_word(n, "tenths")
        self.play(FadeIn(steps[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "eighty-one")
        self.play(FadeIn(steps[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_solved_03",
            text="A beats C by one hundred minus eighty-one: nineteen metres.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "minus")
        self.play(FadeIn(steps[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "nineteen")
        self.play(FadeIn(steps[3][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S08_hook_solved")

    # ============================================== 9. A SECOND WORKED EXAMPLE - A CIRCULAR TRACK ==========

    def second_example(self):
        self.scene_start("S09_second_example", title="A Second Worked Example - A Circular Track")

        head = self.heading("A circular track")
        ask = text("A and B start together on a 600 m track at 5 m/s and 3 m/s:   first meeting, each direction?   together at the start?",
                   LABEL, MUTED)
        fit_width(ask, SAFE_W - 0.6)
        steps = self.solve_steps([("Opposite directions:    600 ÷ (5 + 3)", "=  75 s"),
                                  ("Same direction:    600 ÷ (5 − 3)", "=  300 s"),
                                  ("Lap times:    600 ÷ 5 = 120 s,      600 ÷ 3 = 200 s", "LCM = 600 s  =  10 min")])
        self.stack(head, [ask, steps], buff=0.8, top=0.8)
        self.no_overlap(*steps)

        n = self.narrate(
            id="second_example_01",
            text="A and B start together from the same point of a six hundred metre circular track, at five metres per "
                 "second and three metres per second. When do they first meet in opposite directions, and in the same "
                 "direction? And when are they first together at the starting point?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "start")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "circular")
        self.play(FadeIn(ask, shift=UP * 0.1))
        self.at_word(n, "meet")
        self.play(Indicate(ask, color=FOCUS, scale_factor=1.03))
        self.at_word(n, "starting")
        self.play(Indicate(ask, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_02",
            text="In opposite directions: six hundred divided by five plus three is seventy-five seconds.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "divided")
        self.play(FadeIn(steps[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "seventy-five")
        self.play(FadeIn(steps[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_03",
            text="In the same direction: six hundred divided by five minus three is three hundred seconds.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "divided")
        self.play(FadeIn(steps[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "hundred", occurrence=2)
        self.play(FadeIn(steps[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_04",
            text="The lap times are one hundred and twenty seconds and two hundred seconds, and their L C M is six hundred "
                 "seconds: ten minutes.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "lap")
        self.play(FadeIn(steps[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "ten")
        self.play(FadeIn(steps[2][2], shift=LEFT * 0.1))
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
            text="Beats by metres: a one kilometre race, and A beats B by fifty metres. One thousand to nine hundred and "
                 "fifty: the speeds are twenty to nineteen.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "metres")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "thousand")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_03",
            text="Beats by seconds: one kilometre, and A beats B by fifty metres or ten seconds. B's speed is five metres "
                 "per second and B's time two hundred seconds: A's time is one hundred and ninety seconds.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "seconds")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "speed")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_04",
            text="The start for a dead heat: two hundred metres, with A at five metres per second and B at four. B runs "
                 "two hundred times four fifths, one hundred and sixty: a forty metre start.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "heat")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "runs")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Exam patterns  ·  4 to 6 of 6")
        blocks = self.pattern_blocks(PATTERNS[3:6])
        self.stack(head, list(blocks), buff=0.6, top=0.8, align=LEFT)

        n = self.narrate(
            id="exam_patterns_05",
            text="Three runners: five hundred metres; A beats B by twenty metres, and B beats C by twenty-five. C runs "
                 "four hundred and eighty times four seventy-five over five hundred, four hundred and fifty-six: A beats C "
                 "by forty-four metres.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "runners")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "runs")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_06",
            text="Opposite on a track: a four hundred metre track, at six and four metres per second. Four hundred divided "
                 "by ten: forty seconds.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "track")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "divided")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_07",
            text="Back at the start: lap times of forty, sixty and ninety seconds. Their L C M is three hundred and sixty "
                 "seconds: six minutes.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "start")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "Their")
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
            text="Trap one: margins added. A beats B by ten metres and B beats C by ten metres, in one hundred metre "
                 "races: by how much does A beat C?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "added")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "beats")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_02",
            text="The wrong instinct says twenty metres. The correct answer is nineteen metres.",
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
            text="The rule: B's ten metre lead over C applies over one hundred metres; when A finishes, B has run only "
                 "ninety. Multiply the ratios.",
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
            text="Trap two: speeds added on a same-direction track. A six hundred metre track, five and three metres per "
                 "second, same direction: when is the first meeting?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "added")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "hundred")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_05",
            text="The wrong instinct divides six hundred by eight: seventy-five seconds. The correct answer is six hundred "
                 "divided by two: three hundred seconds.",
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
            text="The rule: the same direction needs a full lap of gain, at the difference of the speeds.",
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
            text="Trap three: the first meeting confused with meeting at the starting point. A six hundred metre track, "
                 "five and three metres per second, opposite directions: when are they first together at the starting "
                 "point?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "confused")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "opposite")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_08",
            text="The wrong instinct says seventy-five seconds, the first meeting. The correct answer is six hundred "
                 "seconds, the L C M of the lap times.",
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
            text="The rule: at the starting point, each runner must have completed whole laps.",
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
        given = pill("1 km race:   A beats B by 100 m,   B beats C by 100 m.    A beats C by?", FOCUS, size=LABEL)
        work = VGroup(text("when A finishes:    B has run 900 m,    C has run 900 × 9/10 = 810 m", LABEL, INK, BOLD),
                      text("A beats C by 190 m", BODY, GOOD, BOLD)).arrange(DOWN, buff=0.4)
        self.stack(head, [given, work], buff=0.9, top=1.0)
        self.no_overlap(*work)

        n = self.narrate(
            id="checkpoint_01",
            text="Your turn. In a one kilometre race, A beats B by one hundred metres, and B beats C by one hundred "
                 "metres. By how much does A beat C?",
            voice="default",
            subtitle=True,
            pause_after=10.0,
        )
        self.at_word(n, "turn")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "race")
        self.play(FadeIn(given, scale=1.03))
        self.at_word(n, "much")
        self.play(Indicate(given, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="checkpoint_02",
            text="When A finishes, B has run nine hundred metres and C eight hundred and ten. A beats C by one hundred and "
                 "ninety metres.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "finishes")
        self.play(FadeIn(work[0], shift=UP * 0.1))
        self.at_word(n, "ninety")
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
            text="Level one, question one: in a one hundred metre race, A beats B by twenty metres; find the ratio of "
                 "their speeds. Question two: A and B start together from the same point of a five hundred metre circular "
                 "track, running in opposite directions at seven and three metres per second; when do they first meet?",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "ratio")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "circular")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="practice_02",
            text="Level two, question three: in a five hundred metre race, A beats B by twenty metres or by five seconds; "
                 "find A's time. Question four: A runs one and a third times as fast as B; in a two hundred metre race, "
                 "what start must A give B for a dead heat? Question five: in question two, when would A and B first meet "
                 "if they ran in the same direction?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "seconds")
        self.play(FadeIn(rows[2], shift=RIGHT * 0.2))
        self.at_word(n, "heat")
        self.play(FadeIn(rows[3], shift=RIGHT * 0.2))
        self.at_word(n, "same")
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
            text="Level three, question six: in a four hundred metre race, A beats B by forty metres, and B beats C by "
                 "twenty metres; by how much does A beat C? Question seven: three cyclists complete one lap of a circular "
                 "track in two, three and four minutes; they start together from the same point in the same direction; "
                 "when are they first together again at the starting point, and how many laps has the fastest completed by "
                 "then? Question eight: in a two hundred metre race, A beats B by twenty metres and beats C by "
                 "thirty-eight metres; by how much would B beat C in a two hundred metre race?",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "forty")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "cyclists")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.at_word(n, "thirty-eight")
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
            text="One: one hundred to eighty is five to four.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "eighty")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "five")
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_02",
            text="Two: five hundred divided by seven plus three is fifty seconds.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "divided")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "fifty")
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_03",
            text="Three: B covers the last twenty metres in five seconds, so B's speed is four metres per second and B's "
                 "time is one hundred and twenty-five seconds. A's time is five seconds less: one hundred and twenty "
                 "seconds.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "last")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "less")
        self.play(FadeIn(rows[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_04",
            text="Four: A to B is four to three, so when A runs two hundred metres, B runs one hundred and fifty: A gives "
                 "B a fifty metre start.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "three")
        self.play(FadeIn(rows[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "gives")
        self.play(FadeIn(rows[3][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Answer key  ·  5 to 8", GOOD)
        table, rows = self.answer_table(head, ANSWERS_B, 5)

        n = self.narrate(
            id="answers_05",
            text="Five: five hundred divided by seven minus three is one hundred and twenty-five seconds.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "divided")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "twenty-five")
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_06",
            text="Six: when A runs four hundred, B runs three hundred and sixty; B to C is four hundred to three hundred "
                 "and eighty, so C runs three hundred and forty-two, and A beats C by fifty-eight metres.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "runs")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "fifty-eight")
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_07",
            text="Seven: the L C M of two, three and four is twelve minutes, and the fastest has completed twelve divided "
                 "by two: six laps.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "twelve")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "laps")
        self.play(FadeIn(rows[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_08",
            text="Eight: when A runs two hundred, B runs one hundred and eighty and C one hundred and sixty-two, so B to C "
                 "is ten to nine. When B runs two hundred, C runs one hundred and eighty: B beats C by twenty metres.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "runs")
        self.play(FadeIn(rows[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "beats")
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
            text="Recognise and move. The recognition cue: beats by, start or dead heat means distances in the same time; "
                 "circular track or laps means relative speed or the L C M.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "cue")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "distances")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_lens_02",
            text="The target time: forty seconds.",
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
            text="The sanity check: in a chain where A beats B and B beats C, A's margin over C is a little less than the "
                 "sum of the two margins.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "sanity")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "little")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S15_exam_lens")

    # ============================================== 16. QUICK REVISION AND SUMMARY ==========

    def summary(self):
        self.scene_start("S16_summary", title="Quick Revision and Summary")

        head = self.heading("Quick revision")
        race = pill("same time:   distances are in the ratio of the speeds;     A : B = L : (L − x)", GOOD, size=LABEL)
        links = pill("three runners:   chain the ratios, never add the margins", WORD, size=LABEL)
        track = VGroup(pill("first meeting:  track ÷ (sum or difference of speeds)", RATIO, size=SMALL),
                       pill("at the starting point:  LCM of the lap times", RATIO, size=SMALL)).arrange(RIGHT, buff=0.4)
        fit_width(track, SAFE_W - 0.4)
        clock = text("the clock hands: the faster one must gain a full circle", LABEL, MUTED)
        nxt = self.breadcrumb("Next", "Video 7 · Speed Tricks for Time & Distance")
        self.stack(head, [race, links, track, clock, nxt], buff=0.6, top=0.7)
        self.no_overlap(*track)

        n = self.narrate(
            id="summary_01",
            text="In a race, distances run in the same time are in the ratio of the speeds: A to B is L to L minus x.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "ratio")
        self.play(FadeIn(race, scale=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_02",
            text="Chain the ratios for three runners; never add the margins.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Chain")
        self.play(FadeIn(links, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_03",
            text="On a circular track, divide the track length by the sum or difference of the speeds for the first "
                 "meeting, and use the L C M of the lap times for the starting point.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "divide")
        self.play(FadeIn(track[0], shift=UP * 0.1))
        self.at_word(n, "starting")
        self.play(FadeIn(track[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_04",
            text="Remember the clock hands.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "clock")
        self.play(FadeIn(clock, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_05",
            text="Next: speed tricks for time and distance.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Next")
        self.play(FadeIn(nxt, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S16_summary")

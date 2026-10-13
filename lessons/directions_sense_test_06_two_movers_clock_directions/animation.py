"""
animation.py for the LMS video generator.

Course : Pre-C-CAT - Section A - Logical Reasoning
Video  : Lesson 3 - Directions Sense Test - 06 - Two Movers & Clock Directions

Source script:
  C:\\Scripts\\Section A\\Reasoning_Scripts\\Sessions 1-4 - Coding-Decoding, Alphabets, Directions, Number Series, Odd Man Out\\Lesson 3 - Directions Sense Test\\06 - Two Movers & Clock Directions.pdf

Built on the golden-reference pattern:
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``;
  * layouts stacked with next_to and guarded with ``no_overlap``; nothing is
    ever animated onto or into another box.

Lesson 3, Video 5 of 6 (file 06 in its folder).
Not the first video: a silent breadcrumb, a one-line recap of Video 4, then today's topic.
The narration follows the script section by section and ends with the Section Quiz and its answer key.
Two movers are drawn to scale from one origin (A blue, B orange) with a dashed green line for the gap; clocks are drawn flat,
seen from above, with N, E, S and W marked around them (hour hand orange, minute hand blue).
Long quiz questions are written compactly on screen and read in full.
Every gap, direction and clock-hand angle in the script was recomputed in the data block; all of them are correct.
Pauses: 3 seconds on the hook question, 10 seconds on the checkpoint, 12 seconds on each practice and quiz screen.
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

import math as _math

POINTS = ["north", "north-east", "east", "south-east", "south", "south-west", "west", "north-west"]
STEP = {"N": (0, 1), "E": (1, 0), "S": (0, -1), "W": (-1, 0)}


def end_of(*legs):
    """End point of legs (distance, "N" / "E" / "S" / "W") from the origin."""
    x = sum(d * STEP[way][0] for d, way in legs)
    y = sum(d * STEP[way][1] for d, way in legs)
    return x, y


def apart(a, b):
    """(gap, where a is with respect to b)."""
    dx, dy = a[0] - b[0], a[1] - b[1]
    name = ("north" if dy > 0 else "south" if dy < 0 else "") + ("-" if dx and dy else "") + ("east" if dx > 0 else "west" if dx < 0 else "")
    return _math.hypot(dx, dy), name


def hour_hand(hour, minute):
    return 30 * (hour % 12) + 0.5 * minute


def minute_hand(minute):
    return 6 * minute


def points_to(angle_from_12, twelve_faces="north"):
    """Compass direction of a clock hand when the 12 mark faces the given direction."""
    total = (angle_from_12 + POINTS.index(twelve_faces) * 45) % 360
    assert total % 45 == 0, total
    return POINTS[int(total // 45)]


# ---- hook, worked examples ----
assert apart(end_of((6, "N")), end_of((8, "E"))) == (10, "north-west") and end_of((6, "N")) == (0, 6) and end_of((8, "E")) == (8, 0)
assert hour_hand(1, 30) == 45 and points_to(hour_hand(1, 30), "north-east") == "east" and minute_hand(0) == 0
# ---- concept steps, exam patterns ----
assert points_to(30 * 3) == "east" and points_to(30 * 6) == "south" and points_to(30 * 9) == "west"
assert apart(end_of((5, "E")), end_of((7, "W")))[0] == 12 and apart(end_of((10, "N")), end_of((4, "N")))[0] == 6
A_LEGS, B_LEGS = [(4, "N"), (3, "E")], [(2, "S"), (3, "E")]
assert end_of(*A_LEGS) == (3, 4) and end_of(*B_LEGS) == (3, -2) and apart(end_of(*A_LEGS), end_of(*B_LEGS)) == (6, "north")
assert end_of((3, "N"), (4, "W")) == (-4, 3) and end_of((3, "S"), (4, "E")) == (4, -3)
assert apart((-4, 3), (4, -3)) == (10, "north-west")
assert hour_hand(4, 30) == 135 and points_to(135) == "south-east" and points_to(hour_hand(3, 0), "south") == "west"
# ---- practice ----
assert points_to(hour_hand(9, 0)) == "west" and minute_hand(45) == 270 and points_to(270) == "west"
assert hour_hand(7, 30) == 225 and points_to(225) == "south-west"
assert hour_hand(10, 30) == 315 and points_to(315, "east") == "north-east" and (315 + 90) % 360 == 45
# ---- section quiz ----
assert apart(end_of((9, "E")), end_of((12, "N")))[0] == 15 and apart(end_of((7, "N")), end_of((3, "S")))[0] == 10
assert points_to(hour_hand(3, 0), "west") == "north" and (90 - 90) % 360 == 0
assert end_of((6, "N"), (4, "E")) == (4, 6) and end_of((2, "S"), (4, "E")) == (4, -2) and apart((4, 6), (4, -2)) == (8, "north")

OBJECTIVES = [("Find the distance and direction between two people", "who move from the same start"),
              ("Handle movers", "with several legs each"),
              ("Solve clock-based direction questions", "including clocks placed at an angle")]
FORMULAS = ["Two movers:   same origin,  track each end point",
            "Opposite:  add        same direction:  subtract        perpendicular:  Pythagoras",
            "Clock flat, 12 north:   each hour mark = 30°;    3 E,   6 S,   9 W",
            "Hour hand  =  30h + 0.5m;        minute hand  =  6m        (degrees from 12)",
            "Rotated clock:   add the rotation of the 12 mark"]
PATTERNS_A = [["Perpendicular", "6 km N and 8 km E from one point", "Pythagoras", "10 km"],
              ["Opposite", "5 km E and 7 km W", "add", "12 km"],
              ["Same direction", "10 km N and 4 km N", "subtract", "6 km"],
              ["Several legs each", "A:  4 N then 3 E;     B:  2 S then 3 E", "A (3, 4),  B (3, −2)", "6 km;  A is north of B"]]
PATTERNS_B = [["Mirror paths", "A:  3 N, 4 W;     B:  3 S, 4 E", "A (−4, 3),  B (4, −3)", "10 km;  A is north-west of B"],
              ["Standard clock", "hour hand at 4:30,  12 facing north", "135°", "south-east"],
              ["Rotated clock", "12 faces north-east;  hour hand at 1:30", "45° + 45°", "east"],
              ["Rotated clock", "minute hand points south at 3:00;  hour hand?", "90° + 180°", "west"]]
TRAPS = [("Trap 1  ·  adding the two paths",
          "A walks 4 km N then 3 km E;  B walks 2 km S then 3 km E, from the same point.   How far apart?",
          "4 + 3 + 2 + 3  =  12 km", "A (3, 4),  B (3, −2):   6 km",
          "compare end points, never path lengths"),
         ("Trap 2  ·  the hour hand exactly on the hour mark", "With 12 facing north, where does the hour hand point at 4:30?",
          "on the 4, at 120°:  not a direction", "120° + 15°  =  135°:  south-east",
          "always add 0.5° × minutes to the hour hand")]
PRACTICE_A = [("L1", "From one point, A walks 6 km north and B walks 8 km east.  How far apart are they?"),
              ("L1", "From one point, A walks 10 km north and B walks 4 km north.  How far apart are they?"),
              ("L1", "A clock lies flat with 12 facing north.  In which direction does the hour hand point at 9:00?"),
              ("L2", "From one point, A walks 4 km north then 3 km east;  B walks 2 km south then 3 km east.  "
                     "How far apart, and where is A with respect to B?"),
              ("L2", "A clock lies flat with 12 facing north.  In which direction does the minute hand point at 4:45?"),
              ("L2", "A clock lies flat with 12 facing north.  In which direction does the hour hand point at 7:30?")]
PRACTICE_B = [("L3", "From one point, A walks 3 km north and 4 km west;  B walks 3 km south and 4 km east.  "
                     "How far apart, and where is A with respect to B?"),
              ("L3", "A clock is placed so that at 12 noon its minute hand points east.  In which direction does its hour hand point at 10:30?")]
ANSWERS_A = [("√(36 + 64)", "10 km"),
             ("10 − 4", "6 km"),
             ("9 × 30°  =  270°", "west"),
             ("A (3, 4),   B (3, −2)", "6 km;  A is north of B")]
ANSWERS_B = [("45 × 6°  =  270°", "west"),
             ("210° + 15°  =  225°", "south-west"),
             ("A (−4, 3),   B (4, −3):    √(64 + 36)", "10 km;  A is north-west of B"),
             ("rotation +90°;   hour hand 300° + 15° = 315°;   315° + 90° = 405°  →  45°", "north-east")]
LENS = [("Recognition cue", "two people from one point;  “how far apart”;  a clock with a stated hand direction"),
        ("Target time", "30 seconds"),
        ("Sanity check", "the gap between two movers can never exceed the sum of their path lengths")]
QUIZ = [["From one point, A walks 9 km east and B walks 12 km north.   How far apart are they?", "(a) 21 km   (b) 15 km   (c) 3 km   (d) 225 km"],
        ["From one point, A walks 7 km north and B walks 3 km south.   How far apart are they?", "(a) 10 km   (b) 4 km   (c) √58 km   (d) 21 km"],
        ["A clock lies flat with 12 facing north.   Which way does the hour hand point at 4:30?",
         "(a) South   (b) South-west   (c) East   (d) South-east"],
        ["At 12 noon a clock's minute hand points west.   Which way does its hour hand point at 3:00?",
         "(a) South   (b) East   (c) North   (d) West"],
        ["A:  6 km N then 4 km E;    B:  2 km S then 4 km E  (same start).   How far apart, and where is A from B?",
         "(a) 8 km, N   (b) 16 km, N   (c) 8 km, S   (d) 4 km, N"]]
QUIZ_KEY = [("the 9-12-15 triple", "(b)  15 km"),
            ("opposite directions:  add", "(a)  10 km"),
            ("120° + 15°  =  135°", "(d)  South-east"),
            ("rotation −90°:    90° − 90°  =  0°", "(c)  North"),
            ("A (4, 6),   B (4, −2)", "(a)  8 km;  A is north of B")]


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


class TwoMoversAndClockDirectionsVideo(LMSScene):
    lesson_title = "Two Movers & Clock Directions"

    def construct(self):
        self.camera.background_color = BG

        self.intro()
        self.hook()
        self.objectives()
        self.why_this_section()
        self.concept_journey()
        self.rule_box()
        self.short_trick()
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
        self.section_quiz()

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

    def table_under(self, head, ref, header, rows, widths, size=SMALL):
        """A reference block under ``head`` and a table under it, fitted to the space that is left.  Returns (table, body rows)."""
        fit_width(ref, SAFE_W)
        ref.next_to(head, DOWN, buff=0.35)
        table = self.table_rows(header, rows, widths, size=size)
        fit_within(table, SAFE_W, ref.get_bottom()[1] + FRAME_H / 2 - SAFE - 1.2)
        table.next_to(ref, DOWN, buff=0.4)
        self.no_overlap(head, ref, table)
        self.no_overlap(*table)
        self.validator.check_in_frame(VGroup(head, ref, table))
        return table, table[1:]
    def step_rows(self, items, color=WORD):
        """Numbered concept steps.  Each row = (number chip, the step[, a short note in green])."""
        rows = VGroup()
        for i, (what, note) in enumerate(items):
            row = VGroup(pill(str(i + 1), color, size=SMALL), text(what, LABEL, INK, BOLD))
            if note:
                row.add(text(note, LABEL, GOOD, BOLD))
            rows.add(row.arrange(RIGHT, buff=0.35))
        return fit_width(rows.arrange(DOWN, buff=0.5, aligned_edge=LEFT), SAFE_W - 0.6)

    def two_paths(self, first, second, names=("A", "B"), box=(4.2, 3.0)):
        """Two paths from one origin, drawn to the same scale, north at the top.  Each path = [(east, north), ...].
        Returns (origin dot, first path, second path, end dots, end labels, dashed gap (a group), north mark)."""
        def track(legs):
            pts = [np.zeros(3)]
            for east, north in legs:
                pts.append(pts[-1] + np.array([float(east), float(north), 0.0]))
            return pts
        one, two = track(first), track(second)
        xs, ys = [p[0] for p in one + two], [p[1] for p in one + two]
        k = min(box[0] / max(max(xs) - min(xs), 1e-6), box[1] / max(max(ys) - min(ys), 1e-6), 1.0)
        paths = VGroup()
        for pts, color in ((one, WORD), (two, RATIO)):
            paths.add(VGroup(*[Arrow(a * k, b * k, buff=0, color=color, stroke_width=5, max_tip_length_to_length_ratio=0.12)
                               for a, b in zip(pts, pts[1:])]))
        ends = VGroup(Dot(one[-1] * k, color=WORD, radius=0.1), Dot(two[-1] * k, color=RATIO, radius=0.1))
        mid = (one[-1] + two[-1]) * k / 3
        labels = VGroup()
        for name, p, dot, color in zip(names, (one[-1], two[-1]), ends, (WORD, RATIO)):
            away = p * k - mid
            corner = np.array([1.0 if away[0] >= -1e-6 else -1.0, 1.0 if away[1] >= -1e-6 else -1.0, 0.0])
            labels.add(text(f"{name} ({p[0]:g}, {p[1]:g})".replace("-", "−"), SMALL, color, BOLD).next_to(dot, corner, buff=0.08))
        gap = VGroup(DashedLine(one[-1] * k, two[-1] * k, color=GOOD, stroke_width=4))
        origin = Dot(ORIGIN, color=FOCUS, radius=0.1)
        north = VGroup(Arrow(ORIGIN, UP * 0.6, buff=0, color=MUTED, stroke_width=3), text("N", SMALL, MUTED, BOLD)).arrange(UP, buff=0.05)
        north.next_to(VGroup(paths, labels), LEFT, buff=0.5, aligned_edge=UP)
        self.no_overlap(*labels, gap=0.02)
        return VGroup(origin, paths[0], paths[1], ends, labels, gap, north)

    def clock(self, hour, minute, turn=0, radius=1.45):
        """A clock lying flat, seen from above, with its 12 mark turned ``turn`` degrees clockwise from north.
        Returns (ring, numbers, hour hand, minute hand, the N / E / S / W marks)."""
        def unit(deg):
            return np.array([math.sin(deg * DEGREES), math.cos(deg * DEGREES), 0.0])
        ring = Circle(radius=radius, color=MUTED, stroke_width=3)
        numbers = VGroup(*[text(str(n), MIN_FONT, FOCUS if n == 12 else INK, BOLD).move_to(unit(n * 30 + turn) * radius * 0.82) for n in range(1, 13)])
        hour_line = Line(ORIGIN, unit(30 * (hour % 12) + 0.5 * minute + turn) * radius * 0.42, color=RATIO, stroke_width=9)
        minute_line = Line(ORIGIN, unit(6 * minute + turn) * radius * 0.6, color=WORD, stroke_width=5)
        marks = VGroup(*[text(s, LABEL, GOOD, BOLD).move_to(unit(d) * (radius + 0.42)) for s, d in (("N", 0), ("E", 90), ("S", 180), ("W", 270))])
        self.no_overlap(*numbers, gap=0.02)
        return VGroup(ring, numbers, hour_line, minute_line, marks)

    # ============================================== 0. INTRO ==========
    # Not the first video: silent breadcrumb, a one-line recap of the previous video, then today's topic.

    def intro(self):
        self.scene_start("S00_intro", title="Intro")

        crumb = self.breadcrumb("Logical Reasoning", "Lesson 3 · Directions Sense Test", "Video 5 of 6")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        recap = VGroup(text("from Video 4  ·  Relative Position & Coded Directions", SMALL, MUTED), pill("origin at a shared point;   subtract coordinates", WORD, size=LABEL)).arrange(DOWN, buff=0.25)
        title = fit_width(text("Two Movers & Clock Directions", TITLE, INK, BOLD), SAFE_W - 0.4)
        today = text("today: two end points, and clock hands", LABEL, FOCUS)
        block = VGroup(recap, title, today).arrange(DOWN, buff=0.7)
        fit_within(block, SAFE_W, SAFE_H - crumb.height - 0.9)
        block.next_to(crumb, DOWN, buff=0.7)
        self.no_overlap(crumb, recap, title, today)
        self.validator.check_in_frame(VGroup(crumb, block))

        n = self.narrate(
            id="intro_01",
            text="In the last video, every point got coordinates from a shared origin, and one subtraction gave the "
                 "direction and the distance.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.at_word(n, "coordinates")
        self.play(FadeIn(recap[0]))
        self.at_word(n, "subtraction")
        self.play(FadeIn(recap[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="intro_02",
            text="This video covers two movers and clock directions: two end points, and clock hands.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "covers")
        self.play(FadeIn(title, shift=UP * 0.1))
        self.at_word(n, "hands")
        self.play(FadeIn(today, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_intro")

    # ============================================== 1. HOOK ==========

    def hook(self):
        self.scene_start("S01_hook", title="Hook")

        head = self.heading("Two riders, one hub")
        ride = self.two_paths([(0, 6)], [(8, 0)], names=("rider 1", "rider 2"))
        ask = text("one rides 6 km north, the other 8 km east:\nhow far apart are they now?", LABEL, FOCUS, BOLD)
        answer = pill("(0, 6) and (8, 0):   one Pythagoras step,  10 km", GOOD, size=LABEL)
        moral = text("two movers:  track two points instead of one;\nthe method does not change", SMALL, RATIO, BOLD)
        side = VGroup(ask, answer, moral).arrange(DOWN, buff=0.7)
        row = VGroup(ride, side).arrange(RIGHT, buff=0.7)
        self.stack(head, [row], top=0.9)
        self.no_overlap(ride, side)

        n = self.narrate(
            id="hook_01",
            text="Two delivery riders leave the same hub. One rides six kilometres north, the other eight kilometres east. "
                 "How far apart are they now?",
            voice="default",
            subtitle=True,
            pause_after=3.0,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "hub")
        self.play(FadeIn(ride[0]), FadeIn(ride[6], shift=UP * 0.1))
        self.at_word(n, "north")
        self.play(GrowArrow(ride[1][0]), FadeIn(ride[3][0]))
        self.at_word(n, "east")
        self.play(GrowArrow(ride[2][0]), FadeIn(ride[3][1]))
        self.at_word(n, "far")
        self.play(FadeIn(ask, shift=UP * 0.1))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="hook_02",
            text="Neither rider's path matters on its own. Give each end point coordinates, zero, six and eight, zero, and "
                 "the gap is one Pythagoras step: ten kilometres.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "path")
        self.play(Indicate(ask, color=FOCUS, scale_factor=1.03))
        self.at_word(n, "coordinates")
        self.play(FadeIn(ride[4]))
        self.at_word(n, "gap")
        self.play(Create(ride[5][0]), FadeIn(answer))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_03",
            text="With two movers, you track two points instead of one; the method does not change.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "track")
        self.play(FadeIn(moral, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S01_hook")

    # ============================================== 2. OBJECTIVES ==========

    def objectives(self):
        self.scene_start("S02_objectives", title="Objectives")

        head = self.heading("By the end of this video")
        blocks = two_line_blocks(OBJECTIVES, WORD)
        self.stack(head, list(blocks), buff=0.6, top=0.8, align=LEFT)

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
            text="One: find the distance and direction between two people who move from the same start.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "distance")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "same")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="objectives_03",
            text="Two: handle movers with several legs each.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "handle")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "several")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="objectives_04",
            text="Three: solve clock-based direction questions, including clocks placed at an angle.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "solve")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "angle")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_objectives")

    # ============================================== 3. WHY THIS SECTION ==========

    def why_this_section(self):
        self.scene_start("S03_why_this_section", title="Why This Section")

        head = self.heading("Why this section")
        twist = pill("two-mover and clock questions add one twist to the direction toolkit", WORD, size=LABEL)
        same = text("the same coordinates and rotations solve both", BODY, GOOD, BOLD)
        self.stack(head, [twist, same], buff=1.2, top=1.5)

        n = self.narrate(
            id="why_this_section_01",
            text="Two-mover and clock questions add one twist to the direction toolkit.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "twist")
        self.play(FadeIn(twist, scale=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="why_this_section_02",
            text="The same coordinates and rotations solve both.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "solve")
        self.play(FadeIn(same, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_why_this_section")

    # ============================================== 4. THE CONCEPT JOURNEY ==========

    def concept_journey(self):
        self.scene_start("S04_concept_journey", title="The Concept Journey")

        head = self.heading("Steps 1 to 4  ·  one origin, two paths")
        ride = self.two_paths([(0, 4), (3, 0)], [(0, -2), (3, 0)], box=(3.0, 3.4))
        steps = VGroup(
            VGroup(pill("one origin, two paths", WORD, size=LABEL), text("common start at (0, 0);  track each person's net movement separately", SMALL, INK, BOLD))
            .arrange(DOWN, buff=0.16, aligned_edge=LEFT),
            VGroup(pill("distance between them", GOOD, size=LABEL), text("subtract one end point from the other, then Pythagoras", SMALL, INK, BOLD))
            .arrange(DOWN, buff=0.16, aligned_edge=LEFT),
            VGroup(pill("special cases", RATIO, size=LABEL), text("opposite:  add     same direction:  subtract     perpendicular:  Pythagoras", SMALL, INK, BOLD))
            .arrange(DOWN, buff=0.16, aligned_edge=LEFT),
            VGroup(pill("direction between them", SECOND, size=LABEL), text("“where is A with respect to B”  =  A's position minus B's, by its signs", SMALL, INK, BOLD))
            .arrange(DOWN, buff=0.16, aligned_edge=LEFT)).arrange(DOWN, buff=0.38, aligned_edge=LEFT)
        row = VGroup(ride, steps).arrange(RIGHT, buff=0.5)
        self.stack(head, [row], top=0.6)
        self.no_overlap(ride, steps)

        n = self.narrate(
            id="concept_journey_01",
            text="Step one: one origin, two paths. Put the common start at zero, zero, and track each person's net "
                 "east-west and north-south movement separately.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "one")
        self.play(FadeIn(steps[0][0], shift=UP * 0.1))
        self.at_word(n, "start")
        self.play(FadeIn(ride[0]), FadeIn(ride[6], shift=UP * 0.1), FadeIn(steps[0][1], shift=UP * 0.1))
        self.at_word(n, "track")
        self.play(FadeIn(ride[1]), FadeIn(ride[2], shift=UP * 0.1), FadeIn(ride[3], shift=UP * 0.1), FadeIn(ride[4], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_journey_02",
            text="Step two: the distance between them. Subtract one end point from the other, then apply Pythagoras.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "two")
        self.play(FadeIn(steps[1][0], shift=UP * 0.1))
        self.at_word(n, "Subtract")
        self.play(FadeIn(steps[1][1], shift=UP * 0.1), Create(ride[5][0]))
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_journey_03",
            text="Step three: special cases. In opposite directions, add the distances. In the same direction, subtract. "
                 "If perpendicular, use Pythagoras.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "three")
        self.play(FadeIn(steps[2][0], shift=UP * 0.1))
        self.at_word(n, "opposite")
        self.play(FadeIn(steps[2][1], shift=UP * 0.1))
        self.at_word(n, "same")
        self.play(Indicate(steps[2][1], color=FOCUS, scale_factor=1.03))
        self.at_word(n, "perpendicular")
        self.play(Indicate(steps[2][0], color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_journey_04",
            text="Step four: the direction between them. Where is A with respect to B means A's position minus B's, read "
                 "by its signs.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "four")
        self.play(FadeIn(steps[3][0], shift=UP * 0.1))
        self.at_word(n, "means")
        self.play(FadeIn(steps[3][1], shift=UP * 0.1), Indicate(ride[4], color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Step 5  ·  clock hands as directions")
        face = self.clock(3, 0)
        facts = VGroup(text("the clock lies flat, with 12 pointing north", LABEL, INK), pill("each hour mark  =  30° clockwise", FOCUS, size=LABEL),
                       text("3 is east,   6 is south,   9 is west", LABEL, GOOD, BOLD),
                       VGroup(text("hour hand angle  =  30 × hour + 0.5 × minutes", SMALL, RATIO, BOLD), text("minute hand angle  =  6 × minutes", SMALL, WORD, BOLD))
                       .arrange(DOWN, buff=0.16, aligned_edge=LEFT)).arrange(DOWN, buff=0.5)
        row = VGroup(face, facts).arrange(RIGHT, buff=0.9)
        self.stack(head, [row], top=0.9)
        self.no_overlap(face, facts)

        n = self.narrate(
            id="concept_journey_05",
            text="Step five: clock hands as directions. With the clock flat and twelve pointing north, each hour mark is "
                 "thirty degrees clockwise.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "five")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "flat")
        self.play(FadeIn(face[0]), FadeIn(face[1], shift=UP * 0.1), FadeIn(face[4], shift=UP * 0.1), FadeIn(facts[0], shift=UP * 0.1))
        self.at_word(n, "mark")
        self.play(FadeIn(facts[1], scale=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_journey_06",
            text="Three is east, six is south, and nine is west.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Three")
        self.play(face[1][2].animate.set_color(FOCUS), FadeIn(facts[2], shift=UP * 0.1))
        self.at_word(n, "six")
        self.play(face[1][5].animate.set_color(FOCUS))
        self.at_word(n, "nine")
        self.play(face[1][8].animate.set_color(FOCUS))
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_journey_07",
            text="The hour hand angle is thirty times the hour, plus half a degree per minute; the minute hand angle is "
                 "six times the minutes.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "hour")
        self.play(FadeIn(face[2]), FadeIn(facts[3][0], shift=UP * 0.1))
        self.at_word(n, "minute", occurrence=2)
        self.play(FadeIn(face[3]), FadeIn(facts[3][1], shift=UP * 0.1))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Step 6  ·  rotated clocks")
        face = self.clock(3, 0, turn=45)
        facts = VGroup(text("12 points north-east instead of north", LABEL, INK), pill("every hand direction rotates by the same 45°", FOCUS, size=LABEL),
                       text("find the hand's normal angle, then add the rotation", LABEL, GOOD, BOLD),
                       text("exactly as with renamed directions", SMALL, MUTED)).arrange(DOWN, buff=0.55)
        row = VGroup(face, facts).arrange(RIGHT, buff=0.9)
        self.stack(head, [row], top=0.9)
        self.no_overlap(face, facts)

        n = self.narrate(
            id="concept_journey_08",
            text="Step six: rotated clocks. If twelve points north-east instead of north, every hand direction rotates by "
                 "the same forty-five degrees.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "six")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "north-east")
        self.play(FadeIn(face), FadeIn(facts[0], shift=UP * 0.1))
        self.at_word(n, "rotates")
        self.play(FadeIn(facts[1], scale=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_journey_09",
            text="Find the hand's normal angle, then add the rotation, as with renamed directions.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "normal")
        self.play(FadeIn(facts[2], shift=UP * 0.1))
        self.at_word(n, "renamed")
        self.play(FadeIn(facts[3], shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_concept_journey")

    # ============================================== 5. RULE BOX ==========

    def rule_box(self):
        self.scene_start("S05_rule_box", title="Rule Box")

        head = self.heading("Rule box", GOOD)
        lines = VGroup(*[text(f, LABEL, INK) for f in FORMULAS]).arrange(DOWN, buff=0.42, aligned_edge=LEFT)
        fit_width(lines, SAFE_W - 1.6)
        box = self.card(lines, width=SAFE_W - 0.4, color=GOOD, pad=0.5)
        self.stack(head, [box], top=0.8)

        n = self.narrate(
            id="rule_box_01",
            text="Here is the rule box. Two movers: the same origin, and track each end point.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "box")
        self.play(FadeIn(box[0]))
        self.at_word(n, "movers")
        self.play(FadeIn(lines[0], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="rule_box_02",
            text="Opposite directions, add; the same direction, subtract; perpendicular, Pythagoras.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "add")
        self.play(FadeIn(lines[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="rule_box_03",
            text="With the clock flat and twelve north, each hour mark is thirty degrees: three is east, six south, nine "
                 "west.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "mark")
        self.play(FadeIn(lines[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="rule_box_04",
            text="The hour hand is thirty h plus half m; the minute hand is six m, in degrees from twelve.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "hand")
        self.play(FadeIn(lines[3], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="rule_box_05",
            text="For a rotated clock, add the rotation of the twelve mark.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "rotated")
        self.play(FadeIn(lines[4], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_rule_box")

    # ============================================== 6. SHORT TRICK ==========

    def short_trick(self):
        self.scene_start("S06_short_trick", title="Short Trick")

        head = self.heading("Short trick", RATIO)
        movers = VGroup(pill("two movers", WORD, size=LABEL), text("compare end points, never path lengths", BODY, INK, BOLD)).arrange(RIGHT, buff=0.5)
        clocks = VGroup(pill("clocks", RATIO, size=LABEL), text("hand angle from 12:   hour 30h + 0.5m,   minute 6m", LABEL, INK, BOLD),
                        text("plus the rotation of the 12 mark", SMALL, GOOD, BOLD))
        clocks[1].next_to(clocks[0], RIGHT, buff=0.5)
        clocks[2].next_to(clocks[1], DOWN, buff=0.2, aligned_edge=LEFT)
        self.stack(head, [movers, clocks], buff=1.2, top=1.3, align=LEFT)
        self.no_overlap(*movers)
        self.no_overlap(*clocks)

        n = self.narrate(
            id="short_trick_01",
            text="The short trick. Two movers: compare end points, never path lengths.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "movers")
        self.play(FadeIn(movers[0], shift=UP * 0.1))
        self.at_word(n, "compare")
        self.play(FadeIn(movers[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="short_trick_02",
            text="Clocks: take the hand angle from twelve, then add the rotation of the twelve mark.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "angle")
        self.play(FadeIn(clocks[:2], shift=UP * 0.1))
        self.at_word(n, "rotation")
        self.play(FadeIn(clocks[2], shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_short_trick")

    # ============================================== 7. THE ANALOGY - TWO PINS ON A MAP ==========

    def analogy(self):
        self.scene_start("S07_analogy", title="The Analogy - Two Pins on a Map")

        head = self.heading("Two pins on a map app")
        ride = self.two_paths([(0, 6)], [(8, 0)], names=("pin 1", "pin 2"), box=(3.6, 2.7))
        shows = text("a map app shows two pins and the straight-line distance\nbetween them, however each pin got there", SMALL, INK)
        stops = VGroup(text("where the analogy stops", SMALL, BAD, BOLD), text("map apps use the Earth's curvature", SMALL, INK),
                       text("exam distances are on flat ground", SMALL, GOOD, BOLD)).arrange(DOWN, buff=0.14, aligned_edge=LEFT)
        side = VGroup(shows, stops).arrange(DOWN, buff=0.8)
        row = VGroup(ride, side).arrange(RIGHT, buff=0.8)
        self.stack(head, [row], top=1.0)
        self.no_overlap(ride, side)

        n = self.narrate(
            id="analogy_01",
            text="A map app shows two pins and the straight-line distance between them, however each pin got there.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "pins")
        self.play(FadeIn(ride[3]), FadeIn(ride[4], shift=UP * 0.1), FadeIn(ride[6], shift=UP * 0.1))
        self.at_word(n, "distance")
        self.play(Create(ride[5][0]), FadeIn(shows))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_02",
            text="Two-mover questions ask for exactly that number.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "exactly")
        self.play(Indicate(ride[5], color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_03",
            text="Where the analogy stops: map apps use the Earth's curvature. Exam distances are on flat ground.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "stops")
        self.play(FadeIn(stops[0], shift=RIGHT * 0.2))
        self.at_word(n, "curvature")
        self.play(FadeIn(stops[1], shift=RIGHT * 0.2))
        self.at_word(n, "flat")
        self.play(FadeIn(stops[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S07_analogy")

    # ============================================== 8. WORKED EXAMPLE - CLOSING THE HOOK ==========

    def hook_solved(self):
        self.scene_start("S08_hook_solved", title="Worked Example - Closing the Hook")

        head = self.heading("Worked example: closing the hook")
        ride = self.two_paths([(0, 6)], [(8, 0)], names=("rider 1", "rider 2"))
        steps = self.solve_steps([("rider 1 ends at", "(0, 6)"), ("rider 2 ends at", "(8, 0)"), ("distance  =  √(8² + 6²)", "10 km"),
                                  ("rider 1 is", "north-west of rider 2")])
        row = VGroup(ride, steps).arrange(RIGHT, buff=0.8)
        self.stack(head, [row], top=1.1)
        self.no_overlap(ride, steps)
        self.no_overlap(*steps)

        n = self.narrate(
            id="hook_solved_01",
            text="Rider one ends at zero, six; rider two ends at eight, zero.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "one")
        self.play(FadeIn(ride[0]), FadeIn(ride[1], shift=UP * 0.1), FadeIn(ride[3][0], shift=UP * 0.1), FadeIn(ride[4][0], shift=UP * 0.1), FadeIn(ride[6], shift=UP * 0.1), FadeIn(steps[0], shift=RIGHT * 0.2))
        self.at_word(n, "two")
        self.play(FadeIn(ride[2]), FadeIn(ride[3][1], shift=UP * 0.1), FadeIn(ride[4][1], shift=UP * 0.1), FadeIn(steps[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_solved_02",
            text="The distance is the square root of eight squared plus six squared: ten kilometres.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "root")
        self.play(Create(ride[5][0]), FadeIn(steps[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_solved_03",
            text="And rider one is north-west of rider two.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "north-west")
        self.play(FadeIn(steps[3], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S08_hook_solved")

    # ============================================== 9. A SECOND WORKED EXAMPLE - A ROTATED CLOCK ==========

    def second_example(self):
        self.scene_start("S09_second_example", title="A Second Worked Example - A Rotated Clock")

        head = self.heading("A second worked example: a rotated clock")
        ask = text("A clock lies flat so that at 12 noon its minute hand points north-east.  Where does its hour hand point at 1:30 pm?", SMALL, INK)
        face = self.clock(1, 30, turn=45, radius=1.35)
        steps = self.solve_steps([("at noon the minute hand is on 12, so 12 faces north-east", "rotation +45°"),
                                  ("at 1:30 the hour hand is  30 × 1 + 0.5 × 30", "45° from 12"),
                                  ("45° + 45°  =  90°", "east")])
        row = VGroup(face, steps).arrange(RIGHT, buff=0.6)
        self.stack(head, [ask, row], buff=0.5, top=0.5)
        self.no_overlap(face, steps)
        self.no_overlap(*steps)

        n = self.narrate(
            id="second_example_01",
            text="A clock lies flat so that at twelve noon its minute hand points north-east. In which direction does its "
                 "hour hand point at one thirty?",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "clock")
        self.play(FadeIn(ask, shift=UP * 0.1))
        self.at_word(n, "noon")
        self.play(FadeIn(face[0]), FadeIn(face[1], shift=UP * 0.1), FadeIn(face[4], shift=UP * 0.1))
        self.at_word(n, "direction")
        self.play(Indicate(ask, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_02",
            text="Step one: at noon the minute hand points at twelve, so the twelve mark faces north-east: a rotation of "
                 "plus forty-five degrees.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "mark")
        self.play(face[1][11].animate.set_color(FOCUS), FadeIn(steps[0], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_03",
            text="Step two: at one thirty, the hour hand is thirty times one, plus half of thirty: forty-five degrees from "
                 "twelve.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "hand")
        self.play(FadeIn(face[2]), FadeIn(face[3], shift=UP * 0.1), FadeIn(steps[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_04",
            text="Step three: forty-five plus forty-five is ninety degrees, which is east.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "plus")
        self.play(FadeIn(steps[2], shift=RIGHT * 0.2), face[4][1].animate.set_color(FOCUS))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S09_second_example")

    # ============================================== 10. EXAM PATTERNS - HOW THIS IS ASKED ==========

    def exam_patterns(self):
        self.scene_start("S10_exam_patterns", title="Exam Patterns - How This Is Asked")

        head = self.heading("Exam patterns  ·  part 1")
        table, rows = self.placed_table(head, ["Pattern", "Example", "Method", "Answer"], PATTERNS_A, [2.6, 4.9, 2.9, 2.9], room=1.2)
        for row in rows:
            row[0].set_color(WORD)
            row[3].set_color(GOOD)

        n = self.narrate(
            id="exam_patterns_01",
            text="Exams ask this in eight ways.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "eight")
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_02",
            text="Perpendicular: six kilometres north and eight east from one point. Use Pythagoras: ten kilometres.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Perpendicular")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "Pythagoras")
        self.play(FadeIn(rows[0][2], shift=RIGHT * 0.2), FadeIn(rows[0][3], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_03",
            text="Opposite: five east and seven west. Add: twelve kilometres.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Opposite")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "Add")
        self.play(FadeIn(rows[1][2], shift=RIGHT * 0.2), FadeIn(rows[1][3], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_04",
            text="Same direction: ten north and four north. Subtract: six kilometres.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Same")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "Subtract")
        self.play(FadeIn(rows[2][2], shift=RIGHT * 0.2), FadeIn(rows[2][3], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_05",
            text="Several legs each: A goes four north then three east; B goes two south then three east. A is at three, "
                 "four and B at three, minus two, so they are six kilometres apart, and A is north of B.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "legs")
        self.play(FadeIn(rows[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "minus")
        self.play(FadeIn(rows[3][2], shift=RIGHT * 0.2))
        self.at_word(n, "apart")
        self.play(FadeIn(rows[3][3], shift=LEFT * 0.1))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Exam patterns  ·  part 2")
        table, rows = self.placed_table(head, ["Pattern", "Example", "Method", "Answer"], PATTERNS_B, [2.6, 4.9, 2.9, 2.9], room=1.2)
        for row in rows:
            row[0].set_color(WORD)
            row[3].set_color(GOOD)

        n = self.narrate(
            id="exam_patterns_06",
            text="Mirror paths: A is at minus four, three and B at four, minus three: ten kilometres, and A is north-west "
                 "of B.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "Mirror")
        self.play(FadeIn(rows[0][:3], shift=RIGHT * 0.2))
        self.at_word(n, "ten")
        self.play(FadeIn(rows[0][3], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_07",
            text="A standard clock: the hour hand at four thirty, with twelve facing north, is at one hundred and "
                 "thirty-five degrees: south-east.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "standard")
        self.play(FadeIn(rows[1][:3], shift=RIGHT * 0.2))
        self.at_word(n, "south-east")
        self.play(FadeIn(rows[1][3], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_08",
            text="A rotated clock: twelve faces north-east, and the hour hand at one thirty gives forty-five plus "
                 "forty-five: east.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "rotated")
        self.play(FadeIn(rows[2][:3], shift=RIGHT * 0.2))
        self.at_word(n, "east")
        self.play(FadeIn(rows[2][3], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_09",
            text="Another rotated clock: the minute hand points south at three o'clock, so the hour hand is at ninety plus "
                 "one hundred and eighty: west.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Another")
        self.play(FadeIn(rows[3][:3], shift=RIGHT * 0.2))
        self.at_word(n, "west")
        self.play(FadeIn(rows[3][3], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S10_exam_patterns")

    # ============================================== 11. TRAPS AND CONFUSING QUESTIONS ==========

    def traps(self):
        self.scene_start("S11_traps", title="Traps and Confusing Questions")

        head, ask, wrong, right, rule = self.show_trap(TRAPS[0])

        n = self.narrate(
            id="traps_01",
            text="Trap one: adding the two paths.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "adding")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_02",
            text="A walks four kilometres north then three east; B walks two south then three east, from the same point. "
                 "How far apart are they?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "walks")
        self.play(FadeIn(ask, shift=UP * 0.1))
        self.at_word(n, "far")
        self.play(Indicate(ask, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_03",
            text="The wrong instinct: four plus three plus two plus three, twelve kilometres.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "instinct")
        self.play(FadeIn(wrong, shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_04",
            text="Correct: A is at three, four and B at three, minus two, so they are six kilometres apart.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "minus")
        self.play(FadeIn(right, shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_05",
            text="The rule: compare end points, never path lengths.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "compare")
        self.play(FadeIn(rule, scale=1.03))
        self.wait_for_narration(n)
        self.clear_stage()

        head, ask, wrong, right, rule = self.show_trap(TRAPS[1])

        n = self.narrate(
            id="traps_06",
            text="Trap two: the hour hand exactly on the hour mark.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "exactly")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_07",
            text="With twelve facing north, where does the hour hand point at four thirty?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "where")
        self.play(FadeIn(ask, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_08",
            text="The wrong instinct: the hour hand sits on the four, at one hundred and twenty degrees, which is not one "
                 "of the eight directions.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "instinct")
        self.play(FadeIn(wrong, shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_09",
            text="Correct: the hour hand moves half a degree per minute, so one hundred and twenty plus fifteen is one "
                 "hundred and thirty-five: south-east.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "moves")
        self.play(FadeIn(right, shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_10",
            text="The rule: always add half a degree times the minutes to the hour hand.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "always")
        self.play(FadeIn(rule, scale=1.03))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S11_traps")

    # ============================================== 12. CHECKPOINT ==========

    def checkpoint(self):
        self.scene_start("S12_checkpoint", title="Checkpoint")

        head = self.heading("Checkpoint  ·  your turn")
        ask = text("From one point, A walks 5 km east and B walks 7 km west.   How far apart are they?", LABEL, FOCUS, BOLD)
        ride = self.two_paths([(5, 0)], [(-7, 0)], box=(7.0, 1.0))
        work = text("opposite directions:  add        5 + 7", BODY, INK, BOLD)
        answer = pill("12 km", GOOD, size=BODY)
        self.stack(head, [ask, ride, work, answer], buff=0.8, top=0.7)

        n = self.narrate(
            id="checkpoint_01",
            text="Your turn. From one point, A walks five kilometres east and B walks seven kilometres west. How far apart "
                 "are they?",
            voice="default",
            subtitle=True,
            pause_after=10.0,
        )
        self.at_word(n, "turn")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "point")
        self.play(FadeIn(ask, shift=UP * 0.1))
        self.at_word(n, "far")
        self.play(Indicate(ask, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="checkpoint_02",
            text="They walk in opposite directions, so add: five plus seven is twelve kilometres.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "opposite")
        self.play(FadeIn(ride[:5]), FadeIn(ride[6], shift=UP * 0.1))
        self.at_word(n, "add")
        self.play(FadeIn(work, shift=UP * 0.1))
        self.at_word(n, "twelve")
        self.play(Create(ride[5][0]), FadeIn(answer))
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
            text="Level one, question one: from one point, A walks six kilometres north and B walks eight east; how far "
                 "apart are they? Question two: A walks ten kilometres north and B walks four north; how far apart? "
                 "Question three: a clock lies flat with twelve facing north; in which direction does the hour hand point "
                 "at nine o'clock?",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "six")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "ten")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.at_word(n, "clock")
        self.play(FadeIn(rows[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="practice_02",
            text="Level two, question four: from one point, A walks four kilometres north then three east, and B walks two "
                 "south then three east; how far apart are they, and where is A with respect to B? Question five: with "
                 "twelve facing north, in which direction does the minute hand point at four forty-five? Question six: and "
                 "the hour hand at seven thirty?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "four")
        self.play(FadeIn(rows[3], shift=RIGHT * 0.2))
        self.at_word(n, "five")
        self.play(FadeIn(rows[4], shift=RIGHT * 0.2))
        self.at_word(n, "six")
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
        self.play(Indicate(head, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)
        self.clear_stage()

        head = self.heading("Practice  ·  Level 3")
        table, rows = self.practice_table(head, PRACTICE_B, 7)

        n = self.narrate(
            id="practice_04",
            text="Level three, question seven: from one point, A walks three kilometres north and four west, and B walks "
                 "three south and four east; how far apart are they, and where is A with respect to B? Question eight: a "
                 "clock is placed so that at twelve noon its minute hand points east; in which direction does its hour "
                 "hand point at ten thirty?",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "seven")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "eight")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="practice_05",
            text="Pause again and solve these two.",
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
            text="One: the square root of thirty-six plus sixty-four is ten kilometres.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "root")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "ten")
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_02",
            text="Two: ten minus four is six kilometres.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "minus")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "six")
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_03",
            text="Three: nine times thirty degrees is two hundred and seventy: west.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "times")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "west")
        self.play(FadeIn(rows[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_04",
            text="Four: A is at three, four and B at three, minus two: six kilometres, and A is north of B.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "minus")
        self.play(FadeIn(rows[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "six")
        self.play(FadeIn(rows[3][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Answer key  ·  5 to 8", GOOD)
        table, rows = self.answer_table(head, ANSWERS_B, 5)

        n = self.narrate(
            id="answers_05",
            text="Five: forty-five times six degrees is two hundred and seventy: west.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "times")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "west")
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_06",
            text="Six: two hundred and ten plus fifteen is two hundred and twenty-five: south-west.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "plus")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "south-west")
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_07",
            text="Seven: A is at minus four, three and B at four, minus three: ten kilometres, and A is north-west of B.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "minus")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "ten")
        self.play(FadeIn(rows[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_08",
            text="Eight: the rotation is plus ninety degrees; the hour hand is at three hundred and fifteen; and three "
                 "hundred and fifteen plus ninety reduces to forty-five: north-east.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "rotation")
        self.play(FadeIn(rows[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "north-east")
        self.play(FadeIn(rows[3][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S14_answers")

    # ============================================== 15. EXAM LENS - RECOGNISE AND MOVE ==========

    def exam_lens(self):
        self.scene_start("S15_exam_lens", title="Exam Lens - Recognise and Move")

        head = self.heading("Exam lens: recognise and move", RATIO)
        blocks = two_line_blocks(LENS, RATIO)
        self.stack(head, list(blocks), buff=0.6, top=0.8, align=LEFT)

        n = self.narrate(
            id="exam_lens_01",
            text="Recognise and move. The recognition cue: two people from one point; the words, how far apart; or a clock "
                 "with a stated hand direction.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "cue")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "people")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_lens_02",
            text="The target time: thirty seconds.",
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
            text="The sanity check: the gap between two movers can never exceed the sum of their path lengths.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "sanity")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "never")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S15_exam_lens")

    # ============================================== 16. QUICK REVISION AND SUMMARY ==========

    def summary(self):
        self.scene_start("S16_summary", title="Quick Revision and Summary")

        head = self.heading("Quick revision")
        points = VGroup(text("two movers:  track two end points from one origin, and compare them", LABEL, INK, BOLD),
                        text("clocks:  convert the hand to degrees from 12, then add the rotation of the 12 mark", LABEL, INK, BOLD))\
            .arrange(DOWN, buff=0.55, aligned_edge=LEFT)
        box = VGroup(pill("two end points", GOOD, size=SMALL), pill("add · subtract · Pythagoras", GOOD, size=SMALL), pill("hour = 30h + 0.5m", GOOD, size=SMALL),
                     pill("minute = 6m", GOOD, size=SMALL), pill("add the rotation", GOOD, size=SMALL)).arrange(RIGHT, buff=0.3)
        fit_width(box, SAFE_W - 0.4)
        self.stack(head, [points, box], buff=1.2, top=1.2)
        self.no_overlap(*points)
        self.no_overlap(*box)

        n = self.narrate(
            id="summary_01",
            text="With two movers, track two end points from one origin and compare them.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "track")
        self.play(FadeIn(points[0], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_02",
            text="For clocks, convert the hand to degrees from twelve, then add the rotation of the twelve mark.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "convert")
        self.play(FadeIn(points[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_03",
            text="That is the rule box in one line.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "line")
        self.play(FadeIn(box, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S16_summary")

    # ============================================== 17. SECTION QUIZ ==========

    def section_quiz(self):
        self.scene_start("S17_section_quiz", title="Section Quiz")

        head = self.heading("Section quiz")
        rules = VGroup(pill("5 questions", WORD, size=BODY), pill("4 minutes", WORD, size=BODY), pill("+3 correct", GOOD, size=BODY),
                       pill("−1 wrong", BAD, size=BODY)).arrange(RIGHT, buff=0.4)
        gate = VGroup(VGroup(pill("12 or more out of 15", GOOD, size=LABEL), text("move on", BODY, GOOD, BOLD)).arrange(RIGHT, buff=0.5),
                      VGroup(pill("below 12", BAD, size=LABEL), text("replay the Traps segment, then retry", BODY, INK, BOLD)).arrange(RIGHT, buff=0.5))            .arrange(DOWN, buff=0.6, aligned_edge=LEFT)
        self.stack(head, [rules, gate], buff=1.1, top=1.1)
        self.no_overlap(*rules)
        self.no_overlap(*gate)

        n = self.narrate(
            id="section_quiz_01",
            text="Now the section quiz: five questions in four minutes, with plus three for a correct answer and minus one "
                 "for a wrong one.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "quiz")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "questions")
        self.play(FadeIn(rules[0], shift=UP * 0.1))
        self.at_word(n, "minutes")
        self.play(FadeIn(rules[1], shift=UP * 0.1))
        self.at_word(n, "plus")
        self.play(FadeIn(rules[2], shift=UP * 0.1))
        self.at_word(n, "minus")
        self.play(FadeIn(rules[3], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="section_quiz_02",
            text="Twelve or more out of fifteen: move on. Below twelve: replay the traps segment, then retry.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "move")
        self.play(FadeIn(gate[0], shift=RIGHT * 0.2))
        self.at_word(n, "replay")
        self.play(FadeIn(gate[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Section quiz  ·  questions 1 to 3")
        table, rows = self.placed_table(head, ["#", "Question", "Options"],
                                        [[str(0 + i + 1)] + list(row) for i, row in enumerate(QUIZ[0:3])], [0.8, 7.6, 4.8], room=1.3)
        for row in rows:
            row[0].set_color(MUTED)

        n = self.narrate(
            id="section_quiz_03",
            text="Here are questions one, two and three.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "one")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "two")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.at_word(n, "three")
        self.play(FadeIn(rows[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="section_quiz_04",
            text="Pause the video and solve them.",
            voice="default",
            subtitle=True,
            pause_after=12.0,
        )
        self.at_word(n, "Pause")
        self.play(Indicate(head, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)
        self.clear_stage()

        head = self.heading("Section quiz  ·  questions 4 to 5")
        table, rows = self.placed_table(head, ["#", "Question", "Options"],
                                        [[str(3 + i + 1)] + list(row) for i, row in enumerate(QUIZ[3:5])], [0.8, 7.6, 4.8], room=1.3)
        for row in rows:
            row[0].set_color(MUTED)

        n = self.narrate(
            id="section_quiz_05",
            text="And here are questions four and five.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "four")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "five")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="section_quiz_06",
            text="Pause again and solve them.",
            voice="default",
            subtitle=True,
            pause_after=12.0,
        )
        self.at_word(n, "Pause")
        self.play(Indicate(head, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)
        self.clear_stage()

        head = self.heading("Section quiz  ·  answer key", GOOD)
        table, rows = self.answer_table(head, QUIZ_KEY, 1)
        nxt = self.breadcrumb("Next", "Video 6 · All Tricks Combined")
        nxt.next_to(table, DOWN, buff=0.6)
        self.no_overlap(table, nxt)
        self.validator.check_in_frame(VGroup(head, table, nxt))

        n = self.narrate(
            id="section_quiz_07",
            text="The answers. One: the nine, twelve, fifteen triple: option b.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "triple")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "option")
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="section_quiz_08",
            text="Two: opposite directions, so add: ten kilometres: option a.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "add")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "option")
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="section_quiz_09",
            text="Three: one hundred and twenty plus fifteen is one hundred and thirty-five, south-east: option d.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "plus")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "option")
        self.play(FadeIn(rows[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="section_quiz_10",
            text="Four: the rotation is minus ninety degrees, and ninety minus ninety is zero, north: option c.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "rotation")
        self.play(FadeIn(rows[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "option")
        self.play(FadeIn(rows[3][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="section_quiz_11",
            text="Five: A is at four, six and B at four, minus two: eight kilometres, with A north of B: option a.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "minus")
        self.play(FadeIn(rows[4][:2], shift=RIGHT * 0.2))
        self.at_word(n, "option")
        self.play(FadeIn(rows[4][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="section_quiz_12",
            text="Next: all tricks combined.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Next")
        self.play(FadeIn(nxt, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S17_section_quiz")

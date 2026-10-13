"""
animation.py for the LMS video generator.

Course : Pre-C-CAT - Section A - Logical Reasoning
Video  : Lesson 3 - Directions Sense Test - 03 - Distance & Displacement

Source script:
  C:\\Scripts\\Section A\\Reasoning_Scripts\\Sessions 1-4 - Coding-Decoding, Alphabets, Directions, Number Series, Odd Man Out\\Lesson 3 - Directions Sense Test\\03 - Distance & Displacement.pdf

Built on the golden-reference pattern:
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``;
  * layouts stacked with next_to and guarded with ``no_overlap``; nothing is
    ever animated onto or into another box.

Lesson 3, Video 2 of 6 (file 03 in its folder).
Not the first video: a silent breadcrumb, a one-line recap of Video 1, then today's topic.
The narration follows the script section by section and ends with the Section Quiz and its answer key.
Paths are drawn to scale with north at the top: blue arrows for the legs, a dashed green line for the straight-line distance.
Long practice and quiz questions are written compactly on screen ("Facing north: 4 km, right 6 km, ...") and read in full;
quiz options use N, E, SW and so on.
Every path in the script was walked again in the data block (turn by turn) and its distance and direction recomputed;
all the script's answers are correct.
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

COMPASS = {"N": (0, 1), "NE": (1, 1), "E": (1, 0), "SE": (1, -1), "S": (0, -1), "SW": (-1, -1), "W": (-1, 0), "NW": (-1, 1)}
ORDER = ["N", "E", "S", "W"]


def net_of(legs):
    """Net (east, north) of legs given as (distance, compass point); a diagonal leg of d adds d / sqrt(2) to each axis."""
    east = north = 0.0
    for d, point in legs:
        x, y = COMPASS[point]
        scale = d / _math.sqrt(2) if x and y else d
        east, north = east + x * scale, north + y * scale
    return round(east, 9), round(north, 9)


def walk(facing, *moves):
    """Turn-by-turn walk: numbers are distances, "R" / "L" / "U" are right, left and about turns.
    Returns (legs, final facing)."""
    legs = []
    for m in moves:
        if m in ("R", "L", "U"):
            facing = ORDER[(ORDER.index(facing) + {"R": 1, "L": -1, "U": 2}[m]) % 4]
        else:
            legs.append((m, facing))
    return legs, facing


def where(legs):
    """(straight-line distance, direction of the end from the start)."""
    east, north = net_of(legs)
    name = ("north" if north > 0 else "south" if north < 0 else "") + ("-" if east and north else "") + \
           ("east" if east > 0 else "west" if east < 0 else "")
    return round(_math.hypot(east, north), 6), name


ROOT2 = _math.sqrt(2)
# ---- hook, worked examples ----
assert where([(3, "N"), (4, "E")]) == (5, "north-east") and 3 + 4 == 7
CANCEL_LEGS, CANCEL_FACING = walk("N", 4, "R", 6, "R", 4, "L", 2)
assert CANCEL_LEGS == [(4, "N"), (6, "E"), (4, "S"), (2, "E")] and net_of(CANCEL_LEGS) == (8, 0) and where(CANCEL_LEGS) == (8, "east")
# ---- concept steps, exam patterns ----
assert net_of([(4 * ROOT2, "NE")]) == (4, 4)
assert where([(6, "E"), (8, "N")]) == (10, "north-east") and where([(5, "N"), (4, "E"), (2, "S"), (4, "W")]) == (3, "north")
assert walk("W", 12, "L", 5)[0] == [(12, "W"), (5, "S")] and where(walk("W", 12, "L", 5)[0]) == (13, "south-west")
assert walk("E", 15, "L", 10, "L", 15)[0] == [(15, "E"), (10, "N"), (15, "W")] and where(walk("E", 15, "L", 10, "L", 15)[0]) == (10, "north")
assert net_of([(7, "N"), (3, "E"), (3, "S"), (1, "E")]) == (4, 4) and round(4 * ROOT2, 2) == 5.66
assert where([(4 * ROOT2, "NE"), (4, "S")]) == (4, "east")
# ---- practice ----
assert where(walk("S", 10, "U", 4)[0]) == (6, "south") and where(walk("N", 3, "R", 4)[0]) == (5, "north-east")
EQUAL_LEGS, EQUAL_FACING = walk("N", 7, "R", 3, "R", 3, "L", 1)
assert net_of(EQUAL_LEGS) == (4, 4) and EQUAL_FACING == "E" and where(EQUAL_LEGS)[1] == "north-east"
# ---- section quiz ----
assert walk("S", 5, "R", 12)[0] == [(5, "S"), (12, "W")] and where(walk("S", 5, "R", 12)[0]) == (13, "south-west")
assert where(walk("N", 6, "R", 4, "R", 6)[0]) == (4, "east") and where(walk("E", 8, "L", 6)[0])[0] == 10
assert net_of(walk("N", 9, "L", 3, "L", 5, "L", 6)[0]) == (3, 4) and where(walk("N", 9, "L", 3, "L", 5, "L", 6)[0]) == (5, "north-east")
assert where([(3 * ROOT2, "SE"), (3, "N")]) == (3, "east")

OBJECTIVES = [("Reduce any path", "to a net north-south and a net east-west movement"),
              ("Find the shortest distance from the start", "with Pythagoras"),
              ("Name the direction of the end point", "from the start")]
FORMULAS = ["Net N–S  =  north legs − south legs;        net E–W  =  east legs − west legs",
            "Shortest distance  =  √(N–S² + E–W²)",
            "Direction from the start:   combine the signs of the nets",
            "Start from the end  =  the opposite direction",
            "Triples:   3-4-5,    6-8-10,    5-12-13,    8-15-17",
            "Coordinates:   east +x,  north +y;    a 45° leg of d adds d/√2 to each axis"]
PATTERNS = [["Two legs at right angles", "6 km east,  8 km north", "√(36 + 64)", "10 km, north-east"],
            ["Legs that cancel", "5 N,  4 E,  2 S,  4 W", "net 3 N,  0 E", "3 km north"],
            ["Turns, then distance", "facing W:  12 km;  left;  5 km", "left from W is S", "13 km, south-west"],
            ["U-shaped path", "facing E:  15,  left 10,  left 15", "E and W cancel", "10 m north"],
            ["Equal components", "7 N,  3 E,  3 S,  1 E", "net 4 N,  4 E", "4√2 ≈ 5.66 km, north-east"],
            ["Diagonal leg", "4√2 km north-east,  then 4 km south", "(4, 4)  then  (4, 0)", "4 km east"]]
TRAPS = [("Trap 1  ·  total path instead of distance from the start", "A drone flies 3 km north and 4 km east.   How far is it from base?",
          "7 km", "5 km",
          "“how far from the start” means the straight-line distance"),
         ("Trap 2  ·  direction from the wrong end",
          "A person ends 5 km north-east of the start.   In which direction is the start from the person?",
          "north-east", "south-west",
          "reversing the viewpoint reverses the direction")]
PRACTICE_L1 = [("L1", "A person walks 6 km east, then 8 km north.  How far is the person from the start?"),
               ("L1", "A person walks 5 km north, 4 km east, 2 km south and 4 km west.  How far, and in which direction, from the start?"),
               ("L1", "A person walks 10 m south, turns around and walks 4 m.  How far is the person from the start?")]
PRACTICE_L2 = [("L2", "Facing north, a person walks 3 km, turns right and walks 4 km.  How far, and in which direction, from the start?"),
               ("L2", "Facing west, a person walks 12 km, turns left and walks 5 km.  How far, and in which direction, from the start?"),
               ("L2", "Facing east, a person walks 15 m, turns left and walks 10 m, then turns left and walks 15 m.  "
                      "Where is the person relative to the start?")]
PRACTICE_L3 = [("L3", "Facing north:  4 km,  right 6 km,  right 4 km,  left 2 km.   How far, and in which direction, from the start?"),
               ("L3", "Facing north:  7 km,  right 3 km,  right 3 km,  left 1 km.   How far, in which direction, and facing which way?"),
               ("L3", "A person walks 4√2 km north-east, then 4 km south.  Where is the person relative to the start?")]
ANSWERS_A = [("√(36 + 64)", "10 km"),
             ("net 3 N,  0 E", "3 km north"),
             ("10 − 4", "6 m,  south of the start"),
             ("3 N,  4 E", "5 km north-east"),
             ("left from west is south:   12 W,  5 S", "13 km south-west")]
ANSWERS_B = [("E and W cancel", "10 m north"),
             ("net 0 N–S,  8 E", "8 km east"),
             ("net 4 N,  4 E:   4√2 ≈ 5.66 km", "north-east;  facing east"),
             ("north-east leg  =  4 E and 4 N;   then 4 S", "4 km east")]
LENS = [("Recognition cue", "“how far from the starting point”,  “in which direction from”"),
        ("Target time", "25 seconds for two legs,  30 seconds for four"),
        ("Sanity check", "the distance from the start can never exceed the total path walked")]
QUIZ = [["Facing south:  5 km,  right,  12 km.   How far and in which direction from the start?",
         "(a) 17 km SW   (b) 13 km SW   (c) 13 km SE   (d) 7 km SW"],
        ["Facing north:  6 km,  right,  4 km,  right,  6 km.   Where is the person relative to the start?",
         "(a) 4 km east   (b) 16 km east   (c) 4 km west   (d) 12 km north"],
        ["Facing east:  8 km,  left,  6 km.   How far from the start?", "(a) 14 km   (b) 2 km   (c) 100 km   (d) 10 km"],
        ["Facing north:  9 km,  left 3 km,  left 5 km,  left 6 km.   How far and in which direction?",
         "(a) 5 km NE   (b) 5 km NW   (c) 23 km NE   (d) 4 km N"],
        ["A person ends 10 km north-west of the start.   In which direction is the start from the person?",
         "(a) North-west   (b) South-west   (c) South-east   (d) North-east"],
        ["A person walks 3√2 km south-east, then 3 km north.   Where is the person relative to the start?",
         "(a) 3 km SE   (b) 3 km E   (c) 3√2 km E   (d) 6 km E"]]
QUIZ_KEY = [("right from south is west:   5 S,  12 W", "(b)  13 km SW"),
            ("north and south cancel;   4 E", "(a)  4 km east"),
            ("the 6-8-10 triple", "(d)  10 km"),
            ("net 4 N,  3 E", "(a)  5 km NE"),
            ("reverse north-west", "(c)  South-east"),
            ("south-east leg  =  3 E and 3 S;   then 3 N", "(b)  3 km E")]


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


class DistanceAndDisplacementVideo(LMSScene):
    lesson_title = "Distance & Displacement"

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

    def path_map(self, legs, tags, box=(4.4, 3.4), color=WORD):
        """A path drawn to scale, north at the top.  legs = [(east, north), ...]; tags = one label per leg.
        Returns (start dot, leg arrows, leg labels, end dot, dashed start-to-end line, north mark)."""
        pts = [np.zeros(3)]
        for east, north in legs:
            pts.append(pts[-1] + np.array([float(east), float(north), 0.0]))
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        k = min(box[0] / max(max(xs) - min(xs), 1e-6), box[1] / max(max(ys) - min(ys), 1e-6), 1.2)
        pts = [p * k for p in pts]
        arrows, labels = VGroup(), VGroup()
        for a, b, tag in zip(pts, pts[1:], tags):
            arrows.add(Arrow(a, b, buff=0, color=color, stroke_width=5, max_tip_length_to_length_ratio=0.12))
            along = (b - a) / np.linalg.norm(b - a)
            side = np.array([-along[1], along[0], 0.0])                # the left-hand side of the direction of travel
            label = text(tag, SMALL, INK, BOLD)
            label.move_to((a + b) / 2 + side * (0.2 + abs(side[0]) * label.width / 2 + abs(side[1]) * label.height / 2))
            labels.add(label)
        start, end = Dot(pts[0], color=FOCUS, radius=0.1), Dot(pts[-1], color=GOOD, radius=0.1)
        net = DashedLine(pts[0], pts[-1], color=GOOD, stroke_width=4)
        north = VGroup(Arrow(ORIGIN, UP * 0.6, buff=0, color=MUTED, stroke_width=3), text("N", SMALL, MUTED, BOLD)).arrange(UP, buff=0.05)
        north.next_to(VGroup(arrows, labels), LEFT, buff=0.6, aligned_edge=UP)
        self.no_overlap(*labels, gap=0.02)
        return VGroup(start, arrows, labels, end, net, north)

    def net_tag(self, path, tag, side):
        """A label for the dashed start-to-end line of a placed path_map, offset to the given side."""
        return text(tag, SMALL, GOOD, BOLD).move_to(path[4].get_center() + side)

    # ============================================== 0. INTRO ==========
    # Not the first video: silent breadcrumb, a one-line recap of the previous video, then today's topic.

    def intro(self):
        self.scene_start("S00_intro", title="Intro")

        crumb = self.breadcrumb("Logical Reasoning", "Lesson 3 · Directions Sense Test", "Video 2 of 6")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        recap = VGroup(text("from Video 1  ·  Directions & Turns", SMALL, MUTED), pill("right +90°,  left −90°;   apply the net turn once", WORD, size=LABEL)).arrange(DOWN, buff=0.25)
        title = fit_width(text("Distance & Displacement", TITLE, INK, BOLD), SAFE_W - 0.4)
        today = text("today: the straight-line distance, not the path", LABEL, FOCUS)
        block = VGroup(recap, title, today).arrange(DOWN, buff=0.7)
        fit_within(block, SAFE_W, SAFE_H - crumb.height - 0.9)
        block.next_to(crumb, DOWN, buff=0.7)
        self.no_overlap(crumb, recap, title, today)
        self.validator.check_in_frame(VGroup(crumb, block))

        n = self.narrate(
            id="intro_01",
            text="In the last video, a right turn added ninety degrees and a left turn subtracted ninety, and the net turn "
                 "was applied once.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.at_word(n, "added")
        self.play(FadeIn(recap[0]))
        self.at_word(n, "net")
        self.play(FadeIn(recap[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="intro_02",
            text="This video covers distance and displacement: the straight-line distance, not the path walked.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "covers")
        self.play(FadeIn(title, shift=UP * 0.1))
        self.at_word(n, "straight-line")
        self.play(FadeIn(today, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_intro")

    # ============================================== 1. HOOK ==========

    def hook(self):
        self.scene_start("S01_hook", title="Hook")

        head = self.heading("A drone's flight log")
        path = self.path_map([(0, 3), (4, 0)], ["3 km", "4 km"])
        log = self.card(VGroup(text("3 km north,  then 4 km east", LABEL, INK), text("total flown:  7 km", LABEL, MUTED)).arrange(DOWN, buff=0.2),
                        color=WORD, pad=0.35)
        ask = text("how far is it from base right now?", LABEL, FOCUS, BOLD)
        tri = VGroup(pill("not 7", BAD, size=LABEL), pill("a right triangle, sides 3 and 4:   5 km", GOOD, size=LABEL)).arrange(DOWN, buff=0.3)
        moral = text("exams ask for the straight-line distance,\nnot the path walked", SMALL, RATIO, BOLD)
        side = VGroup(log, ask, tri, moral).arrange(DOWN, buff=0.5)
        row = VGroup(path, side).arrange(RIGHT, buff=0.9)
        self.stack(head, [row], top=0.6)
        self.no_overlap(path, side)
        far = self.net_tag(path, "5 km", RIGHT * 0.5 + DOWN * 0.3)

        n = self.narrate(
            id="hook_01",
            text="A delivery drone flies three kilometres north, then four kilometres east.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "drone")
        self.play(FadeIn(path[0]), FadeIn(path[5], shift=UP * 0.1))
        self.at_word(n, "north")
        self.play(GrowArrow(path[1][0]), FadeIn(path[2][0]))
        self.at_word(n, "east")
        self.play(GrowArrow(path[1][1]), FadeIn(path[2][1]), FadeIn(path[3], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_02",
            text="Its log says seven kilometres flown. How far is it from base right now?",
            voice="default",
            subtitle=True,
            pause_after=3.0,
        )
        self.at_word(n, "log")
        self.play(FadeIn(log, shift=UP * 0.1))
        self.at_word(n, "far")
        self.play(FadeIn(ask, shift=UP * 0.1))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="hook_03",
            text="Not seven. The drone is at the corner of a right triangle with sides three and four, so it is five "
                 "kilometres from base.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Not")
        self.play(FadeIn(tri[0], shift=UP * 0.1))
        self.at_word(n, "triangle")
        self.play(Create(path[4]))
        self.at_word(n, "five")
        self.play(FadeIn(tri[1], shift=UP * 0.1), FadeIn(far, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_04",
            text="Exam questions almost always ask for this straight-line distance, not the path walked.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "straight-line")
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
            text="One: reduce any path to a net north-south and a net east-west movement.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "reduce")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "net")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="objectives_03",
            text="Two: find the shortest distance from the start with Pythagoras.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "shortest")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "Pythagoras")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="objectives_04",
            text="Three: name the direction of the end point from the start.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "name")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "from")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_objectives")

    # ============================================== 3. WHY THIS SECTION ==========

    def why_this_section(self):
        self.scene_start("S03_why_this_section", title="Why This Section")

        head = self.heading("Why this section")
        long = pill("exam paths are long on purpose", WORD, size=BODY)
        left = VGroup(pill("most legs cancel", RATIO, size=LABEL), text("→", BODY, MUTED), pill("what remains is a single right triangle", GOOD, size=LABEL))\
            .arrange(RIGHT, buff=0.4)
        self.stack(head, [long, left], buff=1.2, top=1.4)
        self.no_overlap(*left)

        n = self.narrate(
            id="why_this_section_01",
            text="Exam paths are long on purpose.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "long")
        self.play(FadeIn(long, scale=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="why_this_section_02",
            text="Most legs cancel, and what remains is a single right triangle.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "cancel")
        self.play(FadeIn(left[0], shift=UP * 0.1))
        self.at_word(n, "remains")
        self.play(FadeIn(left[1:], shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_why_this_section")

    # ============================================== 4. THE CONCEPT JOURNEY ==========

    def concept_journey(self):
        self.scene_start("S04_concept_journey", title="The Concept Journey")

        head = self.heading("Steps 1 to 3  ·  draw, split each leg, net movement")
        path = self.path_map([(0, 4), (6, 0), (0, -4), (2, 0)], ["4", "6", "4", "2"], box=(4.8, 2.8))
        draw = text("north at the top;  track the facing after every turn", SMALL, MUTED)
        signs = VGroup(pill("north and east:  positive", GOOD, size=SMALL), pill("south and west:  negative", BAD, size=SMALL)).arrange(RIGHT, buff=0.3)
        nets = VGroup(text("north–south:    +4 − 4  =  0", LABEL, INK, BOLD), text("east–west:    +6 + 2  =  8", LABEL, INK, BOLD))\
            .arrange(DOWN, buff=0.25, aligned_edge=LEFT)
        cancel = text("add each set separately:  opposite legs cancel", SMALL, RATIO, BOLD)
        side = VGroup(draw, signs, nets, cancel).arrange(DOWN, buff=0.5)
        row = VGroup(path, side).arrange(RIGHT, buff=0.8)
        self.stack(head, [row], top=0.9)
        self.no_overlap(path, side)
        self.no_overlap(*signs)

        n = self.narrate(
            id="concept_journey_01",
            text="Step one: draw with north at the top. Track the facing after every turn, as in the last video.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "one")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "draw")
        self.play(FadeIn(path[0]), FadeIn(path[5], shift=UP * 0.1), FadeIn(draw, shift=UP * 0.1))
        self.at_word(n, "Track")
        self.play(FadeIn(path[1]), FadeIn(path[2], shift=UP * 0.1), FadeIn(path[3], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_journey_02",
            text="Step two: split each leg. Each leg adds to north-south or to east-west. North and east are positive; "
                 "south and west are negative.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "two")
        self.play(Indicate(head, color=FOCUS, scale_factor=1.03))
        self.at_word(n, "adds")
        self.play(Indicate(path[2], color=FOCUS, scale_factor=1.03))
        self.at_word(n, "positive")
        self.play(FadeIn(signs[0], shift=UP * 0.1))
        self.at_word(n, "negative")
        self.play(FadeIn(signs[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_journey_03",
            text="Step three: net movement. Add the north-south legs and the east-west legs separately. Opposite legs "
                 "cancel.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "three")
        self.play(Indicate(head, color=FOCUS, scale_factor=1.03))
        self.at_word(n, "separately")
        self.play(FadeIn(nets[0], shift=RIGHT * 0.2), FadeIn(nets[1], shift=RIGHT * 0.2))
        self.at_word(n, "cancel")
        self.play(FadeIn(cancel, shift=UP * 0.1), Create(path[4]))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Steps 4 to 6  ·  shortest distance, and direction")
        path = self.path_map([(0, 3), (4, 0)], ["3", "4"], box=(3.6, 2.7))
        dist = VGroup(pill("shortest distance  =  √(N–S² + E–W²)", FOCUS, size=LABEL), text("if one net is zero, the distance is just the other", SMALL, MUTED))\
            .arrange(DOWN, buff=0.18, aligned_edge=LEFT)
        way = VGroup(pill("direction from the start:  combine the signs", RATIO, size=LABEL),
                     text("north and east → north-east;     south only → south", SMALL, INK, BOLD),
                     text("“north-east” = somewhere north and east, not exactly 45°", SMALL, MUTED)).arrange(DOWN, buff=0.18, aligned_edge=LEFT)
        back = VGroup(pill("direction from the end:  reverse it", SECOND, size=LABEL), text("north-east becomes south-west", SMALL, INK, BOLD))\
            .arrange(DOWN, buff=0.18, aligned_edge=LEFT)
        side = VGroup(dist, way, back).arrange(DOWN, buff=0.45, aligned_edge=LEFT)
        row = VGroup(path, side).arrange(RIGHT, buff=0.7)
        self.stack(head, [row], top=0.7)
        self.no_overlap(path, side)
        far = self.net_tag(path, "5", RIGHT * 0.35 + DOWN * 0.25)

        n = self.narrate(
            id="concept_journey_04",
            text="Step four: the shortest distance is the square root of the north-south net squared plus the east-west "
                 "net squared. If one net is zero, the distance is just the other.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "four")
        self.play(FadeIn(path[:4]), FadeIn(path[5], shift=UP * 0.1))
        self.at_word(n, "root")
        self.play(FadeIn(dist[0], shift=UP * 0.1), Create(path[4]), FadeIn(far))
        self.at_word(n, "zero")
        self.play(FadeIn(dist[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_journey_05",
            text="Step five: the direction from the start. Combine the signs: north and east give north-east; south only "
                 "gives south.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "five")
        self.play(FadeIn(way[0], shift=UP * 0.1))
        self.at_word(n, "signs")
        self.play(FadeIn(way[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_journey_06",
            text="In exam answers, north-east means somewhere north and east, not exactly forty-five degrees, unless the "
                 "two nets are equal.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "somewhere")
        self.play(FadeIn(way[2], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_journey_07",
            text="Step six: the direction from the end. Asked where the start is from the end point? Reverse it: "
                 "north-east becomes south-west.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "six")
        self.play(FadeIn(back[0], shift=UP * 0.1))
        self.at_word(n, "Asked")
        self.play(Indicate(path[3], color=FOCUS, scale_factor=1.03))
        self.at_word(n, "Reverse")
        self.play(FadeIn(back[1], shift=UP * 0.1))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Step 7  ·  diagonal legs and coordinates")
        path = self.path_map([(4, 4)], ["4√2 km"], box=(3.2, 3.2), color=RATIO)
        axes = text("the start is (0, 0);   east is +x,   north is +y", LABEL, INK)
        rule = pill("a leg of d at 45° adds d/√2 to both components", FOCUS, size=LABEL)
        ex = text("4√2 km north-east   =   4 km east  and  4 km north", LABEL, GOOD, BOLD)
        side = VGroup(axes, rule, ex).arrange(DOWN, buff=0.7)
        row = VGroup(path, side).arrange(RIGHT, buff=0.8)
        self.stack(head, [row], top=0.9)
        self.no_overlap(path, side)
        corner = np.array([path[3].get_center()[0], path[0].get_center()[1], 0.0])
        parts = VGroup(DashedLine(path[0].get_center(), corner, color=GOOD, stroke_width=4), DashedLine(corner, path[3].get_center(), color=GOOD, stroke_width=4))
        marks = VGroup(text("4 E", SMALL, GOOD, BOLD).next_to(parts[0], DOWN, buff=0.15), text("4 N", SMALL, GOOD, BOLD).next_to(parts[1], LEFT, buff=0.15))
        self.no_overlap(marks[1], path[2])

        n = self.narrate(
            id="concept_journey_08",
            text="Step seven: diagonal legs and coordinates. Treat the start as the origin, with east as plus x and north "
                 "as plus y.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "seven")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "origin")
        self.play(FadeIn(path[0]), FadeIn(path[5], shift=UP * 0.1), FadeIn(axes, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_journey_09",
            text="A leg of d at forty-five degrees, for example north-east, adds d over root two to both components.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "leg")
        self.play(GrowArrow(path[1][0]), FadeIn(path[2]), FadeIn(path[3], shift=UP * 0.1))
        self.at_word(n, "adds")
        self.play(FadeIn(rule, scale=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_journey_10",
            text="So four root two kilometres north-east is four kilometres east and four kilometres north.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "east")
        self.play(Create(parts[0]), FadeIn(marks[0], shift=UP * 0.1), FadeIn(ex, shift=UP * 0.1))
        self.at_word(n, "north")
        self.play(Create(parts[1]), FadeIn(marks[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_concept_journey")

    # ============================================== 5. RULE BOX ==========

    def rule_box(self):
        self.scene_start("S05_rule_box", title="Rule Box")

        head = self.heading("Rule box", GOOD)
        lines = VGroup(*[text(f, LABEL, INK) for f in FORMULAS]).arrange(DOWN, buff=0.36, aligned_edge=LEFT)
        fit_width(lines, SAFE_W - 1.6)
        box = self.card(lines, width=SAFE_W - 0.4, color=GOOD, pad=0.5)
        self.stack(head, [box], top=0.8)

        n = self.narrate(
            id="rule_box_01",
            text="Here is the rule box. The north-south net is the north legs minus the south legs; the east-west net is "
                 "the east legs minus the west legs.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "box")
        self.play(FadeIn(box[0]))
        self.at_word(n, "minus")
        self.play(FadeIn(lines[0], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="rule_box_02",
            text="The shortest distance is the square root of the sum of their squares.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "root")
        self.play(FadeIn(lines[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="rule_box_03",
            text="The direction from the start combines the signs of the nets.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "signs")
        self.play(FadeIn(lines[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="rule_box_04",
            text="The start, seen from the end, is in the opposite direction.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "opposite")
        self.play(FadeIn(lines[3], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="rule_box_05",
            text="Know the triples: three, four, five; six, eight, ten; five, twelve, thirteen; and eight, fifteen, "
                 "seventeen.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "triples")
        self.play(FadeIn(lines[4], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="rule_box_06",
            text="And in coordinates, a forty-five degree leg of d adds d over root two to each axis.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "coordinates")
        self.play(FadeIn(lines[5], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_rule_box")

    # ============================================== 6. SHORT TRICK ==========

    def short_trick(self):
        self.scene_start("S06_short_trick", title="Short Trick")

        head = self.heading("Short trick", RATIO)
        totals = VGroup(pill("east–west total", WORD, size=BODY), pill("north–south total", RATIO, size=BODY)).arrange(RIGHT, buff=0.6)
        keep = text("keep two running totals as you read", BODY, INK, BOLD)
        only = text("only the two final totals matter:  ignore everything else", LABEL, GOOD, BOLD)
        self.stack(head, [keep, totals, only], buff=1.0, top=1.1)
        self.no_overlap(*totals)

        n = self.narrate(
            id="short_trick_01",
            text="The short trick: keep two running totals as you read, east-west and north-south.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "totals")
        self.play(FadeIn(keep, shift=UP * 0.1))
        self.at_word(n, "east-west")
        self.play(FadeIn(totals[0], shift=UP * 0.1))
        self.at_word(n, "north-south")
        self.play(FadeIn(totals[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="short_trick_02",
            text="Only the two final totals matter; ignore everything else.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "final")
        self.play(FadeIn(only, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_short_trick")

    # ============================================== 7. THE ANALOGY - A BANK STATEMENT ==========

    def analogy(self):
        self.scene_start("S07_analogy", title="The Analogy - A Bank Statement")

        head = self.heading("A path is a bank statement with two accounts")
        north = VGroup(text("north–south account", SMALL, WORD, BOLD), text("+4      −4", BODY, INK, BOLD), text("closing balance:   0", LABEL, GOOD, BOLD))\
            .arrange(DOWN, buff=0.3)
        east = VGroup(text("east–west account", SMALL, RATIO, BOLD), text("+6      +2", BODY, INK, BOLD), text("closing balance:   8", LABEL, GOOD, BOLD))\
            .arrange(DOWN, buff=0.3)
        books = VGroup(self.card(north, color=WORD, pad=0.4), self.card(east, color=RATIO, pad=0.4)).arrange(RIGHT, buff=0.8)
        only = text("each leg is a deposit or a withdrawal;  only the closing balances matter", LABEL, INK)
        stops = VGroup(text("where the analogy stops", SMALL, BAD, BOLD), text("balances are combined with Pythagoras, not by adding them", SMALL, INK))\
            .arrange(DOWN, buff=0.14, aligned_edge=LEFT)
        self.stack(head, [books, only, stops], buff=0.7, top=0.7)
        self.no_overlap(*books)

        n = self.narrate(
            id="analogy_01",
            text="A path is like a bank statement with two accounts, north-south and east-west.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "statement")
        self.play(FadeIn(books[0][0]), FadeIn(books[1][0], shift=UP * 0.1))
        self.at_word(n, "north-south")
        self.play(FadeIn(north[0], shift=UP * 0.1))
        self.at_word(n, "east-west")
        self.play(FadeIn(east[0], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_02",
            text="Each leg is a deposit or a withdrawal; only the closing balances matter.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "deposit")
        self.play(FadeIn(north[1], shift=UP * 0.1), FadeIn(east[1], shift=UP * 0.1))
        self.at_word(n, "closing")
        self.play(FadeIn(north[2], shift=UP * 0.1), FadeIn(east[2], shift=UP * 0.1), FadeIn(only, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_03",
            text="Where the analogy stops: balances are combined with Pythagoras, not by adding them.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "stops")
        self.play(FadeIn(stops[0], shift=RIGHT * 0.2))
        self.at_word(n, "Pythagoras")
        self.play(FadeIn(stops[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S07_analogy")

    # ============================================== 8. WORKED EXAMPLE - CLOSING THE HOOK ==========

    def hook_solved(self):
        self.scene_start("S08_hook_solved", title="Worked Example - Closing the Hook")

        head = self.heading("Worked example: closing the hook")
        path = self.path_map([(0, 3), (4, 0)], ["3 km", "4 km"])
        nets = VGroup(pill("net north  3", WORD, size=LABEL), pill("net east  4", RATIO, size=LABEL)).arrange(RIGHT, buff=0.5)
        root = text("distance  =  √(9 + 16)  =  5 km", BODY, INK, BOLD)
        answer = pill("5 km,  to the north-east of base", GOOD, size=LABEL)
        side = VGroup(nets, root, answer).arrange(DOWN, buff=0.8)
        row = VGroup(path, side).arrange(RIGHT, buff=0.9)
        self.stack(head, [row], top=0.8)
        self.no_overlap(path, side)
        self.no_overlap(*nets)
        far = self.net_tag(path, "5 km", RIGHT * 0.5 + DOWN * 0.3)

        n = self.narrate(
            id="hook_solved_01",
            text="The net movement is three north and four east.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "net")
        self.play(FadeIn(path[:4]), FadeIn(path[5], shift=UP * 0.1))
        self.at_word(n, "three")
        self.play(FadeIn(nets[0], shift=UP * 0.1))
        self.at_word(n, "four")
        self.play(FadeIn(nets[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_solved_02",
            text="The distance is the square root of nine plus sixteen, which is five kilometres.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "root")
        self.play(FadeIn(root, shift=UP * 0.1))
        self.at_word(n, "five")
        self.play(Create(path[4]), FadeIn(far))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_solved_03",
            text="And it lies to the north-east of base.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "north-east")
        self.play(FadeIn(answer, scale=1.03))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S08_hook_solved")

    # ============================================== 9. A SECOND WORKED EXAMPLE - LEGS THAT CANCEL ==========

    def second_example(self):
        self.scene_start("S09_second_example", title="A Second Worked Example - Legs That Cancel")

        head = self.heading("A second worked example: legs that cancel")
        ask = text("Facing north:  walks 4 km,  turns right 6 km,  turns right 4 km,  turns left 2 km.   How far, and in which direction?", SMALL, INK)
        path = self.path_map([(0, 4), (6, 0), (0, -4), (2, 0)], ["4 N", "6 E", "4 S", "2 E"], box=(4.8, 2.6))
        steps = self.solve_steps([("north–south:   4 − 4", "0"), ("east–west:   6 + 2", "8"), ("the answer", "8 km east of the start")])
        row = VGroup(path, steps).arrange(RIGHT, buff=0.9)
        self.stack(head, [ask, row], buff=0.7, top=0.6)
        self.no_overlap(path, steps)
        self.no_overlap(*steps)

        n = self.narrate(
            id="second_example_01",
            text="A person starts facing north, walks four kilometres, turns right and walks six, turns right and walks "
                 "four, then turns left and walks two. How far, and in which direction, is the person from the start?",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "person")
        self.play(FadeIn(ask, shift=UP * 0.1))
        self.at_word(n, "north")
        self.play(FadeIn(path[0]), FadeIn(path[5], shift=UP * 0.1))
        self.at_word(n, "far")
        self.play(Indicate(ask, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_02",
            text="Step one, the legs: four north, six east, then four south, because after the second right the person "
                 "faces south. Left from south is east, so the last leg is two east.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "north")
        self.play(GrowArrow(path[1][0]), FadeIn(path[2][0]))
        self.at_word(n, "east")
        self.play(GrowArrow(path[1][1]), FadeIn(path[2][1]))
        self.at_word(n, "south")
        self.play(GrowArrow(path[1][2]), FadeIn(path[2][2]))
        self.at_word(n, "last")
        self.play(GrowArrow(path[1][3]), FadeIn(path[2][3]), FadeIn(path[3], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_03",
            text="Step two, the nets: north-south is four minus four, zero. East-west is six plus two, eight.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "minus")
        self.play(FadeIn(steps[0], shift=RIGHT * 0.2))
        self.at_word(n, "plus")
        self.play(FadeIn(steps[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_04",
            text="The answer: eight kilometres east of the start.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "answer")
        self.play(FadeIn(steps[2], shift=RIGHT * 0.2), Create(path[4]))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S09_second_example")

    # ============================================== 10. EXAM PATTERNS - HOW THIS IS ASKED ==========

    def exam_patterns(self):
        self.scene_start("S10_exam_patterns", title="Exam Patterns - How This Is Asked")

        head = self.heading("Exam patterns  ·  part 1")
        table, rows = self.placed_table(head, ["Pattern", "Example", "Method", "Answer"], PATTERNS[:3], [3.1, 4.2, 2.8, 3.2], room=1.2)
        for row in rows:
            row[0].set_color(WORD)
            row[3].set_color(GOOD)

        n = self.narrate(
            id="exam_patterns_01",
            text="Exams ask this in six ways.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "six")
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_02",
            text="Two legs at right angles: six kilometres east and eight north give the square root of thirty-six plus "
                 "sixty-four: ten kilometres, north-east.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "legs")
        self.play(FadeIn(rows[0][:3], shift=RIGHT * 0.2))
        self.at_word(n, "ten")
        self.play(FadeIn(rows[0][3], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_03",
            text="Legs that cancel: five north, four east, two south, four west leave a net of three north: three "
                 "kilometres north.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "cancel")
        self.play(FadeIn(rows[1][:3], shift=RIGHT * 0.2))
        self.at_word(n, "kilometres")
        self.play(FadeIn(rows[1][3], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_04",
            text="Turns, then distance: facing west, twelve kilometres, then left, which is south, five kilometres: "
                 "thirteen kilometres, south-west.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Turns")
        self.play(FadeIn(rows[2][:3], shift=RIGHT * 0.2))
        self.at_word(n, "thirteen")
        self.play(FadeIn(rows[2][3], shift=LEFT * 0.1))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Exam patterns  ·  part 2")
        table, rows = self.placed_table(head, ["Pattern", "Example", "Method", "Answer"], PATTERNS[3:], [3.1, 4.2, 2.8, 3.2], room=1.2)
        for row in rows:
            row[0].set_color(WORD)
            row[3].set_color(GOOD)

        n = self.narrate(
            id="exam_patterns_05",
            text="A U-shaped path: facing east, fifteen, left ten, left fifteen. East and west cancel, leaving ten metres "
                 "north.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "path")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "cancel")
        self.play(FadeIn(rows[0][2], shift=RIGHT * 0.2))
        self.at_word(n, "leaving")
        self.play(FadeIn(rows[0][3], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_06",
            text="Equal components: seven north, three east, three south, one east make a net of four north and four east: "
                 "four root two, about five point six six kilometres, north-east.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "components")
        self.play(FadeIn(rows[1][:3], shift=RIGHT * 0.2))
        self.at_word(n, "root")
        self.play(FadeIn(rows[1][3], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_07",
            text="A diagonal leg: four root two kilometres north-east, then four south, goes to four, four, then to four, "
                 "zero: four kilometres east.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "diagonal")
        self.play(FadeIn(rows[2][:3], shift=RIGHT * 0.2))
        self.at_word(n, "zero")
        self.play(FadeIn(rows[2][3], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S10_exam_patterns")

    # ============================================== 11. TRAPS AND CONFUSING QUESTIONS ==========

    def traps(self):
        self.scene_start("S11_traps", title="Traps and Confusing Questions")

        head, ask, wrong, right, rule = self.show_trap(TRAPS[0])

        n = self.narrate(
            id="traps_01",
            text="Trap one: the total path instead of the distance from the start.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "total")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_02",
            text="A drone flies three kilometres north and four kilometres east. How far is it from base?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "drone")
        self.play(FadeIn(ask, shift=UP * 0.1))
        self.at_word(n, "far")
        self.play(Indicate(ask, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_03",
            text="The wrong instinct: seven kilometres.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "instinct")
        self.play(FadeIn(wrong, shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_04",
            text="Correct: five kilometres.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "five")
        self.play(FadeIn(right, shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_05",
            text="The rule: how far from the start means the straight-line distance. Add the path lengths only if you are "
                 "asked for the total distance walked.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "means")
        self.play(FadeIn(rule, scale=1.03))
        self.at_word(n, "only")
        self.play(Indicate(rule, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)
        self.clear_stage()

        head, ask, wrong, right, rule = self.show_trap(TRAPS[1])

        n = self.narrate(
            id="traps_06",
            text="Trap two: the direction from the wrong end.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "wrong")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_07",
            text="A person ends five kilometres north-east of the start. In which direction is the start from the person?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "ends")
        self.play(FadeIn(ask, shift=UP * 0.1))
        self.at_word(n, "direction")
        self.play(Indicate(ask, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_08",
            text="The wrong instinct: north-east.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "instinct")
        self.play(FadeIn(wrong, shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_09",
            text="Correct: south-west.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "south-west")
        self.play(FadeIn(right, shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_10",
            text="The rule: check which point the question measures from; reversing the viewpoint reverses the direction.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "reversing")
        self.play(FadeIn(rule, scale=1.03))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S11_traps")

    # ============================================== 12. CHECKPOINT ==========

    def checkpoint(self):
        self.scene_start("S12_checkpoint", title="Checkpoint")

        head = self.heading("Checkpoint  ·  your turn")
        ask = text("A person walks 5 km north, 4 km east, 2 km south and 4 km west.   How far from the start?", LABEL, FOCUS, BOLD)
        path = self.path_map([(0, 5), (4, 0), (0, -2), (-4, 0)], ["5", "4", "2", "4"], box=(3.6, 2.9))
        work = VGroup(text("east and west cancel", LABEL, INK), text("north–south:   5 − 2  =  3", LABEL, INK, BOLD)).arrange(DOWN, buff=0.35)
        answer = pill("3 km north", GOOD, size=BODY)
        side = VGroup(work, answer).arrange(DOWN, buff=0.8)
        row = VGroup(path, side).arrange(RIGHT, buff=1.2)
        self.stack(head, [ask, row], buff=0.7, top=0.6)
        self.no_overlap(path, side)

        n = self.narrate(
            id="checkpoint_01",
            text="Your turn. A person walks five kilometres north, four east, two south and four west. How far from the "
                 "start?",
            voice="default",
            subtitle=True,
            pause_after=10.0,
        )
        self.at_word(n, "turn")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "person")
        self.play(FadeIn(ask, shift=UP * 0.1))
        self.at_word(n, "far")
        self.play(Indicate(ask, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="checkpoint_02",
            text="East and west cancel, and five minus two is three.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "cancel")
        self.play(FadeIn(path[:4]), FadeIn(path[5], shift=UP * 0.1), FadeIn(work[0], shift=UP * 0.1))
        self.at_word(n, "minus")
        self.play(FadeIn(work[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="checkpoint_03",
            text="The person is three kilometres north of the start.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "north")
        self.play(Create(path[4]), FadeIn(answer))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S12_checkpoint")

    # ============================================== 13. PRACTICE QUESTIONS ==========

    def practice(self):
        self.scene_start("S13_practice", title="Practice Questions")

        head = self.heading("Practice  ·  Level 1")
        table, rows = self.practice_table(head, PRACTICE_L1, 1)

        n = self.narrate(
            id="practice_01",
            text="Level one, question one: a person walks six kilometres east, then eight north; how far from the start? "
                 "Question two: a person walks five kilometres north, four east, two south and four west; how far, and in "
                 "which direction, from the start? Question three: a person walks ten metres south, turns around and walks "
                 "four metres; how far from the start?",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "six")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "five")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.at_word(n, "ten")
        self.play(FadeIn(rows[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="practice_02",
            text="Pause the video and solve these three.",
            voice="default",
            subtitle=True,
            pause_after=12.0,
        )
        self.at_word(n, "Pause")
        self.play(Indicate(head, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)
        self.clear_stage()

        head = self.heading("Practice  ·  Level 2")
        table, rows = self.practice_table(head, PRACTICE_L2, 4)

        n = self.narrate(
            id="practice_03",
            text="Level two, question four: facing north, a person walks three kilometres, turns right and walks four. "
                 "Question five: facing west, a person walks twelve kilometres, turns left and walks five. For both: how "
                 "far, and in which direction, from the start?",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "four")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "five")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.at_word(n, "both")
        self.play(Indicate(head, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="practice_04",
            text="Question six: facing east, a person walks fifteen metres, turns left and walks ten, then turns left and "
                 "walks fifteen. Where is the person relative to the start?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "six")
        self.play(FadeIn(rows[2], shift=RIGHT * 0.2))
        self.at_word(n, "Where")
        self.play(Indicate(rows[2], color=FOCUS, scale_factor=1.03))
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

        head = self.heading("Practice  ·  Level 3")
        table, rows = self.practice_table(head, PRACTICE_L3, 7)

        n = self.narrate(
            id="practice_06",
            text="Level three, question seven: facing north, a person walks four kilometres, turns right and walks six, "
                 "turns right and walks four, then turns left and walks two. How far, and in which direction, from the "
                 "start?",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "seven")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "far")
        self.play(Indicate(rows[0], color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="practice_07",
            text="Question eight: facing north, a person walks seven kilometres, turns right and walks three, turns right "
                 "and walks three, then turns left and walks one. How far, in which direction, and which way is the person "
                 "facing?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "eight")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.at_word(n, "far")
        self.play(Indicate(rows[1], color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="practice_08",
            text="Question nine: a person walks four root two kilometres north-east, then four kilometres south. Where is "
                 "the person relative to the start?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "nine")
        self.play(FadeIn(rows[2], shift=RIGHT * 0.2))
        self.at_word(n, "Where")
        self.play(Indicate(rows[2], color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="practice_09",
            text="Pause once more and solve these three.",
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

        head = self.heading("Answer key  ·  1 to 5", GOOD)
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
            text="Two: the net is three north and zero east: three kilometres north.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "net")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "kilometres")
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_03",
            text="Three: ten minus four is six metres, south of the start.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "minus")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "six")
        self.play(FadeIn(rows[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_04",
            text="Four: three north and four east: five kilometres, north-east.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "north")
        self.play(FadeIn(rows[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "five")
        self.play(FadeIn(rows[3][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_05",
            text="Five: left from west is south, so twelve west and five south: thirteen kilometres, south-west.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "left")
        self.play(FadeIn(rows[4][:2], shift=RIGHT * 0.2))
        self.at_word(n, "thirteen")
        self.play(FadeIn(rows[4][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Answer key  ·  6 to 9", GOOD)
        table, rows = self.answer_table(head, ANSWERS_B, 6)

        n = self.narrate(
            id="answers_06",
            text="Six: east and west cancel: ten metres north.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "cancel")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "ten")
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_07",
            text="Seven: the net is zero north-south and eight east: eight kilometres east.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "net")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "kilometres")
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_08",
            text="Eight: the net is four north and four east, so four root two, about five point six six kilometres, "
                 "north-east; and the person is facing east.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "net")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "facing")
        self.play(FadeIn(rows[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_09",
            text="Nine: the north-east leg is four east and four north; then four south leaves four kilometres east.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "leg")
        self.play(FadeIn(rows[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "leaves")
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
            text="Recognise and move. The recognition cue: the words, how far from the starting point, or, in which "
                 "direction from.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "cue")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "words")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_lens_02",
            text="The target time: twenty-five seconds for two legs, thirty seconds for four.",
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
            text="The sanity check: the distance from the start can never exceed the total path walked.",
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
        points = VGroup(text("split every leg into north–south and east–west, and add each set", LABEL, INK, BOLD),
                        text("combine the two nets with Pythagoras", LABEL, INK, BOLD),
                        text("name the direction from the signs;  reverse it if the question measures from the end", LABEL, INK, BOLD))\
            .arrange(DOWN, buff=0.45, aligned_edge=LEFT)
        box = VGroup(pill("net N–S,  net E–W", GOOD, size=SMALL), pill("√(a² + b²)", GOOD, size=SMALL), pill("signs → direction", GOOD, size=SMALL),
                     pill("from the end:  reverse", GOOD, size=SMALL)).arrange(RIGHT, buff=0.3)
        self.stack(head, [points, box], buff=1.1, top=1.1)
        self.no_overlap(*points)
        self.no_overlap(*box)

        n = self.narrate(
            id="summary_01",
            text="Split every leg into north-south and east-west, add each set, and combine with Pythagoras.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "Split")
        self.play(FadeIn(points[0], shift=RIGHT * 0.2))
        self.at_word(n, "Pythagoras")
        self.play(FadeIn(points[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_02",
            text="Name the direction from the signs, and reverse it if the question measures from the end point.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "signs")
        self.play(FadeIn(points[2], shift=RIGHT * 0.2))
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
        rules = VGroup(pill("6 questions", WORD, size=BODY), pill("5 minutes", WORD, size=BODY), pill("+3 correct", GOOD, size=BODY),
                       pill("−1 wrong", BAD, size=BODY)).arrange(RIGHT, buff=0.4)
        gate = VGroup(VGroup(pill("15 or more out of 18", GOOD, size=LABEL), text("move on", BODY, GOOD, BOLD)).arrange(RIGHT, buff=0.5),
                      VGroup(pill("below 15", BAD, size=LABEL), text("replay the Traps segment, then retry", BODY, INK, BOLD)).arrange(RIGHT, buff=0.5))            .arrange(DOWN, buff=0.6, aligned_edge=LEFT)
        self.stack(head, [rules, gate], buff=1.1, top=1.1)
        self.no_overlap(*rules)
        self.no_overlap(*gate)

        n = self.narrate(
            id="section_quiz_01",
            text="Now the section quiz: six questions in five minutes, with plus three for a correct answer and minus one "
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
            text="Fifteen or more out of eighteen: move on. Below fifteen: replay the traps segment, then retry.",
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

        head = self.heading("Section quiz  ·  questions 4 to 6")
        table, rows = self.placed_table(head, ["#", "Question", "Options"],
                                        [[str(3 + i + 1)] + list(row) for i, row in enumerate(QUIZ[3:6])], [0.8, 7.6, 4.8], room=1.3)
        for row in rows:
            row[0].set_color(MUTED)

        n = self.narrate(
            id="section_quiz_05",
            text="And here are questions four, five and six.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "four")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "five")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.at_word(n, "six")
        self.play(FadeIn(rows[2], shift=RIGHT * 0.2))
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
        nxt = self.breadcrumb("Next", "Video 3 · Shadows & Renamed Directions")
        nxt.next_to(table, DOWN, buff=0.6)
        self.no_overlap(table, nxt)
        self.validator.check_in_frame(VGroup(head, table, nxt))

        n = self.narrate(
            id="section_quiz_07",
            text="The answers. One: right from south is west, so five south and twelve west: thirteen kilometres, "
                 "south-west: option b.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "right")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "option")
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="section_quiz_08",
            text="Two: north and south cancel, leaving four east: option a.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "cancel")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "option")
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="section_quiz_09",
            text="Three: the six, eight, ten triple: option d.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "triple")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "option")
        self.play(FadeIn(rows[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="section_quiz_10",
            text="Four: the net is four north and three east, so five kilometres, north-east: option a.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "net")
        self.play(FadeIn(rows[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "option")
        self.play(FadeIn(rows[3][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="section_quiz_11",
            text="Five: reverse north-west to get south-east: option c.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "reverse")
        self.play(FadeIn(rows[4][:2], shift=RIGHT * 0.2))
        self.at_word(n, "option")
        self.play(FadeIn(rows[4][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="section_quiz_12",
            text="Six: the south-east leg is three east and three south; then three north leaves three kilometres east: "
                 "option b.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "leg")
        self.play(FadeIn(rows[5][:2], shift=RIGHT * 0.2))
        self.at_word(n, "option")
        self.play(FadeIn(rows[5][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="section_quiz_13",
            text="Next: shadows and renamed directions.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Next")
        self.play(FadeIn(nxt, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S17_section_quiz")

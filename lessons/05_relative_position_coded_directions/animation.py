"""
animation.py for the LMS video generator.

Course : Pre-C-CAT - Section A - Logical Reasoning
Video  : Lesson 3 - Directions Sense Test - 05 - Relative Position & Coded Directions

Source script:
  C:\\Scripts\\Section A\\Reasoning_Scripts\\Sessions 1-4 - Coding-Decoding, Alphabets, Directions, Number Series, Odd Man Out\\Lesson 3 - Directions Sense Test\\05 - Relative Position & Coded Directions.pdf

Built on the golden-reference pattern:
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``;
  * layouts stacked with next_to and guarded with ``no_overlap``; nothing is
    ever animated onto or into another box.

Lesson 3, Video 4 of 6 (file 05 in its folder).
Not the first video: a silent breadcrumb, a one-line recap of Video 3, then today's topic.
The narration follows the script section by section and ends with the Section Quiz and its answer key.
Layouts are plotted to scale with north at the top; each point carries its coordinates, and the asked pair is joined by a dashed green line.
The direction codes (# north, $ east, @ south, & west, each 2 m) are shown again on every screen whose questions use them.
Every layout in the script was placed again from its statements in the data block and its distance and direction recomputed;
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

STEP = {"north": (0, 1), "east": (1, 0), "south": (0, -1), "west": (-1, 0)}
CODES = {"#": "north", "$": "east", "@": "south", "&": "west"}


def place(origin, *statements):
    """Coordinates from statements (A, d, direction, B) = "A is d m <direction> of B", starting from ``origin`` at (0, 0)."""
    at = {origin: (0, 0)}
    todo = list(statements)
    while todo:
        for s in todo:
            a, d, way, b = s
            dx, dy = STEP[way]
            if b in at and a not in at:
                at[a] = (at[b][0] + dx * d, at[b][1] + dy * d)
            elif a in at and b not in at:
                at[b] = (at[a][0] - dx * d, at[a][1] - dy * d)
            else:
                continue
            todo.remove(s)
            break
        else:
            raise ValueError(todo)
    return at


def decode(chain):
    """"A @ B & C" -> statements, each link 2 m."""
    parts = chain.split()
    return [(parts[i], 2, CODES[parts[i + 1]], parts[i + 2]) for i in range(0, len(parts) - 2, 2)]


def seen_from(at, a, b):
    """Where a is with respect to b: (dx, dy, distance, direction)."""
    dx, dy = at[a][0] - at[b][0], at[a][1] - at[b][1]
    name = ("north" if dy > 0 else "south" if dy < 0 else "") + ("-" if dx and dy else "") + ("east" if dx > 0 else "west" if dx < 0 else "")
    return dx, dy, round(_math.hypot(dx, dy), 4), name


ROOT8 = round(2 * _math.sqrt(2), 4)
# ---- hook, worked examples ----
RACKS = place("C", ("A", 3, "north", "B"), ("B", 4, "east", "C"))
assert RACKS == {"C": (0, 0), "B": (4, 0), "A": (4, 3)} and seen_from(RACKS, "A", "C") == (4, 3, 5, "north-east")
assert decode("A @ B & C") == [("A", 2, "south", "B"), ("B", 2, "west", "C")]
CODED = place("C", *decode("A @ B & C"))
assert CODED == {"C": (0, 0), "B": (-2, 0), "A": (-2, -2)} and seen_from(CODED, "A", "C") == (-2, -2, ROOT8, "south-west") and ROOT8 == 2.8284
# ---- exam patterns, traps, checkpoint, practice ----
PQR = place("Q", ("P", 6, "south", "Q"), ("R", 8, "east", "Q"))
assert PQR["P"] == (0, -6) and PQR["R"] == (8, 0) and seen_from(PQR, "P", "R") == (-8, -6, 10, "south-west")
assert seen_from(place("N", ("M", 5, "east", "N"), ("O", 5, "west", "N")), "M", "O") == (10, 0, 10, "east")
JKLM = place("L", ("J", 4, "north", "K"), ("K", 6, "east", "L"), ("M", 4, "north", "L"))
assert JKLM["J"] == (6, 4) and JKLM["M"] == (0, 4) and seen_from(JKLM, "J", "M") == (6, 0, 6, "east")
assert seen_from(place("C", ("A", 1, "north", "B"), ("B", 1, "west", "C")), "A", "C")[3] == "north-west"
FGHI = place("I", *decode("F # G $ H @ I"))
assert FGHI == {"I": (0, 0), "H": (0, -2), "G": (2, -2), "F": (2, 0)} and seen_from(FGHI, "F", "I") == (2, 0, 2, "east")
XYZ = place("Y", ("X", 4, "north", "Y"), ("Z", 3, "west", "Y"))
assert XYZ["X"] == (0, 4) and XYZ["Z"] == (-3, 0) and seen_from(XYZ, "X", "Z") == (3, 4, 5, "north-east")
QRS = place("R", ("Q", 8, "north", "R"), ("S", 6, "east", "R"))
assert seen_from(QRS, "S", "Q") == (6, -8, 10, "south-east")
RST = place("T", *decode("R & S # T"))
assert RST == {"T": (0, 0), "S": (0, 2), "R": (-2, 2)} and seen_from(RST, "T", "R") == (2, -2, ROOT8, "south-east")
# ---- section quiz ----
assert seen_from(place("C", ("A", 5, "north", "B"), ("B", 12, "west", "C")), "A", "C") == (-12, 5, 13, "north-west")
assert seen_from(place("Q", ("P", 4, "east", "Q"), ("R", 4, "north", "Q")), "P", "R")[:2] + seen_from(place("Q", ("P", 4, "east", "Q"), ("R", 4, "north", "Q")), "P", "R")[3:] == (4, -4, "south-east")
assert seen_from(place("R", *decode("P $ Q # R")), "P", "R") == (2, 2, ROOT8, "north-east")
assert seen_from(place("Z", *decode("X & Y @ Z")), "X", "Z") == (-2, -2, ROOT8, "south-west")

CODE_LINE = "#  north        $  east        @  south        &  west        each 2 m"
OBJECTIVES = [("Place points on a coordinate grid", "from statements like “A is 3 m north of B”"),
              ("Find the direction and distance", "between any two points"),
              ("Decode coded direction statements", "“P # Q means P is north of Q”, and solve them")]
FORMULAS = ["“A is d m north of B”:   from B, move d north to A",
            "Origin at a shared point;   east +x,   north +y",
            "Direction from the signs of (x, y);   distance  √(x² + y²)",
            "No distances given   →   the direction may be fixed, the distance cannot",
            "Coded symbols:   decode to plain statements first"]
PATTERNS_A = [["Two statements", "A 3 m north of B;   B 4 m east of C", "coordinates", "A is 5 m north-east of C"],
              ["Reverse view", "P 6 m south of Q;   R 8 m east of Q;   P from R?", "P (0, −6),  R (8, 0)", "10 m south-west"],
              ["In a line", "M 5 m east of N;   O 5 m west of N", "same row", "M is 10 m east of O"],
              ["Parallel offsets", "J 4 m north of K;   K 6 m east of L;   M 4 m north of L", "J (6, 4),  M (0, 4)", "J is 6 m east of M"]]
PATTERNS_B = [["No distances", "A north of B;   B west of C", "signs only", "north-west of C;  distance not fixed"],
              ["Coded, two links", "A @ B & C", "decode, then place", "A is 2√2 m south-west of C"],
              ["Coded, three links", "F # G $ H @ I", "F (2, 0) from I", "F is 2 m east of I"]]
TRAPS = [("Trap 1  ·  reading the statement backwards", "P is 6 m south of Q, and R is 8 m east of Q.   In which direction is P from R?",
          "Q placed south of P:  north-west", "P − R = (−8, −6):  south-west",
          "“A is north of B”:  start at B and move north to reach A"),
         ("Trap 2  ·  inventing a distance", "A is north of B, and B is west of C.   How far is A from C?",
          "picking an option such as 5 m", "only the direction is fixed:  north-west",
          "a distance needs numbers;  directions alone fix only the direction")]
PRACTICE_L1 = [("L1", "A is 3 m north of B, and B is 4 m east of C.  How far, and in which direction, is A from C?"),
               ("L1", "M is 5 m east of N, and O is 5 m west of N.  Where is M with respect to O?"),
               ("L1", "X is 4 m north of Y, and Z is 3 m west of Y.  Where is X with respect to Z?")]
PRACTICE_L2 = [["L2  ·  4", "P is 6 m south of Q, and R is 8 m east of Q.  Where is P with respect to R?"],
               ["L2  ·  5", "Q is 8 m north of R, and S is 6 m east of R.  Where is S with respect to Q?"],
               ["L2  ·  6", "If A @ B & C, where is A with respect to C?"]]
PRACTICE_L3 = [["L3  ·  7", "If F # G $ H @ I, where is F with respect to I?"],
               ["L3  ·  8", "If R & S # T, where is T with respect to R?"]]
ANSWERS_A = [("A (4, 3) from C (0, 0)", "5 m north-east"),
             ("M (5, 0),   O (−5, 0)", "10 m east"),
             ("X (0, 4),   Z (−3, 0)", "5 m north-east"),
             ("P (0, −6),   R (8, 0)", "10 m south-west")]
ANSWERS_B = [("Q (0, 8),   S (6, 0):    S − Q  =  (6, −8)", "10 m south-east"),
             ("A (−2, −2) from C", "2√2 m south-west"),
             ("I (0, 0),   H (0, −2),   G (2, −2),   F (2, 0)", "2 m east"),
             ("T (0, 0),   S (0, 2),   R (−2, 2):    T − R  =  (2, −2)", "2√2 m south-east")]
LENS = [("Recognition cue", "“is … m north of”,  “with respect to”,  or symbols defined as directions"),
        ("Target time", "30 seconds for two statements,  45 seconds for coded chains"),
        ("Sanity check", "swap the two points, and the direction must reverse exactly")]
QUIZ = [["A is 5 m north of B, and B is 12 m west of C.   How far, and in which direction, is A from C?",
         "(a) 17 m NW   (b) 13 m NE   (c) 13 m NW   (d) 7 m NW"],
        ["P is 4 m east of Q, and R is 4 m north of Q.   In which direction is P from R?",
         "(a) South-east   (b) North-east   (c) North-west   (d) South-west"],
        ["A is north of B, and B is east of C.   How far is A from C?", "(a) North-east   (b) 5 m   (c) 0 m   (d) Cannot be determined"],
        ["If P $ Q # R, where is P with respect to R?", "(a) 4 m NE   (b) 2√2 m NE   (c) 2√2 m SW   (d) 2 m east"],
        ["If X & Y @ Z, where is X with respect to Z?", "(a) 2√2 m SW   (b) 2√2 m NE   (c) 4 m SW   (d) 2 m south"]]
QUIZ_KEY = [("A (−12, 5) from C (0, 0)", "(c)  13 m NW"),
            ("P (4, 0) − R (0, 4)  =  (4, −4)", "(a)  South-east"),
            ("no distances are given", "(d)  Cannot be determined"),
            ("P (2, 2) from R (0, 0)", "(b)  2√2 m NE"),
            ("Z (0, 0),   Y (0, −2),   X (−2, −2)", "(a)  2√2 m SW")]


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


class RelativePositionAndCodedDirectionsVideo(LMSScene):
    lesson_title = "Relative Position & Coded Directions"

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

    def point_plot(self, points, links=(), ask=None, box=(4.2, 3.0), coords=True):
        """Points plotted to scale, north at the top.  points = [(name, x, y)]; links = [(i, j, tag)] are solid lines
        between points i and j; ask = (i, j) is the pair joined by the dashed line.
        Returns (dots, labels, link lines, link tags, dashed line (a group), north mark)."""
        xs, ys = [p[1] for p in points], [p[2] for p in points]
        k = min(box[0] / max(max(xs) - min(xs), 1e-6), box[1] / max(max(ys) - min(ys), 1e-6), 1.0)
        pos = [np.array([x * k, y * k, 0.0]) for _, x, y in points]
        mid = sum(pos) / len(pos)
        dots, labels = VGroup(), VGroup()
        for (name, x, y), p in zip(points, pos):
            dot = Dot(p, color=FOCUS, radius=0.1)
            away = p - mid
            corner = np.array([1.0 if away[0] >= -1e-6 else -1.0, 1.0 if away[1] >= -1e-6 else -1.0, 0.0])
            tag = f"{name} ({x:g}, {y:g})".replace("-", "−") if coords else name
            labels.add(text(tag, SMALL, INK, BOLD).next_to(dot, corner, buff=0.08))
            dots.add(dot)
        lines, tags = VGroup(), VGroup()
        for i, j, tag in links:
            lines.add(Line(pos[i], pos[j], color=WORD, stroke_width=4))
            along = (pos[j] - pos[i]) / np.linalg.norm(pos[j] - pos[i])
            side = np.array([-along[1], along[0], 0.0])
            centre = (pos[i] + pos[j]) / 2
            if np.dot(side, centre - mid) < 0:
                side = -side
            label = text(tag, SMALL, WORD, BOLD)
            label.move_to(centre + side * (0.2 + abs(side[0]) * label.width / 2 + abs(side[1]) * label.height / 2))
            tags.add(label)
        dash = VGroup(DashedLine(pos[ask[0]], pos[ask[1]], color=GOOD, stroke_width=4)) if ask else VGroup()
        north = VGroup(Arrow(ORIGIN, UP * 0.6, buff=0, color=MUTED, stroke_width=3), text("N", SMALL, MUTED, BOLD)).arrange(UP, buff=0.05)
        north.next_to(VGroup(dots, labels, tags), LEFT, buff=0.5, aligned_edge=UP)
        self.no_overlap(*labels, *tags, gap=0.02)
        return VGroup(dots, labels, lines, tags, dash, north)

    def code_key(self):
        """The four direction codes of this lesson, as one row."""
        key = VGroup(*[pill(s, c, size=SMALL) for s, c in [("#  north", WORD), ("$  east", RATIO), ("@  south", SECOND), ("&  west", GOOD)]],
                     text("each 2 m", SMALL, MUTED)).arrange(RIGHT, buff=0.35)
        self.no_overlap(*key)
        return key

    # ============================================== 0. INTRO ==========
    # Not the first video: silent breadcrumb, a one-line recap of the previous video, then today's topic.

    def intro(self):
        self.scene_start("S00_intro", title="Intro")

        crumb = self.breadcrumb("Logical Reasoning", "Lesson 3 · Directions Sense Test", "Video 4 of 6")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        recap = VGroup(text("from Video 3  ·  Shadows & Renamed Directions", SMALL, MUTED), pill("morning shadow W,  evening shadow E;   one rotation for all", WORD, size=LABEL)).arrange(DOWN, buff=0.25)
        title = fit_width(text("Relative Position & Coded Directions", TITLE, INK, BOLD), SAFE_W - 0.4)
        today = text("today: coordinate geometry in words", LABEL, FOCUS)
        block = VGroup(recap, title, today).arrange(DOWN, buff=0.7)
        fit_within(block, SAFE_W, SAFE_H - crumb.height - 0.9)
        block.next_to(crumb, DOWN, buff=0.7)
        self.no_overlap(crumb, recap, title, today)
        self.validator.check_in_frame(VGroup(crumb, block))

        n = self.narrate(
            id="intro_01",
            text="In the last video, morning shadows pointed west and evening shadows east, and a renamed direction was "
                 "one rotation applied to all.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.at_word(n, "shadows")
        self.play(FadeIn(recap[0]))
        self.at_word(n, "rotation")
        self.play(FadeIn(recap[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="intro_02",
            text="This video covers relative position and coded directions: coordinate geometry in words.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "covers")
        self.play(FadeIn(title, shift=UP * 0.1))
        self.at_word(n, "geometry")
        self.play(FadeIn(today, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_intro")

    # ============================================== 1. HOOK ==========

    def hook(self):
        self.scene_start("S01_hook", title="Hook")

        head = self.heading("A data-centre floor plan")
        plan = self.point_plot([("C", 0, 0), ("B", 4, 0), ("A", 4, 3)], links=[(1, 2, "3 m"), (0, 1, "4 m")], ask=(0, 2))
        said = VGroup(text("Rack A is 3 m north of Rack B", LABEL, INK), text("Rack B is 4 m east of Rack C", LABEL, INK)).arrange(DOWN, buff=0.2, aligned_edge=LEFT)
        ask = text("a cable from A to C:  how long, and in which direction?", SMALL, FOCUS, BOLD)
        answer = pill("5 m;   A is north-east of C", GOOD, size=LABEL)
        moral = text("relative position is coordinate geometry in words", SMALL, RATIO, BOLD)
        side = VGroup(said, ask, answer, moral).arrange(DOWN, buff=0.55)
        row = VGroup(plan, side).arrange(RIGHT, buff=0.8)
        self.stack(head, [row], top=0.9)
        self.no_overlap(plan, side)

        n = self.narrate(
            id="hook_01",
            text="On a data-centre floor plan, Rack A is three metres north of Rack B, and Rack B is four metres east of "
                 "Rack C.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "plan")
        self.play(FadeIn(plan[5]))
        self.at_word(n, "north")
        self.play(FadeIn(said[0], shift=RIGHT * 0.2))
        self.at_word(n, "east")
        self.play(FadeIn(said[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_02",
            text="A cable must run straight from A to C. How long, and in which direction?",
            voice="default",
            subtitle=True,
            pause_after=3.0,
        )
        self.at_word(n, "cable")
        self.play(FadeIn(ask, shift=UP * 0.1))
        self.at_word(n, "long")
        self.play(Indicate(ask, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="hook_03",
            text="Nobody walks here; there are no turns to track. Place C at the origin, B at four, zero, and A at four, "
                 "three.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "turns")
        self.play(Indicate(said, color=FOCUS, scale_factor=1.03))
        self.at_word(n, "origin")
        self.play(FadeIn(plan[0][0]), FadeIn(plan[1][0], shift=UP * 0.1))
        self.at_word(n, "B")
        self.play(FadeIn(plan[0][1]), FadeIn(plan[1][1], shift=UP * 0.1), FadeIn(plan[2][1], shift=UP * 0.1), FadeIn(plan[3][1], shift=UP * 0.1))
        self.at_word(n, "A")
        self.play(FadeIn(plan[0][2]), FadeIn(plan[1][2], shift=UP * 0.1), FadeIn(plan[2][0], shift=UP * 0.1), FadeIn(plan[3][0], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_04",
            text="The cable runs five metres, and A is north-east of C.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "five")
        self.play(Create(plan[4][0]))
        self.at_word(n, "north-east")
        self.play(FadeIn(answer, scale=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_05",
            text="Relative-position questions are coordinate geometry in words.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "geometry")
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
            text="One: place points on a coordinate grid from statements like, A is three metres north of B.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "place")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "statements")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="objectives_03",
            text="Two: find the direction and distance between any two points.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "direction")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "between")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="objectives_04",
            text="Three: decode coded direction statements, and solve them.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "decode")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "solve")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_objectives")

    # ============================================== 3. WHY THIS SECTION ==========

    def why_this_section(self):
        self.scene_start("S03_why_this_section", title="Why This Section")

        head = self.heading("Why this section")
        layout = pill("these questions describe a layout, not a walk", WORD, size=BODY)
        one = text("coordinates turn any chain of statements into a single subtraction", LABEL, GOOD, BOLD)
        self.stack(head, [layout, one], buff=1.2, top=1.5)

        n = self.narrate(
            id="why_this_section_01",
            text="Relative-position questions describe a layout, not a walk.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "layout")
        self.play(FadeIn(layout, scale=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="why_this_section_02",
            text="Coordinates turn any chain of statements into a single subtraction.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "subtraction")
        self.play(FadeIn(one, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_why_this_section")

    # ============================================== 4. THE CONCEPT JOURNEY ==========

    def concept_journey(self):
        self.scene_start("S04_concept_journey", title="The Concept Journey")

        head = self.heading("Steps 1 to 3  ·  read, fix an origin, place every point")
        plan = self.point_plot([("C", 0, 0), ("B", 4, 0), ("A", 4, 3)], links=[(1, 2, "3 m"), (0, 1, "4 m")], box=(3.8, 2.7))
        read = VGroup(pill("“A is 3 m north of B”", WORD, size=LABEL), text("start at B, move 3 m north to reach A", SMALL, INK, BOLD))\
            .arrange(DOWN, buff=0.18, aligned_edge=LEFT)
        origin = VGroup(pill("fix an origin", RATIO, size=LABEL), text("a point that appears in two statements, at (0, 0);  east +x,  north +y", SMALL, INK, BOLD))\
            .arrange(DOWN, buff=0.18, aligned_edge=LEFT)
        chain = VGroup(pill("place every point", GOOD, size=LABEL), text("chain the statements, writing coordinates as you go", SMALL, INK, BOLD))\
            .arrange(DOWN, buff=0.18, aligned_edge=LEFT)
        side = VGroup(read, origin, chain).arrange(DOWN, buff=0.5, aligned_edge=LEFT)
        row = VGroup(plan, side).arrange(RIGHT, buff=0.6)
        self.stack(head, [row], top=0.8)
        self.no_overlap(plan, side)
        go = Arrow(plan[0][1].get_center(), plan[0][2].get_center(), buff=0.14, color=WORD, stroke_width=5)

        n = self.narrate(
            id="concept_journey_01",
            text="Step one: read the statement correctly. A is three metres north of B places A relative to B: start at B, "
                 "and move three metres north to reach A.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "one")
        self.play(FadeIn(read[0], shift=UP * 0.1))
        self.at_word(n, "places")
        self.play(FadeIn(plan[0][1:]), FadeIn(plan[1][1:], shift=UP * 0.1), FadeIn(plan[5], shift=UP * 0.1))
        self.at_word(n, "move")
        self.play(FadeIn(read[1], shift=UP * 0.1), GrowArrow(go), FadeIn(plan[3][0]))
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_journey_02",
            text="Step two: fix an origin. Put one point, ideally one that appears in two statements, at zero, zero. East "
                 "is plus x, and north is plus y.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "two")
        self.play(FadeIn(origin[0], shift=UP * 0.1))
        self.at_word(n, "ideally")
        self.play(FadeIn(origin[1], shift=UP * 0.1))
        self.at_word(n, "East")
        self.play(Indicate(plan[5], color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_journey_03",
            text="Step three: place every point. Chain the statements, writing coordinates as you go.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "three")
        self.play(FadeIn(chain[0], shift=UP * 0.1))
        self.at_word(n, "Chain")
        self.play(FadeIn(chain[1], shift=UP * 0.1), FadeIn(plan[0][0]), FadeIn(plan[1][0], shift=UP * 0.1), FadeIn(plan[2][1], shift=UP * 0.1), FadeIn(plan[3][1], shift=UP * 0.1))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Steps 4 and 5  ·  compare two points;  missing distances")
        plan = self.point_plot([("C", 0, 0), ("B", 4, 0), ("A", 4, 3)], links=[(1, 2, "3 m"), (0, 1, "4 m")], ask=(0, 2), box=(3.8, 2.7))
        compare = VGroup(pill("compare two points:  subtract coordinates", FOCUS, size=LABEL), text("A − C  =  (4, 3)", LABEL, INK, BOLD),
                         text("the signs give the direction;  Pythagoras gives the distance", SMALL, INK)).arrange(DOWN, buff=0.2, aligned_edge=LEFT)
        missing = VGroup(pill("missing distances", BAD, size=LABEL), text("“north of” and “east of”:  the direction is still north-east", SMALL, INK, BOLD),
                         text("but the distance cannot be determined", SMALL, BAD, BOLD)).arrange(DOWN, buff=0.2, aligned_edge=LEFT)
        side = VGroup(compare, missing).arrange(DOWN, buff=0.7, aligned_edge=LEFT)
        row = VGroup(plan, side).arrange(RIGHT, buff=0.6)
        self.stack(head, [row], top=0.8)
        self.no_overlap(plan, side)

        n = self.narrate(
            id="concept_journey_04",
            text="Step four: compare two points. Subtract the coordinates. The signs give the direction, such as "
                 "north-east or south; Pythagoras gives the distance.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "four")
        self.play(FadeIn(plan[:4]), FadeIn(plan[5], shift=UP * 0.1), FadeIn(compare[0], shift=UP * 0.1))
        self.at_word(n, "Subtract")
        self.play(FadeIn(compare[1], shift=UP * 0.1), Create(plan[4][0]))
        self.at_word(n, "signs")
        self.play(FadeIn(compare[2], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_journey_05",
            text="Step five: missing distances. If the statements give directions without distances, the direction may "
                 "still be fixed: north of, and east of, gives north-east.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "five")
        self.play(FadeIn(missing[0], shift=UP * 0.1))
        self.at_word(n, "fixed")
        self.play(FadeIn(missing[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_journey_06",
            text="But the distance cannot be determined.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "cannot")
        self.play(FadeIn(missing[2], shift=UP * 0.1))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Step 6  ·  coded directions")
        said = pill("“P # Q  means  P is 2 m north of Q”", WORD, size=LABEL)
        key = self.code_key()
        how = VGroup(text("decode each symbol into a plain statement first", LABEL, INK, BOLD), text("then place the points exactly as before", LABEL, GOOD, BOLD))\
            .arrange(DOWN, buff=0.35)
        self.stack(head, [said, key, how], buff=1.0, top=1.1)

        n = self.narrate(
            id="concept_journey_07",
            text="Step six: coded directions. For example, P hash Q means P is two metres north of Q.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "six")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "hash")
        self.play(FadeIn(said, shift=UP * 0.1))
        self.at_word(n, "means")
        self.play(FadeIn(key, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_journey_08",
            text="Decode each symbol into a plain statement first, then place the points exactly as above.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Decode")
        self.play(FadeIn(how[0], shift=UP * 0.1))
        self.at_word(n, "place")
        self.play(FadeIn(how[1], shift=UP * 0.1))
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
            text="Here is the rule box. A is d metres north of B means: from B, move d north to A.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "box")
        self.play(FadeIn(box[0]))
        self.at_word(n, "means")
        self.play(FadeIn(lines[0], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="rule_box_02",
            text="Put the origin at a shared point, with east as plus x and north as plus y.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "origin")
        self.play(FadeIn(lines[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="rule_box_03",
            text="The direction comes from the signs, and the distance from Pythagoras.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "signs")
        self.play(FadeIn(lines[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="rule_box_04",
            text="With no distances given, the direction may be fixed, but the distance cannot.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "distances")
        self.play(FadeIn(lines[3], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="rule_box_05",
            text="And coded symbols are decoded to plain statements first.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "decoded")
        self.play(FadeIn(lines[4], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_rule_box")

    # ============================================== 6. SHORT TRICK ==========

    def short_trick(self):
        self.scene_start("S06_short_trick", title="Short Trick")

        head = self.heading("Short trick", RATIO)
        steps = VGroup(pill("put the shared point at (0, 0)", WORD, size=LABEL), pill("read “A is north of B” as “from B, go north to reach A”", RATIO, size=LABEL),
                       pill("subtract coordinates", GOOD, size=LABEL)).arrange(DOWN, buff=0.7)
        self.stack(head, [steps], top=1.2)
        self.no_overlap(*steps)

        n = self.narrate(
            id="short_trick_01",
            text="The short trick: put the shared point at zero, zero; read, A is north of B, as, from B, go north to "
                 "reach A; and subtract coordinates.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "shared")
        self.play(FadeIn(steps[0], shift=UP * 0.1))
        self.at_word(n, "read")
        self.play(FadeIn(steps[1], shift=UP * 0.1))
        self.at_word(n, "subtract")
        self.play(FadeIn(steps[2], shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_short_trick")

    # ============================================== 7. THE ANALOGY - A FLOOR PLAN ==========

    def analogy(self):
        self.scene_start("S07_analogy", title="The Analogy - A Floor Plan")

        head = self.heading("Relative position is a floor plan")
        plan = self.point_plot([("C", 0, 0), ("B", 4, 0), ("A", 4, 3)], links=[(1, 2, "3 m"), (0, 1, "4 m")], ask=(0, 2), box=(3.8, 2.7))
        one = text("once every object has coordinates,\nany distance or direction is one subtraction away", SMALL, INK)
        stops = VGroup(text("where the analogy stops", SMALL, BAD, BOLD), text("floor plans are drawn to scale", SMALL, INK),
                       text("in an exam you draw a rough sketch,\nand the coordinates do the measuring", SMALL, GOOD, BOLD)).arrange(DOWN, buff=0.14, aligned_edge=LEFT)
        side = VGroup(one, stops).arrange(DOWN, buff=0.8)
        row = VGroup(plan, side).arrange(RIGHT, buff=0.8)
        self.stack(head, [row], top=1.0)
        self.no_overlap(plan, side)

        n = self.narrate(
            id="analogy_01",
            text="Relative position is a floor plan: once every object has coordinates, any distance or direction is one "
                 "subtraction away.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "plan")
        self.play(FadeIn(plan[:4]), FadeIn(plan[5], shift=UP * 0.1))
        self.at_word(n, "coordinates")
        self.play(FadeIn(one, shift=UP * 0.1))
        self.at_word(n, "subtraction")
        self.play(Create(plan[4][0]))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_02",
            text="Where the analogy stops: floor plans are drawn to scale.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "stops")
        self.play(FadeIn(stops[0], shift=RIGHT * 0.2))
        self.at_word(n, "scale")
        self.play(FadeIn(stops[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_03",
            text="In an exam you draw a rough sketch, and the coordinates do the measuring.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "rough")
        self.play(FadeIn(stops[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S07_analogy")

    # ============================================== 8. WORKED EXAMPLE - CLOSING THE HOOK ==========

    def hook_solved(self):
        self.scene_start("S08_hook_solved", title="Worked Example - Closing the Hook")

        head = self.heading("Worked example: closing the hook")
        plan = self.point_plot([("C", 0, 0), ("B", 4, 0), ("A", 4, 3)], links=[(1, 2, "3 m"), (0, 1, "4 m")], ask=(0, 2))
        steps = self.solve_steps([("C at the origin", "(0, 0)"), ("B is 4 m east of C", "(4, 0)"), ("A is 3 m north of B", "(4, 3)"),
                                  ("A − C = (4, 3):   √(16 + 9)", "5 m north-east")])
        row = VGroup(plan, steps).arrange(RIGHT, buff=0.8)
        self.stack(head, [row], top=1.1)
        self.no_overlap(plan, steps)
        self.no_overlap(*steps)

        n = self.narrate(
            id="hook_solved_01",
            text="Put C at zero, zero.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "C")
        self.play(FadeIn(plan[0][0]), FadeIn(plan[1][0], shift=UP * 0.1), FadeIn(plan[5], shift=UP * 0.1), FadeIn(steps[0], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_solved_02",
            text="B is four metres east of C, so B is at four, zero.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "east")
        self.play(FadeIn(plan[0][1]), FadeIn(plan[1][1], shift=UP * 0.1), FadeIn(plan[2][1], shift=UP * 0.1), FadeIn(plan[3][1], shift=UP * 0.1), FadeIn(steps[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_solved_03",
            text="A is three metres north of B, so A is at four, three.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "north")
        self.play(FadeIn(plan[0][2]), FadeIn(plan[1][2], shift=UP * 0.1), FadeIn(plan[2][0], shift=UP * 0.1), FadeIn(plan[3][0], shift=UP * 0.1), FadeIn(steps[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_solved_04",
            text="A minus C is four, three: north and east, at a distance of the square root of sixteen plus nine, five "
                 "metres, north-east.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "minus")
        self.play(Create(plan[4][0]))
        self.at_word(n, "root")
        self.play(FadeIn(steps[3], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S08_hook_solved")

    # ============================================== 9. A SECOND WORKED EXAMPLE - CODED DIRECTIONS ==========

    def second_example(self):
        self.scene_start("S09_second_example", title="A Second Worked Example - Coded Directions")

        head = self.heading("A second worked example: coded directions")
        key = self.code_key()
        ask = pill("If  A @ B & C,  where is A with respect to C?", FOCUS, size=LABEL)
        plan = self.point_plot([("C", 0, 0), ("B", -2, 0), ("A", -2, -2)], links=[(1, 2, "2 m"), (0, 1, "2 m")], ask=(0, 2), box=(2.4, 2.4))
        steps = self.solve_steps([("decode:   A is 2 m south of B;   B is 2 m west of C", ""), ("place:   C (0, 0),   B (−2, 0),   A (−2, −2)", ""),
                                  ("A − C  =  (−2, −2)", "south-west,  2√2 m  ≈  2.83 m")])
        row = VGroup(plan, steps).arrange(RIGHT, buff=0.7)
        self.stack(head, [key, ask, row], buff=0.5, top=0.45)
        self.no_overlap(plan, steps)
        self.no_overlap(*steps)

        n = self.narrate(
            id="second_example_01",
            text="P hash Q means P is two metres north of Q; dollar means east; at means south; and the and sign means "
                 "west.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "hash")
        self.play(FadeIn(key[0]))
        self.at_word(n, "dollar")
        self.play(FadeIn(key[1]))
        self.at_word(n, "south")
        self.play(FadeIn(key[2]))
        self.at_word(n, "west")
        self.play(FadeIn(key[3:]))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_02",
            text="If A at B, and sign, C, where is A with respect to C?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "where")
        self.play(FadeIn(ask, scale=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_03",
            text="Step one, decode: A is two metres south of B, and B is two metres west of C.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "decode")
        self.play(FadeIn(steps[0][:2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_04",
            text="Step two, place: C at zero, zero; B at minus two, zero; and A at minus two, minus two.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "place")
        self.play(FadeIn(steps[1][:2], shift=RIGHT * 0.2), FadeIn(plan[:4]), FadeIn(plan[5], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_05",
            text="Step three: A minus C is minus two, minus two, which is south-west, at two root two metres, about two "
                 "point eight three.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "minus")
        self.play(Create(plan[4][0]))
        self.at_word(n, "south-west")
        self.play(FadeIn(steps[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S09_second_example")

    # ============================================== 10. EXAM PATTERNS - HOW THIS IS ASKED ==========

    def exam_patterns(self):
        self.scene_start("S10_exam_patterns", title="Exam Patterns - How This Is Asked")

        head = self.heading("Exam patterns  ·  plain statements")
        table, rows = self.placed_table(head, ["Pattern", "Example", "Method", "Answer"], PATTERNS_A, [2.4, 4.6, 2.9, 3.4], room=1.2)
        for row in rows:
            row[0].set_color(WORD)
            row[3].set_color(GOOD)

        n = self.narrate(
            id="exam_patterns_01",
            text="Exams ask this in seven ways.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "seven")
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_02",
            text="Two statements: A three metres north of B, and B four metres east of C. With coordinates, A is five "
                 "metres north-east of C.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "statements")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "coordinates")
        self.play(FadeIn(rows[0][2], shift=RIGHT * 0.2), FadeIn(rows[0][3], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_03",
            text="The reverse view: P six metres south of Q, and R eight metres east of Q. P from R is ten metres, "
                 "south-west.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "reverse")
        self.play(FadeIn(rows[1][:3], shift=RIGHT * 0.2))
        self.at_word(n, "ten")
        self.play(FadeIn(rows[1][3], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_04",
            text="In a line: M five metres east of N, and O five metres west of N. They are in the same row, so M is ten "
                 "metres east of O.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "line")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "row")
        self.play(FadeIn(rows[2][2], shift=RIGHT * 0.2), FadeIn(rows[2][3], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_05",
            text="Parallel offsets: J is at six, four, and M is at zero, four, so J is six metres east of M.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "offsets")
        self.play(FadeIn(rows[3][:3], shift=RIGHT * 0.2))
        self.at_word(n, "so")
        self.play(FadeIn(rows[3][3], shift=LEFT * 0.1))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Exam patterns  ·  no distances, and codes")
        ref = self.code_key()
        table, rows = self.table_under(head, ref, ["Pattern", "Example", "Method", "Answer"], PATTERNS_B, [2.6, 3.2, 3.0, 4.5])
        for row in rows:
            row[0].set_color(WORD)
            row[3].set_color(GOOD)

        n = self.narrate(
            id="exam_patterns_06",
            text="No distances: A north of B, and B west of C. From the signs only, A is north-west of C, and the distance "
                 "cannot be determined.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "distances")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "signs")
        self.play(FadeIn(rows[0][2], shift=RIGHT * 0.2))
        self.at_word(n, "cannot")
        self.play(FadeIn(rows[0][3], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_07",
            text="Coded, with two links: A at B, and sign, C. Decode, then place: A is two root two metres south-west of "
                 "C.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "links")
        self.play(FadeIn(ref), FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "Decode")
        self.play(FadeIn(rows[1][2], shift=RIGHT * 0.2), FadeIn(rows[1][3], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_08",
            text="Coded, with three links: F hash G, dollar H, at I. F is at two, zero from I, so F is two metres east of "
                 "I.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "three")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "zero")
        self.play(FadeIn(rows[2][2], shift=RIGHT * 0.2), FadeIn(rows[2][3], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S10_exam_patterns")

    # ============================================== 11. TRAPS AND CONFUSING QUESTIONS ==========

    def traps(self):
        self.scene_start("S11_traps", title="Traps and Confusing Questions")

        head, ask, wrong, right, rule = self.show_trap(TRAPS[0])

        n = self.narrate(
            id="traps_01",
            text="Trap one: reading the statement backwards.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "backwards")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_02",
            text="P is six metres south of Q, and R is eight metres east of Q. In which direction is P from R?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "south")
        self.play(FadeIn(ask, shift=UP * 0.1))
        self.at_word(n, "direction")
        self.play(Indicate(ask, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_03",
            text="The wrong instinct: placing Q south of P, which gives north-west.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "instinct")
        self.play(FadeIn(wrong, shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_04",
            text="Correct: P is at zero, minus six, and R is at eight, zero, so P minus R is minus eight, minus six: "
                 "south-west.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "minus")
        self.play(FadeIn(right, shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_05",
            text="The rule: A is north of B means you start at B and move north to reach A.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "means")
        self.play(FadeIn(rule, scale=1.03))
        self.wait_for_narration(n)
        self.clear_stage()

        head, ask, wrong, right, rule = self.show_trap(TRAPS[1])

        n = self.narrate(
            id="traps_06",
            text="Trap two: inventing a distance.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "inventing")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_07",
            text="A is north of B, and B is west of C. How far is A from C?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "north")
        self.play(FadeIn(ask, shift=UP * 0.1))
        self.at_word(n, "far")
        self.play(Indicate(ask, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_08",
            text="The wrong instinct: picking an option such as five metres.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "instinct")
        self.play(FadeIn(wrong, shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_09",
            text="Correct: without distances, only the direction, north-west, is fixed; the distance cannot be determined.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "only")
        self.play(FadeIn(right, shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_10",
            text="The rule: a distance needs numbers; directions alone fix only the direction.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "needs")
        self.play(FadeIn(rule, scale=1.03))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S11_traps")

    # ============================================== 12. CHECKPOINT ==========

    def checkpoint(self):
        self.scene_start("S12_checkpoint", title="Checkpoint")

        head = self.heading("Checkpoint  ·  your turn")
        ask = text("X is 4 m north of Y, and Z is 3 m west of Y.   Where is X with respect to Z?", LABEL, FOCUS, BOLD)
        plan = self.point_plot([("Y", 0, 0), ("X", 0, 4), ("Z", -3, 0)], links=[(0, 1, "4 m"), (0, 2, "3 m")], ask=(2, 1), box=(2.6, 3.0))
        work = VGroup(text("X − Z  =  (0, 4) − (−3, 0)  =  (3, 4)", LABEL, INK, BOLD), pill("5 m north-east", GOOD, size=BODY)).arrange(DOWN, buff=0.7)
        row = VGroup(plan, work).arrange(RIGHT, buff=1.0)
        self.stack(head, [ask, row], buff=0.6, top=0.6)
        self.no_overlap(plan, work)

        n = self.narrate(
            id="checkpoint_01",
            text="Your turn. X is four metres north of Y, and Z is three metres west of Y. Where is X with respect to Z?",
            voice="default",
            subtitle=True,
            pause_after=10.0,
        )
        self.at_word(n, "turn")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "north")
        self.play(FadeIn(ask, shift=UP * 0.1))
        self.at_word(n, "Where")
        self.play(Indicate(ask, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="checkpoint_02",
            text="Put Y at the origin: X is at zero, four, and Z is at minus three, zero.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "origin")
        self.play(FadeIn(plan[:4]), FadeIn(plan[5], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="checkpoint_03",
            text="X minus Z is three, four, so X is five metres north-east of Z.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "minus")
        self.play(FadeIn(work[0], shift=UP * 0.1), Create(plan[4][0]))
        self.at_word(n, "five")
        self.play(FadeIn(work[1], scale=1.03))
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
            text="Level one, question one: A is three metres north of B, and B is four metres east of C; how far, and in "
                 "which direction, is A from C? Question two: M is five metres east of N, and O is five metres west of N; "
                 "where is M with respect to O? Question three: X is four metres north of Y, and Z is three metres west of "
                 "Y; where is X with respect to Z?",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "north")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "M")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.at_word(n, "X")
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
        ref = self.code_key()
        table, rows = self.table_under(head, ref, ["Level", "Question"], PRACTICE_L2, [1.6, 11.0])
        for row in rows:
            row[0].set_color(RATIO)

        n = self.narrate(
            id="practice_03",
            text="Level two, question four: P is six metres south of Q, and R is eight metres east of Q; where is P with "
                 "respect to R? Question five: Q is eight metres north of R, and S is six metres east of R; where is S "
                 "with respect to Q?",
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
            id="practice_04",
            text="Question six uses the codes shown: if A at B, and sign, C, where is A with respect to C?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "six")
        self.play(FadeIn(rows[2], shift=RIGHT * 0.2))
        self.at_word(n, "codes")
        self.play(FadeIn(ref))
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
        ref = self.code_key()
        table, rows = self.table_under(head, ref, ["Level", "Question"], PRACTICE_L3, [1.6, 11.0])
        for row in rows:
            row[0].set_color(BAD)

        n = self.narrate(
            id="practice_06",
            text="Level three, with the same codes. Question seven: if F hash G, dollar H, at I, where is F with respect "
                 "to I? Question eight: if R and sign S, hash T, where is T with respect to R?",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "codes")
        self.play(FadeIn(ref))
        self.at_word(n, "seven")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "eight")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="practice_07",
            text="Pause once more and solve these two.",
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
            text="One: A is at four, three from C: five metres, north-east.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "three")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "five")
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_02",
            text="Two: M is at five, zero and O at minus five, zero: ten metres east.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "zero")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "ten")
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_03",
            text="Three: X is at zero, four and Z at minus three, zero: five metres, north-east.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "zero")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "five")
        self.play(FadeIn(rows[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_04",
            text="Four: P is at zero, minus six and R at eight, zero: ten metres, south-west.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "zero")
        self.play(FadeIn(rows[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "ten")
        self.play(FadeIn(rows[3][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Answer key  ·  5 to 8", GOOD)
        table, rows = self.answer_table(head, ANSWERS_B, 5)

        n = self.narrate(
            id="answers_05",
            text="Five: Q is at zero, eight and S at six, zero, so S minus Q is six, minus eight: ten metres, south-east.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "zero")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "ten")
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_06",
            text="Six: A is at minus two, minus two from C: two root two metres, south-west.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "minus")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "root")
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_07",
            text="Seven: I at the origin, H at zero, minus two, G at two, minus two, and F at two, zero: two metres east.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "origin")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "metres")
        self.play(FadeIn(rows[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_08",
            text="Eight: T at the origin, S at zero, two, and R at minus two, two, so T minus R is two, minus two: two "
                 "root two metres, south-east.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "origin")
        self.play(FadeIn(rows[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "root")
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
            text="Recognise and move. The recognition cue: the words, is so many metres north of, or, with respect to, or "
                 "symbols defined as directions.",
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
            text="The target time: thirty seconds for two statements, forty-five seconds for coded chains.",
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
            text="The sanity check: swap the two points, and the direction must reverse exactly.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "sanity")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "swap")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S15_exam_lens")

    # ============================================== 16. QUICK REVISION AND SUMMARY ==========

    def summary(self):
        self.scene_start("S16_summary", title="Quick Revision and Summary")

        head = self.heading("Quick revision")
        points = VGroup(text("fix an origin;  place each point by reading “A is north of B” from B to A", LABEL, INK, BOLD),
                        text("subtract coordinates:  signs → direction,  Pythagoras → distance", LABEL, INK, BOLD),
                        text("decode coded symbols first", LABEL, INK, BOLD),
                        text("without distances:  the direction may be fixed, the distance cannot be", LABEL, BAD, BOLD))\
            .arrange(DOWN, buff=0.4, aligned_edge=LEFT)
        box = VGroup(pill("from B to A", GOOD, size=SMALL), pill("origin at a shared point", GOOD, size=SMALL), pill("signs and Pythagoras", GOOD, size=SMALL),
                     pill("decode first", GOOD, size=SMALL)).arrange(RIGHT, buff=0.3)
        self.stack(head, [points, box], buff=0.9, top=0.9)
        self.no_overlap(*points)
        self.no_overlap(*box)

        n = self.narrate(
            id="summary_01",
            text="Fix an origin, place each point by reading, A is north of B, from B to A, and subtract coordinates.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "origin")
        self.play(FadeIn(points[0], shift=RIGHT * 0.2))
        self.at_word(n, "subtract")
        self.play(FadeIn(points[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_02",
            text="Decode coded symbols first.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Decode")
        self.play(FadeIn(points[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_03",
            text="Without distances, the direction may be fixed, but the distance cannot be.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Without")
        self.play(FadeIn(points[3], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_04",
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
        ref = self.code_key()
        table, rows = self.table_under(head, ref, ["#", "Question", "Options"],
                                       [[str(3 + i + 1)] + list(row) for i, row in enumerate(QUIZ[3:5])], [0.8, 7.6, 4.8])
        for row in rows:
            row[0].set_color(MUTED)

        n = self.narrate(
            id="section_quiz_05",
            text="And here are questions four and five.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(ref), FadeIn(table[0]))
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
        nxt = self.breadcrumb("Next", "Video 5 · Two Movers & Clock Directions")
        nxt.next_to(table, DOWN, buff=0.6)
        self.no_overlap(table, nxt)
        self.validator.check_in_frame(VGroup(head, table, nxt))

        n = self.narrate(
            id="section_quiz_07",
            text="The answers. One: A is at minus twelve, five from C, so thirteen metres, north-west: option c.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "minus")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "option")
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="section_quiz_08",
            text="Two: P minus R is four, minus four, which is south-east: option a.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "minus")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "option")
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="section_quiz_09",
            text="Three: no distances are given, so it cannot be determined: option d.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "distances")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "option")
        self.play(FadeIn(rows[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="section_quiz_10",
            text="Four: P is at two, two from R, so two root two metres, north-east: option b.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "from")
        self.play(FadeIn(rows[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "option")
        self.play(FadeIn(rows[3][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="section_quiz_11",
            text="Five: Z at the origin, Y at zero, minus two, and X at minus two, minus two: two root two metres, "
                 "south-west: option a.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "origin")
        self.play(FadeIn(rows[4][:2], shift=RIGHT * 0.2))
        self.at_word(n, "option")
        self.play(FadeIn(rows[4][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="section_quiz_12",
            text="Next: two movers and clock directions.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Next")
        self.play(FadeIn(nxt, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S17_section_quiz")

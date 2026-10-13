"""
animation.py for the LMS video generator.

Course : Pre-C-CAT - Section A - Logical Reasoning
Video  : Lesson 3 - Directions Sense Test - 02 - Directions & Turns

Source script:
  C:\\Scripts\\Section A\\Reasoning_Scripts\\Sessions 1-4 - Coding-Decoding, Alphabets, Directions, Number Series, Odd Man Out\\Lesson 3 - Directions Sense Test\\02 - Directions & Turns.pdf

Built on the golden-reference pattern:
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``;
  * layouts stacked with next_to and guarded with ``no_overlap``; nothing is
    ever animated onto or into another box.

Lesson 3, Video 1 of 6 (file 02 in its folder; file 01 is the Pre-Lesson Brief, which is reading material).
First video of the lesson: a silent breadcrumb, "Now we start lesson three", a one-line recap of Lesson 2, then today's topic.
The narration follows the script section by section and ends with the Section Quiz and its answer key.
A compass with a facing arrow is used throughout; the arrow really turns (clockwise for right, anticlockwise for left).
Every facing direction in the script was recomputed in the data block as a heading from north; all of them are correct.
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

POINTS = ["north", "north-east", "east", "south-east", "south", "south-west", "west", "north-west"]
COMPASS_POINTS = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
TURN_DEGREES = {"right": 90, "left": -90, "around": 180}


def heading(name):
    return POINTS.index(name) * 45


def face(start, *turns):
    """Facing direction after the turns: "right", "left", "around", or degrees (clockwise positive)."""
    total = heading(start) + sum(TURN_DEGREES.get(t, t) for t in turns)
    return POINTS[(total % 360) // 45]


HOOK_TURNS = ["RIGHT", "RIGHT", "LEFT", "RIGHT", "RIGHT"]
# ---- hook, worked examples ----
assert face("north", *[t.lower() for t in HOOK_TURNS]) == "west" and 4 * 90 - 90 == 270 == heading("west")
assert [face("north", *[t.lower() for t in HOOK_TURNS[:k]]) for k in range(1, 6)] == ["east", "south", "east", "south", "west"]
assert face("west", 45) == "north-west" and face("west", 45, "around") == "south-east" and (315 + 180) % 360 == 135
assert face("west", 45, "around", -90) == "north-east" and (270 + 45 + 180 - 90) % 360 == 45
# ---- concept steps, exam patterns, traps, checkpoint, practice ----
assert face("south", "right") == "west" and face("south", "left") == "east" and face("north", *["right"] * 4) == "north"
assert face("north", 135) == "south-east" and face("north", "around") == "south" and face("north-east", "around") == "south-west"
assert face("west", "left") == "south" and face("north", "right", "right", "left") == "east" and face("east", "left", "left", "left") == "south"
assert face("north-east", 90) == "south-east" and face("south", -135) == "north-east"
assert face("north", "right") == "east" and face("south", "around") == "north"
# ---- section quiz ----
assert face("east", "right", "right", "right", "left") == "west" and face("north", 225) == "south-west" and face("west", -45) == "south-west"
assert face("south-east", "right", "around") == "north-east" and (135 + 90 + 180) % 360 == 45

OBJECTIVES = [("Name the 8 directions", "and their angles from north"),
              ("Find the facing direction", "after any sequence of left and right turns"),
              ("Handle turns given in degrees", "45°,  90°,  135°,  180°")]
FORMULAS = ["N 0°,   NE 45°,   E 90°,   SE 135°,   S 180°,   SW 225°,   W 270°,   NW 315°",
            "Right  =  +90°  (clockwise);        left  =  −90°  (anticlockwise)",
            "Net turn  =  the sum of all turns;   reduce by 360°",
            "Facing south:   right = west,   left = east",
            "About turn  =  180°"]
PATTERNS = [("One turn", "facing west, turns left", "270° − 90°", "south"),
            ("Several turns", "facing north:  right, right, left", "net +90°", "east"),
            ("Same turn repeated", "facing east:  left three times", "−270°  →  +90°", "south"),
            ("Angle turn", "facing north-east,  90° clockwise", "45° + 90°", "south-east"),
            ("Anticlockwise angle", "facing south,  135° anticlockwise", "180° − 135°", "north-east")]
TRAPS = [("Trap 1  ·  the south flip", "A person faces south and turns left.   Which way does the person face?",
          "west, as “left is west” on a map", "facing south, left is east",
          "left and right belong to the person, not to the page"),
         ("Trap 2  ·  clockwise from the wrong side", "Facing north, a person turns 135° clockwise.   Which way?",
          "south-west", "0° + 135°  =  south-east",
          "clockwise from north passes through east first:  N, NE, E, SE")]
PRACTICE_A = [("L1", "A person faces north and turns right.  Which way does the person face?"),
              ("L1", "A person faces west and turns left.  Which way does the person face?"),
              ("L1", "A person faces south and turns around.  Which way does the person face?"),
              ("L2", "A person faces north and turns right, right, then left.  Which way does the person face?"),
              ("L2", "A person faces east and turns left three times.  Which way does the person face?"),
              ("L2", "A person faces north-east and turns 90° clockwise.  Which way does the person face?")]
PRACTICE_B = [("L3", "A person faces south and turns 135° anticlockwise.  Which way does the person face?"),
              ("L3", "A person faces west, turns 45° clockwise, turns around, then turns 90° anticlockwise.  Which way does the person face?")]
ANSWERS_A = [("0° + 90°", "east"),
             ("270° − 90°  =  180°", "south"),
             ("180° + 180°", "north"),
             ("net +90°", "east")]
ANSWERS_B = [("90° − 270°  =  −180°   →   180°", "south"),
             ("45° + 90°  =  135°", "south-east"),
             ("180° − 135°  =  45°", "north-east"),
             ("270° + 45° + 180° − 90°  =  405°   →   45°", "north-east")]
LENS = [("Recognition cue", "“turns left / right”, “clockwise”, “turns around”, “which direction is he facing”"),
        ("Target time", "15 seconds"),
        ("Sanity check", "equal numbers of rights and lefts always return you to the starting direction")]
QUIZ = [["Facing east:  right, right, right, then left.   Which way now?", "(a) North   (b) South   (c) West   (d) East"],
        ["A person faces south and turns left.   Which way now?", "(a) East   (b) West   (c) North   (d) South"],
        ["A person faces north and turns 225° clockwise.   Which way now?", "(a) South-east   (b) North-east   (c) West   (d) South-west"],
        ["A person faces west and turns 45° anticlockwise.   Which way now?", "(a) North-west   (b) South-west   (c) South   (d) North"],
        ["Facing south-east:  turns right, then turns around.   Which way now?",
         "(a) South-west   (b) North-west   (c) North-east   (d) South-east"]]
QUIZ_KEY = [("net +2:   east + 180°  =  west", "(c)  West"),
            ("facing south, left is east", "(a)  East"),
            ("0° + 225°", "(d)  South-west"),
            ("270° − 45°  =  225°", "(b)  South-west"),
            ("135° + 90° + 180°  =  405°   →   45°", "(c)  North-east")]


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


class DirectionsAndTurnsVideo(LMSScene):
    lesson_title = "Directions & Turns"

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

    def compass(self, radius=1.6, angles=True):
        """An 8-point compass.  Returns (ring, ticks, labels); labels[i] is the i-th point clockwise from north."""
        ring = Circle(radius=radius, color=MUTED, stroke_width=2.5)
        ticks, labels = VGroup(), VGroup()
        for i, name in enumerate(COMPASS_POINTS):
            a = i * 45 * DEGREES
            d = np.array([math.sin(a), math.cos(a), 0.0])
            ticks.add(Line(d * (radius - 0.12), d * (radius + 0.12), color=MUTED, stroke_width=3))
            label = VGroup(text(name, LABEL, FOCUS if i % 2 == 0 else INK, BOLD))
            if angles:
                label.add(text(f"{i * 45}°", MIN_FONT, MUTED))
                label.arrange(DOWN, buff=0.06)
            label.move_to(d * (radius + (0.66 if angles else 0.48)))
            labels.add(label)
        self.no_overlap(*labels, gap=0.02)
        return VGroup(ring, ticks, labels)

    def needle(self, comp, heading_deg, color=GOOD):
        """A facing arrow from the centre of a placed compass (heading in degrees clockwise from north)."""
        a = heading_deg * DEGREES
        centre, reach = comp[0].get_center(), comp[0].width / 2 * 0.84
        return Arrow(centre, centre + np.array([math.sin(a), math.cos(a), 0.0]) * reach, buff=0, color=color, stroke_width=7,
                     max_tip_length_to_length_ratio=0.22)

    def turn(self, comp, needle, degrees, run_time=1.0):
        """Animation: turn the facing arrow clockwise by ``degrees`` (negative = anticlockwise)."""
        return Rotate(needle, angle=-degrees * DEGREES, about_point=comp[0].get_center(), run_time=run_time)

    # ============================================== 0. INTRO ==========
    # First video of the lesson: silent breadcrumb, the lesson announcement, a recap of the previous lesson, then today's topic.

    def intro(self):
        self.scene_start("S00_intro", title="Intro")

        crumb = self.breadcrumb("Logical Reasoning", "Lesson 3 · Directions Sense Test", "Video 1 of 6")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        lesson = pill("Lesson 3  ·  Directions Sense Test", RATIO, size=LABEL)
        recap = VGroup(text("from Lesson 2  ·  Alphabets", SMALL, MUTED),
                       fit_width(VGroup(pill("from the right = 27 − from the left", WORD, size=LABEL), pill("classify once, then scan", GOOD, size=LABEL)).arrange(RIGHT, buff=0.4), SAFE_W - 0.6)).arrange(DOWN, buff=0.25)
        title = fit_width(text("Directions & Turns", TITLE, INK, BOLD), SAFE_W - 0.4)
        today = text("today: track any sequence of turns", LABEL, FOCUS)
        block = VGroup(lesson, recap, title, today).arrange(DOWN, buff=0.55)
        fit_within(block, SAFE_W, SAFE_H - crumb.height - 0.9)
        block.next_to(crumb, DOWN, buff=0.6)
        self.no_overlap(crumb, lesson, recap, title, today)
        self.no_overlap(*recap[1])
        self.validator.check_in_frame(VGroup(crumb, block))

        n = self.narrate(
            id="intro_01",
            text="Now we start lesson three: the directions sense test.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.at_word(n, "three")
        self.play(FadeIn(lesson, scale=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="intro_02",
            text="In lesson two, alphabets, a position from the right was twenty-seven minus the position from the left, "
                 "and a mixed sequence was classified once, then scanned.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "minus")
        self.play(FadeIn(recap[0]), FadeIn(recap[1][0], shift=UP * 0.1))
        self.at_word(n, "classified")
        self.play(FadeIn(recap[1][1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="intro_03",
            text="This first video covers directions and turns: how to track any sequence of turns.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "covers")
        self.play(FadeIn(title, shift=UP * 0.1))
        self.at_word(n, "track")
        self.play(FadeIn(today, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_intro")

    # ============================================== 1. HOOK ==========

    def hook(self):
        self.scene_start("S01_hook", title="Hook")

        head = self.heading("A drone and five commands")
        comp = self.compass(angles=False)
        chips = VGroup(*[pill(c, GOOD if c == "RIGHT" else BAD, size=SMALL) for c in HOOK_TURNS]).arrange(RIGHT, buff=0.2)
        ask = text("the drone faces north:  which way does it face now?", LABEL, INK)
        cancel = text("one left cancels one right:  three rights remain", LABEL, RATIO, BOLD)
        net = pill("3 × 90°  =  270° clockwise from north", FOCUS, size=LABEL)
        west = pill("the drone faces west", GOOD, size=LABEL)
        side = VGroup(chips, ask, cancel, net, west).arrange(DOWN, buff=0.45)
        row = VGroup(comp, side).arrange(RIGHT, buff=0.7)
        self.stack(head, [row], top=0.5)
        self.no_overlap(comp, side)
        self.no_overlap(*chips)
        needle = self.needle(comp, 0)

        n = self.narrate(
            id="hook_01",
            text="A drone faces north and receives five commands: right, right, left, right, right. Which way does it face "
                 "now?",
            voice="default",
            subtitle=True,
            pause_after=3.0,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "drone")
        self.play(FadeIn(comp), FadeIn(needle, shift=UP * 0.1))
        self.at_word(n, "commands")
        self.play(FadeIn(chips, shift=UP * 0.1))
        self.at_word(n, "Which")
        self.play(FadeIn(ask, shift=UP * 0.1))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="hook_02",
            text="You could rotate it five times in your head.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "rotate")
        self.play(Indicate(chips, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_03",
            text="Or notice that one left cancels one right, leaving three rights: two hundred and seventy degrees "
                 "clockwise from north.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "cancels")
        self.play(VGroup(chips[1], chips[2]).animate.set_opacity(0.3), FadeIn(cancel, shift=UP * 0.1))
        self.at_word(n, "degrees")
        self.play(FadeIn(net, shift=UP * 0.1), self.turn(comp, needle, 270, run_time=2.0))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_04",
            text="The drone faces west.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "west")
        self.play(FadeIn(west, scale=1.03), comp[2][6].animate.set_color(FOCUS))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_05",
            text="Today you learn to track any sequence of turns without losing your bearings.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "track")
        self.play(Indicate(comp[2], color=FOCUS, scale_factor=1.03))
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
            text="One: name the eight directions and their angles from north.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "name")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "angles")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="objectives_03",
            text="Two: find the facing direction after any sequence of left and right turns.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "facing")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "sequence")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="objectives_04",
            text="Three: handle turns given in degrees.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "handle")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "degrees")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_objectives")

    # ============================================== 3. WHY THIS SECTION ==========

    def why_this_section(self):
        self.scene_start("S03_why_this_section", title="Why This Section")

        head = self.heading("Why this section")
        fact = pill("every direction question starts with one fact:  which way is the person facing?", WORD, size=LABEL)
        rest = text("get that right, and the rest is arithmetic", BODY, GOOD, BOLD)
        self.stack(head, [fact, rest], buff=1.2, top=1.5)

        n = self.narrate(
            id="why_this_section_01",
            text="Every direction question starts with one fact: which way the person is facing.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "fact")
        self.play(FadeIn(fact, scale=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="why_this_section_02",
            text="Get that right, and the rest is arithmetic.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "arithmetic")
        self.play(FadeIn(rest, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_why_this_section")

    # ============================================== 4. THE CONCEPT JOURNEY ==========

    def concept_journey(self):
        self.scene_start("S04_concept_journey", title="The Concept Journey")

        head = self.heading("Step 1  ·  eight directions, clockwise")
        comp = self.compass()
        facts = VGroup(pill("8 directions, clockwise", FOCUS, size=LABEL), text("N,  NE,  E,  SE,  S,  SW,  W,  NW", BODY, INK, BOLD),
                       text("each 45° apart", LABEL, RATIO, BOLD), text("measure every direction as an angle\nclockwise from north", SMALL, MUTED))\
            .arrange(DOWN, buff=0.5)
        row = VGroup(comp, facts).arrange(RIGHT, buff=0.9)
        self.stack(head, [row], top=0.45)
        self.no_overlap(comp, facts)

        n = self.narrate(
            id="concept_journey_01",
            text="Step one: eight directions, clockwise: north, north-east, east, south-east, south, south-west, west and "
                 "north-west, each forty-five degrees apart.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "one")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "eight")
        self.play(FadeIn(comp[:2]), FadeIn(facts[0], shift=UP * 0.1))
        self.at_word(n, "north")
        self.play(FadeIn(comp[2]), FadeIn(facts[1], shift=UP * 0.1))
        self.at_word(n, "apart")
        self.play(FadeIn(facts[2], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_journey_02",
            text="Measure every direction as an angle clockwise from north.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "angle")
        self.play(FadeIn(facts[3], shift=UP * 0.1))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Steps 2 and 3  ·  right, left, and the south flip")
        comp = self.compass(angles=False)
        turns = VGroup(pill("right  =  clockwise 90°", GOOD, size=LABEL), pill("left  =  anticlockwise 90°", BAD, size=LABEL))\
            .arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        rel = text("always relative to where the person faces, not to the page", SMALL, MUTED)
        flip = VGroup(pill("the south flip", RATIO, size=LABEL), text("facing south:  right hand → west,  left hand → east", SMALL, INK, BOLD),
                      text("this is where most errors happen", SMALL, BAD, BOLD)).arrange(DOWN, buff=0.22, aligned_edge=LEFT)
        side = VGroup(turns, rel, flip).arrange(DOWN, buff=0.5, aligned_edge=LEFT)
        row = VGroup(comp, side).arrange(RIGHT, buff=0.8)
        self.stack(head, [row], top=0.5)
        self.no_overlap(comp, side)
        needle = self.needle(comp, 0)

        n = self.narrate(
            id="concept_journey_03",
            text="Step two: right is clockwise ninety degrees. Left is anticlockwise ninety degrees.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "two")
        self.play(FadeIn(comp), FadeIn(needle, shift=UP * 0.1))
        self.at_word(n, "right")
        self.play(FadeIn(turns[0], shift=UP * 0.1), self.turn(comp, needle, 90))
        self.at_word(n, "Left")
        self.play(FadeIn(turns[1], shift=UP * 0.1), self.turn(comp, needle, -90))
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_journey_04",
            text="This is always relative to where the person currently faces, not to the page.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "relative")
        self.play(FadeIn(rel, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_journey_05",
            text="Step three: the south flip. Facing south, your right hand points west, and your left hand points east.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "flip")
        self.play(FadeIn(flip[0], shift=UP * 0.1), self.turn(comp, needle, 180))
        self.at_word(n, "right")
        self.play(FadeIn(flip[1], shift=UP * 0.1), comp[2][6].animate.set_color(FOCUS))
        self.at_word(n, "left")
        self.play(comp[2][2].animate.set_color(FOCUS))
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_journey_06",
            text="This is where most errors happen.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "errors")
        self.play(FadeIn(flip[2], shift=UP * 0.1))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Steps 4 to 6  ·  net turns, angle turns, the about turn")
        comp = self.compass()
        net = VGroup(pill("net turns", WORD, size=LABEL), text("rights +90°,  lefts −90°:  add them, apply once", SMALL, INK, BOLD),
                     text("four rights (or four lefts) bring you back to the start", SMALL, MUTED)).arrange(DOWN, buff=0.16, aligned_edge=LEFT)
        angle = VGroup(pill("angle turns", RATIO, size=LABEL), text("135° clockwise  =  three 45° steps clockwise", SMALL, INK, BOLD))\
            .arrange(DOWN, buff=0.16, aligned_edge=LEFT)
        about = VGroup(pill("about turn", SECOND, size=LABEL), text("turning around is 180°:   N ↔ S,   E ↔ W,   NE ↔ SW", SMALL, INK, BOLD))\
            .arrange(DOWN, buff=0.16, aligned_edge=LEFT)
        side = VGroup(net, angle, about).arrange(DOWN, buff=0.5, aligned_edge=LEFT)
        row = VGroup(comp, side).arrange(RIGHT, buff=0.7)
        self.stack(head, [row], top=0.45)
        self.no_overlap(comp, side)
        needle = self.needle(comp, 0)

        n = self.narrate(
            id="concept_journey_07",
            text="Step four: net turns. Count rights as plus ninety degrees and lefts as minus ninety, add them, and apply "
                 "once.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "four")
        self.play(FadeIn(comp), FadeIn(needle, shift=UP * 0.1))
        self.at_word(n, "net")
        self.play(FadeIn(net[0], shift=UP * 0.1))
        self.at_word(n, "add")
        self.play(FadeIn(net[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_journey_08",
            text="Four rights, or four lefts, bring you back to the start.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "back")
        self.play(FadeIn(net[2], shift=UP * 0.1), self.turn(comp, needle, 360, run_time=1.6))
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_journey_09",
            text="Step five: angle turns. One hundred and thirty-five degrees clockwise means three forty-five degree "
                 "steps clockwise around the compass.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "angle")
        self.play(FadeIn(angle[0], shift=UP * 0.1))
        self.at_word(n, "steps")
        self.play(FadeIn(angle[1], shift=UP * 0.1), self.turn(comp, needle, 135, run_time=1.4))
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_journey_10",
            text="Step six: the about turn. Turning around is one hundred and eighty degrees: north to south, east to "
                 "west, north-east to south-west.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "about")
        self.play(FadeIn(about[0], shift=UP * 0.1))
        self.at_word(n, "Turning")
        self.play(FadeIn(about[1], shift=UP * 0.1), self.turn(comp, needle, 180, run_time=1.2))
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
            text="Here is the rule box. The eight headings: north is zero, then forty-five degrees more for each point "
                 "clockwise.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "box")
        self.play(FadeIn(box[0]))
        self.at_word(n, "headings")
        self.play(FadeIn(lines[0], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="rule_box_02",
            text="Right is plus ninety degrees, clockwise; left is minus ninety, anticlockwise.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "plus")
        self.play(FadeIn(lines[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="rule_box_03",
            text="The net turn is the sum of all turns, reduced by three hundred and sixty degrees.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "sum")
        self.play(FadeIn(lines[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="rule_box_04",
            text="Facing south, right is west and left is east.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "south")
        self.play(FadeIn(lines[3], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="rule_box_05",
            text="And an about turn is one hundred and eighty degrees.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "about")
        self.play(FadeIn(lines[4], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_rule_box")

    # ============================================== 6. SHORT TRICK ==========

    def short_trick(self):
        self.scene_start("S06_short_trick", title="Short Trick")

        head = self.heading("Short trick", RATIO)
        score = VGroup(pill("each right  =  +1", GOOD, size=BODY), pill("each left  =  −1", BAD, size=BODY)).arrange(RIGHT, buff=0.6)
        add = text("add them, and make that many quarter-turns clockwise", BODY, INK, BOLD)
        three = pill("a net of 3 is the same as one left", RATIO, size=LABEL)
        self.stack(head, [score, add, three], buff=1.0, top=1.1)
        self.no_overlap(*score)

        n = self.narrate(
            id="short_trick_01",
            text="The short trick: score each right as plus one and each left as minus one, add them, and make that many "
                 "quarter-turns clockwise.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "right")
        self.play(FadeIn(score[0], shift=UP * 0.1))
        self.at_word(n, "left")
        self.play(FadeIn(score[1], shift=UP * 0.1))
        self.at_word(n, "add")
        self.play(FadeIn(add, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="short_trick_02",
            text="A net of three is the same as one left.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "same")
        self.play(FadeIn(three, scale=1.03))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_short_trick")

    # ============================================== 7. THE ANALOGY - A HEADING ==========

    def analogy(self):
        self.scene_start("S07_analogy", title="The Analogy - A Heading")

        head = self.heading("Pilots and ships use a heading")
        comp = self.compass()
        what = text("a heading:  direction measured clockwise from north", LABEL, INK)
        add = pill("every sequence of turns becomes simple addition", GOOD, size=LABEL)
        stops = VGroup(text("where the analogy stops", SMALL, BAD, BOLD), text("real headings use 360 degrees continuously", SMALL, INK),
                       text("exam questions stay on the 8 points, in steps of 45°", SMALL, INK)).arrange(DOWN, buff=0.14, aligned_edge=LEFT)
        side = VGroup(what, add, stops).arrange(DOWN, buff=0.7)
        row = VGroup(comp, side).arrange(RIGHT, buff=0.7)
        self.stack(head, [row], top=0.45)
        self.no_overlap(comp, side)
        self.no_overlap(*stops)
        needle = self.needle(comp, 0)

        n = self.narrate(
            id="analogy_01",
            text="Pilots and ships give direction as a heading, measured clockwise from north.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "heading")
        self.play(FadeIn(comp), FadeIn(needle, shift=UP * 0.1), FadeIn(what, shift=UP * 0.1))
        self.at_word(n, "clockwise")
        self.play(self.turn(comp, needle, 270, run_time=2.0))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_02",
            text="Thinking in headings turns every sequence of turns into simple addition.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "addition")
        self.play(FadeIn(add, scale=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_03",
            text="Where the analogy stops: real headings use three hundred and sixty degrees continuously.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "stops")
        self.play(FadeIn(stops[0], shift=RIGHT * 0.2))
        self.at_word(n, "real")
        self.play(FadeIn(stops[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_04",
            text="Exam questions stay on the eight points, in steps of forty-five degrees.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "stay")
        self.play(FadeIn(stops[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S07_analogy")

    # ============================================== 8. WORKED EXAMPLE - CLOSING THE HOOK ==========

    def hook_solved(self):
        self.scene_start("S08_hook_solved", title="Worked Example - Closing the Hook")

        head = self.heading("Worked example: closing the hook")
        comp = self.compass(radius=1.4)
        chips = VGroup(*[VGroup(pill(c, GOOD if c == "RIGHT" else BAD, size=SMALL), text("+90°" if c == "RIGHT" else "−90°", SMALL, INK, BOLD))
                         .arrange(DOWN, buff=0.15) for c in HOOK_TURNS]).arrange(RIGHT, buff=0.2)
        total = text("four rights and one left:    +360° − 90°  =  +270°", LABEL, INK, BOLD)
        west = pill("north (0°) + 270°  =  270°  =  west", GOOD, size=LABEL)
        check = text("check:   N → E → S → (left) E → S → W", SMALL, FOCUS, BOLD)
        side = VGroup(chips, total, west, check).arrange(DOWN, buff=0.5)
        row = VGroup(comp, side).arrange(RIGHT, buff=0.6)
        self.stack(head, [row], top=0.6)
        self.no_overlap(comp, side)
        self.no_overlap(*chips)
        needle = self.needle(comp, 0)

        n = self.narrate(
            id="hook_solved_01",
            text="Four rights and one left: plus three hundred and sixty degrees, minus ninety, is plus two hundred and "
                 "seventy.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "rights")
        self.play(FadeIn(comp), FadeIn(needle, shift=UP * 0.1), FadeIn(chips, shift=UP * 0.1))
        self.at_word(n, "minus")
        self.play(FadeIn(total, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_solved_02",
            text="North, at zero, plus two hundred and seventy degrees is west.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "plus")
        self.play(FadeIn(west, scale=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_solved_03",
            text="Check by turning: north to east, to south, then the left turn back to east, then south, then west.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Check")
        self.play(FadeIn(check, shift=UP * 0.1))
        self.at_word(n, "east")
        self.play(self.turn(comp, needle, 90, run_time=0.6))
        self.at_word(n, "south")
        self.play(self.turn(comp, needle, 90, run_time=0.6))
        self.at_word(n, "left")
        self.play(self.turn(comp, needle, -90, run_time=0.6))
        self.at_word(n, "south", occurrence=2)
        self.play(self.turn(comp, needle, 90, run_time=0.6))
        self.at_word(n, "west")
        self.play(self.turn(comp, needle, 90, run_time=0.6))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S08_hook_solved")

    # ============================================== 9. A SECOND WORKED EXAMPLE - AN ANGLE TURN ==========

    def second_example(self):
        self.scene_start("S09_second_example", title="A Second Worked Example - An Angle Turn")

        head = self.heading("A second worked example: an angle turn")
        ask = text("A person faces west, turns 45° clockwise, then turns around, then turns 90° anticlockwise.  Which way?", SMALL, INK)
        comp = self.compass(radius=1.3)
        steps = self.solve_steps([("west = 270°;    + 45°  =  315°", "north-west"),
                                  ("turn around:    315° + 180°  =  495°  →  135°", "south-east"),
                                  ("− 90°:    135° − 90°  =  45°", "north-east")])
        row = VGroup(comp, steps).arrange(RIGHT, buff=0.6)
        self.stack(head, [ask, row], buff=0.5, top=0.5)
        self.no_overlap(comp, steps)
        self.no_overlap(*steps)
        needle = self.needle(comp, 270)

        n = self.narrate(
            id="second_example_01",
            text="A person faces west, turns forty-five degrees clockwise, then turns around, then turns ninety degrees "
                 "anticlockwise. Which way does the person face?",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "person")
        self.play(FadeIn(ask, shift=UP * 0.1))
        self.at_word(n, "west")
        self.play(FadeIn(comp), FadeIn(needle, shift=UP * 0.1))
        self.at_word(n, "Which")
        self.play(Indicate(ask, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_02",
            text="Step one: west is two hundred and seventy degrees. Plus forty-five is three hundred and fifteen: "
                 "north-west.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Plus")
        self.play(self.turn(comp, needle, 45))
        self.at_word(n, "north-west")
        self.play(FadeIn(steps[0], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_03",
            text="Step two, turn around: three hundred and fifteen plus one hundred and eighty is four hundred and "
                 "ninety-five, which reduces to one hundred and thirty-five: south-east.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "around")
        self.play(self.turn(comp, needle, 180, run_time=1.4))
        self.at_word(n, "south-east")
        self.play(FadeIn(steps[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_04",
            text="Step three, minus ninety: forty-five degrees, which is north-east.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "minus")
        self.play(self.turn(comp, needle, -90))
        self.at_word(n, "north-east")
        self.play(FadeIn(steps[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S09_second_example")

    # ============================================== 10. EXAM PATTERNS - HOW THIS IS ASKED ==========

    def exam_patterns(self):
        self.scene_start("S10_exam_patterns", title="Exam Patterns - How This Is Asked")

        head = self.heading("Exam patterns: how this is asked")
        table, rows = self.pattern_table(head, PATTERNS)

        n = self.narrate(
            id="exam_patterns_01",
            text="Exams ask this in five ways.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "five")
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_02",
            text="One turn: facing west and turning left is two hundred and seventy minus ninety: south.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "turn")
        self.play(FadeIn(rows[0][:3], shift=RIGHT * 0.2))
        self.at_word(n, "south")
        self.play(FadeIn(rows[0][3], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_03",
            text="Several turns: facing north, then right, right, left, is a net of plus ninety: east.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Several")
        self.play(FadeIn(rows[1][:3], shift=RIGHT * 0.2))
        self.at_word(n, "east")
        self.play(FadeIn(rows[1][3], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_04",
            text="The same turn repeated: facing east, left three times is the same as one right: south.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "repeated")
        self.play(FadeIn(rows[2][:3], shift=RIGHT * 0.2))
        self.at_word(n, "south")
        self.play(FadeIn(rows[2][3], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_05",
            text="An angle turn: facing north-east, ninety degrees clockwise gives south-east.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "angle")
        self.play(FadeIn(rows[3][:3], shift=RIGHT * 0.2))
        self.at_word(n, "gives")
        self.play(FadeIn(rows[3][3], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_06",
            text="An anticlockwise angle: facing south, one hundred and thirty-five degrees anticlockwise gives "
                 "north-east.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "anticlockwise")
        self.play(FadeIn(rows[4][:3], shift=RIGHT * 0.2))
        self.at_word(n, "gives")
        self.play(FadeIn(rows[4][3], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S10_exam_patterns")

    # ============================================== 11. TRAPS AND CONFUSING QUESTIONS ==========

    def traps(self):
        self.scene_start("S11_traps", title="Traps and Confusing Questions")

        head, ask, wrong, right, rule = self.show_trap(TRAPS[0])

        n = self.narrate(
            id="traps_01",
            text="Trap one: the south flip.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "flip")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_02",
            text="A person faces south and turns left. Which way does the person face?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "south")
        self.play(FadeIn(ask, shift=UP * 0.1))
        self.at_word(n, "Which")
        self.play(Indicate(ask, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_03",
            text="The wrong instinct: west, because left is west on a map.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "instinct")
        self.play(FadeIn(wrong, shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_04",
            text="Correct: facing south, left is east.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "east")
        self.play(FadeIn(right, shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_05",
            text="The rule: left and right belong to the person, not to the page. Draw the facing arrow, and turn from it.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "belong")
        self.play(FadeIn(rule, scale=1.03))
        self.at_word(n, "arrow")
        self.play(Indicate(rule, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)
        self.clear_stage()

        head, ask, wrong, right, rule = self.show_trap(TRAPS[1])

        n = self.narrate(
            id="traps_06",
            text="Trap two: clockwise from the wrong side.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "clockwise")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_07",
            text="Facing north, a person turns one hundred and thirty-five degrees clockwise. Which way?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "turns")
        self.play(FadeIn(ask, shift=UP * 0.1))
        self.at_word(n, "Which")
        self.play(Indicate(ask, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_08",
            text="The wrong instinct: south-west.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "instinct")
        self.play(FadeIn(wrong, shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_09",
            text="Correct: zero plus one hundred and thirty-five degrees is south-east.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "plus")
        self.play(FadeIn(right, shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_10",
            text="The rule: clockwise from north passes through east first: north, north-east, east, south-east.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "passes")
        self.play(FadeIn(rule, scale=1.03))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S11_traps")

    # ============================================== 12. CHECKPOINT ==========

    def checkpoint(self):
        self.scene_start("S12_checkpoint", title="Checkpoint")

        head = self.heading("Checkpoint  ·  your turn")
        comp = self.compass(angles=False)
        ask = text("Facing east, a person turns left three times.\nWhich way does the person face?", LABEL, FOCUS, BOLD)
        path = text("E  →  N  →  W  →  S", BODY, INK, BOLD)
        answer = pill("south", GOOD, size=BODY)
        side = VGroup(ask, path, answer).arrange(DOWN, buff=0.8)
        row = VGroup(comp, side).arrange(RIGHT, buff=0.9)
        self.stack(head, [row], top=0.6)
        self.no_overlap(comp, side)
        needle = self.needle(comp, 90)

        n = self.narrate(
            id="checkpoint_01",
            text="Your turn. Facing east, a person turns left three times. Which way does the person face?",
            voice="default",
            subtitle=True,
            pause_after=10.0,
        )
        self.at_word(n, "turn")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "east")
        self.play(FadeIn(comp), FadeIn(needle, shift=UP * 0.1), FadeIn(ask, shift=UP * 0.1))
        self.at_word(n, "Which")
        self.play(Indicate(ask, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="checkpoint_02",
            text="East, then north, then west, then south.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "East")
        self.play(FadeIn(path, shift=UP * 0.1))
        self.at_word(n, "north")
        self.play(self.turn(comp, needle, -90, run_time=0.7))
        self.at_word(n, "west")
        self.play(self.turn(comp, needle, -90, run_time=0.7))
        self.at_word(n, "south")
        self.play(self.turn(comp, needle, -90, run_time=0.7))
        self.wait_for_narration(n)

        n = self.narrate(
            id="checkpoint_03",
            text="The person faces south.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "faces")
        self.play(FadeIn(answer, scale=1.03))
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
            text="Level one, question one: a person faces north and turns right. Question two: a person faces west and "
                 "turns left. Question three: a person faces south and turns around. In each, which way does the person "
                 "face?",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "north")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "west")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.at_word(n, "south")
        self.play(FadeIn(rows[2], shift=RIGHT * 0.2))
        self.at_word(n, "each")
        self.play(Indicate(head, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="practice_02",
            text="Level two, question four: a person faces north and turns right, right, then left. Question five: a "
                 "person faces east and turns left three times. Question six: a person faces north-east and turns ninety "
                 "degrees clockwise.",
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
            text="Level three, question seven: a person faces south and turns one hundred and thirty-five degrees "
                 "anticlockwise. Question eight: a person faces west, turns forty-five degrees clockwise, turns around, "
                 "then turns ninety degrees anticlockwise.",
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
            text="One: zero plus ninety degrees: east.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "plus")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "east")
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_02",
            text="Two: two hundred and seventy minus ninety is one hundred and eighty: south.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "minus")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "south")
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_03",
            text="Three: one hundred and eighty plus one hundred and eighty: north.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "plus")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "north")
        self.play(FadeIn(rows[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_04",
            text="Four: a net of plus ninety: east.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "net")
        self.play(FadeIn(rows[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "east")
        self.play(FadeIn(rows[3][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Answer key  ·  5 to 8", GOOD)
        table, rows = self.answer_table(head, ANSWERS_B, 5)

        n = self.narrate(
            id="answers_05",
            text="Five: ninety minus two hundred and seventy is minus one hundred and eighty, which is south.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "minus")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "south")
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_06",
            text="Six: forty-five plus ninety is one hundred and thirty-five: south-east.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "plus")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "south-east")
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_07",
            text="Seven: one hundred and eighty minus one hundred and thirty-five is forty-five: north-east.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "minus")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "north-east")
        self.play(FadeIn(rows[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_08",
            text="Eight: two hundred and seventy, plus forty-five, plus one hundred and eighty, minus ninety, is four "
                 "hundred and five, which reduces to forty-five: north-east.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "plus")
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
            text="Recognise and move. The recognition cue: the words, turns left or right, clockwise, turns around, or, "
                 "which direction is he facing.",
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
            text="The target time: fifteen seconds.",
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
            text="The sanity check: equal numbers of rights and lefts always return you to the starting direction.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "sanity")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "equal")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S15_exam_lens")

    # ============================================== 16. QUICK REVISION AND SUMMARY ==========

    def summary(self):
        self.scene_start("S16_summary", title="Quick Revision and Summary")

        head = self.heading("Quick revision")
        points = VGroup(text("think in headings from north", LABEL, INK, BOLD), text("rights add 90°,  lefts subtract 90°;  apply the net turn once", LABEL, INK, BOLD),
                        text("facing south, left is east", LABEL, RATIO, BOLD)).arrange(DOWN, buff=0.5, aligned_edge=LEFT)
        box = VGroup(pill("headings from N", GOOD, size=SMALL), pill("right +90,  left −90", GOOD, size=SMALL), pill("net turn", GOOD, size=SMALL),
                     pill("south:  left = east", GOOD, size=SMALL)).arrange(RIGHT, buff=0.3)
        self.stack(head, [points, box], buff=1.1, top=1.1)
        self.no_overlap(*points)
        self.no_overlap(*box)

        n = self.narrate(
            id="summary_01",
            text="Think in headings from north.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "headings")
        self.play(FadeIn(points[0], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_02",
            text="Rights add ninety degrees, lefts subtract ninety, and the net turn is applied once.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "add")
        self.play(FadeIn(points[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_03",
            text="Facing south, left is east.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "south")
        self.play(FadeIn(points[2], shift=RIGHT * 0.2))
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
                                        [[str(0 + i + 1)] + list(row) for i, row in enumerate(QUIZ[0:3])], [0.8, 7.4, 5.0], room=1.3)
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
                                        [[str(3 + i + 1)] + list(row) for i, row in enumerate(QUIZ[3:5])], [0.8, 7.4, 5.0], room=1.3)
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
        nxt = self.breadcrumb("Next", "Video 2 · Distance & Displacement")
        nxt.next_to(table, DOWN, buff=0.6)
        self.no_overlap(table, nxt)
        self.validator.check_in_frame(VGroup(head, table, nxt))

        n = self.narrate(
            id="section_quiz_07",
            text="The answers. One: a net of two rights, so east plus one hundred and eighty degrees is west: option c.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "net")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "option")
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="section_quiz_08",
            text="Two: facing south, left is east: option a.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "south")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "option")
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="section_quiz_09",
            text="Three: zero plus two hundred and twenty-five degrees is south-west: option d.",
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
            text="Four: two hundred and seventy minus forty-five is two hundred and twenty-five, south-west: option b.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "minus")
        self.play(FadeIn(rows[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "option")
        self.play(FadeIn(rows[3][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="section_quiz_11",
            text="Five: one hundred and thirty-five, plus ninety, plus one hundred and eighty, is four hundred and five, "
                 "which reduces to forty-five, north-east: option c.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "plus")
        self.play(FadeIn(rows[4][:2], shift=RIGHT * 0.2))
        self.at_word(n, "option")
        self.play(FadeIn(rows[4][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="section_quiz_12",
            text="Next: distance and displacement.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Next")
        self.play(FadeIn(nxt, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S17_section_quiz")

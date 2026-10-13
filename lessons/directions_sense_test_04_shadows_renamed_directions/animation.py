"""
animation.py for the LMS video generator.

Course : Pre-C-CAT - Section A - Logical Reasoning
Video  : Lesson 3 - Directions Sense Test - 04 - Shadows & Renamed Directions

Source script:
  C:\\Scripts\\Section A\\Reasoning_Scripts\\Sessions 1-4 - Coding-Decoding, Alphabets, Directions, Number Series, Odd Man Out\\Lesson 3 - Directions Sense Test\\04 - Shadows & Renamed Directions.pdf

Built on the golden-reference pattern:
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``;
  * layouts stacked with next_to and guarded with ``no_overlap``; nothing is
    ever animated onto or into another box.

Lesson 3, Video 3 of 6 (file 04 in its folder).
Not the first video: a silent breadcrumb, a one-line recap of Video 2, then today's topic.
The narration follows the script section by section and ends with the Section Quiz and its answer key.
Shadows are shown with a sun, a stick and its shadow on an east-west ground line; renamed directions with a compass whose
new names (orange) sit outside the true ones.
Every shadow, facing direction and renamed direction in the script was recomputed in the data block; all of them are correct.
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


def heading(name):
    return POINTS.index(name) * 45


def point_at(degrees):
    return POINTS[(degrees % 360) // 45]


def shadow_of(time):
    """Morning: sun east, shadow west.  Evening: sun west, shadow east."""
    return {"morning": "west", "evening": "east"}[time]


def facing_with(shadow, side):
    """Which way you face if the shadow falls on your left / right / ahead."""
    return point_at(heading(shadow) + {"left": 90, "right": -90, "ahead": 0}[side])


def rotation(old, new):
    return (heading(new) - heading(old)) % 360


def renamed(name, old, new):
    return point_at(heading(name) + rotation(old, new))


# ---- hook, concept steps, worked examples ----
assert shadow_of("morning") == "west" and facing_with("west", "ahead") == "west" and facing_with("west", "left") == "north"
assert rotation("north-east", "west") == 225 and renamed("south", "north-east", "west") == "north-east" and (180 + 225) % 360 == 45
B_FACES = facing_with(shadow_of("morning"), "right")
assert B_FACES == "south" and point_at(heading(B_FACES) + 180) == "north"
# ---- exam patterns, traps, checkpoint, practice ----
assert shadow_of("evening") == "east" and facing_with("east", "left") == "south"
assert rotation("north", "east") == 90 and renamed("west", "north", "east") == "north" and (270 + 90) % 360 == 0
# ---- section quiz ----
assert facing_with(shadow_of("evening"), "ahead") == "east" and facing_with(shadow_of("morning"), "right") == "south"
assert rotation("west", "north") == 90 and renamed("south", "west", "north") == "west"
assert rotation("north-east", "south-east") == 90 and renamed("north-west", "north-east", "south-east") == "north-east"
A_FACES = facing_with(shadow_of("morning"), "left")
assert A_FACES == "north" and point_at(heading(A_FACES) + 180) == "south"

OBJECTIVES = [("Use the sun's position", "to find the direction of a shadow, and the reverse"),
              ("Combine the shadow direction with left and right", "to find which way a person faces"),
              ("Solve renamed-direction questions", "with a single rotation")]
FORMULAS = ["Morning:   sun east,   shadow west",
            "Evening:   sun west,   shadow east",
            "Renamed directions:   rotation  =  new angle − old angle   (clockwise)",
            "Apply the same rotation to every direction;   reduce by 360°"]
PATTERNS = [("Facing the sun", "morning;  facing the sun", "the sun is in the east", "east"),
            ("Shadow direction", "evening;  where does your shadow fall?", "opposite the sun", "east"),
            ("Shadow on one side", "evening;  shadow on your left", "facing south puts east on the left", "south"),
            ("Simple rename", "north is called east;  west is called?", "+90°", "north"),
            ("Angle rename", "north-east is called west;  south is called?", "+225°", "north-east")]
TRAPS = [("Trap 1  ·  the shadow in the sun's direction", "In the evening, which way does your shadow fall?",
          "west, because the sun sets in the west", "opposite the sun:  east",
          "find the sun first, then turn 180° for the shadow"),
         ("Trap 2  ·  renaming by “similar sounding” logic", "If north-east is called west, what is south called?",
          "“NE became W, so S becomes E”", "rotation +225°:  north-east",
          "compute the angle from the given pair, then apply it")]
PRACTICE_A = [("L1", "In the morning, you face the sun.  Which way are you facing?"),
              ("L1", "In the evening, in which direction does your shadow fall?"),
              ("L1", "In the morning, you walk towards your shadow.  Which way are you walking?"),
              ("L2", "In the evening, your shadow falls to your left.  Which way are you facing?"),
              ("L2", "In the morning, your shadow falls to your left.  Which way are you facing?"),
              ("L2", "If north is called east and every direction is rotated the same way, what is west called?")]
PRACTICE_B = [("L3", "If north-east is called west and every direction is rotated the same way, what is south called?"),
              ("L3", "One morning, A and B stand facing each other.  A's shadow falls exactly to B's right.  Which way is A facing?")]
ANSWERS_A = [("the morning sun is in the east", "east"),
             ("opposite the setting sun", "east"),
             ("the shadow points west", "west"),
             ("shadow east, on your left", "facing south")]
ANSWERS_B = [("shadow west, on your left", "facing north"),
             ("rotation +90°:   270° + 90°  =  360°  →  0°", "north"),
             ("rotation 270° − 45°  =  +225°:   180° + 225°  →  45°", "north-east"),
             ("shadow west is on B's right, so B faces south;   A faces B", "north")]
LENS = [("Recognition cue", "“morning”, “evening”, “shadow”, “sun”;   or  “is called”, “becomes”"),
        ("Target time", "25 seconds for shadows,  30 seconds for renaming"),
        ("Sanity check", "for a rotation, opposite directions must stay opposite after renaming")]
QUIZ = [["In the evening, you walk towards your shadow.   Which way are you walking?", "(a) West   (b) North   (c) South   (d) East"],
        ["In the morning, your shadow falls to your right.   Which way are you facing?", "(a) North   (b) South   (c) East   (d) West"],
        ["If west is called north (every direction rotated the same way), what is south called?", "(a) West   (b) East   (c) North   (d) South"],
        ["If north-east is called south-east (same rotation for all), what is north-west called?",
         "(a) South-west   (b) North   (c) North-east   (d) South-east"],
        ["One morning, A and B face each other.   B's shadow falls exactly to A's left.   Which way is B facing?",
         "(a) North   (b) East   (c) West   (d) South"]]
QUIZ_KEY = [("the evening shadow points east", "(d)  East"),
            ("shadow west, on the right:  facing south", "(b)  South"),
            ("rotation +90°:   180° + 90°  =  270°", "(a)  West"),
            ("rotation +90°:   315° + 90°  →  45°", "(c)  North-east"),
            ("shadow west on A's left:  A faces north, so B faces south", "(d)  South")]


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


class ShadowsAndRenamedDirectionsVideo(LMSScene):
    lesson_title = "Shadows & Renamed Directions"

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

    def with_room(self, comp, reach=1.15):
        """The compass inside an unseen square that reserves the space new_names() will use."""
        side = comp[0].width + 2 * (reach + 0.35)
        return VGroup(Square(side_length=side).set_stroke(width=0).move_to(comp[0]), comp)

    def new_names(self, comp, shift_deg, reach=1.15):
        """The renamed directions around a placed compass (drawn with angles=False): the name now used for each true point."""
        centre, radius = comp[0].get_center(), comp[0].width / 2
        names = VGroup()
        for i in range(8):
            a = i * 45 * DEGREES
            d = np.array([math.sin(a), math.cos(a), 0.0])
            names.add(text(COMPASS_POINTS[((i * 45 + shift_deg) % 360) // 45], SMALL, RATIO, BOLD).move_to(centre + d * (radius + reach)))
        self.no_overlap(*names, *comp[2], gap=0.02)
        self.validator.check_in_frame(names)
        return names

    def sun_scene(self, time):
        """A stick on an east-west ground line with the sun and the stick's shadow.
        Returns (ground with its W and E marks, stick, sun with its label, shadow with its label)."""
        east = time == "morning"
        ground = VGroup(Line(LEFT * 2.6, RIGHT * 2.6, color=MUTED, stroke_width=3), text("W", LABEL, INK, BOLD).move_to(LEFT * 3.0),
                        text("E", LABEL, INK, BOLD).move_to(RIGHT * 3.0))
        stick = Line(ORIGIN, UP * 1.1, color=INK, stroke_width=7)
        side = RIGHT if east else LEFT
        disc = Circle(radius=0.32, color=FOCUS, fill_color=FOCUS, fill_opacity=0.9, stroke_width=0).move_to(side * 2.1 + UP * 1.5)
        sun = VGroup(disc, text(f"{time} sun", SMALL, FOCUS, BOLD).next_to(disc, UP, buff=0.12))
        shade = Line(ORIGIN, -side * 1.9, color=SECOND, stroke_width=9).shift(DOWN * 0.07)
        shadow = VGroup(shade, text("shadow", SMALL, SECOND, BOLD).next_to(shade, DOWN, buff=0.14))
        return VGroup(ground, stick, sun, shadow)

    # ============================================== 0. INTRO ==========
    # Not the first video: silent breadcrumb, a one-line recap of the previous video, then today's topic.

    def intro(self):
        self.scene_start("S00_intro", title="Intro")

        crumb = self.breadcrumb("Logical Reasoning", "Lesson 3 · Directions Sense Test", "Video 3 of 6")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        recap = VGroup(text("from Video 2  ·  Distance & Displacement", SMALL, MUTED), pill("net N–S and net E–W,  combined with Pythagoras", WORD, size=LABEL)).arrange(DOWN, buff=0.25)
        title = fit_width(text("Shadows & Renamed Directions", TITLE, INK, BOLD), SAFE_W - 0.4)
        today = text("today: one fact plus one rotation", LABEL, FOCUS)
        block = VGroup(recap, title, today).arrange(DOWN, buff=0.7)
        fit_within(block, SAFE_W, SAFE_H - crumb.height - 0.9)
        block.next_to(crumb, DOWN, buff=0.7)
        self.no_overlap(crumb, recap, title, today)
        self.validator.check_in_frame(VGroup(crumb, block))

        n = self.narrate(
            id="intro_01",
            text="In the last video, every path reduced to a net north-south and a net east-west movement, combined with "
                 "Pythagoras.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.at_word(n, "reduced")
        self.play(FadeIn(recap[0]))
        self.at_word(n, "Pythagoras")
        self.play(FadeIn(recap[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="intro_02",
            text="This video covers shadows and renamed directions: one fact plus one rotation.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "covers")
        self.play(FadeIn(title, shift=UP * 0.1))
        self.at_word(n, "rotation")
        self.play(FadeIn(today, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_intro")

    # ============================================== 1. HOOK ==========

    def hook(self):
        self.scene_start("S01_hook", title="Hook")

        head = self.heading("Seven in the morning")
        sky = self.sun_scene("morning")
        ask = text("your long shadow is straight in front of you:  which way are you walking?", LABEL, FOCUS, BOLD)
        facts = VGroup(pill("the morning sun is in the east", FOCUS, size=LABEL), pill("so your shadow points west", SECOND, size=LABEL),
                       pill("you walk towards it:  west", GOOD, size=LABEL)).arrange(RIGHT, buff=0.4)
        moral = text("the sun is a compass you always carry", LABEL, INK)
        self.stack(head, [ask, sky, facts, moral], buff=0.55, top=0.5)
        self.no_overlap(*facts)

        n = self.narrate(
            id="hook_01",
            text="It is seven in the morning, and you are walking with your long shadow stretched straight out in front of "
                 "you. Which way are you walking?",
            voice="default",
            subtitle=True,
            pause_after=3.0,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "morning")
        self.play(FadeIn(sky[0]), FadeIn(sky[1], shift=UP * 0.1))
        self.at_word(n, "shadow")
        self.play(FadeIn(ask, shift=UP * 0.1))
        self.at_word(n, "Which")
        self.play(Indicate(ask, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="hook_02",
            text="You do not need a compass. The morning sun is in the east, so your shadow points west, and you are "
                 "walking towards it: west.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "compass")
        self.play(Indicate(sky[0], color=FOCUS, scale_factor=1.03))
        self.at_word(n, "sun")
        self.play(FadeIn(sky[2]), FadeIn(facts[0], shift=UP * 0.1))
        self.at_word(n, "points")
        self.play(FadeIn(sky[3]), FadeIn(facts[1], shift=UP * 0.1))
        self.at_word(n, "towards")
        self.play(FadeIn(facts[2], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_03",
            text="The sun is a compass you always carry.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "carry")
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
            text="One: use the sun's position to find the direction of a shadow, and the reverse.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "position")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "shadow")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="objectives_03",
            text="Two: combine the shadow direction with left and right to find which way a person faces.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "combine")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "faces")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="objectives_04",
            text="Three: solve renamed-direction questions with a single rotation.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "solve")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "single")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_objectives")

    # ============================================== 3. WHY THIS SECTION ==========

    def why_this_section(self):
        self.scene_start("S03_why_this_section", title="Why This Section")

        head = self.heading("Why this section")
        riddle = pill("they look like riddles, but each is one fact plus one rotation", WORD, size=LABEL)
        quick = text("fix the method, and they become quick marks", BODY, GOOD, BOLD)
        self.stack(head, [riddle, quick], buff=1.2, top=1.5)

        n = self.narrate(
            id="why_this_section_01",
            text="Shadow and renaming questions look like riddles, but each is one fact plus one rotation.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "riddles")
        self.play(FadeIn(riddle, scale=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="why_this_section_02",
            text="Fix the method, and they become quick marks.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "quick")
        self.play(FadeIn(quick, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_why_this_section")

    # ============================================== 4. THE CONCEPT JOURNEY ==========

    def concept_journey(self):
        self.scene_start("S04_concept_journey", title="The Concept Journey")

        head = self.heading("Steps 1 to 3  ·  the sun and the shadow")
        morning = self.sun_scene("morning")
        evening = self.sun_scene("evening")
        skies = VGroup(morning, evening).arrange(RIGHT, buff=0.7)
        assume = text("the exam assumption:  the sun rises in exact east and sets in exact west", SMALL, MUTED)
        rule = pill("the shadow is opposite the sun", FOCUS, size=LABEL)
        side = text("shadow on your left or right?  find the facing that puts that side towards it.   Facing north, your left is west.", SMALL, INK, BOLD)
        self.stack(head, [assume, skies, rule, side], buff=0.5, top=0.5)
        self.no_overlap(morning, evening)

        n = self.narrate(
            id="concept_journey_01",
            text="Step one: the exam assumption. The sun rises in the east and sets in the west.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "one")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "rises")
        self.play(FadeIn(morning[:3]))
        self.at_word(n, "sets")
        self.play(FadeIn(evening[:3]))
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_journey_02",
            text="Real sunrise drifts north or south of east through the year, but exam questions use exact east and west.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "exact")
        self.play(FadeIn(assume, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_journey_03",
            text="Step two: the shadow is opposite the sun. In the morning the shadow falls west; in the evening it falls "
                 "east.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "opposite")
        self.play(FadeIn(rule, scale=1.03))
        self.at_word(n, "morning")
        self.play(FadeIn(morning[3]))
        self.at_word(n, "evening")
        self.play(FadeIn(evening[3]))
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_journey_04",
            text="Step three: shadow plus left or right. If the shadow falls on your left or right, find which facing "
                 "direction puts that side towards the shadow. Facing north, your left is west.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "three")
        self.play(Indicate(head, color=FOCUS, scale_factor=1.03))
        self.at_word(n, "find")
        self.play(FadeIn(side, shift=UP * 0.1))
        self.at_word(n, "Facing")
        self.play(Indicate(side, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Steps 4 to 6  ·  renamed directions")
        comp = self.compass(radius=1.3, angles=False)
        said = pill("“north-east is called west”", WORD, size=LABEL)
        same = text("every direction is rotated by the same angle", SMALL, INK)
        angle = text("NE (45°)  →  W (270°):    +225° clockwise", LABEL, FOCUS, BOLD)
        apply = text("south (180°) + 225°  =  405°  →  45°", LABEL, INK, BOLD)
        result = pill("south is called north-east", GOOD, size=LABEL)
        check = text("a second pair, if given, must give the same angle", SMALL, MUTED)
        side = VGroup(said, same, angle, apply, result, check).arrange(DOWN, buff=0.38)
        row = VGroup(self.with_room(comp), side).arrange(RIGHT, buff=0.5)
        self.stack(head, [row], top=0.25)
        names = self.new_names(comp, 225)
        self.no_overlap(names, side)
        self.no_overlap(names, head)

        n = self.narrate(
            id="concept_journey_05",
            text="Step four: renamed directions. If north-east is called west, every direction is rotated by the same "
                 "angle.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "four")
        self.play(FadeIn(comp))
        self.at_word(n, "called")
        self.play(FadeIn(said, shift=UP * 0.1))
        self.at_word(n, "rotated")
        self.play(FadeIn(same, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_journey_06",
            text="Find the angle once: from north-east, at forty-five degrees, to west, at two hundred and seventy, is "
                 "plus two hundred and twenty-five degrees clockwise.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "angle")
        self.play(FadeIn(angle, shift=UP * 0.1))
        self.at_word(n, "west")
        self.play(FadeIn(names[1]), comp[2][1].animate.set_color(FOCUS))
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_journey_07",
            text="Step five: apply the same rotation. South, at one hundred and eighty, plus two hundred and twenty-five "
                 "is four hundred and five, which reduces to forty-five: south is called north-east.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "apply")
        self.play(FadeIn(apply, shift=UP * 0.1))
        self.at_word(n, "reduces")
        self.play(FadeIn(names[4]), comp[2][4].animate.set_color(FOCUS))
        self.at_word(n, "called")
        self.play(FadeIn(result, scale=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_journey_08",
            text="Step six: check with a second pair if the question gives one; both pairs must give the same angle.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "check")
        self.play(FadeIn(check, shift=UP * 0.1))
        self.at_word(n, "both")
        self.play(FadeIn(VGroup(*[names[i] for i in (0, 2, 3, 5, 6, 7)])))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_concept_journey")

    # ============================================== 5. RULE BOX ==========

    def rule_box(self):
        self.scene_start("S05_rule_box", title="Rule Box")

        head = self.heading("Rule box", GOOD)
        lines = VGroup(*[text(f, LABEL, INK) for f in FORMULAS]).arrange(DOWN, buff=0.5, aligned_edge=LEFT)
        fit_width(lines, SAFE_W - 1.6)
        box = self.card(lines, width=SAFE_W - 0.4, color=GOOD, pad=0.5)
        self.stack(head, [box], top=0.8)

        n = self.narrate(
            id="rule_box_01",
            text="Here is the rule box. In the morning, the sun is east and the shadow is west.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "box")
        self.play(FadeIn(box[0]))
        self.at_word(n, "morning")
        self.play(FadeIn(lines[0], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="rule_box_02",
            text="In the evening, the sun is west and the shadow is east.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "evening")
        self.play(FadeIn(lines[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="rule_box_03",
            text="For renamed directions, the rotation is the new angle minus the old angle, clockwise.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "minus")
        self.play(FadeIn(lines[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="rule_box_04",
            text="Apply the same rotation to every direction, and reduce by three hundred and sixty degrees.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Apply")
        self.play(FadeIn(lines[3], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_rule_box")

    # ============================================== 6. SHORT TRICK ==========

    def short_trick(self):
        self.scene_start("S06_short_trick", title="Short Trick")

        head = self.heading("Short trick", RATIO)
        shadows = VGroup(pill("morning shadows point west", SECOND, size=BODY), pill("evening shadows point east", RATIO, size=BODY)).arrange(RIGHT, buff=0.6)
        rename = text("renamed directions:  find one rotation angle, and apply it to every direction", LABEL, GOOD, BOLD)
        self.stack(head, [shadows, rename], buff=1.3, top=1.4)
        self.no_overlap(*shadows)

        n = self.narrate(
            id="short_trick_01",
            text="The short trick: morning shadows point west, evening shadows point east.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "morning")
        self.play(FadeIn(shadows[0], shift=UP * 0.1))
        self.at_word(n, "evening")
        self.play(FadeIn(shadows[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="short_trick_02",
            text="For renamed directions, find one rotation angle and apply it to every direction.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "rotation")
        self.play(FadeIn(rename, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_short_trick")

    # ============================================== 7. THE ANALOGY - A SLIPPED COMPASS CARD ==========

    def analogy(self):
        self.scene_start("S07_analogy", title="The Analogy - A Slipped Compass Card")

        head = self.heading("A compass card that has slipped in its case")
        comp = self.compass(radius=1.3, angles=False)
        same = text("every label moves by the same angle", LABEL, INK)
        one = pill("one known pair tells you where every other label now sits", GOOD, size=SMALL)
        stops = VGroup(text("where the analogy stops", SMALL, BAD, BOLD), text("a slipped card only rotates", SMALL, INK),
                       text("a swap no rotation can produce:  treat each given\npair as a fixed rule, and do not extend it", SMALL, INK))\
            .arrange(DOWN, buff=0.14, aligned_edge=LEFT)
        side = VGroup(same, one, stops).arrange(DOWN, buff=0.6)
        row = VGroup(self.with_room(comp), side).arrange(RIGHT, buff=0.5)
        self.stack(head, [row], top=0.25)
        names = self.new_names(comp, 225)
        self.no_overlap(names, side)
        self.no_overlap(names, head)

        n = self.narrate(
            id="analogy_01",
            text="Renaming directions is like a compass card that has slipped inside its case.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "card")
        self.play(FadeIn(comp))
        self.at_word(n, "slipped")
        self.play(FadeIn(names))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_02",
            text="Every label moves by the same angle, so one known pair tells you where every other label now sits.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "same")
        self.play(FadeIn(same, shift=UP * 0.1))
        self.at_word(n, "pair")
        self.play(FadeIn(one, scale=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_03",
            text="Where the analogy stops: a slipped card only rotates.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "stops")
        self.play(FadeIn(stops[0], shift=RIGHT * 0.2))
        self.at_word(n, "only")
        self.play(FadeIn(stops[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_04",
            text="If a question swaps directions in a way no rotation can produce, treat each given pair as a fixed rule, "
                 "and do not extend it.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "swaps")
        self.play(FadeIn(stops[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S07_analogy")

    # ============================================== 8. WORKED EXAMPLE - CLOSING THE HOOK ==========

    def hook_solved(self):
        self.scene_start("S08_hook_solved", title="Worked Example - Closing the Hook")

        head = self.heading("Worked example: closing the hook")
        sky = self.sun_scene("morning")
        steps = VGroup(pill("morning:  the sun is east", FOCUS, size=LABEL), pill("the shadow points west", SECOND, size=LABEL),
                       pill("you walk towards your shadow:  west", GOOD, size=LABEL)).arrange(DOWN, buff=0.4)
        row = VGroup(sky, steps).arrange(RIGHT, buff=0.9)
        self.stack(head, [row], top=1.2)
        self.no_overlap(sky, steps)

        n = self.narrate(
            id="hook_solved_01",
            text="It is morning, so the sun is in the east, and the shadow points west.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "morning")
        self.play(FadeIn(sky[:3]), FadeIn(steps[0], shift=UP * 0.1))
        self.at_word(n, "points")
        self.play(FadeIn(sky[3]), FadeIn(steps[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_solved_02",
            text="You walk towards your shadow, so you are walking west.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "towards")
        self.play(FadeIn(steps[2], scale=1.03))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S08_hook_solved")

    # ============================================== 9. A SECOND WORKED EXAMPLE - TWO PEOPLE, ONE SHADOW ==========

    def second_example(self):
        self.scene_start("S09_second_example", title="A Second Worked Example - Two People, One Shadow")

        head = self.heading("A second worked example: two people, one shadow")
        ask = text("One morning, A and B stand facing each other.  A's shadow falls exactly to B's right.  Which way is A facing?", SMALL, INK)
        a = Dot(DOWN * 1.0, color=WORD, radius=0.14)
        b = Dot(UP * 1.0, color=RATIO, radius=0.14)
        tags = VGroup(text("A", LABEL, WORD, BOLD).next_to(a, RIGHT, buff=0.2), text("B", LABEL, RATIO, BOLD).next_to(b, RIGHT, buff=0.2))
        faces = VGroup(Arrow(a.get_center(), a.get_center() + UP * 0.85, buff=0.16, color=WORD, stroke_width=5),
                       Arrow(b.get_center(), b.get_center() + DOWN * 0.85, buff=0.16, color=RATIO, stroke_width=5))
        shade = Line(a.get_center(), a.get_center() + LEFT * 1.5, color=SECOND, stroke_width=9)
        shadow = VGroup(shade, text("A's shadow:  west", SMALL, SECOND, BOLD).next_to(shade, DOWN, buff=0.14))
        scene = VGroup(a, b, tags, faces, shadow)
        steps = self.solve_steps([("morning:   A's shadow points", "west"), ("west is on B's right, so B faces", "south"),
                                  ("A faces B, so A faces", "north")])
        row = VGroup(scene, steps).arrange(RIGHT, buff=1.0)
        self.stack(head, [ask, row], buff=0.7, top=0.6)
        self.no_overlap(scene, steps)
        self.no_overlap(*steps)

        n = self.narrate(
            id="second_example_01",
            text="One morning, A and B stand facing each other. A's shadow falls exactly to B's right. Which way is A "
                 "facing?",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "morning")
        self.play(FadeIn(ask, shift=UP * 0.1))
        self.at_word(n, "stand")
        self.play(FadeIn(a), FadeIn(b, shift=UP * 0.1), FadeIn(tags, shift=UP * 0.1))
        self.at_word(n, "Which")
        self.play(Indicate(ask, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_02",
            text="Step one: it is morning, so A's shadow points west.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "points")
        self.play(FadeIn(shadow), FadeIn(steps[0], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_03",
            text="Step two: west is on B's right, so B faces south; facing south, your right is west.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "faces")
        self.play(FadeIn(faces[1]), FadeIn(steps[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_04",
            text="Step three: A faces B, so A faces north.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "north")
        self.play(FadeIn(faces[0]), FadeIn(steps[2], shift=RIGHT * 0.2))
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
            text="Facing the sun: in the morning the sun is in the east, so you face east.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Facing")
        self.play(FadeIn(rows[0][:3], shift=RIGHT * 0.2))
        self.at_word(n, "so")
        self.play(FadeIn(rows[0][3], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_03",
            text="Shadow direction: in the evening your shadow falls opposite the sun: east.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "direction")
        self.play(FadeIn(rows[1][:3], shift=RIGHT * 0.2))
        self.at_word(n, "east")
        self.play(FadeIn(rows[1][3], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_04",
            text="Shadow on one side: in the evening, with the shadow on your left, facing south puts east on the left: "
                 "south.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "side")
        self.play(FadeIn(rows[2][:3], shift=RIGHT * 0.2))
        self.at_word(n, "puts")
        self.play(FadeIn(rows[2][3], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_05",
            text="A simple rename: north is called east, a rotation of plus ninety degrees, so west is called north.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "simple")
        self.play(FadeIn(rows[3][:3], shift=RIGHT * 0.2))
        self.at_word(n, "so")
        self.play(FadeIn(rows[3][3], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_06",
            text="An angle rename: north-east is called west, a rotation of plus two hundred and twenty-five degrees, so "
                 "south is called north-east.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "angle")
        self.play(FadeIn(rows[4][:3], shift=RIGHT * 0.2))
        self.at_word(n, "so")
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
            text="Trap one: the shadow in the sun's direction.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "shadow")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_02",
            text="In the evening, which way does your shadow fall?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "evening")
        self.play(FadeIn(ask, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_03",
            text="The wrong instinct: west, because the sun sets in the west.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "instinct")
        self.play(FadeIn(wrong, shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_04",
            text="Correct: the shadow is opposite the sun: east.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "opposite")
        self.play(FadeIn(right, shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_05",
            text="The rule: find the sun first, then turn one hundred and eighty degrees for the shadow.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "first")
        self.play(FadeIn(rule, scale=1.03))
        self.wait_for_narration(n)
        self.clear_stage()

        head, ask, wrong, right, rule = self.show_trap(TRAPS[1])

        n = self.narrate(
            id="traps_06",
            text="Trap two: renaming by similar-sounding logic.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "renaming")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_07",
            text="If north-east is called west, what is south called?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "called")
        self.play(FadeIn(ask, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_08",
            text="The wrong instinct: north-east became west, so south becomes east, or some other pairing by guesswork.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "instinct")
        self.play(FadeIn(wrong, shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_09",
            text="Correct: the rotation is plus two hundred and twenty-five degrees, so south becomes north-east.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "rotation")
        self.play(FadeIn(right, shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_10",
            text="The rule: compute the angle from the given pair, then apply it; never pattern-match labels.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "compute")
        self.play(FadeIn(rule, scale=1.03))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S11_traps")

    # ============================================== 12. CHECKPOINT ==========

    def checkpoint(self):
        self.scene_start("S12_checkpoint", title="Checkpoint")

        head = self.heading("Checkpoint  ·  your turn")
        ask = text("In the evening, your shadow falls to your left.   Which way are you facing?", LABEL, FOCUS, BOLD)
        sky = self.sun_scene("evening")
        steps = VGroup(text("evening:  the shadow falls east", LABEL, INK), text("east on your left means facing south", LABEL, INK, BOLD),
                       pill("south", GOOD, size=BODY)).arrange(DOWN, buff=0.45)
        row = VGroup(sky, steps).arrange(RIGHT, buff=0.9)
        self.stack(head, [ask, row], buff=0.9, top=0.7)
        self.no_overlap(sky, steps)

        n = self.narrate(
            id="checkpoint_01",
            text="Your turn. In the evening, your shadow falls to your left. Which way are you facing?",
            voice="default",
            subtitle=True,
            pause_after=10.0,
        )
        self.at_word(n, "turn")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "evening")
        self.play(FadeIn(ask, shift=UP * 0.1))
        self.at_word(n, "Which")
        self.play(Indicate(ask, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="checkpoint_02",
            text="In the evening the shadow falls east.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "shadow")
        self.play(FadeIn(sky), FadeIn(steps[0], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="checkpoint_03",
            text="East on your left means you are facing south.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "left")
        self.play(FadeIn(steps[1], shift=UP * 0.1))
        self.at_word(n, "south")
        self.play(FadeIn(steps[2], scale=1.03))
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
            text="Level one, question one: in the morning, you face the sun; which way are you facing? Question two: in "
                 "the evening, in which direction does your shadow fall? Question three: in the morning, you walk towards "
                 "your shadow; which way are you walking?",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "sun")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "direction")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.at_word(n, "towards")
        self.play(FadeIn(rows[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="practice_02",
            text="Level two, question four: in the evening, your shadow falls to your left; which way are you facing? "
                 "Question five: in the morning, your shadow falls to your left; which way are you facing? Question six: "
                 "if north is called east, and every direction is rotated the same way, what is west called?",
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
            text="Level three, question seven: if north-east is called west, and every direction is rotated the same way, "
                 "what is south called? Question eight: one morning, A and B stand facing each other, and A's shadow falls "
                 "exactly to B's right; which way is A facing?",
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
            text="One: the morning sun is in the east, so east.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "sun")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "so")
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_02",
            text="Two: opposite the setting sun: east.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "opposite")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "east")
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_03",
            text="Three: the shadow points west, so you walk west.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "points")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "walk")
        self.play(FadeIn(rows[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_04",
            text="Four: the shadow is east, on your left, so you face south.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "left")
        self.play(FadeIn(rows[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "face")
        self.play(FadeIn(rows[3][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Answer key  ·  5 to 8", GOOD)
        table, rows = self.answer_table(head, ANSWERS_B, 5)

        n = self.narrate(
            id="answers_05",
            text="Five: the shadow is west, on your left, so you face north.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "left")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "face")
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_06",
            text="Six: the rotation is plus ninety degrees, and two hundred and seventy plus ninety is three hundred and "
                 "sixty, which is north.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "rotation")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "which")
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_07",
            text="Seven: the rotation is plus two hundred and twenty-five degrees, and one hundred and eighty plus that "
                 "reduces to forty-five: north-east.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "rotation")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "reduces")
        self.play(FadeIn(rows[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_08",
            text="Eight: the shadow, west, is on B's right, so B faces south; A faces B, so A faces north.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "right")
        self.play(FadeIn(rows[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "north")
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
            text="Recognise and move. The recognition cue: the words morning, evening, shadow or sun; or, is called, and "
                 "becomes.",
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
            text="The target time: twenty-five seconds for shadows, thirty seconds for renaming.",
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
            text="The sanity check: for a rotation, opposite directions must stay opposite after renaming.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "sanity")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "opposite")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S15_exam_lens")

    # ============================================== 16. QUICK REVISION AND SUMMARY ==========

    def summary(self):
        self.scene_start("S16_summary", title="Quick Revision and Summary")

        head = self.heading("Quick revision")
        points = VGroup(text("morning shadows point west,  evening shadows east", LABEL, INK, BOLD),
                        text("combine the shadow with left or right to find the facing direction", LABEL, INK, BOLD),
                        text("renamed directions:  find the rotation from one pair, and apply it to all", LABEL, INK, BOLD))\
            .arrange(DOWN, buff=0.45, aligned_edge=LEFT)
        box = VGroup(pill("morning shadow W", GOOD, size=SMALL), pill("evening shadow E", GOOD, size=SMALL), pill("rotation = new − old", GOOD, size=SMALL),
                     pill("apply to all", GOOD, size=SMALL)).arrange(RIGHT, buff=0.3)
        self.stack(head, [points, box], buff=1.1, top=1.1)
        self.no_overlap(*points)
        self.no_overlap(*box)

        n = self.narrate(
            id="summary_01",
            text="Morning shadows point west, evening shadows east.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "Morning")
        self.play(FadeIn(points[0], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_02",
            text="Combine the shadow with left or right to find the facing direction.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Combine")
        self.play(FadeIn(points[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_03",
            text="For renamed directions, find the rotation from one pair, and apply it to all.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "rotation")
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
        nxt = self.breadcrumb("Next", "Video 4 · Relative Position & Coded Directions")
        nxt.next_to(table, DOWN, buff=0.6)
        self.no_overlap(table, nxt)
        self.validator.check_in_frame(VGroup(head, table, nxt))

        n = self.narrate(
            id="section_quiz_07",
            text="The answers. One: the evening shadow points east: option d.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "shadow")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "option")
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="section_quiz_08",
            text="Two: the shadow, west, is on the right, so you face south: option b.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "right")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "option")
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="section_quiz_09",
            text="Three: the rotation is plus ninety degrees, and one hundred and eighty plus ninety is two hundred and "
                 "seventy, west: option a.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "rotation")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "option")
        self.play(FadeIn(rows[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="section_quiz_10",
            text="Four: the rotation is plus ninety degrees, and three hundred and fifteen plus ninety reduces to "
                 "forty-five, north-east: option c.",
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
            text="Five: the shadow, west, is on A's left, so A faces north, and B faces south: option d.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "left")
        self.play(FadeIn(rows[4][:2], shift=RIGHT * 0.2))
        self.at_word(n, "option")
        self.play(FadeIn(rows[4][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="section_quiz_12",
            text="Next: relative position and coded directions.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Next")
        self.play(FadeIn(nxt, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S17_section_quiz")

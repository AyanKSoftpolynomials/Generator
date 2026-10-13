"""
animation.py for the LMS video generator.

Course : Pre-C-CAT - Section A
Module : Module 1 - Logical Reasoning
Lesson : Lesson 2 - Coding & Decoding I: Letter and Number Coding
Topic  : Number Coding (Topic 2)

Source script:
  C:\\Scripts\\Section A\\Module 1 - Logical Reasoning\\Lesson 02 - Coding & Decoding I\\
  Topic 2 - Number Coding.md

Built on the golden-reference pattern:
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``.

Opening: not the first video of the course, so no spoken course welcome.
The module > lesson > topic trail is shown on screen (silent), followed by a
one-idea recap of Topic 1 (the shift row) and what this video covers.

Section map (script heading -> VISUAL PLAN scene):
  S00 Intro (trail + recap)   -> -
  S01 Opening Hook            -> scene 1
  S02 Concept                 -> scene 2
  S03 Letter-by-letter codes  -> scene 3
  S04 Word values             -> scene 4
  S05 Testing candidate rules -> scene 5
  S06-S08 Examples 1-3        -> scene 6
  S09 Exam Application        -> scene 7
  S10 Common Mistake          -> scene 8
  S11-S12 Practice / Answers  -> scene 9
  S13-S14 Revision / Closing  -> scene 10
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

# Semantic colours: one meaning each (same palette as the earlier topics).
FWD = "#4FC3F7"        # forward positions / forward sum
REV = "#F48FB1"        # reverse positions / reverse sum
ANCHOR = "#FFB74D"     # the given code / other candidate rules
OPP = "#CE93D8"        # a second candidate rule
FOCUS = "#FFD54F"      # "look here" / unknown
GOOD = "#66BB6A"       # rule confirmed / answer
BAD = "#EF5350"        # rule rejected / trap

FONT = "Segoe UI"
MIN_FONT = 22          # readable floor: text is never shrunk below this
TITLE = 46
BODY = 30
LABEL = 28
SMALL = 24
NUM = 22
LETTER = 26
MATH = 44

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def pos(ch):
    return ALPHABET.index(ch) + 1


def fsum(word):
    return sum(pos(ch) for ch in word)


def rsum(word):
    return 27 * len(word) - fsum(word)


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


def math_line(*parts, colors=None, size=MATH):
    """MathTex split into ``parts``, each part coloured from ``colors``."""
    colors = colors or {}
    line = MathTex(*parts, font_size=size, color=INK)
    for part, sub in zip(parts, line):
        if part in colors:
            sub.set_color(colors[part])
    return line


def pill(label, color=FOCUS, size=SMALL, fill_opacity=0.14):
    """Short keyword tag. The box is sized from the text, so text cannot escape."""
    t = text(label, size, color, BOLD)
    box = RoundedRectangle(corner_radius=(t.height + 0.26) / 2, width=t.width + 0.5, height=t.height + 0.26,
                           stroke_color=color, stroke_width=2, fill_color=color, fill_opacity=fill_opacity)
    t.move_to(box)
    return VGroup(box, t)


# ==================================================== diagram helpers ====

def tile(ch, side=0.8, color=INK):
    """One letter (or number) in a rounded square."""
    sq = RoundedRectangle(corner_radius=0.1, width=side, height=side, stroke_color=MUTED,
                          stroke_width=2, fill_color=CELL, fill_opacity=1)
    size = int(side * (52 if len(ch) == 1 else 40))
    return VGroup(sq, text(ch, size, color, BOLD).move_to(sq))


def mark_tile(t, color):
    return AnimationGroup(t[0].animate.set_fill(color, 0.3).set_stroke(color, 3), t[1].animate.set_color(color))


def column_xs(n, spacing, centre=ORIGIN):
    """x positions of ``n`` evenly spaced columns centred on ``centre``."""
    return [centre[0] + (k - (n - 1) / 2) * spacing for k in range(n)]


def word_row(word, xs, y, side=0.8, color=INK):
    """A word as tiles in fixed columns."""
    return VGroup(*[tile(ch, side, color).move_to(RIGHT * x + UP * y) for ch, x in zip(word, xs)])


def number_row(values, xs, y, side=0.8, color=FWD):
    """Numbers as tiles, one per column."""
    return VGroup(*[tile(str(v), side, color).move_to(RIGHT * x + UP * y) for v, x in zip(values, xs)])


def positions_under(tiles, word, color=FWD, size=NUM):
    """Each letter's position, placed just below its tile."""
    return VGroup(*[text(str(pos(ch)), size, color, BOLD).next_to(t, DOWN, buff=0.14) for ch, t in zip(word, tiles)])


def verdict(ok, size=LABEL):
    return text("✓" if ok else "✗", size, GOOD if ok else BAD, BOLD)


class RuleTable:
    """The 'rule tester': a header row and word rows in fixed columns.
    ``cell(r, c, s)`` makes the text for row r (0 = first word), column c,
    centred in its column; ``tick(mob, ok)`` places ✓ / ✗ just right of it."""

    def __init__(self, headers, col_x, top_y, row_h=0.8, colors=None):
        colors = colors or [MUTED] * len(headers)
        self.col_x, self.top_y, self.row_h = col_x, top_y, row_h
        self.header = VGroup(*[text(h, SMALL, c, BOLD).move_to(RIGHT * x + UP * top_y)
                               for h, x, c in zip(headers, col_x, colors)])
        left = col_x[0] - 1.2
        right = col_x[-1] + 1.2
        self.rule = Line(RIGHT * left + UP * (top_y - 0.35), RIGHT * right + UP * (top_y - 0.35),
                         color=MUTED, stroke_width=2)

    def at(self, r, c):
        return RIGHT * self.col_x[c] + UP * (self.top_y - 0.35 - (r + 0.6) * self.row_h)

    def cell(self, r, c, s, color=INK, size=LABEL):
        return text(s, size, color, BOLD).move_to(self.at(r, c))

    def tick(self, mob, ok):
        return verdict(ok).next_to(mob, RIGHT, buff=0.15)

    def head(self):
        return VGroup(self.header, self.rule)


# ============================================================= lesson ====

class NumberCodingVideo(LMSScene):
    lesson_title = "Number Coding"

    def construct(self):
        self.camera.background_color = BG

        self.lesson_intro()
        self.hook()
        self.concept()
        self.letter_codes()
        self.word_values()
        self.rule_tester()
        self.example_position()
        self.example_reverse_sum()
        self.example_two_examples()
        self.exam_application()
        self.common_mistake()
        self.practice()
        self.answer()
        self.quick_revision()
        self.closing()

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

    def question_card(self, s, color=FOCUS):
        """The on-screen question: one fitted line (or two) in a card at the top."""
        t = fitted_text(s, SAFE_W - 1.6, BODY, INK, max_lines=2)
        c = self.card(t, color=color)
        return c.move_to(UP * (CARD_TOP - c.height / 2))

    def caption(self, s, color=INK):
        """One-line keyword caption in a fixed-width bar at the bottom of the frame."""
        t = fitted_text(s, SAFE_W - 1.0, BODY, color)
        bar = self.card(t, width=SAFE_W - 0.4, height=t.height + 0.9)
        return bar.move_to(UP * BOTTOM_Y)

    def breadcrumb(self, *parts):
        """Silent 'where are we' trail: Module > Lesson > Topic."""
        colors = [FWD, REV, ANCHOR]
        items = []
        for i, p in enumerate(parts):
            if i:
                items.append(text("›", LABEL, MUTED))
            items.append(pill(p, colors[i % 3], size=SMALL))
        return fit_width(VGroup(*items).arrange(RIGHT, buff=0.25), SAFE_W)

    def verdict_card(self, good, s, width):
        """A ✓ (green) or ✗ (red) card with fitted text."""
        color = GOOD if good else BAD
        body = VGroup(verdict(good, 34), fitted_text(s, width - 1.3, SMALL, color, max_lines=2)).arrange(RIGHT, buff=0.25)
        return self.card(body, width=width, height=1.2, color=color)

    def flip(self, a, b, run_time=0.5):
        """Flip tile ``a`` over to show tile ``b`` (same place)."""
        b.move_to(a).stretch(0.02, 0)
        self.play(a.animate.stretch(0.02, 0), run_time=run_time / 2)
        self.remove(a)
        self.add(b)
        self.play(b.animate.stretch(50, 0), run_time=run_time / 2)

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

    # ========================================= 0. LESSON INTRO ==========
    # Purpose: where we are (silent trail), last time (one idea), today.

    def lesson_intro(self):
        self.scene_start("S00_intro", title="Lesson Introduction")

        crumb = self.breadcrumb("Module 1 · Logical Reasoning", "Lesson 2 · Coding & Decoding I", "Topic 2")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        last = pill("Last time", MUTED, size=SMALL).move_to(UP * 1.9)
        xs = column_xs(5, 1.1)
        plain = word_row("MANGO", xs, 0.9, side=0.75)
        coded = word_row("OCPIQ", xs, -0.5, side=0.75)
        arrows = VGroup(*[Arrow(a.get_bottom(), b.get_top(), buff=0.08, color=MUTED, stroke_width=3,
                                max_tip_length_to_length_ratio=0.2) for a, b in zip(plain, coded)])
        shifts = VGroup(*[pill("+2", ANCHOR, size=SMALL).next_to(t, DOWN, buff=0.2) for t in coded])
        recap = VGroup(last, plain, arrows, coded, shifts)
        self.validator.check_in_frame(VGroup(crumb, recap))

        # SEE (silent): the trail.  HEAR: the shift row from last time.
        n = self.narrate(
            id="intro_01",
            text="Last time, you cracked letter codes by writing the shift row: how far each letter moved.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.play(FadeIn(last), FadeIn(plain), FadeIn(arrows), FadeIn(coded))
        self.at_word(n, "shift")
        self.play(LaggedStart(*[FadeIn(s, shift=UP * 0.15) for s in shifts], lag_ratio=0.2))
        self.wait_for_narration(n)

        # HEAR: today, letters become numbers.  SEE: the title.
        title = fitted_text("Number Coding", SAFE_W, 72, INK, BOLD)
        underline = Line(LEFT, RIGHT, color=FWD, stroke_width=5).set_width(title.width * 0.6)
        VGroup(title, underline).arrange(DOWN, buff=0.2).move_to(UP * 0.2)
        n = self.narrate(
            id="intro_02",
            text="In this video, the letters turn into numbers.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(recap, shift=UP * 0.3))
        self.at_word(n, "numbers")
        self.play(Write(title), run_time=1.1)
        self.play(GrowFromCenter(underline))
        self.wait_for_narration(n)

        # HEAR: the three objectives.  SEE: one row per objective, on its word.
        goals = [
            ("Encode and decode words written as positions", FWD),
            ("Work out a word's value, forward or reverse", REV),
            ("Use a second example to rule out wrong rules", GOOD),
        ]
        rows = VGroup(*[VGroup(pill(str(i + 1), c, size=SMALL), fitted_text(s, SAFE_W - 2.4, BODY, INK))
                        .arrange(RIGHT, buff=0.35) for i, (s, c) in enumerate(goals)])
        rows.arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        heading = text("By the end of this video, you will:", LABEL, MUTED, BOLD)
        objectives = self.card(VGroup(heading, rows).arrange(DOWN, buff=0.4, aligned_edge=LEFT))
        small_title = title.copy().scale(0.6)
        small_title.next_to(crumb, DOWN, buff=0.3)
        objectives.next_to(small_title, DOWN, buff=0.35)
        self.validator.check_in_frame(VGroup(crumb, small_title, objectives))
        n = self.narrate(
            id="intro_03",
            text="By the end of this video, you'll be able to encode and decode words written as letter positions, "
                 "work out a word's value, and use a second example to rule out rules that only fit by coincidence.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(underline), ReplacementTransform(title, small_title), run_time=0.8)
        self.play(FadeIn(objectives[0]), FadeIn(heading))
        for row, spoken in zip(rows, ["encode", "value", "second"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.5)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_intro")

    # ================================================= 1. HOOK ==========
    # Purpose: a word coded as one number; the rule hides in the positions.

    def hook(self):
        self.scene_start("S01_hook", title="Opening Hook")

        box_eq = VGroup(text("BOX", 64, INK, BOLD), text("=", 64, MUTED), text("40", 64, ANCHOR, BOLD))
        box_eq.arrange(RIGHT, buff=0.35)
        fan_eq = VGroup(text("FAN", 64, INK, BOLD), text("=", 64, MUTED), text("?", 64, FOCUS, BOLD))
        fan_eq.arrange(RIGHT, buff=0.35)
        pair = VGroup(box_eq, fan_eq).arrange(RIGHT, buff=2.0).move_to(UP * 1.6)

        n = self.narrate(
            id="hook_01",
            text="In a certain code, BOX is written as forty. What is FAN?",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(box_eq[0], shift=DOWN * 0.2))
        self.at_word(n, "forty")
        self.play(FadeIn(box_eq[1:], shift=LEFT * 0.2))
        self.at_word(n, "FAN")
        self.play(FadeIn(fan_eq, shift=DOWN * 0.2))
        self.wait_for_narration(n)

        # HEAR: one number; a rule built from positions.  SEE: BOX's tiles
        # with their positions, and a "rule ?" arrow to 40.
        xs = column_xs(3, 1.2, LEFT * 2.2)
        tiles = word_row("BOX", xs, -0.4, side=0.9)
        nums = positions_under(tiles, "BOX", size=LABEL)
        forty = text("40", 60, ANCHOR, BOLD).move_to(RIGHT * 3.2 + DOWN * 0.4)
        arrow = Arrow(tiles.get_right(), forty.get_left(), buff=0.4, color=MUTED, stroke_width=5)
        rule = pill("rule ?", FOCUS, size=SMALL).next_to(arrow, UP, buff=0.12)
        self.validator.check_in_frame(VGroup(pair, tiles, nums, forty))
        n = self.narrate(
            id="hook_02",
            text="There are no letters in the answer this time. The word has been turned into a single number. "
                 "Somewhere between BOX and forty is a rule, and it's almost always built from the letter positions "
                 "you already know.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "single")
        self.play(Indicate(box_eq[2], color=ANCHOR, scale_factor=1.2))
        self.at_word(n, "between")
        self.play(FadeIn(tiles, shift=UP * 0.2), FadeIn(forty), GrowArrow(arrow))
        self.at_word(n, "rule")
        self.play(FadeIn(rule, shift=DOWN * 0.1))
        self.at_word(n, "positions")
        self.play(LaggedStart(*[FadeIn(x, shift=UP * 0.1) for x in nums], lag_ratio=0.3))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_03",
            text="Let's see how to find it.",
            voice="default",
            subtitle=True,
        )
        self.play(Indicate(rule, color=FOCUS, scale_factor=1.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S01_hook")

    # ============================================== 2. CONCEPT ==========
    # Purpose: letters become numbers, almost always via positions.

    def concept(self):
        self.scene_start("S02_concept", title="Concept Introduction")

        c_tile = tile("C", 1.6).move_to(UP * 1.2)
        three = tile("3", 1.6, FWD)
        kinds = VGroup(pill("each letter  →  its own number", FWD, size=LABEL),
                       pill("whole word  →  one value", REV, size=LABEL)).arrange(RIGHT, buff=0.6)
        kinds.move_to(DOWN * 0.8)
        self.validator.check_in_frame(VGroup(c_tile, kinds))

        # HEAR: letters are replaced by numbers.  SEE: C flips to show 3; then
        # the two kinds of number code, on the words that name them.
        n = self.narrate(
            id="concept_01",
            text="In number coding, letters are replaced by numbers. Most of the time, the numbers come from letter "
                 "positions. Either each letter becomes its own number, or the whole word becomes a single value "
                 "calculated from those positions.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(c_tile, scale=0.9))
        self.at_word(n, "replaced")
        self.flip(c_tile, three)
        self.at_word(n, "Either")
        self.play(FadeIn(kinds[0], shift=UP * 0.2))
        self.at_word(n, "whole")
        self.play(FadeIn(kinds[1], shift=UP * 0.2))
        self.wait_for_narration(n)

        # HEAR: it's position arithmetic; EJOTY and 27 are the tools.
        tools = VGroup(pill("EJOTY", ANCHOR), pill("rule of 27", GOOD)).arrange(RIGHT, buff=0.5)
        tools.move_to(DOWN * 1.9)
        n = self.narrate(
            id="concept_02",
            text="So number coding is really position arithmetic. If you can find positions quickly with EJOTY and "
                 "the rule of twenty-seven, you already have most of what you need.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "arithmetic")
        cap = self.caption("Number coding  =  position arithmetic", FOCUS)
        self.play(FadeIn(cap, shift=UP * 0.2))
        self.at_word(n, "EJOTY")
        self.play(FadeIn(tools[0], shift=UP * 0.2))
        self.at_word(n, "rule")
        self.play(FadeIn(tools[1], shift=UP * 0.2))
        self.validator.check_in_frame(VGroup(three, kinds, tools, cap))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_concept")

    # ================================= 3. LETTER-BY-LETTER CODES ==========

    def letter_codes(self):
        self.scene_start("S03_letter_codes", title="Explanation - Letter-by-letter Codes")

        # Three rows: label | CAT | → | numbers.  All rows share columns.
        word_xs = column_xs(3, 0.95, LEFT * 1.3)
        num_xs = column_xs(3, 1.15, RIGHT * 3.6)
        ys = [1.9, 0.6, -0.7]
        specs = [("Forward", [3, 1, 20], FWD), ("Reverse", [24, 26, 7], REV), ("Position + 1", [4, 2, 21], ANCHOR)]
        rows = []
        for (label, values, c), y in zip(specs, ys):
            lab = pill(label, c, size=SMALL).move_to(RIGHT * -4.9 + UP * y)
            cat = word_row("CAT", word_xs, y, side=0.75)
            arr = Arrow(cat.get_right(), RIGHT * (num_xs[0] - 0.55) + UP * y, buff=0.2, color=MUTED, stroke_width=4)
            nums = number_row(values, num_xs, y, side=0.85, color=c)
            rows.append(VGroup(lab, cat, arr, nums))
        self.validator.check_in_frame(VGroup(*rows))

        n = self.narrate(
            id="letters_01",
            text="The simplest form writes each letter as its position. CAT becomes three, one, twenty.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(rows[0][:3]))
        self.at_word(n, "becomes")
        self.play(LaggedStart(*[FadeIn(t, shift=LEFT * 0.15) for t in rows[0][3]], lag_ratio=0.3))
        self.wait_for_narration(n)

        n = self.narrate(
            id="letters_02",
            text="A variation uses reverse positions. Then CAT becomes twenty-four, twenty-six, seven.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(rows[1][:3]))
        self.at_word(n, "becomes")
        self.play(LaggedStart(*[FadeIn(t, shift=LEFT * 0.15) for t in rows[1][3]], lag_ratio=0.3))
        self.wait_for_narration(n)

        n = self.narrate(
            id="letters_03",
            text="Another adds or subtracts a constant from each position.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(rows[2][:3]))
        self.play(LaggedStart(*[FadeIn(t, shift=LEFT * 0.15) for t in rows[2][3]], lag_ratio=0.3))
        self.wait_for_narration(n)

        # HEAR: compare the code with the forward positions.  SEE: the forward
        # row pulses against each code row in turn.
        n = self.narrate(
            id="letters_04",
            text="Identifying which variation is used works just like the shift row in letter coding. Write each "
                 "letter's forward position under the code number, and see how they relate.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "forward")
        self.play(Indicate(rows[0][3], color=FWD))
        self.at_word(n, "relate")
        self.play(Indicate(rows[1][3], color=REV), Indicate(rows[2][3], color=ANCHOR))
        self.wait_for_narration(n)

        # HEAR: concatenated codes; split into valid positions.  SEE: 3120,
        # then the wrong split (3 | 12 | 0) crossed, the right split ticked.
        self.play(FadeOut(VGroup(*rows)))
        string = VGroup(text("CAT", 56, INK, BOLD), text("→", 56, MUTED), text("3120", 56, FWD, BOLD))
        string.arrange(RIGHT, buff=0.4).move_to(UP * 1.6)
        wrong = VGroup(*[pill(s, BAD if s == "0" else INK, size=LABEL, fill_opacity=0.06) for s in ["3", "12", "0"]])
        wrong.arrange(RIGHT, buff=0.25)
        wrong_line = VGroup(wrong, verdict(False), text("0 is not a position", SMALL, BAD)).arrange(RIGHT, buff=0.35)
        right = VGroup(*[pill(s, GOOD, size=LABEL) for s in ["3", "1", "20"]]).arrange(RIGHT, buff=0.25)
        right_line = VGroup(right, verdict(True), text("C · A · T", SMALL, GOOD)).arrange(RIGHT, buff=0.35)
        splits = VGroup(wrong_line, right_line).arrange(DOWN, buff=0.5, aligned_edge=LEFT).move_to(DOWN * 0.4)
        self.validator.check_in_frame(VGroup(string, splits))
        n = self.narrate(
            id="letters_05",
            text="Sometimes the numbers are written together as one string: CAT becomes three-one-two-zero. When "
                 "decoding a string like this, split it carefully. Three, twelve, zero is impossible, because zero "
                 "isn't a letter position. Three, one, twenty is the only valid reading.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "string", occurrence=1)
        self.play(FadeIn(string, shift=DOWN * 0.2))
        self.at_word(n, "split")
        self.play(Indicate(string[2], color=FOCUS, scale_factor=1.15))
        self.at_word(n, "impossible")
        self.play(FadeIn(wrong_line, shift=RIGHT * 0.2))
        self.at_word(n, "only")
        self.play(FadeIn(right_line, shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_letter_codes")

    # ============================================ 4. WORD VALUES ==========

    def word_values(self):
        self.scene_start("S04_word_values", title="Explanation - Word Values")

        rule = self.card(text("Word value  =  sum of letter positions", LABEL, INK, BOLD,
                              t2c={"sum of letter positions": FWD}), color=FWD)
        rule.move_to(UP * (CARD_TOP - rule.height / 2))
        xs = column_xs(3, 1.2, LEFT * 3.2)
        cat = word_row("CAT", xs, 0.7, side=0.85)
        nums = positions_under(cat, "CAT", size=LABEL)
        fwd = math_line("3", "+", "1", "+", "20", "=", "24", colors={"24": FWD}, size=46)
        fwd.move_to(RIGHT * 2.6 + UP * 0.5)

        n = self.narrate(
            id="values_01",
            text="The second form gives the whole word a single number. The most common rule is the sum of the letter "
                 "positions. CAT is three plus one plus twenty, which is twenty-four.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(cat, shift=UP * 0.2))
        self.at_word(n, "sum")
        self.play(FadeIn(rule, shift=DOWN * 0.2), FadeIn(nums))
        self.at_word(n, "plus", occurrence=1)
        self.play(Write(fwd))
        self.wait_for_narration(n)

        # HEAR: the reverse-sum shortcut.  SEE: the shortcut card, then CAT's
        # reverse sum worked out.
        shortcut = self.card(text("Reverse sum  =  27 × (number of letters)  −  forward sum", SMALL, INK, BOLD,
                                  t2c={"Reverse sum": REV, "27": ANCHOR, "forward sum": FWD}), color=REV)
        shortcut.move_to(DOWN * 1.0)
        rev = math_line(r"27\times 3", "-", "24", "=", "81", "-", "24", "=", "57",
                        colors={"24": FWD, "57": REV}, size=44).next_to(shortcut, DOWN, buff=0.4)
        self.validator.check_in_frame(VGroup(rule, cat, nums, shortcut, rev))
        n = self.narrate(
            id="values_02",
            text="The sum can also use reverse positions. Here, the shortcut from the Alphabet Test saves time. Each "
                 "letter's forward and reverse positions add up to twenty-seven, so the reverse sum is twenty-seven "
                 "times the number of letters, minus the forward sum.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "shortcut")
        self.play(FadeIn(shortcut, shift=UP * 0.2))
        self.at_word(n, "times")
        self.play(Indicate(shortcut[1], color=ANCHOR, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="values_03",
            text="For CAT, that's eighty-one minus twenty-four, which is fifty-seven.",
            voice="default",
            subtitle=True,
        )
        self.play(Write(rev))
        self.wait_for_narration(n)

        # HEAR: operations on the sum.  SEE: three variation tags.
        variations = VGroup(pill("sum × k", ANCHOR), pill("sum + k", ANCHOR), pill("sum × number of letters", ANCHOR))
        variations.arrange(RIGHT, buff=0.35).move_to(UP * BOTTOM_Y)
        n = self.narrate(
            id="values_04",
            text="Some codes go one step further and multiply or adjust the sum. For example, the code might be twice "
                 "the sum, or the sum plus a constant.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "multiply")
        self.play(LaggedStart(*[FadeIn(v, shift=UP * 0.2) for v in variations], lag_ratio=0.3))
        self.validator.check_in_frame(VGroup(rev, variations))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_word_values")

    # ========================================= 5. THE RULE TESTER ==========

    def rule_tester(self):
        self.scene_start("S05_tester", title="Explanation - Testing Candidate Rules")

        table = RuleTable(["Word", "Given code", "Forward sum", "Reverse sum", "Other rule"],
                          [-5.2, -2.8, -0.2, 2.5, 5.1], 2.4,
                          colors=[MUTED, ANCHOR, FWD, REV, OPP])
        blank = VGroup(table.cell(0, 0, "?", MUTED), table.cell(0, 1, "?", MUTED))
        steps = VGroup(pill("1st", FWD, size=SMALL).next_to(table.header[2], UP, buff=0.2),
                       pill("2nd", REV, size=SMALL).next_to(table.header[3], UP, buff=0.2),
                       pill("3rd", OPP, size=SMALL).next_to(table.header[4], UP, buff=0.2))
        self.validator.check_in_frame(VGroup(steps, table.head(), blank))

        n = self.narrate(
            id="tester_01",
            text="When a word is coded as a single number, the fastest approach is to test a short list of candidate "
                 "rules in order.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(table.head()), FadeIn(blank))
        self.wait_for_narration(n)

        # HEAR: forward sum, reverse sum, simple operation.  SEE: the columns
        # numbered in testing order.
        n = self.narrate(
            id="tester_02",
            text="First, is it the forward sum? Second, is it the reverse sum? Third, is it a simple multiple of "
                 "either, or the sum plus a constant?",
            voice="default",
            subtitle=True,
        )
        for step, col, spoken in zip(steps, [2, 3, 4], ["First", "Second", "Third"]):
            self.at_word(n, spoken)
            self.play(FadeIn(step, shift=DOWN * 0.1), Indicate(table.header[col], scale_factor=1.15), run_time=0.6)
        self.wait_for_narration(n)

        # HEAR: one example can fit several rules; the rule must fit both.
        n = self.narrate(
            id="tester_03",
            text="There's an important subtlety. With only one example, more than one rule can match by coincidence. "
                 "That's why many questions give two coded words. The correct rule must fit both, and the second "
                 "example is there to eliminate the rules that only seem right.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "coincidence")
        warn = pill("one example can fit several rules", BAD, size=LABEL).move_to(DOWN * 0.6)
        self.play(FadeIn(warn, scale=1.1))
        self.at_word(n, "both")
        cap = self.caption("Two examples given?  The rule must fit both", GOOD)
        self.play(FadeIn(cap, shift=UP * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_tester")

    # ================================= 6. EXAMPLE 1: POSITION CODE ==========

    def example_position(self):
        self.scene_start("S06_example_position", title="Example 1 - Position Code")

        question = self.question_card("JAM → 10 · 1 · 13.   How is PEN coded?")
        xs = column_xs(3, 1.3, LEFT * 3.3)
        jam = word_row("JAM", xs, 0.9, side=0.85)
        jam_code = number_row([10, 1, 13], xs, -0.5, side=0.85)
        pxs = column_xs(3, 1.3, RIGHT * 3.3)
        pen = word_row("PEN", pxs, 0.9, side=0.85)
        pen_code = number_row([16, 5, 14], pxs, -0.5, side=0.85, color=GOOD)
        divider = DashedLine(UP * 1.6, DOWN * 1.2, color=MUTED)
        forward = pill("forward positions", FWD, size=LABEL).move_to(DOWN * 1.9)
        self.validator.check_in_frame(VGroup(question, jam, jam_code, pen_code, forward))

        n = self.narrate(
            id="ex1_01",
            text="If JAM is coded as ten, one, thirteen, how is PEN coded?",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(question, shift=DOWN * 0.3))
        self.play(FadeIn(jam), FadeIn(jam_code))
        self.wait_for_narration(n)

        # HEAR: J 10, A 1, M 13 = forward; PEN = 16, 5, 14.
        n = self.narrate(
            id="ex1_02",
            text="J is ten, A is one, and M is thirteen. These are simply forward positions. "
                 "So PEN is sixteen, five, fourteen.",
            voice="default",
            subtitle=True,
        )
        for k, spoken in enumerate(["ten", "one", "thirteen"]):
            self.at_word(n, spoken)
            self.play(Indicate(VGroup(jam[k], jam_code[k]), color=FWD), run_time=0.5)
        self.at_word(n, "forward")
        self.play(FadeIn(forward, scale=1.1))
        self.play(Create(divider), FadeIn(pen))
        for k, spoken in enumerate(["sixteen", "five", "fourteen"]):
            self.at_word(n, spoken)
            self.play(FadeIn(pen_code[k], shift=DOWN * 0.15), run_time=0.4)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_example_position")

    # ============================== 7. EXAMPLE 2: REVERSE-SUM CODE ==========

    def example_reverse_sum(self):
        self.scene_start("S07_example_reverse", title="Example 2 - Reverse-sum Code")

        question = self.question_card("BOX = 40.   FAN = ?")
        table = RuleTable(["Word", "Given code", "Forward sum", "Reverse sum"], [-4.8, -2.0, 1.0, 4.2], 2.0,
                          colors=[MUTED, ANCHOR, FWD, REV])
        box_word, box_code = table.cell(0, 0, "BOX"), table.cell(0, 1, "40", ANCHOR)
        fan_word, fan_code = table.cell(1, 0, "FAN"), table.cell(1, 1, "?", FOCUS)
        box_f = table.cell(0, 2, "41", FWD)
        box_r = table.cell(0, 3, "40", REV)
        fan_f = table.cell(1, 2, "21", FWD)
        fan_r = table.cell(1, 3, "60", GOOD)
        work_y = table.at(1, 0)[1] - 1.0
        work_f = math_line("2", "+", "15", "+", "24", "=", "41", colors={"41": FWD}, size=40).move_to(UP * work_y)
        work_r = math_line(r"27\times 3", "=", "81", ",", r"\;81-41", "=", "40",
                           colors={"40": REV}, size=40).move_to(UP * work_y)
        work_fan = math_line("6", "+", "1", "+", "14", "=", "21", r"\;\rightarrow\;", "81-21", "=", "60",
                             colors={"21": FWD, "60": GOOD}, size=40).move_to(UP * work_y)
        self.validator.check_in_frame(VGroup(question, table.head(), fan_word, work_fan))

        n = self.narrate(
            id="ex2_01",
            text="Now back to our opening question. BOX is forty. What is FAN?",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(question, shift=DOWN * 0.3))
        self.play(FadeIn(table.head()), FadeIn(VGroup(box_word, box_code)))
        self.at_word(n, "FAN")
        self.play(FadeIn(VGroup(fan_word, fan_code)))
        self.wait_for_narration(n)

        # HEAR: forward sum = 41, not 40.  SEE: the working, then 41 ✗.
        n = self.narrate(
            id="ex2_02",
            text="Test the forward sum first. B is two, O is fifteen, and X is twenty-four, which gives forty-one. "
                 "That's not forty.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "two")
        self.play(Write(work_f))
        self.at_word(n, "gives")
        self.play(TransformFromCopy(work_f[-1], box_f))
        self.at_word(n, "not")
        box_f_mark = table.tick(box_f, False)
        self.play(FadeIn(box_f_mark, scale=1.3))
        self.wait_for_narration(n)

        # HEAR: reverse sum = 81 - 41 = 40 ✓.
        n = self.narrate(
            id="ex2_03",
            text="Next, test the reverse sum. Using the shortcut, twenty-seven times three is eighty-one, minus "
                 "forty-one, which is exactly forty. That's the rule.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "shortcut")
        self.play(ReplacementTransform(work_f, work_r))
        self.at_word(n, "exactly")
        self.play(TransformFromCopy(work_r[-1], box_r))
        box_r_mark = table.tick(box_r, True)
        self.play(FadeIn(box_r_mark, scale=1.3))
        self.at_word(n, "rule")
        frame = SurroundingRectangle(VGroup(table.header[3], box_r), color=GOOD, buff=0.15)
        self.play(Create(frame))
        self.wait_for_narration(n)

        # HEAR: FAN: 21 forward, 60 reverse.  SEE: FAN's row fills; 60 moves
        # into the code column.
        n = self.narrate(
            id="ex2_04",
            text="For FAN, the forward positions are six, one and fourteen, which add up to twenty-one. The reverse "
                 "sum is eighty-one minus twenty-one, which is sixty.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "six")
        self.play(ReplacementTransform(work_r, work_fan))
        self.at_word(n, "add")
        self.play(FadeIn(fan_f))
        self.at_word(n, "reverse")
        self.play(FadeIn(fan_r))
        self.at_word(n, "sixty")
        answer = table.cell(1, 1, "60", GOOD)
        self.play(ReplacementTransform(fan_code, answer), Flash(answer, color=GOOD))
        self.wait_for_narration(n)

        n = self.narrate(
            id="ex2_05",
            text="Notice that twenty-one, the forward sum, would almost certainly appear among the wrong options.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "wrong")
        self.play(fan_f.animate.set_color(BAD), Indicate(fan_f, color=BAD, scale_factor=1.3))
        cap = self.caption("The forward sum (21) is the trap option", BAD)
        self.play(FadeIn(cap, shift=UP * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S07_example_reverse")

    # ========================== 8. EXAMPLE 3: TWO EXAMPLES, ONE RULE ==========

    def example_two_examples(self):
        self.scene_start("S08_example_two", title="Example 3 - Two Examples, One Rule")

        question = self.question_card("BAG = 20,   DOG = 52.   HEN = ?")
        table = RuleTable(["Word", "Given code", "Forward sum", "sum × 2", "sum + 10"], [-5.3, -3.0, -0.4, 2.3, 5.0],
                          2.0, colors=[MUTED, ANCHOR, FWD, GOOD, OPP])
        words = ["BAG", "DOG", "HEN"]
        codes = ["20", "52", "?"]
        word_cells = VGroup(*[table.cell(r, 0, w) for r, w in enumerate(words)])
        code_cells = VGroup(*[table.cell(r, 1, c, FOCUS if c == "?" else ANCHOR) for r, c in enumerate(codes)])
        sums = [table.cell(r, 2, str(fsum(w)), FWD) for r, w in enumerate(words)]
        doubles = [table.cell(r, 3, str(2 * fsum(w)), GOOD) for r, w in enumerate(words)]
        plus10 = [table.cell(r, 4, str(fsum(w) + 10), OPP) for r, w in enumerate(words[:2])]
        self.validator.check_in_frame(VGroup(question, table.head(), word_cells))

        n = self.narrate(
            id="ex3_01",
            text="In a certain code, BAG is written as twenty and DOG as fifty-two. How is HEN written?",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(question, shift=DOWN * 0.3))
        self.play(FadeIn(table.head()))
        for r, spoken in enumerate(words):
            self.at_word(n, spoken)
            self.play(FadeIn(VGroup(word_cells[r], code_cells[r]), shift=RIGHT * 0.2), run_time=0.4)
        self.wait_for_narration(n)

        # HEAR: BAG: sum 10; ×2 and +10 both give 20.  SEE: both candidate
        # cells tick; a "can't tell yet" tag.
        tie = pill("one example: can't tell them apart", FOCUS, size=SMALL).move_to(DOWN * 1.9)
        n = self.narrate(
            id="ex3_02",
            text="Start with BAG. Its forward sum is two plus one plus seven, which is ten. Two rules could turn ten "
                 "into twenty: multiplying by two, or adding ten. One example can't tell them apart.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "seven")
        self.play(FadeIn(sums[0], shift=LEFT * 0.1))
        self.at_word(n, "multiplying")
        m1 = table.tick(doubles[0], True)
        self.play(FadeIn(doubles[0]), FadeIn(m1))
        self.at_word(n, "adding")
        m2 = table.tick(plus10[0], True)
        self.play(FadeIn(plus10[0]), FadeIn(m2))
        self.at_word(n, "apart")
        self.play(FadeIn(tie, scale=1.1))
        self.wait_for_narration(n)

        # HEAR: DOG: sum 26; ×2 = 52 ✓, +10 = 36 ✗.  SEE: the +10 column is
        # struck out; the ×2 column framed.
        n = self.narrate(
            id="ex3_03",
            text="Now use DOG. Its forward sum is four plus fifteen plus seven, which is twenty-six. Twice twenty-six "
                 "is fifty-two, which matches. Twenty-six plus ten is thirty-six, which doesn't. So the rule is twice "
                 "the sum of the positions.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(tie))
        self.at_word(n, "seven")
        self.play(FadeIn(sums[1], shift=LEFT * 0.1))
        self.at_word(n, "matches")
        m3 = table.tick(doubles[1], True)
        self.play(FadeIn(doubles[1]), FadeIn(m3))
        self.at_word(n, "doesn't")
        m4 = table.tick(plus10[1], False)
        strike = Line(table.header[4].get_top() + UP * 0.1, plus10[1].get_bottom() + DOWN * 0.15,
                      color=BAD, stroke_width=4).set_x(table.col_x[4])
        self.play(FadeIn(plus10[1]), FadeIn(m4))
        self.play(Create(strike), VGroup(table.header[4], plus10[0], m2).animate.set_opacity(0.4))
        self.at_word(n, "rule")
        frame = SurroundingRectangle(VGroup(table.header[3], m3), color=GOOD, buff=0.15)
        self.play(Create(frame))
        self.wait_for_narration(n)

        # HEAR: HEN: 27, twice = 54.  SEE: HEN's row; 54 into the code column.
        n = self.narrate(
            id="ex3_04",
            text="For HEN, eight plus five plus fourteen is twenty-seven. Twice that is fifty-four.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "fourteen")
        self.play(FadeIn(sums[2], shift=LEFT * 0.1))
        self.at_word(n, "Twice")
        self.play(FadeIn(doubles[2]))
        answer = table.cell(2, 1, "54", GOOD)
        self.play(ReplacementTransform(code_cells[2], answer), Flash(answer, color=GOOD))
        self.validator.check_in_frame(VGroup(question, table.head(), answer, frame))
        self.wait_for_narration(n)

        n = self.narrate(
            id="ex3_05",
            text="This is exactly why the second example exists. A solver who stopped after BAG had a fifty-fifty "
                 "chance of choosing the wrong rule.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "second")
        self.play(Indicate(VGroup(word_cells[1], sums[1], doubles[1], plus10[1]), color=FOCUS, scale_factor=1.05))
        cap = self.caption("The second example eliminates the rule that only fit by chance", FOCUS)
        self.play(FadeIn(cap, shift=UP * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S08_example_two")

    # ======================================== 9. EXAM APPLICATION ==========

    def exam_application(self):
        self.scene_start("S09_exam", title="Exam Application")

        specs = [("Several numbers", "letter-by-letter code: compare with forward and reverse positions", FWD),
                 ("One number", "word value: forward sum → reverse sum → simple operation", REV),
                 ("Two examples", "the rule must fit both", GOOD)]
        heads = VGroup(*[pill(h, c, size=SMALL) for h, _, c in specs])
        bodies = VGroup(*[fitted_text(b, SAFE_W - 5.2, SMALL, INK, max_lines=2) for _, b, _ in specs])
        rows = VGroup()
        for k, (h, b) in enumerate(zip(heads, bodies)):
            y = -k * 0.95
            h.move_to(UP * y, aligned_edge=LEFT).shift(LEFT * 6.0)
            b.move_to(UP * y, aligned_edge=LEFT).shift(LEFT * 2.6)
            rows.add(VGroup(h, text("→", LABEL, MUTED).move_to(LEFT * 3.0 + UP * y), b))
        heading = text("Look at the shape of the code", LABEL, MUTED, BOLD)
        decision = self.card(VGroup(heading, rows).arrange(DOWN, buff=0.35, aligned_edge=LEFT)).move_to(UP * 0.4)
        self.validator.check_in_frame(decision)

        n = self.narrate(
            id="exam_01",
            text="In the exam, first look at the shape of the code. If there's one number per letter, it's a "
                 "letter-by-letter code, so compare it with the forward and reverse positions. If the whole word "
                 "becomes one number, it's a word value. Test the forward sum, then the reverse sum, then a simple "
                 "operation on either.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(decision[0]), FadeIn(heading))
        self.at_word(n, "per")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "whole")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_02",
            text="When two examples are given, confirm your rule on both before calculating the answer.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(rows[2], shift=RIGHT * 0.2))
        self.at_word(n, "both")
        self.play(Indicate(rows[2], color=GOOD, scale_factor=1.03))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S09_exam")

    # =========================================== 10. COMMON MISTAKE ==========
    # Three rows of ✗ | ✓ cards, one row per mistake.

    def common_mistake(self):
        self.scene_start("S10_mistake", title="Common Mistake")

        card_w = ZONE_W - 0.3
        pairs = [
            (self.verdict_card(False, "Stop at the first rule that fits BAG", card_w),
             self.verdict_card(True, "Check that rule on DOG too", card_w)),
            (self.verdict_card(False, "3120  →  3 · 12 · 0", card_w),
             self.verdict_card(True, "3120  →  3 · 1 · 20", card_w)),
            (self.verdict_card(False, "Reverse sum = 26 × n − forward sum", card_w),
             self.verdict_card(True, "Reverse sum = 27 × n − forward sum", card_w)),
        ]
        for (wrong, right), y in zip(pairs, [1.6, 0.05, -1.5]):
            wrong.move_to(LEFT_ZONE + UP * y)
            right.move_to(RIGHT_ZONE + UP * y)
        header = pill("3 mistakes", BAD, size=LABEL).move_to(UP * (CARD_TOP - 0.3))
        self.validator.check_in_frame(VGroup(header, *[c for p in pairs for c in p]))

        n = self.narrate(
            id="mistake_01",
            text="The first mistake is stopping at the first rule that works for one example. As we just saw, BAG "
                 "equals twenty fits two different rules. Always check the second example.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(header))
        self.at_word(n, "stopping")
        self.play(FadeIn(pairs[0][0], shift=RIGHT * 0.3))
        self.at_word(n, "Always")
        self.play(FadeIn(pairs[0][1], shift=LEFT * 0.3))
        self.wait_for_narration(n)

        n = self.narrate(
            id="mistake_02",
            text="The second mistake is splitting concatenated codes wrongly. When digits run together, use validity "
                 "to guide you. Positions run only from one to twenty-six, and none of them is zero.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "splitting")
        self.play(FadeIn(pairs[1][0], shift=RIGHT * 0.3))
        self.at_word(n, "validity")
        self.play(FadeIn(pairs[1][1], shift=LEFT * 0.3))
        self.wait_for_narration(n)

        n = self.narrate(
            id="mistake_03",
            text="The third mistake is the familiar one: using twenty-six instead of twenty-seven in the reverse "
                 "shortcut. It shifts every reverse position, and the total, by one per letter.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "familiar")
        self.play(FadeIn(pairs[2][0], shift=RIGHT * 0.3))
        self.at_word(n, "instead")
        self.play(FadeIn(pairs[2][1], shift=LEFT * 0.3))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S10_mistake")

    # ================================================ 11. PRACTICE ==========

    def practice(self):
        self.scene_start("S11_practice", title="Practice Question")

        card_w = SAFE_W - 1.0
        q1 = VGroup(pill("Q1", FOCUS), fitted_text("If CAT is coded as 3120, how is DOG coded?", card_w - 1.6, BODY))
        q2 = VGroup(pill("Q2", FOCUS), fitted_text("If ACE = 72 and BAD = 74, what is CAB?", card_w - 1.6, BODY))
        for q in (q1, q2):
            q.arrange(RIGHT, buff=0.35)
        questions = VGroup(q1, q2).arrange(DOWN, buff=0.6, aligned_edge=LEFT)
        board = self.card(questions, color=FOCUS).move_to(UP * 0.4)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="practice_01",
            text="Try these two.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(board[0]), FadeIn(questions, shift=UP * 0.2))
        self.play(questions.animate.set_opacity(0.45))
        self.wait_for_narration(n)

        n = self.narrate(
            id="practice_02",
            text="First, if CAT is coded as three-one-two-zero, how is DOG coded?",
            voice="default",
            subtitle=True,
        )
        self.play(q1.animate.set_opacity(1))
        self.wait_for_narration(n)

        # SILENCE (pause_after): countdown ring while the learner thinks.
        n = self.narrate(
            id="practice_03",
            text="Second, if ACE equals seventy-two and BAD equals seventy-four, what is CAB?",
            voice="default",
            subtitle=True,
            pause_after=8.0,
        )
        self.play(q2.animate.set_opacity(1))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        self.clear_stage()
        self.scene_end("S11_practice")

    # ================================================== 12. ANSWER ==========

    def answer(self):
        self.scene_start("S12_answer", title="Answer and Explanation")

        # Q1: DOG -> 4 15 7 -> 4157.
        tag_q1 = pill("Q1", FOCUS).move_to(UP * (CARD_TOP - 0.3))
        xs = column_xs(3, 1.4, LEFT * 2.0)
        dog = word_row("DOG", xs, 1.2, side=0.9)
        dog_nums = number_row([4, 15, 7], xs, -0.2, side=0.9)
        joined = text("4157", 64, GOOD, BOLD).move_to(RIGHT * 3.4 + DOWN * 0.2)
        join_arrow = Arrow(dog_nums.get_right(), joined.get_left(), buff=0.35, color=MUTED, stroke_width=5)
        side = pill("positions side by side", FWD, size=SMALL).next_to(join_arrow, UP, buff=0.12)
        self.validator.check_in_frame(VGroup(tag_q1, dog, dog_nums, joined))

        n = self.narrate(
            id="answer_01",
            text="For the first question, the code writes the positions side by side. D is four, O is fifteen, and "
                 "G is seven. So DOG becomes four-one-five-seven.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(tag_q1), FadeIn(dog))
        for k, spoken in enumerate(["four", "fifteen", "seven"]):
            self.at_word(n, spoken)
            self.play(FadeIn(dog_nums[k], shift=DOWN * 0.15), run_time=0.4)
        self.at_word(n, "becomes")
        self.play(GrowArrow(join_arrow), FadeIn(side), FadeIn(joined, shift=LEFT * 0.2))
        self.wait_for_narration(n)

        # Q2: rule tester with ACE, BAD, CAB.
        tag_q2 = pill("Q2", FOCUS).move_to(tag_q1)
        table = RuleTable(["Word", "Given code", "Forward sum", "Reverse sum (81 − sum)"], [-4.8, -2.2, 0.6, 4.0],
                          2.2, colors=[MUTED, ANCHOR, FWD, REV])
        words, codes = ["ACE", "BAD", "CAB"], ["72", "74", "?"]
        word_cells = VGroup(*[table.cell(r, 0, w) for r, w in enumerate(words)])
        code_cells = VGroup(*[table.cell(r, 1, c, FOCUS if c == "?" else ANCHOR) for r, c in enumerate(codes)])
        sums = [table.cell(r, 2, str(fsum(w)), FWD) for r, w in enumerate(words)]
        revs = [table.cell(r, 3, str(rsum(w)), REV) for r, w in enumerate(words)]
        self.validator.check_in_frame(VGroup(tag_q2, table.head(), word_cells, revs[2]))

        n = self.narrate(
            id="answer_02",
            text="For the second, ACE has a forward sum of one plus three plus five, which is nine. That's clearly not "
                 "seventy-two. Try the reverse sum: eighty-one minus nine is seventy-two, which matches. Check BAD: "
                 "its forward sum is seven, and eighty-one minus seven is seventy-four. That matches too.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(VGroup(tag_q1, dog, dog_nums, joined, join_arrow, side)), FadeIn(tag_q2))
        self.play(FadeIn(table.head()), FadeIn(word_cells), FadeIn(code_cells))
        self.at_word(n, "nine")
        self.play(FadeIn(sums[0]))
        self.at_word(n, "not")
        m0 = table.tick(sums[0], False)
        self.play(FadeIn(m0))
        self.at_word(n, "matches", occurrence=1)
        m1 = table.tick(revs[0], True)
        self.play(FadeIn(revs[0]), FadeIn(m1))
        self.at_word(n, "BAD")
        self.play(Indicate(word_cells[1], color=FOCUS))
        self.at_word(n, "seven")
        self.play(FadeIn(sums[1]))
        self.at_word(n, "too")
        m2 = table.tick(revs[1], True)
        self.play(FadeIn(revs[1]), FadeIn(m2))
        self.wait_for_narration(n)

        # HEAR: CAB: sum 6 -> 81 - 6 = 75.  SEE: CAB's row; 75 into the code column.
        n = self.narrate(
            id="answer_03",
            text="So the rule is the reverse sum. CAB has a forward sum of three plus one plus two, which is six. "
                 "The answer is eighty-one minus six, which is seventy-five.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "rule")
        frame = SurroundingRectangle(VGroup(table.header[3], m2), color=GOOD, buff=0.15)
        self.play(Create(frame))
        self.at_word(n, "six")
        self.play(FadeIn(sums[2]))
        self.at_word(n, "answer")
        self.play(FadeIn(revs[2]))
        answer = table.cell(2, 1, "75", GOOD)
        self.play(ReplacementTransform(code_cells[2], answer), Flash(answer, color=GOOD))
        self.validator.check_in_frame(VGroup(frame, answer))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S12_answer")

    # ========================================== 13. QUICK REVISION ==========

    def quick_revision(self):
        self.scene_start("S13_revision", title="Quick Revision")

        card_w, card_h = SAFE_W - 1.0, 4.8
        items = [
            ("One number per letter → forward or reverse positions (± a constant)", FWD),
            ("Concatenated codes → split into valid positions (1–26)", ANCHOR),
            ("One number per word → sum of positions, forward or reverse", REV),
            ("Reverse sum = 27 × letters − forward sum", FOCUS),
            ("Test candidate rules in order; the rule must fit every example", GOOD),
        ]
        bullets = VGroup(*[VGroup(Dot(radius=0.07, color=c), fitted_text(s, card_w - 1.4, BODY, c, max_lines=2))
                           .arrange(RIGHT, buff=0.3) for s, c in items]).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        board = self.card(bullets, width=card_w, height=card_h).move_to(DOWN * 0.1)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="revision_01",
            text="To revise: in number coding, letters become positions, forward or reverse, sometimes adjusted by a "
                 "constant. When positions run together, split them into valid numbers from one to twenty-six.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(board[0]))
        self.play(FadeIn(bullets[0], shift=RIGHT * 0.2))
        self.at_word(n, "together")
        self.play(FadeIn(bullets[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="revision_02",
            text="When a whole word becomes one number, it's usually a sum of positions, possibly with a simple "
                 "operation on top. The reverse sum is twenty-seven times the number of letters, minus the forward sum.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(bullets[2], shift=RIGHT * 0.2))
        self.at_word(n, "reverse")
        self.play(FadeIn(bullets[3], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="revision_03",
            text="And whenever two examples are given, your rule must fit both.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(bullets[4], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S13_revision")

    # ================================================= 14. CLOSING ==========
    # Purpose: teaser for Pattern Identification: the two tools merge into one
    # process.

    def closing(self):
        self.scene_start("S14_closing", title="Closing")

        shift_tool = pill("shift row  ·  letter codes", ANCHOR, size=LABEL).move_to(LEFT * 3.4 + UP * 1.3)
        rule_tool = pill("rule tester  ·  number codes", FWD, size=LABEL).move_to(RIGHT * 3.4 + UP * 1.3)
        merged = pill("Next:  Pattern Identification", GOOD, size=BODY).move_to(DOWN * 1.2)
        a1 = Arrow(shift_tool.get_bottom(), merged.get_top() + LEFT * 1.0, buff=0.2, color=ANCHOR, stroke_width=5)
        a2 = Arrow(rule_tool.get_bottom(), merged.get_top() + RIGHT * 1.0, buff=0.2, color=FWD, stroke_width=5)
        self.validator.check_in_frame(VGroup(shift_tool, rule_tool, merged))

        n = self.narrate(
            id="closing_01",
            text="We now have two tools, the shift row for letter codes and the rule tester for number codes. In the "
                 "next topic, we'll combine them into a single, disciplined process for identifying any coding "
                 "pattern. We'll also practise it on codes that mix more than one idea.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "shift")
        self.play(FadeIn(shift_tool, shift=DOWN * 0.2))
        self.at_word(n, "tester")
        self.play(FadeIn(rule_tool, shift=DOWN * 0.2))
        self.at_word(n, "combine")
        self.play(GrowArrow(a1), GrowArrow(a2))
        self.play(FadeIn(merged, scale=1.1))
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S14_closing")

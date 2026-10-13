"""
animation.py for the LMS video generator.

Course : Pre-C-CAT - Section A
Module : Module 1 - Logical Reasoning
Lesson : Lesson 6 - Series Completion: Number Series
Topic  : Difference Series (Topic 1)

Source script:
  C:\\Scripts\\Section A\\Module 1 - Logical Reasoning\\Lesson 06 - Number Series\\
  Topic 1 - Difference Series.md

Built on the golden-reference pattern:
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``.

Opening: first video of a NEW LESSON (not of the course), so no spoken course
welcome. The module > lesson > topic trail is shown on screen (silent), then a
one-line recap of Lesson 5, one line saying Lesson 6 starts, the topic title
and the objectives.

Core visual: a series as a row of tiles; the difference row sits between the
terms (at the gaps), the second-difference row under the differences. All
differences are computed from the series.

Section map (script heading -> VISUAL PLAN scene):
  S00 Intro (trail + recap)   -> -
  S01 Opening Hook            -> scene 1
  S02 Concept                 -> scene 2
  S03 The difference row      -> scene 3
  S04 Three patterns          -> scene 4
  S05-S07 Examples 1-3        -> scene 5
  S08 Exam Application        -> scene 6
  S09 Common Mistake          -> scene 7
  S10-S11 Practice / Answer   -> scene 8
  S12-S13 Revision / Closing  -> scene 9
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


# ==================================================== series helpers ====

def column_xs(n, spacing, centre=ORIGIN):
    """x positions of ``n`` evenly spaced columns centred on ``centre``."""
    return [centre[0] + (k - (n - 1) / 2) * spacing for k in range(n)]


def tile(label, side=0.85, color=TERM, stroke=MUTED):
    sq = RoundedRectangle(corner_radius=0.12, width=side * 1.25, height=side, stroke_color=stroke,
                          stroke_width=2, fill_color=CELL, fill_opacity=1)
    return VGroup(sq, text(label, int(side * 44), color, BOLD).move_to(sq))


def diffs(values):
    return [b - a for a, b in zip(values, values[1:])]


def signed(d):
    return f"+{d}" if d >= 0 else f"−{-d}"


class Series:
    """A series as tiles, with rows underneath:
       row 1 = differences, at the gaps between terms;
       row 2 = second differences, under the gaps between differences.
    ``values`` may contain None for a blank ("?")."""

    def __init__(self, values, y=1.0, spacing=1.55, side=0.85, centre=ORIGIN):
        self.values = list(values)
        self.xs = column_xs(len(values), spacing, centre)
        self.y, self.side = y, side
        self.tiles = VGroup(*[tile("?" if v is None else str(v), side, FOCUS if v is None else TERM)
                              .move_to(RIGHT * x + UP * y) for v, x in zip(values, self.xs)])

    def gap_x(self, k):
        """x of the gap between term k and term k + 1."""
        return (self.xs[k] + self.xs[k + 1]) / 2

    def diff_pill(self, k, label, color=DIFF):
        return pill(label, color, size=SMALL).move_to(RIGHT * self.gap_x(k) + UP * (self.y - 0.95))

    def diff_row(self, values, start=0, color=DIFF):
        return VGroup(*[self.diff_pill(start + k, signed(d), color) for k, d in enumerate(values)])

    def second_pill(self, k, label, color=SECOND):
        """Under the gap between difference k and difference k + 1 (= under term k + 1)."""
        return pill(label, color, size=SMALL).move_to(RIGHT * self.xs[k + 1] + UP * (self.y - 1.8))

    def second_row(self, values, color=SECOND):
        return VGroup(*[self.second_pill(k, signed(d), color) for k, d in enumerate(values)])

    def value_tile(self, k, value, color=GOOD):
        return tile(str(value), self.side, color, stroke=color).move_to(self.tiles[k])


# ============================================================= lesson ====

class DifferenceSeriesVideo(LMSScene):
    lesson_title = "Difference Series"

    def construct(self):
        self.camera.background_color = BG

        self.lesson_intro()
        self.hook()
        self.concept()
        self.difference_row()
        self.three_patterns()
        self.example_constant()
        self.example_ap()
        self.example_missing()
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

    def fill_answer(self, series, k, value):
        """Animation: the '?' tile k becomes the answer (green)."""
        new = series.value_tile(k, value)
        return new, ReplacementTransform(series.tiles[k], new)

    # ========================================= 0. LESSON INTRO ==========
    # Purpose: where we are (silent trail, now Lesson 6), a one-line recap of
    # Lesson 5, the new lesson, today's topic.

    def lesson_intro(self):
        self.scene_start("S00_intro", title="Lesson Introduction")

        crumb = self.breadcrumb("Module 1 · Logical Reasoning", "Lesson 6 · Number Series", "Topic 1")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        last = pill("Last lesson: Symbols & Notations", MUTED, size=SMALL)
        skills = VGroup(pill("decode symbols", SECOND, size=LABEL), pill("build chains", DIFF, size=LABEL),
                        pill("judge conclusions", GOOD, size=LABEL)).arrange(RIGHT, buff=0.4)
        fit_width(skills, SAFE_W)
        recap = VGroup(last, skills).arrange(DOWN, buff=0.5).move_to(UP * 0.2)
        self.validator.check_in_frame(VGroup(crumb, recap))

        # SEE (silent): the trail.  HEAR: Lesson 5 in one sentence.
        n = self.narrate(
            id="intro_01",
            text="In the last lesson, you decoded symbols as relations, combined them into chains, and judged conclusions.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.play(FadeIn(last))
        for tag, spoken in zip(skills, ["decoded", "chains", "judged"]):
            self.at_word(n, spoken)
            self.play(FadeIn(tag, shift=UP * 0.2), run_time=0.4)
        self.wait_for_narration(n)

        # HEAR: Lesson 6 starts; today's topic.  SEE: lesson tag pulses; title.
        title = fitted_text("Difference Series", SAFE_W, 72, INK, BOLD)
        underline = Line(LEFT, RIGHT, color=DIFF, stroke_width=5).set_width(title.width * 0.6)
        VGroup(title, underline).arrange(DOWN, buff=0.2).move_to(UP * 0.2)
        n = self.narrate(
            id="intro_02",
            text="Now we start Lesson Six, Number Series, where you'll discover the hidden rule that builds a sequence. "
                 "Our first topic is the difference series.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Lesson")
        self.play(Indicate(crumb[2], color="#F48FB1", scale_factor=1.1))
        self.at_word(n, "hidden")
        self.play(FadeOut(recap, shift=UP * 0.3))
        self.at_word(n, "first")
        self.play(Write(title), run_time=1.1)
        self.play(GrowFromCenter(underline))
        self.wait_for_narration(n)

        # HEAR: the three objectives.  SEE: one row per objective, on its word.
        goals = [
            ("Build a difference row (and a second one)", DIFF),
            ("Recognise the three difference patterns", SECOND),
            ("Find a missing term and check both sides", GOOD),
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
            text="By the end of this video, you'll be able to build a difference row, recognise the three common "
                 "difference patterns, and find a missing term, checking it on both sides.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(underline), ReplacementTransform(title, small_title), run_time=0.8)
        self.play(FadeIn(objectives[0]), FadeIn(heading))
        for row, spoken in zip(rows, ["build", "recognise", "missing"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.5)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_intro")

    # ================================================= 1. HOOK ==========

    def hook(self):
        self.scene_start("S01_hook", title="Opening Hook")

        s = Series([3, 5, 9, 15, 23, None], y=1.0)
        not_fixed = pill("not  + a fixed amount", BAD, size=SMALL)
        not_double = pill("not  × 2", BAD, size=SMALL)
        VGroup(not_fixed, not_double).arrange(RIGHT, buff=0.6).move_to(DOWN * 0.7)
        gaps = VGroup(*[text("?", LABEL, DIFF, BOLD).move_to(RIGHT * s.gap_x(k) + UP * 0.05) for k in range(4)])
        self.validator.check_in_frame(VGroup(s.tiles, not_fixed, not_double))

        n = self.narrate(
            id="hook_01",
            text="What comes next: three, five, nine, fifteen, twenty-three?",
            voice="default",
            subtitle=True,
        )
        self.play_with(n, LaggedStart(*[FadeIn(t, shift=UP * 0.2) for t in s.tiles], lag_ratio=0.3), fraction=0.9)
        self.wait_for_narration(n)

        # HEAR: not fixed, not doubling; look between the numbers.  SEE: the two
        # ruled-out ideas; "?" marks appear in the gaps.
        n = self.narrate(
            id="hook_02",
            text="The numbers don't grow by a fixed amount, and they don't double. Yet there's a clear rule hiding in "
                 "plain sight. You just need to look between the numbers rather than at them.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "fixed")
        self.play(FadeIn(not_fixed, shift=UP * 0.1))
        self.at_word(n, "double")
        self.play(FadeIn(not_double, shift=UP * 0.1))
        self.at_word(n, "between")
        self.play(LaggedStart(*[FadeIn(g, scale=1.4) for g in gaps], lag_ratio=0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S01_hook")

    # ============================================== 2. CONCEPT ==========

    def concept(self):
        self.scene_start("S02_concept", title="Concept Introduction")

        values = [7, 12, 17, 22]
        s = Series(values + [None], y=0.9)
        gaps = VGroup(*[text("?", LABEL, DIFF, BOLD).move_to(s.diff_pill(k, "+0")) for k in range(3)])
        row = s.diff_row(diffs(values))
        self.validator.check_in_frame(VGroup(s.tiles, row))

        n = self.narrate(
            id="concept_01",
            text="A number series is a sequence of numbers generated by a rule. Your job is to find the rule and extend "
                 "it, or to fill a gap.",
            voice="default",
            subtitle=True,
        )
        self.play(LaggedStart(*[FadeIn(t, shift=UP * 0.2) for t in s.tiles], lag_ratio=0.2))
        self.at_word(n, "extend")
        self.play(Indicate(s.tiles[-1], color=FOCUS, scale_factor=1.15))
        self.wait_for_narration(n)

        # HEAR: rules built on differences.  SEE: the gaps fill with +5.
        n = self.narrate(
            id="concept_02",
            text="The most common rules are built on differences: how much each term changes from the one before. When "
                 "the terms themselves look irregular, the differences are often perfectly regular.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "differences", occurrence=1)
        self.play(FadeIn(gaps))
        self.at_word(n, "changes")
        self.play(*[ReplacementTransform(g, r) for g, r in zip(gaps, row)])
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_03",
            text="So the very first test for almost any series is to write the difference row.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "difference")
        cap = self.caption("First test for any series: the difference row", DIFF)
        self.play(FadeIn(cap, shift=UP * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_concept")

    # ======================================== 3. THE DIFFERENCE ROW ==========

    def difference_row(self):
        self.scene_start("S03_difference_row", title="Explanation - The Difference Row")

        values = [3, 5, 9, 15, 23]
        d1 = diffs(values)                     # 2, 4, 6, 8
        d2 = diffs(d1)                         # 2, 2, 2
        nxt_d = d1[-1] + d2[-1]                # 10
        s = Series(values + [None], y=1.6)
        row1 = s.diff_row(d1)
        row2 = s.second_row(d2)
        next_diff = s.diff_pill(4, signed(nxt_d), FOCUS)
        self.validator.check_in_frame(VGroup(s.tiles, row2))

        n = self.narrate(
            id="diff_01",
            text="Subtract each term from the next one. For three, five, nine, fifteen, twenty-three, the differences are "
                 "two, four, six and eight.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(s.tiles))
        for pill_, spoken in zip(row1, ["two", "four", "six", "eight"]):
            self.at_word(n, spoken)
            self.play(FadeIn(pill_, shift=DOWN * 0.15), run_time=0.4)
        self.wait_for_narration(n)

        # HEAR: they rise by 2; next difference 10; next term 33.
        n = self.narrate(
            id="diff_02",
            text="Now the pattern is obvious: the differences increase by two each time. The next difference is ten, so "
                 "the next term is twenty-three plus ten, which is thirty-three.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "increase")
        self.play(Indicate(row1, color=DIFF, scale_factor=1.1))
        self.at_word(n, "ten", occurrence=1)
        self.play(FadeIn(next_diff, scale=1.2))
        self.at_word(n, "which")
        answer, swap = self.fill_answer(s, 5, values[-1] + nxt_d)
        self.play(swap, Flash(answer, color=GOOD))
        self.wait_for_narration(n)

        # HEAR: second differences 2, 2, 2: the AP signature.
        n = self.narrate(
            id="diff_03",
            text="If the differences themselves aren't constant, take differences again. Here, the second differences "
                 "are two, two, two. That's constant. A constant second difference is the signature of a series whose "
                 "differences form an arithmetic progression.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "second", occurrence=1)
        self.play(LaggedStart(*[FadeIn(p, shift=DOWN * 0.15) for p in row2], lag_ratio=0.3))
        self.at_word(n, "signature")
        cap = self.caption("Constant second difference  →  differences in arithmetic progression", SECOND)
        self.play(FadeIn(cap, shift=UP * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_difference_row")

    # ========================================== 4. THREE PATTERNS ==========

    def three_patterns(self):
        self.scene_start("S04_patterns", title="Explanation - Three Difference Patterns")

        rows = VGroup(*[VGroup(pill(k, c, size=SMALL), fitted_text(s, SAFE_W - 3.4, BODY, INK))
                        .arrange(RIGHT, buff=0.35) for k, s, c in [
                            ("constant", "differences equal  (5, 5, 5 …)", DIFF),
                            ("AP", "differences rise by a fixed amount  (2, 4, 6 …)", SECOND),
                            ("GP", "differences multiply by a fixed ratio  (1, 2, 4, 8 …)", RATIO)]])
        rows.arrange(DOWN, buff=0.25, aligned_edge=LEFT)
        patterns = self.card(rows)
        patterns.move_to(UP * (CARD_TOP - patterns.height / 2))
        self.validator.check_in_frame(patterns)

        n = self.narrate(
            id="pat_01",
            text="Three difference patterns cover most exam series.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(patterns[0]))
        self.wait_for_narration(n)

        # HEAR: constant: 7, 12, 17, 22 -> 27.
        mini = VGroup(text("7, 12, 17, 22", LABEL, INK, BOLD), text("+5 each", SMALL, DIFF),
                      text("→  27", LABEL, GOOD, BOLD)).arrange(RIGHT, buff=0.35).move_to(DOWN * 0.3)
        n = self.narrate(
            id="pat_02",
            text="First, constant differences. Seven, twelve, seventeen, twenty-two goes up by five every time, so the "
                 "next term is twenty-seven.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "Seven")
        self.play(FadeIn(mini[0]))
        self.at_word(n, "five")
        self.play(FadeIn(mini[1]))
        self.at_word(n, "next")
        self.play(FadeIn(mini[2]))
        self.wait_for_narration(n)

        n = self.narrate(
            id="pat_03",
            text="Second, differences in arithmetic progression, like our opening example, where the differences rise by "
                 "a fixed amount.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(mini), FadeIn(rows[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        # HEAR: GP: 2, 3, 5, 9, 17: differences double; next 16 -> 33.
        values = [2, 3, 5, 9, 17]
        d1 = diffs(values)
        s = Series(values + [None], y=-0.3)
        row1 = s.diff_row(d1, color=RATIO)
        times = VGroup(*[text("×2", SMALL, RATIO, BOLD).move_to(RIGHT * s.xs[k + 1] + UP * (s.y - 1.55))
                         for k in range(3)])
        nxt = s.diff_pill(4, signed(d1[-1] * 2), FOCUS)
        self.validator.check_in_frame(VGroup(patterns, s.tiles, times))
        n = self.narrate(
            id="pat_04",
            text="Third, differences in geometric progression. In two, three, five, nine, seventeen, the differences are "
                 "one, two, four and eight. Each difference doubles. So the next difference is sixteen, and the next "
                 "term is thirty-three.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(rows[2], shift=RIGHT * 0.2))
        self.at_word(n, "two", occurrence=1)
        self.play(FadeIn(s.tiles))
        self.at_word(n, "one")
        self.play(LaggedStart(*[FadeIn(p, shift=DOWN * 0.15) for p in row1], lag_ratio=0.3))
        self.at_word(n, "doubles")
        self.play(LaggedStart(*[FadeIn(t, scale=1.3) for t in times], lag_ratio=0.3))
        self.at_word(n, "sixteen")
        self.play(FadeIn(nxt, scale=1.2))
        self.at_word(n, "next", occurrence=2)
        answer, swap = self.fill_answer(s, 5, values[-1] + d1[-1] * 2)
        self.play(swap)
        self.wait_for_narration(n)

        n = self.narrate(
            id="pat_05",
            text="If the second differences aren't constant, check whether the differences are multiplying by a fixed "
                 "ratio.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "multiplying")
        cap = self.caption("Second differences not constant?  Check whether the differences multiply", RATIO)
        self.play(FadeIn(cap, shift=UP * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_patterns")

    # ================================================ 5. EXAMPLE 1 ==========

    def example_constant(self):
        self.scene_start("S05_example_constant", title="Example 1 - Basic")

        values = [7, 12, 17, 22]
        s = Series(values + [None], y=0.9)
        row = s.diff_row(diffs(values))
        nxt = s.diff_pill(3, signed(diffs(values)[-1]), FOCUS)
        self.validator.check_in_frame(VGroup(s.tiles, row))

        n = self.narrate(
            id="ex1_01",
            text="Seven, twelve, seventeen, twenty-two. The differences are five, five, five. The next term is "
                 "twenty-seven.",
            voice="default",
            subtitle=True,
        )
        self.play(LaggedStart(*[FadeIn(t, shift=UP * 0.2) for t in s.tiles], lag_ratio=0.2))
        self.at_word(n, "differences")
        self.play(LaggedStart(*[FadeIn(p, shift=DOWN * 0.15) for p in row], lag_ratio=0.3))
        self.at_word(n, "next")
        answer, swap = self.fill_answer(s, 4, values[-1] + diffs(values)[-1])
        self.play(FadeIn(nxt), swap, Flash(answer, color=GOOD))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_example_constant")

    # ================================================ 6. EXAMPLE 2 ==========

    def example_ap(self):
        self.scene_start("S06_example_ap", title="Example 2 - Application")

        values = [4, 9, 18, 31, 48]
        d1 = diffs(values)                     # 5, 9, 13, 17
        d2 = diffs(d1)                         # 4, 4, 4
        s = Series(values + [None], y=1.3)
        row1 = s.diff_row(d1)
        row2 = s.second_row(d2)
        nxt = s.diff_pill(4, signed(d1[-1] + d2[-1]), FOCUS)
        self.validator.check_in_frame(VGroup(s.tiles, row2))

        n = self.narrate(
            id="ex2_01",
            text="Four, nine, eighteen, thirty-one, forty-eight. What's next?",
            voice="default",
            subtitle=True,
        )
        self.play(LaggedStart(*[FadeIn(t, shift=UP * 0.2) for t in s.tiles], lag_ratio=0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="ex2_02",
            text="The differences are five, nine, thirteen and seventeen. They rise by four each time. The next difference "
                 "is twenty-one, so the next term is forty-eight plus twenty-one, which is sixty-nine.",
            voice="default",
            subtitle=True,
        )
        for p, spoken in zip(row1, ["five", "nine", "thirteen", "seventeen"]):
            self.at_word(n, spoken)
            self.play(FadeIn(p, shift=DOWN * 0.15), run_time=0.4)
        self.at_word(n, "rise")
        self.play(LaggedStart(*[FadeIn(p, shift=DOWN * 0.15) for p in row2], lag_ratio=0.3))
        self.at_word(n, "difference", occurrence=1)
        self.play(FadeIn(nxt, scale=1.2))
        self.at_word(n, "which")
        answer, swap = self.fill_answer(s, 5, values[-1] + d1[-1] + d2[-1])
        self.play(swap, Flash(answer, color=GOOD))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_example_ap")

    # ================================ 7. EXAMPLE 3: MISSING MIDDLE TERM ==========

    def example_missing(self):
        self.scene_start("S07_example_missing", title="Example 3 - A Missing Middle Term")

        values = [11, 14, 20, 29, None, 56]
        known = diffs([11, 14, 20, 29])        # 3, 6, 9
        step = known[1] - known[0]             # 3
        next1, next2 = known[-1] + step, known[-1] + 2 * step     # 12, 15
        missing = 29 + next1                   # 41
        s = Series(values, y=1.1)
        row = s.diff_row(known)
        guess1 = s.diff_pill(3, signed(next1) + "?", FOCUS)
        guess2 = s.diff_pill(4, signed(next2) + "?", FOCUS)
        check = pill(f"{missing} + {next2} = {missing + next2}  ✓  matches 56", GOOD, size=LABEL).move_to(DOWN * 1.4)
        self.validator.check_in_frame(VGroup(s.tiles, row, check))

        n = self.narrate(
            id="ex3_01",
            text="Eleven, fourteen, twenty, twenty-nine, blank, fifty-six. Find the missing term.",
            voice="default",
            subtitle=True,
        )
        self.play(LaggedStart(*[FadeIn(t, shift=UP * 0.2) for t in s.tiles], lag_ratio=0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="ex3_02",
            text="The known differences are three, six and nine. They're rising by three, so the next two should be "
                 "twelve and fifteen.",
            voice="default",
            subtitle=True,
        )
        for p, spoken in zip(row, ["three", "six", "nine"]):
            self.at_word(n, spoken)
            self.play(FadeIn(p, shift=DOWN * 0.15), run_time=0.4)
        self.at_word(n, "twelve")
        self.play(FadeIn(guess1, scale=1.2))
        self.at_word(n, "fifteen")
        self.play(FadeIn(guess2, scale=1.2))
        self.wait_for_narration(n)

        # HEAR: 29 + 12 = 41; check 41 + 15 = 56.  SEE: 41 drops in; both gaps green.
        n = self.narrate(
            id="ex3_03",
            text="Twenty-nine plus twelve is forty-one. Now check the other side: forty-one plus fifteen is fifty-six, "
                 "which matches the given term.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "twelve")
        answer, swap = self.fill_answer(s, 4, missing)
        self.play(swap)
        self.at_word(n, "check")
        self.play(guess1[0].animate.set_stroke(GOOD), guess1[1].animate.set_color(GOOD))
        self.at_word(n, "matches")
        self.play(guess2[0].animate.set_stroke(GOOD), guess2[1].animate.set_color(GOOD), FadeIn(check, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="ex3_04",
            text="The answer is forty-one. The check against fifty-six isn't optional. A missing-term answer must fit on "
                 "both sides of the gap.",
            voice="default",
            subtitle=True,
        )
        self.play(Flash(answer, color=GOOD))
        self.at_word(n, "both")
        cap = self.caption("A missing term must fit on BOTH sides of the gap", GOOD)
        self.play(FadeIn(cap, shift=UP * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S07_example_missing")

    # ======================================== 8. EXAM APPLICATION ==========

    def exam_application(self):
        self.scene_start("S08_exam", title="Exam Application")

        steps = VGroup(*[VGroup(pill(str(i + 1), c, size=SMALL), fitted_text(s, SAFE_W - 2.2, BODY, INK))
                         .arrange(RIGHT, buff=0.3) for i, (s, c) in enumerate([
                             ("Write the difference row", DIFF),
                             ("Constant?  →  done", GOOD),
                             ("Not constant  →  second differences (AP?) or ratios of differences (GP?)", SECOND),
                             ("Missing term  →  confirm on both sides", FOCUS)])])
        steps.arrange(DOWN, buff=0.22, aligned_edge=LEFT)
        routine = self.card(steps).move_to(UP * 0.7)
        tip = pill("Very fast growth (each term several times the last)?  Test ratios", RATIO, size=SMALL)
        fit_width(tip, SAFE_W).move_to(DOWN * 2.1)
        self.validator.check_in_frame(VGroup(routine, tip))

        n = self.narrate(
            id="exam_01",
            text="In the exam, the difference row is your first move for any series that grows steadily. It takes a few "
                 "seconds, and it solves a large share of questions outright.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(routine[0]))
        self.play_with(n, LaggedStart(*[FadeIn(r, shift=RIGHT * 0.2) for r in steps], lag_ratio=0.4), fraction=0.8)
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_02",
            text="If the numbers grow very fast, with each term several times the last, differences may not be the right "
                 "tool. That's the signal to test ratios instead, which is the subject of the next topic.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "ratios")
        self.play(FadeIn(tip, scale=1.05))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S08_exam")

    # =========================================== 9. COMMON MISTAKE ==========

    def common_mistake(self):
        self.scene_start("S09_mistake", title="Common Mistake")

        card_w = ZONE_W - 0.3
        pairs = [
            (self.verdict_card(False, "A slip in one subtraction hides the pattern", card_w),
             self.verdict_card(True, "Write the differences clearly; double-check", card_w)),
            (self.verdict_card(False, "Pattern fits the first three terms only", card_w),
             self.verdict_card(True, "Pattern fits every term", card_w)),
            (self.verdict_card(False, "Missing term checked on one side only", card_w),
             self.verdict_card(True, "Check both sides of the gap", card_w)),
        ]
        for (wrong, right), y in zip(pairs, [1.6, 0.05, -1.5]):
            wrong.move_to(LEFT_ZONE + UP * y)
            right.move_to(RIGHT_ZONE + UP * y)
        header = pill("3 mistakes", BAD, size=LABEL).move_to(UP * (CARD_TOP - 0.3))
        self.validator.check_in_frame(VGroup(header, *[c for p in pairs for c in p]))

        n = self.narrate(
            id="mistake_01",
            text="The first mistake is arithmetic in the difference row itself. One wrong subtraction hides the pattern "
                 "completely. Write the differences clearly and double-check them.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(header))
        self.at_word(n, "arithmetic")
        self.play(FadeIn(pairs[0][0], shift=RIGHT * 0.3))
        self.at_word(n, "Write")
        self.play(FadeIn(pairs[0][1], shift=LEFT * 0.3))
        self.wait_for_narration(n)

        n = self.narrate(
            id="mistake_02",
            text="The second is stopping at a pattern that fits only the first few terms. Every term in the series must "
                 "follow the rule.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "stopping")
        self.play(FadeIn(pairs[1][0], shift=RIGHT * 0.3))
        self.at_word(n, "Every")
        self.play(FadeIn(pairs[1][1], shift=LEFT * 0.3))
        self.wait_for_narration(n)

        n = self.narrate(
            id="mistake_03",
            text="The third, for missing terms, is checking only one side of the gap. A wrong value can match the left side "
                 "and still fail on the right.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "checking")
        self.play(FadeIn(pairs[2][0], shift=RIGHT * 0.3))
        self.at_word(n, "fail")
        self.play(FadeIn(pairs[2][1], shift=LEFT * 0.3))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S09_mistake")

    # ================================================ 10. PRACTICE ==========

    def practice(self):
        self.scene_start("S10_practice", title="Practice Question")

        q1 = VGroup(pill("Q1", FOCUS), text("2,  3,  5,  9,  17,  ?", TITLE, INK, BOLD)).arrange(RIGHT, buff=0.4)
        q2 = VGroup(pill("Q2", FOCUS), text("6,  11,  21,  36,  ?,  81", TITLE, INK, BOLD)).arrange(RIGHT, buff=0.4)
        qs = VGroup(q1, q2).arrange(DOWN, buff=0.7, aligned_edge=LEFT)
        board = self.card(qs, color=FOCUS).move_to(UP * 0.4)
        self.validator.check_in_frame(board)

        # SILENCE (pause_after): countdown ring while the learner thinks.
        n = self.narrate(
            id="practice_01",
            text="Try these. First: two, three, five, nine, seventeen, what's next? Second: six, eleven, twenty-one, "
                 "thirty-six, blank, eighty-one. What's the missing term?",
            voice="default",
            subtitle=True,
            pause_after=8.0,
        )
        self.play(FadeIn(board[0]))
        self.at_word(n, "First")
        self.play(FadeIn(q1, shift=UP * 0.2))
        self.at_word(n, "Second")
        self.play(FadeIn(q2, shift=UP * 0.2))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        self.clear_stage()
        self.scene_end("S10_practice")

    # ================================================== 11. ANSWER ==========

    def answer(self):
        self.scene_start("S11_answer", title="Answer and Explanation")

        # Q1: differences double -> 33.
        v1 = [2, 3, 5, 9, 17]
        d1 = diffs(v1)
        s1 = Series(v1 + [None], y=2.2, spacing=1.35, side=0.75)
        row1 = s1.diff_row(d1)
        nxt1 = s1.diff_pill(4, signed(d1[-1] * 2), FOCUS)
        tag1 = pill("Q1", FOCUS).next_to(s1.tiles, LEFT, buff=0.4)

        # Q2: differences +5 each: 5, 10, 15, (20), (25) -> 56.
        v2 = [6, 11, 21, 36, None, 81]
        k2 = diffs([6, 11, 21, 36])            # 5, 10, 15
        step = k2[1] - k2[0]
        g1, g2 = k2[-1] + step, k2[-1] + 2 * step        # 20, 25
        s2 = Series(v2, y=-0.7, spacing=1.35, side=0.75)
        row2 = s2.diff_row(k2)
        p1 = s2.diff_pill(3, signed(g1), FOCUS)
        p2 = s2.diff_pill(4, signed(g2), FOCUS)
        tag2 = pill("Q2", FOCUS).next_to(s2.tiles, LEFT, buff=0.4)
        self.validator.check_in_frame(VGroup(tag1, s1.tiles, row1, tag2, s2.tiles, row2))

        n = self.narrate(
            id="answer_01",
            text="For the first, the differences are one, two, four, eight. They're doubling, so the next difference is "
                 "sixteen, and the next term is thirty-three.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(tag1), FadeIn(s1.tiles))
        self.at_word(n, "one")
        self.play(LaggedStart(*[FadeIn(p, shift=DOWN * 0.15) for p in row1], lag_ratio=0.3))
        self.at_word(n, "sixteen")
        self.play(FadeIn(nxt1, scale=1.2))
        self.at_word(n, "next", occurrence=2)
        a1, swap1 = self.fill_answer(s1, 5, v1[-1] + d1[-1] * 2)
        self.play(swap1, Flash(a1, color=GOOD))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answer_02",
            text="For the second, the differences are five, ten and fifteen, rising by five. The next two differences are "
                 "twenty and twenty-five. Thirty-six plus twenty is fifty-six, and fifty-six plus twenty-five is "
                 "eighty-one, which matches.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(tag2), FadeIn(s2.tiles))
        self.at_word(n, "five", occurrence=1)
        self.play(LaggedStart(*[FadeIn(p, shift=DOWN * 0.15) for p in row2], lag_ratio=0.3))
        self.at_word(n, "twenty", occurrence=1)
        self.play(FadeIn(p1, scale=1.2), FadeIn(p2, scale=1.2))
        self.at_word(n, "plus", occurrence=1)
        a2, swap2 = self.fill_answer(s2, 4, 36 + g1)
        self.play(swap2)
        self.at_word(n, "matches")
        self.play(*[p[0].animate.set_stroke(GOOD) for p in (p1, p2)], *[p[1].animate.set_color(GOOD) for p in (p1, p2)])
        self.wait_for_narration(n)

        n = self.narrate(
            id="answer_03",
            text="The missing term is fifty-six.",
            voice="default",
            subtitle=True,
        )
        self.play(Flash(a2, color=GOOD))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S11_answer")

    # ========================================== 12. QUICK REVISION ==========

    def quick_revision(self):
        self.scene_start("S12_revision", title="Quick Revision")

        card_w, card_h = SAFE_W - 1.0, 5.0
        items = [
            ("First move: the difference row", DIFF),
            ("Constant  →  constant-difference series", DIFF),
            ("Differences rising by a fixed amount  →  second differences constant", SECOND),
            ("Differences multiplying  →  differences in GP", RATIO),
            ("Missing term  →  check both sides", GOOD),
            ("Very fast growth  →  test ratios", FOCUS),
        ]
        bullets = VGroup(*[VGroup(Dot(radius=0.07, color=c), fitted_text(s, card_w - 1.4, BODY, c, max_lines=2))
                           .arrange(RIGHT, buff=0.3) for s, c in items]).arrange(DOWN, buff=0.25, aligned_edge=LEFT)
        board = self.card(bullets, width=card_w, height=card_h).move_to(DOWN * 0.1)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="revision_01",
            text="To revise: start with the difference row. Constant differences give a simple series. If the differences "
                 "rise steadily, the second differences will be constant. If the differences multiply, they form a "
                 "geometric progression. Always check missing terms on both sides. And when numbers grow very quickly, "
                 "test ratios instead.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(board[0]))
        self.play(FadeIn(bullets[0], shift=RIGHT * 0.2))
        for b, spoken in zip(bullets[1:], ["Constant", "rise", "multiply", "missing", "quickly"]):
            self.at_word(n, spoken)
            self.play(FadeIn(b, shift=RIGHT * 0.2), run_time=0.5)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S12_revision")

    # ================================================= 13. CLOSING ==========
    # Purpose: teaser for Ratio Series: ×2 arrows between terms.

    def closing(self):
        self.scene_start("S13_closing", title="Closing")

        values = [3, 6, 12, 24]
        s = Series(values + [None], y=0.8)
        ratios = VGroup(*[pill("×2", RATIO, size=SMALL).move_to(RIGHT * s.gap_x(k) + UP * (s.y + 0.85))
                          for k in range(3)])
        nxt = pill("Next:  Ratio Series", RATIO, size=BODY).move_to(DOWN * 1.4)
        self.validator.check_in_frame(VGroup(ratios, s.tiles, nxt))

        n = self.narrate(
            id="closing_01",
            text="Next, we'll look at series where each term is a multiple of the one before, sometimes with a small "
                 "addition. That's where the ratio test takes over from differences.",
            voice="default",
            subtitle=True,
        )
        self.play(LaggedStart(*[FadeIn(t, shift=UP * 0.2) for t in s.tiles], lag_ratio=0.2))
        self.at_word(n, "multiple")
        self.play(LaggedStart(*[FadeIn(r, shift=DOWN * 0.15) for r in ratios], lag_ratio=0.3))
        self.at_word(n, "ratio")
        self.play(FadeIn(nxt, scale=1.1))
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S13_closing")

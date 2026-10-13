"""
animation.py for the LMS video generator.

Course : C-CAT - Section A - English
Module : Module 1 - Vocabulary
Lesson : Lesson 1 - Synonyms
Video  : 02 - Types of Synonyms (Video 2 of 6)

Source script:
  C:\\Users\\User\\Downloads\\C-CAT_SectionA_Module1_English\\English\\Module 1 - Vocabulary\\
  Lesson 1 - Synonyms\\02 - Types of Synonyms.pdf

Built on the golden-reference pattern:
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``.

Opening: a later video of Lesson 1, so no spoken welcome. The module > lesson >
video trail is shown on screen (silent), then a one-line recap of Video 1
(reusing its overlapping candid / frank circles), the line about today's
topic, the title and the objectives.

Core visuals: the four dimensions as scales (degree, connotation, register)
plus collocation pairs; an audio mixer per word (the knob positions are data,
and the synonym / distractor gap is asserted); ``OptionQuestion`` cards with
struck-through traps and the key boxed in green.

Section map (script heading -> scene):
  S00 Intro (trail + recap)          S09 The Process
  S01 Hook                           S10 Hook, Solved
  S02 The Concept                    S11 Exam Patterns and Solving Models
  S03 Why You Need It                S12 Common Mistakes
  S04 The Analogy                    S13 Practice Questions
  S05-S07 Worked Examples 1-3        S14 Answers
  S08 Rules                          S15 Recap Card / S16 Next
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

DIMS = [("Degree", RATIO), ("Connotation", "#F48FB1"), ("Register", SECOND), ("Collocation", FOCUS)]
DIM_COL = dict(DIMS)


def scale_row(words, colors, label, label_color, width=10.0):
    """A labelled scale: words spaced evenly along an arrow, left to right."""
    arrow = Arrow(LEFT * width / 2, RIGHT * width / 2, buff=0, color=MUTED, stroke_width=3,
                  max_tip_length_to_length_ratio=0.03)
    xs = [(-width / 2 + 0.9) + i * (width - 1.8) / max(1, len(words) - 1) for i in range(len(words))]
    chips = VGroup(*[pill(w, c, size=LABEL).move_to(RIGHT * x + UP * 0.45) for w, c, x in zip(words, colors, xs)])
    tag = pill(label, label_color, size=SMALL).next_to(arrow, LEFT, buff=0.3)
    return VGroup(tag, arrow, chips)


def slider(label, value, color, height=2.6):
    """One mixer channel: a vertical track, a knob at ``value`` (0 = bottom, 1 = top), a label."""
    track = Line(DOWN * height / 2, UP * height / 2, color=MUTED, stroke_width=6)
    knob = RoundedRectangle(corner_radius=0.06, width=0.7, height=0.26, color=color, fill_color=color,
                            fill_opacity=0.9).move_to(UP * (value - 0.5) * height)
    name = text(label, SMALL, INK).next_to(track, DOWN, buff=0.25)
    return VGroup(track, knob, name)


class TypesOfSynonymsVideo(LMSScene):
    lesson_title = "Types of Synonyms"

    def construct(self):
        self.camera.background_color = BG

        self.lesson_intro()
        self.hook()
        self.concept()
        self.why_you_need_it()
        self.analogy()
        self.example_frugal()
        self.example_furious()
        self.example_commence()
        self.rules()
        self.process()
        self.hook_solved()
        self.exam_patterns()
        self.common_mistakes()
        self.practice()
        self.answers()
        self.recap()
        self.next_video()

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

    def show_question(self, q, pos_, n, row_words):
        """Word, then each option on its spoken word (clear of the pinned panel)."""
        q.group.move_to(pos_)
        if getattr(self, "pinned", None) is not None:
            self.no_overlap(q.group, self.pinned)
        self.play(FadeIn(q.word, scale=1.1))
        for row, spoken in zip(q.rows, row_words):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.35)

    # ========================================= 0. LESSON INTRO ==========
    # Purpose: silent trail, a one-line recap of Video 1 (reusing its
    # overlapping meaning circles), today's topic, the objectives.

    def lesson_intro(self):
        self.scene_start("S00_intro", title="Lesson Introduction")

        crumb = self.breadcrumb("English · Module 1 Vocabulary", "Lesson 1 · Synonyms", "Video 2")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        circles = meaning_circles(["candid", "frank"], [LEFT * 0.5 + UP * 0.2, RIGHT * 0.3 + UP * 0.2], [1.3, 1.3],
                                  [WORD, GOOD])
        circles[0][1].shift(LEFT * 0.5 + UP * 0.55)
        circles[1][1].shift(RIGHT * 0.5 + DOWN * 0.55)
        gap = pill("overlap, but rarely an exact match", FOCUS, size=SMALL).move_to(DOWN * 1.8)
        self.validator.check_in_frame(VGroup(crumb, circles, gap))

        # SEE (silent): the trail.  HEAR: Video 1 in one idea.
        n = self.narrate(
            id="intro_01",
            text="In video one, you saw that synonyms overlap, but rarely match exactly.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.at_word(n, "overlap")
        self.play(Create(circles[0][0]), FadeIn(circles[0][1]), Create(circles[1][0]), FadeIn(circles[1][1]))
        self.at_word(n, "rarely")
        self.play(FadeIn(gap, shift=UP * 0.1))
        self.wait_for_narration(n)

        title = fitted_text("Types of Synonyms", SAFE_W, 72, INK, BOLD)
        underline = Line(LEFT, RIGHT, color=WORD, stroke_width=5).set_width(title.width * 0.6)
        VGroup(title, underline).arrange(DOWN, buff=0.2).move_to(UP * 0.2)
        n = self.narrate(
            id="intro_02",
            text="Today we name the kinds of mismatch, because exam options are built from them. These are the types of "
                 "synonyms.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "mismatch")
        self.play(FadeOut(VGroup(circles, gap), shift=UP * 0.3))
        self.at_word(n, "types")
        self.play(Write(title), run_time=1.1)
        self.play(GrowFromCenter(underline))
        self.wait_for_narration(n)

        goals = [
            ("Recognise the four ways near-synonyms differ", RATIO),
            ("Use those differences to choose between two close options", GOOD),
        ]
        rows = VGroup(*[VGroup(pill(str(i + 1), c, size=SMALL), fitted_text(s_, SAFE_W - 2.4, BODY, INK))
                        .arrange(RIGHT, buff=0.35) for i, (s_, c) in enumerate(goals)])
        rows.arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        heading = text("By the end of this video, you will:", LABEL, MUTED, BOLD)
        objectives = self.card(VGroup(heading, rows).arrange(DOWN, buff=0.4, aligned_edge=LEFT))
        small_title = title.copy().scale(0.6)
        small_title.next_to(crumb, DOWN, buff=0.3)
        objectives.next_to(small_title, DOWN, buff=0.35)
        self.validator.check_in_frame(VGroup(crumb, small_title, objectives))
        n = self.narrate(
            id="intro_03",
            text="By the end of this video, you'll recognise the four ways near-synonyms differ: degree, connotation, "
                 "register and collocation. And you'll use those differences to choose between two close options.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(underline), ReplacementTransform(title, small_title), run_time=0.8)
        self.play(FadeIn(objectives[0]), FadeIn(heading))
        for row_, spoken in zip(rows, ["recognise", "choose"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row_, shift=RIGHT * 0.2), run_time=0.5)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_intro")

    # ================================================= 1. HOOK ==========

    HOOK = dict(word="frugal", options=["stingy", "poor", "economical", "greedy"], key="c",
                traps={"a": "same core, NEGATIVE feeling", "b": "lacking money", "d": "wanting more"})

    def review_card(self):
        head = text("Performance review", SMALL, MUTED, BOLD)
        line = text("“Priya is very ______ with the project budget.”", BODY, INK)
        note = text("goal: praise her", SMALL, GOOD)
        return self.card(VGroup(head, fit_width(line, SAFE_W - 2.0), note).arrange(DOWN, buff=0.25, aligned_edge=LEFT))

    def hook(self):
        self.scene_start("S01_hook", title="Hook")

        form = self.review_card()
        form.move_to(UP * (CARD_TOP - form.height / 2))
        h = self.HOOK
        q = OptionQuestion(h["word"], h["options"], h["key"], h["traps"])
        opts = q.rows.copy().arrange(RIGHT, buff=0.8).move_to(DOWN * 0.9)
        word = pill("frugal", WORD, size=BODY).move_to(UP * 0.2)
        two = pill("two options mean “careful with money”; only one is a compliment", FOCUS, size=SMALL)
        fit_width(two, SAFE_W).move_to(DOWN * 2.3)
        self.validator.check_in_frame(VGroup(form, word, opts, two))

        n = self.narrate(
            id="hook_01",
            text="You're drafting a performance review, and you want to praise a colleague who never wastes money. The "
                 "word you have in mind is frugal. Which word is closest in meaning, and keeps it a compliment?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "review")
        self.play(FadeIn(form, shift=DOWN * 0.2))
        self.at_word(n, "frugal")
        self.play(FadeIn(word, scale=1.1))
        self.at_word(n, "compliment")
        self.play(Indicate(form[1][2], color=GOOD, scale_factor=1.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_02",
            text="Stingy, poor, economical, or greedy? Two options mean careful with money. Only one works in a review "
                 "she'll be happy to read.",
            voice="default",
            subtitle=True,
            pause_after=3.0,
        )
        for row, spoken in zip(opts, ["Stingy", "poor", "economical", "greedy"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=UP * 0.15), run_time=0.35)
        self.at_word(n, "Two")
        self.play(FadeIn(two, shift=UP * 0.1))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        self.clear_stage()
        self.scene_end("S01_hook")

    # ============================================== 2. CONCEPT ==========

    def concept(self):
        self.scene_start("S02_concept", title="The Concept")

        head = pill("near-synonyms: same core, different on ONE of four dimensions", WORD, size=LABEL)
        fit_width(head, SAFE_W)
        head.move_to(UP * (CARD_TOP - head.height / 2))
        degree = scale_row(["warm", "hot", "scorching"], [INK, INK, INK], "Degree", RATIO)
        feeling = scale_row(["thrifty  +", "economical  0", "stingy  −"], [GOOD, INK, BAD], "Connotation", "#F48FB1")
        register = scale_row(["kick off", "start", "commence"], [INK, INK, INK], "Register", SECOND)
        rows = VGroup(degree, feeling, register).arrange(DOWN, buff=0.45)
        fit_within(rows, SAFE_W, 3.6)
        rows.next_to(head, DOWN, buff=0.4)
        colloc = VGroup(pill("Collocation", FOCUS, size=SMALL),
                        pill("heavy rain  ✓", GOOD, size=LABEL), pill("strong rain  ✗", BAD, size=LABEL),
                        pill("make a decision  ✓", GOOD, size=LABEL), pill("do a decision  ✗", BAD, size=LABEL))\
            .arrange(RIGHT, buff=0.3)
        fit_width(colloc, SAFE_W)
        colloc.next_to(rows, DOWN, buff=0.4)
        self.no_overlap(head, rows, colloc)
        self.validator.check_in_frame(VGroup(head, rows, colloc))

        n = self.narrate(
            id="concept_01",
            text="Near-synonyms share a core meaning, but differ along one of four dimensions.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_02",
            text="Degree, or intensity: warm, hot, scorching. Dislike, hate, detest. The meaning is the same, but the "
                 "strength differs.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Degree")
        self.play(FadeIn(degree[0]), GrowArrow(degree[1]))
        self.at_word(n, "warm")
        self.play(LaggedStart(*[FadeIn(c, shift=UP * 0.1) for c in degree[2]], lag_ratio=0.3))
        self.at_word(n, "Dislike")
        self.play(Indicate(degree[2], color=RATIO, scale_factor=1.05))
        self.at_word(n, "strength")
        self.play(ShowPassingFlash(degree[1].copy().set_color(RATIO).set_stroke(width=8), time_width=0.6))
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_03",
            text="Connotation, or feeling: thrifty is positive, economical is neutral, and stingy is negative. Confident "
                 "versus arrogant. Curious versus nosy.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Connotation")
        self.play(FadeIn(feeling[0]), GrowArrow(feeling[1]))
        for chip, spoken in zip(feeling[2], ["thrifty", "economical", "stingy"]):
            self.at_word(n, spoken)
            self.play(FadeIn(chip, shift=UP * 0.1), run_time=0.35)
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_04",
            text="Register, or formality: buy and purchase, start and commence, enough and sufficient. The meaning is the "
                 "same, but the setting differs.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Register")
        self.play(FadeIn(register[0]), GrowArrow(register[1]))
        self.at_word(n, "start")
        self.play(LaggedStart(*[FadeIn(c, shift=UP * 0.1) for c in register[2]], lag_ratio=0.3))
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_05",
            text="Collocation, or usage: words that go together by habit. Heavy rain, not strong rain. Make a decision, "
                 "not do a decision. Two words can mean the same thing, but only one fits a particular partner word.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Collocation")
        self.play(FadeIn(colloc[0]))
        self.at_word(n, "Heavy")
        self.play(FadeIn(colloc[1:3], shift=UP * 0.1))
        self.at_word(n, "Make")
        self.play(FadeIn(colloc[3:], shift=UP * 0.1))
        self.at_word(n, "partner")
        self.play(Indicate(colloc[1], color=GOOD), Indicate(colloc[3], color=GOOD))
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_06",
            text="In a synonym question, the best answer shares the core, and stays closest on these four dimensions. When "
                 "two options share the core, one of these dimensions breaks the tie.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "best")
        self.play(Circumscribe(rows, color=GOOD))
        self.at_word(n, "tie")
        cap = self.caption("Same core?  One of the four dimensions breaks the tie.", GOOD)
        self.play(FadeOut(colloc), FadeIn(cap, shift=UP * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_concept")

    # ======================================== 3. WHY YOU NEED IT ==========

    def why_you_need_it(self):
        self.scene_start("S03_why", title="Why You Need It")

        pair = VGroup(pill("option B:  roughly right", GOOD, size=LABEL), pill("option C:  roughly right", GOOD, size=LABEL))\
            .arrange(RIGHT, buff=0.8).move_to(UP * 1.5)
        which = pill("which dimension separates them?", FOCUS, size=BODY).move_to(UP * 0.1)
        later = VGroup(pill("Sentence Completion", WORD, size=LABEL), pill("Cloze Test", RATIO, size=LABEL))\
            .arrange(RIGHT, buff=0.6).move_to(DOWN * 1.5)
        self.validator.check_in_frame(VGroup(pair, which, later))

        n = self.narrate(
            id="why_01",
            text="The hardest synonym questions have two options that are both roughly right. The only way to choose "
                 "between them is to see which dimension separates them. The same skill decides sentence completion and "
                 "cloze test blanks later.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "hardest")
        self.play(FadeIn(pair, shift=UP * 0.2))
        self.at_word(n, "dimension")
        self.play(FadeIn(which, scale=1.05))
        self.at_word(n, "sentence")
        self.play(FadeIn(later, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_why")

    # ============================================== 4. ANALOGY ==========

    def analogy(self):
        self.scene_start("S04_analogy", title="The Analogy")

        # Knob positions (0 = bottom, 1 = top) for frugal, economical and stingy on each dimension.
        dims = ["Degree", "Feeling", "Formality", "Usage"]
        frugal = [0.5, 0.75, 0.55, 0.5]
        economical = [0.5, 0.65, 0.55, 0.5]
        stingy = [0.5, 0.05, 0.5, 0.5]
        close = max(abs(a - b) for a, b in zip(frugal, economical))
        far = max(abs(a - b) for a, b in zip(frugal, stingy))
        assert close <= 0.15 and far >= 0.6                        # synonym: all close; distractor: one far

        def mixer(values, color, title_):
            chans = VGroup(*[slider(d, v, color) for d, v in zip(dims, values)]).arrange(RIGHT, buff=0.45)
            head = pill(title_, color, size=SMALL).next_to(chans, UP, buff=0.3)
            return VGroup(head, chans)

        song = pill("the song = the core meaning", WORD, size=LABEL).move_to(UP * 2.7)
        m1 = mixer(frugal, WORD, "frugal")
        m2 = mixer(economical, GOOD, "economical  (synonym)")
        m3 = mixer(stingy, BAD, "stingy  (distractor)")
        mixers = VGroup(m1, m2, m3).arrange(RIGHT, buff=0.7).move_to(DOWN * 0.3)
        fit_width(mixers, SAFE_W)
        self.validator.check_in_frame(VGroup(song, mixers))

        n = self.narrate(
            id="analogy_01",
            text="Think of each word as a track on an audio mixer. The core meaning is the song. The four sliders are "
                 "degree, feeling, formality and usage.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "mixer")
        self.play(FadeIn(m1, shift=UP * 0.2))
        self.at_word(n, "song")
        self.play(FadeIn(song, shift=DOWN * 0.1))
        self.at_word(n, "sliders")
        self.play(*[Indicate(ch[1], color=WORD) for ch in m1[1]])
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_02",
            text="A good synonym plays the same song with the sliders in roughly the same positions. A distractor plays the "
                 "same song with one slider pushed all the way.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "good")
        self.play(FadeIn(m2, shift=UP * 0.2))
        self.at_word(n, "distractor")
        self.play(FadeIn(m3, shift=UP * 0.2))
        self.at_word(n, "pushed")
        self.play(Indicate(m3[1][1], color=BAD, scale_factor=1.15))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_analogy")

    # ======================================== 5-7. WORKED EXAMPLES ==========

    def example_frugal(self):
        self.scene_start("S05_ex_frugal", title="Worked Example 1")
        self.play(self.pin(self.steps_pin("four dimensions", [("Degree: strength", RATIO), ("Connotation: feeling", "#F48FB1"),
                                                   ("Register: formality", SECOND), ("Collocation: partners", FOCUS)])))

        word = VGroup(pill("FRUGAL", WORD, size=TITLE), text("positive: careful with money", LABEL, MUTED))\
            .arrange(DOWN, buff=0.2).move_to(UP * 1.8)
        keep = VGroup(pill("economical", GOOD, size=BODY), text("keeps the feeling  ✓", LABEL, GOOD))\
            .arrange(DOWN, buff=0.2)
        flip = VGroup(pill("stingy", BAD, size=BODY), text("flips it to negative  ✗", LABEL, BAD))\
            .arrange(DOWN, buff=0.2)
        self.place_free(VGroup(keep, flip).arrange(RIGHT, buff=1.2), y=-0.8)
        self.place_free(word)
        self.validator.check_in_frame(VGroup(word, keep, flip))

        n = self.narrate(
            id="ex1_01",
            text="Frugal is positive: careful with money. Economical keeps the feeling. Stingy flips it to negative. So "
                 "the answer is economical.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(word, shift=DOWN * 0.2), self.pin_step(1))
        self.at_word(n, "Economical")
        self.play(FadeIn(keep, shift=UP * 0.1))
        self.at_word(n, "Stingy")
        self.play(FadeIn(flip, shift=UP * 0.1))
        self.at_word(n, "answer")
        self.play(Circumscribe(keep[0], color=GOOD))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_ex_frugal")

    def example_furious(self):
        self.scene_start("S06_ex_furious", title="Worked Example 2")

        q = OptionQuestion("FURIOUS", ["annoyed", "enraged", "upset", "sad"], "b",
                           {"a": "too mild", "c": "too mild", "d": "different emotion"})
        core = pill("all share “negative emotion”: which matches the STRENGTH?", RATIO, size=SMALL)
        self.place_free(core, y=-2.8)
        self.validator.check_in_frame(VGroup(q.group.copy().move_to(LEFT * 2.4 + UP * 0.2), core))

        n = self.narrate(
            id="ex2_01",
            text="Furious: annoyed, enraged, upset, or sad? All share negative emotion, but only enraged matches the "
                 "strength. The answer is enraged.",
            voice="default",
            subtitle=True,
        )
        self.show_question(q, LEFT * 2.4 + UP * 0.2, n, ["annoyed", "enraged", "upset", "sad"])
        self.at_word(n, "negative")
        self.play(FadeIn(core, shift=UP * 0.1))
        self.at_word(n, "strength")
        _, a1 = q.strike("a")
        _, a2 = q.strike("c")
        _, a3 = q.strike("d")
        self.play(*a1, *a2, *a3, self.pin_step(0))
        self.at_word(n, "answer")
        _, ok = q.confirm()
        self.play(*ok)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_ex_furious")

    def example_commence(self):
        self.scene_start("S07_ex_commence", title="Worked Example 3")

        q = OptionQuestion("COMMENCE", ["kick off", "begin", "stop", "plan"], "b",
                           {"a": "casual register", "c": "opposite", "d": "unrelated"})
        reg = pill("commence is formal: keep the register close", SECOND, size=SMALL)
        self.place_free(reg, y=-2.8)
        self.validator.check_in_frame(VGroup(q.group.copy().move_to(LEFT * 2.4 + UP * 0.2), reg))

        n = self.narrate(
            id="ex3_01",
            text="Commence is formal. Kick off, begin, stop, or plan? Begin is closest in both meaning and register. Kick "
                 "off shares the meaning, but it's casual. The answer is begin.",
            voice="default",
            subtitle=True,
        )
        self.show_question(q, LEFT * 2.4 + UP * 0.2, n, ["Kick", "begin", "stop", "plan"])
        self.at_word(n, "register")
        self.play(FadeIn(reg, shift=UP * 0.1), self.pin_step(2))
        _, a2 = q.strike("c")
        _, a3 = q.strike("d")
        self.play(*a2, *a3)
        self.at_word(n, "casual")
        _, a1 = q.strike("a")
        self.play(*a1)
        self.at_word(n, "answer")
        _, ok = q.confirm()
        self.play(*ok)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S07_ex_commence")

    # ================================================ 8. RULES ==========

    def rules(self):
        self.scene_start("S08_rules", title="Rules")
        self.play(self.unpin())

        table = self.table_rows(["Dimension", "Question to ask", "Example"], [
            ["Degree", "Is it as strong, or as mild?", "furious ≈ enraged, not annoyed"],
            ["Connotation", "Same feeling?", "frugal ≈ economical, not stingy"],
            ["Register", "Same formality?", "commence ≈ begin, not kick off"],
            ["Collocation", "Fits the same partner words?", "heavy rain, not strong rain"],
        ], [2.8, 4.2, 4.8], size=LABEL)
        for row, (_, c) in zip(table[1:], DIMS):
            row[0].set_color(c)
        board = self.card(table, width=SAFE_W - 0.2).move_to(UP * 0.3)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="rules_01",
            text="Here's one question for each dimension. Degree: is it as strong, or as mild? Connotation: same feeling? "
                 "Register: same formality? Collocation: does it fit the same partner words?",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(board[0]), FadeIn(table[0]))
        for row, spoken in zip(table[1:], ["Degree", "Connotation", "Register", "Collocation"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.45)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S08_rules")

    # ============================================== 9. PROCESS ==========

    def process(self):
        self.scene_start("S09_process", title="The Process")

        steps = VGroup(*[VGroup(pill(str(i + 1), c, size=SMALL), fitted_text(s_, SAFE_W - 2.2, BODY, INK))
                         .arrange(RIGHT, buff=0.3) for i, (s_, c) in enumerate([
                             ("Find the core; keep only options that share it", WORD),
                             ("More than one left?  Check degree → connotation → register", RATIO),
                             ("Confirm in a sentence with the word's usual partners", GOOD)])])
        steps.arrange(DOWN, buff=0.32, aligned_edge=LEFT)
        board = self.card(steps).move_to(UP * 0.8)
        order = VGroup(*[pill(t, c, size=LABEL) for t, c in [("core", WORD), ("degree", RATIO),
                                                            ("connotation", "#F48FB1"), ("register", SECOND)]])
        chain = VGroup()
        for i, o in enumerate(order):
            if i:
                chain.add(text("→", LABEL, MUTED))
            chain.add(o)
        chain.arrange(RIGHT, buff=0.25).move_to(DOWN * 1.8)
        self.validator.check_in_frame(VGroup(board, chain))

        n = self.narrate(
            id="process_01",
            text="The process. First, find the core meaning, and cut to the options that share it. If more than one "
                 "remains, check degree, then connotation, then register. Finally, confirm by putting the answer in a "
                 "sentence that uses the word's usual partners.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(board[0]))
        self.at_word(n, "First")
        self.play(FadeIn(steps[0], shift=RIGHT * 0.2))
        self.at_word(n, "remains")
        self.play(FadeIn(steps[1], shift=RIGHT * 0.2), FadeIn(chain, shift=UP * 0.1))
        self.at_word(n, "Finally")
        self.play(FadeIn(steps[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S09_process")

    # ========================================== 10. HOOK, SOLVED ==========

    def hook_solved(self):
        self.scene_start("S10_hook_solved", title="Hook, Solved")

        h = self.HOOK
        q = OptionQuestion(h["word"], h["options"], h["key"], h["traps"])
        q.group.move_to(LEFT * 2.6 + DOWN * 0.1)
        strip = process_strip(SMALL).move_to(UP * (CARD_TOP - 0.2))
        fit_width(strip, SAFE_W)
        predict = pill("careful with money, in a good way", STEP_COLS["PREDICT"], size=SMALL)\
            .next_to(q.word, RIGHT, buff=0.5)
        confirm = text("“Priya is very economical with the project budget.”", LABEL, GOOD)
        fit_width(confirm, SAFE_W).move_to(DOWN * 2.8)
        self.validator.check_in_frame(VGroup(strip, q.group, predict, confirm))

        n = self.narrate(
            id="solved_01",
            text="Let's solve the hook. Read: frugal is an adjective with a positive feeling. Predict: careful with money, "
                 "in a good way.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(strip), FadeIn(q.word), FadeIn(q.rows))
        self.at_word(n, "Read")
        self.play(Indicate(step_chip(strip, "READ")))
        self.at_word(n, "Predict")
        self.play(Indicate(step_chip(strip, "PREDICT")), FadeIn(predict, shift=LEFT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_02",
            text="Eliminate. Poor means lacking money, not careful with it. Greedy means wanting more. Stingy shares the "
                 "core, but flips the connotation to negative.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Eliminate")
        self.play(Indicate(step_chip(strip, "ELIMINATE")))
        for letter, spoken in [("b", "Poor"), ("d", "Greedy"), ("a", "Stingy")]:
            self.at_word(n, spoken)
            _, anims = q.strike(letter)
            self.play(*anims)
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_03",
            text="Confirm: Priya is very economical with the project budget. It's a compliment. The answer is economical.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Confirm")
        self.play(Indicate(step_chip(strip, "CONFIRM")), FadeIn(confirm, shift=UP * 0.1))
        self.at_word(n, "compliment")
        self.play(Indicate(confirm, color=GOOD, scale_factor=1.03))
        self.at_word(n, "answer")
        _, ok = q.confirm()
        self.play(*ok)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S10_hook_solved")

    # ========================================== 11. EXAM PATTERNS ==========

    def exam_patterns(self):
        self.scene_start("S11_patterns", title="Exam Patterns and Solving Models")

        table = self.table_rows(["Pattern", "Solving model"], [
            ["Two options share the core", "break the tie on degree, then connotation"],
            ["Formal word in the question", "prefer the option of similar register"],
            ["Word pair / collocation", "check which option sits naturally with the partner word"],
        ], [4.4, 7.4], size=LABEL)
        board = self.card(table, width=SAFE_W - 0.2).move_to(UP * 0.4)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="patterns_01",
            text="Three exam patterns. When two options share the core, break the tie on degree, then connotation. When "
                 "the question word is formal, prefer the option of similar register. And for a word pair, check which "
                 "option sits naturally with the partner word.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(board[0]), FadeIn(table[0]))
        for row, spoken in zip(table[1:], ["two", "formal", "pair"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.45)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S11_patterns")

    # ======================================== 12. COMMON MISTAKES ==========

    def common_mistakes(self):
        self.scene_start("S12_mistakes", title="Common Mistakes")

        card_w = ZONE_W - 0.3
        pairs = [
            (self.verdict_card(False, "Stopping at the core when two options share it", card_w),
             self.verdict_card(True, "Break the tie on a dimension", card_w)),
            (self.verdict_card(False, "Ignoring strength: annoyed for furious", card_w),
             self.verdict_card(True, "Match the degree: enraged", card_w)),
            (self.verdict_card(False, "Negative word for a neutral one: nosy for curious", card_w),
             self.verdict_card(True, "Match the feeling", card_w)),
        ]
        for (wrong, right), yy in zip(pairs, [1.6, 0.05, -1.5]):
            wrong.move_to(LEFT_ZONE + UP * yy)
            right.move_to(RIGHT_ZONE + UP * yy)
        header = pill("3 mistakes", BAD, size=LABEL).move_to(UP * (CARD_TOP - 0.3))
        self.validator.check_in_frame(VGroup(header, *[c for p in pairs for c in p]))

        n = self.narrate(
            id="mistakes_01",
            text="Three common mistakes. The first is stopping at the core meaning when two options share it. The second "
                 "is ignoring strength, like choosing annoyed for furious. The third is choosing a negative word for a "
                 "neutral or positive one, like nosy for curious.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(header))
        for pr, spoken in zip(pairs, ["first", "second", "third"]):
            self.at_word(n, spoken)
            self.play(FadeIn(pr[0], shift=RIGHT * 0.3), FadeIn(pr[1], shift=LEFT * 0.3))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S12_mistakes")

    # ============================================== 13. PRACTICE ==========

    PRACTICE = [
        ("ELATED", ["overjoyed", "pleased", "calm", "relieved"], "a",
         {"b": "too mild", "c": "unrelated", "d": "different feeling"}, "intense joy"),
        ("ASSERTIVE", ["aggressive", "shy", "rude", "confident"], "d",
         {"a": "negative", "b": "opposite", "c": "negative"}, "positive, self-assured"),
        ("SUFFICIENT", ["plenty", "enough", "excess", "little"], "b",
         {"a": "more than enough", "c": "too much", "d": "too little"}, "exactly what's needed"),
    ]

    def practice(self):
        self.scene_start("S13_practice", title="Practice Questions")

        lines = VGroup(*[VGroup(pill(str(i + 1), FOCUS, size=SMALL), pill(w, WORD, size=LABEL),
                                text("   ".join(f"({l}) {o}" for l, o in zip("abcd", opts)), LABEL, INK))
                         .arrange(RIGHT, buff=0.35) for i, (w, opts, *_rest) in enumerate(self.PRACTICE)])
        lines.arrange(DOWN, buff=0.5, aligned_edge=LEFT)
        board = self.card(lines, color=FOCUS).move_to(UP * 0.4)
        fit_width(board, SAFE_W)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="practice_01",
            text="Your turn. One: elated. Overjoyed, pleased, calm, or relieved? Two: assertive. Aggressive, shy, rude, or "
                 "confident? Three: sufficient. Plenty, enough, excess, or little?",
            voice="default",
            subtitle=True,
            pause_after=10.0,
        )
        self.play(FadeIn(board[0]))
        for ln, (spoken, first_option) in zip(lines, [("elated", "Overjoyed"), ("assertive", "Aggressive"),
                                                     ("sufficient", "Plenty")]):
            self.at_word(n, spoken)
            self.play(FadeIn(ln[:2], shift=UP * 0.15), run_time=0.4)
            self.at_word(n, first_option)
            self.play(FadeIn(ln[2], shift=LEFT * 0.15), run_time=0.4)
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        self.clear_stage()
        self.scene_end("S13_practice")

    # =============================================== 14. ANSWERS ==========

    def answers(self):
        self.scene_start("S14_answers", title="Answers")

        rows = VGroup()
        for w, opts, key, traps, core in self.PRACTICE:
            OptionQuestion(w, opts, key, traps)            # validates key / traps
            rows.add(VGroup(pill(w, WORD, size=LABEL), text("→", LABEL, MUTED),
                            pill(f"({key}) {opts['abcd'.index(key)]}", GOOD, size=LABEL),
                            text(core, SMALL, INK)).arrange(RIGHT, buff=0.3))
        rows.arrange(DOWN, buff=0.35, aligned_edge=LEFT).move_to(UP * 0.9)
        fit_width(rows, SAFE_W)
        why = VGroup(pill("pleased: too mild", RATIO, size=SMALL), pill("aggressive, rude: negative", "#F48FB1", size=SMALL),
                     pill("plenty: more than enough", RATIO, size=SMALL)).arrange(RIGHT, buff=0.3)
        fit_width(why, SAFE_W).move_to(DOWN * 1.6)
        self.validator.check_in_frame(VGroup(rows, why))

        n = self.narrate(
            id="answers_01",
            text="One: overjoyed. Elated is intense joy, and pleased is too mild. Two: confident. Assertive is positive, "
                 "while aggressive and rude are negative. Three: enough. It's the same degree, exactly what's needed. "
                 "Plenty is more than enough.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "overjoyed")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "mild")
        self.play(FadeIn(why[0], shift=UP * 0.1))
        self.at_word(n, "confident")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.at_word(n, "aggressive")
        self.play(FadeIn(why[1], shift=UP * 0.1))
        self.at_word(n, "enough", occurrence=1)
        self.play(FadeIn(rows[2], shift=RIGHT * 0.2))
        self.at_word(n, "same")
        self.play(Indicate(rows[2][3], color=GOOD, scale_factor=1.05))
        self.at_word(n, "Plenty")
        self.play(FadeIn(why[2], shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S14_answers")

    # ================================================ 15. RECAP ==========

    def recap(self):
        self.scene_start("S15_recap", title="Recap Card")

        card, table = self.recap_card("Recap Card: Video 2", [
            ["Degree", "match the strength (furious ≈ enraged)"],
            ["Connotation", "match the feeling (frugal ≈ economical, not stingy)"],
            ["Register", "match the formality (commence ≈ begin)"],
            ["Collocation", "match the usual partner words (heavy rain)"],
            ["Tie-break order", "core → degree → connotation → register"],
        ])
        card.move_to(UP * 0.2)
        self.validator.check_in_frame(card)

        n = self.narrate(
            id="recap_01",
            text="To recap. Match the degree, the strength. Match the connotation, the feeling. Match the register, the "
                 "formality. And match the collocation, the usual partner words. When options tie, go in order: core, "
                 "then degree, then connotation, then register.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(card[0]), FadeIn(table[0]))
        for row, (spoken, occ) in zip(table[1:], [("degree", 1), ("connotation", 1), ("register", 1),
                                                  ("collocation", 1), ("order", 1)]):
            self.at_word(n, spoken, occurrence=occ)
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.45)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S15_recap")

    # ================================================= 16. NEXT ==========

    def next_video(self):
        self.scene_start("S16_next", title="Next")

        word = pill("bright", WORD, size=TITLE).move_to(UP * 1.4)
        senses = VGroup(pill("a bright student  →  clever", GOOD, size=LABEL),
                        pill("a bright room  →  full of light", RATIO, size=LABEL)).arrange(DOWN, buff=0.3)
        senses.move_to(DOWN * 0.2)
        nxt = pill("Next:  Context-Based Synonyms", FOCUS, size=BODY).move_to(DOWN * 2.1)
        self.validator.check_in_frame(VGroup(word, senses, nxt))

        n = self.narrate(
            id="next_01",
            text="Many words have more than one meaning. Video three shows how the sentence decides which one the "
                 "question wants.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Many")
        self.play(FadeIn(word, scale=1.1))
        self.at_word(n, "one", occurrence=1)
        self.play(LaggedStart(*[FadeIn(s, shift=UP * 0.1) for s in senses], lag_ratio=0.4))
        self.at_word(n, "Video")
        self.play(FadeIn(nxt, scale=1.1))
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S16_next")

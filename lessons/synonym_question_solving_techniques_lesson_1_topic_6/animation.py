"""
animation.py for the LMS video generator.

Course : C-CAT - Section A - English
Module : Module 1 - Vocabulary
Lesson : Lesson 1 - Synonyms
Video  : 06 - Synonym Question-Solving Techniques (Video 6 of 6)

Source script:
  C:\\Users\\User\\Downloads\\C-CAT_SectionA_Module1_English\\English\\Module 1 - Vocabulary\\
  Lesson 1 - Synonyms\\06 - Synonym Question-Solving Techniques.pdf

Built on the golden-reference pattern:
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``.

Opening: a later video of Lesson 1, so no spoken welcome. The module > lesson >
video trail is shown on screen (silent), then a one-line recap of Videos 1-5
(each idea becomes one check today), the title and the objectives.

Core visuals: the P-M-D-T checks as four airport scanner gates (each option
is stopped at the gate that catches it); worked examples with a P-M-D-T column
that lights as each check is used; a 0-30 s timeline built from ``TIMELINE``
(its segments are asserted to join up); and the +3 / -1 expected-marks card
computed with fractions (blind guess 0, one option eliminated +1/3).

Script note: the practice set repeats FRUGAL from Video 2, as the script does.

Section map (script heading -> scene):
  S00 Intro (trail + continuity)     S09 The Process
  S01 Hook                           S10 Hook, Solved
  S02 The Concept                    S11 Exam Patterns and Solving Models
  S03 Why You Need It                S12 Common Mistakes
  S04 The Analogy                    S13 Practice Questions
  S05-S07 Worked Examples 1-3        S14 Answers
  S08 Rules                          S15 Recap Card (Lesson 1 method) / S16 Next
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

import re
from fractions import Fraction

CHECKS = [("P", "Part of speech", WORD), ("M", "Meaning core", BAD), ("D", "Degree", RATIO),
          ("T", "Tone & register", SECOND)]
CHECK_COL = {k: c for k, _, c in CHECKS}

# Time budget from the script (seconds): (start, end, step).
TIMELINE = [(0, 5, "read + predict"), (5, 20, "P and M on all four"), (20, 25, "D and T if two remain"),
            (25, 30, "confirm + “is this the opposite?”")]


def expected_marks(options_left, right=3, wrong=-1):
    """Expected marks for a blind guess among ``options_left`` options (+3 / −1 marking)."""
    p = Fraction(1, options_left)
    return p * right + (1 - p) * wrong


def scanner(letter, name, color, width=2.2, height=2.4):
    """One airport scanner gate: an arch with the check letter and its name."""
    arch = VGroup(Line(DOWN * height / 2, UP * height / 2, color=color, stroke_width=6).shift(LEFT * width / 2),
                  Line(DOWN * height / 2, UP * height / 2, color=color, stroke_width=6).shift(RIGHT * width / 2),
                  Line(LEFT * width / 2 + UP * height / 2, RIGHT * width / 2 + UP * height / 2, color=color,
                       stroke_width=6))
    tag = text(letter, TITLE, color, BOLD).next_to(arch, UP, buff=0.15)
    name_ = text(name, SMALL, color).next_to(arch, DOWN, buff=0.15)
    return VGroup(arch, tag, name_)


class SynonymTechniquesVideo(LMSScene):
    lesson_title = "Synonym Question-Solving Techniques"

    def construct(self):
        self.camera.background_color = BG

        self.lesson_intro()
        self.hook()
        self.concept()
        self.why_you_need_it()
        self.analogy()
        self.example_pragmatic()
        self.example_reticent()
        self.example_incessant()
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

    def method_strip(self, size=LABEL):
        parts = [("PREDICT", STEP_COLS["PREDICT"])] + [(k, c) for k, _, c in CHECKS] + [("CONFIRM", GOOD)]
        chips = []
        for i, (t, c) in enumerate(parts):
            if i:
                chips.append(text("→", size, MUTED))
            chips.append(pill(t, c, size=size))
        return VGroup(*chips).arrange(RIGHT, buff=0.2)

    def alert_card(self, word="abate", fill=False):
        head = VGroup(text("WEATHER ALERT", SMALL, RATIO, BOLD), pill("0:30", BAD, size=SMALL)).arrange(RIGHT, buff=0.5)
        body = text(f"“The cyclone is expected to {word} by Thursday.”", BODY, INK,
                    t2c={rf"\b{word}\b": GOOD if fill else WORD})
        cx, w = self.free_area()
        card = self.card(VGroup(head, fit_width(body, w - 1.4)).arrange(DOWN, buff=0.2, aligned_edge=LEFT),
                         width=w - 0.2)
        return card.move_to(RIGHT * cx + UP * (CARD_TOP - card.height / 2))

    def pmdt_example(self, word, options, key, traps):
        """Question on the left; the pinned P-M-D-T panel lights as each check is used."""
        q = OptionQuestion(word, options, key, traps, word_size=TITLE)
        q.group.to_edge(LEFT, buff=SAFE + 0.6).set_y(0.3)
        self.no_overlap(q.group, self.pinned)
        self.validator.check_in_frame(q.group)
        return q, self.pinned

    # ========================================= 0. LESSON INTRO ==========
    # Purpose: silent trail, a one-line recap of Videos 1-5 (each becomes a
    # check today), today's topic, the objectives.

    def lesson_intro(self):
        self.scene_start("S00_intro", title="Lesson Introduction")

        crumb = self.breadcrumb("English · Module 1 Vocabulary", "Lesson 1 · Synonyms", "Video 6")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        ideas = VGroup(*[pill(t, c, size=LABEL) for t, c in [("method", WORD), ("tie-breakers", RATIO),
                                                            ("context", SECOND), ("look-alikes", BAD),
                                                            ("shelves & roots", GOOD)]]).arrange(RIGHT, buff=0.3)
        fit_width(ideas, SAFE_W)
        one = pill("each one becomes a check in today's method", FOCUS, size=LABEL)
        VGroup(ideas, one).arrange(DOWN, buff=0.8).move_to(DOWN * 0.1)
        self.no_overlap(crumb, ideas, one)
        self.validator.check_in_frame(VGroup(crumb, ideas, one))

        n = self.narrate(
            id="intro_01",
            text="Every idea from videos one to five becomes one check in today's method.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.at_word(n, "idea")
        self.play(LaggedStart(*[FadeIn(i, shift=UP * 0.1) for i in ideas], lag_ratio=0.15))
        self.at_word(n, "check")
        self.play(FadeIn(one, shift=UP * 0.1))
        self.wait_for_narration(n)

        title = fitted_text("Synonym Question-Solving Techniques", SAFE_W, 64, INK, BOLD)
        underline = Line(LEFT, RIGHT, color=GOOD, stroke_width=5).set_width(title.width * 0.6)
        VGroup(title, underline).arrange(DOWN, buff=0.2).move_to(UP * 0.2)
        n = self.narrate(
            id="intro_02",
            text="This is the last video of lesson one: synonym question-solving techniques.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(VGroup(ideas, one), shift=UP * 0.3))
        self.at_word(n, "synonym")
        self.play(Write(title), run_time=1.1)
        self.play(GrowFromCenter(underline))
        self.wait_for_narration(n)

        goals = [
            ("Solve any synonym question with a fixed four-check elimination", BAD),
            ("Finish a synonym question in about 30 seconds", GOOD),
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
            text="By the end of this video, you'll solve any synonym question with a fixed four-check elimination, and "
                 "finish it in about thirty seconds.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(underline), ReplacementTransform(title, small_title), run_time=0.8)
        self.play(FadeIn(objectives[0]), FadeIn(heading))
        for row_, spoken in zip(rows, ["solve", "finish"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row_, shift=RIGHT * 0.2), run_time=0.5)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_intro")

    # ================================================= 1. HOOK ==========

    HOOK = dict(word="ABATE", options=["subside", "intensify", "arrive", "wander"], key="a",
                traps={"b": "M: the ANTONYM (the trap)", "c": "M: movement, not strength",
                       "d": "M: movement, not strength"})

    def hook(self):
        self.scene_start("S01_hook", title="Hook")

        alert = self.alert_card()
        h = self.HOOK
        q = OptionQuestion(h["word"], h["options"], h["key"], h["traps"])
        opts = q.rows.copy().arrange(RIGHT, buff=0.8)
        fit_width(opts, SAFE_W)
        danger = pill("the trap here is the most dangerous kind", BAD, size=SMALL)
        opts.next_to(alert, DOWN, buff=0.9)
        danger.next_to(opts, DOWN, buff=0.7)
        self.no_overlap(alert, opts, danger)
        self.validator.check_in_frame(VGroup(alert, opts, danger))

        n = self.narrate(
            id="hook_01",
            text="A weather alert says: The cyclone is expected to abate by Thursday. Your family is deciding whether to "
                 "travel on Friday. You have thirty seconds.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(alert, shift=DOWN * 0.2))
        self.at_word(n, "travel")
        self.play(Indicate(alert[1][1], color=WORD, scale_factor=1.02))
        self.at_word(n, "seconds")
        self.play(Indicate(alert[1][0][1], color=BAD, scale_factor=1.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_02",
            text="Abate is closest to: subside, intensify, arrive, or wander? The trap here is the most dangerous kind in "
                 "synonym questions. Let's see if the method catches it.",
            voice="default",
            subtitle=True,
            pause_after=3.0,
        )
        for row, spoken in zip(opts, ["subside", "intensify", "arrive", "wander"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=UP * 0.15), run_time=0.35)
        self.at_word(n, "dangerous")
        self.play(FadeIn(danger, shift=UP * 0.1))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        self.clear_stage()
        self.scene_end("S01_hook")

    # ============================================== 2. CONCEPT ==========

    def concept(self):
        self.scene_start("S02_concept", title="The Concept")

        head = pill("four kinds of distractor  →  four checks:  P-M-D-T", FOCUS, size=LABEL)
        fit_width(head, SAFE_W)
        head.move_to(UP * (CARD_TOP - head.height / 2))
        rows = VGroup(*[VGroup(pill(k, c, size=BODY), text(name, LABEL, c, BOLD),
                               fitted_text(q, 6.4, LABEL, INK)).arrange(RIGHT, buff=0.35)
                        for (k, name, c), q in zip(CHECKS, [
                            "adjective for adjective?",
                            "same core? (catches opposites, sound-alikes, “nearby” words)",
                            "as strong, or as mild?",
                            "same feeling? same formality?"])])
        rows.arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        fit_width(rows, SAFE_W)
        rows.next_to(head, DOWN, buff=0.45)
        split = VGroup(pill("P, M: fast, remove most options", GOOD, size=SMALL),
                       pill("D, T: tie-breakers for the last two", RATIO, size=SMALL)).arrange(RIGHT, buff=0.4)
        fit_width(split, SAFE_W)
        split.next_to(rows, DOWN, buff=0.4)
        self.no_overlap(head, rows, split)
        self.validator.check_in_frame(VGroup(head, rows, split))

        n = self.narrate(
            id="concept_01",
            text="Synonym distractors are built in four predictable ways, so four checks catch them: P, M, D, T.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_02",
            text="P is part of speech: does the option match the word's grammar, adjective for adjective? M is meaning "
                 "core: does it share the core meaning? This check catches opposites, sound-alikes and nearby words. D is "
                 "degree: is it as strong, or as mild? And T is tone and register: same feeling, same formality?",
            voice="default",
            subtitle=True,
        )
        for r, (spoken, occ) in zip(rows, [("part", 1), ("meaning", 1), ("degree", 1), ("tone", 1)]):
            self.at_word(n, spoken, occurrence=occ)
            self.play(FadeIn(r, shift=RIGHT * 0.2), run_time=0.45)
            if spoken == "meaning":
                self.at_word(n, "catches")
                self.play(Indicate(r[2], color=BAD, scale_factor=1.04), run_time=0.5)
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_03",
            text="Run them in that order. P and M are fast, and remove most options. D and T are the tie-breakers for the "
                 "last two. Before any of this, predict your own answer, so the options can't pull you.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "order")
        self.play(LaggedStart(*[Indicate(r[0], color=FOCUS) for r in rows], lag_ratio=0.25), run_time=1.0)
        self.at_word(n, "fast")
        self.play(FadeIn(split[0], shift=UP * 0.1))
        self.at_word(n, "tie-breakers")
        self.play(FadeIn(split[1], shift=UP * 0.1))
        self.at_word(n, "predict")
        cap = self.caption("Predict first, so the options can't pull you", STEP_COLS["PREDICT"])
        self.play(FadeOut(split), FadeIn(cap, shift=UP * 0.2))
        self.wait_for_narration(n)

        # The antonym habit.
        habit = VGroup(pill("the most dangerous distractor: the ANTONYM", BAD, size=BODY),
                       text("under pressure the brain reads “strongly related” and grabs it", LABEL, MUTED),
                       pill("before confirming, ask:  Is my answer the opposite?", GOOD, size=BODY))\
            .arrange(DOWN, buff=0.45)
        fit_width(habit, SAFE_W).move_to(UP * 0.3)
        self.validator.check_in_frame(habit)
        n = self.narrate(
            id="concept_04",
            text="The most dangerous distractor is the antonym. Under time pressure, the brain registers strongly related, "
                 "and grabs it. So make one habit automatic: before confirming, ask, is my answer the opposite?",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(VGroup(head, rows, cap)))
        self.at_word(n, "antonym")
        self.play(FadeIn(habit[0], scale=1.05))
        self.at_word(n, "pressure")
        self.play(FadeIn(habit[1], shift=UP * 0.1))
        self.at_word(n, "habit")
        self.play(FadeIn(habit[2], shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_concept")

    # ======================================== 3. WHY YOU NEED IT ==========

    def why_you_need_it(self):
        self.scene_start("S03_why", title="Why You Need It")

        bar = VGroup(Rectangle(width=7.0, height=0.5, color=MUTED, fill_opacity=0.1),
                     Rectangle(width=3.0, height=0.5, color=GOOD, fill_color=GOOD, fill_opacity=0.5))
        bar[1].align_to(bar[0], LEFT)
        bar_lab = VGroup(text("≈ 70 s per question", SMALL, MUTED).next_to(bar[0], UP, buff=0.15).align_to(bar[0], RIGHT),
                         text("synonym: 30 s", SMALL, GOOD).next_to(bar[1], UP, buff=0.15).align_to(bar[1], LEFT))
        saved = pill("the rest banks time for aptitude", GOOD, size=SMALL).next_to(bar, DOWN, buff=0.3)
        time_block = VGroup(bar, bar_lab, saved).move_to(UP * 1.3)
        blind, one_out = expected_marks(4), expected_marks(3)
        ev = VGroup(VGroup(pill("blind guess (4 left)", MUTED, size=LABEL), text(f"expected: {blind}", LABEL, MUTED))
                    .arrange(DOWN, buff=0.15),
                    VGroup(pill("one eliminated (3 left)", GOOD, size=LABEL),
                           text(f"expected: +{one_out}", LABEL, GOOD)).arrange(DOWN, buff=0.15)).arrange(RIGHT, buff=1.2)
        mark = text("+3 / −1 marking", LABEL, FOCUS, BOLD)
        ev_block = VGroup(mark, ev).arrange(DOWN, buff=0.35).move_to(DOWN * 1.6)
        assert blind == 0 and one_out == Fraction(1, 3)
        self.no_overlap(time_block, ev_block)
        self.validator.check_in_frame(VGroup(time_block, ev_block))

        n = self.narrate(
            id="why_01",
            text="At about seventy seconds per question in section A, synonym questions should take thirty seconds, which "
                 "banks time for aptitude.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "seventy")
        self.play(FadeIn(bar[0]), FadeIn(bar_lab[0]))
        self.at_word(n, "thirty")
        self.play(GrowFromEdge(bar[1], LEFT), FadeIn(bar_lab[1]))
        self.at_word(n, "banks")
        self.play(FadeIn(saved, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="why_02",
            text="And a plus three, minus one marking scheme rewards a method that turns one elimination into a "
                 "positive-value guess. A blind guess is worth nothing on average. Remove one option, and the guess is "
                 "worth a third of a mark.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "marking")
        self.play(FadeIn(mark, shift=DOWN * 0.1))
        self.at_word(n, "blind")
        self.play(FadeIn(ev[0], shift=UP * 0.1))
        self.at_word(n, "Remove")
        self.play(FadeIn(ev[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_why")

    # ============================================== 4. ANALOGY ==========

    def analogy(self):
        self.scene_start("S04_analogy", title="The Analogy")

        board = pill("board", GOOD, size=LABEL)
        # Travellers: where each one is stopped (index of the gate) or None if it boards.
        travellers = [("noun", 0), ("antonym", 1), ("too mild", 2), ("synonym", None)]
        dots = VGroup(*[pill(t, INK if stop is None else MUTED, size=SMALL) for t, stop in travellers])
        fit_width(dots.arrange(DOWN, buff=0.25), 1.9)
        # The row is travellers | gates | board: the gates get whatever width the other two leave.
        gap = 0.4
        gates = VGroup(*[scanner(k, name, c) for k, name, c in CHECKS]).arrange(RIGHT, buff=0.3)
        fit_width(gates, SAFE_W - dots.width - board.width - 2 * gap)
        VGroup(dots, gates, board).arrange(RIGHT, buff=gap).move_to(DOWN * 0.2)
        self.no_overlap(dots, gates, board)
        self.validator.check_in_frame(VGroup(dots, gates, board))

        n = self.narrate(
            id="analogy_01",
            text="Think of airport security. Four scanners in a row, each built to catch one kind of item.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Four")
        self.play(LaggedStart(*[FadeIn(g, shift=UP * 0.2) for g in gates], lag_ratio=0.2))
        self.at_word(n, "catch")
        self.play(FadeIn(dots, shift=RIGHT * 0.1), FadeIn(board))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_02",
            text="An option has to pass all four to board. Most fail at the first two.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "pass")
        for chip, (label, stop) in zip(dots, travellers):
            target_x = gates[stop][0].get_center()[0] if stop is not None                 else board.get_left()[0] - chip.width / 2 - 0.15      # stop beside "board", never on it
            self.play(chip.animate.set_x(target_x), run_time=0.6)
            if stop is not None:
                self.play(chip.animate.set_opacity(0.3), Flash(chip.get_center(), color=CHECKS[stop][2],
                                                               flash_radius=0.4), run_time=0.4)
            else:
                self.play(Indicate(chip, color=GOOD), Indicate(board, color=GOOD), run_time=0.5)
        self.at_word(n, "first")
        self.play(Circumscribe(gates[:2], color=GOOD))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_analogy")

    # ======================================== 5-7. WORKED EXAMPLES ==========

    def light(self, col, letter):
        """Animation: light the row of the pinned P-M-D-T panel for this check."""
        return self.pin_step([k for k, _, _ in CHECKS].index(letter), color=CHECK_COL[letter])

    def example_pragmatic(self):
        self.scene_start("S05_ex_pragmatic", title="Worked Example 1")
        self.play(self.pin(self.steps_pin("P-M-D-T", [(f"{k}  {name}", c) for k, name, c in CHECKS])))

        q, col = self.pmdt_example("PRAGMATIC", ["practical", "idealistic", "dramatic", "pragmatism"], "a",
                                   {"b": "M: opposite", "c": "M: sound-alike", "d": "P: noun"})

        n = self.narrate(
            id="ex1_01",
            text="Pragmatic: practical, idealistic, dramatic, or pragmatism? P: pragmatism is a noun, so it's out. M: "
                 "idealistic is the opposite, and dramatic is a sound-alike, so both are out. The answer is practical.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(q.word, scale=1.1))
        self.at_word(n, "practical", occurrence=1)
        self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.2) for r in q.rows], lag_ratio=0.2))
        self.at_word(n, "P")
        self.play(self.light(col, "P"), *q.strike("d")[1])
        self.at_word(n, "M")
        self.play(self.light(col, "M"), *q.strike("b")[1])
        self.at_word(n, "dramatic", occurrence=2)
        self.play(*q.strike("c")[1])
        self.at_word(n, "answer")
        self.play(*q.confirm()[1])
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_ex_pragmatic")

    def example_reticent(self):
        self.scene_start("S06_ex_reticent", title="Worked Example 2")

        q, col = self.pmdt_example("RETICENT", ["talkative", "reserved", "rude", "recent"], "b",
                                   {"a": "M: antonym", "c": "M: unrelated", "d": "M: sound-alike"})

        n = self.narrate(
            id="ex2_01",
            text="Reticent: talkative, reserved, rude, or recent? M: talkative is the antonym, recent is a sound-alike, and "
                 "rude is unrelated. The answer is reserved.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(q.word, scale=1.1))
        self.at_word(n, "talkative", occurrence=1)
        self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.2) for r in q.rows], lag_ratio=0.2))
        self.at_word(n, "M")
        self.play(self.light(col, "M"))
        self.at_word(n, "antonym")
        self.play(*q.strike("a")[1])
        self.at_word(n, "sound-alike")
        self.play(*q.strike("d")[1])
        self.at_word(n, "unrelated")
        self.play(*q.strike("c")[1])
        self.at_word(n, "answer")
        self.play(*q.confirm()[1])
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_ex_reticent")

    def example_incessant(self):
        self.scene_start("S07_ex_incessant", title="Worked Example 3")

        q, col = self.pmdt_example("INCESSANT", ["occasional", "constant", "loud", "innocent"], "b",
                                   {"a": "M: antonym", "c": "M: unrelated", "d": "M: sound-alike"})

        n = self.narrate(
            id="ex3_01",
            text="Incessant: occasional, constant, loud, or innocent? M: occasional is the antonym, and innocent is a "
                 "sound-alike. Loud is about volume, not time. D: constant matches never stopping. The answer is "
                 "constant.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(q.word, scale=1.1))
        self.at_word(n, "occasional", occurrence=1)
        self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.2) for r in q.rows], lag_ratio=0.2))
        self.at_word(n, "M")
        self.play(self.light(col, "M"), *q.strike("a")[1])
        self.at_word(n, "sound-alike")
        self.play(*q.strike("d")[1])
        self.at_word(n, "Loud", occurrence=2)
        self.play(*q.strike("c")[1])
        self.at_word(n, "D")
        self.play(self.light(col, "D"))
        self.at_word(n, "answer")
        self.play(*q.confirm()[1])
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S07_ex_incessant")

    # ================================================ 8. RULES ==========

    def rules(self):
        self.scene_start("S08_rules", title="Rules")
        self.play(self.unpin())

        strip = self.method_strip()
        fit_width(strip, SAFE_W)
        strip.move_to(UP * (CARD_TOP - strip.height / 2))
        table = self.table_rows(["Check", "Catches"], [
            ["P", "nouns for adjectives, verbs for nouns"],
            ["M", "antonyms, sound-alikes, “nearby” words"],
            ["D", "too mild or too strong"],
            ["T", "positive for negative, casual for formal"],
        ], [2.0, 9.0], size=LABEL)
        for row, (_, _, c) in zip(table[1:], CHECKS):
            row[0].set_color(c)
        board = self.card(table, width=SAFE_W - 0.2)
        board.next_to(strip, DOWN, buff=0.5)
        self.no_overlap(strip, board)
        self.validator.check_in_frame(VGroup(strip, board))

        n = self.narrate(
            id="rules_01",
            text="The full method: predict, then P, M, D, T, then confirm. P catches nouns for adjectives, and verbs for "
                 "nouns. M catches antonyms, sound-alikes and nearby words. D catches options that are too mild or too "
                 "strong. And T catches positive for negative, and casual for formal.",
            voice="default",
            subtitle=True,
        )
        self.play(LaggedStart(*[FadeIn(c, shift=RIGHT * 0.1) for c in strip], lag_ratio=0.1))
        self.play(FadeIn(board[0]), FadeIn(table[0]))
        for row, spoken in zip(table[1:], ["nouns", "antonyms", "mild", "positive"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.45)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S08_rules")

    # ============================================== 9. PROCESS ==========

    def process(self):
        self.scene_start("S09_process", title="The Process: 30 Seconds")

        scale = 0.38                                          # units per second
        cols = [STEP_COLS["PREDICT"], BAD, RATIO, GOOD]
        segs = VGroup(*[Rectangle(width=(e - s_) * scale, height=0.55, color=c, fill_color=c, fill_opacity=0.35)
                        for (s_, e, _), c in zip(TIMELINE, cols)]).arrange(RIGHT, buff=0)
        segs.move_to(UP * 1.4)
        ticks = VGroup(*[text(f"{t} s", SMALL, MUTED).next_to(segs, DOWN, buff=0.15).set_x(segs.get_left()[0] + t * scale)
                         for t in [0, 5, 20, 25, 30]])
        labels = VGroup(*[fitted_text(lab, 5.2, LABEL, c) for (_, _, lab), c in zip(TIMELINE, cols)])
        labels.arrange(DOWN, buff=0.22, aligned_edge=LEFT)
        rows = VGroup(*[VGroup(pill(f"{s_}–{e} s", c, size=SMALL), lab).arrange(RIGHT, buff=0.3)
                        for (s_, e, _), c, lab in zip(TIMELINE, cols, labels)]).arrange(DOWN, buff=0.22,
                                                                                        aligned_edge=LEFT)
        rows.next_to(ticks, DOWN, buff=0.5)
        never = pill("never guess without at least one elimination", FOCUS, size=SMALL)
        never.next_to(rows, DOWN, buff=0.4)
        assert TIMELINE[0][0] == 0 and TIMELINE[-1][1] == 30 and all(a[1] == b[0] for a, b in zip(TIMELINE, TIMELINE[1:]))
        self.no_overlap(VGroup(segs, ticks), rows, never)
        self.validator.check_in_frame(VGroup(segs, ticks, rows, never))

        n = self.narrate(
            id="process_01",
            text="Here's the thirty-second budget. From zero to five seconds, read the word, and predict. From five to "
                 "twenty, run P and M across all four options. From twenty to twenty-five, if two remain, run D and T. "
                 "From twenty-five to thirty, confirm in a sentence, and ask, is this the opposite?",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(ticks))
        for seg, row, (spoken, occ) in zip(segs, rows, [("zero", 1), ("five", 2), ("twenty", 2),
                                                         ("twenty-five", 2)]):
            self.at_word(n, spoken, occurrence=occ)
            self.play(GrowFromEdge(seg, LEFT), FadeIn(row, shift=RIGHT * 0.2), run_time=0.5)
        self.wait_for_narration(n)

        n = self.narrate(
            id="process_02",
            text="And never guess without at least one elimination.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "never")
        self.play(FadeIn(never, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S09_process")

    # ========================================== 10. HOOK, SOLVED ==========

    def hook_solved(self):
        self.scene_start("S10_hook_solved", title="Hook, Solved")
        self.play(self.pin(self.steps_pin("P-M-D-T", [(f"{k}  {name}", c) for k, name, c in CHECKS])))

        h = self.HOOK
        alert = self.alert_card()
        q = OptionQuestion(h["word"], h["options"], h["key"], h["traps"], word_size=BODY)
        q.group.next_to(alert, DOWN, buff=0.45).to_edge(LEFT, buff=SAFE + 0.6)
        predict = pill("predict: weaken, die down", STEP_COLS["PREDICT"], size=SMALL)
        predict.next_to(q.word, RIGHT, buff=0.4)
        self.no_overlap(predict, self.pinned)
        filled = self.alert_card("subside", fill=True)
        verdict = pill("Is it the opposite?  No.  Friday travel looks reasonable, subject to the next update", GOOD,
                       size=SMALL)
        fit_width(verdict, SAFE_W)
        verdict.to_edge(DOWN, buff=SAFE + 0.4)
        self.no_overlap(alert, q.group, verdict)
        self.validator.check_in_frame(VGroup(alert, q.group, predict, verdict))

        n = self.narrate(
            id="solved_01",
            text="Let's solve the hook. Read: abate, a verb, in a weather alert. Predict: weaken, or die down.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(alert), FadeIn(q.word), FadeIn(q.rows))
        self.at_word(n, "Read")
        self.play(Indicate(q.word, color=WORD, scale_factor=1.1), self.pin_step(0))
        self.at_word(n, "Predict")
        self.play(FadeIn(predict, shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_02",
            text="Eliminate with M. Intensify is the antonym: the trap. Arrive and wander are about movement, not "
                 "strength.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Eliminate")
        self.play(self.pin_step(1, color=BAD))
        self.at_word(n, "Intensify")
        self.play(*q.strike("b")[1])
        self.at_word(n, "Arrive")
        self.play(*q.strike("c")[1], *q.strike("d")[1])
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_03",
            text="Confirm: the cyclone is expected to subside by Thursday. The answer is subside. Is it the opposite? No. "
                 "So Friday travel looks reasonable, subject to the next update.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Confirm")
        self.play(ReplacementTransform(alert, filled))
        self.at_word(n, "answer")
        self.play(*q.confirm()[1])
        self.at_word(n, "opposite")
        self.play(FadeIn(verdict, shift=UP * 0.1))
        self.at_word(n, "No")
        self.play(Indicate(q.row("b"), color=BAD, scale_factor=1.05))
        self.at_word(n, "Friday")
        self.play(Circumscribe(verdict, color=GOOD))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S10_hook_solved")

    # ========================================== 11. EXAM PATTERNS ==========

    def exam_patterns(self):
        self.scene_start("S11_patterns", title="Exam Patterns and Solving Models")
        self.play(self.unpin())

        table = self.table_rows(["Pattern", "First checks"], [
            ["Single word, four options", "P, M"],
            ["Two close survivors", "D, T"],
            ["Word in a sentence", "context first (Video 3), then P, M"],
            ["Look-alike in the options", "M, with the pair hook (Video 4)"],
        ], [5.2, 6.6], size=LABEL)
        board = self.card(table, width=SAFE_W - 0.2).move_to(UP * 0.4)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="patterns_01",
            text="Which checks come first? For a single word with four options: P and M. For two close survivors: D and T. "
                 "For a word in a sentence: context first, from video three, then P and M. And for a look-alike in the "
                 "options: M, with the pair hook from video four.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(board[0]), FadeIn(table[0]))
        for row, spoken in zip(table[1:], ["single", "survivors", "sentence", "look-alike"]):
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
            (self.verdict_card(False, "Picking the antonym under time pressure", card_w),
             self.verdict_card(True, "Ask: is this the opposite?", card_w)),
            (self.verdict_card(False, "Reading the options before predicting", card_w),
             self.verdict_card(True, "Predict first", card_w)),
            (self.verdict_card(False, "Over a minute on an unknown word", card_w),
             self.verdict_card(True, "Use roots, eliminate one, move on", card_w)),
        ]
        for (wrong, right), yy in zip(pairs, [1.6, 0.05, -1.5]):
            wrong.move_to(LEFT_ZONE + UP * yy)
            right.move_to(RIGHT_ZONE + UP * yy)
        header = pill("3 mistakes", BAD, size=LABEL).move_to(UP * (CARD_TOP - 0.3))
        self.validator.check_in_frame(VGroup(header, *[c for p in pairs for c in p]))

        n = self.narrate(
            id="mistakes_01",
            text="Three common mistakes. The first is picking the antonym under time pressure. The second is reading the "
                 "options before predicting. The third is spending over a minute on an unknown word, instead of using "
                 "roots and moving on.",
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
        ("VINDICATE", ["accuse", "revenge", "avoid", "justify"], "d",
         {"a": "antonym", "b": "nearby word", "c": "unrelated"}, "to clear of blame"),
        ("FRUGAL", ["wasteful", "fruitful", "economical", "greedy"], "c",
         {"a": "antonym", "b": "sound-alike", "d": "different meaning"}, "careful with money"),
        ("AMBIGUOUS", ["clear", "uncertain", "ambitious", "angry"], "b",
         {"a": "antonym", "c": "sound-alike", "d": "unrelated"}, "open to more than one meaning"),
    ]

    def practice(self):
        self.scene_start("S13_practice", title="Practice Questions")

        lines = VGroup(*[VGroup(pill(str(i + 1), FOCUS, size=SMALL), pill(w, WORD, size=LABEL),
                                text("   ".join(f"({l}) {o}" for l, o in zip("abcd", opts)), LABEL, INK))
                         .arrange(RIGHT, buff=0.35) for i, (w, opts, *_r) in enumerate(self.PRACTICE)])
        lines.arrange(DOWN, buff=0.5, aligned_edge=LEFT)
        board = self.card(lines, color=FOCUS).move_to(UP * 0.4)
        fit_width(board, SAFE_W)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="practice_01",
            text="Your turn, thirty seconds each. One: vindicate. Accuse, revenge, avoid, or justify? Two: frugal. "
                 "Wasteful, fruitful, economical, or greedy? Three: ambiguous. Clear, uncertain, ambitious, or angry?",
            voice="default",
            subtitle=True,
            pause_after=12.0,
        )
        self.play(FadeIn(board[0]))
        for ln, (spoken, first_option) in zip(lines, [("vindicate", "Accuse"), ("frugal", "Wasteful"),
                                                     ("ambiguous", "Clear")]):
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
            others = [f"({l}) {opts['abcd'.index(l)]}: {r}" for l, r in traps.items()
                      if r in ("antonym", "sound-alike", "nearby word")]
            rows.add(VGroup(pill(w, WORD, size=LABEL), text("→", LABEL, MUTED),
                            pill(f"({key}) {opts['abcd'.index(key)]}", GOOD, size=LABEL),
                            text("   ".join(others), SMALL, BAD)).arrange(RIGHT, buff=0.3))
        rows.arrange(DOWN, buff=0.45, aligned_edge=LEFT)
        fit_width(rows, SAFE_W).move_to(UP * 0.3)
        self.validator.check_in_frame(rows)

        n = self.narrate(
            id="answers_01",
            text="One: justify, to clear of blame. Accuse is the antonym, and revenge is a nearby word. Two: economical. "
                 "Wasteful is the antonym, and fruitful is a sound-alike. Three: uncertain, open to more than one meaning. "
                 "Clear is the antonym, and ambitious is a sound-alike.",
            voice="default",
            subtitle=True,
        )
        for r, (spoken, trap) in zip(rows, [("justify", "Accuse"), ("economical", "Wasteful"),
                                           ("uncertain", "Clear")]):
            self.at_word(n, spoken)
            self.play(FadeIn(r[:3], shift=RIGHT * 0.2), run_time=0.5)
            self.at_word(n, trap)
            self.play(FadeIn(r[3], shift=LEFT * 0.1), run_time=0.4)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S14_answers")

    # ================================================ 15. RECAP ==========

    def recap(self):
        self.scene_start("S15_recap", title="Recap Card: Lesson 1 Method")

        card, table = self.recap_card("Recap Card: Lesson 1 Method", [
            ["Method", "PREDICT → P → M → D → T → CONFIRM"],
            ["Biggest trap", "the antonym: always ask “is this the opposite?”"],
            ["Other traps", "sound-alikes, nearby words, wrong part of speech"],
            ["Time", "about 30 seconds per synonym question"],
        ])
        card.move_to(UP * 0.2)
        self.validator.check_in_frame(card)

        n = self.narrate(
            id="recap_01",
            text="To recap the lesson one method: predict, then P, M, D, T, then confirm. The biggest trap is the antonym, "
                 "so always ask, is this the opposite? The other traps are sound-alikes, nearby words, and the wrong part "
                 "of speech. And the target time is about thirty seconds per synonym question.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(card[0]), FadeIn(table[0]))
        for row, spoken in zip(table[1:], ["predict", "biggest", "other", "time"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.45)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S15_recap")

    # ================================================= 16. NEXT ==========

    def next_video(self):
        self.scene_start("S16_next", title="Next")

        done = pill("Lesson 1: Synonyms  ✓", GOOD, size=LABEL)
        todo = VGroup(pill("Lesson 1 Quiz", FOCUS, size=LABEL), pill("Cheat Sheet", WORD, size=LABEL))\
            .arrange(RIGHT, buff=0.6)
        flip = VGroup(pill("synonym:  same", GOOD, size=BODY), text("⇄", TITLE, MUTED),
                      pill("antonym:  opposite", BAD, size=BODY)).arrange(RIGHT, buff=0.4)
        nxt = pill("Next lesson:  Antonyms", FOCUS, size=BODY)
        VGroup(done, todo, flip, nxt).arrange(DOWN, buff=0.5).move_to(UP * 0.1)
        self.no_overlap(done, todo, flip, nxt)
        self.validator.check_in_frame(VGroup(done, todo, flip, nxt))

        n = self.narrate(
            id="next_01",
            text="Take the lesson one quiz, and keep the cheat sheet. Lesson two flips everything: antonyms.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(done, scale=1.1))
        self.at_word(n, "quiz")
        self.play(FadeIn(todo[0], shift=UP * 0.1))
        self.at_word(n, "cheat")
        self.play(FadeIn(todo[1], shift=UP * 0.1))
        self.at_word(n, "flips")
        self.play(FadeIn(flip, shift=UP * 0.1))
        self.at_word(n, "antonyms")
        self.play(FadeIn(nxt, scale=1.1))
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S16_next")

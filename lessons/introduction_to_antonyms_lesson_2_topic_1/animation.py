"""
animation.py for the LMS video generator.

Course : C-CAT - Section A - English
Module : Module 1 - Vocabulary
Lesson : Lesson 2 - Antonyms
Video  : 01 - Introduction to Antonyms (Video 1 of 7)

Source script:
  C:\\Users\\User\\Downloads\\C-CAT_SectionA_Module1_English\\English\\Module 1 - Vocabulary\\
  Lesson 2 - Antonyms\\01 - Introduction to Antonyms.pdf

Built on the golden-reference pattern:
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``;
  * layouts stacked with next_to and guarded with ``no_overlap``; nothing is
    ever animated onto or into another box.

Opening: first video of a NEW LESSON, so no spoken welcome. The module >
lesson > video trail is shown on screen (silent), then a one-line recap of
Lesson 1 (its PREDICT-P-M-D-T-CONFIRM method), one line saying Lesson 2
starts (match the word -> OPPOSE the word), the title and the objectives.

Core visuals: ``OptionQuestion`` cards with the synonym trap struck first; a
compass whose needle swings north (synonym) and south (antonym); the confirm
step as a contrast sentence, "Not X, but Y."
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

OPP = "#EF9A9A"          # antonym direction colour (south)


def contrast(x, y, size=BODY):
    """The antonym confirm sentence: “Not X, but Y.”"""
    return text(f"“Not {x}, but {y}.”", size, INK, t2c={rf"\b{x}\b": WORD, rf"\b{y}\b": GOOD})


class IntroductionToAntonymsVideo(LMSScene):
    lesson_title = "Introduction to Antonyms"

    def construct(self):
        self.camera.background_color = BG

        self.lesson_intro()
        self.hook()
        self.concept()
        self.why_you_need_it()
        self.analogy()
        self.example_transparent()
        self.example_commend()
        self.example_abundant()
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

    def report_card(self):
        head = text("USABILITY TEST REPORT", SMALL, RATIO, BOLD)
        goal = text("Goal: “The checkout flow must be intuitive.”", LABEL, INK, t2c={"intuitive": WORD})
        note = text("Tester: “Users found it the exact opposite.”", LABEL, INK, t2c={"opposite": BAD})
        card = self.card(VGroup(head, goal, note).arrange(DOWN, buff=0.2, aligned_edge=LEFT), width=SAFE_W - 0.4)
        return card.move_to(UP * (CARD_TOP - card.height / 2))

    def option_example(self, word, options, key, traps):
        q = OptionQuestion(word, options, key, traps)
        q.group.to_edge(LEFT, buff=SAFE + 0.6).set_y(0.2)
        if getattr(self, "pinned", None) is not None:
            self.no_overlap(q.group, self.pinned)
        self.validator.check_in_frame(q.group)
        return q

    # ========================================= 0. LESSON INTRO ==========
    # First video of a NEW LESSON: silent trail, a one-line recap of Lesson 1
    # (its method), one line that Lesson 2 starts, the title and objectives.

    def lesson_intro(self):
        self.scene_start("S00_intro", title="Lesson Introduction")

        crumb = self.breadcrumb("English · Module 1 Vocabulary", "Lesson 2 · Antonyms", "Video 1")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        last = pill("Last lesson: Synonyms", MUTED, size=SMALL)
        method = VGroup(*[pill(t, c, size=LABEL) for t, c in [("PREDICT", STEP_COLS["PREDICT"]), ("P", WORD),
                                                             ("M", BAD), ("D", RATIO), ("T", SECOND),
                                                             ("CONFIRM", GOOD)]]).arrange(RIGHT, buff=0.25)
        fit_width(method, SAFE_W)
        VGroup(last, method).arrange(DOWN, buff=0.5).move_to(UP * 0.4)
        self.no_overlap(crumb, last, method)
        self.validator.check_in_frame(VGroup(crumb, last, method))

        n = self.narrate(
            id="intro_01",
            text="In lesson one, you learned to find the option that matches a word: predict, then check part of speech, "
                 "meaning, degree and tone, then confirm.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.play(FadeIn(last))
        self.at_word(n, "predict")
        self.play(LaggedStart(*[FadeIn(m, shift=UP * 0.1) for m in method], lag_ratio=0.15))
        self.wait_for_narration(n)

        flip = VGroup(pill("match the word", GOOD, size=LABEL), text("⇄", TITLE, MUTED),
                      pill("OPPOSE the word", BAD, size=LABEL)).arrange(RIGHT, buff=0.4)
        flip.next_to(method, DOWN, buff=0.6)
        self.no_overlap(method, flip)
        n = self.narrate(
            id="intro_02",
            text="Now we start lesson two, antonyms. Antonyms reverse the target: find the option that opposes the word. "
                 "The method stays the same; only the direction of the prediction changes.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "lesson")
        self.play(Indicate(crumb[2], color="#F48FB1", scale_factor=1.1))
        self.at_word(n, "reverse")
        self.play(FadeIn(flip, shift=UP * 0.1))
        self.at_word(n, "method")
        self.play(Circumscribe(method, color=GOOD))
        self.wait_for_narration(n)

        title = fitted_text("Introduction to Antonyms", SAFE_W, 72, INK, BOLD)
        underline = Line(LEFT, RIGHT, color=BAD, stroke_width=5).set_width(title.width * 0.6)
        VGroup(title, underline).arrange(DOWN, buff=0.2).move_to(UP * 0.2)
        goals = [
            ("Explain what an antonym is, and how exams build antonym distractors", BAD),
            ("Solve a basic antonym question with the four-step method", GOOD),
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
            text="This is the introduction to antonyms. By the end of this video, you'll be able to explain what an "
                 "antonym is and how exams build antonym distractors, and you'll solve a basic antonym question with the "
                 "four-step method.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(VGroup(last, method, flip), shift=UP * 0.3))
        self.at_word(n, "introduction")
        self.play(Write(title), run_time=1.1)
        self.play(GrowFromCenter(underline))
        self.at_word(n, "By")
        self.play(FadeOut(underline), ReplacementTransform(title, small_title), run_time=0.8)
        self.play(FadeIn(objectives[0]), FadeIn(heading))
        for row_, spoken in zip(rows, ["explain", "solve"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row_, shift=RIGHT * 0.2), run_time=0.5)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_intro")

    # ================================================= 1. HOOK ==========

    HOOK = dict(word="INTUITIVE", options=["baffling", "simple", "instinctive", "modern"], key="a",
                traps={"b": "synonym: the trap", "c": "synonym: the trap", "d": "unrelated"})

    def hook(self):
        self.scene_start("S01_hook", title="Hook")

        report = self.report_card()
        h = self.HOOK
        q = OptionQuestion(h["word"], h["options"], h["key"], h["traps"])
        opts = q.rows.copy().arrange(RIGHT, buff=0.8)
        fit_width(opts, SAFE_W)
        note = pill("two traps: one agrees with “intuitive”, one just sits near it", FOCUS, size=SMALL)
        fit_width(note, SAFE_W)
        opts.next_to(report, DOWN, buff=0.9)
        note.next_to(opts, DOWN, buff=0.7)
        self.no_overlap(report, opts, note)
        self.validator.check_in_frame(VGroup(report, opts, note))

        n = self.narrate(
            id="hook_01",
            text="Your product's checkout flow was meant to be intuitive. A usability tester writes that users found it the "
                 "exact opposite. Which word did they mean?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "intuitive")
        self.play(FadeIn(report[0]), FadeIn(report[1][0]), FadeIn(report[1][1]))
        self.at_word(n, "opposite")
        self.play(FadeIn(report[1][2], shift=UP * 0.1))
        self.at_word(n, "Which")
        self.play(Circumscribe(report[1][2], color=BAD))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_02",
            text="Baffling, simple, instinctive, or modern? Two options are traps: one agrees with intuitive, and one "
                 "simply sits near it. Choose, then we'll check.",
            voice="default",
            subtitle=True,
            pause_after=3.0,
        )
        for row, spoken in zip(opts, ["Baffling", "simple", "instinctive", "modern"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=UP * 0.15), run_time=0.35)
        self.at_word(n, "traps")
        self.play(FadeIn(note, shift=UP * 0.1))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        self.clear_stage()
        self.scene_end("S01_hook")

    # ============================================== 2. CONCEPT ==========

    def concept(self):
        self.scene_start("S02_concept", title="The Concept")

        head = pill("antonym:  opposite in meaning, in context", BAD, size=BODY)
        fit_width(head, SAFE_W)
        head.move_to(UP * (CARD_TOP - head.height / 2))
        pairs = VGroup(*[pill(f"{a}  ↔  {b}", c, size=LABEL) for a, b, c in [
            ("abundant", "scarce", GOOD), ("transparent", "opaque", WORD), ("praise", "criticise", RATIO)]])
        pairs.arrange(RIGHT, buff=0.4)
        fit_width(pairs, SAFE_W)
        pairs.next_to(head, DOWN, buff=0.5)
        fact = pill("the options almost always include a SYNONYM", BAD, size=LABEL)
        fit_width(fact, SAFE_W)
        fact.next_to(pairs, DOWN, buff=0.6)
        why = text("strongly related, just in the wrong direction", LABEL, MUTED)
        why.next_to(fact, DOWN, buff=0.3)
        self.no_overlap(head, pairs, fact, why)
        self.validator.check_in_frame(VGroup(head, pairs, fact, why))

        n = self.narrate(
            id="concept_01",
            text="An antonym is a word opposite in meaning to another, in a given context. Abundant and scarce. Transparent "
                 "and opaque. Praise and criticise.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "antonym")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        for p, spoken in zip(pairs, ["Abundant", "Transparent", "Praise"]):
            self.at_word(n, spoken)
            self.play(FadeIn(p, shift=UP * 0.1), run_time=0.4)
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_02",
            text="The single most important fact about antonym questions: the options almost always include a synonym. "
                 "When your brain is looking for strongly related to the word, the synonym feels right, because it is "
                 "strongly related, just in the wrong direction. Test-setters rely on this.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "synonym")
        self.play(FadeIn(fact, scale=1.05))
        self.at_word(n, "wrong")
        self.play(FadeIn(why, shift=UP * 0.1))
        self.at_word(n, "rely")
        self.play(Circumscribe(fact, color=BAD))
        self.wait_for_narration(n)

        # Core first, then oppose the core: intuitive → hard, not ugly or old.
        core = VGroup(pill("intuitive", WORD, size=BODY), text("= easy to understand without instructions", LABEL, INK))\
            .arrange(RIGHT, buff=0.3)
        opp = VGroup(pill("hard to understand  ✓", GOOD, size=LABEL), pill("ugly  ✗", BAD, size=LABEL),
                     pill("old  ✗", BAD, size=LABEL)).arrange(RIGHT, buff=0.4)
        block = VGroup(core, opp).arrange(DOWN, buff=0.6)
        fit_width(block, SAFE_W).move_to(UP * 0.3)
        self.validator.check_in_frame(block)
        n = self.narrate(
            id="concept_03",
            text="As with synonyms, find the core meaning first. Then predict its opposite in your own words. The answer "
                 "must be the same part of speech, and must reverse the core, not just some side feature. The opposite of "
                 "intuitive, easy to understand without instructions, is something hard to understand, not something ugly "
                 "or old.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(VGroup(head, pairs, fact, why)))
        self.at_word(n, "core", occurrence=1)
        self.play(FadeIn(core, shift=UP * 0.1))
        self.at_word(n, "hard")
        self.play(FadeIn(opp[0], shift=UP * 0.1))
        self.at_word(n, "ugly")
        self.play(FadeIn(opp[1:], shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_concept")

    # ======================================== 3. WHY YOU NEED IT ==========

    def why_you_need_it(self):
        self.scene_start("S03_why", title="Why You Need It")

        freq = pill("one of the most frequent C-CAT English question types", BAD, size=LABEL)
        uses = VGroup(pill("tone questions", SECOND, size=LABEL), pill("“the author would disagree with …”", WORD,
                                                                       size=LABEL)).arrange(RIGHT, buff=0.5)
        fit_width(uses, SAFE_W)
        VGroup(freq, uses).arrange(DOWN, buff=0.9).move_to(UP * 0.3)
        self.no_overlap(freq, uses)
        self.validator.check_in_frame(VGroup(freq, uses))

        n = self.narrate(
            id="why_01",
            text="Antonyms are one of the most frequent English question types in C-CAT. They also sharpen your reading: "
                 "tone questions, and the author would disagree with questions, both depend on recognising opposites.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "frequent")
        self.play(FadeIn(freq, shift=DOWN * 0.1))
        self.at_word(n, "tone")
        self.play(FadeIn(uses[0], shift=UP * 0.1))
        self.at_word(n, "disagree")
        self.play(FadeIn(uses[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_why")

    # ============================================== 4. ANALOGY ==========

    def analogy(self):
        self.scene_start("S04_analogy", title="The Analogy")

        centre = LEFT * 2.6 + DOWN * 0.1
        dial = Circle(radius=1.8, color=MUTED, stroke_width=3).move_to(centre)
        marks = VGroup(*[text(t, LABEL, INK, BOLD).move_to(centre + v * 2.2) for t, v in
                         [("N", UP), ("S", DOWN), ("E", RIGHT), ("W", LEFT)]])
        needle = Arrow(centre, centre + UP * 1.5, buff=0, color=GOOD, stroke_width=8,
                       max_tip_length_to_length_ratio=0.2)
        tags = VGroup(pill("synonym: same direction", GOOD, size=SMALL),
                      pill("antonym: opposite direction", BAD, size=SMALL),
                      pill("the synonym option: a strong signal, WRONG direction", FOCUS, size=SMALL))\
            .arrange(DOWN, buff=0.35, aligned_edge=LEFT)
        tags.move_to(RIGHT * 3.3 + UP * 0.2)
        fit_width(tags, 5.6)
        self.no_overlap(VGroup(dial, marks), tags)
        self.validator.check_in_frame(VGroup(dial, marks, tags))

        n = self.narrate(
            id="analogy_01",
            text="A synonym points the same way on the compass as the question word. An antonym points the opposite way.",
            voice="default",
            subtitle=True,
        )
        self.play(Create(dial), FadeIn(marks))
        self.at_word(n, "synonym")
        self.play(GrowArrow(needle), FadeIn(tags[0], shift=LEFT * 0.1))
        self.at_word(n, "antonym")
        self.play(needle.animate.rotate(PI, about_point=centre).set_color(BAD), run_time=1.2)
        self.play(FadeIn(tags[1], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_02",
            text="The synonym in the options is a needle pointing north when you were asked for south. It's a strong, clear "
                 "signal, but in the wrong direction.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "north")
        self.play(needle.animate.rotate(PI, about_point=centre).set_color(FOCUS), run_time=1.0)
        self.at_word(n, "wrong")
        self.play(FadeIn(tags[2], shift=LEFT * 0.1), Indicate(marks[1], color=BAD))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_analogy")

    # ======================================== 5-7. WORKED EXAMPLES ==========

    def example_transparent(self):
        self.scene_start("S05_ex_transparent", title="Worked Example 1")
        self.play(self.pin(self.steps_pin("antonym method", [("find the core meaning", WORD),
                                                 ("predict the OPPOSITE", STEP_COLS["PREDICT"]),
                                                 ("strike synonyms first", BAD), ("confirm: not X, but Y", GOOD)])))

        q = self.option_example("TRANSPARENT", ["clear", "opaque", "glass", "bright"], "b",
                                {"a": "synonym trap", "c": "nearby word", "d": "unrelated"})

        n = self.narrate(
            id="ex1_01",
            text="Transparent: clear, opaque, glass, or bright? Clear is the synonym trap. Glass is a nearby word, and "
                 "bright is unrelated. The opposite is opaque.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(q.word, scale=1.1))
        self.at_word(n, "clear", occurrence=1)
        self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.2) for r in q.rows], lag_ratio=0.2))
        self.at_word(n, "synonym")
        self.play(*q.strike("a")[1], self.pin_step(2))
        self.at_word(n, "nearby")
        self.play(*q.strike("c")[1], *q.strike("d")[1])
        self.at_word(n, "opposite")
        self.play(*q.confirm()[1], self.pin_step(1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_ex_transparent")

    def example_commend(self):
        self.scene_start("S06_ex_commend", title="Worked Example 2")

        q = self.option_example("COMMEND", ["praise", "command", "criticise", "comment"], "c",
                                {"a": "synonym trap", "b": "sound-alike", "d": "sound-alike"})

        n = self.narrate(
            id="ex2_01",
            text="Commend: praise, command, criticise, or comment? Praise is the synonym. Command and comment are "
                 "sound-alikes. The opposite is criticise.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(q.word, scale=1.1))
        self.at_word(n, "praise", occurrence=1)
        self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.2) for r in q.rows], lag_ratio=0.2))
        self.at_word(n, "synonym")
        self.play(*q.strike("a")[1], self.pin_step(2))
        self.at_word(n, "sound-alikes")
        self.play(*q.strike("b")[1], *q.strike("d")[1])
        self.at_word(n, "opposite")
        self.play(*q.confirm()[1], self.pin_step(1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_ex_commend")

    def example_abundant(self):
        self.scene_start("S07_ex_abundant", title="Worked Example 3")

        q = self.option_example("ABUNDANT", ["plentiful", "scarce", "useful", "heavy"], "b",
                                {"a": "synonym trap", "c": "unrelated", "d": "unrelated"})

        n = self.narrate(
            id="ex3_01",
            text="Abundant: plentiful, scarce, useful, or heavy? Plentiful is the synonym. The opposite of existing in "
                 "large quantities is scarce.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(q.word, scale=1.1))
        self.at_word(n, "plentiful", occurrence=1)
        self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.2) for r in q.rows], lag_ratio=0.2))
        self.at_word(n, "synonym")
        self.play(*q.strike("a")[1], *q.strike("c")[1], *q.strike("d")[1], self.pin_step(2))
        self.at_word(n, "existing")
        self.play(self.pin_step(0))
        self.at_word(n, "scarce", occurrence=2)
        self.play(*q.confirm()[1], self.pin_step(1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S07_ex_abundant")

    # ================================================ 8. RULES ==========

    def rules(self):
        self.scene_start("S08_rules", title="Rules")
        self.play(self.unpin())

        rules = VGroup(*[VGroup(pill(str(i + 1), c, size=SMALL), fitted_text(s_, SAFE_W - 2.2, BODY, INK))
                         .arrange(RIGHT, buff=0.3) for i, (s_, c) in enumerate([
                             ("Find the core meaning, then predict its opposite", WORD),
                             ("Expect a synonym in the options: it's a trap", BAD),
                             ("Match the part of speech", SECOND),
                             ("Reverse the core meaning, not a side feature", GOOD)])])
        rules.arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        board = self.card(rules).move_to(UP * 0.3)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="rules_01",
            text="Four rules. First, find the core meaning, then predict its opposite. Second, expect a synonym in the "
                 "options: it's a trap. Third, match the part of speech. And fourth, reverse the core meaning, not a side "
                 "feature.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(board[0]))
        for r, spoken in zip(rules, ["First", "Second", "Third", "fourth"]):
            self.at_word(n, spoken)
            self.play(FadeIn(r, shift=RIGHT * 0.2), run_time=0.45)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S08_rules")

    # ============================================== 9. PROCESS ==========

    def process(self):
        self.scene_start("S09_process", title="The Process")

        strip = process_strip(BODY)
        fit_width(strip, SAFE_W)
        strip.move_to(UP * (CARD_TOP - strip.height / 2))
        details = VGroup(*[VGroup(pill(name, col, size=SMALL), fitted_text(s_, SAFE_W - 3.4, LABEL, INK))
                           .arrange(RIGHT, buff=0.3) for (name, col), s_ in zip(STEP_COLS.items(), [
                               "the word, its part of speech, any sentence",
                               "state the OPPOSITE in your own words",
                               "synonyms first, then sound-alikes, nearby words, wrong part of speech",
                               "a contrast sentence:  “Not X, but Y.”"])])
        details.arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        board = self.card(details)
        board.next_to(strip, DOWN, buff=0.5)
        self.no_overlap(strip, board)
        self.validator.check_in_frame(VGroup(strip, board))

        n = self.narrate(
            id="process_01",
            text="The process. Read: note the word, its part of speech, and any sentence. Predict: state the opposite in "
                 "your own words. Eliminate: remove synonyms first, then sound-alikes, nearby words and wrong parts of "
                 "speech. And confirm: put the answer into a contrast sentence, not X, but Y.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(strip, shift=DOWN * 0.2), FadeIn(board[0]))
        for d, name, spoken in zip(details, STEP_COLS, ["Read", "Predict", "Eliminate", "confirm"]):
            self.at_word(n, spoken)
            self.play(Indicate(step_chip(strip, name)), FadeIn(d, shift=RIGHT * 0.2), run_time=0.5)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S09_process")

    # ========================================== 10. HOOK, SOLVED ==========

    def hook_solved(self):
        self.scene_start("S10_hook_solved", title="Hook, Solved")

        h = self.HOOK
        report = self.report_card()
        q = OptionQuestion(h["word"], h["options"], h["key"], h["traps"], word_size=BODY)
        q.group.next_to(report, DOWN, buff=0.45).to_edge(LEFT, buff=SAFE + 0.6)
        predict = pill("predict: hard to understand, confusing", STEP_COLS["PREDICT"], size=SMALL)
        predict.to_edge(RIGHT, buff=SAFE + 0.2).align_to(q.word, UP)
        conf = contrast("intuitive", "baffling")
        verdict = pill("users couldn't figure out the flow at all", GOOD, size=SMALL)
        bottom = VGroup(conf, verdict).arrange(RIGHT, buff=0.5)
        fit_width(bottom, SAFE_W)
        bottom.to_edge(DOWN, buff=SAFE + 0.35)
        self.no_overlap(report, q.group, bottom)
        self.validator.check_in_frame(VGroup(report, q.group, predict, bottom))

        n = self.narrate(
            id="solved_01",
            text="Let's solve the hook. Read: intuitive is an adjective, meaning easy to use without instructions. "
                 "Predict: hard to understand, confusing.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(report), FadeIn(q.word), FadeIn(q.rows))
        self.at_word(n, "Read")
        self.play(Indicate(q.word, color=WORD, scale_factor=1.1))
        self.at_word(n, "Predict")
        self.play(FadeIn(predict, shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_02",
            text="Eliminate. Simple and instinctive are synonyms: the traps. Modern is unrelated.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Eliminate")
        self.play(Indicate(q.rows, color=BAD, scale_factor=1.02))
        self.at_word(n, "Simple")
        self.play(*q.strike("b")[1], *q.strike("c")[1])
        self.at_word(n, "Modern")
        self.play(*q.strike("d")[1])
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_03",
            text="Confirm: not intuitive, but baffling. The answer is baffling. The report is saying users couldn't figure "
                 "out the flow at all.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Confirm")
        self.play(FadeIn(conf, shift=UP * 0.1))
        self.at_word(n, "answer")
        self.play(*q.confirm()[1])
        self.at_word(n, "report")
        self.play(FadeIn(verdict, shift=LEFT * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S10_hook_solved")

    # ========================================== 11. EXAM PATTERNS ==========

    def exam_patterns(self):
        self.scene_start("S11_patterns", title="Exam Patterns and Solving Models")

        table = self.table_rows(["Pattern", "Solving model"], [
            ["Single word, four options", "predict the opposite → strike synonyms → confirm “not X but Y”"],
            ["Word in a sentence", "the opposite of the meaning in that sentence (Video 3)"],
            ["Prefix options (unfair, disfair …)", "apply the prefix rules (Video 4)"],
        ], [4.6, 7.2], size=LABEL)
        board = self.card(table, width=SAFE_W - 0.2).move_to(UP * 0.4)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="patterns_01",
            text="Three exam patterns. A single word with four options: predict the opposite, strike the synonyms, and "
                 "confirm with not X but Y. A word in a sentence: find the opposite of the meaning in that sentence, "
                 "which is video three. And prefix options, like unfair and disfair: apply the prefix rules from video "
                 "four.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(board[0]), FadeIn(table[0]))
        for row, spoken in zip(table[1:], ["single", "sentence", "prefix"]):
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
            (self.verdict_card(False, "Choosing the synonym", card_w),
             self.verdict_card(True, "Strike synonyms first", card_w)),
            (self.verdict_card(False, "Choosing a sound-alike: commend → command", card_w),
             self.verdict_card(True, "Match meaning, not sound", card_w)),
            (self.verdict_card(False, "Opposing a side feature", card_w),
             self.verdict_card(True, "Reverse the CORE meaning", card_w)),
        ]
        for (wrong, right), yy in zip(pairs, [1.6, 0.05, -1.5]):
            wrong.move_to(LEFT_ZONE + UP * yy)
            right.move_to(RIGHT_ZONE + UP * yy)
        header = pill("3 mistakes", BAD, size=LABEL).move_to(UP * (CARD_TOP - 0.3))
        self.validator.check_in_frame(VGroup(header, *[c for p in pairs for c in p]))

        n = self.narrate(
            id="mistakes_01",
            text="Three common mistakes. The first is choosing the synonym. The second is choosing a sound-alike, like "
                 "command for commend. The third is opposing a side feature instead of the core meaning.",
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
        ("LUCID", ["clear", "obscure", "lucky", "bright"], "b",
         {"a": "synonym", "c": "sound-alike", "d": "nearby word"}),
        ("DILIGENT", ["hard-working", "intelligent", "indolent", "quick"], "c",
         {"a": "synonym", "b": "sound-alike", "d": "unrelated"}),
        ("OPTIMISTIC", ["hopeful", "realistic", "optional", "pessimistic"], "d",
         {"a": "synonym", "b": "in between, not opposite", "c": "sound-alike"}),
    ]

    def practice(self):
        self.scene_start("S13_practice", title="Practice Questions")

        head = pill("Choose the OPPOSITE", BAD, size=LABEL)
        lines = VGroup(*[VGroup(pill(str(i + 1), FOCUS, size=SMALL), pill(w, WORD, size=LABEL),
                                text("   ".join(f"({l}) {o}" for l, o in zip("abcd", opts)), LABEL, INK))
                         .arrange(RIGHT, buff=0.35) for i, (w, opts, *_r) in enumerate(self.PRACTICE)])
        lines.arrange(DOWN, buff=0.5, aligned_edge=LEFT)
        board = self.card(VGroup(head, lines).arrange(DOWN, buff=0.5, aligned_edge=LEFT), color=FOCUS)
        fit_width(board, SAFE_W)
        board.move_to(UP * 0.4)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="practice_01",
            text="Your turn: choose the opposite. One: lucid. Clear, obscure, lucky, or bright? Two: diligent. "
                 "Hard-working, intelligent, indolent, or quick? Three: optimistic. Hopeful, realistic, optional, or "
                 "pessimistic?",
            voice="default",
            subtitle=True,
            pause_after=10.0,
        )
        self.play(FadeIn(board[0]), FadeIn(head))
        for ln, (spoken, first_option) in zip(lines, [("lucid", "Clear"), ("diligent", "Hard-working"),
                                                     ("optimistic", "Hopeful")]):
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

        notes = ["(a) clear: synonym;  (c) lucky: sound-alike", "indolent = lazy;  (a) hard-working: synonym",
                 "(b) realistic sits between the two"]
        rows = VGroup()
        for (w, opts, key, traps), note in zip(self.PRACTICE, notes):
            OptionQuestion(w, opts, key, traps)            # validates key / traps
            rows.add(VGroup(pill(w, WORD, size=LABEL), text("↔", LABEL, MUTED),
                            pill(f"({key}) {opts['abcd'.index(key)]}", GOOD, size=LABEL),
                            text(note, SMALL, INK)).arrange(RIGHT, buff=0.3))
        rows.arrange(DOWN, buff=0.45, aligned_edge=LEFT)
        fit_width(rows, SAFE_W).move_to(UP * 0.3)
        self.validator.check_in_frame(rows)

        n = self.narrate(
            id="answers_01",
            text="One: obscure. Clear is the synonym, and lucky is a sound-alike. Two: indolent, which means lazy. "
                 "Hard-working is the synonym. Three: pessimistic. Realistic sits between the two; it isn't the "
                 "opposite.",
            voice="default",
            subtitle=True,
        )
        for r, (spoken, reason) in zip(rows, [("obscure", "Clear"), ("indolent", "Hard-working"),
                                             ("pessimistic", "Realistic")]):
            self.at_word(n, spoken)
            self.play(FadeIn(r[:3], shift=RIGHT * 0.2), run_time=0.5)
            self.at_word(n, reason)
            self.play(FadeIn(r[3], shift=LEFT * 0.1), run_time=0.4)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S14_answers")

    # ================================================ 15. RECAP ==========

    def recap(self):
        self.scene_start("S15_recap", title="Recap Card")

        card, table = self.recap_card("Recap Card: Video 1", [
            ["Antonym", "opposite in meaning, in context"],
            ["Biggest trap", "the synonym in the options"],
            ["Method", "predict the opposite → strike synonyms → confirm “not X but Y”"],
            ["Must match", "part of speech; oppose the core meaning"],
        ])
        card.move_to(UP * 0.2)
        self.validator.check_in_frame(card)

        n = self.narrate(
            id="recap_01",
            text="To recap. An antonym is opposite in meaning, in context. The biggest trap is the synonym in the options. "
                 "The method: predict the opposite, strike the synonyms, and confirm with not X but Y. And the answer must "
                 "match the part of speech, and oppose the core meaning.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(card[0]), FadeIn(table[0]))
        for row, spoken in zip(table[1:], ["antonym", "biggest", "method", "match"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.45)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S15_recap")

    # ================================================= 16. NEXT ==========

    def next_video(self):
        self.scene_start("S16_next", title="Next")

        scale = VGroup(pill("cold", WORD, size=BODY), pill("cool", "#90CAF9", size=BODY), pill("warm", RATIO, size=BODY),
                       pill("hot", BAD, size=BODY)).arrange(RIGHT, buff=0.5)
        not_hot = pill("“not hot” ≠ “cold”", FOCUS, size=BODY)
        nxt = pill("Next:  Types of Antonyms", FOCUS, size=LABEL)
        VGroup(scale, not_hot, nxt).arrange(DOWN, buff=0.7).move_to(UP * 0.2)
        self.no_overlap(scale, not_hot, nxt)
        self.validator.check_in_frame(VGroup(scale, not_hot, nxt))

        n = self.narrate(
            id="next_01",
            text="Not all opposites work the same way. Video two shows three types, and why not hot doesn't mean cold.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "opposites")
        self.play(LaggedStart(*[FadeIn(c, shift=UP * 0.1) for c in scale], lag_ratio=0.2))
        self.at_word(n, "Video")
        self.play(FadeIn(nxt, scale=1.05))
        self.at_word(n, "hot")
        self.play(FadeIn(not_hot, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S16_next")

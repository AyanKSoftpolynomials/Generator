"""
animation.py for the LMS video generator.

Course : C-CAT - Section A - English
Module : Module 1 - Vocabulary
Lesson : Lesson 2 - Antonyms
Video  : 07 - Antonym Question-Solving Techniques (Video 7 of 7)

Source script:
  C:\\Users\\User\\Downloads\\C-CAT_SectionA_Module1_English\\English\\Module 1 - Vocabulary\\
  Lesson 2 - Antonyms\\07 - Antonym Question-Solving Techniques.pdf

Built on the golden-reference pattern:
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``;
  * layouts stacked with next_to and guarded with ``no_overlap``; nothing is
    ever animated onto or into another box.

The five checks live in CHECKS (S, P, T, M, D) and the 30-second budget in TIMELINE; the S-P-T-M-D card stays pinned top-right through the worked examples and Hook, Solved, and each check lights up as it is used.
Answers that have a Video 6 shelf pair are asserted against OPPOSITE.
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

CHECKS = [("S", "Synonym strike", BAD), ("P", "Part of speech", WORD), ("T", "Type", RATIO),
          ("M", "Meaning in context", SECOND), ("D", "Decode", FOCUS)]
CHECK_COL = {k: c for k, _, c in CHECKS}

# Time budget from the script (seconds): (start, end, step).
TIMELINE = [(0, 5, "read + predict the opposite"), (5, 15, "strike synonyms, then wrong parts of speech"),
            (15, 25, "type, context and decode for the survivors"), (25, 30, "confirm “not X but Y”")]

# Opposites this video relies on (from the Video 6 shelves).
OPPOSITE = {"ephemeral": "permanent", "augment": "diminish", "adamant": "yielding", "explicit": "vague"}


def gate(letter, name, color, width=2.2, height=3.4):
    """One gate of the sorting machine: an arch with the check letter and its name."""
    arch = VGroup(Line(DOWN * height / 2, UP * height / 2, color=color, stroke_width=6).shift(LEFT * width / 2),
                  Line(DOWN * height / 2, UP * height / 2, color=color, stroke_width=6).shift(RIGHT * width / 2),
                  Line(LEFT * width / 2 + UP * height / 2, RIGHT * width / 2 + UP * height / 2, color=color,
                       stroke_width=6))
    tag = text(letter, TITLE, color, BOLD).next_to(arch, UP, buff=0.15)
    name_ = text(name, SMALL, color).next_to(arch, DOWN, buff=0.15)
    return VGroup(arch, tag, name_)


class AntonymTechniquesVideo(LMSScene):
    lesson_title = "Antonym Question-Solving Techniques"

    def construct(self):
        self.camera.background_color = BG

        self.lesson_intro()
        self.hook()
        self.concept()
        self.why_you_need_it()
        self.analogy()
        self.example_augment()
        self.example_conciliatory()
        self.example_invaluable()
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

    def check_pin(self):
        return self.steps_pin("S-P-T-M-D", [(f"{k}  {name}", c) for k, name, c in CHECKS])

    def light(self, letter):
        """Animation: light the row of the pinned S-P-T-M-D panel for this check."""
        return self.pin_step([k for k, _, _ in CHECKS].index(letter), color=CHECK_COL[letter])

    def slide_card(self, fill=None):
        head = VGroup(text("MARKETING SLIDE", SMALL, RATIO, BOLD), pill("0:30", BAD, size=SMALL)).arrange(RIGHT, buff=0.5)
        line = "“Social media trends are ephemeral.”" if not fill else f"“Trends are not ephemeral but {fill}.”"
        body = text(line, BODY, INK, t2c={"ephemeral": WORD, fill or "ephemeral": GOOD if fill else WORD})
        cx, w = self.free_area()
        card = self.card(VGroup(head, fit_width(body, w - 1.4)).arrange(DOWN, buff=0.2, aligned_edge=LEFT),
                         width=min(w - 0.2, SAFE_W - 0.4))
        return card.move_to(RIGHT * cx + UP * (CARD_TOP - card.height / 2))

    def left_question(self, word, options, key, traps, above=None, below=None):
        """Question at the left, beside the pinned panel; optional line above / note below."""
        q = OptionQuestion(word, options, key, traps, word_size=BODY if (above or below) else TITLE)
        parts = [m for m in (above, q.group, below) if m is not None]
        block = VGroup(*parts).arrange(DOWN, buff=0.45, aligned_edge=LEFT)
        block.to_edge(LEFT, buff=SAFE + 0.6).set_y(0.2)
        self.no_overlap(*parts)
        self.no_overlap(block, self.pinned)
        self.validator.check_in_frame(block)
        return q

    # ========================================= 0. LESSON INTRO ==========

    def lesson_intro(self):
        self.scene_start("S00_intro", title="Lesson Introduction")

        crumb = self.breadcrumb("English · Module 1 Vocabulary", "Lesson 2 · Antonyms", "Video 7")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        ideas = VGroup(*[pill(t, c, size=LABEL) for t, c in [("synonym traps", BAD), ("types", RATIO),
                                                            ("context", SECOND), ("prefixes", FOCUS),
                                                            ("false opposites", WORD), ("shelves", GOOD)]])
        ideas.arrange(RIGHT, buff=0.25)
        fit_width(ideas, SAFE_W)
        one = pill("today: one ordered method", FOCUS, size=LABEL)
        VGroup(ideas, one).arrange(DOWN, buff=0.8).move_to(DOWN * 0.1)
        self.no_overlap(crumb, ideas, one)
        self.validator.check_in_frame(VGroup(crumb, ideas, one))

        n = self.narrate(
            id="intro_01",
            text="Videos one to six each gave you one defence: synonym traps, types, context, prefixes, false opposites "
                 "and shelves. Today they become one ordered method.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.at_word(n, "defence")
        self.play(LaggedStart(*[FadeIn(i, shift=UP * 0.1) for i in ideas], lag_ratio=0.3), run_time=3.0)
        self.at_word(n, "Today")
        self.play(FadeIn(one, shift=UP * 0.1))
        self.wait_for_narration(n)

        title = fitted_text("Antonym Question-Solving Techniques", SAFE_W, 64, INK, BOLD)
        underline = Line(LEFT, RIGHT, color=BAD, stroke_width=5).set_width(title.width * 0.6)
        VGroup(title, underline).arrange(DOWN, buff=0.2).move_to(UP * 0.2)
        n = self.narrate(
            id="intro_02",
            text="This is the last video of lesson two: antonym question-solving techniques.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(VGroup(ideas, one), shift=UP * 0.3))
        self.at_word(n, "antonym")
        self.play(Write(title), run_time=1.1)
        self.play(GrowFromCenter(underline))
        self.wait_for_narration(n)

        goals = [
            ("Solve any antonym question with a fixed elimination order", BAD),
            ("Build the reflex that catches the synonym trap every time", GOOD),
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
            text="By the end of this video, you'll solve any antonym question with a fixed elimination order, and build "
                 "the reflex that catches the synonym trap every time.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(underline), ReplacementTransform(title, small_title), run_time=0.8)
        self.play(FadeIn(objectives[0]), FadeIn(heading))
        for row_, spoken in zip(rows, ["solve", "reflex"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row_, shift=RIGHT * 0.2), run_time=0.5)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_intro")

    # ================================================= 1. HOOK ==========

    HOOK = dict(word="EPHEMERAL", options=["permanent", "brief", "popular", "digital"], key="a",
                traps={"b": "S: synonym (the trap)", "c": "M: different topic", "d": "M: different topic"})

    def hook(self):
        self.scene_start("S01_hook", title="Hook")

        h = self.HOOK
        assert h["options"]["abcd".index(h["key"])] == OPPOSITE["ephemeral"]
        slide = self.slide_card()
        q = OptionQuestion(h["word"], h["options"], h["key"], h["traps"])
        opts = q.rows.copy().arrange(RIGHT, buff=0.8)
        fit_width(opts, SAFE_W)
        ask = pill("your manager wants a slide that argues the OPPOSITE", BAD, size=LABEL)
        ask.next_to(slide, DOWN, buff=0.6)
        opts.next_to(ask, DOWN, buff=0.6)
        self.no_overlap(slide, ask, opts)
        self.validator.check_in_frame(VGroup(slide, ask, opts))

        n = self.narrate(
            id="hook_01",
            text="A marketing slide says: social media trends are ephemeral. Your manager wants a slide that argues the "
                 "opposite. You have thirty seconds.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(slide, shift=DOWN * 0.2))
        self.at_word(n, "opposite")
        self.play(FadeIn(ask, shift=UP * 0.1))
        self.at_word(n, "seconds")
        self.play(Indicate(slide[1][0][1], color=BAD, scale_factor=1.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_02",
            text="The opposite of ephemeral is: permanent, brief, popular, or digital?",
            voice="default",
            subtitle=True,
            pause_after=3.0,
        )
        for row, spoken in zip(opts, ["permanent", "brief", "popular", "digital"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=UP * 0.15), run_time=0.35)
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        self.clear_stage()
        self.scene_end("S01_hook")

    # ============================================== 2. CONCEPT ==========

    def concept(self):
        self.scene_start("S02_concept", title="The Concept")

        head = pill("five kinds of distractor  →  five checks:  S-P-T-M-D", FOCUS, size=LABEL)
        fit_width(head, SAFE_W)
        head.move_to(UP * (CARD_TOP - head.height / 2))
        rows = VGroup(*[VGroup(pill(k, c, size=BODY), text(name, LABEL, c, BOLD),
                               fitted_text(q, 6.4, LABEL, INK)).arrange(RIGHT, buff=0.35)
                        for (k, name, c), q in zip(CHECKS, [
                            "remove any option that means the SAME: do this first",
                            "the answer must match",
                            "gradable, complementary, relational? no midpoints, no same-side words",
                            "in a sentence: oppose the meaning used there",
                            "prefixed or unfamiliar: decode the true meaning, or use roots"])])
        rows.arrange(DOWN, buff=0.28, aligned_edge=LEFT)
        fit_within(rows, SAFE_W, SAFE_H - head.height - 1.6)
        rows.next_to(head, DOWN, buff=0.4)
        self.no_overlap(head, rows)
        self.validator.check_in_frame(VGroup(head, rows))

        n = self.narrate(
            id="concept_01",
            text="Antonym distractors are built in five predictable ways, so the checks come in five: S, P, T, M, D.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_02",
            text="S is the synonym strike: remove any option that means the same. Do this first; it's the most common "
                 "trap. P is part of speech: the answer must match. T is type: gradable, complementary or relational? "
                 "Reject midpoints and same-side words.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "synonym")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2), run_time=0.45)
        self.at_word(n, "first")
        self.play(Indicate(rows[0][0], color=BAD, scale_factor=1.3))
        self.at_word(n, "part")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2), run_time=0.45)
        self.at_word(n, "type")
        self.play(FadeIn(rows[2], shift=RIGHT * 0.2), run_time=0.45)
        self.at_word(n, "Reject")
        self.play(Indicate(rows[2][2], color=RATIO, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_03",
            text="M is meaning in context: if there's a sentence, oppose the meaning used there. And D is decode: for "
                 "prefixed or unfamiliar words, decode the true meaning, like inflammable and disinterested, or use roots.",
            voice="default",
            subtitle=True,
        )
        traps = self.caption("inflammable = burns easily   ·   disinterested = impartial", FOCUS)
        self.at_word(n, "meaning", occurrence=1)
        self.play(FadeIn(rows[3], shift=RIGHT * 0.2), run_time=0.45)
        self.at_word(n, "decode", occurrence=1)
        self.play(FadeIn(rows[4], shift=RIGHT * 0.2), run_time=0.45)
        self.at_word(n, "inflammable")
        self.play(FadeIn(traps, shift=UP * 0.2))
        self.wait_for_narration(n)

        frame_ = VGroup(pill("PREDICT before reading the options", STEP_COLS["PREDICT"], size=BODY),
                        pill("always CONFIRM with “not X but Y”", GOOD, size=BODY),
                        text("reads like a contradiction?  you have the antonym", LABEL, INK))\
            .arrange(DOWN, buff=0.5)
        fit_width(frame_, SAFE_W).move_to(UP * 0.3)
        self.validator.check_in_frame(frame_)
        n = self.narrate(
            id="concept_04",
            text="Predict before reading the options, and always confirm with not X but Y. If the sentence reads like a "
                 "contradiction, you have the antonym.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(VGroup(head, rows, traps)))
        self.at_word(n, "Predict")
        self.play(FadeIn(frame_[0], scale=1.05))
        self.at_word(n, "confirm")
        self.play(FadeIn(frame_[1], shift=UP * 0.1))
        self.at_word(n, "contradiction")
        self.play(FadeIn(frame_[2], shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_concept")

    # ======================================== 3. WHY YOU NEED IT ==========

    def why_you_need_it(self):
        self.scene_start("S03_why", title="Why You Need It")

        cost = pill("the synonym trap: more lost antonym marks than any other error", BAD, size=LABEL)
        fix = pill("fixed first step:  STRIKE SYNONYMS  →  trap removed for good", GOOD, size=LABEL)
        time_ = pill("≈ 30 s per antonym question  →  time banked for the rest of Section A", RATIO, size=LABEL)
        group = VGroup(cost, fix, time_).arrange(DOWN, buff=0.7)
        fit_width(group, SAFE_W).move_to(UP * 0.3)
        self.no_overlap(cost, fix, time_)
        self.validator.check_in_frame(group)

        n = self.narrate(
            id="why_01",
            text="The synonym trap costs more antonym marks than any other error. A fixed first step, strike synonyms, "
                 "removes it permanently. And at about thirty seconds per antonym question, you bank time for the rest of "
                 "section A.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "trap")
        self.play(FadeIn(cost, shift=DOWN * 0.1))
        self.at_word(n, "fixed")
        self.play(FadeIn(fix, shift=UP * 0.1))
        self.at_word(n, "thirty")
        self.play(FadeIn(time_, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_why")

    # ============================================== 4. ANALOGY ==========

    def analogy(self):
        self.scene_start("S04_analogy", title="The Analogy")

        gates = VGroup(*[gate(k, name.split()[0], c) for k, name, c in CHECKS]).arrange(RIGHT, buff=0.45)
        fit_width(gates, SAFE_W - 3.6)
        gates.move_to(RIGHT * 0.6 + DOWN * 0.1)
        tray = text("kept", LABEL, GOOD, BOLD).next_to(gates[-1][0], RIGHT, buff=0.3)
        # Coins: the gate (index) that catches each one, or None if it passes all five.
        coins_ = [("synonym", 0), ("noun", 1), ("midpoint", 2), ("other sense", 3), ("prefix trap", 4), ("antonym", None)]
        coins = VGroup(*[pill(t, GOOD if stop is None else MUTED, size=SMALL) for t, stop in coins_])
        coins.arrange(DOWN, buff=0.12)
        arch = gates[0][0]
        fit_within(coins, arch.width - 0.3, arch.height - 0.4)     # every coin fits inside a gate
        coins.next_to(gates, LEFT, buff=0.3).set_y(arch.get_y())
        self.no_overlap(coins, tray)
        self.validator.check_in_frame(VGroup(coins, gates, tray))

        n = self.narrate(
            id="analogy_01",
            text="Think of a coin-sorting machine with five gates. Each gate is sized to catch one kind of wrong coin.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "five")
        self.play(LaggedStart(*[FadeIn(g, shift=UP * 0.2) for g in gates], lag_ratio=0.2))
        self.at_word(n, "catch")
        self.play(FadeIn(coins, shift=RIGHT * 0.1), FadeIn(tray))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_02",
            text="The synonym gate comes first, because most wrong coins are that size.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "synonym")
        self.play(Indicate(gates[0][1], color=BAD, scale_factor=1.3))
        for chip, (label, stop) in zip(coins, coins_):
            target_x = gates[stop][0].get_center()[0] if stop is not None \
                else gates[-1][0].get_center()[0]
            self.play(chip.animate.set_x(target_x), run_time=0.45)
            if stop is not None:
                self.play(chip.animate.set_opacity(0.3), Flash(chip.get_center(), color=CHECKS[stop][2],
                                                               flash_radius=0.4), run_time=0.3)
            else:
                self.play(Indicate(chip, color=GOOD), Indicate(tray, color=GOOD), run_time=0.5)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_analogy")

    # ======================================== 5-7. WORKED EXAMPLES ==========

    def example_augment(self):
        self.scene_start("S05_ex_augment", title="Worked Example 1")
        self.play(self.pin(self.check_pin()))

        opts = ["increase", "diminish", "argue", "augur"]
        assert opts[1] == OPPOSITE["augment"]
        q = self.left_question("AUGMENT", opts, "b",
                               {"a": "S: synonym", "c": "M: sound-alike", "d": "M: sound-alike"})

        n = self.narrate(
            id="ex1_01",
            text="Augment: increase, diminish, argue, or augur? S: increase is a synonym, so it's out. M: argue and augur "
                 "are sound-alikes. The answer is diminish.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(q.word, scale=1.1))
        self.at_word(n, "increase", occurrence=1)
        self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.2) for r in q.rows], lag_ratio=0.2))
        self.at_word(n, "S")
        self.play(self.light("S"), *q.strike("a")[1])
        self.at_word(n, "M")
        self.play(self.light("M"), *q.strike("c")[1], *q.strike("d")[1])
        self.at_word(n, "answer")
        self.play(*q.confirm()[1])
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_ex_augment")

    def example_conciliatory(self):
        self.scene_start("S06_ex_conciliatory", title="Worked Example 2")

        cx, w = self.free_area()
        sent = text("“The speaker's tone was conciliatory.”", BODY, INK, t2c={"conciliatory": WORD})
        fit_width(sent, w - 1.4)
        q = self.left_question("CONCILIATORY", ["friendly", "hostile", "calm", "soft"], "b",
                               {"a": "S: same side", "c": "S: same side", "d": "S: same side"}, above=sent)

        n = self.narrate(
            id="ex2_01",
            text="The speaker's tone was conciliatory. Friendly, hostile, calm, or soft? S: friendly, calm and soft all "
                 "lean the same way. The answer is hostile.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(sent, shift=DOWN * 0.1), FadeIn(q.word, scale=1.1))
        self.at_word(n, "Friendly", occurrence=1)
        self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.2) for r in q.rows], lag_ratio=0.2))
        self.at_word(n, "S")
        self.play(self.light("S"), *q.strike("a")[1], *q.strike("c")[1], *q.strike("d")[1])
        self.at_word(n, "answer")
        self.play(*q.confirm()[1])
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_ex_conciliatory")

    def example_invaluable(self):
        self.scene_start("S07_ex_invaluable", title="Worked Example 3")

        decoded = pill("decode:  invaluable = VERY valuable", FOCUS, size=SMALL)
        q = self.left_question("INVALUABLE", ["priceless", "useless", "valuable", "costly"], "b",
                               {"a": "S: synonym", "c": "S: synonym", "d": "about price, not worth"}, below=decoded)

        n = self.narrate(
            id="ex3_01",
            text="Invaluable: priceless, useless, valuable, or costly? D: decode first. Invaluable means very valuable. "
                 "S: so priceless and valuable are both out. Costly is about price, not worth. The answer is useless.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(q.word, scale=1.1))
        self.at_word(n, "priceless", occurrence=1)
        self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.2) for r in q.rows], lag_ratio=0.2))
        self.at_word(n, "D")
        self.play(self.light("D"))
        self.at_word(n, "means")
        self.play(FadeIn(decoded, shift=UP * 0.1))
        self.at_word(n, "S")
        self.play(self.light("S"), *q.strike("a")[1], *q.strike("c")[1])
        self.at_word(n, "Costly", occurrence=2)
        self.play(*q.strike("d")[1])
        self.at_word(n, "answer")
        self.play(*q.confirm()[1])
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S07_ex_invaluable")

    # ================================================ 8. RULES ==========

    def rules(self):
        self.scene_start("S08_rules", title="Rules")
        self.play(self.unpin())

        strip = self.method_strip()
        fit_width(strip, SAFE_W)
        strip.move_to(UP * (CARD_TOP - strip.height / 2))
        table = self.table_rows(["Check", "Catches"], [
            ["S", "synonyms of the word"],
            ["P", "wrong part of speech"],
            ["T", "midpoints, same-side roles"],
            ["M", "opposites of other meanings"],
            ["D", "prefix traps, unknown words"],
        ], [2.0, 9.0], size=LABEL)
        for row, (_, _, c) in zip(table[1:], CHECKS):
            row[0].set_color(c)
        board = self.card(table, width=SAFE_W - 0.2)
        fit_height(board, SAFE_H - strip.height - 1.4)
        board.next_to(strip, DOWN, buff=0.4)
        self.no_overlap(strip, board)
        self.validator.check_in_frame(VGroup(strip, board))

        n = self.narrate(
            id="rules_01",
            text="The full method: predict, then S, P, T, M, D, then confirm with not X but Y. S catches synonyms of the "
                 "word. P catches the wrong part of speech. T catches midpoints and same-side roles. M catches opposites "
                 "of other meanings. And D catches prefix traps and unknown words.",
            voice="default",
            subtitle=True,
        )
        self.play(LaggedStart(*[FadeIn(c, shift=RIGHT * 0.1) for c in strip], lag_ratio=0.1))
        self.play(FadeIn(board[0]), FadeIn(table[0]))
        for row, spoken in zip(table[1:], ["synonyms", "wrong", "midpoints", "opposites", "prefix"]):
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
                         for t in [0, 5, 15, 25, 30]])
        labels = VGroup(*[fitted_text(lab, 7.0, LABEL, c) for (_, _, lab), c in zip(TIMELINE, cols)])
        rows = VGroup(*[VGroup(pill(f"{s_}–{e} s", c, size=SMALL), lab).arrange(RIGHT, buff=0.3)
                        for (s_, e, _), c, lab in zip(TIMELINE, cols, labels)]).arrange(DOWN, buff=0.22,
                                                                                        aligned_edge=LEFT)
        rows.next_to(ticks, DOWN, buff=0.5)
        never = pill("guess only after at least one elimination", FOCUS, size=SMALL)
        never.next_to(rows, DOWN, buff=0.4)
        assert TIMELINE[0][0] == 0 and TIMELINE[-1][1] == 30 and all(a[1] == b[0] for a, b in zip(TIMELINE, TIMELINE[1:]))
        self.no_overlap(VGroup(segs, ticks), rows, never)
        self.validator.check_in_frame(VGroup(segs, ticks, rows, never))

        n = self.narrate(
            id="process_01",
            text="Here's the thirty-second budget. From zero to five seconds, read, and predict the opposite. From five to "
                 "fifteen, strike synonyms, then wrong parts of speech. From fifteen to twenty-five, run type, context "
                 "and decode on the survivors. From twenty-five to thirty, confirm with not X but Y.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(ticks))
        for seg, row, (spoken, occ) in zip(segs, rows, [("zero", 1), ("five", 2), ("fifteen", 2),
                                                         ("twenty-five", 2)]):
            self.at_word(n, spoken, occurrence=occ)
            self.play(GrowFromEdge(seg, LEFT), FadeIn(row, shift=RIGHT * 0.2), run_time=0.5)
        self.wait_for_narration(n)

        n = self.narrate(
            id="process_02",
            text="And guess only after at least one elimination.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "guess")
        self.play(FadeIn(never, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S09_process")

    # ========================================== 10. HOOK, SOLVED ==========

    def hook_solved(self):
        self.scene_start("S10_hook_solved", title="Hook, Solved")
        self.play(self.pin(self.check_pin()))

        h = self.HOOK
        slide = self.slide_card()
        q = OptionQuestion(h["word"], h["options"], h["key"], h["traps"], word_size=BODY)
        q.group.next_to(slide, DOWN, buff=0.45).to_edge(LEFT, buff=SAFE + 0.6)
        meaning = text("= lasting a very short time", SMALL, WORD).next_to(q.word, RIGHT, buff=0.3)
        predict = pill("predict: lasting, permanent", STEP_COLS["PREDICT"], size=SMALL)
        predict.next_to(q.word, RIGHT, buff=0.3)
        filled = self.slide_card(fill=OPPOSITE["ephemeral"])
        verdict = pill("it contradicts  →  it's the antonym", GOOD, size=LABEL)
        verdict.to_edge(DOWN, buff=SAFE + 0.4)
        self.no_overlap(slide, q.group, verdict)
        self.no_overlap(slide, self.pinned)
        self.no_overlap(q.group, predict, self.pinned)
        self.no_overlap(meaning, self.pinned)
        self.validator.check_in_frame(VGroup(slide, q.group, predict, meaning, verdict))

        n = self.narrate(
            id="solved_01",
            text="Let's solve the hook. Read: ephemeral means lasting a very short time. Predict: lasting, permanent.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(slide), FadeIn(q.word), FadeIn(q.rows))
        self.at_word(n, "Read")
        self.play(Indicate(q.word, color=WORD, scale_factor=1.1), FadeIn(meaning, shift=LEFT * 0.1))
        self.at_word(n, "Predict")
        self.play(FadeOut(meaning), run_time=0.3)
        self.play(FadeIn(predict, shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_02",
            text="Eliminate. S: brief is a synonym, so it's struck. M: popular and digital are different topics.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Eliminate")
        self.play(Indicate(q.rows, color=BAD, scale_factor=1.02))
        self.at_word(n, "S")
        self.play(self.light("S"), *q.strike("b")[1])
        self.at_word(n, "M")
        self.play(self.light("M"), *q.strike("c")[1], *q.strike("d")[1])
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_03",
            text="Confirm: trends are not ephemeral but permanent. It contradicts, so it's the antonym. The answer is "
                 "permanent.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Confirm")
        self.play(ReplacementTransform(slide, filled))
        self.at_word(n, "contradicts")
        self.play(FadeIn(verdict, shift=UP * 0.1))
        self.at_word(n, "answer")
        self.play(*q.confirm()[1])
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S10_hook_solved")

    # ========================================== 11. EXAM PATTERNS ==========

    def exam_patterns(self):
        self.scene_start("S11_patterns", title="Exam Patterns and Solving Models")
        self.play(self.unpin())

        table = self.table_rows(["Pattern", "First checks"], [
            ["Single word", "S, P"],
            ["Word in a sentence", "M, then S"],
            ["Prefixed word", "D, then S"],
            ["Gradable or role word", "T"],
        ], [6.4, 5.4], size=LABEL)
        board = self.card(table, width=SAFE_W - 0.2).move_to(UP * 0.4)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="patterns_01",
            text="Which checks come first? For a single word: S and P. For a word in a sentence: M, then S. For a prefixed "
                 "word: D, then S. And for a gradable or role word: T.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(board[0]), FadeIn(table[0]))
        for row, spoken in zip(table[1:], ["single", "sentence", "prefixed", "gradable"]):
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
            (self.verdict_card(False, "Skipping the synonym strike", card_w),
             self.verdict_card(True, "Strike synonyms first, every time", card_w)),
            (self.verdict_card(False, "Reading the options before predicting", card_w),
             self.verdict_card(True, "Predict first", card_w)),
            (self.verdict_card(False, "Stripping a prefix", card_w),
             self.verdict_card(True, "Decode the true meaning", card_w)),
        ]
        for (wrong, right), yy in zip(pairs, [1.6, 0.05, -1.5]):
            wrong.move_to(LEFT_ZONE + UP * yy)
            right.move_to(RIGHT_ZONE + UP * yy)
        header = pill("3 mistakes", BAD, size=LABEL).move_to(UP * (CARD_TOP - 0.3))
        self.validator.check_in_frame(VGroup(header, *[c for p in pairs for c in p]))

        n = self.narrate(
            id="mistakes_01",
            text="Three common mistakes. The first is skipping the synonym strike. The second is reading the options "
                 "before predicting. The third is stripping a prefix instead of decoding it.",
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
        ("ADAMANT", "ADAMANT", ["stubborn", "angry", "adamantine", "yielding"], "d",
         {"a": "synonym", "b": "unrelated", "c": "sound-alike"}),
        ("ACQUIT", "ACQUIT", ["release", "acquire", "convict", "accuse"], "c",
         {"a": "synonym", "b": "sound-alike", "d": "happens earlier: not the verdict"}),
        ("EXPLICIT", "“The report was full of EXPLICIT instructions.”", ["clear", "vague", "exact", "written"], "b",
         {"a": "synonym", "c": "synonym", "d": "unrelated"}),
    ]

    def practice(self):
        self.scene_start("S13_practice", title="Practice Questions")

        lines = VGroup(*[VGroup(VGroup(pill(str(i + 1), FOCUS, size=SMALL), pill(shown, WORD, size=LABEL))
                                .arrange(RIGHT, buff=0.35),
                                text("   ".join(f"({l}) {o}" for l, o in zip("abcd", opts)), LABEL, INK))
                         .arrange(DOWN, buff=0.2, aligned_edge=LEFT)
                         for i, (w, shown, opts, *_r) in enumerate(self.PRACTICE)])
        lines.arrange(DOWN, buff=0.45, aligned_edge=LEFT)
        board = self.card(lines, color=FOCUS)
        fit_within(board, SAFE_W, SAFE_H - 1.2)
        board.move_to(UP * 0.4)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="practice_01",
            text="Your turn, thirty seconds each. One: adamant. Stubborn, angry, adamantine, or yielding? Two: acquit. "
                 "Release, acquire, convict, or accuse? Three: the report was full of explicit instructions. Clear, "
                 "vague, exact, or written?",
            voice="default",
            subtitle=True,
            pause_after=12.0,
        )
        self.play(FadeIn(board[0]))
        for ln, (spoken, first_option) in zip(lines, [("adamant", "Stubborn"), ("acquit", "Release"),
                                                     ("report", "Clear")]):
            self.at_word(n, spoken)
            self.play(FadeIn(ln[0], shift=UP * 0.15), run_time=0.4)
            self.at_word(n, first_option)
            self.play(FadeIn(ln[1], shift=LEFT * 0.15), run_time=0.4)
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        self.clear_stage()
        self.scene_end("S13_practice")

    # =============================================== 14. ANSWERS ==========

    def answers(self):
        self.scene_start("S14_answers", title="Answers")

        rows = VGroup()
        for w, shown, opts, key, traps in self.PRACTICE:
            OptionQuestion(w, opts, key, traps)            # validates key / traps
            if w.lower() in OPPOSITE:
                assert opts["abcd".index(key)] == OPPOSITE[w.lower()]
            others = [f"({l}) {opts['abcd'.index(l)]}: {r}" for l, r in traps.items() if r != "unrelated"]
            rows.add(VGroup(VGroup(pill(w, WORD, size=LABEL), text("↔", LABEL, MUTED),
                                   pill(f"({key}) {opts['abcd'.index(key)]}", GOOD, size=LABEL)).arrange(RIGHT, buff=0.3),
                            text("   ".join(others), SMALL, BAD)).arrange(DOWN, buff=0.18, aligned_edge=LEFT))
        rows.arrange(DOWN, buff=0.5, aligned_edge=LEFT)
        fit_within(rows, SAFE_W, SAFE_H - 1.2)
        rows.move_to(UP * 0.3)
        self.validator.check_in_frame(rows)

        n = self.narrate(
            id="answers_01",
            text="One: yielding. Stubborn is a synonym, and adamantine is a sound-alike. Two: convict. The legal opposite "
                 "of acquit is convict; accuse happens earlier, so it's not the opposite of the verdict. Three: vague. "
                 "Clear and exact are synonyms.",
            voice="default",
            subtitle=True,
        )
        for r, (spoken, trap) in zip(rows, [("yielding", "Stubborn"), ("convict", "accuse"), ("vague", "Clear")]):
            self.at_word(n, spoken, occurrence=1)
            self.play(FadeIn(r[0], shift=RIGHT * 0.2), run_time=0.5)
            self.at_word(n, trap)
            self.play(FadeIn(r[1], shift=LEFT * 0.1), run_time=0.4)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S14_answers")

    # ================================================ 15. RECAP ==========

    def recap(self):
        self.scene_start("S15_recap", title="Recap Card: Lesson 2 Method")

        card, table = self.recap_card("Recap Card: Lesson 2 Method", [
            ["Method", "PREDICT → S → P → T → M → D → CONFIRM"],
            ["First reflex", "strike synonyms"],
            ["Confirm", "“not X but Y” should read as a contradiction"],
            ["Time", "about 30 seconds per antonym question"],
        ])
        card.move_to(UP * 0.2)
        self.validator.check_in_frame(card)

        n = self.narrate(
            id="recap_01",
            text="To recap the lesson two method: predict, then S, P, T, M, D, then confirm. The first reflex: strike "
                 "synonyms. As a final test, not X but Y should read as a contradiction. And the target time is about "
                 "thirty seconds per antonym question.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(card[0]), FadeIn(table[0]))
        for row, spoken in zip(table[1:], ["predict", "reflex", "contradiction", "time"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.45)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S15_recap")

    # ================================================= 16. NEXT ==========

    def next_video(self):
        self.scene_start("S16_next", title="Next")

        done = pill("Lesson 2: Antonyms  ✓", GOOD, size=LABEL)
        todo = VGroup(pill("Lesson 2 Quiz", FOCUS, size=LABEL), pill("Cheat Sheet", WORD, size=LABEL))\
            .arrange(RIGHT, buff=0.6)
        move = VGroup(pill("single words", MUTED, size=BODY), text("→", TITLE, MUTED),
                      pill("phrases", SECOND, size=BODY)).arrange(RIGHT, buff=0.4)
        nxt = pill("Next lesson:  Idioms & Phrases", FOCUS, size=BODY)
        VGroup(done, todo, move, nxt).arrange(DOWN, buff=0.5).move_to(UP * 0.1)
        self.no_overlap(done, todo, move, nxt)
        self.validator.check_in_frame(VGroup(done, todo, move, nxt))

        n = self.narrate(
            id="next_01",
            text="Take the lesson two quiz, and keep the cheat sheet. Lesson three moves from single words to phrases: "
                 "idioms and phrases.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(done, scale=1.1))
        self.at_word(n, "quiz")
        self.play(FadeIn(todo[0], shift=UP * 0.1))
        self.at_word(n, "cheat")
        self.play(FadeIn(todo[1], shift=UP * 0.1))
        self.at_word(n, "single")
        self.play(FadeIn(move, shift=UP * 0.1))
        self.at_word(n, "idioms")
        self.play(FadeIn(nxt, scale=1.1))
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S16_next")

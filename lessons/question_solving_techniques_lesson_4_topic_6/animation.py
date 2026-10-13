"""
animation.py for the LMS video generator.

Course : C-CAT - Section A - English
Module : Module 1 - Vocabulary
Lesson : Lesson 4 - One-Word Substitution
Video  : 06 - Question-Solving Techniques (Video 6 of 6)

Source script:
  C:\\Users\\User\\Downloads\\C-CAT_SectionA_Module1_English\\English\\Module 1 - Vocabulary\\
  Lesson 4 - One-Word Substitution\\06 - Question-Solving Techniques.pdf

Built on the golden-reference pattern:
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``;
  * layouts stacked with next_to and guarded with ``no_overlap``; nothing is
    ever animated onto or into another box.

The four checks live in CHECKS (C, K, Q, R), the 30-second budget in TIMELINE, and the hook's shared-root options in HALVES (first half, second half, what the second half says).
The C-K-Q-R card stays pinned top-right through the worked examples and Hook, Solved, and each check lights up as it is used.
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

CHECKS = [("C", "Category", WORD), ("K", "Key idea", RATIO), ("Q", "Qualifier", SECOND), ("R", "Root check", BAD)]
CHECK_COL = {k: c for k, _, c in CHECKS}

# Time budget from the script (seconds): (start, end, step).
TIMELINE = [(0, 5, "read; split into C, K, Q; predict"), (5, 20, "strike wrong categories and wrong key ideas"),
            (20, 25, "apply the qualifier; decode the second halves"), (25, 30, "confirm in a sentence")]

# Shared-root options from the hook: word -> (first half, second half, what the second half says).
HALVES = {
    "ambidextrous": ("ambi", "dextrous", "hand: both hands"),
    "ambivert": ("ambi", "vert", "turn: personality"),
    "ambiguous": ("ambi", "guous", "way: doubtful meaning"),
    "amphibious": ("amphi", "bious", "life: on land and in water"),
}
assert all(a + b == w for w, (a, b, _m) in HALVES.items())


class SubstitutionTechniquesVideo(LMSScene):
    lesson_title = "Question-Solving Techniques"

    def construct(self):
        self.camera.background_color = BG

        self.lesson_intro()
        self.hook()
        self.concept()
        self.why_you_need_it()
        self.analogy()
        self.example_hydrophobia()
        self.example_autocracy()
        self.example_egoist()
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
        return self.steps_pin("C-K-Q-R", [(f"{k}  {name}", c) for k, name, c in CHECKS])

    def light(self, letter):
        """Animation: light the row of the pinned C-K-Q-R panel for this check."""
        return self.pin_step([k for k, _, _ in CHECKS].index(letter), color=CHECK_COL[letter])

    def profile_card(self, fill=None):
        head = VGroup(text("CRICKET PROFILE", SMALL, RATIO, BOLD), pill("0:30", BAD, size=SMALL)).arrange(RIGHT, buff=0.5)
        s_ = (f"“The bowler is {fill}.”" if fill else "“The bowler can bowl equally well with both hands.”")
        cx, w = self.free_area()
        line = fitted_text(s_, min(w - 1.4, SAFE_W - 1.8), LABEL, INK, NORMAL, max_lines=2,
                           t2c={fill or "equally well with both hands": GOOD if fill else WORD})
        card = self.card(VGroup(head, line).arrange(DOWN, buff=0.2, aligned_edge=LEFT), width=min(w - 0.2, SAFE_W - 0.4))
        return card.move_to(RIGHT * cx + UP * (CARD_TOP - card.height / 2))

    def check_chips(self, items, size=SMALL):
        """One chip per check used: (letter, what it finds)."""
        return VGroup(*[VGroup(pill(k, CHECK_COL[k], size=size), text(v, LABEL, INK)).arrange(RIGHT, buff=0.2)
                        for k, v in items])

    def ckqr_example(self, definition, items, word, miss=None):
        """Definition, the checks used (lit on the pin), the word, and an optional near-miss."""
        cx, w = self.free_area()
        head = fitted_text(f"“{definition}”", w - 0.8, BODY, INK, NORMAL, max_lines=2)
        chips = self.check_chips(items).arrange(DOWN, buff=0.25, aligned_edge=LEFT)
        answer = VGroup(text("→", BODY, MUTED), pill(word, GOOD, size=BODY)).arrange(RIGHT, buff=0.3)
        parts = [head, chips, answer] + ([fitted_text(miss, w - 0.8, LABEL, BAD, NORMAL, max_lines=2)] if miss else [])
        block = VGroup(*parts).arrange(DOWN, buff=0.45, aligned_edge=LEFT)
        fit_height(block, SAFE_H - 1.6)
        self.place_free(block, y=0.1)
        self.no_overlap(*parts)
        self.validator.check_in_frame(block)
        return parts

    # ========================================= 0. LESSON INTRO ==========

    def lesson_intro(self):
        self.scene_start("S00_intro", title="Lesson Introduction")

        crumb = self.breadcrumb("English · Module 1 Vocabulary", "Lesson 4 · One-Word Substitution", "Video 6")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        ideas = VGroup(*[pill(t, c, size=LABEL) for t, c in [("conditions", WORD), ("categories", RATIO),
                                                            ("context", SECOND), ("confusable groups", BAD),
                                                            ("high-frequency list", GOOD)]]).arrange(RIGHT, buff=0.3)
        fit_width(ideas, SAFE_W)
        one = pill("today: one method holds them together", FOCUS, size=LABEL)
        VGroup(ideas, one).arrange(DOWN, buff=0.8).move_to(DOWN * 0.1)
        self.no_overlap(crumb, ideas, one)
        self.validator.check_in_frame(VGroup(crumb, ideas, one))

        n = self.narrate(
            id="intro_01",
            text="Videos one to five gave you conditions, categories, context, confusable groups and the high-frequency "
                 "list. Today, one method holds them together.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.at_word(n, "conditions")
        self.play(LaggedStart(*[FadeIn(i, shift=UP * 0.1) for i in ideas], lag_ratio=0.3), run_time=2.5)
        self.at_word(n, "Today")
        self.play(FadeIn(one, shift=UP * 0.1))
        self.wait_for_narration(n)

        title = fitted_text("Question-Solving Techniques", SAFE_W, 68, INK, BOLD)
        underline = Line(LEFT, RIGHT, color=GOOD, stroke_width=5).set_width(title.width * 0.6)
        VGroup(title, underline).arrange(DOWN, buff=0.2).move_to(UP * 0.2)
        n = self.narrate(
            id="intro_02",
            text="This is the last video of lesson four: question-solving techniques.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(VGroup(ideas, one), shift=UP * 0.3))
        self.at_word(n, "question-solving")
        self.play(Write(title), run_time=1.1)
        self.play(GrowFromCenter(underline))
        self.wait_for_narration(n)

        goals = [
            ("Solve any one-word substitution question with a fixed method", BAD),
            ("Decode unfamiliar options using the second half of the word", GOOD),
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
            text="By the end of this video, you'll solve any one-word substitution question with a fixed method, and "
                 "decode unfamiliar options using the second half of the word.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(underline), ReplacementTransform(title, small_title), run_time=0.8)
        self.play(FadeIn(objectives[0]), FadeIn(heading))
        for row_, spoken in zip(rows, ["solve", "decode"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row_, shift=RIGHT * 0.2), run_time=0.5)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_intro")

    # ================================================= 1. HOOK ==========

    HOOK = dict(word="one word?", options=list(HALVES), key="a",
                traps={"b": "R: vert = turn (personality)", "c": "R: about meaning",
                       "d": "R: living on land and in water"})

    def hook(self):
        self.scene_start("S01_hook", title="Hook")

        h = self.HOOK
        profile = self.profile_card()
        q = OptionQuestion(h["word"], h["options"], h["key"], h["traps"])
        opts = q.rows.copy().arrange(RIGHT, buff=0.7)
        fit_width(opts, SAFE_W)
        ask = pill("the editor: one word for “able to use both hands equally well”", FOCUS, size=SMALL)
        trap = pill("all four start with the same root: that's exactly the trap", BAD, size=SMALL)
        ask.next_to(profile, DOWN, buff=0.45)
        opts.next_to(ask, DOWN, buff=0.55)
        trap.next_to(opts, DOWN, buff=0.55)
        self.no_overlap(profile, ask, opts, trap)
        self.validator.check_in_frame(VGroup(profile, ask, opts, trap))

        n = self.narrate(
            id="hook_01",
            text="A cricket profile says: the bowler can bowl equally well with both hands. The editor wants one word for: "
                 "able to use both hands equally well. You have thirty seconds.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "profile")
        self.play(FadeIn(profile, shift=DOWN * 0.2))
        self.at_word(n, "editor")
        self.play(FadeIn(ask, shift=UP * 0.1))
        self.at_word(n, "seconds")
        self.play(Indicate(profile[1][0][1], color=BAD, scale_factor=1.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_02",
            text="Ambidextrous, ambivert, ambiguous, or amphibious? All four start with the same root. That's exactly the "
                 "trap.",
            voice="default",
            subtitle=True,
            pause_after=3.0,
        )
        for row, spoken in zip(opts, ["Ambidextrous", "ambivert", "ambiguous", "amphibious"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=UP * 0.15), run_time=0.35)
        self.at_word(n, "same")
        self.play(FadeIn(trap, shift=UP * 0.1))
        self.at_word(n, "trap")
        self.play(Indicate(trap, color=BAD, scale_factor=1.04))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        self.clear_stage()
        self.scene_end("S01_hook")

    # ============================================== 2. CONCEPT ==========

    def concept(self):
        self.scene_start("S02_concept", title="The Concept")

        head = pill("every substitution question: four checks:  C-K-Q-R", FOCUS, size=LABEL)
        fit_width(head, SAFE_W)
        head.move_to(UP * (CARD_TOP - head.height / 2))
        rows = VGroup(*[VGroup(pill(k, c, size=BODY), text(name, LABEL, c, BOLD),
                               fitted_text(q, 6.6, LABEL, INK)).arrange(RIGHT, buff=0.35)
                        for (k, name, c), q in zip(CHECKS, [
                            "person, place, action, state, study or rule?  fixes the ENDING",
                            "the core meaning of the definition",
                            "two / many, in / out, self / others, cannot / can",
                            "decode each surviving option"])])
        rows.arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        fit_within(rows, SAFE_W, SAFE_H - head.height - 1.6)
        rows.next_to(head, DOWN, buff=0.45)
        self.no_overlap(head, rows)
        self.validator.check_in_frame(VGroup(head, rows))

        n = self.narrate(
            id="concept_01",
            text="Every substitution question can be solved with four checks: C, K, Q, R.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "checks")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_02",
            text="C is category: person, place, action, state, study or rule? This fixes the ending. K is the key idea: the "
                 "core meaning of the definition. Q is the qualifier: the detail that separates close options: two or "
                 "many, in or out, self or others, cannot or can. And R is the root check: decode each surviving option.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "category")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2), run_time=0.45)
        self.at_word(n, "ending")
        self.play(Indicate(rows[0][2], color=WORD, scale_factor=1.03))
        for r, spoken in zip(rows[1:], ["key", "qualifier", "root"]):
            self.at_word(n, spoken)
            self.play(FadeIn(r, shift=RIGHT * 0.2), run_time=0.45)
        self.wait_for_narration(n)

        # Shared roots: the second half decides.
        shared = pill("options share a root (amb-, omni-, anti-):  the first half is useless", BAD, size=LABEL)
        shared.move_to(UP * (CARD_TOP - shared.height / 2))
        second = pill("the SECOND half decides", GOOD, size=BODY)
        halves = VGroup(*[VGroup(text(a, BODY, MUTED), text("+", LABEL, MUTED), pill(b, GOOD, size=LABEL),
                                 text(m, LABEL, INK)).arrange(RIGHT, buff=0.3)
                          for a, b, m in [HALVES[w] for w in ["ambidextrous", "ambivert", "ambiguous"]]])
        halves.arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        body = VGroup(second, halves).arrange(DOWN, buff=0.5)
        fit_width(body, SAFE_W)
        body.next_to(shared, DOWN, buff=0.6)
        self.no_overlap(shared, second, halves)
        self.validator.check_in_frame(VGroup(shared, body))
        n = self.narrate(
            id="concept_03",
            text="When options share a root, like amb, omni or anti, the first half is useless for choosing. The answer is "
                 "decided by the second half. Ambi plus dextrous: hand. Ambi plus vert: turn. Ambi plus guous: way, a "
                 "doubtful meaning.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(VGroup(head, rows)))
        self.at_word(n, "share")
        self.play(FadeIn(shared, shift=DOWN * 0.2))
        self.at_word(n, "second")
        self.play(FadeIn(second, scale=1.05))
        for r, spoken in zip(halves, ["dextrous", "vert", "guous"]):
            self.at_word(n, spoken)
            self.play(FadeIn(r, shift=RIGHT * 0.2), run_time=0.45)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_concept")

    # ======================================== 3. WHY YOU NEED IT ==========

    def why_you_need_it(self):
        self.scene_start("S03_why", title="Why You Need It")

        time_ = pill("a substitution question: about 30 seconds", RATIO, size=BODY)
        new = pill("C-K-Q-R gets you there even when the word is NEW", GOOD, size=LABEL)
        common = text("…which is common in this topic", LABEL, MUTED)
        group = VGroup(time_, VGroup(new, common).arrange(DOWN, buff=0.2)).arrange(DOWN, buff=0.9)
        fit_width(group, SAFE_W).move_to(UP * 0.3)
        self.validator.check_in_frame(group)

        n = self.narrate(
            id="why_01",
            text="Substitution questions should take about thirty seconds. C, K, Q, R lets you get there even when the word "
                 "is new, which is common in this topic.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "thirty")
        self.play(FadeIn(time_, shift=DOWN * 0.1))
        self.at_word(n, "new")
        self.play(FadeIn(new, shift=UP * 0.1))
        self.at_word(n, "common")
        self.play(FadeIn(common, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_why")

    # ============================================== 4. ANALOGY ==========

    def analogy(self):
        self.scene_start("S04_analogy", title="The Analogy")

        words = ["ambidextrous", "ambivert", "ambiguous"]
        fields = VGroup()
        for w in words:
            a, b, _m = HALVES[w]
            start = text(a, BODY, WORD)
            dots = text("•" * len(b), BODY, MUTED).next_to(start, RIGHT, buff=0.06)
            full = text(b, BODY, GOOD if w == "ambidextrous" else INK).next_to(start, RIGHT, buff=0.06)
            fields.add(VGroup(start, dots, full))
        fields.arrange(DOWN, buff=0.45, aligned_edge=LEFT)
        login = text("✓  logs in", LABEL, GOOD).next_to(fields[0], RIGHT, buff=0.5)
        left = VGroup(text("password", SMALL, MUTED, BOLD).next_to(fields, UP, buff=0.3).align_to(fields, LEFT), fields,
                      login)
        left.move_to(LEFT * 3.2 + UP * 0.3)
        tags = VGroup(pill("same beginning: proves nothing", BAD, size=LABEL),
                      pill("only the FULL string logs you in", GOOD, size=LABEL),
                      pill("shared-root options: check the ENDING", FOCUS, size=LABEL))\
            .arrange(DOWN, buff=0.5, aligned_edge=LEFT)
        fit_width(tags, 6.2)
        tags.move_to(RIGHT * 3.3 + UP * 0.3)
        self.no_overlap(left, tags)
        self.validator.check_in_frame(VGroup(left, tags))

        n = self.narrate(
            id="analogy_01",
            text="When several passwords start the same way, the beginning proves nothing. Only the full string logs you "
                 "in. With shared-root options, check the ending.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "passwords")
        self.play(FadeIn(left[0]), LaggedStart(*[FadeIn(VGroup(f[0], f[1]), shift=RIGHT * 0.2) for f in fields],
                                               lag_ratio=0.25))
        self.at_word(n, "beginning")
        self.play(FadeIn(tags[0], shift=LEFT * 0.1), *[Indicate(f[0], color=BAD, scale_factor=1.1) for f in fields])
        self.at_word(n, "full")
        self.play(*[ReplacementTransform(f[1], f[2]) for f in fields], FadeIn(tags[1], shift=LEFT * 0.1))
        self.play(FadeIn(login, shift=LEFT * 0.1), run_time=0.4)
        self.at_word(n, "ending")
        self.play(FadeIn(tags[2], shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_analogy")

    # ======================================== 5-7. WORKED EXAMPLES ==========

    def example_hydrophobia(self):
        self.scene_start("S05_ex_hydrophobia", title="Worked Example 1")
        self.play(self.pin(self.check_pin()))

        head, chips, answer = self.ckqr_example("Fear of water", [("C", "a state: a fear  →  -phobia"),
                                                                  ("K", "water  →  hydro")], "hydrophobia")

        n = self.narrate(
            id="ex1_01",
            text="Fear of water. C: a state, a fear, so the ending is phobia. K: water, which is hydro. The word is "
                 "hydrophobia.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "water", occurrence=1)
        self.play(FadeIn(head, shift=DOWN * 0.1))
        self.at_word(n, "C")
        self.play(FadeIn(chips[0], shift=RIGHT * 0.2), self.light("C"))
        self.at_word(n, "K")
        self.play(FadeIn(chips[1], shift=RIGHT * 0.2), self.light("K"))
        self.at_word(n, "hydrophobia")
        self.play(FadeIn(answer, scale=1.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_ex_hydrophobia")

    def example_autocracy(self):
        self.scene_start("S06_ex_autocracy", title="Worked Example 2")

        head, chips, answer, miss = self.ckqr_example(
            "Rule by one person with absolute power", [("C", "a rule word  →  -cracy"), ("Q", "ONE person  →  auto")],
            "autocracy", miss="not monarchy: rule by a king or queen, often hereditary")

        n = self.narrate(
            id="ex2_01",
            text="Rule by one person with absolute power. C: a rule word. Q: one person. The word is autocracy. Not "
                 "monarchy, which is rule by a king or queen, often hereditary.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Rule", occurrence=1)
        self.play(FadeIn(head, shift=DOWN * 0.1))
        self.at_word(n, "C")
        self.play(FadeIn(chips[0], shift=RIGHT * 0.2), self.light("C"))
        self.at_word(n, "Q")
        self.play(FadeIn(chips[1], shift=RIGHT * 0.2), self.light("Q"))
        self.at_word(n, "autocracy")
        self.play(FadeIn(answer, scale=1.1))
        self.at_word(n, "monarchy")
        self.play(FadeIn(miss, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_ex_autocracy")

    def example_egoist(self):
        self.scene_start("S07_ex_egoist", title="Worked Example 3")

        head, chips, answer = self.ckqr_example("A person who is interested only in himself",
                                                [("C", "a person  →  -ist"), ("K", "self  →  ego")], "egoist")

        n = self.narrate(
            id="ex3_01",
            text="A person who is interested only in himself. C: a person. K: self, and ego means self. The word is "
                 "egoist.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "interested")
        self.play(FadeIn(head, shift=DOWN * 0.1))
        self.at_word(n, "C")
        self.play(FadeIn(chips[0], shift=RIGHT * 0.2), self.light("C"))
        self.at_word(n, "K")
        self.play(FadeIn(chips[1], shift=RIGHT * 0.2), self.light("K"))
        self.at_word(n, "egoist")
        self.play(FadeIn(answer, scale=1.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S07_ex_egoist")

    # ================================================ 8. RULES ==========

    def rules(self):
        self.scene_start("S08_rules", title="Rules")
        self.play(self.unpin())

        strip = self.method_strip()
        fit_width(strip, SAFE_W)
        strip.move_to(UP * (CARD_TOP - strip.height / 2))
        table = self.table_rows(["Check", "Catches"], [
            ["C", "wrong category (study for person, place for thing)"],
            ["K", "wrong core meaning"],
            ["Q", "wrong scope, direction or number"],
            ["R", "shared-root traps"],
        ], [2.0, 9.0], size=LABEL)
        for row, (_, _, c) in zip(table[1:], CHECKS):
            row[0].set_color(c)
        board = self.card(table, width=SAFE_W - 0.2)
        fit_height(board, SAFE_H - strip.height - 1.4)
        board.next_to(strip, DOWN, buff=0.5)
        self.no_overlap(strip, board)
        self.validator.check_in_frame(VGroup(strip, board))

        n = self.narrate(
            id="rules_01",
            text="The full method: predict, then C, K, Q, R, then confirm. C catches the wrong category: a study for a "
                 "person, or a place for a thing. K catches the wrong core meaning. Q catches the wrong scope, direction "
                 "or number. And R catches shared-root traps.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "predict")
        self.play(LaggedStart(*[FadeIn(c, shift=RIGHT * 0.1) for c in strip], lag_ratio=0.1))
        self.play(FadeIn(board[0]), FadeIn(table[0]))
        for row, spoken in zip(table[1:], ["category", "core", "scope", "shared-root"]):
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
        labels = VGroup(*[fitted_text(lab, 7.4, LABEL, c) for (_, _, lab), c in zip(TIMELINE, cols)])
        rows = VGroup(*[VGroup(pill(f"{s_}–{e} s", c, size=SMALL), lab).arrange(RIGHT, buff=0.3)
                        for (s_, e, _), c, lab in zip(TIMELINE, cols, labels)]).arrange(DOWN, buff=0.25,
                                                                                        aligned_edge=LEFT)
        rows.next_to(ticks, DOWN, buff=0.5)
        assert TIMELINE[0][0] == 0 and TIMELINE[-1][1] == 30 and all(a[1] == b[0] for a, b in zip(TIMELINE, TIMELINE[1:]))
        self.no_overlap(VGroup(segs, ticks), rows)
        self.validator.check_in_frame(VGroup(segs, ticks, rows))

        n = self.narrate(
            id="process_01",
            text="Here's the thirty-second budget. From zero to five seconds, read, split the definition into C, K and Q, "
                 "and predict. From five to twenty, strike wrong categories and wrong key ideas. From twenty to "
                 "twenty-five, apply the qualifier, and decode the second halves of shared-root options. From twenty-five "
                 "to thirty, confirm in a sentence.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "budget")
        self.play(FadeIn(ticks))
        for seg, row, (spoken, occ) in zip(segs, rows, [("zero", 1), ("five", 2), ("twenty", 2),
                                                         ("twenty-five", 2)]):
            self.at_word(n, spoken, occurrence=occ)
            self.play(GrowFromEdge(seg, LEFT), FadeIn(row, shift=RIGHT * 0.2), run_time=0.5)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S09_process")

    # ========================================== 10. HOOK, SOLVED ==========

    def hook_solved(self):
        self.scene_start("S10_hook_solved", title="Hook, Solved")
        self.play(self.pin(self.check_pin()))

        h = self.HOOK
        cx, w = self.free_area()
        profile = self.profile_card()
        chips = self.check_chips([("C", "a person's ability"), ("K", "using hands"), ("Q", "BOTH, equally")])\
            .arrange(RIGHT, buff=0.35)
        predict = pill("ambi (both) + dext (hand)", STEP_COLS["PREDICT"], size=SMALL)
        notes = VGroup(chips, predict).arrange(RIGHT, buff=0.4)
        fit_width(notes, w - 0.6)
        notes.next_to(profile, DOWN, buff=0.3).to_edge(LEFT, buff=SAFE + 0.6)
        q = OptionQuestion(h["word"], h["options"], h["key"], h["traps"], word_size=LABEL)
        fit_height(q.group, notes.get_bottom()[1] - 0.3 - (BOTTOM_Y + 0.6))
        q.group.next_to(notes, DOWN, buff=0.3).to_edge(LEFT, buff=SAFE + 0.6)
        fixed = self.profile_card(fill="ambidextrous")
        self.no_overlap(profile, notes, q.group)
        self.no_overlap(profile, self.pinned)
        self.no_overlap(notes, self.pinned)
        self.validator.check_in_frame(VGroup(profile, notes, q.group))

        n = self.narrate(
            id="solved_01",
            text="Let's solve the hook. Read. C: a person's ability. K: using hands. Q: both hands, equally. Predict: ambi, "
                 "both, plus dext, hand.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "solve")
        self.play(FadeIn(profile), FadeIn(q.word), FadeIn(q.rows))
        self.at_word(n, "Read")
        self.play(Indicate(profile[1][1], color=WORD, scale_factor=1.02))
        for chip, spoken in zip(chips, ["C", "K", "Q"]):
            self.at_word(n, spoken)
            self.play(FadeIn(chip, shift=UP * 0.1), self.light(spoken), run_time=0.5)
        self.at_word(n, "Predict")
        self.play(FadeIn(predict, shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_02",
            text="Eliminate with R. Ambivert is about personality: vert means turn. Ambiguous is about meaning. Amphibious "
                 "means living on land and in water.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Eliminate")
        self.play(self.light("R"))
        for letter, spoken in [("b", "Ambivert"), ("c", "Ambiguous"), ("d", "Amphibious")]:
            self.at_word(n, spoken)
            self.play(*q.strike(letter)[1])
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_03",
            text="Confirm: the bowler is ambidextrous. That's the answer.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Confirm")
        self.play(ReplacementTransform(profile, fixed))
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
            ["“A person who …”", "C, then Q"],
            ["Shared-root options", "R on the second half"],
            ["Confusable group", "Q (scope, direction, level)"],
            ["In a sentence", "add a grammar check (Video 3)"],
        ], [5.4, 6.4], size=LABEL)
        board = self.card(table, width=SAFE_W - 0.2).move_to(UP * 0.4)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="patterns_01",
            text="Which checks come first? For a person who: C, then Q. For shared-root options: R, on the second half. "
                 "For a confusable group: Q: scope, direction or level. And in a sentence: add a grammar check, from "
                 "video three.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "first")
        self.play(FadeIn(board[0]), FadeIn(table[0]))
        for row, spoken in zip(table[1:], ["person", "shared-root", "confusable", "sentence"]):
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
            (self.verdict_card(False, "Choosing on the shared first root", card_w),
             self.verdict_card(True, "Decide on the SECOND half", card_w)),
            (self.verdict_card(False, "Ignoring the qualifier", card_w),
             self.verdict_card(True, "two / many, in / out, self / others", card_w)),
            (self.verdict_card(False, "A word from the wrong category", card_w),
             self.verdict_card(True, "Fix the category first", card_w)),
        ]
        for (wrong, right), yy in zip(pairs, [1.6, 0.05, -1.5]):
            wrong.move_to(LEFT_ZONE + UP * yy)
            right.move_to(RIGHT_ZONE + UP * yy)
        header = pill("3 mistakes", BAD, size=LABEL).move_to(UP * (CARD_TOP - 0.3))
        self.validator.check_in_frame(VGroup(header, *[c for p in pairs for c in p]))

        n = self.narrate(
            id="mistakes_01",
            text="Three common mistakes. Number one is choosing on the shared first root. The second is ignoring the "
                 "qualifier. The third is choosing a word from the wrong category.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(header))
        for pr, spoken in zip(pairs, ["one", "second", "third"]):
            self.at_word(n, spoken)
            self.play(FadeIn(pr[0], shift=RIGHT * 0.3), FadeIn(pr[1], shift=LEFT * 0.3))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S12_mistakes")

    # ============================================== 13. PRACTICE ==========

    PRACTICE = [
        ("A person who doubts everything", ["optimist", "pessimist", "sceptic", "cynic"], "c",
         "(b) a pessimist expects the worst;  (d) a cynic distrusts others' motives"),
        ("A thing no longer in use", ["obscure", "obsolete", "absolute", "obstinate"], "b",
         "the others are sound-alikes"),
        ("One who walks on foot", ["pedant", "pedlar", "pedagogue", "pedestrian"], "d",
         "R: ped = foot here;  a pedagogue is a teacher (paed = child)"),
    ]

    def practice(self):
        self.scene_start("S13_practice", title="Practice Questions")

        lines = VGroup(*[VGroup(VGroup(pill(str(i + 1), FOCUS, size=SMALL), text(f"“{phrase}”", LABEL, WORD))
                                .arrange(RIGHT, buff=0.35),
                                text("   ".join(f"({l}) {o}" for l, o in zip("abcd", opts)), LABEL, INK))
                         .arrange(DOWN, buff=0.2, aligned_edge=LEFT)
                         for i, (phrase, opts, *_r) in enumerate(self.PRACTICE)])
        lines.arrange(DOWN, buff=0.45, aligned_edge=LEFT)
        board = self.card(lines, color=FOCUS)
        fit_within(board, SAFE_W, SAFE_H - 1.2)
        board.move_to(UP * 0.4)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="practice_01",
            text="Your turn, thirty seconds each. One: a person who doubts everything. Optimist, pessimist, sceptic, or "
                 "cynic? Two: a thing no longer in use. Obscure, obsolete, absolute, or obstinate? Three: one who walks on "
                 "foot. Pedant, pedlar, pedagogue, or pedestrian?",
            voice="default",
            subtitle=True,
            pause_after=12.0,
        )
        self.play(FadeIn(board[0]))
        for ln, (spoken, first_option) in zip(lines, [("doubts", "Optimist"), ("longer", "Obscure"),
                                                     ("walks", "Pedant")]):
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

        rows = VGroup(*[VGroup(VGroup(text(f"“{phrase}”", LABEL, INK), text("→", LABEL, MUTED),
                                      pill(f"({key}) {opts['abcd'.index(key)]}", GOOD, size=LABEL))
                               .arrange(RIGHT, buff=0.3), text(why, SMALL, BAD)).arrange(DOWN, buff=0.18, aligned_edge=LEFT)
                        for phrase, opts, key, why in self.PRACTICE])
        rows.arrange(DOWN, buff=0.5, aligned_edge=LEFT)
        fit_within(rows, SAFE_W, SAFE_H - 1.2)
        rows.move_to(UP * 0.3)
        self.validator.check_in_frame(rows)

        n = self.narrate(
            id="answers_01",
            text="One: sceptic. A pessimist expects the worst, and a cynic distrusts the motives of others. Two: obsolete. "
                 "The others are sound-alikes. Three: pedestrian. Ped means foot here. A pedagogue is a teacher, from "
                 "paed, meaning child.",
            voice="default",
            subtitle=True,
        )
        for r, (spoken, why) in zip(rows, [("sceptic", "pessimist"), ("obsolete", "sound-alikes"),
                                           ("pedestrian", "Ped")]):
            self.at_word(n, spoken)
            self.play(FadeIn(r[0], shift=RIGHT * 0.2), run_time=0.5)
            self.at_word(n, why)
            self.play(FadeIn(r[1], shift=LEFT * 0.1), run_time=0.4)
        self.at_word(n, "pedagogue")
        self.play(Indicate(rows[2][1], color=BAD, scale_factor=1.03))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S14_answers")

    # ================================================ 15. RECAP ==========

    def recap(self):
        self.scene_start("S15_recap", title="Recap Card: Lesson 4 Method")

        card, table = self.recap_card("Recap Card: Lesson 4 Method", [
            ["Method", "PREDICT → C → K → Q → R → CONFIRM"],
            ["Shared root", "decide on the second half"],
            ["Time", "about 30 seconds"],
        ])
        card.move_to(UP * 0.2)
        self.validator.check_in_frame(card)

        n = self.narrate(
            id="recap_01",
            text="To recap the lesson four method: predict, then C, K, Q, R, then confirm. With a shared root, decide on "
                 "the second half. And the target time is about thirty seconds.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(card[0]), FadeIn(table[0]))
        for row, spoken in zip(table[1:], ["predict", "shared", "time"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.45)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S15_recap")

    # ================================================= 16. NEXT ==========

    def next_video(self):
        self.scene_start("S16_next", title="Next")

        done = pill("Lesson 4: One-Word Substitution  ✓", GOOD, size=LABEL)
        todo = VGroup(pill("Lesson 4 Quiz", FOCUS, size=LABEL), pill("Cheat Sheet", WORD, size=LABEL))\
            .arrange(RIGHT, buff=0.6)
        move = VGroup(pill("words", MUTED, size=BODY), text("→", TITLE, MUTED),
                      pill("relationships between words", SECOND, size=BODY)).arrange(RIGHT, buff=0.4)
        nxt = pill("Next lesson:  Analogies", FOCUS, size=BODY)
        VGroup(done, todo, move, nxt).arrange(DOWN, buff=0.5).move_to(UP * 0.1)
        self.no_overlap(done, todo, move, nxt)
        self.validator.check_in_frame(VGroup(done, todo, move, nxt))

        n = self.narrate(
            id="next_01",
            text="Take the lesson four quiz, and keep the cheat sheet. Lesson five moves from words to the relationships "
                 "between words: analogies.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(done, scale=1.1))
        self.at_word(n, "quiz")
        self.play(FadeIn(todo[0], shift=UP * 0.1))
        self.at_word(n, "cheat")
        self.play(FadeIn(todo[1], shift=UP * 0.1))
        self.at_word(n, "relationships")
        self.play(FadeIn(move, shift=UP * 0.1))
        self.at_word(n, "analogies")
        self.play(FadeIn(nxt, scale=1.1))
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S16_next")

"""
animation.py for the LMS video generator.

Course : C-CAT - Section A - English
Module : Module 1 - Vocabulary
Lesson : Lesson 5 - Analogies
Video  : 07 - Analogy Question-Solving Techniques (Video 7 of 7)

Source script:
  C:\\Users\\User\\Downloads\\C-CAT_SectionA_Module1_English\\English\\Module 1 - Vocabulary\\
  Lesson 5 - Analogies\\07 - Analogy Question-Solving Techniques.pdf

Built on the golden-reference pattern:
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``;
  * layouts stacked with next_to and guarded with ``no_overlap``; nothing is
    ever animated onto or into another box.

The four checks live in CHECKS (B, R, O, T) and the 40-second budget in TIMELINE. RELATION records whether each word pair is a synonym or antonym pair, and meaning_question(stem, options) picks the one option with the stem's relationship; the hook and practice question 1 are computed with it.
The B-R-O-T card stays pinned top-right through the worked examples and Hook, Solved, and each check lights up as it is used.
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

CHECKS = [("B", "Bridge", WORD), ("R", "Refine", RATIO), ("O", "Order", SECOND), ("T", "Type check", BAD)]
CHECK_COL = {k: c for k, _, c in CHECKS}

# Time budget from the script (seconds): (start, end, step).
TIMELINE = [(0, 10, "bridge from A to B"), (10, 25, "test options; refine if two survive"),
            (25, 35, "order and type check"), (35, 40, "confirm; guess only after one elimination")]

# Meaning relationships between word pairs (Lessons 1 and 2 vocabulary).
RELATION = {
    "Obstinate : Flexible": "antonym", "Generous : Stingy": "antonym", "Brave : Bold": "synonym",
    "Rich : Wealthy": "synonym", "Tired : Sleepy": "near-synonym",
    "Candid : Evasive": "antonym", "Frank : Honest": "synonym", "Brief : Short": "synonym",
    "Lucid : Obscure": "antonym", "Calm : Quiet": "synonym",
}


def meaning_question(stem, options):
    """T check on a meaning analogy: the answer is the one option with the stem's relationship."""
    want = RELATION[stem]
    keys = [l for l, o in zip("abcd", options) if RELATION[o] == want]
    assert len(keys) == 1, keys
    traps = {l: f"T: {RELATION[o]}s, not {want}s" for l, o in zip("abcd", options) if l != keys[0]}
    return options, keys[0], traps


def analogy_line(a, b, c, d="?", size=BODY):
    """A : B :: C : D as chips.  [0], [2] = first pair;  [4], [6] = second pair."""
    return VGroup(pill(a, WORD, size=size), text(":", size, MUTED), pill(b, WORD, size=size), text("::", size, MUTED),
                  pill(c, SECOND if c != "?" else FOCUS, size=size), text(":", size, MUTED),
                  pill(d, FOCUS if d == "?" else GOOD, size=size)).arrange(RIGHT, buff=0.25)


HOOK_Q = meaning_question("Obstinate : Flexible", ["Generous : Stingy", "Brave : Bold", "Rich : Wealthy",
                                                   "Tired : Sleepy"])
PRACTICE_Q1 = meaning_question("Candid : Evasive", ["Frank : Honest", "Brief : Short", "Lucid : Obscure", "Calm : Quiet"])
assert HOOK_Q[1] == "a" and PRACTICE_Q1[1] == "c"


class AnalogyTechniquesVideo(LMSScene):
    lesson_title = "Analogy Question-Solving Techniques"

    def construct(self):
        self.camera.background_color = BG

        self.lesson_intro()
        self.hook()
        self.concept()
        self.why_you_need_it()
        self.analogy()
        self.example_sock()
        self.example_starving()
        self.example_apprentice()
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
        parts = [("READ", STEP_COLS["READ"])] + [(k, c) for k, _, c in CHECKS] + [("CONFIRM", GOOD)]
        chips = []
        for i, (t, c) in enumerate(parts):
            if i:
                chips.append(text("→", size, MUTED))
            chips.append(pill(t, c, size=size))
        return VGroup(*chips).arrange(RIGHT, buff=0.2)

    def check_pin(self):
        return self.steps_pin("B-R-O-T", [(f"{k}  {name}", c) for k, name, c in CHECKS])

    def light(self, letter):
        """Animation: light the row of the pinned B-R-O-T panel for this check."""
        return self.pin_step([k for k, _, _ in CHECKS].index(letter), color=CHECK_COL[letter])

    def timer_card(self):
        head = VGroup(text("ANALOGY", SMALL, RATIO, BOLD), pill("0:40", BAD, size=SMALL)).arrange(RIGHT, buff=0.5)
        line = analogy_line("OBSTINATE", "FLEXIBLE", "?", size=LABEL)
        cx, w = self.free_area()
        body = VGroup(head, line).arrange(DOWN, buff=0.25, aligned_edge=LEFT)
        fit_width(body, min(w - 1.4, SAFE_W - 1.8))
        card = self.card(body, width=min(w - 0.2, SAFE_W - 0.4))
        return card.move_to(RIGHT * cx + UP * (CARD_TOP - card.height / 2))

    def brot_example(self, a, b, c, d, items, second):
        """Analogy line, the checks used (lit on the pin), and the bridge carried to the second pair."""
        cx, w = self.free_area()
        line = analogy_line(a, b, c)
        chips = VGroup(*[VGroup(pill(k, CHECK_COL[k], size=SMALL), text(v, LABEL, INK)).arrange(RIGHT, buff=0.25)
                         for k, v in items]).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        b2 = text(f"“{second}”", LABEL, INK, t2c={d: GOOD})
        block = VGroup(line, chips, b2).arrange(DOWN, buff=0.55, aligned_edge=LEFT)
        fit_within(block, w - 0.6, SAFE_H - 1.8)
        self.place_free(block, y=0.2)
        answer = pill(d, GOOD, size=BODY).scale(line[6].height / pill("?", FOCUS, size=BODY).height)
        answer.move_to(line[6], aligned_edge=LEFT)
        self.no_overlap(line, chips, b2)
        self.validator.check_in_frame(VGroup(block, answer))
        return line, chips, b2, answer

    # ========================================= 0. LESSON INTRO ==========

    def lesson_intro(self):
        self.scene_start("S00_intro", title="Lesson Introduction")

        crumb = self.breadcrumb("English · Module 1 Vocabulary", "Lesson 5 · Analogies", "Video 7")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        closes = pill("this video closes Module 1", FOCUS, size=LABEL)
        vocab = pill("the vocabulary from Lessons 1 to 4", WORD, size=LABEL)
        bridges = pill("the bridges from Videos 1 to 6", RATIO, size=LABEL)
        plus = text("+", BODY, MUTED)
        VGroup(closes, VGroup(vocab, plus, bridges).arrange(RIGHT, buff=0.4)).arrange(DOWN, buff=0.8).move_to(DOWN * 0.1)
        self.no_overlap(crumb, closes, vocab, bridges)
        self.validator.check_in_frame(VGroup(crumb, closes, vocab, bridges))

        n = self.narrate(
            id="intro_01",
            text="This video closes module one. It pulls together the vocabulary from lessons one to four, and the bridges "
                 "from videos one to six.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.at_word(n, "closes")
        self.play(FadeIn(closes, shift=UP * 0.1))
        self.at_word(n, "vocabulary")
        self.play(FadeIn(vocab, shift=UP * 0.1))
        self.at_word(n, "bridges")
        self.play(FadeIn(plus), FadeIn(bridges, shift=UP * 0.1))
        self.wait_for_narration(n)

        title = fitted_text("Analogy Question-Solving Techniques", SAFE_W, 64, INK, BOLD)
        underline = Line(LEFT, RIGHT, color=RATIO, stroke_width=5).set_width(title.width * 0.6)
        VGroup(title, underline).arrange(DOWN, buff=0.2).move_to(UP * 0.2)
        n = self.narrate(
            id="intro_02",
            text="This is the last video of lesson five: analogy question-solving techniques.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(VGroup(closes, vocab, plus, bridges), shift=UP * 0.3))
        self.at_word(n, "analogy")
        self.play(Write(title), run_time=1.1)
        self.play(GrowFromCenter(underline))
        self.wait_for_narration(n)

        goals = [
            ("Solve any analogy question with a fixed method", BAD),
            ("Handle vocabulary-heavy analogies: Lessons 1 and 2, plus bridges", GOOD),
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
            text="By the end of this video, you'll solve any analogy question with a fixed method, and handle "
                 "vocabulary-heavy analogies by combining lessons one and two with bridges.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(underline), ReplacementTransform(title, small_title), run_time=0.8)
        self.play(FadeIn(objectives[0]), FadeIn(heading))
        for row_, spoken in zip(rows, ["solve", "handle"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row_, shift=RIGHT * 0.2), run_time=0.5)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_intro")

    # ================================================= 1. HOOK ==========

    def hook(self):
        self.scene_start("S01_hook", title="Hook")

        options, key, traps = HOOK_Q
        card = self.timer_card()
        q = OptionQuestion("?", options, key, traps)
        opts = q.rows.copy().arrange_in_grid(rows=2, cols=2, buff=(1.4, 0.4), cell_alignment=LEFT)
        notes = VGroup(pill("it mixes vocabulary and relationships", RATIO, size=SMALL),
                       pill("exactly what the method is for", GOOD, size=SMALL)).arrange(RIGHT, buff=0.4)
        opts.next_to(card, DOWN, buff=0.7)
        notes.next_to(opts, DOWN, buff=0.6)
        self.no_overlap(card, opts, notes)
        self.validator.check_in_frame(VGroup(card, opts, notes))

        n = self.narrate(
            id="hook_01",
            text="You have forty seconds. Obstinate is to flexible, as what is to what?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "forty")
        self.play(FadeIn(card[0]), FadeIn(card[1][0]))
        self.at_word(n, "Obstinate")
        self.play(FadeIn(card[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_02",
            text="Generous, stingy; brave, bold; rich, wealthy; or tired, sleepy? This one mixes vocabulary and "
                 "relationships, and it's exactly the kind of question the method is for.",
            voice="default",
            subtitle=True,
            pause_after=3.0,
        )
        for row, spoken in zip(opts, ["Generous", "brave", "rich", "tired"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=UP * 0.15), run_time=0.35)
        self.at_word(n, "mixes")
        self.play(FadeIn(notes[0], shift=UP * 0.1))
        self.at_word(n, "method")
        self.play(FadeIn(notes[1], shift=UP * 0.1))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        self.clear_stage()
        self.scene_end("S01_hook")

    # ============================================== 2. CONCEPT ==========

    def concept(self):
        self.scene_start("S02_concept", title="The Concept")

        head = pill("the method:  B-R-O-T", FOCUS, size=BODY)
        head.move_to(UP * (CARD_TOP - head.height / 2))
        rows = VGroup(*[VGroup(pill(k, c, size=BODY), text(name, LABEL, c, BOLD),
                               fitted_text(q, 6.8, LABEL, INK)).arrange(RIGHT, buff=0.35)
                        for (k, name, c), q in zip(CHECKS, [
                            "a short sentence from A to B, in the given order",
                            "add level, function or direction until one option fits",
                            "the answer's first word plays the same role as A",
                            "same relationship type, same part of speech"])])
        rows.arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        fit_within(rows, SAFE_W, SAFE_H - head.height - 1.6)
        rows.next_to(head, DOWN, buff=0.45)
        self.no_overlap(head, rows)
        self.validator.check_in_frame(VGroup(head, rows))

        n = self.narrate(
            id="concept_01",
            text="The method is B, R, O, T.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "method")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_02",
            text="B is bridge: a short sentence from A to B, in the given order. R is refine: add level, function or "
                 "direction, until only one option fits. O is order: check that the answer's first word plays the same "
                 "role as A. And T is type check: confirm that the answer is the same relationship type, and the same "
                 "part of speech.",
            voice="default",
            subtitle=True,
        )
        for r, (spoken, occ) in zip(rows, [("bridge", 1), ("refine", 1), ("order", 2), ("type", 1)]):
            self.at_word(n, spoken, occurrence=occ)
            self.play(FadeIn(r, shift=RIGHT * 0.2), run_time=0.45)
        self.wait_for_narration(n)

        # Meaning analogies: the bridge is a vocabulary question.
        about = pill("analogy about word MEANING: synonym, antonym, degree", WORD, size=LABEL)
        vocab = pill("the bridge is a VOCABULARY question", RATIO, size=LABEL)
        need = text("you need Lesson 1 and Lesson 2 knowledge", LABEL, MUTED)
        b1 = text("“Obstinate is the opposite of flexible.”", BODY, INK, t2c={"is the opposite of": RATIO})
        look = pill("so look for an ANTONYM pair", GOOD, size=LABEL)
        block = VGroup(about, vocab, need, b1, look).arrange(DOWN, buff=0.4)
        fit_within(block, SAFE_W, SAFE_H - 1.4)
        block.move_to(UP * 0.3)
        self.validator.check_in_frame(block)
        assert RELATION["Obstinate : Flexible"] == "antonym"
        n = self.narrate(
            id="concept_03",
            text="When the analogy is about word meaning, synonym, antonym or degree, the bridge is a vocabulary question. "
                 "You need lesson one and lesson two knowledge. Obstinate is the opposite of flexible. Then you look for "
                 "an antonym pair.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(VGroup(head, rows)))
        self.at_word(n, "meaning")
        self.play(FadeIn(about, shift=DOWN * 0.1))
        self.at_word(n, "vocabulary")
        self.play(FadeIn(vocab, shift=UP * 0.1))
        self.at_word(n, "knowledge")
        self.play(FadeIn(need, shift=UP * 0.1))
        self.at_word(n, "Obstinate")
        self.play(FadeIn(b1, shift=UP * 0.1))
        self.at_word(n, "antonym", occurrence=2)
        self.play(FadeIn(look, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_concept")

    # ======================================== 3. WHY YOU NEED IT ==========

    def why_you_need_it(self):
        self.scene_start("S03_why", title="Why You Need It")

        time_ = pill("an analogy: 30 to 40 seconds", RATIO, size=BODY)
        fixed = pill("a fixed method stops you chasing “related” options", GOOD, size=LABEL)
        lost = text("…which is where time and marks go", LABEL, MUTED)
        group = VGroup(time_, VGroup(fixed, lost).arrange(DOWN, buff=0.2)).arrange(DOWN, buff=0.9)
        fit_width(group, SAFE_W).move_to(UP * 0.3)
        self.validator.check_in_frame(group)

        n = self.narrate(
            id="why_01",
            text="Analogies should take thirty to forty seconds. A fixed method stops you from chasing related options, "
                 "which is where time and marks go.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "thirty")
        self.play(FadeIn(time_, shift=DOWN * 0.1))
        self.at_word(n, "fixed")
        self.play(FadeIn(fixed, shift=UP * 0.1))
        self.at_word(n, "marks")
        self.play(FadeIn(lost, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_why")

    # ============================================== 4. ANALOGY ==========

    def analogy(self):
        self.scene_start("S04_analogy", title="The Analogy")

        items = VGroup(*[VGroup(text("✓", BODY, GOOD), pill(k, c, size=LABEL), text(name, LABEL, INK))
                         .arrange(RIGHT, buff=0.3) for k, name, c in CHECKS]).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        clip = self.card(VGroup(text("PRE-FLIGHT CHECKLIST", SMALL, RATIO, BOLD), items)
                         .arrange(DOWN, buff=0.35, aligned_edge=LEFT))
        every = pill("the same checklist before EVERY flight, however experienced", MUTED, size=SMALL)
        yours = pill("B-R-O-T: your checklist for every analogy", FOCUS, size=LABEL)
        block = VGroup(clip, every, yours).arrange(DOWN, buff=0.45)
        fit_within(block, SAFE_W, SAFE_H - 1.4)
        block.move_to(UP * 0.3)
        self.no_overlap(clip, every, yours)
        self.validator.check_in_frame(block)

        n = self.narrate(
            id="analogy_01",
            text="Pilots run the same checklist before every flight, however experienced they are. B, R, O, T is your "
                 "pre-flight checklist for every analogy.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "checklist", occurrence=1)
        self.play(FadeIn(clip[0]), FadeIn(clip[1][0]), *[FadeIn(i[1:]) for i in items])
        self.at_word(n, "every", occurrence=1)
        self.play(LaggedStart(*[FadeIn(i[0], scale=1.4) for i in items], lag_ratio=0.3), FadeIn(every, shift=UP * 0.1))
        self.at_word(n, "pre-flight")
        self.play(FadeIn(yours, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_analogy")

    # ======================================== 5-7. WORKED EXAMPLES ==========

    def example_sock(self):
        self.scene_start("S05_ex_sock", title="Worked Example 1")
        self.play(self.pin(self.check_pin()))

        line, chips, b2, answer = self.brot_example("Glove", "Hand", "Sock", "foot",
                                                    [("B", "a glove covers and protects a hand")],
                                                    "A sock covers and protects a foot.")

        n = self.narrate(
            id="ex1_01",
            text="Glove is to hand, as sock is to what? B, the bridge: a glove covers and protects a hand. So a sock covers "
                 "and protects a foot.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Glove", occurrence=1)
        self.play(FadeIn(line, shift=DOWN * 0.1))
        self.at_word(n, "B")
        self.play(FadeIn(chips[0], shift=RIGHT * 0.2), self.light("B"))
        self.at_word(n, "foot")
        self.play(FadeIn(b2, shift=RIGHT * 0.2), ReplacementTransform(line[6], answer))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_ex_sock")

    def example_starving(self):
        self.scene_start("S06_ex_starving", title="Worked Example 2")

        line, chips, b2, answer = self.brot_example("Illiterate", "Education", "Starving", "food",
                                                    [("B", "illiterate = lacking education")],
                                                    "Starving = lacking food.")

        n = self.narrate(
            id="ex2_01",
            text="Illiterate is to education, as starving is to what? B, the bridge: illiterate means lacking education. So "
                 "starving means lacking food.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Illiterate", occurrence=1)
        self.play(FadeIn(line, shift=DOWN * 0.1))
        self.at_word(n, "B")
        self.play(FadeIn(chips[0], shift=RIGHT * 0.2), self.light("B"))
        self.at_word(n, "food")
        self.play(FadeIn(b2, shift=RIGHT * 0.2), ReplacementTransform(line[6], answer))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_ex_starving")

    def example_apprentice(self):
        self.scene_start("S07_ex_apprentice", title="Worked Example 3")

        line, chips, b2, answer = self.brot_example(
            "Novice", "Expert", "Apprentice", "master",
            [("B", "a novice is a beginner; an expert is skilled"), ("R", "the skilled form of the SAME role")],
            "An apprentice becomes a master.")

        n = self.narrate(
            id="ex3_01",
            text="Novice is to expert, as apprentice is to what? B, the bridge: a novice is a beginner; an expert is "
                 "skilled. R, refine: the skilled form of the same role. So an apprentice becomes a master.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Novice", occurrence=1)
        self.play(FadeIn(line, shift=DOWN * 0.1))
        self.at_word(n, "B")
        self.play(FadeIn(chips[0], shift=RIGHT * 0.2), self.light("B"))
        self.at_word(n, "R")
        self.play(FadeIn(chips[1], shift=RIGHT * 0.2), self.light("R"))
        self.at_word(n, "master")
        self.play(FadeIn(b2, shift=RIGHT * 0.2), ReplacementTransform(line[6], answer))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S07_ex_apprentice")

    # ================================================ 8. RULES ==========

    def rules(self):
        self.scene_start("S08_rules", title="Rules")
        self.play(self.unpin())

        strip = self.method_strip()
        fit_width(strip, SAFE_W)
        strip.move_to(UP * (CARD_TOP - strip.height / 2))
        table = self.table_rows(["Check", "Catches"], [
            ["B", "options related by a different link"],
            ["R", "general vs specific; function traps"],
            ["O", "reversed pairs"],
            ["T", "wrong type; wrong part of speech"],
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
            text="The full method: read, then B, R, O, T, then confirm. B catches options related by a different link. R "
                 "catches general against specific, and function traps. O catches reversed pairs. And T catches the "
                 "wrong type, or the wrong part of speech.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "read")
        self.play(LaggedStart(*[FadeIn(c, shift=RIGHT * 0.1) for c in strip], lag_ratio=0.1))
        self.play(FadeIn(board[0]), FadeIn(table[0]))
        for row, spoken in zip(table[1:], ["link", "general", "reversed", "type"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.45)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S08_rules")

    # ============================================== 9. PROCESS ==========

    def process(self):
        self.scene_start("S09_process", title="The Process: 40 Seconds")

        scale = 0.28                                          # units per second
        cols = [WORD, BAD, RATIO, GOOD]
        segs = VGroup(*[Rectangle(width=(e - s_) * scale, height=0.55, color=c, fill_color=c, fill_opacity=0.35)
                        for (s_, e, _), c in zip(TIMELINE, cols)]).arrange(RIGHT, buff=0)
        segs.move_to(UP * 1.4)
        ticks = VGroup(*[text(f"{t} s", SMALL, MUTED).next_to(segs, DOWN, buff=0.15).set_x(segs.get_left()[0] + t * scale)
                         for t in [0, 10, 25, 35, 40]])
        labels = VGroup(*[fitted_text(lab, 7.4, LABEL, c) for (_, _, lab), c in zip(TIMELINE, cols)])
        rows = VGroup(*[VGroup(pill(f"{s_}–{e} s", c, size=SMALL), lab).arrange(RIGHT, buff=0.3)
                        for (s_, e, _), c, lab in zip(TIMELINE, cols, labels)]).arrange(DOWN, buff=0.25,
                                                                                        aligned_edge=LEFT)
        rows.next_to(ticks, DOWN, buff=0.5)
        assert TIMELINE[0][0] == 0 and TIMELINE[-1][1] == 40 and all(a[1] == b[0] for a, b in zip(TIMELINE, TIMELINE[1:]))
        self.no_overlap(VGroup(segs, ticks), rows)
        self.validator.check_in_frame(VGroup(segs, ticks, rows))

        n = self.narrate(
            id="process_01",
            text="Here's the forty-second budget. From zero to ten seconds, bridge from A to B. From ten to twenty-five, "
                 "test the options, and refine if two survive. From twenty-five to thirty-five, run the order and type "
                 "check. From thirty-five to forty, confirm; and guess only after at least one elimination.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "budget")
        self.play(FadeIn(ticks))
        for seg, row, (spoken, occ) in zip(segs, rows, [("zero", 1), ("ten", 2), ("twenty-five", 2),
                                                         ("thirty-five", 2)]):
            self.at_word(n, spoken, occurrence=occ)
            self.play(GrowFromEdge(seg, LEFT), FadeIn(row, shift=RIGHT * 0.2), run_time=0.5)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S09_process")

    # ========================================== 10. HOOK, SOLVED ==========

    def hook_solved(self):
        self.scene_start("S10_hook_solved", title="Hook, Solved")
        self.play(self.pin(self.check_pin()))

        options, key, traps = HOOK_Q
        cx, w = self.free_area()
        card = self.timer_card()
        b1 = text("“Obstinate is the opposite of flexible.”", LABEL, INK, t2c={"is the opposite of": RATIO})
        need = pill("need: an ANTONYM pair", GOOD, size=SMALL)
        notes = VGroup(b1, need).arrange(RIGHT, buff=0.4)
        fit_width(notes, w - 0.8)
        notes.next_to(card, DOWN, buff=0.3).to_edge(LEFT, buff=SAFE + 0.6)
        q = OptionQuestion("?", options, key, traps, word_size=LABEL)
        b2 = text("“Generous is the opposite of stingy.”", LABEL, INK, t2c={"is the opposite of": RATIO})
        body = VGroup(q.rows, b2).arrange(DOWN, buff=0.35, aligned_edge=LEFT)
        fit_height(body, notes.get_bottom()[1] - 0.3 - (BOTTOM_Y + 0.6))
        body.next_to(notes, DOWN, buff=0.3).to_edge(LEFT, buff=SAFE + 0.6)
        self.no_overlap(card, notes, q.rows, b2)
        self.no_overlap(card, self.pinned)
        self.no_overlap(notes, self.pinned)
        self.validator.check_in_frame(VGroup(card, notes, body))

        n = self.narrate(
            id="solved_01",
            text="Let's solve the hook. Read: obstinate is to flexible. B, the bridge: obstinate is the opposite of "
                 "flexible. So we need an antonym pair.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(card), FadeIn(q.rows))
        self.at_word(n, "Read")
        self.play(Indicate(card[1][1][:3], color=WORD, scale_factor=1.05))
        self.at_word(n, "B")
        self.play(FadeIn(b1, shift=RIGHT * 0.2), self.light("B"))
        self.at_word(n, "antonym")
        self.play(FadeIn(need, shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_02",
            text="Eliminate with T. Brave, bold and rich, wealthy are synonyms. Tired, sleepy are near-synonyms.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Eliminate")
        self.play(self.light("T"))
        self.at_word(n, "Brave")
        self.play(*q.strike("b")[1], *q.strike("c")[1])
        self.at_word(n, "Tired")
        self.play(*q.strike("d")[1])
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_03",
            text="Confirm: generous is the opposite of stingy. That's the answer.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Confirm")
        self.play(FadeIn(b2, shift=UP * 0.1))
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
            ["Meaning pairs", "B with vocabulary; T for synonym vs antonym"],
            ["Choose the pair", "B, then O"],
            ["Odd pair out", "B for every pair, then R"],
            ["Double-meaning words", "fix the meaning first (Video 4)"],
        ], [4.6, 7.2], size=LABEL)
        board = self.card(table, width=SAFE_W - 0.2).move_to(UP * 0.4)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="patterns_01",
            text="Which checks come first? For meaning pairs: B with vocabulary, and T for synonym against antonym. For "
                 "choose the pair: B, then O. For odd pair out: B for every pair, then R. And for double-meaning words: "
                 "fix the meaning first, as in video four.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "first", occurrence=1)
        self.play(FadeIn(board[0]), FadeIn(table[0]))
        for row, spoken in zip(table[1:], ["meaning", "choose", "odd", "double-meaning"]):
            self.at_word(n, spoken, occurrence=1)
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.45)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S11_patterns")

    # ======================================== 12. COMMON MISTAKES ==========

    def common_mistakes(self):
        self.scene_start("S12_mistakes", title="Common Mistakes")

        card_w = ZONE_W - 0.3
        pairs = [
            (self.verdict_card(False, "Skipping the bridge: matching by “feel”", card_w),
             self.verdict_card(True, "Always write the bridge", card_w)),
            (self.verdict_card(False, "Forgetting the order check", card_w),
             self.verdict_card(True, "First word: same role as A", card_w)),
            (self.verdict_card(False, "Not knowing the vocabulary", card_w),
             self.verdict_card(True, "Revise Lessons 1 and 2", card_w)),
        ]
        for (wrong, right), yy in zip(pairs, [1.6, 0.05, -1.5]):
            wrong.move_to(LEFT_ZONE + UP * yy)
            right.move_to(RIGHT_ZONE + UP * yy)
        header = pill("3 mistakes", BAD, size=LABEL).move_to(UP * (CARD_TOP - 0.3))
        self.validator.check_in_frame(VGroup(header, *[c for p in pairs for c in p]))

        n = self.narrate(
            id="mistakes_01",
            text="Three common mistakes. The first is skipping the bridge, and matching by feel. The second is forgetting "
                 "the order check. The third is not knowing the vocabulary: revise lessons one and two.",
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
        (("Candid", "Evasive", "?"), PRACTICE_Q1[0], PRACTICE_Q1[1], "an antonym pair;  the others are synonym pairs"),
        (("Paper", "Ream", "?"), ["Book : Library", "Soldier : Army", "Both (a) and (b)", "Neither"], "c",
         "item → a collection of it;  both keep that relationship and order"),
        (("Cup", "Coffee", "Bowl"), ["dish", "soup", "spoon", "food"], "b",
         "holds a specific liquid meal;  (d) food is too general"),
    ]

    def practice(self):
        self.scene_start("S13_practice", title="Practice Questions")

        lines = VGroup(*[VGroup(VGroup(pill(str(i + 1), FOCUS, size=SMALL), analogy_line(*abc, size=LABEL))
                                .arrange(RIGHT, buff=0.35),
                                text("   ".join(f"({l}) {o}" for l, o in zip("abcd", opts)), LABEL, INK))
                         .arrange(DOWN, buff=0.2, aligned_edge=LEFT)
                         for i, (abc, opts, *_r) in enumerate(self.PRACTICE)])
        lines.arrange(DOWN, buff=0.45, aligned_edge=LEFT)
        board = self.card(lines, color=FOCUS)
        fit_within(board, SAFE_W, SAFE_H - 1.2)
        board.move_to(UP * 0.4)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="practice_01",
            text="Your turn, forty seconds each. One: candid is to evasive, as what is to what? Frank, honest; brief, "
                 "short; lucid, obscure; or calm, quiet? Two: paper is to ream, as what is to what? Book, library; "
                 "soldier, army; both of them; or neither? Three: cup is to coffee, as bowl is to what? Dish, soup, "
                 "spoon, or food?",
            voice="default",
            subtitle=True,
            pause_after=12.0,
        )
        self.play(FadeIn(board[0]))
        for ln, (spoken, first_option) in zip(lines, [("candid", "Frank"), ("paper", "Book"), ("cup", "Dish")]):
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
        for (a, b, c), opts, key, why in self.PRACTICE:
            ans = opts["abcd".index(key)]
            if c != "?":
                top = analogy_line(a, b, c, ans, size=LABEL)
            elif " : " in ans:
                top = analogy_line(a, b, *ans.split(" : "), size=LABEL)
                top[4].set_color(GOOD)
            else:
                top = VGroup(analogy_line(a, b, "?", size=LABEL)[:3], text("→", LABEL, MUTED),
                             pill(f"({key}) {ans}", GOOD, size=LABEL)).arrange(RIGHT, buff=0.3)
            rows.add(VGroup(top, text(why, SMALL, RATIO)).arrange(DOWN, buff=0.18, aligned_edge=LEFT))
        rows.arrange(DOWN, buff=0.5, aligned_edge=LEFT)
        fit_within(rows, SAFE_W, SAFE_H - 1.2)
        rows.move_to(UP * 0.3)
        self.validator.check_in_frame(rows)

        n = self.narrate(
            id="answers_01",
            text="One: lucid, obscure: an antonym pair. The others are synonym pairs. Two: both. An item, then a "
                 "collection of it; book, library and soldier, army both keep that relationship and order. Three: soup. A "
                 "bowl holds a specific liquid meal; food is too general.",
            voice="default",
            subtitle=True,
        )
        for r, (spoken, why) in zip(rows, [("lucid", "synonym"), ("both", "collection"), ("soup", "holds")]):
            self.at_word(n, spoken, occurrence=1)
            self.play(FadeIn(r[0], shift=RIGHT * 0.2), run_time=0.5)
            self.at_word(n, why)
            self.play(FadeIn(r[1], shift=LEFT * 0.1), run_time=0.4)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S14_answers")

    # ================================================ 15. RECAP ==========

    def recap(self):
        self.scene_start("S15_recap", title="Recap Card: Lesson 5 Method")

        card, table = self.recap_card("Recap Card: Lesson 5 Method", [
            ["Method", "B → R → O → T → CONFIRM"],
            ["Meaning analogies", "use Lessons 1 and 2 vocabulary for the bridge"],
            ["Time", "30–40 seconds"],
        ])
        card.move_to(UP * 0.2)
        self.validator.check_in_frame(card)

        n = self.narrate(
            id="recap_01",
            text="To recap the lesson five method: B, R, O, T, then confirm. For meaning analogies, use the vocabulary from "
                 "lessons one and two for the bridge. And the target time is thirty to forty seconds.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(card[0]), FadeIn(table[0]))
        for row, spoken in zip(table[1:], ["method", "meaning", "time"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.45)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S15_recap")

    # ================================================= 16. NEXT ==========

    def next_video(self):
        self.scene_start("S16_next", title="Next")

        todo = VGroup(pill("Lesson 5 Quiz", FOCUS, size=LABEL), pill("Cheat Sheet", WORD, size=LABEL))\
            .arrange(RIGHT, buff=0.6)
        done = pill("Module 1: Vocabulary  ✓", GOOD, size=BODY)
        nxt = VGroup(pill("Next:  Module 2, Grammar", FOCUS, size=BODY), text("Lesson 6: Prepositions", LABEL, MUTED))\
            .arrange(DOWN, buff=0.2)
        VGroup(todo, done, nxt).arrange(DOWN, buff=0.6).move_to(UP * 0.1)
        self.no_overlap(todo, done, nxt)
        self.validator.check_in_frame(VGroup(todo, done, nxt))

        n = self.narrate(
            id="next_01",
            text="Take the lesson five quiz, and keep the cheat sheet. That completes module one. Module two, grammar, "
                 "begins with lesson six: prepositions.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "quiz")
        self.play(FadeIn(todo[0], shift=UP * 0.1))
        self.at_word(n, "cheat")
        self.play(FadeIn(todo[1], shift=UP * 0.1))
        self.at_word(n, "completes")
        self.play(FadeIn(done, scale=1.1))
        self.at_word(n, "grammar")
        self.play(FadeIn(nxt[0], scale=1.05))
        self.at_word(n, "prepositions")
        self.play(FadeIn(nxt[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S16_next")

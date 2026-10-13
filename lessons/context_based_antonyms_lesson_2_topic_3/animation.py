"""
animation.py for the LMS video generator.

Course : C-CAT - Section A - English
Module : Module 1 - Vocabulary
Lesson : Lesson 2 - Antonyms
Video  : 03 - Context-Based Antonyms (Video 3 of 7)

Source script:
  C:\\Users\\User\\Downloads\\C-CAT_SectionA_Module1_English\\English\\Module 1 - Vocabulary\\
  Lesson 2 - Antonyms\\03 - Context-Based Antonyms.pdf

Built on the golden-reference pattern:
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``;
  * layouts stacked with next_to and guarded with ``no_overlap``; nothing is
    ever animated onto or into another box.

Opening: a later video of Lesson 2, so no spoken welcome. The module > lesson >
video trail is shown on screen (silent), then a one-line recap of Video 2 (the
three types) and Lesson 1 Video 3 (the sentence selects the meaning), the
title and the objectives.

Pinned panel: the context-antonym method (meaning HERE -> its opposite ->
other meanings' opposites are traps -> confirm "not X, but Y") stays in the
top-right corner from Worked Example 1 through Hook, Solved, and the step in
use lights up each time. Content in those scenes goes in the free area beside
it (``place_free`` / ``no_overlap`` against the panel).

Core visuals: sense tables (each meaning of "light" / "fair" with its own
opposite, from ``SENSES``); a road junction for the analogy; the contrast
substitution, where the sentence is re-written with the opposite in place
(``swapped`` asserts the word is found).
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


def sentence_text(sentence, word, color=WORD, size=BODY, width=None):
    """A quoted sentence with ``word`` highlighted (whole-word match)."""
    t = text(f"“{sentence}”", size, INK, t2c={rf"\b{re.escape(word)}\b": color})
    return fit_width(t, width or SAFE_W - 1.2)


def swapped(sentence, word, replacement):
    """The sentence with ``word`` replaced (the contrast-substitution test)."""
    out, n = re.subn(rf"\b{re.escape(word)}\b", replacement, sentence, count=1)
    assert n == 1, f"{word!r} not in {sentence!r}"
    return out


# Each meaning of a word and the opposite that belongs to it.
SENSES = {
    "light": [("weight", "heavy"), ("brightness", "dark"), ("mood", "serious")],
    "fair": [("justice", "unfair"), ("complexion (old usage)", "dark"), ("weather", "foul")],
}


class ContextBasedAntonymsVideo(LMSScene):
    lesson_title = "Context-Based Antonyms"

    def construct(self):
        self.camera.background_color = BG

        self.lesson_intro()
        self.hook()
        self.concept()
        self.why_you_need_it()
        self.analogy()
        self.example_light()
        self.example_fair()
        self.example_sound()
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

    def sentence_card(self, sentence, word, color=WORD):
        cx, w = self.free_area()
        card = self.card(sentence_text(sentence, word, color, width=w - 1.0), width=w - 0.2)
        return card.move_to(RIGHT * cx + UP * (CARD_TOP - card.height / 2))

    def method_pin(self):
        """The context-antonym method, kept in the corner while the examples use it."""
        steps = [("meaning HERE", WORD), ("its opposite", GOOD), ("other meanings' opposites = traps", BAD),
                 ("confirm: not X, but Y", SECOND)]
        rows = VGroup(*[VGroup(pill(str(i + 1), c, size=SMALL), text(t, SMALL, INK)).arrange(RIGHT, buff=0.2)
                        for i, (t, c) in enumerate(steps)])
        rows.arrange(DOWN, buff=0.18, aligned_edge=LEFT)
        return self.card(VGroup(text("method", SMALL, MUTED, BOLD), rows).arrange(DOWN, buff=0.2, aligned_edge=LEFT),
                         color=FOCUS)

    def pin_step(self, i, color=FOCUS):
        """Animation: light up step i of the pinned method card."""
        return Indicate(self.pinned[1][1][i], color=color, scale_factor=1.08)

    def context_question(self, sentence, word, options, key, traps):
        card = self.sentence_card(sentence, word)
        q = OptionQuestion(word, options, key, traps, word_size=BODY)
        q.group.next_to(card, DOWN, buff=0.45).to_edge(LEFT, buff=SAFE + 0.6)
        self.no_overlap(card, q.group)
        if getattr(self, "pinned", None) is not None:
            self.no_overlap(card, q.group, self.pinned)
        self.validator.check_in_frame(VGroup(card, q.group))
        return card, q

    def contrast_swap(self, card, sentence, word, answer):
        """The sentence re-written with the opposite in place (green)."""
        new = self.sentence_card(swapped(sentence, word, answer), answer, GOOD)
        return new, ReplacementTransform(card, new)

    def sense_table(self, word):
        rows = [[meaning, opp] for meaning, opp in SENSES[word]]
        return self.table_rows([f"“{word}” meaning", "its opposite"], rows, [5.4, 4.0], size=LABEL)

    # ========================================= 0. LESSON INTRO ==========

    def lesson_intro(self):
        self.scene_start("S00_intro", title="Lesson Introduction")

        crumb = self.breadcrumb("English · Module 1 Vocabulary", "Lesson 2 · Antonyms", "Video 3")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        types = VGroup(pill("gradable: far end", RATIO, size=LABEL), pill("complementary: other state", WORD, size=LABEL),
                       pill("relational: partner", SECOND, size=LABEL)).arrange(RIGHT, buff=0.35)
        fit_width(types, SAFE_W)
        rule = pill("Lesson 1, Video 3: the sentence selects the meaning", FOCUS, size=LABEL)
        fit_width(rule, SAFE_W)
        decides = pill("same rule: the sentence decides which OPPOSITE is correct", GOOD, size=LABEL)
        fit_width(decides, SAFE_W)
        VGroup(types, rule, decides).arrange(DOWN, buff=0.55).move_to(UP * 0.0)
        self.no_overlap(crumb, types, rule, decides)
        self.validator.check_in_frame(VGroup(crumb, types, rule, decides))

        n = self.narrate(
            id="intro_01",
            text="In video two, the type of antonym told you what the answer looks like. And in lesson one, video three, "
                 "the sentence selected a word's meaning for synonyms. The same rule applies here: the sentence decides "
                 "which opposite is correct.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.at_word(n, "type")
        self.play(LaggedStart(*[FadeIn(t, shift=UP * 0.1) for t in types], lag_ratio=0.2))
        self.at_word(n, "sentence", occurrence=1)
        self.play(FadeIn(rule, shift=UP * 0.1))
        self.at_word(n, "decides")
        self.play(FadeIn(decides, shift=UP * 0.1))
        self.wait_for_narration(n)

        title = fitted_text("Context-Based Antonyms", SAFE_W, 72, INK, BOLD)
        underline = Line(LEFT, RIGHT, color=WORD, stroke_width=5).set_width(title.width * 0.6)
        VGroup(title, underline).arrange(DOWN, buff=0.2).move_to(UP * 0.2)
        goals = [("Choose the antonym of a word's meaning IN THE GIVEN SENTENCE", WORD),
                 ("Use the contrast-substitution test to confirm", GOOD)]
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
            id="intro_02",
            text="These are context-based antonyms. By the end of this video, you'll choose the antonym of a word's meaning "
                 "in the given sentence, and use the contrast-substitution test to confirm.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(VGroup(types, rule, decides), shift=UP * 0.3))
        self.at_word(n, "context-based")
        self.play(Write(title), run_time=1.1)
        self.play(GrowFromCenter(underline))
        self.at_word(n, "By")
        self.play(FadeOut(underline), ReplacementTransform(title, small_title), run_time=0.8)
        self.play(FadeIn(objectives[0]), FadeIn(heading))
        for row_, spoken in zip(rows, ["choose", "contrast-substitution"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row_, shift=RIGHT * 0.2), run_time=0.5)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_intro")

    # ================================================= 1. HOOK ==========

    HOOK = dict(sentence="Your parcel is light. Standard delivery applies", word="light",
                options=["dark", "heavy", "dim", "serious"], key="b",
                traps={"a": "opposes brightness", "c": "opposes brightness", "d": "opposes “light-hearted”"})

    def hook(self):
        self.scene_start("S01_hook", title="Hook")

        h = self.HOOK
        app = self.card(VGroup(text("COURIER APP", SMALL, RATIO, BOLD), sentence_text(h["sentence"], h["word"]))
                        .arrange(DOWN, buff=0.2, aligned_edge=LEFT), width=SAFE_W - 0.4)
        app.move_to(UP * (CARD_TOP - app.height / 2))
        ask = pill("his parcel: the opposite label, plus a surcharge", FOCUS, size=LABEL)
        fit_width(ask, SAFE_W)
        q = OptionQuestion(h["word"], h["options"], h["key"], h["traps"])
        opts = q.rows.copy().arrange(RIGHT, buff=0.8)
        note = pill("every option is a real opposite of “light”; only one matches here", MUTED, size=SMALL)
        fit_width(note, SAFE_W)
        ask.next_to(app, DOWN, buff=0.5)
        opts.next_to(ask, DOWN, buff=0.5)
        note.next_to(opts, DOWN, buff=0.5)
        self.no_overlap(app, ask, opts, note)
        self.validator.check_in_frame(VGroup(app, ask, opts, note))

        n = self.narrate(
            id="hook_01",
            text="A courier app says: your parcel is light. Standard delivery applies. A colleague's parcel got the "
                 "opposite label, and a surcharge. What did his label say?",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(app, shift=DOWN * 0.2))
        self.at_word(n, "Standard")
        self.play(Indicate(app[1][1], color=WORD, scale_factor=1.02))
        self.at_word(n, "opposite")
        self.play(FadeIn(ask, shift=UP * 0.1))
        self.at_word(n, "What")
        self.play(Indicate(ask, color=FOCUS, scale_factor=1.05))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_02",
            text="Dark, heavy, dim, or serious? Every option is a real opposite of light. Only one matches this sentence.",
            voice="default",
            subtitle=True,
            pause_after=3.0,
        )
        for row, spoken in zip(opts, ["Dark", "heavy", "dim", "serious"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=UP * 0.15), run_time=0.35)
        self.at_word(n, "Every")
        self.play(FadeIn(note, shift=UP * 0.1))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        self.clear_stage()
        self.scene_end("S01_hook")

    # ============================================== 2. CONCEPT ==========

    def concept(self):
        self.scene_start("S02_concept", title="The Concept")

        head = pill("several meanings  →  several antonyms, one per meaning", WORD, size=LABEL)
        fit_width(head, SAFE_W)
        head.move_to(UP * (CARD_TOP - head.height / 2))
        light = self.sense_table("light")
        fair = self.sense_table("fair")
        boards = VGroup(self.card(light), self.card(fair)).arrange(RIGHT, buff=0.4, aligned_edge=UP)
        fit_width(boards, SAFE_W)
        boards.next_to(head, DOWN, buff=0.45)
        self.no_overlap(head, boards)
        self.validator.check_in_frame(VGroup(head, boards))

        n = self.narrate(
            id="concept_01",
            text="A word with several meanings has several antonyms, one for each meaning. Light can be the opposite of "
                 "heavy, for weight; dark, for brightness; or serious, as in a light comedy.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "several")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "Light")
        self.play(FadeIn(boards[0][0]), FadeIn(light[0]))
        for row, spoken in zip(light[1:], ["heavy", "dark", "serious"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.4)
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_02",
            text="Fair can oppose unfair, for justice; dark, for complexion, which is an old usage; or foul, for weather.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(boards[1][0]), FadeIn(fair[0]))
        for row, spoken in zip(fair[1:], ["unfair", "dark", "foul"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.4)
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_03",
            text="When the question gives a sentence, work out the meaning first, then the opposite of that meaning. The "
                 "other opposites will be in the options, because each is correct somewhere, just not here.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "meaning", occurrence=1)
        cap = self.caption("Meaning HERE first, then the opposite of THAT meaning", WORD)
        self.play(FadeIn(cap, shift=UP * 0.2))
        self.at_word(n, "other")
        self.play(Indicate(boards, color=BAD, scale_factor=1.02))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_concept")

    # ======================================== 3. WHY YOU NEED IT ==========

    def why_you_need_it(self):
        self.scene_start("S03_why", title="Why You Need It")

        hard = pill("the hardest antonym items: every option looks defensible", BAD, size=LABEL)
        rc = pill("RC: “opposite in meaning to X as used in the passage”", SECOND, size=LABEL)
        group = VGroup(hard, rc).arrange(DOWN, buff=0.8)
        fit_width(group, SAFE_W).move_to(UP * 0.3)
        self.no_overlap(hard, rc)
        self.validator.check_in_frame(group)

        n = self.narrate(
            id="why_01",
            text="Context antonyms are the hardest antonym items, because every option looks defensible. Reading "
                 "comprehension also asks which word is opposite in meaning to X, as used in the passage. That's the same "
                 "skill.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "hardest")
        self.play(FadeIn(hard, shift=DOWN * 0.1))
        self.at_word(n, "Reading")
        self.play(FadeIn(rc, shift=UP * 0.1))
        self.at_word(n, "same")
        link = pill("same skill", GOOD, size=SMALL).next_to(rc, DOWN, buff=0.35)
        self.play(FadeIn(link, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_why")

    # ============================================== 4. ANALOGY ==========

    def analogy(self):
        self.scene_start("S04_analogy", title="The Analogy")

        centre = LEFT * 1.5 + DOWN * 0.2
        hub = Dot(centre, radius=0.12, color=WORD)
        hub_lab = text("light", BODY, WORD, BOLD).next_to(hub, DOWN, buff=0.25)
        dirs = [UP + RIGHT * 0.2, RIGHT + DOWN * 0.1, DOWN + RIGHT * 0.6]
        roads, ends = VGroup(), VGroup()
        for (meaning, opp), d in zip(SENSES["light"], dirs):
            unit = d / np.linalg.norm(d)
            road = Line(centre - unit * 2.2, centre + unit * 2.2, color=MUTED, stroke_width=6)
            roads.add(road)
            ends.add(VGroup(pill(meaning, INK, size=SMALL).next_to(road.get_start(), -unit, buff=0.15),
                            pill(opp, BAD, size=SMALL).next_to(road.get_end(), unit, buff=0.15)))
        # Two columns: the junction on the left, the sentence note on the right. The junction
        # gets whatever width the note leaves, so their bounding boxes can never intersect.
        sentence = VGroup(pill("sentence: “parcel is light”", GOOD, size=SMALL),
                          pill("→ the WEIGHT road", GOOD, size=SMALL)).arrange(DOWN, buff=0.2)
        sentence.to_edge(RIGHT, buff=SAFE).set_y(-0.2)
        junction = VGroup(roads, ends, hub, hub_lab)
        gap = 0.4
        fit_within(junction, SAFE_W - sentence.width - gap, SAFE_H - 1.6)
        junction.next_to(sentence, LEFT, buff=gap).set_y(-0.2)
        self.no_overlap(junction, sentence)
        self.validator.check_in_frame(VGroup(roads, ends, hub, hub_lab, sentence))

        n = self.narrate(
            id="analogy_01",
            text="A word is a junction with several roads. Each road has its own opposite direction.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(hub), FadeIn(hub_lab))
        self.at_word(n, "roads")
        self.play(LaggedStart(*[Create(r) for r in roads], lag_ratio=0.2))
        self.at_word(n, "opposite")
        self.play(LaggedStart(*[FadeIn(e) for e in ends], lag_ratio=0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_02",
            text="The sentence tells you which road you're on. Turn around on that road, not on a different one.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "sentence")
        self.play(FadeIn(sentence, shift=LEFT * 0.1), roads[0].animate.set_color(GOOD))
        self.at_word(n, "Turn")
        self.play(ShowPassingFlash(roads[0].copy().set_color(GOOD).set_stroke(width=10), time_width=0.5), run_time=1.0)
        self.play(Indicate(ends[0][1], color=GOOD, scale_factor=1.2))
        self.at_word(n, "different")
        self.play(roads[1].animate.set_opacity(0.3), roads[2].animate.set_opacity(0.3),
                  ends[1].animate.set_opacity(0.3), ends[2].animate.set_opacity(0.3))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_analogy")

    # ======================================== 5-7. WORKED EXAMPLES ==========

    def example_light(self):
        self.scene_start("S05_ex_light", title="Worked Example 1")

        if getattr(self, "pinned", None) is None:
            self.play(self.pin(self.method_pin()))
        card, q = self.context_question("She has a light workload this week", "light",
                                        ["dark", "heavy", "serious", "dim"], "b",
                                        {"a": "brightness", "c": "mood", "d": "brightness"})
        here = pill("here: weight / amount", GOOD, size=SMALL).next_to(q.word, RIGHT, buff=0.4)

        n = self.narrate(
            id="ex1_01",
            text="She has a light workload this week. Here, light is about weight, or amount. Dark, heavy, serious, or dim? "
                 "The opposite is heavy.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(card, shift=DOWN * 0.2), FadeIn(q.word))
        self.at_word(n, "weight")
        self.play(FadeIn(here, shift=LEFT * 0.1), self.pin_step(0))
        self.at_word(n, "Dark")
        self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.2) for r in q.rows], lag_ratio=0.2))
        self.at_word(n, "opposite")
        self.play(*q.strike("a")[1], *q.strike("c")[1], *q.strike("d")[1], self.pin_step(2))
        self.play(*q.confirm()[1], self.pin_step(1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_ex_light")

    def example_fair(self):
        self.scene_start("S06_ex_fair", title="Worked Example 2")

        card, q = self.context_question("The judge was fair to both sides", "fair",
                                        ["dark", "biased", "ugly", "foul"], "b",
                                        {"a": "complexion (old usage)", "c": "looks", "d": "weather"})
        here = pill("here: justice", GOOD, size=SMALL).next_to(q.word, RIGHT, buff=0.4)

        n = self.narrate(
            id="ex2_01",
            text="The judge was fair to both sides. Here, fair is about justice. Dark, biased, ugly, or foul? The opposite "
                 "is biased. Dark and foul belong to other meanings of fair.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(card, shift=DOWN * 0.2), FadeIn(q.word))
        self.at_word(n, "justice")
        self.play(FadeIn(here, shift=LEFT * 0.1), self.pin_step(0))
        self.at_word(n, "Dark", occurrence=1)
        self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.2) for r in q.rows], lag_ratio=0.2))
        self.at_word(n, "opposite")
        self.play(*q.confirm()[1])
        self.at_word(n, "Dark", occurrence=2)
        self.play(*q.strike("a")[1], *q.strike("c")[1], *q.strike("d")[1], self.pin_step(2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_ex_fair")

    def example_sound(self):
        self.scene_start("S07_ex_sound", title="Worked Example 3")

        card, q = self.context_question("The team gave a sound argument", "sound",
                                        ["silent", "weak", "quiet", "sick"], "b",
                                        {"a": "the “noise” meaning", "c": "the “noise” meaning",
                                         "d": "the “healthy” meaning"})
        here = pill("here: strong, valid", GOOD, size=SMALL).next_to(q.word, RIGHT, buff=0.4)

        n = self.narrate(
            id="ex3_01",
            text="The team gave a sound argument. Silent, weak, quiet, or sick? Sound here means strong, or valid. So the "
                 "opposite is weak. Silent and quiet oppose the noise meaning, and sick opposes the healthy meaning.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(card, shift=DOWN * 0.2), FadeIn(q.word))
        self.at_word(n, "Silent", occurrence=1)
        self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.2) for r in q.rows], lag_ratio=0.2))
        self.at_word(n, "strong")
        self.play(FadeIn(here, shift=LEFT * 0.1), self.pin_step(0))
        self.at_word(n, "opposite")
        self.play(*q.confirm()[1])
        self.at_word(n, "Silent", occurrence=2)
        self.play(*q.strike("a")[1], *q.strike("c")[1])
        self.at_word(n, "sick", occurrence=2)
        self.play(*q.strike("d")[1])
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S07_ex_sound")

    # ================================================ 8. RULES ==========

    def rules(self):
        self.scene_start("S08_rules", title="Rules")

        rules = VGroup(*[VGroup(pill(str(i + 1), c, size=SMALL), fitted_text(s_, SAFE_W - 2.2, BODY, INK))
                         .arrange(RIGHT, buff=0.3) for i, (s_, c) in enumerate([
                             ("Read the sentence first; decide the meaning", WORD),
                             ("Predict the opposite of THAT meaning", SECOND),
                             ("Expect the opposites of the OTHER meanings as traps", BAD),
                             ("Confirm with a contrast: “not a light workload but a heavy one”", GOOD)])])
        rules.arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        board = self.card(rules)
        self.place_free(board, y=0.3)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="rules_01",
            text="Four rules. First, read the sentence, and decide the meaning. Second, predict the opposite of that "
                 "meaning. Third, expect the opposites of the other meanings as traps. And fourth, confirm with a "
                 "contrast: not a light workload, but a heavy one.",
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

        strip = process_strip(LABEL)
        self.place_free(strip)
        strip.set_y(CARD_TOP - strip.height / 2)
        details = VGroup(*[VGroup(pill(name, col, size=SMALL), fitted_text(s_, SAFE_W - 3.4, LABEL, INK))
                           .arrange(RIGHT, buff=0.3) for (name, col), s_ in zip(STEP_COLS.items(), [
                               "the sentence; underline the word",
                               "its meaning HERE, then the opposite",
                               "opposites that belong to other meanings",
                               "swap the answer into the sentence as a contrast"])])
        details.arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        board = self.card(details)
        self.place_free(board)
        board.next_to(strip, DOWN, buff=0.5)
        self.no_overlap(strip, board, self.pinned)
        self.validator.check_in_frame(VGroup(strip, board))

        n = self.narrate(
            id="process_01",
            text="The process. Read the sentence, and underline the word. Predict its meaning here, then the opposite. "
                 "Eliminate opposites that belong to other meanings. And confirm by swapping the answer into the sentence "
                 "as a contrast.",
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
        card, q = self.context_question(h["sentence"], h["word"], h["options"], h["key"], h["traps"])
        predict = pill("weight  →  predict: heavy", STEP_COLS["PREDICT"], size=SMALL)
        predict.next_to(q.word, RIGHT, buff=0.4)
        self.no_overlap(predict, self.pinned)
        answer = h["options"]["abcd".index(h["key"])]

        n = self.narrate(
            id="solved_01",
            text="Let's solve the hook. Read: your parcel is light. It's about weight. Predict: heavy.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(card), FadeIn(q.word), FadeIn(q.rows))
        self.at_word(n, "Read")
        self.play(Indicate(card, color=WORD, scale_factor=1.02))
        self.at_word(n, "weight")
        self.play(self.pin_step(0))
        self.at_word(n, "Predict")
        self.play(FadeIn(predict, shift=LEFT * 0.1), self.pin_step(1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_02",
            text="Eliminate. Dark and dim oppose brightness. Serious opposes the light-hearted meaning.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Eliminate")
        self.play(Indicate(q.rows, color=BAD, scale_factor=1.02))
        self.at_word(n, "Dark")
        self.play(*q.strike("a")[1], *q.strike("c")[1])
        self.at_word(n, "Serious")
        self.play(*q.strike("d")[1], self.pin_step(2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_03",
            text="Confirm: your parcel is heavy; surcharge applies. The answer is heavy.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Confirm")
        new, swap = self.contrast_swap(card, h["sentence"], h["word"], answer)
        self.play(swap, self.pin_step(3))
        self.at_word(n, "answer")
        self.play(*q.confirm()[1])
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S10_hook_solved")

    # ========================================== 11. EXAM PATTERNS ==========

    def exam_patterns(self):
        self.scene_start("S11_patterns", title="Exam Patterns and Solving Models")
        self.play(self.unpin())

        table = self.table_rows(["Pattern", "Solving model"], [
            ["Bold word in a sentence", "meaning here → its opposite → reject other meanings' opposites"],
            ["Vocabulary in context (RC)", "re-read the surrounding line before choosing"],
        ], [4.4, 7.4], size=LABEL)
        board = self.card(table, width=SAFE_W - 0.2).move_to(UP * 0.4)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="patterns_01",
            text="Two exam patterns. A bold word in a sentence: find the meaning here, then its opposite, and reject the "
                 "other meanings' opposites. And vocabulary in context, in reading comprehension: re-read the surrounding "
                 "line before choosing.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(board[0]), FadeIn(table[0]))
        for row, spoken in zip(table[1:], ["bold", "vocabulary"]):
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
            (self.verdict_card(False, "Opposite of the most COMMON meaning", card_w),
             self.verdict_card(True, "Opposite of the meaning HERE", card_w)),
            (self.verdict_card(False, "Skipping the contrast check", card_w),
             self.verdict_card(True, "“Not X, but Y” in the sentence", card_w)),
            (self.verdict_card(False, "Opposite in feeling, not in meaning", card_w),
             self.verdict_card(True, "Reverse the meaning itself", card_w)),
        ]
        for (wrong, right), yy in zip(pairs, [1.6, 0.05, -1.5]):
            wrong.move_to(LEFT_ZONE + UP * yy)
            right.move_to(RIGHT_ZONE + UP * yy)
        header = pill("3 mistakes", BAD, size=LABEL).move_to(UP * (CARD_TOP - 0.3))
        self.validator.check_in_frame(VGroup(header, *[c for p in pairs for c in p]))

        n = self.narrate(
            id="mistakes_01",
            text="Three common mistakes. The first is answering with the opposite of the word's most common meaning. The "
                 "second is skipping the contrast check. The third is choosing an option that's opposite in feeling, but "
                 "not in meaning.",
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
        ("The market remained firm despite the news", "firm", ["soft", "loose", "liquid", "weak"], "d",
         {"a": "opposes the texture meaning", "b": "texture", "c": "texture"}, "firm here: steady and strong"),
        ("He gave a flat refusal", "flat", ["hesitant", "round", "bumpy", "sharp"], "a",
         {"b": "opposes the shape meaning", "c": "opposes the shape meaning", "d": "other meaning"},
         "a flat refusal is absolute"),
        ("The room was bare", "bare", ["covered", "clothed", "furnished", "hidden"], "c",
         {"a": "other meaning", "b": "opposes the “naked” meaning", "d": "unrelated"}, "a bare room has no furniture"),
    ]

    def practice(self):
        self.scene_start("S13_practice", title="Practice Questions")

        head = pill("Choose the OPPOSITE, as used in the sentence", BAD, size=LABEL)
        lines = VGroup()
        for i, (sent, w, opts, *_r) in enumerate(self.PRACTICE):
            lines.add(VGroup(VGroup(pill(str(i + 1), FOCUS, size=SMALL), sentence_text(sent, w, size=LABEL, width=9.5))
                             .arrange(RIGHT, buff=0.3),
                             text("   ".join(f"({l}) {o}" for l, o in zip("abcd", opts)), SMALL, MUTED))
                      .arrange(DOWN, buff=0.12, aligned_edge=LEFT))
        lines.arrange(DOWN, buff=0.4, aligned_edge=LEFT)
        board = self.card(VGroup(head, lines).arrange(DOWN, buff=0.4, aligned_edge=LEFT), width=SAFE_W - 0.2,
                          color=FOCUS).move_to(UP * 0.3)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="practice_01",
            text="Your turn: choose the opposite, as used in the sentence. One: the market remained firm despite the news. "
                 "Soft, loose, liquid, or weak? Two: he gave a flat refusal. Hesitant, round, bumpy, or sharp? Three: the "
                 "room was bare. Covered, clothed, furnished, or hidden?",
            voice="default",
            subtitle=True,
            pause_after=10.0,
        )
        self.play(FadeIn(board[0]), FadeIn(head))
        for ln, (spoken, first_option) in zip(lines, [("One", "Soft"), ("Two", "Hesitant"), ("Three", "Covered")]):
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
        for sent, w, opts, key, traps, note in self.PRACTICE:
            OptionQuestion(w, opts, key, traps)            # validates key / traps
            ans = opts["abcd".index(key)]
            rows.add(VGroup(pill(w, WORD, size=LABEL), text("↔", LABEL, MUTED), pill(f"({key}) {ans}", GOOD, size=LABEL),
                            text(note, SMALL, INK)).arrange(RIGHT, buff=0.3))
        rows.arrange(DOWN, buff=0.45, aligned_edge=LEFT)
        fit_width(rows, SAFE_W).move_to(UP * 0.8)
        why = VGroup(pill("soft: texture", BAD, size=SMALL), pill("round, bumpy: shape", BAD, size=SMALL),
                     pill("clothed: the “naked” meaning", BAD, size=SMALL)).arrange(RIGHT, buff=0.3)
        fit_width(why, SAFE_W)
        why.next_to(rows, DOWN, buff=0.7)
        self.no_overlap(rows, why)
        self.validator.check_in_frame(VGroup(rows, why))

        n = self.narrate(
            id="answers_01",
            text="One: weak. Firm here means steady and strong, and soft opposes the texture meaning. Two: hesitant. A flat "
                 "refusal is absolute, and round and bumpy oppose the shape meaning. Three: furnished. A bare room has no "
                 "furniture, and clothed opposes the naked meaning.",
            voice="default",
            subtitle=True,
        )
        for r, w_, (spoken, meaning, trap) in zip(rows, why, [("weak", "steady", "soft"),
                                                              ("hesitant", "absolute", "round"),
                                                              ("furnished", "furniture", "clothed")]):
            self.at_word(n, spoken)
            self.play(FadeIn(r[:3], shift=RIGHT * 0.2), run_time=0.4)
            self.at_word(n, meaning)
            self.play(FadeIn(r[3], shift=LEFT * 0.1), run_time=0.35)
            self.at_word(n, trap)
            self.play(FadeIn(w_, shift=UP * 0.1), run_time=0.35)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S14_answers")

    # ================================================ 15. RECAP ==========

    def recap(self):
        self.scene_start("S15_recap", title="Recap Card")

        card, table = self.recap_card("Recap Card: Video 3", [
            ["Several meanings", "several antonyms, one per meaning"],
            ["Key question", "opposite of what it means HERE"],
            ["Traps", "opposites of the word's other meanings"],
            ["Confirm", "a contrast sentence: “not X but Y”"],
        ])
        card.move_to(UP * 0.2)
        self.validator.check_in_frame(card)

        n = self.narrate(
            id="recap_01",
            text="To recap. Several meanings mean several antonyms, one per meaning. The key question: the opposite of what "
                 "it means here. The traps are the opposites of the word's other meanings. And confirm with a contrast "
                 "sentence: not X but Y.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(card[0]), FadeIn(table[0]))
        for row, spoken in zip(table[1:], ["Several", "key", "traps", "confirm"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.45)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S15_recap")

    # ================================================= 16. NEXT ==========

    def next_video(self):
        self.scene_start("S16_next", title="Next")

        prefixes = VGroup(*[pill(p, c, size=BODY) for p, c in [("un-", WORD), ("in-", RATIO), ("dis-", SECOND),
                                                              ("im-", GOOD)]]).arrange(RIGHT, buff=0.5)
        liar = pill("…and where prefixes lie", BAD, size=LABEL)
        nxt = pill("Next:  Prefixes and Word Formation", FOCUS, size=LABEL)
        VGroup(prefixes, liar, nxt).arrange(DOWN, buff=0.7).move_to(UP * 0.2)
        self.no_overlap(prefixes, liar, nxt)
        self.validator.check_in_frame(VGroup(prefixes, liar, nxt))

        n = self.narrate(
            id="next_01",
            text="Many antonyms are built by adding a prefix. Video four shows which prefix goes where, and where prefixes "
                 "lie.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "prefix")
        self.play(LaggedStart(*[FadeIn(p, shift=UP * 0.1) for p in prefixes], lag_ratio=0.2))
        self.at_word(n, "Video")
        self.play(FadeIn(nxt, scale=1.05))
        self.at_word(n, "lie")
        self.play(FadeIn(liar, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S16_next")

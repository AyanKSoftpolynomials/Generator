"""
animation.py for the LMS video generator.

Course : C-CAT - Section A - English
Module : Module 1 - Vocabulary
Lesson : Lesson 1 - Synonyms
Video  : 03 - Context-Based Synonyms (Video 3 of 6)

Source script:
  C:\\Users\\User\\Downloads\\C-CAT_SectionA_Module1_English\\English\\Module 1 - Vocabulary\\
  Lesson 1 - Synonyms\\03 - Context-Based Synonyms.pdf

Built on the golden-reference pattern:
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``.

Opening: a later video of Lesson 1, so no spoken welcome. The module > lesson >
video trail is shown on screen (silent), then a one-line recap of Video 2
(its four dimension chips), the line about today's topic, the title and the
objectives.

Core visuals: the question word highlighted inside its sentence; a "meaning
fan" for polysemous words; ``OptionQuestion`` cards with each trap tagged by
the meaning it came from; and the substitution test, where the sentence is
re-written with the answer in place (``swapped`` asserts the word is found).
Layouts are stacked with next_to and guarded with ``no_overlap``.

Section map (script heading -> scene):
  S00 Intro (trail + continuity)     S09 The Process
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

import re


def sentence_text(sentence, word, color=WORD, size=BODY, width=None):
    """A quoted sentence with ``word`` highlighted (whole-word match)."""
    t = text(f"“{sentence}”", size, INK, t2c={rf"\b{re.escape(word)}\b": color})
    return fit_width(t, width or SAFE_W - 1.2)


def swapped(sentence, word, replacement):
    """The sentence with ``word`` replaced by ``replacement`` (the substitution test)."""
    out, n = re.subn(rf"\b{re.escape(word)}\b", replacement, sentence, count=1)
    assert n == 1, f"{word!r} not in {sentence!r}"
    return out


class ContextBasedSynonymsVideo(LMSScene):
    lesson_title = "Context-Based Synonyms"

    def construct(self):
        self.camera.background_color = BG

        self.lesson_intro()
        self.hook()
        self.concept()
        self.why_you_need_it()
        self.analogy()
        self.example_sound()
        self.example_launch()
        self.example_bright()
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

    def context_question(self, sentence, word, options, key, traps):
        """Sentence card at the top, the options underneath on the left. Returns (card, question)."""
        card = self.sentence_card(sentence, word)
        q = OptionQuestion(word, options, key, traps, word_size=BODY)
        q.group.next_to(card, DOWN, buff=0.45).to_edge(LEFT, buff=SAFE + 0.6)
        self.no_overlap(card, q.group)
        if getattr(self, "pinned", None) is not None:
            self.no_overlap(card, q.group, self.pinned)
        self.validator.check_in_frame(VGroup(card, q.group))
        return card, q

    def substitution(self, card, sentence, word, answer):
        """Animation: the sentence card re-written with the answer in place (green)."""
        new = self.sentence_card(swapped(sentence, word, answer), answer, GOOD)
        return new, ReplacementTransform(card, new)

    # ========================================= 0. LESSON INTRO ==========
    # Purpose: silent trail, a one-line recap of Video 2 (its four dimension
    # chips), today's topic, the objectives.

    def lesson_intro(self):
        self.scene_start("S00_intro", title="Lesson Introduction")

        crumb = self.breadcrumb("English · Module 1 Vocabulary", "Lesson 1 · Synonyms", "Video 3")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        dims = VGroup(*[pill(d, c, size=LABEL) for d, c in [("degree", RATIO), ("connotation", "#F48FB1"),
                                                           ("register", SECOND), ("collocation", FOCUS)]])
        dims.arrange(RIGHT, buff=0.4).move_to(UP * 0.6)
        fit_width(dims, SAFE_W)
        first = pill("but first: the RIGHT meaning of the word", WORD, size=LABEL).move_to(DOWN * 1.0)
        self.no_overlap(crumb, dims, first)
        self.validator.check_in_frame(VGroup(crumb, dims, first))

        n = self.narrate(
            id="intro_01",
            text="In video two, you compared near-synonyms on four dimensions: degree, connotation, register and "
                 "collocation.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        for chip, spoken in zip(dims, ["degree", "connotation", "register", "collocation"]):
            self.at_word(n, spoken)
            self.play(FadeIn(chip, shift=UP * 0.15), run_time=0.35)
        self.wait_for_narration(n)

        title = fitted_text("Context-Based Synonyms", SAFE_W, 72, INK, BOLD)
        underline = Line(LEFT, RIGHT, color=WORD, stroke_width=5).set_width(title.width * 0.6)
        VGroup(title, underline).arrange(DOWN, buff=0.2).move_to(UP * 0.2)
        n = self.narrate(
            id="intro_02",
            text="But before any of that, you need the right meaning of the word, and many words have several. Today: "
                 "context-based synonyms.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "right")
        self.play(FadeIn(first, shift=UP * 0.1))
        self.at_word(n, "Today")
        self.play(FadeOut(VGroup(dims, first), shift=UP * 0.3))
        self.play(Write(title), run_time=1.1)
        self.play(GrowFromCenter(underline))
        self.wait_for_narration(n)

        goals = [
            ("Choose a synonym by its meaning in the sentence, not its most common meaning", WORD),
            ("Use the substitution test to confirm the answer", GOOD),
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
            text="By the end of this video, you'll choose a synonym by its meaning in the given sentence, not its most "
                 "common meaning, and you'll use the substitution test to confirm the answer.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(underline), ReplacementTransform(title, small_title), run_time=0.8)
        self.play(FadeIn(objectives[0]), FadeIn(heading))
        for row_, spoken in zip(rows, ["choose", "substitution"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row_, shift=RIGHT * 0.2), run_time=0.5)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_intro")

    # ================================================= 1. HOOK ==========

    HOOK = dict(sentence="Board to address shareholder complaints at Friday meeting", word="address",
                options=["lecture", "locate", "label", "tackle"], key="d",
                traps={"a": "“address” as a speech", "b": "“address” as a location", "c": "addressing an envelope"})

    def hook(self):
        self.scene_start("S01_hook", title="Hook")

        h = self.HOOK
        alert = VGroup(text("NEWS ALERT", SMALL, BAD, BOLD), sentence_text(h["sentence"], h["word"]))\
            .arrange(DOWN, buff=0.25, aligned_edge=LEFT)
        phone = self.card(alert, width=SAFE_W - 0.4)
        phone.move_to(UP * (CARD_TOP - phone.height / 2))
        q = OptionQuestion(h["word"], h["options"], h["key"], h["traps"])
        opts = q.rows.copy().arrange(RIGHT, buff=0.8)
        note = pill("every option is a real meaning of “address” somewhere; only one fits here", FOCUS, size=SMALL)
        fit_width(note, SAFE_W)
        opts.next_to(phone, DOWN, buff=0.9)
        note.next_to(opts, DOWN, buff=0.7)
        self.no_overlap(phone, opts, note)
        self.validator.check_in_frame(VGroup(phone, opts, note))

        n = self.narrate(
            id="hook_01",
            text="A news alert on your phone: Board to address shareholder complaints at Friday meeting. In this "
                 "sentence, which word is closest to address?",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(phone, shift=DOWN * 0.2))
        self.at_word(n, "closest")
        self.play(Indicate(phone[1][1], color=WORD, scale_factor=1.04))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_02",
            text="Lecture, locate, label, or tackle? Every option is a real meaning of address somewhere. Only one fits "
                 "this sentence.",
            voice="default",
            subtitle=True,
            pause_after=3.0,
        )
        for row, spoken in zip(opts, ["Lecture", "locate", "label", "tackle"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=UP * 0.15), run_time=0.35)
        self.at_word(n, "Every")
        self.play(FadeIn(note, shift=UP * 0.1))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        self.clear_stage()
        self.scene_end("S01_hook")

    # ============================================== 2. CONCEPT ==========

    def fan(self, word, senses, color, centre):
        """A word with its meanings fanned out underneath."""
        hub = pill(word, color, size=BODY).move_to(centre)
        chips = VGroup(*[pill(s_, INK, size=SMALL, fill_opacity=0.06) for s_ in senses]).arrange(DOWN, buff=0.18)
        chips.next_to(hub, DOWN, buff=0.45)
        lines = VGroup(*[Line(hub.get_bottom(), c.get_top(), color=MUTED, stroke_width=1.5) for c in chips])
        return VGroup(hub, lines, chips)

    def concept(self):
        self.scene_start("S02_concept", title="The Concept")

        head = pill("polysemous: one word, several related meanings", WORD, size=LABEL)
        fit_width(head, SAFE_W)
        head.move_to(UP * (CARD_TOP - head.height / 2))
        fans = VGroup(self.fan("address", ["a location", "a speech", "deal with a problem"], WORD, ORIGIN),
                      self.fan("bright", ["full of light", "intelligent"], RATIO, ORIGIN),
                      self.fan("sound", ["a noise", "healthy (a sound mind)", "reliable (sound advice)"], SECOND,
                           ORIGIN)).arrange(RIGHT, buff=0.9, aligned_edge=UP)
        fit_width(fans, SAFE_W)
        fans.next_to(head, DOWN, buff=0.5)
        self.no_overlap(head, fans)
        self.validator.check_in_frame(VGroup(head, fans))

        n = self.narrate(
            id="concept_01",
            text="Many common words are polysemous: they have several related meanings. Address can mean a location, a "
                 "speech, or to deal with a problem. Bright can mean full of light, or intelligent. Sound can mean a "
                 "noise, healthy, as in a sound mind, or reliable, as in sound advice.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "polysemous")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        for f, spoken in zip(fans, ["Address", "Bright", "Sound"]):
            self.at_word(n, spoken)
            self.play(FadeIn(f[0], scale=1.1), Create(f[1]), LaggedStart(*[FadeIn(c) for c in f[2]], lag_ratio=0.2))
        self.wait_for_narration(n)

        # HEAR: the sentence selects one meaning; the rest become traps.
        sent = self.sentence_card("She has a sound mind", "sound")
        pick = self.fan("sound", ["a noise", "healthy", "reliable"], SECOND, ORIGIN)
        pick.next_to(sent, DOWN, buff=0.5)
        trap = pill("the other meanings return as TRAPS, the most common one first", BAD, size=SMALL)
        fit_width(trap, SAFE_W)
        trap.next_to(pick, DOWN, buff=0.45)
        self.no_overlap(sent, pick, trap)
        self.validator.check_in_frame(VGroup(sent, pick, trap))
        n = self.narrate(
            id="concept_02",
            text="When a synonym question gives the word inside a sentence, the sentence selects one meaning. The exam "
                 "then puts the other meanings into the options as traps. The most common meaning is usually one of "
                 "them, because it's the first one your brain reaches for.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(VGroup(head, fans)))
        self.play(FadeIn(sent, shift=DOWN * 0.2), FadeIn(pick))
        self.at_word(n, "selects")
        self.play(pick[2][1].animate.set_color(GOOD))
        self.at_word(n, "traps")
        self.play(pick[2][0].animate.set_opacity(0.4), pick[2][2].animate.set_opacity(0.4), FadeIn(trap, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_03",
            text="So in context questions, you don't ask what does this word mean. You ask what does this word mean here. "
                 "Then you predict a replacement that keeps the sentence's meaning intact.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "ask", occurrence=1)
        self.play(Indicate(pick[0], color=MUTED, scale_factor=1.1))
        self.at_word(n, "here")
        cap = self.caption("Not “what does it mean?”, but “what does it mean HERE?”", WORD)
        self.play(FadeIn(cap, shift=UP * 0.2))
        self.at_word(n, "predict")
        self.play(Indicate(pick[2][1], color=GOOD, scale_factor=1.15))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_concept")

    # ======================================== 3. WHY YOU NEED IT ==========

    def why_you_need_it(self):
        self.scene_start("S03_why", title="Why You Need It")

        where = VGroup(pill("C-CAT: word-in-a-sentence synonyms", WORD, size=LABEL),
                       pill("Reading Comprehension: vocabulary in context (Lesson 14)", SECOND, size=LABEL))\
            .arrange(DOWN, buff=0.4)
        fit_width(where, SAFE_W)
        warn = pill("built to punish the dictionary-first reader", BAD, size=LABEL)
        VGroup(where, warn).arrange(DOWN, buff=0.8).move_to(UP * 0.3)
        self.no_overlap(where, warn)
        self.validator.check_in_frame(VGroup(where, warn))

        n = self.narrate(
            id="why_01",
            text="Word-in-a-sentence synonyms are common in C-CAT, and in vocabulary in context questions in reading "
                 "comprehension, lesson fourteen. They're built to punish the dictionary-first reader.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "common")
        self.play(FadeIn(where[0], shift=UP * 0.1))
        self.at_word(n, "vocabulary")
        self.play(FadeIn(where[1], shift=UP * 0.1))
        self.at_word(n, "punish")
        self.play(FadeIn(warn, scale=1.05))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_why")

    # ============================================== 4. ANALOGY ==========

    def analogy(self):
        self.scene_start("S04_analogy", title="The Analogy")

        body = RoundedRectangle(corner_radius=0.3, width=2.0, height=4.2, color=MUTED, stroke_width=3,
                                fill_color=PANEL, fill_opacity=1).move_to(LEFT * 4.2 + DOWN * 0.1)
        button = Circle(radius=0.35, color=WORD, fill_color=WORD, fill_opacity=0.5).move_to(body.get_center() + DOWN * 0.8)
        devices = ["TV", "AC", "Music"]
        tabs = VGroup(*[pill(d, MUTED, size=SMALL) for d in devices]).arrange(DOWN, buff=0.15)
        tabs.move_to(body.get_center() + UP * 0.9)
        remote = VGroup(body, tabs, button)
        results = ["next channel", "cooler", "next song"]
        outs = VGroup(*[pill(r, GOOD, size=LABEL) for r in results])
        for o in outs:
            o.move_to(RIGHT * 1.5 + DOWN * 0.1)
        arrow = Arrow(button.get_right(), outs[0].get_left(), buff=0.3, color=MUTED)
        map_ = VGroup(pill("button = the word", WORD, size=SMALL), pill("selector = the sentence", SECOND, size=SMALL))\
            .arrange(DOWN, buff=0.25, aligned_edge=LEFT)
        map_.move_to(RIGHT * 3.4 + UP * 2.0)
        self.no_overlap(remote, outs[0], map_)
        self.validator.check_in_frame(VGroup(remote, outs, map_, arrow))

        n = self.narrate(
            id="analogy_01",
            text="A word is like a button on a universal remote. The same button does different things, depending on which "
                 "device is selected.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "button")
        self.play(FadeIn(remote), FadeIn(map_[0], shift=LEFT * 0.1))
        self.at_word(n, "different")
        current = outs[0]
        self.play(tabs[0].animate.set_color(SECOND), GrowArrow(arrow), FadeIn(current))
        for k in (1, 2):
            self.play(tabs[k - 1].animate.set_color(MUTED), tabs[k].animate.set_color(SECOND),
                      Indicate(button, color=WORD), ReplacementTransform(current, outs[k]), run_time=0.6)
            current = outs[k]
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_02",
            text="The sentence is the device selector. Check the selector before you press the button.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "selector", occurrence=1)
        self.play(FadeIn(map_[1], shift=LEFT * 0.1), Circumscribe(tabs, color=SECOND))
        self.at_word(n, "Check")
        cap = self.caption("Check the selector (the sentence) before you press the button", SECOND)
        self.play(FadeIn(cap, shift=UP * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_analogy")

    # ======================================== 5-7. WORKED EXAMPLES ==========

    def example_sound(self):
        self.scene_start("S05_ex_sound", title="Worked Example 1")
        self.play(self.pin(self.steps_pin("in context", [("meaning HERE", WORD), ("predict a replacement", STEP_COLS["PREDICT"]),
                                             ("other meanings = traps", BAD), ("substitute to confirm", GOOD)])))

        sentence, word = "She gave a sound explanation", "sound"
        card, q = self.context_question(sentence, word, ["noisy", "valid", "healthy", "loud"], "b",
                                        {"a": "the “noise” meaning", "c": "the “sound mind” meaning",
                                         "d": "the “noise” meaning"})
        here = pill("here: reliable, logical", GOOD, size=LABEL).next_to(q.word, RIGHT, buff=0.5)

        n = self.narrate(
            id="ex1_01",
            text="She gave a sound explanation. Sound here means reliable, or logical. Noisy, valid, healthy, or loud? The "
                 "answer is valid. Noisy and loud come from the noise meaning, and healthy from the sound mind meaning.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(card, shift=DOWN * 0.2))
        self.at_word(n, "reliable")
        self.play(FadeIn(q.word), FadeIn(here, shift=LEFT * 0.1), self.pin_step(0))
        self.at_word(n, "Noisy", occurrence=1)
        self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.2) for r in q.rows], lag_ratio=0.2))
        self.at_word(n, "answer")
        _, ok = q.confirm()
        self.play(*ok)
        self.at_word(n, "Noisy", occurrence=2)
        self.play(self.pin_step(2), run_time=0.4)
        _, a1 = q.strike("a")
        _, a4 = q.strike("d")
        self.play(*a1, *a4)
        self.at_word(n, "healthy", occurrence=2)
        _, a3 = q.strike("c")
        self.play(*a3)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_ex_sound")

    def example_launch(self):
        self.scene_start("S06_ex_launch", title="Worked Example 2")

        sentence, word = "The company will launch a probe", "launch"
        card, q = self.context_question(sentence, word, ["fire", "initiate", "float", "throw"], "b",
                                        {"a": "launching a rocket", "c": "launching a ship", "d": "launching a ball"})
        here = pill("here: start", GOOD, size=LABEL).next_to(q.word, RIGHT, buff=0.5)

        n = self.narrate(
            id="ex2_01",
            text="The company will launch a probe. Launch here means start. Fire, initiate, float, or throw? The answer is "
                 "initiate. The others are other meanings of launch.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(card, shift=DOWN * 0.2))
        self.at_word(n, "start")
        self.play(FadeIn(q.word), FadeIn(here, shift=LEFT * 0.1), self.pin_step(0))
        self.at_word(n, "Fire")
        self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.2) for r in q.rows], lag_ratio=0.2))
        self.at_word(n, "answer")
        _, ok = q.confirm()
        self.play(*ok)
        self.at_word(n, "others")
        self.play(self.pin_step(2), run_time=0.4)
        anims = []
        for letter in "acd":
            anims += q.strike(letter)[1]
        self.play(*anims)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_ex_launch")

    def example_bright(self):
        self.scene_start("S07_ex_bright", title="Worked Example 3")

        sentence, word = "He is a bright student", "bright"
        card, q = self.context_question(sentence, word, ["shining", "cheerful", "intelligent", "colourful"], "c",
                                        {"a": "the “light” meaning", "b": "a bright smile", "d": "bright colours"})

        n = self.narrate(
            id="ex3_01",
            text="He is a bright student. Shining, cheerful, intelligent, or colourful? A bright student is a clever one. "
                 "The answer is intelligent.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(card, shift=DOWN * 0.2), FadeIn(q.word))
        self.at_word(n, "Shining")
        self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.2) for r in q.rows], lag_ratio=0.2))
        self.at_word(n, "clever")
        self.play(self.pin_step(0), run_time=0.4)
        anims = []
        for letter in "abd":
            anims += q.strike(letter)[1]
        self.play(*anims)
        self.at_word(n, "answer")
        _, ok = q.confirm()
        self.play(*ok)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S07_ex_bright")

    # ================================================ 8. RULES ==========

    def rules(self):
        self.scene_start("S08_rules", title="Rules")

        rules = VGroup(*[VGroup(pill(str(i + 1), c, size=SMALL), fitted_text(s_, SAFE_W - 2.2, BODY, INK))
                         .arrange(RIGHT, buff=0.3) for i, (s_, c) in enumerate([
                             ("Read the full sentence before the options", WORD),
                             ("Cover the word and predict what should go in the gap", SECOND),
                             ("The answer must keep the sentence's meaning AND grammar", GOOD),
                             ("Expect the word's most common meaning as a trap", BAD)])])
        rules.arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        board = self.card(rules)
        self.place_free(board, y=0.3)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="rules_01",
            text="Four rules. First, read the full sentence before the options. Second, cover the word and predict what "
                 "should go in the gap. Third, the answer must keep the sentence's meaning and its grammar when swapped "
                 "in. And fourth, expect the word's most common meaning to appear as a trap.",
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
                               "a replacement from the sentence, not from memory",
                               "real meanings of the word that don't fit this sentence",
                               "the substitution test: read the sentence with the option in place"])])
        details.arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        board = self.card(details)
        self.place_free(board)
        board.next_to(strip, DOWN, buff=0.5)
        self.no_overlap(strip, board, self.pinned)
        self.validator.check_in_frame(VGroup(strip, board))

        n = self.narrate(
            id="process_01",
            text="The process, adapted for context. Read the sentence, and underline the word. Predict a replacement from "
                 "the sentence, not from memory. Eliminate options that are real meanings of the word, but not in this "
                 "sentence. And confirm with the substitution test: read the sentence with the option in place.",
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
        predict = pill("predict: deal with, handle", STEP_COLS["PREDICT"], size=LABEL).next_to(q.word, RIGHT, buff=0.5)
        answer = h["options"]["abcd".index(h["key"])]

        n = self.narrate(
            id="solved_01",
            text="Let's solve the hook. Read: Board to address shareholder complaints. Predict: deal with, or handle.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(card), FadeIn(q.word), FadeIn(q.rows))
        self.at_word(n, "Read")
        self.play(Indicate(card, color=WORD, scale_factor=1.02), self.pin_step(0))
        self.at_word(n, "Predict")
        self.play(FadeIn(predict, shift=LEFT * 0.2), self.pin_step(1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_02",
            text="Eliminate. Lecture matches address as a speech, but the board is handling complaints, not giving a talk. "
                 "Locate comes from the location meaning. Label comes from addressing an envelope.",
            voice="default",
            subtitle=True,
        )
        self.play(self.pin_step(2))
        for letter, spoken in [("a", "Lecture"), ("b", "Locate"), ("c", "Label")]:
            self.at_word(n, spoken)
            self.play(*q.strike(letter)[1])
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_03",
            text="Confirm: Board to tackle shareholder complaints. It holds. The answer is tackle.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Confirm")
        new, swap = self.substitution(card, h["sentence"], h["word"], answer)
        self.play(swap, self.pin_step(3))
        self.at_word(n, "holds")
        self.play(Indicate(new, color=GOOD, scale_factor=1.02))
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
            ["Bold word in a sentence", "predict from the sentence; expect the common meaning as a trap"],
            ["Same word, two sentences", "decide the meaning separately in each"],
            ["Vocabulary in context (RC)", "re-read the line before and after; substitute each option"],
        ], [4.4, 7.4], size=LABEL)
        board = self.card(table, width=SAFE_W - 0.2).move_to(UP * 0.4)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="patterns_01",
            text="Three exam patterns. A bold word in a sentence: predict from the sentence, and expect the common meaning "
                 "as a trap. The same word in two sentences: decide the meaning separately in each. And vocabulary in "
                 "context, in reading comprehension: re-read the line before and after, and substitute each option.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(board[0]), FadeIn(table[0]))
        for row, spoken in zip(table[1:], ["bold", "same", "vocabulary"]):
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
            (self.verdict_card(False, "Answering with the most common meaning", card_w),
             self.verdict_card(True, "Ask what it means HERE", card_w)),
            (self.verdict_card(False, "Skipping the substitution test", card_w),
             self.verdict_card(True, "Read the sentence with the option in place", card_w)),
            (self.verdict_card(False, "Right meaning, broken grammar", card_w),
             self.verdict_card(True, "Meaning AND grammar must hold", card_w)),
        ]
        for (wrong, right), yy in zip(pairs, [1.6, 0.05, -1.5]):
            wrong.move_to(LEFT_ZONE + UP * yy)
            right.move_to(RIGHT_ZONE + UP * yy)
        header = pill("3 mistakes", BAD, size=LABEL).move_to(UP * (CARD_TOP - 0.3))
        self.validator.check_in_frame(VGroup(header, *[c for p in pairs for c in p]))

        n = self.narrate(
            id="mistakes_01",
            text="Three common mistakes. The first is answering with the most common meaning of the word. The second is "
                 "skipping the substitution test. The third is choosing an option that fits the meaning, but breaks the "
                 "grammar.",
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
        ("The new policy will affect all employees", "affect", ["influence", "pretend", "infect", "result"], "a",
         {"b": "“affect” as pretend", "c": "sound-alike", "d": "the “effect” trap"}),
        ("His argument does not hold water", "hold", ["carry", "stand up", "grip", "contain"], "b",
         {"a": "literal trap", "c": "literal trap", "d": "literal trap"}, "hold water"),
        ("The minister fielded tough questions", "fielded", ["farmed", "avoided", "handled", "played"], "c",
         {"a": "the “field” as farmland meaning", "b": "opposite", "d": "the sports meaning"}),
    ]

    def practice(self):
        self.scene_start("S13_practice", title="Practice Questions")

        lines = VGroup()
        for i, (sent, w, opts, *_rest) in enumerate(self.PRACTICE):
            lines.add(VGroup(VGroup(pill(str(i + 1), FOCUS, size=SMALL), sentence_text(sent, w, size=LABEL, width=9.5))
                             .arrange(RIGHT, buff=0.3),
                             text("   ".join(f"({l}) {o}" for l, o in zip("abcd", opts)), SMALL, MUTED))
                      .arrange(DOWN, buff=0.12, aligned_edge=LEFT))
        lines.arrange(DOWN, buff=0.4, aligned_edge=LEFT)
        board = self.card(lines, width=SAFE_W - 0.2, color=FOCUS).move_to(UP * 0.4)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="practice_01",
            text="Your turn. One: the new policy will affect all employees. Influence, pretend, infect, or result? Two: his "
                 "argument does not hold water. Carry, stand up, grip, or contain? Three: the minister fielded tough "
                 "questions. Farmed, avoided, handled, or played?",
            voice="default",
            subtitle=True,
            pause_after=10.0,
        )
        self.play(FadeIn(board[0]))
        for ln, (spoken, first_option) in zip(lines, [("One", "Influence"), ("Two", "Carry"), ("Three", "Farmed")]):
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
        for sent, w, opts, key, traps, *phrase in self.PRACTICE:
            OptionQuestion(w, opts, key, traps)            # validates key / traps
            ans = opts["abcd".index(key)]
            target = phrase[0] if phrase else w            # "hold water" is replaced as a whole idiom
            rows.add(VGroup(sentence_text(swapped(sent, target, ans), ans, GOOD, LABEL, width=7.5),
                            pill(f"({key})", GOOD, size=SMALL)).arrange(RIGHT, buff=0.3))
        rows.arrange(DOWN, buff=0.35, aligned_edge=LEFT)
        why = VGroup(pill("result: the “effect” trap", BAD, size=SMALL),
                     pill("carry, contain: literal traps", BAD, size=SMALL),
                     pill("played: the sports meaning", BAD, size=SMALL)).arrange(RIGHT, buff=0.3)
        fit_width(why, SAFE_W)
        VGroup(rows, why).arrange(DOWN, buff=0.7).move_to(UP * 0.3)
        self.no_overlap(rows, why)
        self.validator.check_in_frame(VGroup(rows, why))

        n = self.narrate(
            id="answers_01",
            text="One: influence. Result is the effect trap. Two: stand up. Hold water means it's convincing, and carry and "
                 "contain are literal traps. Three: handled. Played comes from the sports meaning.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "influence")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "Result")
        self.play(FadeIn(why[0], shift=UP * 0.1))
        self.at_word(n, "stand")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.at_word(n, "literal")
        self.play(FadeIn(why[1], shift=UP * 0.1))
        self.at_word(n, "handled")
        self.play(FadeIn(rows[2], shift=RIGHT * 0.2))
        self.at_word(n, "Played")
        self.play(FadeIn(why[2], shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S14_answers")

    # ================================================ 15. RECAP ==========

    def recap(self):
        self.scene_start("S15_recap", title="Recap Card")

        card, table = self.recap_card("Recap Card: Video 3", [
            ["Polysemy", "one word, several meanings; the sentence picks one"],
            ["Key question", "what does it mean HERE?"],
            ["Trap", "the word's most common meaning"],
            ["Confirm", "substitute the option into the sentence"],
        ])
        card.move_to(UP * 0.2)
        self.validator.check_in_frame(card)

        n = self.narrate(
            id="recap_01",
            text="To recap. Polysemy: one word, several meanings, and the sentence picks one. The key question: what does "
                 "it mean here? The trap: the word's most common meaning. And confirm by substituting the option into the "
                 "sentence.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(card[0]), FadeIn(table[0]))
        for row, spoken in zip(table[1:], ["Polysemy", "key", "trap", "confirm"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.45)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S15_recap")

    # ================================================= 16. NEXT ==========

    def next_video(self):
        self.scene_start("S16_next", title="Next")

        pairs = VGroup(VGroup(pill("continual", WORD, size=BODY), text("≠", TITLE, BAD, BOLD),
                              pill("continuous", WORD, size=BODY)).arrange(RIGHT, buff=0.4),
                       VGroup(pill("economic", RATIO, size=BODY), text("≠", TITLE, BAD, BOLD),
                              pill("economical", RATIO, size=BODY)).arrange(RIGHT, buff=0.4)).arrange(DOWN, buff=0.5)
        nxt = pill("Next:  Commonly Confused Synonyms", FOCUS, size=BODY)
        VGroup(pairs, nxt).arrange(DOWN, buff=0.9).move_to(UP * 0.2)
        self.no_overlap(pairs, nxt)
        self.validator.check_in_frame(VGroup(pairs, nxt))

        n = self.narrate(
            id="next_01",
            text="Some words look like synonyms but aren't: continual and continuous, economic and economical. Video four "
                 "sorts the pairs exams use most.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "continual")
        self.play(FadeIn(pairs[0], shift=UP * 0.2))
        self.at_word(n, "economic")
        self.play(FadeIn(pairs[1], shift=UP * 0.2))
        self.at_word(n, "Video")
        self.play(FadeIn(nxt, scale=1.1))
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S16_next")

"""
animation.py for the LMS video generator.

Course : C-CAT - Section A - English
Module : Module 1 - Vocabulary
Lesson : Lesson 1 - Synonyms
Video  : 05 - Exam-Oriented Synonyms (Video 5 of 6)

Source script:
  C:\\Users\\User\\Downloads\\C-CAT_SectionA_Module1_English\\English\\Module 1 - Vocabulary\\
  Lesson 1 - Synonyms\\05 - Exam-Oriented Synonyms.pdf

Built on the golden-reference pattern:
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``.

Opening: a later video of Lesson 1, so no spoken welcome. The module > lesson >
video trail is shown on screen (silent), then a one-line recap of Videos 1-4
(method, tie-breakers, context, look-alike defences), the line about today's
topic, the title and the objectives.

Core visuals: the spice-rack "shelves" (one shelf per meaning group, all
twelve groups from the script's table in ``SHELVES``); words broken into their
roots (``word_parts`` asserts the pieces spell the word); ``OptionQuestion``
cards. Practice answers name the shelf found with ``shelf_of``. Layouts are
stacked with next_to and guarded with ``no_overlap``.

Section map (script heading -> scene):
  S00 Intro (trail + continuity)     S10 The Process
  S01 Hook                           S11 Hook, Solved
  S02 The Concept                    S12 Exam Patterns
  S03 Why You Need It                S13 Common Mistakes
  S04 The Analogy                    S14 Practice Questions
  S05-S07 Worked Examples 1-3      
  S08-S09 Rules (shelves, roots)     S15 Answers  S16 Recap Card  S17 Next
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

# Meaning groups ("shelves") from the script's Rules table.
SHELVES = [
    ("Plenty", ["abundant", "ample", "copious", "profuse", "lavish"], GOOD),
    ("Scarce", ["meagre", "scanty", "sparse", "paltry", "scarce"], BAD),
    ("Honest / open", ["candid", "frank", "forthright", "sincere"], WORD),
    ("Careful", ["meticulous", "diligent", "scrupulous", "thorough"], SECOND),
    ("Clear", ["lucid", "explicit", "coherent", "transparent"], "#4DD0E1"),
    ("Unclear", ["ambiguous", "vague", "obscure", "cryptic"], MUTED),
    ("Old / out of use", ["obsolete", "archaic", "antiquated", "defunct"], RATIO),
    ("Brief", ["concise", "succinct", "terse", "laconic"], "#AED581"),
    ("Stubborn", ["obstinate", "adamant", "rigid", "headstrong"], "#FF8A65"),
    ("Calm down / reduce", ["abate", "subside", "diminish", "wane"], "#90CAF9"),
    ("Praise", ["commend", "laud", "acclaim", "extol"], FOCUS),
    ("Criticise", ["censure", "rebuke", "reprimand", "condemn"], "#F48FB1"),
]
SHELF = {name: (words, col) for name, words, col in SHELVES}

ROOTS = [
    ("bene- / mal-", "good / bad", "benign, malign"),
    ("loqu / dict", "speak / say", "eloquent, verdict"),
    ("chron", "time", "chronic, chronology"),
    ("omni- / pan-", "all", "omnipotent, panorama"),
    ("ambi- / amphi-", "both", "ambiguous, ambivalent"),
]


def shelf_of(word):
    return next(name for name, (words, _) in SHELF.items() if word in words)


def shelf(name, words, color, width=SAFE_W - 0.6, size=SMALL):
    """One spice-rack shelf: the group label, the words as jars, and a plank underneath."""
    tag = pill(name, color, size=size)
    jars = VGroup(*[pill(w, INK, size=size, fill_opacity=0.06) for w in words]).arrange(RIGHT, buff=0.18)
    row = VGroup(tag, jars).arrange(RIGHT, buff=0.35)
    fit_width(row, width)
    plank = Line(row.get_corner(DL) + DOWN * 0.08, row.get_corner(DR) + DOWN * 0.08, color=color, stroke_width=4)
    return VGroup(tag, jars, plank)


def word_parts(word, parts, size=BODY):
    """A word broken into its parts, each with its meaning underneath. ``parts`` = [(piece, meaning, color)];
    the pieces must spell the word."""
    assert "".join(p for p, _, _ in parts) == word, (word, parts)
    cols = VGroup(*[VGroup(pill(p, c, size=size), text(m, SMALL, c)).arrange(DOWN, buff=0.15)
                    for p, m, c in parts]).arrange(RIGHT, buff=0.15, aligned_edge=UP)
    return cols


class ExamOrientedSynonymsVideo(LMSScene):
    lesson_title = "Exam-Oriented Synonyms"

    def construct(self):
        self.camera.background_color = BG

        self.lesson_intro()
        self.hook()
        self.concept()
        self.why_you_need_it()
        self.analogy()
        self.example_obsolete()
        self.example_benevolent()
        self.example_loquacious()
        self.rules_shelves()
        self.rules_roots()
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

    def release_note(self, fill=None):
        head = text("RELEASE NOTE", SMALL, RATIO, BOLD)
        word = fill or "obsolete"
        body = text(f"“Version 2 of our API is now {word}. Please migrate by 31 March.”", BODY, INK,
                    t2c={rf"\b{word}\b": GOOD if fill else WORD})
        card = self.card(VGroup(head, fit_width(body, SAFE_W - 1.6)).arrange(DOWN, buff=0.2, aligned_edge=LEFT),
                         width=SAFE_W - 0.4)
        return card.move_to(UP * (CARD_TOP - card.height / 2))

    # ========================================= 0. LESSON INTRO ==========
    # Purpose: silent trail, a one-line recap of Videos 1-4 (the four tools),
    # today's topic, the objectives.

    def lesson_intro(self):
        self.scene_start("S00_intro", title="Lesson Introduction")

        crumb = self.breadcrumb("English · Module 1 Vocabulary", "Lesson 1 · Synonyms", "Video 5")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        tools = VGroup(*[VGroup(pill(t, c, size=LABEL), text(f"Video {i + 1}", SMALL, MUTED)).arrange(DOWN, buff=0.15)
                         for i, (t, c) in enumerate([("method", WORD), ("tie-breakers", RATIO), ("context", SECOND),
                                                     ("look-alike defences", BAD)])]).arrange(RIGHT, buff=0.45)
        fit_width(tools, SAFE_W)
        left = pill("what's left: the raw material, the words exams actually use", GOOD, size=LABEL)
        fit_width(left, SAFE_W)
        VGroup(tools, left).arrange(DOWN, buff=0.8).move_to(DOWN * 0.1)
        self.no_overlap(crumb, tools, left)
        self.validator.check_in_frame(VGroup(crumb, tools, left))

        n = self.narrate(
            id="intro_01",
            text="You now have a method from video one, tie-breakers from video two, context from video three, and "
                 "look-alike defences from video four. What's left is the raw material: the words exams actually use.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        for t, spoken in zip(tools, ["method", "tie-breakers", "context", "look-alike"]):
            self.at_word(n, spoken)
            self.play(FadeIn(t, shift=UP * 0.15), run_time=0.35)
        self.at_word(n, "raw")
        self.play(FadeIn(left, shift=UP * 0.1))
        self.wait_for_narration(n)

        title = fitted_text("Exam-Oriented Synonyms", SAFE_W, 72, INK, BOLD)
        underline = Line(LEFT, RIGHT, color=GOOD, stroke_width=5).set_width(title.width * 0.6)
        VGroup(title, underline).arrange(DOWN, buff=0.2).move_to(UP * 0.2)
        n = self.narrate(
            id="intro_02",
            text="These are the exam-oriented synonyms.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(VGroup(tools, left), shift=UP * 0.3))
        self.at_word(n, "exam-oriented")
        self.play(Write(title), run_time=1.1)
        self.play(GrowFromCenter(underline))
        self.wait_for_narration(n)

        goals = [
            ("Learn a core set of high-frequency exam words, in meaning groups", GOOD),
            ("Decode unfamiliar words with roots and prefixes", SECOND),
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
            text="By the end of this video, you'll learn a core set of high-frequency exam words in meaning groups, and "
                 "you'll decode unfamiliar words with roots and prefixes.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(underline), ReplacementTransform(title, small_title), run_time=0.8)
        self.play(FadeIn(objectives[0]), FadeIn(heading))
        for row_, spoken in zip(rows, ["learn", "decode"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row_, shift=RIGHT * 0.2), run_time=0.5)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_intro")

    # ================================================= 1. HOOK ==========

    HOOK = dict(word="OBSOLETE", options=["broken", "hidden", "outdated", "expensive"], key="c",
                traps={"a": "it may still work", "b": "not about age", "d": "not about age"})

    def hook(self):
        self.scene_start("S01_hook", title="Hook")

        note = self.release_note()
        h = self.HOOK
        q = OptionQuestion(h["word"], h["options"], h["key"], h["traps"])
        opts = q.rows.copy().arrange(RIGHT, buff=0.7)
        fit_width(opts, SAFE_W)
        tag = pill("one word, a real migration decision", FOCUS, size=SMALL)
        opts.next_to(note, DOWN, buff=0.9)
        tag.next_to(opts, DOWN, buff=0.7)
        self.no_overlap(note, opts, tag)
        self.validator.check_in_frame(VGroup(note, opts, tag))

        n = self.narrate(
            id="hook_01",
            text="A release note from a vendor says: Version two of our API is now obsolete. Please migrate by thirty-one "
                 "March. Your team has to decide how urgent this is.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(note, shift=DOWN * 0.2))
        self.at_word(n, "migrate")
        self.play(Circumscribe(note, color=RATIO))
        self.at_word(n, "urgent")
        self.play(Indicate(note[1][1], color=WORD, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_02",
            text="Obsolete is closest to: broken, hidden, outdated, or expensive? One word, a real migration decision, and "
                 "it's exactly the kind of word C-CAT tests.",
            voice="default",
            subtitle=True,
            pause_after=3.0,
        )
        for row, spoken in zip(opts, ["broken", "hidden", "outdated", "expensive"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=UP * 0.15), run_time=0.35)
        self.at_word(n, "migration")
        self.play(FadeIn(tag, shift=UP * 0.1))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        self.clear_stage()
        self.scene_end("S01_hook")

    # ============================================== 2. CONCEPT ==========

    def concept(self):
        self.scene_start("S02_concept", title="The Concept")

        head = pill("the same few hundred words recur: C-CAT, placement tests, bank exams", WORD, size=SMALL)
        fit_width(head, SAFE_W)
        head.move_to(UP * (CARD_TOP - head.height / 2))
        pair = VGroup(shelf("Plenty", SHELF["Plenty"][0], GOOD), shelf("Scarce", SHELF["Scarce"][0], BAD))\
            .arrange(DOWN, buff=0.35, aligned_edge=LEFT)
        pair.next_to(head, DOWN, buff=0.45)
        bonus = pill("each group: a synonym set AND, usually, an antonym set", GOOD, size=SMALL)
        fit_width(bonus, SAFE_W)
        bonus.next_to(pair, DOWN, buff=0.35)
        self.no_overlap(head, pair, bonus)
        self.validator.check_in_frame(VGroup(head, pair, bonus))

        n = self.narrate(
            id="concept_01",
            text="Exam vocabulary isn't random. The same few hundred words recur across C-CAT, placement tests and bank "
                 "exams, and most cluster into a small number of meaning groups.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "recur")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "groups")
        self.play(FadeIn(pair[0][0]), Create(pair[0][2]),
                  LaggedStart(*[FadeIn(j, shift=DOWN * 0.1) for j in pair[0][1]], lag_ratio=0.15))
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_02",
            text="Learning words in groups is faster than learning them alphabetically, because each group gives you a "
                 "synonym set and, usually, an antonym set at the same time.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "antonym")
        self.play(FadeIn(pair[1][0]), Create(pair[1][2]),
                  LaggedStart(*[FadeIn(j, shift=DOWN * 0.1) for j in pair[1][1]], lag_ratio=0.15))
        self.play(FadeIn(bonus, shift=UP * 0.1))
        self.wait_for_narration(n)

        # Roots: benevolent has bene- (good), so it can't mean cruel.
        parts = word_parts("benevolent", [("bene", "good", GOOD), ("vol", "wish", SECOND), ("ent", "ending", MUTED)])
        cruel = VGroup(pill("cruel", BAD, size=BODY), text("contradicts “good”", SMALL, BAD)).arrange(DOWN, buff=0.15)
        roots = VGroup(parts, cruel).arrange(RIGHT, buff=1.5).move_to(DOWN * 0.6)
        built = pill("many exam words: built from Latin or Greek parts", SECOND, size=SMALL)
        knock = pill("know the part  →  eliminate two options", GOOD, size=SMALL)
        clues = VGroup(built, knock).arrange(DOWN, buff=0.3).next_to(roots, UP, buff=0.6)
        self.no_overlap(parts, cruel)
        self.no_overlap(clues, roots)
        self.validator.check_in_frame(VGroup(roots, clues))
        n = self.narrate(
            id="concept_03",
            text="When you meet a word you don't know, you still have roots. A large share of exam words are built from "
                 "Latin or Greek parts. If you know the part, you can often eliminate two options, even when the full "
                 "word is new. Benevolent has bene, meaning good, so it can't mean cruel.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "roots")
        self.play(FadeOut(VGroup(head, pair, bonus)))
        self.at_word(n, "Latin")
        self.play(FadeIn(built, shift=DOWN * 0.1))
        self.at_word(n, "eliminate")
        self.play(FadeIn(knock, shift=DOWN * 0.1))
        self.at_word(n, "Benevolent")
        self.play(LaggedStart(*[FadeIn(c, shift=UP * 0.15) for c in parts], lag_ratio=0.3))
        self.at_word(n, "cruel")
        self.play(FadeIn(cruel, shift=LEFT * 0.1))
        self.play(Create(Cross(cruel[0], stroke_color=BAD, stroke_width=4)))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_concept")

    # ======================================== 3. WHY YOU NEED IT ==========

    def why_you_need_it(self):
        self.scene_start("S03_why", title="Why You Need It")

        grid = VGroup(*[Square(side_length=0.45, color=MUTED, stroke_width=2) for _ in range(20)])\
            .arrange_in_grid(rows=2, cols=10, buff=0.12)
        hits = [2, 6, 9, 13, 17]
        for i in hits:
            grid[i].set_fill(GOOD, opacity=0.6).set_stroke(GOOD)
        label = text("a 20-question English section", LABEL, INK)
        next_ = pill("the groups feed straight into Lesson 2: Antonyms", SECOND, size=LABEL)
        VGroup(label, grid, next_).arrange(DOWN, buff=0.5).move_to(UP * 0.2)
        self.no_overlap(label, grid, next_)
        self.validator.check_in_frame(VGroup(label, grid, next_))

        n = self.narrate(
            id="why_01",
            text="In a twenty-question English section, you'll almost certainly meet several of these words. And the "
                 "groups feed directly into lesson two, antonyms.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(label), LaggedStart(*[FadeIn(s) for s in grid], lag_ratio=0.03))
        self.at_word(n, "several")
        self.play(*[Indicate(grid[i], color=GOOD) for i in hits])
        self.at_word(n, "groups")
        self.play(FadeIn(next_, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_why")

    # ============================================== 4. ANALOGY ==========

    def analogy(self):
        self.scene_start("S04_analogy", title="The Analogy")

        rack = VGroup(*[shelf(name, SHELF[name][0][:3], SHELF[name][1], width=7.2) for name in
                        ["Plenty", "Scarce", "Honest / open"]]).arrange(DOWN, buff=0.45, aligned_edge=LEFT)
        rack.move_to(LEFT * 2.2 + DOWN * 0.1)
        frame = SurroundingRectangle(rack, color=MUTED, buff=0.3, corner_radius=0.15)
        not_abc = VGroup(pill("by flavour", GOOD, size=LABEL), pill("not A → Z", BAD, size=LABEL))\
            .arrange(DOWN, buff=0.35).next_to(frame, RIGHT, buff=0.7)
        self.no_overlap(frame, not_abc)
        self.validator.check_in_frame(VGroup(frame, not_abc))

        n = self.narrate(
            id="analogy_01",
            text="A good kitchen groups spices by flavour, not alphabetically. When you need something hot, you go to one "
                 "shelf.",
            voice="default",
            subtitle=True,
        )
        self.play(Create(frame))
        self.at_word(n, "flavour")
        self.play(FadeIn(not_abc[0], shift=LEFT * 0.1))
        self.at_word(n, "alphabetically")
        self.play(FadeIn(not_abc[1], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_02",
            text="Store words the same way: one shelf for plenty, one for scarce, one for honest. In the exam, you go "
                 "straight to the right shelf.",
            voice="default",
            subtitle=True,
        )
        for sh, spoken in zip(rack, ["plenty", "scarce", "honest"]):
            self.at_word(n, spoken)
            self.play(FadeIn(sh[0]), Create(sh[2]), FadeIn(sh[1], shift=DOWN * 0.1), run_time=0.5)
        self.at_word(n, "straight")
        self.play(Circumscribe(rack[2], color=WORD))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_analogy")

    # ======================================== 5-7. WORKED EXAMPLES ==========

    def example_obsolete(self):
        self.scene_start("S05_ex_obsolete", title="Worked Example 1")
        self.play(self.pin(self.steps_pin("any exam word", [("known word: its shelf", GOOD), ("unknown: break into roots", SECOND),
                                                ("predict the direction", STEP_COLS["PREDICT"]),
                                                ("eliminate contradictions", BAD)])))

        word = pill("OBSOLETE", WORD, size=TITLE)
        name = shelf_of("obsolete")
        sh = shelf(name, SHELF[name][0], SHELF[name][1])
        group = VGroup(word, sh).arrange(DOWN, buff=0.9)
        self.place_free(group, y=-0.6)
        self.no_overlap(word, sh)
        self.validator.check_in_frame(group)

        n = self.narrate(
            id="ex1_01",
            text="Obsolete goes on the old, or no longer used, shelf, with outdated, archaic and defunct.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(word, scale=1.1))
        self.at_word(n, "shelf")
        self.play(FadeIn(sh[0]), Create(sh[2]), self.pin_step(0))
        self.play(LaggedStart(*[FadeIn(j, shift=DOWN * 0.1) for j in sh[1]], lag_ratio=0.2))
        pointer = Arrow(word.get_bottom(), sh[1][0].get_top(), buff=0.12, color=WORD)
        self.play(GrowArrow(pointer), Indicate(sh[1][0], color=WORD, scale_factor=1.15))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_ex_obsolete")

    def example_benevolent(self):
        self.scene_start("S06_ex_benevolent", title="Worked Example 2")

        word = pill("BENEVOLENT", WORD, size=TITLE)
        parts = word_parts("benevolent", [("bene", "good", GOOD), ("vol", "wish", SECOND), ("ent", "ending", MUTED)])
        result = pill("→  kind, generous", GOOD, size=BODY)
        group = VGroup(word, parts, result).arrange(DOWN, buff=0.6)
        self.place_free(group, y=0.2)
        self.no_overlap(word, parts, result)
        self.validator.check_in_frame(group)

        n = self.narrate(
            id="ex2_01",
            text="Benevolent. The root bene means good, and vol means wish. Wishing good: kind, generous.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(word, scale=1.1))
        self.at_word(n, "bene")
        self.play(FadeIn(parts[0], shift=UP * 0.1), FadeIn(parts[2]), self.pin_step(1))
        self.at_word(n, "vol")
        self.play(FadeIn(parts[1], shift=UP * 0.1))
        self.at_word(n, "kind")
        self.play(FadeIn(result, shift=UP * 0.1), self.pin_step(2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_ex_benevolent")

    def example_loquacious(self):
        self.scene_start("S07_ex_loquacious", title="Worked Example 3")

        word = pill("LOQUACIOUS", WORD, size=TITLE)
        parts = word_parts("loquacious", [("loqu", "speak", SECOND), ("acious", "full of", MUTED)])
        result = pill("→  talkative", GOOD, size=BODY)
        silent = VGroup(pill("silent", BAD, size=BODY), text("contradicts “speak”", SMALL, BAD)).arrange(DOWN, buff=0.15)
        row = VGroup(result, silent).arrange(RIGHT, buff=1.2)
        group = VGroup(word, parts, row).arrange(DOWN, buff=0.6)
        self.place_free(group, y=0.2)
        self.no_overlap(word, parts, row)
        self.validator.check_in_frame(group)

        n = self.narrate(
            id="ex3_01",
            text="Loquacious. The root loqu means speak, so it means talkative. An option like silent must be wrong.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(word, scale=1.1))
        self.at_word(n, "loqu")
        self.play(FadeIn(parts, shift=UP * 0.1), self.pin_step(1))
        self.at_word(n, "talkative")
        self.play(FadeIn(result, shift=UP * 0.1))
        self.at_word(n, "silent")
        self.play(FadeIn(silent, shift=LEFT * 0.1), self.pin_step(3))
        self.play(Create(Cross(silent[0], stroke_color=BAD, stroke_width=4)))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S07_ex_loquacious")

    # ================================================ 8. RULES ==========

    def shelf_board(self, names):
        rows = VGroup(*[shelf(nm, SHELF[nm][0], SHELF[nm][1]) for nm in names]).arrange(DOWN, buff=0.28,
                                                                                         aligned_edge=LEFT)
        fit_within(rows, SAFE_W - 0.6, SAFE_H - 1.6)
        rows.move_to(UP * (CARD_TOP - rows.height / 2 - 0.1))
        return rows

    def rules_shelves(self):
        self.scene_start("S08_rules_shelves", title="Rules: Twelve Meaning Groups")
        self.play(self.unpin())

        first = self.shelf_board([s[0] for s in SHELVES[:6]])
        second = self.shelf_board([s[0] for s in SHELVES[6:]])
        self.validator.check_in_frame(first)
        self.validator.check_in_frame(second)

        n = self.narrate(
            id="shelves_01",
            text="Here are twelve shelves to learn. Plenty: abundant, ample, copious. Scarce: meagre, scanty, sparse. "
                 "Honest: candid, frank, forthright. Careful: meticulous, diligent, scrupulous. Clear: lucid, explicit, "
                 "coherent. Unclear: ambiguous, vague, obscure.",
            voice="default",
            subtitle=True,
        )
        twelve = pill("12 shelves", FOCUS, size=BODY)
        self.at_word(n, "twelve")
        self.play(FadeIn(twelve, scale=1.2), run_time=0.4)
        self.play(FadeOut(twelve), run_time=0.3)
        for sh, spoken in zip(first, ["Plenty", "Scarce", "Honest", "Careful", "Clear", "Unclear"]):
            self.at_word(n, spoken)
            self.play(FadeIn(sh[0]), Create(sh[2]), FadeIn(sh[1], shift=DOWN * 0.1), run_time=0.5)
        self.wait_for_narration(n)

        n = self.narrate(
            id="shelves_02",
            text="Old: obsolete, archaic, antiquated. Brief: concise, succinct, terse. Stubborn: obstinate, adamant, "
                 "rigid. Calm down: abate, subside, diminish. Praise: commend, laud, acclaim. And criticise: censure, "
                 "rebuke, reprimand.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(first))
        for sh, spoken in zip(second, ["Old", "Brief", "Stubborn", "Calm", "Praise", "criticise"]):
            self.at_word(n, spoken)
            self.play(FadeIn(sh[0]), Create(sh[2]), FadeIn(sh[1], shift=DOWN * 0.1), run_time=0.5)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S08_rules_shelves")

    def rules_roots(self):
        self.scene_start("S09_rules_roots", title="Rules: Key Roots")

        table = self.table_rows(["Root / prefix", "Meaning", "Examples"], [list(r) for r in ROOTS], [3.6, 3.4, 4.8],
                                size=LABEL)
        board = self.card(table, width=SAFE_W - 0.2).move_to(UP * 0.3)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="roots_01",
            text="And five roots to decode the rest. Bene and mal: good and bad, as in benign and malign. Loqu and dict: "
                 "speak and say, as in eloquent and verdict. Chron: time, as in chronic. Omni and pan: all, as in "
                 "omnipotent and panorama. And ambi: both, as in ambiguous and ambivalent.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(board[0]), FadeIn(table[0]))
        for row, spoken in zip(table[1:], ["Bene", "Loqu", "Chron", "Omni", "ambi"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.45)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S09_rules_roots")

    # ============================================== 9. PROCESS ==========

    def process(self):
        self.scene_start("S10_process", title="The Process")

        steps = VGroup(*[VGroup(pill(str(i + 1), c, size=SMALL), fitted_text(s_, SAFE_W - 2.2, BODY, INK))
                         .arrange(RIGHT, buff=0.3) for i, (s_, c) in enumerate([
                             ("Know the word?  Place it on its shelf; predict from that group", GOOD),
                             ("Don't know it?  Break it into parts; predict the direction", SECOND),
                             ("Eliminate options that contradict the direction", BAD),
                             ("Confirm in a sentence", WORD)])])
        steps.arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        board = self.card(steps).move_to(UP * 0.3)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="process_01",
            text="The process. Do you know the word? Place it on its shelf and predict from that group. Don't know it? "
                 "Break it into parts, and predict the direction: good or bad, more or less. Then eliminate options that "
                 "contradict the direction, and confirm in a sentence.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(board[0]))
        for r, (spoken, follow) in zip(steps, [("know", "Place"), ("Don't", "Break"), ("eliminate", "contradict"),
                                               ("confirm", "sentence")]):
            self.at_word(n, spoken)
            self.play(FadeIn(r, shift=RIGHT * 0.2), run_time=0.4)
            self.at_word(n, follow)
            self.play(Indicate(r[1], color=FOCUS, scale_factor=1.03), run_time=0.4)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S10_process")

    # ========================================== 10. HOOK, SOLVED ==========

    def hook_solved(self):
        self.scene_start("S11_hook_solved", title="Hook, Solved")

        h = self.HOOK
        note = self.release_note()
        q = OptionQuestion(h["word"], h["options"], h["key"], h["traps"], word_size=BODY)
        q.group.next_to(note, DOWN, buff=0.45).to_edge(LEFT, buff=SAFE + 0.6)
        predict = pill("predict: outdated, no longer supported", STEP_COLS["PREDICT"], size=SMALL)
        predict.to_edge(RIGHT, buff=SAFE + 0.2).align_to(q.word, UP)
        decision = pill("plan the migration now, but nothing is broken yet", GOOD, size=LABEL)
        fit_width(decision, SAFE_W)
        decision.to_edge(DOWN, buff=SAFE + 0.4)
        filled = self.release_note("outdated")
        self.no_overlap(note, q.group, decision)
        self.validator.check_in_frame(VGroup(note, q.group, predict, decision))

        n = self.narrate(
            id="solved_01",
            text="Let's solve the hook. Read: obsolete, describing an API version. Predict: outdated, no longer "
                 "supported.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(note), FadeIn(q.word), FadeIn(q.rows))
        self.at_word(n, "Read")
        self.play(Indicate(q.word, color=WORD, scale_factor=1.1))
        self.at_word(n, "Predict")
        self.play(FadeIn(predict, shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_02",
            text="Eliminate. Broken: it may still work, it's just not supported. Hidden and expensive aren't about age.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Eliminate")
        self.play(Indicate(q.rows, color=BAD, scale_factor=1.02))
        self.at_word(n, "Broken")
        self.play(*q.strike("a")[1])
        self.at_word(n, "Hidden")
        self.play(*q.strike("b")[1], *q.strike("d")[1])
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_03",
            text="Confirm: version two is now outdated, please migrate. The answer is outdated. So: plan the migration "
                 "now, but nothing is broken yet.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Confirm")
        self.play(ReplacementTransform(note, filled))
        self.at_word(n, "answer")
        self.play(*q.confirm()[1])
        self.at_word(n, "plan")
        self.play(FadeIn(decision, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S11_hook_solved")

    # ========================================== 11. EXAM PATTERNS ==========

    def exam_patterns(self):
        self.scene_start("S12_patterns", title="Exam Patterns and Solving Models")

        table = self.table_rows(["Pattern", "Solving model"], [
            ["Known high-frequency word", "place it on its shelf; pick the option from the same shelf"],
            ["Unknown word", "root → direction → eliminate the contradicting options"],
            ["Two options from the same shelf", "break the tie on degree and connotation (Video 2)"],
        ], [4.6, 7.2], size=LABEL)
        board = self.card(table, width=SAFE_W - 0.2).move_to(UP * 0.4)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="patterns_01",
            text="Three exam patterns. A known high-frequency word: place it on its shelf, and pick the option from the "
                 "same shelf. An unknown word: root, then direction, then eliminate the contradicting options. And two "
                 "options from the same shelf: break the tie on degree and connotation, as in video two.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(board[0]), FadeIn(table[0]))
        for row, spoken in zip(table[1:], ["known", "unknown", "two"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.45)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S12_patterns")

    # ======================================== 12. COMMON MISTAKES ==========

    def common_mistakes(self):
        self.scene_start("S13_mistakes", title="Common Mistakes")

        card_w = ZONE_W - 0.3
        pairs = [
            (self.verdict_card(False, "Isolated words, no group: can't recall them", card_w),
             self.verdict_card(True, "Learn by shelf", card_w)),
            (self.verdict_card(False, "Guessing from sound: benign read as “bad”", card_w),
             self.verdict_card(True, "bene = good: benign = gentle", card_w)),
            (self.verdict_card(False, "Ignoring degree: scarce vs paltry", card_w),
             self.verdict_card(True, "Check strength inside the group", card_w)),
        ]
        for (wrong, right), yy in zip(pairs, [1.6, 0.05, -1.5]):
            wrong.move_to(LEFT_ZONE + UP * yy)
            right.move_to(RIGHT_ZONE + UP * yy)
        header = pill("3 mistakes", BAD, size=LABEL).move_to(UP * (CARD_TOP - 0.3))
        self.validator.check_in_frame(VGroup(header, *[c for p in pairs for c in p]))

        n = self.narrate(
            id="mistakes_01",
            text="Three common mistakes. The first is learning isolated words without their group, so you can't recall "
                 "them under pressure. The second is guessing from sound instead of roots, like reading benign as bad. "
                 "The third is ignoring degree inside a group, like scarce versus paltry.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(header))
        for pr, spoken in zip(pairs, ["first", "second", "third"]):
            self.at_word(n, spoken)
            self.play(FadeIn(pr[0], shift=RIGHT * 0.3), FadeIn(pr[1], shift=LEFT * 0.3))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S13_mistakes")

    # ============================================== 13. PRACTICE ==========

    PRACTICE = [
        ("COPIOUS", ["plentiful", "exact", "copied", "careful"], "a", {"b": "unrelated", "c": "sound trap",
                                                                       "d": "unrelated"}),
        ("TERSE", ["tense", "polite", "confused", "brief"], "d", {"a": "sound trap", "b": "unrelated",
                                                                   "c": "unrelated"}),
        ("LAUD", ["shout", "praise", "blame", "permit"], "b", {"a": "sound trap (loud)", "c": "opposite",
                                                               "d": "unrelated"}),
    ]

    def practice(self):
        self.scene_start("S14_practice", title="Practice Questions")

        lines = VGroup(*[VGroup(pill(str(i + 1), FOCUS, size=SMALL), pill(w, WORD, size=LABEL),
                                text("   ".join(f"({l}) {o}" for l, o in zip("abcd", opts)), LABEL, INK))
                         .arrange(RIGHT, buff=0.35) for i, (w, opts, *_r) in enumerate(self.PRACTICE)])
        lines.arrange(DOWN, buff=0.5, aligned_edge=LEFT)
        board = self.card(lines, color=FOCUS).move_to(UP * 0.4)
        fit_width(board, SAFE_W)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="practice_01",
            text="Your turn. One: copious. Plentiful, exact, copied, or careful? Two: terse. Tense, polite, confused, or "
                 "brief? Three: laud. Shout, praise, blame, or permit?",
            voice="default",
            subtitle=True,
            pause_after=10.0,
        )
        self.play(FadeIn(board[0]))
        for ln, (spoken, first_option) in zip(lines, [("copious", "Plentiful"), ("terse", "Tense"),
                                                     ("laud", "Shout")]):
            self.at_word(n, spoken)
            self.play(FadeIn(ln[:2], shift=UP * 0.15), run_time=0.4)
            self.at_word(n, first_option)
            self.play(FadeIn(ln[2], shift=LEFT * 0.15), run_time=0.4)
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        self.clear_stage()
        self.scene_end("S14_practice")

    # =============================================== 14. ANSWERS ==========

    def answers(self):
        self.scene_start("S15_answers", title="Answers")

        rows = VGroup()
        for w, opts, key, traps in self.PRACTICE:
            OptionQuestion(w, opts, key, traps)            # validates key / traps
            name = shelf_of(w.lower())
            sound = next(l for l, r in traps.items() if r.startswith("sound"))
            rows.add(VGroup(pill(w, WORD, size=LABEL), text("→", LABEL, MUTED),
                            pill(f"({key}) {opts['abcd'.index(key)]}", GOOD, size=LABEL),
                            pill(f"“{name}” shelf", SHELF[name][1], size=SMALL),
                            text(f"({sound}) {opts['abcd'.index(sound)]}: {traps[sound]}", SMALL, BAD))
                     .arrange(RIGHT, buff=0.3))
        rows.arrange(DOWN, buff=0.45, aligned_edge=LEFT)
        fit_width(rows, SAFE_W).move_to(UP * 0.3)
        self.validator.check_in_frame(rows)

        n = self.narrate(
            id="answers_01",
            text="One: plentiful, from the plenty shelf. Copied is a sound trap. Two: brief, from the brief shelf. Tense "
                 "is a sound trap. Three: praise, from the praise shelf. Shout is a sound trap, from loud.",
            voice="default",
            subtitle=True,
        )
        for r, (spoken, trap) in zip(rows, [("plentiful", "Copied"), ("brief", "Tense"), ("praise", "Shout")]):
            self.at_word(n, spoken)
            self.play(FadeIn(r[:4], shift=RIGHT * 0.2), run_time=0.5)
            self.at_word(n, trap)
            self.play(FadeIn(r[4], shift=LEFT * 0.1), run_time=0.4)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S15_answers")

    # ================================================ 15. RECAP ==========

    def recap(self):
        self.scene_start("S16_recap", title="Recap Card")

        card, table = self.recap_card("Recap Card: Video 5", [
            ["Learn in groups", "one shelf per meaning (plenty, scarce, honest, careful …)"],
            ["Unknown word", "root → direction → eliminate"],
            ["Key roots", "bene / mal, loqu / dict, chron, omni, ambi"],
            ["Daily habit", "10 words a day, by shelf, with one sentence each"],
        ])
        card.move_to(UP * 0.2)
        self.validator.check_in_frame(card)

        n = self.narrate(
            id="recap_01",
            text="To recap. Learn in groups: one shelf per meaning. For an unknown word, go root, then direction, then "
                 "eliminate. Keep the key roots handy: bene and mal, loqu and dict, chron, omni and ambi. And build a "
                 "daily habit: ten words a day, by shelf, with one sentence each.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(card[0]), FadeIn(table[0]))
        for row, spoken in zip(table[1:], ["groups", "unknown", "roots", "daily"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.45)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S16_recap")

    # ================================================= 16. NEXT ==========

    def next_video(self):
        self.scene_start("S17_next", title="Next")

        parts = VGroup(*[pill(t, c, size=LABEL) for t, c in [("method", WORD), ("tie-breakers", RATIO),
                                                            ("context", SECOND), ("look-alikes", BAD),
                                                            ("shelves & roots", GOOD)]]).arrange(RIGHT, buff=0.3)
        fit_width(parts, SAFE_W)
        one = pill("one fast method for any synonym question", FOCUS, size=BODY)
        nxt = pill("Next:  Synonym Question-Solving Techniques", FOCUS, size=LABEL)
        VGroup(parts, one, nxt).arrange(DOWN, buff=0.7).move_to(UP * 0.2)
        self.no_overlap(parts, one, nxt)
        self.validator.check_in_frame(VGroup(parts, one, nxt))

        n = self.narrate(
            id="next_01",
            text="Video six turns all of this into one fast method for any synonym question.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "all")
        self.play(LaggedStart(*[FadeIn(p, shift=UP * 0.1) for p in parts], lag_ratio=0.15))
        self.at_word(n, "one")
        self.play(TransformFromCopy(parts, one))
        self.play(FadeIn(nxt, scale=1.05))
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S17_next")

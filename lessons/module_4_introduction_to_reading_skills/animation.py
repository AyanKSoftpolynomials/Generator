"""
animation.py for the LMS video generator.

Course : Pre-C-CAT - Section A - English
Video  : Module 4 Introduction - Why Reading Skills Are in the Pre-C-CAT Course

Source script:
  C:\\Scripts\\Section A\\English - Module 4 Introduction - Why Reading Skills.md

Built on the golden-reference pattern:
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``;
  * layouts stacked with next_to and guarded with ``no_overlap``; nothing is
    ever animated onto or into another box.

Module introduction. Opening rule from the script: a silent breadcrumb and a one-line recap of Module 3, no spoken course welcome.
The narration is the script's. The worked example is data: an option is marked right only if the quoted passage line contains what it claims.
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

from fractions import Fraction

MARKS_RIGHT, TOTAL_MIN = 3, 60
PASSAGE_Q_2019, PASSAGE_Q_2025, SLOW_READ_MIN = 5, 4, 6

assert PASSAGE_Q_2019 * MARKS_RIGHT == 15 and Fraction(SLOW_READ_MIN, TOTAL_MIN) == Fraction(1, 10)

# The worked example (passage on the history of Spain, as students recalled it).
KEY_WORDS = "Napoleonic Wars"
LINE = "…Napoleonic Wars, leading to French occupation of much of Europe, including Spain."
# The line as it is laid out on screen: two rows of parts (the key words and the extent stand alone).
LINE_ROWS = [["…", KEY_WORDS, ", leading to French occupation of"], ["much of Europe", ", including Spain."]]
# (words that carry the claim, rest of the option, what the line must contain for it to be supported)
OPTIONS = [("A small part", "of the continent was occupied by French people", ["small part"]),
           ("Spain", "was occupied by the French", ["Spain", "French"])]


def supported(needs, line):
    """An option is supported only if the passage line itself says it."""
    return all(need in line for need in needs)


assert "".join(LINE_ROWS[0]) + " " + "".join(LINE_ROWS[1]) == LINE
assert [supported(needs, LINE) for _, _, needs in OPTIONS] == [False, True]
ANSWER = [supported(needs, LINE) for _, _, needs in OPTIONS].index(True)

# (kind of question, example)
KINDS = [("Detail", "What was the result of…?"),
         ("Word meaning", "What does “culminated” mean?"),
         ("Main idea", "What is the summary of the passage?"),
         ("Inference", "What does the passage suggest?")]
MODULE_3_STEPS = ["Find the clue", "Predict", "Match and eliminate"]


def steps_strip(labels, colors, size=LABEL, buff=0.25):
    """Numbered steps in a row, joined by arrows.  Steps are at [0], [2], [4]."""
    parts = []
    for i, (label, c) in enumerate(zip(labels, colors)):
        if i:
            parts.append(text("→", size, MUTED))
        parts.append(pill(f"{i + 1}  {label}", c, size=size))
    return VGroup(*parts).arrange(RIGHT, buff=buff)


def lesson_rows(lessons, first_number=1, color=WORD):
    """One row per item: number chip, name, example.  Names and examples are column-aligned."""
    names = [text(name, LABEL, color, BOLD) for name, _ in lessons]
    gap = max(n.width for n in names) + 0.6
    rows = VGroup()
    for i, (name, (_, example)) in enumerate(zip(names, lessons)):
        num = pill(str(first_number + i), color, size=SMALL)
        ex = text(example, LABEL, INK)
        name.next_to(num, RIGHT, buff=0.3)
        ex.next_to(num, RIGHT, buff=0.3 + gap)
        rows.add(VGroup(num, name, ex))
    return rows.arrange(DOWN, buff=0.32, aligned_edge=LEFT)


def passage_bars(widths, height=0.1, gap=0.16):
    """A passage drawn as grey lines of text (one bar per line)."""
    bars = VGroup(*[Rectangle(width=w, height=height, stroke_color=MUTED, stroke_width=1, fill_color=MUTED,
                              fill_opacity=0.4) for w in widths])
    return bars.arrange(DOWN, buff=gap, aligned_edge=LEFT)


def question_tiles(count, color):
    return VGroup(*[pill(f"Q{i}", color) for i in range(1, count + 1)]).arrange(RIGHT, buff=0.12)


class WhyReadingSkillsVideo(LMSScene):
    lesson_title = "Why Reading Skills Are in the Pre-C-CAT Course"

    def construct(self):
        self.camera.background_color = BG

        self.opening_recap()
        self.passage_marks()
        self.questions_first()
        self.four_kinds()
        self.how_lesson_works()
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

    def heading(self, s, color=FOCUS):
        head = pill(s, color, size=LABEL)
        return head.move_to(UP * (CARD_TOP - head.height / 2))

    # ========================================= 0. OPENING AND RECAP ==========
    # Opening rule: silent breadcrumb, a one-line recap of Module 3, no spoken welcome.

    def opening_recap(self):
        self.scene_start("S00_recap", title="Opening and Recap")

        crumb = self.breadcrumb("English", "Module 4 · Reading Skills", "Introduction")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        strip = steps_strip(MODULE_3_STEPS, [FOCUS, RATIO, GOOD], size=SMALL)
        one = VGroup(text("one sentence:", SMALL, MUTED), text("I visit my parents ____ as I work in a different city.", SMALL, INK))\
            .arrange(RIGHT, buff=0.3)
        bars = passage_bars([7.0, 6.4, 3.2, 7.0, 5.6, 7.0, 6.8, 2.6, 7.0, 4.4])
        whole = text("a whole passage", LABEL, WORD, BOLD)
        where = pill("the clue is somewhere in here", FOCUS)
        side = VGroup(whole, where).arrange(DOWN, buff=0.4, aligned_edge=LEFT)
        passage = VGroup(bars, side).arrange(RIGHT, buff=0.7)
        block = VGroup(strip, one, passage).arrange(DOWN, buff=0.55)
        fit_within(block, SAFE_W, SAFE_H - crumb.height - 0.8)
        block.next_to(crumb, DOWN, buff=0.5)
        self.no_overlap(crumb, strip, one, passage)
        self.no_overlap(bars, side)
        self.validator.check_in_frame(VGroup(crumb, block))

        n = self.narrate(
            id="recap_01",
            text="In the last module, you found the clue inside one sentence.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.at_word(n, "module")
        self.play(LaggedStart(*[FadeIn(s_, shift=RIGHT * 0.1) for s_ in strip], lag_ratio=0.12))
        self.at_word(n, "sentence")
        self.play(FadeIn(one, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="recap_02",
            text="Now the clue is somewhere inside a whole passage.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "somewhere")
        self.play(LaggedStart(*[FadeIn(b, shift=RIGHT * 0.2) for b in bars], lag_ratio=0.08), FadeIn(where, shift=LEFT * 0.1))
        self.at_word(n, "passage")
        self.play(FadeIn(whole, shift=LEFT * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_recap")

    # ==================================== 1. ONE PASSAGE, MANY MARKS ==========

    def passage_marks(self):
        self.scene_start("S01_passage_marks", title="One Passage, Many Marks")

        head = self.heading("How much is one passage worth?")
        cols = VGroup()
        for label, count, c in [("2019 paper", PASSAGE_Q_2019, WORD), ("July 2025  ·  history of Spain  ·  recalled",
                                                                       PASSAGE_Q_2025, RATIO)]:
            cols.add(VGroup(text(label, SMALL, c, BOLD), passage_bars([4.6, 4.0, 4.6, 2.8]), question_tiles(count, c))
                     .arrange(DOWN, buff=0.25, aligned_edge=LEFT))
        cols.arrange(RIGHT, buff=1.2, aligned_edge=UP)
        marks = text(f"{PASSAGE_Q_2019} questions × {MARKS_RIGHT} marks  =  {PASSAGE_Q_2019 * MARKS_RIGHT} marks", LABEL, GOOD,
                     BOLD)
        risk = VGroup(pill("the risk: time", BAD, size=LABEL),
                      text(f"read slowly, read twice  →  {SLOW_READ_MIN}:00 for one passage", LABEL, INK))\
            .arrange(RIGHT, buff=0.4)
        per_min = 0.19
        gone = Rectangle(width=SLOW_READ_MIN * per_min, height=0.4, color=BAD, fill_color=BAD, fill_opacity=0.7)
        rest = Rectangle(width=(TOTAL_MIN - SLOW_READ_MIN) * per_min, height=0.4, color=MUTED, fill_color=MUTED,
                         fill_opacity=0.2)
        bar = VGroup(gone, rest).arrange(RIGHT, buff=0)
        tenth = text(f"{SLOW_READ_MIN} of {TOTAL_MIN} minutes  =  a tenth of Section A, on five questions", SMALL, BAD, BOLD)
        budget = VGroup(bar, tenth).arrange(DOWN, buff=0.2)
        body = VGroup(cols, marks, risk, budget).arrange(DOWN, buff=0.4)
        fit_within(body, SAFE_W, SAFE_H - head.height - 0.6)
        body.next_to(head, DOWN, buff=0.35)
        self.no_overlap(head, cols, marks, risk, budget)
        self.no_overlap(cols[0], cols[1])
        self.no_overlap(bar, tenth)
        self.validator.check_in_frame(VGroup(head, body))

        n = self.narrate(
            id="marks_01",
            text="Here is why this module matters.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "matters")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="marks_02",
            text="The 2019 paper opened with one passage and five questions.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "passage")
        self.play(FadeIn(cols[0][0]), FadeIn(cols[0][1], shift=UP * 0.1))
        self.at_word(n, "five")
        self.play(LaggedStart(*[FadeIn(q, scale=0.7) for q in cols[0][2]], lag_ratio=0.12))
        self.wait_for_narration(n)

        n = self.narrate(
            id="marks_03",
            text="That is fifteen marks from a single passage.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "fifteen")
        self.play(FadeIn(marks, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="marks_04",
            text="Students recalled a passage in 2025 as well, with about four questions.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "recalled")
        self.play(FadeIn(cols[1][0]), FadeIn(cols[1][1], shift=UP * 0.1))
        self.at_word(n, "four")
        self.play(LaggedStart(*[FadeIn(q, scale=0.7) for q in cols[1][2]], lag_ratio=0.12))
        self.wait_for_narration(n)

        n = self.narrate(
            id="marks_05",
            text="The risk is time. Read slowly, read twice, and one passage can take six minutes.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "time")
        self.play(FadeIn(risk[0], shift=UP * 0.1))
        self.at_word(n, "six")
        self.play(FadeIn(risk[1], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="marks_06",
            text="That is a tenth of your whole section, gone on five questions.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "tenth")
        self.play(FadeIn(rest), GrowFromEdge(gone, LEFT))
        self.at_word(n, "gone")
        self.play(FadeIn(tenth, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S01_passage_marks")

    # ===================================== 2. READ THE QUESTIONS FIRST ==========

    def questions_first(self):
        self.scene_start("S02_questions_first", title="Read the Questions First")

        head = self.heading("What are you looking for?")
        first = pill("questions first", GOOD, size=LABEL).next_to(head, RIGHT, buff=0.4)
        q_key = text(KEY_WORDS, LABEL, INK, BOLD)
        question = VGroup(text("Q.", LABEL, MUTED, BOLD), text("What was the result of the", LABEL, INK), q_key,
                          text("?", LABEL, INK), pill("key words", FOCUS)).arrange(RIGHT, buff=0.14)
        question[4].shift(RIGHT * 0.3)

        line_rows = VGroup(*[VGroup(*[text(part, SMALL, INK) for part in row]).arrange(RIGHT, buff=0.06, aligned_edge=DOWN)
                             for row in LINE_ROWS]).arrange(DOWN, buff=0.14, aligned_edge=LEFT)
        l_key, l_extent = line_rows[0][1], line_rows[1][0]
        above, below = passage_bars([7.4, 6.2]), passage_bars([7.4, 4.8])
        passage = VGroup(above, line_rows, below).arrange(DOWN, buff=0.3, aligned_edge=LEFT)

        options = VGroup(*[VGroup(text(f"({l})", LABEL, MUTED), text(claim, LABEL, INK), text(rest, LABEL, INK))
                           .arrange(RIGHT, buff=0.14) for l, (claim, rest, _) in zip("ab", OPTIONS)])\
            .arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        wrong, right = options[1 - ANSWER], options[ANSWER]
        moral = VGroup(text("no history needed", LABEL, MUTED),
                       pill("The answer is on the page, not in your memory.", GOOD, size=LABEL)).arrange(RIGHT, buff=0.4)
        stack = VGroup(question, passage, options, moral).arrange(DOWN, buff=0.45)
        fit_within(stack, SAFE_W, SAFE_H - head.height - 0.6)
        stack.next_to(head, DOWN, buff=0.4)
        found = SurroundingRectangle(line_rows, color=FOCUS, buff=0.1, corner_radius=0.08)
        strike = Line(wrong.get_left() + LEFT * 0.05, wrong.get_right() + RIGHT * 0.05, color=BAD, stroke_width=3)
        box = SurroundingRectangle(right, color=GOOD, buff=0.1, corner_radius=0.1)
        self.no_overlap(head, first)
        self.no_overlap(head, question, passage, options, moral)
        self.no_overlap(above, found, below)
        self.no_overlap(wrong, box)
        self.validator.check_in_frame(VGroup(head, first, stack))

        n = self.narrate(
            id="first_01",
            text="So do not start with the passage. Start with the questions.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "not")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "questions")
        self.play(FadeIn(first, shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="first_02",
            text="Take this one. Now you know what to look for: the words Napoleonic Wars.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "one")
        self.play(FadeIn(question[:4], shift=UP * 0.1))
        self.at_word(n, "Napoleonic")
        self.play(q_key.animate.set_color(FOCUS), FadeIn(question[4], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="first_03",
            text="Scan for those words. You find them in one sentence.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Scan")
        self.play(LaggedStart(*[FadeIn(b, shift=RIGHT * 0.2) for b in [*above, *below]], lag_ratio=0.15))
        self.at_word(n, "sentence")
        self.play(FadeIn(line_rows, shift=RIGHT * 0.1))
        self.play(l_key.animate.set_color(FOCUS), run_time=0.4)
        self.wait_for_narration(n)

        n = self.narrate(
            id="first_04",
            text="It says the wars led to French occupation of much of Europe, including Spain.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "occupation")
        self.play(Create(found))
        self.at_word(n, "much")
        self.play(l_extent.animate.set_color(FOCUS))
        self.wait_for_narration(n)

        n = self.narrate(
            id="first_05",
            text="Now compare the options with that line.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "options")
        self.play(LaggedStart(*[FadeIn(o, shift=UP * 0.1) for o in options], lag_ratio=0.3))
        self.wait_for_narration(n)

        n = self.narrate(
            id="first_06",
            text="One says a small part of the continent. The passage says much of Europe. So it is wrong.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "small")
        self.play(wrong[1].animate.set_color(BAD))
        self.at_word(n, "much")
        self.play(Indicate(l_extent, color=FOCUS, scale_factor=1.15))
        self.at_word(n, "wrong")
        self.play(Create(strike), wrong.animate.set_opacity(0.45))
        self.wait_for_narration(n)

        n = self.narrate(
            id="first_07",
            text="The other matches the line exactly.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "matches")
        self.play(Create(box), right[1:].animate.set_color(GOOD))
        self.wait_for_narration(n)

        n = self.narrate(
            id="first_08",
            text="You did not need history. The answer was on the page.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "history")
        self.play(FadeIn(moral[0], shift=UP * 0.1))
        self.at_word(n, "page")
        self.play(FadeIn(moral[1], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_questions_first")

    # ================================= 3. THE FOUR KINDS OF QUESTION ==========

    def four_kinds(self):
        self.scene_start("S03_four_kinds", title="The Four Kinds of Question")

        head = self.heading("What a passage can ask")
        rows = lesson_rows(KINDS)
        vocab = pill("your vocabulary method works", GOOD).next_to(rows[1][2], RIGHT, buff=0.35)
        table = VGroup(rows, vocab)
        warning = pill("True in general  ≠  stated in the passage", BAD, size=LABEL)
        trap = VGroup(text("true in real life…", LABEL, MUTED), text("…still wrong if the passage does not say it", LABEL, INK))\
            .arrange(RIGHT, buff=0.3)
        body = VGroup(table, warning, trap).arrange(DOWN, buff=0.45)
        fit_within(body, SAFE_W, SAFE_H - head.height - 0.8)
        body.next_to(head, DOWN, buff=0.5)
        self.no_overlap(head, table, warning, trap)
        self.no_overlap(rows[1][2], vocab)
        self.validator.check_in_frame(VGroup(head, body))

        n = self.narrate(
            id="kinds_01",
            text="A passage can ask four kinds of question.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "four")
        self.play(FadeIn(head, shift=DOWN * 0.2), LaggedStart(*[FadeIn(r[0], scale=0.7) for r in rows], lag_ratio=0.12))
        self.wait_for_narration(n)

        n = self.narrate(
            id="kinds_02",
            text="A detail question: find one fact.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "detail")
        self.play(FadeIn(rows[0][1], shift=RIGHT * 0.2))
        self.at_word(n, "fact")
        self.play(FadeIn(rows[0][2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="kinds_03",
            text="A word-meaning question: what a word means in this passage. Your vocabulary method works here.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "word-meaning")
        self.play(FadeIn(rows[1][1], shift=RIGHT * 0.2))
        self.at_word(n, "means")
        self.play(FadeIn(rows[1][2], shift=RIGHT * 0.2))
        self.at_word(n, "vocabulary")
        self.play(FadeIn(vocab, shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="kinds_04",
            text="A main-idea question: what the whole passage is about.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "main-idea")
        self.play(FadeIn(rows[2][1], shift=RIGHT * 0.2))
        self.at_word(n, "whole")
        self.play(FadeIn(rows[2][2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="kinds_05",
            text="And an inference question: what the passage suggests without saying it directly.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "inference")
        self.play(FadeIn(rows[3][1], shift=RIGHT * 0.2))
        self.at_word(n, "suggests")
        self.play(FadeIn(rows[3][2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="kinds_06",
            text="One trap runs through all four. An option can be true in real life and still be wrong, because the passage "
                 "does not say it.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "trap")
        self.play(FadeIn(warning, scale=1.05))
        self.at_word(n, "true")
        self.play(FadeIn(trap[0], shift=UP * 0.1))
        self.at_word(n, "wrong")
        self.play(FadeIn(trap[1], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_four_kinds")

    # ==================================== 4. HOW THE LESSON WORKS ==========

    def how_lesson_works(self):
        self.scene_start("S04_how_lesson_works", title="How the Lesson Works")

        head = self.heading("The same three steps every time")
        strip = steps_strip(["Read the questions", "Locate the lines", "Match and eliminate"], [WORD, FOCUS, GOOD])
        fit_width(strip, SAFE_W)
        strip.next_to(head, DOWN, buff=0.6)
        keys = VGroup(text("note the key words", SMALL, MUTED), pill(KEY_WORDS, FOCUS)).arrange(DOWN, buff=0.22)
        lines = passage_bars([3.0, 2.6, 3.0, 2.2, 3.0])
        tiles = VGroup(*[pill(f"({l})", INK, size=SMALL, fill_opacity=0.06) for l in "ab"]).arrange(RIGHT, buff=0.3)
        unsupported = text("not in the passage: out", SMALL, BAD)
        match = VGroup(tiles, unsupported).arrange(DOWN, buff=0.22)
        for detail, step in zip([keys, lines, match], [strip[0], strip[2], strip[4]]):
            fit_width(detail, 3.4)
            detail.next_to(step, DOWN, buff=0.6)
        out, kept = tiles[1 - ANSWER], tiles[ANSWER]
        cross = Line(out.get_corner(DL), out.get_corner(UR), color=BAD, stroke_width=3)
        self.no_overlap(head, strip)
        self.no_overlap(keys, lines, match)
        self.validator.check_in_frame(VGroup(head, strip, keys, lines, match))

        n = self.narrate(
            id="how_01",
            text="The lesson uses three steps.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "three")
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(strip[1]), FadeIn(strip[3]))
        self.wait_for_narration(n)

        n = self.narrate(
            id="how_02",
            text="Read the questions, and note the key words.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Read")
        self.play(FadeIn(strip[0], shift=DOWN * 0.1))
        self.at_word(n, "key")
        self.play(FadeIn(keys, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="how_03",
            text="Locate the lines that contain them.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Locate")
        self.play(FadeIn(strip[2], shift=DOWN * 0.1), FadeIn(lines, shift=UP * 0.1))
        self.at_word(n, "contain")
        self.play(lines[2].animate.set_fill(FOCUS, opacity=0.9).set_stroke(FOCUS))
        self.wait_for_narration(n)

        n = self.narrate(
            id="how_04",
            text="Then match each option against those lines, and eliminate what the passage does not support.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "match")
        self.play(FadeIn(strip[4], shift=DOWN * 0.1), FadeIn(tiles, shift=UP * 0.1))
        self.play(kept.animate.set_color(GOOD), run_time=0.5)
        self.at_word(n, "eliminate")
        self.play(Create(cross), out[1].animate.set_opacity(0.35), FadeIn(unsupported, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_how_lesson_works")

    # ================================================ 5. CLOSING ==========

    def closing(self):
        self.scene_start("S05_closing", title="Closing")

        facts = VGroup(pill(f"one passage  =  up to {PASSAGE_Q_2019 * MARKS_RIGHT} marks", WORD, size=LABEL),
                       pill("the answers are on the page", GOOD, size=LABEL)).arrange(RIGHT, buff=0.5)
        fit_width(facts, SAFE_W)
        title = pill("Lesson 14  ·  Reading Comprehension", RATIO, size=LABEL)
        strip = VGroup(*[pill(name, MUTED) for name, _ in KINDS]).arrange(RIGHT, buff=0.3)
        lesson = VGroup(title, strip).arrange(DOWN, buff=0.3)
        nxt = self.breadcrumb("Next", "Lesson 14 · Reading Comprehension")
        VGroup(facts, lesson, nxt).arrange(DOWN, buff=0.8).move_to(UP * 0.2)
        self.no_overlap(facts, title, strip, nxt)
        self.validator.check_in_frame(VGroup(facts, lesson, nxt))

        n = self.narrate(
            id="closing_01",
            text="To sum up: one passage can be worth fifteen marks, and the answers are always on the page.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "fifteen")
        self.play(FadeIn(facts[0], shift=UP * 0.1))
        self.at_word(n, "page")
        self.play(FadeIn(facts[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="closing_02",
            text="We begin with reading comprehension. See you in lesson fourteen.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "reading")
        self.play(FadeIn(title, shift=UP * 0.1), LaggedStart(*[FadeIn(p, shift=UP * 0.1) for p in strip], lag_ratio=0.12))
        self.at_word(n, "lesson")
        self.play(FadeIn(nxt, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S05_closing")

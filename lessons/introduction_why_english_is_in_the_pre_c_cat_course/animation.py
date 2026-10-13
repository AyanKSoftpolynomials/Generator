"""
animation.py for the LMS video generator.

Course : Pre-C-CAT - Section A - English
Video  : Introduction - Why English Is in the Pre-C-CAT Course

Source script:
  C:\\Scripts\\Section A\\English - Introduction - Why English in Pre-C-CAT.md

Built on the golden-reference pattern:
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``;
  * layouts stacked with next_to and guarded with ``no_overlap``; nothing is
    ever animated onto or into another box.

Section introduction. Opening rule from the script: a silent breadcrumb only, no spoken course welcome.
The narration is the script's, word for word. The figures (50 questions, about 20 English, +3 / -1, 60 minutes, about 14 and 5) are constants, and the totals on screen (60 of 150 marks, 52 minutes, the value of a guess) are computed from them.
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

# Figures from the script (a recent memory-based paper; all "about").
TOTAL_Q, ENGLISH_Q, MARKS_RIGHT, MARKS_WRONG = 50, 20, 3, -1
TOTAL_MIN, ENGLISH_MIN = 60, 8
VOCAB_Q, GRAMMAR_Q = 14, 5
MODULE_1 = ["Synonyms", "Antonyms", "Idioms & Phrases", "One-Word Substitution", "Analogies"]
MODULE_2 = ["Prepositions", "Articles", "Active & Passive Voice", "Spotting Errors", "Sentence Correction"]


def expected_marks(options_left):
    """Average marks for a guess among ``options_left`` options (+3 / −1 marking)."""
    p = Fraction(1, options_left)
    return p * MARKS_RIGHT + (1 - p) * MARKS_WRONG


assert ENGLISH_Q * MARKS_RIGHT == 60 and TOTAL_Q * MARKS_RIGHT == 150
assert expected_marks(4) == 0 and expected_marks(2) == 1 and TOTAL_MIN - ENGLISH_MIN == 52


def question_squares(n=TOTAL_Q, side=0.42):
    """Section A as a block of n small grey squares (10 per row)."""
    squares = VGroup(*[Square(side_length=side, stroke_color=MUTED, stroke_width=2, fill_color=MUTED, fill_opacity=0.25)
                       for _ in range(n)])
    return squares.arrange_in_grid(rows=n // 10, cols=10, buff=0.1)


def steps_strip(labels, colors, size=LABEL):
    """Numbered steps in a row, joined by arrows.  Steps are at [0], [2], [4]."""
    parts = []
    for i, (label, c) in enumerate(zip(labels, colors)):
        if i:
            parts.append(text("→", size, MUTED))
        parts.append(pill(f"{i + 1}  {label}", c, size=size))
    return VGroup(*parts).arrange(RIGHT, buff=0.25)


class WhyEnglishVideo(LMSScene):
    lesson_title = "Why English Is in the Pre-C-CAT Course"

    def construct(self):
        self.camera.background_color = BG

        self.opening_hook()
        self.reason_speed()
        self.reason_marking()
        self.reason_ties()
        self.what_you_learn()
        self.how_lessons_work()
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

    def lesson_card(self, title, rows, color):
        body = VGroup(text(title, LABEL, color, BOLD), *[text(r, LABEL, INK) for r in rows])\
            .arrange(DOWN, buff=0.2, aligned_edge=LEFT)
        return self.card(body, width=ZONE_W - 0.4, color=color)

    # ============================================ 0. OPENING HOOK ==========
    # Opening rule for this video: a silent breadcrumb only, no spoken welcome.

    def opening_hook(self):
        self.scene_start("S00_hook", title="Opening Hook")

        crumb = self.breadcrumb("English", "Introduction", "Why English in Pre-C-CAT")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        ask = VGroup(text("You are applying for a computing course.", BODY, INK),
                     text("So why is there English in the entrance test?", BODY, FOCUS, BOLD)).arrange(DOWN, buff=0.4)
        ask.move_to(UP * 0.2)
        self.no_overlap(crumb, ask)
        self.validator.check_in_frame(VGroup(crumb, ask))

        n = self.narrate(
            id="hook_01",
            text="You are preparing for a computing course. So why does the entrance test ask you about synonyms and "
                 "prepositions?",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.at_word(n, "computing")
        self.play(FadeIn(ask[0], shift=UP * 0.1))
        self.at_word(n, "why")
        self.play(FadeIn(ask[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        paper = text("Section A of C-CAT", LABEL, MUTED, BOLD)
        squares = question_squares()
        count = text(f"{TOTAL_Q} questions", LABEL, INK)
        english = pill(f"English ≈ {ENGLISH_Q}", WORD, size=LABEL)
        source = text("a recent memory-based paper", SMALL, MUTED)
        marks = VGroup(text(f"{ENGLISH_Q} questions × {MARKS_RIGHT} marks", LABEL, INK),
                       text(f"=  {ENGLISH_Q * MARKS_RIGHT} of {TOTAL_Q * MARKS_RIGHT} marks", LABEL, GOOD, BOLD))\
            .arrange(RIGHT, buff=0.3)
        biggest = pill("no other part of Section A is bigger", FOCUS, size=SMALL)
        left = VGroup(paper, squares, count).arrange(DOWN, buff=0.25)
        right = VGroup(english, source, marks, biggest).arrange(DOWN, buff=0.4, aligned_edge=LEFT)
        block = VGroup(left, right).arrange(RIGHT, buff=0.9)
        fit_width(block, SAFE_W)
        block.move_to(DOWN * 0.2)
        self.no_overlap(crumb, block)
        self.no_overlap(left, right)
        self.validator.check_in_frame(VGroup(crumb, block))

        n = self.narrate(
            id="hook_02",
            text="Here is the short answer. Look at Section A of C-CAT. It has fifty questions.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "short")
        self.play(FadeOut(ask, shift=UP * 0.2))
        self.at_word(n, "Section")
        self.play(FadeIn(paper, shift=DOWN * 0.1))
        self.at_word(n, "fifty")
        self.play(LaggedStart(*[FadeIn(s_, scale=0.6) for s_ in squares], lag_ratio=0.02), FadeIn(count), run_time=1.4)
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_03",
            text="In a recent memory-based paper, about twenty of those fifty were English.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "memory-based")
        self.play(FadeIn(source, shift=UP * 0.1))
        self.at_word(n, "twenty")
        self.play(LaggedStart(*[s_.animate.set_fill(WORD, opacity=0.8).set_stroke(WORD) for s_ in squares[:ENGLISH_Q]],
                              lag_ratio=0.04), FadeIn(english, shift=LEFT * 0.1), run_time=1.2)
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_04",
            text="At three marks each, that is sixty marks out of one hundred and fifty. No other part of Section A is "
                 "bigger.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "three")
        self.play(FadeIn(marks[0], shift=UP * 0.1))
        self.at_word(n, "sixty")
        self.play(FadeIn(marks[1], shift=LEFT * 0.1))
        self.at_word(n, "bigger")
        self.play(FadeIn(biggest, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_hook")

    # ================================= 1. REASON 1: THE FASTEST MARKS ==========

    def reason_speed(self):
        self.scene_start("S01_reason_speed", title="Reason 1 - The Fastest Marks in the Paper")

        head = self.heading("Reason 1  ·  Fastest marks", GOOD)
        per_sec = 0.05                                          # timer bar: units per second
        contents, cards, timers = [], VGroup(), VGroup()
        for label, body, seconds, c in [("an English question", "Opposite of FRUGAL?", 15, GOOD),
                                        ("a quant question", "Two pipes fill a tank in 12 h and 18 h. Together?", 75, BAD)]:
            content = VGroup(text(label, SMALL, MUTED, BOLD), fitted_text(body, 4.6, LABEL, INK, NORMAL, max_lines=2))\
                .arrange(DOWN, buff=0.2, aligned_edge=LEFT)
            contents.append(content)
            timers.add(VGroup(Rectangle(width=seconds * per_sec, height=0.3, color=c, fill_color=c, fill_opacity=0.6),
                              text(f"≈ {seconds} s", LABEL, c, BOLD)).arrange(RIGHT, buff=0.2))
        tallest = max(c.height for c in contents) + 0.6           # both cards the same height
        for content in contents:
            cards.add(self.card(content, width=5.6, height=tallest))
        cards.arrange(RIGHT, buff=0.6, aligned_edge=UP)
        cards.next_to(head, DOWN, buff=0.6)
        for card_, timer in zip(cards, timers):
            timer.next_to(card_, DOWN, buff=0.3).align_to(card_, LEFT)
        self.no_overlap(head, cards)
        self.no_overlap(cards[0], cards[1])
        for timer in timers:
            self.no_overlap(head, timer)
            self.no_overlap(cards[0], timer)
            self.no_overlap(cards[1], timer)
        self.no_overlap(timers[0], timers[1])
        self.validator.check_in_frame(VGroup(head, cards, timers))

        n = self.narrate(
            id="speed_01",
            text="The first reason is speed.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "speed")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="speed_02",
            text="Compare two questions. One asks for the opposite of frugal. The other asks how long two pipes take to "
                 "fill a tank.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Compare")
        self.play(FadeIn(cards[0][0]), FadeIn(cards[1][0]))
        self.at_word(n, "frugal")
        self.play(FadeIn(cards[0][1], shift=UP * 0.1))
        self.at_word(n, "pipes")
        self.play(FadeIn(cards[1][1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="speed_03",
            text="The first takes about fifteen seconds if you know the word. The second takes over a minute, even if you "
                 "know the method.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "fifteen")
        self.play(GrowFromEdge(timers[0][0], LEFT), FadeIn(timers[0][1]), run_time=0.6)
        self.at_word(n, "minute")
        self.play(GrowFromEdge(timers[1][0], LEFT), FadeIn(timers[1][1]), run_time=1.6)
        self.wait_for_narration(n)

        # The 60-minute budget.
        per_min = 0.19
        eng = Rectangle(width=ENGLISH_MIN * per_min, height=0.7, color=WORD, fill_color=WORD, fill_opacity=0.6)
        rest = Rectangle(width=(TOTAL_MIN - ENGLISH_MIN) * per_min, height=0.7, color=RATIO, fill_color=RATIO,
                         fill_opacity=0.25)
        bar = VGroup(eng, rest).arrange(RIGHT, buff=0)
        bar.move_to(DOWN * 0.3)
        total = text(f"Section A:  {TOTAL_MIN} minutes for {TOTAL_Q} questions", LABEL, INK).next_to(bar, UP, buff=0.9)
        eng_label = text(f"English ≈ {ENGLISH_MIN} min", LABEL, WORD, BOLD).next_to(eng, DOWN, buff=0.25)\
            .align_to(eng, LEFT)
        rest_label = text(f"Quant + Reasoning ≈ {TOTAL_MIN - ENGLISH_MIN} min", LABEL, RATIO, BOLD)\
            .next_to(rest, UP, buff=0.25)
        need = pill("…where you really need them", FOCUS, size=SMALL).next_to(eng_label, DOWN, buff=0.6)\
            .set_x(rest.get_center()[0])
        self.no_overlap(head, total, rest_label, bar, eng_label)
        self.no_overlap(eng_label, need)
        self.validator.check_in_frame(VGroup(total, bar, eng_label, rest_label, need))

        n = self.narrate(
            id="speed_04",
            text="Section A gives you sixty minutes for fifty questions. If English takes you eight minutes, the remaining "
                 "fifty-two go to quant and reasoning, where you really need them.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(VGroup(cards, timers)))
        self.at_word(n, "sixty")
        self.play(FadeIn(total, shift=DOWN * 0.1), FadeIn(rest), FadeIn(eng))
        self.at_word(n, "eight")
        self.play(Indicate(eng, color=WORD, scale_factor=1.1), FadeIn(eng_label, shift=UP * 0.1))
        self.at_word(n, "fifty-two")
        self.play(FadeIn(rest_label, shift=DOWN * 0.1))
        self.at_word(n, "need")
        self.play(FadeIn(need, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S01_reason_speed")

    # ================================ 2. REASON 2: WRONG ANSWERS COST ==========

    def reason_marking(self):
        self.scene_start("S02_reason_marking", title="Reason 2 - Wrong Answers Cost You")

        head = self.heading("Reason 2  ·  Guessing is expensive", BAD)
        pans = VGroup(pill(f"+{MARKS_RIGHT}  correct", GOOD, size=BODY), pill(f"−{abs(MARKS_WRONG)}  wrong", BAD, size=BODY))\
            .arrange(RIGHT, buff=1.6)
        beam = Line(pans[0].get_bottom() + DOWN * 0.15, pans[1].get_bottom() + DOWN * 0.15, color=MUTED, stroke_width=5)
        pivot = Triangle(color=MUTED, fill_color=MUTED, fill_opacity=0.6).scale(0.2).next_to(beam, DOWN, buff=0.02)
        scale = VGroup(pans, beam, pivot)
        tiles = VGroup(*[pill(l, INK, size=BODY, fill_opacity=0.06) for l in "ABCD"]).arrange(RIGHT, buff=0.4)
        blind = text(f"blind guess (4 options):  worth {expected_marks(4)} on average", LABEL, MUTED)
        better = text(f"two removed (2 options):  worth +{expected_marks(2)} on average", LABEL, GOOD)
        guess = VGroup(tiles, blind, better).arrange(DOWN, buff=0.3)
        body = VGroup(scale, guess).arrange(DOWN, buff=0.6)
        fit_within(body, SAFE_W, SAFE_H - head.height - 2.4)
        body.next_to(head, DOWN, buff=0.5)
        crosses = VGroup(*[Line(t.get_corner(DL), t.get_corner(UR), color=BAD, stroke_width=4) for t in tiles[2:]])
        method = steps_strip(["Method", "eliminate", "then answer"], [WORD, BAD, GOOD], size=SMALL)
        no_lists = text("no word lists to memorise", LABEL, MUTED)
        closing = VGroup(no_lists, method).arrange(RIGHT, buff=0.6)
        fit_width(closing, SAFE_W)
        closing.next_to(body, DOWN, buff=0.5)
        self.no_overlap(head, scale, guess, closing)
        self.validator.check_in_frame(VGroup(head, body, closing))

        n = self.narrate(
            id="marking_01",
            text="The second reason is the marking.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "marking")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="marking_02",
            text="A correct answer gives you three marks. A wrong answer takes one away.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "three")
        self.play(Create(beam), FadeIn(pivot), FadeIn(pans[0], shift=DOWN * 0.1))
        self.at_word(n, "wrong")
        self.play(FadeIn(pans[1], shift=DOWN * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="marking_03",
            text="So a blind guess is worth nothing on average. But if you can remove two wrong options, the guess is in "
                 "your favour.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "blind")
        self.play(LaggedStart(*[FadeIn(t, shift=UP * 0.1) for t in tiles], lag_ratio=0.15), FadeIn(blind))
        self.at_word(n, "remove")
        self.play(*[Create(c) for c in crosses], *[t[1].animate.set_opacity(0.35) for t in tiles[2:]])
        self.at_word(n, "favour")
        self.play(FadeIn(better, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="marking_04",
            text="That is why this course does not hand you word lists to memorise. Every lesson gives you a method for "
                 "removing wrong options.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "lists")
        self.play(FadeIn(no_lists, shift=UP * 0.1))
        self.at_word(n, "method")
        self.play(LaggedStart(*[FadeIn(m, shift=RIGHT * 0.1) for m in method], lag_ratio=0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_reason_marking")

    # ================================ 3. REASON 3: SECTION A DECIDES TIES ==========

    def reason_ties(self):
        self.scene_start("S03_reason_ties", title="Reason 3 - Section A Decides Ties")

        head = self.heading("Reason 3  ·  Section A breaks ties", RATIO)
        rows = VGroup(*[VGroup(pill(name, INK, size=LABEL, fill_opacity=0.06), text("same total", LABEL, MUTED),
                               pill("Section A:  " + level, c, size=LABEL)).arrange(RIGHT, buff=0.45)
                        for name, level, c in [("Candidate 1", "higher", GOOD), ("Candidate 2", "lower", MUTED)]])
        rows.arrange(DOWN, buff=0.6, aligned_edge=LEFT)
        rows[0].add(text("↑  ranked higher", LABEL, GOOD, BOLD).next_to(rows[0], RIGHT, buff=0.45))
        easy = pill("easy English marks can decide that", FOCUS, size=LABEL)
        body = VGroup(rows, easy).arrange(DOWN, buff=0.8)
        fit_width(body, SAFE_W)
        body.next_to(head, DOWN, buff=0.9)
        self.no_overlap(head, rows, easy)
        self.validator.check_in_frame(VGroup(head, body))

        n = self.narrate(
            id="ties_01",
            text="The third reason is your rank.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "rank")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="ties_02",
            text="When two candidates have the same total, the one with the higher Section A score is ranked higher. Easy "
                 "English marks can decide that.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "same")
        self.play(*[FadeIn(r[:2], shift=RIGHT * 0.2) for r in rows])
        self.at_word(n, "higher", occurrence=1)
        self.play(*[FadeIn(r[2], shift=LEFT * 0.1) for r in rows])
        self.at_word(n, "ranked")
        self.play(FadeIn(rows[0][3], shift=LEFT * 0.1))
        self.at_word(n, "Easy")
        self.play(FadeIn(easy, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_reason_ties")

    # ================================ 4. WHAT THESE TWO MODULES COVER ==========

    def what_you_learn(self):
        self.scene_start("S04_modules", title="What These Two Modules Cover")

        head = self.heading("What you will learn")
        vocab = self.lesson_card("Module 1  ·  Vocabulary", MODULE_1, WORD)
        grammar = self.lesson_card("Module 2  ·  Grammar", MODULE_2, RATIO)
        vocab_badge = pill(f"≈ {VOCAB_Q} of {ENGLISH_Q}", WORD, size=LABEL)
        grammar_badge = VGroup(pill(f"≈ {GRAMMAR_Q} of {ENGLISH_Q}", RATIO, size=LABEL),
                               text("short: one rule each", SMALL, MUTED)).arrange(RIGHT, buff=0.3)
        cols = VGroup(VGroup(vocab, vocab_badge).arrange(DOWN, buff=0.25),
                      VGroup(grammar, grammar_badge).arrange(DOWN, buff=0.25)).arrange(RIGHT, buff=0.5, aligned_edge=UP)
        later = pill("Later  ·  Verbal Ability and Reading Skills", MUTED, size=SMALL)
        body = VGroup(cols, later).arrange(DOWN, buff=0.35)
        fit_within(body, SAFE_W, SAFE_H - head.height - 1.3)
        body.next_to(head, DOWN, buff=0.35)
        self.no_overlap(head, cols, later)
        self.no_overlap(cols[0], cols[1])
        self.validator.check_in_frame(VGroup(head, body))

        n = self.narrate(
            id="modules_01",
            text="So what will you learn?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "learn")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="modules_02",
            text="Module one is vocabulary. It covers synonyms, antonyms, idioms and phrases, one-word substitution, and "
                 "analogies.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "vocabulary")
        self.play(FadeIn(vocab[0]), FadeIn(vocab[1][0]))
        for row, spoken in zip(vocab[1][1:], ["synonyms", "antonyms", "idioms", "one-word", "analogies"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.35)
        self.wait_for_narration(n)

        n = self.narrate(
            id="modules_03",
            text="In that same paper, about fourteen of the twenty English questions came from these types.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "fourteen")
        self.play(FadeIn(vocab_badge, scale=1.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="modules_04",
            text="Module two is grammar. It covers prepositions, articles, active and passive voice, spotting errors, and "
                 "sentence correction.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "grammar")
        self.play(FadeIn(grammar[0]), FadeIn(grammar[1][0]))
        for row, spoken in zip(grammar[1][1:], ["prepositions", "articles", "active", "spotting", "sentence"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.35)
        self.wait_for_narration(n)

        n = self.narrate(
            id="modules_05",
            text="About five questions came from here. They are short, and each one tests a single rule.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "five")
        self.play(FadeIn(grammar_badge[0], scale=1.2))
        self.at_word(n, "single")
        self.play(FadeIn(grammar_badge[1], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="modules_06",
            text="Sentence arrangement, cloze tests and reading comprehension come after these two modules.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "after")
        self.play(FadeIn(later, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_modules")

    # ==================================== 5. HOW EACH LESSON WORKS ==========

    def how_lessons_work(self):
        self.scene_start("S05_how_lessons_work", title="How Each Lesson Works")

        head = self.heading("How every lesson is built")
        strip = steps_strip(["Spot the question type", "Apply the method", "Eliminate and confirm"], [WORD, RATIO, GOOD])
        fit_width(strip, SAFE_W)
        strip.next_to(head, DOWN, buff=0.5)
        q = OptionQuestion("Opposite of FRUGAL", ["thrifty", "extravagant", "careful", "poor"], "b",
                           {"a": "synonym trap", "c": "synonym trap", "d": "different idea"},
                           word_size=LABEL)
        fit_height(q.group, strip.get_bottom()[1] - 0.5 - (BOTTOM_Y + 0.5))
        q.group.next_to(strip, DOWN, buff=0.5).to_edge(LEFT, buff=SAFE + 0.4)
        note = VGroup(text("not school grammar from the start", LABEL, MUTED),
                      text("how the exam asks…", LABEL, INK), text("…and where it tries to trap you", LABEL, BAD))\
            .arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        fit_width(note, 4.6)
        note.next_to(strip, DOWN, buff=0.7).to_edge(RIGHT, buff=SAFE + 0.4)
        self.no_overlap(head, strip, q.group)
        self.no_overlap(strip, note)
        strikes = {l: q.strike(l) for l in "acd"}
        self.no_overlap(VGroup(*[strikes[l][0] for l in "acd"]), note)
        self.validator.check_in_frame(VGroup(head, strip, q.group, note))

        n = self.narrate(
            id="how_01",
            text="Every lesson follows the same three steps.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "three")
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(strip[1]), FadeIn(strip[3]))
        self.wait_for_narration(n)

        n = self.narrate(
            id="how_02",
            text="First, you learn to spot the question type from its wording.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "First")
        self.play(FadeIn(strip[0], shift=DOWN * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="how_03",
            text="Second, you apply one clear method for that type.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Second")
        self.play(FadeIn(strip[2], shift=DOWN * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="how_04",
            text="Third, you eliminate the wrong options and confirm the one that is left.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Third")
        self.play(FadeIn(strip[4], shift=DOWN * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="how_05",
            text="You are a graduate, so we will not teach you school grammar from the start. We will show you how the exam "
                 "asks the question, and where it tries to trap you.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "graduate")
        self.play(FadeIn(q.word), FadeIn(q.rows, shift=UP * 0.1), FadeIn(note[0], shift=LEFT * 0.1))
        self.at_word(n, "exam")
        self.play(Indicate(strip[0], color=WORD, scale_factor=1.05), FadeIn(note[1], shift=LEFT * 0.1))
        self.at_word(n, "trap")
        self.play(*strikes["a"][1], *strikes["c"][1], *strikes["d"][1], FadeIn(note[2], shift=LEFT * 0.1))
        self.play(*q.confirm()[1], Indicate(strip[4], color=GOOD, scale_factor=1.05))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_how_lessons_work")

    # ================================================ 6. CLOSING ==========

    def closing(self):
        self.scene_start("S06_closing", title="Closing")

        facts = VGroup(pill(f"English ≈ {ENGLISH_Q} questions", WORD, size=LABEL),
                       pill("the fastest part of Section A", GOOD, size=LABEL),
                       pill("it can decide your rank", RATIO, size=LABEL)).arrange(RIGHT, buff=0.4)
        fit_width(facts, SAFE_W)
        reasons = text("Fastest marks   ·   Costly guesses   ·   Tie-breaker", LABEL, MUTED)
        nxt = self.breadcrumb("Next", "Module 1 · Vocabulary", "Lesson 1 · Synonyms")
        VGroup(facts, reasons, nxt).arrange(DOWN, buff=0.8).move_to(UP * 0.2)
        self.no_overlap(facts, reasons, nxt)
        self.validator.check_in_frame(VGroup(facts, reasons, nxt))

        n = self.narrate(
            id="closing_01",
            text="To sum up: English is about twenty questions, it is the fastest part of Section A, and it can decide your "
                 "rank.",
            voice="default",
            subtitle=True,
        )
        for f, spoken in zip(facts, ["twenty", "fastest", "rank"]):
            self.at_word(n, spoken)
            self.play(FadeIn(f, shift=UP * 0.1), run_time=0.5)
        self.wait_for_narration(n)

        n = self.narrate(
            id="closing_02",
            text="We start with the largest group of questions: synonyms. See you in lesson one.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "start")
        self.play(FadeIn(reasons, shift=UP * 0.1))
        self.at_word(n, "synonyms")
        self.play(FadeIn(nxt, shift=UP * 0.1))
        self.at_word(n, "lesson")
        self.play(Indicate(nxt[4], color=RATIO, scale_factor=1.1))
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S06_closing")

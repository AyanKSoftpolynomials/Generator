"""
animation.py for the LMS video generator.

Course : Pre-C-CAT - Section A - English
Video  : Module 1 Introduction - Why Vocabulary Is in the Pre-C-CAT Course

Source script:
  C:\\Scripts\\Section A\\English - Module 1 Introduction - Why Vocabulary.md

Built on the golden-reference pattern:
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``;
  * layouts stacked with next_to and guarded with ``no_overlap``; nothing is
    ever animated onto or into another box.

Module introduction. Opening rule from the script: a silent breadcrumb and a one-line recap of the English introduction, no spoken course welcome.
The narration is the script's. The TENACIOUS question is data: the answer on screen is whatever survives the listed traps (asserted to be "Persistent").
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
TOTAL_Q, ENGLISH_Q, VOCAB_Q, MARKS_RIGHT, MARKS_WRONG = 50, 20, 14, 3, -1

# The hook question: reached by elimination, not by knowing the word.
HOOK_WORD = "TENACIOUS"
HOOK_OPTIONS = ["Weak", "Persistent", "Tender", "Brief"]
HOOK_TRAPS = {"a": "not a strong word", "c": "sounds similar: trap", "d": "not a strong word"}

# (lesson name, example shown on its row)
LESSONS = [("Synonyms", "LUCID  →  Clear"),
           ("Antonyms", "FRUGAL  →  Extravagant"),
           ("Idioms & Phrases", "bury the hatchet  →  make peace"),
           ("One-Word Substitution", "knows many languages  →  Polyglot"),
           ("Analogies", "Reptile : Lizard  ::  Flower : Daisy")]


def expected_marks(options_left):
    """Average marks for a guess among ``options_left`` options (+3 / −1 marking)."""
    p = Fraction(1, options_left)
    return p * MARKS_RIGHT + (1 - p) * MARKS_WRONG


def survivor(options, traps):
    """The one option left after every trap is removed."""
    left = [o for l, o in zip("abcd", options) if l not in traps]
    assert len(left) == 1
    return left[0]


assert survivor(HOOK_OPTIONS, HOOK_TRAPS) == "Persistent"
assert VOCAB_Q <= ENGLISH_Q <= TOTAL_Q and expected_marks(4) == 0 and expected_marks(2) == 1 and len(LESSONS) == 5


def question_squares(n=TOTAL_Q, side=0.42):
    """Section A as a block of n small grey squares (10 per row)."""
    squares = VGroup(*[Square(side_length=side, stroke_color=MUTED, stroke_width=2, fill_color=MUTED, fill_opacity=0.25)
                       for _ in range(n)])
    return squares.arrange_in_grid(rows=n // 10, cols=10, buff=0.1)


def steps_strip(labels, colors, size=LABEL, buff=0.25):
    """Numbered steps in a row, joined by arrows.  Steps are at [0], [2], [4]."""
    parts = []
    for i, (label, c) in enumerate(zip(labels, colors)):
        if i:
            parts.append(text("→", size, MUTED))
        parts.append(pill(f"{i + 1}  {label}", c, size=size))
    return VGroup(*parts).arrange(RIGHT, buff=buff)


def lesson_rows(lessons, first_number=1, color=WORD, example_width=None, example_size=LABEL):
    """One row per lesson: number chip, name, example.  Names and examples are column-aligned."""
    names = [text(name, LABEL, color, BOLD) for name, _ in lessons]
    gap = max(n.width for n in names) + 0.6
    rows = VGroup()
    for i, (name, (_, example)) in enumerate(zip(names, lessons)):
        num = pill(str(first_number + i), color, size=SMALL)
        ex = text(example, example_size, INK) if example_width is None else \
            fitted_text(example, example_width, example_size, INK, NORMAL, max_lines=2)
        name.next_to(num, RIGHT, buff=0.3)
        ex.next_to(num, RIGHT, buff=0.3 + gap)
        rows.add(VGroup(num, name, ex))
    return rows.arrange(DOWN, buff=0.32, aligned_edge=LEFT)


class WhyVocabularyVideo(LMSScene):
    lesson_title = "Why Vocabulary Is in the Pre-C-CAT Course"

    def construct(self):
        self.camera.background_color = BG

        self.opening_recap()
        self.word_lists()
        self.why_it_pays()
        self.five_types()
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

    # ========================================= 0. OPENING AND RECAP ==========
    # Opening rule: silent breadcrumb, a one-line recap, no spoken course welcome.

    def opening_recap(self):
        self.scene_start("S00_recap", title="Opening and Recap")

        crumb = self.breadcrumb("English", "Module 1 · Vocabulary", "Introduction")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        paper = text("Section A  ·  50 questions", LABEL, MUTED, BOLD)
        squares = question_squares()
        for s_ in squares[:ENGLISH_Q]:
            s_.set_fill(WORD, opacity=0.8).set_stroke(WORD)
        left = VGroup(paper, squares).arrange(DOWN, buff=0.3)
        english = pill(f"English ≈ {ENGLISH_Q}", WORD, size=LABEL)
        vocab = pill(f"Vocabulary ≈ {VOCAB_Q}", FOCUS, size=LABEL)
        source = text("a recent memory-based paper", SMALL, MUTED)
        module = pill("This module: those fourteen", GOOD, size=LABEL)
        right = VGroup(english, vocab, source, module).arrange(DOWN, buff=0.4, aligned_edge=LEFT)
        block = VGroup(left, right).arrange(RIGHT, buff=0.9)
        fit_width(block, SAFE_W)
        block.move_to(DOWN * 0.2)
        self.no_overlap(crumb, block)
        self.no_overlap(left, right)
        self.validator.check_in_frame(VGroup(crumb, block))

        n = self.narrate(
            id="recap_01",
            text="In the last video, you saw that about twenty of the fifty Section A questions are English.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.at_word(n, "twenty")
        self.play(FadeIn(english, shift=LEFT * 0.1))
        self.at_word(n, "fifty")
        self.play(FadeIn(paper), LaggedStart(*[FadeIn(s_, scale=0.6) for s_ in squares], lag_ratio=0.02), run_time=1.2)
        self.wait_for_narration(n)

        n = self.narrate(
            id="recap_02",
            text="In a recent memory-based paper, about fourteen of those twenty were vocabulary questions. This module is "
                 "about those fourteen.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "memory-based")
        self.play(FadeIn(source, shift=UP * 0.1))
        self.at_word(n, "fourteen", occurrence=1)
        self.play(LaggedStart(*[s_.animate.set_fill(FOCUS, opacity=0.9).set_stroke(FOCUS) for s_ in squares[:VOCAB_Q]],
                              lag_ratio=0.05), FadeIn(vocab, shift=LEFT * 0.1), run_time=1.2)
        self.at_word(n, "module")
        self.play(FadeIn(module, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_recap")

    # ================================ 1. THE PROBLEM WITH WORD LISTS ==========

    def word_lists(self):
        self.scene_start("S01_word_lists", title="The Problem with Word Lists")

        head = self.heading("Can you memorise the dictionary?")
        cards = VGroup(*[pill(w, INK, size=SMALL, fill_opacity=0.06) for w in
                         ["abate", "benign", "candid", "diligent", "ephemeral", "frugal", "garrulous"]])
        more = text("…", BODY, MUTED, BOLD)
        stack = VGroup(more, *cards[::-1]).arrange(DOWN, buff=0.12)      # the list grows upward
        fit_height(stack, SAFE_H - head.height - 1.6)
        stack.next_to(head, DOWN, buff=0.5).set_x(-3.4)
        notes = VGroup(text("the list never ends", LABEL, BAD, BOLD), text("the exam can pick any word", LABEL, INK),
                       text("you cannot learn them all", LABEL, MUTED)).arrange(DOWN, buff=0.5, aligned_edge=LEFT)
        notes.next_to(stack, RIGHT, buff=1.2)
        self.no_overlap(head, stack)
        self.no_overlap(head, notes)
        self.no_overlap(stack, notes)
        self.validator.check_in_frame(VGroup(head, stack, notes))

        n = self.narrate(
            id="lists_01",
            text="Most students prepare for vocabulary in one way. They memorise word lists.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Most")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "lists")
        self.play(LaggedStart(*[FadeIn(c, shift=UP * 0.1) for c in cards[:3]], lag_ratio=0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="lists_02",
            text="The trouble is that the list never ends. The exam can pick any word, and you cannot learn them all.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "never")
        self.play(LaggedStart(*[FadeIn(c, shift=UP * 0.1) for c in cards[3:]], FadeIn(more), lag_ratio=0.15),
                  FadeIn(notes[0], shift=LEFT * 0.1))
        self.at_word(n, "any")
        self.play(Indicate(cards[4], color=FOCUS, scale_factor=1.15), FadeIn(notes[1], shift=LEFT * 0.1))
        self.at_word(n, "cannot")
        self.play(FadeIn(notes[2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        # One question, solved without knowing the word.
        ask = text("Choose the word most similar in meaning to", SMALL, MUTED)
        q = OptionQuestion(HOOK_WORD, HOOK_OPTIONS, "b", HOOK_TRAPS, word_size=BODY)
        left = VGroup(ask, q.group).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        fit_height(left, SAFE_H - head.height - 1.2)
        left.next_to(head, DOWN, buff=0.5).to_edge(LEFT, buff=SAFE + 0.3)
        strikes = {l: q.strike(l) for l in "acd"}
        box, confirm = q.confirm()
        side = VGroup(text("never seen this word?", LABEL, MUTED), text("you can still remove options", LABEL, INK),
                      text("answer reached with a method", LABEL, GOOD), pill("Method beats memory", FOCUS, size=BODY),
                      text("words too, but the method comes first", SMALL, MUTED))\
            .arrange(DOWN, buff=0.4, aligned_edge=LEFT)
        fit_width(side, 5.2)
        side.next_to(head, DOWN, buff=0.7).to_edge(RIGHT, buff=SAFE)
        tags = VGroup(*[strikes[l][0] for l in "acd"])
        self.no_overlap(head, left)
        self.no_overlap(head, side)
        self.no_overlap(left, side)
        self.no_overlap(tags, side)
        self.validator.check_in_frame(VGroup(head, left, side, tags))

        n = self.narrate(
            id="lists_03",
            text="Take this question. Suppose you have never seen the word tenacious.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(VGroup(stack, notes)))
        self.at_word(n, "question")
        self.play(FadeIn(ask), FadeIn(q.word), FadeIn(q.rows, shift=UP * 0.1))
        self.at_word(n, "tenacious")
        self.play(Indicate(q.word, color=WORD, scale_factor=1.1), FadeIn(side[0], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="lists_04",
            text="You can still remove options. Tender only sounds similar, and that is a common trap. Weak and brief do "
                 "not fit a word built to sound strong.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "remove")
        self.play(FadeIn(side[1], shift=LEFT * 0.1))
        self.at_word(n, "Tender")
        self.play(*strikes["c"][1])
        self.at_word(n, "Weak")
        self.play(*strikes["a"][1])
        self.at_word(n, "brief")
        self.play(*strikes["d"][1])
        self.wait_for_narration(n)

        n = self.narrate(
            id="lists_05",
            text="That leaves persistent. You reached the answer with a method.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "persistent")
        self.play(*confirm)
        self.at_word(n, "method")
        self.play(FadeIn(side[2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="lists_06",
            text="That is what this module teaches. You will learn words too, but the method comes first.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "teaches")
        self.play(FadeIn(side[3], scale=1.1))
        self.at_word(n, "words")
        self.play(FadeIn(side[4], shift=UP * 0.1))
        self.at_word(n, "first")
        self.play(Indicate(side[3], color=FOCUS, scale_factor=1.08))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S01_word_lists")

    # ================================= 2. WHY IT IS WORTH YOUR TIME ==========

    def why_it_pays(self):
        self.scene_start("S02_why_it_pays", title="Why It Is Worth Your Time")

        head = self.heading("Why vocabulary pays", GOOD)
        line = self.card(VGroup(text("Synonym of", LABEL, MUTED), text("LUCID", LABEL, WORD, BOLD), text("?", LABEL, MUTED))
                         .arrange(RIGHT, buff=0.2))
        one = text("a single line", LABEL, INK)
        timer = VGroup(Rectangle(width=15 * 0.12, height=0.3, color=GOOD, fill_color=GOOD, fill_opacity=0.6),
                       text("≈ 15 s", LABEL, GOOD, BOLD)).arrange(RIGHT, buff=0.2)
        top = VGroup(line, one, timer).arrange(RIGHT, buff=0.6)
        scale = VGroup(pill(f"+{MARKS_RIGHT}  correct", GOOD, size=BODY), pill(f"−{abs(MARKS_WRONG)}  wrong", BAD, size=BODY))\
            .arrange(RIGHT, buff=1.2)
        tiles = VGroup(*[pill(l, INK, size=BODY, fill_opacity=0.06) for l in "ABCD"]).arrange(RIGHT, buff=0.4)
        odds = text(f"two removed:  a guess is worth +{expected_marks(2)} on average", LABEL, GOOD)
        bottom = VGroup(tiles, odds).arrange(RIGHT, buff=0.6)
        body = VGroup(top, scale, bottom).arrange(DOWN, buff=0.8)
        fit_within(body, SAFE_W, SAFE_H - head.height - 1.6)
        body.next_to(head, DOWN, buff=0.7)
        crosses = VGroup(*[Line(t.get_corner(DL), t.get_corner(UR), color=BAD, stroke_width=4) for t in tiles[2:]])
        self.no_overlap(head, top, scale, bottom)
        self.no_overlap(line, one, timer)
        self.validator.check_in_frame(VGroup(head, body))

        n = self.narrate(
            id="pays_01",
            text="Vocabulary questions are the shortest questions in the paper.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "shortest")
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(line, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="pays_02",
            text="Each one is a single line, and takes about fifteen seconds.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "single")
        self.play(FadeIn(one, shift=LEFT * 0.1))
        self.at_word(n, "fifteen")
        self.play(GrowFromEdge(timer[0], LEFT), FadeIn(timer[1]), run_time=0.8)
        self.wait_for_narration(n)

        n = self.narrate(
            id="pays_03",
            text="And with one mark lost for every wrong answer, removing even two options before you answer puts the odds "
                 "in your favour.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "lost")
        self.play(FadeIn(scale[0], shift=DOWN * 0.1), FadeIn(scale[1], shift=DOWN * 0.1))
        self.at_word(n, "two")
        self.play(LaggedStart(*[FadeIn(t, shift=UP * 0.1) for t in tiles], lag_ratio=0.1))
        self.play(*[Create(c) for c in crosses], *[t[1].animate.set_opacity(0.35) for t in tiles[2:]], run_time=0.5)
        self.at_word(n, "favour")
        self.play(FadeIn(odds, shift=LEFT * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_why_it_pays")

    # ================================== 3. THE FIVE QUESTION TYPES ==========

    def five_types(self):
        self.scene_start("S03_five_types", title="The Five Question Types")

        head = self.heading("What Module 1 covers")
        rows = lesson_rows(LESSONS)
        trap = pill("trap: a synonym", BAD, size=SMALL).next_to(rows[1][2], RIGHT, buff=0.35)
        table = VGroup(rows, trap)
        top, bot = table.get_corner(UR) + RIGHT * 0.3, table.get_corner(DR) + RIGHT * 0.3
        bracket = VGroup(Line(top + LEFT * 0.15, top), Line(top, bot), Line(bot, bot + LEFT * 0.15))\
            .set_stroke(FOCUS, width=3)
        total = pill(f"≈ {VOCAB_Q} questions", FOCUS, size=LABEL).next_to(bracket, RIGHT, buff=0.2)
        body = VGroup(table, bracket, total)
        fit_within(body, SAFE_W, SAFE_H - head.height - 0.8)
        body.next_to(head, DOWN, buff=0.5)
        self.no_overlap(head, body)
        self.no_overlap(rows[1][2], trap)
        self.no_overlap(table, total)
        self.validator.check_in_frame(VGroup(head, body))

        n = self.narrate(
            id="types_01",
            text="The module has five lessons, one for each question type.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "five")
        self.play(FadeIn(head, shift=DOWN * 0.2), LaggedStart(*[FadeIn(r[0], scale=0.7) for r in rows], lag_ratio=0.12))
        self.wait_for_narration(n)

        n = self.narrate(
            id="types_02",
            text="Lesson one is synonyms: choose the word closest in meaning.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "synonyms")
        self.play(FadeIn(rows[0][1], shift=RIGHT * 0.2))
        self.at_word(n, "closest")
        self.play(FadeIn(rows[0][2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="types_03",
            text="Lesson two is antonyms: choose the opposite. The trap here is picking a synonym by mistake.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "antonyms")
        self.play(FadeIn(rows[1][1], shift=RIGHT * 0.2))
        self.at_word(n, "opposite")
        self.play(FadeIn(rows[1][2], shift=RIGHT * 0.2))
        self.at_word(n, "trap")
        self.play(FadeIn(trap, shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="types_04",
            text="Lesson three is idioms and phrases, where the meaning is not in the individual words.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "idioms")
        self.play(FadeIn(rows[2][1], shift=RIGHT * 0.2))
        self.at_word(n, "meaning")
        self.play(FadeIn(rows[2][2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="types_05",
            text="Lesson four is one-word substitution: one word that replaces a whole description.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "one-word")
        self.play(FadeIn(rows[3][1], shift=RIGHT * 0.2))
        self.at_word(n, "replaces")
        self.play(FadeIn(rows[3][2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="types_06",
            text="Lesson five is analogies: find the relationship in one pair and apply it to another.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "analogies")
        self.play(FadeIn(rows[4][1], shift=RIGHT * 0.2))
        self.at_word(n, "relationship")
        self.play(FadeIn(rows[4][2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="types_07",
            text="All five types appeared in the 2025 recollections.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "five")
        self.play(Create(bracket), FadeIn(total, shift=LEFT * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_five_types")

    # ==================================== 4. HOW EACH LESSON WORKS ==========

    def how_lessons_work(self):
        self.scene_start("S04_how_lessons_work", title="How Each Lesson Works")

        head = self.heading("The same three steps every time")
        strip = steps_strip(["Spot the type", "Use the clues", "Eliminate and confirm"], [WORD, RATIO, GOOD], buff=0.4)
        fit_width(strip, SAFE_W)
        strip.next_to(head, DOWN, buff=0.6)
        wording = VGroup(text("“most similar in meaning”", SMALL, INK), text("→  a synonym question", SMALL, WORD, BOLD))\
            .arrange(DOWN, buff=0.2)
        fit_width(wording, 3.3)
        clues = VGroup(pill("root", RATIO), pill("prefix", RATIO), pill("tone", RATIO)).arrange(DOWN, buff=0.25)
        tiles = VGroup(*[pill(o, INK, size=SMALL, fill_opacity=0.06) for o in HOOK_OPTIONS])\
            .arrange_in_grid(rows=2, cols=2, buff=0.25)
        fit_width(tiles, 3.4)
        for detail, step in zip([wording, clues, tiles], [strip[0], strip[2], strip[4]]):
            detail.next_to(step, DOWN, buff=0.7)
        wrong = [t for t, o in zip(tiles, HOOK_OPTIONS) if o != survivor(HOOK_OPTIONS, HOOK_TRAPS)]
        right = tiles[HOOK_OPTIONS.index(survivor(HOOK_OPTIONS, HOOK_TRAPS))]
        crosses = VGroup(*[Line(t.get_left(), t.get_right(), color=BAD, stroke_width=3) for t in wrong])
        self.no_overlap(head, strip)
        self.no_overlap(wording, clues, tiles)
        self.validator.check_in_frame(VGroup(head, strip, wording, clues, tiles))

        n = self.narrate(
            id="how_01",
            text="Every lesson uses the same three steps.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "three")
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(strip[1]), FadeIn(strip[3]))
        self.wait_for_narration(n)

        n = self.narrate(
            id="how_02",
            text="Spot the question type from its wording.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Spot")
        self.play(FadeIn(strip[0], shift=DOWN * 0.1))
        self.at_word(n, "wording")
        self.play(FadeIn(wording, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="how_03",
            text="Use the clues inside the word: its root, its prefix, and its tone.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "clues")
        self.play(FadeIn(strip[2], shift=DOWN * 0.1))
        for chip, spoken in zip(clues, ["root", "prefix", "tone"]):
            self.at_word(n, spoken)
            self.play(FadeIn(chip, shift=UP * 0.1), run_time=0.4)
        self.wait_for_narration(n)

        n = self.narrate(
            id="how_04",
            text="Then eliminate the wrong options and confirm what is left.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "eliminate")
        self.play(FadeIn(strip[4], shift=DOWN * 0.1), FadeIn(tiles, shift=UP * 0.1))
        self.play(*[Create(c) for c in crosses], *[t[1].animate.set_opacity(0.35) for t in wrong], run_time=0.5)
        self.at_word(n, "confirm")
        self.play(right.animate.set_color(GOOD))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_how_lessons_work")

    # ================================================ 5. CLOSING ==========

    def closing(self):
        self.scene_start("S05_closing", title="Closing")

        facts = VGroup(pill(f"Vocabulary ≈ {VOCAB_Q} of {ENGLISH_Q}", FOCUS, size=LABEL),
                       pill("solved with a method", GOOD, size=LABEL)).arrange(RIGHT, buff=0.5)
        strip = VGroup(*[pill(name, WORD if i == 0 else MUTED, size=SMALL) for i, (name, _) in enumerate(LESSONS)])\
            .arrange(RIGHT, buff=0.25)
        fit_width(strip, SAFE_W)
        nxt = self.breadcrumb("Next", "Lesson 1 · Synonyms")
        VGroup(facts, strip, nxt).arrange(DOWN, buff=0.9).move_to(UP * 0.2)
        self.no_overlap(facts, strip, nxt)
        self.validator.check_in_frame(VGroup(facts, strip, nxt))

        n = self.narrate(
            id="closing_01",
            text="To sum up: vocabulary is the largest group of English questions, and you will solve it with a method.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "largest")
        self.play(FadeIn(facts[0], shift=UP * 0.1))
        self.at_word(n, "method")
        self.play(FadeIn(facts[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="closing_02",
            text="We begin with synonyms. See you in lesson one.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "synonyms")
        self.play(LaggedStart(*[FadeIn(p, shift=UP * 0.1) for p in strip], lag_ratio=0.1))
        self.play(Indicate(strip[0], color=WORD, scale_factor=1.15), run_time=0.6)
        self.at_word(n, "lesson")
        self.play(FadeIn(nxt, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S05_closing")

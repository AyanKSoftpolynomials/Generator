"""
animation.py for the LMS video generator.

Course : Pre-C-CAT - Section A - English
Video  : Module 3 Introduction - Why Verbal Ability Is in the Pre-C-CAT Course

Source script:
  C:\\Scripts\\Section A\\English - Module 3 Introduction - Why Verbal Ability.md

Built on the golden-reference pattern:
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``;
  * layouts stacked with next_to and guarded with ``no_overlap``; nothing is
    ever animated onto or into another box.

Module introduction. Opening rule from the script: a silent breadcrumb and a one-line recap of Modules 1 and 2, no spoken course welcome.
The narration is the script's. The hook answer is whichever option means the predicted word ("rarely"), asserted to be "once in a blue moon". The script says "more than half" of the 2019 English questions were fill-in-the-blank without a count, so 11 of 20 squares are coloured.
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

MARKS_RIGHT, MARKS_WRONG, ENGLISH_Q = 3, -1, 20
FILL_BLANK_2019 = 11            # "more than half" of the 20: the script gives no exact count, so one over half is shown

# The hook question (2019 paper).  Each option with what it would mean in the blank
# (None = not a real expression).  The clue in the sentence fixes the meaning needed.
HOOK_BEFORE, HOOK_CLUE = "I visit my parents", "as I work in a different city."
HOOK_OPTIONS = [("once in a month", "regularly"), ("once in a blue moon", "rarely"),
                ("once in a full moon", None), ("once in a white moon", None)]
PREDICTION = "rarely"


def matches(options, prediction):
    """The options whose meaning is the predicted one."""
    return [o for o, meaning in options if meaning == prediction]


assert matches(HOOK_OPTIONS, PREDICTION) == ["once in a blue moon"]
HOOK_KEY = [o for o, _ in HOOK_OPTIONS].index(matches(HOOK_OPTIONS, PREDICTION)[0])

JUMBLED, ORDERED = "RPSQ", "PQRS"
assert sorted(JUMBLED) == list(ORDERED) and FILL_BLANK_2019 * 2 > ENGLISH_Q

LESSONS = ["Arrangement of Sentences", "Sentence Completion", "Cloze Test"]
FIRST_LESSON = 11


def steps_strip(labels, colors, size=LABEL, buff=0.25):
    """Numbered steps in a row, joined by arrows.  Steps are at [0], [2], [4]."""
    parts = []
    for i, (label, c) in enumerate(zip(labels, colors)):
        if i:
            parts.append(text("→", size, MUTED))
        parts.append(pill(f"{i + 1}  {label}", c, size=size))
    return VGroup(*parts).arrange(RIGHT, buff=buff)


class WhyVerbalAbilityVideo(LMSScene):
    lesson_title = "Why Verbal Ability Is in the Pre-C-CAT Course"

    def construct(self):
        self.camera.background_color = BG

        self.opening_recap()
        self.clue_in_sentence()
        self.why_it_pays()
        self.three_types()
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

    def module_card(self, title, line, color, width):
        body = VGroup(text(title, LABEL, color, BOLD), text(line, LABEL, INK)).arrange(DOWN, buff=0.2)
        return self.card(body, width=width, height=1.8, color=color)

    # ========================================= 0. OPENING AND RECAP ==========
    # Opening rule: silent breadcrumb, a one-line recap of Modules 1 and 2, no spoken welcome.

    def opening_recap(self):
        self.scene_start("S00_recap", title="Opening and Recap")

        crumb = self.breadcrumb("English", "Module 3 · Verbal Ability", "Introduction")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        vocab = self.module_card("Module 1  ·  Vocabulary", "what a word means", WORD, 5.8)
        grammar = self.module_card("Module 2  ·  Grammar", "which rule applies", RATIO, 5.8)
        pair = VGroup(vocab, grammar).arrange(RIGHT, buff=0.6)
        join = text("↓", BODY, MUTED, BOLD)
        verbal = self.module_card("Module 3  ·  Verbal Ability", "words and rules inside a sentence", GOOD, 7.6)
        block = VGroup(pair, join, verbal).arrange(DOWN, buff=0.35)
        fit_within(block, SAFE_W, SAFE_H - crumb.height - 0.8)
        block.next_to(crumb, DOWN, buff=0.5)
        self.no_overlap(crumb, pair, join, verbal)
        self.no_overlap(vocab, grammar)
        self.validator.check_in_frame(VGroup(crumb, block))

        n = self.narrate(
            id="recap_01",
            text="So far, you have handled words on their own, and rules on their own.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.at_word(n, "words")
        self.play(FadeIn(vocab, shift=UP * 0.1))
        self.at_word(n, "rules")
        self.play(FadeIn(grammar, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="recap_02",
            text="In this module, both come together inside a sentence.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "both")
        self.play(FadeIn(join, shift=DOWN * 0.1))
        self.at_word(n, "sentence")
        self.play(FadeIn(verbal, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_recap")

    # ============================ 1. THE CLUE IS ALREADY IN THE SENTENCE ==========

    def clue_in_sentence(self):
        self.scene_start("S01_clue_in_sentence", title="The Clue Is Already in the Sentence")

        head = self.heading("Where is the answer hiding?")
        source = pill("2019 paper", MUTED).next_to(head, RIGHT, buff=0.4)
        before, blank, clue = text(HOOK_BEFORE, BODY, INK), text("________", BODY, MUTED), text(HOOK_CLUE, BODY, INK)
        sentence = VGroup(before, blank, clue).arrange(RIGHT, buff=0.2)
        blank.align_to(before, DOWN)                                    # the blank sits on the baseline
        need = pill(f"needs  →  {PREDICTION}", FOCUS, size=LABEL)
        room = Rectangle(width=1.0, height=need.height + 0.25).set_stroke(width=0)        # never shown
        options = VGroup(*[VGroup(text(f"({l})", LABEL, MUTED), text(o, BODY, INK)).arrange(RIGHT, buff=0.25)
                           for l, (o, _) in zip("abcd", HOOK_OPTIONS)]).arrange(DOWN, buff=0.25, aligned_edge=LEFT)
        notes = VGroup(text("trying every option: slow", LABEL, BAD), text("two of them sound possible", LABEL, MUTED),
                       text("the clue: a reason", LABEL, FOCUS, BOLD), text("known before any option", LABEL, GOOD))\
            .arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        lower = VGroup(options, notes).arrange(RIGHT, buff=1.2, aligned_edge=UP)
        rule = pill("Find the clue.  Predict.  Then look at the options.", GOOD, size=LABEL)
        stack = VGroup(room, sentence, lower, rule).arrange(DOWN, buff=0.4)
        fit_within(stack, SAFE_W, SAFE_H - head.height - 0.5)
        stack.next_to(head, DOWN, buff=0.3)
        need.next_to(sentence, UP, buff=0.15).set_x(blank.get_x())      # above the line, over the blank
        underline = Line(clue.get_corner(DL) + DOWN * 0.1, clue.get_corner(DR) + DOWN * 0.1, color=FOCUS, stroke_width=4)
        key = options[HOOK_KEY]
        others = [r for i, r in enumerate(options) if i != HOOK_KEY]
        box = SurroundingRectangle(key, color=GOOD, buff=0.1, corner_radius=0.1)
        self.no_overlap(head, source)
        self.no_overlap(head, need, sentence, lower, rule)
        self.no_overlap(underline, lower)
        self.no_overlap(options, notes)
        self.validator.check_in_frame(VGroup(head, source, stack, need))

        n = self.narrate(
            id="clue_01",
            text="Look at this question from the 2019 paper.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "question")
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(sentence, shift=UP * 0.1))
        self.at_word(n, "2019")
        self.play(FadeIn(source, shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="clue_02",
            text="Most students go straight to the options, and try each one in the blank.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "options")
        self.play(LaggedStart(*[FadeIn(r, shift=UP * 0.1) for r in options], lag_ratio=0.15))
        self.at_word(n, "try")
        self.play(LaggedStart(*[Indicate(r, color=WORD, scale_factor=1.06) for r in options], lag_ratio=0.5),
                  run_time=1.8)
        self.wait_for_narration(n)

        n = self.narrate(
            id="clue_03",
            text="That is slow, and two of them will sound possible.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "slow")
        self.play(FadeIn(notes[0], shift=LEFT * 0.1))
        self.at_word(n, "two")
        self.play(Indicate(options[0], color=FOCUS, scale_factor=1.06), Indicate(options[1], color=FOCUS, scale_factor=1.06),
                  FadeIn(notes[1], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="clue_04",
            text="Read the sentence first. It gives a reason: as I work in a different city.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Read")
        self.play(options.animate.set_opacity(0.25), Indicate(sentence, color=INK, scale_factor=1.03))
        self.at_word(n, "reason")
        self.play(Create(underline), clue.animate.set_color(FOCUS), FadeIn(notes[2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="clue_05",
            text="So the blank must mean rarely. You know that before you see a single option.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "rarely")
        self.play(FadeIn(need, shift=DOWN * 0.1), blank.animate.set_color(FOCUS))
        self.at_word(n, "before")
        self.play(FadeIn(notes[3], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="clue_06",
            text="Now only one option fits: once in a blue moon.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "one")
        self.play(options.animate.set_opacity(1.0))
        self.at_word(n, "blue")
        self.play(Create(box), key[1].animate.set_color(GOOD), *[r.animate.set_opacity(0.35) for r in others])
        self.wait_for_narration(n)

        n = self.narrate(
            id="clue_07",
            text="The sentence always carries a clue. This module teaches you to find it.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "clue")
        self.play(FadeIn(rule, shift=UP * 0.1))
        self.at_word(n, "find")
        self.play(Indicate(rule, color=GOOD, scale_factor=1.05))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S01_clue_in_sentence")

    # ================================= 2. WHY IT IS WORTH YOUR TIME ==========

    def why_it_pays(self):
        self.scene_start("S02_why_it_pays", title="Why It Is Worth Your Time")

        head = self.heading("Why verbal ability pays", GOOD)
        label = text("2019 paper  ·  English questions", LABEL, MUTED, BOLD)
        squares = VGroup(*[Square(side_length=0.42, stroke_color=MUTED, stroke_width=2, fill_color=MUTED, fill_opacity=0.25)
                           for _ in range(ENGLISH_Q)]).arrange(RIGHT, buff=0.1)
        half = pill("fill in the blank  ·  more than half", WORD, size=LABEL)
        count = VGroup(label, squares, half).arrange(DOWN, buff=0.25)
        reuse = VGroup(pill("Module 1  ·  Vocabulary", WORD, size=SMALL), text("→", LABEL, MUTED),
                       pill("a blank, with a sentence around it", FOCUS, size=SMALL), text("←", LABEL, MUTED),
                       pill("Module 2  ·  Grammar", RATIO, size=SMALL)).arrange(RIGHT, buff=0.25)
        scale = VGroup(pill(f"+{MARKS_RIGHT}  correct", GOOD, size=LABEL), pill(f"−{abs(MARKS_WRONG)}  wrong", BAD, size=LABEL),
                       text("predict first: skip what only sounds right", LABEL, INK)).arrange(RIGHT, buff=0.4)
        body = VGroup(count, reuse, scale).arrange(DOWN, buff=0.7)
        fit_within(body, SAFE_W, SAFE_H - head.height - 0.9)
        body.next_to(head, DOWN, buff=0.5)
        self.no_overlap(head, count, reuse, scale)
        self.no_overlap(label, squares, half)
        self.validator.check_in_frame(VGroup(head, body))

        n = self.narrate(
            id="pays_01",
            text="These questions are common.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "common")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="pays_02",
            text="In the 2019 paper, more than half of the English questions asked you to fill a blank.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "2019")
        self.play(FadeIn(label), LaggedStart(*[FadeIn(s_, scale=0.6) for s_ in squares], lag_ratio=0.04), run_time=1.0)
        self.at_word(n, "half")
        self.play(LaggedStart(*[s_.animate.set_fill(WORD, opacity=0.8).set_stroke(WORD) for s_ in squares[:FILL_BLANK_2019]],
                              lag_ratio=0.06), FadeIn(half, shift=UP * 0.1), run_time=1.2)
        self.wait_for_narration(n)

        n = self.narrate(
            id="pays_03",
            text="They also reuse what you already know. Every blank is a vocabulary question or a grammar question, with a "
                 "sentence around it.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "reuse")
        self.play(FadeIn(reuse[0], shift=RIGHT * 0.1), FadeIn(reuse[4], shift=LEFT * 0.1))
        self.at_word(n, "blank")
        self.play(FadeIn(reuse[1]), FadeIn(reuse[3]), FadeIn(reuse[2], scale=1.05))
        self.wait_for_narration(n)

        n = self.narrate(
            id="pays_04",
            text="And because a wrong answer costs a mark, predicting the answer first keeps you away from the options that "
                 "only sound right.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "wrong")
        self.play(FadeIn(scale[0], shift=UP * 0.1), FadeIn(scale[1], shift=UP * 0.1))
        self.at_word(n, "predicting")
        self.play(FadeIn(scale[2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_why_it_pays")

    # ================================= 3. THE THREE QUESTION TYPES ==========

    def three_types(self):
        self.scene_start("S03_three_types", title="The Three Question Types")

        head = self.heading("What Module 3 covers")
        nums = [pill(str(FIRST_LESSON + i), RATIO, size=SMALL) for i in range(3)]
        names = [text(name, LABEL, RATIO, BOLD) for name in LESSONS]
        tags = [pill("on the syllabus", MUTED), pill("the type you just saw", GOOD), pill("on the syllabus", MUTED)]
        tops = [VGroup(num, name, tag).arrange(RIGHT, buff=0.3) for num, name, tag in zip(nums, names, tags)]

        jumbled = VGroup(*[pill(l, MUTED) for l in JUMBLED]).arrange(RIGHT, buff=0.12)
        ordered = VGroup(*[pill(l, WORD) for l in ORDERED]).arrange(RIGHT, buff=0.12)
        arrange_note = text("opener first, then fixed pairs", SMALL, INK)
        show_1 = VGroup(jumbled, text("→", LABEL, MUTED), ordered, arrange_note).arrange(RIGHT, buff=0.3)

        blank_line = text(f"{HOOK_BEFORE} ____ {HOOK_CLUE}", SMALL, INK)
        blanks_note = text("one or two blanks", SMALL, MUTED)
        show_2 = VGroup(blank_line, blanks_note).arrange(RIGHT, buff=0.4)

        clue_word = pill("clue word", MUTED)
        gaps = VGroup(*[pill(f"({i})", MUTED) for i in range(1, 6)]).arrange(RIGHT, buff=0.12)
        cloze_note = text("clue in another sentence", SMALL, INK)
        show_3 = VGroup(clue_word, text("…", LABEL, MUTED), gaps, cloze_note).arrange(RIGHT, buff=0.3)

        blocks = VGroup()
        for top, show in zip(tops, [show_1, show_2, show_3]):
            indent = Rectangle(width=0.7, height=0.1).set_stroke(width=0)                 # never shown
            blocks.add(VGroup(top, VGroup(indent, show).arrange(RIGHT, buff=0)).arrange(DOWN, buff=0.22, aligned_edge=LEFT))
        blocks.arrange(DOWN, buff=0.5, aligned_edge=LEFT)
        fit_within(blocks, SAFE_W, SAFE_H - head.height - 0.9)
        blocks.next_to(head, DOWN, buff=0.5)
        self.no_overlap(head, *blocks)
        for top, show in zip(tops, [show_1, show_2, show_3]):
            self.no_overlap(top, show)
        self.validator.check_in_frame(VGroup(head, blocks))

        n = self.narrate(
            id="types_01",
            text="The module has three lessons.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "three")
        self.play(FadeIn(head, shift=DOWN * 0.2), LaggedStart(*[FadeIn(num, scale=0.7) for num in nums], lag_ratio=0.15))
        self.wait_for_narration(n)

        n = self.narrate(
            id="types_02",
            text="Lesson eleven is arrangement of sentences. You get jumbled sentences and put them in order. It is on the "
                 "syllabus.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "arrangement")
        self.play(FadeIn(names[0], shift=RIGHT * 0.2))
        self.at_word(n, "jumbled")
        self.play(LaggedStart(*[FadeIn(t, shift=UP * 0.1) for t in jumbled], lag_ratio=0.12))
        self.at_word(n, "order")
        self.play(FadeIn(show_1[1]), LaggedStart(*[FadeIn(t, shift=UP * 0.1) for t in ordered], lag_ratio=0.12))
        self.at_word(n, "syllabus")
        self.play(FadeIn(tags[0], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="types_03",
            text="The method is to find the opening sentence, and then the pairs that must stay together.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "opening")
        self.play(Indicate(ordered[0], color=FOCUS, scale_factor=1.2), FadeIn(arrange_note, shift=LEFT * 0.1))
        self.at_word(n, "pairs")
        self.play(Indicate(ordered[1], color=GOOD, scale_factor=1.2), Indicate(ordered[2], color=GOOD, scale_factor=1.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="types_04",
            text="Lesson twelve is sentence completion: one sentence, one or two blanks. This is the type you just saw.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "completion")
        self.play(FadeIn(names[1], shift=RIGHT * 0.2))
        self.at_word(n, "blanks")
        self.play(FadeIn(blank_line, shift=UP * 0.1), FadeIn(blanks_note, shift=LEFT * 0.1))
        self.at_word(n, "saw")
        self.play(FadeIn(tags[1], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="types_05",
            text="Lesson thirteen is the cloze test: a short passage with several blanks. It is also on the syllabus.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "cloze")
        self.play(FadeIn(names[2], shift=RIGHT * 0.2))
        self.at_word(n, "passage")
        self.play(FadeIn(clue_word), FadeIn(show_3[1]), LaggedStart(*[FadeIn(g, shift=UP * 0.1) for g in gaps], lag_ratio=0.1))
        self.at_word(n, "syllabus")
        self.play(FadeIn(tags[2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="types_06",
            text="Here, the clue for one blank often sits in another sentence.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "clue")
        self.play(Indicate(gaps[2], color=FOCUS, scale_factor=1.2), Indicate(clue_word, color=FOCUS, scale_factor=1.1))
        self.at_word(n, "another")
        self.play(FadeIn(cloze_note, shift=LEFT * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_three_types")

    # ==================================== 4. HOW EACH LESSON WORKS ==========

    def how_lessons_work(self):
        self.scene_start("S04_how_lessons_work", title="How Each Lesson Works")

        head = self.heading("The same three steps every time")
        strip = steps_strip(["Find the clue", "Predict", "Match and eliminate"], [FOCUS, RATIO, GOOD], buff=0.4)
        fit_width(strip, SAFE_W)
        strip.next_to(head, DOWN, buff=0.6)
        clues = VGroup(pill("a reason", FOCUS), pill("a contrast", FOCUS), pill("a linking word", FOCUS))\
            .arrange(DOWN, buff=0.22)
        predict = VGroup(text(f"blank = “{PREDICTION}”", SMALL, RATIO, BOLD), text("before the options", SMALL, MUTED))\
            .arrange(DOWN, buff=0.22)
        tiles = VGroup(*[pill(o.replace("once in a ", ""), INK, size=SMALL, fill_opacity=0.06) for o, _ in HOOK_OPTIONS])\
            .arrange(DOWN, buff=0.2)
        for detail, step, width in zip([clues, predict, tiles], [strip[0], strip[2], strip[4]], [2.9, 2.9, 2.9]):
            fit_width(detail, width)
            detail.next_to(step, DOWN, buff=0.6)
        wrong = [t for i, t in enumerate(tiles) if i != HOOK_KEY]
        crosses = VGroup(*[Line(t.get_left(), t.get_right(), color=BAD, stroke_width=3) for t in wrong])
        self.no_overlap(head, strip)
        self.no_overlap(clues, predict, tiles)
        self.validator.check_in_frame(VGroup(head, strip, clues, predict, tiles))

        n = self.narrate(
            id="how_01",
            text="Every lesson uses three steps.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "three")
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(strip[1]), FadeIn(strip[3]))
        self.wait_for_narration(n)

        n = self.narrate(
            id="how_02",
            text="Find the clue: a reason, a contrast, or a linking word.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Find")
        self.play(FadeIn(strip[0], shift=DOWN * 0.1))
        for chip, spoken in zip(clues, ["reason", "contrast", "linking"]):
            self.at_word(n, spoken)
            self.play(FadeIn(chip, shift=UP * 0.1), run_time=0.4)
        self.wait_for_narration(n)

        n = self.narrate(
            id="how_03",
            text="Predict what the answer must mean, before you read the options.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Predict")
        self.play(FadeIn(strip[2], shift=DOWN * 0.1), FadeIn(predict[0], shift=UP * 0.1))
        self.at_word(n, "before")
        self.play(FadeIn(predict[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="how_04",
            text="Then match your prediction to the options, and eliminate the rest.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "match")
        self.play(FadeIn(strip[4], shift=DOWN * 0.1), FadeIn(tiles, shift=UP * 0.1))
        self.play(tiles[HOOK_KEY].animate.set_color(GOOD), run_time=0.5)
        self.at_word(n, "eliminate")
        self.play(*[Create(c) for c in crosses], *[t[1].animate.set_opacity(0.35) for t in wrong])
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_how_lessons_work")

    # ================================================ 5. CLOSING ==========

    def closing(self):
        self.scene_start("S05_closing", title="Closing")

        facts = VGroup(pill("words + rules, inside a sentence", WORD, size=LABEL),
                       pill("the sentence gives the clue", FOCUS, size=LABEL)).arrange(RIGHT, buff=0.5)
        fit_width(facts, SAFE_W)
        strip = VGroup(*[pill(name, RATIO if i == 0 else MUTED, size=SMALL) for i, name in enumerate(LESSONS)])\
            .arrange(RIGHT, buff=0.3)
        fit_width(strip, SAFE_W)
        nxt = self.breadcrumb("Next", f"Lesson {FIRST_LESSON} · {LESSONS[0]}")
        VGroup(facts, strip, nxt).arrange(DOWN, buff=0.9).move_to(UP * 0.2)
        self.no_overlap(facts, strip, nxt)
        self.validator.check_in_frame(VGroup(facts, strip, nxt))

        n = self.narrate(
            id="closing_01",
            text="To sum up: verbal ability puts words and rules inside a sentence, and the sentence gives you the clue.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "words")
        self.play(FadeIn(facts[0], shift=UP * 0.1))
        self.at_word(n, "clue")
        self.play(FadeIn(facts[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="closing_02",
            text="We begin with arranging sentences. See you in lesson eleven.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "arranging")
        self.play(LaggedStart(*[FadeIn(p, shift=UP * 0.1) for p in strip], lag_ratio=0.15))
        self.play(Indicate(strip[0], color=RATIO, scale_factor=1.12), run_time=0.6)
        self.at_word(n, "lesson")
        self.play(FadeIn(nxt, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S05_closing")

"""
animation.py for the LMS video generator.

Course : C-CAT - Section A - English
Module : Module 2 - Grammar
Lesson : Lesson 10 - Sentence Correction
Video  : 01 - Introduction to Sentence Correction (Video 1 of 6)

Source script:
  C:\\Scripts\\01 - Introduction to Sentence Correction.pdf

Built on the golden-reference pattern:
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``;
  * layouts stacked with next_to and guarded with ``no_overlap``; nothing is
    ever animated onto or into another box.

First video of Lesson 10: the intro recaps Lesson 9 (error spotting, the S-T-P-A-W scan) and announces the new lesson.
judge(options) runs the three tests on a set of options: each option carries the test it fails (FIX, CLEAN or FAITHFUL) or None, exactly one passes, and the strike reasons are built from it. The hook and the worked examples use it.
The "three tests" card (fix, clean, faithful, tie-break) stays pinned top-right through the worked examples and Hook, Solved; the failed test lights up as each option is struck.
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

TESTS = [("FIX", "removes the original error", GOOD), ("CLEAN", "adds no new error", WORD),
         ("FAITHFUL", "keeps the original meaning", SECOND)]
TEST_COL = {name: c for name, _, c in TESTS}


def judge(options):
    """Run the three tests on a set of options.
    ``options`` = [(text, failed test or None, reason), ...].  Exactly one option passes all three.
    Returns (option texts, key letter, {letter: 'TEST ✗: reason'})."""
    letters = "abcd"[:len(options)]
    keys = [l for l, (_t, failed, _r) in zip(letters, options) if failed is None]
    assert len(keys) == 1, keys
    assert all(failed in (None, *TEST_COL) for _t, failed, _r in options)
    traps = {l: f"{failed} ✗:  {reason}" for l, (_t, failed, reason) in zip(letters, options) if failed}
    return [t for t, _f, _r in options], keys[0], traps


HOOK_Q = judge([("asked me why I was late", None, ""),
                ("asked me that why was I late", "FIX", "keeps “that”, question order"),
                ("asked me why was I late", "CLEAN", "question order “was I”"),
                ("No improvement", "FIX", "keeps the error")])
assert HOOK_Q[1] == "a"


class IntroductionToSentenceCorrectionVideo(LMSScene):
    lesson_title = "Introduction to Sentence Correction"

    def construct(self):
        self.camera.background_color = BG

        self.lesson_intro()
        self.hook()
        self.concept()
        self.why_you_need_it()
        self.analogy()
        self.example_know()
        self.example_gone()
        self.example_each()
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

    def tests_pin(self):
        return self.steps_pin("three tests", [("FIX: the error is gone", GOOD), ("CLEAN: no new error", WORD),
                                              ("FAITHFUL: same meaning", SECOND), ("a tie?  the shorter one", RATIO)])

    def light_test(self, name):
        return self.pin_step([t for t, _, _ in TESTS].index(name), color=TEST_COL[name])

    def note_card(self, part="asked me that why I was late", good=False):
        head = text("FEEDBACK NOTE", SMALL, RATIO, BOLD)
        cx, w = self.free_area()
        line = fitted_text(f"“The manager {part} for the client call.”", min(w - 1.4, SAFE_W - 1.8), LABEL, INK, NORMAL,
                           max_lines=2, t2c={part: GOOD if good else WORD})
        card = self.card(VGroup(head, line).arrange(DOWN, buff=0.2, aligned_edge=LEFT), width=min(w - 0.2, SAFE_W - 0.4))
        return card.move_to(RIGHT * cx + UP * (CARD_TOP - card.height / 2))

    def correction_example(self, sentence, bold, options, note):
        """Sentence with its bold part, a one-line diagnosis, and the options, beside the pinned tests."""
        texts, key, traps = judge(options)
        cx, w = self.free_area()
        sent = fitted_text(f"“{sentence}”", w - 0.8, BODY, INK, NORMAL, max_lines=2, t2c={bold: WORD})
        diag = VGroup(pill("diagnose", STEP_COLS["PREDICT"], size=SMALL), text(note, LABEL, INK)).arrange(RIGHT, buff=0.25)
        fit_width(diag, w - 0.8)
        q = OptionQuestion("?", texts, key, traps, word_size=LABEL)
        block = VGroup(sent, diag, q.rows).arrange(DOWN, buff=0.5, aligned_edge=LEFT)
        fit_height(block, SAFE_H - 1.6)
        block.to_edge(LEFT, buff=SAFE + 0.6).set_y(0.1)
        self.no_overlap(sent, diag, q.rows)
        self.no_overlap(block, self.pinned)
        self.validator.check_in_frame(block)
        return sent, diag, q

    # ========================================= 0. LESSON INTRO ==========
    # First video of a NEW LESSON: silent trail, a one-line recap of Lesson 9
    # (error spotting), one line that Lesson 10 starts, the title and objectives.

    def lesson_intro(self):
        self.scene_start("S00_intro", title="Lesson Introduction")

        crumb = self.breadcrumb("English · Module 2 Grammar", "Lesson 10 · Sentence Correction", "Video 1")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        last = VGroup(pill("Lesson 9: you FOUND the error", MUTED, size=LABEL),
                      pill("S-T-P-A-W scan", WORD, size=LABEL)).arrange(RIGHT, buff=0.4)
        now = pill("Lesson 10: you also CHOOSE THE FIX", GOOD, size=LABEL)
        roles = VGroup(text("the scan: what's broken", LABEL, WORD), text("·", LABEL, MUTED),
                       text("today's tests: which option repairs it properly", LABEL, GOOD)).arrange(RIGHT, buff=0.3)
        group = VGroup(last, now, roles).arrange(DOWN, buff=0.6)
        fit_width(group, SAFE_W).move_to(DOWN * 0.1)
        self.no_overlap(crumb, last, now, roles)
        self.validator.check_in_frame(VGroup(crumb, group))

        n = self.narrate(
            id="intro_01",
            text="In lesson nine, you found the error, with the S, T, P, A, W scan.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.at_word(n, "found")
        self.play(FadeIn(last[0], shift=UP * 0.1))
        self.at_word(n, "scan")
        self.play(FadeIn(last[1], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="intro_02",
            text="Now we start lesson ten, sentence correction. Here you also have to choose the fix. Your scan tells you "
                 "what's broken; today's tests tell you which option repairs it properly.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "lesson")
        self.play(Indicate(crumb[2], color="#F48FB1", scale_factor=1.1))
        self.at_word(n, "fix")
        self.play(FadeIn(now, shift=UP * 0.1))
        self.at_word(n, "scan")
        self.play(FadeIn(roles[0], shift=UP * 0.1))
        self.at_word(n, "tests")
        self.play(FadeIn(roles[1:], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        title = fitted_text("Introduction to Sentence Correction", SAFE_W, 64, INK, BOLD)
        underline = Line(LEFT, RIGHT, color=GOOD, stroke_width=5).set_width(title.width * 0.6)
        VGroup(title, underline).arrange(DOWN, buff=0.2).move_to(UP * 0.2)
        goals = [
            ("Explain how sentence correction differs from error spotting", WORD),
            ("Judge an option by three tests: fixes the error, adds no new error, keeps the meaning", GOOD),
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
            text="This is the introduction to sentence correction. By the end of this video, you'll be able to explain how "
                 "sentence correction differs from error spotting, and judge an option by three tests: it fixes the "
                 "error, adds no new error, and keeps the meaning.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(group, shift=UP * 0.3))
        self.at_word(n, "introduction")
        self.play(Write(title), run_time=1.1)
        self.play(GrowFromCenter(underline))
        self.at_word(n, "By")
        self.play(FadeOut(underline), ReplacementTransform(title, small_title), run_time=0.8)
        self.play(FadeIn(objectives[0]), FadeIn(heading))
        for row_, spoken in zip(rows, ["explain", "judge"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row_, shift=RIGHT * 0.2), run_time=0.5)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_intro")

    # ================================================= 1. HOOK ==========

    def hook(self):
        self.scene_start("S01_hook", title="Hook")

        texts, key, traps = HOOK_Q
        note = self.note_card()
        q = OptionQuestion("?", texts, key, traps)
        opts = q.rows.copy().arrange_in_grid(rows=2, cols=2, buff=(1.2, 0.4), cell_alignment=LEFT)
        fit_width(opts, SAFE_W)
        ask = pill("choose the best replacement for the highlighted part", FOCUS, size=LABEL)
        ask.next_to(note, DOWN, buff=0.5)
        opts.next_to(ask, DOWN, buff=0.6)
        self.no_overlap(note, ask, opts)
        self.validator.check_in_frame(VGroup(note, ask, opts))

        n = self.narrate(
            id="hook_01",
            text="You're writing up a feedback conversation: the manager asked me that why I was late for the client call. "
                 "Choose the best replacement for the highlighted part.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "feedback")
        self.play(FadeIn(note, shift=DOWN * 0.2))
        self.at_word(n, "Choose")
        self.play(FadeIn(ask, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_02",
            text="Asked me why I was late; asked me that why was I late; asked me why was I late; or no improvement?",
            voice="default",
            subtitle=True,
            pause_after=3.0,
        )
        for row, (spoken, occ) in zip(opts, [("Asked", 1), ("asked", 2), ("asked", 3), ("no", 1)]):
            self.at_word(n, spoken, occurrence=occ)
            self.play(FadeIn(row, shift=UP * 0.15), run_time=0.35)
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        self.clear_stage()
        self.scene_end("S01_hook")

    # ============================================== 2. CONCEPT ==========

    def concept(self):
        self.scene_start("S02_concept", title="The Concept")

        sample = text("“She has went home.”", BODY, INK, t2c={"has went": WORD})
        label = text("part of the sentence is bold or underlined", SMALL, WORD)
        choose = pill("choose the option that best REPLACES it", GOOD, size=LABEL)
        none = pill("…or “No improvement”", MUTED, size=LABEL)
        block = VGroup(VGroup(sample, label).arrange(DOWN, buff=0.2), choose, none).arrange(DOWN, buff=0.6)
        block.move_to(UP * 0.3)
        self.validator.check_in_frame(block)

        n = self.narrate(
            id="concept_01",
            text="In a sentence correction question, part of the sentence is bold or underlined. You choose the option "
                 "that best replaces it, or no improvement.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "bold")
        self.play(FadeIn(sample, shift=DOWN * 0.1), FadeIn(label))
        self.at_word(n, "replaces")
        self.play(FadeIn(choose, shift=UP * 0.1))
        self.at_word(n, "improvement")
        self.play(FadeIn(none, shift=UP * 0.1))
        self.wait_for_narration(n)

        several = pill("several options may FIX the original error", RATIO, size=LABEL)
        cleanly = pill("only ONE does it cleanly", GOOD, size=BODY)
        wrong = VGroup(text("wrong options usually:", LABEL, MUTED),
                       *[pill(t, BAD, size=LABEL) for t in ["fix one error, add a second", "change the meaning",
                                                           "add unnecessary words"]]).arrange(DOWN, buff=0.25)
        diff = VGroup(several, cleanly, wrong).arrange(DOWN, buff=0.5)
        fit_within(diff, SAFE_W, SAFE_H - 1.4)
        diff.move_to(UP * 0.3)
        self.validator.check_in_frame(diff)
        n = self.narrate(
            id="concept_02",
            text="The key difference from error spotting: several options may fix the original error, but only one does it "
                 "cleanly. Wrong options usually fix the first error and then introduce a second, or change the meaning, "
                 "or add unnecessary words.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(block))
        self.at_word(n, "several")
        self.play(FadeIn(several, shift=DOWN * 0.1))
        self.at_word(n, "cleanly")
        self.play(FadeIn(cleanly, scale=1.05))
        self.at_word(n, "Wrong")
        self.play(FadeIn(wrong[0]))
        for w_, spoken in zip(wrong[1:], ["second", "meaning", "unnecessary"]):
            self.at_word(n, spoken)
            self.play(FadeIn(w_, shift=UP * 0.1), run_time=0.4)
        self.wait_for_narration(n)

        head = pill("every option must pass THREE tests", FOCUS, size=LABEL)
        head.move_to(UP * (CARD_TOP - head.height / 2))
        tests = VGroup(*[VGroup(pill(name, c, size=BODY), text(q_ + "?", LABEL, INK)).arrange(RIGHT, buff=0.4)
                         for (name, _d, c), q_ in zip(TESTS, ["does it remove the original error",
                                                              "does it avoid any new error",
                                                              "does it keep the original meaning"])])
        tests.arrange(DOWN, buff=0.4, aligned_edge=LEFT)
        tie = pill("two options pass all three?  prefer the shorter, clearer one", RATIO, size=LABEL)
        body = VGroup(tests, tie).arrange(DOWN, buff=0.6)
        fit_width(body, SAFE_W)
        body.next_to(head, DOWN, buff=0.6)
        self.no_overlap(head, tests, tie)
        self.validator.check_in_frame(VGroup(head, body))
        n = self.narrate(
            id="concept_03",
            text="So every option must pass three tests. Fix: does it remove the original error? Clean: does it avoid any "
                 "new error? Faithful: does it keep the original meaning? If two options pass all three, prefer the "
                 "shorter, clearer one.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(diff))
        self.at_word(n, "three", occurrence=1)
        self.play(FadeIn(head, shift=DOWN * 0.2))
        for r, spoken in zip(tests, ["Fix", "Clean", "Faithful"]):
            self.at_word(n, spoken)
            self.play(FadeIn(r, shift=RIGHT * 0.2), run_time=0.45)
        self.at_word(n, "shorter")
        self.play(FadeIn(tie, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_concept")

    # ======================================== 3. WHY YOU NEED IT ==========

    def why_you_need_it(self):
        self.scene_start("S03_why", title="Why You Need It")

        exams = pill("sentence correction and improvement: regular in C-CAT and placement tests", BAD, size=LABEL)
        edit = pill("it's exactly what you do when you edit a report", WORD, size=LABEL)
        right = VGroup(text("not just “this is wrong”", LABEL, MUTED), text("→", LABEL, MUTED),
                       text("“this is the RIGHT version”", LABEL, GOOD)).arrange(RIGHT, buff=0.3)
        group = VGroup(exams, edit, right).arrange(DOWN, buff=0.7)
        fit_width(group, SAFE_W).move_to(UP * 0.3)
        self.no_overlap(exams, edit, right)
        self.validator.check_in_frame(group)

        n = self.narrate(
            id="why_01",
            text="Sentence correction and sentence improvement appear regularly in C-CAT and placement tests. It's also "
                 "exactly what you do when you edit a report: not just this is wrong, but this is the right version.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "regularly")
        self.play(FadeIn(exams, shift=DOWN * 0.1))
        self.at_word(n, "report")
        self.play(FadeIn(edit, shift=UP * 0.1))
        self.at_word(n, "wrong")
        self.play(FadeIn(right[0], shift=UP * 0.1))
        self.at_word(n, "right")
        self.play(FadeIn(right[1:], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_why")

    # ============================================== 4. ANALOGY ==========

    def analogy(self):
        self.scene_start("S04_analogy", title="The Analogy")

        # Keep the entire illustration comfortably inside the safe area.
        # The previous version made the pipe almost frame-width and then
        # attached the tap label to its right, pushing the combined VGroup
        # outside the validator's safe boundary.
        y = 1.75
        pipe = VGroup(
            Line(LEFT * 4.0 + UP * y, LEFT * 1.35 + UP * y, color=MUTED, stroke_width=10),
            Line(LEFT * 1.35 + UP * y, RIGHT * 1.35 + UP * y, color=GOOD, stroke_width=10),
            Line(RIGHT * 1.35 + UP * y, RIGHT * 4.0 + UP * y, color=MUTED, stroke_width=10),
        )
        joints = VGroup(
            Dot(LEFT * 1.35 + UP * y, radius=0.16, color=WORD),
            Dot(RIGHT * 1.35 + UP * y, radius=0.16, color=WORD),
        )

        # Position the tap label from the pipe end, then constrain it so the
        # complete drawing remains within the safe width.
        tap = text("→ the same tap", SMALL, SECOND)
        tap.next_to(pipe, RIGHT, buff=0.12)
        new = text("the replaced section", SMALL, GOOD)
        new.next_to(pipe[1], UP, buff=0.2)

        drawing = VGroup(pipe, joints, new, tap)
        fit_width(drawing, SAFE_W - 0.35)
        drawing.move_to(UP * y)

        rows = VGroup(*[
            VGroup(text(job, LABEL, INK), text("=", LABEL, MUTED), pill(name, c, size=LABEL))
            .arrange(RIGHT, buff=0.3)
            for job, (name, _d, c) in zip(
                [
                    "stop the leak",
                    "no new leak at the joints",
                    "the water still reaches the same tap",
                ],
                TESTS,
            )
        ]).arrange(DOWN, buff=0.35, aligned_edge=LEFT)

        # Fit the widest explanation row before placing it below the drawing.
        fit_width(rows, SAFE_W - 0.6)
        rows.next_to(drawing, DOWN, buff=0.65)
        rows.align_to(drawing, LEFT)

        # Final combined fit/centering guard before validation.
        block = VGroup(drawing, rows)
        fit_within(block, SAFE_W - 0.2, SAFE_H - 0.5)
        block.move_to(UP * 0.15)

        self.no_overlap(drawing, rows)
        self.validator.check_in_frame(block)

        n = self.narrate(
            id="analogy_01",
            text="A plumber replacing a leaking pipe has to stop the leak, and not create a new one at the joints, and keep "
                 "the water going to the same tap. That's fix, clean and faithful.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "plumber")
        self.play(Create(pipe), FadeIn(new))
        self.at_word(n, "stop")
        self.play(FadeIn(rows[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "joints")
        self.play(FadeIn(joints, scale=1.3), FadeIn(rows[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "tap")
        self.play(FadeIn(tap), FadeIn(rows[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "fix")
        self.play(LaggedStart(*[FadeIn(r[1:], shift=LEFT * 0.1) for r in rows], lag_ratio=0.35))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_analogy")

    # ======================================== 5-7. WORKED EXAMPLES ==========

    def example_know(self):
        self.scene_start("S05_ex_know", title="Worked Example 1")
        self.play(self.pin(self.tests_pin()))

        sent, diag, q = self.correction_example(
            "He do not know the answer.", "do not know",
            [("does not knows", "CLEAN", "breaks “knows”"), ("does not know", None, ""),
             ("not know", "FIX", "no helping verb")], "he → does")

        n = self.narrate(
            id="ex1_01",
            text="He do not know the answer. Does not knows, does not know, or not know? The subject is he, so do must "
                 "become does. Does not knows fixes do, but breaks knows: it fails clean. Not know drops the helping verb: "
                 "it fails fix. The right option is does not know.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "He", occurrence=1)
        self.play(FadeIn(sent, shift=DOWN * 0.1))
        self.at_word(n, "Does", occurrence=1)
        self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.2) for r in q.rows], lag_ratio=0.25))
        self.at_word(n, "subject")
        self.play(FadeIn(diag, shift=RIGHT * 0.2))
        self.at_word(n, "breaks")
        self.play(*q.strike("a")[1], self.light_test("CLEAN"))
        self.at_word(n, "drops")
        self.play(*q.strike("c")[1], self.light_test("FIX"))
        self.at_word(n, "right")
        self.play(*q.confirm()[1])
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_ex_know")

    def example_gone(self):
        self.scene_start("S06_ex_gone", title="Worked Example 2")

        sent, diag, q = self.correction_example(
            "She has went home.", "has went",
            [("has gone", None, ""), ("had went", "FIX", "keeps “went”"), ("went gone", "CLEAN", "not a verb form")],
            "has + third form:  gone")

        n = self.narrate(
            id="ex2_01",
            text="She has went home. Has gone, had went, or went gone? After has, we need the third form: gone. Had went "
                 "keeps the wrong form: it fails fix. Went gone is not a verb form at all. The right option is has gone.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "She")
        self.play(FadeIn(sent, shift=DOWN * 0.1))
        self.at_word(n, "Has", occurrence=2)
        self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.2) for r in q.rows], lag_ratio=0.25))
        self.at_word(n, "third")
        self.play(FadeIn(diag, shift=RIGHT * 0.2))
        self.at_word(n, "keeps")
        self.play(*q.strike("b")[1], self.light_test("FIX"))
        self.at_word(n, "all")
        self.play(*q.strike("c")[1], self.light_test("CLEAN"))
        self.at_word(n, "right")
        self.play(*q.confirm()[1])
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_ex_gone")

    def example_each(self):
        self.scene_start("S07_ex_each", title="Worked Example 3")

        sent, diag, q = self.correction_example(
            "Each of the reports were checked.", "were checked",
            [("was checked", None, ""), ("were being checked", "FIX", "still plural"),
             ("have been checked", "FIX", "still plural")], "“each” is singular  →  singular verb")

        n = self.narrate(
            id="ex3_01",
            text="Each of the reports were checked. Was checked, were being checked, or have been checked? Each is "
                 "singular, so the verb must be singular. Were being and have been are both plural: they fail fix. The "
                 "right option is was checked.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Each", occurrence=1)
        self.play(FadeIn(sent, shift=DOWN * 0.1))
        self.at_word(n, "Was", occurrence=1)
        self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.2) for r in q.rows], lag_ratio=0.25))
        self.at_word(n, "singular", occurrence=1)
        self.play(FadeIn(diag, shift=RIGHT * 0.2))
        self.at_word(n, "plural")
        self.play(*q.strike("b")[1], *q.strike("c")[1], self.light_test("FIX"))
        self.at_word(n, "right")
        self.play(*q.confirm()[1])
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S07_ex_each")

    # ================================================ 8. RULES ==========

    def rules(self):
        self.scene_start("S08_rules", title="Rules")
        self.play(self.unpin())

        rules = VGroup(*[VGroup(pill(str(i + 1), c, size=SMALL), fitted_text(s_, SAFE_W - 2.2, BODY, INK))
                         .arrange(RIGHT, buff=0.3) for i, (s_, c) in enumerate([
                             ("Diagnose the error in the bold part first (S-T-P-A-W)", WORD),
                             ("Test each option: fix, clean, faithful", GOOD),
                             ("If two pass, choose the more concise", RATIO),
                             ("“No improvement” only if the bold part passes the scan", MUTED)])])
        rules.arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        board = self.card(rules).move_to(UP * 0.3)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="rules_01",
            text="Four rules. First, diagnose the error in the bold part, with the S, T, P, A, W scan. Second, test each "
                 "option: fix, clean, faithful. Third, if two pass, choose the more concise. And fourth, choose no "
                 "improvement only if the bold part passes the scan.",
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

        strip = process_strip(BODY)
        fit_width(strip, SAFE_W)
        strip.move_to(UP * (CARD_TOP - strip.height / 2))
        details = VGroup(*[VGroup(pill(name, col, size=SMALL), fitted_text(s_, SAFE_W - 3.4, LABEL, INK))
                           .arrange(RIGHT, buff=0.3) for (name, col), s_ in zip(STEP_COLS.items(), [
                               "the whole sentence; diagnose the bold part",
                               "the correct version, before looking at the options",
                               "options that fail fix, clean or faithful",
                               "read the sentence with the chosen option"])])
        details.arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        board = self.card(details)
        board.next_to(strip, DOWN, buff=0.5)
        self.no_overlap(strip, board)
        self.validator.check_in_frame(VGroup(strip, board))

        n = self.narrate(
            id="process_01",
            text="The process. Read the whole sentence, and diagnose the bold part. Predict the correct version, before "
                 "looking at the options. Eliminate options that fail fix, clean or faithful. And confirm, by reading the "
                 "sentence with the chosen option.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(strip, shift=DOWN * 0.2), FadeIn(board[0]))
        for d, name, spoken in zip(details, STEP_COLS, ["Read", "Predict", "Eliminate", "confirm"]):
            self.at_word(n, spoken, occurrence=1)
            self.play(Indicate(step_chip(strip, name)), FadeIn(d, shift=RIGHT * 0.2), run_time=0.5)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S09_process")

    # ========================================== 10. HOOK, SOLVED ==========

    def hook_solved(self):
        self.scene_start("S10_hook_solved", title="Hook, Solved")
        self.play(self.pin(self.tests_pin()))

        texts, key, traps = HOOK_Q
        cx, w = self.free_area()
        note = self.note_card()
        notes = VGroup(pill("indirect question: no “that”, statement order", STEP_COLS["PREDICT"], size=SMALL),
                       pill("asked me why I was late", GOOD, size=SMALL)).arrange(RIGHT, buff=0.35)
        fit_width(notes, w - 0.6)
        notes.next_to(note, DOWN, buff=0.3).to_edge(LEFT, buff=SAFE + 0.6)
        q = OptionQuestion("?", texts, key, traps, word_size=LABEL)
        fit_height(q.rows, notes.get_bottom()[1] - 0.3 - (BOTTOM_Y + 0.6))
        q.rows.next_to(notes, DOWN, buff=0.35).to_edge(LEFT, buff=SAFE + 0.6)
        fixed = self.note_card(texts["abcd".index(key)], good=True)
        self.no_overlap(note, notes, q.rows)
        self.no_overlap(note, self.pinned)
        self.no_overlap(notes, self.pinned)
        self.validator.check_in_frame(VGroup(note, notes, q.rows))

        n = self.narrate(
            id="solved_01",
            text="Let's solve the hook. Read: asked me that why I was late. Predict: an indirect question takes no that, "
                 "and uses statement order: asked me why I was late.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(note), FadeIn(q.rows))
        self.at_word(n, "Read")
        self.play(Indicate(note[1][1], color=WORD, scale_factor=1.02))
        self.at_word(n, "Predict")
        self.play(FadeIn(notes[0], shift=UP * 0.1))
        self.at_word(n, "statement")
        self.play(FadeIn(notes[1], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_02",
            text="Eliminate. Option B keeps that, and uses question order. Option C removes that, but keeps question "
                 "order, was I: a new error. Option D keeps the original error.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Eliminate")
        self.play(Indicate(q.rows, color=BAD, scale_factor=1.02))
        self.at_word(n, "B")
        self.play(*q.strike("b")[1], self.light_test("FIX"))
        self.at_word(n, "C")
        self.play(*q.strike("c")[1], self.light_test("CLEAN"))
        self.at_word(n, "D")
        self.play(*q.strike("d")[1])
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_03",
            text="Confirm: the manager asked me why I was late for the client call. That's the answer.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Confirm")
        self.play(ReplacementTransform(note, fixed))
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
            ["Replace the bold part", "diagnose → predict → fix / clean / faithful"],
            ["“No improvement” option", "only if the scan finds nothing"],
            ["Two fixes pass", "choose the more concise"],
        ], [5.0, 6.8], size=LABEL)
        board = self.card(table, width=SAFE_W - 0.2).move_to(UP * 0.4)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="patterns_01",
            text="Three exam patterns. Replace the bold part: diagnose, predict, then fix, clean, faithful. The "
                 "no-improvement option: only if the scan finds nothing. And when two fixes pass: choose the more "
                 "concise.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(board[0]), FadeIn(table[0]))
        for row, spoken in zip(table[1:], ["Replace", "no-improvement", "two"]):
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
            (self.verdict_card(False, "Taking the first option that fixes the error", card_w),
             self.verdict_card(True, "Check it for NEW errors", card_w)),
            (self.verdict_card(False, "“No improvement” because it sounds fine", card_w),
             self.verdict_card(True, "Only after the scan finds nothing", card_w)),
            (self.verdict_card(False, "An option that changes the meaning", card_w),
             self.verdict_card(True, "Keep it faithful", card_w)),
        ]
        for (wrong, right), yy in zip(pairs, [1.6, 0.05, -1.5]):
            wrong.move_to(LEFT_ZONE + UP * yy)
            right.move_to(RIGHT_ZONE + UP * yy)
        header = pill("3 mistakes", BAD, size=LABEL).move_to(UP * (CARD_TOP - 0.3))
        self.validator.check_in_frame(VGroup(header, *[c for p in pairs for c in p]))

        n = self.narrate(
            id="mistakes_01",
            text="Three common mistakes. Number one is choosing the first option that fixes the error, without checking "
                 "for new errors. The second is choosing no improvement because it sounds fine. The third is picking an "
                 "option that changes the meaning.",
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
        ("She did not went to the party.", "did not went", ["not went", "did not go", "did not gone", "No improvement"],
         "b", "after “did”, use the first form (V1)"),
        ("He asked me where do I live.", "where do I live",
         ["where did I live", "that where I live", "where I live", "No improvement"], "c",
         "an indirect question: statement order"),
        ("The team has completed the project last month.", "has completed",
         ["completed", "had completed", "has been completing", "No improvement"], "a", "“last month”  →  simple past"),
    ]

    def practice(self):
        self.scene_start("S13_practice", title="Practice Questions")

        lines = VGroup(*[VGroup(VGroup(pill(str(i + 1), FOCUS, size=SMALL),
                                       text(f"“{sent}”", LABEL, INK, t2c={bold: WORD})).arrange(RIGHT, buff=0.35),
                                text("   ".join(f"({l}) {o}" for l, o in zip("abcd", opts)), LABEL, INK))
                         .arrange(DOWN, buff=0.2, aligned_edge=LEFT)
                         for i, (sent, bold, opts, *_r) in enumerate(self.PRACTICE)])
        lines.arrange(DOWN, buff=0.45, aligned_edge=LEFT)
        board = self.card(lines, color=FOCUS)
        fit_within(board, SAFE_W, SAFE_H - 1.2)
        board.move_to(UP * 0.4)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="practice_01",
            text="Your turn. One: she did not went to the party. Not went, did not go, did not gone, or no improvement? "
                 "Two: he asked me where do I live. Where did I live, that where I live, where I live, or no improvement? "
                 "Three: the team has completed the project last month. Completed, had completed, has been completing, or "
                 "no improvement?",
            voice="default",
            subtitle=True,
            pause_after=12.0,
        )
        self.play(FadeIn(board[0]))
        for ln, (spoken, first_option, occ) in zip(lines, [("party", "Not", 2), ("asked", "Where", 2),
                                                          ("team", "Completed", 2)]):
            self.at_word(n, spoken)
            self.play(FadeIn(ln[0], shift=UP * 0.15), run_time=0.4)
            self.at_word(n, first_option, occurrence=occ)
            self.play(FadeIn(ln[1], shift=LEFT * 0.15), run_time=0.4)
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        self.clear_stage()
        self.scene_end("S13_practice")

    # =============================================== 14. ANSWERS ==========

    def answers(self):
        self.scene_start("S14_answers", title="Answers")

        rows = VGroup(*[VGroup(VGroup(pill(str(i + 1), FOCUS, size=SMALL), text(bold, LABEL, BAD), text("→", LABEL, MUTED),
                                      pill(f"({key}) {opts['abcd'.index(key)]}", GOOD, size=LABEL))
                               .arrange(RIGHT, buff=0.3), text(why, SMALL, RATIO)).arrange(DOWN, buff=0.18, aligned_edge=LEFT)
                        for i, (_sent, bold, opts, key, why) in enumerate(self.PRACTICE)])
        rows.arrange(DOWN, buff=0.55, aligned_edge=LEFT)
        fit_within(rows, SAFE_W, SAFE_H - 1.2)
        rows.move_to(UP * 0.3)
        self.validator.check_in_frame(rows)

        n = self.narrate(
            id="answers_01",
            text="One: did not go. After did, use the first form of the verb. Two: where I live. An indirect question uses "
                 "statement order. Three: completed. Last month needs the simple past.",
            voice="default",
            subtitle=True,
        )
        for r, (spoken, why) in zip(rows, [("One", "After"), ("Two", "indirect"), ("Three", "Last")]):
            self.at_word(n, spoken)
            self.play(FadeIn(r[0], shift=RIGHT * 0.2), run_time=0.5)
            self.at_word(n, why)
            self.play(FadeIn(r[1], shift=LEFT * 0.1), run_time=0.4)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S14_answers")

    # ================================================ 15. RECAP ==========

    def recap(self):
        self.scene_start("S15_recap", title="Recap Card")

        card, table = self.recap_card("Recap Card: Video 1", [
            ["Three tests", "fix · clean (no new error) · faithful (same meaning)"],
            ["Tie-break", "the more concise option wins"],
            ["No improvement", "only after the scan finds nothing"],
        ])
        card.move_to(UP * 0.2)
        self.validator.check_in_frame(card)

        n = self.narrate(
            id="recap_01",
            text="To recap. Three tests: fix, clean, with no new error, and faithful, with the same meaning. The tie-break: "
                 "the more concise option wins. And no improvement: only after the scan finds nothing.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(card[0]), FadeIn(table[0]))
        for row, spoken in zip(table[1:], ["tests", "tie-break", "improvement"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.45)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S15_recap")

    # ================================================= 16. NEXT ==========

    def next_video(self):
        self.scene_start("S16_next", title="Next")

        types = pill("corrections, sorted into TYPES", RATIO, size=LABEL)
        predict = pill("predict the fix before reading the options", GOOD, size=LABEL)
        nxt = pill("Next:  Types of Corrections", FOCUS, size=LABEL)
        VGroup(types, predict, nxt).arrange(DOWN, buff=0.7).move_to(UP * 0.2)
        self.no_overlap(types, predict, nxt)
        self.validator.check_in_frame(VGroup(types, predict, nxt))

        n = self.narrate(
            id="next_01",
            text="Video two sorts corrections into types, so you can predict the fix before reading the options.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Video")
        self.play(FadeIn(nxt, scale=1.05))
        self.at_word(n, "types")
        self.play(FadeIn(types, shift=UP * 0.1))
        self.at_word(n, "predict")
        self.play(FadeIn(predict, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S16_next")
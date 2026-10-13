"""
animation.py for the LMS video generator.

Course : C-CAT - Section A - English
Module : Module 1 - Vocabulary
Lesson : Lesson 3 - Idioms & Phrases
Video  : 03 - Context-Based Idioms (Video 3 of 7)

Source script:
  C:\\Users\\User\\Downloads\\C-CAT_SectionA_Module1_English\\English\\Module 1 - Vocabulary\\
  Lesson 3 - Idioms & Phrases\\03 - Context-Based Idioms.pdf

Built on the golden-reference pattern:
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``;
  * layouts stacked with next_to and guarded with ``no_overlap``; nothing is
    ever animated onto or into another box.

Plain-word meanings of every idiom used live in MEANING; the worked examples, Hook Solved prediction and the answers are built from it.
The "ask the sentence" card (What's happening? What's the result? What's the tone? then predict) stays pinned top-right through the worked examples and Hook, Solved.
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

BLANK = "______"

# Plain-word meaning of every idiom this video uses.
MEANING = {
    "buried the hatchet": "made peace",
    "beating about the bush": "avoiding the point",
    "by leaps and bounds": "very quickly",
    "in the nick of time": "just in time, and it worked",
    "once in a blue moon": "rarely",
    "at sixes and sevens": "in confusion and disorder",
    "a dark horse": "someone whose abilities are unknown",
    "bit the bullet": "faced something unpleasant bravely",
}


def key_shape(label, color):
    """A simple key: bow, shaft, two teeth, with its idiom underneath."""
    bow = Circle(radius=0.28, color=color, stroke_width=5)
    shaft = Line(bow.get_bottom(), bow.get_bottom() + DOWN * 0.7, color=color, stroke_width=5)
    teeth = VGroup(Line(shaft.get_end(), shaft.get_end() + RIGHT * 0.2, color=color, stroke_width=5),
                   Line(shaft.get_end() + UP * 0.22, shaft.get_end() + UP * 0.22 + RIGHT * 0.14, color=color,
                        stroke_width=5))
    drawing = VGroup(bow, shaft, teeth)
    return VGroup(drawing, text(label, SMALL, color).next_to(drawing, DOWN, buff=0.15))


class ContextBasedIdiomsVideo(LMSScene):
    lesson_title = "Context-Based Idioms"

    def construct(self):
        self.camera.background_color = BG

        self.lesson_intro()
        self.hook()
        self.concept()
        self.why_you_need_it()
        self.analogy()
        self.example_hatchet()
        self.example_bush()
        self.example_leaps()
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

    def ask_pin(self):
        return self.steps_pin("ask the sentence", [("What's happening?", WORD), ("What's the result?", RATIO),
                                                   ("What's the tone?", SECOND),
                                                   ("predict, then pick the idiom", GOOD)])

    def log_card(self):
        head = text("DEPLOYMENT LOG", SMALL, RATIO, BOLD)
        row = VGroup(text("10:58  fix deployed", LABEL, INK), text("11:00  client demo", LABEL, INK),
                     text("demo passed ✓", LABEL, GOOD)).arrange(RIGHT, buff=0.6)
        cx, w = self.free_area()
        body = VGroup(head, row).arrange(DOWN, buff=0.2, aligned_edge=LEFT)
        fit_width(body, w - 1.4)
        card = self.card(body, width=min(w - 0.2, SAFE_W - 0.4))
        return card.move_to(RIGHT * cx + UP * (CARD_TOP - card.height / 2))

    def blank_example(self, sentence, clues, idiom):
        """Sentence with a blank, the answers to the pinned questions, the plain meaning, the idiom."""
        cx, w = self.free_area()
        sent = fitted_text(f"“{sentence}”", w - 0.8, BODY, INK, NORMAL, max_lines=2)
        chips = VGroup(*[VGroup(pill(k, c, size=SMALL), text(v, LABEL, INK)).arrange(RIGHT, buff=0.25)
                         for k, v, c in clues]).arrange(DOWN, buff=0.22, aligned_edge=LEFT)
        plain = pill("plain meaning:  " + MEANING[idiom], STEP_COLS["PREDICT"], size=LABEL)
        fit = pill(idiom, GOOD, size=BODY)
        block = VGroup(sent, chips, plain, fit).arrange(DOWN, buff=0.4, aligned_edge=LEFT)
        fit_height(block, SAFE_H - 1.6)
        self.place_free(block, y=0.1)
        self.no_overlap(sent, chips, plain, fit)
        self.validator.check_in_frame(block)
        return sent, chips, plain, fit

    # ========================================= 0. LESSON INTRO ==========

    def lesson_intro(self):
        self.scene_start("S00_intro", title="Lesson Introduction")

        crumb = self.breadcrumb("English · Module 1 Vocabulary", "Lesson 3 · Idioms & Phrases", "Video 3")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        before = VGroup(text("Video 2", SMALL, MUTED), pill("idiom", WORD, size=LABEL), text("→", LABEL, MUTED),
                        pill("meaning", GOOD, size=LABEL)).arrange(RIGHT, buff=0.3)
        today = VGroup(text("Today", SMALL, FOCUS), pill("situation", RATIO, size=LABEL), text("→", LABEL, MUTED),
                       pill("the idiom that fits", WORD, size=LABEL)).arrange(RIGHT, buff=0.3)
        VGroup(before, today).arrange(DOWN, buff=0.7, aligned_edge=LEFT).move_to(DOWN * 0.1)
        self.no_overlap(crumb, before, today)
        self.validator.check_in_frame(VGroup(crumb, before, today))

        n = self.narrate(
            id="intro_01",
            text="In video two, you learned idiom meanings by group. Today the direction reverses: you're given a "
                 "situation, and must pick the idiom that fits it.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.at_word(n, "meanings")
        self.play(FadeIn(before, shift=UP * 0.1))
        self.at_word(n, "reverses")
        self.play(FadeIn(today[:2], shift=UP * 0.1))
        self.at_word(n, "pick")
        self.play(FadeIn(today[2:], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        title = fitted_text("Context-Based Idioms", SAFE_W, 72, INK, BOLD)
        underline = Line(LEFT, RIGHT, color=SECOND, stroke_width=5).set_width(title.width * 0.6)
        VGroup(title, underline).arrange(DOWN, buff=0.2).move_to(UP * 0.2)
        goals = [("Choose the idiom that fits a sentence's situation and tone", GOOD),
                 ("Use the sentence clues to reject idioms that are real but wrong", BAD)]
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
            text="This video is context-based idioms. By the end, you'll choose the idiom that fits a sentence's situation "
                 "and tone, and use the sentence clues to reject idioms that are real but wrong.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(VGroup(before, today), shift=UP * 0.3))
        self.at_word(n, "context-based")
        self.play(Write(title), run_time=1.1)
        self.play(GrowFromCenter(underline))
        self.at_word(n, "By")
        self.play(FadeOut(underline), ReplacementTransform(title, small_title), run_time=0.8)
        self.play(FadeIn(objectives[0]), FadeIn(heading))
        for row_, spoken in zip(rows, ["choose", "reject"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row_, shift=RIGHT * 0.2), run_time=0.5)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_intro")

    # ================================================= 1. HOOK ==========

    HOOK = dict(word=f"deployed {BLANK}", options=["once in a blue moon", "by leaps and bounds", "at sixes and sevens",
                                                  "in the nick of time"], key="d",
                traps={"a": "= rarely", "b": "= growing rapidly", "c": "= in confusion"})

    def hook(self):
        self.scene_start("S01_hook", title="Hook")

        h = self.HOOK
        assert all(o in MEANING for o in h["options"])
        log = self.log_card()
        update = text(f"Your update:  “The patch was deployed {BLANK}.”", BODY, INK, t2c={BLANK: FOCUS})
        q = OptionQuestion(h["word"], h["options"], h["key"], h["traps"])
        opts = q.rows.copy().arrange_in_grid(rows=2, cols=2, buff=(1.2, 0.35), cell_alignment=LEFT)
        fit_width(opts, SAFE_W)
        update.next_to(log, DOWN, buff=0.6)
        opts.next_to(update, DOWN, buff=0.6)
        self.no_overlap(log, update, opts)
        self.validator.check_in_frame(VGroup(log, update, opts))

        n = self.narrate(
            id="hook_01",
            text="The deployment log says the fix went live at ten fifty-eight. The client demo started at eleven, and "
                 "passed. Your update to the team begins: the patch was deployed, blank.",
            voice="default",
            subtitle=True,
        )
        items = log[1][1]
        self.at_word(n, "log")
        self.play(FadeIn(log[0]), FadeIn(log[1][0]), FadeIn(items[0], shift=UP * 0.1))
        self.at_word(n, "demo")
        self.play(FadeIn(items[1], shift=UP * 0.1))
        self.at_word(n, "passed")
        self.play(FadeIn(items[2], shift=UP * 0.1))
        self.at_word(n, "update")
        self.play(FadeIn(update, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_02",
            text="Which idiom fits? Once in a blue moon, by leaps and bounds, at sixes and sevens, or in the nick of time?",
            voice="default",
            subtitle=True,
            pause_after=3.0,
        )
        self.at_word(n, "Which")
        self.play(Indicate(update, color=FOCUS, scale_factor=1.03))
        for row, spoken in zip(opts, ["Once", "leaps", "sixes", "nick"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=UP * 0.15), run_time=0.35)
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        self.clear_stage()
        self.scene_end("S01_hook")

    # ============================================== 2. CONCEPT ==========

    def concept(self):
        self.scene_start("S02_concept", title="The Concept")

        head = pill("fill in the idiom:  every option is usually a REAL idiom", SECOND, size=LABEL)
        fit_width(head, SAFE_W)
        head.move_to(UP * (CARD_TOP - head.height / 2))
        idioms = VGroup(*[VGroup(pill(i, WORD, size=LABEL), text("real idiom ✓", SMALL, MUTED)).arrange(DOWN, buff=0.12)
                          for i in self.HOOK["options"]]).arrange(RIGHT, buff=0.35)
        fit_width(idioms, SAFE_W)
        idioms.next_to(head, DOWN, buff=0.6)
        only = pill("only ONE matches the situation the sentence describes", GOOD, size=LABEL)
        only.next_to(idioms, DOWN, buff=0.5)
        start = pill("so start from the SENTENCE, not the idioms", FOCUS, size=BODY)
        start.next_to(only, DOWN, buff=0.5)
        self.no_overlap(head, idioms, only, start)
        self.validator.check_in_frame(VGroup(head, idioms, only, start))

        n = self.narrate(
            id="concept_01",
            text="In a fill-in-the-idiom question, every option is usually a real idiom. They're all correct English, but "
                 "only one matches the situation the sentence describes. So the sentence, not the idioms, is where you "
                 "start.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "real")
        self.play(FadeIn(head, shift=DOWN * 0.2), LaggedStart(*[FadeIn(i, shift=UP * 0.1) for i in idioms],
                                                              lag_ratio=0.15))
        self.at_word(n, "one")
        self.play(FadeIn(only, shift=UP * 0.1), Indicate(idioms[3][0], color=GOOD, scale_factor=1.08))
        self.at_word(n, "start")
        self.play(FadeIn(start, shift=UP * 0.1))
        self.wait_for_narration(n)

        # Three questions, then predict.
        ask_head = pill("read the sentence, ask three questions", FOCUS, size=LABEL)
        ask_head.move_to(UP * (CARD_TOP - ask_head.height / 2))
        qs = VGroup(*[VGroup(pill(q_, c, size=LABEL), text(ex, LABEL, INK)).arrange(RIGHT, buff=0.35)
                      for q_, ex, c in [("What's happening?", "timing?  conflict?  effort?", WORD),
                                        ("What's the result?", "success?  failure?  trouble?", RATIO),
                                        ("What's the tone?", "praise?  criticism?  neutral?", SECOND)]])
        qs.arrange(DOWN, buff=0.35, aligned_edge=LEFT)
        then = pill("then PREDICT the meaning in plain words  →  find the idiom that carries it", GOOD, size=SMALL)
        body = VGroup(qs, then).arrange(DOWN, buff=0.55)
        fit_width(body, SAFE_W)
        body.next_to(ask_head, DOWN, buff=0.55)
        self.no_overlap(ask_head, qs, then)
        self.validator.check_in_frame(VGroup(ask_head, body))
        n = self.narrate(
            id="concept_02",
            text="Read the sentence and ask three questions. What's happening: timing, conflict, effort? What's the "
                 "result: success, failure, trouble? What's the tone: praise, criticism, neutral? Then predict the "
                 "meaning in plain words, and find the idiom that carries it.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(VGroup(head, idioms, only, start)))
        self.at_word(n, "three")
        self.play(FadeIn(ask_head, shift=DOWN * 0.2))
        for row, spoken in zip(qs, ["happening", "result", "tone"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.45)
        self.at_word(n, "predict")
        self.play(FadeIn(then, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_concept")

    # ======================================== 3. WHY YOU NEED IT ==========

    def why_you_need_it(self):
        self.scene_start("S03_why", title="Why You Need It")

        tests = pill("common in placement tests:  fill-in idioms, sentence completion", BAD, size=LABEL)
        work = pill("at work: an idiom that doesn't fit sounds careless", RATIO, size=LABEL)
        bad = VGroup(text("“We grew by leaps and bounds.”", LABEL, INK, t2c={"by leaps and bounds": BAD}),
                     text("✗  about a one-day fix", SMALL, BAD)).arrange(RIGHT, buff=0.4)
        group = VGroup(tests, work, bad).arrange(DOWN, buff=0.7)
        fit_width(group, SAFE_W).move_to(UP * 0.3)
        self.no_overlap(tests, work, bad)
        self.validator.check_in_frame(group)

        n = self.narrate(
            id="why_01",
            text="Fill-in idiom questions, and sentence-completion questions with idioms, are common in placement tests. "
                 "And at work, an idiom that doesn't fit sounds careless: like we grew by leaps and bounds, about a "
                 "one-day fix.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "common")
        self.play(FadeIn(tests, shift=DOWN * 0.1))
        self.at_word(n, "work")
        self.play(FadeIn(work, shift=UP * 0.1))
        self.at_word(n, "leaps")
        self.play(FadeIn(bad, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_why")

    # ============================================== 4. ANALOGY ==========

    def analogy(self):
        self.scene_start("S04_analogy", title="The Analogy")

        keys = VGroup(*[key_shape(i, WORD) for i in self.HOOK["options"]]).arrange(RIGHT, buff=0.7, aligned_edge=UP)
        fit_width(keys, SAFE_W - 1.0)
        keys.move_to(UP * 1.9)
        lock = self.card(VGroup(text("the lock = the sentence", SMALL, RATIO, BOLD),
                                text(f"“The patch was deployed {BLANK}.”", LABEL, INK, t2c={BLANK: FOCUS}))
                         .arrange(DOWN, buff=0.18, aligned_edge=LEFT))
        lock.move_to(DOWN * 1.0)
        fits = Arrow(keys[3].get_bottom() + DOWN * 0.1, lock.get_corner(UR) + UP * 0.1 + LEFT * 0.6, buff=0, color=GOOD,
                     stroke_width=5)
        shape = pill("check the lock's shape BEFORE trying keys", FOCUS, size=LABEL)
        shape.next_to(lock, DOWN, buff=0.4)
        self.no_overlap(keys, lock, shape)
        self.validator.check_in_frame(VGroup(keys, lock, shape))

        n = self.narrate(
            id="analogy_01",
            text="Every key on the ring is a real key. Only one fits this lock. The sentence is the lock; check its shape "
                 "before trying keys.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "key", occurrence=1)
        self.play(LaggedStart(*[FadeIn(k, shift=DOWN * 0.2) for k in keys], lag_ratio=0.2))
        self.at_word(n, "fits")
        self.play(FadeIn(lock[0]), GrowArrow(fits), keys[3].animate.set_color(GOOD))
        self.at_word(n, "sentence")
        self.play(FadeIn(lock[1], shift=UP * 0.1))
        self.at_word(n, "shape")
        self.play(FadeIn(shape, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_analogy")

    # ======================================== 5-7. WORKED EXAMPLES ==========

    def example_hatchet(self):
        self.scene_start("S05_ex_hatchet", title="Worked Example 1")
        self.play(self.pin(self.ask_pin()))

        sent, chips, plain, fit = self.blank_example(
            f"After years of rivalry, the two founders finally {BLANK} and merged their companies.",
            [("happening", "a conflict is ending", WORD), ("result", "a merger: a good outcome", RATIO)],
            "buried the hatchet")

        n = self.narrate(
            id="ex1_01",
            text="After years of rivalry, the two founders finally, blank, and merged their companies. What's happening? A "
                 "conflict is ending. The result: a merger, a good outcome. So the plain meaning is: made peace. The "
                 "idiom: buried the hatchet.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "After")
        self.play(FadeIn(sent, shift=DOWN * 0.1))
        self.at_word(n, "happening")
        self.play(FadeIn(chips[0][0], shift=RIGHT * 0.1), self.pin_step(0, color=WORD))
        self.at_word(n, "conflict")
        self.play(FadeIn(chips[0][1], shift=LEFT * 0.1))
        self.at_word(n, "result")
        self.play(FadeIn(chips[1], shift=RIGHT * 0.1), self.pin_step(1, color=RATIO))
        self.at_word(n, "plain")
        self.play(FadeIn(plain, shift=UP * 0.1), self.pin_step(3, color=GOOD))
        self.at_word(n, "idiom")
        self.play(FadeIn(fit, scale=1.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_ex_hatchet")

    def example_bush(self):
        self.scene_start("S06_ex_bush", title="Worked Example 2")

        sent, chips, plain, fit = self.blank_example(
            f"Stop {BLANK}; tell me whether the project is delayed.",
            [("happening", "someone is avoiding the answer", WORD), ("tone", "impatient: a complaint", SECOND)],
            "beating about the bush")

        n = self.narrate(
            id="ex2_01",
            text="Stop, blank; tell me whether the project is delayed. What's happening? Someone is avoiding the answer. "
                 "The tone: impatient, a complaint. So the plain meaning is: avoiding the point. The idiom: beating about "
                 "the bush.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Stop")
        self.play(FadeIn(sent, shift=DOWN * 0.1))
        self.at_word(n, "happening")
        self.play(FadeIn(chips[0][0], shift=RIGHT * 0.1), self.pin_step(0, color=WORD))
        self.at_word(n, "Someone")
        self.play(FadeIn(chips[0][1], shift=LEFT * 0.1))
        self.at_word(n, "tone")
        self.play(FadeIn(chips[1], shift=RIGHT * 0.1), self.pin_step(2, color=SECOND))
        self.at_word(n, "plain")
        self.play(FadeIn(plain, shift=UP * 0.1), self.pin_step(3, color=GOOD))
        self.at_word(n, "idiom")
        self.play(FadeIn(fit, scale=1.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_ex_bush")

    def example_leaps(self):
        self.scene_start("S07_ex_leaps", title="Worked Example 3")

        sent, chips, plain, fit = self.blank_example(
            f"The startup's revenue grew {BLANK} after the launch.",
            [("happening", "growth", WORD), ("result", "success, and fast", RATIO)],
            "by leaps and bounds")

        n = self.narrate(
            id="ex3_01",
            text="The startup's revenue grew, blank, after the launch. What's happening? Growth. The result: success, and "
                 "fast. So the plain meaning is: very quickly. The idiom: by leaps and bounds.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "revenue")
        self.play(FadeIn(sent, shift=DOWN * 0.1))
        self.at_word(n, "happening")
        self.play(FadeIn(chips[0][0], shift=RIGHT * 0.1), self.pin_step(0, color=WORD))
        self.at_word(n, "Growth")
        self.play(FadeIn(chips[0][1], shift=LEFT * 0.1))
        self.at_word(n, "result")
        self.play(FadeIn(chips[1], shift=RIGHT * 0.1), self.pin_step(1, color=RATIO))
        self.at_word(n, "plain")
        self.play(FadeIn(plain, shift=UP * 0.1), self.pin_step(3, color=GOOD))
        self.at_word(n, "idiom")
        self.play(FadeIn(fit, scale=1.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S07_ex_leaps")

    # ================================================ 8. RULES ==========

    def rules(self):
        self.scene_start("S08_rules", title="Rules")
        self.play(self.unpin())

        rules = VGroup(*[VGroup(pill(str(i + 1), c, size=SMALL), fitted_text(s_, SAFE_W - 2.2, BODY, INK))
                         .arrange(RIGHT, buff=0.3) for i, (s_, c) in enumerate([
                             ("Start from the sentence: situation, result, tone", WORD),
                             ("Predict the meaning in plain words before looking at the idioms", STEP_COLS["PREDICT"]),
                             ("Every option may be a real idiom: judge FIT, not familiarity", BAD),
                             ("Check grammar too: the idiom must fit the sentence structure", GOOD)])])
        rules.arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        board = self.card(rules).move_to(UP * 0.3)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="rules_01",
            text="Four rules. First, start from the sentence: situation, result, tone. Second, predict the meaning in "
                 "plain words before looking at the idioms. Third, every option may be a real idiom, so judge fit, not "
                 "familiarity. And fourth, check grammar too: the idiom must fit the sentence structure.",
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
                               "the sentence: time words, result words, tone",
                               "the meaning needed",
                               "idioms with the wrong meaning, wrong tone or wrong grammar",
                               "read the full sentence"])])
        details.arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        board = self.card(details)
        board.next_to(strip, DOWN, buff=0.5)
        self.no_overlap(strip, board)
        self.validator.check_in_frame(VGroup(strip, board))

        n = self.narrate(
            id="process_01",
            text="The process. Read the sentence: note the time words, result words and tone. Predict the meaning needed. "
                 "Eliminate idioms with the wrong meaning, wrong tone, or wrong grammar. And confirm by reading the full "
                 "sentence.",
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
        self.play(self.pin(self.ask_pin()))

        h = self.HOOK
        answer = h["options"]["abcd".index(h["key"])]
        log = self.log_card()
        items = log[1][1]
        q = OptionQuestion(h["word"], h["options"], h["key"], h["traps"], word_size=LABEL)
        fit_height(q.group, log.get_bottom()[1] - 0.4 - (BOTTOM_Y + 0.6))
        q.group.next_to(log, DOWN, buff=0.4).to_edge(LEFT, buff=SAFE + 0.6)
        pin_left = self.pinned.get_left()[0]
        predict = pill("predict:  " + MEANING[answer], STEP_COLS["PREDICT"], size=SMALL)
        fit_width(predict, pin_left - 0.3 - (q.word.get_right()[0] + 0.3))
        predict.next_to(q.word, RIGHT, buff=0.3)
        answer_row = q.row(h["key"])
        conf = text(f"“The patch was deployed {answer}.”", SMALL, INK, t2c={answer: GOOD})
        fit_width(conf, pin_left - 0.3 - answer_row.get_right()[0] - 0.5)
        conf.next_to(answer_row, RIGHT, buff=0.4)
        self.no_overlap(log, q.group)
        self.no_overlap(log, self.pinned)
        self.no_overlap(q.rows, predict)
        self.no_overlap(predict, self.pinned)
        self.validator.check_in_frame(VGroup(log, q.group, predict, conf))

        n = self.narrate(
            id="solved_01",
            text="Let's solve the hook. Read: the fix was deployed two minutes before the demo, and the demo passed. "
                 "Predict: just in time, and it worked.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(log), FadeIn(q.word), FadeIn(q.rows))
        self.at_word(n, "Read")
        self.play(Indicate(items[:2], color=WORD, scale_factor=1.03), self.pin_step(0, color=WORD))
        self.at_word(n, "passed")
        self.play(Indicate(items[2], color=GOOD, scale_factor=1.08), self.pin_step(1, color=RATIO))
        self.at_word(n, "Predict")
        self.play(FadeIn(predict, shift=LEFT * 0.1), self.pin_step(3, color=GOOD))
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_02",
            text="Eliminate. Once in a blue moon means rarely. By leaps and bounds means growing rapidly. At sixes and "
                 "sevens means in confusion.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Eliminate")
        self.play(Indicate(q.rows, color=BAD, scale_factor=1.02))
        for letter, spoken in [("a", "Once"), ("b", "leaps"), ("c", "sixes")]:
            self.at_word(n, spoken)
            self.play(*q.strike(letter)[1])
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_03",
            text="Confirm: the patch was deployed in the nick of time. That's the answer.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Confirm")
        self.play(FadeIn(conf, shift=LEFT * 0.1))
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
            ["Fill in the idiom", "situation → plain meaning → matching idiom"],
            ["Which idiom is used correctly?", "test each sentence: does the situation match the idiom's meaning?"],
            ["Replace the underlined phrase", "find the idiom with the same meaning and tone"],
        ], [4.8, 7.0], size=LABEL)
        board = self.card(table, width=SAFE_W - 0.2).move_to(UP * 0.4)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="patterns_01",
            text="Three exam patterns. Fill in the idiom: situation, then plain meaning, then the matching idiom. Which "
                 "idiom is used correctly: test each sentence, and ask whether the situation matches the idiom's meaning. "
                 "And replace the underlined phrase: find the idiom with the same meaning and tone.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(board[0]), FadeIn(table[0]))
        for row, spoken in zip(table[1:], ["Fill", "correctly", "replace"]):
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
            (self.verdict_card(False, "Picking the most familiar idiom", card_w),
             self.verdict_card(True, "Pick the one that FITS", card_w)),
            (self.verdict_card(False, "Ignoring the result", card_w),
             self.verdict_card(True, "eleventh hour: late.  nick of time: late, and it worked", card_w)),
            (self.verdict_card(False, "Ignoring grammar", card_w),
             self.verdict_card(True, "“buried the hatchet” needs a subject that can make peace", card_w)),
        ]
        for (wrong, right), yy in zip(pairs, [1.6, 0.05, -1.5]):
            wrong.move_to(LEFT_ZONE + UP * yy)
            right.move_to(RIGHT_ZONE + UP * yy)
        header = pill("3 mistakes", BAD, size=LABEL).move_to(UP * (CARD_TOP - 0.3))
        self.validator.check_in_frame(VGroup(header, *[c for p in pairs for c in p]))

        n = self.narrate(
            id="mistakes_01",
            text="Three common mistakes. The first is picking the most familiar idiom, not the one that fits. The second "
                 "is ignoring the result: at the eleventh hour doesn't say it succeeded; in the nick of time does. The "
                 "third is ignoring grammar: buried the hatchet needs a subject that can make peace.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(header))
        for pr, (spoken, detail) in zip(pairs, [("first", "fits"), ("second", "eleventh"), ("third", "buried")]):
            self.at_word(n, spoken)
            self.play(FadeIn(pr[0], shift=RIGHT * 0.3))
            self.at_word(n, detail)
            self.play(FadeIn(pr[1], shift=LEFT * 0.3))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S12_mistakes")

    # ============================================== 13. PRACTICE ==========

    PRACTICE = [
        (f"The new manager is {BLANK}; nobody knows what she's capable of yet.",
         ["a white elephant", "a piece of cake", "a dark horse", "in hot water"], "c"),
        (f"The team was {BLANK} after the sudden resignation; nobody knew who was in charge.",
         ["at sixes and sevens", "on cloud nine", "in the nick of time", "at the eleventh hour"], "a"),
        (f"He finally {BLANK} and told the board the truth about the losses.",
         ["sat on the fence", "bit the bullet", "beat about the bush", "cut corners"], "b"),
    ]

    def practice(self):
        self.scene_start("S13_practice", title="Practice Questions")

        head = pill("Which idiom FITS?", SECOND, size=LABEL)
        lines = VGroup(*[VGroup(VGroup(pill(str(i + 1), FOCUS, size=SMALL),
                                       text(f"“{sent}”", LABEL, INK, t2c={BLANK: FOCUS})).arrange(RIGHT, buff=0.35),
                                text("   ".join(f"({l}) {o}" for l, o in zip("abcd", opts)), LABEL, WORD))
                         .arrange(DOWN, buff=0.2, aligned_edge=LEFT)
                         for i, (sent, opts, _k) in enumerate(self.PRACTICE)])
        lines.arrange(DOWN, buff=0.4, aligned_edge=LEFT)
        board = self.card(VGroup(head, lines).arrange(DOWN, buff=0.4, aligned_edge=LEFT), color=FOCUS)
        fit_within(board, SAFE_W, SAFE_H - 1.2)
        board.move_to(UP * 0.4)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="practice_01",
            text="Your turn: which idiom fits? One: the new manager is, blank; nobody knows what she's capable of yet. A "
                 "white elephant, a piece of cake, a dark horse, or in hot water? Two: the team was, blank, after the "
                 "sudden resignation; nobody knew who was in charge. At sixes and sevens, on cloud nine, in the nick of "
                 "time, or at the eleventh hour? Three: he finally, blank, and told the board the truth about the losses. "
                 "Sat on the fence, bit the bullet, beat about the bush, or cut corners?",
            voice="default",
            subtitle=True,
            pause_after=12.0,
        )
        self.play(FadeIn(board[0]), FadeIn(head))
        for ln, (spoken, first_option) in zip(lines, [("manager", "white"), ("team", "sixes"), ("finally", "Sat")]):
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
        for i, (sent, opts, key) in enumerate(self.PRACTICE):
            idiom = opts["abcd".index(key)]
            rows.add(VGroup(pill(str(i + 1), FOCUS, size=SMALL), pill(f"({key}) {idiom}", GOOD, size=LABEL),
                            text("=  " + MEANING[idiom], LABEL, INK)).arrange(RIGHT, buff=0.3))
        opposite = text("(a) sat on the fence, (c) beat about the bush: the opposite", SMALL, BAD)
        rows.arrange(DOWN, buff=0.6, aligned_edge=LEFT)
        block = VGroup(rows, opposite).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        fit_within(block, SAFE_W, SAFE_H - 1.2)
        block.move_to(UP * 0.3)
        self.validator.check_in_frame(block)

        n = self.narrate(
            id="answers_01",
            text="One: a dark horse: someone whose abilities are unknown. Two: at sixes and sevens: in confusion and "
                 "disorder. Three: bit the bullet. He faced something unpleasant bravely. Sat on the fence and beat about "
                 "the bush are the opposite.",
            voice="default",
            subtitle=True,
        )
        for r, (spoken, meaning) in zip(rows, [("dark", "abilities"), ("sixes", "confusion"), ("bullet", "faced")]):
            self.at_word(n, spoken)
            self.play(FadeIn(r[:2], shift=RIGHT * 0.2), run_time=0.5)
            self.at_word(n, meaning)
            self.play(FadeIn(r[2], shift=LEFT * 0.1), run_time=0.4)
        self.at_word(n, "opposite")
        self.play(FadeIn(opposite, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S14_answers")

    # ================================================ 15. RECAP ==========

    def recap(self):
        self.scene_start("S15_recap", title="Recap Card")

        card, table = self.recap_card("Recap Card: Video 3", [
            ["Start from", "the sentence: situation, result, tone"],
            ["Predict", "the plain-word meaning first"],
            ["All options real", "judge fit, not familiarity"],
        ])
        card.move_to(UP * 0.2)
        self.validator.check_in_frame(card)

        n = self.narrate(
            id="recap_01",
            text="To recap. Start from the sentence: situation, result, tone. Predict the plain-word meaning first. And "
                 "remember that all the options are real idioms, so judge fit, not familiarity.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(card[0]), FadeIn(table[0]))
        for row, spoken in zip(table[1:], ["Start", "Predict", "real"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.45)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S15_recap")

    # ================================================= 16. NEXT ==========

    def next_video(self):
        self.scene_start("S16_next", title="Next")

        cousins = VGroup(pill("phrasal verbs", WORD, size=BODY), pill("fixed phrases", SECOND, size=BODY))\
            .arrange(RIGHT, buff=0.6)
        often = pill("close cousins of idioms: tested just as often", BAD, size=LABEL)
        nxt = pill("Next:  Phrases and Their Meanings", FOCUS, size=LABEL)
        VGroup(cousins, often, nxt).arrange(DOWN, buff=0.7).move_to(UP * 0.2)
        self.no_overlap(cousins, often, nxt)
        self.validator.check_in_frame(VGroup(cousins, often, nxt))

        n = self.narrate(
            id="next_01",
            text="Phrasal verbs and fixed phrases are close cousins of idioms, and they're tested just as often. Video four "
                 "covers them.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Phrasal")
        self.play(FadeIn(cousins[0], shift=UP * 0.1))
        self.at_word(n, "fixed")
        self.play(FadeIn(cousins[1], shift=UP * 0.1))
        self.at_word(n, "tested")
        self.play(FadeIn(often, shift=UP * 0.1))
        self.at_word(n, "Video")
        self.play(FadeIn(nxt, scale=1.05))
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S16_next")

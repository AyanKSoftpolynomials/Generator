"""
animation.py for the LMS video generator.

Course : C-CAT - Section A - English
Module : Module 2 - Grammar
Lesson : Lesson 10 - Sentence Correction
Video  : 02 - Types of Corrections (Video 2 of 6)

Source script:
  C:\\Scripts\\02 - Types of Corrections.pdf

Built on the golden-reference pattern:
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``;
  * layouts stacked with next_to and guarded with ``no_overlap``; nothing is
    ever animated onto or into another box.

The four correction types live in TYPES and the five-row Rules table (type, signal, fix, family) in RULES; the rules table is built from it.
The "name the type" card (grammar, structure, word choice, redundancy) stays pinned top-right through the worked examples and Hook, Solved; the type in use lights up.
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

TYPES = ["GRAMMAR", "STRUCTURE", "WORD CHOICE", "REDUNDANCY"]
TYPE_COL = dict(zip(TYPES, [WORD, RATIO, SECOND, BAD]))

# The script's Rules table: (type, signal, fix, family it belongs to).
RULES = [
    ("Grammar", "S-T-P-A-W error", "standard rule", "GRAMMAR"),
    ("Dangling modifier", "opening -ing or -ed phrase; wrong subject after the comma",
     "add the right subject, or rewrite as a clause", "STRUCTURE"),
    ("Parallelism", "list or paired conjunction with mixed forms", "make all items the same form", "STRUCTURE"),
    ("Word choice", "confusable pair or broken idiom", "correct word or fixed form", "WORD CHOICE"),
    ("Redundancy", "two words with the same meaning", "remove one", "REDUNDANCY"),
]
assert all(fam in TYPES for *_x, fam in RULES)


class TypesOfCorrectionsVideo(LMSScene):
    lesson_title = "Types of Corrections"

    def construct(self):
        self.camera.background_color = BG

        self.lesson_intro()
        self.hook()
        self.concept()
        self.why_you_need_it()
        self.analogy()
        self.example_dangling()
        self.example_parallel()
        self.example_redundant()
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

    def type_pin(self):
        return self.steps_pin("name the type", [("GRAMMAR: S-T-P-A-W", WORD), ("STRUCTURE: dangling, parallel", RATIO),
                                                ("WORD CHOICE: wrong word", SECOND), ("REDUNDANCY: repeats", BAD)])

    def light_type(self, name):
        return self.pin_step(TYPES.index(name), color=TYPE_COL[name])

    def club_card(self, part="Being a rainy day", good=False):
        head = text("SPORTS CLUB  ·  announcement", SMALL, RATIO, BOLD)
        cx, w = self.free_area()
        line = fitted_text(f"“{part}, the inter-college match was cancelled.”", min(w - 1.4, SAFE_W - 1.8), LABEL, INK,
                           NORMAL, max_lines=2, t2c={part: GOOD if good else WORD})
        card = self.card(VGroup(head, line).arrange(DOWN, buff=0.2, aligned_edge=LEFT), width=min(w - 0.2, SAFE_W - 0.4))
        return card.move_to(RIGHT * cx + UP * (CARD_TOP - card.height / 2))

    def type_example(self, before, bold, why, kind, family, after, good):
        """Sentence with its bold part, why it's wrong, the correction type (lit on the pin), the fix."""
        cx, w = self.free_area()
        first = fitted_text(f"“{before}”", w - 0.8, BODY, INK, NORMAL, max_lines=2, t2c={bold: WORD})
        note = text(why, LABEL, MUTED)
        tag = VGroup(pill("type", TYPE_COL[family], size=SMALL), text(kind, LABEL, TYPE_COL[family], BOLD))\
            .arrange(RIGHT, buff=0.25)
        fixed = fitted_text(f"“{after}”", w - 0.8, BODY, INK, NORMAL, max_lines=2, t2c={good: GOOD})
        block = VGroup(first, note, tag, fixed).arrange(DOWN, buff=0.5, aligned_edge=LEFT)
        fit_within(block, w - 0.6, SAFE_H - 1.6)
        self.place_free(block, y=0.1)
        self.no_overlap(first, note, tag, fixed)
        self.validator.check_in_frame(block)
        return first, note, tag, fixed

    # ========================================= 0. LESSON INTRO ==========

    def lesson_intro(self):
        self.scene_start("S00_intro", title="Lesson Introduction")

        crumb = self.breadcrumb("English · Module 2 Grammar", "Lesson 10 · Sentence Correction", "Video 2")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        tests = VGroup(text("Video 1", SMALL, MUTED), *[pill(t, c, size=LABEL) for t, c in [("FIX", GOOD), ("CLEAN", WORD),
                                                                                           ("FAITHFUL", SECOND)]])\
            .arrange(RIGHT, buff=0.3)
        what = pill("today: WHAT is typically being fixed", RATIO, size=LABEL)
        faster = pill("so you can predict the correct version faster", GOOD, size=LABEL)
        VGroup(tests, what, faster).arrange(DOWN, buff=0.6).move_to(DOWN * 0.1)
        self.no_overlap(crumb, tests, what, faster)
        self.validator.check_in_frame(VGroup(crumb, tests, what, faster))

        n = self.narrate(
            id="intro_01",
            text="Video one gave you fix, clean and faithful. Today we look at what is typically being fixed, so you can "
                 "predict the correct version faster.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.at_word(n, "fix")
        self.play(LaggedStart(*[FadeIn(t, shift=UP * 0.1) for t in tests], lag_ratio=0.25))
        self.at_word(n, "what")
        self.play(FadeIn(what, shift=UP * 0.1))
        self.at_word(n, "faster")
        self.play(FadeIn(faster, shift=UP * 0.1))
        self.wait_for_narration(n)

        title = fitted_text("Types of Corrections", SAFE_W, 72, INK, BOLD)
        underline = Line(LEFT, RIGHT, color=RATIO, stroke_width=5).set_width(title.width * 0.6)
        VGroup(title, underline).arrange(DOWN, buff=0.2).move_to(UP * 0.2)
        goals = [("Recognise the main types: grammar, structure, word choice, redundancy", RATIO),
                 ("Fix dangling modifiers and faulty parallelism", GOOD)]
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
            text="This video is types of corrections. By the end, you'll recognise the main types of correction: grammar, "
                 "structure, word choice and redundancy; and fix dangling modifiers and faulty parallelism.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(VGroup(tests, what, faster), shift=UP * 0.3))
        self.at_word(n, "types", occurrence=1)
        self.play(Write(title), run_time=1.1)
        self.play(GrowFromCenter(underline))
        self.at_word(n, "By")
        self.play(FadeOut(underline), ReplacementTransform(title, small_title), run_time=0.8)
        self.play(FadeIn(objectives[0]), FadeIn(heading))
        for row_, spoken in zip(rows, ["recognise", "dangling"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row_, shift=RIGHT * 0.2), run_time=0.5)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_intro")

    # ================================================= 1. HOOK ==========

    HOOK = dict(word="?", options=["Being rainy day", "Having been a rainy day", "It being a rainy day",
                                   "No improvement"], key="c",
                traps={"a": "drops the article; still dangling", "b": "still has no subject", "d": "keeps the error"})

    def hook(self):
        self.scene_start("S01_hook", title="Hook")

        h = self.HOOK
        club = self.club_card()
        q = OptionQuestion(h["word"], h["options"], h["key"], h["traps"])
        opts = q.rows.copy().arrange_in_grid(rows=2, cols=2, buff=(1.2, 0.4), cell_alignment=LEFT)
        fit_width(opts, SAFE_W)
        ask = pill("choose the best replacement", FOCUS, size=LABEL)
        ask.next_to(club, DOWN, buff=0.5)
        opts.next_to(ask, DOWN, buff=0.6)
        self.no_overlap(club, ask, opts)
        self.validator.check_in_frame(VGroup(club, ask, opts))

        n = self.narrate(
            id="hook_01",
            text="The club secretary's announcement says: being a rainy day, the inter-college match was cancelled. Choose "
                 "the best replacement.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "announcement")
        self.play(FadeIn(club, shift=DOWN * 0.2))
        self.at_word(n, "Choose")
        self.play(FadeIn(ask, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_02",
            text="Being rainy day; having been a rainy day; it being a rainy day; or no improvement?",
            voice="default",
            subtitle=True,
            pause_after=3.0,
        )
        for row, spoken in zip(opts, ["Being", "having", "it", "no"]):
            self.at_word(n, spoken, occurrence=1)
            self.play(FadeIn(row, shift=UP * 0.15), run_time=0.35)
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        self.clear_stage()
        self.scene_end("S01_hook")

    # ============================================== 2. CONCEPT ==========

    def concept(self):
        self.scene_start("S02_concept", title="The Concept")

        heads = VGroup(*[pill(t, TYPE_COL[t], size=LABEL) for t in TYPES]).arrange(RIGHT, buff=0.35)
        fit_width(heads, SAFE_W)
        heads.move_to(UP * (CARD_TOP - heads.height / 2))

        def below(mob):
            fit_within(mob, SAFE_W, SAFE_H - heads.height - 1.6)
            mob.next_to(heads, DOWN, buff=0.7)
            self.no_overlap(heads, mob)
            self.validator.check_in_frame(VGroup(heads, mob))
            return mob

        n = self.narrate(
            id="concept_01",
            text="Most corrections fall into four types.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "four")
        self.play(LaggedStart(*[FadeIn(h, shift=DOWN * 0.2) for h in heads], lag_ratio=0.25))
        self.wait_for_narration(n)

        grammar = below(VGroup(text("fix S-T-P-A-W errors", LABEL, WORD),
                               VGroup(*[pill(t, WORD, size=LABEL) for t in ["agreement", "tense", "pronoun", "article",
                                                                           "preposition"]]).arrange(RIGHT, buff=0.3))
                        .arrange(DOWN, buff=0.4))
        n = self.narrate(
            id="concept_02",
            text="Grammar corrections fix S, T, P, A, W errors: agreement, tense, pronoun, article, preposition.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Grammar")
        self.play(Indicate(heads[0], color=WORD, scale_factor=1.06), FadeIn(grammar[0], shift=UP * 0.1))
        self.at_word(n, "agreement")
        self.play(LaggedStart(*[FadeIn(g, shift=UP * 0.1) for g in grammar[1]], lag_ratio=0.3), run_time=2.0)
        self.wait_for_narration(n)

        structure = below(VGroup(
            text("fix how the sentence is BUILT", LABEL, RATIO),
            VGroup(pill("dangling modifier", RATIO, size=LABEL),
                   text("an opening phrase with no proper subject to describe", LABEL, INK)).arrange(RIGHT, buff=0.35),
            VGroup(pill("faulty parallelism", RATIO, size=LABEL),
                   text("items in a list in different forms", LABEL, INK)).arrange(RIGHT, buff=0.35))
                          .arrange(DOWN, buff=0.4, aligned_edge=LEFT))
        n = self.narrate(
            id="concept_03",
            text="Structure corrections fix how the sentence is built. The two most common are dangling modifiers, an "
                 "opening phrase with no proper subject to describe, and faulty parallelism: items in a list in different "
                 "forms.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(grammar))
        self.at_word(n, "Structure")
        self.play(Indicate(heads[1], color=RATIO, scale_factor=1.06), FadeIn(structure[0], shift=UP * 0.1))
        self.at_word(n, "dangling")
        self.play(FadeIn(structure[1], shift=RIGHT * 0.2))
        self.at_word(n, "parallelism")
        self.play(FadeIn(structure[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        words = below(VGroup(text("replace a wrong word with the right one", LABEL, SECOND),
                             VGroup(*[pill(t, SECOND, size=LABEL) for t in ["affect / effect", "fewer / less",
                                                                           "good / well", "idioms: fixed form"]])
                             .arrange(RIGHT, buff=0.3)).arrange(DOWN, buff=0.4))
        n = self.narrate(
            id="concept_04",
            text="Word-choice corrections replace a wrong word with the right one: affect and effect, fewer and less, good "
                 "and well, and idioms in their fixed form.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(structure))
        self.at_word(n, "Word-choice")
        self.play(Indicate(heads[2], color=SECOND, scale_factor=1.06), FadeIn(words[0], shift=UP * 0.1))
        for w_, spoken in zip(words[1], ["affect", "fewer", "good", "idioms"]):
            self.at_word(n, spoken)
            self.play(FadeIn(w_, shift=UP * 0.1), run_time=0.35)
        self.wait_for_narration(n)

        repeats = below(VGroup(text("remove words that repeat meaning", LABEL, BAD),
                               VGroup(*[pill(t, BAD, size=LABEL) for t in ["return back", "each and every",
                                                                          "final outcome", "advance planning"]])
                               .arrange(RIGHT, buff=0.3)).arrange(DOWN, buff=0.4))
        n = self.narrate(
            id="concept_05",
            text="Redundancy corrections remove words that repeat meaning: return back, each and every, final outcome, "
                 "advance planning.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(words))
        self.at_word(n, "Redundancy")
        self.play(Indicate(heads[3], color=BAD, scale_factor=1.06), FadeIn(repeats[0], shift=UP * 0.1))
        for r, spoken in zip(repeats[1], ["return", "each", "final", "advance"]):
            self.at_word(n, spoken)
            self.play(FadeIn(r, shift=UP * 0.1), run_time=0.35)
        self.wait_for_narration(n)

        contain = below(VGroup(
            pill("the type tells you what the right option MUST CONTAIN", FOCUS, size=LABEL),
            VGroup(pill("dangling: add the subject", RATIO, size=SMALL),
                   text("“It being a rainy day, …”", LABEL, INK, t2c={"It": GOOD})).arrange(RIGHT, buff=0.35),
            VGroup(pill("…or rewrite as a clause", RATIO, size=SMALL),
                   text("“As it was a rainy day, …”", LABEL, INK, t2c={"As it was": GOOD})).arrange(RIGHT, buff=0.35))
                        .arrange(DOWN, buff=0.45))
        n = self.narrate(
            id="concept_06",
            text="Knowing the type tells you what the right option must contain. For a dangling modifier, the right option "
                 "either adds the correct subject to the phrase, it being a rainy day, or rewrites it as a clause: as it "
                 "was a rainy day.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(repeats))
        self.at_word(n, "contain")
        self.play(FadeIn(contain[0], shift=DOWN * 0.1))
        self.at_word(n, "adds")
        self.play(FadeIn(contain[1], shift=RIGHT * 0.2))
        self.at_word(n, "rewrites")
        self.play(FadeIn(contain[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_concept")

    # ======================================== 3. WHY YOU NEED IT ==========

    def why_you_need_it(self):
        self.scene_start("S03_why", title="Why You Need It")

        ear = pill("structure errors: hard to spot by EAR", BAD, size=LABEL)
        rule = pill("…but easy by RULE", GOOD, size=LABEL)
        named = pill("name the type  →  the correct option becomes predictable", FOCUS, size=LABEL)
        group = VGroup(ear, rule, named).arrange(DOWN, buff=0.7)
        fit_width(group, SAFE_W).move_to(UP * 0.3)
        self.no_overlap(ear, rule, named)
        self.validator.check_in_frame(group)

        n = self.narrate(
            id="why_01",
            text="Structure errors are hard to spot by ear, but easy by rule. Once you can name the type, the correct "
                 "option becomes predictable.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "ear")
        self.play(FadeIn(ear, shift=DOWN * 0.1))
        self.at_word(n, "rule")
        self.play(FadeIn(rule, shift=UP * 0.1))
        self.at_word(n, "name")
        self.play(FadeIn(named, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_why")

    # ============================================== 4. ANALOGY ==========

    def analogy(self):
        self.scene_start("S04_analogy", title="The Analogy")

        device = pill("every incoming device", MUTED, size=LABEL)
        bins = VGroup(*[VGroup(pill(b, c, size=LABEL), text("bin", SMALL, MUTED)).arrange(DOWN, buff=0.1)
                        for b, c in zip(["screen", "battery", "software", "casing"], [WORD, RATIO, SECOND, BAD])])\
            .arrange(RIGHT, buff=0.5)
        tools = pill("the bin tells the technician which tools to pick up", GOOD, size=LABEL)
        first = pill("name the correction TYPE first", FOCUS, size=BODY)
        block = VGroup(device, bins, tools, first).arrange(DOWN, buff=0.55)
        fit_within(block, SAFE_W, SAFE_H - 1.4)
        block.move_to(UP * 0.3)
        self.no_overlap(device, bins, tools, first)
        self.validator.check_in_frame(block)

        n = self.narrate(
            id="analogy_01",
            text="A repair shop sorts every device into a bin first: screen, battery, software, casing. The bin tells the "
                 "technician which tools to pick up. Name the correction type first.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "sorts")
        self.play(FadeIn(device, shift=DOWN * 0.1))
        for b, spoken in zip(bins, ["screen", "battery", "software", "casing"]):
            self.at_word(n, spoken)
            self.play(FadeIn(b, shift=UP * 0.1), run_time=0.3)
        self.at_word(n, "tools")
        self.play(FadeIn(tools, shift=UP * 0.1))
        self.at_word(n, "Name")
        self.play(FadeIn(first, scale=1.05))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_analogy")

    # ======================================== 5-7. WORKED EXAMPLES ==========

    def example_dangling(self):
        self.scene_start("S05_ex_dangling", title="Worked Example 1")
        self.play(self.pin(self.type_pin()))

        first, note, tag, fixed = self.type_example(
            "Walking to the station, my phone fell.", "Walking to the station", "who was walking?  not the phone",
            "dangling modifier", "STRUCTURE", "While I was walking to the station, my phone fell.", "While I was walking")

        n = self.narrate(
            id="ex1_01",
            text="Walking to the station, my phone fell. Who was walking? Not the phone. This is a dangling modifier: a "
                 "structure correction. The fix: while I was walking to the station, my phone fell.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Walking", occurrence=1)
        self.play(FadeIn(first, shift=DOWN * 0.1))
        self.at_word(n, "Who")
        self.play(FadeIn(note, shift=UP * 0.1))
        self.at_word(n, "Not")
        self.play(Indicate(note, color=BAD, scale_factor=1.04))
        self.at_word(n, "dangling")
        self.play(FadeIn(tag, shift=RIGHT * 0.2), self.light_type("STRUCTURE"))
        self.at_word(n, "fix")
        self.play(FadeIn(fixed, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_ex_dangling")

    def example_parallel(self):
        self.scene_start("S06_ex_parallel", title="Worked Example 2")

        first, note, tag, fixed = self.type_example(
            "She likes dancing, singing and to paint.", "dancing, singing and to paint", "a list with mixed forms",
            "faulty parallelism", "STRUCTURE", "She likes dancing, singing and painting.", "dancing, singing and painting")

        n = self.narrate(
            id="ex2_01",
            text="She likes dancing, singing and to paint. A list with mixed forms: faulty parallelism. Make every item the "
                 "same form: dancing, singing and painting.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "likes")
        self.play(FadeIn(first, shift=DOWN * 0.1))
        self.at_word(n, "list")
        self.play(FadeIn(note, shift=UP * 0.1))
        self.at_word(n, "parallelism")
        self.play(FadeIn(tag, shift=RIGHT * 0.2), self.light_type("STRUCTURE"))
        self.at_word(n, "painting")
        self.play(FadeIn(fixed, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_ex_parallel")

    def example_redundant(self):
        self.scene_start("S07_ex_redundant", title="Worked Example 3")

        first, note, tag, fixed = self.type_example(
            "We need to plan in advance.", "plan in advance", "planning is always in advance: the words repeat",
            "redundancy (depending on context)", "REDUNDANCY", "We need to plan.", "plan")

        n = self.narrate(
            id="ex3_01",
            text="We need to plan in advance. Planning is always in advance, so the words repeat: redundancy. The fix, "
                 "depending on context: we need to plan.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "need", occurrence=1)
        self.play(FadeIn(first, shift=DOWN * 0.1))
        self.at_word(n, "Planning")
        self.play(FadeIn(note, shift=UP * 0.1))
        self.at_word(n, "redundancy")
        self.play(FadeIn(tag, shift=RIGHT * 0.2), self.light_type("REDUNDANCY"))
        self.at_word(n, "fix")
        self.play(FadeIn(fixed, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S07_ex_redundant")

    # ================================================ 8. RULES ==========

    def rules(self):
        self.scene_start("S08_rules", title="Rules")
        self.play(self.unpin())

        table = self.table_rows(["Type", "Signal", "Fix"], [[t, s_, f] for t, s_, f, _fam in RULES], [2.8, 5.0, 4.2],
                                size=LABEL)
        for row, (*_x, fam) in zip(table[1:], RULES):
            row[0].set_color(TYPE_COL[fam])
        board = self.card(table, width=SAFE_W - 0.2)
        fit_height(board, SAFE_H - 1.0)
        board.move_to(UP * 0.3)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="rules_01",
            text="Five rows to remember. Grammar: the signal is an S, T, P, A, W error; apply the standard rule. Dangling "
                 "modifier: an opening ing or ed phrase, with the wrong subject after the comma; add the right subject, "
                 "or rewrite as a clause. Parallelism: a list, or a paired conjunction, with mixed forms; make all items "
                 "the same form. Word choice: a confusable pair, or a broken idiom; use the correct word, or the fixed "
                 "form. Redundancy: two words with the same meaning; remove one.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Five")
        self.play(FadeIn(board[0]), FadeIn(table[0]))
        for row, spoken in zip(table[1:], ["Grammar", "Dangling", "Parallelism", "Word", "Redundancy"]):
            self.at_word(n, spoken, occurrence=1)
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.45)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S08_rules")

    # ============================================== 9. PROCESS ==========

    def process(self):
        self.scene_start("S09_process", title="The Process")

        steps = VGroup(*[VGroup(pill(str(i + 1), c, size=SMALL), fitted_text(s_, SAFE_W - 2.2, BODY, INK))
                         .arrange(RIGHT, buff=0.3) for i, (s_, c) in enumerate([
                             ("Identify the correction type from the signal", RATIO),
                             ("Predict what the correct version must contain", STEP_COLS["PREDICT"]),
                             ("Eliminate options that don't contain it, or add new errors", BAD),
                             ("Confirm", GOOD)])])
        steps.arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        board = self.card(steps).move_to(UP * 0.3)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="process_01",
            text="The process. First, identify the correction type from the signal. Second, predict what the correct "
                 "version must contain. Third, eliminate options that don't contain it, or that add new errors. And "
                 "fourth, confirm.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(board[0]))
        for r, spoken in zip(steps, ["First", "Second", "Third", "fourth"]):
            self.at_word(n, spoken)
            self.play(FadeIn(r, shift=RIGHT * 0.2), run_time=0.45)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S09_process")

    # ========================================== 10. HOOK, SOLVED ==========

    def hook_solved(self):
        self.scene_start("S10_hook_solved", title="Hook, Solved")
        self.play(self.pin(self.type_pin()))

        h = self.HOOK
        cx, w = self.free_area()
        club = self.club_card()
        notes = VGroup(pill("dangling: the match wasn't “a rainy day”", RATIO, size=SMALL),
                       pill("needs its own subject:  It being a rainy day", STEP_COLS["PREDICT"], size=SMALL))\
            .arrange(RIGHT, buff=0.35)
        fit_width(notes, w - 0.6)
        notes.next_to(club, DOWN, buff=0.3).to_edge(LEFT, buff=SAFE + 0.6)
        q = OptionQuestion(h["word"], h["options"], h["key"], h["traps"], word_size=LABEL)
        also = text("“As it was a rainy day” would also work, if offered", SMALL, MUTED)
        body = VGroup(q.rows, also).arrange(DOWN, buff=0.35, aligned_edge=LEFT)
        fit_height(body, notes.get_bottom()[1] - 0.3 - (BOTTOM_Y + 0.6))
        body.next_to(notes, DOWN, buff=0.35).to_edge(LEFT, buff=SAFE + 0.6)
        fixed = self.club_card("It being a rainy day", good=True)
        self.no_overlap(club, notes, q.rows, also)
        self.no_overlap(club, self.pinned)
        self.no_overlap(notes, self.pinned)
        self.validator.check_in_frame(VGroup(club, notes, body))

        n = self.narrate(
            id="solved_01",
            text="Let's solve the hook. Read: being a rainy day, the match was cancelled. Predict. It's a dangling "
                 "modifier: the match wasn't a rainy day. The phrase needs its own subject: it being a rainy day.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(club), FadeIn(q.rows))
        self.at_word(n, "Read")
        self.play(Indicate(club[1][1], color=WORD, scale_factor=1.02))
        self.at_word(n, "Predict")
        self.play(self.light_type("STRUCTURE"))
        self.at_word(n, "dangling")
        self.play(FadeIn(notes[0], shift=UP * 0.1))
        self.at_word(n, "subject")
        self.play(FadeIn(notes[1], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_02",
            text="Eliminate. Option A drops the article, and keeps the dangling problem. Option B, having been a rainy day, "
                 "still has no subject. Option D keeps the error.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Eliminate")
        self.play(Indicate(q.rows, color=BAD, scale_factor=1.02))
        for letter, spoken in [("a", "A"), ("b", "B"), ("d", "D")]:
            self.at_word(n, spoken, occurrence=1)
            self.play(*q.strike(letter)[1])
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_03",
            text="Confirm: it being a rainy day, the inter-college match was cancelled. That's the answer. As it was a "
                 "rainy day would also work, if offered.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Confirm")
        self.play(ReplacementTransform(club, fixed))
        self.at_word(n, "answer")
        self.play(*q.confirm()[1])
        self.at_word(n, "also")
        self.play(FadeIn(also, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S10_hook_solved")

    # ========================================== 11. EXAM PATTERNS ==========

    def exam_patterns(self):
        self.scene_start("S11_patterns", title="Exam Patterns and Solving Models")
        self.play(self.unpin())

        table = self.table_rows(["Pattern", "Solving model"], [
            ["Opening participle phrase", "check who or what is doing the action"],
            ["Lists with and / or", "match the form of every item"],
            ["Paired conjunctions", "same form on both sides (not only X but also Y)"],
        ], [4.8, 7.0], size=LABEL)
        board = self.card(table, width=SAFE_W - 0.2).move_to(UP * 0.4)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="patterns_01",
            text="Three exam patterns. An opening participle phrase: check who, or what, is doing the action. Lists with "
                 "and, or or: match the form of every item. And paired conjunctions: use the same form on both sides, as "
                 "in not only X, but also Y.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(board[0]), FadeIn(table[0]))
        for row, spoken in zip(table[1:], ["opening", "Lists", "paired"]):
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
            (self.verdict_card(False, "Missing a dangling modifier: it “sounds normal”", card_w),
             self.verdict_card(True, "Ask: who is doing the action?", card_w)),
            (self.verdict_card(False, "Fixing one item in a list, not the others", card_w),
             self.verdict_card(True, "Every item: the same form", card_w)),
            (self.verdict_card(False, "Redundancy as “acceptable emphasis”", card_w),
             self.verdict_card(True, "Remove the repeat", card_w)),
        ]
        for (wrong, right), yy in zip(pairs, [1.6, 0.05, -1.5]):
            wrong.move_to(LEFT_ZONE + UP * yy)
            right.move_to(RIGHT_ZONE + UP * yy)
        header = pill("3 mistakes", BAD, size=LABEL).move_to(UP * (CARD_TOP - 0.3))
        self.validator.check_in_frame(VGroup(header, *[c for p in pairs for c in p]))

        n = self.narrate(
            id="mistakes_01",
            text="Three common mistakes. The first is missing dangling modifiers, because the sentence sounds normal. The "
                 "second is fixing one item in a list, but not the others. The third is treating redundancy as acceptable "
                 "emphasis.",
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
        ("Having finished the work, the laptop was switched off.", "Having finished the work",
         ["Having been finished the work, the laptop was switched off",
          "Having finished the work, she switched off the laptop", "Finishing the work, the laptop switched off",
          "No improvement"], "b", "gives the phrase its real subject"),
        ("The job requires coding, testing and to document.", "coding, testing and to document",
         ["coding, testing and documenting", "to code, testing and documentation", "code, test and documenting",
          "No improvement"], "a", "parallel -ing forms"),
        ("Please return back the form by Friday.", "return back",
         ["return it back", "give back return", "return", "No improvement"], "c", "remove the redundancy"),
    ]

    def practice(self):
        self.scene_start("S13_practice", title="Practice Questions")

        lines = VGroup(*[VGroup(VGroup(pill(str(i + 1), FOCUS, size=SMALL),
                                       text(f"“{sent}”", LABEL, INK, t2c={bold: WORD})).arrange(RIGHT, buff=0.35),
                                fitted_text("   ".join(f"({l}) {o}" for l, o in zip("abcd", opts)), SAFE_W - 1.6, SMALL,
                                            INK, NORMAL, max_lines=3))
                         .arrange(DOWN, buff=0.2, aligned_edge=LEFT)
                         for i, (sent, bold, opts, *_r) in enumerate(self.PRACTICE)])
        lines.arrange(DOWN, buff=0.4, aligned_edge=LEFT)
        board = self.card(lines, color=FOCUS)
        fit_within(board, SAFE_W, SAFE_H - 1.2)
        board.move_to(UP * 0.4)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="practice_01",
            text="Your turn. One: having finished the work, the laptop was switched off. Pick the version where the opening "
                 "phrase has its real subject. Two: the job requires coding, testing and to document. Pick the parallel "
                 "list. Three: please return back the form by Friday. Pick the version without the repeat.",
            voice="default",
            subtitle=True,
            pause_after=12.0,
        )
        self.at_word(n, "turn")
        self.play(FadeIn(board[0]))
        for ln, (spoken, occ) in zip(lines, [("laptop", 1), ("requires", 2), ("return", 3)]):
            self.at_word(n, spoken)
            self.play(FadeIn(ln[0], shift=UP * 0.15), run_time=0.4)
            self.at_word(n, "Pick", occurrence=occ)
            self.play(FadeIn(ln[1], shift=LEFT * 0.15), run_time=0.4)
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        self.clear_stage()
        self.scene_end("S13_practice")

    # =============================================== 14. ANSWERS ==========

    def answers(self):
        self.scene_start("S14_answers", title="Answers")

        rows = VGroup(*[VGroup(VGroup(pill(str(i + 1), FOCUS, size=SMALL),
                                      fitted_text(f"({key}) {opts['abcd'.index(key)]}", SAFE_W - 2.0, LABEL, GOOD))
                               .arrange(RIGHT, buff=0.3), text(why, SMALL, RATIO)).arrange(DOWN, buff=0.18, aligned_edge=LEFT)
                        for i, (_sent, _bold, opts, key, why) in enumerate(self.PRACTICE)])
        rows.arrange(DOWN, buff=0.55, aligned_edge=LEFT)
        fit_within(rows, SAFE_W, SAFE_H - 1.2)
        rows.move_to(UP * 0.3)
        self.validator.check_in_frame(rows)

        n = self.narrate(
            id="answers_01",
            text="One: option B: having finished the work, she switched off the laptop. It gives the phrase its real "
                 "subject. Two: option A: coding, testing and documenting. Parallel ing forms. Three: option C: return. "
                 "Remove the redundancy.",
            voice="default",
            subtitle=True,
        )
        for r, (spoken, why) in zip(rows, [("One", "real"), ("Two", "Parallel"), ("Three", "Remove")]):
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

        card, table = self.recap_card("Recap Card: Video 2", [
            ["Four types", "grammar · structure · word choice · redundancy"],
            ["Dangling modifier", "give the phrase its real subject"],
            ["Parallelism", "same form for every item"],
            ["Redundancy", "remove the repeat"],
        ])
        card.move_to(UP * 0.2)
        self.validator.check_in_frame(card)

        n = self.narrate(
            id="recap_01",
            text="To recap. Four types: grammar, structure, word choice, redundancy. A dangling modifier: give the phrase "
                 "its real subject. Parallelism: the same form for every item. And the last one: remove the repeat.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(card[0]), FadeIn(table[0]))
        for row, spoken in zip(table[1:], ["types", "dangling", "Parallelism", "repeat"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.45)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S15_recap")

    # ================================================= 16. NEXT ==========

    def next_video(self):
        self.scene_start("S16_next", title="Next")

        setting = pill("grammatically correct, but wrong for the setting", BAD, size=LABEL)
        nxt = pill("Next:  Context-Based Correction (Register and Clarity)", FOCUS, size=LABEL)
        VGroup(setting, nxt).arrange(DOWN, buff=0.8).move_to(UP * 0.2)
        self.no_overlap(setting, nxt)
        self.validator.check_in_frame(VGroup(setting, nxt))

        n = self.narrate(
            id="next_01",
            text="Some sentences are grammatically correct, but wrong for their setting. Video three covers register and "
                 "clarity.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "setting")
        self.play(FadeIn(setting, shift=DOWN * 0.1))
        self.at_word(n, "Video")
        self.play(FadeIn(nxt, scale=1.05))
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S16_next")
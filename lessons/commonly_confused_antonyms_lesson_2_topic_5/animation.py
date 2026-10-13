"""
animation.py for the LMS video generator.

Course : C-CAT - Section A - English
Module : Module 1 - Vocabulary
Lesson : Lesson 2 - Antonyms
Video  : 05 - Commonly Confused Antonyms (Video 5 of 7)

Source script:
  C:\\Users\\User\\Downloads\\C-CAT_SectionA_Module1_English\\English\\Module 1 - Vocabulary\\
  Lesson 2 - Antonyms\\05 - Commonly Confused Antonyms.pdf

Built on the golden-reference pattern:
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``;
  * layouts stacked with next_to and guarded with ``no_overlap``; nothing is
    ever animated onto or into another box.

Opening: a later video of Lesson 2, so no spoken welcome. The module > lesson >
video trail is shown on screen (silent), then a one-line recap of Video 4
(prefixes that mislead) and Lesson 1 Video 4 (the confused pairs), the title
and the objectives.

Pinned panel: the "decode first" method (exact meaning -> mirror image ->
reject "prefix removed" -> reject a different topic) stays in the top-right
corner through the worked examples and again in Hook, Solved; the step in use
lights up.

Data: ``PAIRS`` holds each word's true opposites and its common wrong answer
(the script's Rules table). The rules table, recap card and mistake cards are
built from it, and ``check_answer`` asserts each keyed option is a listed true
opposite. Every narration sentence has its own visual cue.
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

# word -> (true opposites, the common wrong answer), from the script's Rules table.
PAIRS = {
    "disinterested": (["biased", "partial"], "interested"),
    "infamous": (["reputable", "respected"], "famous"),
    "invaluable": (["worthless"], "valuable"),
    "generous": (["mean", "stingy"], "poor"),
    "eminent": (["obscure", "unknown"], "imminent"),
    "imminent": (["remote", "distant"], "eminent"),
    "brave": (["cowardly"], "careful"),
}


def mirror_row(word, size=LABEL):
    """word  ↔  its true opposite(s) ✓   |   the common wrong answer ✗"""
    good, wrong = PAIRS[word]
    return VGroup(pill(word, WORD, size=size), text("↔", size, MUTED), pill(", ".join(good) + "  ✓", GOOD, size=size),
                  pill(wrong + "  ✗", BAD, size=size)).arrange(RIGHT, buff=0.3)


def check_answer(word, options, key):
    """The keyed option must be a listed true opposite of ``word``."""
    assert options["abcd".index(key)] in PAIRS[word][0], (word, options, key)


class CommonlyConfusedAntonymsVideo(LMSScene):
    lesson_title = "Commonly Confused Antonyms"

    def construct(self):
        self.camera.background_color = BG

        self.lesson_intro()
        self.hook()
        self.concept_false()
        self.concept_near_and_lookalike()
        self.why_you_need_it()
        self.analogy()
        self.example_disinterested()
        self.example_generous()
        self.example_imminent()
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

    def decode_pin(self):
        return self.steps_pin("decode first", [("exact meaning of the word", WORD),
                                               ("predict its mirror image", STEP_COLS["PREDICT"]),
                                               ("reject “prefix removed”", BAD), ("reject a different topic", RATIO)])

    def option_example(self, word, options, key, traps):
        q = OptionQuestion(word, options, key, traps)
        q.group.to_edge(LEFT, buff=SAFE + 0.6).set_y(0.3)
        self.no_overlap(q.group, self.pinned)
        self.validator.check_in_frame(q.group)
        return q

    # ========================================= 0. LESSON INTRO ==========

    def lesson_intro(self):
        self.scene_start("S00_intro", title="Lesson Introduction")

        crumb = self.breadcrumb("English · Module 1 Vocabulary", "Lesson 2 · Antonyms", "Video 5")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        mislead = VGroup(pill("inflammable", BAD, size=LABEL), text("=", LABEL, MUTED), pill("flammable", GOOD, size=LABEL))\
            .arrange(RIGHT, buff=0.3)
        pairs = pill("Lesson 1, Video 4 pairs: eminent / imminent, disinterested / uninterested …", SECOND, size=SMALL)
        fit_width(pairs, SAFE_W)
        flipped = pill("today: flipped into antonym form", GOOD, size=LABEL)
        VGroup(mislead, pairs, flipped).arrange(DOWN, buff=0.55).move_to(DOWN * 0.1)
        self.no_overlap(crumb, mislead, pairs, flipped)
        self.validator.check_in_frame(VGroup(crumb, mislead, pairs, flipped))

        n = self.narrate(
            id="intro_01",
            text="Video four showed that some prefixes mislead. Today we apply that caution across the most commonly "
                 "confused pairs from lesson one, video four, flipped into antonym form.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.at_word(n, "mislead")
        self.play(FadeIn(mislead, shift=UP * 0.1))
        self.at_word(n, "pairs")
        self.play(FadeIn(pairs, shift=UP * 0.1))
        self.at_word(n, "flipped")
        self.play(FadeIn(flipped, shift=UP * 0.1))
        self.wait_for_narration(n)

        title = fitted_text("Commonly Confused Antonyms", SAFE_W, 72, INK, BOLD)
        underline = Line(LEFT, RIGHT, color=BAD, stroke_width=5).set_width(title.width * 0.6)
        VGroup(title, underline).arrange(DOWN, buff=0.2).move_to(UP * 0.2)
        goals = [("Avoid false opposites created by removing a prefix", BAD),
                 ("Separate near-opposites from true opposites", GOOD)]
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
            text="These are the commonly confused antonyms. By the end of this video, you'll avoid false opposites created "
                 "by removing a prefix, and separate near-opposites from true opposites.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(VGroup(mislead, pairs, flipped), shift=UP * 0.3))
        self.at_word(n, "confused")
        self.play(Write(title), run_time=1.1)
        self.play(GrowFromCenter(underline))
        self.at_word(n, "By")
        self.play(FadeOut(underline), ReplacementTransform(title, small_title), run_time=0.8)
        self.play(FadeIn(objectives[0]), FadeIn(heading))
        for row_, spoken in zip(rows, ["avoid", "separate"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row_, shift=RIGHT * 0.2), run_time=0.5)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_intro")

    # ================================================= 1. HOOK ==========

    HOOK = dict(word="DISINTERESTED", options=["biased", "interested", "bored", "curious"], key="a",
                traps={"b": "the prefix-removed trap", "c": "that's “uninterested”", "d": "unrelated"})

    def brief_card(self, margin=True):
        head = text("INTERVIEW PANEL BRIEF", SMALL, RATIO, BOLD)
        line = text("“The panel must be disinterested.”", BODY, INK, t2c={"disinterested": WORD})
        items = [head, line]
        if margin:
            items.append(text("margin note:  opposite = interested ?", LABEL, BAD))
        cx, w = self.free_area()
        card = self.card(VGroup(*items).arrange(DOWN, buff=0.2, aligned_edge=LEFT), width=min(w - 0.2, SAFE_W - 0.4))
        return card.move_to(RIGHT * cx + UP * (CARD_TOP - card.height / 2))

    def hook(self):
        self.scene_start("S01_hook", title="Hook")

        h = self.HOOK
        check_answer("disinterested", h["options"], h["key"])
        brief = self.brief_card()
        q = OptionQuestion(h["word"], h["options"], h["key"], h["traps"])
        opts = q.rows.copy().arrange(RIGHT, buff=0.8)
        ask = pill("What's the REAL opposite of disinterested?", FOCUS, size=LABEL)
        ask.next_to(brief, DOWN, buff=0.5)
        opts.next_to(ask, DOWN, buff=0.5)
        self.no_overlap(brief, ask, opts)
        self.validator.check_in_frame(VGroup(brief, ask, opts))

        n = self.narrate(
            id="hook_01",
            text="An HR executive is preparing an interview panel brief that says the panel must be disinterested. She "
                 "writes opposite, interested, in the margin. What's the real opposite of disinterested?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "brief")
        self.play(FadeIn(brief[0]), FadeIn(brief[1][:2]))
        self.at_word(n, "margin")
        self.play(FadeIn(brief[1][2], shift=LEFT * 0.2))
        self.at_word(n, "real")
        self.play(FadeIn(ask, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_02",
            text="Biased, interested, bored, or curious?",
            voice="default",
            subtitle=True,
            pause_after=3.0,
        )
        for row, spoken in zip(opts, ["Biased", "interested", "bored", "curious"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=UP * 0.15), run_time=0.35)
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        self.clear_stage()
        self.scene_end("S01_hook")

    # ===================================== 2. CONCEPT: FALSE OPPOSITES ==========

    def concept_false(self):
        self.scene_start("S02_concept_false", title="The Concept - False Opposites")

        three = VGroup(pill("false opposites", BAD, size=LABEL), pill("near-opposites", RATIO, size=LABEL),
                       pill("look-alike opposites", SECOND, size=LABEL)).arrange(RIGHT, buff=0.4)
        fit_width(three, SAFE_W)
        three.move_to(UP * (CARD_TOP - three.height / 2))
        rule = text("removing a prefix doesn't always give the opposite", LABEL, MUTED)
        rule.next_to(three, DOWN, buff=0.4)
        r1 = mirror_row("disinterested")
        m1 = text("disinterested = impartial", SMALL, WORD)
        r2 = mirror_row("infamous")
        block = VGroup(m1, r1, r2).arrange(DOWN, buff=0.4, aligned_edge=LEFT)
        fit_width(block, SAFE_W)
        block.next_to(rule, DOWN, buff=0.5)
        self.no_overlap(three, rule, block)
        self.validator.check_in_frame(VGroup(three, rule, block))

        n = self.narrate(
            id="false_01",
            text="Three kinds of confusion cost the most marks. First, false opposites. Removing a prefix doesn't always "
                 "give the opposite.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Three")
        self.play(LaggedStart(*[FadeIn(t, shift=DOWN * 0.1) for t in three], lag_ratio=0.2))
        self.at_word(n, "false")
        self.play(Indicate(three[0], color=BAD, scale_factor=1.1))
        self.at_word(n, "Removing")
        self.play(FadeIn(rule, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="false_02",
            text="Disinterested means impartial, so its opposite is biased or partial, not interested. The opposite of "
                 "infamous isn't famous; it's closer to reputable or respected.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "impartial")
        self.play(FadeIn(m1, shift=UP * 0.1), FadeIn(r1[0]))
        self.at_word(n, "biased")
        self.play(FadeIn(r1[1:3], shift=RIGHT * 0.1))
        self.at_word(n, "interested")
        self.play(FadeIn(r1[3], shift=RIGHT * 0.1))
        self.at_word(n, "infamous")
        self.play(FadeIn(r2[0]), FadeIn(r2[3], shift=RIGHT * 0.1))
        self.at_word(n, "reputable")
        self.play(FadeIn(r2[1:3], shift=RIGHT * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_concept_false")

    # ============================ 3. CONCEPT: NEAR-OPPOSITES, LOOK-ALIKES ==========

    def concept_near_and_lookalike(self):
        self.scene_start("S03_concept_near", title="The Concept - Near-Opposites and Look-Alikes")

        head1 = pill("near-opposites: different, but not opposite", RATIO, size=LABEL)
        head1.move_to(UP * (CARD_TOP - head1.height / 2))
        near = VGroup(mirror_row("generous"), mirror_row("brave")).arrange(DOWN, buff=0.35, aligned_edge=LEFT)
        topic = text("“poor” is only a different topic", SMALL, MUTED)
        block1 = VGroup(near, topic).arrange(DOWN, buff=0.25, aligned_edge=LEFT)
        fit_width(block1, SAFE_W)
        block1.next_to(head1, DOWN, buff=0.45)
        self.no_overlap(head1, block1)
        self.validator.check_in_frame(VGroup(head1, block1))

        n = self.narrate(
            id="near_01",
            text="Second, near-opposites. Some words are different, but not opposite. The opposite of generous is mean or "
                 "stingy; poor is only a different topic. The opposite of brave is cowardly, not careful.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "near-opposites")
        self.play(FadeIn(head1, shift=DOWN * 0.2))
        self.at_word(n, "generous")
        self.play(FadeIn(near[0][:3], shift=RIGHT * 0.1))
        self.at_word(n, "poor")
        self.play(FadeIn(near[0][3], shift=RIGHT * 0.1), FadeIn(topic))
        self.at_word(n, "brave")
        self.play(FadeIn(near[1][:3], shift=RIGHT * 0.1))
        self.at_word(n, "careful")
        self.play(FadeIn(near[1][3], shift=RIGHT * 0.1))
        self.wait_for_narration(n)

        head2 = pill("look-alike opposites: the Lesson 1 look-alikes again", SECOND, size=LABEL)
        head2.move_to(head1)
        look = VGroup(VGroup(text("eminent = distinguished", SMALL, WORD), mirror_row("eminent")).arrange(
            DOWN, buff=0.15, aligned_edge=LEFT), VGroup(text("imminent = about to happen", SMALL, WORD),
                                                         mirror_row("imminent")).arrange(DOWN, buff=0.15,
                                                                                         aligned_edge=LEFT))
        look.arrange(DOWN, buff=0.45, aligned_edge=LEFT)
        fit_width(look, SAFE_W)
        look.next_to(head2, DOWN, buff=0.45)
        self.no_overlap(head2, look)
        self.validator.check_in_frame(VGroup(head2, look))
        n = self.narrate(
            id="near_02",
            text="Third, look-alike opposites. Look-alikes from lesson one appear here too. The opposite of eminent, "
                 "meaning distinguished, is obscure or unknown. The opposite of imminent, meaning about to happen, is "
                 "distant or remote.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(VGroup(head1, block1)))
        self.at_word(n, "look-alike")
        self.play(FadeIn(head2, shift=DOWN * 0.2))
        self.at_word(n, "lesson")
        self.play(Indicate(head2, color=SECOND, scale_factor=1.03))
        self.at_word(n, "eminent")
        self.play(FadeIn(look[0], shift=RIGHT * 0.1))
        self.at_word(n, "imminent")
        self.play(FadeIn(look[1], shift=RIGHT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="near_03",
            text="The defence is the same each time: decode the exact meaning of the question word before you reverse it.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "decode")
        cap = self.caption("Decode the EXACT meaning before you reverse it", GOOD)
        self.play(FadeIn(cap, shift=UP * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_concept_near")

    # ======================================== 4. WHY YOU NEED IT ==========

    def why_you_need_it(self):
        self.scene_start("S04_why", title="Why You Need It")

        obvious = VGroup(pill("disinterested", WORD, size=LABEL), text("→", LABEL, MUTED),
                         pill("interested  ✗", BAD, size=LABEL), text("the “obvious” answer is wrong by design", SMALL,
                                                                     BAD)).arrange(RIGHT, buff=0.3)
        where = VGroup(pill("antonym questions", BAD, size=LABEL), pill("Spotting Errors", SECOND, size=LABEL))\
            .arrange(RIGHT, buff=0.5)
        group = VGroup(obvious, where).arrange(DOWN, buff=0.9)
        fit_width(group, SAFE_W).move_to(UP * 0.3)
        self.no_overlap(obvious, where)
        self.validator.check_in_frame(group)

        n = self.narrate(
            id="why_01",
            text="These pairs are designed so that the obvious antonym, often the word without its prefix, is wrong. They "
                 "appear in antonym questions, and the underlying words appear in spotting errors.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "obvious")
        self.play(FadeIn(obvious, shift=UP * 0.1))
        self.at_word(n, "questions")
        self.play(FadeIn(where[0], shift=UP * 0.1))
        self.at_word(n, "spotting")
        self.play(FadeIn(where[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_why")

    # ============================================== 5. ANALOGY ==========

    def analogy(self):
        self.scene_start("S05_analogy", title="The Analogy")

        mirror = DashedLine(UP * 1.6, DOWN * 1.2, color=WORD, stroke_width=4).move_to(LEFT * 1.2 + UP * 0.3)
        m_lab = text("mirror", SMALL, WORD).next_to(mirror, UP, buff=0.15)
        left_glove = pill("left glove", INK, size=LABEL, fill_opacity=0.06).next_to(mirror, LEFT, buff=0.7)
        right_glove = pill("right glove", GOOD, size=LABEL).next_to(mirror, RIGHT, buff=0.7)
        shoe = pill("left shoe", RATIO, size=LABEL).next_to(right_glove, RIGHT, buff=1.0)
        tags = VGroup(text("antonym: the mirror image", SMALL, GOOD).next_to(right_glove, DOWN, buff=0.3),
                      text("near-opposite: a different object", SMALL, RATIO).next_to(shoe, UP, buff=0.3))
        check = pill("check that your answer mirrors the SAME thing", FOCUS, size=LABEL).move_to(DOWN * 2.2)
        self.no_overlap(left_glove, right_glove, shoe, check)
        self.validator.check_in_frame(VGroup(mirror, m_lab, left_glove, right_glove, shoe, tags, check))

        n = self.narrate(
            id="analogy_01",
            text="An antonym is a mirror image of the meaning. A near-opposite is just a different object.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "mirror")
        self.play(Create(mirror), FadeIn(m_lab), FadeIn(left_glove))
        self.play(FadeIn(right_glove, shift=RIGHT * 0.2), FadeIn(tags[0]))
        self.at_word(n, "different")
        self.play(FadeIn(shoe, shift=LEFT * 0.2), FadeIn(tags[1]))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_02",
            text="A left shoe isn't the mirror image of a left glove, even though both are left. Check that your answer "
                 "mirrors the same thing.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "shoe")
        self.play(Indicate(shoe, color=BAD, scale_factor=1.1))
        self.at_word(n, "Check")
        self.play(FadeIn(check, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_analogy")

    # ======================================== 6-8. WORKED EXAMPLES ==========

    def example_disinterested(self):
        self.scene_start("S06_ex_disinterested", title="Worked Example 1")
        self.play(self.pin(self.decode_pin()))

        opts, key = ["interested", "partial", "bored", "lazy"], "b"
        check_answer("disinterested", opts, key)
        q = self.option_example("DISINTERESTED", opts, key,
                                {"a": "prefix removed", "c": "that's “uninterested”", "d": "unrelated"})

        n = self.narrate(
            id="ex1_01",
            text="Disinterested: interested, partial, bored, or lazy? It means impartial. Its mirror is taking sides: "
                 "partial. Interested is just the prefix removed.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(q.word, scale=1.1))
        self.at_word(n, "interested", occurrence=1)
        self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.2) for r in q.rows], lag_ratio=0.2))
        self.at_word(n, "impartial")
        self.play(self.pin_step(0))
        self.at_word(n, "mirror")
        self.play(*q.confirm()[1], self.pin_step(1))
        self.at_word(n, "Interested", occurrence=2)
        self.play(*q.strike("a")[1], *q.strike("c")[1], *q.strike("d")[1], self.pin_step(2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_ex_disinterested")

    def example_generous(self):
        self.scene_start("S07_ex_generous", title="Worked Example 2")

        opts, key = ["poor", "mean", "kind", "rich"], "b"
        check_answer("generous", opts, key)
        q = self.option_example("GENEROUS", opts, key,
                                {"a": "different topic: money owned", "c": "synonym", "d": "different topic"})

        n = self.narrate(
            id="ex2_01",
            text="Generous: poor, mean, kind, or rich? The opposite is mean. Poor is about money owned, not how you share "
                 "it.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(q.word, scale=1.1), self.pin_step(0))
        self.at_word(n, "poor", occurrence=1)
        self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.2) for r in q.rows], lag_ratio=0.2))
        self.at_word(n, "opposite")
        self.play(*q.confirm()[1], self.pin_step(1))
        self.at_word(n, "Poor", occurrence=2)
        self.play(*q.strike("a")[1], *q.strike("c")[1], *q.strike("d")[1], self.pin_step(3))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S07_ex_generous")

    def example_imminent(self):
        self.scene_start("S08_ex_imminent", title="Worked Example 3")

        opts, key = ["eminent", "remote", "sudden", "urgent"], "b"
        check_answer("imminent", opts, key)
        q = self.option_example("IMMINENT", opts, key,
                                {"a": "look-alike", "c": "related, not opposite", "d": "synonym-like"})

        n = self.narrate(
            id="ex3_01",
            text="Imminent: eminent, remote, sudden, or urgent? Imminent means about to happen, so its opposite is remote. "
                 "Eminent is a look-alike.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(q.word, scale=1.1))
        self.at_word(n, "eminent", occurrence=1)
        self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.2) for r in q.rows], lag_ratio=0.2))
        self.at_word(n, "means")
        self.play(self.pin_step(0))
        self.at_word(n, "opposite")
        self.play(*q.confirm()[1], self.pin_step(1))
        self.at_word(n, "Eminent", occurrence=2)
        self.play(*q.strike("a")[1], *q.strike("c")[1], *q.strike("d")[1])
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S08_ex_imminent")

    # ================================================ 9. RULES ==========

    def rules(self):
        self.scene_start("S09_rules", title="Rules")
        self.play(self.unpin())

        order = ["disinterested", "infamous", "invaluable", "generous", "eminent", "imminent", "brave"]
        table = self.table_rows(["Word", "True opposite", "Common wrong answer"],
                                [[w, ", ".join(PAIRS[w][0]), PAIRS[w][1]] for w in order], [4.0, 4.4, 3.4], size=LABEL)
        for row in table[1:]:
            row[1].set_color(GOOD)
            row[2].set_color(BAD)
        board = self.card(table, width=SAFE_W - 0.2)
        fit_height(board, SAFE_H - 1.0)
        board.move_to(UP * (CARD_TOP - board.height / 2))
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="rules_01",
            text="Here are the pairs to know. Disinterested: biased, not interested. Infamous: reputable, not famous. "
                 "Invaluable: worthless, not valuable. Generous: mean, not poor.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(board[0]), FadeIn(table[0]))
        for row, spoken in zip(table[1:5], ["Disinterested", "Infamous", "Invaluable", "Generous"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.4)
        self.wait_for_narration(n)

        n = self.narrate(
            id="rules_02",
            text="Eminent: obscure, not imminent. Imminent: remote, not eminent. And brave: cowardly, not careful.",
            voice="default",
            subtitle=True,
        )
        for row, (spoken, occ) in zip(table[5:], [("Eminent", 1), ("Imminent", 2), ("brave", 1)]):
            self.at_word(n, spoken, occurrence=occ)
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.4)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S09_rules")

    # ============================================= 10. PROCESS ==========

    def process(self):
        self.scene_start("S10_process", title="The Process")

        steps = VGroup(*[VGroup(pill(str(i + 1), c, size=SMALL), fitted_text(s_, SAFE_W - 2.2, BODY, INK))
                         .arrange(RIGHT, buff=0.3) for i, (s_, c) in enumerate([
                             ("Decode the exact meaning, especially if it has a prefix", WORD),
                             ("Predict the mirror image of that meaning", STEP_COLS["PREDICT"]),
                             ("Reject the “prefix-removed” option unless it truly mirrors", BAD),
                             ("Reject options that are just a different topic", RATIO)])])
        steps.arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        board = self.card(steps).move_to(UP * 0.3)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="process_01",
            text="The process. First, decode the exact meaning of the question word, especially if it has a prefix. "
                 "Second, predict the mirror image of that meaning. Third, reject the prefix-removed option, unless it "
                 "truly mirrors the meaning. And fourth, reject options that are just a different topic.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(board[0]))
        for r, spoken in zip(steps, ["First", "Second", "Third", "fourth"]):
            self.at_word(n, spoken)
            self.play(FadeIn(r, shift=RIGHT * 0.2), run_time=0.45)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S10_process")

    # ========================================== 11. HOOK, SOLVED ==========

    def hook_solved(self):
        self.scene_start("S11_hook_solved", title="Hook, Solved")
        self.play(self.pin(self.decode_pin()))

        h = self.HOOK
        brief = self.brief_card(margin=False)
        q = OptionQuestion(h["word"], h["options"], h["key"], h["traps"], word_size=BODY)
        q.group.next_to(brief, DOWN, buff=0.4).to_edge(LEFT, buff=SAFE + 0.6)
        # Two lines, so the pill ends before the pinned panel (one line ran underneath it).
        predict = pill("impartial\n→ mirror: taking sides", STEP_COLS["PREDICT"], size=SMALL)
        cx, w = self.free_area()
        fit_width(predict, cx + w / 2 - q.word.get_right()[0] - 0.4)
        predict.next_to(q.word, RIGHT, buff=0.4)
        conf = text("“The panel must not be biased.”", LABEL, GOOD)
        conf.to_edge(DOWN, buff=SAFE + 0.4)
        self.no_overlap(brief, q.group, conf)
        self.no_overlap(brief, self.pinned)
        self.no_overlap(q.group, predict, self.pinned)
        self.validator.check_in_frame(VGroup(brief, q.group, predict, conf))

        n = self.narrate(
            id="solved_01",
            text="Let's solve the hook. Read: disinterested means impartial, with no personal stake. Predict its mirror: "
                 "taking sides, biased.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(brief), FadeIn(q.word), FadeIn(q.rows))
        self.at_word(n, "Read")
        self.play(Indicate(q.word, color=WORD, scale_factor=1.08), self.pin_step(0))
        self.at_word(n, "Predict")
        self.play(FadeIn(predict, shift=LEFT * 0.1), self.pin_step(1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_02",
            text="Eliminate. Interested is the prefix-removed trap. Bored is the meaning of uninterested. Curious is "
                 "unrelated.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Eliminate")
        self.play(Indicate(q.rows, color=BAD, scale_factor=1.02))
        self.at_word(n, "Interested")
        self.play(*q.strike("b")[1], self.pin_step(2))
        self.at_word(n, "Bored")
        self.play(*q.strike("c")[1])
        self.at_word(n, "Curious")
        self.play(*q.strike("d")[1], self.pin_step(3))
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_03",
            text="Confirm: the panel must not be biased. The answer is biased.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Confirm")
        self.play(FadeIn(conf, shift=UP * 0.1))
        self.at_word(n, "answer")
        self.play(*q.confirm()[1])
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S11_hook_solved")

    # ========================================== 12. EXAM PATTERNS ==========

    def exam_patterns(self):
        self.scene_start("S12_patterns", title="Exam Patterns and Solving Models")
        self.play(self.unpin())

        table = self.table_rows(["Pattern", "Solving model"], [
            ["Prefixed word", "decode first; don't just strip the prefix"],
            ["Two “negative-looking” options", "choose the one that mirrors the exact core"],
            ["Look-alike in the options", "default to “trap”"],
        ], [4.8, 7.0], size=LABEL)
        board = self.card(table, width=SAFE_W - 0.2).move_to(UP * 0.4)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="patterns_01",
            text="Three exam patterns. A prefixed word: decode first, and don't just strip the prefix. Two negative-looking "
                 "options: choose the one that mirrors the exact core. And a look-alike in the options: default to trap.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(board[0]), FadeIn(table[0]))
        for row, spoken in zip(table[1:], ["prefixed", "Two", "look-alike"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.45)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S12_patterns")

    # ======================================== 13. COMMON MISTAKES ==========

    def common_mistakes(self):
        self.scene_start("S13_mistakes", title="Common Mistakes")

        card_w = ZONE_W - 0.3
        pairs = [
            (self.verdict_card(False, "Stripping the prefix: disinterested → interested", card_w),
             self.verdict_card(True, "disinterested ↔ " + PAIRS["disinterested"][0][0], card_w)),
            (self.verdict_card(False, "A different topic: generous → poor", card_w),
             self.verdict_card(True, "generous ↔ " + PAIRS["generous"][0][0], card_w)),
            (self.verdict_card(False, "Confusing look-alikes: imminent → eminent", card_w),
             self.verdict_card(True, "imminent ↔ " + PAIRS["imminent"][0][0], card_w)),
        ]
        for (wrong, right), yy in zip(pairs, [1.6, 0.05, -1.5]):
            wrong.move_to(LEFT_ZONE + UP * yy)
            right.move_to(RIGHT_ZONE + UP * yy)
        header = pill("3 mistakes", BAD, size=LABEL).move_to(UP * (CARD_TOP - 0.3))
        self.validator.check_in_frame(VGroup(header, *[c for p in pairs for c in p]))

        n = self.narrate(
            id="mistakes_01",
            text="Three common mistakes. The first is stripping the prefix: disinterested to interested. The second is "
                 "choosing a different topic: generous to poor. The third is confusing look-alikes: imminent to eminent.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(header))
        for pr, (spoken, example) in zip(pairs, [("first", "disinterested"), ("second", "generous"),
                                                 ("third", "imminent")]):
            self.at_word(n, spoken)
            self.play(FadeIn(pr[0], shift=RIGHT * 0.3), run_time=0.4)
            self.at_word(n, example)
            self.play(FadeIn(pr[1], shift=LEFT * 0.3), run_time=0.4)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S13_mistakes")

    # ============================================== 14. PRACTICE ==========

    PRACTICE = [
        ("INFAMOUS", ["famous", "unknown", "popular", "respected"], "d",
         {"a": "prefix removed", "b": "different topic", "c": "different topic"}, "infamous = known for bad deeds"),
        ("FRUGAL", ["poor", "extravagant", "careful", "greedy"], "b",
         {"a": "different topic", "c": "synonym", "d": "different topic"}, "frugal = careful with money"),
        ("PARTIAL (in judgement)", ["complete", "whole", "impartial", "partly"], "c",
         {"a": "opposes “incomplete”", "b": "opposes “incomplete”", "d": "synonym of the other meaning"},
         "in judgement, partial = biased"),
    ]

    def practice(self):
        self.scene_start("S14_practice", title="Practice Questions")

        check_answer("infamous", self.PRACTICE[0][1], self.PRACTICE[0][2])
        head = pill("Choose the OPPOSITE", BAD, size=LABEL)
        lines = VGroup(*[VGroup(pill(str(i + 1), FOCUS, size=SMALL), pill(w, WORD, size=LABEL),
                                text("   ".join(f"({l}) {o}" for l, o in zip("abcd", opts)), LABEL, INK))
                         .arrange(RIGHT, buff=0.35) for i, (w, opts, *_r) in enumerate(self.PRACTICE)])
        lines.arrange(DOWN, buff=0.5, aligned_edge=LEFT)
        board = self.card(VGroup(head, lines).arrange(DOWN, buff=0.5, aligned_edge=LEFT), color=FOCUS)
        fit_width(board, SAFE_W)
        board.move_to(UP * 0.4)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="practice_01",
            text="Your turn: choose the opposite. One: infamous. Famous, unknown, popular, or respected? Two: frugal. Poor, "
                 "extravagant, careful, or greedy? Three: partial, in judgement. Complete, whole, impartial, or partly?",
            voice="default",
            subtitle=True,
            pause_after=10.0,
        )
        self.play(FadeIn(board[0]), FadeIn(head))
        for ln, (spoken, first_option) in zip(lines, [("infamous", "Famous"), ("frugal", "Poor"),
                                                     ("partial", "Complete")]):
            self.at_word(n, spoken)
            self.play(FadeIn(ln[:2], shift=UP * 0.15), run_time=0.4)
            self.at_word(n, first_option)
            self.play(FadeIn(ln[2], shift=LEFT * 0.15), run_time=0.4)
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        self.clear_stage()
        self.scene_end("S14_practice")

    # =============================================== 15. ANSWERS ==========

    def answers(self):
        self.scene_start("S15_answers", title="Answers")

        rows = VGroup()
        for w, opts, key, traps, note in self.PRACTICE:
            OptionQuestion(w, opts, key, traps)            # validates key / traps
            rows.add(VGroup(pill(w, WORD, size=LABEL), text("↔", LABEL, MUTED),
                            pill(f"({key}) {opts['abcd'.index(key)]}", GOOD, size=LABEL),
                            text(note, SMALL, INK)).arrange(RIGHT, buff=0.3))
        rows.arrange(DOWN, buff=0.45, aligned_edge=LEFT)
        fit_width(rows, SAFE_W).move_to(UP * 0.7)
        extra = pill("complete, whole: oppose the “incomplete” meaning of partial", BAD, size=SMALL)
        fit_width(extra, SAFE_W)
        extra.next_to(rows, DOWN, buff=0.6)
        self.no_overlap(rows, extra)
        self.validator.check_in_frame(VGroup(rows, extra))

        n = self.narrate(
            id="answers_01",
            text="One: respected. Infamous means known for bad deeds. Two: extravagant. Frugal means careful with money; "
                 "its opposite is wasteful spending. Three: impartial. In judgement, partial means biased. Complete and "
                 "whole oppose the incomplete meaning.",
            voice="default",
            subtitle=True,
        )
        for r, (spoken, reason) in zip(rows, [("respected", "Infamous"), ("extravagant", "Frugal"),
                                             ("impartial", "judgement")]):
            self.at_word(n, spoken)
            self.play(FadeIn(r[:3], shift=RIGHT * 0.2), run_time=0.5)
            self.at_word(n, reason)
            self.play(FadeIn(r[3], shift=LEFT * 0.1), run_time=0.4)
        self.at_word(n, "Complete")
        self.play(FadeIn(extra, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S15_answers")

    # ================================================ 16. RECAP ==========

    def recap(self):
        self.scene_start("S16_recap", title="Recap Card")

        card, table = self.recap_card("Recap Card: Video 5", [
            ["Decode first", "don't just strip the prefix"],
            ["disinterested ↔", ", ".join(PAIRS["disinterested"][0])],
            ["infamous ↔", ", ".join(PAIRS["infamous"][0])],
            ["generous ↔", ", ".join(PAIRS["generous"][0]) + "  (not poor)"],
            ["Look-alikes", "always traps unless the meaning matches"],
        ])
        card.move_to(UP * 0.2)
        self.validator.check_in_frame(card)

        n = self.narrate(
            id="recap_01",
            text="To recap. Decode first: don't just strip the prefix. Disinterested is the opposite of biased or partial. "
                 "Infamous is the opposite of reputable or respected. Generous is the opposite of mean or stingy, not "
                 "poor. And look-alikes are always traps, unless the meaning matches.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(card[0]), FadeIn(table[0]))
        for row, spoken in zip(table[1:], ["Decode", "Disinterested", "Infamous", "Generous", "look-alikes"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.45)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S16_recap")

    # ================================================= 17. NEXT ==========

    def next_video(self):
        self.scene_start("S17_next", title="Next")

        shelves = VGroup(pill("plenty", GOOD, size=BODY), text("↔", TITLE, MUTED), pill("scarce", BAD, size=BODY))\
            .arrange(RIGHT, buff=0.5)
        tag = text("opposite shelves", LABEL, MUTED)
        nxt = pill("Next:  Exam-Oriented Antonyms", FOCUS, size=BODY)
        VGroup(shelves, tag, nxt).arrange(DOWN, buff=0.6).move_to(UP * 0.2)
        self.no_overlap(shelves, tag, nxt)
        self.validator.check_in_frame(VGroup(shelves, tag, nxt))

        n = self.narrate(
            id="next_01",
            text="Video six gives you the high-frequency antonym pairs exams keep using, organised as opposite shelves.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Video")
        self.play(FadeIn(nxt, scale=1.05))
        self.at_word(n, "shelves")
        self.play(FadeIn(shelves, shift=UP * 0.1), FadeIn(tag))
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S17_next")

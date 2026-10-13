"""
animation.py for the LMS video generator.

Course : C-CAT - Section A - English
Module : Module 1 - Vocabulary
Lesson : Lesson 2 - Antonyms
Video  : 04 - Prefixes and Word Formation (Video 4 of 7)

Source script:
  C:\\Users\\User\\Downloads\\C-CAT_SectionA_Module1_English\\English\\Module 1 - Vocabulary\\
  Lesson 2 - Antonyms\\04 - Prefixes and Word Formation.pdf

Built on the golden-reference pattern:
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``;
  * layouts stacked with next_to and guarded with ``no_overlap``; nothing is
    ever animated onto or into another box.

Opening: a later video of Lesson 2, so no spoken welcome. The module > lesson >
video trail is shown on screen (silent), then a one-line link to the
prerequisite page (the negative prefixes), the title and the objectives.

Pinned panel: the in- family rule (il- before l, im- before b / m / p, ir-
before r, in- elsewhere) stays in the top-right corner through the worked
examples and again in Hook, Solved; the row that applies lights up.

Every formed antonym is computed by ``in_prefix`` / ``negative`` and asserted
(illogical, impatient, irresponsible, irregular, immature, illegible,
incapable, and every example in the rules table). Every narration sentence has
its own visual cue.
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

IN_COL = {"il": "#4FC3F7", "im": "#FFB74D", "ir": "#CE93D8", "in": "#66BB6A"}


def in_prefix(word):
    """The shape the in- prefix takes before ``word``: il- before l, im- before b / m / p, ir- before r, else in-."""
    first = word[0].lower()
    if first == "l":
        return "il"
    if first in "bmp":
        return "im"
    if first == "r":
        return "ir"
    return "in"


def negative(word):
    return in_prefix(word) + word.lower()


def formed(word, size=BODY):
    """prefix chip + word chip → the formed antonym (prefix chosen by ``in_prefix``)."""
    pre = in_prefix(word)
    left = VGroup(pill(pre + "-", IN_COL[pre], size=size), pill(word.lower(), INK, size=size, fill_opacity=0.06))\
        .arrange(RIGHT, buff=0.12)
    result = text(negative(word), size, IN_COL[pre], BOLD)
    return VGroup(left, text("→", size, MUTED), result).arrange(RIGHT, buff=0.35)


FAMILY = [("il-", "before  l", "il"), ("im-", "before  b, m, p", "im"), ("ir-", "before  r", "ir"),
          ("in-", "elsewhere", "in")]
TRAPS = [("inflammable", "easily set on fire  (= flammable)"), ("invaluable", "extremely valuable"),
         ("infamous", "famous for something bad"), ("priceless", "extremely valuable")]


class PrefixesWordFormationVideo(LMSScene):
    lesson_title = "Prefixes and Word Formation"

    def construct(self):
        self.camera.background_color = BG

        self.lesson_intro()
        self.hook()
        self.concept_family()
        self.concept_others()
        self.concept_traps()
        self.why_you_need_it()
        self.analogy()
        self.examples_prefix()
        self.example_invaluable()
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

    def family_pin(self):
        """The in- family rule, kept in the corner while the examples use it."""
        return self.steps_pin("in- family", [(f"{p}  {when}", IN_COL[k]) for p, when, k in FAMILY])

    def family_step(self, word):
        """Animation: light the pinned row that applies to ``word``."""
        i = [k for _, _, k in FAMILY].index(in_prefix(word))
        return self.pin_step(i, color=IN_COL[in_prefix(word)])

    # ========================================= 0. LESSON INTRO ==========

    def lesson_intro(self):
        self.scene_start("S00_intro", title="Lesson Introduction")

        crumb = self.breadcrumb("English · Module 1 Vocabulary", "Lesson 2 · Antonyms", "Video 4")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        listed = VGroup(*[pill(p, c, size=BODY) for p, c in [("un-", WORD), ("in-", GOOD), ("dis-", SECOND),
                                                            ("non-", RATIO), ("mis-", BAD)]]).arrange(RIGHT, buff=0.4)
        which = pill("today: which prefix each word takes", GOOD, size=LABEL)
        lies = pill("…and the few words where a prefix misleads", BAD, size=LABEL)
        VGroup(listed, which, lies).arrange(DOWN, buff=0.55).move_to(DOWN * 0.1)
        self.no_overlap(crumb, listed, which, lies)
        self.validator.check_in_frame(VGroup(crumb, listed, which, lies))

        n = self.narrate(
            id="intro_01",
            text="The prerequisite page listed the negative prefixes. Today you learn which one each word takes, and the "
                 "few words where a prefix misleads.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.at_word(n, "prefixes")
        self.play(LaggedStart(*[FadeIn(p, shift=UP * 0.1) for p in listed], lag_ratio=0.15))
        self.at_word(n, "which")
        self.play(FadeIn(which, shift=UP * 0.1))
        self.at_word(n, "misleads")
        self.play(FadeIn(lies, shift=UP * 0.1))
        self.wait_for_narration(n)

        title = fitted_text("Prefixes and Word Formation", SAFE_W, 72, INK, BOLD)
        underline = Line(LEFT, RIGHT, color=GOOD, stroke_width=5).set_width(title.width * 0.6)
        VGroup(title, underline).arrange(DOWN, buff=0.2).move_to(UP * 0.2)
        goals = [("Choose the right negative prefix for a word", GOOD),
                 ("Spot the prefix traps: words that look negative but aren't", BAD)]
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
            text="This video is prefixes and word formation. By the end, you'll choose the right negative prefix for a "
                 "word, and spot the prefix traps: words that look negative but aren't.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(VGroup(listed, which, lies), shift=UP * 0.3))
        self.at_word(n, "prefixes")
        self.play(Write(title), run_time=1.1)
        self.play(GrowFromCenter(underline))
        self.at_word(n, "By")
        self.play(FadeOut(underline), ReplacementTransform(title, small_title), run_time=0.8)
        self.play(FadeIn(objectives[0]), FadeIn(heading))
        for row_, spoken in zip(rows, ["choose", "spot"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row_, shift=RIGHT * 0.2), run_time=0.5)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_intro")

    # ================================================= 1. HOOK ==========

    HOOK = dict(word="REGULAR", options=["unregular", "disregular", "inregular", "irregular"], key="d",
                traps={"a": "not an English word", "b": "not an English word", "c": "not an English word"})

    def validator_card(self, typed="unregular", ok=False):
        head = text("SPELLING TOOL", SMALL, RATIO, BOLD)
        field = VGroup(text("Enter the opposite of REGULAR:", LABEL, INK),
                       pill(typed, GOOD if ok else BAD, size=LABEL),
                       text("✓" if ok else "✗", BODY, GOOD if ok else BAD, BOLD)).arrange(RIGHT, buff=0.3)
        card = self.card(VGroup(head, field).arrange(DOWN, buff=0.2, aligned_edge=LEFT))
        cx, _ = self.free_area()
        return card.move_to(RIGHT * cx + UP * (CARD_TOP - card.height / 2))

    def hook(self):
        self.scene_start("S01_hook", title="Hook")

        assert negative("regular") == "irregular"
        form = self.validator_card()
        h = self.HOOK
        q = OptionQuestion(h["word"], h["options"], h["key"], h["traps"])
        opts = q.rows.copy().arrange(RIGHT, buff=0.7)
        fit_width(opts, SAFE_W)
        ask = pill("Which answer should the tool accept?", FOCUS, size=LABEL)
        note = pill("all four look like real prefixes; only one follows the rule", MUTED, size=SMALL)
        ask.next_to(form, DOWN, buff=0.5)
        opts.next_to(ask, DOWN, buff=0.5)
        note.next_to(opts, DOWN, buff=0.5)
        self.no_overlap(form, ask, opts, note)
        self.validator.check_in_frame(VGroup(form, ask, opts, note))

        n = self.narrate(
            id="hook_01",
            text="You're writing validation messages for a spelling tool. A user has to type the opposite of regular. "
                 "Which answer should the tool accept?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "spelling")
        self.play(FadeIn(form[0]), FadeIn(form[1][0]))
        self.at_word(n, "opposite")
        self.play(FadeIn(form[1][1], shift=RIGHT * 0.2))
        self.at_word(n, "Which")
        self.play(FadeIn(ask, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_02",
            text="Unregular, disregular, inregular, or irregular? All four look like real prefixes. Only one follows the "
                 "rule.",
            voice="default",
            subtitle=True,
            pause_after=3.0,
        )
        for row, spoken in zip(opts, ["Unregular", "disregular", "inregular", "irregular"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=UP * 0.15), run_time=0.35)
        self.at_word(n, "All")
        self.play(FadeIn(note, shift=UP * 0.1))
        self.at_word(n, "Only")
        self.play(Circumscribe(opts, color=FOCUS))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        self.clear_stage()
        self.scene_end("S01_hook")

    # ======================================= 2. CONCEPT: THE in- FAMILY ==========

    def concept_family(self):
        self.scene_start("S02_concept_family", title="The Concept - The in- Family")

        head = pill("many antonyms = negative prefix + word", WORD, size=LABEL)
        head.move_to(UP * (CARD_TOP - head.height / 2))
        how = VGroup(pill("some follow sound rules", GOOD, size=SMALL), pill("others you simply learn", MUTED, size=SMALL))\
            .arrange(RIGHT, buff=0.4).next_to(head, DOWN, buff=0.35)
        examples = {"il": ["legal", "logical"], "im": ["balance", "mature", "possible"], "ir": ["regular", "relevant"],
                    "in": ["complete", "accurate"]}
        for k, words in examples.items():
            assert all(in_prefix(w) == k for w in words), (k, words)
        rows = VGroup()
        for p, when, k in FAMILY:
            rows.add(VGroup(pill(p, IN_COL[k], size=BODY), text(when, LABEL, INK),
                            text(", ".join(negative(w) for w in examples[k]), LABEL, IN_COL[k])).arrange(RIGHT, buff=0.4))
        for r in rows:
            r[1].set_x(-2.6 + r[1].width / 2)
            r[2].set_x(0.6 + r[2].width / 2)
            r[0].set_x(-4.6)
        rows.arrange(DOWN, buff=0.32)
        for r in rows:
            r[0].set_x(-4.6)
            r[1].set_x(-3.4 + r[1].width / 2)
            r[2].set_x(0.2 + r[2].width / 2)
        board = self.card(rows, width=SAFE_W - 0.6)
        board.next_to(how, DOWN, buff=0.4)
        self.no_overlap(head, how, board)
        self.validator.check_in_frame(VGroup(head, how, board))

        n = self.narrate(
            id="family_01",
            text="Many antonyms are formed by adding a negative prefix. Some choices follow sound rules; others you simply "
                 "learn.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "prefix")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "sound")
        self.play(FadeIn(how[0], shift=UP * 0.1))
        self.at_word(n, "learn")
        self.play(FadeIn(how[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="family_02",
            text="The in family changes shape to match the next sound. I-L before L: illegal, illogical. I-M before B, M "
                 "and P: imbalance, immature, impossible. I-R before R: irregular, irrelevant. And I-N elsewhere: "
                 "incomplete, inaccurate.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "family")
        self.play(FadeIn(board[0]))
        for r, (rule_word, example_word) in zip(rows, [("I-L", "illegal"), ("I-M", "imbalance"), ("I-R", "irregular"),
                                                        ("I-N", "incomplete")]):
            self.at_word(n, rule_word)
            self.play(FadeIn(r[:2], shift=RIGHT * 0.2), run_time=0.4)
            self.at_word(n, example_word)
            self.play(FadeIn(r[2], shift=LEFT * 0.1), run_time=0.4)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_concept_family")

    # ================================= 3. CONCEPT: un-, dis-, non-, mis- ==========

    def concept_others(self):
        self.scene_start("S03_concept_others", title="The Concept - un-, dis-, non-, mis-")

        data = [("un-", WORD, "most common, native English words", "unfair, unhappy"),
                ("dis-", SECOND, "verbs, some nouns and adjectives", "disagree, dishonest"),
                ("non-", RATIO, "“not a member of”", "non-member, non-violent"),
                ("mis-", BAD, "“wrongly”, NOT “opposite”", "misunderstand = wrong understanding")]
        table = self.table_rows(["prefix", "used with / meaning", "examples"], [[p, m, e] for p, _, m, e in data],
                                [1.8, 5.0, 5.0], size=LABEL)
        for row, (_, c, _, _) in zip(table[1:], data):
            row[0].set_color(c)
        board = self.card(table, width=SAFE_W - 0.2).move_to(UP * 0.3)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="others_01",
            text="Un is the most common prefix for native English words: unfair, unhappy. Dis often goes with verbs, and "
                 "some nouns and adjectives: disagree, dishonest.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(board[0]), FadeIn(table[0]))
        self.at_word(n, "Un")
        self.play(FadeIn(table[1], shift=RIGHT * 0.2))
        self.at_word(n, "Dis")
        self.play(FadeIn(table[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="others_02",
            text="Non means not a member of: non-member, non-violent. Mis means wrongly, not opposite. Misunderstand is "
                 "wrong understanding, not the opposite of understanding.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Non")
        self.play(FadeIn(table[3], shift=RIGHT * 0.2))
        self.at_word(n, "Mis")
        self.play(FadeIn(table[4][:2], shift=RIGHT * 0.2))
        self.at_word(n, "Misunderstand")
        self.play(FadeIn(table[4][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_concept_others")

    # ========================================= 4. CONCEPT: THE TRAPS ==========

    def concept_traps(self):
        self.scene_start("S04_concept_traps", title="The Concept - Look-Negative Traps")

        head = pill("traps: words that LOOK negative but aren't", BAD, size=LABEL)
        head.move_to(UP * (CARD_TOP - head.height / 2))
        table = self.table_rows(["word", "really means"], [[w, m] for w, m in TRAPS], [3.6, 7.0], size=LABEL)
        for row in table[1:]:
            row[0].set_color(BAD)
            row[1].set_color(GOOD)
        board = self.card(table, width=SAFE_W - 1.0)
        board.next_to(head, DOWN, buff=0.45)
        self.no_overlap(head, board)
        self.validator.check_in_frame(VGroup(head, board))

        n = self.narrate(
            id="traps_01",
            text="Then the traps. Some words look negative but aren't. Inflammable means easily set on fire, the same as "
                 "flammable. Invaluable means extremely valuable, not worthless.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "traps")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "look")
        self.play(FadeIn(board[0]), FadeIn(table[0]))
        self.at_word(n, "Inflammable")
        self.play(FadeIn(table[1], shift=RIGHT * 0.2))
        self.at_word(n, "Invaluable")
        self.play(FadeIn(table[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_02",
            text="Infamous means famous for something bad. And priceless means extremely valuable.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Infamous")
        self.play(FadeIn(table[3], shift=RIGHT * 0.2))
        self.at_word(n, "priceless")
        self.play(FadeIn(table[4], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_concept_traps")

    # ======================================== 5. WHY YOU NEED IT ==========

    def why_you_need_it(self):
        self.scene_start("S05_why", title="Why You Need It")

        exam = VGroup(pill("antonym questions", BAD, size=LABEL), pill("spelling-based error questions", SECOND,
                                                                       size=LABEL)).arrange(RIGHT, buff=0.5)
        label = VGroup(text("⚠", TITLE, RATIO), pill("INFLAMMABLE", BAD, size=BODY),
                       text("= catches fire easily", LABEL, INK)).arrange(RIGHT, buff=0.3)
        real = pill("a misreading has real consequences", RATIO, size=LABEL)
        VGroup(exam, label, real).arrange(DOWN, buff=0.7).move_to(UP * 0.2)
        self.no_overlap(exam, label, real)
        self.validator.check_in_frame(VGroup(exam, label, real))

        n = self.narrate(
            id="why_01",
            text="Prefix options appear constantly in antonym questions, and in spelling-based error questions. The trap "
                 "words appear in safety labels and business writing, where a misreading has real consequences.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "antonym")
        self.play(FadeIn(exam[0], shift=UP * 0.1))
        self.at_word(n, "spelling-based")
        self.play(FadeIn(exam[1], shift=UP * 0.1))
        self.at_word(n, "safety")
        self.play(FadeIn(label, shift=UP * 0.1))
        self.at_word(n, "consequences")
        self.play(FadeIn(real, scale=1.05))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_why")

    # ============================================== 6. ANALOGY ==========

    def analogy(self):
        self.scene_start("S06_analogy", title="The Analogy")

        adapter = pill("in-  adapter", GOOD, size=BODY).move_to(LEFT * 4.4)
        heads = VGroup(*[pill(p, IN_COL[k], size=BODY) for p, _, k in FAMILY]).arrange(DOWN, buff=0.45)
        heads.move_to(LEFT * 1.2)
        sockets = VGroup(*[pill(s_, INK, size=LABEL, fill_opacity=0.06) for s_ in
                           ["l…  (legal)", "b… m… p…  (possible)", "r…  (regular)", "anything else  (complete)"]])
        for s_, h_ in zip(sockets, heads):
            s_.next_to(h_, RIGHT, buff=1.6)
        wires = VGroup(*[Line(adapter.get_right(), h_.get_left(), color=MUTED, stroke_width=2) for h_ in heads])
        fits = VGroup(*[Arrow(h_.get_right(), s_.get_left(), buff=0.12, color=IN_COL[k], stroke_width=3)
                        for h_, s_, (_, _, k) in zip(heads, sockets, FAMILY)])
        wrong = Arrow(heads[0].get_right() + DOWN * 0.1, sockets[2].get_left() + UP * 0.1, buff=0.12, color=BAD,
                      stroke_width=3)
        wrong_tag = text("wrong head: doesn't fit", SMALL, BAD).next_to(sockets[3], DOWN, buff=0.35)
        self.no_overlap(adapter, heads, sockets)
        self.validator.check_in_frame(VGroup(adapter, heads, sockets, wrong_tag))

        n = self.narrate(
            id="analogy_01",
            text="The in prefix is one adapter with four heads. The head you use depends on the socket: the first letter "
                 "of the word.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "adapter")
        self.play(FadeIn(adapter, scale=1.1))
        self.at_word(n, "four")
        self.play(Create(wires), LaggedStart(*[FadeIn(h_, shift=RIGHT * 0.1) for h_ in heads], lag_ratio=0.2))
        self.at_word(n, "socket")
        self.play(LaggedStart(*[FadeIn(s_, shift=LEFT * 0.1) for s_ in sockets], lag_ratio=0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_02",
            text="L takes I-L. B, M and P take I-M. R takes I-R. Use the wrong head, and it doesn't fit.",
            voice="default",
            subtitle=True,
        )
        for arrow, spoken in zip(fits[:3], ["L", "B", "R"]):
            self.at_word(n, spoken)
            self.play(GrowArrow(arrow), run_time=0.4)
        self.at_word(n, "wrong")
        self.play(GrowArrow(wrong), FadeIn(wrong_tag))
        self.play(FadeOut(wrong), GrowArrow(fits[3]), run_time=0.5)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_analogy")

    # ==================================== 7. WORKED EXAMPLES 1-3 ==========

    def examples_prefix(self):
        self.scene_start("S07_examples", title="Worked Examples 1-3")
        self.play(self.pin(self.family_pin()))

        words = ["LOGICAL", "PATIENT", "RESPONSIBLE"]
        assert [negative(w) for w in words] == ["illogical", "impatient", "irresponsible"]
        lines = VGroup(*[formed(w) for w in words]).arrange(DOWN, buff=0.7, aligned_edge=LEFT)
        self.place_free(lines, y=0.0)
        self.validator.check_in_frame(lines)

        n = self.narrate(
            id="ex123_01",
            text="Logical starts with L, and L takes I-L: illogical. Patient starts with P, and P takes I-M: impatient. "
                 "Responsible starts with R, and R takes I-R: irresponsible.",
            voice="default",
            subtitle=True,
        )
        for ln, w, (first, result) in zip(lines, words, [("Logical", "illogical"), ("Patient", "impatient"),
                                                        ("Responsible", "irresponsible")]):
            self.at_word(n, first)
            self.play(FadeIn(ln[0][1], shift=UP * 0.1), run_time=0.4)
            self.play(FadeIn(ln[0][0], shift=RIGHT * 0.1), self.family_step(w), run_time=0.5)
            self.at_word(n, result)
            self.play(FadeIn(ln[1:], shift=LEFT * 0.1), run_time=0.4)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S07_examples")

    # ================================ 8. WORKED EXAMPLE 4: INVALUABLE ==========

    def example_invaluable(self):
        self.scene_start("S08_ex_invaluable", title="Worked Example 4")

        q = OptionQuestion("INVALUABLE", ["valuable", "worthless", "priceless", "precious"], "b",
                           {"a": "synonym", "c": "synonym", "d": "synonym"})
        q.group.to_edge(LEFT, buff=SAFE + 0.6).set_y(0.2)
        real = pill("really means: very valuable", GOOD, size=SMALL).next_to(q.word, DOWN, buff=0.15)
        q.rows.next_to(real, DOWN, buff=0.35, aligned_edge=LEFT)
        trap = pill("look-negative trap: “in-” is NOT “not” here", BAD, size=SMALL)
        self.place_free(trap, y=-2.9)
        self.no_overlap(q.word, real, q.rows, trap)
        self.no_overlap(VGroup(q.word, real, q.rows), self.pinned)
        self.validator.check_in_frame(VGroup(q.word, real, q.rows, trap))

        n = self.narrate(
            id="ex4_01",
            text="Invaluable: which is the antonym? Valuable, worthless, priceless, or precious? Invaluable means very "
                 "valuable. So its opposite is worthless.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(q.word, scale=1.1))
        self.at_word(n, "Valuable", occurrence=1)
        self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.2) for r in q.rows], lag_ratio=0.2))
        self.at_word(n, "means")
        self.play(FadeIn(real, shift=UP * 0.1), FadeIn(trap, shift=UP * 0.1))
        self.at_word(n, "opposite")
        self.play(*q.strike("a")[1], *q.strike("c")[1], *q.strike("d")[1])
        self.play(*q.confirm()[1])
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S08_ex_invaluable")

    # ================================================ 9. RULES ==========

    def rules(self):
        self.scene_start("S09_rules", title="Rules")
        self.play(self.unpin())

        data = [("il- before l", "illegal, illiterate, illegible", IN_COL["il"]),
                ("im- before b, m, p", "imbalance, immoral, impossible", IN_COL["im"]),
                ("ir- before r", "irregular, irrational, irreversible", IN_COL["ir"]),
                ("in- elsewhere", "inaccurate, inconsistent, inefficient", IN_COL["in"]),
                ("un- (common, native words)", "unfair, unaware, unusual", WORD),
                ("dis- (verbs, some adjectives)", "disagree, dishonest, dislike", SECOND),
                ("mis- = wrongly", "misuse, mislead  (not an opposite)", BAD),
                ("look-negative traps", "inflammable = flammable; invaluable = priceless; infamous = notorious", FOCUS)]
        for rule, ex, _ in data[:4]:
            pre = rule[:2]
            assert all(w.startswith(pre) and in_prefix(w[2:]) == pre for w in ex.split(", ")), rule
        table = self.table_rows(["Rule", "Examples"], [[r, e] for r, e, _ in data], [4.6, 7.2], size=SMALL)
        for row, (_, _, c) in zip(table[1:], data):
            row[0].set_color(c)
        board = self.card(table, width=SAFE_W - 0.2)
        fit_height(board, SAFE_H - 1.0)
        board.move_to(UP * (CARD_TOP - board.height / 2))
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="rules_01",
            text="Here are the rules in one table. I-L before L. I-M before B, M and P. I-R before R. And I-N elsewhere.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(board[0]), FadeIn(table[0]))
        for row, spoken in zip(table[1:5], ["I-L", "I-M", "I-R", "I-N"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.4)
        self.wait_for_narration(n)

        n = self.narrate(
            id="rules_02",
            text="Un goes with common, native words. Dis goes with verbs and some adjectives. Mis means wrongly, so it's "
                 "not an opposite. And remember the look-negative traps: inflammable, invaluable and infamous.",
            voice="default",
            subtitle=True,
        )
        for row, spoken in zip(table[5:], ["Un", "Dis", "Mis", "look-negative"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.4)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S09_rules")

    # ============================================= 10. PROCESS ==========

    def process(self):
        self.scene_start("S10_process", title="The Process")

        steps = VGroup(*[VGroup(pill(str(i + 1), c, size=SMALL), fitted_text(s_, SAFE_W - 2.2, BODY, INK))
                         .arrange(RIGHT, buff=0.3) for i, (s_, c) in enumerate([
                             ("Check the first letter: the in- / il- / im- / ir- rule", GOOD),
                             ("Not an in- word?  Try un- or dis-, and check it's a real word", WORD),
                             ("Watch for look-negative traps before you “remove” a prefix", BAD),
                             ("Confirm: a real word with the opposite meaning", SECOND)])])
        steps.arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        board = self.card(steps).move_to(UP * 0.3)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="process_01",
            text="The process. First, check the first letter of the word for the in family rule. Second, if it's not an in "
                 "word, try un or dis, and check that it's a real word. Third, watch for look-negative traps before you "
                 "remove a prefix. And fourth, confirm the answer is a real word with the opposite meaning.",
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
        self.play(self.pin(self.family_pin()))

        h = self.HOOK
        form = self.validator_card()
        q = OptionQuestion(h["word"], h["options"], h["key"], h["traps"], word_size=BODY)
        q.group.next_to(form, DOWN, buff=0.45).to_edge(LEFT, buff=SAFE + 0.6)
        predict = pill("starts with r  →  ir-", STEP_COLS["PREDICT"], size=SMALL).next_to(q.word, RIGHT, buff=0.4)
        fixed = self.validator_card("irregular", ok=True)
        self.no_overlap(form, q.group)
        self.no_overlap(form, self.pinned)
        self.no_overlap(q.group, predict, self.pinned)
        self.validator.check_in_frame(VGroup(form, q.group, predict))

        n = self.narrate(
            id="solved_01",
            text="Let's solve the hook. Read: the opposite of regular, formed with a prefix. Predict: it starts with R, so "
                 "I-R: irregular.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(form), FadeIn(q.rows))
        self.at_word(n, "Read")
        self.play(FadeIn(q.word, scale=1.1))
        self.at_word(n, "Predict")
        self.play(FadeIn(predict, shift=LEFT * 0.1), self.family_step("regular"))
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_02",
            text="Eliminate. Unregular, disregular and inregular are not English words.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Eliminate")
        self.play(Indicate(q.rows, color=BAD, scale_factor=1.02))
        self.at_word(n, "Unregular")
        self.play(*q.strike("a")[1], *q.strike("b")[1], *q.strike("c")[1])
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_03",
            text="Confirm: irregular. That's the R takes I-R rule.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Confirm")
        self.play(*q.confirm()[1], ReplacementTransform(form, fixed))
        self.at_word(n, "rule")
        self.play(self.family_step("regular"))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S11_hook_solved")

    # ========================================== 12. EXAM PATTERNS ==========

    def exam_patterns(self):
        self.scene_start("S12_patterns", title="Exam Patterns and Solving Models")
        self.play(self.unpin())

        table = self.table_rows(["Pattern", "Solving model"], [
            ["Prefix options for one word", "apply the letter rule, then check the word is real"],
            ["Look-negative word as the question", "decode the true meaning first (invaluable = very valuable)"],
            ["mis- option", "it means “wrongly”: usually not the opposite"],
        ], [4.8, 7.0], size=LABEL)
        board = self.card(table, width=SAFE_W - 0.2).move_to(UP * 0.4)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="patterns_01",
            text="Three exam patterns. Prefix options for one word: apply the letter rule, then check the word is real. A "
                 "look-negative word as the question: decode the true meaning first. And a mis option: it means "
                 "wrongly, and is usually not the opposite.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(board[0]), FadeIn(table[0]))
        for row, spoken in zip(table[1:], ["Prefix", "look-negative", "mis"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.45)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S12_patterns")

    # ======================================== 13. COMMON MISTAKES ==========

    def common_mistakes(self):
        self.scene_start("S13_mistakes", title="Common Mistakes")

        assert negative("capable") == "incapable"
        card_w = ZONE_W - 0.3
        pairs = [
            (self.verdict_card(False, "inflammable = “not flammable”", card_w),
             self.verdict_card(True, "inflammable = flammable", card_w)),
            (self.verdict_card(False, "un- where in- is required: uncapable", card_w),
             self.verdict_card(True, "incapable", card_w)),
            (self.verdict_card(False, "mis- treated as “opposite”", card_w),
             self.verdict_card(True, "misunderstand = understand wrongly", card_w)),
        ]
        for (wrong, right), yy in zip(pairs, [1.6, 0.05, -1.5]):
            wrong.move_to(LEFT_ZONE + UP * yy)
            right.move_to(RIGHT_ZONE + UP * yy)
        header = pill("3 mistakes", BAD, size=LABEL).move_to(UP * (CARD_TOP - 0.3))
        self.validator.check_in_frame(VGroup(header, *[c for p in pairs for c in p]))

        n = self.narrate(
            id="mistakes_01",
            text="Three common mistakes. The first is treating inflammable as not flammable. The second is using un where "
                 "in is required: uncapable, for incapable. The third is treating mis as opposite: misunderstand is not "
                 "the opposite of understand.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(header))
        for pr, (spoken, fix) in zip(pairs, [("first", "flammable"), ("second", "incapable"), ("third", "misunderstand")]):
            self.at_word(n, spoken)
            self.play(FadeIn(pr[0], shift=RIGHT * 0.3), run_time=0.4)
            self.at_word(n, fix)
            self.play(FadeIn(pr[1], shift=LEFT * 0.3), run_time=0.4)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S13_mistakes")

    # ============================================== 14. PRACTICE ==========

    PRACTICE = [
        ("The opposite of MATURE", ["unmature", "dismature", "immature", "inmature"], "c",
         {"a": "not a word", "b": "not a word", "d": "not a word"}, "m takes im-"),
        ("The antonym of INFLAMMABLE", ["non-flammable", "flammable", "burning", "explosive"], "a",
         {"b": "synonym: the trap", "c": "related", "d": "related"}, "inflammable = flammable"),
        ("The opposite of LEGIBLE", ["unlegible", "illegible", "inlegible", "dislegible"], "b",
         {"a": "not a word", "c": "not a word", "d": "not a word"}, "l takes il-"),
    ]

    def practice(self):
        self.scene_start("S14_practice", title="Practice Questions")

        assert negative("mature") == "immature" and negative("legible") == "illegible"
        lines = VGroup()
        for i, (prompt, opts, *_r) in enumerate(self.PRACTICE):
            lines.add(VGroup(VGroup(pill(str(i + 1), FOCUS, size=SMALL), text(prompt, LABEL, INK, BOLD))
                             .arrange(RIGHT, buff=0.3),
                             text("   ".join(f"({l}) {o}" for l, o in zip("abcd", opts)), LABEL, MUTED))
                      .arrange(DOWN, buff=0.12, aligned_edge=LEFT))
        lines.arrange(DOWN, buff=0.4, aligned_edge=LEFT)
        board = self.card(lines, width=SAFE_W - 0.2, color=FOCUS).move_to(UP * 0.4)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="practice_01",
            text="Your turn. One: the opposite of mature. Unmature, dismature, immature, or inmature? Two: the antonym of "
                 "inflammable. Non-flammable, flammable, burning, or explosive? Three: the opposite of legible. Unlegible, "
                 "illegible, inlegible, or dislegible?",
            voice="default",
            subtitle=True,
            pause_after=10.0,
        )
        self.play(FadeIn(board[0]))
        for ln, (spoken, first_option) in zip(lines, [("One", "Unmature"), ("Two", "Non-flammable"),
                                                     ("Three", "Unlegible")]):
            self.at_word(n, spoken)
            self.play(FadeIn(ln[0], shift=UP * 0.15), run_time=0.4)
            self.at_word(n, first_option)
            self.play(FadeIn(ln[1], shift=LEFT * 0.15), run_time=0.4)
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        self.clear_stage()
        self.scene_end("S14_practice")

    # =============================================== 15. ANSWERS ==========

    def answers(self):
        self.scene_start("S15_answers", title="Answers")

        rows = VGroup()
        for prompt, opts, key, traps, why in self.PRACTICE:
            OptionQuestion(prompt, opts, key, traps)       # validates key / traps
            rows.add(VGroup(text(prompt, LABEL, INK), text("→", LABEL, MUTED),
                            pill(f"({key}) {opts['abcd'.index(key)]}", GOOD, size=LABEL),
                            pill(why, FOCUS, size=SMALL)).arrange(RIGHT, buff=0.3))
        rows.arrange(DOWN, buff=0.5, aligned_edge=LEFT)
        fit_width(rows, SAFE_W).move_to(UP * 0.3)
        self.validator.check_in_frame(rows)

        n = self.narrate(
            id="answers_01",
            text="One: immature. M takes I-M. Two: non-flammable. Inflammable means flammable, so its opposite is "
                 "non-flammable. Three: illegible. L takes I-L.",
            voice="default",
            subtitle=True,
        )
        for r, (spoken, reason) in zip(rows, [("immature", "M"), ("non-flammable", "Inflammable"),
                                             ("illegible", "L")]):
            self.at_word(n, spoken)
            self.play(FadeIn(r[:3], shift=RIGHT * 0.2), run_time=0.5)
            self.at_word(n, reason)
            self.play(FadeIn(r[3], shift=LEFT * 0.1), run_time=0.4)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S15_answers")

    # ================================================ 16. RECAP ==========

    def recap(self):
        self.scene_start("S16_recap", title="Recap Card")

        card, table = self.recap_card("Recap Card: Video 4", [
            ["in- family", "il- (l), im- (b, m, p), ir- (r), in- (elsewhere)"],
            ["un- / dis- / non-", "common native words / verbs / “not a member of”"],
            ["mis-", "means “wrongly”: not an opposite"],
            ["Look-negative", "inflammable = flammable; invaluable = very valuable; infamous = known for bad things"],
        ])
        card.move_to(UP * 0.2)
        self.validator.check_in_frame(card)

        n = self.narrate(
            id="recap_01",
            text="To recap. The in family: I-L before L, I-M before B, M and P, I-R before R, and I-N elsewhere. Un is for "
                 "common native words, dis for verbs, and non for not a member of. Mis means wrongly; it's not an "
                 "opposite. And the look-negative words: inflammable is flammable, invaluable is very valuable, and "
                 "infamous is known for bad things.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(card[0]), FadeIn(table[0]))
        for row, spoken in zip(table[1:], ["family", "Un", "Mis", "look-negative"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.45)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S16_recap")

    # ================================================= 17. NEXT ==========

    def next_video(self):
        self.scene_start("S17_next", title="Next")

        kinds = VGroup(pill("near-opposites", RATIO, size=LABEL), pill("false opposites", BAD, size=LABEL),
                       pill("look-alikes", SECOND, size=LABEL)).arrange(RIGHT, buff=0.5)
        nxt = pill("Next:  Commonly Confused Antonyms", FOCUS, size=BODY)
        VGroup(kinds, nxt).arrange(DOWN, buff=0.9).move_to(UP * 0.2)
        self.no_overlap(kinds, nxt)
        self.validator.check_in_frame(VGroup(kinds, nxt))

        n = self.narrate(
            id="next_01",
            text="Video five collects the other antonym pairs people get wrong: near-opposites, false opposites and "
                 "look-alikes.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Video")
        self.play(FadeIn(nxt, scale=1.05))
        for k, spoken in zip(kinds, ["near-opposites", "false", "look-alikes"]):
            self.at_word(n, spoken)
            self.play(FadeIn(k, shift=UP * 0.1), run_time=0.4)
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S17_next")

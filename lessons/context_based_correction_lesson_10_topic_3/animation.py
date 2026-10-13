"""
animation.py for the LMS video generator.

Course : C-CAT - Section A - English
Module : Module 2 - Grammar
Lesson : Lesson 10 - Sentence Correction
Video  : 03 - Context-Based Correction (Register and Clarity) (Video 3 of 6)

Source script:
  C:\\Scripts\\03 - Context-Based Correction (Register and Clarity).pdf

Built on the golden-reference pattern:
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``;
  * layouts stacked with next_to and guarded with ``no_overlap``; nothing is
    ever animated onto or into another box.

The three tests live in TESTS (register, clarity, concision) and the four email versions in HOOK_VERSIONS, each with the reason it fails (None for the one to send); Hook and Hook, Solved are built from it.
The "all options grammatical?" card (register, clarity, concision, in that order) stays pinned top-right through the worked examples and Hook, Solved; the test in use lights up.
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

TESTS = [("REGISTER", "neutral to formal: no slang, abbreviations or clichés", WORD),
         ("CLARITY", "one clear meaning; only / just / even next to what they limit", RATIO),
         ("CONCISION", "a shorter way that says the same thing", GOOD)]
TEST_COL = {name: c for name, _, c in TESTS}

# Hook: (version, why it fails, or None for the one to send).
HOOK_VERSIONS = [
    ("Hey, we want to close this quickly, so send the files.", "keeps “Hey”; sounds abrupt"),
    ("We would like to close this soon, so please send the files at your earliest convenience.", None),
    ("We wanna close this at the earliest, pls send files.", "keeps “wanna” and “pls”"),
    ("Kindly do the needful and send the files ASAP.", "“do the needful”: a non-standard cliché;  “ASAP”: informal"),
]
assert [why for _v, why in HOOK_VERSIONS].count(None) == 1


class ContextBasedCorrectionVideo(LMSScene):
    lesson_title = "Context-Based Correction (Register and Clarity)"

    def construct(self):
        self.camera.background_color = BG

        self.lesson_intro()
        self.hook()
        self.concept()
        self.why_you_need_it()
        self.analogy()
        self.example_wordy()
        self.example_only()
        self.example_ambiguous()
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

    def order_pin(self):
        return self.steps_pin("all options grammatical?", [("REGISTER: neutral to formal", WORD),
                                                           ("CLARITY: one clear meaning", RATIO),
                                                           ("CONCISION: the shorter one", GOOD)])

    def light_test(self, name):
        return self.pin_step([t for t, _, _ in TESTS].index(name), color=TEST_COL[name])

    def email_card(self):
        head = text("DRAFT EMAIL  ·  to a client", SMALL, RATIO, BOLD)
        cx, w = self.free_area()
        line = fitted_text("“Hey, we wanna close this ASAP, so pls send the files.”", min(w - 1.4, SAFE_W - 1.8), LABEL,
                           INK, NORMAL, max_lines=2, t2c={"Hey": BAD, "wanna": BAD, "ASAP": BAD, "pls": BAD})
        card = self.card(VGroup(head, line).arrange(DOWN, buff=0.2, aligned_edge=LEFT), width=min(w - 0.2, SAFE_W - 0.4))
        return card.move_to(RIGHT * cx + UP * (CARD_TOP - card.height / 2))

    def version_rows(self, width, size=LABEL):
        """(a)-(d) versions of the email, each with its verdict underneath."""
        rows = VGroup()
        for letter, (version, why) in zip("abcd", HOOK_VERSIONS):
            line = VGroup(text(f"({letter})", size, MUTED),
                          fitted_text(version, width - 1.0, size, INK, NORMAL, max_lines=2))\
                .arrange(RIGHT, buff=0.25, aligned_edge=UP)
            note = text(why or "formal, clear and complete", SMALL, BAD if why else GOOD)
            fit_width(note, width - 1.0)
            rows.add(VGroup(line, note).arrange(DOWN, buff=0.1, aligned_edge=LEFT))
        return rows.arrange(DOWN, buff=0.28, aligned_edge=LEFT)

    def clarity_example(self, before, bold, why, test, kind, after, good):
        """Sentence, what's wrong, the test it fails (lit on the pin), and the corrected sentence."""
        cx, w = self.free_area()
        first = fitted_text(f"“{before}”", w - 0.8, LABEL, INK, NORMAL, max_lines=2, t2c={bold: WORD})
        note = text(why, LABEL, MUTED)
        fit_width(note, w - 0.8)
        tag = VGroup(pill(test, TEST_COL[test], size=SMALL), text(kind, LABEL, TEST_COL[test], BOLD))\
            .arrange(RIGHT, buff=0.25)
        fixed = fitted_text(f"“{after}”", w - 0.8, LABEL, INK, NORMAL, max_lines=2, t2c={good: GOOD})
        block = VGroup(first, note, tag, fixed).arrange(DOWN, buff=0.5, aligned_edge=LEFT)
        fit_within(block, w - 0.6, SAFE_H - 1.6)
        self.place_free(block, y=0.1)
        self.no_overlap(first, note, tag, fixed)
        self.validator.check_in_frame(block)
        return first, note, tag, fixed

    # ========================================= 0. LESSON INTRO ==========

    def lesson_intro(self):
        self.scene_start("S00_intro", title="Lesson Introduction")

        crumb = self.breadcrumb("English · Module 2 Grammar", "Lesson 10 · Sentence Correction", "Video 3")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        fixed = pill("Videos 1 and 2: grammar and structure", MUTED, size=LABEL)
        setting = pill("grammatical, and still wrong for its setting", BAD, size=LABEL)
        more = VGroup(text("two more tests:", LABEL, MUTED), pill("REGISTER", WORD, size=BODY),
                      pill("CLARITY", RATIO, size=BODY)).arrange(RIGHT, buff=0.4)
        VGroup(fixed, setting, more).arrange(DOWN, buff=0.6).move_to(DOWN * 0.1)
        self.no_overlap(crumb, fixed, setting, more)
        self.validator.check_in_frame(VGroup(crumb, fixed, setting, more))

        n = self.narrate(
            id="intro_01",
            text="Videos one and two fixed grammar and structure. But a sentence can be grammatical, and still wrong for its "
                 "setting. Today adds two more tests: register and clarity.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.at_word(n, "grammar")
        self.play(FadeIn(fixed, shift=UP * 0.1))
        self.at_word(n, "setting")
        self.play(FadeIn(setting, shift=UP * 0.1))
        self.at_word(n, "register")
        self.play(FadeIn(more[:2], shift=UP * 0.1))
        self.at_word(n, "clarity")
        self.play(FadeIn(more[2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        title = fitted_text("Context-Based Correction", SAFE_W, 72, INK, BOLD)
        sub = text("register and clarity", LABEL, MUTED)
        underline = Line(LEFT, RIGHT, color=WORD, stroke_width=5).set_width(title.width * 0.6)
        VGroup(title, underline, sub).arrange(DOWN, buff=0.2).move_to(UP * 0.2)
        goals = [("Correct sentences for register (formality) and clarity", WORD),
                 ("Choose between grammatically correct options by fit and concision", GOOD)]
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
            text="This video is context-based correction: register and clarity. By the end, you'll correct sentences for "
                 "register, which means formality, and for clarity, and choose between grammatically correct options by "
                 "fit and concision.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(VGroup(fixed, setting, more), shift=UP * 0.3))
        self.at_word(n, "context-based")
        self.play(Write(title), run_time=1.1)
        self.play(GrowFromCenter(underline), FadeIn(sub))
        self.at_word(n, "By")
        self.play(FadeOut(underline), FadeOut(sub), ReplacementTransform(title, small_title), run_time=0.8)
        self.play(FadeIn(objectives[0]), FadeIn(heading))
        for row_, spoken in zip(rows, ["correct", "choose"]):
            self.at_word(n, spoken, occurrence=1)
            self.play(FadeIn(row_, shift=RIGHT * 0.2), run_time=0.5)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_intro")

    # ================================================= 1. HOOK ==========

    def hook(self):
        self.scene_start("S01_hook", title="Hook")

        email = self.email_card()
        ask = pill("which version should actually go to the client?", FOCUS, size=LABEL)
        versions = VGroup(*[r[0] for r in self.version_rows(SAFE_W - 0.6)]).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        body = VGroup(ask, versions).arrange(DOWN, buff=0.4)
        fit_within(body, SAFE_W, email.get_bottom()[1] - 0.4 - (BOTTOM_Y + 0.5))
        body.next_to(email, DOWN, buff=0.4)
        self.no_overlap(email, ask, versions)
        self.validator.check_in_frame(VGroup(email, body))

        n = self.narrate(
            id="hook_01",
            text="A junior colleague's email to a client reads: hey, we wanna close this ASAP, so please send the files, "
                 "with please typed as P L S. Which version should actually go to the client?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "email")
        self.play(FadeIn(email, shift=DOWN * 0.2))
        self.at_word(n, "Which")
        self.play(FadeIn(ask, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_02",
            text="Version A: hey, we want to close this quickly, so send the files. Version B: we would like to close this "
                 "soon, so please send the files at your earliest convenience. Version C: we wanna close this at the "
                 "earliest, please send files. Version D: kindly do the needful, and send the files ASAP.",
            voice="default",
            subtitle=True,
            pause_after=3.0,
        )
        for v, spoken in zip(versions, ["A", "B", "C", "D"]):
            self.at_word(n, spoken, occurrence=1)
            self.play(FadeIn(v, shift=UP * 0.15), run_time=0.4)
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        self.clear_stage()
        self.scene_end("S01_hook")

    # ============================================== 2. CONCEPT ==========

    def concept(self):
        self.scene_start("S02_concept", title="The Concept")

        head = pill("REGISTER:  how formal a sentence is", WORD, size=LABEL)
        head.move_to(UP * (CARD_TOP - head.height / 2))
        expect = text("exams and professional writing expect neutral-to-formal", SMALL, MUTED)
        expect.next_to(head, DOWN, buff=0.2)
        bans = VGroup(*[VGroup(pill("✗  " + kind, BAD, size=LABEL), text(ex, LABEL, INK)).arrange(RIGHT, buff=0.35)
                        for kind, ex in [("slang", "wanna, gonna, gotta"), ("chat abbreviations", "pls, u, thx"),
                                         ("casual openers", "“Hey” in formal communication"),
                                         ("stiff clichés", "“do the needful”, “revert back”")]])
        bans.arrange(DOWN, buff=0.32, aligned_edge=LEFT)
        unclear = text("clichés are marked down too: unclear, or regionally non-standard", SMALL, RATIO)
        body = VGroup(bans, unclear).arrange(DOWN, buff=0.4, aligned_edge=LEFT)
        fit_within(body, SAFE_W, SAFE_H - head.height - 2.2)
        body.next_to(expect, DOWN, buff=0.45)
        self.no_overlap(head, expect, bans, unclear)
        self.validator.check_in_frame(VGroup(head, expect, body))

        n = self.narrate(
            id="concept_01",
            text="Register is how formal a sentence is. Exams and professional writing expect a neutral-to-formal register: "
                 "no slang, like wanna, gonna, gotta; no chat abbreviations, like P L S or T H X; and no overly casual "
                 "openers, like hey, in formal communication.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Register")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "expect")
        self.play(FadeIn(expect, shift=UP * 0.1))
        for b, spoken in zip(bans[:3], ["slang", "abbreviations", "openers"]):
            self.at_word(n, spoken)
            self.play(FadeIn(b, shift=RIGHT * 0.2), run_time=0.45)
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_02",
            text="But very stiff or clichéd phrases, like do the needful, or revert back, are also marked down, because "
                 "they're unclear, or regionally non-standard.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "stiff")
        self.play(FadeIn(bans[3], shift=RIGHT * 0.2))
        self.at_word(n, "unclear")
        self.play(FadeIn(unclear, shift=UP * 0.1))
        self.wait_for_narration(n)

        # Clarity.
        chead = pill("CLARITY:  the reader understands ONE meaning, quickly", RATIO, size=LABEL)
        chead.move_to(UP * (CARD_TOP - chead.height / 2))
        damage = VGroup(
            VGroup(pill("wordiness", BAD, size=LABEL), text("“due to the fact that”  →  “because”", LABEL, INK))
            .arrange(RIGHT, buff=0.35),
            VGroup(pill("ambiguity", BAD, size=LABEL), text("“She told her sister that she had won.”", LABEL, INK),
                   text("who won?", LABEL, FOCUS)).arrange(RIGHT, buff=0.35),
            VGroup(pill("misplaced words", BAD, size=LABEL),
                   text("“I only ate two samosas”  vs  “I ate only two samosas”", LABEL, INK, t2c={"only": WORD}))
            .arrange(RIGHT, buff=0.35)).arrange(DOWN, buff=0.45, aligned_edge=LEFT)
        fit_within(damage, SAFE_W, SAFE_H - chead.height - 1.6)
        damage.next_to(chead, DOWN, buff=0.7)
        self.no_overlap(chead, damage)
        self.validator.check_in_frame(VGroup(chead, damage))
        n = self.narrate(
            id="concept_03",
            text="Clarity means the reader understands one meaning quickly. Three things damage clarity. Wordiness: due to "
                 "the fact that, instead of because. Ambiguity: she told her sister that she had won. Who won? And "
                 "misplaced words: I only ate two samosas, against I ate only two samosas.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(VGroup(head, expect, body)))
        self.at_word(n, "Clarity", occurrence=1)
        self.play(FadeIn(chead, shift=DOWN * 0.2))
        self.at_word(n, "damage")
        self.play(Indicate(chead, color=BAD, scale_factor=1.03))
        self.at_word(n, "Wordiness")
        self.play(FadeIn(damage[0], shift=RIGHT * 0.2))
        self.at_word(n, "Ambiguity")
        self.play(FadeIn(damage[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "Who")
        self.play(FadeIn(damage[1][2], scale=1.2))
        self.at_word(n, "misplaced")
        self.play(FadeIn(damage[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        order = VGroup(text("all options grammatical?  choose the one that is", LABEL, MUTED),
                       VGroup(pill("1  formal enough", WORD, size=BODY), pill("2  clear", RATIO, size=BODY),
                              pill("3  concise", GOOD, size=BODY)).arrange(RIGHT, buff=0.5),
                       text("in that order", LABEL, MUTED)).arrange(DOWN, buff=0.45)
        fit_width(order, SAFE_W).move_to(UP * 0.3)
        self.validator.check_in_frame(order)
        n = self.narrate(
            id="concept_04",
            text="When all options are grammatical, choose the one that is formal enough, clear, and concise, in that "
                 "order.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(VGroup(chead, damage)))
        self.at_word(n, "grammatical")
        self.play(FadeIn(order[0]))
        for o, spoken in zip(order[1], ["formal", "clear", "concise"]):
            self.at_word(n, spoken)
            self.play(FadeIn(o, shift=UP * 0.1), run_time=0.4)
        self.at_word(n, "order")
        self.play(FadeIn(order[2]))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_concept")

    # ======================================== 3. WHY YOU NEED IT ==========

    def why_you_need_it(self):
        self.scene_start("S03_why", title="Why You Need It")

        several = pill("improvement questions: two or three GRAMMATICAL options", BAD, size=LABEL)
        only = pill("only register or clarity separates them", RATIO, size=LABEL)
        work = pill("at work: the same judgement decides how clients and seniors see you", GOOD, size=LABEL)
        group = VGroup(several, only, work).arrange(DOWN, buff=0.7)
        fit_width(group, SAFE_W).move_to(UP * 0.3)
        self.no_overlap(several, only, work)
        self.validator.check_in_frame(group)

        n = self.narrate(
            id="why_01",
            text="Improvement questions often have two or three grammatical options, and only register or clarity "
                 "separates them. At work, the same judgement decides how clients and seniors see you.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "grammatical")
        self.play(FadeIn(several, shift=DOWN * 0.1))
        self.at_word(n, "separates")
        self.play(FadeIn(only, shift=UP * 0.1))
        self.at_word(n, "work")
        self.play(FadeIn(work, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_why")

    # ============================================== 4. ANALOGY ==========

    def analogy(self):
        self.scene_start("S04_analogy", title="The Analogy")

        outfits = VGroup(*[VGroup(pill(o, MUTED, size=BODY), text("correct clothes ✓", SMALL, MUTED)).arrange(DOWN, buff=0.12)
                           for o in ["gym clothes", "a formal suit", "a costume"]]).arrange(RIGHT, buff=0.7)
        invite = pill("the occasion:  a job interview", RATIO, size=LABEL)
        fits = text("only one fits", LABEL, GOOD)
        register = pill("register = choosing the outfit that fits the occasion", FOCUS, size=LABEL)
        block = VGroup(outfits, invite, fits, register).arrange(DOWN, buff=0.5)
        fit_within(block, SAFE_W, SAFE_H - 1.4)
        block.move_to(UP * 0.3)
        self.no_overlap(outfits, invite, fits, register)
        self.validator.check_in_frame(block)

        n = self.narrate(
            id="analogy_01",
            text="All three outfits are correct clothes. Only one fits a job interview. Register is choosing the outfit "
                 "that fits the occasion.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "three")
        self.play(LaggedStart(*[FadeIn(o, shift=UP * 0.1) for o in outfits], lag_ratio=0.25))
        self.at_word(n, "interview")
        self.play(FadeIn(invite, shift=UP * 0.1))
        self.play(outfits[1][0].animate.set_color(GOOD), FadeIn(fits), run_time=0.5)
        self.at_word(n, "Register")
        self.play(FadeIn(register, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_analogy")

    # ======================================== 5-7. WORKED EXAMPLES ==========

    def example_wordy(self):
        self.scene_start("S05_ex_wordy", title="Worked Example 1")
        self.play(self.pin(self.order_pin()))

        first, note, tag, fixed = self.clarity_example(
            "Due to the fact that the server was down, we postponed the release.", "Due to the fact that",
            "five words do the job of one", "CONCISION", "wordiness",
            "Because the server was down, we postponed the release.", "Because")

        n = self.narrate(
            id="ex1_01",
            text="Due to the fact that the server was down, we postponed the release. Five words do the job of one. That's "
                 "wordiness. The concise version: because the server was down.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Due")
        self.play(FadeIn(first, shift=DOWN * 0.1))
        self.at_word(n, "Five")
        self.play(FadeIn(note, shift=UP * 0.1))
        self.at_word(n, "wordiness")
        self.play(FadeIn(tag, shift=RIGHT * 0.2), self.light_test("CONCISION"))
        self.at_word(n, "because")
        self.play(FadeIn(fixed, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_ex_wordy")

    def example_only(self):
        self.scene_start("S06_ex_only", title="Worked Example 2")

        first, note, tag, fixed = self.clarity_example(
            "He only passed two subjects.", "only", "“only” should sit next to what it limits: two subjects",
            "CLARITY", "a misplaced word", "He passed only two subjects.", "only two subjects")

        n = self.narrate(
            id="ex2_01",
            text="He only passed two subjects. Only should sit next to what it limits: two subjects. A misplaced word: a "
                 "clarity fix. He passed only two subjects.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "He", occurrence=1)
        self.play(FadeIn(first, shift=DOWN * 0.1))
        self.at_word(n, "limits")
        self.play(FadeIn(note, shift=UP * 0.1))
        self.at_word(n, "misplaced")
        self.play(FadeIn(tag, shift=RIGHT * 0.2), self.light_test("CLARITY"))
        self.at_word(n, "passed", occurrence=2)
        self.play(FadeIn(fixed, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_ex_only")

    def example_ambiguous(self):
        self.scene_start("S07_ex_ambiguous", title="Worked Example 3")

        first, note, tag, fixed = self.clarity_example(
            "Ravi told Arjun that he was promoted.", "he", "who was promoted:  Ravi, or Arjun?", "CLARITY",
            "ambiguity", "Ravi told Arjun, “You have been promoted.”", "You have been promoted")

        n = self.narrate(
            id="ex3_01",
            text="Ravi told Arjun that he was promoted. Who was promoted: Ravi, or Arjun? That's ambiguity. Resolved: Ravi "
                 "told Arjun, you have been promoted.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Ravi", occurrence=1)
        self.play(FadeIn(first, shift=DOWN * 0.1))
        self.at_word(n, "Who")
        self.play(FadeIn(note, shift=UP * 0.1))
        self.at_word(n, "ambiguity")
        self.play(FadeIn(tag, shift=RIGHT * 0.2), self.light_test("CLARITY"))
        self.at_word(n, "Resolved")
        self.play(FadeIn(fixed, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S07_ex_ambiguous")

    # ================================================ 8. RULES ==========

    def rules(self):
        self.scene_start("S08_rules", title="Rules")
        self.play(self.unpin())

        table = self.table_rows(["Test", "Question"], [
            ["Register", "Is it neutral-to-formal?  No slang, abbreviations or clichés?"],
            ["Clarity", "One clear meaning?  Are only / just / even placed next to what they limit?"],
            ["Concision", "Is there a shorter way that says the same thing?"],
        ], [2.8, 9.2], size=LABEL)
        for row, (_n, _d, c) in zip(table[1:], TESTS):
            row[0].set_color(c)
        board = self.card(table, width=SAFE_W - 0.2).move_to(UP * 0.4)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="rules_01",
            text="Three tests, in order. Register: is it neutral to formal, with no slang, abbreviations or clichés? "
                 "Clarity: does it have one clear meaning, and are words like only, just and even placed next to what they "
                 "limit? Concision: is there a shorter way that says the same thing?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "tests")
        self.play(FadeIn(board[0]), FadeIn(table[0]))
        for row, spoken in zip(table[1:], ["Register", "Clarity", "Concision"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.45)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S08_rules")

    # ============================================== 9. PROCESS ==========

    def process(self):
        self.scene_start("S09_process", title="The Process")

        steps = VGroup(*[VGroup(pill(str(i + 1), c, size=SMALL), fitted_text(s_, SAFE_W - 2.2, BODY, INK))
                         .arrange(RIGHT, buff=0.3) for i, (s_, c) in enumerate([
                             ("Confirm the grammar is correct (S-T-P-A-W)", MUTED),
                             ("Check register: remove slang, abbreviations, clichés", WORD),
                             ("Check clarity: ambiguity and word placement", RATIO),
                             ("Choose the most concise option that passes", GOOD)])])
        steps.arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        board = self.card(steps).move_to(UP * 0.3)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="process_01",
            text="The process. First, confirm the grammar is correct, with the S, T, P, A, W scan. Second, check register: "
                 "remove slang, abbreviations and clichés. Third, check clarity: ambiguity and word placement. And fourth, "
                 "choose the most concise option that passes.",
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
        self.play(self.pin(self.order_pin()))

        cx, w = self.free_area()
        head = VGroup(pill("an email to a CLIENT", WORD, size=SMALL),
                      pill("predict: polite, formal, clear, no abbreviations", STEP_COLS["PREDICT"], size=SMALL))\
            .arrange(RIGHT, buff=0.3)
        fit_width(head, w - 0.6)
        rows = self.version_rows(w - 0.4)
        block = VGroup(head, rows).arrange(DOWN, buff=0.4, aligned_edge=LEFT)
        fit_height(block, SAFE_H - 1.4)
        self.place_free(block, y=0.2)
        send = [why for _v, why in HOOK_VERSIONS].index(None)
        box = SurroundingRectangle(rows[send][0], color=GOOD, buff=0.1, corner_radius=0.1)
        self.no_overlap(head, rows)
        self.validator.check_in_frame(block)

        n = self.narrate(
            id="solved_01",
            text="Let's solve the hook. Read: an email to a client. Predict: polite, formal, clear, with no abbreviations.",
            voice="default",
            subtitle=True,
        )
        self.play(LaggedStart(*[FadeIn(r[0], shift=UP * 0.1) for r in rows], lag_ratio=0.15))
        self.at_word(n, "Read")
        self.play(FadeIn(head[0], shift=DOWN * 0.1), self.light_test("REGISTER"))
        self.at_word(n, "Predict")
        self.play(FadeIn(head[1], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_02",
            text="Eliminate. Version A keeps hey, and sounds abrupt. Version C keeps wanna, and P L S. Version D uses do "
                 "the needful, a non-standard cliché, and ASAP is informal.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Eliminate")
        self.play(Indicate(rows, color=BAD, scale_factor=1.01))
        for i, spoken in [(0, "A"), (2, "C"), (3, "D")]:
            self.at_word(n, spoken, occurrence=1)
            self.play(FadeIn(rows[i][1], shift=UP * 0.05), rows[i][0].animate.set_opacity(0.45), run_time=0.6)
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_03",
            text="Confirm: version B. We would like to close this soon, so please send the files at your earliest "
                 "convenience. It's formal, clear and complete.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Confirm")
        self.play(Create(box))
        self.at_word(n, "like")
        self.play(Indicate(rows[send][0], color=GOOD, scale_factor=1.02))
        self.at_word(n, "formal")
        self.play(FadeIn(rows[send][1], shift=UP * 0.05))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S10_hook_solved")

    # ========================================== 11. EXAM PATTERNS ==========

    def exam_patterns(self):
        self.scene_start("S11_patterns", title="Exam Patterns and Solving Models")
        self.play(self.unpin())

        table = self.table_rows(["Pattern", "Solving model"], [
            ["All options grammatical", "register, then clarity, then concision"],
            ["“only / just / even” in the bold part", "place it next to what it limits"],
            ["Wordy bold part", "look for the shortest correct replacement"],
        ], [5.4, 6.4], size=LABEL)
        board = self.card(table, width=SAFE_W - 0.2).move_to(UP * 0.4)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="patterns_01",
            text="Three exam patterns. All options grammatical: check register, then clarity, then concision. Only, just "
                 "or even in the bold part: place it next to what it limits. And a wordy bold part: look for the shortest "
                 "correct replacement.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(board[0]), FadeIn(table[0]))
        for row, spoken in zip(table[1:], ["grammatical", "Only", "wordy"]):
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
            (self.verdict_card(False, "The most formal-sounding cliché: “do the needful”", card_w),
             self.verdict_card(True, "Plain, standard and polite", card_w)),
            (self.verdict_card(False, "Ignoring ambiguous pronouns", card_w),
             self.verdict_card(True, "Ask: who does “he” mean?", card_w)),
            (self.verdict_card(False, "Longer options “sound more complete”", card_w),
             self.verdict_card(True, "The shortest correct version wins", card_w)),
        ]
        for (wrong, right), yy in zip(pairs, [1.6, 0.05, -1.5]):
            wrong.move_to(LEFT_ZONE + UP * yy)
            right.move_to(RIGHT_ZONE + UP * yy)
        header = pill("3 mistakes", BAD, size=LABEL).move_to(UP * (CARD_TOP - 0.3))
        self.validator.check_in_frame(VGroup(header, *[c for p in pairs for c in p]))

        n = self.narrate(
            id="mistakes_01",
            text="Three common mistakes. The first is choosing the most formal-sounding cliché, like do the needful. The "
                 "second is ignoring ambiguous pronouns. The third is preferring longer options, because they sound more "
                 "complete.",
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
        ("At this point in time, we have no openings.", "At this point in time",
         ["Currently", "At this moment in time", "At this point of time now", "No improvement"], "a", "concise"),
        ("I just told him the truth yesterday.", "just told him the truth",
         ["told him just", "told him only", "told him the truth only yesterday", "No improvement"], "c",
         "the limiting word goes next to “yesterday”;  “just” with a past time is awkward"),
        ("Kindly revert back by Monday.", "revert back", ["reply", "revert", "revert back again", "No improvement"], "a",
         "“revert” = return to a previous state;  in formal writing, “reply” is the standard word"),
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
            text="Your turn. One: at this point in time, we have no openings. Currently, at this moment in time, at this "
                 "point of time now, or no improvement? Two: I just told him the truth yesterday. Told him just, told him "
                 "only, told him the truth only yesterday, or no improvement? Three: kindly revert back by Monday. Reply, "
                 "revert, revert back again, or no improvement?",
            voice="default",
            subtitle=True,
            pause_after=12.0,
        )
        self.play(FadeIn(board[0]))
        for ln, (spoken, first_option, occ) in zip(lines, [("openings", "Currently", 1), ("truth", "Told", 2),
                                                          ("kindly", "Reply", 1)]):
            self.at_word(n, spoken, occurrence=1)
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
            text="One: currently. It's concise. Two: told him the truth only yesterday. The limiting word goes next to "
                 "yesterday, and just with a past time is awkward. Three: reply. Revert means return to a previous state; "
                 "in formal writing, reply is the standard word.",
            voice="default",
            subtitle=True,
        )
        for r, (spoken, why) in zip(rows, [("One", "concise"), ("Two", "limiting"), ("Three", "previous")]):
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

        card, table = self.recap_card("Recap Card: Video 3", [
            ["Register", "neutral to formal; no slang, abbreviations or clichés"],
            ["Clarity", "one meaning; limiting words next to what they limit"],
            ["Concision", "the shortest correct version wins"],
        ])
        card.move_to(UP * 0.2)
        self.validator.check_in_frame(card)

        n = self.narrate(
            id="recap_01",
            text="To recap. Register: neutral to formal, with no slang, abbreviations or clichés. Clarity: one meaning, "
                 "with limiting words next to what they limit. Concision: the shortest correct version wins.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(card[0]), FadeIn(table[0]))
        for row, spoken in zip(table[1:], ["Register", "Clarity", "Concision"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.45)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S15_recap")

    # ================================================= 16. NEXT ==========

    def next_video(self):
        self.scene_start("S16_next", title="Next")

        traps = pill("the traps built into the options themselves", BAD, size=LABEL)
        wrong = pill("including “corrections” that are actually wrong", RATIO, size=LABEL)
        nxt = pill("Next:  Commonly Confused Correction Traps", FOCUS, size=LABEL)
        VGroup(traps, wrong, nxt).arrange(DOWN, buff=0.7).move_to(UP * 0.2)
        self.no_overlap(traps, wrong, nxt)
        self.validator.check_in_frame(VGroup(traps, wrong, nxt))

        n = self.narrate(
            id="next_01",
            text="Video four shows the traps built into the options themselves, including corrections that are actually "
                 "wrong.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Video")
        self.play(FadeIn(nxt, scale=1.05))
        self.at_word(n, "traps")
        self.play(FadeIn(traps, shift=UP * 0.1))
        self.at_word(n, "wrong")
        self.play(FadeIn(wrong, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S16_next")
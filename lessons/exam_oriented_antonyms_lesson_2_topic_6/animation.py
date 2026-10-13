"""
animation.py for the LMS video generator.

Course : C-CAT - Section A - English
Module : Module 1 - Vocabulary
Lesson : Lesson 2 - Antonyms
Video  : 06 - Exam-Oriented Antonyms (Video 6 of 7)

Source script:
  C:\\Users\\User\\Downloads\\C-CAT_SectionA_Module1_English\\English\\Module 1 - Vocabulary\\
  Lesson 2 - Antonyms\\06 - Exam-Oriented Antonyms.pdf

Built on the golden-reference pattern:
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``;
  * layouts stacked with next_to and guarded with ``no_overlap``; nothing is
    ever animated onto or into another box.

The twelve shelf pairs live in SHELF_PAIRS; shelves_of(word) looks up a word's own shelf and its opposite shelf, and the hook, worked examples and practice answers are asserted against it.
The "opposite shelves" four-step card stays pinned top-right through the worked examples and Hook, Solved.
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

# Opposite shelves from the script's Rules table: (shelf, opposite shelf).
SHELF_PAIRS = [
    (["abundant", "copious", "ample"], ["scarce", "meagre", "sparse"]),
    (["verbose", "wordy", "loquacious"], ["concise", "terse", "taciturn"]),
    (["lucid", "explicit", "transparent"], ["obscure", "vague", "opaque"]),
    (["diligent", "industrious"], ["indolent", "lazy", "idle"]),
    (["obstinate", "adamant", "rigid"], ["flexible", "docile", "yielding"]),
    (["commend", "laud", "extol"], ["censure", "criticise", "condemn"]),
    (["frugal", "thrifty"], ["extravagant", "lavish", "prodigal"]),
    (["ephemeral", "transient"], ["permanent", "enduring"]),
    (["augment", "amplify"], ["diminish", "curtail"]),
    (["novice", "amateur"], ["veteran", "expert"]),
    (["benevolent", "benign"], ["malevolent", "malign"]),
    (["candid", "frank"], ["evasive", "guarded"]),
]
ROOT_PAIRS = [("bene", "mal", "good / bad"), ("pro", "anti", "for / against"), ("pre", "post", "before / after"),
              ("ascend", "descend", "up / down")]


def shelves_of(word):
    """(same shelf, opposite shelf) for a word in the table."""
    for a, b in SHELF_PAIRS:
        if word in a:
            return a, b
        if word in b:
            return b, a
    raise KeyError(word)


def double_shelf(left, right, width=SAFE_W - 0.6, size=SMALL, left_col=GOOD, right_col=BAD):
    """Two faces of one shelf: a shelf of words, ↔, the opposite shelf."""
    lj = VGroup(*[pill(w, INK, size=size, fill_opacity=0.06) for w in left]).arrange(RIGHT, buff=0.15)
    rj = VGroup(*[pill(w, INK, size=size, fill_opacity=0.06) for w in right]).arrange(RIGHT, buff=0.15)
    mid = text("↔", LABEL, MUTED)
    row = VGroup(lj, mid, rj).arrange(RIGHT, buff=0.4)
    fit_width(row, width)
    pl = Line(lj.get_corner(DL) + DOWN * 0.08, lj.get_corner(DR) + DOWN * 0.08, color=left_col, stroke_width=4)
    pr = Line(rj.get_corner(DL) + DOWN * 0.08, rj.get_corner(DR) + DOWN * 0.08, color=right_col, stroke_width=4)
    return VGroup(VGroup(lj, pl), mid, VGroup(rj, pr))


class ExamOrientedAntonymsVideo(LMSScene):
    lesson_title = "Exam-Oriented Antonyms"

    def construct(self):
        self.camera.background_color = BG

        self.lesson_intro()
        self.hook()
        self.concept_shelves()
        self.concept_roots()
        self.why_you_need_it()
        self.analogy()
        self.example_verbose()
        self.example_ephemeral()
        self.example_malevolent()
        self.rules_first()
        self.rules_second()
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

    def shelf_pin(self):
        return self.steps_pin("opposite shelves", [("place the word on its shelf", GOOD),
                                                   ("turn to the opposite shelf", STEP_COLS["PREDICT"]),
                                                   ("strike same-shelf options", BAD),
                                                   ("confirm: not X, but Y", SECOND)])

    def shelf_board(self, pairs):
        rows = VGroup(*[double_shelf(a, b) for a, b in pairs]).arrange(DOWN, buff=0.32)
        fit_within(rows, SAFE_W - 0.4, SAFE_H - 1.4)
        rows.move_to(UP * (CARD_TOP - rows.height / 2 - 0.1))
        return rows

    def readme_card(self, fill=None):
        head = text("REVIEW COMMENT on README", SMALL, RATIO, BOLD)
        line = text("“Too verbose. Make it the opposite.”" if not fill else f"“Not verbose, but {fill}.”", BODY, INK,
                    t2c={"verbose": WORD, fill or "opposite": GOOD if fill else BAD})
        cx, w = self.free_area()
        card = self.card(VGroup(head, fit_width(line, w - 1.4)).arrange(DOWN, buff=0.2, aligned_edge=LEFT),
                         width=min(w - 0.2, SAFE_W - 0.4))
        return card.move_to(RIGHT * cx + UP * (CARD_TOP - card.height / 2))

    # ========================================= 0. LESSON INTRO ==========

    def lesson_intro(self):
        self.scene_start("S00_intro", title="Lesson Introduction")

        crumb = self.breadcrumb("English · Module 1 Vocabulary", "Lesson 2 · Antonyms", "Video 6")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        one = double_shelf(SHELF_PAIRS[0][0], SHELF_PAIRS[0][1], width=SAFE_W - 1.5, size=LABEL)
        before = text("Lesson 1, Video 5: one shelf per meaning", SMALL, MUTED)
        both = pill("one word  →  a synonym set AND an antonym set", GOOD, size=LABEL)
        VGroup(before, one, both).arrange(DOWN, buff=0.5).move_to(DOWN * 0.1)
        self.no_overlap(crumb, before, one, both)
        self.validator.check_in_frame(VGroup(crumb, before, one, both))

        n = self.narrate(
            id="intro_01",
            text="In lesson one, video five, you stored words on meaning shelves. Today each shelf gets its opposite "
                 "shelf, so one word gives you both a synonym set and an antonym set.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.at_word(n, "shelves")
        self.play(FadeIn(before), FadeIn(one[0], shift=UP * 0.1))
        self.at_word(n, "opposite")
        self.play(FadeIn(one[1]), FadeIn(one[2], shift=LEFT * 0.2))
        self.at_word(n, "both")
        self.play(FadeIn(both, shift=UP * 0.1))
        self.wait_for_narration(n)

        title = fitted_text("Exam-Oriented Antonyms", SAFE_W, 72, INK, BOLD)
        underline = Line(LEFT, RIGHT, color=BAD, stroke_width=5).set_width(title.width * 0.6)
        VGroup(title, underline).arrange(DOWN, buff=0.2).move_to(UP * 0.2)
        goals = [("Learn high-frequency exam words as opposite shelves", GOOD),
                 ("Use roots to predict the opposite of unfamiliar words", SECOND)]
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
            text="These are the exam-oriented antonyms. By the end of this video, you'll learn high-frequency exam words as "
                 "opposite shelves, and use roots to predict the opposite of unfamiliar words.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(VGroup(before, one, both), shift=UP * 0.3))
        self.at_word(n, "exam-oriented")
        self.play(Write(title), run_time=1.1)
        self.play(GrowFromCenter(underline))
        self.at_word(n, "By")
        self.play(FadeOut(underline), ReplacementTransform(title, small_title), run_time=0.8)
        self.play(FadeIn(objectives[0]), FadeIn(heading))
        for row_, spoken in zip(rows, ["learn", "roots"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row_, shift=RIGHT * 0.2), run_time=0.5)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_intro")

    # ================================================= 1. HOOK ==========

    HOOK = dict(word="VERBOSE", options=["wordy", "concise", "detailed", "formal"], key="b",
                traps={"a": "same shelf: the synonym trap", "c": "different topic", "d": "different topic"})

    def hook(self):
        self.scene_start("S01_hook", title="Hook")

        h = self.HOOK
        same, opp = shelves_of("verbose")
        assert h["options"]["abcd".index(h["key"])] in opp and "wordy" in same
        note = self.readme_card()
        q = OptionQuestion(h["word"], h["options"], h["key"], h["traps"])
        opts = q.rows.copy().arrange(RIGHT, buff=0.8)
        ask = pill("What kind of README does she want?", FOCUS, size=LABEL)
        ask.next_to(note, DOWN, buff=0.6)
        opts.next_to(ask, DOWN, buff=0.6)
        self.no_overlap(note, ask, opts)
        self.validator.check_in_frame(VGroup(note, ask, opts))

        n = self.narrate(
            id="hook_01",
            text="Your documentation lead reviews your README: too verbose. Make it the opposite. What kind of README does "
                 "she want?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "README")
        self.play(FadeIn(note, shift=DOWN * 0.2))
        self.at_word(n, "opposite")
        self.play(Indicate(note[1][1], color=BAD, scale_factor=1.03))
        self.at_word(n, "What")
        self.play(FadeIn(ask, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_02",
            text="Wordy, concise, detailed, or formal?",
            voice="default",
            subtitle=True,
            pause_after=3.0,
        )
        for row, spoken in zip(opts, ["Wordy", "concise", "detailed", "formal"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=UP * 0.15), run_time=0.35)
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        self.clear_stage()
        self.scene_end("S01_hook")

    # ===================================== 2. CONCEPT: OPPOSITE SHELVES ==========

    def concept_shelves(self):
        self.scene_start("S02_concept_shelves", title="The Concept - Opposite Shelves")

        head = pill("exam antonyms come from a stable pool of words", WORD, size=LABEL)
        head.move_to(UP * (CARD_TOP - head.height / 2))
        pair = double_shelf(["verbose", "wordy", "loquacious"], ["concise", "terse", "succinct"], size=LABEL)
        pair.next_to(head, DOWN, buff=0.9)
        fastest = text("learn them as opposite pairs of shelves: the fastest route", LABEL, GOOD)
        fastest.next_to(pair, UP, buff=0.3)
        rule = pill("a word from one shelf  →  the answer comes from the opposite shelf", FOCUS, size=SMALL)
        fit_width(rule, SAFE_W)
        rule.next_to(pair, DOWN, buff=0.6)
        self.no_overlap(head, fastest, pair, rule)
        self.validator.check_in_frame(VGroup(head, fastest, pair, rule))

        n = self.narrate(
            id="shelves_01",
            text="Exam antonyms come from a stable pool of words. Learning them as opposite pairs of shelves is the "
                 "fastest route: verbose, wordy and loquacious on one side; concise, terse and succinct on the other.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "stable")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "pairs")
        self.play(FadeIn(fastest, shift=UP * 0.1))
        self.at_word(n, "verbose")
        self.play(FadeIn(pair[0], shift=RIGHT * 0.2))
        self.at_word(n, "concise")
        self.play(FadeIn(pair[1]), FadeIn(pair[2], shift=LEFT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="shelves_02",
            text="When you meet any word from one shelf, the answer comes from the opposite shelf.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "answer")
        self.play(FadeIn(rule, shift=UP * 0.1), Indicate(pair[2], color=GOOD, scale_factor=1.04))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_concept_shelves")

    # ============================================ 3. CONCEPT: ROOTS ==========

    def concept_roots(self):
        self.scene_start("S03_concept_roots", title="The Concept - Root Pairs")

        head = pill("unfamiliar word?  roots still work", SECOND, size=LABEL)
        head.move_to(UP * (CARD_TOP - head.height / 2))
        rows = VGroup(*[VGroup(pill(a, GOOD, size=LABEL), text("/", LABEL, MUTED), pill(b, BAD, size=LABEL),
                               text(meaning, LABEL, INK)).arrange(RIGHT, buff=0.3) for a, b, meaning in ROOT_PAIRS])
        rows.arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        example = text("benevolent  ↔  malevolent", LABEL, FOCUS).next_to(rows[0], RIGHT, buff=0.6)
        block = VGroup(rows, example)
        fit_width(block, SAFE_W)
        block.next_to(head, DOWN, buff=0.5)
        partial = pill("even a partial decode tells you the DIRECTION you need", FOCUS, size=SMALL)
        partial.next_to(block, DOWN, buff=0.5)
        self.no_overlap(head, block, partial)
        self.validator.check_in_frame(VGroup(head, block, partial))

        n = self.narrate(
            id="roots_01",
            text="For unfamiliar words, roots still work. Bene and mal, good and bad, give benevolent and malevolent. Pro "
                 "and anti: for and against. Pre and post: before and after. Ascend and descend.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "roots")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "Bene")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "benevolent")
        self.play(FadeIn(example, shift=LEFT * 0.1))
        for r, spoken in zip(rows[1:], ["Pro", "Pre", "Ascend"]):
            self.at_word(n, spoken)
            self.play(FadeIn(r, shift=RIGHT * 0.2), run_time=0.4)
        self.wait_for_narration(n)

        n = self.narrate(
            id="roots_02",
            text="Even a partial decode tells you the direction you need.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "direction")
        self.play(FadeIn(partial, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_concept_roots")

    # ======================================== 4. WHY YOU NEED IT ==========

    def why_you_need_it(self):
        self.scene_start("S04_why", title="Why You Need It")

        often = pill("several of these pairs in almost every English section", BAD, size=LABEL)
        blank = text("“Although the first draft was verbose, the final one was ______.”", LABEL, INK,
                     t2c={"verbose": WORD, "______": FOCUS})
        tag = pill("Sentence Completion: the blank needs the OPPOSITE of the clue word", GOOD, size=SMALL)
        group = VGroup(often, blank, tag).arrange(DOWN, buff=0.6)
        fit_width(group, SAFE_W).move_to(UP * 0.3)
        self.no_overlap(often, blank, tag)
        self.validator.check_in_frame(group)

        n = self.narrate(
            id="why_01",
            text="You'll meet several of these pairs in almost every English section. The shelves also make sentence "
                 "completion faster, because blanks often need the opposite of a clue word.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "several")
        self.play(FadeIn(often, shift=DOWN * 0.1))
        self.at_word(n, "sentence")
        self.play(FadeIn(blank, shift=UP * 0.1))
        self.at_word(n, "opposite")
        self.play(FadeIn(tag, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_why")

    # ============================================== 5. ANALOGY ==========

    def analogy(self):
        self.scene_start("S05_analogy", title="The Analogy")

        front = VGroup(text("Plenty", LABEL, GOOD, BOLD), *[pill(w, INK, size=LABEL, fill_opacity=0.06)
                                                           for w in SHELF_PAIRS[0][0]]).arrange(DOWN, buff=0.25)
        back = VGroup(text("Scarce", LABEL, BAD, BOLD), *[pill(w, INK, size=LABEL, fill_opacity=0.06)
                                                         for w in SHELF_PAIRS[0][1]]).arrange(DOWN, buff=0.25)
        spine = Line(UP * 1.6, DOWN * 1.6, color=MUTED, stroke_width=8)
        case = VGroup(front, spine, back).arrange(RIGHT, buff=0.9).move_to(UP * 0.4)
        links = VGroup(*[DashedLine(f.get_right(), b.get_left(), color=MUTED, stroke_width=2)
                         for f, b in zip(front[1:], back[1:])])
        both = pill("learn the shelf once: you get both sides", GOOD, size=LABEL).to_edge(DOWN, buff=SAFE + 0.4)
        self.no_overlap(case, both)
        self.validator.check_in_frame(VGroup(case, both))

        n = self.narrate(
            id="analogy_01",
            text="Think of a bookshelf with two faces. Turn it round, and every word has its opposite directly behind it. "
                 "Learn the shelf once, and you get both sides.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "bookshelf")
        self.play(Create(spine), FadeIn(front, shift=RIGHT * 0.2))
        self.at_word(n, "Turn")
        self.play(FadeIn(back, shift=LEFT * 0.2))
        self.play(LaggedStart(*[Create(l) for l in links], lag_ratio=0.2), run_time=0.8)
        self.at_word(n, "Learn")
        self.play(FadeIn(both, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_analogy")

    # ======================================== 6-8. WORKED EXAMPLES ==========

    def shelf_example(self, word, left_label, right_label):
        """Word above its double shelf, laid out beside the pinned panel."""
        same, opp = shelves_of(word)
        title = pill(word.upper(), WORD, size=TITLE)
        ds = double_shelf(same, opp, size=LABEL)
        labels = VGroup(text(left_label, SMALL, GOOD).next_to(ds[0], UP, buff=0.15),
                        text(right_label, SMALL, BAD).next_to(ds[2], UP, buff=0.15))
        group = VGroup(title, VGroup(ds, labels)).arrange(DOWN, buff=0.7)
        self.place_free(group, y=0.0)
        self.validator.check_in_frame(group)
        return title, ds, labels, opp

    def example_verbose(self):
        self.scene_start("S06_ex_verbose", title="Worked Example 1")
        self.play(self.pin(self.shelf_pin()))

        title, ds, labels, opp = self.shelf_example("verbose", "shelf: wordy", "opposite shelf: brief")
        assert "concise" in opp

        n = self.narrate(
            id="ex1_01",
            text="Verbose sits on the wordy shelf. Turn to the opposite shelf, brief. The antonym is concise.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(title, scale=1.1))
        self.at_word(n, "wordy")
        self.play(FadeIn(ds[0], shift=UP * 0.1), FadeIn(labels[0]), self.pin_step(0))
        self.at_word(n, "Turn")
        self.play(FadeIn(ds[1]), FadeIn(ds[2], shift=LEFT * 0.2), FadeIn(labels[1]), self.pin_step(1))
        self.at_word(n, "concise")
        self.play(Indicate(ds[2][0][opp.index("concise")], color=GOOD, scale_factor=1.25))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_ex_verbose")

    def example_ephemeral(self):
        self.scene_start("S07_ex_ephemeral", title="Worked Example 2")

        title, ds, labels, opp = self.shelf_example("ephemeral", "shelf: short-lived", "opposite shelf: lasting")
        assert opp == ["permanent", "enduring"]

        n = self.narrate(
            id="ex2_01",
            text="Ephemeral sits on the short-lived shelf. The opposite shelf is lasting. So the antonym is permanent, or "
                 "enduring.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(title, scale=1.1))
        self.at_word(n, "short-lived")
        self.play(FadeIn(ds[0], shift=UP * 0.1), FadeIn(labels[0]), self.pin_step(0))
        self.at_word(n, "lasting")
        self.play(FadeIn(ds[1]), FadeIn(ds[2], shift=LEFT * 0.2), FadeIn(labels[1]), self.pin_step(1))
        self.at_word(n, "permanent")
        self.play(Indicate(ds[2][0], color=GOOD, scale_factor=1.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S07_ex_ephemeral")

    def example_malevolent(self):
        self.scene_start("S08_ex_malevolent", title="Worked Example 3")

        same, opp = shelves_of("malevolent")
        assert "benevolent" in opp
        title = pill("MALEVOLENT", WORD, size=TITLE)
        parts = VGroup(VGroup(pill("mal", BAD, size=BODY), text("bad", SMALL, BAD)).arrange(DOWN, buff=0.12),
                       VGroup(pill("vol", SECOND, size=BODY), text("wish", SMALL, SECOND)).arrange(DOWN, buff=0.12),
                       VGroup(pill("ent", MUTED, size=BODY), text("ending", SMALL, MUTED)).arrange(DOWN, buff=0.12))\
            .arrange(RIGHT, buff=0.15, aligned_edge=UP)
        assert "".join(["mal", "e", "vol", "ent"]) == "malevolent"
        swap = VGroup(pill("mal", BAD, size=LABEL), text("→", LABEL, MUTED), pill("bene", GOOD, size=LABEL),
                      text("=", LABEL, MUTED), pill("benevolent", GOOD, size=BODY)).arrange(RIGHT, buff=0.3)
        group = VGroup(title, parts, swap).arrange(DOWN, buff=0.6)
        self.place_free(group, y=0.1)
        self.no_overlap(title, parts, swap)
        self.validator.check_in_frame(group)

        n = self.narrate(
            id="ex3_01",
            text="Malevolent. The root mal means bad, and vol means wish: wishing bad. Flip mal to bene, and the opposite "
                 "is benevolent.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(title, scale=1.1))
        self.at_word(n, "mal", occurrence=1)
        self.play(FadeIn(parts[0], shift=UP * 0.1), FadeIn(parts[2]))
        self.at_word(n, "vol")
        self.play(FadeIn(parts[1], shift=UP * 0.1))
        self.at_word(n, "Flip")
        self.play(FadeIn(swap[:3], shift=UP * 0.1), self.pin_step(1))
        self.at_word(n, "benevolent")
        self.play(FadeIn(swap[3:], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S08_ex_malevolent")

    # ================================================ 9. RULES ==========

    def rules_first(self):
        self.scene_start("S09_rules_first", title="Rules: Opposite Shelves (1)")
        self.play(self.unpin())

        board = self.shelf_board(SHELF_PAIRS[:6])
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="rules_01",
            text="Here are twelve pairs of shelves. Abundant, against scarce. Verbose, against concise. Lucid, against "
                 "obscure. Diligent, against indolent. Obstinate, against flexible. Commend, against censure.",
            voice="default",
            subtitle=True,
        )
        twelve = pill("12 pairs of shelves", FOCUS, size=BODY)
        self.at_word(n, "twelve")
        self.play(FadeIn(twelve, scale=1.2), run_time=0.4)
        self.play(FadeOut(twelve), run_time=0.3)
        for row, spoken in zip(board, ["Abundant", "Verbose", "Lucid", "Diligent", "Obstinate", "Commend"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row[0], shift=RIGHT * 0.1), FadeIn(row[1]), FadeIn(row[2], shift=LEFT * 0.1), run_time=0.5)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S09_rules_first")

    def rules_second(self):
        self.scene_start("S10_rules_second", title="Rules: Opposite Shelves (2)")

        board = self.shelf_board(SHELF_PAIRS[6:])
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="rules_02",
            text="Frugal, against extravagant. Ephemeral, against permanent. Augment, against diminish. Novice, against "
                 "veteran. Benevolent, against malevolent. And candid, against evasive.",
            voice="default",
            subtitle=True,
        )
        for row, spoken in zip(board, ["Frugal", "Ephemeral", "Augment", "Novice", "Benevolent", "candid"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row[0], shift=RIGHT * 0.1), FadeIn(row[1]), FadeIn(row[2], shift=LEFT * 0.1), run_time=0.5)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S10_rules_second")

    # ============================================= 11. PROCESS ==========

    def process(self):
        self.scene_start("S11_process", title="The Process")

        steps = VGroup(*[VGroup(pill(str(i + 1), c, size=SMALL), fitted_text(s_, SAFE_W - 2.2, BODY, INK))
                         .arrange(RIGHT, buff=0.3) for i, (s_, c) in enumerate([
                             ("Place the question word on its shelf", GOOD),
                             ("Turn to the opposite shelf and predict", STEP_COLS["PREDICT"]),
                             ("Strike any option from the SAME shelf (the synonym trap)", BAD),
                             ("Confirm with “not X but Y”", SECOND)])])
        steps.arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        board = self.card(steps).move_to(UP * 0.3)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="process_01",
            text="The process. First, place the question word on its shelf. Second, turn to the opposite shelf and "
                 "predict. Third, strike any option from the same shelf: the synonym trap. And fourth, confirm with not X "
                 "but Y.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(board[0]))
        for r, spoken in zip(steps, ["First", "Second", "Third", "fourth"]):
            self.at_word(n, spoken)
            self.play(FadeIn(r, shift=RIGHT * 0.2), run_time=0.45)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S11_process")

    # ========================================== 12. HOOK, SOLVED ==========

    def hook_solved(self):
        self.scene_start("S12_hook_solved", title="Hook, Solved")
        self.play(self.pin(self.shelf_pin()))

        h = self.HOOK
        note = self.readme_card()
        q = OptionQuestion(h["word"], h["options"], h["key"], h["traps"], word_size=BODY)
        q.group.next_to(note, DOWN, buff=0.4).to_edge(LEFT, buff=SAFE + 0.6)
        predict = pill("too many words  →  the “brief” shelf", STEP_COLS["PREDICT"], size=SMALL)
        predict.next_to(q.word, RIGHT, buff=0.4)
        fixed = self.readme_card(fill="concise")
        cut = pill("cut the README down", GOOD, size=LABEL).to_edge(DOWN, buff=SAFE + 0.4)
        self.no_overlap(note, q.group, cut)
        self.no_overlap(note, self.pinned)
        self.no_overlap(q.group, predict, self.pinned)
        self.validator.check_in_frame(VGroup(note, q.group, predict, cut))

        n = self.narrate(
            id="solved_01",
            text="Let's solve the hook. Read: verbose means using too many words. Predict: the brief shelf.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(note), FadeIn(q.word), FadeIn(q.rows))
        self.at_word(n, "Read")
        self.play(Indicate(q.word, color=WORD, scale_factor=1.08), self.pin_step(0))
        self.at_word(n, "Predict")
        self.play(FadeIn(predict, shift=LEFT * 0.1), self.pin_step(1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_02",
            text="Eliminate. Wordy is the synonym: the trap. Detailed and formal are different topics.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Eliminate")
        self.play(self.pin_step(2))
        self.at_word(n, "Wordy")
        self.play(*q.strike("a")[1])
        self.at_word(n, "Detailed")
        self.play(*q.strike("c")[1], *q.strike("d")[1])
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_03",
            text="Confirm: not verbose, but concise. The answer is concise. Cut the README down.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Confirm")
        self.play(ReplacementTransform(note, fixed), self.pin_step(3))
        self.at_word(n, "answer")
        self.play(*q.confirm()[1])
        self.at_word(n, "Cut")
        self.play(FadeIn(cut, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S12_hook_solved")

    # ========================================== 13. EXAM PATTERNS ==========

    def exam_patterns(self):
        self.scene_start("S13_patterns", title="Exam Patterns and Solving Models")
        self.play(self.unpin())

        table = self.table_rows(["Pattern", "Solving model"], [
            ["Known word", "opposite shelf; strike same-shelf options"],
            ["Unknown word", "root → direction → opposite direction"],
            ["Two options from the opposite shelf", "break the tie on degree (Lesson 1, Video 2)"],
        ], [4.8, 7.0], size=LABEL)
        board = self.card(table, width=SAFE_W - 0.2).move_to(UP * 0.4)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="patterns_01",
            text="Three exam patterns. A known word: go to the opposite shelf, and strike same-shelf options. An unknown "
                 "word: root, then direction, then the opposite direction. And two options from the opposite shelf: break "
                 "the tie on degree, as in lesson one, video two.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(board[0]), FadeIn(table[0]))
        for row, spoken in zip(table[1:], ["known", "unknown", "two"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.45)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S13_patterns")

    # ======================================== 14. COMMON MISTAKES ==========

    def common_mistakes(self):
        self.scene_start("S14_mistakes", title="Common Mistakes")

        card_w = ZONE_W - 0.3
        pairs = [
            (self.verdict_card(False, "Picking a same-shelf word", card_w),
             self.verdict_card(True, "Strike the same shelf first", card_w)),
            (self.verdict_card(False, "Pairs learned without shelves", card_w),
             self.verdict_card(True, "Both shelves together: easy recall", card_w)),
            (self.verdict_card(False, "A different topic: verbose → formal", card_w),
             self.verdict_card(True, "verbose ↔ concise", card_w)),
        ]
        for (wrong, right), yy in zip(pairs, [1.6, 0.05, -1.5]):
            wrong.move_to(LEFT_ZONE + UP * yy)
            right.move_to(RIGHT_ZONE + UP * yy)
        header = pill("3 mistakes", BAD, size=LABEL).move_to(UP * (CARD_TOP - 0.3))
        self.validator.check_in_frame(VGroup(header, *[c for p in pairs for c in p]))

        n = self.narrate(
            id="mistakes_01",
            text="Three common mistakes. The first is picking a same-shelf word. The second is learning pairs without "
                 "shelves, so they're hard to recall under pressure. The third is picking a different-topic word, like "
                 "formal for verbose.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(header))
        for pr, spoken in zip(pairs, ["first", "second", "third"]):
            self.at_word(n, spoken)
            self.play(FadeIn(pr[0], shift=RIGHT * 0.3), FadeIn(pr[1], shift=LEFT * 0.3))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S14_mistakes")

    # ============================================== 15. PRACTICE ==========

    PRACTICE = [
        ("CURTAIL", ["extend", "shorten", "cut", "cover"], "a",
         {"b": "synonym", "c": "synonym", "d": "unrelated"}, "curtail = cut short"),
        ("TACITURN", ["silent", "rude", "angry", "talkative"], "d",
         {"a": "synonym", "b": "unrelated", "c": "unrelated"}, "taciturn = saying little"),
        ("NOVICE", ["beginner", "student", "veteran", "novelist"], "c",
         {"a": "synonym", "b": "near, not opposite", "d": "sound-alike"}, "novice ↔ veteran: opposite shelf"),
    ]

    def practice(self):
        self.scene_start("S15_practice", title="Practice Questions")

        assert "veteran" in shelves_of("novice")[1]
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
            text="Your turn: choose the opposite. One: curtail. Extend, shorten, cut, or cover? Two: taciturn. Silent, "
                 "rude, angry, or talkative? Three: novice. Beginner, student, veteran, or novelist?",
            voice="default",
            subtitle=True,
            pause_after=10.0,
        )
        self.play(FadeIn(board[0]), FadeIn(head))
        for ln, (spoken, first_option) in zip(lines, [("curtail", "Extend"), ("taciturn", "Silent"),
                                                     ("novice", "Beginner")]):
            self.at_word(n, spoken)
            self.play(FadeIn(ln[:2], shift=UP * 0.15), run_time=0.4)
            self.at_word(n, first_option)
            self.play(FadeIn(ln[2], shift=LEFT * 0.15), run_time=0.4)
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        self.clear_stage()
        self.scene_end("S15_practice")

    # =============================================== 16. ANSWERS ==========

    def answers(self):
        self.scene_start("S16_answers", title="Answers")

        rows = VGroup()
        for w, opts, key, traps, note in self.PRACTICE:
            OptionQuestion(w, opts, key, traps)            # validates key / traps
            syn = [f"({l}) {opts['abcd'.index(l)]}" for l, r in traps.items() if r in ("synonym", "sound-alike")]
            rows.add(VGroup(pill(w, WORD, size=LABEL), text("↔", LABEL, MUTED),
                            pill(f"({key}) {opts['abcd'.index(key)]}", GOOD, size=LABEL), text(note, SMALL, INK),
                            text("traps: " + ", ".join(syn), SMALL, BAD)).arrange(RIGHT, buff=0.3))
        rows.arrange(DOWN, buff=0.5, aligned_edge=LEFT)
        fit_width(rows, SAFE_W).move_to(UP * 0.3)
        self.validator.check_in_frame(rows)

        n = self.narrate(
            id="answers_01",
            text="One: extend. Curtail means to cut short, so shorten and cut are synonyms. Two: talkative. Taciturn means "
                 "saying little, and silent is the synonym. Three: veteran. Beginner is the synonym, and novelist is a "
                 "sound-alike.",
            voice="default",
            subtitle=True,
        )
        for r, (spoken, meaning, trap) in zip(rows, [("extend", "Curtail", "shorten"), ("talkative", "Taciturn", "silent"),
                                                     ("veteran", "Beginner", "novelist")]):
            self.at_word(n, spoken)
            self.play(FadeIn(r[:3], shift=RIGHT * 0.2), run_time=0.4)
            self.at_word(n, meaning)
            self.play(FadeIn(r[3], shift=LEFT * 0.1), run_time=0.35)
            self.at_word(n, trap)
            self.play(FadeIn(r[4], shift=LEFT * 0.1), run_time=0.35)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S16_answers")

    # ================================================ 17. RECAP ==========

    def recap(self):
        self.scene_start("S17_recap", title="Recap Card")

        card, table = self.recap_card("Recap Card: Video 6", [
            ["Pairs of shelves", "one word gives you a synonym set and an antonym set"],
            ["Root pairs", " · ".join(f"{a} / {b}" for a, b, _ in ROOT_PAIRS)],
            ["Trap", "a same-shelf word (the synonym)"],
            ["Habit", "10 pairs a day, both shelves"],
        ])
        card.move_to(UP * 0.2)
        self.validator.check_in_frame(card)

        n = self.narrate(
            id="recap_01",
            text="To recap. Learn words as pairs of shelves, so one word gives you a synonym set and an antonym set. Know "
                 "the root pairs: bene and mal, pro and anti, pre and post, ascend and descend. The trap is a same-shelf "
                 "word: the synonym. And the habit: ten pairs a day, both shelves.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(card[0]), FadeIn(table[0]))
        for row, spoken in zip(table[1:], ["pairs", "root", "trap", "habit"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.45)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S17_recap")

    # ================================================= 18. NEXT ==========

    def next_video(self):
        self.scene_start("S18_next", title="Next")

        method = pill("one fast method", GOOD, size=BODY)
        reflex = pill("the reflex that beats the synonym trap", BAD, size=LABEL)
        nxt = pill("Next:  Antonym Question-Solving Techniques", FOCUS, size=LABEL)
        VGroup(method, reflex, nxt).arrange(DOWN, buff=0.7).move_to(UP * 0.2)
        self.no_overlap(method, reflex, nxt)
        self.validator.check_in_frame(VGroup(method, reflex, nxt))

        n = self.narrate(
            id="next_01",
            text="Video seven turns the lesson into one fast method, and trains the reflex that beats the synonym trap.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Video")
        self.play(FadeIn(nxt, scale=1.05))
        self.at_word(n, "method")
        self.play(FadeIn(method, shift=UP * 0.1))
        self.at_word(n, "reflex")
        self.play(FadeIn(reflex, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S18_next")

"""
animation.py for the LMS video generator.

Course : C-CAT - Section A - English
Module : Module 1 - Vocabulary
Lesson : Lesson 4 - One-Word Substitution
Video  : 05 - Exam-Oriented One-Word Substitutions (Video 5 of 6)

Source script:
  C:\\Users\\User\\Downloads\\C-CAT_SectionA_Module1_English\\English\\Module 1 - Vocabulary\\
  Lesson 4 - One-Word Substitution\\05 - Exam-Oriented One-Word Substitutions.pdf

Built on the golden-reference pattern:
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``;
  * layouts stacked with next_to and guarded with ``no_overlap``; nothing is
    ever animated onto or into another box.

The sixteen high-frequency substitutes live in EXAM as (definition, word, decode); the rules tables, worked examples and answers read their decodes from it.
The "word + decode" card (recall or decode, check every condition, strike look-alikes, confirm) stays pinned top-right through the worked examples and Hook, Solved.
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

# The script's Rules table: (definition, word, decode).
EXAM = [
    ("all agree", "unanimous", "one mind"),
    ("name not known", "anonymous", "without name"),
    ("after death", "posthumous", "post = after"),
    ("word for word", "verbatim", "verb = word"),
    ("speech without preparation", "extempore", "from the moment"),
    ("cure for all ills", "panacea", "pan = all"),
    ("cannot be corrected", "incorrigible", "not correctable"),
    ("cannot make mistakes", "infallible", "cannot fail"),
    ("cannot be avoided", "inevitable", "not avoidable"),
    ("living at the same time", "contemporary", "con (with) + tempus (time)"),
    ("unable to pay debts", "insolvent", "not solvent"),
    ("longing for the past", "nostalgia", "nostos = return home"),
    ("belief in one God", "monotheism", "mono + theo"),
    ("government by a few", "oligarchy", "oligo = few"),
    ("government by the wealthy", "plutocracy", "pluto = wealth"),
    ("someone who walks in sleep", "somnambulist", "somnus (sleep) + ambulare (walk)"),
]
DECODE = {word: decode for _d, word, decode in EXAM}
DEFINITION = {word: d for d, word, _x in EXAM}


class ExamOrientedSubstitutionsVideo(LMSScene):
    lesson_title = "Exam-Oriented One-Word Substitutions"

    def construct(self):
        self.camera.background_color = BG

        self.lesson_intro()
        self.hook()
        self.concept()
        self.why_you_need_it()
        self.analogy()
        self.example_posthumous()
        self.example_verbatim()
        self.example_panacea()
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

    def decode_pin(self):
        return self.steps_pin("word + decode", [("recall, or DECODE the roots", RATIO), ("check EVERY condition", WORD),
                                                ("strike look-alikes", BAD), ("confirm in a sentence", GOOD)])

    def minutes_card(self, fill=None):
        head = text("BOARD MEETING MINUTES", SMALL, RATIO, BOLD)
        draft = text("draft:  “The resolution was passed with every member voting in favour.”", LABEL, INK,
                     t2c={"with every member voting in favour": WORD})
        short = text(f"one word:  “The resolution was passed {fill or BLANK}.”", LABEL, INK,
                     t2c={fill or BLANK: GOOD if fill else FOCUS})
        cx, w = self.free_area()
        body = VGroup(head, draft, short).arrange(DOWN, buff=0.18, aligned_edge=LEFT)
        fit_width(body, min(w - 1.4, SAFE_W - 1.8))
        card = self.card(body, width=min(w - 0.2, SAFE_W - 0.4))
        return card.move_to(RIGHT * cx + UP * (CARD_TOP - card.height / 2))

    def decode_example(self, definition, word):
        """Definition, the decode from the Rules table, and the word."""
        cx, w = self.free_area()
        head = fitted_text(f"“{definition}”", w - 0.8, BODY, INK, NORMAL, max_lines=2)
        decode = VGroup(pill("decode", RATIO, size=SMALL), text(DECODE[word], BODY, RATIO)).arrange(RIGHT, buff=0.3)
        answer = VGroup(text("→", BODY, MUTED), pill(word, GOOD, size=TITLE)).arrange(RIGHT, buff=0.3)
        block = VGroup(head, decode, answer).arrange(DOWN, buff=0.6, aligned_edge=LEFT)
        fit_height(block, SAFE_H - 1.6)
        self.place_free(block, y=0.1)
        self.no_overlap(head, decode, answer)
        self.validator.check_in_frame(block)
        return head, decode, answer

    def exam_board(self, items):
        table = self.table_rows(["Definition", "Word", "Decode"], [list(i) for i in items], [4.4, 3.0, 4.6], size=LABEL)
        for row in table[1:]:
            row[1].set_color(GOOD)
            row[2].set_color(RATIO)
        board = self.card(table, width=SAFE_W - 0.2)
        fit_height(board, SAFE_H - 1.0)
        board.move_to(UP * 0.3)
        self.validator.check_in_frame(board)
        return board, table

    # ========================================= 0. LESSON INTRO ==========

    def lesson_intro(self):
        self.scene_start("S00_intro", title="Lesson Introduction")

        crumb = self.breadcrumb("English · Module 1 Vocabulary", "Lesson 4 · One-Word Substitution", "Video 5")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        earlier = VGroup(*[pill(t, MUTED, size=LABEL) for t in ["categories", "context", "confusable groups"]])\
            .arrange(RIGHT, buff=0.4)
        today = pill("today: the high-frequency set", BAD, size=LABEL)
        paired = pill("each word paired with a DECODE: remember by meaning, not rote", RATIO, size=LABEL)
        group = VGroup(earlier, today, paired).arrange(DOWN, buff=0.6)
        fit_width(group, SAFE_W).move_to(DOWN * 0.1)
        self.no_overlap(crumb, earlier, today, paired)
        self.validator.check_in_frame(VGroup(crumb, group))

        n = self.narrate(
            id="intro_01",
            text="Videos two to four gave you categories, context and confusable groups. Today's list is the "
                 "high-frequency set, each paired with a decode, so you remember it by meaning, not rote.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.at_word(n, "categories")
        self.play(LaggedStart(*[FadeIn(e, shift=UP * 0.1) for e in earlier], lag_ratio=0.3))
        self.at_word(n, "high-frequency")
        self.play(FadeIn(today, shift=UP * 0.1))
        self.at_word(n, "decode")
        self.play(FadeIn(paired, shift=UP * 0.1))
        self.wait_for_narration(n)

        title = fitted_text("Exam-Oriented One-Word Substitutions", SAFE_W, 64, INK, BOLD)
        underline = Line(LEFT, RIGHT, color=RATIO, stroke_width=5).set_width(title.width * 0.6)
        VGroup(title, underline).arrange(DOWN, buff=0.2).move_to(UP * 0.2)
        goals = [("Learn the one-word substitutes that recur most in exam papers", GOOD),
                 ("Decode each with its root, so recall is fast", RATIO)]
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
            text="These are the exam-oriented one-word substitutions. By the end of this video, you'll learn the "
                 "substitutes that recur most in exam papers, and decode each with its root, so recall is fast.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(group, shift=UP * 0.3))
        self.at_word(n, "exam-oriented")
        self.play(Write(title), run_time=1.1)
        self.play(GrowFromCenter(underline))
        self.at_word(n, "By")
        self.play(FadeOut(underline), ReplacementTransform(title, small_title), run_time=0.8)
        self.play(FadeIn(objectives[0]), FadeIn(heading))
        for row_, spoken in zip(rows, ["learn", "decode"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row_, shift=RIGHT * 0.2), run_time=0.5)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_intro")

    # ================================================= 1. HOOK ==========

    HOOK = dict(word=f"passed {BLANK}", options=["anonymously", "universally", "unanimously", "uniformly"], key="c",
                traps={"a": "look-alike:  = without a name", "b": "= everywhere, not agreement",
                       "d": "= in the same way"})

    def hook(self):
        self.scene_start("S01_hook", title="Hook")

        h = self.HOOK
        assert DEFINITION["unanimous"] == "all agree" and h["options"]["abcd".index(h["key"])] == "unanimously"
        minutes = self.minutes_card()
        q = OptionQuestion(h["word"], h["options"], h["key"], h["traps"])
        opts = q.rows.copy().arrange(RIGHT, buff=0.8)
        fit_width(opts, SAFE_W)
        ask = pill("which word?", FOCUS, size=LABEL)
        ask.next_to(minutes, DOWN, buff=0.5)
        opts.next_to(ask, DOWN, buff=0.6)
        self.no_overlap(minutes, ask, opts)
        self.validator.check_in_frame(VGroup(minutes, ask, opts))

        n = self.narrate(
            id="hook_01",
            text="You're writing board meeting minutes. The draft says: the resolution was passed, with every member "
                 "voting in favour. Your manager wants one word: the resolution was passed, blank.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "minutes")
        self.play(FadeIn(minutes[0]), FadeIn(minutes[1][0]))
        self.at_word(n, "draft")
        self.play(FadeIn(minutes[1][1], shift=UP * 0.1))
        self.at_word(n, "manager")
        self.play(FadeIn(minutes[1][2], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_02",
            text="Which word: anonymously, universally, unanimously, or uniformly?",
            voice="default",
            subtitle=True,
            pause_after=3.0,
        )
        self.at_word(n, "Which")
        self.play(FadeIn(ask, shift=UP * 0.1))
        for row, spoken in zip(opts, ["anonymously", "universally", "unanimously", "uniformly"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=UP * 0.15), run_time=0.35)
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        self.clear_stage()
        self.scene_end("S01_hook")

    # ============================================== 2. CONCEPT ==========

    def concept(self):
        self.scene_start("S02_concept", title="The Concept")

        pool = pill("a small pool of substitutes accounts for most exam questions", BAD, size=LABEL)
        fit_width(pool, SAFE_W)
        pool.move_to(UP * (CARD_TOP - pool.height / 2))
        formula = VGroup(pill("WORD", GOOD, size=BODY), text("+", BODY, MUTED), pill("DECODE", RATIO, size=BODY))\
            .arrange(RIGHT, buff=0.4)
        fastest = text("the fastest way to learn them", LABEL, MUTED)
        top = VGroup(formula, fastest).arrange(DOWN, buff=0.2)
        top.next_to(pool, DOWN, buff=0.9)
        self.no_overlap(pool, top)
        self.validator.check_in_frame(VGroup(pool, top))

        n = self.narrate(
            id="concept_01",
            text="A small pool of substitutes accounts for most exam questions. The fastest way to learn them is word plus "
                 "decode.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "pool")
        self.play(FadeIn(pool, shift=DOWN * 0.2))
        self.at_word(n, "fastest")
        self.play(FadeIn(fastest, shift=UP * 0.1))
        self.at_word(n, "word")
        self.play(FadeIn(formula[0], scale=1.1))
        self.at_word(n, "decode")
        self.play(FadeIn(formula[1:], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        # Three decodes.
        una = VGroup(pill("unanimous", GOOD, size=BODY), text("=", BODY, MUTED),
                     VGroup(pill("uni", RATIO, size=LABEL), text("one", SMALL, MUTED)).arrange(DOWN, buff=0.1),
                     text("+", LABEL, MUTED),
                     VGroup(pill("animus", RATIO, size=LABEL), text("mind", SMALL, MUTED)).arrange(DOWN, buff=0.1),
                     text("all of one mind", LABEL, INK)).arrange(RIGHT, buff=0.3)
        post = VGroup(pill("posthumous", GOOD, size=BODY), text("=", BODY, MUTED), text("after death", LABEL, INK))\
            .arrange(RIGHT, buff=0.3)
        verb = VGroup(pill("verbatim", GOOD, size=BODY), text("=", BODY, MUTED),
                      VGroup(pill("verbum", RATIO, size=LABEL), text("word", SMALL, MUTED)).arrange(DOWN, buff=0.1),
                      text("word for word", LABEL, INK)).arrange(RIGHT, buff=0.3)
        picture = pill("the decode turns each word into a small picture", FOCUS, size=LABEL)
        block = VGroup(una, post, verb, picture).arrange(DOWN, buff=0.5, aligned_edge=LEFT)
        fit_within(block, SAFE_W, SAFE_H - 1.4)
        block.move_to(UP * 0.3)
        self.no_overlap(una, post, verb, picture)
        self.validator.check_in_frame(block)
        n = self.narrate(
            id="concept_02",
            text="Unanimous: uni, one, plus animus, mind: all of one mind. Posthumous: after death. Verbatim: from verbum, "
                 "word: word for word. The decode turns each word into a small picture.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(VGroup(pool, top)))
        self.at_word(n, "Unanimous")
        self.play(FadeIn(una[:2], shift=RIGHT * 0.2))
        self.at_word(n, "uni")
        self.play(FadeIn(una[2:], shift=LEFT * 0.1))
        self.at_word(n, "Posthumous")
        self.play(FadeIn(post, shift=RIGHT * 0.2))
        self.at_word(n, "Verbatim")
        self.play(FadeIn(verb, shift=RIGHT * 0.2))
        self.at_word(n, "picture")
        self.play(FadeIn(picture, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_concept")

    # ======================================== 3. WHY YOU NEED IT ==========

    def why_you_need_it(self):
        self.scene_start("S03_why", title="Why You Need It")

        likely = pill("one or two substitution questions per paper: these words are the likely ones", BAD, size=LABEL)
        also = VGroup(pill("reading passages", WORD, size=LABEL), pill("formal writing", SECOND, size=LABEL))\
            .arrange(RIGHT, buff=0.6)
        group = VGroup(likely, also).arrange(DOWN, buff=0.9)
        fit_width(group, SAFE_W).move_to(UP * 0.3)
        self.no_overlap(likely, also)
        self.validator.check_in_frame(group)

        n = self.narrate(
            id="why_01",
            text="In a paper with one or two substitution questions, these words are the likely ones. They also appear in "
                 "reading passages and formal writing.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "likely")
        self.play(FadeIn(likely, shift=DOWN * 0.1))
        self.at_word(n, "passages")
        self.play(FadeIn(also[0], shift=UP * 0.1))
        self.at_word(n, "formal")
        self.play(FadeIn(also[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_why")

    # ============================================== 4. ANALOGY ==========

    def analogy(self):
        self.scene_start("S04_analogy", title="The Analogy")

        zipped = pill("unanimous.zip", MUTED, size=BODY)
        arrow = text("→  unzip  →", LABEL, RATIO)
        parts = VGroup(pill("uni = one", RATIO, size=LABEL), pill("animus = mind", RATIO, size=LABEL))\
            .arrange(DOWN, buff=0.25)
        row = VGroup(zipped, arrow, parts).arrange(RIGHT, buff=0.5)
        once = pill("unzip it once  →  recognise it every time", GOOD, size=LABEL)
        block = VGroup(row, once).arrange(DOWN, buff=0.9)
        fit_width(block, SAFE_W).move_to(UP * 0.3)
        self.no_overlap(zipped, parts)
        self.no_overlap(row, once)
        self.validator.check_in_frame(block)

        n = self.narrate(
            id="analogy_01",
            text="Each word is a compressed file. The decode unzips it into its parts. Once you've unzipped it once, "
                 "you'll recognise it every time.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "compressed")
        self.play(FadeIn(zipped, scale=1.1))
        self.at_word(n, "unzips")
        self.play(FadeIn(arrow), LaggedStart(*[FadeIn(p, shift=LEFT * 0.2) for p in parts], lag_ratio=0.4))
        self.at_word(n, "recognise")
        self.play(FadeIn(once, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_analogy")

    # ======================================== 5-7. WORKED EXAMPLES ==========

    def example_posthumous(self):
        self.scene_start("S05_ex_posthumous", title="Worked Example 1")
        self.play(self.pin(self.decode_pin()))

        head, decode, answer = self.decode_example("Published after the author's death", "posthumous")

        n = self.narrate(
            id="ex1_01",
            text="Published after the author's death. Post means after. So the word is posthumous.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Published")
        self.play(FadeIn(head, shift=DOWN * 0.1))
        self.at_word(n, "Post")
        self.play(FadeIn(decode, shift=RIGHT * 0.2), self.pin_step(0, color=RATIO))
        self.at_word(n, "posthumous")
        self.play(FadeIn(answer, scale=1.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_ex_posthumous")

    def example_verbatim(self):
        self.scene_start("S06_ex_verbatim", title="Worked Example 2")

        head, decode, answer = self.decode_example("Word for word", "verbatim")

        n = self.narrate(
            id="ex2_01",
            text="Word for word. Verb means word. So the answer is verbatim.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Word", occurrence=1)
        self.play(FadeIn(head, shift=DOWN * 0.1))
        self.at_word(n, "Verb")
        self.play(FadeIn(decode, shift=RIGHT * 0.2), self.pin_step(0, color=RATIO))
        self.at_word(n, "verbatim")
        self.play(FadeIn(answer, scale=1.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_ex_verbatim")

    def example_panacea(self):
        self.scene_start("S07_ex_panacea", title="Worked Example 3")

        head, decode, answer = self.decode_example("A remedy for all diseases or problems", "panacea")

        n = self.narrate(
            id="ex3_01",
            text="A remedy for all diseases or problems. Pan means all. So the word is panacea.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "remedy")
        self.play(FadeIn(head, shift=DOWN * 0.1))
        self.at_word(n, "Pan")
        self.play(FadeIn(decode, shift=RIGHT * 0.2), self.pin_step(0, color=RATIO))
        self.at_word(n, "panacea")
        self.play(FadeIn(answer, scale=1.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S07_ex_panacea")

    # ================================================ 8. RULES ==========

    def rules_first(self):
        self.scene_start("S08_rules_first", title="Rules: High-Frequency List (1)")
        self.play(self.unpin())

        board, table = self.exam_board(EXAM[:8])

        n = self.narrate(
            id="rules_01",
            text="Here is the high-frequency list. All agree: unanimous, one mind. Name not known: anonymous, without name. "
                 "After death: posthumous. Word for word: verbatim. Speech without preparation: extempore, from the "
                 "moment. Cure for all ills: panacea. Cannot be corrected: incorrigible. Cannot make mistakes: infallible.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "list")
        self.play(FadeIn(board[0]), FadeIn(table[0]))
        for row, spoken in zip(table[1:], ["unanimous", "anonymous", "posthumous", "verbatim", "extempore", "panacea",
                                           "incorrigible", "infallible"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.45)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S08_rules_first")

    def rules_second(self):
        self.scene_start("S09_rules_second", title="Rules: High-Frequency List (2)")

        board, table = self.exam_board(EXAM[8:])

        n = self.narrate(
            id="rules_02",
            text="Cannot be avoided: inevitable. Living at the same time: contemporary, con for with, tempus for time. "
                 "Unable to pay debts: insolvent. Longing for the past: nostalgia. Belief in one God: monotheism. "
                 "Government by a few: oligarchy. Government by the wealthy: plutocracy. And someone who walks in sleep: "
                 "a somnambulist.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(board[0]), FadeIn(table[0]))
        for row, spoken in zip(table[1:], ["inevitable", "contemporary", "insolvent", "nostalgia", "monotheism",
                                           "oligarchy", "plutocracy", "somnambulist"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.45)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S09_rules_second")

    # ============================================= 10. PROCESS ==========

    def process(self):
        self.scene_start("S10_process", title="The Process")

        steps = VGroup(*[VGroup(pill(str(i + 1), c, size=SMALL), fitted_text(s_, SAFE_W - 2.2, BODY, INK))
                         .arrange(RIGHT, buff=0.3) for i, (s_, c) in enumerate([
                             ("Recall the word, or decode the options' roots", RATIO),
                             ("Check every condition of the definition", WORD),
                             ("Strike look-alikes and same-root traps: anonymous / unanimous", BAD),
                             ("Confirm in a sentence", GOOD)])])
        steps.arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        board = self.card(steps).move_to(UP * 0.3)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="process_01",
            text="The process. First, recall the word, or decode the roots of the options. Second, check every condition "
                 "of the definition. Third, strike look-alikes and same-root traps, like anonymous and unanimous. And "
                 "fourth, confirm in a sentence.",
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
        cx, w = self.free_area()
        minutes = self.minutes_card()
        notes = VGroup(pill("every member in favour = all agree", WORD, size=SMALL),
                       pill("uni (one) + mind  →  unanimously", STEP_COLS["PREDICT"], size=SMALL)).arrange(RIGHT, buff=0.4)
        fit_width(notes, w - 0.6)
        notes.next_to(minutes, DOWN, buff=0.3).to_edge(LEFT, buff=SAFE + 0.6)
        q = OptionQuestion(h["word"], h["options"], h["key"], h["traps"], word_size=LABEL)
        fit_height(q.group, notes.get_bottom()[1] - 0.3 - (BOTTOM_Y + 0.6))
        q.group.next_to(notes, DOWN, buff=0.3).to_edge(LEFT, buff=SAFE + 0.6)
        fixed = self.minutes_card(fill="unanimously")
        self.no_overlap(minutes, notes, q.group)
        self.no_overlap(minutes, self.pinned)
        self.no_overlap(notes, self.pinned)
        self.validator.check_in_frame(VGroup(minutes, notes, q.group))

        n = self.narrate(
            id="solved_01",
            text="Let's solve the hook. Read: every member voting in favour means all agree. Predict: uni, one, plus mind: "
                 "unanimously.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(minutes), FadeIn(q.word), FadeIn(q.rows))
        self.at_word(n, "Read")
        self.play(FadeIn(notes[0], shift=UP * 0.1), self.pin_step(1, color=WORD))
        self.at_word(n, "Predict")
        self.play(FadeIn(notes[1], shift=LEFT * 0.1), self.pin_step(0, color=RATIO))
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_02",
            text="Eliminate. Anonymously means without a name: a look-alike. Universally means everywhere, not agreement. "
                 "Uniformly means in the same way.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Eliminate")
        self.play(self.pin_step(2, color=BAD))
        for letter, spoken in [("a", "Anonymously"), ("b", "Universally"), ("d", "Uniformly")]:
            self.at_word(n, spoken)
            self.play(*q.strike(letter)[1])
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_03",
            text="Confirm: the resolution was passed unanimously. That's the answer.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Confirm")
        self.play(ReplacementTransform(minutes, fixed), self.pin_step(3, color=GOOD))
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
            ["Known high-frequency word", "recall with decode; strike look-alikes"],
            ["Unknown word", "decode roots of each option; check conditions"],
            ["Rule by … (-cracy / -archy)", "decode the first root: pluto (wealth), oligo (few), theo (god)"],
        ], [4.8, 7.0], size=LABEL)
        board = self.card(table, width=SAFE_W - 0.2).move_to(UP * 0.4)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="patterns_01",
            text="Three exam patterns. A known high-frequency word: recall it with its decode, and strike look-alikes. An "
                 "unknown word: decode the roots of each option, and check the conditions. And rule-by words, ending in "
                 "cracy or archy: decode the first root: pluto for wealth, oligo for few, theo for god.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(board[0]), FadeIn(table[0]))
        for row, spoken in zip(table[1:], ["known", "unknown", "rule-by"]):
            self.at_word(n, spoken, occurrence=1)
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.45)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S12_patterns")

    # ======================================== 13. COMMON MISTAKES ==========

    def common_mistakes(self):
        self.scene_start("S13_mistakes", title="Common Mistakes")

        card_w = ZONE_W - 0.3
        pairs = [
            (self.verdict_card(False, "anonymous = unanimous", card_w),
             self.verdict_card(True, "without name  vs  one mind", card_w)),
            (self.verdict_card(False, "contemporary = modern", card_w),
             self.verdict_card(True, "contemporary: at the SAME time", card_w)),
            (self.verdict_card(False, "Guessing -cracy words from sound", card_w),
             self.verdict_card(True, "Decode the first root", card_w)),
        ]
        for (wrong, right), yy in zip(pairs, [1.6, 0.05, -1.5]):
            wrong.move_to(LEFT_ZONE + UP * yy)
            right.move_to(RIGHT_ZONE + UP * yy)
        header = pill("3 mistakes", BAD, size=LABEL).move_to(UP * (CARD_TOP - 0.3))
        self.validator.check_in_frame(VGroup(header, *[c for p in pairs for c in p]))

        n = self.narrate(
            id="mistakes_01",
            text="Three common mistakes. The first is confusing anonymous and unanimous. The second is confusing "
                 "contemporary, which means at the same time, with modern. The third is guessing cracy words from their "
                 "sound.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(header))
        for pr, spoken in zip(pairs, ["first", "second", "third"]):
            self.at_word(n, spoken)
            self.play(FadeIn(pr[0], shift=RIGHT * 0.3), FadeIn(pr[1], shift=LEFT * 0.3))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S13_mistakes")

    # ============================================== 14. PRACTICE ==========

    PRACTICE = [
        ("Government by the wealthy", ["aristocracy", "plutocracy", "autocracy", "democracy"], "b",
         "(a) aristocracy: rule by nobles;  (c) autocracy: rule by one person"),
        ("A person unable to pay debts", ["insolvent", "miser", "spendthrift", "debtor"], "a",
         "(d) a debtor owes money but may be able to pay;  (c) a spendthrift spends wastefully"),
        ("Something that cannot be corrected", ["incurable", "irreversible", "inevitable", "incorrigible"], "d",
         "(a) incurable: for diseases;  (b) irreversible: for processes"),
    ]

    def practice(self):
        self.scene_start("S14_practice", title="Practice Questions")

        head = pill("One word for the phrase?", GOOD, size=LABEL)
        lines = VGroup(*[VGroup(VGroup(pill(str(i + 1), FOCUS, size=SMALL), text(f"“{phrase}”", LABEL, WORD))
                                .arrange(RIGHT, buff=0.35),
                                text("   ".join(f"({l}) {o}" for l, o in zip("abcd", opts)), LABEL, INK))
                         .arrange(DOWN, buff=0.2, aligned_edge=LEFT)
                         for i, (phrase, opts, *_r) in enumerate(self.PRACTICE)])
        lines.arrange(DOWN, buff=0.4, aligned_edge=LEFT)
        board = self.card(VGroup(head, lines).arrange(DOWN, buff=0.4, aligned_edge=LEFT), color=FOCUS)
        fit_within(board, SAFE_W, SAFE_H - 1.2)
        board.move_to(UP * 0.4)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="practice_01",
            text="Your turn. One: government by the wealthy. Aristocracy, plutocracy, autocracy, or democracy? Two: a "
                 "person unable to pay debts. Insolvent, miser, spendthrift, or debtor? Three: something that cannot be "
                 "corrected. Incurable, irreversible, inevitable, or incorrigible?",
            voice="default",
            subtitle=True,
            pause_after=10.0,
        )
        self.play(FadeIn(board[0]), FadeIn(head))
        for ln, (spoken, first_option) in zip(lines, [("wealthy", "Aristocracy"), ("debts", "Insolvent"),
                                                     ("corrected", "Incurable")]):
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
        for phrase, opts, key, why in self.PRACTICE:
            word = opts["abcd".index(key)]
            rows.add(VGroup(VGroup(text(f"“{phrase}”", LABEL, INK), text("→", LABEL, MUTED),
                                   pill(f"({key}) {word}", GOOD, size=LABEL), pill(DECODE[word], RATIO, size=SMALL))
                            .arrange(RIGHT, buff=0.3), text(why, SMALL, BAD)).arrange(DOWN, buff=0.18, aligned_edge=LEFT))
        rows.arrange(DOWN, buff=0.5, aligned_edge=LEFT)
        fit_within(rows, SAFE_W, SAFE_H - 1.2)
        rows.move_to(UP * 0.3)
        self.validator.check_in_frame(rows)

        n = self.narrate(
            id="answers_01",
            text="One: plutocracy. Aristocracy is rule by nobles, and autocracy is rule by one person. Two: insolvent. A "
                 "debtor owes money, but may be able to pay; a spendthrift spends wastefully. Three: incorrigible. "
                 "Incurable is for diseases, and irreversible is for processes.",
            voice="default",
            subtitle=True,
        )
        for r, (spoken, why) in zip(rows, [("plutocracy", "nobles"), ("insolvent", "debtor"),
                                           ("incorrigible", "diseases")]):
            self.at_word(n, spoken)
            self.play(FadeIn(r[0], shift=RIGHT * 0.2), run_time=0.5)
            self.at_word(n, why)
            self.play(FadeIn(r[1], shift=LEFT * 0.1), run_time=0.4)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S15_answers")

    # ================================================ 16. RECAP ==========

    def recap(self):
        self.scene_start("S16_recap", title="Recap Card")

        card, table = self.recap_card("Recap Card: Video 5", [
            ["Learn as word + decode", "unanimous (one mind), posthumous (after death), verbatim (word for word)"],
            ["Rule words", "pluto (wealth), oligo (few), auto (self), theo (god)"],
            ["Watch", "anonymous ≠ unanimous"],
        ])
        card.move_to(UP * 0.2)
        self.validator.check_in_frame(card)

        n = self.narrate(
            id="recap_01",
            text="To recap. Learn each word with its decode: unanimous, one mind; posthumous, after death; verbatim, word "
                 "for word. Know the rule words: pluto for wealth, oligo for few, auto for self, theo for god. And watch "
                 "out: anonymous is not unanimous.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(card[0]), FadeIn(table[0]))
        for row, spoken in zip(table[1:], ["decode", "rule", "watch"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.45)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S16_recap")

    # ================================================= 17. NEXT ==========

    def next_video(self):
        self.scene_start("S17_next", title="Next")

        method = pill("one method for any substitution question", GOOD, size=LABEL)
        unknown = pill("even when you don't know the word", RATIO, size=LABEL)
        nxt = pill("Next:  Question-Solving Techniques", FOCUS, size=LABEL)
        VGroup(method, unknown, nxt).arrange(DOWN, buff=0.7).move_to(UP * 0.2)
        self.no_overlap(method, unknown, nxt)
        self.validator.check_in_frame(VGroup(method, unknown, nxt))

        n = self.narrate(
            id="next_01",
            text="Video six gives you one method for any substitution question, even when you don't know the word.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Video")
        self.play(FadeIn(nxt, scale=1.05))
        self.at_word(n, "method")
        self.play(FadeIn(method, shift=UP * 0.1))
        self.at_word(n, "even")
        self.play(FadeIn(unknown, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S17_next")

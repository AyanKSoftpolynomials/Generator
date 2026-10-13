"""
animation.py for the LMS video generator.

Course : C-CAT - Section A - English
Module : Module 1 - Vocabulary
Lesson : Lesson 3 - Idioms & Phrases
Video  : 01 - Introduction to Idioms (Video 1 of 7)

Source script:
  C:\\Users\\User\\Downloads\\C-CAT_SectionA_Module1_English\\English\\Module 1 - Vocabulary\\
  Lesson 3 - Idioms & Phrases\\01 - Introduction to Idioms.pdf

Built on the golden-reference pattern:
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``;
  * layouts stacked with next_to and guarded with ``no_overlap``; nothing is
    ever animated onto or into another box.

First video of Lesson 3: the intro recaps Lessons 1-2 (single words) and announces the new lesson.
Each idiom's picture and idea live in IDIOMS; every worked example and practice answer is asserted against it.
The "idiom method" card (picture, idea, strike the literal option, confirm) stays pinned top-right through the worked examples and Hook, Solved.
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

# idiom -> (the picture it starts from, the idea it stands for)
IDIOMS = {
    "break the ice": ("ice between two people", "start a conversation in an awkward setting"),
    "spill the beans": ("beans spilling out", "reveal a secret"),
    "back to the drawing board": ("the board where designs begin", "start again"),
    "hit the nail on the head": ("one clean strike, right on target", "describe something exactly right"),
    "once in a blue moon": ("a blue moon: a rare sight", "very rarely"),
    "burn the midnight oil": ("a lamp still burning at midnight", "work late into the night"),
    "cost an arm and a leg": ("paying with an arm and a leg", "be very expensive"),
}


def picture_idea(idiom, size=SMALL):
    """picture → idea chips for one idiom."""
    picture, idea = IDIOMS[idiom]
    return VGroup(pill("picture:  " + picture, WORD, size=size), text("→", size, MUTED),
                  pill("idea:  " + idea, GOOD, size=size)).arrange(RIGHT, buff=0.2)


class IntroductionToIdiomsVideo(LMSScene):
    lesson_title = "Introduction to Idioms"

    def construct(self):
        self.camera.background_color = BG

        self.lesson_intro()
        self.hook()
        self.concept()
        self.why_you_need_it()
        self.analogy()
        self.example_ice()
        self.example_nail()
        self.example_moon()
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

    def method_pin(self):
        return self.steps_pin("idiom method", [("see the PICTURE", WORD), ("state the IDEA", STEP_COLS["PREDICT"]),
                                               ("strike the literal option", BAD), ("confirm in a sentence", GOOD)])

    def chat_card(self, fill=None):
        head = text("TEAM CHANNEL  ·  from your lead", SMALL, RATIO, BOLD)
        first = text("“Client rejected the design.", LABEL, INK)
        second = text(f"We're {fill}.”" if fill else "We're going back to the drawing board.”", LABEL, INK,
                      t2c={fill or "drawing board": GOOD if fill else WORD})
        cx, w = self.free_area()
        body = VGroup(head, first, second).arrange(DOWN, buff=0.18, aligned_edge=LEFT)
        fit_width(body, w - 1.4)
        card = self.card(body, width=min(w - 0.2, SAFE_W - 0.4))
        return card.move_to(RIGHT * cx + UP * (CARD_TOP - card.height / 2))

    def idiom_question(self, idiom, options, key, traps):
        """Idiom + options at the left, its picture → idea chips underneath, beside the pinned panel."""
        assert options["abcd".index(key)] == IDIOMS[idiom][1]
        q = OptionQuestion(f"“{idiom.capitalize()}”", options, key, traps, word_size=BODY)
        note = picture_idea(idiom)
        cx, w = self.free_area()
        fit_width(note, w - 1.0)
        block = VGroup(q.group, note).arrange(DOWN, buff=0.45, aligned_edge=LEFT)
        fit_height(block, SAFE_H - 1.6)
        block.to_edge(LEFT, buff=SAFE + 0.6).set_y(0.2)
        self.no_overlap(q.group, note)
        self.no_overlap(block, self.pinned)
        self.validator.check_in_frame(block)
        return q, note

    # ========================================= 0. LESSON INTRO ==========
    # First video of a NEW LESSON: silent trail, a one-line recap of Lessons 1-2
    # (single words), one line that Lesson 3 starts, the title and objectives.

    def lesson_intro(self):
        self.scene_start("S00_intro", title="Lesson Introduction")

        crumb = self.breadcrumb("English · Module 1 Vocabulary", "Lesson 3 · Idioms & Phrases", "Video 1")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        last = pill("Lessons 1 and 2: single words", MUTED, size=SMALL)
        words = VGroup(pill("synonym:  same meaning", GOOD, size=LABEL), pill("antonym:  opposite meaning", BAD,
                                                                             size=LABEL)).arrange(RIGHT, buff=0.5)
        VGroup(last, words).arrange(DOWN, buff=0.5).move_to(UP * 0.6)
        parts = VGroup(pill("break", WORD, size=LABEL), text("+", LABEL, MUTED), pill("the", WORD, size=LABEL),
                       text("+", LABEL, MUTED), pill("ice", WORD, size=LABEL), text("≠", BODY, BAD),
                       pill("breaking ice", MUTED, size=LABEL)).arrange(RIGHT, buff=0.25)
        parts.next_to(words, DOWN, buff=0.7)
        self.no_overlap(crumb, last, words, parts)
        self.validator.check_in_frame(VGroup(crumb, last, words, parts))

        n = self.narrate(
            id="intro_01",
            text="In lessons one and two, you worked with single words: synonyms and antonyms.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.at_word(n, "single")
        self.play(FadeIn(last))
        self.at_word(n, "synonyms")
        self.play(LaggedStart(*[FadeIn(w, shift=UP * 0.1) for w in words], lag_ratio=0.4))
        self.wait_for_narration(n)

        n = self.narrate(
            id="intro_02",
            text="Now we start lesson three, idioms and phrases. Idioms are groups of words that act like a single word, "
                 "with a meaning you can't get by adding up the parts.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "lesson")
        self.play(Indicate(crumb[2], color="#F48FB1", scale_factor=1.1))
        self.at_word(n, "groups")
        self.play(FadeIn(parts[:5], shift=UP * 0.1))
        self.at_word(n, "adding")
        self.play(FadeIn(parts[5:], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        title = fitted_text("Introduction to Idioms", SAFE_W, 72, INK, BOLD)
        underline = Line(LEFT, RIGHT, color=SECOND, stroke_width=5).set_width(title.width * 0.6)
        VGroup(title, underline).arrange(DOWN, buff=0.2).move_to(UP * 0.2)
        goals = [
            ("Explain what an idiom is, and why its literal meaning is a trap", BAD),
            ("Solve a basic idiom-meaning question with the four-step method", GOOD),
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
            text="This is the introduction to idioms. By the end of this video, you'll be able to explain what an idiom is "
                 "and why its literal meaning is a trap, and you'll solve a basic idiom-meaning question with the "
                 "four-step method.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(VGroup(last, words, parts), shift=UP * 0.3))
        self.at_word(n, "introduction")
        self.play(Write(title), run_time=1.1)
        self.play(GrowFromCenter(underline))
        self.at_word(n, "By")
        self.play(FadeOut(underline), ReplacementTransform(title, small_title), run_time=0.8)
        self.play(FadeIn(objectives[0]), FadeIn(heading))
        for row_, spoken in zip(rows, ["explain", "solve"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row_, shift=RIGHT * 0.2), run_time=0.5)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_intro")

    # ================================================= 1. HOOK ==========

    HOOK = dict(word="drawing board", options=["Designing a new logo", "Returning to the office",
                                               "Reviewing the old drawings", "Starting the plan again from scratch"],
                key="d", traps={"a": "literal: drawing", "b": "board ≠ a place", "c": "literal: drawing"})

    def hook(self):
        self.scene_start("S01_hook", title="Hook")

        h = self.HOOK
        chat = self.chat_card()
        q = OptionQuestion(h["word"], h["options"], h["key"], h["traps"])
        opts = q.rows.copy().arrange_in_grid(rows=2, cols=2, buff=(1.0, 0.35), cell_alignment=LEFT)
        fit_width(opts, SAFE_W)
        ask = pill("a new teammate: “What does that mean for my week?”", FOCUS, size=LABEL)
        ask.next_to(chat, DOWN, buff=0.5)
        opts.next_to(ask, DOWN, buff=0.5)
        self.no_overlap(chat, ask, opts)
        self.validator.check_in_frame(VGroup(chat, ask, opts))

        n = self.narrate(
            id="hook_01",
            text="After a tough client call, your lead posts: Client rejected the design. We're going back to the drawing "
                 "board. A new teammate asks what that means for his week.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "posts")
        self.play(FadeIn(chat[0]), FadeIn(chat[1][0]), FadeIn(chat[1][1], shift=UP * 0.1))
        self.at_word(n, "going")
        self.play(FadeIn(chat[1][2], shift=UP * 0.1))
        self.at_word(n, "teammate")
        self.play(FadeIn(ask, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_02",
            text="What does it mean? Designing a new logo, returning to the office, reviewing the old drawings, or starting "
                 "the plan again from scratch?",
            voice="default",
            subtitle=True,
            pause_after=3.0,
        )
        self.at_word(n, "mean")
        self.play(Indicate(chat[1][2], color=WORD, scale_factor=1.03))
        for row, spoken in zip(opts, ["Designing", "returning", "reviewing", "starting"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=UP * 0.15), run_time=0.35)
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        self.clear_stage()
        self.scene_end("S01_hook")

    # ============================================== 2. CONCEPT ==========

    def concept(self):
        self.scene_start("S02_concept", title="The Concept")

        head = pill("idiom:  a fixed expression  ·  meaning ≠ its literal words", SECOND, size=LABEL)
        fit_width(head, SAFE_W)
        head.move_to(UP * (CARD_TOP - head.height / 2))
        rows = VGroup(*[VGroup(pill(f"“{idiom}”", WORD, size=LABEL), text("not about " + literal, LABEL, BAD),
                               text("=  " + IDIOMS[idiom][1], LABEL, GOOD)).arrange(DOWN, buff=0.18, aligned_edge=LEFT)
                        for idiom, literal in [("break the ice", "ice"), ("spill the beans", "beans")]])
        rows.arrange(DOWN, buff=0.5, aligned_edge=LEFT)
        fit_within(rows, SAFE_W, SAFE_H - head.height - 1.4)
        rows.next_to(head, DOWN, buff=0.5)
        self.no_overlap(head, rows)
        self.validator.check_in_frame(VGroup(head, rows))

        n = self.narrate(
            id="concept_01",
            text="An idiom is a fixed expression whose meaning differs from the literal meanings of its words. Break the "
                 "ice has nothing to do with ice; it means to start a conversation in an awkward situation. Spill the "
                 "beans means to reveal a secret.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "idiom")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "Break")
        self.play(FadeIn(rows[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "nothing")
        self.play(FadeIn(rows[0][1], shift=UP * 0.1))
        self.at_word(n, "conversation")
        self.play(FadeIn(rows[0][2], shift=UP * 0.1))
        self.at_word(n, "Spill")
        self.play(FadeIn(rows[1][0], shift=RIGHT * 0.2), FadeIn(rows[1][1]))
        self.at_word(n, "reveal")
        self.play(FadeIn(rows[1][2], shift=UP * 0.1))
        self.wait_for_narration(n)

        # Picture → idea.
        chain = VGroup(pill("PICTURE", WORD, size=BODY), text("→", TITLE, MUTED), pill("IDEA", GOOD, size=BODY))\
            .arrange(RIGHT, buff=0.5)
        sub = VGroup(text("something physical, easy to imagine", SMALL, WORD),
                     text("what the picture became shorthand for", SMALL, GOOD))
        board_ = VGroup(pill("“back to the drawing board”", SECOND, size=LABEL),
                        picture_idea("back to the drawing board", size=LABEL)).arrange(DOWN, buff=0.3)
        block = VGroup(chain, board_).arrange(DOWN, buff=1.1)
        fit_width(block, SAFE_W).move_to(UP * 0.4)
        sub[0].next_to(chain[0], DOWN, buff=0.15)
        sub[1].next_to(chain[2], DOWN, buff=0.15)
        if sub[0].get_right()[0] + 0.2 > sub[1].get_left()[0]:
            sub[0].align_to(chain[0], RIGHT)
            sub[1].align_to(chain[2], LEFT)
        self.no_overlap(sub[0], sub[1])
        self.no_overlap(VGroup(chain, sub), board_)
        self.validator.check_in_frame(VGroup(block, sub))
        n = self.narrate(
            id="concept_02",
            text="Idioms usually start from a picture: something physical that everyone could imagine. Over time, that "
                 "picture became a shorthand for an idea. Back to the drawing board pictures an engineer going back to "
                 "the board where the design began. The idea: start over.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(VGroup(head, rows)))
        self.at_word(n, "picture", occurrence=1)
        self.play(FadeIn(chain[0], scale=1.1), FadeIn(sub[0]))
        self.at_word(n, "shorthand")
        self.play(FadeIn(chain[1]), FadeIn(chain[2], shift=LEFT * 0.2), FadeIn(sub[1]))
        self.at_word(n, "engineer")
        self.play(FadeIn(board_[0], shift=UP * 0.1), FadeIn(board_[1][0], shift=UP * 0.1))
        self.at_word(n, "over", occurrence=2)
        self.play(FadeIn(board_[1][1:], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        trap = VGroup(pill("most common wrong option:  the LITERAL reading", BAD, size=BODY),
                      text("it describes the picture, not the idea", LABEL, MUTED),
                      pill("your job:  see the picture  →  jump to what it stands for", GOOD, size=LABEL))\
            .arrange(DOWN, buff=0.5)
        fit_width(trap, SAFE_W).move_to(UP * 0.3)
        self.validator.check_in_frame(trap)
        n = self.narrate(
            id="concept_03",
            text="That's why the most common wrong option in idiom questions is the literal reading: the answer that "
                 "describes the picture, not the idea. Your job is to see the picture, then make the jump to what it "
                 "stands for.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(VGroup(chain, sub, board_)))
        self.at_word(n, "literal")
        self.play(FadeIn(trap[0], scale=1.05))
        self.at_word(n, "describes")
        self.play(FadeIn(trap[1], shift=UP * 0.1))
        self.at_word(n, "job")
        self.play(FadeIn(trap[2], shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_concept")

    # ======================================== 3. WHY YOU NEED IT ==========

    def why_you_need_it(self):
        self.scene_start("S03_why", title="Why You Need It")

        exam = pill("C-CAT and placement tests:  “Choose the meaning of the idiom”", BAD, size=LABEL)
        work = VGroup(*[pill(t, WORD, size=LABEL) for t in ["meetings", "emails", "chats"]]).arrange(RIGHT, buff=0.5)
        miss = pill("miss the idiom  →  miss the message", FOCUS, size=LABEL)
        group = VGroup(exam, work, miss).arrange(DOWN, buff=0.7)
        fit_width(group, SAFE_W).move_to(UP * 0.3)
        self.no_overlap(exam, work, miss)
        self.validator.check_in_frame(group)

        n = self.narrate(
            id="why_01",
            text="Idiom questions appear regularly in C-CAT and placement tests, usually as: choose the meaning of the "
                 "idiom. Idioms are also everywhere in workplace English: in meetings, emails and chats. Missing one means "
                 "missing the message.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "regularly")
        self.play(FadeIn(exam, shift=DOWN * 0.1))
        self.at_word(n, "meetings")
        self.play(LaggedStart(*[FadeIn(w, shift=UP * 0.1) for w in work], lag_ratio=0.3))
        self.at_word(n, "Missing")
        self.play(FadeIn(miss, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_why")

    # ============================================== 4. ANALOGY ==========

    def analogy(self):
        self.scene_start("S04_analogy", title="The Analogy")

        centre = LEFT * 3.4 + UP * 0.3
        plate = Triangle(color=BAD, stroke_width=10).scale(1.9).move_to(centre)
        slope = Line(centre + LEFT * 0.75 + DOWN * 0.75, centre + RIGHT * 0.15 + UP * 0.35, color=INK, stroke_width=5)
        rocks = VGroup(*[Dot(centre + RIGHT * x + DOWN * y, radius=r, color=INK)
                         for x, y, r in [(0.35, 0.05, 0.11), (0.55, 0.4, 0.14), (0.2, 0.55, 0.09)]])
        post = Line(plate.get_bottom(), plate.get_bottom() + DOWN * 1.1, color=MUTED, stroke_width=8)
        sign = VGroup(plate, slope, rocks, post)
        tags = VGroup(pill("the drawing: falling rocks", MUTED, size=LABEL),
                      pill("the message: slow down, danger ahead", GOOD, size=LABEL),
                      pill("idiom:  read the MESSAGE, not the drawing", FOCUS, size=LABEL))\
            .arrange(DOWN, buff=0.5, aligned_edge=LEFT)
        fit_width(tags, 6.4)
        tags.move_to(RIGHT * 2.9 + UP * 0.2)
        self.no_overlap(sign, tags)
        self.validator.check_in_frame(VGroup(sign, tags))

        n = self.narrate(
            id="analogy_01",
            text="An idiom is like a road sign. The picture of falling rocks isn't asking you to look at rocks; it means "
                 "slow down, danger ahead. Read the sign for its message, not its drawing.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "road")
        self.play(Create(plate), Create(post))
        self.at_word(n, "falling")
        self.play(Create(slope), FadeIn(rocks, shift=DOWN * 0.2), FadeIn(tags[0], shift=LEFT * 0.1))
        self.at_word(n, "slow")
        self.play(FadeIn(tags[1], shift=LEFT * 0.1))
        self.at_word(n, "Read")
        self.play(FadeIn(tags[2], shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_analogy")

    # ======================================== 5-7. WORKED EXAMPLES ==========

    def example_ice(self):
        self.scene_start("S05_ex_ice", title="Worked Example 1")
        self.play(self.pin(self.method_pin()))

        q, note = self.idiom_question("break the ice", ["smash frozen water", "start a conversation in an awkward setting",
                                                        "end a friendship", "cool down"], "b",
                                      {"a": "literal", "c": "not the idea", "d": "literal: ice"})

        n = self.narrate(
            id="ex1_01",
            text="Break the ice. Smash frozen water, start a conversation in an awkward setting, end a friendship, or cool "
                 "down? The picture: ice between two people. The idea: get the conversation started. Smash frozen water "
                 "is the literal reading, so strike it. End a friendship and cool down miss the idea. The answer is: "
                 "start a conversation in an awkward setting.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(q.word, scale=1.1))
        self.at_word(n, "Smash", occurrence=1)
        self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.2) for r in q.rows], lag_ratio=0.2))
        self.at_word(n, "picture")
        self.play(FadeIn(note[0], shift=UP * 0.1), self.pin_step(0, color=WORD))
        self.at_word(n, "idea", occurrence=1)
        self.play(FadeIn(note[1:], shift=LEFT * 0.1), self.pin_step(1, color=STEP_COLS["PREDICT"]))
        self.at_word(n, "literal")
        self.play(*q.strike("a")[1], self.pin_step(2, color=BAD))
        self.at_word(n, "End", occurrence=2)
        self.play(*q.strike("c")[1], *q.strike("d")[1])
        self.at_word(n, "answer")
        self.play(*q.confirm()[1])
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_ex_ice")

    def example_nail(self):
        self.scene_start("S06_ex_nail", title="Worked Example 2")

        q, note = self.idiom_question("hit the nail on the head", ["do carpentry", "hurt someone",
                                                                   "describe something exactly right", "work hard"], "c",
                                      {"a": "literal", "b": "literal: hit", "d": "not the idea"})

        n = self.narrate(
            id="ex2_01",
            text="Hit the nail on the head. Do carpentry, hurt someone, describe something exactly right, or work hard? "
                 "The picture: one clean strike, right on target. The idea: exactly right. Carpentry is the literal "
                 "reading. Hurting someone and working hard miss the idea. The answer is: describe something exactly "
                 "right.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(q.word, scale=1.1))
        self.at_word(n, "Do")
        self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.2) for r in q.rows], lag_ratio=0.2))
        self.at_word(n, "picture")
        self.play(FadeIn(note[0], shift=UP * 0.1), self.pin_step(0, color=WORD))
        self.at_word(n, "idea", occurrence=1)
        self.play(FadeIn(note[1:], shift=LEFT * 0.1), self.pin_step(1, color=STEP_COLS["PREDICT"]))
        self.at_word(n, "literal")
        self.play(*q.strike("a")[1], self.pin_step(2, color=BAD))
        self.at_word(n, "Hurting")
        self.play(*q.strike("b")[1], *q.strike("d")[1])
        self.at_word(n, "answer")
        self.play(*q.confirm()[1])
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_ex_nail")

    def example_moon(self):
        self.scene_start("S07_ex_moon", title="Worked Example 3")

        q, note = self.idiom_question("once in a blue moon", ["at night", "very rarely", "every month", "never"], "b",
                                      {"a": "literal", "c": "too often", "d": "goes too far"})

        n = self.narrate(
            id="ex3_01",
            text="Once in a blue moon. At night, very rarely, every month, or never? The picture: a blue moon is a rare "
                 "sight. The idea: very rarely. Never goes too far: rare still happens. At night is literal, and every "
                 "month is too often. The answer is very rarely.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(q.word, scale=1.1))
        self.at_word(n, "At", occurrence=1)
        self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.2) for r in q.rows], lag_ratio=0.2))
        self.at_word(n, "picture")
        self.play(FadeIn(note[0], shift=UP * 0.1), self.pin_step(0, color=WORD))
        self.at_word(n, "idea")
        self.play(FadeIn(note[1:], shift=LEFT * 0.1), self.pin_step(1, color=STEP_COLS["PREDICT"]))
        self.at_word(n, "Never", occurrence=2)
        self.play(*q.strike("d")[1], self.pin_step(2, color=BAD))
        self.at_word(n, "literal")
        self.play(*q.strike("a")[1], *q.strike("c")[1])
        self.at_word(n, "answer")
        self.play(*q.confirm()[1])
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S07_ex_moon")

    # ================================================ 8. RULES ==========

    def rules(self):
        self.scene_start("S08_rules", title="Rules")
        self.play(self.unpin())

        rules = VGroup(*[VGroup(pill(str(i + 1), c, size=SMALL), fitted_text(s_, SAFE_W - 2.2, BODY, INK))
                         .arrange(RIGHT, buff=0.3) for i, (s_, c) in enumerate([
                             ("Idioms are FIGURATIVE: the literal option is almost always a trap", BAD),
                             ("Idioms are FIXED: their words can't be changed", WORD),
                             ("Start from the picture, then ask: what idea does it represent?", SECOND),
                             ("Match the DEGREE: “rarely” is not “never”", GOOD)])])
        rules.arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        board = self.card(rules).move_to(UP * 0.3)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="rules_01",
            text="Four rules. First, idioms are figurative: the literal option is almost always a trap. Second, idioms are "
                 "fixed: their words can't be changed. Third, start from the picture, then ask what idea it represents. "
                 "And fourth, match the degree: rarely is not never.",
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
                               "identify the idiom, and any sentence around it",
                               "see the picture, then state the idea in plain words",
                               "the literal option, opposites, and “too far” options",
                               "replace the idiom in a sentence with your answer"])])
        details.arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        board = self.card(details)
        board.next_to(strip, DOWN, buff=0.5)
        self.no_overlap(strip, board)
        self.validator.check_in_frame(VGroup(strip, board))

        n = self.narrate(
            id="process_01",
            text="The process. Read: identify the idiom, and any sentence around it. Predict: see the picture, then state "
                 "the idea in plain words. Eliminate: remove the literal option, opposites, and options that go too far. "
                 "And confirm: replace the idiom in a sentence with your answer.",
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
        self.play(self.pin(self.method_pin()))

        h = self.HOOK
        assert IDIOMS["back to the drawing board"][1] == "start again"
        chat = self.chat_card()
        q = OptionQuestion(h["word"], h["options"], h["key"], h["traps"], word_size=LABEL)
        fit_height(q.group, chat.get_bottom()[1] - 0.4 - (BOTTOM_Y + 0.6))
        q.group.next_to(chat, DOWN, buff=0.4).to_edge(LEFT, buff=SAFE + 0.6)
        note = picture_idea("back to the drawing board")
        fit_width(note, self.pinned.get_left()[0] - 0.3 - (q.word.get_right()[0] + 0.3))
        note.next_to(q.word, RIGHT, buff=0.3)
        filled = self.chat_card(fill="starting the plan again from scratch")
        verdict = pill("expect a fresh design cycle", GOOD, size=SMALL)

        # Place the verdict below the complete question block.
        # The previous layout positioned it beside only the correct answer row,
        # but no_overlap() checks the bounding box of the entire q.group.
        # That allowed the verdict to overlap another answer row.
        verdict.next_to(q.group, DOWN, buff=0.35)
        verdict.align_to(q.group, LEFT)
        fit_width(verdict, q.group.width)
        self.no_overlap(chat, q.group)
        self.no_overlap(q.group, verdict)
        self.no_overlap(verdict, self.pinned)
        self.no_overlap(chat, self.pinned)
        self.no_overlap(note, self.pinned)
        self.no_overlap(q.rows, note)
        self.validator.check_in_frame(VGroup(chat, q.group, note, verdict))

        n = self.narrate(
            id="solved_01",
            text="Let's solve the hook. Read: going back to the drawing board, after a rejection. Predict: the picture is "
                 "the board where designs begin. The idea: start again.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(chat), FadeIn(q.word), FadeIn(q.rows))
        self.at_word(n, "Read")
        self.play(Indicate(chat[1][2], color=WORD, scale_factor=1.03))
        self.at_word(n, "Predict")
        self.play(FadeIn(note[0], shift=LEFT * 0.1), self.pin_step(0, color=WORD))
        self.at_word(n, "idea")
        self.play(FadeIn(note[1:], shift=LEFT * 0.1), self.pin_step(1, color=STEP_COLS["PREDICT"]))
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_02",
            text="Eliminate. Designing a new logo and reviewing the old drawings are literal readings of drawing. Returning "
                 "to the office confuses board with a place.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Eliminate")
        self.play(self.pin_step(2, color=BAD))
        self.at_word(n, "Designing")
        self.play(*q.strike("a")[1], *q.strike("c")[1])
        self.at_word(n, "Returning")
        self.play(*q.strike("b")[1])
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_03",
            text="Confirm: Client rejected the design. We're starting the plan again from scratch. That's the answer. The "
                 "teammate should expect a fresh design cycle.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Confirm")
        self.play(ReplacementTransform(chat, filled), self.pin_step(3, color=GOOD))
        self.at_word(n, "starting")
        self.play(Indicate(filled[1][2], color=GOOD, scale_factor=1.03))
        self.at_word(n, "answer")
        self.play(*q.confirm()[1])
        self.at_word(n, "teammate")
        self.play(FadeIn(verdict, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S10_hook_solved")

    # ========================================== 11. EXAM PATTERNS ==========

    def exam_patterns(self):
        self.scene_start("S11_patterns", title="Exam Patterns and Solving Models")
        self.play(self.unpin())

        table = self.table_rows(["Pattern", "Solving model"], [
            ["Meaning of the idiom", "picture → idea → strike the literal option"],
            ["Idiom in a sentence", "use the sentence's situation to confirm the idea"],
            ["Fill in the idiom", "match the situation and tone (Video 3)"],
        ], [4.6, 7.2], size=LABEL)
        board = self.card(table, width=SAFE_W - 0.2).move_to(UP * 0.4)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="patterns_01",
            text="Three exam patterns. Meaning of the idiom: picture, then idea, then strike the literal option. Idiom in "
                 "a sentence: use the situation in that sentence to confirm the idea. And fill in the idiom: match the "
                 "situation and tone, which is video three.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(board[0]), FadeIn(table[0]))
        for row, spoken in zip(table[1:], ["Meaning", "sentence", "fill"]):
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
            (self.verdict_card(False, "Choosing the literal option", card_w),
             self.verdict_card(True, "Picture → idea", card_w)),
            (self.verdict_card(False, "An option that shares a word with the idiom", card_w),
             self.verdict_card(True, "Match the idea, not the words", card_w)),
            (self.verdict_card(False, "Overstating: “never” for “rarely”", card_w),
             self.verdict_card(True, "Match the degree", card_w)),
        ]
        for (wrong, right), yy in zip(pairs, [1.6, 0.05, -1.5]):
            wrong.move_to(LEFT_ZONE + UP * yy)
            right.move_to(RIGHT_ZONE + UP * yy)
        header = pill("3 mistakes", BAD, size=LABEL).move_to(UP * (CARD_TOP - 0.3))
        self.validator.check_in_frame(VGroup(header, *[c for p in pairs for c in p]))

        n = self.narrate(
            id="mistakes_01",
            text="Three common mistakes. The first is choosing the literal option. The second is choosing an option that "
                 "shares a word with the idiom. The third is overstating the meaning, like never for rarely.",
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
        ("spill the beans", ["reveal a secret", "waste food", "make a mess", "cook badly"], "a",
         {"b": "literal", "c": "literal", "d": "not the idea"}),
        ("burn the midnight oil", ["waste fuel", "work late into the night", "start a fire", "sleep late"], "b",
         {"a": "literal", "c": "literal", "d": "the opposite of the effort meant"}),
        ("cost an arm and a leg", ["cause injury", "be cheap", "be very expensive", "need effort"], "c",
         {"a": "literal", "b": "the opposite", "d": "not the idea"}),
    ]

    def practice(self):
        self.scene_start("S13_practice", title="Practice Questions")

        head = pill("Choose the MEANING of the idiom", SECOND, size=LABEL)
        lines = VGroup(*[VGroup(VGroup(pill(str(i + 1), FOCUS, size=SMALL), pill(f"“{idiom.capitalize()}”", WORD,
                                                                                size=LABEL)).arrange(RIGHT, buff=0.35),
                                text("   ".join(f"({l}) {o}" for l, o in zip("abcd", opts)), LABEL, INK))
                         .arrange(DOWN, buff=0.2, aligned_edge=LEFT)
                         for i, (idiom, opts, *_r) in enumerate(self.PRACTICE)])
        lines.arrange(DOWN, buff=0.4, aligned_edge=LEFT)
        board = self.card(VGroup(head, lines).arrange(DOWN, buff=0.4, aligned_edge=LEFT), color=FOCUS)
        fit_within(board, SAFE_W, SAFE_H - 1.2)
        board.move_to(UP * 0.4)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="practice_01",
            text="Your turn: choose the meaning. One: spill the beans. Reveal a secret, waste food, make a mess, or cook "
                 "badly? Two: burn the midnight oil. Waste fuel, work late into the night, start a fire, or sleep late? "
                 "Three: cost an arm and a leg. Cause injury, be cheap, be very expensive, or need effort?",
            voice="default",
            subtitle=True,
            pause_after=10.0,
        )
        self.play(FadeIn(board[0]), FadeIn(head))
        for ln, (spoken, first_option, occ) in zip(lines, [("spill", "Reveal", 1), ("burn", "Waste", 2),
                                                          ("cost", "Cause", 1)]):
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

        rows = VGroup()
        for idiom, opts, key, traps in self.PRACTICE:
            OptionQuestion(idiom, opts, key, traps)            # validates key / traps
            assert opts["abcd".index(key)] == IDIOMS[idiom][1]
            others = [f"({l}) {opts['abcd'.index(l)]}: {r}" for l, r in traps.items() if r != "not the idea"]
            rows.add(VGroup(VGroup(pill(f"“{idiom.capitalize()}”", WORD, size=LABEL), text("=", LABEL, MUTED),
                                   pill(f"({key}) {opts['abcd'.index(key)]}", GOOD, size=LABEL)).arrange(RIGHT, buff=0.3),
                            text("   ".join(others), SMALL, BAD)).arrange(DOWN, buff=0.18, aligned_edge=LEFT))
        rows.arrange(DOWN, buff=0.5, aligned_edge=LEFT)
        fit_within(rows, SAFE_W, SAFE_H - 1.2)
        rows.move_to(UP * 0.3)
        self.validator.check_in_frame(rows)

        n = self.narrate(
            id="answers_01",
            text="One: reveal a secret. Waste food and make a mess are literal. Two: work late into the night. Waste fuel "
                 "is literal, and sleep late is the opposite of the effort meant. Three: be very expensive. Cause injury "
                 "is literal.",
            voice="default",
            subtitle=True,
        )
        for r, (spoken, trap) in zip(rows, [("reveal", "mess"), ("work", "fuel"), ("expensive", "injury")]):
            self.at_word(n, spoken)
            self.play(FadeIn(r[0], shift=RIGHT * 0.2), run_time=0.5)
            self.at_word(n, trap)
            self.play(FadeIn(r[1], shift=LEFT * 0.1), run_time=0.4)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S14_answers")

    # ================================================ 15. RECAP ==========

    def recap(self):
        self.scene_start("S15_recap", title="Recap Card")

        card, table = self.recap_card("Recap Card: Video 1", [
            ["Idiom", "a fixed phrase with a figurative meaning"],
            ["Method", "picture → idea → strike the literal option → confirm in a sentence"],
            ["Traps", "literal readings, word-sharing options, overstatement"],
        ])
        card.move_to(UP * 0.2)
        self.validator.check_in_frame(card)

        n = self.narrate(
            id="recap_01",
            text="To recap. An idiom is a fixed phrase with a figurative meaning. The method: picture, then idea, then "
                 "strike the literal option, then confirm in a sentence. And the traps: literal readings, word-sharing "
                 "options, and overstatement.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(card[0]), FadeIn(table[0]))
        for row, spoken in zip(table[1:], ["idiom", "method", "traps"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.45)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S15_recap")

    # ================================================= 16. NEXT ==========

    def next_video(self):
        self.scene_start("S16_next", title="Next")

        common = pill("the most common idioms", SECOND, size=BODY)
        grouped = pill("grouped by the situations where you'll meet them", WORD, size=LABEL)
        nxt = pill("Next:  Common Idioms", FOCUS, size=LABEL)
        VGroup(common, grouped, nxt).arrange(DOWN, buff=0.7).move_to(UP * 0.2)
        self.no_overlap(common, grouped, nxt)
        self.validator.check_in_frame(VGroup(common, grouped, nxt))

        n = self.narrate(
            id="next_01",
            text="Video two gives you the most common idioms, grouped by the situations where you'll meet them.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Video")
        self.play(FadeIn(nxt, scale=1.05))
        self.at_word(n, "common")
        self.play(FadeIn(common, shift=UP * 0.1))
        self.at_word(n, "grouped")
        self.play(FadeIn(grouped, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S16_next")

"""
animation.py for the LMS video generator.

Course : Pre-C-CAT - Section A - English
Video  : Module 2 Introduction - Why Grammar Is in the Pre-C-CAT Course

Source script:
  C:\\Scripts\\Section A\\English - Module 2 Introduction - Why Grammar.md

Built on the golden-reference pattern:
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``;
  * layouts stacked with next_to and guarded with ``no_overlap``; nothing is
    ever animated onto or into another box.

Module introduction. Opening rule from the script: a silent breadcrumb and a one-line recap of Module 1, no spoken course welcome.
The narration is the script's. The corrected verb in the hook ("has") comes from a small subject-verb agreement check, not a typed label.
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

MARKS_RIGHT, MARKS_WRONG, ENGLISH_Q, GRAMMAR_2025 = 3, -1, 20, 5
GRAMMAR_2019 = ENGLISH_Q // 2                       # "about half of its English questions"

MODULE_1 = ["Synonyms", "Antonyms", "Idioms & Phrases", "One-Word Substitution", "Analogies"]

# The hook sentence, split into the four lettered parts (the words of part A are kept apart).
HOOK_PARTS = [("A", ["Each", "of the players"]), ("B", ["have"]), ("C", ["a unique"]), ("D", ["skill set."])]
SINGULAR_SUBJECTS = {"each", "every", "either", "neither", "one"}


def verb_for(subject, singular, plural):
    """Subject-verb agreement: the verb follows the subject, not the nearest noun."""
    return singular if subject.lower() in SINGULAR_SUBJECTS else plural


# (question with a blank, answer, what it tests)
ONE_RULE = [("proficient ___ French", "in", "one preposition"),
            ("___ honest man", "an", "one article"),
            ("Neither the teacher nor the students ___ present", "were", "one verb that must agree")]

# (lesson name, example shown on its row); Lessons 6 to 10
LESSONS = [("Prepositions", "proficient in French"),
           ("Articles", "an honest man, a utopian world"),
           ("Active & Passive Voice", "The chef cooked a meal → A meal was cooked by the chef"),
           ("Spotting Errors", "Each of the players have…"),
           ("Sentence Correction", "choose the corrected version")]
FIRST_LESSON = 6

assert verb_for("Each", "has", "have") == "has" and verb_for("players", "has", "have") == "have"
assert len(LESSONS) == 5 and GRAMMAR_2019 == 10 and GRAMMAR_2025 < GRAMMAR_2019


def steps_strip(labels, colors, size=LABEL, buff=0.25):
    """Numbered steps in a row, joined by arrows.  Steps are at [0], [2], [4]."""
    parts = []
    for i, (label, c) in enumerate(zip(labels, colors)):
        if i:
            parts.append(text("→", size, MUTED))
        parts.append(pill(f"{i + 1}  {label}", c, size=size))
    return VGroup(*parts).arrange(RIGHT, buff=buff)


def lesson_rows(lessons, first_number=1, color=WORD, example_width=None, example_size=LABEL):
    """One row per lesson: number chip, name, example.  Names and examples are column-aligned."""
    names = [text(name, LABEL, color, BOLD) for name, _ in lessons]
    gap = max(n.width for n in names) + 0.6
    rows = VGroup()
    for i, (name, (_, example)) in enumerate(zip(names, lessons)):
        num = pill(str(first_number + i), color, size=SMALL)
        ex = text(example, example_size, INK) if example_width is None else \
            fitted_text(example, example_width, example_size, INK, NORMAL, max_lines=2)
        name.next_to(num, RIGHT, buff=0.3)
        ex.next_to(num, RIGHT, buff=0.3 + gap)
        rows.add(VGroup(num, name, ex))
    return rows.arrange(DOWN, buff=0.32, aligned_edge=LEFT)


def lettered_sentence(parts, size=BODY):
    """The sentence as lettered, underlined parts.  Each part = (words, underline, letter)."""
    out = VGroup()
    for letter, words in parts:
        w = VGroup(*[text(s, size, INK) for s in words]).arrange(RIGHT, buff=0.16)
        line = Line(w.get_corner(DL) + DOWN * 0.12, w.get_corner(DR) + DOWN * 0.12, color=MUTED, stroke_width=2)
        tag = text(f"({letter})", SMALL, MUTED).next_to(line, DOWN, buff=0.12)
        out.add(VGroup(w, line, tag))
    return out.arrange(RIGHT, buff=0.3, aligned_edge=UP)


class WhyGrammarVideo(LMSScene):
    lesson_title = "Why Grammar Is in the Pre-C-CAT Course"

    def construct(self):
        self.camera.background_color = BG

        self.opening_recap()
        self.sounds_right()
        self.one_rule()
        self.how_much()
        self.five_types()
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

    # ========================================= 0. OPENING AND RECAP ==========
    # Opening rule: silent breadcrumb, a one-line recap of Module 1, no spoken welcome.

    def opening_recap(self):
        self.scene_start("S00_recap", title="Opening and Recap")

        crumb = self.breadcrumb("English", "Module 2 · Grammar", "Introduction")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        done = VGroup(*[pill(f"✓  {name}", GOOD, size=SMALL) for name in MODULE_1]).arrange(RIGHT, buff=0.25)
        fit_width(done, SAFE_W)
        method = steps_strip(["Spot the type", "Use the clues", "Eliminate"], [WORD, RATIO, GOOD])
        title = pill("Module 2  ·  Grammar", RATIO, size=TITLE)
        same = text("the same idea, for grammar", LABEL, MUTED)
        block = VGroup(done, method, title, same).arrange(DOWN, buff=0.6)
        fit_within(block, SAFE_W, SAFE_H - crumb.height - 0.8)
        block.next_to(crumb, DOWN, buff=0.6)
        self.no_overlap(crumb, done, method, title, same)
        self.validator.check_in_frame(VGroup(crumb, block))

        n = self.narrate(
            id="recap_01",
            text="In module one, you answered vocabulary questions with a method: spot the type, use the clues, eliminate.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.at_word(n, "module")
        self.play(LaggedStart(*[FadeIn(d, shift=UP * 0.1) for d in done], lag_ratio=0.12))
        self.at_word(n, "spot")
        self.play(FadeIn(method[0], shift=RIGHT * 0.1))
        self.at_word(n, "clues")
        self.play(FadeIn(method[1:3], shift=RIGHT * 0.1))
        self.at_word(n, "eliminate")
        self.play(FadeIn(method[3:], shift=RIGHT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="recap_02",
            text="This module uses the same idea for grammar.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "module")
        self.play(FadeIn(title, scale=1.1))
        self.at_word(n, "same")
        self.play(FadeIn(same, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_recap")

    # ============================ 1. THE PROBLEM WITH "IT SOUNDS RIGHT" ==========

    def sounds_right(self):
        self.scene_start("S01_sounds_right", title="The Problem with It Sounds Right")

        head = self.heading("Does it sound right?")
        by_ear = pill("most students answer by ear", MUTED, size=LABEL)
        find = pill("Find the error", FOCUS, size=LABEL)
        source = text("a recent memory-based paper", SMALL, MUTED)
        ask = VGroup(find, source).arrange(RIGHT, buff=0.4)
        sentence = lettered_sentence(HOOK_PARTS)
        each, players, have = sentence[0][0][0], sentence[0][0][1], sentence[1][0][0]
        bubble = pill("“players have…”  sounds fine", BAD, size=LABEL)
        lines = VGroup(text("The ear follows the nearest word.", LABEL, BAD),
                       text("The rule follows the subject.", LABEL, GOOD, BOLD)).arrange(DOWN, buff=0.25)
        catch = pill("the question is written to catch the ear", FOCUS, size=SMALL)
        # the "subject / singular" and "has" tags sit above the sentence: a spacer keeps their room,
        # and they are scaled together with the rest so the room can never be lost
        subject = VGroup(text("singular", SMALL, FOCUS), pill("subject", FOCUS)).arrange(DOWN, buff=0.12)
        correct = pill(verb_for("Each", "has", "have"), GOOD, size=LABEL)
        room = Rectangle(width=1.0, height=subject.height + 0.25).set_stroke(width=0)     # never shown
        top_row = VGroup(by_ear, ask).arrange(RIGHT, buff=0.6)
        body = VGroup(top_row, room, sentence, bubble, lines, catch).arrange(DOWN, buff=0.25)
        subject.next_to(each, UP, buff=0.15)
        correct.next_to(have, UP, buff=0.15)
        fit_within(VGroup(body, subject, correct), SAFE_W, SAFE_H - head.height - 0.5)
        VGroup(body, subject, correct).next_to(head, DOWN, buff=0.35)
        cross = Line(have.get_left() + LEFT * 0.05, have.get_right() + RIGHT * 0.05, color=BAD, stroke_width=4)
        self.no_overlap(head, top_row, subject, sentence, bubble, lines, catch)
        self.no_overlap(by_ear, ask)
        self.no_overlap(top_row, correct, sentence)
        self.no_overlap(subject, correct)
        self.validator.check_in_frame(VGroup(head, body, subject, correct))

        n = self.narrate(
            id="ear_01",
            text="You have used English for years. So most students answer grammar questions by ear.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "years")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "ear")
        self.play(FadeIn(by_ear, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="ear_02",
            text="Try this one from a recent memory-based paper. Find the error.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "memory-based")
        self.play(FadeIn(source), LaggedStart(*[FadeIn(p[0], shift=UP * 0.1) for p in sentence], lag_ratio=0.15))
        self.at_word(n, "error")
        self.play(FadeIn(find, shift=RIGHT * 0.1), *[FadeIn(p[1:]) for p in sentence])
        self.wait_for_narration(n)

        n = self.narrate(
            id="ear_03",
            text="Read it aloud and it sounds fine. Players have is what we say every day.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "aloud")
        self.play(FadeIn(bubble, shift=UP * 0.1))
        self.at_word(n, "Players")
        self.play(Indicate(players, color=BAD, scale_factor=1.1), Indicate(have, color=BAD, scale_factor=1.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="ear_04",
            text="But the subject is each, and each is singular. So the verb must be has.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "subject")
        self.play(each.animate.set_color(FOCUS), FadeIn(subject[1], shift=DOWN * 0.1))
        self.at_word(n, "singular")
        self.play(FadeIn(subject[0], shift=DOWN * 0.1))
        self.at_word(n, "has")
        self.play(have.animate.set_color(BAD), Create(cross), FadeIn(correct, shift=DOWN * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="ear_05",
            text="Your ear followed the nearest word. The rule follows the subject. The examiner knows this, and writes the "
                 "question to catch it.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "ear")
        self.play(FadeIn(lines[0], shift=UP * 0.1))
        self.at_word(n, "rule")
        self.play(FadeIn(lines[1], shift=UP * 0.1))
        self.at_word(n, "examiner")
        self.play(FadeIn(catch, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S01_sounds_right")

    # ============================= 2. WHAT C-CAT GRAMMAR REALLY TESTS ==========

    def one_rule(self):
        self.scene_start("S02_one_rule", title="What C-CAT Grammar Really Tests")

        head = self.heading("One question, one rule", GOOD)
        cards = VGroup()
        for question, answer, tests in ONE_RULE:
            cards.add(VGroup(fitted_text(question, 3.6, LABEL, INK, NORMAL, max_lines=3),
                             pill(f"→  {answer}", GOOD, size=LABEL),
                             text(tests, SMALL, RATIO, BOLD)).arrange(DOWN, buff=0.3))
        cards.arrange(RIGHT, buff=0.7, aligned_edge=UP)
        fit_width(cards, SAFE_W)
        counter = VGroup(pill("about 10 rules", FOCUS, size=BODY), text("→", BODY, MUTED),
                         text("most grammar questions", BODY, INK)).arrange(RIGHT, buff=0.3)
        scale = VGroup(pill(f"+{MARKS_RIGHT}  correct", GOOD, size=LABEL), pill(f"−{abs(MARKS_WRONG)}  wrong", BAD, size=LABEL),
                       text("a rule lets you be sure first", LABEL, INK)).arrange(RIGHT, buff=0.5)
        body = VGroup(cards, counter, scale).arrange(DOWN, buff=0.6)
        fit_within(body, SAFE_W, SAFE_H - head.height - 0.9)
        body.next_to(head, DOWN, buff=0.5)
        self.no_overlap(head, cards, counter, scale)
        self.no_overlap(cards[0], cards[1], cards[2])
        self.validator.check_in_frame(VGroup(head, body))

        n = self.narrate(
            id="rule_01",
            text="Here is the good news. Each grammar question tests one rule.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "news")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "one")
        self.play(LaggedStart(*[FadeIn(c[0], shift=UP * 0.1) for c in cards], lag_ratio=0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="rule_02",
            text="One preposition. One article. One verb that must agree.",
            voice="default",
            subtitle=True,
        )
        for c, spoken in zip(cards, ["preposition", "article", "verb"]):
            self.at_word(n, spoken)
            self.play(FadeIn(c[1], shift=UP * 0.1), FadeIn(c[2], shift=UP * 0.1), run_time=0.5)
        self.wait_for_narration(n)

        n = self.narrate(
            id="rule_03",
            text="And the same small set of rules comes back again and again. Learn those, and most grammar questions "
                 "become quick marks.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "small")
        self.play(FadeIn(counter[0], scale=1.1))
        self.at_word(n, "most")
        self.play(FadeIn(counter[1:], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="rule_04",
            text="That matters, because a wrong answer costs you a mark. A rule lets you be sure before you answer.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "wrong")
        self.play(FadeIn(scale[0], shift=UP * 0.1), FadeIn(scale[1], shift=UP * 0.1))
        self.at_word(n, "sure")
        self.play(FadeIn(scale[2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_one_rule")

    # ============================ 3. HOW MUCH OF THE PAPER IS GRAMMAR ==========

    def how_much(self):
        self.scene_start("S03_how_much", title="How Much of the Paper Is Grammar")

        head = self.heading("How many questions?")
        unit = 0.16                                            # bar height per question
        cols = VGroup()
        for paper, count, label, c in [("2025 memory paper", GRAMMAR_2025, f"about {GRAMMAR_2025} of {ENGLISH_Q}", WORD),
                                       ("2019 paper", GRAMMAR_2019, "about half of the English questions", RATIO)]:
            rest = Rectangle(width=1.4, height=(ENGLISH_Q - count) * unit, stroke_color=MUTED, stroke_width=2,
                             fill_color=MUTED, fill_opacity=0.12)
            fill = Rectangle(width=1.4, height=count * unit, stroke_color=c, stroke_width=2, fill_color=c, fill_opacity=0.7)
            bar = VGroup(rest, fill).arrange(DOWN, buff=0)
            cols.add(VGroup(bar, text(paper, LABEL, INK, BOLD), text(label, SMALL, c, BOLD)).arrange(DOWN, buff=0.22))
        cols.arrange(RIGHT, buff=1.6, aligned_edge=DOWN)
        both = pill("Prepare for both", FOCUS, size=BODY)
        body = VGroup(cols, both).arrange(DOWN, buff=0.5)
        fit_within(body, SAFE_W, SAFE_H - head.height - 0.8)
        body.next_to(head, DOWN, buff=0.4)
        self.no_overlap(head, cols, both)
        self.no_overlap(cols[0], cols[1])
        self.validator.check_in_frame(VGroup(head, body))

        n = self.narrate(
            id="much_01",
            text="How many grammar questions should you expect?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "many")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="much_02",
            text="It changes from paper to paper. A recent memory-based paper had about five. The 2019 paper had many more: "
                 "about half of its English questions were grammar and usage.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "changes")
        self.play(*[FadeIn(c[0][0]) for c in cols], *[FadeIn(c[1], shift=UP * 0.1) for c in cols])
        self.at_word(n, "five")
        self.play(GrowFromEdge(cols[0][0][1], DOWN), FadeIn(cols[0][2], shift=UP * 0.1))
        self.at_word(n, "half")
        self.play(GrowFromEdge(cols[1][0][1], DOWN), FadeIn(cols[1][2], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="much_03",
            text="So you should be ready for either.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "ready")
        self.play(FadeIn(both, scale=1.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_how_much")

    # ================================== 4. THE FIVE QUESTION TYPES ==========

    def five_types(self):
        self.scene_start("S04_five_types", title="The Five Question Types")

        head = self.heading("What Module 2 covers")
        rows = lesson_rows(LESSONS, first_number=FIRST_LESSON, color=RATIO, example_width=6.2, example_size=SMALL)
        fit_within(rows, SAFE_W, SAFE_H - head.height - 0.8)
        rows.next_to(head, DOWN, buff=0.5)
        self.no_overlap(head, rows)
        self.no_overlap(*rows)
        self.validator.check_in_frame(VGroup(head, rows))

        n = self.narrate(
            id="types_01",
            text="The module has five lessons.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "five")
        self.play(FadeIn(head, shift=DOWN * 0.2), LaggedStart(*[FadeIn(r[0], scale=0.7) for r in rows], lag_ratio=0.12))
        self.wait_for_narration(n)

        n = self.narrate(
            id="types_02",
            text="Lesson six is prepositions: which small word follows which verb or adjective.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "prepositions")
        self.play(FadeIn(rows[0][1], shift=RIGHT * 0.2))
        self.at_word(n, "small")
        self.play(FadeIn(rows[0][2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="types_03",
            text="Lesson seven is articles. The choice depends on the sound, not the spelling.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "articles")
        self.play(FadeIn(rows[1][1], shift=RIGHT * 0.2))
        self.at_word(n, "sound")
        self.play(FadeIn(rows[1][2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="types_04",
            text="Lesson eight is active and passive voice, where the tense must stay the same.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "active")
        self.play(FadeIn(rows[2][1], shift=RIGHT * 0.2))
        self.at_word(n, "tense")
        self.play(FadeIn(rows[2][2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="types_05",
            text="Lesson nine is spotting errors: find the one part that breaks a rule.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "spotting")
        self.play(FadeIn(rows[3][1], shift=RIGHT * 0.2))
        self.at_word(n, "breaks")
        self.play(FadeIn(rows[3][2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="types_06",
            text="Lesson ten is sentence correction: choose the version that fixes it.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "sentence")
        self.play(FadeIn(rows[4][1], shift=RIGHT * 0.2))
        self.at_word(n, "fixes")
        self.play(FadeIn(rows[4][2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_five_types")

    # ==================================== 5. HOW EACH LESSON WORKS ==========

    def how_lessons_work(self):
        self.scene_start("S05_how_lessons_work", title="How Each Lesson Works")

        head = self.heading("The same three steps every time")
        strip = steps_strip(["Spot what is being tested", "Apply the rule", "Eliminate and confirm"], [WORD, RATIO, GOOD],
                            size=SMALL)
        fit_width(strip, SAFE_W)
        strip.next_to(head, DOWN, buff=0.5)
        tested = VGroup(text("Each … have", SMALL, INK), text("→  subject–verb agreement", SMALL, WORD, BOLD))\
            .arrange(DOWN, buff=0.2)
        fit_width(tested, 3.7)
        apply = VGroup(text("Each = singular  →  has", SMALL, RATIO, BOLD), text("not “it sounds fine”", SMALL, BAD))\
            .arrange(DOWN, buff=0.2)
        fit_width(apply, 2.9)
        tiles = VGroup(*[pill(l, INK, size=SMALL, fill_opacity=0.06) for l in "ABCD"]).arrange(RIGHT, buff=0.2)
        fit_width(tiles, 3.4)
        for detail, step in zip([tested, apply, tiles], [strip[0], strip[2], strip[4]]):
            detail.next_to(step, DOWN, buff=0.5)
        wrong = [tiles[i] for i in (0, 2, 3)]
        crosses = VGroup(*[Line(t.get_corner(DL), t.get_corner(UR), color=BAD, stroke_width=3) for t in wrong])
        notes = VGroup(text("No school grammar from the start", LABEL, MUTED),
                       text("only the rules the exam uses", LABEL, INK, BOLD),
                       text("and the traps built around them", LABEL, BAD)).arrange(DOWN, buff=0.25)
        notes.move_to(UP * (BOTTOM_Y + notes.height / 2))
        self.no_overlap(head, strip)
        self.no_overlap(tested, apply, tiles)
        self.no_overlap(tested, notes)
        self.no_overlap(apply, notes)
        self.no_overlap(tiles, notes)
        self.validator.check_in_frame(VGroup(head, strip, tested, apply, tiles, notes))

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
            text="Spot which rule the question is testing.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Spot")
        self.play(FadeIn(strip[0], shift=DOWN * 0.1))
        self.at_word(n, "testing")
        self.play(FadeIn(tested, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="how_03",
            text="Apply that rule, not your ear.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "rule")
        self.play(FadeIn(strip[2], shift=DOWN * 0.1), FadeIn(apply[0], shift=UP * 0.1))
        self.at_word(n, "ear")
        self.play(FadeIn(apply[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="how_04",
            text="Then eliminate the options that break it, and confirm the one that is left.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "eliminate")
        self.play(FadeIn(strip[4], shift=DOWN * 0.1), FadeIn(tiles, shift=UP * 0.1))
        self.play(*[Create(c) for c in crosses], *[t[1].animate.set_opacity(0.35) for t in wrong], run_time=0.5)
        self.at_word(n, "confirm")
        self.play(tiles[1].animate.set_color(GOOD))
        self.wait_for_narration(n)

        n = self.narrate(
            id="how_05",
            text="We will not go through school grammar from the beginning. We will cover the rules the exam uses, and the "
                 "traps built around them.",
            voice="default",
            subtitle=True,
        )
        for note, spoken in zip(notes, ["school", "rules", "traps"]):
            self.at_word(n, spoken)
            self.play(FadeIn(note, shift=UP * 0.1), run_time=0.5)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_how_lessons_work")

    # ================================================ 6. CLOSING ==========

    def closing(self):
        self.scene_start("S06_closing", title="Closing")

        facts = VGroup(pill("one question, one rule", GOOD, size=LABEL),
                       pill("the ear is not reliable", BAD, size=LABEL)).arrange(RIGHT, buff=0.5)
        strip = VGroup(*[pill(name, RATIO if i == 0 else MUTED, size=SMALL) for i, (name, _) in enumerate(LESSONS)])\
            .arrange(RIGHT, buff=0.25)
        fit_width(strip, SAFE_W)
        nxt = self.breadcrumb("Next", "Lesson 6 · Prepositions")
        VGroup(facts, strip, nxt).arrange(DOWN, buff=0.9).move_to(UP * 0.2)
        self.no_overlap(facts, strip, nxt)
        self.validator.check_in_frame(VGroup(facts, strip, nxt))

        n = self.narrate(
            id="closing_01",
            text="To sum up: grammar questions test one rule each, and the ear is not reliable.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "one")
        self.play(FadeIn(facts[0], shift=UP * 0.1))
        self.at_word(n, "ear")
        self.play(FadeIn(facts[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="closing_02",
            text="We begin with prepositions. See you in lesson six.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "prepositions")
        self.play(LaggedStart(*[FadeIn(p, shift=UP * 0.1) for p in strip], lag_ratio=0.1))
        self.play(Indicate(strip[0], color=RATIO, scale_factor=1.15), run_time=0.6)
        self.at_word(n, "lesson")
        self.play(FadeIn(nxt, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S06_closing")

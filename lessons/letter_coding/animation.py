"""
animation.py for the LMS video generator.

Course : Pre-C-CAT - Section A
Module : Module 1 - Logical Reasoning
Lesson : Lesson 2 - Coding & Decoding I: Letter and Number Coding
Topic  : Letter Coding (Topic 1)

Source script:
  C:\\Scripts\\Section A\\Module 1 - Logical Reasoning\\Lesson 02 - Coding & Decoding I\\
  Topic 1 - Letter Coding.md

Built on the golden-reference pattern:
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``.

Opening: first video of a NEW LESSON (not of the course), so no spoken course
welcome. The module > lesson > topic trail is shown on screen (silent), then a
one-line recap of Lesson 1 (the Alphabet Test), one line saying Lesson 2
starts, the topic title and the objectives.

Section map (script heading -> VISUAL PLAN scene):
  S00 Intro (trail + recap)   -> -
  S01 Opening Hook            -> scene 1
  S02 Concept                 -> scene 2
  S03 The shift row           -> scene 3
  S04 Wrap-around             -> scene 4
  S05 Code families           -> scene 5
  S06-S08 Examples 1-3        -> scene 6
  S09 Exam Application        -> scene 7
  S10 Common Mistake          -> scene 8
  S11-S12 Practice / Answer   -> scene 9
  S13-S14 Revision / Closing  -> scene 10
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

# Semantic colours: one meaning each (same palette as Lesson 1).
FWD = "#4FC3F7"        # forward / encoding direction, positive shifts
REV = "#F48FB1"        # backward / decoding direction, negative shifts
ANCHOR = "#FFB74D"     # the shift row
OPP = "#CE93D8"        # opposite letters / reversal
FOCUS = "#FFD54F"      # "look here"
GOOD = "#66BB6A"       # confirmed rule / result
BAD = "#EF5350"        # no pattern / wrong answer

FONT = "Segoe UI"
MIN_FONT = 22          # readable floor: text is never shrunk below this
TITLE = 46
BODY = 30
LABEL = 28
SMALL = 24
NUM = 22
LETTER = 26
MATH = 44

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def pos(ch):
    return ALPHABET.index(ch) + 1


def shift_of(a, b):
    """How far letter ``a`` moved to become ``b``, in -12..+13 (wrap-around aware)."""
    d = (pos(b) - pos(a)) % 26
    return d - 26 if d > 13 else d


def shift_label(d):
    return "0" if d == 0 else (f"+{d}" if d > 0 else f"−{-d}")


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
CELL_SIZE = 0.46                              # alphabet strip cell (26 cells < SAFE_W)


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


def math_line(*parts, colors=None, size=MATH):
    """MathTex split into ``parts``, each part coloured from ``colors``."""
    colors = colors or {}
    line = MathTex(*parts, font_size=size, color=INK)
    for part, sub in zip(parts, line):
        if part in colors:
            sub.set_color(colors[part])
    return line


def pill(label, color=FOCUS, size=SMALL, fill_opacity=0.14):
    """Short keyword tag. The box is sized from the text, so text cannot escape."""
    t = text(label, size, color, BOLD)
    box = RoundedRectangle(corner_radius=(t.height + 0.26) / 2, width=t.width + 0.5, height=t.height + 0.26,
                           stroke_color=color, stroke_width=2, fill_color=color, fill_opacity=fill_opacity)
    t.move_to(box)
    return VGroup(box, t)


# ==================================================== diagram helpers ====

def tile(ch, side=0.8, color=INK):
    """One big letter in a rounded square."""
    sq = RoundedRectangle(corner_radius=0.1, width=side, height=side, stroke_color=MUTED,
                          stroke_width=2, fill_color=CELL, fill_opacity=1)
    return VGroup(sq, text(ch, int(side * 52), color, BOLD).move_to(sq))


def mark_tile(t, color):
    return AnimationGroup(t[0].animate.set_fill(color, 0.3).set_stroke(color, 3), t[1].animate.set_color(color))


def column_xs(n, spacing, centre=ORIGIN):
    """x positions of ``n`` evenly spaced columns centred on ``centre``."""
    return [centre[0] + (k - (n - 1) / 2) * spacing for k in range(n)]


class CodeBlock(VGroup):
    """A word row over its code row, one column per letter, with a
    ``shift_row`` (pills) under the code. Columns never move, so the shift
    under a column always belongs to that column's letters.

    word_y / code_y are absolute rows; ``xs`` the column centres. Parts are
    exposed but not added, so each can be revealed on its own beat.
    """

    def __init__(self, word, code, xs, word_y=1.2, code_y=-0.3, side=0.8):
        super().__init__()
        self.word = VGroup(*[tile(ch, side).move_to(RIGHT * x + UP * word_y) for ch, x in zip(word, xs)])
        self.code = VGroup(*[tile(ch, side).move_to(RIGHT * x + UP * code_y) for ch, x in zip(code, xs)])
        self.arrows = VGroup(*[Arrow(a.get_bottom(), b.get_top(), buff=0.1, color=MUTED, stroke_width=4,
                                     max_tip_length_to_length_ratio=0.2) for a, b in zip(self.word, self.code)])
        self.xs, self.side = xs, side

    def shift_row(self, shifts, color=ANCHOR, size=SMALL):
        """Pills under the code row, one per column."""
        return VGroup(*[pill(shift_label(d), color, size=size).next_to(t, DOWN, buff=0.22)
                        for d, t in zip(shifts, self.code)])


class AlphabetStrip(VGroup):
    """The 26 letters in a single row of cells, centred on the origin."""

    def __init__(self, letters=ALPHABET, cell=CELL_SIZE):
        super().__init__()
        self.letters = letters
        self.cells, self.chars = VGroup(), VGroup()
        for i, ch in enumerate(letters):
            sq = Square(cell, stroke_color=MUTED, stroke_width=1.5, fill_color=CELL, fill_opacity=1)
            sq.move_to(RIGHT * (i - (len(letters) - 1) / 2) * cell)
            self.cells.add(sq)
            self.chars.add(text(ch, LETTER, INK, BOLD).move_to(sq))
        self.add(self.cells, self.chars)


def circle_point(i, centre, radius):
    """Where letter ``i`` sits on the alphabet circle (A at the top, clockwise)."""
    a = PI / 2 - i * TAU / 26
    return centre + radius * np.array([np.cos(a), np.sin(a), 0.0])


# ============================================================= lesson ====

class LetterCodingVideo(LMSScene):
    lesson_title = "Letter Coding"

    def construct(self):
        self.camera.background_color = BG

        self.lesson_intro()
        self.hook()
        self.concept()
        self.shift_row_tool()
        self.wrap_around()
        self.code_families()
        self.example_decode()
        self.example_progressive()
        self.example_reversal()
        self.exam_application()
        self.common_mistake()
        self.practice()
        self.answer()
        self.quick_revision()
        self.closing()

    # ---------------------------------------------------- scene helpers --

    def clear_stage(self, run_time=0.6):
        """Scene transition: fade out everything on screen."""
        if self.mobjects:
            self.play(FadeOut(Group(*self.mobjects)), run_time=run_time)

    def card(self, content, width=None, height=None, color=MUTED, pad=0.3):
        """Container-aware card (grows to content, or fits content to a fixed size)."""
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

    def question_card(self, s, color=FOCUS):
        """The on-screen question: one fitted line (or two) in a card at the top."""
        t = fitted_text(s, SAFE_W - 1.6, BODY, INK, max_lines=2)
        c = self.card(t, color=color)
        return c.move_to(UP * (CARD_TOP - c.height / 2))

    def caption(self, s, color=INK):
        """One-line keyword caption in a fixed-width bar at the bottom of the frame."""
        t = fitted_text(s, SAFE_W - 1.0, BODY, color)
        bar = self.card(t, width=SAFE_W - 0.4, height=t.height + 0.9)
        return bar.move_to(UP * BOTTOM_Y)

    def breadcrumb(self, *parts):
        """Silent 'where are we' trail: Module > Lesson > Topic."""
        colors = [FWD, REV, ANCHOR]
        items = []
        for i, p in enumerate(parts):
            if i:
                items.append(text("›", LABEL, MUTED))
            items.append(pill(p, colors[i % 3], size=SMALL))
        return fit_width(VGroup(*items).arrange(RIGHT, buff=0.25), SAFE_W)

    def step_rows(self, rows, width):
        """Numbered rows (pill + fitted text) for routine cards."""
        return VGroup(*[VGroup(pill(str(i + 1), c, size=SMALL), fitted_text(s, width - 1.2, BODY, INK))
                        .arrange(RIGHT, buff=0.3) for i, (s, c) in enumerate(rows)]
                      ).arrange(DOWN, buff=0.25, aligned_edge=LEFT)

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

    def reverse_row(self, row):
        """Animation: the tiles of ``row`` swap into reverse order (in place)."""
        centres = [t.get_center() for t in row]
        return AnimationGroup(*[t.animate.move_to(centres[len(row) - 1 - k]) for k, t in enumerate(row)],
                              run_time=1.4)

    # ========================================= 0. LESSON INTRO ==========
    # Purpose: where we are (silent trail, now Lesson 2), a one-line recap of
    # the whole Alphabet Test, the new lesson, today's topic.

    def lesson_intro(self):
        self.scene_start("S00_intro", title="Lesson Introduction")

        crumb = self.breadcrumb("Module 1 · Logical Reasoning", "Lesson 2 · Coding & Decoding I", "Topic 1")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        last = pill("Last lesson: the Alphabet Test", MUTED, size=SMALL)
        strip = AlphabetStrip()
        skills = VGroup(pill("positions", FWD, size=SMALL), pill("opposites", OPP, size=SMALL),
                        pill("movement", ANCHOR, size=SMALL), pill("whole words", GOOD, size=SMALL))
        skills.arrange(RIGHT, buff=0.35)
        recap = VGroup(last, strip, skills).arrange(DOWN, buff=0.45).move_to(UP * 0.2)
        self.validator.check_in_frame(VGroup(crumb, recap))

        # SEE (silent): the trail.  HEAR: the Alphabet Test in one sentence.
        # SEE: one skill tag per skill named.
        n = self.narrate(
            id="intro_01",
            text="In the last lesson, the Alphabet Test, you learned to place any letter from either end, "
                 "find its opposite, move from one letter to another, and work with whole words.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.play(FadeIn(last), FadeIn(strip))
        for tag, spoken in zip(skills, ["place", "opposite", "move", "words"]):
            self.at_word(n, spoken)
            self.play(FadeIn(tag, shift=UP * 0.2), run_time=0.4)
        self.wait_for_narration(n)

        # HEAR: Lesson 2 starts; today's topic.  SEE: the lesson tag in the
        # trail pulses; the recap gives way to the title.
        title = fitted_text("Letter Coding", SAFE_W, 72, INK, BOLD)
        underline = Line(LEFT, RIGHT, color=ANCHOR, stroke_width=5).set_width(title.width * 0.6)
        VGroup(title, underline).arrange(DOWN, buff=0.2).move_to(UP * 0.2)
        n = self.narrate(
            id="intro_02",
            text="Now we start Lesson Two, Coding and Decoding, where those same skills become the tools "
                 "for cracking codes. Our first topic is Letter Coding.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Lesson")
        self.play(Indicate(crumb[2], color=REV, scale_factor=1.1))
        self.at_word(n, "tools")
        self.play(FadeOut(VGroup(last, strip)), skills.animate.scale(0.8).to_edge(DOWN, buff=SAFE + 0.2))
        self.at_word(n, "first")
        self.play(Write(title), run_time=1.1)
        self.play(GrowFromCenter(underline))
        self.wait_for_narration(n)

        # HEAR: the four objectives.  SEE: one row per objective, on its word.
        goals = [
            ("Find the rule behind a letter code", ANCHOR),
            ("Name the type of code", OPP),
            ("Encode and decode, even past Z", FWD),
            ("Avoid the two most common traps", BAD),
        ]
        rows = VGroup(*[VGroup(pill(str(i + 1), c, size=SMALL), fitted_text(s, SAFE_W - 2.4, BODY, INK))
                        .arrange(RIGHT, buff=0.35) for i, (s, c) in enumerate(goals)])
        rows.arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        heading = text("By the end of this video, you will:", LABEL, MUTED, BOLD)
        objectives = self.card(VGroup(heading, rows).arrange(DOWN, buff=0.4, aligned_edge=LEFT))
        small_title = title.copy().scale(0.6)
        small_title.next_to(crumb, DOWN, buff=0.3)
        objectives.next_to(small_title, DOWN, buff=0.35)
        self.validator.check_in_frame(VGroup(crumb, small_title, objectives))
        n = self.narrate(
            id="intro_03",
            text="By the end of this video, you'll be able to find the rule behind a letter code, name the type of "
                 "code, encode or decode a word even when it wraps around from Z to A, "
                 "and avoid the two most common traps.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(VGroup(underline, skills)), ReplacementTransform(title, small_title), run_time=0.8)
        self.play(FadeIn(objectives[0]), FadeIn(heading))
        for row, spoken in zip(rows, ["find", "name", "encode", "avoid"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.5)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_intro")

    # ================================================= 1. HOOK ==========

    def hook(self):
        self.scene_start("S01_hook", title="Opening Hook")

        xs = column_xs(5, 1.25)
        block = CodeBlock("MANGO", "OCPIQ", xs, word_y=1.9, code_y=0.5)
        apple = VGroup(*[tile(ch, 0.8).move_to(RIGHT * x + DOWN * 1.2) for ch, x in zip("APPLE", xs)])
        unknown = VGroup(*[tile("?", 0.8, FOCUS).move_to(RIGHT * x + DOWN * 2.6) for x in xs])
        apple_arrows = VGroup(*[Arrow(a.get_bottom(), u.get_top(), buff=0.1, color=MUTED, stroke_width=4,
                                      max_tip_length_to_length_ratio=0.2) for a, u in zip(apple, unknown)])
        self.validator.check_in_frame(VGroup(block.word, unknown))

        # HEAR: MANGO is OCPIQ; what is APPLE?  SEE: the pair, then APPLE → ?.
        n = self.narrate(
            id="hook_01",
            text="Suppose you're told that MANGO is written in a certain code as OCPIQ. "
                 "How would APPLE be written in the same code?",
            voice="default",
            subtitle=True,
        )
        self.play(LaggedStart(*[FadeIn(t, shift=DOWN * 0.2) for t in block.word], lag_ratio=0.1))
        self.at_word(n, "code")
        self.play(LaggedStart(*[GrowArrow(a) for a in block.arrows], lag_ratio=0.1),
                  LaggedStart(*[FadeIn(t, shift=DOWN * 0.2) for t in block.code], lag_ratio=0.1))
        self.at_word(n, "APPLE")
        self.play(FadeIn(apple), FadeIn(apple_arrows), FadeIn(unknown, scale=1.2))
        self.wait_for_narration(n)

        # HEAR: the same thinking cracks harder codes.  SEE: caption; the word
        # row flips backwards and back on "backwards".
        n = self.narrate(
            id="hook_02",
            text="This is the simplest form of a coding question. But the same way of thinking solves much harder "
                 "codes too, the ones where letters jump by different amounts, or where the word is written "
                 "backwards before it's changed.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "harder")
        cap = self.caption("Same thinking  →  much harder codes", FOCUS)
        self.play(FadeIn(cap, shift=UP * 0.2), FadeOut(VGroup(apple, apple_arrows, unknown)))
        self.at_word(n, "different")
        self.play(Indicate(block.code, color=ANCHOR, scale_factor=1.05))
        self.at_word(n, "backwards")
        self.play(self.reverse_row(block.word))
        self.play(self.reverse_row(block.word))
        self.wait_for_narration(n)

        # HEAR: the goal is one reliable way to uncover any code.
        n = self.narrate(
            id="hook_03",
            text="The goal of this lesson isn't to memorise code types. "
                 "It's to learn one reliable way to uncover any letter code.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "uncover")
        new_cap = self.caption("One reliable way to uncover any letter code", GOOD)
        self.play(FadeTransform(cap, new_cap))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S01_hook")

    # ============================================== 2. CONCEPT ==========

    def concept(self):
        self.scene_start("S02_concept", title="Concept Introduction")

        word = pill("WORD", FWD, size=TITLE)
        code = pill("CODE", ANCHOR, size=TITLE)
        VGroup(word, code).arrange(RIGHT, buff=4.0).move_to(UP * 0.8)
        enc = Arrow(word.get_right(), code.get_left(), buff=0.25, color=GOOD, stroke_width=6).shift(UP * 0.3)
        enc_label = text("rule", LABEL, GOOD, BOLD).next_to(enc, UP, buff=0.12)
        dec = Arrow(code.get_left(), word.get_right(), buff=0.25, color=REV, stroke_width=6).shift(DOWN * 0.3)
        dec_label = text("rule in reverse", SMALL, REV, BOLD).next_to(dec, DOWN, buff=0.12)

        # HEAR: a word becomes a code by a rule; find it, apply it, or undo it.
        # SEE: WORD, CODE, the "rule" arrow, then the reverse arrow.
        n = self.narrate(
            id="concept_01",
            text="In a coding question, a word is changed into a code by applying a fixed rule to its letters. "
                 "You're shown one word and its code. Your task is to find the rule, and then apply it to a new "
                 "word, or apply it in reverse to decode a code.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(word, shift=RIGHT * 0.2), FadeIn(code, shift=LEFT * 0.2))
        self.at_word(n, "rule", occurrence=1)
        self.play(GrowArrow(enc), FadeIn(enc_label))
        self.at_word(n, "reverse")
        self.play(GrowArrow(dec), FadeIn(dec_label))
        self.wait_for_narration(n)

        # HEAR: letter coding uses the Alphabet Test tools.  SEE: three tags.
        tools = VGroup(pill("positions", FWD), pill("opposites", OPP), pill("movement", ANCHOR))
        tools.arrange(RIGHT, buff=0.5).move_to(DOWN * 1.6)
        n = self.narrate(
            id="concept_02",
            text="Technically, this is letter coding: each letter is replaced by another letter according to a "
                 "positional rule. Everything you learned in the Alphabet Test, such as positions, opposites and "
                 "movement, now becomes the machinery of these rules.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "positions")
        self.play(FadeIn(tools[0], shift=UP * 0.2))
        self.at_word(n, "opposites")
        self.play(FadeIn(tools[1], shift=UP * 0.2))
        self.at_word(n, "movement")
        self.play(FadeIn(tools[2], shift=UP * 0.2))
        self.at_word(n, "machinery")
        self.play(Indicate(VGroup(enc, enc_label), color=GOOD))
        self.validator.check_in_frame(VGroup(enc_label, word, code, dec_label, tools))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_concept")

    # =========================================== 3. THE SHIFT ROW ==========

    def shift_row_tool(self):
        self.scene_start("S03_shift_row", title="Explanation - The Shift Row")

        xs = column_xs(5, 1.35)
        block = CodeBlock("MANGO", "OCPIQ", xs, word_y=2.0, code_y=0.4)
        shifts = block.shift_row([shift_of(a, b) for a, b in zip("MANGO", "OCPIQ")])

        # HEAR: write the shift under each letter.  SEE: MANGO over OCPIQ.
        n = self.narrate(
            id="shift_01",
            text="The single most useful habit is to write the shift under each letter: how many places the letter "
                 "moved in the alphabet, and in which direction.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(block.word), FadeIn(block.arrows), FadeIn(block.code))
        self.at_word(n, "shift")
        self.play(Indicate(block.arrows, color=ANCHOR))
        self.wait_for_narration(n)

        # HEAR: +2 each.  SEE: the +2 pills column by column.
        n = self.narrate(
            id="shift_02",
            text="For MANGO to OCPIQ, M moves to O, which is plus two. A moves to C, also plus two. Every letter "
                 "moves forward two places. That's a constant shift of plus two.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "plus", occurrence=1)
        self.play(FadeIn(shifts[0], shift=UP * 0.15))
        self.at_word(n, "plus", occurrence=2)
        self.play(FadeIn(shifts[1], shift=UP * 0.15))
        self.at_word(n, "Every")
        self.play(LaggedStart(*[FadeIn(s, shift=UP * 0.15) for s in shifts[2:]], lag_ratio=0.3))
        self.at_word(n, "constant")
        tag = pill("constant shift  +2", GOOD, size=LABEL).next_to(shifts, DOWN, buff=0.35)
        self.play(FadeIn(tag, scale=1.1))
        self.wait_for_narration(n)

        # HEAR: APPLE becomes CRRNG.  SEE: APPLE takes MANGO's place; the code
        # letters appear one per spoken letter.
        apple = CodeBlock("APPLE", "CRRNG", xs, word_y=2.0, code_y=0.4)
        apple_shifts = apple.shift_row([2] * 5)
        n = self.narrate(
            id="shift_03",
            text="So APPLE becomes C, R, R, N, G: CRRNG.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(VGroup(block.code, block.arrows, tag)), FadeTransform(block.word, apple.word),
                  FadeTransform(shifts, apple_shifts))
        self.play_with(n, LaggedStart(*[AnimationGroup(GrowArrow(a), FadeIn(c, shift=DOWN * 0.15))
                                        for a, c in zip(apple.arrows, apple.code)], lag_ratio=0.5), fraction=0.7)
        self.play(*[mark_tile(c, GOOD) for c in apple.code])
        self.wait_for_narration(n)

        # HEAR: the shift row turns guessing into a pattern.  SEE: formula card.
        formula = self.card(text("Shift = code position − word position", LABEL, INK, BOLD,
                                 t2c={"Shift": ANCHOR, "code position": GOOD, "word position": FWD}), color=ANCHOR)
        formula.move_to(UP * (BOTTOM_Y + 0.3))
        n = self.narrate(
            id="shift_04",
            text="The shift row turns a guessing game into a pattern you can see. "
                 "Almost every letter code shows up clearly in it.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(formula, shift=UP * 0.2))
        self.at_word(n, "pattern")
        self.play(Circumscribe(apple_shifts, color=ANCHOR))
        self.validator.check_in_frame(VGroup(apple.word, apple_shifts, formula))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_shift_row")

    # ============================================ 4. WRAP-AROUND ==========

    def wrap_around(self):
        self.scene_start("S04_wrap", title="Explanation - Wrap-around")

        strip = AlphabetStrip().move_to(UP * 0.3)
        centre, radius = LEFT_ZONE + DOWN * 0.1, 2.35
        ring = Circle(radius=radius + 0.32, stroke_color=MUTED, stroke_width=1.5).move_to(centre)

        # HEAR: past Z?  The alphabet is a circle.  SEE: the strip's letters
        # move onto a circle, so Z sits next to A.
        n = self.narrate(
            id="wrap_01",
            text="What happens when a shift runs past Z? The alphabet is treated as a circle. After Z comes A again.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(strip))
        self.at_word(n, "circle")
        self.play(FadeOut(strip.cells),
                  *[strip.chars[i].animate.move_to(circle_point(i, centre, radius)) for i in range(26)],
                  Create(ring), run_time=1.8)
        self.at_word(n, "After")
        self.play(Indicate(VGroup(strip.chars[25], strip.chars[0]), color=FOCUS, scale_factor=1.5))
        self.wait_for_narration(n)

        # HEAR: +2: Y -> A, Z -> B; ZEBRA -> BGDTC.  SEE: arcs round the top of
        # the circle, then ZEBRA and its code on the right.
        def hop_arc(i, j, color):
            return ArcBetweenPoints(circle_point(i, centre, radius + 0.55), circle_point(j, centre, radius + 0.55),
                                    angle=-TAU / 26 * ((j - i) % 26), color=color, stroke_width=4)

        ya, zb = hop_arc(24, 0, FWD), hop_arc(25, 1, ANCHOR)
        zebra = CodeBlock("ZEBRA", "BGDTC", column_xs(5, 1.1, RIGHT_ZONE), word_y=1.1, code_y=-0.5, side=0.75)
        plus = zebra.shift_row([2] * 5)
        n = self.narrate(
            id="wrap_02",
            text="So with a shift of plus two, Y becomes A, and Z becomes B. ZEBRA becomes BGDTC.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "becomes", occurrence=1)
        self.play(Create(ya), strip.chars[24].animate.set_color(FWD), strip.chars[0].animate.set_color(FWD))
        self.at_word(n, "becomes", occurrence=2)
        self.play(Create(zb), strip.chars[25].animate.set_color(ANCHOR), strip.chars[1].animate.set_color(ANCHOR))
        self.at_word(n, "ZEBRA")
        self.play(FadeIn(zebra.word))
        self.play(LaggedStart(*[AnimationGroup(GrowArrow(a), FadeIn(c, shift=DOWN * 0.15), FadeIn(p))
                                for a, c, p in zip(zebra.arrows, zebra.code, plus)], lag_ratio=0.4))
        self.play(mark_tile(zebra.code[0], ANCHOR))
        self.validator.check_in_frame(VGroup(ring, zebra.word, plus))
        self.wait_for_narration(n)

        # HEAR: the rule in numbers.  SEE: the caption.
        n = self.narrate(
            id="wrap_03",
            text="In numbers: if the new position goes above twenty-six, subtract twenty-six. "
                 "If it drops below one, add twenty-six.",
            voice="default",
            subtitle=True,
        )
        cap = self.caption("Above 26  →  subtract 26      ·      below 1  →  add 26", FOCUS)
        self.at_word(n, "above")
        self.play(FadeIn(cap, shift=UP * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_wrap")

    # ========================================== 5. CODE FAMILIES ==========

    def code_families(self):
        self.scene_start("S05_families", title="Explanation - Code Families")

        specs = [
            ("same number every time  (+2, +2, +2)", "Constant shift", GOOD),
            ("increasing or decreasing  (+1, +2, +3 …)", "Progressive shift", FWD),
            ("word + code positions = 27", "Opposite letters", OPP),
            ("code = word written backwards", "Reversal", REV),
            ("reversed word, then a constant shift", "Reversal + shift", ANCHOR),
        ]
        # Two aligned columns: pattern text (left-aligned) | arrow | family tag.
        patterns = VGroup(*[fitted_text(p, 6.4, SMALL, INK) for p, _, _ in specs])
        tags = VGroup(*[pill(f, c) for _, f, c in specs])
        rows = VGroup()
        for k, (p, t) in enumerate(zip(patterns, tags)):
            y = -k * 0.72
            p.move_to(UP * y, aligned_edge=LEFT).shift(LEFT * 6.0)
            arrow = text("→", LABEL, MUTED).move_to(RIGHT * 0.9 + UP * y)
            t.move_to(UP * y, aligned_edge=LEFT).shift(RIGHT * 1.4)
            rows.add(VGroup(p, arrow, t))
        heading = VGroup(text("Shift row pattern", SMALL, MUTED, BOLD), text("Code type", SMALL, MUTED, BOLD))
        heading[0].next_to(rows, UP, buff=0.35).align_to(patterns, LEFT)
        heading[1].move_to(heading[0]).align_to(tags, LEFT)
        table = self.card(VGroup(heading, rows))
        fit_width(table, SAFE_W).move_to(UP * 0.6)
        self.validator.check_in_frame(table)

        n = self.narrate(
            id="families_01",
            text="Once the shift row is written, it usually points straight to one of five families.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(table[0]), FadeIn(heading))
        self.wait_for_narration(n)

        # HEAR: one family per sentence.  SEE: its row appears on that sentence.
        n = self.narrate(
            id="families_02",
            text="If every shift is the same, it's a constant shift, forward or backward.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="families_03",
            text="If the shifts grow in a pattern, such as plus one, plus two, plus three, it's a progressive shift.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="families_04",
            text="If the shifts look irregular, check whether each pair of positions adds up to twenty-seven. "
                 "That's opposite-letter coding, from the Alphabet Test.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "check")
        self.play(FadeIn(rows[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        tiger = VGroup(pill("TIGER", INK, size=SMALL, fill_opacity=0.05), text("→", SMALL, MUTED),
                       pill("REGIT", REV, size=SMALL)).arrange(RIGHT, buff=0.2)
        tiger.next_to(table, DOWN, buff=0.3).align_to(table, RIGHT)
        n = self.narrate(
            id="families_05",
            text="If the code looks like the word written backwards, it's a reversal. TIGER becomes REGIT.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(rows[3], shift=RIGHT * 0.2))
        self.at_word(n, "TIGER")
        self.play(FadeIn(tiger, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="families_06",
            text="And if the shifts look random, try reversing the word first, and then write the shift row again. "
                 "Very often, a constant shift appears. That's reversal plus shift.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "reversing")
        self.play(FadeOut(tiger), FadeIn(rows[4], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        # HEAR: irregular -> test opposites, then reversal.  SEE: highlight.
        n = self.narrate(
            id="families_07",
            text="So when the direct shift row looks irregular, the next two things to test are opposites and reversal.",
            voice="default",
            subtitle=True,
        )
        cap = self.caption("Irregular shifts?  Test opposites, then test reversal", FOCUS)
        self.play(FadeIn(cap, shift=UP * 0.2))
        self.at_word(n, "opposites")
        self.play(Indicate(rows[2], color=OPP, scale_factor=1.03))
        self.at_word(n, "reversal")
        self.play(Indicate(rows[3], color=REV, scale_factor=1.03), Indicate(rows[4], color=ANCHOR, scale_factor=1.03))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_families")

    # ============================ 6. EXAMPLE 1: DECODING A CONSTANT SHIFT ==========

    def example_decode(self):
        self.scene_start("S06_example_decode", title="Example 1 - Decoding")

        question = self.question_card("Every letter is shifted +2.  Which word is written as FQI?")
        # Code on top, word below: the arrows run from the code back to the word.
        block = CodeBlock("FQI", "DOG", column_xs(3, 1.6), word_y=1.0, code_y=-0.7, side=0.95)
        minus = block.shift_row([-2, -2, -2], color=REV)
        block.arrows.set_color(REV)

        n = self.narrate(
            id="ex1_01",
            text="Coding also works in reverse. If every letter is shifted forward by two, "
                 "which word is written as FQI?",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(question, shift=DOWN * 0.3))
        self.at_word(n, "FQI")
        self.play(LaggedStart(*[FadeIn(t, shift=DOWN * 0.2) for t in block.word], lag_ratio=0.2))
        self.wait_for_narration(n)

        # HEAR: undo the rule: back two.  SEE: F->D, Q->O, I->G on each "becomes".
        n = self.narrate(
            id="ex1_02",
            text="To decode, undo the rule: move each letter back two places. F becomes D, Q becomes O, "
                 "and I becomes G. The word is DOG.",
            voice="default",
            subtitle=True,
        )
        for k in range(3):
            self.at_word(n, "becomes", occurrence=k + 1)
            self.play(GrowArrow(block.arrows[k]), FadeIn(block.code[k], shift=DOWN * 0.15), FadeIn(minus[k]),
                      run_time=0.5)
        self.at_word(n, "DOG")
        self.play(*[mark_tile(t, GOOD) for t in block.code])
        self.validator.check_in_frame(VGroup(question, block.word, minus))
        self.wait_for_narration(n)

        n = self.narrate(
            id="ex1_03",
            text="Encoding applies the rule. Decoding applies the opposite of the rule.",
            voice="default",
            subtitle=True,
        )
        cap = self.caption("Encode: apply the rule   ·   Decode: undo it", FOCUS)
        self.play(FadeIn(cap, shift=UP * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_example_decode")

    # ================================ 7. EXAMPLE 2: PROGRESSIVE SHIFT ==========

    def example_progressive(self):
        self.scene_start("S07_example_progressive", title="Example 2 - Progressive Shift")

        question = self.question_card("FIRE → GKUI.   How is WATER coded?")
        fire = CodeBlock("FIRE", "GKUI", column_xs(4, 1.15, LEFT_ZONE), word_y=1.3, code_y=-0.2, side=0.75)
        fire_shifts = fire.shift_row([shift_of(a, b) for a, b in zip("FIRE", "GKUI")], color=FWD)
        water = CodeBlock("WATER", "XCWIW", column_xs(5, 1.1, RIGHT_ZONE), word_y=1.3, code_y=-0.2, side=0.75)
        water_shifts = water.shift_row([1, 2, 3, 4, 5], color=FWD)
        divider = DashedLine(UP * 1.9, DOWN * 1.4, color=MUTED)

        n = self.narrate(
            id="ex2_01",
            text="If FIRE is coded as GKUI, how is WATER coded?",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(question, shift=DOWN * 0.3))
        self.play(FadeIn(fire.word), FadeIn(fire.arrows), FadeIn(fire.code))
        self.wait_for_narration(n)

        # HEAR: +1, +2, +3, +4.  SEE: one pill per spoken shift.
        n = self.narrate(
            id="ex2_02",
            text="Write the shift row. F to G is plus one. I to K is plus two. R to U is plus three. E to I is "
                 "plus four. This is a progressive shift, starting at plus one and increasing by one each letter.",
            voice="default",
            subtitle=True,
        )
        for k in range(4):
            self.at_word(n, "plus", occurrence=k + 1)
            self.play(FadeIn(fire_shifts[k], shift=UP * 0.15), run_time=0.4)
        self.at_word(n, "progressive")
        tag = pill("progressive  +1, +2, +3 …", FWD, size=SMALL).next_to(fire_shifts, DOWN, buff=0.3)
        self.play(FadeIn(tag, scale=1.1))
        self.wait_for_narration(n)

        # HEAR: apply to WATER letter by letter.  SEE: each code letter + shift.
        n = self.narrate(
            id="ex2_03",
            text="Apply it to WATER. W plus one is X. A plus two is C. T plus three is W. E plus four is I. "
                 "And R plus five is W. The code is XCWIW.",
            voice="default",
            subtitle=True,
        )
        self.play(Create(divider), FadeIn(water.word))
        for k in range(5):
            self.at_word(n, "plus", occurrence=k + 1)
            self.play(GrowArrow(water.arrows[k]), FadeIn(water.code[k], shift=DOWN * 0.15),
                      FadeIn(water_shifts[k]), run_time=0.45)
        self.at_word(n, "code")
        self.play(*[mark_tile(t, GOOD) for t in water.code])
        self.validator.check_in_frame(VGroup(question, fire_shifts, tag, water_shifts))
        self.wait_for_narration(n)

        # HEAR: extend the pattern to +5.  SEE: the fifth shift pulses.
        n = self.narrate(
            id="ex2_04",
            text="Notice that WATER has five letters and FIRE only four. So we extend the pattern to plus five. "
                 "The rule is the pattern, not a fixed list of shifts.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "extend")
        self.play(Indicate(water_shifts[4], color=FOCUS, scale_factor=1.4))
        self.at_word(n, "pattern", occurrence=2)
        cap = self.caption("The rule is the pattern, not a fixed list of shifts", FOCUS)
        self.play(FadeIn(cap, shift=UP * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S07_example_progressive")

    # ================================ 8. EXAMPLE 3: REVERSAL + SHIFT ==========

    def example_reversal(self):
        self.scene_start("S08_example_reversal", title="Example 3 - Reversal plus Shift")

        question = self.question_card("SMART → SQZLR.   How is BRAIN coded?")
        xs = column_xs(5, 1.35)
        block = CodeBlock("SMART", "SQZLR", xs, word_y=1.25, code_y=-0.3)
        direct = block.shift_row([shift_of(a, b) for a, b in zip("SMART", "SQZLR")], color=BAD)
        no_pattern = pill("no pattern", BAD, size=SMALL).next_to(direct, RIGHT, buff=0.35)

        n = self.narrate(
            id="ex3_01",
            text="Now a harder one. SMART is coded as SQZLR. How is BRAIN coded?",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(question, shift=DOWN * 0.3))
        self.play(FadeIn(block.word), FadeIn(block.arrows), FadeIn(block.code))
        self.wait_for_narration(n)

        # HEAR: direct shift row: no pattern; opposites fail.  SEE: red row.
        n = self.narrate(
            id="ex3_02",
            text="The direct shift row gives zero, plus four, minus one, minus six, minus two. There's no pattern. "
                 "Opposites don't work either: S and S don't add to twenty-seven.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "zero")
        self.play(LaggedStart(*[FadeIn(d, shift=UP * 0.15) for d in direct], lag_ratio=0.5), run_time=2.0)
        self.at_word(n, "pattern")
        self.play(FadeIn(no_pattern, scale=1.1))
        self.at_word(n, "Opposites")
        self.play(Indicate(VGroup(block.word[0], block.code[0]), color=BAD))
        self.wait_for_narration(n)

        # HEAR: reverse SMART -> TRAMS; every shift is -1.  SEE: the word row
        # flips in place; the red row is replaced by a green row of -1.
        after = block.shift_row([-1] * 5, color=GOOD)
        rule = self.caption("Rule: reverse the word, then shift each letter back by one", GOOD)
        n = self.narrate(
            id="ex3_03",
            text="So try reversal. SMART written backwards is TRAMS. Now compare TRAMS with SQZLR. T to S is "
                 "minus one, R to Q is minus one, and every letter is minus one. The rule is: reverse the word, "
                 "then shift each letter back by one.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "backwards")
        self.play(FadeOut(no_pattern), FadeOut(direct), self.reverse_row(block.word))
        self.at_word(n, "minus", occurrence=1)
        self.play(FadeIn(after[0], shift=UP * 0.15))
        self.at_word(n, "minus", occurrence=2)
        self.play(FadeIn(after[1], shift=UP * 0.15))
        self.at_word(n, "every")
        self.play(LaggedStart(*[FadeIn(a, shift=UP * 0.15) for a in after[2:]], lag_ratio=0.3))
        self.at_word(n, "rule")
        self.play(FadeIn(rule, shift=UP * 0.2))
        self.wait_for_narration(n)

        # HEAR: BRAIN -> NIARB -> MHZQA.  SEE: BRAIN flips to NIARB, then each
        # code letter on its "becomes" / "wraps".
        brain = CodeBlock("BRAIN", "MHZQA", xs, word_y=1.25, code_y=-0.3)
        back = brain.shift_row([-1] * 5, color=GOOD)
        n = self.narrate(
            id="ex3_04",
            text="Apply it to BRAIN. Reversed, it's NIARB. Shift each letter back by one: N becomes M, I becomes H, "
                 "A wraps around to Z, R becomes Q, and B becomes A.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(VGroup(block.word, block.arrows, block.code, after)))
        self.at_word(n, "BRAIN")
        self.play(FadeIn(brain.word, shift=DOWN * 0.2))
        self.at_word(n, "Reversed")
        self.play(self.reverse_row(brain.word))
        cues = [("becomes", 1), ("becomes", 2), ("wraps", 1), ("becomes", 3), ("becomes", 4)]
        for k, (spoken, occurrence) in enumerate(cues):
            self.at_word(n, spoken, occurrence=occurrence)
            self.play(GrowArrow(brain.arrows[k]), FadeIn(brain.code[k], shift=DOWN * 0.15), FadeIn(back[k]),
                      run_time=0.45)
        self.wait_for_narration(n)

        answer = pill("BRAIN  →  MHZQA", GOOD, size=LABEL).next_to(back, DOWN, buff=0.35)
        n = self.narrate(
            id="ex3_05",
            text="The code is MHZQA.",
            voice="default",
            subtitle=True,
        )
        self.play(*[mark_tile(t, GOOD) for t in brain.code], FadeIn(answer, scale=1.1))
        self.validator.check_in_frame(VGroup(question, brain.word, answer, rule))
        self.wait_for_narration(n)

        # HEAR: the wrap-around in the middle.  SEE: Z framed, "A − 1 = Z".
        wrap_tag = pill("A − 1 = Z", FOCUS, size=SMALL).next_to(back[2], DOWN, buff=0.15)
        n = self.narrate(
            id="ex3_06",
            text="Notice the wrap-around in the middle, where A minus one became Z. Questions that combine two steps "
                 "often include a wrap-around, because it catches careless solvers.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "minus")
        self.play(FadeOut(answer), mark_tile(brain.code[2], FOCUS), FadeIn(wrap_tag, shift=UP * 0.1))
        self.at_word(n, "careless")
        self.play(Circumscribe(brain.code[2], color=FOCUS))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S08_example_reversal")

    # ======================================== 9. EXAM APPLICATION ==========

    def exam_application(self):
        self.scene_start("S09_exam", title="Exam Application")

        rows = self.step_rows([
            ("Write the shift row", ANCHOR),
            ("Constant?  →  apply it", GOOD),
            ("Pattern (+1, +2, +3 …)?  →  extend it", FWD),
            ("Irregular?  →  test sum 27, then test reversal", OPP),
            ("Apply to the new word;  check for wrap-around", FOCUS),
        ], SAFE_W - 0.8)
        heading = text("The exam routine", LABEL, MUTED, BOLD)
        routine = self.card(VGroup(heading, rows).arrange(DOWN, buff=0.3, aligned_edge=LEFT)).move_to(UP * 0.6)
        self.validator.check_in_frame(routine)

        n = self.narrate(
            id="exam_01",
            text="In the exam, follow the same short routine every time.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(routine[0]), FadeIn(heading))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_02",
            text="Write the shift row. If it's constant, apply it. If it follows a pattern, extend it. If it's "
                 "irregular, test opposites, and then test reversal. Finally, apply the rule to the new word, "
                 "watching for wrap-around.",
            voice="default",
            subtitle=True,
        )
        for row, spoken in zip(rows, ["Write", "constant", "pattern", "irregular", "Finally"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.5)
        self.wait_for_narration(n)

        # HEAR: the three designed wrong options.  SEE: three red trap tags.
        traps = VGroup(pill("wrong direction", BAD, size=SMALL), pill("forgot the reversal", BAD, size=SMALL),
                       pill("wrap-around slip", BAD, size=SMALL)).arrange(RIGHT, buff=0.35)
        traps.move_to(UP * BOTTOM_Y)
        n = self.narrate(
            id="exam_03",
            text="Examiners design the wrong options carefully. One option usually follows the right rule but in the "
                 "wrong direction. Another applies the rule correctly but forgets the reversal. And a third gets the "
                 "wrap-around wrong. The routine protects you from all three.",
            voice="default",
            subtitle=True,
        )
        for trap, spoken in zip(traps, ["direction", "forgets", "third"]):
            self.at_word(n, spoken)
            self.play(FadeIn(trap, shift=UP * 0.2), run_time=0.4)
        self.at_word(n, "protects")
        self.play(Circumscribe(routine, color=GOOD, run_time=1.2))
        self.validator.check_in_frame(VGroup(routine, traps))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S09_exam")

    # =========================================== 10. COMMON MISTAKE ==========

    def common_mistake(self):
        self.scene_start("S10_mistake", title="Common Mistake")

        mat = CodeBlock("MAT", "NBU", column_xs(3, 2.2), word_y=1.9, code_y=0.3)
        opp_tag = pill("opposite?", FOCUS, size=SMALL).next_to(mat.arrows[0], LEFT, buff=0.2)
        plus = VGroup(*[pill("+1", GOOD, size=SMALL).next_to(a, RIGHT, buff=0.2) for a in mat.arrows])

        # HEAR: deciding from the first letter.  SEE: M -> N tagged "opposite?",
        # then the other letters reveal +1 everywhere.
        n = self.narrate(
            id="mistake_01",
            text="The first common mistake is deciding the rule from the first letter or two. As we saw in the "
                 "Alphabet Test, M to N could be opposite coding or a plus-one shift. Only the full shift row tells "
                 "you which. Verify the rule on every letter before applying it.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(mat.word), FadeIn(mat.code[0]), GrowArrow(mat.arrows[0]))
        self.at_word(n, "opposite")
        self.play(FadeIn(opp_tag, shift=RIGHT * 0.1))
        self.at_word(n, "full")
        self.play(GrowArrow(mat.arrows[1]), GrowArrow(mat.arrows[2]), FadeIn(mat.code[1:]))
        self.play(LaggedStart(*[FadeIn(p, shift=LEFT * 0.1) for p in plus], lag_ratio=0.3))
        self.at_word(n, "Verify")
        cap = self.caption("Verify the rule on every letter", FOCUS)
        self.play(FadeIn(cap, shift=UP * 0.2), *[mark_tile(t, GOOD) for t in mat.code])
        self.validator.check_in_frame(VGroup(opp_tag, mat.word, plus, cap))
        self.wait_for_narration(n)

        # HEAR: decoding the wrong way.  SEE: ✗ +2 -> HSK, ✓ -2 -> DOG.
        wrong = self.card(VGroup(text("✗", 36, BAD, BOLD), text("Decode FQI with +2  →  HSK", LABEL, BAD))
                          .arrange(RIGHT, buff=0.25), color=BAD)
        right = self.card(VGroup(text("✓", 36, GOOD, BOLD), text("Decode FQI with −2  →  DOG", LABEL, GOOD))
                          .arrange(RIGHT, buff=0.25), color=GOOD)
        VGroup(wrong, right).arrange(DOWN, buff=0.35).move_to(UP * 0.8)
        n = self.narrate(
            id="mistake_02",
            text="The second mistake is shifting the wrong way when decoding. If the code adds two, recovering the "
                 "word subtracts two. It helps to say it aloud: word to code: apply; code to word: undo.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(VGroup(mat.word, mat.code, mat.arrows, opp_tag, plus, cap)))
        self.at_word(n, "wrong")
        self.play(FadeIn(wrong, shift=RIGHT * 0.3))
        self.at_word(n, "subtracts")
        self.play(FadeIn(right, shift=LEFT * 0.3))
        self.at_word(n, "aloud")
        cap = self.caption("Word → code: apply   ·   code → word: undo", FOCUS)
        self.play(FadeIn(cap, shift=UP * 0.2))
        self.wait_for_narration(n)

        # HEAR: Y + 3 = 28 -> subtract 26 -> 2 = B.  SEE: the working, line by line.
        line1 = math_line(r"\text{Y}", "+", "3", "=", "25", "+", "3", "=", "28",
                          colors={"28": BAD}, size=40).move_to(UP * 0.8)
        stop = pill("no 28th letter!", BAD, size=SMALL).next_to(line1, RIGHT, buff=0.35)
        line2 = math_line("28", "-", "26", "=", "2", r"\rightarrow", r"\text{B}",
                          colors={"2": GOOD, r"\text{B}": GOOD}, size=40).next_to(line1, DOWN, buff=0.5)
        n = self.narrate(
            id="mistake_03",
            text="The third mistake is wrap-around. A learner shifts Y by plus three, gets position twenty-eight, "
                 "and stops. Twenty-eight minus twenty-six is two, so the answer is B.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(VGroup(wrong, right, cap)))
        self.at_word(n, "shifts")
        self.play(Write(line1))
        self.at_word(n, "stops")
        self.play(FadeIn(stop, scale=1.1))
        self.at_word(n, "minus")
        self.play(Write(line2))
        self.at_word(n, "answer")
        self.play(Circumscribe(line2[-1], color=GOOD))
        self.validator.check_in_frame(VGroup(line1, stop, line2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S10_mistake")

    # ================================================ 11. PRACTICE ==========

    def practice(self):
        self.scene_start("S11_practice", title="Practice Question")

        turn = pill("Your turn", FOCUS, size=LABEL).move_to(UP * (CARD_TOP - 0.35))
        paper = CodeBlock("PAPER", "QCSIW", column_xs(5, 1.35), word_y=1.1, code_y=-0.5)
        pencil = VGroup(pill("PENCIL", INK, size=LABEL, fill_opacity=0.05), text("→", LABEL, MUTED),
                        pill("?", FOCUS, size=LABEL)).arrange(RIGHT, buff=0.35).move_to(DOWN * 2.0)

        n = self.narrate(
            id="practice_01",
            text="Try this one.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(turn))
        self.wait_for_narration(n)

        # SILENCE (pause_after): countdown ring while the learner thinks.
        n = self.narrate(
            id="practice_02",
            text="If PAPER is coded as QCSIW, how is PENCIL coded?",
            voice="default",
            subtitle=True,
            pause_after=8.0,
        )
        self.play(FadeIn(paper.word), FadeIn(paper.arrows), FadeIn(paper.code))
        self.at_word(n, "PENCIL")
        self.play(FadeIn(pencil, shift=UP * 0.2))
        self.validator.check_in_frame(VGroup(turn, paper.word, pencil))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        self.clear_stage()
        self.scene_end("S11_practice")

    # ================================================== 12. ANSWER ==========

    def answer(self):
        self.scene_start("S12_answer", title="Answer and Explanation")

        paper = CodeBlock("PAPER", "QCSIW", column_xs(5, 1.1, LEFT_ZONE), word_y=1.6, code_y=0.1, side=0.75)
        paper_shifts = paper.shift_row([shift_of(a, b) for a, b in zip("PAPER", "QCSIW")], color=FWD)
        pencil = CodeBlock("PENCIL", "QGQGNR", column_xs(6, 0.98, RIGHT_ZONE), word_y=1.6, code_y=0.1, side=0.7)
        pencil_shifts = pencil.shift_row([1, 2, 3, 4, 5, 6], color=FWD)
        divider = DashedLine(UP * 2.2, DOWN * 1.2, color=MUTED)

        n = self.narrate(
            id="answer_01",
            text="Write the shift row for PAPER and QCSIW.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(paper.word), FadeIn(paper.arrows), FadeIn(paper.code))
        self.wait_for_narration(n)

        # HEAR: +1 ... +5, progressive.  SEE: one pill per spoken shift.
        n = self.narrate(
            id="answer_02",
            text="P to Q is plus one. A to C is plus two. P to S is plus three. E to I is plus four. "
                 "And R to W is plus five. It's a progressive shift.",
            voice="default",
            subtitle=True,
        )
        for k in range(5):
            self.at_word(n, "plus", occurrence=k + 1)
            self.play(FadeIn(paper_shifts[k], shift=UP * 0.15), run_time=0.4)
        self.at_word(n, "progressive")
        self.play(Circumscribe(paper_shifts, color=FWD))
        self.wait_for_narration(n)

        # HEAR: extend to +6; letter by letter.  SEE: PENCIL on the right. The
        # first "plus" is "plus six", so letter k is on occurrence k + 2.
        n = self.narrate(
            id="answer_03",
            text="PENCIL has six letters, so extend the shifts to plus six. P plus one is Q. E plus two is G. "
                 "N plus three is Q. C plus four is G. I plus five is N. And L plus six is R.",
            voice="default",
            subtitle=True,
        )
        self.play(Create(divider), FadeIn(pencil.word))
        for k in range(6):
            self.at_word(n, "plus", occurrence=k + 2)
            self.play(GrowArrow(pencil.arrows[k]), FadeIn(pencil.code[k], shift=DOWN * 0.15),
                      FadeIn(pencil_shifts[k]), run_time=0.45)
        self.wait_for_narration(n)

        answer = pill("PENCIL  →  QGQGNR", GOOD, size=LABEL).next_to(pencil_shifts, DOWN, buff=0.45)
        n = self.narrate(
            id="answer_04",
            text="The code is QGQGNR.",
            voice="default",
            subtitle=True,
        )
        self.play(*[mark_tile(t, GOOD) for t in pencil.code], FadeIn(answer, scale=1.1))
        self.validator.check_in_frame(VGroup(paper.word, paper_shifts, pencil.word, answer))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answer_05",
            text="If you got a different answer, check the last letter. Stopping the pattern at plus five is the "
                 "usual slip.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "last")
        self.play(Indicate(VGroup(pencil.code[5], pencil_shifts[5]), color=FOCUS, scale_factor=1.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S12_answer")

    # ========================================== 13. QUICK REVISION ==========

    def quick_revision(self):
        self.scene_start("S13_revision", title="Quick Revision")

        card_w, card_h = SAFE_W - 1.0, 5.4
        items = [
            ("Always write the shift row (code position − word position)", ANCHOR),
            ("Constant → shift · growing pattern → progressive · sum 27 → opposite", FWD),
            ("Irregular → try reversal, then write the shift row again", OPP),
            ("The alphabet is a circle: Z + 1 = A,  A − 1 = Z", FOCUS),
            ("Decode by undoing the rule", REV),
            ("Verify on every letter", GOOD),
        ]
        bullets = VGroup(*[VGroup(Dot(radius=0.07, color=c), fitted_text(s, card_w - 1.4, BODY, c, max_lines=2))
                           .arrange(RIGHT, buff=0.3) for s, c in items]).arrange(DOWN, buff=0.25, aligned_edge=LEFT)
        board = self.card(bullets, width=card_w, height=card_h).move_to(DOWN * 0.1)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="revision_01",
            text="Let's revise.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(board[0]))
        self.wait_for_narration(n)

        n = self.narrate(
            id="revision_02",
            text="The shift row is the main tool: write how far each letter moved. A constant shift row means a "
                 "simple shift. A growing pattern means a progressive shift. Positions that add to twenty-seven mean "
                 "opposites. And if nothing fits, try reversing the word first.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(bullets[0], shift=RIGHT * 0.2))
        self.at_word(n, "constant")
        self.play(FadeIn(bullets[1], shift=RIGHT * 0.2))
        self.at_word(n, "nothing")
        self.play(FadeIn(bullets[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="revision_03",
            text="The alphabet is circular, so Z plus one is A. To decode, undo the rule. "
                 "And always check the rule on every letter.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(bullets[3], shift=RIGHT * 0.2))
        self.at_word(n, "decode")
        self.play(FadeIn(bullets[4], shift=RIGHT * 0.2))
        self.at_word(n, "always")
        self.play(FadeIn(bullets[5], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S13_revision")

    # ================================================= 14. CLOSING ==========
    # Purpose: teaser for Number Coding: letters turning into numbers.

    def closing(self):
        self.scene_start("S14_closing", title="Closing")

        xs = column_xs(3, 1.6)
        letters = VGroup(*[tile(ch, 1.0).move_to(RIGHT * x + UP * 0.8) for ch, x in zip("CAT", xs)])
        numbers = VGroup(*[tile(str(pos(ch)), 1.0, FWD).move_to(RIGHT * x + UP * 0.8) for ch, x in zip("CAT", xs)])
        total = math_line("3", "+", "1", "+", "20", "=", "24", colors={"24": GOOD}, size=48).move_to(DOWN * 0.9)
        nxt = pill("Next:  Number Coding", ANCHOR, size=BODY).move_to(DOWN * 2.3)

        n = self.narrate(
            id="closing_01",
            text="Letters can also be coded as numbers. A word might be written as a string of positions, or as a "
                 "single total. In the next topic, we'll see how number coding works, and how the same idea of "
                 "positions makes it easy to crack.",
            voice="default",
            subtitle=True,
        )
        self.play(LaggedStart(*[FadeIn(t, shift=UP * 0.2) for t in letters], lag_ratio=0.2))
        self.at_word(n, "string")
        self.play(*[ReplacementTransform(a, b) for a, b in zip(letters, numbers)], run_time=1.2)
        self.at_word(n, "total")
        self.play(Write(total))
        self.at_word(n, "next")
        self.play(FadeIn(nxt, scale=1.1))
        self.validator.check_in_frame(VGroup(numbers, total, nxt))
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S14_closing")

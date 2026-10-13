"""
animation.py for the LMS video generator.

Course : Pre-C-CAT - Section A
Module : Module 1 - Logical Reasoning
Lesson : Lesson 2 - Coding & Decoding I: Letter and Number Coding
Topic  : Pattern Identification (Topic 3)

Source script:
  C:\\Scripts\\Section A\\Module 1 - Logical Reasoning\\Lesson 02 - Coding & Decoding I\\
  Topic 3 - Pattern Identification.md

Built on the golden-reference pattern:
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``.

Opening: not the first video of the course, so no spoken course welcome.
The module > lesson > topic trail is shown on screen (silent), followed by a
one-idea recap of Topic 2 (the rule tester) and what this video covers.

Script note: the Common Mistake card says "fits 5 of 8 letters" but the
narration (correctly) says the +1 shift fits six of COMPUTER's eight letters;
the card here says 6 of 8 to match.

Section map (script heading -> VISUAL PLAN scene):
  S00 Intro (trail + recap)       -> -
  S01 Opening Hook                -> scene 1
  S02 Concept                     -> scene 2
  S03 The procedure               -> scene 3
  S04 Rearrangement patterns      -> scene 4
  S05 Alternating shift           -> scene 5
  S06-S08 Examples 1-3            -> scene 6
  S09 Exam Application            -> scene 7
  S10 Common Mistake              -> scene 8
  S11-S12 Practice / Answers      -> scene 9
  S13-S14 Revision / Closing      -> scene 10
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

# Semantic colours: one meaning each (same palette as the earlier topics).
FWD = "#4FC3F7"        # +shifts / odd positions / substitution
REV = "#F48FB1"        # -shifts / even positions
ANCHOR = "#FFB74D"     # the shift row / rearrangement
OPP = "#CE93D8"        # opposite letters / reversal
FOCUS = "#FFD54F"      # "look here"
GOOD = "#66BB6A"       # rule confirmed / answer
BAD = "#EF5350"        # no pattern / wrong

FONT = "Segoe UI"
MIN_FONT = 22          # readable floor: text is never shrunk below this
TITLE = 46
BODY = 30
LABEL = 28
SMALL = 24
NUM = 22
MATH = 44

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def pos(ch):
    return ALPHABET.index(ch) + 1


def shift_of(a, b):
    """How far letter ``a`` moved to become ``b``, in -12..+13 (wrap-around aware)."""
    d = (pos(b) - pos(a)) % 26
    return d - 26 if d > 13 else d


def raw_shift(a, b):
    """Straight distance from ``a`` to ``b`` (no wrap-around), as the script reads
    COMPUTER's direct row: C -> R is +15, R -> C is -15."""
    return pos(b) - pos(a)


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


# ==================================================== diagram helpers ====

def tile(ch, side=0.8, color=INK):
    """One letter in a rounded square."""
    sq = RoundedRectangle(corner_radius=0.1, width=side, height=side, stroke_color=MUTED,
                          stroke_width=2, fill_color=CELL, fill_opacity=1)
    return VGroup(sq, text(ch, int(side * 52), color, BOLD).move_to(sq))


def mark_tile(t, color):
    return AnimationGroup(t[0].animate.set_fill(color, 0.3).set_stroke(color, 3), t[1].animate.set_color(color))


def column_xs(n, spacing, centre=ORIGIN):
    """x positions of ``n`` evenly spaced columns centred on ``centre``."""
    return [centre[0] + (k - (n - 1) / 2) * spacing for k in range(n)]


def word_row(word, xs, y, side=0.8, color=INK):
    """A word as tiles in fixed columns."""
    return VGroup(*[tile(ch, side, color).move_to(RIGHT * x + UP * y) for ch, x in zip(word, xs)])


def alt_colors(n):
    """Odd positions (1st, 3rd ...) in FWD, even positions in REV."""
    return [FWD if k % 2 == 0 else REV for k in range(n)]


class CodeBlock(VGroup):
    """A word row over its code row, one column per letter. Parts are exposed
    but not added, so each can be revealed on its own beat."""

    def __init__(self, word, code, xs, word_y=1.2, code_y=-0.3, side=0.8):
        super().__init__()
        self.word = word_row(word, xs, word_y, side)
        self.code = word_row(code, xs, code_y, side)
        self.arrows = VGroup(*[Arrow(a.get_bottom(), b.get_top(), buff=0.1, color=MUTED, stroke_width=4,
                                     max_tip_length_to_length_ratio=0.2) for a, b in zip(self.word, self.code)])

    def shift_row(self, shifts, color=ANCHOR, size=SMALL):
        """Pills under the code row, one per column. ``color`` may be a list."""
        colors = color if isinstance(color, list) else [color] * len(shifts)
        return VGroup(*[pill(shift_label(d), c, size=size).next_to(t, DOWN, buff=0.22)
                        for d, c, t in zip(shifts, colors, self.code)])


def spread(row, groups, gap):
    """Animation: pull the letter groups of ``row`` apart by ``gap`` (negative
    ``gap`` closes them again). ``groups`` are lists of tile indices."""
    n = len(groups)
    anims = []
    for g_i, g in enumerate(groups):
        offset = (g_i - (n - 1) / 2) * gap
        anims += [row[k].animate.shift(RIGHT * offset) for k in g]
    return AnimationGroup(*anims, run_time=0.8)


def reverse_groups(row, groups):
    """Animation: reverse the order of the tiles inside each group, in place."""
    anims = []
    for g in groups:
        centres = [row[k].get_center() for k in g]
        anims += [row[k].animate.move_to(centres[len(g) - 1 - j]) for j, k in enumerate(g)]
    return AnimationGroup(*anims, run_time=1.2)


# ============================================================= lesson ====

class PatternIdentificationVideo(LMSScene):
    lesson_title = "Pattern Identification"

    def construct(self):
        self.camera.background_color = BG

        self.lesson_intro()
        self.hook()
        self.concept()
        self.procedure()
        self.rearrangements()
        self.alternating()
        self.example_halves()
        self.example_alternating()
        self.example_fixed_ends()
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
                      ).arrange(DOWN, buff=0.22, aligned_edge=LEFT)

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

    # ========================================= 0. LESSON INTRO ==========
    # Purpose: where we are (silent trail), last time (one idea), today.

    def lesson_intro(self):
        self.scene_start("S00_intro", title="Lesson Introduction")

        crumb = self.breadcrumb("Module 1 · Logical Reasoning", "Lesson 2 · Coding & Decoding I", "Topic 3")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        last = pill("Last time", MUTED, size=SMALL)
        chain = VGroup(pill("forward sum", FWD, size=LABEL), text("→", LABEL, MUTED),
                       pill("reverse sum", REV, size=LABEL), text("→", LABEL, MUTED),
                       pill("simple operation", ANCHOR, size=LABEL)).arrange(RIGHT, buff=0.3)
        fit_width(chain, SAFE_W)
        tester = text("the rule tester", LABEL, MUTED, BOLD)
        recap = VGroup(last, tester, chain).arrange(DOWN, buff=0.4).move_to(DOWN * 0.1)
        self.validator.check_in_frame(VGroup(crumb, recap))

        # SEE (silent): the trail.  HEAR: the rule tester from last time.
        n = self.narrate(
            id="intro_01",
            text="Last time, you cracked number codes with the rule tester: forward sum, then reverse sum, "
                 "then a simple operation.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.play(FadeIn(last), FadeIn(tester))
        for k, spoken in zip([0, 2, 4], ["forward", "reverse", "operation"]):
            self.at_word(n, spoken)
            self.play(FadeIn(chain[k], shift=UP * 0.2), *([FadeIn(chain[k - 1])] if k else []), run_time=0.5)
        self.wait_for_narration(n)

        # HEAR: today, one procedure for any letter code.  SEE: the title.
        title = fitted_text("Pattern Identification", SAFE_W, 68, INK, BOLD)
        underline = Line(LEFT, RIGHT, color=GOOD, stroke_width=5).set_width(title.width * 0.6)
        VGroup(title, underline).arrange(DOWN, buff=0.2).move_to(UP * 0.2)
        n = self.narrate(
            id="intro_02",
            text="In this video, we put everything together into one procedure for identifying any letter code.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(recap, shift=UP * 0.3))
        self.at_word(n, "procedure")
        self.play(Write(title), run_time=1.1)
        self.play(GrowFromCenter(underline))
        self.wait_for_narration(n)

        # HEAR: the four objectives.  SEE: one row per objective, on its word.
        goals = [
            ("Decide: rearrangement or substitution?", ANCHOR),
            ("Name the exact pattern", FWD),
            ("Spot letters that don't change", FOCUS),
            ("Encode and decode multi-step codes", GOOD),
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
            text="By the end of this video, you'll be able to decide whether a code rearranges or substitutes, name "
                 "the exact pattern, spot letters that don't change, and encode or decode multi-step codes accurately.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(underline), ReplacementTransform(title, small_title), run_time=0.8)
        self.play(FadeIn(objectives[0]), FadeIn(heading))
        for row, spoken in zip(rows, ["decide", "name", "spot", "encode"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.5)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_intro")

    # ================================================= 1. HOOK ==========
    # Purpose: a code whose direct shift row looks like chaos.

    def hook(self):
        self.scene_start("S01_hook", title="Opening Hook")

        question = self.question_card("COMPUTER → RFUVQNPC.   How is MEDICINE written?")
        block = CodeBlock("COMPUTER", "RFUVQNPC", column_xs(8, 1.25), word_y=1.1, code_y=-0.4, side=0.75)
        direct = block.shift_row([raw_shift(a, b) for a, b in zip("COMPUTER", "RFUVQNPC")], color=BAD)
        self.validator.check_in_frame(VGroup(question, block.word, direct))

        n = self.narrate(
            id="hook_01",
            text="In a certain code, COMPUTER is written as RFUVQNPC. How would MEDICINE be written?",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(block.word, shift=DOWN * 0.2))
        self.at_word(n, "RFUVQNPC")
        self.play(FadeIn(block.arrows), FadeIn(block.code, shift=DOWN * 0.2))
        self.at_word(n, "MEDICINE")
        self.play(FadeIn(question, shift=DOWN * 0.3))
        self.wait_for_narration(n)

        # HEAR: the direct shift row; chaos.  SEE: red shifts, one per word.
        n = self.narrate(
            id="hook_02",
            text="If you write the direct shift row, you get plus fifteen, minus nine, plus eight, and so on. "
                 "It looks like chaos.",
            voice="default",
            subtitle=True,
        )
        for k, (spoken, occurrence) in enumerate([("plus", 1), ("minus", 1), ("plus", 2)]):
            self.at_word(n, spoken, occurrence=occurrence)
            self.play(FadeIn(direct[k], shift=UP * 0.15), run_time=0.4)
        self.at_word(n, "so")
        self.play(LaggedStart(*[FadeIn(d, shift=UP * 0.15) for d in direct[3:]], lag_ratio=0.2))
        self.at_word(n, "chaos")
        self.play(Wiggle(direct))
        self.wait_for_narration(n)

        # HEAR: a procedure, not a formula.  SEE: caption.
        n = self.narrate(
            id="hook_03",
            text="But this is a real, solvable code with a simple rule. What's missing isn't a formula. It's a "
                 "procedure: a fixed order of tests that finds the rule without guessing. That's what this topic is about.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "procedure")
        cap = self.caption("Not a formula:  a procedure, a fixed order of tests", GOOD)
        self.play(FadeIn(cap, shift=UP * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S01_hook")

    # ============================================== 2. CONCEPT ==========
    # Purpose: every code rearranges, substitutes, or both.

    def concept(self):
        self.scene_start("S02_concept", title="Concept Introduction")

        root = pill("Word  →  Code", INK, size=BODY, fill_opacity=0.06).move_to(UP * 2.3)
        card_w = ZONE_W - 0.4
        rearr = self.card(VGroup(text("REARRANGEMENT", LABEL, ANCHOR, BOLD),
                                 fitted_text("same letters, new order", card_w - 0.7, SMALL, INK),
                                 pill("TIGER  →  REGIT", ANCHOR, size=SMALL)).arrange(DOWN, buff=0.22),
                          width=card_w, color=ANCHOR).move_to(LEFT_ZONE + DOWN * 0.3)
        subst = self.card(VGroup(text("SUBSTITUTION", LABEL, FWD, BOLD),
                                 fitted_text("new letters", card_w - 0.7, SMALL, INK),
                                 pill("MANGO  →  OCPIQ", FWD, size=SMALL)).arrange(DOWN, buff=0.22),
                          width=card_w, color=FWD).move_to(RIGHT_ZONE + DOWN * 0.3)
        a1 = Arrow(root.get_bottom(), rearr.get_top(), buff=0.15, color=ANCHOR, stroke_width=4)
        a2 = Arrow(root.get_bottom(), subst.get_top(), buff=0.15, color=FWD, stroke_width=4)
        self.validator.check_in_frame(VGroup(root, rearr, subst))

        # HEAR: rearranges or substitutes.  SEE: the two branches, on their words.
        n = self.narrate(
            id="concept_01",
            text="Every letter code does one of two things, or both. It either rearranges the letters of the word, "
                 "or it substitutes them with other letters.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(root, shift=DOWN * 0.2))
        self.at_word(n, "rearranges")
        self.play(GrowArrow(a1), FadeIn(rearr[0]), FadeIn(rearr[1][0]))
        self.at_word(n, "substitutes")
        self.play(GrowArrow(a2), FadeIn(subst[0]), FadeIn(subst[1][0]))
        self.wait_for_narration(n)

        # HEAR: definitions.  SEE: each branch's description and example.
        n = self.narrate(
            id="concept_02",
            text="In a rearrangement, the code contains exactly the same letters as the word, just in a different "
                 "order. In a substitution, the letters themselves change.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "rearrangement")
        self.play(FadeIn(rearr[1][1:], shift=UP * 0.15))
        self.at_word(n, "substitution")
        self.play(FadeIn(subst[1][1:], shift=UP * 0.15))
        self.wait_for_narration(n)

        # HEAR: decide, narrow down, check.  SEE: caption.
        n = self.narrate(
            id="concept_03",
            text="Pattern identification means deciding which of these is happening first, then narrowing it down to "
                 "the exact rule, and finally checking that rule on every letter.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "deciding")
        cap = self.caption("Decide  →  narrow down  →  check every letter", GOOD)
        self.play(FadeIn(cap, shift=UP * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_concept")

    # ============================================= 3. THE PROCEDURE ==========
    # Purpose: the identification flowchart, revealed branch by branch.

    def procedure(self):
        self.scene_start("S03_procedure", title="Explanation - The Procedure")

        start = pill("Does the code use the same letters as the word?", FOCUS, size=LABEL).move_to(UP * 2.6)
        card_w = ZONE_W - 0.4
        left = self.card(VGroup(text("Yes  →  REARRANGEMENT", SMALL, ANCHOR, BOLD),
                                fitted_text("full reversal  ·  halves reversed  ·  pairs swapped", card_w - 0.7,
                                            SMALL, INK, max_lines=2)).arrange(DOWN, buff=0.18, aligned_edge=LEFT),
                         width=card_w, color=ANCHOR).move_to(LEFT_ZONE + UP * 0.7)
        right = self.card(VGroup(text("No  →  SUBSTITUTION", SMALL, FWD, BOLD),
                                 fitted_text("shift row: constant / progressive / alternating  →  test 27  →  "
                                             "reverse and re-check", card_w - 0.7, SMALL, INK, max_lines=3))
                          .arrange(DOWN, buff=0.18, aligned_edge=LEFT),
                          width=card_w, color=FWD).move_to(RIGHT_ZONE + UP * 0.7)
        a_yes = Arrow(start.get_bottom(), left.get_top(), buff=0.15, color=ANCHOR, stroke_width=4)
        a_no = Arrow(start.get_bottom(), right.get_top(), buff=0.15, color=FWD, stroke_width=4)
        ends = pill("Watch for letters that don't change, especially at the ends", FOCUS, size=SMALL)
        ends.move_to(DOWN * 1.35)
        verify = pill("Verify on every letter  →  apply", GOOD, size=LABEL).move_to(DOWN * 2.35)
        d1 = Arrow(left.get_bottom(), ends.get_top() + LEFT * 1.5, buff=0.12, color=MUTED, stroke_width=3)
        d2 = Arrow(right.get_bottom(), ends.get_top() + RIGHT * 1.5, buff=0.12, color=MUTED, stroke_width=3)
        d3 = Arrow(ends.get_bottom(), verify.get_top(), buff=0.1, color=MUTED, stroke_width=3)
        self.validator.check_in_frame(VGroup(start, left, right, ends, verify))

        n = self.narrate(
            id="proc_01",
            text="Here's the full procedure.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(start, shift=DOWN * 0.2))
        self.wait_for_narration(n)

        # HEAR: step one, compare the letters.  SEE: the question box pulses.
        n = self.narrate(
            id="proc_02",
            text="Step one: compare the letters. Is the code simply the word's letters in a new order? A quick way to "
                 "tell is to look for the same letters, or to sort both mentally.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "compare")
        self.play(Indicate(start, color=FOCUS, scale_factor=1.05))
        self.wait_for_narration(n)

        # HEAR: yes -> rearrangement tests.  SEE: the left branch.
        n = self.narrate(
            id="proc_03",
            text="If yes, it's a rearrangement. Test the common ones: is the whole word reversed? Is each half "
                 "reversed separately? Are neighbouring letters swapped in pairs?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "rearrangement")
        self.play(GrowArrow(a_yes), FadeIn(left, shift=DOWN * 0.2))
        self.wait_for_narration(n)

        # HEAR: no -> substitution tests, in order.  SEE: the right branch.
        n = self.narrate(
            id="proc_04",
            text="If no, it's a substitution. Write the shift row. Is it constant, progressive, or alternating? If "
                 "it's irregular, test opposites with the sum of twenty-seven. If that fails, reverse the word and "
                 "write the shift row again.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "substitution")
        self.play(GrowArrow(a_no), FadeIn(right, shift=DOWN * 0.2))
        self.wait_for_narration(n)

        # HEAR: unchanged letters at the ends.  SEE: the watch-for pill.
        n = self.narrate(
            id="proc_05",
            text="At every stage, watch for letters that don't change, especially at the ends of the word. Some codes "
                 "apply the rule only to the middle letters.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "watch")
        self.play(GrowArrow(d1), GrowArrow(d2), FadeIn(ends, shift=UP * 0.15))
        self.wait_for_narration(n)

        n = self.narrate(
            id="proc_06",
            text="And finally, verify the rule on every letter before you apply it.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "verify")
        self.play(GrowArrow(d3), FadeIn(verify, scale=1.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_procedure")

    # ===================================== 4. REARRANGEMENT PATTERNS ==========

    def rearrangements(self):
        self.scene_start("S04_rearrangement", title="Explanation - Rearrangement Patterns")

        xs = column_xs(6, 0.95, RIGHT * 0.8)
        system = word_row("SYSTEM", xs, 1.4, side=0.8)
        halves_tag = pill("halves reversal", ANCHOR, size=SMALL).move_to(LEFT * 5.2 + UP * 1.4)
        halves = [[0, 1, 2], [3, 4, 5]]
        garden = word_row("GARDEN", xs, -0.9, side=0.8)
        pairs_tag = pill("pair swap", OPP, size=SMALL).move_to(LEFT * 5.2 + DOWN * 0.9)
        pairs = [[0, 1], [2, 3], [4, 5]]
        system_code = pill("SYSMET", GOOD, size=LABEL).move_to(RIGHT * 0.8 + UP * 0.45)
        garden_code = pill("AGDRNE", GOOD, size=LABEL).move_to(RIGHT * 0.8 + DOWN * 1.85)
        self.validator.check_in_frame(VGroup(halves_tag, system, garden, garden_code))

        # HEAR: halves reversal.  SEE: SYSTEM splits in two, each half flips,
        # the halves rejoin as SYSMET.
        n = self.narrate(
            id="rear_01",
            text="The most common rearrangement is halves reversal. The word is cut in the middle, and each half is "
                 "written backwards. SYSTEM splits into S-Y-S and T-E-M. Reversed, they become S-Y-S and M-E-T. "
                 "Together, that's SYSMET.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(halves_tag), FadeIn(system, shift=DOWN * 0.2))
        self.at_word(n, "splits")
        self.play(spread(system, halves, 0.7))
        self.at_word(n, "Reversed")
        self.play(reverse_groups(system, halves))
        self.at_word(n, "Together")
        self.play(spread(system, halves, -0.7))
        self.play(FadeIn(system_code, shift=UP * 0.1))
        self.wait_for_narration(n)

        # HEAR: pair swap.  SEE: GARDEN splits into pairs, each pair swaps.
        n = self.narrate(
            id="rear_02",
            text="Another is the pair swap. Each pair of neighbouring letters trades places. "
                 "GARDEN becomes A-G, D-R, N-E: AGDRNE.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(pairs_tag), FadeIn(garden, shift=DOWN * 0.2))
        self.at_word(n, "trades")
        self.play(spread(garden, pairs, 0.5))
        self.at_word(n, "becomes")
        self.play(reverse_groups(garden, pairs))
        self.play(spread(garden, pairs, -0.5))
        self.play(FadeIn(garden_code, shift=UP * 0.1))
        self.wait_for_narration(n)

        # HEAR: track positions, not shifts.  SEE: caption.
        n = self.narrate(
            id="rear_03",
            text="In rearrangement codes, no letter changes, so the shift row isn't needed. What you track is "
                 "positions: where each letter of the word ends up in the code.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "positions")
        cap = self.caption("Rearrangement:  track positions, not shifts", ANCHOR)
        self.play(FadeIn(cap, shift=UP * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_rearrangement")

    # ========================================== 5. ALTERNATING SHIFT ==========

    def alternating(self):
        self.scene_start("S05_alternating", title="Explanation - Alternating Shift")

        block = CodeBlock("PLANT", "QKBMU", column_xs(5, 1.4), word_y=1.8, code_y=0.2, side=0.85)
        shifts = block.shift_row([shift_of(a, b) for a, b in zip("PLANT", "QKBMU")], color=alt_colors(5))
        odd = VGroup(*[block.word[k] for k in (0, 2, 4)])
        even = VGroup(*[block.word[k] for k in (1, 3)])
        pattern = pill("+1, −1, repeating", GOOD, size=LABEL).next_to(shifts, DOWN, buff=0.35)
        self.validator.check_in_frame(VGroup(block.word, shifts, pattern))

        # HEAR: odd positions one rule, even another.  SEE: PLANT, odd letters
        # pulse blue, even letters pulse pink.
        n = self.narrate(
            id="alt_01",
            text="Besides constant and progressive shifts, one more pattern appears often: the alternating shift. "
                 "Letters in odd positions follow one rule, and letters in even positions follow another.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(block.word), FadeIn(block.arrows), FadeIn(block.code))
        self.at_word(n, "odd")
        self.play(*[mark_tile(t, FWD) for t in odd])
        self.at_word(n, "even")
        self.play(*[mark_tile(t, REV) for t in even])
        self.wait_for_narration(n)

        # HEAR: +1, -1, +1 ...  SEE: shift pills, coloured by odd / even.
        n = self.narrate(
            id="alt_02",
            text="PLANT becomes QKBMU. P goes forward one, L goes back one, A goes forward one, and so on. "
                 "The pattern is plus one, minus one, repeating.",
            voice="default",
            subtitle=True,
        )
        for k, (spoken, occurrence) in enumerate([("forward", 1), ("back", 1), ("forward", 2)]):
            self.at_word(n, spoken, occurrence=occurrence)
            self.play(FadeIn(shifts[k], shift=UP * 0.15), run_time=0.4)
        self.at_word(n, "so")
        self.play(FadeIn(shifts[3:], shift=UP * 0.15))
        self.at_word(n, "repeating")
        self.play(FadeIn(pattern, scale=1.1))
        self.wait_for_narration(n)

        # HEAR: read every second value.  SEE: odd shifts, then even shifts.
        n = self.narrate(
            id="alt_03",
            text="When a shift row looks messy, try reading every second value. Alternating patterns are easy to miss "
                 "when you read the row straight through.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "second")
        self.play(Indicate(VGroup(*[shifts[k] for k in (0, 2, 4)]), color=FWD, scale_factor=1.2))
        self.play(Indicate(VGroup(*[shifts[k] for k in (1, 3)]), color=REV, scale_factor=1.2))
        cap = self.caption("Irregular shift row?  Read every second value", FOCUS)
        self.play(FadeIn(cap, shift=UP * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_alternating")

    # ================================ 6. EXAMPLE 1: HALVES REVERSAL ==========

    def example_halves(self):
        self.scene_start("S06_example_halves", title="Example 1 - Halves Reversal")

        question = self.question_card("SYSTEM → SYSMET.   How is NEARER coded?")
        pair = VGroup(pill("SYSTEM", INK, size=LABEL, fill_opacity=0.06), text("→", LABEL, MUTED),
                      pill("SYSMET", ANCHOR, size=LABEL)).arrange(RIGHT, buff=0.35).move_to(UP * 1.3)
        same = pill("same letters: S, Y, S, T, E, M  →  rearrangement", ANCHOR, size=SMALL).move_to(UP * 0.3)
        nearer = word_row("NEARER", column_xs(6, 0.95), -1.0, side=0.8)
        halves = [[0, 1, 2], [3, 4, 5]]
        answer = pill("NEARER  →  AENRER", GOOD, size=LABEL).move_to(DOWN * 2.2)
        self.validator.check_in_frame(VGroup(question, pair, nearer, answer))

        n = self.narrate(
            id="ex1_01",
            text="If SYSTEM is coded as SYSMET, how is NEARER coded?",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(question, shift=DOWN * 0.3), FadeIn(pair))
        self.wait_for_narration(n)

        # HEAR: same letters -> rearrangement; halves reversed.
        n = self.narrate(
            id="ex1_02",
            text="Step one: are the letters the same? SYSTEM and SYSMET both contain S, Y, S, T, E and M. So this is a "
                 "rearrangement. As we saw, each half has been reversed.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "contain")
        self.play(FadeIn(same, shift=UP * 0.15))
        self.at_word(n, "half")
        self.play(Indicate(pair[2], color=ANCHOR, scale_factor=1.1))
        self.wait_for_narration(n)

        # HEAR: NEA | RER -> AEN | RER.  SEE: split, flip, rejoin.
        n = self.narrate(
            id="ex1_03",
            text="NEARER splits into N-E-A and R-E-R. Reversing each half gives A-E-N and R-E-R. The code is AENRER.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(nearer, shift=DOWN * 0.2))
        self.at_word(n, "splits")
        self.play(spread(nearer, halves, 0.7))
        self.at_word(n, "Reversing")
        self.play(reverse_groups(nearer, halves))
        self.at_word(n, "code")
        self.play(spread(nearer, halves, -0.7))
        self.play(FadeIn(answer, scale=1.1))
        self.wait_for_narration(n)

        # HEAR: RER reads the same backwards.  SEE: the second half framed.
        n = self.narrate(
            id="ex1_04",
            text="Notice that R-E-R reads the same backwards, so the second half looks unchanged. A learner who "
                 "expected every letter to move might doubt the rule here. The rule is correct. It just happens to "
                 "leave a symmetric half unchanged.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "backwards")
        frame = SurroundingRectangle(VGroup(*[nearer[k] for k in (3, 4, 5)]), color=FOCUS, buff=0.1)
        self.play(Create(frame))
        self.at_word(n, "correct")
        cap = self.caption("A symmetric half looks unchanged; the rule still holds", FOCUS)
        self.play(FadeIn(cap, shift=UP * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_example_halves")

    # ============================ 7. EXAMPLE 2: ALTERNATING SHIFT ==========

    def example_alternating(self):
        self.scene_start("S07_example_alternating", title="Example 2 - Alternating Shift")

        question = self.question_card("PLANT → QKBMU.   How is CROWN coded?")
        plant = CodeBlock("PLANT", "QKBMU", column_xs(5, 1.1, LEFT_ZONE), word_y=1.3, code_y=-0.2, side=0.75)
        plant_shifts = plant.shift_row([1, -1, 1, -1, 1], color=alt_colors(5))
        crown = CodeBlock("CROWN", "DQPVO", column_xs(5, 1.1, RIGHT_ZONE), word_y=1.3, code_y=-0.2, side=0.75)
        crown_shifts = crown.shift_row([1, -1, 1, -1, 1], color=alt_colors(5))
        divider = DashedLine(UP * 1.9, DOWN * 1.4, color=MUTED)
        subst = pill("new letters  →  substitution", FWD, size=SMALL).next_to(plant_shifts, DOWN, buff=0.35)
        answer = pill("CROWN  →  DQPVO", GOOD, size=LABEL).next_to(crown_shifts, DOWN, buff=0.35)
        self.validator.check_in_frame(VGroup(question, plant.word, subst, answer))

        n = self.narrate(
            id="ex2_01",
            text="If PLANT is coded as QKBMU, how is CROWN coded?",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(question, shift=DOWN * 0.3))
        self.play(FadeIn(plant.word), FadeIn(plant.arrows), FadeIn(plant.code))
        self.wait_for_narration(n)

        n = self.narrate(
            id="ex2_02",
            text="The letters are different, so it's a substitution. The shift row reads plus one, minus one, plus one, "
                 "minus one, plus one. That's an alternating shift.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "substitution")
        self.play(FadeIn(subst, shift=UP * 0.1))
        self.at_word(n, "reads")
        self.play(LaggedStart(*[FadeIn(s, shift=UP * 0.15) for s in plant_shifts], lag_ratio=0.4), run_time=2.0)
        self.at_word(n, "alternating")
        self.play(Indicate(plant_shifts, color=FOCUS, scale_factor=1.1))
        self.wait_for_narration(n)

        # HEAR: CROWN letter by letter.  SEE: each code letter + its shift.
        n = self.narrate(
            id="ex2_03",
            text="For CROWN: C plus one is D. R minus one is Q. O plus one is P. W minus one is V. "
                 "And N plus one is O. The code is DQPVO.",
            voice="default",
            subtitle=True,
        )
        self.play(Create(divider), FadeIn(crown.word))
        cues = [("plus", 1), ("minus", 1), ("plus", 2), ("minus", 2), ("plus", 3)]
        for k, (spoken, occurrence) in enumerate(cues):
            self.at_word(n, spoken, occurrence=occurrence)
            self.play(GrowArrow(crown.arrows[k]), FadeIn(crown.code[k], shift=DOWN * 0.15), FadeIn(crown_shifts[k]),
                      run_time=0.45)
        self.at_word(n, "code")
        self.play(*[mark_tile(t, GOOD) for t in crown.code], FadeIn(answer, scale=1.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S07_example_alternating")

    # ============================ 8. EXAMPLE 3: REVERSAL WITH FIXED ENDS ==========

    def example_fixed_ends(self):
        self.scene_start("S08_example_fixed_ends", title="Example 3 - Reversal with Fixed Ends")

        xs = column_xs(8, 1.25)
        block = CodeBlock("COMPUTER", "RFUVQNPC", xs, word_y=1.9, code_y=0.4, side=0.75)
        direct = block.shift_row([raw_shift(a, b) for a, b in zip("COMPUTER", "RFUVQNPC")], color=BAD)
        new_letters = VGroup(*[block.code[k] for k in (1, 3, 4, 5)])     # F, V, Q, N
        after = block.shift_row([0, 1, 1, 1, 1, 1, 1, 0], color=[MUTED] + [GOOD] * 6 + [MUTED])
        self.validator.check_in_frame(VGroup(block.word, direct))

        n = self.narrate(
            id="ex3_01",
            text="Now let's return to COMPUTER and RFUVQNPC.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(block.word), FadeIn(block.arrows), FadeIn(block.code), FadeIn(direct))
        self.wait_for_narration(n)

        # HEAR: new letters -> substitution; direct row irregular; opposites
        # fail (C + R = 21).  SEE: F, V, Q, N marked; a red "21, not 27" tag.
        subst = pill("F, V, Q, N are new  →  substitution", FWD, size=SMALL).move_to(DOWN * 1.9)
        opp = pill("C + R  =  3 + 18  =  21,  not 27", BAD, size=SMALL).move_to(DOWN * 2.7)
        n = self.narrate(
            id="ex3_02",
            text="The letters aren't the same, since the code has F, V, Q and N, which COMPUTER doesn't. So it's a "
                 "substitution. The direct shift row was irregular. So test opposites: C and R give three plus "
                 "eighteen, which is twenty-one, not twenty-seven. That fails.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "has")
        self.play(*[mark_tile(t, FWD) for t in new_letters])
        self.at_word(n, "substitution")
        self.play(FadeIn(subst, shift=UP * 0.1))
        self.at_word(n, "irregular")
        self.play(Indicate(direct, color=BAD, scale_factor=1.05))
        self.at_word(n, "opposites")
        self.play(Indicate(VGroup(block.word[0], block.code[0]), color=OPP))
        self.at_word(n, "fails")
        self.play(FadeIn(opp, shift=UP * 0.1))
        self.wait_for_narration(n)

        # HEAR: reverse -> RETUPMOC; shift row 0, +1 ... +1, 0.  SEE: the word
        # row flips in place; the red row gives way to grey / green values.
        n = self.narrate(
            id="ex3_03",
            text="So reverse the word: RETUPMOC. Now write the shift row against RFUVQNPC. R to R is zero. E to F is "
                 "plus one, and every middle letter is plus one. The last letter, C to C, is zero again.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(VGroup(subst, opp, direct)), *[mark_tile(t, INK) for t in new_letters])
        self.at_word(n, "reverse")
        self.play(reverse_groups(block.word, [list(range(8))]))
        self.at_word(n, "zero", occurrence=1)
        self.play(FadeIn(after[0], shift=UP * 0.15))
        self.at_word(n, "plus", occurrence=1)
        self.play(FadeIn(after[1], shift=UP * 0.15))
        self.at_word(n, "every")
        self.play(LaggedStart(*[FadeIn(a, shift=UP * 0.15) for a in after[2:7]], lag_ratio=0.25))
        self.at_word(n, "last")
        self.play(FadeIn(after[7], shift=UP * 0.15))
        self.wait_for_narration(n)

        n = self.narrate(
            id="ex3_04",
            text="The rule is: reverse the word, keep the first and last letters, and shift every middle letter "
                 "forward by one.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "rule")
        cap = self.caption("Reverse  ·  keep both ends  ·  middle letters +1", GOOD)
        self.play(FadeIn(cap, shift=UP * 0.2))
        self.at_word(n, "keep")
        self.play(Indicate(VGroup(after[0], after[7]), color=FOCUS, scale_factor=1.3))
        self.wait_for_narration(n)

        # HEAR: MEDICINE -> ENICIDEM -> E | OJDJEF | M.  SEE: a new block;
        # the word flips, the ends drop down unchanged, the middle shifts +1.
        med = CodeBlock("MEDICINE", "EOJDJEFM", xs, word_y=1.9, code_y=0.4, side=0.75)
        med_shifts = med.shift_row([0, 1, 1, 1, 1, 1, 1, 0], color=[MUTED] + [GOOD] * 6 + [MUTED])
        n = self.narrate(
            id="ex3_05",
            text="Apply it to MEDICINE. Reversed, it's ENICIDEM. Keep E at the start and M at the end. Shift the "
                 "middle letters, N-I-C-I-D-E, forward by one to get O-J-D-J-E-F.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(VGroup(block.word, block.arrows, block.code, after)))
        self.at_word(n, "MEDICINE")
        self.play(FadeIn(med.word, shift=DOWN * 0.2))
        self.at_word(n, "Reversed")
        self.play(reverse_groups(med.word, [list(range(8))]))
        self.at_word(n, "Keep")
        self.play(*[AnimationGroup(GrowArrow(med.arrows[k]), FadeIn(med.code[k]), FadeIn(med_shifts[k]))
                    for k in (0, 7)])
        self.at_word(n, "Shift")
        self.play(LaggedStart(*[AnimationGroup(GrowArrow(med.arrows[k]), FadeIn(med.code[k], shift=DOWN * 0.15),
                                               FadeIn(med_shifts[k])) for k in range(1, 7)], lag_ratio=0.3))
        self.wait_for_narration(n)

        answer = pill("MEDICINE  →  EOJDJEFM", GOOD, size=LABEL).next_to(med_shifts, DOWN, buff=0.35)
        n = self.narrate(
            id="ex3_06",
            text="The code is EOJDJEFM.",
            voice="default",
            subtitle=True,
        )
        self.play(*[mark_tile(t, GOOD) for t in med.code], FadeIn(answer, scale=1.1))
        self.validator.check_in_frame(VGroup(med.word, answer, cap))
        self.wait_for_narration(n)

        # HEAR: the unchanged ends made it look chaotic.  SEE: the ends framed.
        n = self.narrate(
            id="ex3_07",
            text="The two unchanged end letters are exactly what makes this code look chaotic at first. The procedure "
                 "finds them, because it tells you to look for letters that don't change.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "unchanged")
        frames = VGroup(*[SurroundingRectangle(VGroup(med.word[k], med.code[k]), color=FOCUS, buff=0.1)
                          for k in (0, 7)])
        self.play(Create(frames))
        self.at_word(n, "procedure")
        new_cap = self.caption("Look for letters that don't change", FOCUS)
        self.play(FadeTransform(cap, new_cap))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S08_example_fixed_ends")

    # ======================================== 9. EXAM APPLICATION ==========

    def exam_application(self):
        self.scene_start("S09_exam", title="Exam Application")

        rows = self.step_rows([
            ("Same letters?  →  rearrangement (reversal / halves / pairs)", ANCHOR),
            ("New letters?  →  shift row (constant / progressive / alternating)", FWD),
            ("Irregular?  →  sum 27  →  reverse and re-check", OPP),
            ("Look for unchanged end letters", FOCUS),
            ("Verify on every letter  →  apply", GOOD),
        ], SAFE_W - 0.8)
        routine = self.card(rows).move_to(UP * 0.9)
        tips = VGroup(pill("Tip: check one letter of each option, only once the rule is sure", MUTED, size=SMALL),
                      pill("Tip: write the reversed word down", MUTED, size=SMALL)).arrange(DOWN, buff=0.2)
        tips.next_to(routine, DOWN, buff=0.3)
        self.validator.check_in_frame(VGroup(routine, tips))

        n = self.narrate(
            id="exam_01",
            text="In the exam, the procedure takes seconds once you've practised it. Most codes are identified by step "
                 "one or step two. The later steps are for the codes designed to look difficult.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(routine[0]))
        self.play_with(n, LaggedStart(*[FadeIn(r, shift=RIGHT * 0.2) for r in rows], lag_ratio=0.4), fraction=0.6)
        self.at_word(n, "later")
        self.play(Indicate(VGroup(rows[2], rows[3]), color=OPP, scale_factor=1.02))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_02",
            text="Two practical tips. First, when options are given, you can sometimes eliminate choices by checking "
                 "just one letter of the new code, for example the last letter. But only do this after you're sure of "
                 "the rule.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "eliminate")
        self.play(FadeIn(tips[0], shift=UP * 0.15))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_03",
            text="Second, when a code involves reversal, write the reversed word down explicitly. Reversing in your "
                 "head while also shifting letters is where errors creep in.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "write")
        self.play(FadeIn(tips[1], shift=UP * 0.15))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S09_exam")

    # =========================================== 10. COMMON MISTAKE ==========
    # Three rows of ✗ | ✓ cards, one row per mistake.

    def common_mistake(self):
        self.scene_start("S10_mistake", title="Common Mistake")

        card_w = ZONE_W - 0.3
        pairs = [
            (self.verdict_card(False, "SYSMET looks shifted: start writing shift values", card_w),
             self.verdict_card(True, "Check the letters first: same letters means rearrangement", card_w)),
            (self.verdict_card(False, "Rule fits 6 of 8 letters: close enough", card_w),
             self.verdict_card(True, "A rule must fit every letter", card_w)),
            (self.verdict_card(False, "Read the shift row straight through", card_w),
             self.verdict_card(True, "Irregular? Read every second value", card_w)),
        ]
        for (wrong, right), y in zip(pairs, [1.6, 0.05, -1.5]):
            wrong.move_to(LEFT_ZONE + UP * y)
            right.move_to(RIGHT_ZONE + UP * y)
        header = pill("3 mistakes", BAD, size=LABEL).move_to(UP * (CARD_TOP - 0.3))
        self.validator.check_in_frame(VGroup(header, *[c for p in pairs for c in p]))

        n = self.narrate(
            id="mistake_01",
            text="The biggest mistake is guessing the code type from appearance, and skipping the letter check. A "
                 "learner sees SYSMET, assumes letters were shifted, and starts writing shift values. Checking whether "
                 "the letters are the same takes two seconds and saves the whole question.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(header))
        self.at_word(n, "guessing")
        self.play(FadeIn(pairs[0][0], shift=RIGHT * 0.3))
        self.at_word(n, "Checking")
        self.play(FadeIn(pairs[0][1], shift=LEFT * 0.3))
        self.wait_for_narration(n)

        n = self.narrate(
            id="mistake_02",
            text="The second mistake is accepting a rule that fits most of the letters. In COMPUTER, the plus-one shift "
                 "fits six of the eight letters. Someone who applies it to all eight gets the ends wrong, and that "
                 "wrong answer will be among the options. When a rule fails on a few letters, those letters are "
                 "telling you something, such as fixed ends or an alternating pattern.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "accepting")
        self.play(FadeIn(pairs[1][0], shift=RIGHT * 0.3))
        self.at_word(n, "telling")
        self.play(FadeIn(pairs[1][1], shift=LEFT * 0.3))
        self.wait_for_narration(n)

        n = self.narrate(
            id="mistake_03",
            text="The third mistake is reading the shift row straight through and missing an alternating pattern. "
                 "When the row looks irregular, read every second value.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "straight")
        self.play(FadeIn(pairs[2][0], shift=RIGHT * 0.3))
        self.at_word(n, "second")
        self.play(FadeIn(pairs[2][1], shift=LEFT * 0.3))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S10_mistake")

    # ================================================ 11. PRACTICE ==========

    def practice(self):
        self.scene_start("S11_practice", title="Practice Question")

        card_w = SAFE_W - 1.0
        q1 = VGroup(pill("Q1", FOCUS), fitted_text("If GARDEN is coded as AGDRNE, how is FLOWER coded?",
                                                   card_w - 1.6, BODY, max_lines=2))
        q2 = VGroup(pill("Q2", FOCUS), fitted_text("Same code as PLANT → QKBMU: which word is written as CNPJ?",
                                                   card_w - 1.6, BODY, max_lines=2))
        for q in (q1, q2):
            q.arrange(RIGHT, buff=0.35)
        questions = VGroup(q1, q2).arrange(DOWN, buff=0.6, aligned_edge=LEFT)
        board = self.card(questions, color=FOCUS).move_to(UP * 0.4)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="practice_01",
            text="Try these two.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(board[0]), FadeIn(questions, shift=UP * 0.2))
        self.play(questions.animate.set_opacity(0.45))
        self.wait_for_narration(n)

        n = self.narrate(
            id="practice_02",
            text="First, if GARDEN is coded as AGDRNE, how is FLOWER coded?",
            voice="default",
            subtitle=True,
        )
        self.play(q1.animate.set_opacity(1))
        self.wait_for_narration(n)

        # SILENCE (pause_after): countdown ring while the learner thinks.
        n = self.narrate(
            id="practice_03",
            text="Second, using the same code in which PLANT is written as QKBMU, which word is written as CNPJ?",
            voice="default",
            subtitle=True,
            pause_after=8.0,
        )
        self.play(q2.animate.set_opacity(1))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        self.clear_stage()
        self.scene_end("S11_practice")

    # ================================================== 12. ANSWER ==========

    def answer(self):
        self.scene_start("S12_answer", title="Answer and Explanation")

        # Q1: GARDEN / AGDRNE -> pair swap; FLOWER -> LFWORE.
        tag_q1 = pill("Q1", FOCUS).move_to(UP * (CARD_TOP - 0.3))
        pairs = [[0, 1], [2, 3], [4, 5]]
        xs = column_xs(6, 0.95)
        garden = word_row("GARDEN", xs, 1.6, side=0.75)
        code = word_row("AGDRNE", xs, 0.6, side=0.75)
        frames = VGroup(*[SurroundingRectangle(VGroup(*[garden[k] for k in p], *[code[k] for k in p]),
                                               color=OPP, buff=0.08) for p in pairs])
        flower = word_row("FLOWER", xs, -0.8, side=0.8)
        answer1 = pill("FLOWER  →  LFWORE", GOOD, size=LABEL).move_to(DOWN * 2.1)
        self.validator.check_in_frame(VGroup(tag_q1, garden, flower, answer1))

        n = self.narrate(
            id="answer_01",
            text="For the first question, GARDEN and AGDRNE contain the same letters, so it's a rearrangement. The "
                 "pairs G-A, R-D and E-N have each swapped. That's a pair swap.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(tag_q1), FadeIn(garden), FadeIn(code))
        self.at_word(n, "same")
        self.play(Indicate(VGroup(garden, code), color=ANCHOR, scale_factor=1.03))
        self.at_word(n, "swapped")
        self.play(Create(frames))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answer_02",
            text="FLOWER splits into F-L, O-W and E-R. Swapping each pair gives L-F, W-O and R-E. The code is LFWORE.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(flower, shift=DOWN * 0.2))
        self.at_word(n, "splits")
        self.play(spread(flower, pairs, 0.5))
        self.at_word(n, "Swapping")
        self.play(reverse_groups(flower, pairs))
        self.at_word(n, "code")
        self.play(spread(flower, pairs, -0.5))
        self.play(FadeIn(answer1, scale=1.1))
        self.wait_for_narration(n)

        # Q2: undo the alternating rule: -1 odd, +1 even.  CNPJ -> BOOK.
        tag_q2 = pill("Q2", FOCUS).move_to(tag_q1)
        enc = VGroup(text("encode:", SMALL, MUTED, BOLD),
                     *[pill(s, c, size=SMALL) for s, c in zip(["+1", "−1", "+1", "−1"], alt_colors(4))])
        dec = VGroup(text("decode:", SMALL, MUTED, BOLD),
                     *[pill(s, c, size=SMALL) for s, c in zip(["−1", "+1", "−1", "+1"], alt_colors(4))])
        for r in (enc, dec):
            r.arrange(RIGHT, buff=0.25)
        rules = VGroup(enc, dec).arrange(DOWN, buff=0.25, aligned_edge=LEFT).move_to(UP * 1.7)
        block = CodeBlock("CNPJ", "BOOK", column_xs(4, 1.4), word_y=0.3, code_y=-1.2, side=0.8)
        back = block.shift_row([-1, 1, -1, 1], color=alt_colors(4))
        answer2 = pill("CNPJ  →  BOOK", GOOD, size=LABEL).next_to(back, DOWN, buff=0.3)
        self.validator.check_in_frame(VGroup(tag_q2, rules, block.word, answer2))

        n = self.narrate(
            id="answer_03",
            text="For the second, the code adds one in odd positions and subtracts one in even positions. To decode, "
                 "we undo it: subtract one in odd positions, and add one in even positions.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(VGroup(tag_q1, garden, code, frames, flower, answer1)), FadeIn(tag_q2))
        self.at_word(n, "adds")
        self.play(FadeIn(enc, shift=RIGHT * 0.2))
        self.at_word(n, "undo")
        self.play(FadeIn(dec, shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answer_04",
            text="C minus one is B. N plus one is O. P minus one is O. J plus one is K. The word is BOOK.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(block.word))
        cues = [("minus", 1), ("plus", 1), ("minus", 2), ("plus", 2)]
        for k, (spoken, occurrence) in enumerate(cues):
            self.at_word(n, spoken, occurrence=occurrence)
            self.play(GrowArrow(block.arrows[k]), FadeIn(block.code[k], shift=DOWN * 0.15), FadeIn(back[k]),
                      run_time=0.45)
        self.at_word(n, "word")
        self.play(*[mark_tile(t, GOOD) for t in block.code], FadeIn(answer2, scale=1.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S12_answer")

    # ========================================== 13. QUICK REVISION ==========

    def quick_revision(self):
        self.scene_start("S13_revision", title="Quick Revision")

        card_w, card_h = SAFE_W - 1.0, 5.2
        items = [
            ("First: same letters (rearrangement) or new letters (substitution)?", FOCUS),
            ("Rearrangements: full reversal · halves reversed · pairs swapped", ANCHOR),
            ("Substitutions: constant · progressive · alternating · opposite · reversal + shift", FWD),
            ("Irregular row → read every second value; test 27; reverse and re-check", OPP),
            ("Watch for unchanged letters, especially at the ends", FOCUS),
            ("A rule must fit every letter", GOOD),
        ]
        bullets = VGroup(*[VGroup(Dot(radius=0.07, color=c), fitted_text(s, card_w - 1.4, BODY, c, max_lines=2))
                           .arrange(RIGHT, buff=0.3) for s, c in items]).arrange(DOWN, buff=0.22, aligned_edge=LEFT)
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
            text="Always begin by asking whether the code uses the same letters or new ones. Same letters means a "
                 "rearrangement: reversal, halves reversal, or pair swaps. New letters means a substitution: constant, "
                 "progressive, alternating, opposite, or reversal with a shift.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(bullets[0], shift=RIGHT * 0.2))
        self.at_word(n, "Same")
        self.play(FadeIn(bullets[1], shift=RIGHT * 0.2))
        self.at_word(n, "New")
        self.play(FadeIn(bullets[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="revision_03",
            text="If the shift row looks irregular, read every second value, test the sum of twenty-seven, "
                 "and try reversing the word.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(bullets[3], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="revision_04",
            text="Watch for letters that stay the same. And never accept a rule unless it fits every letter.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(bullets[4], shift=RIGHT * 0.2))
        self.at_word(n, "never")
        self.play(FadeIn(bullets[5], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S13_revision")

    # ================================================= 14. CLOSING ==========
    # Purpose: teaser for Lesson 3: coded sentences whose words overlap.

    def closing(self):
        self.scene_start("S14_closing", title="Closing")

        badge = pill("Single-word codes  ✓", GOOD, size=BODY).move_to(UP * 2.3)
        sentences = [["tip", "nop", "sa"], ["nop", "kul", "tip"], ["sa", "jo", "nop"]]
        rows = VGroup()
        for words in sentences:
            rows.add(VGroup(*[pill(w, INK, size=LABEL, fill_opacity=0.06) for w in words]).arrange(RIGHT, buff=0.3))
        rows.arrange(DOWN, buff=0.3).move_to(UP * 0.2)
        shared = VGroup(*[p for r in rows for p in r if p[1].text == "nop"])
        nxt = pill("Next lesson:  Coding & Decoding II", ANCHOR, size=LABEL).move_to(DOWN * 2.2)
        self.validator.check_in_frame(VGroup(badge, rows, nxt))

        n = self.narrate(
            id="closing_01",
            text="With this procedure, you can take apart almost any single-word code.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(badge, scale=1.1))
        self.wait_for_narration(n)

        # HEAR: next lesson: whole sentences, compared.  SEE: three coded
        # sentences; the word they share lights up on "comparing".
        n = self.narrate(
            id="closing_02",
            text="In the next lesson, the codes get larger. Whole sentences are coded word by word, and one word is "
                 "renamed as another. The skill there changes from tracking letters to comparing statements, and we'll "
                 "build that method next.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "sentences")
        self.play(LaggedStart(*[FadeIn(r, shift=UP * 0.2) for r in rows], lag_ratio=0.3))
        self.at_word(n, "comparing")
        self.play(*[p[0].animate.set_stroke(FOCUS, 3).set_fill(FOCUS, 0.2) for p in shared],
                  *[p[1].animate.set_color(FOCUS) for p in shared])
        self.at_word(n, "build")
        self.play(FadeIn(nxt, scale=1.1))
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S14_closing")

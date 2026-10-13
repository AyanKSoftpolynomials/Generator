"""
animation.py for the LMS video generator.

Course : Pre-C-CAT - Section A
Module : Module 1 - Logical Reasoning
Lesson : Lesson 1 - Alphabet Test
Topic  : Opposite Letters (Topic 2)

Source script:
  C:\\Scripts\\Section A\\Module 1 - Logical Reasoning\\Lesson 01 - Alphabet Test\\
  Topic 2 - Opposite Letters.md

Built on the golden-reference pattern:
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``.

Opening: not the first video of the course, so no spoken course welcome.
The module > lesson > topic trail is shown on screen (silent), followed by a
one-idea recap of Topic 1 (the sum-27 rule) and what this video covers.

Section map (script heading -> VISUAL PLAN scene):
  S00 Intro (trail + recap)   -> -
  S01 Opening Hook            -> scene 1
  S02 Concept (the fold)      -> scene 2
  S03 The rule                -> scene 3
  S04 The 13 pairs            -> scene 4
  S05-S07 Examples 1-3        -> scene 5
  S08 Exam Application        -> scene 6
  S09 Common Mistake          -> scene 7
  S10-S11 Practice / Answers  -> scene 8
  S12-S13 Revision / Closing  -> scene 9
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

# Semantic colours: one meaning each, used the same way in every section
# (and the same as Topic 1, so the series looks like one course).
FWD = "#4FC3F7"        # forward position (counted from A)
REV = "#F48FB1"        # reverse position (counted from Z)
ANCHOR = "#FFB74D"     # EJOTY anchors and hop arrows
OPP = "#CE93D8"        # an opposite pair / the fold
FOCUS = "#FFD54F"      # "look here"
GOOD = "#66BB6A"       # confirmed result
BAD = "#EF5350"        # the trap / wrong answer

FONT = "Segoe UI"
MIN_FONT = 22          # readable floor: text is never shrunk below this
TITLE = 46
BODY = 30
LABEL = 28
SMALL = 24
NUM = 22               # position numbers over / under the strip
LETTER = 26            # letters inside the strip
MATH = 44

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def pos(ch):
    return ALPHABET.index(ch) + 1


def opposite(ch):
    return ALPHABET[26 - pos(ch)]


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
STRIP_Y = 0.35                                # the alphabet strip's home row
MATH_Y1 = -1.2                                # first working line under the strip
MATH_GAP = 0.72                               # spacing between working lines
CELL_SIZE = 0.46                              # 26 cells = 11.96 units < SAFE_W


# ======================================================= text helpers ====

def text(s, size=BODY, color=INK, weight=NORMAL):
    return Text(s, font=FONT, font_size=size, color=color, weight=weight)


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


def fitted_text(s, max_width, size=BODY, color=INK, weight=NORMAL, max_lines=3):
    """Readable text no wider than ``max_width`` (never below MIN_FONT)."""
    floor = max(MIN_FONT, 0.85 * size)
    for lines in range(1, max_lines + 1):
        body = s if lines == 1 else wrap_lines(s, lines)
        mob = text(body, size, color, weight)
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


def math_row(line, row, x=ORIGIN):
    """Put a working line on row ``row`` (0, 1, 2 ...) under the strip."""
    return line.move_to(x + UP * (MATH_Y1 - row * MATH_GAP))


def tile(ch, side=0.9, color=INK):
    """One big letter in a rounded square (for words such as GOLD, HORSE)."""
    sq = RoundedRectangle(corner_radius=0.1, width=side, height=side, stroke_color=MUTED,
                          stroke_width=2, fill_color=CELL, fill_opacity=1)
    return VGroup(sq, text(ch, int(side * 52), color, BOLD).move_to(sq))


def word_tiles(word, side=0.9, buff=0.3):
    return VGroup(*[tile(ch, side) for ch in word]).arrange(RIGHT, buff=buff)


def mark_tile(t, color):
    return AnimationGroup(t[0].animate.set_fill(color, 0.3).set_stroke(color, 3), t[1].animate.set_color(color))


# ==================================================== diagram helpers ====

class AlphabetStrip(VGroup):
    """The 26 letters in a single row of cells, centred on the origin.

    Anything attached to a letter is placed with ``label`` (outward from its
    cell), so numbers, counts and tags never sit on a letter.
    """

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

    def idx(self, ch):
        return self.letters.index(ch)

    def cell(self, ch):
        return self.cells[self.idx(ch)]

    def unit(self, i):
        return VGroup(self.cells[i], self.chars[i])

    def label(self, ch, mob, side=UP, buff=0.14):
        """Place ``mob`` just outside the cell of ``ch`` (above or below)."""
        return mob.next_to(self.cell(ch), side, buff=buff)

    def mark(self, ch, color=ANCHOR):
        i = self.idx(ch)
        return AnimationGroup(self.cells[i].animate.set_fill(color, 0.35).set_stroke(color, 3),
                              self.chars[i].animate.set_color(color))

    def unmark(self, ch):
        i = self.idx(ch)
        return AnimationGroup(self.cells[i].animate.set_fill(CELL, 1).set_stroke(MUTED, 1.5),
                              self.chars[i].animate.set_color(INK))

    def hops(self, start, steps, side=DOWN, color=ANCHOR, numbered=True):
        """Curved hop arrows from ``start``, ``steps`` letters right (+) or left (-)."""
        i0, s = self.idx(start), (1 if steps > 0 else -1)
        below = side[1] < 0
        arrows, labels = VGroup(), VGroup()
        for k in range(abs(steps)):
            a, b = self.cells[i0 + s * k], self.cells[i0 + s * (k + 1)]
            if below:
                p, q, angle = a.get_bottom() + DOWN * 0.06, b.get_bottom() + DOWN * 0.06, s * 0.7 * PI
            else:
                p, q, angle = a.get_top() + UP * 0.06, b.get_top() + UP * 0.06, -s * 0.7 * PI
            arc = CurvedArrow(p, q, angle=angle, color=color, stroke_width=3, tip_length=0.12)
            arrows.add(arc)
            if numbered:
                labels.add(text(str(k + 1), NUM, color, BOLD)
                           .next_to(arc.point_from_proportion(0.5), side, buff=0.06))
        return arrows, labels

    def pair_arc(self, a, b, color=OPP, angle=-PI / 2.5):
        """Arc above the strip joining letters ``a`` (left) and ``b`` (right)."""
        return ArcBetweenPoints(self.cell(a).get_top() + UP * 0.08, self.cell(b).get_top() + UP * 0.08,
                                angle=angle, color=color, stroke_width=4)


# ============================================================= lesson ====

class OppositeLettersVideo(LMSScene):
    lesson_title = "Opposite Letters"

    def construct(self):
        self.camera.background_color = BG

        self.lesson_intro()
        self.hook()
        self.concept_fold()
        self.the_rule()
        self.the_pairs()
        self.example_basic()
        self.example_application()
        self.example_exam()
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
        if width is not None or height is not None:
            fit_within(content, (width or 99) - 2 * pad, (height or 99) - 2 * pad)
        w = width if width is not None else content.width + 2 * pad
        h = height if height is not None else content.height + 2 * pad
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

    def code_columns(self, plain, coded, xs, top_y=1.0, bottom_y=-1.0, side=0.9):
        """Plain word on top, coded word underneath, one column per letter."""
        top = VGroup(*[tile(ch, side).move_to(RIGHT * x + UP * top_y) for ch, x in zip(plain, xs)])
        bottom = VGroup(*[tile(ch, side).move_to(RIGHT * x + UP * bottom_y) for ch, x in zip(coded, xs)])
        arrows = VGroup(*[Arrow(t.get_bottom(), b.get_top(), buff=0.12, color=MUTED, stroke_width=4,
                                max_tip_length_to_length_ratio=0.2) for t, b in zip(top, bottom)])
        return top, bottom, arrows

    # ========================================= 0. LESSON INTRO ==========
    # Purpose: where we are (silent trail), what we learned last time (one
    # idea, with its visual), and what this video covers.

    def lesson_intro(self):
        self.scene_start("S00_intro", title="Lesson Introduction")

        crumb = self.breadcrumb("Module 1 · Logical Reasoning", "Lesson 1 · Alphabet Test", "Topic 2")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        last = pill("Last time", MUTED, size=SMALL)
        rule = self.card(math_line(r"\text{Forward}", "+", r"\text{Reverse}", "=", "27",
                                   colors={r"\text{Forward}": FWD, r"\text{Reverse}": REV, "27": ANCHOR}, size=52),
                         color=ANCHOR)
        recap = VGroup(last, rule).arrange(DOWN, buff=0.3).move_to(UP * 0.2)

        # SEE (silent): the trail.  HEAR: the one idea from last time.
        # SEE: the sum-27 card from Topic 1, on the word "rule".
        n = self.narrate(
            id="intro_01",
            text="Last time, you learned to place any letter from either end of the alphabet, and we found one rule: "
                 "a letter's forward and reverse positions always add up to twenty-seven.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.play(FadeIn(last))
        self.at_word(n, "rule")
        self.play(FadeIn(rule, scale=0.9))
        self.wait_for_narration(n)

        # HEAR: today.  SEE: the recap shrinks away; the title is written.
        title = fitted_text("Opposite Letters", SAFE_W, 72, INK, BOLD)
        underline = Line(LEFT, RIGHT, color=OPP, stroke_width=5).set_width(title.width * 0.6)
        header = VGroup(title, underline).arrange(DOWN, buff=0.2).move_to(UP * 0.2)
        n = self.narrate(
            id="intro_02",
            text="In this video, we'll use that rule to find any letter's opposite, "
                 "and to crack one of the most common codes in the exam.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(recap, shift=UP * 0.3))
        self.at_word(n, "opposite")
        self.play(Write(title), run_time=1.1)
        self.play(GrowFromCenter(underline))
        self.wait_for_narration(n)

        # HEAR: the four objectives.  SEE: one row per objective, on its word.
        goals = [
            ("Find the opposite of any letter", OPP),
            ("Recall all 13 opposite pairs", ANCHOR),
            ("Spot opposite-letter coding", FWD),
            ("Don't confuse it with a +1 shift", BAD),
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
            text="By the end of this video, you'll be able to find the opposite of any letter, "
                 "recall all thirteen opposite pairs, spot opposite-letter coding in a question, "
                 "and avoid confusing it with a simple shift.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(underline), ReplacementTransform(title, small_title), run_time=0.8)
        self.play(FadeIn(objectives[0]), FadeIn(heading))
        for row, spoken in zip(rows, ["find", "recall", "spot", "avoid"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.5)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_intro")

    # ================================================= 1. HOOK ==========
    # Purpose: a code that looks random (every letter moves a different amount).

    def hook(self):
        self.scene_start("S01_hook", title="Opening Hook")

        xs = [-3.3, -1.1, 1.1, 3.3]
        top, bottom, arrows = self.code_columns("GOLD", "TLOW", xs, top_y=1.3, bottom_y=-0.9)
        labels = VGroup(*[text(s, LABEL, BAD, BOLD).next_to(a, RIGHT, buff=0.2)
                          for s, a in zip(["+13", "−3", "+3", "+19"], arrows)])

        # HEAR: the code.  SEE: GOLD over TLOW.
        n = self.narrate(
            id="hook_01",
            text="Look at this code. GOLD is written as TLOW.",
            voice="default",
            subtitle=True,
        )
        self.play(LaggedStart(*[FadeIn(t, shift=DOWN * 0.2) for t in top], lag_ratio=0.15))
        self.at_word(n, "written")
        self.play(LaggedStart(*[FadeIn(b, shift=UP * 0.2) for b in bottom], lag_ratio=0.15))
        self.wait_for_narration(n)

        # HEAR: each letter's replacement.  SEE: one arrow per "becomes".
        n = self.narrate(
            id="hook_02",
            text="At first sight, the letters seem to have been replaced at random. "
                 "G becomes T, O becomes L, L becomes O, and D becomes W.",
            voice="default",
            subtitle=True,
        )
        for k in range(4):
            self.at_word(n, "becomes", occurrence=k + 1)
            self.play(GrowArrow(arrows[k]), run_time=0.5)
        self.wait_for_narration(n)

        # HEAR: no common shift.  SEE: each arrow gets its (different) shift.
        n = self.narrate(
            id="hook_03",
            text="There's no common shift. G moves forward thirteen places, but O moves back three.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "thirteen")
        self.play(FadeIn(labels[0], shift=LEFT * 0.1))
        self.at_word(n, "three")
        self.play(FadeIn(labels[1], shift=LEFT * 0.1))
        self.play(FadeIn(labels[2:], shift=LEFT * 0.1))
        self.validator.check_in_frame(VGroup(top, bottom, labels))
        self.wait_for_narration(n)

        # HEAR: there is a rule.  SEE: a caption with the promise.
        n = self.narrate(
            id="hook_04",
            text="So is there a rule at all? There is, and it's one of the most common rules in alphabet "
                 "and coding questions. By the end of this lesson, you'll recognise it at a glance.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "rule")
        self.play(Indicate(labels, color=FOCUS))
        cap = self.caption("There is a rule, and it's a common one", FOCUS)
        self.at_word(n, "common")
        self.play(FadeIn(cap, shift=UP * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S01_hook")

    # ============================================ 2. CONCEPT: FOLD ==========
    # Purpose: opposite letters defined by folding the alphabet in half.

    def concept_fold(self):
        self.scene_start("S02_concept", title="Concept Introduction")

        strip = AlphabetStrip().move_to(UP * STRIP_Y)
        units = [strip.unit(i) for i in range(26)]
        for u in units:
            u.save_state()
        # Folded layout: column k holds letter k on top and letter 25 - k below.
        top_y, bottom_y = STRIP_Y + 0.3, STRIP_Y - 0.3
        folds = []
        for i, u in enumerate(units):
            k = i if i < 13 else 25 - i
            target = RIGHT * (k - 6) * CELL_SIZE + UP * (top_y if i < 13 else bottom_y)
            folds.append(u.animate(path_arc=0 if i < 13 else -PI / 2).move_to(target))

        # HEAR: fold the alphabet.  SEE: the strip folds; the first columns pulse
        # as "A lands on Z", "B lands on Y" are said.
        n = self.narrate(
            id="concept_01",
            text="Imagine folding the alphabet in half, so that the first letter lands on the last. "
                 "A lands on Z, B lands on Y, C lands on X, and so on, all the way to the middle.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(strip))
        self.at_word(n, "folding")
        self.play(*folds, run_time=1.8)
        folded = VGroup(*units)
        self.play(folded.animate.scale(1.7).move_to(UP * STRIP_Y))
        columns = [VGroup(units[k], units[25 - k]) for k in range(13)]
        for occurrence, k in [(2, 0), (3, 1), (4, 2)]:
            self.at_word(n, "lands", occurrence=occurrence)
            self.play(Indicate(columns[k], color=OPP, scale_factor=1.1), run_time=0.6)
        self.at_word(n, "middle")
        self.play(Indicate(columns[12], color=OPP, scale_factor=1.1), run_time=0.6)
        self.wait_for_narration(n)

        # HEAR: the name.  SEE: every folded column tints, and the keyword caption.
        n = self.narrate(
            id="concept_02",
            text="Each pair of letters that meet in this fold are called opposite letters.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "opposite")
        cap = self.caption("Opposite letters: the pairs that meet in the fold", OPP)
        self.play(FadeIn(cap, shift=UP * 0.2),
                  *[u[0].animate.set_stroke(OPP, 2.5) for u in units])
        self.wait_for_narration(n)

        # HEAR: same position from the other end.  SEE: the strip unfolds;
        # A and Z get "1" (left / right), then B and Y get "2", each pair arced.
        a1 = strip.label("A", text("1", NUM, FWD, BOLD))
        z1 = strip.label("Z", text("1", NUM, REV, BOLD), DOWN)
        b2 = strip.label("B", text("2", NUM, FWD, BOLD))
        y2 = strip.label("Y", text("2", NUM, REV, BOLD), DOWN)
        n = self.narrate(
            id="concept_03",
            text="Put more precisely, the opposite of a letter is the letter at the same position from the other end "
                 "of the alphabet. A is first from the left, and Z is first from the right, so A and Z are opposites. "
                 "B is second from the left, and Y is second from the right, so B and Y are opposites.",
            voice="default",
            subtitle=True,
        )
        new_cap = self.caption("Same position from the other end", OPP)
        self.play(FadeTransform(cap, new_cap), *[Restore(u) for u in units], run_time=1.5)
        self.at_word(n, "first", occurrence=1)
        self.play(strip.mark("A", OPP), FadeIn(a1))
        self.at_word(n, "first", occurrence=2)
        self.play(strip.mark("Z", OPP), FadeIn(z1))
        arc_az = strip.pair_arc("A", "Z", angle=-PI / 3)
        arc_by = strip.pair_arc("B", "Y", color=FOCUS, angle=-PI / 3)
        self.play(Create(arc_az))
        self.at_word(n, "second", occurrence=1)
        self.play(strip.mark("B", FOCUS), FadeIn(b2))
        self.at_word(n, "second", occurrence=2)
        self.play(strip.mark("Y", FOCUS), FadeIn(y2))
        self.play(Create(arc_by))
        self.validator.check_in_frame(VGroup(arc_az, strip, z1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_concept")

    # ================================================ 3. THE RULE ==========
    # Purpose: opposite = 27 - n, derived from the sum-27 rule.

    def the_rule(self):
        self.scene_start("S03_rule", title="Explanation - The Rule")

        strip = AlphabetStrip().move_to(UP * STRIP_Y)
        k11 = strip.label("K", text("11", NUM, FWD, BOLD))
        k16 = strip.label("K", text("16", NUM, REV, BOLD), DOWN)
        recall = self.card(math_line(r"\text{Forward}", "+", r"\text{Reverse}", "=", "27",
                                     colors={r"\text{Forward}": FWD, r"\text{Reverse}": REV, "27": ANCHOR}),
                           color=ANCHOR)
        recall.move_to(UP * (CARD_TOP - recall.height / 2))

        # HEAR: recall the sum-27 rule.  SEE: its card, then K with 11 and 16.
        n = self.narrate(
            id="rule_01",
            text="In the previous topic, we saw that for any letter, its forward position plus its reverse position "
                 "equals twenty-seven.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(recall, shift=DOWN * 0.2), FadeIn(strip))
        self.at_word(n, "forward")
        self.play(strip.mark("K", FWD), FadeIn(k11, shift=DOWN * 0.1))
        self.at_word(n, "reverse")
        self.play(FadeIn(k16, shift=UP * 0.1))
        self.wait_for_narration(n)

        # HEAR: the opposite's forward position = this letter's reverse position.
        # SEE: "16" travels from under K to above P, and P lights up.
        p16 = strip.label("P", text("16", NUM, FWD, BOLD))
        arc = strip.pair_arc("K", "P", angle=-PI / 2)
        n = self.narrate(
            id="rule_02",
            text="Now think about what the opposite letter is. It sits at the same distance from the other end. "
                 "So the opposite letter's forward position is exactly the original letter's reverse position.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "distance")
        self.play(Indicate(k16, color=REV, scale_factor=1.4))
        self.at_word(n, "exactly")
        self.play(TransformFromCopy(k16, p16, path_arc=-PI / 3), run_time=1.2)
        self.play(strip.mark("P", OPP), Create(arc))
        self.wait_for_narration(n)

        # HEAR: n <-> 27 - n; positions of opposites add to 27.  SEE: two lines.
        line1 = math_row(math_line(r"n", r"\;\longleftrightarrow\;", r"27-n",
                                   colors={"n": FWD, r"27-n": OPP}, size=52), 0)
        line2 = math_row(math_line(r"\text{position}", "+", r"\text{opposite's position}", "=", "27",
                                   colors={r"\text{position}": FWD, r"\text{opposite's position}": OPP,
                                           "27": ANCHOR}), 1)
        box = SurroundingRectangle(line2, color=ANCHOR, buff=0.15)
        n = self.narrate(
            id="rule_03",
            text="That gives us one simple rule. If a letter is at position n, its opposite is at position "
                 "twenty-seven minus n. Equivalently, the positions of two opposite letters always add up "
                 "to twenty-seven.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "minus")
        self.play(Write(line1))
        self.at_word(n, "Equivalently")
        self.play(Write(line2))
        self.at_word(n, "always")
        self.play(Create(box))
        self.validator.check_in_frame(VGroup(recall, strip, line2, box))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_rule")

    # ============================================ 4. THE 13 PAIRS ==========
    # Purpose: all thirteen pairs at a glance, the M-N centre, word hooks.

    def the_pairs(self):
        self.scene_start("S04_pairs", title="Explanation - The 13 Pairs")

        side = 0.7
        tops = VGroup(*[tile(ALPHABET[k], side) for k in range(13)]).arrange(RIGHT, buff=0.12)
        bots = VGroup(*[tile(ALPHABET[25 - k], side) for k in range(13)]).arrange(RIGHT, buff=0.12)
        grid = VGroup(tops, bots).arrange(DOWN, buff=0.15).move_to(UP * 1.1)
        top_nums = VGroup(*[text(str(k + 1), NUM, FWD).next_to(t, UP, buff=0.12) for k, t in enumerate(tops)])
        bot_nums = VGroup(*[text(str(26 - k), NUM, OPP).next_to(b, DOWN, buff=0.12) for k, b in enumerate(bots)])
        sums = VGroup(*[text("27", NUM, ANCHOR, BOLD).next_to(n_, DOWN, buff=0.18) for n_ in bot_nums])
        self.validator.check_in_frame(VGroup(top_nums, grid, sums))

        # HEAR: thirteen pairs; A..M pairs with Z..N.  SEE: top row on "first",
        # bottom row on "second", then every column's sum of 27.
        n = self.narrate(
            id="pairs_01",
            text="Twenty-six letters make exactly thirteen pairs. The first half of the alphabet, A to M, "
                 "pairs with the second half, running backwards from Z to N.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "first")
        self.play(LaggedStart(*[FadeIn(VGroup(t, m), shift=DOWN * 0.15) for t, m in zip(tops, top_nums)],
                              lag_ratio=0.08))
        self.at_word(n, "second")
        self.play(LaggedStart(*[FadeIn(VGroup(b, m), shift=UP * 0.15) for b, m in zip(bots, bot_nums)],
                              lag_ratio=0.08))
        self.play_with(n, LaggedStart(*[FadeIn(s, scale=0.6) for s in sums], lag_ratio=0.08), fraction=0.9)
        self.wait_for_narration(n)

        # HEAR: M and N sit side by side at the centre.  SEE: the M-N column
        # is framed and labelled "centre".
        mn = VGroup(tops[12], bots[12], top_nums[12], bot_nums[12], sums[12])
        frame = SurroundingRectangle(mn, color=FOCUS, buff=0.1)
        centre = pill("centre of the alphabet", FOCUS).next_to(frame, DOWN, buff=0.25)
        centre.align_to(frame, RIGHT)
        n = self.narrate(
            id="pairs_02",
            text="Notice the last pair, M and N. They sit side by side, because the centre of the alphabet falls "
                 "between them. Since there's an even number of letters, no letter is its own opposite.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "last")
        self.play(Create(frame))
        self.at_word(n, "centre")
        self.play(FadeIn(centre, shift=UP * 0.1))
        self.at_word(n, "even")
        self.play(Indicate(sums, color=ANCHOR, scale_factor=1.15))
        self.wait_for_narration(n)

        # HEAR: memory hooks, then "the rule is what you rely on".
        # SEE: the hook strip; then a caption with the 27 check.
        hooks = VGroup(*[pill(h, OPP, size=SMALL, fill_opacity=0.08)
                         for h in ["BY", "DeW", "EVe", "GT", "HS", "IR", "JQ", "KP", "LO", "MaN"]])
        hooks.arrange(RIGHT, buff=0.18)
        fit_width(hooks, SAFE_W).move_to(DOWN * 1.75)
        n = self.narrate(
            id="pairs_03",
            text="Many learners remember the pairs through small word hooks. BY, DEW, EVE, MAN, and letter pairs "
                 "like GT, HS and IR. These hooks are useful for speed. But the rule is what you rely on: "
                 "if you ever doubt a pair, add the two positions and check that you get twenty-seven.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(VGroup(frame, centre)))
        self.at_word(n, "hooks")
        self.play(LaggedStart(*[FadeIn(h, shift=UP * 0.15) for h in hooks], lag_ratio=0.12))
        self.at_word(n, "rule")
        cap = self.caption("Doubt a pair?  Add the positions: they must make 27", ANCHOR)
        self.play(FadeIn(cap, shift=UP * 0.2))
        self.at_word(n, "check")
        self.play(Indicate(sums, color=ANCHOR, scale_factor=1.15))
        self.validator.check_in_frame(VGroup(top_nums, grid, sums, hooks, cap))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_pairs")

    # ======================================== 5. EXAMPLE 1: BASIC ==========

    def example_basic(self):
        self.scene_start("S05_example_basic", title="Example 1 - Basic")

        question = self.question_card("What is the opposite of K?")
        strip = AlphabetStrip().move_to(UP * STRIP_Y)

        n = self.narrate(
            id="ex1_01",
            text="What is the opposite of K?",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(question, shift=DOWN * 0.3), FadeIn(strip))
        self.play(strip.mark("K", FWD))
        self.wait_for_narration(n)

        # HEAR: K = 11 (after J), 27 - 11 = 16, 16 = P (after O).
        # SEE: numbers below the strip, hops above, the working line.
        j10 = strip.label("J", text("10", NUM, ANCHOR), DOWN)
        k11 = strip.label("K", text("11", NUM, FWD, BOLD), DOWN)
        o15 = strip.label("O", text("15", NUM, ANCHOR), DOWN)
        p16 = strip.label("P", text("16", NUM, OPP, BOLD), DOWN)
        hop_k, _ = strip.hops("J", 1, side=UP, numbered=False)
        hop_p, _ = strip.hops("O", 1, side=UP, numbered=False)
        work = math_row(math_line("27", "-", "11", "=", "16", colors={"11": FWD, "16": OPP}), 0)
        n = self.narrate(
            id="ex1_02",
            text="K is eleven, one after J at ten. Twenty-seven minus eleven is sixteen, and sixteen is one after O "
                 "at fifteen. So the opposite of K is P.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "eleven")
        self.play(FadeIn(k11))
        self.at_word(n, "after")
        self.play(FadeIn(j10), Create(hop_k))
        self.at_word(n, "minus")
        self.play(Write(work))
        self.at_word(n, "fifteen")
        self.play(FadeIn(o15), Create(hop_p), FadeIn(p16))
        self.at_word(n, "opposite")
        self.play(strip.mark("P", OPP), Flash(strip.cell("P"), color=OPP))
        self.wait_for_narration(n)

        # HEAR: the check.  SEE: an arc K-P labelled 11 + 16 = 27.
        arc = strip.pair_arc("K", "P", angle=-PI / 2)
        arc_label = math_line("11", "+", "16", "=", "27", colors={"11": FWD, "16": OPP, "27": ANCHOR}, size=34)
        arc_label.next_to(arc, UP, buff=0.12)
        n = self.narrate(
            id="ex1_03",
            text="Check: eleven plus sixteen is twenty-seven.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(VGroup(hop_k, hop_p, j10, o15)))
        self.at_word(n, "plus")
        self.play(Create(arc), FadeIn(arc_label, shift=DOWN * 0.1))
        self.validator.check_in_frame(VGroup(question, arc_label, strip, work))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_example_basic")

    # ================================== 6. EXAMPLE 2: APPLICATION ==========

    def example_application(self):
        self.scene_start("S06_example_application", title="Example 2 - Application")

        question = self.question_card("HORSE: how many letters have their opposite also in the word?")
        word = word_tiles("HORSE", side=1.0, buff=0.9).move_to(UP * 0.9)
        opps = VGroup(*[tile(opposite(ch), 0.75).next_to(t, DOWN, buff=0.9) for ch, t in zip("HORSE", word)])
        links = VGroup(*[Arrow(t.get_bottom(), o.get_top(), buff=0.1, color=OPP, stroke_width=3,
                               max_tip_length_to_length_ratio=0.25) for t, o in zip(word, opps)])
        present = [opposite(ch) in "HORSE" for ch in "HORSE"]
        marks = VGroup(*[text("✓" if ok else "✗", LABEL, GOOD if ok else BAD, BOLD).next_to(o, RIGHT, buff=0.15)
                         for ok, o in zip(present, opps)])

        n = self.narrate(
            id="ex2_01",
            text="Here's a common application. In the word HORSE, how many letters have their opposite letter "
                 "also in the word?",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(question, shift=DOWN * 0.3))
        self.at_word(n, "HORSE")
        self.play(LaggedStart(*[FadeIn(t, shift=UP * 0.2) for t in word], lag_ratio=0.15))
        self.wait_for_narration(n)

        n = self.narrate(
            id="ex2_02",
            text="Go letter by letter.",
            voice="default",
            subtitle=True,
        )
        self.play(Indicate(word[0], color=FOCUS))
        self.wait_for_narration(n)

        # HEAR: each letter's opposite, and whether it is in the word.
        # SEE: the opposite appears under each letter on "opposite" / "pairs",
        # and its tick or cross on the word that decides it.
        n = self.narrate(
            id="ex2_03",
            text="H is eight, so its opposite is nineteen, which is S. S is in the word, so that's a match. "
                 "O's opposite is L, and L isn't in HORSE. R's opposite is I, which isn't there. "
                 "S pairs with H, which we've already found. E's opposite is V, which isn't there.",
            voice="default",
            subtitle=True,
        )
        cues = [("opposite", 1, "match", 1), ("opposite", 2, "isn't", 1), ("opposite", 3, "isn't", 2),
                ("pairs", 1, "already", 1), ("opposite", 4, "isn't", 3)]
        for k, (show_w, show_o, judge_w, judge_o) in enumerate(cues):
            self.at_word(n, show_w, occurrence=show_o)
            self.play(GrowArrow(links[k]), FadeIn(opps[k], shift=DOWN * 0.15), run_time=0.5)
            self.at_word(n, judge_w, occurrence=judge_o)
            self.play(FadeIn(marks[k], scale=1.4), run_time=0.4)
        self.wait_for_narration(n)

        # HEAR: only H and S.  SEE: H and S light up, joined by an arc; the answer.
        arc = ArcBetweenPoints(word[0].get_top() + UP * 0.1, word[3].get_top() + UP * 0.1,
                               angle=-PI / 3, color=GOOD, stroke_width=4)
        answer = pill("Answer: 2 letters  (1 pair)", GOOD, size=LABEL).move_to(DOWN * 2.4)
        n = self.narrate(
            id="ex2_04",
            text="So only H and S qualify. The answer is two letters, forming one pair.",
            voice="default",
            subtitle=True,
        )
        self.play(mark_tile(word[0], GOOD), mark_tile(word[3], GOOD), Create(arc))
        self.at_word(n, "answer")
        self.play(FadeIn(answer, scale=1.1))
        self.validator.check_in_frame(VGroup(question, arc, word, opps, marks, answer))
        self.wait_for_narration(n)

        n = self.narrate(
            id="ex2_05",
            text="Notice the method: check every letter, and count each pair once, so that you don't double-count.",
            voice="default",
            subtitle=True,
        )
        cap = self.caption("Check every letter · count each pair once", FOCUS)
        self.play(FadeOut(answer), FadeIn(cap, shift=UP * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_example_application")

    # ================================= 7. EXAMPLE 3: EXAM-ORIENTED ==========

    def example_exam(self):
        self.scene_start("S07_example_exam", title="Example 3 - Exam-Oriented")

        xs = [-3.9, -1.3, 1.3, 3.9]
        top, bottom, arrows = self.code_columns("GOLD", "TLOW", xs, top_y=2.0, bottom_y=0.1)
        sums = VGroup(*[math_line(a, "+", b, colors={a: FWD, b: OPP}, size=36).next_to(bt, DOWN, buff=0.35)
                        for (a, b), bt in zip([("7", "20"), ("15", "12"), ("12", "15"), ("4", "23")], bottom)])
        equals = VGroup(*[math_line("=", "27", colors={"27": ANCHOR}, size=36).next_to(s, DOWN, buff=0.15)
                          for s in sums])

        # HEAR: back to GOLD -> TLOW.  SEE: the code again.
        n = self.narrate(
            id="ex3_01",
            text="Now let's go back to our opening code, GOLD to TLOW.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(top), FadeIn(bottom), FadeIn(arrows))
        self.wait_for_narration(n)

        # HEAR: each pair's sum.  SEE: the sum under each column, then "= 27"
        # under all four on "Every"; the arrows turn into the opposite colour.
        n = self.narrate(
            id="ex3_02",
            text="Check each pair against the rule. G and T give seven plus twenty. O and L give fifteen plus twelve. "
                 "D and W give four plus twenty-three. Every pair adds up to twenty-seven. "
                 "So each letter has simply been replaced by its opposite.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "seven")
        self.play(FadeIn(sums[0], shift=DOWN * 0.1))
        self.at_word(n, "fifteen")
        self.play(FadeIn(sums[1], shift=DOWN * 0.1), FadeIn(sums[2], shift=DOWN * 0.1))
        self.at_word(n, "four")
        self.play(FadeIn(sums[3], shift=DOWN * 0.1))
        self.at_word(n, "Every")
        self.play(LaggedStart(*[FadeIn(e, scale=0.7) for e in equals], lag_ratio=0.2))
        self.at_word(n, "opposite")
        self.play(arrows.animate.set_color(OPP))
        self.validator.check_in_frame(VGroup(top, equals))
        self.wait_for_narration(n)

        # HEAR: apply it to SILVER.  SEE: the question card and SILVER.
        question = self.question_card("Using the same code, how is SILVER written?")
        xs6 = [(-2.5 + k) * 1.5 for k in range(6)]
        s_top, s_bottom, s_arrows = self.code_columns("SILVER", "HROVEI", xs6, top_y=0.7, bottom_y=-1.3, side=0.85)
        n = self.narrate(
            id="ex3_03",
            text="Now apply the rule to SILVER.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(VGroup(top, bottom, arrows, sums, equals)))
        self.play(FadeIn(question, shift=DOWN * 0.3),
                  LaggedStart(*[FadeIn(t, shift=UP * 0.2) for t in s_top], lag_ratio=0.1))
        self.wait_for_narration(n)

        # HEAR: letter by letter.  SEE: each code letter on its "becomes".
        n = self.narrate(
            id="ex3_04",
            text="S becomes H. I becomes R. L becomes O. V becomes E. E becomes V. And R becomes I.",
            voice="default",
            subtitle=True,
        )
        for k in range(6):
            self.at_word(n, "becomes", occurrence=k + 1)
            self.play(GrowArrow(s_arrows[k].set_color(OPP)), FadeIn(s_bottom[k], shift=DOWN * 0.15), run_time=0.45)
        self.wait_for_narration(n)

        answer = pill("SILVER  →  HROVEI", GOOD, size=LABEL).next_to(s_bottom, DOWN, buff=0.45)
        n = self.narrate(
            id="ex3_05",
            text="The code for SILVER is HROVEI.",
            voice="default",
            subtitle=True,
        )
        self.play(*[mark_tile(t, GOOD) for t in s_bottom], FadeIn(answer, scale=1.1))
        self.validator.check_in_frame(VGroup(question, s_top, answer))
        self.wait_for_narration(n)

        # HEAR: why this is a favourite; the quick test.  SEE: caption.
        n = self.narrate(
            id="ex3_06",
            text="The shift sizes looked random at first, but the underlying rule was simple. That's why "
                 "opposite-letter coding is a favourite. The test is quick: when the shifts don't match, "
                 "check whether the positions add up to twenty-seven.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "test")
        cap = self.caption("Shifts don't match?  Test: do positions add up to 27?", ANCHOR)
        self.play(FadeOut(answer), FadeIn(cap, shift=UP * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S07_example_exam")

    # ======================================== 8. EXAM APPLICATION ==========

    def exam_application(self):
        self.scene_start("S08_exam", title="Exam Application")

        card_w, card_h = 4.0, 2.6
        specs = [("1  Signal", "Shifts are unequal and change direction", FOCUS),
                 ("2  Test", "position + code position = 27, for every letter", ANCHOR),
                 ("3  Apply", "replace each letter with 27 − position", GOOD)]
        steps = VGroup(*[
            self.card(VGroup(pill(head, c, size=LABEL), fitted_text(body, card_w - 0.7, SMALL, INK, max_lines=3))
                      .arrange(DOWN, buff=0.35), width=card_w, height=card_h, color=c)
            for head, body, c in specs]).arrange(RIGHT, buff=0.35)
        fit_width(steps, SAFE_W).move_to(UP * 0.8)
        self.validator.check_in_frame(steps)

        # HEAR: signal, then test.  SEE: step cards 1 and 2 on their words.
        n = self.narrate(
            id="exam_01",
            text="So in the exam, the signal is shifts that are unequal and change direction. "
                 "When you see that, test the sum of twenty-seven.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "signal")
        self.play(FadeIn(steps[0], shift=UP * 0.3))
        self.at_word(n, "test")
        self.play(FadeIn(steps[1], shift=UP * 0.3))
        self.wait_for_narration(n)

        # HEAR: every letter, then apply.  SEE: card 2 pulses, card 3 appears.
        n = self.narrate(
            id="exam_02",
            text="The test must hold for every letter, not just the first one. "
                 "Once it does, apply the rule letter by letter.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "every")
        self.play(Indicate(steps[1], color=ANCHOR, scale_factor=1.04))
        self.at_word(n, "apply")
        self.play(FadeIn(steps[2], shift=UP * 0.3))
        self.wait_for_narration(n)

        # HEAR: direct questions, and the link to the next topic.
        n = self.narrate(
            id="exam_03",
            text="Opposite letters also appear in direct questions, such as what is the opposite of the fourth letter "
                 "from the right? These combine this topic with position counting, which we'll cover next.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "direct")
        cap = self.caption("e.g.  Opposite of the 4th letter from the right?", FOCUS)
        self.play(FadeIn(cap, shift=UP * 0.2))
        self.at_word(n, "next")
        nxt = pill("next topic", MUTED).next_to(cap, UP, buff=0.3).align_to(cap, RIGHT)
        self.play(FadeIn(nxt, shift=DOWN * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S08_exam")

    # =========================================== 9. COMMON MISTAKE ==========

    def common_mistake(self):
        self.scene_start("S09_mistake", title="Common Mistake")

        wrong = self.card(VGroup(text("✗", 40, BAD, BOLD),
                                 math_line("26", "-", "11", "=", "15", r"\rightarrow", r"\text{O}", size=40))
                          .arrange(RIGHT, buff=0.3), color=BAD)
        right = self.card(VGroup(text("✓", 40, GOOD, BOLD),
                                 math_line("27", "-", "11", "=", "16", r"\rightarrow", r"\text{P}", size=40))
                          .arrange(RIGHT, buff=0.3), color=GOOD)
        wrong.move_to(LEFT_ZONE + UP * (CARD_TOP - wrong.height / 2))
        right.move_to(RIGHT_ZONE + UP * (CARD_TOP - right.height / 2))
        strip = AlphabetStrip().move_to(UP * STRIP_Y)
        trap = text("trap option", SMALL, BAD, BOLD)
        strip.label("O", trap, DOWN, buff=0.2)

        # HEAR: 26 instead of 27 again.  SEE: wrong vs right, O (red) beside P (green).
        n = self.narrate(
            id="mistake_01",
            text="The first mistake is the same off-by-one error from the previous topic: subtracting from "
                 "twenty-six instead of twenty-seven. That gives the letter next to the correct answer, which is "
                 "exactly the kind of wrong option an examiner likes to include.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(wrong, shift=RIGHT * 0.3))
        self.at_word(n, "instead")
        self.play(FadeIn(right, shift=LEFT * 0.3))
        self.at_word(n, "next")
        self.play(FadeIn(strip))
        self.play(strip.mark("O", BAD), strip.mark("P", GOOD))
        self.at_word(n, "examiner")
        self.play(FadeIn(trap, shift=UP * 0.1))
        self.wait_for_narration(n)

        # HEAR: MAT -> NBU; M -> N looks like "opposite".  SEE: the code, and the
        # M -> N arrow labelled "opposite".
        xs = [-2.4, 0.0, 2.4]
        top, bottom, arrows = self.code_columns("MAT", "NBU", xs, top_y=1.2, bottom_y=-0.9)
        opp_label = pill("opposite?", OPP, size=SMALL).next_to(arrows[0], LEFT, buff=0.2)
        n = self.narrate(
            id="mistake_02",
            text="The second mistake is subtler. Suppose MAT is coded as NBU. M becomes N, which is its opposite. "
                 "A learner who checks only the first letter concludes that this is opposite coding.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(VGroup(wrong, right, strip, trap)))
        self.at_word(n, "Suppose")
        self.play(FadeIn(top), FadeIn(bottom))
        self.at_word(n, "becomes")
        self.play(GrowArrow(arrows[0]))
        self.at_word(n, "opposite", occurrence=1)
        self.play(FadeIn(opp_label, shift=RIGHT * 0.1))
        self.at_word(n, "only")
        self.play(Indicate(VGroup(top[0], bottom[0]), color=FOCUS))
        self.wait_for_narration(n)

        # HEAR: A -> B, not Z: a forward shift of one.  SEE: the other arrows,
        # "+1" on every arrow (M -> N now double-labelled), a crossed-out Z.
        plus = VGroup(*[pill("+1", GOOD, size=SMALL).next_to(a, RIGHT, buff=0.2) for a in arrows])
        not_z = VGroup(text("not Z", SMALL, BAD, BOLD)).next_to(bottom[1], DOWN, buff=0.25)
        n = self.narrate(
            id="mistake_03",
            text="But A becomes B, not Z. The real rule is a forward shift of one.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "becomes")
        self.play(GrowArrow(arrows[1]), GrowArrow(arrows[2]))
        self.at_word(n, "not")
        self.play(FadeIn(not_z, shift=UP * 0.1))
        self.at_word(n, "shift")
        self.play(LaggedStart(*[FadeIn(p, shift=LEFT * 0.1) for p in plus], lag_ratio=0.3),
                  *[mark_tile(b, GOOD) for b in bottom])
        self.validator.check_in_frame(VGroup(top, bottom, opp_label, plus, not_z))
        self.wait_for_narration(n)

        # HEAR: M-N is the only ambiguous pair; check every letter.
        n = self.narrate(
            id="mistake_04",
            text="The M–N pair is the only pair where the opposite is also the next letter, so a single letter "
                 "can't tell the two rules apart. Always confirm the rule on every letter before you apply it.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "only")
        self.play(Indicate(VGroup(opp_label, plus[0]), color=FOCUS, scale_factor=1.15))
        self.at_word(n, "Always")
        cap = self.caption("Confirm the rule on every letter", FOCUS)
        self.play(FadeIn(cap, shift=UP * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S09_mistake")

    # ================================================ 10. PRACTICE ==========

    def practice(self):
        self.scene_start("S10_practice", title="Practice Question")

        card_w = SAFE_W - 1.0
        q1 = VGroup(pill("Q1", FOCUS), fitted_text("What is the opposite of U?", card_w - 1.6, BODY))
        q2 = VGroup(pill("Q2", FOCUS), fitted_text("WIZARD: how many letters have their opposite also in the word?",
                                                   card_w - 1.6, BODY))
        for q in (q1, q2):
            q.arrange(RIGHT, buff=0.35)
        questions = VGroup(q1, q2).arrange(DOWN, buff=0.6, aligned_edge=LEFT)
        board = self.card(questions, color=FOCUS).move_to(UP * 0.4)

        n = self.narrate(
            id="practice_01",
            text="Now try these two yourself.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(board[0]), FadeIn(questions, shift=UP * 0.2))
        self.play(questions.animate.set_opacity(0.45))
        self.wait_for_narration(n)

        n = self.narrate(
            id="practice_02",
            text="First, what's the opposite of U?",
            voice="default",
            subtitle=True,
        )
        self.play(q1.animate.set_opacity(1))
        self.wait_for_narration(n)

        # SILENCE (pause_after): countdown ring while the learner thinks.
        n = self.narrate(
            id="practice_03",
            text="Second, in the word WIZARD, how many letters have their opposite letter also present in the word?",
            voice="default",
            subtitle=True,
            pause_after=6.0,
        )
        self.play(q2.animate.set_opacity(1))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        self.clear_stage()
        self.scene_end("S10_practice")

    # ================================================== 11. ANSWER ==========

    def answer(self):
        self.scene_start("S11_answer", title="Answer and Explanation")

        # HEAR: U = 21 (after T), 27 - 21 = 6 = F.  SEE: the strip, U with 21,
        # the working line, F lit, and a U-F arc.
        tag_q1 = pill("Q1", FOCUS).move_to(UP * (CARD_TOP - 0.3))
        strip = AlphabetStrip().move_to(UP * STRIP_Y)
        t20 = strip.label("T", text("20", NUM, ANCHOR), DOWN)
        u21 = strip.label("U", text("21", NUM, FWD, BOLD), DOWN)
        f6 = strip.label("F", text("6", NUM, OPP, BOLD), DOWN)
        hop, _ = strip.hops("T", 1, side=UP, numbered=False)
        work = math_row(math_line("27", "-", "21", "=", "6", r"\rightarrow", r"\text{F}",
                                  colors={"21": FWD, "6": OPP, r"\text{F}": GOOD}), 0)
        n = self.narrate(
            id="answer_01",
            text="For the first question, U is twenty-one, one after T. Twenty-seven minus twenty-one is six, "
                 "so the opposite of U is F.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(tag_q1), FadeIn(strip), strip.mark("U", FWD))
        self.at_word(n, "after")
        self.play(FadeIn(t20), Create(hop), FadeIn(u21))
        self.at_word(n, "six")
        self.play(Write(work))
        self.at_word(n, "opposite")
        arc = strip.pair_arc("F", "U", color=GOOD, angle=-PI / 3)
        self.play(FadeOut(hop), strip.mark("F", GOOD), FadeIn(f6), Create(arc))
        self.wait_for_narration(n)

        # HEAR: WIZARD letter by letter.  SEE: the word, then one arc per pair
        # (W-D, I-R, Z-A), nested like the fold.
        tag_q2 = pill("Q2", FOCUS).move_to(tag_q1)
        word = word_tiles("WIZARD", side=1.0, buff=0.45).move_to(DOWN * 0.4)
        pair_colors = [OPP, ANCHOR, FWD]
        arcs = VGroup(*[ArcBetweenPoints(word[i].get_top() + UP * 0.1, word[j].get_top() + UP * 0.1,
                                         angle=-PI / 2, color=c, stroke_width=4)
                        for (i, j), c in zip([(0, 5), (1, 4), (2, 3)], pair_colors)])
        n = self.narrate(
            id="answer_02",
            text="For the second, go letter by letter. W is twenty-three, and its opposite is D, at four. "
                 "D is in the word. I is nine, and its opposite is R, at eighteen. R is in the word. "
                 "Z's opposite is A, which is also in the word.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(VGroup(strip, t20, u21, f6, work, arc)), FadeTransform(tag_q1, tag_q2))
        self.play(LaggedStart(*[FadeIn(t, shift=UP * 0.2) for t in word], lag_ratio=0.1))
        for k, (i, j) in enumerate([(0, 5), (1, 4), (2, 3)]):
            self.at_word(n, "opposite", occurrence=k + 1)
            self.play(Create(arcs[k]), mark_tile(word[i], pair_colors[k]), mark_tile(word[j], pair_colors[k]))
        self.wait_for_narration(n)

        # HEAR: all six, three pairs.  SEE: the answer pill.
        answer = pill("All 6 letters  ·  3 complete pairs", GOOD, size=LABEL).next_to(word, DOWN, buff=0.6)
        n = self.narrate(
            id="answer_03",
            text="That accounts for all six letters: W and D, I and R, Z and A. "
                 "The answer is all six letters, forming three complete pairs.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "answer")
        self.play(FadeIn(answer, scale=1.1))
        self.validator.check_in_frame(VGroup(tag_q2, arcs, word, answer))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answer_04",
            text="WIZARD is an unusual word: it's built entirely from opposite pairs. "
                 "And the only way to be sure of that is the letter-by-letter check.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "entirely")
        self.play(Indicate(arcs, color=FOCUS, scale_factor=1.05))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S11_answer")

    # ========================================== 12. QUICK REVISION ==========

    def quick_revision(self):
        self.scene_start("S12_revision", title="Quick Revision")

        card_w, card_h = SAFE_W - 1.0, 5.2
        items = [
            ("Opposite letter = same position from the other end", OPP),
            ("Opposite of position n  →  position 27 − n", ANCHOR),
            ("Positions of opposite letters add to 27", FOCUS),
            ("13 pairs: A–Z … M–N  (no letter is its own opposite)", FWD),
            ("Unequal shifts in a code  →  test for opposites", INK),
            ("Verify every letter  (M → N is also a +1 shift)", BAD),
        ]
        bullets = VGroup(*[VGroup(Dot(radius=0.07, color=c), fitted_text(s, card_w - 1.4, BODY, c))
                           .arrange(RIGHT, buff=0.3) for s, c in items]).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        board = self.card(bullets, width=card_w, height=card_h).move_to(DOWN * 0.1)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="revision_01",
            text="Let's quickly revise.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(board[0]))
        self.wait_for_narration(n)

        n = self.narrate(
            id="revision_02",
            text="An opposite letter is the letter at the same position from the other end of the alphabet. "
                 "For a letter at position n, the opposite is at twenty-seven minus n, so the two positions always "
                 "add up to twenty-seven.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(bullets[0], shift=RIGHT * 0.2))
        self.at_word(n, "minus")
        self.play(FadeIn(bullets[1], shift=RIGHT * 0.2))
        self.at_word(n, "always")
        self.play(FadeIn(bullets[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="revision_03",
            text="There are thirteen pairs, from A–Z to M–N, and no letter is its own opposite.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(bullets[3], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="revision_04",
            text="In coding questions, unequal shifts are the signal to test for opposites. "
                 "Always confirm the rule on every letter.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(bullets[4], shift=RIGHT * 0.2))
        self.at_word(n, "Always")
        self.play(FadeIn(bullets[5], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S12_revision")

    # ================================================= 13. CLOSING ==========
    # Purpose: both skills together, and a teaser for Letter-Position Questions
    # (a pointer moving left and right on the strip).

    def closing(self):
        self.scene_start("S13_closing", title="Closing")

        strip = AlphabetStrip().move_to(DOWN * 0.1)
        arc = strip.pair_arc("K", "P", angle=-PI / 2)

        n = self.narrate(
            id="closing_01",
            text="You can now position any letter from either end, and find its opposite instantly.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(strip))
        self.at_word(n, "opposite")
        self.play(strip.mark("K", FWD), strip.mark("P", OPP), Create(arc))
        self.wait_for_narration(n)

        # HEAR: next topic.  SEE: a pointer steps left, then right, from K.
        pointer = Triangle(color=FOCUS, fill_opacity=1).scale(0.13)
        strip.label("K", pointer, DOWN, buff=0.12)

        def under(ch):
            return strip.cell(ch).get_bottom() + DOWN * (0.12 + pointer.height / 2)

        nxt = pill("Next:  Letter-Position Questions", ANCHOR, size=BODY).move_to(DOWN * 2.3)
        n = self.narrate(
            id="closing_02",
            text="Next, we'll combine these skills in the question type that tests them together: finding a letter "
                 "that is a given number of steps to the left or right of another letter, counted from either end.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(arc), strip.unmark("P"), FadeIn(pointer))
        self.at_word(n, "left")
        self.play(pointer.animate.move_to(under("F")), run_time=1.0)
        self.at_word(n, "right")
        self.play(pointer.animate.move_to(under("S")), run_time=1.4)
        self.play(FadeIn(nxt, scale=1.1))
        self.validator.check_in_frame(VGroup(strip, pointer, nxt))
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S13_closing")

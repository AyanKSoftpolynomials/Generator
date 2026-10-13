"""
animation.py for the LMS video generator.

Course : Pre-C-CAT - Section A
Module : Module 1 - Logical Reasoning
Lesson : Lesson 5 - Symbols & Notations (Coded Inequalities)
Topic  : Combining Inequalities (Topic 2)

Source script:
  C:\\Scripts\\Section A\\Module 1 - Logical Reasoning\\Lesson 05 - Symbols & Notations\\
  Topic 2 - Combining Inequalities.md

Built on the golden-reference pattern:
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``.

Opening: not the first video of the course, so no spoken course welcome.
The module > lesson > topic trail is shown on screen (silent), followed by a
one-idea recap of Topic 1 (decoding) and what this video covers.

Colour code for signs (used everywhere): signs pointing "down the chain"
(>, ≥) are blue, signs pointing "up" (<, ≤) are orange, "=" is grey. Two
colours on one path = opposite directions = no definite relation. Every
result on screen is computed by ``combine`` (direction + strength rules).

Section map (script heading -> VISUAL PLAN scene):
  S00 Intro (trail + recap)   -> -
  S01 Opening Hook            -> scene 1
  S02 Concept (the bridge)    -> scene 2
  S03 Building a chain        -> scene 3
  S04 Direction rule          -> scene 4
  S05 Strength rule           -> scene 5
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

DOWN_C = "#4FC3F7"     # > and ≥ : pointing one way
UP_C = "#FFB74D"       # < and ≤ : pointing the other way
EQ_C = MUTED           # = : neutral
TERM = "#CE93D8"       # the common term / bridge
FOCUS = "#FFD54F"      # "look here" / a traced path
GOOD = "#66BB6A"       # a definite relation
BAD = "#EF5350"        # no definite relation / wrong

FONT = "Segoe UI"
MIN_FONT = 22          # readable floor: text is never shrunk below this
TITLE = 46
BODY = 30
LABEL = 28
SMALL = 24
MATH = 56

SIGN_TEX = {">": ">", "<": "<", ">=": r"\ge", "<=": r"\le", "=": "="}
SIGN_COLOR = {">": DOWN_C, ">=": DOWN_C, "<": UP_C, "<=": UP_C, "=": EQ_C}
FLIP = {">": "<", "<": ">", ">=": "<=", "<=": ">=", "=": "="}


def combine(signs):
    """Direction + strength rules. Returns the combined sign (">", ">=", "<",
    "<=", "=") or None when the path points in opposite directions."""
    down = any(s in (">", ">=") for s in signs)
    up = any(s in ("<", "<=") for s in signs)
    if down and up:
        return None
    strict = any(s in (">", "<") for s in signs)
    if down:
        return ">" if strict else ">="
    if up:
        return "<" if strict else "<="
    return "="


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


# ================================================= inequality helpers ====

def ineq(s, size=MATH):
    """A spaced chain like "P <= Q < R < S" as MathTex: terms at even token
    indices, signs at odd ones (coloured by direction)."""
    toks = s.split()
    parts = [SIGN_TEX.get(t, t) for t in toks]
    line = MathTex(*parts, font_size=size, color=INK)
    for k, t in enumerate(toks):
        if k % 2 == 1:
            line[k].set_color(SIGN_COLOR[t])
    return line


def signs_of(s):
    return s.split()[1::2]


def terms_of(s):
    return s.split()[0::2]


def result_of(s, a, b):
    """The relation between terms a and b of chain ``s`` as a string ("A > D"),
    or None (no definite relation)."""
    terms = terms_of(s)
    i, j = terms.index(a), terms.index(b)
    lo, hi = min(i, j), max(i, j)
    sign = combine(signs_of(s)[lo:hi])
    if sign is None:
        return None
    if i > j:
        sign = FLIP[sign]
    return f"{a} {sign} {b}"


def under_bar(part, whole, color=FOCUS, width=10):
    """A highlight bar under ``part`` of the MathTex ``whole``.

    Used instead of a SurroundingRectangle: the validator treats a rectangle
    drawn around part of a MathTex as a box that must contain the WHOLE
    formula, so boxes around partial paths were reported as overflowing.
    """
    y = whole.get_bottom()[1] - 0.18                 # same height for every bar
    return Line([part.get_left()[0] - 0.08, y, 0], [part.get_right()[0] + 0.08, y, 0],
                color=color, stroke_width=width)


def path_box(line, i, j, color=FOCUS):
    """Mark the tokens from term i to term j (inclusive) of a chain."""
    lo, hi = min(i, j), max(i, j)
    return under_bar(line[2 * lo:2 * hi + 1], line, color)


def no_relation():
    stamp = pill("no definite relation", BAD, size=LABEL)
    return stamp.rotate(-0.08)


# ============================================================= lesson ====

class CombiningInequalitiesVideo(LMSScene):
    lesson_title = "Combining Inequalities"

    def construct(self):
        self.camera.background_color = BG

        self.lesson_intro()
        self.hook()
        self.concept()
        self.building()
        self.direction_rule()
        self.strength_rule()
        self.example_basic()
        self.example_two()
        self.example_coded()
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

    def caption(self, s, color=INK):
        """One-line keyword caption in a fixed-width bar at the bottom of the frame."""
        t = fitted_text(s, SAFE_W - 1.0, BODY, color)
        bar = self.card(t, width=SAFE_W - 0.4, height=t.height + 0.9)
        return bar.move_to(UP * BOTTOM_Y)

    def breadcrumb(self, *parts):
        """Silent 'where are we' trail: Module > Lesson > Topic."""
        colors = [DOWN_C, "#F48FB1", UP_C]
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

    def rule_card(self, head, lines, color):
        body = VGroup(text(head, LABEL, color, BOLD),
                      *[fitted_text(l, SAFE_W - 1.4, SMALL, INK, max_lines=2) for l in lines])
        body.arrange(DOWN, buff=0.18, aligned_edge=LEFT)
        return self.card(body, color=color)

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

    def verdict_for(self, chain_str, a, b, size=MATH):
        """The on-screen verdict for a pair: a green relation or a red stamp."""
        r = result_of(chain_str, a, b)
        if r is None:
            return no_relation()
        line = ineq(r, size=size)
        return VGroup(line, text("✓", LABEL, GOOD, BOLD)).arrange(RIGHT, buff=0.3)

    # ========================================= 0. LESSON INTRO ==========
    # Purpose: where we are (silent trail), last time (one idea), today.

    def lesson_intro(self):
        self.scene_start("S00_intro", title="Lesson Introduction")

        crumb = self.breadcrumb("Module 1 · Logical Reasoning", "Lesson 5 · Symbols & Notations", "Topic 2")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        last = pill("Last time", MUTED, size=SMALL)
        decoded = VGroup(*[VGroup(text(sym, TITLE, TERM, BOLD), MathTex(r"\to", rel, font_size=52, color=INK))
                           .arrange(RIGHT, buff=0.2)
                           for sym, rel in [("@", r"\le"), ("#", r"\ge"), ("$", "<"), ("%", ">"), ("&", "=")]])
        decoded.arrange(RIGHT, buff=0.7)
        fit_width(decoded, SAFE_W)
        recap = VGroup(last, decoded).arrange(DOWN, buff=0.5).move_to(UP * 0.2)
        self.validator.check_in_frame(VGroup(crumb, recap))

        # SEE (silent): the trail.  HEAR: decoding in one sentence.
        n = self.narrate(
            id="intro_01",
            text="Last time, you decoded each coded symbol into an ordinary relation, like less than or equal to.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.play(FadeIn(last))
        self.at_word(n, "decoded")
        self.play(LaggedStart(*[FadeIn(d, shift=UP * 0.2) for d in decoded], lag_ratio=0.2))
        self.wait_for_narration(n)

        # HEAR: today, combine them.  SEE: the title.
        title = fitted_text("Combining Inequalities", SAFE_W, 72, INK, BOLD)
        underline = Line(LEFT, RIGHT, color=TERM, stroke_width=5).set_width(title.width * 0.6)
        VGroup(title, underline).arrange(DOWN, buff=0.2).move_to(UP * 0.2)
        n = self.narrate(
            id="intro_02",
            text="In this video, we combine those relations, and learn exactly when a conclusion can be drawn.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(recap, shift=UP * 0.3))
        self.at_word(n, "combine")
        self.play(Write(title), run_time=1.1)
        self.play(GrowFromCenter(underline))
        self.wait_for_narration(n)

        # HEAR: the three objectives.  SEE: one row per objective, on its word.
        goals = [
            ("Build one chain from several statements", TERM),
            ("Decide whether two terms have a definite relation", DOWN_C),
            ("Find the exact sign that results", GOOD),
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
            text="By the end of this video, you'll be able to build one chain from several statements, decide whether "
                 "two terms have a definite relation, and find the exact sign that results.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(underline), ReplacementTransform(title, small_title), run_time=0.8)
        self.play(FadeIn(objectives[0]), FadeIn(heading))
        for row, spoken in zip(rows, ["build", "decide", "exact"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.5)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_intro")

    # ================================================= 1. HOOK ==========

    def hook(self):
        self.scene_start("S01_hook", title="Opening Hook")

        given = VGroup(ineq("A > B", size=72), text("and", LABEL, MUTED), ineq("B < C", size=72))
        given.arrange(RIGHT, buff=0.6).move_to(UP * 1.9)
        ask = VGroup(text("A", TITLE, INK, BOLD), text("?", TITLE, FOCUS, BOLD), text("C", TITLE, INK, BOLD))
        ask.arrange(RIGHT, buff=0.4).move_to(UP * 0.6)
        both = pill("A and C are both bigger than B", TERM, size=LABEL).move_to(DOWN * 0.5)
        options = VGroup(ineq("A > C", size=44), ineq("A < C", size=44), ineq("A = C", size=44))
        options.arrange(RIGHT, buff=1.0).move_to(DOWN * 1.6)
        self.validator.check_in_frame(VGroup(given, ask, both, options))

        n = self.narrate(
            id="hook_01",
            text="If A is greater than B, and B is less than C, what's the relation between A and C?",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(given[0], shift=DOWN * 0.2))
        self.at_word(n, "less")
        self.play(FadeIn(given[1:], shift=DOWN * 0.2))
        self.at_word(n, "relation")
        self.play(FadeIn(ask, scale=1.2))
        self.wait_for_narration(n)

        # HEAR: all three are possible.  SEE: the three options appear.
        n = self.narrate(
            id="hook_02",
            text="It's tempting to say something definite. But think about it: A and C are both bigger than B. That's all "
                 "we know. A could be larger than C, smaller than C, or equal to it.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "both")
        self.play(FadeIn(both, shift=UP * 0.1))
        for opt, spoken in zip(options, ["larger", "smaller", "equal"]):
            self.at_word(n, spoken)
            self.play(FadeIn(opt, shift=UP * 0.2), run_time=0.4)
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_03",
            text="Knowing when a relation exists, and when it doesn't, is the heart of every coded-inequality question.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "heart")
        cap = self.caption("When does a relation exist, and when doesn't it?", FOCUS)
        self.play(FadeIn(cap, shift=UP * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S01_hook")

    # ============================================== 2. CONCEPT ==========
    # Purpose: the common term is a bridge that only works in one direction.

    def height_scale(self, centre, heights):
        """A vertical 'height' scale with labelled markers at the given heights
        (``heights`` = {label: ValueTracker}). Returns the group."""
        axis = Line(centre + DOWN * 1.6, centre + UP * 1.6, color=MUTED, stroke_width=3)
        marks = VGroup()
        for label, tracker in heights.items():
            dot = always_redraw(lambda t=tracker: Dot(centre + UP * t.get_value(), radius=0.1, color=INK))
            tag = always_redraw(lambda t=tracker, l=label: text(l, LABEL, TERM if l == "B" else INK, BOLD)
                                .next_to(centre + UP * t.get_value(), RIGHT, buff=0.25))
            marks.add(dot, tag)
        return VGroup(axis, marks)

    def concept(self):
        self.scene_start("S02_concept", title="Concept Introduction")

        s1, s2 = ineq("A > B", size=60), ineq("B > C", size=60)
        pair = VGroup(s1, s2).arrange(RIGHT, buff=1.2).move_to(UP * 2.3)
        bridge = VGroup(under_bar(s1[2], s1, TERM, width=8), under_bar(s2[0], s2, TERM, width=8))
        bridge_tag = pill("common term: the bridge", TERM, size=SMALL).next_to(pair, DOWN, buff=0.25)

        n = self.narrate(
            id="concept_01",
            text="Two statements can be combined only if they share a common term. The common term acts as a bridge.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(pair, shift=DOWN * 0.2))
        self.at_word(n, "common")
        self.play(Create(bridge))
        self.at_word(n, "bridge")
        self.play(FadeIn(bridge_tag, shift=UP * 0.1))
        self.wait_for_narration(n)

        # HEAR: same direction works; both-above-B tells nothing.  SEE: two
        # height scales; on the right, A and C keep trading places above B.
        left_h = {"A": ValueTracker(1.2), "B": ValueTracker(0.0), "C": ValueTracker(-1.2)}
        right_h = {"A": ValueTracker(1.2), "B": ValueTracker(-1.2), "C": ValueTracker(0.4)}
        left = self.height_scale(LEFT_ZONE + DOWN * 1.0 + LEFT * 0.4, left_h)
        right = self.height_scale(RIGHT_ZONE + DOWN * 1.0 + LEFT * 0.4, right_h)
        ok = VGroup(ineq("A > C", size=44), text("✓", LABEL, GOOD, BOLD)).arrange(RIGHT, buff=0.2)
        ok.next_to(left, RIGHT, buff=0.4)
        unknown = pill("A vs C ?", BAD, size=SMALL).next_to(right, RIGHT, buff=0.3)
        n = self.narrate(
            id="concept_02",
            text="But a bridge only takes you somewhere if both statements point in the same direction across it. If A "
                 "is above B, and B is above C, then A is above C. If A and C are both above B, the bridge tells you "
                 "nothing about A compared with C.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(bridge_tag))
        self.at_word(n, "above", occurrence=1)
        self.play(FadeIn(left))
        self.at_word(n, "then")
        self.play(FadeIn(ok, scale=1.2))
        self.at_word(n, "both", occurrence=2)
        self.play(FadeIn(right))
        self.play(right_h["A"].animate.set_value(0.2), right_h["C"].animate.set_value(1.3), run_time=1.0)
        self.play(right_h["A"].animate.set_value(0.8), right_h["C"].animate.set_value(0.8), run_time=0.8)
        self.at_word(n, "nothing")
        self.play(right_h["A"].animate.set_value(1.3), right_h["C"].animate.set_value(0.3), FadeIn(unknown), run_time=1.0)
        self.validator.check_in_frame(VGroup(pair, left, ok, unknown))
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_03",
            text="That's the direction rule. A second rule, the strength rule, tells you exactly which sign results.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "direction")
        cap = self.caption("Direction rule: does a relation exist?   ·   Strength rule: which sign?", FOCUS)
        self.play(FadeIn(cap, shift=UP * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_concept")

    # ======================================== 3. BUILDING A CHAIN ==========

    def building(self):
        self.scene_start("S03_building", title="Explanation - Building a Chain")

        statements = [ineq("P <= Q", size=56), ineq("R > Q", size=56), ineq("S > R", size=56)]
        VGroup(*statements).arrange(RIGHT, buff=1.2).move_to(UP * 1.9)
        flipped = [ineq("Q < R", size=56).move_to(statements[1]), ineq("R < S", size=56).move_to(statements[2])]
        tags = VGroup(*[pill("flipped", UP_C, size=SMALL).next_to(f, UP, buff=0.2) for f in flipped])
        chain_s = "P <= Q < R < S"
        joined = ineq(chain_s, size=72).move_to(DOWN * 0.6)
        self.validator.check_in_frame(VGroup(tags, *statements, joined))

        n = self.narrate(
            id="build_01",
            text="First, write all the statements as a single chain, joining them at their common terms.",
            voice="default",
            subtitle=True,
        )
        self.play(LaggedStart(*[FadeIn(s, shift=DOWN * 0.2) for s in statements], lag_ratio=0.3))
        self.at_word(n, "common")
        self.play(Indicate(statements[0][2], color=TERM, scale_factor=1.3), Indicate(statements[1][2], color=TERM,
                                                                                     scale_factor=1.3))
        self.wait_for_narration(n)

        # HEAR: flip a statement that faces the wrong way.  SEE: both flips.
        n = self.narrate(
            id="build_02",
            text="Sometimes a statement faces the wrong way. For example, R is greater than Q can be rewritten as Q is "
                 "less than R. Flip it, reversing the sign, so that it attaches to the chain.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "rewritten")
        self.play(ReplacementTransform(statements[1], flipped[0]), FadeIn(tags[0], shift=DOWN * 0.1))
        self.at_word(n, "Flip")
        self.play(ReplacementTransform(statements[2], flipped[1]), FadeIn(tags[1], shift=DOWN * 0.1))
        self.wait_for_narration(n)

        # HEAR: the chain.  SEE: the three statements merge into one line.
        n = self.narrate(
            id="build_03",
            text="In this example, P is less than or equal to Q, Q is less than R, and R is less than S. That gives one "
                 "chain: P less than or equal to Q, less than R, less than S.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "gives")
        self.play(TransformFromCopy(statements[0], joined[:3]), TransformFromCopy(flipped[0][1:], joined[3:5]),
                  TransformFromCopy(flipped[1][1:], joined[5:]), run_time=1.4)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_building")

    # ========================================== 4. DIRECTION RULE ==========

    def direction_rule(self):
        self.scene_start("S04_direction", title="Explanation - The Direction Rule")

        rule = self.rule_card("The direction rule", [
            "Between two terms, look at every sign on the path.",
            "All pointing the same way ( > ≥ = or < ≤ = )  →  a relation exists",
            "Signs pointing in opposite directions  →  NO definite relation",
        ], DOWN_C)
        rule.move_to(UP * (CARD_TOP - rule.height / 2))
        body = rule[1]
        legend = VGroup(VGroup(ineq("x > y", size=40), text("one way", SMALL, DOWN_C)).arrange(RIGHT, buff=0.2),
                        VGroup(ineq("x < y", size=40), text("the other way", SMALL, UP_C)).arrange(RIGHT, buff=0.2),
                        VGroup(ineq("x = y", size=40), text("neutral", SMALL, EQ_C)).arrange(RIGHT, buff=0.2))
        legend.arrange(RIGHT, buff=0.8).move_to(DOWN * 0.1)
        self.validator.check_in_frame(VGroup(rule, legend))

        n = self.narrate(
            id="dir_01",
            text="To compare any two terms in the chain, look at every sign on the path between them.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(rule[0]), FadeIn(body[0]), FadeIn(body[1]))
        self.wait_for_narration(n)

        n = self.narrate(
            id="dir_02",
            text="If all the signs point the same way, for example all greater-than or greater-than-or-equal, with equals "
                 "signs allowed anywhere, then a definite relation exists.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(body[2], shift=RIGHT * 0.2))
        self.at_word(n, "equals")
        self.play(LaggedStart(*[FadeIn(l, shift=UP * 0.2) for l in legend], lag_ratio=0.3))
        self.wait_for_narration(n)

        n = self.narrate(
            id="dir_03",
            text="If the path contains signs pointing in opposite directions, such as a greater-than and then a "
                 "less-than, there's no definite relation.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(body[3], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        # HEAR: the opening example: opposite directions -> no relation.
        chain_s = "A > B < C"
        hook = ineq(chain_s, size=80).move_to(DOWN * 1.5)
        box = path_box(hook, 0, 2)
        verdict = self.verdict_for(chain_s, "A", "C").next_to(hook, RIGHT, buff=0.6)
        n = self.narrate(
            id="dir_04",
            text="That's our opening example. A is greater than B, then B is less than C. The signs point in opposite "
                 "directions, so there's no relation between A and C.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(legend), FadeIn(hook, shift=UP * 0.2))
        self.at_word(n, "opposite")
        self.play(Create(box), Indicate(hook[1], color=DOWN_C, scale_factor=1.4),
                  Indicate(hook[3], color=UP_C, scale_factor=1.4))
        self.at_word(n, "no")
        self.play(FadeIn(verdict, scale=1.2))
        self.validator.check_in_frame(VGroup(rule, hook, verdict))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_direction")

    # =========================================== 5. STRENGTH RULE ==========

    def strength_rule(self):
        self.scene_start("S05_strength", title="Explanation - The Strength Rule")

        rule = self.rule_card("The strength rule  (once a relation exists)", [
            "Any strict sign ( > or < ) on the path  →  the result is strict",
            "Only ≥ / ≤ and = on the path  →  the result is ≥ or ≤",
            "Only = on the path  →  the result is =",
        ], GOOD)
        rule.move_to(UP * (CARD_TOP - rule.height / 2))
        body = rule[1]
        self.validator.check_in_frame(rule)

        n = self.narrate(
            id="str_01",
            text="When a relation exists, which sign results? If there's at least one strict sign, greater-than or "
                 "less-than, anywhere on the path, the result is strict.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(rule[0]), FadeIn(body[0]))
        self.at_word(n, "strict", occurrence=1)
        self.play(FadeIn(body[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="str_02",
            text="If the path contains only or equal to signs and equals signs, the result keeps the or equal to. And if "
                 "the path is made only of equals signs, the result is equality.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "keeps")
        self.play(FadeIn(body[2], shift=RIGHT * 0.2))
        self.at_word(n, "equality")
        self.play(FadeIn(body[3], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        # HEAR: A > B ≥ C = D gives A > D.  SEE: the path, the strict sign
        # pulses, the result.
        chain_s = "A > B >= C = D"
        line = ineq(chain_s, size=76).move_to(DOWN * 0.6)
        box = path_box(line, 0, 3)
        verdict = self.verdict_for(chain_s, "A", "D").move_to(DOWN * 2.0)
        n = self.narrate(
            id="str_03",
            text="For example, if A is greater than B, B is greater than or equal to C, and C equals D, then A is greater "
                 "than D. The single strict sign makes the result strict.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(line, shift=UP * 0.2))
        self.at_word(n, "then")
        self.play(Create(box))
        self.play(FadeIn(verdict, scale=1.1))
        self.at_word(n, "single")
        self.play(Indicate(line[1], color=DOWN_C, scale_factor=1.5))
        self.validator.check_in_frame(VGroup(rule, line, verdict))
        self.wait_for_narration(n)

        # HEAR: why: B ≥ D, and A > B, so A > D.
        why = VGroup(ineq("B >= D", size=44), text("and", SMALL, MUTED), ineq("A > B", size=44), text("so", SMALL,
                                                                                                     MUTED),
                     ineq("A > D", size=44)).arrange(RIGHT, buff=0.3).move_to(UP * BOTTOM_Y)
        n = self.narrate(
            id="str_04",
            text="Why? Because B is at least C, and C is D, so B is at least D. A is strictly more than B, so A is "
                 "strictly more than D.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(verdict))
        self.at_word(n, "least", occurrence=2)
        self.play(FadeIn(why[0], shift=UP * 0.1))
        self.at_word(n, "strictly", occurrence=1)
        self.play(FadeIn(why[1:3], shift=UP * 0.1))
        self.at_word(n, "strictly", occurrence=2)
        self.play(FadeIn(why[3:], shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_strength")

    # ================================================ 6. EXAMPLE 1 ==========

    def example_basic(self):
        self.scene_start("S06_example_basic", title="Example 1 - Basic")

        given = VGroup(ineq("P <= Q", size=52), ineq("Q < R", size=52), ineq("S > R", size=52)).arrange(RIGHT, buff=1.0)
        ask = text("Relation between P and S?", LABEL, MUTED)
        card = self.card(VGroup(given, ask).arrange(DOWN, buff=0.3), color=FOCUS)
        card.move_to(UP * (CARD_TOP - card.height / 2))
        flipped = ineq("R < S", size=52).move_to(given[2])
        chain_s = "P <= Q < R < S"
        line = ineq(chain_s, size=76).move_to(DOWN * 0.3)
        box = path_box(line, 0, 3)
        verdict = self.verdict_for(chain_s, "P", "S").move_to(DOWN * 1.9)
        self.validator.check_in_frame(VGroup(card, line, verdict))

        n = self.narrate(
            id="ex1_01",
            text="Given P is less than or equal to Q, Q is less than R, and S is greater than R, what's the relation "
                 "between P and S?",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(card, shift=DOWN * 0.3))
        self.wait_for_narration(n)

        n = self.narrate(
            id="ex1_02",
            text="Flip S greater than R into R less than S, and build the chain: P less than or equal to Q, less than R, "
                 "less than S.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Flip")
        self.play(ReplacementTransform(given[2], flipped))
        self.at_word(n, "build")
        self.play(TransformFromCopy(given[0], line[:3]), TransformFromCopy(given[1][1:], line[3:5]),
                  TransformFromCopy(flipped[1:], line[5:]), run_time=1.3)
        self.wait_for_narration(n)

        n = self.narrate(
            id="ex1_03",
            text="The path from P to S has less-than-or-equal, less-than, less-than. They all point the same way, and "
                 "there's at least one strict sign. So P is less than S.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "path")
        self.play(Create(box))
        self.at_word(n, "same")
        self.play(*[Indicate(line[k], color=UP_C, scale_factor=1.4) for k in (1, 3, 5)])
        self.at_word(n, "So")
        self.play(FadeIn(verdict, scale=1.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_example_basic")

    # ================================================ 7. EXAMPLE 2 ==========

    def example_two(self):
        self.scene_start("S07_example_two", title="Example 2 - Application")

        given = VGroup(ineq("H < I", size=52), ineq("I >= J", size=52), ineq("J = K", size=52)).arrange(RIGHT, buff=1.0)
        ask = text("(a) H and K?     (b) I and K?", LABEL, MUTED)
        card = self.card(VGroup(given, ask).arrange(DOWN, buff=0.3), color=FOCUS)
        card.move_to(UP * (CARD_TOP - card.height / 2))
        chain_s = "H < I >= J = K"
        line = ineq(chain_s, size=76).move_to(DOWN * 0.1)
        box_hk = path_box(line, 0, 3)
        box_ik = path_box(line, 1, 3, color=GOOD)
        v_hk = self.verdict_for(chain_s, "H", "K").move_to(LEFT_ZONE + DOWN * 1.7)
        v_ik = self.verdict_for(chain_s, "I", "K").move_to(RIGHT_ZONE + DOWN * 1.7)
        self.validator.check_in_frame(VGroup(card, line, v_hk, v_ik))

        n = self.narrate(
            id="ex2_01",
            text="Given H is less than I, I is greater than or equal to J, and J equals K, what's the relation between H "
                 "and K? And between I and K?",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(card, shift=DOWN * 0.3))
        self.wait_for_narration(n)

        n = self.narrate(
            id="ex2_02",
            text="The chain is H less than I, greater than or equal to J, equal to K.",
            voice="default",
            subtitle=True,
        )
        self.play(TransformFromCopy(given[0], line[:3]), TransformFromCopy(given[1][1:], line[3:5]),
                  TransformFromCopy(given[2][1:], line[5:]), run_time=1.3)
        self.wait_for_narration(n)

        n = self.narrate(
            id="ex2_03",
            text="From H to K, the path goes less-than, then greater-than-or-equal. The directions are opposite, so "
                 "there's no definite relation.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "path")
        self.play(Create(box_hk))
        self.at_word(n, "opposite")
        self.play(Indicate(line[1], color=UP_C, scale_factor=1.4), Indicate(line[3], color=DOWN_C, scale_factor=1.4))
        self.at_word(n, "no")
        self.play(FadeIn(v_hk, scale=1.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="ex2_04",
            text="From I to K, the path is greater-than-or-equal and then equals. They point the same way, with no strict "
                 "sign, so I is greater than or equal to K.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(box_hk))
        self.at_word(n, "path")
        self.play(Create(box_ik))
        self.at_word(n, "so")
        self.play(FadeIn(v_ik, scale=1.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S07_example_two")

    # ========================================== 8. EXAMPLE 3 (CODED) ==========

    def example_coded(self):
        self.scene_start("S08_example_coded", title="Example 3 - Exam-Oriented")

        coded = VGroup(*[text(f"{a}  {s}  {b}", TITLE, INK, BOLD, t2c={s: TERM})
                         for a, s, b in [("R", "%", "T"), ("T", "#", "V")]],
                       text("V  $  W", TITLE, INK, BOLD)).arrange(RIGHT, buff=0.9)
        coded[2][1].set_color(TERM)
        key = text("%  is  >      #  is  ≥      $  is  <", SMALL, MUTED)
        card = self.card(VGroup(coded, key).arrange(DOWN, buff=0.3), color=TERM)
        card.move_to(UP * (CARD_TOP - card.height / 2))
        chain_s = "R > T >= V < W"
        line = ineq(chain_s, size=76).move_to(DOWN * 0.1)
        box_rv = path_box(line, 0, 2, color=GOOD)
        box_tw = path_box(line, 1, 3)
        v_rv = self.verdict_for(chain_s, "R", "V").move_to(LEFT_ZONE + DOWN * 1.7)
        v_tw = self.verdict_for(chain_s, "W", "T").move_to(RIGHT_ZONE + DOWN * 1.7)
        self.validator.check_in_frame(VGroup(card, line, v_rv, v_tw))

        n = self.narrate(
            id="ex3_01",
            text="Now let's return to the coded statements from the previous topic: R percent T, T hash V, V dollar W. "
                 "Decoded, that's R greater than T, greater than or equal to V, less than W.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(card, shift=DOWN * 0.3))
        self.at_word(n, "Decoded")
        self.play(Write(line), run_time=1.2)
        self.wait_for_narration(n)

        n = self.narrate(
            id="ex3_02",
            text="For R and V, the path is greater-than, then greater-than-or-equal. Same direction, with a strict sign, "
                 "so R is greater than V.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "path")
        self.play(Create(box_rv))
        self.at_word(n, "so")
        self.play(FadeIn(v_rv, scale=1.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="ex3_03",
            text="For W and T, the path from T to W is greater-than-or-equal, then less-than. The directions are opposite, "
                 "so no relation can be established.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(box_rv))
        self.at_word(n, "path")
        self.play(Create(box_tw))
        self.at_word(n, "opposite")
        self.play(Indicate(line[3], color=DOWN_C, scale_factor=1.4), Indicate(line[5], color=UP_C, scale_factor=1.4))
        self.at_word(n, "no")
        self.play(FadeIn(v_tw, scale=1.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S08_example_coded")

    # ======================================== 9. EXAM APPLICATION ==========

    def exam_application(self):
        self.scene_start("S09_exam", title="Exam Application")

        steps = VGroup(*[VGroup(pill(str(i + 1), c, size=SMALL), fitted_text(s, SAFE_W - 2.2, BODY, INK))
                         .arrange(RIGHT, buff=0.3) for i, (s, c) in enumerate([
                             ("Decode", TERM),
                             ("Build one chain (flip statements as needed)", TERM),
                             ("For each conclusion, trace the path between its two terms", FOCUS),
                             ("Direction rule: relation or not?", DOWN_C),
                             ("Strength rule: which sign?", GOOD)])])
        steps.arrange(DOWN, buff=0.22, aligned_edge=LEFT)
        routine = self.card(steps).move_to(UP * 0.7)
        branch = pill("No single straight chain?  Trace only the part linking the two terms", FOCUS, size=SMALL)
        fit_width(branch, SAFE_W).move_to(DOWN * 2.2)
        self.validator.check_in_frame(VGroup(routine, branch))

        n = self.narrate(
            id="exam_01",
            text="In the exam, the routine is: decode, build the chain, then for each conclusion, trace the path between "
                 "its two terms. Apply the direction rule to see whether any relation exists, then the strength rule to "
                 "see exactly which one.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(routine[0]))
        for row, spoken in zip(steps, ["decode", "build", "trace", "direction", "strength"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.45)
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_02",
            text="Sometimes the statements can't form a single straight chain, for example when one term connects to two "
                 "others. In that case, trace only the part that links the two terms in the conclusion.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "trace")
        self.play(FadeIn(branch, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S09_exam")

    # =========================================== 10. COMMON MISTAKE ==========

    def common_mistake(self):
        self.scene_start("S10_mistake", title="Common Mistake")

        card_w = ZONE_W - 0.3
        pairs = [
            (self.verdict_card(False, "A > B < C  →  A > C", card_w),
             self.verdict_card(True, "A > B < C  →  no relation", card_w)),
            (self.verdict_card(False, "A > B ≥ C  →  A ≥ C", card_w),
             self.verdict_card(True, "A > B ≥ C  →  A > C", card_w)),
            (self.verdict_card(False, "R > Q  becomes  Q > R", card_w),
             self.verdict_card(True, "R > Q  becomes  Q < R", card_w)),
        ]
        for (wrong, right), y in zip(pairs, [1.6, 0.05, -1.5]):
            wrong.move_to(LEFT_ZONE + UP * y)
            right.move_to(RIGHT_ZONE + UP * y)
        header = pill("3 mistakes", BAD, size=LABEL).move_to(UP * (CARD_TOP - 0.3))
        self.validator.check_in_frame(VGroup(header, *[c for p in pairs for c in p]))

        n = self.narrate(
            id="mistake_01",
            text="The biggest mistake is combining signs that point in opposite directions. It feels as if something "
                 "should follow, but nothing does.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(header))
        self.at_word(n, "combining")
        self.play(FadeIn(pairs[0][0], shift=RIGHT * 0.3))
        self.at_word(n, "nothing")
        self.play(FadeIn(pairs[0][1], shift=LEFT * 0.3))
        self.wait_for_narration(n)

        n = self.narrate(
            id="mistake_02",
            text="The second mistake is weakening the result: concluding greater-than-or-equal when one strict sign on the "
                 "path makes the result strictly greater.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "weakening")
        self.play(FadeIn(pairs[1][0], shift=RIGHT * 0.3))
        self.at_word(n, "strictly")
        self.play(FadeIn(pairs[1][1], shift=LEFT * 0.3))
        self.wait_for_narration(n)

        n = self.narrate(
            id="mistake_03",
            text="The third is forgetting to flip the sign when a statement is reversed to fit the chain. R is greater "
                 "than Q becomes Q is less than R, not Q is greater than R.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "forgetting")
        self.play(FadeIn(pairs[2][0], shift=RIGHT * 0.3))
        self.at_word(n, "becomes")
        self.play(FadeIn(pairs[2][1], shift=LEFT * 0.3))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S10_mistake")

    # ================================================ 11. PRACTICE ==========

    def practice(self):
        self.scene_start("S11_practice", title="Practice Question")

        given = VGroup(ineq("W > X", size=60), ineq("X = Y", size=60), ineq("Y >= Z", size=60)).arrange(RIGHT, buff=1.0)
        ask = text("Relation between W and Z?", BODY, MUTED)
        board = self.card(VGroup(given, ask).arrange(DOWN, buff=0.4), color=FOCUS).move_to(UP * 0.4)
        self.validator.check_in_frame(board)

        # SILENCE (pause_after): countdown ring while the learner thinks.
        n = self.narrate(
            id="practice_01",
            text="If W is greater than X, X equals Y, and Y is greater than or equal to Z, what's the relation between W "
                 "and Z?",
            voice="default",
            subtitle=True,
            pause_after=8.0,
        )
        self.play(FadeIn(board[0]), LaggedStart(*[FadeIn(g, shift=DOWN * 0.2) for g in given], lag_ratio=0.3))
        self.at_word(n, "relation")
        self.play(FadeIn(ask, shift=UP * 0.1))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        self.clear_stage()
        self.scene_end("S11_practice")

    # ================================================== 12. ANSWER ==========

    def answer(self):
        self.scene_start("S12_answer", title="Answer and Explanation")

        chain_s = "W > X = Y >= Z"
        line = ineq(chain_s, size=80).move_to(UP * 1.2)
        box = path_box(line, 0, 3)
        verdict = self.verdict_for(chain_s, "W", "Z", size=72).move_to(DOWN * 1.1)
        self.validator.check_in_frame(VGroup(line, box, verdict))

        n = self.narrate(
            id="answer_01",
            text="The chain is W greater than X, equal to Y, greater than or equal to Z.",
            voice="default",
            subtitle=True,
        )
        self.play(Write(line), run_time=1.2)
        self.wait_for_narration(n)

        n = self.narrate(
            id="answer_02",
            text="The path from W to Z contains greater-than, equals, and greater-than-or-equal. They all point the same "
                 "way, so a relation exists. There's a strict sign on the path, so the result is strict. W is greater "
                 "than Z.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "path", occurrence=1)
        self.play(Create(box))
        self.at_word(n, "same")
        self.play(Indicate(line[1], color=DOWN_C, scale_factor=1.4), Indicate(line[5], color=DOWN_C, scale_factor=1.4))
        self.at_word(n, "strict", occurrence=1)
        self.play(Indicate(line[1], color=GOOD, scale_factor=1.6))
        self.at_word(n, "W", occurrence=2)
        self.play(FadeIn(verdict, scale=1.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S12_answer")

    # ========================================== 13. QUICK REVISION ==========

    def quick_revision(self):
        self.scene_start("S13_revision", title="Quick Revision")

        card_w, card_h = SAFE_W - 1.0, 4.0
        items = [
            ("Combine only through a common term", TERM),
            ("Flip statements to fit the chain (reverse the sign)", UP_C),
            ("Direction rule: same direction → relation; opposite → none", DOWN_C),
            ("Strength rule: any strict sign → strict; only ≥/≤ and = → ≥/≤; only = → =", GOOD),
        ]
        bullets = VGroup(*[VGroup(Dot(radius=0.07, color=c), fitted_text(s, card_w - 1.4, BODY, c, max_lines=2))
                           .arrange(RIGHT, buff=0.3) for s, c in items]).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        board = self.card(bullets, width=card_w, height=card_h).move_to(DOWN * 0.1)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="revision_01",
            text="To revise: combine statements only through common terms, and flip them as needed to form a chain. If "
                 "the signs on the path point the same way, a relation exists. If they point opposite ways, it doesn't. "
                 "When a relation exists, any strict sign makes the result strict.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(board[0]))
        self.play(FadeIn(bullets[0], shift=RIGHT * 0.2))
        for b, spoken in zip(bullets[1:], ["flip", "signs", "strict"]):
            self.at_word(n, spoken)
            self.play(FadeIn(b, shift=RIGHT * 0.2), run_time=0.5)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S13_revision")

    # ================================================= 14. CLOSING ==========
    # Purpose: teaser for Definite vs Indefinite Conclusions: two conclusions
    # and the five answer choices.

    def closing(self):
        self.scene_start("S14_closing", title="Closing")

        conclusions = VGroup(VGroup(pill("I", FOCUS), ineq("A > C", size=52)).arrange(RIGHT, buff=0.3),
                             VGroup(pill("II", FOCUS), ineq("A = C", size=52)).arrange(RIGHT, buff=0.3))
        conclusions.arrange(RIGHT, buff=1.5).move_to(UP * 1.4)
        choices = VGroup(*[pill(c, MUTED, size=SMALL, fill_opacity=0.06)
                           for c in ["only I", "only II", "both", "neither", "either I or II"]]).arrange(RIGHT, buff=0.3)
        fit_width(choices, SAFE_W).move_to(DOWN * 0.1)
        nxt = pill("Next:  Definite vs Indefinite Conclusions", TERM, size=LABEL).move_to(DOWN * 1.8)
        self.validator.check_in_frame(VGroup(conclusions, choices, nxt))

        n = self.narrate(
            id="closing_01",
            text="Now we can judge any single conclusion. In the final topic of this lesson, we'll deal with the full exam "
                 "format: two conclusions, where the answer may be only one follows, both follow, neither follows, or "
                 "the subtle case of either one or the other follows.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "two")
        self.play(FadeIn(conclusions, shift=DOWN * 0.2))
        self.at_word(n, "only")
        self.play(LaggedStart(*[FadeIn(c, shift=UP * 0.15) for c in choices[:4]], lag_ratio=0.3))
        self.at_word(n, "either")
        self.play(FadeIn(choices[4], scale=1.2), choices[4][0].animate.set_stroke(FOCUS))
        self.play(FadeIn(nxt, scale=1.1))
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S14_closing")

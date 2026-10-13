"""
animation.py for the LMS video generator.

Course : Pre-C-CAT - Section A
Module : Module 1 - Logical Reasoning
Lesson : Lesson 5 - Symbols & Notations (Coded Inequalities)
Topic  : Definite vs Indefinite Conclusions (Topic 3)

Source script:
  C:\\Scripts\\Section A\\Module 1 - Logical Reasoning\\Lesson 05 - Symbols & Notations\\
  Topic 3 - Definite vs Indefinite Conclusions.md

Built on the golden-reference pattern:
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``.

Opening: not the first video of the course, so no spoken course welcome.
The module > lesson > topic trail is shown on screen (silent), followed by a
one-idea recap of Topic 2 (combining) and what this video covers.

Every verdict on screen (follows / doesn't, and the final option) is computed
by ``judge`` from the chain, using the direction + strength rules, so it
always matches the logic.

Section map (script heading -> VISUAL PLAN scene):
  S00 Intro (trail + recap)       -> -
  S01 Opening Hook                -> scene 1
  S02 Concept (five options)      -> scene 2
  S03 Judging each conclusion     -> scene 3
  S04 The "either" case           -> scene 4
  S05-S07 Examples 1-3            -> scene 5
  S08 Exam Application            -> scene 6
  S09 Common Mistake              -> scene 7
  S10-S11 Practice / Answer       -> scene 8
  S12-S13 Revision / Closing      -> scene 9
"""

import math
import re

import numpy as np
from manim import *

from src.animation import LMSScene

# ============================================================== style ====

BG = "#0B1020"
INK = "#E6EAF2"
MUTED = "#8B95A7"
PANEL = "#151C2E"

DOWN_C = "#4FC3F7"     # > and ≥
UP_C = "#FFB74D"       # < and ≤
EQ_C = MUTED           # =
CODED = "#CE93D8"      # coded symbols / "either"
FOCUS = "#FFD54F"      # "look here" / traced path
GOOD = "#66BB6A"       # follows
BAD = "#EF5350"        # does not follow

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
CASES = {">": {">"}, ">=": {">", "="}, "=": {"="}, "<": {"<"}, "<=": {"<", "="}}
ALL = {"<", "=", ">"}
OPTIONS = ["only I follows", "only II follows", "either I or II follows", "neither follows", "both follow"]


def combine(signs):
    """Direction + strength rules (from Topic 2)."""
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


def allowed(chain_s, a, b):
    """The cases (of <, =, >) the chain allows for 'a ? b'."""
    toks = chain_s.split()
    terms, signs = toks[0::2], toks[1::2]
    i, j = terms.index(a), terms.index(b)
    r = combine(signs[min(i, j):max(i, j)])
    if r is None:
        return set(ALL)
    return CASES[FLIP[r] if i > j else r]


def follows(chain_s, conclusion):
    a, rel, b = conclusion.split()
    return allowed(chain_s, a, b) <= CASES[rel]


def judge(chain_s, c1, c2):
    """The standard option for conclusions I and II."""
    f1, f2 = follows(chain_s, c1), follows(chain_s, c2)
    if f1 and f2:
        return "both follow"
    if f1:
        return "only I follows"
    if f2:
        return "only II follows"
    a1, r1, b1 = c1.split()
    a2, r2, b2 = c2.split()
    if {a1, b1} == {a2, b2}:
        s2 = CASES[r2] if (a2, b2) == (a1, b1) else {FLIP[x] if x != "=" else x for x in CASES[r2]}
        if allowed(chain_s, a1, b1) <= (CASES[r1] | s2) and not (CASES[r1] & s2):
            return "either I or II follows"
    return "neither follows"


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
    """A spaced chain "P <= Q < R" as MathTex; signs coloured by direction."""
    toks = s.split()
    line = MathTex(*[SIGN_TEX.get(t, t) for t in toks], font_size=size, color=INK)
    for k, t in enumerate(toks):
        if k % 2 == 1:
            line[k].set_color(SIGN_COLOR[t])
    return line


def path_box(line, chain_s, a, b, color=FOCUS):
    """Mark the part of a chain between terms a and b with a bar under it.

    A bar, not a SurroundingRectangle: the validator treats a rectangle drawn
    around part of a MathTex as a box that must contain the WHOLE formula, so
    partial paths (e.g. N..P in M >= N > O = P) were reported as overflowing.
    """
    terms = chain_s.split()[0::2]
    i, j = sorted((terms.index(a), terms.index(b)))
    seg = line[2 * i:2 * j + 1]
    y = line.get_bottom()[1] - 0.18                  # same height for every path
    return Line([seg.get_left()[0] - 0.08, y, 0], [seg.get_right()[0] + 0.08, y, 0],
                color=color, stroke_width=10)


def coded_line(s, size=TITLE):
    """A coded statement such as 'F # G' with the symbol coloured."""
    sym = s.split()[1]
    return text("  ".join(s.split()), size, INK, BOLD, t2c={re.escape(sym): CODED})


class CaseStrip(VGroup):
    """Three cells  < | = | >  (as in Topic 1)."""

    ORDER = ["<", "=", ">"]

    def __init__(self, w=1.6, h=1.0):
        super().__init__()
        self.cells = VGroup()
        for sym in self.ORDER:
            box = RoundedRectangle(corner_radius=0.14, width=w, height=h, stroke_color=MUTED, stroke_width=3,
                                   fill_color=PANEL, fill_opacity=1)
            self.cells.add(VGroup(box, MathTex(sym, font_size=60, color=INK).move_to(box)))
        self.cells.arrange(RIGHT, buff=0.25)
        self.add(self.cells)

    def cell(self, sym):
        return self.cells[self.ORDER.index(sym)]

    def strike(self, cases):
        return AnimationGroup(*[Create(Cross(self.cell(c), stroke_color=BAD, stroke_width=6, scale_factor=0.7))
                                for c in cases],
                              *[self.cell(c)[0].animate.set_fill(BAD, 0.12).set_stroke(BAD) for c in cases])

    def light(self, cases):
        return AnimationGroup(*[self.cell(c)[0].animate.set_fill(GOOD, 0.25).set_stroke(GOOD, 4) for c in cases],
                              *[self.cell(c)[1].animate.set_color(GOOD) for c in cases])


# ============================================================= lesson ====

class DefiniteIndefiniteConclusionsVideo(LMSScene):
    lesson_title = "Definite vs Indefinite Conclusions"

    def construct(self):
        self.camera.background_color = BG

        self.lesson_intro()
        self.hook()
        self.concept()
        self.judging()
        self.either_case()
        self.example_both()
        self.example_only_one()
        self.example_either()
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

    def problem_card(self, statements, conclusions, coded=False):
        """Statements row over a conclusions row, in a card at the top."""
        make = coded_line if coded else (lambda s: ineq(s, size=48))
        st = VGroup(*[make(s) if not coded else coded_line(s, size=LABEL + 6) for s in statements])
        st.arrange(RIGHT, buff=0.8)
        cs = VGroup(*[VGroup(pill(tag, FOCUS, size=SMALL), make(c) if not coded else coded_line(c, size=LABEL + 6))
                      .arrange(RIGHT, buff=0.25) for tag, c in zip(["I", "II"], conclusions)]).arrange(RIGHT, buff=1.2)
        body = VGroup(VGroup(text("Statements", SMALL, MUTED, BOLD), st).arrange(RIGHT, buff=0.4),
                      VGroup(text("Conclusions", SMALL, MUTED, BOLD), cs).arrange(RIGHT, buff=0.4))
        body.arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        c = self.card(body, color=FOCUS)
        fit_width(c, SAFE_W)
        return c.move_to(UP * (CARD_TOP - c.height / 2)), st, cs

    def conclusion_row(self, chain_s, tag, concl, y):
        """'I   A > D   ✓ follows' (or ✗), computed from the chain. Returns (row, mark)."""
        ok = follows(chain_s, concl)
        head = VGroup(pill(tag, FOCUS, size=SMALL), ineq(concl, size=44)).arrange(RIGHT, buff=0.3)
        head.move_to(LEFT * 3.2 + UP * y)
        mark = text("✓ follows" if ok else "✗ does not follow", LABEL, GOOD if ok else BAD, BOLD)
        mark.next_to(head, RIGHT, buff=0.6)
        return head, mark

    def answer_pill(self, chain_s, c1, c2, y=-2.3):
        return pill("Answer:  " + judge(chain_s, c1, c2), GOOD, size=BODY).move_to(UP * y)

    # ========================================= 0. LESSON INTRO ==========
    # Purpose: where we are (silent trail), last time (one idea), today.

    def lesson_intro(self):
        self.scene_start("S00_intro", title="Lesson Introduction")

        crumb = self.breadcrumb("Module 1 · Logical Reasoning", "Lesson 5 · Symbols & Notations", "Topic 3")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        last = pill("Last time", MUTED, size=SMALL)
        tools = VGroup(pill("one chain", CODED, size=LABEL), pill("direction rule", DOWN_C, size=LABEL),
                       pill("strength rule", GOOD, size=LABEL)).arrange(RIGHT, buff=0.5)
        recap = VGroup(last, tools).arrange(DOWN, buff=0.5).move_to(UP * 0.2)
        self.validator.check_in_frame(VGroup(crumb, recap))

        # SEE (silent): the trail.  HEAR: combining in one sentence.
        n = self.narrate(
            id="intro_01",
            text="Last time, you combined inequalities into one chain, and used the direction and strength rules to find "
                 "the relation between two terms.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.play(FadeIn(last))
        for tag, spoken in zip(tools, ["chain", "direction", "strength"]):
            self.at_word(n, spoken)
            self.play(FadeIn(tag, shift=UP * 0.2), run_time=0.4)
        self.wait_for_narration(n)

        # HEAR: today, the full exam format.  SEE: the title.
        title = fitted_text("Definite vs Indefinite Conclusions", SAFE_W, 60, INK, BOLD)
        underline = Line(LEFT, RIGHT, color=CODED, stroke_width=5).set_width(title.width * 0.6)
        VGroup(title, underline).arrange(DOWN, buff=0.2).move_to(UP * 0.2)
        n = self.narrate(
            id="intro_02",
            text="In this video, we tackle the full exam format: two conclusions, and five possible answers.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(recap, shift=UP * 0.3))
        self.at_word(n, "format")
        self.play(Write(title), run_time=1.1)
        self.play(GrowFromCenter(underline))
        self.wait_for_narration(n)

        # HEAR: the three objectives.  SEE: one row per objective, on its word.
        goals = [
            ("Decide whether each conclusion is definitely true", GOOD),
            ("Choose the right standard option", FOCUS),
            ("Spot when “either I or II” follows", CODED),
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
            text="By the end of this video, you'll be able to decide whether each conclusion is definitely true, choose "
                 "the right standard option, and spot when either one or the other follows.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(underline), ReplacementTransform(title, small_title), run_time=0.8)
        self.play(FadeIn(objectives[0]), FadeIn(heading))
        for row, spoken in zip(rows, ["decide", "choose", "either"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.5)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_intro")

    # ================================================= 1. HOOK ==========

    HOOK_CHAIN = "A >= B = C >= D"

    def hook(self):
        self.scene_start("S01_hook", title="Opening Hook")

        card, st, cs = self.problem_card(["A >= B", "B = C", "C >= D"], ["A > D", "A = D"])
        marks = VGroup(*[text("✗", TITLE, BAD, BOLD).next_to(c, DOWN, buff=0.15) for c in cs])
        reasons = VGroup(pill("A might equal D", BAD, size=SMALL), pill("A might be greater than D", BAD, size=SMALL))
        reasons.arrange(RIGHT, buff=1.0).move_to(UP * 0.1)
        together = Brace(cs, DOWN, color=CODED)
        question = VGroup(text("neither?", BODY, BAD, BOLD), text("or…", BODY, MUTED),
                          text("together?", BODY, CODED, BOLD)).arrange(RIGHT, buff=0.4).move_to(DOWN * 1.3)
        self.validator.check_in_frame(VGroup(card, reasons, question))

        n = self.narrate(
            id="hook_01",
            text="Here are three statements: A is greater than or equal to B, B equals C, and C is greater than or equal "
                 "to D. The conclusions are: one, A is greater than D; two, A equals D.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(card[0]), FadeIn(card[1][0][0]))
        self.play(LaggedStart(*[FadeIn(s, shift=DOWN * 0.15) for s in st], lag_ratio=0.4))
        self.at_word(n, "conclusions")
        self.play(FadeIn(card[1][1][0]), LaggedStart(*[FadeIn(c, shift=DOWN * 0.15) for c in cs], lag_ratio=0.4))
        self.wait_for_narration(n)

        # HEAR: neither follows alone.  SEE: a ✗ and a reason for each.
        n = self.narrate(
            id="hook_02",
            text="Does conclusion one follow? No. A might equal D. Does conclusion two follow? No. A might be greater "
                 "than D.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "No", occurrence=1)
        self.play(FadeIn(marks[0], scale=1.3), FadeIn(reasons[0], shift=UP * 0.1))
        self.at_word(n, "No", occurrence=2)
        self.play(FadeIn(marks[1], scale=1.3), FadeIn(reasons[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_03",
            text="So neither follows. Or does it? Something important happens when we look at the two conclusions "
                 "together. This lesson is about that moment.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "neither")
        self.play(FadeIn(question[0]))
        self.at_word(n, "together")
        self.play(FadeIn(question[1:]), GrowFromCenter(together))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S01_hook")

    # ============================================== 2. CONCEPT ==========

    def concept(self):
        self.scene_start("S02_concept", title="Concept Introduction")

        rows = VGroup(*[VGroup(pill(f"({l})", MUTED, size=SMALL), text(o, BODY, INK)).arrange(RIGHT, buff=0.35)
                        for l, o in zip("abcde", ["Only I follows", "Only II follows", "Either I or II follows",
                                                   "Neither I nor II follows", "Both I and II follow"])])
        rows.arrange(DOWN, buff=0.25, aligned_edge=LEFT)
        options = self.card(rows).move_to(UP * 0.5)
        self.validator.check_in_frame(options)

        n = self.narrate(
            id="concept_01",
            text="In the standard exam format, you're given coded statements and two conclusions. You choose from five "
                 "options: only one follows, only two follows, either one or two follows, neither follows, or both follow.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "five")
        self.play(FadeIn(options[0]))
        self.play_with(n, LaggedStart(*[FadeIn(r, shift=RIGHT * 0.2) for r in rows], lag_ratio=0.5), fraction=0.9)
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_02",
            text="A conclusion follows only if it's definitely true in every situation the statements allow. Possibly "
                 "true isn't enough.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "definitely")
        cap = self.caption("Follows = definitely true.   “Possibly true” is not enough.", GOOD)
        self.play(FadeIn(cap, shift=UP * 0.2))
        self.wait_for_narration(n)

        # HEAR: four options judge each conclusion alone; "either" is different.
        n = self.narrate(
            id="concept_03",
            text="Four of the five options depend only on judging each conclusion separately. The fifth, either one or "
                 "two, depends on how the two conclusions relate to each other.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Four")
        self.play(*[Indicate(rows[k], color=FOCUS, scale_factor=1.03) for k in (0, 1, 3, 4)])
        self.at_word(n, "fifth")
        self.play(rows[2][1].animate.set_color(CODED), Circumscribe(rows[2], color=CODED))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_concept")

    # ================================= 3. JUDGING EACH CONCLUSION ==========

    def judging(self):
        self.scene_start("S03_judging", title="Explanation - Judging Each Conclusion")

        flow = VGroup(pill("trace the path", FOCUS, size=LABEL), text("→", LABEL, MUTED),
                      pill("direction rule", DOWN_C, size=LABEL), text("→", LABEL, MUTED),
                      pill("strength rule", GOOD, size=LABEL), text("→", LABEL, MUTED),
                      pill("does it guarantee the claim?", CODED, size=LABEL)).arrange(RIGHT, buff=0.2)
        fit_width(flow, SAFE_W).move_to(UP * 2.3)
        strong = VGroup(text("derived", SMALL, MUTED), ineq("A > D", size=48), MathTex(r"\Rightarrow", font_size=48),
                        ineq("A >= D", size=48), text("✓ weaker claim follows", LABEL, GOOD, BOLD))
        strong.arrange(RIGHT, buff=0.3)
        weak = VGroup(text("derived", SMALL, MUTED), ineq("A >= D", size=48), MathTex(r"\not\Rightarrow", font_size=48),
                      ineq("A > D", size=48), text("✗ equality still possible", LABEL, BAD, BOLD))
        weak.arrange(RIGHT, buff=0.3)
        compare = VGroup(strong, weak).arrange(DOWN, buff=0.6, aligned_edge=LEFT).move_to(DOWN * 0.6)
        fit_width(compare, SAFE_W)
        self.validator.check_in_frame(VGroup(flow, compare))

        n = self.narrate(
            id="judge_01",
            text="For each conclusion, use the tools from the last topic: trace the path, apply the direction rule, then "
                 "the strength rule.",
            voice="default",
            subtitle=True,
        )
        for k, spoken in zip([0, 2, 4], ["trace", "direction", "strength"]):
            self.at_word(n, spoken)
            self.play(FadeIn(flow[k], shift=RIGHT * 0.2), *([FadeIn(flow[k - 1])] if k else []), run_time=0.45)
        self.wait_for_narration(n)

        n = self.narrate(
            id="judge_02",
            text="Then compare what you've derived with what the conclusion claims. The conclusion follows only if your "
                 "result guarantees it.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "guarantees")
        self.play(FadeIn(flow[5:], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="judge_03",
            text="For example, if you derive A is greater than D, then A is greater than or equal to D also follows, "
                 "because it's a weaker claim. But if you derive only A is greater than or equal to D, then A is greater "
                 "than D does not follow, because equality is still possible.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "weaker")
        self.play(FadeIn(strong, shift=RIGHT * 0.2))
        self.at_word(n, "possible")
        self.play(FadeIn(weak, shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_judging")

    # ======================================== 4. THE "EITHER" CASE ==========

    def either_case(self):
        self.scene_start("S04_either", title="Explanation - The Either Case")

        rows = VGroup(*[VGroup(pill(str(i + 1), CODED, size=SMALL), fitted_text(s, SAFE_W - 2.2, BODY, INK))
                        .arrange(RIGHT, buff=0.3) for i, s in enumerate([
                            "Neither I nor II follows on its own",
                            "Both conclusions compare the SAME two terms",
                            "Together they cover every possibility the statements allow"])])
        rows.arrange(DOWN, buff=0.22, aligned_edge=LEFT)
        head = text("“Either I or II” needs ALL THREE", LABEL, CODED, BOLD)
        conditions = self.card(VGroup(head, rows).arrange(DOWN, buff=0.25, aligned_edge=LEFT), color=CODED)
        conditions.move_to(UP * (CARD_TOP - conditions.height / 2))
        self.validator.check_in_frame(conditions)

        n = self.narrate(
            id="either_01",
            text="Either one or two requires three conditions.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(conditions[0]), FadeIn(head))
        self.wait_for_narration(n)

        n = self.narrate(
            id="either_02",
            text="First, neither conclusion follows on its own.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="either_03",
            text="Second, both conclusions are about the same two terms.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="either_04",
            text="Third, together they cover every case the statements allow, so one of them must be true, even if we "
                 "don't know which.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(rows[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        # HEAR: the opening example: A ≥ D allows > and =; I covers >, II covers =.
        # SEE: the case strip; < struck; = and > lit; I and II tags on them.
        strip = CaseStrip().move_to(DOWN * 0.9)
        pair = ineq("A >= D", size=52).next_to(strip, LEFT, buff=0.8)
        tag1 = pill("I:  A > D", FOCUS, size=SMALL).next_to(strip.cell(">"), DOWN, buff=0.25)
        tag2 = pill("II:  A = D", FOCUS, size=SMALL).next_to(strip.cell("="), DOWN, buff=0.25)
        n = self.narrate(
            id="either_05",
            text="Now let's return to the opening example. The statements give A is greater than or equal to D, so A is "
                 "either greater than D or equal to D. Conclusion one covers greater than, and conclusion two covers "
                 "equal to. Neither is certain alone, but together they cover every possibility.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(strip), FadeIn(pair))
        self.at_word(n, "either")
        self.play(strip.strike(["<"]), strip.light(sorted(allowed(self.HOOK_CHAIN, "A", "D"))))
        self.at_word(n, "covers", occurrence=1)
        self.play(FadeIn(tag1, shift=UP * 0.1))
        self.at_word(n, "covers", occurrence=2)
        self.play(FadeIn(tag2, shift=UP * 0.1))
        self.at_word(n, "together")
        self.play(Circumscribe(VGroup(strip.cell("="), strip.cell(">"), tag1, tag2), color=CODED))
        self.validator.check_in_frame(VGroup(conditions, pair, strip, tag1))
        self.wait_for_narration(n)

        answer = self.answer_pill(self.HOOK_CHAIN, "A > D", "A = D", y=BOTTOM_Y)
        n = self.narrate(
            id="either_06",
            text="So the answer is either one or two follows.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(answer, scale=1.1))
        self.wait_for_narration(n)

        # HEAR: the common complementary pairs.  SEE: four pair tags.
        self.play(FadeOut(VGroup(conditions, strip, pair, tag1, tag2, answer)))
        pairs = VGroup(
            VGroup(ineq("x > y", size=44), text("with", SMALL, MUTED), ineq("x <= y", size=44)).arrange(RIGHT, buff=0.3),
            VGroup(ineq("x < y", size=44), text("with", SMALL, MUTED), ineq("x >= y", size=44)).arrange(RIGHT, buff=0.3),
            VGroup(ineq("x > y", size=44), text("with", SMALL, MUTED), ineq("x = y", size=44),
                   text("if  x ≥ y  is known", SMALL, CODED)).arrange(RIGHT, buff=0.3),
            VGroup(ineq("x < y", size=44), text("with", SMALL, MUTED), ineq("x = y", size=44),
                   text("if  x ≤ y  is known", SMALL, CODED)).arrange(RIGHT, buff=0.3),
        ).arrange(DOWN, buff=0.35, aligned_edge=LEFT)
        pair_card = self.card(VGroup(text("Complementary pairs", LABEL, CODED, BOLD), pairs)
                              .arrange(DOWN, buff=0.3, aligned_edge=LEFT), color=CODED).move_to(UP * 0.2)
        self.validator.check_in_frame(pair_card)
        n = self.narrate(
            id="either_07",
            text="The most common complementary pairs are: greater-than with less-than-or-equal, and less-than with "
                 "greater-than-or-equal. These cover all three cases on their own. The other pairs are greater-than with "
                 "equals, which works when greater-than-or-equal is known, and less-than with equals, which works when "
                 "less-than-or-equal is known.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(pair_card[0]), FadeIn(pair_card[1][0]))
        self.at_word(n, "most")
        self.play(FadeIn(pairs[0], shift=RIGHT * 0.2), FadeIn(pairs[1], shift=RIGHT * 0.2))
        self.at_word(n, "other")
        self.play(FadeIn(pairs[2], shift=RIGHT * 0.2))
        self.at_word(n, "works", occurrence=2)
        self.play(FadeIn(pairs[3], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_either")

    # ================================ 5. EXAMPLE 1: BOTH FOLLOW ==========

    def example_both(self):
        self.scene_start("S05_example_both", title="Example 1 - Both Follow")

        chain_s, c1, c2 = "M >= N > O = P", "M > P", "N >= P"
        card, st, cs = self.problem_card(["M >= N", "N > O", "O = P"], [c1, c2])
        line = ineq(chain_s, size=72).move_to(UP * 0.3)
        row1, mark1 = self.conclusion_row(chain_s, "I", c1, -0.9)
        row2, mark2 = self.conclusion_row(chain_s, "II", c2, -1.6)
        answer = self.answer_pill(chain_s, c1, c2, y=-2.6)
        self.validator.check_in_frame(VGroup(card, line, row1, mark2, answer))

        n = self.narrate(
            id="ex1_01",
            text="Statements: M is greater than or equal to N, N is greater than O, and O equals P. Conclusions: one, M is "
                 "greater than P; two, N is greater than or equal to P.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(card, shift=DOWN * 0.3))
        self.wait_for_narration(n)

        n = self.narrate(
            id="ex1_02",
            text="The chain is M greater than or equal to N, greater than O, equal to P.",
            voice="default",
            subtitle=True,
        )
        self.play(Write(line), run_time=1.2)
        self.wait_for_narration(n)

        n = self.narrate(
            id="ex1_03",
            text="From M to P, the signs all point the same way, and there's a strict sign, so M is greater than P. "
                 "Conclusion one follows.",
            voice="default",
            subtitle=True,
        )
        box = path_box(line, chain_s, "M", "P")
        self.play(Create(box), FadeIn(row1))
        self.at_word(n, "follows")
        self.play(FadeIn(mark1, scale=1.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="ex1_04",
            text="From N to P, the path is greater-than, then equals, so N is greater than P. That guarantees N is greater "
                 "than or equal to P. Conclusion two follows too.",
            voice="default",
            subtitle=True,
        )
        box2 = path_box(line, chain_s, "N", "P")
        self.play(ReplacementTransform(box, box2), FadeIn(row2))
        self.at_word(n, "too")
        self.play(FadeIn(mark2, scale=1.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="ex1_05",
            text="The answer is both follow.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(answer, scale=1.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_example_both")

    # ================================ 6. EXAMPLE 2: ONLY ONE FOLLOWS ==========

    def example_only_one(self):
        self.scene_start("S06_example_only", title="Example 2 - Only One Follows")

        chain_s, c1, c2 = "F >= G > H <= K", "F > H", "K > G"
        card, st, cs = self.problem_card(["F # G", "G % H", "H @ K"], ["F % H", "K % G"], coded=True)
        key = text("#  is  ≥      %  is  >      @  is  ≤", SMALL, MUTED).next_to(card, DOWN, buff=0.15)
        line = ineq(chain_s, size=68).move_to(UP * 0.1)
        row1, mark1 = self.conclusion_row(chain_s, "I", c1, -1.0)
        row2, mark2 = self.conclusion_row(chain_s, "II", c2, -1.7)
        diff = pill("different pairs of terms  →  “either” is impossible", CODED, size=SMALL).move_to(DOWN * 2.45)
        answer = self.answer_pill(chain_s, c1, c2, y=BOTTOM_Y - 0.05)
        self.validator.check_in_frame(VGroup(card, key, line, row1, mark2, diff))

        n = self.narrate(
            id="ex2_01",
            text="Coded statements: F hash G, G percent H, H at K. Conclusions: one, F percent H; two, K percent G.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(card, shift=DOWN * 0.3), FadeIn(key))
        self.wait_for_narration(n)

        n = self.narrate(
            id="ex2_02",
            text="Decode everything. The chain is F greater than or equal to G, greater than H, less than or equal to K. "
                 "Conclusion one says F is greater than H. Conclusion two says K is greater than G.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "chain")
        self.play(Write(line), run_time=1.2)
        self.at_word(n, "Conclusion", occurrence=1)
        self.play(FadeIn(row1, shift=RIGHT * 0.2))
        self.at_word(n, "Conclusion", occurrence=2)
        self.play(FadeIn(row2, shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="ex2_03",
            text="From F to H, the path is greater-than-or-equal, then greater-than. It's the same direction and strict, "
                 "so F is greater than H. Conclusion one follows.",
            voice="default",
            subtitle=True,
        )
        box = path_box(line, chain_s, "F", "H", color=GOOD)
        self.at_word(n, "path")
        self.play(Create(box))
        self.at_word(n, "follows")
        self.play(FadeIn(mark1, scale=1.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="ex2_04",
            text="From G to K, the path is greater-than, then less-than-or-equal. Those are opposite directions, so "
                 "there's no relation. Conclusion two doesn't follow.",
            voice="default",
            subtitle=True,
        )
        box2 = path_box(line, chain_s, "G", "K", color=BAD)
        self.at_word(n, "path")
        self.play(ReplacementTransform(box, box2))
        self.at_word(n, "opposite")
        self.play(Indicate(line[3], color=DOWN_C, scale_factor=1.4), Indicate(line[5], color=UP_C, scale_factor=1.4))
        self.at_word(n, "doesn't")
        self.play(FadeIn(mark2, scale=1.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="ex2_05",
            text="The two conclusions compare different pairs of terms, so either is impossible. The answer is only one "
                 "follows.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "different")
        self.play(FadeIn(diff, shift=UP * 0.1))
        self.at_word(n, "answer")
        self.play(FadeOut(diff), FadeIn(answer, scale=1.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_example_only")

    # ================================ 7. EXAMPLE 3: SPOTTING "EITHER" ==========

    def example_either(self):
        self.scene_start("S07_example_either", title="Example 3 - Spotting Either")

        chain_s, c1, c2 = "T <= U = V < W", "V = T", "V > T"
        card, st, cs = self.problem_card(["T @ U", "U & V", "V $ W"], ["V & T", "V % T"], coded=True)
        key = text("@  is  ≤      &  is  =      $  is  <      %  is  >", SMALL, MUTED).next_to(card, DOWN, buff=0.15)
        line = ineq(chain_s, size=68).move_to(UP * 0.2)
        derived = VGroup(ineq("T <= V", size=48), text("so", SMALL, MUTED), ineq("V >= T", size=48))
        derived.arrange(RIGHT, buff=0.3).move_to(LEFT_ZONE + DOWN * 1.1)
        strip = CaseStrip(w=1.2, h=0.8).move_to(RIGHT_ZONE + DOWN * 1.1)
        t1 = pill("II", FOCUS, size=SMALL).next_to(strip.cell(">"), DOWN, buff=0.15)
        t2 = pill("I", FOCUS, size=SMALL).next_to(strip.cell("="), DOWN, buff=0.15)
        answer = self.answer_pill(chain_s, c1, c2, y=BOTTOM_Y - 0.05)
        self.validator.check_in_frame(VGroup(card, key, line, derived, strip, t1, answer))

        n = self.narrate(
            id="ex3_01",
            text="Coded statements: T at U, U ampersand V, V dollar W. Conclusions: one, V ampersand T; two, V percent T.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(card, shift=DOWN * 0.3), FadeIn(key))
        self.wait_for_narration(n)

        n = self.narrate(
            id="ex3_02",
            text="Decoded, the chain is T less than or equal to U, equal to V, less than W. Conclusion one says V equals T. "
                 "Conclusion two says V is greater than T.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "chain")
        self.play(Write(line), run_time=1.2)
        self.wait_for_narration(n)

        # HEAR: T ≤ V, i.e. V ≥ T: V = T or V > T.  SEE: path box; derived
        # relation; the strip with = and > lit, tagged I and II.
        n = self.narrate(
            id="ex3_03",
            text="From T to V, the path gives T is less than or equal to V. In other words, V is greater than or equal to "
                 "T. So V equals T, or V is greater than T.",
            voice="default",
            subtitle=True,
        )
        box = path_box(line, chain_s, "T", "V")
        self.at_word(n, "path")
        self.play(Create(box), FadeIn(derived[0], shift=UP * 0.1))
        self.at_word(n, "words")
        self.play(FadeIn(derived[1:], shift=UP * 0.1))
        self.at_word(n, "So")
        self.play(FadeIn(strip), strip.strike(["<"]), strip.light(sorted(allowed(chain_s, "V", "T"))))
        self.play(FadeIn(t2, shift=UP * 0.1), FadeIn(t1, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="ex3_04",
            text="Neither conclusion is certain alone. Both involve the same terms, V and T, and together they cover both "
                 "allowed cases.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "same")
        self.play(Indicate(cs, color=CODED, scale_factor=1.05))
        self.at_word(n, "together")
        self.play(Circumscribe(VGroup(strip.cell("="), strip.cell(">")), color=CODED))
        self.wait_for_narration(n)

        n = self.narrate(
            id="ex3_05",
            text="The answer is either one or two follows.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(answer, scale=1.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S07_example_either")

    # ======================================== 8. EXAM APPLICATION ==========

    def exam_application(self):
        self.scene_start("S08_exam", title="Exam Application")

        judge_row = VGroup(pill("judge I", FOCUS, size=LABEL), text("→", LABEL, MUTED), pill("judge II", FOCUS,
                                                                                          size=LABEL))
        judge_row.arrange(RIGHT, buff=0.3).move_to(UP * 2.3)
        outcomes = VGroup(
            VGroup(pill("both follow", GOOD, size=SMALL), text("→  (e) both", SMALL, INK)).arrange(RIGHT, buff=0.3),
            VGroup(pill("one follows", GOOD, size=SMALL), text("→  (a) or (b)", SMALL, INK)).arrange(RIGHT, buff=0.3),
            VGroup(pill("neither follows", BAD, size=SMALL),
                   text("→  same two terms, complementary?  yes: (c) either   ·   no: (d) neither", SMALL, INK))
            .arrange(RIGHT, buff=0.3),
        ).arrange(DOWN, buff=0.35, aligned_edge=LEFT)
        fit_width(outcomes, SAFE_W).move_to(UP * 0.2)
        warn = pill("Most marks are lost by stopping at “neither” one step too early", BAD, size=SMALL)
        fit_width(warn, SAFE_W).move_to(DOWN * 1.8)
        self.validator.check_in_frame(VGroup(judge_row, outcomes, warn))

        n = self.narrate(
            id="exam_01",
            text="The exam routine: judge conclusion one, then conclusion two.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(judge_row, shift=DOWN * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_02",
            text="If both follow, choose both. If exactly one follows, choose that one. And if neither follows, don't stop "
                 "yet. Check whether they involve the same two terms, and whether they're complementary. If so, the "
                 "answer is either. Otherwise, it's neither.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "both", occurrence=1)
        self.play(FadeIn(outcomes[0], shift=RIGHT * 0.2))
        self.at_word(n, "exactly")
        self.play(FadeIn(outcomes[1], shift=RIGHT * 0.2))
        self.at_word(n, "stop")
        self.play(FadeIn(outcomes[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_03",
            text="The either check only matters when neither conclusion follows. That's where most students lose marks, by "
                 "stopping one step too early.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "lose")
        self.play(FadeIn(warn, scale=1.05))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S08_exam")

    # =========================================== 9. COMMON MISTAKE ==========

    def common_mistake(self):
        self.scene_start("S09_mistake", title="Common Mistake")

        card_w = ZONE_W - 0.3
        pairs = [
            (self.verdict_card(False, "Answer “neither” without checking the pair together", card_w),
             self.verdict_card(True, "Neither alone?  Check for “either”", card_w)),
            (self.verdict_card(False, "“Either” for conclusions about different terms", card_w),
             self.verdict_card(True, "“Either” needs the same two terms", card_w)),
            (self.verdict_card(False, "Accept a conclusion that is only possibly true", card_w),
             self.verdict_card(True, "Equality allowed?  A strict conclusion fails", card_w)),
        ]
        for (wrong, right), y in zip(pairs, [1.6, 0.05, -1.5]):
            wrong.move_to(LEFT_ZONE + UP * y)
            right.move_to(RIGHT_ZONE + UP * y)
        header = pill("3 mistakes", BAD, size=LABEL).move_to(UP * (CARD_TOP - 0.3))
        self.validator.check_in_frame(VGroup(header, *[c for p in pairs for c in p]))

        n = self.narrate(
            id="mistake_01",
            text="The first mistake is choosing neither when the answer is either, because the learner never checks the "
                 "pair together.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(header))
        self.at_word(n, "choosing")
        self.play(FadeIn(pairs[0][0], shift=RIGHT * 0.3))
        self.at_word(n, "together")
        self.play(FadeIn(pairs[0][1], shift=LEFT * 0.3))
        self.wait_for_narration(n)

        n = self.narrate(
            id="mistake_02",
            text="The second is the opposite: choosing either for two conclusions about different terms, just because "
                 "neither follows. Complementary conclusions must describe the same two terms.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "different")
        self.play(FadeIn(pairs[1][0], shift=RIGHT * 0.3))
        self.at_word(n, "Complementary")
        self.play(FadeIn(pairs[1][1], shift=LEFT * 0.3))
        self.wait_for_narration(n)

        n = self.narrate(
            id="mistake_03",
            text="The third is accepting a conclusion that is only possibly true. If equality is allowed, a strict "
                 "conclusion doesn't follow.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "accepting")
        self.play(FadeIn(pairs[2][0], shift=RIGHT * 0.3))
        self.at_word(n, "equality")
        self.play(FadeIn(pairs[2][1], shift=LEFT * 0.3))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S09_mistake")

    # ================================================ 10. PRACTICE ==========

    PRACTICE_CHAIN = "T <= U = V < W"

    def practice(self):
        self.scene_start("S10_practice", title="Practice Question")

        st = VGroup(ineq("T <= U", size=52), ineq("U = V", size=52), ineq("V < W", size=52)).arrange(RIGHT, buff=1.0)
        st_card = self.card(VGroup(text("Statements", SMALL, MUTED, BOLD), st).arrange(RIGHT, buff=0.4), color=FOCUS)
        st_card.move_to(UP * (CARD_TOP - st_card.height / 2))
        q1 = VGroup(pill("Q1", FOCUS), pill("I", MUTED, size=SMALL), ineq("T < W", size=48), pill("II", MUTED, size=SMALL),
                    ineq("T = V", size=48)).arrange(RIGHT, buff=0.35)
        q2 = VGroup(pill("Q2", FOCUS), pill("I", MUTED, size=SMALL), ineq("W > U", size=48), pill("II", MUTED, size=SMALL),
                    ineq("U >= T", size=48)).arrange(RIGHT, buff=0.35)
        qs = VGroup(q1, q2).arrange(DOWN, buff=0.6, aligned_edge=LEFT).move_to(DOWN * 0.6)
        self.validator.check_in_frame(VGroup(st_card, qs))

        n = self.narrate(
            id="practice_01",
            text="Use the statements T is less than or equal to U, U equals V, and V is less than W.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(st_card, shift=DOWN * 0.3))
        self.wait_for_narration(n)

        n = self.narrate(
            id="practice_02",
            text="For question one, the conclusions are: one, T is less than W; two, T equals V.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(q1, shift=UP * 0.2))
        self.wait_for_narration(n)

        # SILENCE (pause_after): countdown ring while the learner thinks.
        n = self.narrate(
            id="practice_03",
            text="For question two, the conclusions are: one, W is greater than U; two, U is greater than or equal to T.",
            voice="default",
            subtitle=True,
            pause_after=8.0,
        )
        self.play(FadeIn(q2, shift=UP * 0.2))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        self.clear_stage()
        self.scene_end("S10_practice")

    # ================================================== 11. ANSWER ==========

    def answer(self):
        self.scene_start("S11_answer", title="Answer and Explanation")

        chain_s = self.PRACTICE_CHAIN
        line = ineq(chain_s, size=72).move_to(UP * 2.3)
        tag_q1 = pill("Q1", FOCUS).move_to(LEFT * 5.8 + UP * 1.0)
        r1, m1 = self.conclusion_row(chain_s, "I", "T < W", 1.0)
        r2, m2 = self.conclusion_row(chain_s, "II", "T = V", 0.3)
        a1 = pill("Q1:  " + judge(chain_s, "T < W", "T = V"), GOOD, size=LABEL).move_to(DOWN * 0.45)
        tag_q2 = pill("Q2", FOCUS).move_to(LEFT * 5.8 + DOWN * 1.2)
        r3, m3 = self.conclusion_row(chain_s, "I", "W > U", -1.2)
        r4, m4 = self.conclusion_row(chain_s, "II", "U >= T", -1.9)
        a2 = pill("Q2:  " + judge(chain_s, "W > U", "U >= T"), GOOD, size=LABEL).move_to(DOWN * 2.7)
        self.validator.check_in_frame(VGroup(line, tag_q1, r1, m1, a1, r4, a2))

        n = self.narrate(
            id="answer_01",
            text="The chain is T less than or equal to U, equal to V, less than W.",
            voice="default",
            subtitle=True,
        )
        self.play(Write(line), run_time=1.2)
        self.wait_for_narration(n)

        n = self.narrate(
            id="answer_02",
            text="For question one: from T to W, the path is less-than-or-equal, equals, less-than. That's the same "
                 "direction with a strict sign, so T is less than W. Conclusion one follows. From T to V, the path gives T "
                 "is less than or equal to V, so T equals V isn't certain. Conclusion two doesn't follow.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(tag_q1), FadeIn(r1))
        box = path_box(line, chain_s, "T", "W")
        self.at_word(n, "path", occurrence=1)
        self.play(Create(box))
        self.at_word(n, "follows")
        self.play(FadeIn(m1, scale=1.2))
        self.at_word(n, "path", occurrence=2)
        box2 = path_box(line, chain_s, "T", "V")
        self.play(ReplacementTransform(box, box2), FadeIn(r2))
        self.at_word(n, "doesn't")
        self.play(FadeIn(m2, scale=1.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answer_03",
            text="The answer is only one follows.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(a1, scale=1.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answer_04",
            text="For question two: from U to W, the path is equals, then less-than, so U is less than W. That means W is "
                 "greater than U, so conclusion one follows. And T is less than or equal to U means U is greater than or "
                 "equal to T, so conclusion two follows.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(tag_q2), FadeIn(r3), FadeOut(box2))
        self.at_word(n, "one")
        self.play(FadeIn(m3, scale=1.2))
        self.at_word(n, "And")
        self.play(FadeIn(r4))
        self.at_word(n, "two", occurrence=2)
        self.play(FadeIn(m4, scale=1.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answer_05",
            text="The answer is both follow.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(a2, scale=1.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S11_answer")

    # ========================================== 12. QUICK REVISION ==========

    def quick_revision(self):
        self.scene_start("S12_revision", title="Quick Revision")

        card_w, card_h = SAFE_W - 1.0, 4.2
        items = [
            ("A conclusion follows only if it is definitely true", GOOD),
            ("A stronger result guarantees a weaker conclusion (> ⇒ ≥), not the reverse", DOWN_C),
            ("“Either” needs: neither alone + same two terms + together they cover all cases", CODED),
            ("If neither follows, always check for “either” before choosing “neither”", FOCUS),
        ]
        bullets = VGroup(*[VGroup(Dot(radius=0.07, color=c), fitted_text(s, card_w - 1.4, BODY, c, max_lines=2))
                           .arrange(RIGHT, buff=0.3) for s, c in items]).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        board = self.card(bullets, width=card_w, height=card_h).move_to(DOWN * 0.1)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="revision_01",
            text="To revise: a conclusion follows only if it's definitely true. A strict result guarantees an or equal to "
                 "conclusion, but not the other way round.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(board[0]))
        self.play(FadeIn(bullets[0], shift=RIGHT * 0.2))
        self.at_word(n, "strict")
        self.play(FadeIn(bullets[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="revision_02",
            text="Either one or two needs all three conditions: neither follows alone, the conclusions concern the same two "
                 "terms, and together they cover every allowed case. And whenever neither follows, check for either "
                 "before you answer.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(bullets[2], shift=RIGHT * 0.2))
        self.at_word(n, "whenever")
        self.play(FadeIn(bullets[3], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S12_revision")

    # ================================================= 13. CLOSING ==========
    # Purpose: Lesson 5 complete; teaser for Number Series.

    def closing(self):
        self.scene_start("S13_closing", title="Closing")

        badge = pill("Symbols & Notations  ✓  complete", GOOD, size=TITLE).move_to(UP * 1.9)
        fit_width(badge, SAFE_W)
        series = VGroup(*[pill(s, DOWN_C if s != "?" else FOCUS, size=TITLE, fill_opacity=0.08)
                          for s in ["2", "5", "10", "17", "?"]]).arrange(RIGHT, buff=0.4).move_to(UP * 0.1)
        nxt = pill("Next lesson:  Number Series", UP_C, size=LABEL).move_to(DOWN * 1.7)
        self.validator.check_in_frame(VGroup(badge, series, nxt))

        n = self.narrate(
            id="closing_01",
            text="That completes Symbols and Notations, and with it the part of the module on relationships and symbols.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "completes")
        self.play(FadeIn(badge, scale=1.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="closing_02",
            text="Next, we move to series and classification, starting with number series. There, the skill shifts from "
                 "reading given rules to discovering hidden ones.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "number")
        self.play(LaggedStart(*[FadeIn(s, shift=UP * 0.2) for s in series], lag_ratio=0.25))
        self.at_word(n, "discovering")
        self.play(Indicate(series[-1], color=FOCUS, scale_factor=1.3), FadeIn(nxt, scale=1.1))
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S13_closing")

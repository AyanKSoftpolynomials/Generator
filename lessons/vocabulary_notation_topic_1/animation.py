"""
animation.py for the LMS video generator.

Course : Pre-C-CAT - Section A
Module : Module 1 - Logical Reasoning
Lesson : Lesson 10 - Blood Relations
Topic  : Vocabulary & Notation (Topic 1)

Source script:
  C:\\Scripts\\Section A\\Module 1 - Logical Reasoning\\Lesson 10 - Blood Relations\\
  Topic 1 - Vocabulary & Notation.md

Built on the golden-reference pattern:
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``.

Opening: first video of a NEW LESSON (not of the course), so no spoken course
welcome. The module > lesson > topic trail is shown on screen (silent), then a
one-line recap of Lesson 9 (definite / either / possible), one line saying
Lesson 10 starts, the topic title and the objectives.

Family model: every answer is checked by a tiny ``Family`` (people with
gender, parents and spouse) whose ``relation`` names how one person is related
to another; the chain is walked with ``mother`` / ``sons`` / ``sisters`` ... and
the result asserted. Tree art: square = male, circle = female, dashed box =
gender not known; double line = married, bar = siblings, vertical = parent to
child.

Section map (script heading -> VISUAL PLAN scene):
  S00 Intro (trail + recap)          -> -
  S01 Opening Hook                   -> scene 1
  S02 Concept                        -> scene 2
  S03 Core vocabulary                -> scene 3
  S04 Family-tree notation           -> scene 4
  S05 Collapsing chained phrases     -> scene 5
  S06-S08 Examples 1-3               -> scene 6
  S09 Exam Application               -> scene 7
  S10 Common Mistake                 -> scene 8
  S11-S12 Practice / Answer          -> scene 9
  S13-S14 Revision / Closing         -> scene 10
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


# ==================================================== series helpers ====

def column_xs(n, spacing, centre=ORIGIN):
    """x positions of ``n`` evenly spaced columns centred on ``centre``."""
    return [centre[0] + (k - (n - 1) / 2) * spacing for k in range(n)]


def tile(label, side=0.85, color=TERM, stroke=MUTED):
    sq = RoundedRectangle(corner_radius=0.12, width=side * 1.25, height=side, stroke_color=stroke,
                          stroke_width=2, fill_color=CELL, fill_opacity=1)
    return VGroup(sq, text(label, int(side * 44), color, BOLD).move_to(sq))


def diffs(values):
    return [b - a for a, b in zip(values, values[1:])]


def signed(d):
    return f"+{d}" if d >= 0 else f"−{-d}"


class Series:
    """A series as tiles, with rows underneath:
       row 1 = differences, at the gaps between terms;
       row 2 = second differences, under the gaps between differences.
    ``values`` may contain None for a blank ("?")."""

    def __init__(self, values, y=1.0, spacing=1.55, side=0.85, centre=ORIGIN):
        self.values = list(values)
        self.xs = column_xs(len(values), spacing, centre)
        self.y, self.side = y, side
        self.tiles = VGroup(*[tile("?" if v is None else str(v), side, FOCUS if v is None else TERM)
                              .move_to(RIGHT * x + UP * y) for v, x in zip(values, self.xs)])

    def gap_x(self, k):
        """x of the gap between term k and term k + 1."""
        return (self.xs[k] + self.xs[k + 1]) / 2

    def diff_pill(self, k, label, color=DIFF):
        return pill(label, color, size=SMALL).move_to(RIGHT * self.gap_x(k) + UP * (self.y - 0.95))

    def diff_row(self, values, start=0, color=DIFF):
        return VGroup(*[self.diff_pill(start + k, signed(d), color) for k, d in enumerate(values)])

    def second_pill(self, k, label, color=SECOND):
        """Under the gap between difference k and difference k + 1 (= under term k + 1)."""
        return pill(label, color, size=SMALL).move_to(RIGHT * self.xs[k + 1] + UP * (self.y - 1.8))

    def second_row(self, values, color=SECOND):
        return VGroup(*[self.second_pill(k, signed(d), color) for k, d in enumerate(values)])

    def value_tile(self, k, value, color=GOOD):
        return tile(str(value), self.side, color, stroke=color).move_to(self.tiles[k])


# ===================================================== family model ====
# A tiny family model used to CHECK every answer in the video: people with a
# gender (M / F / None = unknown), parents and a spouse. ``relation`` names how
# ``target`` is related to ``ego`` for the relations this lesson uses.

class Family:
    def __init__(self):
        self.gender, self.parents, self.spouse_of = {}, {}, {}

    def add(self, name, gender=None, parents=(), spouse=None):
        self.gender[name] = gender
        self.parents[name] = tuple(parents)
        if spouse:
            self.spouse_of[name], self.spouse_of[spouse] = spouse, name
        return name

    def children(self, x):
        return [c for c, ps in self.parents.items() if x in ps]

    def sons(self, x):
        return [c for c in self.children(x) if self.gender[c] == "M"]

    def daughters(self, x):
        return [c for c in self.children(x) if self.gender[c] == "F"]

    def father(self, x):
        return next(p for p in self.parents[x] if self.gender[p] == "M")

    def mother(self, x):
        return next(p for p in self.parents[x] if self.gender[p] == "F")

    def siblings(self, x):
        ps = set(self.parents[x])
        return [s for s, sp in self.parents.items() if s != x and ps and ps & set(sp)]

    def brothers(self, x):
        return [s for s in self.siblings(x) if self.gender[s] == "M"]

    def sisters(self, x):
        return [s for s in self.siblings(x) if self.gender[s] == "F"]

    def spouse(self, x):
        return self.spouse_of.get(x)

    def relation(self, target, ego):
        g = self.gender[target]
        pick = lambda m, f, n=None: m if g == "M" else f if g == "F" else (n or f"{m} / {f}")
        if target in self.parents[ego]:
            return pick("father", "mother", "parent")
        if target in self.children(ego):
            return pick("son", "daughter", "child")
        if target == self.spouse(ego):
            return pick("husband", "wife", "spouse")
        if target in self.siblings(ego):
            return pick("brother", "sister", "sibling")
        aunts_uncles = [s for p in self.parents[ego] for s in self.siblings(p)]
        if any(p in aunts_uncles for p in self.parents[target]):
            return "cousin"
        sp = self.spouse(ego)
        if (sp and target in self.siblings(sp)) or any(target == self.spouse(s) for s in self.siblings(ego)):
            return pick("brother-in-law", "sister-in-law")
        raise ValueError(f"relation of {target} to {ego} not covered")


# ================================================== family-tree art ====

MALE, FEMALE, UNKNOWN = DIFF, "#F48FB1", MUTED


def person(label, gender=None, at=ORIGIN, size=0.55):
    """Square = male, circle = female, dashed rounded box = gender not known.
    The name sits under the symbol."""
    if gender == "M":
        shape = Square(side_length=size, color=MALE, stroke_width=3, fill_color=MALE, fill_opacity=0.15)
    elif gender == "F":
        shape = Circle(radius=size / 2, color=FEMALE, stroke_width=3, fill_color=FEMALE, fill_opacity=0.15)
    else:
        shape = DashedVMobject(RoundedRectangle(corner_radius=0.12, width=size, height=size, color=UNKNOWN,
                                                stroke_width=3), num_dashes=16)
    shape.move_to(at)
    name = text(label, SMALL, INK).next_to(shape, DOWN, buff=0.12)
    return VGroup(shape, name)


def married(a, b, color=INK):
    """Double horizontal line between two people (a on the left)."""
    start, end = a[0].get_right() + RIGHT * 0.05, b[0].get_left() + LEFT * 0.05
    return VGroup(Line(start + UP * 0.05, end + UP * 0.05, color=color, stroke_width=2.5),
                  Line(start + DOWN * 0.05, end + DOWN * 0.05, color=color, stroke_width=2.5))


def siblings_bar(people, color=INK, lift=0.35):
    """Single horizontal line joining siblings above their symbols, with short drops."""
    y = max(p[0].get_top()[1] for p in people) + lift
    xs = [p[0].get_center()[0] for p in people]
    bar = Line(RIGHT * min(xs) + UP * y, RIGHT * max(xs) + UP * y, color=color, stroke_width=2.5)
    drops = [Line(RIGHT * x + UP * y, p[0].get_top(), color=color, stroke_width=2.5) for x, p in zip(xs, people)]
    return VGroup(bar, *drops)


def descent(top_point, bottom_y, color=INK):
    """Vertical parent → child line from ``top_point`` straight down to ``bottom_y``."""
    return Line(top_point, RIGHT * top_point[0] + UP * bottom_y, color=color, stroke_width=2.5)


def chain_chips(parts, color=FOCUS):
    """A possessive chain as chips: ["mother's", "only son's", "daughter"]."""
    return VGroup(*[pill(p, color, size=LABEL) for p in parts]).arrange(RIGHT, buff=0.2)


# ============================================================= lesson ====

class VocabularyNotationVideo(LMSScene):
    lesson_title = "Vocabulary & Notation"

    def construct(self):
        self.camera.background_color = BG

        self.lesson_intro()
        self.hook()
        self.concept()
        self.vocabulary()
        self.notation()
        self.chaining()
        self.example_only_son()
        self.example_cousin()
        self.example_daughter_in_law()
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

    def fill_answer(self, series, k, value):
        """Animation: the '?' tile k becomes the answer (green)."""
        new = series.value_tile(k, value)
        return new, ReplacementTransform(series.tiles[k], new)

    # ========================================= 0. LESSON INTRO ==========
    # Purpose: where we are (silent trail, now Lesson 10), a one-line recap of
    # Lesson 9 (fixed / open / possible), the new lesson, today's topic.

    def lesson_intro(self):
        self.scene_start("S00_intro", title="Lesson Introduction")

        crumb = self.breadcrumb("Module 1 · Logical Reasoning", "Lesson 10 · Blood Relations", "Topic 1")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        last = pill("Last lesson: Syllogism", MUTED, size=SMALL).move_to(UP * 1.8)
        a = Circle(radius=0.8, color=DIFF, fill_opacity=0.12).move_to(LEFT * 0.5 + UP * 0.2)
        b = Circle(radius=0.8, color=RATIO, fill_opacity=0.12).move_to(RIGHT * 0.5 + UP * 0.2)
        tags = VGroup(pill("definite", GOOD, size=SMALL), pill("either", FOCUS, size=SMALL),
                      pill("possibility", SECOND, size=SMALL)).arrange(RIGHT, buff=0.4).move_to(DOWN * 1.3)
        self.validator.check_in_frame(VGroup(crumb, last, a, b, tags))

        # SEE (silent): the trail.  HEAR: Lesson 9 in one sentence.
        n = self.narrate(
            id="intro_01",
            text="In the last lesson, you used Venn diagrams to decide which conclusions are definite, which are either-or, "
                 "and which are only possible.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.play(FadeIn(last))
        self.at_word(n, "Venn")
        self.play(Create(a), Create(b))
        self.at_word(n, "definite")
        self.play(FadeIn(tags[0], shift=UP * 0.1))
        self.at_word(n, "which", occurrence=2)
        self.play(FadeIn(tags[1], shift=UP * 0.1))
        self.at_word(n, "possible")
        self.play(FadeIn(tags[2], shift=UP * 0.1))
        self.wait_for_narration(n)

        # HEAR: Lesson 10 starts; today's topic.  SEE: lesson tag pulses; title.
        title = fitted_text("Vocabulary & Notation", SAFE_W, 72, INK, BOLD)
        underline = Line(LEFT, RIGHT, color=FEMALE, stroke_width=5).set_width(title.width * 0.6)
        VGroup(title, underline).arrange(DOWN, buff=0.2).move_to(UP * 0.2)
        n = self.narrate(
            id="intro_02",
            text="Now we start Lesson Ten, Blood Relations, where you name how people in a family are related. Our first "
                 "topic is the vocabulary and notation you'll need.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Lesson")
        self.play(Indicate(crumb[2], color="#F48FB1", scale_factor=1.1))
        self.at_word(n, "family")
        self.play(FadeOut(VGroup(last, a, b, tags), shift=UP * 0.3))
        self.at_word(n, "first")
        self.play(Write(title), run_time=1.1)
        self.play(GrowFromCenter(underline))
        self.wait_for_narration(n)

        # HEAR: the three objectives.  SEE: one row per objective, on its word.
        goals = [
            ("Name relationships across three generations", MALE),
            ("Draw a family tree with standard notation", FEMALE),
            ("Collapse chained phrases one link at a time", GOOD),
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
            text="By the end of this video, you'll name relationships precisely across three generations, draw a family "
                 "tree with standard notation, and collapse chained phrases one link at a time.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(underline), ReplacementTransform(title, small_title), run_time=0.8)
        self.play(FadeIn(objectives[0]), FadeIn(heading))
        for row_, spoken in zip(rows, ["name", "draw", "collapse"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row_, shift=RIGHT * 0.2), run_time=0.5)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_intro")

    # ================================================= 1. HOOK ==========

    def hook(self):
        self.scene_start("S01_hook", title="Opening Hook")

        f = Family()
        f.add("father", "M")
        f.add("mother", "F", spouse="father")
        f.add("man", "M", ("father", "mother"))
        f.add("wife", "F", spouse="man")
        f.add("girl", "F", ("man", "wife"))
        only_son = f.sons(f.mother("man"))
        assert only_son == ["man"] and f.relation(f.daughters("man")[0], "man") == "daughter"

        chips = chain_chips(["A man's", "mother's", "only son's", "daughter"]).move_to(UP * 1.2)
        q = text("is his — ?", BODY, MUTED).next_to(chips, DOWN, buff=0.35)
        self.validator.check_in_frame(VGroup(chips, q))

        n = self.narrate(
            id="hook_01",
            text="A man's mother's only son's daughter is his what?",
            voice="default",
            subtitle=True,
        )
        self.play_with(n, LaggedStart(*[FadeIn(c, shift=UP * 0.2) for c in chips], lag_ratio=0.3), fraction=0.8)
        self.play(FadeIn(q))
        self.wait_for_narration(n)

        # HEAR: his mother's only son is the man himself.  SEE: two chips collapse.
        himself = pill("the man himself", FOCUS, size=LABEL).move_to(chips[1:3].get_center())
        n = self.narrate(
            id="hook_02",
            text="Read it once more, slowly. His mother's only son. Who is that? If the man is his mother's only son, then "
                 "it's the man himself. So the question is simply asking about the man's own daughter.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "slowly")
        self.play(Indicate(chips[1:3], color=FOCUS, scale_factor=1.08))
        self.at_word(n, "himself")
        self.play(ReplacementTransform(chips[1:3], himself))
        self.at_word(n, "own")
        final = pill("his daughter", GOOD, size=BODY).move_to(chips.get_center())
        self.play(ReplacementTransform(VGroup(chips[0], himself, chips[3]), final))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_03",
            text="Blood-relation questions are full of phrases like this. The skill is to collapse them, one link at a "
                 "time, into a single, familiar relationship.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "collapse")
        cap = self.caption("Collapse the chain, one link at a time", GOOD)
        self.play(FadeIn(cap, shift=UP * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S01_hook")

    # ============================================== 2. CONCEPT ==========

    def build_three_generations(self):
        gf = person("Grandfather", "M", LEFT * 3.4 + UP * 1.9)
        gm = person("Grandmother", "F", LEFT * 1.4 + UP * 1.9)
        uncle = person("Uncle", "M", LEFT * 3.3 + UP * 0.2)
        father = person("Father", "M", LEFT * 1.5 + UP * 0.2)
        mother = person("Mother", "F", LEFT * 0.1 + UP * 0.2)
        me = person("Me", None, LEFT * 1.5 + DOWN * 1.5)
        sister = person("Sister", "F", LEFT * 0.1 + DOWN * 1.5)
        cousin = person("Cousin", None, LEFT * 3.3 + DOWN * 1.5)
        m1 = married(gf, gm)
        bar1 = siblings_bar([uncle, father])
        d1 = descent(m1.get_center(), bar1[0].get_center()[1])
        m2 = married(father, mother)
        bar2 = siblings_bar([me, sister])
        d2 = descent(m2.get_center(), bar2[0].get_center()[1])
        d3 = descent(uncle[1].get_bottom() + DOWN * 0.05, cousin[0].get_top()[1])
        people = VGroup(gf, gm, uncle, father, mother, me, sister, cousin)
        links = VGroup(m1, bar1, d1, m2, bar2, d2, d3)
        return people, links

    def concept(self):
        self.scene_start("S02_concept", title="Concept Introduction")

        people, links = self.build_three_generations()
        gens = VGroup(*[pill(t, c, size=SMALL) for t, c in [("Gen 1: grandparents", MUTED),
                                                           ("Gen 2: parents, aunts, uncles", MUTED),
                                                           ("Gen 3: me, siblings, cousins", FOCUS)]])
        for g, y in zip(gens, [1.9, 0.2, -1.5]):
            g.move_to(RIGHT * 3.4 + UP * y)
        tools = VGroup(pill("vocabulary", GOOD, size=LABEL), pill("notation", MALE, size=LABEL)).arrange(RIGHT, buff=0.5)
        tools.move_to(UP * BOTTOM_Y)
        self.validator.check_in_frame(VGroup(people, links, gens, tools))

        n = self.narrate(
            id="concept_01",
            text="Blood relations questions describe how people are related, and ask you to name the relationship between "
                 "two of them.",
            voice="default",
            subtitle=True,
        )
        self.play(LaggedStart(*[FadeIn(p, scale=0.8) for p in people], lag_ratio=0.1), Create(links), run_time=2.0)
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_02",
            text="Two things make these questions manageable: precise vocabulary, so you know what each relationship word "
                 "means, and a clear notation, so you can draw the family instead of holding it in your head.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "vocabulary")
        self.play(FadeIn(tools[0], shift=UP * 0.1))
        self.at_word(n, "notation")
        self.play(FadeIn(tools[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_03",
            text="A useful organising idea is generation. Grandparents are one generation above parents, and parents are "
                 "one above you. Your siblings and cousins are in your own generation.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Grandparents")
        self.play(FadeIn(gens[0], shift=LEFT * 0.2))
        self.at_word(n, "parents", occurrence=2)
        self.play(FadeIn(gens[1], shift=LEFT * 0.2))
        self.at_word(n, "siblings")
        self.play(FadeIn(gens[2], shift=LEFT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_concept")

    # ============================================ 3. VOCABULARY ==========

    def vocabulary(self):
        self.scene_start("S03_vocabulary", title="Explanation - Core Vocabulary")

        groups = [
            ("Uncles & aunts", MALE, ["father's brother → paternal uncle", "mother's brother → maternal uncle",
                                      "father's / mother's sister → paternal / maternal aunt"]),
            ("Cousins", FOCUS, ["uncle's or aunt's child → cousin (same generation)"]),
            ("Nephews & nieces", GOOD, ["sibling's son → nephew · daughter → niece"]),
            ("In-laws", FEMALE, ["spouse's parent → father- / mother-in-law",
                                 "spouse's brother, or sister's husband → brother-in-law",
                                 "spouse's sister, or brother's wife → sister-in-law"]),
        ]
        blocks = VGroup()
        for head, c, lines in groups:
            blocks.add(VGroup(pill(head, c, size=SMALL),
                              VGroup(*[fitted_text(l, SAFE_W - 3.6, SMALL, INK) for l in lines])
                              .arrange(DOWN, buff=0.1, aligned_edge=LEFT)).arrange(RIGHT, buff=0.35, aligned_edge=UP))
        blocks.arrange(DOWN, buff=0.28, aligned_edge=LEFT)
        board = self.card(blocks, width=SAFE_W - 0.2)
        board.move_to(UP * (CARD_TOP - board.height / 2))
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="vocab_01",
            text="Here's the vocabulary you'll use constantly. Your father's brother is your paternal uncle, and your "
                 "mother's brother is your maternal uncle. The same pattern gives paternal and maternal aunts.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(board[0]))
        self.at_word(n, "father's")
        self.play(FadeIn(blocks[0][0]), FadeIn(blocks[0][1][0], shift=RIGHT * 0.2))
        self.at_word(n, "mother's")
        self.play(FadeIn(blocks[0][1][1], shift=RIGHT * 0.2))
        self.at_word(n, "aunts")
        self.play(FadeIn(blocks[0][1][2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="vocab_02",
            text="The children of your uncles and aunts are your cousins. They're in your generation. Your brother's or "
                 "sister's son is your nephew, and their daughter is your niece.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "cousins")
        self.play(FadeIn(blocks[1], shift=RIGHT * 0.2))
        self.at_word(n, "nephew")
        self.play(FadeIn(blocks[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="vocab_03",
            text="The in-law relations come through marriage. Your spouse's parents are your parents-in-law. Your "
                 "brother-in-law is either your spouse's brother or your sister's husband. Your sister-in-law is your "
                 "spouse's sister, or your brother's wife.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "marriage")
        self.play(FadeIn(blocks[3][0]), FadeIn(blocks[3][1][0], shift=RIGHT * 0.2))
        self.at_word(n, "either")
        self.play(FadeIn(blocks[3][1][1], shift=RIGHT * 0.2))
        self.at_word(n, "spouse's", occurrence=3)
        self.play(FadeIn(blocks[3][1][2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_vocabulary")

    # ============================================== 4. NOTATION ==========

    def notation(self):
        self.scene_start("S04_notation", title="Explanation - Family-Tree Notation")

        m = person("male  (□ or +)", "M")
        fm = person("female  (○ or −)", "F")
        u = person("gender not known", None)
        symbols = VGroup(m, fm, u).arrange(RIGHT, buff=1.3).move_to(UP * 1.7)
        a, b = person("A", "M"), person("B", "F")
        VGroup(a, b).arrange(RIGHT, buff=1.0)
        couple = VGroup(a, b, married(a, b), text("married  (═)", SMALL, MUTED))
        couple[3].next_to(VGroup(a, b), DOWN, buff=0.2)
        c, d = person("C", None), person("D", None)
        VGroup(c, d).arrange(RIGHT, buff=1.0)
        sibs = VGroup(c, d, siblings_bar([c, d]), text("siblings  (—)", SMALL, MUTED))
        sibs[3].next_to(VGroup(c, d), DOWN, buff=0.2)
        p = person("P", None)
        k = person("K", None).next_to(p, DOWN, buff=0.8)
        pc = VGroup(p, k, descent(p[1].get_bottom() + DOWN * 0.05, k[0].get_top()[1]),
                    text("parent → child  ( | )", SMALL, MUTED))
        pc[3].next_to(pc[2], RIGHT, buff=0.25)
        links = VGroup(couple, sibs, pc).arrange(RIGHT, buff=1.2, aligned_edge=DOWN).move_to(DOWN * 0.6)
        fit_width(links, SAFE_W)
        self.validator.check_in_frame(VGroup(symbols, links))

        n = self.narrate(
            id="note_01",
            text="Now the notation. Use a square, or a plus sign, for a male, and a circle, or a minus sign, for a female. "
                 "If the gender isn't known, leave the symbol open, for example as a plain letter.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "square")
        self.play(FadeIn(m, scale=0.8))
        self.at_word(n, "circle")
        self.play(FadeIn(fm, scale=0.8))
        self.at_word(n, "open")
        self.play(FadeIn(u, scale=0.8))
        self.wait_for_narration(n)

        n = self.narrate(
            id="note_02",
            text="A double horizontal line joins a married couple. A single horizontal line joins siblings. A vertical "
                 "line goes down one generation, from parent to child.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "double")
        self.play(FadeIn(couple))
        self.at_word(n, "single")
        self.play(FadeIn(sibs))
        self.at_word(n, "vertical")
        self.play(FadeIn(pc))
        self.wait_for_narration(n)

        n = self.narrate(
            id="note_03",
            text="One important rule: never assume someone's gender from a name. Mark gender only when the statements "
                 "make it clear, for example through words like son, wife or he.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "never")
        cap = self.caption("Never assume gender from a name.  Mark it only when the statements say so.", BAD)
        self.play(FadeIn(cap, shift=UP * 0.2))
        self.at_word(n, "son")
        self.play(Indicate(u, color=FOCUS, scale_factor=1.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_notation")

    # ============================================= 5. CHAINING ==========

    def chaining(self):
        self.scene_start("S05_chaining", title="Explanation - Collapsing Chained Phrases")

        chips = chain_chips(["my mother's", "brother's", "son"]).move_to(UP * 1.0)
        rule = pill("start next to the speaker; replace one link at a time", FOCUS, size=SMALL).move_to(UP * 2.4)
        self.validator.check_in_frame(VGroup(rule, chips))

        n = self.narrate(
            id="chain_01",
            text="To simplify a chain like my mother's brother's son, start next to the speaker and replace one link at a "
                 "time. My mother's brother is my maternal uncle. My maternal uncle's son is my cousin.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(chips, shift=UP * 0.2))
        self.at_word(n, "start")
        self.play(FadeIn(rule, shift=DOWN * 0.1))
        self.at_word(n, "maternal", occurrence=1)
        uncle = pill("my maternal uncle's", MALE, size=LABEL).move_to(chips[0:2].get_center())
        self.play(ReplacementTransform(chips[0:2], uncle))
        self.at_word(n, "cousin")
        final = pill("my cousin", GOOD, size=BODY).move_to(chips.get_center())
        self.play(ReplacementTransform(VGroup(uncle, chips[2]), final))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_chaining")

    # ============================================ 6. EXAMPLE 1 ==========

    def example_only_son(self):
        self.scene_start("S06_example_only_son", title="Example 1 - Basic")

        f = Family()
        f.add("grandpa", "M")
        f.add("mother", "F", spouse="grandpa")
        f.add("man", "M", ("grandpa", "mother"))
        f.add("wife", "F", spouse="man")
        f.add("girl", "F", ("man", "wife"))
        assert f.sons(f.mother("man")) == ["man"] and f.relation("girl", "man") == "daughter"

        mother = person("mother", "F", LEFT * 0.0 + UP * 1.5)
        man = person("man", "M", DOWN * 0.3)
        girl = person("daughter", "F", DOWN * 2.1)
        d1 = descent(mother[1].get_bottom() + DOWN * 0.05, man[0].get_top()[1])
        d2 = descent(man[1].get_bottom() + DOWN * 0.05, girl[0].get_top()[1])
        tree = VGroup(mother, man, girl, d1, d2).move_to(RIGHT * 3.6 + DOWN * 0.2)
        chips = chain_chips(["man's", "mother's", "only son's", "daughter"]).move_to(LEFT * 2.6 + UP * 1.6)
        fit_width(chips, 7.0)
        only = pill("only son  =  the man himself", FOCUS, size=SMALL).next_to(chips, DOWN, buff=0.4)
        answer = pill("his daughter", GOOD, size=BODY).move_to(LEFT * 2.6 + DOWN * 1.2)
        self.validator.check_in_frame(VGroup(tree, chips, only, answer))

        n = self.narrate(
            id="ex1_01",
            text="Let's return to the opening question: a man's mother's only son's daughter.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(chips, shift=UP * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="ex1_02",
            text="His mother's only son is the man himself, since he's male and her only son. So the phrase becomes the "
                 "man's daughter. She's his daughter.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "mother's")
        self.play(FadeIn(mother), Create(d1), FadeIn(man))
        self.at_word(n, "himself")
        self.play(FadeIn(only, shift=UP * 0.1), Indicate(man, color=FOCUS, scale_factor=1.15))
        self.at_word(n, "becomes")
        self.play(Create(d2), FadeIn(girl))
        self.at_word(n, "She's")
        self.play(FadeIn(answer, scale=1.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_example_only_son")

    # ============================================ 7. EXAMPLE 2 ==========

    def example_cousin(self):
        self.scene_start("S07_example_cousin", title="Example 2 - Application")

        f = Family()
        f.add("gp", "M")
        f.add("gm", "F", spouse="gp")
        f.add("mother", "F", ("gp", "gm"))
        f.add("uncle", "M", ("gp", "gm"))
        f.add("dad", "M", spouse="mother")
        f.add("X", None, ("dad", "mother"))
        f.add("aunt", "F", spouse="uncle")
        f.add("son", "M", ("uncle", "aunt"))
        answer_rel = f.relation(f.sons(f.brothers(f.mother("X"))[0])[0], "X")
        assert answer_rel == "cousin"

        mother = person("X's mother", "F", RIGHT * 2.0 + UP * 0.9)
        uncle = person("her brother", "M", RIGHT * 4.6 + UP * 0.9)
        bar = siblings_bar([mother, uncle])
        x = person("X", None, RIGHT * 2.0 + DOWN * 1.2)
        son = person("his son", "M", RIGHT * 4.6 + DOWN * 1.2)
        dx = descent(mother[1].get_bottom() + DOWN * 0.05, x[0].get_top()[1])
        ds = descent(uncle[1].get_bottom() + DOWN * 0.05, son[0].get_top()[1])
        same_gen = DashedLine(x[0].get_right() + RIGHT * 0.1, son[0].get_left() + LEFT * 0.1, color=GOOD)
        chips = chain_chips(["X's mother's", "brother's", "son"]).move_to(LEFT * 3.3 + UP * 1.6)
        fit_width(chips, 6.0)
        answer = pill(answer_rel, GOOD, size=BODY).move_to(LEFT * 3.3 + DOWN * 0.8)
        self.validator.check_in_frame(VGroup(mother, uncle, bar, x, son, chips, answer))

        n = self.narrate(
            id="ex2_01",
            text="X's mother's brother's son is X's what?",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(chips, shift=UP * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="ex2_02",
            text="X's mother's brother is X's maternal uncle. The uncle's son is in X's generation, a child of X's parent's "
                 "sibling. That's X's cousin.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "maternal")
        self.play(FadeIn(mother), FadeIn(uncle), Create(bar))
        self.play(Create(dx), FadeIn(x))
        self.at_word(n, "son")
        self.play(Create(ds), FadeIn(son))
        self.at_word(n, "generation")
        self.play(Create(same_gen))
        self.at_word(n, "cousin")
        self.play(FadeIn(answer, scale=1.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S07_example_cousin")

    # ================================ 8. EXAMPLE 3: ONLY DAUGHTER-IN-LAW ==========

    def example_daughter_in_law(self):
        self.scene_start("S08_example_dil", title="Example 3 - Exam-Oriented")

        f = Family()
        f.add("G", "M")
        f.add("GW", "F", spouse="G")
        f.add("F", "M", ("G", "GW"))
        f.add("W", "F", spouse="F")
        f.add("me", None, ("F", "W"))
        dils = [f.spouse(s) for s in f.sons(f.father(f.father("me"))) if f.spouse(s)]
        assert len(dils) == 1 and f.relation(dils[0], "me") == "mother"

        g = person("grandfather", "M", RIGHT * 1.4 + UP * 1.8)
        gw = person("grandmother", "F", RIGHT * 2.8 + UP * 1.8)
        fa = person("father", "M", RIGHT * 2.1 + UP * 0.1)
        w = person("his wife", "F", RIGHT * 4.3 + UP * 0.1)
        me = person("me", None, RIGHT * 3.2 + DOWN * 1.7)
        m1 = married(g, gw)
        d1 = descent(m1.get_center(), fa[0].get_top()[1])
        m2 = married(fa, w)
        d2 = descent(m2.get_center(), me[0].get_top()[1])
        chips = chain_chips(["my father's", "father's", "only daughter-in-law"]).move_to(LEFT * 3.2 + UP * 1.8)
        fit_width(chips, 6.2)
        steps = VGroup(pill("father's father = grandfather", MUTED, size=SMALL),
                       pill("his daughter-in-law = a son's wife", MUTED, size=SMALL),
                       pill("only one  →  father's wife", FOCUS, size=SMALL)).arrange(DOWN, buff=0.2, aligned_edge=LEFT)
        steps.next_to(chips, DOWN, buff=0.4).align_to(chips, LEFT)
        answer = pill("mother", GOOD, size=BODY).move_to(LEFT * 3.2 + DOWN * 1.9)
        self.validator.check_in_frame(VGroup(g, gw, fa, w, me, chips, steps, answer))

        n = self.narrate(
            id="ex3_01",
            text="My father's father's only daughter-in-law. Who's that?",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(chips, shift=UP * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="ex3_02",
            text="My father's father is my grandfather. His daughter-in-law is the wife of one of his sons. We're told "
                 "there's only one daughter-in-law, and my father is his son, so she must be my father's wife.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "grandfather")
        self.play(FadeIn(g), FadeIn(gw), Create(m1), FadeIn(steps[0], shift=RIGHT * 0.2))
        self.at_word(n, "wife", occurrence=1)
        self.play(Create(d1), FadeIn(fa), FadeIn(steps[1], shift=RIGHT * 0.2))
        self.at_word(n, "only")
        self.play(FadeIn(steps[2], shift=RIGHT * 0.2))
        self.at_word(n, "must")
        self.play(Create(m2), FadeIn(w), Create(d2), FadeIn(me))
        self.wait_for_narration(n)

        n = self.narrate(
            id="ex3_03",
            text="She's my mother.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(answer, scale=1.1), Indicate(w, color=GOOD, scale_factor=1.15))
        self.wait_for_narration(n)

        n = self.narrate(
            id="ex3_04",
            text="Notice that the word only did important work here. Without it, the daughter-in-law could have been the "
                 "wife of an uncle.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "only")
        self.play(Circumscribe(steps[2], color=FOCUS))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S08_example_dil")

    # ======================================== 9. EXAM APPLICATION ==========

    def exam_application(self):
        self.scene_start("S09_exam", title="Exam Application")

        tips = VGroup(*[VGroup(pill(str(i + 1), c, size=SMALL), fitted_text(s_, SAFE_W - 2.2, BODY, INK))
                        .arrange(RIGHT, buff=0.3) for i, (s_, c) in enumerate([
                            ("Draw generations as rows", MUTED),
                            ("Mark genders only when known", FEMALE),
                            ("Collapse the chain step by step", GOOD)])])
        tips.arrange(DOWN, buff=0.28, aligned_edge=LEFT)
        board = self.card(tips).move_to(UP * 1.0)
        only = pill("“only son / only daughter” often points back to the speaker", FOCUS, size=LABEL)
        fit_width(only, SAFE_W).move_to(DOWN * 1.6)
        self.validator.check_in_frame(VGroup(board, only))

        n = self.narrate(
            id="exam_01",
            text="In the exam, even simple one-line questions reward a quick sketch. Draw generations as rows, mark "
                 "genders only when known, and collapse the chain step by step.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(board[0]))
        for r, spoken in zip(tips, ["generations", "genders", "collapse"]):
            self.at_word(n, spoken)
            self.play(FadeIn(r, shift=RIGHT * 0.2), run_time=0.5)
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_02",
            text="Pay special attention to the word only. Only son or only daughter often refers back to the speaker "
                 "themselves, or fixes a single person, which is usually the key to the whole question.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "only", occurrence=1)
        self.play(FadeIn(only, scale=1.05))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S09_exam")

    # =========================================== 10. COMMON MISTAKE ==========

    def common_mistake(self):
        self.scene_start("S10_mistake", title="Common Mistake")

        card_w = ZONE_W - 0.3
        pairs = [
            (self.verdict_card(False, "Gender assumed from a name", card_w),
             self.verdict_card(True, "Gender only from son, wife, he …", card_w)),
            (self.verdict_card(False, "Mother's brother called paternal uncle", card_w),
             self.verdict_card(True, "Mother's side = maternal", card_w)),
            (self.verdict_card(False, "“Only” ignored", card_w),
             self.verdict_card(True, "“My mother's only son” = me (if male)", card_w)),
        ]
        for (wrong, right), yy in zip(pairs, [1.6, 0.05, -1.5]):
            wrong.move_to(LEFT_ZONE + UP * yy)
            right.move_to(RIGHT_ZONE + UP * yy)
        header = pill("3 mistakes", BAD, size=LABEL).move_to(UP * (CARD_TOP - 0.3))
        self.validator.check_in_frame(VGroup(header, *[c for p in pairs for c in p]))

        n = self.narrate(
            id="mistake_01",
            text="The first mistake is assuming gender from names. Exam questions deliberately use names that don't settle "
                 "the matter. If the statements don't fix gender, it isn't known.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(header))
        self.at_word(n, "assuming")
        self.play(FadeIn(pairs[0][0], shift=RIGHT * 0.3))
        self.at_word(n, "fix")
        self.play(FadeIn(pairs[0][1], shift=LEFT * 0.3))
        self.wait_for_narration(n)

        n = self.narrate(
            id="mistake_02",
            text="The second is mixing the paternal and maternal sides, for example calling a mother's brother a paternal "
                 "uncle.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "mixing")
        self.play(FadeIn(pairs[1][0], shift=RIGHT * 0.3))
        self.at_word(n, "calling")
        self.play(FadeIn(pairs[1][1], shift=LEFT * 0.3))
        self.wait_for_narration(n)

        n = self.narrate(
            id="mistake_03",
            text="The third is ignoring only. My mother's only son is the speaker, when the speaker is male. Missing that "
                 "turns a one-step question into a confusing one.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "ignoring")
        self.play(FadeIn(pairs[2][0], shift=RIGHT * 0.3))
        self.at_word(n, "speaker", occurrence=1)
        self.play(FadeIn(pairs[2][1], shift=LEFT * 0.3))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S10_mistake")

    # ================================================ 11. PRACTICE ==========

    def practice(self):
        self.scene_start("S11_practice", title="Practice Question")

        q1 = VGroup(pill("Q1", FOCUS), text("X is a woman.  X's husband's sister is X's — ?", BODY, INK, BOLD))\
            .arrange(RIGHT, buff=0.4)
        q2 = VGroup(pill("Q2", FOCUS), text("Y's father's sister's daughter is Y's — ?", BODY, INK, BOLD))\
            .arrange(RIGHT, buff=0.4)
        qs = VGroup(q1, q2).arrange(DOWN, buff=0.7, aligned_edge=LEFT)
        board = self.card(qs, width=SAFE_W - 0.4, color=FOCUS).move_to(UP * 0.4)
        self.validator.check_in_frame(board)

        # SILENCE (pause_after): countdown ring while the learner thinks.
        n = self.narrate(
            id="practice_01",
            text="Try these two. First, X is a woman. X's husband's sister is X's what? Second, Y's father's sister's "
                 "daughter is Y's what?",
            voice="default",
            subtitle=True,
            pause_after=8.0,
        )
        self.play(FadeIn(board[0]))
        self.at_word(n, "First")
        self.play(FadeIn(q1, shift=UP * 0.2))
        self.at_word(n, "Second")
        self.play(FadeIn(q2, shift=UP * 0.2))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        self.clear_stage()
        self.scene_end("S11_practice")

    # ================================================== 12. ANSWER ==========

    def answer(self):
        self.scene_start("S12_answer", title="Answer and Explanation")

        f1 = Family()
        f1.add("p1", "M")
        f1.add("p2", "F", spouse="p1")
        f1.add("H", "M", ("p1", "p2"))
        f1.add("S", "F", ("p1", "p2"))
        f1.add("X", "F", spouse="H")
        a1 = f1.relation(f1.sisters(f1.spouse("X"))[0], "X")
        f2 = Family()
        f2.add("gp", "M")
        f2.add("gm", "F", spouse="gp")
        f2.add("dad", "M", ("gp", "gm"))
        f2.add("aunt", "F", ("gp", "gm"))
        f2.add("mum", "F", spouse="dad")
        f2.add("Y", None, ("dad", "mum"))
        f2.add("uncle", "M", spouse="aunt")
        f2.add("girl", "F", ("uncle", "aunt"))
        a2 = f2.relation(f2.daughters(f2.sisters(f2.father("Y"))[0])[0], "Y")
        assert (a1, a2) == ("sister-in-law", "cousin")

        c1 = chain_chips(["X's husband's", "sister"]).move_to(UP * 1.8 + LEFT * 2.0)
        r1 = pill(a1, GOOD, size=BODY).next_to(c1, RIGHT, buff=0.8)
        why1 = text("spouse's sister", SMALL, MUTED).next_to(c1, DOWN, buff=0.25)
        c2 = chain_chips(["Y's father's", "sister's", "daughter"]).move_to(DOWN * 0.8 + LEFT * 2.0)
        r2 = pill(a2, GOOD, size=BODY).next_to(c2, RIGHT, buff=0.8)
        why2 = text("paternal aunt's daughter: same generation", SMALL, MUTED).next_to(c2, DOWN, buff=0.25)
        self.validator.check_in_frame(VGroup(c1, r1, why1, c2, r2, why2))

        n = self.narrate(
            id="answer_01",
            text="For the first, a spouse's sister is a sister-in-law.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(c1, shift=UP * 0.2))
        self.at_word(n, "spouse's")
        self.play(FadeIn(why1))
        self.at_word(n, "is", occurrence=1)
        self.play(TransformFromCopy(c1, r1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answer_02",
            text="For the second, Y's father's sister is Y's paternal aunt, and her daughter is in Y's generation. She's "
                 "Y's cousin.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(c2, shift=UP * 0.2))
        self.at_word(n, "paternal")
        self.play(FadeIn(why2))
        self.at_word(n, "cousin")
        self.play(TransformFromCopy(c2, r2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S12_answer")

    # ========================================== 13. QUICK REVISION ==========

    def quick_revision(self):
        self.scene_start("S13_revision", title="Quick Revision")

        card_w, card_h = SAFE_W - 1.0, 5.0
        items = [
            ("Think in generations", MUTED),
            ("Paternal = father's side · Maternal = mother's side", MALE),
            ("In-laws come through marriage", FEMALE),
            ("□/+ male · ○/− female · ═ married · — siblings · | parent→child", INK),
            ("Never assume gender from names", BAD),
            ("“Only” often points back to the speaker", FOCUS),
        ]
        bullets = VGroup(*[VGroup(Dot(radius=0.07, color=c), fitted_text(s_, card_w - 1.4, BODY, c, max_lines=2))
                           .arrange(RIGHT, buff=0.3) for s_, c in items]).arrange(DOWN, buff=0.24, aligned_edge=LEFT)
        board = self.card(bullets, width=card_w, height=card_h).move_to(DOWN * 0.1)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="revision_01",
            text="To revise: think in generations. Keep paternal and maternal sides separate. Remember that in-laws come "
                 "through marriage. Draw with a clear notation, and never assume gender from a name. And watch the word "
                 "only. It often points back to the speaker.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(board[0]))
        self.play(FadeIn(bullets[0], shift=RIGHT * 0.2))
        for b, spoken in zip(bullets[1:], ["paternal", "marriage", "notation", "never", "only"]):
            self.at_word(n, spoken)
            self.play(FadeIn(b, shift=RIGHT * 0.2), run_time=0.5)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S13_revision")

    # ================================================= 14. CLOSING ==========
    # Purpose: teaser for Pointing Relations: a speaker points at a photograph.

    def closing(self):
        self.scene_start("S14_closing", title="Closing")

        speaker = person("speaker", None, LEFT * 2.5 + UP * 0.3, size=0.8)
        frame = RoundedRectangle(corner_radius=0.1, width=1.6, height=1.9, color=FOCUS, stroke_width=3)\
            .move_to(RIGHT * 2.0 + UP * 0.4)
        face = person("?", None, frame.get_center() + UP * 0.1)
        arrow = Arrow(speaker[0].get_right(), frame.get_left(), buff=0.2, color=FOCUS)
        quote = pill("“Pointing to a person, someone said …”", MUTED, size=LABEL).move_to(UP * 2.3)
        nxt = pill("Next:  Pointing Relations", FOCUS, size=BODY).move_to(DOWN * 2.2)
        self.validator.check_in_frame(VGroup(speaker, frame, quote, nxt))

        n = self.narrate(
            id="closing_01",
            text="Next, we'll apply this to the classic question type: pointing to a person, someone said. We'll learn to "
                 "decode the speaker's sentence from the end, back to the speaker.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "classic")
        self.play(FadeIn(quote, shift=DOWN * 0.1))
        self.at_word(n, "pointing")
        self.play(FadeIn(speaker), Create(frame), FadeIn(face), GrowArrow(arrow))
        self.at_word(n, "decode")
        self.play(FadeIn(nxt, scale=1.1))
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S14_closing")

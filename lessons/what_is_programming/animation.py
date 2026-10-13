"""
animation.py for the LMS video generator.

Course : Pre-C-CAT - Section A
Module : Module 1 - Logical Reasoning
Lesson : Lesson 1 - Alphabet Test
Topic  : Alphabet Positions

Source script:
  C:\\Scripts\\Section A\\Module 1 - Logical Reasoning\\Lesson 01 - Alphabet Test\\
  Topic 1 - Alphabet Positions.md

Built on the golden-reference pattern:
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never ``self.wait(seconds)``;
  * one method per section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``,
    labels placed outward from the cell they name (``AlphabetStrip.label``).

Section map (script heading -> VISUAL PLAN scene):
  S01 Opening Hook            -> scene 1
  S02 Concept Introduction    -> scene 2
  S03 EJOTY anchors           -> scene 3
  S04 Sum-27 rule             -> scene 4
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

# Semantic colours: one meaning each, used the same way in every section.
FWD = "#4FC3F7"        # forward position (counted from A)
REV = "#F48FB1"        # reverse position (counted from Z)
ANCHOR = "#FFB74D"     # EJOTY anchors and hop arrows
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
ANCHORS = {"E": 5, "J": 10, "O": 15, "T": 20, "Y": 25}

# ============================================================= layout ====

FRAME_W = config.frame_width
FRAME_H = config.frame_height
SAFE = 0.45                                   # margin kept clear on every side
SAFE_W = FRAME_W - 2 * SAFE
SAFE_H = FRAME_H - 2 * SAFE

ZONE_W = 6.2                                  # width of each half-screen zone
LEFT_ZONE = LEFT * 3.35                       # centre of the left half
RIGHT_ZONE = RIGHT * 3.35                     # centre of the right half
TOP_Y = FRAME_H / 2 - SAFE - 0.9              # first row under the section tag
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
    """Readable text no wider than ``max_width``.

    Order of preference: as written > slightly smaller (to 85 %) > wrapped
    over more lines > wrapped and smaller (never below MIN_FONT). If none of
    that fits, fail loudly.
    """
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
    """MathTex split into ``parts`` (so TransformMatchingTex can match them),
    each part coloured from ``colors`` = {part: colour}."""
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


def keep_in_frame(mob, margin=SAFE):
    """Shrink (if needed) and shift ``mob`` so it lies inside the safe area."""
    fit_within(mob, FRAME_W - 2 * margin, FRAME_H - 2 * margin)
    x_min, x_max = -FRAME_W / 2 + margin, FRAME_W / 2 - margin
    y_min, y_max = -FRAME_H / 2 + margin, FRAME_H / 2 - margin
    dx = max(0, x_min - mob.get_left()[0]) - max(0, mob.get_right()[0] - x_max)
    dy = max(0, y_min - mob.get_bottom()[1]) - max(0, mob.get_top()[1] - y_max)
    return mob.shift(RIGHT * dx + UP * dy)


def math_row(line, row, x=ORIGIN):
    """Put a working line on row ``row`` (0, 1, 2 ...) under the strip."""
    return line.move_to(x + UP * (MATH_Y1 - row * MATH_GAP))


# ==================================================== diagram helpers ====

class AlphabetStrip(VGroup):
    """The 26 letters in a single row of cells, centred on the origin.

    ``cells[i]`` / ``chars[i]`` hold letter ``letters[i]``. Anything attached
    to a letter is placed with ``label`` (outward from its cell), so numbers,
    counts and tags never sit on a letter.
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

    def label(self, ch, mob, side=UP, buff=0.14):
        """Place ``mob`` just outside the cell of ``ch`` (above or below)."""
        return mob.next_to(self.cell(ch), side, buff=buff)

    def number_row(self, reverse=False, side=UP, color=FWD, only=None):
        """Position numbers for every letter (or only the letters in ``only``)."""
        row = VGroup()
        for i, ch in enumerate(self.letters):
            if only is not None and ch not in only:
                continue
            n = len(self.letters) - i if reverse else i + 1
            row.add(self.label(ch, text(str(n), NUM, color), side))
        return row

    def mark(self, ch, color=ANCHOR):
        i = self.idx(ch)
        return AnimationGroup(self.cells[i].animate.set_fill(color, 0.35).set_stroke(color, 3),
                              self.chars[i].animate.set_color(color))

    def unmark(self, ch):
        i = self.idx(ch)
        return AnimationGroup(self.cells[i].animate.set_fill(CELL, 1).set_stroke(MUTED, 1.5),
                              self.chars[i].animate.set_color(INK))

    def hops(self, start, steps, side=DOWN, color=ANCHOR, numbered=True):
        """Curved hop arrows from ``start``, ``steps`` letters right (+) or left (-).

        Returns (arrows, labels). Hop numbers sit on the hops, not on letters:
        "count the hops, not the letters you touch".
        """
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


# ============================================================= lesson ====

class AlphabetPositionsVideo(LMSScene):
    lesson_title = "Alphabet Positions"

    def construct(self):
        self.camera.background_color = BG

        self.lesson_intro()
        self.hook()
        self.concept_intro()
        self.ejoty()
        self.sum_27_rule()
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
        """The on-screen question: one fitted line (or two) in a card under the tag."""
        t = fitted_text(s, SAFE_W - 1.6, BODY, INK, max_lines=2)
        c = self.card(t, color=color)
        return c.move_to(UP * (CARD_TOP - c.height / 2))

    def caption(self, s, color=INK):
        """One-line keyword caption in a fixed-width bar at the bottom of the frame."""
        t = fitted_text(s, SAFE_W - 1.0, BODY, color)
        bar = self.card(t, width=SAFE_W - 0.4, height=t.height + 0.9)
        return bar.move_to(UP * BOTTOM_Y)

    def step_tracker(self, labels):
        tracker = VGroup(*[pill(f"{i + 1}  {label}", MUTED, fill_opacity=0.05)
                           for i, label in enumerate(labels)]).arrange(RIGHT, buff=0.3)
        return fit_width(tracker, SAFE_W).move_to(UP * BOTTOM_Y)

    def focus_step(self, tracker, index):
        """Light step ``index``, mark earlier steps done, dim later ones."""
        anims = []
        for i, (box, label) in enumerate(tracker):
            color = FOCUS if i == index else GOOD if i < index else MUTED
            opacity = 0.2 if i == index else 0.05
            anims += [box.animate.set_stroke(color).set_fill(color, opacity), label.animate.set_color(color)]
        return AnimationGroup(*anims)

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

    def stopwatch(self, centre):
        """A running stopwatch; returns (group, clock). Add an updater to ``clock`` to run it."""
        clock = ValueTracker(0.0)
        face = Circle(radius=0.5, stroke_color=MUTED, stroke_width=3).move_to(centre)
        knob = Rectangle(width=0.16, height=0.1, stroke_width=0, fill_color=MUTED, fill_opacity=1)
        knob.next_to(face, UP, buff=0)
        hand = always_redraw(lambda: Line(
            face.get_center(),
            face.get_center() + 0.42 * np.array([np.sin(clock.get_value() * TAU / 10),
                                                 np.cos(clock.get_value() * TAU / 10), 0.0]),
            color=BAD, stroke_width=4))
        readout = always_redraw(lambda: text(f"{clock.get_value():4.1f} s", SMALL, BAD)
                                .next_to(face, DOWN, buff=0.15))
        return VGroup(face, knob, hand, readout), clock

    # ========================================= 0. LESSON INTRO ==========
    # Purpose: open like a real lesson: where we are in the course, what
    # this topic is, and what the learner will be able to do by the end.

    def lesson_intro(self):
        self.scene_start("S00_intro", title="Lesson Introduction")

        course = text("PRE-C-CAT  ·  SECTION A", SMALL, MUTED, BOLD)
        module = pill("Module 1  ·  Logical Reasoning", FWD, size=LABEL)
        lesson = pill("Lesson 1  ·  Alphabet Test", REV, size=LABEL)
        path = VGroup(module, lesson).arrange(RIGHT, buff=0.4)
        fit_width(path, SAFE_W)
        title = fitted_text("Alphabet Positions", SAFE_W, 72, INK, BOLD)
        underline = Line(LEFT, RIGHT, color=ANCHOR, stroke_width=5).set_width(title.width * 0.6)
        topic = text("Topic 1", SMALL, ANCHOR, BOLD)
        header = VGroup(course, path, topic, title, underline).arrange(DOWN, buff=0.35)
        underline.next_to(title, DOWN, buff=0.2)
        header.move_to(ORIGIN)
        self.validator.check_in_frame(header)

        # HEAR: welcome and where we are.  SEE: course line, then the module
        # and lesson pills on the words that name them.
        n = self.narrate(
            id="intro_01",
            text="Welcome to Pre-C-CAT, Section A. This is Module One, Logical Reasoning, "
                 "and we're starting Lesson One, the Alphabet Test.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(course, shift=DOWN * 0.2))
        self.at_word(n, "Module")
        self.play(FadeIn(module, shift=UP * 0.2))
        self.at_word(n, "Lesson")
        self.play(FadeIn(lesson, shift=UP * 0.2))
        self.wait_for_narration(n)

        # HEAR: today's topic.  SEE: the topic title is written and underlined.
        n = self.narrate(
            id="intro_02",
            text="Our first topic is Alphabet Positions: how to place any letter of the alphabet "
                 "in a couple of seconds, from either end.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Alphabet")
        self.play(FadeIn(topic), Write(title), run_time=1.2)
        self.play(GrowFromCenter(underline))
        self.wait_for_narration(n)

        # HEAR: the four learning objectives.  SEE: the header moves up and one
        # objective row appears on the word that names it.
        goals = [
            ("Find any forward position with five anchors", ANCHOR),
            ("Convert forward ↔ reverse with one rule", FOCUS),
            ("Solve position questions as the exam words them", FWD),
            ("Avoid the off-by-one trap", BAD),
        ]
        rows = VGroup(*[VGroup(pill(str(i + 1), c, size=SMALL), fitted_text(s, SAFE_W - 2.4, BODY, INK))
                        .arrange(RIGHT, buff=0.35) for i, (s, c) in enumerate(goals)])
        rows.arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        heading = text("By the end of this lesson, you will:", LABEL, MUTED, BOLD)
        objectives = self.card(VGroup(heading, rows).arrange(DOWN, buff=0.4, aligned_edge=LEFT))
        small_header = VGroup(path.copy(), title.copy()).arrange(RIGHT, buff=0.5)
        fit_width(small_header, SAFE_W)
        small_header.move_to(UP * (FRAME_H / 2 - SAFE - small_header.height / 2))
        objectives.next_to(small_header, DOWN, buff=0.4)
        self.validator.check_in_frame(VGroup(small_header, objectives))
        n = self.narrate(
            id="intro_03",
            text="By the end of this lesson, you'll be able to find any letter's position using five anchors, "
                 "convert between forward and reverse positions with one simple rule, "
                 "solve position questions the way the exam words them, "
                 "and avoid the off-by-one trap that catches most learners.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(VGroup(course, topic, underline)),
                  ReplacementTransform(VGroup(path, title), small_header), run_time=0.8)
        self.play(FadeIn(objectives[0]), FadeIn(heading))
        for row, spoken in zip(rows, ["anchors", "convert", "solve", "avoid"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.5)
        self.wait_for_narration(n)

        # HEAR: let's begin.  SEE: the objectives fade and the stage clears.
        n = self.narrate(
            id="intro_04",
            text="Let's begin with a question.",
            voice="default",
            subtitle=True,
        )
        self.play(Indicate(objectives[0], color=FOCUS, scale_factor=1.01))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_intro")

    # ================================================= 1. HOOK ==========
    # Purpose: show that counting from Z is slow and error-prone.

    def hook(self):
        self.scene_start("S01_hook", title="Opening Hook")

        question = self.question_card("Which letter is 8th from the right end of the English alphabet?")
        strip = AlphabetStrip().move_to(UP * STRIP_Y)
        watch, clock = self.stopwatch(RIGHT * (FRAME_W / 2 - SAFE - 0.9) + DOWN * 1.5)

        # HEAR: the question.  SEE: the question card; "8th" pulses on "eighth".
        n = self.narrate(
            id="hook_01",
            text="Here's a question that looks almost too simple. "
                 "Which letter is eighth from the right end of the English alphabet?",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(question, shift=DOWN * 0.3))
        self.at_word(n, "eighth")
        self.play(Indicate(question[1], color=FOCUS, scale_factor=1.05))
        self.wait_for_narration(n)

        # HEAR: people count back from Z.  SEE: the strip, a running stopwatch,
        # and a pointer stepping Z, Y, X, W ... with a count under each letter.
        pointer = Triangle(color=ANCHOR, fill_opacity=1).scale(0.13).rotate(PI)
        strip.label("Z", pointer, UP, buff=0.12)
        counts = VGroup(*[strip.label(ch, text(str(k + 1), NUM, REV), DOWN)
                          for k, ch in enumerate("ZYXWVUTS")])
        steps = []
        for k, ch in enumerate("ZYXWVUTS"):
            target = strip.cell(ch).get_top() + UP * (0.12 + pointer.height / 2)
            steps.append(AnimationGroup(pointer.animate.move_to(target), FadeIn(counts[k], scale=0.5)))
        n = self.narrate(
            id="hook_02",
            text="Most people answer it the same way. They start at Z and count backwards "
                 "on their fingers: Z, Y, X, W, and so on.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(strip), FadeIn(watch), run_time=0.8)
        clock.add_updater(lambda m, dt: m.increment_value(2.5 * dt))   # exaggerated: counting is slow
        self.add(clock)
        self.at_word(n, "start")
        self.play(FadeIn(pointer))
        self.play_with(n, Succession(*steps), fraction=0.9)
        self.wait_for_narration(n)

        # HEAR: it's slow and it's easy to lose count.  SEE: the stopwatch stops
        # and pulses red on "seconds"; a red caption names the problem.
        n = self.narrate(
            id="hook_03",
            text="That works, but it's slow, and it's easy to lose count. In a timed reasoning section, "
                 "questions like this appear inside bigger questions. "
                 "You don't want to spend twenty seconds just finding one letter.",
            voice="default",
            subtitle=True,
        )
        cap = self.caption("Slow  ·  easy to lose count", BAD)
        self.at_word(n, "slow")
        clock.clear_updaters()
        self.play(FadeIn(cap, shift=UP * 0.2))
        self.at_word(n, "seconds")
        self.play(Indicate(watch, color=BAD))
        self.wait_for_narration(n)

        # HEAR: the promise.  SEE: the caption turns green.
        n = self.narrate(
            id="hook_04",
            text="By the end of this lesson, you'll answer questions like this in about two seconds, "
                 "without counting at all.",
            voice="default",
            subtitle=True,
        )
        new_cap = self.caption("Goal: about 2 seconds, no counting", GOOD)
        self.at_word(n, "two")
        self.play(FadeTransform(cap, new_cap), FadeOut(VGroup(pointer, counts)), FadeOut(watch))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S01_hook")

    # ========================================= 2. CONCEPT INTRO ==========
    # Purpose: every letter carries two numbers, forward and reverse.

    def concept_intro(self):
        self.scene_start("S02_concept", title="Concept Introduction")

        strip = AlphabetStrip().move_to(UP * STRIP_Y)
        fwd = strip.number_row(color=FWD)
        rev = strip.number_row(reverse=True, side=DOWN, color=REV)

        # HEAR: every letter has a position.  SEE: the strip builds left to
        # right; the keyword "position" appears on the word.
        n = self.narrate(
            id="concept_01",
            text="Every letter of the alphabet has a fixed place in the sequence. "
                 "That place, written as a number, is the letter's position.",
            voice="default",
            subtitle=True,
        )
        build = LaggedStart(*[FadeIn(VGroup(c, t), shift=UP * 0.15) for c, t in zip(strip.cells, strip.chars)],
                            lag_ratio=0.08)
        self.play_with(n, build, fraction=0.5)
        self.at_word(n, "position")
        cap = self.caption("Position = a letter's place, as a number", FOCUS)
        self.play(FadeIn(cap, shift=UP * 0.2))
        self.wait_for_narration(n)

        # HEAR: forward position.  SEE: 1 to 26 appear above, left to right.
        n = self.narrate(
            id="concept_02",
            text="When we count from the left, A is one, B is two, and so on, up to Z at twenty-six. "
                 "This is the forward position.",
            voice="default",
            subtitle=True,
        )
        self.play_with(n, LaggedStart(*[FadeIn(x, shift=DOWN * 0.1) for x in fwd], lag_ratio=0.12), fraction=0.6)
        self.at_word(n, "forward")
        new_cap = self.caption("Forward position: count from A  →", FWD)
        self.play(FadeTransform(cap, new_cap))
        cap = new_cap
        self.wait_for_narration(n)

        # HEAR: reverse position.  SEE: 1 to 26 appear below, right to left.
        n = self.narrate(
            id="concept_03",
            text="We can also count from the right. Then Z is one, Y is two, and A is twenty-six. "
                 "This is the reverse position.",
            voice="default",
            subtitle=True,
        )
        self.play_with(n, LaggedStart(*[FadeIn(x, shift=UP * 0.1) for x in reversed(rev)], lag_ratio=0.12),
                       fraction=0.6)
        self.at_word(n, "reverse")
        new_cap = self.caption("←  Reverse position: count from Z", REV)
        self.play(FadeTransform(cap, new_cap))
        cap = new_cap
        self.wait_for_narration(n)

        # HEAR: two numbers per letter.  SEE: A and Z light up with both numbers.
        n = self.narrate(
            id="concept_04",
            text="So every letter carries two numbers: its position from the left, and its position from the right. "
                 "Almost every alphabet-based reasoning question depends on moving quickly between these two numbers.",
            voice="default",
            subtitle=True,
        )
        new_cap = self.caption("Every letter carries two numbers", FOCUS)
        self.play(FadeTransform(cap, new_cap))
        self.at_word(n, "left")
        self.play(strip.mark("A", FOCUS), Indicate(fwd[0], color=FWD, scale_factor=1.5),
                  Indicate(rev[0], color=REV, scale_factor=1.5))
        self.at_word(n, "right")
        self.play(strip.mark("Z", FOCUS), Indicate(fwd[25], color=FWD, scale_factor=1.5),
                  Indicate(rev[25], color=REV, scale_factor=1.5))
        self.validator.check_in_frame(VGroup(strip, fwd, rev))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_concept")

    # ================================================ 3. EJOTY ==========
    # Purpose: five anchors make any forward position one small step away.

    def ejoty(self):
        self.scene_start("S03_ejoty", title="Explanation - EJOTY")

        word = text("E  J  O  T  Y", 96, ANCHOR, BOLD)
        strip = AlphabetStrip().move_to(UP * STRIP_Y)
        anchor_nums = strip.number_row(color=ANCHOR, only=ANCHORS)

        # HEAR: five anchors.  SEE: EJOTY, large, on the word "anchors".
        n = self.narrate(
            id="ejoty_01",
            text="Memorising twenty-six numbers isn't necessary. You only need five anchors, "
                 "and they spell a nonsense word: EJOTY.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "anchors")
        self.play(Write(word), run_time=1.2)
        self.wait_for_narration(n)

        # HEAR: E five, J ten ...  SEE: each anchor lights up with its number
        # on the word that says it.
        n = self.narrate(
            id="ejoty_02",
            text="E is five, J is ten, O is fifteen, T is twenty, and Y is twenty-five. "
                 "They fall at every multiple of five.",
            voice="default",
            subtitle=True,
        )
        self.play(word.animate.scale(0.5).move_to(UP * (CARD_TOP - 0.4)), FadeIn(strip))
        for k, (ch, spoken) in enumerate(zip("EJOT", ["five", "ten", "fifteen", "twenty"])):
            self.at_word(n, spoken)
            self.play(strip.mark(ch), FadeIn(anchor_nums[k], shift=DOWN * 0.15), run_time=0.5)
        self.play(strip.mark("Y"), FadeIn(anchor_nums[4], shift=DOWN * 0.15), run_time=0.5)
        self.at_word(n, "multiple")
        cap = self.caption("Anchors sit at every multiple of 5", ANCHOR)
        self.play(FadeIn(cap, shift=UP * 0.2))
        self.wait_for_narration(n)

        # HEAR: every letter is at most two steps from an anchor.
        n = self.narrate(
            id="ejoty_03",
            text="Every other letter is at most two steps away from one of these anchors. "
                 "So finding a position means one small addition or subtraction.",
            voice="default",
            subtitle=True,
        )
        new_cap = self.caption("Any letter: at most 2 steps from an anchor", ANCHOR)
        self.play(FadeTransform(cap, new_cap))
        cap = new_cap
        self.wait_for_narration(n)

        # HEAR: R = 15 + 3.  SEE: O pulses, three hops to R, then the sum.
        arcs, hop_nums = strip.hops("O", 3)
        eq_r = math_row(math_line("R", "=", "15", "+", "3", "=", "18",
                                  colors={"R": FWD, "15": ANCHOR, "18": FWD}), 0)
        n = self.narrate(
            id="ejoty_04",
            text="Take R. The nearest anchor is O, at fifteen. R comes three letters after O, so R is eighteen.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(cap), strip.mark("R", FWD))
        self.at_word(n, "nearest")
        self.play(Indicate(strip.cell("O"), color=ANCHOR), Indicate(anchor_nums[2], color=ANCHOR))
        self.at_word(n, "three")
        self.play(LaggedStart(*[AnimationGroup(Create(a), FadeIn(l)) for a, l in zip(arcs, hop_nums)],
                              lag_ratio=0.6))
        self.at_word(n, "eighteen")
        self.play(Write(eq_r))
        self.wait_for_narration(n)

        # HEAR: W = 25 - 2.  SEE: Y pulses, two hops back to W, then the difference.
        arcs_w, hop_nums_w = strip.hops("Y", -2)
        eq_w = math_row(math_line("W", "=", "25", "-", "2", "=", "23",
                                  colors={"W": FWD, "25": ANCHOR, "23": FWD}), 1)
        n = self.narrate(
            id="ejoty_05",
            text="Take W. The nearest anchor is Y, at twenty-five. W is two letters before Y, so W is twenty-three.",
            voice="default",
            subtitle=True,
        )
        self.play(strip.mark("W", FWD))
        self.at_word(n, "nearest")
        self.play(Indicate(strip.cell("Y"), color=ANCHOR), Indicate(anchor_nums[4], color=ANCHOR))
        self.at_word(n, "two")
        self.play(LaggedStart(*[AnimationGroup(Create(a), FadeIn(l)) for a, l in zip(arcs_w, hop_nums_w)],
                              lag_ratio=0.6))
        self.at_word(n, "before")
        self.play(Write(eq_w))
        self.validator.check_in_frame(VGroup(word, strip, eq_r, eq_w))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_ejoty")

    # ============================================= 4. SUM-27 RULE ==========
    # Purpose: derive Forward + Reverse = 27 from the picture, then generalise.

    def sum_27_rule(self):
        self.scene_start("S04_sum27", title="Explanation - Sum-27 Rule")

        question = self.question_card("Reverse position, without counting from Z?")
        strip = AlphabetStrip().move_to(UP * STRIP_Y)
        i = strip.idx("J")
        n_label = strip.label("J", MathTex("n", font_size=40, color=ANCHOR), UP)
        before = Brace(strip.cells[:i], UP, color=FWD)
        before_label = MathTex(r"n-1", r"\text{ letters}", font_size=34, color=FWD).next_to(before, UP, buff=0.1)
        after = Brace(strip.cells[i + 1:], DOWN, color=REV)
        after_label = MathTex(r"26-n", r"\text{ letters}", font_size=34, color=REV).next_to(after, DOWN, buff=0.1)

        # HEAR: the question.  SEE: the question card.
        n = self.narrate(
            id="sum27_01",
            text="Now the more useful idea. How do we get the reverse position without counting from Z?",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(question, shift=DOWN * 0.3))
        self.wait_for_narration(n)

        # HEAR: n - 1 before, 26 - n after.  SEE: the strip, the letter at n,
        # and a brace for each group on the word that names it.
        n = self.narrate(
            id="sum27_02",
            text="Suppose a letter is at forward position n. Then there are n minus one letters before it, "
                 "and twenty-six minus n letters after it.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(question), FadeIn(strip))
        self.play(strip.mark("J"), FadeIn(n_label, shift=DOWN * 0.15))
        self.at_word(n, "before")
        self.play(GrowFromCenter(before), FadeIn(before_label))
        self.at_word(n, "after")
        self.play(GrowFromCenter(after), FadeIn(after_label))
        self.wait_for_narration(n)

        # HEAR: pass the letters after it, land on it: 26 - n + 1 = 27 - n.
        # SEE: a pointer sweeps in from Z, then the derivation, line by line.
        pointer = Triangle(color=REV, fill_opacity=1).scale(0.12)
        strip.label("Z", pointer, UP, buff=0.1)
        land = strip.cell("K").get_top() + UP * (0.1 + pointer.height / 2)
        line1 = math_row(math_line(r"\text{Reverse}", "=", r"(26-n)", r"+1",
                                   colors={r"\text{Reverse}": REV, r"+1": ANCHOR}), 0)
        line2 = math_row(math_line(r"\text{Reverse}", "=", r"27-n",
                                   colors={r"\text{Reverse}": REV, r"27-n": ANCHOR}), 1)
        n = self.narrate(
            id="sum27_03",
            text="Counting from the right, we pass all the letters after it and then land on the letter itself. "
                 "So its reverse position is twenty-six minus n, plus one. That's twenty-seven minus n.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(pointer))
        self.play(pointer.animate.move_to(land), run_time=1.5, rate_func=linear)
        self.at_word(n, "land")
        self.play(FadeOut(pointer), Circumscribe(strip.cell("J"), color=ANCHOR))
        self.at_word(n, "plus")
        self.play(Write(line1))
        self.play_with(n, TransformMatchingTex(line1.copy(), line2), fraction=0.8)
        self.wait_for_narration(n)

        # HEAR: forward + reverse = 27.  SEE: the rule card replaces line 2.
        rule = self.card(math_line(r"\text{Forward}", "+", r"\text{Reverse}", "=", "27",
                                   colors={r"\text{Forward}": FWD, r"\text{Reverse}": REV, "27": ANCHOR}, size=52),
                         color=ANCHOR)
        rule.move_to(UP * (MATH_Y1 - MATH_GAP - 0.25))
        n = self.narrate(
            id="sum27_04",
            text="In other words, for any letter, forward position plus reverse position always equals twenty-seven.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "always")
        self.play(FadeOut(line2), FadeIn(rule, scale=0.9))
        self.wait_for_narration(n)

        # HEAR: the +1 is the letter itself.  SEE: "+1" boxed, the letter circled.
        plus_one = SurroundingRectangle(line1[3], color=ANCHOR, buff=0.08)
        n = self.narrate(
            id="sum27_05",
            text="Notice where the twenty-seven comes from. It's twenty-six letters, plus one, "
                 "because the letter itself is counted from both ends.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "plus")
        self.play(Create(plus_one))
        self.at_word(n, "itself")
        self.play(Circumscribe(strip.cell("J"), color=ANCHOR), Indicate(n_label, color=ANCHOR))
        self.validator.check_in_frame(VGroup(before_label, strip, after_label, line1, rule))
        self.wait_for_narration(n)

        # HEAR: the general rule for any row.  SEE: the general card, and a
        # pill pointing ahead to the Ranking lesson.
        general = self.card(math_line(r"\text{Left}", "+", r"\text{Right}", "=", "N+1",
                                      colors={r"\text{Left}": FWD, r"\text{Right}": REV, "N+1": ANCHOR}, size=52),
                            color=FOCUS)
        general.move_to(rule)
        ahead = pill("Ranking lesson", MUTED).next_to(general, RIGHT, buff=0.4)
        n = self.narrate(
            id="sum27_06",
            text="This is a general rule you'll see again. In any row of N items, an item's position from the left "
                 "plus its position from the right equals N plus one. You'll use it again in the Ranking lesson.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "row")
        self.play(FadeOut(VGroup(line1, plus_one)), FadeTransform(rule, general))
        self.at_word(n, "Ranking")
        self.play(FadeIn(ahead, shift=LEFT * 0.2))
        self.validator.check_in_frame(VGroup(general, ahead))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_sum27")

    # ======================================== 5. EXAMPLE 1: BASIC ==========

    def example_basic(self):
        self.scene_start("S05_example_basic", title="Example 1 - Basic")

        question = self.question_card("Find the forward and reverse positions of P.")
        strip = AlphabetStrip().move_to(UP * STRIP_Y)
        colors = {r"\text{Forward}": FWD, r"\text{Reverse}": REV, "16": FWD, "11": REV, "15": ANCHOR}

        n = self.narrate(
            id="ex1_01",
            text="Let's find both positions of the letter P.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(question, shift=DOWN * 0.3), FadeIn(strip))
        self.play(strip.mark("P", FOCUS))
        self.wait_for_narration(n)

        # HEAR: after O, so sixteen.  SEE: O 15, one hop to P, P 16, the working.
        o15 = strip.label("O", text("15", NUM, ANCHOR))
        p16 = strip.label("P", text("16", NUM, FWD))
        arcs, _ = strip.hops("O", 1, numbered=False)
        fwd = math_row(math_line(r"\text{Forward}", "=", "15", "+", "1", "=", "16", colors=colors), 0)
        n = self.narrate(
            id="ex1_02",
            text="P comes right after O, which is fifteen. So P's forward position is sixteen.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "after")
        self.play(strip.mark("O"), FadeIn(o15))
        self.play(Create(arcs))
        self.at_word(n, "sixteen")
        self.play(FadeIn(p16, shift=DOWN * 0.1), Write(fwd))
        self.wait_for_narration(n)

        # HEAR: 27 - 16 = 11.  SEE: the reverse line.
        rev = math_row(math_line(r"\text{Reverse}", "=", "27", "-", "16", "=", "11", colors=colors), 1)
        n = self.narrate(
            id="ex1_03",
            text="Its reverse position is twenty-seven minus sixteen, which is eleven.",
            voice="default",
            subtitle=True,
        )
        self.play(Write(rev))
        self.wait_for_narration(n)

        # HEAR: the check.  SEE: counts 1..11 from Z back to P, the 11 circled.
        ticks = VGroup(*[strip.label(ch, text(str(k + 1), NUM, REV), DOWN)
                         for k, ch in enumerate("ZYXWVUTSRQP")])
        holds = pill("✓  rule holds", GOOD).next_to(rev, RIGHT, buff=0.5)
        n = self.narrate(
            id="ex1_04",
            text="Quick check: counting from Z back to P, we land on eleven. The rule holds.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(arcs))
        self.play_with(n, LaggedStart(*[FadeIn(t, scale=0.5) for t in ticks], lag_ratio=0.5), fraction=0.6)
        self.at_word(n, "holds")
        self.play(Circumscribe(ticks[-1], color=GOOD), FadeIn(holds))
        self.validator.check_in_frame(VGroup(question, strip, ticks, fwd, rev, holds))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_example_basic")

    # ================================== 6. EXAMPLE 2: APPLICATION ==========

    def example_application(self):
        self.scene_start("S06_example_application", title="Example 2 - Application")

        question = self.question_card("Which letter is 8th from the right end?")
        strip = AlphabetStrip().move_to(UP * STRIP_Y)
        colors = {r"\text{Forward}": FWD, r"\text{Reverse}": REV, "19": FWD, "8": REV}

        # HEAR: back to the opening question.
        n = self.narrate(
            id="ex2_01",
            text="Now let's go back to our opening question: which letter is eighth from the right end?",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(question, shift=DOWN * 0.3), FadeIn(strip))
        self.wait_for_narration(n)

        # HEAR: reverse 8, so forward 27 - 8 = 19.  SEE: two working lines.
        line1 = math_row(math_line(r"\text{Reverse}", "=", "8", colors=colors), 0)
        line2 = math_row(math_line(r"\text{Forward}", "=", "27", "-", "8", "=", "19", colors=colors), 1)
        n = self.narrate(
            id="ex2_02",
            text="Being eighth from the right means a reverse position of eight. "
                 "So the forward position is twenty-seven minus eight, which is nineteen.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "reverse")
        self.play(Write(line1))
        self.at_word(n, "forward")
        self.play(Write(line2))
        self.wait_for_narration(n)

        # HEAR: one before T, so S.  SEE: T 20, one hop back, S turns green.
        t20 = strip.label("T", text("20", NUM, ANCHOR))
        arcs, _ = strip.hops("T", -1, numbered=False)
        answer = pill("Answer:  S", GOOD, size=LABEL).next_to(line2, RIGHT, buff=0.6)
        n = self.narrate(
            id="ex2_03",
            text="Nineteen is one before T, which is twenty. The answer is S.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "before")
        self.play(strip.mark("T"), FadeIn(t20))
        self.play(Create(arcs))
        self.at_word(n, "answer")
        self.play(strip.mark("S", GOOD), Flash(strip.cell("S"), color=GOOD), FadeIn(answer, scale=1.2))
        self.validator.check_in_frame(VGroup(line2, answer))
        self.wait_for_narration(n)

        n = self.narrate(
            id="ex2_04",
            text="No counting on fingers, and about two seconds of work.",
            voice="default",
            subtitle=True,
        )
        cap = self.caption("No counting  ·  about 2 seconds", GOOD)
        self.play(FadeIn(cap, shift=UP * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_example_application")

    # ================================= 7. EXAMPLE 3: EXAM-ORIENTED ==========

    def example_exam(self):
        self.scene_start("S07_example_exam", title="Example 3 - Exam-Oriented")

        question = self.question_card("Each letter → its reverse position.  Value of CAT?")
        letters = VGroup(*[text(c, 84, INK, BOLD) for c in "CAT"]).arrange(RIGHT, buff=1.8).move_to(UP * 0.9)
        fwd_vals, rev_vals = ["3", "1", "20"], ["24", "26", "7"]
        fwd = VGroup(*[text(v, 36, FWD, BOLD).next_to(l, DOWN, buff=0.3) for v, l in zip(fwd_vals, letters)])
        rev = VGroup(*[text(v, 36, REV, BOLD).next_to(l, DOWN, buff=0.3) for v, l in zip(rev_vals, letters)])

        # HEAR: the coding pattern.  SEE: the question card, then C, A, T.
        n = self.narrate(
            id="ex3_01",
            text="Here's a pattern that turns up in coding questions. Every letter is replaced by its reverse "
                 "position, and you're asked for the total value of the word CAT.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(question, shift=DOWN * 0.3))
        self.at_word(n, "total")
        self.play(LaggedStart(*[FadeIn(l, shift=UP * 0.3) for l in letters], lag_ratio=0.25))
        self.wait_for_narration(n)

        # HEAR: C 3 -> 24, A 1 -> 26, T 20 -> 7.  SEE: each forward number
        # appears on "forward" and turns into the reverse number on "reverse".
        n = self.narrate(
            id="ex3_02",
            text="The direct method is to convert each letter. C is three forward, so twenty-four in reverse. "
                 "A is one forward, so twenty-six in reverse. T is twenty forward, so seven in reverse.",
            voice="default",
            subtitle=True,
        )
        for k in range(3):
            self.at_word(n, "forward", occurrence=k + 1)
            self.play(FadeIn(fwd[k], shift=DOWN * 0.15), run_time=0.5)
            self.at_word(n, "reverse", occurrence=k + 1)
            self.play(ReplacementTransform(fwd[k], rev[k]), run_time=0.6)
        self.wait_for_narration(n)

        # HEAR: 24 + 26 + 7 = 57.  SEE: the sum under the letters.
        total = math_row(math_line("24", "+", "26", "+", "7", "=", "57",
                                   colors={"24": REV, "26": REV, "7": REV, "57": GOOD}), 0)
        n = self.narrate(
            id="ex3_03",
            text="Twenty-four plus twenty-six plus seven gives fifty-seven.",
            voice="default",
            subtitle=True,
        )
        self.play(Write(total))
        self.wait_for_narration(n)

        # HEAR: the faster way.  SEE: the shortcut replaces the question; the
        # forward sum is written first.
        shortcut = self.card(math_line(r"\text{Reverse sum}", "=", r"27\times(\text{letters})", "-",
                                       r"\text{Forward sum}",
                                       colors={r"\text{Reverse sum}": REV, r"\text{Forward sum}": FWD,
                                               r"27\times(\text{letters})": ANCHOR}, size=38),
                             color=ANCHOR)
        shortcut.move_to(UP * (CARD_TOP - shortcut.height / 2))
        work1 = math_line(r"\text{Forward sum}", "=", "3+1+20", "=", "24",
                          colors={r"\text{Forward sum}": FWD, "24": FWD}, size=40).move_to(UP * 0.9)
        n = self.narrate(
            id="ex3_04",
            text="There's also a faster way. The forward values add up to three plus one plus twenty, "
                 "which is twenty-four.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(VGroup(letters, rev, total)), FadeTransform(question, shortcut))
        self.at_word(n, "forward")
        self.play(Write(work1))
        self.wait_for_narration(n)

        # HEAR: 3 x 27 - 24 = 81 - 24 = 57.  SEE: two more lines, the result boxed.
        work2 = math_line(r"\text{Reverse sum}", "=", r"3\times 27", "-", "24",
                          colors={r"\text{Reverse sum}": REV, r"3\times 27": ANCHOR}, size=40)
        work3 = math_line("=", "81", "-", "24", "=", "57", colors={"57": GOOD}, size=40)
        work2.next_to(work1, DOWN, buff=0.45, aligned_edge=LEFT)
        work3.next_to(work2, DOWN, buff=0.45).align_to(work2[1], LEFT)
        box = SurroundingRectangle(work3, color=GOOD, buff=0.12)
        n = self.narrate(
            id="ex3_05",
            text="Each of the three letters contributes twenty-seven between its two positions, so the reverse sum "
                 "is three times twenty-seven, minus twenty-four. That's eighty-one minus twenty-four, "
                 "which is fifty-seven again.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "times")
        self.play(Write(work2))
        self.play_with(n, Write(work3), fraction=0.5)
        self.at_word(n, "again")
        self.play(Create(box))
        self.validator.check_in_frame(VGroup(shortcut, work1, work3, box))
        self.wait_for_narration(n)

        n = self.narrate(
            id="ex3_06",
            text="Notice that the shortcut isn't a trick to memorise. It follows directly from the sum-27 rule.",
            voice="default",
            subtitle=True,
        )
        cap = self.caption("The shortcut is just the sum-27 rule, once per letter", FOCUS)
        self.at_word(n, "follows")
        self.play(FadeIn(cap, shift=UP * 0.2), Indicate(work2[2], color=ANCHOR))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S07_example_exam")

    # ======================================== 8. EXAM APPLICATION ==========

    def exam_application(self):
        self.scene_start("S08_exam", title="Exam Application")

        row_w = SAFE_W - 1.2
        rows = VGroup(
            VGroup(text("“from the right end”", LABEL, INK), text("→", LABEL, MUTED),
                   text("reverse position", LABEL, REV, BOLD)).arrange(RIGHT, buff=0.35),
            VGroup(text("“alphabet written in reverse order”", LABEL, INK), text("→", LABEL, MUTED),
                   text("reverse becomes the new forward", LABEL, REV, BOLD)).arrange(RIGHT, buff=0.35),
        ).arrange(DOWN, buff=0.5, aligned_edge=LEFT)
        fit_width(rows, row_w)
        wording = self.card(rows).move_to(UP * 0.3)

        # HEAR: recognise the wording.
        n = self.narrate(
            id="exam_01",
            text="In the exam, position questions rarely say reverse position directly. "
                 "You'll need to recognise the wording.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "wording")
        self.play(FadeIn(wording[0]))
        self.wait_for_narration(n)

        # HEAR: the two phrases.  SEE: one row per phrase.
        n = self.narrate(
            id="exam_02",
            text="Phrases like from the right end mean a reverse position. Phrases like if the alphabet is written "
                 "in reverse order mean the reverse positions become the new left-to-right positions.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Phrases", occurrence=1)
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "Phrases", occurrence=2)
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        # HEAR: the question.  SEE: the question card and the strip.
        question = self.question_card("Alphabet written in reverse order: which letter is 15th from the left?")
        strip = AlphabetStrip().move_to(UP * STRIP_Y)
        n = self.narrate(
            id="exam_03",
            text="Let's try one. If the alphabet is written in reverse order, which letter is fifteenth from the left?",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(wording), FadeIn(question, shift=DOWN * 0.3))
        self.play(FadeIn(strip))
        self.wait_for_narration(n)

        # HEAR: 15th from the left of the reversed strip = 27 - 15 = 12 = L.
        # SEE: the strip flips to Z...A, slot 15 lights up, L turns green.
        slot = strip.cells[14]
        slot_label = text("15th", NUM, FOCUS, BOLD).next_to(slot, UP, buff=0.14)
        work = math_row(math_line("27", "-", "15", "=", "12", r"\rightarrow", r"\text{L}",
                                  colors={"12": FWD, r"\text{L}": GOOD}), 0)
        n = self.narrate(
            id="exam_04",
            text="In the reversed alphabet, the fifteenth from the left is the fifteenth from the right of the "
                 "normal alphabet. Twenty-seven minus fifteen is twelve, and the twelfth letter is L.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "reversed")
        self.play(*[strip.chars[k].animate.move_to(strip.cells[25 - k]) for k in range(26)],
                  run_time=1.6, path_arc=PI / 2)
        self.at_word(n, "fifteenth", occurrence=1)
        self.play(slot.animate.set_fill(FOCUS, 0.3).set_stroke(FOCUS, 3), FadeIn(slot_label))
        self.at_word(n, "minus")
        self.play(Write(work))
        self.at_word(n, "twelfth")
        self.play(strip.chars[11].animate.set_color(GOOD), Flash(slot, color=GOOD))
        self.wait_for_narration(n)

        # HEAR: the method in three steps.  SEE: a step tracker, lit step by step.
        tracker = self.step_tracker(["Which end?", "Convert with 27", "Nearest anchor"])
        n = self.narrate(
            id="exam_05",
            text="So the method is always the same. First, identify which end you're counting from. "
                 "Then, if needed, convert using twenty-seven. Finally, find the letter using the nearest anchor.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(tracker, shift=UP * 0.2))
        self.at_word(n, "First")
        self.play(self.focus_step(tracker, 0))
        self.at_word(n, "Then")
        self.play(self.focus_step(tracker, 1))
        self.at_word(n, "Finally")
        self.play(self.focus_step(tracker, 2))
        self.validator.check_in_frame(VGroup(question, strip, work, tracker))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S08_exam")

    # =========================================== 9. COMMON MISTAKE ==========

    def common_mistake(self):
        self.scene_start("S09_mistake", title="Common Mistake")

        wrong = self.card(VGroup(text("✗", 40, BAD, BOLD),
                                 math_line("26", "-", "8", "=", "18", r"\rightarrow", r"\text{R}", colors={}, size=40))
                          .arrange(RIGHT, buff=0.3), color=BAD)
        right = self.card(VGroup(text("✓", 40, GOOD, BOLD),
                                 math_line("27", "-", "8", "=", "19", r"\rightarrow", r"\text{S}", colors={}, size=40))
                          .arrange(RIGHT, buff=0.3), color=GOOD)
        wrong.move_to(LEFT_ZONE + UP * (CARD_TOP - wrong.height / 2))
        right.move_to(RIGHT_ZONE + UP * (CARD_TOP - right.height / 2))
        strip = AlphabetStrip().move_to(UP * STRIP_Y)

        # HEAR: 26 instead of 27.  SEE: the wrong card.
        n = self.narrate(
            id="mistake_01",
            text="The most common mistake is using twenty-six instead of twenty-seven.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(wrong, shift=RIGHT * 0.3))
        self.wait_for_narration(n)

        # HEAR: it ignores the letter itself; it shifts the answer by one.
        # SEE: the right card, then R (red) beside S (green) on the strip.
        trap = text("trap option", SMALL, BAD, BOLD)
        strip.label("R", trap, DOWN, buff=0.2)
        n = self.narrate(
            id="mistake_02",
            text="It's an understandable slip, since there are twenty-six letters. But that ignores the letter "
                 "itself, which is counted from both ends. Using twenty-six shifts your answer by one letter. "
                 "That's exactly the wrong option an examiner will place among the choices.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "ignores")
        self.play(FadeIn(right, shift=LEFT * 0.3))
        self.at_word(n, "shifts")
        self.play(FadeIn(strip))
        self.play(strip.mark("R", BAD), strip.mark("S", GOOD))
        self.at_word(n, "examiner")
        self.play(FadeIn(trap, shift=UP * 0.1))
        self.wait_for_narration(n)

        # HEAR: counting O itself as step one.  SEE: 1, 2, 3 written on O, P, Q
        # (on the letters, the wrong way), and Q marked red.
        question = self.question_card("3 steps after O = ?")
        bad_counts = VGroup(*[strip.label(ch, text(str(k + 1), NUM, BAD, BOLD), DOWN)
                              for k, ch in enumerate("OPQ")])
        n = self.narrate(
            id="mistake_03",
            text="A second mistake happens with the anchors. To find the letter three after O, some learners count "
                 "O itself as the first step: O, P, Q, and they answer Q. That's wrong.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(VGroup(wrong, right, trap)), strip.unmark("R"), strip.unmark("S"))
        self.play(FadeIn(question, shift=DOWN * 0.3), strip.mark("O"))
        self.at_word(n, "first")
        self.play(LaggedStart(*[FadeIn(c, scale=0.6) for c in bad_counts], lag_ratio=0.5))
        self.at_word(n, "answer")
        self.play(strip.mark("Q", BAD))
        self.at_word(n, "wrong")
        self.play(Indicate(strip.cell("Q"), color=BAD))
        self.wait_for_narration(n)

        # HEAR: three hops from O lands on R.  SEE: hops numbered on the hops.
        arcs, hop_nums = strip.hops("O", 3)
        result = math_row(math_line(r"\text{O}", "+", "3", "=", r"\text{R}", "=", "18",
                                    colors={r"\text{R}": GOOD, "18": GOOD}), 1)
        n = self.narrate(
            id="mistake_04",
            text="Moving three steps forward from O lands on R, which is eighteen.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(bad_counts), strip.unmark("Q"))
        self.play_with(n, LaggedStart(*[AnimationGroup(Create(a), FadeIn(l)) for a, l in zip(arcs, hop_nums)],
                                      lag_ratio=0.8), fraction=0.6)
        self.at_word(n, "eighteen")
        self.play(strip.mark("R", GOOD), Write(result))
        self.wait_for_narration(n)

        n = self.narrate(
            id="mistake_05",
            text="The correct habit is to count the hops, not the letters you touch.",
            voice="default",
            subtitle=True,
        )
        cap = self.caption("Count the hops, not the letters you touch", FOCUS)
        self.at_word(n, "hops")
        self.play(FadeIn(cap, shift=UP * 0.2), Indicate(hop_nums, color=FOCUS))
        self.validator.check_in_frame(VGroup(question, strip, hop_nums, result, cap))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S09_mistake")

    # ================================================ 10. PRACTICE ==========

    def practice(self):
        self.scene_start("S10_practice", title="Practice Question")

        card_w = SAFE_W - 1.0
        q1 = VGroup(pill("Q1", FOCUS), fitted_text("Which letter is 20th from the right end?", card_w - 1.6, BODY))
        q2 = VGroup(pill("Q2", FOCUS), fitted_text("Which letter's forward position is twice its reverse position?",
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
            text="First, which letter is twentieth from the right end?",
            voice="default",
            subtitle=True,
        )
        self.play(q1.animate.set_opacity(1))
        self.wait_for_narration(n)

        # SILENCE (pause_after): countdown ring while the learner thinks.
        n = self.narrate(
            id="practice_03",
            text="Second, and this one needs a little more thought: which letter has a forward position "
                 "exactly twice its reverse position?",
            voice="default",
            subtitle=True,
            pause_after=6.0,
        )
        self.play(q2.animate.set_opacity(1))
        self.at_word(n, "twice")
        self.play(Indicate(q2[1], color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        self.clear_stage()
        self.scene_end("S10_practice")

    # ================================================== 11. ANSWER ==========

    def answer(self):
        self.scene_start("S11_answer", title="Answer and Explanation")

        strip = AlphabetStrip().move_to(UP * STRIP_Y)

        # HEAR: Q1: 27 - 20 = 7, two after E, so G.  SEE: working line, E 5,
        # two hops to G.
        tag_q1 = pill("Q1", FOCUS).move_to(UP * (CARD_TOP - 0.3))
        q1 = math_row(math_line(r"\text{Reverse}=20", r"\;\rightarrow\;", r"\text{Forward}", "=", "27", "-", "20",
                                "=", "7", colors={r"\text{Reverse}=20": REV, r"\text{Forward}": FWD, "7": FWD}), 0)
        e5 = strip.label("E", text("5", NUM, ANCHOR))
        arcs, hop_nums = strip.hops("E", 2)
        n = self.narrate(
            id="answer_01",
            text="For the first question, twentieth from the right means a reverse position of twenty. "
                 "Twenty-seven minus twenty is seven. Seven is two after E, so the answer is G.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(tag_q1), FadeIn(strip))
        self.at_word(n, "minus")
        self.play(Write(q1))
        self.at_word(n, "two")
        self.play(strip.mark("E"), FadeIn(e5))
        self.play(LaggedStart(*[AnimationGroup(Create(a), FadeIn(l)) for a, l in zip(arcs, hop_nums)],
                              lag_ratio=0.6))
        self.at_word(n, "answer")
        self.play(strip.mark("G", GOOD), Flash(strip.cell("G"), color=GOOD))
        self.wait_for_narration(n)

        # HEAR: Q2 set-up: f = 2(27 - f) = 54 - 2f.  SEE: three lines, left zone.
        tag_q2 = pill("Q2", FOCUS).move_to(tag_q1)
        colors = {"f": FWD, "27-f": REV, "18": GOOD, r"\text{R}": GOOD}
        left_x = LEFT_ZONE + LEFT * 1.2
        l1 = math_line(r"\text{Reverse}", "=", "27-f", colors={r"\text{Reverse}": REV, "27-f": REV}, size=40)
        l2 = math_line("f", "=", r"2\times", "(27-f)", colors={"f": FWD, "(27-f)": REV}, size=40)
        l3 = math_line("f", "=", "54", "-", "2f", colors={"f": FWD}, size=40)
        left_col = VGroup(l1, l2, l3).arrange(DOWN, buff=0.35, aligned_edge=LEFT)
        left_col.move_to(left_x + UP * (MATH_Y1 - 0.55))
        n = self.narrate(
            id="answer_02",
            text="For the second, call the forward position f. Then the reverse position is twenty-seven minus f. "
                 "The condition says f equals two times that, so f equals fifty-four minus two f.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(VGroup(q1, e5, arcs, hop_nums)), strip.unmark("E"), strip.unmark("G"),
                  FadeTransform(tag_q1, tag_q2))
        self.at_word(n, "reverse")
        self.play(Write(l1))
        self.at_word(n, "condition")
        self.play(Write(l2))
        self.play_with(n, Write(l3), fraction=0.7)
        self.wait_for_narration(n)

        # HEAR: 3f = 54, f = 18, R.  SEE: right-zone lines, then R lights up.
        r1 = math_line("3f", "=", "54", colors={"3f": FWD}, size=40)
        r2 = math_line("f", "=", "18", r"\;\rightarrow\;", r"\text{R}", colors=colors, size=40)
        right_col = VGroup(r1, r2).arrange(DOWN, buff=0.35, aligned_edge=LEFT)
        right_col.move_to(RIGHT_ZONE + UP * (MATH_Y1 - 0.2))
        arrow = Arrow(left_col.get_right(), right_col.get_left(), buff=0.3, color=MUTED, stroke_width=4)
        n = self.narrate(
            id="answer_03",
            text="Adding two f to both sides gives three f equals fifty-four, so f is eighteen. "
                 "The eighteenth letter is R.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "gives")
        self.play(GrowArrow(arrow), Write(r1))
        self.at_word(n, "eighteen")
        self.play(Write(r2))
        self.at_word(n, "letter")
        self.play(strip.mark("R", GOOD))
        self.wait_for_narration(n)

        # HEAR: R is 18 from the left and 9 from the right.  SEE: 18 above,
        # 9 below, and the check pill.
        r18 = strip.label("R", text("18", NUM, FWD, BOLD), UP)
        r9 = strip.label("R", text("9", NUM, REV, BOLD), DOWN)
        check = pill("18 = 2 × 9  ✓", GOOD).next_to(r18, UP, buff=0.3)
        n = self.narrate(
            id="answer_04",
            text="To check: R is eighteen from the left and nine from the right, and eighteen is twice nine.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "left")
        self.play(FadeIn(r18, shift=DOWN * 0.1))
        self.at_word(n, "nine")
        self.play(FadeIn(r9, shift=UP * 0.1))
        self.at_word(n, "twice")
        self.play(FadeIn(check, shift=DOWN * 0.1))
        self.validator.check_in_frame(VGroup(check, strip, r9, left_col, right_col))
        self.wait_for_narration(n)

        # HEAR: this can't be solved by counting.  SEE: the equation work is framed.
        n = self.narrate(
            id="answer_05",
            text="Notice that the second question can't be solved by counting. It needs the relationship between "
                 "the two positions, and that relationship is exactly what this lesson is about.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "relationship", occurrence=1)
        self.play(Circumscribe(VGroup(left_col, right_col), color=FOCUS, run_time=1.5))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S11_answer")

    # ========================================== 12. QUICK REVISION ==========

    def quick_revision(self):
        self.scene_start("S12_revision", title="Quick Revision")

        card_w, card_h = SAFE_W - 1.0, 5.2
        items = [
            ("Forward position:  A = 1 … Z = 26", FWD),
            ("EJOTY:  E5 · J10 · O15 · T20 · Y25", ANCHOR),
            ("Forward + Reverse = 27", FOCUS),
            ("Reverse = 27 − Forward", REV),
            ("“From the right” / “reverse order”  →  convert with 27", INK),
            ("Count hops, not letters", GOOD),
        ]
        bullets = VGroup(*[VGroup(Dot(radius=0.07, color=c), fitted_text(s, card_w - 1.4, BODY, c))
                           .arrange(RIGHT, buff=0.3) for s, c in items]).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        board = self.card(bullets, width=card_w, height=card_h).move_to(DOWN * 0.1)
        faded = AlphabetStrip().set_opacity(0.12).move_to(DOWN * (FRAME_H / 2 - SAFE - 0.3))
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="revision_01",
            text="Let's quickly revise.",
            voice="default",
            subtitle=True,
        )
        self.add(faded)
        self.play(FadeIn(board[0]))
        self.wait_for_narration(n)

        n = self.narrate(
            id="revision_02",
            text="Every letter has a forward position, counted from A, and a reverse position, counted from Z.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(bullets[0], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="revision_03",
            text="The EJOTY anchors, at five, ten, fifteen, twenty and twenty-five, "
                 "let you find any forward position in one small step.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(bullets[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="revision_04",
            text="Forward plus reverse always equals twenty-seven, because the letter itself is counted from both ends.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(bullets[2], shift=RIGHT * 0.2))
        self.at_word(n, "because")
        self.play(FadeIn(bullets[3], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="revision_05",
            text="And in exam questions, wording like from the right or reverse order "
                 "is your signal to convert using twenty-seven.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(bullets[4], shift=RIGHT * 0.2))
        self.at_word(n, "signal")
        self.play(FadeIn(bullets[5], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S12_revision")

    # ================================================= 13. CLOSING ==========
    # Purpose: return to the strip, now readable from both ends, and point
    # ahead to Opposite Letters (A-Z, B-Y).

    def closing(self):
        self.scene_start("S13_closing", title="Closing")

        strip = AlphabetStrip().move_to(DOWN * 0.3)
        fwd = strip.number_row(color=FWD)
        rev = strip.number_row(reverse=True, side=DOWN, color=REV)

        n = self.narrate(
            id="closing_01",
            text="With these few ideas, you can place any letter instantly, from either end of the alphabet.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(strip))
        self.at_word(n, "either")
        self.play(LaggedStart(FadeIn(fwd, shift=DOWN * 0.1), FadeIn(rev, shift=UP * 0.1), lag_ratio=0.4))
        self.wait_for_narration(n)

        # HEAR: letters at the same distance from opposite ends.  SEE: arcs
        # join A-Z and B-Y on the words that name them.
        def pair_arc(a, b, color):
            return ArcBetweenPoints(strip.cell(a).get_top() + UP * 0.08, strip.cell(b).get_top() + UP * 0.08,
                                    angle=-PI / 3, color=color, stroke_width=4)

        arc_az, arc_by = pair_arc("A", "Z", ANCHOR), pair_arc("B", "Y", FOCUS)
        n = self.narrate(
            id="closing_02",
            text="The sum-27 rule leads straight into the next idea: letters that sit at the same distance from "
                 "opposite ends, like A and Z, or B and Y.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(fwd), FadeOut(rev))
        self.at_word(n, "like")
        self.play(Create(arc_az), strip.mark("A", ANCHOR), strip.mark("Z", ANCHOR))
        self.at_word(n, "or")
        self.play(Create(arc_by), strip.mark("B", FOCUS), strip.mark("Y", FOCUS))
        self.validator.check_in_frame(VGroup(arc_az, strip))
        self.wait_for_narration(n)

        nxt = pill("Next:  Opposite Letters", ANCHOR, size=BODY).move_to(DOWN * 2.2)
        n = self.narrate(
            id="closing_03",
            text="These are called opposite letters, and they're a favourite in coding questions. "
                 "We'll look at them next.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "opposite")
        self.play(FadeIn(nxt, scale=1.1))
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S13_closing")

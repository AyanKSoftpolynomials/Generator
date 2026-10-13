"""
animation.py for the LMS video generator.

Course : C-CAT - Section A - English
Module : Module 1 - Vocabulary
Lesson : Lesson 2 - Antonyms
Video  : 02 - Types of Antonyms (Video 2 of 7)

Source script:
  C:\\Users\\User\\Downloads\\C-CAT_SectionA_Module1_English\\English\\Module 1 - Vocabulary\\
  Lesson 2 - Antonyms\\02 - Types of Antonyms.pdf

Built on the golden-reference pattern:
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``;
  * layouts stacked with next_to and guarded with ``no_overlap``; nothing is
    ever animated onto or into another box.

Opening: a later video of Lesson 2, so no spoken welcome. The module > lesson >
video trail is shown on screen (silent), then a one-line recap of Video 1
(intuitive <-> baffling: reverse the core), the title and the objectives.

Core visuals: the three types drawn as a gradable scale (far ends lit), a
complementary split box (nothing in between) and relational role pairs; the
analogy as a dimmer, a switch and a flipping coin (every moving part stays on
its own track or inside its own housing); ``OptionQuestion`` cards tagged with
the type that decides them.
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

TYPES = [("Gradable", RATIO, "a scale with a middle", "pick the FAR END"),
         ("Complementary", WORD, "no middle", "pick the OTHER STATE"),
         ("Relational", SECOND, "two roles", "pick the PARTNER")]
TYPE_COL = {t: c for t, c, _, _ in TYPES}


def scale_line(words, far_color=GOOD, width=9.0):
    """A gradable scale: words spread along a line with ticks; both ends marked as the far ends."""
    line = Line(LEFT * width / 2, RIGHT * width / 2, color=MUTED, stroke_width=4)
    xs = [-width / 2 + i * width / (len(words) - 1) for i in range(len(words))]
    ticks = VGroup(*[Line(UP * 0.15, DOWN * 0.15, color=MUTED, stroke_width=3).move_to(RIGHT * x) for x in xs])
    chips = VGroup(*[pill(w, far_color if i in (0, len(words) - 1) else MUTED, size=LABEL)
                     .move_to(RIGHT * x + UP * 0.55) for i, (w, x) in enumerate(zip(words, xs))])
    return VGroup(line, ticks, chips)


def switch_box(left, right, width=5.0, height=1.0):
    """A complementary pair: one box split in two, nothing in between."""
    box = Rectangle(width=width, height=height, color=WORD, stroke_width=3)
    mid = Line(box.get_top(), box.get_bottom(), color=WORD, stroke_width=3)
    lt = text(left, LABEL, INK, BOLD).move_to(box.get_center() + LEFT * width / 4)
    rt = text(right, LABEL, INK, BOLD).move_to(box.get_center() + RIGHT * width / 4)
    return VGroup(box, mid, lt, rt)


def role_pair(a, b, verb_a, verb_b):
    """A relational pair: two roles joined by a double arrow."""
    left = VGroup(pill(a, SECOND, size=LABEL), text(verb_a, SMALL, MUTED)).arrange(DOWN, buff=0.12)
    right = VGroup(pill(b, SECOND, size=LABEL), text(verb_b, SMALL, MUTED)).arrange(DOWN, buff=0.12)
    arrow = DoubleArrow(LEFT, RIGHT, color=SECOND, buff=0, stroke_width=3).set_length(1.4)
    return VGroup(left, arrow, right).arrange(RIGHT, buff=0.3)


class TypesOfAntonymsVideo(LMSScene):
    lesson_title = "Types of Antonyms"

    def construct(self):
        self.camera.background_color = BG

        self.lesson_intro()
        self.hook()
        self.concept()
        self.why_you_need_it()
        self.analogy()
        self.example_scorching()
        self.example_present()
        self.example_lend()
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

    def option_example(self, word, options, key, traps, note):
        q = OptionQuestion(word, options, key, traps)
        q.group.to_edge(LEFT, buff=SAFE + 0.6).set_y(0.3)
        tag = pill(note, TYPE_COL[note.split(":")[0]], size=SMALL).to_edge(RIGHT, buff=SAFE + 0.2).align_to(q.word, UP)
        self.no_overlap(q.word, tag)
        self.validator.check_in_frame(VGroup(q.group, tag))
        return q, tag

    # ========================================= 0. LESSON INTRO ==========

    def lesson_intro(self):
        self.scene_start("S00_intro", title="Lesson Introduction")

        crumb = self.breadcrumb("English · Module 1 Vocabulary", "Lesson 2 · Antonyms", "Video 2")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        rev = VGroup(pill("intuitive", WORD, size=BODY), text("↔", TITLE, MUTED), pill("baffling", GOOD, size=BODY))\
            .arrange(RIGHT, buff=0.4)
        core = pill("reverse the CORE meaning", GOOD, size=LABEL)
        VGroup(rev, core).arrange(DOWN, buff=0.6).move_to(UP * 0.2)
        self.no_overlap(crumb, rev, core)
        self.validator.check_in_frame(VGroup(crumb, rev, core))

        n = self.narrate(
            id="intro_01",
            text="In video one, you learned to reverse a word's core meaning, like intuitive and baffling. Today you'll see "
                 "that reverse works differently for different kinds of words.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.at_word(n, "reverse", occurrence=1)
        self.play(FadeIn(core, shift=UP * 0.1))
        self.at_word(n, "intuitive")
        self.play(FadeIn(rev, shift=UP * 0.1))
        self.wait_for_narration(n)

        title = fitted_text("Types of Antonyms", SAFE_W, 72, INK, BOLD)
        underline = Line(LEFT, RIGHT, color=RATIO, stroke_width=5).set_width(title.width * 0.6)
        VGroup(title, underline).arrange(DOWN, buff=0.2).move_to(UP * 0.2)
        goals = [("Recognise gradable, complementary and relational antonyms", RATIO),
                 ("Use the type to pick the true opposite, not a midpoint", GOOD)]
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
            text="These are the types of antonyms. By the end of this video, you'll recognise gradable, complementary and "
                 "relational antonyms, and you'll use the type to pick the true opposite, not a midpoint.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(VGroup(rev, core), shift=UP * 0.3))
        self.at_word(n, "types")
        self.play(Write(title), run_time=1.1)
        self.play(GrowFromCenter(underline))
        self.at_word(n, "By")
        self.play(FadeOut(underline), ReplacementTransform(title, small_title), run_time=0.8)
        self.play(FadeIn(objectives[0]), FadeIn(heading))
        for row_, spoken in zip(rows, ["recognise", "use"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row_, shift=RIGHT * 0.2), run_time=0.5)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_intro")

    # ================================================= 1. HOOK ==========

    HOOK = dict(word="no middle ground?", options=["hot – cold", "pass – fail", "rich – poor", "happy – sad"],
                key="b", traps={"a": "warm and cool between", "c": "“comfortable” between",
                                "d": "“content” between"})

    def dashboard(self):
        tests = VGroup(*[VGroup(text(f"test_{i}", SMALL, INK), pill(r, GOOD if r == "PASS" else BAD, size=SMALL))
                         .arrange(RIGHT, buff=0.3) for i, r in enumerate(["PASS", "PASS", "FAIL"], start=1)])
        tests.arrange(DOWN, buff=0.15, aligned_edge=LEFT)
        ci = self.card(VGroup(text("CI dashboard", SMALL, MUTED, BOLD), tests).arrange(DOWN, buff=0.2, aligned_edge=LEFT))
        weather = self.card(VGroup(text("weather", SMALL, MUTED, BOLD), pill("warm", RATIO, size=LABEL))
                            .arrange(DOWN, buff=0.2))
        both = VGroup(ci, weather).arrange(RIGHT, buff=0.8, aligned_edge=UP)
        return both.move_to(UP * (CARD_TOP - both.height / 2))

    def hook(self):
        self.scene_start("S01_hook", title="Hook")

        dash = self.dashboard()
        h = self.HOOK
        q = OptionQuestion(h["word"], h["options"], h["key"], h["traps"])
        opts = q.rows.copy().arrange(RIGHT, buff=0.7)
        fit_width(opts, SAFE_W)
        ask = pill("Which pair has NO middle ground at all?", FOCUS, size=LABEL)
        ask.next_to(dash, DOWN, buff=0.6)
        opts.next_to(ask, DOWN, buff=0.5)
        self.no_overlap(dash, ask, opts)
        self.validator.check_in_frame(VGroup(dash, ask, opts))

        n = self.narrate(
            id="hook_01",
            text="Your CI dashboard shows every test as pass or fail. Next to it, a weather widget says warm. Your "
                 "colleague says both are just opposites.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "dashboard")
        self.play(FadeIn(dash[0], shift=DOWN * 0.2))
        self.at_word(n, "weather")
        self.play(FadeIn(dash[1], shift=DOWN * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_02",
            text="Which pair has no middle ground at all? Hot and cold, pass and fail, rich and poor, or happy and sad?",
            voice="default",
            subtitle=True,
            pause_after=3.0,
        )
        self.play(FadeIn(ask, shift=UP * 0.1))
        for row, spoken in zip(opts, ["Hot", "pass", "rich", "happy"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=UP * 0.15), run_time=0.35)
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        self.clear_stage()
        self.scene_end("S01_hook")

    # ============================================== 2. CONCEPT ==========

    def concept(self):
        self.scene_start("S02_concept", title="The Concept")

        heads = VGroup(*[pill(f"{t}: {d}", c, size=LABEL) for t, c, d, _ in TYPES])
        grad = scale_line(["hot", "warm", "cool", "cold"])
        not_hot = pill("“not hot” could be warm: take the FAR END", RATIO, size=SMALL)
        g_block = VGroup(heads[0], grad, not_hot).arrange(DOWN, buff=0.35)
        comp = VGroup(switch_box("pass", "fail"), switch_box("alive", "dead")).arrange(RIGHT, buff=0.6)
        c_block = VGroup(heads[1], comp).arrange(DOWN, buff=0.35)
        rel = VGroup(role_pair("buy", "sell", "", ""), role_pair("lend", "borrow", "", "")).arrange(RIGHT, buff=0.8)
        r_block = VGroup(heads[2], rel).arrange(DOWN, buff=0.35)
        for blk in (g_block, c_block, r_block):
            fit_width(blk, SAFE_W)
            blk.move_to(UP * 0.4)
        self.validator.check_in_frame(VGroup(g_block))
        self.validator.check_in_frame(VGroup(c_block))
        self.validator.check_in_frame(VGroup(r_block))

        n = self.narrate(
            id="concept_01",
            text="Gradable antonyms are ends of a scale, with steps in between: hot, warm, cool, cold. Rich and poor. "
                 "Ancient and modern. Not hot doesn't mean cold; it could be warm. In exams, the correct antonym is the far "
                 "end of the scale, not a midpoint.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Gradable")
        self.play(FadeIn(heads[0], shift=DOWN * 0.1), Create(grad[0]), FadeIn(grad[1]))
        self.at_word(n, "hot", occurrence=1)
        self.play(LaggedStart(*[FadeIn(c, shift=UP * 0.1) for c in grad[2]], lag_ratio=0.25))
        self.at_word(n, "far")
        self.play(FadeIn(not_hot, shift=UP * 0.1), Indicate(grad[2][3], color=GOOD))
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_02",
            text="Complementary antonyms divide the world into two, with no middle: pass and fail, alive and dead, true and "
                 "false, present and absent. Not alive means dead. There's nothing in between.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(g_block))
        self.at_word(n, "Complementary")
        self.play(FadeIn(heads[1], shift=DOWN * 0.1))
        self.at_word(n, "pass")
        self.play(FadeIn(comp[0], shift=UP * 0.1))
        self.at_word(n, "alive", occurrence=1)
        self.play(FadeIn(comp[1], shift=UP * 0.1))
        self.at_word(n, "nothing")
        self.play(Indicate(comp[0][1], color=WORD), Indicate(comp[1][1], color=WORD))
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_03",
            text="Relational antonyms describe two sides of one relationship: buy and sell, employer and employee, teacher "
                 "and student, lend and borrow. Each needs the other to exist.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(c_block))
        self.at_word(n, "Relational")
        self.play(FadeIn(heads[2], shift=DOWN * 0.1))
        self.at_word(n, "buy")
        self.play(FadeIn(rel[0], shift=UP * 0.1))
        self.at_word(n, "lend")
        self.play(FadeIn(rel[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        summary = VGroup(*[VGroup(pill(t, c, size=LABEL), text(pick, LABEL, INK)).arrange(RIGHT, buff=0.35)
                           for t, c, _, pick in TYPES]).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        board = self.card(summary).move_to(UP * 0.3)
        self.validator.check_in_frame(board)
        n = self.narrate(
            id="concept_04",
            text="Knowing the type tells you what the answer should look like: the far end, the only other option, or the "
                 "partner role.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(r_block))
        self.play(FadeIn(board[0]))
        for row, spoken in zip(summary, ["far", "other", "partner"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.4)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_concept")

    # ======================================== 3. WHY YOU NEED IT ==========

    def why_you_need_it(self):
        self.scene_start("S03_why", title="Why You Need It")

        mid = VGroup(pill("middle-of-the-scale trap", RATIO, size=LABEL), text("hot  →  cool  ✗", LABEL, BAD))\
            .arrange(DOWN, buff=0.2)
        side = VGroup(pill("same-side trap", SECOND, size=LABEL), text("lend  →  loan  ✗", LABEL, BAD))\
            .arrange(DOWN, buff=0.2)
        traps = VGroup(mid, side).arrange(RIGHT, buff=1.4)
        fix = pill("knowing the type removes both", GOOD, size=LABEL)
        VGroup(traps, fix).arrange(DOWN, buff=0.9).move_to(UP * 0.3)
        self.no_overlap(traps, fix)
        self.validator.check_in_frame(VGroup(traps, fix))

        n = self.narrate(
            id="why_01",
            text="Gradable words produce the middle-of-the-scale trap: cool offered as the opposite of hot. Relational pairs "
                 "produce the same side trap: lend and loan offered as opposites. Knowing the type removes both.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "middle-of-the-scale")
        self.play(FadeIn(mid, shift=UP * 0.1))
        self.at_word(n, "same")
        self.play(FadeIn(side, shift=UP * 0.1))
        self.at_word(n, "Knowing")
        self.play(FadeIn(fix, scale=1.05))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_why")

    # ============================================== 4. ANALOGY ==========

    def analogy(self):
        self.scene_start("S04_analogy", title="The Analogy")

        # Dimmer: a track with a knob that slides between off and full (the knob stays on its own track).
        track = Line(DOWN * 1.1, UP * 1.1, color=MUTED, stroke_width=8)
        knob = Circle(radius=0.2, color=RATIO, fill_color=RATIO, fill_opacity=0.9).move_to(track.get_bottom())
        dimmer = VGroup(track, knob, text("dimmer", LABEL, RATIO, BOLD).next_to(track, DOWN, buff=0.45),
                        text("gradable", SMALL, MUTED))
        dimmer[3].next_to(dimmer[2], DOWN, buff=0.1)
        # Switch: a housing with a toggle that flips between two positions (always inside the housing).
        # Housing drawn from lines (not a box), so the toggle moving inside it is never a box-on-box overlap.
        housing = VGroup(*[Line(p0, p1, color=WORD, stroke_width=3) for p0, p1 in [
            (LEFT * 0.5 + UP * 1.0, RIGHT * 0.5 + UP * 1.0), (RIGHT * 0.5 + UP * 1.0, RIGHT * 0.5 + DOWN * 1.0),
            (RIGHT * 0.5 + DOWN * 1.0, LEFT * 0.5 + DOWN * 1.0), (LEFT * 0.5 + DOWN * 1.0, LEFT * 0.5 + UP * 1.0)]])
        toggle = RoundedRectangle(corner_radius=0.08, width=0.6, height=0.7, color=WORD, fill_color=WORD,
                                  fill_opacity=0.6).move_to(housing.get_center() + DOWN * 0.5)
        on_off = VGroup(text("ON", SMALL, INK).next_to(housing, UP, buff=0.1),
                        text("OFF", SMALL, INK).next_to(housing, DOWN, buff=0.1))
        switch = VGroup(housing, toggle, on_off, text("switch", LABEL, WORD, BOLD), text("complementary", SMALL, MUTED))
        switch[3].next_to(on_off[1], DOWN, buff=0.25)
        switch[4].next_to(switch[3], DOWN, buff=0.1)
        # Coin: two faces that only exist together.
        coin_face = Circle(radius=0.95, color=SECOND, fill_color=SECOND, fill_opacity=0.2)
        face_lab = text("buy", LABEL, INK, BOLD)
        coin = VGroup(coin_face, face_lab, text("coin", LABEL, SECOND, BOLD), text("relational", SMALL, MUTED))
        coin[2].next_to(coin_face, DOWN, buff=0.45)
        coin[3].next_to(coin[2], DOWN, buff=0.1)
        row = VGroup(dimmer, switch, coin).arrange(RIGHT, buff=1.6, aligned_edge=UP).move_to(UP * 0.2)
        ask = pill("Ask: which one is your word?", FOCUS, size=LABEL).to_edge(DOWN, buff=SAFE + 0.3)
        self.no_overlap(dimmer, switch, coin, ask)
        self.validator.check_in_frame(VGroup(row, ask))

        n = self.narrate(
            id="analogy_01",
            text="A dimmer has many settings between off and full. That's gradable. A light switch has only on and off. "
                 "That's complementary.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "dimmer")
        self.play(FadeIn(dimmer))
        self.play(knob.animate.move_to(track.get_top()), run_time=1.0)
        self.play(knob.animate.move_to(track.get_center()), run_time=0.6)
        self.at_word(n, "switch")
        self.play(FadeIn(switch))
        self.play(toggle.animate.move_to(housing.get_center() + UP * 0.5), run_time=0.4)
        self.play(toggle.animate.move_to(housing.get_center() + DOWN * 0.5), run_time=0.4)
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_02",
            text="A coin has two faces that only exist together. That's relational. Ask which one your word is.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "coin")
        self.play(FadeIn(coin))
        other = text("sell", LABEL, INK, BOLD).move_to(face_lab)
        self.play(coin_face.animate.stretch(0.05, 0), FadeOut(face_lab), run_time=0.35)
        self.play(coin_face.animate.stretch(20, 0), FadeIn(other), run_time=0.35)
        self.at_word(n, "Ask")
        self.play(FadeIn(ask, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_analogy")

    # ======================================== 5-7. WORKED EXAMPLES ==========

    def example_scorching(self):
        self.scene_start("S05_ex_scorching", title="Worked Example 1")

        q, tag = self.option_example("SCORCHING", ["warm", "cool", "freezing", "mild"], "c",
                                     {"a": "same side", "b": "midpoint", "d": "midpoint"}, "Gradable: far end")

        n = self.narrate(
            id="ex1_01",
            text="Scorching: warm, cool, freezing, or mild? It's gradable, so take the far end. Warm is on the same side, "
                 "and cool and mild are midpoints. The answer is freezing.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(q.word, scale=1.1))
        self.at_word(n, "warm", occurrence=1)
        self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.2) for r in q.rows], lag_ratio=0.2))
        self.at_word(n, "gradable")
        self.play(FadeIn(tag, shift=LEFT * 0.1))
        self.at_word(n, "Warm", occurrence=2)
        self.play(*q.strike("a")[1])
        self.at_word(n, "midpoints")
        self.play(*q.strike("b")[1], *q.strike("d")[1])
        self.at_word(n, "answer")
        self.play(*q.confirm()[1])
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_ex_scorching")

    def example_present(self):
        self.scene_start("S06_ex_present", title="Worked Example 2")

        q, tag = self.option_example("PRESENT (in class)", ["gift", "absent", "late", "current"], "b",
                                     {"a": "a different meaning", "c": "trap: not the other state",
                                      "d": "a different meaning"}, "Complementary: other state")

        n = self.narrate(
            id="ex2_01",
            text="Present, as in present in class: gift, absent, late, or current? It's complementary: you're either there "
                 "or you're not. Late is a trap, and gift and current are other meanings of present. The answer is "
                 "absent.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(q.word, scale=1.1))
        self.at_word(n, "gift", occurrence=1)
        self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.2) for r in q.rows], lag_ratio=0.2))
        self.at_word(n, "complementary")
        self.play(FadeIn(tag, shift=LEFT * 0.1))
        self.at_word(n, "Late", occurrence=2)
        self.play(*q.strike("c")[1])
        self.at_word(n, "gift", occurrence=2)
        self.play(*q.strike("a")[1], *q.strike("d")[1])
        self.at_word(n, "answer")
        self.play(*q.confirm()[1])
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_ex_present")

    def example_lend(self):
        self.scene_start("S07_ex_lend", title="Worked Example 3")

        q, tag = self.option_example("LEND", ["give", "borrow", "loan", "spend"], "b",
                                     {"a": "same side", "c": "same side", "d": "unrelated"}, "Relational: partner")

        n = self.narrate(
            id="ex3_01",
            text="Lend: give, borrow, loan, or spend? It's relational, so pick the partner role. Loan and give are on the "
                 "same side as lend. The answer is borrow.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(q.word, scale=1.1))
        self.at_word(n, "give", occurrence=1)
        self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.2) for r in q.rows], lag_ratio=0.2))
        self.at_word(n, "relational")
        self.play(FadeIn(tag, shift=LEFT * 0.1))
        self.at_word(n, "Loan", occurrence=2)
        self.play(*q.strike("c")[1], *q.strike("a")[1], *q.strike("d")[1])
        self.at_word(n, "answer")
        self.play(*q.confirm()[1])
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S07_ex_lend")

    # ================================================ 8. RULES ==========

    def rules(self):
        self.scene_start("S08_rules", title="Rules")

        table = self.table_rows(["Type", "Test", "Pick"], [
            ["Gradable", "can you say “very X” or “X-er”?", "the far end of the scale"],
            ["Complementary", "does “not X” automatically mean Y?", "the only other state"],
            ["Relational", "does one role need the other?", "the partner role"],
        ], [3.0, 5.2, 3.6], size=LABEL)
        for row, (_, c, _, _) in zip(table[1:], TYPES):
            row[0].set_color(c)
        board = self.card(table, width=SAFE_W - 0.2).move_to(UP * 0.3)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="rules_01",
            text="One test for each type. Gradable: can you say very X, or X-er? Then pick the far end of the scale. "
                 "Complementary: does not X automatically mean Y? Then pick the only other state. Relational: does one "
                 "role need the other? Then pick the partner role.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(board[0]), FadeIn(table[0]))
        for row, spoken in zip(table[1:], ["Gradable", "Complementary", "Relational"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.45)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S08_rules")

    # ============================================== 9. PROCESS ==========

    def process(self):
        self.scene_start("S09_process", title="The Process")

        steps = VGroup(*[VGroup(pill(str(i + 1), c, size=SMALL), fitted_text(s_, SAFE_W - 2.2, BODY, INK))
                         .arrange(RIGHT, buff=0.3) for i, (s_, c) in enumerate([
                             ("Identify the word's core meaning", WORD),
                             ("Decide its type: dimmer, switch or coin", RATIO),
                             ("Predict: far end, other state or partner role", SECOND),
                             ("Eliminate midpoints and same-side words, then confirm", GOOD)])])
        steps.arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        board = self.card(steps).move_to(UP * 0.3)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="process_01",
            text="The process. Identify the word's core meaning. Decide its type: dimmer, switch or coin. Predict the far "
                 "end, the other state, or the partner role. Then eliminate midpoints and same-side words, and confirm.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(board[0]))
        for r, spoken in zip(steps, ["Identify", "Decide", "Predict", "eliminate"]):
            self.at_word(n, spoken)
            self.play(FadeIn(r, shift=RIGHT * 0.2), run_time=0.45)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S09_process")

    # ========================================== 10. HOOK, SOLVED ==========

    def hook_solved(self):
        self.scene_start("S10_hook_solved", title="Hook, Solved")

        h = self.HOOK
        q = OptionQuestion(h["word"], h["options"], h["key"], h["traps"], word_size=BODY)
        q.group.to_edge(LEFT, buff=SAFE + 0.6).to_edge(UP, buff=SAFE + 0.4)
        predict = pill("no middle  =  complementary: “not X” must equal Y", STEP_COLS["PREDICT"], size=SMALL)
        predict.to_edge(RIGHT, buff=SAFE + 0.2).align_to(q.word, UP)
        fit_width(predict, 6.0)
        verdict = pill("a test that didn't pass has failed: no “sort of passed”", GOOD, size=LABEL)
        fit_width(verdict, SAFE_W)
        verdict.to_edge(DOWN, buff=SAFE + 0.4)
        self.no_overlap(q.group, verdict)
        self.no_overlap(q.word, predict)
        self.validator.check_in_frame(VGroup(q.group, predict, verdict))

        n = self.narrate(
            id="solved_01",
            text="Let's solve the hook. Predict: no middle means complementary. Not X must equal Y.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(q.word), FadeIn(q.rows))
        self.at_word(n, "Predict")
        self.play(FadeIn(predict, shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_02",
            text="Eliminate. Hot and cold have warm and cool between them. Rich and poor have comfortable. Happy and sad "
                 "have content.",
            voice="default",
            subtitle=True,
        )
        for letter, spoken in [("a", "Hot"), ("c", "Rich"), ("d", "Happy")]:
            self.at_word(n, spoken)
            self.play(*q.strike(letter)[1])
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_03",
            text="Confirm: pass and fail. A test that didn't pass has failed. There's no sort of passed.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "pass", occurrence=1)
        self.play(*q.confirm()[1])
        self.at_word(n, "failed")
        self.play(FadeIn(verdict, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S10_hook_solved")

    # ========================================== 11. EXAM PATTERNS ==========

    def exam_patterns(self):
        self.scene_start("S11_patterns", title="Exam Patterns and Solving Models")

        table = self.table_rows(["Pattern", "Solving model"], [
            ["Strong gradable word (furious, scorching)", "the far end, with matching strength"],
            ["Midpoint in the options", "reject it: it's not the opposite"],
            ["Role word (employer, creditor)", "the partner role (employee, debtor)"],
        ], [5.6, 6.2], size=LABEL)
        board = self.card(table, width=SAFE_W - 0.2).move_to(UP * 0.4)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="patterns_01",
            text="Three exam patterns. A strong gradable word, like furious or scorching: choose the far end, with matching "
                 "strength. A midpoint in the options: reject it, because it's not the opposite. And a role word, like "
                 "employer or creditor: choose the partner role, employee or debtor.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(board[0]), FadeIn(table[0]))
        for row, spoken in zip(table[1:], ["strong", "midpoint", "role"]):
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
            (self.verdict_card(False, "A midpoint: cool for hot", card_w),
             self.verdict_card(True, "The far end: cold", card_w)),
            (self.verdict_card(False, "Same side: loan for lend", card_w),
             self.verdict_card(True, "The partner: borrow", card_w)),
            (self.verdict_card(False, "Strength ignored: happy for miserable", card_w),
             self.verdict_card(True, "Strong word, strong opposite: elated", card_w)),
        ]
        for (wrong, right), yy in zip(pairs, [1.6, 0.05, -1.5]):
            wrong.move_to(LEFT_ZONE + UP * yy)
            right.move_to(RIGHT_ZONE + UP * yy)
        header = pill("3 mistakes", BAD, size=LABEL).move_to(UP * (CARD_TOP - 0.3))
        self.validator.check_in_frame(VGroup(header, *[c for p in pairs for c in p]))

        n = self.narrate(
            id="mistakes_01",
            text="Three common mistakes. The first is choosing a midpoint, like cool for hot. The second is choosing a "
                 "same-side word in a relational pair, like loan for lend. The third is ignoring strength: happy as the "
                 "opposite of miserable is acceptable, but elated is better if it's offered with a strong word.",
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
        ("CREDITOR", ["lender", "banker", "debtor", "investor"], "c",
         {"a": "same side", "b": "same side", "d": "same side"}, "Relational: the one who lends / the one who owes"),
        ("ANCIENT", ["old", "recent", "historic", "modern"], "d",
         {"a": "synonym", "b": "close, not the standard opposite", "c": "same side"},
         "Gradable: the far end. Recent is close; modern is standard"),
        ("VISIBLE", ["invisible", "seen", "clear", "faint"], "a",
         {"b": "synonym", "c": "synonym", "d": "midpoint"}, "Complementary: faint is a midpoint"),
    ]

    def practice(self):
        self.scene_start("S13_practice", title="Practice Questions")

        head = pill("Choose the OPPOSITE", BAD, size=LABEL)
        lines = VGroup(*[VGroup(pill(str(i + 1), FOCUS, size=SMALL), pill(w, WORD, size=LABEL),
                                text("   ".join(f"({l}) {o}" for l, o in zip("abcd", opts)), LABEL, INK))
                         .arrange(RIGHT, buff=0.35) for i, (w, opts, *_r) in enumerate(self.PRACTICE)])
        lines.arrange(DOWN, buff=0.5, aligned_edge=LEFT)
        board = self.card(VGroup(head, lines).arrange(DOWN, buff=0.5, aligned_edge=LEFT), color=FOCUS)
        fit_width(board, SAFE_W)
        board.move_to(UP * 0.4)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="practice_01",
            text="Your turn: choose the opposite. One: creditor. Lender, banker, debtor, or investor? Two: ancient. Old, "
                 "recent, historic, or modern? Three: visible. Invisible, seen, clear, or faint?",
            voice="default",
            subtitle=True,
            pause_after=10.0,
        )
        self.play(FadeIn(board[0]), FadeIn(head))
        for ln, spoken in zip(lines, ["creditor", "ancient", "visible"]):
            self.at_word(n, spoken)
            self.play(FadeIn(ln, shift=UP * 0.15), run_time=0.5)
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        self.clear_stage()
        self.scene_end("S13_practice")

    # =============================================== 14. ANSWERS ==========

    def answers(self):
        self.scene_start("S14_answers", title="Answers")

        rows = VGroup()
        for w, opts, key, traps, note in self.PRACTICE:
            OptionQuestion(w, opts, key, traps)            # validates key / traps
            kind = note.split(":")[0]
            rows.add(VGroup(pill(w, WORD, size=LABEL), text("↔", LABEL, MUTED),
                            pill(f"({key}) {opts['abcd'.index(key)]}", GOOD, size=LABEL),
                            text(note, SMALL, TYPE_COL[kind])).arrange(RIGHT, buff=0.3))
        rows.arrange(DOWN, buff=0.45, aligned_edge=LEFT)
        fit_width(rows, SAFE_W).move_to(UP * 0.3)
        self.validator.check_in_frame(rows)

        n = self.narrate(
            id="answers_01",
            text="One: debtor. It's relational: the one who lends, and the one who owes. Two: modern, the far end of the "
                 "scale. Recent is close, but modern is the standard opposite. Three: invisible. It's complementary, and "
                 "faint is a midpoint.",
            voice="default",
            subtitle=True,
        )
        for r, spoken in zip(rows, ["debtor", "modern", "invisible"]):
            self.at_word(n, spoken)
            self.play(FadeIn(r, shift=RIGHT * 0.2), run_time=0.6)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S14_answers")

    # ================================================ 15. RECAP ==========

    def recap(self):
        self.scene_start("S15_recap", title="Recap Card")

        card, table = self.recap_card("Recap Card: Video 2", [
            ["Gradable", "a scale with a middle (hot – cold): pick the far end"],
            ["Complementary", "no middle (pass – fail): pick the other state"],
            ["Relational", "two roles (lend – borrow): pick the partner"],
            ["Traps", "midpoints and same-side words"],
        ])
        card.move_to(UP * 0.2)
        self.validator.check_in_frame(card)

        n = self.narrate(
            id="recap_01",
            text="To recap. Gradable: a scale with a middle, so pick the far end. Complementary: no middle, so pick the "
                 "other state. Relational: two roles, so pick the partner. And the traps are midpoints and same-side "
                 "words.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(card[0]), FadeIn(table[0]))
        for row, spoken in zip(table[1:], ["Gradable", "Complementary", "Relational", "traps"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.45)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S15_recap")

    # ================================================= 16. NEXT ==========

    def next_video(self):
        self.scene_start("S16_next", title="Next")

        word = pill("light", WORD, size=TITLE)
        opps = VGroup(pill("a light bag  ↔  heavy", RATIO, size=LABEL), pill("a light room  ↔  dark", SECOND, size=LABEL))\
            .arrange(RIGHT, buff=0.6)
        nxt = pill("Next:  Context-Based Antonyms", FOCUS, size=LABEL)
        VGroup(word, opps, nxt).arrange(DOWN, buff=0.7).move_to(UP * 0.2)
        self.no_overlap(word, opps, nxt)
        self.validator.check_in_frame(VGroup(word, opps, nxt))

        n = self.narrate(
            id="next_01",
            text="One word can have several opposites, depending on its meaning in the sentence. Video three handles that.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "word")
        self.play(FadeIn(word, scale=1.1))
        self.at_word(n, "several")
        self.play(FadeIn(opps, shift=UP * 0.1))
        self.at_word(n, "Video")
        self.play(FadeIn(nxt, scale=1.05))
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S16_next")

"""
animation.py for the LMS video generator.

Course : C-CAT - Section A - English
Module : Module 1 - Vocabulary
Lesson : Lesson 5 - Analogies
Video  : 06 - Exam-Oriented Analogies (Video 6 of 7)

Source script:
  C:\\Users\\User\\Downloads\\C-CAT_SectionA_Module1_English\\English\\Module 1 - Vocabulary\\
  Lesson 5 - Analogies\\06 - Exam-Oriented Analogies.pdf

Built on the golden-reference pattern:
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``;
  * layouts stacked with next_to and guarded with ``no_overlap``; nothing is
    ever animated onto or into another box.

The five pools of pairs exams reuse live in POOLS (with each pool's bridge); pool_of(first, second) finds a pair's pool, and odd_pair(pairs, test) bridges every pair and returns the single one that fails. The hook, the odd-pair worked example and the practice answers are computed with these.
The "three formats" card (missing term, choose the pair, odd pair out) stays pinned top-right through the worked examples and Hook, Solved; the format in use lights up.
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

# The pools exams reuse (the script's Rules table): pool -> (bridge, [(first, second), ...]).
POOLS = {
    "Instruments": ("measures", [("ammeter", "current"), ("voltmeter", "voltage"), ("barometer", "pressure"),
                                 ("hygrometer", "humidity"), ("odometer", "distance"),
                                 ("seismograph", "earthquakes")]),
    "Young": ("has a young one called a", [("cow", "calf"), ("dog", "puppy"), ("cat", "kitten"), ("horse", "foal"),
                                           ("lion", "cub"), ("sheep", "lamb")]),
    "Homes": ("lives in a", [("lion", "den"), ("bee", "hive"), ("horse", "stable"), ("dog", "kennel"),
                             ("spider", "web"), ("bird", "nest")]),
    "Groups": ("is a group of", [("flock", "sheep"), ("pack", "wolves"), ("swarm", "bees"), ("school", "fish"),
                                 ("herd", "cattle")]),
    "Fields": ("are studied in", [("birds", "ornithology"), ("insects", "entomology"), ("earth", "geology"),
                                  ("stars", "astronomy")]),
}
POOL_COL = dict(zip(POOLS, [RATIO, GOOD, WORD, SECOND, FOCUS]))
# Exact measures used by the hook (a speedometer and a thermometer are not in the script's table).
MEASURES = dict(POOLS["Instruments"][1] + [("speedometer", "speed"), ("thermometer", "temperature")])


def pool_of(first, second):
    """The pool that contains this pair in this order, or None."""
    for name, (_bridge, pairs) in POOLS.items():
        if (first, second) in pairs:
            return name
    return None


def odd_pair(pairs, keeps_bridge):
    """Odd pair out: bridge every pair; exactly one fails."""
    odd = [p for p in pairs if not keeps_bridge(*p)]
    assert len(odd) == 1, odd
    return odd[0]


def analogy_line(a, b, c, d="?", size=BODY):
    """A : B :: C : D as chips.  [0], [2] = first pair;  [4], [6] = second pair."""
    return VGroup(pill(a, WORD, size=size), text(":", size, MUTED), pill(b, WORD, size=size), text("::", size, MUTED),
                  pill(c, SECOND if c != "?" else FOCUS, size=size), text(":", size, MUTED),
                  pill(d, FOCUS if d == "?" else GOOD, size=size)).arrange(RIGHT, buff=0.25)


HOOK_PAIRS = [("ammeter", "current"), ("barometer", "pressure"), ("thermometer", "heat"), ("speedometer", "speed")]
assert odd_pair(HOOK_PAIRS, lambda x, y: MEASURES[x] == y) == ("thermometer", "heat")
YOUNG_PAIRS = [("cow", "calf"), ("dog", "puppy"), ("cat", "kitten"), ("horse", "stable")]
assert odd_pair(YOUNG_PAIRS, lambda x, y: pool_of(x, y) == "Young") == ("horse", "stable")
assert pool_of("horse", "stable") == "Homes"


class ExamOrientedAnalogiesVideo(LMSScene):
    lesson_title = "Exam-Oriented Analogies"

    def construct(self):
        self.camera.background_color = BG

        self.lesson_intro()
        self.hook()
        self.concept()
        self.why_you_need_it()
        self.analogy()
        self.example_missing_term()
        self.example_choose_pair()
        self.example_odd_pair()
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

    def table_rows(self, header, rows, widths, size=SMALL, max_lines=2):
        """A small table as a VGroup of rows (header first). Each cell is fitted
        to its column (wrapping to at most ``max_lines`` lines) and left-aligned
        at the column's left edge."""
        lefts, x = [], -sum(widths) / 2
        for w in widths:
            lefts.append(x)
            x += w
        out = VGroup()
        for i, cells in enumerate([header] + rows):
            color, weight = (FOCUS, BOLD) if i == 0 else (INK, NORMAL)
            row = VGroup(*[fitted_text(c, w - 0.3, size, color, weight, max_lines=max_lines)
                           for c, w in zip(cells, widths)])
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

    def format_pin(self):
        return self.steps_pin("three formats", [("MISSING TERM: bridge, fill", WORD),
                                                ("CHOOSE THE PAIR: test each", RATIO),
                                                ("ODD PAIR: bridge EVERY pair", BAD)])

    def pair_rows(self, pairs, size=BODY):
        """(a) X : Y rows for an odd-pair question."""
        rows = VGroup(*[VGroup(text(f"({l})", LABEL, MUTED), text(f"{x.capitalize()} : {y.capitalize()}", size, INK))
                        .arrange(RIGHT, buff=0.25) for l, (x, y) in zip("abcd", pairs)])
        return rows.arrange(DOWN, buff=0.3, aligned_edge=LEFT)

    def verdicts(self, rows, notes):
        """A ✓ / ✗ note to the right of each row."""
        return VGroup(*[text(note, SMALL, GOOD if ok else BAD).next_to(row, RIGHT, buff=0.5)
                        for row, (note, ok) in zip(rows, notes)])

    def quiz_card(self):
        head = text("PLACEMENT APTITUDE ROUND  ·  last question", SMALL, RATIO, BOLD)
        ask = text("Find the ODD PAIR OUT", BODY, INK, t2c={"ODD PAIR OUT": BAD})
        cx, w = self.free_area()
        body = VGroup(head, ask).arrange(DOWN, buff=0.2, aligned_edge=LEFT)
        fit_width(body, min(w - 1.4, SAFE_W - 1.8))
        card = self.card(body, width=min(w - 0.2, SAFE_W - 0.4))
        return card.move_to(RIGHT * cx + UP * (CARD_TOP - card.height / 2))

    # ========================================= 0. LESSON INTRO ==========

    def lesson_intro(self):
        self.scene_start("S00_intro", title="Lesson Introduction")

        crumb = self.breadcrumb("English · Module 1 Vocabulary", "Lesson 5 · Analogies", "Video 6")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        have = VGroup(*[VGroup(pill(t, c, size=LABEL), text(f"Video {i + 1}", SMALL, MUTED)).arrange(DOWN, buff=0.1)
                        for i, (t, c) in enumerate([("bridges", WORD), ("types", RATIO), ("refinement", GOOD),
                                                    ("context", SECOND), ("direction", BAD)])]).arrange(RIGHT, buff=0.3)
        fit_width(have, SAFE_W)
        formats = pill("today: the FORMATS exams use", FOCUS, size=LABEL)
        reuse = pill("…and the PAIRS they reuse", RATIO, size=LABEL)
        VGroup(have, formats, reuse).arrange(DOWN, buff=0.55).move_to(DOWN * 0.1)
        self.no_overlap(crumb, have, formats, reuse)
        self.validator.check_in_frame(VGroup(crumb, have, formats, reuse))

        n = self.narrate(
            id="intro_01",
            text="You now have bridges, types, refinement, context and direction. Today we apply them to the formats exams "
                 "use, and the pairs they reuse.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.at_word(n, "bridges")
        self.play(LaggedStart(*[FadeIn(h, shift=UP * 0.1) for h in have], lag_ratio=0.3), run_time=2.5)
        self.at_word(n, "formats")
        self.play(FadeIn(formats, shift=UP * 0.1))
        self.at_word(n, "pairs")
        self.play(FadeIn(reuse, shift=UP * 0.1))
        self.wait_for_narration(n)

        title = fitted_text("Exam-Oriented Analogies", SAFE_W, 72, INK, BOLD)
        underline = Line(LEFT, RIGHT, color=RATIO, stroke_width=5).set_width(title.width * 0.6)
        VGroup(title, underline).arrange(DOWN, buff=0.2).move_to(UP * 0.2)
        goals = [("Solve the three exam formats: missing term, choose the pair, odd pair out", BAD),
                 ("Learn the high-frequency analogy pairs", GOOD)]
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
            text="These are the exam-oriented analogies. By the end of this video, you'll solve the three exam formats: "
                 "missing term, choose the pair, and odd pair out; and learn the high-frequency analogy pairs.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(VGroup(have, formats, reuse), shift=UP * 0.3))
        self.at_word(n, "exam-oriented")
        self.play(Write(title), run_time=1.1)
        self.play(GrowFromCenter(underline))
        self.at_word(n, "By")
        self.play(FadeOut(underline), ReplacementTransform(title, small_title), run_time=0.8)
        self.play(FadeIn(objectives[0]), FadeIn(heading))
        for row_, spoken in zip(rows, ["solve", "learn"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row_, shift=RIGHT * 0.2), run_time=0.5)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_intro")

    # ================================================= 1. HOOK ==========

    def hook(self):
        self.scene_start("S01_hook", title="Hook")

        quiz = self.quiz_card()
        rows = self.pair_rows(HOOK_PAIRS).arrange_in_grid(rows=2, cols=2, buff=(1.6, 0.4), cell_alignment=LEFT)
        notes = VGroup(pill("three pairs share an EXACT relationship", GOOD, size=SMALL),
                       pill("one is almost right: that's the odd one", BAD, size=SMALL)).arrange(RIGHT, buff=0.4)
        fit_width(notes, SAFE_W)
        rows.next_to(quiz, DOWN, buff=0.7)
        notes.next_to(rows, DOWN, buff=0.6)
        self.no_overlap(quiz, rows, notes)
        self.validator.check_in_frame(VGroup(quiz, rows, notes))

        n = self.narrate(
            id="hook_01",
            text="The last question of a placement aptitude round: find the odd pair out.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "last")
        self.play(FadeIn(quiz[0]), FadeIn(quiz[1][0]))
        self.at_word(n, "odd")
        self.play(FadeIn(quiz[1][1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_02",
            text="Ammeter, current; barometer, pressure; thermometer, heat; or speedometer, speed? Three pairs share an "
                 "exact relationship. One is almost right, and that's the odd one.",
            voice="default",
            subtitle=True,
            pause_after=3.0,
        )
        for row, spoken in zip(rows, ["Ammeter", "barometer", "thermometer", "speedometer"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=UP * 0.15), run_time=0.35)
        self.at_word(n, "Three")
        self.play(FadeIn(notes[0], shift=UP * 0.1))
        self.at_word(n, "almost")
        self.play(FadeIn(notes[1], shift=UP * 0.1))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        self.clear_stage()
        self.scene_end("S01_hook")

    # ============================================== 2. CONCEPT ==========

    def concept(self):
        self.scene_start("S02_concept", title="The Concept")

        head = pill("exams use THREE formats", FOCUS, size=LABEL)
        head.move_to(UP * (CARD_TOP - head.height / 2))
        formats = VGroup(*[VGroup(VGroup(pill(name, c, size=LABEL), text(shape, LABEL, INK)).arrange(RIGHT, buff=0.35),
                                  text(how, SMALL, c)).arrange(DOWN, buff=0.12, aligned_edge=LEFT)
                           for name, shape, how, c in [
                               ("missing term", "A : B :: C : ?", "bridge from A–B, fill in C's partner", WORD),
                               ("choose the pair", "A : B :: ? : ?",
                                "bridge from A–B, test every option pair; watch for reversed pairs", RATIO),
                               ("odd pair out", "four pairs, three share a relationship",
                                "bridge each pair: the one whose bridge differs is the answer", BAD)]])
        formats.arrange(DOWN, buff=0.4, aligned_edge=LEFT)
        nearly = text("often the odd pair is NEARLY the same type, but fails one refinement", SMALL, MUTED)
        body = VGroup(formats, nearly).arrange(DOWN, buff=0.35, aligned_edge=LEFT)
        fit_within(body, SAFE_W, SAFE_H - head.height - 1.6)
        body.next_to(head, DOWN, buff=0.5)
        self.no_overlap(head, formats, nearly)
        self.validator.check_in_frame(VGroup(head, body))

        n = self.narrate(
            id="concept_01",
            text="Exams use three formats.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "three")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_02",
            text="Missing term: A is to B, as C is to what? Bridge from A and B, and fill in C's partner.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Missing")
        self.play(FadeIn(formats[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "Bridge")
        self.play(FadeIn(formats[0][1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_03",
            text="Choose the pair: A is to B, as what is to what? Bridge from A and B, then test every option pair, and "
                 "watch for reversed pairs.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Choose")
        self.play(FadeIn(formats[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "Bridge")
        self.play(FadeIn(formats[1][1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_04",
            text="Odd pair out: four pairs, and three share a relationship. Bridge each pair; the one whose bridge differs "
                 "is the answer. Often the odd pair is nearly the same type, but fails one refinement.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Odd", occurrence=1)
        self.play(FadeIn(formats[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "Bridge", occurrence=1)
        self.play(FadeIn(formats[2][1], shift=UP * 0.1))
        self.at_word(n, "nearly")
        self.play(FadeIn(nearly, shift=UP * 0.1))
        self.wait_for_narration(n)

        # The pools.
        pool_head = pill("the pairs come from a familiar pool", RATIO, size=LABEL)
        pool_head.move_to(UP * (CARD_TOP - pool_head.height / 2))
        pools = VGroup(*[VGroup(pill(name, POOL_COL[name], size=LABEL),
                                text("  ·  ".join(f"{x} : {y}" for x, y in pairs[:2]) + "  …", LABEL, INK))
                         .arrange(RIGHT, buff=0.35) for name, (_b, pairs) in POOLS.items()])
        pools.arrange(DOWN, buff=0.35, aligned_edge=LEFT)
        fit_within(pools, SAFE_W, SAFE_H - pool_head.height - 1.6)
        pools.next_to(pool_head, DOWN, buff=0.6)
        self.no_overlap(pool_head, pools)
        self.validator.check_in_frame(VGroup(pool_head, pools))
        n = self.narrate(
            id="concept_05",
            text="The pairs themselves are drawn from a familiar pool: instruments and what they measure, animals and "
                 "their young, animals and their homes, groups of animals, and scientific fields.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(VGroup(head, body)))
        self.at_word(n, "pool")
        self.play(FadeIn(pool_head, shift=DOWN * 0.2))
        for p, spoken in zip(pools, ["instruments", "young", "homes", "groups", "fields"]):
            self.at_word(n, spoken)
            self.play(FadeIn(p, shift=RIGHT * 0.2), run_time=0.4)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_concept")

    # ======================================== 3. WHY YOU NEED IT ==========

    def why_you_need_it(self):
        self.scene_start("S03_why", title="Why You Need It")

        hardest = pill("odd-pair questions: the hardest analogy format", BAD, size=LABEL)
        alike = pill("…because three pairs look alike", RATIO, size=LABEL)
        fix = pill("know the common pools + refine each bridge  →  manageable", GOOD, size=LABEL)
        group = VGroup(hardest, alike, fix).arrange(DOWN, buff=0.7)
        fit_width(group, SAFE_W).move_to(UP * 0.3)
        self.no_overlap(hardest, alike, fix)
        self.validator.check_in_frame(group)

        n = self.narrate(
            id="why_01",
            text="Odd-pair questions are the hardest analogy format, because three pairs look alike. Knowing the common "
                 "pools, and refining each bridge, makes them manageable.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "hardest")
        self.play(FadeIn(hardest, shift=DOWN * 0.1))
        self.at_word(n, "alike")
        self.play(FadeIn(alike, shift=UP * 0.1))
        self.at_word(n, "pools")
        self.play(FadeIn(fix, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_why")

    # ============================================== 4. ANALOGY ==========

    def analogy(self):
        self.scene_start("S04_analogy", title="The Analogy")

        lock = pill("the lock = one bridge:  “the young of”", WORD, size=LABEL)
        lock.move_to(UP * (CARD_TOP - lock.height / 2 - 0.2))
        odd = odd_pair(YOUNG_PAIRS, lambda x, y: pool_of(x, y) == "Young")
        keys = VGroup(*[VGroup(pill(f"{x} : {y}", MUTED, size=LABEL),
                               text("✗  doesn't turn" if (x, y) == odd else "✓  turns", SMALL,
                                    BAD if (x, y) == odd else GOOD)).arrange(DOWN, buff=0.15)
                        for x, y in YOUNG_PAIRS]).arrange(RIGHT, buff=0.5, aligned_edge=UP)
        fit_width(keys, SAFE_W - 0.6)
        keys.next_to(lock, DOWN, buff=0.9)
        answer = pill("the key that doesn't turn is the answer", FOCUS, size=LABEL)
        answer.next_to(keys, DOWN, buff=0.7)
        self.no_overlap(lock, keys, answer)
        self.validator.check_in_frame(VGroup(lock, keys, answer))

        n = self.narrate(
            id="analogy_01",
            text="Odd pair out is four keys, where three open the same lock. Try each key with the same bridge. The one "
                 "that doesn't turn is the answer.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "keys")
        self.play(LaggedStart(*[FadeIn(k[0], shift=UP * 0.1) for k in keys], lag_ratio=0.2))
        self.at_word(n, "lock")
        self.play(FadeIn(lock, shift=DOWN * 0.1))
        self.at_word(n, "Try")
        self.play(LaggedStart(*[FadeIn(k[1], shift=UP * 0.1) for k in keys[:3]], lag_ratio=0.3))
        self.at_word(n, "turn")
        self.play(FadeIn(keys[3][1], shift=UP * 0.1), FadeIn(answer, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_analogy")

    # ======================================== 5-7. WORKED EXAMPLES ==========

    def example_missing_term(self):
        self.scene_start("S05_ex_missing_term", title="Worked Example 1: Missing Term")
        self.play(self.pin(self.format_pin()))

        assert pool_of("lion", "den") == pool_of("bee", "hive") == "Homes"
        cx, w = self.free_area()
        tag = pill("format 1:  missing term", WORD, size=SMALL)
        line = analogy_line("Lion", "Den", "Bee")
        b1 = text("“A lion lives in a den.”", LABEL, INK, t2c={"lives in": RATIO})
        b2 = text("“A bee lives in a hive.”", LABEL, INK, t2c={"lives in": RATIO, "hive": GOOD})
        block = VGroup(tag, line, b1, b2).arrange(DOWN, buff=0.5, aligned_edge=LEFT)
        fit_within(block, w - 0.6, SAFE_H - 1.8)
        self.place_free(block, y=0.2)
        answer = pill("hive", GOOD, size=BODY).scale(line[6].height / pill("?", FOCUS, size=BODY).height)
        answer.move_to(line[6], aligned_edge=LEFT)
        self.no_overlap(tag, line, b1, b2)
        self.validator.check_in_frame(VGroup(block, answer))

        n = self.narrate(
            id="ex1_01",
            text="Format one: the missing term. Lion is to den, as bee is to what? Bridge: a lion lives in a den. So a bee "
                 "lives in a hive.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "missing")
        self.play(FadeIn(tag, shift=DOWN * 0.1), self.pin_step(0, color=WORD))
        self.at_word(n, "Lion", occurrence=1)
        self.play(FadeIn(line, shift=UP * 0.1))
        self.at_word(n, "Bridge")
        self.play(FadeIn(b1, shift=RIGHT * 0.2))
        self.at_word(n, "hive")
        self.play(FadeIn(b2, shift=RIGHT * 0.2), ReplacementTransform(line[6], answer))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_ex_missing_term")

    def example_choose_pair(self):
        self.scene_start("S06_ex_choose_pair", title="Worked Example 2: Choose the Pair")

        cx, w = self.free_area()
        tag = pill("format 2:  choose the pair", RATIO, size=SMALL)
        line = analogy_line("Doctor", "Patient", "?", size=LABEL)
        bridge_ = VGroup(pill("bridge", WORD, size=SMALL), text("a doctor serves a patient:  professional → person served",
                                                                 LABEL, INK)).arrange(RIGHT, buff=0.25)
        fit_width(bridge_, w - 0.8)
        q = OptionQuestion("?", ["Lawyer : Client", "Client : Lawyer"], "a", {"b": "person served → professional:  REVERSED"},
                           word_size=LABEL)
        block = VGroup(tag, line, bridge_, q.rows).arrange(DOWN, buff=0.45, aligned_edge=LEFT)
        fit_height(block, SAFE_H - 1.6)
        block.to_edge(LEFT, buff=SAFE + 0.6).set_y(0.1)
        self.no_overlap(tag, line, bridge_, q.rows)
        self.no_overlap(block, self.pinned)
        self.validator.check_in_frame(block)

        n = self.narrate(
            id="ex2_01",
            text="Format two: choose the pair. Doctor is to patient, as what is to what? Lawyer, client, or client, lawyer? "
                 "Bridge: a doctor serves a patient: the professional, then the person served. Client, lawyer is "
                 "reversed. The answer is lawyer, client.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "choose")
        self.play(FadeIn(tag, shift=DOWN * 0.1), self.pin_step(1, color=RATIO))
        self.at_word(n, "Doctor", occurrence=1)
        self.play(FadeIn(line, shift=UP * 0.1))
        self.at_word(n, "Lawyer", occurrence=1)
        self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.2) for r in q.rows], lag_ratio=0.3))
        self.at_word(n, "Bridge")
        self.play(FadeIn(bridge_, shift=RIGHT * 0.2))
        self.at_word(n, "reversed")
        self.play(*q.strike("b")[1])
        self.at_word(n, "answer")
        self.play(*q.confirm()[1])
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_ex_choose_pair")

    def example_odd_pair(self):
        self.scene_start("S07_ex_odd_pair", title="Worked Example 3: Odd Pair Out")

        odd = odd_pair(YOUNG_PAIRS, lambda x, y: pool_of(x, y) == "Young")
        cx, w = self.free_area()
        tag = pill("format 3:  odd pair out", BAD, size=SMALL)
        rows = self.pair_rows(YOUNG_PAIRS)
        block = VGroup(tag, rows).arrange(DOWN, buff=0.5, aligned_edge=LEFT)
        marks = self.verdicts(rows, [("✓  the young of a " + x, True) if (x, y) != odd
                                     else (f"✗  the HOME of a {x}: a different bridge", False) for x, y in YOUNG_PAIRS])
        # Rows + notes together must fit beside the pinned card: fit the whole group, then place it.
        content = VGroup(block, marks)
        fit_within(content, w - 0.4, SAFE_H - 1.8)
        self.place_free(content, y=0.1)          # centres in the free area and runs no_overlap vs the pin
        box = SurroundingRectangle(rows[YOUNG_PAIRS.index(odd)], color=BAD, buff=0.12, corner_radius=0.1)
        self.no_overlap(tag, rows)
        self.validator.check_in_frame(content)

        n = self.narrate(
            id="ex3_01",
            text="Format three: the odd pair out. Cow, calf; dog, puppy; cat, kitten; horse, stable. Bridge every pair. A "
                 "calf is the young of a cow. A puppy is the young of a dog. A kitten is the young of a cat. But a stable "
                 "is the home of a horse. That's the odd pair.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "odd", occurrence=1)
        self.play(FadeIn(tag, shift=DOWN * 0.1), self.pin_step(2, color=BAD))
        self.at_word(n, "Cow", occurrence=1)
        self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.2) for r in rows], lag_ratio=0.3), run_time=2.0)
        self.at_word(n, "Bridge")
        self.play(Indicate(rows, color=WORD, scale_factor=1.02))
        for mark, (spoken, occ) in zip(marks, [("calf", 2), ("puppy", 2), ("kitten", 2), ("stable", 2)]):
            self.at_word(n, spoken, occurrence=occ)
            self.play(FadeIn(mark, shift=LEFT * 0.1), run_time=0.4)
        self.at_word(n, "odd", occurrence=2)
        self.play(Create(box))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S07_ex_odd_pair")

    # ================================================ 8. RULES ==========

    def rules(self):
        self.scene_start("S08_rules", title="Rules: The Pools")
        self.play(self.unpin())

        # The Instruments row is the longest: a tight separator, the full card width
        # (2.4 + 10.1 = the card's inner width) and up to 3 lines keep it at a readable size.
        table = self.table_rows(["Pool", "Pairs"], [[name, ", ".join(f"{x} : {y}" for x, y in pairs)]
                                                    for name, (_b, pairs) in POOLS.items()], [2.4, 10.1],
                                size=SMALL, max_lines=3)
        for row, name in zip(table[1:], POOLS):
            row[0].set_color(POOL_COL[name])
        board = self.card(table, width=SAFE_W - 0.2)
        fit_height(board, SAFE_H - 1.0)
        board.move_to(UP * 0.3)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="rules_01",
            text="Here are the pools that exams reuse. Instruments: ammeter, current; voltmeter, voltage; barometer, "
                 "pressure; hygrometer, humidity; odometer, distance; seismograph, earthquakes. Young: cow, calf; dog, "
                 "puppy; cat, kitten; horse, foal; lion, cub; sheep, lamb. Homes: lion, den; bee, hive; horse, stable; "
                 "dog, kennel; spider, web; bird, nest.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "pools")
        self.play(FadeIn(board[0]), FadeIn(table[0]))
        for row, spoken in zip(table[1:4], ["Instruments", "Young", "Homes"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.45)
        self.wait_for_narration(n)

        n = self.narrate(
            id="rules_02",
            text="Groups: flock, sheep; pack, wolves; swarm, bees; school, fish; herd, cattle. And fields: birds, "
                 "ornithology; insects, entomology; earth, geology; stars, astronomy.",
            voice="default",
            subtitle=True,
        )
        for row, spoken in zip(table[4:], ["Groups", "fields"]):
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
                             ("Identify the format", FOCUS),
                             ("Build and refine a bridge (odd pair: one bridge per pair)", WORD),
                             ("Check direction and level", RATIO),
                             ("Confirm", GOOD)])])
        steps.arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        board = self.card(steps).move_to(UP * 0.3)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="process_01",
            text="The process. Step one: identify the format. Step two: build and refine a bridge; for an odd pair, one "
                 "bridge per pair. Step three: check direction and level. And step four: confirm.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(board[0]))
        for r, (spoken, occ) in zip(steps, [("one", 1), ("two", 1), ("three", 1), ("four", 1)]):
            self.at_word(n, spoken, occurrence=occ)
            self.play(FadeIn(r, shift=RIGHT * 0.2), run_time=0.45)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S09_process")

    # ========================================== 10. HOOK, SOLVED ==========

    def hook_solved(self):
        self.scene_start("S10_hook_solved", title="Hook, Solved")
        self.play(self.pin(self.format_pin()))

        odd = odd_pair(HOOK_PAIRS, lambda x, y: MEASURES[x] == y)
        cx, w = self.free_area()
        quiz = self.quiz_card()
        bridge_ = pill("bridge:  “an X-meter measures X”", WORD, size=SMALL)
        bridge_.next_to(quiz, DOWN, buff=0.3).to_edge(LEFT, buff=SAFE + 0.6)
        rows = self.pair_rows(HOOK_PAIRS, size=LABEL)
        why = text("heat is energy;  temperature is its measure", SMALL, MUTED)
        body = VGroup(rows, why).arrange(DOWN, buff=0.35, aligned_edge=LEFT)
        fit_height(body, bridge_.get_bottom()[1] - 0.3 - (BOTTOM_Y + 0.6))
        body.next_to(bridge_, DOWN, buff=0.3).to_edge(LEFT, buff=SAFE + 0.6)
        marks = self.verdicts(rows, [(f"✓  measures {y}", True) if (x, y) != odd
                                     else (f"✗  measures {MEASURES[x].upper()}, not {y}", False)
                                     for x, y in HOOK_PAIRS])
        # Rows + notes must stay left of the pinned card: shrink the pair (about its left edge) if needed.
        right_limit = self.pinned.get_left()[0] - 0.3
        content = VGroup(body, marks)
        left = content.get_left()[0]
        if content.get_right()[0] > right_limit:
            content.scale((right_limit - left) / content.width, about_edge=LEFT)
        box = SurroundingRectangle(rows[HOOK_PAIRS.index(odd)], color=BAD, buff=0.1, corner_radius=0.1)
        self.no_overlap(quiz, bridge_, rows, why)
        self.no_overlap(quiz, self.pinned)
        self.no_overlap(bridge_, self.pinned)
        self.no_overlap(content, self.pinned)
        self.validator.check_in_frame(VGroup(quiz, bridge_, body, marks))

        n = self.narrate(
            id="solved_01",
            text="Let's solve the hook. Read: odd pair out. Predict the bridge: an X-meter measures X.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(quiz), FadeIn(rows))
        self.at_word(n, "Read")
        self.play(Indicate(quiz[1][1], color=BAD, scale_factor=1.03), self.pin_step(2, color=BAD))
        self.at_word(n, "bridge")
        self.play(FadeIn(bridge_, shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_02",
            text="Test every pair. An ammeter measures current. A barometer measures pressure. A speedometer measures "
                 "speed.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Test")
        self.play(Indicate(rows, color=WORD, scale_factor=1.02))
        for i, spoken in [(0, "ammeter"), (1, "barometer"), (3, "speedometer")]:
            self.at_word(n, spoken)
            self.play(FadeIn(marks[i], shift=LEFT * 0.1), run_time=0.4)
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_03",
            text="But a thermometer measures temperature, not heat. Heat is energy; temperature is its measure. So "
                 "thermometer, heat is the odd pair: a one-refinement difference.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "thermometer", occurrence=1)
        self.play(FadeIn(marks[2], shift=LEFT * 0.1))
        self.at_word(n, "energy")
        self.play(FadeIn(why, shift=UP * 0.1))
        self.at_word(n, "odd")
        self.play(Create(box))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S10_hook_solved")

    # ========================================== 11. EXAM PATTERNS ==========

    def exam_patterns(self):
        self.scene_start("S11_patterns", title="Exam Patterns and Solving Models")
        self.play(self.unpin())

        table = self.table_rows(["Pattern", "Solving model"], [
            ["Missing term", "bridge → fill"],
            ["Choose the pair", "bridge → test each pair → reject reversed pairs"],
            ["Odd pair out", "one bridge per pair; find the one that fails a refinement"],
        ], [4.2, 7.6], size=LABEL)
        board = self.card(table, width=SAFE_W - 0.2).move_to(UP * 0.4)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="patterns_01",
            text="Three exam patterns. Missing term: bridge, then fill. Choose the pair: bridge, test each pair, and reject "
                 "reversed pairs. And odd pair out: one bridge per pair; find the one that fails a refinement.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(board[0]), FadeIn(table[0]))
        for row, spoken in zip(table[1:], ["Missing", "Choose", "odd"]):
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
            (self.verdict_card(False, "Odd pair: not bridging every pair", card_w),
             self.verdict_card(True, "One bridge per pair", card_w)),
            (self.verdict_card(False, "heat = temperature", card_w),
             self.verdict_card(True, "heat: energy;  temperature: its measure", card_w)),
            (self.verdict_card(False, "Accepting reversed pairs", card_w),
             self.verdict_card(True, "Check the order in “choose the pair”", card_w)),
        ]
        for (wrong, right), yy in zip(pairs, [1.6, 0.05, -1.5]):
            wrong.move_to(LEFT_ZONE + UP * yy)
            right.move_to(RIGHT_ZONE + UP * yy)
        header = pill("3 mistakes", BAD, size=LABEL).move_to(UP * (CARD_TOP - 0.3))
        self.validator.check_in_frame(VGroup(header, *[c for p in pairs for c in p]))

        n = self.narrate(
            id="mistakes_01",
            text="Three common mistakes. The first, in odd-pair questions, is not bridging every pair. The second is "
                 "treating heat and temperature as the same. The third is accepting reversed pairs in choose-the-pair "
                 "questions.",
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

    ODD_Q = [("pack", "wolves"), ("den", "lion"), ("swarm", "bees"), ("herd", "cattle")]

    def practice(self):
        self.scene_start("S13_practice", title="Practice Questions")

        def options(items):
            return text("   ".join(f"({l}) {o}" for l, o in zip("abcd", items)), LABEL, INK)

        lines = VGroup(
            VGroup(VGroup(pill("1", FOCUS, size=SMALL), analogy_line("Entomology", "Insects", "Ornithology", size=LABEL))
                   .arrange(RIGHT, buff=0.35), options(["birds", "fish", "flowers", "bones"]))
            .arrange(DOWN, buff=0.2, aligned_edge=LEFT),
            VGroup(VGroup(pill("2", FOCUS, size=SMALL), pill("odd pair out", BAD, size=LABEL)).arrange(RIGHT, buff=0.35),
                   options([f"{x.capitalize()} : {y.capitalize()}" for x, y in self.ODD_Q]))
            .arrange(DOWN, buff=0.2, aligned_edge=LEFT),
            VGroup(VGroup(pill("3", FOCUS, size=SMALL), analogy_line("Horse", "Foal", "Sheep", size=LABEL))
                   .arrange(RIGHT, buff=0.35), options(["calf", "kid", "cub", "lamb"]))
            .arrange(DOWN, buff=0.2, aligned_edge=LEFT)).arrange(DOWN, buff=0.45, aligned_edge=LEFT)
        board = self.card(lines, color=FOCUS)
        fit_within(board, SAFE_W, SAFE_H - 1.2)
        board.move_to(UP * 0.4)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="practice_01",
            text="Your turn. One: entomology is to insects, as ornithology is to what? Birds, fish, flowers, or bones? "
                 "Two: find the odd pair out: pack, wolves; den, lion; swarm, bees; or herd, cattle? Three: horse is to "
                 "foal, as sheep is to what? Calf, kid, cub, or lamb?",
            voice="default",
            subtitle=True,
            pause_after=10.0,
        )
        self.play(FadeIn(board[0]))
        for ln, (spoken, first_option) in zip(lines, [("entomology", "Birds"), ("odd", "pack"), ("horse", "Calf")]):
            self.at_word(n, spoken)
            self.play(FadeIn(ln[0], shift=UP * 0.15), run_time=0.4)
            self.at_word(n, first_option)
            self.play(FadeIn(ln[1], shift=LEFT * 0.15), run_time=0.4)
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        self.clear_stage()
        self.scene_end("S13_practice")

    # =============================================== 14. ANSWERS ==========

    def answers(self):
        self.scene_start("S14_answers", title="Answers")

        assert pool_of("birds", "ornithology") == "Fields" and pool_of("sheep", "lamb") == "Young"
        odd = odd_pair(self.ODD_Q, lambda x, y: pool_of(x, y) == "Groups")
        assert odd == ("den", "lion") and pool_of("lion", "den") == "Homes"
        rows = VGroup(
            VGroup(analogy_line("Entomology", "Insects", "Ornithology", "birds", size=LABEL),
                   text("ornithology is the study of birds", SMALL, RATIO)).arrange(DOWN, buff=0.18, aligned_edge=LEFT),
            VGroup(VGroup(pill("odd pair", BAD, size=LABEL), pill("(b) Den : Lion", GOOD, size=LABEL))
                   .arrange(RIGHT, buff=0.3),
                   text("the others: a group and its members;  this one: a home and its animal", SMALL, RATIO))
            .arrange(DOWN, buff=0.18, aligned_edge=LEFT),
            VGroup(analogy_line("Horse", "Foal", "Sheep", "lamb", size=LABEL),
                   text("(b) a kid is the young of a goat", SMALL, BAD)).arrange(DOWN, buff=0.18, aligned_edge=LEFT))\
            .arrange(DOWN, buff=0.5, aligned_edge=LEFT)
        fit_within(rows, SAFE_W, SAFE_H - 1.2)
        rows.move_to(UP * 0.3)
        self.validator.check_in_frame(rows)

        n = self.narrate(
            id="answers_01",
            text="One: birds. Ornithology is the study of birds. Two: den, lion. The others are a group and its members; "
                 "this one is a home and its animal. Three: lamb. A kid is the young of a goat.",
            voice="default",
            subtitle=True,
        )
        for r, (spoken, why) in zip(rows, [("birds", "study"), ("den", "group"), ("lamb", "kid")]):
            self.at_word(n, spoken, occurrence=1)
            self.play(FadeIn(r[0], shift=RIGHT * 0.2), run_time=0.5)
            self.at_word(n, why)
            self.play(FadeIn(r[1], shift=LEFT * 0.1), run_time=0.4)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S14_answers")

    # ================================================ 15. RECAP ==========

    def recap(self):
        self.scene_start("S15_recap", title="Recap Card")

        card, table = self.recap_card("Recap Card: Video 6", [
            ["Formats", "missing term, choose the pair, odd pair out"],
            ["Odd pair", "bridge every pair; the odd one fails one refinement"],
            ["Pools", ", ".join(p.lower() for p in POOLS)],
        ])
        card.move_to(UP * 0.2)
        self.validator.check_in_frame(card)

        n = self.narrate(
            id="recap_01",
            text="To recap. Three formats: missing term, choose the pair, odd pair out. For an odd pair, bridge every pair; "
                 "the odd one fails one refinement. And know the pools: instruments, young, homes, groups, fields.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(card[0]), FadeIn(table[0]))
        for row, spoken in zip(table[1:], ["formats", "bridge", "pools"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.45)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S15_recap")

    # ================================================= 16. NEXT ==========

    def next_video(self):
        self.scene_start("S16_next", title="Next")

        method = pill("everything  →  one fast analogy method", GOOD, size=LABEL)
        nxt = pill("Next:  Analogy Question-Solving Techniques", FOCUS, size=LABEL)
        VGroup(method, nxt).arrange(DOWN, buff=0.8).move_to(UP * 0.2)
        self.no_overlap(method, nxt)
        self.validator.check_in_frame(VGroup(method, nxt))

        n = self.narrate(
            id="next_01",
            text="Video seven turns everything into one fast analogy method.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Video")
        self.play(FadeIn(nxt, scale=1.05))
        self.at_word(n, "method")
        self.play(FadeIn(method, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S16_next")
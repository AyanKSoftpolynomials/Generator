"""
animation.py for the LMS video generator.

Course : Pre-C-CAT - Section A - Quantitative Aptitude
Video  : Module Introduction - Why Aptitude?

Source script:
  C:\\Scripts\\Section A\\Module_2_Section_A_Quantitative_Aptitude_Part_1\\Aptitude_Scripts\\Sessions 1-4 - Interest, Profit & Loss, Time & Work\\00 - Module Introduction - Why Aptitude.pdf

Built on the golden-reference pattern:
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``;
  * layouts stacked with next_to and guarded with ``no_overlap``; nothing is
    ever animated onto or into another box.

Module opener. No spoken course welcome: a silent breadcrumb, then straight into the hook.
The script is prose notes, so the narration follows it sentence by sentence, with numbers written as words for the voice. The table and the three reasons are spoken one row at a time. All figures on screen (150 s, 100 s, 48 MB/s, 1/6 per minute, 6 minutes, the value of a guess) are computed from the given numbers and asserted.
The checkpoint question is followed by the script's 10-second countdown (pause_after=10).
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

from fractions import Fraction

# ---- Hook: the upload -------------------------------------------------------
DATA_MB, SPEEDS = 12000, (40, 60)                       # 12 GB, first half / second half in MB/s
HALF_MB = DATA_MB // 2
TIMES = tuple(HALF_MB // s for s in SPEEDS)             # seconds for each half
OBVIOUS = sum(SPEEDS) // 2                              # what everyone says
AVERAGE = DATA_MB // sum(TIMES)                         # total data / total time
assert TIMES == (150, 100) and OBVIOUS == 50 and AVERAGE == 48

# ---- C-CAT Section A ---------------------------------------------------------
TOTAL_Q, TOTAL_MIN, MARKS_RIGHT, MARKS_WRONG = 50, 60, 3, -1


def expected_marks(options_left):
    """Average marks for a guess among ``options_left`` options (+3 / −1 marking)."""
    p = Fraction(1, options_left)
    return p * MARKS_RIGHT + (1 - p) * MARKS_WRONG


assert expected_marks(4) == 0 and expected_marks(2) == 1

# ---- Checkpoint: two build servers ------------------------------------------
BUILD_MIN = (10, 15)                                    # server A, server B
RATES = tuple(Fraction(1, m) for m in BUILD_MIN)        # builds per minute
TOGETHER = sum(RATES)
BOTH_MIN = 1 / TOGETHER
assert TOGETHER == Fraction(1, 6) and BOTH_MIN == 6 and BOTH_MIN < min(BUILD_MIN)

REASONS = [("One scale for everyone", "degrees and grading systems differ; an aptitude test does not"),
           ("It mirrors real work", "estimating time, cost, load and growth is everyday engineering"),
           ("It reveals judgement", "time limits and negative marking show whether your method holds")]
EXAMS = ["C-CAT", "GATE General Aptitude", "placement tests", "bank and government exams"]
ABILITIES = [("Comprehension", "reading exactly what is asked"),
             ("Modelling", "turning words into one equation"),
             ("Numerical fluency", "1/8 = 12.5% without working"),
             ("Logic", "reasoning backwards from a condition"),
             ("Speed with accuracy", "about a minute per question"),
             ("Judgement", "knowing which question to skip")]
METHOD = [("READ", "what is asked?", "#4FC3F7"), ("MODEL", "words → numbers", "#CE93D8"),
          ("SOLVE", "step by step", "#FFB74D"), ("CHECK", "does it make sense?", "#66BB6A")]


def frac(f):
    return f"{f.numerator}/{f.denominator}"


def name_rows(items, color, buff=0.28):
    """One row per item: number chip, name, description.  Names and descriptions are column-aligned."""
    names = [text(name, LABEL, color, BOLD) for name, _ in items]
    gap = max(n.width for n in names) + 0.6
    rows = VGroup()
    for i, (name, (_, what)) in enumerate(zip(names, items)):
        num = pill(str(i + 1), color, size=SMALL)
        desc = text(what, LABEL, INK)
        name.next_to(num, RIGHT, buff=0.3)
        desc.next_to(num, RIGHT, buff=0.3 + gap)
        rows.add(VGroup(num, name, desc))
    return rows.arrange(DOWN, buff=buff, aligned_edge=LEFT)


def method_columns(with_details=True):
    """READ → MODEL → SOLVE → CHECK.  Columns are at [0], [2], [4], [6]; each is (chip, detail)."""
    parts = []
    for i, (name, detail, c) in enumerate(METHOD):
        if i:
            parts.append(text("→", LABEL, MUTED))
        col = VGroup(pill(name, c, size=LABEL))
        if with_details:
            col.add(text(detail, SMALL, INK))
            col.arrange(DOWN, buff=0.3)
        parts.append(col)
    cols = VGroup(*parts).arrange(RIGHT, buff=0.4, aligned_edge=UP)
    for i in range(1, len(cols), 2):                    # arrows level with the chips
        cols[i].set_y(cols[0][0].get_y())
    return cols


class WhyAptitudeVideo(LMSScene):
    lesson_title = "Why Aptitude?"

    def construct(self):
        self.camera.background_color = BG

        self.hook()
        self.what_is_aptitude()
        self.why_needed()
        self.what_it_tests()
        self.ccat_at_a_glance()
        self.the_method()
        self.checkpoint()
        self.summary()

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

    # ================================================== 0. HOOK ==========
    # Module opener: a silent breadcrumb, no spoken course welcome, straight into the hook.

    def hook(self):
        self.scene_start("S00_hook", title="Hook")

        crumb = self.breadcrumb("Quantitative Aptitude", "Module Introduction", "Why Aptitude?")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))

        title = text(f"Uploading dataset  ·  {DATA_MB // 1000} GB", LABEL, MUTED, BOLD)
        halves = VGroup(*[Rectangle(width=2.9, height=0.5, color=c, fill_color=c, fill_opacity=0.5)
                          for c in (WORD, RATIO)]).arrange(RIGHT, buff=0)
        labels = VGroup(*[VGroup(text(which, SMALL, MUTED), text(f"{s} MB/s", LABEL, c, BOLD)).arrange(DOWN, buff=0.1)
                          for which, s, c in zip(["first half", "second half"], SPEEDS, (WORD, RATIO))])
        ask = pill("Average speed = ?", FOCUS, size=LABEL)
        guess = VGroup(text("everyone says", SMALL, MUTED), pill(str(OBVIOUS), BAD, size=LABEL)).arrange(RIGHT, buff=0.2)
        answer = VGroup(text("it is", SMALL, MUTED), pill(f"{AVERAGE} MB/s", GOOD, size=LABEL)).arrange(RIGHT, buff=0.2)
        answers = VGroup(guess, answer).arrange(RIGHT, buff=0.5)
        window = VGroup(title, halves, Rectangle(width=5.8, height=labels.height).set_stroke(width=0), ask, answers)\
            .arrange(DOWN, buff=0.3)
        for label, half in zip(labels, halves):
            label.move_to(window[2]).set_x(half.get_x())

        work = VGroup(text(f"{HALF_MB:,} MB ÷ {SPEEDS[0]} MB/s  =  {TIMES[0]} s", LABEL, WORD),
                      text(f"{HALF_MB:,} MB ÷ {SPEEDS[1]} MB/s  =  {TIMES[1]} s", LABEL, RATIO),
                      text(f"{DATA_MB:,} MB ÷ {sum(TIMES)} s", LABEL, INK),
                      text(f"=  {AVERAGE} MB/s", LABEL, GOOD, BOLD)).arrange(DOWN, buff=0.22, aligned_edge=LEFT)
        per_s = 0.022
        clock = VGroup(*[Rectangle(width=t * per_s, height=0.4, color=c, fill_color=c, fill_opacity=0.5)
                         for t, c in zip(TIMES, (WORD, RATIO))]).arrange(RIGHT, buff=0)
        share = Fraction(TIMES[0], sum(TIMES))
        longer = text(f"slow half: {TIMES[0]} of {sum(TIMES)} s = {int(share * 100)}% of the time", SMALL, FOCUS, BOLD)
        right = VGroup(work, clock, longer).arrange(DOWN, buff=0.35, aligned_edge=LEFT)

        top = VGroup(VGroup(window, labels), right).arrange(RIGHT, buff=0.9)
        gap = pill("obvious answer  ≠  right answer:  that gap is this module", FOCUS, size=LABEL)
        block = VGroup(top, gap).arrange(DOWN, buff=0.5)
        fit_within(block, SAFE_W, SAFE_H - crumb.height - 0.7)
        block.next_to(crumb, DOWN, buff=0.45)
        strike = Line(guess[1].get_left() + LEFT * 0.05, guess[1].get_right() + RIGHT * 0.05, color=BAD, stroke_width=4)
        self.no_overlap(crumb, top, gap)
        self.no_overlap(title, halves, labels, ask, answers)
        self.no_overlap(labels[0], labels[1])
        self.no_overlap(VGroup(window, labels), right)
        self.no_overlap(work, clock, longer)
        self.validator.check_in_frame(VGroup(crumb, block))

        n = self.narrate(
            id="hook_01",
            text="You upload a twelve gigabyte dataset. The first half goes at forty megabytes per second, the second half "
                 "at sixty. What is the average speed?",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.at_word(n, "upload")
        self.play(FadeIn(title, shift=DOWN * 0.1))
        self.at_word(n, "forty")
        self.play(GrowFromEdge(halves[0], LEFT), FadeIn(labels[0], shift=UP * 0.1))
        self.at_word(n, "sixty")
        self.play(GrowFromEdge(halves[1], LEFT), FadeIn(labels[1], shift=UP * 0.1))
        self.at_word(n, "average")
        self.play(FadeIn(ask, scale=1.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_02",
            text="Everyone says fifty. It is forty-eight.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "fifty")
        self.play(FadeIn(guess, shift=UP * 0.1))
        self.at_word(n, "forty-eight")
        self.play(Create(strike), FadeIn(answer, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_03",
            text="The first half took one hundred and fifty seconds, the second one hundred, so twelve thousand megabytes "
                 "in two hundred and fifty seconds is forty-eight megabytes per second.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "fifty", occurrence=1)
        self.play(FadeIn(work[0], shift=LEFT * 0.1))
        self.at_word(n, "second", occurrence=1)
        self.play(FadeIn(work[1], shift=LEFT * 0.1))
        self.at_word(n, "thousand")
        self.play(FadeIn(work[2], shift=LEFT * 0.1))
        self.at_word(n, "forty-eight")
        self.play(FadeIn(work[3], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_04",
            text="The slow half lasted longer, so it counts for more.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "longer")
        self.play(GrowFromEdge(clock[0], LEFT), run_time=0.9)
        self.play(GrowFromEdge(clock[1], LEFT), run_time=0.6)
        self.at_word(n, "more")
        self.play(FadeIn(longer, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_05",
            text="That gap between the obvious answer and the right one is what this module is about.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "gap")
        self.play(Indicate(guess[1], color=BAD, scale_factor=1.1), Indicate(answer[1], color=GOOD, scale_factor=1.1))
        self.at_word(n, "module")
        self.play(FadeIn(gap, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_hook")

    # ========================================= 1. WHAT IS APTITUDE? ==========

    def what_is_aptitude(self):
        self.scene_start("S01_what_is_aptitude", title="What Is Aptitude?")

        head = self.heading("What is aptitude?")
        parts = [pill("simple maths + logic", WORD, size=LABEL), pill("unfamiliar problems", RATIO, size=LABEL),
                 pill("accurately", GOOD, size=LABEL), pill("strict time limit", BAD, size=LABEL)]
        grid = VGroup(VGroup(*parts[:2]).arrange(RIGHT, buff=0.6), VGroup(*parts[2:]).arrange(RIGHT, buff=0.6))
        grid.arrange(DOWN, buff=0.4)
        not_this = VGroup(text("✗", 34, BAD, BOLD), text("how much maths you know", BODY, MUTED)).arrange(RIGHT, buff=0.3)
        but_this = VGroup(text("✓", 34, GOOD, BOLD), text("how well you use it under pressure", BODY, INK, BOLD))\
            .arrange(RIGHT, buff=0.3)
        tests = VGroup(not_this, but_this).arrange(DOWN, buff=0.4, aligned_edge=LEFT)
        body = VGroup(grid, tests).arrange(DOWN, buff=0.9)
        fit_within(body, SAFE_W, SAFE_H - head.height - 1.0)
        body.next_to(head, DOWN, buff=0.7)
        self.no_overlap(head, grid, not_this, but_this)
        self.no_overlap(*parts)
        self.validator.check_in_frame(VGroup(head, body))

        n = self.narrate(
            id="what_01",
            text="Aptitude is applying simple mathematics and logic to unfamiliar problems, accurately, within a strict "
                 "time limit.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        for chip, spoken in zip(parts, ["simple", "unfamiliar", "accurately", "strict"]):
            self.at_word(n, spoken)
            self.play(FadeIn(chip, shift=UP * 0.1), run_time=0.45)
        self.wait_for_narration(n)

        n = self.narrate(
            id="what_02",
            text="It does not test how much maths you know.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "much")
        self.play(FadeIn(not_this, shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="what_03",
            text="It tests how well you use it under pressure.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "well")
        self.play(FadeIn(but_this, shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S01_what_is_aptitude")

    # ========================================= 2. WHY IS IT NEEDED? ==========

    def why_needed(self):
        self.scene_start("S02_why_needed", title="Why Is It Needed?")

        head = self.heading("Why is it needed?")
        blocks = VGroup()
        for i, (title, detail) in enumerate(REASONS):
            top = VGroup(pill(str(i + 1), RATIO, size=SMALL), text(title, LABEL, RATIO, BOLD)).arrange(RIGHT, buff=0.3)
            indent = Rectangle(width=0.75, height=0.1).set_stroke(width=0)                # never shown
            blocks.add(VGroup(top, VGroup(indent, text(detail, SMALL, INK)).arrange(RIGHT, buff=0))
                       .arrange(DOWN, buff=0.16, aligned_edge=LEFT))
        blocks.arrange(DOWN, buff=0.45, aligned_edge=LEFT)
        where = text("where it appears", SMALL, MUTED, BOLD)
        exams = VGroup(*[pill(e, WORD) for e in EXAMS]).arrange(RIGHT, buff=0.25)
        appears = VGroup(where, exams).arrange(DOWN, buff=0.2)
        body = VGroup(blocks, appears).arrange(DOWN, buff=0.6)
        fit_within(body, SAFE_W, SAFE_H - head.height - 0.8)
        body.next_to(head, DOWN, buff=0.5)
        self.no_overlap(head, *blocks, where, exams)
        self.validator.check_in_frame(VGroup(head, body))

        n = self.narrate(
            id="why_01",
            text="First, it gives one scale for everyone. Degrees and grading systems differ; an aptitude test does not.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "scale")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "differ")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="why_02",
            text="Second, it mirrors real work. Estimating time, cost, load and growth is everyday engineering.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "mirrors")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "Estimating")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="why_03",
            text="Third, it reveals judgement. Time limits and negative marking show whether your method holds.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "judgement")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "negative")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="why_04",
            text="It appears in C-CAT, GATE General Aptitude, placement tests, and bank and government exams.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "appears")
        self.play(FadeIn(where))
        for chip, spoken in zip(exams, ["C-CAT", "GATE", "placement", "bank"]):
            self.at_word(n, spoken)
            self.play(FadeIn(chip, shift=UP * 0.1), run_time=0.4)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_why_needed")

    # ================================ 3. WHAT AN APTITUDE QUESTION TESTS ==========

    def what_it_tests(self):
        self.scene_start("S03_what_it_tests", title="What an Aptitude Question Tests")

        head = self.heading("What an aptitude question tests")
        rows = name_rows(ABILITIES, WORD)
        fit_within(rows, SAFE_W, SAFE_H - head.height - 0.8)
        rows.next_to(head, DOWN, buff=0.5)
        self.no_overlap(head, *rows)
        self.validator.check_in_frame(VGroup(head, rows))

        n = self.narrate(
            id="tests_01",
            text="An aptitude question tests six abilities.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "six")
        self.play(FadeIn(head, shift=DOWN * 0.2), LaggedStart(*[FadeIn(r[0], scale=0.7) for r in rows], lag_ratio=0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="tests_02",
            text="Comprehension: reading exactly what is asked.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Comprehension")
        self.play(FadeIn(rows[0][1], shift=RIGHT * 0.2))
        self.at_word(n, "exactly")
        self.play(FadeIn(rows[0][2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="tests_03",
            text="Modelling: turning words into one equation.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Modelling")
        self.play(FadeIn(rows[1][1], shift=RIGHT * 0.2))
        self.at_word(n, "equation")
        self.play(FadeIn(rows[1][2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="tests_04",
            text="Numerical fluency: knowing that one eighth is twelve point five percent, without working.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "fluency")
        self.play(FadeIn(rows[2][1], shift=RIGHT * 0.2))
        self.at_word(n, "eighth")
        self.play(FadeIn(rows[2][2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="tests_05",
            text="Logic: reasoning backwards from a condition.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Logic")
        self.play(FadeIn(rows[3][1], shift=RIGHT * 0.2))
        self.at_word(n, "backwards")
        self.play(FadeIn(rows[3][2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="tests_06",
            text="Speed with accuracy: about a minute per question.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Speed")
        self.play(FadeIn(rows[4][1], shift=RIGHT * 0.2))
        self.at_word(n, "minute")
        self.play(FadeIn(rows[4][2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="tests_07",
            text="And judgement: knowing which question to skip.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "judgement")
        self.play(FadeIn(rows[5][1], shift=RIGHT * 0.2))
        self.at_word(n, "skip")
        self.play(FadeIn(rows[5][2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_what_it_tests")

    # ========================================= 4. C-CAT AT A GLANCE ==========

    def ccat_at_a_glance(self):
        self.scene_start("S04_ccat_at_a_glance", title="C-CAT at a Glance")

        head = self.heading("C-CAT at a glance  ·  Section A")
        facts = VGroup(pill(f"{TOTAL_Q} questions", WORD, size=BODY), pill(f"{TOTAL_MIN} minutes", RATIO, size=BODY),
                       pill(f"+{MARKS_RIGHT}  correct", GOOD, size=BODY), pill(f"−{abs(MARKS_WRONG)}  wrong", BAD, size=BODY))\
            .arrange(RIGHT, buff=0.5)
        blind = text(f"blind guess (4 options):  worth {expected_marks(4)} on average", LABEL, MUTED)
        tiles = VGroup(*[pill(l, INK, size=BODY, fill_opacity=0.06) for l in "ABCD"]).arrange(RIGHT, buff=0.4)
        better = text(f"eliminate two first (2 options):  worth +{expected_marks(2)} on average", LABEL, GOOD, BOLD)
        body = VGroup(facts, blind, tiles, better).arrange(DOWN, buff=0.55)
        fit_within(body, SAFE_W, SAFE_H - head.height - 1.0)
        body.next_to(head, DOWN, buff=0.7)
        crosses = VGroup(*[Line(t.get_corner(DL), t.get_corner(UR), color=BAD, stroke_width=4) for t in tiles[2:]])
        self.no_overlap(head, facts, blind, tiles, better)
        self.validator.check_in_frame(VGroup(head, body))

        n = self.narrate(
            id="ccat_01",
            text="Section A has fifty questions in sixty minutes.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "fifty")
        self.play(FadeIn(facts[0], shift=UP * 0.1))
        self.at_word(n, "sixty")
        self.play(FadeIn(facts[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="ccat_02",
            text="You get three marks for a correct answer, and lose one for a wrong one.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "three")
        self.play(FadeIn(facts[2], shift=UP * 0.1))
        self.at_word(n, "lose")
        self.play(FadeIn(facts[3], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="ccat_03",
            text="A blind guess is worth zero on average, so eliminate two options first.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "blind")
        self.play(LaggedStart(*[FadeIn(t, shift=UP * 0.1) for t in tiles], lag_ratio=0.12))
        self.at_word(n, "zero")
        self.play(FadeIn(blind, shift=DOWN * 0.1))
        self.at_word(n, "eliminate")
        self.play(*[Create(c) for c in crosses], *[t[1].animate.set_opacity(0.35) for t in tiles[2:]])
        self.play(FadeIn(better, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_ccat_at_a_glance")

    # ================================================ 5. THE METHOD ==========

    def the_method(self):
        self.scene_start("S05_the_method", title="The Method - Read, Model, Solve, Check")

        head = self.heading("The method")
        cols = method_columns()
        fit_width(cols, SAFE_W)
        avoid = text("Rates and percentages don't simply average or add.", LABEL, BAD)
        convert = pill("Convert to totals or multipliers first.", GOOD, size=LABEL)
        body = VGroup(cols, avoid, convert).arrange(DOWN, buff=0.7)
        fit_within(body, SAFE_W, SAFE_H - head.height - 1.0)
        body.next_to(head, DOWN, buff=0.7)
        self.no_overlap(head, cols, avoid, convert)
        self.no_overlap(*[cols[i] for i in (0, 2, 4, 6)])
        self.validator.check_in_frame(VGroup(head, body))

        n = self.narrate(
            id="method_01",
            text="The method has four steps: read, model, solve, check.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "read")
        self.play(FadeIn(cols[0][0], shift=DOWN * 0.1), run_time=0.4)
        self.at_word(n, "model")
        self.play(FadeIn(cols[1]), FadeIn(cols[2][0], shift=DOWN * 0.1), run_time=0.4)
        self.at_word(n, "solve")
        self.play(FadeIn(cols[3]), FadeIn(cols[4][0], shift=DOWN * 0.1), run_time=0.4)
        self.at_word(n, "check")
        self.play(FadeIn(cols[5]), FadeIn(cols[6][0], shift=DOWN * 0.1), run_time=0.4)
        self.wait_for_narration(n)

        n = self.narrate(
            id="method_02",
            text="Read what is asked, turn it into numbers, solve step by step, and check that the answer makes sense.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "asked")
        self.play(FadeIn(cols[0][1], shift=UP * 0.1), run_time=0.4)
        self.at_word(n, "numbers")
        self.play(FadeIn(cols[2][1], shift=UP * 0.1), run_time=0.4)
        self.at_word(n, "step", occurrence=1)
        self.play(FadeIn(cols[4][1], shift=UP * 0.1), run_time=0.4)
        self.at_word(n, "sense")
        self.play(FadeIn(cols[6][1], shift=UP * 0.1), run_time=0.4)
        self.wait_for_narration(n)

        n = self.narrate(
            id="method_03",
            text="Rates and percentages don't simply average or add. Convert to totals or multipliers first.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "average")
        self.play(FadeIn(avoid, shift=UP * 0.1))
        self.at_word(n, "Convert")
        self.play(FadeIn(convert, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_the_method")

    # ================================================ 6. CHECKPOINT ==========

    def checkpoint(self):
        self.scene_start("S06_checkpoint", title="Checkpoint")

        head = self.heading("Checkpoint")
        contents = [VGroup(text(f"Server {name}", LABEL, c, BOLD), text(f"{m} minutes per build", LABEL, INK))
                    .arrange(DOWN, buff=0.2) for name, m, c in zip("AB", BUILD_MIN, (WORD, RATIO))]
        tallest = max(c.height for c in contents) + 0.6
        servers = VGroup(*[self.card(c, width=3.9, height=tallest, color=col) for c, col in zip(contents, (WORD, RATIO))])\
            .arrange(RIGHT, buff=0.5)
        ask = pill("both in parallel:  ? minutes", FOCUS, size=LABEL)
        top = VGroup(servers, ask).arrange(RIGHT, buff=0.6)
        wrong = VGroup(*[VGroup(text("not", SMALL, MUTED), pill(v, BAD, size=LABEL)).arrange(RIGHT, buff=0.2)
                         for v in ["12.5", "25"]]).arrange(RIGHT, buff=0.8)
        work = VGroup(text(f"A:  {frac(RATES[0])} of the build per minute", LABEL, WORD),
                      text(f"B:  {frac(RATES[1])} of the build per minute", LABEL, RATIO),
                      text(f"together:  {frac(RATES[0])} + {frac(RATES[1])}  =  {frac(TOGETHER)} per minute", LABEL, INK))\
            .arrange(DOWN, buff=0.22, aligned_edge=LEFT)
        result = VGroup(pill(f"{BOTH_MIN} minutes", GOOD, size=BODY),
                        text(f"{BOTH_MIN} < {min(BUILD_MIN)}:  faster than the fastest server alone", LABEL, GOOD))\
            .arrange(RIGHT, buff=0.4)
        body = VGroup(top, wrong, work, result).arrange(DOWN, buff=0.4)
        fit_within(body, SAFE_W, SAFE_H - head.height - 0.6)
        body.next_to(head, DOWN, buff=0.4)
        self.no_overlap(head, top, wrong, work, result)
        self.no_overlap(servers[0], servers[1], ask)
        self.validator.check_in_frame(VGroup(head, body))

        n = self.narrate(
            id="check_01",
            text="A build takes ten minutes on server A and fifteen on server B. Split across both, how long does it take?",
            voice="default",
            subtitle=True,
            pause_after=10.0,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "ten")
        self.play(FadeIn(servers[0], shift=UP * 0.1))
        self.at_word(n, "fifteen")
        self.play(FadeIn(servers[1], shift=UP * 0.1))
        self.at_word(n, "Split")
        self.play(FadeIn(ask, shift=LEFT * 0.1))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="check_02",
            text="Not twelve point five, and not twenty-five.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "twelve")
        self.play(FadeIn(wrong[0], shift=UP * 0.1))
        self.at_word(n, "twenty-five")
        self.play(FadeIn(wrong[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="check_03",
            text="A does one tenth of the build per minute, B does one fifteenth, so together they do one sixth per minute: "
                 "six minutes.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "tenth")
        self.play(FadeIn(work[0], shift=RIGHT * 0.1))
        self.at_word(n, "fifteenth")
        self.play(FadeIn(work[1], shift=RIGHT * 0.1))
        self.at_word(n, "sixth")
        self.play(FadeIn(work[2], shift=RIGHT * 0.1))
        self.at_word(n, "six")
        self.play(FadeIn(result[0], scale=1.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="check_04",
            text="That is faster than the fastest server alone.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "faster")
        self.play(FadeIn(result[1], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_checkpoint")

    # ================================================== 7. SUMMARY ==========

    def summary(self):
        self.scene_start("S07_summary", title="Summary")

        facts = VGroup(pill("simple maths", WORD, size=LABEL), pill("accurate and fast", GOOD, size=LABEL))\
            .arrange(RIGHT, buff=0.5)
        steps = method_columns(with_details=False)
        distrust = pill("distrust any answer that came too easily", BAD, size=LABEL)
        nxt = self.breadcrumb("Next", "Lesson 11 · Simple & Compound Interest")
        VGroup(facts, steps, distrust, nxt).arrange(DOWN, buff=0.7).move_to(UP * 0.1)
        self.no_overlap(facts, steps, distrust, nxt)
        self.validator.check_in_frame(VGroup(facts, steps, distrust, nxt))

        n = self.narrate(
            id="summary_01",
            text="Aptitude is simple maths done accurately and fast.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "simple")
        self.play(FadeIn(facts[0], shift=UP * 0.1))
        self.at_word(n, "accurately")
        self.play(FadeIn(facts[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_02",
            text="Read, model, solve, check, and distrust any answer that came too easily.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Read")
        self.play(LaggedStart(*[FadeIn(s_, shift=RIGHT * 0.1) for s_ in steps], lag_ratio=0.15))
        self.at_word(n, "distrust")
        self.play(FadeIn(distrust, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_03",
            text="Next is lesson eleven: simple and compound interest.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "lesson")
        self.play(FadeIn(nxt, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S07_summary")

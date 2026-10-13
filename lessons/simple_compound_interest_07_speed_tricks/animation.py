"""
animation.py for the LMS video generator.

Course : Pre-C-CAT - Section A - Quantitative Aptitude
Video  : Lesson 11 - Simple & Compound Interest - 07 - Speed Tricks

Source script:
  C:\\Scripts\\Section A\\Module_2_Section_A_Quantitative_Aptitude_Part_1\\Aptitude_Scripts\\Sessions 1-4 - Interest, Profit & Loss, Time & Work\\Lesson 11 - Simple & Compound Interest\\07 - Speed Tricks.pdf

Built on the golden-reference pattern:
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``;
  * layouts stacked with next_to and guarded with ``no_overlap``; nothing is
    ever animated onto or into another box.

Lesson 11, Video 7 of 7 (speed tricks). Not the first video of the lesson: a silent breadcrumb, a one-line recap of Video 6, then today's topic. No spoken course welcome.
The narration follows the script section by section, with numbers written as words for the voice. The seven shortcuts are spread over four screens. Every figure on screen is computed and asserted, including the true doubling times in "When it fails".
Pauses: 10 s on the hook, and the script's own time limit after each timed drill (10, 8, 10, 8 and 8 seconds).
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

import math
from fractions import Fraction


def dec(x):
    return f"{float(x):g}"


def rs(x):
    return f"₹{round(x):,}"


def rule_of_72(r):
    """Compound doubling time, estimated."""
    return Fraction(72) / Fraction(r)


def true_doubling(r):
    """Compound doubling time, exact."""
    return math.log(2) / math.log(1 + r / 100)


def si_doubling(r):
    """Simple-interest doubling time (exact): 100 ÷ R."""
    return Fraction(100) / Fraction(r)


def si_scale(t, n, m):
    """SI: n times in t years -> m times in t(m − 1)/(n − 1) years."""
    return Fraction(t) * (m - 1) / (n - 1)


def ci_scale(x, target):
    """CI: doubles in x years -> ``target`` (a power of 2) times in x × log2(target) years."""
    doublings = int(math.log2(target))
    assert 2 ** doublings == target
    return x * doublings


def successive(a, b):
    """Two successive percentage changes: a + b + ab/100."""
    return Fraction(a) + Fraction(b) + Fraction(a) * Fraction(b) / 100


# ---- the hook and the doubling shortcuts ----
HOOK_R, HOOK_YEARS = 8, 9
assert rule_of_72(HOOK_R) == HOOK_YEARS and round(1.08 ** 9, 3) == 1.999 and si_doubling(HOOK_R) == Fraction("12.5")

# ---- scaling ----
assert si_scale(8, 2, 5) == 32 and ci_scale(6, 16) == 24 and [ci_scale(1, k) for k in (4, 8, 16)] == [2, 3, 4]

# ---- successive changes, fractions, the 2-year gap ----
assert successive(10, 10) == 21 and successive(20, -10) == 8
FRACTIONS = [("10%", Fraction(11, 10)), ("12.5%", Fraction(9, 8)), ("20%", Fraction(6, 5)), ("25%", Fraction(5, 4)),
             ("16 2/3%", Fraction(7, 6))]
assert all(m == 1 + Fraction(p.replace("%", "").replace("16 2/3", "50/3")) / 100 for p, m in FRACTIONS)
assert 6400 * Fraction(9, 8) ** 2 == 8100 and Fraction(10, 100) ** 2 == Fraction(1, 100)

# ---- when it fails ----
FAILS = [(1, rule_of_72(1), true_doubling(1)), (50, rule_of_72(50), true_doubling(50))]
assert [(dec(est), f"{true:.2f}") for _, est, true in FAILS] == [("72", "69.66"), ("1.44", "1.71")]

# ---- the trap ----
TRAP_SI, TRAP_CI = si_scale(5, 2, 4), ci_scale(5, 4)
assert (TRAP_SI, TRAP_CI) == (15, 10)

# ---- timed drills: (seconds, question, answer) ----
D2 = 5000 * successive(10, 10) / 100
assert (rule_of_72(12), D2, si_scale(8, 2, 5), ci_scale(6, 16), successive(20, -10)) == (6, 1050, 32, 24, 8)
DRILLS = [(10, "About how many years does money take to double at 12% compound?", f"72 ÷ 12  =  {rule_of_72(12)} years"),
          (8, "Compound interest on ₹5,000 at 10% for 2 years?", f"21% of 5,000  =  {rs(D2)}"),
          (10, "A sum doubles in 8 years at simple interest.  When does it become 5 times?",
           f"8 × (5 − 1)/(2 − 1)  =  {si_scale(8, 2, 5)} years"),
          (8, "A sum doubles in 6 years at compound interest.  When does it become 16 times?",
           f"16 = 2⁴,  so 4 × 6  =  {ci_scale(6, 16)} years"),
          (8, "A value rises 20% and then falls 10%.  Net change?", f"20 − 10 − 2  =  +{successive(20, -10)}%")]

OBJECTIVES = [("Estimate compound doubling time", "in under 10 seconds, and know when the estimate fails"),
              ("Scale “n times” questions", "for both simple and compound interest, instantly"),
              ("Calculate mentally", "with fraction multipliers and the successive-change formula")]
FORMULAS = ["Compound doubling  ≈  72/R            Simple doubling  =  100/R",
            "SI:    n× in T years    →    m× in T(m − 1)/(n − 1) years",
            "CI:    2× in x years    →    4× in 2x,    8× in 3x",
            "Successive change:    a + b + ab/100"]


def two_line_blocks(items, color, detail_size=SMALL):
    """Numbered blocks: a bold title line with a detail line under it.  block[0] = title line, block[1] = detail line."""
    blocks = VGroup()
    for i, (title, detail) in enumerate(items):
        top = VGroup(pill(str(i + 1), color, size=SMALL), text(title, LABEL, color, BOLD)).arrange(RIGHT, buff=0.3)
        indent = Rectangle(width=0.75, height=0.1).set_stroke(width=0)                    # never shown
        blocks.add(VGroup(top, VGroup(indent, text(detail, detail_size, INK)).arrange(RIGHT, buff=0))
                   .arrange(DOWN, buff=0.16, aligned_edge=LEFT))
    return blocks.arrange(DOWN, buff=0.5, aligned_edge=LEFT)


def given_chips(p, r, t):
    return VGroup(pill(f"P = {p}", "#4FC3F7", size=LABEL), pill(f"R = {r}", "#FFB74D", size=LABEL),
                  pill(f"T = {t}", "#CE93D8", size=LABEL)).arrange(RIGHT, buff=0.35)


class SpeedTricksInterestVideo(LMSScene):
    lesson_title = "Speed Tricks: Simple & Compound Interest"

    def construct(self):
        self.camera.background_color = BG

        self.intro()
        self.hook()
        self.objectives()
        self.the_slow_way()
        self.doubling_shortcuts()
        self.scaling_shortcuts()
        self.successive_changes()
        self.fractions_and_gap()
        self.formula_box()
        self.when_it_fails()
        self.the_trap()
        self.timed_drills()
        self.quick_revision()

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

    def stack(self, head, items, buff=0.45, top=0.5, align=None):
        """Stack ``items`` under ``head`` (fitted to the frame, guarded against overlap).  Returns the group."""
        body = VGroup(*items)
        if align is None:
            body.arrange(DOWN, buff=buff)
        else:
            body.arrange(DOWN, buff=buff, aligned_edge=align)
        fit_within(body, SAFE_W, SAFE_H - head.height - top - 0.3)
        body.next_to(head, DOWN, buff=top)
        self.no_overlap(head, *items)
        self.validator.check_in_frame(VGroup(head, body))
        return body

    def placed_table(self, head, header, rows, widths, size=SMALL, room=0.8):
        """A table fitted under ``head``.  Returns (table, body rows)."""
        table = self.table_rows(header, rows, widths, size=size)
        fit_within(table, SAFE_W, SAFE_H - head.height - room)
        table.next_to(head, DOWN, buff=0.45)
        self.no_overlap(head, table)
        self.no_overlap(*table)
        self.validator.check_in_frame(VGroup(head, table))
        return table, table[1:]

    def verdict_pair(self, wrong, right):
        """A ✗ card and a ✓ card of the same height, side by side."""
        contents = [VGroup(text(mark, 34, c, BOLD), text(s, LABEL, c)).arrange(RIGHT, buff=0.25)
                    for mark, s, c in [("✗", wrong, BAD), ("✓", right, GOOD)]]
        tallest = max(c.height for c in contents) + 0.6
        return VGroup(*[self.card(c, width=6.2, height=tallest, color=col) for c, col in zip(contents, (BAD, GOOD))])\
            .arrange(RIGHT, buff=0.5)

    def show_trap(self, trap):
        """Lay out one trap.  Returns (head, question, wrong card, right card, rule)."""
        title, question, wrong, right, rule = trap
        head = self.heading(title, BAD)
        q = fitted_text(question, SAFE_W - 1.0, BODY, INK, NORMAL, max_lines=2)
        pair = self.verdict_pair(wrong, right)
        rule_pill = fit_width(pill(rule, FOCUS, size=LABEL), SAFE_W)
        self.stack(head, [q, pair, rule_pill], buff=0.7, top=0.8)
        self.no_overlap(pair[0], pair[1])
        return head, q, pair[0], pair[1], rule_pill

    def solve_steps(self, steps, color=WORD):
        """Numbered solution rows.  Each row = (number chip, working, result)."""
        rows = VGroup(*[VGroup(pill(str(i + 1), color, size=SMALL), text(what, LABEL, INK), text(result, LABEL, GOOD, BOLD))
                        .arrange(RIGHT, buff=0.3) for i, (what, result) in enumerate(steps)])
        return rows.arrange(DOWN, buff=0.5, aligned_edge=LEFT)

    def pattern_table(self, head, patterns):
        table, rows = self.placed_table(head, ["Pattern", "Example", "Method", "Answer"], [list(p) for p in patterns],
                                        [2.6, 4.6, 4.2, 1.8], room=1.2)
        for row in rows:
            row[0].set_color(WORD)
            row[3].set_color(GOOD)
        return table, rows

    def practice_table(self, head, questions, first):
        table, rows = self.placed_table(head, ["Level", "Question"],
                                        [[f"{level}  ·  {first + i}", q] for i, (level, q) in enumerate(questions)],
                                        [1.6, 11.0], room=1.3)
        level_cols = {"L1": GOOD, "L2": RATIO, "L3": BAD}
        for row, (level, _) in zip(rows, questions):
            row[0].set_color(level_cols[level])
        return table, rows

    def answer_table(self, head, answers, first):
        table, rows = self.placed_table(head, ["#", "Reasoning", "Answer"],
                                        [[str(first + i), how, ans] for i, (how, ans) in enumerate(answers)], [0.8, 8.6, 3.6])
        for row in rows:
            row[0].set_color(MUTED)
            row[2].set_color(GOOD)
        return table, rows

    def titled(self, title, color, *lines):
        """A shortcut: bold title with its lines underneath."""
        return VGroup(text(title, LABEL, color, BOLD), *lines).arrange(DOWN, buff=0.25)

    def drill(self, index, drill):
        """Lay out one timed drill.  Returns (head, question, answer)."""
        seconds, question, answer = drill
        head = self.heading(f"Timed drill {index} of {len(DRILLS)}  ·  {seconds} seconds", RATIO)
        q = fitted_text(question, SAFE_W - 1.0, BODY, INK, NORMAL, max_lines=2)
        ans = pill(answer, GOOD, size=BODY)
        self.stack(head, [q, ans], buff=1.0, top=1.0)
        return head, q, ans

    # ================================================== 0. INTRO ==========
    # Not the first video: silent breadcrumb, a one-line recap of Video 6, then today's topic.

    def intro(self):
        self.scene_start("S00_intro", title="Intro")

        crumb = self.breadcrumb("Quantitative Aptitude", "Lesson 11 · Simple & Compound Interest", "Video 7 of 7")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        recap = VGroup(text("last video", SMALL, MUTED), pill("growth and depreciation: one chain of multipliers", WORD, size=LABEL))\
            .arrange(DOWN, buff=0.25)
        title = fit_width(text("Speed Tricks: Simple & Compound Interest", TITLE, INK, BOLD), SAFE_W)
        today = text("the last video of this lesson: shortcuts, for after the method is understood", LABEL, FOCUS)
        block = VGroup(recap, title, today).arrange(DOWN, buff=0.7)
        fit_within(block, SAFE_W, SAFE_H - crumb.height - 0.9)
        block.next_to(crumb, DOWN, buff=0.7)
        self.no_overlap(crumb, recap, title, today)
        self.validator.check_in_frame(VGroup(crumb, block))

        n = self.narrate(
            id="intro_01",
            text="In the last video, growth and depreciation became one chain of multipliers.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.at_word(n, "chain")
        self.play(FadeIn(recap, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="intro_02",
            text="This is the last video of the lesson: speed tricks, for after you understand the method.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "speed")
        self.play(FadeIn(title, shift=UP * 0.1))
        self.at_word(n, "after")
        self.play(FadeIn(today, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_intro")

    # =================================================== 1. HOOK ==========

    def hook(self):
        self.scene_start("S01_hook", title="Hook")

        head = self.heading("A message from a friend")
        message = fitted_text(f"“At {HOOK_R}% a year, compounded, my money doubles in {HOOK_YEARS} years.”", 9.4, BODY, INK,
                              NORMAL, max_lines=2)
        chat = self.card(message, width=10.4, color=WORD, pad=0.5)
        ask = VGroup(pill("True or false?", FOCUS, size=BODY), pill("10 seconds, no calculator", MUTED, size=LABEL))\
            .arrange(RIGHT, buff=0.5)
        ways = VGroup(text("the slow way:  1.08 × 1.08 × …  nine times", LABEL, BAD),
                      text("the fast way:  three seconds", LABEL, GOOD, BOLD)).arrange(DOWN, buff=0.3)
        self.stack(head, [chat, ask, ways], buff=0.6, top=0.7)
        self.no_overlap(*ask)

        n = self.narrate(
            id="hook_01",
            text="A friend messages: at eight percent a year, compounded, my money doubles in nine years.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "messages")
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(chat[0]))
        self.at_word(n, "doubles")
        self.play(FadeIn(message, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_02",
            text="True or false? Ten seconds, no calculator.",
            voice="default",
            subtitle=True,
            pause_after=10.0,
        )
        self.at_word(n, "True")
        self.play(FadeIn(ask[0], shift=UP * 0.1))
        self.at_word(n, "Ten")
        self.play(FadeIn(ask[1], shift=LEFT * 0.1))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="hook_03",
            text="The slow way multiplies one point zero eight by itself nine times. The fast way takes three seconds.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "slow")
        self.play(FadeIn(ways[0], shift=UP * 0.1))
        self.at_word(n, "fast")
        self.play(FadeIn(ways[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S01_hook")

    # ============================================== 2. OBJECTIVES ==========

    def objectives(self):
        self.scene_start("S02_objectives", title="Objectives")

        head = self.heading("By the end of this video")
        blocks = two_line_blocks(OBJECTIVES, WORD)
        self.stack(head, list(blocks), buff=0.55, top=0.7, align=LEFT)

        n = self.narrate(
            id="obj_01",
            text="By the end of this video, you will be able to do three things.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "three")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="obj_02",
            text="First, estimate compound doubling time in under ten seconds, and know when the estimate fails.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "estimate")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "fails")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="obj_03",
            text="Second, scale n times questions for both simple and compound interest, instantly.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "scale")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "both")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="obj_04",
            text="Third, use fraction multipliers and the successive-change formula for mental calculation.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "fraction")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "mental")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_objectives")

    # ============================================== 3. THE SLOW WAY ==========

    def the_slow_way(self):
        self.scene_start("S03_the_slow_way", title="The Slow Way")

        head = self.heading("The slow way")
        mults = VGroup(*[pill("× 1.08", MUTED) for _ in range(HOOK_YEARS)]).arrange(RIGHT, buff=0.1)
        exact = text("the exact method: one multiplier per year", LABEL, INK)
        verdict = VGroup(text("reliable", LABEL, GOOD, BOLD), text("nine multiplications: slow", LABEL, BAD),
                         text("each one is a chance to slip", LABEL, BAD)).arrange(RIGHT, buff=0.7)
        only = pill("speed tricks are only for after the method is understood", FOCUS, size=LABEL)
        self.stack(head, [exact, mults, verdict, only], buff=0.65, top=0.8)
        self.no_overlap(*verdict)

        n = self.narrate(
            id="slow_01",
            text="You already have the exact method: one multiplier per year.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "exact")
        self.play(FadeIn(exact, shift=UP * 0.1), LaggedStart(*[FadeIn(m, shift=RIGHT * 0.1) for m in mults], lag_ratio=0.12))
        self.wait_for_narration(n)

        n = self.narrate(
            id="slow_02",
            text="It is reliable, but nine multiplications are slow, and each one is a chance to slip.",
            voice="default",
            subtitle=True,
        )
        for part, spoken in zip(verdict, ["reliable", "slow", "slip"]):
            self.at_word(n, spoken)
            self.play(FadeIn(part, shift=UP * 0.1), run_time=0.45)
        self.wait_for_narration(n)

        n = self.narrate(
            id="slow_03",
            text="Speed tricks are only for after the method is understood.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "only")
        self.play(FadeIn(only, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_the_slow_way")

    # ================================ 4. SHORTCUTS 1 AND 2: DOUBLING ==========

    def doubling_shortcuts(self):
        self.scene_start("S04_doubling_shortcuts", title="Shortcuts 1 and 2 - Doubling Time")

        head = self.heading("Shortcuts 1 and 2  ·  doubling time")
        rule = pill("doubling time  ≈  72 ÷ R", GOOD, size=BODY)
        at_8 = text(f"at {HOOK_R}%:   72 ÷ {HOOK_R}  =  {rule_of_72(HOOK_R)} years", LABEL, INK)
        friend = text(f"your friend is right:   1.08^9  ≈  {1.08 ** 9:.3f}", LABEL, GOOD, BOLD)
        one = self.titled("1   Rule of 72: compound doubling", RATIO, rule, VGroup(at_8, friend).arrange(RIGHT, buff=0.7))
        exact = pill("doubling time  =  100 ÷ R", GOOD, size=BODY)
        si_8 = text(f"at {HOOK_R}%:   {dec(si_doubling(HOOK_R))} years", LABEL, INK)
        compare = text(f"compare: {rule_of_72(HOOK_R)} years for compound", LABEL, MUTED)
        two = self.titled("2   Simple-interest doubling is exact", WORD, exact, VGroup(si_8, compare).arrange(RIGHT, buff=0.7))
        self.stack(head, [one, two], buff=0.7, top=0.6)
        self.no_overlap(at_8, friend)
        self.no_overlap(si_8, compare)

        n = self.narrate(
            id="double_01",
            text="Shortcut one: the rule of seventy-two, for compound doubling. The doubling time is about seventy-two divided "
                 "by R.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "seventy-two", occurrence=1)
        self.play(FadeIn(one[0], shift=UP * 0.1))
        self.at_word(n, "divided")
        self.play(FadeIn(rule, scale=1.05))
        self.wait_for_narration(n)

        n = self.narrate(
            id="double_02",
            text="At eight percent: seventy-two divided by eight is nine years. Your friend is right: one point zero eight to "
                 "the power nine is about one point nine nine nine.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "nine", occurrence=1)
        self.play(FadeIn(at_8, shift=UP * 0.1))
        self.at_word(n, "right")
        self.play(FadeIn(friend, shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="double_03",
            text="Shortcut two: simple-interest doubling is exact. The doubling time is one hundred divided by R.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "exact")
        self.play(FadeIn(two[0], shift=UP * 0.1))
        self.at_word(n, "divided")
        self.play(FadeIn(exact, scale=1.05))
        self.wait_for_narration(n)

        n = self.narrate(
            id="double_04",
            text="At eight percent that is twelve point five years. Compare with nine years for compound.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "twelve")
        self.play(FadeIn(si_8, shift=UP * 0.1))
        self.at_word(n, "Compare")
        self.play(FadeIn(compare, shift=LEFT * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_doubling_shortcuts")

    # ================================ 5. SHORTCUTS 3 AND 4: SCALING ==========

    def scaling_shortcuts(self):
        self.scene_start("S05_scaling_shortcuts", title="Shortcuts 3 and 4 - Scaling n Times")

        head = self.heading("Shortcuts 3 and 4  ·  scaling “n times”")
        linear = text("interest grows linearly", SMALL, MUTED)
        si_rule = pill("n× in T years   →   m× in T × (m − 1)/(n − 1) years", WORD, size=LABEL)
        si_ex = text("doubles in 8 years   →   5 times in 8 × 4", LABEL, INK)
        si_ans = text(f"=  {si_scale(8, 2, 5)} years", LABEL, GOOD, BOLD)
        three = self.titled("3   Simple interest", WORD, linear, si_rule, VGroup(si_ex, si_ans).arrange(RIGHT, buff=0.4))
        multiply = text("multipliers multiply", SMALL, MUTED)
        ci_rule = pill("2× in x   →   4× in 2x   →   8× in 3x   →   16× in 4x", RATIO, size=LABEL)
        ci_ex = text("doubles in 6 years   →   16 times", LABEL, INK)
        ci_ans = text(f"in {ci_scale(6, 16)} years", LABEL, GOOD, BOLD)
        four = self.titled("4   Compound interest", RATIO, multiply, ci_rule, VGroup(ci_ex, ci_ans).arrange(RIGHT, buff=0.4))
        self.stack(head, [three, four], buff=0.5, top=0.5)
        self.no_overlap(si_ex, si_ans)
        self.no_overlap(ci_ex, ci_ans)

        n = self.narrate(
            id="scale_01",
            text="Shortcut three: scaling n times with simple interest. Interest grows linearly, so if a sum becomes n times in "
                 "T years, it becomes m times in T times m minus one, over n minus one, years.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "three")
        self.play(FadeIn(three[0], shift=UP * 0.1))
        self.at_word(n, "linearly")
        self.play(FadeIn(linear, shift=UP * 0.1))
        self.at_word(n, "minus", occurrence=1)
        self.play(FadeIn(si_rule, scale=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="scale_02",
            text="Doubles in eight years means five times in eight times four: thirty-two years.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "eight", occurrence=1)
        self.play(FadeIn(si_ex, shift=UP * 0.1))
        self.at_word(n, "thirty-two")
        self.play(FadeIn(si_ans, shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="scale_03",
            text="Shortcut four: scaling n times with compound interest. Multipliers multiply, so doubling in x years means "
                 "four times in two x, eight times in three x, sixteen times in four x.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "four", occurrence=1)
        self.play(FadeIn(four[0], shift=UP * 0.1))
        self.at_word(n, "multiply")
        self.play(FadeIn(multiply, shift=UP * 0.1))
        self.at_word(n, "sixteen")
        self.play(FadeIn(ci_rule, scale=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="scale_04",
            text="Doubles in six years means sixteen times in twenty-four years.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "six")
        self.play(FadeIn(ci_ex, shift=UP * 0.1))
        self.at_word(n, "twenty-four")
        self.play(FadeIn(ci_ans, shift=LEFT * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_scaling_shortcuts")

    # ================================ 6. SHORTCUT 5: SUCCESSIVE CHANGES ==========

    def successive_changes(self):
        self.scene_start("S06_successive_changes", title="Shortcut 5 - Successive Changes in One Line")

        head = self.heading("Shortcut 5  ·  successive changes in one line")
        rule = pill("a% then b%   =   a + b + ab/100", GOOD, size=BODY)
        falls = text("use negatives for falls", SMALL, MUTED)
        ex_1 = VGroup(text("two years at 10%:", LABEL, MUTED), text(f"10 + 10 + 1  =  {successive(10, 10)}%", LABEL, INK, BOLD))\
            .arrange(RIGHT, buff=0.4)
        ex_2 = VGroup(text("+20% then −10%:", LABEL, MUTED), text(f"20 − 10 − 2  =  {successive(20, -10)}%", LABEL, INK, BOLD))\
            .arrange(RIGHT, buff=0.4)
        self.stack(head, [rule, falls, ex_1, ex_2], buff=0.6, top=0.9)

        n = self.narrate(
            id="succ_01",
            text="Shortcut five: successive changes in one line. Two changes of a percent and b percent combine to a plus b "
                 "plus a b over a hundred, using negatives for falls.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "five")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "combine")
        self.play(FadeIn(rule, scale=1.05))
        self.at_word(n, "negatives")
        self.play(FadeIn(falls, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="succ_02",
            text="Two years at ten percent: ten plus ten plus one is twenty-one percent. Plus twenty then minus ten: twenty "
                 "minus ten minus two is eight percent.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "twenty-one")
        self.play(FadeIn(ex_1, shift=UP * 0.1))
        self.at_word(n, "eight")
        self.play(FadeIn(ex_2, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_successive_changes")

    # ====================== 7. SHORTCUTS 6 AND 7: FRACTIONS, THE 2-YEAR GAP ==========

    def fractions_and_gap(self):
        self.scene_start("S07_fractions_and_gap", title="Shortcuts 6 and 7 - Fraction Multipliers and the 2-Year Gap")

        head = self.heading("Shortcuts 6 and 7")
        chips = VGroup(*[pill(f"{p}  →  {m}", RATIO, size=SMALL) for p, m in FRACTIONS]).arrange(RIGHT, buff=0.25)
        mental = text("P a multiple of the denominator's power: the answer is mental", SMALL, MUTED)
        example = text("₹6,400 at 12.5% for 2 years   =   6,400 × 81/64   =   ₹8,100", LABEL, INK, BOLD)
        six = self.titled("6   Fraction multipliers", RATIO, chips, mental, example)
        gap_10 = text("at 10%:   1% of P", LABEL, INK, BOLD)
        gap_r = text("at R%:   (R²/100)% of P", LABEL, INK, BOLD)
        seven = self.titled("7   CI − SI for 2 years", WORD, VGroup(gap_10, gap_r).arrange(RIGHT, buff=1.0))
        self.stack(head, [six, seven], buff=0.7, top=0.6)
        self.no_overlap(*chips)
        self.no_overlap(gap_10, gap_r)

        n = self.narrate(
            id="frac_01",
            text="Shortcut six: fraction multipliers. Ten percent is eleven tenths, twelve point five percent is nine eighths, "
                 "twenty percent is six fifths, twenty-five percent is five fourths, and sixteen and two thirds percent is "
                 "seven sixths.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "six", occurrence=1)
        self.play(FadeIn(six[0], shift=UP * 0.1))
        for chip, spoken in zip(chips, ["eleven", "nine", "fifths", "fourths", "seven"]):
            self.at_word(n, spoken)
            self.play(FadeIn(chip, shift=UP * 0.1), run_time=0.4)
        self.wait_for_narration(n)

        n = self.narrate(
            id="frac_02",
            text="When P is a multiple of the denominator raised to the power, the answer is mental: six thousand four hundred "
                 "at twelve point five percent for two years is eight thousand one hundred.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "mental")
        self.play(FadeIn(mental, shift=UP * 0.1))
        self.at_word(n, "eight")
        self.play(FadeIn(example, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="frac_03",
            text="Shortcut seven: compound minus simple interest at ten percent for two years is one percent of P. At R "
                 "percent, it is R squared over a hundred, percent of P.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "seven")
        self.play(FadeIn(seven[0], shift=UP * 0.1), FadeIn(gap_10, shift=UP * 0.1))
        self.at_word(n, "squared")
        self.play(FadeIn(gap_r, shift=LEFT * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S07_fractions_and_gap")

    # ============================================== 8. FORMULA BOX ==========

    def formula_box(self):
        self.scene_start("S08_formula_box", title="Formula Box")

        head = self.heading("Formula box", GOOD)
        lines = VGroup(*[text(f, LABEL, INK) for f in FORMULAS]).arrange(DOWN, buff=0.5, aligned_edge=LEFT)
        box = self.card(lines, width=SAFE_W - 1.0, color=GOOD, pad=0.5)
        self.stack(head, [box], top=0.8)

        n = self.narrate(
            id="formula_01",
            text="Here is the formula box. Compound doubling is about seventy-two over R; simple doubling is one hundred over "
                 "R.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "box")
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(box[0]))
        self.at_word(n, "doubling")
        self.play(FadeIn(lines[0], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_02",
            text="For simple interest, n times in T years scales linearly.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "linearly")
        self.play(FadeIn(lines[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_03",
            text="For compound interest, doubling in x years means four times in two x, and eight times in three x.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "doubling")
        self.play(FadeIn(lines[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_04",
            text="And two successive changes combine to a plus b plus a b over a hundred.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "successive")
        self.play(FadeIn(lines[3], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S08_formula_box")

    # ============================================ 9. WHEN IT FAILS ==========

    def when_it_fails(self):
        self.scene_start("S09_when_it_fails", title="When It Fails")

        head = self.heading("When it fails", BAD)
        estimate = VGroup(text("the Rule of 72 is an estimate", LABEL, INK, BOLD), pill("close for about 6% to 12%", GOOD))\
            .arrange(RIGHT, buff=0.5)
        table = self.table_rows(["Rate", "Rule of 72", "True doubling time"],
                                [[f"{r}%", f"{dec(est)} years", f"{true:.2f} years" if r > 10 else f"{true:.1f} years"]
                                 for r, est, true in FAILS], [2.0, 3.4, 4.2], size=LABEL)
        for row in table[1:]:
            row[1].set_color(BAD)
            row[2].set_color(GOOD)
        never = pill("never use it when an exact answer is asked for", BAD, size=LABEL)
        more = VGroup(text("CI scaling (4× in 2x) needs a constant rate and compounding", SMALL, INK),
                      text("a + b + ab/100 combines exactly two changes: for three, apply it twice", SMALL, INK))\
            .arrange(DOWN, buff=0.25)
        self.stack(head, [estimate, table, never, more], buff=0.5, top=0.5)
        self.no_overlap(*estimate)
        self.no_overlap(*table)

        n = self.narrate(
            id="fails_01",
            text="The rule of seventy-two is an estimate. It is close for rates of about six to twelve percent.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "estimate")
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(estimate[0], shift=UP * 0.1))
        self.at_word(n, "close")
        self.play(FadeIn(estimate[1], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="fails_02",
            text="At one percent it gives seventy-two years, against a true sixty-nine point seven. At fifty percent it gives "
                 "one point four four years, against a true one point seven one.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(table[0]))
        self.at_word(n, "sixty-nine")
        self.play(FadeIn(table[1], shift=RIGHT * 0.2))
        self.at_word(n, "fifty")
        self.play(FadeIn(table[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="fails_03",
            text="Never use it when an exact answer is asked for.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Never")
        self.play(FadeIn(never, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="fails_04",
            text="The compound scaling needs a constant rate and compounding; it fails if the rate changes.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "constant")
        self.play(FadeIn(more[0], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="fails_05",
            text="And the successive-change formula combines exactly two changes. For three, apply it twice.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "exactly")
        self.play(FadeIn(more[1], shift=UP * 0.1))
        self.at_word(n, "twice")
        self.play(Indicate(more[1], color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S09_when_it_fails")

    # ================================================ 10. THE TRAP ==========

    def the_trap(self):
        self.scene_start("S10_the_trap", title="Trap - Mixing the SI and CI Scaling Rules")

        head = self.heading("Trap  ·  mixing the SI and CI scaling rules", BAD)
        q = text("A sum doubles in 5 years.  When does it become 4 times?", BODY, INK)
        contents = [VGroup(text(kind, LABEL, c, BOLD), text(answer, BODY, INK, BOLD), text(why, SMALL, MUTED)).arrange(DOWN, buff=0.2)
                    for kind, answer, why, c in [("simple interest", f"{TRAP_SI} years", "4× needs 3P of interest", WORD),
                                                 ("compound interest", f"{TRAP_CI} years", "two doublings: 2 × 2", RATIO)]]
        tallest = max(c.height for c in contents) + 0.7
        cards = VGroup(*[self.card(c, width=5.6, height=tallest, color=col) for c, col in zip(contents, (WORD, RATIO))])\
            .arrange(RIGHT, buff=0.6)
        rule = pill("read whether the interest is simple or compound before scaling", FOCUS, size=LABEL)
        self.stack(head, [q, cards, rule], buff=0.6, top=0.7)
        self.no_overlap(cards[0], cards[1])

        n = self.narrate(
            id="trap_01",
            text="One trap: mixing the simple and compound scaling rules. A sum doubles in five years. When does it become four "
                 "times?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "mixing")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "doubles")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.at_word(n, "four")
        self.play(Indicate(q, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="trap_02",
            text="With simple interest, fifteen years, because four times needs three P of interest. With compound interest, "
                 "ten years: two doublings.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "fifteen")
        self.play(FadeIn(cards[0], shift=UP * 0.1))
        self.at_word(n, "ten")
        self.play(FadeIn(cards[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="trap_03",
            text="The rule: read whether the interest is simple or compound before scaling.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "rule")
        self.play(FadeIn(rule, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S10_the_trap")

    # ============================================== 11. TIMED DRILLS ==========

    def timed_drills(self):
        self.scene_start("S11_timed_drills", title="Timed Drills")

        head, q, ans = self.drill(1, DRILLS[0])
        n = self.narrate(
            id="drill1_q",
            text="Drill one: about how many years does money take to double at twelve percent compound?",
            voice="default",
            subtitle=True,
            pause_after=10.0,
        )
        self.at_word(n, "Drill")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "double")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="drill1_a",
            text="Seventy-two divided by twelve: six years.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "divided")
        self.play(FadeIn(ans, scale=1.05))
        self.wait_for_narration(n)
        self.clear_stage()

        head, q, ans = self.drill(2, DRILLS[1])
        n = self.narrate(
            id="drill2_q",
            text="Drill two: what is the compound interest on five thousand rupees at ten percent for two years?",
            voice="default",
            subtitle=True,
            pause_after=8.0,
        )
        self.at_word(n, "Drill")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "compound")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="drill2_a",
            text="Twenty-one percent of five thousand: one thousand and fifty rupees.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Twenty-one")
        self.play(FadeIn(ans, scale=1.05))
        self.wait_for_narration(n)
        self.clear_stage()

        head, q, ans = self.drill(3, DRILLS[2])
        n = self.narrate(
            id="drill3_q",
            text="Drill three: a sum doubles in eight years at simple interest. When does it become five times?",
            voice="default",
            subtitle=True,
            pause_after=10.0,
        )
        self.at_word(n, "Drill")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "doubles")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.at_word(n, "five")
        self.play(Indicate(q, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="drill3_a",
            text="Eight times four: thirty-two years.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "times")
        self.play(FadeIn(ans, scale=1.05))
        self.wait_for_narration(n)
        self.clear_stage()

        head, q, ans = self.drill(4, DRILLS[3])
        n = self.narrate(
            id="drill4_q",
            text="Drill four: a sum doubles in six years at compound interest. When does it become sixteen times?",
            voice="default",
            subtitle=True,
            pause_after=8.0,
        )
        self.at_word(n, "Drill")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "doubles")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.at_word(n, "sixteen")
        self.play(Indicate(q, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="drill4_a",
            text="Sixteen is two to the power four, so four times six: twenty-four years.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "power")
        self.play(FadeIn(ans, scale=1.05))
        self.wait_for_narration(n)
        self.clear_stage()

        head, q, ans = self.drill(5, DRILLS[4])
        n = self.narrate(
            id="drill5_q",
            text="Drill five: a value rises twenty percent and then falls ten percent. What is the net change?",
            voice="default",
            subtitle=True,
            pause_after=8.0,
        )
        self.at_word(n, "Drill")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "rises")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.at_word(n, "net")
        self.play(Indicate(q, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="drill5_a",
            text="Twenty minus ten minus two: a rise of eight percent.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "minus", occurrence=1)
        self.play(FadeIn(ans, scale=1.05))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S11_timed_drills")

    # ============================================== 12. QUICK REVISION ==========

    def quick_revision(self):
        self.scene_start("S12_quick_revision", title="Quick Revision")

        head = self.heading("Quick revision")
        tricks = VGroup(*[VGroup(text(label, SMALL, MUTED), pill(formula, GOOD, size=LABEL)).arrange(RIGHT, buff=0.4)
                          for label, formula in [("compound doubling, an estimate", "72 / R"),
                                                 ("simple-interest doubling, exact", "100 / R"),
                                                 ("SI scaling, linear", "T (m − 1)/(n − 1)"),
                                                 ("CI scaling, powers", "2× → 4× → 8×  in  x, 2x, 3x"),
                                                 ("two successive changes", "a + b + ab/100")]])\
            .arrange(DOWN, buff=0.25, aligned_edge=RIGHT)
        limits = text("know where each trick stops working", LABEL, BAD, BOLD)
        nxt = self.breadcrumb("Next", "Lesson 11 Practice Kit", "Lesson 12 · Profit & Loss")
        self.stack(head, [tricks, limits, nxt], buff=0.5, top=0.5)
        self.no_overlap(*tricks)

        n = self.narrate(
            id="revision_01",
            text="Use the rule of seventy-two for compound doubling estimates, one hundred over R for exact simple-interest "
                 "doubling, linear scaling for simple interest and power scaling for compound interest, and a plus b plus a b "
                 "over a hundred for any two successive changes.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        for trick, spoken in zip(tricks, ["seventy-two", "exact", "linear", "power", "successive"]):
            self.at_word(n, spoken)
            self.play(FadeIn(trick, shift=RIGHT * 0.2), run_time=0.45)
        self.wait_for_narration(n)

        n = self.narrate(
            id="revision_02",
            text="Know where each trick stops working.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "stops")
        self.play(FadeIn(limits, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="revision_03",
            text="Next: the lesson eleven practice kit, and then lesson twelve, profit and loss.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Next")
        self.play(FadeIn(nxt, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S12_quick_revision")

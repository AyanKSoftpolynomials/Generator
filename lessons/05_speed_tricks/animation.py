"""
animation.py for the LMS video generator.

Course : Pre-C-CAT - Section A - Quantitative Aptitude
Video  : Lesson 18 - Pipes & Cistern - 05 - Speed Tricks

Source script:
  C:\\Scripts\\Section A\\Aptitude\\Sessions 13-18 - Pipes, Time Distance, Partnership\\Lesson 18 - Pipes & Cistern\\05 - Speed Tricks.pdf

Built on the golden-reference pattern:
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``;
  * layouts stacked with next_to and guarded with ``no_overlap``; nothing is
    ever animated onto or into another box.

Lesson 18, Video 5 of 5 (Speed Tricks). Not the first video of the lesson: a silent breadcrumb, a one-line recap of Video 4, then today's topic. No spoken course welcome.
The six shortcuts are spread over four screens, each with the script's live example; every result is checked against the plain rate calculation in the data block.
Text colours: white and grey, one blue accent, green and red only for right and wrong.
Pauses: 10 seconds on the hook, then the script's own timers on the five drills (5, 8, 5, 12, 10 seconds).
The closing breadcrumb points to the Lesson 18 Practice Kit and then Lesson 19, Time & Distance.
"""

import math

import numpy as np
from manim import *

from src.animation import LMSScene

# ============================================================== style ====

BG = "#0B1020"
INK = "#F1F5F9"
MUTED = "#94A3B8"
PANEL = "#151C2E"
CELL = "#1B2440"

TERM = INK             # series terms
DIFF = "#7FB2E5"       # first differences
SECOND = "#7FB2E5"     # second differences / pattern of the differences
RATIO = "#7FB2E5"      # ratios (the next topic's tool)
FOCUS = "#7FB2E5"      # "look here" / predicted value
GOOD = "#7FC8A0"       # confirmed answer
BAD = "#E08080"        # wrong / trap

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

SHORT_WORDS = {"a", "an", "as", "at", "be", "by", "do", "he", "if", "in", "is", "it", "no", "of", "on", "or", "so", "to", "up", "we"}


def cap_first(s):
    """Start on-screen text with a capital letter when it starts with a word (not a variable, unit or number)."""
    start = 0
    while start < len(s) and s[start] in "“\"'(":
        start += 1
    words = s[start:].split()
    if not words:
        return s
    first = words[0].rstrip(".,;:?!”’")
    plain = first.replace("'", "").replace("’", "").replace("-", "")
    if not (plain.isalpha() and plain.islower()):
        return s
    if len(plain) == 1:
        follower = words[1].rstrip(".,;:?!") if len(words) > 1 else ""
        if not (plain == "a" and len(follower) >= 2 and follower.replace("-", "").isalpha()):
            return s
    elif len(plain) == 2 and plain not in SHORT_WORDS:
        return s
    return s[:start] + s[start].upper() + s[start + 1:]

def text(s, size=BODY, color=INK, weight=NORMAL, t2c=None):
    return Text(cap_first(s), font=FONT, font_size=size, color=color, weight=weight, t2c=t2c or {})


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

WORD = "#7FB2E5"          # the question word
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
from math import isqrt


def together(*times):
    """Plain rate method: full-tank times, negative for an outlet."""
    return 1 / sum(Fraction(1, t) for t in times)


# ---- the hook: tap 12 min, with the drain 20 min ----
assert Fraction(12 * 20, 20 - 12) == 30 == 1 / (Fraction(1, 12) - Fraction(1, 20)) and (60 // 12, 60 // 20, 60 // 2) == (5, 3, 30)

# ---- the shortcuts, each against the rate method ----
assert Fraction(18 * 36, 18 + 36) == 12 == together(18, 36) and 18 * 36 == 648
assert Fraction(6 * 9, 9 - 6) == 18 == together(6, -9)
assert 6 * 8 * 12 == 576 and 8 * 12 + 12 * 6 - 6 * 8 == 120 and Fraction(576, 120) == Fraction(24, 5) == together(6, 8, -12)
T_CLOSED = Fraction(15 * (10 + 5), 15 + 10)
assert T_CLOSED == 9 and Fraction(T_CLOSED, 15) + Fraction(T_CLOSED - 5, 10) == 1
assert isqrt(8 * 18) == 12 and together(12 + 8, 12 + 18) == 12

# ---- the trap, and the timed drills: (seconds, question, answer) ----
assert Fraction(12 * 20, 12 + 20) == Fraction(15, 2)
assert together(10, -15) == 30 and Fraction(8 * 6, 8 - 6) == 24 and together(8, 24) == 6 and Fraction(5 * 6, 6 - 5) == 30
T_DRILL = Fraction(12 * (6 + 3), 12 + 6)
assert T_DRILL == 6 and Fraction(T_DRILL, 12) + Fraction(T_DRILL - 3, 6) == 1
DRILLS = [(5, "Fill in 10 hours, empty in 15 hours, both open.  Time to fill?", "10 × 15 ÷ (15 − 10)  =  150 ÷ 5  =  30 hours"),
          (8, "A alone fills in 8 minutes; A and B together in 6 minutes.  B alone?", "8 × 6 ÷ (8 − 6)  =  24 minutes"),
          (5, "A pipe fills a tank in 5 hours; with a leak, in 6 hours.  Leak alone?", "5 × 6 ÷ (6 − 5)  =  30 hours"),
          (12, "Inlets 6 and 8 hours, outlet 12 hours, all open.  Time to fill?", "576 ÷ (96 + 72 − 48)  =  576 ÷ 120  =  4.8 hours"),
          (10, "A fills in 12 minutes, B in 6.  Both start; B is closed 3 minutes before the tank is full.  Total time?",
           "12 × (6 + 3) ÷ 18  =  6 minutes")]

OBJECTIVES = [("Use one-line formulas", "for two pipes, fill-and-empty pairs and three pipes with an outlet"),
              ("Find a missing pipe or a leak instantly", "from two times"),
              ("Solve “closed x minutes before full” in one line", "and know when each shortcut fails")]
FORMULAS = ["Two inlets:    xy/(x + y)                    Fill x, empty y:    xy/(y − x)",
            "Missing pipe:    xt/(x − t)  inlet;          xt/(t − x)  outlet or leak",
            "Inlets x, y and outlet z:    xyz/(yz + zx − xy)",
            "B (time y) closed d before full:    T  =  x(y + d)/(x + y)",
            "Two inlets, extra times a and b:    t  =  √(ab)"]
FAILS = [("Shortcuts 1 to 4 and 6 assume every pipe runs from start to full", "opens later, closes early, takes turns or starts at a level:  back to the timeline (Video 3)"),
         ("xy/(y − x) needs y > x", "a faster outlet (y < x):  the empty tank never fills;  a full tank empties in xy/(x − y)"),
         ("The three-pipe formula needs a positive denominator", "if yz + zx − xy ≤ 0, the outlet wins and the tank never fills"),
         ("√(ab) works only for two inlets running together throughout", "a and b are measured from the joint time;  never with an outlet"),
         ("Litre questions need the capacity or a flow", "these formulas give times only")]
TRAPS = [("Trap  ·  the two-inlet formula used with an outlet", "Fill in 12 minutes, empty in 20 minutes, both open.  Time to fill?",
          "12 × 20/(12 + 20)  =  7.5 min", "12 × 20/(20 − 12)  =  30 min",
          "An outlet changes the plus to a minus.  Decide the sign before choosing the formula.")]


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


class SpeedTricksPipesAndCisternVideo(LMSScene):
    lesson_title = "Speed Tricks: Pipes & Cistern"

    def construct(self):
        self.camera.background_color = BG

        self.intro()
        self.hook()
        self.objectives()
        self.the_slow_way()
        self.two_pipes()
        self.missing_pipe()
        self.three_pipes_and_closed()
        self.extra_time()
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
        colors = [DIFF, MUTED, RATIO]
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
        level_cols = {"L1": WORD, "L2": WORD, "L3": WORD}
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

    def step_rows(self, items, color=WORD):
        """Numbered concept steps.  Each row = (number chip, the step[, a short note in green])."""
        rows = VGroup()
        for i, (what, note) in enumerate(items):
            row = VGroup(pill(str(i + 1), color, size=SMALL), text(what, LABEL, INK, BOLD))
            if note:
                row.add(text(note, LABEL, GOOD, BOLD))
            rows.add(row.arrange(RIGHT, buff=0.35))
        return fit_width(rows.arrange(DOWN, buff=0.5, aligned_edge=LEFT), SAFE_W - 0.6)

    def pattern_blocks(self, patterns):
        """Each exam pattern as two lines: name + example, then method + answer.  block[0], block[1]."""
        blocks = VGroup()
        for name, example, method, answer in patterns:
            first = VGroup(text(name, LABEL, WORD, BOLD), text(example, LABEL, INK)).arrange(RIGHT, buff=0.5)
            second = VGroup(text(method, LABEL, MUTED), text(answer, LABEL, GOOD, BOLD)).arrange(RIGHT, buff=0.6)
            blocks.add(fit_width(VGroup(first, second).arrange(DOWN, buff=0.2, aligned_edge=LEFT), SAFE_W - 0.8))
        return blocks

    def drill(self, index, drill):
        """Lay out one timed drill.  Returns (head, question, answer)."""
        seconds, question, answer = drill
        head = self.heading(f"Timed drill {index} of {len(DRILLS)}  ·  {seconds} seconds")
        q = fitted_text(question, SAFE_W - 1.0, BODY, INK, NORMAL, max_lines=2)
        ans = fit_width(pill(answer, GOOD, size=BODY), SAFE_W)
        self.stack(head, [q, ans], buff=1.0, top=1.0)
        return head, q, ans

    # ============================================== 0. INTRO ==========
    # Not the first video: silent breadcrumb, a one-line recap of the previous video, then today's topic.

    def intro(self):
        self.scene_start("S00_intro", title="Intro")

        crumb = self.breadcrumb("Quantitative Aptitude", "Lesson 18 · Pipes & Cistern", "Video 5 of 5")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        recap = VGroup(text("last video", SMALL, MUTED), pill("a leak:  xy/(y − x)", WORD, size=LABEL)).arrange(DOWN, buff=0.25)
        title = fit_width(text("Speed Tricks: Pipes & Cistern", TITLE, INK, BOLD), SAFE_W - 0.4)
        today = text("today: four lines become one", LABEL, FOCUS)
        block = VGroup(recap, title, today).arrange(DOWN, buff=0.7)
        fit_within(block, SAFE_W, SAFE_H - crumb.height - 0.9)
        block.next_to(crumb, DOWN, buff=0.7)
        self.no_overlap(crumb, recap, title, today)
        self.validator.check_in_frame(VGroup(crumb, block))

        n = self.narrate(
            id="intro_01",
            text="In the last video, a leak was the gap between two rates: x y over y minus x.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.at_word(n, "gap")
        self.play(FadeIn(recap, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="intro_02",
            text="Today: speed tricks for pipes and cistern, where four lines of working become one.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "speed")
        self.play(FadeIn(title, shift=UP * 0.1))
        self.at_word(n, "become")
        self.play(FadeIn(today, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_intro")

    # ============================================== 1. HOOK ==========

    def hook(self):
        self.scene_start("S01_hook", title="Hook")

        head = self.heading("Ten seconds")
        given = VGroup(pill("tap alone:  12 min", GOOD, size=BODY), pill("tap with the drain open:  20 min", BAD, size=BODY)).arrange(RIGHT, buff=0.6)
        ask = pill("drain alone?", FOCUS, size=BODY)
        target = VGroup(text("the LCM method: four lines", LABEL, MUTED), text("today's target: one", LABEL, INK, BOLD)).arrange(RIGHT, buff=0.8)
        self.stack(head, [given, ask, target], buff=0.9, top=1.0)
        self.no_overlap(*given)
        self.no_overlap(*target)

        n = self.narrate(
            id="hook_01",
            text="Ten seconds. A tap fills a basin in twelve minutes. With the drain open as well, it takes twenty "
                 "minutes. How long would the drain alone take to empty the full basin?",
            voice="default",
            subtitle=True,
            pause_after=10.0,
        )
        self.at_word(n, "Ten")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "twelve")
        self.play(FadeIn(given[0], shift=UP * 0.1))
        self.at_word(n, "twenty")
        self.play(FadeIn(given[1], shift=UP * 0.1))
        self.at_word(n, "alone")
        self.play(FadeIn(ask, scale=1.03))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="hook_02",
            text="The L C M method takes four lines. Today's target is one.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "four")
        self.play(FadeIn(target[0], shift=UP * 0.1))
        self.at_word(n, "target")
        self.play(FadeIn(target[1], shift=LEFT * 0.1))
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
            id="objectives_01",
            text="By the end of this video, you will be able to do three things.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "three")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="objectives_02",
            text="First, use one-line formulas for two pipes, fill-and-empty pairs, and three pipes with an outlet.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "formulas")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "pairs")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="objectives_03",
            text="Second, find a missing pipe or a leak instantly from two times.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "missing")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "times")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="objectives_04",
            text="Third, solve closed x minutes before full in one line, and know when each shortcut fails.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "solve")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "fails")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_objectives")

    # ============================================== 3. THE SLOW WAY ==========

    def the_slow_way(self):
        self.scene_start("S03_the_slow_way", title="The Slow Way")

        head = self.heading("The slow way:  the LCM method", BAD)
        lines = VGroup(text("total 60 units:    tap = 5,    with the drain = 3", BODY, INK, BOLD),
                       text("drain  =  5 − 3  =  2 units a minute", BODY, INK, BOLD),
                       text("60 ÷ 2  =  30 minutes", BODY, INK, BOLD)).arrange(DOWN, buff=0.5)
        verdict = pill("reliable, but about 20 seconds", BAD, size=LABEL)
        self.stack(head, [lines, verdict], buff=0.9, top=1.0)
        self.no_overlap(*lines)

        n = self.narrate(
            id="the_slow_way_01",
            text="Pick a total, count units, subtract: total sixty, the tap is five, with the drain three, so the drain is "
                 "two, and sixty divided by two is thirty minutes.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "Pick")
        self.play(FadeIn(lines[0], shift=UP * 0.1))
        self.at_word(n, "so")
        self.play(FadeIn(lines[1], shift=UP * 0.1))
        self.at_word(n, "divided")
        self.play(FadeIn(lines[2], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="the_slow_way_02",
            text="Reliable, but about twenty seconds.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Reliable")
        self.play(FadeIn(verdict, scale=1.03))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_the_slow_way")

    # ============================================== 4. SHORTCUTS 1 AND 2 - TWO PIPES ==========

    def two_pipes(self):
        self.scene_start("S04_two_pipes", title="Shortcuts 1 and 2 - Two Pipes")

        head = self.heading("Shortcuts 1 and 2  ·  two pipes")
        first = VGroup(pill("two inlets together:    T = xy/(x + y)", WORD, size=BODY),
                       text("18 and 36 min:    648 ÷ 54  =  12 min", BODY, GOOD, BOLD)).arrange(DOWN, buff=0.35)
        second = VGroup(pill("fill in x, empty in y  (y > x):    T = xy/(y − x)", WORD, size=BODY),
                        text("6 and 9 h:    54 ÷ 3  =  18 h", BODY, GOOD, BOLD)).arrange(DOWN, buff=0.35)
        self.stack(head, [first, second], buff=1.0, top=0.9)

        n = self.narrate(
            id="two_pipes_01",
            text="Shortcut one: two inlets together take x y over x plus y, as in lesson thirteen. For eighteen and "
                 "thirty-six minutes: six hundred and forty-eight divided by fifty-four is twelve minutes.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "inlets")
        self.play(FadeIn(first[0], scale=1.03))
        self.at_word(n, "divided")
        self.play(FadeIn(first[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="two_pipes_02",
            text="Shortcut two: fill and empty together. An inlet fills in x and an outlet empties in y, with y bigger "
                 "than x: the tank fills in x y over y minus x. For six and nine hours: fifty-four divided by three is "
                 "eighteen hours.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "empty")
        self.play(FadeIn(second[0], scale=1.03))
        self.at_word(n, "minus")
        self.play(Indicate(second[0], color=FOCUS, scale_factor=1.03))
        self.at_word(n, "divided")
        self.play(FadeIn(second[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_two_pipes")

    # ============================================== 5. SHORTCUT 3 - THE MISSING PIPE, OR THE LEAK ==========

    def missing_pipe(self):
        self.scene_start("S05_missing_pipe", title="Shortcut 3 - The Missing Pipe, or the Leak")

        head = self.heading("Shortcut 3  ·  the missing pipe, or the leak")
        given = text("a pipe alone fills in x;   with a second pipe open, the tank fills in t", LABEL, INK)
        inlet = pill("t < x:    the second pipe is an inlet, alone in  xt/(x − t)", GOOD, size=LABEL)
        outlet = pill("t > x:    it is an outlet or a leak, alone in  xt/(t − x)", BAD, size=LABEL)
        solved = VGroup(text("the hook:    12 × 20 ÷ (20 − 12)", BODY, INK, BOLD), text("=  30 minutes", BODY, GOOD, BOLD)).arrange(RIGHT, buff=0.5)
        same = text("a fill time rising from x to y is the same formula:  the leak takes xy/(y − x)", LABEL, MUTED)
        self.stack(head, [given, inlet, outlet, solved, same], buff=0.6, top=0.7)
        self.no_overlap(*solved)

        n = self.narrate(
            id="missing_pipe_01",
            text="Shortcut three: the missing pipe, or the leak. A pipe alone fills in x and, with a second pipe open, the "
                 "tank fills in t.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "missing")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "second")
        self.play(FadeIn(given, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="missing_pipe_02",
            text="If t is less than x, the second pipe is an inlet that fills alone in x t over x minus t.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "less")
        self.play(FadeIn(inlet, scale=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="missing_pipe_03",
            text="If t is more than x, the second pipe is an outlet, or a leak, that empties alone in x t over t minus x.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "more")
        self.play(FadeIn(outlet, scale=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="missing_pipe_04",
            text="The hook: twelve times twenty, divided by twenty minus twelve, is thirty minutes.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "times")
        self.play(FadeIn(solved[0], shift=UP * 0.1))
        self.at_word(n, "thirty")
        self.play(FadeIn(solved[1], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="missing_pipe_05",
            text="A fill time that rises from x to y is the same formula: the leak takes x y over y minus x.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "same")
        self.play(FadeIn(same, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_missing_pipe")

    # ============================================== 6. SHORTCUTS 4 AND 5 - THREE PIPES; CLOSED BEFORE FULL ==========

    def three_pipes_and_closed(self):
        self.scene_start("S06_three_pipes_and_closed", title="Shortcuts 4 and 5 - Three Pipes; Closed Before Full")

        head = self.heading("Shortcuts 4 and 5")
        three = VGroup(pill("inlets x and y, outlet z:    T = xyz/(yz + zx − xy)", WORD, size=LABEL),
                       text("6, 8 and 12 h:    576 ÷ (96 + 72 − 48)  =  576 ÷ 120  =  4.8 h", LABEL, GOOD, BOLD),
                       text("(all three inlets:    xyz/(xy + yz + zx))", LABEL, MUTED)).arrange(DOWN, buff=0.3)
        closed = VGroup(pill("B (time y) closed d minutes before full:    T = x(y + d)/(x + y)", WORD, size=LABEL),
                        text("15, 10 and 5:    15 × 15 ÷ 25  =  9 min", LABEL, GOOD, BOLD)).arrange(DOWN, buff=0.3)
        self.stack(head, [three, closed], buff=0.9, top=0.8)

        n = self.narrate(
            id="three_pipes_and_closed_01",
            text="Shortcut four: three pipes, one an outlet. With inlets x and y and outlet z, the time is x y z over y z "
                 "plus z x minus x y.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "pipes")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "over")
        self.play(FadeIn(three[0], scale=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="three_pipes_and_closed_02",
            text="For six, eight and twelve hours: five hundred and seventy-six, divided by ninety-six plus seventy-two "
                 "minus forty-eight, one hundred and twenty, is four point eight hours. With all three as inlets, every "
                 "term is added.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "divided")
        self.play(FadeIn(three[1], shift=UP * 0.1))
        self.at_word(n, "added")
        self.play(FadeIn(three[2], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="three_pipes_and_closed_03",
            text="Shortcut five: closed d minutes before full. A fills in x, B fills in y, both start together, and B is "
                 "closed d minutes before the tank is full: the total time is x times y plus d, over x plus y.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "closed")
        self.play(FadeIn(closed[0], scale=1.03))
        self.at_word(n, "total")
        self.play(Indicate(closed[0], color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="three_pipes_and_closed_04",
            text="For fifteen, ten and five: fifteen times fifteen, divided by twenty-five, is nine minutes.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "divided")
        self.play(FadeIn(closed[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_three_pipes_and_closed")

    # ============================================== 7. SHORTCUT 6 - TWO INLETS WITH EXTRA TIME ==========

    def extra_time(self):
        self.scene_start("S07_extra_time", title="Shortcut 6 - Two Inlets with Extra Time")

        head = self.heading("Shortcut 6  ·  two inlets with “extra time”")
        law = fit_width(pill("together t;   A alone needs a more,  B alone needs b more:    t = √(ab)", WORD, size=LABEL), SAFE_W - 0.4)
        only = text("inlets only", LABEL, BAD, BOLD)
        eg = VGroup(text("A needs 8 more, B needs 18 more:    t = √144", BODY, INK, BOLD), text("=  12", BODY, GOOD, BOLD)).arrange(RIGHT, buff=0.5)
        check = text("check:   20 and 30 minutes give   1/20 + 1/30  =  1/12", LABEL, MUTED)
        self.stack(head, [law, only, eg, check], buff=0.75, top=0.9)
        self.no_overlap(*eg)

        n = self.narrate(
            id="extra_time_01",
            text="Shortcut six: two inlets with extra time. If A and B together take t, and A alone needs a more and B "
                 "alone needs b more, then t is the square root of a times b. Inlets only.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "extra")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "root")
        self.play(FadeIn(law, scale=1.03))
        self.at_word(n, "only")
        self.play(FadeIn(only, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="extra_time_02",
            text="A needs eight more and B eighteen more: t is the square root of one hundred and forty-four, twelve.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "root")
        self.play(FadeIn(eg[0], shift=UP * 0.1))
        self.at_word(n, "twelve")
        self.play(FadeIn(eg[1], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="extra_time_03",
            text="Check: twenty and thirty minutes give one twentieth plus one thirtieth, one twelfth.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Check")
        self.play(FadeIn(check, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S07_extra_time")

    # ============================================== 8. FORMULA BOX ==========

    def formula_box(self):
        self.scene_start("S08_formula_box", title="Formula Box")

        head = self.heading("Formula box", GOOD)
        lines = VGroup(*[text(f, LABEL, INK) for f in FORMULAS]).arrange(DOWN, buff=0.45, aligned_edge=LEFT)
        fit_width(lines, SAFE_W - 1.6)
        box = self.card(lines, width=SAFE_W - 0.4, color=GOOD, pad=0.5)
        self.stack(head, [box], top=0.7)

        n = self.narrate(
            id="formula_box_01",
            text="Here is the formula box. Two inlets: x y over x plus y; fill x, empty y: x y over y minus x.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "box")
        self.play(FadeIn(box[0]))
        self.at_word(n, "inlets")
        self.play(FadeIn(lines[0], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_box_02",
            text="The missing pipe: x t over x minus t for an inlet, x t over t minus x for an outlet or a leak.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "missing")
        self.play(FadeIn(lines[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_box_03",
            text="Inlets x and y with outlet z: x y z over y z plus z x minus x y.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "outlet")
        self.play(FadeIn(lines[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_box_04",
            text="B closed d before full: x times y plus d, over x plus y.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "closed")
        self.play(FadeIn(lines[3], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_box_05",
            text="And two inlets with extra times a and b: the square root of a b.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "extra")
        self.play(FadeIn(lines[4], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S08_formula_box")

    # ============================================== 9. WHEN IT FAILS ==========

    def when_it_fails(self):
        self.scene_start("S09_when_it_fails", title="When It Fails")

        head = self.heading("When it fails", BAD)
        blocks = two_line_blocks(FAILS, BAD)
        self.stack(head, list(blocks), buff=0.4, top=0.5, align=LEFT)

        n = self.narrate(
            id="when_it_fails_01",
            text="Shortcuts one to four and six assume every pipe runs from the start until the tank is full. If a pipe "
                 "opens later, closes early, takes turns or starts at a level, go back to the timeline and units of video "
                 "three.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "assume")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "back")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="when_it_fails_02",
            text="X y over y minus x needs y bigger than x. If the outlet is faster, the empty tank never fills, and a "
                 "full tank empties in x y over x minus y.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "needs")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "faster")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="when_it_fails_03",
            text="The three-pipe formula needs a positive denominator. If it is zero or negative, the outlet wins and the "
                 "tank never fills.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "positive")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "wins")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="when_it_fails_04",
            text="The square root of a b works only for two inlets that run together throughout, with a and b measured "
                 "from the joint time. It does not apply when one pipe is an outlet.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "root")
        self.play(FadeIn(blocks[3][0], shift=RIGHT * 0.2))
        self.at_word(n, "apply")
        self.play(FadeIn(blocks[3][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="when_it_fails_05",
            text="Litre questions need the capacity or a flow; these formulas give times only.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Litre")
        self.play(FadeIn(blocks[4][0], shift=RIGHT * 0.2))
        self.at_word(n, "only")
        self.play(FadeIn(blocks[4][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S09_when_it_fails")

    # ============================================== 10. TRAPS AND CONFUSING QUESTIONS ==========

    def the_trap(self):
        self.scene_start("S10_the_trap", title="Traps and Confusing Questions")

        head, q, wrong, right, rule = self.show_trap(TRAPS[0])

        n = self.narrate(
            id="the_trap_01",
            text="The trap: the two-inlet formula used with an outlet. Fill in twelve minutes, empty in twenty minutes, "
                 "both open: what is the time to fill?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "trap")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "Fill")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="the_trap_02",
            text="The wrong instinct uses twelve times twenty over thirty-two: seven and a half minutes. The correct "
                 "formula is twelve times twenty over eight: thirty minutes.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "wrong")
        self.play(FadeIn(wrong, shift=UP * 0.1))
        self.at_word(n, "correct")
        self.play(FadeIn(right, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="the_trap_03",
            text="The rule: an outlet changes the plus to a minus. Decide the sign before choosing the formula.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "rule")
        self.play(FadeIn(rule, shift=UP * 0.1))
        self.at_word(n, "Decide")
        self.play(Indicate(rule, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S10_the_trap")

    # ============================================== 11. TIMED DRILLS ==========

    def timed_drills(self):
        self.scene_start("S11_timed_drills", title="Timed Drills")

        head, q, ans = self.drill(1, DRILLS[0])

        n = self.narrate(
            id="timed_drills_01",
            text="Drill one, five seconds: fill in ten hours, empty in fifteen hours, both open. What is the time to fill?",
            voice="default",
            subtitle=True,
            pause_after=5.0,
        )
        self.at_word(n, "Drill")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "fill")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="timed_drills_02",
            text="One hundred and fifty divided by five: thirty hours.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "divided")
        self.play(FadeIn(ans, scale=1.03))
        self.wait_for_narration(n)
        self.clear_stage()

        head, q, ans = self.drill(2, DRILLS[1])

        n = self.narrate(
            id="timed_drills_03",
            text="Drill two, eight seconds: A alone fills in eight minutes; A and B together in six minutes. How long for "
                 "B alone?",
            voice="default",
            subtitle=True,
            pause_after=8.0,
        )
        self.at_word(n, "Drill")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "alone")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="timed_drills_04",
            text="Eight times six, divided by two: twenty-four minutes.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "divided")
        self.play(FadeIn(ans, scale=1.03))
        self.wait_for_narration(n)
        self.clear_stage()

        head, q, ans = self.drill(3, DRILLS[2])

        n = self.narrate(
            id="timed_drills_05",
            text="Drill three, five seconds: a pipe fills a tank in five hours; with a leak, in six hours. How long for "
                 "the leak alone?",
            voice="default",
            subtitle=True,
            pause_after=5.0,
        )
        self.at_word(n, "Drill")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "pipe")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="timed_drills_06",
            text="Five times six, divided by one: thirty hours.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "divided")
        self.play(FadeIn(ans, scale=1.03))
        self.wait_for_narration(n)
        self.clear_stage()

        head, q, ans = self.drill(4, DRILLS[3])

        n = self.narrate(
            id="timed_drills_07",
            text="Drill four, twelve seconds: inlets of six and eight hours, an outlet of twelve hours, all open. What is "
                 "the time to fill?",
            voice="default",
            subtitle=True,
            pause_after=12.0,
        )
        self.at_word(n, "Drill")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "inlets")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="timed_drills_08",
            text="Five hundred and seventy-six divided by one hundred and twenty: four point eight hours.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "divided")
        self.play(FadeIn(ans, scale=1.03))
        self.wait_for_narration(n)
        self.clear_stage()

        head, q, ans = self.drill(5, DRILLS[4])

        n = self.narrate(
            id="timed_drills_09",
            text="Drill five, ten seconds: A fills in twelve minutes, B in six; both start, and B is closed three minutes "
                 "before the tank is full. What is the total time?",
            voice="default",
            subtitle=True,
            pause_after=10.0,
        )
        self.at_word(n, "Drill")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "fills")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="timed_drills_10",
            text="Twelve times nine, divided by eighteen: six minutes.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "divided")
        self.play(FadeIn(ans, scale=1.03))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S11_timed_drills")

    # ============================================== 12. QUICK REVISION ==========

    def quick_revision(self):
        self.scene_start("S12_quick_revision", title="Quick Revision")

        head = self.heading("Quick revision")
        signs = VGroup(pill("two inlets:  plus", WORD, size=LABEL), pill("an inlet and an outlet:  minus", WORD, size=LABEL)).arrange(RIGHT, buff=0.5)
        more = VGroup(pill("missing pipe or leak:  one formula", RATIO, size=SMALL), pill("three pipes:  outlet's terms signed", RATIO, size=SMALL),
                      pill("“closed before full”:  one line", RATIO, size=SMALL)).arrange(RIGHT, buff=0.3)
        fit_width(more, SAFE_W - 0.4)
        only = text("use them only when the pipes run the whole time", LABEL, INK, BOLD)
        box = fit_width(text("xy/(x + y)     xy/(y − x)     xt/(x − t),  xt/(t − x)     xyz/(yz + zx − xy)     x(y + d)/(x + y)     √(ab)",
                             LABEL, GOOD, BOLD), SAFE_W - 0.6)
        nxt = self.breadcrumb("Next", "Lesson 18 Practice Kit", "Lesson 19 · Time & Distance")
        self.stack(head, [signs, more, only, box, nxt], buff=0.65, top=0.8)
        self.no_overlap(*signs)
        self.no_overlap(*more)

        n = self.narrate(
            id="quick_revision_01",
            text="Plus for two inlets, minus for an inlet and an outlet, one formula for the missing pipe or leak, the "
                 "three-pipe formula with the outlet's terms signed, and one line for closed before full.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "Plus")
        self.play(FadeIn(signs[0], shift=UP * 0.1))
        self.at_word(n, "minus")
        self.play(FadeIn(signs[1], shift=UP * 0.1))
        self.at_word(n, "missing")
        self.play(FadeIn(more[0], shift=UP * 0.1))
        self.at_word(n, "three-pipe")
        self.play(FadeIn(more[1], shift=UP * 0.1))
        self.at_word(n, "closed")
        self.play(FadeIn(more[2], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="quick_revision_02",
            text="Use them only when the pipes run the whole time.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "only")
        self.play(FadeIn(only, shift=UP * 0.1), FadeIn(box, scale=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="quick_revision_03",
            text="Next: the lesson eighteen practice kit, and then lesson nineteen, time and distance.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Next")
        self.play(FadeIn(nxt, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S12_quick_revision")

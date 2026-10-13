"""
animation.py for the LMS video generator.

Course : Pre-C-CAT - Section A - Quantitative Aptitude
Video  : Lesson 19 - Time & Distance - 07 - Speed Tricks

Source script:
  C:\\Scripts\\Section A\\Aptitude\\Sessions 13-18 - Pipes, Time Distance, Partnership\\Lesson 19 - Time & Distance\\07 - Speed Tricks.pdf

Built on the golden-reference pattern:
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``;
  * layouts stacked with next_to and guarded with ``no_overlap``; nothing is
    ever animated onto or into another box.

Lesson 19, Video 7 of 7 (Speed Tricks). Not the first video of the lesson: a silent breadcrumb, a one-line recap of Video 6, then today's topic. No spoken course welcome.
The seven shortcuts are spread over three screens, each with the script's live example; every result is checked in the data block. The formula box is set as seven short lines. Subscripted speeds are written as s (slow) and f (fast), the two gaps as p and q, and the after-meeting ratio with its square roots (√b : √a).
Text colours: white and grey, one blue accent, green and red only for right and wrong.
Pauses: 10 seconds on the hook, then the script's own timers on the five drills (5, 5, 10, 8, 10 seconds).
The closing breadcrumb points to the Lesson 19 Practice Kit and then Lesson 20, Partnership.
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


def ms(kmh):
    return Fraction(kmh) * 5 / 18


def late_early(slow, fast, gap_minutes):
    d = slow * fast * Fraction(gap_minutes, 60) / (fast - slow)
    assert (d / slow - d / fast) * 60 == gap_minutes
    return d


# ---- the hook: 3 km/h 15 late, 4 km/h 5 early ----
HOOK = late_early(3, 4, 15 + 5)
assert HOOK == 4 and (HOOK / 3 * 60, HOOK / 4 * 60) == (80, 60) and 80 - 15 == 65 == 60 + 5
assert Fraction(HOOK, 3) == Fraction(65, 60) + Fraction(1, 4) and Fraction(HOOK, 4) == Fraction(65, 60) - Fraction(1, 12)   # the slow way

# ---- the shortcuts ----
assert [ms(k) for k in (18, 36, 54, 72, 90, 108)] == [5, 10, 15, 20, 25, 30] and 12 * Fraction(36, 10) == Fraction(432, 10)
assert Fraction(10 ** 2 - 2 ** 2, 10) == Fraction(96, 10) == Fraction(2 * 12 * 8, 12 + 8)
assert Fraction(3 * 20, 4 - 3) == 60 and 20 / (Fraction(4, 3) - 1) == 60
assert (isqrt(9), isqrt(16), isqrt(16 * 9)) == (3, 4, 12)
assert Fraction(250 * 18, 5 * 90) == 10 == Fraction(250) / ms(90)

# ---- the trap, and the timed drills: (seconds, question, answer) ----
assert late_early(3, 4, 10) == 2
assert ms(126) == 35 and Fraction(20 ** 2 - 4 ** 2, 20) == Fraction(192, 10) and late_early(5, 6, 6 + 4) == 5
assert (isqrt(16), isqrt(9)) == (4, 3) and Fraction(225 * 18, 5 * 81) == 10 == Fraction(225) / ms(81)
DRILLS = [(5, "Convert 126 km/h to m/s.", "126 × 5/18  =  35 m/s"),
          (5, "A boat's still-water speed is 20 km/h and the stream flows at 4 km/h.  Average speed for a round trip?",
           "(400 − 16) ÷ 20  =  19.2 km/h"),
          (10, "5 km/h: 6 minutes late;   6 km/h: 4 minutes early.   Distance?", "30 × (10/60) ÷ 1  =  5 km"),
          (8, "After meeting, A takes 9 hours and B 16 hours.  Ratio of their speeds?", "√16 : √9  =  4 : 3"),
          (10, "Trains of 100 m and 125 m approach each other at 30 and 51 km/h.  Time to cross?", "225 × 18 ÷ (5 × 81)  =  10 s")]

OBJECTIVES = [("Convert between km/h and m/s by sight", "for the common speeds"),
              ("Use one-line formulas", "for speed changes, late-and-early trips, meetings and train crossings"),
              ("Know when each shortcut fails", "check the conditions first")]
FORMULAS = ["km/h × 5/18 = m/s;          m/s × 3.6 = km/h",
            "Round trip:    2xy/(x + y);          boat:    (u² − v²)/u",
            "Late and early:    D = s × f × (p + q)/(f − s)",
            "At a/b of the usual speed, t late:    usual time = at/(b − a)",
            "After meeting:    speed A : speed B = √b : √a;          meeting time √(ab)",
            "Trains:    time (s) = 18 × (sum of lengths)/(5 × relative speed in km/h)",
            "Boats:    u = (D + U)/2,      v = (D − U)/2"]
FAILS = [("Late-and-early needs the same distance and a constant speed on each trip", "a rest, a breakdown or a change of speed midway:  D = S × T, leg by leg"),
         ("(u² − v²)/u needs the same distance downstream and upstream", "otherwise:  total distance ÷ total time"),
         ("The square-root formula needs the same starting moment and constant speeds", "one starts later:  go back to the gap and relative speed"),
         ("The train shortcut needs lengths in metres and speeds in km/h", "a length in km, or a speed already in m/s, breaks the factor 18/5"),
         ("2xy/(x + y) is for equal distances only", "equal times give (x + y)/2")]
TRAPS = [("Trap  ·  late and early minutes subtracted", "3 km/h: 15 minutes late;   4 km/h: 5 minutes early.   Distance?",
          "gap 15 − 5 = 10 min:  D = 2 km", "gap 20 min:  D = 4 km",
          "Late and early sit on opposite sides of the right time: add them.")]


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


class SpeedTricksTimeAndDistanceVideo(LMSScene):
    lesson_title = "Speed Tricks: Time & Distance"

    def construct(self):
        self.camera.background_color = BG

        self.intro()
        self.hook()
        self.objectives()
        self.the_slow_way()
        self.sight_and_river()
        self.late_early_and_fraction()
        self.root_trains_boats()
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

        crumb = self.breadcrumb("Quantitative Aptitude", "Lesson 19 · Time & Distance", "Video 7 of 7")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        recap = VGroup(text("last video", SMALL, MUTED), pill("races:  A : B = L : (L − x)", WORD, size=LABEL)).arrange(DOWN, buff=0.25)
        title = fit_width(text("Speed Tricks: Time & Distance", TITLE, INK, BOLD), SAFE_W - 0.4)
        today = text("today: forty seconds of working, in one line", LABEL, FOCUS)
        block = VGroup(recap, title, today).arrange(DOWN, buff=0.7)
        fit_within(block, SAFE_W, SAFE_H - crumb.height - 0.9)
        block.next_to(crumb, DOWN, buff=0.7)
        self.no_overlap(crumb, recap, title, today)
        self.validator.check_in_frame(VGroup(crumb, block))

        n = self.narrate(
            id="intro_01",
            text="In the last video, a race gave a ratio: A to B is L to L minus x.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.at_word(n, "ratio")
        self.play(FadeIn(recap, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="intro_02",
            text="Today: speed tricks for time and distance, forty seconds of working done in one line.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "speed")
        self.play(FadeIn(title, shift=UP * 0.1))
        self.at_word(n, "line")
        self.play(FadeIn(today, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_intro")

    # ============================================== 1. HOOK ==========

    def hook(self):
        self.scene_start("S01_hook", title="Hook")

        head = self.heading("Ten seconds")
        given = VGroup(pill("3 km/h:  15 minutes late", BAD, size=BODY), pill("4 km/h:  5 minutes early", GOOD, size=BODY)).arrange(RIGHT, buff=0.6)
        ask = pill("how far does he walk?", FOCUS, size=BODY)
        target = VGroup(text("two equations: about forty seconds", LABEL, MUTED), text("today's target: one line", LABEL, INK, BOLD)).arrange(RIGHT, buff=0.8)
        self.stack(head, [given, ask, target], buff=0.9, top=1.0)
        self.no_overlap(*given)
        self.no_overlap(*target)

        n = self.narrate(
            id="hook_01",
            text="Ten seconds. Walking at three kilometres per hour, a man is fifteen minutes late; at four kilometres per "
                 "hour, he is five minutes early. How far does he walk?",
            voice="default",
            subtitle=True,
            pause_after=10.0,
        )
        self.at_word(n, "Ten")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "late")
        self.play(FadeIn(given[0], shift=UP * 0.1))
        self.at_word(n, "early")
        self.play(FadeIn(given[1], shift=UP * 0.1))
        self.at_word(n, "far")
        self.play(FadeIn(ask, scale=1.03))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="hook_02",
            text="Two equations in the distance and the correct time will get there in about forty seconds. Today's target "
                 "is one line.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "equations")
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
            text="First, convert between kilometres per hour and metres per second by sight, for the common speeds.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "sight")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "common")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="objectives_03",
            text="Second, use one-line formulas for speed changes, late and early trips, meetings and train crossings.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "formulas")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "changes")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="objectives_04",
            text="Third, know when each shortcut fails, and check the conditions first.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "fails")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "conditions")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_objectives")

    # ============================================== 3. THE SLOW WAY ==========

    def the_slow_way(self):
        self.scene_start("S03_the_slow_way", title="The Slow Way")

        head = self.heading("The slow way:  two equations", BAD)
        lines = VGroup(text("D/3  =  T + 1/4", BODY, INK, BOLD), text("D/4  =  T − 1/12", BODY, INK, BOLD),
                       text("subtract, solve, substitute", BODY, MUTED, BOLD)).arrange(DOWN, buff=0.5)
        verdict = pill("reliable, but about 40 seconds", BAD, size=LABEL)
        self.stack(head, [lines, verdict], buff=0.9, top=1.0)
        self.no_overlap(*lines)

        n = self.narrate(
            id="the_slow_way_01",
            text="Let the distance be D and the correct time T, write one equation per trip, and eliminate T.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "distance")
        self.play(FadeIn(lines[0], shift=UP * 0.1))
        self.at_word(n, "equation")
        self.play(FadeIn(lines[1], shift=UP * 0.1))
        self.at_word(n, "eliminate")
        self.play(FadeIn(lines[2], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="the_slow_way_02",
            text="Reliable, but about forty seconds.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Reliable")
        self.play(FadeIn(verdict, scale=1.03))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_the_slow_way")

    # ============================================== 4. SHORTCUTS 1 AND 2 - BY SIGHT; THE RIVER ROUND TRIP ==========

    def sight_and_river(self):
        self.scene_start("S04_sight_and_river", title="Shortcuts 1 and 2 - By Sight; the River Round Trip")

        head = self.heading("Shortcuts 1 and 2")
        sight = VGroup(pill("5/18 by sight:   multiples of 18 km/h give whole m/s", WORD, size=LABEL),
                       text("18 → 5      36 → 10      54 → 15      72 → 20      90 → 25      108 → 30", LABEL, GOOD, BOLD),
                       text("going back:    m/s × 3.6 = km/h;      12 m/s = 43.2 km/h", LABEL, INK)).arrange(DOWN, buff=0.3)
        river = VGroup(pill("round trip on a river:   average = (u² − v²)/u,   no distance needed", WORD, size=LABEL),
                       text("u = 10, v = 2:     96 ÷ 10  =  9.6 km/h          (check:  2 × 12 × 8/20 = 9.6)", LABEL, GOOD, BOLD)).arrange(DOWN, buff=0.3)
        self.stack(head, [sight, river], buff=0.9, top=0.8)

        n = self.narrate(
            id="sight_and_river_01",
            text="Shortcut one: five over eighteen by sight. Multiples of eighteen kilometres per hour convert to whole "
                 "metres per second: eighteen gives five, thirty-six ten, fifty-four fifteen, seventy-two twenty, ninety "
                 "twenty-five, and one hundred and eight thirty.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "sight")
        self.play(FadeIn(sight[0], scale=1.03))
        self.at_word(n, "gives")
        self.play(FadeIn(sight[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="sight_and_river_02",
            text="Going back, metres per second times three point six is kilometres per hour: twelve metres per second is "
                 "forty-three point two.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "back")
        self.play(FadeIn(sight[2], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="sight_and_river_03",
            text="Shortcut two: the round-trip average on a river. Equal distances at x and y give two x y over x plus y; "
                 "for a boat, that is u squared minus v squared, over u, with no distance needed.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "river")
        self.play(FadeIn(river[0], scale=1.03))
        self.at_word(n, "squared")
        self.play(Indicate(river[0], color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="sight_and_river_04",
            text="With u ten and v two: ninety-six divided by ten is nine point six kilometres per hour.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "divided")
        self.play(FadeIn(river[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_sight_and_river")

    # ============================================== 5. SHORTCUTS 3 AND 4 - LATE AND EARLY; A FRACTION OF THE USUAL SPEED ==========

    def late_early_and_fraction(self):
        self.scene_start("S05_late_early_and_fraction", title="Shortcuts 3 and 4 - Late and Early; a Fraction of the Usual Speed")

        head = self.heading("Shortcuts 3 and 4")
        late = VGroup(pill("late and early:    D = s × f × (p + q)/(f − s),    gaps in hours", WORD, size=LABEL),
                      text("both trips late:   use p − q", LABEL, MUTED),
                      text("the hook:    3 × 4 × (20/60) ÷ 1  =  4 km         (80 and 60 minutes, either side of 65)", LABEL, GOOD, BOLD))\
            .arrange(DOWN, buff=0.3)
        frac = VGroup(pill("at a/b of the usual speed, late by t:    usual time = a × t/(b − a)", WORD, size=LABEL),
                      text("at 3/4, 20 minutes late:     3 × 20 ÷ 1  =  60 minutes", LABEL, GOOD, BOLD)).arrange(DOWN, buff=0.3)
        self.stack(head, [late, frac], buff=0.9, top=0.8)

        n = self.narrate(
            id="late_early_and_fraction_01",
            text="Shortcut three: late and early. The distance is slow times fast, times the sum of the two gaps in hours, "
                 "over the difference of the speeds; use the difference of the gaps if both trips are late.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "early")
        self.play(FadeIn(late[0], scale=1.03))
        self.at_word(n, "both")
        self.play(FadeIn(late[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="late_early_and_fraction_02",
            text="The hook: three times four, times twenty minutes as a third of an hour, divided by one, is four "
                 "kilometres. Check: eighty minutes and sixty minutes, either side of sixty-five.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "times")
        self.play(FadeIn(late[2], shift=UP * 0.1))
        self.at_word(n, "Check")
        self.play(Indicate(late[2], color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="late_early_and_fraction_03",
            text="Shortcut four: a fraction of the usual speed. At a over b of the usual speed, late by t, the usual time "
                 "is a times t, over b minus a.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "fraction")
        self.play(FadeIn(frac[0], scale=1.03))
        self.at_word(n, "minus")
        self.play(Indicate(frac[0], color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="late_early_and_fraction_04",
            text="At three-quarters, twenty minutes late: three times twenty, divided by one, is sixty minutes.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "divided")
        self.play(FadeIn(frac[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_late_early_and_fraction")

    # ============================================== 6. SHORTCUTS 5, 6 AND 7 - MEETINGS, TRAINS AND BOATS ==========

    def root_trains_boats(self):
        self.scene_start("S06_root_trains_boats", title="Shortcuts 5, 6 and 7 - Meetings, Trains and Boats")

        head = self.heading("Shortcuts 5, 6 and 7")
        root = VGroup(pill("after meeting in a and b hours:    speeds √b : √a,    meeting after √(ab)", WORD, size=LABEL),
                      text("a = 16, b = 9:     speeds 3 : 4,     meeting after 12 hours", LABEL, GOOD, BOLD)).arrange(DOWN, buff=0.3)
        trains = VGroup(pill("trains:    time (s) = (sum of lengths) × 18 ÷ (5 × relative km/h)", WORD, size=LABEL),
                        text("120 m and 130 m, approaching at 40 and 50 km/h:     250 × 18 ÷ 450  =  10 s", LABEL, GOOD, BOLD)).arrange(DOWN, buff=0.3)
        boats = pill("boats:    u = (D + U)/2   and   v = (D − U)/2,    straight from the two speeds", WORD, size=LABEL)
        self.stack(head, [root, trains, boats], buff=0.7, top=0.7)

        n = self.narrate(
            id="root_trains_boats_01",
            text="Shortcut five: the square-root meeting formula. After meeting, A takes a hours and B takes b hours: the "
                 "speeds are as root b to root a, and they met root a b hours after starting.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "square-root")
        self.play(FadeIn(root[0], scale=1.03))
        self.at_word(n, "met")
        self.play(Indicate(root[0], color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="root_trains_boats_02",
            text="With a sixteen and b nine: the speeds are three to four, and they meet after twelve hours.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "three")
        self.play(FadeIn(root[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="root_trains_boats_03",
            text="Shortcut six: train crossings in one step. The time in seconds is the sum of the lengths times eighteen, "
                 "divided by five times the relative speed in kilometres per hour.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "crossings")
        self.play(FadeIn(trains[0], scale=1.03))
        self.at_word(n, "divided")
        self.play(Indicate(trains[0], color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="root_trains_boats_04",
            text="Trains of one hundred and twenty and one hundred and thirty metres, approaching at forty and fifty "
                 "kilometres per hour: two hundred and fifty times eighteen, divided by four hundred and fifty, is ten "
                 "seconds.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "divided")
        self.play(FadeIn(trains[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="root_trains_boats_05",
            text="Shortcut seven: boats. U is the half-sum and v is the half-difference, straight from the two speeds.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "boats")
        self.play(FadeIn(boats, scale=1.03))
        self.at_word(n, "straight")
        self.play(Indicate(boats, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_root_trains_boats")

    # ============================================== 7. FORMULA BOX ==========

    def formula_box(self):
        self.scene_start("S07_formula_box", title="Formula Box")

        head = self.heading("Formula box", GOOD)
        lines = VGroup(*[text(f, LABEL, INK) for f in FORMULAS]).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        fit_width(lines, SAFE_W - 1.6)
        box = self.card(lines, width=SAFE_W - 0.4, color=GOOD, pad=0.5)
        self.stack(head, [box], top=0.7)

        n = self.narrate(
            id="formula_box_01",
            text="Here is the formula box. Kilometres per hour times five over eighteen is metres per second, and metres "
                 "per second times three point six is kilometres per hour.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "box")
        self.play(FadeIn(box[0]))
        self.at_word(n, "five")
        self.play(FadeIn(lines[0], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_box_02",
            text="A round trip is two x y over x plus y, and for a boat, u squared minus v squared, over u.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "round")
        self.play(FadeIn(lines[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_box_03",
            text="Late and early: slow times fast times the sum of the gaps, over the difference of the speeds. At a over "
                 "b of the usual speed and t late, the usual time is a t over b minus a.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Late")
        self.play(FadeIn(lines[2], shift=RIGHT * 0.2))
        self.at_word(n, "usual")
        self.play(FadeIn(lines[3], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_box_04",
            text="After meeting, the speeds are as root b to root a, and the meeting time is root a b.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "root")
        self.play(FadeIn(lines[4], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_box_05",
            text="For trains, the time in seconds is eighteen times the sum of the lengths, over five times the relative "
                 "speed in kilometres per hour; and for boats, the half-sum and the half-difference.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "trains")
        self.play(FadeIn(lines[5], shift=RIGHT * 0.2))
        self.at_word(n, "boats")
        self.play(FadeIn(lines[6], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S07_formula_box")

    # ============================================== 8. WHEN IT FAILS ==========

    def when_it_fails(self):
        self.scene_start("S08_when_it_fails", title="When It Fails")

        head = self.heading("When it fails", BAD)
        blocks = two_line_blocks(FAILS, BAD)
        self.stack(head, list(blocks), buff=0.4, top=0.5, align=LEFT)

        n = self.narrate(
            id="when_it_fails_01",
            text="The late and early formula assumes the same distance and a constant speed on each trip. A rest, a "
                 "breakdown or a change of speed midway needs D equals S times T, leg by leg.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "assumes")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "rest")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="when_it_fails_02",
            text="U squared minus v squared, over u, needs the same distance downstream and upstream; otherwise use total "
                 "distance over total time.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "needs")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "otherwise")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="when_it_fails_03",
            text="The square-root formula needs both to start at the same moment and keep constant speeds. If one starts "
                 "later, go back to the gap and relative speed.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "square-root")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "later")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="when_it_fails_04",
            text="The train shortcut needs lengths in metres and speeds in kilometres per hour. A length in kilometres, or "
                 "a speed already in metres per second, breaks the factor.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "train")
        self.play(FadeIn(blocks[3][0], shift=RIGHT * 0.2))
        self.at_word(n, "breaks")
        self.play(FadeIn(blocks[3][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="when_it_fails_05",
            text="Two x y over x plus y is for equal distances only. Equal times give x plus y over two.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "only")
        self.play(FadeIn(blocks[4][0], shift=RIGHT * 0.2))
        self.at_word(n, "times")
        self.play(FadeIn(blocks[4][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S08_when_it_fails")

    # ============================================== 9. TRAPS AND CONFUSING QUESTIONS ==========

    def the_trap(self):
        self.scene_start("S09_the_trap", title="Traps and Confusing Questions")

        head, q, wrong, right, rule = self.show_trap(TRAPS[0])

        n = self.narrate(
            id="the_trap_01",
            text="The trap: late and early minutes subtracted. At three kilometres per hour, fifteen minutes late; at "
                 "four, five minutes early: what is the distance?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "trap")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "fifteen")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="the_trap_02",
            text="The wrong instinct takes the gap as fifteen minus five, ten minutes, and gets two kilometres. The "
                 "correct gap is twenty minutes, and the distance is four kilometres.",
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
            text="The rule: late and early sit on opposite sides of the right time, so add them.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "rule")
        self.play(FadeIn(rule, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S09_the_trap")

    # ============================================== 10. TIMED DRILLS ==========

    def timed_drills(self):
        self.scene_start("S10_timed_drills", title="Timed Drills")

        head, q, ans = self.drill(1, DRILLS[0])

        n = self.narrate(
            id="timed_drills_01",
            text="Drill one, five seconds: convert one hundred and twenty-six kilometres per hour to metres per second.",
            voice="default",
            subtitle=True,
            pause_after=5.0,
        )
        self.at_word(n, "Drill")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "convert")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="timed_drills_02",
            text="One hundred and twenty-six times five over eighteen is thirty-five metres per second.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "over")
        self.play(FadeIn(ans, scale=1.03))
        self.wait_for_narration(n)
        self.clear_stage()

        head, q, ans = self.drill(2, DRILLS[1])

        n = self.narrate(
            id="timed_drills_03",
            text="Drill two, five seconds: a boat's still-water speed is twenty kilometres per hour and the stream flows "
                 "at four. What is the average speed for a round trip?",
            voice="default",
            subtitle=True,
            pause_after=5.0,
        )
        self.at_word(n, "Drill")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "stream")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="timed_drills_04",
            text="Four hundred minus sixteen, divided by twenty: nineteen point two kilometres per hour.",
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
            text="Drill three, ten seconds: at five kilometres per hour, six minutes late; at six, four minutes early. "
                 "What is the distance?",
            voice="default",
            subtitle=True,
            pause_after=10.0,
        )
        self.at_word(n, "Drill")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "late")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="timed_drills_06",
            text="Thirty times ten minutes as a sixth of an hour, divided by one: five kilometres.",
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
            text="Drill four, eight seconds: after meeting, A takes nine hours and B sixteen hours. What is the ratio of "
                 "their speeds?",
            voice="default",
            subtitle=True,
            pause_after=8.0,
        )
        self.at_word(n, "Drill")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "meeting")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="timed_drills_08",
            text="Root sixteen to root nine: four to three.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Root")
        self.play(FadeIn(ans, scale=1.03))
        self.wait_for_narration(n)
        self.clear_stage()

        head, q, ans = self.drill(5, DRILLS[4])

        n = self.narrate(
            id="timed_drills_09",
            text="Drill five, ten seconds: trains of one hundred and one hundred and twenty-five metres approach each "
                 "other at thirty and fifty-one kilometres per hour. What is the time to cross?",
            voice="default",
            subtitle=True,
            pause_after=10.0,
        )
        self.at_word(n, "Drill")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "trains")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="timed_drills_10",
            text="Two hundred and twenty-five times eighteen, divided by five times eighty-one: ten seconds.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "divided")
        self.play(FadeIn(ans, scale=1.03))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S10_timed_drills")

    # ============================================== 11. QUICK REVISION ==========

    def quick_revision(self):
        self.scene_start("S11_quick_revision", title="Quick Revision")

        head = self.heading("Quick revision")
        first = VGroup(pill("convert by sight", WORD, size=LABEL), pill("round trips:  2xy/(x + y);   boat (u² − v²)/u", WORD, size=LABEL))\
            .arrange(RIGHT, buff=0.4)
        second = VGroup(pill("add the late and early minutes", RATIO, size=SMALL), pill("after meeting:  √b : √a", RATIO, size=SMALL),
                        pill("trains:  fold in the 18/5", RATIO, size=SMALL)).arrange(RIGHT, buff=0.3)
        fit_width(second, SAFE_W - 0.4)
        check = text("check the conditions before each shortcut", LABEL, INK, BOLD)
        nxt = self.breadcrumb("Next", "Lesson 19 Practice Kit", "Lesson 20 · Partnership")
        self.stack(head, [first, second, check, nxt], buff=0.75, top=0.9)
        self.no_overlap(*first)
        self.no_overlap(*second)

        n = self.narrate(
            id="quick_revision_01",
            text="Convert by sight, use two x y over x plus y, or u squared minus v squared over u for a boat, for round "
                 "trips, add the late and early minutes, use root b to root a after meeting, and fold the eighteen over "
                 "five into train crossings.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "sight")
        self.play(FadeIn(first[0], shift=UP * 0.1))
        self.at_word(n, "round")
        self.play(FadeIn(first[1], shift=UP * 0.1))
        self.at_word(n, "add")
        self.play(FadeIn(second[0], shift=UP * 0.1))
        self.at_word(n, "root")
        self.play(FadeIn(second[1], shift=UP * 0.1))
        self.at_word(n, "fold")
        self.play(FadeIn(second[2], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="quick_revision_02",
            text="Check the conditions before each shortcut.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "conditions")
        self.play(FadeIn(check, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="quick_revision_03",
            text="Next: the lesson nineteen practice kit, and then lesson twenty, partnership.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Next")
        self.play(FadeIn(nxt, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S11_quick_revision")

"""
animation.py for the LMS video generator.

Course : Pre-C-CAT - Section A - Quantitative Aptitude
Video  : Lesson 20 - Partnership - 04 - Speed Tricks

Source script:
  C:\\Scripts\\Section A\\Aptitude\\Sessions 13-18 - Pipes, Time Distance, Partnership\\Lesson 20 - Partnership\\04 - Speed Tricks.pdf

Built on the golden-reference pattern:
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``;
  * layouts stacked with next_to and guarded with ``no_overlap``; nothing is
    ever animated onto or into another box.

Lesson 20, Video 4 of 4 (Speed Tricks). Not the first video of the lesson: a silent breadcrumb, a one-line recap of Video 3, then today's topic. No spoken course welcome.
The five shortcuts are spread over three screens, each with the script's live examples; every result is checked in the data block.
Text colours: white and grey, one blue accent, green and red only for right and wrong.
Pauses: 10 seconds on the hook, then the script's own timers on the five drills (8, 6, 6, 8, 10 seconds).
The closing breadcrumb points to the Lesson 20 Practice Kit and then Lesson 21, Probability.
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
from math import gcd
from functools import reduce


def ratio(*values):
    """Smallest whole-number ratio of the given values (fractions allowed)."""
    values = [Fraction(v) for v in values]
    scale = reduce(lambda a, b: a * b // gcd(a, b), [v.denominator for v in values])
    whole = [int(v * scale) for v in values]
    g = reduce(gcd, whole)
    return [w // g for w in whole]


# ---- the hook ----
assert 12000 * 12 == 16000 * 9 == 18000 * 8 == 144000 and ratio(12 * 12, 16 * 9, 18 * 8) == [1, 1, 1]

# ---- the shortcuts ----
assert ratio(45000 * 8, 60000 * 9) == [2, 3] and ratio(45, 60) == [3, 4] and (3 * 8, 4 * 9) == (24, 36)
assert ratio(Fraction(1, 2), Fraction(1, 3), Fraction(1, 4)) == [6, 4, 3] and ratio(Fraction(2, 3), Fraction(3, 4), Fraction(5, 6)) == [8, 9, 10]
assert Fraction(4000, 5 - 3) == 2000 and (5 + 3) * 2000 == 16000
assert ratio(Fraction(5, 3), Fraction(4, 2)) == [5, 6] and 40000 * 12 // 60000 == 8 and 12 - 8 == 4
assert Fraction(10, 100) + Fraction(90, 100) * Fraction(3, 5) == Fraction(64, 100)

# ---- the trap, and the timed drills: (seconds, question, answer) ----
REST = (20000 - 12000) * 5
assert REST == 40000 and 12000 + REST == 52000 and (12000 + REST * 3 // 5) - REST * 2 // 5 == 20000 and 20000 * 5 == 100000
assert ratio(25000 * 12, 30000 * 10) == [1, 1] and ratio(Fraction(1, 3), Fraction(1, 4), Fraction(1, 6)) == [4, 3, 2]
assert Fraction(6000, 7 - 5) == 3000 and (7 + 5) * 3000 == 36000 and ratio(Fraction(9, 3), Fraction(10, 5)) == [3, 2]
assert 30000 * 12 * Fraction(2, 3) == 240000 and 240000 // 40000 == 6 and 12 - 6 == 6
DRILLS = [(8, "A invests ₹25,000 for 12 months and B ₹30,000 for 10 months.  Profit ratio?", "25 × 12 : 30 × 10  =  300 : 300  =  1 : 1"),
          (6, "Capitals in the ratio 1/3 : 1/4 : 1/6 for the same period.  Whole-number ratio?", "× 12  =  4 : 3 : 2"),
          (6, "Profits are in the ratio 7 : 5, and A gets ₹6,000 more than B.  Total profit?", "1 part = 3,000;    total 12 × 3,000  =  ₹36,000"),
          (8, "Capitals are 3 : 5 and profits 9 : 10.  Ratio of times?", "9/3 : 10/5  =  3 : 2"),
          (10, "A invests ₹30,000 all year.  B joins with ₹40,000, and the profits are shared 3 : 2.  After how many months did B join?",
           "2,40,000 ÷ 40,000 = 6 months in:    joined after 6 months")]

OBJECTIVES = [("Write a capital-month ratio in one line", "by cancelling before multiplying"),
              ("Clear fractional ratios with the LCM", "and get a total profit straight from a difference"),
              ("Find an unknown time or joining month in one step", "and know when each shortcut fails")]
FORMULAS = ["Cancel first:     capital × time ratios, with common factors removed",
            "Fractions:     × LCM of the denominators",
            "Difference d, ratio a : b:     1 part = d/(a − b),       total = (a + b) × d/(a − b)",
            "Time follows P/C;       joiner's months = needed capital-months ÷ capital",
            "Working partner:     k% + (100 − k)% × s"]
FAILS = [("The one-line ratio needs each partner's capital to stay constant", "with a withdrawal or an addition, add the segments first"),
         ("The difference shortcut needs the whole profit to be shared in the ratio", "a salary or commission paid first is inside the difference:  use the percentage form, or an equation in P"),
         ("The reverse-time shortcut assumes sharing purely by capital × time", "if a working partner is paid first, remove that payment before forming the profit ratio"),
         ("The LCM trick turns capitals into whole numbers;  it does not include time", "still multiply by months if the periods differ")]
TRAPS = [("Trap  ·  share from a difference with a salary paid first",
          "Capitals 3 : 2.  A gets ₹12,000 for managing first, then the rest 3 : 2.  A receives ₹20,000 more than B.  Total profit?",
          "1 part = 20,000:  ₹1,00,000", "R/5 = 8,000:  profit ₹52,000",
          "Remove the working partner's payment from the difference before using the ratio.")]


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


class SpeedTricksPartnershipVideo(LMSScene):
    lesson_title = "Speed Tricks: Partnership"

    def construct(self):
        self.camera.background_color = BG

        self.intro()
        self.hook()
        self.objectives()
        self.the_slow_way()
        self.one_line_and_lcm()
        self.difference_and_reverse_time()
        self.one_percentage()
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
        ans = fit_width(pill(answer, GOOD, size=BODY if len(answer) <= 45 else LABEL), SAFE_W)
        self.stack(head, [q, ans], buff=1.0, top=1.0)
        return head, q, ans

    # ============================================== 0. INTRO ==========
    # Not the first video: silent breadcrumb, a one-line recap of the previous video, then today's topic.

    def intro(self):
        self.scene_start("S00_intro", title="Intro")

        crumb = self.breadcrumb("Quantitative Aptitude", "Lesson 20 · Partnership", "Video 4 of 4")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        recap = VGroup(text("last video", SMALL, MUTED), pill("pay the working partner first, then share", WORD, size=LABEL)).arrange(DOWN, buff=0.25)
        title = fit_width(text("Speed Tricks: Partnership", TITLE, INK, BOLD), SAFE_W - 0.4)
        today = text("today: cancel first, multiply last", LABEL, FOCUS)
        block = VGroup(recap, title, today).arrange(DOWN, buff=0.7)
        fit_within(block, SAFE_W, SAFE_H - crumb.height - 0.9)
        block.next_to(crumb, DOWN, buff=0.7)
        self.no_overlap(crumb, recap, title, today)
        self.validator.check_in_frame(VGroup(crumb, block))

        n = self.narrate(
            id="intro_01",
            text="In the last video, you paid the working partner first and then shared the remainder.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.at_word(n, "first")
        self.play(FadeIn(recap, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="intro_02",
            text="Today: speed tricks for partnership: cancel first, multiply last.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "speed")
        self.play(FadeIn(title, shift=UP * 0.1))
        self.at_word(n, "cancel")
        self.play(FadeIn(today, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_intro")

    # ============================================== 1. HOOK ==========

    def hook(self):
        self.scene_start("S01_hook", title="Hook")

        head = self.heading("Ten seconds")
        given = VGroup(pill("A:  ₹12,000 for 12 months", WORD, size=LABEL), pill("B:  ₹16,000 for 9 months", WORD, size=LABEL),
                       pill("C:  ₹18,000 for 8 months", WORD, size=LABEL)).arrange(RIGHT, buff=0.35)
        ask = pill("ratio of their profits?", FOCUS, size=BODY)
        target = VGroup(text("three five-digit products: slow, and slips creep in", LABEL, MUTED),
                        text("today: cancel first, multiply last, one line", LABEL, INK, BOLD)).arrange(DOWN, buff=0.25)
        self.stack(head, [given, ask, target], buff=0.8, top=0.9)
        self.no_overlap(*given)

        n = self.narrate(
            id="hook_01",
            text="Ten seconds. A invests twelve thousand rupees for twelve months, B sixteen thousand for nine months, and "
                 "C eighteen thousand for eight months. What is the ratio of their profits?",
            voice="default",
            subtitle=True,
            pause_after=10.0,
        )
        self.at_word(n, "Ten")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "invests")
        self.play(FadeIn(given[0], shift=UP * 0.1))
        self.at_word(n, "sixteen")
        self.play(FadeIn(given[1], shift=UP * 0.1))
        self.at_word(n, "eighteen")
        self.play(FadeIn(given[2], shift=UP * 0.1))
        self.at_word(n, "ratio")
        self.play(FadeIn(ask, scale=1.03))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="hook_02",
            text="Multiplying out three five-digit products takes time and invites slips. Today's target: cancel first, "
                 "multiply last, and answer in one line.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "products")
        self.play(FadeIn(target[0], shift=UP * 0.1))
        self.at_word(n, "cancel")
        self.play(FadeIn(target[1], shift=UP * 0.1))
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
            text="First, write a capital-month ratio in one line by cancelling before multiplying.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "line")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "cancelling")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="objectives_03",
            text="Second, clear fractional ratios with the L C M, and get a total profit straight from a difference.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "clear")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "difference")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="objectives_04",
            text="Third, find an unknown time or joining month in one step, and know when each shortcut fails.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "unknown")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "fails")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_objectives")

    # ============================================== 3. THE SLOW WAY ==========

    def the_slow_way(self):
        self.scene_start("S03_the_slow_way", title="The Slow Way")

        head = self.heading("The slow way:  full products", BAD)
        lines = VGroup(text("12,000 × 12  =  1,44,000", BODY, INK, BOLD), text("16,000 × 9  =  1,44,000", BODY, INK, BOLD),
                       text("18,000 × 8  =  1,44,000", BODY, INK, BOLD)).arrange(DOWN, buff=0.5)
        verdict = pill("reliable, but about 25 seconds", BAD, size=LABEL)
        self.stack(head, [lines, verdict], buff=0.9, top=1.0)
        self.no_overlap(*lines)

        n = self.narrate(
            id="the_slow_way_01",
            text="Multiply each capital by its months, write the full products, then simplify.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "Multiply")
        self.play(FadeIn(lines[0], shift=UP * 0.1))
        self.at_word(n, "products")
        self.play(FadeIn(lines[1], shift=UP * 0.1))
        self.at_word(n, "simplify")
        self.play(FadeIn(lines[2], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="the_slow_way_02",
            text="Reliable, but about twenty-five seconds.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Reliable")
        self.play(FadeIn(verdict, scale=1.03))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_the_slow_way")

    # ============================================== 4. SHORTCUTS 1 AND 2 - THE ONE-LINE RATIO; THE LCM ==========

    def one_line_and_lcm(self):
        self.scene_start("S04_one_line_and_lcm", title="Shortcuts 1 and 2 - The One-Line Ratio; the LCM")

        head = self.heading("Shortcuts 1 and 2")
        one = VGroup(pill("capital-month ratio in one line:   drop zeros, cancel factors, then multiply", WORD, size=LABEL),
                     text("the hook:     12 × 12 : 16 × 9 : 18 × 8  =  144 : 144 : 144  =  1 : 1 : 1", LABEL, GOOD, BOLD),
                     text("45,000 × 8 and 60,000 × 9:     45 : 60 = 3 : 4;      3 × 8 : 4 × 9 = 24 : 36 = 2 : 3", LABEL, GOOD, BOLD))\
            .arrange(DOWN, buff=0.3)
        two = VGroup(pill("LCM to clear fractions:   multiply every term by the LCM of the denominators", WORD, size=LABEL),
                     text("1/2 : 1/3 : 1/4,  × 12  =  6 : 4 : 3             2/3 : 3/4 : 5/6,  × 12  =  8 : 9 : 10", LABEL, GOOD, BOLD))\
            .arrange(DOWN, buff=0.3)
        self.stack(head, [one, two], buff=0.8, top=0.7)

        n = self.narrate(
            id="one_line_and_lcm_01",
            text="Shortcut one: the capital-month ratio in one line. Drop the common zeros, cancel common factors, then "
                 "multiply.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "line")
        self.play(FadeIn(one[0], scale=1.03))
        self.at_word(n, "cancel")
        self.play(Indicate(one[0], color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="one_line_and_lcm_02",
            text="The hook: twelve times twelve, sixteen times nine and eighteen times eight are all one hundred and "
                 "forty-four: one to one to one.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "times")
        self.play(FadeIn(one[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="one_line_and_lcm_03",
            text="For forty-five thousand times eight and sixty thousand times nine: forty-five to sixty is three to four, "
                 "so three times eight to four times nine is twenty-four to thirty-six: two to three.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "thousand")
        self.play(FadeIn(one[2], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="one_line_and_lcm_04",
            text="Shortcut two: the L C M to clear fractions. Multiply every term by the L C M of the denominators.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "fractions")
        self.play(FadeIn(two[0], scale=1.03))
        self.at_word(n, "Multiply")
        self.play(Indicate(two[0], color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="one_line_and_lcm_05",
            text="A half, a third and a quarter, times twelve, give six to four to three; two thirds, three quarters and "
                 "five sixths, times twelve, give eight to nine to ten.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "give")
        self.play(FadeIn(two[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_one_line_and_lcm")

    # ============================================== 5. SHORTCUTS 3 AND 4 - SHARE FROM A DIFFERENCE; REVERSE TIME ==========

    def difference_and_reverse_time(self):
        self.scene_start("S05_difference_and_reverse_time", title="Shortcuts 3 and 4 - Share from a Difference; Reverse Time")

        head = self.heading("Shortcuts 3 and 4")
        three = VGroup(pill("share from a difference:   ratio a : b, A gets d more;    1 part = d ÷ (a − b)", WORD, size=LABEL),
                       text("ratio 5 : 3, A gets ₹4,000 more:     1 part = ₹2,000;      total = 8 × 2,000 = ₹16,000", LABEL, GOOD, BOLD))\
            .arrange(DOWN, buff=0.3)
        four = VGroup(pill("reverse time:   time follows profit ÷ capital", WORD, size=LABEL),
                      text("capitals 3 : 2, profits 5 : 4:     times = 5/3 : 4/2 = 5 : 6", LABEL, GOOD, BOLD),
                      text("a joiner:   months in = capital-months needed ÷ capital;    joined after 12 − that", LABEL, INK),
                      text("A ₹40,000 all year, B ₹60,000, equal profits:     4,80,000 ÷ 60,000 = 8 months in;    joined after 4",
                           LABEL, GOOD, BOLD)).arrange(DOWN, buff=0.3)
        fit_width(four, SAFE_W - 0.6)
        self.stack(head, [three, four], buff=0.7, top=0.6)

        n = self.narrate(
            id="difference_and_reverse_time_01",
            text="Shortcut three: the share from a difference. If the ratio is a to b and A gets d more than B, then one "
                 "part is d divided by a minus b, and the total is a plus b parts.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "difference")
        self.play(FadeIn(three[0], scale=1.03))
        self.at_word(n, "divided")
        self.play(Indicate(three[0], color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="difference_and_reverse_time_02",
            text="With a ratio of five to three and A getting four thousand rupees more: one part is two thousand, and the "
                 "total is eight times two thousand, sixteen thousand rupees.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "part")
        self.play(FadeIn(three[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="difference_and_reverse_time_03",
            text="Shortcut four: reverse time. Time follows profit divided by capital. With capitals three to two and "
                 "profits five to four, the times are five thirds to four halves: five to six.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "reverse")
        self.play(FadeIn(four[0], scale=1.03))
        self.at_word(n, "divided")
        self.play(Indicate(four[0], color=FOCUS, scale_factor=1.03))
        self.at_word(n, "thirds")
        self.play(FadeIn(four[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="difference_and_reverse_time_04",
            text="For a joiner, the months in are the capital-months needed, divided by the capital, and the partner "
                 "joined after twelve minus that.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "joiner")
        self.play(FadeIn(four[2], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="difference_and_reverse_time_05",
            text="A, forty thousand all year, B, sixty thousand, with equal profits: B is in for four lakh eighty thousand "
                 "divided by sixty thousand, eight months, so B joined after four months.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "lakh")
        self.play(FadeIn(four[3], shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_difference_and_reverse_time")

    # ============================================== 6. SHORTCUT 5 - THE WORKING PARTNER AS ONE PERCENTAGE ==========

    def one_percentage(self):
        self.scene_start("S06_one_percentage", title="Shortcut 5 - The Working Partner as One Percentage")

        head = self.heading("Shortcut 5  ·  the working partner as one percentage")
        law = pill("k% for managing, capital share s:    working partner gets  k% + (100 − k)% × s", WORD, size=LABEL)
        eg = text("10% for managing, capitals 3 : 2:     10% + 90% × 3/5  =  64% of the profit", BODY, GOOD, BOLD)
        fit_width(eg, SAFE_W - 0.6)
        self.stack(head, [law, eg], buff=1.1, top=1.3)

        n = self.narrate(
            id="one_percentage_01",
            text="Shortcut five: the working partner as one percentage. With k percent for managing and a capital share s, "
                 "the working partner gets k percent, plus one hundred minus k percent times s, of the profit.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "percentage")
        self.play(FadeIn(law, scale=1.03))
        self.at_word(n, "plus")
        self.play(Indicate(law, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="one_percentage_02",
            text="Ten percent for managing with capitals three to two: ten percent plus ninety percent times three fifths "
                 "is sixty-four percent.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "plus")
        self.play(FadeIn(eg, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_one_percentage")

    # ============================================== 7. FORMULA BOX ==========

    def formula_box(self):
        self.scene_start("S07_formula_box", title="Formula Box")

        head = self.heading("Formula box", GOOD)
        lines = VGroup(*[text(f, LABEL, INK) for f in FORMULAS]).arrange(DOWN, buff=0.45, aligned_edge=LEFT)
        fit_width(lines, SAFE_W - 1.6)
        box = self.card(lines, width=SAFE_W - 0.4, color=GOOD, pad=0.5)
        self.stack(head, [box], top=0.7)

        n = self.narrate(
            id="formula_box_01",
            text="Here is the formula box. Cancel first: write the capital times time ratio with the common factors "
                 "removed.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "box")
        self.play(FadeIn(box[0]))
        self.at_word(n, "Cancel")
        self.play(FadeIn(lines[0], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_box_02",
            text="For fractions, multiply by the L C M of the denominators.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "fractions")
        self.play(FadeIn(lines[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_box_03",
            text="For a difference d and a ratio a to b, one part is d over a minus b, and the total is a plus b parts.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "difference")
        self.play(FadeIn(lines[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_box_04",
            text="Time follows profit over capital, and a joiner's months are the needed capital-months divided by the "
                 "capital.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Time")
        self.play(FadeIn(lines[3], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_box_05",
            text="And the working partner gets k percent, plus one hundred minus k percent, times s.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "working")
        self.play(FadeIn(lines[4], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S07_formula_box")

    # ============================================== 8. WHEN IT FAILS ==========

    def when_it_fails(self):
        self.scene_start("S08_when_it_fails", title="When It Fails")

        head = self.heading("When it fails", BAD)
        blocks = two_line_blocks(FAILS, BAD)
        self.stack(head, list(blocks), buff=0.5, top=0.7, align=LEFT)

        n = self.narrate(
            id="when_it_fails_01",
            text="The one-line ratio needs each partner's capital to stay constant. With a withdrawal or an addition, add "
                 "the segments first.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "constant")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "segments")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="when_it_fails_02",
            text="The difference shortcut needs the whole profit to be shared in the ratio. If a salary or commission is "
                 "paid first, the difference includes that payment; use the percentage form, or an equation in P.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "whole")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "includes")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="when_it_fails_03",
            text="The reverse-time shortcut assumes the profit is shared purely by capital times time. If a working "
                 "partner is paid first, remove that payment before forming the profit ratio.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "purely")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "remove")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="when_it_fails_04",
            text="The L C M trick turns capitals into whole numbers; it does not include time. Still multiply by months if "
                 "the periods differ.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "whole")
        self.play(FadeIn(blocks[3][0], shift=RIGHT * 0.2))
        self.at_word(n, "Still")
        self.play(FadeIn(blocks[3][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S08_when_it_fails")

    # ============================================== 9. TRAPS AND CONFUSING QUESTIONS ==========

    def the_trap(self):
        self.scene_start("S09_the_trap", title="Traps and Confusing Questions")

        head, q, wrong, right, rule = self.show_trap(TRAPS[0])

        n = self.narrate(
            id="the_trap_01",
            text="The trap: the share from a difference, with a salary paid first. Capitals are three to two; A gets "
                 "twelve thousand rupees for managing first, then the rest is shared three to two; A receives twenty "
                 "thousand more than B: what is the total profit?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "trap")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "Capitals")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="the_trap_02",
            text="The wrong instinct says one part is twenty thousand, so the total is one lakh. The correct working: with "
                 "remainder R, twelve thousand plus one fifth of R is twenty thousand, so R is forty thousand, and the "
                 "profit is fifty-two thousand rupees.",
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
            text="The rule: remove the working partner's payment from the difference before using the ratio.",
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
            text="Drill one, eight seconds: A invests twenty-five thousand rupees for twelve months and B thirty thousand "
                 "for ten months. What is the profit ratio?",
            voice="default",
            subtitle=True,
            pause_after=8.0,
        )
        self.at_word(n, "Drill")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "invests")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="timed_drills_02",
            text="Twenty-five times twelve and thirty times ten are both three hundred: one to one.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "both")
        self.play(FadeIn(ans, scale=1.03))
        self.wait_for_narration(n)
        self.clear_stage()

        head, q, ans = self.drill(2, DRILLS[1])

        n = self.narrate(
            id="timed_drills_03",
            text="Drill two, six seconds: capitals in the ratio a third, a quarter and a sixth, for the same period. What "
                 "is the whole-number ratio?",
            voice="default",
            subtitle=True,
            pause_after=6.0,
        )
        self.at_word(n, "Drill")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "capitals")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="timed_drills_04",
            text="Times twelve: four to three to two.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Times")
        self.play(FadeIn(ans, scale=1.03))
        self.wait_for_narration(n)
        self.clear_stage()

        head, q, ans = self.drill(3, DRILLS[2])

        n = self.narrate(
            id="timed_drills_05",
            text="Drill three, six seconds: profits are in the ratio seven to five, and A gets six thousand rupees more "
                 "than B. What is the total profit?",
            voice="default",
            subtitle=True,
            pause_after=6.0,
        )
        self.at_word(n, "Drill")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "profits")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="timed_drills_06",
            text="One part is six thousand divided by two, three thousand, so the total is twelve times three thousand: "
                 "thirty-six thousand rupees.",
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
            text="Drill four, eight seconds: capitals are three to five and profits nine to ten. What is the ratio of "
                 "times?",
            voice="default",
            subtitle=True,
            pause_after=8.0,
        )
        self.at_word(n, "Drill")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "capitals")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="timed_drills_08",
            text="Nine thirds to ten fifths: three to two.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "thirds")
        self.play(FadeIn(ans, scale=1.03))
        self.wait_for_narration(n)
        self.clear_stage()

        head, q, ans = self.drill(5, DRILLS[4])

        n = self.narrate(
            id="timed_drills_09",
            text="Drill five, ten seconds: A invests thirty thousand rupees for the whole year; B joins with forty "
                 "thousand, and the profits are shared three to two. After how many months did B join?",
            voice="default",
            subtitle=True,
            pause_after=10.0,
        )
        self.at_word(n, "Drill")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "invests")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="timed_drills_10",
            text="B needs two thirds of three lakh sixty thousand, two lakh forty thousand capital-months; divided by "
                 "forty thousand, that is six months in, so B joined after six months.",
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
        first = VGroup(pill("cancel before you multiply", WORD, size=LABEL), pill("clear fractions with the LCM", WORD, size=LABEL)).arrange(RIGHT, buff=0.5)
        second = VGroup(pill("total from a difference:  d/(a − b)", RATIO, size=LABEL), pill("times:  profit ÷ capital", RATIO, size=LABEL))\
            .arrange(RIGHT, buff=0.5)
        only = text("only when the profit is shared purely in the ratio:  pay any working partner first", LABEL, INK, BOLD)
        fit_width(only, SAFE_W - 0.6)
        nxt = self.breadcrumb("Next", "Lesson 20 Practice Kit", "Lesson 21 · Probability")
        self.stack(head, [first, second, only, nxt], buff=0.75, top=0.9)
        self.no_overlap(*first)
        self.no_overlap(*second)

        n = self.narrate(
            id="quick_revision_01",
            text="Cancel before you multiply, clear fractions with the L C M, get the total from a difference with d over "
                 "a minus b, and find times by dividing profit by capital.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "Cancel")
        self.play(FadeIn(first[0], shift=UP * 0.1))
        self.at_word(n, "clear")
        self.play(FadeIn(first[1], shift=UP * 0.1))
        self.at_word(n, "difference")
        self.play(FadeIn(second[0], shift=UP * 0.1))
        self.at_word(n, "dividing")
        self.play(FadeIn(second[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="quick_revision_02",
            text="Use them only when the profit is shared purely in the ratio; pay any working partner first.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "only")
        self.play(FadeIn(only, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="quick_revision_03",
            text="Next: the lesson twenty practice kit, and then lesson twenty-one, probability.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Next")
        self.play(FadeIn(nxt, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S11_quick_revision")

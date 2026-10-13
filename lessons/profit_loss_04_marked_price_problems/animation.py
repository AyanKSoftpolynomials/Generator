"""
animation.py for the LMS video generator.

Course : Pre-C-CAT - Section A - Quantitative Aptitude
Video  : Lesson 14 - LCM & HCF - 01 - What are LCM & HCF

Source script:
  C:\\Scripts\\Section A\\Module_2_Section_A_Quantitative_Aptitude_Part_1\\Aptitude_Scripts\\Sessions 5-7 - LCM & HCF, Number System\\Lesson 14 - LCM & HCF\\01 - What are LCM & HCF.pdf

Built on the golden-reference pattern:
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``;
  * layouts stacked with next_to and guarded with ``no_overlap``; nothing is
    ever animated onto or into another box.

Lesson 14, Video 1 of 7. First video of a new lesson: a silent breadcrumb, "Now we start lesson fourteen", a one-line recap of Lesson 13, then today's topic. No spoken course welcome.
The narration follows the script section by section, with numbers written as words and "L C M", "H C F", "G C D" spelled for the voice. The rows of multiples and factors are drawn as chips, with the shared number in the focus colour. Every figure on screen is computed and asserted.
Pauses: 3 seconds on the hook question, 10 seconds on the checkpoint, 12 seconds on each practice screen.
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

from functools import reduce
from math import gcd


def hcf(*numbers):
    return reduce(gcd, numbers)


def lcm(*numbers):
    return reduce(lambda a, b: a * b // gcd(a, b), numbers)


def multiples(n, upto):
    return list(range(n, upto + 1, n))


def factors(n):
    return [d for d in range(1, n + 1) if n % d == 0]


def check_limits(*numbers):
    """HCF ≤ smallest ≤ largest ≤ LCM, and the HCF divides the LCM."""
    return hcf(*numbers) <= min(numbers) <= max(numbers) <= lcm(*numbers) and lcm(*numbers) % hcf(*numbers) == 0


# ---- the hook: two sensors ----
S1, S2 = 12, 18
MEET, PIECE = lcm(S1, S2), hcf(S1, S2)
COMMON = [f for f in factors(S1) if f in factors(S2)]
assert (MEET, PIECE, S1 + S2, S1 * S2) == (36, 6, 30, 216) and 30 % S1 != 0 and 216 % S1 == 0 == 216 % S2
assert multiples(S1, 48) == [12, 24, 36, 48] and multiples(S2, 54) == [18, 36, 54]
assert factors(S1) == [1, 2, 3, 4, 6, 12] and factors(S2) == [1, 2, 3, 6, 9, 18] and COMMON == [1, 2, 3, 6]
assert check_limits(S1, S2) and (MEET // S1, MEET // S2) == (3, 2)

# ---- second worked example: the cable reels ----
PIECES = S1 // PIECE + S2 // PIECE
assert PIECES == 5

# ---- exam patterns (answers computed) ----
assert (lcm(15, 20), lcm(6, 15), hcf(18, 30), lcm(6, 8, 12), lcm(18, 30)) == (60, 30, 6, 24, 90)
PATTERNS_A = [("Meet again", "Buses every 15 and 20 minutes from 6:00", "LCM", "7:00"),
              ("Smallest divisible", "Smallest number divisible by 6 and 15", "LCM", str(lcm(6, 15))),
              ("Largest divisor", "Largest number dividing 18 and 30", "HCF", str(hcf(18, 30)))]
PATTERNS_B = [("Equal pieces", "Cut 12 m and 18 m into equal maximum pieces", "HCF", f"{PIECE} m, {PIECES} pieces"),
              ("Three events", "Bells every 6, 8, 12 minutes", "LCM", f"{lcm(6, 8, 12)} minutes")]

# ---- traps: (title, question, wrong, right, rule) ----
TRAPS = [("Trap 1  ·  adding or multiplying", "Every 12 and every 18 seconds.  Next together?",
          "30 (sum)  or  216 (product)", str(MEET),
          "The LCM is the first common multiple; the product is usually not the first."),
         ("Trap 2  ·  “greatest” read as LCM", "The greatest number that divides both 18 and 30?",
          f"“greatest”:  LCM = {lcm(18, 30)}", f"HCF = {hcf(18, 30)}",
          "A number that divides others is a factor: HCF, however big the word sounds.")]

# ---- practice (answers computed) ----
PRACTICE_A = [("L1", "Find the LCM and HCF of 8 and 12."),
              ("L1", "Find the smallest number divisible by both 6 and 15."),
              ("L1", "Find the largest number that divides both 18 and 30."),
              ("L2", "Three bells ring every 6, 8 and 12 minutes.  If they ring together now, after how many minutes will they next ring together?"),
              ("L2", "Find the HCF and LCM of 20 and 30."),
              ("L2", "Two runners complete a lap in 12 and 18 minutes.  If they start together, after how many minutes will they next be together at the start?")]
PRACTICE_B = [("L3", "The HCF of two numbers is 9.  Which of these cannot be their LCM:  54, 72, 84, 90?"),
              ("L3", "Two cables of 45 m and 75 m are cut into equal pieces of the greatest possible length.  How many pieces are there in all?")]
assert (lcm(8, 12), hcf(8, 12), hcf(20, 30), lcm(20, 30)) == (24, 4, 10, 60) and 20 == 2 ** 2 * 5 and 30 == 2 * 3 * 5
assert [c for c in (54, 72, 84, 90) if c % 9] == [84]
A8 = 45 // hcf(45, 75) + 75 // hcf(45, 75)
assert (hcf(45, 75), A8) == (15, 8)
ANSWERS_A = [("multiples of 12:  12, 24;   common factors of 8 and 12:  1, 2, 4", f"LCM {lcm(8, 12)};  HCF {hcf(8, 12)}"),
             ("LCM(6, 15)", str(lcm(6, 15))),
             ("HCF(18, 30)", str(hcf(18, 30))),
             ("LCM(6, 8, 12)", f"{lcm(6, 8, 12)} minutes")]
ANSWERS_B = [("20  =  2² × 5,     30  =  2 × 3 × 5", f"HCF {hcf(20, 30)};  LCM {lcm(20, 30)}"),
             ("LCM(12, 18)", f"{MEET} minutes"),
             ("the HCF must divide the LCM:   9 divides 54, 72 and 90, but not 84", "84 cannot be the LCM"),
             ("HCF(45, 75)  =  15 m;    pieces:  3 + 5", f"{A8} pieces")]

OBJECTIVES = [("Explain LCM and HCF in plain words", "and find them for small numbers"),
              ("Decide which one a problem needs", "from its wording"),
              ("State the size limits", "each must satisfy, as a quick check")]
LENS = [("Recognition cue", "say “clock” or “saw” before writing a number"),
        ("Target time", "20 to 30 seconds"),
        ("Sanity check", "HCF ≤ smallest ≤ largest ≤ LCM,  and the HCF divides the LCM")]
FORMULAS = ["LCM  =  smallest number divisible by all          (repeat and meet)",
            "HCF  =  largest number dividing all exactly          (cut and share)",
            "HCF ≤ smallest number ≤ largest number ≤ LCM;          HCF divides LCM"]


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


class WhatAreLCMAndHCFVideo(LMSScene):
    lesson_title = "What are LCM & HCF?"

    def construct(self):
        self.camera.background_color = BG

        self.intro()
        self.hook()
        self.objectives()
        self.why_this_matters()
        self.multiples_and_lcm()
        self.factors_and_hcf()
        self.size_limits()
        self.formula_box()
        self.analogy()
        self.hook_solved()
        self.second_example()
        self.exam_patterns()
        self.traps()
        self.checkpoint()
        self.practice()
        self.answers()
        self.exam_lens()
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

    def two_cards(self, lines_a, lines_b, colors=(WORD, RATIO), width=6.2):
        """Two cards of the same height.  Returns (cards, contents)."""
        contents = [VGroup(*[text(s, size, c, w) for s, size, c, w in lines]).arrange(DOWN, buff=0.25)
                    for lines in (lines_a, lines_b)]
        tallest = max(c.height for c in contents) + 0.7
        cards = VGroup(*[self.card(c, width=width, height=tallest, color=col) for c, col in zip(contents, colors)])\
            .arrange(RIGHT, buff=0.6)
        return cards, contents

    def number_row(self, label, numbers, color, glow=()):
        """VGroup(label, chips): one chip per number, the ``glow`` numbers in the focus colour."""
        chips = VGroup(*[pill(str(v), FOCUS if v in glow else color, size=LABEL) for v in numbers]).arrange(RIGHT, buff=0.2)
        return VGroup(text(label, LABEL, color, BOLD), chips).arrange(RIGHT, buff=0.4)

    def number_rows(self, label_a, a, label_b, b, glow):
        rows = VGroup(self.number_row(label_a, a, WORD, glow), self.number_row(label_b, b, RATIO, glow))\
            .arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        shared = [chip for row, nums in zip(rows, (a, b)) for chip, v in zip(row[1], nums) if v in glow]
        return rows, shared

    def tool_table(self, head, patterns):
        table, rows = self.placed_table(head, ["Pattern", "Example", "Tool", "Answer"], [list(p) for p in patterns],
                                        [2.6, 6.4, 1.4, 2.8], room=1.2)
        for row in rows:
            row[0].set_color(WORD)
            row[2].set_color(RATIO)
            row[3].set_color(GOOD)
        return table, rows

    # ================================================== 0. INTRO ==========
    # First video of a new lesson: silent breadcrumb, "now we start Lesson 14", a one-line recap
    # of Lesson 13, and today's topic.  No spoken course welcome.

    def intro(self):
        self.scene_start("S00_intro", title="Intro")

        crumb = self.breadcrumb("Quantitative Aptitude", "Lesson 14 · LCM & HCF", "Video 1 of 7")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        lesson = pill("Lesson 14  ·  LCM & HCF", RATIO, size=LABEL)
        recap = VGroup(text("from Lesson 13  ·  Time & Work", SMALL, MUTED),
                       VGroup(pill("rates add; times don't", WORD, size=LABEL), pill("total work = the LCM of the times", GOOD, size=LABEL))
                       .arrange(RIGHT, buff=0.4)).arrange(DOWN, buff=0.25)
        title = text("What are LCM & HCF?", TITLE, INK, BOLD)
        today = text("today: what they mean, and which one a problem needs", LABEL, FOCUS)
        block = VGroup(lesson, recap, title, today).arrange(DOWN, buff=0.55)
        fit_within(block, SAFE_W, SAFE_H - crumb.height - 0.9)
        block.next_to(crumb, DOWN, buff=0.6)
        self.no_overlap(crumb, lesson, recap, title, today)
        self.no_overlap(*recap[1])
        self.validator.check_in_frame(VGroup(crumb, block))

        n = self.narrate(
            id="intro_01",
            text="Now we start lesson fourteen: L C M and H C F.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.at_word(n, "fourteen")
        self.play(FadeIn(lesson, scale=1.05))
        self.wait_for_narration(n)

        n = self.narrate(
            id="intro_02",
            text="In lesson thirteen, you learned that rates add, and you used the L C M as the total work.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "rates")
        self.play(FadeIn(recap[0]), FadeIn(recap[1][0], shift=UP * 0.1))
        self.at_word(n, "total")
        self.play(FadeIn(recap[1][1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="intro_03",
            text="This first video asks what L C M and H C F actually mean, and which one a problem needs.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "asks")
        self.play(FadeIn(title, shift=UP * 0.1))
        self.at_word(n, "mean")
        self.play(FadeIn(today, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_intro")

    # =================================================== 1. HOOK ==========

    def hook(self):
        self.scene_start("S01_hook", title="Hook")

        head = self.heading("Two sensors on a test rig")
        pulses = VGroup(pill("fire together at t = 0", GOOD, size=LABEL), pill(f"one every {S1} ms", WORD, size=LABEL),
                        pill(f"one every {S2} ms", RATIO, size=LABEL)).arrange(RIGHT, buff=0.45)
        ask = pill("when do they next fire together?", FOCUS, size=BODY)
        guesses = VGroup(pill(f"add:  {S1 + S2} ms   (wrong)", BAD, size=LABEL), pill(f"multiply:  {S1 * S2} ms   (not the first time)", BAD, size=LABEL))\
            .arrange(RIGHT, buff=0.5)
        promise = text("by the end: the first time, and a cable-cutting question, with the same two ideas", SMALL, GOOD, BOLD)
        self.stack(head, [pulses, ask, guesses, promise], buff=0.65, top=0.7)
        self.no_overlap(*pulses)
        self.no_overlap(*guesses)

        n = self.narrate(
            id="hook_01",
            text="Two sensors on a test rig fire a pulse together at time zero.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "sensors")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "together")
        self.play(FadeIn(pulses[0], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_02",
            text="One fires every twelve milliseconds, the other every eighteen.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "twelve")
        self.play(FadeIn(pulses[1], shift=UP * 0.1))
        self.at_word(n, "eighteen")
        self.play(FadeIn(pulses[2], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_03",
            text="When do they next fire together?",
            voice="default",
            subtitle=True,
            pause_after=3.0,
        )
        self.at_word(n, "next")
        self.play(FadeIn(ask, scale=1.05))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="hook_04",
            text="Most people add: thirty milliseconds. It feels natural, and it's wrong.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "add")
        self.play(FadeIn(guesses[0], shift=UP * 0.1))
        self.at_word(n, "wrong")
        self.play(Indicate(guesses[0], color=BAD, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_05",
            text="Others multiply: two hundred and sixteen milliseconds. They do coincide then, but it isn't the first time.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "multiply")
        self.play(FadeIn(guesses[1], shift=UP * 0.1))
        self.at_word(n, "first")
        self.play(Indicate(guesses[1], color=BAD, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_06",
            text="By the end of this video you'll find the first time, and you'll solve a completely different-looking "
                 "question, about cutting cable, with the same two ideas.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "cable")
        self.play(FadeIn(promise, shift=UP * 0.1))
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
            text="First, explain L C M and H C F in plain words, and find them for small numbers.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "explain")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "small")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="obj_03",
            text="Second, decide which one a problem needs, from its wording.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "decide")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "wording")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="obj_04",
            text="Third, state the size limits each must satisfy, as a quick check.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "state")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "check")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_objectives")

    # ========================================== 3. WHY THIS MATTERS ==========

    def why_this_matters(self):
        self.scene_start("S03_why_this_matters", title="Why This Matters")

        head = self.heading("Why this matters")
        rarely = text("the arithmetic is rarely the hard part", LABEL, INK)
        marks = VGroup(pill("read the story", WORD, size=LABEL), pill("know which tool it needs", RATIO, size=LABEL)).arrange(RIGHT, buff=0.5)
        quick = pill("then: some of the quickest marks in the paper", GOOD, size=LABEL)
        self.stack(head, [rarely, marks, quick], buff=0.8, top=0.9)
        self.no_overlap(*marks)

        n = self.narrate(
            id="why_01",
            text="In L C M and H C F questions, the arithmetic is rarely the hard part.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "arithmetic")
        self.play(FadeIn(rarely, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="why_02",
            text="The marks are in reading the story, and knowing which tool it needs.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "story")
        self.play(FadeIn(marks[0], shift=UP * 0.1))
        self.at_word(n, "tool")
        self.play(FadeIn(marks[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="why_03",
            text="Get that right, and these become some of the quickest marks in the paper.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "quickest")
        self.play(FadeIn(quick, scale=1.05))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_why_this_matters")

    # ================================ 4. CONCEPT: MULTIPLES AND THE LCM ==========

    def multiples_and_lcm(self):
        self.scene_start("S04_multiples_and_lcm", title="Concept - Multiples and the LCM")

        head = self.heading("Multiples: where repeating events land")
        rows, shared = self.number_rows(f"every {S1} ms:", multiples(S1, 48), f"every {S2} ms:", multiples(S2, 54), {MEET})
        first = pill(f"LCM  =  {MEET}:  the first landing they share", FOCUS, size=LABEL)
        meaning = text("Least Common Multiple: the smallest number both divide into", LABEL, INK, BOLD)
        self.stack(head, [rows, first, meaning], buff=0.75, top=0.8)
        self.no_overlap(*rows[0][1])
        self.no_overlap(*rows[1][1])

        n = self.narrate(
            id="multiples_01",
            text="Multiples are where repeating events land. The twelve millisecond sensor fires at twelve, twenty-four, "
                 "thirty-six, forty-eight, and so on; the eighteen millisecond sensor at eighteen, thirty-six, fifty-four, "
                 "and so on.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Multiples")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "twelve", occurrence=1)
        self.play(FadeIn(rows[0][0]), LaggedStart(*[FadeIn(c, shift=UP * 0.1) for c in rows[0][1]], lag_ratio=0.5), run_time=3.0)
        self.at_word(n, "eighteen", occurrence=1)
        self.play(FadeIn(rows[1][0]), LaggedStart(*[FadeIn(c, shift=UP * 0.1) for c in rows[1][1]], lag_ratio=0.5), run_time=2.5)
        self.wait_for_narration(n)

        n = self.narrate(
            id="multiples_02",
            text="The L C M is the first landing they share: thirty-six.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "first")
        self.play(*[Indicate(c, color=FOCUS, scale_factor=1.2) for c in shared])
        self.at_word(n, "thirty-six")
        self.play(FadeIn(first, scale=1.05))
        self.wait_for_narration(n)

        n = self.narrate(
            id="multiples_03",
            text="Least common multiple: the smallest number both divide into.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "smallest")
        self.play(FadeIn(meaning, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_multiples_and_lcm")

    # ================================ 5. CONCEPT: FACTORS AND THE HCF ==========

    def factors_and_hcf(self):
        self.scene_start("S05_factors_and_hcf", title="Concept - Factors and the HCF")

        head = self.heading("Factors: the equal pieces a number can be cut into")
        rows, shared = self.number_rows(f"factors of {S1}:", factors(S1), f"factors of {S2}:", factors(S2), {PIECE})
        common = text("common factors:   " + ",  ".join(str(c) for c in COMMON), LABEL, INK)
        highest = pill(f"HCF  =  {PIECE}:  the largest piece both can be cut into", FOCUS, size=LABEL)
        meaning = text("Highest Common Factor   (also called GCD)", LABEL, INK, BOLD)
        self.stack(head, [rows, common, highest, meaning], buff=0.6, top=0.7)
        self.no_overlap(*rows[0][1])
        self.no_overlap(*rows[1][1])

        n = self.narrate(
            id="factors_01",
            text="Factors are the equal pieces a number can be cut into. The factors of twelve are one, two, three, four, six "
                 "and twelve. The factors of eighteen are one, two, three, six, nine and eighteen.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Factors", occurrence=1)
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "twelve", occurrence=1)
        self.play(FadeIn(rows[0][0]), LaggedStart(*[FadeIn(c, shift=UP * 0.1) for c in rows[0][1]], lag_ratio=0.5), run_time=3.0)
        self.at_word(n, "eighteen", occurrence=1)
        self.play(FadeIn(rows[1][0]), LaggedStart(*[FadeIn(c, shift=UP * 0.1) for c in rows[1][1]], lag_ratio=0.5), run_time=3.0)
        self.wait_for_narration(n)

        n = self.narrate(
            id="factors_02",
            text="The H C F is the largest piece both can be cut into. The common factors are one, two, three and six; the "
                 "highest is six.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "largest")
        self.play(*[Indicate(c, color=FOCUS, scale_factor=1.2) for c in shared])
        self.at_word(n, "common")
        self.play(FadeIn(common, shift=UP * 0.1))
        self.at_word(n, "highest")
        self.play(FadeIn(highest, scale=1.05))
        self.wait_for_narration(n)

        n = self.narrate(
            id="factors_03",
            text="Highest common factor, also called G C D.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "also")
        self.play(FadeIn(meaning, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_factors_and_hcf")

    # ================================ 6. CONCEPT: SIZE LIMITS ==========

    def size_limits(self):
        self.scene_start("S06_size_limits", title="Concept - Size Limits; the HCF Divides the LCM")

        head = self.heading("Size limits")
        limits = VGroup(pill("the LCM is never smaller than the largest number", WORD, size=LABEL),
                        pill("the HCF is never larger than the smallest number", RATIO, size=LABEL)).arrange(DOWN, buff=0.25)
        chain = text(f"HCF ≤ smallest ≤ largest ≤ LCM:      {PIECE} ≤ {S1} ≤ {S2} ≤ {MEET}", LABEL, INK, BOLD)
        outside = text("any answer outside these limits is wrong", LABEL, BAD, BOLD)
        divides = VGroup(pill(f"the HCF always divides the LCM:   {MEET} ÷ {PIECE} = {MEET // PIECE}", GOOD, size=LABEL),
                         text("if yours doesn't, recheck", LABEL, MUTED)).arrange(RIGHT, buff=0.5)
        self.stack(head, [limits, chain, outside, divides], buff=0.6, top=0.7)
        self.no_overlap(*divides)

        n = self.narrate(
            id="limits_01",
            text="Size limits. The L C M is never smaller than the largest number; the H C F is never larger than the smallest.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Size")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "smaller")
        self.play(FadeIn(limits[0], shift=UP * 0.1))
        self.at_word(n, "larger")
        self.play(FadeIn(limits[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="limits_02",
            text="Any answer outside these limits is wrong.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "outside")
        self.play(FadeIn(chain, shift=UP * 0.1))
        self.at_word(n, "wrong")
        self.play(FadeIn(outside, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="limits_03",
            text="The H C F always divides the L C M: six divides thirty-six. If yours doesn't, recheck.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "divides", occurrence=1)
        self.play(FadeIn(divides[0], scale=1.03))
        self.at_word(n, "recheck")
        self.play(FadeIn(divides[1], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_size_limits")

    # ============================================== 7. FORMULA BOX ==========

    def formula_box(self):
        self.scene_start("S07_formula_box", title="Formula Box")

        head = self.heading("Formula box", GOOD)
        lines = VGroup(*[text(f, LABEL, INK) for f in FORMULAS]).arrange(DOWN, buff=0.6, aligned_edge=LEFT)
        box = self.card(lines, width=SAFE_W - 0.4, color=GOOD, pad=0.5)
        self.stack(head, [box], top=0.9)

        n = self.narrate(
            id="formula_01",
            text="Here is the formula box. The L C M is the smallest number divisible by all: repeat and meet.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "box")
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(box[0]))
        self.at_word(n, "smallest")
        self.play(FadeIn(lines[0], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_02",
            text="The H C F is the largest number dividing all exactly: cut and share.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "largest")
        self.play(FadeIn(lines[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_03",
            text="The H C F is at most the smallest number, the L C M is at least the largest, and the H C F divides the L C M.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "most")
        self.play(FadeIn(lines[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S07_formula_box")

    # ============================================== 8. THE ANALOGY ==========

    def analogy(self):
        self.scene_start("S08_analogy", title="The Analogy - A Clock and a Saw")

        head = self.heading("A clock and a saw")
        cards, _ = self.two_cards(
            [("The clock repeats", LABEL, WORD, BOLD), ("two repeating things line up again", SMALL, INK, NORMAL), ("LCM", BODY, WORD, BOLD)],
            [("The saw cuts", LABEL, RATIO, BOLD), ("the biggest equal piece that fits both", SMALL, INK, NORMAL), ("HCF", BODY, RATIO, BOLD)])
        reach = VGroup(text("repeating and meeting:  reach for the clock", LABEL, WORD, BOLD),
                       text("cutting or sharing equally:  reach for the saw", LABEL, RATIO, BOLD)).arrange(DOWN, buff=0.2)
        stops = VGroup(text("Where the analogy stops", LABEL, BAD, BOLD),
                       text("some questions mix both ideas:  “the least number leaving a remainder”  (Video 6)", LABEL, MUTED),
                       text("then you use one tool and adjust", LABEL, INK)).arrange(DOWN, buff=0.2)
        self.stack(head, [cards, reach, stops], buff=0.55, top=0.5)
        self.no_overlap(cards[0], cards[1])

        n = self.narrate(
            id="analogy_01",
            text="A clock repeats, and when two repeating things line up again, that's an L C M.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "clock")
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(cards[0], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_02",
            text="A saw cuts, and the biggest equal piece that fits two lengths exactly is an H C F.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "saw")
        self.play(FadeIn(cards[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_03",
            text="When a story is about repeating and meeting, reach for the clock. When it's about cutting or sharing equally, "
                 "reach for the saw.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "meeting")
        self.play(FadeIn(reach[0], shift=UP * 0.1))
        self.at_word(n, "sharing")
        self.play(FadeIn(reach[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_04",
            text="Where the analogy stops: some questions mix both ideas, such as the least number leaving a remainder, in "
                 "video six.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "stops")
        self.play(FadeIn(stops[0], shift=UP * 0.1))
        self.at_word(n, "mix")
        self.play(FadeIn(stops[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_05",
            text="Then you use one tool and adjust.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "adjust")
        self.play(FadeIn(stops[2], shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S08_analogy")

    # ================================ 9. WORKED EXAMPLE: CLOSING THE HOOK ==========

    def hook_solved(self):
        self.scene_start("S09_hook_solved", title="Worked Example - Closing the Hook")

        head = self.heading(f"Sensors:  every {S1} ms and every {S2} ms")
        rows, shared = self.number_rows(f"multiples of {S1}:", multiples(S1, MEET), f"multiples of {S2}:", multiples(S2, MEET), {MEET})
        match = pill(f"first match:  {MEET} ms", GOOD, size=BODY)
        check = text(f"check:   {MEET} ÷ {S1} = {MEET // S1}   and   {MEET} ÷ {S2} = {MEET // S2},   both whole", LABEL, INK)
        never = text("30 was never possible:  30 isn't a multiple of 12", LABEL, BAD, BOLD)
        self.stack(head, [rows, match, check, never], buff=0.6, top=0.7)

        n = self.narrate(
            id="solved_01",
            text="Multiples of twelve: twelve, twenty-four, thirty-six. Multiples of eighteen: eighteen, thirty-six.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "twelve", occurrence=1)
        self.play(FadeIn(rows[0][0]), LaggedStart(*[FadeIn(c, shift=UP * 0.1) for c in rows[0][1]], lag_ratio=0.5), run_time=2.0)
        self.at_word(n, "eighteen", occurrence=1)
        self.play(FadeIn(rows[1][0]), LaggedStart(*[FadeIn(c, shift=UP * 0.1) for c in rows[1][1]], lag_ratio=0.5), run_time=1.5)
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_02",
            text="The first match is thirty-six milliseconds.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "match")
        self.play(*[Indicate(c, color=FOCUS, scale_factor=1.2) for c in shared], FadeIn(match, scale=1.05))
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_03",
            text="Check: thirty-six divided by twelve is three, and thirty-six divided by eighteen is two, both whole.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Check")
        self.play(FadeIn(check, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_04",
            text="And thirty was never possible: thirty isn't a multiple of twelve.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "never")
        self.play(FadeIn(never, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S09_hook_solved")

    # ====================== 10. SECOND WORKED EXAMPLE: THE SAW ==========

    def second_example(self):
        self.scene_start("S10_second_example", title="A Second Worked Example - Same Numbers, the Saw")

        head = self.heading("Same numbers, the saw")
        given = VGroup(pill("cable reels:  12 m and 18 m", WORD, size=LABEL), pill("equal pieces, as long as possible", RATIO, size=LABEL),
                       pill("nothing left over", GOOD, size=LABEL), pill("how long?  how many?", FOCUS, size=LABEL)).arrange(RIGHT, buff=0.3)
        steps = self.solve_steps([
            ("“equal pieces, as long as possible, nothing left”", "the saw:  HCF"),
            (f"HCF({S1}, {S2})", f"=  {PIECE} m"),
            (f"Pieces:   {S1} ÷ {PIECE} + {S2} ÷ {PIECE}  =  2 + 3", f"=  {PIECES} pieces")])
        self.stack(head, [given, steps], buff=0.8, top=0.8)
        self.no_overlap(*given)
        self.no_overlap(*steps)

        n = self.narrate(
            id="saw_01",
            text="Two cable reels hold twelve metres and eighteen metres. You must cut both into equal pieces, as long as "
                 "possible, with nothing left over. How long is each piece, and how many pieces?",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "reels")
        self.play(FadeIn(given[0], shift=UP * 0.1))
        self.at_word(n, "equal")
        self.play(FadeIn(given[1], shift=UP * 0.1))
        self.at_word(n, "nothing")
        self.play(FadeIn(given[2], shift=UP * 0.1))
        self.at_word(n, "many")
        self.play(FadeIn(given[3], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="saw_02",
            text="Equal pieces, as long as possible, nothing left: that is the saw, so the H C F.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Equal")
        self.play(FadeIn(steps[0][:2], shift=RIGHT * 0.1))
        self.at_word(n, "saw")
        self.play(FadeIn(steps[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="saw_03",
            text="The H C F of twelve and eighteen is six metres.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "twelve")
        self.play(FadeIn(steps[1][:2], shift=RIGHT * 0.1))
        self.at_word(n, "six")
        self.play(FadeIn(steps[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="saw_04",
            text="The pieces: twelve divided by six, plus eighteen divided by six, is two plus three: five pieces.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "pieces", occurrence=1)
        self.play(FadeIn(steps[2][:2], shift=RIGHT * 0.1))
        self.at_word(n, "five")
        self.play(FadeIn(steps[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S10_second_example")

    # ============================================ 11. EXAM PATTERNS ==========

    def exam_patterns(self):
        self.scene_start("S11_exam_patterns", title="Exam Patterns - How This Is Asked")

        head = self.heading("Exam patterns  ·  1 to 3 of 5")
        table, rows = self.tool_table(head, PATTERNS_A)

        n = self.narrate(
            id="patterns_01",
            text="Exams ask this in five ways.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "five")
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.wait_for_narration(n)

        n = self.narrate(
            id="patterns_02",
            text="Meet again: buses every fifteen and twenty minutes from six o'clock. The tool is the L C M: sixty minutes, so "
                 "seven o'clock.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Meet")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "tool")
        self.play(FadeIn(rows[0][2:], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="patterns_03",
            text="Smallest divisible: the smallest number divisible by six and fifteen. The L C M: thirty.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Smallest", occurrence=1)
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "thirty")
        self.play(FadeIn(rows[1][2:], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="patterns_04",
            text="Largest divisor: the largest number dividing eighteen and thirty. The H C F: six.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Largest", occurrence=1)
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "six")
        self.play(FadeIn(rows[2][2:], shift=RIGHT * 0.2))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Exam patterns  ·  4 and 5 of 5")
        table, rows = self.tool_table(head, PATTERNS_B)

        n = self.narrate(
            id="patterns_05",
            text="Equal pieces: cut twelve metres and eighteen metres into equal maximum pieces. The H C F: six metres, five "
                 "pieces.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "Equal", occurrence=1)
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "five")
        self.play(FadeIn(rows[0][2:], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="patterns_06",
            text="Three events: bells every six, eight and twelve minutes. The L C M: twenty-four minutes.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Three")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "twenty-four")
        self.play(FadeIn(rows[1][2:], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S11_exam_patterns")

    # ================================ 12. TRAPS AND CONFUSING QUESTIONS ==========

    def traps(self):
        self.scene_start("S12_traps", title="Traps and Confusing Questions")

        head, q, wrong, right, rule = self.show_trap(TRAPS[0])

        n = self.narrate(
            id="trap1_01",
            text="Trap one: adding or multiplying. Every twelve and every eighteen seconds; when are they next together?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "adding")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "twelve")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="trap1_02",
            text="The wrong instinct is thirty, the sum, or two hundred and sixteen, the product. The correct answer is "
                 "thirty-six.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "wrong")
        self.play(FadeIn(wrong, shift=UP * 0.1))
        self.at_word(n, "correct")
        self.play(FadeIn(right, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="trap1_03",
            text="The rule: the L C M is the first common multiple; the product is a common multiple, but usually not the "
                 "first.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "rule")
        self.play(FadeIn(rule, shift=UP * 0.1))
        self.wait_for_narration(n)
        self.clear_stage()

        head, q, wrong, right, rule = self.show_trap(TRAPS[1])

        n = self.narrate(
            id="trap2_01",
            text="Trap two: greatest, read as L C M. What is the greatest number that divides both eighteen and thirty?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "read")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "divides")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="trap2_02",
            text="The wrong instinct hears greatest and gives the L C M, ninety. The correct answer is six.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "wrong")
        self.play(FadeIn(wrong, shift=UP * 0.1))
        self.at_word(n, "correct")
        self.play(FadeIn(right, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="trap2_03",
            text="The rule: a number that divides others is a factor, so H C F, however big the word sounds.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "rule")
        self.play(FadeIn(rule, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S12_traps")

    # =============================================== 13. CHECKPOINT ==========

    def checkpoint(self):
        self.scene_start("S13_checkpoint", title="Checkpoint")

        head = self.heading("Checkpoint  ·  your turn")
        given = VGroup(pill("two buses leave together at 6:00", GOOD, size=LABEL), pill("every 15 minutes", WORD, size=LABEL),
                       pill("every 20 minutes", RATIO, size=LABEL)).arrange(RIGHT, buff=0.4)
        ask = VGroup(text("when do they next leave together?", LABEL, INK, BOLD), pill("clock or saw?", FOCUS, size=LABEL)).arrange(RIGHT, buff=0.6)
        work = VGroup(text(f"the clock:   LCM(15, 20)  =  {lcm(15, 20)} minutes", LABEL, INK), text("7:00", BODY, GOOD, BOLD)).arrange(RIGHT, buff=0.9)
        self.stack(head, [given, ask, work], buff=0.7, top=0.8)
        self.no_overlap(*given)
        self.no_overlap(*ask)
        self.no_overlap(*work)

        n = self.narrate(
            id="check_01",
            text="Your turn. Two buses leave a depot together at six o'clock, one every fifteen minutes and one every twenty. "
                 "When do they next leave together? Clock or saw?",
            voice="default",
            subtitle=True,
            pause_after=10.0,
        )
        self.at_word(n, "turn")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "buses")
        self.play(FadeIn(given, shift=UP * 0.1))
        self.at_word(n, "next")
        self.play(FadeIn(ask[0], shift=UP * 0.1))
        self.at_word(n, "Clock")
        self.play(FadeIn(ask[1], shift=LEFT * 0.1))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="check_02",
            text="The clock: the L C M of fifteen and twenty is sixty minutes, so seven o'clock.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "clock")
        self.play(FadeIn(work[0], shift=UP * 0.1))
        self.at_word(n, "seven")
        self.play(FadeIn(work[1], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S13_checkpoint")

    # ======================================== 14. PRACTICE QUESTIONS ==========

    def practice(self):
        self.scene_start("S14_practice", title="Practice Questions")

        head = self.heading("Practice  ·  Levels 1 and 2")
        table, rows = self.practice_table(head, PRACTICE_A, 1)

        n = self.narrate(
            id="practice_01",
            text="Level one, question one: find the L C M and H C F of eight and twelve. Question two: find the smallest number "
                 "divisible by both six and fifteen. Question three: find the largest number that divides both eighteen and "
                 "thirty.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "eight")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "smallest")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.at_word(n, "largest")
        self.play(FadeIn(rows[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="practice_02",
            text="Level two, question four: three bells ring every six, eight and twelve minutes; if they ring together now, "
                 "after how many minutes will they next ring together? Question five: find the H C F and L C M of twenty and "
                 "thirty. Question six: two runners complete a lap in twelve and eighteen minutes; if they start together, "
                 "after how many minutes will they next be together at the start?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "bells")
        self.play(FadeIn(rows[3], shift=RIGHT * 0.2))
        self.at_word(n, "twenty")
        self.play(FadeIn(rows[4], shift=RIGHT * 0.2))
        self.at_word(n, "runners")
        self.play(FadeIn(rows[5], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="practice_03",
            text="Pause the video and solve these six.",
            voice="default",
            subtitle=True,
            pause_after=12.0,
        )
        self.at_word(n, "Pause")
        self.play(Indicate(head, color=FOCUS, scale_factor=1.05))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)
        self.clear_stage()

        head = self.heading("Practice  ·  Level 3")
        table, rows = self.practice_table(head, PRACTICE_B, 7)

        n = self.narrate(
            id="practice_04",
            text="Level three, question seven: the H C F of two numbers is nine; which of these cannot be their L C M: "
                 "fifty-four, seventy-two, eighty-four or ninety? Question eight: two cables of forty-five metres and "
                 "seventy-five metres are cut into equal pieces of the greatest possible length; how many pieces are there in "
                 "all?",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "nine")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "cables")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="practice_05",
            text="Pause again and solve these two.",
            voice="default",
            subtitle=True,
            pause_after=12.0,
        )
        self.at_word(n, "Pause")
        self.play(Indicate(head, color=FOCUS, scale_factor=1.05))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        self.clear_stage()
        self.scene_end("S14_practice")

    # ================================================= 15. ANSWERS ==========

    def answers(self):
        self.scene_start("S15_answers", title="Answer Key, with Reasoning")

        head = self.heading("Answer key  ·  1 to 4", GOOD)
        table, rows = self.answer_table(head, ANSWERS_A, 1)

        n = self.narrate(
            id="answers_01",
            text="One: the L C M is twenty-four, and the H C F is four.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "twenty-four")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "four")
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_02",
            text="Two: the L C M of six and fifteen is thirty.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "six")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "thirty")
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_03",
            text="Three: the H C F of eighteen and thirty is six.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "eighteen")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "six")
        self.play(FadeIn(rows[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_04",
            text="Four: the L C M of six, eight and twelve is twenty-four minutes.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "six")
        self.play(FadeIn(rows[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "twenty-four")
        self.play(FadeIn(rows[3][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Answer key  ·  5 to 8", GOOD)
        table, rows = self.answer_table(head, ANSWERS_B, 5)

        n = self.narrate(
            id="answers_05",
            text="Five: twenty is two squared times five, and thirty is two times three times five. The H C F is ten and the "
                 "L C M is sixty.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "squared")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "ten")
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_06",
            text="Six: the L C M of twelve and eighteen is thirty-six minutes.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "twelve")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "thirty-six")
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_07",
            text="Seven: the H C F must divide the L C M. Nine divides fifty-four, seventy-two and ninety, but not eighty-four. "
                 "So eighty-four cannot be the L C M.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "divide")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "not")
        self.play(Indicate(rows[2][1], color=FOCUS, scale_factor=1.02))
        self.at_word(n, "cannot")
        self.play(FadeIn(rows[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_08",
            text="Eight: the H C F of forty-five and seventy-five is fifteen metres. The pieces are three plus five: eight.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "fifteen")
        self.play(FadeIn(rows[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "plus")
        self.play(FadeIn(rows[3][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S15_answers")

    # =============================================== 16. EXAM LENS ==========

    def exam_lens(self):
        self.scene_start("S16_exam_lens", title="Exam Lens - Recognise and Move")

        head = self.heading("Exam lens: recognise and move", RATIO)
        blocks = two_line_blocks(LENS, RATIO)
        self.stack(head, list(blocks), buff=0.6, top=0.8, align=LEFT)

        n = self.narrate(
            id="lens_01",
            text="Recognise and move. The recognition cue: say clock or saw before writing a number.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Recognise")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "cue")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "clock")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="lens_02",
            text="The target time: twenty to thirty seconds.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "target")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "twenty")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="lens_03",
            text="The sanity check: the H C F is at most the smallest, the L C M is at least the largest, and the H C F divides "
                 "the L C M.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "sanity")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "most")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S16_exam_lens")

    # ==================================== 17. QUICK REVISION + SUMMARY ==========

    def summary(self):
        self.scene_start("S17_summary", title="Quick Revision and Summary")

        head = self.heading("Quick revision")
        ideas = VGroup(pill("LCM:  where repeating things first meet", WORD, size=LABEL), pill("HCF:  the largest equal piece", RATIO, size=LABEL))\
            .arrange(RIGHT, buff=0.5)
        choose = text("choose from the wording, then check with the size limits", LABEL, INK, BOLD)
        box = pill("clock → LCM          saw → HCF          HCF divides LCM", GOOD, size=LABEL)
        nxt = self.breadcrumb("Next", "Video 2 · Finding HCF & LCM")
        self.stack(head, [ideas, choose, box, nxt], buff=0.7, top=0.8)
        self.no_overlap(*ideas)

        n = self.narrate(
            id="summary_01",
            text="The L C M is where repeating things first meet; the H C F is the largest equal piece.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "meet")
        self.play(FadeIn(ideas[0], shift=UP * 0.1))
        self.at_word(n, "piece")
        self.play(FadeIn(ideas[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_02",
            text="Choose from the wording, then use the size limits to check.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "wording")
        self.play(FadeIn(choose, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_03",
            text="Remember the formula box: clock, L C M; saw, H C F; and the H C F divides the L C M.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "box")
        self.play(FadeIn(box, scale=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_04",
            text="Next: finding the H C F and the L C M.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Next")
        self.play(FadeIn(nxt, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S17_summary")

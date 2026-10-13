"""
animation.py for the LMS video generator.

Course : Pre-C-CAT - Section A - Quantitative Aptitude
Video  : Lesson 25 - Alligation & Mixtures - 07 - Speed Tricks

Source script:
  C:\\Scripts\\Section A\\Module2\\S21-25_Ratio_Age_Clock_Mixtures_Mensuration\\Lesson 25 - Allegation & Mixtures\\07 - Speed Tricks.pdf

Built on the golden-reference pattern:
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``;
  * layouts stacked with next_to and guarded with ``no_overlap``; nothing is
    ever animated onto or into another box.

Lesson 25, Video 7 of 7 (Speed Tricks). Not the first video of the lesson: a silent breadcrumb, a one-line recap of Video 6,
then today's topic. No spoken course welcome.
The seven source scripts of this lesson are identical apart from their titles, so, as agreed with the course owner, each video was
written for its own topic. This one turns the lesson's formulas (the script's formula box) into six one-line shortcuts, with the
script's hook (rice at 40 and 60 making 48), a "when it fails" screen, one trap and five timed drills. Every result is checked
in the data block.
Text colours: white and grey, one blue accent, green and red only for right and wrong.
Pauses: 10 seconds on the hook, then timers on the five drills (8, 8, 10, 10, 6 seconds).
The closing breadcrumb points to the Lesson 25 Practice Kit and then Lesson 26, Problems on Mensuration.
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

from fractions import Fraction as F

# ---- the hook and the shortcuts ----
assert F(60 - 48, 48 - 40) == F(3, 2) and 40 * 3 + 60 * 2 == 48 * 5
assert F(40 - 30, 30 - 20) == 1 and F(60 - 45, 45) == F(1, 3) and (50 * 12 // 20, 50 * 8 // 20) == (30, 20)
assert 50 * F(4, 5) ** 2 == 32 and F(1, 4) == F(25, 100) and F(20, 100) == F(1, 5)
# ---- when it fails, the trap, and the timed drills: (seconds, question, answer) ----
assert F(66, 1) / F(11, 10) == 60 and F(2 * 40 + 3 * 60, 5) == 52 and 60 * F(4, 5) * F(3, 4) == 36
assert F(50 - 30, 30 - 20) == 2
assert F(50 - 42, 42 - 30) == F(2, 3) and F(50 - 40, 40) == F(1, 4) and F(40 - 25, 25 - 10) == 1
assert 40 * F(4, 5) ** 2 == F(128, 5) and F(3, 12) == F(25, 100)
DRILLS = [(8, "₹30 and ₹50 a kg, to make ₹42 a kg.  Cheaper : dearer?", "8 : 12  =  2 : 3"),
          (8, "Water and milk at ₹50 a litre, to make ₹40 a litre.  Water : milk?", "10 : 40  =  1 : 4"),
          (10, "10% and 40%, to make 60 L of 25%.  How much of each?", "15 : 15 = 1 : 1;      30 L each"),
          (10, "8 L of a 40 L vessel of milk is replaced with water, twice.  Milk left?", "40 × (4/5)^2  =  25.6 L"),
          (6, "3 L of water is added to 12 L of milk and sold at the cost price.  Profit percent?", "3/12  =  25%")]

OBJECTIVES = [("Write an alligation ratio with two subtractions", "and place the mean by eye before you calculate"),
              ("Handle water, known totals and replacement in one line each", "without setting up an equation"),
              ("Know when each shortcut fails", "and what to do instead")]
FORMULAS = ["Cross:      qL : qH   =   (H − M) : (M − L)",
            "Water:      water : liquid   =   (H − M) : M",
            "Known total T:      share   =   T × (its difference)/(H − L)",
            "Replacement:      original left   =   V × (1 − x/V)^n",
            "Milk and water at the cost price:      profit %   =   water ÷ milk × 100"]
FAILS = [("The cross needs a mean between the two values, and a cost", "sold at ₹66 with 10% profit:  the mean is 66 ÷ 1.1 = ₹60,  not 66"),
         ("The cross gives a ratio;  it cannot find a mean", "2 kg at ₹40 and 3 kg at ₹60:  use the average, (80 + 180)/5 = ₹52"),
         ("The power needs the same amount each time, and a full refill", "60 L, then 12 L and 15 L replaced:  multiply 4/5 × 3/4 instead,  36 L"),
         ("Water ÷ milk works only at the cost price of milk", "at any other selling price, find the cost and the selling price separately")]
TRAPS = [("Trap  ·  the differences on the wrong side",
          "20% and 50% solutions are mixed to make 30%.  Find the ratio weaker : stronger.",
          "(30 − 20) : (50 − 30)  =  1 : 2", "(50 − 30) : (30 − 20)  =  2 : 1",
          "The mean is nearer 20%, so there is more of the weaker.  Cross over.")]


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


class SpeedTricksAlligationVideo(LMSScene):
    lesson_title = "Speed Tricks: Alligation & Mixtures"

    def construct(self):
        self.camera.background_color = BG

        self.intro()
        self.hook()
        self.objectives()
        self.the_slow_way()
        self.cross_and_position()
        self.water_and_total()
        self.power_and_profit()
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
        self.side = None                         # the formula panel leaves with its screen
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
        side = getattr(self, "side", None)
        fit_within(body, self.body_w(), SAFE_H - head.height - top - 0.3)
        body.next_to(head, DOWN, buff=top)
        if side is not None:                     # the formula panel keeps the left; the example works on the right
            body.set_x(FRAME_W / 2 - SAFE - self.body_w() / 2)
            side.next_to(head, DOWN, buff=top).to_edge(LEFT, buff=SAFE)
            self.no_overlap(side, body)
            self.no_overlap(head, side)
            self.validator.check_in_frame(side)
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
        if getattr(self, "side", None) is None:
            rows = VGroup(*[VGroup(pill(str(i + 1), color, size=SMALL), text(what, LABEL, INK), text(result, LABEL, GOOD, BOLD))
                            .arrange(RIGHT, buff=0.3) for i, (what, result) in enumerate(steps)])
            return rows.arrange(DOWN, buff=0.5, aligned_edge=LEFT)
        rows = VGroup()                          # beside a formula panel: long lines wrap, a long result drops below
        for i, (what, result) in enumerate(steps):
            chip = pill(str(i + 1), color, size=SMALL)
            row = VGroup(chip, fitted_text(what, self.body_w() - chip.width - 0.3, LABEL, INK, max_lines=2),
                         text(result, LABEL, GOOD, BOLD)).arrange(RIGHT, buff=0.3)
            if row.width > self.body_w():
                row[1].align_to(chip, UP)
                row[2].next_to(row[1], DOWN, buff=0.15, aligned_edge=LEFT)
            rows.add(row)
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

    SIDE_W = 4.3                                  # width of the formula panel kept on the left of an example

    def side_panel(self, lines, title="Formula"):
        """The main formula(s) for the example on screen, in a panel that stays on the left
        while the working builds up on the right.  ``stack`` lays the example out beside it."""
        # a line that already has its own line breaks is kept as written (formulas break at the operators)
        rows = VGroup(*[text(s, LABEL, INK, BOLD) if chr(10) in s else
                        fitted_text(s, self.SIDE_W - 0.7, LABEL, INK, BOLD, max_lines=4) for s in lines])
        scale = min(1.0, *[(self.SIDE_W - 0.7) / r.width for r in rows])
        for r in rows:                           # every formula line at the same size
            r.scale(scale)
        rows.arrange(DOWN, buff=0.35, aligned_edge=LEFT)
        content = VGroup(text(title, SMALL, MUTED, BOLD), rows).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        panel = self.card(content, width=self.SIDE_W, color=FOCUS)
        panel.to_edge(LEFT, buff=SAFE).set_y(CARD_TOP - 1.3 - panel.height / 2)
        self.side = panel
        return panel

    def body_w(self):
        """Width left for the content of the screen (narrower beside a formula panel)."""
        return SAFE_W if getattr(self, "side", None) is None else SAFE_W - self.SIDE_W - 0.4
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

        crumb = self.breadcrumb("Quantitative Aptitude", "Lesson 25 · Alligation & Mixtures", "Video 7 of 7")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        recap = VGroup(text("last video", SMALL, MUTED), pill("turn percentages into amounts;  track what does not change", WORD, size=LABEL)).arrange(DOWN, buff=0.25)
        title = fit_width(text("Speed Tricks: Alligation & Mixtures", TITLE, INK, BOLD), SAFE_W - 0.4)
        today = text("today: every mixture question in one line", LABEL, FOCUS)
        block = VGroup(recap, title, today).arrange(DOWN, buff=0.7)
        fit_within(block, SAFE_W, SAFE_H - crumb.height - 0.9)
        block.next_to(crumb, DOWN, buff=0.7)
        self.no_overlap(crumb, recap, title, today)
        self.validator.check_in_frame(VGroup(crumb, block))

        n = self.narrate(
            id="intro_01",
            text="In the last video, you turned percentages into amounts and tracked what does not change.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.at_word(n, "tracked")
        self.play(FadeIn(recap, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="intro_02",
            text="Today: speed tricks for alligation and mixtures: every mixture question in one line.",
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
        given = VGroup(pill("rice at ₹40 a kg", WORD, size=LABEL), pill("rice at ₹60 a kg", WORD, size=LABEL),
                       pill("blend at ₹48 a kg", WORD, size=LABEL)).arrange(RIGHT, buff=0.35)
        ask = pill("In what ratio are they mixed?", FOCUS, size=BODY)
        target = VGroup(text("an equation in x and y takes most of a minute", LABEL, MUTED),
                        text("today's target: two subtractions", LABEL, INK, BOLD)).arrange(DOWN, buff=0.25)
        self.stack(head, [given, ask, target], buff=0.8, top=0.9)
        self.no_overlap(*given)

        n = self.narrate(
            id="hook_01",
            text="Ten seconds. Rice at forty rupees and rice at sixty rupees a kilogram make a blend worth forty-eight. In "
                 "what ratio are they mixed?",
            voice="default",
            subtitle=True,
            pause_after=10.0,
        )
        self.at_word(n, "Ten")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "Rice")
        self.play(FadeIn(given, shift=UP * 0.1))
        self.at_word(n, "ratio")
        self.play(FadeIn(ask, scale=1.03))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="hook_02",
            text="An equation in x and y takes most of a minute. Today's target is two subtractions.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "equation")
        self.play(FadeIn(target[0], shift=UP * 0.1))
        self.at_word(n, "subtractions")
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
            text="First, write an alligation ratio with two subtractions, and place the mean by eye before you calculate.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "subtractions")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "eye")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="objectives_03",
            text="Second, handle water, known totals and replacement in one line each, without setting up an equation.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "water")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "equation")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="objectives_04",
            text="Third, know when each shortcut fails, and what to do instead.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "fails")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "instead")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_objectives")

    # ============================================== 3. THE SLOW WAY ==========

    def the_slow_way(self):
        self.scene_start("S03_the_slow_way", title="The Slow Way")

        head = self.heading("The slow way:  an equation", BAD)
        lines = VGroup(text("let the quantities be x kg and y kg", BODY, INK, BOLD),
                       text("40x + 60y  =  48(x + y)", BODY, INK, BOLD),
                       text("12y  =  8x,    so    x : y  =  3 : 2", BODY, INK, BOLD)).arrange(DOWN, buff=0.5)
        verdict = pill("reliable, but about 40 seconds", BAD, size=LABEL)
        self.stack(head, [lines, verdict], buff=0.9, top=1.0)
        self.no_overlap(*lines)

        n = self.narrate(
            id="the_slow_way_01",
            text="Let the quantities be x and y kilograms, write forty x plus sixty y equals forty-eight times x plus y, "
                 "and simplify to three to two.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "quantities")
        self.play(FadeIn(lines[0], shift=UP * 0.1))
        self.at_word(n, "equals")
        self.play(FadeIn(lines[1], shift=UP * 0.1))
        self.at_word(n, "simplify")
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

    # ============================================== 4. SHORTCUTS 1 AND 2 - THE CROSS; THE MEAN BY EYE ==========

    def cross_and_position(self):
        self.scene_start("S04_cross_and_position", title="Shortcuts 1 and 2 - The Cross; the Mean by Eye")

        head = self.heading("Shortcuts 1 and 2")
        one = VGroup(pill("the cross in your head:   cheaper : dearer  =  (H − M) : (M − L)", WORD, size=LABEL),
                     text("the hook:     (60 − 48) : (48 − 40)  =  12 : 8  =  3 : 2", LABEL, GOOD, BOLD)).arrange(DOWN, buff=0.3)
        two = VGroup(pill("place the mean by eye:   it sits nearer the larger share", WORD, size=LABEL),
                     text("mean in the middle (₹20, ₹40 making ₹30):     1 : 1,  no working", LABEL, GOOD, BOLD),
                     text("48 is nearer 40 than 60:     more of the ₹40 rice, so 3 : 2 and not 2 : 3", LABEL, GOOD, BOLD)).arrange(DOWN, buff=0.3)
        self.stack(head, [one, two], buff=0.8, top=0.7)

        n = self.narrate(
            id="cross_and_position_01",
            text="Shortcut one: the cross in your head. Cheaper to dearer is H minus M to M minus L.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "cross")
        self.play(FadeIn(one[0], scale=1.03))
        self.at_word(n, "minus")
        self.play(Indicate(one[0], color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="cross_and_position_02",
            text="The hook: sixty minus forty-eight to forty-eight minus forty is twelve to eight: three to two.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "minus")
        self.play(FadeIn(one[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="cross_and_position_03",
            text="Shortcut two: place the mean by eye. It sits nearer the larger share.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "eye")
        self.play(FadeIn(two[0], scale=1.03))
        self.at_word(n, "nearer")
        self.play(Indicate(two[0], color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="cross_and_position_04",
            text="If the mean is exactly in the middle, like twenty and forty making thirty, the ratio is one to one with "
                 "no working.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "middle")
        self.play(FadeIn(two[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="cross_and_position_05",
            text="And forty-eight is nearer forty than sixty, so there is more of the forty rupee rice: three to two, not "
                 "two to three.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "nearer")
        self.play(FadeIn(two[2], shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_cross_and_position")

    # ============================================== 5. SHORTCUTS 3 AND 4 - WATER AS ZERO; A KNOWN TOTAL ==========

    def water_and_total(self):
        self.scene_start("S05_water_and_total", title="Shortcuts 3 and 4 - Water as Zero; a Known Total")

        head = self.heading("Shortcuts 3 and 4")
        three = VGroup(pill("water as zero:   water : liquid  =  (H − M) : M", WORD, size=LABEL),
                       text("milk at ₹60 a litre brought down to ₹45:     15 : 45  =  1 : 3", LABEL, GOOD, BOLD)).arrange(DOWN, buff=0.3)
        four = VGroup(pill("a known total T in one line:   share  =  T × (its difference)/(H − L)", WORD, size=LABEL),
                      text("50 kg of the ₹48 blend:     cheaper  =  50 × 12/20  =  30 kg;      dearer  =  50 × 8/20  =  20 kg", LABEL, GOOD, BOLD))\
            .arrange(DOWN, buff=0.3)
        fit_width(four, SAFE_W - 0.6)
        self.stack(head, [three, four], buff=0.9, top=0.9)

        n = self.narrate(
            id="water_and_total_01",
            text="Shortcut three: water as zero. Water to liquid is H minus M to M.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "zero")
        self.play(FadeIn(three[0], scale=1.03))
        self.at_word(n, "minus")
        self.play(Indicate(three[0], color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="water_and_total_02",
            text="Milk at sixty rupees a litre brought down to forty-five: fifteen to forty-five, one to three.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "fifteen")
        self.play(FadeIn(three[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="water_and_total_03",
            text="Shortcut four: a known total in one line. Each share is the total times its difference, over H minus L.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "total")
        self.play(FadeIn(four[0], scale=1.03))
        self.at_word(n, "share")
        self.play(Indicate(four[0], color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="water_and_total_04",
            text="For fifty kilograms of the forty-eight rupee blend, the cheaper is fifty times twelve over twenty, "
                 "thirty kilograms, and the dearer is fifty times eight over twenty, twenty kilograms.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "cheaper")
        self.play(FadeIn(four[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_water_and_total")

    # ============================================== 6. SHORTCUTS 5 AND 6 - THE REPLACEMENT POWER; WATER AS PROFIT ==========

    def power_and_profit(self):
        self.scene_start("S06_power_and_profit", title="Shortcuts 5 and 6 - The Replacement Power; Water as Profit")

        head = self.heading("Shortcuts 5 and 6")
        five = VGroup(pill("replacement in one line:   original left  =  V × (1 − x/V)^n", WORD, size=LABEL),
                      text("50 L of milk, 10 L replaced twice:     50 × (4/5)^2  =  32 L", LABEL, GOOD, BOLD)).arrange(DOWN, buff=0.3)
        six = VGroup(pill("milk and water sold at the cost price:   profit %  =  water ÷ milk × 100", WORD, size=LABEL),
                     text("1 L of water in 4 L of milk:     25%", LABEL, GOOD, BOLD),
                     text("to gain 20%:     water : milk  =  20 : 100  =  1 : 5", LABEL, GOOD, BOLD)).arrange(DOWN, buff=0.3)
        self.stack(head, [five, six], buff=0.8, top=0.7)

        n = self.narrate(
            id="power_and_profit_01",
            text="Shortcut five: replacement in one line. The original left is V times one minus x over V, to the power n.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "replacement")
        self.play(FadeIn(five[0], scale=1.03))
        self.at_word(n, "power")
        self.play(Indicate(five[0], color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="power_and_profit_02",
            text="Fifty litres of milk with ten litres replaced twice: fifty times four fifths squared, thirty-two litres.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "squared")
        self.play(FadeIn(five[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="power_and_profit_03",
            text="Shortcut six: milk and water sold at the cost price of milk. The profit percent is water over milk, "
                 "times one hundred.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "cost")
        self.play(FadeIn(six[0], scale=1.03))
        self.at_word(n, "over")
        self.play(Indicate(six[0], color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="power_and_profit_04",
            text="One litre of water in four litres of milk is twenty-five percent.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "twenty-five")
        self.play(FadeIn(six[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="power_and_profit_05",
            text="And to gain twenty percent, water to milk is twenty to one hundred: one to five.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "gain")
        self.play(FadeIn(six[2], shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_power_and_profit")

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
            text="Here is the formula box. The cross: the quantities are in the ratio H minus M to M minus L.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "box")
        self.play(FadeIn(box[0]))
        self.at_word(n, "cross")
        self.play(FadeIn(lines[0], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_box_02",
            text="With water, water to liquid is H minus M to M.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "water")
        self.play(FadeIn(lines[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_box_03",
            text="With a known total, each share is the total times its difference over H minus L.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "total")
        self.play(FadeIn(lines[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_box_04",
            text="For replacement, the original left is V times one minus x over V, to the power n.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "replacement")
        self.play(FadeIn(lines[3], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_box_05",
            text="And for milk and water at the cost price, the profit percent is water over milk, times one hundred.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "profit")
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
            text="The cross needs a mean between the two values, and it must be a cost. If the blend is sold at sixty-six "
                 "rupees with ten percent profit, the mean is sixty, not sixty-six.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "between")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "sold")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="when_it_fails_02",
            text="The cross gives a ratio; it cannot find a mean. For two kilograms at forty and three at sixty, use the "
                 "average: fifty-two rupees.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "cannot")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "average")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="when_it_fails_03",
            text="The power needs the same amount each time, and a full refill. With twelve and then fifteen litres "
                 "replaced from sixty, multiply four fifths by three quarters instead: thirty-six litres.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "same")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "multiply")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="when_it_fails_04",
            text="Water over milk works only at the cost price of milk. At any other selling price, find the cost and the "
                 "selling price separately.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "only")
        self.play(FadeIn(blocks[3][0], shift=RIGHT * 0.2))
        self.at_word(n, "separately")
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
            text="The trap: the differences on the wrong side. Twenty percent and fifty percent solutions are mixed to "
                 "make thirty percent: find the ratio of weaker to stronger.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "trap")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "mixed")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="the_trap_02",
            text="The wrong instinct writes thirty minus twenty to fifty minus thirty: one to two. The correct answer "
                 "crosses over: twenty to ten, two to one.",
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
            text="The rule: the mean is nearer twenty percent, so there is more of the weaker. Cross over.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "rule")
        self.play(FadeIn(rule, shift=UP * 0.1))
        self.at_word(n, "Cross")
        self.play(Indicate(rule, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S09_the_trap")

    # ============================================== 10. TIMED DRILLS ==========

    def timed_drills(self):
        self.scene_start("S10_timed_drills", title="Timed Drills")

        head, q, ans = self.drill(1, DRILLS[0])

        n = self.narrate(
            id="timed_drills_01",
            text="Drill one, eight seconds: thirty and fifty rupees a kilogram, to make forty-two. What is cheaper to "
                 "dearer?",
            voice="default",
            subtitle=True,
            pause_after=8.0,
        )
        self.at_word(n, "Drill")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "rupees")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="timed_drills_02",
            text="Eight to twelve: two to three.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "twelve")
        self.play(FadeIn(ans, scale=1.03))
        self.wait_for_narration(n)
        self.clear_stage()

        head, q, ans = self.drill(2, DRILLS[1])

        n = self.narrate(
            id="timed_drills_03",
            text="Drill two, eight seconds: water and milk at fifty rupees a litre, to make forty. What is water to milk?",
            voice="default",
            subtitle=True,
            pause_after=8.0,
        )
        self.at_word(n, "Drill")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "milk")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="timed_drills_04",
            text="Ten to forty: one to four.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "forty")
        self.play(FadeIn(ans, scale=1.03))
        self.wait_for_narration(n)
        self.clear_stage()

        head, q, ans = self.drill(3, DRILLS[2])

        n = self.narrate(
            id="timed_drills_05",
            text="Drill three, ten seconds: ten percent and forty percent, to make sixty litres of twenty-five percent. "
                 "How much of each?",
            voice="default",
            subtitle=True,
            pause_after=10.0,
        )
        self.at_word(n, "Drill")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "percent")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="timed_drills_06",
            text="Fifteen to fifteen is one to one: thirty litres each.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "thirty")
        self.play(FadeIn(ans, scale=1.03))
        self.wait_for_narration(n)
        self.clear_stage()

        head, q, ans = self.drill(4, DRILLS[3])

        n = self.narrate(
            id="timed_drills_07",
            text="Drill four, ten seconds: eight litres of a forty litre vessel of milk is replaced with water, twice. How "
                 "much milk is left?",
            voice="default",
            subtitle=True,
            pause_after=10.0,
        )
        self.at_word(n, "Drill")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "vessel")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="timed_drills_08",
            text="Forty times four fifths squared: twenty-five point six litres.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "squared")
        self.play(FadeIn(ans, scale=1.03))
        self.wait_for_narration(n)
        self.clear_stage()

        head, q, ans = self.drill(5, DRILLS[4])

        n = self.narrate(
            id="timed_drills_09",
            text="Drill five, six seconds: three litres of water is added to twelve litres of milk and sold at the cost "
                 "price. What is the profit percent?",
            voice="default",
            subtitle=True,
            pause_after=6.0,
        )
        self.at_word(n, "Drill")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "water")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="timed_drills_10",
            text="Three over twelve: twenty-five percent.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "over")
        self.play(FadeIn(ans, scale=1.03))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S10_timed_drills")

    # ============================================== 11. QUICK REVISION ==========

    def quick_revision(self):
        self.scene_start("S11_quick_revision", title="Quick Revision")

        head = self.heading("Quick revision")
        first = VGroup(pill("cross:  (H − M) : (M − L)", WORD, size=LABEL), pill("the mean sits nearer the larger share", WORD, size=LABEL))\
            .arrange(RIGHT, buff=0.5)
        second = VGroup(pill("water:  (H − M) : M", RATIO, size=LABEL), pill("total:  T × difference/(H − L)", RATIO, size=LABEL))\
            .arrange(RIGHT, buff=0.5)
        third = VGroup(pill("replacement:  V × (1 − x/V)^n", WORD, size=LABEL), pill("profit %  =  water ÷ milk", WORD, size=LABEL))\
            .arrange(RIGHT, buff=0.5)
        nxt = self.breadcrumb("Next", "Lesson 25 Practice Kit", "Lesson 26 · Problems on Mensuration")
        self.stack(head, [first, second, third, nxt], buff=0.75, top=0.9)
        self.no_overlap(*first)
        self.no_overlap(*second)
        self.no_overlap(*third)

        n = self.narrate(
            id="quick_revision_01",
            text="Run the cross with two subtractions, and remember that the mean sits nearer the larger share.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "cross")
        self.play(FadeIn(first[0], shift=UP * 0.1))
        self.at_word(n, "nearer")
        self.play(FadeIn(first[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="quick_revision_02",
            text="Treat water as zero, and split a known total with its difference over H minus L.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "water")
        self.play(FadeIn(second[0], shift=UP * 0.1))
        self.at_word(n, "total")
        self.play(FadeIn(second[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="quick_revision_03",
            text="For replacement, raise the fraction left to the power n; for milk and water at cost price, the profit is "
                 "water over milk.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "replacement")
        self.play(FadeIn(third[0], shift=UP * 0.1))
        self.at_word(n, "profit")
        self.play(FadeIn(third[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="quick_revision_04",
            text="Next: the lesson twenty-five practice kit, and then lesson twenty-six, problems on mensuration.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Next")
        self.play(FadeIn(nxt, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S11_quick_revision")

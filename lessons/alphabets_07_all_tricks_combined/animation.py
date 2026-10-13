"""
animation.py for the LMS video generator.

Course : Pre-C-CAT - Section A - Logical Reasoning
Video  : Lesson 3 - Directions Sense Test - 07 - All Tricks Combined

Source script:
  C:\\Scripts\\Section A\\Reasoning_Scripts\\Sessions 1-4 - Coding-Decoding, Alphabets, Directions, Number Series, Odd Man Out\\Lesson 3 - Directions Sense Test\\07 - All Tricks Combined.pdf

Built on the golden-reference pattern:
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``;
  * layouts stacked with next_to and guarded with ``no_overlap``; nothing is
    ever animated onto or into another box.

Lesson 3, Video 6 of 6 (file 07 in its folder), the exam-level wrap-up; it has no practice set or section quiz.
Not the first video: a silent breadcrumb, a one-line recap of Video 5, then today's topic.
The narration follows the script: hook, objectives, every section's short trick, the slow way, six exam shortcuts,
the rule box, when it fails, one trap, five timed drills and the quick revision.
In the short-trick table each trick is shortened to fit two lines on screen; the narration gives it in full.
Timers: 10 seconds on the hook, and 6, 6, 6, 6 and 5 seconds on the timed drills, as in the script.
Every answer in the script was recomputed in the data block; all of them are correct.
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

import math as _math

POINTS = ["north", "north-east", "east", "south-east", "south", "south-west", "west", "north-west"]
STEP = {"N": (0, 1), "E": (1, 0), "S": (0, -1), "W": (-1, 0)}
ORDER = ["N", "E", "S", "W"]


def net_of(*legs):
    return sum(d * STEP[w][0] for d, w in legs), sum(d * STEP[w][1] for d, w in legs)


def after_turns(facing, turns):
    """Facing after a string of R / L turns."""
    return ORDER[(ORDER.index(facing) + turns.count("R") - turns.count("L")) % 4]


def walk(facing, *moves):
    legs = []
    for m in moves:
        if m in ("R", "L"):
            facing = after_turns(facing, m)
        else:
            legs.append((m, facing))
    return legs


def renamed(name, old, new):
    return POINTS[(POINTS.index(name) + POINTS.index(new) - POINTS.index(old)) % 8]


HOOK_LEGS = [(5, "E"), (3, "N"), (2, "W"), (3, "S"), (1, "W")]
assert net_of(*HOOK_LEGS) == (2, 0) and 5 - 2 - 1 == 2 and 3 - 3 == 0
assert after_turns("N", "R") == "E" and after_turns("N", "RR") == "S" and after_turns("N", "RRR") == after_turns("N", "L") == "W"
assert all(a * a + b * b == c * c for a, b, c in [(3, 4, 5), (6, 8, 10), (5, 12, 13), (8, 15, 17)]) and round(_math.sqrt(2), 2) == 1.41
assert after_turns("S", "L") == "E" and after_turns("S", "R") == "W" and renamed("south", "north", "south") == "north"
TRAP_LEGS = walk("N", 4, "R", 6, "R", 4, "L", 2)
assert TRAP_LEGS == [(4, "N"), (6, "E"), (4, "S"), (2, "E")] and net_of(*TRAP_LEGS) == (8, 0)
# ---- timed drills ----
assert after_turns("W", "RRRLL") == "N" and net_of((8, "N"), (6, "W")) == (-6, 8) and _math.hypot(6, 8) == 10
assert after_turns("N", "R") == "E" and renamed("east", "south", "north") == "west"

OBJECTIVES = [("Find a final facing direction", "by counting net turns"),
              ("Cancel opposite legs", "before drawing anything"),
              ("Recognise Pythagorean triples and equal-component diagonals", "instantly")]
TRICKS = [["Directions & Turns",
           "Score each right +1 and each left −1, add, and make that many quarter-turns clockwise;  a net of 3 = one left."],
          ["Distance & Displacement",
           "Keep two running totals as you read, east–west and north–south;  only the two final totals matter."],
          ["Shadows & Renamed Directions",
           "Morning shadows point west, evening shadows east;  renames:  one rotation angle, applied to every direction."],
          ["Relative Position & Coded Directions",
           "Put the shared point at (0, 0);  read “A is north of B” as “from B, go north to reach A”;  subtract coordinates."],
          ["Two Movers & Clock Directions",
           "Movers:  compare end points, never path lengths;  clocks:  hand angle from 12, plus the rotation of the 12 mark."]]
FORMULAS = ["Net turns:   (rights − lefts) mod 4",
            "Cancel opposite legs first",
            "Triples:   3-4-5,    6-8-10,    5-12-13,    8-15-17",
            "Equal nets:   side × √2",
            "Facing south:   left = east",
            "Rename:   one rotation for all"]
FAILS = [("Cancelling works for paths along N, S, E and W", "a 45° leg needs splitting into components, or a drawing"),
         ("Net turns work for 90° turns only", "mix in 45° or 135° turns, and you must add angles instead"),
         ("If the nets are not a triple", "give the answer as a root, such as √41, or check the options for the nearest value")]
TRAPS = [("Trap  ·  cancelling legs before fixing their directions",
          "Facing north:  walk 4 km,  right 6 km,  right 4 km,  left 2 km.   How far from the start?",
          "the last leg is west, because “left”", "left from south is east:   8 km east",
          "fix each leg's direction from the current facing, then cancel")]


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


class AllTricksCombinedDirectionsVideo(LMSScene):
    lesson_title = "All Tricks Combined: Directions Sense Test"

    def construct(self):
        self.camera.background_color = BG

        self.intro()
        self.hook()
        self.objectives()
        self.why_this_video()
        self.every_short_trick()
        self.slow_way()
        self.exam_shortcuts()
        self.rule_box()
        self.when_it_fails()
        self.trap()
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

    def table_under(self, head, ref, header, rows, widths, size=SMALL):
        """A reference block under ``head`` and a table under it, fitted to the space that is left.  Returns (table, body rows)."""
        fit_width(ref, SAFE_W)
        ref.next_to(head, DOWN, buff=0.35)
        table = self.table_rows(header, rows, widths, size=size)
        fit_within(table, SAFE_W, ref.get_bottom()[1] + FRAME_H / 2 - SAFE - 1.2)
        table.next_to(ref, DOWN, buff=0.4)
        self.no_overlap(head, ref, table)
        self.no_overlap(*table)
        self.validator.check_in_frame(VGroup(head, ref, table))
        return table, table[1:]
    def step_rows(self, items, color=WORD):
        """Numbered concept steps.  Each row = (number chip, the step[, a short note in green])."""
        rows = VGroup()
        for i, (what, note) in enumerate(items):
            row = VGroup(pill(str(i + 1), color, size=SMALL), text(what, LABEL, INK, BOLD))
            if note:
                row.add(text(note, LABEL, GOOD, BOLD))
            rows.add(row.arrange(RIGHT, buff=0.35))
        return fit_width(rows.arrange(DOWN, buff=0.5, aligned_edge=LEFT), SAFE_W - 0.6)

    def drill(self, head, ask, work, result):
        """A timed drill: the question, then its working and answer.  Returns (ask, work, answer)."""
        parts = VGroup(fit_width(pill(ask, FOCUS, size=BODY), SAFE_W - 0.4), text(work, BODY, INK, BOLD), pill(result, GOOD, size=BODY))
        self.stack(head, list(parts), buff=1.0, top=1.2)
        return parts

    # ============================================== 0. INTRO ==========
    # Not the first video: silent breadcrumb, a one-line recap of the previous video, then today's topic.

    def intro(self):
        self.scene_start("S00_intro", title="Intro")

        crumb = self.breadcrumb("Logical Reasoning", "Lesson 3 · Directions Sense Test", "Video 6 of 6")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        recap = VGroup(text("from Video 5  ·  Two Movers & Clock Directions", SMALL, MUTED), pill("compare end points;   hand angle + rotation of the 12 mark", WORD, size=LABEL)).arrange(DOWN, buff=0.25)
        title = fit_width(text("All Tricks Combined", TITLE, INK, BOLD), SAFE_W - 0.4)
        today = text("today: one decision path for the whole topic", LABEL, FOCUS)
        block = VGroup(recap, title, today).arrange(DOWN, buff=0.7)
        fit_within(block, SAFE_W, SAFE_H - crumb.height - 0.9)
        block.next_to(crumb, DOWN, buff=0.7)
        self.no_overlap(crumb, recap, title, today)
        self.validator.check_in_frame(VGroup(crumb, block))

        n = self.narrate(
            id="intro_01",
            text="In the last video, two movers meant comparing two end points, and a clock hand was an angle from twelve "
                 "plus the rotation of the twelve mark.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.at_word(n, "comparing")
        self.play(FadeIn(recap[0]))
        self.at_word(n, "angle")
        self.play(FadeIn(recap[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="intro_02",
            text="This last video of the lesson puts all the tricks together: one decision path for the whole topic.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "together")
        self.play(FadeIn(title, shift=UP * 0.1))
        self.at_word(n, "path")
        self.play(FadeIn(today, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_intro")

    # ============================================== 1. HOOK ==========

    def hook(self):
        self.scene_start("S01_hook", title="Hook")

        head = self.heading("Ten seconds")
        ask = pill("5 km east,  3 km north,  2 km west,  3 km south,  1 km west.   Distance from the start?", FOCUS, size=LABEL)
        ways = VGroup(VGroup(pill("drawing five legs", BAD, size=LABEL), text("thirty seconds", BODY, INK, BOLD)).arrange(RIGHT, buff=0.5),
                      VGroup(pill("cancelling them", GOOD, size=LABEL), text("five seconds", BODY, GOOD, BOLD)).arrange(RIGHT, buff=0.5))\
            .arrange(DOWN, buff=0.5, aligned_edge=LEFT)
        self.stack(head, [ask, ways], buff=1.2, top=1.2)
        self.no_overlap(*ways)

        n = self.narrate(
            id="hook_01",
            text="Five kilometres east, three north, two west, three south, one west. What is the distance from the start? "
                 "You have ten seconds.",
            voice="default",
            subtitle=True,
            pause_after=10.0,
        )
        self.at_word(n, "Five")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "east")
        self.play(FadeIn(ask, scale=1.03))
        self.at_word(n, "distance")
        self.play(Indicate(ask, color=FOCUS, scale_factor=1.03))
        self.at_word(n, "ten")
        self.play(Indicate(head, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="hook_02",
            text="Drawing five legs takes thirty seconds.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Drawing")
        self.play(FadeIn(ways[0], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_03",
            text="Cancelling them takes five.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Cancelling")
        self.play(FadeIn(ways[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S01_hook")

    # ============================================== 2. OBJECTIVES ==========

    def objectives(self):
        self.scene_start("S02_objectives", title="Objectives")

        head = self.heading("By the end of this video")
        blocks = two_line_blocks(OBJECTIVES, WORD)
        self.stack(head, list(blocks), buff=0.6, top=0.8, align=LEFT)

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
            text="One: find a final facing direction by counting net turns.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "facing")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "counting")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="objectives_03",
            text="Two: cancel opposite legs before drawing anything.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "cancel")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "before")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="objectives_04",
            text="Three: recognise Pythagorean triples and equal-component diagonals instantly.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "recognise")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "instantly")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_objectives")

    # ============================================== 3. WHY THIS VIDEO ==========

    def why_this_video(self):
        self.scene_start("S03_why_this_video", title="Why This Video")

        head = self.heading("Why this video")
        each = pill("each section taught one short trick", WORD, size=BODY)
        path = pill("seen together:  a single decision path for the whole topic", GOOD, size=LABEL)
        use = text("which is how you will use them under exam time pressure", LABEL, MUTED)
        self.stack(head, [each, path, use], buff=1.0, top=1.2)

        n = self.narrate(
            id="why_this_video_01",
            text="Each section taught one short trick.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "short")
        self.play(FadeIn(each, scale=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="why_this_video_02",
            text="Seen together, they form a single decision path for the whole topic, which is how you will use them "
                 "under exam time pressure.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "path")
        self.play(FadeIn(path, shift=UP * 0.1))
        self.at_word(n, "pressure")
        self.play(FadeIn(use, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_why_this_video")

    # ============================================== 4. EVERY SECTION'S SHORT TRICK ==========

    def every_short_trick(self):
        self.scene_start("S04_every_short_trick", title="Every Section's Short Trick")

        head = self.heading("Every section's short trick  ·  1 to 3")
        table, rows = self.placed_table(head, ["Section", "Short trick"], TRICKS[:3], [4.2, 8.8], room=1.2)
        for row in rows:
            row[0].set_color(WORD)

        n = self.narrate(
            id="every_short_trick_01",
            text="Directions and turns: score each right as plus one and each left as minus one, add them, and make that "
                 "many quarter-turns clockwise. A net of three is the same as one left.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "turns")
        self.play(FadeIn(rows[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "score")
        self.play(FadeIn(rows[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="every_short_trick_02",
            text="Distance and displacement: keep two running totals as you read, east-west and north-south. Only the two "
                 "final totals matter; ignore everything else.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "displacement")
        self.play(FadeIn(rows[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "totals")
        self.play(FadeIn(rows[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="every_short_trick_03",
            text="Shadows and renamed directions: morning shadows point west, evening shadows point east. For renamed "
                 "directions, find one rotation angle and apply it to every direction.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Shadows")
        self.play(FadeIn(rows[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "morning")
        self.play(FadeIn(rows[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Every section's short trick  ·  4 and 5")
        table, rows = self.placed_table(head, ["Section", "Short trick"], TRICKS[3:], [4.2, 8.8], room=1.2)
        for row in rows:
            row[0].set_color(WORD)

        n = self.narrate(
            id="every_short_trick_04",
            text="Relative position and coded directions: put the shared point at zero, zero; read, A is north of B, as, "
                 "from B, go north to reach A; and subtract coordinates.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "position")
        self.play(FadeIn(rows[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "shared")
        self.play(FadeIn(rows[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="every_short_trick_05",
            text="Two movers and clock directions. For two movers, compare end points, never path lengths. For clocks, "
                 "take the hand angle from twelve, plus the rotation of the twelve mark.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "movers")
        self.play(FadeIn(rows[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "compare")
        self.play(FadeIn(rows[1][1], shift=RIGHT * 0.2))
        self.at_word(n, "clocks")
        self.play(Indicate(rows[1][1], color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_every_short_trick")

    # ============================================== 5. THE SLOW WAY ==========

    def slow_way(self):
        self.scene_start("S05_slow_way", title="The Slow Way")

        head = self.heading("The slow way", BAD)
        steps = VGroup(pill("draw every leg", MUTED, size=LABEL), text("→", BODY, MUTED), pill("mark every turn", MUTED, size=LABEL),
                       text("→", BODY, MUTED), pill("then measure", MUTED, size=LABEL)).arrange(RIGHT, buff=0.4)
        verdict = text("reliable, but slow on long paths", BODY, BAD, BOLD)
        self.stack(head, [steps, verdict], buff=1.2, top=1.5)
        self.no_overlap(*steps)

        n = self.narrate(
            id="slow_way_01",
            text="The slow way: draw every leg, mark every turn, then measure.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "draw")
        self.play(FadeIn(steps[0], shift=UP * 0.1))
        self.at_word(n, "mark")
        self.play(FadeIn(steps[1:3], shift=UP * 0.1))
        self.at_word(n, "measure")
        self.play(FadeIn(steps[3:], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="slow_way_02",
            text="Reliable, but slow on long paths.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "slow")
        self.play(FadeIn(verdict, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_slow_way")

    # ============================================== 6. THE EXAM SHORTCUTS ==========

    def exam_shortcuts(self):
        self.scene_start("S06_exam_shortcuts", title="The Exam Shortcuts")

        head = self.heading("Shortcuts 1 and 2  ·  net turns;  cancel first")
        turns = VGroup(pill("net turns  =  rights − lefts,  modulo 4", WORD, size=LABEL),
                       text("one net right = +90°        two = about turn        three = one left", SMALL, INK, BOLD)).arrange(DOWN, buff=0.25)
        cancel = VGroup(pill("cancel first:  list the legs by direction, cancel opposites", RATIO, size=LABEL),
                        text("the hook:    east  5 − 2 − 1  =  2        north  3 − 3  =  0", LABEL, INK, BOLD),
                        pill("answer:  2 km east", GOOD, size=LABEL)).arrange(DOWN, buff=0.3)
        self.stack(head, [turns, cancel], buff=1.0, top=0.9)

        n = self.narrate(
            id="exam_shortcuts_01",
            text="Shortcut one: net turns. Rights minus lefts, taken modulo four. One net right is plus ninety degrees, "
                 "two is an about turn, and three is one left.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "one")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "minus")
        self.play(FadeIn(turns[0], shift=UP * 0.1))
        self.at_word(n, "net", occurrence=2)
        self.play(FadeIn(turns[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_shortcuts_02",
            text="Shortcut two: cancel first. List the legs by direction and cancel opposites.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "two")
        self.play(Indicate(head, color=FOCUS, scale_factor=1.03))
        self.at_word(n, "List")
        self.play(FadeIn(cancel[0], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_shortcuts_03",
            text="For the hook: east is five minus two minus one, two; north is three minus three, zero. The answer is two "
                 "kilometres east.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "hook")
        self.play(FadeIn(cancel[1], shift=UP * 0.1))
        self.at_word(n, "answer")
        self.play(FadeIn(cancel[2], scale=1.03))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Shortcuts 3 and 4  ·  triples;  equal nets")
        triples = VGroup(pill("triples", WORD, size=LABEL), text("3-4-5,     6-8-10,     5-12-13,     8-15-17,     and their multiples", LABEL, INK, BOLD),
                         text("if the nets fit a triple, the distance is immediate", SMALL, GOOD, BOLD)).arrange(DOWN, buff=0.25)
        equal = VGroup(pill("equal nets", RATIO, size=LABEL), text("equal north–south and east–west nets give an exact diagonal", SMALL, INK, BOLD),
                       text("distance  =  side × √2     (about 1.41 × side)", LABEL, GOOD, BOLD)).arrange(DOWN, buff=0.25)
        self.stack(head, [triples, equal], buff=1.0, top=0.9)

        n = self.narrate(
            id="exam_shortcuts_04",
            text="Shortcut three: triples. Three, four, five; six, eight, ten; five, twelve, thirteen; eight, fifteen, "
                 "seventeen; and their multiples. If the nets fit a triple, the distance is immediate.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "three")
        self.play(FadeIn(triples[0], shift=UP * 0.1))
        self.at_word(n, "four")
        self.play(FadeIn(triples[1], shift=UP * 0.1))
        self.at_word(n, "immediate")
        self.play(FadeIn(triples[2], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_shortcuts_05",
            text="Shortcut four: equal nets. Equal north-south and east-west nets give an exact diagonal: the distance is "
                 "the side times root two, about one point four one times the side.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "four")
        self.play(FadeIn(equal[0], shift=UP * 0.1))
        self.at_word(n, "diagonal")
        self.play(FadeIn(equal[1], shift=UP * 0.1))
        self.at_word(n, "root")
        self.play(FadeIn(equal[2], shift=UP * 0.1))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Shortcuts 5 and 6  ·  the south mirror;  one rotation for renames")
        south = VGroup(pill("the south mirror", SECOND, size=LABEL), text("facing south, left and right are mirrored from the map", SMALL, INK, BOLD),
                       text("left = east          right = west", LABEL, GOOD, BOLD)).arrange(DOWN, buff=0.25)
        rename = VGroup(pill("one rotation for renames", RATIO, size=LABEL), text("rotation  =  new angle − old angle", LABEL, INK, BOLD),
                        text("opposite directions stay opposite:  a rename of north also fixes south", SMALL, GOOD, BOLD)).arrange(DOWN, buff=0.25)
        self.stack(head, [south, rename], buff=1.0, top=0.9)

        n = self.narrate(
            id="exam_shortcuts_06",
            text="Shortcut five: the south mirror. Facing south, left and right are mirrored from the map: left is east, "
                 "and right is west.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "five")
        self.play(FadeIn(south[0], shift=UP * 0.1))
        self.at_word(n, "mirrored")
        self.play(FadeIn(south[1], shift=UP * 0.1))
        self.at_word(n, "east")
        self.play(FadeIn(south[2], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_shortcuts_07",
            text="Shortcut six: one rotation for renames. The rotation is the new angle minus the old angle. Opposite "
                 "directions stay opposite, so a rename of north also fixes south.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "six")
        self.play(FadeIn(rename[0], shift=UP * 0.1))
        self.at_word(n, "minus")
        self.play(FadeIn(rename[1], shift=UP * 0.1))
        self.at_word(n, "opposite", occurrence=2)
        self.play(FadeIn(rename[2], shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_exam_shortcuts")

    # ============================================== 7. RULE BOX ==========

    def rule_box(self):
        self.scene_start("S07_rule_box", title="Rule Box")

        head = self.heading("Rule box", GOOD)
        lines = VGroup(*[text(f, LABEL, INK) for f in FORMULAS]).arrange(DOWN, buff=0.36, aligned_edge=LEFT)
        fit_width(lines, SAFE_W - 1.6)
        box = self.card(lines, width=SAFE_W - 0.4, color=GOOD, pad=0.5)
        self.stack(head, [box], top=0.8)

        n = self.narrate(
            id="rule_box_01",
            text="Here is the rule box. Net turns: rights minus lefts, modulo four.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "box")
        self.play(FadeIn(box[0]))
        self.at_word(n, "minus")
        self.play(FadeIn(lines[0], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="rule_box_02",
            text="Cancel opposite legs first.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Cancel")
        self.play(FadeIn(lines[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="rule_box_03",
            text="Know the triples.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "triples")
        self.play(FadeIn(lines[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="rule_box_04",
            text="Equal nets give the side times root two.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "root")
        self.play(FadeIn(lines[3], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="rule_box_05",
            text="Facing south, left is east.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "south")
        self.play(FadeIn(lines[4], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="rule_box_06",
            text="And a rename is one rotation for all.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "rotation")
        self.play(FadeIn(lines[5], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S07_rule_box")

    # ============================================== 8. WHEN IT FAILS ==========

    def when_it_fails(self):
        self.scene_start("S08_when_it_fails", title="When It Fails")

        head = self.heading("When it fails", BAD)
        blocks = two_line_blocks(FAILS, BAD)
        self.stack(head, list(blocks), buff=0.7, top=0.9, align=LEFT)

        n = self.narrate(
            id="when_it_fails_01",
            text="When do the shortcuts fail? Cancelling works for paths along north, south, east and west. A forty-five "
                 "degree leg needs splitting into components, or a drawing.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "fail")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "Cancelling")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "splitting")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="when_it_fails_02",
            text="Net turns work for ninety degree turns only; mix in forty-five or one hundred and thirty-five degree "
                 "turns, and you must add angles instead.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "only")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "angles")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="when_it_fails_03",
            text="And if the nets are not a triple, give the answer as a root, or check the options for the nearest value.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "triple")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "root")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S08_when_it_fails")

    # ============================================== 9. TRAPS AND CONFUSING QUESTIONS ==========

    def trap(self):
        self.scene_start("S09_trap", title="Traps and Confusing Questions")

        head, ask, wrong, right, rule = self.show_trap(TRAPS[0])

        n = self.narrate(
            id="trap_01",
            text="The trap: cancelling legs before fixing their directions.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "before")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="trap_02",
            text="Facing north, walk four kilometres, turn right and walk six, turn right and walk four, turn left and "
                 "walk two.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "north")
        self.play(FadeIn(ask, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="trap_03",
            text="The wrong instinct: listing the last leg as west, because it says left.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "instinct")
        self.play(FadeIn(wrong, shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="trap_04",
            text="Correct: after two rights you face south, and left from south is east. The net is eight kilometres east.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "south")
        self.play(FadeIn(right, shift=RIGHT * 0.2))
        self.at_word(n, "net")
        self.play(Indicate(right, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="trap_05",
            text="The rule: fix each leg's direction from the current facing, then cancel.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "fix")
        self.play(FadeIn(rule, scale=1.03))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S09_trap")

    # ============================================== 10. TIMED DRILLS ==========

    def timed_drills(self):
        self.scene_start("S10_timed_drills", title="Timed Drills")

        head = self.heading("Timed drill 1  ·  6 seconds")
        ask, work, answer = self.drill(head, "Facing west:  right, right, right, left, left.   Final facing?", "net +1 right:    west + 90°", "north")

        n = self.narrate(
            id="timed_drills_01",
            text="Drill one: facing west, turn right, right, right, left, left; what is the final facing? Six seconds.",
            voice="default",
            subtitle=True,
            pause_after=6.0,
        )
        self.at_word(n, "one")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "facing")
        self.play(FadeIn(ask, scale=1.03))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="timed_drills_02",
            text="The net is one right, and west plus ninety degrees is north.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "net")
        self.play(FadeIn(work, shift=UP * 0.1))
        self.at_word(n, "plus")
        self.play(FadeIn(answer, scale=1.03))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Timed drill 2  ·  6 seconds")
        ask, work, answer = self.drill(head, "8 km north, then 6 km west.   Distance and direction?", "the 6-8-10 triple", "10 km north-west")

        n = self.narrate(
            id="timed_drills_03",
            text="Drill two: eight kilometres north, then six kilometres west; what are the distance and the direction? "
                 "Six seconds.",
            voice="default",
            subtitle=True,
            pause_after=6.0,
        )
        self.at_word(n, "two")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "north")
        self.play(FadeIn(ask, scale=1.03))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="timed_drills_04",
            text="It is the six, eight, ten triple: ten kilometres, north-west.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "triple")
        self.play(FadeIn(work, shift=UP * 0.1))
        self.at_word(n, "kilometres")
        self.play(FadeIn(answer, scale=1.03))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Timed drill 3  ·  6 seconds")
        ask, work, answer = self.drill(head, "5 km east,  3 north,  2 west,  3 south,  1 west.   Distance from the start?", "east  5 − 2 − 1        north  3 − 3", "2 km east")

        n = self.narrate(
            id="timed_drills_05",
            text="Drill three: five kilometres east, three north, two west, three south, one west; what is the distance "
                 "from the start? Six seconds.",
            voice="default",
            subtitle=True,
            pause_after=6.0,
        )
        self.at_word(n, "three")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "east")
        self.play(FadeIn(ask, scale=1.03))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="timed_drills_06",
            text="East is five minus two minus one, and north cancels: two kilometres east.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "minus")
        self.play(FadeIn(work, shift=UP * 0.1))
        self.at_word(n, "cancels")
        self.play(FadeIn(answer, scale=1.03))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Timed drill 4  ·  6 seconds")
        ask, work, answer = self.drill(head, "Evening, facing north.   Which side does your shadow fall on?", "the shadow is east;   facing north, east is on the", "right")

        n = self.narrate(
            id="timed_drills_07",
            text="Drill four: it is evening, and you face north; which side does your shadow fall on? Six seconds.",
            voice="default",
            subtitle=True,
            pause_after=6.0,
        )
        self.at_word(n, "four")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "evening")
        self.play(FadeIn(ask, scale=1.03))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="timed_drills_08",
            text="The shadow falls east, and facing north, east is on the right.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "falls")
        self.play(FadeIn(work, shift=UP * 0.1))
        self.at_word(n, "right")
        self.play(FadeIn(answer, scale=1.03))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Timed drill 5  ·  5 seconds")
        ask, work, answer = self.drill(head, "If south is called north, what is east called?", "rotation 180°", "west")

        n = self.narrate(
            id="timed_drills_09",
            text="Drill five: if south is called north, what is east called? Five seconds.",
            voice="default",
            subtitle=True,
            pause_after=5.0,
        )
        self.at_word(n, "five")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "called")
        self.play(FadeIn(ask, scale=1.03))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="timed_drills_10",
            text="The rotation is one hundred and eighty degrees, so east is called west.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "rotation")
        self.play(FadeIn(work, shift=UP * 0.1))
        self.at_word(n, "so")
        self.play(FadeIn(answer, scale=1.03))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S10_timed_drills")

    # ============================================== 11. QUICK REVISION ==========

    def quick_revision(self):
        self.scene_start("S11_quick_revision", title="Quick Revision")

        head = self.heading("Quick revision")
        uses = VGroup(pill("count net turns", WORD, size=LABEL), pill("cancel opposite legs", RATIO, size=LABEL), pill("recognise triples and diagonals", FOCUS, size=LABEL),
                      pill("remember the south mirror", SECOND, size=LABEL), pill("rename with one rotation", GOOD, size=LABEL))
        uses.arrange_in_grid(cols=3, buff=(0.4, 0.4))
        box = VGroup(pill("net turns", GOOD, size=SMALL), pill("cancel", GOOD, size=SMALL), pill("triples", GOOD, size=SMALL), pill("side × √2", GOOD, size=SMALL),
                     pill("south mirror", GOOD, size=SMALL), pill("one rotation", GOOD, size=SMALL)).arrange(RIGHT, buff=0.3)
        nxt = self.breadcrumb("Next", "Lesson 3 Cheat Sheet", "Assignment · Home Task · Final Quiz")
        self.stack(head, [uses, box, nxt], buff=0.9, top=0.9)
        self.no_overlap(*uses)
        self.no_overlap(*box)

        n = self.narrate(
            id="quick_revision_01",
            text="Count net turns, cancel opposite legs, recognise triples and diagonals, remember the south mirror, and "
                 "rename with one rotation.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "Count")
        self.play(FadeIn(uses[0], shift=UP * 0.1))
        self.at_word(n, "cancel")
        self.play(FadeIn(uses[1], shift=UP * 0.1))
        self.at_word(n, "recognise")
        self.play(FadeIn(uses[2], shift=UP * 0.1))
        self.at_word(n, "remember")
        self.play(FadeIn(uses[3], shift=UP * 0.1))
        self.at_word(n, "rename")
        self.play(FadeIn(uses[4], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="quick_revision_02",
            text="That is the whole rule box in one line.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "line")
        self.play(FadeIn(box, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="quick_revision_03",
            text="Next: the lesson three cheat sheet, then the assignment, the home task and the final quiz.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Next")
        self.play(FadeIn(nxt, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S11_quick_revision")

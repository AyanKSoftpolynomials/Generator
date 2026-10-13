"""
animation.py for the LMS video generator.

Course : Pre-C-CAT - Section A - Logical Reasoning
Video  : 00 - Module Introduction - Why Logical Reasoning

Source script:
  C:\\Scripts\\Section A\\Reasoning_Scripts\\Sessions 1-4 - Coding-Decoding, Alphabets, Directions, Number Series, Odd Man Out\\00 - Module Introduction - Why Logical Reasoning.pdf

Built on the golden-reference pattern:
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``;
  * layouts stacked with next_to and guarded with ``no_overlap``; nothing is
    ever animated onto or into another box.

Module opener (about 4 minutes). It opens with a silent breadcrumb and one welcome line, then follows the script section by section:
hook, what logical reasoning is, why it is needed, what a question tests, C-CAT at a glance, the method, a checkpoint, the summary.
Pauses: 3 seconds on the hook question, 10 seconds on the checkpoint.
Checked in the data block: the checkpoint series by both methods, and that a blind guess among four options is worth zero on average.
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

# ---- checkpoint: 2, 6, 12, 20, 30, ? ----
SERIES = [2, 6, 12, 20, 30]
SERIES_GAPS = [b - a for a, b in zip(SERIES, SERIES[1:])] + [12]
assert SERIES_GAPS == [4, 6, 8, 10, 12] and SERIES[-1] + 12 == 42
assert SERIES == [n * (n + 1) for n in range(1, 6)] and 6 * 7 == 42
# ---- C-CAT marking: a blind guess among four options ----
assert Fraction(1, 4) * 3 + Fraction(3, 4) * (-1) == 0

NEEDED = [("It is how problems get solved", "debugging is reasoning:  form a hypothesis, test it, reject what the evidence does not support"),
          ("It is fair to everyone", "no syllabus knowledge gives an advantage;  only clear thinking does"),
          ("It scores fast", "most questions are one step:  a trained eye solves them in under a minute")]
ABILITIES = [("Pattern spotting", "Finding the rule in a series or a code"),
             ("Spatial tracking", "Following turns and distances on a map"),
             ("Relation mapping", "Turning “my father's only son” into a tree"),
             ("Deduction", "Accepting only what must be true"),
             ("Arrangement", "Placing people from clues"),
             ("Judgement", "Knowing when the data is enough")]


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


class WhyLogicalReasoningVideo(LMSScene):
    lesson_title = "Why Logical Reasoning?"

    def construct(self):
        self.camera.background_color = BG

        self.intro()
        self.hook()
        self.what_is_it()
        self.why_needed()
        self.what_it_tests()
        self.ccat_at_a_glance()
        self.method()
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

    def step_rows(self, items, color=WORD):
        """Numbered concept steps.  Each row = (number chip, the step[, a short note in green])."""
        rows = VGroup()
        for i, (what, note) in enumerate(items):
            row = VGroup(pill(str(i + 1), color, size=SMALL), text(what, LABEL, INK, BOLD))
            if note:
                row.add(text(note, LABEL, GOOD, BOLD))
            rows.add(row.arrange(RIGHT, buff=0.35))
        return fit_width(rows.arrange(DOWN, buff=0.5, aligned_edge=LEFT), SAFE_W - 0.6)

    # ============================================== 0. INTRO ==========
    # Module opener: silent breadcrumb, one welcome line, the title.

    def intro(self):
        self.scene_start("S00_intro", title="Intro")

        crumb = self.breadcrumb("Logical Reasoning", "Module Introduction")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        title = text("Why Logical Reasoning?", TITLE, INK, BOLD)
        today = text("the module opener", LABEL, FOCUS)
        block = VGroup(title, today).arrange(DOWN, buff=0.7)
        block.next_to(crumb, DOWN, buff=1.6)
        self.no_overlap(crumb, title, today)
        self.validator.check_in_frame(VGroup(crumb, block))

        n = self.narrate(
            id="intro_01",
            text="Welcome to the Logical Reasoning module. This opening video answers one question: why logical reasoning?",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.at_word(n, "Welcome")
        self.play(FadeIn(title, shift=UP * 0.1))
        self.at_word(n, "opening")
        self.play(FadeIn(today, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_intro")

    # ============================================== 1. HOOK ==========

    def hook(self):
        self.scene_start("S01_hook", title="Hook")

        head = self.heading("A server dashboard")
        lines = VGroup(pill("All servers in Rack A are patched.", WORD, size=BODY),
                       pill("Some patched servers are slow.", RATIO, size=BODY)).arrange(DOWN, buff=0.4)
        ask = pill("So some Rack A servers are slow?", FOCUS, size=BODY)
        verdict = VGroup(pill("most people say yes", BAD, size=LABEL), pill("it does not follow", GOOD, size=LABEL)).arrange(RIGHT, buff=0.6)
        self.stack(head, [lines, ask, verdict], buff=0.75, top=0.8)
        self.no_overlap(*lines)
        self.no_overlap(*verdict)

        n = self.narrate(
            id="hook_01",
            text="Every server in Rack A is patched.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "patched")
        self.play(FadeIn(lines[0], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_02",
            text="Some patched servers are slow.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "slow")
        self.play(FadeIn(lines[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_03",
            text="So some servers in Rack A are slow. True?",
            voice="default",
            subtitle=True,
            pause_after=3.0,
        )
        self.at_word(n, "So")
        self.play(FadeIn(ask, scale=1.03))
        self.at_word(n, "True")
        self.play(Indicate(ask, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="hook_04",
            text="Most people say yes. It does not follow.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "yes")
        self.play(FadeIn(verdict[0], shift=UP * 0.1))
        self.at_word(n, "not")
        self.play(FadeIn(verdict[1], shift=UP * 0.1))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Why it does not follow")
        patched = Circle(radius=1.9, color=WORD, stroke_width=3, fill_color=WORD, fill_opacity=0.10)
        rack = Circle(radius=0.85, color=GOOD, stroke_width=3, fill_color=GOOD, fill_opacity=0.18).move_to(patched.get_center() + LEFT * 0.75)
        slow = Circle(radius=1.2, color=BAD, stroke_width=3, fill_color=BAD, fill_opacity=0.14).move_to(patched.get_center() + RIGHT * 2.2)
        names = VGroup(text("Patched", SMALL, WORD, BOLD).move_to(patched.get_center() + UP * 1.4),
                       text("Rack A", SMALL, GOOD, BOLD).move_to(rack),
                       text("Slow", SMALL, BAD, BOLD).move_to(slow.get_center() + RIGHT * 0.5))
        self.no_overlap(*names)
        diagram = VGroup(patched, rack, slow, names)
        notes = VGroup(text("the slow patched servers", LABEL, INK), text("could all be outside Rack A", LABEL, BAD, BOLD),
                       text("nothing given puts them inside", LABEL, MUTED)).arrange(DOWN, buff=0.35, aligned_edge=LEFT)
        row = VGroup(diagram, notes).arrange(RIGHT, buff=0.9)
        gap = pill("what feels true   vs   what is actually proven", FOCUS, size=LABEL)
        self.stack(head, [row, gap], buff=0.6, top=0.6)
        self.no_overlap(diagram, notes)

        n = self.narrate(
            id="hook_05",
            text="Rack A sits inside the patched servers.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Rack")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "inside")
        self.play(FadeIn(patched), FadeIn(names[0], shift=UP * 0.1), FadeIn(rack, shift=UP * 0.1), FadeIn(names[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_06",
            text="The slow patched servers could all be outside Rack A.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "slow")
        self.play(FadeIn(slow), FadeIn(names[2], shift=UP * 0.1))
        self.at_word(n, "could")
        self.play(FadeIn(notes[0], shift=RIGHT * 0.2))
        self.at_word(n, "outside")
        self.play(FadeIn(notes[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_07",
            text="Nothing in the two statements puts them inside it.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Nothing")
        self.play(FadeIn(notes[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_08",
            text="That gap, between what feels true and what is actually proven, is what this module trains.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "gap")
        self.play(FadeIn(gap, scale=1.03))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S01_hook")

    # ============================================== 2. WHAT IS LOGICAL REASONING ==========

    def what_is_it(self):
        self.scene_start("S02_what_is_it", title="What Is Logical Reasoning")

        head = self.heading("What is logical reasoning?")
        core = pill("drawing conclusions only from the information given", FOCUS, size=BODY)
        parts = VGroup(pill("find the rule behind a pattern", WORD, size=LABEL), pill("map a structure", RATIO, size=LABEL),
                       pill("check the answer in every case", GOOD, size=LABEL)).arrange(RIGHT, buff=0.4)
        needs = VGroup(text("almost no formulas", BODY, MUTED), text("it needs a method", BODY, GOOD, BOLD)).arrange(RIGHT, buff=0.9)
        self.stack(head, [core, parts, needs], buff=0.9, top=1.0)
        self.no_overlap(*parts)
        self.no_overlap(*needs)

        n = self.narrate(
            id="what_is_it_01",
            text="Logical reasoning is drawing conclusions only from the information given: finding the rule behind a "
                 "pattern, mapping a structure, and checking that the answer holds in every case.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "only")
        self.play(FadeIn(core, scale=1.03))
        self.at_word(n, "rule")
        self.play(FadeIn(parts[0], shift=UP * 0.1))
        self.at_word(n, "mapping")
        self.play(FadeIn(parts[1], shift=UP * 0.1))
        self.at_word(n, "checking")
        self.play(FadeIn(parts[2], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="what_is_it_02",
            text="It needs almost no formulas. It needs a method.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "formulas")
        self.play(FadeIn(needs[0], shift=UP * 0.1))
        self.at_word(n, "method")
        self.play(FadeIn(needs[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_what_is_it")

    # ============================================== 3. WHY IS IT NEEDED ==========

    def why_needed(self):
        self.scene_start("S03_why_needed", title="Why Is It Needed")

        head = self.heading("Why is it needed?")
        blocks = two_line_blocks(NEEDED, WORD)
        exams = VGroup(pill("C-CAT", FOCUS, size=SMALL), pill("placement tests", WORD, size=SMALL), pill("bank and government exams", RATIO, size=SMALL),
                       pill("management entrance tests", GOOD, size=SMALL)).arrange(RIGHT, buff=0.3)
        self.stack(head, list(blocks) + [exams], buff=0.5, top=0.6, align=LEFT)
        self.no_overlap(*exams)

        n = self.narrate(
            id="why_needed_01",
            text="One: it is how problems get solved. Debugging is reasoning: form a hypothesis, test it against the "
                 "evidence, and reject what the evidence does not support.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "solved")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "Debugging")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="why_needed_02",
            text="Two: it is fair to everyone. No syllabus knowledge gives an advantage; only clear thinking does.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "fair")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "syllabus")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="why_needed_03",
            text="Three: it scores fast. Most questions are one step, and a trained eye solves them in under a minute.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "fast")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "trained")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="why_needed_04",
            text="It appears in C-CAT, placement tests, bank and government exams, and management entrance tests.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "appears")
        self.play(FadeIn(exams[0], shift=UP * 0.1))
        self.at_word(n, "placement")
        self.play(FadeIn(exams[1], shift=UP * 0.1))
        self.at_word(n, "bank")
        self.play(FadeIn(exams[2], shift=UP * 0.1))
        self.at_word(n, "management")
        self.play(FadeIn(exams[3], shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_why_needed")

    # ============================================== 4. WHAT A REASONING QUESTION TESTS ==========

    def what_it_tests(self):
        self.scene_start("S04_what_it_tests", title="What a Reasoning Question Tests")

        head = self.heading("What a reasoning question tests")
        table, rows = self.placed_table(head, ["Ability", "What it looks like"], [list(a) for a in ABILITIES], [4.0, 8.6], size=LABEL, room=1.2)
        for row in rows:
            row[0].set_color(WORD)

        n = self.narrate(
            id="what_it_tests_01",
            text="A reasoning question tests six abilities.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "six")
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.wait_for_narration(n)

        n = self.narrate(
            id="what_it_tests_02",
            text="Pattern spotting: finding the rule in a series or a code.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "spotting")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="what_it_tests_03",
            text="Spatial tracking: following turns and distances on a map.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "tracking")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="what_it_tests_04",
            text="Relation mapping: turning a phrase like, my father's only son, into a tree.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Relation")
        self.play(FadeIn(rows[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="what_it_tests_05",
            text="Deduction: accepting only what must be true.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Deduction")
        self.play(FadeIn(rows[3], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="what_it_tests_06",
            text="Arrangement: placing people from clues.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Arrangement")
        self.play(FadeIn(rows[4], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="what_it_tests_07",
            text="And judgement: knowing when the data is enough.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "judgement")
        self.play(FadeIn(rows[5], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_what_it_tests")

    # ============================================== 5. C-CAT AT A GLANCE ==========

    def ccat_at_a_glance(self):
        self.scene_start("S05_ccat_at_a_glance", title="C-CAT at a Glance")

        head = self.heading("C-CAT at a glance  ·  Section A")
        paper = VGroup(pill("50 questions", WORD, size=BODY), pill("60 minutes", WORD, size=BODY), pill("+3 correct", GOOD, size=BODY),
                       pill("−1 wrong", BAD, size=BODY)).arrange(RIGHT, buff=0.4)
        share = VGroup(pill("reasoning  ≈  15 of the 50", RATIO, size=LABEL), text("from third-party analyses of recent papers", SMALL, MUTED))\
            .arrange(RIGHT, buff=0.4)
        guess = VGroup(text("a blind guess:   ¼ × (+3)  +  ¾ × (−1)  =  0", LABEL, INK), pill("eliminate options before you guess", FOCUS, size=LABEL))\
            .arrange(DOWN, buff=0.4)
        self.stack(head, [paper, share, guess], buff=0.85, top=0.9)
        self.no_overlap(*paper)
        self.no_overlap(*share)

        n = self.narrate(
            id="ccat_at_a_glance_01",
            text="Section A has fifty questions in sixty minutes, with plus three for a correct answer and minus one for a "
                 "wrong one.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "fifty")
        self.play(FadeIn(paper[0], shift=UP * 0.1))
        self.at_word(n, "sixty")
        self.play(FadeIn(paper[1], shift=UP * 0.1))
        self.at_word(n, "plus")
        self.play(FadeIn(paper[2], shift=UP * 0.1))
        self.at_word(n, "minus")
        self.play(FadeIn(paper[3], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="ccat_at_a_glance_02",
            text="Third-party analyses of recent papers put reasoning at about fifteen of the fifty questions.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "analyses")
        self.play(FadeIn(share[1]))
        self.at_word(n, "about")
        self.play(FadeIn(share[0], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="ccat_at_a_glance_03",
            text="A blind guess is worth zero on average, so eliminate options before you guess.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "zero")
        self.play(FadeIn(guess[0], shift=UP * 0.1))
        self.at_word(n, "eliminate")
        self.play(FadeIn(guess[1], scale=1.03))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_ccat_at_a_glance")

    # ============================================== 6. THE METHOD - SPOT, STRUCTURE, SOLVE, VERIFY ==========

    def method(self):
        self.scene_start("S06_method", title="The Method - Spot, Structure, Solve, Verify")

        head = self.heading("The method")
        route = VGroup(pill("SPOT", WORD, size=BODY), text("→", BODY, MUTED), pill("STRUCTURE", RATIO, size=BODY), text("→", BODY, MUTED),
                       pill("SOLVE", FOCUS, size=BODY), text("→", BODY, MUTED), pill("VERIFY", GOOD, size=BODY)).arrange(RIGHT, buff=0.3)
        does = VGroup(text("spot the question type", LABEL, WORD), text("draw its structure:  a tree, a map, a grid or a diagram", LABEL, RATIO),
                      text("solve from the structure", LABEL, FOCUS), text("verify the answer against every clue", LABEL, GOOD))\
            .arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        rule = pill("Use only what is given.  If a conclusion needs an assumption, it does not follow.", BAD, size=LABEL)
        self.stack(head, [route, does, rule], buff=0.7, top=0.7)
        self.no_overlap(*route)
        self.no_overlap(*does)

        n = self.narrate(
            id="method_01",
            text="The method has four steps: spot, structure, solve, verify.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "four")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "spot")
        self.play(FadeIn(route[0], shift=UP * 0.1))
        self.at_word(n, "structure")
        self.play(FadeIn(route[1:3], shift=UP * 0.1))
        self.at_word(n, "solve")
        self.play(FadeIn(route[3:5], shift=UP * 0.1))
        self.at_word(n, "verify")
        self.play(FadeIn(route[5:], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="method_02",
            text="Spot the question type, draw its structure, which may be a tree, a map, a grid or a diagram, solve from "
                 "the structure, and verify the answer against every clue.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "type")
        self.play(FadeIn(does[0], shift=RIGHT * 0.2))
        self.at_word(n, "draw")
        self.play(FadeIn(does[1], shift=RIGHT * 0.2))
        self.at_word(n, "from")
        self.play(FadeIn(does[2], shift=RIGHT * 0.2))
        self.at_word(n, "against")
        self.play(FadeIn(does[3], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="method_03",
            text="Use only what is given. If a conclusion needs an assumption, it does not follow.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "only")
        self.play(FadeIn(rule, scale=1.03))
        self.at_word(n, "assumption")
        self.play(Indicate(rule, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_method")

    # ============================================== 7. CHECKPOINT ==========

    def checkpoint(self):
        self.scene_start("S07_checkpoint", title="Checkpoint")

        head = self.heading("Checkpoint  ·  what comes next?")
        terms = VGroup(*[pill(str(t), WORD, size=BODY) for t in SERIES], pill("?", FOCUS, size=BODY)).arrange(RIGHT, buff=0.9)
        gaps = VGroup(*[text(f"+{g}", LABEL, DIFF if i < 4 else FOCUS, BOLD) for i, g in enumerate(SERIES_GAPS)])
        for i, gap in enumerate(gaps):
            gap.move_to((terms[i].get_center() + terms[i + 1].get_center()) / 2 + DOWN * 0.8)
        ladder = VGroup(terms, gaps)
        answer = pill("30 + 12  =  42", GOOD, size=BODY)
        second = VGroup(text("verify:   each term is  n × (n + 1)", LABEL, MUTED),
                        text("1×2,   2×3,   3×4,   4×5,   5×6,   then   6×7  =  42", LABEL, INK, BOLD)).arrange(DOWN, buff=0.25)
        both = pill("two methods, one answer", FOCUS, size=LABEL)
        self.stack(head, [ladder, answer, second, both], buff=0.55, top=0.7)
        self.no_overlap(*terms)
        self.no_overlap(terms, gaps)

        n = self.narrate(
            id="checkpoint_01",
            text="What comes next: two, six, twelve, twenty, thirty?",
            voice="default",
            subtitle=True,
            pause_after=10.0,
        )
        self.at_word(n, "next")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "two")
        self.play(FadeIn(terms, shift=UP * 0.1))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="checkpoint_02",
            text="The gaps are four, six, eight and ten, so the next gap is twelve: the answer is forty-two.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "gaps")
        self.play(FadeIn(gaps[:4], shift=UP * 0.1))
        self.at_word(n, "next")
        self.play(FadeIn(gaps[4], scale=1.03))
        self.at_word(n, "answer")
        self.play(FadeIn(answer, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="checkpoint_03",
            text="Verify a second way. Each term is n times n plus one: one times two, two times three, up to five times "
                 "six, so the next is six times seven: forty-two.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "second")
        self.play(FadeIn(second[0], shift=UP * 0.1))
        self.at_word(n, "times")
        self.play(FadeIn(second[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="checkpoint_04",
            text="Two methods, one answer.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "methods")
        self.play(FadeIn(both, scale=1.03))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S07_checkpoint")

    # ============================================== 8. SUMMARY ==========

    def summary(self):
        self.scene_start("S08_summary", title="Summary")

        head = self.heading("Summary")
        route = VGroup(pill("spot the type", WORD, size=LABEL), pill("draw the structure", RATIO, size=LABEL), pill("solve", FOCUS, size=LABEL),
                       pill("verify against every clue", GOOD, size=LABEL)).arrange(RIGHT, buff=0.35)
        trust = text("Trust the structure, not the first impression.", BODY, INK, BOLD)
        nxt = self.breadcrumb("Next", "Lesson 1 Qualifying Quiz")
        skip = text("33 or more out of 36:  you may skip the Coding & Decoding videos", LABEL, MUTED)
        self.stack(head, [route, trust, nxt, skip], buff=0.75, top=0.9)
        self.no_overlap(*route)

        n = self.narrate(
            id="summary_01",
            text="Reasoning is disciplined thinking: spot the type, draw the structure, solve, then verify against every "
                 "clue.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "spot")
        self.play(FadeIn(route[0], shift=UP * 0.1))
        self.at_word(n, "draw")
        self.play(FadeIn(route[1], shift=UP * 0.1))
        self.at_word(n, "solve")
        self.play(FadeIn(route[2], shift=UP * 0.1))
        self.at_word(n, "verify")
        self.play(FadeIn(route[3], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_02",
            text="Trust the structure, not the first impression.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Trust")
        self.play(FadeIn(trust, scale=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_03",
            text="Next: the lesson one qualifying quiz. Score thirty-three or more out of thirty-six, and you may skip the "
                 "coding and decoding videos.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Next")
        self.play(FadeIn(nxt, shift=UP * 0.1))
        self.at_word(n, "Score")
        self.play(FadeIn(skip, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S08_summary")

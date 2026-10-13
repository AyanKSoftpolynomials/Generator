"""
animation.py for the LMS video generator.

Course : Pre-C-CAT - Section A - Logical Reasoning
Video  : Lesson 2 - Alphabets - 02 - Positions from Both Ends

Source script:
  C:\\Scripts\\Section A\\Reasoning_Scripts\\Sessions 1-4 - Coding-Decoding, Alphabets, Directions, Number Series, Odd Man Out\\Lesson 2 - Alphabets\\02 - Positions from Both Ends.pdf

Built on the golden-reference pattern:
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``;
  * layouts stacked with next_to and guarded with ``no_overlap``; nothing is
    ever animated onto or into another box.

Lesson 2, Video 1 of 6 (file 02 in its folder; file 01 is the Pre-Lesson Brief, which is reading material).
First video of the lesson: a silent breadcrumb, "Now we start lesson two", a one-line recap of Lesson 1, then today's topic.
The narration follows the script section by section and ends with the Section Quiz and its answer key.
Every position and answer in the script was recomputed in the data block; all of them are correct.
Pauses: 3 seconds on the hook question, 10 seconds on the checkpoint, 12 seconds on each practice and quiz screen.
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

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
THINNED = ALPHABET[::2]                                   # every second letter dropped: A C E ... Y
HALF_REVERSED = ALPHABET[:13][::-1] + ALPHABET[13:]    # first half reversed: M L ... A N ... Z
BACKWARDS = ALPHABET[::-1]


def letter_pos(ch):
    return ALPHABET.index(ch) + 1


def from_left(k, order=ALPHABET):
    return order[k - 1]


def from_right(k, order=ALPHABET):
    return order[len(order) - k]


def between(a, b):
    return abs(letter_pos(a) - letter_pos(b)) - 1


def midway(a, b):
    total = letter_pos(a) + letter_pos(b)
    assert total % 2 == 0
    return ALPHABET[total // 2 - 1]


# ---- hook and worked examples ----
assert from_right(10) == "Q" == from_left(27 - 10) and ALPHABET[::-1][:10] == "ZYXWVUTSRQ"
assert from_left(17 - 5) == "L" and letter_pos("Q") == 17
# ---- concept steps, exam patterns ----
assert between("D", "K") == 6 and ALPHABET[4:10] == "EFGHIJ" and midway("F", "P") == "K" and letter_pos("K") == 11
assert len(THINNED) == 13 and THINNED == "ACEGIKMOQSUWY" and from_right(5, THINNED) == "Q" == from_left(14 - 5, THINNED)
assert from_right(8) == "S" == from_left(19) and from_left(12 + 7) == "S"
assert HALF_REVERSED.startswith("MLKJIHGFEDCBAN") and from_left(9 + 4, HALF_REVERSED) == "A"
# ---- traps, checkpoint, practice ----
assert letter_pos(from_right(15)) == 12 and from_right(15) == "L" and from_left(12 + 8) == "T" and from_right(23) == "D"
assert letter_pos("V") == 22 and 27 - 22 == 5 and from_right(5) == "V"
assert from_left(5 + 8, BACKWARDS) == "N" and letter_pos("N") == 27 - 13 == 14
# ---- section quiz ----
assert from_right(11) == "P" and letter_pos("P") == 16 and letter_pos(from_right(9)) == 18 and from_left(18 + 4) == "V"
assert between("F", "S") == 12 and midway("H", "T") == "N" and from_right(6, BACKWARDS) == "F" and from_right(4, THINNED) == "S"

OBJECTIVES = [("Convert any position from the right", "into a position from the left"),
              ("Solve “kth to the right / left of the nth letter from …”", "in one line"),
              ("Find the midpoint of two letters", "and count the letters between them")]
FORMULAS = ["From the right  =  27 − from the left",
            "kth to the right of position n  =  n + k;        kth to the left  =  n − k",
            "Letters between a and b  =  |a − b| − 1",
            "Midpoint  =  (a + b) / 2",
            "Changed alphabet:   write the new order first",
            "Shorter alphabet of n letters:   kth from the right  =  (n + 1 − k)th from the left"]
PATTERNS = [("From the right", "8th from the right", "27 − 8 = 19", "S"),
            ("Right of a left position", "7th to the right of the 12th from the left", "12 + 7", "S"),
            ("Left of a right position", "5th to the left of the 10th from the right", "17 − 5", "L"),
            ("Letters between", "D and K", "11 − 4 − 1", "6"),
            ("Midpoint", "midway between F and P", "(6 + 16) / 2", "K"),
            ("Changed alphabet", "first half reversed;  4th right of the 9th from left", "new order:  M … A,  N … Z", "A"),
            ("Every second letter dropped", "5th from the right", "A, C, E … Y (13 letters);  14 − 5 = 9th", "Q")]
TRAPS = [("Trap 1  ·  moving before converting", "Which letter is 8th to the right of the 15th letter from the right?",
          "15 + 8 = 23rd from the right:  D", "15th from right = 12;   12 + 8 = 20:  T",
          "convert to a left position first, then move:  right means add, left means subtract"),
         ("Trap 2  ·  counting the end letters as “between”", "How many letters are there between D and K?",
          "11 − 4  =  7", "E, F, G, H, I, J:   6",
          "between means excluding both ends:  difference − 1")]
PRACTICE_A = [("L1", "Which letter is 8th from the right?"),
              ("L1", "What is the position of V from the right?"),
              ("L1", "How many letters are there between D and K?"),
              ("L2", "Which letter is 7th to the right of the 12th letter from the left?"),
              ("L2", "Which letter is 5th to the left of the 10th letter from the right?"),
              ("L2", "Which letter is midway between F and P?")]
PRACTICE_B = [("L3", "If the alphabet is written in reverse order, which letter is 8th to the right of the 5th letter from the left?"),
              ("L3", "If the first half of the alphabet is reversed, which letter is 4th to the right of the 9th letter from the left?"),
              ("L3", "If every second letter of the alphabet (B, D, F …) is dropped, which letter is 5th from the right?")]
ANSWERS_A = [("27 − 8  =  19", "S"),
             ("V = 22;    27 − 22", "5"),
             ("11 − 4 − 1", "6"),
             ("12 + 7  =  19", "S"),
             ("10th from the right = 17;    17 − 5  =  12", "L")]
ANSWERS_B = [("(6 + 16) / 2  =  11", "K"),
             ("reversed order Z, Y, X …:   position 5 + 8 = 13 holds the letter 27 − 13 = 14", "N"),
             ("new order M, L, K … B, A, N … Z:   position 9 + 4 = 13", "A"),
             ("remaining:  A C E G I K M O Q S U W Y;   9th from the left", "Q")]
LENS = [("Recognition cue", "“from the right”, “to the left of”, “between”, “midway”"),
        ("Target time", "10 seconds for one step,  20 seconds for two"),
        ("Sanity check", "a letter “from the right” near 1 must be near Z;  near 26, near A")]
QUIZ = [["Which letter is 11th from the right?", "(a) K   (b) O   (c) P   (d) Q"],
        ["Which letter is 4th to the right of the 9th letter from the right?", "(a) V   (b) N   (c) M   (d) U"],
        ["How many letters are there between F and S?", "(a) 13   (b) 14   (c) 11   (d) 12"],
        ["Which letter is midway between H and T?", "(a) M   (b) N   (c) O   (d) K"],
        ["If the alphabet is written in reverse order, which letter is 6th from the right?", "(a) U   (b) F   (c) T   (d) G"],
        ["If every second letter of the alphabet (B, D, F …) is dropped, which letter is 4th from the right?", "(a) W   (b) S   (c) U   (d) Q"]]
QUIZ_KEY = [("27 − 11  =  16", "(c)  P"),
            ("9th from the right = 18;    18 + 4  =  22", "(a)  V"),
            ("19 − 6 − 1", "(d)  12"),
            ("(8 + 20) / 2  =  14", "(b)  N"),
            ("in the reversed order the right end is A:   A, B, C, D, E, F", "(b)  F"),
            ("A C E … S U W Y;   from the right:  Y, W, U, S", "(b)  S")]


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


class PositionsFromBothEndsVideo(LMSScene):
    lesson_title = "Positions from Both Ends"

    def construct(self):
        self.camera.background_color = BG

        self.intro()
        self.hook()
        self.objectives()
        self.why_this_section()
        self.concept_journey()
        self.rule_box()
        self.short_trick()
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
        self.section_quiz()

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

    def letter_row(self, letters, gap=0.5):
        """Letters in one row with the position (1, 2, 3 ...) under each.  row[i] = (letter, position)."""
        cells = VGroup()
        for i, ch in enumerate(letters):
            x = RIGHT * (i - (len(letters) - 1) / 2) * gap
            cells.add(VGroup(text(ch, LABEL, INK, BOLD).move_to(x + UP * 0.28), text(str(i + 1), MIN_FONT, MUTED).move_to(x + DOWN * 0.28)))
        self.no_overlap(*cells, gap=0.02)
        return cells

    def building(self, floors=26, floor=17, height=4.4, width=1.5):
        """A building of ``floors`` floors with one floor marked, counted from the ground and from the roof.
        Returns (frame, floor lines, marked floor, ground count, roof count)."""
        step = height / floors
        frame = Rectangle(width=width, height=height, color=MUTED, stroke_width=2.5)
        lines = VGroup(*[Line(LEFT * width / 2, RIGHT * width / 2, color=MUTED, stroke_width=1).shift(UP * (-height / 2 + k * step))
                         for k in range(1, floors)])
        level = -height / 2 + (floor - 0.5) * step
        mark = Line(LEFT * (width / 2 - 0.04), RIGHT * (width / 2 - 0.04), color=FOCUS, stroke_width=13).shift(UP * level)
        up = Arrow(LEFT * (width / 2 + 0.35) + DOWN * height / 2, LEFT * (width / 2 + 0.35) + UP * level, color=WORD, buff=0, stroke_width=4)
        down = Arrow(RIGHT * (width / 2 + 0.35) + UP * height / 2, RIGHT * (width / 2 + 0.35) + UP * level, color=RATIO, buff=0, stroke_width=4)
        ground = VGroup(up, text(f"floor {floor}\nfrom the ground", SMALL, WORD, BOLD).next_to(up, LEFT, buff=0.25))
        roof = VGroup(down, text(f"floor {floors + 1 - floor}\nfrom the roof", SMALL, RATIO, BOLD).next_to(down, RIGHT, buff=0.25))
        return VGroup(frame, lines, mark, ground, roof)

    # ============================================== 0. INTRO ==========
    # First video of the lesson: silent breadcrumb, the lesson announcement, a recap of the previous lesson, then today's topic.

    def intro(self):
        self.scene_start("S00_intro", title="Intro")

        crumb = self.breadcrumb("Logical Reasoning", "Lesson 2 · Alphabets", "Video 1 of 6")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        lesson = pill("Lesson 2  ·  Alphabets", RATIO, size=LABEL)
        recap = VGroup(text("from Lesson 1  ·  Coding & Decoding", SMALL, MUTED),
                       fit_width(VGroup(pill("A = 1 … Z = 26,  anchors E J O T Y", WORD, size=LABEL), pill("opposite = 27 − position", GOOD, size=LABEL)).arrange(RIGHT, buff=0.4), SAFE_W - 0.6)).arrange(DOWN, buff=0.25)
        title = fit_width(text("Positions from Both Ends", TITLE, INK, BOLD), SAFE_W - 0.4)
        today = text("today: from the right, without counting", LABEL, FOCUS)
        block = VGroup(lesson, recap, title, today).arrange(DOWN, buff=0.55)
        fit_within(block, SAFE_W, SAFE_H - crumb.height - 0.9)
        block.next_to(crumb, DOWN, buff=0.6)
        self.no_overlap(crumb, lesson, recap, title, today)
        self.no_overlap(*recap[1])
        self.validator.check_in_frame(VGroup(crumb, block))

        n = self.narrate(
            id="intro_01",
            text="Now we start lesson two: alphabets.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.at_word(n, "two")
        self.play(FadeIn(lesson, scale=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="intro_02",
            text="In lesson one, coding and decoding, every letter had a position from one to twenty-six, and its opposite "
                 "was twenty-seven minus that position.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "position")
        self.play(FadeIn(recap[0]), FadeIn(recap[1][0], shift=UP * 0.1))
        self.at_word(n, "minus")
        self.play(FadeIn(recap[1][1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="intro_03",
            text="This first video covers positions from both ends: finding a letter from the right, without counting.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "covers")
        self.play(FadeIn(title, shift=UP * 0.1))
        self.at_word(n, "without")
        self.play(FadeIn(today, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_intro")

    # ============================================== 1. HOOK ==========

    def hook(self):
        self.scene_start("S01_hook", title="Hook")

        head = self.heading("Which letter is 10th from the right?")
        strip = self.letter_row(ALPHABET)
        lost = text("Z, Y, X …  and somewhere around S they lose count", LABEL, BAD, BOLD)
        need = text("no need to count at all:  one subtraction", LABEL, INK)
        calc = pill("27 − 10  =  17", FOCUS, size=BODY)
        answer = pill("the 17th letter:  Q", GOOD, size=BODY)
        result = VGroup(calc, answer).arrange(RIGHT, buff=0.6)
        self.stack(head, [strip, lost, need, result], buff=0.75, top=0.9)
        self.no_overlap(*result)

        n = self.narrate(
            id="hook_01",
            text="Quick: which letter is tenth from the right?",
            voice="default",
            subtitle=True,
            pause_after=3.0,
        )
        self.at_word(n, "Quick")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "letter")
        self.play(FadeIn(strip))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="hook_02",
            text="Most people start at Z and count backwards: Z, Y, X, and somewhere around S they lose count.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "count")
        self.play(LaggedStart(*[Indicate(strip[25 - i][0], color=BAD, scale_factor=1.4) for i in range(8)], lag_ratio=0.6))
        self.at_word(n, "lose")
        self.play(FadeIn(lost, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_03",
            text="There is no need to count at all. One subtraction gives the answer: twenty-seven minus ten is seventeen, "
                 "which is Q.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "need")
        self.play(FadeIn(need, shift=UP * 0.1))
        self.at_word(n, "minus")
        self.play(FadeIn(calc, shift=UP * 0.1))
        self.at_word(n, "which")
        self.play(strip[16].animate.set_color(FOCUS), FadeIn(answer, shift=UP * 0.1))
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
            text="One: convert any position from the right into a position from the left.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "convert")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "into")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="objectives_03",
            text="Two: solve questions such as, the k-th letter to the right or left of the n-th letter, in one line.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "solve")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "line")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="objectives_04",
            text="Three: find the midpoint of two letters, and count the letters between them.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "midpoint")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "count")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_objectives")

    # ============================================== 3. WHY THIS SECTION ==========

    def why_this_section(self):
        self.scene_start("S03_why_this_section", title="Why This Section")

        head = self.heading("Why this section")
        marks = pill("position questions:  near-guaranteed marks", GOOD, size=BODY)
        slips = pill("lost only to direction slips", BAD, size=LABEL)
        rule = text("one conversion rule removes the slip", BODY, FOCUS, BOLD)
        self.stack(head, [marks, slips, rule], buff=1.0, top=1.2)

        n = self.narrate(
            id="why_this_section_01",
            text="Position questions are near-guaranteed marks that are lost only to direction slips.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "marks")
        self.play(FadeIn(marks, scale=1.03))
        self.at_word(n, "slips")
        self.play(FadeIn(slips, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="why_this_section_02",
            text="One conversion rule removes the slip.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "conversion")
        self.play(FadeIn(rule, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_why_this_section")

    # ============================================== 4. THE CONCEPT JOURNEY ==========

    def concept_journey(self):
        self.scene_start("S04_concept_journey", title="The Concept Journey")

        head = self.heading("Steps 1 to 3  ·  convert first, then move")
        strip = self.letter_row(ALPHABET)
        rule = pill("from the right  =  27 − from the left", FOCUS, size=LABEL)
        adds = text("the two always add to 27  ·  the same rule as opposite letters", SMALL, MUTED)
        first = pill("convert every “from the right” into a left position first", RATIO, size=LABEL)
        left = VGroup(Arrow(RIGHT * 1.3, LEFT * 1.3, color=BAD, buff=0, stroke_width=5), text("to the left of  =  subtract", LABEL, BAD, BOLD))\
            .arrange(DOWN, buff=0.15)
        right = VGroup(Arrow(LEFT * 1.3, RIGHT * 1.3, color=GOOD, buff=0, stroke_width=5), text("to the right of  =  add", LABEL, GOOD, BOLD))\
            .arrange(DOWN, buff=0.15)
        moves = VGroup(left, right).arrange(RIGHT, buff=1.5)
        self.stack(head, [strip, rule, adds, first, moves], buff=0.45, top=0.5)
        self.no_overlap(left, right)

        n = self.narrate(
            id="concept_journey_01",
            text="Step one: from the right. The position from the right is twenty-seven minus the position from the left.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "one")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "right")
        self.play(FadeIn(strip))
        self.at_word(n, "minus")
        self.play(FadeIn(rule, scale=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_journey_02",
            text="The two always add to twenty-seven, the same rule as opposite letters.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "add")
        self.play(FadeIn(adds, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_journey_03",
            text="Step two: convert first. Turn every, from the right, into a left position before doing anything else.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "two")
        self.play(Indicate(head, color=FOCUS, scale_factor=1.03))
        self.at_word(n, "Turn")
        self.play(FadeIn(first, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_journey_04",
            text="Step three: then move. To the right of means add; to the left of means subtract.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "three")
        self.play(Indicate(head, color=FOCUS, scale_factor=1.03))
        self.at_word(n, "add")
        self.play(FadeIn(right, shift=RIGHT * 0.2))
        self.at_word(n, "subtract")
        self.play(FadeIn(left, shift=LEFT * 0.1))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Steps 4 and 5  ·  letters between, midpoint")
        strip = self.letter_row(ALPHABET)
        gap = VGroup(pill("letters between a and b  =  |a − b| − 1", FOCUS, size=LABEL), text("D (4) and K (11):    11 − 4 − 1  =  6", LABEL, GOOD, BOLD))\
            .arrange(RIGHT, buff=0.6)
        mid = VGroup(pill("midpoint  =  (a + b) / 2", RATIO, size=LABEL), text("F (6) and P (16):    22 / 2  =  11  =  K", LABEL, GOOD, BOLD))\
            .arrange(RIGHT, buff=0.6)
        whole = text("only when that is a whole number", SMALL, MUTED)
        self.stack(head, [strip, gap, mid, whole], buff=0.75, top=0.8)
        self.no_overlap(*gap)
        self.no_overlap(*mid)

        n = self.narrate(
            id="concept_journey_05",
            text="Step four: letters between. Between positions a and b there are the difference, minus one, letters.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "four")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "between")
        self.play(FadeIn(strip))
        self.at_word(n, "minus")
        self.play(FadeIn(gap[0], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_journey_06",
            text="Between D, at four, and K, at eleven, there are six.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Between")
        self.play(VGroup(strip[3], strip[10]).animate.set_color(FOCUS))
        self.at_word(n, "six")
        self.play(strip[4:10].animate.set_color(GOOD), FadeIn(gap[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_journey_07",
            text="Step five: the midpoint. The letter midway between a and b is at a plus b, divided by two, when that is "
                 "a whole number.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "five")
        self.play(Indicate(head, color=FOCUS, scale_factor=1.03))
        self.at_word(n, "divided")
        self.play(FadeIn(mid[0], shift=UP * 0.1))
        self.at_word(n, "whole")
        self.play(FadeIn(whole, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_journey_08",
            text="Midway between F and P is position eleven, which is K.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Midway")
        self.play(VGroup(strip[5], strip[15]).animate.set_color(RATIO))
        self.at_word(n, "which")
        self.play(FadeIn(mid[1], shift=UP * 0.1), Indicate(strip[10], color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Steps 6 and 7  ·  modified and thinned alphabets")
        changed = VGroup(pill("reversed or partly reversed alphabet", WORD, size=LABEL), text("write the new order first, then count in it", LABEL, INK, BOLD))\
            .arrange(RIGHT, buff=0.5)
        dropped = pill("every second letter dropped:  13 letters remain", RATIO, size=LABEL)
        thin = self.letter_row(THINNED, gap=0.75)
        rule = text("the 27 − n rule no longer applies:  for 13 letters use 14 − n", LABEL, BAD, BOLD)
        self.stack(head, [changed, dropped, thin, rule], buff=0.75, top=0.8)
        self.no_overlap(*changed)

        n = self.narrate(
            id="concept_journey_09",
            text="Step six: modified alphabets. If the alphabet is reversed or partly reversed, write the new order first, "
                 "then count in it.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "six")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "reversed")
        self.play(FadeIn(changed[0], shift=UP * 0.1))
        self.at_word(n, "write")
        self.play(FadeIn(changed[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_journey_10",
            text="Step seven: thinned alphabets. If every second letter is dropped, thirteen letters remain: A, C, E, G, "
                 "and so on, up to Y.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "seven")
        self.play(Indicate(head, color=FOCUS, scale_factor=1.03))
        self.at_word(n, "dropped")
        self.play(FadeIn(dropped, shift=UP * 0.1))
        self.at_word(n, "remain")
        self.play(FadeIn(thin))
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_journey_11",
            text="Write the new list, then count in it; the twenty-seven minus n rule no longer applies, so use fourteen "
                 "minus n for thirteen letters.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "longer")
        self.play(FadeIn(rule, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_concept_journey")

    # ============================================== 5. RULE BOX ==========

    def rule_box(self):
        self.scene_start("S05_rule_box", title="Rule Box")

        head = self.heading("Rule box", GOOD)
        lines = VGroup(*[text(f, LABEL, INK) for f in FORMULAS]).arrange(DOWN, buff=0.36, aligned_edge=LEFT)
        fit_width(lines, SAFE_W - 1.6)
        box = self.card(lines, width=SAFE_W - 0.4, color=GOOD, pad=0.5)
        self.stack(head, [box], top=0.8)

        n = self.narrate(
            id="rule_box_01",
            text="Here is the rule box. From the right is twenty-seven minus from the left.",
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
            text="The k-th to the right of position n is n plus k; the k-th to the left is n minus k.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "plus")
        self.play(FadeIn(lines[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="rule_box_03",
            text="The letters between a and b number the difference minus one.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "between")
        self.play(FadeIn(lines[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="rule_box_04",
            text="The midpoint is a plus b, over two.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "midpoint")
        self.play(FadeIn(lines[3], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="rule_box_05",
            text="For a changed alphabet, write the new order first.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "changed")
        self.play(FadeIn(lines[4], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="rule_box_06",
            text="And in a shorter alphabet of n letters, the k-th from the right is the n plus one minus k-th from the "
                 "left.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "shorter")
        self.play(FadeIn(lines[5], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_rule_box")

    # ============================================== 6. SHORT TRICK ==========

    def short_trick(self):
        self.scene_start("S06_short_trick", title="Short Trick")

        head = self.heading("Short trick", RATIO)
        order = VGroup(pill("convert first", FOCUS, size=BODY), text("→", BODY, MUTED), pill("then move", GOOD, size=BODY)).arrange(RIGHT, buff=0.5)
        convert = text("position n from the right  =  27 − n from the left", BODY, INK, BOLD)
        move = VGroup(pill("right means add", GOOD, size=LABEL), pill("left means subtract", BAD, size=LABEL)).arrange(RIGHT, buff=0.6)
        self.stack(head, [order, convert, move], buff=1.0, top=1.1)
        self.no_overlap(*order)
        self.no_overlap(*move)

        n = self.narrate(
            id="short_trick_01",
            text="The short trick: convert first, then move.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "convert")
        self.play(FadeIn(order[0], shift=UP * 0.1))
        self.at_word(n, "move")
        self.play(FadeIn(order[1:], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="short_trick_02",
            text="A position n from the right is twenty-seven minus n from the left; then right means add, and left means "
                 "subtract.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "minus")
        self.play(FadeIn(convert, shift=UP * 0.1))
        self.at_word(n, "add")
        self.play(FadeIn(move[0], shift=UP * 0.1))
        self.at_word(n, "subtract")
        self.play(FadeIn(move[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_short_trick")

    # ============================================== 7. THE ANALOGY - A 26-FLOOR BUILDING ==========

    def analogy(self):
        self.scene_start("S07_analogy", title="The Analogy - A 26-Floor Building")

        head = self.heading("The alphabet is a 26-floor building")
        tower = self.building()
        total = pill("17  +  10  =  27", GOOD, size=BODY)
        why = text("the two counts always add up to 27", LABEL, INK)
        stops = VGroup(text("where the analogy stops", SMALL, BAD, BOLD), text("some countries number the ground floor zero", SMALL, INK),
                       text("the alphabet always starts at 1", SMALL, GOOD, BOLD)).arrange(DOWN, buff=0.14, aligned_edge=LEFT)
        side = VGroup(total, why, stops).arrange(DOWN, buff=0.7)
        row = VGroup(tower, side).arrange(RIGHT, buff=0.9)
        self.stack(head, [row], top=0.5)
        self.no_overlap(tower, side)
        self.no_overlap(*side)
        self.no_overlap(tower[3][1], tower[0], tower[4][1])

        n = self.narrate(
            id="analogy_01",
            text="The alphabet is a twenty-six floor building.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "building")
        self.play(FadeIn(tower[0]), FadeIn(tower[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_02",
            text="Floor seventeen from the ground is floor ten from the roof, because the two counts always add up to "
                 "twenty-seven.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "ground")
        self.play(FadeIn(tower[2]), FadeIn(tower[3], shift=UP * 0.1))
        self.at_word(n, "roof")
        self.play(FadeIn(tower[4]))
        self.at_word(n, "add")
        self.play(FadeIn(total, shift=UP * 0.1), FadeIn(why, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_03",
            text="Where the analogy stops: buildings have a ground floor numbered zero in some countries.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "stops")
        self.play(FadeIn(stops[0], shift=RIGHT * 0.2))
        self.at_word(n, "zero")
        self.play(FadeIn(stops[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_04",
            text="The alphabet always starts at one.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "starts")
        self.play(FadeIn(stops[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S07_analogy")

    # ============================================== 8. WORKED EXAMPLE - CLOSING THE HOOK ==========

    def hook_solved(self):
        self.scene_start("S08_hook_solved", title="Worked Example - Closing the Hook")

        head = self.heading("Worked example: closing the hook")
        strip = self.letter_row(ALPHABET)
        calc = pill("10th from the right  =  27 − 10  =  17  =  Q", GOOD, size=BODY)
        check = text("check by counting from Z:   Z, Y, X, W, V, U, T, S, R, Q", LABEL, FOCUS, BOLD)
        self.stack(head, [strip, calc, check], buff=1.0, top=1.1)

        n = self.narrate(
            id="hook_solved_01",
            text="The tenth from the right is twenty-seven minus ten, the seventeenth letter, which is Q.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "tenth")
        self.play(FadeIn(strip))
        self.at_word(n, "minus")
        self.play(FadeIn(calc, shift=UP * 0.1))
        self.at_word(n, "which")
        self.play(strip[16].animate.set_color(FOCUS))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_solved_02",
            text="Check by counting from Z: Z, Y, X, W, V, U, T, S, R, Q.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "counting")
        self.play(FadeIn(check, shift=UP * 0.1))
        self.at_word(n, "Z", occurrence=2)
        self.play(LaggedStart(*[Indicate(strip[25 - i][0], color=GOOD, scale_factor=1.4) for i in range(10)], lag_ratio=0.7))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S08_hook_solved")

    # ============================================== 9. A SECOND WORKED EXAMPLE - TWO STEPS ==========

    def second_example(self):
        self.scene_start("S09_second_example", title="A Second Worked Example - Two Steps")

        head = self.heading("A second worked example: two steps")
        ask = pill("Which letter is 5th to the left of the 10th letter from the right?", FOCUS, size=LABEL)
        strip = self.letter_row(ALPHABET)
        steps = self.solve_steps([("convert:   10th from the right  =  27 − 10", "17th from the left"),
                                  ("move:   5th to the left  =  17 − 5", "12"), ("the 12th letter", "L")])
        self.stack(head, [ask, strip, steps], buff=0.7, top=0.6)
        self.no_overlap(*steps)
        hop = CurvedArrow(strip[16][0].get_top() + UP * 0.08, strip[11][0].get_top() + UP * 0.08, color=BAD, angle=TAU / 6, stroke_width=4)

        n = self.narrate(
            id="second_example_01",
            text="Which letter is fifth to the left of the tenth letter from the right?",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "letter")
        self.play(FadeIn(ask, scale=1.03))
        self.at_word(n, "right")
        self.play(FadeIn(strip))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_02",
            text="Step one, convert: the tenth from the right is the seventeenth from the left.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "convert")
        self.play(FadeIn(steps[0], shift=RIGHT * 0.2))
        self.at_word(n, "seventeenth")
        self.play(strip[16].animate.set_color(FOCUS))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_03",
            text="Step two, move: the fifth to the left is seventeen minus five, twelve.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "move")
        self.play(FadeIn(steps[1], shift=RIGHT * 0.2))
        self.at_word(n, "minus")
        self.play(Create(hop))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_04",
            text="The answer is L.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "answer")
        self.play(FadeIn(steps[2], shift=RIGHT * 0.2), strip[11].animate.set_color(GOOD))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S09_second_example")

    # ============================================== 10. EXAM PATTERNS - HOW THIS IS ASKED ==========

    def exam_patterns(self):
        self.scene_start("S10_exam_patterns", title="Exam Patterns - How This Is Asked")

        head = self.heading("Exam patterns  ·  part 1")
        table, rows = self.pattern_table(head, PATTERNS[:4])

        n = self.narrate(
            id="exam_patterns_01",
            text="Exams ask this in seven ways.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "seven")
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_02",
            text="From the right: the eighth from the right is twenty-seven minus eight, nineteen, which is S.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "eighth")
        self.play(FadeIn(rows[0][:3], shift=RIGHT * 0.2))
        self.at_word(n, "which")
        self.play(FadeIn(rows[0][3], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_03",
            text="Right of a left position: the seventh to the right of the twelfth from the left is twelve plus seven: S.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "seventh")
        self.play(FadeIn(rows[1][:3], shift=RIGHT * 0.2))
        self.at_word(n, "plus")
        self.play(FadeIn(rows[1][3], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_04",
            text="Left of a right position: the fifth to the left of the tenth from the right is seventeen minus five: L.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "fifth")
        self.play(FadeIn(rows[2][:3], shift=RIGHT * 0.2))
        self.at_word(n, "minus")
        self.play(FadeIn(rows[2][3], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_05",
            text="Letters between D and K: eleven minus four minus one, six.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "between")
        self.play(FadeIn(rows[3][:3], shift=RIGHT * 0.2))
        self.at_word(n, "six")
        self.play(FadeIn(rows[3][3], shift=LEFT * 0.1))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Exam patterns  ·  part 2")
        table, rows = self.pattern_table(head, PATTERNS[4:])

        n = self.narrate(
            id="exam_patterns_06",
            text="Midpoint: midway between F and P is six plus sixteen, over two: K.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "midway")
        self.play(FadeIn(rows[0][:3], shift=RIGHT * 0.2))
        self.at_word(n, "over")
        self.play(FadeIn(rows[0][3], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_07",
            text="Changed alphabet: with the first half reversed, the new order is M down to A, then N to Z, and the "
                 "fourth to the right of the ninth from the left is A.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "reversed")
        self.play(FadeIn(rows[1][:3], shift=RIGHT * 0.2))
        self.at_word(n, "is", occurrence=2)
        self.play(FadeIn(rows[1][3], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_08",
            text="Every second letter dropped: thirteen letters remain, so the fifth from the right is the ninth from the "
                 "left: Q.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "dropped")
        self.play(FadeIn(rows[2][:3], shift=RIGHT * 0.2))
        self.at_word(n, "ninth")
        self.play(FadeIn(rows[2][3], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S10_exam_patterns")

    # ============================================== 11. TRAPS AND CONFUSING QUESTIONS ==========

    def traps(self):
        self.scene_start("S11_traps", title="Traps and Confusing Questions")

        head, ask, wrong, right, rule = self.show_trap(TRAPS[0])

        n = self.narrate(
            id="traps_01",
            text="Trap one: moving before converting.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "moving")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_02",
            text="Which letter is eighth to the right of the fifteenth letter from the right?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "letter")
        self.play(FadeIn(ask, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_03",
            text="The wrong instinct: fifteen plus eight is the twenty-third from the right, D. Adding on the right-hand "
                 "scale moves you left, not right.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "instinct")
        self.play(FadeIn(wrong, shift=RIGHT * 0.2))
        self.at_word(n, "Adding")
        self.play(Indicate(wrong, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_04",
            text="Correct: the fifteenth from the right is position twelve, L; the eighth to the right is twelve plus "
                 "eight, twenty: T.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "position")
        self.play(FadeIn(right, shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_05",
            text="The rule: convert to a left position first, then move: right means add, left means subtract.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "convert")
        self.play(FadeIn(rule, scale=1.03))
        self.wait_for_narration(n)
        self.clear_stage()

        head, ask, wrong, right, rule = self.show_trap(TRAPS[1])

        n = self.narrate(
            id="traps_06",
            text="Trap two: counting the end letters as between.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "counting")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_07",
            text="How many letters are there between D and K?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "between")
        self.play(FadeIn(ask, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_08",
            text="The wrong instinct: eleven minus four, seven.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "instinct")
        self.play(FadeIn(wrong, shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_09",
            text="Correct: E, F, G, H, I, J: six.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "six")
        self.play(FadeIn(right, shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_10",
            text="The rule: between means excluding both ends: the difference, minus one.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "excluding")
        self.play(FadeIn(rule, scale=1.03))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S11_traps")

    # ============================================== 12. CHECKPOINT ==========

    def checkpoint(self):
        self.scene_start("S12_checkpoint", title="Checkpoint")

        head = self.heading("Checkpoint  ·  your turn")
        ask = pill("Which letter is 7th to the right of the 12th letter from the left?", FOCUS, size=LABEL)
        strip = self.letter_row(ALPHABET)
        calc = text("12 + 7  =  19", BODY, INK, BOLD)
        answer = pill("the 19th letter:  S", GOOD, size=BODY)
        result = VGroup(calc, answer).arrange(RIGHT, buff=0.7)
        self.stack(head, [ask, strip, result], buff=0.9, top=0.9)
        self.no_overlap(*result)

        n = self.narrate(
            id="checkpoint_01",
            text="Your turn. Which letter is seventh to the right of the twelfth letter from the left?",
            voice="default",
            subtitle=True,
            pause_after=10.0,
        )
        self.at_word(n, "turn")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "letter")
        self.play(FadeIn(ask, scale=1.03))
        self.at_word(n, "left")
        self.play(FadeIn(strip))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="checkpoint_02",
            text="To the right means add: twelve plus seven is nineteen, which is S.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "add")
        self.play(strip[11].animate.set_color(FOCUS))
        self.at_word(n, "plus")
        self.play(FadeIn(calc, shift=UP * 0.1))
        self.at_word(n, "which")
        self.play(FadeIn(answer, shift=UP * 0.1), strip[18].animate.set_color(GOOD))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S12_checkpoint")

    # ============================================== 13. PRACTICE QUESTIONS ==========

    def practice(self):
        self.scene_start("S13_practice", title="Practice Questions")

        head = self.heading("Practice  ·  Levels 1 and 2")
        table, rows = self.practice_table(head, PRACTICE_A, 1)

        n = self.narrate(
            id="practice_01",
            text="Level one, question one: which letter is eighth from the right? Question two: what is the position of V "
                 "from the right? Question three: how many letters are there between D and K?",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "eighth")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "position")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.at_word(n, "between")
        self.play(FadeIn(rows[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="practice_02",
            text="Level two, question four: which letter is seventh to the right of the twelfth letter from the left? "
                 "Question five: which letter is fifth to the left of the tenth letter from the right? Question six: which "
                 "letter is midway between F and P?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "seventh")
        self.play(FadeIn(rows[3], shift=RIGHT * 0.2))
        self.at_word(n, "fifth")
        self.play(FadeIn(rows[4], shift=RIGHT * 0.2))
        self.at_word(n, "midway")
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
        self.play(Indicate(head, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)
        self.clear_stage()

        head = self.heading("Practice  ·  Level 3")
        table, rows = self.practice_table(head, PRACTICE_B, 7)

        n = self.narrate(
            id="practice_04",
            text="Level three, question seven: if the alphabet is written in reverse order, which letter is eighth to the "
                 "right of the fifth letter from the left? Question eight: if the first half of the alphabet is reversed, "
                 "which letter is fourth to the right of the ninth letter from the left? Question nine: if every second "
                 "letter of the alphabet is dropped, which letter is fifth from the right?",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "reverse")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "half")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.at_word(n, "dropped")
        self.play(FadeIn(rows[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="practice_05",
            text="Pause again and solve these three.",
            voice="default",
            subtitle=True,
            pause_after=12.0,
        )
        self.at_word(n, "Pause")
        self.play(Indicate(head, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        self.clear_stage()
        self.scene_end("S13_practice")

    # ============================================== 14. ANSWER KEY, WITH REASONING ==========

    def answers(self):
        self.scene_start("S14_answers", title="Answer Key, with Reasoning")

        head = self.heading("Answer key  ·  1 to 5", GOOD)
        table, rows = self.answer_table(head, ANSWERS_A, 1)

        n = self.narrate(
            id="answers_01",
            text="One: twenty-seven minus eight is nineteen: S.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "minus")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "S")
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_02",
            text="Two: V is twenty-two, and twenty-seven minus twenty-two is five.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "V")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "five")
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_03",
            text="Three: eleven minus four minus one is six.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "minus")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "six")
        self.play(FadeIn(rows[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_04",
            text="Four: twelve plus seven is nineteen: S.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "plus")
        self.play(FadeIn(rows[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "S")
        self.play(FadeIn(rows[3][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_05",
            text="Five: the tenth from the right is seventeen, and seventeen minus five is twelve: L.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "tenth")
        self.play(FadeIn(rows[4][:2], shift=RIGHT * 0.2))
        self.at_word(n, "L")
        self.play(FadeIn(rows[4][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Answer key  ·  6 to 9", GOOD)
        table, rows = self.answer_table(head, ANSWERS_B, 6)

        n = self.narrate(
            id="answers_06",
            text="Six: six plus sixteen, over two, is eleven: K.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "plus")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "K")
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_07",
            text="Seven: in the reversed order, Z, Y, X and so on, position five plus eight is thirteen, which holds the "
                 "letter twenty-seven minus thirteen, the fourteenth: N.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "reversed")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "N")
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_08",
            text="Eight: the new order is M, L, K, down to A, then N to Z. Position nine plus four, thirteen, holds A.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "order")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "holds")
        self.play(FadeIn(rows[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_09",
            text="Nine: the remaining letters are A, C, E, up to Y, and the ninth from the left is Q.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "remaining")
        self.play(FadeIn(rows[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "ninth")
        self.play(FadeIn(rows[3][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S14_answers")

    # ============================================== 15. EXAM LENS - RECOGNISE AND MOVE ==========

    def exam_lens(self):
        self.scene_start("S15_exam_lens", title="Exam Lens - Recognise and Move")

        head = self.heading("Exam lens: recognise and move", RATIO)
        blocks = two_line_blocks(LENS, RATIO)
        self.stack(head, list(blocks), buff=0.6, top=0.8, align=LEFT)

        n = self.narrate(
            id="exam_lens_01",
            text="Recognise and move. The recognition cue: the words, from the right, to the left of, between, or midway.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "cue")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "words")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_lens_02",
            text="The target time: ten seconds for one step, twenty seconds for two.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "target")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "seconds")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_lens_03",
            text="The sanity check: a letter, from the right, near one must be near Z; near twenty-six, it must be near A.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "sanity")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "near")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S15_exam_lens")

    # ============================================== 16. QUICK REVISION AND SUMMARY ==========

    def summary(self):
        self.scene_start("S16_summary", title="Quick Revision and Summary")

        head = self.heading("Quick revision")
        points = VGroup(text("convert right to left with 27 − n,  then add for right and subtract for left", LABEL, INK, BOLD),
                        text("letters between  =  the difference minus one", LABEL, INK, BOLD),
                        text("a changed alphabet:  write the new order first", LABEL, INK, BOLD)).arrange(DOWN, buff=0.55, aligned_edge=LEFT)
        box = VGroup(pill("27 − n", GOOD, size=SMALL), pill("right +,  left −", GOOD, size=SMALL), pill("between = difference − 1", GOOD, size=SMALL),
                     pill("midpoint = average", GOOD, size=SMALL)).arrange(RIGHT, buff=0.3)
        self.stack(head, [points, box], buff=1.1, top=1.1)
        self.no_overlap(*points)
        self.no_overlap(*box)

        n = self.narrate(
            id="summary_01",
            text="Convert right to left with twenty-seven minus n, then add for right and subtract for left.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "Convert")
        self.play(FadeIn(points[0], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_02",
            text="The letters between are the difference minus one.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "between")
        self.play(FadeIn(points[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_03",
            text="For a changed alphabet, write the new order first.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "changed")
        self.play(FadeIn(points[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_04",
            text="The rule box in one line: twenty-seven minus n; right is plus and left is minus; between is the "
                 "difference minus one; and the midpoint is the average.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "line")
        self.play(FadeIn(box[0], shift=UP * 0.1))
        self.at_word(n, "plus")
        self.play(FadeIn(box[1], shift=UP * 0.1))
        self.at_word(n, "difference")
        self.play(FadeIn(box[2], shift=UP * 0.1))
        self.at_word(n, "average")
        self.play(FadeIn(box[3], shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S16_summary")

    # ============================================== 17. SECTION QUIZ ==========

    def section_quiz(self):
        self.scene_start("S17_section_quiz", title="Section Quiz")

        head = self.heading("Section quiz")
        rules = VGroup(pill("6 questions", WORD, size=BODY), pill("5 minutes", WORD, size=BODY), pill("+3 correct", GOOD, size=BODY),
                       pill("−1 wrong", BAD, size=BODY)).arrange(RIGHT, buff=0.4)
        gate = VGroup(VGroup(pill("15 or more out of 18", GOOD, size=LABEL), text("move on", BODY, GOOD, BOLD)).arrange(RIGHT, buff=0.5),
                      VGroup(pill("below 15", BAD, size=LABEL), text("replay the Traps segment, then retry", BODY, INK, BOLD)).arrange(RIGHT, buff=0.5))            .arrange(DOWN, buff=0.6, aligned_edge=LEFT)
        self.stack(head, [rules, gate], buff=1.1, top=1.1)
        self.no_overlap(*rules)
        self.no_overlap(*gate)

        n = self.narrate(
            id="section_quiz_01",
            text="Now the section quiz: six questions in five minutes, with plus three for a correct answer and minus one "
                 "for a wrong one.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "quiz")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "questions")
        self.play(FadeIn(rules[0], shift=UP * 0.1))
        self.at_word(n, "minutes")
        self.play(FadeIn(rules[1], shift=UP * 0.1))
        self.at_word(n, "plus")
        self.play(FadeIn(rules[2], shift=UP * 0.1))
        self.at_word(n, "minus")
        self.play(FadeIn(rules[3], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="section_quiz_02",
            text="Fifteen or more out of eighteen: move on. Below fifteen: replay the traps segment, then retry.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "move")
        self.play(FadeIn(gate[0], shift=RIGHT * 0.2))
        self.at_word(n, "replay")
        self.play(FadeIn(gate[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Section quiz  ·  questions 1 to 3")
        table, rows = self.placed_table(head, ["#", "Question", "Options"],
                                        [[str(0 + i + 1)] + list(row) for i, row in enumerate(QUIZ[0:3])], [0.8, 8.4, 4.0], room=1.3)
        for row in rows:
            row[0].set_color(MUTED)

        n = self.narrate(
            id="section_quiz_03",
            text="Here are questions one, two and three.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "one")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "two")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.at_word(n, "three")
        self.play(FadeIn(rows[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="section_quiz_04",
            text="Pause the video and solve them.",
            voice="default",
            subtitle=True,
            pause_after=12.0,
        )
        self.at_word(n, "Pause")
        self.play(Indicate(head, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)
        self.clear_stage()

        head = self.heading("Section quiz  ·  questions 4 to 6")
        table, rows = self.placed_table(head, ["#", "Question", "Options"],
                                        [[str(3 + i + 1)] + list(row) for i, row in enumerate(QUIZ[3:6])], [0.8, 8.4, 4.0], room=1.3)
        for row in rows:
            row[0].set_color(MUTED)

        n = self.narrate(
            id="section_quiz_05",
            text="And here are questions four, five and six.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "four")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "five")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.at_word(n, "six")
        self.play(FadeIn(rows[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="section_quiz_06",
            text="Pause again and solve them.",
            voice="default",
            subtitle=True,
            pause_after=12.0,
        )
        self.at_word(n, "Pause")
        self.play(Indicate(head, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)
        self.clear_stage()

        head = self.heading("Section quiz  ·  answer key", GOOD)
        table, rows = self.answer_table(head, QUIZ_KEY, 1)
        nxt = self.breadcrumb("Next", "Video 2 · Word Order & Letter Pairs")
        nxt.next_to(table, DOWN, buff=0.6)
        self.no_overlap(table, nxt)
        self.validator.check_in_frame(VGroup(head, table, nxt))

        n = self.narrate(
            id="section_quiz_07",
            text="The answers. One: twenty-seven minus eleven is sixteen, P: option c.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "minus")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "option")
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="section_quiz_08",
            text="Two: the ninth from the right is eighteen, and eighteen plus four is twenty-two, V: option a.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "ninth")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "option")
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="section_quiz_09",
            text="Three: nineteen minus six minus one is twelve: option d.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "minus")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "option")
        self.play(FadeIn(rows[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="section_quiz_10",
            text="Four: eight plus twenty, over two, is fourteen, N: option b.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "plus")
        self.play(FadeIn(rows[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "option")
        self.play(FadeIn(rows[3][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="section_quiz_11",
            text="Five: in the reversed order the right end is A, so the sixth from the right is F: option b.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "reversed")
        self.play(FadeIn(rows[4][:2], shift=RIGHT * 0.2))
        self.at_word(n, "option")
        self.play(FadeIn(rows[4][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="section_quiz_12",
            text="Six: from the right, the remaining letters run Y, W, U, S: option b.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "remaining")
        self.play(FadeIn(rows[5][:2], shift=RIGHT * 0.2))
        self.at_word(n, "option")
        self.play(FadeIn(rows[5][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="section_quiz_13",
            text="Next: word order and letter pairs.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Next")
        self.play(FadeIn(nxt, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S17_section_quiz")

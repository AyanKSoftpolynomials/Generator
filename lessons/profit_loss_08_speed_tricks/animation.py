"""
animation.py for the LMS video generator.

Course : Pre-C-CAT - Section A - Logical Reasoning
Video  : Lesson 2 - Alphabets - 06 - Alphanumeric Sequences

Source script:
  C:\\Scripts\\Section A\\Reasoning_Scripts\\Sessions 1-4 - Coding-Decoding, Alphabets, Directions, Number Series, Odd Man Out\\Lesson 2 - Alphabets\\06 - Alphanumeric Sequences.pdf

Built on the golden-reference pattern:
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``;
  * layouts stacked with next_to and guarded with ``no_overlap``; nothing is
    ever animated onto or into another box.

Lesson 2, Video 5 of 6 (file 06 in its folder).
Not the first video: a silent breadcrumb, a one-line recap of Video 4, then today's topic.
The narration follows the script section by section and ends with the Section Quiz and its answer key.
The 20-element sequence stays on screen wherever a question needs it (concept steps, worked examples, exam patterns, traps,
checkpoint, practice, quiz), with its positions above and its type marks below; letters are blue (vowels orange),
numbers green and symbols purple.
Every count and position in the script was recomputed in the data block; all of them are correct.
Pauses: 10 seconds on the checkpoint, 12 seconds on each practice and quiz screen.
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

SEQ = list("B4#K7E@2MA9$R5U%3T8I")
VOWELS = "AEIOU"


def kind(ch):
    """'V' vowel, 'C' consonant, 'N' number, 'S' symbol."""
    if ch.isalpha():
        return "V" if ch in VOWELS else "C"
    return "N" if ch.isdigit() else "S"


def is_letter(ch):
    return kind(ch) in "VC"


def neighbours(seq):
    """(left neighbour or None, element, right neighbour or None) for every element."""
    return [(seq[i - 1] if i else None, ch, seq[i + 1] if i + 1 < len(seq) else None) for i, ch in enumerate(seq)]


def from_right(k, seq=SEQ):
    return seq[len(seq) - k]


NO_SYMBOLS = [ch for ch in SEQ if kind(ch) != "S"]
NO_NUMBERS = [ch for ch in SEQ if kind(ch) != "N"]
NUMBERS = [ch for ch in SEQ if kind(ch) == "N"]

# ---- concept steps and worked examples ----
assert len(SEQ) == 20 and sum(is_letter(c) for c in SEQ) == 9 and sum(kind(c) == "V" for c in SEQ) == 4
assert NUMBERS == list("4729538") and [c for c in SEQ if kind(c) == "S"] == list("#@$%")
NUM_THEN_LETTER = [c for l, c, r in neighbours(SEQ) if kind(c) == "N" and r and is_letter(r)]
assert NUM_THEN_LETTER == list("72538") and [r for l, c, r in neighbours(SEQ) if kind(c) == "N"] == list("#EM$UTI")
assert "".join(NO_SYMBOLS) == "B4K7E2MA9R5U3T8I" and len(NO_SYMBOLS) == 16 and from_right(6, NO_SYMBOLS) == "5" == NO_SYMBOLS[17 - 6 - 1]
# ---- exam patterns, traps, checkpoint, practice ----
assert [c for l, c, r in neighbours(SEQ) if is_letter(c) and l and kind(l) == "N" and r and kind(r) == "S"] == ["E", "U"]
assert [c for l, c, r in neighbours(SEQ) if kind(c) == "V" and r and kind(r) == "S"] == ["E", "U"]
assert [c for l, c, r in neighbours(SEQ) if kind(c) == "N" and l and r and is_letter(l) and is_letter(r)] == ["7", "5", "8"]
assert SEQ[9 + 7 - 1] == "%" and from_right(4) == SEQ[17 - 1] == "3" and SEQ[17 - 5 - 1] == "$" and SEQ[(3 + 17) // 2 - 1] == "A"
LETTER_THEN_NUM = [c for l, c, r in neighbours(SEQ) if is_letter(c) and r and kind(r) == "N"]
assert LETTER_THEN_NUM == list("BKART") and from_right(6) == "U" and from_right(12) == SEQ[21 - 12 - 1] == "M"
# ---- section quiz ----
assert from_right(8) == SEQ[13 - 1] == "R" and "".join(NO_NUMBERS[:4]) == "B#KE"
assert [c for c in LETTER_THEN_NUM if kind(c) == "C"] == list("BKRT")

OBJECTIVES = [("Classify every element of a mixed sequence", "letter (vowel or consonant), number or symbol"),
              ("Count elements that meet a condition", "“preceded by” and “followed by”"),
              ("Find positions from either end", "including after elements are removed")]
FORMULAS = ["Classify every element first:   L (vowel / consonant),   N,   S",
            "Preceded by  =  left neighbour;        followed by  =  right neighbour",
            "Scan only the anchor type",
            "kth from the right  =  (n + 1 − k)th from the left",
            "Removing elements:   rewrite the sequence, then count"]
PATTERNS_A = [["Number then letter", "numbers immediately followed by a letter", "scan numbers, look right", "5"],
              ["Sandwich", "letters preceded by a number and followed by a symbol", "scan letters, check both sides", "2  (E, U)"],
              ["Vowel condition", "vowels immediately followed by a symbol", "scan vowels, look right", "2  (E, U)"],
              ["Number between letters", "numbers with a letter on both sides", "scan numbers", "3  (7, 5, 8)"]]
PATTERNS_B = [["Position", "7th to the right of the 9th from the left", "9 + 7 = 16", "%"],
              ["From the right", "5th to the left of the 4th from the right", "4th from right = 17th;   17 − 5 = 12", "$"],
              ["After removal", "symbols removed;   6th from the right", "rewrite, then count", "5"],
              ["Middle element", "midway between the 3rd and 17th", "(3 + 17) / 2 = 10", "A"]]
TRAPS = [("Trap 1  ·  “preceded” and “followed” swapped", "How many letters are immediately followed by a number?",
          "counting letters with a number on the left", "look right:  B, K, A, R, T  =  5",
          "“followed by” means the element to its right"),
         ("Trap 2  ·  counting in the original sequence after removal", "If all symbols are removed, which element is 6th from the right?",
          "6th from the right of the original 20:  U", "16 elements remain;  the 6th from right is 5",
          "removal changes every position:  rewrite first")]
PRACTICE = ["How many numbers are immediately followed by a letter?",
            "Which element is 12th from the right?",
            "How many symbols are there in the sequence?",
            "How many letters are immediately preceded by a number and immediately followed by a symbol?",
            "Which element is 7th to the right of the 9th element from the left?",
            "How many numbers have a letter on both sides?",
            "If all symbols are removed, which element is 6th from the right?",
            "Which element is 5th to the left of the 4th element from the right?"]
ANSWERS_A = [("7,  2,  5,  3,  8", "5"),
             ("21 − 12  =  9th from the left", "M"),
             ("#,  @,  $,  %", "4"),
             ("E (7 before, @ after)  and  U (5 before, % after)", "2")]
ANSWERS_B = [("9 + 7  =  16th", "%"),
             ("K 7 E,   R 5 U,   T 8 I", "3"),
             ("16 elements remain;   6th from the right  =  11th", "5"),
             ("4th from the right = 17th;   17 − 5  =  12th", "$")]
LENS = [("Recognition cue", "a line of mixed letters, digits and symbols followed by several questions"),
        ("Target time", "30 seconds per question once the sequence is marked"),
        ("Sanity check", "list the elements you counted:  a number without a list is a guess")]
QUIZ = [["How many vowels are immediately followed by a symbol?", "(a) 0   (b) 2   (c) 1   (d) 4"],
        ["How many letters are immediately followed by a number?", "(a) 5   (b) 4   (c) 6   (d) 3"],
        ["Which element is 8th from the right?", "(a) 2   (b) 5   (c) $   (d) R"],
        ["If all numbers are removed, which element is 4th from the left?", "(a) K   (b) @   (c) E   (d) M"],
        ["How many consonants are immediately followed by a number?", "(a) 5   (b) 4   (c) 3   (d) 2"]]
QUIZ_KEY = [("E (@)  and  U (%)", "(b)  2"),
            ("B,  K,  A,  R,  T", "(a)  5"),
            ("21 − 8  =  13th from the left", "(d)  R"),
            ("B  #  K  E  …", "(c)  E"),
            ("B,  K,  R,  T", "(b)  4")]


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


class AlphanumericSequencesVideo(LMSScene):
    lesson_title = "Alphanumeric Sequences"

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
        self.worked_example()
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

    def token_row(self, seq, gap=0.62):
        """A mixed sequence with positions above and type marks below.  row[i] = (position, element, mark).
        Consonants are blue, vowels orange, numbers green, symbols purple."""
        colors = {"C": WORD, "V": RATIO, "N": GOOD, "S": SECOND}
        marks = {"C": "L", "V": "L", "N": "N", "S": "S"}
        cells = VGroup()
        for i, ch in enumerate(seq):
            x = RIGHT * (i - (len(seq) - 1) / 2) * gap
            k = kind(ch)
            cells.add(VGroup(text(str(i + 1), MIN_FONT, MUTED).move_to(x + UP * 0.52), text(ch, 34, colors[k], BOLD).move_to(x),
                             text(marks[k], MIN_FONT, colors[k]).move_to(x + DOWN * 0.52)))
        self.no_overlap(*cells, gap=0.02)
        return cells

    def layer(self, row, k):
        """One layer of a token_row: 0 = positions, 1 = elements, 2 = type marks."""
        return VGroup(*[cell[k] for cell in row])

    def of_kind(self, row, seq, kinds):
        """The elements of a token_row whose kind is in ``kinds`` ("V", "C", "N", "S")."""
        return VGroup(*[cell[1] for cell, ch in zip(row, seq) if kind(ch) in kinds])

    def trap_with_ref(self, trap, ref):
        """A trap laid out under a reference block.  Returns (head, question, wrong card, right card, rule)."""
        title, question, wrong, right, rule = trap
        head = self.heading(title, BAD)
        ask = fitted_text(question, SAFE_W - 1.0, LABEL, INK, NORMAL, max_lines=2)
        pair = self.verdict_pair(wrong, right)
        rule_pill = fit_width(pill(rule, FOCUS, size=LABEL), SAFE_W)
        self.stack(head, [ref, ask, pair, rule_pill], buff=0.4, top=0.35)
        self.no_overlap(pair[0], pair[1])
        return head, ask, pair[0], pair[1], rule_pill

    # ============================================== 0. INTRO ==========
    # Not the first video: silent breadcrumb, a one-line recap of the previous video, then today's topic.

    def intro(self):
        self.scene_start("S00_intro", title="Intro")

        crumb = self.breadcrumb("Logical Reasoning", "Lesson 2 · Alphabets", "Video 5 of 6")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        recap = VGroup(text("from Video 4  ·  Letter Series", SMALL, MUTED), pill("write positions  →  read the steps  →  extend", WORD, size=LABEL)).arrange(DOWN, buff=0.25)
        title = fit_width(text("Alphanumeric Sequences", TITLE, INK, BOLD), SAFE_W - 0.4)
        today = text("today: classify once, then scan", LABEL, FOCUS)
        block = VGroup(recap, title, today).arrange(DOWN, buff=0.7)
        fit_within(block, SAFE_W, SAFE_H - crumb.height - 0.9)
        block.next_to(crumb, DOWN, buff=0.7)
        self.no_overlap(crumb, recap, title, today)
        self.validator.check_in_frame(VGroup(crumb, block))

        n = self.narrate(
            id="intro_01",
            text="In the last video, a letter series became a number series: write the positions, read the steps, and "
                 "extend.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.at_word(n, "became")
        self.play(FadeIn(recap[0]))
        self.at_word(n, "positions")
        self.play(FadeIn(recap[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="intro_02",
            text="This video covers alphanumeric sequences: classify once, then scan.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "covers")
        self.play(FadeIn(title, shift=UP * 0.1))
        self.at_word(n, "classify")
        self.play(FadeIn(today, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_intro")

    # ============================================== 1. HOOK ==========

    def hook(self):
        self.scene_start("S01_hook", title="Hook")

        head = self.heading("A raw log line")
        raw = Text("".join(SEQ), font="Consolas", font_size=44, color=INK)
        row = self.token_row(SEQ)
        kinds = VGroup(pill("letters", WORD, size=LABEL), pill("digits", GOOD, size=LABEL), pill("symbols", SECOND, size=LABEL)).arrange(RIGHT, buff=0.5)
        job = text("the parser's first job:  classify every token", LABEL, INK)
        moral = pill("classify every element once;  after that, every question is a careful scan", FOCUS, size=LABEL)
        self.stack(head, [raw, row, kinds, job, moral], buff=0.55, top=0.6)
        self.no_overlap(*kinds)

        n = self.narrate(
            id="hook_01",
            text="A parser reading a raw log line does not see words.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "raw")
        self.play(FadeIn(raw))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_02",
            text="It sees tokens: letters, digits, symbols, one after another. Its first job is to classify each one.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "tokens")
        self.play(FadeIn(self.layer(row, 1)))
        self.at_word(n, "letters")
        self.play(FadeIn(kinds[0], shift=UP * 0.1))
        self.at_word(n, "digits")
        self.play(FadeIn(kinds[1], shift=UP * 0.1))
        self.at_word(n, "symbols")
        self.play(FadeIn(kinds[2], shift=UP * 0.1))
        self.at_word(n, "classify")
        self.play(FadeIn(job, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_03",
            text="Exam questions on mixed sequences test exactly that.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "exactly")
        self.play(Indicate(self.layer(row, 1), color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_04",
            text="Before answering, how many numbers are immediately followed by a letter, classify every element once. "
                 "After that, every question is a careful scan.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "classify")
        self.play(FadeIn(self.layer(row, 2)))
        self.at_word(n, "scan")
        self.play(FadeIn(moral, scale=1.03))
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
            text="One: classify every element of a mixed sequence as a letter, vowel or consonant, a number, or a symbol.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "classify")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "vowel")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="objectives_03",
            text="Two: count the elements that meet preceded by, and followed by, conditions.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "count")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "preceded")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="objectives_04",
            text="Three: find positions from either end, including after elements are removed.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "positions")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "removed")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_objectives")

    # ============================================== 3. WHY THIS SECTION ==========

    def why_this_section(self):
        self.scene_start("S03_why_this_section", title="Why This Section")

        head = self.heading("Why this section")
        tests = pill("mixed sequences test precise scanning under conditions", WORD, size=LABEL)
        such = text("such as  “immediately preceded by”", LABEL, MUTED)
        clean = pill("one clean pass, with every element marked, removes almost every error", GOOD, size=LABEL)
        self.stack(head, [tests, such, clean], buff=1.0, top=1.2)

        n = self.narrate(
            id="why_this_section_01",
            text="Mixed sequences test precise scanning under conditions such as, immediately preceded by.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "scanning")
        self.play(FadeIn(tests, scale=1.03))
        self.at_word(n, "such")
        self.play(FadeIn(such, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="why_this_section_02",
            text="One clean pass, with every element marked, removes almost every error.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "pass")
        self.play(FadeIn(clean, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_why_this_section")

    # ============================================== 4. THE CONCEPT JOURNEY ==========

    def concept_journey(self):
        self.scene_start("S04_concept_journey", title="The Concept Journey")

        head = self.heading("Step 1  ·  classify once")
        note = text("we use this 20-element sequence throughout", SMALL, MUTED)
        row = self.token_row(SEQ)
        counts = VGroup(pill("9 letters  (4 vowels)", WORD, size=LABEL), pill("7 numbers", GOOD, size=LABEL), pill("4 symbols", SECOND, size=LABEL))\
            .arrange(RIGHT, buff=0.5)
        mark = text("mark each element:   L  letter  (vowels in orange),   N  number,   S  symbol", LABEL, INK)
        self.stack(head, [note, row, mark, counts], buff=0.8, top=0.8)
        self.no_overlap(*counts)

        n = self.narrate(
            id="concept_journey_01",
            text="We use this sequence of twenty elements throughout.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "sequence")
        self.play(FadeIn(note), FadeIn(self.layer(row, 0), shift=UP * 0.1), FadeIn(self.layer(row, 1), shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_journey_02",
            text="Step one: classify once. Mark each element: L for a letter, with the vowels picked out, N for a number, "
                 "or S for a symbol.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "one")
        self.play(Indicate(head, color=FOCUS, scale_factor=1.03))
        self.at_word(n, "Mark")
        self.play(FadeIn(mark, shift=UP * 0.1), FadeIn(self.layer(row, 2), shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_journey_03",
            text="Here there are nine letters, four of them vowels, seven numbers and four symbols.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "nine")
        self.play(FadeIn(counts[0], shift=UP * 0.1), Indicate(self.of_kind(row, SEQ, 'VC'), color=FOCUS, scale_factor=1.03))
        self.at_word(n, "seven")
        self.play(FadeIn(counts[1], shift=UP * 0.1), Indicate(self.of_kind(row, SEQ, 'N'), color=FOCUS, scale_factor=1.03))
        self.at_word(n, "symbols")
        self.play(FadeIn(counts[2], shift=UP * 0.1), Indicate(self.of_kind(row, SEQ, 'S'), color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Steps 2 and 3  ·  look left, look right;  scan the anchor type")
        row = self.token_row(SEQ)
        left = VGroup(Arrow(RIGHT * 1.1, LEFT * 1.1, color=RATIO, buff=0, stroke_width=5), text("“preceded by”  looks left", LABEL, RATIO, BOLD))\
            .arrange(DOWN, buff=0.15)
        right = VGroup(Arrow(LEFT * 1.1, RIGHT * 1.1, color=GOOD, buff=0, stroke_width=5), text("“followed by”  looks right", LABEL, GOOD, BOLD))\
            .arrange(DOWN, buff=0.15)
        looks = VGroup(left, right).arrange(RIGHT, buff=1.4)
        near = text("“immediately”  means the neighbour, with nothing in between", SMALL, MUTED)
        anchor = VGroup(pill("scan the anchor type", FOCUS, size=LABEL),
                        text("“numbers followed by a letter”:  stop only at numbers, look one step right", SMALL, INK)).arrange(RIGHT, buff=0.4)
        self.stack(head, [row, looks, near, anchor], buff=0.55, top=0.5)
        self.no_overlap(left, right)
        self.no_overlap(*anchor)

        n = self.narrate(
            id="concept_journey_04",
            text="Step two: preceded by looks left; followed by looks right.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "two")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "left")
        self.play(FadeIn(row), FadeIn(left, shift=UP * 0.1))
        self.at_word(n, "right")
        self.play(FadeIn(right, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_journey_05",
            text="Immediately means the neighbour, with nothing in between.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "neighbour")
        self.play(FadeIn(near, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_journey_06",
            text="Step three: scan the anchor type. For numbers followed by a letter, stop only at numbers, and look one "
                 "step right.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "three")
        self.play(FadeIn(anchor[0], shift=UP * 0.1))
        self.at_word(n, "stop")
        self.play(FadeIn(anchor[1], shift=UP * 0.1), Indicate(self.of_kind(row, SEQ, 'N'), color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_journey_07",
            text="Scanning everything wastes time and invites double counting.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "wastes")
        self.play(Indicate(anchor[0], color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Steps 4 to 6  ·  positions, removal, the middle element")
        row = self.token_row(SEQ)
        rules = VGroup(
            VGroup(pill("from either end", WORD, size=LABEL), text("kth from the right  =  (n + 1 − k)th from the left;   here n = 20, so 21 − k", SMALL, INK, BOLD))
            .arrange(RIGHT, buff=0.4),
            VGroup(pill("removing elements", BAD, size=LABEL), text("write the shorter sequence first;  never adjust positions in your head", SMALL, INK, BOLD))
            .arrange(RIGHT, buff=0.4),
            VGroup(pill("middle element", RATIO, size=LABEL), text("between the ath and the bth:  position (a + b) / 2", SMALL, INK, BOLD))
            .arrange(RIGHT, buff=0.4)).arrange(DOWN, buff=0.55, aligned_edge=LEFT)
        self.stack(head, [row, rules], buff=0.8, top=0.6)
        self.no_overlap(*rules)

        n = self.narrate(
            id="concept_journey_08",
            text="Step four: positions from either end. In a sequence of n elements, the k-th from the right is the n plus "
                 "one minus k-th from the left. Here n is twenty, so use twenty-one minus k.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "four")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "sequence")
        self.play(FadeIn(row))
        self.at_word(n, "plus")
        self.play(FadeIn(rules[0], shift=RIGHT * 0.2))
        self.at_word(n, "Here")
        self.play(Indicate(rules[0][1], color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_journey_09",
            text="Step five: removing elements. If symbols are removed, write the shorter sequence before counting "
                 "positions. Never adjust positions in your head.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "five")
        self.play(Indicate(head, color=FOCUS, scale_factor=1.03))
        self.at_word(n, "shorter")
        self.play(FadeIn(rules[1], shift=RIGHT * 0.2))
        self.at_word(n, "Never")
        self.play(Indicate(rules[1][1], color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_journey_10",
            text="Step six: the middle element. Between the a-th and b-th elements, the middle one is at position a plus "
                 "b, over two.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "six")
        self.play(Indicate(head, color=FOCUS, scale_factor=1.03))
        self.at_word(n, "middle", occurrence=2)
        self.play(FadeIn(rules[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_concept_journey")

    # ============================================== 5. RULE BOX ==========

    def rule_box(self):
        self.scene_start("S05_rule_box", title="Rule Box")

        head = self.heading("Rule box", GOOD)
        lines = VGroup(*[text(f, LABEL, INK) for f in FORMULAS]).arrange(DOWN, buff=0.42, aligned_edge=LEFT)
        fit_width(lines, SAFE_W - 1.6)
        box = self.card(lines, width=SAFE_W - 0.4, color=GOOD, pad=0.5)
        self.stack(head, [box], top=0.8)

        n = self.narrate(
            id="rule_box_01",
            text="Here is the rule box. Classify every element first: a letter, vowel or consonant, a number, or a symbol.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "box")
        self.play(FadeIn(box[0]))
        self.at_word(n, "Classify")
        self.play(FadeIn(lines[0], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="rule_box_02",
            text="Preceded by is the left neighbour; followed by is the right neighbour.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "left")
        self.play(FadeIn(lines[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="rule_box_03",
            text="Scan only the anchor type.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "anchor")
        self.play(FadeIn(lines[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="rule_box_04",
            text="The k-th from the right is the n plus one minus k-th from the left.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "plus")
        self.play(FadeIn(lines[3], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="rule_box_05",
            text="When elements are removed, rewrite the sequence, then count.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "rewrite")
        self.play(FadeIn(lines[4], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_rule_box")

    # ============================================== 6. SHORT TRICK ==========

    def short_trick(self):
        self.scene_start("S06_short_trick", title="Short Trick")

        head = self.heading("Short trick", RATIO)
        mark = pill("mark each element  L,  N  or  S,  once", FOCUS, size=BODY)
        scan = text("then scan only the type the question names", BODY, INK, BOLD)
        looks = VGroup(pill("“preceded”  looks left", RATIO, size=LABEL), pill("“followed”  looks right", GOOD, size=LABEL)).arrange(RIGHT, buff=0.6)
        self.stack(head, [mark, scan, looks], buff=1.0, top=1.1)
        self.no_overlap(*looks)

        n = self.narrate(
            id="short_trick_01",
            text="The short trick: mark each element L, N or S once, then scan only the type the question names.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "mark")
        self.play(FadeIn(mark, scale=1.03))
        self.at_word(n, "scan")
        self.play(FadeIn(scan, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="short_trick_02",
            text="Preceded looks left; followed looks right.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "left")
        self.play(FadeIn(looks[0], shift=UP * 0.1))
        self.at_word(n, "right")
        self.play(FadeIn(looks[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_short_trick")

    # ============================================== 7. THE ANALOGY - A TOKENIZER ==========

    def analogy(self):
        self.scene_start("S07_analogy", title="The Analogy - A Tokenizer")

        head = self.heading("This is tokenizing")
        row = self.token_row(SEQ)
        tags = text("tag every token's type first;  every later query is a filter over the tags", LABEL, INK)
        stops = VGroup(text("where the analogy stops", SMALL, BAD, BOLD), text("a program never miscounts;  you can", SMALL, INK),
                       text("mark the sequence on paper instead of holding it in memory", SMALL, GOOD, BOLD)).arrange(DOWN, buff=0.14, aligned_edge=LEFT)
        self.stack(head, [row, tags, stops], buff=0.9, top=0.9)
        self.no_overlap(*stops)

        n = self.narrate(
            id="analogy_01",
            text="This is tokenizing: tag every token's type first, and every later query is a filter over the tags.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "tokenizing")
        self.play(FadeIn(self.layer(row, 1)))
        self.at_word(n, "tag")
        self.play(FadeIn(self.layer(row, 2)))
        self.at_word(n, "filter")
        self.play(FadeIn(tags, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_02",
            text="Where the analogy stops: a program never miscounts.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "stops")
        self.play(FadeIn(stops[0], shift=RIGHT * 0.2))
        self.at_word(n, "never")
        self.play(FadeIn(stops[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_03",
            text="You can, so mark the sequence on paper instead of holding it in memory.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "paper")
        self.play(FadeIn(stops[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S07_analogy")

    # ============================================== 8. WORKED EXAMPLE - NUMBERS FOLLOWED BY A LETTER ==========

    def worked_example(self):
        self.scene_start("S08_worked_example", title="Worked Example - Numbers Followed by a Letter")

        head = self.heading("Worked example")
        ask = pill("How many numbers are immediately followed by a letter?", FOCUS, size=LABEL)
        row = self.token_row(SEQ)
        pairs = VGroup(*[text(f"{c} → {r}", LABEL, GOOD if c in NUM_THEN_LETTER else MUTED, BOLD)
                         for l, c, r in neighbours(SEQ) if kind(c) == "N"]).arrange(RIGHT, buff=0.55)
        answer = pill("followed by a letter:   7,  2,  5,  3,  8      →      5", GOOD, size=LABEL)
        self.stack(head, [ask, row, pairs, answer], buff=0.8, top=0.6)
        self.no_overlap(*pairs)

        n = self.narrate(
            id="worked_example_01",
            text="How many numbers are immediately followed by a letter?",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "numbers")
        self.play(FadeIn(ask, scale=1.03))
        self.at_word(n, "letter")
        self.play(FadeIn(row))
        self.wait_for_narration(n)

        n = self.narrate(
            id="worked_example_02",
            text="Step one, the numbers: four, seven, two, nine, five, three, eight.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "numbers")
        self.play(Indicate(self.of_kind(row, SEQ, 'N'), color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="worked_example_03",
            text="Step two, their right neighbours: four has a hash, seven has E, two has M, nine has a dollar, five has "
                 "U, three has T and eight has I.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "neighbours")
        self.play(FadeIn(pairs, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="worked_example_04",
            text="Step three: seven, two, five, three and eight are followed by a letter, so the answer is five.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "followed")
        self.play(Indicate(pairs, color=FOCUS, scale_factor=1.03))
        self.at_word(n, "answer")
        self.play(FadeIn(answer, scale=1.03))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S08_worked_example")

    # ============================================== 9. A SECOND WORKED EXAMPLE - POSITIONS AFTER REMOVAL ==========

    def second_example(self):
        self.scene_start("S09_second_example", title="A Second Worked Example - Positions After Removal")

        head = self.heading("A second worked example: positions after removal")
        ask = pill("If all symbols are removed, which element is 6th from the right?", FOCUS, size=LABEL)
        row = self.token_row(SEQ)
        short = self.token_row(NO_SYMBOLS)
        steps = VGroup(text("16 elements remain", LABEL, INK), text("6th from the right  =  17 − 6  =  11th from the left", LABEL, INK, BOLD),
                       pill("answer:  5", GOOD, size=LABEL)).arrange(RIGHT, buff=0.6)
        self.stack(head, [ask, row, short, steps], buff=0.5, top=0.45)
        self.no_overlap(*steps)

        n = self.narrate(
            id="second_example_01",
            text="If all symbols are removed, which element is sixth from the right?",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "symbols")
        self.play(FadeIn(ask, scale=1.03))
        self.at_word(n, "element")
        self.play(FadeIn(row))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_02",
            text="Step one: remove the hash, the at sign, the dollar and the percent. Sixteen elements remain.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "remove")
        self.play(VGroup(*[cell for cell, ch in zip(row, SEQ) if kind(ch) == 'S']).animate.set_opacity(0.25))
        self.at_word(n, "remain")
        self.play(FadeIn(short), FadeIn(steps[0], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_03",
            text="Step two: the sixth from the right is seventeen minus six, the eleventh from the left.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "minus")
        self.play(FadeIn(steps[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_04",
            text="Step three: the answer is five.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "answer")
        self.play(FadeIn(steps[2], shift=UP * 0.1), short[10][1].animate.set_color(FOCUS))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S09_second_example")

    # ============================================== 10. EXAM PATTERNS - HOW THIS IS ASKED ==========

    def exam_patterns(self):
        self.scene_start("S10_exam_patterns", title="Exam Patterns - How This Is Asked")

        head = self.heading("Exam patterns  ·  conditions")
        ref = self.token_row(SEQ)
        table, rows = self.table_under(head, ref, ["Pattern", "Example", "Method", "Answer"], PATTERNS_A, [2.8, 4.4, 3.9, 2.2])
        for row in rows:
            row[0].set_color(WORD)
            row[3].set_color(GOOD)

        n = self.narrate(
            id="exam_patterns_01",
            text="Exams ask this in eight ways. Four are conditions.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "eight")
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "conditions")
        self.play(FadeIn(ref))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_02",
            text="Number then letter: scan the numbers and look right, giving five.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Number")
        self.play(FadeIn(rows[0][:3], shift=RIGHT * 0.2))
        self.at_word(n, "giving")
        self.play(FadeIn(rows[0][3], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_03",
            text="The sandwich: letters preceded by a number and followed by a symbol. Scan the letters and check both "
                 "sides: two, E and U.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "sandwich")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "check")
        self.play(FadeIn(rows[1][2], shift=RIGHT * 0.2))
        self.at_word(n, "two")
        self.play(FadeIn(rows[1][3], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_04",
            text="The vowel condition: vowels immediately followed by a symbol. Scan the vowels and look right: two, E and "
                 "U.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "vowel")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "Scan")
        self.play(FadeIn(rows[2][2], shift=RIGHT * 0.2))
        self.at_word(n, "two")
        self.play(FadeIn(rows[2][3], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_05",
            text="A number between letters: numbers with a letter on both sides: three of them, seven, five and eight.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "between")
        self.play(FadeIn(rows[3][:3], shift=RIGHT * 0.2))
        self.at_word(n, "three")
        self.play(FadeIn(rows[3][3], shift=LEFT * 0.1))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Exam patterns  ·  positions")
        ref = self.token_row(SEQ)
        table, rows = self.table_under(head, ref, ["Pattern", "Example", "Method", "Answer"], PATTERNS_B, [2.8, 4.4, 3.9, 2.2])
        for row in rows:
            row[0].set_color(WORD)
            row[3].set_color(GOOD)

        n = self.narrate(
            id="exam_patterns_06",
            text="And four are positions.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "positions")
        self.play(FadeIn(ref))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_07",
            text="Position: the seventh to the right of the ninth from the left is nine plus seven, the sixteenth: the "
                 "percent sign.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "seventh")
        self.play(FadeIn(rows[0][:3], shift=RIGHT * 0.2))
        self.at_word(n, "percent")
        self.play(FadeIn(rows[0][3], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_08",
            text="From the right: the fourth from the right is the seventeenth, and seventeen minus five is the twelfth: "
                 "the dollar sign.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "fourth")
        self.play(FadeIn(rows[1][:3], shift=RIGHT * 0.2))
        self.at_word(n, "dollar")
        self.play(FadeIn(rows[1][3], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_09",
            text="After removal: with the symbols removed, rewrite, then count; the sixth from the right is five.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "removal")
        self.play(FadeIn(rows[2][:3], shift=RIGHT * 0.2))
        self.at_word(n, "five")
        self.play(FadeIn(rows[2][3], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_10",
            text="The middle element: midway between the third and the seventeenth is position ten, which is A.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "midway")
        self.play(FadeIn(rows[3][:3], shift=RIGHT * 0.2))
        self.at_word(n, "which")
        self.play(FadeIn(rows[3][3], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S10_exam_patterns")

    # ============================================== 11. TRAPS AND CONFUSING QUESTIONS ==========

    def traps(self):
        self.scene_start("S11_traps", title="Traps and Confusing Questions")

        ref = self.token_row(SEQ)
        head, ask, wrong, right, rule = self.trap_with_ref(TRAPS[0], ref)

        n = self.narrate(
            id="traps_01",
            text="Trap one: preceded and followed, swapped.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "swapped")
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(ref))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_02",
            text="How many letters are immediately followed by a number?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "letters")
        self.play(FadeIn(ask, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_03",
            text="The wrong instinct: counting the letters whose left neighbour is a number.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "instinct")
        self.play(FadeIn(wrong, shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_04",
            text="Correct: look right. B has four, K has seven, A has nine, R has five and T has eight: five letters.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "right")
        self.play(FadeIn(right, shift=RIGHT * 0.2))
        self.at_word(n, "five", occurrence=2)
        self.play(Indicate(right, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_05",
            text="The rule: followed by means the element to its right.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "means")
        self.play(FadeIn(rule, scale=1.03))
        self.wait_for_narration(n)
        self.clear_stage()

        ref = self.token_row(SEQ)
        head, ask, wrong, right, rule = self.trap_with_ref(TRAPS[1], ref)

        n = self.narrate(
            id="traps_06",
            text="Trap two: counting positions in the original sequence after a removal.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "original")
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(ref))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_07",
            text="If all symbols are removed, which element is sixth from the right?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "removed")
        self.play(FadeIn(ask, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_08",
            text="The wrong instinct: the sixth from the right of the original twenty, which is U.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "instinct")
        self.play(FadeIn(wrong, shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_09",
            text="Correct: the new sequence has sixteen elements, and its sixth from the right is five.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "new")
        self.play(FadeIn(right, shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_10",
            text="The rule: removal changes every position, so rewrite first.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "rewrite")
        self.play(FadeIn(rule, scale=1.03))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S11_traps")

    # ============================================== 12. CHECKPOINT ==========

    def checkpoint(self):
        self.scene_start("S12_checkpoint", title="Checkpoint")

        head = self.heading("Checkpoint  ·  your turn")
        ask = pill("Which element is 12th from the right?", FOCUS, size=BODY)
        row = self.token_row(SEQ)
        work = text("21 − 12  =  9th from the left", BODY, INK, BOLD)
        answer = pill("M", GOOD, size=BODY)
        result = VGroup(work, answer).arrange(RIGHT, buff=0.7)
        self.stack(head, [ask, row, result], buff=0.9, top=0.8)
        self.no_overlap(*result)

        n = self.narrate(
            id="checkpoint_01",
            text="Your turn. Which element is twelfth from the right?",
            voice="default",
            subtitle=True,
            pause_after=10.0,
        )
        self.at_word(n, "turn")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "element")
        self.play(FadeIn(ask, shift=UP * 0.1), FadeIn(row, shift=UP * 0.1))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="checkpoint_02",
            text="Twenty-one minus twelve is nine, and the ninth from the left is M.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "minus")
        self.play(FadeIn(work, shift=UP * 0.1))
        self.at_word(n, "ninth")
        self.play(row[8].animate.set_color(FOCUS), FadeIn(answer, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S12_checkpoint")

    # ============================================== 13. PRACTICE QUESTIONS ==========

    def practice(self):
        self.scene_start("S13_practice", title="Practice Questions")

        head = self.heading("Practice  ·  Level 1")
        ref = self.token_row(SEQ)
        table, rows = self.table_under(head, ref, ["Level", "Question"], [[f"L1  ·  {i + 1}", ask] for i, ask in enumerate(PRACTICE[:3])], [1.6, 11.0])
        for row in rows:
            row[0].set_color(GOOD)

        n = self.narrate(
            id="practice_01",
            text="Level one, with the same sequence. Question one: how many numbers are immediately followed by a letter? "
                 "Question two: which element is twelfth from the right? Question three: how many symbols are there in the "
                 "sequence?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "one")
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "sequence")
        self.play(FadeIn(ref))
        self.at_word(n, "numbers")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "twelfth")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.at_word(n, "symbols")
        self.play(FadeIn(rows[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="practice_02",
            text="Pause the video and solve these three.",
            voice="default",
            subtitle=True,
            pause_after=12.0,
        )
        self.at_word(n, "Pause")
        self.play(Indicate(head, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)
        self.clear_stage()

        head = self.heading("Practice  ·  Level 2")
        ref = self.token_row(SEQ)
        table, rows = self.table_under(head, ref, ["Level", "Question"], [[f"L2  ·  {i + 4}", ask] for i, ask in enumerate(PRACTICE[3:6])], [1.6, 11.0])
        for row in rows:
            row[0].set_color(RATIO)

        n = self.narrate(
            id="practice_03",
            text="Level two. Question four: how many letters are immediately preceded by a number and immediately followed "
                 "by a symbol? Question five: which element is seventh to the right of the ninth element from the left? "
                 "Question six: how many numbers have a letter on both sides?",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "two")
        self.play(FadeIn(ref))
        self.at_word(n, "preceded")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "seventh")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.at_word(n, "both")
        self.play(FadeIn(rows[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="practice_04",
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

        head = self.heading("Practice  ·  Level 3")
        ref = self.token_row(SEQ)
        table, rows = self.table_under(head, ref, ["Level", "Question"], [[f"L3  ·  {i + 7}", ask] for i, ask in enumerate(PRACTICE[6:])], [1.6, 11.0])
        for row in rows:
            row[0].set_color(BAD)

        n = self.narrate(
            id="practice_05",
            text="Level three. Question seven: if all symbols are removed, which element is sixth from the right? Question "
                 "eight: which element is fifth to the left of the fourth element from the right?",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "three")
        self.play(FadeIn(ref))
        self.at_word(n, "removed")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "fifth")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="practice_06",
            text="Pause once more and solve these two.",
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

        head = self.heading("Answer key  ·  1 to 4", GOOD)
        table, rows = self.answer_table(head, ANSWERS_A, 1)

        n = self.narrate(
            id="answers_01",
            text="One: seven, two, five, three and eight, so five.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "seven")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "so")
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_02",
            text="Two: twenty-one minus twelve is the ninth from the left: M.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "minus")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "M")
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_03",
            text="Three: the hash, the at sign, the dollar and the percent: four.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "hash")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "four")
        self.play(FadeIn(rows[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_04",
            text="Four: E, with seven before and the at sign after, and U, with five before and the percent after: two.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "before")
        self.play(FadeIn(rows[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "two")
        self.play(FadeIn(rows[3][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Answer key  ·  5 to 8", GOOD)
        table, rows = self.answer_table(head, ANSWERS_B, 5)

        n = self.narrate(
            id="answers_05",
            text="Five: nine plus seven is the sixteenth, the percent sign.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "plus")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "percent")
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_06",
            text="Six: K seven E, R five U and T eight I: three.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "K")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "three")
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_07",
            text="Seven: sixteen elements remain, and the sixth from the right is the eleventh: five.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "remain")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "five")
        self.play(FadeIn(rows[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_08",
            text="Eight: the fourth from the right is the seventeenth, and seventeen minus five is the twelfth: the dollar "
                 "sign.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "fourth")
        self.play(FadeIn(rows[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "dollar")
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
            text="Recognise and move. The recognition cue: a line of mixed letters, digits and symbols, followed by "
                 "several questions.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "cue")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "line")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_lens_02",
            text="The target time: thirty seconds per question, once the sequence is marked.",
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
            text="The sanity check: list the elements you counted; a number without a list is a guess.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "sanity")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "list")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S15_exam_lens")

    # ============================================== 16. QUICK REVISION AND SUMMARY ==========

    def summary(self):
        self.scene_start("S16_summary", title="Quick Revision and Summary")

        head = self.heading("Quick revision")
        points = VGroup(text("classify every element once", LABEL, INK, BOLD), text("“preceded”  looks left,   “followed”  looks right", LABEL, INK, BOLD),
                        text("use  n + 1 − k  for positions from the right", LABEL, INK, BOLD),
                        text("rewrite the sequence after any removal", LABEL, INK, BOLD)).arrange(DOWN, buff=0.4, aligned_edge=LEFT)
        box = VGroup(pill("classify first", GOOD, size=SMALL), pill("left = preceded,  right = followed", GOOD, size=SMALL), pill("n + 1 − k", GOOD, size=SMALL),
                     pill("rewrite after removal", GOOD, size=SMALL)).arrange(RIGHT, buff=0.3)
        self.stack(head, [points, box], buff=1.0, top=1.0)
        self.no_overlap(*points)
        self.no_overlap(*box)

        n = self.narrate(
            id="summary_01",
            text="Classify every element once.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "Classify")
        self.play(FadeIn(points[0], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_02",
            text="Preceded looks left, followed looks right.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "left")
        self.play(FadeIn(points[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_03",
            text="Use n plus one minus k for positions from the right, and rewrite the sequence after any removal.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "plus")
        self.play(FadeIn(points[2], shift=RIGHT * 0.2))
        self.at_word(n, "rewrite")
        self.play(FadeIn(points[3], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_04",
            text="That is the rule box in one line.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "line")
        self.play(FadeIn(box, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S16_summary")

    # ============================================== 17. SECTION QUIZ ==========

    def section_quiz(self):
        self.scene_start("S17_section_quiz", title="Section Quiz")

        head = self.heading("Section quiz")
        rules = VGroup(pill("5 questions", WORD, size=BODY), pill("4 minutes", WORD, size=BODY), pill("+3 correct", GOOD, size=BODY),
                       pill("−1 wrong", BAD, size=BODY)).arrange(RIGHT, buff=0.4)
        gate = VGroup(VGroup(pill("12 or more out of 15", GOOD, size=LABEL), text("move on", BODY, GOOD, BOLD)).arrange(RIGHT, buff=0.5),
                      VGroup(pill("below 12", BAD, size=LABEL), text("replay the Traps segment, then retry", BODY, INK, BOLD)).arrange(RIGHT, buff=0.5))            .arrange(DOWN, buff=0.6, aligned_edge=LEFT)
        self.stack(head, [rules, gate], buff=1.1, top=1.1)
        self.no_overlap(*rules)
        self.no_overlap(*gate)

        n = self.narrate(
            id="section_quiz_01",
            text="Now the section quiz: five questions in four minutes, with plus three for a correct answer and minus one "
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
            text="Twelve or more out of fifteen: move on. Below twelve: replay the traps segment, then retry.",
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
        ref = self.token_row(SEQ)
        table, rows = self.table_under(head, ref, ["#", "Question", "Options"],
                                       [[str(0 + i + 1)] + list(row) for i, row in enumerate(QUIZ[0:3])], [0.8, 7.6, 4.8])
        for row in rows:
            row[0].set_color(MUTED)

        n = self.narrate(
            id="section_quiz_03",
            text="Here are questions one, two and three.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(ref), FadeIn(table[0]))
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

        head = self.heading("Section quiz  ·  questions 4 to 5")
        ref = self.token_row(SEQ)
        table, rows = self.table_under(head, ref, ["#", "Question", "Options"],
                                       [[str(3 + i + 1)] + list(row) for i, row in enumerate(QUIZ[3:5])], [0.8, 7.6, 4.8])
        for row in rows:
            row[0].set_color(MUTED)

        n = self.narrate(
            id="section_quiz_05",
            text="And here are questions four and five.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(ref), FadeIn(table[0]))
        self.at_word(n, "four")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "five")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
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
        nxt = self.breadcrumb("Next", "Video 6 · All Tricks Combined")
        nxt.next_to(table, DOWN, buff=0.6)
        self.no_overlap(table, nxt)
        self.validator.check_in_frame(VGroup(head, table, nxt))

        n = self.narrate(
            id="section_quiz_07",
            text="The answers. One: E, before the at sign, and U, before the percent: option b.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "before")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "option")
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="section_quiz_08",
            text="Two: B, K, A, R and T: option a.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "and")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "option")
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="section_quiz_09",
            text="Three: twenty-one minus eight is the thirteenth from the left, R: option d.",
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
            text="Four: without numbers the sequence starts B, hash, K, E, so the fourth is E: option c.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "starts")
        self.play(FadeIn(rows[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "option")
        self.play(FadeIn(rows[3][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="section_quiz_11",
            text="Five: B, K, R and T: option b.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "and")
        self.play(FadeIn(rows[4][:2], shift=RIGHT * 0.2))
        self.at_word(n, "option")
        self.play(FadeIn(rows[4][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="section_quiz_12",
            text="Next: all tricks combined.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Next")
        self.play(FadeIn(nxt, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S17_section_quiz")

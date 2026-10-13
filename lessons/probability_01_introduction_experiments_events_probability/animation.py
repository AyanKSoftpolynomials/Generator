"""
animation.py for the LMS video generator.

Course : Pre-C-CAT - Section A - Quantitative Aptitude
Video  : Lesson 21 - Probability - 01 - Introduction - Experiments, Events & Probability

Source script:
  C:\\Scripts\\Section A\\Aptitude\\Sessions 19-20 - Probability\\Lesson 21 - Probability\\01 - Introduction - Experiments, Events & Probability.pdf

Built on the golden-reference pattern:
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``;
  * layouts stacked with next_to and guarded with ``no_overlap``; nothing is
    ever animated onto or into another box.

Lesson 21, Video 1 of 6. First video of the lesson: a silent breadcrumb, "Now we start lesson twenty-one", a one-line recap of Lesson 20, then today's topic. No spoken course welcome.
The narration follows the script section by section. The seven concept steps are split over two screens; the six exam patterns are a four-column table over two screens. The hook's solution shows the numbers 1 to 40 with the primes highlighted, and the analogy shows eight slices with three shaded. Every count is computed in the data block.
Text colours: white and grey, one blue accent, green and red only for right and wrong.
The script has eight practice questions (2 + 3 + 3): five on the first screen, three on the second.
Pauses: 3 seconds on the hook question, 10 seconds on the checkpoint, 12 seconds on each practice screen.
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


def is_prime(n):
    return n > 1 and all(n % d for d in range(2, int(n ** 0.5) + 1))


def prob(event, space):
    """Classical probability over an explicit sample space."""
    space = list(space)
    return Fraction(sum(1 for x in space if event(x)), len(space))


# ---- the hook: tokens 1 to 40, a prime wins ----
PRIMES_40 = [n for n in range(1, 41) if is_prime(n)]
assert PRIMES_40 == [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37] and len(PRIMES_40) == 12
P_HOOK = prob(is_prime, range(1, 41))
assert P_HOOK == Fraction(3, 10) < Fraction(1, 3) and 40 - 12 == 28 and Fraction(12, 28) == Fraction(3, 7)

# ---- second worked example: the complement ----
SQUARES = [n for n in range(1, 101) if int(n ** 0.5) ** 2 == n]
assert len(SQUARES) == 10 and 1 - Fraction(10, 100) == Fraction(9, 10)

# ---- exam patterns, traps, checkpoint, practice (answers computed) ----
assert prob(lambda x: x > 4, range(1, 7)) == Fraction(1, 3) and prob(lambda x: x % 7 == 0, range(1, 51)) == Fraction(7, 50)
assert Fraction(4, 4 + 7) == Fraction(4, 11) and (9 - 2, 2) == (7, 2) and prob(lambda x: x == 8, range(1, 7)) == 0
assert Fraction(3, 3 + 5) == Fraction(3, 8) and len(range(11, 31)) == 20 and prob(lambda x: x % 5 == 0, range(11, 31)) == Fraction(1, 5)
assert prob(lambda x: x % 4 != 0, range(1, 26)) == Fraction(19, 25) and len([x for x in range(1, 26) if x % 4 == 0]) == 6
assert prob(lambda x: x > 2, range(1, 7)) == Fraction(2, 3) and prob(lambda x: x % 4 == 0, range(1, 21)) == Fraction(1, 4)
assert prob(lambda x: int(x ** 0.5) ** 2 == x, range(1, 51)) == Fraction(7, 50) and 1 - Fraction(5, 12) == Fraction(7, 12) and 20 - 7 == 13
assert prob(is_prime, range(1, 31)) == Fraction(1, 3) and prob(lambda x: x % 2 and x % 5, range(1, 101)) == Fraction(2, 5)
assert prob(lambda x: x // 10 == x % 10, range(10, 100)) == Fraction(1, 10)

OBJECTIVES = [("Describe an experiment by its sample space", "and an event as part of it"),
              ("Find a probability as favourable ÷ total outcomes", "and use the complement"),
              ("Convert between probability and odds", "in favour or against")]
STEPS_A = [("Experiment and outcome", "an action whose result is uncertain:  a coin, a die, a card;    each possible result is an outcome"),
           ("Sample space S:  the set of all possible outcomes", "for one die:   S = {1, 2, 3, 4, 5, 6},   n(S) = 6"),
           ("Event:  any collection of outcomes", "“an even number”:   E = {2, 4, 6},   n(E) = 3"),
           ("Classical probability:   P(E) = n(E)/n(S)", "when all outcomes are equally likely;    an even number on a die:   3/6 = 1/2")]
STEPS_B = [("The range:   0 ≤ P(E) ≤ 1", "impossible (a 7 on a die):   P = 0;     sure (a number from 1 to 6):   P = 1"),
           ("The complement:   P(not E) = 1 − P(E)", "“not E” is every outcome outside E:  the two together cover the whole sample space"),
           ("Odds in favour = n(E) : n(not E);     odds against = n(not E) : n(E)", "odds in favour a : b    gives    P(E) = a/(a + b)")]
FORMULAS = ["P(E)   =   n(E) / n(S)          (equally likely outcomes)",
            "0 ≤ P(E) ≤ 1;          impossible:  0;          sure:  1",
            "P(not E)   =   1 − P(E)",
            "Odds in favour  =  n(E) : n(not E);          odds against  =  n(not E) : n(E)",
            "Odds in favour a : b      →      P(E)  =  a/(a + b)"]
PATTERNS = [("One die", "a number greater than 4", "{5, 6} of 6", "1/3"),
            ("Number range", "1 to 50;  a multiple of 7", "7, 14, …, 49:  7 numbers", "7/50"),
            ("Complement", "1 to 100;  not a perfect square", "1 − 10/100", "9/10"),
            ("Odds to probability", "odds in favour 4 : 7", "4/(4 + 7)", "4/11"),
            ("Probability to odds", "P(E) = 2/9;  odds against?", "(9 − 2) : 2", "7 : 2"),
            ("Impossible event", "one die shows 8", "no outcome qualifies", "0")]
TRAPS = [("Trap 1  ·  odds read as a probability", "The odds in favour of an event are 3 : 5.  Find P(event).",
          "3/5", "3/(3 + 5)  =  3/8",
          "Odds compare favourable with unfavourable; probability, favourable with the total."),
         ("Trap 2  ·  miscounting an inclusive range", "A number is chosen at random from 11 to 30.  Find P(it is a multiple of 5).",
          "30 − 11 = 19 numbers:  4/19", "20 numbers:  4/20 = 1/5",
          "Numbers from a to b inclusive:  b − a + 1."),
         ("Trap 3  ·  1 counted as a prime", "A number from 1 to 40 is chosen.  Find P(prime).",
          "13/40,  counting 1", "12/40  =  3/10",
          "1 is neither prime nor composite; the smallest prime is 2.")]
PRACTICE_A = [("L1", "A die is rolled.  Find the probability of a number greater than 2."),
              ("L1", "A number is chosen at random from 1 to 20.  Find the probability that it is a multiple of 4."),
              ("L2", "A number is chosen at random from 1 to 50.  Find the probability that it is a perfect square."),
              ("L2", "The odds in favour of an event are 5 : 7.  Find the probability that the event does not happen."),
              ("L2", "The probability of an event is 7/20.  Find the odds against it.")]
PRACTICE_B = [("L3", "A number is chosen at random from 1 to 30.  Find the probability that it is prime."),
              ("L3", "A number is chosen at random from 1 to 100.  Find the probability that it is divisible by neither 2 nor 5."),
              ("L3", "A two-digit number (10 to 99) is chosen at random.  Find the probability that its two digits are equal.")]
ANSWERS_A = [("{3, 4, 5, 6}:     4/6", "2/3"),
             ("4, 8, 12, 16, 20:     5/20", "1/4"),
             ("1, 4, 9, 16, 25, 36, 49:     7 numbers", "7/50"),
             ("P(happens) = 5/12", "P(does not) = 7/12")]
ANSWERS_B = [("unfavourable   20 − 7 = 13", "odds against  13 : 7"),
             ("2, 3, 5, 7, 11, 13, 17, 19, 23, 29:     10/30", "1/3"),
             ("such numbers end in 1, 3, 7 or 9:    4 in every 10;    40/100", "2/5"),
             ("11, 22, …, 99:     9 numbers out of 90", "1/10")]
LENS = [("Recognition cue", "“at random”, “chosen”, “drawn”:   write n(S) first, then n(E)"),
        ("Target time", "15 seconds;  20 seconds when odds are involved"),
        ("Sanity check", "the answer lies between 0 and 1,   and   P(E) + P(not E) = 1")]


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


class IntroductionExperimentsEventsAndProbabilityVideo(LMSScene):
    lesson_title = "Introduction: Experiments, Events & Probability"

    def construct(self):
        self.camera.background_color = BG

        self.intro()
        self.hook()
        self.objectives()
        self.why_this_matters()
        self.experiment_to_probability()
        self.range_complement_odds()
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

    # ============================================== 0. INTRO ==========
    # First video of the lesson: silent breadcrumb, the lesson announcement, a recap of the previous lesson, then today's topic.

    def intro(self):
        self.scene_start("S00_intro", title="Intro")

        crumb = self.breadcrumb("Quantitative Aptitude", "Lesson 21 · Probability", "Video 1 of 6")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        lesson = pill("Lesson 21  ·  Probability", RATIO, size=LABEL)
        recap = VGroup(text("from Lesson 20  ·  Partnership", SMALL, MUTED),
                       fit_width(VGroup(pill("profit ratio = capital × time", WORD, size=LABEL), pill("pay the working partner first", GOOD, size=LABEL)).arrange(RIGHT, buff=0.4), SAFE_W - 0.6)).arrange(DOWN, buff=0.25)
        title = fit_width(text("Introduction: Experiments, Events & Probability", TITLE, INK, BOLD), SAFE_W - 0.4)
        today = text("today: the one fraction this lesson is built on", LABEL, FOCUS)
        block = VGroup(lesson, recap, title, today).arrange(DOWN, buff=0.55)
        fit_within(block, SAFE_W, SAFE_H - crumb.height - 0.9)
        block.next_to(crumb, DOWN, buff=0.6)
        self.no_overlap(crumb, lesson, recap, title, today)
        self.no_overlap(*recap[1])
        self.validator.check_in_frame(VGroup(crumb, block))

        n = self.narrate(
            id="intro_01",
            text="Now we start lesson twenty-one: probability.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.at_word(n, "twenty-one")
        self.play(FadeIn(lesson, scale=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="intro_02",
            text="In lesson twenty, profit was shared in the ratio of capital times time, after paying any working partner "
                 "first.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "times")
        self.play(FadeIn(recap[0]), FadeIn(recap[1][0], shift=UP * 0.1))
        self.at_word(n, "first")
        self.play(FadeIn(recap[1][1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="intro_03",
            text="This first video is the introduction: experiments, events and probability, and the one fraction this "
                 "lesson is built on.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "introduction")
        self.play(FadeIn(title, shift=UP * 0.1))
        self.at_word(n, "fraction")
        self.play(FadeIn(today, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_intro")

    # ============================================== 1. HOOK ==========

    def hook(self):
        self.scene_start("S01_hook", title="Hook")

        head = self.heading("A tech-fest lucky draw")
        drum = pill("a drum of 40 tokens, numbered 1 to 40;   one is drawn at random", WORD, size=LABEL)
        prize = pill("every prime number wins a prize", GOOD, size=LABEL)
        friend = text("a friend:  “roughly one small number in three is prime, so it's about 1 in 3”", LABEL, INK)
        ask = VGroup(pill("better or worse than 1 in 3?", FOCUS, size=LABEL), pill("what are the odds against you?", FOCUS, size=LABEL))\
            .arrange(RIGHT, buff=0.5)
        promise = text("by the end: both, exactly, and the one formula this lesson is built on", LABEL, INK, BOLD)
        self.stack(head, [drum, prize, friend, ask, promise], buff=0.45, top=0.5)
        self.no_overlap(*ask)

        n = self.narrate(
            id="hook_01",
            text="At a tech fest, tokens numbered one to forty go into a drum, and one is drawn at random. Every prime "
                 "number wins a prize.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "tokens")
        self.play(FadeIn(drum, shift=UP * 0.1))
        self.at_word(n, "prime")
        self.play(FadeIn(prize, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_02",
            text="A friend says: roughly one small number in three is prime, so it's about one in three.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "friend")
        self.play(FadeIn(friend, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_03",
            text="Is your chance better or worse than one in three? And what are the odds against you?",
            voice="default",
            subtitle=True,
            pause_after=3.0,
        )
        self.at_word(n, "better")
        self.play(FadeIn(ask[0], scale=1.03))
        self.at_word(n, "odds")
        self.play(FadeIn(ask[1], scale=1.03))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="hook_04",
            text="By the end of this video you will answer both exactly, and you will have the one formula this whole "
                 "lesson is built on.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "exactly")
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
            text="First, describe an experiment by its sample space, and an event as part of it.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "describe")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "event")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="objectives_03",
            text="Second, find a probability as favourable outcomes over total outcomes, and use the complement.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "favourable")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "complement")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="objectives_04",
            text="Third, convert between probability and odds, in favour or against.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "convert")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "favour")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_objectives")

    # ============================================== 3. WHY THIS MATTERS ==========

    def why_this_matters(self):
        self.scene_start("S03_why_this_matters", title="Why This Matters")

        head = self.heading("Why this matters")
        frac = pill("every probability question rests on one fraction:    favourable over total", WORD, size=LABEL)
        counts = text("get the two counts right", LABEL, INK, BOLD)
        comp = pill("and know that   P(not A) = 1 − P(A)", FOCUS, size=LABEL)
        settles = text("that settles most questions before any formula is needed", LABEL, MUTED)
        self.stack(head, [frac, counts, comp, settles], buff=0.7, top=0.9)

        n = self.narrate(
            id="why_this_matters_01",
            text="Every probability question in the exam rests on one fraction: favourable over total.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "fraction")
        self.play(FadeIn(frac, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="why_this_matters_02",
            text="Getting the two counts right, and knowing that P of not A is one minus P of A, settles most questions "
                 "before any formula is needed.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "counts")
        self.play(FadeIn(counts, shift=UP * 0.1))
        self.at_word(n, "minus")
        self.play(FadeIn(comp, scale=1.03))
        self.at_word(n, "settles")
        self.play(FadeIn(settles, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_why_this_matters")

    # ============================================== 4. CONCEPT - FROM EXPERIMENT TO PROBABILITY ==========

    def experiment_to_probability(self):
        self.scene_start("S04_experiment_to_probability", title="Concept - From Experiment to Probability")

        head = self.heading("From experiment to probability")
        blocks = two_line_blocks(STEPS_A, WORD)
        self.stack(head, list(blocks), buff=0.5, top=0.7, align=LEFT)

        n = self.narrate(
            id="experiment_to_probability_01",
            text="An experiment is an action whose result is uncertain: tossing a coin, rolling a die, drawing a card. "
                 "Each possible result is an outcome.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "experiment")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "outcome")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="experiment_to_probability_02",
            text="The sample space is the set of all possible outcomes, written S. For one die, S is one to six, and n of "
                 "S is six.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "space")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "die")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="experiment_to_probability_03",
            text="An event is any collection of outcomes. An even number is the event E, two, four, six, so n of E is "
                 "three.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "event")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "even")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="experiment_to_probability_04",
            text="Classical probability: when all outcomes are equally likely, P of E is n of E over n of S. For an even "
                 "number on a die: three over six, one half.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Classical")
        self.play(FadeIn(blocks[3][0], shift=RIGHT * 0.2))
        self.at_word(n, "half")
        self.play(FadeIn(blocks[3][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_experiment_to_probability")

    # ============================================== 5. CONCEPT - THE RANGE, THE COMPLEMENT AND ODDS ==========

    def range_complement_odds(self):
        self.scene_start("S05_range_complement_odds", title="Concept - The Range, the Complement and Odds")

        head = self.heading("The range, the complement and odds")
        blocks = two_line_blocks(STEPS_B, WORD)
        self.stack(head, list(blocks), buff=0.75, top=1.0, align=LEFT)

        n = self.narrate(
            id="range_complement_odds_01",
            text="The range: P of E lies between zero and one. An impossible event, like a seven on a die, has probability "
                 "zero; a sure event, like a number from one to six, has probability one.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "range")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "impossible")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="range_complement_odds_02",
            text="The complement: not E is every outcome outside E. P of not E is one minus P of E, because the two "
                 "together cover the whole sample space.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "complement")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "together")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="range_complement_odds_03",
            text="Odds in favour are n of E to n of not E; odds against are the other way round. If the odds in favour are "
                 "a to b, then P of E is a over a plus b.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "favour")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "over")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_range_complement_odds")

    # ============================================== 6. FORMULA BOX ==========

    def formula_box(self):
        self.scene_start("S06_formula_box", title="Formula Box")

        head = self.heading("Formula box", GOOD)
        lines = VGroup(*[text(f, LABEL, INK) for f in FORMULAS]).arrange(DOWN, buff=0.45, aligned_edge=LEFT)
        fit_width(lines, SAFE_W - 1.6)
        box = self.card(lines, width=SAFE_W - 0.4, color=GOOD, pad=0.5)
        self.stack(head, [box], top=0.7)

        n = self.narrate(
            id="formula_box_01",
            text="Here is the formula box. P of E is n of E over n of S, for equally likely outcomes.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "box")
        self.play(FadeIn(box[0]))
        self.at_word(n, "over")
        self.play(FadeIn(lines[0], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_box_02",
            text="P of E lies between zero and one: zero if impossible, one if sure.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "between")
        self.play(FadeIn(lines[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_box_03",
            text="P of not E is one minus P of E.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "minus")
        self.play(FadeIn(lines[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_box_04",
            text="Odds in favour are n of E to n of not E, and odds against are the reverse.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "favour")
        self.play(FadeIn(lines[3], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_box_05",
            text="And odds in favour of a to b give P of E as a over a plus b.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "give")
        self.play(FadeIn(lines[4], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_formula_box")

    # ============================================== 7. THE ANALOGY - A PIZZA IN EQUAL SLICES ==========

    def analogy(self):
        self.scene_start("S07_analogy", title="The Analogy - A Pizza in Equal Slices")

        head = self.heading("A pizza in equal slices")
        slices = VGroup(*[Square(side_length=0.45, color=WORD, stroke_width=2, fill_color=WORD, fill_opacity=0.7 if i < 3 else 0.0)
                          for i in range(8)]).arrange(RIGHT, buff=0.12)
        space = pill("the sample space:  a pizza cut into equal slices, one per outcome", WORD, size=LABEL)
        event = text("an event:  the slices with a particular topping", LABEL, INK, BOLD)
        share = pill("probability = the share of the pizza:    3 olive slices out of 8 is 3/8", FOCUS, size=LABEL)
        stops = VGroup(text("Where the analogy stops:  the slices must be equal", LABEL, BAD, BOLD),
                       text("“0, 1 or 2 heads” for two coins are unequal slices:  counting them gives a wrong answer", LABEL, INK),
                       text("Video 2 shows exactly where this goes wrong", LABEL, MUTED)).arrange(DOWN, buff=0.2)
        self.stack(head, [slices, space, event, share, stops], buff=0.45, top=0.6)

        n = self.narrate(
            id="analogy_01",
            text="Think of the sample space as a pizza cut into equal slices, one slice per outcome.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "pizza")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "slices")
        self.play(FadeIn(slices), FadeIn(space, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_02",
            text="An event is the slices with a particular topping.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "topping")
        self.play(FadeIn(event, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_03",
            text="The probability is simply the share of the pizza those slices make up: three olive slices out of eight "
                 "is three eighths.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "share")
        self.play(FadeIn(share, scale=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_04",
            text="Where the analogy stops: the slices must be equal. If you list results that are not equally likely, say "
                 "zero, one or two heads for two coins, you have unequal slices, and counting them gives a wrong answer. "
                 "Video two shows exactly where this goes wrong.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "stops")
        self.play(FadeIn(stops[0], shift=UP * 0.1))
        self.at_word(n, "unequal")
        self.play(FadeIn(stops[1], shift=UP * 0.1))
        self.at_word(n, "Video")
        self.play(FadeIn(stops[2], shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S07_analogy")

    # ============================================== 8. WORKED EXAMPLE - CLOSING THE HOOK ==========

    def hook_solved(self):
        self.scene_start("S08_hook_solved", title="Worked Example - Closing the Hook")

        head = self.heading("Primes from 1 to 40")
        grid = VGroup(*[text(str(k), SMALL, GOOD if k in PRIMES_40 else MUTED, BOLD if k in PRIMES_40 else NORMAL) for k in range(1, 41)])\
            .arrange_in_grid(rows=4, cols=10, buff=(0.42, 0.2))
        steps = self.solve_steps([("Primes:   2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37", "12 primes   (1 is not prime)"),
                                  ("P(prize)  =  12/40", "=  3/10,   less than 1/3"),
                                  ("Not prime:   40 − 12 = 28;      odds in favour 12 : 28 = 3 : 7", "odds against   7 : 3")])
        self.stack(head, [grid, steps], buff=0.6, top=0.6)
        self.no_overlap(*steps)

        n = self.narrate(
            id="hook_solved_01",
            text="The primes from one to forty are two, three, five, seven, eleven, thirteen, seventeen, nineteen, "
                 "twenty-three, twenty-nine, thirty-one and thirty-seven. That is twelve; one is not prime.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "primes")
        self.play(FadeIn(grid))
        self.at_word(n, "twelve")
        self.play(FadeIn(steps[0], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_solved_02",
            text="The probability of a prize is twelve over forty, three tenths. This is less than one third, so your "
                 "chance is slightly worse than your friend's guess.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "over")
        self.play(FadeIn(steps[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "less")
        self.play(FadeIn(steps[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_solved_03",
            text="Not prime: forty minus twelve is twenty-eight. The odds in favour are twelve to twenty-eight, three to "
                 "seven, so the odds against you are seven to three.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "minus")
        self.play(FadeIn(steps[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "against")
        self.play(FadeIn(steps[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S08_hook_solved")

    # ============================================== 9. A SECOND WORKED EXAMPLE - USING THE COMPLEMENT ==========

    def second_example(self):
        self.scene_start("S09_second_example", title="A Second Worked Example - Using the Complement")

        head = self.heading("Using the complement")
        ask = text("a number is chosen at random from 1 to 100:   P(it is not a perfect square)?", LABEL, MUTED)
        steps = self.solve_steps([("Perfect squares from 1 to 100:    1², 2², …, 10²", "10 numbers"),
                                  ("P(perfect square)  =  10/100", "=  1/10"),
                                  ("P(not a perfect square)  =  1 − 1/10", "=  9/10")])
        self.stack(head, [ask, steps], buff=0.8, top=0.9)
        self.no_overlap(*steps)

        n = self.narrate(
            id="second_example_01",
            text="A number is chosen at random from one to one hundred. What is the probability that it is not a perfect "
                 "square?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "chosen")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "not")
        self.play(FadeIn(ask, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_02",
            text="The perfect squares from one to one hundred are one squared up to ten squared: ten numbers.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "squared")
        self.play(FadeIn(steps[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "numbers")
        self.play(FadeIn(steps[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_03",
            text="The probability of a perfect square is ten over one hundred, one tenth.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "over")
        self.play(FadeIn(steps[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "tenth")
        self.play(FadeIn(steps[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_04",
            text="So the probability of not a perfect square is one minus one tenth: nine tenths.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "minus")
        self.play(FadeIn(steps[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "nine")
        self.play(FadeIn(steps[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S09_second_example")

    # ============================================== 10. EXAM PATTERNS - HOW THIS IS ASKED ==========

    def exam_patterns(self):
        self.scene_start("S10_exam_patterns", title="Exam Patterns - How This Is Asked")

        head = self.heading("Exam patterns  ·  1 to 3 of 6")
        table, rows = self.placed_table(head, ["Pattern", "Example", "Method", "Answer"], [list(p) for p in PATTERNS[0:3]],
                                        [2.8, 4.4, 4.0, 2.0], room=1.2)
        for row in rows:
            row[0].set_color(WORD)
            row[3].set_color(GOOD)

        n = self.narrate(
            id="exam_patterns_01",
            text="Exams ask this in six ways.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "six")
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_02",
            text="One die: a number greater than four. Five and six, out of six: one third.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "greater")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "out")
        self.play(FadeIn(rows[0][2:], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_03",
            text="A number range: one to fifty, a multiple of seven. Seven, fourteen, up to forty-nine, seven numbers: "
                 "seven fiftieths.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "range")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "numbers")
        self.play(FadeIn(rows[1][2:], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_04",
            text="The complement: one to one hundred, not a perfect square. One minus ten hundredths: nine tenths.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "complement")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "minus")
        self.play(FadeIn(rows[2][2:], shift=RIGHT * 0.2))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Exam patterns  ·  4 to 6 of 6")
        table, rows = self.placed_table(head, ["Pattern", "Example", "Method", "Answer"], [list(p) for p in PATTERNS[3:6]],
                                        [2.8, 4.4, 4.0, 2.0], room=1.2)
        for row in rows:
            row[0].set_color(WORD)
            row[3].set_color(GOOD)

        n = self.narrate(
            id="exam_patterns_05",
            text="Odds to probability: odds in favour of four to seven. Four over four plus seven: four elevenths.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "Odds")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "over")
        self.play(FadeIn(rows[0][2:], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_06",
            text="Probability to odds: P of E is two ninths; what are the odds against? Nine minus two, to two: seven to "
                 "two.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "ninths")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "minus")
        self.play(FadeIn(rows[1][2:], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_07",
            text="An impossible event: one die shows eight. No outcome qualifies: zero.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "impossible")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "qualifies")
        self.play(FadeIn(rows[2][2:], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S10_exam_patterns")

    # ============================================== 11. TRAPS AND CONFUSING QUESTIONS ==========

    def traps(self):
        self.scene_start("S11_traps", title="Traps and Confusing Questions")

        head, q, wrong, right, rule = self.show_trap(TRAPS[0])

        n = self.narrate(
            id="traps_01",
            text="Trap one: odds read as a probability. The odds in favour of an event are three to five: find the "
                 "probability of the event.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "read")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "favour")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_02",
            text="The wrong instinct says three fifths. The correct answer is three over three plus five: three eighths.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "wrong")
        self.play(FadeIn(wrong, shift=UP * 0.1))
        self.at_word(n, "correct")
        self.play(FadeIn(right, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_03",
            text="The rule: odds compare favourable with unfavourable; probability compares favourable with the total.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "rule")
        self.play(FadeIn(rule, shift=UP * 0.1))
        self.wait_for_narration(n)
        self.clear_stage()

        head, q, wrong, right, rule = self.show_trap(TRAPS[1])

        n = self.narrate(
            id="traps_04",
            text="Trap two: miscounting an inclusive range. A number is chosen at random from eleven to thirty: find the "
                 "probability that it is a multiple of five.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "miscounting")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "chosen")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_05",
            text="The wrong instinct counts thirty minus eleven, nineteen numbers: four nineteenths. The correct count is "
                 "twenty numbers, and fifteen, twenty, twenty-five and thirty qualify: four twentieths, one fifth.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "wrong")
        self.play(FadeIn(wrong, shift=UP * 0.1))
        self.at_word(n, "correct")
        self.play(FadeIn(right, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_06",
            text="The rule: the numbers from a to b inclusive number b minus a plus one.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "rule")
        self.play(FadeIn(rule, shift=UP * 0.1))
        self.wait_for_narration(n)
        self.clear_stage()

        head, q, wrong, right, rule = self.show_trap(TRAPS[2])

        n = self.narrate(
            id="traps_07",
            text="Trap three: one counted as a prime. A number from one to forty is chosen: find the probability that it "
                 "is prime.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "counted")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "chosen")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_08",
            text="The wrong instinct counts one, and says thirteen fortieths. The correct answer is twelve fortieths: "
                 "three tenths.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "wrong")
        self.play(FadeIn(wrong, shift=UP * 0.1))
        self.at_word(n, "correct")
        self.play(FadeIn(right, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_09",
            text="The rule: one is neither prime nor composite; the smallest prime is two.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "rule")
        self.play(FadeIn(rule, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S11_traps")

    # ============================================== 12. CHECKPOINT ==========

    def checkpoint(self):
        self.scene_start("S12_checkpoint", title="Checkpoint")

        head = self.heading("Checkpoint  ·  your turn")
        given = pill("a number is chosen at random from 1 to 25:   P(it is not a multiple of 4)?", FOCUS, size=LABEL)
        work = VGroup(text("multiples of 4:    4, 8, 12, 16, 20, 24:    6 numbers;      P = 6/25", LABEL, INK, BOLD),
                      text("P(not)  =  1 − 6/25  =  19/25", BODY, GOOD, BOLD)).arrange(DOWN, buff=0.4)
        self.stack(head, [given, work], buff=0.9, top=1.0)
        self.no_overlap(*work)

        n = self.narrate(
            id="checkpoint_01",
            text="Your turn. A number is chosen at random from one to twenty-five. Find the probability that it is not a "
                 "multiple of four.",
            voice="default",
            subtitle=True,
            pause_after=10.0,
        )
        self.at_word(n, "turn")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "chosen")
        self.play(FadeIn(given, scale=1.03))
        self.at_word(n, "not")
        self.play(Indicate(given, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="checkpoint_02",
            text="The multiples of four are six numbers, so that probability is six twenty-fifths, and the probability of "
                 "not is one minus six twenty-fifths: nineteen twenty-fifths.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "multiples")
        self.play(FadeIn(work[0], shift=UP * 0.1))
        self.at_word(n, "minus")
        self.play(FadeIn(work[1], shift=UP * 0.1))
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
            text="Level one, question one: a die is rolled; find the probability of a number greater than two. Question "
                 "two: a number is chosen at random from one to twenty; find the probability that it is a multiple of "
                 "four.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "die")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "multiple")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="practice_02",
            text="Level two, question three: a number is chosen at random from one to fifty; find the probability that it "
                 "is a perfect square. Question four: the odds in favour of an event are five to seven; find the "
                 "probability that the event does not happen. Question five: the probability of an event is seven "
                 "twentieths; find the odds against it.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "square")
        self.play(FadeIn(rows[2], shift=RIGHT * 0.2))
        self.at_word(n, "favour")
        self.play(FadeIn(rows[3], shift=RIGHT * 0.2))
        self.at_word(n, "against")
        self.play(FadeIn(rows[4], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="practice_03",
            text="Pause the video and solve these five.",
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
        table, rows = self.practice_table(head, PRACTICE_B, 6)

        n = self.narrate(
            id="practice_04",
            text="Level three, question six: a number is chosen at random from one to thirty; find the probability that it "
                 "is prime. Question seven: a number is chosen at random from one to one hundred; find the probability "
                 "that it is divisible by neither two nor five. Question eight: a two-digit number, from ten to "
                 "ninety-nine, is chosen at random; find the probability that its two digits are equal.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "prime")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "neither")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.at_word(n, "equal")
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

        head = self.heading("Answer key  ·  1 to 4", GOOD)
        table, rows = self.answer_table(head, ANSWERS_A, 1)

        n = self.narrate(
            id="answers_01",
            text="One: three, four, five and six qualify: four sixths, two thirds.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "qualify")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "thirds")
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_02",
            text="Two: four, eight, twelve, sixteen and twenty: five twentieths, one quarter.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "twentieths")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "quarter")
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_03",
            text="Three: one, four, nine, sixteen, twenty-five, thirty-six and forty-nine are seven numbers: seven "
                 "fiftieths.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "numbers")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "fiftieths")
        self.play(FadeIn(rows[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_04",
            text="Four: the probability that it happens is five twelfths, so the probability that it does not is seven "
                 "twelfths.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "happens")
        self.play(FadeIn(rows[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "not")
        self.play(FadeIn(rows[3][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Answer key  ·  5 to 8", GOOD)
        table, rows = self.answer_table(head, ANSWERS_B, 5)

        n = self.narrate(
            id="answers_05",
            text="Five: the unfavourable outcomes are twenty minus seven, thirteen, so the odds against are thirteen to "
                 "seven.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "minus")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "against")
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_06",
            text="Six: the primes up to thirty are ten numbers: ten thirtieths, one third.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "primes")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "third")
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_07",
            text="Seven: such numbers end in one, three, seven or nine, four in every ten, so forty out of one hundred: "
                 "two fifths.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "end")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "fifths")
        self.play(FadeIn(rows[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_08",
            text="Eight: eleven, twenty-two, up to ninety-nine are nine numbers out of ninety: one tenth.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "numbers")
        self.play(FadeIn(rows[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "tenth")
        self.play(FadeIn(rows[3][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S14_answers")

    # ============================================== 15. EXAM LENS - RECOGNISE AND MOVE ==========

    def exam_lens(self):
        self.scene_start("S15_exam_lens", title="Exam Lens - Recognise and Move")

        head = self.heading("Exam lens: recognise and move")
        blocks = two_line_blocks(LENS, RATIO)
        self.stack(head, list(blocks), buff=0.6, top=0.8, align=LEFT)

        n = self.narrate(
            id="exam_lens_01",
            text="Recognise and move. The recognition cue: at random, chosen or drawn; write n of S first, then n of E.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "cue")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "write")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_lens_02",
            text="The target time: fifteen seconds, or twenty seconds when odds are involved.",
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
            text="The sanity check: the answer lies between zero and one, and P of E plus P of not E is one.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "sanity")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "between")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S15_exam_lens")

    # ============================================== 16. QUICK REVISION AND SUMMARY ==========

    def summary(self):
        self.scene_start("S16_summary", title="Quick Revision and Summary")

        head = self.heading("Quick revision")
        exp = pill("an experiment has a sample space of outcomes;    an event is a part of it", WORD, size=LABEL)
        chance = pill("equally likely outcomes:    P = favourable ÷ total,    always between 0 and 1", GOOD, size=LABEL)
        tools = VGroup(pill("complement:  when “not E” is easier to count", RATIO, size=SMALL), pill("odds a : b  →  a/(a + b)", RATIO, size=SMALL))\
            .arrange(RIGHT, buff=0.4)
        pizza = text("the pizza: equal slices, and the share with the topping", LABEL, MUTED)
        nxt = self.breadcrumb("Next", "Video 2 · Coins & Dice")
        self.stack(head, [exp, chance, tools, pizza, nxt], buff=0.6, top=0.7)
        self.no_overlap(*tools)

        n = self.narrate(
            id="summary_01",
            text="An experiment has a sample space of outcomes; an event is a part of it.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "space")
        self.play(FadeIn(exp, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_02",
            text="With equally likely outcomes, probability is favourable over total, always between zero and one.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "favourable")
        self.play(FadeIn(chance, scale=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_03",
            text="Use the complement when not E is easier to count, and turn odds of a to b into a over a plus b.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "complement")
        self.play(FadeIn(tools[0], shift=UP * 0.1))
        self.at_word(n, "odds")
        self.play(FadeIn(tools[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_04",
            text="Remember the pizza slices.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "pizza")
        self.play(FadeIn(pizza, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_05",
            text="Next: coins and dice.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Next")
        self.play(FadeIn(nxt, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S16_summary")

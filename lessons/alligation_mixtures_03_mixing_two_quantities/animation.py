"""
animation.py for the LMS video generator.

Course : Pre-C-CAT - Section A - Quantitative Aptitude
Video  : Lesson 25 - Alligation & Mixtures - 03 - Mixing Two Quantities

Source script:
  C:\\Scripts\\Section A\\Module2\\S21-25_Ratio_Age_Clock_Mixtures_Mensuration\\Lesson 25 - Allegation & Mixtures\\04 - Mixing Two Quantities.pdf

Built on the golden-reference pattern:
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``;
  * layouts stacked with next_to and guarded with ``no_overlap``; nothing is
    ever animated onto or into another box.

Lesson 25, Video 3 of 7 (the lesson's own order, from its Pre-Lesson Brief). Not the first video of the lesson: a silent
breadcrumb, a one-line recap of Video 2, then today's topic. No spoken course welcome.
The seven source scripts of this lesson are identical apart from their titles, so, as agreed with the course owner, each video was
written for its own topic. This one covers the script's "known total: scale the ratio" pattern (3 : 2 of 50 gives 30 and 20) and
its practice questions with a known total, and adds actual-amount questions: a known part, adding water or a pure ingredient,
and mixing two mixtures given as ratios. Every answer is computed with exact fractions in the data block.
The main formula stays in a panel on the left while each worked example is solved on the right.
Text colours: white and grey, one blue accent, green and red only for right and wrong.
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

from fractions import Fraction as F


def cross(low, high, m):
    """Alligation: (quantity at the low value) / (quantity at the high value) as one fraction."""
    assert F(low) < F(m) < F(high)
    return (F(high) - F(m)) / (F(m) - F(low))


def mean(q1, v1, q2, v2):
    return (F(q1) * F(v1) + F(q2) * F(v2)) / (F(q1) + F(q2))


# ---- hook, examples, patterns ----
assert cross(40, 60, 48) == F(3, 2) and (30, 20) == (50 * 3 // 5, 50 * 2 // 5) and mean(30, 40, 20, 60) == 48
assert cross(F(1, 2), F(3, 4), F(5, 8)) == 1 and mean(1, F(1, 2), 1, F(3, 4)) == F(5, 8)
assert cross(10, 50, 30) == 1 and cross(30, 45, 36) == F(3, 2) and F(18) / F(3, 2) == 12 and mean(18, 30, 12, 45) == 36
assert cross(0, 40, 30) == F(1, 3) and mean(10, 0, 30, 40) == 30
assert cross(20, 100, 36) == 4 and mean(20, 20, 5, 100) == 36
# ---- traps and checkpoint ----
assert mean(20, 40, 30, 60) == 52 and mean(3, 0, 30, 40) == F(400, 11) and cross(20, 35, 26) == F(3, 2) and mean(18, 20, 12, 35) == 26
# ---- practice ----
assert F(8) * F(3, 2) == 12 and cross(0, 20, 15) == F(1, 3) and mean(15, 0, 45, 20) == 15
assert cross(60, 90, 80) == F(1, 2) and mean(15, 60, 30, 90) == 80
assert cross(60, 100, 75) == F(5, 3) and mean(30, 60, 18, 100) == 75
assert cross(F(2, 3), F(4, 5), F(3, 4)) == F(3, 5) and mean(3, F(2, 3), 5, F(4, 5)) == F(3, 4)
assert F(30, 40 + 5) == F(2, 3)

OBJECTIVES = [("Turn an alligation ratio into actual amounts", "when the total, or one of the two parts, is known"),
              ("Add water or a pure ingredient to a mixture", "by treating it as 0% or 100%"),
              ("Mix two mixtures that are given as ratios", "by working with the fraction of one ingredient")]
STEPS_A = [("Alligation gives only a ratio", "₹40 and ₹60 making ₹48:    3 : 2;    the amounts come from one more fact"),
           ("Known total:  divide it in that ratio", "50 kg in the ratio 3 : 2:    30 kg and 20 kg"),
           ("Known part:  scale the ratio from that part", "ratio 3 : 2 with 18 kg of the cheaper:    1 part = 6 kg,  so 12 kg of the dearer"),
           ("Always say which amount belongs to which ingredient", "the first number of the ratio belongs to the first value in the cross")]
STEPS_B = [("Adding water:  water is 0%", "water to 30 L of 40% acid to make 30%:    10 : 30 = 1 : 3,  so 10 L of water"),
           ("Adding a pure ingredient:  it is 100%", "pure acid to 20 L of 20% acid to make 36%:    64 : 16 = 4 : 1,  so 5 L"),
           ("Mixtures given as ratios:  use fractions of one ingredient", "milk : water = 3 : 1 means milk is 3/4;    1 : 1 means milk is 1/2"),
           ("Then run the cross on those fractions", "3/4 and 1/2 making 5/8:    1/8 : 1/8  =  1 : 1")]
FORMULAS = ["Ratio first:      qL : qH   =   (H − M) : (M − L)",
            "Known total T:      qL  =  T × (H − M)/(H − L),        qH  =  T × (M − L)/(H − L)",
            "Known part:      1 part  =  that amount ÷ its ratio number",
            "Water  =  0%;        pure ingredient  =  100%",
            "Ratio a : b in a mixture:      the first ingredient is  a/(a + b)  of it"]
PATTERNS = [("Known total", "10% and 50% to make 30%;  total 60 L", "1 : 1 of 60 L", "30 L each"),
            ("Known part", "₹30 and ₹45 to make ₹36;  18 kg of the cheaper", "9 : 6 = 3 : 2;    1 part = 6 kg", "12 kg dearer"),
            ("Adding water", "water to 30 L of 40% acid to make 30%", "10 : 30 = 1 : 3", "10 L"),
            ("Adding pure", "pure acid to 20 L of 20% acid to make 36%", "64 : 16 = 4 : 1", "5 L"),
            ("Two mixtures", "milk 3/4 and milk 1/2 to make milk 5/8", "1/8 : 1/8", "1 : 1"),
            ("Equal parts mixed", "equal volumes of milk : water 1 : 1 and 3 : 1", "(1/2 + 3/4)/2 = 5/8 milk", "5 : 3")]
TRAPS = [("Trap 1  ·  the total divided the wrong way round",
          "₹40 and ₹60 rice makes 50 kg worth ₹48 a kg.  How much of each?",
          "20 kg at ₹40,  30 kg at ₹60", "30 kg at ₹40,  20 kg at ₹60",
          "The mean is nearer 40, so the larger share is the cheaper rice.  Check: ₹48."),
         ("Trap 2  ·  a cross on ratio numbers, not fractions",
          "Milk : water is 3 : 1 in one vessel and 1 : 1 in another.  Mix them to get 5 : 3.",
          "A cross on 3, 1 and 5", "Milk 3/4, 1/2, 5/8:   1 : 1",
          "Turn each ratio into the fraction of one ingredient before using the cross."),
         ("Trap 3  ·  water added as a percentage of the volume",
          "How much water must be added to 30 L of 40% acid to make it 30%?",
          "10% less, so 10% of 30:  3 L", "Acid stays 12 L:  40 L,  add 10 L",
          "The acid does not change.  New volume = acid ÷ new strength.")]
PRACTICE_A = [("L1", "Rice at ₹40 and ₹60 a kg is mixed to make 50 kg worth ₹48 a kg.  How many kg of each?"),
              ("L1", "10% and 50% solutions are mixed to make 60 L of a 30% solution.  How much of each?"),
              ("L2", "Two varieties are mixed in the ratio 2 : 3.  If 8 kg of the first is used, how much of the second?"),
              ("L2", "How much water must be added to 45 L of a 20% salt solution to make it 15%?"),
              ("L2", "Tea at ₹60 and ₹90 a kg is mixed to make 45 kg worth ₹80 a kg.  How many kg of each?")]
PRACTICE_B = [("L3", "How much pure milk must be added to 30 L of a mixture that is 60% milk to make it 75% milk?"),
              ("L3", "Milk : water is 2 : 1 in one vessel and 4 : 1 in another.  In what ratio must they be mixed to get 3 : 1?"),
              ("L3", "A 40 L mixture has milk and water in the ratio 3 : 1.  How much water must be added to make it 2 : 1?")]
ANSWERS_A = [("12 : 8 = 3 : 2;      50 kg in that ratio", "30 kg and 20 kg"),
             ("20 : 20 = 1 : 1;      60 L in that ratio", "30 L each"),
             ("2 parts = 8 kg,  so 1 part = 4 kg;      3 parts", "12 kg"),
             ("Water : solution  =  (20 − 15) : (15 − 0)  =  1 : 3", "15 L")]
ANSWERS_B = [("10 : 20 = 1 : 2;      45 kg in that ratio", "15 kg and 30 kg"),
             ("Mixture : pure  =  (100 − 75) : (75 − 60)  =  5 : 3;      30 L is 5 parts", "18 L"),
             ("Milk 2/3 and 4/5 making 3/4:      1/20 : 1/12", "3 : 5"),
             ("Milk is 30 L and must be 2/3 of the total:   total 45 L", "5 L")]
LENS = [("Recognition cue", "“how many kg of each”, “how much water must be added”, a total or one part given with the mean"),
        ("Target time", "40 seconds;  60 seconds for two mixtures given as ratios"),
        ("Sanity check", "the amounts add up to the total, and put back into the average they give the mean")]


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


class MixingTwoQuantitiesVideo(LMSScene):
    lesson_title = "Mixing Two Quantities"

    def construct(self):
        self.camera.background_color = BG

        self.intro()
        self.hook()
        self.objectives()
        self.why_this_matters()
        self.ratio_to_amounts()
        self.water_pure_and_ratios()
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

    # ============================================== 0. INTRO ==========
    # Not the first video: silent breadcrumb, a one-line recap of the previous video, then today's topic.

    def intro(self):
        self.scene_start("S00_intro", title="Intro")

        crumb = self.breadcrumb("Quantitative Aptitude", "Lesson 25 · Alligation & Mixtures", "Video 3 of 7")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        recap = VGroup(text("last video", SMALL, MUTED), pill("cheaper : dearer  =  (H − M) : (M − L)", WORD, size=LABEL)).arrange(DOWN, buff=0.25)
        title = fit_width(text("Mixing Two Quantities", TITLE, INK, BOLD), SAFE_W - 0.4)
        today = text("today: from the ratio to the actual amounts", LABEL, FOCUS)
        block = VGroup(recap, title, today).arrange(DOWN, buff=0.7)
        fit_within(block, SAFE_W, SAFE_H - crumb.height - 0.9)
        block.next_to(crumb, DOWN, buff=0.7)
        self.no_overlap(crumb, recap, title, today)
        self.validator.check_in_frame(VGroup(crumb, block))

        n = self.narrate(
            id="intro_01",
            text="In the last video, the alligation cross gave the ratio: H minus M to M minus L.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.at_word(n, "cross")
        self.play(FadeIn(recap, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="intro_02",
            text="Today: mixing two quantities, going from the ratio to the actual amounts.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "mixing")
        self.play(FadeIn(title, shift=UP * 0.1))
        self.at_word(n, "actual")
        self.play(FadeIn(today, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_intro")

    # ============================================== 1. HOOK ==========

    def hook(self):
        self.scene_start("S01_hook", title="Hook")

        head = self.heading("The 50 kg order")
        packs = VGroup(pill("rice at ₹40 a kg", WORD, size=LABEL), pill("rice at ₹60 a kg", WORD, size=LABEL)).arrange(RIGHT, buff=0.5)
        order = pill("An order for 50 kg of a blend worth ₹48 a kg", WORD, size=LABEL)
        ask = pill("How many kilograms of each?", FOCUS, size=BODY)
        note = text("the cross gives 3 : 2, but the customer wants kilograms, not a ratio", LABEL, INK, BOLD)
        self.stack(head, [packs, order, ask, note], buff=0.6, top=0.8)
        self.no_overlap(*packs)

        n = self.narrate(
            id="hook_01",
            text="The shop with rice at forty and sixty rupees a kilogram gets an order for fifty kilograms of a blend "
                 "worth forty-eight rupees a kilogram.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "forty")
        self.play(FadeIn(packs, shift=UP * 0.1))
        self.at_word(n, "order")
        self.play(FadeIn(order, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_02",
            text="How many kilograms of each should go in?",
            voice="default",
            subtitle=True,
            pause_after=3.0,
        )
        self.at_word(n, "each")
        self.play(FadeIn(ask, scale=1.03))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="hook_03",
            text="The cross gives three to two, but the customer wants kilograms, not a ratio.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "kilograms")
        self.play(FadeIn(note, shift=UP * 0.1))
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
            text="First, turn an alligation ratio into actual amounts when the total, or one of the two parts, is known.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "actual")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "total")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="objectives_03",
            text="Second, add water or a pure ingredient to a mixture, by treating it as zero or one hundred percent.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "water")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "treating")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="objectives_04",
            text="Third, mix two mixtures that are given as ratios, by working with the fraction of one ingredient.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "mixtures")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "fraction")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_objectives")

    # ============================================== 3. WHY THIS MATTERS ==========

    def why_this_matters(self):
        self.scene_start("S03_why_this_matters", title="Why This Matters")

        head = self.heading("Why this matters")
        ratio = text("a ratio answers “in what proportion”", LABEL, MUTED)
        real = pill("most exam questions ask “how much”", FOCUS, size=BODY)
        facts = VGroup(pill("a total is given", WORD, size=LABEL), pill("one part is given", WORD, size=LABEL),
                       pill("water or a pure ingredient is added", WORD, size=LABEL)).arrange(RIGHT, buff=0.4)
        step = text("one extra step turns the ratio into litres or kilograms", LABEL, INK, BOLD)
        self.stack(head, [ratio, real, facts, step], buff=0.75, top=1.0)
        self.no_overlap(*facts)

        n = self.narrate(
            id="why_this_matters_01",
            text="A ratio answers in what proportion, but most exam questions ask how much.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "proportion")
        self.play(FadeIn(ratio, shift=UP * 0.1))
        self.at_word(n, "much")
        self.play(FadeIn(real, scale=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="why_this_matters_02",
            text="Either a total is given, or one part is given, or water or a pure ingredient is added.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "total")
        self.play(FadeIn(facts[0], shift=UP * 0.1))
        self.at_word(n, "part")
        self.play(FadeIn(facts[1], shift=UP * 0.1))
        self.at_word(n, "water")
        self.play(FadeIn(facts[2], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="why_this_matters_03",
            text="One extra step turns the ratio into litres or kilograms.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "extra")
        self.play(FadeIn(step, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_why_this_matters")

    # ============================================== 4. CONCEPT - FROM THE RATIO TO AMOUNTS ==========

    def ratio_to_amounts(self):
        self.scene_start("S04_ratio_to_amounts", title="Concept - From the Ratio to Amounts")

        head = self.heading("From the ratio to amounts")
        blocks = two_line_blocks(STEPS_A, WORD)
        self.stack(head, list(blocks), buff=0.5, top=0.7, align=LEFT)

        n = self.narrate(
            id="ratio_to_amounts_01",
            text="Alligation gives only a ratio. Forty and sixty rupees making forty-eight give three to two; the amounts "
                 "come from one more fact.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "only")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "three")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="ratio_to_amounts_02",
            text="With a known total, divide it in that ratio. Fifty kilograms in the ratio three to two is thirty "
                 "kilograms and twenty kilograms.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "total")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "thirty")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="ratio_to_amounts_03",
            text="With a known part, scale the ratio from that part. If the ratio is three to two and there are eighteen "
                 "kilograms of the cheaper, one part is six kilograms, so the dearer is twelve kilograms.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "part")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "eighteen")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="ratio_to_amounts_04",
            text="Always say which amount belongs to which ingredient. The first number of the ratio belongs to the first "
                 "value in the cross.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "belongs")
        self.play(FadeIn(blocks[3][0], shift=RIGHT * 0.2))
        self.at_word(n, "first")
        self.play(FadeIn(blocks[3][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_ratio_to_amounts")

    # ============================================== 5. CONCEPT - WATER, PURE INGREDIENTS AND RATIOS ==========

    def water_pure_and_ratios(self):
        self.scene_start("S05_water_pure_and_ratios", title="Concept - Water, Pure Ingredients and Ratios")

        head = self.heading("Water, pure ingredients, and ratios")
        blocks = two_line_blocks(STEPS_B, WORD)
        self.stack(head, list(blocks), buff=0.5, top=0.7, align=LEFT)

        n = self.narrate(
            id="water_pure_and_ratios_01",
            text="Adding water: water is zero percent. Water added to thirty litres of forty percent acid to make thirty "
                 "percent is in the ratio ten to thirty, one to three, so ten litres of water.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "zero")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "ratio")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="water_pure_and_ratios_02",
            text="Adding a pure ingredient: it is one hundred percent. Pure acid added to twenty litres of twenty percent "
                 "acid to make thirty-six percent: the solution to the pure acid is sixty-four to sixteen, four to one, so "
                 "five litres.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "pure")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "sixty-four")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="water_pure_and_ratios_03",
            text="When mixtures are given as ratios, use the fraction of one ingredient. Milk to water three to one means "
                 "milk is three quarters; one to one means milk is one half.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "fraction")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "quarters")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="water_pure_and_ratios_04",
            text="Then run the cross on those fractions. Three quarters and one half making five eighths: one eighth to "
                 "one eighth, one to one.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "cross")
        self.play(FadeIn(blocks[3][0], shift=RIGHT * 0.2))
        self.at_word(n, "eighths")
        self.play(FadeIn(blocks[3][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_water_pure_and_ratios")

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
            text="Here is the formula box. The ratio comes first: H minus M to M minus L.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "box")
        self.play(FadeIn(box[0]))
        self.at_word(n, "ratio")
        self.play(FadeIn(lines[0], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_box_02",
            text="With a known total, each share is the total times its difference, over H minus L.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "total")
        self.play(FadeIn(lines[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_box_03",
            text="With a known part, one part is that amount divided by its ratio number.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "part")
        self.play(FadeIn(lines[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_box_04",
            text="Water is zero percent, and a pure ingredient is one hundred percent.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Water")
        self.play(FadeIn(lines[3], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_box_05",
            text="And a ratio of a to b in a mixture means the first ingredient is a over a plus b of it.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "means")
        self.play(FadeIn(lines[4], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_formula_box")

    # ============================================== 7. THE ANALOGY - A RECIPE AND A PARTY ==========

    def analogy(self):
        self.scene_start("S07_analogy", title="The Analogy - A Recipe and a Party")

        head = self.heading("A recipe, and a party")
        recipe = pill("a recipe says:  3 cups of flour to 2 cups of sugar", WORD, size=LABEL)
        need = text("the ratio is the recipe;  the order is the size of the party", LABEL, INK, BOLD)
        scale = text("for 50 cups in all:    1 share = 10 cups,   so 30 cups of flour and 20 of sugar", LABEL, GOOD, BOLD)
        stops = VGroup(text("Where the analogy stops", LABEL, BAD, BOLD),
                       text("a recipe is given to you;  in a mixture question you must find the ratio first", LABEL, INK),
                       text("so there are two steps:  the cross, then the scaling", LABEL, MUTED)).arrange(DOWN, buff=0.2)
        self.stack(head, [recipe, need, scale, stops], buff=0.55, top=0.7)

        n = self.narrate(
            id="analogy_01",
            text="Think of a recipe: three cups of flour to two cups of sugar. The ratio is the recipe, and the order is "
                 "the size of the party.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "recipe")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "three")
        self.play(FadeIn(recipe, shift=UP * 0.1))
        self.at_word(n, "party")
        self.play(FadeIn(need, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_02",
            text="For fifty cups in all, one share is ten cups, so thirty cups of flour and twenty of sugar.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "share")
        self.play(FadeIn(scale, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_03",
            text="Where the analogy stops: a recipe is given to you, but in a mixture question you must find the ratio "
                 "first. So there are two steps: the cross, then the scaling.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "stops")
        self.play(FadeIn(stops[0], shift=UP * 0.1))
        self.at_word(n, "given")
        self.play(FadeIn(stops[1], shift=UP * 0.1))
        self.at_word(n, "steps")
        self.play(FadeIn(stops[2], shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S07_analogy")

    # ============================================== 8. WORKED EXAMPLE - CLOSING THE HOOK ==========

    def hook_solved(self):
        self.scene_start("S08_hook_solved", title="Worked Example - Closing the Hook")

        head = self.heading("50 kg worth ₹48 a kg")
        panel = self.side_panel(["Cheaper : dearer  =\n(H − M) : (M − L)", "Known total:\ndivide it in that ratio"])
        steps = self.solve_steps([("Cross:    (60 − 48) : (48 − 40)  =  12 : 8", "=  3 : 2"),
                                  ("5 parts = 50 kg", "1 part = 10 kg"),
                                  ("Rice at ₹40:    3 parts", "=  30 kg"),
                                  ("Rice at ₹60:    2 parts", "=  20 kg"),
                                  ("Check:    (30 × 40 + 20 × 60)/50  =  2,400/50", "=  ₹48")])
        self.stack(head, [steps], top=0.8)
        self.no_overlap(*steps)

        n = self.narrate(
            id="hook_solved_01",
            text="The cross: sixty minus forty-eight to forty-eight minus forty, twelve to eight, three to two.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(panel, shift=RIGHT * 0.2))
        self.at_word(n, "cross")
        self.play(FadeIn(steps[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "three")
        self.play(FadeIn(steps[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_solved_02",
            text="Five parts are fifty kilograms, so one part is ten kilograms.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "parts")
        self.play(FadeIn(steps[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "ten")
        self.play(FadeIn(steps[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_solved_03",
            text="The rice at forty rupees takes three parts: thirty kilograms.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "forty")
        self.play(FadeIn(steps[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "thirty")
        self.play(FadeIn(steps[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_solved_04",
            text="The rice at sixty rupees takes two parts: twenty kilograms.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "sixty")
        self.play(FadeIn(steps[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "twenty")
        self.play(FadeIn(steps[3][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_solved_05",
            text="Check: thirty times forty plus twenty times sixty is twenty-four hundred, and divided by fifty that is "
                 "forty-eight.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Check")
        self.play(FadeIn(steps[4][:2], shift=RIGHT * 0.2))
        self.at_word(n, "divided")
        self.play(FadeIn(steps[4][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S08_hook_solved")

    # ============================================== 9. A SECOND WORKED EXAMPLE - TWO VESSELS OF MILK AND WATER ==========

    def second_example(self):
        self.scene_start("S09_second_example", title="A Second Worked Example - Two Vessels of Milk and Water")

        head = self.heading("Two vessels of milk and water")
        panel = self.side_panel(["Ratio a : b  means\nfirst part = a/(a + b)", "Then the cross\non the fractions:\n(H − M) : (M − L)"])
        ask = fitted_text("milk : water is 3 : 1 in one vessel and 1 : 1 in another:    in what ratio must they be mixed to get 5 : 3?", self.body_w() - 0.2, LABEL, MUTED, max_lines=3)
        steps = self.solve_steps([("Fraction of milk:    3/4,    1/2,    target 5/8", "in eighths:  6, 4, 5"),
                                  ("Weaker (1/2) : richer (3/4)  =  (6 − 5) : (5 − 4)", "=  1 : 1"),
                                  ("Check with 8 L of each:    milk 4 + 6 = 10 L in 16 L", "=  5/8")])
        self.stack(head, [ask, steps], buff=0.8, top=0.8)
        self.no_overlap(*steps)

        n = self.narrate(
            id="second_example_01",
            text="Milk to water is three to one in one vessel and one to one in another. In what ratio must they be mixed "
                 "to get five to three?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "vessel")
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(panel, shift=RIGHT * 0.2))
        self.at_word(n, "mixed")
        self.play(FadeIn(ask, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_02",
            text="Use the fraction of milk: three quarters, one half, and a target of five eighths. In eighths, those are "
                 "six, four and five.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "fraction")
        self.play(FadeIn(steps[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "eighths", occurrence=2)
        self.play(FadeIn(steps[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_03",
            text="So the weaker to the richer is six minus five to five minus four: one to one.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "weaker")
        self.play(FadeIn(steps[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "one")
        self.play(FadeIn(steps[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_04",
            text="Check with eight litres of each: the milk is four plus six, ten litres in sixteen, which is five "
                 "eighths.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Check")
        self.play(FadeIn(steps[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "which")
        self.play(FadeIn(steps[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S09_second_example")

    # ============================================== 10. EXAM PATTERNS - HOW THIS IS ASKED ==========

    def exam_patterns(self):
        self.scene_start("S10_exam_patterns", title="Exam Patterns - How This Is Asked")

        head = self.heading("Exam patterns  ·  1 to 3 of 6")
        blocks = self.pattern_blocks(PATTERNS[0:3])
        self.stack(head, list(blocks), buff=0.6, top=0.8, align=LEFT)

        n = self.narrate(
            id="exam_patterns_01",
            text="Exams ask this in six ways.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "six")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_02",
            text="A known total: ten percent and fifty percent making thirty percent, sixty litres in all. One to one: "
                 "thirty litres each.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "total")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "each")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_03",
            text="A known part: thirty and forty-five rupees making thirty-six, with eighteen kilograms of the cheaper. "
                 "Three to two, one part is six: twelve kilograms of the dearer.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "part")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "twelve")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_04",
            text="Adding water: water to thirty litres of forty percent acid to make thirty percent. One to three: ten "
                 "litres.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "water")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "ten")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Exam patterns  ·  4 to 6 of 6")
        blocks = self.pattern_blocks(PATTERNS[3:6])
        self.stack(head, list(blocks), buff=0.6, top=0.8, align=LEFT)

        n = self.narrate(
            id="exam_patterns_05",
            text="Adding pure: pure acid to twenty litres of twenty percent acid to make thirty-six percent. Four to one: "
                 "five litres.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "pure")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "five")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_06",
            text="Two mixtures: milk three quarters and milk one half, making milk five eighths. One eighth to one eighth: "
                 "one to one.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "mixtures")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "eighth")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_07",
            text="Equal parts mixed: equal volumes of one to one and three to one. The milk is the average of one half and "
                 "three quarters, five eighths: five to three.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Equal")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "average")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S10_exam_patterns")

    # ============================================== 11. TRAPS AND CONFUSING QUESTIONS ==========

    def traps(self):
        self.scene_start("S11_traps", title="Traps and Confusing Questions")

        head, q, wrong, right, rule = self.show_trap(TRAPS[0])

        n = self.narrate(
            id="traps_01",
            text="Trap one: the total divided the wrong way round. Forty and sixty rupee rice makes fifty kilograms worth "
                 "forty-eight: how much of each?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "wrong")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "makes")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_02",
            text="The wrong instinct gives twenty kilograms at forty and thirty at sixty. The correct answer is thirty "
                 "kilograms at forty and twenty at sixty.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "instinct")
        self.play(FadeIn(wrong, shift=UP * 0.1))
        self.at_word(n, "correct")
        self.play(FadeIn(right, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_03",
            text="The rule: the mean is nearer forty, so the larger share is the cheaper rice. Check that the blend really "
                 "costs forty-eight.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "rule")
        self.play(FadeIn(rule, shift=UP * 0.1))
        self.at_word(n, "Check")
        self.play(Indicate(rule, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)
        self.clear_stage()

        head, q, wrong, right, rule = self.show_trap(TRAPS[1])

        n = self.narrate(
            id="traps_04",
            text="Trap two: a cross on the ratio numbers instead of fractions. Milk to water is three to one in one vessel "
                 "and one to one in another: mix them to get five to three.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "numbers")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "vessel")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_05",
            text="The wrong instinct runs a cross on three, one and five. The correct working uses the milk fractions, "
                 "three quarters, one half and five eighths, and gets one to one.",
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
            text="The rule: turn each ratio into the fraction of one ingredient before using the cross.",
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
            text="Trap three: water added as a percentage of the volume. How much water must be added to thirty litres of "
                 "forty percent acid to make it thirty percent?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "percentage")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "much")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_08",
            text="The wrong instinct says ten percent less, so ten percent of thirty: three litres. The correct working "
                 "keeps the acid at twelve litres, which must be thirty percent of forty litres: add ten litres.",
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
            text="The rule: the acid does not change. The new volume is the acid divided by the new strength.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "rule")
        self.play(FadeIn(rule, shift=UP * 0.1))
        self.at_word(n, "new")
        self.play(Indicate(rule, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S11_traps")

    # ============================================== 12. CHECKPOINT ==========

    def checkpoint(self):
        self.scene_start("S12_checkpoint", title="Checkpoint")

        head = self.heading("Checkpoint  ·  your turn")
        given = pill("₹20 and ₹35 a kg make 30 kg of a mixture worth ₹26 a kg:   how many kg of each?", FOCUS, size=LABEL)
        work = VGroup(text("9 : 6  =  3 : 2;      1 part = 6 kg", BODY, INK, BOLD), text("18 kg and 12 kg", BODY, GOOD, BOLD)).arrange(RIGHT, buff=0.6)
        self.stack(head, [given, work], buff=1.0, top=1.0)
        self.no_overlap(*work)

        n = self.narrate(
            id="checkpoint_01",
            text="Your turn. Varieties at twenty and thirty-five rupees a kilogram make thirty kilograms of a mixture "
                 "worth twenty-six. How many kilograms of each?",
            voice="default",
            subtitle=True,
            pause_after=10.0,
        )
        self.at_word(n, "turn")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "Varieties")
        self.play(FadeIn(given, scale=1.03))
        self.at_word(n, "many")
        self.play(Indicate(given, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="checkpoint_02",
            text="Nine to six is three to two, and one part is six kilograms: eighteen kilograms of the cheaper and twelve "
                 "of the dearer.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Nine")
        self.play(FadeIn(work[0], shift=UP * 0.1))
        self.at_word(n, "eighteen")
        self.play(FadeIn(work[1], shift=LEFT * 0.1))
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
            text="Level one, question one: rice at forty and sixty rupees is mixed to make fifty kilograms worth "
                 "forty-eight; how many kilograms of each? Question two: ten percent and fifty percent solutions are mixed "
                 "to make sixty litres of thirty percent; how much of each?",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "rice")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "solutions")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="practice_02",
            text="Level two, question three: two varieties are mixed in the ratio two to three; if eight kilograms of the "
                 "first is used, how much of the second? Question four: how much water must be added to forty-five litres "
                 "of a twenty percent salt solution to make it fifteen percent? Question five: tea at sixty and ninety "
                 "rupees is mixed to make forty-five kilograms worth eighty; how many kilograms of each?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "varieties")
        self.play(FadeIn(rows[2], shift=RIGHT * 0.2))
        self.at_word(n, "water")
        self.play(FadeIn(rows[3], shift=RIGHT * 0.2))
        self.at_word(n, "tea")
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
            text="Level three, question six: how much pure milk must be added to thirty litres of a mixture that is sixty "
                 "percent milk to make it seventy-five percent? Question seven: milk to water is two to one in one vessel "
                 "and four to one in another; in what ratio must they be mixed to get three to one? Question eight: a "
                 "forty litre mixture has milk and water in the ratio three to one; how much water must be added to make "
                 "it two to one?",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "pure")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "vessel")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.at_word(n, "forty")
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
            text="One: three to two of fifty kilograms: thirty kilograms and twenty kilograms.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "three")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "thirty")
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_02",
            text="Two: twenty to twenty is one to one, so thirty litres each.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "twenty")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "thirty")
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_03",
            text="Three: two parts are eight kilograms, so one part is four, and three parts are twelve kilograms.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "parts")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "twelve")
        self.play(FadeIn(rows[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_04",
            text="Four: water to solution is five to fifteen, one to three, so fifteen litres of water.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "water")
        self.play(FadeIn(rows[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "litres")
        self.play(FadeIn(rows[3][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Answer key  ·  5 to 8", GOOD)
        table, rows = self.answer_table(head, ANSWERS_B, 5)

        n = self.narrate(
            id="answers_05",
            text="Five: ten to twenty is one to two of forty-five kilograms: fifteen and thirty.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "ten")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "fifteen")
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_06",
            text="Six: the mixture to the pure milk is twenty-five to fifteen, five to three. Thirty litres is five parts, "
                 "so add eighteen litres.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "mixture")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "eighteen")
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_07",
            text="Seven: the milk fractions are two thirds and four fifths, making three quarters. One twentieth to one "
                 "twelfth: three to five.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "fractions")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "three", occurrence=2)
        self.play(FadeIn(rows[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_08",
            text="Eight: the milk is thirty litres and must be two thirds of the total, so the total is forty-five: add "
                 "five litres.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "milk")
        self.play(FadeIn(rows[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "add")
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
            text="Recognise and move. The recognition cue: how many kilograms of each, or how much water must be added, "
                 "with a total or one part given.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "cue")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "many")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_lens_02",
            text="The target time: forty seconds, or sixty seconds for two mixtures given as ratios.",
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
            text="The sanity check: the amounts add up to the total, and put back into the average they give the mean.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "sanity")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "add")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S15_exam_lens")

    # ============================================== 16. QUICK REVISION AND SUMMARY ==========

    def summary(self):
        self.scene_start("S16_summary", title="Quick Revision and Summary")

        head = self.heading("Quick revision")
        main = pill("find the ratio with the cross, then scale it to the fact you are given", GOOD, size=LABEL)
        row = VGroup(pill("known total:  divide it", WORD, size=SMALL), pill("known part:  scale from it", WORD, size=SMALL),
                     pill("water 0%,  pure 100%", WORD, size=SMALL)).arrange(RIGHT, buff=0.3)
        fit_width(row, SAFE_W - 0.4)
        frac = pill("mixtures given as ratios:   use the fraction of one ingredient", RATIO, size=LABEL)
        recipe = text("the ratio is the recipe;  the total is the size of the party", LABEL, MUTED)
        nxt = self.breadcrumb("Next", "Video 4 · Replacement Problems")
        self.stack(head, [main, row, frac, recipe, nxt], buff=0.6, top=0.7)
        self.no_overlap(*row)

        n = self.narrate(
            id="summary_01",
            text="Find the ratio with the cross, then scale it to the fact you are given.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "scale")
        self.play(FadeIn(main, scale=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_02",
            text="A known total is divided in the ratio, a known part scales it, and water and pure ingredients are zero "
                 "and one hundred percent.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "total")
        self.play(FadeIn(row[0], shift=UP * 0.1))
        self.at_word(n, "part")
        self.play(FadeIn(row[1], shift=UP * 0.1))
        self.at_word(n, "water")
        self.play(FadeIn(row[2], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_03",
            text="For mixtures given as ratios, use the fraction of one ingredient.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "fraction")
        self.play(FadeIn(frac, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_04",
            text="The ratio is the recipe, and the total is the size of the party.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "recipe")
        self.play(FadeIn(recipe, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_05",
            text="Next: replacement problems.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Next")
        self.play(FadeIn(nxt, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S16_summary")

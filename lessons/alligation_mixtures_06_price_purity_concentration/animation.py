"""
animation.py for the LMS video generator.

Course : Pre-C-CAT - Section A - Quantitative Aptitude
Video  : Lesson 25 - Alligation & Mixtures - 06 - Price, Purity & Concentration

Source script:
  C:\\Scripts\\Section A\\Module2\\S21-25_Ratio_Age_Clock_Mixtures_Mensuration\\Lesson 25 - Allegation & Mixtures\\03 - Price Purity Concentration.pdf

Built on the golden-reference pattern:
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``;
  * layouts stacked with next_to and guarded with ``no_overlap``; nothing is
    ever animated onto or into another box.

Lesson 25, Video 6 of 7 (the lesson's own order, from its Pre-Lesson Brief). Not the first video of the lesson: a silent
breadcrumb, a one-line recap of Video 5, then today's topic. No spoken course welcome.
The seven source scripts of this lesson are identical apart from their titles, so, as agreed with the course owner, each video was
written for its own topic. This one builds on the script's two rules "for purity, translate percentages into actual pure
substance when the wording is complex" and "treat price, concentration or strength as a weighted average", with verified
questions on alloys, evaporation, dilution, adulteration profit, blends sold at a profit, and dried fruit.
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

# ---- hook, examples, patterns ----
FINE_GOLD = F(75, 100) * 30 + 10
assert FINE_GOLD == F(65, 2) and FINE_GOLD / 40 == F(8125, 10000)
SALT = F(5, 100) * 40
assert SALT == 2 and SALT / F(8, 100) == 25 and 40 - 25 == 15
assert F(25, 100) * 40 / F(20, 100) == 50 and 50 - 40 == 10
assert F(1, 4) == F(25, 100) and F(3 * 40 + 2 * 50, 5) == 44 and 44 * F(125, 100) == 55
assert 20 * F(10, 100) == 2 and 2 / F(80, 100) == F(5, 2)
# ---- traps and checkpoint ----
assert F(10, 100) * 60 / 40 == F(15, 100) and F(1, 5) == F(20, 100) and 20 - F(70, 100) * 20 == 6
assert F(20, 100) * 50 / 40 == F(25, 100)
# ---- practice ----
assert F(15, 100) * 200 == 30 and F(40, 100) * 30 / 40 == F(30, 100)
assert F(15, 100) * 80 / F(20, 100) == 60 and 80 - 60 == 20
assert (F(60, 100) * 40 + 10) / 50 == F(68, 100) and F(2, 10) == F(20, 100)
assert F(2 * 30 + 3 * 40, 5) == 36 and 36 * F(125, 100) == 45
assert 45 * F(20, 100) == 9 and 9 / F(90, 100) == 10 and F(20, 100) == F(1, 5)

OBJECTIVES = [("Turn every percentage into an actual amount", "and find the quantity that does not change"),
              ("Solve purity, dilution and evaporation questions", "from that unchanged amount"),
              ("Link mixtures to price and profit", "for blends sold at a profit and for milk mixed with water")]
STEPS_A = [("A percentage is a share of the whole mixture", "pure amount  =  percentage × total;    15% of 200 g of solution is 30 g of salt"),
           ("Find the quantity that does not change", "adding water or boiling it off changes the water;  the dissolved part stays the same"),
           ("New strength  =  unchanged amount ÷ new total", "2 L of salt in 40 L is 5%;    the same 2 L in 25 L is 8%"),
           ("Purity of an alloy:  add the pure amounts", "then divide by the total weight;    pure metal counts as 100%")]
STEPS_B = [("A blend sold at a profit:  find its cost first", "cost of the blend  =  weighted average;    selling price  =  cost × (1 + profit rate)"),
           ("Water costs nothing", "milk mixed with water and sold at the cost price of milk:  the water is the profit"),
           ("Profit percent  =  water ÷ milk × 100", "1 L of water in 4 L of milk:    1/4  =  25%,    not 1/5"),
           ("Drying:  the solid part does not change", "fresh fruit that is 90% water is 10% pulp;  the pulp is the same before and after")]
FORMULAS = ["Pure amount   =   percentage × total quantity",
            "Water added or evaporated:      new strength  =  (unchanged amount) ÷ (new total)",
            "Purity of an alloy   =   total pure metal ÷ total weight",
            "Blend sold at a profit:      selling price  =  (weighted-average cost) × (1 + profit rate)",
            "Milk and water sold at the cost price of milk:      profit %  =  water ÷ milk × 100"]
PATTERNS = [("Alloy", "30 g of 75% gold melted with 10 g of pure gold", "(22.5 + 10)/40", "81.25%"),
            ("Evaporation", "40 L of 5% salt solution boiled down to 8%", "2 L of salt ÷ 8%  =  25 L", "15 L of water"),
            ("Dilution", "water added to 40 L of 25% acid to make it 20%", "10 L of acid ÷ 20%  =  50 L", "10 L"),
            ("Milk and water", "1 L of water in 4 L of milk, sold at the cost price", "water ÷ milk  =  1/4", "25% profit"),
            ("Blend at a profit", "₹40 and ₹50 tea mixed 3 : 2, sold at 25% profit", "cost ₹44;    44 × 1.25", "₹55 a kg"),
            ("Dried fruit", "20 kg of fresh fruit, 90% water, dried to 20% water", "pulp 2 kg  =  80% of the dry weight", "2.5 kg")]
TRAPS = [("Trap 1  ·  the dissolved part treated as if it boils away",
          "20 L of water evaporates from 60 L of a 10% sugar solution.  Find the new strength.",
          "Still 10%", "6 L in 40 L  =  15%",
          "Only the water leaves.  The sugar stays, so the strength rises."),
         ("Trap 2  ·  profit worked out on the total",
          "1 L of water is added to 4 L of milk and sold at the cost price of milk.  Profit percent?",
          "1/5  =  20%", "1/4  =  25%",
          "Profit percent is on what you paid for.  You paid for 4 L of milk, not 5 L."),
         ("Trap 3  ·  the percentage of water subtracted from the weight",
          "20 kg of fresh fruit that is 90% water is dried until it is 20% water.  Find its weight.",
          "20 − 70% of 20  =  6 kg", "pulp 2 kg ÷ 0.8  =  2.5 kg",
          "The two percentages are of different totals.  Track the pulp, which does not change.")]
PRACTICE_A = [("L1", "How much salt is there in 200 g of a 15% salt solution?"),
              ("L1", "10 L of water is added to 30 L of a 40% acid solution.  Find the new strength."),
              ("L2", "How much water must evaporate from 80 L of a 15% sugar solution to make it 20%?"),
              ("L2", "40 g of an alloy that is 60% silver is melted with 10 g of pure silver.  Find the purity of the new alloy."),
              ("L2", "A milkman adds 2 L of water to 10 L of milk and sells the mixture at the cost price of milk.  Find his profit percent.")]
PRACTICE_B = [("L3", "Tea at ₹30 and ₹40 a kg is mixed in the ratio 2 : 3 and sold at a profit of 25%.  Find the selling price per kg."),
              ("L3", "Fresh grapes are 80% water and dried grapes are 10% water.  How much dried grapes come from 45 kg of fresh grapes?"),
              ("L3", "In what ratio must water be mixed with milk to gain 20% by selling the mixture at the cost price of milk?")]
ANSWERS_A = [("15% of 200 g", "30 g"),
             ("Acid 12 L   in 40 L", "30%"),
             ("Sugar 12 L;      12 ÷ 20%  =  60 L;      80 − 60", "20 L"),
             ("Silver  24 + 10 = 34 g   in 50 g", "68%")]
ANSWERS_B = [("Water ÷ milk  =  2/10", "20%"),
             ("Cost  (60 + 120)/5 = ₹36;      36 × 1.25", "₹45 a kg"),
             ("Pulp  20% of 45 = 9 kg;      9 kg is 90% of the dry weight", "10 kg"),
             ("Water ÷ milk  =  20/100", "1 : 5")]
LENS = [("Recognition cue", "“percent pure”, “evaporated”, “diluted”, “sold at cost price”, “fresh and dried”, “gain percent”"),
        ("Target time", "40 to 50 seconds"),
        ("Sanity check", "adding water lowers the strength, removing water raises it;  the unchanged amount is the same at the end")]


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


class PricePurityConcentrationVideo(LMSScene):
    lesson_title = "Price, Purity & Concentration"

    def construct(self):
        self.camera.background_color = BG

        self.intro()
        self.hook()
        self.objectives()
        self.why_this_matters()
        self.unchanged_amount()
        self.price_and_profit()
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

        crumb = self.breadcrumb("Quantitative Aptitude", "Lesson 25 · Alligation & Mixtures", "Video 6 of 7")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        recap = VGroup(text("last video", SMALL, MUTED), pill("after n rounds:  V × (1 − x/V)^n  is left", WORD, size=LABEL)).arrange(DOWN, buff=0.25)
        title = fit_width(text("Price, Purity & Concentration", TITLE, INK, BOLD), SAFE_W - 0.4)
        today = text("today: find the amount that does not change", LABEL, FOCUS)
        block = VGroup(recap, title, today).arrange(DOWN, buff=0.7)
        fit_within(block, SAFE_W, SAFE_H - crumb.height - 0.9)
        block.next_to(crumb, DOWN, buff=0.7)
        self.no_overlap(crumb, recap, title, today)
        self.validator.check_in_frame(VGroup(crumb, block))

        n = self.narrate(
            id="intro_01",
            text="In the last video, repeated replacement left the fraction that stays, raised to the power n.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.at_word(n, "power")
        self.play(FadeIn(recap, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="intro_02",
            text="Today: price, purity and concentration, where the key is to find the amount that does not change.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "price")
        self.play(FadeIn(title, shift=UP * 0.1))
        self.at_word(n, "change")
        self.play(FadeIn(today, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_intro")

    # ============================================== 1. HOOK ==========

    def hook(self):
        self.scene_start("S01_hook", title="Hook")

        head = self.heading("The jeweller's furnace")
        melt = VGroup(pill("30 g of gold that is 75% pure", WORD, size=LABEL), pill("10 g of pure gold", WORD, size=LABEL)).arrange(RIGHT, buff=0.5)
        ask = pill("How pure is the new piece?", FOCUS, size=BODY)
        guess = text("it is not 75% + 100%, and it is not halfway either", LABEL, MUTED)
        way = text("count the actual gold, then divide by the total weight", LABEL, INK, BOLD)
        self.stack(head, [melt, ask, guess, way], buff=0.6, top=0.8)
        self.no_overlap(*melt)

        n = self.narrate(
            id="hook_01",
            text="A jeweller melts thirty grams of gold that is seventy-five percent pure together with ten grams of pure "
                 "gold.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "thirty")
        self.play(FadeIn(melt[0], shift=UP * 0.1))
        self.at_word(n, "ten")
        self.play(FadeIn(melt[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_02",
            text="How pure is the new piece?",
            voice="default",
            subtitle=True,
            pause_after=3.0,
        )
        self.at_word(n, "pure")
        self.play(FadeIn(ask, scale=1.03))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="hook_03",
            text="It is not seventy-five plus one hundred, and it is not halfway either. Count the actual gold, then "
                 "divide by the total weight.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "halfway")
        self.play(FadeIn(guess, shift=UP * 0.1))
        self.at_word(n, "actual")
        self.play(FadeIn(way, shift=UP * 0.1))
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
            text="First, turn every percentage into an actual amount, and find the quantity that does not change.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "actual")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "change")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="objectives_03",
            text="Second, solve purity, dilution and evaporation questions from that unchanged amount.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "purity")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "unchanged")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="objectives_04",
            text="Third, link mixtures to price and profit, for blends sold at a profit and for milk mixed with water.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "profit")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "blends")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_objectives")

    # ============================================== 3. WHY THIS MATTERS ==========

    def why_this_matters(self):
        self.scene_start("S03_why_this_matters", title="Why This Matters")

        head = self.heading("Why this matters")
        word = text("these questions are wordy:  alloys, syrups, dried fruit, a milkman's profit", LABEL, MUTED)
        same = pill("each one becomes simple once percentages are turned into amounts", FOCUS, size=LABEL)
        ask = text("then one question settles it:  what stays the same?", LABEL, INK, BOLD)
        self.stack(head, [word, same, ask], buff=0.9, top=1.2)

        n = self.narrate(
            id="why_this_matters_01",
            text="These questions are wordy: alloys, syrups, dried fruit, a milkman's profit.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "wordy")
        self.play(FadeIn(word, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="why_this_matters_02",
            text="Each one becomes simple once the percentages are turned into actual amounts.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "simple")
        self.play(FadeIn(same, scale=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="why_this_matters_03",
            text="Then one question settles it: what stays the same?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "stays")
        self.play(FadeIn(ask, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_why_this_matters")

    # ============================================== 4. CONCEPT - THE AMOUNT THAT DOES NOT CHANGE ==========

    def unchanged_amount(self):
        self.scene_start("S04_unchanged_amount", title="Concept - The Amount That Does Not Change")

        head = self.heading("The amount that does not change")
        blocks = two_line_blocks(STEPS_A, WORD)
        self.stack(head, list(blocks), buff=0.5, top=0.7, align=LEFT)

        n = self.narrate(
            id="unchanged_amount_01",
            text="A percentage is a share of the whole mixture, so the pure amount is the percentage times the total. "
                 "Fifteen percent of two hundred grams of solution is thirty grams of salt.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "share")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "thirty")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="unchanged_amount_02",
            text="Find the quantity that does not change. Adding water or boiling it off changes the water; the dissolved "
                 "part stays the same.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "change")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "dissolved")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="unchanged_amount_03",
            text="The new strength is the unchanged amount divided by the new total. Two litres of salt in forty litres is "
                 "five percent; the same two litres in twenty-five litres is eight percent.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "strength")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "same")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="unchanged_amount_04",
            text="For the purity of an alloy, add the pure amounts, then divide by the total weight. Pure metal counts as "
                 "one hundred percent.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "alloy")
        self.play(FadeIn(blocks[3][0], shift=RIGHT * 0.2))
        self.at_word(n, "weight")
        self.play(FadeIn(blocks[3][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_unchanged_amount")

    # ============================================== 5. CONCEPT - PRICE, PROFIT AND DRYING ==========

    def price_and_profit(self):
        self.scene_start("S05_price_and_profit", title="Concept - Price, Profit and Drying")

        head = self.heading("Price, profit, and drying")
        blocks = two_line_blocks(STEPS_B, WORD)
        self.stack(head, list(blocks), buff=0.5, top=0.7, align=LEFT)

        n = self.narrate(
            id="price_and_profit_01",
            text="For a blend sold at a profit, find its cost first. The cost of the blend is the weighted average, and "
                 "the selling price is the cost times one plus the profit rate.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "cost")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "weighted")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="price_and_profit_02",
            text="Water costs nothing. When milk is mixed with water and sold at the cost price of milk, the water is the "
                 "profit.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "nothing")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "profit")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="price_and_profit_03",
            text="So the profit percent is water divided by milk, times one hundred. One litre of water in four litres of "
                 "milk is one quarter, twenty-five percent, not one fifth.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "divided")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "quarter")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="price_and_profit_04",
            text="In drying, the solid part does not change. Fresh fruit that is ninety percent water is ten percent pulp, "
                 "and the pulp is the same before and after.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "solid")
        self.play(FadeIn(blocks[3][0], shift=RIGHT * 0.2))
        self.at_word(n, "pulp")
        self.play(FadeIn(blocks[3][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_price_and_profit")

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
            text="Here is the formula box. The pure amount is the percentage times the total quantity.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "box")
        self.play(FadeIn(box[0]))
        self.at_word(n, "pure")
        self.play(FadeIn(lines[0], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_box_02",
            text="When water is added or evaporated, the new strength is the unchanged amount over the new total.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "water")
        self.play(FadeIn(lines[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_box_03",
            text="The purity of an alloy is the total pure metal over the total weight.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "alloy")
        self.play(FadeIn(lines[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_box_04",
            text="A blend sold at a profit sells at its weighted-average cost times one plus the profit rate.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "blend")
        self.play(FadeIn(lines[3], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_box_05",
            text="And milk and water sold at the cost price of milk gives a profit percent of water over milk, times one "
                 "hundred.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "milk")
        self.play(FadeIn(lines[4], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_formula_box")

    # ============================================== 7. THE ANALOGY - SALT IN A POT OF SOUP ==========

    def analogy(self):
        self.scene_start("S07_analogy", title="The Analogy - Salt in a Pot of Soup")

        head = self.heading("Salt in a pot of soup")
        pot = pill("a pot of soup has two spoons of salt in it", WORD, size=LABEL)
        boil = text("boil it down and it tastes saltier;  add water and it tastes weaker", LABEL, INK)
        same = text("the two spoons of salt never changed:  only the amount of soup did", LABEL, GOOD, BOLD)
        stops = VGroup(text("Where the analogy stops", LABEL, BAD, BOLD),
                       text("when you add pure gold or pure acid, the pure amount does change", LABEL, INK),
                       text("then add the new pure amount first, and divide by the new total", LABEL, MUTED)).arrange(DOWN, buff=0.2)
        self.stack(head, [pot, boil, same, stops], buff=0.55, top=0.7)

        n = self.narrate(
            id="analogy_01",
            text="Think of a pot of soup with two spoons of salt in it. Boil it down and it tastes saltier; add water and "
                 "it tastes weaker.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "soup")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "spoons")
        self.play(FadeIn(pot, shift=UP * 0.1))
        self.at_word(n, "saltier")
        self.play(FadeIn(boil, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_02",
            text="The two spoons of salt never changed: only the amount of soup did.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "never")
        self.play(FadeIn(same, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_03",
            text="Where the analogy stops: when you add pure gold or pure acid, the pure amount does change. Then add the "
                 "new pure amount first, and divide by the new total.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "stops")
        self.play(FadeIn(stops[0], shift=UP * 0.1))
        self.at_word(n, "does")
        self.play(FadeIn(stops[1], shift=UP * 0.1))
        self.at_word(n, "divide")
        self.play(FadeIn(stops[2], shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S07_analogy")

    # ============================================== 8. WORKED EXAMPLE - CLOSING THE HOOK ==========

    def hook_solved(self):
        self.scene_start("S08_hook_solved", title="Worked Example - Closing the Hook")

        head = self.heading("30 g of 75% gold, with 10 g of pure gold")
        panel = self.side_panel(["Pure amount  =\npercentage × total", "Purity  =\ntotal pure metal\n÷ total weight"])
        steps = self.solve_steps([("Gold in the first piece:    75% of 30 g", "=  22.5 g"),
                                  ("Add the pure gold:    22.5 + 10", "=  32.5 g of gold"),
                                  ("Total weight:    30 + 10", "=  40 g"),
                                  ("Purity:    32.5 ÷ 40", "=  81.25%")])
        self.stack(head, [steps], top=1.0)
        self.no_overlap(*steps)

        n = self.narrate(
            id="hook_solved_01",
            text="The gold in the first piece is seventy-five percent of thirty grams: twenty-two and a half grams.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(panel, shift=RIGHT * 0.2))
        self.at_word(n, "first")
        self.play(FadeIn(steps[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "twenty-two")
        self.play(FadeIn(steps[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_solved_02",
            text="Add the ten grams of pure gold: thirty-two and a half grams of gold.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Add")
        self.play(FadeIn(steps[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "thirty-two")
        self.play(FadeIn(steps[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_solved_03",
            text="The total weight is thirty plus ten, forty grams.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "weight")
        self.play(FadeIn(steps[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "forty")
        self.play(FadeIn(steps[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_solved_04",
            text="So the purity is thirty-two and a half over forty: eighty-one and a quarter percent.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "purity")
        self.play(FadeIn(steps[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "eighty-one")
        self.play(FadeIn(steps[3][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S08_hook_solved")

    # ============================================== 9. A SECOND WORKED EXAMPLE - BOILING A SOLUTION DOWN ==========

    def second_example(self):
        self.scene_start("S09_second_example", title="A Second Worked Example - Boiling a Solution Down")

        head = self.heading("Boiling a solution down")
        panel = self.side_panel(["The salt does not change", "New total  =\nsalt ÷ new strength"])
        ask = fitted_text("how much water must evaporate from 40 L of a 5% salt solution to make it an 8% solution?", self.body_w() - 0.2, LABEL, MUTED, max_lines=3)
        steps = self.solve_steps([("Salt:    5% of 40 L", "=  2 L,  and it does not change"),
                                  ("At 8%, the 2 L of salt is 8% of the new total:    2 ÷ 0.08", "=  25 L"),
                                  ("Water to evaporate:    40 − 25", "=  15 L"),
                                  ("Check:    2 L in 25 L", "=  8%")])
        self.stack(head, [ask, steps], buff=0.7, top=0.7)
        self.no_overlap(*steps)

        n = self.narrate(
            id="second_example_01",
            text="How much water must evaporate from forty litres of a five percent salt solution to make it an eight "
                 "percent solution?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "evaporate")
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(panel, shift=RIGHT * 0.2))
        self.at_word(n, "solution")
        self.play(FadeIn(ask, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_02",
            text="The salt is five percent of forty litres, two litres, and it does not change.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "salt")
        self.play(FadeIn(steps[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "change")
        self.play(FadeIn(steps[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_03",
            text="At eight percent, those two litres are eight percent of the new total, so the new total is two divided "
                 "by zero point zero eight: twenty-five litres.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "total")
        self.play(FadeIn(steps[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "twenty-five")
        self.play(FadeIn(steps[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_04",
            text="So the water to evaporate is forty minus twenty-five: fifteen litres.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "minus")
        self.play(FadeIn(steps[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "fifteen")
        self.play(FadeIn(steps[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_05",
            text="Check: two litres in twenty-five is eight percent.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Check")
        self.play(FadeIn(steps[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "eight")
        self.play(FadeIn(steps[3][2], shift=LEFT * 0.1))
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
            text="An alloy: thirty grams of seventy-five percent gold with ten grams of pure gold. Thirty-two and a half "
                 "grams in forty: eighty-one and a quarter percent.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "alloy")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "forty")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_03",
            text="Evaporation: forty litres of five percent salt solution boiled down to eight percent. Two litres of salt "
                 "needs twenty-five litres, so fifteen litres of water goes.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Evaporation")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "needs")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_04",
            text="Dilution: water added to forty litres of twenty-five percent acid to make it twenty percent. Ten litres "
                 "of acid needs fifty litres: add ten litres.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Dilution")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "needs")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Exam patterns  ·  4 to 6 of 6")
        blocks = self.pattern_blocks(PATTERNS[3:6])
        self.stack(head, list(blocks), buff=0.6, top=0.8, align=LEFT)

        n = self.narrate(
            id="exam_patterns_05",
            text="Milk and water: one litre of water in four litres of milk, sold at the cost price. Water over milk is "
                 "one quarter: twenty-five percent profit.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "water")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "quarter")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_06",
            text="A blend at a profit: forty and fifty rupee tea mixed three to two, sold at twenty-five percent profit. "
                 "The cost is forty-four rupees, so the price is fifty-five.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "blend")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "cost")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_07",
            text="Dried fruit: twenty kilograms of fresh fruit, ninety percent water, dried to twenty percent water. The "
                 "pulp, two kilograms, is eighty percent of the dry weight: two and a half kilograms.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Dried")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "pulp")
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
            text="Trap one: the dissolved part treated as if it boils away. Twenty litres of water evaporates from sixty "
                 "litres of a ten percent sugar solution: find the new strength.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "dissolved")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "evaporates")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_02",
            text="The wrong instinct says it is still ten percent. The correct answer is six litres of sugar in forty "
                 "litres: fifteen percent.",
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
            text="The rule: only the water leaves. The sugar stays, so the strength rises.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "rule")
        self.play(FadeIn(rule, shift=UP * 0.1))
        self.at_word(n, "rises")
        self.play(Indicate(rule, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)
        self.clear_stage()

        head, q, wrong, right, rule = self.show_trap(TRAPS[1])

        n = self.narrate(
            id="traps_04",
            text="Trap two: profit worked out on the total. One litre of water is added to four litres of milk and sold at "
                 "the cost price of milk: what is the profit percent?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "total")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "added")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_05",
            text="The wrong instinct says one fifth, twenty percent. The correct answer is one quarter, twenty-five "
                 "percent.",
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
            text="The rule: profit percent is on what you paid for. You paid for four litres of milk, not five.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "rule")
        self.play(FadeIn(rule, shift=UP * 0.1))
        self.at_word(n, "paid", occurrence=2)
        self.play(Indicate(rule, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)
        self.clear_stage()

        head, q, wrong, right, rule = self.show_trap(TRAPS[2])

        n = self.narrate(
            id="traps_07",
            text="Trap three: the percentage of water subtracted from the weight. Twenty kilograms of fresh fruit that is "
                 "ninety percent water is dried until it is twenty percent water: find its weight.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "subtracted")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "dried")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_08",
            text="The wrong instinct removes seventy percent of twenty kilograms and gets six kilograms. The correct "
                 "working divides the two kilograms of pulp by zero point eight: two and a half kilograms.",
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
            text="The rule: the two percentages are of different totals. Track the pulp, which does not change.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "rule")
        self.play(FadeIn(rule, shift=UP * 0.1))
        self.at_word(n, "pulp")
        self.play(Indicate(rule, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S11_traps")

    # ============================================== 12. CHECKPOINT ==========

    def checkpoint(self):
        self.scene_start("S12_checkpoint", title="Checkpoint")

        head = self.heading("Checkpoint  ·  your turn")
        given = pill("10 L of water evaporates from 50 L of a 20% sugar solution:   the new strength?", FOCUS, size=LABEL)
        work = VGroup(text("sugar 10 L,  now in 40 L", BODY, INK, BOLD), text("=  25%", BODY, GOOD, BOLD)).arrange(RIGHT, buff=0.6)
        self.stack(head, [given, work], buff=1.0, top=1.0)
        self.no_overlap(*work)

        n = self.narrate(
            id="checkpoint_01",
            text="Your turn. Ten litres of water evaporates from fifty litres of a twenty percent sugar solution. What is "
                 "the new strength?",
            voice="default",
            subtitle=True,
            pause_after=10.0,
        )
        self.at_word(n, "turn")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "Ten")
        self.play(FadeIn(given, scale=1.03))
        self.at_word(n, "new")
        self.play(Indicate(given, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="checkpoint_02",
            text="The sugar is ten litres, now in forty litres: twenty-five percent.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "sugar")
        self.play(FadeIn(work[0], shift=UP * 0.1))
        self.at_word(n, "twenty-five")
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
            text="Level one, question one: how much salt is there in two hundred grams of a fifteen percent salt solution? "
                 "Question two: ten litres of water is added to thirty litres of a forty percent acid solution; find the "
                 "new strength.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "salt")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "water")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="practice_02",
            text="Level two, question three: how much water must evaporate from eighty litres of a fifteen percent sugar "
                 "solution to make it twenty percent? Question four: forty grams of an alloy that is sixty percent silver "
                 "is melted with ten grams of pure silver; find the purity of the new alloy. Question five: a milkman adds "
                 "two litres of water to ten litres of milk and sells the mixture at the cost price of milk; find his "
                 "profit percent.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "evaporate")
        self.play(FadeIn(rows[2], shift=RIGHT * 0.2))
        self.at_word(n, "alloy")
        self.play(FadeIn(rows[3], shift=RIGHT * 0.2))
        self.at_word(n, "milkman")
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
            text="Level three, question six: tea at thirty and forty rupees a kilogram is mixed in the ratio two to three "
                 "and sold at a profit of twenty-five percent; find the selling price. Question seven: fresh grapes are "
                 "eighty percent water and dried grapes are ten percent water; how much dried grapes come from forty-five "
                 "kilograms of fresh grapes? Question eight: in what ratio must water be mixed with milk to gain twenty "
                 "percent by selling the mixture at the cost price of milk?",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "tea")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "grapes")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.at_word(n, "gain")
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
            text="One: fifteen percent of two hundred grams: thirty grams.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "percent")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "thirty")
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_02",
            text="Two: the acid is twelve litres, now in forty litres: thirty percent.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "acid")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "thirty")
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_03",
            text="Three: the sugar is twelve litres, which is twenty percent of sixty litres, so twenty litres must "
                 "evaporate.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "sugar")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "must")
        self.play(FadeIn(rows[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_04",
            text="Four: the silver is twenty-four plus ten, thirty-four grams in fifty: sixty-eight percent.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "silver")
        self.play(FadeIn(rows[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "sixty-eight")
        self.play(FadeIn(rows[3][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Answer key  ·  5 to 8", GOOD)
        table, rows = self.answer_table(head, ANSWERS_B, 5)

        n = self.narrate(
            id="answers_05",
            text="Five: water over milk is two tenths: twenty percent.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "over")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "twenty")
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_06",
            text="Six: the cost is sixty plus one hundred and twenty, over five, thirty-six rupees. Times one point two "
                 "five: forty-five rupees a kilogram.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "cost")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "forty-five")
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_07",
            text="Seven: the pulp is twenty percent of forty-five, nine kilograms, and that is ninety percent of the dry "
                 "weight: ten kilograms.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "pulp")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "ten")
        self.play(FadeIn(rows[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_08",
            text="Eight: water over milk must be twenty over one hundred: one to five.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "over")
        self.play(FadeIn(rows[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "five")
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
            text="Recognise and move. The recognition cue: percent pure, evaporated, diluted, sold at cost price, fresh "
                 "and dried, or gain percent.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "cue")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "pure")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_lens_02",
            text="The target time: forty to fifty seconds.",
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
            text="The sanity check: adding water lowers the strength and removing water raises it, and the unchanged "
                 "amount is the same at the end.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "sanity")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "lowers")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S15_exam_lens")

    # ============================================== 16. QUICK REVISION AND SUMMARY ==========

    def summary(self):
        self.scene_start("S16_summary", title="Quick Revision and Summary")

        head = self.heading("Quick revision")
        main = pill("turn percentages into amounts, then find what does not change", GOOD, size=LABEL)
        row = VGroup(pill("new strength  =  unchanged ÷ new total", WORD, size=SMALL), pill("alloy:  pure metal ÷ weight", WORD, size=SMALL))\
            .arrange(RIGHT, buff=0.4)
        money = VGroup(pill("blend:  cost first, then profit", RATIO, size=SMALL), pill("milk and water:  profit % = water ÷ milk", RATIO, size=SMALL))\
            .arrange(RIGHT, buff=0.4)
        soup = text("the soup:  the salt in the pot never changes", LABEL, MUTED)
        nxt = self.breadcrumb("Next", "Video 7 · Speed Tricks")
        self.stack(head, [main, row, money, soup, nxt], buff=0.6, top=0.7)
        self.no_overlap(*row)
        self.no_overlap(*money)

        n = self.narrate(
            id="summary_01",
            text="Turn percentages into amounts, then find what does not change.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "amounts")
        self.play(FadeIn(main, scale=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_02",
            text="The new strength is the unchanged amount over the new total, and an alloy's purity is its pure metal "
                 "over its weight.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "strength")
        self.play(FadeIn(row[0], shift=UP * 0.1))
        self.at_word(n, "alloy's")
        self.play(FadeIn(row[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_03",
            text="For a blend, find the cost first and then the profit; for milk and water, the profit percent is water "
                 "over milk.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "blend")
        self.play(FadeIn(money[0], shift=UP * 0.1))
        self.at_word(n, "water")
        self.play(FadeIn(money[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_04",
            text="Remember the soup: the salt in the pot never changes.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "soup")
        self.play(FadeIn(soup, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_05",
            text="Next: speed tricks for alligation and mixtures.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Next")
        self.play(FadeIn(nxt, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S16_summary")

"""
animation.py for the LMS video generator.

Course : Pre-C-CAT - Section A - Quantitative Aptitude
Video  : Lesson 20 - Partnership - 01 - Simple & Compound Partnership

Source script:
  C:\\Scripts\\Section A\\Aptitude\\Sessions 13-18 - Pipes, Time Distance, Partnership\\Lesson 20 - Partnership\\01 - Simple & Compound Partnership.pdf

Built on the golden-reference pattern:
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``;
  * layouts stacked with next_to and guarded with ``no_overlap``; nothing is
    ever animated onto or into another box.

Lesson 20, Video 1 of 4. First video of the lesson: a silent breadcrumb, "Now we start lesson twenty", a one-line recap of Lesson 19, then today's topic. No spoken course welcome.
The narration follows the script section by section. Amounts keep the script's Indian grouping (3,00,000) and are spoken as lakh. The seven concept steps are split over two screens; the six exam patterns are two-line blocks. The formula box is written in words (no subscripts). Two bars of equal area (capital x months) are drawn beside the hook's solution.
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


def shares(amount, *partners):
    """partners: (capital, months).  Returns each partner's share of ``amount`` in the ratio of capital × months."""
    weights = [c * m for c, m in partners]
    return [Fraction(amount * w, sum(weights)) for w in weights]


# ---- the hook: Asha 3,00,000 × 12, Ravi 4,50,000 × 8, profit 1,20,000 ----
assert 300000 * 12 == 450000 * 8 == 3600000 and shares(120000, (300000, 12), (450000, 8)) == [60000, 60000]
assert shares(120000, (300000, 1), (450000, 1)) == [48000, 72000] and 72000 - 60000 == 12000

# ---- second worked example: finding the time ----
assert 28000 - 12000 == 16000 and Fraction(16, 12) == Fraction(4, 3) and shares(28000, (40000, 12), (60000, 6)) == [16000, 12000]
assert 480000 * 3 == 4 * 60000 * 6 == 1440000 and Fraction(480000, 360000) == Fraction(4, 3)

# ---- exam patterns, traps, checkpoint, practice (answers computed) ----
assert shares(15000, (20000, 1), (30000, 1)) == [6000, 9000] and shares(12500, (15000, 8), (20000, 9)) == [5000, 7500]
assert (15000 * 8, 20000 * 9) == (120000, 180000) and shares(9600, (50000, 1), (70000, 1)) == [4000, 5600]
assert 24000 * Fraction(5, 3) == 40000 and Fraction(2, 4) / Fraction(3, 9) == Fraction(3, 2)
assert 10000 * 12 == 15000 * 8 and shares(7500, (12000, 1), (18000, 1))[0] == 3000
assert shares(18000, (25000, 12), (35000, 12)) == [7500, 10500] and 16000 * 9 == 12000 * 12 == 144000
assert shares(39000, (20000, 12), (30000, 8), (50000, 6)) == [12000, 12000, 15000] and shares(6300, (40000, 1), (50000, 1)) == [2800, 3500]
assert 45000 * Fraction(3, 5) == 27000 and Fraction(5, 3) / Fraction(4, 2) == Fraction(5, 6) and Fraction(3 * 10, 2 * 12) == Fraction(5, 4)
assert shares(21000, (30000, 12), (45000, 4)) == [14000, 7000] and shares(110000, (120000, 10), (150000, 8), (180000, 5))[2] == 30000

OBJECTIVES = [("Share a profit or a loss in the ratio of capitals", "when the time is the same"),
              ("Share it in the ratio of capital × time", "when the times differ"),
              ("Work backwards from a profit ratio", "to an unknown capital or an unknown time")]
STEPS_A = [("A partnership pools capital", "two or more people invest in one business and share its profit or loss;  the share follows capital × time"),
           ("Same time:  simple partnership", "time cancels:  profit ratio = capital ratio"),
           ("Different times:  compound partnership", "multiply each capital by its months:  the capital-months (rupee-months) give the profit ratio"),
           ("A loss is shared the same way", "the ratio does not care whether the result is a profit or a loss")]
STEPS_B = [("One partner's share = own parts ÷ total parts × profit", "simplify the ratio first:  cancel common zeros and factors"),
           ("Working backwards:  divide, don't multiply", "capital follows profit ÷ time;     time follows profit ÷ capital"),
           ("Keep the units the same", "convert every period to months before multiplying:  1 year = 12 months")]
FORMULAS = ["Same time:       profit ratio  =  capital ratio",
            "Different times:       profit ratio  =  ratio of (capital × time)",
            "Capital ratio  =  ratio of (profit ÷ time)                  Time ratio  =  ratio of (profit ÷ capital)",
            "Share   =   (own parts ÷ total parts) × profit    (or loss)"]
PATTERNS = [("Same time", "A ₹20,000, B ₹30,000;   profit ₹15,000", "2 : 3", "₹6,000 and ₹9,000"),
            ("Different times", "A ₹15,000 for 8 months, B ₹20,000 for 9 months;   profit ₹12,500", "1,20,000 : 1,80,000 = 2 : 3", "₹5,000 and ₹7,500"),
            ("Loss", "A ₹50,000, B ₹70,000, same time;   loss ₹9,600", "5 : 7", "₹4,000 and ₹5,600"),
            ("Capital from profit", "same time;   profits 3 : 5;   A invested ₹24,000", "24,000 × 5/3", "B:  ₹40,000"),
            ("Capital ratio from profit and time", "profits 2 : 3;   times 4 and 9 months", "2/4 : 3/9 = 1/2 : 1/3", "3 : 2"),
            ("Time from a share", "A ₹40,000 for 12 months;   B ₹60,000;   profits 4 : 3", "4,80,000 : 60,000t = 4 : 3", "B:  6 months")]
TRAPS = [("Trap 1  ·  ignoring time", "₹3,00,000 for 12 months and ₹4,50,000 for 8 months.  Profit ratio?",
          "3 : 4.5  =  2 : 3", "36,00,000 : 36,00,000 = 1 : 1",
          "When the periods differ, multiply capital by months before forming the ratio."),
         ("Trap 2  ·  multiplying when working backwards",
          "Profits are 2 : 3 and the money was invested for 4 and 9 months.  Capital ratio?",
          "2 × 4 : 3 × 9  =  8 : 27", "2/4 : 3/9  =  3 : 2",
          "Profit = capital × time, so capital = profit ÷ time.  In reverse, divide."),
         ("Trap 3  ·  years and months mixed", "A invests ₹10,000 for 1 year and B ₹15,000 for 8 months.  Profit ratio?",
          "10,000 × 1 : 15,000 × 8 = 1 : 12", "10,000 × 12 : 15,000 × 8 = 1 : 1",
          "Convert every period to months first.")]
PRACTICE_A = [("L1", "A and B invest ₹25,000 and ₹35,000 for one year.  The profit is ₹18,000.  Find each share."),
              ("L1", "A invests ₹16,000 for 9 months and B invests ₹12,000 for 12 months.  Find the ratio of their profits."),
              ("L2", "A, B and C invest ₹20,000, ₹30,000 and ₹50,000 for 12, 8 and 6 months.  The profit is ₹39,000.  Find each share."),
              ("L2", "A and B invest ₹40,000 and ₹50,000 for the same period.  The business loses ₹6,300.  How much does each lose?"),
              ("L2", "A and B invest for the same period; their profits are in the ratio 5 : 3.  A invested ₹45,000.  B's investment?")]
PRACTICE_B = [("L3", "A and B invest in the ratio 3 : 2; their profits are 5 : 4.  A's money stayed 10 months.  How long did B's?"),
              ("L3", "A invests ₹30,000 for 12 months, B invests ₹45,000.  Of a ₹21,000 profit B receives ₹7,000.  B's months?"),
              ("L3", "A, B and C invest ₹1,20,000, ₹1,50,000 and ₹1,80,000 for 10, 8 and 5 months.  Profit ₹1,10,000.  C's share?")]
ANSWERS_A = [("25 : 35 = 5 : 7;     1 part = 18,000 ÷ 12 = 1,500", "₹7,500 and ₹10,500"),
             ("16,000 × 9 = 1,44,000;     12,000 × 12 = 1,44,000", "1 : 1"),
             ("2,40,000 : 2,40,000 : 3,00,000 = 4 : 4 : 5;     1 part = 3,000", "₹12,000, ₹12,000, ₹15,000"),
             ("4 : 5;     1 part = 6,300 ÷ 9 = 700", "₹2,800 and ₹3,500")]
ANSWERS_B = [("same time, so capitals are 5 : 3;     45,000 × 3/5", "₹27,000"),
             ("time follows profit ÷ capital:   5/3 : 4/2 = 5 : 6;   A 10 months", "B:  12 months"),
             ("A's share 14,000:  A : B = 2 : 1;     3,60,000 = 2 × 45,000 × t", "t  =  4 months"),
             ("12,00,000 : 12,00,000 : 9,00,000 = 4 : 4 : 3;     3/11 × 1,10,000", "₹30,000")]
LENS = [("Recognition cue", "“invest”, “partners”, “start a business”, “share of the profit”:  write capital × months for each partner"),
        ("Target time", "20 seconds for the same time;  30 seconds for different times"),
        ("Sanity check", "the shares add up to the total profit;  more capital-months means a bigger share")]


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


class SimpleAndCompoundPartnershipVideo(LMSScene):
    lesson_title = "Simple & Compound Partnership"

    def construct(self):
        self.camera.background_color = BG

        self.intro()
        self.hook()
        self.objectives()
        self.why_this_matters()
        self.capital_times_time()
        self.shares_and_working_backwards()
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

        crumb = self.breadcrumb("Quantitative Aptitude", "Lesson 20 · Partnership", "Video 1 of 4")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        lesson = pill("Lesson 20  ·  Partnership", RATIO, size=LABEL)
        recap = VGroup(text("from Lesson 19  ·  Time & Distance", SMALL, MUTED),
                       fit_width(VGroup(pill("D = S × T, with matching units", WORD, size=LABEL), pill("two bodies:  watch the gap", GOOD, size=LABEL)).arrange(RIGHT, buff=0.4), SAFE_W - 0.6)).arrange(DOWN, buff=0.25)
        title = fit_width(text("Simple & Compound Partnership", TITLE, INK, BOLD), SAFE_W - 0.4)
        today = text("today: who gets how much of the profit", LABEL, FOCUS)
        block = VGroup(lesson, recap, title, today).arrange(DOWN, buff=0.55)
        fit_within(block, SAFE_W, SAFE_H - crumb.height - 0.9)
        block.next_to(crumb, DOWN, buff=0.6)
        self.no_overlap(crumb, lesson, recap, title, today)
        self.no_overlap(*recap[1])
        self.validator.check_in_frame(VGroup(crumb, block))

        n = self.narrate(
            id="intro_01",
            text="Now we start lesson twenty: partnership.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.at_word(n, "twenty")
        self.play(FadeIn(lesson, scale=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="intro_02",
            text="In lesson nineteen, D was S times T with matching units, and with two bodies you watched the gap.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "matching")
        self.play(FadeIn(recap[0]), FadeIn(recap[1][0], shift=UP * 0.1))
        self.at_word(n, "gap")
        self.play(FadeIn(recap[1][1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="intro_03",
            text="This first video is simple and compound partnership: who gets how much of the profit.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "simple")
        self.play(FadeIn(title, shift=UP * 0.1))
        self.at_word(n, "profit")
        self.play(FadeIn(today, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_intro")

    # ============================================== 1. HOOK ==========

    def hook(self):
        self.scene_start("S01_hook", title="Hook")

        head = self.heading("A startup's cap table")
        asha = pill("Asha:   ₹3,00,000,   in the business for 12 months", WORD, size=LABEL)
        ravi = pill("Ravi:   ₹4,50,000,   in the business for 8 months", WORD, size=LABEL)
        profit = pill("year-end profit:   ₹1,20,000", GOOD, size=LABEL)
        claim = text("Ravi:  “I put in more money, so I take the bigger share.”", LABEL, INK, BOLD)
        ask = pill("is he right?    work out each founder's share", FOCUS, size=LABEL)
        self.stack(head, [asha, ravi, profit, claim, ask], buff=0.55, top=0.7)

        n = self.narrate(
            id="hook_01",
            text="Two co-founders run a cloud-services startup. Asha put in three lakh rupees, and her money was in the "
                 "business all twelve months.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "co-founders")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "Asha")
        self.play(FadeIn(asha, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_02",
            text="Ravi put in four lakh fifty thousand rupees, but his money was in the business for only eight months.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Ravi")
        self.play(FadeIn(ravi, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_03",
            text="The year's profit is one lakh twenty thousand rupees.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "profit")
        self.play(FadeIn(profit, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_04",
            text="Ravi says: I put in more money, so I take the bigger share. Is he right? Work out each founder's share "
                 "before the video does.",
            voice="default",
            subtitle=True,
            pause_after=3.0,
        )
        self.at_word(n, "says")
        self.play(FadeIn(claim, shift=UP * 0.1))
        self.at_word(n, "right")
        self.play(FadeIn(ask, scale=1.03))
        self.at_word(n, "Work")
        self.play(Indicate(ask, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

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
            text="First, share a profit or a loss in the ratio of capitals when the time is the same.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "share")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "same")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="objectives_03",
            text="Second, share it in the ratio of capital times time when the times differ.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "times")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "differ")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="objectives_04",
            text="Third, work backwards from a profit ratio to an unknown capital or an unknown time.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "backwards")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "unknown")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_objectives")

    # ============================================== 3. WHY THIS MATTERS ==========

    def why_this_matters(self):
        self.scene_start("S03_why_this_matters", title="Why This Matters")

        head = self.heading("Why this matters")
        often = pill("one of the most predictable topics in aptitude papers", WORD, size=LABEL)
        one = text("almost every question is one ratio and one division", LABEL, INK, BOLD)
        lost = VGroup(pill("marks are lost by ignoring time", BAD, size=LABEL),
                      pill("or by dividing in the wrong direction when working backwards", BAD, size=LABEL)).arrange(DOWN, buff=0.35)
        self.stack(head, [often, one, lost], buff=0.8, top=1.0)

        n = self.narrate(
            id="why_this_matters_01",
            text="Partnership is one of the most predictable topics in aptitude papers: almost every question is one ratio "
                 "and one division.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "predictable")
        self.play(FadeIn(often, shift=UP * 0.1))
        self.at_word(n, "ratio")
        self.play(FadeIn(one, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="why_this_matters_02",
            text="The marks are lost by ignoring time, or by dividing in the wrong direction when working backwards.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "ignoring")
        self.play(FadeIn(lost[0], shift=UP * 0.1))
        self.at_word(n, "wrong")
        self.play(FadeIn(lost[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_why_this_matters")

    # ============================================== 4. CONCEPT - CAPITAL TIMES TIME ==========

    def capital_times_time(self):
        self.scene_start("S04_capital_times_time", title="Concept - Capital Times Time")

        head = self.heading("Capital × time")
        blocks = two_line_blocks(STEPS_A, WORD)
        self.stack(head, list(blocks), buff=0.5, top=0.7, align=LEFT)

        n = self.narrate(
            id="capital_times_time_01",
            text="A partnership pools capital. Two or more people invest in one business and agree to share its profit or "
                 "loss. Unless the question states another rule, the share follows capital times time.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "pools")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "invest")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.at_word(n, "follows")
        self.play(Indicate(blocks[0][1], color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="capital_times_time_02",
            text="Same time means a simple partnership. If every partner's money is in the business for the same period, "
                 "time cancels, and the profit ratio is the capital ratio.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "simple")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "cancels")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="capital_times_time_03",
            text="Different times mean a compound partnership. Multiply each capital by the months it stayed in the "
                 "business. These products, called capital-months or rupee-months, give the profit ratio.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "compound")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "Multiply")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.at_word(n, "products")
        self.play(Indicate(blocks[2][1], color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="capital_times_time_04",
            text="A loss is shared the same way. The ratio does not care whether the result is a profit or a loss.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "loss")
        self.play(FadeIn(blocks[3][0], shift=RIGHT * 0.2))
        self.at_word(n, "care")
        self.play(FadeIn(blocks[3][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_capital_times_time")

    # ============================================== 5. CONCEPT - SHARES, AND WORKING BACKWARDS ==========

    def shares_and_working_backwards(self):
        self.scene_start("S05_shares_and_working_backwards", title="Concept - Shares, and Working Backwards")

        head = self.heading("Shares, and working backwards")
        blocks = two_line_blocks(STEPS_B, WORD)
        self.stack(head, list(blocks), buff=0.75, top=1.0, align=LEFT)

        n = self.narrate(
            id="shares_and_working_backwards_01",
            text="One partner's share is their parts, divided by the total parts, times the profit. Simplify the ratio "
                 "first: cancel common zeros and factors.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "divided")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "Simplify")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="shares_and_working_backwards_02",
            text="Working backwards: capital follows profit divided by time, and time follows profit divided by capital. "
                 "Going in reverse means dividing, not multiplying.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "backwards")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "reverse")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="shares_and_working_backwards_03",
            text="Keep the units the same. Convert every period to months before multiplying: one year is twelve months.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "units")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "Convert")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_shares_and_working_backwards")

    # ============================================== 6. FORMULA BOX ==========

    def formula_box(self):
        self.scene_start("S06_formula_box", title="Formula Box")

        head = self.heading("Formula box", GOOD)
        lines = VGroup(*[text(f, LABEL, INK) for f in FORMULAS]).arrange(DOWN, buff=0.55, aligned_edge=LEFT)
        fit_width(lines, SAFE_W - 1.6)
        box = self.card(lines, width=SAFE_W - 0.4, color=GOOD, pad=0.5)
        self.stack(head, [box], top=0.7)

        n = self.narrate(
            id="formula_box_01",
            text="Here is the formula box. For the same time, the profit ratio is the capital ratio.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "box")
        self.play(FadeIn(box[0]))
        self.at_word(n, "same")
        self.play(FadeIn(lines[0], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_box_02",
            text="For different times, the profit ratio is the ratio of capital times time.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "different")
        self.play(FadeIn(lines[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_box_03",
            text="Backwards, the capital ratio is the ratio of profit divided by time, and the time ratio is the ratio of "
                 "profit divided by capital.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Backwards")
        self.play(FadeIn(lines[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_box_04",
            text="And a share is the partner's own parts over the total parts, times the profit or loss.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "share")
        self.play(FadeIn(lines[3], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_formula_box")

    # ============================================== 7. THE ANALOGY - A CLOUD BILL IN GB-HOURS ==========

    def analogy(self):
        self.scene_start("S07_analogy", title="The Analogy - A Cloud Bill in GB-Hours")

        head = self.heading("A cloud bill in GB-hours")
        bill = pill("memory used × hours used  =  GB-hours", WORD, size=BODY)
        same = text("a large machine for a few hours can cost the same as a small one for a whole day", LABEL, INK)
        cap = pill("capital works the same way:    rupees × months, not rupees alone", FOCUS, size=LABEL)
        stops = VGroup(text("Where the analogy stops", LABEL, BAD, BOLD),
                       text("a cloud bill charges every GB-hour at the same price", LABEL, INK),
                       text("real businesses may value early money more;  exams treat every rupee-month as equal", LABEL, MUTED)).arrange(DOWN, buff=0.2)
        self.stack(head, [bill, same, cap, stops], buff=0.6, top=0.7)

        n = self.narrate(
            id="analogy_01",
            text="Cloud providers bill memory in G B hours: how much you used, multiplied by how long you used it.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "bill")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "multiplied")
        self.play(FadeIn(bill, scale=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_02",
            text="A large machine for a few hours can cost the same as a small one for a whole day.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "large")
        self.play(FadeIn(same, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_03",
            text="Capital in a business works the same way: what counts is rupees times months, not rupees alone.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "counts")
        self.play(FadeIn(cap, scale=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_04",
            text="Where the analogy stops: a cloud bill charges every G B hour at the same price. Real businesses may "
                 "value early money more; exam questions treat every rupee-month as equal unless they say otherwise.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "stops")
        self.play(FadeIn(stops[0], shift=UP * 0.1))
        self.at_word(n, "charges")
        self.play(FadeIn(stops[1], shift=UP * 0.1))
        self.at_word(n, "early")
        self.play(FadeIn(stops[2], shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S07_analogy")

    # ============================================== 8. WORKED EXAMPLE - CLOSING THE HOOK ==========

    def hook_solved(self):
        self.scene_start("S08_hook_solved", title="Worked Example - Closing the Hook")

        head = self.heading("Asha and Ravi")
        bars = VGroup(VGroup(Rectangle(width=2.4, height=0.6, color=WORD, fill_color=WORD, fill_opacity=0.5),
                             text("Asha:  3 lakh × 12 months", SMALL, WORD, BOLD)).arrange(DOWN, buff=0.15),
                      VGroup(Rectangle(width=1.6, height=0.9, color=WORD, fill_color=WORD, fill_opacity=0.5),
                             text("Ravi:  4.5 lakh × 8 months", SMALL, WORD, BOLD)).arrange(DOWN, buff=0.15)).arrange(RIGHT, buff=1.0, aligned_edge=DOWN)
        steps = self.solve_steps([("Asha:    ₹3,00,000 × 12", "=  36,00,000 rupee-months"),
                                  ("Ravi:    ₹4,50,000 × 8", "=  36,00,000 rupee-months"),
                                  ("Ratio 1 : 1:    each founder gets", "₹60,000"),
                                  ("By capital alone (2 : 3), Ravi would get ₹72,000", "₹12,000 too much")])
        self.stack(head, [bars, steps], buff=0.5, top=0.6)
        self.no_overlap(*steps)
        self.no_overlap(*bars)

        n = self.narrate(
            id="hook_solved_01",
            text="Asha: three lakh times twelve is thirty-six lakh rupee-months.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "times")
        self.play(FadeIn(steps[0][:2], shift=RIGHT * 0.2), FadeIn(bars[0]))
        self.at_word(n, "thirty-six")
        self.play(FadeIn(steps[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_solved_02",
            text="Ravi: four lakh fifty thousand times eight is also thirty-six lakh rupee-months.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "times")
        self.play(FadeIn(steps[1][:2], shift=RIGHT * 0.2), FadeIn(bars[1]))
        self.at_word(n, "also")
        self.play(FadeIn(steps[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_solved_03",
            text="The ratio is one to one, so each founder gets sixty thousand rupees. Ravi put in more money, but for "
                 "less time; the two contributions are exactly equal.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "ratio")
        self.play(FadeIn(steps[2], shift=RIGHT * 0.2))
        self.at_word(n, "equal")
        self.play(Indicate(bars, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_solved_04",
            text="A split by capital alone, two to three, would have given Ravi seventy-two thousand rupees, which is "
                 "twelve thousand too much.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "alone")
        self.play(FadeIn(steps[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "twelve")
        self.play(FadeIn(steps[3][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S08_hook_solved")

    # ============================================== 9. A SECOND WORKED EXAMPLE - FINDING THE TIME ==========

    def second_example(self):
        self.scene_start("S09_second_example", title="A Second Worked Example - Finding the Time")

        head = self.heading("Finding the time")
        ask = text("A invests ₹40,000 for 12 months, B invests ₹60,000; of a ₹28,000 profit B receives ₹12,000:   B's months?", LABEL, MUTED)
        fit_width(ask, SAFE_W - 0.6)
        steps = self.solve_steps([("A's share:  28,000 − 12,000 = 16,000;      profit ratio A : B", "=  16 : 12  =  4 : 3"),
                                  ("Capital-months in the same ratio:    40,000 × 12 : 60,000 × t", "=  4 : 3"),
                                  ("4,80,000 × 3  =  4 × 60,000 × t;      14,40,000 = 2,40,000 × t", "t  =  6 months"),
                                  ("Check:    4,80,000 : 3,60,000", "=  4 : 3")])
        self.stack(head, [ask, steps], buff=0.7, top=0.7)
        self.no_overlap(*steps)

        n = self.narrate(
            id="second_example_01",
            text="A invests forty thousand rupees for twelve months, and B invests sixty thousand rupees. Of a profit of "
                 "twenty-eight thousand rupees, B receives twelve thousand. For how many months was B's money in the "
                 "business?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "invests")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "profit")
        self.play(FadeIn(ask, shift=UP * 0.1))
        self.at_word(n, "months", occurrence=2)
        self.play(Indicate(ask, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_02",
            text="A's share is twenty-eight thousand minus twelve thousand, sixteen thousand, so the profit ratio A to B "
                 "is sixteen to twelve: four to three.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "minus")
        self.play(FadeIn(steps[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "four")
        self.play(FadeIn(steps[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_03",
            text="The capital-months must be in the same ratio: forty thousand times twelve, to sixty thousand times t, is "
                 "four to three.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "capital-months")
        self.play(FadeIn(steps[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "four")
        self.play(FadeIn(steps[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_04",
            text="Four lakh eighty thousand times three equals four times sixty thousand times t, so fourteen lakh forty "
                 "thousand is two lakh forty thousand times t, and t is six months.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "equals")
        self.play(FadeIn(steps[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "six")
        self.play(FadeIn(steps[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_05",
            text="Check: four lakh eighty thousand to three lakh sixty thousand is four to three.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Check")
        self.play(FadeIn(steps[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "is")
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
            text="Same time: A twenty thousand, B thirty thousand, and a profit of fifteen thousand rupees. Two to three: "
                 "six thousand and nine thousand.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "time")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "Two")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_03",
            text="Different times: A fifteen thousand for eight months, B twenty thousand for nine months, and a profit of "
                 "twelve thousand five hundred. One lakh twenty thousand to one lakh eighty thousand, two to three: five "
                 "thousand and seven thousand five hundred.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "times")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "lakh")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_04",
            text="A loss: A fifty thousand, B seventy thousand, the same time, and a loss of nine thousand six hundred. "
                 "Five to seven: four thousand and five thousand six hundred.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "loss")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "seven")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Exam patterns  ·  4 to 6 of 6")
        blocks = self.pattern_blocks(PATTERNS[3:6])
        self.stack(head, list(blocks), buff=0.6, top=0.8, align=LEFT)

        n = self.narrate(
            id="exam_patterns_05",
            text="Capital from profit: the same time, profits three to five, and A invested twenty-four thousand. "
                 "Twenty-four thousand times five thirds: B invested forty thousand.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "Capital")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "times")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_06",
            text="The capital ratio from profit and time: profits two to three, times four and nine months. Two over four "
                 "to three over nine, a half to a third: three to two.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "ratio")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "over")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_07",
            text="Time from a share: A forty thousand for twelve months, B sixty thousand, and profits four to three. Four "
                 "lakh eighty thousand to sixty thousand t is four to three: B, six months.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "share")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "lakh")
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
            text="Trap one: ignoring time. Three lakh rupees for twelve months, and four lakh fifty thousand for eight "
                 "months: what is the profit ratio?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "ignoring")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "lakh")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_02",
            text="The wrong instinct says three to four and a half, two to three. The correct answer is thirty-six lakh to "
                 "thirty-six lakh: one to one.",
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
            text="The rule: whenever the periods differ, multiply capital by months before forming the ratio.",
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
            text="Trap two: multiplying when working backwards. Profits are two to three, and the money was invested for "
                 "four and nine months: what is the capital ratio?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "multiplying")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "Profits")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_05",
            text="The wrong instinct multiplies: eight to twenty-seven. The correct answer divides, two over four to three "
                 "over nine: three to two.",
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
            text="The rule: profit is capital times time, so capital is profit divided by time. Going in reverse means "
                 "dividing.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "rule")
        self.play(FadeIn(rule, shift=UP * 0.1))
        self.at_word(n, "reverse")
        self.play(Indicate(rule, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)
        self.clear_stage()

        head, q, wrong, right, rule = self.show_trap(TRAPS[2])

        n = self.narrate(
            id="traps_07",
            text="Trap three: years and months mixed. A invests ten thousand rupees for one year and B fifteen thousand "
                 "for eight months: what is the profit ratio?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "mixed")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "invests")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_08",
            text="The wrong instinct uses one for the year, and gets one to twelve. The correct answer uses twelve months: "
                 "one to one.",
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
            text="The rule: convert every period to months first.",
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
        given = pill("A invests ₹12,000, B ₹18,000, same period; the profit is ₹7,500:   A's share?", FOCUS, size=LABEL)
        work = VGroup(text("12,000 : 18,000  =  2 : 3", BODY, INK, BOLD), text("A gets 2/5 of 7,500  =  ₹3,000", BODY, GOOD, BOLD)).arrange(RIGHT, buff=0.8)
        self.stack(head, [given, work], buff=1.0, top=1.0)
        self.no_overlap(*work)

        n = self.narrate(
            id="checkpoint_01",
            text="Your turn. A invests twelve thousand rupees and B invests eighteen thousand for the same period. The "
                 "profit is seven thousand five hundred rupees. Find A's share.",
            voice="default",
            subtitle=True,
            pause_after=10.0,
        )
        self.at_word(n, "turn")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "invests")
        self.play(FadeIn(given, scale=1.03))
        self.at_word(n, "profit")
        self.play(Indicate(given, color=FOCUS, scale_factor=1.03))
        self.at_word(n, "Find")
        self.play(Indicate(given, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="checkpoint_02",
            text="Twelve thousand to eighteen thousand is two to three, so A gets two fifths of seven thousand five "
                 "hundred: three thousand rupees.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "two")
        self.play(FadeIn(work[0], shift=UP * 0.1))
        self.at_word(n, "fifths")
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
            text="Level one, question one: A and B invest twenty-five thousand and thirty-five thousand rupees for one "
                 "year, and the profit is eighteen thousand rupees; find each share. Question two: A invests sixteen "
                 "thousand rupees for nine months and B invests twelve thousand for twelve months; find the ratio of their "
                 "profits.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "year")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "ratio")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="practice_02",
            text="Level two, question three: A, B and C invest twenty thousand, thirty thousand and fifty thousand rupees "
                 "for twelve, eight and six months, and the profit is thirty-nine thousand; find each share. Question "
                 "four: A and B invest forty thousand and fifty thousand rupees for the same period, and the business "
                 "makes a loss of six thousand three hundred; how much does each partner lose? Question five: A and B "
                 "invest for the same period, and their profits are in the ratio five to three; A invested forty-five "
                 "thousand rupees; how much did B invest?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "C")
        self.play(FadeIn(rows[2], shift=RIGHT * 0.2))
        self.at_word(n, "loss")
        self.play(FadeIn(rows[3], shift=RIGHT * 0.2))
        self.at_word(n, "ratio")
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
            text="Level three, question six: A and B invest in the ratio three to two, and their profits are in the ratio "
                 "five to four; A's money was in the business for ten months; for how long was B's? Question seven: A "
                 "invests thirty thousand rupees for twelve months, and B invests forty-five thousand; of a profit of "
                 "twenty-one thousand, B receives seven thousand; for how many months was B's money in the business? "
                 "Question eight: A, B and C invest one lakh twenty thousand, one lakh fifty thousand and one lakh eighty "
                 "thousand rupees for ten, eight and five months, and the profit is one lakh ten thousand; find C's share.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "ratio")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "receives")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.at_word(n, "lakh")
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
            text="One: twenty-five to thirty-five is five to seven, and one part is eighteen thousand divided by twelve, "
                 "fifteen hundred: A gets seven thousand five hundred and B ten thousand five hundred.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "divided")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "gets")
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_02",
            text="Two: sixteen thousand times nine and twelve thousand times twelve are both one lakh forty-four thousand: "
                 "the ratio is one to one.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "times")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "ratio")
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_03",
            text="Three: two lakh forty thousand, two lakh forty thousand and three lakh is four to four to five; one part "
                 "is three thousand, so A and B get twelve thousand each and C fifteen thousand.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "lakh")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "each")
        self.play(FadeIn(rows[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_04",
            text="Four: four to five, and one part is six thousand three hundred divided by nine, seven hundred: A loses "
                 "two thousand eight hundred and B three thousand five hundred.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "divided")
        self.play(FadeIn(rows[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "loses")
        self.play(FadeIn(rows[3][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Answer key  ·  5 to 8", GOOD)
        table, rows = self.answer_table(head, ANSWERS_B, 5)

        n = self.narrate(
            id="answers_05",
            text="Five: the time is the same, so the capitals are five to three, and B invested forty-five thousand times "
                 "three fifths: twenty-seven thousand rupees.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "same")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "twenty-seven")
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_06",
            text="Six: time follows profit divided by capital: five thirds to four halves is five to six. A is ten months, "
                 "so B is twelve months. Check: three times ten to two times twelve is five to four.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "divided")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "twelve")
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.at_word(n, "Check")
        self.play(Indicate(rows[1][1], color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_07",
            text="Seven: A's share is fourteen thousand, so A to B is two to one. Three lakh sixty thousand equals two "
                 "times forty-five thousand times t, so t is four months.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "share")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "four")
        self.play(FadeIn(rows[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_08",
            text="Eight: twelve lakh, twelve lakh and nine lakh is four to four to three, so C gets three elevenths of one "
                 "lakh ten thousand: thirty thousand rupees.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "lakh")
        self.play(FadeIn(rows[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "thirty")
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
            text="Recognise and move. The recognition cue: invest, partners, start a business or share of the profit; "
                 "write capital times months for each partner.",
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
            text="The target time: twenty seconds for the same time, and thirty seconds for different times.",
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
            text="The sanity check: the shares add up to the total profit, and the partner with more capital-months gets "
                 "more.",
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
        law = pill("profit and loss are shared in the ratio of capital × time", GOOD, size=LABEL)
        same = pill("same time:   it cancels, and the capital ratio is enough", WORD, size=LABEL)
        back = pill("backwards, divide:    capital from profit ÷ time,    time from profit ÷ capital", RATIO, size=LABEL)
        hours = text("GB-hours: rupees × months, not rupees alone", LABEL, MUTED)
        nxt = self.breadcrumb("Next", "Video 2 · Changing Capital: Joining, Leaving & Withdrawals")
        self.stack(head, [law, same, back, hours, nxt], buff=0.6, top=0.7)

        n = self.narrate(
            id="summary_01",
            text="Profit and loss are shared in the ratio of capital times time.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "ratio")
        self.play(FadeIn(law, scale=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_02",
            text="If the time is the same, it cancels and the capital ratio is enough.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "cancels")
        self.play(FadeIn(same, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_03",
            text="To work backwards, divide: capital follows profit over time, and time follows profit over capital.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "divide")
        self.play(FadeIn(back, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_04",
            text="Remember the G B hours.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "hours")
        self.play(FadeIn(hours, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_05",
            text="Next: changing capital: joining, leaving and withdrawals.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Next")
        self.play(FadeIn(nxt, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S16_summary")

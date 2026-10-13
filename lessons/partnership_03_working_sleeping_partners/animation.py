"""
animation.py for the LMS video generator.

Course : Pre-C-CAT - Section A - Quantitative Aptitude
Video  : Lesson 20 - Partnership - 03 - Working & Sleeping Partners

Source script:
  C:\\Scripts\\Section A\\Aptitude\\Sessions 13-18 - Pipes, Time Distance, Partnership\\Lesson 20 - Partnership\\03 - Working & Sleeping Partners.pdf

Built on the golden-reference pattern:
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``;
  * layouts stacked with next_to and guarded with ``no_overlap``; nothing is
    ever animated onto or into another box.

Lesson 20, Video 3 of 4. Not the first video of the lesson: a silent breadcrumb, a one-line recap of Video 2, then today's topic. No spoken course welcome.
The narration follows the script section by section. Amounts keep the script's Indian grouping and are spoken as lakh. The seven concept steps are split over two screens; the six exam patterns are two-line blocks. A profit bar (managing share first, then the 3 : 2 split) is drawn beside the hook's solution.
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


def split(amount, *parts):
    return [Fraction(amount) * p / sum(parts) for p in parts]


# ---- the hook: Neha 6,00,000 (10% for managing), Vikram 4,00,000, profit 5,00,000 ----
MANAGING = Fraction(10, 100) * 500000
NEHA_PART, VIKRAM = split(500000 - MANAGING, 6, 4)
assert (MANAGING, NEHA_PART, VIKRAM, MANAGING + NEHA_PART) == (50000, 270000, 180000, 320000)
assert split(500000, 3, 2)[0] + MANAGING == 350000 and 500000 - 350000 == 150000 and VIKRAM - 150000 == 30000

# ---- second worked example: total profit from a difference ----
A_FRAC = Fraction(2, 10) + Fraction(8, 10) * Fraction(5, 8)
B_FRAC = Fraction(8, 10) * Fraction(3, 8)
assert (A_FRAC, B_FRAC) == (Fraction(7, 10), Fraction(3, 10)) and 20000 / (A_FRAC - B_FRAC) == 50000 and (A_FRAC * 50000, B_FRAC * 50000) == (35000, 15000)

# ---- exam patterns, traps, checkpoint, practice (answers computed) ----
P1 = split(60000 - 12 * 2000, 3, 2)
assert (24000 + P1[0], P1[1]) == (45600, 14400)
P2 = split(40000 - 6000, 3, 2)
assert (6000 + P2[0], P2[1]) == (26400, 13600) and Fraction(15, 100) * 40000 == 6000
assert Fraction(22000 * 10, 110) == 2000 and Fraction(10, 100) * (22000 - 2000) == 2000
assert (4000 + 10000, 6000 + 10000) == (14000, 16000) and 30000 - 4000 - 6000 == 20000
ONE = Fraction(1, 10) + Fraction(9, 10) * Fraction(3, 5)
assert ONE == Fraction(64, 100) and 32000 / ONE == 50000
C1 = split(42000 - 12000, 2, 3)
assert 12000 + C1[0] == 24000
assert (18000 + 15000, 15000) == (33000, 15000) and 48000 - 18000 == 30000
Q2 = split(25000 - 2500, 3, 2)
assert (2500 + Q2[0], Q2[1]) == (16000, 9000)
Q3 = split(45000 - 9000, 2, 3)
assert (9000 + Q3[0], Q3[1]) == (23400, 21600)
assert Fraction(33000 * 10, 110) == 3000 and 3000 + (33000 - 3000) // 2 == 18000
assert (4000 + 12000, 2000 + 12000) == (16000, 14000) and 30000 - 6000 == 24000
assert 14000 / (ONE - (1 - ONE)) == 50000 and 1 - ONE == Fraction(36, 100)
assert 12 * 3000 == 36000 and 36000 + split(136000 - 36000, 2, 3, 5)[2] == 86000
assert 40000 * 12 == 60000 * 8 and 33000 / (Fraction(2, 10) + Fraction(4, 10)) == 55000 and Fraction(4, 10) * 55000 == 22000

OBJECTIVES = [("Pay a working partner's salary, commission or “x% for managing”", "before sharing the remainder"),
              ("Handle commission “after charging the commission”", "and interest on capital"),
              ("Find the total profit", "from the difference between two partners' receipts")]
STEPS_A = [("Two roles:  a working partner invests and runs the business", "a sleeping partner only invests;    here every capital stays the whole year unless a time is given"),
           ("Pay the working partner first", "salary, allowance, commission, “x% for managing”, interest on capital:  all come out before sharing"),
           ("Salary is per month × months", "₹2,000 a month for a year is ₹24,000"),
           ("“x% of the profit” means x% of the total profit", "unless “after charging the commission”:  then C = x% of (P − C),  so C = P × x/(100 + x)")]
STEPS_B = [("Interest on capital is paid first, at the stated rate on each capital", "then the remainder is shared as stated"),
           ("A working partner's total = payment + their share of the remainder", "the remainder follows capital × time, unless the question says otherwise"),
           ("Difference of receipts gives the total profit", "write each receipt as a fraction of P;    10% for managing, capitals 3 : 2:    10% + 90% × 3/5 = 64% of P")]
FORMULAS = ["Remainder   =   profit − (salary + commission + interest)",
            "Working partner's total   =   payment + (own parts ÷ total parts) × remainder",
            "Commission after charging it:       C  =  P × x/(100 + x)",
            "k% for managing, capital share s:       working partner gets  k% + (100 − k)% × s"]
PATTERNS = [("Salary first", "A ₹30,000 (₹2,000 a month for managing), B ₹20,000;   profit ₹60,000", "60,000 − 24,000 = 36,000,  shared 3 : 2", "A ₹45,600,  B ₹14,400"),
            ("% for managing", "A ₹1,20,000 (15% for managing), B ₹80,000;   profit ₹40,000", "6,000 + 34,000 × 3/5", "A ₹26,400,  B ₹13,600"),
            ("Commission after charging it", "profit ₹22,000;   10% of the profit after charging the commission", "22,000 × 10/110", "₹2,000"),
            ("Interest on capital", "A ₹40,000, B ₹60,000;   10% interest;   rest shared equally;   profit ₹30,000", "4,000 and 6,000,  then 10,000 each", "A ₹14,000,  B ₹16,000"),
            ("Total from a difference", "capitals 5 : 3;   A 20% for managing;   A gets ₹20,000 more", "0.7P − 0.3P = 20,000", "₹50,000"),
            ("Total from one receipt", "capitals 3 : 2;   A 10% for managing;   A receives ₹32,000", "0.1P + 0.54P = 32,000", "₹50,000")]
TRAPS = [("Trap 1  ·  sharing first, paying the working partner on top",
          "Capitals 3 : 2; A gets 10% for managing; profit ₹5,00,000.  A's total?",
          "3,00,000 + 50,000 = ₹3,50,000", "50,000 + 2,70,000 = ₹3,20,000",
          "The payment comes out first.  Receipts adding to more than the profit: wrong order."),
         ("Trap 2  ·  “after charging the commission” read as a plain percentage",
          "Profit ₹22,000.  The manager gets 10% of the profit after charging his commission.  Commission?",
          "10% of 22,000  =  ₹2,200", "22,000 × 10/110  =  ₹2,000",
          "Check:  10% of what is left (₹20,000) must equal the commission (₹2,000)."),
         ("Trap 3  ·  a monthly salary taken once",
          "A gets ₹2,000 a month for managing; profit ₹60,000 for the year.  Amount left to share?",
          "60,000 − 2,000  =  ₹58,000", "60,000 − 24,000  =  ₹36,000",
          "Multiply a monthly salary by the number of months it is paid.")]
PRACTICE_A = [("L1", "A and B invest ₹50,000 each.  A, the working partner, gets ₹1,500 a month.  The year's profit is ₹48,000.  Each total?"),
              ("L1", "A and B invest ₹30,000 and ₹20,000.  A gets 10% of the profit for managing; the rest by capital.  Profit ₹25,000.  Totals?"),
              ("L2", "A and B invest in the ratio 2 : 3.  A, the working partner, gets 20% of the profit; the rest by capital.  Profit ₹45,000.  Totals?"),
              ("L2", "A and B invest ₹50,000 each.  A gets 10% of the profit after charging his commission; rest equally.  Profit ₹33,000.  A's total?"),
              ("L2", "A and B invest ₹80,000 and ₹40,000.  Each gets 5% interest on capital; the rest is shared equally.  Profit ₹30,000.  Totals?")]
PRACTICE_B = [("L3", "A and B invest ₹60,000 and ₹40,000.  A gets 10% for managing; the rest by capital.  A receives ₹14,000 more than B.  Profit?"),
              ("L3", "A, B and C invest ₹1,00,000, ₹1,50,000 and ₹2,50,000.  C, the working partner, gets ₹3,000 a month.  Profit ₹1,36,000.  C's total?"),
              ("L3", "A ₹40,000 for 12 months, B ₹60,000 for 8.  A gets 20% for managing; rest by capital × time.  A receives ₹33,000.  Profit?  B's share?")]
ANSWERS_A = [("salary 18,000;    remainder 30,000 shared equally:  15,000 each", "A ₹33,000,  B ₹15,000"),
             ("managing share 2,500;    remainder 22,500 shared 3 : 2:  13,500 and 9,000", "A ₹16,000,  B ₹9,000"),
             ("A's 20% = 9,000;    remainder 36,000 shared 2 : 3:  14,400 and 21,600", "A ₹23,400,  B ₹21,600"),
             ("C = 33,000 × 10/110 = 3,000;    remainder 30,000 shared equally", "A:  3,000 + 15,000 = ₹18,000")]
ANSWERS_B = [("interest 4,000 and 2,000;    remainder 24,000:  12,000 each", "A ₹16,000,  B ₹14,000"),
             ("A = 0.1P + 0.9P × 3/5 = 0.64P;    B = 0.36P;    0.28P = 14,000", "P  =  ₹50,000"),
             ("salary 36,000;    remainder 1,00,000 shared 2 : 3 : 5", "C:  36,000 + 50,000 = ₹86,000"),
             ("capital-months 1 : 1;    A = 0.2P + 0.4P = 0.6P = 33,000", "P ₹55,000;  B ₹22,000")]
LENS = [("Recognition cue", "“working partner”, “managing”, “salary”, “commission”, “interest on capital”, “sleeping partner”:  pay first, then share"),
        ("Target time", "45 seconds"),
        ("Sanity check", "all receipts add up to the total profit;  the working partner gets more than the plain capital share")]


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


class WorkingAndSleepingPartnersVideo(LMSScene):
    lesson_title = "Working & Sleeping Partners"

    def construct(self):
        self.camera.background_color = BG

        self.intro()
        self.hook()
        self.objectives()
        self.why_this_matters()
        self.pay_first()
        self.interest_totals_differences()
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
    # Not the first video: silent breadcrumb, a one-line recap of the previous video, then today's topic.

    def intro(self):
        self.scene_start("S00_intro", title="Intro")

        crumb = self.breadcrumb("Quantitative Aptitude", "Lesson 20 · Partnership", "Video 3 of 4")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        recap = VGroup(text("last video", SMALL, MUTED), pill("timeline:  capital × months for each segment", WORD, size=LABEL)).arrange(DOWN, buff=0.25)
        title = fit_width(text("Working & Sleeping Partners", TITLE, INK, BOLD), SAFE_W - 0.4)
        today = text("today: pay first, then share", LABEL, FOCUS)
        block = VGroup(recap, title, today).arrange(DOWN, buff=0.7)
        fit_within(block, SAFE_W, SAFE_H - crumb.height - 0.9)
        block.next_to(crumb, DOWN, buff=0.7)
        self.no_overlap(crumb, recap, title, today)
        self.validator.check_in_frame(VGroup(crumb, block))

        n = self.narrate(
            id="intro_01",
            text="In the last video, you split the year at every change and added capital times months for each segment.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.at_word(n, "segment")
        self.play(FadeIn(recap, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="intro_02",
            text="Today: working and sleeping partners, where you pay first, and then share.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "working")
        self.play(FadeIn(title, shift=UP * 0.1))
        self.at_word(n, "pay")
        self.play(FadeIn(today, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_intro")

    # ============================================== 1. HOOK ==========

    def hook(self):
        self.scene_start("S01_hook", title="Hook")

        head = self.heading("A partnership agreement")
        partners = VGroup(pill("Neha:  ₹6,00,000,  runs the company", WORD, size=LABEL), pill("Vikram:  ₹4,00,000,  investor only", WORD, size=LABEL))\
            .arrange(RIGHT, buff=0.5)
        clause = text("Neha receives 10% of the profit for managing; the rest is shared in the ratio of capitals", LABEL, INK)
        fit_width(clause, SAFE_W - 0.6)
        profit = pill("profit:   ₹5,00,000", GOOD, size=LABEL)
        est = text("Vikram's estimate:  3 : 2 gives Neha ₹3,00,000, plus her 10%:  ₹3,50,000;   that leaves him ₹1,50,000", LABEL, BAD, BOLD)
        fit_width(est, SAFE_W - 0.6)
        ask = pill("is his arithmetic right?    how much does each partner really receive?", FOCUS, size=LABEL)
        self.stack(head, [partners, clause, profit, est, ask], buff=0.55, top=0.7)
        self.no_overlap(*partners)

        n = self.narrate(
            id="hook_01",
            text="Neha and Vikram start an analytics firm with six lakh and four lakh rupees. Neha runs the business day "
                 "to day; Vikram only invests.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "six")
        self.play(FadeIn(partners[0], shift=UP * 0.1))
        self.at_word(n, "four")
        self.play(FadeIn(partners[1], shift=UP * 0.1))
        self.at_word(n, "runs")
        self.play(Indicate(partners[0], color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_02",
            text="Their agreement gives Neha ten percent of the profit for managing, and the rest is shared in the ratio "
                 "of capitals. The year's profit is five lakh rupees.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "agreement")
        self.play(FadeIn(clause, shift=UP * 0.1))
        self.at_word(n, "profit", occurrence=2)
        self.play(FadeIn(profit, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_03",
            text="Vikram's quick estimate: capitals are three to two, so Neha gets three lakh, plus her ten percent: three "
                 "lakh fifty thousand. That leaves Vikram one lakh fifty thousand.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "estimate")
        self.play(FadeIn(est, shift=UP * 0.1))
        self.at_word(n, "leaves")
        self.play(Indicate(est, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_04",
            text="Is his arithmetic right, and how much does each partner really receive?",
            voice="default",
            subtitle=True,
            pause_after=3.0,
        )
        self.at_word(n, "right")
        self.play(FadeIn(ask, scale=1.03))
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
            text="First, pay a working partner's salary, commission or x percent for managing before sharing the "
                 "remainder.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "pay")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "before")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="objectives_03",
            text="Second, handle commission after charging the commission, and interest on capital.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "handle")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "interest")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="objectives_04",
            text="Third, find the total profit from the difference between two partners' receipts.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "total")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "difference")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_objectives")

    # ============================================== 3. WHY THIS MATTERS ==========

    def why_this_matters(self):
        self.scene_start("S03_why_this_matters", title="Why This Matters")

        head = self.heading("Why this matters")
        always = pill("exam-level partnership questions almost always include a working partner", WORD, size=LABEL)
        easy = text("the ratio is easy", LABEL, MUTED)
        marks = VGroup(pill("do the steps in the right order", FOCUS, size=LABEL), pill("read what the percentage is a percentage of", FOCUS, size=LABEL))\
            .arrange(RIGHT, buff=0.4)
        fit_width(marks, SAFE_W - 0.4)
        self.stack(head, [always, easy, marks], buff=0.9, top=1.1)
        self.no_overlap(*marks)

        n = self.narrate(
            id="why_this_matters_01",
            text="Exam-level partnership questions almost always include a working partner.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "working")
        self.play(FadeIn(always, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="why_this_matters_02",
            text="The ratio is easy; the marks depend on doing the steps in the right order, and on reading exactly what "
                 "the percentage is a percentage of.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "easy")
        self.play(FadeIn(easy, shift=UP * 0.1))
        self.at_word(n, "order")
        self.play(FadeIn(marks[0], shift=UP * 0.1))
        self.at_word(n, "reading")
        self.play(FadeIn(marks[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_why_this_matters")

    # ============================================== 4. CONCEPT - PAY THE WORKING PARTNER FIRST ==========

    def pay_first(self):
        self.scene_start("S04_pay_first", title="Concept - Pay the Working Partner First")

        head = self.heading("Pay the working partner first")
        blocks = two_line_blocks(STEPS_A, WORD)
        self.stack(head, list(blocks), buff=0.5, top=0.7, align=LEFT)

        n = self.narrate(
            id="pay_first_01",
            text="There are two roles. A working, or active, partner invests and also runs the business. A sleeping, or "
                 "passive, partner only invests. In this video, every capital stays in the business for the whole year "
                 "unless a time is given.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "roles")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "working")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "sleeping")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.at_word(n, "whole")
        self.play(Indicate(blocks[0][1], color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="pay_first_02",
            text="Pay the working partner first. Salary, allowance, commission, x percent for managing and interest on "
                 "capital all come out of the total profit before it is shared. Unless the question says otherwise, the "
                 "remainder is then shared in the ratio of capital times time.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "first")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "Salary")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.at_word(n, "remainder")
        self.play(Indicate(blocks[1][1], color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="pay_first_03",
            text="Salary is per month, times the months: two thousand rupees a month for a year is twenty-four thousand.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "month")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "twenty-four")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="pay_first_04",
            text="X percent of the profit means x percent of the total profit, unless the question says after charging the "
                 "commission. Then the commission C is x percent of P minus C, which gives C as P times x, over one "
                 "hundred plus x.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "total")
        self.play(FadeIn(blocks[3][0], shift=RIGHT * 0.2))
        self.at_word(n, "minus")
        self.play(FadeIn(blocks[3][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_pay_first")

    # ============================================== 5. CONCEPT - INTEREST, TOTALS AND DIFFERENCES ==========

    def interest_totals_differences(self):
        self.scene_start("S05_interest_totals_differences", title="Concept - Interest, Totals and Differences")

        head = self.heading("Interest, totals and differences")
        blocks = two_line_blocks(STEPS_B, WORD)
        self.stack(head, list(blocks), buff=0.75, top=1.0, align=LEFT)

        n = self.narrate(
            id="interest_totals_differences_01",
            text="Interest on capital is paid first, at the stated rate on each partner's capital. Then the remainder is "
                 "shared as stated. If the remainder is shared in the capital ratio, interest at the same rate for "
                 "everyone does not change anyone's total.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "Interest")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "remainder")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.at_word(n, "change")
        self.play(Indicate(blocks[0][1], color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="interest_totals_differences_02",
            text="A working partner's total is the payment, plus their share of the remainder.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "plus")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "remainder")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="interest_totals_differences_03",
            text="The difference of receipts gives the total profit. Write each partner's receipt as a fraction of P, "
                 "subtract, and solve. A ten percent managing share with capitals three to two gives the working partner "
                 "ten percent plus ninety percent times three fifths: sixty-four percent of P.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "difference")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "Write")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.at_word(n, "sixty-four")
        self.play(Indicate(blocks[2][1], color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_interest_totals_differences")

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
            text="Here is the formula box. The remainder is the profit minus salary, commission and interest.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "box")
        self.play(FadeIn(box[0]))
        self.at_word(n, "remainder")
        self.play(FadeIn(lines[0], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_box_02",
            text="The working partner's total is the payment, plus their own parts over the total parts, times the "
                 "remainder.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "total")
        self.play(FadeIn(lines[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_box_03",
            text="A commission after charging it is P times x, over one hundred plus x.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "commission")
        self.play(FadeIn(lines[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_box_04",
            text="And with k percent for managing and a capital share s, the working partner gets k percent, plus one "
                 "hundred minus k percent, times s.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "managing")
        self.play(FadeIn(lines[3], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_formula_box")

    # ============================================== 7. THE ANALOGY - A SHARED CAB ==========

    def analogy(self):
        self.scene_start("S07_analogy", title="The Analogy - A Shared Cab")

        head = self.heading("A shared cab, and one passenger drives")
        fuel = pill("first the driver is repaid for the fuel", WORD, size=LABEL)
        fare = pill("only then is the rest of the fare split by distance travelled", WORD, size=LABEL)
        above = text("pay for the work comes off the top; the remainder follows the ratio", LABEL, INK, BOLD)
        stops = VGroup(text("Where the analogy stops", LABEL, BAD, BOLD),
                       text("the driving passenger does not invest money in the car", LABEL, INK),
                       text("a working partner is also an investor:  payment and a share of the remainder", LABEL, MUTED)).arrange(DOWN, buff=0.2)
        self.stack(head, [fuel, fare, above, stops], buff=0.6, top=0.7)

        n = self.narrate(
            id="analogy_01",
            text="Think of a shared cab where one passenger also drives.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "cab")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_02",
            text="First the driver is repaid for the fuel; only then is the rest of the fare split by how far each person "
                 "travelled.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "repaid")
        self.play(FadeIn(fuel, shift=UP * 0.1))
        self.at_word(n, "split")
        self.play(FadeIn(fare, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_03",
            text="Pay for the work comes off the top; the remainder follows the ratio.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "top")
        self.play(FadeIn(above, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_04",
            text="Where the analogy stops: the driving passenger does not invest money in the car. A working partner is "
                 "also an investor, so they receive both the payment and a share of the remainder.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "stops")
        self.play(FadeIn(stops[0], shift=UP * 0.1))
        self.at_word(n, "invest")
        self.play(FadeIn(stops[1], shift=UP * 0.1))
        self.at_word(n, "investor")
        self.play(FadeIn(stops[2], shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S07_analogy")

    # ============================================== 8. WORKED EXAMPLE - CLOSING THE HOOK ==========

    def hook_solved(self):
        self.scene_start("S08_hook_solved", title="Worked Example - Closing the Hook")

        head = self.heading("Neha and Vikram")
        bar = VGroup(Rectangle(width=0.9, height=0.35, color=FOCUS, fill_color=FOCUS, fill_opacity=0.85),
                     Rectangle(width=4.86, height=0.35, color=WORD, fill_color=WORD, fill_opacity=0.45),
                     Rectangle(width=3.24, height=0.35, color=MUTED, fill_color=MUTED, fill_opacity=0.45)).arrange(RIGHT, buff=0)
        steps = self.solve_steps([("Managing share, paid first:    10% of ₹5,00,000", "=  ₹50,000"),
                                  ("Remainder ₹4,50,000, shared 3 : 2:    Neha ₹2,70,000", "Vikram ₹1,80,000"),
                                  ("Neha receives    50,000 + 2,70,000", "=  ₹3,20,000"),
                                  ("Vikram's estimate hands out ₹5,50,000 from ₹5,00,000", "his share is ₹30,000 short")])
        self.stack(head, [bar, steps], buff=0.7, top=0.8)
        self.no_overlap(*steps)

        n = self.narrate(
            id="hook_solved_01",
            text="The managing share is ten percent of five lakh, fifty thousand rupees, paid first.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "percent")
        self.play(FadeIn(steps[0][:2], shift=RIGHT * 0.2), FadeIn(bar[0]))
        self.at_word(n, "fifty")
        self.play(FadeIn(steps[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_solved_02",
            text="The remainder, four lakh fifty thousand, is shared three to two: Neha two lakh seventy thousand, Vikram "
                 "one lakh eighty thousand.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "shared")
        self.play(FadeIn(steps[1][:2], shift=RIGHT * 0.2), FadeIn(bar[1]))
        self.at_word(n, "Vikram")
        self.play(FadeIn(steps[1][2], shift=LEFT * 0.1), FadeIn(bar[2]))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_solved_03",
            text="Neha receives fifty thousand plus two lakh seventy thousand: three lakh twenty thousand rupees. Vikram "
                 "receives one lakh eighty thousand.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "plus")
        self.play(FadeIn(steps[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "twenty")
        self.play(FadeIn(steps[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_solved_04",
            text="Vikram's estimate shared the full profit first and then added the ten percent on top. That hands out "
                 "five lakh fifty thousand from a five lakh profit, and the extra fifty thousand came out of his own "
                 "share: thirty thousand rupees short.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "estimate")
        self.play(FadeIn(steps[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "short")
        self.play(FadeIn(steps[3][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S08_hook_solved")

    # ============================================== 9. A SECOND WORKED EXAMPLE - TOTAL PROFIT FROM A DIFFERENCE ==========

    def second_example(self):
        self.scene_start("S09_second_example", title="A Second Worked Example - Total Profit from a Difference")

        head = self.heading("Total profit from a difference")
        ask = text("A and B invest ₹50,000 and ₹30,000; A gets 20% for managing; A receives ₹20,000 more than B:   total profit?", LABEL, MUTED)
        fit_width(ask, SAFE_W - 0.6)
        steps = self.solve_steps([("Profit P:    managing share 0.2P;      remainder 0.8P", "shared 5 : 3"),
                                  ("A  =  0.2P + 0.8P × 5/8  =  0.7P", "B  =  0.8P × 3/8  =  0.3P"),
                                  ("Difference:    0.4P = 20,000", "P  =  ₹50,000"),
                                  ("Check:    A ₹35,000,    B ₹15,000", "difference ₹20,000")])
        self.stack(head, [ask, steps], buff=0.7, top=0.7)
        self.no_overlap(*steps)

        n = self.narrate(
            id="second_example_01",
            text="A and B invest fifty thousand and thirty thousand rupees. A is the working partner and receives twenty "
                 "percent of the profit for managing; the rest is shared in the ratio of capitals. A receives twenty "
                 "thousand rupees more than B. Find the total profit.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "invest")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "working")
        self.play(FadeIn(ask, shift=UP * 0.1))
        self.at_word(n, "more")
        self.play(Indicate(ask, color=FOCUS, scale_factor=1.03))
        self.at_word(n, "Find")
        self.play(Indicate(ask, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_02",
            text="Let the profit be P. The managing share is zero point two P, and the remainder, zero point eight P, is "
                 "shared five to three.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "profit")
        self.play(FadeIn(steps[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "shared")
        self.play(FadeIn(steps[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_03",
            text="A gets zero point two P plus five eighths of zero point eight P, zero point seven P; B gets three "
                 "eighths of zero point eight P, zero point three P.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "plus")
        self.play(FadeIn(steps[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "three")
        self.play(FadeIn(steps[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_04",
            text="The difference, zero point four P, is twenty thousand, so P is fifty thousand rupees.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "difference")
        self.play(FadeIn(steps[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "fifty")
        self.play(FadeIn(steps[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_05",
            text="Check: A gets thirty-five thousand and B fifteen thousand, a difference of twenty thousand.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Check")
        self.play(FadeIn(steps[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "difference")
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
            text="Salary first: A thirty thousand, with two thousand a month for managing, B twenty thousand, and a profit "
                 "of sixty thousand. Sixty thousand minus twenty-four thousand is thirty-six thousand, shared three to "
                 "two: A forty-five thousand six hundred, B fourteen thousand four hundred.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Salary")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "minus")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_03",
            text="A percentage for managing: A one lakh twenty thousand, with fifteen percent for managing, B eighty "
                 "thousand, and a profit of forty thousand. Six thousand, plus three fifths of thirty-four thousand: A "
                 "twenty-six thousand four hundred, B thirteen thousand six hundred.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "percentage")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "plus")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_04",
            text="Commission after charging it: a profit of twenty-two thousand, and ten percent of the profit after "
                 "charging the commission. Twenty-two thousand times ten over one hundred and ten: two thousand rupees.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Commission")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "over")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Exam patterns  ·  4 to 6 of 6")
        blocks = self.pattern_blocks(PATTERNS[3:6])
        self.stack(head, list(blocks), buff=0.6, top=0.8, align=LEFT)

        n = self.narrate(
            id="exam_patterns_05",
            text="Interest on capital: A forty thousand, B sixty thousand, ten percent interest, the rest shared equally, "
                 "and a profit of thirty thousand. Four thousand and six thousand, then ten thousand each: A fourteen "
                 "thousand, B sixteen thousand.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "Interest")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "each")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_06",
            text="The total from a difference: capitals five to three, A twenty percent for managing, and A gets twenty "
                 "thousand more. Zero point seven P minus zero point three P is twenty thousand: fifty thousand rupees.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "difference")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "minus")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_07",
            text="The total from one receipt: capitals three to two, A ten percent for managing, and A receives thirty-two "
                 "thousand. Zero point one P plus zero point five four P is thirty-two thousand: fifty thousand rupees.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "receipt")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "plus")
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
            text="Trap one: sharing first, and paying the working partner on top. Capitals are three to two, A gets ten "
                 "percent for managing, and the profit is five lakh rupees: what is A's total?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "sharing")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "Capitals")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_02",
            text="The wrong instinct adds three lakh and fifty thousand: three lakh fifty thousand. The correct answer is "
                 "fifty thousand plus three fifths of four lakh fifty thousand: three lakh twenty thousand.",
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
            text="The rule: the payment comes out of the profit first. If the receipts add up to more than the profit, the "
                 "order is wrong.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "rule")
        self.play(FadeIn(rule, shift=UP * 0.1))
        self.at_word(n, "order")
        self.play(Indicate(rule, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)
        self.clear_stage()

        head, q, wrong, right, rule = self.show_trap(TRAPS[1])

        n = self.narrate(
            id="traps_04",
            text="Trap two: after charging the commission, read as a plain percentage. The profit is twenty-two thousand "
                 "rupees, and the manager gets ten percent of the profit after charging his commission: what is the "
                 "commission?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "plain")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "manager")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_05",
            text="The wrong instinct takes ten percent of twenty-two thousand: two thousand two hundred. The correct "
                 "answer is twenty-two thousand times ten over one hundred and ten: two thousand rupees.",
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
            text="The rule: check that ten percent of what is left, twenty thousand, equals the commission, two thousand.",
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
            text="Trap three: a monthly salary taken once. A gets two thousand rupees a month for managing, and the profit "
                 "is sixty thousand for the year: what amount is left to share?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "once")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "month")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_08",
            text="The wrong instinct subtracts two thousand: fifty-eight thousand. The correct answer subtracts "
                 "twenty-four thousand: thirty-six thousand rupees.",
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
            text="The rule: multiply a monthly salary by the number of months it is paid.",
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
        given = pill("A ₹40,000, B ₹60,000; A gets ₹1,000 a month for managing; profit ₹42,000:   A's total?", FOCUS, size=LABEL)
        work = VGroup(text("salary  12 × 1,000  =  12,000;      remainder 30,000 shared 2 : 3:   A gets 12,000", LABEL, INK, BOLD),
                      text("A's total  =  ₹24,000", BODY, GOOD, BOLD)).arrange(DOWN, buff=0.4)
        fit_width(work, SAFE_W - 0.6)
        self.stack(head, [given, work], buff=0.9, top=1.0)
        self.no_overlap(*work)

        n = self.narrate(
            id="checkpoint_01",
            text="Your turn. A and B invest forty thousand and sixty thousand rupees. A, the working partner, gets one "
                 "thousand rupees a month. The year's profit is forty-two thousand. Find A's total.",
            voice="default",
            subtitle=True,
            pause_after=10.0,
        )
        self.at_word(n, "turn")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "invest")
        self.play(FadeIn(given, scale=1.03))
        self.at_word(n, "working")
        self.play(Indicate(given, color=FOCUS, scale_factor=1.03))
        self.at_word(n, "profit")
        self.play(Indicate(given, color=FOCUS, scale_factor=1.03))
        self.at_word(n, "Find")
        self.play(Indicate(given, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="checkpoint_02",
            text="The salary is twelve times one thousand, twelve thousand. The remainder, thirty thousand, is shared two "
                 "to three, so A gets twelve thousand of it. A's total is twenty-four thousand rupees.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "salary")
        self.play(FadeIn(work[0], shift=UP * 0.1))
        self.at_word(n, "remainder")
        self.play(Indicate(work[0], color=FOCUS, scale_factor=1.03))
        self.at_word(n, "twenty-four")
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
            text="Level one, question one: A and B invest fifty thousand rupees each; A, the working partner, gets a "
                 "salary of fifteen hundred rupees a month; the year's profit is forty-eight thousand; find each partner's "
                 "total. Question two: A and B invest thirty thousand and twenty thousand rupees; A gets ten percent of "
                 "the profit for managing, and the rest is shared in the ratio of capitals; the profit is twenty-five "
                 "thousand; find each partner's total.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "salary")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "managing")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="practice_02",
            text="Level two, question three: A and B invest in the ratio two to three; A, the working partner, gets twenty "
                 "percent of the profit, and the rest is shared in the ratio of capitals; the profit is forty-five "
                 "thousand; find each partner's total. Question four: A and B invest fifty thousand rupees each; A, the "
                 "managing partner, gets a commission of ten percent of the profit after charging his commission, and the "
                 "rest is shared equally; the profit before commission is thirty-three thousand; find A's total. Question "
                 "five: A and B invest eighty thousand and forty thousand rupees; each receives five percent a year "
                 "interest on capital, and the remaining profit is shared equally; the year's profit is thirty thousand; "
                 "find each partner's total.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "ratio")
        self.play(FadeIn(rows[2], shift=RIGHT * 0.2))
        self.at_word(n, "commission")
        self.play(FadeIn(rows[3], shift=RIGHT * 0.2))
        self.at_word(n, "interest")
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
            text="Level three, question six: A and B invest sixty thousand and forty thousand rupees; A, the working "
                 "partner, gets ten percent of the profit for managing, and the rest is shared in the ratio of capitals; A "
                 "receives fourteen thousand rupees more than B; find the total profit. Question seven: A, B and C invest "
                 "one lakh, one lakh fifty thousand and two lakh fifty thousand rupees; C, the working partner, gets three "
                 "thousand rupees a month; the year's profit is one lakh thirty-six thousand; find C's total. Question "
                 "eight: A invests forty thousand rupees for twelve months and B invests sixty thousand for eight months; "
                 "A manages the business and gets twenty percent of the profit, and the rest is shared in the ratio of "
                 "capital times time; A receives thirty-three thousand rupees in all; find the total profit and B's share.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "more")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "lakh")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.at_word(n, "manages")
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
            text="One: the salary is eighteen thousand, and the remainder, thirty thousand, is shared equally, fifteen "
                 "thousand each: A gets thirty-three thousand and B fifteen thousand.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "salary")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "gets")
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_02",
            text="Two: the managing share is two thousand five hundred, and the remainder, twenty-two thousand five "
                 "hundred, is shared three to two: A gets sixteen thousand in all and B nine thousand.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "managing")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "gets")
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_03",
            text="Three: A's twenty percent is nine thousand, and the remainder, thirty-six thousand, is shared two to "
                 "three, fourteen thousand four hundred and twenty-one thousand six hundred: A gets twenty-three thousand "
                 "four hundred and B twenty-one thousand six hundred.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "percent")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "gets")
        self.play(FadeIn(rows[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_04",
            text="Four: the commission is thirty-three thousand times ten over one hundred and ten, three thousand. The "
                 "remainder, thirty thousand, is shared equally, so A's total is three thousand plus fifteen thousand: "
                 "eighteen thousand rupees.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "commission")
        self.play(FadeIn(rows[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "total")
        self.play(FadeIn(rows[3][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Answer key  ·  5 to 8", GOOD)
        table, rows = self.answer_table(head, ANSWERS_B, 5)

        n = self.narrate(
            id="answers_05",
            text="Five: the interest is four thousand and two thousand, and the remainder, twenty-four thousand, gives "
                 "twelve thousand each: A gets sixteen thousand and B fourteen thousand.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "interest")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "gets")
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_06",
            text="Six: A gets zero point one P plus three fifths of zero point nine P, zero point six four P, and B zero "
                 "point three six P. The difference, zero point two eight P, is fourteen thousand, so P is fifty thousand "
                 "rupees.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "plus")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "fifty")
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_07",
            text="Seven: the salary is thirty-six thousand, and the remainder, one lakh, is shared two to three to five, "
                 "so C gets thirty-six thousand plus fifty thousand: eighty-six thousand rupees.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "salary")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "eighty-six")
        self.play(FadeIn(rows[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_08",
            text="Eight: the capital-months are equal, one to one, so A gets zero point two P plus zero point four P, zero "
                 "point six P, which is thirty-three thousand. So P is fifty-five thousand, and B's share is twenty-two "
                 "thousand rupees.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "equal")
        self.play(FadeIn(rows[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "fifty-five")
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
            text="Recognise and move. The recognition cue: working partner, managing, salary, commission, allowance, "
                 "interest on capital or sleeping partner; pay first, then share.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "cue")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "pay")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_lens_02",
            text="The target time: forty-five seconds.",
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
            text="The sanity check: all receipts add up to the total profit, and the working partner receives more than "
                 "their plain capital share.",
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
        first = pill("pay the working partner first:  salary × months, x% of profit, commission or interest", GOOD, size=LABEL)
        rest = pill("then share the remainder in the agreed ratio", WORD, size=LABEL)
        after = pill("“after charging the commission”:    C = P × x/(100 + x)", RATIO, size=LABEL)
        whole = text("total from a difference:  write each receipt as a fraction of P", LABEL, INK, BOLD)
        cab = text("the shared cab: fuel first, then the fare", LABEL, MUTED)
        nxt = self.breadcrumb("Next", "Video 4 · Speed Tricks for Partnership")
        self.stack(head, [first, rest, after, whole, cab, nxt], buff=0.45, top=0.6)

        n = self.narrate(
            id="summary_01",
            text="Pay the working partner first: salary times months, x percent of the profit, commission or interest; "
                 "then share the remainder in the agreed ratio.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "first")
        self.play(FadeIn(first, scale=1.03))
        self.at_word(n, "remainder")
        self.play(FadeIn(rest, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_02",
            text="After charging the commission means C is P times x, over one hundred plus x.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "over")
        self.play(FadeIn(after, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_03",
            text="To find the total from a difference, write each receipt as a fraction of P.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "write")
        self.play(FadeIn(whole, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_04",
            text="Remember the shared cab.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "cab")
        self.play(FadeIn(cab, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_05",
            text="Next: speed tricks for partnership.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Next")
        self.play(FadeIn(nxt, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S16_summary")

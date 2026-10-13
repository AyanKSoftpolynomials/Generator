"""
animation.py for the LMS video generator.

Course : Pre-C-CAT - Section A - Quantitative Aptitude
Video  : Lesson 20 - Partnership - 02 - Changing Capital - Joining, Leaving & Withdrawals

Source script:
  C:\\Scripts\\Section A\\Aptitude\\Sessions 13-18 - Pipes, Time Distance, Partnership\\Lesson 20 - Partnership\\02 - Changing Capital - Joining, Leaving & Withdrawals.pdf

Built on the golden-reference pattern:
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``;
  * layouts stacked with next_to and guarded with ``no_overlap``; nothing is
    ever animated onto or into another box.

Lesson 20, Video 2 of 4. Not the first video of the lesson: a silent breadcrumb, a one-line recap of Video 1, then today's topic. No spoken course welcome.
The narration follows the script section by section. Amounts keep the script's Indian grouping and are spoken as lakh. The eight concept steps are shown as seven blocks over two screens ("joins after" and "leaves after" share one block). The six exam patterns are two-line blocks. The hook's timeline is shown as four dated rows.
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


def months(*segments):
    """Capital-months of one partner: segments are (capital, months)."""
    return sum(Fraction(c) * m for c, m in segments)


def shares(amount, *totals):
    return [Fraction(amount) * t / sum(totals) for t in totals]


# ---- the hook: the bootcamp ----
A_HOOK, B_HOOK = months((200000, 6), (150000, 6)), months((300000, 12 - 3))
assert (A_HOOK, B_HOOK) == (2100000, 2700000) and Fraction(A_HOOK, B_HOOK) == Fraction(7, 9)
assert shares(160000, A_HOOK, B_HOOK) == [70000, 90000] and 160000 // 16 == 10000

# ---- second worked example: 1/2 : 1/3 : 1/4, A withdraws half after 2 months ----
UNITS = [Fraction(1, d) * 12 for d in (2, 3, 4)]
A2, B2, C2 = months((6, 2), (3, 10)), months((4, 12)), months((3, 12))
assert UNITS == [6, 4, 3] and (A2, B2, C2) == (42, 48, 36) and shares(126000, A2, B2, C2) == [42000, 48000, 36000] and 126000 // 21 == 6000

# ---- exam patterns, traps, checkpoint, practice (answers computed) ----
assert shares(34000, months((60000, 12)), months((80000, 8))) == [18000, 16000] and (60000 * 12, 80000 * 8) == (720000, 640000)
assert shares(24000, months((50000, 12)), months((40000, 9))) == [15000, 9000]
assert months((80000, 4), (60000, 8)) == 800000 and shares(38000, 800000, months((60000, 12))) == [20000, 18000]
assert months((30000, 6), (40000, 6)) == 420000 and shares(32000, 420000, months((45000, 12))) == [14000, 18000]
assert 45000 * 12 == 60000 * (12 - 3) and Fraction(months((50000, 12)), months((75000, 10))) == Fraction(4, 5)
assert Fraction(months((70000, 12)), months((90000, 7))) == Fraction(4, 3) and shares(27000, months((36000, 8)), months((48000, 12))) == [9000, 18000]
assert [Fraction(1, d) * 12 for d in (3, 4, 6)] == [4, 3, 2] and shares(45000, 4, 3, 2) == [20000, 15000, 10000]
assert shares(60000, months((100000, 3), (60000, 9)), months((80000, 12))) == [28000, 32000]
assert shares(38000, months((40000, 6), (60000, 6)), months((50000, 6), (40000, 6))) == [20000, 18000]
assert Fraction(months((54000, 12)), months((72000, 6))) == Fraction(3, 2) and shares(45000, months((60000, 12)), months((72000, 8))) == [25000, 20000]
assert shares(69000, months((40000, 12)), months((60000, 9)), months((120000, 3))) == [24000, 27000, 18000]

OBJECTIVES = [("Split the year into segments", "and add capital × months for each partner"),
              ("Handle partners who join late or leave early", "and partners who withdraw or add money"),
              ("Clear fractional capital ratios with the LCM", "and find an unknown capital or joining time")]
STEPS_A = [("Draw a 12-month timeline", "“after x months” means x months from the start;  mark every month where anyone's capital changes"),
           ("Between two marks each capital is constant:  a segment", "segment contribution = capital in that segment × months in that segment"),
           ("Each partner's total = the sum of their segments", "the profit is shared in the ratio of these totals"),
           ("Joins after x months:  in for 12 − x months, not x", "leaves after x months:  in for x months")]
STEPS_B = [("Withdraws or adds money after x months", "old capital × x,  plus new capital × (12 − x)"),
           ("Fractional capitals:  multiply every term by the LCM of the denominators", "1/2 : 1/3 : 1/4,  × 12,  gives 6 : 4 : 3"),
           ("Unknown capital or time", "write the capital-months ratio equal to the profit ratio and solve one equation")]
FORMULAS = ["Partner's capital-months   =   sum of (capital in segment × months in segment)",
            "Joins after x months:     C × (12 − x)                   Leaves after x months:     C × x",
            "Change after x months:     old capital × x  +  new capital × (12 − x)",
            "Fractional capitals:     multiply by the LCM of the denominators"]
PATTERNS = [("Joins after x months", "A ₹60,000;   B joins after 4 months with ₹80,000;   profit ₹34,000", "7,20,000 : 6,40,000 = 9 : 8", "₹18,000 and ₹16,000"),
            ("Leaves after x months", "A ₹50,000, B ₹40,000;   B leaves after 9 months;   profit ₹24,000", "6,00,000 : 3,60,000 = 5 : 3", "₹15,000 and ₹9,000"),
            ("Withdrawal", "A ₹80,000, withdraws ₹20,000 after 4 months;   B ₹60,000;   profit ₹38,000", "8,00,000 : 7,20,000 = 10 : 9", "₹20,000 and ₹18,000"),
            ("Addition", "A ₹30,000, adds ₹10,000 after 6 months;   B ₹45,000;   profit ₹32,000", "4,20,000 : 5,40,000 = 7 : 9", "₹14,000 and ₹18,000"),
            ("Fractional capitals", "1/2 : 1/3 : 1/4,  same time", "× 12", "6 : 4 : 3"),
            ("Unknown joining time", "A ₹45,000 all year;   B joins with ₹60,000;   profits equal", "5,40,000 = 60,000 × (12 − x)", "after 3 months")]
TRAPS = [("Trap 1  ·  “joins after 4 months” counted as 4 months", "A invests ₹60,000; B joins after 4 months with ₹80,000.  Ratio?",
          "60,000 × 12 : 80,000 × 4 = 9 : 4", "60,000 × 12 : 80,000 × 8 = 9 : 8",
          "A partner who joins after x months is in for the remaining 12 − x."),
         ("Trap 2  ·  a withdrawal applied to the whole year",
          "A invests ₹80,000 and withdraws ₹20,000 after 4 months.  A's capital-months?",
          "60,000 × 12  =  7,20,000", "3,20,000 + 4,80,000 = 8,00,000",
          "A change applies only from the month it happens: each segment keeps its own capital."),
         ("Trap 3  ·  fractional ratios read from the denominators", "Capitals in the ratio 1/2 : 1/3 : 1/4.  Whole-number ratio?",
          "2 : 3 : 4", "6 : 4 : 3",
          "1/2 is the largest, so A has the largest share.  Multiply by the LCM.")]
PRACTICE_A = [("L1", "A starts a business with ₹70,000.  After 5 months, B joins with ₹90,000.  Find the ratio of their profits for the year."),
              ("L1", "A and B start with ₹36,000 and ₹48,000.  A leaves after 8 months.  The year's profit is ₹27,000.  Find each share."),
              ("L2", "A, B and C invest capitals in the ratio 1/3 : 1/4 : 1/6 for the same period.  The profit is ₹45,000.  Each share?"),
              ("L2", "A starts with ₹1,00,000 and withdraws ₹40,000 after 3 months.  B invests ₹80,000 all year.  Profit ₹60,000.  Shares?"),
              ("L2", "A and B start with ₹40,000 and ₹50,000.  After 6 months A adds ₹20,000, B withdraws ₹10,000.  Profit ₹38,000.  Shares?")]
PRACTICE_B = [("L3", "A starts with ₹54,000; later B joins with ₹72,000.  The year's profit is shared 3 : 2.  After how many months did B join?"),
              ("L3", "A invests ₹60,000 all year.  B joins after 4 months.  Of a ₹45,000 profit B receives ₹20,000.  B's investment?"),
              ("L3", "A starts with ₹40,000.  B joins after 3 months with ₹60,000; C joins 6 months after B with ₹1,20,000.  Profit ₹69,000.  Shares?")]
ANSWERS_A = [("70,000 × 12 : 90,000 × 7  =  8,40,000 : 6,30,000", "4 : 3"),
             ("36,000 × 8 : 48,000 × 12  =  2,88,000 : 5,76,000  =  1 : 2", "₹9,000 and ₹18,000"),
             ("× 12 gives 4 : 3 : 2;      1 part = 45,000 ÷ 9 = 5,000", "₹20,000, ₹15,000, ₹10,000"),
             ("A:  1,00,000 × 3 + 60,000 × 9 = 8,40,000;    B:  9,60,000;    7 : 8", "₹28,000 and ₹32,000")]
ANSWERS_B = [("A:  6,00,000;    B:  50,000 × 6 + 40,000 × 6 = 5,40,000;    10 : 9", "₹20,000 and ₹18,000"),
             ("54,000 × 12 : 72,000 × m = 3 : 2;     m = 6 months in", "B joined after 6 months"),
             ("A's share 25,000:  A : B = 5 : 4;     60,000 × 12 : 8x = 5 : 4", "x  =  ₹72,000"),
             ("4,80,000 : 5,40,000 : 3,60,000 = 8 : 9 : 6;     1 part = 3,000", "₹24,000, ₹27,000, ₹18,000")]
LENS = [("Recognition cue", "“joins after”, “leaves after”, “withdraws”, “adds”, “some months later”:  draw the 12-month timeline"),
        ("Target time", "35 seconds for one change;  45 seconds for two or more"),
        ("Sanity check", "no partner's months exceed 12;  each segment uses the capital in force during that segment")]


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


class ChangingCapitalVideo(LMSScene):
    lesson_title = "Changing Capital: Joining, Leaving & Withdrawals"

    def construct(self):
        self.camera.background_color = BG

        self.intro()
        self.hook()
        self.objectives()
        self.why_this_matters()
        self.timeline_and_segments()
        self.changes_fractions_unknowns()
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

        crumb = self.breadcrumb("Quantitative Aptitude", "Lesson 20 · Partnership", "Video 2 of 4")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        recap = VGroup(text("last video", SMALL, MUTED), pill("profit ratio = ratio of capital × time", WORD, size=LABEL)).arrange(DOWN, buff=0.25)
        title = fit_width(text("Changing Capital: Joining, Leaving & Withdrawals", TITLE, INK, BOLD), SAFE_W - 0.4)
        today = text("today: a fair ratio when the money keeps moving", LABEL, FOCUS)
        block = VGroup(recap, title, today).arrange(DOWN, buff=0.7)
        fit_within(block, SAFE_W, SAFE_H - crumb.height - 0.9)
        block.next_to(crumb, DOWN, buff=0.7)
        self.no_overlap(crumb, recap, title, today)
        self.validator.check_in_frame(VGroup(crumb, block))

        n = self.narrate(
            id="intro_01",
            text="In the last video, profit was shared in the ratio of capital times time.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.at_word(n, "ratio")
        self.play(FadeIn(recap, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="intro_02",
            text="Today: changing capital, with partners joining, leaving and withdrawing, and a fair ratio when the money "
                 "keeps moving.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "changing")
        self.play(FadeIn(title, shift=UP * 0.1))
        self.at_word(n, "fair")
        self.play(FadeIn(today, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_intro")

    # ============================================== 1. HOOK ==========

    def hook(self):
        self.scene_start("S01_hook", title="Hook")

        head = self.heading("A coding bootcamp, month by month")
        events = VGroup(*[VGroup(pill(m, WORD, size=SMALL), text(t, LABEL, INK, BOLD)).arrange(RIGHT, buff=0.4)
                          for m, t in (("month 0", "A invests ₹2,00,000"), ("month 3", "B joins with ₹3,00,000"),
                                       ("month 6", "A withdraws ₹50,000"), ("month 12", "profit ₹1,60,000"))])\
            .arrange(DOWN, buff=0.2, aligned_edge=LEFT)
        puzzle = text("no single “capital × time” works for A", LABEL, MUTED)
        ask = pill("how do you build a fair ratio when the money keeps moving?", FOCUS, size=LABEL)
        self.stack(head, [events, puzzle, ask], buff=0.4, top=0.5)
        self.no_overlap(*events)

        n = self.narrate(
            id="hook_01",
            text="A starts a coding bootcamp with two lakh rupees. Three months later, B joins with three lakh.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "starts")
        self.play(FadeIn(events[0], shift=UP * 0.1))
        self.at_word(n, "joins")
        self.play(FadeIn(events[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_02",
            text="Six months after the start, A takes fifty thousand rupees out to cover a personal expense. At the end of "
                 "the year, the profit is one lakh sixty thousand rupees.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "takes")
        self.play(FadeIn(events[2], shift=UP * 0.1))
        self.at_word(n, "profit")
        self.play(FadeIn(events[3], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_03",
            text="A's capital changed halfway through, and B was not there for the first quarter. No single capital times "
                 "time works for A.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "changed")
        self.play(Indicate(events[2], color=FOCUS, scale_factor=1.03))
        self.at_word(n, "single")
        self.play(FadeIn(puzzle, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_04",
            text="How do you build a fair ratio when the money keeps moving?",
            voice="default",
            subtitle=True,
            pause_after=3.0,
        )
        self.at_word(n, "fair")
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
            text="First, split the year into segments and add capital times months for each partner.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "split")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "add")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="objectives_03",
            text="Second, handle partners who join late, leave early, withdraw or add money.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "join")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "withdraw")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="objectives_04",
            text="Third, clear fractional capital ratios with the L C M, and find an unknown capital or joining time.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "clear")
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
        most = pill("most exam questions are not “same capital, same time”", WORD, size=LABEL)
        moves = text("someone joins, leaves or changes their stake", LABEL, INK)
        method = text("the method does not change; only the bookkeeping does", LABEL, INK, BOLD)
        line = pill("a timeline makes the bookkeeping mechanical", FOCUS, size=LABEL)
        self.stack(head, [most, moves, method, line], buff=0.7, top=0.9)

        n = self.narrate(
            id="why_this_matters_01",
            text="Most exam partnership questions are not same capital, same time. Someone joins, leaves or changes their "
                 "stake.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "Most")
        self.play(FadeIn(most, shift=UP * 0.1))
        self.at_word(n, "joins")
        self.play(FadeIn(moves, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="why_this_matters_02",
            text="The method does not change; only the bookkeeping does, and a timeline makes the bookkeeping mechanical.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "method")
        self.play(FadeIn(method, shift=UP * 0.1))
        self.at_word(n, "timeline")
        self.play(FadeIn(line, scale=1.03))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_why_this_matters")

    # ============================================== 4. CONCEPT - THE TIMELINE AND ITS SEGMENTS ==========

    def timeline_and_segments(self):
        self.scene_start("S04_timeline_and_segments", title="Concept - The Timeline and Its Segments")

        head = self.heading("The timeline and its segments")
        blocks = two_line_blocks(STEPS_A, WORD)
        self.stack(head, list(blocks), buff=0.5, top=0.7, align=LEFT)

        n = self.narrate(
            id="timeline_and_segments_01",
            text="Draw a twelve-month timeline. After x months means x months from the start of the business. Mark every "
                 "month where anyone's capital changes.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "timeline")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "start")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.at_word(n, "Mark")
        self.play(Indicate(blocks[0][1], color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="timeline_and_segments_02",
            text="Between two marks, each capital is constant: a segment. The segment's contribution is the capital in "
                 "that segment times the months in that segment.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "segment")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "times")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="timeline_and_segments_03",
            text="Each partner's total is the sum of their segments, and the profit is shared in the ratio of these "
                 "totals.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "sum")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "shared")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="timeline_and_segments_04",
            text="A partner who joins after x months has money in for twelve minus x months, not x. A partner who leaves "
                 "after x months has money in for x months.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "joins")
        self.play(FadeIn(blocks[3][0], shift=RIGHT * 0.2))
        self.at_word(n, "leaves")
        self.play(FadeIn(blocks[3][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_timeline_and_segments")

    # ============================================== 5. CONCEPT - CHANGES, FRACTIONS AND UNKNOWNS ==========

    def changes_fractions_unknowns(self):
        self.scene_start("S05_changes_fractions_unknowns", title="Concept - Changes, Fractions and Unknowns")

        head = self.heading("Changes, fractions and unknowns")
        blocks = two_line_blocks(STEPS_B, WORD)
        self.stack(head, list(blocks), buff=0.75, top=1.0, align=LEFT)

        n = self.narrate(
            id="changes_fractions_unknowns_01",
            text="A partner who withdraws or adds money after x months counts the old capital times x, plus the new "
                 "capital times twelve minus x.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "withdraws")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "plus")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="changes_fractions_unknowns_02",
            text="For fractional capitals, multiply every term by the L C M of the denominators: a half, a third and a "
                 "quarter, times twelve, give six to four to three.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "multiply")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "give")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="changes_fractions_unknowns_03",
            text="For an unknown capital or time, write the capital-months ratio equal to the profit ratio and solve one "
                 "equation.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "unknown")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "write")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_changes_fractions_unknowns")

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
            text="Here is the formula box. A partner's capital-months are the sum of capital times months over every "
                 "segment.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "box")
        self.play(FadeIn(box[0]))
        self.at_word(n, "sum")
        self.play(FadeIn(lines[0], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_box_02",
            text="Joins after x months: C times twelve minus x. Leaves after x months: C times x.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Joins")
        self.play(FadeIn(lines[1], shift=RIGHT * 0.2))
        self.at_word(n, "Leaves")
        self.play(Indicate(lines[1], color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_box_03",
            text="A change after x months: old capital times x, plus new capital times twelve minus x.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "change")
        self.play(FadeIn(lines[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_box_04",
            text="And fractional capitals: multiply by the L C M of the denominators.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "fractional")
        self.play(FadeIn(lines[3], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_formula_box")

    # ============================================== 7. THE ANALOGY - AN ELECTRICITY METER ==========

    def analogy(self):
        self.scene_start("S07_analogy", title="The Analogy - An Electricity Meter")

        head = self.heading("An electricity meter")
        kwh = pill("the bill counts kilowatt-hours:   power × hours", WORD, size=LABEL)
        added = text("added up over every period when the load changed:  a heater for 2 h plus a fan for 10 h is one total", LABEL, INK)
        fit_width(added, SAFE_W - 0.6)
        cap = pill("capital-months:   add every period a partner's money was in the business", FOCUS, size=LABEL)
        stops = VGroup(text("Where the analogy stops", LABEL, BAD, BOLD),
                       text("electricity tariffs can change with the time of day", LABEL, INK),
                       text("in partnership questions every month counts the same", LABEL, MUTED)).arrange(DOWN, buff=0.2)
        self.stack(head, [kwh, added, cap, stops], buff=0.6, top=0.7)

        n = self.narrate(
            id="analogy_01",
            text="An electricity bill counts kilowatt-hours: power times hours, added up over every period when the load "
                 "changed.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "bill")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "times")
        self.play(FadeIn(kwh, shift=UP * 0.1))
        self.at_word(n, "added")
        self.play(FadeIn(added, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_02",
            text="A heater for two hours plus a fan for ten hours is one total.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "total")
        self.play(Indicate(added, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_03",
            text="Capital-months are the same: add up every period in which a partner's money was in the business.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "same")
        self.play(FadeIn(cap, scale=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_04",
            text="Where the analogy stops: electricity tariffs can change with the time of day. In partnership questions "
                 "every month counts the same.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "stops")
        self.play(FadeIn(stops[0], shift=UP * 0.1))
        self.at_word(n, "tariffs")
        self.play(FadeIn(stops[1], shift=UP * 0.1))
        self.at_word(n, "month")
        self.play(FadeIn(stops[2], shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S07_analogy")

    # ============================================== 8. WORKED EXAMPLE - CLOSING THE HOOK ==========

    def hook_solved(self):
        self.scene_start("S08_hook_solved", title="Worked Example - Closing the Hook")

        head = self.heading("The bootcamp:   A and B")
        steps = self.solve_steps([("A:    2,00,000 × 6  +  1,50,000 × 6  =  12,00,000 + 9,00,000", "=  21,00,000"),
                                  ("B joins after 3 months:    3,00,000 × 9", "=  27,00,000"),
                                  ("Ratio 21 : 27 = 7 : 9;       1 part = 1,60,000 ÷ 16", "=  ₹10,000"),
                                  ("A gets ₹70,000", "B gets ₹90,000")])
        self.stack(head, [steps], top=1.0)
        self.no_overlap(*steps)

        n = self.narrate(
            id="hook_solved_01",
            text="A: two lakh times six, plus one and a half lakh times six, is twelve lakh plus nine lakh: twenty-one "
                 "lakh.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "times")
        self.play(FadeIn(steps[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "twenty-one")
        self.play(FadeIn(steps[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_solved_02",
            text="B joins after three months, so three lakh times nine: twenty-seven lakh.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "joins")
        self.play(FadeIn(steps[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "twenty-seven")
        self.play(FadeIn(steps[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_solved_03",
            text="The ratio is twenty-one to twenty-seven, seven to nine, and one part is one lakh sixty thousand divided "
                 "by sixteen: ten thousand rupees.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "ratio")
        self.play(FadeIn(steps[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "ten")
        self.play(FadeIn(steps[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_solved_04",
            text="A gets seventy thousand rupees and B gets ninety thousand.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "seventy")
        self.play(FadeIn(steps[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "ninety")
        self.play(FadeIn(steps[3][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S08_hook_solved")

    # ============================================== 9. A SECOND WORKED EXAMPLE - FRACTIONAL CAPITALS WITH A WITHDRAWAL ==========

    def second_example(self):
        self.scene_start("S09_second_example", title="A Second Worked Example - Fractional Capitals with a Withdrawal")

        head = self.heading("Fractional capitals with a withdrawal")
        ask = text("capitals 1/2 : 1/3 : 1/4; after 2 months A withdraws half his capital; profit ₹1,26,000:   each share?", LABEL, MUTED)
        fit_width(ask, SAFE_W - 0.6)
        steps = self.solve_steps([("Clear the fractions:    × 12", "6 : 4 : 3 units"),
                                  ("A:  6 × 2 + 3 × 10 = 42;       B:  4 × 12 = 48;       C:  3 × 12", "=  36"),
                                  ("42 : 48 : 36 = 7 : 8 : 6;       1 part = 1,26,000 ÷ 21", "=  ₹6,000"),
                                  ("A ₹42,000,    B ₹48,000", "C ₹36,000")])
        self.stack(head, [ask, steps], buff=0.7, top=0.7)
        self.no_overlap(*steps)

        n = self.narrate(
            id="second_example_01",
            text="A, B and C start a business with capitals in the ratio a half, a third and a quarter. After two months, "
                 "A withdraws half of his capital. The year's profit is one lakh twenty-six thousand rupees. Find each "
                 "share.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "start")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "ratio")
        self.play(FadeIn(ask, shift=UP * 0.1))
        self.at_word(n, "withdraws")
        self.play(Indicate(ask, color=FOCUS, scale_factor=1.03))
        self.at_word(n, "profit")
        self.play(Indicate(ask, color=FOCUS, scale_factor=1.03))
        self.at_word(n, "Find")
        self.play(Indicate(ask, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_02",
            text="Clear the fractions: multiplying by twelve gives six to four to three, so take the capitals as six, four "
                 "and three units.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "multiplying")
        self.play(FadeIn(steps[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "units")
        self.play(FadeIn(steps[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_03",
            text="A: six times two plus three times ten is forty-two. B: four times twelve is forty-eight. C: three times "
                 "twelve is thirty-six.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "forty-two")
        self.play(FadeIn(steps[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "forty-eight")
        self.play(Indicate(steps[1][1], color=FOCUS, scale_factor=1.03))
        self.at_word(n, "thirty-six")
        self.play(FadeIn(steps[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_04",
            text="Forty-two to forty-eight to thirty-six is seven to eight to six, and one part is one lakh twenty-six "
                 "thousand divided by twenty-one: six thousand rupees.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "seven")
        self.play(FadeIn(steps[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "thousand", occurrence=2)
        self.play(FadeIn(steps[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_05",
            text="A gets forty-two thousand, B forty-eight thousand, and C thirty-six thousand rupees.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "forty-two")
        self.play(FadeIn(steps[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "thirty-six")
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
            text="Joins after some months: A sixty thousand; B joins after four months with eighty thousand; profit "
                 "thirty-four thousand. Seven lakh twenty thousand to six lakh forty thousand, nine to eight: eighteen "
                 "thousand and sixteen thousand.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Joins")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "lakh")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_03",
            text="Leaves after some months: A fifty thousand, B forty thousand; B leaves after nine months; profit "
                 "twenty-four thousand. Six lakh to three lakh sixty thousand, five to three: fifteen thousand and nine "
                 "thousand.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Leaves")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "lakh")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_04",
            text="A withdrawal: A eighty thousand, withdrawing twenty thousand after four months; B sixty thousand; profit "
                 "thirty-eight thousand. Eight lakh to seven lakh twenty thousand, ten to nine: twenty thousand and "
                 "eighteen thousand.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "withdrawal")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "lakh")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Exam patterns  ·  4 to 6 of 6")
        blocks = self.pattern_blocks(PATTERNS[3:6])
        self.stack(head, list(blocks), buff=0.6, top=0.8, align=LEFT)

        n = self.narrate(
            id="exam_patterns_05",
            text="An addition: A thirty thousand, adding ten thousand after six months; B forty-five thousand; profit "
                 "thirty-two thousand. Four lakh twenty thousand to five lakh forty thousand, seven to nine: fourteen "
                 "thousand and eighteen thousand.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "addition")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "lakh")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_06",
            text="Fractional capitals: a half, a third and a quarter, for the same time. Times twelve: six to four to "
                 "three.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Fractional")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "Times")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_07",
            text="An unknown joining time: A forty-five thousand all year; B joins with sixty thousand; the profits are "
                 "equal. Five lakh forty thousand equals sixty thousand times twelve minus x: B joined after three months.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "unknown")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "equals")
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
            text="Trap one: joins after four months, counted as four months. A invests sixty thousand rupees; B joins "
                 "after four months with eighty thousand: what is the ratio?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "counted")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "invests")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_02",
            text="The wrong instinct gives B four months: nine to four. The correct answer gives B eight months: nine to "
                 "eight.",
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
            text="The rule: a partner who joins after x months is in for the remaining twelve minus x.",
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
            text="Trap two: a withdrawal applied to the whole year. A invests eighty thousand rupees and withdraws twenty "
                 "thousand after four months: what are A's capital-months?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "applied")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "invests")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_05",
            text="The wrong instinct takes sixty thousand for twelve months: seven lakh twenty thousand. The correct "
                 "answer is eighty thousand for four months plus sixty thousand for eight: eight lakh.",
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
            text="The rule: a change applies only from the month it happens. Every segment keeps its own capital.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "rule")
        self.play(FadeIn(rule, shift=UP * 0.1))
        self.at_word(n, "segment")
        self.play(Indicate(rule, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)
        self.clear_stage()

        head, q, wrong, right, rule = self.show_trap(TRAPS[2])

        n = self.narrate(
            id="traps_07",
            text="Trap three: fractional ratios read from the denominators. Capitals are in the ratio a half, a third and "
                 "a quarter: what is the whole-number ratio?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "denominators")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "Capitals")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_08",
            text="The wrong instinct says two to three to four. The correct answer is six to four to three.",
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
            text="The rule: a half is the largest of the three, so A must have the largest share. Multiply by the L C M; "
                 "never just copy the denominators.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "rule")
        self.play(FadeIn(rule, shift=UP * 0.1))
        self.at_word(n, "Multiply")
        self.play(Indicate(rule, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S11_traps")

    # ============================================== 12. CHECKPOINT ==========

    def checkpoint(self):
        self.scene_start("S12_checkpoint", title="Checkpoint")

        head = self.heading("Checkpoint  ·  your turn")
        given = pill("A starts with ₹50,000; after 2 months B joins with ₹75,000:   profit ratio?", FOCUS, size=LABEL)
        work = VGroup(text("50,000 × 12 : 75,000 × 10  =  6,00,000 : 7,50,000", BODY, INK, BOLD), text("=  4 : 5", BODY, GOOD, BOLD)).arrange(RIGHT, buff=0.5)
        self.stack(head, [given, work], buff=1.0, top=1.0)
        self.no_overlap(*work)

        n = self.narrate(
            id="checkpoint_01",
            text="Your turn. A starts a business with fifty thousand rupees. After two months, B joins with seventy-five "
                 "thousand. Find the ratio of their profits at the end of the year.",
            voice="default",
            subtitle=True,
            pause_after=10.0,
        )
        self.at_word(n, "turn")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "starts")
        self.play(FadeIn(given, scale=1.03))
        self.at_word(n, "joins")
        self.play(Indicate(given, color=FOCUS, scale_factor=1.03))
        self.at_word(n, "ratio")
        self.play(Indicate(given, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="checkpoint_02",
            text="Fifty thousand times twelve, to seventy-five thousand times ten, is six lakh to seven and a half lakh: "
                 "four to five.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "times")
        self.play(FadeIn(work[0], shift=UP * 0.1))
        self.at_word(n, "four")
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
            text="Level one, question one: A starts a business with seventy thousand rupees; after five months, B joins "
                 "with ninety thousand; find the ratio of their profits at the end of the year. Question two: A and B "
                 "start a business with thirty-six thousand and forty-eight thousand rupees; A leaves after eight months; "
                 "the year's profit is twenty-seven thousand; find each share.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "joins")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "leaves")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="practice_02",
            text="Level two, question three: A, B and C invest capitals in the ratio a third, a quarter and a sixth for "
                 "the same period; the profit is forty-five thousand rupees; find each share. Question four: A starts with "
                 "one lakh rupees and withdraws forty thousand after three months; B invests eighty thousand for the whole "
                 "year; the profit is sixty thousand; find each share. Question five: A and B start with forty thousand "
                 "and fifty thousand rupees; after six months, A adds twenty thousand and B withdraws ten thousand; the "
                 "year's profit is thirty-eight thousand; find each share.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "ratio")
        self.play(FadeIn(rows[2], shift=RIGHT * 0.2))
        self.at_word(n, "withdraws")
        self.play(FadeIn(rows[3], shift=RIGHT * 0.2))
        self.at_word(n, "adds")
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
            text="Level three, question six: A starts a business with fifty-four thousand rupees; some months later, B "
                 "joins with seventy-two thousand; at the end of the year, the profit is shared in the ratio three to two; "
                 "after how many months did B join? Question seven: A invests sixty thousand rupees for the whole year, "
                 "and B joins after four months; of a profit of forty-five thousand, B receives twenty thousand; how much "
                 "did B invest? Question eight: A starts a business with forty thousand rupees; B joins after three months "
                 "with sixty thousand, and C joins six months after B with one lakh twenty thousand; the year's profit is "
                 "sixty-nine thousand; find each share.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "later")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "receives")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.at_word(n, "C")
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
            text="One: seventy thousand times twelve, to ninety thousand times seven, is eight lakh forty thousand to six "
                 "lakh thirty thousand: four to three.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "times")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "four")
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_02",
            text="Two: thirty-six thousand times eight, to forty-eight thousand times twelve, is one to two, so A gets "
                 "nine thousand and B eighteen thousand.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "times")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "gets")
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_03",
            text="Three: multiplying by twelve gives four to three to two; one part is forty-five thousand divided by "
                 "nine, five thousand, so the shares are twenty thousand, fifteen thousand and ten thousand.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "multiplying")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "shares")
        self.play(FadeIn(rows[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_04",
            text="Four: A has one lakh for three months plus sixty thousand for nine, eight lakh forty thousand; B has "
                 "nine lakh sixty thousand. Seven to eight: A gets twenty-eight thousand and B thirty-two thousand.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "plus")
        self.play(FadeIn(rows[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "gets")
        self.play(FadeIn(rows[3][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Answer key  ·  5 to 8", GOOD)
        table, rows = self.answer_table(head, ANSWERS_B, 5)

        n = self.narrate(
            id="answers_05",
            text="Five: A has six lakh, and B has fifty thousand for six months plus forty thousand for six, five lakh "
                 "forty thousand. Ten to nine: A gets twenty thousand and B eighteen thousand.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "lakh")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "gets")
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_06",
            text="Six: fifty-four thousand times twelve, to seventy-two thousand times m, is three to two, so m is six. "
                 "B's money was in for six months, so B joined after six months.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "times")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "joined")
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_07",
            text="Seven: A's share is twenty-five thousand, so A to B is five to four. Sixty thousand times twelve, to "
                 "eight x, is five to four, so x is seventy-two thousand rupees.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "share")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "seventy-two")
        self.play(FadeIn(rows[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_08",
            text="Eight: C joins after nine months. Four lakh eighty thousand, five lakh forty thousand and three lakh "
                 "sixty thousand is eight to nine to six; one part is three thousand, so the shares are twenty-four "
                 "thousand, twenty-seven thousand and eighteen thousand.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "joins")
        self.play(FadeIn(rows[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "shares")
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
            text="Recognise and move. The recognition cue: joins after, leaves after, withdraws, adds or some months "
                 "later; draw the twelve-month timeline.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "cue")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "draw")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_lens_02",
            text="The target time: thirty-five seconds for one change, and forty-five seconds for two or more.",
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
            text="The sanity check: every partner's months add up to no more than twelve, and each segment uses the "
                 "capital in force during that segment.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "sanity")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "twelve")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S15_exam_lens")

    # ============================================== 16. QUICK REVISION AND SUMMARY ==========

    def summary(self):
        self.scene_start("S16_summary", title="Quick Revision and Summary")

        head = self.heading("Quick revision")
        split = pill("split the year at every change;    capital × months per segment;    add", GOOD, size=LABEL)
        both = VGroup(pill("joins after x:  in for 12 − x", WORD, size=LABEL), pill("leaves after x:  in for x", WORD, size=LABEL)).arrange(RIGHT, buff=0.5)
        frac = pill("fractional capitals:   clear them with the LCM first", RATIO, size=LABEL)
        meter = text("the electricity meter: add every period", LABEL, MUTED)
        nxt = self.breadcrumb("Next", "Video 3 · Working & Sleeping Partners")
        self.stack(head, [split, both, frac, meter, nxt], buff=0.6, top=0.7)
        self.no_overlap(*both)

        n = self.narrate(
            id="summary_01",
            text="Split the year at every change, multiply capital by months in each segment, and add each partner's "
                 "segments.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "Split")
        self.play(FadeIn(split, scale=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_02",
            text="A joiner after x months is in for twelve minus x; a leaver after x months is in for x.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "joiner")
        self.play(FadeIn(both[0], shift=UP * 0.1))
        self.at_word(n, "leaver")
        self.play(FadeIn(both[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_03",
            text="Clear fractional capitals with the L C M before anything else.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Clear")
        self.play(FadeIn(frac, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_04",
            text="Remember the electricity meter.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "meter")
        self.play(FadeIn(meter, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_05",
            text="Next: working and sleeping partners.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Next")
        self.play(FadeIn(nxt, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S16_summary")

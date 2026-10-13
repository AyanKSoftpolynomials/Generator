"""
animation.py for the LMS video generator.

Course : Pre-C-CAT - Section A - Quantitative Aptitude
Video  : Lesson 18 - Pipes & Cistern - 04 - Leaks & Cistern Problems

Source script:
  C:\\Scripts\\Section A\\Aptitude\\Sessions 13-18 - Pipes, Time Distance, Partnership\\Lesson 18 - Pipes & Cistern\\04 - Leaks & Cistern Problems.pdf

Built on the golden-reference pattern:
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``;
  * layouts stacked with next_to and guarded with ``no_overlap``; nothing is
    ever animated onto or into another box.

Lesson 18, Video 4 of 5. Not the first video of the lesson: a silent breadcrumb, a one-line recap of Video 3, then today's topic. No spoken course welcome.
The narration follows the script section by section. The eight concept steps are split over two screens. The six exam patterns are shown as two-line blocks. Two bars (4 and 3 units an hour) are drawn beside the hook's solution.
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
from math import lcm


def leak_time(x, y):
    """Fill time rises from x to y because of a leak: the leak alone empties a full tank in xy/(y − x)."""
    t = Fraction(x * y, y - x)
    assert Fraction(1, x) - Fraction(1, y) == 1 / t
    return t


# ---- the hook: fills in 6 h, with a leak 8 h ----
HOOK = leak_time(6, 8)
assert HOOK == 24 and lcm(6, 8) == 24 and (24 // 6, 24 // 8) == (4, 3) and 8 - 6 == 2 and HOOK == 12 * 2
assert Fraction(1, 2) == 3 * Fraction(1, 6)                                  # a 2-hour leak would be 3 times the pipe

# ---- second worked example: capacity from a tap in litres ----
TAP = 4 * 60
CAPACITY = TAP / (Fraction(1, 6) - Fraction(1, 8))
assert TAP == 240 and Fraction(1, 6) - Fraction(1, 8) == Fraction(1, 24) and CAPACITY == 5760

# ---- exam patterns, traps, checkpoint, practice (answers computed) ----
assert leak_time(9, 10) == 90 and 1 / (Fraction(1, 12) + Fraction(1, 15) - Fraction(1, 10)) == 20
assert (4 - 1) * 20 == 60 and (60 // 4, 60 // 1) == (15, 60)
assert 600 / (Fraction(1, 6) - Fraction(1, 12) - Fraction(1, 20)) == 18000 and Fraction(1, 12) - Fraction(1, 20) == Fraction(1, 30)
assert leak_time(5, 6) == 30 and leak_time(4, 5) == 20 and 1 / (Fraction(1, 10) - Fraction(1, 15)) == 30
assert 6 * 60 / (Fraction(1, 10) - Fraction(1, 12)) == 21600
SECOND_HALF = Fraction(1, 2) / (6 + 1 - 3)
assert SECOND_HALF == Fraction(1, 8) and 1 / (Fraction(1, 6) - SECOND_HALF) == 24

OBJECTIVES = [("Find a leak's emptying time", "from the change in fill time"),
              ("Find a tank's capacity", "when a leak or tap is given in litres per minute"),
              ("Solve cistern problems with an inlet, a leak and an extra tap", "and with rate ratios")]
STEPS_A = [("A leak is an outlet that is always on", "a negative rate, working whenever there is water in the tank"),
           ("Leak rate = rate without the leak − rate with the leak", "fill time rises from x to y:  rate 1/x − 1/y;  it empties a full tank in xy/(y − x)"),
           ("“Takes d hours longer” means y = x + d", "add first, then use the formula:  d itself is not the leak's time"),
           ("Litres and fractions meet through the capacity C", "each pipe's rate = C ÷ its time;  a litre flow = the difference of two such rates")]
STEPS_B = [("Keep one time unit", "times in hours, flow in litres per minute:  convert the flow to litres per hour (× 60)"),
           ("An inlet, a leak and an extra tap:  one equation", "inlet − leak − tap  =  the net rate you observe"),
           ("Rate ratios give parts directly", "pipe 4 times as fast as the leak:  pipe 4 parts, leak 1, net 3;  the given time belongs to the net"),
           ("A leak that starts later is a stage problem", "fill to the level where the leak begins, then use the reduced net rate (Video 3)")]
FORMULAS = ["Leak rate  =  1/x − 1/y;         the leak alone empties a full tank in  xy/(y − x)",
            "“d hours longer”:      y  =  x + d",
            "Capacity C:      rate  =  C ÷ time;        a litre flow  =  the difference of two such rates",
            "Inlet − leak − tap   =   observed net rate",
            "Ratio k : 1  (pipe : leak):      net  =  k − 1 parts"]
PATTERNS = [("Fill time increases", "fills in 6 h;   with a leak, 8 h", "24 units:   4 − 3 = 1", "leak empties in 24 h"),
            ("“d hours longer”", "fills in 9 h;   the leak adds 1 h", "90 units:   10 − 9 = 1", "leak empties in 90 h"),
            ("Two inlets and a leak", "A 12 h, B 15 h;   with a leak, 10 h", "60 units:   9 − 6 = 3", "leak empties in 20 h"),
            ("Rate ratio", "pipe 4 × leak;   with the leak, fills in 20 h", "net 3 parts × 20 = 60 parts", "pipe alone 15 h"),
            ("Tap and leak in litres", "leak 6 h;   tap 4 L/min;   now empties in 8 h", "tap = C/24 per hour = 240 L", "5,760 L"),
            ("Inlet, leak and extra tap", "inlet 6 h, leak 12 h, tap draws 10 L/min;   fills in 20 h", "C/6 − C/12 − 600 = C/20", "18,000 L")]
TRAPS = [("Trap 1  ·  subtracting the times", "A pipe fills a tank in 6 hours; with a leak it takes 8.  Leak alone?",
          "8 − 6  =  2 hours", "1/6 − 1/8 = 1/24:  24 hours",
          "Subtract rates, not times.  The leak must be slower than the pipe, or it never fills."),
         ("Trap 2  ·  litres per minute mixed with hours", "Tap = C/24 litres an hour, and the tap admits 4 litres a minute.  Capacity?",
          "C/24 = 4:  C = 96 litres", "4 L/min = 240 L/h:  5,760 L",
          "Put every rate in the same time unit before equating."),
         ("Trap 3  ·  a rate ratio used as a time ratio",
          "A pipe fills 4 times as fast as a leak empties.  With the leak it fills in 20 h.  Pipe alone?",
          "20 ÷ 4  =  5 hours", "net 3 parts, tank 60:  15 hours",
          "The observed time belongs to the net rate.  Convert parts to a tank first.")]
PRACTICE_A = [("L1", "A pipe fills a tank in 4 hours.  Because of a leak, it takes 5 hours.  Leak alone: time to empty the full tank?"),
              ("L1", "A leak can empty a tank in 15 h.  A pipe that fills it in 10 h is opened on the empty tank.  Time to fill?"),
              ("L2", "A pipe fills a tank in 9 hours.  Because of a leak, it takes 1 hour longer.  Leak alone: time to empty?"),
              ("L2", "A and B fill a tank in 12 and 15 h.  Because of a leak, together they take 10 h.  Leak alone: time to empty?"),
              ("L2", "A pipe fills 4 times as fast as a leak empties.  With the leak the tank fills in 20 h.  Pipe alone?  Leak alone?")]
PRACTICE_B = [("L3", "A leak empties the full tank in 10 h.  A tap admitting 6 L/min is opened, and it now empties in 12 h.  Capacity?"),
              ("L3", "Inlet fills in 6 h, leak empties in 12 h, a tap draws 10 L/min.  With all three it fills in 20 h.  Capacity?"),
              ("L3", "A pipe fills a tank in 6 h.  At half full a leak develops, and filling takes 1 h longer than usual.  Leak alone?")]
ANSWERS_A = [("20 units:   pipe 5, with the leak 4;   leak 1 an hour", "20 hours"),
             ("30 units:   +3 − 2 = +1 an hour", "30 hours"),
             ("fill time 9 → 10 h;   90 units:   10 − 9 = 1", "90 hours"),
             ("60 units:   A + B = 5 + 4 = 9, with the leak 6;   leak 3", "20 hours")]
ANSWERS_B = [("pipe 4 parts, leak 1, net 3;   tank = 3 × 20 = 60 parts", "pipe 15 h,  leak 60 h"),
             ("tap = C/10 − C/12 = C/60 per hour = 360 L", "21,600 litres"),
             ("C/6 − C/12 − 600 = C/20;   C/30 = 600", "18,000 litres"),
             ("first half 3 h, second half 4 h:  net 1/8;   leak = 1/6 − 1/8", "24 hours")]
LENS = [("Recognition cue", "“leak”, “hole in the bottom”, “due to a leak it takes … longer”, “a tap draws … litres a minute”"),
        ("Target time", "30 seconds for a leak's time;  60 seconds for capacity in litres"),
        ("Sanity check", "the leak alone must take longer than the pipe alone, or the tank would never fill")]


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


class LeaksAndCisternProblemsVideo(LMSScene):
    lesson_title = "Leaks & Cistern Problems"

    def construct(self):
        self.camera.background_color = BG

        self.intro()
        self.hook()
        self.objectives()
        self.why_this_matters()
        self.leak_rate()
        self.units_taps_ratios()
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

        crumb = self.breadcrumb("Quantitative Aptitude", "Lesson 18 · Pipes & Cistern", "Video 4 of 5")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        recap = VGroup(text("last video", SMALL, MUTED), pill("timeline:  sum of rate × open time = the tank", WORD, size=LABEL)).arrange(DOWN, buff=0.25)
        title = fit_width(text("Leaks & Cistern Problems", TITLE, INK, BOLD), SAFE_W - 0.4)
        today = text("today: the outlet nobody opened on purpose", LABEL, FOCUS)
        block = VGroup(recap, title, today).arrange(DOWN, buff=0.7)
        fit_within(block, SAFE_W, SAFE_H - crumb.height - 0.9)
        block.next_to(crumb, DOWN, buff=0.7)
        self.no_overlap(crumb, recap, title, today)
        self.validator.check_in_frame(VGroup(crumb, block))

        n = self.narrate(
            id="intro_01",
            text="In the last video, you drew the timeline and added each pipe's rate times its open time.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.at_word(n, "timeline")
        self.play(FadeIn(recap, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="intro_02",
            text="Today: leaks and cistern problems, the outlet that nobody opened on purpose.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "leaks")
        self.play(FadeIn(title, shift=UP * 0.1))
        self.at_word(n, "purpose")
        self.play(FadeIn(today, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_intro")

    # ============================================== 1. HOOK ==========

    def hook(self):
        self.scene_start("S01_hook", title="Hook")

        head = self.heading("An overhead tank")
        log = VGroup(pill("usual fill time:  6 h", GOOD, size=LABEL), pill("today:  8 h", BAD, size=LABEL),
                     pill("a leak at the bottom", BAD, size=LABEL)).arrange(RIGHT, buff=0.4)
        ask = pill("pipe shut off:   how long will the leak take to drain the full tank?", FOCUS, size=LABEL)
        quick = text("the quick answer:  8 − 6 = 2 hours", LABEL, BAD, BOLD)
        why = text("that leak would be three times faster than the pipe: the tank could never have filled", LABEL, MUTED)
        fit_width(why, SAFE_W - 0.6)
        real = text("the real answer is twelve times longer", LABEL, INK, BOLD)
        self.stack(head, [log, ask, quick, why, real], buff=0.6, top=0.7)
        self.no_overlap(*log)

        n = self.narrate(
            id="hook_01",
            text="A pipe normally fills an overhead tank in six hours.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "six")
        self.play(FadeIn(log[0], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_02",
            text="Today it took eight hours, and the maintenance team finds a leak at the bottom.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "eight")
        self.play(FadeIn(log[1], shift=UP * 0.1))
        self.at_word(n, "leak")
        self.play(FadeIn(log[2], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_03",
            text="If the pipe is shut off, how long will the leak take to drain the full tank?",
            voice="default",
            subtitle=True,
            pause_after=3.0,
        )
        self.at_word(n, "drain")
        self.play(FadeIn(ask, scale=1.03))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="hook_04",
            text="The quick answer, eight minus six, two hours, would mean a leak three times faster than the pipe, and "
                 "then the tank could never have filled at all.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "minus")
        self.play(FadeIn(quick, shift=UP * 0.1))
        self.at_word(n, "never")
        self.play(FadeIn(why, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_05",
            text="The real answer is twelve times longer.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "twelve")
        self.play(FadeIn(real, shift=UP * 0.1))
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
            text="First, find a leak's emptying time from the change in fill time.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "emptying")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "change")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="objectives_03",
            text="Second, find a tank's capacity when a leak or tap is given in litres per minute.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "capacity")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "litres")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="objectives_04",
            text="Third, solve cistern problems with an inlet, a leak and an extra tap, and with rate ratios.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "cistern")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "ratios")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_objectives")

    # ============================================== 3. WHY THIS MATTERS ==========

    def why_this_matters(self):
        self.scene_start("S03_why_this_matters", title="Why This Matters")

        head = self.heading("Why this matters")
        leak = pill("a leak is an outlet nobody opened on purpose", BAD, size=LABEL)
        often = text("one of the most frequent Pipes & Cistern questions", LABEL, INK)
        back = pill("the method:  Video 1's net rate, run backwards", FOCUS, size=LABEL)
        gap = text("you know the net, you know the inlet: the leak is the difference", LABEL, INK, BOLD)
        self.stack(head, [leak, often, back, gap], buff=0.7, top=0.9)

        n = self.narrate(
            id="why_this_matters_01",
            text="A leak is an outlet nobody opened on purpose, and it is one of the most frequent pipes and cistern "
                 "questions.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "purpose")
        self.play(FadeIn(leak, shift=UP * 0.1))
        self.at_word(n, "frequent")
        self.play(FadeIn(often, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="why_this_matters_02",
            text="The method is video one's net rate run backwards: you know the net, you know the inlet, and the leak is "
                 "the difference.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "backwards")
        self.play(FadeIn(back, scale=1.03))
        self.at_word(n, "difference")
        self.play(FadeIn(gap, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_why_this_matters")

    # ============================================== 4. CONCEPT - THE LEAK'S RATE ==========

    def leak_rate(self):
        self.scene_start("S04_leak_rate", title="Concept - The Leak's Rate")

        head = self.heading("The leak's rate")
        blocks = two_line_blocks(STEPS_A, WORD)
        self.stack(head, list(blocks), buff=0.5, top=0.7, align=LEFT)

        n = self.narrate(
            id="leak_rate_01",
            text="A leak is an outlet that is always on. It has a negative rate, and it works whenever there is water in "
                 "the tank.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "always")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "negative")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="leak_rate_02",
            text="The leak's rate is the rate without the leak, minus the rate with the leak. If the fill time rises from "
                 "x to y, the leak's rate is one over x minus one over y, and it empties a full tank in x y over y minus "
                 "x.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "without")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "rises")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="leak_rate_03",
            text="Takes d hours longer means y is x plus d. Add first, then use the formula; d itself is not the leak's "
                 "time.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "longer")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "Add")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="leak_rate_04",
            text="Litres and fractions meet through the capacity, C. Write each pipe's rate as C divided by its time. A "
                 "flow in litres per minute equals the difference of two such rates; solve for C.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "capacity")
        self.play(FadeIn(blocks[3][0], shift=RIGHT * 0.2))
        self.at_word(n, "Write")
        self.play(FadeIn(blocks[3][1], shift=RIGHT * 0.2))
        self.at_word(n, "solve")
        self.play(Indicate(blocks[3][1], color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_leak_rate")

    # ============================================== 5. CONCEPT - UNITS, EXTRA TAPS AND RATE RATIOS ==========

    def units_taps_ratios(self):
        self.scene_start("S05_units_taps_ratios", title="Concept - Units, Extra Taps and Rate Ratios")

        head = self.heading("Units, extra taps and rate ratios")
        blocks = two_line_blocks(STEPS_B, WORD)
        self.stack(head, list(blocks), buff=0.5, top=0.7, align=LEFT)

        n = self.narrate(
            id="units_taps_ratios_01",
            text="Keep one time unit. If times are in hours and a flow is in litres per minute, convert the flow to litres "
                 "per hour, times sixty, before equating.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "Keep")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "convert")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="units_taps_ratios_02",
            text="An inlet, a leak and an extra tap need one equation: inlet minus leak minus tap equals the net rate you "
                 "observe.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "equation")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "minus")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="units_taps_ratios_03",
            text="Rate ratios give parts directly. The pipe fills four times as fast as the leak empties: pipe four parts, "
                 "leak one part, net three parts. The given time belongs to the net.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "directly")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "parts", occurrence=2)
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.at_word(n, "belongs")
        self.play(Indicate(blocks[2][1], color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="units_taps_ratios_04",
            text="A leak that starts later is a stage problem. Fill to the level at which the leak begins, then use the "
                 "reduced net rate, as in video three.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "stage")
        self.play(FadeIn(blocks[3][0], shift=RIGHT * 0.2))
        self.at_word(n, "Fill")
        self.play(FadeIn(blocks[3][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_units_taps_ratios")

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
            text="Here is the formula box. The leak's rate is one over x minus one over y, so the leak alone empties a "
                 "full tank in x y over y minus x.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "box")
        self.play(FadeIn(box[0]))
        self.at_word(n, "rate")
        self.play(FadeIn(lines[0], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_box_02",
            text="D hours longer means y is x plus d.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "longer")
        self.play(FadeIn(lines[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_box_03",
            text="With a capacity C, each rate is C divided by its time, and a litre flow is the difference of two such "
                 "rates.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "capacity")
        self.play(FadeIn(lines[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_box_04",
            text="Inlet minus leak minus tap is the observed net rate.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "minus")
        self.play(FadeIn(lines[3], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_box_05",
            text="And for a ratio of k to one, pipe to leak, the net is k minus one parts.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "ratio")
        self.play(FadeIn(lines[4], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_formula_box")

    # ============================================== 7. THE ANALOGY - A PHONE ON CHARGE ==========

    def analogy(self):
        self.scene_start("S07_analogy", title="The Analogy - A Phone on Charge")

        head = self.heading("A phone on charge, with an app running")
        slow = pill("navigation app running:  the phone takes longer to charge", WORD, size=LABEL)
        tells = text("the slower charge time tells you how hard the app is draining", LABEL, INK, BOLD)
        unplug = pill("unplug the charger:  that same drain, alone, empties the battery", BAD, size=LABEL)
        stops = VGroup(text("Where the analogy stops", LABEL, BAD, BOLD),
                       text("real batteries charge non-linearly near full", LABEL, INK),
                       text("tanks and pipes run at constant rates from empty to full", LABEL, MUTED)).arrange(DOWN, buff=0.2)
        self.stack(head, [slow, tells, unplug, stops], buff=0.65, top=0.8)

        n = self.narrate(
            id="analogy_01",
            text="Charge a phone while a navigation app runs, and it takes longer to fill.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "navigation")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "longer")
        self.play(FadeIn(slow, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_02",
            text="The slower charge time tells you how hard the app is draining.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "tells")
        self.play(FadeIn(tells, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_03",
            text="Unplug the charger and that same drain, alone, empties the battery.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Unplug")
        self.play(FadeIn(unplug, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_04",
            text="Where the analogy stops: real batteries charge non-linearly near full; tanks and pipes are assumed to "
                 "run at constant rates from empty to full.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "stops")
        self.play(FadeIn(stops[0], shift=UP * 0.1))
        self.at_word(n, "non-linearly")
        self.play(FadeIn(stops[1], shift=UP * 0.1))
        self.at_word(n, "constant")
        self.play(FadeIn(stops[2], shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S07_analogy")

    # ============================================== 8. WORKED EXAMPLE - CLOSING THE HOOK ==========

    def hook_solved(self):
        self.scene_start("S08_hook_solved", title="Worked Example - Closing the Hook")

        head = self.heading("Fills in 6 h;  with a leak, 8 h")
        bars = VGroup(VGroup(Rectangle(width=4.0, height=0.3, color=GOOD, fill_color=GOOD, fill_opacity=0.5),
                             text("pipe alone:  4 units an hour", SMALL, GOOD, BOLD)).arrange(RIGHT, buff=0.3),
                      VGroup(Rectangle(width=3.0, height=0.3, color=WORD, fill_color=WORD, fill_opacity=0.5),
                             text("with the leak:  3 units an hour", SMALL, WORD, BOLD)).arrange(RIGHT, buff=0.3))\
            .arrange(DOWN, buff=0.2, aligned_edge=LEFT)
        steps = self.solve_steps([("Tank  =  LCM(6, 8)  =  24 units:    pipe alone", "4 units an hour"),
                                  ("Pipe with the leak:    24 ÷ 8", "=  3 units an hour"),
                                  ("The leak removes  4 − 3  =  1 unit an hour", "drains it in 24 hours"),
                                  ("Formula check:    6 × 8/(8 − 6)", "=  24 hours")])
        self.stack(head, [bars, steps], buff=0.6, top=0.7)
        self.no_overlap(*steps)
        self.no_overlap(*bars)

        n = self.narrate(
            id="hook_solved_01",
            text="The tank is the L C M of six and eight: twenty-four units. The pipe alone adds four units an hour.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "twenty-four")
        self.play(FadeIn(steps[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "four")
        self.play(FadeIn(steps[0][2], shift=LEFT * 0.1), FadeIn(bars[0]))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_solved_02",
            text="The pipe with the leak gains twenty-four divided by eight: three units an hour.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "divided")
        self.play(FadeIn(steps[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "three")
        self.play(FadeIn(steps[1][2], shift=LEFT * 0.1), FadeIn(bars[1]))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_solved_03",
            text="So the leak removes one unit an hour, and alone it drains the full tank in twenty-four hours.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "removes")
        self.play(FadeIn(steps[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "drains")
        self.play(FadeIn(steps[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_solved_04",
            text="Formula check: six times eight, over eight minus six, is twenty-four hours.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "check")
        self.play(FadeIn(steps[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "is")
        self.play(FadeIn(steps[3][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S08_hook_solved")

    # ============================================== 9. A SECOND WORKED EXAMPLE - CAPACITY FROM A TAP IN LITRES ==========

    def second_example(self):
        self.scene_start("S09_second_example", title="A Second Worked Example - Capacity from a Tap in Litres")

        head = self.heading("Capacity from a tap in litres")
        ask = text("a leak empties the full tank in 6 h; a tap admitting 4 L/min is opened; now it empties in 8 h:   capacity?", LABEL, MUTED)
        fit_width(ask, SAFE_W - 0.6)
        steps = self.solve_steps([("Capacity C litres:    leak  C/6 an hour out", "net with the tap:  C/8 an hour out"),
                                  ("Tap  =  C/6 − C/8", "=  C/24 litres an hour"),
                                  ("Tap  =  4 litres a minute  =  240 litres an hour", "C/24  =  240"),
                                  ("C  =  24 × 240", "=  5,760 litres")])
        self.stack(head, [ask, steps], buff=0.7, top=0.7)
        self.no_overlap(*steps)

        n = self.narrate(
            id="second_example_01",
            text="A leak in the bottom of a tank can empty the full tank in six hours. An inlet tap that admits four "
                 "litres a minute is opened, and the full tank now empties in eight hours. Find the capacity.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "leak")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "tap")
        self.play(FadeIn(ask, shift=UP * 0.1))
        self.at_word(n, "Find")
        self.play(Indicate(ask, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_02",
            text="Let the capacity be C litres. The leak takes out C over six litres an hour, and the net with the tap is "
                 "C over eight an hour out.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "capacity")
        self.play(FadeIn(steps[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "net")
        self.play(FadeIn(steps[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_03",
            text="So the tap is C over six minus C over eight: C over twenty-four litres an hour.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "minus")
        self.play(FadeIn(steps[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "twenty-four")
        self.play(FadeIn(steps[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_04",
            text="The tap admits four litres a minute, which is two hundred and forty litres an hour, so C over "
                 "twenty-four is two hundred and forty.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "admits")
        self.play(FadeIn(steps[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "so")
        self.play(FadeIn(steps[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_05",
            text="C is five thousand seven hundred and sixty litres.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "thousand")
        self.play(FadeIn(steps[3], scale=1.03))
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
            text="Fill time increases: it fills in six hours, and with a leak, eight. Twenty-four units, four minus three "
                 "is one: the leak empties it in twenty-four hours.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "increases")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "minus")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_03",
            text="D hours longer: it fills in nine hours and the leak adds one hour. Ninety units, ten minus nine is one: "
                 "the leak empties it in ninety hours.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "longer")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "minus")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_04",
            text="Two inlets and a leak: A twelve hours, B fifteen, and with a leak, ten. Sixty units, nine minus six is "
                 "three: the leak empties it in twenty hours.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "inlets")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "minus")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Exam patterns  ·  4 to 6 of 6")
        blocks = self.pattern_blocks(PATTERNS[3:6])
        self.stack(head, list(blocks), buff=0.6, top=0.8, align=LEFT)

        n = self.narrate(
            id="exam_patterns_05",
            text="Rate ratio: the pipe is four times the leak, and with the leak it fills in twenty hours. Net three parts "
                 "times twenty is sixty parts: the pipe alone takes fifteen hours.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "ratio")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "Net")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_06",
            text="Tap and leak in litres: the leak takes six hours, the tap admits four litres a minute, and now it "
                 "empties in eight hours. The tap is C over twenty-four an hour, two hundred and forty litres: five "
                 "thousand seven hundred and sixty litres.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "litres")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "over")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_07",
            text="Inlet, leak and an extra tap: inlet six hours, leak twelve hours, a tap drawing ten litres a minute, and "
                 "it fills in twenty hours. C over six, minus C over twelve, minus six hundred, is C over twenty: eighteen "
                 "thousand litres.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "extra")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "over")
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
            text="Trap one: subtracting the times. A pipe fills a tank in six hours; with a leak it takes eight: how long "
                 "for the leak alone?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "subtracting")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "pipe")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_02",
            text="The wrong instinct says eight minus six, two hours. The correct working: one sixth minus one eighth is "
                 "one twenty-fourth, so twenty-four hours.",
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
            text="The rule: subtract rates, not times. The leak must be slower than the pipe, or the tank would never "
                 "fill.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "rule")
        self.play(FadeIn(rule, shift=UP * 0.1))
        self.at_word(n, "slower")
        self.play(Indicate(rule, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)
        self.clear_stage()

        head, q, wrong, right, rule = self.show_trap(TRAPS[1])

        n = self.narrate(
            id="traps_04",
            text="Trap two: litres per minute mixed with hours. The tap is C over twenty-four litres an hour, and the tap "
                 "admits four litres a minute: what is the capacity?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "mixed")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "tap")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_05",
            text="The wrong instinct sets C over twenty-four equal to four, so ninety-six litres. The correct working: "
                 "four litres a minute is two hundred and forty litres an hour, so five thousand seven hundred and sixty "
                 "litres.",
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
            text="The rule: put every rate in the same time unit before equating.",
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
            text="Trap three: a rate ratio used as a time ratio. A pipe fills four times as fast as a leak empties, and "
                 "with the leak the tank fills in twenty hours: how long for the pipe alone?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "ratio")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "fills")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_08",
            text="The wrong instinct says twenty divided by four, five hours. The correct working: the net is four minus "
                 "one, three parts, so the tank is sixty parts and the pipe alone takes sixty divided by four, fifteen "
                 "hours.",
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
            text="The rule: the observed time belongs to the net rate. Convert parts to a tank first.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "rule")
        self.play(FadeIn(rule, shift=UP * 0.1))
        self.at_word(n, "Convert")
        self.play(Indicate(rule, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S11_traps")

    # ============================================== 12. CHECKPOINT ==========

    def checkpoint(self):
        self.scene_start("S12_checkpoint", title="Checkpoint")

        head = self.heading("Checkpoint  ·  your turn")
        given = fit_width(pill("fills in 5 h; because of a leak it takes 6 h:   leak alone to empty the full tank?", FOCUS, size=LABEL),
                          SAFE_W - 0.4)
        work = VGroup(text("30 units:    pipe 6 an hour,  with the leak 5 an hour", LABEL, INK, BOLD),
                      text("the leak removes 1 an hour:    30 hours", BODY, GOOD, BOLD)).arrange(DOWN, buff=0.4)
        self.stack(head, [given, work], buff=0.9, top=1.0)
        self.no_overlap(*work)

        n = self.narrate(
            id="checkpoint_01",
            text="Your turn. A pipe fills a tank in five hours. Because of a leak, it takes six hours. How long would the "
                 "leak take to empty the full tank?",
            voice="default",
            subtitle=True,
            pause_after=10.0,
        )
        self.at_word(n, "turn")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "fills")
        self.play(FadeIn(given, scale=1.03))
        self.at_word(n, "leak")
        self.play(Indicate(given, color=FOCUS, scale_factor=1.03))
        self.at_word(n, "long")
        self.play(Indicate(given, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="checkpoint_02",
            text="Thirty units: the pipe adds six an hour, and with the leak five an hour. The leak removes one an hour: "
                 "thirty hours.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Thirty")
        self.play(FadeIn(work[0], shift=UP * 0.1))
        self.at_word(n, "removes")
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
            text="Level one, question one: a pipe fills a tank in four hours; because of a leak, it takes five hours; how "
                 "long would the leak take to empty the full tank? Question two: a tank has a leak that can empty it in "
                 "fifteen hours; a pipe that fills the tank in ten hours is opened on the empty tank; how long does it "
                 "take to fill?",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "leak")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "fifteen")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="practice_02",
            text="Level two, question three: a pipe fills a tank in nine hours; because of a leak, it takes one hour "
                 "longer; how long would the leak take to empty the full tank? Question four: pipes A and B fill a tank in "
                 "twelve and fifteen hours; because of a leak, together they take ten hours; how long would the leak alone "
                 "take to empty the full tank? Question five: a pipe fills a tank four times as fast as a leak empties it; "
                 "with the leak, the tank fills in twenty hours; how long would the pipe take alone, and the leak alone?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "longer")
        self.play(FadeIn(rows[2], shift=RIGHT * 0.2))
        self.at_word(n, "together")
        self.play(FadeIn(rows[3], shift=RIGHT * 0.2))
        self.at_word(n, "times")
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
            text="Level three, question six: a leak in the bottom of a tank can empty the full tank in ten hours; an inlet "
                 "tap that admits six litres a minute is opened, and the full tank now empties in twelve hours; find the "
                 "capacity of the tank. Question seven: a cistern has an inlet that fills it in six hours and a leak that "
                 "empties it in twelve hours; a tap that draws ten litres a minute is also open; with all three, the empty "
                 "cistern fills in twenty hours; find its capacity. Question eight: a pipe normally fills a tank in six "
                 "hours; when the tank was half full, a leak developed, and the tank took one hour longer than usual to "
                 "fill; how long would the leak alone take to empty the full tank?",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "admits")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "draws")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.at_word(n, "developed")
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
            text="One: twenty units, the pipe adds five and with the leak four, so the leak removes one an hour: twenty "
                 "hours.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "units")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "hours")
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_02",
            text="Two: thirty units, plus three minus two is plus one an hour: thirty hours.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "minus")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "hours")
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_03",
            text="Three: the fill time rises from nine to ten hours; ninety units, ten minus nine is one, so the leak "
                 "takes ninety hours.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "rises")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "takes")
        self.play(FadeIn(rows[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_04",
            text="Four: sixty units, A plus B is five plus four, nine, and with the leak six; the leak removes three an "
                 "hour: twenty hours.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "units")
        self.play(FadeIn(rows[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "twenty")
        self.play(FadeIn(rows[3][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Answer key  ·  5 to 8", GOOD)
        table, rows = self.answer_table(head, ANSWERS_B, 5)

        n = self.narrate(
            id="answers_05",
            text="Five: pipe four parts, leak one part, net three parts; the tank is three times twenty, sixty parts, so "
                 "the pipe alone takes fifteen hours and the leak alone sixty hours.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "parts")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "alone")
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_06",
            text="Six: the tap is C over ten minus C over twelve, C over sixty per hour, which is six times sixty, three "
                 "hundred and sixty litres an hour; so C is twenty-one thousand six hundred litres.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "minus")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "thousand")
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_07",
            text="Seven: ten litres a minute is six hundred litres an hour. C over six minus C over twelve minus six "
                 "hundred is C over twenty, so C over thirty is six hundred, and C is eighteen thousand litres.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "litres")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "thousand")
        self.play(FadeIn(rows[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_08",
            text="Eight: the first half takes three hours and the total is seven, so the second half took four hours, a "
                 "net rate of one eighth. The leak is one sixth minus one eighth, one twenty-fourth: twenty-four hours.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "half")
        self.play(FadeIn(rows[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "hours", occurrence=3)
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
            text="Recognise and move. The recognition cue: leak, hole in the bottom, due to a leak it takes longer, or a "
                 "tap draws so many litres a minute.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "cue")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "hole")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_lens_02",
            text="The target time: thirty seconds for a leak's time, and sixty seconds for capacity in litres.",
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
            text="The sanity check: the leak alone must take longer than the pipe alone, or the tank would never fill.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "sanity")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "longer")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S15_exam_lens")

    # ============================================== 16. QUICK REVISION AND SUMMARY ==========

    def summary(self):
        self.scene_start("S16_summary", title="Quick Revision and Summary")

        head = self.heading("Quick revision")
        always = pill("a leak is an always-on outlet", BAD, size=BODY)
        gap = pill("its rate = the gap:    fill time rises from x to y   →   leak  xy/(y − x)", WORD, size=LABEL)
        litres = pill("litres:    every rate = capacity ÷ time;    one time unit;    one equation", RATIO, size=LABEL)
        phone = text("the phone on charge: the slower charge shows the drain", LABEL, MUTED)
        box = fit_width(pill("“d hours longer”:  y = x + d            ratio k : 1  →  net k − 1 parts", GOOD, size=SMALL), SAFE_W - 0.4)
        nxt = self.breadcrumb("Next", "Video 5 · Speed Tricks for Pipes & Cistern")
        self.stack(head, [always, gap, litres, phone, box, nxt], buff=0.45, top=0.6)

        n = self.narrate(
            id="summary_01",
            text="A leak is an always-on outlet.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "leak")
        self.play(FadeIn(always, scale=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_02",
            text="Its rate is the gap between the rate without it and the rate with it, so a fill time that rises from x "
                 "to y means a leak of x y over y minus x.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "gap")
        self.play(FadeIn(gap, scale=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_03",
            text="With litres, write every rate as capacity divided by time, convert to one time unit, and solve one "
                 "equation.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "litres")
        self.play(FadeIn(litres, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_04",
            text="Remember the phone on charge, and the formula box.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "phone")
        self.play(FadeIn(phone, shift=UP * 0.1))
        self.at_word(n, "box")
        self.play(FadeIn(box, scale=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_05",
            text="Next: speed tricks for pipes and cistern.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Next")
        self.play(FadeIn(nxt, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S16_summary")

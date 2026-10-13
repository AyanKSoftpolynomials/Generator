"""
animation.py for the LMS video generator.

Course : Pre-C-CAT - Section A - Quantitative Aptitude
Video  : Lesson 18 - Pipes & Cistern - 03 - Pipes Opened & Closed at Different Times

Source script:
  C:\\Scripts\\Section A\\Aptitude\\Sessions 13-18 - Pipes, Time Distance, Partnership\\Lesson 18 - Pipes & Cistern\\03 - Pipes Opened & Closed at Different Times.pdf

Built on the golden-reference pattern:
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``;
  * layouts stacked with next_to and guarded with ``no_overlap``; nothing is
    ever animated onto or into another box.

Lesson 18, Video 3 of 5. Not the first video of the lesson: a silent breadcrumb, a one-line recap of Video 2, then today's topic. No spoken course welcome.
The narration follows the script section by section. The seven concept steps are split over two screens. The six exam patterns are shown as two-line blocks. Every alternate-turn answer is checked by a minute-by-minute simulation in the data block.
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


def alternate(tank, turns):
    """Pipes take one-minute turns in order (units per minute, negative for an outlet).  Time until the tank is full."""
    level, minutes = Fraction(0), Fraction(0)
    while True:
        for rate in turns:
            if rate > 0 and level + rate >= tank:
                return minutes + (tank - level) / rate
            level = max(Fraction(0), level + rate)
            minutes += 1


# ---- the hook: A 16 min, B 24 min, full in 13 min ----
TANK = lcm(16, 24)
A_PART = (TANK // 16) * 13
B_TIME = Fraction(TANK - A_PART, TANK // 24)
assert (TANK, TANK // 16, TANK // 24, A_PART, TANK - A_PART, B_TIME) == (48, 3, 2, 39, 9, Fraction(9, 2))

# ---- second worked example: A fills in 3 min, B empties in 6, alternately ----
assert alternate(6, [2, -1]) == 9 != 6 * 2

# ---- exam patterns, traps, checkpoint, practice (answers computed) ----
assert 4 * (5 + 4) == 36 and 4 + Fraction(60 - 36, 5) == Fraction(44, 5)                  # closed after 4 min: 8.8
assert 5 * 3 == 15 and 5 + Fraction(60 - 15, 3 + 2) == 14                                 # opened later
assert 2 * 9 + 3 * (9 - 5) == 30 and 1 / (Fraction(1, 15) + Fraction(1, 10)) == 6         # closed 5 min before full: T = 9
assert alternate(12, [3, 2]) == 4 + Fraction(2, 3) and alternate(12, [3, -2]) == 19
assert Fraction(15, 3) + Fraction(15, 3 - 2) == 20                                        # outlet opened at half: 5 + 15
assert 3 * (3 + 2) == 15 and 3 + Fraction(30 - 15, 3) == 8                                # checkpoint
assert Fraction(12, 3) + Fraction(12, 3 - 1) == 10                                        # practice 4
assert lcm(24, 32) == 96 and 4 * 18 == 72 and Fraction(96 - 72, 3) == 8                   # practice 7
assert 6 * (3 + 2) == 30 and 6 + Fraction(60 - 30, 3 + 2 - 4) == 36                       # practice 8

OBJECTIVES = [("Split a filling into stages", "add each pipe's contribution over the time it was open"),
              ("Solve “closed after”, “opened later”, “closed before full”", "and “outlet opened when half full”"),
              ("Handle pipes opened alternately", "including an outlet that takes turns")]
STEPS_A = [("Draw the timeline:  mark every moment a pipe is opened or closed", "between marks the open set is constant:  one stage"),
           ("Stage change = net units per minute × minutes in the stage", "outlets subtract, exactly as in Video 1"),
           ("Or count by pipe:  contribution = its rate × the time it was open", "the contributions add to one full tank:  fastest when one open time is unknown"),
           ("A level as a switch point:  “when half full, an outlet is opened”", "find the time to reach half, then run the second stage at the new net rate")]
STEPS_B = [("“Closed x minutes before the tank is full” hides the total", "let the total be T:  that pipe was open for T − x minutes;  one equation in T"),
           ("Alternate minutes:  a cycle, then the leftover", "count full cycles, then go minute by minute;  the last turn may need only part of a minute"),
           ("With an outlet in the cycle, check after every inlet turn", "the level peaks after an inlet's minute:  never divide the tank by the cycle's net gain")]
FORMULAS = ["Sum of (each pipe's rate × its open time)   =   1 tank     (or the total units)",
            "Stage change   =   net rate × stage time",
            "Closed x min before full:      a × T + b × (T − x)  =  total         (b = the pipe closed early)",
            "Alternate turns:      full cycles, then turn by turn;      last turn  =  leftover ÷ that pipe's rate",
            "Outlet in the cycle:      stop as soon as an inlet turn reaches full"]
PATTERNS = [("Closed after x min", "A 12, B 15 min;   B closed after 4 min", "60 units:   4 × 9 = 36;   24 ÷ 5", "8.8 min in all"),
            ("Opened later", "A (20 min) alone for 5 min, then B (30 min) too", "60 units:   15 done;   45 ÷ 5", "14 min in all"),
            ("Closed x min before full", "A 15, B 10 min;   B closed 5 min before full", "30 units:   2T + 3(T − 5) = 30", "9 min"),
            ("Alternate, two inlets", "A 4, B 6 min;   one minute each, A first", "12 units:   10 after 4 min;   A needs 2 at 3", "4 2/3 min"),
            ("Alternate, inlet and outlet", "A fills 3 min, B empties 6 min;   A first", "6 units:   +2, −1;   4 after 8 min", "9 min"),
            ("Outlet opened at half", "A fills 10 h;   outlet (15 h) opened at half full", "30 units:   15 in 5 h;   15 at net 1", "20 h in all")]
TRAPS = [("Trap 1  ·  dividing by the cycle's net gain",
          "A fills in 3 min, B empties in 6; alternately one minute each, A first.  Time to fill?",
          "+1 per cycle, 6 cycles:  12 min", "9 minutes",
          "With an outlet in the cycle, check the level after every inlet turn."),
         ("Trap 2  ·  “closed before full” treated as “closed after”",
          "A fills in 15 min, B in 10.  Both open; B is closed 5 min before the tank is full.  Total time?",
          "together 6 min, plus 5:  11 min", "2T + 3(T − 5) = 30:  T = 9",
          "The last x minutes are inside the total.  Write the equation in T."),
         ("Trap 3  ·  only the second stage reported",
          "A fills in 10 h; at half full an outlet (15 h) is opened.  How long does the whole filling take?",
          "15 hours  (second stage only)", "5 + 15  =  20 hours",
          "Underline whether the question asks for the total time or the time after the switch.")]
PRACTICE_A = [("L1", "A and B fill a tank in 12 and 15 min.  Both are opened, and B is closed after 4 min.  Time to fill the tank?"),
              ("L1", "A fills a tank in 20 min.  After A has run alone for 5 min, B (30 min) is also opened.  Find the total time."),
              ("L2", "A and B fill in 15 and 10 min.  Both opened; B is closed 5 min before the tank is full.  Find the total time."),
              ("L2", "A fills a tank in 8 h.  When it is half full, an outlet (24 h) is also opened.  Find the total time to fill."),
              ("L2", "A and B fill in 4 and 6 min, opened alternately for one minute each, A first.  Find the time to fill.")]
PRACTICE_B = [("L3", "A fills in 4 min, B empties in 6 min; alternately one minute each, A first, tank empty.  When is it full?"),
              ("L3", "A and B fill in 24 and 32 min, opened together.  After how many minutes should B be closed to fill in 18 min?"),
              ("L3", "A and B fill in 20 and 30 min, C empties in 15 min.  A and B open; C is opened 6 min later.  Total time to fill?")]
ANSWERS_A = [("60 units:   A 5, B 4;   first 4 min: 36;   24 ÷ 5 = 4.8", "8.8 minutes"),
             ("60 units:   A 3, B 2;   A alone 5 min: 15;   45 ÷ 5 = 9", "14 minutes"),
             ("30 units:   A 2, B 3;   2T + 3(T − 5) = 30;   5T = 45", "9 minutes"),
             ("24 units:   half takes 4 h;   then net 3 − 1 = 2:  6 h", "10 hours")]
ANSWERS_B = [("12 units:   2 cycles (4 min) = 10;   A needs 2 at 3 a minute", "4 2/3 minutes"),
             ("12 units:   +3, −2;   9 after 18 min;   minute 19 (A) fills it", "19 min,  not 24"),
             ("96 units:   A over 18 min: 72;   B supplies 24 at 3 a minute", "close B after 8 min"),
             ("60 units:   first 6 min: 30;   then net 3 + 2 − 4 = 1", "36 minutes")]
LENS = [("Recognition cue", "“after x minutes”, “is closed”, “opened later”, “before the tank is full”, “when half full”, “alternately”"),
        ("Target time", "50 seconds;  60 seconds for “before full” and alternate turns"),
        ("Sanity check", "inlets only: between the all-together time and the lone pipe's time;  with an outlet: ends on an inlet's turn")]


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


class PipesOpenedAndClosedAtDifferentTimesVideo(LMSScene):
    lesson_title = "Pipes Opened & Closed at Different Times"

    def construct(self):
        self.camera.background_color = BG

        self.intro()
        self.hook()
        self.objectives()
        self.why_this_matters()
        self.timeline_and_stages()
        self.before_full_and_turns()
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

        crumb = self.breadcrumb("Quantitative Aptitude", "Lesson 18 · Pipes & Cistern", "Video 3 of 5")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        recap = VGroup(text("last video", SMALL, MUTED), pill("LCM units with signs:  missing pipe = all − known", WORD, size=LABEL)).arrange(DOWN, buff=0.25)
        title = fit_width(text("Pipes Opened & Closed at Different Times", TITLE, INK, BOLD), SAFE_W - 0.4)
        today = text("today: one line of bookkeeping", LABEL, FOCUS)
        block = VGroup(recap, title, today).arrange(DOWN, buff=0.7)
        fit_within(block, SAFE_W, SAFE_H - crumb.height - 0.9)
        block.next_to(crumb, DOWN, buff=0.7)
        self.no_overlap(crumb, recap, title, today)
        self.validator.check_in_frame(VGroup(crumb, block))

        n = self.narrate(
            id="intro_01",
            text="In the last video, you used L C M units with signs, and found a missing pipe as all together minus the "
                 "known ones.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.at_word(n, "signs")
        self.play(FadeIn(recap, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="intro_02",
            text="Today: pipes opened and closed at different times, solved with one line of bookkeeping.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "opened")
        self.play(FadeIn(title, shift=UP * 0.1))
        self.at_word(n, "bookkeeping")
        self.play(FadeIn(today, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_intro")

    # ============================================== 1. HOOK ==========

    def hook(self):
        self.scene_start("S01_hook", title="Hook")

        head = self.heading("A plant-room log")
        pipes = VGroup(pill("pipe A:  fills alone in 16 min", GOOD, size=LABEL), pill("pipe B:  fills alone in 24 min", GOOD, size=LABEL))\
            .arrange(RIGHT, buff=0.5)
        log = VGroup(pill("09:00  both opened", WORD, size=LABEL), pill("B closed at  ??", BAD, size=LABEL),
                     pill("09:13  tank full", WORD, size=LABEL)).arrange(RIGHT, buff=0.4)
        ask = pill("when was B closed?", FOCUS, size=BODY)
        note = text("the time she wrote down is missing, and the tank cannot tell you", LABEL, MUTED)
        one = text("one line of bookkeeping can", LABEL, INK, BOLD)
        self.stack(head, [pipes, log, ask, note, one], buff=0.6, top=0.7)
        self.no_overlap(*pipes)
        self.no_overlap(*log)

        n = self.narrate(
            id="hook_01",
            text="A night operator opens two pipes into an empty coolant tank: A fills it alone in sixteen minutes and B "
                 "in twenty-four.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "sixteen")
        self.play(FadeIn(pipes[0], shift=UP * 0.1), FadeIn(log[0], shift=UP * 0.1))
        self.at_word(n, "twenty-four")
        self.play(FadeIn(pipes[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_02",
            text="At some point she closes B, and A finishes alone.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "closes")
        self.play(FadeIn(log[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_03",
            text="The log shows the tank was full exactly thirteen minutes after the start.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "thirteen")
        self.play(FadeIn(log[2], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_04",
            text="When was B closed?",
            voice="default",
            subtitle=True,
            pause_after=3.0,
        )
        self.at_word(n, "closed")
        self.play(FadeIn(ask, scale=1.03))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="hook_05",
            text="The time she wrote down is missing, and the tank cannot tell you. One line of bookkeeping can.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "missing")
        self.play(FadeIn(note, shift=UP * 0.1))
        self.at_word(n, "bookkeeping")
        self.play(FadeIn(one, shift=UP * 0.1))
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
            text="First, split a filling into stages, and add each pipe's contribution over the time it was open.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "split")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "contribution")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="objectives_03",
            text="Second, solve closed after x minutes, opened later, closed x minutes before full, and outlet opened when "
                 "half full.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "solve")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "outlet")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="objectives_04",
            text="Third, handle pipes opened alternately, including the case where an outlet takes turns.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "alternately")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "turns")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_objectives")

    # ============================================== 3. WHY THIS MATTERS ==========

    def why_this_matters(self):
        self.scene_start("S03_why_this_matters", title="Why This Matters")

        head = self.heading("Why this matters")
        same = pill("Lesson 13, Video 4 (leaving and joining) and Video 5 (alternate days), with pipes", WORD, size=LABEL)
        twist = text("the new twist is the outlet", BODY, BAD, BOLD)
        full = pill("in an alternating cycle the tank can be full before the cycle ends", FOCUS, size=LABEL)
        wrong = text("that is where the standard answer goes wrong", LABEL, MUTED)
        self.stack(head, [same, twist, full, wrong], buff=0.7, top=0.9)

        n = self.narrate(
            id="why_this_matters_01",
            text="This is lesson thirteen, video four, leaving and joining, and video five, alternate days, with pipes.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "pipes")
        self.play(FadeIn(same, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="why_this_matters_02",
            text="The new twist is the outlet: in an alternating cycle the tank can be full before the cycle ends, and "
                 "that is where the standard answer goes wrong.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "twist")
        self.play(FadeIn(twist, shift=UP * 0.1))
        self.at_word(n, "before")
        self.play(FadeIn(full, scale=1.03))
        self.at_word(n, "wrong")
        self.play(FadeIn(wrong, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_why_this_matters")

    # ============================================== 4. CONCEPT - THE TIMELINE AND ITS STAGES ==========

    def timeline_and_stages(self):
        self.scene_start("S04_timeline_and_stages", title="Concept - The Timeline and Its Stages")

        head = self.heading("The timeline and its stages")
        blocks = two_line_blocks(STEPS_A, WORD)
        self.stack(head, list(blocks), buff=0.5, top=0.7, align=LEFT)

        n = self.narrate(
            id="timeline_and_stages_01",
            text="Draw the timeline. Mark every moment a pipe is opened or closed. Between marks, the open set is "
                 "constant: one stage.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "timeline")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "Mark")
        self.play(Indicate(blocks[0][0], color=FOCUS, scale_factor=1.03))
        self.at_word(n, "stage")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="timeline_and_stages_02",
            text="The stage change is the net units per minute, times the minutes in the stage. Outlets subtract, exactly "
                 "as in video one.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "times")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "subtract")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="timeline_and_stages_03",
            text="Or count by pipe: each pipe's contribution is its rate times the time it was open. The contributions add "
                 "to one full tank. This is the fastest way when one open time is unknown.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "count")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "add")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.at_word(n, "fastest")
        self.play(Indicate(blocks[2][1], color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="timeline_and_stages_04",
            text="A level can be a switch point. When the tank is half full, an outlet is opened: first find how long the "
                 "inlets take to reach half, then run the second stage at the new net rate.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "switch")
        self.play(FadeIn(blocks[3][0], shift=RIGHT * 0.2))
        self.at_word(n, "first")
        self.play(FadeIn(blocks[3][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_timeline_and_stages")

    # ============================================== 5. CONCEPT - CLOSED BEFORE FULL, AND ALTERNATE TURNS ==========

    def before_full_and_turns(self):
        self.scene_start("S05_before_full_and_turns", title="Concept - Closed Before Full, and Alternate Turns")

        head = self.heading("“Before full”, and alternate turns")
        blocks = two_line_blocks(STEPS_B, WORD)
        self.stack(head, list(blocks), buff=0.75, top=1.0, align=LEFT)

        n = self.narrate(
            id="before_full_and_turns_01",
            text="Closed x minutes before the tank is full hides the total. Let the total time be T. That pipe was open "
                 "for T minus x minutes. Write one equation in T.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "hides")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "Let")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.at_word(n, "minus")
        self.play(Indicate(blocks[0][1], color=FOCUS, scale_factor=1.03))
        self.at_word(n, "equation")
        self.play(Indicate(blocks[0], color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="before_full_and_turns_02",
            text="Alternate minutes: a cycle, then the leftover. Count full cycles, then go minute by minute in the given "
                 "order. The last turn may need only part of a minute.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "leftover")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "Count")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.at_word(n, "last")
        self.play(Indicate(blocks[1][1], color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="before_full_and_turns_03",
            text="With an outlet in the cycle, check after every inlet turn. The level peaks at the end of an inlet's "
                 "minute, so the tank can be full before the outlet's turn arrives. Never divide the tank by the cycle's "
                 "net gain.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "check")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "peaks")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.at_word(n, "Never")
        self.play(Indicate(blocks[2][1], color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_before_full_and_turns")

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
            text="Here is the formula box. The sum of each pipe's rate times its open time is one tank, or the total "
                 "units.",
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
            text="The stage change is the net rate times the stage time.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "stage")
        self.play(FadeIn(lines[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_box_03",
            text="Closed x minutes before full: a times T, plus b times T minus x, equals the total, where b is the rate "
                 "of the pipe closed early.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "before")
        self.play(FadeIn(lines[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_box_04",
            text="Alternate turns: full cycles, then turn by turn; the last turn is the leftover divided by that pipe's "
                 "rate.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Alternate")
        self.play(FadeIn(lines[3], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_box_05",
            text="And with an outlet in the cycle, stop as soon as an inlet turn reaches full.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "outlet")
        self.play(FadeIn(lines[4], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_formula_box")

    # ============================================== 7. THE ANALOGY - AN EDITING TIMELINE ==========

    def analogy(self):
        self.scene_start("S07_analogy", title="The Analogy - An Editing Timeline")

        head = self.heading("An editing timeline")
        bars = VGroup(*[Rectangle(width=w, height=0.28, color=WORD, fill_color=WORD, fill_opacity=o)
                        for w, o in ((5.0, 0.55), (2.2, 0.35), (3.4, 0.2))]).arrange(DOWN, buff=0.12, aligned_edge=LEFT)
        tracks = pill("each track contributes only while its clip is on", WORD, size=LABEL)
        mix = pill("the mix at any moment  =  the sum of the tracks playing", FOCUS, size=LABEL)
        whole = text("total  =  each track's length × its level,  not the length of the whole video", LABEL, INK, BOLD)
        stops = VGroup(text("Where the analogy stops", LABEL, BAD, BOLD),
                       text("a timeline can run on past its peak", LABEL, INK),
                       text("a tank stops the instant it is full, even mid-cycle", LABEL, MUTED)).arrange(DOWN, buff=0.2)
        self.stack(head, [bars, tracks, mix, whole, stops], buff=0.45, top=0.6)

        n = self.narrate(
            id="analogy_01",
            text="Think of an editing timeline with several tracks.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "timeline")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "tracks")
        self.play(FadeIn(bars))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_02",
            text="Each track contributes only while its clip is on, and the mix at any moment is the sum of the tracks "
                 "playing.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "contributes")
        self.play(FadeIn(tracks, shift=UP * 0.1))
        self.at_word(n, "mix")
        self.play(FadeIn(mix, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_03",
            text="To know the total, you add each track's length times its level, not the length of the whole video.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "total")
        self.play(FadeIn(whole, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_04",
            text="Where the analogy stops: a timeline can run on past its peak; a tank stops the instant it is full, even "
                 "mid-cycle.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "stops")
        self.play(FadeIn(stops[0], shift=UP * 0.1))
        self.at_word(n, "past")
        self.play(FadeIn(stops[1], shift=UP * 0.1))
        self.at_word(n, "instant")
        self.play(FadeIn(stops[2], shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S07_analogy")

    # ============================================== 8. WORKED EXAMPLE - CLOSING THE HOOK ==========

    def hook_solved(self):
        self.scene_start("S08_hook_solved", title="Worked Example - Closing the Hook")

        head = self.heading("A 16 min,   B 24 min,   full in 13 min")
        steps = self.solve_steps([("Tank  =  LCM(16, 24)  =  48 units", "A = 3 a minute,  B = 2 a minute"),
                                  ("A was open all 13 minutes:    3 × 13", "=  39 units"),
                                  ("B supplied the rest:    48 − 39 = 9 units, at 2 a minute", "=  4.5 minutes"),
                                  ("B was closed 4 1/2 minutes after the start", "09:04:30")])
        self.stack(head, [steps], top=1.0)
        self.no_overlap(*steps)

        n = self.narrate(
            id="hook_solved_01",
            text="The tank is the L C M of sixteen and twenty-four: forty-eight units. A adds three a minute and B adds "
                 "two.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "forty-eight")
        self.play(FadeIn(steps[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "adds")
        self.play(FadeIn(steps[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_solved_02",
            text="A was open for all thirteen minutes: three times thirteen is thirty-nine units.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "open")
        self.play(FadeIn(steps[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "thirty-nine")
        self.play(FadeIn(steps[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_solved_03",
            text="B supplied the rest: forty-eight minus thirty-nine is nine units, at two a minute: four and a half "
                 "minutes.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "rest")
        self.play(FadeIn(steps[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "half")
        self.play(FadeIn(steps[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_solved_04",
            text="So B was closed four and a half minutes after the start, at four minutes thirty seconds past nine.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "closed")
        self.play(FadeIn(steps[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "past")
        self.play(FadeIn(steps[3][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S08_hook_solved")

    # ============================================== 9. A SECOND WORKED EXAMPLE - AN OUTLET TAKES TURNS ==========

    def second_example(self):
        self.scene_start("S09_second_example", title="A Second Worked Example - An Outlet Takes Turns")

        head = self.heading("An outlet takes turns")
        ask = text("A fills in 3 min, B empties in 6 min; alternately one minute each, A first:   when is the tank full?", LABEL, MUTED)
        fit_width(ask, SAFE_W - 0.6)
        steps = self.solve_steps([("Tank = 6 units:    A +2 in its minute,  B −1 in its minute", "each 2-minute cycle:  +1"),
                                  ("The level peaks after each A minute:    k units before, then", "k + 2"),
                                  ("Full when k + 2 = 6,  so k = 4:    after 4 cycles (8 min)", "4 units"),
                                  ("Minute 9 (A):    4 + 2 = 6 units", "full in 9 min,  not 12")])
        self.stack(head, [ask, steps], buff=0.7, top=0.7)
        self.no_overlap(*steps)

        n = self.narrate(
            id="second_example_01",
            text="Pipe A fills a tank in three minutes and pipe B empties a full tank in six minutes. Starting with an "
                 "empty tank, they are opened alternately for one minute each, A first. When is the tank full?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Pipe")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "alternately")
        self.play(FadeIn(ask, shift=UP * 0.1))
        self.at_word(n, "When")
        self.play(Indicate(ask, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_02",
            text="Take the tank as six units: A adds two in its minute, B removes one in its minute, so each two-minute "
                 "cycle gains one.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "six")
        self.play(FadeIn(steps[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "cycle")
        self.play(FadeIn(steps[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_03",
            text="The level peaks after each A minute: before A's minute in the next cycle the tank holds k units, and A "
                 "lifts it to k plus two.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "peaks")
        self.play(FadeIn(steps[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "lifts")
        self.play(FadeIn(steps[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_04",
            text="It is full when k plus two is six, so k is four: after four cycles, eight minutes, the tank holds four "
                 "units.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "full")
        self.play(FadeIn(steps[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "holds")
        self.play(FadeIn(steps[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_05",
            text="In minute nine, A's turn, four plus two is six units. The tank is full in nine minutes, not six times "
                 "two, twelve.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "nine")
        self.play(FadeIn(steps[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "not")
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
            text="Closed after some minutes: A twelve, B fifteen minutes, and B is closed after four minutes. Sixty units: "
                 "four times nine is thirty-six, then twenty-four divided by five: eight point eight minutes in all.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Closed")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "divided")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_03",
            text="Opened later: A, twenty minutes, runs alone for five minutes, then B, thirty minutes, joins. Sixty "
                 "units: fifteen done, then forty-five divided by five: fourteen minutes in all.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "later")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "divided")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_04",
            text="Closed some minutes before full: A fifteen, B ten minutes, and B is closed five minutes before full. "
                 "Thirty units: two T plus three times T minus five is thirty, so nine minutes.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "before")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "plus")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Exam patterns  ·  4 to 6 of 6")
        blocks = self.pattern_blocks(PATTERNS[3:6])
        self.stack(head, list(blocks), buff=0.6, top=0.8, align=LEFT)

        n = self.narrate(
            id="exam_patterns_05",
            text="Alternate, two inlets: A four, B six minutes, one minute each, A first. Twelve units: ten after four "
                 "minutes, then A needs two at three a minute: four and two thirds minutes.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "Alternate")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "needs")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_06",
            text="Alternate, inlet and outlet: A fills in three minutes, B empties in six, A first. Six units, plus two "
                 "then minus one: four units after eight minutes, so nine minutes.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "outlet")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "plus")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_07",
            text="Outlet opened at half: A fills in ten hours, and an outlet of fifteen hours is opened at half full. "
                 "Thirty units: fifteen in five hours, then fifteen at net one: twenty hours in all.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "half")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "net")
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
            text="Trap one: dividing by the cycle's net gain. A fills in three minutes, B empties in six, alternately one "
                 "minute each, A first: what is the time to fill?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "dividing")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "alternately")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_02",
            text="The wrong instinct says a net gain of one per two-minute cycle, six cycles: twelve minutes. The correct "
                 "answer is nine minutes.",
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
            text="The rule: with an outlet in the cycle, the tank can be full at the end of an inlet's turn. Check the "
                 "level after every inlet turn.",
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
            text="Trap two: closed before full, treated as closed after. A fills in fifteen minutes, B in ten; both are "
                 "open, and B is closed five minutes before the tank is full: what is the total time?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "treated")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "both")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_05",
            text="The wrong instinct says together they take six minutes, plus five: eleven minutes. The correct equation, "
                 "two T plus three times T minus five equals thirty, gives nine minutes.",
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
            text="The rule: the last x minutes are inside the total. Write the equation in T.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "rule")
        self.play(FadeIn(rule, shift=UP * 0.1))
        self.at_word(n, "Write")
        self.play(Indicate(rule, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)
        self.clear_stage()

        head, q, wrong, right, rule = self.show_trap(TRAPS[2])

        n = self.narrate(
            id="traps_07",
            text="Trap three: only the second stage reported. A fills in ten hours; at half full an outlet of fifteen "
                 "hours is opened: how long does the whole filling take?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "reported")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "outlet")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_08",
            text="The wrong instinct says fifteen hours, the second stage alone. The correct answer is five plus fifteen: "
                 "twenty hours.",
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
            text="The rule: underline whether the question asks for the total time, or the time after the switch.",
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
        given = fit_width(pill("A fills in 10 min, B in 15; both opened, B closed after 3 minutes:   total time?", FOCUS, size=LABEL), SAFE_W - 0.4)
        work = VGroup(text("30 units:    first 3 minutes  =  3 × 5  =  15 units", LABEL, INK, BOLD),
                      text("15 left at 3 a minute:    5 minutes", LABEL, INK, BOLD),
                      text("total  =  8 minutes", BODY, GOOD, BOLD)).arrange(DOWN, buff=0.4)
        self.stack(head, [given, work], buff=0.9, top=0.9)
        self.no_overlap(*work)

        n = self.narrate(
            id="checkpoint_01",
            text="Your turn. A fills a tank in ten minutes and B in fifteen. Both are opened, and B is closed after three "
                 "minutes. What is the total time?",
            voice="default",
            subtitle=True,
            pause_after=10.0,
        )
        self.at_word(n, "turn")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "fills")
        self.play(FadeIn(given, scale=1.03))
        self.at_word(n, "closed")
        self.play(Indicate(given, color=FOCUS, scale_factor=1.03))
        self.at_word(n, "total")
        self.play(Indicate(given, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="checkpoint_02",
            text="Thirty units. In the first three minutes, three times five is fifteen units. Fifteen are left at three a "
                 "minute: five minutes. The total is eight minutes.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Thirty")
        self.play(FadeIn(work[0], shift=UP * 0.1))
        self.at_word(n, "times")
        self.play(Indicate(work[0], color=FOCUS, scale_factor=1.03))
        self.at_word(n, "left")
        self.play(FadeIn(work[1], shift=UP * 0.1))
        self.at_word(n, "total")
        self.play(FadeIn(work[2], scale=1.03))
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
            text="Level one, question one: pipes A and B fill a tank in twelve and fifteen minutes; both are opened, and B "
                 "is closed after four minutes; how long does it take to fill the tank? Question two: pipe A fills a tank "
                 "in twenty minutes; after A has run alone for five minutes, pipe B, which fills the tank in thirty "
                 "minutes, is also opened; find the total time.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "closed")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "alone")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="practice_02",
            text="Level two, question three: pipes A and B fill a tank in fifteen and ten minutes; both are opened "
                 "together, but B is closed five minutes before the tank is full; find the total time. Question four: pipe "
                 "A fills a tank in eight hours; when the tank is half full, an outlet that empties a full tank in "
                 "twenty-four hours is also opened; find the total time to fill the tank. Question five: pipes A and B "
                 "fill a tank in four and six minutes; they are opened alternately for one minute each, A first; find the "
                 "time to fill the tank.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "before")
        self.play(FadeIn(rows[2], shift=RIGHT * 0.2))
        self.at_word(n, "half")
        self.play(FadeIn(rows[3], shift=RIGHT * 0.2))
        self.at_word(n, "alternately")
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
            text="Level three, question six: pipe A fills a tank in four minutes and pipe B empties a full tank in six "
                 "minutes; starting with an empty tank, they are opened alternately for one minute each, A first; when is "
                 "the tank full? Question seven: pipes A and B fill a tank in twenty-four and thirty-two minutes; both are "
                 "opened together; after how many minutes should B be closed so that the tank is full in eighteen minutes? "
                 "Question eight: pipes A and B fill a tank in twenty and thirty minutes, and pipe C empties a full tank "
                 "in fifteen minutes; A and B are opened on an empty tank, and C is opened six minutes later; find the "
                 "total time to fill the tank.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "alternately")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "closed")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.at_word(n, "later")
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
            text="One: sixty units, A five and B four. The first four minutes give thirty-six; twenty-four are left at "
                 "five a minute, four point eight minutes: eight point eight minutes in all.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "units")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "all")
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_02",
            text="Two: sixty units, A three and B two. A alone for five minutes gives fifteen; forty-five are left at five "
                 "a minute, nine minutes: fourteen minutes in all.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "units")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "all")
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_03",
            text="Three: thirty units, A two and B three. Two T plus three times T minus five is thirty, so five T is "
                 "forty-five, and T is nine minutes.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "units")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "nine")
        self.play(FadeIn(rows[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_04",
            text="Four: twenty-four units, A three an hour. Half the tank takes four hours; then the net is three minus "
                 "one, two an hour, for six hours: ten hours in all.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "units")
        self.play(FadeIn(rows[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "ten")
        self.play(FadeIn(rows[3][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Answer key  ·  5 to 8", GOOD)
        table, rows = self.answer_table(head, ANSWERS_B, 5)

        n = self.narrate(
            id="answers_05",
            text="Five: twelve units, A three and B two, five per cycle. Two cycles, four minutes, give ten units; in "
                 "minute five, A needs two units at three a minute, two thirds of a minute: four and two thirds minutes.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "units")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "thirds", occurrence=2)
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_06",
            text="Six: twelve units, A plus three and B minus two, so plus one per cycle. A lifts the level from k to k "
                 "plus three, which is twelve when k is nine. After nine cycles, eighteen minutes, the tank holds nine, "
                 "and minute nineteen fills it: nineteen minutes, not twenty-four.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "units")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "lifts")
        self.play(Indicate(rows[1][1], color=FOCUS, scale_factor=1.03))
        self.at_word(n, "nineteen")
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_07",
            text="Seven: ninety-six units, A four and B three. A over eighteen minutes gives seventy-two, so B must supply "
                 "twenty-four at three a minute: close B after eight minutes.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "units")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "close")
        self.play(FadeIn(rows[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_08",
            text="Eight: sixty units, A three, B two, C minus four. The first six minutes give thirty units; then the net "
                 "is one a minute for thirty more minutes: thirty-six minutes in all.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "units")
        self.play(FadeIn(rows[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "all")
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
            text="Recognise and move. The recognition cue: after x minutes, is closed, is opened later, before the tank is "
                 "full, when half full, or alternately.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "cue")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "closed")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_lens_02",
            text="The target time: fifty seconds, or sixty seconds for before full and alternate turns.",
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
            text="The sanity check: with inlets only, the total lies between the all-together time and the time of the "
                 "pipe left running alone; in an alternating cycle with an outlet, the answer ends on an inlet's turn.",
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
        draw = pill("draw the timeline:    sum of rate × open time  =  the tank", GOOD, size=LABEL)
        before = pill("“closed x minutes before full”:    let the total be T", WORD, size=LABEL)
        turns = pill("alternate turns:    full cycles, then turn by turn", RATIO, size=LABEL)
        halt = pill("an outlet takes turns:    stop the moment an inlet's turn fills the tank", FOCUS, size=LABEL)
        edit = text("the editing timeline: each track counts only while it is on", LABEL, MUTED)
        nxt = self.breadcrumb("Next", "Video 4 · Leaks & Cistern Problems")
        self.stack(head, [draw, before, turns, halt, edit, nxt], buff=0.45, top=0.6)

        n = self.narrate(
            id="summary_01",
            text="Draw the timeline, add each pipe's rate times its open time, and set the sum equal to the tank.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "timeline")
        self.play(FadeIn(draw, scale=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_02",
            text="For closed x minutes before full, let the total be T.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "total")
        self.play(FadeIn(before, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_03",
            text="For alternate turns, count full cycles and go turn by turn, and when an outlet takes turns, stop the "
                 "moment an inlet's turn fills the tank.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "cycles")
        self.play(FadeIn(turns, shift=UP * 0.1))
        self.at_word(n, "stop")
        self.play(FadeIn(halt, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_04",
            text="Remember the editing timeline.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "editing")
        self.play(FadeIn(edit, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_05",
            text="Next: leaks and cistern problems.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Next")
        self.play(FadeIn(nxt, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S16_summary")

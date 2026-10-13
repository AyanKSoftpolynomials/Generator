"""
animation.py for the LMS video generator.

Course : Pre-C-CAT - Section A - Quantitative Aptitude
Video  : Lesson 19 - Time & Distance - 03 - Relative Speed - Meeting & Chasing

Source script:
  C:\\Scripts\\Section A\\Aptitude\\Sessions 13-18 - Pipes, Time Distance, Partnership\\Lesson 19 - Time & Distance\\03 - Relative Speed - Meeting & Chasing.pdf

Built on the golden-reference pattern:
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``;
  * layouts stacked with next_to and guarded with ``no_overlap``; nothing is
    ever animated onto or into another box.

Lesson 19, Video 3 of 7. Not the first video of the lesson: a silent breadcrumb, a one-line recap of Video 2, then today's topic. No spoken course welcome.
The narration follows the script section by section. The eight concept steps are split over two screens. The six exam patterns are shown as two-line blocks.
The script's formula boxes print the "after meeting" relation as "speed of A : speed of B = b : a" (the square-root signs were lost); the concept step and the worked answers use the square root, so the screens show speed A : speed B = √b : √a, which is checked in the data block.
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
from math import isqrt

# ---- the hook: 360 km apart, 50 and 70 km/h, towards each other ----
CLOSING = 50 + 70
MEET = Fraction(360, CLOSING)
assert (CLOSING, MEET, 9 + MEET, 50 * MEET, 70 * MEET) == (120, 3, 12, 150, 210)

# ---- second worked example: the thief and the guard ----
HEAD = 8 * Fraction(15, 60)
CHASE = HEAD / (10 - 8)
assert (HEAD, CHASE, 10 * CHASE) == (2, 1, 10) and 8 * (Fraction(1, 4) + CHASE) == 10

# ---- exam patterns, traps, checkpoint, practice (answers computed) ----
assert Fraction(300, 40 + 60) == 3 and Fraction(200, 35 + 45) == Fraction(5, 2) and Fraction(4, 12 - 10) == 2
assert 40 * 2 == 80 and 11 + Fraction(80, 60 - 40) == 15 and 450 * Fraction(40, 90) == 200
# after meeting: speeds a and b, meeting after t; A needs (b t)/a more, B needs (a t)/b more
A_SP, B_SP, T = 2, 3, 6
assert (Fraction(B_SP * T, A_SP), Fraction(A_SP * T, B_SP)) == (9, 4) and isqrt(9 * 4) == T and (isqrt(4), isqrt(9)) == (A_SP, B_SP)
assert Fraction(210, 30 + 40) == 3 and 30 * 3 == 90
assert Fraction(280, 60 + 80) == 2 and (4 + 6) * 3 == 30 and Fraction(6, 18 - 15) == 2
assert 380 - 50 == 330 and 9 + Fraction(330, 50 + 60) == 12 and 50 * 4 == 200
THIEF = 9 * (Fraction(10, 60) + 9 * Fraction(10, 60) / (12 - 9))
assert THIEF == 6 and (isqrt(9), isqrt(16)) == (3, 4) and 45 * Fraction(4, 3) == 60
assert Fraction(2, 10) / (12 - 10) == Fraction(1, 10) and 10 * Fraction(1, 10) == 1 and Fraction(60, 50 - 40) == 6 and (50 + 40) * 6 == 540

OBJECTIVES = [("Choose the relative speed", "add for opposite directions, subtract for the same direction"),
              ("Find the meeting time and meeting point", "including bodies that start at different times"),
              ("Solve chases", "and use the “after meeting” square-root relation")]
STEPS_A = [("Watch the gap, not the bodies", "relative speed = the rate at which the distance between two bodies changes"),
           ("Opposite directions:  add", "towards each other or away from each other, the gap changes at the sum of the speeds"),
           ("Same direction:  subtract", "the gap changes at faster minus slower"),
           ("Time = gap ÷ relative speed", "for a meeting, the gap is the starting distance;    for a chase, it is the head start")]
STEPS_B = [("Meeting point:  distances are in the ratio of the speeds", "both move for the same time, so they share the gap in the ratio of their speeds"),
           ("Different starting times:  move the early starter first", "find where it is when the second body starts:  that gap is the one to close"),
           ("Chases:  head start = thief's speed × delay", "catch time = head start ÷ (police speed − thief speed),  counted from when the chase starts"),
           ("After meeting, they reach in a and b hours   (same start, opposite ends)", "speed A : speed B = √b : √a;     they met √(ab) hours after starting")]
FORMULAS = ["Opposite directions:   sum of the speeds                Same direction:   faster − slower",
            "Time to meet or catch   =   gap / relative speed",
            "Meeting point:    distances in the ratio of the speeds",
            "Head start  =  speed × delay;        count the chase time from the chaser's start",
            "Same start; after meeting in a and b hours:     speed A : speed B = √b : √a;      meeting time = √(ab)"]
PATTERNS = [("Towards each other", "300 km apart at 40 and 60 km/h", "300 ÷ 100", "3 h"),
            ("Moving apart", "from one point, opposite ways, at 35 and 45 km/h;   200 km apart when?", "200 ÷ 80", "2.5 h"),
            ("Same direction", "gap 4 km;   12 km/h behind 10 km/h", "4 ÷ 2", "2 h"),
            ("Different starts", "A leaves at 9 a.m. at 40 km/h;   B follows at 11 a.m. at 60 km/h", "head start 80 km;   80 ÷ 20", "3 p.m."),
            ("Meeting point", "450 km apart at 40 and 50 km/h", "ratio 4 : 5", "200 km from A's start"),
            ("After meeting", "A reaches 9 h and B 4 h after meeting", "√(4/9)", "speed A : speed B = 2 : 3")]
TRAPS = [("Trap 1  ·  speeds added in the same direction", "A cyclist at 12 km/h is 4 km behind one at 10 km/h.  Catch-up time?",
          "4 ÷ 22 h", "4 ÷ 2  =  2 h",
          "Same direction, subtract;  opposite directions, add."),
         ("Trap 2  ·  chase time counted from the wrong start",
          "A leaves at 9 a.m. at 40 km/h; B follows at 11 a.m. at 60 km/h.  When does B catch A?",
          "4 hours after 9 a.m.:  1 p.m.", "4 hours after 11 a.m.:  3 p.m.",
          "The gap is measured when the chaser starts, so the chase time is counted from then."),
         ("Trap 3  ·  the square-root ratio inverted",
          "After meeting, A takes 9 h and B takes 4 h to finish.  Ratio of their speeds, A : B?",
          "√(9/4)  =  3 : 2", "√(4/9)  =  2 : 3",
          "The one who needs longer after meeting is the slower one.")]
PRACTICE_A = [("L1", "Two cars 280 km apart drive towards each other at 60 and 80 km/h.  When do they meet?"),
              ("L1", "A and B start from the same point and walk in opposite directions at 4 and 6 km/h.  How far apart after 3 h?"),
              ("L2", "A cyclist at 15 km/h is 6 km ahead of another at 18 km/h, same direction.  How long to catch up?"),
              ("L2", "P and Q are 380 km apart.  A car leaves P at 8 a.m. at 50 km/h; another leaves Q at 9 a.m. at 60 km/h.  When, where?"),
              ("L2", "A thief runs at 9 km/h.  A policeman notices 10 minutes later and chases at 12 km/h.  How far does the thief run?")]
PRACTICE_B = [("L3", "After meeting, A takes 16 h and B 9 h to finish.  Ratio of speeds?  If A's speed is 45 km/h, find B's."),
              ("L3", "A policeman spots a thief 200 m ahead.  Thief 10 km/h, policeman 12 km/h.  How far does the thief run?"),
              ("L3", "Two cars start together from A and B towards each other at 50 and 40 km/h; at meeting one has done 60 km more.  AB?")]
ANSWERS_A = [("280 ÷ 140", "2 hours"),
             ("(4 + 6) × 3", "30 km"),
             ("6 ÷ (18 − 15)", "2 hours"),
             ("by 9 a.m. the first car has done 50 km;   330 ÷ 110 = 3 h", "12 noon,  200 km from P")]
ANSWERS_B = [("head start 9 × 1/6 = 1.5 km;   chase 1.5 ÷ 3 = 1/2 h;   9 × 2/3", "6 km"),
             ("speed A : speed B = √9 : √16 = 3 : 4;    45 × 4/3", "B:  60 km/h"),
             ("0.2 km ÷ 2 km/h = 0.1 h;    10 × 0.1", "1 km"),
             ("the faster gains 10 km an hour:  6 h;    (50 + 40) × 6", "540 km")]
LENS = [("Recognition cue", "two moving bodies, “towards”, “opposite”, “overtakes”, “catches”, “chases”:  relative speed"),
        ("Target time", "30 seconds;  45 seconds with different start times"),
        ("Sanity check", "at the meeting point the faster has covered more;  in a chase both are at the same place at the answer time")]


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


class RelativeSpeedMeetingAndChasingVideo(LMSScene):
    lesson_title = "Relative Speed: Meeting & Chasing"

    def construct(self):
        self.camera.background_color = BG

        self.intro()
        self.hook()
        self.objectives()
        self.why_this_matters()
        self.watch_the_gap()
        self.meetings_and_chases()
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

        crumb = self.breadcrumb("Quantitative Aptitude", "Lesson 19 · Time & Distance", "Video 3 of 7")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        recap = VGroup(text("last video", SMALL, MUTED), pill("same distance:  time is the inverse of speed", WORD, size=LABEL)).arrange(DOWN, buff=0.25)
        title = fit_width(text("Relative Speed: Meeting & Chasing", TITLE, INK, BOLD), SAFE_W - 0.4)
        today = text("today: watch the gap, not the bodies", LABEL, FOCUS)
        block = VGroup(recap, title, today).arrange(DOWN, buff=0.7)
        fit_within(block, SAFE_W, SAFE_H - crumb.height - 0.9)
        block.next_to(crumb, DOWN, buff=0.7)
        self.no_overlap(crumb, recap, title, today)
        self.validator.check_in_frame(VGroup(crumb, block))

        n = self.narrate(
            id="intro_01",
            text="In the last video, the same distance made time the inverse of speed.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.at_word(n, "inverse")
        self.play(FadeIn(recap, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="intro_02",
            text="Today: relative speed, meeting and chasing, where you watch the gap and not the bodies.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "relative")
        self.play(FadeIn(title, shift=UP * 0.1))
        self.at_word(n, "gap")
        self.play(FadeIn(today, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_intro")

    # ============================================== 1. HOOK ==========

    def hook(self):
        self.scene_start("S01_hook", title="Hook")

        head = self.heading("Two courier vans")
        road = VGroup(text("360 km apart", SMALL, MUTED), Line(LEFT * 2.2, RIGHT * 2.2, color=MUTED)).arrange(DOWN, buff=0.12)
        row = VGroup(pill("van 1:  50 km/h", WORD, size=LABEL), road, pill("van 2:  70 km/h", WORD, size=LABEL)).arrange(RIGHT, buff=0.4)
        start = text("both set out at 9 a.m., driving towards each other", LABEL, INK)
        ask = pill("when do they meet, and how far from the first city?", FOCUS, size=LABEL)
        one = text("not two equations: one speed, the speed at which the gap closes", LABEL, INK, BOLD)
        self.stack(head, [row, start, ask, one], buff=0.75, top=0.9)
        self.no_overlap(*row)

        n = self.narrate(
            id="hook_01",
            text="Two courier vans set out at nine in the morning from cities three hundred and sixty kilometres apart, "
                 "driving towards each other on the same highway, at fifty and seventy kilometres per hour.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "vans")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "apart")
        self.play(FadeIn(row[1]), FadeIn(start, shift=UP * 0.1))
        self.at_word(n, "fifty")
        self.play(FadeIn(row[0], shift=UP * 0.1))
        self.at_word(n, "seventy")
        self.play(FadeIn(row[2], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_02",
            text="They must meet to hand over a parcel. At what time do they meet, and how far from the first city should "
                 "the handover point be booked?",
            voice="default",
            subtitle=True,
            pause_after=3.0,
        )
        self.at_word(n, "hand")
        self.play(Indicate(start, color=FOCUS, scale_factor=1.03))
        self.at_word(n, "far")
        self.play(FadeIn(ask, scale=1.03))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="hook_03",
            text="You don't need two equations. You need one speed: the speed at which the gap closes.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "equations")
        self.play(FadeIn(one, shift=UP * 0.1))
        self.at_word(n, "closes")
        self.play(Indicate(one, color=FOCUS, scale_factor=1.03))
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
            text="First, choose the relative speed: add for opposite directions, subtract for the same direction.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "choose")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "add")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="objectives_03",
            text="Second, find the meeting time and meeting point, including bodies that start at different times.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "meeting")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "different")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="objectives_04",
            text="Third, solve chases, and use the after meeting square-root relation.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "chases")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "square-root")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_objectives")

    # ============================================== 3. WHY THIS MATTERS ==========

    def why_this_matters(self):
        self.scene_start("S03_why_this_matters", title="Why This Matters")

        head = self.heading("Why this matters")
        gap = fit_width(pill("two things moving at once:   the question is really about the gap between them", WORD, size=LABEL), SAFE_W - 0.4)
        one = text("relative speed turns a two-body problem into a one-body problem", LABEL, INK, BOLD)
        base = text("the foundation of the next three videos", LABEL, MUTED)
        self.stack(head, [gap, one, base], buff=0.9, top=1.1)

        n = self.narrate(
            id="why_this_matters_01",
            text="Whenever two things move at once, vehicles, trains, runners or boats, the question is really about the "
                 "gap between them.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "gap")
        self.play(FadeIn(gap, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="why_this_matters_02",
            text="Relative speed turns a two-body problem into a one-body problem, and it is the foundation of the next "
                 "three videos.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "turns")
        self.play(FadeIn(one, shift=UP * 0.1))
        self.at_word(n, "foundation")
        self.play(FadeIn(base, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_why_this_matters")

    # ============================================== 4. CONCEPT - WATCH THE GAP ==========

    def watch_the_gap(self):
        self.scene_start("S04_watch_the_gap", title="Concept - Watch the Gap")

        head = self.heading("Watch the gap")
        blocks = two_line_blocks(STEPS_A, WORD)
        self.stack(head, list(blocks), buff=0.5, top=0.7, align=LEFT)

        n = self.narrate(
            id="watch_the_gap_01",
            text="Watch the gap, not the bodies. Relative speed is the rate at which the distance between two bodies "
                 "changes.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "gap")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "rate")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="watch_the_gap_02",
            text="Opposite directions: add. Moving towards each other or away from each other, the gap changes at the sum "
                 "of the two speeds.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "add")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "sum")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="watch_the_gap_03",
            text="Same direction: subtract. The gap changes at the faster speed minus the slower.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "subtract")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "minus")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="watch_the_gap_04",
            text="Time is the gap divided by the relative speed. For a meeting, the gap is the starting distance; for a "
                 "chase, it is the head start.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "divided")
        self.play(FadeIn(blocks[3][0], shift=RIGHT * 0.2))
        self.at_word(n, "meeting")
        self.play(FadeIn(blocks[3][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_watch_the_gap")

    # ============================================== 5. CONCEPT - MEETINGS, LATE STARTS AND CHASES ==========

    def meetings_and_chases(self):
        self.scene_start("S05_meetings_and_chases", title="Concept - Meetings, Late Starts and Chases")

        head = self.heading("Meetings, late starts and chases")
        blocks = two_line_blocks(STEPS_B, WORD)
        self.stack(head, list(blocks), buff=0.5, top=0.7, align=LEFT)

        n = self.narrate(
            id="meetings_and_chases_01",
            text="At the meeting point, the distances are in the ratio of the speeds: both move for the same time, so they "
                 "cover the gap in that ratio.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "ratio")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "same")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="meetings_and_chases_02",
            text="With different starting times, move the early starter first. Find where it is when the second body "
                 "starts; the gap at that moment is the one to close.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "early")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "Find")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="meetings_and_chases_03",
            text="In a chase, the head start is the thief's speed times the delay, and the catch time is the head start "
                 "divided by police speed minus thief speed, counted from when the chase starts.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "head")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "divided")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="meetings_and_chases_04",
            text="After meeting, they reach in a and b hours. If A and B start at the same moment from opposite ends at "
                 "constant speeds, and A takes a hours and B takes b hours to finish after meeting, then A's speed to B's "
                 "speed is root b to root a, and they met root a b hours after starting.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "reach")
        self.play(FadeIn(blocks[3][0], shift=RIGHT * 0.2))
        self.at_word(n, "root")
        self.play(FadeIn(blocks[3][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_meetings_and_chases")

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
            text="Here is the formula box. Opposite directions: add the speeds. Same direction: faster minus slower.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "box")
        self.play(FadeIn(box[0]))
        self.at_word(n, "add")
        self.play(FadeIn(lines[0], shift=RIGHT * 0.2))
        self.at_word(n, "minus")
        self.play(Indicate(lines[0], color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_box_02",
            text="The time to meet or catch is the gap over the relative speed.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "gap")
        self.play(FadeIn(lines[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_box_03",
            text="At the meeting point, the distances are in the ratio of the speeds.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "ratio")
        self.play(FadeIn(lines[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_box_04",
            text="The head start is speed times delay, and the chase time is counted from the chaser's start.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "head")
        self.play(FadeIn(lines[3], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_box_05",
            text="And for the same start time, after meeting in a and b hours: the speeds are as root b to root a, and the "
                 "meeting time is root a b.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "root")
        self.play(FadeIn(lines[4], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_formula_box")

    # ============================================== 7. THE ANALOGY - TWO TUNNELLING CREWS ==========

    def analogy(self):
        self.scene_start("S07_analogy", title="The Analogy - Two Tunnelling Crews")

        head = self.heading("Two tunnelling crews")
        crews = pill("two crews boring from opposite sides of a mountain", WORD, size=LABEL)
        done = text("they finish when their combined digging equals the length of the tunnel", LABEL, INK, BOLD)
        rates = fit_width(pill("their rates add, as in Time & Work:   two vehicles close a gap the same way", FOCUS, size=LABEL), SAFE_W - 0.4)
        stops = VGroup(text("Where the analogy stops", LABEL, BAD, BOLD),
                       text("tunnel crews always work towards each other", LABEL, INK),
                       text("same direction: the gap closes at the difference of the speeds, or not at all", LABEL, MUTED)).arrange(DOWN, buff=0.2)
        self.stack(head, [crews, done, rates, stops], buff=0.6, top=0.7)

        n = self.narrate(
            id="analogy_01",
            text="Two crews boring a tunnel from opposite sides of a mountain finish when their combined digging equals "
                 "the length of the tunnel.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "crews")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "opposite")
        self.play(FadeIn(crews, shift=UP * 0.1))
        self.at_word(n, "combined")
        self.play(FadeIn(done, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_02",
            text="Their rates add, exactly as in time and work. Two vehicles approaching each other close the gap the same "
                 "way.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "add")
        self.play(FadeIn(rates, scale=1.03))
        self.at_word(n, "vehicles")
        self.play(Indicate(rates, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_03",
            text="Where the analogy stops: tunnel crews always work towards each other. When two vehicles move in the same "
                 "direction, the gap closes only at the difference of their speeds, or not at all if the one behind is "
                 "slower.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "stops")
        self.play(FadeIn(stops[0], shift=UP * 0.1))
        self.at_word(n, "always")
        self.play(FadeIn(stops[1], shift=UP * 0.1))
        self.at_word(n, "difference")
        self.play(FadeIn(stops[2], shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S07_analogy")

    # ============================================== 8. WORKED EXAMPLE - CLOSING THE HOOK ==========

    def hook_solved(self):
        self.scene_start("S08_hook_solved", title="Worked Example - Closing the Hook")

        head = self.heading("360 km apart, at 50 and 70 km/h")
        steps = self.solve_steps([("Relative speed:    50 + 70", "=  120 km/h"),
                                  ("Time:    360 ÷ 120  =  3 hours", "they meet at 12 noon"),
                                  ("First van:    50 × 3", "=  150 km"),
                                  ("Book the handover", "150 km from the first city  (210 from the second)")])
        self.stack(head, [steps], top=1.0)
        self.no_overlap(*steps)

        n = self.narrate(
            id="hook_solved_01",
            text="The relative speed is fifty plus seventy: one hundred and twenty kilometres per hour.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "plus")
        self.play(FadeIn(steps[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "twenty")
        self.play(FadeIn(steps[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_solved_02",
            text="The time is three hundred and sixty divided by one hundred and twenty, three hours, so they meet at "
                 "twelve noon.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "divided")
        self.play(FadeIn(steps[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "noon")
        self.play(FadeIn(steps[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_solved_03",
            text="The first van has covered fifty times three, one hundred and fifty kilometres.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "covered")
        self.play(FadeIn(steps[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "fifty", occurrence=2)
        self.play(FadeIn(steps[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_solved_04",
            text="So book the handover one hundred and fifty kilometres from the first city, which is two hundred and ten "
                 "from the second.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "book")
        self.play(FadeIn(steps[3], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S08_hook_solved")

    # ============================================== 9. A SECOND WORKED EXAMPLE - A CHASE WITH A DELAY ==========

    def second_example(self):
        self.scene_start("S09_second_example", title="A Second Worked Example - A Chase with a Delay")

        head = self.heading("A chase with a delay")
        ask = text("a thief runs at 8 km/h; a guard notices 15 minutes later and chases at 10 km/h:   when and where is he caught?", LABEL, MUTED)
        fit_width(ask, SAFE_W - 0.6)
        steps = self.solve_steps([("Head start:    8 × 1/4", "=  2 km"),
                                  ("Relative speed 10 − 8 = 2 km/h:    2 ÷ 2", "=  1 hour of chase"),
                                  ("The guard runs 10 × 1", "=  10 km"),
                                  ("Check:    the thief ran 1 1/4 hours at 8 km/h", "=  10 km")])
        self.stack(head, [ask, steps], buff=0.7, top=0.7)
        self.no_overlap(*steps)

        n = self.narrate(
            id="second_example_01",
            text="A thief snatches a laptop and runs at eight kilometres per hour. A guard notices fifteen minutes later "
                 "and chases at ten kilometres per hour. When and where is the thief caught?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "thief")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "guard")
        self.play(FadeIn(ask, shift=UP * 0.1))
        self.at_word(n, "caught")
        self.play(Indicate(ask, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_02",
            text="The head start is eight times a quarter of an hour: two kilometres.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "times")
        self.play(FadeIn(steps[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "two")
        self.play(FadeIn(steps[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_03",
            text="The relative speed is ten minus eight, two kilometres per hour, so the guard needs two divided by two: "
                 "one hour.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "minus")
        self.play(FadeIn(steps[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "hour", occurrence=2)
        self.play(FadeIn(steps[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_04",
            text="The guard runs ten times one: ten kilometres.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "runs")
        self.play(FadeIn(steps[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "kilometres")
        self.play(FadeIn(steps[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_05",
            text="Check: the thief has run for one and a quarter hours at eight kilometres per hour, which is also ten "
                 "kilometres.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Check")
        self.play(FadeIn(steps[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "also")
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
            text="Towards each other: three hundred kilometres apart, at forty and sixty kilometres per hour. Three "
                 "hundred divided by one hundred: three hours.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Towards")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "divided")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_03",
            text="Moving apart: from one point in opposite directions at thirty-five and forty-five kilometres per hour; "
                 "when are they two hundred kilometres apart? Two hundred divided by eighty: two and a half hours.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "apart")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "divided")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_04",
            text="Same direction: a gap of four kilometres, with twelve kilometres per hour behind ten. Four divided by "
                 "two: two hours.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "direction")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "divided")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Exam patterns  ·  4 to 6 of 6")
        blocks = self.pattern_blocks(PATTERNS[3:6])
        self.stack(head, list(blocks), buff=0.6, top=0.8, align=LEFT)

        n = self.narrate(
            id="exam_patterns_05",
            text="Different starts: A leaves at nine in the morning at forty kilometres per hour, and B follows from the "
                 "same point at eleven at sixty. The head start is eighty kilometres, and eighty divided by twenty is four "
                 "hours: three in the afternoon.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "starts")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "head")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_06",
            text="Meeting point: four hundred and fifty kilometres apart, at forty and fifty kilometres per hour. The "
                 "distances are in the ratio four to five: two hundred kilometres from A's start.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "point")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "ratio")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_07",
            text="After meeting: A reaches nine hours and B four hours after meeting. The root of four ninths: the speeds "
                 "are two to three.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "reaches")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "root")
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
            text="Trap one: speeds added in the same direction. A cyclist at twelve kilometres per hour is four kilometres "
                 "behind one at ten: what is the catch-up time?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "added")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "cyclist")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_02",
            text="The wrong instinct divides four by twenty-two. The correct answer is four divided by two: two hours.",
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
            text="The rule: same direction, subtract; opposite directions, add.",
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
            text="Trap two: the chase time counted from the wrong start. A leaves at nine in the morning at forty "
                 "kilometres per hour; B follows at eleven at sixty: when does B catch A?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "counted")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "leaves")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_05",
            text="The wrong instinct counts four hours from nine, and says one in the afternoon. The correct answer counts "
                 "four hours from eleven: three in the afternoon.",
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
            text="The rule: the gap is measured when the chaser starts, so the chase time is counted from then.",
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
            text="Trap three: the square-root ratio inverted. After meeting, A takes nine hours and B takes four hours to "
                 "finish: what is the ratio of their speeds, A to B?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "inverted")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "takes")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_08",
            text="The wrong instinct takes the root of nine over four: three to two. The correct answer is the root of "
                 "four over nine: two to three.",
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
            text="The rule: the one who needs longer after meeting is the slower one.",
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
        given = fit_width(pill("210 km apart, towards each other at 30 and 40 km/h:   when and where do they meet?", FOCUS, size=LABEL),
                          SAFE_W - 0.4)
        work = VGroup(text("210 ÷ 70  =  3 hours", BODY, INK, BOLD), text("90 km from the first train's start", BODY, GOOD, BOLD)).arrange(RIGHT, buff=0.8)
        self.stack(head, [given, work], buff=1.0, top=1.0)
        self.no_overlap(*work)

        n = self.narrate(
            id="checkpoint_01",
            text="Your turn. Two trains two hundred and ten kilometres apart move towards each other at thirty and forty "
                 "kilometres per hour. When and where do they meet?",
            voice="default",
            subtitle=True,
            pause_after=10.0,
        )
        self.at_word(n, "turn")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "trains")
        self.play(FadeIn(given, scale=1.03))
        self.at_word(n, "where")
        self.play(Indicate(given, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="checkpoint_02",
            text="After two hundred and ten divided by seventy, three hours, ninety kilometres from the first train's "
                 "start.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "divided")
        self.play(FadeIn(work[0], shift=UP * 0.1))
        self.at_word(n, "ninety")
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
            text="Level one, question one: two cars two hundred and eighty kilometres apart drive towards each other at "
                 "sixty and eighty kilometres per hour; when do they meet? Question two: A and B start from the same point "
                 "and walk in opposite directions at four and six kilometres per hour; how far apart are they after three "
                 "hours?",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "cars")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "walk")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="practice_02",
            text="Level two, question three: a cyclist riding at fifteen kilometres per hour is six kilometres ahead of "
                 "another riding at eighteen in the same direction; how long does the second take to catch up? Question "
                 "four: towns P and Q are three hundred and eighty kilometres apart; a car leaves P at eight in the "
                 "morning for Q at fifty kilometres per hour, and another leaves Q at nine for P at sixty; when and where "
                 "do they meet? Question five: a thief runs at nine kilometres per hour; a policeman notices ten minutes "
                 "later and chases at twelve; how far does the thief run before he is caught?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "cyclist")
        self.play(FadeIn(rows[2], shift=RIGHT * 0.2))
        self.at_word(n, "towns")
        self.play(FadeIn(rows[3], shift=RIGHT * 0.2))
        self.at_word(n, "thief")
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
            text="Level three, question six: A and B start at the same time towards each other; after meeting, A takes "
                 "sixteen hours and B nine hours to reach their destinations; find the ratio of their speeds, and B's "
                 "speed if A's is forty-five kilometres per hour. Question seven: a policeman spots a thief two hundred "
                 "metres ahead; the thief runs at ten kilometres per hour and the policeman at twelve; how far does the "
                 "thief run before he is caught? Question eight: two cars start at the same time from towns A and B "
                 "towards each other at fifty and forty kilometres per hour; when they meet, one has covered sixty "
                 "kilometres more than the other; find the distance A B.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "ratio")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "spots")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.at_word(n, "cars")
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
            text="One: two hundred and eighty divided by one hundred and forty is two hours.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "divided")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "two", occurrence=2)
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_02",
            text="Two: four plus six, times three, is thirty kilometres.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "plus")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "thirty")
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_03",
            text="Three: six divided by eighteen minus fifteen is two hours.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "divided")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "hours")
        self.play(FadeIn(rows[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_04",
            text="Four: by nine, the first car has covered fifty kilometres, leaving three hundred and thirty. Three "
                 "hundred and thirty divided by one hundred and ten is three hours, so they meet at twelve noon, two "
                 "hundred kilometres from P.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "covered")
        self.play(FadeIn(rows[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "noon")
        self.play(FadeIn(rows[3][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Answer key  ·  5 to 8", GOOD)
        table, rows = self.answer_table(head, ANSWERS_B, 5)

        n = self.narrate(
            id="answers_05",
            text="Five: the head start is nine times one sixth of an hour, one and a half kilometres, and the chase takes "
                 "half an hour. The thief runs for two thirds of an hour in all: six kilometres.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "head")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "six")
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_06",
            text="Six: the speeds are as root nine to root sixteen, three to four, so B's speed is forty-five times four "
                 "thirds: sixty kilometres per hour.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "root")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "sixty")
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_07",
            text="Seven: zero point two kilometres divided by two kilometres per hour is zero point one hours, so the "
                 "thief runs ten times zero point one: one kilometre.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "divided")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "kilometre")
        self.play(FadeIn(rows[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_08",
            text="Eight: the faster car gains ten kilometres every hour, so sixty kilometres takes six hours, and A B is "
                 "ninety times six: five hundred and forty kilometres.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "gains")
        self.play(FadeIn(rows[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "ninety")
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
            text="Recognise and move. The recognition cue: two moving bodies, with towards, opposite, overtakes, catches "
                 "or chases, means relative speed.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "cue")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "relative")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_lens_02",
            text="The target time: thirty seconds, or forty-five seconds with different start times.",
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
            text="The sanity check: at the meeting point, the faster body has covered more; in a chase, both bodies must "
                 "be at the same place at the answer time.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "sanity")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "faster")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S15_exam_lens")

    # ============================================== 16. QUICK REVISION AND SUMMARY ==========

    def summary(self):
        self.scene_start("S16_summary", title="Quick Revision and Summary")

        head = self.heading("Quick revision")
        watch = pill("watch the gap", GOOD, size=BODY)
        dirs = VGroup(pill("opposite directions:  add the speeds", WORD, size=LABEL), pill("same direction:  subtract", WORD, size=LABEL))\
            .arrange(RIGHT, buff=0.5)
        when = pill("time = gap ÷ relative speed,   the gap measured when both are moving", RATIO, size=LABEL)
        meet = text("meeting distances follow the speeds;    after meeting in a and b hours:  speeds as √b : √a", LABEL, INK, BOLD)
        fit_width(meet, SAFE_W - 0.6)
        crews = text("the tunnel crews: their rates add", LABEL, MUTED)
        nxt = self.breadcrumb("Next", "Video 4 · Problems on Trains")
        self.stack(head, [watch, dirs, when, meet, crews, nxt], buff=0.45, top=0.6)
        self.no_overlap(*dirs)

        n = self.narrate(
            id="summary_01",
            text="Watch the gap.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "gap")
        self.play(FadeIn(watch, scale=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_02",
            text="Opposite directions add the speeds; the same direction subtracts them.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "add")
        self.play(FadeIn(dirs[0], shift=UP * 0.1))
        self.at_word(n, "subtracts")
        self.play(FadeIn(dirs[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_03",
            text="Time is the gap divided by the relative speed, with the gap measured when both are moving.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "divided")
        self.play(FadeIn(when, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_04",
            text="Meeting distances follow the speeds, and after meeting in a and b hours, the speeds are as root b to "
                 "root a.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "follow")
        self.play(FadeIn(meet, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_05",
            text="Remember the tunnel crews.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "tunnel")
        self.play(FadeIn(crews, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_06",
            text="Next: problems on trains.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Next")
        self.play(FadeIn(nxt, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S16_summary")

"""
animation.py for the LMS video generator.

Course : Pre-C-CAT - Section A - Quantitative Aptitude
Video  : Lesson 19 - Time & Distance - 01 - Speed, Distance, Time & Units

Source script:
  C:\\Scripts\\Section A\\Aptitude\\Sessions 13-18 - Pipes, Time Distance, Partnership\\Lesson 19 - Time & Distance\\01 - Speed, Distance, Time & Units.pdf

Built on the golden-reference pattern:
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``;
  * layouts stacked with next_to and guarded with ``no_overlap``; nothing is
    ever animated onto or into another box.

Lesson 19, Video 1 of 7. First video of the lesson: a silent breadcrumb, "Now we start lesson nineteen", a one-line recap of Lesson 18, then today's topic. No spoken course welcome.
The narration follows the script section by section. The seven concept steps are split over two screens. The six exam patterns are shown as two-line blocks. The ratio lines of the formula box are written in words (no subscripts).
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

KMH_TO_MS = Fraction(5, 18)
assert KMH_TO_MS == Fraction(1000, 3600)

# ---- the hook: 72 km/h, 1.5 s delay ----
HOOK_MS = 72 * KMH_TO_MS
assert HOOK_MS == 20 and HOOK_MS * Fraction(3, 2) == 30

# ---- the concept examples; second worked example ----
assert Fraction(40, 60) == Fraction(2, 3) and 15 / KMH_TO_MS == 54 and (40 * 3, 60 * 3) == (120, 180)
assert Fraction(5 * 6, 6 + 4) == 3 and 4 * 3 == 12 and Fraction(12, 6) == 2                 # the office: 3 h there, 2 h back, 12 km

# ---- exam patterns, traps, checkpoint, practice (answers computed) ----
assert 90 * KMH_TO_MS == 25 and Fraction(25, 2) / KMH_TO_MS == 45 and Fraction(600, 120) / KMH_TO_MS == 18
assert (5 * 15, 4 * 15) == (75, 60) and (45 * 3, 60 * 3) == (135, 180) and Fraction(2 * 36 * 45, 36 + 45) == 40
assert 45 * Fraction(20, 60) == 15 and 36 * KMH_TO_MS == 10 and Fraction(36 * 18, 5) == Fraction(1296, 10)
assert 108 * KMH_TO_MS * 60 == 1800
assert 54 * KMH_TO_MS == 15 and 25 / KMH_TO_MS == 90 and 210 / Fraction(7, 2) == 60 and Fraction(900, 180) / KMH_TO_MS == 18
assert (3 * 20, 4 * 20) == (60, 80) and Fraction(160, 8) * 3 == 60 and 5 * 1 == 5 and Fraction(5, 3) * 60 == 100
assert 50 * 6 // 5 == 60 and Fraction(36, 72 - 54) == 2 and (54 * 2, 72 * 2) == (108, 144)

OBJECTIVES = [("Use D = S × T in all three forms", "with consistent units"),
              ("Convert between km/h and m/s", "in one step"),
              ("Use proportions", "fixed distance: speed and time are inverse;   fixed time: distance follows speed")]
STEPS_A = [("One relation, three forms", "Distance = Speed × Time;    Speed = Distance ÷ Time;    Time = Distance ÷ Speed"),
           ("Units must match:  km with hours, metres with seconds", "write minutes as a fraction of an hour:  40 minutes = 2/3 h"),
           ("km/h to m/s:  multiply by 5/18", "1 km/h = 1,000 m ÷ 3,600 s = 5/18 m/s;    72 km/h = 72 × 5/18 = 20 m/s"),
           ("m/s to km/h:  multiply by 18/5", "15 m/s = 15 × 18/5 = 54 km/h;    the m/s number is always the smaller one")]
STEPS_B = [("Fixed distance:  speed and time are inversely proportional", "speeds in the ratio 2 : 3 give times in the ratio 3 : 2"),
           ("Fixed time:  distance is proportional to speed", "in 3 hours, cars at 40 and 60 km/h cover 120 km and 180 km:  2 : 3"),
           ("Average speed = total distance ÷ total time   (Lesson 17)", "never the average of the speeds by default;    equal distances at x and y:  2xy/(x + y)")]
FORMULAS = ["D  =  S × T              S  =  D/T              T  =  D/S",
            "km/h  →  m/s:    × 5/18                    m/s  →  km/h:    × 18/5",
            "Same distance:   times are inverse to speeds            Same time:   distances follow speeds",
            "Average speed   =   total distance / total time      (Lesson 17)"]
PATTERNS = [("km/h to m/s", "90 km/h", "90 × 5/18", "25 m/s"),
            ("m/s to km/h", "12.5 m/s", "12.5 × 18/5", "45 km/h"),
            ("Mixed units", "600 m in 2 minutes", "5 m/s × 18/5", "18 km/h"),
            ("Speed ratio to time", "speeds 4 : 5;   the slower takes 15 min more", "times 5 : 4;   1 part = 15 min", "slower 75 min,  faster 60 min"),
            ("Same time", "two cars for 3 h at 45 and 60 km/h", "distance follows speed", "135 km and 180 km"),
            ("Average speed (Lesson 17)", "36 km/h out,  45 km/h back", "2 × 36 × 45/81", "40 km/h")]
TRAPS = [("Trap 1  ·  minutes used as hours", "A car runs at 45 km/h for 20 minutes.  Distance?",
          "45 × 20  =  900 km", "45 × 1/3  =  15 km",
          "With km/h, write every time in hours first."),
         ("Trap 2  ·  the conversion turned upside down", "Convert 36 km/h to m/s.",
          "36 × 18/5  =  129.6 m/s", "36 × 5/18  =  10 m/s",
          "The value in m/s is always smaller than the value in km/h."),
         ("Trap 3  ·  the speed ratio copied as the time ratio", "Speeds 3 : 4 over the same distance.  Ratio of times?",
          "3 : 4", "4 : 3",
          "For the same distance the faster one takes less time: invert the ratio.")]
PRACTICE_A = [("L1", "Convert 54 km/h to m/s."),
              ("L1", "Convert 25 m/s to km/h."),
              ("L2", "A car covers 210 km in 3 hours 30 minutes.  Find its speed."),
              ("L2", "A cyclist covers 900 m in 3 minutes.  Find the speed in km/h."),
              ("L2", "Speeds of A and B are in the ratio 3 : 4.  For the same distance A takes 20 min more than B.  B's time?")]
PRACTICE_B = [("L3", "A man walks to work at 5 km/h and returns at 3 km/h.  The round trip takes 2 h 40 min.  How far is it?"),
              ("L3", "A car covers a distance in 6 hours at 50 km/h.  What speed covers the same distance in 5 hours?"),
              ("L3", "Two trains run for the same time at 54 and 72 km/h; the faster covers 36 km more.  How long, how far each?")]
ANSWERS_A = [("54 × 5/18", "15 m/s"),
             ("25 × 18/5", "90 km/h"),
             ("210 ÷ 3.5", "60 km/h"),
             ("900 ÷ 180 = 5 m/s;     5 × 18/5", "18 km/h")]
ANSWERS_B = [("times 4 : 3;   1 part = 20 min;   B takes 3 × 20", "60 minutes  (A 80)"),
             ("times 3 : 5;   8 parts = 160 min;   there 60 min;   5 × 1", "5 km"),
             ("distance 50 × 6 = 300 km;     300 ÷ 5", "60 km/h"),
             ("gap grows at 72 − 54 = 18 km/h;    36 ÷ 18", "2 h;  108 and 144 km")]
LENS = [("Recognition cue", "km/h together with metres or seconds:  convert first;    “same distance”:  invert the speed ratio"),
        ("Target time", "20 seconds"),
        ("Sanity check", "an m/s value is a little over a quarter of the km/h value   (5/18 is about 0.28)")]


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


class SpeedDistanceTimeAndUnitsVideo(LMSScene):
    lesson_title = "Speed, Distance, Time & Units"

    def construct(self):
        self.camera.background_color = BG

        self.intro()
        self.hook()
        self.objectives()
        self.why_this_matters()
        self.relation_and_units()
        self.proportions()
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

        crumb = self.breadcrumb("Quantitative Aptitude", "Lesson 19 · Time & Distance", "Video 1 of 7")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        lesson = pill("Lesson 19  ·  Time & Distance", RATIO, size=LABEL)
        recap = VGroup(text("from Lesson 18  ·  Pipes & Cistern", SMALL, MUTED),
                       fit_width(VGroup(pill("every pipe is a signed rate", WORD, size=LABEL), pill("the net rate decides the time", GOOD, size=LABEL)).arrange(RIGHT, buff=0.4), SAFE_W - 0.6)).arrange(DOWN, buff=0.25)
        title = fit_width(text("Speed, Distance, Time & Units", TITLE, INK, BOLD), SAFE_W - 0.4)
        today = text("today: one relation, and one conversion factor", LABEL, FOCUS)
        block = VGroup(lesson, recap, title, today).arrange(DOWN, buff=0.55)
        fit_within(block, SAFE_W, SAFE_H - crumb.height - 0.9)
        block.next_to(crumb, DOWN, buff=0.6)
        self.no_overlap(crumb, lesson, recap, title, today)
        self.no_overlap(*recap[1])
        self.validator.check_in_frame(VGroup(crumb, block))

        n = self.narrate(
            id="intro_01",
            text="Now we start lesson nineteen: time and distance.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.at_word(n, "nineteen")
        self.play(FadeIn(lesson, scale=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="intro_02",
            text="In lesson eighteen, every pipe was a signed rate, and the net rate decided the time.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "signed")
        self.play(FadeIn(recap[0]), FadeIn(recap[1][0], shift=UP * 0.1))
        self.at_word(n, "net")
        self.play(FadeIn(recap[1][1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="intro_03",
            text="This first video is about speed, distance, time and units.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "speed")
        self.play(FadeIn(title, shift=UP * 0.1))
        self.at_word(n, "units")
        self.play(FadeIn(today, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_intro")

    # ============================================== 1. HOOK ==========

    def hook(self):
        self.scene_start("S01_hook", title="Hook")

        head = self.heading("A self-driving car")
        dash = VGroup(pill("speed:  72 km/h", WORD, size=BODY), pill("braking system delay:  1.5 s", BAD, size=BODY)).arrange(RIGHT, buff=0.6)
        keeps = text("during the delay the car keeps moving at full speed", LABEL, MUTED)
        ask = pill("how many metres before the brakes even engage?", FOCUS, size=LABEL)
        units = text("the speed is in kilometres per hour, the delay in seconds", LABEL, INK)
        factor = text("one conversion factor settles it: the most used number in this lesson", LABEL, INK, BOLD)
        self.stack(head, [dash, keeps, ask, units, factor], buff=0.6, top=0.7)
        self.no_overlap(*dash)

        n = self.narrate(
            id="hook_01",
            text="A self-driving car is moving at seventy-two kilometres per hour when its camera spots an obstacle.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "moving")
        self.play(FadeIn(dash[0], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_02",
            text="The braking system needs one and a half seconds to respond, and during that time the car keeps moving at "
                 "full speed.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "needs")
        self.play(FadeIn(dash[1], shift=UP * 0.1))
        self.at_word(n, "keeps")
        self.play(FadeIn(keeps, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_03",
            text="How many metres does it travel before the brakes even engage?",
            voice="default",
            subtitle=True,
            pause_after=3.0,
        )
        self.at_word(n, "metres")
        self.play(FadeIn(ask, scale=1.03))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="hook_04",
            text="The speed is in kilometres per hour and the delay is in seconds. One conversion factor settles it, and "
                 "it is the most used number in this lesson.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "delay")
        self.play(FadeIn(units, shift=UP * 0.1))
        self.at_word(n, "factor")
        self.play(FadeIn(factor, shift=UP * 0.1))
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
            text="First, use D equals S times T in all three forms, with consistent units.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "forms")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "consistent")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="objectives_03",
            text="Second, convert between kilometres per hour and metres per second in one step.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "convert")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "step")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="objectives_04",
            text="Third, use proportions: at a fixed distance, speed and time are inverse; in a fixed time, distance "
                 "follows speed.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "proportions")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "inverse")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_objectives")

    # ============================================== 3. WHY THIS MATTERS ==========

    def why_this_matters(self):
        self.scene_start("S03_why_this_matters", title="Why This Matters")

        head = self.heading("Why this matters")
        under = pill("trains, boats, races:   all of it is  D = S × T  underneath", WORD, size=LABEL)
        errors = text("most errors are not in the idea but in the units", LABEL, INK, BOLD)
        mixes = VGroup(pill("kilometres mixed with metres", BAD, size=LABEL), pill("minutes left as whole numbers", BAD, size=LABEL))\
            .arrange(RIGHT, buff=0.5)
        self.stack(head, [under, errors, mixes], buff=0.9, top=1.1)
        self.no_overlap(*mixes)

        n = self.narrate(
            id="why_this_matters_01",
            text="Every question in this lesson, from trains to boats to races, is D equals S times T underneath.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "underneath")
        self.play(FadeIn(under, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="why_this_matters_02",
            text="Most errors are not in the idea but in the units: kilometres mixed with metres, or minutes left as whole "
                 "numbers.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "units")
        self.play(FadeIn(errors, shift=UP * 0.1))
        self.at_word(n, "mixed")
        self.play(FadeIn(mixes[0], shift=UP * 0.1))
        self.at_word(n, "whole")
        self.play(FadeIn(mixes[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_why_this_matters")

    # ============================================== 4. CONCEPT - ONE RELATION, MATCHING UNITS ==========

    def relation_and_units(self):
        self.scene_start("S04_relation_and_units", title="Concept - One Relation, Matching Units")

        head = self.heading("One relation, matching units")
        blocks = two_line_blocks(STEPS_A, WORD)
        self.stack(head, list(blocks), buff=0.5, top=0.7, align=LEFT)

        n = self.narrate(
            id="relation_and_units_01",
            text="One relation, three forms: distance is speed times time, speed is distance divided by time, and time is "
                 "distance divided by speed.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "forms")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "times")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="relation_and_units_02",
            text="Units must match: kilometres with hours, metres with seconds. Write minutes as a fraction of an hour: "
                 "forty minutes is two thirds of an hour.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "match")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "fraction")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="relation_and_units_03",
            text="From kilometres per hour to metres per second, multiply by five over eighteen. One kilometre per hour is "
                 "one thousand metres in three thousand six hundred seconds, so seventy-two kilometres per hour is twenty "
                 "metres per second.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "multiply")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "thousand")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="relation_and_units_04",
            text="From metres per second to kilometres per hour, multiply by eighteen over five. Fifteen metres per second "
                 "is fifty-four kilometres per hour. The metres per second number is always the smaller one.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "multiply")
        self.play(FadeIn(blocks[3][0], shift=RIGHT * 0.2))
        self.at_word(n, "Fifteen")
        self.play(FadeIn(blocks[3][1], shift=RIGHT * 0.2))
        self.at_word(n, "smaller")
        self.play(Indicate(blocks[3][1], color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_relation_and_units")

    # ============================================== 5. CONCEPT - PROPORTIONS AND AVERAGE SPEED ==========

    def proportions(self):
        self.scene_start("S05_proportions", title="Concept - Proportions and Average Speed")

        head = self.heading("Proportions, and average speed")
        blocks = two_line_blocks(STEPS_B, WORD)
        self.stack(head, list(blocks), buff=0.75, top=1.0, align=LEFT)

        n = self.narrate(
            id="proportions_01",
            text="At a fixed distance, speed and time are inversely proportional: speeds in the ratio two to three give "
                 "times in the ratio three to two.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "inversely")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "give")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="proportions_02",
            text="In a fixed time, distance is proportional to speed: in three hours, cars at forty and sixty kilometres "
                 "per hour cover one hundred and twenty and one hundred and eighty kilometres, in the ratio two to three.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "proportional")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "cover")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="proportions_03",
            text="Average speed, a recap from lesson seventeen, is total distance divided by total time, never the average "
                 "of the speeds by default; equal distances at x and y give two x y over x plus y.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "divided")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "never")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_proportions")

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
            text="Here is the formula box. D is S times T, S is D over T, and T is D over S.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "box")
        self.play(FadeIn(box[0]))
        self.at_word(n, "times")
        self.play(FadeIn(lines[0], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_box_02",
            text="Kilometres per hour to metres per second: times five over eighteen. Metres per second to kilometres per "
                 "hour: times eighteen over five.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "five")
        self.play(FadeIn(lines[1], shift=RIGHT * 0.2))
        self.at_word(n, "eighteen", occurrence=2)
        self.play(Indicate(lines[1], color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_box_03",
            text="For the same distance, the times are in the inverse ratio of the speeds; for the same time, the "
                 "distances are in the ratio of the speeds.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "inverse")
        self.play(FadeIn(lines[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_box_04",
            text="And average speed is total distance over total time, from lesson seventeen.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "average")
        self.play(FadeIn(lines[3], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_formula_box")

    # ============================================== 7. THE ANALOGY - TWO CURRENCIES ==========

    def analogy(self):
        self.scene_start("S07_analogy", title="The Analogy - Two Currencies")

        head = self.heading("Two currencies")
        board = VGroup(pill("km/h", WORD, size=BODY), text("×  5/18  →", BODY, MUTED), pill("m/s", WORD, size=BODY)).arrange(RIGHT, buff=0.4)
        never = text("never add rupees to dollars without converting;   never multiply km/h by seconds", LABEL, INK, BOLD)
        fit_width(never, SAFE_W - 0.6)
        pick = pill("pick one currency, convert everything into it, then calculate", FOCUS, size=LABEL)
        stops = VGroup(text("Where the analogy stops", LABEL, BAD, BOLD),
                       text("exchange rates change daily", LABEL, INK),
                       text("5/18 is exact and permanent:   1,000 m per km,   3,600 s per hour", LABEL, MUTED)).arrange(DOWN, buff=0.2)
        self.stack(head, [board, never, pick, stops], buff=0.6, top=0.7)
        self.no_overlap(*board)

        n = self.narrate(
            id="analogy_01",
            text="Think of kilometres per hour and metres per second as two currencies.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Think")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "currencies")
        self.play(FadeIn(board))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_02",
            text="You would never add rupees to dollars without converting, and you would never multiply a speed in "
                 "kilometres per hour by a time in seconds.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "rupees")
        self.play(FadeIn(never, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_03",
            text="Pick one currency for the whole question, convert everything into it, and only then calculate.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Pick")
        self.play(FadeIn(pick, scale=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_04",
            text="Where the analogy stops: exchange rates change daily. The factor five over eighteen is exact and "
                 "permanent, because it comes from one thousand metres per kilometre and three thousand six hundred "
                 "seconds per hour.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "stops")
        self.play(FadeIn(stops[0], shift=UP * 0.1))
        self.at_word(n, "daily")
        self.play(FadeIn(stops[1], shift=UP * 0.1))
        self.at_word(n, "permanent")
        self.play(FadeIn(stops[2], shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S07_analogy")

    # ============================================== 8. WORKED EXAMPLE - CLOSING THE HOOK ==========

    def hook_solved(self):
        self.scene_start("S08_hook_solved", title="Worked Example - Closing the Hook")

        head = self.heading("72 km/h for 1.5 seconds")
        steps = self.solve_steps([("Speed:    72 × 5/18", "=  20 m/s"),
                                  ("Distance in 1.5 s:    20 × 1.5", "=  30 m"),
                                  ("The car travels", "30 m before the brakes engage")])
        strip = VGroup(Rectangle(width=6.0, height=0.25, color=WORD, fill_color=WORD, fill_opacity=0.5), text("30 m", SMALL, WORD, BOLD))\
            .arrange(RIGHT, buff=0.3)
        self.stack(head, [steps, strip], buff=0.9, top=1.1)
        self.no_overlap(*steps)

        n = self.narrate(
            id="hook_solved_01",
            text="The speed is seventy-two times five over eighteen: twenty metres per second.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "times")
        self.play(FadeIn(steps[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "twenty")
        self.play(FadeIn(steps[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_solved_02",
            text="In one and a half seconds, that is twenty times one point five: thirty metres.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "times")
        self.play(FadeIn(steps[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "thirty")
        self.play(FadeIn(steps[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_solved_03",
            text="The car travels thirty metres before the brakes even engage.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "travels")
        self.play(FadeIn(steps[2], shift=RIGHT * 0.2), FadeIn(strip))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S08_hook_solved")

    # ============================================== 9. A SECOND WORKED EXAMPLE - INVERSE PROPORTION ==========

    def second_example(self):
        self.scene_start("S09_second_example", title="A Second Worked Example - Inverse Proportion")

        head = self.heading("Inverse proportion:  the walk to the office")
        ask = text("walks there at 4 km/h, returns at 6 km/h; the round trip takes 5 hours:   how far is the office?", LABEL, MUTED)
        fit_width(ask, SAFE_W - 0.6)
        steps = self.solve_steps([("Same distance:    times in the ratio 6 : 4", "=  3 : 2"),
                                  ("5 parts = 5 hours:    there 3 h", "back 2 h"),
                                  ("Distance:    4 × 3", "=  12 km"),
                                  ("Check:    12 ÷ 6", "=  2 h")])
        self.stack(head, [ask, steps], buff=0.7, top=0.7)
        self.no_overlap(*steps)

        n = self.narrate(
            id="second_example_01",
            text="A man walks to his office at four kilometres per hour and returns along the same road at six kilometres "
                 "per hour. The round trip takes five hours. How far is the office?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "walks")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "returns")
        self.play(FadeIn(ask, shift=UP * 0.1))
        self.at_word(n, "trip")
        self.play(Indicate(ask, color=FOCUS, scale_factor=1.03))
        self.at_word(n, "far")
        self.play(Indicate(ask, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_02",
            text="It is the same distance, so the times are in the ratio six to four, which is three to two.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "ratio")
        self.play(FadeIn(steps[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "which")
        self.play(FadeIn(steps[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_03",
            text="Five parts are five hours, so the walk there takes three hours and the walk back two.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "parts")
        self.play(FadeIn(steps[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "back")
        self.play(FadeIn(steps[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_04",
            text="The distance is four times three: twelve kilometres.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "times")
        self.play(FadeIn(steps[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "twelve")
        self.play(FadeIn(steps[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_05",
            text="Check: twelve divided by six is two hours.",
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
            text="Kilometres per hour to metres per second: ninety kilometres per hour. Ninety times five over eighteen: "
                 "twenty-five metres per second.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "ninety")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "times")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_03",
            text="Metres per second to kilometres per hour: twelve point five metres per second. Times eighteen over five: "
                 "forty-five kilometres per hour.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "twelve")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "Times")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_04",
            text="Mixed units: six hundred metres in two minutes. That is five metres per second, times eighteen over "
                 "five: eighteen kilometres per hour.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Mixed")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "times")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Exam patterns  ·  4 to 6 of 6")
        blocks = self.pattern_blocks(PATTERNS[3:6])
        self.stack(head, list(blocks), buff=0.6, top=0.8, align=LEFT)

        n = self.narrate(
            id="exam_patterns_05",
            text="Speed ratio to time: speeds four to five, and the slower takes fifteen minutes more. The times are five "
                 "to four, and one part is fifteen minutes: the slower takes seventy-five minutes and the faster sixty.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "ratio")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "part")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_06",
            text="Same time: two cars run for three hours at forty-five and sixty kilometres per hour. Distance follows "
                 "speed: one hundred and thirty-five and one hundred and eighty kilometres.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "cars")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "follows")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_07",
            text="Average speed, from lesson seventeen: thirty-six kilometres per hour out and forty-five back. Two times "
                 "thirty-six times forty-five, over eighty-one: forty kilometres per hour.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Average")
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
            text="Trap one: minutes used as hours. A car runs at forty-five kilometres per hour for twenty minutes: what "
                 "is the distance?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "minutes")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "car")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_02",
            text="The wrong instinct multiplies forty-five by twenty: nine hundred kilometres. The correct answer is "
                 "forty-five times one third: fifteen kilometres.",
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
            text="The rule: with kilometres per hour, write every time in hours first.",
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
            text="Trap two: the conversion turned upside down. Convert thirty-six kilometres per hour to metres per "
                 "second.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "upside")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "Convert")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_05",
            text="The wrong instinct multiplies by eighteen over five: one hundred and twenty-nine point six metres per "
                 "second. The correct answer multiplies by five over eighteen: ten metres per second.",
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
            text="The rule: the value in metres per second is always smaller than the value in kilometres per hour.",
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
            text="Trap three: the speed ratio copied as the time ratio. Speeds are three to four over the same distance: "
                 "what is the ratio of times?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "copied")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "Speeds")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_08",
            text="The wrong instinct says three to four. The correct answer is four to three.",
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
            text="The rule: for the same distance, the faster one takes less time; invert the ratio.",
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
        given = pill("a train runs at 108 km/h:   how many metres does it cover in one minute?", FOCUS, size=LABEL)
        work = VGroup(text("108 × 5/18  =  30 m/s", BODY, INK, BOLD), text("30 × 60 s  =  1,800 m", BODY, GOOD, BOLD)).arrange(RIGHT, buff=0.8)
        self.stack(head, [given, work], buff=1.0, top=1.0)
        self.no_overlap(*work)

        n = self.narrate(
            id="checkpoint_01",
            text="Your turn. A train runs at one hundred and eight kilometres per hour. How many metres does it cover in "
                 "one minute?",
            voice="default",
            subtitle=True,
            pause_after=10.0,
        )
        self.at_word(n, "turn")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "train")
        self.play(FadeIn(given, scale=1.03))
        self.at_word(n, "metres")
        self.play(Indicate(given, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="checkpoint_02",
            text="One hundred and eight times five over eighteen is thirty metres per second, and thirty times sixty "
                 "seconds is one thousand eight hundred metres.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "over")
        self.play(FadeIn(work[0], shift=UP * 0.1))
        self.at_word(n, "sixty")
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
            text="Level one, question one: convert fifty-four kilometres per hour to metres per second. Question two: "
                 "convert twenty-five metres per second to kilometres per hour.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "fifty-four")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "twenty-five")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="practice_02",
            text="Level two, question three: a car covers two hundred and ten kilometres in three hours thirty minutes; "
                 "find its speed. Question four: a cyclist covers nine hundred metres in three minutes; find the speed in "
                 "kilometres per hour. Question five: the speeds of A and B are in the ratio three to four; for the same "
                 "distance, A takes twenty minutes more than B; how long does B take?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "car")
        self.play(FadeIn(rows[2], shift=RIGHT * 0.2))
        self.at_word(n, "cyclist")
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
            text="Level three, question six: a man walks to work at five kilometres per hour and returns at three "
                 "kilometres per hour; the round trip takes two hours forty minutes; how far is his workplace? Question "
                 "seven: a car covers a distance in six hours at fifty kilometres per hour; at what speed must it travel "
                 "to cover the same distance in five hours? Question eight: two trains start at the same time and run for "
                 "the same time at fifty-four and seventy-two kilometres per hour; the faster one covers thirty-six "
                 "kilometres more; how long did they run, and how far did each go?",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "walks")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "car")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.at_word(n, "trains")
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
            text="One: fifty-four times five over eighteen is fifteen metres per second.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "over")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "fifteen")
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_02",
            text="Two: twenty-five times eighteen over five is ninety kilometres per hour.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "over")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "ninety")
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_03",
            text="Three: two hundred and ten divided by three point five is sixty kilometres per hour.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "divided")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "sixty")
        self.play(FadeIn(rows[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_04",
            text="Four: nine hundred divided by one hundred and eighty is five metres per second, and five times eighteen "
                 "over five is eighteen kilometres per hour.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "divided")
        self.play(FadeIn(rows[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "kilometres")
        self.play(FadeIn(rows[3][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Answer key  ·  5 to 8", GOOD)
        table, rows = self.answer_table(head, ANSWERS_B, 5)

        n = self.narrate(
            id="answers_05",
            text="Five: the times are four to three; the difference, one part, is twenty minutes, so B takes three times "
                 "twenty, sixty minutes, and A eighty.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "times")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "sixty")
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_06",
            text="Six: the times are three to five; eight parts are one hundred and sixty minutes, so one part is twenty "
                 "minutes and the walk there takes sixty minutes. The distance is five times one: five kilometres.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "parts")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "distance")
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_07",
            text="Seven: the distance is three hundred kilometres, and three hundred divided by five is sixty kilometres "
                 "per hour.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "distance")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "sixty")
        self.play(FadeIn(rows[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_08",
            text="Eight: the gap grows at seventy-two minus fifty-four, eighteen kilometres per hour, so thirty-six "
                 "kilometres takes two hours. The distances are one hundred and eight and one hundred and forty-four "
                 "kilometres.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "gap")
        self.play(FadeIn(rows[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "distances")
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
            text="Recognise and move. The recognition cue: kilometres per hour together with metres or seconds means "
                 "convert first; same distance means invert the speed ratio.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "cue")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "convert")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_lens_02",
            text="The target time: twenty seconds.",
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
            text="The sanity check: a metres per second value is a little over a quarter of the kilometres per hour value.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "sanity")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "quarter")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S15_exam_lens")

    # ============================================== 16. QUICK REVISION AND SUMMARY ==========

    def summary(self):
        self.scene_start("S16_summary", title="Quick Revision and Summary")

        head = self.heading("Quick revision")
        dst = pill("D = S × T,  with matching units", GOOD, size=BODY)
        conv = VGroup(pill("km/h → m/s:   × 5/18", WORD, size=LABEL), pill("m/s → km/h:   × 18/5", WORD, size=LABEL)).arrange(RIGHT, buff=0.5)
        prop = VGroup(pill("fixed distance:  times inverse to speeds", RATIO, size=SMALL), pill("fixed time:  distances follow speeds", RATIO, size=SMALL))\
            .arrange(RIGHT, buff=0.4)
        avg = text("average speed  =  total distance ÷ total time    (Lesson 17)", LABEL, MUTED)
        nxt = self.breadcrumb("Next", "Video 2 · Speed Changes: Late, Early & Ratios")
        self.stack(head, [dst, conv, prop, avg, nxt], buff=0.6, top=0.7)
        self.no_overlap(*conv)
        self.no_overlap(*prop)

        n = self.narrate(
            id="summary_01",
            text="D equals S times T, with matching units.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "matching")
        self.play(FadeIn(dst, scale=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_02",
            text="Multiply by five over eighteen to go from kilometres per hour to metres per second, and by eighteen over "
                 "five to come back.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "five")
        self.play(FadeIn(conv[0], shift=UP * 0.1))
        self.at_word(n, "back")
        self.play(FadeIn(conv[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_03",
            text="At a fixed distance, times are in the inverse ratio of speeds; in a fixed time, distances follow speeds.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "inverse")
        self.play(FadeIn(prop[0], shift=UP * 0.1))
        self.at_word(n, "follow")
        self.play(FadeIn(prop[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_04",
            text="Average speed is total distance over total time, from lesson seventeen.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Average")
        self.play(FadeIn(avg, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_05",
            text="Next: speed changes: late, early and ratios.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Next")
        self.play(FadeIn(nxt, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S16_summary")

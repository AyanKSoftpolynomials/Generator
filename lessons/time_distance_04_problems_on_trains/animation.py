"""
animation.py for the LMS video generator.

Course : Pre-C-CAT - Section A - Quantitative Aptitude
Video  : Lesson 19 - Time & Distance - 04 - Problems on Trains

Source script:
  C:\\Scripts\\Section A\\Aptitude\\Sessions 13-18 - Pipes, Time Distance, Partnership\\Lesson 19 - Time & Distance\\04 - Problems on Trains.pdf

Built on the golden-reference pattern:
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``;
  * layouts stacked with next_to and guarded with ``no_overlap``; nothing is
    ever animated onto or into another box.

Lesson 19, Video 4 of 7. Not the first video of the lesson: a silent breadcrumb, a one-line recap of Video 3, then today's topic. No spoken course welcome.
The narration follows the script section by section. The seven concept steps are split over two screens. The six exam patterns are shown as two-line blocks. The script's subscripted symbols are written in words (sum of lengths, T and t).
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


def ms(kmh):
    return Fraction(kmh) * 5 / 18


def cross(lengths, speed_kmh):
    """Seconds to cover the given lengths (metres) at a speed in km/h."""
    return Fraction(sum(lengths)) / ms(speed_kmh)


# ---- the hook: a 240 m train passes a pole in 12 s; a 360 m platform ----
HOOK_SPEED = Fraction(240, 12)
assert HOOK_SPEED == 20 and Fraction(240 + 360, HOOK_SPEED) == 30 and Fraction(360, HOOK_SPEED) == 18

# ---- second worked example: 150 m and 200 m at 54 and 72 km/h ----
assert (ms(54 + 72), ms(72 - 54)) == (35, 5) and (cross([150, 200], 54 + 72), cross([150, 200], 72 - 54)) == (10, 70)

# ---- exam patterns, traps, checkpoint, practice (answers computed) ----
assert cross([180], 54) == 12 and cross([200, 300], 72) == 25 and cross([120, 130], 40 + 50) == 10
assert cross([100, 150], 68 - 50) == 50 and cross([220], 60 + 6) == 12 and Fraction(150, 25 - 10) == 10 and 10 * 10 == 100
assert round(float(Fraction(180, 54)), 1) == 3.3 and round(float(cross([100, 150], 68 + 50)), 1) == 7.6
assert ms(90) == 25 and cross([300, 200], 90) == 20
assert cross([150], 54) == 10 and cross([250, 350], 90) == 24 and Fraction(180, 21 - 9) == 15 == ms(54) and 15 * 9 == 135
assert cross([140, 160], 50 + 58) == 10 and cross([200], 63 - 3) == 12
assert 9 * (22 - 2) == 10 * (22 - 4) and 9 * ms(22 - 2) == 50 == 10 * ms(22 - 4)
assert ms(60 - 42) * 20 == 100 and ms(46 - 36) * 36 == 100

OBJECTIVES = [("Decide the distance a train must cover", "to cross a pole, a man, a platform or another train"),
              ("Use relative speed", "for two trains, or for a train and a moving man"),
              ("Find a train's length and speed", "from two crossing times")]
STEPS_A = [("Crossing means front in, back out", "starts when the engine reaches the object, ends when the last coach clears it"),
           ("Pole, standing man, signal post:  distance = the train's length", "these objects have no length worth counting"),
           ("Platform, bridge, tunnel, a stationary train:  distance = sum of the lengths", "the train's own length is always part of the trip"),
           ("Two moving trains:  distance = sum of lengths,  speed = relative speed", "add the speeds for opposite directions;    subtract for the same direction")]
STEPS_B = [("A moving man is a train of length zero", "distance = the train's length;    speed = relative speed of train and man"),
           ("Convert km/h to m/s first", "lengths are in metres and times in seconds"),
           ("Two crossings give length and speed", "pole in t, platform P in T:    speed = P ÷ (T − t);    length = speed × t")]
FORMULAS = ["Time to cross   =   (sum of the lengths involved) / relative speed",
            "Pole or standing man:    L/S                      Platform or bridge:    (L + P)/S",
            "Two trains:    sum of lengths ÷ sum of speeds  (opposite);        ÷ difference of speeds  (same direction)",
            "Pole in t, platform P in T:       S  =  P/(T − t),         L  =  S × t"]
PATTERNS = [("Pole", "180 m train at 54 km/h", "180 ÷ 15", "12 s"),
            ("Platform", "200 m train at 72 km/h;   300 m platform", "500 ÷ 20", "25 s"),
            ("Two trains, opposite", "120 m and 130 m at 40 and 50 km/h", "250 ÷ 25", "10 s"),
            ("Two trains, same direction", "100 m and 150 m at 68 and 50 km/h", "250 ÷ 5", "50 s"),
            ("Moving man", "220 m train at 60 km/h;   man at 6 km/h towards it", "220 ÷ (66 × 5/18)", "12 s"),
            ("Length from two crossings", "pole in 10 s;   150 m platform in 25 s", "S = 150 ÷ 15 = 10 m/s", "100 m")]
TRAPS = [("Trap 1  ·  the train's own length forgotten", "A 240 m train at 20 m/s goes through a 360 m platform.  Time?",
          "360 ÷ 20  =  18 s", "600 ÷ 20  =  30 s",
          "For anything with length, add the train's length."),
         ("Trap 2  ·  km/h used with metres", "A 180 m train at 54 km/h passes a pole.  Time?",
          "180 ÷ 54:  about 3.3 s", "180 ÷ 15  =  12 s",
          "Convert to m/s before dividing metres by speed."),
         ("Trap 3  ·  speeds added for trains moving the same way", "100 m and 150 m trains at 68 and 50 km/h, same direction.  Time?",
          "250 ÷ (118 × 5/18):  7.6 s", "250 ÷ (18 × 5/18)  =  50 s",
          "Overtaking is slow: it uses the difference of the speeds.")]
PRACTICE_A = [("L1", "A 150 m train runs at 54 km/h.  How long does it take to pass a pole?"),
              ("L1", "A 250 m train at 90 km/h crosses a 350 m platform.  Find the time."),
              ("L2", "A train passes a pole in 9 seconds and a 180 m platform in 21 seconds.  Find its length and its speed in km/h."),
              ("L2", "Trains of 140 m and 160 m run in opposite directions at 50 and 58 km/h.  How long to cross each other?"),
              ("L2", "A 200 m train at 63 km/h overtakes a man walking at 3 km/h in the same direction.  How long to pass him?")]
PRACTICE_B = [("L3", "A train passes two men walking its way at 2 and 4 km/h in 9 s and 10 s.  Find the train's length and speed."),
              ("L3", "Trains run the same way at 60 and 42 km/h.  A man in the slower sees the faster pass in 20 s.  Its length?"),
              ("L3", "Two trains of equal length, same direction, at 46 and 36 km/h; the faster passes the slower in 36 s.  Length of each?")]
ANSWERS_A = [("54 km/h = 15 m/s;     150 ÷ 15", "10 s"),
             ("90 km/h = 25 m/s;     600 ÷ 25", "24 s"),
             ("the extra 12 s covers 180 m:  15 m/s;     15 × 9", "135 m,  54 km/h"),
             ("108 km/h = 30 m/s;     300 ÷ 30", "10 s")]
ANSWERS_B = [("relative speed 60 km/h = 50/3 m/s;     200 ÷ 50/3", "12 s"),
             ("9(S − 2) = 10(S − 4):   S = 22 km/h;     9 × 20 × 5/18", "50 m,  22 km/h"),
             ("the man is a point:   18 km/h = 5 m/s;     5 × 20", "100 m"),
             ("10 km/h = 25/9 m/s;     25/9 × 36 = 100 m = both lengths", "50 m each")]
LENS = [("Recognition cue", "“crosses”, “passes”, “overtakes” with a train:  list every length involved and choose the relative speed"),
        ("Target time", "30 seconds;  40 seconds for two trains"),
        ("Sanity check", "a platform takes longer than a pole at the same speed;  overtaking takes longer than crossing head-on")]


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


class ProblemsOnTrainsVideo(LMSScene):
    lesson_title = "Problems on Trains"

    def construct(self):
        self.camera.background_color = BG

        self.intro()
        self.hook()
        self.objectives()
        self.why_this_matters()
        self.what_distance()
        self.men_units_two_crossings()
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

        crumb = self.breadcrumb("Quantitative Aptitude", "Lesson 19 · Time & Distance", "Video 4 of 7")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        recap = VGroup(text("last video", SMALL, MUTED), pill("watch the gap:  add or subtract the speeds", WORD, size=LABEL)).arrange(DOWN, buff=0.25)
        title = fit_width(text("Problems on Trains", TITLE, INK, BOLD), SAFE_W - 0.4)
        today = text("today: a train is not a point", LABEL, FOCUS)
        block = VGroup(recap, title, today).arrange(DOWN, buff=0.7)
        fit_within(block, SAFE_W, SAFE_H - crumb.height - 0.9)
        block.next_to(crumb, DOWN, buff=0.7)
        self.no_overlap(crumb, recap, title, today)
        self.validator.check_in_frame(VGroup(crumb, block))

        n = self.narrate(
            id="intro_01",
            text="In the last video, you watched the gap: add the speeds for opposite directions, subtract for the same "
                 "direction.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.at_word(n, "gap")
        self.play(FadeIn(recap, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="intro_02",
            text="Today: problems on trains, where one extra idea matters: a train is not a point.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "trains")
        self.play(FadeIn(title, shift=UP * 0.1))
        self.at_word(n, "point")
        self.play(FadeIn(today, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_intro")

    # ============================================== 1. HOOK ==========

    def hook(self):
        self.scene_start("S01_hook", title="Hook")

        head = self.heading("A metro station")
        drawing = VGroup(VGroup(Rectangle(width=2.4, height=0.4, color=WORD, fill_color=WORD, fill_opacity=0.5),
                                text("240 m train", SMALL, WORD, BOLD)).arrange(DOWN, buff=0.15),
                         VGroup(Rectangle(width=3.6, height=0.4, color=MUTED, fill_color=MUTED, fill_opacity=0.35),
                                text("360 m platform", SMALL, MUTED, BOLD)).arrange(DOWN, buff=0.15)).arrange(RIGHT, buff=0.9)
        train = pill("the train passes a signal pole in 12 seconds", WORD, size=LABEL)
        ask = pill("same speed:   how long to pass completely through the platform?", FOCUS, size=LABEL)
        quick = text("the quick answer:   360 m at 20 m/s  =  18 seconds", LABEL, BAD, BOLD)
        idea = text("it is wrong, for the one idea behind every train question:  a train is not a point", LABEL, INK, BOLD)
        fit_width(idea, SAFE_W - 0.6)
        self.stack(head, [drawing, train, ask, quick, idea], buff=0.5, top=0.6)
        self.no_overlap(*drawing)

        n = self.narrate(
            id="hook_01",
            text="A two hundred and forty metre metro train passes a signal pole in twelve seconds.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "train")
        self.play(FadeIn(drawing[0]), FadeIn(train, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_02",
            text="At the same speed, how long does it take to pass completely through a three hundred and sixty metre "
                 "station platform?",
            voice="default",
            subtitle=True,
            pause_after=3.0,
        )
        self.at_word(n, "completely")
        self.play(FadeIn(drawing[1]), FadeIn(ask, scale=1.03))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="hook_03",
            text="The quick answer is eighteen seconds, since three hundred and sixty metres at twenty metres per second "
                 "is eighteen seconds.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "quick")
        self.play(FadeIn(quick, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_04",
            text="It is wrong, and the reason is the one idea that makes every train question work: a train is not a "
                 "point.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "wrong")
        self.play(FadeIn(idea, shift=UP * 0.1))
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
            text="First, decide the distance a train must cover to cross a pole, a man, a platform or another train.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "decide")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "cross")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="objectives_03",
            text="Second, use relative speed for two trains, or for a train and a moving man.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "relative")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "moving")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="objectives_04",
            text="Third, find a train's length and speed from two crossing times.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "length")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "crossing")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_objectives")

    # ============================================== 3. WHY THIS MATTERS ==========

    def why_this_matters(self):
        self.scene_start("S03_why_this_matters", title="Why This Matters")

        head = self.heading("Why this matters")
        often = pill("one of the most frequent topics in aptitude papers", WORD, size=LABEL)
        mix = VGroup(pill("unit conversion", WORD, size=LABEL), pill("relative speed", WORD, size=LABEL),
                     pill("one extra idea:  length", FOCUS, size=LABEL)).arrange(RIGHT, buff=0.4)
        whole = text("it tests the whole lesson in a single question", LABEL, INK, BOLD)
        self.stack(head, [often, mix, whole], buff=0.9, top=1.1)
        self.no_overlap(*mix)

        n = self.narrate(
            id="why_this_matters_01",
            text="Problems on trains is one of the most frequent topics in aptitude papers.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "frequent")
        self.play(FadeIn(often, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="why_this_matters_02",
            text="It combines unit conversion, relative speed and one extra idea, length, so it tests the whole lesson in "
                 "a single question.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "conversion")
        self.play(FadeIn(mix[0], shift=UP * 0.1))
        self.at_word(n, "relative")
        self.play(FadeIn(mix[1], shift=UP * 0.1))
        self.at_word(n, "length")
        self.play(FadeIn(mix[2], shift=UP * 0.1))
        self.at_word(n, "whole")
        self.play(FadeIn(whole, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_why_this_matters")

    # ============================================== 4. CONCEPT - WHAT DISTANCE DOES THE TRAIN COVER ==========

    def what_distance(self):
        self.scene_start("S04_what_distance", title="Concept - What Distance Does the Train Cover")

        head = self.heading("What distance does the train cover?")
        conv = text("unless stated:  constant speeds, parallel tracks, lengths in metres", SMALL, MUTED)
        blocks = two_line_blocks(STEPS_A, WORD)
        self.stack(head, [conv] + list(blocks), buff=0.42, top=0.55, align=LEFT)

        n = self.narrate(
            id="what_distance_01",
            text="Unless stated otherwise, speeds are constant, tracks are parallel, and lengths are in metres.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "constant")
        self.play(FadeIn(conv, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="what_distance_02",
            text="Crossing means front in, back out: a crossing starts when the engine reaches the object and ends when "
                 "the last coach clears it.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "front")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "starts")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="what_distance_03",
            text="For a pole, a standing man or a signal post, the distance is the train's length. These objects have no "
                 "length worth counting.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "pole")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "worth")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="what_distance_04",
            text="For a platform, a bridge, a tunnel or another stationary train, the distance is the sum of the lengths.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "platform")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "sum")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="what_distance_05",
            text="For two moving trains, the distance is the sum of the lengths and the speed is the relative speed. Add "
                 "the speeds for opposite directions; subtract for the same direction.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "moving")
        self.play(FadeIn(blocks[3][0], shift=RIGHT * 0.2))
        self.at_word(n, "Add")
        self.play(FadeIn(blocks[3][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_what_distance")

    # ============================================== 5. CONCEPT - A MOVING MAN, UNITS, AND TWO CROSSINGS ==========

    def men_units_two_crossings(self):
        self.scene_start("S05_men_units_two_crossings", title="Concept - A Moving Man, Units, and Two Crossings")

        head = self.heading("A moving man, units, and two crossings")
        blocks = two_line_blocks(STEPS_B, WORD)
        self.stack(head, list(blocks), buff=0.75, top=1.0, align=LEFT)

        n = self.narrate(
            id="men_units_two_crossings_01",
            text="A moving man is a train of length zero: the distance is the train's length, and the speed is the "
                 "relative speed of train and man.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "zero")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "relative")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="men_units_two_crossings_02",
            text="Convert kilometres per hour to metres per second first. Lengths are in metres and times in seconds.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Convert")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "Lengths")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="men_units_two_crossings_03",
            text="Two crossings give length and speed. If a train crosses a pole in a short time and a platform in a "
                 "longer time, the extra time is spent covering the platform, so the speed is the platform length divided "
                 "by the extra time, and the length is the speed times the pole time.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "crossings")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "extra")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_men_units_two_crossings")

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
            text="Here is the formula box. The time to cross is the sum of the lengths involved, over the relative speed.",
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
            text="A pole or a standing man: L over S. A platform or a bridge: L plus P, over S.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "pole")
        self.play(FadeIn(lines[1], shift=RIGHT * 0.2))
        self.at_word(n, "platform")
        self.play(Indicate(lines[1], color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_box_03",
            text="Two trains: the sum of the lengths over the sum of the speeds in opposite directions, and over the "
                 "difference of the speeds in the same direction.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "trains")
        self.play(FadeIn(lines[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_box_04",
            text="And with a pole in a short time and a platform in a longer time: the speed is P over the extra time, and "
                 "the length is the speed times the pole time.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "extra")
        self.play(FadeIn(lines[3], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_formula_box")

    # ============================================== 7. THE ANALOGY - A TRUCK AT A TOLL BARRIER ==========

    def analogy(self):
        self.scene_start("S07_analogy", title="The Analogy - A Truck at a Toll Barrier")

        head = self.heading("A truck at a toll barrier")
        barrier = pill("the barrier stays up until the last bumper has passed, not just the cab", WORD, size=LABEL)
        longer = text("the longer the truck, the longer the barrier stays open, even at the same speed", LABEL, INK, BOLD)
        truck = pill("a train crossing anything is that truck:   its own length is part of the trip", FOCUS, size=LABEL)
        stops = VGroup(text("Where the analogy stops", LABEL, BAD, BOLD),
                       text("trucks slow down at tolls", LABEL, INK),
                       text("exam trains run at a constant speed throughout the crossing", LABEL, MUTED)).arrange(DOWN, buff=0.2)
        self.stack(head, [barrier, longer, truck, stops], buff=0.6, top=0.7)

        n = self.narrate(
            id="analogy_01",
            text="A toll barrier stays up until the last bumper of the truck has passed, not just the cab.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "barrier")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "bumper")
        self.play(FadeIn(barrier, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_02",
            text="The longer the truck, the longer the barrier stays open, even at the same speed.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "longer")
        self.play(FadeIn(longer, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_03",
            text="A train crossing anything is that truck: its own length is part of the trip.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "truck")
        self.play(FadeIn(truck, scale=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_04",
            text="Where the analogy stops: trucks slow down at tolls. Exam trains run at a constant speed throughout the "
                 "crossing.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "stops")
        self.play(FadeIn(stops[0], shift=UP * 0.1))
        self.at_word(n, "slow")
        self.play(FadeIn(stops[1], shift=UP * 0.1))
        self.at_word(n, "constant")
        self.play(FadeIn(stops[2], shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S07_analogy")

    # ============================================== 8. WORKED EXAMPLE - CLOSING THE HOOK ==========

    def hook_solved(self):
        self.scene_start("S08_hook_solved", title="Worked Example - Closing the Hook")

        head = self.heading("A 240 m train, a 360 m platform")
        steps = self.solve_steps([("Speed:    240 ÷ 12", "=  20 m/s"),
                                  ("To clear the platform:    240 + 360", "=  600 m"),
                                  ("Time:    600 ÷ 20", "=  30 seconds,  not 18")])
        self.stack(head, [steps], top=1.2)
        self.no_overlap(*steps)

        n = self.narrate(
            id="hook_solved_01",
            text="The speed is two hundred and forty divided by twelve: twenty metres per second.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "divided")
        self.play(FadeIn(steps[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "twenty")
        self.play(FadeIn(steps[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_solved_02",
            text="To clear the platform, the train covers two hundred and forty plus three hundred and sixty: six hundred "
                 "metres.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "plus")
        self.play(FadeIn(steps[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "six")
        self.play(FadeIn(steps[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_solved_03",
            text="Six hundred divided by twenty is thirty seconds, not eighteen.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "divided")
        self.play(FadeIn(steps[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "thirty")
        self.play(FadeIn(steps[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S08_hook_solved")

    # ============================================== 9. A SECOND WORKED EXAMPLE - TWO TRAINS, BOTH DIRECTIONS ==========

    def second_example(self):
        self.scene_start("S09_second_example", title="A Second Worked Example - Two Trains, Both Directions")

        head = self.heading("Two trains, both directions")
        ask = text("trains of 150 m and 200 m on parallel tracks at 54 and 72 km/h:   crossing time, opposite and same direction?", LABEL, MUTED)
        fit_width(ask, SAFE_W - 0.6)
        steps = self.solve_steps([("Total length:    150 + 200", "=  350 m"),
                                  ("Opposite:    54 + 72 = 126 km/h = 35 m/s;      350 ÷ 35", "=  10 s"),
                                  ("Same direction:    72 − 54 = 18 km/h = 5 m/s;      350 ÷ 5", "=  70 s")])
        self.stack(head, [ask, steps], buff=0.8, top=0.8)
        self.no_overlap(*steps)

        n = self.narrate(
            id="second_example_01",
            text="Trains of one hundred and fifty metres and two hundred metres run on parallel tracks at fifty-four and "
                 "seventy-two kilometres per hour. How long do they take to cross each other in opposite directions, and "
                 "in the same direction?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Trains")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "parallel")
        self.play(FadeIn(ask, shift=UP * 0.1))
        self.at_word(n, "opposite")
        self.play(Indicate(ask, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_02",
            text="The total length is three hundred and fifty metres.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "total")
        self.play(FadeIn(steps[0], scale=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_03",
            text="In opposite directions: fifty-four plus seventy-two is one hundred and twenty-six kilometres per hour, "
                 "thirty-five metres per second, so three hundred and fifty divided by thirty-five is ten seconds.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "plus")
        self.play(FadeIn(steps[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "ten")
        self.play(FadeIn(steps[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_04",
            text="In the same direction: seventy-two minus fifty-four is eighteen kilometres per hour, five metres per "
                 "second, so three hundred and fifty divided by five is seventy seconds.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "minus")
        self.play(FadeIn(steps[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "seventy")
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
            text="A pole: a one hundred and eighty metre train at fifty-four kilometres per hour. One hundred and eighty "
                 "divided by fifteen: twelve seconds.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "pole")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "divided")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_03",
            text="A platform: a two hundred metre train at seventy-two kilometres per hour, and a three hundred metre "
                 "platform. Five hundred divided by twenty: twenty-five seconds.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "platform")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "divided")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_04",
            text="Two trains in opposite directions: one hundred and twenty and one hundred and thirty metres, at forty "
                 "and fifty kilometres per hour. Two hundred and fifty divided by twenty-five: ten seconds.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "opposite")
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
            text="Two trains in the same direction: one hundred and one hundred and fifty metres, at sixty-eight and fifty "
                 "kilometres per hour. Two hundred and fifty divided by five: fifty seconds.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "same")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "divided")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_06",
            text="A moving man: a two hundred and twenty metre train at sixty kilometres per hour, and a man walking "
                 "towards it at six. Two hundred and twenty divided by sixty-six kilometres per hour in metres per second: "
                 "twelve seconds.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "man")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "divided")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_07",
            text="Length from two crossings: a pole in ten seconds and a one hundred and fifty metre platform in "
                 "twenty-five seconds. The speed is one hundred and fifty divided by fifteen, ten metres per second: the "
                 "length is one hundred metres.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "crossings")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "divided")
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
            text="Trap one: the train's own length forgotten. A two hundred and forty metre train at twenty metres per "
                 "second goes through a three hundred and sixty metre platform: what is the time?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "forgotten")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "train")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_02",
            text="The wrong instinct divides three hundred and sixty by twenty: eighteen seconds. The correct answer is "
                 "six hundred divided by twenty: thirty seconds.",
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
            text="The rule: for anything with length, add the train's length.",
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
            text="Trap two: kilometres per hour used with metres. A one hundred and eighty metre train at fifty-four "
                 "kilometres per hour passes a pole: what is the time?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "used")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "train")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_05",
            text="The wrong instinct divides one hundred and eighty by fifty-four: about three point three seconds. The "
                 "correct answer is one hundred and eighty divided by fifteen: twelve seconds.",
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
            text="The rule: convert to metres per second before dividing metres by speed.",
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
            text="Trap three: speeds added for trains moving the same way. Trains of one hundred and one hundred and fifty "
                 "metres run at sixty-eight and fifty kilometres per hour in the same direction: what is the time?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "added")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "run")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_08",
            text="The wrong instinct adds the speeds, and gets about seven point six seconds. The correct answer uses the "
                 "difference, eighteen kilometres per hour: fifty seconds.",
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
            text="The rule: overtaking is slow; it uses the difference of the speeds.",
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
        given = pill("a 300 m train at 90 km/h crosses a 200 m bridge:   how long does it take?", FOCUS, size=LABEL)
        work = VGroup(text("90 × 5/18  =  25 m/s", BODY, INK, BOLD), text("(300 + 200) ÷ 25  =  20 seconds", BODY, GOOD, BOLD)).arrange(RIGHT, buff=0.8)
        self.stack(head, [given, work], buff=1.0, top=1.0)
        self.no_overlap(*work)

        n = self.narrate(
            id="checkpoint_01",
            text="Your turn. A three hundred metre train at ninety kilometres per hour crosses a two hundred metre bridge. "
                 "How long does it take?",
            voice="default",
            subtitle=True,
            pause_after=10.0,
        )
        self.at_word(n, "turn")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "train")
        self.play(FadeIn(given, scale=1.03))
        self.at_word(n, "long")
        self.play(Indicate(given, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="checkpoint_02",
            text="Ninety kilometres per hour is twenty-five metres per second, and five hundred divided by twenty-five is "
                 "twenty seconds.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "twenty-five")
        self.play(FadeIn(work[0], shift=UP * 0.1))
        self.at_word(n, "divided")
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
            text="Level one, question one: a one hundred and fifty metre train runs at fifty-four kilometres per hour; how "
                 "long does it take to pass a pole? Question two: a two hundred and fifty metre train at ninety kilometres "
                 "per hour crosses a three hundred and fifty metre platform; find the time.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "pole")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "platform")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="practice_02",
            text="Level two, question three: a train passes a pole in nine seconds and a one hundred and eighty metre "
                 "platform in twenty-one seconds; find its length and its speed in kilometres per hour. Question four: "
                 "trains of one hundred and forty and one hundred and sixty metres run in opposite directions at fifty and "
                 "fifty-eight kilometres per hour; how long do they take to cross each other? Question five: a two hundred "
                 "metre train at sixty-three kilometres per hour overtakes a man walking at three kilometres per hour in "
                 "the same direction; how long does it take to pass him?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "passes")
        self.play(FadeIn(rows[2], shift=RIGHT * 0.2))
        self.at_word(n, "opposite")
        self.play(FadeIn(rows[3], shift=RIGHT * 0.2))
        self.at_word(n, "overtakes")
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
            text="Level three, question six: a train passes two men walking in the same direction as the train, at two and "
                 "four kilometres per hour, in nine seconds and ten seconds; find the train's length and speed. Question "
                 "seven: two trains run in the same direction at sixty and forty-two kilometres per hour; a man sitting in "
                 "the slower train sees the faster train pass him completely in twenty seconds; find the length of the "
                 "faster train. Question eight: two trains of equal length run in the same direction on parallel tracks at "
                 "forty-six and thirty-six kilometres per hour; the faster passes the slower completely in thirty-six "
                 "seconds; find the length of each train.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "men")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "sitting")
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
            text="One: fifty-four kilometres per hour is fifteen metres per second, and one hundred and fifty divided by "
                 "fifteen is ten seconds.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "divided")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "ten")
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_02",
            text="Two: ninety kilometres per hour is twenty-five metres per second, and six hundred divided by twenty-five "
                 "is twenty-four seconds.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "divided")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "twenty-four")
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_03",
            text="Three: the extra twelve seconds covers one hundred and eighty metres, so the speed is fifteen metres per "
                 "second, fifty-four kilometres per hour, and the length is fifteen times nine: one hundred and "
                 "thirty-five metres.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "extra")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "length")
        self.play(FadeIn(rows[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_04",
            text="Four: one hundred and eight kilometres per hour is thirty metres per second, and three hundred divided "
                 "by thirty is ten seconds.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "divided")
        self.play(FadeIn(rows[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "ten")
        self.play(FadeIn(rows[3][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Answer key  ·  5 to 8", GOOD)
        table, rows = self.answer_table(head, ANSWERS_B, 5)

        n = self.narrate(
            id="answers_05",
            text="Five: the relative speed is sixty kilometres per hour, fifty thirds of a metre per second, and two "
                 "hundred divided by that is twelve seconds.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "relative")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "twelve")
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_06",
            text="Six: nine times S minus two equals ten times S minus four, so S is twenty-two kilometres per hour, and "
                 "the length is nine seconds at twenty kilometres per hour: fifty metres.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "equals")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "fifty")
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_07",
            text="Seven: the man is a point in the slower train. The relative speed is eighteen kilometres per hour, five "
                 "metres per second, so the length is five times twenty: one hundred metres.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "point")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "length")
        self.play(FadeIn(rows[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_08",
            text="Eight: the relative speed is ten kilometres per hour, twenty-five ninths of a metre per second. In "
                 "thirty-six seconds that is one hundred metres, both lengths together, so each train is fifty metres.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "relative")
        self.play(FadeIn(rows[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "each")
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
            text="Recognise and move. The recognition cue: crosses, passes or overtakes, with a train; list every length "
                 "involved and choose the relative speed.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "cue")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "list")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_lens_02",
            text="The target time: thirty seconds, or forty seconds for two trains.",
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
            text="The sanity check: crossing a platform must take longer than crossing a pole at the same speed, and "
                 "overtaking must take longer than crossing head-on.",
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
        own = pill("a train covers its own length, plus the length of whatever it crosses", GOOD, size=LABEL)
        tools = VGroup(pill("the other object moves:  relative speed", WORD, size=SMALL), pill("convert km/h to m/s first", WORD, size=SMALL),
                       pill("two crossing times give length and speed", WORD, size=SMALL)).arrange(RIGHT, buff=0.3)
        fit_width(tools, SAFE_W - 0.4)
        toll = text("the toll barrier: up until the last bumper is through", LABEL, MUTED)
        box = text("time = (sum of lengths)/relative speed         pole:  L/S         S = P/(T − t),   L = S × t", LABEL, GOOD, BOLD)
        fit_width(box, SAFE_W - 0.6)
        nxt = self.breadcrumb("Next", "Video 5 · Boats & Streams")
        self.stack(head, [own, tools, toll, box, nxt], buff=0.6, top=0.7)
        self.no_overlap(*tools)

        n = self.narrate(
            id="summary_01",
            text="A train crossing anything covers its own length plus the length of whatever it crosses.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "own")
        self.play(FadeIn(own, scale=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_02",
            text="Use the relative speed when the other object moves, convert kilometres per hour to metres per second "
                 "first, and get the length and speed from two crossing times when they are not given.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "relative")
        self.play(FadeIn(tools[0], shift=UP * 0.1))
        self.at_word(n, "convert")
        self.play(FadeIn(tools[1], shift=UP * 0.1))
        self.at_word(n, "crossing")
        self.play(FadeIn(tools[2], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_03",
            text="Remember the toll barrier, and the formula box.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "toll")
        self.play(FadeIn(toll, shift=UP * 0.1))
        self.at_word(n, "box")
        self.play(FadeIn(box, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_04",
            text="Next: boats and streams.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Next")
        self.play(FadeIn(nxt, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S16_summary")

"""
animation.py for the LMS video generator.

Course : Pre-C-CAT - Section A - Quantitative Aptitude
Video  : Lesson 19 - Time & Distance - 05 - Boats & Streams

Source script:
  C:\\Scripts\\Section A\\Aptitude\\Sessions 13-18 - Pipes, Time Distance, Partnership\\Lesson 19 - Time & Distance\\05 - Boats & Streams.pdf

Built on the golden-reference pattern:
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``;
  * layouts stacked with next_to and guarded with ``no_overlap``; nothing is
    ever animated onto or into another box.

Lesson 19, Video 5 of 7. Not the first video of the lesson: a silent breadcrumb, a one-line recap of Video 4, then today's topic. No spoken course welcome.
The narration follows the script section by section. The seven concept steps are split over two screens. The six exam patterns are shown as two-line blocks.
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


def still_and_stream(down, up):
    """u = (D + U)/2,  v = (D − U)/2."""
    return Fraction(down + up, 2), Fraction(down - up, 2)


def round_trip(u, v, d):
    return Fraction(d, u + v) + Fraction(d, u - v)


# ---- the hook: 24 km down in 2 h, back up in 3 h ----
HOOK_D, HOOK_U = Fraction(24, 2), Fraction(24, 3)
assert (HOOK_D, HOOK_U) == (12, 8) and still_and_stream(HOOK_D, HOOK_U) == (10, 2)

# ---- second worked example: u = 15, v = 3, 36 km each way ----
TRIP = round_trip(15, 3, 36)
assert (15 + 3, 15 - 3, TRIP) == (18, 12, 5) and Fraction(72, TRIP) == Fraction(72, 5) == Fraction(18 * 12, 15) and float(Fraction(72, 5)) == 14.4

# ---- exam patterns, traps, checkpoint, practice (answers computed) ----
assert (12 + 4, 12 - 4) == (16, 8) and still_and_stream(18, 10) == (14, 4) and still_and_stream(Fraction(32, 2), Fraction(24, 3)) == (12, 4)
assert round_trip(10, 2, 48) == 10 and Fraction(2 + 1, 2 - 1) == 3 and round_trip(9, 3, 24) == 6
assert still_and_stream(20, 14) == (17, 3) and (8 + 2, 8 - 2) == (10, 6) and still_and_stream(21, 15) == (18, 3)
assert still_and_stream(Fraction(40, 4), Fraction(24, 4)) == (8, 2) and round_trip(6, 2, 16) == 6
assert Fraction(3 + 1, 3 - 1) == 2 and 16 // 2 == 8 and (16 + 8, 16 - 8) == (24, 8) and round_trip(10, 2, 24) == 5
assert Fraction(24, 8) + Fraction(36, 12) == 6 and Fraction(36, 8) + Fraction(24, 12) == Fraction(13, 2) and still_and_stream(12, 8) == (10, 2)
assert Fraction(2 * 16 * 8, 16 + 8) == Fraction(32, 3) == 10 + Fraction(2, 3)

OBJECTIVES = [("Write the downstream and upstream speeds", "from the still-water and stream speeds"),
              ("Recover the still-water and stream speeds", "from the downstream and upstream speeds"),
              ("Solve round-trip questions", "and “same distance up and down” questions")]
STEPS_A = [("Two speeds:  u = the boat in still water,   v = the stream", "we assume u > v, and both are constant"),
           ("Downstream (with the current):   D = u + v", "the current helps"),
           ("Upstream (against the current):   U = u − v", "the current opposes"),
           ("Reverse it:   u = (D + U)/2,    v = (D − U)/2", "still-water speed = the average;    stream speed = half the difference")]
STEPS_B = [("Round trip over the same distance d", "time = d/(u + v) + d/(u − v)"),
           ("Average speed of a round trip   (Lesson 17 recap)", "equal distances at D and U:    2DU/(D + U) = (u + v)(u − v)/u,    always below u"),
           ("Same distance up and down in given times", "speeds are inverse to times:  upstream k times as long gives D : U = k : 1,  so u : v = (k + 1) : (k − 1)")]
FORMULAS = ["Downstream   D = u + v                    Upstream   U = u − v",
            "u  =  (D + U)/2                    v  =  (D − U)/2",
            "Round trip over d:      d/(u + v) + d/(u − v)",
            "Upstream takes k times as long:      u : v  =  (k + 1) : (k − 1)"]
PATTERNS = [("Down and up speeds", "u = 12,  v = 4", "u + v,   u − v", "16 and 8 km/h"),
            ("From D and U", "D = 18,  U = 10", "half-sum,  half-difference", "u = 14,  v = 4 km/h"),
            ("From distances and times", "32 km down in 2 h;   24 km up in 3 h", "D = 16,  U = 8", "u = 12,  v = 4 km/h"),
            ("Round-trip time", "u = 10,  v = 2;   48 km each way", "48/12 + 48/8", "10 h"),
            ("Upstream takes twice as long", "k = 2", "u : v = 3 : 1", "u = 3v"),
            ("Distance from round-trip time", "u = 9,  v = 3;   round trip 6 h", "d/12 + d/6 = 6", "24 km each way")]
TRAPS = [("Trap 1  ·  the stream speed not halved", "D = 12 km/h, U = 8 km/h.  Stream speed?",
          "12 − 8  =  4 km/h", "(12 − 8)/2  =  2 km/h",
          "The gap between D and U contains the stream speed twice."),
         ("Trap 2  ·  the still-water speed used as the round-trip average",
          "u = 15, v = 3; the same distance down and back.  Average speed?",
          "15 km/h", "(18 × 12)/15  =  14.4 km/h",
          "The boat spends longer going upstream, so the average is below u."),
         ("Trap 3  ·  “twice as long” read as u = 2v", "Upstream takes twice as long as downstream.  u : v?",
          "2 : 1", "D : U = 2 : 1,  so u : v = 3 : 1",
          "The time ratio gives D : U; then take the half-sum and half-difference.")]
PRACTICE_A = [("L1", "A boat's speed in still water is 8 km/h and the stream flows at 2 km/h.  Find its downstream and upstream speeds."),
              ("L1", "A boat goes downstream at 21 km/h and upstream at 15 km/h.  Find u and v."),
              ("L2", "A boat goes 40 km downstream in 4 hours and 24 km upstream in 4 hours.  Find u and v."),
              ("L2", "A man rows at 6 km/h in still water; the stream flows at 2 km/h.  Time to row 16 km downstream and back?"),
              ("L2", "Upstream takes 3 times as long as the same distance downstream.  Still-water speed 16 km/h.  Stream speed?")]
PRACTICE_B = [("L3", "Still-water speed 10 km/h.  The boat goes 24 km downstream and returns in 5 hours in all.  Find the stream speed."),
              ("L3", "24 km up and 36 km down take 6 h;    36 km up and 24 km down take 6 1/2 h.    Find u and v."),
              ("L3", "Still-water speed 12 km/h, stream 4 km/h; downstream and back over the same distance.  Average speed?")]
ANSWERS_A = [("8 + 2   and   8 − 2", "10 and 6 km/h"),
             ("(21 + 15)/2   and   (21 − 15)/2", "u = 18,  v = 3 km/h"),
             ("D = 10,   U = 6", "u = 8,  v = 2 km/h"),
             ("16/8 + 16/4  =  2 + 4", "6 hours")]
ANSWERS_B = [("D : U = 3 : 1,  so u : v = 4 : 2 = 2 : 1       (D = 24, U = 8)", "v = 8 km/h"),
             ("24/(10 + v) + 24/(10 − v) = 5;   480/(100 − v²) = 5;   v² = 4", "v = 2 km/h"),
             ("x = 1/U, y = 1/D:   x + y = 5/24,  x − y = 1/24;   U = 8, D = 12", "u = 10,  v = 2 km/h"),
             ("D = 16,  U = 8;     2 × 16 × 8/24  =  32/3", "10 2/3 km/h")]
LENS = [("Recognition cue", "“downstream”, “upstream”, “still water”, “current”, “stream”:  write D and U first"),
        ("Target time", "30 seconds;  50 seconds for two-trip equations"),
        ("Sanity check", "U < u < D,  and v is less than u")]


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


class BoatsAndStreamsVideo(LMSScene):
    lesson_title = "Boats & Streams"

    def construct(self):
        self.camera.background_color = BG

        self.intro()
        self.hook()
        self.objectives()
        self.why_this_matters()
        self.two_speeds()
        self.round_trips()
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

        crumb = self.breadcrumb("Quantitative Aptitude", "Lesson 19 · Time & Distance", "Video 5 of 7")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        recap = VGroup(text("last video", SMALL, MUTED), pill("a train covers its own length too", WORD, size=LABEL)).arrange(DOWN, buff=0.25)
        title = fit_width(text("Boats & Streams", TITLE, INK, BOLD), SAFE_W - 0.4)
        today = text("today: relative speed, with the current as helper and opponent", LABEL, FOCUS)
        block = VGroup(recap, title, today).arrange(DOWN, buff=0.7)
        fit_within(block, SAFE_W, SAFE_H - crumb.height - 0.9)
        block.next_to(crumb, DOWN, buff=0.7)
        self.no_overlap(crumb, recap, title, today)
        self.validator.check_in_frame(VGroup(crumb, block))

        n = self.narrate(
            id="intro_01",
            text="In the last video, a train covered its own length as well as whatever it crossed.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.at_word(n, "length")
        self.play(FadeIn(recap, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="intro_02",
            text="Today: boats and streams, relative speed with the current as a helper one way and an opponent the other.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "boats")
        self.play(FadeIn(title, shift=UP * 0.1))
        self.at_word(n, "current")
        self.play(FadeIn(today, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_intro")

    # ============================================== 1. HOOK ==========

    def hook(self):
        self.scene_start("S01_hook", title="Hook")

        head = self.heading("An inspection boat")
        log = VGroup(pill("24 km downstream:  2 h", WORD, size=BODY), pill("24 km back upstream:  3 h", WORD, size=BODY)).arrange(RIGHT, buff=0.6)
        ask = VGroup(pill("boat speed in still water?", FOCUS, size=LABEL), pill("speed of the current?", FOCUS, size=LABEL)).arrange(RIGHT, buff=0.5)
        promise = text("two trips, two speeds: a one-line average gives both answers", LABEL, INK, BOLD)
        self.stack(head, [log, ask, promise], buff=0.9, top=1.0)
        self.no_overlap(*log)
        self.no_overlap(*ask)

        n = self.narrate(
            id="hook_01",
            text="An inspection boat checks sensor buoys along a river pipeline. It covers twenty-four kilometres "
                 "downstream in two hours and returns the same twenty-four kilometres upstream in three hours.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "boat")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "downstream")
        self.play(FadeIn(log[0], shift=UP * 0.1))
        self.at_word(n, "upstream")
        self.play(FadeIn(log[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_02",
            text="How fast is the boat in still water, and how fast is the current?",
            voice="default",
            subtitle=True,
            pause_after=3.0,
        )
        self.at_word(n, "still")
        self.play(FadeIn(ask[0], scale=1.03))
        self.at_word(n, "current")
        self.play(FadeIn(ask[1], scale=1.03))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="hook_03",
            text="Two trips, two speeds, and a one-line average gives both answers.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "average")
        self.play(FadeIn(promise, shift=UP * 0.1))
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
            text="First, write the downstream and upstream speeds from the still-water and stream speeds.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "write")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "from")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="objectives_03",
            text="Second, recover the still-water and stream speeds from the downstream and upstream speeds.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "recover")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "from")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="objectives_04",
            text="Third, solve round-trip questions, and same distance up and down questions.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "round-trip")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "same")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_objectives")

    # ============================================== 3. WHY THIS MATTERS ==========

    def why_this_matters(self):
        self.scene_start("S03_why_this_matters", title="Why This Matters")

        head = self.heading("Why this matters")
        rel = pill("relative speed with a fixed helper and a fixed opponent:   the current", WORD, size=LABEL)
        often = text("it appears regularly in aptitude papers", LABEL, INK)
        two = pill("almost every question reduces to two numbers:   D and U", FOCUS, size=LABEL)
        self.stack(head, [rel, often, two], buff=0.9, top=1.1)

        n = self.narrate(
            id="why_this_matters_01",
            text="Boats and streams is relative speed with a fixed helper and a fixed opponent: the current.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "current")
        self.play(FadeIn(rel, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="why_this_matters_02",
            text="It appears regularly in aptitude papers, and almost every question reduces to two numbers, the "
                 "downstream and upstream speeds.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "regularly")
        self.play(FadeIn(often, shift=UP * 0.1))
        self.at_word(n, "two")
        self.play(FadeIn(two, scale=1.03))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_why_this_matters")

    # ============================================== 4. CONCEPT - TWO SPEEDS, DOWN AND UP ==========

    def two_speeds(self):
        self.scene_start("S04_two_speeds", title="Concept - Two Speeds, Down and Up")

        head = self.heading("Two speeds, down and up")
        blocks = two_line_blocks(STEPS_A, WORD)
        self.stack(head, list(blocks), buff=0.5, top=0.7, align=LEFT)

        n = self.narrate(
            id="two_speeds_01",
            text="There are two speeds: u is the boat's speed in still water, and v is the speed of the stream. We assume "
                 "u is bigger than v, and both are constant.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "still")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "assume")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="two_speeds_02",
            text="Downstream, with the current, the speed is u plus v.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Downstream")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "plus")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="two_speeds_03",
            text="Upstream, against the current, the speed is u minus v.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Upstream")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "minus")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="two_speeds_04",
            text="Reverse it: u is D plus U over two, and v is D minus U over two. The still-water speed is the average, "
                 "and the stream speed is half the difference.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Reverse")
        self.play(FadeIn(blocks[3][0], shift=RIGHT * 0.2))
        self.at_word(n, "average")
        self.play(FadeIn(blocks[3][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_two_speeds")

    # ============================================== 5. CONCEPT - ROUND TRIPS AND TIME RATIOS ==========

    def round_trips(self):
        self.scene_start("S05_round_trips", title="Concept - Round Trips and Time Ratios")

        head = self.heading("Round trips and time ratios")
        blocks = two_line_blocks(STEPS_B, WORD)
        self.stack(head, list(blocks), buff=0.75, top=1.0, align=LEFT)

        n = self.narrate(
            id="round_trips_01",
            text="For a round trip over the same distance d, the time is d over u plus v, plus d over u minus v.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "round")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "over")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="round_trips_02",
            text="The average speed of a round trip, a recap from lesson seventeen: equal distances at D and U give two D "
                 "U over D plus U, which is u plus v, times u minus v, over u, and is always below u.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "average")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "give")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="round_trips_03",
            text="For the same distance up and down in given times, the speeds are in the inverse ratio of the times. If "
                 "upstream takes k times as long as downstream, D to U is k to one, so u to v is k plus one, to k minus "
                 "one.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "same")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "inverse")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_round_trips")

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
            text="Here is the formula box. Downstream, D is u plus v; upstream, U is u minus v.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "box")
        self.play(FadeIn(box[0]))
        self.at_word(n, "plus")
        self.play(FadeIn(lines[0], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_box_02",
            text="In reverse, u is D plus U over two, and v is D minus U over two.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "reverse")
        self.play(FadeIn(lines[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_box_03",
            text="A round trip over a distance d takes d over u plus v, plus d over u minus v.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "round")
        self.play(FadeIn(lines[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="formula_box_04",
            text="And if upstream takes k times as long, u to v is k plus one, to k minus one.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "times")
        self.play(FadeIn(lines[3], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_formula_box")

    # ============================================== 7. THE ANALOGY - A MOVING WALKWAY ==========

    def analogy(self):
        self.scene_start("S07_analogy", title="The Analogy - A Moving Walkway")

        head = self.heading("A moving walkway")
        along = pill("walk along it:   your walking speed plus the walkway's", GOOD, size=LABEL)
        against = pill("walk against it:   the walkway subtracts", BAD, size=LABEL)
        same = text("your walking speed is u, the walkway is v:  the river works the same way", LABEL, INK, BOLD)
        stops = VGroup(text("Where the analogy stops", LABEL, BAD, BOLD),
                       text("a walkway moves at the same speed everywhere", LABEL, INK),
                       text("real rivers run faster in the middle;  exam questions assume one constant stream speed", LABEL, MUTED)).arrange(DOWN, buff=0.2)
        self.stack(head, [along, against, same, stops], buff=0.6, top=0.7)

        n = self.narrate(
            id="analogy_01",
            text="Walk along an airport moving walkway and your speed is your walking speed plus the walkway's.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "walkway")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "plus")
        self.play(FadeIn(along, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_02",
            text="Walk against it and the walkway subtracts.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "against")
        self.play(FadeIn(against, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_03",
            text="Your walking speed is u, the walkway is v, and the river works the same way.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "river")
        self.play(FadeIn(same, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_04",
            text="Where the analogy stops: a walkway moves at the same speed everywhere. Real rivers run faster in the "
                 "middle than near the banks; exam questions assume one constant stream speed.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "stops")
        self.play(FadeIn(stops[0], shift=UP * 0.1))
        self.at_word(n, "everywhere")
        self.play(FadeIn(stops[1], shift=UP * 0.1))
        self.at_word(n, "rivers")
        self.play(FadeIn(stops[2], shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S07_analogy")

    # ============================================== 8. WORKED EXAMPLE - CLOSING THE HOOK ==========

    def hook_solved(self):
        self.scene_start("S08_hook_solved", title="Worked Example - Closing the Hook")

        head = self.heading("24 km down in 2 h, back up in 3 h")
        steps = self.solve_steps([("Downstream:    D = 24 ÷ 2", "=  12 km/h"),
                                  ("Upstream:    U = 24 ÷ 3", "=  8 km/h"),
                                  ("Still water:    u = (12 + 8)/2", "=  10 km/h"),
                                  ("Current:    v = (12 − 8)/2", "=  2 km/h")])
        self.stack(head, [steps], top=1.0)
        self.no_overlap(*steps)

        n = self.narrate(
            id="hook_solved_01",
            text="Downstream, D is twenty-four divided by two, twelve kilometres per hour; upstream, U is twenty-four "
                 "divided by three, eight kilometres per hour.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "Downstream")
        self.play(FadeIn(steps[0], shift=RIGHT * 0.2))
        self.at_word(n, "upstream")
        self.play(FadeIn(steps[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_solved_02",
            text="In still water, u is twelve plus eight, over two: ten kilometres per hour.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "plus")
        self.play(FadeIn(steps[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "ten")
        self.play(FadeIn(steps[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_solved_03",
            text="The current, v, is twelve minus eight, over two: two kilometres per hour.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "minus")
        self.play(FadeIn(steps[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "kilometres")
        self.play(FadeIn(steps[3][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S08_hook_solved")

    # ============================================== 9. A SECOND WORKED EXAMPLE - A ROUND TRIP ==========

    def second_example(self):
        self.scene_start("S09_second_example", title="A Second Worked Example - A Round Trip")

        head = self.heading("A round trip")
        ask = text("still water 15 km/h, stream 3 km/h; 36 km downstream and back:   total time and average speed?", LABEL, MUTED)
        fit_width(ask, SAFE_W - 0.6)
        steps = self.solve_steps([("D = 15 + 3 = 18 km/h", "U = 15 − 3 = 12 km/h"),
                                  ("Time:    36/18 + 36/12  =  2 + 3", "=  5 hours"),
                                  ("Average speed:    72 ÷ 5", "=  14.4 km/h,  below 15"),
                                  ("Check:    (18 × 12)/15", "=  14.4")])
        self.stack(head, [ask, steps], buff=0.7, top=0.7)
        self.no_overlap(*steps)

        n = self.narrate(
            id="second_example_01",
            text="A boat's speed in still water is fifteen kilometres per hour and the stream flows at three kilometres "
                 "per hour. The boat goes thirty-six kilometres downstream and returns. Find the total time and the "
                 "average speed.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "still")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "returns")
        self.play(FadeIn(ask, shift=UP * 0.1))
        self.at_word(n, "Find")
        self.play(Indicate(ask, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_02",
            text="Downstream, D is eighteen kilometres per hour; upstream, U is twelve.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "eighteen")
        self.play(FadeIn(steps[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "twelve")
        self.play(FadeIn(steps[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_03",
            text="The time is thirty-six over eighteen plus thirty-six over twelve, two plus three: five hours.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "over")
        self.play(FadeIn(steps[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "five")
        self.play(FadeIn(steps[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_04",
            text="The average speed is seventy-two divided by five: fourteen point four kilometres per hour, below the "
                 "still-water speed of fifteen.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "divided")
        self.play(FadeIn(steps[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "fourteen")
        self.play(FadeIn(steps[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_05",
            text="Check: eighteen times twelve, over fifteen, is fourteen point four.",
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
            text="Down and up speeds: u is twelve and v is four. U plus v and u minus v: sixteen and eight kilometres per "
                 "hour.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "speeds")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "plus")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_03",
            text="From D and U: D is eighteen and U is ten. The half-sum and the half-difference: u is fourteen and v is "
                 "four.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "eighteen")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "half-sum")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_04",
            text="From distances and times: thirty-two kilometres down in two hours, and twenty-four up in three. D is "
                 "sixteen and U is eight, so u is twelve and v is four.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "distances")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "sixteen")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Exam patterns  ·  4 to 6 of 6")
        blocks = self.pattern_blocks(PATTERNS[3:6])
        self.stack(head, list(blocks), buff=0.6, top=0.8, align=LEFT)

        n = self.narrate(
            id="exam_patterns_05",
            text="Round-trip time: u is ten, v is two, and forty-eight kilometres each way. Forty-eight over twelve plus "
                 "forty-eight over eight: ten hours.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "time")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "over")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_06",
            text="Upstream takes twice as long: k is two. So u to v is three to one, and u is three times v.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "twice")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "three")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_07",
            text="Distance from the round-trip time: u is nine, v is three, and the round trip takes six hours. D over "
                 "twelve plus d over six is six: twenty-four kilometres each way.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Distance")
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
            text="Trap one: the stream speed not halved. D is twelve kilometres per hour and U is eight: what is the "
                 "stream speed?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "halved")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "twelve")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_02",
            text="The wrong instinct says twelve minus eight, four kilometres per hour. The correct answer is twelve minus "
                 "eight, over two: two kilometres per hour.",
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
            text="The rule: the gap between D and U contains the stream speed twice.",
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
            text="Trap two: the still-water speed used as the round-trip average. U is fifteen, v is three, and the boat "
                 "covers the same distance down and back: what is the average speed?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "used")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "fifteen")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_05",
            text="The wrong instinct says fifteen kilometres per hour, because the current helps and hurts equally. The "
                 "correct answer is fourteen point four kilometres per hour.",
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
            text="The rule: the boat spends longer going upstream, so the average is below u.",
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
            text="Trap three: twice as long, read as u equals two v. Upstream takes twice as long as downstream: what is u "
                 "to v?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "read")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "Upstream")
        self.play(FadeIn(q, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_08",
            text="The wrong instinct says two to one. The correct answer: D to U is two to one, so u to v is three to one.",
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
            text="The rule: the time ratio gives D to U; then take the half-sum and the half-difference.",
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
        given = pill("a boat goes downstream at 20 km/h and upstream at 14 km/h:   find u and v", FOCUS, size=LABEL)
        work = VGroup(text("u  =  (20 + 14)/2  =  17 km/h", BODY, GOOD, BOLD), text("v  =  (20 − 14)/2  =  3 km/h", BODY, GOOD, BOLD)).arrange(RIGHT, buff=0.9)
        self.stack(head, [given, work], buff=1.0, top=1.0)
        self.no_overlap(*work)

        n = self.narrate(
            id="checkpoint_01",
            text="Your turn. A boat goes downstream at twenty kilometres per hour and upstream at fourteen kilometres per "
                 "hour. Find u and v.",
            voice="default",
            subtitle=True,
            pause_after=10.0,
        )
        self.at_word(n, "turn")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "boat")
        self.play(FadeIn(given, scale=1.03))
        self.at_word(n, "Find")
        self.play(Indicate(given, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="checkpoint_02",
            text="U is the half-sum, seventeen kilometres per hour, and v is the half-difference, three kilometres per "
                 "hour.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "half-sum")
        self.play(FadeIn(work[0], shift=UP * 0.1))
        self.at_word(n, "half-difference")
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
            text="Level one, question one: a boat's speed in still water is eight kilometres per hour and the stream flows "
                 "at two kilometres per hour; find its downstream and upstream speeds. Question two: a boat goes "
                 "downstream at twenty-one kilometres per hour and upstream at fifteen; find u and v.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "still")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "twenty-one")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="practice_02",
            text="Level two, question three: a boat goes forty kilometres downstream in four hours and twenty-four "
                 "kilometres upstream in four hours; find u and v. Question four: a man rows at six kilometres per hour in "
                 "still water, and the stream flows at two; how long does he take to row sixteen kilometres downstream and "
                 "back? Question five: a boat takes three times as long to go upstream as to cover the same distance "
                 "downstream, and its still-water speed is sixteen kilometres per hour; find the stream speed.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "forty")
        self.play(FadeIn(rows[2], shift=RIGHT * 0.2))
        self.at_word(n, "rows")
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
            text="Level three, question six: a boat's still-water speed is ten kilometres per hour; it goes twenty-four "
                 "kilometres downstream and returns in five hours in all; find the stream speed. Question seven: a boat "
                 "covers twenty-four kilometres upstream and thirty-six downstream in six hours, and thirty-six upstream "
                 "and twenty-four downstream in six and a half hours; find u and v. Question eight: a boat with a "
                 "still-water speed of twelve kilometres per hour goes downstream and returns over the same distance, and "
                 "the stream flows at four kilometres per hour; find the average speed for the round trip.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "returns")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "covers")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.at_word(n, "average")
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
            text="One: eight plus two and eight minus two: ten kilometres per hour downstream, six upstream.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "plus")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "ten")
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_02",
            text="Two: the half-sum and half-difference of twenty-one and fifteen: u is eighteen and v is three.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "half-sum")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "eighteen")
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_03",
            text="Three: D is ten and U is six, so u is eight and v is two.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "ten")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "eight")
        self.play(FadeIn(rows[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_04",
            text="Four: sixteen over eight plus sixteen over four is two plus four: six hours.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "over")
        self.play(FadeIn(rows[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "six")
        self.play(FadeIn(rows[3][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Answer key  ·  5 to 8", GOOD)
        table, rows = self.answer_table(head, ANSWERS_B, 5)

        n = self.narrate(
            id="answers_05",
            text="Five: D to U is three to one, so u to v is four to two, two to one, and v is eight kilometres per hour. "
                 "Check: D is twenty-four and U is eight.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "three")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "eight")
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.at_word(n, "Check")
        self.play(Indicate(rows[0][1], color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_06",
            text="Six: twenty-four over ten plus v, plus twenty-four over ten minus v, is five; so four hundred and eighty "
                 "over one hundred minus v squared is five, v squared is four, and v is two kilometres per hour.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "over")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "two")
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_07",
            text="Seven: with x as one over U and y as one over D, adding the two equations gives x plus y as five "
                 "twenty-fourths, and subtracting gives x minus y as one twenty-fourth. So U is eight and D is twelve: u "
                 "is ten and v is two.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "adding")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "ten")
        self.play(FadeIn(rows[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_08",
            text="Eight: D is sixteen and U is eight, so the average is two times sixteen times eight, over twenty-four: "
                 "ten and two thirds kilometres per hour.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "sixteen")
        self.play(FadeIn(rows[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "thirds")
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
            text="Recognise and move. The recognition cue: downstream, upstream, still water, current or stream; write D "
                 "and U first.",
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
            text="The target time: thirty seconds, or fifty seconds for two-trip equations.",
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
            text="The sanity check: U is less than u, which is less than D, and v is less than u.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "sanity")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "less")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S15_exam_lens")

    # ============================================== 16. QUICK REVISION AND SUMMARY ==========

    def summary(self):
        self.scene_start("S16_summary", title="Quick Revision and Summary")

        head = self.heading("Quick revision")
        dirs = VGroup(pill("downstream:  u + v", WORD, size=LABEL), pill("upstream:  u − v", WORD, size=LABEL)).arrange(RIGHT, buff=0.5)
        rev = VGroup(pill("u = the average of D and U", RATIO, size=LABEL), pill("v = half their difference", RATIO, size=LABEL)).arrange(RIGHT, buff=0.5)
        trip = text("round trips take longer than in still water:  their average speed is below u", LABEL, INK, BOLD)
        walk = text("the moving walkway: with it you add, against it you subtract", LABEL, MUTED)
        box = pill("upstream k times as long:    u : v = (k + 1) : (k − 1)", GOOD, size=LABEL)
        nxt = self.breadcrumb("Next", "Video 6 · Races & Circular Tracks")
        self.stack(head, [dirs, rev, trip, walk, box, nxt], buff=0.45, top=0.6)
        self.no_overlap(*dirs)
        self.no_overlap(*rev)

        n = self.narrate(
            id="summary_01",
            text="Downstream adds the stream speed; upstream subtracts it.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "adds")
        self.play(FadeIn(dirs[0], shift=UP * 0.1))
        self.at_word(n, "subtracts")
        self.play(FadeIn(dirs[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_02",
            text="The still-water speed is the average of D and U; the stream speed is half their difference.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "average")
        self.play(FadeIn(rev[0], shift=UP * 0.1))
        self.at_word(n, "half")
        self.play(FadeIn(rev[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_03",
            text="Round trips take longer than they would in still water, so their average speed is below u.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "longer")
        self.play(FadeIn(trip, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_04",
            text="Remember the moving walkway, and the formula box.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "walkway")
        self.play(FadeIn(walk, shift=UP * 0.1))
        self.at_word(n, "box")
        self.play(FadeIn(box, scale=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_05",
            text="Next: races and circular tracks.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Next")
        self.play(FadeIn(nxt, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S16_summary")

"""
animation.py for the LMS video generator.

Course : Pre-C-CAT - Section A - Logical Reasoning
Video  : Lesson 2 - Alphabets - 03 - Word Order & Letter Pairs

Source script:
  C:\\Scripts\\Section A\\Reasoning_Scripts\\Sessions 1-4 - Coding-Decoding, Alphabets, Directions, Number Series, Odd Man Out\\Lesson 2 - Alphabets\\03 - Word Order & Letter Pairs.pdf

Built on the golden-reference pattern:
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``;
  * layouts stacked with next_to and guarded with ``no_overlap``; nothing is
    ever animated onto or into another box.

Lesson 2, Video 2 of 6 (file 03 in its folder).
Not the first video: a silent breadcrumb, a one-line recap of Video 1, then today's topic.
The narration follows the script section by section and ends with the Section Quiz and its answer key.
Every dictionary order, sorted word and letter-pair count in the script was recomputed in the data block
(the pair counts by a full scan of every pair, in both directions); all of them are correct.
Pauses: 10 seconds on the checkpoint, 12 seconds on each practice and quiz screen.
"""

import math

import numpy as np
from manim import *

from src.animation import LMSScene

# ============================================================== style ====

BG = "#0B1020"
INK = "#E6EAF2"
MUTED = "#8B95A7"
PANEL = "#151C2E"
CELL = "#1B2440"

TERM = INK             # series terms
DIFF = "#4FC3F7"       # first differences
SECOND = "#CE93D8"     # second differences / pattern of the differences
RATIO = "#FFB74D"      # ratios (the next topic's tool)
FOCUS = "#FFD54F"      # "look here" / predicted value
GOOD = "#66BB6A"       # confirmed answer
BAD = "#EF5350"        # wrong / trap

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

def text(s, size=BODY, color=INK, weight=NORMAL, t2c=None):
    return Text(s, font=FONT, font_size=size, color=color, weight=weight, t2c=t2c or {})


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

WORD = "#4FC3F7"          # the question word
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

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def letter_pos(ch):
    return ALPHABET.index(ch) + 1


def letter_pairs(word):
    """Every pair with as many letters between them in the word as in the alphabet: (i, j, "forward" | "backward")."""
    out = []
    for i in range(len(word)):
        for j in range(i + 1, len(word)):
            gap = letter_pos(word[j]) - letter_pos(word[i])
            if abs(gap) == j - i:
                out.append((i, j, "forward" if gap > 0 else "backward"))
    return out


def pair_names(word):
    return [word[i] + word[j] for i, j, _ in letter_pairs(word)]


def in_place(word, other):
    return [a for a, b in zip(word, other) if a == b]


def sort_letters(word):
    return "".join(sorted(word))


DATA_WORDS = ["DATA", "DATE", "DART", "DASH"]
CAR_WORDS = ["CARD", "CAR", "CARE", "CART"]
# ---- hook, worked examples ----
assert sorted(["report1", "report10", "report2"]) == ["report1", "report10", "report2"] and "report10"[6] < "report2"[6]
assert sorted(DATA_WORDS) == ["DART", "DASH", "DATA", "DATE"] and sorted(CAR_WORDS) == ["CAR", "CARD", "CARE", "CART"]
assert letter_pairs("DEMOCRAT") == [(0, 1, "forward"), (4, 6, "backward"), (5, 7, "forward")] and pair_names("DEMOCRAT") == ["DE", "CA", "RT"]
assert [letter_pos(c) for c in "DEMOCRAT"] == [4, 5, 13, 15, 3, 18, 1, 20]
# ---- concept steps, exam patterns, traps, practice ----
assert sort_letters("PLANET") == "AELNPT" and sort_letters("PLANET")[2] == "L" and in_place("PLANET", "AELNPT") == ["N", "T"]
assert in_place("ACHIEVE", ALPHABET) == ["A", "E"] and "ACHIEVE".index("E") + 1 == 5
assert sorted(["CABLE", "CABIN", "CACHE", "CABBAGE"])[0] == "CABBAGE" and sorted(["SERVER", "SERVICE", "SERIAL", "SERUM"])[-1] == "SERVICE"
assert sorted(DATA_WORDS)[2] == "DATA" and pair_names("STAMP") == ["ST"]
assert pair_names("SCHEDULE") == ["CE", "HL", "ED"] and [d for _, _, d in letter_pairs("SCHEDULE")] == ["forward", "forward", "backward"]
# ---- section quiz ----
assert sorted(["STACK", "STAFF", "STAGE", "STABLE"])[0] == "STABLE"
assert sorted(["NETWORK", "NETWORTH", "NETBOOK", "NETIZEN"]) == ["NETBOOK", "NETIZEN", "NETWORK", "NETWORTH"]
assert sort_letters("BINARY") == "ABINRY" and sort_letters("BINARY")[3] == "N"
assert pair_names("GLOBAL") == ["GL", "OL", "BA"] and letter_pairs("GLOBAL")[0][:2] == (0, 5)
assert pair_names("CHANGE") == ["CA", "CG"] and in_place("ABSENT", ALPHABET) == ["A", "B"]

OBJECTIVES = [("Arrange words in dictionary order", "including words that share a prefix"),
              ("Rearrange the letters of a word", "and answer position questions"),
              ("Count letter pairs", "with the same gap in the word as in the alphabet")]
FORMULAS = ["Dictionary order:   the first differing letter decides;   a prefix comes first",
            "Rearranged word:   sort the letters, then read positions",
            "Letter pair:   gap in the word  =  gap in the alphabet,   forward or backward",
            "Scan:   each letter against every later letter",
            "Own position:   kth letter of the word  =  kth letter of the alphabet"]
PATTERNS = [("Shared prefix", "DATA, DATE, DART, DASH;   3rd?", "column by column", "DATA"),
            ("First in dictionary", "CABLE, CABIN, CACHE, CABBAGE", "third letter, then fourth", "CABBAGE"),
            ("Rearranged letters", "PLANET sorted;   3rd letter?", "A E L N P T", "L"),
            ("Letters in place", "PLANET vs AELNPT", "compare position by position", "2  (N, T)"),
            ("Letter pairs", "DEMOCRAT", "scan, both directions", "3"),
            ("Own position", "ACHIEVE", "A at 1,   E at 5", "2")]
TRAPS = [("Trap 1  ·  the prefix", "Which comes first:   CARD, CAR, CARE, CART?",
          "CARD:  D is the earliest fourth letter", "CAR has no fourth letter:  it is first",
          "a word that is the start of another comes before it"),
         ("Trap 2  ·  missing backward pairs", "How many qualifying letter pairs are in SCHEDULE?",
          "forward pairs only:  CE and HL, so 2", "ED is a backward pair:  3",
          "check every pair in both directions")]
PRACTICE_A = [("L1", "Which comes first in a dictionary:  CABLE, CABIN, CACHE or CABBAGE?"),
              ("L1", "Arrange the letters of PLANET alphabetically.  Which letter is 3rd from the left?"),
              ("L1", "Which comes last in a dictionary:  SERVER, SERVICE, SERIAL or SERUM?"),
              ("L2", "Arrange DATA, DATE, DART and DASH in dictionary order.  Which is 3rd?"),
              ("L2", "How many pairs of letters in STAMP have as many letters between them in the word as in the alphabet?"),
              ("L2", "If the letters of PLANET are arranged alphabetically, how many letters stay in the same position?")]
PRACTICE_B = [("L3", "How many pairs of letters in DEMOCRAT have as many letters between them in the word as in the alphabet?"),
              ("L3", "How many such pairs are there in SCHEDULE?"),
              ("L3", "How many letters of ACHIEVE are at the same position in the word as in the alphabet?")]
ANSWERS_A = [("CAB-B before CAB-I and CAB-L;   CAC comes last", "CABBAGE"),
             ("A E L N P T", "L"),
             ("SERI,  SERU,  SERV-E,  SERV-I", "SERVICE"),
             ("DART,  DASH,  DATA,  DATE", "DATA"),
             ("ST only", "1")]
ANSWERS_B = [("N and T stay", "2"),
             ("DE,  CA,  RT", "3"),
             ("CE,  HL,  ED", "3"),
             ("A (1st) and E (5th)", "2")]
LENS = [("Recognition cue", "“dictionary order”, “arranged alphabetically”, “as many letters between them”"),
        ("Target time", "25 seconds for order questions,  40 seconds for letter pairs"),
        ("Sanity check", "for pairs, list them:  a number without a list is a guess")]
QUIZ = [["Which comes first in a dictionary:  STACK, STAFF, STAGE or STABLE?", "(a) STACK   (b) STAFF   (c) STABLE   (d) STAGE"],
        ["In dictionary order, which of NETWORK, NETWORTH, NETBOOK and NETIZEN comes third?",
         "(a) NETWORK   (b) NETWORTH   (c) NETIZEN   (d) NETBOOK"],
        ["Arrange the letters of BINARY alphabetically.  Which letter is 4th from the left?", "(a) R   (b) I   (c) A   (d) N"],
        ["How many pairs of letters in GLOBAL have as many letters between them in the word as in the alphabet?",
         "(a) 1   (b) 3   (c) 2   (d) 4"],
        ["How many such pairs are there in CHANGE?", "(a) 2   (b) 1   (c) 0   (d) 3"],
        ["How many letters of ABSENT are at the same position in the word as in the alphabet?", "(a) 1   (b) 3   (c) 0   (d) 2"]]
QUIZ_KEY = [("fourth letters:   B, C, F, G", "(c)  STABLE"),
            ("NETBOOK,  NETIZEN,  NETWORK,  NETWORTH", "(a)  NETWORK"),
            ("A B I N R Y", "(d)  N"),
            ("GL,  OL,  BA", "(b)  3"),
            ("CA,  CG", "(a)  2"),
            ("A (1st) and B (2nd)", "(d)  2")]


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


class WordOrderAndLetterPairsVideo(LMSScene):
    lesson_title = "Word Order & Letter Pairs"

    def construct(self):
        self.camera.background_color = BG

        self.intro()
        self.hook()
        self.objectives()
        self.why_this_section()
        self.concept_journey()
        self.rule_box()
        self.short_trick()
        self.analogy()
        self.order_example()
        self.pairs_example()
        self.exam_patterns()
        self.traps()
        self.checkpoint()
        self.practice()
        self.answers()
        self.exam_lens()
        self.summary()
        self.section_quiz()

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
        colors = [DIFF, "#F48FB1", RATIO]
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
        level_cols = {"L1": GOOD, "L2": RATIO, "L3": BAD}
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

    def table_under(self, head, ref, header, rows, widths, size=SMALL):
        """A reference block under ``head`` and a table under it, fitted to the space that is left.  Returns (table, body rows)."""
        fit_width(ref, SAFE_W)
        ref.next_to(head, DOWN, buff=0.35)
        table = self.table_rows(header, rows, widths, size=size)
        fit_within(table, SAFE_W, ref.get_bottom()[1] + FRAME_H / 2 - SAFE - 1.2)
        table.next_to(ref, DOWN, buff=0.4)
        self.no_overlap(head, ref, table)
        self.no_overlap(*table)
        self.validator.check_in_frame(VGroup(head, ref, table))
        return table, table[1:]
    def step_rows(self, items, color=WORD):
        """Numbered concept steps.  Each row = (number chip, the step[, a short note in green])."""
        rows = VGroup()
        for i, (what, note) in enumerate(items):
            row = VGroup(pill(str(i + 1), color, size=SMALL), text(what, LABEL, INK, BOLD))
            if note:
                row.add(text(note, LABEL, GOOD, BOLD))
            rows.add(row.arrange(RIGHT, buff=0.35))
        return fit_width(rows.arrange(DOWN, buff=0.5, aligned_edge=LEFT), SAFE_W - 0.6)

    def word_stack(self, words, size=36, step=0.55, drop=0.64, color=INK):
        """Words stacked with their letters in aligned columns.  rows[r][k] = letter k of word r."""
        rows = VGroup(*[VGroup(*[text(ch, size, color, BOLD).move_to(RIGHT * k * step + DOWN * r * drop) for k, ch in enumerate(w)])
                        for r, w in enumerate(words)])
        self.no_overlap(*rows, gap=0.02)
        return rows

    def column(self, rows, k):
        """Column k of a word_stack (only the words long enough to have it)."""
        return VGroup(*[row[k] for row in rows if len(row) > k])

    def word_row(self, word, under, gap=0.9):
        """A word spread out, with a number under each letter.  row[i] = (letter, number)."""
        cells = VGroup()
        for i, (ch, n) in enumerate(zip(word, under)):
            x = RIGHT * (i - (len(word) - 1) / 2) * gap
            cells.add(VGroup(text(ch, 36, INK, BOLD).move_to(x + UP * 0.3), text(str(n), MIN_FONT, MUTED).move_to(x + DOWN * 0.3)))
        self.no_overlap(*cells, gap=0.02)
        return cells

    def pair_arc(self, row, i, j, color):
        """An arc over a word_row joining letters i and j (call it after the row is placed)."""
        return ArcBetweenPoints(row[i][0].get_top() + UP * 0.1, row[j][0].get_top() + UP * 0.1, angle=-TAU / 5, color=color, stroke_width=4)

    # ============================================== 0. INTRO ==========
    # Not the first video: silent breadcrumb, a one-line recap of the previous video, then today's topic.

    def intro(self):
        self.scene_start("S00_intro", title="Intro")

        crumb = self.breadcrumb("Logical Reasoning", "Lesson 2 · Alphabets", "Video 2 of 6")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        recap = VGroup(text("from Video 1  ·  Positions from Both Ends", SMALL, MUTED), pill("from the right = 27 − from the left;   right +,  left −", WORD, size=LABEL)).arrange(DOWN, buff=0.25)
        title = fit_width(text("Word Order & Letter Pairs", TITLE, INK, BOLD), SAFE_W - 0.4)
        today = text("today: the first difference decides", LABEL, FOCUS)
        block = VGroup(recap, title, today).arrange(DOWN, buff=0.7)
        fit_within(block, SAFE_W, SAFE_H - crumb.height - 0.9)
        block.next_to(crumb, DOWN, buff=0.7)
        self.no_overlap(crumb, recap, title, today)
        self.validator.check_in_frame(VGroup(crumb, block))

        n = self.narrate(
            id="intro_01",
            text="In the last video, a position from the right became twenty-seven minus the position from the left; then "
                 "right meant add, and left meant subtract.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.at_word(n, "became")
        self.play(FadeIn(recap[0]))
        self.at_word(n, "minus")
        self.play(FadeIn(recap[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="intro_02",
            text="This video covers word order and letter pairs, where the first difference decides.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "covers")
        self.play(FadeIn(title, shift=UP * 0.1))
        self.at_word(n, "first")
        self.play(FadeIn(today, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_intro")

    # ============================================== 1. HOOK ==========

    def hook(self):
        self.scene_start("S01_hook", title="Hook")

        head = self.heading("A sorted folder")
        files = VGroup(*[Text(name, font="Consolas", font_size=36, color=INK) for name in ("report1", "report10", "report2")])\
            .arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        listing = self.card(files, color=WORD, pad=0.45)
        notes = VGroup(text("“report10” lands before “report2”", LABEL, BAD, BOLD), text("not a bug:  one character at a time", LABEL, INK),
                       text("at the 7th character,  “1” comes before “2”", LABEL, FOCUS, BOLD),
                       text("everything after that is never looked at", SMALL, MUTED)).arrange(DOWN, buff=0.4, aligned_edge=LEFT)
        row = VGroup(listing, notes).arrange(RIGHT, buff=1.0)
        moral = pill("a dictionary works the same way", GOOD, size=LABEL)
        self.stack(head, [row, moral], buff=0.9, top=0.9)
        self.no_overlap(listing, notes)
        self.no_overlap(*notes)

        n = self.narrate(
            id="hook_01",
            text="Sort a folder with a plain character-by-character sort, and report ten lands before report two.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "folder")
        self.play(FadeIn(listing))
        self.at_word(n, "lands")
        self.play(FadeIn(notes[0], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_02",
            text="It looks like a bug. It is not: the sort compares one character at a time, and at the seventh character, "
                 "one comes before two.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "bug")
        self.play(Indicate(files[1], color=FOCUS, scale_factor=1.03))
        self.at_word(n, "compares")
        self.play(FadeIn(notes[1], shift=RIGHT * 0.2))
        self.at_word(n, "seventh")
        self.play(VGroup(files[1][6], files[2][6]).animate.set_color(FOCUS), FadeIn(notes[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_03",
            text="Everything after that is never looked at.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "never")
        self.play(files[1][7].animate.set_opacity(0.3), FadeIn(notes[3], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_04",
            text="A dictionary works the same way. Learn that one rule, and every word-order question is mechanical.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "dictionary")
        self.play(FadeIn(moral, scale=1.03))
        self.at_word(n, "mechanical")
        self.play(Indicate(moral, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S01_hook")

    # ============================================== 2. OBJECTIVES ==========

    def objectives(self):
        self.scene_start("S02_objectives", title="Objectives")

        head = self.heading("By the end of this video")
        blocks = two_line_blocks(OBJECTIVES, WORD)
        self.stack(head, list(blocks), buff=0.6, top=0.8, align=LEFT)

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
            text="One: arrange words in dictionary order, including words that share a prefix.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "arrange")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "prefix")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="objectives_03",
            text="Two: rearrange the letters of a word, and answer position questions.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "rearrange")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "answer")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="objectives_04",
            text="Three: count letter pairs with the same gap in the word as in the alphabet.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "count")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "gap")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_objectives")

    # ============================================== 3. WHY THIS SECTION ==========

    def why_this_section(self):
        self.scene_start("S03_why_this_section", title="Why This Section")

        head = self.heading("Why this section")
        tests = pill("order and pair questions test procedure, not vocabulary", WORD, size=LABEL)
        scan = text("a fixed scan prevents the two classic misses", LABEL, INK)
        misses = VGroup(pill("deciding too early", BAD, size=LABEL), pill("ignoring backward pairs", BAD, size=LABEL)).arrange(RIGHT, buff=0.6)
        self.stack(head, [tests, scan, misses], buff=1.0, top=1.2)
        self.no_overlap(*misses)

        n = self.narrate(
            id="why_this_section_01",
            text="Order and pair questions test procedure, not vocabulary.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "procedure")
        self.play(FadeIn(tests, scale=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="why_this_section_02",
            text="A fixed scan prevents the two classic misses: deciding too early, and ignoring backward pairs.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "scan")
        self.play(FadeIn(scan, shift=UP * 0.1))
        self.at_word(n, "early")
        self.play(FadeIn(misses[0], shift=UP * 0.1))
        self.at_word(n, "backward")
        self.play(FadeIn(misses[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_why_this_section")

    # ============================================== 4. THE CONCEPT JOURNEY ==========

    def concept_journey(self):
        self.scene_start("S04_concept_journey", title="The Concept Journey")

        head = self.heading("Steps 1 and 2  ·  dictionary order, the prefix rule")
        rows = self.word_stack(DATA_WORDS)
        decide = VGroup(text("compare the first letters;  if they match, the second,  and so on", SMALL, INK),
                        pill("the first difference decides", FOCUS, size=LABEL)).arrange(DOWN, buff=0.3)
        top = VGroup(rows, decide).arrange(RIGHT, buff=1.2)
        pre = self.word_stack(["CAR", "CARD"], color=RATIO)
        prefix = VGroup(text("one word is the start of another:", SMALL, INK), text("the shorter word comes first", LABEL, GOOD, BOLD)).arrange(DOWN, buff=0.2)
        low = VGroup(pre, prefix).arrange(RIGHT, buff=1.2)
        self.stack(head, [top, low], buff=0.9, top=0.8)
        self.no_overlap(rows, decide)
        self.no_overlap(pre, prefix)

        n = self.narrate(
            id="concept_journey_01",
            text="Step one: dictionary order. Compare the first letters. If they match, compare the second, and so on.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "one")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "order")
        self.play(FadeIn(rows))
        self.at_word(n, "first")
        self.play(Indicate(self.column(rows, 0), color=FOCUS, scale_factor=1.03), FadeIn(decide[0], shift=UP * 0.1))
        self.at_word(n, "second")
        self.play(Indicate(self.column(rows, 1), color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_journey_02",
            text="The first difference decides.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "difference")
        self.play(self.column(rows, 2).animate.set_color(FOCUS), FadeIn(decide[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_journey_03",
            text="Step two: the prefix rule. If one word is the start of another, the shorter word comes first: CAR before "
                 "CARD.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "two")
        self.play(Indicate(head, color=FOCUS, scale_factor=1.03))
        self.at_word(n, "start")
        self.play(FadeIn(pre), FadeIn(prefix[0], shift=UP * 0.1))
        self.at_word(n, "shorter")
        self.play(FadeIn(prefix[1], shift=UP * 0.1))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Step 3  ·  rearranging letters")
        word = self.word_row("PLANET", range(1, 7))
        ordered = self.word_row(sort_letters("PLANET"), range(1, 7))
        pair = VGroup(word, text("→", TITLE, MUTED), ordered).arrange(RIGHT, buff=0.8)
        asks = VGroup(VGroup(text("which letter is 3rd?", LABEL, INK), pill("L", GOOD, size=LABEL)).arrange(RIGHT, buff=0.4),
                      VGroup(text("how many stay in place?", LABEL, INK), pill("2:  N and T", GOOD, size=LABEL)).arrange(RIGHT, buff=0.4))\
            .arrange(RIGHT, buff=1.2)
        sort = pill("sort the letters of the word alphabetically, then answer", FOCUS, size=LABEL)
        self.stack(head, [sort, pair, asks], buff=0.9, top=0.9)
        self.no_overlap(*pair)
        self.no_overlap(*asks)

        n = self.narrate(
            id="concept_journey_04",
            text="Step three: rearranging letters. Sort the letters of a word alphabetically, then answer the question.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "three")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "Sort")
        self.play(FadeIn(sort, scale=1.03))
        self.at_word(n, "answer")
        self.play(FadeIn(word), FadeIn(pair[1], shift=UP * 0.1), FadeIn(ordered, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_journey_05",
            text="For example: which letter is third, or how many stay in place?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "third")
        self.play(FadeIn(asks[0], shift=UP * 0.1), ordered[2].animate.set_color(FOCUS))
        self.at_word(n, "stay")
        self.play(FadeIn(asks[1], shift=UP * 0.1), VGroup(word[3], ordered[3], word[5], ordered[5]).animate.set_color(GOOD))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Steps 4 to 6  ·  letter pairs")
        rule = pill("letters between them in the word  =  letters between them in the alphabet", FOCUS, size=LABEL)
        row = self.word_row("DEMOCRAT", [letter_pos(ch) for ch in "DEMOCRAT"])
        kinds = VGroup(pill("forward:  word order matches alphabet order", GOOD, size=SMALL), pill("backward:  word order is reversed", RATIO, size=SMALL))\
            .arrange(RIGHT, buff=0.5)
        scan = text("scan:  take each letter in turn and compare it only with the letters after it", LABEL, INK, BOLD)
        self.stack(head, [rule, row, kinds, scan], buff=0.9, top=0.7)
        self.no_overlap(*kinds)
        arcs = VGroup(self.pair_arc(row, 0, 1, GOOD), self.pair_arc(row, 4, 6, RATIO))
        self.no_overlap(rule, arcs)

        n = self.narrate(
            id="concept_journey_06",
            text="Step four: letter pairs. A pair counts if the number of letters between them in the word equals the "
                 "number between them in the alphabet.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "four")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "pair")
        self.play(FadeIn(row))
        self.at_word(n, "equals")
        self.play(FadeIn(rule, scale=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_journey_07",
            text="Step five: both directions. Count forward pairs, where the word order matches the alphabet order, and "
                 "backward pairs, where the word order is reversed.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "five")
        self.play(Indicate(head, color=FOCUS, scale_factor=1.03))
        self.at_word(n, "forward")
        self.play(FadeIn(kinds[0], shift=UP * 0.1), Create(arcs[0]))
        self.at_word(n, "backward")
        self.play(FadeIn(kinds[1], shift=UP * 0.1), Create(arcs[1]))
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_journey_08",
            text="Most errors come from missing backward pairs.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "missing")
        self.play(Indicate(kinds[1], color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_journey_09",
            text="Step six: the systematic scan. Take each letter in turn, and compare it only with the letters after it. "
                 "Nothing is counted twice and nothing is missed.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "six")
        self.play(Indicate(head, color=FOCUS, scale_factor=1.03))
        self.at_word(n, "after")
        self.play(FadeIn(scan, shift=UP * 0.1))
        self.at_word(n, "twice")
        self.play(Indicate(scan, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Step 7  ·  letters at their own position")
        asks = text("how many letters sit at the same position in the word as in the alphabet?", LABEL, INK)
        row = self.word_row("ACHIEVE", range(1, 8))
        same = VGroup(pill("A is 1st", GOOD, size=LABEL), pill("E is 5th", GOOD, size=LABEL), text("2 letters", BODY, GOOD, BOLD)).arrange(RIGHT, buff=0.6)
        self.stack(head, [asks, row, same], buff=1.0, top=1.0)
        self.no_overlap(*same)

        n = self.narrate(
            id="concept_journey_10",
            text="Step seven: letters at their own position. Some questions ask how many letters of a word sit at the same "
                 "position as in the alphabet: the first letter is A, the second is B, the fifth is E, and so on.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "seven")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "ask")
        self.play(FadeIn(asks, shift=UP * 0.1))
        self.at_word(n, "first")
        self.play(FadeIn(row))
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_journey_11",
            text="In ACHIEVE, A is first and E is fifth: two letters.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "first")
        self.play(row[0].animate.set_color(FOCUS), FadeIn(same[0], shift=UP * 0.1))
        self.at_word(n, "fifth")
        self.play(row[4].animate.set_color(FOCUS), FadeIn(same[1], shift=UP * 0.1))
        self.at_word(n, "letters")
        self.play(FadeIn(same[2], shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_concept_journey")

    # ============================================== 5. RULE BOX ==========

    def rule_box(self):
        self.scene_start("S05_rule_box", title="Rule Box")

        head = self.heading("Rule box", GOOD)
        lines = VGroup(*[text(f, LABEL, INK) for f in FORMULAS]).arrange(DOWN, buff=0.42, aligned_edge=LEFT)
        fit_width(lines, SAFE_W - 1.6)
        box = self.card(lines, width=SAFE_W - 0.4, color=GOOD, pad=0.5)
        self.stack(head, [box], top=0.8)

        n = self.narrate(
            id="rule_box_01",
            text="Here is the rule box. Dictionary order: the first differing letter decides, and a prefix comes first.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "box")
        self.play(FadeIn(box[0]))
        self.at_word(n, "differing")
        self.play(FadeIn(lines[0], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="rule_box_02",
            text="A rearranged word: sort the letters, then read positions.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "sort")
        self.play(FadeIn(lines[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="rule_box_03",
            text="A letter pair: the gap in the word equals the gap in the alphabet, forward or backward.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "gap")
        self.play(FadeIn(lines[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="rule_box_04",
            text="The scan: each letter against every later letter.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "later")
        self.play(FadeIn(lines[3], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="rule_box_05",
            text="Own position: the k-th letter of the word is the k-th letter of the alphabet.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Own")
        self.play(FadeIn(lines[4], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_rule_box")

    # ============================================== 6. SHORT TRICK ==========

    def short_trick(self):
        self.scene_start("S06_short_trick", title="Short Trick")

        head = self.heading("Short trick", RATIO)
        words = VGroup(pill("word order", WORD, size=LABEL), text("line the words up and read down the columns", LABEL, INK, BOLD),
                       text("the first column that differs decides", SMALL, GOOD, BOLD))
        words[1].next_to(words[0], RIGHT, buff=0.5)
        words[2].next_to(words[1], DOWN, buff=0.2, aligned_edge=LEFT)
        pairs = VGroup(pill("letter pairs", RATIO, size=LABEL), text("compare each letter only with the letters after it", LABEL, INK, BOLD),
                       text("in both directions", SMALL, GOOD, BOLD))
        pairs[1].next_to(pairs[0], RIGHT, buff=0.5)
        pairs[2].next_to(pairs[1], DOWN, buff=0.2, aligned_edge=LEFT)
        self.stack(head, [words, pairs], buff=1.1, top=1.2, align=LEFT)
        self.no_overlap(*words)
        self.no_overlap(*pairs)

        n = self.narrate(
            id="short_trick_01",
            text="The short trick: line the words up and read down the columns; the first column that differs decides.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "line")
        self.play(FadeIn(words[:2], shift=UP * 0.1))
        self.at_word(n, "differs")
        self.play(FadeIn(words[2], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="short_trick_02",
            text="For pairs, compare each letter only with the letters after it, in both directions.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "compare")
        self.play(FadeIn(pairs[:2], shift=UP * 0.1))
        self.at_word(n, "both")
        self.play(FadeIn(pairs[2], shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_short_trick")

    # ============================================== 7. THE ANALOGY - A STRING COMPARISON ==========

    def analogy(self):
        self.scene_start("S07_analogy", title="The Analogy - A String Comparison")

        head = self.heading("Dictionary order is a string comparison")
        rows = self.word_stack(["DATA", "DATE"], size=44, step=0.7, drop=0.8)
        walk = text("walk both words together, and stop at the first difference", LABEL, INK)
        stops = VGroup(text("where the analogy stops", SMALL, BAD, BOLD),
                       text("computer sorts also rank digits, capitals and symbols, and some use “natural” number order", SMALL, INK),
                       text("exam questions use plain letters only", SMALL, GOOD, BOLD)).arrange(DOWN, buff=0.14, aligned_edge=LEFT)
        self.stack(head, [rows, walk, stops], buff=0.9, top=0.9)
        self.no_overlap(*stops)

        n = self.narrate(
            id="analogy_01",
            text="Dictionary order is a string comparison: walk both words together, and stop at the first difference.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "comparison")
        self.play(FadeIn(rows))
        self.at_word(n, "walk")
        self.play(FadeIn(walk, shift=UP * 0.1), Indicate(self.column(rows, 0), color=FOCUS, scale_factor=1.03))
        self.at_word(n, "stop")
        self.play(self.column(rows, 3).animate.set_color(FOCUS))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_02",
            text="Where the analogy stops: computer sorts also rank digits, capitals and symbols, and some use natural "
                 "number order.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "stops")
        self.play(FadeIn(stops[0], shift=RIGHT * 0.2))
        self.at_word(n, "rank")
        self.play(FadeIn(stops[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_03",
            text="Exam questions use plain letters only.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "plain")
        self.play(FadeIn(stops[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S07_analogy")

    # ============================================== 8. WORKED EXAMPLE - DICTIONARY ORDER ==========

    def order_example(self):
        self.scene_start("S08_order_example", title="Worked Example - Dictionary Order")

        head = self.heading("Worked example: dictionary order")
        rows = self.word_stack(DATA_WORDS)
        steps = self.solve_steps([("all start with DA;   third letters", "R (DART),  S (DASH),  T (DATA, DATE)"),
                                  ("DATA against DATE:   fourth letters", "A before E"),
                                  ("the order", "DART,  DASH,  DATA,  DATE")])
        row = VGroup(rows, steps).arrange(RIGHT, buff=1.0)
        self.stack(head, [row], top=1.2)
        self.no_overlap(rows, steps)
        self.no_overlap(*steps)

        n = self.narrate(
            id="order_example_01",
            text="Arrange DATA, DATE, DART and DASH.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Arrange")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "DATA")
        self.play(FadeIn(rows))
        self.wait_for_narration(n)

        n = self.narrate(
            id="order_example_02",
            text="Step one: all start with D A. The third letters are R in DART, S in DASH, and T in DATA and DATE.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "start")
        self.play(Indicate(VGroup(self.column(rows, 0), self.column(rows, 1)), color=FOCUS, scale_factor=1.03))
        self.at_word(n, "third")
        self.play(self.column(rows, 2).animate.set_color(FOCUS), FadeIn(steps[0], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="order_example_03",
            text="Step two: DATA against DATE. In the fourth letters, A comes before E.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "against")
        self.play(VGroup(rows[0][3], rows[1][3]).animate.set_color(RATIO))
        self.at_word(n, "before")
        self.play(FadeIn(steps[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="order_example_04",
            text="Step three, the order: DART, DASH, DATA, DATE.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "order")
        self.play(FadeIn(steps[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S08_order_example")

    # ============================================== 9. A SECOND WORKED EXAMPLE - LETTER PAIRS ==========

    def pairs_example(self):
        self.scene_start("S09_pairs_example", title="A Second Worked Example - Letter Pairs")

        head = self.heading("A second worked example: letter pairs")
        ask = text("How many pairs of letters in DEMOCRAT have as many letters between them in the word as in the alphabet?", SMALL, INK)
        row = self.word_row("DEMOCRAT", [letter_pos(ch) for ch in "DEMOCRAT"])
        steps = self.solve_steps([("D–E:   adjacent in the word,  adjacent in the alphabet", "forward"),
                                  ("C–A:   one letter (R) between in the word,  one (B) in the alphabet", "backward"),
                                  ("R–T:   one letter (A) between in the word,  one (S) in the alphabet", "forward")])
        answer = pill("a full scan finds no others:   3 pairs", GOOD, size=LABEL)
        self.stack(head, [ask, row, steps, answer], buff=0.6, top=0.9)
        self.no_overlap(*steps)
        arcs = VGroup(self.pair_arc(row, 0, 1, GOOD), self.pair_arc(row, 4, 6, RATIO), self.pair_arc(row, 5, 7, GOOD))
        self.no_overlap(ask, arcs)

        n = self.narrate(
            id="pairs_example_01",
            text="How many pairs of letters in DEMOCRAT have as many letters between them in the word as in the alphabet?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "pairs")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "DEMOCRAT")
        self.play(FadeIn(ask, shift=UP * 0.1), FadeIn(row, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="pairs_example_02",
            text="One: D and E are adjacent in the word and adjacent in the alphabet. A forward pair.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "adjacent")
        self.play(Create(arcs[0]))
        self.at_word(n, "forward")
        self.play(FadeIn(steps[0], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="pairs_example_03",
            text="Two: C and A have one letter, R, between them in the word, and one letter, B, between them in the "
                 "alphabet. A backward pair.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "between")
        self.play(Create(arcs[1]))
        self.at_word(n, "backward")
        self.play(FadeIn(steps[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="pairs_example_04",
            text="Three: R and T have one letter, A, between them in the word, and one letter, S, between them in the "
                 "alphabet. A forward pair.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "between")
        self.play(Create(arcs[2]))
        self.at_word(n, "forward")
        self.play(FadeIn(steps[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="pairs_example_05",
            text="A full scan finds no others, so the answer is three.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "scan")
        self.play(FadeIn(answer, scale=1.03))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S09_pairs_example")

    # ============================================== 10. EXAM PATTERNS - HOW THIS IS ASKED ==========

    def exam_patterns(self):
        self.scene_start("S10_exam_patterns", title="Exam Patterns - How This Is Asked")

        head = self.heading("Exam patterns  ·  part 1")
        table, rows = self.pattern_table(head, PATTERNS[:3])

        n = self.narrate(
            id="exam_patterns_01",
            text="Exams ask this in six ways.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "six")
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_02",
            text="Shared prefix: for DATA, DATE, DART and DASH, go column by column; the third is DATA.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "prefix")
        self.play(FadeIn(rows[0][:3], shift=RIGHT * 0.2))
        self.at_word(n, "third")
        self.play(FadeIn(rows[0][3], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_03",
            text="First in dictionary: for CABLE, CABIN, CACHE and CABBAGE, use the third letter, then the fourth: "
                 "CABBAGE.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "dictionary")
        self.play(FadeIn(rows[1][:3], shift=RIGHT * 0.2))
        self.at_word(n, "fourth")
        self.play(FadeIn(rows[1][3], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_04",
            text="Rearranged letters: PLANET sorted is A, E, L, N, P, T, so the third letter is L.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Rearranged")
        self.play(FadeIn(rows[2][:3], shift=RIGHT * 0.2))
        self.at_word(n, "so")
        self.play(FadeIn(rows[2][3], shift=LEFT * 0.1))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Exam patterns  ·  part 2")
        table, rows = self.pattern_table(head, PATTERNS[3:])

        n = self.narrate(
            id="exam_patterns_05",
            text="Letters in place: compare PLANET with its sorted form position by position; two stay, N and T.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "place")
        self.play(FadeIn(rows[0][:3], shift=RIGHT * 0.2))
        self.at_word(n, "stay")
        self.play(FadeIn(rows[0][3], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_06",
            text="Letter pairs: scan DEMOCRAT in both directions, giving three.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "pairs")
        self.play(FadeIn(rows[1][:3], shift=RIGHT * 0.2))
        self.at_word(n, "giving")
        self.play(FadeIn(rows[1][3], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_07",
            text="Own position: in ACHIEVE, A is at one and E is at five, giving two.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Own")
        self.play(FadeIn(rows[2][:3], shift=RIGHT * 0.2))
        self.at_word(n, "giving")
        self.play(FadeIn(rows[2][3], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S10_exam_patterns")

    # ============================================== 11. TRAPS AND CONFUSING QUESTIONS ==========

    def traps(self):
        self.scene_start("S11_traps", title="Traps and Confusing Questions")

        head, ask, wrong, right, rule = self.show_trap(TRAPS[0])

        n = self.narrate(
            id="traps_01",
            text="Trap one: the prefix.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "prefix")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_02",
            text="Which comes first: CARD, CAR, CARE or CART?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "first")
        self.play(FadeIn(ask, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_03",
            text="The wrong instinct: CARD, because D is the earliest fourth letter.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "instinct")
        self.play(FadeIn(wrong, shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_04",
            text="Correct: CAR has no fourth letter, so it comes first: CAR, CARD, CARE, CART.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "no")
        self.play(FadeIn(right, shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_05",
            text="The rule: a word that is the start of another comes before it.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "start")
        self.play(FadeIn(rule, scale=1.03))
        self.wait_for_narration(n)
        self.clear_stage()

        head, ask, wrong, right, rule = self.show_trap(TRAPS[1])

        n = self.narrate(
            id="traps_06",
            text="Trap two: missing backward pairs.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "missing")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_07",
            text="How many qualifying letter pairs are in SCHEDULE?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "qualifying")
        self.play(FadeIn(ask, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_08",
            text="The wrong instinct: counting only forward pairs, C E and H L, so two.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "instinct")
        self.play(FadeIn(wrong, shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_09",
            text="Correct: E D, E then D, adjacent both ways, is a backward pair, so three.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "backward")
        self.play(FadeIn(right, shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_10",
            text="The rule: check every pair in both directions.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "check")
        self.play(FadeIn(rule, scale=1.03))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S11_traps")

    # ============================================== 12. CHECKPOINT ==========

    def checkpoint(self):
        self.scene_start("S12_checkpoint", title="Checkpoint")

        head = self.heading("Checkpoint  ·  your turn")
        ask = pill("Arrange the letters of PLANET alphabetically.   Which letter is 3rd from the left?", FOCUS, size=LABEL)
        ordered = self.word_row(sort_letters("PLANET"), range(1, 7))
        answer = pill("the 3rd letter:  L", GOOD, size=BODY)
        self.stack(head, [ask, ordered, answer], buff=1.0, top=1.0)

        n = self.narrate(
            id="checkpoint_01",
            text="Your turn. Arrange the letters of PLANET alphabetically. Which letter is third from the left?",
            voice="default",
            subtitle=True,
            pause_after=10.0,
        )
        self.at_word(n, "turn")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "Arrange")
        self.play(FadeIn(ask, scale=1.03))
        self.at_word(n, "third")
        self.play(Indicate(ask, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="checkpoint_02",
            text="The sorted letters are A, E, L, N, P, T, so the third is L.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "sorted")
        self.play(FadeIn(ordered))
        self.at_word(n, "third")
        self.play(ordered[2].animate.set_color(FOCUS), FadeIn(answer, shift=UP * 0.1))
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
            text="Level one, question one: which comes first in a dictionary: CABLE, CABIN, CACHE or CABBAGE? Question "
                 "two: arrange the letters of PLANET alphabetically; which letter is third from the left? Question three: "
                 "which comes last in a dictionary: SERVER, SERVICE, SERIAL or SERUM?",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "first")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "PLANET")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.at_word(n, "last")
        self.play(FadeIn(rows[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="practice_02",
            text="Level two, question four: arrange DATA, DATE, DART and DASH in dictionary order; which is third? "
                 "Question five: how many pairs of letters in STAMP have as many letters between them in the word as in "
                 "the alphabet? Question six: if the letters of PLANET are arranged alphabetically, how many letters stay "
                 "in the same position?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "DATA")
        self.play(FadeIn(rows[3], shift=RIGHT * 0.2))
        self.at_word(n, "STAMP")
        self.play(FadeIn(rows[4], shift=RIGHT * 0.2))
        self.at_word(n, "stay")
        self.play(FadeIn(rows[5], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="practice_03",
            text="Pause the video and solve these six.",
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
        table, rows = self.practice_table(head, PRACTICE_B, 7)

        n = self.narrate(
            id="practice_04",
            text="Level three, question seven: how many pairs of letters in DEMOCRAT have as many letters between them in "
                 "the word as in the alphabet? Question eight: how many such pairs are there in SCHEDULE? Question nine: "
                 "how many letters of ACHIEVE are at the same position in the word as in the alphabet?",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "DEMOCRAT")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "SCHEDULE")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.at_word(n, "ACHIEVE")
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

        head = self.heading("Answer key  ·  1 to 5", GOOD)
        table, rows = self.answer_table(head, ANSWERS_A, 1)

        n = self.narrate(
            id="answers_01",
            text="One: C A B, B comes before C A B, I and C A B, L, and C A C comes last: CABBAGE.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "before")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "CABBAGE")
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_02",
            text="Two: A, E, L, N, P, T, so L.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "so")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2), FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_03",
            text="Three: S E R I, then S E R U, then S E R V, E, then S E R V, I: SERVICE.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "then")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "SERVICE")
        self.play(FadeIn(rows[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_04",
            text="Four: DART, DASH, DATA, DATE, so the third is DATA.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "DART")
        self.play(FadeIn(rows[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "third")
        self.play(FadeIn(rows[3][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_05",
            text="Five: S T only, so one.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "only")
        self.play(FadeIn(rows[4][:2], shift=RIGHT * 0.2))
        self.at_word(n, "one")
        self.play(FadeIn(rows[4][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Answer key  ·  6 to 9", GOOD)
        table, rows = self.answer_table(head, ANSWERS_B, 6)

        n = self.narrate(
            id="answers_06",
            text="Six: N and T stay, so two.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "stay")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "two")
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_07",
            text="Seven: D E, C A and R T, so three.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "and")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "three")
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_08",
            text="Eight: C E, H L and E D, so three.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "and")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "three")
        self.play(FadeIn(rows[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_09",
            text="Nine: A, the first, and E, the fifth, so two.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "first")
        self.play(FadeIn(rows[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "two")
        self.play(FadeIn(rows[3][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S14_answers")

    # ============================================== 15. EXAM LENS - RECOGNISE AND MOVE ==========

    def exam_lens(self):
        self.scene_start("S15_exam_lens", title="Exam Lens - Recognise and Move")

        head = self.heading("Exam lens: recognise and move", RATIO)
        blocks = two_line_blocks(LENS, RATIO)
        self.stack(head, list(blocks), buff=0.6, top=0.8, align=LEFT)

        n = self.narrate(
            id="exam_lens_01",
            text="Recognise and move. The recognition cue: the words, dictionary order, arranged alphabetically, or, as "
                 "many letters between them.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "cue")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "words")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_lens_02",
            text="The target time: twenty-five seconds for order questions, forty seconds for letter pairs.",
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
            text="The sanity check: for pairs, list them; a number without a list is a guess.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "sanity")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "list")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S15_exam_lens")

    # ============================================== 16. QUICK REVISION AND SUMMARY ==========

    def summary(self):
        self.scene_start("S16_summary", title="Quick Revision and Summary")

        head = self.heading("Quick revision")
        points = VGroup(text("compare words letter by letter:  the first difference decides, and a prefix comes first", LABEL, INK, BOLD),
                        text("letter pairs:  scan each letter against every later one, and count both directions", LABEL, INK, BOLD))\
            .arrange(DOWN, buff=0.6, aligned_edge=LEFT)
        box = VGroup(pill("first difference decides", GOOD, size=SMALL), pill("prefix first", GOOD, size=SMALL), pill("sort, then read", GOOD, size=SMALL),
                     pill("pairs:  both directions", GOOD, size=SMALL)).arrange(RIGHT, buff=0.3)
        self.stack(head, [points, box], buff=1.2, top=1.2)
        self.no_overlap(*points)
        self.no_overlap(*box)

        n = self.narrate(
            id="summary_01",
            text="Compare words letter by letter; the first difference decides, and a prefix comes first.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "Compare")
        self.play(FadeIn(points[0], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_02",
            text="For letter pairs, scan each letter against every later one, and count both directions.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "scan")
        self.play(FadeIn(points[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_03",
            text="The rule box in one line: the first difference decides; a prefix comes first; sort, then read; and for "
                 "pairs, both directions.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "line")
        self.play(FadeIn(box[0], shift=UP * 0.1))
        self.at_word(n, "prefix")
        self.play(FadeIn(box[1], shift=UP * 0.1))
        self.at_word(n, "sort")
        self.play(FadeIn(box[2], shift=UP * 0.1))
        self.at_word(n, "both")
        self.play(FadeIn(box[3], shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S16_summary")

    # ============================================== 17. SECTION QUIZ ==========

    def section_quiz(self):
        self.scene_start("S17_section_quiz", title="Section Quiz")

        head = self.heading("Section quiz")
        rules = VGroup(pill("6 questions", WORD, size=BODY), pill("5 minutes", WORD, size=BODY), pill("+3 correct", GOOD, size=BODY),
                       pill("−1 wrong", BAD, size=BODY)).arrange(RIGHT, buff=0.4)
        gate = VGroup(VGroup(pill("15 or more out of 18", GOOD, size=LABEL), text("move on", BODY, GOOD, BOLD)).arrange(RIGHT, buff=0.5),
                      VGroup(pill("below 15", BAD, size=LABEL), text("replay the Traps segment, then retry", BODY, INK, BOLD)).arrange(RIGHT, buff=0.5))            .arrange(DOWN, buff=0.6, aligned_edge=LEFT)
        self.stack(head, [rules, gate], buff=1.1, top=1.1)
        self.no_overlap(*rules)
        self.no_overlap(*gate)

        n = self.narrate(
            id="section_quiz_01",
            text="Now the section quiz: six questions in five minutes, with plus three for a correct answer and minus one "
                 "for a wrong one.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "quiz")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "questions")
        self.play(FadeIn(rules[0], shift=UP * 0.1))
        self.at_word(n, "minutes")
        self.play(FadeIn(rules[1], shift=UP * 0.1))
        self.at_word(n, "plus")
        self.play(FadeIn(rules[2], shift=UP * 0.1))
        self.at_word(n, "minus")
        self.play(FadeIn(rules[3], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="section_quiz_02",
            text="Fifteen or more out of eighteen: move on. Below fifteen: replay the traps segment, then retry.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "move")
        self.play(FadeIn(gate[0], shift=RIGHT * 0.2))
        self.at_word(n, "replay")
        self.play(FadeIn(gate[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Section quiz  ·  questions 1 to 3")
        table, rows = self.placed_table(head, ["#", "Question", "Options"],
                                        [[str(0 + i + 1)] + list(row) for i, row in enumerate(QUIZ[0:3])], [0.8, 7.6, 4.8], room=1.3)
        for row in rows:
            row[0].set_color(MUTED)

        n = self.narrate(
            id="section_quiz_03",
            text="Here are questions one, two and three.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "one")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "two")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.at_word(n, "three")
        self.play(FadeIn(rows[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="section_quiz_04",
            text="Pause the video and solve them.",
            voice="default",
            subtitle=True,
            pause_after=12.0,
        )
        self.at_word(n, "Pause")
        self.play(Indicate(head, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)
        self.clear_stage()

        head = self.heading("Section quiz  ·  questions 4 to 6")
        table, rows = self.placed_table(head, ["#", "Question", "Options"],
                                        [[str(3 + i + 1)] + list(row) for i, row in enumerate(QUIZ[3:6])], [0.8, 7.6, 4.8], room=1.3)
        for row in rows:
            row[0].set_color(MUTED)

        n = self.narrate(
            id="section_quiz_05",
            text="And here are questions four, five and six.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "four")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "five")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.at_word(n, "six")
        self.play(FadeIn(rows[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="section_quiz_06",
            text="Pause again and solve them.",
            voice="default",
            subtitle=True,
            pause_after=12.0,
        )
        self.at_word(n, "Pause")
        self.play(Indicate(head, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)
        self.clear_stage()

        head = self.heading("Section quiz  ·  answer key", GOOD)
        table, rows = self.answer_table(head, QUIZ_KEY, 1)
        nxt = self.breadcrumb("Next", "Video 3 · Word Formation & Letter Rules")
        nxt.next_to(table, DOWN, buff=0.6)
        self.no_overlap(table, nxt)
        self.validator.check_in_frame(VGroup(head, table, nxt))

        n = self.narrate(
            id="section_quiz_07",
            text="The answers. One: the fourth letters are B, C, F and G, so STABLE: option c.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "fourth")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "option")
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="section_quiz_08",
            text="Two: NETBOOK, NETIZEN, NETWORK, NETWORTH, so the third is NETWORK: option a.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "third")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "option")
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="section_quiz_09",
            text="Three: A, B, I, N, R, Y, so N: option d.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "so")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "option")
        self.play(FadeIn(rows[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="section_quiz_10",
            text="Four: G L, O L and B A, three pairs: option b.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "and")
        self.play(FadeIn(rows[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "option")
        self.play(FadeIn(rows[3][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="section_quiz_11",
            text="Five: C A and C G, two pairs: option a.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "and")
        self.play(FadeIn(rows[4][:2], shift=RIGHT * 0.2))
        self.at_word(n, "option")
        self.play(FadeIn(rows[4][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="section_quiz_12",
            text="Six: A, the first, and B, the second, two letters: option d.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "first")
        self.play(FadeIn(rows[5][:2], shift=RIGHT * 0.2))
        self.at_word(n, "option")
        self.play(FadeIn(rows[5][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="section_quiz_13",
            text="Next: word formation and letter rules.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Next")
        self.play(FadeIn(nxt, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S17_section_quiz")

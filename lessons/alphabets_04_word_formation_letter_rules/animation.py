"""
animation.py for the LMS video generator.

Course : Pre-C-CAT - Section A - Logical Reasoning
Video  : Lesson 2 - Alphabets - 04 - Word Formation & Letter Rules

Source script:
  C:\\Scripts\\Section A\\Reasoning_Scripts\\Sessions 1-4 - Coding-Decoding, Alphabets, Directions, Number Series, Odd Man Out\\Lesson 2 - Alphabets\\04 - Word Formation & Letter Rules.pdf

Built on the golden-reference pattern:
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``;
  * layouts stacked with next_to and guarded with ``no_overlap``; nothing is
    ever animated onto or into another box.

Lesson 2, Video 3 of 6 (file 04 in its folder).
Not the first video: a silent breadcrumb, a one-line recap of Video 2, then today's topic.
The narration follows the script section by section and ends with the Section Quiz and its answer key.
Every letter count, formed word and letter-rule result in the script was recomputed in the data block; all of them are correct.
Pauses: 3 seconds on the hook question, 10 seconds on the checkpoint, 12 seconds on each practice and quiz screen.
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

from collections import Counter

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
VOWELS = "AEIOU"


def can_form(target, source):
    have = Counter(source)
    return all(have[ch] >= n for ch, n in Counter(target).items())


def tally(word):
    """(letter, count) in order of first appearance."""
    return [(ch, word.count(ch)) for ch in dict.fromkeys(word)]


def change(word, vowel_step, consonant_step):
    return "".join(ALPHABET[(ALPHABET.index(ch) + (vowel_step if ch in VOWELS else consonant_step)) % 26] for ch in word)


def picked(word, positions):
    return [word[p - 1] for p in positions]


# ---- hook, concept steps, worked examples ----
assert tally("ENGINEERING") == [("E", 3), ("N", 3), ("G", 2), ("I", 2), ("R", 1)] and "T" not in "ENGINEERING"
assert tally("ENTER") == [("E", 2), ("N", 1), ("T", 1), ("R", 1)] and not can_form("ENTER", "ENGINEERING")
assert all(can_form(w, "ENGINEERING") for w in ("GREEN", "REIGN", "GINGER"))
assert change("SECURE", 1, -1) == "RFBVQF" and Counter("RFBVQF").most_common(1) == [("F", 2)]
assert picked("PERSONALITY", [1, 4, 7, 10]) == ["P", "S", "A", "T"] and all(sorted(w) == sorted("PSAT") for w in ("PAST", "PATS", "SPAT", "TAPS"))
# ---- exam patterns, traps, checkpoint, practice ----
assert [w for w in ("AGENT", "MAGNET", "TENANT", "MEANT") if not can_form(w, "MANAGEMENT")] == ["TENANT"]
assert Counter("TENANT")["T"] == 2 and Counter("MANAGEMENT")["T"] == 1
assert Counter("ASSESSMENT").most_common(2) == [("S", 4), ("E", 2)]
assert sorted("PTREUCOM") == sorted("COMPUTER") and "COMPUTER"[3] == "P"
assert change("LOGIC", 0, 1) == "MOHID" and [ch for ch in "MOHID" if ch in VOWELS] == ["O", "I"]
# ---- section quiz ----
assert [w for w in ("FORMAT", "NATION", "MOTION", "FRAMING") if not can_form(w, "INFORMATION")] == ["FRAMING"] and "G" not in "INFORMATION"
assert Counter("EXCELLENCE")["E"] == 4 and Counter("EXCELLENCE")["C"] == 2 and Counter("EXCELLENCE")["L"] == 2
assert sorted("KROWTEN") == sorted("NETWORK") and "NETWORK"[4] == "O" and change("DATA", 1, -1) == "CBSB"
assert all(sorted(w) == sorted("OWN") for w in ("NOW", "OWN", "WON"))

OBJECTIVES = [("Decide whether a word can be formed from given letters", "using letter counts"),
              ("Find the most frequent letter", "and form words from chosen positions"),
              ("Apply letter-change rules", "vowels one way, consonants another")]
FORMULAS = ["Count the source letters first",
            "Target possible only if every letter is available in the needed quantity",
            "Positions  →  letters  →  rearrange;      several words  →  “more than one”",
            "Letter rules:   mark the vowels first, then apply"]
PATTERNS = [("Cannot be formed", "from ENGINEERING:  GREEN, REIGN, GINGER, ENTER", "count T", "ENTER"),
            ("Cannot be formed", "from MANAGEMENT:  AGENT, MAGNET, TENANT, MEANT", "TENANT needs two Ts", "TENANT"),
            ("Most frequent letter", "ASSESSMENT", "tally", "S  (4 times)"),
            ("Jumbled word", "P, T, R, E, U, C, O, M;   4th letter of the word", "COMPUTER", "P"),
            ("Letter rule", "SECURE:  vowels +1,  consonants −1", "letter by letter", "RFBVQF"),
            ("Words from positions", "1st, 4th, 7th, 10th of PERSONALITY", "P, S, A, T:   PAST, PATS, SPAT, TAPS", "more than one")]
TRAPS = [("Trap 1  ·  ignoring quantity", "Can TENANT be formed from MANAGEMENT?",
          "yes:  T, E, N and A are all present", "TENANT needs two Ts;  there is one",
          "compare counts, not just presence"),
         ("Trap 2  ·  stopping at the first word",
          "The 1st, 4th, 7th and 10th letters of PERSONALITY form a meaningful word.   Which?",
          "PAST, the first word that comes to mind", "also PATS, SPAT, TAPS:  more than one",
          "before choosing a word, check whether the letters make any other")]
PRACTICE_A = [("L1", "Can ENTER be formed from the letters of ENGINEERING?"),
              ("L1", "Which letter appears most often in ASSESSMENT?"),
              ("L1", "The letters P, T, R, E, U, C, O, M form a meaningful word.  What is its 4th letter?"),
              ("L2", "Which of AGENT, MAGNET, TENANT and MEANT cannot be formed from MANAGEMENT?"),
              ("L2", "In SECURE, each vowel is replaced by the next letter and each consonant by the previous letter.  What is the result?"),
              ("L2", "In that result, which letter appears twice?")]
PRACTICE_B = [("L3", "How many meaningful English words can be formed from the 1st, 4th, 7th and 10th letters of PERSONALITY, "
                     "using each letter once?"),
              ("L3", "In LOGIC, each consonant is replaced by the next letter and vowels are unchanged.  How many vowels does the result contain?")]
ANSWERS_A = [("there is no T", "no"),
             ("S, 4 times", "S"),
             ("the word is COMPUTER", "P"),
             ("TENANT needs two Ts", "TENANT")]
ANSWERS_B = [("S → R,  E → F,  C → B,  U → V,  R → Q,  E → F", "RFBVQF"),
             ("RFBVQF", "F"),
             ("P, S, A, T:   PAST, PATS, SPAT, TAPS", "more than one  (4)"),
             ("MOHID:   O and I", "2")]
LENS = [("Recognition cue", "“can be formed”, “cannot be formed”, “most frequent”, “replaced by”, “meaningful word”"),
        ("Target time", "25 seconds"),
        ("Sanity check", "formation:  tick each target letter off the source tally;    rules:  recheck the vowels")]
QUIZ = [["Which word cannot be formed from the letters of INFORMATION?", "(a) FORMAT   (b) NATION   (c) MOTION   (d) FRAMING"],
        ["Which letter appears most often in EXCELLENCE?", "(a) E   (b) L   (c) C   (d) N"],
        ["The letters K, R, O, W, T, E, N form a meaningful word.  What is its 5th letter?", "(a) T   (b) R   (c) O   (d) W"],
        ["In DATA, each vowel becomes the next letter and each consonant the previous letter.  The result?",
         "(a) EBUB   (b) CBSB   (c) CZSZ   (d) EZUZ"],
        ["Using O, W and N once each, how many meaningful English words can be formed?", "(a) 1   (b) 2   (c) 3   (d) 4"]]
QUIZ_KEY = [("INFORMATION has no G", "(d)  FRAMING"),
            ("E 4,   C 2,   L 2", "(a)  E"),
            ("NETWORK:   N E T W O", "(c)  O"),
            ("D → C,   A → B,   T → S,   A → B", "(b)  CBSB"),
            ("NOW,  OWN,  WON", "(c)  3")]


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


class WordFormationAndLetterRulesVideo(LMSScene):
    lesson_title = "Word Formation & Letter Rules"

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
        self.hook_solved()
        self.second_example()
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

    def count_grid(self, labels, rows, gap=0.95, size=BODY):
        """Counts under a row of labels.  rows = [(name, values), ...].
        Returns (labels, (name, values), (name, values), ...)."""
        xs = [RIGHT * k * gap for k in range(len(labels))]
        out = VGroup(VGroup(*[text(str(label), size, INK, BOLD).move_to(x) for label, x in zip(labels, xs)]))
        for r, (name, values) in enumerate(rows):
            vals = VGroup(*[text(str(v), size, FOCUS, BOLD).move_to(x + DOWN * (r + 1) * 0.68) for v, x in zip(values, xs)])
            tag = text(name, SMALL, MUTED)
            tag.next_to(LEFT * gap * 0.75 + DOWN * (r + 1) * 0.68, LEFT, buff=0)
            out.add(VGroup(tag, vals))
        self.no_overlap(out[0], *[row[1] for row in out[1:]])
        self.no_overlap(*out[0], gap=0.02)
        return out

    def word_row(self, word, under, gap=0.9):
        """A word spread out, with a number under each letter.  row[i] = (letter, number)."""
        cells = VGroup()
        for i, (ch, n) in enumerate(zip(word, under)):
            x = RIGHT * (i - (len(word) - 1) / 2) * gap
            cells.add(VGroup(text(ch, 36, INK, BOLD).move_to(x + UP * 0.3), text(str(n), MIN_FONT, MUTED).move_to(x + DOWN * 0.3)))
        self.no_overlap(*cells, gap=0.02)
        return cells

    def change_grid(self, word, result, notes, buff=0.8):
        """Each letter over its replacement, vowels in orange.  Returns (word row, notes, arrows, result row)."""
        cols = [VGroup(text(a, 36, RATIO if a in VOWELS else INK, BOLD), text(note, SMALL, FOCUS, BOLD), text("↓", LABEL, MUTED),
                       text(b, 36, GOOD, BOLD)).arrange(DOWN, buff=0.2) for a, b, note in zip(word, result, notes)]
        VGroup(*cols).arrange(RIGHT, buff=buff)
        rows = VGroup(*[VGroup(*[col[k] for col in cols]) for k in range(4)])
        for row in rows:
            for item in row:
                item.set_y(row.get_center()[1])
        self.no_overlap(*rows)
        for row in rows:
            self.no_overlap(*row, gap=0.02)
        return rows

    # ============================================== 0. INTRO ==========
    # Not the first video: silent breadcrumb, a one-line recap of the previous video, then today's topic.

    def intro(self):
        self.scene_start("S00_intro", title="Intro")

        crumb = self.breadcrumb("Logical Reasoning", "Lesson 2 · Alphabets", "Video 3 of 6")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        recap = VGroup(text("from Video 2  ·  Word Order & Letter Pairs", SMALL, MUTED), pill("the first difference decides;   pairs:  scan both directions", WORD, size=LABEL)).arrange(DOWN, buff=0.25)
        title = fit_width(text("Word Formation & Letter Rules", TITLE, INK, BOLD), SAFE_W - 0.4)
        today = text("today: count before guessing", LABEL, FOCUS)
        block = VGroup(recap, title, today).arrange(DOWN, buff=0.7)
        fit_within(block, SAFE_W, SAFE_H - crumb.height - 0.9)
        block.next_to(crumb, DOWN, buff=0.7)
        self.no_overlap(crumb, recap, title, today)
        self.validator.check_in_frame(VGroup(crumb, block))

        n = self.narrate(
            id="intro_01",
            text="In the last video, the first differing letter decided dictionary order, and letter pairs were scanned in "
                 "both directions.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.at_word(n, "decided")
        self.play(FadeIn(recap[0]))
        self.at_word(n, "pairs")
        self.play(FadeIn(recap[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="intro_02",
            text="This video covers word formation and letter rules: counting before guessing.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "covers")
        self.play(FadeIn(title, shift=UP * 0.1))
        self.at_word(n, "counting")
        self.play(FadeIn(today, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_intro")

    # ============================================== 1. HOOK ==========

    def hook(self):
        self.scene_start("S01_hook", title="Hook")

        head = self.heading("Can ENGINEERING make ENTER?")
        words = VGroup(pill("ENGINEERING", WORD, size=BODY), text("→", BODY, MUTED), pill("ENTER  ?", FOCUS, size=BODY)).arrange(RIGHT, buff=0.5)
        likely = text("it looks likely:  E, N, E, R are all there", LABEL, MUTED)
        grid = self.count_grid("ENTR", [("ENTER needs", [2, 1, 1, 1]), ("ENGINEERING has", [3, 3, 0, 1])])
        verdict = VGroup(pill("no T:  the answer is no", BAD, size=LABEL), pill("count before guessing", GOOD, size=LABEL)).arrange(RIGHT, buff=0.6)
        self.stack(head, [words, likely, grid, verdict], buff=0.65, top=0.7)
        self.no_overlap(*words)
        self.no_overlap(*verdict)

        n = self.narrate(
            id="hook_01",
            text="Can the letters of ENGINEERING make the word ENTER?",
            voice="default",
            subtitle=True,
            pause_after=3.0,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "letters")
        self.play(FadeIn(words[0], shift=UP * 0.1))
        self.at_word(n, "make")
        self.play(FadeIn(words[1:], shift=UP * 0.1))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="hook_02",
            text="It looks likely: E, N, E and R are all there.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "likely")
        self.play(FadeIn(likely, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_03",
            text="An anagram checker in code would not guess; it would count.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "count")
        self.play(FadeIn(grid[0]), FadeIn(grid[1], shift=UP * 0.1), FadeIn(grid[2], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_04",
            text="ENGINEERING has no T. The answer is no, in one glance at the counts.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "no")
        self.play(VGroup(grid[0][2], grid[1][1][2], grid[2][1][2]).animate.set_color(BAD))
        self.at_word(n, "answer")
        self.play(FadeIn(verdict[0], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_05",
            text="Every question in this video is solved by counting before guessing.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "counting")
        self.play(FadeIn(verdict[1], scale=1.03))
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
            text="One: decide whether a word can be formed from given letters, using letter counts.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "decide")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "counts")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="objectives_03",
            text="Two: find the most frequent letter, and form words from chosen positions.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "frequent")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "positions")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="objectives_04",
            text="Three: apply letter-change rules, with vowels going one way and consonants another.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "apply")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "vowels")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_objectives")

    # ============================================== 3. WHY THIS SECTION ==========

    def why_this_section(self):
        self.scene_start("S03_why_this_section", title="Why This Section")

        head = self.heading("Why this section")
        looks = pill("they look like vocabulary, but are counting problems", WORD, size=LABEL)
        fast = pill("a letter tally answers most of them in seconds", GOOD, size=LABEL)
        self.stack(head, [looks, fast], buff=1.2, top=1.5)

        n = self.narrate(
            id="why_this_section_01",
            text="Word-formation and letter-rule questions look like vocabulary, but are counting problems.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "counting")
        self.play(FadeIn(looks, scale=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="why_this_section_02",
            text="A letter tally answers most of them in seconds.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "tally")
        self.play(FadeIn(fast, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_why_this_section")

    # ============================================== 4. THE CONCEPT JOURNEY ==========

    def concept_journey(self):
        self.scene_start("S04_concept_journey", title="The Concept Journey")

        head = self.heading("Steps 1 to 3  ·  count the source, check the target")
        source = pill("ENGINEERING", WORD, size=BODY)
        grid = self.count_grid([ch for ch, _ in tally("ENGINEERING")], [("count", [n for _, n in tally("ENGINEERING")])])
        top = VGroup(source, grid).arrange(RIGHT, buff=1.6)
        check = pill("a word can be formed only if every letter it needs is available in at least that quantity", FOCUS, size=SMALL)
        out = text("one missing or short letter rules it out", LABEL, BAD, BOLD)
        most = text("the tally also answers “which letter appears most often” directly", LABEL, INK)
        self.stack(head, [top, check, out, most], buff=0.7, top=0.8)
        self.no_overlap(source, grid)

        n = self.narrate(
            id="concept_journey_01",
            text="Step one: count the source. Write each letter of the source word with its count.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "one")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "source")
        self.play(FadeIn(source, shift=UP * 0.1))
        self.at_word(n, "count", occurrence=2)
        self.play(FadeIn(grid))
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_journey_02",
            text="Step two: check the target. A word can be formed only if every letter it needs is available in at least "
                 "that quantity.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "two")
        self.play(Indicate(head, color=FOCUS, scale_factor=1.03))
        self.at_word(n, "formed")
        self.play(FadeIn(check, scale=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_journey_03",
            text="One missing or short letter rules it out.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "missing")
        self.play(FadeIn(out, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_journey_04",
            text="Step three: frequency questions. The tally answers, which letter appears most often, directly.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "three")
        self.play(Indicate(head, color=FOCUS, scale_factor=1.03))
        self.at_word(n, "tally")
        self.play(FadeIn(most, shift=UP * 0.1))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Step 4  ·  words from positions")
        row = self.word_row("PERSONALITY", range(1, 12))
        got = VGroup(text("positions 1, 4, 7, 10", LABEL, MUTED), pill("P   S   A   T", FOCUS, size=BODY), text("then rearrange", LABEL, MUTED))\
            .arrange(RIGHT, buff=0.5)
        more = VGroup(text("more than one meaningful word is possible?", LABEL, INK), pill("answer “more than one”, when it is offered", RATIO, size=LABEL))\
            .arrange(DOWN, buff=0.3)
        self.stack(head, [row, got, more], buff=0.9, top=0.9)
        self.no_overlap(*got)

        n = self.narrate(
            id="concept_journey_05",
            text="Step four: words from positions. Pick the stated positions, write those letters, then rearrange.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "four")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "Pick")
        self.play(FadeIn(row))
        self.at_word(n, "write")
        self.play(VGroup(row[0], row[3], row[6], row[9]).animate.set_color(FOCUS), FadeIn(got[:2], shift=UP * 0.1))
        self.at_word(n, "rearrange")
        self.play(FadeIn(got[2], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_journey_06",
            text="If more than one meaningful word is possible, the answer is, more than one, when that option is offered.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "possible")
        self.play(FadeIn(more[0], shift=UP * 0.1))
        self.at_word(n, "answer")
        self.play(FadeIn(more[1], shift=UP * 0.1))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Steps 5 and 6  ·  letter-change rules")
        rule = pill("a typical rule:  vowels move to the next letter,  consonants to the previous one", FOCUS, size=SMALL)
        grid = self.change_grid("SECURE", change("SECURE", 1, -1), ["−1", "+1", "−1", "+1", "−1", "+1"])
        mark = VGroup(pill("classify once:  mark the vowels first", RATIO, size=LABEL), text("A   E   I   O   U", BODY, RATIO, BOLD),
                      text("most errors:  a vowel treated as a consonant", SMALL, BAD, BOLD)).arrange(DOWN, buff=0.35)
        row = VGroup(grid, mark).arrange(RIGHT, buff=1.2)
        self.stack(head, [rule, row], buff=0.7, top=0.6)
        self.no_overlap(grid, mark)

        n = self.narrate(
            id="concept_journey_07",
            text="Step five: letter-change rules. A typical rule: vowels move to the next letter, consonants to the "
                 "previous one.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "five")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "typical")
        self.play(FadeIn(rule, scale=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_journey_08",
            text="Apply it letter by letter, then answer the question on the new string.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Apply")
        self.play(FadeIn(grid[0]), FadeIn(grid[1], shift=UP * 0.1), FadeIn(grid[2], shift=UP * 0.1))
        self.at_word(n, "new")
        self.play(FadeIn(grid[3]))
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_journey_09",
            text="Step six: classify once. Mark the vowels, A, E, I, O and U, before applying any rule; most errors are a "
                 "vowel treated as a consonant.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "six")
        self.play(FadeIn(mark[0], shift=UP * 0.1))
        self.at_word(n, "vowels")
        self.play(FadeIn(mark[1], shift=UP * 0.1))
        self.at_word(n, "errors")
        self.play(FadeIn(mark[2], shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_concept_journey")

    # ============================================== 5. RULE BOX ==========

    def rule_box(self):
        self.scene_start("S05_rule_box", title="Rule Box")

        head = self.heading("Rule box", GOOD)
        lines = VGroup(*[text(f, LABEL, INK) for f in FORMULAS]).arrange(DOWN, buff=0.5, aligned_edge=LEFT)
        fit_width(lines, SAFE_W - 1.6)
        box = self.card(lines, width=SAFE_W - 0.4, color=GOOD, pad=0.5)
        self.stack(head, [box], top=0.8)

        n = self.narrate(
            id="rule_box_01",
            text="Here is the rule box. Count the source letters first.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "box")
        self.play(FadeIn(box[0]))
        self.at_word(n, "Count")
        self.play(FadeIn(lines[0], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="rule_box_02",
            text="The target is possible only if every letter is available in the needed quantity.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "possible")
        self.play(FadeIn(lines[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="rule_box_03",
            text="Positions give letters, which you rearrange; several words mean the answer, more than one.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Positions")
        self.play(FadeIn(lines[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="rule_box_04",
            text="For letter rules, mark the vowels first, then apply.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "mark")
        self.play(FadeIn(lines[3], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_rule_box")

    # ============================================== 6. SHORT TRICK ==========

    def short_trick(self):
        self.scene_start("S06_short_trick", title="Short Trick")

        head = self.heading("Short trick", RATIO)
        form = VGroup(pill("formation", WORD, size=LABEL), text("tally the source, then tick off the target's letters", LABEL, INK, BOLD),
                      text("a single shortfall rules the word out", SMALL, BAD, BOLD))
        form[1].next_to(form[0], RIGHT, buff=0.5)
        form[2].next_to(form[1], DOWN, buff=0.2, aligned_edge=LEFT)
        rules = VGroup(pill("letter rules", RATIO, size=LABEL), text("circle the vowels first", LABEL, INK, BOLD)).arrange(RIGHT, buff=0.5)
        self.stack(head, [form, rules], buff=1.1, top=1.3, align=LEFT)
        self.no_overlap(*form)
        self.no_overlap(*rules)

        n = self.narrate(
            id="short_trick_01",
            text="The short trick: tally the source letters, then tick off the target's letters; a single shortfall rules "
                 "the word out.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "tally")
        self.play(FadeIn(form[:2], shift=UP * 0.1))
        self.at_word(n, "shortfall")
        self.play(FadeIn(form[2], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="short_trick_02",
            text="For letter rules, circle the vowels first.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "rules")
        self.play(FadeIn(rules[0], shift=UP * 0.1))
        self.at_word(n, "circle")
        self.play(FadeIn(rules[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_short_trick")

    # ============================================== 7. THE ANALOGY - A RECIPE AND A PANTRY ==========

    def analogy(self):
        self.scene_start("S07_analogy", title="The Analogy - A Recipe and a Pantry")

        head = self.heading("A recipe checked against a pantry")
        grid = self.count_grid(["eggs", "flour", "milk"], [("the recipe needs", [2, 1, 1]), ("the pantry has", [1, 3, 2])], gap=1.7)
        cannot = text("two eggs needed, one in the pantry:  the dish cannot be made", LABEL, BAD, BOLD)
        however = text("however many other ingredients are there", SMALL, MUTED)
        stops = VGroup(text("where the analogy stops", SMALL, BAD, BOLD), text("recipes allow substitutes;  letters do not", SMALL, INK))\
            .arrange(DOWN, buff=0.14, aligned_edge=LEFT)
        self.stack(head, [grid, cannot, however, stops], buff=0.6, top=0.8)
        self.no_overlap(*stops)

        n = self.narrate(
            id="analogy_01",
            text="Forming a word is checking a recipe against a pantry.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "recipe")
        self.play(FadeIn(grid[0]), FadeIn(grid[1], shift=UP * 0.1))
        self.at_word(n, "pantry")
        self.play(FadeIn(grid[2]))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_02",
            text="If the recipe needs two eggs and the pantry has one, the dish cannot be made, however many other "
                 "ingredients are there.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "eggs")
        self.play(VGroup(grid[0][0], grid[1][1][0], grid[2][1][0]).animate.set_color(BAD))
        self.at_word(n, "cannot")
        self.play(FadeIn(cannot, shift=UP * 0.1))
        self.at_word(n, "however")
        self.play(FadeIn(however, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_03",
            text="Where the analogy stops: recipes allow substitutes. Letters do not.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "stops")
        self.play(FadeIn(stops[0], shift=RIGHT * 0.2))
        self.at_word(n, "substitutes")
        self.play(FadeIn(stops[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S07_analogy")

    # ============================================== 8. WORKED EXAMPLE - CLOSING THE HOOK ==========

    def hook_solved(self):
        self.scene_start("S08_hook_solved", title="Worked Example - Closing the Hook")

        head = self.heading("Worked example: closing the hook")
        grid = self.count_grid("ENGIRT", [("ENGINEERING has", [3, 3, 2, 2, 1, 0]), ("ENTER needs", [2, 1, "–", "–", 1, 1])])
        verdict = pill("ENGINEERING has no T:   ENTER cannot be formed", BAD, size=LABEL)
        can = VGroup(text("these can:", LABEL, MUTED), pill("GREEN", GOOD, size=LABEL), pill("REIGN", GOOD, size=LABEL), pill("GINGER", GOOD, size=LABEL))\
            .arrange(RIGHT, buff=0.4)
        self.stack(head, [grid, verdict, can], buff=0.9, top=0.9)
        self.no_overlap(*can)

        n = self.narrate(
            id="hook_solved_01",
            text="The counts for ENGINEERING: E three, N three, G two, I two, R one, and T zero.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "counts")
        self.play(FadeIn(grid[0]), FadeIn(grid[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_solved_02",
            text="ENTER needs two Es, one N, one T and one R.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "needs")
        self.play(FadeIn(grid[2]))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_solved_03",
            text="ENGINEERING has no T, so ENTER cannot be formed.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "no")
        self.play(VGroup(grid[0][5], grid[1][1][5], grid[2][1][5]).animate.set_color(BAD))
        self.at_word(n, "cannot")
        self.play(FadeIn(verdict, scale=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_solved_04",
            text="GREEN, REIGN and GINGER can.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "GREEN")
        self.play(FadeIn(can[:2], shift=UP * 0.1))
        self.at_word(n, "REIGN")
        self.play(FadeIn(can[2], shift=UP * 0.1))
        self.at_word(n, "GINGER")
        self.play(FadeIn(can[3], shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S08_hook_solved")

    # ============================================== 9. A SECOND WORKED EXAMPLE - A LETTER-CHANGE RULE ==========

    def second_example(self):
        self.scene_start("S09_second_example", title="A Second Worked Example - A Letter-Change Rule")

        head = self.heading("A second worked example: a letter-change rule")
        ask = VGroup(text("In SECURE, each vowel is replaced by the next letter and each consonant by the previous letter.", SMALL, INK),
                     text("Which letter appears twice in the result?", LABEL, FOCUS, BOLD)).arrange(DOWN, buff=0.2)
        grid = self.change_grid("SECURE", "RFBVQF", ["−1", "+1", "−1", "+1", "−1", "+1"])
        result = VGroup(pill("result:  RFBVQF", WORD, size=LABEL), pill("F appears twice", GOOD, size=LABEL)).arrange(RIGHT, buff=0.6)
        self.stack(head, [ask, grid, result], buff=0.6, top=0.6)
        self.no_overlap(*result)

        n = self.narrate(
            id="second_example_01",
            text="Each vowel in SECURE is replaced by the next letter, and each consonant by the previous letter. Which "
                 "letter appears twice in the result?",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "vowel")
        self.play(FadeIn(ask[0], shift=UP * 0.1), FadeIn(grid[0], shift=UP * 0.1))
        self.at_word(n, "twice")
        self.play(FadeIn(ask[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_02",
            text="Step one: S becomes R, E becomes F, C becomes B, U becomes V, R becomes Q, and E becomes F.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "one")
        self.play(FadeIn(grid[1]), FadeIn(grid[2], shift=UP * 0.1))
        self.at_word(n, "becomes")
        self.play(FadeIn(grid[3][0], shift=UP * 0.1))
        self.at_word(n, "becomes", occurrence=2)
        self.play(FadeIn(grid[3][1], shift=UP * 0.1))
        self.at_word(n, "becomes", occurrence=3)
        self.play(FadeIn(grid[3][2], shift=UP * 0.1))
        self.at_word(n, "becomes", occurrence=4)
        self.play(FadeIn(grid[3][3], shift=UP * 0.1))
        self.at_word(n, "becomes", occurrence=5)
        self.play(FadeIn(grid[3][4], shift=UP * 0.1))
        self.at_word(n, "becomes", occurrence=6)
        self.play(FadeIn(grid[3][5], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_03",
            text="Step two, the result: R F B V Q F.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "result")
        self.play(FadeIn(result[0], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_04",
            text="Step three: F appears twice, so the answer is F.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "twice")
        self.play(VGroup(grid[3][1], grid[3][5]).animate.set_color(FOCUS))
        self.at_word(n, "answer")
        self.play(FadeIn(result[1], scale=1.03))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S09_second_example")

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
            text="Cannot be formed: from ENGINEERING, out of GREEN, REIGN, GINGER and ENTER, count the T: ENTER.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "formed")
        self.play(FadeIn(rows[0][:3], shift=RIGHT * 0.2))
        self.at_word(n, "count")
        self.play(FadeIn(rows[0][3], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_03",
            text="Cannot be formed, again: from MANAGEMENT, TENANT needs two Ts, so TENANT.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "again")
        self.play(FadeIn(rows[1][:3], shift=RIGHT * 0.2))
        self.at_word(n, "so")
        self.play(FadeIn(rows[1][3], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_04",
            text="Most frequent letter: a tally of ASSESSMENT gives S, four times.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "frequent")
        self.play(FadeIn(rows[2][:3], shift=RIGHT * 0.2))
        self.at_word(n, "gives")
        self.play(FadeIn(rows[2][3], shift=LEFT * 0.1))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Exam patterns  ·  part 2")
        table, rows = self.pattern_table(head, PATTERNS[3:])

        n = self.narrate(
            id="exam_patterns_05",
            text="Jumbled word: P, T, R, E, U, C, O, M make COMPUTER, whose fourth letter is P.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "Jumbled")
        self.play(FadeIn(rows[0][:3], shift=RIGHT * 0.2))
        self.at_word(n, "fourth")
        self.play(FadeIn(rows[0][3], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_06",
            text="Letter rule: SECURE, with vowels plus one and consonants minus one, letter by letter, gives R F B V Q F.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "rule")
        self.play(FadeIn(rows[1][:3], shift=RIGHT * 0.2))
        self.at_word(n, "gives")
        self.play(FadeIn(rows[1][3], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_07",
            text="Words from positions: the first, fourth, seventh and tenth letters of PERSONALITY are P, S, A, T, which "
                 "make more than one word.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "positions")
        self.play(FadeIn(rows[2][:3], shift=RIGHT * 0.2))
        self.at_word(n, "more")
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
            text="Trap one: ignoring quantity.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "quantity")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_02",
            text="Can TENANT be formed from MANAGEMENT?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "formed")
        self.play(FadeIn(ask, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_03",
            text="The wrong instinct: yes, since T, E, N and A are all present.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "instinct")
        self.play(FadeIn(wrong, shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_04",
            text="Correct: TENANT needs two Ts, and MANAGEMENT has one, so no.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "needs")
        self.play(FadeIn(right, shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_05",
            text="The rule: compare counts, not just presence.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "compare")
        self.play(FadeIn(rule, scale=1.03))
        self.wait_for_narration(n)
        self.clear_stage()

        head, ask, wrong, right, rule = self.show_trap(TRAPS[1])

        n = self.narrate(
            id="traps_06",
            text="Trap two: stopping at the first word.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "stopping")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_07",
            text="The first, fourth, seventh and tenth letters of PERSONALITY form a meaningful word. Which?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "letters")
        self.play(FadeIn(ask, shift=UP * 0.1))
        self.at_word(n, "Which")
        self.play(Indicate(ask, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_08",
            text="The wrong instinct: PAST, the first word that comes to mind.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "instinct")
        self.play(FadeIn(wrong, shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_09",
            text="Correct: P, S, A, T also make PATS, SPAT and TAPS, so the answer is, more than one.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "also")
        self.play(FadeIn(right, shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_10",
            text="The rule: before choosing a word, check whether the letters make any other.",
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
        ask = pill("Which letter appears most often in ASSESSMENT?", FOCUS, size=BODY)
        grid = self.count_grid([ch for ch, _ in tally("ASSESSMENT")], [("count", [n for _, n in tally("ASSESSMENT")])])
        answer = pill("S,  4 times", GOOD, size=BODY)
        self.stack(head, [ask, grid, answer], buff=0.9, top=0.9)

        n = self.narrate(
            id="checkpoint_01",
            text="Your turn. Which letter appears most often in ASSESSMENT?",
            voice="default",
            subtitle=True,
            pause_after=10.0,
        )
        self.at_word(n, "turn")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "letter")
        self.play(FadeIn(ask, scale=1.03))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="checkpoint_02",
            text="The tally: S four times, E twice, and the others once each. The answer is S.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "tally")
        self.play(FadeIn(grid))
        self.at_word(n, "answer")
        self.play(VGroup(grid[0][1], grid[1][1][1]).animate.set_color(GOOD), FadeIn(answer, shift=UP * 0.1))
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
            text="Level one, question one: can ENTER be formed from the letters of ENGINEERING? Question two: which letter "
                 "appears most often in ASSESSMENT? Question three: the letters P, T, R, E, U, C, O, M form a meaningful "
                 "word; what is its fourth letter?",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "ENTER")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "ASSESSMENT")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.at_word(n, "meaningful")
        self.play(FadeIn(rows[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="practice_02",
            text="Level two, question four: which of AGENT, MAGNET, TENANT and MEANT cannot be formed from MANAGEMENT? "
                 "Question five: in SECURE, each vowel is replaced by the next letter and each consonant by the previous "
                 "letter; what is the result? Question six: in that result, which letter appears twice?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "AGENT")
        self.play(FadeIn(rows[3], shift=RIGHT * 0.2))
        self.at_word(n, "SECURE")
        self.play(FadeIn(rows[4], shift=RIGHT * 0.2))
        self.at_word(n, "twice")
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
            text="Level three, question seven: how many meaningful English words can be formed from the first, fourth, "
                 "seventh and tenth letters of PERSONALITY, using each letter once? Question eight: in LOGIC, each "
                 "consonant is replaced by the next letter and vowels are unchanged; how many vowels does the result "
                 "contain?",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "PERSONALITY")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "LOGIC")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="practice_05",
            text="Pause again and solve these two.",
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
            text="One: there is no T, so no.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "there")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "so")
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_02",
            text="Two: S, four times.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "times")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2), FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_03",
            text="Three: the word is COMPUTER, so P.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "COMPUTER")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "so")
        self.play(FadeIn(rows[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_04",
            text="Four: TENANT, which needs two Ts.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "needs")
        self.play(FadeIn(rows[3][:2], shift=RIGHT * 0.2), FadeIn(rows[3][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Answer key  ·  5 to 8", GOOD)
        table, rows = self.answer_table(head, ANSWERS_B, 5)

        n = self.narrate(
            id="answers_05",
            text="Five: S to R, E to F, C to B, U to V, R to Q and E to F give R F B V Q F.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "to")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "give")
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_06",
            text="Six: in that result, F appears twice.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "result")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "twice")
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_07",
            text="Seven: P, S, A, T make PAST, PATS, SPAT and TAPS: more than one, four in all.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "make")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "more")
        self.play(FadeIn(rows[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_08",
            text="Eight: the result is M O H I D, with the vowels O and I, so two.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "result")
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
            text="Recognise and move. The recognition cue: the words, can be formed, cannot be formed, most frequent, "
                 "replaced by, or meaningful word.",
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
            text="The target time: twenty-five seconds.",
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
            text="The sanity check: for formation, tick each target letter off the source tally; for rules, recheck the "
                 "vowels.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "sanity")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "tick")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S15_exam_lens")

    # ============================================== 16. QUICK REVISION AND SUMMARY ==========

    def summary(self):
        self.scene_start("S16_summary", title="Quick Revision and Summary")

        head = self.heading("Quick revision")
        first = pill("count before guessing", FOCUS, size=BODY)
        points = VGroup(text("a word can be formed only if every letter is available in the needed quantity", LABEL, INK, BOLD),
                        text("letter rules:  mark the vowels first", LABEL, INK, BOLD),
                        text("letters that make more than one word:  say so", LABEL, INK, BOLD)).arrange(DOWN, buff=0.45, aligned_edge=LEFT)
        box = VGroup(pill("tally", GOOD, size=SMALL), pill("quantity check", GOOD, size=SMALL), pill("mark vowels", GOOD, size=SMALL),
                     pill("more than one word?", GOOD, size=SMALL)).arrange(RIGHT, buff=0.3)
        self.stack(head, [first, points, box], buff=0.8, top=0.8)
        self.no_overlap(*points)
        self.no_overlap(*box)

        n = self.narrate(
            id="summary_01",
            text="Count before guessing.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "Count")
        self.play(FadeIn(first, scale=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_02",
            text="A word can be formed only if every letter is available in the needed quantity.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "formed")
        self.play(FadeIn(points[0], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_03",
            text="For letter rules, mark the vowels first.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "mark")
        self.play(FadeIn(points[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_04",
            text="When letters make more than one word, say so.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "more")
        self.play(FadeIn(points[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_05",
            text="The rule box in one line: tally; quantity check; mark vowels; and ask, more than one word?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "line")
        self.play(FadeIn(box[0], shift=UP * 0.1))
        self.at_word(n, "quantity")
        self.play(FadeIn(box[1], shift=UP * 0.1))
        self.at_word(n, "vowels")
        self.play(FadeIn(box[2], shift=UP * 0.1))
        self.at_word(n, "ask")
        self.play(FadeIn(box[3], shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S16_summary")

    # ============================================== 17. SECTION QUIZ ==========

    def section_quiz(self):
        self.scene_start("S17_section_quiz", title="Section Quiz")

        head = self.heading("Section quiz")
        rules = VGroup(pill("5 questions", WORD, size=BODY), pill("4 minutes", WORD, size=BODY), pill("+3 correct", GOOD, size=BODY),
                       pill("−1 wrong", BAD, size=BODY)).arrange(RIGHT, buff=0.4)
        gate = VGroup(VGroup(pill("12 or more out of 15", GOOD, size=LABEL), text("move on", BODY, GOOD, BOLD)).arrange(RIGHT, buff=0.5),
                      VGroup(pill("below 12", BAD, size=LABEL), text("replay the Traps segment, then retry", BODY, INK, BOLD)).arrange(RIGHT, buff=0.5))            .arrange(DOWN, buff=0.6, aligned_edge=LEFT)
        self.stack(head, [rules, gate], buff=1.1, top=1.1)
        self.no_overlap(*rules)
        self.no_overlap(*gate)

        n = self.narrate(
            id="section_quiz_01",
            text="Now the section quiz: five questions in four minutes, with plus three for a correct answer and minus one "
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
            text="Twelve or more out of fifteen: move on. Below twelve: replay the traps segment, then retry.",
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
                                        [[str(0 + i + 1)] + list(row) for i, row in enumerate(QUIZ[0:3])], [0.8, 7.4, 5.0], room=1.3)
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

        head = self.heading("Section quiz  ·  questions 4 to 5")
        table, rows = self.placed_table(head, ["#", "Question", "Options"],
                                        [[str(3 + i + 1)] + list(row) for i, row in enumerate(QUIZ[3:5])], [0.8, 7.4, 5.0], room=1.3)
        for row in rows:
            row[0].set_color(MUTED)

        n = self.narrate(
            id="section_quiz_05",
            text="And here are questions four and five.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "four")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "five")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
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
        nxt = self.breadcrumb("Next", "Video 4 · Letter Series")
        nxt.next_to(table, DOWN, buff=0.6)
        self.no_overlap(table, nxt)
        self.validator.check_in_frame(VGroup(head, table, nxt))

        n = self.narrate(
            id="section_quiz_07",
            text="The answers. One: INFORMATION has no G, so FRAMING: option d.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "no")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "option")
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="section_quiz_08",
            text="Two: E four times, C twice and L twice, so E: option a.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "times")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "option")
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="section_quiz_09",
            text="Three: the word is NETWORK, N, E, T, W, O, so the fifth letter is O: option c.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "NETWORK")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "option")
        self.play(FadeIn(rows[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="section_quiz_10",
            text="Four: D to C, A to B, T to S and A to B: option b.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "to")
        self.play(FadeIn(rows[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "option")
        self.play(FadeIn(rows[3][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="section_quiz_11",
            text="Five: NOW, OWN and WON, three words: option c.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "NOW")
        self.play(FadeIn(rows[4][:2], shift=RIGHT * 0.2))
        self.at_word(n, "option")
        self.play(FadeIn(rows[4][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="section_quiz_12",
            text="Next: letter series.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Next")
        self.play(FadeIn(nxt, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S17_section_quiz")

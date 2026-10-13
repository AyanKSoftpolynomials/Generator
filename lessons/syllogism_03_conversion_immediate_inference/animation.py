"""
animation.py for the LMS video generator.

Course : Pre-C-CAT - Section A - Logical Reasoning
Video  : Lesson 8 - Syllogism - 03 - Conversion & Immediate Inference

Source script:
  C:\\Scripts\\Section A\\Sessions 5-9 - Mathematical Operators, Symbols, Syllogism\\Lesson 8 - Syllogism\\03 - Conversion & Immediate Inference.pdf

Built on the golden-reference pattern:
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``;
  * layouts stacked with next_to and guarded with ``no_overlap``; nothing is
    ever animated onto or into another box.

Lesson 8, Video 2 of 7 (file 03 in its folder).
Not the first video: a silent breadcrumb, a one-line recap of Video 1, then today's topic.
The narration follows the script section by section and ends with the Section Quiz and its answer key.
Each conversion rule is shown with the Venn diagram that explains it (first set blue, second set orange).
Every question in the script was decided again in the data block by testing all possible diagrams,
with every named category having at least one member; all the script's answers are correct.
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

from itertools import product


def All(a, b):
    return ("all", a, b)


def No(a, b):
    return ("no", a, b)


def Some(a, b):
    return ("some", a, b)


def SomeNot(a, b):
    return ("some not", a, b)


OPPOSITE = {"all": "some not", "some not": "all", "no": "some", "some": "no"}


def denied(statement):
    """The opposite statement: exactly one of the two is true in any diagram."""
    kind, a, b = statement
    return (OPPOSITE[kind], a, b)


def consistent(statements):
    """Can one diagram make every statement true?  Every category named must have at least one member."""
    names = sorted({name for _, a, b in statements for name in (a, b)})
    spots = [dict(zip(names, bits)) for bits in product((True, False), repeat=len(names))]
    for kind, a, b in statements:
        if kind == "all":
            spots = [s for s in spots if not (s[a] and not s[b])]
        elif kind == "no":
            spots = [s for s in spots if not (s[a] and s[b])]
    for kind, a, b in statements:
        if kind == "some" and not any(s[a] and s[b] for s in spots):
            return False
        if kind == "some not" and not any(s[a] and not s[b] for s in spots):
            return False
    return all(any(s[name] for s in spots) for name in names)


def follows(statements, conclusion):
    """True in every diagram the statements allow."""
    return not consistent(list(statements) + [denied(conclusion)])


def possible(statements, conclusion):
    """True in at least one diagram the statements allow."""
    return consistent(list(statements) + [conclusion])


def either(statements, first, second):
    """The exam's either-or: both conclusions are about the same two terms, neither follows alone,
    and no diagram makes both false."""
    return ({first[1], first[2]} == {second[1], second[2]}
            and not follows(statements, first) and not follows(statements, second)
            and not consistent(list(statements) + [denied(first), denied(second)]))


def verdict(statements, first, second):
    """"both", "only I", "only II", "either" or "neither"."""
    one, two = follows(statements, first), follows(statements, second)
    if one and two:
        return "both"
    if one:
        return "only I"
    if two:
        return "only II"
    return "either" if either(statements, first, second) else "neither"


def read(line):
    """A statement written in words, such as "Some A are not B", as a tuple."""
    import re
    m = re.fullmatch(r"(All|No|Some) (\w+) (?:are|is)( not)? (\w+)", line.strip().rstrip("."))
    kind = m.group(1).lower() + (" not" if m.group(3) else "")
    return (kind, m.group(2), m.group(4))


def judge(statements, first, second):
    """The five-way answer for statements and conclusions written in words."""
    return verdict([read(s) for s in statements], read(first), read(second))


assert read("Some A are not B") == SomeNot("A", "B") and read("No A is B") == No("A", "B")
assert consistent([All("x", "y")]) and not consistent([All("x", "y"), No("x", "y")])
assert follows([All("x", "y")], Some("y", "x")) and not follows([All("x", "y")], All("y", "x"))

# ---- the four conversion rules, the implications and the opposites ----
assert follows([All("A", "B")], Some("B", "A")) and not follows([All("A", "B")], All("B", "A"))
assert follows([No("A", "B")], No("B", "A")) and follows([Some("A", "B")], Some("B", "A"))
assert not follows([SomeNot("A", "B")], SomeNot("B", "A")) and possible([SomeNot("A", "B")], All("B", "A"))
assert follows([All("A", "B")], Some("A", "B")) and follows([No("A", "B")], SomeNot("A", "B")) and follows([No("A", "B")], SomeNot("B", "A"))
for kind_ in (All, No, Some, SomeNot):
    assert not possible([kind_("A", "B")], denied(kind_("A", "B")))
# ---- hook and worked examples ----
assert judge(["All integers are numbers"], "Some numbers are integers", "All numbers are integers") == "only I"
assert judge(["Some files are archives"], "All files are archives", "Some files are not archives") == "either"
# ---- exam patterns: statement, I, II, answer ----
PATTERNS = [["All A are B", "Some B are A", "All B are A", "only I"],
            ["No A is B", "No B is A", "Some B are not A", "both"],
            ["Some A are B", "Some B are A", "No A is B", "only I"],
            ["Some A are B", "All A are B", "Some A are not B", "either"],
            ["Some A are not B", "Some A are B", "No A is B", "either"],
            ["No A is B", "Some A are B", "All B are A", "neither"]]
for given_, one_, two_, answer_ in PATTERNS:
    assert judge([given_], one_, two_) == answer_
# ---- traps, checkpoint, practice ----
assert not follows([read("Some cups are not plates")], read("Some plates are not cups"))
ASKED = [("All A are B", "Some B are A", "All B are A", "only I"), ("No A is B", "No B is A", "Some B are not A", "both"),
         ("Some A are B", "Some B are A", "No A is B", "only I"), ("Some A are B", "All A are B", "Some A are not B", "either"),
         ("All A are B", "Some A are B", "Some A are not B", "only I"), ("Some A are not B", "Some A are B", "No A is B", "either"),
         ("Some A are not B", "Some B are not A", "All B are A", "either"), ("No A is B", "Some A are B", "All B are A", "neither")]
for given_, one_, two_, answer_ in ASKED:
    assert judge([given_], one_, two_) == answer_
assert not possible([No("A", "B")], Some("A", "B")) and not possible([No("A", "B")], All("B", "A"))
PRACTICE_A = [("L1" if i < 3 else "L2", f"{given}.          I.  {one}          II.  {two}") for i, (given, one, two, _) in enumerate(ASKED[:6])]
PRACTICE_B = [("L3", f"{given}.          I.  {one}          II.  {two}") for given, one, two, _ in ASKED[6:]]
# ---- section quiz ----
SET = [("All A are B", "Some B are A", "All B are A", "only I"), ("No A is B", "No B is A", "Some A are not B", "both"),
       ("Some A are B", "All A are B", "Some A are not B", "either"), ("Some A are not B", "Some B are not A", "All B are A", "either"),
       ("No A is B", "Some A are B", "All B are A", "neither")]
for given_, one_, two_, answer_ in SET:
    assert judge([given_], one_, two_) == answer_

OBJECTIVES = [("Convert each statement type correctly", "and know which one cannot be converted"),
              ("Use implications", "All → Some,   and   No → Some … not"),
              ("Answer one-statement questions with two conclusions", "including either-or")]
FORMULAS = ["All A are B   →   Some B are A     (and Some A are B)",
            "No A is B   →   No B is A     (and Some A are not B,  Some B are not A)",
            "Some A are B   →   Some B are A",
            "Some A are not B   →   no conversion",
            "Opposites are definitely false:   All ↔ Some not        No ↔ Some"]
TRAPS = [("Trap 1  ·  converting “some … not”", "Some cups are not plates.     Does “Some plates are not cups” follow?",
          "“yes, by swapping”", "every plate might be a cup:  does not follow",
          "“Some A are not B” has no conversion"),
         ("Trap 2  ·  missing the either-or in one-statement questions", "Some A are not B.        I.  Some A are B        II.  No A is B",
          "neither follows, so “neither”", "same pair:  one of Some / No must be true:  either",
          "after rejecting both, check for Some / No or All / Some-not on the same terms")]
ANSWERS_A = [("All converts to Some", "only I"),
             ("No converts to No;   B exists, so some B are not A", "both"),
             ("Some converts to Some;   II contradicts the statement", "only I"),
             ("the same terms, and one must hold", "either")]
ANSWERS_B = [("II contradicts the statement", "only I"),
             ("the same terms:  a Some / No pair", "either"),
             ("All B are A  /  Some B are not A:  opposites, neither alone", "either"),
             ("both are definitely false", "neither")]
LENS = [("Recognition cue", "a single statement with two conclusions, often the reverse of the statement"),
        ("Target time", "20 seconds"),
        ("Sanity check", "“Some … not” never converts;   “All” converts only to “Some”")]
QUIZ = [["All A are B.          I.  Some B are A          II.  All B are A", "(a) Both   (b) Only I   (c) Only II   (d) Neither"],
        ["No A is B.          I.  No B is A          II.  Some A are not B", "(a) Only I   (b) Only II   (c) Either I or II   (d) Both"],
        ["Some A are B.          I.  All A are B          II.  Some A are not B", "(a) Either I or II   (b) Neither   (c) Only II   (d) Only I"],
        ["Some A are not B.          I.  Some B are not A          II.  All B are A", "(a) Only I   (b) Neither   (c) Either I or II   (d) Both"],
        ["No A is B.          I.  Some A are B          II.  All B are A", "(a) Either I or II   (b) Neither   (c) Only I   (d) Only II"]]
QUIZ_KEY = [("All converts to Some", "(b)  only I"),
            ("No ↔ No;   A exists", "(d)  both"),
            ("the same terms;   one must hold", "(a)  either"),
            ("All B are A  /  Some B are not A  on the same terms", "(c)  either"),
            ("both are definitely false", "(b)  neither")]


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


class ConversionAndImmediateInferenceVideo(LMSScene):
    lesson_title = "Conversion & Immediate Inference"

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

    def ring(self, radius, color):
        return Circle(radius=radius, color=color, stroke_width=4, fill_color=color, fill_opacity=0.12)

    def tag(self, word, color, width=1.7):
        return fit_width(text(word, SMALL, color, BOLD), width)

    def venn(self, kind, a, b, r=0.8, colors=(WORD, RATIO)):
        """Two sets drawn one way.  kind: "inside" (a inside b), "around" (b inside a), "same", "overlap", "apart".
        Returns VGroup(circle a, circle b, label a, label b)."""
        ca, cb = colors
        if kind in ("inside", "around"):
            big, small = self.ring(r * 1.5, cb if kind == "inside" else ca), self.ring(r * 0.8, ca if kind == "inside" else cb)
            small.move_to(big.get_center() + DOWN * r * 0.45)
            inner = self.tag(a if kind == "inside" else b, ca if kind == "inside" else cb, r * 1.35).move_to(small)
            outer = self.tag(b if kind == "inside" else a, cb if kind == "inside" else ca, r * 2.4).next_to(big, UP, buff=0.12)
            return VGroup(small, big, inner, outer) if kind == "inside" else VGroup(big, small, outer, inner)
        if kind == "same":
            one, two = self.ring(r * 1.1, ca), self.ring(r * 1.0, cb)
            label = VGroup(self.tag(a, ca), text("=", SMALL, MUTED, BOLD), self.tag(b, cb)).arrange(RIGHT, buff=0.15).next_to(one, UP, buff=0.12)
            return VGroup(one, two, label[0], VGroup(label[1], label[2]))
        gap = r * (1.1 if kind == "overlap" else 2.3)
        one, two = self.ring(r, ca).shift(LEFT * gap / 2), self.ring(r, cb).shift(RIGHT * gap / 2)
        if kind == "overlap":
            la, lb = self.tag(a, ca).next_to(one, UP, buff=0.12), self.tag(b, cb).next_to(two, DOWN, buff=0.12)
            la.align_to(one, LEFT)
            lb.align_to(two, RIGHT)
        else:
            la, lb = self.tag(a, ca, r * 1.7).move_to(one), self.tag(b, cb, r * 1.7).move_to(two)
        return VGroup(one, two, la, lb)

    def sets(self, *items, unit=1.0):
        """Any number of sets.  item = (label, x, y, radius, color, label x, label y), all in units of ``unit``.
        Returns VGroup(circles, labels)."""
        rings = VGroup(*[self.ring(r * unit, color).move_to([x * unit, y * unit, 0]) for _, x, y, r, color, _, _ in items])
        tags = VGroup(*[self.tag(label, color, 1.7 * r * unit).move_to([lx * unit, ly * unit, 0]) for label, _, _, r, color, lx, ly in items])
        return VGroup(rings, tags)

    def linked(self, kind, a="A", b="B", c="C", unit=1.0):
        """Three sets, b the middle term, drawn for one combination.  Returns VGroup(circles, labels), in the order a, b, c."""
        shapes = {
            "all all": [(a, 0, -0.65, 0.7, WORD, 0, -0.65), (b, 0, -0.3, 1.1, RATIO, 0, 0.42), (c, 0, 0, 1.5, SECOND, 0, 1.15)],
            "all no": [(a, -0.9, -0.3, 0.5, WORD, -0.9, -0.3), (b, -0.9, 0, 1.0, RATIO, -0.9, 0.6), (c, 1.2, 0, 0.8, SECOND, 1.2, 0)],
            "some all": [(a, -0.75, -0.3, 0.7, WORD, -1.1, -0.3), (b, 0.45, -0.3, 0.8, RATIO, 0.75, -0.3), (c, 0.45, 0, 1.4, SECOND, 0.45, 1.05)],
            "some no": [(a, -1.0, 0, 0.7, WORD, -1.15, 0.95), (b, 0, 0, 0.8, RATIO, 0.15, -1.05), (c, 1.75, 0, 0.7, SECOND, 1.75, 0)],
            "no all": [(a, -1.6, 0, 0.7, WORD, -1.6, 0), (b, 0.7, -0.3, 0.6, RATIO, 0.7, -0.3), (c, 0.7, 0, 1.2, SECOND, 0.7, 0.8)],
            "all some": [(a, -0.45, -0.25, 0.45, WORD, -0.45, -0.25), (b, 0, 0, 1.1, RATIO, 0, 0.7), (c, 1.35, -0.1, 0.7, SECOND, 1.65, -0.1)],
        }
        return self.sets(*shapes[kind], unit=unit)

    def panel(self, diagram, caption, color=MUTED):
        """A diagram with a caption under it.  Returns VGroup(diagram, caption)."""
        return VGroup(diagram, text(caption, SMALL, color, BOLD)).arrange(DOWN, buff=0.25)

    def judged(self, items):
        """Conclusions with their verdicts.  items = (conclusion, verdict, follows?).  row = (conclusion pill, verdict text)."""
        rows = VGroup(*[VGroup(pill(ask, WORD, size=LABEL), text(result, SMALL, GOOD if yes else BAD, BOLD)).arrange(DOWN, buff=0.14, aligned_edge=LEFT)
                        for ask, result, yes in items]).arrange(DOWN, buff=0.4, aligned_edge=LEFT)
        return rows

    def conversion(self, given, result, kind, note, ok=True, r=0.62):
        """One conversion rule: the statement, what it converts to, the diagram that shows why, and a note.
        Returns VGroup(statement, arrow, result, diagram, note)."""
        block = VGroup(pill(given, WORD, size=LABEL), text("converts to  ↓" if ok else "swap it?  ↓", SMALL, MUTED),
                       pill(result, GOOD if ok else BAD, size=LABEL), self.venn(kind, "A", "B", r=r), text(note, SMALL, INK, BOLD))
        block.arrange(DOWN, buff=0.2)
        return block

    # ============================================== 0. INTRO ==========
    # Not the first video: silent breadcrumb, a one-line recap of the previous video, then today's topic.

    def intro(self):
        self.scene_start("S00_intro", title="Intro")

        crumb = self.breadcrumb("Logical Reasoning", "Lesson 8 · Syllogism", "Video 2 of 7")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        recap = VGroup(text("from Video 1  ·  Statement Types & Venn Diagrams", SMALL, MUTED), pill("four statement types;   “follows” = true in every diagram", WORD, size=LABEL)).arrange(DOWN, buff=0.25)
        title = fit_width(text("Conversion & Immediate Inference", TITLE, INK, BOLD), SAFE_W - 0.4)
        today = text("today: what stays true when you swap the terms", LABEL, FOCUS)
        block = VGroup(recap, title, today).arrange(DOWN, buff=0.7)
        fit_within(block, SAFE_W, SAFE_H - crumb.height - 0.9)
        block.next_to(crumb, DOWN, buff=0.7)
        self.no_overlap(crumb, recap, title, today)
        self.validator.check_in_frame(VGroup(crumb, block))

        n = self.narrate(
            id="intro_01",
            text="In the last video, we drew the diagrams each statement allows, and a conclusion followed only if every "
                 "diagram agreed.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.at_word(n, "drew")
        self.play(FadeIn(recap[0]))
        self.at_word(n, "every")
        self.play(FadeIn(recap[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="intro_02",
            text="This video covers conversion and immediate inference: what stays true when you swap the terms.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "covers")
        self.play(FadeIn(title, shift=UP * 0.1))
        self.at_word(n, "swap")
        self.play(FadeIn(today, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_intro")

    # ============================================== 1. HOOK ==========

    def hook(self):
        self.scene_start("S01_hook", title="Hook")

        head = self.heading("Can you swap the two?")
        banner = pill("Every Integer is a Number", FOCUS, size=BODY)
        drawing = self.venn("inside", "Integer", "Number")
        asks = self.judged([("Every Number is an Integer", "no:  2.5 is a Number", False), ("Some Numbers are Integers", "safe", True)])
        middle = VGroup(drawing, asks).arrange(RIGHT, buff=0.9)
        name = pill("that safe swap has a name:  conversion", RATIO, size=LABEL)
        self.stack(head, [banner, middle, name], buff=0.6, top=0.8)
        self.no_overlap(drawing, asks)

        n = self.narrate(
            id="hook_01",
            text="In a type system, every Integer is a Number.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "every")
        self.play(FadeIn(banner, scale=1.03), FadeIn(drawing))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_02",
            text="Can you swap the two, and say, every Number is an Integer?",
            voice="default",
            subtitle=True,
            pause_after=3.0,
        )
        self.at_word(n, "swap")
        self.play(Indicate(head, color=FOCUS, scale_factor=1.03))
        self.at_word(n, "say")
        self.play(FadeIn(asks[0][0], shift=UP * 0.1))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="hook_03",
            text="No: two point five is a Number. But you can safely say, some Numbers are Integers.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "point")
        self.play(FadeIn(asks[0][1], shift=UP * 0.1))
        self.at_word(n, "safely")
        self.play(FadeIn(asks[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_04",
            text="That safe swap has a name: conversion.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "name")
        self.play(FadeIn(name, scale=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_05",
            text="Each statement type converts in a fixed way, and one of them does not convert at all. Know the four "
                 "rules, and one-statement questions take seconds.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "fixed")
        self.play(Indicate(name, color=FOCUS, scale_factor=1.03))
        self.at_word(n, "four")
        self.play(Indicate(banner, color=FOCUS, scale_factor=1.03))
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
            text="One: convert each statement type correctly, and know which one cannot be converted.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "convert")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "cannot")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="objectives_03",
            text="Two: use implications: all gives some, and no gives some not.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "implications")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "gives")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="objectives_04",
            text="Three: answer one-statement questions with two conclusions, including either-or.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "answer")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "including")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_objectives")

    # ============================================== 3. WHY THIS SECTION ==========

    def why_this_section(self):
        self.scene_start("S03_why_this_section", title="Why This Section")

        head = self.heading("Why this section")
        quick = pill("one-statement questions are the quickest syllogism marks", GOOD, size=LABEL)
        tests = text("conversion is all they test:  four fixed rules settle them in seconds", LABEL, INK, BOLD)
        self.stack(head, [quick, tests], buff=1.2, top=1.5)

        n = self.narrate(
            id="why_this_section_01",
            text="One-statement questions are the quickest syllogism marks, and conversion is all they test.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "quickest")
        self.play(FadeIn(quick, scale=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="why_this_section_02",
            text="Four fixed rules settle them in seconds.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "rules")
        self.play(FadeIn(tests, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_why_this_section")

    # ============================================== 4. THE CONCEPT JOURNEY ==========

    def concept_journey(self):
        self.scene_start("S04_concept_journey", title="The Concept Journey")

        head = self.heading("Steps 1 to 3  ·  conversion swaps the terms:  All, and No")
        swap = text("conversion swaps subject and predicate:  what remains guaranteed after the swap?", SMALL, FOCUS, BOLD)
        rules = VGroup(self.conversion("All A are B", "Some B are A", "inside", "not  “All B are A”"),
                       self.conversion("No A is B", "No B is A", "apart", "no overlap works both ways")).arrange(RIGHT, buff=1.6, aligned_edge=UP)
        self.stack(head, [swap, rules], buff=0.45, top=0.7)
        self.no_overlap(*rules)

        n = self.narrate(
            id="concept_journey_01",
            text="Step one: conversion swaps subject and predicate. The question is what remains guaranteed after the "
                 "swap.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "one")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "guaranteed")
        self.play(FadeIn(swap, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_journey_02",
            text="Step two: all A are B converts to some B are A. Not, all B are A.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "two")
        self.play(FadeIn(rules[0][0], shift=UP * 0.1), FadeIn(rules[0][3]))
        self.at_word(n, "converts")
        self.play(FadeIn(rules[0][1:3], shift=UP * 0.1))
        self.at_word(n, "Not")
        self.play(FadeIn(rules[0][4], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_journey_03",
            text="Step three: no A is B converts to no B is A. No overlap works both ways.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "three")
        self.play(FadeIn(rules[1][0], shift=UP * 0.1), FadeIn(rules[1][3]))
        self.at_word(n, "converts")
        self.play(FadeIn(rules[1][1:3], shift=UP * 0.1))
        self.at_word(n, "both")
        self.play(FadeIn(rules[1][4], shift=UP * 0.1))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Steps 4 and 5  ·  Some converts;  Some … not does not")
        rules = VGroup(self.conversion("Some A are B", "Some B are A", "overlap", "the overlap is shared"),
                       self.conversion("Some A are not B", "Some B are not A ?", "around", "all B might be inside A:  no conversion", ok=False))\
            .arrange(RIGHT, buff=1.4, aligned_edge=UP)
        self.stack(head, [rules], top=0.8)
        self.no_overlap(*rules)

        n = self.narrate(
            id="concept_journey_04",
            text="Step four: some A are B converts to some B are A. The overlap is shared.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "four")
        self.play(Indicate(head, color=FOCUS, scale_factor=1.03), FadeIn(rules[0][0], shift=UP * 0.1), FadeIn(rules[0][3]))
        self.at_word(n, "converts")
        self.play(FadeIn(rules[0][1:3], shift=UP * 0.1))
        self.at_word(n, "shared")
        self.play(FadeIn(rules[0][4], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_journey_05",
            text="Step five: some A are not B has no conversion. Some B are not A does not follow, because all B might be "
                 "inside A.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "five")
        self.play(FadeIn(rules[1][0], shift=UP * 0.1))
        self.at_word(n, "follow")
        self.play(FadeIn(rules[1][1:3], shift=UP * 0.1))
        self.at_word(n, "inside")
        self.play(FadeIn(rules[1][3]), FadeIn(rules[1][4], shift=UP * 0.1))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Steps 6 and 7  ·  implications and contradictions")
        gives = VGroup(text("implications:  both rely on A existing", SMALL, MUTED),
                       VGroup(pill("All A are B   gives   Some A are B", GOOD, size=LABEL), pill("No A is B   gives   Some A are not B", GOOD, size=LABEL))
                       .arrange(DOWN, buff=0.3)).arrange(DOWN, buff=0.25)
        against = VGroup(text("contradictions:  a statement makes its opposite definitely false", SMALL, MUTED),
                         VGroup(pill("All   ↔   Some not", BAD, size=LABEL), pill("No   ↔   Some", BAD, size=LABEL)).arrange(RIGHT, buff=0.6)).arrange(DOWN, buff=0.25)
        self.stack(head, [gives, against], buff=0.9, top=0.9)

        n = self.narrate(
            id="concept_journey_06",
            text="Step six: implications. All A are B gives some A are B. No A is B gives some A are not B. Both rely on A "
                 "existing.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "six")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "gives")
        self.play(FadeIn(gives[1][0], shift=UP * 0.1))
        self.at_word(n, "No")
        self.play(FadeIn(gives[1][1], shift=UP * 0.1))
        self.at_word(n, "rely")
        self.play(FadeIn(gives[0], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_journey_07",
            text="Step seven: contradictions. A statement makes its opposite definitely false: all against some not, and "
                 "no against some.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "seven")
        self.play(FadeIn(against[0], shift=UP * 0.1))
        self.at_word(n, "against")
        self.play(FadeIn(against[1][0], shift=UP * 0.1))
        self.at_word(n, "and")
        self.play(FadeIn(against[1][1], shift=UP * 0.1))
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
            text="Here is the rule box. All A are B converts to some B are A, and also gives some A are B.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "box")
        self.play(FadeIn(box[0]))
        self.at_word(n, "converts")
        self.play(FadeIn(lines[0], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="rule_box_02",
            text="No A is B converts to no B is A, and also gives some A are not B, and some B are not A.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "converts")
        self.play(FadeIn(lines[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="rule_box_03",
            text="Some A are B converts to some B are A.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "converts")
        self.play(FadeIn(lines[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="rule_box_04",
            text="Some A are not B has no conversion.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "conversion")
        self.play(FadeIn(lines[3], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="rule_box_05",
            text="Opposites are definitely false: all with some not, and no with some.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "false")
        self.play(FadeIn(lines[4], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_rule_box")

    # ============================================== 6. SHORT TRICK ==========

    def short_trick(self):
        self.scene_start("S06_short_trick", title="Short Trick")

        head = self.heading("Short trick", RATIO)
        rules = VGroup(pill("All  →  Some", WORD, size=BODY), pill("No  →  No", WORD, size=BODY), pill("Some  →  Some", WORD, size=BODY),
                       pill("Some … not  →  never", BAD, size=BODY)).arrange(RIGHT, buff=0.4)
        fit_width(rules, SAFE_W - 0.4)
        pair = text("if both conclusions fail on the same terms, check for an either-or pair", LABEL, FOCUS, BOLD)
        self.stack(head, [rules, pair], buff=1.2, top=1.4)
        self.no_overlap(*rules)

        n = self.narrate(
            id="short_trick_01",
            text="The short trick: all converts to some; no and some convert to themselves; some not never converts.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "all")
        self.play(FadeIn(rules[0], shift=UP * 0.1))
        self.at_word(n, "themselves")
        self.play(FadeIn(rules[1], shift=UP * 0.1), FadeIn(rules[2], shift=UP * 0.1))
        self.at_word(n, "never")
        self.play(FadeIn(rules[3], scale=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="short_trick_02",
            text="If both conclusions fail on the same terms, check for an either-or pair.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "check")
        self.play(FadeIn(pair, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_short_trick")

    # ============================================== 7. THE ANALOGY - STREET SIGNS ==========

    def analogy(self):
        self.scene_start("S07_analogy", title="The Analogy - Street Signs")

        head = self.heading("Conversion is a street sign")
        signs = VGroup(
            self.card(VGroup(text("⇄", TITLE, GOOD, BOLD), text("“No” and “Some”", LABEL, INK, BOLD), text("two-way streets", SMALL, MUTED)).arrange(DOWN, buff=0.18),
                      width=3.6, height=2.3, color=GOOD),
            self.card(VGroup(text("→", TITLE, RATIO, BOLD), text("“All”", LABEL, INK, BOLD), text("one-way:  reversed, it is “Some”", SMALL, MUTED)).arrange(DOWN, buff=0.18),
                      width=4.4, height=2.3, color=RATIO),
            self.card(VGroup(text("✗", TITLE, BAD, BOLD), text("“Some … not”", LABEL, INK, BOLD), text("no reverse lane at all", SMALL, MUTED)).arrange(DOWN, buff=0.18),
                      width=3.6, height=2.3, color=BAD)).arrange(RIGHT, buff=0.4)
        stops = VGroup(text("where the analogy stops", SMALL, BAD, BOLD), text("real one-way streets do not shrink in the other direction", SMALL, INK),
                       text("“All” does:  it shrinks to “Some”", SMALL, GOOD, BOLD)).arrange(DOWN, buff=0.14, aligned_edge=LEFT)
        self.stack(head, [signs, stops], buff=0.8, top=1.0)
        self.no_overlap(*signs)

        n = self.narrate(
            id="analogy_01",
            text="Conversion is a street sign. No and some are two-way streets: you can drive either direction.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "street")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "two-way")
        self.play(FadeIn(signs[0]))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_02",
            text="All is one-way, and turns into some when you reverse it.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "one-way")
        self.play(FadeIn(signs[1]))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_03",
            text="Some not has no reverse lane at all.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "lane")
        self.play(FadeIn(signs[2]))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_04",
            text="Where the analogy stops: real one-way streets do not shrink in the other direction. All does: it shrinks "
                 "to some.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "stops")
        self.play(FadeIn(stops[0], shift=RIGHT * 0.2))
        self.at_word(n, "shrink")
        self.play(FadeIn(stops[1], shift=RIGHT * 0.2))
        self.at_word(n, "shrinks")
        self.play(FadeIn(stops[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S07_analogy")

    # ============================================== 8. WORKED EXAMPLE - CLOSING THE HOOK ==========

    def hook_solved(self):
        self.scene_start("S08_hook_solved", title="Worked Example - Closing the Hook")

        head = self.heading("Worked example: All integers are numbers")
        drawing = self.panel(self.venn("inside", "Integers", "Numbers", r=0.95), "2.5 is a number outside the integers")
        asks = self.judged([("I.   Some numbers are integers", "the conversion of “All”:  follows", True),
                            ("II.   All numbers are integers", "reverses “All” in full:  does not follow", False)])
        top = VGroup(drawing, asks).arrange(RIGHT, buff=0.8)
        answer = pill("the answer:   only I follows", GOOD, size=BODY)
        self.stack(head, [top, answer], buff=0.8, top=0.9)
        self.no_overlap(drawing, asks)

        n = self.narrate(
            id="hook_solved_01",
            text="The statement: all integers are numbers. Conclusion one: some numbers are integers. Conclusion two: all "
                 "numbers are integers.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "statement")
        self.play(Indicate(head, color=FOCUS, scale_factor=1.03), FadeIn(drawing[0]))
        self.at_word(n, "one")
        self.play(FadeIn(asks[0][0], shift=UP * 0.1))
        self.at_word(n, "two")
        self.play(FadeIn(asks[1][0], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_solved_02",
            text="Step one: the conversion of all is, some numbers are integers. So conclusion one follows.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "conversion")
        self.play(FadeIn(asks[0][1], shift=UP * 0.1))
        self.at_word(n, "follows")
        self.play(Indicate(asks[0][0], color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_solved_03",
            text="Step two: conclusion two reverses all in full, but numbers may include non-integers. It does not follow.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "reverses")
        self.play(FadeIn(asks[1][1], shift=UP * 0.1))
        self.at_word(n, "include")
        self.play(FadeIn(drawing[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_solved_04",
            text="The answer: only one follows.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "only")
        self.play(FadeIn(answer, scale=1.03))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S08_hook_solved")

    # ============================================== 9. A SECOND WORKED EXAMPLE - EITHER-OR FROM ONE STATEMENT ==========

    def second_example(self):
        self.scene_start("S09_second_example", title="A Second Worked Example - Either-Or from One Statement")

        head = self.heading("A second worked example: either-or from one statement")
        given = pill("Some files are archives", FOCUS, size=BODY)
        asks = VGroup(pill("I.   All files are archives", WORD, size=LABEL), pill("II.   Some files are not archives", WORD, size=LABEL)).arrange(RIGHT, buff=0.6)
        steps = self.solve_steps([("“some” could be all, or not all", "neither follows alone"),
                                  ("the same two terms:   all files are archives, or at least one is not", "one must be true"),
                                  ("the answer", "either I or II follows")])
        self.stack(head, [given, asks, steps], buff=0.7, top=0.8)
        self.no_overlap(*asks)
        self.no_overlap(*steps)

        n = self.narrate(
            id="second_example_01",
            text="The statement: some files are archives. Conclusion one: all files are archives. Conclusion two: some "
                 "files are not archives.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "statement")
        self.play(FadeIn(given, scale=1.03))
        self.at_word(n, "one")
        self.play(FadeIn(asks[0], shift=UP * 0.1))
        self.at_word(n, "two")
        self.play(FadeIn(asks[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_02",
            text="Step one: neither follows alone, because some could be all, or not all.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "neither")
        self.play(FadeIn(steps[0][2], shift=LEFT * 0.1))
        self.at_word(n, "could")
        self.play(FadeIn(steps[0][:2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_03",
            text="Step two: they use the same two terms, and one of them must be true: either all files are archives, or "
                 "at least one is not.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "same")
        self.play(FadeIn(steps[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "must")
        self.play(FadeIn(steps[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_04",
            text="The answer: either one or two follows.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "either")
        self.play(FadeIn(steps[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S09_second_example")

    # ============================================== 10. EXAM PATTERNS - HOW THIS IS ASKED ==========

    def exam_patterns(self):
        self.scene_start("S10_exam_patterns", title="Exam Patterns - How This Is Asked")

        head = self.heading("Exam patterns: how this is asked")
        table, rows = self.placed_table(head, ["Statement", "I", "II", "Answer"], PATTERNS, [3.4, 3.2, 3.6, 2.2], room=1.2)
        colors = {"only": WORD, "both": GOOD, "eith": RATIO, "neit": BAD}
        for row, p in zip(rows, PATTERNS):
            row[3].set_color(colors[p[3][:4]])

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
            text="Only one: the conversion follows, but the full reverse of all does not.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Only")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_03",
            text="Both: no converts to no, and B exists, so some B are not A.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Both")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_04",
            text="Only one again: some converts to some, while conclusion two contradicts the statement.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Only")
        self.play(FadeIn(rows[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_05",
            text="Either, twice: an all with some-not pair, and a some with no pair, each on the same terms.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Either")
        self.play(FadeIn(rows[3], shift=RIGHT * 0.2))
        self.at_word(n, "no")
        self.play(FadeIn(rows[4], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_06",
            text="Neither: both conclusions are definitely false.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Neither")
        self.play(FadeIn(rows[5], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S10_exam_patterns")

    # ============================================== 11. TRAPS AND CONFUSING QUESTIONS ==========

    def traps(self):
        self.scene_start("S11_traps", title="Traps and Confusing Questions")

        head, ask, wrong, right, rule = self.show_trap(TRAPS[0])

        n = self.narrate(
            id="traps_01",
            text="Trap one: converting some not.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "converting")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_02",
            text="Some cups are not plates. Does, some plates are not cups, follow?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "cups")
        self.play(FadeIn(ask, shift=UP * 0.1))
        self.at_word(n, "Does")
        self.play(Indicate(ask, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_03",
            text="The wrong instinct: yes, by swapping.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "instinct")
        self.play(FadeIn(wrong, shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_04",
            text="Correct: every plate might be a cup, so it does not follow.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "might")
        self.play(FadeIn(right, shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_05",
            text="The rule: some A are not B has no conversion.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "conversion")
        self.play(FadeIn(rule, scale=1.03))
        self.wait_for_narration(n)
        self.clear_stage()

        head, ask, wrong, right, rule = self.show_trap(TRAPS[1])

        n = self.narrate(
            id="traps_06",
            text="Trap two: missing the either-or in one-statement questions.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "missing")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_07",
            text="Some A are not B. Conclusion one: some A are B. Conclusion two: no A is B.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "not")
        self.play(FadeIn(ask, shift=UP * 0.1))
        self.at_word(n, "one")
        self.play(Indicate(ask, color=FOCUS, scale_factor=1.03))
        self.at_word(n, "two")
        self.play(Indicate(ask, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_08",
            text="The wrong instinct: neither follows, so the answer is neither.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "instinct")
        self.play(FadeIn(wrong, shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_09",
            text="Correct: for the same pair, one of, some A are B, and, no A is B, must be true. So either one or two.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "must")
        self.play(FadeIn(right, shift=RIGHT * 0.2))
        self.at_word(n, "either")
        self.play(Indicate(right, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_10",
            text="The rule: after rejecting both, check whether the pair is some with no, or all with some not, on the "
                 "same terms.",
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
        given = pill("No A is B", FOCUS, size=BODY)
        asks = VGroup(pill("I.   No B is A", WORD, size=LABEL), pill("II.   Some B are not A", WORD, size=LABEL)).arrange(RIGHT, buff=0.6)
        drawing = self.panel(self.venn("apart", "A", "B"), "separate circles:  both hold")
        answer = pill("both follow", GOOD, size=BODY)
        self.stack(head, [given, asks, drawing, answer], buff=0.5, top=0.8)
        self.no_overlap(*asks)

        n = self.narrate(
            id="checkpoint_01",
            text="Your turn. No A is B. Conclusion one: no B is A. Conclusion two: some B are not A.",
            voice="default",
            subtitle=True,
            pause_after=10.0,
        )
        self.at_word(n, "turn")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "No")
        self.play(FadeIn(given, scale=1.03))
        self.at_word(n, "one")
        self.play(FadeIn(asks[0], shift=UP * 0.1))
        self.at_word(n, "two")
        self.play(FadeIn(asks[1], shift=UP * 0.1))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="checkpoint_02",
            text="The circles are separate, so both hold.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "separate")
        self.play(FadeIn(drawing))
        self.wait_for_narration(n)

        n = self.narrate(
            id="checkpoint_03",
            text="Both follow.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Both")
        self.play(FadeIn(answer, scale=1.03))
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
            text="Answer with: only one, only two, either, neither, or both. Level one.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Answer")
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "Level")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2), FadeIn(rows[1], shift=RIGHT * 0.2), FadeIn(rows[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="practice_02",
            text="Level two has three more.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "two")
        self.play(FadeIn(rows[3], shift=RIGHT * 0.2), FadeIn(rows[4], shift=RIGHT * 0.2), FadeIn(rows[5], shift=RIGHT * 0.2))
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
            text="Level three. Two questions that test the opposites.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Level")
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "opposites")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2), FadeIn(rows[1], shift=RIGHT * 0.2))
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
            text="One: only one. All converts to some.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "only")
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.at_word(n, "converts")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_02",
            text="Two: both. No converts to no; and B exists, so some B are not A.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "both")
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.at_word(n, "converts")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_03",
            text="Three: only one. Some converts to some, and conclusion two contradicts the statement.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "only")
        self.play(FadeIn(rows[2][2], shift=LEFT * 0.1))
        self.at_word(n, "converts")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_04",
            text="Four: either. The same terms, and one must hold.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "either")
        self.play(FadeIn(rows[3][2], shift=LEFT * 0.1))
        self.at_word(n, "must")
        self.play(FadeIn(rows[3][:2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Answer key  ·  5 to 8", GOOD)
        table, rows = self.answer_table(head, ANSWERS_B, 5)

        n = self.narrate(
            id="answers_05",
            text="Five: only one. Conclusion two contradicts the statement.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "only")
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.at_word(n, "contradicts")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_06",
            text="Six: either. The same terms, a some with no pair.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "either")
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.at_word(n, "pair")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_07",
            text="Seven: either. All B are A, and some B are not A, are opposites on the same terms, and neither follows "
                 "alone.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "either")
        self.play(FadeIn(rows[2][2], shift=LEFT * 0.1))
        self.at_word(n, "opposites")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_08",
            text="Eight: neither. Both are definitely false.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "neither")
        self.play(FadeIn(rows[3][2], shift=LEFT * 0.1))
        self.at_word(n, "false")
        self.play(FadeIn(rows[3][:2], shift=RIGHT * 0.2))
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
            text="Recognise and move. The recognition cue: a single statement with two conclusions, often the reverse of "
                 "the statement.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "cue")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "single")
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
            text="The sanity check: some not never converts; all converts only to some.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "sanity")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "never")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S15_exam_lens")

    # ============================================== 16. QUICK REVISION AND SUMMARY ==========

    def summary(self):
        self.scene_start("S16_summary", title="Quick Revision and Summary")

        head = self.heading("Quick revision")
        points = VGroup(text("All converts to Some;  No and Some convert to themselves;  Some … not does not convert", SMALL, INK, BOLD),
                        text("opposites are definitely false", LABEL, BAD, BOLD),
                        text("Some / No  or  All / Some-not  on the same terms:  either-or, when neither follows alone", SMALL, RATIO, BOLD))\
            .arrange(DOWN, buff=0.45, aligned_edge=LEFT)
        box = VGroup(pill("All → Some", GOOD, size=SMALL), pill("No → No", GOOD, size=SMALL), pill("Some → Some", GOOD, size=SMALL),
                     pill("Some not → nothing", GOOD, size=SMALL), pill("opposites false", GOOD, size=SMALL), pill("either-or pairs", GOOD, size=SMALL))\
            .arrange(RIGHT, buff=0.25)
        fit_width(box, SAFE_W - 0.4)
        self.stack(head, [points, box], buff=1.1, top=1.1)
        self.no_overlap(*points)
        self.no_overlap(*box)

        n = self.narrate(
            id="summary_01",
            text="All converts to some; no and some convert to themselves; some not does not convert.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "converts")
        self.play(FadeIn(points[0], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_02",
            text="Opposites are definitely false, and some with no, or all with some not, on the same terms, are either-or "
                 "when neither follows alone.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Opposites")
        self.play(FadeIn(points[1], shift=RIGHT * 0.2))
        self.at_word(n, "terms")
        self.play(FadeIn(points[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_03",
            text="That is the rule box in one line.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "line")
        self.play(FadeIn(box, shift=UP * 0.1))
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
                                        [[str(0 + i + 1)] + list(row) for i, row in enumerate(QUIZ[0:3])], [0.8, 6.6, 5.8], room=1.3)
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
                                        [[str(3 + i + 1)] + list(row) for i, row in enumerate(QUIZ[3:5])], [0.8, 6.6, 5.8], room=1.3)
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
        nxt = self.breadcrumb("Next", "Video 3 · Two-Statement Syllogisms")
        nxt.next_to(table, DOWN, buff=0.6)
        self.no_overlap(table, nxt)
        self.validator.check_in_frame(VGroup(head, table, nxt))

        n = self.narrate(
            id="section_quiz_07",
            text="The answers. One: all converts to some, so only one follows: option b.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "converts")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "option")
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="section_quiz_08",
            text="Two: no converts to no, and A exists, so both follow: option d.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "converts")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "option")
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="section_quiz_09",
            text="Three: the same terms, and one must hold: either: option a.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "must")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "option")
        self.play(FadeIn(rows[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="section_quiz_10",
            text="Four: all B are A, and some B are not A, are on the same terms: either: option c.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "same")
        self.play(FadeIn(rows[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "option")
        self.play(FadeIn(rows[3][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="section_quiz_11",
            text="Five: both are definitely false, so neither: option b.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "false")
        self.play(FadeIn(rows[4][:2], shift=RIGHT * 0.2))
        self.at_word(n, "option")
        self.play(FadeIn(rows[4][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="section_quiz_12",
            text="Next: two-statement syllogisms.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Next")
        self.play(FadeIn(nxt, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S17_section_quiz")

"""
animation.py for the LMS video generator.

Course : Pre-C-CAT - Section A - Logical Reasoning
Video  : Lesson 8 - Syllogism - 05 - Three- & Four-Statement Syllogisms

Source script:
  C:\\Scripts\\Section A\\Sessions 5-9 - Mathematical Operators, Symbols, Syllogism\\Lesson 8 - Syllogism\\05 - Three- & Four-Statement Syllogisms.pdf

Built on the golden-reference pattern:
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``;
  * layouts stacked with next_to and guarded with ``no_overlap``; nothing is
    ever animated onto or into another box.

Lesson 8, Video 4 of 7 (file 05 in its folder).
Not the first video: a silent breadcrumb, a one-line recap of Video 3, then today's topic.
The narration follows the script section by section and ends with the Section Quiz and its answer key.
A chain of statements is drawn as terms joined by labelled hops (All, Some, No); a break is a hop pair with no definite link.
Every question in the script was decided again in the data block by testing all possible diagrams,
with every named category having at least one member; all the script's answers are correct.
Practice question 8 (quiz question 5) is "neither" by the exam rule that an either-or pair must be about the same two terms.
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

def asked(given, first, second):
    """The five-way answer; the statements are separated by ";" or by full stops."""
    return judge([s for s in given.replace(".", ";").split(";") if s.strip()], first, second)


# ---- hook and first worked example ----
NETWORK = [All("routers", "switches"), All("switches", "servers"), No("servers", "databases")]
assert follows(NETWORK, All("routers", "servers")) and follows(NETWORK, No("routers", "databases"))
# ---- second worked example ----
BROKEN = "All A are B; Some B are C; All C are D"
assert asked(BROKEN, "Some B are D", "Some A are D") == "only I"
assert not follows([read("All A are B"), read("Some B are C")], Some("A", "C"))
# ---- the either-or pairs of step 6: no diagram makes both false ----
for one_, two_ in [(Some("A", "D"), No("A", "D")), (All("A", "D"), SomeNot("A", "D")), (Some("A", "D"), SomeNot("A", "D"))]:
    assert not consistent([denied(one_), denied(two_)])
# ---- exam patterns: statements, I, II, answer ----
PATTERNS = [["All A are B;  All B are C;  All C are D", "All A are D", "Some D are B", "both"],
            ["Some A are B;  All B are C;  No C is D", "Some A are not D", "Some B are D", "only I"],
            ["All A are B;  Some B are C;  All C are D", "Some B are D", "Some A are D", "only I"],
            ["No A is B;  All C are B;  Some D are C", "No A is C", "Some D are not A", "both"],
            ["Some A are B;  Some B are C;  No C is D", "Some B are not D", "No A is D", "only I"],
            ["Some A are B;  Some B are C;  No C is D", "Some A are D", "No A is D", "either"],
            ["All A are B;  All C are B;  No B is D", "No A is D", "No C is D", "both"],
            ["All A are B;  Some C are B;  No C is D", "Some B are D", "No A is D", "neither"]]
for given_, one_, two_, answer_ in PATTERNS:
    assert asked(given_, one_, two_) == answer_
# ---- traps and checkpoint ----
SOME_SOME = "Some A are B; Some B are C; No C is D"
assert follows([read(s) for s in SOME_SOME.split("; ")], SomeNot("B", "D")) and asked(SOME_SOME, "Some A are D", "No A is D") == "either"
assert asked("All A are B; All B are C; No C is D", "No A is D", "Some B are not D") == "both"
# ---- practice ----
ASKED = [("All A are B.  All B are C.  All C are D", "All A are D", "Some D are B", "both"),
         ("All A are B.  All B are C.  No C is D", "No A is D", "Some B are not D", "both"),
         ("Some A are B.  All B are C.  All C are D", "Some A are D", "All A are D", "only I"),
         ("Some A are B.  All B are C.  No C is D", "Some A are not D", "Some B are D", "only I"),
         ("All A are B.  Some B are C.  All C are D", "Some B are D", "Some A are D", "only I"),
         ("No A is B.  All C are B.  Some D are C", "No A is C", "Some D are not A", "both"),
         ("Some A are B.  Some B are C.  No C is D", "Some A are D", "No A is D", "either"),
         ("All A are B.  Some C are B.  No C is D", "Some B are D", "No A is D", "neither")]
for given_, one_, two_, answer_ in ASKED:
    assert asked(given_, one_, two_) == answer_
assert not possible([read("All B are C"), read("No C is D")], Some("B", "D"))
PRACTICE_A = [("L1" if i < 3 else "L2", f"{given}.          I.  {one}          II.  {two}") for i, (given, one, two, _) in enumerate(ASKED[:6])]
PRACTICE_B = [("L3", f"{given}.          I.  {one}          II.  {two}") for given, one, two, _ in ASKED[6:]]
# ---- section quiz: questions 1 to 5 are practice questions 1, 4, 5, 7 and 8 ----
SET = [ASKED[0], ASKED[3], ASKED[4], ASKED[6], ASKED[7]]
assert [s[3] for s in SET] == ["both", "only I", "only I", "either", "neither"]

OBJECTIVES = [("Chain three or four statements", "by combining two at a time"),
              ("Locate the path", "between the two terms in any conclusion"),
              ("Recognise where a chain breaks", "and test such conclusions for either-or")]
FORMULAS = ["Order the statements so neighbours share a term",
            "For each conclusion, use only the statements on its path",
            "Combine two at a time with the two-statement table",
            "Any break on the path   →   that conclusion does not follow",
            "Both fail   →   test for either-or on the same terms"]
TRAPS = [("Trap 1  ·  using statements off the path", "Some A are B;  Some B are C;  No C is D.      Does “Some B are not D” follow?",
          "“Some + Some breaks the chain”", "path B–C–D:  Some + No → Some B are not D:  follows",
          "combine only the statements on the conclusion's own path"),
         ("Trap 2  ·  a broken path still yields either-or", "Some A are B;  Some B are C;  No C is D.      I.  Some A are D      II.  No A is D",
          "both fail, so “neither”", "A–D breaks, but Some / No on the same terms:  either",
          "after rejecting both, always run the either-or test")]
ANSWERS_A = [("All all the way;   conversion gives II", "both"),
             ("All + All + No → No A is D;   B inside C gives Some B are not D", "both"),
             ("Some + All + All → Some A are D", "only I"),
             ("Some A are not D;   B sits inside C, which never meets D:  II is false", "only I")]
ANSWERS_B = [("B–C–D works;   A–B–C breaks", "only I"),
             ("C inside B, which never meets A;   the D that are C are not A", "both"),
             ("the A–D path breaks;   a Some / No pair on the same terms", "either"),
             ("no definite link, and the conclusions are about different pairs", "neither")]
LENS = [("Recognition cue", "three or four statements in a chain, conclusions about distant terms"),
        ("Target time", "40 seconds"),
        ("Sanity check", "for each conclusion, name the statements on its path before deciding")]
QUIZ = [[f"{given}.\nI.  {one}          II.  {two}", options] for (given, one, two, _), options in zip(SET, [
            "(a) Only I   (b) Only II\n(c) Neither   (d) Both",
            "(a) Only I   (b) Both\n(c) Neither   (d) Either I or II",
            "(a) Both   (b) Only II\n(c) Only I   (d) Neither",
            "(a) Neither   (b) Either I or II\n(c) Only II   (d) Only I",
            "(a) Neither   (b) Either I or II\n(c) Only II   (d) Only I"])]
QUIZ_KEY = [("All all the way;   convert for II", "(d)  both"),
            ("Some A are C;   C never meets D", "(a)  only I"),
            ("B–C–D works;   A–B–C breaks", "(c)  only I"),
            ("the path breaks;   a Some / No pair on the same terms", "(b)  either"),
            ("no definite link;   different pairs", "(a)  neither")]


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


class ThreeAndFourStatementSyllogismsVideo(LMSScene):
    lesson_title = "Three- & Four-Statement Syllogisms"

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

    def hops(self, terms, kinds, size=BODY):
        """A chain of terms joined by labelled hops.  Term i is part 2 * i, the hop after it is part 2 * i + 1."""
        parts = VGroup()
        for i, term in enumerate(terms):
            parts.add(pill(term, WORD, size=size))
            if i < len(kinds):
                parts.add(VGroup(text(kinds[i], SMALL, RATIO, BOLD), text("⟶", BODY, MUTED)).arrange(DOWN, buff=0.02))
        parts.arrange(RIGHT, buff=0.3)
        self.no_overlap(*parts)
        return parts

    def judged(self, items):
        """Conclusions with their verdicts.  items = (conclusion, verdict, follows?).  row = (conclusion pill, verdict text)."""
        rows = VGroup(*[VGroup(pill(ask, WORD, size=LABEL), text(result, SMALL, GOOD if yes else BAD, BOLD)).arrange(DOWN, buff=0.14, aligned_edge=LEFT)
                        for ask, result, yes in items]).arrange(DOWN, buff=0.4, aligned_edge=LEFT)
        return rows

    # ============================================== 0. INTRO ==========
    # Not the first video: silent breadcrumb, a one-line recap of the previous video, then today's topic.

    def intro(self):
        self.scene_start("S00_intro", title="Intro")

        crumb = self.breadcrumb("Logical Reasoning", "Lesson 8 · Syllogism", "Video 4 of 7")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        recap = VGroup(text("from Video 3  ·  Two-Statement Syllogisms", SMALL, MUTED), pill("find the middle term;   read the combination table;   no link → either-or check", WORD, size=LABEL)).arrange(DOWN, buff=0.25)
        title = fit_width(text("Three- & Four-Statement Syllogisms", TITLE, INK, BOLD), SAFE_W - 0.4)
        today = text("today: two at a time, down the chain", LABEL, FOCUS)
        block = VGroup(recap, title, today).arrange(DOWN, buff=0.7)
        fit_within(block, SAFE_W, SAFE_H - crumb.height - 0.9)
        block.next_to(crumb, DOWN, buff=0.7)
        self.no_overlap(crumb, recap, title, today)
        self.validator.check_in_frame(VGroup(crumb, block))

        n = self.narrate(
            id="intro_01",
            text="In the last video, the middle term linked two statements, and a five-row table gave the definite "
                 "conclusion.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.at_word(n, "middle")
        self.play(FadeIn(recap[0]))
        self.at_word(n, "table")
        self.play(FadeIn(recap[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="intro_02",
            text="This video covers three and four statement syllogisms: two at a time, down the chain.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "covers")
        self.play(FadeIn(title, shift=UP * 0.1))
        self.at_word(n, "chain")
        self.play(FadeIn(today, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_intro")

    # ============================================== 1. HOOK ==========

    def hook(self):
        self.scene_start("S01_hook", title="Hook")

        head = self.heading("Three statements, one question")
        given = VGroup(pill("All routers are switches", WORD, size=SMALL), pill("All switches are servers", RATIO, size=SMALL),
                       pill("No server is a database", SECOND, size=SMALL)).arrange(DOWN, buff=0.25)
        ask = text("is any router a database?", LABEL, FOCUS, BOLD)
        no = pill("no", BAD, size=BODY)
        left = VGroup(given, ask, no).arrange(DOWN, buff=0.4)
        drawing = self.sets(("Routers", 0, -0.65, 0.7, WORD, 0, -0.65), ("Switches", 0, -0.3, 1.1, RATIO, 0, 0.42), ("Servers", 0, 0, 1.5, SECOND, 0, 1.15),
                            ("Databases", 2.7, 0, 0.95, GOOD, 2.7, 0), unit=1.25)
        both = VGroup(left, drawing).arrange(RIGHT, buff=0.6)
        method = pill("combine only two at a time, passing the result down the chain", RATIO, size=SMALL)
        self.stack(head, [both, method], buff=0.5, top=0.75)
        self.no_overlap(left, drawing)

        n = self.narrate(
            id="hook_01",
            text="All routers are switches. All switches are servers. No server is a database. Is any router a database?",
            voice="default",
            subtitle=True,
            pause_after=3.0,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "routers")
        self.play(FadeIn(given[0], shift=UP * 0.1))
        self.at_word(n, "servers")
        self.play(FadeIn(given[1], shift=UP * 0.1))
        self.at_word(n, "database")
        self.play(FadeIn(given[2], shift=UP * 0.1))
        self.at_word(n, "any")
        self.play(FadeIn(ask, shift=UP * 0.1))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="hook_02",
            text="No. Routers sit inside switches, switches inside servers, and servers never touch databases.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "No")
        self.play(FadeIn(no, scale=1.03))
        self.at_word(n, "sit")
        self.play(FadeIn(drawing[0][0]), FadeIn(drawing[0][1]), FadeIn(drawing[1][0], shift=UP * 0.1), FadeIn(drawing[1][1], shift=UP * 0.1))
        self.at_word(n, "inside", occurrence=2)
        self.play(FadeIn(drawing[0][2]), FadeIn(drawing[1][2], shift=UP * 0.1))
        self.at_word(n, "never")
        self.play(FadeIn(drawing[0][3]), FadeIn(drawing[1][3], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_03",
            text="Three statements, but you only ever combine two at a time, passing the result down the chain. That is "
                 "the whole method for longer syllogisms.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "combine")
        self.play(FadeIn(method, scale=1.03))
        self.at_word(n, "whole")
        self.play(Indicate(method, color=FOCUS, scale_factor=1.03))
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
            text="One: chain three or four statements by combining two at a time.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "chain")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "combining")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="objectives_03",
            text="Two: locate the path between the two terms in any conclusion.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "locate")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "between")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="objectives_04",
            text="Three: recognise where a chain breaks, and test such conclusions for either-or.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "recognise")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "test")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_objectives")

    # ============================================== 3. WHY THIS SECTION ==========

    def why_this_section(self):
        self.scene_start("S03_why_this_section", title="Why This Section")

        head = self.heading("Why this section")
        same = pill("longer syllogisms look intimidating, but use the same table repeatedly", WORD, size=SMALL)
        path = text("working along each conclusion's path keeps them as quick as two-statement questions", SMALL, GOOD, BOLD)
        self.stack(head, [same, path], buff=1.2, top=1.5)

        n = self.narrate(
            id="why_this_section_01",
            text="Longer syllogisms look intimidating, but use the same table repeatedly.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "same")
        self.play(FadeIn(same, scale=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="why_this_section_02",
            text="Working along each conclusion's path keeps them as quick as two-statement questions.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "path")
        self.play(FadeIn(path, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_why_this_section")

    # ============================================== 4. THE CONCEPT JOURNEY ==========

    def concept_journey(self):
        self.scene_start("S04_concept_journey", title="The Concept Journey")

        head = self.heading("Steps 1 and 2  ·  order the chain;  find each conclusion's path")
        row = self.hops(["A", "B", "C", "D"], ["A–B", "B–C", "C–D"])
        share = text("neighbouring statements share a term", LABEL, INK, BOLD)
        fix = text("convert a statement if its terms are in the wrong order:    “Some C are B”  →  “Some B are C”", SMALL, FOCUS, BOLD)
        path = pill("a conclusion about A and D needs the links   A–B,   B–C,   C–D", GOOD, size=LABEL)
        self.stack(head, [row, share, fix, path], buff=0.75, top=0.9)

        n = self.narrate(
            id="concept_journey_01",
            text="Step one: order the chain. Arrange the statements so neighbouring statements share a term: A to B, B to "
                 "C, C to D.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "one")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "Arrange")
        self.play(FadeIn(row))
        self.at_word(n, "share")
        self.play(FadeIn(share, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_journey_02",
            text="Convert a statement if its terms are in the wrong order: some C are B becomes some B are C.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Convert")
        self.play(FadeIn(fix, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_journey_03",
            text="Step two: work out each conclusion's path. For a conclusion about A and D, you need the links A to B, B "
                 "to C, and C to D.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "two")
        self.play(Indicate(head, color=FOCUS, scale_factor=1.03))
        self.at_word(n, "need")
        self.play(FadeIn(path, scale=1.03))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Steps 3 and 4  ·  combine two at a time;  a break ends the path")
        row = self.hops(["A", "B", "C", "D"], ["A–B", "B–C", "C–D"])
        first = VGroup(text("A–B  with  B–C", LABEL, INK, BOLD), text("→", LABEL, MUTED), pill("A–C", GOOD, size=LABEL)).arrange(RIGHT, buff=0.4)
        then = VGroup(text("A–C  with  C–D", LABEL, INK, BOLD), text("→", LABEL, MUTED), pill("A–D", GOOD, size=LABEL)).arrange(RIGHT, buff=0.4)
        two = VGroup(first, then).arrange(RIGHT, buff=1.2)
        stop = VGroup(pill("a break:   All + Some,   Some + Some,   No + No", BAD, size=LABEL),
                      text("any step with no definite link:  the conclusion about the outer terms does not follow", SMALL, INK, BOLD)).arrange(DOWN, buff=0.25)
        self.stack(head, [row, two, stop], buff=0.85, top=0.9)
        self.no_overlap(first, then)

        n = self.narrate(
            id="concept_journey_04",
            text="Step three: combine two at a time. Apply the table from the last video to A to B and B to C, to get A to "
                 "C. Then combine A to C with C to D.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "three")
        self.play(Indicate(head, color=FOCUS, scale_factor=1.03), FadeIn(row))
        self.at_word(n, "Apply")
        self.play(FadeIn(first, shift=UP * 0.1))
        self.at_word(n, "Then")
        self.play(FadeIn(then, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_journey_05",
            text="Step four: a break ends the path. If any step gives no definite link, all plus some, some plus some, or "
                 "no plus no, the conclusion about the outer terms does not follow.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "four")
        self.play(Indicate(head, color=FOCUS, scale_factor=1.03))
        self.at_word(n, "link")
        self.play(FadeIn(stop[0], scale=1.03))
        self.at_word(n, "outer")
        self.play(FadeIn(stop[1], shift=UP * 0.1))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Steps 5 and 6  ·  short paths first;  then test for either-or")
        row = self.hops(["A", "B", "C", "D"], ["A–B", "B–C", "C–D"])
        short = text("a conclusion about B and D:  combine only the statements on that path", LABEL, INK, BOLD)
        pairs = VGroup(text("both conclusions fail?  test these pairs on the same terms", SMALL, MUTED),
                       VGroup(pill("Some  /  No", RATIO, size=LABEL), pill("All  /  Some not", RATIO, size=LABEL), pill("Some  /  Some not", RATIO, size=LABEL))
                       .arrange(RIGHT, buff=0.5),
                       text("the answer is either-or", LABEL, GOOD, BOLD)).arrange(DOWN, buff=0.3)
        self.stack(head, [row, short, pairs], buff=0.8, top=0.9)
        near = VGroup(*row[2:])

        n = self.narrate(
            id="concept_journey_06",
            text="Step five: short paths first. Many conclusions involve neighbouring terms, B and D for example. Combine "
                 "only the statements on that path.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "five")
        self.play(Indicate(head, color=FOCUS, scale_factor=1.03), FadeIn(row))
        self.at_word(n, "B")
        self.play(Indicate(near, color=FOCUS, scale_factor=1.03))
        self.at_word(n, "only")
        self.play(FadeIn(short, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_journey_07",
            text="Step six: then test for either-or. If both conclusions fail, and they are a some with no pair, an all "
                 "with some not pair, or a some with some not pair, on the same terms, the answer is either-or.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "six")
        self.play(Indicate(head, color=FOCUS, scale_factor=1.03))
        self.at_word(n, "fail")
        self.play(FadeIn(pairs[0], shift=UP * 0.1))
        self.at_word(n, "no")
        self.play(FadeIn(pairs[1][0], shift=UP * 0.1))
        self.at_word(n, "all")
        self.play(FadeIn(pairs[1][1], shift=UP * 0.1))
        self.at_word(n, "or")
        self.play(FadeIn(pairs[1][2], shift=UP * 0.1))
        self.at_word(n, "answer")
        self.play(FadeIn(pairs[2], shift=UP * 0.1))
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
            text="Here is the rule box. Order the statements so neighbours share a term.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "box")
        self.play(FadeIn(box[0]))
        self.at_word(n, "Order")
        self.play(FadeIn(lines[0], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="rule_box_02",
            text="For each conclusion, use only the statements on its path.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "only")
        self.play(FadeIn(lines[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="rule_box_03",
            text="Combine two at a time with the two-statement table.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Combine")
        self.play(FadeIn(lines[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="rule_box_04",
            text="Any break on the path means that conclusion does not follow.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "break")
        self.play(FadeIn(lines[3], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="rule_box_05",
            text="If both fail, test for either-or on the same terms.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "test")
        self.play(FadeIn(lines[4], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_rule_box")

    # ============================================== 6. SHORT TRICK ==========

    def short_trick(self):
        self.scene_start("S06_short_trick", title="Short Trick")

        head = self.heading("Short trick", RATIO)
        steps = VGroup(pill("for each conclusion, list only the statements on its path", FOCUS, size=LABEL),
                       text("combine two at a time", BODY, INK, BOLD),
                       pill("a break anywhere on the path:  that conclusion fails", BAD, size=LABEL))
        self.stack(head, list(steps), buff=1.0, top=1.2)

        n = self.narrate(
            id="short_trick_01",
            text="The short trick: for each conclusion, list only the statements on its path, and combine two at a time.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "list")
        self.play(FadeIn(steps[0], scale=1.03))
        self.at_word(n, "combine")
        self.play(FadeIn(steps[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="short_trick_02",
            text="A break anywhere on the path means that conclusion fails.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "break")
        self.play(FadeIn(steps[2], scale=1.03))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_short_trick")

    # ============================================== 7. THE ANALOGY - A PACKET, HOP BY HOP ==========

    def analogy(self):
        self.scene_start("S07_analogy", title="The Analogy - A Packet, Hop by Hop")

        head = self.heading("A long syllogism is a packet routed hop by hop")
        row = self.hops(["Router", "Switch", "Server", "Database"], ["hop", "hop", "hop"], size=LABEL)
        hop = text("each hop is a two-statement combination", LABEL, INK, BOLD)
        drop = pill("if any hop drops the packet, it never reaches the destination term", BAD, size=SMALL)
        stops = VGroup(text("where the analogy stops", SMALL, BAD, BOLD), text("packets can be rerouted", SMALL, INK),
                       text("a syllogism path cannot:  if the only path breaks, nothing definite follows", SMALL, GOOD, BOLD))\
            .arrange(DOWN, buff=0.14, aligned_edge=LEFT)
        self.stack(head, [row, hop, drop, stops], buff=0.65, top=0.9)

        n = self.narrate(
            id="analogy_01",
            text="A long syllogism is a packet routed hop by hop.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "packet")
        self.play(FadeIn(row))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_02",
            text="Each hop is a two-statement combination; if any hop drops the packet, it never reaches the destination "
                 "term.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "combination")
        self.play(FadeIn(hop, shift=UP * 0.1))
        self.at_word(n, "drops")
        self.play(FadeIn(drop, scale=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_03",
            text="Where the analogy stops: packets can be rerouted. A syllogism path cannot: if the only path breaks, "
                 "nothing definite follows.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "stops")
        self.play(FadeIn(stops[0], shift=RIGHT * 0.2))
        self.at_word(n, "rerouted")
        self.play(FadeIn(stops[1], shift=RIGHT * 0.2))
        self.at_word(n, "cannot")
        self.play(FadeIn(stops[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S07_analogy")

    # ============================================== 8. WORKED EXAMPLE - CLOSING THE HOOK ==========

    def hook_solved(self):
        self.scene_start("S08_hook_solved", title="Worked Example - Closing the Hook")

        head = self.heading("Worked example: the router chain")
        row = self.hops(["Routers", "Switches", "Servers", "Databases"], ["All", "All", "No"], size=LABEL)
        steps = self.solve_steps([("routers → servers:    All + All", "All routers are servers"),
                                  ("routers → databases:    All + No", "No router is a database")])
        drawing = self.sets(("Routers", 0, -0.65, 0.7, WORD, 0, -0.65), ("Switches", 0, -0.3, 1.1, RATIO, 0, 0.42), ("Servers", 0, 0, 1.5, SECOND, 0, 1.15),
                            ("Databases", 2.7, 0, 0.95, GOOD, 2.7, 0), unit=0.8)
        self.stack(head, [row, steps, drawing], buff=0.55, top=0.8)
        self.no_overlap(*steps)

        n = self.narrate(
            id="hook_solved_01",
            text="The statements: all routers are switches; all switches are servers; no server is a database.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "statements")
        self.play(FadeIn(row))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_solved_02",
            text="Step one, routers to servers: all plus all gives, all routers are servers.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "plus")
        self.play(FadeIn(steps[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "gives")
        self.play(FadeIn(steps[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_solved_03",
            text="Step two, routers to databases: all plus no gives, no router is a database.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "plus")
        self.play(FadeIn(steps[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "gives")
        self.play(FadeIn(steps[1][2], shift=LEFT * 0.1))
        self.at_word(n, "database")
        self.play(FadeIn(drawing))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S08_hook_solved")

    # ============================================== 9. A SECOND WORKED EXAMPLE - A BROKEN PATH ==========

    def second_example(self):
        self.scene_start("S09_second_example", title="A Second Worked Example - A Broken Path")

        head = self.heading("A second worked example: a broken path")
        row = self.hops(["A", "B", "C", "D"], ["All", "Some", "All"])
        asks = self.judged([("I.   Some B are D", "path B–C–D:   Some + All → Some B are D:   follows", True),
                            ("II.   Some A are D", "path A–B–C:   All + Some is a break:   does not follow", False)])
        answer = pill("the answer:   only I follows", GOOD, size=BODY)
        self.stack(head, [row, asks, answer], buff=0.7, top=0.85)
        near, far = VGroup(*row[2:]), VGroup(*row[:5])

        n = self.narrate(
            id="second_example_01",
            text="The statements: all A are B, some B are C, all C are D. Conclusion one: some B are D. Conclusion two: "
                 "some A are D.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "statements")
        self.play(FadeIn(row))
        self.at_word(n, "one")
        self.play(FadeIn(asks[0][0], shift=UP * 0.1))
        self.at_word(n, "two")
        self.play(FadeIn(asks[1][0], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_02",
            text="Conclusion one uses the path B, C, D: some plus all gives some B are D. It follows.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "path")
        self.play(Indicate(near, color=FOCUS, scale_factor=1.03))
        self.at_word(n, "gives")
        self.play(FadeIn(asks[0][1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_03",
            text="Conclusion two starts on the path A, B, C: all plus some is a break. It does not follow.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "starts")
        self.play(Indicate(far, color=FOCUS, scale_factor=1.03))
        self.at_word(n, "break")
        self.play(FadeIn(asks[1][1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_04",
            text="The answer: only one follows.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "only")
        self.play(FadeIn(answer, scale=1.03))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S09_second_example")

    # ============================================== 10. EXAM PATTERNS - HOW THIS IS ASKED ==========

    def exam_patterns(self):
        self.scene_start("S10_exam_patterns", title="Exam Patterns - How This Is Asked")

        head = self.heading("Exam patterns: how this is asked")
        table, rows = self.placed_table(head, ["Statements", "I", "II", "Answer"], PATTERNS, [6.3, 2.5, 2.5, 1.4], room=1.0)
        colors = {"only": WORD, "both": GOOD, "eith": RATIO, "neit": BAD}
        for row, p in zip(rows, PATTERNS):
            row[3].set_color(colors[p[3][:4]])

        n = self.narrate(
            id="exam_patterns_01",
            text="Exams ask this in eight ways.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "eight")
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_02",
            text="An unbroken all chain gives both; in the next one, conclusion two is false, because B sits inside C, "
                 "which never meets D.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "unbroken")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "next")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_03",
            text="A short path works where the long path breaks; and a reversed chain still gives both.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "short")
        self.play(FadeIn(rows[2], shift=RIGHT * 0.2))
        self.at_word(n, "reversed")
        self.play(FadeIn(rows[3], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_04",
            text="With some plus some at the start, the short path B, C, D still works; but the conclusions about A and D "
                 "form an either-or pair.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "still")
        self.play(FadeIn(rows[4], shift=RIGHT * 0.2))
        self.at_word(n, "pair")
        self.play(FadeIn(rows[5], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_05",
            text="Two terms inside B, with no B is D, give both; and with no definite link and different pairs, neither.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "inside")
        self.play(FadeIn(rows[6], shift=RIGHT * 0.2))
        self.at_word(n, "neither")
        self.play(FadeIn(rows[7], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S10_exam_patterns")

    # ============================================== 11. TRAPS AND CONFUSING QUESTIONS ==========

    def traps(self):
        self.scene_start("S11_traps", title="Traps and Confusing Questions")

        head, ask, wrong, right, rule = self.show_trap(TRAPS[0])

        n = self.narrate(
            id="traps_01",
            text="Trap one: using statements off the path.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "off")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_02",
            text="Some A are B; some B are C; no C is D. Does, some B are not D, follow?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "B")
        self.play(FadeIn(ask, shift=UP * 0.1))
        self.at_word(n, "Does")
        self.play(Indicate(ask, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_03",
            text="The wrong instinct: some plus some breaks the chain, so nothing follows.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "instinct")
        self.play(FadeIn(wrong, shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_04",
            text="Correct: the path B, C, D uses only, some B are C, and, no C is D. Some plus no gives some B are not D. "
                 "It follows.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "path")
        self.play(FadeIn(right, shift=RIGHT * 0.2))
        self.at_word(n, "gives")
        self.play(Indicate(right, color=FOCUS, scale_factor=1.03))
        self.at_word(n, "follows")
        self.play(Indicate(ask, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_05",
            text="The rule: combine only the statements on the conclusion's own path.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "own")
        self.play(FadeIn(rule, scale=1.03))
        self.wait_for_narration(n)
        self.clear_stage()

        head, ask, wrong, right, rule = self.show_trap(TRAPS[1])

        n = self.narrate(
            id="traps_06",
            text="Trap two: a broken path still yields either-or.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "still")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_07",
            text="The same statements. Conclusion one: some A are D. Conclusion two: no A is D.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "same")
        self.play(FadeIn(ask, shift=UP * 0.1))
        self.at_word(n, "one")
        self.play(Indicate(ask, color=FOCUS, scale_factor=1.03))
        self.at_word(n, "two")
        self.play(Indicate(ask, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_08",
            text="The wrong instinct: both fail, so the answer is neither.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "instinct")
        self.play(FadeIn(wrong, shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_09",
            text="Correct: the path from A to D breaks, but the conclusions are a some with no pair on the same terms. So "
                 "either one or two.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "breaks")
        self.play(FadeIn(right, shift=RIGHT * 0.2))
        self.at_word(n, "either")
        self.play(Indicate(right, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_10",
            text="The rule: after rejecting both, always run the either-or test.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "always")
        self.play(FadeIn(rule, scale=1.03))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S11_traps")

    # ============================================== 12. CHECKPOINT ==========

    def checkpoint(self):
        self.scene_start("S12_checkpoint", title="Checkpoint")

        head = self.heading("Checkpoint  ·  your turn")
        given = pill("All A are B;   All B are C;   No C is D", FOCUS, size=BODY)
        asks = VGroup(pill("I.   No A is D", WORD, size=LABEL), pill("II.   Some B are not D", WORD, size=LABEL)).arrange(RIGHT, buff=0.6)
        drawing = self.sets(("A", 0, -0.65, 0.7, WORD, 0, -0.65), ("B", 0, -0.3, 1.1, RATIO, 0, 0.42), ("C", 0, 0, 1.5, SECOND, 0, 1.15),
                            ("D", 2.6, 0, 0.9, GOOD, 2.6, 0), unit=0.8)
        answer = pill("both follow", GOOD, size=BODY)
        self.stack(head, [given, asks, drawing, answer], buff=0.45, top=0.75)
        self.no_overlap(*asks)

        n = self.narrate(
            id="checkpoint_01",
            text="Your turn. All A are B; all B are C; no C is D. Conclusion one: no A is D. Conclusion two: some B are "
                 "not D.",
            voice="default",
            subtitle=True,
            pause_after=10.0,
        )
        self.at_word(n, "turn")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "All")
        self.play(FadeIn(given, scale=1.03))
        self.at_word(n, "one")
        self.play(FadeIn(asks[0], shift=UP * 0.1))
        self.at_word(n, "two")
        self.play(FadeIn(asks[1], shift=UP * 0.1))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="checkpoint_02",
            text="A is inside B, B is inside C, and D is outside C.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "inside")
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
            text="Level three. Two chains with a break in them.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Level")
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "break")
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
            text="One: both. All, all the way, and conversion gives conclusion two.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "both")
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.at_word(n, "way")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_02",
            text="Two: both. All plus all plus no gives no A is D; and B inside C gives some B are not D.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "both")
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.at_word(n, "gives")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_03",
            text="Three: only one. Some plus all plus all gives some A are D.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "only")
        self.play(FadeIn(rows[2][2], shift=LEFT * 0.1))
        self.at_word(n, "gives")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_04",
            text="Four: only one. The chain gives some A are not D; and B sits inside C, which never meets D, so "
                 "conclusion two is false.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "only")
        self.play(FadeIn(rows[3][2], shift=LEFT * 0.1))
        self.at_word(n, "gives")
        self.play(FadeIn(rows[3][:2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Answer key  ·  5 to 8", GOOD)
        table, rows = self.answer_table(head, ANSWERS_B, 5)

        n = self.narrate(
            id="answers_05",
            text="Five: only one. The path B, C, D works; the path A, B, C breaks.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "only")
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.at_word(n, "works")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_06",
            text="Six: both. C is inside B, which never meets A; and the D that are C are not A.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "both")
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.at_word(n, "inside")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_07",
            text="Seven: either. The path from A to D breaks, and it is a some with no pair on the same terms.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "either")
        self.play(FadeIn(rows[2][2], shift=LEFT * 0.1))
        self.at_word(n, "breaks")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_08",
            text="Eight: neither. There is no definite link, and the two conclusions are about different pairs.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "neither")
        self.play(FadeIn(rows[3][2], shift=LEFT * 0.1))
        self.at_word(n, "link")
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
            text="Recognise and move. The recognition cue: three or four statements in a chain, with conclusions about "
                 "distant terms.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "cue")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "chain")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_lens_02",
            text="The target time: forty seconds.",
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
            text="The sanity check: for each conclusion, name the statements on its path before deciding.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "sanity")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "name")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S15_exam_lens")

    # ============================================== 16. QUICK REVISION AND SUMMARY ==========

    def summary(self):
        self.scene_start("S16_summary", title="Quick Revision and Summary")

        head = self.heading("Quick revision")
        points = VGroup(text("order the chain, and find each conclusion's path", LABEL, INK, BOLD),
                        text("combine two statements at a time", LABEL, RATIO, BOLD),
                        text("a break on the path:  that conclusion fails;  then test the pair for either-or", LABEL, GOOD, BOLD))\
            .arrange(DOWN, buff=0.45, aligned_edge=LEFT)
        box = VGroup(pill("order the chain", GOOD, size=SMALL), pill("path per conclusion", GOOD, size=SMALL), pill("two at a time", GOOD, size=SMALL),
                     pill("break → fails", GOOD, size=SMALL), pill("either-or check", GOOD, size=SMALL)).arrange(RIGHT, buff=0.3)
        fit_width(box, SAFE_W - 0.4)
        self.stack(head, [points, box], buff=1.1, top=1.1)
        self.no_overlap(*points)
        self.no_overlap(*box)

        n = self.narrate(
            id="summary_01",
            text="Order the chain, find each conclusion's path, and combine two statements at a time.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "Order")
        self.play(FadeIn(points[0], shift=RIGHT * 0.2))
        self.at_word(n, "combine")
        self.play(FadeIn(points[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_02",
            text="A break on the path means that conclusion fails; then test the pair for either-or.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "break")
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
                                        [[str(0 + i + 1)] + list(row) for i, row in enumerate(QUIZ[0:3])], [0.8, 8.0, 4.4], room=1.3)
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
                                        [[str(3 + i + 1)] + list(row) for i, row in enumerate(QUIZ[3:5])], [0.8, 8.0, 4.4], room=1.3)
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
        nxt = self.breadcrumb("Next", "Video 5 · Possibility & Either-Or")
        nxt.next_to(table, DOWN, buff=0.6)
        self.no_overlap(table, nxt)
        self.validator.check_in_frame(VGroup(head, table, nxt))

        n = self.narrate(
            id="section_quiz_07",
            text="The answers. One: all, all the way, and convert for conclusion two, so both follow: option d.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "way")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "option")
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="section_quiz_08",
            text="Two: some A are C, and C never meets D, so only one: option a.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "never")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "option")
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="section_quiz_09",
            text="Three: the path B, C, D works, and A, B, C breaks, so only one: option c.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "works")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "option")
        self.play(FadeIn(rows[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="section_quiz_10",
            text="Four: the path breaks, with a some and no pair on the same terms: either: option b.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "breaks")
        self.play(FadeIn(rows[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "option")
        self.play(FadeIn(rows[3][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="section_quiz_11",
            text="Five: no definite link, and different pairs: neither: option a.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "link")
        self.play(FadeIn(rows[4][:2], shift=RIGHT * 0.2))
        self.at_word(n, "option")
        self.play(FadeIn(rows[4][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="section_quiz_12",
            text="Next: possibility and either-or.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Next")
        self.play(FadeIn(nxt, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S17_section_quiz")

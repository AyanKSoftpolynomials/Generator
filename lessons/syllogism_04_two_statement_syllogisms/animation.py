"""
animation.py for the LMS video generator.

Course : Pre-C-CAT - Section A - Logical Reasoning
Video  : Lesson 8 - Syllogism - 04 - Two-Statement Syllogisms

Source script:
  C:\\Scripts\\Section A\\Sessions 5-9 - Mathematical Operators, Symbols, Syllogism\\Lesson 8 - Syllogism\\04 - Two-Statement Syllogisms.pdf

Built on the golden-reference pattern:
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``;
  * layouts stacked with next_to and guarded with ``no_overlap``; nothing is
    ever animated onto or into another box.

Lesson 8, Video 3 of 7 (file 04 in its folder).
Not the first video: a silent breadcrumb, a one-line recap of Video 2, then today's topic.
The narration follows the script section by section and ends with the Section Quiz and its answer key.
Each combination is drawn with three sets: A blue, the middle term B orange, C purple.
In the short trick the letter codes A, E, I, O are shown with their meanings (All, No, Some, Some not) and spoken as words.
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

def links(first, second, a="A", c="C"):
    """Every definite conclusion between the outer terms a and c that two statements give."""
    out = []
    for x, y in ((a, c), (c, a)):
        for kind in (All, No, Some, SomeNot):
            if follows([read(first), read(second)], kind(x, y)):
                out.append(kind(x, y))
    return out


# ---- the combination table ----
assert All("A", "C") in links("All A are B", "All B are C") and No("A", "C") in links("All A are B", "No B is C")
assert Some("A", "C") in links("Some A are B", "All B are C") and All("A", "C") not in links("Some A are B", "All B are C")
assert SomeNot("A", "C") in links("Some A are B", "No B is C") and SomeNot("C", "A") not in links("Some A are B", "No B is C")
assert links("No A is B", "All B are C") == [SomeNot("C", "A")]
assert links("Some A are not B", "All C are B") == [SomeNot("A", "C")]
for one_, two_ in [("All A are B", "Some B are C"), ("Some A are B", "Some B are C"), ("No A is B", "No B is C"),
                   ("Some A are not B", "All B are C"), ("Some A are not B", "No B is C"), ("All A are B", "Some B are not C")]:
    assert links(one_, two_) == []
# ---- hook and worked examples ----
SERVICES = [All("microservices", "containers"), All("containers", "deployable")]
assert follows(SERVICES, All("microservices", "deployable")) and follows(SERVICES, Some("deployable", "microservices"))
LAPTOPS = [Some("laptops", "tablets"), No("tablets", "phones")]
assert verdict(LAPTOPS, SomeNot("laptops", "phones"), No("laptops", "phones")) == "only I"
# ---- exam patterns: statements, I, II, answer ----
PATTERNS = [["All A are B;   All B are C", "All A are C", "Some C are A", "both"],
            ["All A are B;   No B is C", "No A is C", "Some C are not B", "both"],
            ["Some A are B;   All B are C", "Some A are C", "All A are C", "only I"],
            ["Some A are B;   No B is C", "Some A are not C", "No A is C", "only I"],
            ["No A is B;   All B are C", "Some C are not A", "No A is C", "only I"],
            ["All A are B;   Some B are C", "Some A are C", "No A is C", "either"],
            ["No A is B;   No B is C", "No A is C", "Some A are C", "either"],
            ["All A are B;   All A are C", "Some B are C", "All B are C", "only I"]]
for given_, one_, two_, answer_ in PATTERNS:
    assert judge(given_.split(";"), one_, two_) == answer_
# ---- traps and checkpoint ----
assert not follows([read("All A are B"), read("Some B are C")], Some("A", "C"))
assert not follows([read("Some A are B"), read("No B is C")], SomeNot("C", "A")) and possible([read("Some A are B"), read("No B is C")], All("C", "A"))
assert follows([read("All A are B"), read("No B is C")], No("A", "C"))
# ---- practice ----
assert verdict([All("pens", "tools"), All("tools", "items")], All("pens", "items"), Some("items", "pens")) == "both"
ASKED = [("All A are B.  No B is C", "No A is C", "Some C are not B", "both"), ("Some A are B.  All B are C", "Some A are C", "All A are C", "only I"),
         ("Some A are B.  No B is C", "Some A are not C", "No A is C", "only I"), ("All A are B.  Some B are C", "Some A are C", "No A is C", "either"),
         ("No A is B.  All B are C", "Some C are not A", "No A is C", "only I"), ("Some A are B.  Some B are C", "Some A are C", "No A is C", "either"),
         ("All A are B.  All A are C", "Some B are C", "All B are C", "only I")]
for given_, one_, two_, answer_ in ASKED:
    assert judge(given_.split(".  "), one_, two_) == answer_
PRACTICE_A = [("L1", "All pens are tools.  All tools are items.          I.  All pens are items          II.  Some items are pens")] + \
             [("L1" if i < 2 else "L2", f"{given}.          I.  {one}          II.  {two}") for i, (given, one, two, _) in enumerate(ASKED[:5])]
PRACTICE_B = [("L3", f"{given}.          I.  {one}          II.  {two}") for given, one, two, _ in ASKED[5:]]
# ---- section quiz ----
assert verdict([All("routers", "devices"), All("devices", "assets")], All("routers", "assets"), Some("assets", "routers")) == "both"
assert [judge(g.split(".  "), i, ii) for g, i, ii in [("Some A are B.  All B are C", "Some A are C", "All A are C"),
                                                       ("Some A are B.  No B is C", "Some A are not C", "No A is C"),
                                                       ("All A are B.  Some B are C", "Some A are C", "No A is C"),
                                                       ("No A is B.  All B are C", "Some C are not A", "No A is C")]] == ["only I", "only I", "either", "only I"]

OBJECTIVES = [("Identify the middle term", "that links two statements"),
              ("Use the standard combination table", "to read off the definite conclusion"),
              ("Confirm or reject any conclusion", "with a Venn diagram")]
FORMULAS = ["The middle term links the two statements;   the conclusion joins the outer terms",
            "All + All  →  All        All + No  →  No",
            "Some + All  →  Some        Some + No  →  Some not",
            "No + All  →  Some C are not A",
            "Some A are not B  +  All C are B   →   Some A are not C",
            "All + Some,   Some + Some,   No + No,   other Some-not pairs   →   no definite link"]
TRAPS = [("Trap 1  ·  All + Some read as a link", "All A are B;   Some B are C.        Does “Some A are C” follow?",
          "“yes, the chain looks connected”", "the Bs that are C may lie outside A:  does not follow",
          "“All + Some” passes nothing definite from A to C"),
         ("Trap 2  ·  Some + No in the wrong direction", "Some A are B;   No B is C.        Does “Some C are not A” follow?",
          "“yes, reverse Some A are not C”", "all of C might be inside A:  does not follow",
          "Some + No gives “Some A are not C”, in that direction only")]
ANSWERS_A = [("All + All → All;   conversion gives II", "both"),
             ("All + No → No;   No B is C gives Some C are not B", "both"),
             ("Some + All → Some", "only I"),
             ("Some + No → Some not", "only I")]
ANSWERS_B = [("no definite link, and Some / No on the same terms", "either"),
             ("No + All → Some C are not A", "only I"),
             ("no definite link, and Some / No on the same terms", "either"),
             ("A sits inside both B and C, so some B are C", "only I")]
LENS = [("Recognition cue", "two statements sharing one term, conclusions about the other two"),
        ("Target time", "30 seconds"),
        ("Sanity check", "for any “does not follow”, sketch one diagram where the conclusion fails")]
QUIZ = [["All routers are devices.  All devices are assets.\nI.  All routers are assets          II.  Some assets are routers",
         "(a) Only I   (b) Only II\n(c) Both   (d) Either I or II"],
        ["Some A are B.  All B are C.\nI.  Some A are C          II.  All A are C", "(a) Only I   (b) Both\n(c) Either I or II   (d) Only II"],
        ["Some A are B.  No B is C.\nI.  Some A are not C          II.  No A is C", "(a) Both   (b) Neither\n(c) Only II   (d) Only I"],
        ["All A are B.  Some B are C.\nI.  Some A are C          II.  No A is C", "(a) Only I   (b) Either I or II\n(c) Neither   (d) Both"],
        ["No A is B.  All B are C.\nI.  Some C are not A          II.  No A is C", "(a) Only I   (b) Both\n(c) Only II   (d) Neither"]]
QUIZ_KEY = [("All + All → All;   then convert", "(c)  both"),
            ("Some + All → Some", "(a)  only I"),
            ("Some + No → Some not", "(d)  only I"),
            ("no link;   a Some / No pair on the same terms", "(b)  either"),
            ("the Bs are C but not A", "(a)  only I")]


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


class TwoStatementSyllogismsVideo(LMSScene):
    lesson_title = "Two-Statement Syllogisms"

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

    def combo(self, name, given, result, kind, unit=1.0, ok=True):
        """One row of the combination table: its name, the statements, the conclusion and the diagram.
        Returns VGroup(name, statements, conclusion, diagram)."""
        block = VGroup(pill(name, WORD, size=LABEL), text(given, SMALL, INK, BOLD), pill(result, GOOD if ok else BAD, size=LABEL), self.linked(kind, unit=unit))
        block.arrange(DOWN, buff=0.22)
        return block

    def judged(self, items):
        """Conclusions with their verdicts.  items = (conclusion, verdict, follows?).  row = (conclusion pill, verdict text)."""
        rows = VGroup(*[VGroup(pill(ask, WORD, size=LABEL), text(result, SMALL, GOOD if yes else BAD, BOLD)).arrange(DOWN, buff=0.14, aligned_edge=LEFT)
                        for ask, result, yes in items]).arrange(DOWN, buff=0.4, aligned_edge=LEFT)
        return rows

    # ============================================== 0. INTRO ==========
    # Not the first video: silent breadcrumb, a one-line recap of the previous video, then today's topic.

    def intro(self):
        self.scene_start("S00_intro", title="Intro")

        crumb = self.breadcrumb("Logical Reasoning", "Lesson 8 · Syllogism", "Video 3 of 7")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        recap = VGroup(text("from Video 2  ·  Conversion & Immediate Inference", SMALL, MUTED), pill("All → Some;   No → No;   Some → Some;   Some … not → nothing", WORD, size=LABEL)).arrange(DOWN, buff=0.25)
        title = fit_width(text("Two-Statement Syllogisms", TITLE, INK, BOLD), SAFE_W - 0.4)
        today = text("today: what the middle term passes on", LABEL, FOCUS)
        block = VGroup(recap, title, today).arrange(DOWN, buff=0.7)
        fit_within(block, SAFE_W, SAFE_H - crumb.height - 0.9)
        block.next_to(crumb, DOWN, buff=0.7)
        self.no_overlap(crumb, recap, title, today)
        self.validator.check_in_frame(VGroup(crumb, block))

        n = self.narrate(
            id="intro_01",
            text="In the last video, all converted to some, no and some converted to themselves, and some not did not "
                 "convert at all.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.at_word(n, "converted")
        self.play(FadeIn(recap[0]))
        self.at_word(n, "themselves")
        self.play(FadeIn(recap[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="intro_02",
            text="This video covers two-statement syllogisms: what the middle term passes on, and what it does not.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "covers")
        self.play(FadeIn(title, shift=UP * 0.1))
        self.at_word(n, "passes")
        self.play(FadeIn(today, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_intro")

    # ============================================== 1. HOOK ==========

    def hook(self):
        self.scene_start("S01_hook", title="Hook")

        head = self.heading("Two statements, one link")
        given = VGroup(pill("All microservices are containers", WORD, size=LABEL), pill("All containers are deployable", SECOND, size=LABEL)).arrange(DOWN, buff=0.3)
        ask = text("are all microservices deployable?", LABEL, FOCUS, BOLD)
        yes = pill("yes", GOOD, size=BODY)
        middle = text("the middle term, containers, links the two statements", SMALL, RATIO, BOLD)
        left = VGroup(given, ask, yes, middle).arrange(DOWN, buff=0.45)
        drawing = self.linked("all all", "Microservices", "Containers", "Deployable", unit=1.6)
        both = VGroup(left, drawing).arrange(RIGHT, buff=0.6)
        self.stack(head, [both], top=0.9)
        self.no_overlap(left, drawing)

        n = self.narrate(
            id="hook_01",
            text="All microservices are containers. All containers are deployable. Are all microservices deployable?",
            voice="default",
            subtitle=True,
            pause_after=3.0,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "microservices")
        self.play(FadeIn(given[0], shift=UP * 0.1))
        self.at_word(n, "deployable")
        self.play(FadeIn(given[1], shift=UP * 0.1))
        self.at_word(n, "deployable", occurrence=2)
        self.play(FadeIn(ask, shift=UP * 0.1))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="hook_02",
            text="Yes: microservices sit inside containers, and containers sit inside deployable things.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Yes")
        self.play(FadeIn(yes, scale=1.03))
        self.at_word(n, "sit")
        self.play(FadeIn(drawing[0][0]), FadeIn(drawing[0][1]), FadeIn(drawing[1][0], shift=UP * 0.1), FadeIn(drawing[1][1], shift=UP * 0.1))
        self.at_word(n, "things")
        self.play(FadeIn(drawing[0][2]), FadeIn(drawing[1][2], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_03",
            text="The middle term, containers, links the two statements.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "middle")
        self.play(FadeIn(middle, shift=UP * 0.1), Indicate(drawing[0][1], color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_04",
            text="Two-statement syllogisms are always about that link: what the middle term passes from one statement to "
                 "the other, and what it does not.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "link")
        self.play(Indicate(middle, color=FOCUS, scale_factor=1.03))
        self.at_word(n, "passes")
        self.play(Indicate(head, color=FOCUS, scale_factor=1.03))
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
            text="One: identify the middle term that links two statements.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "identify")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "links")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="objectives_03",
            text="Two: use the standard combination table to read off the definite conclusion.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "table")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "read")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="objectives_04",
            text="Three: confirm or reject any conclusion with a Venn diagram.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "confirm")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "diagram")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_objectives")

    # ============================================== 3. WHY THIS SECTION ==========

    def why_this_section(self):
        self.scene_start("S03_why_this_section", title="Why This Section")

        head = self.heading("Why this section")
        core = pill("two-statement syllogisms are the core exam format", WORD, size=LABEL)
        table = text("a five-row combination table answers most of them without drawing anything", LABEL, GOOD, BOLD)
        self.stack(head, [core, table], buff=1.2, top=1.5)

        n = self.narrate(
            id="why_this_section_01",
            text="Two-statement syllogisms are the core exam format.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "core")
        self.play(FadeIn(core, scale=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="why_this_section_02",
            text="A five-row combination table answers most of them without drawing anything.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "table")
        self.play(FadeIn(table, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_why_this_section")

    # ============================================== 4. THE CONCEPT JOURNEY ==========

    def concept_journey(self):
        self.scene_start("S04_concept_journey", title="The Concept Journey")

        head = self.heading("Steps 1 and 2  ·  find the middle term;  arrange the chain")
        pair = VGroup(text("All A are", BODY, INK, BOLD), text("B", BODY, RATIO, BOLD), text(";      All", BODY, INK, BOLD), text("B", BODY, RATIO, BOLD),
                      text("are C", BODY, INK, BOLD)).arrange(RIGHT, buff=0.2)
        middle = text("B appears in both statements:  the middle term.     The conclusion links the other two, A and C", SMALL, INK, BOLD)
        chain = VGroup(pill("A – B", WORD, size=BODY), text("then", LABEL, MUTED), pill("B – C", SECOND, size=BODY)).arrange(RIGHT, buff=0.4)
        fix = text("convert a statement if needed:    “Some B are A”  becomes  “Some A are B”", SMALL, FOCUS, BOLD)
        self.stack(head, [pair, middle, chain, fix], buff=0.75, top=0.9)
        self.no_overlap(*pair, gap=0.02)

        n = self.narrate(
            id="concept_journey_01",
            text="Step one: find the middle term. It appears in both statements: B, in all A are B, all B are C. The "
                 "conclusion links the other two terms, A and C.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "one")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "appears")
        self.play(FadeIn(pair, shift=UP * 0.1), pair[1].animate.scale(1.25), pair[3].animate.scale(1.25))
        self.at_word(n, "other")
        self.play(FadeIn(middle, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_journey_02",
            text="Step two: arrange the chain. Write the statements so the middle term touches: A to B, then B to C.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "two")
        self.play(Indicate(head, color=FOCUS, scale_factor=1.03))
        self.at_word(n, "touches")
        self.play(FadeIn(chain, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_journey_03",
            text="Convert a statement if needed. For example, some B are A becomes some A are B.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Convert")
        self.play(FadeIn(fix, shift=UP * 0.1))
        self.at_word(n, "becomes")
        self.play(Indicate(fix, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Steps 3 and 4  ·  All + All;  All + No")
        rules = VGroup(self.combo("All + All  →  All", "All A are B,   All B are C", "All A are C", "all all"),
                       self.combo("All + No  →  No", "All A are B,   No B is C", "No A is C", "all no")).arrange(RIGHT, buff=1.4, aligned_edge=UP)
        self.stack(head, [rules], top=0.75)
        self.no_overlap(*rules)

        n = self.narrate(
            id="concept_journey_04",
            text="Step three: all plus all gives all. All A are B, all B are C: so all A are C.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "three")
        self.play(Indicate(head, color=FOCUS, scale_factor=1.03), FadeIn(rules[0][0], shift=UP * 0.1))
        self.at_word(n, "B")
        self.play(FadeIn(rules[0][1], shift=UP * 0.1), FadeIn(rules[0][3]))
        self.at_word(n, "so")
        self.play(FadeIn(rules[0][2], scale=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_journey_05",
            text="Step four: all plus no gives no. All A are B, no B is C: so no A is C.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "four")
        self.play(FadeIn(rules[1][0], shift=UP * 0.1))
        self.at_word(n, "B")
        self.play(FadeIn(rules[1][1], shift=UP * 0.1), FadeIn(rules[1][3]))
        self.at_word(n, "so")
        self.play(FadeIn(rules[1][2], scale=1.03))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Steps 5 and 6  ·  Some + All;  Some + No")
        rules = VGroup(self.combo("Some + All  →  Some", "Some A are B,   All B are C", "Some A are C", "some all"),
                       self.combo("Some + No  →  Some … not", "Some A are B,   No B is C", "Some A are not C", "some no")).arrange(RIGHT, buff=1.2, aligned_edge=UP)
        self.stack(head, [rules], top=0.75)
        self.no_overlap(*rules)

        n = self.narrate(
            id="concept_journey_06",
            text="Step five: some plus all gives some. Some A are B, all B are C: so some A are C.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "five")
        self.play(Indicate(head, color=FOCUS, scale_factor=1.03), FadeIn(rules[0][0], shift=UP * 0.1))
        self.at_word(n, "B")
        self.play(FadeIn(rules[0][1], shift=UP * 0.1), FadeIn(rules[0][3]))
        self.at_word(n, "so")
        self.play(FadeIn(rules[0][2], scale=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_journey_07",
            text="Step six: some plus no gives some not. Some A are B, no B is C: so some A are not C.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "six")
        self.play(FadeIn(rules[1][0], shift=UP * 0.1))
        self.at_word(n, "B")
        self.play(FadeIn(rules[1][1], shift=UP * 0.1), FadeIn(rules[1][3]))
        self.at_word(n, "so")
        self.play(FadeIn(rules[1][2], scale=1.03))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Steps 7 and 8  ·  No + All, reversed;  no definite link")
        rule = self.combo("No + All  →  Some … not, reversed", "No A is B,   All B are C", "Some C are not A", "no all")
        none = VGroup(pill("no definite link between A and C", BAD, size=LABEL),
                      text("All + Some        Some + Some        No + No", LABEL, INK, BOLD),
                      text("Some … not links only as:", SMALL, MUTED),
                      text("Some A are not B  +  All C are B   →   Some A are not C", SMALL, GOOD, BOLD),
                      text("no link:  check the conclusions for either-or", SMALL, FOCUS, BOLD)).arrange(DOWN, buff=0.3)
        both = VGroup(rule, none).arrange(RIGHT, buff=0.8)
        self.stack(head, [both], top=0.8)
        self.no_overlap(rule, none)

        n = self.narrate(
            id="concept_journey_08",
            text="Step seven: no plus all gives some not, reversed. No A is B, all B are C: so some C are not A.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "seven")
        self.play(Indicate(head, color=FOCUS, scale_factor=1.03), FadeIn(rule[0], shift=UP * 0.1))
        self.at_word(n, "B")
        self.play(FadeIn(rule[1], shift=UP * 0.1), FadeIn(rule[3]))
        self.at_word(n, "so")
        self.play(FadeIn(rule[2], scale=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_journey_09",
            text="Step eight: no definite link. All plus some, some plus some, and no plus no, give no definite conclusion "
                 "between A and C.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "eight")
        self.play(FadeIn(none[0], scale=1.03))
        self.at_word(n, "plus")
        self.play(FadeIn(none[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_journey_10",
            text="Some not gives one only in this form: some A are not B, with all C are B, gives some A are not C. Other "
                 "some-not pairings give nothing.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "only")
        self.play(FadeIn(none[2], shift=UP * 0.1))
        self.at_word(n, "with")
        self.play(FadeIn(none[3], shift=UP * 0.1))
        self.at_word(n, "Other")
        self.play(Indicate(none[3], color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_journey_11",
            text="So when there is no link, check the conclusions for either-or.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "check")
        self.play(FadeIn(none[4], shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_concept_journey")

    # ============================================== 5. RULE BOX ==========

    def rule_box(self):
        self.scene_start("S05_rule_box", title="Rule Box")

        head = self.heading("Rule box", GOOD)
        lines = VGroup(*[text(f, LABEL, INK) for f in FORMULAS]).arrange(DOWN, buff=0.34, aligned_edge=LEFT)
        fit_width(lines, SAFE_W - 1.6)
        box = self.card(lines, width=SAFE_W - 0.4, color=GOOD, pad=0.5)
        self.stack(head, [box], top=0.8)

        n = self.narrate(
            id="rule_box_01",
            text="Here is the rule box. The middle term links the two statements; the conclusion joins the outer terms.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "box")
        self.play(FadeIn(box[0]))
        self.at_word(n, "links")
        self.play(FadeIn(lines[0], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="rule_box_02",
            text="All plus all gives all; all plus no gives no.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "gives")
        self.play(FadeIn(lines[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="rule_box_03",
            text="Some plus all gives some; some plus no gives some not.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "gives")
        self.play(FadeIn(lines[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="rule_box_04",
            text="No plus all gives some C are not A.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "gives")
        self.play(FadeIn(lines[3], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="rule_box_05",
            text="Some A are not B, with all C are B, gives some A are not C.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "with")
        self.play(FadeIn(lines[4], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="rule_box_06",
            text="All plus some, some plus some, no plus no, and other some-not pairings give no definite link.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "pairings")
        self.play(FadeIn(lines[5], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_rule_box")

    # ============================================== 6. SHORT TRICK ==========

    def short_trick(self):
        self.scene_start("S06_short_trick", title="Short Trick")

        head = self.heading("Short trick", RATIO)
        legend = VGroup(text("the letter codes", SMALL, MUTED),
                        VGroup(pill("A  =  All", WORD, size=SMALL), pill("E  =  No", WORD, size=SMALL), pill("I  =  Some", WORD, size=SMALL),
                               pill("O  =  Some … not", WORD, size=SMALL)).arrange(RIGHT, buff=0.3)).arrange(DOWN, buff=0.2)
        table = VGroup(pill("A + A → A", GOOD, size=BODY), pill("A + E → E", GOOD, size=BODY), pill("I + A → I", GOOD, size=BODY), pill("I + E → O", GOOD, size=BODY),
                       pill("E + A → O reversed", GOOD, size=BODY)).arrange(RIGHT, buff=0.3)
        fit_width(table, SAFE_W - 0.4)
        other = text("any other pairing gives no definite link", LABEL, BAD, BOLD)
        self.stack(head, [legend, table, other], buff=0.9, top=1.0)
        self.no_overlap(*table)

        n = self.narrate(
            id="short_trick_01",
            text="The short trick: find the middle term, then read the table, written in letter codes: A for all, E for "
                 "no, I for some, and O for some not.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "middle")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "codes")
        self.play(FadeIn(legend, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="short_trick_02",
            text="All plus all gives all. All plus no gives no. Some plus all gives some. Some plus no gives some not. And "
                 "no plus all gives some not, reversed.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "gives")
        self.play(FadeIn(table[0], shift=UP * 0.1))
        self.at_word(n, "no")
        self.play(FadeIn(table[1], shift=UP * 0.1))
        self.at_word(n, "Some")
        self.play(FadeIn(table[2], shift=UP * 0.1))
        self.at_word(n, "not")
        self.play(FadeIn(table[3], shift=UP * 0.1))
        self.at_word(n, "reversed")
        self.play(FadeIn(table[4], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="short_trick_03",
            text="Any other pairing gives no definite link.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "other")
        self.play(FadeIn(other, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_short_trick")

    # ============================================== 7. THE ANALOGY - A RELAY HANDOVER ==========

    def analogy(self):
        self.scene_start("S07_analogy", title="The Analogy - A Relay Handover")

        head = self.heading("The middle term is a relay handover")
        runs = VGroup(
            self.card(VGroup(text("a clean handover", LABEL, GOOD, BOLD), text("the baton reaches the next runner", SMALL, INK),
                             text("a conclusion reaches the finish", SMALL, MUTED)).arrange(DOWN, buff=0.18), width=5.4, height=2.2, color=GOOD),
            self.card(VGroup(text("a dropped baton", LABEL, BAD, BOLD), text("the link is lost at the middle term", SMALL, INK),
                             text("no conclusion reaches the finish", SMALL, MUTED)).arrange(DOWN, buff=0.18), width=5.4, height=2.2, color=BAD))\
            .arrange(RIGHT, buff=0.6)
        stops = VGroup(text("where the analogy stops", SMALL, BAD, BOLD), text("a dropped baton ends a race", SMALL, INK),
                       text("a dropped link only means nothing definite follows:  possibility and either-or can still be asked", SMALL, GOOD, BOLD))\
            .arrange(DOWN, buff=0.14, aligned_edge=LEFT)
        self.stack(head, [runs, stops], buff=0.8, top=1.0)
        self.no_overlap(*runs)

        n = self.narrate(
            id="analogy_01",
            text="The middle term is a relay handover.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "relay")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_02",
            text="Some combinations pass the baton cleanly to the next runner; others drop it, and no conclusion reaches "
                 "the finish.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "cleanly")
        self.play(FadeIn(runs[0]))
        self.at_word(n, "drop")
        self.play(FadeIn(runs[1]))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_03",
            text="Where the analogy stops: a dropped baton ends a race. A dropped link only means nothing definite "
                 "follows; possibility and either-or questions can still be asked.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "stops")
        self.play(FadeIn(stops[0], shift=RIGHT * 0.2))
        self.at_word(n, "ends")
        self.play(FadeIn(stops[1], shift=RIGHT * 0.2))
        self.at_word(n, "only")
        self.play(FadeIn(stops[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S07_analogy")

    # ============================================== 8. WORKED EXAMPLE - CLOSING THE HOOK ==========

    def hook_solved(self):
        self.scene_start("S08_hook_solved", title="Worked Example - Closing the Hook")

        head = self.heading("Worked example: All + All")
        drawing = self.linked("all all", "Microservices", "Containers", "Deployable", unit=1.6)
        steps = VGroup(pill("All microservices are containers", WORD, size=SMALL), pill("All containers are deployable", SECOND, size=SMALL),
                       text("All + All  →  All", LABEL, FOCUS, BOLD), pill("All microservices are deployable", GOOD, size=LABEL),
                       text("by conversion:  some deployable things are microservices", SMALL, GOOD, BOLD)).arrange(DOWN, buff=0.35)
        both = VGroup(drawing, steps).arrange(RIGHT, buff=0.6)
        self.stack(head, [both], top=0.9)
        self.no_overlap(drawing, steps)

        n = self.narrate(
            id="hook_solved_01",
            text="All microservices are containers; all containers are deployable.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "containers")
        self.play(FadeIn(steps[0], shift=UP * 0.1), FadeIn(drawing))
        self.at_word(n, "deployable")
        self.play(FadeIn(steps[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_solved_02",
            text="All plus all gives all: all microservices are deployable.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "gives")
        self.play(FadeIn(steps[2], shift=UP * 0.1))
        self.at_word(n, "microservices")
        self.play(FadeIn(steps[3], scale=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_solved_03",
            text="By conversion, some deployable things are microservices too.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "conversion")
        self.play(FadeIn(steps[4], shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S08_hook_solved")

    # ============================================== 9. A SECOND WORKED EXAMPLE - SOME + NO ==========

    def second_example(self):
        self.scene_start("S09_second_example", title="A Second Worked Example - Some + No")

        head = self.heading("A second worked example: Some + No")
        given = VGroup(pill("Some laptops are tablets", WORD, size=LABEL), pill("No tablet is a phone", SECOND, size=LABEL)).arrange(RIGHT, buff=0.5)
        drawing = self.linked("some no", "Laptops", "Tablets", "Phones", unit=1.15)
        asks = self.judged([("I.   Some laptops are not phones", "Some + No → Some not:  follows", True),
                            ("II.   No laptop is a phone", "other laptops could still be phones:  does not follow", False)])
        lower = VGroup(drawing, asks).arrange(RIGHT, buff=0.6)
        answer = pill("the answer:   only I follows", GOOD, size=LABEL)
        self.stack(head, [given, lower, answer], buff=0.55, top=0.8)
        self.no_overlap(drawing, asks)
        self.no_overlap(*given)

        n = self.narrate(
            id="second_example_01",
            text="The statements: some laptops are tablets, and no tablet is a phone. Conclusion one: some laptops are not "
                 "phones. Conclusion two: no laptop is a phone.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "statements")
        self.play(FadeIn(given, shift=UP * 0.1), FadeIn(drawing))
        self.at_word(n, "one")
        self.play(FadeIn(asks[0][0], shift=UP * 0.1))
        self.at_word(n, "two")
        self.play(FadeIn(asks[1][0], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_02",
            text="Step one: the middle term is tablets. Some plus no gives, some laptops are not phones. Conclusion one "
                 "follows.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "middle")
        self.play(Indicate(drawing[0][1], color=FOCUS, scale_factor=1.03))
        self.at_word(n, "gives")
        self.play(FadeIn(asks[0][1], shift=UP * 0.1))
        self.at_word(n, "follows")
        self.play(Indicate(asks[0][0], color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_03",
            text="Step two: laptops that are not tablets could still be phones. Conclusion two does not follow.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "could")
        self.play(FadeIn(asks[1][1], shift=UP * 0.1))
        self.at_word(n, "not", occurrence=2)
        self.play(Indicate(asks[1][0], color=FOCUS, scale_factor=1.03))
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
        table, rows = self.placed_table(head, ["Statements", "I", "II", "Answer"], PATTERNS, [5.0, 3.0, 3.0, 1.6], room=1.1)
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
            text="Both, twice: all plus all, with its conversion; and all plus no, where no B is C also gives some C are "
                 "not B.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Both")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "where")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_03",
            text="Only one, three times: some plus all, some plus no, and no plus all each give one conclusion, and the "
                 "second conclusion asks for too much.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Only")
        self.play(FadeIn(rows[2], shift=RIGHT * 0.2))
        self.at_word(n, "plus", occurrence=2)
        self.play(FadeIn(rows[3], shift=RIGHT * 0.2))
        self.at_word(n, "each")
        self.play(FadeIn(rows[4], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_04",
            text="Either, twice: all plus some, and no plus no, give no definite link, and the conclusions are a some with "
                 "no pair.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Either")
        self.play(FadeIn(rows[5], shift=RIGHT * 0.2))
        self.at_word(n, "link")
        self.play(FadeIn(rows[6], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_05",
            text="And one without a chain: A sits inside both B and C, so some B are C.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "inside")
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
            text="Trap one: all plus some read as a link.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "read")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_02",
            text="All A are B; some B are C. Does, some A are C, follow?",
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
            text="The wrong instinct: yes, the chain looks connected.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "instinct")
        self.play(FadeIn(wrong, shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_04",
            text="Correct: the Bs that are C may lie outside A. It does not follow. With conclusion two as, no A is C, the "
                 "pair is either-or.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "outside")
        self.play(FadeIn(right, shift=RIGHT * 0.2))
        self.at_word(n, "not")
        self.play(Indicate(right, color=FOCUS, scale_factor=1.03))
        self.at_word(n, "pair")
        self.play(Indicate(ask, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_05",
            text="The rule: all plus some passes nothing definite from A to C.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "nothing")
        self.play(FadeIn(rule, scale=1.03))
        self.wait_for_narration(n)
        self.clear_stage()

        head, ask, wrong, right, rule = self.show_trap(TRAPS[1])

        n = self.narrate(
            id="traps_06",
            text="Trap two: some plus no in the wrong direction.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "direction")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_07",
            text="Some A are B; no B is C. Does, some C are not A, follow?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "B")
        self.play(FadeIn(ask, shift=UP * 0.1))
        self.at_word(n, "Does")
        self.play(Indicate(ask, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_08",
            text="The wrong instinct: yes, by reversing, some A are not C.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "instinct")
        self.play(FadeIn(wrong, shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_09",
            text="Correct: some not does not convert. All of C might be inside A. It does not follow.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "convert")
        self.play(FadeIn(right, shift=RIGHT * 0.2))
        self.at_word(n, "inside")
        self.play(Indicate(right, color=FOCUS, scale_factor=1.03))
        self.at_word(n, "follow")
        self.play(Indicate(ask, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_10",
            text="The rule: some plus no gives, some A are not C, in that direction only.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "only")
        self.play(FadeIn(rule, scale=1.03))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S11_traps")

    # ============================================== 12. CHECKPOINT ==========

    def checkpoint(self):
        self.scene_start("S12_checkpoint", title="Checkpoint")

        head = self.heading("Checkpoint  ·  your turn")
        given = VGroup(pill("All A are B;   No B is C", FOCUS, size=BODY), text("does  “No A is C”  follow?", LABEL, INK, BOLD)).arrange(DOWN, buff=0.3)
        drawing = self.panel(self.linked("all no"), "A inside B;  C separate from B")
        answer = pill("yes", GOOD, size=BODY)
        self.stack(head, [given, drawing, answer], buff=0.55, top=0.8)

        n = self.narrate(
            id="checkpoint_01",
            text="Your turn. All A are B; no B is C. Does, no A is C, follow?",
            voice="default",
            subtitle=True,
            pause_after=10.0,
        )
        self.at_word(n, "turn")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "All")
        self.play(FadeIn(given[0], scale=1.03))
        self.at_word(n, "Does")
        self.play(FadeIn(given[1], shift=UP * 0.1))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="checkpoint_02",
            text="A is inside B, and C is separate from B.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "inside")
        self.play(FadeIn(drawing))
        self.wait_for_narration(n)

        n = self.narrate(
            id="checkpoint_03",
            text="So yes, it follows.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "yes")
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
            text="Level three. Two pairs that are not in the table.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Level")
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "pairs")
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
            text="One: both. All plus all gives all, and conversion gives conclusion two.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "both")
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.at_word(n, "gives")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_02",
            text="Two: both. All plus no gives no; and no B is C gives some C are not B.",
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
            text="Three: only one. Some plus all gives some.",
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
            text="Four: only one. Some plus no gives some not.",
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
            text="Five: either. There is no definite link, and it is a some with no pair on the same terms.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "either")
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.at_word(n, "link")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_06",
            text="Six: only one. No plus all gives some C are not A.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "only")
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.at_word(n, "gives")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_07",
            text="Seven: either. Again no definite link, and a some with no pair on the same terms.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "either")
        self.play(FadeIn(rows[2][2], shift=LEFT * 0.1))
        self.at_word(n, "link")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_08",
            text="Eight: only one. A sits inside both B and C, so some B are C.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "only")
        self.play(FadeIn(rows[3][2], shift=LEFT * 0.1))
        self.at_word(n, "inside")
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
            text="Recognise and move. The recognition cue: two statements sharing one term, with conclusions about the "
                 "other two.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "cue")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "sharing")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_lens_02",
            text="The target time: thirty seconds.",
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
            text="The sanity check: for any, does not follow, sketch one diagram where the conclusion fails.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "sanity")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "sketch")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S15_exam_lens")

    # ============================================== 16. QUICK REVISION AND SUMMARY ==========

    def summary(self):
        self.scene_start("S16_summary", title="Quick Revision and Summary")

        head = self.heading("Quick revision")
        points = VGroup(text("find the middle term, and line the statements up", LABEL, INK, BOLD),
                        text("read the result from the combination table", LABEL, RATIO, BOLD),
                        text("no definite link:  test the conclusions for either-or", LABEL, GOOD, BOLD)).arrange(DOWN, buff=0.45, aligned_edge=LEFT)
        box = VGroup(pill("middle term", GOOD, size=SMALL), pill("A+A→A", GOOD, size=SMALL), pill("A+E→E", GOOD, size=SMALL), pill("I+A→I", GOOD, size=SMALL),
                     pill("I+E→O", GOOD, size=SMALL), pill("E+A→O reversed", GOOD, size=SMALL), pill("else: either-or check", GOOD, size=SMALL))\
            .arrange(RIGHT, buff=0.22)
        fit_width(box, SAFE_W - 0.4)
        self.stack(head, [points, box], buff=1.1, top=1.1)
        self.no_overlap(*points)
        self.no_overlap(*box)

        n = self.narrate(
            id="summary_01",
            text="Find the middle term, line the statements up, and read the result from the combination table.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "middle")
        self.play(FadeIn(points[0], shift=RIGHT * 0.2))
        self.at_word(n, "read")
        self.play(FadeIn(points[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_02",
            text="When no definite link exists, test the conclusions for either-or.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "test")
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
        nxt = self.breadcrumb("Next", "Video 4 · Three- & Four-Statement Syllogisms")
        nxt.next_to(table, DOWN, buff=0.6)
        self.no_overlap(table, nxt)
        self.validator.check_in_frame(VGroup(head, table, nxt))

        n = self.narrate(
            id="section_quiz_07",
            text="The answers. One: all plus all gives all, then convert, so both follow: option c.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "gives")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.at_word(n, "option")
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="section_quiz_08",
            text="Two: some plus all gives some, so only one: option a.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "gives")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.at_word(n, "option")
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="section_quiz_09",
            text="Three: some plus no gives some not, so only one: option d.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "gives")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.at_word(n, "option")
        self.play(FadeIn(rows[2][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="section_quiz_10",
            text="Four: no link, and a some with no pair on the same terms: either: option b.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "pair")
        self.play(FadeIn(rows[3][:2], shift=RIGHT * 0.2))
        self.at_word(n, "option")
        self.play(FadeIn(rows[3][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="section_quiz_11",
            text="Five: the Bs are C but not A, so only one: option a.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "but")
        self.play(FadeIn(rows[4][:2], shift=RIGHT * 0.2))
        self.at_word(n, "option")
        self.play(FadeIn(rows[4][2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="section_quiz_12",
            text="Next: three and four statement syllogisms.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Next")
        self.play(FadeIn(nxt, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S17_section_quiz")

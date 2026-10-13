"""
animation.py for the LMS video generator.

Course : Pre-C-CAT - Section A - Logical Reasoning
Video  : Lesson 8 - Syllogism - 02 - Statement Types & Venn Diagrams

Source script:
  C:\\Scripts\\Section A\\Sessions 5-9 - Mathematical Operators, Symbols, Syllogism\\Lesson 8 - Syllogism\\02 - Statement Types & Venn Diagrams.pdf

Built on the golden-reference pattern:
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``;
  * layouts stacked with next_to and guarded with ``no_overlap``; nothing is
    ever animated onto or into another box.

Lesson 8, Video 1 of 7 (file 02 in its folder).
First video of the lesson: a silent breadcrumb, the lesson announcement, a recap of Lesson 7, then today's topic.
The narration follows the script section by section and ends with the Section Quiz and its answer key.
Every statement type is drawn as the Venn diagrams it allows (first set blue, second set orange).
Every question in the script was decided again in the data block by testing all possible diagrams,
with every named category having at least one member; all the script's answers are correct.
Pauses: 3 seconds on the hook questions, 10 seconds on the checkpoint, 12 seconds on each practice and quiz screen.
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
    """Neither follows alone, but no diagram makes both false."""
    return (not follows(statements, first) and not follows(statements, second)
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


assert consistent([All("x", "y")]) and not consistent([All("x", "y"), No("x", "y")])
assert follows([All("x", "y")], Some("y", "x")) and not follows([All("x", "y")], All("y", "x"))

# ---- hook and worked examples ----
ADMINS = [All("admins", "users")]
assert not follows(ADMINS, All("users", "admins")) and follows(ADMINS, Some("users", "admins"))
ENGINEERS = [Some("engineers", "managers")]
assert not follows(ENGINEERS, SomeNot("engineers", "managers")) and possible(ENGINEERS, SomeNot("engineers", "managers"))
assert possible(ENGINEERS, All("engineers", "managers"))
# ---- opposites: never both true, never both false ----
for one_, two_ in [(All("a", "b"), SomeNot("a", "b")), (No("a", "b"), Some("a", "b"))]:
    assert not consistent([one_, two_]) and not consistent([denied(one_), denied(two_)])
# ---- exam patterns: (statement, conclusion, follows?) ----
for given_, asked_, yes_ in [(All("a", "b"), Some("a", "b"), True), (All("a", "b"), Some("b", "a"), True), (All("a", "b"), All("b", "a"), False),
                             (No("a", "b"), SomeNot("a", "b"), True), (Some("a", "b"), SomeNot("a", "b"), False),
                             (SomeNot("a", "b"), Some("a", "b"), False)]:
    assert follows([given_], asked_) == yes_
# ---- checkpoint and practice ----
assert follows([No("laptops", "tablets")], SomeNot("laptops", "tablets"))
for given_, asked_, yes_ in [(All("pens", "tools"), Some("tools", "pens"), True), (No("cats", "dogs"), No("dogs", "cats"), True),
                             (All("pens", "tools"), All("tools", "pens"), False), (Some("books", "files"), Some("files", "books"), True),
                             (Some("books", "files"), SomeNot("books", "files"), False), (No("cats", "dogs"), SomeNot("dogs", "cats"), True),
                             (SomeNot("cups", "plates"), SomeNot("plates", "cups"), False), (SomeNot("cups", "plates"), No("cups", "plates"), False)]:
    assert follows([given_], asked_) == yes_
assert possible([SomeNot("cups", "plates")], All("plates", "cups")) and possible([SomeNot("cups", "plates")], Some("cups", "plates"))
# ---- section quiz ----
assert [follows(ADMINS, c) for c in (All("users", "admins"), SomeNot("users", "admins"), Some("users", "admins"), No("users", "admins"))] \
    == [False, False, True, False]
assert [follows(ENGINEERS, c) for c in (Some("managers", "engineers"), SomeNot("engineers", "managers"), All("engineers", "managers"),
                                        No("managers", "engineers"))] == [True, False, False, False]
assert [follows([No("laptops", "tablets")], c) for c in (Some("tablets", "laptops"), All("laptops", "tablets"), Some("laptops", "tablets"),
                                                          SomeNot("laptops", "tablets"))] == [False, False, False, True]
assert [possible([SomeNot("cups", "plates")], c) for c in (All("plates", "cups"), All("cups", "plates"), No("cups", "plates"),
                                                           Some("cups", "plates"))] == [True, False, True, True]
assert [follows([All("a", "b")], c) for c in (All("b", "a"), Some("a", "b"), Some("b", "a"), All("a", "b"))] == [False, True, True, True]

OBJECTIVES = [("Recognise the four statement types", "All,   No,   Some,   Some … not"),
              ("Draw every Venn diagram", "that a statement allows"),
              ("Apply the two exam conventions", "every category exists, and “some” can mean “all”")]
FORMULAS = ["All A are B:   A inside B",
            "No A is B:   no overlap",
            "Some A are B:   at least one in common;  could be all",
            "Some A are not B:   at least one A outside B",
            "Every category exists;   “follows”  =  true in every diagram",
            "Opposite pairs:   All ↔ Some not        No ↔ Some"]
PATTERNS = [["All A are B", "Some A are B", "follows", "A exists and sits inside B"],
            ["All A are B", "Some B are A", "follows", "the same overlap, read from B"],
            ["All A are B", "All B are A", "does not follow", "B may be larger"],
            ["No A is B", "Some A are not B", "follows", "A exists, all of it outside B"],
            ["Some A are B", "Some A are not B", "does not follow", "“some” can be “all”"],
            ["Some A are not B", "Some A are B", "does not follow", "A and B may not touch"]]
TRAPS = [("Trap 1  ·  reading “some” as “some but not all”", "Some engineers are managers.     Does “Some engineers are not managers” follow?",
          "“yes:  some implies not all”", "“some” allows “all”:  does not follow",
          "“some” means at least one, possibly all"),
         ("Trap 2  ·  reversing “all”", "All admins are users.     Does “All users are admins” follow?",
          "“yes:  the sets match”", "users can include non-admins:  does not follow",
          "“All A are B” never gives “All B are A”")]
PRACTICE_A = [("L1", "All pens are tools.          Conclusion:   Some tools are pens."),
              ("L1", "No cats are dogs.          Conclusion:   No dogs are cats."),
              ("L1", "All pens are tools.          Conclusion:   All tools are pens."),
              ("L2", "Some books are files.          Conclusion:   Some files are books."),
              ("L2", "Some books are files.          Conclusion:   Some books are not files."),
              ("L2", "No cats are dogs.          Conclusion:   Some dogs are not cats.")]
PRACTICE_B = [("L3", "Some cups are not plates.          Conclusion:   Some plates are not cups."),
              ("L3", "Some cups are not plates.          Conclusion:   No cup is a plate.")]
ANSWERS_A = [("pens exist, and all of them are tools", "follows"),
             ("no overlap works both ways", "follows"),
             ("tools may include other things", "does not follow"),
             ("the overlap is shared", "follows")]
ANSWERS_B = [("all books might be files", "does not follow"),
             ("dogs exist, and none is a cat", "follows"),
             ("all plates could be cups", "does not follow"),
             ("some cups might still be plates", "does not follow")]
LENS = [("Recognition cue", "statements with  all,  no,  some,  some … not,  followed by conclusions"),
        ("Target time", "20 seconds per conclusion"),
        ("Sanity check", "try to draw a diagram where the conclusion is false:  if you can, it does not follow")]
QUIZ = [["All admins are users.  Which definitely follows?", "(a) All users are admins\n(b) Some users are not admins\n(c) Some users are admins\n(d) No user is an admin"],
        ["Some engineers are managers.  Which definitely follows?",
         "(a) Some managers are engineers\n(b) Some engineers are not managers\n(c) All engineers are managers\n(d) No manager is an engineer"],
        ["No laptop is a tablet.  Which definitely follows?",
         "(a) Some tablets are laptops\n(b) All laptops are tablets\n(c) Some laptops are tablets\n(d) Some laptops are not tablets"],
        ["Some cups are not plates.  Which is definitely false?",
         "(a) All plates are cups\n(b) All cups are plates\n(c) No cup is a plate\n(d) Some cups are plates"],
        ["All A are B.  Which does NOT follow?", "(a) All B are A\n(b) Some A are B\n(c) Some B are A\n(d) All A are B"]]
QUIZ_KEY = [("admins exist, and all of them are users", "(c)"),
            ("the overlap is shared", "(a)"),
            ("laptops exist, and none is a tablet", "(d)"),
            ("it is the opposite of the statement", "(b)"),
            ("B may be larger than A", "(a)")]


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


class StatementTypesAndVennDiagramsVideo(LMSScene):
    lesson_title = "Statement Types & Venn Diagrams"

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

    def panel(self, diagram, caption, color=MUTED):
        """A diagram with a caption under it.  Returns VGroup(diagram, caption)."""
        return VGroup(diagram, text(caption, SMALL, color, BOLD)).arrange(DOWN, buff=0.25)

    def judged(self, items):
        """Conclusions with their verdicts.  items = (conclusion, verdict, follows?).  row = (conclusion pill, verdict text)."""
        rows = VGroup(*[VGroup(pill(ask, WORD, size=LABEL), text(result, SMALL, GOOD if yes else BAD, BOLD)).arrange(DOWN, buff=0.14, aligned_edge=LEFT)
                        for ask, result, yes in items]).arrange(DOWN, buff=0.4, aligned_edge=LEFT)
        return rows

    # ============================================== 0. INTRO ==========
    # First video of the lesson: silent breadcrumb, the lesson announcement, a recap of the previous lesson, then today's topic.

    def intro(self):
        self.scene_start("S00_intro", title="Intro")

        crumb = self.breadcrumb("Logical Reasoning", "Lesson 8 · Syllogism", "Video 1 of 7")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        lesson = pill("Lesson 8  ·  Syllogism", RATIO, size=LABEL)
        recap = VGroup(text("from Lesson 7  ·  Symbols & Inequalities", SMALL, MUTED),
                       fit_width(VGroup(pill("no flip on the path, or nothing follows", WORD, size=LABEL), pill("either-or: same pair, every case covered", GOOD, size=LABEL)).arrange(RIGHT, buff=0.4), SAFE_W - 0.6)).arrange(DOWN, buff=0.25)
        title = fit_width(text("Statement Types & Venn Diagrams", TITLE, INK, BOLD), SAFE_W - 0.4)
        today = text("today: four statements and the diagrams they allow", LABEL, FOCUS)
        block = VGroup(lesson, recap, title, today).arrange(DOWN, buff=0.55)
        fit_within(block, SAFE_W, SAFE_H - crumb.height - 0.9)
        block.next_to(crumb, DOWN, buff=0.6)
        self.no_overlap(crumb, lesson, recap, title, today)
        self.no_overlap(*recap[1])
        self.validator.check_in_frame(VGroup(crumb, block))

        n = self.narrate(
            id="intro_01",
            text="Now we start lesson eight: syllogism.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.at_word(n, "eight")
        self.play(FadeIn(lesson, scale=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="intro_02",
            text="In lesson seven, symbols and inequalities, a conclusion followed only when the path between two letters "
                 "never flipped, and either-or needed the same pair with every case covered.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "path")
        self.play(FadeIn(recap[0]), FadeIn(recap[1][0], shift=UP * 0.1))
        self.at_word(n, "either-or")
        self.play(FadeIn(recap[1][1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="intro_03",
            text="This first video covers statement types and Venn diagrams: four statements, and the diagrams they allow.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "covers")
        self.play(FadeIn(title, shift=UP * 0.1))
        self.at_word(n, "four")
        self.play(FadeIn(today, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_intro")

    # ============================================== 1. HOOK ==========

    def hook(self):
        self.scene_start("S01_hook", title="Hook")

        head = self.heading("One rule, two questions")
        banner = pill("All admins are users", FOCUS, size=BODY)
        drawing = self.venn("inside", "Admins", "Users")
        asks = self.judged([("Are all users admins?", "does not follow:  some users may not be admins", False),
                            ("Are some users admins?", "follows:  every admin is a user", True)])
        middle = VGroup(drawing, asks).arrange(RIGHT, buff=0.7)
        rule = pill("draw the sets, and accept only what every possible drawing agrees on", RATIO, size=SMALL)
        self.stack(head, [banner, middle, rule], buff=0.6, top=0.8)
        self.no_overlap(drawing, asks)

        n = self.narrate(
            id="hook_01",
            text="Your access-control system guarantees one rule: all admins are users.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "rule")
        self.play(FadeIn(banner, scale=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_02",
            text="A colleague asks two questions. Are all users admins? Are some users admins?",
            voice="default",
            subtitle=True,
            pause_after=3.0,
        )
        self.at_word(n, "colleague")
        self.play(Indicate(head, color=FOCUS, scale_factor=1.03))
        self.at_word(n, "all")
        self.play(FadeIn(asks[0][0], shift=UP * 0.1))
        self.at_word(n, "some")
        self.play(FadeIn(asks[1][0], shift=UP * 0.1))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="hook_03",
            text="The first does not follow: there can be users who are not admins.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "first")
        self.play(FadeIn(drawing))
        self.at_word(n, "not")
        self.play(FadeIn(asks[0][1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_04",
            text="The second does follow: every admin is a user, so at least some users are admins.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "second")
        self.play(FadeIn(asks[1][1], shift=UP * 0.1))
        self.at_word(n, "least")
        self.play(Indicate(drawing[0], color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_05",
            text="That is syllogism in one screen: draw the sets, and accept only what every possible drawing agrees on.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "draw")
        self.play(FadeIn(rule, scale=1.03))
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
            text="One: recognise the four statement types: all, no, some, and some not.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "recognise")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "all")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="objectives_03",
            text="Two: draw every Venn diagram a statement allows.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "draw")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "allows")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="objectives_04",
            text="Three: apply the two exam conventions: every category exists, and some can mean all.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "apply")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "every")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_objectives")

    # ============================================== 3. WHY THIS SECTION ==========

    def why_this_section(self):
        self.scene_start("S03_why_this_section", title="Why This Section")

        head = self.heading("Why this section")
        rests = pill("every syllogism question rests on reading four statement types exactly", WORD, size=SMALL)
        wrong = VGroup(text("most wrong answers come from", LABEL, MUTED),
                       VGroup(pill("treating “some” as “some but not all”", BAD, size=LABEL), pill("reversing “all”", BAD, size=LABEL)).arrange(RIGHT, buff=0.5))\
            .arrange(DOWN, buff=0.3)
        self.stack(head, [rests, wrong], buff=1.2, top=1.4)

        n = self.narrate(
            id="why_this_section_01",
            text="Every syllogism question rests on reading four statement types exactly.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "rests")
        self.play(FadeIn(rests, scale=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="why_this_section_02",
            text="Most wrong answers come from treating some as some but not all, or reversing all.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "wrong")
        self.play(FadeIn(wrong[0], shift=UP * 0.1))
        self.at_word(n, "treating")
        self.play(FadeIn(wrong[1][0], shift=UP * 0.1))
        self.at_word(n, "reversing")
        self.play(FadeIn(wrong[1][1], shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_why_this_section")

    # ============================================== 4. THE CONCEPT JOURNEY ==========

    def concept_journey(self):
        self.scene_start("S04_concept_journey", title="The Concept Journey")

        head = self.heading("Step 1  ·  All A are B")
        says = pill("All A are B", FOCUS, size=BODY)
        views = VGroup(self.panel(self.venn("inside", "A", "B"), "B larger than A"), self.panel(self.venn("same", "A", "B"), "exactly the same"))\
            .arrange(RIGHT, buff=1.6, aligned_edge=DOWN)
        note = text("the A circle lies inside B", LABEL, INK, BOLD)
        self.stack(head, [says, note, views], buff=0.6, top=0.8)

        n = self.narrate(
            id="concept_journey_01",
            text="Step one: all A are B. The A circle lies inside B.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "one")
        self.play(Indicate(head, color=FOCUS, scale_factor=1.03), FadeIn(says, scale=1.03))
        self.at_word(n, "inside")
        self.play(FadeIn(note, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_journey_02",
            text="B may be larger than A, or exactly the same.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "larger")
        self.play(FadeIn(views[0]))
        self.at_word(n, "exactly")
        self.play(FadeIn(views[1]))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Steps 2 and 3  ·  No A is B;  Some A are B")
        no = VGroup(pill("No A is B", BAD, size=BODY), self.panel(self.venn("apart", "A", "B"), "the circles do not touch")).arrange(DOWN, buff=0.45)
        some = VGroup(pill("Some A are B", GOOD, size=BODY),
                      VGroup(self.panel(self.venn("overlap", "A", "B"), "overlap, at least partly"), self.panel(self.venn("inside", "A", "B"), "even all of A inside B"))
                      .arrange(RIGHT, buff=0.8, aligned_edge=DOWN)).arrange(DOWN, buff=0.45)
        both = VGroup(no, some).arrange(RIGHT, buff=1.0, aligned_edge=UP)
        least = text("“some” means “at least one”", LABEL, FOCUS, BOLD)
        self.stack(head, [both, least], buff=0.6, top=0.8)
        self.no_overlap(no, some)

        n = self.narrate(
            id="concept_journey_03",
            text="Step two: no A is B. The circles do not touch at all.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "two")
        self.play(Indicate(head, color=FOCUS, scale_factor=1.03), FadeIn(no[0], scale=1.03))
        self.at_word(n, "touch")
        self.play(FadeIn(no[1]))
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_journey_04",
            text="Step three: some A are B. The circles overlap at least partly.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "three")
        self.play(FadeIn(some[0], scale=1.03))
        self.at_word(n, "overlap")
        self.play(FadeIn(some[1][0]))
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_journey_05",
            text="Some means at least one, so A could even lie entirely inside B.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "least")
        self.play(FadeIn(least, shift=UP * 0.1))
        self.at_word(n, "entirely")
        self.play(FadeIn(some[1][1]))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Step 4  ·  Some A are not B")
        says = pill("Some A are not B", RATIO, size=BODY)
        views = VGroup(self.panel(self.venn("overlap", "A", "B"), "A and B may overlap"), self.panel(self.venn("apart", "A", "B"), "or not touch at all"))\
            .arrange(RIGHT, buff=1.4, aligned_edge=DOWN)
        note = text("at least part of A lies outside B", LABEL, INK, BOLD)
        self.stack(head, [says, note, views], buff=0.6, top=0.8)

        n = self.narrate(
            id="concept_journey_06",
            text="Step four: some A are not B. At least part of A lies outside B.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "four")
        self.play(Indicate(head, color=FOCUS, scale_factor=1.03), FadeIn(says, scale=1.03))
        self.at_word(n, "outside")
        self.play(FadeIn(note, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_journey_07",
            text="A and B may overlap, or not touch at all.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "overlap")
        self.play(FadeIn(views[0]))
        self.at_word(n, "touch")
        self.play(FadeIn(views[1]))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Steps 5 to 7  ·  two conventions and the opposites")
        exists = VGroup(pill("convention 1:  every category exists", WORD, size=LABEL),
                        text("each group named has at least one member:   “All admins are users”  gives  “Some users are admins”", SMALL, INK, BOLD))\
            .arrange(DOWN, buff=0.2)
        definite = VGroup(pill("convention 2:  “follows” means definite", RATIO, size=LABEL),
                          text("a conclusion follows only if it is true in every diagram the statements allow", SMALL, INK, BOLD)).arrange(DOWN, buff=0.2)
        opposites = VGroup(text("opposites:  never both true", SMALL, MUTED),
                           VGroup(pill("All A are B   ↔   Some A are not B", BAD, size=LABEL), pill("No A is B   ↔   Some A are B", BAD, size=LABEL))
                           .arrange(RIGHT, buff=0.5)).arrange(DOWN, buff=0.2)
        self.stack(head, [exists, definite, opposites], buff=0.7, top=0.8)

        n = self.narrate(
            id="concept_journey_08",
            text="Step five, convention one: every category exists. Each group named in a question has at least one "
                 "member. That is why, all admins are users, gives, some users are admins.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "five")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "exists")
        self.play(FadeIn(exists[0], scale=1.03))
        self.at_word(n, "why")
        self.play(FadeIn(exists[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_journey_09",
            text="Step six, convention two: follows means definite. A conclusion follows only if it is true in every "
                 "diagram the statements allow.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "six")
        self.play(FadeIn(definite[0], scale=1.03))
        self.at_word(n, "every")
        self.play(FadeIn(definite[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_journey_10",
            text="Step seven: opposites. All A are B, and some A are not B, cannot both be true; neither can, no A is B, "
                 "and some A are B.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "seven")
        self.play(FadeIn(opposites[0], shift=UP * 0.1))
        self.at_word(n, "cannot")
        self.play(FadeIn(opposites[1][0], shift=UP * 0.1))
        self.at_word(n, "neither")
        self.play(FadeIn(opposites[1][1], shift=UP * 0.1))
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
            text="Here is the rule box. All A are B: A inside B.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "box")
        self.play(FadeIn(box[0]))
        self.at_word(n, "inside")
        self.play(FadeIn(lines[0], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="rule_box_02",
            text="No A is B: no overlap.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "overlap")
        self.play(FadeIn(lines[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="rule_box_03",
            text="Some A are B: at least one in common, and it could be all.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "common")
        self.play(FadeIn(lines[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="rule_box_04",
            text="Some A are not B: at least one A outside B.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "outside")
        self.play(FadeIn(lines[3], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="rule_box_05",
            text="Every category exists, and follows means true in every diagram.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "exists")
        self.play(FadeIn(lines[4], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="rule_box_06",
            text="The opposite pairs: all with some not; and no with some.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "pairs")
        self.play(FadeIn(lines[5], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_rule_box")

    # ============================================== 6. SHORT TRICK ==========

    def short_trick(self):
        self.scene_start("S06_short_trick", title="Short Trick")

        head = self.heading("Short trick", RATIO)
        attempt = pill("to reject a conclusion, try to draw one valid diagram where it fails", FOCUS, size=LABEL)
        ends = VGroup(VGroup(text("you can draw it", LABEL, INK, BOLD), text("→", LABEL, MUTED), text("it does not follow", LABEL, BAD, BOLD)).arrange(RIGHT, buff=0.4),
                      VGroup(text("every diagram agrees", LABEL, INK, BOLD), text("→", LABEL, MUTED), text("it follows", LABEL, GOOD, BOLD)).arrange(RIGHT, buff=0.4))\
            .arrange(DOWN, buff=0.45, aligned_edge=LEFT)
        self.stack(head, [attempt, ends], buff=1.1, top=1.3)

        n = self.narrate(
            id="short_trick_01",
            text="The short trick: to reject a conclusion, try to draw one valid diagram where it fails.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "reject")
        self.play(FadeIn(attempt, scale=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="short_trick_02",
            text="If you can, it does not follow; if every diagram agrees, it does.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "can")
        self.play(FadeIn(ends[0], shift=RIGHT * 0.2))
        self.at_word(n, "agrees")
        self.play(FadeIn(ends[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_short_trick")

    # ============================================== 7. THE ANALOGY - QUERY RESULTS ==========

    def analogy(self):
        self.scene_start("S07_analogy", title="The Analogy - Query Results")

        head = self.heading("Categories are sets, like query results")
        inside = self.panel(self.venn("inside", "A", "B"), "“All A are B”:  one result set inside the other")
        overlap = self.panel(self.venn("overlap", "A", "B"), "“some”:  the intersection is not empty")
        both = VGroup(inside, overlap).arrange(RIGHT, buff=1.0, aligned_edge=DOWN)
        stops = VGroup(text("where the analogy stops", SMALL, BAD, BOLD), text("a database query can return nothing", SMALL, INK),
                       text("in exam syllogisms every named category has at least one member", SMALL, GOOD, BOLD)).arrange(DOWN, buff=0.14, aligned_edge=LEFT)
        self.stack(head, [both, stops], buff=0.7, top=0.9)
        self.no_overlap(inside, overlap)

        n = self.narrate(
            id="analogy_01",
            text="Categories are sets, like the rows returned by two queries.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "sets")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_02",
            text="All A are B says one result set is contained in the other; some says the intersection is not empty.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "contained")
        self.play(FadeIn(inside))
        self.at_word(n, "intersection")
        self.play(FadeIn(overlap))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_03",
            text="Where the analogy stops: a database query can return nothing. In exam syllogisms, every named category "
                 "has at least one member.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "stops")
        self.play(FadeIn(stops[0], shift=RIGHT * 0.2))
        self.at_word(n, "nothing")
        self.play(FadeIn(stops[1], shift=RIGHT * 0.2))
        self.at_word(n, "member")
        self.play(FadeIn(stops[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S07_analogy")

    # ============================================== 8. WORKED EXAMPLE - CLOSING THE HOOK ==========

    def hook_solved(self):
        self.scene_start("S08_hook_solved", title="Worked Example - Closing the Hook")

        head = self.heading("Worked example: All admins are users")
        views = VGroup(self.panel(self.venn("inside", "Admins", "Users"), "with extra users"), self.panel(self.venn("same", "Admins", "Users"), "without extra users"))\
            .arrange(RIGHT, buff=0.8, aligned_edge=DOWN)
        asks = self.judged([("I.   All users are admins", "fails with extra users:  does not follow", False),
                            ("II.   Some users are admins", "holds in every diagram:  follows", True)])
        top = VGroup(views, asks).arrange(RIGHT, buff=0.6)
        answer = pill("the answer:   only II follows", GOOD, size=BODY)
        self.stack(head, [top, answer], buff=0.9, top=1.0)
        self.no_overlap(views, asks)

        n = self.narrate(
            id="hook_solved_01",
            text="The statement: all admins are users. Conclusion one: all users are admins. Conclusion two: some users "
                 "are admins.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "statement")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "one")
        self.play(FadeIn(asks[0][0], shift=UP * 0.1))
        self.at_word(n, "two")
        self.play(FadeIn(asks[1][0], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_solved_02",
            text="Step one, the diagrams: admins inside users, with or without extra users.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "with")
        self.play(FadeIn(views[0]))
        self.at_word(n, "without")
        self.play(FadeIn(views[1]))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_solved_03",
            text="Step two: conclusion one fails in the diagram with extra users, so it does not follow.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "fails")
        self.play(FadeIn(asks[0][1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_solved_04",
            text="Step three: conclusion two holds in every diagram, because admins exist and all of them are users. It "
                 "follows.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "holds")
        self.play(FadeIn(asks[1][1], shift=UP * 0.1))
        self.at_word(n, "exist")
        self.play(Indicate(views, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_solved_05",
            text="The answer: only two follows.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "only")
        self.play(FadeIn(answer, scale=1.03))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S08_hook_solved")

    # ============================================== 9. A SECOND WORKED EXAMPLE - WHAT “SOME” DOES NOT SAY ==========

    def second_example(self):
        self.scene_start("S09_second_example", title="A Second Worked Example - What “Some” Does Not Say")

        head = self.heading("A second worked example: what “some” does not say")
        given = VGroup(pill("Some engineers are managers", FOCUS, size=LABEL), text("does  “Some engineers are not managers”  follow?", LABEL, INK, BOLD))\
            .arrange(DOWN, buff=0.3)
        views = VGroup(self.panel(self.venn("overlap", "Engineers", "Managers"), "diagram 1:  true", GOOD),
                       self.panel(self.venn("inside", "Engineers", "Managers", r=1.0), "diagram 2:  false", BAD)).arrange(RIGHT, buff=1.2, aligned_edge=DOWN)
        answer = pill("not true in every diagram:   does not follow", BAD, size=LABEL)
        self.stack(head, [given, views, answer], buff=0.5, top=0.75)

        n = self.narrate(
            id="second_example_01",
            text="The statement: some engineers are managers. Does, some engineers are not managers, follow?",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "statement")
        self.play(FadeIn(given[0], shift=UP * 0.1))
        self.at_word(n, "Does")
        self.play(FadeIn(given[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_02",
            text="Diagram one, a partial overlap: there it is true.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "partial")
        self.play(FadeIn(views[0][0]))
        self.at_word(n, "true")
        self.play(FadeIn(views[0][1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_03",
            text="Diagram two, all engineers inside managers: there it is false.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "inside")
        self.play(FadeIn(views[1][0]))
        self.at_word(n, "false")
        self.play(FadeIn(views[1][1], shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="second_example_04",
            text="It is not true in every diagram, so it does not follow.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "every")
        self.play(FadeIn(answer, scale=1.03))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S09_second_example")

    # ============================================== 10. EXAM PATTERNS - HOW THIS IS ASKED ==========

    def exam_patterns(self):
        self.scene_start("S10_exam_patterns", title="Exam Patterns - How This Is Asked")

        head = self.heading("Exam patterns: how this is asked")
        table, rows = self.placed_table(head, ["Statement", "Conclusion", "Result", "Why"], PATTERNS, [2.9, 2.9, 2.6, 4.9], room=1.2)
        for row, p in zip(rows, PATTERNS):
            row[2].set_color(GOOD if p[2] == "follows" else BAD)

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
            text="From all A are B: some A are B follows, because A exists and sits inside B; and some B are A follows, "
                 "the same overlap read from B.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "sits")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "read")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_03",
            text="But all B are A does not follow: B may be larger.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "larger")
        self.play(FadeIn(rows[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_04",
            text="From no A is B, some A are not B follows: A exists, and all of it is outside B.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "outside")
        self.play(FadeIn(rows[3], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_05",
            text="From some A are B, some A are not B does not follow, because some can be all.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "because")
        self.play(FadeIn(rows[4], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_patterns_06",
            text="And from some A are not B, some A are B does not follow: A and B may not touch.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "touch")
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
            text="Trap one: reading some as some but not all.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "reading")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_02",
            text="Some engineers are managers. Does, some engineers are not managers, follow?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "engineers")
        self.play(FadeIn(ask, shift=UP * 0.1))
        self.at_word(n, "Does")
        self.play(Indicate(ask, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_03",
            text="The wrong instinct: yes, some implies not all.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "instinct")
        self.play(FadeIn(wrong, shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_04",
            text="Correct: some allows all, so it does not follow.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "allows")
        self.play(FadeIn(right, shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_05",
            text="The rule: some means at least one, possibly all.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "least")
        self.play(FadeIn(rule, scale=1.03))
        self.wait_for_narration(n)
        self.clear_stage()

        head, ask, wrong, right, rule = self.show_trap(TRAPS[1])

        n = self.narrate(
            id="traps_06",
            text="Trap two: reversing all.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "reversing")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_07",
            text="All admins are users. Does, all users are admins, follow?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "admins")
        self.play(FadeIn(ask, shift=UP * 0.1))
        self.at_word(n, "Does")
        self.play(Indicate(ask, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_08",
            text="The wrong instinct: yes, the sets match.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "instinct")
        self.play(FadeIn(wrong, shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_09",
            text="Correct: users can include non-admins, so it does not follow.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "include")
        self.play(FadeIn(right, shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="traps_10",
            text="The rule: all A are B never gives all B are A.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "never")
        self.play(FadeIn(rule, scale=1.03))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S11_traps")

    # ============================================== 12. CHECKPOINT ==========

    def checkpoint(self):
        self.scene_start("S12_checkpoint", title="Checkpoint")

        head = self.heading("Checkpoint  ·  your turn")
        given = VGroup(pill("No laptops are tablets", FOCUS, size=BODY), text("does  “Some laptops are not tablets”  follow?", LABEL, INK, BOLD)).arrange(DOWN, buff=0.3)
        drawing = self.panel(self.venn("apart", "Laptops", "Tablets", r=1.0), "two separate circles, and laptops exist")
        answer = pill("yes:   it follows", GOOD, size=BODY)
        self.stack(head, [given, drawing, answer], buff=0.6, top=0.8)

        n = self.narrate(
            id="checkpoint_01",
            text="Your turn. No laptops are tablets. Does, some laptops are not tablets, follow?",
            voice="default",
            subtitle=True,
            pause_after=10.0,
        )
        self.at_word(n, "turn")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "laptops")
        self.play(FadeIn(given[0], scale=1.03))
        self.at_word(n, "Does")
        self.play(FadeIn(given[1], shift=UP * 0.1))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        n = self.narrate(
            id="checkpoint_02",
            text="Two separate circles, and laptops exist.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "separate")
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
            text="State whether the conclusion follows. Level one.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "State")
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
            text="Level three. Two conclusions drawn from, some cups are not plates.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Level")
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "drawn")
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
            text="One: follows. Pens exist, and all of them are tools.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "follows")
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.at_word(n, "exist")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_02",
            text="Two: follows. No overlap works both ways.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "follows")
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.at_word(n, "both")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_03",
            text="Three: does not follow. Tools may include other things.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "not")
        self.play(FadeIn(rows[2][2], shift=LEFT * 0.1))
        self.at_word(n, "include")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_04",
            text="Four: follows. The overlap is shared.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "follows")
        self.play(FadeIn(rows[3][2], shift=LEFT * 0.1))
        self.at_word(n, "shared")
        self.play(FadeIn(rows[3][:2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Answer key  ·  5 to 8", GOOD)
        table, rows = self.answer_table(head, ANSWERS_B, 5)

        n = self.narrate(
            id="answers_05",
            text="Five: does not follow. All books might be files.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "not")
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.at_word(n, "might")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_06",
            text="Six: follows. Dogs exist, and none is a cat.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "follows")
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.at_word(n, "exist")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_07",
            text="Seven: does not follow. All plates could be cups.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "not")
        self.play(FadeIn(rows[2][2], shift=LEFT * 0.1))
        self.at_word(n, "could")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="answers_08",
            text="Eight: does not follow. Some cups might still be plates.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "not")
        self.play(FadeIn(rows[3][2], shift=LEFT * 0.1))
        self.at_word(n, "still")
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
            text="Recognise and move. The recognition cue: statements with all, no, some, or some not, followed by "
                 "conclusions.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "cue")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "statements")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="exam_lens_02",
            text="The target time: twenty seconds per conclusion.",
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
            text="The sanity check: try to draw a diagram where the conclusion is false. If you can, it does not follow.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "sanity")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "draw")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S15_exam_lens")

    # ============================================== 16. QUICK REVISION AND SUMMARY ==========

    def summary(self):
        self.scene_start("S16_summary", title="Quick Revision and Summary")

        head = self.heading("Quick revision")
        kinds = VGroup(self.panel(self.venn("inside", "A", "B", r=0.6), "All"), self.panel(self.venn("apart", "A", "B", r=0.6), "No"),
                       self.panel(self.venn("overlap", "A", "B", r=0.6), "Some  /  Some not")).arrange(RIGHT, buff=0.9, aligned_edge=DOWN)
        point = text("a conclusion follows only if every possible diagram agrees", LABEL, INK, BOLD)
        box = VGroup(pill("All · No · Some · Some not", GOOD, size=SMALL), pill("categories exist", GOOD, size=SMALL), pill("some can be all", GOOD, size=SMALL),
                     pill("every diagram must agree", GOOD, size=SMALL)).arrange(RIGHT, buff=0.3)
        fit_width(box, SAFE_W - 0.4)
        self.stack(head, [kinds, point, box], buff=0.7, top=0.8)
        self.no_overlap(*kinds)
        self.no_overlap(*box)

        n = self.narrate(
            id="summary_01",
            text="Four statement types, each with its own diagrams.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "Four")
        self.play(FadeIn(kinds, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_02",
            text="Every category exists, some can mean all, and a conclusion follows only if every possible diagram "
                 "agrees.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "exists")
        self.play(Indicate(kinds, color=FOCUS, scale_factor=1.03))
        self.at_word(n, "agrees")
        self.play(FadeIn(point, shift=UP * 0.1))
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
                                        [[str(0 + i + 1)] + list(row) for i, row in enumerate(QUIZ[0:3])], [0.7, 6.4, 6.3], room=1.3)
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
                                        [[str(3 + i + 1)] + list(row) for i, row in enumerate(QUIZ[3:5])], [0.7, 6.4, 6.3], room=1.3)
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
        nxt = self.breadcrumb("Next", "Video 2 · Conversion & Immediate Inference")
        nxt.next_to(table, DOWN, buff=0.6)
        self.no_overlap(table, nxt)
        self.validator.check_in_frame(VGroup(head, table, nxt))

        n = self.narrate(
            id="section_quiz_07",
            text="The answers. One: option c. Admins exist, and all of them are users.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "answers")
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "option")
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.at_word(n, "exist")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="section_quiz_08",
            text="Two: option a. The overlap is shared.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "option")
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.at_word(n, "shared")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="section_quiz_09",
            text="Three: option d. Laptops exist, and none is a tablet.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "option")
        self.play(FadeIn(rows[2][2], shift=LEFT * 0.1))
        self.at_word(n, "exist")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="section_quiz_10",
            text="Four: option b. It is the opposite of the statement.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "option")
        self.play(FadeIn(rows[3][2], shift=LEFT * 0.1))
        self.at_word(n, "opposite")
        self.play(FadeIn(rows[3][:2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="section_quiz_11",
            text="Five: option a. B may be larger than A.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "option")
        self.play(FadeIn(rows[4][2], shift=LEFT * 0.1))
        self.at_word(n, "larger")
        self.play(FadeIn(rows[4][:2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="section_quiz_12",
            text="Next: conversion and immediate inference.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Next")
        self.play(FadeIn(nxt, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S17_section_quiz")

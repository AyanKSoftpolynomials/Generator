"""
animation.py for the LMS video generator.

Course : C-CAT - Section A - English
Module : Module 1 - Vocabulary
Lesson : Lesson 5 - Analogies
Video  : 04 - Context-Based Analogies (Video 4 of 7)

Source script:
  C:\\Users\\User\\Downloads\\C-CAT_SectionA_Module1_English\\English\\Module 1 - Vocabulary\\
  Lesson 5 - Analogies\\04 - Context-Based Analogies.pdf

Built on the golden-reference pattern:
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``;
  * layouts stacked with next_to and guarded with ``no_overlap``; nothing is
    ever animated onto or into another box.

The double-meaning words live in MEANINGS, and PARTNER_FIXES records which meaning each partner word selects; fixed_meaning(word, partner) returns the meaning kept and the one left out, and the concept, analogy, worked examples and Hook, Solved read from it.
The "fix the meaning" card (partner fixes the meaning, bridge in that meaning, strike other-meaning options, domain: match the function) stays pinned top-right through the worked examples and Hook, Solved.
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

# Words with two meanings, and which meaning each partner word selects.
MEANINGS = {
    "mouse": ("an animal", "a computer device"),
    "bank": ("a financial institution", "a river's edge"),
    "school": ("a place of learning", "a group of fish"),
    "scale": ("a weighing device, or a set of notes", "a fish's covering"),
}
PARTNER_FIXES = {("mouse", "computer"): 1, ("bank", "river"): 1, ("bank", "money"): 0, ("school", "fish"): 1,
                 ("scale", "fish"): 1}


def fixed_meaning(word, partner):
    """The meaning of ``word`` that its partner selects, and the meaning left out."""
    k = PARTNER_FIXES[(word, partner)]
    return MEANINGS[word][k], MEANINGS[word][1 - k]


def analogy_line(a, b, c, d="?", size=BODY):
    """A : B :: C : D as chips.  [0], [2] = first pair;  [4], [6] = second pair."""
    return VGroup(pill(a, WORD, size=size), text(":", size, MUTED), pill(b, WORD, size=size), text("::", size, MUTED),
                  pill(c, SECOND, size=size), text(":", size, MUTED),
                  pill(d, FOCUS if d == "?" else GOOD, size=size)).arrange(RIGHT, buff=0.25)


assert fixed_meaning("mouse", "computer") == ("a computer device", "an animal")
assert fixed_meaning("bank", "money")[0] == "a financial institution"


class ContextBasedAnalogiesVideo(LMSScene):
    lesson_title = "Context-Based Analogies"

    def construct(self):
        self.camera.background_color = BG

        self.lesson_intro()
        self.hook()
        self.concept()
        self.why_you_need_it()
        self.analogy()
        self.example_bank()
        self.example_school()
        self.example_firewall()
        self.rules()
        self.process()
        self.hook_solved()
        self.exam_patterns()
        self.common_mistakes()
        self.practice()
        self.answers()
        self.recap()
        self.next_video()

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

    def meaning_pin(self):
        return self.steps_pin("fix the meaning", [("the PARTNER fixes the meaning", WORD),
                                                  ("bridge in that meaning", RATIO),
                                                  ("strike other-meaning options", BAD),
                                                  ("domain: match the FUNCTION", SECOND)])

    def desk_card(self):
        head = text("YOUR DESK  ·  a laptop with a mouse, a TV with a remote", SMALL, RATIO, BOLD)
        line = analogy_line("MOUSE", "COMPUTER", "REMOTE", size=LABEL)
        cx, w = self.free_area()
        body = VGroup(head, line).arrange(DOWN, buff=0.25, aligned_edge=LEFT)
        fit_width(body, min(w - 1.4, SAFE_W - 1.8))
        card = self.card(body, width=min(w - 0.2, SAFE_W - 0.4))
        return card.move_to(RIGHT * cx + UP * (CARD_TOP - card.height / 2))

    def meaning_example(self, a, b, c, d, chips, first, second):
        """Analogy line, the meaning (or function) the partner fixes, and the two bridges."""
        cx, w = self.free_area()
        line = analogy_line(a, b, c)
        marks = VGroup(*[pill(t, col, size=SMALL) for t, col in chips]).arrange(RIGHT, buff=0.3)
        b1 = text(f"“{first}”", LABEL, INK)
        b2 = text(f"“{second}”", LABEL, INK, t2c={d: GOOD})
        block = VGroup(line, marks, b1, b2).arrange(DOWN, buff=0.5, aligned_edge=LEFT)
        fit_within(block, w - 0.6, SAFE_H - 1.8)
        self.place_free(block, y=0.2)
        answer = pill(d, GOOD, size=BODY).scale(line[6].height / pill("?", FOCUS, size=BODY).height)
        answer.move_to(line[6], aligned_edge=LEFT)
        self.no_overlap(line, marks, b1, b2)
        self.validator.check_in_frame(VGroup(block, answer))
        return line, marks, b1, b2, answer

    # ========================================= 0. LESSON INTRO ==========

    def lesson_intro(self):
        self.scene_start("S00_intro", title="Lesson Introduction")

        crumb = self.breadcrumb("English · Module 1 Vocabulary", "Lesson 5 · Analogies", "Video 4")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        before = pill("Lessons 1 and 2: the SENTENCE selects a word's meaning", MUTED, size=LABEL)
        none = pill("in an analogy there is no sentence", BAD, size=LABEL)
        partner = pill("the OTHER WORD in the pair does the selecting", GOOD, size=LABEL)
        VGroup(before, none, partner).arrange(DOWN, buff=0.6).move_to(DOWN * 0.1)
        self.no_overlap(crumb, before, none, partner)
        self.validator.check_in_frame(VGroup(crumb, before, none, partner))

        n = self.narrate(
            id="intro_01",
            text="In lessons one and two, you saw that the sentence selects a word's meaning. In analogies, there's no "
                 "sentence; the other word in the pair does the selecting.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.at_word(n, "selects")
        self.play(FadeIn(before, shift=UP * 0.1))
        self.at_word(n, "no")
        self.play(FadeIn(none, shift=UP * 0.1))
        self.at_word(n, "other")
        self.play(FadeIn(partner, shift=UP * 0.1))
        self.wait_for_narration(n)

        title = fitted_text("Context-Based Analogies", SAFE_W, 72, INK, BOLD)
        underline = Line(LEFT, RIGHT, color=WORD, stroke_width=5).set_width(title.width * 0.6)
        VGroup(title, underline).arrange(DOWN, buff=0.2).move_to(UP * 0.2)
        goals = [("Identify which meaning of a word the analogy uses", WORD),
                 ("Avoid options that belong to another meaning", BAD)]
        rows = VGroup(*[VGroup(pill(str(i + 1), c, size=SMALL), fitted_text(s_, SAFE_W - 2.4, BODY, INK))
                        .arrange(RIGHT, buff=0.35) for i, (s_, c) in enumerate(goals)])
        rows.arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        heading = text("By the end of this video, you will:", LABEL, MUTED, BOLD)
        objectives = self.card(VGroup(heading, rows).arrange(DOWN, buff=0.4, aligned_edge=LEFT))
        small_title = title.copy().scale(0.6)
        small_title.next_to(crumb, DOWN, buff=0.3)
        objectives.next_to(small_title, DOWN, buff=0.35)
        self.validator.check_in_frame(VGroup(crumb, small_title, objectives))
        n = self.narrate(
            id="intro_02",
            text="This video is context-based analogies. By the end, you'll identify which meaning of a word the analogy "
                 "uses, and avoid options that belong to another meaning.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(VGroup(before, none, partner), shift=UP * 0.3))
        self.at_word(n, "context-based")
        self.play(Write(title), run_time=1.1)
        self.play(GrowFromCenter(underline))
        self.at_word(n, "By")
        self.play(FadeOut(underline), ReplacementTransform(title, small_title), run_time=0.8)
        self.play(FadeIn(objectives[0]), FadeIn(heading))
        for row_, spoken in zip(rows, ["identify", "avoid"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row_, shift=RIGHT * 0.2), run_time=0.5)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_intro")

    # ================================================= 1. HOOK ==========

    HOOK = dict(word="REMOTE : ?", options=["cat", "television", "battery", "distance"], key="b",
                traps={"a": "the ANIMAL meaning of “mouse”", "c": "powers the remote", "d": "how it's used"})

    def hook(self):
        self.scene_start("S01_hook", title="Hook")

        h = self.HOOK
        desk = self.desk_card()
        line = desk[1][1]
        q = OptionQuestion(h["word"], h["options"], h["key"], h["traps"])
        opts = q.rows.copy().arrange(RIGHT, buff=0.9)
        notes = VGroup(pill("one option comes from a different meaning of “mouse”", BAD, size=SMALL),
                       pill("your brain will offer it", MUTED, size=SMALL)).arrange(RIGHT, buff=0.4)
        fit_width(notes, SAFE_W)
        opts.next_to(desk, DOWN, buff=0.8)
        notes.next_to(opts, DOWN, buff=0.7)
        self.no_overlap(desk, opts, notes)
        self.validator.check_in_frame(VGroup(desk, opts, notes))

        n = self.narrate(
            id="hook_01",
            text="Look at your desk: a laptop with a mouse, a TV with a remote. Mouse is to computer, as remote is to what?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "desk")
        self.play(FadeIn(desk[0]), FadeIn(desk[1][0]))
        self.at_word(n, "computer")
        self.play(FadeIn(line[:3], shift=RIGHT * 0.2))
        self.at_word(n, "remote", occurrence=2)
        self.play(FadeIn(line[3:], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_02",
            text="Cat, television, battery, or distance? One option comes from a completely different meaning of mouse. "
                 "Your brain will offer it.",
            voice="default",
            subtitle=True,
            pause_after=3.0,
        )
        for row, spoken in zip(opts, ["Cat", "television", "battery", "distance"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=UP * 0.15), run_time=0.35)
        self.at_word(n, "different")
        self.play(FadeIn(notes[0], shift=UP * 0.1))
        self.at_word(n, "brain")
        self.play(FadeIn(notes[1], shift=UP * 0.1))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        self.clear_stage()
        self.scene_end("S01_hook")

    # ============================================== 2. CONCEPT ==========

    def concept(self):
        self.scene_start("S02_concept", title="The Concept")

        head = pill("many analogy words have MORE THAN ONE meaning", BAD, size=LABEL)
        head.move_to(UP * (CARD_TOP - head.height / 2))
        rows = VGroup(*[VGroup(pill(w, WORD, size=BODY), pill(MEANINGS[w][0], MUTED, size=LABEL),
                               text("and", SMALL, MUTED), pill(MEANINGS[w][1], MUTED, size=LABEL))
                        .arrange(RIGHT, buff=0.3) for w in ["mouse", "bank", "school"]])
        rows.arrange(DOWN, buff=0.45, aligned_edge=LEFT)
        fit_width(rows, SAFE_W)
        rows.next_to(head, DOWN, buff=0.7)
        self.no_overlap(head, rows)
        self.validator.check_in_frame(VGroup(head, rows))

        n = self.narrate(
            id="concept_01",
            text="Many analogy words have more than one meaning. Mouse is an animal, and a computer device. Bank is a "
                 "financial institution, and a river's edge. School is a place of learning, and a group of fish.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "more")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        for r, spoken in zip(rows, ["Mouse", "Bank", "School"]):
            self.at_word(n, spoken)
            self.play(FadeIn(r, shift=RIGHT * 0.2), run_time=0.5)
        self.wait_for_narration(n)

        # The partner fixes the meaning.
        keep, drop = fixed_meaning("mouse", "computer")
        fix_head = pill("in A : B, the two words fix each other's meaning", WORD, size=LABEL)
        fix_head.move_to(UP * (CARD_TOP - fix_head.height / 2))
        pair = VGroup(pill("MOUSE", WORD, size=BODY), text(":", BODY, MUTED), pill("COMPUTER", WORD, size=BODY))\
            .arrange(RIGHT, buff=0.3)
        chosen = VGroup(pill(keep + "  ✓", GOOD, size=LABEL), pill(drop + "  ✗", BAD, size=LABEL)).arrange(RIGHT, buff=0.5)
        stay = pill("once fixed, STAY in that meaning", RATIO, size=LABEL)
        traps = pill("options drawn from the other meaning are traps", BAD, size=LABEL)
        body = VGroup(pair, chosen, stay, traps).arrange(DOWN, buff=0.45)
        fit_width(body, SAFE_W)
        body.next_to(fix_head, DOWN, buff=0.5)
        self.no_overlap(fix_head, pair, chosen, stay, traps)
        self.validator.check_in_frame(VGroup(fix_head, body))
        n = self.narrate(
            id="concept_02",
            text="In A, B, the two words fix each other's meaning. Mouse, computer can only mean the device, because only "
                 "the device relates to a computer. Once you've fixed the meaning, stay in that meaning. Options drawn "
                 "from the other meaning are traps.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(VGroup(head, rows)))
        self.at_word(n, "fix")
        self.play(FadeIn(fix_head, shift=DOWN * 0.2))
        self.at_word(n, "Mouse")
        self.play(FadeIn(pair, shift=UP * 0.1))
        self.at_word(n, "device", occurrence=1)
        self.play(FadeIn(chosen[0], shift=UP * 0.1), FadeIn(chosen[1], shift=UP * 0.1))
        self.at_word(n, "stay")
        self.play(FadeIn(stay, shift=UP * 0.1))
        self.at_word(n, "traps")
        self.play(FadeIn(traps, shift=UP * 0.1))
        self.wait_for_narration(n)

        # Domain.
        dom_head = pill("a second kind of context:  DOMAIN", SECOND, size=LABEL)
        dom_head.move_to(UP * (CARD_TOP - dom_head.height / 2))
        dline = analogy_line("Server", "Data", "Warehouse", "Goods")
        dline[6].set_color(SECOND)
        stores = VGroup(text("stores", LABEL, RATIO, BOLD), text("stores", LABEL, RATIO, BOLD))
        func = pill("the same FUNCTION, in two different fields", GOOD, size=LABEL)
        dbody = VGroup(dline, func).arrange(DOWN, buff=1.0)
        fit_width(dbody, SAFE_W)
        dbody.next_to(dom_head, DOWN, buff=1.2)
        stores[0].next_to(VGroup(dline[0], dline[2]), UP, buff=0.15)
        stores[1].next_to(VGroup(dline[4], dline[6]), UP, buff=0.15)
        self.no_overlap(dom_head, stores, dline, func)
        self.validator.check_in_frame(VGroup(dom_head, stores, dbody))
        n = self.narrate(
            id="concept_03",
            text="There's also a second kind of context: domain. Server is to data, as warehouse is to goods, works "
                 "because both are about storing things. Domain analogies ask you to see the same function, in two "
                 "different fields.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(VGroup(fix_head, body)))
        self.at_word(n, "domain")
        self.play(FadeIn(dom_head, shift=DOWN * 0.2))
        self.at_word(n, "Server")
        self.play(FadeIn(dline, shift=UP * 0.1))
        self.at_word(n, "storing")
        self.play(FadeIn(stores, shift=DOWN * 0.1))
        self.at_word(n, "function")
        self.play(FadeIn(func, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_concept")

    # ======================================== 3. WHY YOU NEED IT ==========

    def why_you_need_it(self):
        self.scene_start("S03_why", title="Why You Need It")

        common = pill("double-meaning traps are common in analogy questions", BAD, size=LABEL)
        feels = pill("the wrong option FEELS strongly related", RATIO, size=LABEL)
        gone = pill("know which meaning is in play  →  the trap is gone instantly", GOOD, size=LABEL)
        group = VGroup(common, feels, gone).arrange(DOWN, buff=0.7)
        fit_width(group, SAFE_W).move_to(UP * 0.3)
        self.no_overlap(common, feels, gone)
        self.validator.check_in_frame(group)

        n = self.narrate(
            id="why_01",
            text="Double-meaning traps are common in analogy questions, because the wrong option feels strongly related. "
                 "Recognising which meaning is in play removes them instantly.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "common")
        self.play(FadeIn(common, shift=DOWN * 0.1))
        self.at_word(n, "feels")
        self.play(FadeIn(feels, shift=UP * 0.1))
        self.at_word(n, "Recognising")
        self.play(FadeIn(gone, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_why")

    # ============================================== 4. ANALOGY ==========

    def analogy(self):
        self.scene_start("S04_analogy", title="The Analogy")

        keep, drop = fixed_meaning("mouse", "computer")
        plugs = VGroup(pill("plug 1:  " + drop, MUTED, size=LABEL), pill("plug 2:  " + keep, MUTED, size=LABEL))\
            .arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        adapter = self.card(VGroup(text("the word:  MOUSE", LABEL, WORD, BOLD), plugs).arrange(DOWN, buff=0.35,
                                                                                               aligned_edge=LEFT))
        partner = pill("partner word:  COMPUTER", RATIO, size=LABEL)
        switch = text("flips the switch  →", SMALL, RATIO)
        left = VGroup(partner, switch).arrange(DOWN, buff=0.2)
        top = VGroup(left, adapter).arrange(RIGHT, buff=0.7)
        dead = pill("once it's set, the other plug carries no current", FOCUS, size=LABEL)
        block = VGroup(top, dead).arrange(DOWN, buff=0.6)
        fit_within(block, SAFE_W, SAFE_H - 1.4)
        block.move_to(UP * 0.3)
        self.no_overlap(left, adapter)
        self.no_overlap(top, dead)
        self.validator.check_in_frame(block)

        n = self.narrate(
            id="analogy_01",
            text="A word is a multi-plug adapter. The partner word flips the switch to one plug. Once it's set, the other "
                 "plugs don't carry current.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "adapter")
        self.play(FadeIn(adapter, shift=LEFT * 0.2))
        self.at_word(n, "partner")
        self.play(FadeIn(partner, shift=RIGHT * 0.2))
        self.at_word(n, "switch")
        self.play(FadeIn(switch), plugs[1].animate.set_color(GOOD))
        self.at_word(n, "other")
        self.play(plugs[0].animate.set_opacity(0.3), FadeIn(dead, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_analogy")

    # ======================================== 5-7. WORKED EXAMPLES ==========

    def example_bank(self):
        self.scene_start("S05_ex_bank", title="Worked Example 1")
        self.play(self.pin(self.meaning_pin()))

        keep, drop = fixed_meaning("bank", "river")
        line, marks, b1, b2, answer = self.meaning_example(
            "Bank", "River", "Shore", "sea", [(keep + "  ✓", GOOD), ("not: money  ✗", BAD)],
            "A bank is the edge of a river.", "A shore is the edge of the sea.")

        n = self.narrate(
            id="ex1_01",
            text="Bank is to river, as shore is to what? River fixes the meaning of bank: the edge of water, not money. A "
                 "bank is the edge of a river. So a shore is the edge of the sea.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Bank", occurrence=1)
        self.play(FadeIn(line, shift=DOWN * 0.1))
        self.at_word(n, "fixes")
        self.play(FadeIn(marks[0], shift=RIGHT * 0.2), self.pin_step(0, color=WORD))
        self.at_word(n, "money")
        self.play(FadeIn(marks[1], shift=LEFT * 0.1))
        self.at_word(n, "edge", occurrence=2)
        self.play(FadeIn(b1, shift=RIGHT * 0.2), self.pin_step(1, color=RATIO))
        self.at_word(n, "sea")
        self.play(FadeIn(b2, shift=RIGHT * 0.2), ReplacementTransform(line[6], answer))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_ex_bank")

    def example_school(self):
        self.scene_start("S06_ex_school", title="Worked Example 2")

        keep, drop = fixed_meaning("school", "fish")
        line, marks, b1, b2, answer = self.meaning_example(
            "School", "Fish", "Flock", "birds", [(keep + "  ✓", GOOD), ("not: students  ✗", BAD)],
            "A school is a group of fish.", "A flock is a group of birds (or sheep).")

        n = self.narrate(
            id="ex2_01",
            text="School is to fish, as flock is to what? Fish fixes the meaning of school: a group of animals, not a "
                 "place for students. A school is a group of fish. So a flock is a group of birds, or sheep.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "School", occurrence=1)
        self.play(FadeIn(line, shift=DOWN * 0.1))
        self.at_word(n, "fixes")
        self.play(FadeIn(marks[0], shift=RIGHT * 0.2), self.pin_step(0, color=WORD))
        self.at_word(n, "students")
        self.play(FadeIn(marks[1], shift=LEFT * 0.1))
        self.at_word(n, "group", occurrence=2)
        self.play(FadeIn(b1, shift=RIGHT * 0.2), self.pin_step(1, color=RATIO))
        self.at_word(n, "birds")
        self.play(FadeIn(b2, shift=RIGHT * 0.2), ReplacementTransform(line[6], answer))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_ex_school")

    def example_firewall(self):
        self.scene_start("S07_ex_firewall", title="Worked Example 3")

        line, marks, b1, b2, answer = self.meaning_example(
            "Firewall", "Network", "Lock", "door", [("a DOMAIN analogy", SECOND), ("function:  protects", RATIO)],
            "A firewall protects a network.", "A lock protects a door (or a house).")

        n = self.narrate(
            id="ex3_01",
            text="Firewall is to network, as lock is to what? This is a domain analogy: match the function, not the field. "
                 "A firewall protects a network. So a lock protects a door, or a house.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Firewall", occurrence=1)
        self.play(FadeIn(line, shift=DOWN * 0.1))
        self.at_word(n, "domain")
        self.play(FadeIn(marks[0], shift=RIGHT * 0.2), self.pin_step(3, color=SECOND))
        self.at_word(n, "function")
        self.play(FadeIn(marks[1], shift=LEFT * 0.1))
        self.at_word(n, "protects", occurrence=1)
        self.play(FadeIn(b1, shift=RIGHT * 0.2))
        self.at_word(n, "door")
        self.play(FadeIn(b2, shift=RIGHT * 0.2), ReplacementTransform(line[6], answer))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S07_ex_firewall")

    # ================================================ 8. RULES ==========

    def rules(self):
        self.scene_start("S08_rules", title="Rules")
        self.play(self.unpin())

        rules = VGroup(*[VGroup(pill(str(i + 1), c, size=SMALL), fitted_text(s_, SAFE_W - 2.2, BODY, INK))
                         .arrange(RIGHT, buff=0.3) for i, (s_, c) in enumerate([
                             ("Let the partner word fix the meaning", WORD),
                             ("Stay in that meaning for the whole question", RATIO),
                             ("Strike options from another meaning", BAD),
                             ("Domain analogies: match the FUNCTION, not the field", SECOND)])])
        rules.arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        board = self.card(rules).move_to(UP * 0.3)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="rules_01",
            text="Four rules. First, let the partner word fix the meaning. Second, stay in that meaning for the whole "
                 "question. Third, strike options from another meaning. And fourth, for domain analogies, match the "
                 "function, not the field.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(board[0]))
        for r, spoken in zip(rules, ["First", "Second", "Third", "fourth"]):
            self.at_word(n, spoken)
            self.play(FadeIn(r, shift=RIGHT * 0.2), run_time=0.45)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S08_rules")

    # ============================================== 9. PROCESS ==========

    def process(self):
        self.scene_start("S09_process", title="The Process")

        steps = VGroup(*[VGroup(pill(str(i + 1), c, size=SMALL), fitted_text(s_, SAFE_W - 2.2, BODY, INK))
                         .arrange(RIGHT, buff=0.3) for i, (s_, c) in enumerate([
                             ("Read A : B and fix the meaning of each word", WORD),
                             ("Build the bridge in that meaning", RATIO),
                             ("Apply it to C; strike other-meaning options", BAD),
                             ("Confirm", GOOD)])])
        steps.arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        board = self.card(steps).move_to(UP * 0.3)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="process_01",
            text="The process. First, read A and B, and fix the meaning of each word. Second, build the bridge in that "
                 "meaning. Third, apply it to C, and strike other-meaning options. And fourth, confirm.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(board[0]))
        for r, spoken in zip(steps, ["First", "Second", "Third", "fourth"]):
            self.at_word(n, spoken)
            self.play(FadeIn(r, shift=RIGHT * 0.2), run_time=0.45)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S09_process")

    # ========================================== 10. HOOK, SOLVED ==========

    def hook_solved(self):
        self.scene_start("S10_hook_solved", title="Hook, Solved")
        self.play(self.pin(self.meaning_pin()))

        h = self.HOOK
        keep, drop = fixed_meaning("mouse", "computer")
        cx, w = self.free_area()
        desk = self.desk_card()
        meaning = pill("meaning:  " + keep, GOOD, size=SMALL)
        tail = "a hand-held device used to control"
        b1 = text(f"“A mouse is {tail} a computer.”", LABEL, INK, t2c={tail: RATIO})
        b2 = text(f"“A remote is {tail} a television.”", LABEL, INK, t2c={tail: RATIO, "television": GOOD})
        notes = VGroup(meaning, b1, b2).arrange(DOWN, buff=0.18, aligned_edge=LEFT)
        fit_width(notes, w - 0.8)
        notes.next_to(desk, DOWN, buff=0.3).to_edge(LEFT, buff=SAFE + 0.6)
        q = OptionQuestion(h["word"], h["options"], h["key"], h["traps"], word_size=LABEL)
        fit_height(q.group, notes.get_bottom()[1] - 0.3 - (BOTTOM_Y + 0.6))
        q.group.next_to(notes, DOWN, buff=0.3).to_edge(LEFT, buff=SAFE + 0.6)
        self.no_overlap(desk, notes, q.group)
        self.no_overlap(desk, self.pinned)
        self.no_overlap(notes, self.pinned)
        self.validator.check_in_frame(VGroup(desk, notes, q.group))

        n = self.narrate(
            id="solved_01",
            text="Let's solve the hook. Read: mouse is to computer. Predict. The meaning: the device. The bridge: a mouse "
                 "is a hand-held device used to control a computer. So a remote is a hand-held device used to control a "
                 "television.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(desk), FadeIn(q.word), FadeIn(q.rows))
        self.at_word(n, "Read")
        self.play(Indicate(desk[1][1][:3], color=WORD, scale_factor=1.05))
        self.at_word(n, "Predict")
        self.play(Indicate(desk[1][1][4:], color=FOCUS, scale_factor=1.05))
        self.at_word(n, "meaning")
        self.play(FadeIn(meaning, shift=UP * 0.1), self.pin_step(0, color=WORD))
        self.at_word(n, "bridge")
        self.play(FadeIn(b1, shift=RIGHT * 0.2), self.pin_step(1, color=RATIO))
        self.at_word(n, "remote")
        self.play(FadeIn(b2, shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_02",
            text="Eliminate. Cat is from the animal meaning. A battery powers the remote. Distance describes how it's used.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Eliminate")
        self.play(self.pin_step(2, color=BAD))
        for letter, spoken in [("a", "Cat"), ("c", "battery"), ("d", "Distance")]:
            self.at_word(n, spoken)
            self.play(*q.strike(letter)[1])
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_03",
            text="Confirm: the answer is television.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "answer")
        self.play(*q.confirm()[1])
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S10_hook_solved")

    # ========================================== 11. EXAM PATTERNS ==========

    def exam_patterns(self):
        self.scene_start("S11_patterns", title="Exam Patterns and Solving Models")
        self.play(self.unpin())

        table = self.table_rows(["Pattern", "Solving model"], [
            ["Double-meaning word", "partner word fixes the meaning; strike the other meaning"],
            ["Cross-domain analogy", "match the function (protects, stores, controls)"],
        ], [4.4, 7.4], size=LABEL)
        board = self.card(table, width=SAFE_W - 0.2).move_to(UP * 0.4)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="patterns_01",
            text="Two exam patterns. A double-meaning word: the partner word fixes the meaning, so strike the other "
                 "meaning. And a cross-domain analogy: match the function: protects, stores, controls.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(board[0]), FadeIn(table[0]))
        for row, spoken in zip(table[1:], ["double-meaning", "cross-domain"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.45)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S11_patterns")

    # ======================================== 12. COMMON MISTAKES ==========

    def common_mistakes(self):
        self.scene_start("S12_mistakes", title="Common Mistakes")

        card_w = ZONE_W - 0.3
        pairs = [
            (self.verdict_card(False, "Following the common meaning", card_w),
             self.verdict_card(True, "Use the partner-fixed meaning", card_w)),
            (self.verdict_card(False, "Switching meaning halfway through", card_w),
             self.verdict_card(True, "Stay in one meaning", card_w)),
            (self.verdict_card(False, "Matching fields", card_w),
             self.verdict_card(True, "Match FUNCTIONS", card_w)),
        ]
        for (wrong, right), yy in zip(pairs, [1.6, 0.05, -1.5]):
            wrong.move_to(LEFT_ZONE + UP * yy)
            right.move_to(RIGHT_ZONE + UP * yy)
        header = pill("3 mistakes", BAD, size=LABEL).move_to(UP * (CARD_TOP - 0.3))
        self.validator.check_in_frame(VGroup(header, *[c for p in pairs for c in p]))

        n = self.narrate(
            id="mistakes_01",
            text="Three common mistakes. The first is following the common meaning, instead of the partner-fixed one. The "
                 "second is switching meaning halfway through. The third is matching fields, instead of functions.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(header))
        for pr, spoken in zip(pairs, ["first", "second", "third"]):
            self.at_word(n, spoken)
            self.play(FadeIn(pr[0], shift=RIGHT * 0.3), FadeIn(pr[1], shift=LEFT * 0.3))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S12_mistakes")

    # ============================================== 13. PRACTICE ==========

    PRACTICE = [
        (("Key", "Lock", "Password"), ["keyboard", "letter", "secret", "account"], "d", "opens, or grants access to"),
        (("Bank", "Money", "Library"), ["books", "river", "reading", "silence"], "a",
         "stores and lends;  (b) river: the other meaning of “bank”"),
        (("Scale", "Fish", "Feather"), ["weight", "music", "bird", "pen"], "c",
         "scale = the fish's covering;  (a), (b): other meanings of “scale”"),
    ]

    def practice(self):
        self.scene_start("S13_practice", title="Practice Questions")

        lines = VGroup(*[VGroup(VGroup(pill(str(i + 1), FOCUS, size=SMALL), analogy_line(*abc, size=LABEL))
                                .arrange(RIGHT, buff=0.35),
                                text("   ".join(f"({l}) {o}" for l, o in zip("abcd", opts)), LABEL, INK))
                         .arrange(DOWN, buff=0.2, aligned_edge=LEFT)
                         for i, (abc, opts, *_r) in enumerate(self.PRACTICE)])
        lines.arrange(DOWN, buff=0.45, aligned_edge=LEFT)
        board = self.card(lines, color=FOCUS)
        fit_within(board, SAFE_W, SAFE_H - 1.2)
        board.move_to(UP * 0.4)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="practice_01",
            text="Your turn. One: key is to lock, as password is to what? Keyboard, letter, secret, or account? Two: bank "
                 "is to money, as library is to what? Books, river, reading, or silence? Three: scale is to fish, as "
                 "feather is to what? Weight, music, bird, or pen?",
            voice="default",
            subtitle=True,
            pause_after=10.0,
        )
        self.play(FadeIn(board[0]))
        for ln, (spoken, first_option) in zip(lines, [("key", "Keyboard"), ("bank", "Books"), ("scale", "Weight")]):
            self.at_word(n, spoken)
            self.play(FadeIn(ln[0], shift=UP * 0.15), run_time=0.4)
            self.at_word(n, first_option)
            self.play(FadeIn(ln[1], shift=LEFT * 0.15), run_time=0.4)
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        self.clear_stage()
        self.scene_end("S13_practice")

    # =============================================== 14. ANSWERS ==========

    def answers(self):
        self.scene_start("S14_answers", title="Answers")

        assert fixed_meaning("scale", "fish")[0] == "a fish's covering"
        rows = VGroup(*[VGroup(analogy_line(*abc, opts["abcd".index(key)], size=LABEL), text(why, SMALL, RATIO))
                        .arrange(DOWN, buff=0.18, aligned_edge=LEFT) for abc, opts, key, why in self.PRACTICE])
        rows.arrange(DOWN, buff=0.5, aligned_edge=LEFT)
        fit_within(rows, SAFE_W, SAFE_H - 1.2)
        rows.move_to(UP * 0.3)
        self.validator.check_in_frame(rows)

        n = self.narrate(
            id="answers_01",
            text="One: account. A key opens a lock; a password grants access to an account. Two: books. A bank stores and "
                 "lends money; river comes from the other meaning of bank. Three: bird. Scale here is the fish's covering; "
                 "weight and music are other meanings of scale.",
            voice="default",
            subtitle=True,
        )
        for r, (spoken, why) in zip(rows, [("account", "opens"), ("books", "stores"), ("bird", "covering")]):
            self.at_word(n, spoken, occurrence=1)
            self.play(FadeIn(r[0], shift=RIGHT * 0.2), run_time=0.5)
            self.at_word(n, why)
            self.play(FadeIn(r[1], shift=LEFT * 0.1), run_time=0.4)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S14_answers")

    # ================================================ 15. RECAP ==========

    def recap(self):
        self.scene_start("S15_recap", title="Recap Card")

        card, table = self.recap_card("Recap Card: Video 4", [
            ["Partner word", "fixes the meaning"],
            ["Stay", "in one meaning throughout"],
            ["Domain", "match the function across fields"],
        ])
        card.move_to(UP * 0.2)
        self.validator.check_in_frame(card)

        n = self.narrate(
            id="recap_01",
            text="To recap. The partner word fixes the meaning. Stay in one meaning throughout. And for domain analogies, "
                 "match the function across fields.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(card[0]), FadeIn(table[0]))
        for row, spoken in zip(table[1:], ["partner", "Stay", "domain"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.45)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S15_recap")

    # ================================================= 16. NEXT ==========

    def next_video(self):
        self.scene_start("S16_next", title="Next")

        mixes = VGroup(*[pill(t, BAD, size=LABEL) for t in ["reversed order", "direction of degree", "part vs whole"]])\
            .arrange(RIGHT, buff=0.4)
        label = text("the patterns people mix up", LABEL, MUTED)
        nxt = pill("Next:  Commonly Confused Analogy Patterns", FOCUS, size=LABEL)
        group = VGroup(label, mixes, nxt).arrange(DOWN, buff=0.6)
        fit_width(group, SAFE_W).move_to(UP * 0.2)
        self.no_overlap(label, mixes, nxt)
        self.validator.check_in_frame(group)

        n = self.narrate(
            id="next_01",
            text="Video five covers the patterns people mix up: reversed order, direction of degree, and part versus "
                 "whole.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Video")
        self.play(FadeIn(nxt, scale=1.05), FadeIn(label))
        for m, spoken in zip(mixes, ["reversed", "degree", "part"]):
            self.at_word(n, spoken)
            self.play(FadeIn(m, shift=UP * 0.1), run_time=0.4)
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S16_next")

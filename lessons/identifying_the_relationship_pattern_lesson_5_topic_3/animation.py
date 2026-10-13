"""
animation.py for the LMS video generator.

Course : C-CAT - Section A - English
Module : Module 1 - Vocabulary
Lesson : Lesson 5 - Analogies
Video  : 03 - Identifying the Relationship Pattern (Video 3 of 7)

Source script:
  C:\\Users\\User\\Downloads\\C-CAT_SectionA_Module1_English\\English\\Module 1 - Vocabulary\\
  Lesson 5 - Analogies\\03 - Identifying the Relationship Pattern.pdf

Built on the golden-reference pattern:
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``;
  * layouts stacked with next_to and guarded with ``no_overlap``; nothing is
    ever animated onto or into another box.

The three refining questions live in REFINERS (level, function, direction); each worked example shows the loose first bridge, the refined bridge and then strikes the options the refinement removes.
The "refine the bridge" card (level, function, direction, stop when one option fits) stays pinned top-right through the worked examples and Hook, Solved.
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

REFINERS = [("LEVEL", "specific item, or general field?", WORD), ("FUNCTION", "made, used, or where it happens?", RATIO),
            ("DIRECTION", "who does what to whom?", SECOND)]


def analogy_line(a, b, c, d="?", size=BODY):
    """A : B :: C : D as chips.  [0], [2] = first pair;  [4], [6] = second pair."""
    return VGroup(pill(a, WORD, size=size), text(":", size, MUTED), pill(b, WORD, size=size), text("::", size, MUTED),
                  pill(c, SECOND, size=size), text(":", size, MUTED),
                  pill(d, FOCUS if d == "?" else GOOD, size=size)).arrange(RIGHT, buff=0.25)


class IdentifyingThePatternVideo(LMSScene):
    lesson_title = "Identifying the Relationship Pattern"

    def construct(self):
        self.camera.background_color = BG

        self.lesson_intro()
        self.hook()
        self.concept()
        self.why_you_need_it()
        self.analogy()
        self.example_poem()
        self.example_keyboard()
        self.example_tree()
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

    def refine_pin(self):
        return self.steps_pin("refine the bridge", [("LEVEL: item or field?", WORD), ("FUNCTION: made? used?", RATIO),
                                                    ("DIRECTION: who does what?", SECOND),
                                                    ("stop when ONE option fits", GOOD)])

    def test_card(self):
        head = text("MUSIC SCHOOL  ·  entrance aptitude test", SMALL, RATIO, BOLD)
        line = analogy_line("AUTHOR", "NOVEL", "COMPOSER", size=LABEL)
        cx, w = self.free_area()
        body = VGroup(head, line).arrange(DOWN, buff=0.25, aligned_edge=LEFT)
        fit_width(body, min(w - 1.4, SAFE_W - 1.8))
        card = self.card(body, width=min(w - 0.2, SAFE_W - 0.4))
        return card.move_to(RIGHT * cx + UP * (CARD_TOP - card.height / 2))

    def refine_example(self, a, b, c, options, key, traps, first, refined):
        """Analogy line, the loose first bridge, the refined bridge, and the options, beside the pinned panel."""
        cx, w = self.free_area()
        line = analogy_line(a, b, c, size=LABEL)
        notes = VGroup(VGroup(pill("first bridge", MUTED, size=SMALL), text(first, LABEL, INK)).arrange(RIGHT, buff=0.25),
                       VGroup(pill("refine", WORD, size=SMALL), text(refined, LABEL, WORD)).arrange(RIGHT, buff=0.25))\
            .arrange(DOWN, buff=0.25, aligned_edge=LEFT)
        fit_width(notes, w - 0.8)
        q = OptionQuestion(f"{c} : ?", options, key, traps, word_size=LABEL)
        block = VGroup(line, notes, q.rows).arrange(DOWN, buff=0.45, aligned_edge=LEFT)
        fit_height(block, SAFE_H - 1.6)
        block.to_edge(LEFT, buff=SAFE + 0.6).set_y(0.1)
        self.no_overlap(line, notes, q.rows)
        self.no_overlap(block, self.pinned)
        self.validator.check_in_frame(block)
        return line, notes, q

    # ========================================= 0. LESSON INTRO ==========

    def lesson_intro(self):
        self.scene_start("S00_intro", title="Lesson Introduction")

        crumb = self.breadcrumb("English · Module 1 Vocabulary", "Lesson 5 · Analogies", "Video 3")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        ready = pill("Video 2: ready-made bridges, by type", MUTED, size=LABEL)
        sharpen = pill("today: we SHARPEN them", WORD, size=LABEL)
        decide = pill("two options survive?  a more specific bridge decides", GOOD, size=LABEL)
        VGroup(ready, sharpen, decide).arrange(DOWN, buff=0.6).move_to(DOWN * 0.1)
        self.no_overlap(crumb, ready, sharpen, decide)
        self.validator.check_in_frame(VGroup(crumb, ready, sharpen, decide))

        n = self.narrate(
            id="intro_01",
            text="Video two gave you ready-made bridges by type. Today we sharpen them: when two options survive, a more "
                 "specific bridge decides.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.at_word(n, "ready-made")
        self.play(FadeIn(ready, shift=UP * 0.1))
        self.at_word(n, "sharpen")
        self.play(FadeIn(sharpen, shift=UP * 0.1))
        self.at_word(n, "survive")
        self.play(FadeIn(decide, shift=UP * 0.1))
        self.wait_for_narration(n)

        title = fitted_text("Identifying the Relationship Pattern", SAFE_W, 64, INK, BOLD)
        underline = Line(LEFT, RIGHT, color=WORD, stroke_width=5).set_width(title.width * 0.6)
        VGroup(title, underline).arrange(DOWN, buff=0.2).move_to(UP * 0.2)
        goals = [("Refine a bridge sentence until it picks one answer", WORD),
                 ("Use specificity to separate a general answer from an exact one", GOOD)]
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
            text="This video is identifying the relationship pattern. By the end, you'll refine a bridge sentence until it "
                 "picks one answer, and use specificity to separate a general answer from an exact one.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(VGroup(ready, sharpen, decide), shift=UP * 0.3))
        self.at_word(n, "identifying")
        self.play(Write(title), run_time=1.1)
        self.play(GrowFromCenter(underline))
        self.at_word(n, "By")
        self.play(FadeOut(underline), ReplacementTransform(title, small_title), run_time=0.8)
        self.play(FadeIn(objectives[0]), FadeIn(heading))
        for row_, spoken in zip(rows, ["refine", "specificity"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row_, shift=RIGHT * 0.2), run_time=0.5)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_intro")

    # ================================================= 1. HOOK ==========

    HOOK = dict(word="COMPOSER : ?", options=["music", "orchestra", "symphony", "piano"], key="c",
                traps={"a": "the whole field: wrong level", "b": "performs the work", "d": "an instrument: a tool"})

    def hook(self):
        self.scene_start("S01_hook", title="Hook")

        h = self.HOOK
        card = self.test_card()
        line = card[1][1]
        q = OptionQuestion(h["word"], h["options"], h["key"], h["traps"])
        opts = q.rows.copy().arrange(RIGHT, buff=0.9)
        notes = VGroup(pill("“music” looks right…", MUTED, size=SMALL),
                       pill("…but the bridge says something more SPECIFIC", GOOD, size=SMALL)).arrange(RIGHT, buff=0.4)
        fit_width(notes, SAFE_W)
        opts.next_to(card, DOWN, buff=0.8)
        notes.next_to(opts, DOWN, buff=0.7)
        self.no_overlap(card, opts, notes)
        self.validator.check_in_frame(VGroup(card, opts, notes))

        n = self.narrate(
            id="hook_01",
            text="A music school's entrance aptitude test asks: author is to novel, as composer is to what?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "test")
        self.play(FadeIn(card[0]), FadeIn(card[1][0]))
        self.at_word(n, "author")
        self.play(FadeIn(line[:3], shift=RIGHT * 0.2))
        self.at_word(n, "composer")
        self.play(FadeIn(line[3:], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_02",
            text="Music, orchestra, symphony, or piano? Music looks right. But the bridge says something more specific, and "
                 "that's where marks are won.",
            voice="default",
            subtitle=True,
            pause_after=3.0,
        )
        for row, (spoken, occ) in zip(opts, [("Music", 1), ("orchestra", 1), ("symphony", 1), ("piano", 1)]):
            self.at_word(n, spoken, occurrence=occ)
            self.play(FadeIn(row, shift=UP * 0.15), run_time=0.35)
        self.at_word(n, "looks")
        self.play(FadeIn(notes[0], shift=UP * 0.1))
        self.at_word(n, "specific")
        self.play(FadeIn(notes[1], shift=UP * 0.1))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        self.clear_stage()
        self.scene_end("S01_hook")

    # ============================================== 2. CONCEPT ==========

    def concept(self):
        self.scene_start("S02_concept", title="The Concept")

        head = pill("a first bridge is often too LOOSE", BAD, size=LABEL)
        head.move_to(UP * (CARD_TOP - head.height / 2))
        loose = VGroup(
            VGroup(text("“An author is connected to a novel.”", LABEL, INK, t2c={"is connected to": BAD}),
                   text("fits almost anything", SMALL, BAD)).arrange(RIGHT, buff=0.4),
            VGroup(text("“An author creates a novel.”", LABEL, INK, t2c={"creates": RATIO}),
                   text("two options may still pass", SMALL, RATIO)).arrange(RIGHT, buff=0.4))\
            .arrange(DOWN, buff=0.45, aligned_edge=LEFT)
        fix = pill("the fix: REFINE: add the detail true of the first pair, and nothing else", GOOD, size=SMALL)
        body = VGroup(loose, fix).arrange(DOWN, buff=0.6)
        fit_width(body, SAFE_W)
        body.next_to(head, DOWN, buff=0.7)
        self.no_overlap(head, loose, fix)
        self.validator.check_in_frame(VGroup(head, body))

        n = self.narrate(
            id="concept_01",
            text="A first bridge is often too loose. An author is connected to a novel fits almost anything. Even an "
                 "author creates a novel might let two options through. The fix is to refine the bridge, by adding the "
                 "detail that makes it true of the first pair, and nothing else.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "loose")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "connected")
        self.play(FadeIn(loose[0], shift=RIGHT * 0.2))
        self.at_word(n, "creates")
        self.play(FadeIn(loose[1], shift=RIGHT * 0.2))
        self.at_word(n, "refine")
        self.play(FadeIn(fix, shift=UP * 0.1))
        self.wait_for_narration(n)

        # Three refining questions.
        ask = pill("three refining questions", FOCUS, size=LABEL)
        ask.move_to(UP * (CARD_TOP - ask.height / 2))
        answers = ["a novel: a specific kind of work, not “literature”", "a novel is MADE",
                   "the author WRITES the novel"]
        qs = VGroup(*[VGroup(VGroup(pill(name, c, size=LABEL), text(q_, LABEL, INK)).arrange(RIGHT, buff=0.3),
                             text("→  " + ans, LABEL, c)).arrange(DOWN, buff=0.12, aligned_edge=LEFT)
                      for (name, q_, c), ans in zip(REFINERS, answers)]).arrange(DOWN, buff=0.4, aligned_edge=LEFT)
        fit_within(qs, SAFE_W, SAFE_H - ask.height - 1.6)
        qs.next_to(ask, DOWN, buff=0.5)
        self.no_overlap(ask, qs)
        self.validator.check_in_frame(VGroup(ask, qs))
        n = self.narrate(
            id="concept_02",
            text="Ask three refining questions. Is B a specific item, or a general field? A novel is a specific kind of "
                 "work, not literature. Is B made, used, or where it happens? A novel is made. Who does what to whom? The "
                 "author writes the novel.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(VGroup(head, body)))
        self.at_word(n, "three")
        self.play(FadeIn(ask, shift=DOWN * 0.2))
        for row, (question, q_occ, answer, a_occ) in zip(qs, [("item", 1, "literature", 1), ("used", 1, "made", 2),
                                                              ("Who", 1, "writes", 1)]):
            self.at_word(n, question, occurrence=q_occ)
            self.play(FadeIn(row[0], shift=RIGHT * 0.2), run_time=0.45)
            self.at_word(n, answer, occurrence=a_occ)
            self.play(FadeIn(row[1], shift=UP * 0.1), run_time=0.4)
        self.wait_for_narration(n)

        # The refined bridge, carried across.
        tail = "a specific long work in their field"
        b1 = text(f"“An author writes a novel, {tail}.”", LABEL, INK, t2c={"writes": RATIO, tail: WORD})
        b2 = text(f"“A composer writes a symphony, {tail}.”", LABEL, INK, t2c={"writes": RATIO, tail: WORD,
                                                                              "symphony": GOOD})
        fails = pill("music = the whole field  ✗  fails “a specific work”", BAD, size=LABEL)
        rb = VGroup(pill("the refined bridge", GOOD, size=LABEL), b1, b2, fails).arrange(DOWN, buff=0.5)
        fit_width(rb, SAFE_W).move_to(UP * 0.3)
        self.validator.check_in_frame(rb)
        n = self.narrate(
            id="concept_03",
            text="The refined bridge: an author writes a novel, a specific long work in their field. Carry it across: a "
                 "composer writes a symphony, a specific long work in their field. Now music, the whole field, fails the "
                 "specific-work part.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(VGroup(ask, qs)))
        self.at_word(n, "refined")
        self.play(FadeIn(rb[0], shift=DOWN * 0.1), FadeIn(b1, shift=UP * 0.1))
        self.at_word(n, "Carry")
        self.play(FadeIn(b2, shift=UP * 0.1))
        self.at_word(n, "music")
        self.play(FadeIn(fails, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_concept")

    # ======================================== 3. WHY YOU NEED IT ==========

    def why_you_need_it(self):
        self.scene_start("S03_why", title="Why You Need It")

        built = pill("harder questions are built with TWO plausible answers", BAD, size=LABEL)
        two = VGroup(pill("a general one", MUTED, size=BODY), pill("an exact one", GOOD, size=BODY)).arrange(RIGHT, buff=0.8)
        only = pill("refining the bridge: the only reliable way to separate them", WORD, size=LABEL)
        group = VGroup(built, two, only).arrange(DOWN, buff=0.7)
        fit_width(group, SAFE_W).move_to(UP * 0.3)
        self.no_overlap(built, two, only)
        self.validator.check_in_frame(group)

        n = self.narrate(
            id="why_01",
            text="Harder analogy questions are built with two plausible answers: a general one, and an exact one. Refining "
                 "the bridge is the only reliable way to separate them.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "plausible")
        self.play(FadeIn(built, shift=DOWN * 0.1))
        self.at_word(n, "general")
        self.play(FadeIn(two[0], shift=UP * 0.1))
        self.at_word(n, "exact")
        self.play(FadeIn(two[1], shift=UP * 0.1))
        self.at_word(n, "Refining")
        self.play(FadeIn(only, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_why")

    # ============================================== 4. ANALOGY ==========

    def analogy(self):
        self.scene_start("S04_analogy", title="The Analogy")

        bar = self.card(VGroup(text("search:", SMALL, MUTED), text("author novel", BODY, INK)).arrange(RIGHT, buff=0.3),
                        width=6.4)
        many = text("≈ 300 results", LABEL, BAD)
        filters = VGroup(pill("+ a specific work", WORD, size=SMALL), pill("+ writes it", RATIO, size=SMALL))\
            .arrange(RIGHT, buff=0.3)
        one = pill("1 result", GOOD, size=BODY)
        same = pill("a refined bridge = a search with the right filters", FOCUS, size=LABEL)
        block = VGroup(bar, many, filters, one, same).arrange(DOWN, buff=0.4)
        fit_within(block, SAFE_W, SAFE_H - 1.4)
        block.move_to(UP * 0.3)
        self.no_overlap(bar, many, filters, one, same)
        self.validator.check_in_frame(block)

        n = self.narrate(
            id="analogy_01",
            text="A vague search returns hundreds of results. Add precise filters, and one result remains. A refined bridge "
                 "is a search with the right filters.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "vague")
        self.play(FadeIn(bar, shift=DOWN * 0.1))
        self.at_word(n, "hundreds")
        self.play(FadeIn(many, shift=UP * 0.1))
        self.at_word(n, "filters", occurrence=1)
        self.play(LaggedStart(*[FadeIn(f, shift=UP * 0.1) for f in filters], lag_ratio=0.4))
        self.at_word(n, "one")
        self.play(FadeIn(one, scale=1.1))
        self.at_word(n, "refined")
        self.play(FadeIn(same, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_analogy")

    # ======================================== 5-7. WORKED EXAMPLES ==========

    def example_poem(self):
        self.scene_start("S05_ex_poem", title="Worked Example 1")
        self.play(self.pin(self.refine_pin()))

        line, notes, q = self.refine_example(
            "Sculptor", "Statue", "Poet", ["poetry", "poem", "pen", "verse"], "b",
            {"a": "the whole field", "c": "the tool", "d": "only a part"},
            "a sculptor makes a statue", "a statue = ONE specific work")

        n = self.narrate(
            id="ex1_01",
            text="Sculptor is to statue, as poet is to what? Poetry, poem, pen, or verse? First bridge: a sculptor makes a "
                 "statue. Refine on level: a statue is one specific work. So: a poem. Poetry is the whole field. A pen is "
                 "the tool, and a verse is only a part.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Sculptor", occurrence=1)
        self.play(FadeIn(line, shift=DOWN * 0.1))
        self.at_word(n, "Poetry", occurrence=1)
        self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.2) for r in q.rows], lag_ratio=0.2))
        self.at_word(n, "bridge")
        self.play(FadeIn(notes[0], shift=RIGHT * 0.2))
        self.at_word(n, "Refine")
        self.play(FadeIn(notes[1], shift=RIGHT * 0.2), self.pin_step(0, color=WORD))
        self.at_word(n, "poem", occurrence=2)
        self.play(*q.confirm()[1], self.pin_step(3, color=GOOD))
        self.at_word(n, "Poetry", occurrence=2)
        self.play(*q.strike("a")[1])
        self.at_word(n, "pen", occurrence=2)
        self.play(*q.strike("c")[1], *q.strike("d")[1])
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_ex_poem")

    def example_keyboard(self):
        self.scene_start("S06_ex_keyboard", title="Worked Example 2")

        line, notes, q = self.refine_example(
            "Petal", "Flower", "Key", ["lock", "keyboard", "door", "music"], "b",
            {"a": "used WITH a key", "c": "used WITH a key", "d": "another meaning of “key”"},
            "a petal is part of a flower", "ONE OF MANY identical parts of")

        n = self.narrate(
            id="ex2_01",
            text="Petal is to flower, as key is to what? Lock, keyboard, door, or music? First bridge: a petal is part of a "
                 "flower. Refine: one of many identical parts of. So: a keyboard. A lock and a door are used with a key; "
                 "they aren't made of keys. And music uses another meaning of key.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Petal", occurrence=1)
        self.play(FadeIn(line, shift=DOWN * 0.1))
        self.at_word(n, "Lock", occurrence=1)
        self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.2) for r in q.rows], lag_ratio=0.2))
        self.at_word(n, "bridge")
        self.play(FadeIn(notes[0], shift=RIGHT * 0.2))
        self.at_word(n, "Refine")
        self.play(FadeIn(notes[1], shift=RIGHT * 0.2), self.pin_step(0, color=WORD))
        self.at_word(n, "keyboard", occurrence=2)
        self.play(*q.confirm()[1], self.pin_step(3, color=GOOD))
        self.at_word(n, "lock", occurrence=2)
        self.play(*q.strike("a")[1], *q.strike("c")[1])
        self.at_word(n, "music", occurrence=2)
        self.play(*q.strike("d")[1])
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_ex_keyboard")

    def example_tree(self):
        self.scene_start("S07_ex_tree", title="Worked Example 3")

        line, notes, q = self.refine_example(
            "Kitten", "Cat", "Sapling", ["seed", "tree", "plant", "forest"], "b",
            {"a": "comes earlier", "c": "too general", "d": "a group"},
            "a kitten is a young cat", "the YOUNG FORM of one specific thing")

        n = self.narrate(
            id="ex3_01",
            text="Kitten is to cat, as sapling is to what? Seed, tree, plant, or forest? First bridge: a kitten is a young "
                 "cat. Refine: the young form of one specific thing. So: a tree. Plant is too general. A seed comes "
                 "earlier, and a forest is a group.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Kitten", occurrence=1)
        self.play(FadeIn(line, shift=DOWN * 0.1))
        self.at_word(n, "Seed", occurrence=1)
        self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.2) for r in q.rows], lag_ratio=0.2))
        self.at_word(n, "bridge")
        self.play(FadeIn(notes[0], shift=RIGHT * 0.2))
        self.at_word(n, "Refine")
        self.play(FadeIn(notes[1], shift=RIGHT * 0.2), self.pin_step(0, color=WORD))
        self.at_word(n, "tree", occurrence=2)
        self.play(*q.confirm()[1], self.pin_step(3, color=GOOD))
        self.at_word(n, "Plant", occurrence=2)
        self.play(*q.strike("c")[1])
        self.at_word(n, "seed", occurrence=2)
        self.play(*q.strike("a")[1], *q.strike("d")[1])
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S07_ex_tree")

    # ================================================ 8. RULES ==========

    def rules(self):
        self.scene_start("S08_rules", title="Rules")
        self.play(self.unpin())

        rules = VGroup(*[VGroup(pill(str(i + 1), c, size=SMALL), fitted_text(s_, SAFE_W - 2.2, BODY, INK))
                         .arrange(RIGHT, buff=0.3) for i, (s_, c) in enumerate([
                             ("Start with the type's bridge, then add detail", RATIO),
                             ("Specific item or general field?  Match the LEVEL", WORD),
                             ("Check the DIRECTION: who does what to whom", SECOND),
                             ("Stop refining when only one option fits", GOOD)])])
        rules.arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        board = self.card(rules).move_to(UP * 0.3)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="rules_01",
            text="Four rules. Rule one: start with the type's bridge, then add detail. Rule two: ask, specific item, or "
                 "general field? Match the level. Rule three: check the direction: who does what to whom. And rule four: "
                 "stop refining when only one option fits.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(board[0]))
        self.at_word(n, "one")
        self.play(FadeIn(rules[0], shift=RIGHT * 0.2), run_time=0.45)
        self.at_word(n, "two")
        self.play(FadeIn(rules[1], shift=RIGHT * 0.2), run_time=0.45)
        self.at_word(n, "Match")
        self.play(Indicate(rules[1][1], color=WORD, scale_factor=1.03))
        self.at_word(n, "three")
        self.play(FadeIn(rules[2], shift=RIGHT * 0.2), run_time=0.45)
        self.at_word(n, "four", occurrence=2)
        self.play(FadeIn(rules[3], shift=RIGHT * 0.2), run_time=0.45)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S08_rules")

    # ============================================== 9. PROCESS ==========

    def process(self):
        self.scene_start("S09_process", title="The Process")

        steps = VGroup(*[VGroup(pill(str(i + 1), c, size=SMALL), fitted_text(s_, SAFE_W - 2.2, BODY, INK))
                         .arrange(RIGHT, buff=0.3) for i, (s_, c) in enumerate([
                             ("Write the first bridge", RATIO),
                             ("Test it on all options.  More than one fits?  Refine", BAD),
                             ("Add level (specific or general), function or direction", WORD),
                             ("Re-test until one remains", GOOD)])])
        steps.arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        board = self.card(steps).move_to(UP * 0.3)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="process_01",
            text="The process. Step one: write the first bridge. Step two: test it on all options; if more than one fits, "
                 "refine. Step three: add level, function or direction. And step four: re-test, until one remains.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(board[0]))
        for r, (spoken, occ) in zip(steps, [("one", 1), ("two", 1), ("three", 1), ("four", 1)]):
            self.at_word(n, spoken, occurrence=occ)
            self.play(FadeIn(r, shift=RIGHT * 0.2), run_time=0.45)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S09_process")

    # ========================================== 10. HOOK, SOLVED ==========

    def hook_solved(self):
        self.scene_start("S10_hook_solved", title="Hook, Solved")
        self.play(self.pin(self.refine_pin()))

        h = self.HOOK
        cx, w = self.free_area()
        card = self.test_card()
        tail = "a specific long work"
        b1 = text(f"“An author writes a novel, {tail}.”", LABEL, INK, t2c={"writes": RATIO, tail: WORD})
        b2 = text("“A composer writes a symphony.”", LABEL, INK, t2c={"writes": RATIO, "symphony": GOOD})
        bridges = VGroup(b1, b2).arrange(DOWN, buff=0.2, aligned_edge=LEFT)
        fit_width(bridges, w - 0.8)
        bridges.next_to(card, DOWN, buff=0.3).to_edge(LEFT, buff=SAFE + 0.6)
        q = OptionQuestion(h["word"], h["options"], h["key"], h["traps"], word_size=LABEL)
        fit_height(q.group, bridges.get_bottom()[1] - 0.3 - (BOTTOM_Y + 0.6))
        q.group.next_to(bridges, DOWN, buff=0.3).to_edge(LEFT, buff=SAFE + 0.6)
        self.no_overlap(card, bridges, q.group)
        self.no_overlap(card, self.pinned)
        self.no_overlap(bridges, self.pinned)
        self.validator.check_in_frame(VGroup(card, bridges, q.group))

        n = self.narrate(
            id="solved_01",
            text="Let's solve the hook. Read: author is to novel. Predict, with a refined bridge: an author writes a novel, "
                 "a specific long work. So a composer writes a symphony.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(card), FadeIn(q.word), FadeIn(q.rows))
        self.at_word(n, "Read")
        self.play(Indicate(card[1][1][:3], color=WORD, scale_factor=1.05))
        self.at_word(n, "refined")
        self.play(FadeIn(b1, shift=RIGHT * 0.2), self.pin_step(0, color=WORD))
        self.at_word(n, "composer")
        self.play(FadeIn(b2, shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_02",
            text="Eliminate. Music is the whole field: the wrong level. An orchestra performs the work. A piano is an "
                 "instrument: a tool.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Eliminate")
        self.play(Indicate(q.rows, color=BAD, scale_factor=1.02))
        for letter, spoken in [("a", "Music"), ("b", "orchestra"), ("d", "piano")]:
            self.at_word(n, spoken)
            self.play(*q.strike(letter)[1])
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_03",
            text="Confirm: both bridges now read the same. The answer is symphony.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Confirm")
        self.play(Indicate(bridges, color=GOOD, scale_factor=1.02), self.pin_step(3, color=GOOD))
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
            ["General vs specific option", "match the level of B"],
            ["Two options fit the type", "refine with function or direction"],
            ["Pair questions", "refine, then test each pair"],
        ], [5.4, 6.4], size=LABEL)
        board = self.card(table, width=SAFE_W - 0.2).move_to(UP * 0.4)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="patterns_01",
            text="Three exam patterns. A general option against a specific one: match the level of B. Two options fit the "
                 "type: refine with function or direction. And pair questions: refine, then test each pair.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(board[0]), FadeIn(table[0]))
        for row, spoken in zip(table[1:], ["general", "Two", "pair"]):
            self.at_word(n, spoken, occurrence=1)
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.45)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S11_patterns")

    # ======================================== 12. COMMON MISTAKES ==========

    def common_mistakes(self):
        self.scene_start("S12_mistakes", title="Common Mistakes")

        card_w = ZONE_W - 0.3
        pairs = [
            (self.verdict_card(False, "Stopping at a loose bridge", card_w),
             self.verdict_card(True, "Refine until one option fits", card_w)),
            (self.verdict_card(False, "The whole field, not the specific item", card_w),
             self.verdict_card(True, "Match the level: novel → symphony", card_w)),
            (self.verdict_card(False, "The performer for the creator", card_w),
             self.verdict_card(True, "orchestra performs;  composer creates", card_w)),
        ]
        for (wrong, right), yy in zip(pairs, [1.6, 0.05, -1.5]):
            wrong.move_to(LEFT_ZONE + UP * yy)
            right.move_to(RIGHT_ZONE + UP * yy)
        header = pill("3 mistakes", BAD, size=LABEL).move_to(UP * (CARD_TOP - 0.3))
        self.validator.check_in_frame(VGroup(header, *[c for p in pairs for c in p]))

        n = self.narrate(
            id="mistakes_01",
            text="Three common mistakes. The first is stopping at a loose bridge. The second is choosing the whole field, "
                 "instead of the specific item. The third is confusing the performer, like the orchestra, with the "
                 "creator.",
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
        (("Chapter", "Book", "Scene"), ["play", "actor", "stage", "theatre"], "a",
         "a scene is a section of a play;  (c) and (d) are places"),
        (("Architect", "Blueprint", "Composer"), ["song", "score", "concert", "singer"], "b",
         "the written plan, before the work is performed or built"),
        (("Leaf", "Tree", "Feather"), ["wing", "pillow", "fly", "bird"], "d",
         "one of many parts covering the whole;  (a) a wing is too narrow a whole"),
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
            text="Your turn. One: chapter is to book, as scene is to what? Play, actor, stage, or theatre? Two: architect "
                 "is to blueprint, as composer is to what? Song, score, concert, or singer? Three: leaf is to tree, as "
                 "feather is to what? Wing, pillow, fly, or bird?",
            voice="default",
            subtitle=True,
            pause_after=10.0,
        )
        self.play(FadeIn(board[0]))
        for ln, (spoken, first_option) in zip(lines, [("chapter", "Play"), ("architect", "Song"), ("leaf", "Wing")]):
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

        rows = VGroup(*[VGroup(analogy_line(*abc, opts["abcd".index(key)], size=LABEL), text(why, SMALL, RATIO))
                        .arrange(DOWN, buff=0.18, aligned_edge=LEFT) for abc, opts, key, why in self.PRACTICE])
        rows.arrange(DOWN, buff=0.5, aligned_edge=LEFT)
        fit_within(rows, SAFE_W, SAFE_H - 1.2)
        rows.move_to(UP * 0.3)
        self.validator.check_in_frame(rows)

        n = self.narrate(
            id="answers_01",
            text="One: play. A scene is a section of a play; stage and theatre are places. Two: score: the written plan, "
                 "before the work is performed or built. Three: bird. One of many parts covering the whole; a wing is too "
                 "narrow a whole.",
            voice="default",
            subtitle=True,
        )
        for r, (spoken, why) in zip(rows, [("play", "section"), ("score", "plan"), ("bird", "parts")]):
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

        card, table = self.recap_card("Recap Card: Video 3", [
            ["Refine", "add level, function or direction until one option fits"],
            ["Level", "specific item vs general field"],
            ["Direction", "who does what to whom"],
        ])
        card.move_to(UP * 0.2)
        self.validator.check_in_frame(card)

        n = self.narrate(
            id="recap_01",
            text="To recap. Refine the bridge: add level, function or direction, until one option fits. Level: a specific "
                 "item, against a general field. Direction: who does what to whom.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(card[0]), FadeIn(table[0]))
        for row, (spoken, occ) in zip(table[1:], [("Refine", 1), ("Level", 2), ("Direction", 2)]):
            self.at_word(n, spoken, occurrence=occ)
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.45)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S15_recap")

    # ================================================= 16. NEXT ==========

    def next_video(self):
        self.scene_start("S16_next", title="Next")

        several = pill("words with several meanings: a special trap", BAD, size=LABEL)
        nxt = pill("Next:  Context-Based Analogies", FOCUS, size=LABEL)
        VGroup(several, nxt).arrange(DOWN, buff=0.8).move_to(UP * 0.2)
        self.no_overlap(several, nxt)
        self.validator.check_in_frame(VGroup(several, nxt))

        n = self.narrate(
            id="next_01",
            text="Words with several meanings create a special trap in analogies. Video four covers context.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "several")
        self.play(FadeIn(several, shift=DOWN * 0.1))
        self.at_word(n, "Video")
        self.play(FadeIn(nxt, scale=1.05))
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S16_next")

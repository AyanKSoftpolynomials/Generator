"""
animation.py for the LMS video generator.

Course : C-CAT - Section A - English
Module : Module 1 - Vocabulary
Lesson : Lesson 5 - Analogies
Video  : 01 - Introduction to Analogies (Video 1 of 7)

Source script:
  C:\\Users\\User\\Downloads\\C-CAT_SectionA_Module1_English\\English\\Module 1 - Vocabulary\\
  Lesson 5 - Analogies\\01 - Introduction to Analogies.pdf

Built on the golden-reference pattern:
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``;
  * layouts stacked with next_to and guarded with ``no_overlap``; nothing is
    ever animated onto or into another box.

First video of Lesson 5: the intro recaps Lessons 1-4 (meaning of words) and announces the new lesson.
bridge(a, link, b) builds the bridge sentence for a pair and analogy_line(a, b, c, d) draws A : B :: C : D; the worked examples and Hook, Solved build both bridges from the same link.
The "bridge method" card (bridge the first pair, carry it across, strike other links, same sentence) stays pinned top-right through the worked examples and Hook, Solved.
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

BLANK = "______"


def article(word):
    return "an" if word[0].lower() in "aeiou" else "a"


def bridge(a, link, b, articles=True):
    """The bridge sentence for a pair: 'A pilot operates an aircraft.'"""
    if articles:
        return f"{article(a).capitalize()} {a} {link} {article(b)} {b}."
    return f"{a.capitalize()} {link} {b}."


def analogy_line(a, b, c, d="?", size=BODY):
    """A : B :: C : D as chips.  [0], [2] = first pair;  [4], [6] = second pair."""
    return VGroup(pill(a, WORD, size=size), text(":", size, MUTED), pill(b, WORD, size=size), text("::", size, MUTED),
                  pill(c, SECOND, size=size), text(":", size, MUTED),
                  pill(d, FOCUS if d == "?" else GOOD, size=size)).arrange(RIGHT, buff=0.25)


assert bridge("pilot", "operates", "aircraft") == "A pilot operates an aircraft."
assert bridge("hunger", "is satisfied by", "food", articles=False) == "Hunger is satisfied by food."


class IntroductionToAnalogiesVideo(LMSScene):
    lesson_title = "Introduction to Analogies"

    def construct(self):
        self.camera.background_color = BG

        self.lesson_intro()
        self.hook()
        self.concept()
        self.why_you_need_it()
        self.analogy()
        self.example_bee()
        self.example_architect()
        self.example_thirst()
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

    def bridge_pin(self):
        return self.steps_pin("bridge method", [("bridge the FIRST pair", WORD),
                                                ("carry it to the second pair", STEP_COLS["PREDICT"]),
                                                ("strike other links", BAD), ("same sentence, new words", GOOD)])

    def screen_card(self):
        head = text("APTITUDE SCREEN  ·  recruiter", SMALL, RATIO, BOLD)
        line = analogy_line("PILOT", "AIRCRAFT", "CAPTAIN", size=LABEL)
        cx, w = self.free_area()
        body = VGroup(head, line).arrange(DOWN, buff=0.25, aligned_edge=LEFT)
        fit_width(body, min(w - 1.4, SAFE_W - 1.8))
        card = self.card(body, width=min(w - 0.2, SAFE_W - 0.4))
        return card.move_to(RIGHT * cx + UP * (CARD_TOP - card.height / 2))

    def bridge_example(self, a, b, c, d, link, articles=True):
        """Analogy line, the bridge for the first pair, the same bridge carried to the second pair."""
        cx, w = self.free_area()
        line = analogy_line(a, b, c)
        first = text("“" + bridge(a.lower(), link, b.lower(), articles) + "”", LABEL, INK, t2c={link: RATIO})
        second = text("“" + bridge(c.lower(), link, BLANK, articles) + "”", LABEL, INK, t2c={link: RATIO, BLANK: FOCUS})
        done = text("“" + bridge(c.lower(), link, d, articles) + "”", LABEL, INK, t2c={link: RATIO, d: GOOD})
        rows = VGroup(VGroup(pill("bridge", WORD, size=SMALL), first).arrange(RIGHT, buff=0.25),
                      VGroup(pill("carry", STEP_COLS["PREDICT"], size=SMALL), second).arrange(RIGHT, buff=0.25))\
            .arrange(DOWN, buff=0.4, aligned_edge=LEFT)
        block = VGroup(line, rows).arrange(DOWN, buff=0.8, aligned_edge=LEFT)
        fit_within(block, w - 0.6, SAFE_H - 1.8)
        self.place_free(block, y=0.2)
        done.scale(second.height / text("“" + bridge(c.lower(), link, BLANK, articles) + "”", LABEL, INK).height)
        done.move_to(second, aligned_edge=LEFT)
        answer = pill(d, GOOD, size=BODY).scale(line[6].height / pill("?", FOCUS, size=BODY).height).move_to(line[6],
                                                                                                         aligned_edge=LEFT)
        self.no_overlap(line, rows)
        self.validator.check_in_frame(VGroup(block, done, answer))
        return line, rows, second, done, answer

    # ========================================= 0. LESSON INTRO ==========
    # First video of a NEW LESSON: silent trail, a one-line recap of Lessons 1-4
    # (meaning of words), one line that Lesson 5 starts, the title and objectives.

    def lesson_intro(self):
        self.scene_start("S00_intro", title="Lesson Introduction")

        crumb = self.breadcrumb("English · Module 1 Vocabulary", "Lesson 5 · Analogies", "Video 1")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        before = pill("Lessons 1 to 4:  the MEANING of words", MUTED, size=LABEL)
        pair = VGroup(pill("word", WORD, size=BODY), text("—  the relationship  —", LABEL, RATIO),
                      pill("word", WORD, size=BODY)).arrange(RIGHT, buff=0.3)
        both = pill("the module closes here: you need both meaning AND connection", GOOD, size=SMALL)
        VGroup(before, pair, both).arrange(DOWN, buff=0.6).move_to(DOWN * 0.1)
        self.no_overlap(crumb, before, pair, both)
        self.validator.check_in_frame(VGroup(crumb, before, pair, both))

        n = self.narrate(
            id="intro_01",
            text="In lessons one to four, you worked on the meaning of words.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.at_word(n, "meaning")
        self.play(FadeIn(before, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="intro_02",
            text="Now we start lesson five, analogies. Analogies are about the relationship between words, which is why "
                 "they close the vocabulary module: you need both meaning and connection.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "lesson")
        self.play(Indicate(crumb[2], color="#F48FB1", scale_factor=1.1))
        self.at_word(n, "relationship")
        self.play(FadeIn(pair[0]), FadeIn(pair[2]), FadeIn(pair[1], scale=0.8))
        self.at_word(n, "both")
        self.play(FadeIn(both, shift=UP * 0.1))
        self.wait_for_narration(n)

        title = fitted_text("Introduction to Analogies", SAFE_W, 72, INK, BOLD)
        underline = Line(LEFT, RIGHT, color=RATIO, stroke_width=5).set_width(title.width * 0.6)
        VGroup(title, underline).arrange(DOWN, buff=0.2).move_to(UP * 0.2)
        goals = [
            ("Explain what an analogy question tests", WORD),
            ("Solve a basic analogy with a bridge sentence", GOOD),
        ]
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
            id="intro_03",
            text="This is the introduction to analogies. By the end of this video, you'll be able to explain what an "
                 "analogy question tests, and solve a basic analogy with a bridge sentence.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(VGroup(before, pair, both), shift=UP * 0.3))
        self.at_word(n, "introduction")
        self.play(Write(title), run_time=1.1)
        self.play(GrowFromCenter(underline))
        self.at_word(n, "By")
        self.play(FadeOut(underline), ReplacementTransform(title, small_title), run_time=0.8)
        self.play(FadeIn(objectives[0]), FadeIn(heading))
        for row_, spoken in zip(rows, ["explain", "solve"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row_, shift=RIGHT * 0.2), run_time=0.5)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_intro")

    # ================================================= 1. HOOK ==========

    HOOK = dict(word="CAPTAIN : ?", options=["army", "team", "sea", "ship"], key="d",
                traps={"a": "a rank there: a different link", "b": "leads people, not a vehicle",
                       "c": "where it goes, not what is steered"})

    def hook(self):
        self.scene_start("S01_hook", title="Hook")

        h = self.HOOK
        screen = self.screen_card()
        line = screen[1][1]
        q = OptionQuestion(h["word"], h["options"], h["key"], h["traps"])
        opts = q.rows.copy().arrange(RIGHT, buff=0.9)
        notes = VGroup(pill("three options have a real link to “captain”", MUTED, size=SMALL),
                       pill("only ONE has the SAME link as pilot → aircraft", GOOD, size=SMALL)).arrange(RIGHT, buff=0.4)
        fit_width(notes, SAFE_W)
        opts.next_to(screen, DOWN, buff=0.8)
        notes.next_to(opts, DOWN, buff=0.7)
        self.no_overlap(screen, opts, notes)
        self.validator.check_in_frame(VGroup(screen, opts, notes))

        n = self.narrate(
            id="hook_01",
            text="A recruiter's online aptitude screen shows: pilot is to aircraft, as captain is to what?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "screen")
        self.play(FadeIn(screen[0]), FadeIn(screen[1][0]))
        self.at_word(n, "pilot")
        self.play(FadeIn(line[:3], shift=RIGHT * 0.2))
        self.at_word(n, "captain")
        self.play(FadeIn(line[3:], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_02",
            text="Army, team, sea, or ship? Three options have a real link to captain. Only one has the same link that a "
                 "pilot has to an aircraft.",
            voice="default",
            subtitle=True,
            pause_after=3.0,
        )
        for row, spoken in zip(opts, ["Army", "team", "sea", "ship"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=UP * 0.15), run_time=0.35)
        self.at_word(n, "Three")
        self.play(FadeIn(notes[0], shift=UP * 0.1))
        self.at_word(n, "Only")
        self.play(FadeIn(notes[1], shift=UP * 0.1))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        self.clear_stage()
        self.scene_end("S01_hook")

    # ============================================== 2. CONCEPT ==========

    def concept(self):
        self.scene_start("S02_concept", title="The Concept")

        head = pill("analogy:  two pairs of words sharing the SAME relationship", RATIO, size=LABEL)
        fit_width(head, SAFE_W)
        head.move_to(UP * (CARD_TOP - head.height / 2))
        line = analogy_line("PILOT", "AIRCRAFT", "CAPTAIN")
        line.move_to(UP * 0.4)
        first_pair, second_pair = VGroup(line[0], line[1], line[2]), VGroup(line[4], line[5], line[6])
        links = VGroup(*[VGroup(Line(p.get_corner(UL) + UP * 0.2, p.get_corner(UR) + UP * 0.2, color=RATIO, stroke_width=4),
                                text(t, LABEL, RATIO, BOLD)).arrange(UP, buff=0.12)
                         for p, t in [(first_pair, "operates"), (second_pair, "operates")]])
        for link, p in zip(links, [first_pair, second_pair]):
            link.next_to(p, UP, buff=0.2)
        about = text("not about pilots or aircraft: about the LINK between them", LABEL, MUTED)
        about.next_to(line, DOWN, buff=0.6)
        self.no_overlap(head, links, line, about)
        self.validator.check_in_frame(VGroup(head, links, line, about))

        n = self.narrate(
            id="concept_01",
            text="An analogy says that two pairs of words share the same relationship. Pilot, aircraft isn't about pilots "
                 "or aircraft; it's about the link between them. A pilot flies, or operates, an aircraft. The question "
                 "asks which word has that same link to captain.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "pairs")
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(line, shift=UP * 0.1))
        self.at_word(n, "link", occurrence=1)
        self.play(FadeIn(about, shift=UP * 0.1), Create(links[0][0]))
        self.at_word(n, "operates")
        self.play(FadeIn(links[0][1], shift=DOWN * 0.1))
        self.at_word(n, "question")
        self.play(FadeIn(links[1], shift=DOWN * 0.1), Indicate(line[6], color=FOCUS, scale_factor=1.2))
        self.wait_for_narration(n)

        # The bridge sentence.
        tool = pill("the tool:  a BRIDGE SENTENCE", WORD, size=BODY)
        tool.move_to(UP * (CARD_TOP - tool.height / 2))
        states = text("a short sentence that states the relationship, using the words themselves", SMALL, MUTED)
        states.next_to(tool, DOWN, buff=0.25)
        b1 = text("“" + bridge("pilot", "operates", "aircraft") + "”", BODY, INK, t2c={"operates": RATIO})
        b2 = text("“" + bridge("captain", "operates", BLANK) + "”", BODY, INK, t2c={"operates": RATIO, BLANK: FOCUS})
        b2f = text("“" + bridge("captain", "operates", "ship") + "”", BODY, INK, t2c={"operates": RATIO, "ship": GOOD})
        VGroup(b1, b2).arrange(DOWN, buff=0.6, aligned_edge=LEFT).next_to(states, DOWN, buff=0.7)
        b2f.move_to(b2, aligned_edge=LEFT)
        only = pill("only one option fits", GOOD, size=LABEL).next_to(b2, DOWN, buff=0.6)
        self.no_overlap(tool, states, b1, b2, only)
        self.validator.check_in_frame(VGroup(tool, states, b1, b2, b2f, only))
        n = self.narrate(
            id="concept_02",
            text="The tool that solves analogies is the bridge sentence: a short sentence that states the relationship in "
                 "the first pair, using the words themselves. A pilot operates an aircraft. Then you carry the bridge "
                 "across: a captain operates a, blank. Only one option fits.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(VGroup(head, links, line, about)))
        self.at_word(n, "bridge", occurrence=1)
        self.play(FadeIn(tool, scale=1.05))
        self.at_word(n, "states")
        self.play(FadeIn(states, shift=UP * 0.1))
        self.at_word(n, "pilot")
        self.play(FadeIn(b1, shift=RIGHT * 0.2))
        self.at_word(n, "carry")
        self.play(FadeIn(b2, shift=RIGHT * 0.2))
        self.at_word(n, "fits")
        self.play(ReplacementTransform(b2, b2f), FadeIn(only, shift=UP * 0.1))
        self.wait_for_narration(n)

        # The trap: related, but by a different link.
        trap = pill("the trap: options RELATED to the third word in some other way", BAD, size=LABEL)
        fit_width(trap, SAFE_W)
        trap.move_to(UP * (CARD_TOP - trap.height / 2))
        other = VGroup(*[VGroup(text("a captain", LABEL, MUTED), text(verb, LABEL, BAD), pill(w, MUTED, size=LABEL))
                         .arrange(RIGHT, buff=0.3) for verb, w in [("leads a", "team"), ("serves in an", "army"),
                                                                   ("sails on the", "sea")]])
        other.arrange(DOWN, buff=0.35, aligned_edge=LEFT)
        same = pill("“related” isn't enough: the relationship must be the SAME one", GOOD, size=LABEL)
        body = VGroup(other, same).arrange(DOWN, buff=0.6)
        fit_width(body, SAFE_W)
        body.next_to(trap, DOWN, buff=0.6)
        self.no_overlap(trap, other, same)
        self.validator.check_in_frame(VGroup(trap, body))
        n = self.narrate(
            id="concept_03",
            text="The trap is that most options will be related to the third word in some way. A captain leads a team, "
                 "serves in an army, and sails on the sea. But related isn't enough; the relationship has to be the same "
                 "one.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(VGroup(tool, states, b1, b2f, only)))
        self.at_word(n, "trap")
        self.play(FadeIn(trap, shift=DOWN * 0.2))
        for r, spoken in zip(other, ["team", "army", "sea"]):
            self.at_word(n, spoken)
            self.play(FadeIn(r, shift=RIGHT * 0.2), run_time=0.4)
        self.at_word(n, "enough")
        self.play(FadeIn(same, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_concept")

    # ======================================== 3. WHY YOU NEED IT ==========

    def why_you_need_it(self):
        self.scene_start("S03_why", title="Why You Need It")

        where = VGroup(*[pill(t, BAD, size=LABEL) for t in ["C-CAT verbal", "C-CAT reasoning", "placement tests"]])\
            .arrange(RIGHT, buff=0.4)
        habit = pill("the bridge-sentence habit: state the relationship precisely", WORD, size=LABEL)
        also = VGroup(pill("Sentence Arrangement", SECOND, size=LABEL), pill("Reading Comprehension", SECOND, size=LABEL))\
            .arrange(RIGHT, buff=0.4)
        group = VGroup(where, habit, also).arrange(DOWN, buff=0.7)
        fit_width(group, SAFE_W).move_to(UP * 0.3)
        self.no_overlap(where, habit, also)
        self.validator.check_in_frame(group)

        n = self.narrate(
            id="why_01",
            text="Verbal analogies appear in C-CAT's verbal and reasoning sections, and in most placement tests. The "
                 "bridge-sentence habit, stating the relationship precisely, also helps in sentence arrangement and "
                 "reading comprehension.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "appear")
        self.play(LaggedStart(*[FadeIn(w_, shift=UP * 0.1) for w_ in where], lag_ratio=0.3))
        self.at_word(n, "habit")
        self.play(FadeIn(habit, shift=UP * 0.1))
        self.at_word(n, "arrangement")
        self.play(FadeIn(also[0], shift=UP * 0.1))
        self.at_word(n, "comprehension")
        self.play(FadeIn(also[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_why")

    # ============================================== 4. ANALOGY ==========

    def analogy(self):
        self.scene_start("S04_analogy", title="The Analogy")

        def island_pair(a, b, color):
            pair = VGroup(pill(a, color, size=BODY), pill(b, color, size=BODY)).arrange(RIGHT, buff=2.6)
            return pair

        def span(pair, label, color, dashed=False):
            start, end = pair[0].get_corner(UR) + UP * 0.08, pair[1].get_corner(UL) + UP * 0.08
            arc = ArcBetweenPoints(start, end, angle=-PI / 2.5, color=color, stroke_width=5)
            if dashed:
                arc = DashedVMobject(arc, num_dashes=12)
            return VGroup(arc, text(label, SMALL, color).next_to(arc, UP, buff=0.08))

        first = island_pair("bird", "nest", WORD)
        second = island_pair("bee", "hive", SECOND)
        wrong = island_pair("bee", "flower", MUTED)
        VGroup(first, second, wrong).arrange(DOWN, buff=1.15, aligned_edge=LEFT).move_to(DOWN * 0.3)\
            .to_edge(LEFT, buff=SAFE + 0.3)
        spans = VGroup(span(first, "lives in", RATIO), span(second, "lives in", RATIO),
                       span(wrong, "lives in ✗", BAD, dashed=True))
        tags = VGroup(pill("build the bridge for the first pair", WORD, size=SMALL),
                      pill("copy the SAME design to the second pair", STEP_COLS["PREDICT"], size=SMALL),
                      pill("the copy doesn't reach?  wrong word", BAD, size=SMALL))
        # One tag column, starting right of the WIDEST pair, so every tag gets the same room.
        tag_left = max(p.get_right()[0] for p in (first, second, wrong)) + 0.6
        fit = FRAME_W / 2 - SAFE - tag_left
        for tag, pair in zip(tags, [first, second, wrong]):
            fit_width(tag, fit)
            tag.set_y(pair.get_y()).set_x(tag_left + tag.width / 2)
        self.no_overlap(VGroup(first, spans[0]), VGroup(second, spans[1]), VGroup(wrong, spans[2]))
        self.validator.check_in_frame(VGroup(first, second, wrong, spans, tags))

        n = self.narrate(
            id="analogy_01",
            text="A bridge sentence is literally a bridge. Build one between the first pair, then copy the same design to "
                 "cross between the second pair. If the copy doesn't reach, you've got the wrong word.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "literally")
        self.play(FadeIn(first, shift=UP * 0.1))
        self.at_word(n, "Build")
        self.play(Create(spans[0][0]), FadeIn(spans[0][1]), FadeIn(tags[0], shift=LEFT * 0.1))
        self.at_word(n, "copy", occurrence=1)
        self.play(FadeIn(second, shift=UP * 0.1), Create(spans[1][0]), FadeIn(spans[1][1]),
                  FadeIn(tags[1], shift=LEFT * 0.1))
        self.at_word(n, "reach")
        self.play(FadeIn(wrong, shift=UP * 0.1), FadeIn(spans[2]), FadeIn(tags[2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_analogy")

    # ======================================== 5-7. WORKED EXAMPLES ==========

    def example_bee(self):
        self.scene_start("S05_ex_bee", title="Worked Example 1")
        self.play(self.pin(self.bridge_pin()))

        line, rows, second, done, answer = self.bridge_example("Bird", "Nest", "Bee", "hive", "lives in")

        n = self.narrate(
            id="ex1_01",
            text="Bird is to nest, as bee is to what? Bridge: a bird lives in a nest. Carry it across: a bee lives in a, "
                 "blank. A bee lives in a hive.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Bird")
        self.play(FadeIn(line, shift=DOWN * 0.1))
        self.at_word(n, "Bridge")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2), self.pin_step(0, color=WORD))
        self.at_word(n, "Carry")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2), self.pin_step(1, color=STEP_COLS["PREDICT"]))
        self.at_word(n, "hive")
        self.play(ReplacementTransform(second, done), ReplacementTransform(line[6], answer),
                  self.pin_step(3, color=GOOD))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_ex_bee")

    def example_architect(self):
        self.scene_start("S06_ex_architect", title="Worked Example 2")

        line, rows, second, done, answer = self.bridge_example("Author", "Book", "Architect", "building", "creates")

        n = self.narrate(
            id="ex2_01",
            text="Author is to book, as architect is to what? Bridge: an author creates a book. Carry it across: an "
                 "architect creates a, blank. An architect creates a building: the design.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Author")
        self.play(FadeIn(line, shift=DOWN * 0.1))
        self.at_word(n, "Bridge")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2), self.pin_step(0, color=WORD))
        self.at_word(n, "Carry")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2), self.pin_step(1, color=STEP_COLS["PREDICT"]))
        self.at_word(n, "building")
        self.play(ReplacementTransform(second, done), ReplacementTransform(line[6], answer),
                  self.pin_step(3, color=GOOD))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_ex_architect")

    def example_thirst(self):
        self.scene_start("S07_ex_thirst", title="Worked Example 3")

        line, rows, second, done, answer = self.bridge_example("Hunger", "Food", "Thirst", "water", "is satisfied by",
                                                               articles=False)

        n = self.narrate(
            id="ex3_01",
            text="Hunger is to food, as thirst is to what? Bridge: hunger is satisfied by food. Carry it across: thirst is "
                 "satisfied by, blank. Thirst is satisfied by water.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Hunger", occurrence=1)
        self.play(FadeIn(line, shift=DOWN * 0.1))
        self.at_word(n, "Bridge")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2), self.pin_step(0, color=WORD))
        self.at_word(n, "Carry")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2), self.pin_step(1, color=STEP_COLS["PREDICT"]))
        self.at_word(n, "water")
        self.play(ReplacementTransform(second, done), ReplacementTransform(line[6], answer),
                  self.pin_step(3, color=GOOD))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S07_ex_thirst")

    # ================================================ 8. RULES ==========

    def rules(self):
        self.scene_start("S08_rules", title="Rules")
        self.play(self.unpin())

        rules = VGroup(*[VGroup(pill(str(i + 1), c, size=SMALL), fitted_text(s_, SAFE_W - 2.2, BODY, INK))
                         .arrange(RIGHT, buff=0.3) for i, (s_, c) in enumerate([
                             ("Focus on the RELATIONSHIP, not the words", RATIO),
                             ("Write a bridge sentence using the first pair", WORD),
                             ("Apply the same bridge to the second pair", STEP_COLS["PREDICT"]),
                             ("Being related isn't enough: the relationship must MATCH", GOOD)])])
        rules.arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        board = self.card(rules).move_to(UP * 0.3)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="rules_01",
            text="Four rules. First, focus on the relationship, not the words. Second, write a bridge sentence using the "
                 "first pair. Third, apply the same bridge to the second pair. And fourth, being related isn't enough: the "
                 "relationship must match.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(board[0]))
        for r, (spoken, occ) in zip(rules, [("First", 1), ("Second", 1), ("Third", 1), ("fourth", 1)]):
            self.at_word(n, spoken, occurrence=occ)
            self.play(FadeIn(r, shift=RIGHT * 0.2), run_time=0.45)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S08_rules")

    # ============================================== 9. PROCESS ==========

    def process(self):
        self.scene_start("S09_process", title="The Process")

        strip = process_strip(BODY)
        fit_width(strip, SAFE_W)
        strip.move_to(UP * (CARD_TOP - strip.height / 2))
        details = VGroup(*[VGroup(pill(name, col, size=SMALL), fitted_text(s_, SAFE_W - 3.4, LABEL, INK))
                           .arrange(RIGHT, buff=0.3) for (name, col), s_ in zip(STEP_COLS.items(), [
                               "A : B :: C : ?",
                               "make a bridge for A and B, then fill C's version",
                               "options related to C by a DIFFERENT link",
                               "both bridges: the same sentence, different words"])])
        details.arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        board = self.card(details)
        board.next_to(strip, DOWN, buff=0.5)
        self.no_overlap(strip, board)
        self.validator.check_in_frame(VGroup(strip, board))

        n = self.narrate(
            id="process_01",
            text="The process. Read: A is to B, as C is to what? Predict: make a bridge for A and B, then fill C's version. "
                 "Eliminate: remove options related to C by a different link. And confirm: read both bridges; they should "
                 "be the same sentence, with different words.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(strip, shift=DOWN * 0.2), FadeIn(board[0]))
        for d, name, spoken in zip(details, STEP_COLS, ["Read", "Predict", "Eliminate", "confirm"]):
            self.at_word(n, spoken, occurrence=1)
            self.play(Indicate(step_chip(strip, name)), FadeIn(d, shift=RIGHT * 0.2), run_time=0.5)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S09_process")

    # ========================================== 10. HOOK, SOLVED ==========

    def hook_solved(self):
        self.scene_start("S10_hook_solved", title="Hook, Solved")
        self.play(self.pin(self.bridge_pin()))

        h = self.HOOK
        cx, w = self.free_area()
        screen = self.screen_card()
        link = "operates and steers"
        b1 = text("“" + bridge("pilot", link, "aircraft") + "”", LABEL, INK, t2c={link: RATIO})
        b2 = text("“" + bridge("captain", link, BLANK) + "”", LABEL, INK, t2c={link: RATIO, BLANK: FOCUS})
        bridges = VGroup(b1, b2).arrange(DOWN, buff=0.2, aligned_edge=LEFT)
        fit_width(bridges, w - 0.8)
        bridges.next_to(screen, DOWN, buff=0.3).to_edge(LEFT, buff=SAFE + 0.6)
        b2f = text("“" + bridge("captain", "steers", "ship") + "”", LABEL, INK, t2c={"steers": RATIO, "ship": GOOD})
        b2f.scale(b2.height / text("“" + bridge("captain", link, BLANK) + "”", LABEL, INK).height)
        b2f.move_to(b2, aligned_edge=LEFT)
        q = OptionQuestion(h["word"], h["options"], h["key"], h["traps"], word_size=LABEL)
        fit_height(q.group, bridges.get_bottom()[1] - 0.3 - (BOTTOM_Y + 0.6))
        q.group.next_to(bridges, DOWN, buff=0.3).to_edge(LEFT, buff=SAFE + 0.6)
        self.no_overlap(screen, bridges, q.group)
        self.no_overlap(screen, self.pinned)
        self.no_overlap(bridges, self.pinned)
        self.validator.check_in_frame(VGroup(screen, bridges, q.group))

        n = self.narrate(
            id="solved_01",
            text="Let's solve the hook. Read: pilot is to aircraft. Predict: a pilot operates and steers an aircraft. So a "
                 "captain operates and steers a, blank.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(screen), FadeIn(q.word), FadeIn(q.rows))
        self.at_word(n, "Read")
        self.play(Indicate(screen[1][1][:3], color=WORD, scale_factor=1.05))
        self.at_word(n, "Predict")
        self.play(FadeIn(b1, shift=RIGHT * 0.2), self.pin_step(0, color=WORD))
        self.at_word(n, "captain")
        self.play(FadeIn(b2, shift=RIGHT * 0.2), self.pin_step(1, color=STEP_COLS["PREDICT"]))
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_02",
            text="Eliminate. Army: a captain is a rank there: a different link. Team: a captain leads people, not a "
                 "vehicle. Sea: that's where the ship goes, not what is steered.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Eliminate")
        self.play(self.pin_step(2, color=BAD))
        for letter, spoken in [("a", "Army"), ("b", "Team"), ("c", "Sea")]:
            self.at_word(n, spoken)
            self.play(*q.strike(letter)[1])
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_03",
            text="Confirm: a captain steers a ship. That's the answer.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Confirm")
        self.play(ReplacementTransform(b2, b2f), self.pin_step(3, color=GOOD))
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
            ["A : B :: C : ?", "bridge from A–B; apply to C"],
            ["Choose the pair  (A : B :: ? : ?)", "bridge from A–B; test each pair"],
            ["Odd pair out", "bridge each pair; the one that doesn't match is odd"],
        ], [5.2, 6.6], size=LABEL)
        board = self.card(table, width=SAFE_W - 0.2).move_to(UP * 0.4)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="patterns_01",
            text="Three exam patterns. A is to B, as C is to what: bridge from A and B, and apply it to C. Choose the pair: "
                 "bridge from A and B, and test each pair. And odd pair out: bridge each pair; the one that doesn't match "
                 "is odd.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "patterns")
        self.play(FadeIn(board[0]), FadeIn(table[0]))
        for row, spoken in zip(table[1:], ["apply", "Choose", "odd"]):
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
            (self.verdict_card(False, "A word related to C in a different way", card_w),
             self.verdict_card(True, "The SAME link as A–B", card_w)),
            (self.verdict_card(False, "A vague bridge: “is connected to”", card_w),
             self.verdict_card(True, "A precise verb: operates, lives in", card_w)),
            (self.verdict_card(False, "Ignoring the order of the pair", card_w),
             self.verdict_card(True, "Keep A → B, then C → D", card_w)),
        ]
        for (wrong, right), yy in zip(pairs, [1.6, 0.05, -1.5]):
            wrong.move_to(LEFT_ZONE + UP * yy)
            right.move_to(RIGHT_ZONE + UP * yy)
        header = pill("3 mistakes", BAD, size=LABEL).move_to(UP * (CARD_TOP - 0.3))
        self.validator.check_in_frame(VGroup(header, *[c for p in pairs for c in p]))

        n = self.narrate(
            id="mistakes_01",
            text="Three common mistakes. The first is choosing a word related to C in a different way. The second is using "
                 "a vague bridge, like: is connected to. The third is ignoring the order of the pair.",
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
        (("Doctor", "Hospital", "Teacher"), ["school", "student", "book", "class"], "a",
         "works in;  (b) a student is who they teach"),
        (("Eye", "See", "Ear"), ["sound", "hear", "music", "noise"], "b",
         "organ → function (a verb);  (a) sound is a noun"),
        (("Cow", "Calf", "Dog"), ["kitten", "cub", "puppy", "foal"], "c", "animal → its young"),
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
            text="Your turn. One: doctor is to hospital, as teacher is to what? School, student, book, or class? Two: eye "
                 "is to see, as ear is to what? Sound, hear, music, or noise? Three: cow is to calf, as dog is to what? "
                 "Kitten, cub, puppy, or foal?",
            voice="default",
            subtitle=True,
            pause_after=10.0,
        )
        self.play(FadeIn(board[0]))
        for ln, (spoken, first_option) in zip(lines, [("doctor", "School"), ("eye", "Sound"), ("cow", "Kitten")]):
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
            text="One: school. A teacher works in a school; a student is who they teach. Two: hear. An organ and its "
                 "function, a verb; sound is a noun. Three: puppy. An animal and its young.",
            voice="default",
            subtitle=True,
        )
        for r, (spoken, why) in zip(rows, [("school", "works"), ("hear", "organ"), ("puppy", "young")]):
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

        card, table = self.recap_card("Recap Card: Video 1", [
            ["Analogy", "two pairs sharing the same relationship"],
            ["Tool", "a bridge sentence from the first pair"],
            ["Trap", "related, but by a different link"],
        ])
        card.move_to(UP * 0.2)
        self.validator.check_in_frame(card)

        n = self.narrate(
            id="recap_01",
            text="To recap. An analogy is two pairs sharing the same relationship. The tool is a bridge sentence from the "
                 "first pair. And the trap is a word that's related, but by a different link.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(card[0]), FadeIn(table[0]))
        for row, spoken in zip(table[1:], ["pairs", "tool", "trap"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.45)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S15_recap")

    # ================================================= 16. NEXT ==========

    def next_video(self):
        self.scene_start("S16_next", title="Next")

        types = pill("the common relationship TYPES, named", RATIO, size=LABEL)
        quick = pill("so your bridges are quick and precise", GOOD, size=LABEL)
        nxt = pill("Next:  Types of Relationships", FOCUS, size=LABEL)
        VGroup(types, quick, nxt).arrange(DOWN, buff=0.7).move_to(UP * 0.2)
        self.no_overlap(types, quick, nxt)
        self.validator.check_in_frame(VGroup(types, quick, nxt))

        n = self.narrate(
            id="next_01",
            text="Video two names the common relationship types, so your bridges are quick and precise.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Video")
        self.play(FadeIn(nxt, scale=1.05))
        self.at_word(n, "types")
        self.play(FadeIn(types, shift=UP * 0.1))
        self.at_word(n, "quick")
        self.play(FadeIn(quick, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S16_next")

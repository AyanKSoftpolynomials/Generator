"""
animation.py for the LMS video generator.

Course : C-CAT - Section A - English
Module : Module 1 - Vocabulary
Lesson : Lesson 3 - Idioms & Phrases
Video  : 05 - Commonly Confused Idioms (Video 5 of 7)

Source script:
  C:\\Users\\User\\Downloads\\C-CAT_SectionA_Module1_English\\English\\Module 1 - Vocabulary\\
  Lesson 3 - Idioms & Phrases\\05 - Commonly Confused Idioms.pdf

Built on the golden-reference pattern:
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``;
  * layouts stacked with next_to and guarded with ``no_overlap``; nothing is
    ever animated onto or into another box.

The sister idioms (SISTERS), fixed forms (FIXED_FORMS, WRONG_FORMS) and the four hook lines (HOOK_LINES, with the idiom's meaning, the context and whether they agree) are data; the rules table and Hook, Solved are built from them.
The "clash test" card (idiom's exact meaning, rest of the sentence, do they clash, fixed form) stays pinned top-right through the worked examples and Hook, Solved.
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

# (idiom, meaning, often confused with, that idiom's meaning): the script's Rules table.
SISTERS = [
    ("give up", "stop trying", "give in", "yield to pressure"),
    ("at the eleventh hour", "at the last moment", "in the nick of time", "just in time, successfully"),
    ("a close shave", "a narrow escape", "a clean sweep", "a complete win"),
    ("turn a blind eye", "ignore deliberately", "see eye to eye", "agree"),
    ("call it a day", "stop working for now", "call the shots", "be in control"),
]
FIXED_FORMS = ["make ends meet", "by and large", "take for granted", "in the long run"]
WRONG_FORMS = [("make ends meet", "make both ends meet"), ("by and large", "by and big"),
               ("take it for granted", "take it as granted")]

# Hook: (sentence, idiom as written, its meaning, what the rest of the sentence says, used correctly?)
HOOK_LINES = [
    ("After the rejection email, Neha was on cloud nine.", "on cloud nine", "very happy", "a rejection", False),
    ("Arjun broke the ice with a joke at the start of the meeting.", "broke the ice", "got people talking",
     "a joke at the start of a meeting", True),
    ("The migration was a piece of cake; it took six months of struggle.", "a piece of cake", "very easy",
     "six months of struggle", False),
    ("We saw eye to eye, so we argued all afternoon.", "saw eye to eye", "agreed", "arguing", False),
]


class CommonlyConfusedIdiomsVideo(LMSScene):
    lesson_title = "Commonly Confused Idioms"

    def construct(self):
        self.camera.background_color = BG

        self.lesson_intro()
        self.hook()
        self.concept()
        self.why_you_need_it()
        self.analogy()
        self.example_moon()
        self.example_gave_in()
        self.example_shave()
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

    def clash_pin(self):
        return self.steps_pin("clash test", [("the idiom's exact meaning", WORD), ("the rest of the sentence", RATIO),
                                             ("do they CLASH?", BAD), ("fixed form, word by word", SECOND)])

    def usage_rows(self, lines, width, size=LABEL):
        """(a)-(d) sentences, each with its clash-test verdict underneath."""
        rows = VGroup()
        for letter, (sent, idiom, meaning, context, ok) in zip("abcd", lines):
            line = VGroup(text(f"({letter})", size, MUTED),
                          fitted_text(sent, width - 1.0, size, INK, NORMAL, max_lines=2, t2c={idiom: WORD}))\
                .arrange(RIGHT, buff=0.25, aligned_edge=UP)
            why = text(f"{idiom} = {meaning}:  " + ("agrees with " if ok else "clashes with ") + context, SMALL,
                       GOOD if ok else BAD)
            fit_width(why, width - 1.0)
            rows.add(VGroup(line, why).arrange(DOWN, buff=0.1, aligned_edge=LEFT))
        return rows.arrange(DOWN, buff=0.3, aligned_edge=LEFT)

    def usage_example(self, sentence, idiom, meaning, context, ok, fix=None):
        """One usage check beside the pinned clash test: sentence, idiom meaning, context, verdict."""
        cx, w = self.free_area()
        sent = fitted_text(f"“{sentence}”", w - 0.8, BODY, INK, NORMAL, max_lines=2, t2c={idiom: WORD})
        m = VGroup(pill("idiom", WORD, size=SMALL), text(f"{idiom} = {meaning}", LABEL, INK)).arrange(RIGHT, buff=0.25)
        c = VGroup(pill("sentence", RATIO, size=SMALL), text(context, LABEL, INK)).arrange(RIGHT, buff=0.25)
        verdict = pill("no clash:  CORRECT  ✓" if ok else "clash:  WRONG  ✗", GOOD if ok else BAD, size=BODY)
        parts = [sent, m, c, verdict] + ([text("needed:  " + fix, LABEL, GOOD)] if fix else [])
        block = VGroup(*parts).arrange(DOWN, buff=0.45, aligned_edge=LEFT)
        fit_height(block, SAFE_H - 1.6)
        self.place_free(block, y=0.1)
        self.no_overlap(*parts)
        self.validator.check_in_frame(block)
        return parts

    # ========================================= 0. LESSON INTRO ==========

    def lesson_intro(self):
        self.scene_start("S00_intro", title="Lesson Introduction")

        crumb = self.breadcrumb("English · Module 1 Vocabulary", "Lesson 3 · Idioms & Phrases", "Video 5")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        before = VGroup(text("Video 3", SMALL, MUTED), pill("situation", RATIO, size=LABEL), text("→", LABEL, MUTED),
                        pill("choose the idiom", WORD, size=LABEL)).arrange(RIGHT, buff=0.3)
        today = VGroup(text("Today", SMALL, FOCUS), pill("an idiom, already in a sentence", WORD, size=LABEL),
                       text("→", LABEL, MUTED), pill("does it FIT?", GOOD, size=LABEL)).arrange(RIGHT, buff=0.3)
        tested = pill("how usage and error questions test idioms", BAD, size=SMALL)
        VGroup(before, today, tested).arrange(DOWN, buff=0.6).move_to(DOWN * 0.1)
        self.no_overlap(crumb, before, today, tested)
        self.validator.check_in_frame(VGroup(crumb, before, today, tested))

        n = self.narrate(
            id="intro_01",
            text="In video three, you chose the idiom for a situation. Today you check whether a given idiom fits the "
                 "situation it's placed in, which is how usage and error questions test idioms.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.at_word(n, "chose")
        self.play(FadeIn(before, shift=UP * 0.1))
        self.at_word(n, "check")
        self.play(FadeIn(today, shift=UP * 0.1))
        self.at_word(n, "usage")
        self.play(FadeIn(tested, shift=UP * 0.1))
        self.wait_for_narration(n)

        title = fitted_text("Commonly Confused Idioms", SAFE_W, 72, INK, BOLD)
        underline = Line(LEFT, RIGHT, color=BAD, stroke_width=5).set_width(title.width * 0.6)
        VGroup(title, underline).arrange(DOWN, buff=0.2).move_to(UP * 0.2)
        goals = [("Spot idioms used in the wrong situation", BAD),
                 ("Separate similar-looking idioms and fixed forms", GOOD)]
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
            text="This video is commonly confused idioms. By the end, you'll spot idioms used in the wrong situation, and "
                 "separate similar-looking idioms and fixed forms.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(VGroup(before, today, tested), shift=UP * 0.3))
        self.at_word(n, "commonly")
        self.play(Write(title), run_time=1.1)
        self.play(GrowFromCenter(underline))
        self.at_word(n, "By")
        self.play(FadeOut(underline), ReplacementTransform(title, small_title), run_time=0.8)
        self.play(FadeIn(objectives[0]), FadeIn(heading))
        for row_, spoken in zip(rows, ["spot", "separate"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row_, shift=RIGHT * 0.2), run_time=0.5)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_intro")

    # ================================================= 1. HOOK ==========

    def hook(self):
        self.scene_start("S01_hook", title="Hook")

        assert [ok for *_x, ok in HOOK_LINES].count(True) == 1
        head = VGroup(pill("TEAM NEWSLETTER  ·  draft", RATIO, size=LABEL),
                      pill("only ONE line uses its idiom correctly", BAD, size=LABEL)).arrange(RIGHT, buff=0.4)
        fit_width(head, SAFE_W)
        head.move_to(UP * (CARD_TOP - head.height / 2))
        lines = VGroup(*[r[0] for r in self.usage_rows(HOOK_LINES, SAFE_W - 0.6, size=BODY)])
        lines.arrange(DOWN, buff=0.35, aligned_edge=LEFT)
        ask = pill("which one can go out?", FOCUS, size=LABEL)
        body = VGroup(lines, ask).arrange(DOWN, buff=0.5)
        fit_within(body, SAFE_W, SAFE_H - head.height - 1.6)
        body.next_to(head, DOWN, buff=0.5)
        self.no_overlap(head, lines, ask)
        self.validator.check_in_frame(VGroup(head, body))

        n = self.narrate(
            id="hook_01",
            text="You're editing the team newsletter. Only one of these lines uses its idiom correctly. Which one can go "
                 "out?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "newsletter")
        self.play(FadeIn(head[0], shift=DOWN * 0.2))
        self.at_word(n, "one", occurrence=1)
        self.play(FadeIn(head[1], shift=LEFT * 0.1))
        self.at_word(n, "Which")
        self.play(FadeIn(ask, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_02",
            text="Line A: after the rejection email, Neha was on cloud nine. Line B: Arjun broke the ice with a joke at the "
                 "start of the meeting. Line C: the migration was a piece of cake; it took six months of struggle. Line "
                 "D: we saw eye to eye, so we argued all afternoon.",
            voice="default",
            subtitle=True,
            pause_after=3.0,
        )
        for line, spoken in zip(lines, ["rejection", "Arjun", "migration", "saw"]):
            self.at_word(n, spoken)
            self.play(FadeIn(line, shift=UP * 0.15), run_time=0.4)
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        self.clear_stage()
        self.scene_end("S01_hook")

    # ============================================== 2. CONCEPT ==========

    def concept(self):
        self.scene_start("S02_concept", title="The Concept")

        ways = VGroup(pill("1  wrong situation", BAD, size=LABEL), pill("2  similar idioms confused", RATIO, size=LABEL),
                      pill("3  wrong fixed form", SECOND, size=LABEL)).arrange(RIGHT, buff=0.4)
        fit_width(ways, SAFE_W)
        ways.move_to(UP * (CARD_TOP - ways.height / 2))

        def below(mob):
            fit_within(mob, SAFE_W, SAFE_H - ways.height - 1.6)
            mob.next_to(ways, DOWN, buff=0.6)
            self.no_overlap(ways, mob)
            self.validator.check_in_frame(VGroup(ways, mob))
            return mob

        # 1. Wrong situation.
        one = below(VGroup(
            text("the idiom's meaning clashes with the rest of the sentence", LABEL, INK),
            *[VGroup(pill(f"“{i}”", WORD, size=LABEL), text("=  " + m, LABEL, GOOD), text("✗  " + ctx, LABEL, BAD))
              .arrange(RIGHT, buff=0.35) for i, m, ctx in [("on cloud nine", "very happy", "after a rejection"),
                                                           ("a piece of cake", "very easy", "six months of struggle")]])
                    .arrange(DOWN, buff=0.45))
        n = self.narrate(
            id="concept_01",
            text="Idioms go wrong in three ways. First, the wrong situation: the idiom's meaning clashes with the rest of "
                 "the sentence. On cloud nine, very happy, after a rejection. A piece of cake, very easy, for six months "
                 "of struggle.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "three")
        self.play(LaggedStart(*[FadeIn(w, shift=DOWN * 0.2) for w in ways], lag_ratio=0.2))
        self.at_word(n, "clashes")
        self.play(Indicate(ways[0], color=BAD, scale_factor=1.05), FadeIn(one[0], shift=UP * 0.1))
        self.at_word(n, "cloud")
        self.play(FadeIn(one[1], shift=RIGHT * 0.2))
        self.at_word(n, "cake")
        self.play(FadeIn(one[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        # 2. Similar idioms confused.
        two = below(VGroup(*[VGroup(pill(a, WORD, size=LABEL), text(am, SMALL, INK), text("vs", LABEL, MUTED),
                                    pill(b, RATIO, size=LABEL), text(bm, SMALL, INK)).arrange(RIGHT, buff=0.25)
                             for a, am, b, bm in SISTERS[:3]]).arrange(DOWN, buff=0.45, aligned_edge=LEFT))
        n = self.narrate(
            id="concept_02",
            text="Second, similar idioms confused. Give up, stop trying, against give in, surrender to pressure. At the "
                 "eleventh hour, the last moment, against in the nick of time, just in time, successfully. A close shave, "
                 "a narrow escape, against a clean sweep, winning everything.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(one))
        self.at_word(n, "Second")
        self.play(Indicate(ways[1], color=RATIO, scale_factor=1.05))
        for r, spoken in zip(two, ["Give", "eleventh", "shave"]):
            self.at_word(n, spoken, occurrence=1)
            self.play(FadeIn(r, shift=RIGHT * 0.2), run_time=0.5)
        self.wait_for_narration(n)

        # 3. Wrong fixed form.
        three = below(VGroup(
            text("idioms don't allow word swaps", LABEL, INK),
            *[VGroup(pill(f"“{right}”  ✓", GOOD, size=LABEL), text(f"not “{wrong}”", LABEL, BAD)).arrange(RIGHT, buff=0.4)
              for right, wrong in WRONG_FORMS]).arrange(DOWN, buff=0.4))
        n = self.narrate(
            id="concept_03",
            text="Third, the wrong fixed form. Idioms don't allow word swaps. It's make ends meet, not make both ends "
                 "meet, in modern usage. By and large, not by and big. Take it for granted, not take it as granted.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(two))
        self.at_word(n, "Third")
        self.play(Indicate(ways[2], color=SECOND, scale_factor=1.05))
        self.at_word(n, "swaps")
        self.play(FadeIn(three[0], shift=UP * 0.1))
        for r, spoken in zip(three[1:], ["make", "large", "granted"]):
            self.at_word(n, spoken, occurrence=1)
            self.play(FadeIn(r, shift=RIGHT * 0.2), run_time=0.5)
        self.wait_for_narration(n)

        check = below(pill("one check for all three:  does the idiom's meaning AGREE with the rest of the sentence?",
                           FOCUS, size=LABEL))
        n = self.narrate(
            id="concept_04",
            text="In each case, the check is the same: does the idiom's meaning agree with everything else in the "
                 "sentence?",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(three))
        self.at_word(n, "check")
        self.play(FadeIn(check, scale=1.05))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_concept")

    # ======================================== 3. WHY YOU NEED IT ==========

    def why_you_need_it(self):
        self.scene_start("S03_why", title="Why You Need It")

        question = pill("“Which sentence uses the idiom correctly?”", WORD, size=BODY)
        standard = text("a standard exam question", LABEL, BAD)
        email = pill("a misused idiom in a client email reads as careless", RATIO, size=LABEL)
        opposite = text("the opposite of what an idiom is meant to do", LABEL, MUTED)
        group = VGroup(VGroup(question, standard).arrange(DOWN, buff=0.2), VGroup(email, opposite).arrange(DOWN, buff=0.2))\
            .arrange(DOWN, buff=0.9)
        fit_width(group, SAFE_W).move_to(UP * 0.3)
        self.validator.check_in_frame(group)

        n = self.narrate(
            id="why_01",
            text="Which sentence uses the idiom correctly? That's a standard exam question. And a misused idiom in a client "
                 "email reads as careless: the opposite of what an idiom is meant to do.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Which")
        self.play(FadeIn(question, shift=DOWN * 0.1))
        self.at_word(n, "standard")
        self.play(FadeIn(standard, shift=UP * 0.1))
        self.at_word(n, "email")
        self.play(FadeIn(email, shift=UP * 0.1))
        self.at_word(n, "opposite")
        self.play(FadeIn(opposite, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_why")

    # ============================================== 4. ANALOGY ==========

    def analogy(self):
        self.scene_start("S04_analogy", title="The Analogy")

        side = 1.3
        left = Square(side_length=side, color=WORD, fill_color=WORD, fill_opacity=0.3).move_to(LEFT * (side + 0.1))
        right = Square(side_length=side, color=WORD, fill_color=WORD, fill_opacity=0.3).move_to(RIGHT * (side + 0.1))
        gap = text("?", TITLE, MUTED)
        row = VGroup(left, gap, right).move_to(LEFT * 3.2 + DOWN * 0.9)
        piece = Circle(radius=side / 2, color=WORD, fill_color=WORD, fill_opacity=0.3)
        piece.move_to(gap.get_center() + UP * (side + 1.0))
        tries = Arrow(piece.get_bottom(), gap.get_top() + UP * 0.1, buff=0.1, color=BAD, stroke_width=5)
        cross = text("✗", BODY, BAD).next_to(tries, RIGHT, buff=0.15)
        tags = VGroup(pill("right COLOUR:  it sounds natural", GOOD, size=LABEL),
                      pill("wrong SHAPE:  it doesn't fit", BAD, size=LABEL),
                      pill("piece = the idiom  ·  neighbours = the sentence", FOCUS, size=SMALL))\
            .arrange(DOWN, buff=0.5, aligned_edge=LEFT)
        fit_width(tags, 6.0)
        tags.move_to(RIGHT * 3.2 + UP * 0.2)
        picture = VGroup(row, piece, tries, cross)
        self.no_overlap(picture, tags)
        self.no_overlap(piece, row)
        self.validator.check_in_frame(VGroup(picture, tags))

        n = self.narrate(
            id="analogy_01",
            text="A misused idiom is a jigsaw piece of the right colour and the wrong shape. It looks like it belongs, "
                 "until you try to fit it with its neighbours.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "jigsaw")
        self.play(FadeIn(left), FadeIn(right), FadeIn(gap), FadeIn(piece, shift=DOWN * 0.2))
        self.at_word(n, "colour")
        self.play(FadeIn(tags[0], shift=LEFT * 0.1))
        self.at_word(n, "shape")
        self.play(FadeIn(tags[1], shift=LEFT * 0.1))
        self.at_word(n, "belongs")
        self.play(Indicate(piece, color=GOOD, scale_factor=1.1))
        self.at_word(n, "fit")
        self.play(GrowArrow(tries), FadeIn(cross), FadeIn(tags[2], shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_analogy")

    # ======================================== 5-7. WORKED EXAMPLES ==========

    def example_moon(self):
        self.scene_start("S05_ex_moon", title="Worked Example 1")
        self.play(self.pin(self.clash_pin()))

        sent, m, c, verdict = self.usage_example("She was over the moon when she failed the exam.", "over the moon",
                                                 "delighted", "she failed the exam", ok=False)

        n = self.narrate(
            id="ex1_01",
            text="She was over the moon when she failed the exam. Over the moon means delighted. But she failed the exam. "
                 "Delight clashes with failure: wrong.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "moon", occurrence=1)
        self.play(FadeIn(sent, shift=DOWN * 0.1))
        self.at_word(n, "delighted")
        self.play(FadeIn(m, shift=RIGHT * 0.1), self.pin_step(0, color=WORD))
        self.at_word(n, "failed", occurrence=2)
        self.play(FadeIn(c, shift=RIGHT * 0.1), self.pin_step(1, color=RATIO))
        self.at_word(n, "clashes")
        self.play(FadeIn(verdict, scale=1.1), self.pin_step(2, color=BAD))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_ex_moon")

    def example_gave_in(self):
        self.scene_start("S06_ex_gave_in", title="Worked Example 2")

        assert SISTERS[0][:3] == ("give up", "stop trying", "give in")
        sent, m, c, verdict, fix = self.usage_example("The team gave in and kept trying until midnight.", "gave in",
                                                      "surrendered", "they kept trying", ok=False,
                                                      fix="“didn't give up”")

        n = self.narrate(
            id="ex2_01",
            text="The team gave in, and kept trying until midnight. Gave in means surrendered. But they kept trying. That's "
                 "a clash. The meaning needed is: didn't give up.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "team")
        self.play(FadeIn(sent, shift=DOWN * 0.1))
        self.at_word(n, "surrendered")
        self.play(FadeIn(m, shift=RIGHT * 0.1), self.pin_step(0, color=WORD))
        self.at_word(n, "kept", occurrence=2)
        self.play(FadeIn(c, shift=RIGHT * 0.1), self.pin_step(1, color=RATIO))
        self.at_word(n, "clash")
        self.play(FadeIn(verdict, scale=1.1), self.pin_step(2, color=BAD))
        self.at_word(n, "needed")
        self.play(FadeIn(fix, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_ex_gave_in")

    def example_shave(self):
        self.scene_start("S07_ex_shave", title="Worked Example 3")

        assert SISTERS[2][:2] == ("a close shave", "a narrow escape")
        sent, m, c, verdict = self.usage_example("It was a close shave; the car missed us by inches.", "a close shave",
                                                 "a narrow escape", "the car missed us by inches", ok=True)

        n = self.narrate(
            id="ex3_01",
            text="It was a close shave; the car missed us by inches. A close shave means a narrow escape. The car missed by "
                 "inches. No clash: correct.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "shave", occurrence=1)
        self.play(FadeIn(sent, shift=DOWN * 0.1))
        self.at_word(n, "escape")
        self.play(FadeIn(m, shift=RIGHT * 0.1), self.pin_step(0, color=WORD))
        self.at_word(n, "inches", occurrence=2)
        self.play(FadeIn(c, shift=RIGHT * 0.1), self.pin_step(1, color=RATIO))
        self.at_word(n, "clash")
        self.play(FadeIn(verdict, scale=1.1), self.pin_step(2, color=GOOD))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S07_ex_shave")

    # ================================================ 8. RULES ==========

    def rules(self):
        self.scene_start("S08_rules", title="Rules")
        self.play(self.unpin())

        table = self.table_rows(["Idiom", "Meaning", "Often confused with"],
                                [[a, am, f"{b} ({bm})"] for a, am, b, bm in SISTERS], [3.4, 3.4, 5.0], size=LABEL)
        for row in table[1:]:
            row[0].set_color(WORD)
            row[2].set_color(RATIO)
        board = self.card(table, width=SAFE_W - 0.2)
        forms = VGroup(text("fixed forms:", SMALL, MUTED, BOLD), *[pill(f, SECOND, size=SMALL) for f in FIXED_FORMS])\
            .arrange(RIGHT, buff=0.25)
        block = VGroup(board, forms).arrange(DOWN, buff=0.35)
        fit_within(block, SAFE_W, SAFE_H - 1.0)
        block.move_to(UP * 0.3)
        self.no_overlap(board, forms)
        self.validator.check_in_frame(block)

        n = self.narrate(
            id="rules_01",
            text="Five pairs to keep apart. Give up, stop trying; not give in, yield to pressure. At the eleventh hour, at "
                 "the last moment; not in the nick of time, just in time and successfully. A close shave, a narrow "
                 "escape; not a clean sweep, a complete win. Turn a blind eye, ignore deliberately; not see eye to eye, "
                 "agree. Call it a day, stop working for now; not call the shots, be in control.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Five")
        self.play(FadeIn(board[0]), FadeIn(table[0]))
        for row, spoken in zip(table[1:], ["Give", "eleventh", "shave", "blind", "day"]):
            self.at_word(n, spoken, occurrence=1)
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.45)
        self.wait_for_narration(n)

        n = self.narrate(
            id="rules_02",
            text="And four fixed forms: make ends meet, by and large, take for granted, in the long run.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "fixed")
        self.play(LaggedStart(*[FadeIn(f, shift=UP * 0.1) for f in forms], lag_ratio=0.3), run_time=2.0)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S08_rules")

    # ============================================== 9. PROCESS ==========

    def process(self):
        self.scene_start("S09_process", title="The Process")

        steps = VGroup(*[VGroup(pill(str(i + 1), c, size=SMALL), fitted_text(s_, SAFE_W - 2.2, BODY, INK))
                         .arrange(RIGHT, buff=0.3) for i, (s_, c) in enumerate([
                             ("Recall the exact meaning of the idiom", WORD),
                             ("Read the rest of the sentence: situation, result, tone", RATIO),
                             ("Check for a clash between the idiom and its context", BAD),
                             ("Check the fixed form, word by word", SECOND)])])
        steps.arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        board = self.card(steps).move_to(UP * 0.3)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="process_01",
            text="The process. First, recall the exact meaning of the idiom. Second, read the rest of the sentence: "
                 "situation, result, tone. Third, check for a clash between the idiom and its context. And fourth, check "
                 "the fixed form, word by word.",
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
        self.play(self.pin(self.clash_pin()))

        cx, w = self.free_area()
        head = VGroup(pill("usage check: four sentences", WORD, size=SMALL),
                      pill("find the idiom that AGREES with its context", STEP_COLS["PREDICT"], size=SMALL))\
            .arrange(RIGHT, buff=0.3)
        rows = self.usage_rows(HOOK_LINES, w - 0.4)
        block = VGroup(head, rows).arrange(DOWN, buff=0.4, aligned_edge=LEFT)
        fit_height(block, SAFE_H - 1.4)
        self.place_free(block, y=0.2)
        box = SurroundingRectangle(rows[1][0], color=GOOD, buff=0.1, corner_radius=0.1)
        self.no_overlap(head, rows)
        self.validator.check_in_frame(block)

        n = self.narrate(
            id="solved_01",
            text="Let's solve the hook. Read: a usage check on four sentences. Predict: look for the one where the idiom "
                 "agrees with its context.",
            voice="default",
            subtitle=True,
        )
        self.play(LaggedStart(*[FadeIn(r[0], shift=UP * 0.1) for r in rows], lag_ratio=0.15))
        self.at_word(n, "Read")
        self.play(FadeIn(head[0], shift=DOWN * 0.1), self.pin_step(1, color=RATIO))
        self.at_word(n, "Predict")
        self.play(FadeIn(head[1], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_02",
            text="Eliminate. Line A: on cloud nine means very happy, which clashes with a rejection. Line C: a piece of "
                 "cake means easy, which clashes with struggle. Line D: seeing eye to eye means agreeing, which clashes "
                 "with arguing.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Eliminate")
        self.play(self.pin_step(2, color=BAD))
        for i, spoken in zip([0, 2, 3], ["cloud", "cake", "seeing"]):
            self.at_word(n, spoken)
            self.play(FadeIn(rows[i][1], shift=UP * 0.05), rows[i][0].animate.set_opacity(0.45), run_time=0.6)
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_03",
            text="Confirm: line B. A joke at the start of a meeting is exactly how people break the ice.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Confirm")
        self.play(Create(box))
        self.at_word(n, "joke")
        self.play(FadeIn(rows[1][1], shift=UP * 0.05))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S10_hook_solved")

    # ========================================== 11. EXAM PATTERNS ==========

    def exam_patterns(self):
        self.scene_start("S11_patterns", title="Exam Patterns and Solving Models")
        self.play(self.unpin())

        table = self.table_rows(["Pattern", "Solving model"], [
            ["Which sentence uses the idiom correctly?", "meaning vs context: clash test on each option"],
            ["Error spotting with an idiom", "check the fixed form word by word"],
            ["Similar idioms in the options", "recall the exact difference (give up / give in)"],
        ], [5.4, 6.4], size=LABEL)
        board = self.card(table, width=SAFE_W - 0.2).move_to(UP * 0.4)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="patterns_01",
            text="Three exam patterns. Which sentence uses the idiom correctly: run the meaning-against-context clash test "
                 "on each option. Error spotting with an idiom: check the fixed form word by word. And similar idioms in "
                 "the options: recall the exact difference, like give up and give in.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(board[0]), FadeIn(table[0]))
        for row, spoken in zip(table[1:], ["Which", "Error", "similar"]):
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
            (self.verdict_card(False, "Judging by how natural it sounds", card_w),
             self.verdict_card(True, "Judge whether it FITS", card_w)),
            (self.verdict_card(False, "Confusing sister idioms", card_w),
             self.verdict_card(True, "Recall the exact difference", card_w)),
            (self.verdict_card(False, "Accepting altered fixed forms", card_w),
             self.verdict_card(True, "Check the form word by word", card_w)),
        ]
        for (wrong, right), yy in zip(pairs, [1.6, 0.05, -1.5]):
            wrong.move_to(LEFT_ZONE + UP * yy)
            right.move_to(RIGHT_ZONE + UP * yy)
        header = pill("3 mistakes", BAD, size=LABEL).move_to(UP * (CARD_TOP - 0.3))
        self.validator.check_in_frame(VGroup(header, *[c for p in pairs for c in p]))

        n = self.narrate(
            id="mistakes_01",
            text="Three common mistakes. The first is judging by how natural it sounds, not by whether it fits. The second "
                 "is confusing sister idioms. The third is accepting altered forms of fixed idioms.",
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
        ("Which is correct?", ["The team gave in to success.", "The team gave up their victory happily.",
                               "The team gave in to win.", "The team gave up after one attempt."], "d",
         "the others clash with the idiom's meaning"),
        ("Choose the correct form:", ["take it for granted", "take it as granted", "take it with granted",
                                      "take it by granted"], "a", "the fixed form"),
        ("Which fits?  “The manager ______ to the delays because the client was a friend.”",
         ["saw eye to eye", "called it a day", "turned a blind eye", "called the shots"], "c", "ignored deliberately"),
    ]

    def practice(self):
        self.scene_start("S13_practice", title="Practice Questions")

        lines = VGroup(*[VGroup(VGroup(pill(str(i + 1), FOCUS, size=SMALL), text(stem, LABEL, WORD))
                                .arrange(RIGHT, buff=0.35),
                                fitted_text("   ".join(f"({l}) {o}" for l, o in zip("abcd", opts)), SAFE_W - 1.6, LABEL,
                                            INK, NORMAL, max_lines=2))
                         .arrange(DOWN, buff=0.2, aligned_edge=LEFT)
                         for i, (stem, opts, _k, _why) in enumerate(self.PRACTICE)])
        lines.arrange(DOWN, buff=0.45, aligned_edge=LEFT)
        board = self.card(lines, color=FOCUS)
        fit_within(board, SAFE_W, SAFE_H - 1.2)
        board.move_to(UP * 0.4)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="practice_01",
            text="Your turn. One: which is correct: the team gave in to success, the team gave up their victory happily, "
                 "the team gave in to win, or the team gave up after one attempt? Two: choose the correct form: take it "
                 "for granted, take it as granted, take it with granted, or take it by granted? Three: which fits: the "
                 "manager, blank, to the delays, because the client was a friend? Saw eye to eye, called it a day, turned "
                 "a blind eye, or called the shots?",
            voice="default",
            subtitle=True,
            pause_after=12.0,
        )
        self.play(FadeIn(board[0]))
        for ln, (spoken, first_option) in zip(lines, [("One", "success"), ("Two", "take"), ("Three", "Saw")]):
            self.at_word(n, spoken, occurrence=1)
            self.play(FadeIn(ln[0], shift=UP * 0.15), run_time=0.4)
            self.at_word(n, first_option, occurrence=1)
            self.play(FadeIn(ln[1], shift=LEFT * 0.15), run_time=0.4)
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        self.clear_stage()
        self.scene_end("S13_practice")

    # =============================================== 14. ANSWERS ==========

    def answers(self):
        self.scene_start("S14_answers", title="Answers")

        assert self.PRACTICE[2][1][2] == "turned a blind eye" and SISTERS[3][1] == "ignore deliberately"
        rows = VGroup(*[VGroup(pill(str(i + 1), FOCUS, size=SMALL),
                               pill(f"({key}) {opts['abcd'.index(key)]}", GOOD, size=LABEL), text(why, LABEL, INK))
                        .arrange(RIGHT, buff=0.3) for i, (_stem, opts, key, why) in enumerate(self.PRACTICE)])
        rows.arrange(DOWN, buff=0.7, aligned_edge=LEFT)
        fit_within(rows, SAFE_W, SAFE_H - 1.2)
        rows.move_to(UP * 0.3)
        self.validator.check_in_frame(rows)

        n = self.narrate(
            id="answers_01",
            text="One: the team gave up after one attempt. The others clash with the meaning of the idiom. Two: take it "
                 "for granted: the fixed form. Three: turned a blind eye: ignored deliberately.",
            voice="default",
            subtitle=True,
        )
        for r, (spoken, why) in zip(rows, [("attempt", "clash"), ("granted", "fixed"), ("blind", "ignored")]):
            self.at_word(n, spoken)
            self.play(FadeIn(r[:2], shift=RIGHT * 0.2), run_time=0.5)
            self.at_word(n, why)
            self.play(FadeIn(r[2], shift=LEFT * 0.1), run_time=0.4)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S14_answers")

    # ================================================ 15. RECAP ==========

    def recap(self):
        self.scene_start("S15_recap", title="Recap Card")

        card, table = self.recap_card("Recap Card: Video 5", [
            ["Clash test", "does the idiom's meaning agree with the rest of the sentence?"],
            ["Sister idioms", "give up / give in;  eleventh hour / nick of time;  close shave / clean sweep"],
            ["Fixed forms", "make ends meet, by and large, take for granted"],
        ])
        card.move_to(UP * 0.2)
        self.validator.check_in_frame(card)

        n = self.narrate(
            id="recap_01",
            text="To recap. Run the clash test: does the idiom's meaning agree with the rest of the sentence? Keep the "
                 "sister idioms apart: give up and give in, the eleventh hour and the nick of time, a close shave and a "
                 "clean sweep. And respect the fixed forms: make ends meet, by and large, take for granted.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(card[0]), FadeIn(table[0]))
        for row, spoken in zip(table[1:], ["clash", "sister", "fixed"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.45)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S15_recap")

    # ================================================= 16. NEXT ==========

    def next_video(self):
        self.scene_start("S16_next", title="Next")

        again = pill("the idioms that appear again and again in exam papers", BAD, size=LABEL)
        nxt = pill("Next:  Exam-Oriented Idioms", FOCUS, size=LABEL)
        VGroup(again, nxt).arrange(DOWN, buff=0.8).move_to(UP * 0.2)
        self.no_overlap(again, nxt)
        self.validator.check_in_frame(VGroup(again, nxt))

        n = self.narrate(
            id="next_01",
            text="Video six collects the idioms that appear again and again in exam papers.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Video")
        self.play(FadeIn(nxt, scale=1.05))
        self.at_word(n, "again", occurrence=1)
        self.play(FadeIn(again, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S16_next")

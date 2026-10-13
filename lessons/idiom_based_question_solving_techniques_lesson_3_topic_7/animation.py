"""
animation.py for the LMS video generator.

Course : C-CAT - Section A - English
Module : Module 1 - Vocabulary
Lesson : Lesson 3 - Idioms & Phrases
Video  : 07 - Idiom-Based Question-Solving Techniques (Video 7 of 7)

Source script:
  C:\\Users\\User\\Downloads\\C-CAT_SectionA_Module1_English\\English\\Module 1 - Vocabulary\\
  Lesson 3 - Idioms & Phrases\\07 - Idiom-Based Question-Solving Techniques.pdf

Built on the golden-reference pattern:
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``;
  * layouts stacked with next_to and guarded with ``no_overlap``; nothing is
    ever animated onto or into another box.

The four checks live in CHECKS (L, O, W, T) and the 30-second budget in TIMELINE; the L-O-W-T card stays pinned top-right through the worked examples and Hook, Solved, and each check lights up as it is used.
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

CHECKS = [("L", "Literal", BAD), ("O", "Opposite", RATIO), ("W", "Word-match", SECOND),
          ("T", "Tone & key feature", FOCUS)]
CHECK_COL = {k: c for k, _, c in CHECKS}

# Time budget from the script (seconds): (start, end, step).
TIMELINE = [(0, 5, "read the idiom and any sentence; predict"), (5, 15, "strike literal and opposite options"),
            (15, 25, "strike word-match traps; compare tone and key feature"), (25, 30, "confirm in the sentence")]


class IdiomTechniquesVideo(LMSScene):
    lesson_title = "Idiom-Based Question-Solving Techniques"

    def construct(self):
        self.camera.background_color = BG

        self.lesson_intro()
        self.hook()
        self.concept()
        self.why_you_need_it()
        self.analogy()
        self.example_leg()
        self.example_loggerheads()
        self.example_fingers()
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

    def method_strip(self, size=LABEL):
        parts = [("PREDICT", STEP_COLS["PREDICT"])] + [(k, c) for k, _, c in CHECKS] + [("CONFIRM", GOOD)]
        chips = []
        for i, (t, c) in enumerate(parts):
            if i:
                chips.append(text("→", size, MUTED))
            chips.append(pill(t, c, size=size))
        return VGroup(*chips).arrange(RIGHT, buff=0.2)

    def check_pin(self):
        return self.steps_pin("L-O-W-T", [(f"{k}  {name}", c) for k, name, c in CHECKS])

    def light(self, letter):
        """Animation: light the row of the pinned L-O-W-T panel for this check."""
        return self.pin_step([k for k, _, _ in CHECKS].index(letter), color=CHECK_COL[letter])

    def note_card(self, fill=None):
        head = VGroup(text("APPRAISAL NOTE", SMALL, RATIO, BOLD), pill("0:30", BAD, size=SMALL)).arrange(RIGHT, buff=0.5)
        s_ = (f"“Karthik's {fill}.”" if fill else "“Karthik is the dark horse of this batch.”")
        cx, w = self.free_area()
        line = fitted_text(s_, min(w - 1.4, SAFE_W - 1.8), LABEL, INK, NORMAL, max_lines=2,
                           t2c={fill or "dark horse": GOOD if fill else WORD})
        card = self.card(VGroup(head, line).arrange(DOWN, buff=0.2, aligned_edge=LEFT), width=min(w - 0.2, SAFE_W - 0.4))
        return card.move_to(RIGHT * cx + UP * (CARD_TOP - card.height / 2))

    def left_question(self, idiom, options, key, traps):
        """Idiom question at the left, beside the pinned L-O-W-T panel."""
        q = OptionQuestion(f"“{idiom}”", options, key, traps, word_size=BODY)
        fit_height(q.group, SAFE_H - 1.8)
        q.group.to_edge(LEFT, buff=SAFE + 0.6).set_y(0.2)
        self.no_overlap(q.group, self.pinned)
        self.validator.check_in_frame(q.group)
        return q

    # ========================================= 0. LESSON INTRO ==========

    def lesson_intro(self):
        self.scene_start("S00_intro", title="Lesson Introduction")

        crumb = self.breadcrumb("English · Module 1 Vocabulary", "Lesson 3 · Idioms & Phrases", "Video 7")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        ideas = VGroup(*[pill(t, c, size=LABEL) for t, c in [("meanings", WORD), ("contexts", RATIO),
                                                            ("phrasal verbs", SECOND), ("confusions", BAD),
                                                            ("exam idioms", GOOD)]]).arrange(RIGHT, buff=0.3)
        fit_width(ideas, SAFE_W)
        one = pill("today: one method", FOCUS, size=LABEL)
        VGroup(ideas, one).arrange(DOWN, buff=0.8).move_to(DOWN * 0.1)
        self.no_overlap(crumb, ideas, one)
        self.validator.check_in_frame(VGroup(crumb, ideas, one))

        n = self.narrate(
            id="intro_01",
            text="Videos one to six gave you meanings, contexts, phrasal verbs, confusions and exam idioms. Today they "
                 "become one method.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.at_word(n, "meanings")
        self.play(LaggedStart(*[FadeIn(i, shift=UP * 0.1) for i in ideas], lag_ratio=0.3), run_time=2.5)
        self.at_word(n, "Today")
        self.play(FadeIn(one, shift=UP * 0.1))
        self.wait_for_narration(n)

        title = fitted_text("Idiom-Based Question-Solving Techniques", SAFE_W, 60, INK, BOLD)
        underline = Line(LEFT, RIGHT, color=SECOND, stroke_width=5).set_width(title.width * 0.6)
        VGroup(title, underline).arrange(DOWN, buff=0.2).move_to(UP * 0.2)
        n = self.narrate(
            id="intro_02",
            text="This is the last video of lesson three: idiom-based question-solving techniques.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(VGroup(ideas, one), shift=UP * 0.3))
        self.at_word(n, "idiom-based")
        self.play(Write(title), run_time=1.1)
        self.play(GrowFromCenter(underline))
        self.wait_for_narration(n)

        goals = [
            ("Solve any idiom question with a fixed elimination order", BAD),
            ("Handle unfamiliar idioms with the picture method", GOOD),
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
            text="By the end of this video, you'll solve any idiom question with a fixed elimination order, and handle "
                 "unfamiliar idioms with the picture method.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(underline), ReplacementTransform(title, small_title), run_time=0.8)
        self.play(FadeIn(objectives[0]), FadeIn(heading))
        for row_, spoken in zip(rows, ["solve", "handle"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row_, shift=RIGHT * 0.2), run_time=0.5)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_intro")

    # ================================================= 1. HOOK ==========

    HOOK = dict(word="dark horse", options=["He is often absent", "He is dishonest", "He works the hardest",
                                            "His abilities are not yet known but may surprise everyone"], key="d",
                traps={"a": "T: negative tone", "b": "T: negative tone", "c": "T: a different claim"})

    def hook(self):
        self.scene_start("S01_hook", title="Hook")

        h = self.HOOK
        note = self.note_card()
        q = OptionQuestion(h["word"], h["options"], h["key"], h["traps"])
        opts = q.rows.copy().arrange_in_grid(rows=2, cols=2, buff=(1.0, 0.35), cell_alignment=LEFT)
        fit_width(opts, SAFE_W)
        ask = pill("what is she saying about Karthik?", FOCUS, size=LABEL)
        ask.next_to(note, DOWN, buff=0.5)
        opts.next_to(ask, DOWN, buff=0.5)
        self.no_overlap(note, ask, opts)
        self.validator.check_in_frame(VGroup(note, ask, opts))

        n = self.narrate(
            id="hook_01",
            text="Your manager's appraisal note says: Karthik is the dark horse of this batch. You have thirty seconds.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "appraisal")
        self.play(FadeIn(note, shift=DOWN * 0.2))
        self.at_word(n, "seconds")
        self.play(Indicate(note[1][0][1], color=BAD, scale_factor=1.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_02",
            text="What is she saying about Karthik? He is often absent, he is dishonest, he works the hardest, or his "
                 "abilities are not yet known, but may surprise everyone?",
            voice="default",
            subtitle=True,
            pause_after=3.0,
        )
        self.at_word(n, "What")
        self.play(FadeIn(ask, shift=UP * 0.1))
        for row, spoken in zip(opts, ["absent", "dishonest", "hardest", "abilities"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=UP * 0.15), run_time=0.35)
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        self.clear_stage()
        self.scene_end("S01_hook")

    # ============================================== 2. CONCEPT ==========

    def concept(self):
        self.scene_start("S02_concept", title="The Concept")

        head = pill("four kinds of distractor  →  four checks:  L-O-W-T", FOCUS, size=LABEL)
        fit_width(head, SAFE_W)
        head.move_to(UP * (CARD_TOP - head.height / 2))
        rows = VGroup(*[VGroup(pill(k, c, size=BODY), text(name, LABEL, c, BOLD),
                               fitted_text(q, 6.4, LABEL, INK)).arrange(RIGHT, buff=0.35)
                        for (k, name, c), q in zip(CHECKS, [
                            "strike the option that describes the picture, not the idea",
                            "strike the option that reverses the meaning",
                            "options that reuse a word from the idiom: usually traps",
                            "survivors: right tone + key feature (fake, risky, sudden, rare)"])])
        rows.arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        fit_within(rows, SAFE_W, SAFE_H - head.height - 1.6)
        rows.next_to(head, DOWN, buff=0.45)
        self.no_overlap(head, rows)
        self.validator.check_in_frame(VGroup(head, rows))

        n = self.narrate(
            id="concept_01",
            text="Idiom distractors come in four kinds, so there are four checks: L, O, W, T.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "checks")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_02",
            text="L is literal: strike the option that describes the picture, not the idea. O is opposite: strike the "
                 "option that reverses the meaning. W is word-match: be suspicious of options that reuse a word from the "
                 "idiom. They're usually traps. And T is tone and key feature: of the survivors, pick the one with the "
                 "right tone, and the idiom's key feature: fake, risky, sudden, rare.",
            voice="default",
            subtitle=True,
        )
        for r, spoken in zip(rows[:3], ["literal", "opposite", "word-match"]):
            self.at_word(n, spoken)
            self.play(FadeIn(r, shift=RIGHT * 0.2), run_time=0.45)
        self.at_word(n, "traps")
        self.play(Indicate(rows[2][2], color=SECOND, scale_factor=1.04))
        self.at_word(n, "tone", occurrence=1)
        self.play(FadeIn(rows[3], shift=RIGHT * 0.2), run_time=0.45)
        self.wait_for_narration(n)

        unknown = VGroup(pill("as always: PREDICT before reading the options", STEP_COLS["PREDICT"], size=LABEL),
                         pill("unknown idiom?  use the PICTURE: what would it most naturally stand for?", WORD,
                              size=LABEL),
                         pill("then apply L-O-W-T", FOCUS, size=LABEL),
                         text("you'll often eliminate two or three options without knowing the idiom", LABEL, GOOD))\
            .arrange(DOWN, buff=0.45)
        fit_width(unknown, SAFE_W).move_to(UP * 0.3)
        self.validator.check_in_frame(unknown)
        n = self.narrate(
            id="concept_03",
            text="As always, predict before reading the options. For an idiom you don't know, use the picture: what would "
                 "this image most naturally stand for? Then apply L, O, W, T. You'll often eliminate two or three "
                 "options, even without knowing the idiom.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(VGroup(head, rows)))
        for u, spoken in zip(unknown, ["predict", "picture", "apply", "eliminate"]):
            self.at_word(n, spoken)
            self.play(FadeIn(u, shift=UP * 0.1), run_time=0.5)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_concept")

    # ======================================== 3. WHY YOU NEED IT ==========

    def why_you_need_it(self):
        self.scene_start("S03_why", title="Why You Need It")

        time_ = pill("an idiom question: under 30 seconds", RATIO, size=BODY)
        order = pill("a fixed order removes hesitation", WORD, size=LABEL)
        most = pill("L and W alone remove most distractors", BAD, size=LABEL)
        guess = pill("+3 / −1 marking:  fewer options left  →  a guess becomes worthwhile", GOOD, size=LABEL)
        group = VGroup(time_, order, most, guess).arrange(DOWN, buff=0.5)
        fit_width(group, SAFE_W).move_to(UP * 0.3)
        self.no_overlap(time_, order, most, guess)
        self.validator.check_in_frame(group)

        n = self.narrate(
            id="why_01",
            text="Idiom questions should take under thirty seconds. A fixed order removes hesitation, and L and W alone "
                 "remove most distractors, which makes a guess worthwhile under plus three, minus one marking.",
            voice="default",
            subtitle=True,
        )
        for g, spoken in zip(group, ["thirty", "fixed", "alone", "guess"]):
            self.at_word(n, spoken)
            self.play(FadeIn(g, shift=UP * 0.1), run_time=0.5)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_why")

    # ============================================== 4. ANALOGY ==========

    def analogy(self):
        self.scene_start("S04_analogy", title="The Analogy")

        # Four filter layers drawn as lines; each impurity stops just above the layer that catches it.
        x0, x1 = -3.2, 5.6
        ys = [1.1, 0.3, -0.5, -1.3]
        layers = VGroup(*[Line(RIGHT * x0 + UP * y, RIGHT * x1 + UP * y, color=c, stroke_width=6)
                          for y, (_, _, c) in zip(ys, CHECKS)])
        labels = VGroup(*[text(f"{k}  {name.split()[0]}", SMALL, c, BOLD).next_to(line, LEFT, buff=0.25)
                          for line, (k, name, c) in zip(layers, CHECKS)])
        drops_ = [("literal", 0), ("opposite", 1), ("word-match", 2), ("wrong tone", 3), ("answer", None)]
        drops = VGroup(*[pill(t, GOOD if stop is None else MUTED, size=SMALL) for t, stop in drops_])
        for d in drops:
            fit_width(d, 1.5)
        for i, d in enumerate(drops):
            d.move_to(RIGHT * (x0 + 0.9 + i * 1.75) + UP * 2.1)
        clean = text("clean water", SMALL, GOOD).next_to(layers[-1], DOWN, buff=0.9).align_to(layers[-1], LEFT)
        self.no_overlap(VGroup(labels), drops)
        self.validator.check_in_frame(VGroup(layers, labels, drops, clean))

        n = self.narrate(
            id="analogy_01",
            text="A four-layer water filter: each layer catches a different kind of impurity.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "four-layer")
        self.play(LaggedStart(*[Create(l) for l in layers], lag_ratio=0.2), FadeIn(labels))
        self.at_word(n, "catches")
        self.play(FadeIn(drops, shift=DOWN * 0.1), FadeIn(clean))
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_02",
            text="The literal layer catches the most, so it comes first.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "literal")
        self.play(Indicate(labels[0], color=BAD, scale_factor=1.2))
        for chip, (label, stop) in zip(drops, drops_):
            target_y = ys[stop] + 0.38 if stop is not None else ys[-1] - 0.9
            self.play(chip.animate.set_y(target_y), run_time=0.45)
            if stop is not None:
                self.play(chip.animate.set_opacity(0.35), run_time=0.2)
        self.at_word(n, "first")
        self.play(Indicate(layers[0], color=BAD), Indicate(drops[-1], color=GOOD))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_analogy")

    # ======================================== 5-7. WORKED EXAMPLES ==========

    def example_leg(self):
        self.scene_start("S05_ex_leg", title="Worked Example 1")
        self.play(self.pin(self.check_pin()))

        q = self.left_question("To pull someone's leg", ["injure them", "tease them jokingly", "help them walk",
                                                         "insult them seriously"], "b",
                               {"a": "L: literal", "c": "L: literal", "d": "T: too serious"})

        n = self.narrate(
            id="ex1_01",
            text="To pull someone's leg. Injure them, tease them jokingly, help them walk, or insult them seriously? L: "
                 "injure them and help them walk are literal. T: insult them seriously is too serious. The answer is "
                 "tease them jokingly.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "pull")
        self.play(FadeIn(q.word, scale=1.1))
        self.at_word(n, "Injure", occurrence=1)
        self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.2) for r in q.rows], lag_ratio=0.2))
        self.at_word(n, "L")
        self.play(self.light("L"), *q.strike("a")[1], *q.strike("c")[1])
        self.at_word(n, "T")
        self.play(self.light("T"), *q.strike("d")[1])
        self.at_word(n, "answer")
        self.play(*q.confirm()[1])
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_ex_leg")

    def example_loggerheads(self):
        self.scene_start("S06_ex_loggerheads", title="Worked Example 2")

        q = self.left_question("To be at loggerheads", ["be in strong disagreement", "be tired", "be logging data",
                                                        "agree"], "a",
                               {"b": "unrelated", "c": "W: reuses “log”", "d": "O: opposite"})

        n = self.narrate(
            id="ex2_01",
            text="To be at loggerheads. Be in strong disagreement, be tired, be logging data, or agree? O: agree is the "
                 "opposite. W: be logging data just reuses a word. Be tired is unrelated. The answer is: be in strong "
                 "disagreement.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "loggerheads")
        self.play(FadeIn(q.word, scale=1.1))
        self.at_word(n, "strong", occurrence=1)
        self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.2) for r in q.rows], lag_ratio=0.2))
        self.at_word(n, "O")
        self.play(self.light("O"), *q.strike("d")[1])
        self.at_word(n, "W")
        self.play(self.light("W"), *q.strike("c")[1])
        self.at_word(n, "tired", occurrence=2)
        self.play(*q.strike("b")[1])
        self.at_word(n, "answer")
        self.play(*q.confirm()[1])
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_ex_loggerheads")

    def example_fingers(self):
        self.scene_start("S07_ex_fingers", title="Worked Example 3")

        q = self.left_question("To keep one's fingers crossed", ["hope for a good result", "tell a lie", "be nervous",
                                                                 "be injured"], "a",
                               {"b": "T: a different gesture", "c": "misses the hope", "d": "L: literal"})

        n = self.narrate(
            id="ex3_01",
            text="To keep one's fingers crossed. Hope for a good result, tell a lie, be nervous, or be injured? L: be "
                 "injured is literal. T: tell a lie is the meaning of a different gesture. Be nervous is close, but it "
                 "misses the hope. The answer is: hope for a good result.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "fingers")
        self.play(FadeIn(q.word, scale=1.1))
        self.at_word(n, "Hope", occurrence=1)
        self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.2) for r in q.rows], lag_ratio=0.2))
        self.at_word(n, "L")
        self.play(self.light("L"), *q.strike("d")[1])
        self.at_word(n, "T")
        self.play(self.light("T"), *q.strike("b")[1])
        self.at_word(n, "nervous", occurrence=2)
        self.play(*q.strike("c")[1])
        self.at_word(n, "answer")
        self.play(*q.confirm()[1])
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S07_ex_fingers")

    # ================================================ 8. RULES ==========

    def rules(self):
        self.scene_start("S08_rules", title="Rules")
        self.play(self.unpin())

        strip = self.method_strip()
        fit_width(strip, SAFE_W)
        strip.move_to(UP * (CARD_TOP - strip.height / 2))
        table = self.table_rows(["Check", "Catches"], [
            ["L", "the picture read literally"],
            ["O", "the reversed meaning"],
            ["W", "options reusing the idiom's words"],
            ["T", "wrong tone or missing key feature"],
        ], [2.0, 9.0], size=LABEL)
        for row, (_, _, c) in zip(table[1:], CHECKS):
            row[0].set_color(c)
        board = self.card(table, width=SAFE_W - 0.2)
        fit_height(board, SAFE_H - strip.height - 1.4)
        board.next_to(strip, DOWN, buff=0.5)
        self.no_overlap(strip, board)
        self.validator.check_in_frame(VGroup(strip, board))

        n = self.narrate(
            id="rules_01",
            text="The full method: predict, then L, O, W, T, then confirm. L catches the picture read literally. O catches "
                 "the reversed meaning. W catches options reusing the idiom's words. And T catches the wrong tone, or a "
                 "missing key feature.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "predict")
        self.play(LaggedStart(*[FadeIn(c, shift=RIGHT * 0.1) for c in strip], lag_ratio=0.1))
        self.play(FadeIn(board[0]), FadeIn(table[0]))
        for row, spoken in zip(table[1:], ["literally", "reversed", "reusing", "tone"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.45)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S08_rules")

    # ============================================== 9. PROCESS ==========

    def process(self):
        self.scene_start("S09_process", title="The Process: 30 Seconds")

        scale = 0.38                                          # units per second
        cols = [STEP_COLS["PREDICT"], BAD, RATIO, GOOD]
        segs = VGroup(*[Rectangle(width=(e - s_) * scale, height=0.55, color=c, fill_color=c, fill_opacity=0.35)
                        for (s_, e, _), c in zip(TIMELINE, cols)]).arrange(RIGHT, buff=0)
        segs.move_to(UP * 1.4)
        ticks = VGroup(*[text(f"{t} s", SMALL, MUTED).next_to(segs, DOWN, buff=0.15).set_x(segs.get_left()[0] + t * scale)
                         for t in [0, 5, 15, 25, 30]])
        labels = VGroup(*[fitted_text(lab, 7.4, LABEL, c) for (_, _, lab), c in zip(TIMELINE, cols)])
        rows = VGroup(*[VGroup(pill(f"{s_}–{e} s", c, size=SMALL), lab).arrange(RIGHT, buff=0.3)
                        for (s_, e, _), c, lab in zip(TIMELINE, cols, labels)]).arrange(DOWN, buff=0.25,
                                                                                        aligned_edge=LEFT)
        rows.next_to(ticks, DOWN, buff=0.5)
        assert TIMELINE[0][0] == 0 and TIMELINE[-1][1] == 30 and all(a[1] == b[0] for a, b in zip(TIMELINE, TIMELINE[1:]))
        self.no_overlap(VGroup(segs, ticks), rows)
        self.validator.check_in_frame(VGroup(segs, ticks, rows))

        n = self.narrate(
            id="process_01",
            text="Here's the thirty-second budget. From zero to five seconds, read the idiom and any sentence, and predict. "
                 "From five to fifteen, strike literal and opposite options. From fifteen to twenty-five, strike "
                 "word-match traps, and compare tone and key feature. From twenty-five to thirty, confirm in the "
                 "sentence.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "budget")
        self.play(FadeIn(ticks))
        for seg, row, (spoken, occ) in zip(segs, rows, [("zero", 1), ("five", 2), ("fifteen", 2),
                                                         ("twenty-five", 2)]):
            self.at_word(n, spoken, occurrence=occ)
            self.play(GrowFromEdge(seg, LEFT), FadeIn(row, shift=RIGHT * 0.2), run_time=0.5)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S09_process")

    # ========================================== 10. HOOK, SOLVED ==========

    def hook_solved(self):
        self.scene_start("S10_hook_solved", title="Hook, Solved")
        self.play(self.pin(self.check_pin()))

        h = self.HOOK
        note = self.note_card()
        q = OptionQuestion(h["word"], h["options"], h["key"], h["traps"], word_size=LABEL)
        fit_height(q.group, note.get_bottom()[1] - 0.4 - (BOTTOM_Y + 1.4))     # leaves room for the verdict
        q.group.next_to(note, DOWN, buff=0.4).to_edge(LEFT, buff=SAFE + 0.6)
        pin_left = self.pinned.get_left()[0]
        predict = pill("predict: abilities unknown, but may surprise", STEP_COLS["PREDICT"], size=SMALL)
        fit_width(predict, pin_left - 0.3 - (q.word.get_right()[0] + 0.3))
        predict.next_to(q.word, RIGHT, buff=0.3)
        fixed = self.note_card(fill="abilities are not yet known, but he may surprise everyone")
        verdict = pill("a compliment, with a hint of expectation", GOOD, size=SMALL)
        verdict.next_to(q.group, DOWN, buff=0.3).align_to(q.group, LEFT)
        self.no_overlap(note, q.group, verdict)
        self.no_overlap(note, self.pinned)
        self.no_overlap(q.rows, predict)
        self.no_overlap(predict, self.pinned)
        self.validator.check_in_frame(VGroup(note, q.group, predict, verdict))

        n = self.narrate(
            id="solved_01",
            text="Let's solve the hook. Read: dark horse, in an appraisal. Predict: someone whose abilities are unknown, "
                 "but who may surprise.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(note), FadeIn(q.word), FadeIn(q.rows))
        self.at_word(n, "Read")
        self.play(Indicate(q.word, color=WORD, scale_factor=1.08))
        self.at_word(n, "Predict")
        self.play(FadeIn(predict, shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_02",
            text="Eliminate with T. Often absent and dishonest turn it negative, and a dark horse isn't a criticism. Works "
                 "the hardest is a different claim: hardest-working isn't unknown but surprising.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Eliminate")
        self.play(self.light("T"))
        self.at_word(n, "absent")
        self.play(*q.strike("a")[1], *q.strike("b")[1])
        self.at_word(n, "Works")
        self.play(*q.strike("c")[1])
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_03",
            text="Confirm: Karthik's abilities are not yet known, but he may surprise everyone. That's the answer. It's a "
                 "compliment, with a hint of expectation.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Confirm")
        self.play(ReplacementTransform(note, fixed))
        self.at_word(n, "answer")
        self.play(*q.confirm()[1])
        self.at_word(n, "compliment")
        self.play(FadeIn(verdict, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S10_hook_solved")

    # ========================================== 11. EXAM PATTERNS ==========

    def exam_patterns(self):
        self.scene_start("S11_patterns", title="Exam Patterns and Solving Models")
        self.play(self.unpin())

        table = self.table_rows(["Pattern", "First checks"], [
            ["Meaning of the idiom", "L, O"],
            ["Fill in the idiom", "situation → meaning, then T"],
            ["Correct usage", "clash test (Video 5)"],
            ["Phrasal verb", "verb + particle unit; sister traps"],
        ], [5.4, 6.4], size=LABEL)
        board = self.card(table, width=SAFE_W - 0.2).move_to(UP * 0.4)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="patterns_01",
            text="Which checks come first? For the meaning of an idiom: L and O. For fill in the idiom: situation, then "
                 "meaning, then T. For correct usage: the clash test from video five. And for a phrasal verb: the verb "
                 "plus particle unit, and its sister traps.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "first")
        self.play(FadeIn(board[0]), FadeIn(table[0]))
        for row, spoken in zip(table[1:], ["meaning", "fill", "usage", "phrasal"]):
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
            (self.verdict_card(False, "Choosing an option that shares a word", card_w),
             self.verdict_card(True, "Word-match is usually a trap", card_w)),
            (self.verdict_card(False, "Guessing before striking the literal option", card_w),
             self.verdict_card(True, "Strike the literal option first", card_w)),
            (self.verdict_card(False, "Ignoring the key feature", card_w),
             self.verdict_card(True, "fake · risky · rare", card_w)),
        ]
        for (wrong, right), yy in zip(pairs, [1.6, 0.05, -1.5]):
            wrong.move_to(LEFT_ZONE + UP * yy)
            right.move_to(RIGHT_ZONE + UP * yy)
        header = pill("3 mistakes", BAD, size=LABEL).move_to(UP * (CARD_TOP - 0.3))
        self.validator.check_in_frame(VGroup(header, *[c for p in pairs for c in p]))

        n = self.narrate(
            id="mistakes_01",
            text="Three common mistakes. The first is choosing an option because it shares a word with the idiom. The "
                 "second is guessing without striking the literal option first. The third is ignoring the key feature: "
                 "fake, risky, rare.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(header))
        for pr, (spoken, occ) in zip(pairs, [("first", 1), ("second", 1), ("third", 1)]):
            self.at_word(n, spoken, occurrence=occ)
            self.play(FadeIn(pr[0], shift=RIGHT * 0.3), FadeIn(pr[1], shift=LEFT * 0.3))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S12_mistakes")

    # ============================================== 13. PRACTICE ==========

    PRACTICE = [
        ("To turn over a new leaf", ["read a new page", "start gardening", "change one's behaviour for the better",
                                     "become lazy"], "c", {"a": "L: literal", "b": "L: literal", "d": "not the idea"}),
        ("To be in the same boat", ["travel together", "face the same difficult situation", "work on a ship", "compete"],
         "b", {"a": "L: literal", "c": "L: literal", "d": "not the idea"}),
        ("To throw in the towel", ["admit defeat", "clean up", "start a fight", "get angry"], "a",
         {"b": "L: literal", "c": "T: changes the meaning", "d": "T: changes the meaning"}),
    ]

    def practice(self):
        self.scene_start("S13_practice", title="Practice Questions")

        lines = VGroup(*[VGroup(VGroup(pill(str(i + 1), FOCUS, size=SMALL), pill(f"“{idiom}”", WORD, size=LABEL))
                                .arrange(RIGHT, buff=0.35),
                                text("   ".join(f"({l}) {o}" for l, o in zip("abcd", opts)), LABEL, INK))
                         .arrange(DOWN, buff=0.2, aligned_edge=LEFT)
                         for i, (idiom, opts, *_r) in enumerate(self.PRACTICE)])
        lines.arrange(DOWN, buff=0.45, aligned_edge=LEFT)
        board = self.card(lines, color=FOCUS)
        fit_within(board, SAFE_W, SAFE_H - 1.2)
        board.move_to(UP * 0.4)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="practice_01",
            text="Your turn, thirty seconds each. One: to turn over a new leaf. Read a new page, start gardening, change "
                 "one's behaviour for the better, or become lazy? Two: to be in the same boat. Travel together, face the "
                 "same difficult situation, work on a ship, or compete? Three: to throw in the towel. Admit defeat, clean "
                 "up, start a fight, or get angry?",
            voice="default",
            subtitle=True,
            pause_after=12.0,
        )
        self.play(FadeIn(board[0]))
        for ln, (spoken, first_option) in zip(lines, [("leaf", "Read"), ("boat", "Travel"), ("towel", "Admit")]):
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

        rows = VGroup()
        for idiom, opts, key, traps in self.PRACTICE:
            OptionQuestion(idiom, opts, key, traps)            # validates key / traps
            others = [f"({l}) {opts['abcd'.index(l)]}: {r}" for l, r in traps.items() if r != "not the idea"]
            rows.add(VGroup(VGroup(pill(f"“{idiom}”", WORD, size=LABEL), text("=", LABEL, MUTED),
                                   pill(f"({key}) {opts['abcd'.index(key)]}", GOOD, size=LABEL)).arrange(RIGHT, buff=0.3),
                            text("   ".join(others), SMALL, BAD)).arrange(DOWN, buff=0.18, aligned_edge=LEFT))
        rows.arrange(DOWN, buff=0.5, aligned_edge=LEFT)
        fit_within(rows, SAFE_W, SAFE_H - 1.2)
        rows.move_to(UP * 0.3)
        self.validator.check_in_frame(rows)

        n = self.narrate(
            id="answers_01",
            text="One: change one's behaviour for the better. Read a new page and start gardening are literal. Two: face "
                 "the same difficult situation. Travel together and work on a ship are literal. Three: admit defeat. "
                 "Clean up is literal, and start a fight and get angry change the meaning.",
            voice="default",
            subtitle=True,
        )
        for r, (spoken, trap, occ) in zip(rows, [("behaviour", "page", 1), ("face", "ship", 1), ("admit", "Clean", 1)]):
            self.at_word(n, spoken)
            self.play(FadeIn(r[0], shift=RIGHT * 0.2), run_time=0.5)
            self.at_word(n, trap, occurrence=occ)
            self.play(FadeIn(r[1], shift=LEFT * 0.1), run_time=0.4)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S14_answers")

    # ================================================ 15. RECAP ==========

    def recap(self):
        self.scene_start("S15_recap", title="Recap Card: Lesson 3 Method")

        card, table = self.recap_card("Recap Card: Lesson 3 Method", [
            ["Method", "PREDICT → L → O → W → T → CONFIRM"],
            ["First strike", "the literal option"],
            ["Unknown idiom", "picture → most natural idea → L-O-W-T"],
            ["Time", "under 30 seconds"],
        ])
        card.move_to(UP * 0.2)
        self.validator.check_in_frame(card)

        n = self.narrate(
            id="recap_01",
            text="To recap the lesson three method: predict, then L, O, W, T, then confirm. The first strike is the literal "
                 "option. For an unknown idiom: picture, then the most natural idea, then L, O, W, T. And the target time "
                 "is under thirty seconds.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(card[0]), FadeIn(table[0]))
        for row, spoken in zip(table[1:], ["predict", "strike", "unknown", "time"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.45)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S15_recap")

    # ================================================= 16. NEXT ==========

    def next_video(self):
        self.scene_start("S16_next", title="Next")

        done = pill("Lesson 3: Idioms & Phrases  ✓", GOOD, size=LABEL)
        todo = VGroup(pill("Lesson 3 Quiz", FOCUS, size=LABEL), pill("Cheat Sheet", WORD, size=LABEL))\
            .arrange(RIGHT, buff=0.6)
        squeeze = VGroup(pill("a whole phrase", MUTED, size=BODY), text("→", TITLE, MUTED),
                         pill("one word", SECOND, size=BODY)).arrange(RIGHT, buff=0.4)
        nxt = pill("Next lesson:  One-Word Substitution", FOCUS, size=BODY)
        VGroup(done, todo, squeeze, nxt).arrange(DOWN, buff=0.5).move_to(UP * 0.1)
        self.no_overlap(done, todo, squeeze, nxt)
        self.validator.check_in_frame(VGroup(done, todo, squeeze, nxt))

        n = self.narrate(
            id="next_01",
            text="Take the lesson three quiz, and keep the cheat sheet. Lesson four compresses whole phrases into single "
                 "words: one-word substitution.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(done, scale=1.1))
        self.at_word(n, "quiz")
        self.play(FadeIn(todo[0], shift=UP * 0.1))
        self.at_word(n, "cheat")
        self.play(FadeIn(todo[1], shift=UP * 0.1))
        self.at_word(n, "compresses")
        self.play(FadeIn(squeeze, shift=UP * 0.1))
        self.at_word(n, "one-word")
        self.play(FadeIn(nxt, scale=1.1))
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S16_next")

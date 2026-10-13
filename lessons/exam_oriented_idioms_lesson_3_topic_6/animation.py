"""
animation.py for the LMS video generator.

Course : C-CAT - Section A - English
Module : Module 1 - Vocabulary
Lesson : Lesson 3 - Idioms & Phrases
Video  : 06 - Exam-Oriented Idioms (Video 6 of 7)

Source script:
  C:\\Users\\User\\Downloads\\C-CAT_SectionA_Module1_English\\English\\Module 1 - Vocabulary\\
  Lesson 3 - Idioms & Phrases\\06 - Exam-Oriented Idioms.pdf

Built on the golden-reference pattern:
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``;
  * layouts stacked with next_to and guarded with ``no_overlap``; nothing is
    ever animated onto or into another box.

The fifteen exam idioms live in EXAM_IDIOMS and the one-line origin stories in ORIGIN; the rules tables, worked examples and answers are built from them.
The "old idioms" card (origin story, plain meaning, strike literal / opposite / nearby, confirm) stays pinned top-right through the worked examples and Hook, Solved.
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

# The script's Rules table, in order.
EXAM_IDIOMS = {
    "bell the cat": "take on a risky task for the group",
    "a Herculean task": "a task needing enormous effort",
    "Achilles' heel": "a fatal weakness",
    "crocodile tears": "fake sorrow",
    "a dark horse": "someone whose abilities are unknown but who may surprise",
    "to smell a rat": "to suspect something is wrong",
    "a red-letter day": "a very important, happy day",
    "to be in the doldrums": "to be low in spirits or inactive",
    "to throw down the gauntlet": "to issue a challenge",
    "a wild goose chase": "a hopeless, pointless search",
    "to rain cats and dogs": "to rain heavily",
    "to leave no stone unturned": "to try every possible way",
    "a bolt from the blue": "a complete surprise",
    "to have an axe to grind": "to have a selfish motive",
    "to take the bull by the horns": "to face a problem directly",
}
# One-line origin stories used in this video.
ORIGIN = {
    "bell the cat": "the mice agree a bell on the cat would save them, but no mouse dares to tie it",
    "a Herculean task": "Hercules and his twelve labours",
    "Achilles' heel": "the one weak spot of the hero Achilles",
    "crocodile tears": "crocodiles were said to weep while eating",
    "to throw down the gauntlet": "a knight threw down his glove as a challenge",
}
assert set(ORIGIN) <= set(EXAM_IDIOMS)


class ExamOrientedIdiomsVideo(LMSScene):
    lesson_title = "Exam-Oriented Idioms"

    def construct(self):
        self.camera.background_color = BG

        self.lesson_intro()
        self.hook()
        self.concept()
        self.why_you_need_it()
        self.analogy()
        self.example_herculean()
        self.example_achilles()
        self.example_crocodile()
        self.rules_first()
        self.rules_second()
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

    def story_pin(self):
        return self.steps_pin("old idioms", [("recall the ORIGIN story", RATIO),
                                             ("state the meaning plainly", STEP_COLS["PREDICT"]),
                                             ("strike literal, opposite, nearby", BAD),
                                             ("confirm in the sentence", GOOD)])

    def crisis_card(self, fill=None):
        head = text("TEAM CHAT  ·  release crisis", SMALL, RATIO, BOLD)
        s_ = (f"“Someone has to {fill} of telling the director.”" if fill
              else "“Someone has to bell the cat and tell the director the release will slip.”")
        cx, w = self.free_area()
        line = fitted_text(s_, min(w - 1.4, SAFE_W - 1.8), LABEL, INK, NORMAL, max_lines=2,
                           t2c={fill or "bell the cat": GOOD if fill else WORD})
        card = self.card(VGroup(head, line).arrange(DOWN, buff=0.2, aligned_edge=LEFT), width=min(w - 0.2, SAFE_W - 0.4))
        return card.move_to(RIGHT * cx + UP * (CARD_TOP - card.height / 2))

    def origin_example(self, idiom, shown_meaning):
        """Idiom, its one-line origin story, and the meaning the story leads to."""
        cx, w = self.free_area()
        title = pill(f"“{idiom}”", WORD, size=BODY)
        origin = VGroup(pill("origin", RATIO, size=SMALL),
                        fitted_text(ORIGIN[idiom], w - 2.6, LABEL, INK, NORMAL, max_lines=2)).arrange(RIGHT, buff=0.25)
        mean = VGroup(text("→", BODY, MUTED), pill(shown_meaning, GOOD, size=BODY)).arrange(RIGHT, buff=0.3)
        block = VGroup(title, origin, mean).arrange(DOWN, buff=0.6, aligned_edge=LEFT)
        fit_height(block, SAFE_H - 1.6)
        self.place_free(block, y=0.1)
        self.no_overlap(title, origin, mean)
        self.validator.check_in_frame(block)
        return title, origin, mean

    def idiom_board(self, items):
        table = self.table_rows(["Idiom", "Meaning"], [[i, m] for i, m in items], [4.6, 7.4], size=LABEL)
        for row in table[1:]:
            row[0].set_color(WORD)
        board = self.card(table, width=SAFE_W - 0.2)
        fit_height(board, SAFE_H - 1.0)
        board.move_to(UP * 0.3)
        self.validator.check_in_frame(board)
        return board, table

    # ========================================= 0. LESSON INTRO ==========

    def lesson_intro(self):
        self.scene_start("S00_intro", title="Lesson Introduction")

        crumb = self.breadcrumb("English · Module 1 Vocabulary", "Lesson 3 · Idioms & Phrases", "Video 6")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        store = pill("Videos 2 to 5: your everyday idiom store", MUTED, size=LABEL)
        old = pill("today: the older, more literary set that exam-setters favour", RATIO, size=LABEL)
        hard = pill("several are hard to guess from the picture alone", BAD, size=LABEL)
        group = VGroup(store, old, hard).arrange(DOWN, buff=0.6)
        fit_width(group, SAFE_W).move_to(DOWN * 0.1)
        self.no_overlap(crumb, store, old, hard)
        self.validator.check_in_frame(VGroup(crumb, group))

        n = self.narrate(
            id="intro_01",
            text="Videos two to five built your everyday idiom store. Today's list is the older, more literary set that "
                 "exam-setters favour, and several of them are hard to guess from the picture alone.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.at_word(n, "everyday")
        self.play(FadeIn(store, shift=UP * 0.1))
        self.at_word(n, "literary")
        self.play(FadeIn(old, shift=UP * 0.1))
        self.at_word(n, "hard")
        self.play(FadeIn(hard, shift=UP * 0.1))
        self.wait_for_narration(n)

        title = fitted_text("Exam-Oriented Idioms", SAFE_W, 72, INK, BOLD)
        underline = Line(LEFT, RIGHT, color=RATIO, stroke_width=5).set_width(title.width * 0.6)
        VGroup(title, underline).arrange(DOWN, buff=0.2).move_to(UP * 0.2)
        goals = [("Learn the idioms that recur most in exam papers", GOOD),
                 ("Use origin stories to remember the less transparent ones", RATIO)]
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
            text="These are the exam-oriented idioms. By the end of this video, you'll learn the idioms that recur most in "
                 "exam papers, and use origin stories to remember the less transparent ones.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(group, shift=UP * 0.3))
        self.at_word(n, "exam-oriented")
        self.play(Write(title), run_time=1.1)
        self.play(GrowFromCenter(underline))
        self.at_word(n, "By")
        self.play(FadeOut(underline), ReplacementTransform(title, small_title), run_time=0.8)
        self.play(FadeIn(objectives[0]), FadeIn(heading))
        for row_, spoken in zip(rows, ["learn", "origin"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row_, shift=RIGHT * 0.2), run_time=0.5)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_intro")

    # ================================================= 1. HOOK ==========

    HOOK = dict(word="bell the cat", options=["Someone to set an alarm", "Someone to spread the news informally",
                                              "Someone to avoid responsibility",
                                              "Someone to take on a risky task for the whole group"],
                key="d", traps={"a": "literal: bell", "b": "misses the RISK", "c": "the opposite"})

    def hook(self):
        self.scene_start("S01_hook", title="Hook")

        h = self.HOOK
        chat = self.crisis_card()
        q = OptionQuestion(h["word"], h["options"], h["key"], h["traps"])
        opts = q.rows.copy().arrange_in_grid(rows=2, cols=2, buff=(1.0, 0.35), cell_alignment=LEFT)
        fit_width(opts, SAFE_W)
        ask = pill("what is he asking for?", FOCUS, size=LABEL)
        ask.next_to(chat, DOWN, buff=0.5)
        opts.next_to(ask, DOWN, buff=0.5)
        self.no_overlap(chat, ask, opts)
        self.validator.check_in_frame(VGroup(chat, ask, opts))

        n = self.narrate(
            id="hook_01",
            text="During a release crisis, a senior developer writes: Someone has to bell the cat, and tell the director "
                 "the release will slip. What is he asking for?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "crisis")
        self.play(FadeIn(chat[0]), FadeIn(chat[1][0]))
        self.at_word(n, "bell")
        self.play(FadeIn(chat[1][1], shift=UP * 0.1))
        self.at_word(n, "What")
        self.play(FadeIn(ask, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_02",
            text="Someone to set an alarm, someone to spread the news informally, someone to avoid responsibility, or "
                 "someone to take on a risky task for the whole group?",
            voice="default",
            subtitle=True,
            pause_after=3.0,
        )
        for row, spoken in zip(opts, ["alarm", "spread", "avoid", "risky"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=UP * 0.15), run_time=0.35)
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        self.clear_stage()
        self.scene_end("S01_hook")

    # ============================================== 2. CONCEPT ==========

    def concept(self):
        self.scene_start("S02_concept", title="The Concept")

        sources = VGroup(*[pill(s_, RATIO, size=BODY) for s_ in ["fables", "history", "old professions"]])\
            .arrange(RIGHT, buff=0.5)
        obvious = text("so their pictures are less obvious", LABEL, MUTED)
        top = VGroup(text("exam idioms often come from", LABEL, INK), sources, obvious).arrange(DOWN, buff=0.4)
        top.move_to(UP * 0.4)
        self.validator.check_in_frame(top)

        n = self.narrate(
            id="concept_01",
            text="Exam idioms often come from fables, history or old professions, so their pictures are less obvious.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(top[0]))
        for s_, spoken in zip(sources, ["fables", "history", "professions"]):
            self.at_word(n, spoken)
            self.play(FadeIn(s_, shift=UP * 0.1), run_time=0.35)
        self.at_word(n, "obvious")
        self.play(FadeIn(obvious, shift=UP * 0.1))
        self.wait_for_narration(n)

        # The fable behind "bell the cat".
        idiom = pill("“bell the cat”", WORD, size=BODY)
        idiom.move_to(UP * (CARD_TOP - idiom.height / 2))
        story = VGroup(VGroup(pill("the fable", RATIO, size=SMALL),
                              text("the mice agree: a bell on the cat would save them", LABEL, INK))
                       .arrange(RIGHT, buff=0.3),
                       VGroup(pill("the catch", BAD, size=SMALL), text("but no mouse dares to tie it", LABEL, INK))
                       .arrange(RIGHT, buff=0.3)).arrange(DOWN, buff=0.35, aligned_edge=LEFT)
        mean = pill("take on a risky task everyone agrees is needed, but nobody wants to do", GOOD, size=LABEL)
        body = VGroup(story, mean).arrange(DOWN, buff=0.6)
        fit_width(body, SAFE_W)
        body.next_to(idiom, DOWN, buff=0.6)
        self.no_overlap(idiom, story, mean)
        self.validator.check_in_frame(VGroup(idiom, body))
        n = self.narrate(
            id="concept_02",
            text="Bell the cat comes from a fable in which the mice agree that a bell on the cat would save them, but no "
                 "mouse dares to tie it. So it means: take on a risky task that everyone agrees is needed, but nobody "
                 "wants to do.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(top))
        self.at_word(n, "Bell")
        self.play(FadeIn(idiom, scale=1.1))
        self.at_word(n, "mice")
        self.play(FadeIn(story[0], shift=RIGHT * 0.2))
        self.at_word(n, "dares")
        self.play(FadeIn(story[1], shift=RIGHT * 0.2))
        self.at_word(n, "means")
        self.play(FadeIn(mean, shift=UP * 0.1))
        self.wait_for_narration(n)

        tool = pill("a one-line ORIGIN STORY: the best memory tool", RATIO, size=BODY)
        chain = VGroup(pill("an arbitrary phrase", MUTED, size=LABEL), text("→", LABEL, MUTED),
                       pill("the story", RATIO, size=LABEL), text("→", LABEL, MUTED),
                       pill("a picture you can't forget", GOOD, size=LABEL)).arrange(RIGHT, buff=0.3)
        block = VGroup(tool, chain).arrange(DOWN, buff=0.8)
        fit_width(block, SAFE_W).move_to(UP * 0.3)
        self.validator.check_in_frame(block)
        n = self.narrate(
            id="concept_03",
            text="For these, a one-line origin story is the best memory tool. The story turns an arbitrary phrase into a "
                 "picture you can't forget.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(VGroup(idiom, body)))
        self.at_word(n, "origin")
        self.play(FadeIn(tool, scale=1.05))
        self.at_word(n, "turns")
        self.play(LaggedStart(*[FadeIn(c, shift=RIGHT * 0.1) for c in chain], lag_ratio=0.25))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_concept")

    # ======================================== 3. WHY YOU NEED IT ==========

    def why_you_need_it(self):
        self.scene_start("S03_why", title="Why You Need It")

        papers = VGroup(*[pill(p, RATIO, size=LABEL) for p in ["C-CAT", "bank papers", "placement papers"]])\
            .arrange(RIGHT, buff=0.5)
        traps = pill("a tempting literal option, or a “nearby” option", BAD, size=LABEL)
        safer = pill("knowing them outright is safer than reasoning under time pressure", GOOD, size=LABEL)
        group = VGroup(papers, traps, safer).arrange(DOWN, buff=0.7)
        fit_width(group, SAFE_W).move_to(UP * 0.3)
        self.no_overlap(papers, traps, safer)
        self.validator.check_in_frame(group)

        n = self.narrate(
            id="why_01",
            text="These idioms recur across C-CAT, bank and placement papers. Several have a tempting literal option, or a "
                 "nearby option, so knowing them outright is safer than reasoning under time pressure.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "recur")
        self.play(LaggedStart(*[FadeIn(p, shift=UP * 0.1) for p in papers], lag_ratio=0.3))
        self.at_word(n, "tempting")
        self.play(FadeIn(traps, shift=UP * 0.1))
        self.at_word(n, "safer")
        self.play(FadeIn(safer, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_why")

    # ============================================== 4. ANALOGY ==========

    def analogy(self):
        self.scene_start("S04_analogy", title="The Analogy")

        idiom = "to throw down the gauntlet"
        thing = Star(n=7, outer_radius=0.8, color=RATIO, fill_color=RATIO, fill_opacity=0.25)
        stand = Rectangle(width=2.0, height=0.7, color=MUTED, stroke_width=4).next_to(thing, DOWN, buff=0.15)
        what = text("?", TITLE, BAD).next_to(thing, UP, buff=0.2)
        exhibit = VGroup(thing, stand, what).move_to(LEFT * 4.0 + UP * 0.2)
        label = self.card(VGroup(text("MUSEUM LABEL", SMALL, RATIO, BOLD), text(f"“{idiom}”", LABEL, WORD),
                                 text(ORIGIN[idiom], LABEL, INK)).arrange(DOWN, buff=0.2, aligned_edge=LEFT))
        sense = pill("=  " + EXAM_IDIOMS[idiom], GOOD, size=BODY)
        right = VGroup(label, sense).arrange(DOWN, buff=0.5, aligned_edge=LEFT)
        fit_width(right, 7.4)
        right.move_to(RIGHT * 2.2 + UP * 0.2)
        self.no_overlap(exhibit, right)
        self.no_overlap(thing, stand)
        self.validator.check_in_frame(VGroup(exhibit, right))

        n = self.narrate(
            id="analogy_01",
            text="An old idiom is like an object in a museum. Without the label, it's a strange thing. With one line of "
                 "history, it makes sense instantly.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "museum")
        self.play(FadeIn(thing, scale=1.1), FadeIn(stand))
        self.at_word(n, "strange")
        self.play(FadeIn(what, shift=DOWN * 0.1))
        self.at_word(n, "history")
        self.play(FadeIn(label, shift=LEFT * 0.2))
        self.at_word(n, "sense")
        self.play(FadeOut(what), FadeIn(sense, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_analogy")

    # ======================================== 5-7. WORKED EXAMPLES ==========

    def example_herculean(self):
        self.scene_start("S05_ex_herculean", title="Worked Example 1")
        self.play(self.pin(self.story_pin()))

        title, origin, mean = self.origin_example("a Herculean task", "a task needing huge effort")

        n = self.narrate(
            id="ex1_01",
            text="A Herculean task. The origin: Hercules and his twelve labours. So it means a task needing huge effort.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Herculean")
        self.play(FadeIn(title, scale=1.1))
        self.at_word(n, "origin")
        self.play(FadeIn(origin, shift=RIGHT * 0.2), self.pin_step(0, color=RATIO))
        self.at_word(n, "means")
        self.play(FadeIn(mean, shift=UP * 0.1), self.pin_step(1, color=STEP_COLS["PREDICT"]))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_ex_herculean")

    def example_achilles(self):
        self.scene_start("S06_ex_achilles", title="Worked Example 2")

        title, origin, mean = self.origin_example("Achilles' heel", EXAM_IDIOMS["Achilles' heel"])

        n = self.narrate(
            id="ex2_01",
            text="Achilles' heel. The origin: the one weak spot of the hero Achilles. So it means a fatal weakness.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "heel")
        self.play(FadeIn(title, scale=1.1))
        self.at_word(n, "origin")
        self.play(FadeIn(origin, shift=RIGHT * 0.2), self.pin_step(0, color=RATIO))
        self.at_word(n, "means")
        self.play(FadeIn(mean, shift=UP * 0.1), self.pin_step(1, color=STEP_COLS["PREDICT"]))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_ex_achilles")

    def example_crocodile(self):
        self.scene_start("S07_ex_crocodile", title="Worked Example 3")

        title, origin, mean = self.origin_example("crocodile tears", EXAM_IDIOMS["crocodile tears"])

        n = self.narrate(
            id="ex3_01",
            text="Crocodile tears. The origin: crocodiles were said to weep while eating. So it means fake sorrow.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Crocodile")
        self.play(FadeIn(title, scale=1.1))
        self.at_word(n, "origin")
        self.play(FadeIn(origin, shift=RIGHT * 0.2), self.pin_step(0, color=RATIO))
        self.at_word(n, "means")
        self.play(FadeIn(mean, shift=UP * 0.1), self.pin_step(1, color=STEP_COLS["PREDICT"]))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S07_ex_crocodile")

    # ================================================ 8. RULES ==========

    def rules_first(self):
        self.scene_start("S08_rules_first", title="Rules: Exam Idioms (1)")
        self.play(self.unpin())

        board, table = self.idiom_board(list(EXAM_IDIOMS.items())[:8])

        n = self.narrate(
            id="rules_01",
            text="Here are the exam favourites. Bell the cat: take on a risky task for the group. A Herculean task: a task "
                 "needing enormous effort. Achilles' heel: a fatal weakness. Crocodile tears: fake sorrow. A dark horse: "
                 "someone whose abilities are unknown, but who may surprise. To smell a rat: to suspect something is "
                 "wrong. A red-letter day: a very important, happy day. To be in the doldrums: to be low in spirits, or "
                 "inactive.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "favourites")
        self.play(FadeIn(board[0]), FadeIn(table[0]))
        for row, spoken in zip(table[1:], ["Bell", "Herculean", "heel", "Crocodile", "dark", "smell", "red-letter",
                                           "doldrums"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.45)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S08_rules_first")

    def rules_second(self):
        self.scene_start("S09_rules_second", title="Rules: Exam Idioms (2)")

        board, table = self.idiom_board(list(EXAM_IDIOMS.items())[8:])

        n = self.narrate(
            id="rules_02",
            text="To throw down the gauntlet: to issue a challenge. A wild goose chase: a hopeless, pointless search. To "
                 "rain cats and dogs: to rain heavily. To leave no stone unturned: to try every possible way. A bolt from "
                 "the blue: a complete surprise. To have an axe to grind: to have a selfish motive. And to take the bull "
                 "by the horns: to face a problem directly.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(board[0]), FadeIn(table[0]))
        for row, spoken in zip(table[1:], ["gauntlet", "goose", "cats", "stone", "bolt", "axe", "bull"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.45)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S09_rules_second")

    # ============================================= 10. PROCESS ==========

    def process(self):
        self.scene_start("S10_process", title="The Process")

        steps = VGroup(*[VGroup(pill(str(i + 1), c, size=SMALL), fitted_text(s_, SAFE_W - 2.2, BODY, INK))
                         .arrange(RIGHT, buff=0.3) for i, (s_, c) in enumerate([
                             ("Recall the idiom and its origin story", RATIO),
                             ("State the meaning in plain words", STEP_COLS["PREDICT"]),
                             ("Eliminate literal, opposite and “nearby” options", BAD),
                             ("Confirm in the sentence", GOOD)])])
        steps.arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        board = self.card(steps).move_to(UP * 0.3)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="process_01",
            text="The process. First, recall the idiom and its origin story. Second, state the meaning in plain words. "
                 "Third, eliminate literal, opposite and nearby options. And fourth, confirm in the sentence.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(board[0]))
        for r, spoken in zip(steps, ["First", "Second", "Third", "fourth"]):
            self.at_word(n, spoken)
            self.play(FadeIn(r, shift=RIGHT * 0.2), run_time=0.45)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S10_process")

    # ========================================== 11. HOOK, SOLVED ==========

    def hook_solved(self):
        self.scene_start("S11_hook_solved", title="Hook, Solved")
        self.play(self.pin(self.story_pin()))

        h = self.HOOK
        chat = self.crisis_card()
        q = OptionQuestion(h["word"], h["options"], h["key"], h["traps"], word_size=LABEL)
        fit_height(q.group, chat.get_bottom()[1] - 0.4 - (BOTTOM_Y + 0.6))
        q.group.next_to(chat, DOWN, buff=0.4).to_edge(LEFT, buff=SAFE + 0.6)
        predict = pill("the fable:  the risky job everyone needs, nobody wants", STEP_COLS["PREDICT"], size=SMALL)
        fit_width(predict, self.pinned.get_left()[0] - 0.3 - (q.word.get_right()[0] + 0.3))
        predict.next_to(q.word, RIGHT, buff=0.3)
        fixed = self.crisis_card(fill="take on the risky task")
        self.no_overlap(chat, q.group)
        self.no_overlap(chat, self.pinned)
        self.no_overlap(q.rows, predict)
        self.no_overlap(predict, self.pinned)
        self.validator.check_in_frame(VGroup(chat, q.group, predict))

        n = self.narrate(
            id="solved_01",
            text="Let's solve the hook. Read: bell the cat, in a crisis where someone must deliver bad news. Predict, from "
                 "the fable: take on the risky job everyone needs, but nobody wants.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(chat), FadeIn(q.word), FadeIn(q.rows))
        self.at_word(n, "Read")
        self.play(Indicate(q.word, color=WORD, scale_factor=1.08))
        self.at_word(n, "Predict")
        self.play(self.pin_step(0, color=RATIO))
        self.at_word(n, "risky")
        self.play(FadeIn(predict, shift=LEFT * 0.1), self.pin_step(1, color=STEP_COLS["PREDICT"]))
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_02",
            text="Eliminate. Set an alarm is literal. Spread the news misses the risk. Avoid responsibility is the "
                 "opposite.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Eliminate")
        self.play(self.pin_step(2, color=BAD))
        for letter, spoken in [("a", "alarm"), ("b", "Spread"), ("c", "Avoid")]:
            self.at_word(n, spoken)
            self.play(*q.strike(letter)[1])
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_03",
            text="Confirm: someone has to take on the risky task of telling the director. That's the answer.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Confirm")
        self.play(ReplacementTransform(chat, fixed), self.pin_step(3, color=GOOD))
        self.at_word(n, "answer")
        self.play(*q.confirm()[1])
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S11_hook_solved")

    # ========================================== 12. EXAM PATTERNS ==========

    def exam_patterns(self):
        self.scene_start("S12_patterns", title="Exam Patterns and Solving Models")
        self.play(self.unpin())

        table = self.table_rows(["Pattern", "Solving model"], [
            ["Meaning of a literary idiom", "origin story → meaning → strike literal"],
            ["Two close options", "check the key feature (risk, fake, surprise, selfish)"],
        ], [4.8, 7.0], size=LABEL)
        board = self.card(table, width=SAFE_W - 0.2).move_to(UP * 0.4)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="patterns_01",
            text="Two exam patterns. Meaning of a literary idiom: origin story, then meaning, then strike the literal "
                 "option. And two close options: check the key feature: risk, fake, surprise, selfish.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(board[0]), FadeIn(table[0]))
        for row, spoken in zip(table[1:], ["Meaning", "close"]):
            self.at_word(n, spoken, occurrence=1)
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.45)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S12_patterns")

    # ======================================== 13. COMMON MISTAKES ==========

    def common_mistakes(self):
        self.scene_start("S13_mistakes", title="Common Mistakes")

        card_w = ZONE_W - 0.3
        pairs = [
            (self.verdict_card(False, "The literal option for an unfamiliar idiom", card_w),
             self.verdict_card(True, "Origin story → meaning", card_w)),
            (self.verdict_card(False, "Missing the key feature", card_w),
             self.verdict_card(True, "crocodile tears: FAKE, not just sad", card_w)),
            (self.verdict_card(False, "dark horse = black sheep", card_w),
             self.verdict_card(True, "black sheep: a disgrace to the family", card_w)),
        ]
        for (wrong, right), yy in zip(pairs, [1.6, 0.05, -1.5]):
            wrong.move_to(LEFT_ZONE + UP * yy)
            right.move_to(RIGHT_ZONE + UP * yy)
        header = pill("3 mistakes", BAD, size=LABEL).move_to(UP * (CARD_TOP - 0.3))
        self.validator.check_in_frame(VGroup(header, *[c for p in pairs for c in p]))

        n = self.narrate(
            id="mistakes_01",
            text="Three common mistakes. The first is choosing the literal option for unfamiliar idioms. The second is "
                 "missing the key feature: crocodile tears are fake, not just sad. The third is confusing a dark horse "
                 "with a black sheep, which means a disgrace to the family.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(header))
        for pr, spoken in zip(pairs, ["first", "second", "third"]):
            self.at_word(n, spoken)
            self.play(FadeIn(pr[0], shift=RIGHT * 0.3), FadeIn(pr[1], shift=LEFT * 0.3))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S13_mistakes")

    # ============================================== 14. PRACTICE ==========

    PRACTICE = [
        ("to smell a rat", ["find a pest", "be dirty", "suspect something is wrong", "be afraid"], "c",
         {"a": "literal", "b": "not the idea", "d": "not the idea"}),
        ("a bolt from the blue", ["lightning", "a complete surprise", "a quick decision", "bad weather"], "b",
         {"a": "literal", "c": "not the idea", "d": "literal"}),
        ("to have an axe to grind", ["to have a selfish motive", "to be a carpenter", "to be angry", "to work hard"], "a",
         {"b": "literal", "c": "nearby", "d": "not the idea"}),
    ]

    def practice(self):
        self.scene_start("S14_practice", title="Practice Questions")

        head = pill("Choose the MEANING of the idiom", SECOND, size=LABEL)
        lines = VGroup(*[VGroup(VGroup(pill(str(i + 1), FOCUS, size=SMALL), pill(f"“{idiom}”", WORD, size=LABEL))
                                .arrange(RIGHT, buff=0.35),
                                text("   ".join(f"({l}) {o}" for l, o in zip("abcd", opts)), LABEL, INK))
                         .arrange(DOWN, buff=0.2, aligned_edge=LEFT)
                         for i, (idiom, opts, *_r) in enumerate(self.PRACTICE)])
        lines.arrange(DOWN, buff=0.4, aligned_edge=LEFT)
        board = self.card(VGroup(head, lines).arrange(DOWN, buff=0.4, aligned_edge=LEFT), color=FOCUS)
        fit_within(board, SAFE_W, SAFE_H - 1.2)
        board.move_to(UP * 0.4)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="practice_01",
            text="Your turn. One: to smell a rat. Find a pest, be dirty, suspect something is wrong, or be afraid? Two: a "
                 "bolt from the blue. Lightning, a complete surprise, a quick decision, or bad weather? Three: to have an "
                 "axe to grind. To have a selfish motive, to be a carpenter, to be angry, or to work hard?",
            voice="default",
            subtitle=True,
            pause_after=10.0,
        )
        self.play(FadeIn(board[0]), FadeIn(head))
        for ln, (spoken, first_option) in zip(lines, [("smell", "Find"), ("bolt", "Lightning"), ("axe", "selfish")]):
            self.at_word(n, spoken)
            self.play(FadeIn(ln[0], shift=UP * 0.15), run_time=0.4)
            self.at_word(n, first_option)
            self.play(FadeIn(ln[1], shift=LEFT * 0.15), run_time=0.4)
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        self.clear_stage()
        self.scene_end("S14_practice")

    # =============================================== 15. ANSWERS ==========

    def answers(self):
        self.scene_start("S15_answers", title="Answers")

        rows = VGroup()
        for idiom, opts, key, traps in self.PRACTICE:
            OptionQuestion(idiom, opts, key, traps)            # validates key / traps
            assert opts["abcd".index(key)] in EXAM_IDIOMS[idiom]
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
            text="One: suspect something is wrong. Find a pest is literal. Two: a complete surprise. Lightning and bad "
                 "weather are literal. Three: to have a selfish motive. To be a carpenter is literal, and to be angry is "
                 "only nearby.",
            voice="default",
            subtitle=True,
        )
        for r, (spoken, trap) in zip(rows, [("suspect", "pest"), ("surprise", "weather"), ("selfish", "carpenter")]):
            self.at_word(n, spoken)
            self.play(FadeIn(r[0], shift=RIGHT * 0.2), run_time=0.5)
            self.at_word(n, trap)
            self.play(FadeIn(r[1], shift=LEFT * 0.1), run_time=0.4)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S15_answers")

    # ================================================ 16. RECAP ==========

    def recap(self):
        self.scene_start("S16_recap", title="Recap Card")

        card, table = self.recap_card("Recap Card: Video 6", [
            ["Old idioms", "learn with a one-line origin story"],
            ["Key features", "crocodile tears = fake;  dark horse = unknown but capable;  axe to grind = selfish motive"],
            ["Watch", "dark horse ≠ black sheep"],
        ])
        card.move_to(UP * 0.2)
        self.validator.check_in_frame(card)

        n = self.narrate(
            id="recap_01",
            text="To recap. Learn old idioms with a one-line origin story. Know the key features: crocodile tears are fake, "
                 "a dark horse is unknown but capable, and an axe to grind is a selfish motive. And watch out: a dark "
                 "horse is not a black sheep.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(card[0]), FadeIn(table[0]))
        for row, spoken in zip(table[1:], ["origin", "features", "watch"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.45)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S16_recap")

    # ================================================= 17. NEXT ==========

    def next_video(self):
        self.scene_start("S17_next", title="Next")

        method = pill("everything  →  one fast method for idiom questions", GOOD, size=LABEL)
        nxt = pill("Next:  Idiom-Based Question-Solving Techniques", FOCUS, size=LABEL)
        VGroup(method, nxt).arrange(DOWN, buff=0.8).move_to(UP * 0.2)
        self.no_overlap(method, nxt)
        self.validator.check_in_frame(VGroup(method, nxt))

        n = self.narrate(
            id="next_01",
            text="Video seven puts everything into one fast method for idiom questions.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Video")
        self.play(FadeIn(nxt, scale=1.05))
        self.at_word(n, "method")
        self.play(FadeIn(method, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S17_next")

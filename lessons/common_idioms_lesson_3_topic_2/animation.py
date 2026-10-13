"""
animation.py for the LMS video generator.

Course : C-CAT - Section A - English
Module : Module 1 - Vocabulary
Lesson : Lesson 3 - Idioms & Phrases
Video  : 02 - Common Idioms (Video 2 of 7)

Source script:
  C:\\Users\\User\\Downloads\\C-CAT_SectionA_Module1_English\\English\\Module 1 - Vocabulary\\
  Lesson 3 - Idioms & Phrases\\02 - Common Idioms.pdf

Built on the golden-reference pattern:
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``;
  * layouts stacked with next_to and guarded with ``no_overlap``; nothing is
    ever animated onto or into another box.

The eight situation groups live in GROUPS (idiom, meaning); group_of(idiom) looks up an idiom's group and the rules tables, worked examples and answers are built from it.
The "group method" card (group, meaning + tone, strike other groups and literal options, confirm) stays pinned top-right through the worked examples and Hook, Solved.
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

# Situation groups from the script's Rules table: group -> [(idiom, meaning)].
GROUPS = {
    "Effort": [("burn the midnight oil", "work late"), ("go the extra mile", "do more"),
               ("cut corners", "do it cheaply or carelessly")],
    "Difficulty": [("in hot water", "in trouble"), ("a hard nut to crack", "a difficult problem or person"),
                   ("between the devil and the deep sea", "two bad choices")],
    "Ease": [("a piece of cake", "very easy"), ("plain sailing", "smooth progress")],
    "Time": [("at the eleventh hour", "last moment"), ("in the nick of time", "just in time"),
             ("once in a blue moon", "rarely")],
    "Money": [("cost an arm and a leg", "very expensive"), ("a white elephant", "costly and useless"),
              ("make ends meet", "just manage financially")],
    "Speaking": [("beat about the bush", "avoid the point"), ("spill the beans", "reveal a secret"),
                 ("hit the nail on the head", "be exactly right")],
    "Relationships": [("see eye to eye", "agree"), ("bury the hatchet", "make peace"),
                      ("get on like a house on fire", "get along very well")],
    "Decisions": [("sit on the fence", "not take sides"), ("bite the bullet", "do something unpleasant bravely")],
}
GROUP_COL = dict(zip(GROUPS, [BAD, RATIO, GOOD, WORD, FOCUS, SECOND, "#F48FB1", "#80CBC4"]))


def group_of(idiom):
    for g, items in GROUPS.items():
        if idiom in [i for i, _ in items]:
            return g
    raise KeyError(idiom)


class CommonIdiomsVideo(LMSScene):
    lesson_title = "Common Idioms"

    def construct(self):
        self.camera.background_color = BG

        self.lesson_intro()
        self.hook()
        self.concept()
        self.why_you_need_it()
        self.analogy()
        self.example_mile()
        self.example_water()
        self.example_hour()
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

    def group_pin(self):
        return self.steps_pin("group method", [("find the idiom's GROUP", WORD),
                                               ("recall meaning + TONE", STEP_COLS["PREDICT"]),
                                               ("strike other groups, literal", BAD),
                                               ("confirm in the sentence", GOOD)])

    def sticky(self, fill=None):
        head = text("SPRINT RETROSPECTIVE  ·  sticky note", SMALL, RATIO, BOLD)
        line = text(f"“We {fill} on testing.”" if fill else "“We cut corners on testing to hit the deadline.”", BODY,
                    INK, t2c={fill or "cut corners": GOOD if fill else WORD})
        cx, w = self.free_area()
        card = self.card(VGroup(head, fit_width(line, w - 1.4)).arrange(DOWN, buff=0.2, aligned_edge=LEFT),
                         width=min(w - 0.2, SAFE_W - 0.4))
        return card.move_to(RIGHT * cx + UP * (CARD_TOP - card.height / 2))

    def group_example(self, idiom, meaning):
        """The idiom inside its situation group, with its meaning, beside the pinned panel."""
        g = group_of(idiom)
        head = pill(g + " group", GROUP_COL[g], size=LABEL)
        chips = VGroup(*[pill(f"“{i}”", WORD if i == idiom else MUTED, size=LABEL) for i, _ in GROUPS[g]])
        chips.arrange(DOWN, buff=0.2, aligned_edge=LEFT)
        mean = pill("=  " + meaning, GOOD, size=BODY)
        block = VGroup(head, chips, mean).arrange(DOWN, buff=0.45)
        fit_height(block, SAFE_H - 1.6)
        self.place_free(block, y=0.1)
        self.no_overlap(head, chips, mean)
        self.validator.check_in_frame(block)
        k = [i for i, _ in GROUPS[g]].index(idiom)
        return head, chips[k], VGroup(*[c for j, c in enumerate(chips) if j != k]), mean

    def group_board(self, names):
        table = self.table_rows(["Group", "Idioms and meanings"], [
            [g, "   ·   ".join(f"{i} ({m})" for i, m in GROUPS[g])] for g in names], [2.6, 9.4], size=SMALL)
        for row, g in zip(table[1:], names):
            row[0].set_color(GROUP_COL[g])
        board = self.card(table, width=SAFE_W - 0.2)
        fit_height(board, SAFE_H - 1.2)
        board.move_to(UP * 0.3)
        self.validator.check_in_frame(board)
        return board, table

    # ========================================= 0. LESSON INTRO ==========

    def lesson_intro(self):
        self.scene_start("S00_intro", title="Lesson Introduction")

        crumb = self.breadcrumb("English · Module 1 Vocabulary", "Lesson 3 · Idioms & Phrases", "Video 2")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        chain = VGroup(pill("PICTURE", WORD, size=LABEL), text("→", LABEL, MUTED), pill("IDEA", GOOD, size=LABEL))\
            .arrange(RIGHT, buff=0.3)
        store = VGroup(*[pill(g, GROUP_COL[g], size=SMALL) for g in GROUPS]).arrange(RIGHT, buff=0.2)
        fit_width(store, SAFE_W)
        recall = pill("organised by situation  →  easy to recall under pressure", FOCUS, size=LABEL)
        VGroup(chain, store, recall).arrange(DOWN, buff=0.6).move_to(DOWN * 0.1)
        self.no_overlap(crumb, chain, store, recall)
        self.validator.check_in_frame(VGroup(crumb, chain, store, recall))

        n = self.narrate(
            id="intro_01",
            text="In video one, you learned the picture-to-idea method. Today you build the store of idioms to apply it "
                 "to, organised by situation, so you can recall them under pressure.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.at_word(n, "method")
        self.play(FadeIn(chain, shift=UP * 0.1))
        self.at_word(n, "store")
        self.play(LaggedStart(*[FadeIn(s_, shift=UP * 0.1) for s_ in store], lag_ratio=0.12))
        self.at_word(n, "recall")
        self.play(FadeIn(recall, shift=UP * 0.1))
        self.wait_for_narration(n)

        title = fitted_text("Common Idioms", SAFE_W, 72, INK, BOLD)
        underline = Line(LEFT, RIGHT, color=SECOND, stroke_width=5).set_width(title.width * 0.6)
        VGroup(title, underline).arrange(DOWN, buff=0.2).move_to(UP * 0.2)
        goals = [("Learn high-frequency idioms in situation groups", SECOND),
                 ("Recall the meaning of an idiom from its group", GOOD)]
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
            text="These are the common idioms. By the end of this video, you'll learn high-frequency idioms in situation "
                 "groups, and recall the meaning of an idiom from its group.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(VGroup(chain, store, recall), shift=UP * 0.3))
        self.at_word(n, "common")
        self.play(Write(title), run_time=1.1)
        self.play(GrowFromCenter(underline))
        self.at_word(n, "By")
        self.play(FadeOut(underline), ReplacementTransform(title, small_title), run_time=0.8)
        self.play(FadeIn(objectives[0]), FadeIn(heading))
        for row_, spoken in zip(rows, ["learn", "recall"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row_, shift=RIGHT * 0.2), run_time=0.5)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_intro")

    # ================================================= 1. HOOK ==========

    HOOK = dict(word="cut corners", options=["We tested only the edge cases", "We saved money on equipment",
                                             "We did the job quickly but carelessly", "We finished early and well"],
                key="c", traps={"a": "literal: corners", "b": "wrong group: money", "d": "tone reversed"})

    def hook(self):
        self.scene_start("S01_hook", title="Hook")

        h = self.HOOK
        assert group_of(h["word"]) == "Effort"
        note = self.sticky()
        q = OptionQuestion(h["word"], h["options"], h["key"], h["traps"])
        opts = q.rows.copy().arrange_in_grid(rows=2, cols=2, buff=(1.0, 0.35), cell_alignment=LEFT)
        fit_width(opts, SAFE_W)
        ask = pill("your manager: “Is that good news or bad news?”", FOCUS, size=LABEL)
        ask.next_to(note, DOWN, buff=0.5)
        opts.next_to(ask, DOWN, buff=0.5)
        self.no_overlap(note, ask, opts)
        self.validator.check_in_frame(VGroup(note, ask, opts))

        n = self.narrate(
            id="hook_01",
            text="In a sprint retrospective, a sticky note says: We cut corners on testing to hit the deadline. Your "
                 "manager asks whether that's good news or bad news.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "sticky")
        self.play(FadeIn(note, shift=DOWN * 0.2))
        self.at_word(n, "manager")
        self.play(FadeIn(ask, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_02",
            text="What does it mean? We tested only the edge cases, we saved money on equipment, we did the job quickly "
                 "but carelessly, or we finished early and well?",
            voice="default",
            subtitle=True,
            pause_after=3.0,
        )
        self.at_word(n, "mean")
        self.play(Indicate(note[1][1], color=WORD, scale_factor=1.03))
        for row, spoken in zip(opts, ["tested", "saved", "did", "finished"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=UP * 0.15), run_time=0.35)
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        self.clear_stage()
        self.scene_end("S01_hook")

    # ============================================== 2. CONCEPT ==========

    def concept(self):
        self.scene_start("S02_concept", title="The Concept")

        head = pill("like vocabulary shelves:  idioms in SITUATION GROUPS", SECOND, size=LABEL)
        fit_width(head, SAFE_W)
        head.move_to(UP * (CARD_TOP - head.height / 2))
        spoken_groups = ["Effort", "Difficulty", "Time", "Money", "Speaking", "Relationships", "Decisions"]
        groups = VGroup(*[pill(g, GROUP_COL[g], size=BODY) for g in spoken_groups])
        groups.arrange_in_grid(rows=2, cols=4, buff=(0.5, 0.5))
        fit_width(groups, SAFE_W - 0.6)
        groups.next_to(head, DOWN, buff=0.9)
        self.no_overlap(head, groups)
        self.validator.check_in_frame(VGroup(head, groups))

        n = self.narrate(
            id="concept_01",
            text="Like the vocabulary shelves in lesson one, idioms are easier to remember in situation groups: effort, "
                 "difficulty, time, money, speaking, relationships and decisions.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "shelves")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        for g, spoken in zip(groups, ["effort", "difficulty", "time", "money", "speaking", "relationships",
                                      "decisions"]):
            self.at_word(n, spoken)
            self.play(FadeIn(g, shift=UP * 0.1), run_time=0.3)
        self.wait_for_narration(n)

        # A pair of opposites inside one group.
        tag = pill("Effort group", GROUP_COL["Effort"], size=LABEL)
        pair = VGroup(VGroup(pill("“go the extra mile”", GOOD, size=LABEL), text("more effort", SMALL, GOOD))
                      .arrange(DOWN, buff=0.15), text("↔", TITLE, MUTED),
                      VGroup(pill("“cut corners”", BAD, size=LABEL), text("less effort, lower quality", SMALL, BAD))
                      .arrange(DOWN, buff=0.15)).arrange(RIGHT, buff=0.5)
        two = pill("learn them together:  one recall  →  two answers", FOCUS, size=LABEL)
        block = VGroup(tag, pair, two).arrange(DOWN, buff=0.6)
        fit_width(block, SAFE_W).move_to(UP * 0.3)
        self.validator.check_in_frame(block)
        n = self.narrate(
            id="concept_02",
            text="Each group usually contains a pair of opposites, like go the extra mile, more effort, and cut corners, "
                 "less effort and lower quality. Learning them together means one recall gives you two answers.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(VGroup(head, groups)))
        self.at_word(n, "pair")
        self.play(FadeIn(tag, shift=DOWN * 0.1))
        self.at_word(n, "extra")
        self.play(FadeIn(pair[0], shift=RIGHT * 0.2))
        self.at_word(n, "cut")
        self.play(FadeIn(pair[1]), FadeIn(pair[2], shift=LEFT * 0.2))
        self.at_word(n, "recall")
        self.play(FadeIn(two, shift=UP * 0.1))
        self.wait_for_narration(n)

        # Tone.
        tone_head = pill("watch the TONE as well as the meaning", RATIO, size=LABEL)
        cols = VGroup(VGroup(text("criticises", LABEL, BAD, BOLD), pill("“cut corners”", BAD, size=LABEL),
                             pill("“beat about the bush”", BAD, size=LABEL)).arrange(DOWN, buff=0.3),
                      VGroup(text("praises", LABEL, GOOD, BOLD), pill("“work smart”", GOOD, size=LABEL),
                             pill("“get to the point”", GOOD, size=LABEL)).arrange(DOWN, buff=0.3))\
            .arrange(RIGHT, buff=1.2, aligned_edge=UP)
        exams = pill("exams sometimes test the tone, not only the meaning", FOCUS, size=SMALL)
        tone_block = VGroup(tone_head, cols, exams).arrange(DOWN, buff=0.5)
        fit_width(tone_block, SAFE_W).move_to(UP * 0.3)
        self.validator.check_in_frame(tone_block)
        n = self.narrate(
            id="concept_03",
            text="Pay attention to tone as well as meaning. Cut corners is critical; work smart is positive. Beat about "
                 "the bush is a complaint; get to the point is praise. Exams sometimes test the tone, not only the "
                 "meaning.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(block))
        self.at_word(n, "tone", occurrence=1)
        self.play(FadeIn(tone_head, shift=DOWN * 0.1))
        self.at_word(n, "Cut")
        self.play(FadeIn(cols[0][0]), FadeIn(cols[0][1], shift=UP * 0.1))
        self.at_word(n, "smart")
        self.play(FadeIn(cols[1][0]), FadeIn(cols[1][1], shift=UP * 0.1))
        self.at_word(n, "Beat")
        self.play(FadeIn(cols[0][2], shift=UP * 0.1))
        self.at_word(n, "point")
        self.play(FadeIn(cols[1][2], shift=UP * 0.1))
        self.at_word(n, "Exams")
        self.play(FadeIn(exams, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_concept")

    # ======================================== 3. WHY YOU NEED IT ==========

    def why_you_need_it(self):
        self.scene_start("S03_why", title="Why You Need It")

        pool = pill("most idiom questions come from a fairly stable pool", BAD, size=LABEL)
        fast = pill("known by group  →  a 20-second question", GOOD, size=BODY)
        VGroup(pool, fast).arrange(DOWN, buff=0.9).move_to(UP * 0.3)
        self.no_overlap(pool, fast)
        self.validator.check_in_frame(VGroup(pool, fast))

        n = self.narrate(
            id="why_01",
            text="Most idiom questions come from a fairly stable pool. Knowing the high-frequency ones by group turns "
                 "these into twenty-second questions.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "stable")
        self.play(FadeIn(pool, shift=DOWN * 0.1))
        self.at_word(n, "group")
        self.play(FadeIn(fast, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_why")

    # ============================================== 4. ANALOGY ==========

    def analogy(self):
        self.scene_start("S04_analogy", title="The Analogy")

        long = self.card(VGroup(text("one long list", SMALL, BAD, BOLD),
                                *[text(nm, SMALL, INK) for nm in ["Asha", "Manager", "Dad", "Riya (college)",
                                                                  "Team lead", "Mum"]])
                         .arrange(DOWN, buff=0.14, aligned_edge=LEFT), width=3.6)
        grouped = self.card(VGroup(text("groups", SMALL, GOOD, BOLD),
                                   *[pill(g, c, size=SMALL) for g, c in [("Family", WORD), ("Work", RATIO),
                                                                         ("College", SECOND)]])
                            .arrange(DOWN, buff=0.22, aligned_edge=LEFT), width=3.6)
        top = VGroup(long, text("→", TITLE, MUTED), grouped).arrange(RIGHT, buff=0.7)
        same = VGroup(*[pill(g, GROUP_COL[g], size=SMALL) for g in ["Effort", "Time", "Money"]],
                      text("…", LABEL, MUTED)).arrange(RIGHT, buff=0.3)
        check = pill("meet an idiom:  group first  →  then the meaning", FOCUS, size=LABEL)
        block = VGroup(top, same, check).arrange(DOWN, buff=0.45)
        fit_within(block, SAFE_W, SAFE_H - 1.4)
        block.move_to(UP * 0.3)
        self.no_overlap(top, same, check)
        self.validator.check_in_frame(block)

        n = self.narrate(
            id="analogy_01",
            text="You don't store contacts in one long list; you group them. Store idioms the same way. When you meet one, "
                 "you check its group first, then the meaning.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "contacts")
        self.play(FadeIn(long, shift=RIGHT * 0.2))
        self.at_word(n, "group", occurrence=1)
        self.play(FadeIn(top[1]), FadeIn(grouped, shift=LEFT * 0.2))
        self.at_word(n, "idioms")
        self.play(LaggedStart(*[FadeIn(s_, shift=UP * 0.1) for s_ in same], lag_ratio=0.2))
        self.at_word(n, "check")
        self.play(FadeIn(check, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_analogy")

    # ======================================== 5-7. WORKED EXAMPLES ==========

    def example_mile(self):
        self.scene_start("S05_ex_mile", title="Worked Example 1")
        self.play(self.pin(self.group_pin()))

        parts = self.group_example("go the extra mile", "do more than expected")
        n = self.narrate(
            id="ex1_01",
            text="Go the extra mile. It sits in the effort group. The meaning: do more than expected.",
            voice="default",
            subtitle=True,
        )
        head, target, others, mean = parts
        self.at_word(n, "Go", occurrence=1)
        self.play(FadeIn(target, scale=1.1))
        self.at_word(n, "effort")
        self.play(FadeIn(head, shift=DOWN * 0.1), FadeIn(others, shift=UP * 0.1), self.pin_step(0, color=WORD))
        self.at_word(n, "meaning")
        self.play(FadeIn(mean, shift=UP * 0.1), self.pin_step(1, color=STEP_COLS["PREDICT"]))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_ex_mile")

    def example_water(self):
        self.scene_start("S06_ex_water", title="Worked Example 2")

        parts = self.group_example("in hot water", "in trouble")
        n = self.narrate(
            id="ex2_01",
            text="In hot water. It sits in the difficulty group. The meaning: in trouble.",
            voice="default",
            subtitle=True,
        )
        head, target, others, mean = parts
        self.at_word(n, "In", occurrence=1)
        self.play(FadeIn(target, scale=1.1))
        self.at_word(n, "difficulty")
        self.play(FadeIn(head, shift=DOWN * 0.1), FadeIn(others, shift=UP * 0.1), self.pin_step(0, color=WORD))
        self.at_word(n, "meaning")
        self.play(FadeIn(mean, shift=UP * 0.1), self.pin_step(1, color=STEP_COLS["PREDICT"]))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_ex_water")

    def example_hour(self):
        self.scene_start("S07_ex_hour", title="Worked Example 3")

        parts = self.group_example("at the eleventh hour", "at the last possible moment")
        n = self.narrate(
            id="ex3_01",
            text="At the eleventh hour. It sits in the time group. The meaning: at the last possible moment.",
            voice="default",
            subtitle=True,
        )
        head, target, others, mean = parts
        self.at_word(n, "At", occurrence=1)
        self.play(FadeIn(target, scale=1.1))
        self.at_word(n, "time")
        self.play(FadeIn(head, shift=DOWN * 0.1), FadeIn(others, shift=UP * 0.1), self.pin_step(0, color=WORD))
        self.at_word(n, "meaning")
        self.play(FadeIn(mean, shift=UP * 0.1), self.pin_step(1, color=STEP_COLS["PREDICT"]))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S07_ex_hour")

    # ================================================ 8. RULES ==========

    def rules_first(self):
        self.scene_start("S08_rules_first", title="Rules: Idiom Groups (1)")
        self.play(self.unpin())

        names = ["Effort", "Difficulty", "Ease", "Time"]
        board, table = self.group_board(names)

        n = self.narrate(
            id="rules_01",
            text="Here are the groups. Effort: burn the midnight oil, go the extra mile, cut corners. Difficulty: in hot "
                 "water, a hard nut to crack, between the devil and the deep sea. Ease: a piece of cake, plain sailing. "
                 "Time: at the eleventh hour, in the nick of time, once in a blue moon.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "groups")
        self.play(FadeIn(board[0]), FadeIn(table[0]))
        for row, spoken in zip(table[1:], ["Effort", "Difficulty", "Ease", "Time"]):
            self.at_word(n, spoken, occurrence=1)
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.45)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S08_rules_first")

    def rules_second(self):
        self.scene_start("S09_rules_second", title="Rules: Idiom Groups (2)")

        names = ["Money", "Speaking", "Relationships", "Decisions"]
        board, table = self.group_board(names)

        n = self.narrate(
            id="rules_02",
            text="Money: cost an arm and a leg, a white elephant, make ends meet. Speaking: beat about the bush, spill the "
                 "beans, hit the nail on the head. Relationships: see eye to eye, bury the hatchet, get on like a house "
                 "on fire. Decisions: sit on the fence, bite the bullet.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(board[0]), FadeIn(table[0]))
        for row, spoken in zip(table[1:], ["Money", "Speaking", "Relationships", "Decisions"]):
            self.at_word(n, spoken, occurrence=1)
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.45)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S09_rules_second")

    # ============================================= 10. PROCESS ==========

    def process(self):
        self.scene_start("S10_process", title="The Process")

        steps = VGroup(*[VGroup(pill(str(i + 1), c, size=SMALL), fitted_text(s_, SAFE_W - 2.2, BODY, INK))
                         .arrange(RIGHT, buff=0.3) for i, (s_, c) in enumerate([
                             ("Identify the idiom's group", WORD),
                             ("Recall its meaning and tone", STEP_COLS["PREDICT"]),
                             ("Eliminate options from other groups, and literal options", BAD),
                             ("Confirm in the sentence", GOOD)])])
        steps.arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        board = self.card(steps).move_to(UP * 0.3)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="process_01",
            text="The process. First, identify the idiom's group. Second, recall its meaning and tone. Third, eliminate "
                 "options from other groups, and literal options. And fourth, confirm in the sentence.",
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
        self.play(self.pin(self.group_pin()))

        h = self.HOOK
        note = self.sticky()
        q = OptionQuestion(h["word"], h["options"], h["key"], h["traps"], word_size=LABEL)
        fit_height(q.group, note.get_bottom()[1] - 0.4 - (BOTTOM_Y + 0.6))
        q.group.next_to(note, DOWN, buff=0.4).to_edge(LEFT, buff=SAFE + 0.6)
        predict = VGroup(pill("Effort group: the critical one", GROUP_COL["Effort"], size=SMALL),
                         pill("too quick, skipping steps", STEP_COLS["PREDICT"], size=SMALL)).arrange(RIGHT, buff=0.2)
        fit_width(predict, self.pinned.get_left()[0] - 0.3 - (q.word.get_right()[0] + 0.3))
        predict.next_to(q.word, RIGHT, buff=0.3)
        fixed = self.sticky(fill="did the job quickly but carelessly")
        verdict = pill("bad news: expect bugs", BAD, size=SMALL)

        # Keep the verdict in the free column between the question and the
        # pinned reference card.  The previous layout positioned it beside
        # only the correct answer row, but no_overlap() checks the bounding
        # box of the complete q.group, so another answer row could collide
        # with the verdict.
        free_verdict_width = self.pinned.get_left()[0] - q.group.get_right()[0] - 0.7
        fit_width(verdict, free_verdict_width)
        verdict.next_to(q.group, RIGHT, buff=0.35)
        verdict.align_to(q.rows, DOWN)

        self.no_overlap(note, q.group)
        self.no_overlap(note, self.pinned)
        self.no_overlap(q.rows, predict)
        self.no_overlap(predict, self.pinned)
        self.no_overlap(q.group, verdict)
        self.no_overlap(predict, verdict)
        self.no_overlap(verdict, self.pinned)
        self.validator.check_in_frame(VGroup(note, q.group, predict, verdict))

        n = self.narrate(
            id="solved_01",
            text="Let's solve the hook. Read: cut corners on testing. Predict: the effort group, the critical one. They "
                 "did it too quickly, skipping steps.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(note), FadeIn(q.word), FadeIn(q.rows))
        self.at_word(n, "Read")
        self.play(Indicate(note[1][1], color=WORD, scale_factor=1.03))
        self.at_word(n, "Predict")
        self.play(FadeIn(predict[0], shift=LEFT * 0.1), self.pin_step(0, color=WORD))
        self.at_word(n, "quickly")
        self.play(FadeIn(predict[1], shift=LEFT * 0.1), self.pin_step(1, color=STEP_COLS["PREDICT"]))
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_02",
            text="Eliminate. Tested only the edge cases is a literal reading of corners. Saved money on equipment makes it "
                 "about money. Finished early and well reverses the tone.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Eliminate")
        self.play(self.pin_step(2, color=BAD))
        for letter, spoken in [("a", "Tested"), ("b", "Saved"), ("d", "Finished")]:
            self.at_word(n, spoken)
            self.play(*q.strike(letter)[1])
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_03",
            text="Confirm: we did the job quickly but carelessly on testing. That's the answer. Bad news: expect bugs.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Confirm")
        self.play(ReplacementTransform(note, fixed), self.pin_step(3, color=GOOD))
        self.at_word(n, "answer")
        self.play(*q.confirm()[1])
        self.at_word(n, "Bad")
        self.play(FadeIn(verdict, shift=LEFT * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S11_hook_solved")

    # ========================================== 12. EXAM PATTERNS ==========

    def exam_patterns(self):
        self.scene_start("S12_patterns", title="Exam Patterns and Solving Models")
        self.play(self.unpin())

        table = self.table_rows(["Pattern", "Solving model"], [
            ["Meaning of a common idiom", "group → meaning → strike literal and wrong-tone options"],
            ["Two options with the right meaning", "check the tone: critical or positive"],
        ], [5.0, 6.8], size=LABEL)
        board = self.card(table, width=SAFE_W - 0.2).move_to(UP * 0.4)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="patterns_01",
            text="Two exam patterns. Meaning of a common idiom: group, then meaning, then strike literal and wrong-tone "
                 "options. And two options with the right meaning: check the tone, critical or positive.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(board[0]), FadeIn(table[0]))
        for row, spoken in zip(table[1:], ["Meaning", "right"]):
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
            (self.verdict_card(False, "Mixing up opposites: extra mile / cut corners", card_w),
             self.verdict_card(True, "Learn the pair with its direction", card_w)),
            (self.verdict_card(False, "Ignoring tone", card_w),
             self.verdict_card(True, "Praise or criticism?", card_w)),
            (self.verdict_card(False, "nick of time = eleventh hour", card_w),
             self.verdict_card(True, "nick of time: just in time, with success", card_w)),
        ]
        for (wrong, right), yy in zip(pairs, [1.6, 0.05, -1.5]):
            wrong.move_to(LEFT_ZONE + UP * yy)
            right.move_to(RIGHT_ZONE + UP * yy)
        header = pill("3 mistakes", BAD, size=LABEL).move_to(UP * (CARD_TOP - 0.3))
        self.validator.check_in_frame(VGroup(header, *[c for p in pairs for c in p]))

        n = self.narrate(
            id="mistakes_01",
            text="Three common mistakes. The first is mixing up opposites inside a group, like the extra mile and cut "
                 "corners. The second is ignoring tone. The third is confusing in the nick of time with at the eleventh "
                 "hour. Both are late, but the nick of time means just in time, with success.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(header))
        self.at_word(n, "first")
        self.play(FadeIn(pairs[0][0], shift=RIGHT * 0.3), FadeIn(pairs[0][1], shift=LEFT * 0.3))
        self.at_word(n, "second")
        self.play(FadeIn(pairs[1][0], shift=RIGHT * 0.3), FadeIn(pairs[1][1], shift=LEFT * 0.3))
        self.at_word(n, "third")
        self.play(FadeIn(pairs[2][0], shift=RIGHT * 0.3))
        self.at_word(n, "Both")
        self.play(FadeIn(pairs[2][1], shift=LEFT * 0.3))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S13_mistakes")

    # ============================================== 14. PRACTICE ==========

    PRACTICE = [
        ("sit on the fence", ["relax", "avoid choosing a side", "guard property", "wait for someone"], "b",
         {"a": "literal", "c": "literal", "d": "not the idea"}),
        ("a white elephant", ["a costly, useless possession", "a rare animal", "a big success", "a gift"], "a",
         {"b": "literal", "c": "not the idea", "d": "a nearby idea"}),
        ("bite the bullet", ["get hurt", "be angry", "fire a gun", "face something unpleasant bravely"], "d",
         {"a": "literal", "b": "not the idea", "c": "literal"}),
    ]

    def practice(self):
        self.scene_start("S14_practice", title="Practice Questions")

        head = pill("Choose the MEANING of the idiom", SECOND, size=LABEL)
        lines = VGroup(*[VGroup(VGroup(pill(str(i + 1), FOCUS, size=SMALL), pill(f"“{idiom.capitalize()}”", WORD,
                                                                                size=LABEL)).arrange(RIGHT, buff=0.35),
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
            text="Your turn. One: sit on the fence. Relax, avoid choosing a side, guard property, or wait for someone? Two: "
                 "a white elephant. A costly, useless possession, a rare animal, a big success, or a gift? Three: bite "
                 "the bullet. Get hurt, be angry, fire a gun, or face something unpleasant bravely?",
            voice="default",
            subtitle=True,
            pause_after=10.0,
        )
        self.play(FadeIn(board[0]), FadeIn(head))
        for ln, (spoken, first_option) in zip(lines, [("sit", "Relax"), ("white", "costly"), ("bite", "Get")]):
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
            g = group_of(idiom)
            others = [f"({l}) {opts['abcd'.index(l)]}: {r}" for l, r in traps.items() if r != "not the idea"]
            rows.add(VGroup(VGroup(pill(f"“{idiom.capitalize()}”", WORD, size=LABEL), text("=", LABEL, MUTED),
                                   pill(f"({key}) {opts['abcd'.index(key)]}", GOOD, size=LABEL),
                                   pill(g, GROUP_COL[g], size=SMALL)).arrange(RIGHT, buff=0.3),
                            text("   ".join(others), SMALL, BAD)).arrange(DOWN, buff=0.18, aligned_edge=LEFT))
        rows.arrange(DOWN, buff=0.5, aligned_edge=LEFT)
        fit_within(rows, SAFE_W, SAFE_H - 1.2)
        rows.move_to(UP * 0.3)
        self.validator.check_in_frame(rows)

        n = self.narrate(
            id="answers_01",
            text="One: avoid choosing a side. Relax and guard property are literal. Two: a costly, useless possession. A "
                 "rare animal is literal, and a gift is only a nearby idea. Three: face something unpleasant bravely. Get "
                 "hurt and fire a gun are literal.",
            voice="default",
            subtitle=True,
        )
        for r, (spoken, trap) in zip(rows, [("avoid", "guard"), ("costly", "rare"), ("face", "fire")]):
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

        card, table = self.recap_card("Recap Card: Video 2", [
            ["Learn by group", ", ".join(g.lower() for g in GROUPS)],
            ["Opposite pairs", "extra mile ↔ cut corners;  beat about the bush ↔ hit the nail on the head"],
            ["Tone", "some idioms praise, some criticise"],
        ])
        card.move_to(UP * 0.2)
        self.validator.check_in_frame(card)

        n = self.narrate(
            id="recap_01",
            text="To recap. Learn idioms by group: effort, difficulty, ease, time, money, speaking, relationships and "
                 "decisions. Know the opposite pairs: the extra mile against cut corners, and beat about the bush against "
                 "hit the nail on the head. And watch the tone: some idioms praise, some criticise.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(card[0]), FadeIn(table[0]))
        for row, spoken in zip(table[1:], ["group", "pairs", "tone"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.45)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S16_recap")

    # ================================================= 17. NEXT ==========

    def next_video(self):
        self.scene_start("S17_next", title="Next")

        half = pill("knowing meanings: half the job", MUTED, size=LABEL)
        blank = text("“The deadline was close, so the team had to ______.”", LABEL, INK, t2c={"______": FOCUS})
        nxt = pill("Next:  Context-Based Idioms", FOCUS, size=LABEL)
        VGroup(half, blank, nxt).arrange(DOWN, buff=0.7).move_to(UP * 0.2)
        self.no_overlap(half, blank, nxt)
        self.validator.check_in_frame(VGroup(half, blank, nxt))

        n = self.narrate(
            id="next_01",
            text="Knowing meanings is half the job. Video three shows how to choose the idiom that fits a sentence.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "half")
        self.play(FadeIn(half, shift=DOWN * 0.1))
        self.at_word(n, "Video")
        self.play(FadeIn(nxt, scale=1.05))
        self.at_word(n, "fits")
        self.play(FadeIn(blank, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S17_next")

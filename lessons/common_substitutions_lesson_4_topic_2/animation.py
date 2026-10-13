"""
animation.py for the LMS video generator.

Course : C-CAT - Section A - English
Module : Module 1 - Vocabulary
Lesson : Lesson 4 - One-Word Substitution
Video  : 02 - Common Substitutions (Video 2 of 6)

Source script:
  C:\\Users\\User\\Downloads\\C-CAT_SectionA_Module1_English\\English\\Module 1 - Vocabulary\\
  Lesson 4 - One-Word Substitution\\02 - Common Substitutions.pdf

Built on the golden-reference pattern:
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``;
  * layouts stacked with next_to and guarded with ``no_overlap``; nothing is
    ever animated onto or into another box.

The four drawers (People, Places, Actions, States) live in DRAWERS with the script's rows; drawer_of(word) finds a word's drawer, and the rules tables, worked examples and answers are built from it.
The "four drawers" card (each drawer with its typical endings) stays pinned top-right through the worked examples and Hook, Solved; the drawer in use lights up.
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

# The four drawers, with the script's Rules rows: (definition, word).
DRAWERS = {
    "People": [
        ("doctor for children / skin / eyes / bones", "paediatrician / dermatologist / ophthalmologist / orthopaedist"),
        ("lover of mankind / hater of mankind", "philanthropist / misanthrope"),
        ("one who hates women", "misogynist"),
        ("one who knows everything", "omniscient"),
        ("a lover of books", "bibliophile"),
        ("one who eats human flesh", "cannibal"),
    ],
    "Places": [
        ("birds / bees / fish kept", "aviary / apiary / aquarium"),
        ("dead bodies kept", "mortuary"),
        ("arms stored", "armoury, arsenal"),
        ("orphans live", "orphanage"),
    ],
    "Actions": [
        ("killing of a king / mother / father / brother", "regicide / matricide / patricide / fratricide"),
        ("killing oneself", "suicide"),
        ("painless killing to end suffering", "euthanasia"),
    ],
    "States": [
        ("cannot be read / corrected / avoided", "illegible / incorrigible / inevitable"),
        ("cannot be seen / heard", "invisible / inaudible"),
        ("cannot make a mistake", "infallible"),
        ("name not known", "anonymous"),
        ("everyone agrees", "unanimous"),
    ],
}
DRAWER_COL = {"People": WORD, "Actions": BAD, "Places": RATIO, "States": SECOND}
ENDINGS = {"People": "-ist  -er  -ian  -ant", "Actions": "-cide", "Places": "-ary  -arium  -ory",
           "States": "in- / il- / im-  +  -ible / -able"}
PIN_ORDER = ["People", "Actions", "Places", "States"]
PIN_ENDINGS = {"People": "-ist -er -ian", "Actions": "-cide", "Places": "-ary -arium", "States": "in- … -ible"}


def drawer_of(word):
    """The drawer whose Rules table contains this word."""
    for name, rows in DRAWERS.items():
        if any(word in cell.replace(",", " /").split(" / ") or word in cell.split(", ") for _d, cell in rows):
            return name
    raise KeyError(word)


assert [drawer_of(w) for w in ["paediatrician", "aviary", "apiary", "patricide", "incorrigible", "inevitable",
                               "philanthropist"]] == ["People", "Places", "Places", "Actions", "States", "States",
                                                      "People"]


class CommonSubstitutionsVideo(LMSScene):
    lesson_title = "Common Substitutions"

    def construct(self):
        self.camera.background_color = BG

        self.lesson_intro()
        self.hook()
        self.concept()
        self.why_you_need_it()
        self.analogy()
        self.example_aviary()
        self.example_incorrigible()
        self.example_patricide()
        self.rules_people()
        self.rules_places_actions()
        self.rules_states()
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

    def drawer_pin(self):
        return self.steps_pin("four drawers", [(f"{d.upper()}:  {PIN_ENDINGS[d]}", DRAWER_COL[d]) for d in PIN_ORDER])

    def open_drawer(self, name):
        """Animation: light this drawer's row in the pinned panel."""
        return self.pin_step(PIN_ORDER.index(name), color=DRAWER_COL[name])

    def directory_card(self):
        head = text("HOSPITAL DIRECTORY", SMALL, RATIO, BOLD)
        need = text("needed:  “a doctor who treats children”", LABEL, INK, t2c={"children": WORD})
        cx, w = self.free_area()
        body = VGroup(head, need).arrange(DOWN, buff=0.2, aligned_edge=LEFT)
        fit_width(body, w - 1.4)
        card = self.card(body, width=min(w - 0.2, SAFE_W - 0.4))
        return card.move_to(RIGHT * cx + UP * (CARD_TOP - card.height / 2))

    def drawer_example(self, definition, word, build):
        """Definition → its drawer → root + ending → the word, beside the pinned drawers."""
        name = drawer_of(word)
        cx, w = self.free_area()
        head = fitted_text(f"“{definition}”", w - 0.8, BODY, INK, NORMAL, max_lines=2)
        drawer = VGroup(text("→", LABEL, MUTED), pill(name.upper() + " drawer", DRAWER_COL[name], size=LABEL))\
            .arrange(RIGHT, buff=0.3)
        parts = VGroup(*[VGroup(pill(piece, RATIO, size=LABEL), text(meaning, SMALL, MUTED)).arrange(DOWN, buff=0.1)
                         for piece, meaning in build]).arrange(RIGHT, buff=0.3, aligned_edge=UP)
        answer = pill(word, GOOD, size=BODY)
        block = VGroup(head, drawer, parts, answer).arrange(DOWN, buff=0.45, aligned_edge=LEFT)
        fit_height(block, SAFE_H - 1.6)
        self.place_free(block, y=0.1)
        self.no_overlap(head, drawer, parts, answer)
        self.validator.check_in_frame(block)
        return name, head, drawer, parts, answer

    def drawer_board(self, names):
        rows, cols = [], []
        for name in names:
            for definition, word in DRAWERS[name]:
                rows.append([definition, word])
                cols.append(DRAWER_COL[name])
        table = self.table_rows([" / ".join(names), "Word"], rows, [5.6, 6.4], size=LABEL)
        for row, c in zip(table[1:], cols):
            row[1].set_color(c)
        board = self.card(table, width=SAFE_W - 0.2)
        fit_height(board, SAFE_H - 1.0)
        board.move_to(UP * 0.3)
        self.validator.check_in_frame(board)
        return board, table

    # ========================================= 0. LESSON INTRO ==========

    def lesson_intro(self):
        self.scene_start("S00_intro", title="Lesson Introduction")

        crumb = self.breadcrumb("English · Module 1 Vocabulary", "Lesson 4 · One-Word Substitution", "Video 2")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        conds = VGroup(pill("CATEGORY", WORD, size=LABEL), pill("CORE", RATIO, size=LABEL),
                       pill("QUALIFIER", SECOND, size=LABEL)).arrange(RIGHT, buff=0.4)
        first = pill("the first condition is always the CATEGORY  →  today's lists are organised by it", FOCUS,
                     size=SMALL)
        VGroup(conds, first).arrange(DOWN, buff=0.7).move_to(DOWN * 0.1)
        fit_width(first, SAFE_W)
        self.no_overlap(crumb, conds, first)
        self.validator.check_in_frame(VGroup(crumb, conds, first))

        n = self.narrate(
            id="intro_01",
            text="Video one taught you to read a definition as conditions. The first condition is always the category, so "
                 "today's lists are organised by category.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.at_word(n, "conditions")
        self.play(LaggedStart(*[FadeIn(c, shift=UP * 0.1) for c in conds], lag_ratio=0.25))
        self.at_word(n, "first")
        self.play(Indicate(conds[0], color=WORD, scale_factor=1.15), FadeIn(first, shift=UP * 0.1))
        self.wait_for_narration(n)

        title = fitted_text("Common Substitutions", SAFE_W, 72, INK, BOLD)
        sub = text("people  ·  actions  ·  places  ·  states", LABEL, MUTED)
        underline = Line(LEFT, RIGHT, color=GOOD, stroke_width=5).set_width(title.width * 0.6)
        VGroup(title, underline, sub).arrange(DOWN, buff=0.2).move_to(UP * 0.2)
        goals = [("Learn high-frequency substitutes in four categories", GOOD),
                 ("Use category and root to recall the word quickly", RATIO)]
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
            text="This video is common substitutions: people, actions, places and states. By the end, you'll learn "
                 "high-frequency substitutes in four categories, and use category and root to recall the word quickly.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(VGroup(conds, first), shift=UP * 0.3))
        self.at_word(n, "common")
        self.play(Write(title), run_time=1.1)
        self.play(GrowFromCenter(underline))
        self.at_word(n, "people")
        self.play(FadeIn(sub, shift=UP * 0.1))
        self.at_word(n, "By")
        self.play(FadeOut(underline), FadeOut(sub), ReplacementTransform(title, small_title), run_time=0.8)
        self.play(FadeIn(objectives[0]), FadeIn(heading))
        for row_, spoken in zip(rows, ["learn", "recall"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row_, shift=RIGHT * 0.2), run_time=0.5)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_intro")

    # ================================================= 1. HOOK ==========

    HOOK = dict(word="doctor for children", options=["Orthopaedician", "Dermatologist", "Gynaecologist", "Paediatrician"],
                key="d", traps={"a": "treats bones", "b": "treats skin", "c": "treats women's reproductive health"})

    def hook(self):
        self.scene_start("S01_hook", title="Hook")

        h = self.HOOK
        assert drawer_of(h["options"]["abcd".index(h["key"])].lower()) == "People"
        board = self.directory_card()
        q = OptionQuestion(h["word"], h["options"], h["key"], h["traps"])
        opts = q.rows.copy().arrange(RIGHT, buff=0.7)
        fit_width(opts, SAFE_W)
        ask = pill("which board do you point to?", FOCUS, size=LABEL)
        ask.next_to(board, DOWN, buff=0.6)
        opts.next_to(ask, DOWN, buff=0.7)
        self.no_overlap(board, ask, opts)
        self.validator.check_in_frame(VGroup(board, ask, opts))

        n = self.narrate(
            id="hook_01",
            text="You're helping a relative find the right department on a hospital directory. She needs a doctor who "
                 "treats children. Which board do you point to?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "directory")
        self.play(FadeIn(board[0]), FadeIn(board[1][0]))
        self.at_word(n, "children")
        self.play(FadeIn(board[1][1], shift=UP * 0.1))
        self.at_word(n, "Which")
        self.play(FadeIn(ask, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_02",
            text="Orthopaedician, dermatologist, gynaecologist, or paediatrician?",
            voice="default",
            subtitle=True,
            pause_after=3.0,
        )
        for row, spoken in zip(opts, ["Orthopaedician", "dermatologist", "gynaecologist", "paediatrician"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=UP * 0.15), run_time=0.35)
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        self.clear_stage()
        self.scene_end("S01_hook")

    # ============================================== 2. CONCEPT ==========

    def concept(self):
        self.scene_start("S02_concept", title="The Concept")

        head = pill("most definitions describe one of FOUR things", FOCUS, size=LABEL)
        head.move_to(UP * (CARD_TOP - head.height / 2))
        starts = {"People": "“someone who …”", "Actions": "“the act of …”", "Places": "“a place where …”",
                  "States": "“that which cannot be …”"}
        rows = VGroup(*[VGroup(pill(d[:-1].upper() if d != "States" else "STATE / QUALITY", DRAWER_COL[d], size=LABEL),
                               text(starts[d], LABEL, INK), text(ENDINGS[d], LABEL, DRAWER_COL[d]))
                        .arrange(RIGHT, buff=0.4) for d in PIN_ORDER])
        rows.arrange(DOWN, buff=0.4, aligned_edge=LEFT)
        for r in rows:                                   # endings in one column
            r[2].set_x(max(x[1].get_right()[0] for x in rows) + 0.5 + r[2].width / 2)
        fit_width(rows, SAFE_W)
        rows.next_to(head, DOWN, buff=0.6)
        narrows = pill("the category narrows the ENDING you're looking for", GOOD, size=SMALL)
        narrows.next_to(rows, DOWN, buff=0.45)
        self.no_overlap(head, rows, narrows)
        self.validator.check_in_frame(VGroup(head, rows, narrows))

        n = self.narrate(
            id="concept_01",
            text="Most definitions describe one of four things: a person, someone who; an action, the act of; a place, a "
                 "place where; or a state or quality, that which cannot be.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "four")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        for r, spoken in zip(rows, ["person", "action", "place", "state"]):
            self.at_word(n, spoken, occurrence=1)
            self.play(FadeIn(r[:2], shift=RIGHT * 0.2), run_time=0.45)
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_02",
            text="Knowing the category immediately narrows the ending you're looking for. Persons often end in ist, er, "
                 "ian or ant. Killings end in cide. Places end in ary, arium or ory. And cannot-be states use ible or "
                 "able, with a negative prefix.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "narrows")
        self.play(FadeIn(narrows, shift=UP * 0.1))
        for r, spoken in zip(rows, ["Persons", "Killings", "Places", "states"]):
            self.at_word(n, spoken)
            self.play(FadeIn(r[2], shift=LEFT * 0.1), run_time=0.45)
        self.wait_for_narration(n)

        # Medical terms: root + ending.
        med = pill("medical and professional terms: especially common", BAD, size=LABEL)
        med.move_to(UP * (CARD_TOP - med.height / 2))
        formula = VGroup(pill("root: body part or group", RATIO, size=LABEL), text("+", LABEL, MUTED),
                         pill("-ologist  /  -ician", WORD, size=LABEL)).arrange(RIGHT, buff=0.3)
        build = VGroup(VGroup(pill("paed", RATIO, size=BODY), text("child", SMALL, MUTED)).arrange(DOWN, buff=0.1),
                       text("+", BODY, MUTED),
                       VGroup(pill("-iatrician", WORD, size=BODY), text("healer", SMALL, MUTED)).arrange(DOWN, buff=0.1),
                       text("=", BODY, MUTED), pill("paediatrician", GOOD, size=BODY))\
            .arrange(RIGHT, buff=0.3, aligned_edge=UP)
        body = VGroup(formula, build).arrange(DOWN, buff=0.8)
        fit_width(body, SAFE_W)
        body.next_to(med, DOWN, buff=0.8)
        self.no_overlap(med, formula, build)
        self.validator.check_in_frame(VGroup(med, body))
        n = self.narrate(
            id="concept_03",
            text="Medical and professional terms are especially common. They're built from a root for the body part or "
                 "group, plus ologist or ician. Paed, meaning child, plus iatrician, a healer, gives paediatrician.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(VGroup(head, rows, narrows)))
        self.at_word(n, "Medical")
        self.play(FadeIn(med, shift=DOWN * 0.2))
        self.at_word(n, "root")
        self.play(FadeIn(formula, shift=UP * 0.1))
        self.at_word(n, "Paed")
        self.play(FadeIn(build[0], shift=UP * 0.1))
        self.at_word(n, "iatrician")
        self.play(FadeIn(build[1:3], shift=UP * 0.1))
        self.at_word(n, "paediatrician")
        self.play(FadeIn(build[3:], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_concept")

    # ======================================== 3. WHY YOU NEED IT ==========

    def why_you_need_it(self):
        self.scene_start("S03_why", title="Why You Need It")

        share = pill("these lists cover a large share of real exam questions", BAD, size=LABEL)
        recall = pill("learned by category  →  recalled from the definition's FIRST WORDS", GOOD, size=LABEL)
        group = VGroup(share, recall).arrange(DOWN, buff=0.9)
        fit_width(group, SAFE_W).move_to(UP * 0.3)
        self.no_overlap(share, recall)
        self.validator.check_in_frame(group)

        n = self.narrate(
            id="why_01",
            text="These lists cover a large share of real exam questions. Learning them by category means you can recall "
                 "them from the definition's first words.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "share")
        self.play(FadeIn(share, shift=DOWN * 0.1))
        self.at_word(n, "category")
        self.play(FadeIn(recall, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_why")

    # ============================================== 4. ANALOGY ==========

    def analogy(self):
        self.scene_start("S04_analogy", title="The Analogy")

        drawers = VGroup(*[VGroup(Rectangle(width=3.6, height=0.85, color=DRAWER_COL[d], stroke_width=4),
                                  text(d, LABEL, DRAWER_COL[d], BOLD)) for d in PIN_ORDER]).arrange(DOWN, buff=0.12)
        drawers.move_to(LEFT * 3.6 + UP * 0.3)
        target = drawers[PIN_ORDER.index("Places")]
        first = text("“A place where birds are kept”", LABEL, INK, t2c={"A place where": RATIO})
        arrow_tip = text("first words  →  which drawer", SMALL, RATIO)
        never = pill("you never search the whole cabinet", GOOD, size=LABEL)
        right = VGroup(first, arrow_tip, never).arrange(DOWN, buff=0.5, aligned_edge=LEFT)
        fit_width(right, 6.2)
        right.move_to(RIGHT * 3.0 + UP * 0.3)
        pointer = Arrow(first.get_left() + LEFT * 0.15, target.get_right() + RIGHT * 0.1, buff=0, color=RATIO,
                        stroke_width=5)
        self.no_overlap(drawers, right)
        self.validator.check_in_frame(VGroup(drawers, right))

        n = self.narrate(
            id="analogy_01",
            text="A four-drawer filing cabinet. The first words of the definition tell you which drawer to open. You never "
                 "search the whole cabinet.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "four-drawer")
        self.play(LaggedStart(*[FadeIn(d, shift=RIGHT * 0.2) for d in drawers], lag_ratio=0.2))
        self.at_word(n, "first")
        self.play(FadeIn(first, shift=LEFT * 0.1), FadeIn(arrow_tip))
        self.at_word(n, "open")
        self.play(GrowArrow(pointer), Indicate(target, color=RATIO, scale_factor=1.08))
        self.at_word(n, "never")
        self.play(FadeIn(never, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_analogy")

    # ======================================== 5-7. WORKED EXAMPLES ==========

    def example_aviary(self):
        self.scene_start("S05_ex_aviary", title="Worked Example 1")
        self.play(self.pin(self.drawer_pin()))

        name, head, drawer, parts, answer = self.drawer_example("A place where birds are kept", "aviary",
                                                                [("avi", "bird"), ("-ary", "place ending")])

        n = self.narrate(
            id="ex1_01",
            text="A place where birds are kept. A place where: open the place drawer. The root avi means bird, and the "
                 "ending is ary. So the word is aviary.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "birds")
        self.play(FadeIn(head, shift=DOWN * 0.1))
        self.at_word(n, "drawer")
        self.play(FadeIn(drawer, shift=RIGHT * 0.1), self.open_drawer(name))
        self.at_word(n, "root")
        self.play(LaggedStart(*[FadeIn(p, shift=UP * 0.1) for p in parts], lag_ratio=0.4))
        self.at_word(n, "aviary")
        self.play(FadeIn(answer, scale=1.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_ex_aviary")

    def example_incorrigible(self):
        self.scene_start("S06_ex_incorrigible", title="Worked Example 2")

        name, head, drawer, parts, answer = self.drawer_example("That which cannot be corrected", "incorrigible",
                                                                [("in-", "not"), ("corrigible", "correctable")])

        n = self.narrate(
            id="ex2_01",
            text="That which cannot be corrected. That which cannot be: open the state drawer. A negative prefix, in, plus "
                 "corrigible, correctable. So the word is incorrigible.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "corrected")
        self.play(FadeIn(head, shift=DOWN * 0.1))
        self.at_word(n, "drawer")
        self.play(FadeIn(drawer, shift=RIGHT * 0.1), self.open_drawer(name))
        self.at_word(n, "prefix")
        self.play(LaggedStart(*[FadeIn(p, shift=UP * 0.1) for p in parts], lag_ratio=0.4))
        self.at_word(n, "incorrigible")
        self.play(FadeIn(answer, scale=1.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_ex_incorrigible")

    def example_patricide(self):
        self.scene_start("S07_ex_patricide", title="Worked Example 3")

        name, head, drawer, parts, answer = self.drawer_example("Killing of one's own father", "patricide",
                                                                [("patri", "father"), ("-cide", "killing")])

        n = self.narrate(
            id="ex3_01",
            text="Killing of one's own father. Killing of: open the action drawer. The root patri means father, and cide "
                 "means killing. So the word is patricide.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "father", occurrence=1)
        self.play(FadeIn(head, shift=DOWN * 0.1))
        self.at_word(n, "drawer")
        self.play(FadeIn(drawer, shift=RIGHT * 0.1), self.open_drawer(name))
        self.at_word(n, "root")
        self.play(LaggedStart(*[FadeIn(p, shift=UP * 0.1) for p in parts], lag_ratio=0.4))
        self.at_word(n, "patricide")
        self.play(FadeIn(answer, scale=1.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S07_ex_patricide")

    # ================================================ 8. RULES ==========

    def rules_people(self):
        self.scene_start("S08_rules_people", title="Rules: People")
        self.play(self.unpin())

        board, table = self.drawer_board(["People"])

        n = self.narrate(
            id="rules_01",
            text="The people drawer. Doctors for children, skin, eyes and bones: paediatrician, dermatologist, "
                 "ophthalmologist, orthopaedist. A lover of mankind is a philanthropist; a hater of mankind, a "
                 "misanthrope. One who hates women: a misogynist. One who knows everything: omniscient. A lover of books: "
                 "a bibliophile. One who eats human flesh: a cannibal.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "people")
        self.play(FadeIn(board[0]), FadeIn(table[0]))
        for row, spoken in zip(table[1:], ["Doctors", "philanthropist", "misogynist", "omniscient", "bibliophile",
                                           "cannibal"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.45)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S08_rules_people")

    def rules_places_actions(self):
        self.scene_start("S09_rules_places_actions", title="Rules: Places and Actions")

        board, table = self.drawer_board(["Places", "Actions"])

        n = self.narrate(
            id="rules_02",
            text="The places drawer. Birds, bees and fish are kept in an aviary, an apiary and an aquarium. Dead bodies: a "
                 "mortuary. Arms: an armoury, or arsenal. Orphans: an orphanage.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "places")
        self.play(FadeIn(board[0]), FadeIn(table[0]))
        for row, spoken in zip(table[1:5], ["Birds", "Dead", "Arms", "Orphans"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.45)
        self.wait_for_narration(n)

        n = self.narrate(
            id="rules_03",
            text="The actions drawer. Killing a king, mother, father or brother: regicide, matricide, patricide, "
                 "fratricide. Killing oneself: suicide. And painless killing to end suffering: euthanasia.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "actions")
        self.play(Indicate(table[0][0], color=BAD, scale_factor=1.05))
        for row, spoken in zip(table[5:], ["king", "oneself", "painless"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.45)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S09_rules_places_actions")

    def rules_states(self):
        self.scene_start("S10_rules_states", title="Rules: States and Qualities")

        board, table = self.drawer_board(["States"])

        n = self.narrate(
            id="rules_04",
            text="The states drawer. What cannot be read, corrected or avoided is illegible, incorrigible, inevitable. "
                 "What cannot be seen or heard is invisible, inaudible. One who cannot make a mistake is infallible. Name "
                 "not known: anonymous. Everyone agrees: unanimous.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "states")
        self.play(FadeIn(board[0]), FadeIn(table[0]))
        for row, spoken in zip(table[1:], ["read", "seen", "mistake", "Name", "Everyone"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.45)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S10_rules_states")

    # ============================================= 11. PROCESS ==========

    def process(self):
        self.scene_start("S11_process", title="The Process")

        steps = VGroup(*[VGroup(pill(str(i + 1), c, size=SMALL), fitted_text(s_, SAFE_W - 2.2, BODY, INK))
                         .arrange(RIGHT, buff=0.3) for i, (s_, c) in enumerate([
                             ("Open the right drawer: person, action, place or state", WORD),
                             ("Find the root for the core idea", RATIO),
                             ("Add the drawer's typical ending", SECOND),
                             ("Eliminate same-family words from other drawers", BAD)])])
        steps.arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        board = self.card(steps).move_to(UP * 0.3)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="process_01",
            text="The process. First, open the right drawer: person, action, place or state. Second, find the root for the "
                 "core idea. Third, add the drawer's typical ending. And fourth, eliminate same-family words from other "
                 "drawers.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(board[0]))
        for r, spoken in zip(steps, ["First", "Second", "Third", "fourth"]):
            self.at_word(n, spoken)
            self.play(FadeIn(r, shift=RIGHT * 0.2), run_time=0.45)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S11_process")

    # ========================================== 12. HOOK, SOLVED ==========

    def hook_solved(self):
        self.scene_start("S12_hook_solved", title="Hook, Solved")
        self.play(self.pin(self.drawer_pin()))

        h = self.HOOK
        board = self.directory_card()
        q = OptionQuestion(h["word"], h["options"], h["key"], h["traps"], word_size=LABEL)
        fit_height(q.group, board.get_bottom()[1] - 0.4 - (BOTTOM_Y + 1.4))
        q.group.next_to(board, DOWN, buff=0.4).to_edge(LEFT, buff=SAFE + 0.6)
        pin_left = self.pinned.get_left()[0]
        predict = pill("paed = child  →  paediatrician", STEP_COLS["PREDICT"], size=SMALL)
        fit_width(predict, pin_left - 0.3 - (q.word.get_right()[0] + 0.3))
        predict.next_to(q.word, RIGHT, buff=0.3)
        conf = text("a paediatrician is a doctor who treats children", LABEL, GOOD)
        fit_width(conf, pin_left - 0.6 - q.group.get_left()[0])
        conf.next_to(q.group, DOWN, buff=0.35).align_to(q.group, LEFT)
        self.no_overlap(board, q.group, conf)
        self.no_overlap(board, self.pinned)
        self.no_overlap(q.rows, predict)
        self.no_overlap(predict, self.pinned)
        self.validator.check_in_frame(VGroup(board, q.group, predict, conf))

        n = self.narrate(
            id="solved_01",
            text="Let's solve the hook. Read: a person, a doctor, who treats children. Predict: paed means child, so "
                 "paediatrician.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(board), FadeIn(q.word), FadeIn(q.rows))
        self.at_word(n, "Read")
        self.play(Indicate(board[1][1], color=WORD, scale_factor=1.03), self.open_drawer("People"))
        self.at_word(n, "Predict")
        self.play(FadeIn(predict, shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_02",
            text="Eliminate. An orthopaedician treats bones. A dermatologist treats skin. A gynaecologist treats women's "
                 "reproductive health.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Eliminate")
        self.play(Indicate(q.rows, color=BAD, scale_factor=1.02))
        for letter, spoken in [("a", "orthopaedician"), ("b", "dermatologist"), ("c", "gynaecologist")]:
            self.at_word(n, spoken)
            self.play(*q.strike(letter)[1])
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_03",
            text="Confirm: a paediatrician is a doctor who treats children. That's the answer.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Confirm")
        self.play(FadeIn(conf, shift=UP * 0.1))
        self.at_word(n, "answer")
        self.play(*q.confirm()[1])
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S12_hook_solved")

    # ========================================== 13. EXAM PATTERNS ==========

    def exam_patterns(self):
        self.scene_start("S13_patterns", title="Exam Patterns and Solving Models")
        self.play(self.unpin())

        table = self.table_rows(["Pattern", "Solving model"], [
            ["“A person who …”", "person drawer → root + -ist / -er / -ian"],
            ["“A place where … are kept”", "place drawer → -ary / -arium / -ory"],
            ["“That which cannot be …”", "state drawer → in- / il- / im- + -ible / -able"],
        ], [5.0, 6.8], size=LABEL)
        board = self.card(table, width=SAFE_W - 0.2).move_to(UP * 0.4)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="patterns_01",
            text="Three exam patterns. A person who: open the person drawer, then root plus ist, er or ian. A place where "
                 "things are kept: the place drawer, then ary, arium or ory. That which cannot be: the state drawer, then "
                 "a negative prefix, plus ible or able.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(board[0]), FadeIn(table[0]))
        for row, spoken in zip(table[1:], ["person", "place", "cannot"]):
            self.at_word(n, spoken, occurrence=1)
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.45)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S13_patterns")

    # ======================================== 14. COMMON MISTAKES ==========

    def common_mistakes(self):
        self.scene_start("S14_mistakes", title="Common Mistakes")

        card_w = ZONE_W - 0.3
        pairs = [
            (self.verdict_card(False, "aviary = apiary", card_w),
             self.verdict_card(True, "aviary: birds;  apiary: bees", card_w)),
            (self.verdict_card(False, "philanthropist = misanthrope", card_w),
             self.verdict_card(True, "phil-: loves;  mis-: hates", card_w)),
            (self.verdict_card(False, "Right root, wrong drawer", card_w),
             self.verdict_card(True, "geologist: person;  geology: study", card_w)),
        ]
        for (wrong, right), yy in zip(pairs, [1.6, 0.05, -1.5]):
            wrong.move_to(LEFT_ZONE + UP * yy)
            right.move_to(RIGHT_ZONE + UP * yy)
        header = pill("3 mistakes", BAD, size=LABEL).move_to(UP * (CARD_TOP - 0.3))
        self.validator.check_in_frame(VGroup(header, *[c for p in pairs for c in p]))

        n = self.narrate(
            id="mistakes_01",
            text="Three common mistakes. The first is confusing aviary, for birds, and apiary, for bees. The second is "
                 "confusing philanthropist and misanthrope. The third is picking the right root from the wrong drawer, "
                 "like geology for a geologist.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(header))
        for pr, spoken in zip(pairs, ["first", "second", "third"]):
            self.at_word(n, spoken)
            self.play(FadeIn(pr[0], shift=RIGHT * 0.3), FadeIn(pr[1], shift=LEFT * 0.3))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S14_mistakes")

    # ============================================== 15. PRACTICE ==========

    PRACTICE = [
        ("A place where bees are kept", ["aviary", "apiary", "aquarium", "granary"], "b", "(a) an aviary is for birds"),
        ("That which cannot be avoided", ["invincible", "infallible", "inevitable", "incorrigible"], "c",
         "(a) invincible = cannot be defeated"),
        ("One who loves mankind", ["philanthropist", "misanthrope", "philatelist", "anthropologist"], "a",
         "(c) a philatelist collects stamps;  (d) an anthropologist studies humans"),
    ]

    def practice(self):
        self.scene_start("S15_practice", title="Practice Questions")

        head = pill("One word for the phrase?", GOOD, size=LABEL)
        lines = VGroup(*[VGroup(VGroup(pill(str(i + 1), FOCUS, size=SMALL), text(f"“{phrase}”", LABEL, WORD))
                                .arrange(RIGHT, buff=0.35),
                                text("   ".join(f"({l}) {o}" for l, o in zip("abcd", opts)), LABEL, INK))
                         .arrange(DOWN, buff=0.2, aligned_edge=LEFT)
                         for i, (phrase, opts, *_r) in enumerate(self.PRACTICE)])
        lines.arrange(DOWN, buff=0.4, aligned_edge=LEFT)
        board = self.card(VGroup(head, lines).arrange(DOWN, buff=0.4, aligned_edge=LEFT), color=FOCUS)
        fit_within(board, SAFE_W, SAFE_H - 1.2)
        board.move_to(UP * 0.4)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="practice_01",
            text="Your turn. One: a place where bees are kept. Aviary, apiary, aquarium, or granary? Two: that which cannot "
                 "be avoided. Invincible, infallible, inevitable, or incorrigible? Three: one who loves mankind. "
                 "Philanthropist, misanthrope, philatelist, or anthropologist?",
            voice="default",
            subtitle=True,
            pause_after=10.0,
        )
        self.play(FadeIn(board[0]), FadeIn(head))
        for ln, (spoken, first_option) in zip(lines, [("bees", "Aviary"), ("avoided", "Invincible"),
                                                     ("loves", "Philanthropist")]):
            self.at_word(n, spoken)
            self.play(FadeIn(ln[0], shift=UP * 0.15), run_time=0.4)
            self.at_word(n, first_option)
            self.play(FadeIn(ln[1], shift=LEFT * 0.15), run_time=0.4)
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        self.clear_stage()
        self.scene_end("S15_practice")

    # =============================================== 16. ANSWERS ==========

    def answers(self):
        self.scene_start("S16_answers", title="Answers")

        rows = VGroup()
        for phrase, opts, key, why in self.PRACTICE:
            word = opts["abcd".index(key)]
            d = drawer_of(word)                               # every answer is in the Rules tables
            rows.add(VGroup(VGroup(text(f"“{phrase}”", LABEL, INK), text("→", LABEL, MUTED),
                                   pill(f"({key}) {word}", GOOD, size=LABEL), pill(d, DRAWER_COL[d], size=SMALL))
                            .arrange(RIGHT, buff=0.3), text(why, SMALL, BAD)).arrange(DOWN, buff=0.18, aligned_edge=LEFT))
        rows.arrange(DOWN, buff=0.5, aligned_edge=LEFT)
        fit_within(rows, SAFE_W, SAFE_H - 1.2)
        rows.move_to(UP * 0.3)
        self.validator.check_in_frame(rows)

        n = self.narrate(
            id="answers_01",
            text="One: apiary. An aviary is for birds. Two: inevitable. Invincible means cannot be defeated. Three: "
                 "philanthropist. A philatelist collects stamps, and an anthropologist studies humans.",
            voice="default",
            subtitle=True,
        )
        for r, (spoken, why) in zip(rows, [("apiary", "birds"), ("inevitable", "defeated"), ("philanthropist", "stamps")]):
            self.at_word(n, spoken)
            self.play(FadeIn(r[0], shift=RIGHT * 0.2), run_time=0.5)
            self.at_word(n, why)
            self.play(FadeIn(r[1], shift=LEFT * 0.1), run_time=0.4)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S16_answers")

    # ================================================ 17. RECAP ==========

    def recap(self):
        self.scene_start("S17_recap", title="Recap Card")

        card, table = self.recap_card("Recap Card: Video 2", [
            ["Four drawers", "people, actions, places, states"],
            ["Endings", "-ist/-er/-ian (person), -ary/-arium (place), -cide (killing), in-…-ible (cannot be)"],
            ["Pairs to watch", "aviary / apiary,  philanthropist / misanthrope"],
        ])
        card.move_to(UP * 0.2)
        self.validator.check_in_frame(card)

        n = self.narrate(
            id="recap_01",
            text="To recap. Four drawers: people, actions, places, states. Know the endings: ist, er and ian for a person; "
                 "ary and arium for a place; cide for a killing; and in, plus ible, for cannot be. And two pairs to "
                 "watch: aviary and apiary, philanthropist and misanthrope.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(card[0]), FadeIn(table[0]))
        for row, spoken in zip(table[1:], ["drawers", "endings", "pairs"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.45)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S17_recap")

    # ================================================= 18. NEXT ==========

    def next_video(self):
        self.scene_start("S18_next", title="Next")

        enough = pill("knowing the word isn't enough", MUTED, size=LABEL)
        fit = pill("it must also FIT the sentence", GOOD, size=BODY)
        nxt = pill("Next:  Context-Based Usage", FOCUS, size=LABEL)
        VGroup(enough, fit, nxt).arrange(DOWN, buff=0.7).move_to(UP * 0.2)
        self.no_overlap(enough, fit, nxt)
        self.validator.check_in_frame(VGroup(enough, fit, nxt))

        n = self.narrate(
            id="next_01",
            text="Knowing the word isn't enough; it must also fit the sentence. Video three shows how.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "enough")
        self.play(FadeIn(enough, shift=DOWN * 0.1))
        self.at_word(n, "fit")
        self.play(FadeIn(fit, shift=UP * 0.1))
        self.at_word(n, "Video")
        self.play(FadeIn(nxt, scale=1.05))
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S18_next")

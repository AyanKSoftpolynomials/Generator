"""
animation.py for the LMS video generator.

Course : C-CAT - Section A - English
Module : Module 1 - Vocabulary
Lesson : Lesson 5 - Analogies
Video  : 02 - Types of Relationships (Video 2 of 7)

Source script:
  C:\\Users\\User\\Downloads\\C-CAT_SectionA_Module1_English\\English\\Module 1 - Vocabulary\\
  Lesson 5 - Analogies\\02 - Types of Relationships.pdf

Built on the golden-reference pattern:
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``;
  * layouts stacked with next_to and guarded with ``no_overlap``; nothing is
    ever animated onto or into another box.

The four families of relationship types live in FAMILIES and the twelve-row Rules table (type, bridge, example) in TYPES; family_of(type) finds a type's family, and the concept, rules tables and recap are built from this data.
The "name the TYPE" card (meaning, structure, action, other) stays pinned top-right through the worked examples and Hook, Solved; the family in use lights up.
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

# The four families, with the pairs the script uses to introduce each type.
FAMILIES = {
    "MEANING": [("synonym", "big : large"), ("antonym", "hot : cold"), ("degree", "warm : hot")],
    "STRUCTURE": [("part–whole", "page : book"), ("type–category", "rose : flower"), ("group–member", "flock : sheep")],
    "ACTION": [("worker–tool", "carpenter : saw"), ("worker–product", "baker : bread"), ("tool–function", "knife : cut"),
               ("instrument–measures", "thermometer : temperature")],
    "OTHER": [("cause–effect", "fire : smoke"), ("place", "bee : hive"), ("young", "cow : calf"),
              ("lack", "drought : water")],
}
FAMILY_COL = dict(zip(FAMILIES, [WORD, SECOND, RATIO, GOOD]))

# The script's Rules table: (type, ready-made bridge, example).
TYPES = [
    ("Synonym / Antonym", "means the same / opposite", "brave : bold  /  brave : cowardly"),
    ("Degree", "is a stronger form of", "hot : warm  (reversed: warm : hot)"),
    ("Part–whole", "is part of", "petal : flower"),
    ("Type–category", "is a type of", "cobra : snake"),
    ("Group–member", "is a group of", "pack : wolves"),
    ("Worker–tool", "uses", "surgeon : scalpel"),
    ("Worker–product", "makes", "potter : pot"),
    ("Tool–function", "is used to", "scissors : cut"),
    ("Instrument–measures", "measures", "ammeter : current"),
    ("Cause–effect", "causes", "virus : disease"),
    ("Place / habitat", "lives or works in", "lion : den"),
    ("Lack", "is a lack of", "darkness : light"),
]
BRIDGE = {t: b for t, b, _e in TYPES}


def family_of(type_name):
    for fam, items in FAMILIES.items():
        if type_name in [t for t, _e in items]:
            return fam
    raise KeyError(type_name)


def analogy_line(a, b, c, d="?", size=BODY):
    """A : B :: C : D as chips.  [0], [2] = first pair;  [4], [6] = second pair."""
    return VGroup(pill(a, WORD, size=size), text(":", size, MUTED), pill(b, WORD, size=size), text("::", size, MUTED),
                  pill(c, SECOND, size=size), text(":", size, MUTED),
                  pill(d, FOCUS if d == "?" else GOOD, size=size)).arrange(RIGHT, buff=0.25)


assert family_of("group–member") == "STRUCTURE" and family_of("lack") == "OTHER" and len(TYPES) == 12


class TypesOfRelationshipsVideo(LMSScene):
    lesson_title = "Types of Relationships"

    def construct(self):
        self.camera.background_color = BG

        self.lesson_intro()
        self.hook()
        self.concept()
        self.why_you_need_it()
        self.analogy()
        self.example_swarm()
        self.example_famine()
        self.example_odometer()
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

    def type_pin(self):
        return self.steps_pin("name the TYPE", [("MEANING: same, opposite, degree", FAMILY_COL["MEANING"]),
                                                ("STRUCTURE: part, type, group", FAMILY_COL["STRUCTURE"]),
                                                ("ACTION: tool, product, measures", FAMILY_COL["ACTION"]),
                                                ("OTHER: cause, place, young, lack", FAMILY_COL["OTHER"])])

    def light_family(self, fam):
        return self.pin_step(list(FAMILIES).index(fam), color=FAMILY_COL[fam])

    def manual_card(self):
        head = text("LAB MANUAL  ·  instruments and what they measure", SMALL, RATIO, BOLD)
        line = analogy_line("THERMOMETER", "TEMPERATURE", "BAROMETER", size=LABEL)
        cx, w = self.free_area()
        body = VGroup(head, line).arrange(DOWN, buff=0.25, aligned_edge=LEFT)
        fit_width(body, min(w - 1.4, SAFE_W - 1.8))
        card = self.card(body, width=min(w - 0.2, SAFE_W - 0.4))
        return card.move_to(RIGHT * cx + UP * (CARD_TOP - card.height / 2))

    def type_example(self, a, b, c, d, type_name, first, second):
        """Analogy line, its type (lit on the pin), the type's bridge on the first pair, then on the second."""
        fam = family_of(type_name)
        cx, w = self.free_area()
        line = analogy_line(a, b, c)
        kind = VGroup(pill("type", FAMILY_COL[fam], size=SMALL), text(type_name, LABEL, FAMILY_COL[fam], BOLD))\
            .arrange(RIGHT, buff=0.25)
        b1 = text(f"“{first}”", LABEL, INK)
        b2 = text(f"“{second}”", LABEL, INK, t2c={d: GOOD})
        block = VGroup(line, kind, b1, b2).arrange(DOWN, buff=0.5, aligned_edge=LEFT)
        fit_within(block, w - 0.6, SAFE_H - 1.8)
        self.place_free(block, y=0.2)
        answer = pill(d, GOOD, size=BODY).scale(line[6].height / pill("?", FOCUS, size=BODY).height)
        answer.move_to(line[6], aligned_edge=LEFT)
        self.no_overlap(line, kind, b1, b2)
        self.validator.check_in_frame(VGroup(block, answer))
        return fam, line, kind, b1, b2, answer

    def type_board(self, rows_):
        table = self.table_rows(["Type", "Bridge", "Example"], [list(r) for r in rows_], [3.8, 3.8, 4.4], size=LABEL)
        for row in table[1:]:
            row[0].set_color(WORD)
            row[1].set_color(RATIO)
        board = self.card(table, width=SAFE_W - 0.2)
        fit_height(board, SAFE_H - 1.0)
        board.move_to(UP * 0.3)
        self.validator.check_in_frame(board)
        return board, table

    # ========================================= 0. LESSON INTRO ==========

    def lesson_intro(self):
        self.scene_start("S00_intro", title="Lesson Introduction")

        crumb = self.breadcrumb("English · Module 1 Vocabulary", "Lesson 5 · Analogies", "Video 2")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        last = VGroup(pill("Video 1: the bridge sentence", MUTED, size=SMALL),
                      text("“A pilot operates an aircraft.”", LABEL, INK, t2c={"operates": RATIO})).arrange(DOWN, buff=0.2)
        dozen = pill("today: the dozen relationship TYPES most bridges fall into", RATIO, size=LABEL)
        fast = pill("so you can build a bridge in seconds", GOOD, size=LABEL)
        VGroup(last, dozen, fast).arrange(DOWN, buff=0.55).move_to(DOWN * 0.1)
        self.no_overlap(crumb, last, dozen, fast)
        self.validator.check_in_frame(VGroup(crumb, last, dozen, fast))

        n = self.narrate(
            id="intro_01",
            text="Video one introduced the bridge sentence. Today you learn the dozen relationship types that most bridges "
                 "fall into, so you can build them in seconds.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.at_word(n, "bridge")
        self.play(FadeIn(last, shift=UP * 0.1))
        self.at_word(n, "dozen")
        self.play(FadeIn(dozen, shift=UP * 0.1))
        self.at_word(n, "seconds")
        self.play(FadeIn(fast, shift=UP * 0.1))
        self.wait_for_narration(n)

        title = fitted_text("Types of Relationships", SAFE_W, 72, INK, BOLD)
        underline = Line(LEFT, RIGHT, color=RATIO, stroke_width=5).set_width(title.width * 0.6)
        VGroup(title, underline).arrange(DOWN, buff=0.2).move_to(UP * 0.2)
        goals = [("Recognise the most common relationship types in analogy questions", RATIO),
                 ("Name the type quickly, so the bridge sentence writes itself", GOOD)]
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
            text="This video is types of relationships. By the end, you'll recognise the most common relationship types in "
                 "analogy questions, and name the type quickly, so the bridge sentence writes itself.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(VGroup(last, dozen, fast), shift=UP * 0.3))
        self.at_word(n, "types", occurrence=1)
        self.play(Write(title), run_time=1.1)
        self.play(GrowFromCenter(underline))
        self.at_word(n, "By")
        self.play(FadeOut(underline), ReplacementTransform(title, small_title), run_time=0.8)
        self.play(FadeIn(objectives[0]), FadeIn(heading))
        for row_, spoken in zip(rows, ["recognise", "name"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row_, shift=RIGHT * 0.2), run_time=0.5)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_intro")

    # ================================================= 1. HOOK ==========

    HOOK = dict(word="BAROMETER : ?", options=["weather", "height", "pressure", "rain"], key="c",
                traps={"a": "broader: forecast, not measured", "b": "measured by an altimeter",
                       "d": "measured by a rain gauge"})

    def hook(self):
        self.scene_start("S01_hook", title="Hook")

        h = self.HOOK
        manual = self.manual_card()
        line = manual[1][1]
        q = OptionQuestion(h["word"], h["options"], h["key"], h["traps"])
        opts = q.rows.copy().arrange(RIGHT, buff=0.9)
        opts.next_to(manual, DOWN, buff=0.9)
        self.no_overlap(manual, opts)
        self.validator.check_in_frame(VGroup(manual, opts))

        n = self.narrate(
            id="hook_01",
            text="A lab manual lists instruments, and what they measure. Thermometer is to temperature, as barometer is to "
                 "what?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "manual")
        self.play(FadeIn(manual[0]), FadeIn(manual[1][0]))
        self.at_word(n, "Thermometer")
        self.play(FadeIn(line[:3], shift=RIGHT * 0.2))
        self.at_word(n, "barometer")
        self.play(FadeIn(line[3:], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_02",
            text="Weather, height, pressure, or rain?",
            voice="default",
            subtitle=True,
            pause_after=3.0,
        )
        for row, spoken in zip(opts, ["Weather", "height", "pressure", "rain"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=UP * 0.15), run_time=0.35)
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        self.clear_stage()
        self.scene_end("S01_hook")

    # ============================================== 2. CONCEPT ==========

    def concept(self):
        self.scene_start("S02_concept", title="The Concept")

        limited = pill("exam analogies come from a LIMITED set of relationship types", BAD, size=LABEL)
        ready = VGroup(pill("recognise the TYPE", RATIO, size=BODY), text("→", BODY, MUTED),
                       pill("a ready-made BRIDGE", GOOD, size=BODY)).arrange(RIGHT, buff=0.4)
        opening = VGroup(limited, ready).arrange(DOWN, buff=0.9)
        fit_width(opening, SAFE_W).move_to(UP * 0.3)
        self.validator.check_in_frame(opening)

        n = self.narrate(
            id="concept_01",
            text="Exam analogies come from a limited set of relationship types. Recognising the type gives you a "
                 "ready-made bridge.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "limited")
        self.play(FadeIn(limited, shift=DOWN * 0.1))
        self.at_word(n, "Recognising")
        self.play(FadeIn(ready[0], shift=RIGHT * 0.2))
        self.at_word(n, "ready-made")
        self.play(FadeIn(ready[1:], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        heads = VGroup(*[pill(f + " links", FAMILY_COL[f], size=LABEL) for f in FAMILIES]).arrange(RIGHT, buff=0.35)
        fit_width(heads, SAFE_W)
        heads.move_to(UP * (CARD_TOP - heads.height / 2))

        def family_rows(fam):
            rows = VGroup(*[VGroup(pill(t, FAMILY_COL[fam], size=LABEL), text(e, BODY, INK)).arrange(RIGHT, buff=0.4)
                            for t, e in FAMILIES[fam]]).arrange(DOWN, buff=0.4, aligned_edge=LEFT)
            fit_within(rows, SAFE_W, SAFE_H - heads.height - 1.6)
            rows.next_to(heads, DOWN, buff=0.7)
            self.no_overlap(heads, rows)
            self.validator.check_in_frame(VGroup(heads, rows))
            return rows

        self.play(FadeOut(opening))

        meaning = family_rows("MEANING")
        n = self.narrate(
            id="concept_02",
            text="Meaning links. Synonym: big, large. Antonym: hot, cold. Degree: warm, hot.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Meaning")
        self.play(FadeIn(heads[0], shift=DOWN * 0.2))
        for r, spoken in zip(meaning, ["Synonym", "Antonym", "Degree"]):
            self.at_word(n, spoken)
            self.play(FadeIn(r, shift=RIGHT * 0.2), run_time=0.4)
        self.wait_for_narration(n)

        structure = family_rows("STRUCTURE")
        n = self.narrate(
            id="concept_03",
            text="Structure links. Part and whole: page, book. Type and category: rose, flower. Group and member: flock, "
                 "sheep.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(meaning))
        self.at_word(n, "Structure")
        self.play(FadeIn(heads[1], shift=DOWN * 0.2))
        for r, spoken in zip(structure, ["Part", "Type", "Group"]):
            self.at_word(n, spoken)
            self.play(FadeIn(r, shift=RIGHT * 0.2), run_time=0.4)
        self.wait_for_narration(n)

        action = family_rows("ACTION")
        n = self.narrate(
            id="concept_04",
            text="Action links. Worker and tool: carpenter, saw. Worker and product: baker, bread. Tool and function: "
                 "knife, cut. Instrument, and what it measures: thermometer, temperature.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(structure))
        self.at_word(n, "Action")
        self.play(FadeIn(heads[2], shift=DOWN * 0.2))
        for r, spoken in zip(action, ["carpenter", "baker", "knife", "thermometer"]):
            self.at_word(n, spoken)
            self.play(FadeIn(r, shift=RIGHT * 0.2), run_time=0.4)
        self.wait_for_narration(n)

        other = family_rows("OTHER")
        n = self.narrate(
            id="concept_05",
            text="Other links. Cause and effect: fire, smoke. Place: bee, hive. Young: cow, calf. Lack: drought, water.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(action))
        self.at_word(n, "Other")
        self.play(FadeIn(heads[3], shift=DOWN * 0.2))
        for r, spoken in zip(other, ["Cause", "Place", "Young", "Lack"]):
            self.at_word(n, spoken)
            self.play(FadeIn(r, shift=RIGHT * 0.2), run_time=0.4)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_concept")

    # ======================================== 3. WHY YOU NEED IT ==========

    def why_you_need_it(self):
        self.scene_start("S03_why", title="Why You Need It")

        instant = pill("type named  →  the bridge is instant", GOOD, size=BODY)
        drop = pill("…and so is the elimination: options of a different type drop out", BAD, size=LABEL)
        group = VGroup(instant, drop).arrange(DOWN, buff=0.9)
        fit_width(group, SAFE_W).move_to(UP * 0.3)
        self.no_overlap(instant, drop)
        self.validator.check_in_frame(group)

        n = self.narrate(
            id="why_01",
            text="With the type named, the bridge is instant, and so is the elimination: options of a different type drop "
                 "out immediately.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "instant")
        self.play(FadeIn(instant, shift=DOWN * 0.1))
        self.at_word(n, "elimination")
        self.play(FadeIn(drop, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_why")

    # ============================================== 4. ANALOGY ==========

    def analogy(self):
        self.scene_start("S04_analogy", title="The Analogy")

        sizes = [8, 10, 12, 14]
        sockets = VGroup(*[VGroup(Circle(radius=0.2 + 0.03 * s_, color=MUTED, stroke_width=5), text(str(s_), SMALL, MUTED))
                           .arrange(DOWN, buff=0.15) for s_ in sizes]).arrange(RIGHT, buff=0.6, aligned_edge=DOWN)
        sockets.move_to(LEFT * 3.2 + UP * 1.0)
        bolt = VGroup(RegularPolygon(n=6, color=RATIO, stroke_width=5).scale(0.55), text("bolt: size 12", SMALL, RATIO))\
            .arrange(DOWN, buff=0.15)
        bolt.move_to(LEFT * 3.2 + DOWN * 1.3)
        match = sockets[sizes.index(12)]
        tags = VGroup(pill("a socket set = the relationship types", MUTED, size=LABEL),
                      pill("don't try every socket: READ THE SIZE", RATIO, size=LABEL),
                      pill("name the TYPE  →  pick the BRIDGE", GOOD, size=LABEL))\
            .arrange(DOWN, buff=0.5, aligned_edge=LEFT)
        fit_width(tags, 6.2)
        tags.move_to(RIGHT * 3.3 + UP * 0.2)
        self.no_overlap(sockets, bolt)
        self.no_overlap(VGroup(sockets, bolt), tags)
        self.validator.check_in_frame(VGroup(sockets, bolt, tags))

        n = self.narrate(
            id="analogy_01",
            text="Relationship types are like a socket set. When you see a bolt, you don't try every socket; you read the "
                 "size, and pick the right one. Name the type, pick the bridge.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "socket", occurrence=1)
        self.play(LaggedStart(*[FadeIn(s_, shift=UP * 0.1) for s_ in sockets], lag_ratio=0.2), FadeIn(tags[0]))
        self.at_word(n, "bolt")
        self.play(FadeIn(bolt[0], scale=0.8))
        self.at_word(n, "size")
        self.play(FadeIn(bolt[1]), FadeIn(tags[1], shift=LEFT * 0.1))
        self.at_word(n, "pick", occurrence=1)
        self.play(match.animate.set_color(RATIO), run_time=0.4)
        self.play(Indicate(match, color=RATIO, scale_factor=1.15), run_time=0.6)
        self.at_word(n, "Name")
        self.play(FadeIn(tags[2], shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_analogy")

    # ======================================== 5-7. WORKED EXAMPLES ==========

    def example_swarm(self):
        self.scene_start("S05_ex_swarm", title="Worked Example 1")
        self.play(self.pin(self.type_pin()))

        fam, line, kind, b1, b2, answer = self.type_example(
            "Flock", "Sheep", "Swarm", "bees", "group–member", "A flock is a group of sheep.",
            "A swarm is a group of bees.")

        n = self.narrate(
            id="ex1_01",
            text="Flock is to sheep, as swarm is to what? The type: group and member. A flock is a group of sheep. So a "
                 "swarm is a group of bees.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Flock", occurrence=1)
        self.play(FadeIn(line, shift=DOWN * 0.1))
        self.at_word(n, "type")
        self.play(FadeIn(kind, shift=RIGHT * 0.2), self.light_family(fam))
        self.at_word(n, "sheep", occurrence=2)
        self.play(FadeIn(b1, shift=RIGHT * 0.2))
        self.at_word(n, "bees")
        self.play(FadeIn(b2, shift=RIGHT * 0.2), ReplacementTransform(line[6], answer))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_ex_swarm")

    def example_famine(self):
        self.scene_start("S06_ex_famine", title="Worked Example 2")

        fam, line, kind, b1, b2, answer = self.type_example(
            "Drought", "Water", "Famine", "food", "lack", "A drought is a lack of water.", "A famine is a lack of food.")

        n = self.narrate(
            id="ex2_01",
            text="Drought is to water, as famine is to what? The type: lack. A drought is a lack of water. So a famine is "
                 "a lack of food.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Drought", occurrence=1)
        self.play(FadeIn(line, shift=DOWN * 0.1))
        self.at_word(n, "type")
        self.play(FadeIn(kind, shift=RIGHT * 0.2), self.light_family(fam))
        self.at_word(n, "water", occurrence=2)
        self.play(FadeIn(b1, shift=RIGHT * 0.2))
        self.at_word(n, "food")
        self.play(FadeIn(b2, shift=RIGHT * 0.2), ReplacementTransform(line[6], answer))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_ex_famine")

    def example_odometer(self):
        self.scene_start("S07_ex_odometer", title="Worked Example 3")

        fam, line, kind, b1, b2, answer = self.type_example(
            "Seismograph", "Earthquake", "Odometer", "distance", "instrument–measures",
            "A seismograph measures earthquakes.", "An odometer measures distance.")

        n = self.narrate(
            id="ex3_01",
            text="Seismograph is to earthquake, as odometer is to what? The type: instrument, and what it measures. A "
                 "seismograph measures earthquakes. So an odometer measures distance.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Seismograph", occurrence=1)
        self.play(FadeIn(line, shift=DOWN * 0.1))
        self.at_word(n, "type")
        self.play(FadeIn(kind, shift=RIGHT * 0.2), self.light_family(fam))
        self.at_word(n, "earthquakes")
        self.play(FadeIn(b1, shift=RIGHT * 0.2))
        self.at_word(n, "distance")
        self.play(FadeIn(b2, shift=RIGHT * 0.2), ReplacementTransform(line[6], answer))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S07_ex_odometer")

    # ================================================ 8. RULES ==========

    def rules_first(self):
        self.scene_start("S08_rules_first", title="Rules: Types and Bridges (1)")
        self.play(self.unpin())

        board, table = self.type_board(TYPES[:6])

        n = self.narrate(
            id="rules_01",
            text="Here are the types, each with its ready-made bridge. Synonym or antonym: means the same, or the "
                 "opposite. Degree: is a stronger form of. Part and whole: is part of. Type and category: is a type of. "
                 "Group and member: is a group of. Worker and tool: uses.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "ready-made")
        self.play(FadeIn(board[0]), FadeIn(table[0]))
        for row, spoken in zip(table[1:], ["Synonym", "Degree", "Part", "Type", "Group", "Worker"]):
            self.at_word(n, spoken, occurrence=1)
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.45)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S08_rules_first")

    def rules_second(self):
        self.scene_start("S09_rules_second", title="Rules: Types and Bridges (2)")

        board, table = self.type_board(TYPES[6:])

        n = self.narrate(
            id="rules_02",
            text="Worker and product: makes. Tool and function: is used to. Instrument and measure: measures. Cause and "
                 "effect: causes. Place or habitat: lives or works in. And lack: is a lack of.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(board[0]), FadeIn(table[0]))
        for row, spoken in zip(table[1:], ["product", "Tool", "Instrument", "Cause", "Place", "lack"]):
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
                             ("Name the TYPE of the first pair", RATIO),
                             ("Use the type's bridge sentence", WORD),
                             ("Apply it to the second pair", STEP_COLS["PREDICT"]),
                             ("Strike options of a different type", BAD)])])
        steps.arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        board = self.card(steps).move_to(UP * 0.3)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="process_01",
            text="The process. First, name the type of the first pair. Second, use the type's bridge sentence. Third, "
                 "apply it to the second pair. And fourth, strike options of a different type.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(board[0]))
        for r, (spoken, occ) in zip(steps, [("First", 1), ("Second", 1), ("Third", 1), ("fourth", 1)]):
            self.at_word(n, spoken, occurrence=occ)
            self.play(FadeIn(r, shift=RIGHT * 0.2), run_time=0.45)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S10_process")

    # ========================================== 11. HOOK, SOLVED ==========

    def hook_solved(self):
        self.scene_start("S11_hook_solved", title="Hook, Solved")
        self.play(self.pin(self.type_pin()))

        h = self.HOOK
        cx, w = self.free_area()
        manual = self.manual_card()
        fam = family_of("instrument–measures")
        kind = VGroup(pill("type", FAMILY_COL[fam], size=SMALL), text("instrument–measures", LABEL, FAMILY_COL[fam], BOLD))\
            .arrange(RIGHT, buff=0.2)
        link = BRIDGE["Instrument–measures"]
        b2 = text(f"“A barometer {link} {BLANK}.”", LABEL, INK, t2c={link: RATIO, BLANK: FOCUS})
        predict = pill("atmospheric pressure", STEP_COLS["PREDICT"], size=SMALL)
        notes = VGroup(kind, b2, predict).arrange(RIGHT, buff=0.35)
        fit_width(notes, w - 0.6)
        notes.next_to(manual, DOWN, buff=0.3).to_edge(LEFT, buff=SAFE + 0.6)
        q = OptionQuestion(h["word"], h["options"], h["key"], h["traps"], word_size=LABEL)
        fit_height(q.group, notes.get_bottom()[1] - 0.3 - (BOTTOM_Y + 1.3))
        q.group.next_to(notes, DOWN, buff=0.3).to_edge(LEFT, buff=SAFE + 0.6)
        conf = text(f"“A barometer {link} pressure.”", LABEL, INK, t2c={link: RATIO, "pressure": GOOD})
        conf.next_to(q.group, DOWN, buff=0.3).align_to(q.group, LEFT)
        self.no_overlap(manual, notes, q.group, conf)
        self.no_overlap(manual, self.pinned)
        self.no_overlap(notes, self.pinned)
        self.validator.check_in_frame(VGroup(manual, notes, q.group, conf))

        n = self.narrate(
            id="solved_01",
            text="Let's solve the hook. Read: thermometer is to temperature. Predict. The type: instrument, and what it "
                 "measures. A barometer measures, blank: atmospheric pressure.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(manual), FadeIn(q.word), FadeIn(q.rows))
        self.at_word(n, "Read")
        self.play(Indicate(manual[1][1][:3], color=WORD, scale_factor=1.05))
        self.at_word(n, "Predict")
        self.play(Indicate(manual[1][1][4:], color=FOCUS, scale_factor=1.05))
        self.at_word(n, "type")
        self.play(FadeIn(kind, shift=UP * 0.1), self.light_family(fam))
        self.at_word(n, "barometer")
        self.play(FadeIn(b2, shift=LEFT * 0.1))
        self.at_word(n, "atmospheric")
        self.play(FadeIn(predict, shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_02",
            text="Eliminate. Weather is broader: a barometer helps forecast it, but doesn't measure weather. Height is "
                 "measured by an altimeter. Rain is measured by a rain gauge.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Eliminate")
        self.play(Indicate(q.rows, color=BAD, scale_factor=1.02))
        for letter, spoken in [("a", "Weather"), ("b", "Height"), ("d", "Rain")]:
            self.at_word(n, spoken, occurrence=1)
            self.play(*q.strike(letter)[1])
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_03",
            text="Confirm: a barometer measures pressure. That's the answer.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Confirm")
        self.play(FadeIn(conf, shift=UP * 0.1))
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
            ["Missing term", "type → bridge → fill"],
            ["Choose the pair", "type of the given pair; pick the pair of the same type"],
            ["Instrument analogies", "ammeter (current), voltmeter (voltage), hygrometer (humidity), anemometer (wind "
                                     "speed)"],
        ], [4.2, 7.6], size=LABEL)
        board = self.card(table, width=SAFE_W - 0.2).move_to(UP * 0.4)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="patterns_01",
            text="Three exam patterns. A missing term: type, then bridge, then fill. Choose the pair: find the type of the "
                 "given pair, and pick the pair of the same type. And instrument analogies: know the common ones: ammeter "
                 "for current, voltmeter for voltage, hygrometer for humidity, anemometer for wind speed.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(board[0]), FadeIn(table[0]))
        for row, spoken in zip(table[1:], ["missing", "Choose", "instrument"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.45)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S12_patterns")

    # ======================================== 13. COMMON MISTAKES ==========

    def common_mistakes(self):
        self.scene_start("S13_mistakes", title="Common Mistakes")

        card_w = ZONE_W - 0.3
        pairs = [
            (self.verdict_card(False, "A broader word: weather for pressure", card_w),
             self.verdict_card(True, "Exactly what is measured", card_w)),
            (self.verdict_card(False, "Mixing worker–tool with worker–product", card_w),
             self.verdict_card(True, "uses  vs  makes", card_w)),
            (self.verdict_card(False, "Missing the “lack” type", card_w),
             self.verdict_card(True, "drought : water  =  a lack of", card_w)),
        ]
        for (wrong, right), yy in zip(pairs, [1.6, 0.05, -1.5]):
            wrong.move_to(LEFT_ZONE + UP * yy)
            right.move_to(RIGHT_ZONE + UP * yy)
        header = pill("3 mistakes", BAD, size=LABEL).move_to(UP * (CARD_TOP - 0.3))
        self.validator.check_in_frame(VGroup(header, *[c for p in pairs for c in p]))

        n = self.narrate(
            id="mistakes_01",
            text="Three common mistakes. The first is picking a broader word, like weather for pressure. The second is "
                 "mixing worker and tool with worker and product. The third is missing the lack type.",
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
        (("Hygrometer", "Humidity", "Anemometer"), ["rain", "pressure", "altitude", "wind speed"], "d",
         "instrument–measures"),
        (("Pack", "Wolves", "School"), ["fish", "students", "teachers", "books"], "a",
         "group–member;  (b) students: the other meaning of “school”"),
        (("Potter", "Clay", "Sculptor"), ["chisel", "stone", "statue", "art"], "b",
         "worker–raw material;  (a) chisel: the tool,  (c) statue: the product"),
    ]

    def practice(self):
        self.scene_start("S14_practice", title="Practice Questions")

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
            text="Your turn. One: hygrometer is to humidity, as anemometer is to what? Rain, pressure, altitude, or wind "
                 "speed? Two: pack is to wolves, as school is to what? Fish, students, teachers, or books? Three: potter "
                 "is to clay, as sculptor is to what? Chisel, stone, statue, or art?",
            voice="default",
            subtitle=True,
            pause_after=10.0,
        )
        self.play(FadeIn(board[0]))
        for ln, (spoken, first_option) in zip(lines, [("hygrometer", "Rain"), ("pack", "Fish"), ("potter", "Chisel")]):
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

        rows = VGroup(*[VGroup(analogy_line(*abc, opts["abcd".index(key)], size=LABEL), text(why, SMALL, RATIO))
                        .arrange(DOWN, buff=0.18, aligned_edge=LEFT) for abc, opts, key, why in self.PRACTICE])
        rows.arrange(DOWN, buff=0.5, aligned_edge=LEFT)
        fit_within(rows, SAFE_W, SAFE_H - 1.2)
        rows.move_to(UP * 0.3)
        self.validator.check_in_frame(rows)

        n = self.narrate(
            id="answers_01",
            text="One: wind speed. An instrument, and what it measures. Two: fish. Group and member; students is the other "
                 "meaning of school. Three: stone. Worker and raw material; the chisel is the tool, and the statue is the "
                 "product.",
            voice="default",
            subtitle=True,
        )
        for r, (spoken, why) in zip(rows, [("wind", "instrument"), ("fish", "Group"), ("stone", "Worker")]):
            self.at_word(n, spoken)
            self.play(FadeIn(r[0], shift=RIGHT * 0.2), run_time=0.5)
            self.at_word(n, why)
            self.play(FadeIn(r[1], shift=LEFT * 0.1), run_time=0.4)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S15_answers")

    # ================================================ 16. RECAP ==========

    def recap(self):
        self.scene_start("S16_recap", title="Recap Card")

        card, table = self.recap_card("Recap Card: Video 2", [[fam.capitalize(), ", ".join(t for t, _e in items)]
                                                              for fam, items in FAMILIES.items()])
        card.move_to(UP * 0.2)
        self.validator.check_in_frame(card)

        n = self.narrate(
            id="recap_01",
            text="To recap. Meaning links: synonym, antonym, degree. Structure links: part and whole, type and category, "
                 "group and member. Action links: worker and tool, worker and product, tool and function, instrument and "
                 "measure. And other links: cause and effect, place, young, lack.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(card[0]), FadeIn(table[0]))
        for row, spoken in zip(table[1:], ["Meaning", "Structure", "Action", "other"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.45)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S16_recap")

    # ================================================= 17. NEXT ==========

    def next_video(self):
        self.scene_start("S17_next", title="Next")

        two = pill("some pairs fit TWO types at once", BAD, size=LABEL)
        refine = pill("refine the bridge until only one answer fits", GOOD, size=LABEL)
        nxt = pill("Next:  Identifying the Relationship Pattern", FOCUS, size=LABEL)
        VGroup(two, refine, nxt).arrange(DOWN, buff=0.7).move_to(UP * 0.2)
        self.no_overlap(two, refine, nxt)
        self.validator.check_in_frame(VGroup(two, refine, nxt))

        n = self.narrate(
            id="next_01",
            text="Some pairs fit two types at once. Video three shows how to refine the bridge, until only one answer "
                 "fits.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "two")
        self.play(FadeIn(two, shift=DOWN * 0.1))
        self.at_word(n, "Video")
        self.play(FadeIn(nxt, scale=1.05))
        self.at_word(n, "refine")
        self.play(FadeIn(refine, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S17_next")

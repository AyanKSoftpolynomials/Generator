"""
animation.py for the LMS video generator.

Course : C-CAT - Section A - English
Module : Module 1 - Vocabulary
Lesson : Lesson 3 - Idioms & Phrases
Video  : 04 - Phrases and Their Meanings (Video 4 of 7)

Source script:
  C:\\Users\\User\\Downloads\\C-CAT_SectionA_Module1_English\\English\\Module 1 - Vocabulary\\
  Lesson 3 - Idioms & Phrases\\04 - Phrases and Their Meanings.pdf

Built on the golden-reference pattern:
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``;
  * layouts stacked with next_to and guarded with ``no_overlap``; nothing is
    ever animated onto or into another box.

The phrasal verbs and fixed phrases live in PHRASAL, MORE_PHRASAL and FIXED; sisters(pv) finds verbs that share a verb, and the tables, examples and answers are built from this data.
The "one unit" card (verb + particle together, recall the unit's meaning, strike sister-verb meanings, confirm) stays pinned top-right through the worked examples and Hook, Solved.
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

# Phrasal verbs from the script's Rules table, in table order (left, right, left, right ...).
PHRASAL = {
    "call off": "cancel", "put off": "postpone",
    "carry out": "execute", "carry on": "continue",
    "turn down": "reject", "turn up": "arrive, appear",
    "give up": "quit trying", "give in": "surrender, yield",
    "look into": "investigate", "look up to": "respect",
    "bring up": "raise a topic", "break down": "stop working, collapse",
    "run out of": "exhaust a supply", "set up": "establish",
}
MORE_PHRASAL = {"put up with": "tolerate", "put out": "extinguish"}
FIXED = {"in lieu of": "instead of", "by dint of": "by means of", "in view of": "considering",
         "on account of": "because of", "at the behest of": "at the request of"}
ALL_UNITS = {**PHRASAL, **MORE_PHRASAL, **FIXED}


def sisters(pv):
    """Other phrasal verbs built on the same verb."""
    verb = pv.split()[0]
    return [p for p in {**PHRASAL, **MORE_PHRASAL} if p.split()[0] == verb and p != pv]


def unit_chips(pv, size=LABEL):
    """verb + particle = one unit."""
    verb, particle = pv.split(" ", 1)
    return VGroup(pill(verb, WORD, size=size), text("+", size, MUTED), pill(particle, RATIO, size=size))\
        .arrange(RIGHT, buff=0.2)


class PhrasesAndMeaningsVideo(LMSScene):
    lesson_title = "Phrases and Their Meanings"

    def construct(self):
        self.camera.background_color = BG

        self.lesson_intro()
        self.hook()
        self.concept()
        self.why_you_need_it()
        self.analogy()
        self.example_put_off()
        self.example_put_up_with()
        self.example_turn_down()
        self.example_in_lieu_of()
        self.rules_phrasal()
        self.rules_fixed()
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

    def unit_pin(self):
        return self.steps_pin("one unit", [("verb + particle TOGETHER", WORD),
                                           ("recall the UNIT's meaning", STEP_COLS["PREDICT"]),
                                           ("strike sister-verb meanings", BAD), ("confirm in the sentence", GOOD)])

    def calendar_card(self, fill=None):
        head = text("CALENDAR  ·  notification", SMALL, RATIO, BOLD)
        line = text(f"“Friday's client review has been {fill or 'called off'}.”", BODY, INK,
                    t2c={fill or "called off": GOOD if fill else WORD})
        cx, w = self.free_area()
        card = self.card(VGroup(head, fit_width(line, w - 1.4)).arrange(DOWN, buff=0.2, aligned_edge=LEFT),
                         width=min(w - 0.2, SAFE_W - 0.4))
        return card.move_to(RIGHT * cx + UP * (CARD_TOP - card.height / 2))

    def phrase_example(self, sentence, phrase, shown_meaning, rewritten, note=None):
        """Sentence, its unit and meaning, an optional note, and the sentence rewritten in plain words."""
        cx, w = self.free_area()
        sent = fitted_text(f"“{sentence}”", w - 0.8, BODY, INK, NORMAL, max_lines=2)
        unit = unit_chips(phrase) if phrase in {**PHRASAL, **MORE_PHRASAL} else pill(phrase, WORD, size=LABEL)
        mean = VGroup(text("=", LABEL, MUTED), pill(shown_meaning, GOOD, size=LABEL)).arrange(RIGHT, buff=0.25)
        row = VGroup(unit, mean).arrange(RIGHT, buff=0.3)
        plain = fitted_text(f"“{rewritten}”", w - 0.8, LABEL, GOOD, NORMAL, max_lines=2)
        parts = [sent, row] + ([text(note, SMALL, MUTED)] if note else []) + [plain]
        block = VGroup(*parts).arrange(DOWN, buff=0.5, aligned_edge=LEFT)
        fit_height(block, SAFE_H - 1.6)
        self.place_free(block, y=0.1)
        self.no_overlap(*parts)
        self.validator.check_in_frame(block)
        return sent, unit, mean, (parts[2] if note else None), plain

    # ========================================= 0. LESSON INTRO ==========

    def lesson_intro(self):
        self.scene_start("S00_intro", title="Lesson Introduction")

        crumb = self.breadcrumb("English · Module 1 Vocabulary", "Lesson 3 · Idioms & Phrases", "Video 4")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        prereq = pill("prerequisite page: phrasal verbs", MUTED, size=SMALL)
        rows = VGroup(VGroup(pill("idiom", SECOND, size=LABEL), text("a fixed PICTURE", LABEL, INK))
                      .arrange(RIGHT, buff=0.3),
                      VGroup(pill("phrasal verb", WORD, size=LABEL), text("a fixed VERB + PARTICLE unit", LABEL, INK))
                      .arrange(RIGHT, buff=0.3)).arrange(DOWN, buff=0.35, aligned_edge=LEFT)
        whole = pill("both are learned as WHOLE units", GOOD, size=LABEL)
        VGroup(prereq, rows, whole).arrange(DOWN, buff=0.55).move_to(DOWN * 0.1)
        self.no_overlap(crumb, prereq, rows, whole)
        self.validator.check_in_frame(VGroup(crumb, prereq, rows, whole))

        n = self.narrate(
            id="intro_01",
            text="The prerequisite page introduced phrasal verbs. Idioms, from videos one to three, are fixed pictures; "
                 "phrasal verbs are fixed verb-plus-particle units. Both must be learned as whole units.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.at_word(n, "prerequisite")
        self.play(FadeIn(prereq))
        self.at_word(n, "pictures")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "verb-plus-particle")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.at_word(n, "whole")
        self.play(FadeIn(whole, shift=UP * 0.1))
        self.wait_for_narration(n)

        title = fitted_text("Phrases and Their Meanings", SAFE_W, 72, INK, BOLD)
        underline = Line(LEFT, RIGHT, color=SECOND, stroke_width=5).set_width(title.width * 0.6)
        VGroup(title, underline).arrange(DOWN, buff=0.2).move_to(UP * 0.2)
        goals = [("Learn high-frequency phrasal verbs and fixed phrases", GOOD),
                 ("Tell apart phrasal verbs that share a verb but differ in particle", BAD)]
        grows = VGroup(*[VGroup(pill(str(i + 1), c, size=SMALL), fitted_text(s_, SAFE_W - 2.4, BODY, INK))
                         .arrange(RIGHT, buff=0.35) for i, (s_, c) in enumerate(goals)])
        grows.arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        heading = text("By the end of this video, you will:", LABEL, MUTED, BOLD)
        objectives = self.card(VGroup(heading, grows).arrange(DOWN, buff=0.4, aligned_edge=LEFT))
        small_title = title.copy().scale(0.6)
        small_title.next_to(crumb, DOWN, buff=0.3)
        objectives.next_to(small_title, DOWN, buff=0.35)
        self.validator.check_in_frame(VGroup(crumb, small_title, objectives))
        n = self.narrate(
            id="intro_02",
            text="This video is phrases and their meanings. By the end, you'll learn high-frequency phrasal verbs and fixed "
                 "phrases, and tell apart phrasal verbs that share a verb but differ in particle.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(VGroup(prereq, rows, whole), shift=UP * 0.3))
        self.at_word(n, "phrases", occurrence=1)
        self.play(Write(title), run_time=1.1)
        self.play(GrowFromCenter(underline))
        self.at_word(n, "By")
        self.play(FadeOut(underline), ReplacementTransform(title, small_title), run_time=0.8)
        self.play(FadeIn(objectives[0]), FadeIn(heading))
        for row_, spoken in zip(grows, ["learn", "tell"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row_, shift=RIGHT * 0.2), run_time=0.5)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_intro")

    # ================================================= 1. HOOK ==========

    HOOK = dict(word="called off", options=["postponed", "cancelled", "shortened", "moved online"], key="b",
                traps={"a": "= put off: the sister trap", "c": "unrelated", "d": "unrelated"})

    def hook(self):
        self.scene_start("S01_hook", title="Hook")

        h = self.HOOK
        assert PHRASAL["call off"] == "cancel" and PHRASAL["put off"] == "postpone"
        note = self.calendar_card()
        replies = VGroup(*[pill("“OK, what's the new date?”", MUTED, size=SMALL) for _ in range(3)])\
            .arrange(RIGHT, buff=0.3)
        fit_width(replies, SAFE_W - 1.0)
        ask = pill("are they right to ask?", FOCUS, size=LABEL)
        q = OptionQuestion(h["word"], h["options"], h["key"], h["traps"])
        opts = q.rows.copy().arrange(RIGHT, buff=0.8)
        fit_width(opts, SAFE_W)
        replies.next_to(note, DOWN, buff=0.45)
        ask.next_to(replies, DOWN, buff=0.4)
        opts.next_to(ask, DOWN, buff=0.5)
        self.no_overlap(note, replies, ask, opts)
        self.validator.check_in_frame(VGroup(note, replies, ask, opts))

        n = self.narrate(
            id="hook_01",
            text="Your calendar pings: Friday's client review has been called off. Half the team replies, asking for the "
                 "new date. Are they right to?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "pings")
        self.play(FadeIn(note, shift=DOWN * 0.2))
        self.at_word(n, "replies")
        self.play(LaggedStart(*[FadeIn(r, shift=UP * 0.1) for r in replies], lag_ratio=0.25))
        self.at_word(n, "right")
        self.play(FadeIn(ask, shift=UP * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_02",
            text="Does called off mean postponed, cancelled, shortened, or moved online?",
            voice="default",
            subtitle=True,
            pause_after=3.0,
        )
        for row, spoken in zip(opts, ["postponed", "cancelled", "shortened", "moved"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=UP * 0.15), run_time=0.35)
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        self.clear_stage()
        self.scene_end("S01_hook")

    # ============================================== 2. CONCEPT ==========

    def concept(self):
        self.scene_start("S02_concept", title="The Concept")

        head = VGroup(pill("verb", WORD, size=BODY), text("+", BODY, MUTED), pill("particle", RATIO, size=BODY),
                      text("=", BODY, MUTED), pill("phrasal verb: ONE unit", GOOD, size=BODY)).arrange(RIGHT, buff=0.3)
        head.move_to(UP * (CARD_TOP - head.height / 2))
        particles = VGroup(*[pill(p, RATIO, size=SMALL) for p in ["off", "up", "down", "out", "into", "with"]])\
            .arrange(RIGHT, buff=0.25)
        particles.next_to(head, DOWN, buff=0.35)
        guess = text("the meaning can't be guessed from the parts", LABEL, MUTED).next_to(particles, DOWN, buff=0.35)
        units = VGroup(*[VGroup(unit_chips(pv), text("=  " + PHRASAL[pv], LABEL, GOOD)).arrange(RIGHT, buff=0.3)
                         for pv in ["call off", "put off", "bring up", "turn down"]])
        units.arrange_in_grid(rows=2, cols=2, buff=(1.0, 0.35), cell_alignment=LEFT)
        fit_width(units, SAFE_W - 0.6)
        units.next_to(guess, DOWN, buff=0.45)
        self.no_overlap(head, particles, guess, units)
        self.validator.check_in_frame(VGroup(head, particles, guess, units))

        n = self.narrate(
            id="concept_01",
            text="A phrasal verb combines a verb with a particle: off, up, down, out, into, with. The combination often "
                 "has a meaning you can't guess from the parts. Call off means cancel. Put off means postpone. Bring up "
                 "means raise a topic. Turn down means reject.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "combines")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "off", occurrence=1)
        self.play(LaggedStart(*[FadeIn(p, shift=UP * 0.1) for p in particles], lag_ratio=0.2))
        self.at_word(n, "guess")
        self.play(FadeIn(guess, shift=UP * 0.1))
        for u, spoken in zip(units, ["Call", "Put", "Bring", "Turn"]):
            self.at_word(n, spoken)
            self.play(FadeIn(u, shift=RIGHT * 0.2), run_time=0.4)
        self.wait_for_narration(n)

        # Sister traps.
        same_verb = VGroup(text("same VERB, different particle", LABEL, BAD, BOLD),
                           *[VGroup(unit_chips(pv, SMALL), text("=  " + ALL_UNITS[pv], LABEL, INK))
                             .arrange(RIGHT, buff=0.25) for pv in ["put off", "put up with", "put out"]])\
            .arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        same_part = VGroup(text("same PARTICLE, different verb", LABEL, BAD, BOLD),
                           *[VGroup(unit_chips(pv, SMALL), text("=  " + ALL_UNITS[pv], LABEL, INK))
                             .arrange(RIGHT, buff=0.25) for pv in ["call off", "put off"]])\
            .arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        traps = VGroup(same_verb, same_part).arrange(RIGHT, buff=1.0, aligned_edge=UP)
        trap_head = pill("the exam trap: sister verbs", BAD, size=LABEL)
        trap_block = VGroup(trap_head, traps).arrange(DOWN, buff=0.6)
        fit_width(trap_block, SAFE_W).move_to(UP * 0.3)
        assert sisters("put off") == ["put up with", "put out"]
        self.validator.check_in_frame(trap_block)
        n = self.narrate(
            id="concept_02",
            text="The exam trap is the same verb with a different particle: put off, postpone; put up with, tolerate; put "
                 "out, extinguish. Or the same particle with a different verb: call off, cancel, and put off, postpone.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(VGroup(head, particles, guess, units)))
        self.at_word(n, "trap")
        self.play(FadeIn(trap_head, shift=DOWN * 0.1), FadeIn(same_verb[0]))
        for r, (spoken, occ) in zip(same_verb[1:], [("postpone", 1), ("tolerate", 1), ("extinguish", 1)]):
            self.at_word(n, spoken, occurrence=occ)
            self.play(FadeIn(r, shift=RIGHT * 0.2), run_time=0.4)
        self.at_word(n, "particle", occurrence=2)
        self.play(FadeIn(same_part[0]))
        for r, (spoken, occ) in zip(same_part[1:], [("cancel", 1), ("postpone", 2)]):
            self.at_word(n, spoken, occurrence=occ)
            self.play(FadeIn(r, shift=RIGHT * 0.2), run_time=0.4)
        self.wait_for_narration(n)

        # Fixed phrases.
        fixed_head = pill("fixed phrases work the same way", SECOND, size=LABEL)
        fixed_head.move_to(UP * (CARD_TOP - fixed_head.height / 2))
        fixed = VGroup(*[VGroup(pill(p, WORD, size=LABEL), text("=  " + m, LABEL, GOOD)).arrange(RIGHT, buff=0.3)
                         for p, m in FIXED.items()]).arrange(DOWN, buff=0.25, aligned_edge=LEFT)
        formal = pill("seen in formal writing, and in phrase-meaning questions", FOCUS, size=SMALL)
        body = VGroup(fixed, formal).arrange(DOWN, buff=0.45)
        fit_within(body, SAFE_W, SAFE_H - fixed_head.height - 1.5)
        body.next_to(fixed_head, DOWN, buff=0.45)
        self.no_overlap(fixed_head, fixed, formal)
        self.validator.check_in_frame(VGroup(fixed_head, body))
        n = self.narrate(
            id="concept_03",
            text="Fixed phrases work similarly. In lieu of means instead of. By dint of: by means of. In view of: "
                 "considering. On account of: because of. At the behest of: at the request of. These appear in formal "
                 "writing, and in phrase-meaning questions.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(trap_block))
        self.at_word(n, "Fixed")
        self.play(FadeIn(fixed_head, shift=DOWN * 0.2))
        for r, spoken in zip(fixed, ["lieu", "dint", "view", "account", "behest"]):
            self.at_word(n, spoken)
            self.play(FadeIn(r, shift=RIGHT * 0.2), run_time=0.4)
        self.at_word(n, "formal")
        self.play(FadeIn(formal, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_concept")

    # ======================================== 3. WHY YOU NEED IT ==========

    def why_you_need_it(self):
        self.scene_start("S03_why", title="Why You Need It")

        emails = pill("phrasal verbs are everywhere in workplace emails", WORD, size=LABEL)
        cost = pill("postponed  ≠  cancelled", BAD, size=BODY)
        exams = VGroup(*[pill(t, RATIO, size=LABEL) for t in ["meaning questions", "sentence completion",
                                                             "error spotting"]]).arrange(RIGHT, buff=0.4)
        group = VGroup(emails, cost, exams).arrange(DOWN, buff=0.7)
        fit_width(group, SAFE_W).move_to(UP * 0.3)
        self.no_overlap(emails, cost, exams)
        self.validator.check_in_frame(group)

        n = self.narrate(
            id="why_01",
            text="Phrasal verbs are everywhere in workplace emails, and misreading one has real consequences: postponed "
                 "isn't cancelled. In exams, they appear in meaning questions, sentence completion and error spotting.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "emails")
        self.play(FadeIn(emails, shift=DOWN * 0.1))
        self.at_word(n, "postponed")
        self.play(FadeIn(cost, scale=1.1))
        self.at_word(n, "exams")
        self.play(LaggedStart(*[FadeIn(e, shift=UP * 0.1) for e in exams], lag_ratio=0.3))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_why")

    # ============================================== 4. ANALOGY ==========

    def analogy(self):
        self.scene_start("S04_analogy", title="The Analogy")

        car_buttons = VGroup(*[pill(b, RATIO, size=LABEL) for b in ["lock", "unlock", "open boot"]])\
            .arrange(DOWN, buff=0.25)
        car = self.card(VGroup(text("one car key", LABEL, WORD, BOLD), car_buttons).arrange(DOWN, buff=0.35), width=3.8)
        verb_rows = VGroup(*[VGroup(pill(pv.split(" ", 1)[1], RATIO, size=LABEL), text("=  " + ALL_UNITS[pv], LABEL, GOOD))
                             .arrange(RIGHT, buff=0.3) for pv in ["put off", "put up with", "put out"]])\
            .arrange(DOWN, buff=0.25, aligned_edge=LEFT)
        verb = self.card(VGroup(text("the verb:  PUT", LABEL, WORD, BOLD), verb_rows).arrange(DOWN, buff=0.35), width=5.6)
        pair = VGroup(car, verb).arrange(RIGHT, buff=0.9, aligned_edge=UP)
        check = pill("the verb is the key  ·  the particle is the button:  check which button", FOCUS, size=SMALL)
        block = VGroup(pair, check).arrange(DOWN, buff=0.5)
        fit_within(block, SAFE_W, SAFE_H - 1.4)
        block.move_to(UP * 0.3)
        self.no_overlap(car, verb)
        self.no_overlap(pair, check)
        self.validator.check_in_frame(block)

        n = self.narrate(
            id="analogy_01",
            text="One key, several buttons, completely different actions. The verb is the key; the particle is the button. "
                 "Check which button was pressed.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "key", occurrence=1)
        self.play(FadeIn(car[0]), FadeIn(car[1][0]))
        self.at_word(n, "buttons")
        self.play(LaggedStart(*[FadeIn(b, shift=UP * 0.1) for b in car_buttons], lag_ratio=0.25))
        self.at_word(n, "verb")
        self.play(FadeIn(verb[0]), FadeIn(verb[1][0]))
        self.at_word(n, "particle")
        self.play(LaggedStart(*[FadeIn(r[0], shift=UP * 0.1) for r in verb_rows], lag_ratio=0.25))
        self.at_word(n, "Check")
        self.play(FadeIn(check, shift=UP * 0.1), LaggedStart(*[FadeIn(r[1], shift=LEFT * 0.1) for r in verb_rows],
                                                             lag_ratio=0.25))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_analogy")

    # ======================================== 5-8. WORKED EXAMPLES ==========

    def example_put_off(self):
        self.scene_start("S05_ex_put_off", title="Worked Example 1")
        self.play(self.pin(self.unit_pin()))

        sent, unit, mean, _note, plain = self.phrase_example(
            "The event was put off until next month.", "put off", PHRASAL["put off"],
            "The event was postponed until next month.")

        n = self.narrate(
            id="ex1_01",
            text="The event was put off until next month. Verb and particle together: put off. The unit means postpone. "
                 "So the event was postponed.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "event", occurrence=1)
        self.play(FadeIn(sent, shift=DOWN * 0.1))
        self.at_word(n, "together")
        self.play(FadeIn(unit, shift=RIGHT * 0.1), self.pin_step(0, color=WORD))
        self.at_word(n, "unit")
        self.play(FadeIn(mean, shift=LEFT * 0.1), self.pin_step(1, color=STEP_COLS["PREDICT"]))
        self.at_word(n, "postponed")
        self.play(FadeIn(plain, shift=UP * 0.1), self.pin_step(3, color=GOOD))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_ex_put_off")

    def example_put_up_with(self):
        self.scene_start("S06_ex_put_up_with", title="Worked Example 2")

        sent, unit, mean, note, plain = self.phrase_example(
            "I can't put up with this noise.", "put up with", MORE_PHRASAL["put up with"],
            "I can't tolerate this noise.", note="same verb as “put off”, different particle")

        n = self.narrate(
            id="ex2_01",
            text="I can't put up with this noise. Same verb, different particle: put up with. The unit means tolerate. I "
                 "can't tolerate this noise.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "can't", occurrence=1)
        self.play(FadeIn(sent, shift=DOWN * 0.1))
        self.at_word(n, "Same")
        self.play(FadeIn(unit, shift=RIGHT * 0.1), FadeIn(note), self.pin_step(0, color=WORD))
        self.at_word(n, "unit")
        self.play(FadeIn(mean, shift=LEFT * 0.1), self.pin_step(1, color=STEP_COLS["PREDICT"]))
        self.at_word(n, "can't", occurrence=2)
        self.play(FadeIn(plain, shift=UP * 0.1), self.pin_step(3, color=GOOD))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_ex_put_up_with")

    def example_turn_down(self):
        self.scene_start("S07_ex_turn_down", title="Worked Example 3")

        assert sisters("turn down") == ["turn up"]
        sent, unit, mean, note, plain = self.phrase_example(
            "She turned down the offer.", "turn down", PHRASAL["turn down"], "She rejected the offer.",
            note="sister:  turn up = arrive, appear")

        n = self.narrate(
            id="ex3_01",
            text="She turned down the offer. The unit is turn down, and it means reject. She rejected the offer. Its "
                 "sister, turn up, means arrive.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "turned")
        self.play(FadeIn(sent, shift=DOWN * 0.1))
        self.at_word(n, "unit")
        self.play(FadeIn(unit, shift=RIGHT * 0.1), self.pin_step(0, color=WORD))
        self.at_word(n, "reject")
        self.play(FadeIn(mean, shift=LEFT * 0.1), self.pin_step(1, color=STEP_COLS["PREDICT"]))
        self.at_word(n, "rejected")
        self.play(FadeIn(plain, shift=UP * 0.1), self.pin_step(3, color=GOOD))
        self.at_word(n, "sister")
        self.play(FadeIn(note, shift=UP * 0.1), self.pin_step(2, color=BAD))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S07_ex_turn_down")

    def example_in_lieu_of(self):
        self.scene_start("S08_ex_in_lieu_of", title="Worked Example 4")

        sent, unit, mean, note, plain = self.phrase_example(
            "In lieu of a bonus, staff got extra leave.", "in lieu of", FIXED["in lieu of"],
            "Instead of a bonus, staff got extra leave.", note="a fixed phrase:  lieu = place")

        n = self.narrate(
            id="ex4_01",
            text="In lieu of a bonus, staff got extra leave. In lieu of is a fixed phrase: lieu means place. As a unit, it "
                 "means instead of. Instead of a bonus, staff got extra leave.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "bonus", occurrence=1)
        self.play(FadeIn(sent, shift=DOWN * 0.1))
        self.at_word(n, "fixed")
        self.play(FadeIn(unit, shift=RIGHT * 0.1), FadeIn(note), self.pin_step(0, color=WORD))
        self.at_word(n, "unit")
        self.play(FadeIn(mean, shift=LEFT * 0.1), self.pin_step(1, color=STEP_COLS["PREDICT"]))
        self.at_word(n, "bonus", occurrence=2)
        self.play(FadeIn(plain, shift=UP * 0.1), self.pin_step(3, color=GOOD))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S08_ex_in_lieu_of")

    # ================================================ 9. RULES ==========

    def rules_phrasal(self):
        self.scene_start("S09_rules_phrasal", title="Rules: Phrasal Verbs")
        self.play(self.unpin())

        items = list(PHRASAL.items())
        table = self.table_rows(["Phrasal verb", "Meaning", "Phrasal verb", "Meaning"],
                                [[items[i][0], items[i][1], items[i + 1][0], items[i + 1][1]]
                                 for i in range(0, len(items), 2)], [2.7, 3.3, 2.7, 3.3], size=LABEL)
        for row in table[1:]:
            row[0].set_color(WORD)
            row[2].set_color(WORD)
        board = self.card(table, width=SAFE_W - 0.2)
        fit_height(board, SAFE_H - 1.2)
        board.move_to(UP * 0.3)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="rules_01",
            text="Here are the high-frequency phrasal verbs. Call off: cancel. Put off: postpone. Carry out: execute. Carry "
                 "on: continue. Turn down: reject. Turn up: arrive. Give up: quit trying. Give in: surrender.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "high-frequency")
        self.play(FadeIn(board[0]), FadeIn(table[0]))
        for row, (left, left_occ, right, right_occ) in zip(table[1:5], [("Call", 1, "Put", 1), ("Carry", 1, "Carry", 2),
                                                                        ("Turn", 1, "Turn", 2), ("Give", 1, "Give", 2)]):
            self.at_word(n, left, occurrence=left_occ)
            self.play(FadeIn(row[:2], shift=RIGHT * 0.2), run_time=0.4)
            self.at_word(n, right, occurrence=right_occ)
            self.play(FadeIn(row[2:], shift=RIGHT * 0.2), run_time=0.4)
        self.wait_for_narration(n)

        n = self.narrate(
            id="rules_02",
            text="Look into: investigate. Look up to: respect. Bring up: raise a topic. Break down: stop working. Run out "
                 "of: exhaust a supply. Set up: establish.",
            voice="default",
            subtitle=True,
        )
        for row, (left, left_occ, right, right_occ) in zip(table[5:], [("Look", 1, "Look", 2), ("Bring", 1, "Break", 1),
                                                                       ("Run", 1, "Set", 1)]):
            self.at_word(n, left, occurrence=left_occ)
            self.play(FadeIn(row[:2], shift=RIGHT * 0.2), run_time=0.4)
            self.at_word(n, right, occurrence=right_occ)
            self.play(FadeIn(row[2:], shift=RIGHT * 0.2), run_time=0.4)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S09_rules_phrasal")

    def rules_fixed(self):
        self.scene_start("S10_rules_fixed", title="Rules: Fixed Phrases")

        four = list(FIXED.items())[:4]
        table = self.table_rows(["Fixed phrase", "Meaning"], [[p, m] for p, m in four], [5.6, 5.6], size=BODY)
        for row in table[1:]:
            row[0].set_color(WORD)
        board = self.card(table, width=SAFE_W - 0.4).move_to(UP * 0.4)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="rules_03",
            text="And four fixed phrases. In lieu of: instead of. By dint of: by means of. In view of: considering. On "
                 "account of: because of.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "four")
        self.play(FadeIn(board[0]), FadeIn(table[0]))
        for row, spoken in zip(table[1:], ["lieu", "dint", "view", "account"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.45)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S10_rules_fixed")

    # ============================================= 11. PROCESS ==========

    def process(self):
        self.scene_start("S11_process", title="The Process")

        steps = VGroup(*[VGroup(pill(str(i + 1), c, size=SMALL), fitted_text(s_, SAFE_W - 2.2, BODY, INK))
                         .arrange(RIGHT, buff=0.3) for i, (s_, c) in enumerate([
                             ("Identify the verb AND the particle together", WORD),
                             ("Recall the unit's meaning, not the verb's", STEP_COLS["PREDICT"]),
                             ("Eliminate meanings of the same verb with another particle", BAD),
                             ("Confirm in the sentence", GOOD)])])
        steps.arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        board = self.card(steps).move_to(UP * 0.3)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="process_01",
            text="The process. First, identify the verb and the particle together. Second, recall the unit's meaning, not "
                 "the verb's. Third, eliminate meanings that belong to the same verb with another particle. And fourth, "
                 "confirm in the sentence.",
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
        self.play(self.pin(self.unit_pin()))

        h = self.HOOK
        note = self.calendar_card()
        q = OptionQuestion(h["word"], h["options"], h["key"], h["traps"], word_size=LABEL)
        fit_height(q.group, note.get_bottom()[1] - 0.4 - (BOTTOM_Y + 0.6))
        q.group.next_to(note, DOWN, buff=0.4).to_edge(LEFT, buff=SAFE + 0.6)
        pin_left = self.pinned.get_left()[0]
        predict = VGroup(unit_chips("call off", SMALL), text("=  " + PHRASAL["call off"], LABEL, GOOD))\
            .arrange(RIGHT, buff=0.25)
        fit_width(predict, pin_left - 0.3 - (q.word.get_right()[0] + 0.4))
        predict.next_to(q.word, RIGHT, buff=0.4)
        fixed = self.calendar_card(fill="cancelled")
        answer_row = q.row(h["key"])
        verdict = pill("no new date to ask for", GOOD, size=SMALL)
        fit_width(verdict, pin_left - 0.3 - answer_row.get_right()[0] - 0.5)
        verdict.next_to(answer_row, RIGHT, buff=0.4)
        self.no_overlap(note, q.group)
        self.no_overlap(note, self.pinned)
        self.no_overlap(q.rows, predict)
        self.no_overlap(predict, self.pinned)
        self.validator.check_in_frame(VGroup(note, q.group, predict, verdict))

        n = self.narrate(
            id="solved_01",
            text="Let's solve the hook. Read: called off. Predict: call off means cancel.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(note), FadeIn(q.word), FadeIn(q.rows))
        self.at_word(n, "Read")
        self.play(Indicate(q.word, color=WORD, scale_factor=1.08), FadeIn(predict[0], shift=LEFT * 0.1),
                  self.pin_step(0, color=WORD))
        self.at_word(n, "Predict")
        self.play(FadeIn(predict[1], shift=LEFT * 0.1), self.pin_step(1, color=STEP_COLS["PREDICT"]))
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_02",
            text="Eliminate. Postponed is the meaning of put off: the trap. Shortened and moved online are unrelated.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Eliminate")
        self.play(self.pin_step(2, color=BAD))
        self.at_word(n, "Postponed")
        self.play(*q.strike("a")[1])
        self.at_word(n, "Shortened")
        self.play(*q.strike("c")[1], *q.strike("d")[1])
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_03",
            text="Confirm: Friday's client review has been cancelled. That's the answer. There's no new date to ask for.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Confirm")
        self.play(ReplacementTransform(note, fixed), self.pin_step(3, color=GOOD))
        self.at_word(n, "answer")
        self.play(*q.confirm()[1])
        self.at_word(n, "date")
        self.play(FadeIn(verdict, shift=LEFT * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S12_hook_solved")

    # ========================================== 13. EXAM PATTERNS ==========

    def exam_patterns(self):
        self.scene_start("S13_patterns", title="Exam Patterns and Solving Models")
        self.play(self.unpin())

        table = self.table_rows(["Pattern", "Solving model"], [
            ["Meaning of a phrasal verb", "verb + particle as one unit; watch for sister verbs"],
            ["Fill the particle", f"“The meeting was called {'___'}” → off: use the meaning to pick the particle"],
            ["Fixed phrase meaning", "learn as a unit; decode “lieu” = place"],
        ], [4.6, 7.2], size=LABEL)
        board = self.card(table, width=SAFE_W - 0.2).move_to(UP * 0.4)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="patterns_01",
            text="Three exam patterns. Meaning of a phrasal verb: treat verb plus particle as one unit, and watch for "
                 "sister verbs. Fill the particle: the meeting was called, blank. Use the meaning to pick the particle: "
                 "off. And fixed phrase meaning: learn it as a unit, and decode lieu as place.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "patterns")
        self.play(FadeIn(board[0]), FadeIn(table[0]))
        self.at_word(n, "Meaning")
        self.play(FadeIn(table[1], shift=RIGHT * 0.2), run_time=0.45)
        self.at_word(n, "Fill")
        self.play(FadeIn(table[2][0], shift=RIGHT * 0.2), run_time=0.45)
        self.at_word(n, "pick")
        self.play(FadeIn(table[2][1], shift=LEFT * 0.1), run_time=0.45)
        self.at_word(n, "fixed")
        self.play(FadeIn(table[3], shift=RIGHT * 0.2), run_time=0.45)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S13_patterns")

    # ======================================== 14. COMMON MISTAKES ==========

    def common_mistakes(self):
        self.scene_start("S14_mistakes", title="Common Mistakes")

        card_w = ZONE_W - 0.3
        pairs = [
            (self.verdict_card(False, "“call off” = postpone", card_w),
             self.verdict_card(True, "call off = cancel;  put off = postpone", card_w)),
            (self.verdict_card(False, "“give up” = “give in”", card_w),
             self.verdict_card(True, "give up: quit trying;  give in: surrender", card_w)),
            (self.verdict_card(False, "Guessing from the verb alone", card_w),
             self.verdict_card(True, "Verb + particle = one unit", card_w)),
        ]
        for (wrong, right), yy in zip(pairs, [1.6, 0.05, -1.5]):
            wrong.move_to(LEFT_ZONE + UP * yy)
            right.move_to(RIGHT_ZONE + UP * yy)
        header = pill("3 mistakes", BAD, size=LABEL).move_to(UP * (CARD_TOP - 0.3))
        self.validator.check_in_frame(VGroup(header, *[c for p in pairs for c in p]))

        n = self.narrate(
            id="mistakes_01",
            text="Three common mistakes. The first is treating call off as postpone. The second is confusing give up and "
                 "give in. The third is guessing from the verb alone.",
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
        ("The machine broke down on the way.", "broke down", "break down",
         ["stopped working", "was destroyed", "was dismantled", "slowed down"], "a"),
        ("We have run out of printer ink.", "run out of", "run out of", ["spilled", "bought", "wasted", "used all of"], "d"),
        ("He succeeded by dint of hard work.", "by dint of", "by dint of",
         ["in spite of", "instead of", "by means of", "because of luck"], "c"),
    ]

    def practice(self):
        self.scene_start("S15_practice", title="Practice Questions")

        head = pill("What does the highlighted phrase mean?", SECOND, size=LABEL)
        lines = VGroup(*[VGroup(VGroup(pill(str(i + 1), FOCUS, size=SMALL),
                                       text(f"“{sent}”", LABEL, INK, t2c={shown: WORD})).arrange(RIGHT, buff=0.35),
                                text("   ".join(f"({l}) {o}" for l, o in zip("abcd", opts)), LABEL, INK))
                         .arrange(DOWN, buff=0.2, aligned_edge=LEFT)
                         for i, (sent, shown, _unit, opts, _k) in enumerate(self.PRACTICE)])
        lines.arrange(DOWN, buff=0.4, aligned_edge=LEFT)
        board = self.card(VGroup(head, lines).arrange(DOWN, buff=0.4, aligned_edge=LEFT), color=FOCUS)
        fit_within(board, SAFE_W, SAFE_H - 1.2)
        board.move_to(UP * 0.4)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="practice_01",
            text="Your turn: what does the phrase mean? One: the machine broke down on the way. Stopped working, was "
                 "destroyed, was dismantled, or slowed down? Two: we have run out of printer ink. Spilled, bought, wasted, "
                 "or used all of? Three: he succeeded by dint of hard work. In spite of, instead of, by means of, or "
                 "because of luck?",
            voice="default",
            subtitle=True,
            pause_after=10.0,
        )
        self.play(FadeIn(board[0]), FadeIn(head))
        for ln, (spoken, first_option) in zip(lines, [("machine", "Stopped"), ("printer", "Spilled"),
                                                     ("succeeded", "spite")]):
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
        for i, (sent, shown, unit, opts, key) in enumerate(self.PRACTICE):
            assert unit in ALL_UNITS
            rows.add(VGroup(pill(str(i + 1), FOCUS, size=SMALL), pill(shown, WORD, size=LABEL), text("=", LABEL, MUTED),
                            pill(f"({key}) {opts['abcd'.index(key)]}", GOOD, size=LABEL)).arrange(RIGHT, buff=0.3))
        assert self.PRACTICE[2][3][2] == FIXED["by dint of"]
        opposite = text("(a) in spite of: the opposite relationship", SMALL, BAD)
        rows.arrange(DOWN, buff=0.6, aligned_edge=LEFT)
        block = VGroup(rows, opposite).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        fit_within(block, SAFE_W, SAFE_H - 1.2)
        block.move_to(UP * 0.3)
        self.validator.check_in_frame(block)

        n = self.narrate(
            id="answers_01",
            text="One: stopped working. Two: used all of. Three: by means of. In spite of is the opposite relationship.",
            voice="default",
            subtitle=True,
        )
        for r, spoken in zip(rows, ["stopped", "used", "means"]):
            self.at_word(n, spoken)
            self.play(FadeIn(r, shift=RIGHT * 0.2), run_time=0.5)
        self.at_word(n, "spite")
        self.play(FadeIn(opposite, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S16_answers")

    # ================================================ 17. RECAP ==========

    def recap(self):
        self.scene_start("S17_recap", title="Recap Card")

        card, table = self.recap_card("Recap Card: Video 4", [
            ["Unit", "verb + particle = one meaning"],
            ["Sister traps", "call off (cancel) vs put off (postpone);  give up vs give in"],
            ["Fixed phrases", ", ".join(list(FIXED)[:4])],
        ])
        card.move_to(UP * 0.2)
        self.validator.check_in_frame(card)

        n = self.narrate(
            id="recap_01",
            text="To recap. Verb plus particle is one unit, with one meaning. Watch the sister traps: call off, cancel, "
                 "against put off, postpone; and give up against give in. And learn the fixed phrases: in lieu of, by "
                 "dint of, in view of, on account of.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(card[0]), FadeIn(table[0]))
        for row, spoken in zip(table[1:], ["unit", "sister", "fixed"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.45)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S17_recap")

    # ================================================= 18. NEXT ==========

    def next_video(self):
        self.scene_start("S18_next", title="Next")

        misused = pill("idioms and phrases that are misused very often", BAD, size=LABEL)
        sounds = pill("the wrong version starts to sound right", RATIO, size=LABEL)
        nxt = pill("Next:  Commonly Confused Idioms", FOCUS, size=LABEL)
        VGroup(misused, sounds, nxt).arrange(DOWN, buff=0.7).move_to(UP * 0.2)
        self.no_overlap(misused, sounds, nxt)
        self.validator.check_in_frame(VGroup(misused, sounds, nxt))

        n = self.narrate(
            id="next_01",
            text="Some idioms and phrases are misused so often that the wrong version sounds right. Video five sorts them "
                 "out.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "misused")
        self.play(FadeIn(misused, shift=DOWN * 0.1))
        self.at_word(n, "wrong")
        self.play(FadeIn(sounds, shift=UP * 0.1))
        self.at_word(n, "Video")
        self.play(FadeIn(nxt, scale=1.05))
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S18_next")

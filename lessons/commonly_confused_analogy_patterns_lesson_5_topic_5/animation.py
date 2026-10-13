"""
animation.py for the LMS video generator.

Course : C-CAT - Section A - English
Module : Module 1 - Vocabulary
Lesson : Lesson 5 - Analogies
Video  : 05 - Commonly Confused Analogy Patterns (Video 5 of 7)

Source script:
  C:\\Users\\User\\Downloads\\C-CAT_SectionA_Module1_English\\English\\Module 1 - Vocabulary\\
  Lesson 5 - Analogies\\05 - Commonly Confused Analogy Patterns.pdf

Built on the golden-reference pattern:
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``;
  * layouts stacked with next_to and guarded with ``no_overlap``; nothing is
    ever animated onto or into another box.

pair_options(stem_roles, options) runs the direction check on a "choose the pair" question: it compares the roles of each option's two words with the stem's, finds the single option that keeps them, and labels reversed pairs; the hook, two worked examples and two practice questions are built with it.
The "direction check" card (bridge from A, name A's role, first word same role, bridge reads identically) stays pinned top-right through the worked examples and Hook, Solved.
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

def analogy_line(a, b, c, d="?", size=BODY):
    """A : B :: C : D as chips.  [0], [2] = first pair;  [4], [6] = second pair."""
    return VGroup(pill(a, WORD, size=size), text(":", size, MUTED), pill(b, WORD, size=size), text("::", size, MUTED),
                  pill(c, SECOND if c != "?" else FOCUS, size=size), text(":", size, MUTED),
                  pill(d, FOCUS if d == "?" else GOOD, size=size)).arrange(RIGHT, buff=0.25)


def pair_options(stem_roles, options):
    """Direction check for a 'choose the pair' question.
    ``stem_roles`` = (role of A, role of B); ``options`` = [(pair text, (role of first, role of second)), ...].
    Returns (option texts, key letter, {letter: why it fails}).  Exactly one option keeps the stem's roles."""
    texts, traps, keys = [], {}, []
    for letter, (pair, roles) in zip("abcd", options):
        texts.append(pair)
        if roles == stem_roles:
            keys.append(letter)
        elif roles == stem_roles[::-1]:
            traps[letter] = f"{roles[0]} → {roles[1]}:  REVERSED"
        else:
            traps[letter] = f"{roles[0]} → {roles[1]}"
    assert len(keys) == 1, keys
    return texts, keys[0], traps


HOOK_Q = pair_options(("product", "worker"), [("Tailor : Clothes", ("worker", "product")),
                                              ("Clothes : Tailor", ("product", "worker")),
                                              ("Needle : Tailor", ("tool", "worker")),
                                              ("Shop : Tailor", ("place", "worker"))])
assert HOOK_Q[1] == "b" and "REVERSED" in HOOK_Q[2]["a"]


class ConfusedAnalogyPatternsVideo(LMSScene):
    lesson_title = "Commonly Confused Analogy Patterns"

    def construct(self):
        self.camera.background_color = BG

        self.lesson_intro()
        self.hook()
        self.concept()
        self.why_you_need_it()
        self.analogy()
        self.example_wheel()
        self.example_drizzle()
        self.example_carpenter()
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

    def direction_pin(self):
        return self.steps_pin("direction check", [("bridge starts from A", WORD), ("name A's ROLE", RATIO),
                                                  ("first word: same role?", BAD),
                                                  ("bridge reads identically", GOOD)])

    def round_card(self):
        head = text("PLACEMENT APTITUDE ROUND", SMALL, RATIO, BOLD)
        line = analogy_line("BREAD", "BAKER", "?", size=LABEL)
        cx, w = self.free_area()
        body = VGroup(head, line).arrange(DOWN, buff=0.25, aligned_edge=LEFT)
        fit_width(body, min(w - 1.4, SAFE_W - 1.8))
        card = self.card(body, width=min(w - 0.2, SAFE_W - 0.4))
        return card.move_to(RIGHT * cx + UP * (CARD_TOP - card.height / 2))

    def direction_example(self, line, options, key, traps, bridge_text, role_text):
        """Analogy line, the bridge written from A, A's role, and the options, beside the pinned panel."""
        cx, w = self.free_area()
        notes = VGroup(VGroup(pill("bridge from A", WORD, size=SMALL), text(bridge_text, LABEL, INK))
                       .arrange(RIGHT, buff=0.25),
                       VGroup(pill("role of A", RATIO, size=SMALL), text(role_text, LABEL, RATIO))
                       .arrange(RIGHT, buff=0.25)).arrange(DOWN, buff=0.25, aligned_edge=LEFT)
        fit_width(notes, w - 0.8)
        q = OptionQuestion("?", options, key, traps, word_size=LABEL)
        block = VGroup(line, notes, q.rows).arrange(DOWN, buff=0.45, aligned_edge=LEFT)
        fit_height(block, SAFE_H - 1.6)
        block.to_edge(LEFT, buff=SAFE + 0.6).set_y(0.1)
        self.no_overlap(line, notes, q.rows)
        self.no_overlap(block, self.pinned)
        self.validator.check_in_frame(block)
        return notes, q

    # ========================================= 0. LESSON INTRO ==========

    def lesson_intro(self):
        self.scene_start("S00_intro", title="Lesson Introduction")

        crumb = self.breadcrumb("English · Module 1 Vocabulary", "Lesson 5 · Analogies", "Video 5")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        built = pill("Videos 1 to 4: precise bridges", MUTED, size=LABEL)
        content = pill("today's errors aren't about the bridge's content", BAD, size=LABEL)
        direction = VGroup(pill("they're about its DIRECTION", GOOD, size=BODY), text("A  →  B", BODY, RATIO, BOLD))\
            .arrange(RIGHT, buff=0.5)
        VGroup(built, content, direction).arrange(DOWN, buff=0.6).move_to(DOWN * 0.1)
        self.no_overlap(crumb, built, content, direction)
        self.validator.check_in_frame(VGroup(crumb, built, content, direction))

        n = self.narrate(
            id="intro_01",
            text="Videos one to four built precise bridges. Today's errors aren't about the content of the bridge; "
                 "they're about its direction.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.at_word(n, "precise")
        self.play(FadeIn(built, shift=UP * 0.1))
        self.at_word(n, "content")
        self.play(FadeIn(content, shift=UP * 0.1))
        self.at_word(n, "direction")
        self.play(FadeIn(direction, shift=UP * 0.1))
        self.wait_for_narration(n)

        title = fitted_text("Commonly Confused Analogy Patterns", SAFE_W, 64, INK, BOLD)
        underline = Line(LEFT, RIGHT, color=BAD, stroke_width=5).set_width(title.width * 0.6)
        VGroup(title, underline).arrange(DOWN, buff=0.2).move_to(UP * 0.2)
        goals = [("Keep the order and direction of a relationship when you carry it across", GOOD),
                 ("Separate worker–tool from worker–product, and part–whole from whole–part", BAD)]
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
            text="This video is commonly confused analogy patterns. By the end, you'll keep the order and direction of a "
                 "relationship when you carry it across, and separate worker and tool from worker and product, and part "
                 "and whole from whole and part.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(VGroup(built, content, direction), shift=UP * 0.3))
        self.at_word(n, "commonly")
        self.play(Write(title), run_time=1.1)
        self.play(GrowFromCenter(underline))
        self.at_word(n, "By")
        self.play(FadeOut(underline), ReplacementTransform(title, small_title), run_time=0.8)
        self.play(FadeIn(objectives[0]), FadeIn(heading))
        for row_, spoken in zip(rows, ["keep", "separate"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row_, shift=RIGHT * 0.2), run_time=0.5)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_intro")

    # ================================================= 1. HOOK ==========

    def hook(self):
        self.scene_start("S01_hook", title="Hook")

        options, key, traps = HOOK_Q
        card = self.round_card()
        line = card[1][1]
        q = OptionQuestion("?", options, key, traps)
        opts = q.rows.copy().arrange_in_grid(rows=2, cols=2, buff=(1.4, 0.4), cell_alignment=LEFT)
        notes = VGroup(pill("two options contain exactly the SAME words", BAD, size=SMALL),
                       pill("one is right;  one is the trap", MUTED, size=SMALL)).arrange(RIGHT, buff=0.4)
        fit_width(notes, SAFE_W)
        opts.next_to(card, DOWN, buff=0.7)
        notes.next_to(opts, DOWN, buff=0.6)
        self.no_overlap(card, opts, notes)
        self.validator.check_in_frame(VGroup(card, opts, notes))

        n = self.narrate(
            id="hook_01",
            text="In a placement aptitude round, you get: bread is to baker, as what is to what?",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "round")
        self.play(FadeIn(card[0]), FadeIn(card[1][0]))
        self.at_word(n, "bread")
        self.play(FadeIn(line, shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_02",
            text="Tailor, clothes; clothes, tailor; needle, tailor; or shop, tailor? Two options contain exactly the same "
                 "words. One is right; one is the trap.",
            voice="default",
            subtitle=True,
            pause_after=3.0,
        )
        for row, (spoken, occ) in zip(opts, [("Tailor", 1), ("clothes", 2), ("needle", 1), ("shop", 1)]):
            self.at_word(n, spoken, occurrence=occ)
            self.play(FadeIn(row, shift=UP * 0.15), run_time=0.35)
        self.at_word(n, "same")
        self.play(FadeIn(notes[0], shift=UP * 0.1))
        self.at_word(n, "trap")
        self.play(FadeIn(notes[1], shift=UP * 0.1))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        self.clear_stage()
        self.scene_end("S01_hook")

    # ============================================== 2. CONCEPT ==========

    def concept(self):
        self.scene_start("S02_concept", title="The Concept")

        errors = VGroup(pill("1  reversed order", BAD, size=LABEL), pill("2  degree direction", RATIO, size=LABEL),
                        pill("3  similar-but-different types", SECOND, size=LABEL)).arrange(RIGHT, buff=0.4)
        fit_width(errors, SAFE_W)
        errors.move_to(UP * (CARD_TOP - errors.height / 2))

        def below(mob):
            fit_within(mob, SAFE_W, SAFE_H - errors.height - 1.6)
            mob.next_to(errors, DOWN, buff=0.6)
            self.no_overlap(errors, mob)
            self.validator.check_in_frame(VGroup(errors, mob))
            return mob

        def pair_row(pair, note, color):
            return VGroup(pill(pair, WORD, size=LABEL), text(note, LABEL, color)).arrange(RIGHT, buff=0.4)

        n = self.narrate(
            id="concept_01",
            text="Three direction errors cause most wrong answers.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Three")
        self.play(LaggedStart(*[FadeIn(e, shift=DOWN * 0.2) for e in errors], lag_ratio=0.25))
        self.wait_for_narration(n)

        one = below(VGroup(pair_row("Bread : Baker", "product → worker", INK),
                           pair_row("Tailor : Clothes", "worker → product   ✗  right words, wrong direction", BAD),
                           pair_row("Clothes : Tailor", "product → worker   ✓  same order", GOOD))
                    .arrange(DOWN, buff=0.4, aligned_edge=LEFT))
        n = self.narrate(
            id="concept_02",
            text="First, reversed order. Bread, baker is product to worker. Tailor, clothes is worker to product: the right "
                 "words, in the wrong direction. The answer must keep the same order: clothes, tailor.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "reversed")
        self.play(Indicate(errors[0], color=BAD, scale_factor=1.05))
        self.at_word(n, "Bread")
        self.play(FadeIn(one[0], shift=RIGHT * 0.2))
        self.at_word(n, "Tailor")
        self.play(FadeIn(one[1], shift=RIGHT * 0.2))
        self.at_word(n, "keep")
        self.play(FadeIn(one[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        two = below(VGroup(pair_row("Warm : Hot", "↑  up the scale: milder → stronger", GOOD),
                           pair_row("Hot : Warm", "↓  down the scale", BAD),
                           pair_row("Drizzle : Downpour", "↑  up", GOOD),
                           pair_row("Breeze : Gale", "↑  up too: the answer", GOOD))
                    .arrange(DOWN, buff=0.35, aligned_edge=LEFT))
        n = self.narrate(
            id="concept_03",
            text="Second, degree direction. Warm, hot goes up the scale: milder to stronger. Hot, warm goes down. Drizzle, "
                 "downpour goes up, so the answer must go up too: breeze, gale.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(one))
        self.at_word(n, "degree")
        self.play(Indicate(errors[1], color=RATIO, scale_factor=1.05))
        for r, (spoken, occ) in zip(two, [("Warm", 1), ("Hot", 2), ("Drizzle", 1), ("breeze", 1)]):
            self.at_word(n, spoken, occurrence=occ)
            self.play(FadeIn(r, shift=RIGHT * 0.2), run_time=0.45)
        self.wait_for_narration(n)

        three = below(VGroup(pair_row("Carpenter : Saw", "worker – TOOL", RATIO),
                             pair_row("Carpenter : Furniture", "worker – PRODUCT", SECOND),
                             pair_row("Carpenter : Wood", "worker – MATERIAL", WORD),
                             pair_row("Wheel : Car   vs   Car : Wheel", "part → whole   vs   whole → part", BAD))
                      .arrange(DOWN, buff=0.35, aligned_edge=LEFT))
        n = self.narrate(
            id="concept_04",
            text="Third, similar but different types. Worker and tool: carpenter, saw. Worker and product: carpenter, "
                 "furniture. Worker and material: carpenter, wood. And part to whole, wheel, car, against whole to part: "
                 "car, wheel.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(two))
        self.at_word(n, "similar")
        self.play(Indicate(errors[2], color=SECOND, scale_factor=1.05))
        for r, spoken in zip(three, ["saw", "furniture", "wood", "wheel"]):
            self.at_word(n, spoken, occurrence=1)
            self.play(FadeIn(r, shift=RIGHT * 0.2), run_time=0.45)
        self.wait_for_narration(n)

        defence = below(VGroup(pill("the defence: write the bridge in the ORDER the words appear, starting with A", GOOD,
                                    size=SMALL),
                               text("“Bread is made by a baker.”", BODY, INK, t2c={"Bread": WORD, "is made by": RATIO}),
                               text("“Clothes are made by a tailor.”", BODY, INK, t2c={"Clothes": GOOD,
                                                                                    "are made by": RATIO}))
                        .arrange(DOWN, buff=0.5))
        n = self.narrate(
            id="concept_05",
            text="The defence: when you write the bridge, write it in the order the words appear, starting with A. Bread "
                 "is made by a baker. Then the second pair must start with the product: clothes are made by a tailor.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(three))
        self.at_word(n, "defence")
        self.play(FadeIn(defence[0], shift=DOWN * 0.1))
        self.at_word(n, "Bread")
        self.play(FadeIn(defence[1], shift=UP * 0.1))
        self.at_word(n, "clothes")
        self.play(FadeIn(defence[2], shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_concept")

    # ======================================== 3. WHY YOU NEED IT ==========

    def why_you_need_it(self):
        self.scene_start("S03_why", title="Why You Need It")

        common = pill("reversed pairs: among the most common distractors in “choose the pair”", BAD, size=LABEL)
        right = pill("…because they use the RIGHT words", RATIO, size=LABEL)
        only = pill("only a DIRECTION check catches them", GOOD, size=BODY)
        group = VGroup(common, right, only).arrange(DOWN, buff=0.7)
        fit_width(group, SAFE_W).move_to(UP * 0.3)
        self.no_overlap(common, right, only)
        self.validator.check_in_frame(group)

        n = self.narrate(
            id="why_01",
            text="Reversed pairs are among the most common distractors in choose-the-pair questions, because they use the "
                 "right words. Only a direction check catches them.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Reversed")
        self.play(FadeIn(common, shift=DOWN * 0.1))
        self.at_word(n, "right")
        self.play(FadeIn(right, shift=UP * 0.1))
        self.at_word(n, "direction")
        self.play(FadeIn(only, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_why")

    # ============================================== 4. ANALOGY ==========

    def analogy(self):
        self.scene_start("S04_analogy", title="The Analogy")

        x0, x1 = -5.6, 5.6
        kerbs = VGroup(Line(RIGHT * x0 + UP * 1.5, RIGHT * x1 + UP * 1.5, color=MUTED, stroke_width=5),
                       Line(RIGHT * x0 + DOWN * 1.3, RIGHT * x1 + DOWN * 1.3, color=MUTED, stroke_width=5))
        sign = pill("ONE WAY  →", FOCUS, size=LABEL).next_to(kerbs[0], UP, buff=0.3)
        legal = VGroup(Arrow(LEFT * 1.6, RIGHT * 1.6, buff=0, color=GOOD, stroke_width=8),
                       text("Clothes : Tailor   (product → worker)", SMALL, GOOD)).arrange(UP, buff=0.12)
        legal.move_to(UP * 0.7 + LEFT * 1.6)
        wrong = VGroup(Arrow(RIGHT * 1.6, LEFT * 1.6, buff=0, color=BAD, stroke_width=8),
                       text("Tailor : Clothes   (worker → product)", SMALL, BAD)).arrange(UP, buff=0.12)
        wrong.move_to(DOWN * 0.6 + RIGHT * 1.6)
        verdict = pill("the same street, opposite directions: only one is legal", FOCUS, size=LABEL)
        verdict.next_to(kerbs[1], DOWN, buff=0.4)
        self.no_overlap(sign, legal, wrong, verdict)
        self.validator.check_in_frame(VGroup(sign, kerbs, legal, wrong, verdict))

        n = self.narrate(
            id="analogy_01",
            text="A relationship is a one-way street. Two cars on the right street can still be driving in opposite "
                 "directions. Only one is legal.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "one-way")
        self.play(Create(kerbs), FadeIn(sign, shift=DOWN * 0.1))
        self.at_word(n, "cars")
        self.play(GrowArrow(legal[0]), FadeIn(legal[1]))
        self.at_word(n, "opposite")
        self.play(GrowArrow(wrong[0]), FadeIn(wrong[1]))
        self.at_word(n, "legal")
        self.play(FadeIn(verdict, shift=UP * 0.1), Indicate(legal[0], color=GOOD, scale_factor=1.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_analogy")

    # ======================================== 5-7. WORKED EXAMPLES ==========

    def example_wheel(self):
        self.scene_start("S05_ex_wheel", title="Worked Example 1")
        self.play(self.pin(self.direction_pin()))

        options, key, traps = pair_options(("part", "whole"), [("Book : Page", ("whole", "part")),
                                                               ("Page : Book", ("part", "whole"))])
        line = analogy_line("Wheel", "Car", "?", size=LABEL)
        notes, q = self.direction_example(line, options, key, traps, "a wheel is part of a car", "the PART comes first")

        n = self.narrate(
            id="ex1_01",
            text="Wheel is to car, as what is to what? Book, page, or page, book? Bridge from A: a wheel is part of a car. "
                 "The first word is the part. Book, page starts with the whole: reversed. Page, book starts with the "
                 "part: that's the answer.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Wheel", occurrence=1)
        self.play(FadeIn(line, shift=DOWN * 0.1))
        self.at_word(n, "Book", occurrence=1)
        self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.2) for r in q.rows], lag_ratio=0.3))
        self.at_word(n, "Bridge")
        self.play(FadeIn(notes[0], shift=RIGHT * 0.2), self.pin_step(0, color=WORD))
        self.at_word(n, "first")
        self.play(FadeIn(notes[1], shift=RIGHT * 0.2), self.pin_step(1, color=RATIO))
        self.at_word(n, "reversed")
        self.play(*q.strike("a")[1], self.pin_step(2, color=BAD))
        self.at_word(n, "answer")
        self.play(*q.confirm()[1], self.pin_step(3, color=GOOD))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_ex_wheel")

    def example_drizzle(self):
        self.scene_start("S06_ex_drizzle", title="Worked Example 2")

        line = analogy_line("Drizzle", "Downpour", "Breeze", size=LABEL)
        notes, q = self.direction_example(line, ["calm", "gale", "air"], "b",
                                          {"a": "goes DOWN the scale", "c": "not on the scale"},
                                          "a drizzle is a milder form of a downpour", "the MILDER one first: ↑ up")

        n = self.narrate(
            id="ex2_01",
            text="Drizzle is to downpour, as breeze is to what? Calm, gale, or air? Bridge from A: a drizzle is a milder "
                 "form of a downpour. The first word is the milder one, so the scale goes up. Calm goes down the scale, "
                 "and air isn't on it. The answer is gale.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Drizzle", occurrence=1)
        self.play(FadeIn(line, shift=DOWN * 0.1))
        self.at_word(n, "Calm", occurrence=1)
        self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.2) for r in q.rows], lag_ratio=0.3))
        self.at_word(n, "Bridge")
        self.play(FadeIn(notes[0], shift=RIGHT * 0.2), self.pin_step(0, color=WORD))
        self.at_word(n, "first")
        self.play(FadeIn(notes[1], shift=RIGHT * 0.2), self.pin_step(1, color=RATIO))
        self.at_word(n, "Calm", occurrence=2)
        self.play(*q.strike("a")[1], *q.strike("c")[1], self.pin_step(2, color=BAD))
        self.at_word(n, "answer")
        self.play(*q.confirm()[1], self.pin_step(3, color=GOOD))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_ex_drizzle")

    def example_carpenter(self):
        self.scene_start("S07_ex_carpenter", title="Worked Example 3")

        options, key, traps = pair_options(("worker", "tool"), [("Writer : Book", ("worker", "product")),
                                                                ("Surgeon : Scalpel", ("worker", "tool"))])
        line = analogy_line("Carpenter", "Saw", "?", size=LABEL)
        notes, q = self.direction_example(line, options, key, traps, "a carpenter uses a saw", "worker → TOOL")

        n = self.narrate(
            id="ex3_01",
            text="Carpenter is to saw, as what is to what? Writer, book, or surgeon, scalpel? Bridge from A: a carpenter "
                 "uses a saw. The roles are worker, then tool. Writer, book is worker, then product. Surgeon, scalpel is "
                 "worker, then tool: that's the answer.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Carpenter", occurrence=1)
        self.play(FadeIn(line, shift=DOWN * 0.1))
        self.at_word(n, "Writer", occurrence=1)
        self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.2) for r in q.rows], lag_ratio=0.3))
        self.at_word(n, "Bridge")
        self.play(FadeIn(notes[0], shift=RIGHT * 0.2), self.pin_step(0, color=WORD))
        self.at_word(n, "roles")
        self.play(FadeIn(notes[1], shift=RIGHT * 0.2), self.pin_step(1, color=RATIO))
        self.at_word(n, "product")
        self.play(*q.strike("a")[1], self.pin_step(2, color=BAD))
        self.at_word(n, "answer")
        self.play(*q.confirm()[1], self.pin_step(3, color=GOOD))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S07_ex_carpenter")

    # ================================================ 8. RULES ==========

    def rules(self):
        self.scene_start("S08_rules", title="Rules")
        self.play(self.unpin())

        rules = VGroup(*[VGroup(pill(str(i + 1), c, size=SMALL), fitted_text(s_, SAFE_W - 2.2, BODY, INK))
                         .arrange(RIGHT, buff=0.3) for i, (s_, c) in enumerate([
                             ("Write the bridge starting with A, in the given order", WORD),
                             ("The answer pair must start with the same ROLE as A", RATIO),
                             ("For degree: check UP or DOWN the scale", BAD),
                             ("Separate tool, product and material", SECOND)])])
        rules.arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        board = self.card(rules).move_to(UP * 0.3)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="rules_01",
            text="Four rules. First, write the bridge starting with A, in the given order. Second, the answer pair must "
                 "start with the same role as A. Third, for degree, check up or down the scale. And fourth, separate "
                 "tool, product and material.",
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
                             ("Bridge starting from A", WORD),
                             ("Identify the role of A: product, part, milder, worker", RATIO),
                             ("In each option: does the FIRST word play the same role?", BAD),
                             ("Confirm the bridge reads identically", GOOD)])])
        steps.arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        board = self.card(steps).move_to(UP * 0.3)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="process_01",
            text="The process. Step one: bridge starting from A. Step two: identify the role of A: product, part, milder, "
                 "or worker. Step three: in each option, check that the first word plays the same role. And step four: "
                 "confirm that the bridge reads identically.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(board[0]))
        for r, spoken in zip(steps, ["one", "two", "three", "four"]):
            self.at_word(n, spoken)
            self.play(FadeIn(r, shift=RIGHT * 0.2), run_time=0.45)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S09_process")

    # ========================================== 10. HOOK, SOLVED ==========

    def hook_solved(self):
        self.scene_start("S10_hook_solved", title="Hook, Solved")
        self.play(self.pin(self.direction_pin()))

        options, key, traps = HOOK_Q
        cx, w = self.free_area()
        card = self.round_card()
        b1 = text("“Bread is made by a baker.”", LABEL, INK, t2c={"Bread": WORD, "is made by": RATIO})
        role = pill("first word = the PRODUCT", RATIO, size=SMALL)
        notes = VGroup(b1, role).arrange(RIGHT, buff=0.4)
        fit_width(notes, w - 0.8)
        notes.next_to(card, DOWN, buff=0.3).to_edge(LEFT, buff=SAFE + 0.6)
        q = OptionQuestion("?", options, key, traps, word_size=LABEL)
        b2 = text("“Clothes are made by a tailor.”", LABEL, INK, t2c={"Clothes": GOOD, "are made by": RATIO})
        body = VGroup(q.rows, b2).arrange(DOWN, buff=0.35, aligned_edge=LEFT)
        fit_height(body, notes.get_bottom()[1] - 0.3 - (BOTTOM_Y + 0.6))
        body.next_to(notes, DOWN, buff=0.3).to_edge(LEFT, buff=SAFE + 0.6)
        self.no_overlap(card, notes, q.rows, b2)
        self.no_overlap(card, self.pinned)
        self.no_overlap(notes, self.pinned)
        self.validator.check_in_frame(VGroup(card, notes, body))

        n = self.narrate(
            id="solved_01",
            text="Let's solve the hook. Read: bread is to baker. Predict, with a bridge from A: bread is made by a baker. "
                 "The first word is the product.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(card), FadeIn(q.rows))
        self.at_word(n, "Read")
        self.play(Indicate(card[1][1][:3], color=WORD, scale_factor=1.05))
        self.at_word(n, "bridge")
        self.play(FadeIn(b1, shift=RIGHT * 0.2), self.pin_step(0, color=WORD))
        self.at_word(n, "product")
        self.play(FadeIn(role, shift=LEFT * 0.1), self.pin_step(1, color=RATIO))
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_02",
            text="Eliminate. Tailor, clothes starts with the worker: reversed. Needle, tailor is tool to worker. Shop, "
                 "tailor is place to worker.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Eliminate")
        self.play(self.pin_step(2, color=BAD))
        for letter, spoken in [("a", "Tailor"), ("c", "Needle"), ("d", "Shop")]:
            self.at_word(n, spoken, occurrence=1)
            self.play(*q.strike(letter)[1])
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_03",
            text="Confirm: clothes are made by a tailor. That's the answer.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Confirm")
        self.play(FadeIn(b2, shift=UP * 0.1), self.pin_step(3, color=GOOD))
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
            ["Choose the pair", "bridge from A; check the role of each pair's first word"],
            ["Degree analogies", "up or down the scale, and keep it"],
            ["Worker analogies", "tool, product or material?  match exactly"],
        ], [4.2, 7.6], size=LABEL)
        board = self.card(table, width=SAFE_W - 0.2).move_to(UP * 0.4)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="patterns_01",
            text="Three exam patterns. Choose the pair: bridge from A, and check the role of each pair's first word. "
                 "Degree analogies: up or down the scale, and keep it. And worker analogies: tool, product or material? "
                 "Match exactly.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "patterns")
        self.play(FadeIn(board[0]), FadeIn(table[0]))
        for row, spoken in zip(table[1:], ["Choose", "Degree", "worker"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.45)
        self.at_word(n, "Match")
        self.play(Indicate(table[3][1], color=GOOD, scale_factor=1.03))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S11_patterns")

    # ======================================== 12. COMMON MISTAKES ==========

    def common_mistakes(self):
        self.scene_start("S12_mistakes", title="Common Mistakes")

        card_w = ZONE_W - 0.3
        pairs = [
            (self.verdict_card(False, "Accepting reversed pairs", card_w),
             self.verdict_card(True, "Check the first word's role", card_w)),
            (self.verdict_card(False, "Reversing a degree scale", card_w),
             self.verdict_card(True, "Up stays up;  down stays down", card_w)),
            (self.verdict_card(False, "Mixing tool, product and material", card_w),
             self.verdict_card(True, "uses  /  makes  /  works with", card_w)),
        ]
        for (wrong, right), yy in zip(pairs, [1.6, 0.05, -1.5]):
            wrong.move_to(LEFT_ZONE + UP * yy)
            right.move_to(RIGHT_ZONE + UP * yy)
        header = pill("3 mistakes", BAD, size=LABEL).move_to(UP * (CARD_TOP - 0.3))
        self.validator.check_in_frame(VGroup(header, *[c for p in pairs for c in p]))

        n = self.narrate(
            id="mistakes_01",
            text="Three common mistakes. The first is accepting reversed pairs. The second is reversing a degree scale. "
                 "The third is mixing tool, product and material.",
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

    Q1 = pair_options(("whole", "part"), [("Tree : Leaf", ("whole", "part")), ("Leaf : Tree", ("part", "whole")),
                                          ("Root : Soil", ("part", "place")), ("Stem : Branch", ("part", "part"))])
    Q3 = pair_options(("worker", "tool"), [("Painter : Painting", ("worker", "product")),
                                           ("Farmer : Crop", ("worker", "product")), ("Writer : Pen", ("worker", "tool")),
                                           ("Baker : Bread", ("worker", "product"))])
    PRACTICE = [
        (("Flower", "Petal", "?"), Q1[0], Q1[1], "whole → part"),
        (("Whisper", "Shout", "Smile"), ["grin", "frown", "cry", "laugh"], "d",
         "a quieter → louder form of the same act"),
        (("Surgeon", "Scalpel", "?"), Q3[0], Q3[1], "worker → tool;  the others are worker → product"),
    ]
    assert Q1[1] == "a" and Q3[1] == "c"

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
            text="Your turn. One: flower is to petal, as what is to what? Tree, leaf; leaf, tree; root, soil; or stem, "
                 "branch? Two: whisper is to shout, as smile is to what? Grin, frown, cry, or laugh? Three: surgeon is to "
                 "scalpel, as what is to what? Painter, painting; farmer, crop; writer, pen; or baker, bread?",
            voice="default",
            subtitle=True,
            pause_after=10.0,
        )
        self.play(FadeIn(board[0]))
        for ln, (spoken, first_option) in zip(lines, [("flower", "Tree"), ("whisper", "Grin"), ("surgeon", "Painter")]):
            self.at_word(n, spoken)
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

        rows = VGroup()
        for (a, b, c), opts, key, why in self.PRACTICE:
            ans = opts["abcd".index(key)]
            line = analogy_line(a, b, *ans.split(" : "), size=LABEL) if c == "?" else analogy_line(a, b, c, ans,
                                                                                                   size=LABEL)
            if c == "?":
                line[4].set_color(GOOD)
            rows.add(VGroup(line, text(why, SMALL, RATIO)).arrange(DOWN, buff=0.18, aligned_edge=LEFT))
        rows.arrange(DOWN, buff=0.5, aligned_edge=LEFT)
        fit_within(rows, SAFE_W, SAFE_H - 1.2)
        rows.move_to(UP * 0.3)
        self.validator.check_in_frame(rows)

        n = self.narrate(
            id="answers_01",
            text="One: tree, leaf. Whole, then part. Two: laugh: a quieter, then a louder form of the same act. Three: "
                 "writer, pen. Worker, then tool; the others are worker, then product.",
            voice="default",
            subtitle=True,
        )
        for r, (spoken, why) in zip(rows, [("tree", "Whole"), ("laugh", "quieter"), ("writer", "tool")]):
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

        card, table = self.recap_card("Recap Card: Video 5", [
            ["Start with A", "write the bridge in the given order"],
            ["Same first role", "product, part, milder or worker must match"],
            ["Separate", "tool / product / material"],
        ])
        card.move_to(UP * 0.2)
        self.validator.check_in_frame(card)

        n = self.narrate(
            id="recap_01",
            text="To recap. Start with A: write the bridge in the given order. Keep the same first role: product, part, "
                 "milder or worker must match. And separate tool, product and material.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(card[0]), FadeIn(table[0]))
        for row, spoken in zip(table[1:], ["Start", "role", "separate"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.45)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S15_recap")

    # ================================================= 16. NEXT ==========

    def next_video(self):
        self.scene_start("S16_next", title="Next")

        pairs = pill("the analogy pairs that exams use most often", BAD, size=LABEL)
        nxt = pill("Next:  Exam-Oriented Analogies", FOCUS, size=LABEL)
        VGroup(pairs, nxt).arrange(DOWN, buff=0.8).move_to(UP * 0.2)
        self.no_overlap(pairs, nxt)
        self.validator.check_in_frame(VGroup(pairs, nxt))

        n = self.narrate(
            id="next_01",
            text="Video six brings together the analogy pairs that exams use most often.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Video")
        self.play(FadeIn(nxt, scale=1.05))
        self.at_word(n, "pairs")
        self.play(FadeIn(pairs, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S16_next")

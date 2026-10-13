"""
animation.py for the LMS video generator.

Course : C-CAT - Section A - English
Module : Module 1 - Vocabulary
Lesson : Lesson 1 - Synonyms
Video  : 04 - Commonly Confused Synonyms (Video 4 of 6)

Source script:
  C:\\Users\\User\\Downloads\\C-CAT_SectionA_Module1_English\\English\\Module 1 - Vocabulary\\
  Lesson 1 - Synonyms\\04 - Commonly Confused Synonyms.pdf

Built on the golden-reference pattern:
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``.

Opening: a later video of Lesson 1, so no spoken welcome. The module > lesson >
video trail is shown on screen (silent), then a one-line recap of Videos 1-3
(right meaning, then compare close options), the line about today's topic,
the title and the objectives.

Core visuals: look-alike pairs with the differing letters lit (computed with
difflib, so the highlight always matches the spelling); one memory hook per
pair with the matching letters lit (every span is range-checked); a USB-C /
Lightning plug analogy; ``OptionQuestion`` cards with traps tagged by the pair
they belong to. Layouts are stacked with next_to and guarded with
``no_overlap``.

Script note: the hook's VISUAL cue says "Server downtime is ___" but the
narration says "A server shutdown is ___"; the video uses "shutdown"
throughout.

Section map (script heading -> scene):
  S00 Intro (trail + continuity)     S09 The Process
  S01 Hook                           S10 Hook, Solved
  S02 The Concept                    S11 Exam Patterns and Solving Models
  S03 Why You Need It                S12 Common Mistakes
  S04 The Analogy                    S13 Practice Questions
  S05-S07 Worked Examples 1-3        S14 Answers
  S08 Rules                          S15 Recap Card / S16 Next
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

import difflib
import re


def marked(word, spans, size=BODY, color=INK, mark=FOCUS, weight=BOLD):
    """A single word (no spaces) with the character ``spans`` [(start, end), ...] coloured."""
    assert " " not in word
    for s_, e_ in spans:
        assert 0 <= s_ < e_ <= len(word), (word, s_, e_)
    return text(word, size, color, weight, t2c={f"[{s_}:{e_}]": mark for s_, e_ in spans})


def diff_spans(a, b):
    """Character spans where two look-alike words differ (per word)."""
    sm = difflib.SequenceMatcher(a=a, b=b, autojunk=False)
    sa, sb = [], []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag != "equal":
            if i2 > i1:
                sa.append((i1, i2))
            if j2 > j1:
                sb.append((j1, j2))
    return sa, sb


def look_alike_pair(a, b, mean_a, mean_b, size=BODY):
    """Two look-alike words with their differing letters lit, each with its meaning underneath."""
    sa, sb = diff_spans(a, b)
    left = VGroup(marked(a, sa, size, mark=BAD), text(mean_a, SMALL, MUTED)).arrange(DOWN, buff=0.15)
    right = VGroup(marked(b, sb, size, mark=BAD), text(mean_b, SMALL, MUTED)).arrange(DOWN, buff=0.15)
    return VGroup(left, text("≠", TITLE, BAD, BOLD), right).arrange(RIGHT, buff=0.5)


def hook_line(tokens, size=LABEL):
    """A memory hook built from tokens: plain strings, or (word, [spans]) with letters lit."""
    parts = []
    for t in tokens:
        if isinstance(t, str):
            parts.append(text(t, size, MUTED))
        else:
            parts.append(marked(t[0], t[1], size, INK, GOOD))
    return VGroup(*parts).arrange(RIGHT, buff=0.18)


# Memory hooks (pair, tokens). Every lit span is checked by ``marked``.
HOOKS = [
    ("eminent / imminent", [("imminent", [(0, 2)]), "=", ("immediate", [(0, 2)])]),
    ("elicit / illicit", [("illicit", [(0, 3)]), "=", ("illegal", [(0, 3)])]),
    ("complement / compliment", [("complement", [(5, 6)]), "completes;", ("compliment", [(5, 6)]), "=",
                                 ("I", [(0, 1)]), "like", "you"]),
    ("continual / continuous", [("continuous", [(7, 10)]), "=", ("one", [(0, 1)]), ("unbroken", [(0, 1)]),
                                ("stretch", [(0, 1)])]),
    ("economic / economical", [("economical", [(8, 10)]), "=", "saves", "money"]),
    ("disinterested / uninterested", [("disinterested", [(0, 3)]), "=", ("distanced", [(0, 3)]), "(neutral)"]),
    ("historic / historical", [("historic", [(6, 8)]), "=", ("important", [(0, 1)])]),
]


class CommonlyConfusedSynonymsVideo(LMSScene):
    lesson_title = "Commonly Confused Synonyms"

    def construct(self):
        self.camera.background_color = BG

        self.lesson_intro()
        self.hook()
        self.concept()
        self.why_you_need_it()
        self.analogy()
        self.example_historic()
        self.example_disinterested()
        self.example_continual()
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

    def sentence_card(self, sentence, word, color=WORD):
        t = text(f"“{sentence}”", BODY, INK, t2c={rf"\b{re.escape(word)}\b": color})
        card = self.card(fit_width(t, SAFE_W - 1.2), width=SAFE_W - 0.4)
        return card.move_to(UP * (CARD_TOP - card.height / 2))

    def context_question(self, sentence, word, options, key, traps):
        card = self.sentence_card(sentence, word)
        q = OptionQuestion(word, options, key, traps, word_size=BODY)
        q.group.next_to(card, DOWN, buff=0.45).to_edge(LEFT, buff=SAFE + 0.6)
        self.no_overlap(card, q.group)
        self.validator.check_in_frame(VGroup(card, q.group))
        return card, q

    # ========================================= 0. LESSON INTRO ==========
    # Purpose: silent trail, a one-line recap of Videos 1-3 (the right meaning,
    # then compare close options), today's topic, the objectives.

    def lesson_intro(self):
        self.scene_start("S00_intro", title="Lesson Introduction")

        crumb = self.breadcrumb("English · Module 1 Vocabulary", "Lesson 1 · Synonyms", "Video 4")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        so_far = VGroup(pill("right meaning (Video 3)", WORD, size=LABEL), text("→", LABEL, MUTED),
                        pill("compare close options (Video 2)", RATIO, size=LABEL)).arrange(RIGHT, buff=0.3)
        fit_width(so_far, SAFE_W)
        today = pill("today: pairs that trick your EYES", BAD, size=LABEL)
        VGroup(so_far, today).arrange(DOWN, buff=0.7).move_to(DOWN * 0.1)
        self.no_overlap(crumb, so_far, today)
        self.validator.check_in_frame(VGroup(crumb, so_far, today))

        n = self.narrate(
            id="intro_01",
            text="In videos one to three, you found the right meaning, and compared close options. Today's pairs trick "
                 "your eyes rather than your understanding, so they need a different defence: a fixed memory hook for "
                 "each pair.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.at_word(n, "right")
        self.play(FadeIn(so_far[0], shift=UP * 0.1))
        self.at_word(n, "compared")
        self.play(FadeIn(so_far[1:], shift=UP * 0.1))
        self.at_word(n, "eyes")
        self.play(FadeIn(today, shift=UP * 0.1))
        self.wait_for_narration(n)

        title = fitted_text("Commonly Confused Synonyms", SAFE_W, 72, INK, BOLD)
        underline = Line(LEFT, RIGHT, color=BAD, stroke_width=5).set_width(title.width * 0.6)
        VGroup(title, underline).arrange(DOWN, buff=0.2).move_to(UP * 0.2)
        n = self.narrate(
            id="intro_02",
            text="These are the commonly confused synonyms.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(VGroup(so_far, today), shift=UP * 0.3))
        self.at_word(n, "confused")
        self.play(Write(title), run_time=1.1)
        self.play(GrowFromCenter(underline))
        self.wait_for_narration(n)

        goals = [
            ("Separate the look-alike and near-alike pairs exams use as distractors", BAD),
            ("Use a memory hook for each high-frequency pair", GOOD),
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
            text="By the end of this video, you'll separate the look-alike and near-alike pairs that exams use as "
                 "distractors, and use a memory hook for each high-frequency pair.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(underline), ReplacementTransform(title, small_title), run_time=0.8)
        self.play(FadeIn(objectives[0]), FadeIn(heading))
        for row_, spoken in zip(rows, ["separate", "memory"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row_, shift=RIGHT * 0.2), run_time=0.5)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_intro")

    # ================================================= 1. HOOK ==========

    HOOK = dict(options=["eminent", "immanent", "imminent", "emanant"], key="c",
                traps={"a": "distinguished", "b": "inherent", "d": "flowing out"})

    def chat_card(self, blank="______", color=INK):
        who = text("DevOps lead", SMALL, WORD, BOLD)
        msg = text(f"A server shutdown is {blank}. Save your work now.", BODY, color,
                   t2c={re.escape(blank): FOCUS if blank.startswith("_") else GOOD})
        return self.card(VGroup(who, fit_width(msg, SAFE_W - 1.6)).arrange(DOWN, buff=0.2, aligned_edge=LEFT),
                         width=SAFE_W - 0.4)

    def hook(self):
        self.scene_start("S01_hook", title="Hook")

        chat = self.chat_card()
        chat.move_to(UP * (CARD_TOP - chat.height / 2))
        h = self.HOOK
        words = VGroup(*[VGroup(text(f"({l})", LABEL, MUTED), text(o, TITLE, INK, BOLD)).arrange(RIGHT, buff=0.2)
                         for l, o in zip("abcd", h["options"])]).arrange_in_grid(rows=2, cols=2, buff=(1.4, 0.4))
        note = pill("they look nearly identical; one means “about to happen”", FOCUS, size=SMALL)
        fit_width(note, SAFE_W)
        words.next_to(chat, DOWN, buff=0.6)
        note.next_to(words, DOWN, buff=0.5)
        self.no_overlap(chat, words, note)
        self.validator.check_in_frame(VGroup(chat, words, note))

        n = self.narrate(
            id="hook_01",
            text="Your DevOps lead posts in the team chat: a server shutdown is blank. Save your work now. Which word "
                 "fits?",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(chat, shift=DOWN * 0.2))
        self.wait_for_narration(n)

        n = self.narrate(
            id="hook_02",
            text="Eminent, immanent, imminent, or emanant? They look nearly identical. One means about to happen. The "
                 "others would make the message nonsense.",
            voice="default",
            subtitle=True,
            pause_after=3.0,
        )
        for w, spoken in zip(words, ["Eminent", "immanent", "imminent", "emanant"]):
            self.at_word(n, spoken)
            self.play(FadeIn(w, shift=UP * 0.15), run_time=0.35)
        self.at_word(n, "identical")
        self.play(FadeIn(note, shift=UP * 0.1))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        self.clear_stage()
        self.scene_end("S01_hook")

    # ============================================== 2. CONCEPT ==========

    def concept(self):
        self.scene_start("S02_concept", title="The Concept")

        head1 = pill("Look-alikes (paronyms): a letter or two apart, completely different meanings", BAD, size=SMALL)
        fit_width(head1, SAFE_W)
        head1.move_to(UP * (CARD_TOP - head1.height / 2))
        looks = VGroup(look_alike_pair("eminent", "imminent", "distinguished", "about to happen", LABEL),
                       look_alike_pair("elicit", "illicit", "draw out", "illegal", LABEL),
                       look_alike_pair("complement", "compliment", "complete", "praise", LABEL))
        looks.arrange(DOWN, buff=0.35)
        fit_within(looks, SAFE_W, 4.6)
        looks.next_to(head1, DOWN, buff=0.4)
        self.no_overlap(head1, looks)
        self.validator.check_in_frame(VGroup(head1, looks))

        n = self.narrate(
            id="concept_01",
            text="Two kinds of pairs cause most errors. Look-alikes, or paronyms, differ by a letter or two, but mean "
                 "completely different things. Eminent means distinguished, and imminent means about to happen. Elicit "
                 "means draw out, and illicit means illegal. Complement means complete, and compliment means praise.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "paronyms")
        self.play(FadeIn(head1, shift=DOWN * 0.2))
        for pr, spoken in zip(looks, ["Eminent", "Elicit", "Complement"]):
            self.at_word(n, spoken)
            self.play(FadeIn(pr, shift=UP * 0.15), run_time=0.5)
        self.wait_for_narration(n)

        # Near-alikes: related but not interchangeable.
        head2 = pill("Near-alikes: genuinely related, NOT interchangeable", RATIO, size=SMALL)
        fit_width(head2, SAFE_W)
        head2.move_to(head1)
        table = self.table_rows(["pair", "first", "second"], [
            ["continual / continuous", "repeated, with breaks", "without a break"],
            ["economic / economical", "about the economy", "saving money"],
            ["disinterested / uninterested", "neutral, impartial", "not interested"],
            ["historic / historical", "important in history", "about the past"],
        ], [4.4, 3.8, 3.6], size=LABEL)
        near = self.card(table, width=SAFE_W - 0.2)
        near.next_to(head2, DOWN, buff=0.4)
        self.no_overlap(head2, near)
        self.validator.check_in_frame(VGroup(head2, near))
        n = self.narrate(
            id="concept_02",
            text="Near-alikes are genuinely related, but not interchangeable. Continual means repeated, with breaks; "
                 "continuous means without a break. Economic is about the economy; economical is about saving money. "
                 "Disinterested means neutral, or impartial; uninterested means not interested. Historic means important "
                 "in history; historical means about the past.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeOut(VGroup(head1, looks)))
        self.at_word(n, "related")
        self.play(FadeIn(head2, shift=DOWN * 0.2), FadeIn(near[0]), FadeIn(table[0]))
        for row, spoken in zip(table[1:], ["Continual", "Economic", "Disinterested", "Historic"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.45)
        self.wait_for_narration(n)

        n = self.narrate(
            id="concept_03",
            text="In a synonym question, a look-alike of the question word is almost always a trap. And if a near-alike "
                 "appears, check which half of the pair the question word really is.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "trap")
        cap = self.caption("Look-alike in the options?  Almost always a trap.", BAD)
        self.play(FadeIn(cap, shift=UP * 0.2))
        self.at_word(n, "half")
        self.play(Indicate(near, color=RATIO, scale_factor=1.02))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_concept")

    # ======================================== 3. WHY YOU NEED IT ==========

    def why_you_need_it(self):
        self.scene_start("S03_why", title="Why You Need It")

        where = VGroup(pill("synonym options", WORD, size=LABEL), pill("Spotting Errors (Lesson 9)", RATIO, size=LABEL),
                       pill("Sentence Correction (Lesson 10)", SECOND, size=LABEL)).arrange(RIGHT, buff=0.35)
        fit_width(where, SAFE_W)
        judge = VGroup(VGroup(text("“The judge was uninterested.”", LABEL, INK), text("bored: alarming", SMALL, BAD))
                       .arrange(DOWN, buff=0.12),
                       VGroup(text("“The judge was disinterested.”", LABEL, INK), text("impartial: what you want", SMALL,
                                                                                         GOOD)).arrange(DOWN, buff=0.12))\
            .arrange(RIGHT, buff=1.0)
        fit_width(judge, SAFE_W)
        VGroup(where, judge).arrange(DOWN, buff=1.0).move_to(UP * 0.2)
        self.no_overlap(where, judge)
        self.validator.check_in_frame(VGroup(where, judge))

        n = self.narrate(
            id="why_01",
            text="These pairs appear in synonym options, in spotting errors, lesson nine, and in sentence correction, "
                 "lesson ten. They also appear in real emails, where the judge was uninterested says something very "
                 "different from disinterested.",
            voice="default",
            subtitle=True,
        )
        for chip, spoken in zip(where, ["synonym", "spotting", "sentence"]):
            self.at_word(n, spoken)
            self.play(FadeIn(chip, shift=UP * 0.1), run_time=0.4)
        self.at_word(n, "uninterested")
        self.play(FadeIn(judge[0], shift=UP * 0.1))
        self.at_word(n, "disinterested")
        self.play(FadeIn(judge[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_why")

    # ============================================== 4. ANALOGY ==========

    def plug(self, kind, color):
        """A simple cable end: USB-C is a rounded oval, Lightning a thin flat tab."""
        cable = Line(DOWN * 1.4, DOWN * 0.3, color=MUTED, stroke_width=8)
        housing = RoundedRectangle(corner_radius=0.1, width=0.7, height=0.9, color=color, fill_color=PANEL,
                                   fill_opacity=1).move_to(DOWN * 0.3 + UP * 0.45)
        if kind == "usb-c":
            tip = RoundedRectangle(corner_radius=0.12, width=0.46, height=0.24, color=color, fill_opacity=0.4)
        else:
            tip = RoundedRectangle(corner_radius=0.05, width=0.3, height=0.16, color=color, fill_opacity=0.4)
        tip.next_to(housing, UP, buff=0)
        return VGroup(cable, housing, tip)

    def analogy(self):
        self.scene_start("S04_analogy", title="The Analogy")

        a = self.plug("usb-c", GOOD)
        b = self.plug("lightning", BAD)
        VGroup(a, b).arrange(RIGHT, buff=1.4).move_to(LEFT * 2.6 + DOWN * 0.6)
        port = RoundedRectangle(corner_radius=0.12, width=0.5, height=0.28, color=INK, stroke_width=3)
        socket = VGroup(RoundedRectangle(corner_radius=0.2, width=2.2, height=1.2, color=MUTED, fill_color=PANEL,
                                         fill_opacity=1), port).move_to(LEFT * 2.6 + UP * 2.0)
        port.move_to(socket[0])
        lab_a = text("fits", SMALL, GOOD).next_to(a, DOWN, buff=0.15)
        lab_b = text("doesn't fit", SMALL, BAD).next_to(b, DOWN, buff=0.15)
        mapping = VGroup(pill("similar from a distance", MUTED, size=SMALL),
                         pill("only one fits the port", GOOD, size=SMALL),
                         pill("the connector = the exact spelling", FOCUS, size=SMALL)).arrange(DOWN, buff=0.3,
                                                                                               aligned_edge=LEFT)
        mapping.move_to(RIGHT * 3.4 + UP * 0.4)
        self.no_overlap(VGroup(a, b, lab_a, lab_b), socket, mapping)
        self.validator.check_in_frame(VGroup(a, b, socket, mapping, lab_a, lab_b))

        n = self.narrate(
            id="analogy_01",
            text="Picture two nearly identical cables, one USB-C and one Lightning. They look like the same cable until "
                 "you try to plug one in.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "cables")
        self.play(FadeIn(a, shift=UP * 0.2), FadeIn(b, shift=UP * 0.2), FadeIn(socket))
        self.at_word(n, "look")
        self.play(FadeIn(mapping[0], shift=LEFT * 0.1))
        self.at_word(n, "plug")
        for plug_, other, lab, ok in [(a, b, lab_a, True), (b, a, lab_b, False)]:
            start = plug_.get_center()
            # Stop just below the socket (tip touching its edge) instead of entering it,
            # so no two boxes overlap; the port's flash tells fit / no fit.
            docked = plug_.copy().next_to(socket, DOWN, buff=0.06).set_x(socket.get_x())
            self.no_overlap(docked, socket, other)
            self.play(Transform(plug_, docked), run_time=0.6)
            self.play(Flash(port, color=GOOD if ok else BAD, flash_radius=0.4),
                      socket[0].animate.set_stroke(GOOD if ok else BAD), run_time=0.4)
            self.play(plug_.animate.move_to(start), socket[0].animate.set_stroke(MUTED), FadeIn(lab), run_time=0.5)
        self.wait_for_narration(n)

        n = self.narrate(
            id="analogy_02",
            text="Look-alike words are the same: similar from a distance, but only one fits the port. Check the "
                 "connector, meaning the exact spelling, before you plug in.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "only")
        self.play(FadeIn(mapping[1], shift=LEFT * 0.1))
        self.at_word(n, "spelling")
        self.play(FadeIn(mapping[2], shift=LEFT * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_analogy")

    # ======================================== 5-7. WORKED EXAMPLES ==========

    def example_historic(self):
        self.scene_start("S05_ex_historic", title="Worked Example 1")

        card, q = self.context_question("The treaty was a historic moment", "historic",
                                        ["old", "momentous", "recorded", "ancient"], "b",
                                        {"a": "merely old", "c": "“historical” territory", "d": "merely old"})
        hook = hook_line(HOOKS[6][1]).next_to(q.word, RIGHT, buff=0.6)

        n = self.narrate(
            id="ex1_01",
            text="The treaty was a historic moment. Old, momentous, recorded, or ancient? Historic means important, not "
                 "merely old. The answer is momentous.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(card, shift=DOWN * 0.2), FadeIn(q.word))
        self.at_word(n, "Old")
        self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.2) for r in q.rows], lag_ratio=0.2))
        self.at_word(n, "important")
        self.play(FadeIn(hook, shift=LEFT * 0.1))
        self.at_word(n, "merely")
        anims = []
        for letter in "acd":
            anims += q.strike(letter)[1]
        self.play(*anims)
        self.at_word(n, "answer")
        self.play(*q.confirm()[1])
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_ex_historic")

    def example_disinterested(self):
        self.scene_start("S06_ex_disinterested", title="Worked Example 2")

        card, q = self.context_question("The referee must be disinterested", "disinterested",
                                        ["bored", "impartial", "careless", "absent"], "b",
                                        {"a": "belongs to “uninterested”", "c": "unrelated", "d": "unrelated"})
        hook = hook_line(HOOKS[5][1]).next_to(q.word, RIGHT, buff=0.6)

        n = self.narrate(
            id="ex2_01",
            text="The referee must be disinterested. Bored, impartial, careless, or absent? A referee must be neutral. The "
                 "answer is impartial. Bored belongs to uninterested.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(card, shift=DOWN * 0.2), FadeIn(q.word))
        self.at_word(n, "Bored", occurrence=1)
        self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.2) for r in q.rows], lag_ratio=0.2))
        self.at_word(n, "neutral")
        self.play(FadeIn(hook, shift=LEFT * 0.1))
        self.at_word(n, "answer")
        self.play(*q.confirm()[1], *q.strike("c")[1], *q.strike("d")[1])
        self.at_word(n, "Bored", occurrence=2)
        self.play(*q.strike("a")[1])
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_ex_disinterested")

    def example_continual(self):
        self.scene_start("S07_ex_continual", title="Worked Example 3")

        card, q = self.context_question("The printer made a continual clicking", "continual",
                                        ["repeated", "nonstop", "loud", "final"], "a",
                                        {"b": "that's “continuous”", "c": "unrelated", "d": "unrelated"})
        # Clicks with breaks vs one unbroken line.
        ticks = VGroup(*[Line(UP * 0.2, DOWN * 0.2, color=GOOD, stroke_width=5) for _ in range(6)]).arrange(RIGHT, buff=0.3)
        steady = Line(LEFT * 1.3, RIGHT * 1.3, color=BAD, stroke_width=5)
        waves = VGroup(VGroup(ticks, text("continual: with breaks", SMALL, GOOD)).arrange(DOWN, buff=0.2),
                       VGroup(steady, text("continuous: no break", SMALL, BAD)).arrange(DOWN, buff=0.3))\
            .arrange(DOWN, buff=0.5)
        waves.to_edge(RIGHT, buff=SAFE + 0.3).set_y(q.group.get_y())
        self.no_overlap(card, q.group, waves)
        self.validator.check_in_frame(VGroup(card, q.group, waves))

        n = self.narrate(
            id="ex3_01",
            text="The printer made a continual clicking. Repeated, nonstop, loud, or final? It clicks again and again, with "
                 "breaks. That's continual. Nonstop would be continuous. The answer is repeated.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(card, shift=DOWN * 0.2), FadeIn(q.word))
        self.at_word(n, "Repeated")
        self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.2) for r in q.rows], lag_ratio=0.2))
        self.at_word(n, "again")
        self.play(LaggedStart(*[FadeIn(t, scale=1.4) for t in ticks], lag_ratio=0.15), FadeIn(waves[0][1]))
        self.at_word(n, "Nonstop", occurrence=2)
        self.play(Create(steady), FadeIn(waves[1][1]), *q.strike("b")[1])
        self.at_word(n, "answer")
        self.play(*q.confirm()[1], *q.strike("c")[1], *q.strike("d")[1])
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S07_ex_continual")

    # ================================================ 8. RULES ==========

    def rules(self):
        self.scene_start("S08_rules", title="Rules: One Memory Hook per Pair")

        rows = VGroup()
        for pair, tokens in HOOKS:
            rows.add(VGroup(fitted_text(pair, 4.6, LABEL, MUTED), hook_line(tokens)))
        for r in rows:
            r[0].set_x(-5.8 + r[0].width / 2)
            r[1].set_x(-0.9 + r[1].width / 2)
        rows.arrange(DOWN, buff=0.28)
        for r in rows:
            r[0].set_x(-5.8 + r[0].width / 2)
            r[1].set_x(-0.9 + r[1].width / 2)
        board = self.card(rows, width=SAFE_W - 0.2)
        fit_height(board, SAFE_H - 1.2)
        board.move_to(UP * (CARD_TOP - board.height / 2))
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="rules_01",
            text="Here is one memory hook per pair. Imminent starts like immediate. Illicit starts like illegal. Complement "
                 "completes, and compliment has the I of I like you.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(board[0]))
        for r, spoken in zip(rows[:3], ["Imminent", "Illicit", "Complement"]):
            self.at_word(n, spoken)
            self.play(FadeIn(r, shift=RIGHT * 0.2), run_time=0.45)
        self.wait_for_narration(n)

        n = self.narrate(
            id="rules_02",
            text="Continuous is one unbroken stretch. Economical saves money. Disinterested means distanced, or neutral. "
                 "And historic means important.",
            voice="default",
            subtitle=True,
        )
        for r, spoken in zip(rows[3:], ["Continuous", "Economical", "Disinterested", "historic"]):
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
                             ("Check the spelling of the question word, letter by letter", WORD),
                             ("Recall its hook and predict a meaning", GOOD),
                             ("A look-alike in the options is a trap unless the meaning matches", BAD),
                             ("Confirm in a sentence", SECOND)])])
        steps.arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        board = self.card(steps).move_to(UP * 0.3)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="process_01",
            text="The process. First, check the spelling of the question word, letter by letter. Second, recall its hook "
                 "and predict a meaning. Third, treat any look-alike in the options as a trap, unless the meaning "
                 "matches. And fourth, confirm in a sentence.",
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

        h = self.HOOK
        chat = self.chat_card()
        chat.move_to(UP * (CARD_TOP - chat.height / 2))
        q = OptionQuestion("___", h["options"], h["key"], h["traps"], word_size=BODY)
        q.rows.next_to(chat, DOWN, buff=0.5).to_edge(LEFT, buff=SAFE + 0.6)
        predict = pill("predict: about to happen", STEP_COLS["PREDICT"], size=LABEL)
        predict.to_edge(RIGHT, buff=SAFE + 0.2).align_to(q.rows, UP)
        hook = hook_line(HOOKS[0][1], size=BODY)
        filled = self.chat_card(blank="imminent")
        filled.move_to(chat)
        self.no_overlap(chat, q.rows)
        self.validator.check_in_frame(VGroup(chat, q.rows, predict))

        n = self.narrate(
            id="solved_01",
            text="Let's solve the hook. Read: fill the blank in a server shutdown is blank. Predict: about to happen.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(chat), FadeIn(q.rows))
        self.at_word(n, "Predict")
        self.play(FadeIn(predict, shift=LEFT * 0.1))
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_02",
            text="Eliminate. Eminent means distinguished, which is wrong for a shutdown. Immanent means inherent, and "
                 "emanant means flowing out. Neither fits.",
            voice="default",
            subtitle=True,
        )
        for letter, spoken in [("a", "Eminent"), ("b", "Immanent"), ("d", "emanant")]:
            self.at_word(n, spoken)
            self.play(*q.strike(letter)[1])
        self.wait_for_narration(n)

        n = self.narrate(
            id="solved_03",
            text="Confirm: a server shutdown is imminent. Imminent, immediate. The answer is imminent.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "Confirm")
        self.play(ReplacementTransform(chat, filled))
        self.at_word(n, "immediate")
        hook.move_to(DOWN * 2.8)
        self.play(FadeIn(hook, shift=UP * 0.1))
        self.at_word(n, "answer")
        self.play(*q.confirm()[1])
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S10_hook_solved")

    # ========================================== 11. EXAM PATTERNS ==========

    def exam_patterns(self):
        self.scene_start("S11_patterns", title="Exam Patterns and Solving Models")

        table = self.table_rows(["Pattern", "Solving model"], [
            ["Look-alike in the options", "default to “trap” unless its meaning matches your prediction"],
            ["Question word is one half of a pair", "recall the hook; don't answer for the other half"],
            ["Sentence usage", "check the pair's hook, then substitute"],
        ], [4.6, 7.2], size=LABEL)
        board = self.card(table, width=SAFE_W - 0.2).move_to(UP * 0.4)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="patterns_01",
            text="Three exam patterns. A look-alike in the options: default to trap, unless its meaning matches your "
                 "prediction. The question word is one half of a pair: recall the hook, and don't answer for the other "
                 "half. And sentence usage: check the pair's hook, then substitute.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(board[0]), FadeIn(table[0]))
        for row, spoken in zip(table[1:], ["look-alike", "half", "usage"]):
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
            (self.verdict_card(False, "Reading too fast: eminent read as imminent", card_w),
             self.verdict_card(True, "Check the spelling letter by letter", card_w)),
            (self.verdict_card(False, "disinterested = “bored”", card_w),
             self.verdict_card(True, "disinterested = impartial", card_w)),
            (self.verdict_card(False, "historical for “important”", card_w),
             self.verdict_card(True, "historic = important", card_w)),
        ]
        for (wrong, right), yy in zip(pairs, [1.6, 0.05, -1.5]):
            wrong.move_to(LEFT_ZONE + UP * yy)
            right.move_to(RIGHT_ZONE + UP * yy)
        header = pill("3 mistakes", BAD, size=LABEL).move_to(UP * (CARD_TOP - 0.3))
        self.validator.check_in_frame(VGroup(header, *[c for p in pairs for c in p]))

        n = self.narrate(
            id="mistakes_01",
            text="Three common mistakes. The first is reading the question word too fast, so eminent is read as imminent. "
                 "The second is treating disinterested as bored. The third is using historical for important.",
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
        ("ILLICIT", None, ["drawn out", "unclear", "sick", "unlawful"], "d",
         {"a": "the meaning of “elicit”", "b": "unrelated", "c": "sound-alike (ill)"}),
        ("complements", "The scarf complements her outfit", ["praises", "completes", "copies", "hides"], "b",
         {"a": "the meaning of “compliments”", "c": "unrelated", "d": "unrelated"}),
        ("ECONOMICAL", None, ["thrifty", "financial", "costly", "wealthy"], "a",
         {"b": "the meaning of “economic”", "c": "opposite", "d": "unrelated"}),
    ]

    def practice(self):
        self.scene_start("S13_practice", title="Practice Questions")

        lines = VGroup()
        for i, (w, sent, opts, *_rest) in enumerate(self.PRACTICE):
            prompt = text(f"“{sent}”", LABEL, INK, t2c={rf"\b{w}\b": WORD}) if sent else pill(w, WORD, size=LABEL)
            lines.add(VGroup(VGroup(pill(str(i + 1), FOCUS, size=SMALL), prompt).arrange(RIGHT, buff=0.3),
                             text("   ".join(f"({l}) {o}" for l, o in zip("abcd", opts)), SMALL, MUTED))
                      .arrange(DOWN, buff=0.12, aligned_edge=LEFT))
        lines.arrange(DOWN, buff=0.4, aligned_edge=LEFT)
        board = self.card(lines, width=SAFE_W - 0.2, color=FOCUS).move_to(UP * 0.4)
        self.validator.check_in_frame(board)

        n = self.narrate(
            id="practice_01",
            text="Your turn. One: illicit. Drawn out, unclear, sick, or unlawful? Two: the scarf complements her outfit. "
                 "Praises, completes, copies, or hides? Three: economical. Thrifty, financial, costly, or wealthy?",
            voice="default",
            subtitle=True,
            pause_after=10.0,
        )
        self.play(FadeIn(board[0]))
        for ln, spoken in zip(lines, ["One", "Two", "Three"]):
            self.at_word(n, spoken)
            self.play(FadeIn(ln, shift=UP * 0.15), run_time=0.5)
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        self.clear_stage()
        self.scene_end("S13_practice")

    # =============================================== 14. ANSWERS ==========

    def answers(self):
        self.scene_start("S14_answers", title="Answers")

        rows = VGroup()
        for w, sent, opts, key, traps in self.PRACTICE:
            OptionQuestion(w, opts, key, traps)            # validates key / traps
            wrong = next(l for l, reason in traps.items() if reason.startswith("the meaning of"))
            rows.add(VGroup(pill(w, WORD, size=LABEL), text("→", LABEL, MUTED),
                            pill(f"({key}) {opts['abcd'.index(key)]}", GOOD, size=LABEL),
                            text(f"({wrong}) {opts['abcd'.index(wrong)]}: {traps[wrong]}", SMALL, BAD))
                     .arrange(RIGHT, buff=0.3))
        rows.arrange(DOWN, buff=0.45, aligned_edge=LEFT)
        fit_width(rows, SAFE_W).move_to(UP * 0.3)
        self.validator.check_in_frame(rows)

        n = self.narrate(
            id="answers_01",
            text="One: unlawful. Drawn out is the meaning of elicit. Two: completes. Praises is the meaning of compliments. "
                 "Three: thrifty. Financial is the meaning of economic.",
            voice="default",
            subtitle=True,
        )
        for r, spoken in zip(rows, ["unlawful", "completes", "thrifty"]):
            self.at_word(n, spoken)
            self.play(FadeIn(r, shift=RIGHT * 0.2), run_time=0.6)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S14_answers")

    # ================================================ 15. RECAP ==========

    def recap(self):
        self.scene_start("S15_recap", title="Recap Card")

        card, table = self.recap_card("Recap Card: Video 4", [
            ["Look-alikes", "different words, similar spelling: usually traps"],
            ["eminent / imminent", "distinguished / about to happen"],
            ["disinterested / uninterested", "impartial / bored"],
            ["continual / continuous", "with breaks / without breaks"],
            ["historic / historical", "important / about the past"],
        ])
        card.move_to(UP * 0.2)
        self.validator.check_in_frame(card)

        n = self.narrate(
            id="recap_01",
            text="To recap. Look-alikes are different words with similar spelling, and they're usually traps. Eminent is "
                 "distinguished; imminent is about to happen. Disinterested is impartial; uninterested is bored. Continual "
                 "has breaks; continuous doesn't. And historic is important, while historical is about the past.",
            voice="default",
            subtitle=True,
        )
        self.play(FadeIn(card[0]), FadeIn(table[0]))
        for row, spoken in zip(table[1:], ["Look-alikes", "Eminent", "Disinterested", "Continual", "historic"]):
            self.at_word(n, spoken)
            self.play(FadeIn(row, shift=RIGHT * 0.2), run_time=0.45)
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S15_recap")

    # ================================================= 16. NEXT ==========

    def next_video(self):
        self.scene_start("S16_next", title="Next")

        word = VGroup(pill("bene", GOOD, size=BODY), text("+", TITLE, MUTED), pill("volent", MUTED, size=BODY))\
            .arrange(RIGHT, buff=0.3)
        gloss = text("good + wishing  →  kind", LABEL, GOOD)
        nxt = pill("Next:  Exam-Oriented Synonyms", FOCUS, size=BODY)
        VGroup(word, gloss, nxt).arrange(DOWN, buff=0.6).move_to(UP * 0.2)
        self.no_overlap(word, gloss, nxt)
        self.validator.check_in_frame(VGroup(word, gloss, nxt))

        n = self.narrate(
            id="next_01",
            text="Video five gives you the high-frequency exam words, and a root-based way to decode the ones you've never "
                 "seen.",
            voice="default",
            subtitle=True,
        )
        self.at_word(n, "high-frequency")
        self.play(FadeIn(nxt, scale=1.1))
        self.at_word(n, "root-based")
        self.play(FadeIn(word, shift=UP * 0.1))
        self.play(FadeIn(gloss, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage(run_time=1.0)
        self.scene_end("S16_next")

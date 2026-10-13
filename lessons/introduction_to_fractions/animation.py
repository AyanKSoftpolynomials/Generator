"""
Introduction To Fractions

Generated from a natural teaching script by the local script generator
(template: Project Default). The class name is the video title.
Scenes: hook (title_card), what_is_a_fraction (definition), how_to_compare_fractions (steps), worked_example (equations), question (question), summary (bullets).
Edit freely: this is an ordinary animation.py.
"""

from manim import *
from src.animation import LMSScene



# ---------------------------------------------- style
KIT_BACKGROUND = None
KIT_TEXT = "#E2E8F0"
KIT_MUTED = "#94A3B8"
KIT_ACCENT = "#38BDF8"
KIT_ACCENT_2 = "#A78BFA"
KIT_GOOD = "#34D399"
KIT_BAD = "#F87171"
KIT_WARN = "#FBBF24"
KIT_FONT = ""


class LessonKit:
    """Layout-safe building blocks for generated lessons (mixed into the LMSScene class).

    Every text is wrapped to the width it is given by measuring real glyphs,
    shrinks for height only down to KIT_MIN_FONT, and every card registers its
    text with self.validator.check_fit(), so text never leaves its box.
    """

    KIT_WIDTH = 12.4           # usable content width (frame 14.2 minus safe margins)
    KIT_BOTTOM = -3.5          # lowest content edge
    KIT_MIN_FONT = 20          # generated text never gets smaller than this

    # -- setup / frame -------------------------------------------------------

    def kit_setup(self):
        if KIT_BACKGROUND:
            self.camera.background_color = KIT_BACKGROUND
        self._kit_top = 3.35
        self._kit_widths = {}

    def kit_clear(self, run_time=0.6):
        """Fade everything out: every section starts on a clean frame."""
        if self.mobjects:
            self.play(*[FadeOut(m) for m in self.mobjects], run_time=run_time)
        self._kit_top = 3.35

    def kit_place(self, group, gap=0.35):
        """Centre ``group`` in the free area under the title, scaled down only if it cannot fit."""
        top = self._kit_top - gap
        height, width = top - self.KIT_BOTTOM, self.KIT_WIDTH
        if group.height > height:
            group.scale_to_fit_height(height)
        if group.width > width:
            group.scale_to_fit_width(width)
        group.move_to([0, (top + self.KIT_BOTTOM) / 2, 0])
        return group

    # -- text ----------------------------------------------------------------

    def _kit_font(self):
        return {"font": KIT_FONT} if KIT_FONT else {}

    def _kit_measure(self, text, size, weight):
        key = (text, size, weight)
        if key not in self._kit_widths:
            self._kit_widths[key] = Text(text, font_size=size, weight=weight, **self._kit_font()).width
        return self._kit_widths[key]

    def _kit_wrap(self, text, width, size, weight):
        lines, current = [], ""
        for word in text.split():
            trial = f"{current} {word}".strip()
            if current and self._kit_measure(trial, size, weight) > width:
                lines.append(current)
                current = word
            else:
                current = trial
        return lines + ([current] if current else [])

    def kit_text(self, text, width, size=30, color=None, weight=NORMAL, align="center", max_height=None):
        """``text`` wrapped to ``width``; smaller font (not below KIT_MIN_FONT) until it fits ``max_height``."""
        size = max(size, self.KIT_MIN_FONT)
        while True:
            lines = self._kit_wrap(text, width, size, weight) or [" "]
            group = VGroup(*[Text(line, font_size=size, color=color or KIT_TEXT, weight=weight, **self._kit_font())
                             for line in lines])
            group.arrange(DOWN, buff=0.14 * size / 30, aligned_edge=LEFT if align == "left" else ORIGIN)
            if max_height is None or group.height <= max_height or size <= self.KIT_MIN_FONT:
                break
            size = max(self.KIT_MIN_FONT, int(size * 0.9))
        if group.width > width:                       # one unbreakable word wider than the space
            group.scale_to_fit_width(width)
        return group

    def kit_title(self, text):
        """Section title at the top, with an accent bar; content goes below it."""
        title = self.kit_text(text, self.KIT_WIDTH, size=40, weight=BOLD, max_height=1.15)
        title.to_edge(UP, buff=0.42)
        bar = RoundedRectangle(width=min(max(title.width, 1.2), 3.2), height=0.07, corner_radius=0.035,
                               stroke_width=0, fill_color=KIT_ACCENT, fill_opacity=1)
        bar.next_to(title, DOWN, buff=0.16)
        self._kit_top = bar.get_bottom()[1]
        return VGroup(title, bar)

    def kit_title_card(self, title, subtitle=None):
        """Big centred title (openings and closings)."""
        head = self.kit_text(title, 11.5, size=52, weight=BOLD, color=KIT_TEXT, max_height=2.2)
        bar = RoundedRectangle(width=min(head.width, 4), height=0.08, corner_radius=0.04, stroke_width=0,
                               fill_color=KIT_ACCENT, fill_opacity=1)
        parts = [head, bar]
        if subtitle:
            parts.append(self.kit_text(subtitle, 10.5, size=30, color=KIT_MUTED, max_height=1.8))
        return VGroup(*parts).arrange(DOWN, buff=0.35).move_to(ORIGIN)

    # -- cards and lists -----------------------------------------------------

    def kit_card(self, body, width=5.6, heading=None, color=None, size=30, min_height=0.0, align="center"):
        """A rounded box whose text is wrapped to fit it (checked by the layout validator)."""
        color = color or KIT_ACCENT
        inner = width - 0.6
        parts = []
        if heading:
            parts.append(self.kit_text(heading, inner, size=size + 2, weight=BOLD, color=color))
        if isinstance(body, (list, tuple)):
            parts.append(self.kit_bullets(body, width=inner, size=size, max_height=None))
        elif body:
            parts.append(self.kit_text(body, inner, size=size, align=align))
        content = VGroup(*parts).arrange(DOWN, buff=0.22, aligned_edge=LEFT if align == "left" else ORIGIN)
        box = RoundedRectangle(width=width, height=max(content.height + 0.55, min_height), corner_radius=0.16,
                               stroke_color=color, stroke_width=2.4, fill_color=color, fill_opacity=0.08)
        content.move_to(box)
        self.validator.check_fit(content, box, margin=0.15)
        return VGroup(box, content)

    def kit_bullets(self, points, width=11.6, size=34, color=None, numbered=False, max_height=4.9):
        """One row per point (marker + wrapped text), smaller font if the list is too tall."""
        color = color or KIT_ACCENT
        while True:
            rows = VGroup()
            for i, point in enumerate(points, 1):
                if numbered:
                    marker = Text(f"{i}.", font_size=size, weight=BOLD, color=color, **self._kit_font())
                else:
                    marker = Dot(radius=0.075 * size / 28, color=color)
                text = self.kit_text(point, width - 0.55, size=size, align="left")
                marker.next_to(text[0], LEFT, buff=0.22)
                rows.add(VGroup(marker, text))
            rows.arrange(DOWN, buff=0.3 * size / 28, aligned_edge=LEFT)
            if max_height is None or rows.height <= max_height or size <= self.KIT_MIN_FONT:
                return rows
            size = max(self.KIT_MIN_FONT, int(size * 0.9))

    def kit_definition(self, term, meaning):
        head = self.kit_text(term, 11.0, size=50, weight=BOLD, color=KIT_ACCENT, max_height=1.3)
        card = self.kit_card(meaning, width=11.0, size=34)
        return VGroup(head, card).arrange(DOWN, buff=0.45)

    def kit_compare(self, left, left_points, right, right_points):
        """Two cards side by side (equal height) with a "VS" badge between them."""
        cards = [self.kit_card(points or [" "], width=5.5, heading=name, color=color, size=30, align="left")
                 for name, points, color in ((left, left_points, KIT_ACCENT), (right, right_points, KIT_ACCENT_2))]
        height = max(c[0].height for c in cards)
        cards = [self.kit_card(points or [" "], width=5.5, heading=name, color=color, size=30, align="left",
                               min_height=height)
                 for name, points, color in ((left, left_points, KIT_ACCENT), (right, right_points, KIT_ACCENT_2))]
        badge = VGroup(Circle(radius=0.42, stroke_color=KIT_MUTED, stroke_width=2, fill_color=KIT_MUTED,
                              fill_opacity=0.12),
                       Text("VS", font_size=26, weight=BOLD, color=KIT_TEXT, **self._kit_font()))
        row = VGroup(cards[0], badge, cards[1]).arrange(RIGHT, buff=0.35)
        return row

    def kit_steps(self, steps):
        """Short steps: chips in a row with arrows; longer ones: a numbered column."""
        n = len(steps)
        if n <= 4 and max(len(s.split()) for s in steps) <= 7:
            width = min(2.9, (self.KIT_WIDTH - 0.75 * (n - 1)) / n)
            chips = VGroup(*[self.kit_card(step, width=width, heading=f"Step {i}", size=28)
                             for i, step in enumerate(steps, 1)]).arrange(RIGHT, buff=0.75)
            height = max(c[0].height for c in chips)
            chips = VGroup(*[self.kit_card(step, width=width, heading=f"Step {i}", size=28, min_height=height)
                             for i, step in enumerate(steps, 1)]).arrange(RIGHT, buff=0.75)
            arrows = [Arrow(a.get_right(), b.get_left(), buff=0.08, stroke_width=4, color=KIT_MUTED,
                            max_tip_length_to_length_ratio=0.35) for a, b in zip(chips, chips[1:])]
            return chips, arrows
        rows = VGroup()
        for i, step in enumerate(steps, 1):
            badge = VGroup(Circle(radius=0.3, stroke_color=KIT_ACCENT, stroke_width=2.4, fill_color=KIT_ACCENT,
                                  fill_opacity=0.15),
                           Text(str(i), font_size=26, weight=BOLD, color=KIT_TEXT, **self._kit_font()))
            text = self.kit_text(step, 10.6, size=34, align="left")
            text.next_to(badge, RIGHT, buff=0.3)
            rows.add(VGroup(badge, text))
        rows.arrange(DOWN, buff=0.4, aligned_edge=LEFT)
        return rows, []

    # -- sequences and transformations ---------------------------------------

    def kit_tile(self, label, size=0.9, color=None):
        box = RoundedRectangle(width=size, height=size, corner_radius=0.1, stroke_color=color or KIT_ACCENT,
                               stroke_width=2.2, fill_color=color or KIT_ACCENT, fill_opacity=0.1)
        text = Text(str(label), font_size=44, weight=BOLD, color=KIT_TEXT, **self._kit_font())
        text.scale_to_fit_height(min(text.height, size * 0.5))
        if text.width > size * 0.75:
            text.scale_to_fit_width(size * 0.75)
        text.move_to(box)
        return VGroup(box, text)

    def kit_sequence(self, items, steps=None):
        """A row of tiles with the change between neighbours ("+2") on arcs above them."""
        n = len(items)
        size = min(1.4, (self.KIT_WIDTH - 0.4 * (n - 1)) / n)
        tiles = VGroup(*[self.kit_tile(v, size=size, color=KIT_WARN if str(v) in ("?", "_") else None)
                         for v in items]).arrange(RIGHT, buff=0.35)
        arcs, labels = VGroup(), VGroup()
        for i, step in enumerate(steps or []):
            if i + 1 >= n:
                break
            arc = CurvedArrow(tiles[i].get_top() + UP * 0.08, tiles[i + 1].get_top() + UP * 0.08, angle=-PI / 2.2,
                              color=KIT_MUTED, stroke_width=2.5, tip_length=0.14)
            label = Text(step, font_size=28, color=KIT_ACCENT_2, weight=BOLD, **self._kit_font())
            label.next_to(arc, UP, buff=0.06)
            arcs.add(arc)
            labels.add(label)
        return tiles, arcs, labels

    def kit_code_rows(self, source, target, steps):
        """Word coding: each letter of ``source``, an arrow with its shift, the letter of ``target``."""
        n = len(source)
        size = min(1.35, (self.KIT_WIDTH - 0.6 * (n - 1)) / n)
        top = VGroup(*[self.kit_tile(c, size=size) for c in source]).arrange(RIGHT, buff=0.5)
        bottom = VGroup(*[self.kit_tile(c, size=size, color=KIT_GOOD) for c in target]).arrange(RIGHT, buff=0.5)
        bottom.next_to(top, DOWN, buff=1.5)
        arrows, labels = VGroup(), VGroup()
        for a, b, step in zip(top, bottom, steps):
            arrow = Arrow(a.get_bottom(), b.get_top(), buff=0.1, stroke_width=4, color=KIT_MUTED)
            label = Text(step, font_size=28, weight=BOLD, color=KIT_ACCENT_2, **self._kit_font())
            label.next_to(arrow, RIGHT, buff=0.08)
            arrows.add(arrow)
            labels.add(label)
        return top, arrows, labels, bottom

    # -- maths and questions -------------------------------------------------

    def kit_equation(self, line, size=54):
        """MathTex for plain arithmetic/algebra, Text otherwise (never a LaTeX error)."""
        latex = line.replace("×", r"\times ").replace("÷", r"\div ").replace("*", r"\times ")
        latex = latex.replace("²", "^2").replace("³", "^3").replace("%", r"\%")
        simple = all(ch.isalnum() or ch in " +-=().,/^<>\\%" for ch in latex)
        mob = MathTex(latex, font_size=size, color=KIT_TEXT) if simple else \
            Text(line, font_size=int(size * 0.8), color=KIT_TEXT, **self._kit_font())
        if mob.width > 11.0:
            mob.scale_to_fit_width(11.0)
        return mob

    def kit_equations(self, lines):
        return VGroup(*[self.kit_equation(line) for line in lines]).arrange(DOWN, buff=0.4)

    def kit_question(self, question, options, labels=None):
        """Question card with option cards in a grid (2 columns for 3-4 options)."""
        labels = labels or [chr(65 + i) for i in range(len(options))]
        q = self.kit_card(question, width=12.0, size=34, color=KIT_ACCENT_2)
        cols = 2 if len(options) > 2 else len(options)
        width = 5.8 if cols == 2 else min(5.8, 11.6 / max(cols, 1))
        cards = [self.kit_card(f"({l}) {o}", width=width, size=30, color=KIT_MUTED) for l, o in zip(labels, options)]
        height = max(c[0].height for c in cards)
        cards = [self.kit_card(f"({l}) {o}", width=width, size=30, color=KIT_MUTED, min_height=height)
                 for l, o in zip(labels, options)]
        grid = VGroup(*cards).arrange_in_grid(cols=cols, buff=(0.3, 0.25))
        return q, grid

    def kit_mark_answer(self, card):
        """Animations that mark an option card as the correct answer."""
        return [card[0].animate.set_stroke(KIT_GOOD, width=4).set_fill(KIT_GOOD, opacity=0.18),
                Indicate(card[1], color=KIT_GOOD, scale_factor=1.06)]


class IntroductionToFractions(LessonKit, LMSScene):
    """Introduction To Fractions: generated from a teaching script (template: Project Default)."""

    default_voice = "teacher_a"

    def construct(self):
        self.kit_setup()

        # -------------------------------------------------------- 1. Hook (hook -> title_card)
        self.scene_start('hook', title='Hook')
        card = self.kit_title_card('Introduction To Fractions', None)
        n = self.narrate('hook_01', (
            'Have you ever shared a pizza with your friends and wondered how much each '
            'person really gets? Today we will learn how to describe parts of a whole.'
        ))
        self.play(FadeIn(card, shift=UP * 0.2), run_time=1.2)
        self.wait_for_narration(n)
        self.kit_clear()

        # ----------------------------------------- 2. What is a fraction? (definition -> definition)
        self.scene_start('what_is_a_fraction', title='What is a fraction?')
        title = self.kit_title('What is a fraction?')
        definition = self.kit_definition('fraction', 'Number that represents a part of a whole')
        self.kit_place(definition)
        n = self.narrate('what_is_a_fraction_01', 'A fraction is a number that represents a part of a whole.')
        self.play(FadeIn(title, shift=DOWN * 0.2), Write(definition[0]), run_time=1.4)
        n = self.narrate('what_is_a_fraction_02', (
            'The top number is called the numerator and the bottom number is called the '
            'denominator.'
        ))
        self.play(FadeIn(definition[1], shift=UP * 0.2), run_time=1.2)
        self.wait_for_narration(n)
        self.kit_clear()

        # ------------------------------------ 3. How to compare fractions (process -> steps)
        self.scene_start('how_to_compare_fractions', title='How to compare fractions')
        title = self.kit_title('How to compare fractions')
        steps, arrows = self.kit_steps([
            'Make the denominators the same',
            'Compare the numerators',
            'The bigger numerator gives the bigger fraction',
        ])
        self.kit_place(VGroup(steps, *arrows))
        n = self.narrate('how_to_compare_fractions_01', 'Make the denominators the same.')
        self.play(FadeIn(title, shift=DOWN * 0.2), FadeIn(steps[0], shift=UP * 0.2), run_time=1.4)
        n = self.narrate('how_to_compare_fractions_02', 'Compare the numerators.')
        self.play(FadeIn(steps[1], shift=UP * 0.2), *[GrowArrow(a) for a in arrows[0:1]], run_time=1.2)
        n = self.narrate('how_to_compare_fractions_03', 'The bigger numerator gives the bigger fraction.')
        self.play(FadeIn(steps[2], shift=UP * 0.2), *[GrowArrow(a) for a in arrows[1:2]], run_time=1.2)
        self.wait_for_narration(n)
        self.kit_clear()

        # ---------------------------------------------- 4. Worked example (example -> equations)
        self.scene_start('worked_example', title='Worked example')
        title = self.kit_title('Worked example')
        equations = self.kit_place(self.kit_equations(['1/4 + 2/4 = 3/4']))
        n = self.narrate('worked_example_01', 'Add the fractions.')
        self.play(FadeIn(title, shift=DOWN * 0.2), run_time=1.2)
        n = self.narrate('worked_example_02', '1/4 plus 2/4 equals 3/4.')
        self.play(Write(equations[0]), run_time=1.2)
        self.wait_for_narration(n)
        self.kit_clear()

        # ---------------------------------------------------- 5. Question (question -> question)
        self.scene_start('question', title='Question')
        title = self.kit_title('Question')
        question, options = self.kit_question(
            'Which fraction is the largest?',
            ['1/2', '1/3', '3/4', '1/4'],
            ['A', 'B', 'C', 'D'],
        )
        self.kit_place(VGroup(question, options).arrange(DOWN, buff=0.45))
        n = self.narrate('question_01', 'Which fraction is the largest?')
        self.play(FadeIn(title, shift=DOWN * 0.2), FadeIn(question, shift=DOWN * 0.2), run_time=1.4)
        n = self.narrate('question_02', 'The options are. A: 1/2. B: 1/3. C: 3/4. D: 1/4.')
        self.play(LaggedStart(*[FadeIn(o, shift=UP * 0.15) for o in options], lag_ratio=0.15), run_time=1.2)
        n = self.narrate('question_03', 'The answer is (c) 3/4.')
        self.play(*self.kit_mark_answer(options[2]), run_time=1.2)
        self.wait_for_narration(n)
        self.kit_clear()

        # ----------------------------------------------------- 6. Summary (summary -> bullets)
        self.scene_start('summary', title='Summary')
        title = self.kit_title('Summary')
        points = self.kit_place(self.kit_bullets(
            [
                'A fraction describes a part of a whole',
                'Always compare fractions with the same denominator',
            ],
            color=KIT_GOOD, numbered=True,
        ))
        n = self.narrate('summary_01', 'A fraction describes a part of a whole.')
        self.play(FadeIn(title, shift=DOWN * 0.2), FadeIn(points[0], shift=RIGHT * 0.2), run_time=1.4)
        n = self.narrate('summary_02', 'Always compare fractions with the same denominator.')
        self.play(FadeIn(points[1], shift=RIGHT * 0.2), run_time=1.2)
        self.wait_for_narration(n)
        self.kit_clear()

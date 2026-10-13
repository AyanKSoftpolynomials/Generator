from manim import *
from src.animation.lms_scene import LMSScene


class WholeNumbersVideo(LMSScene):
    """
    Whole Numbers
    Educational animated lesson.

    Visual concept:
        Natural Numbers
                +
               ZERO
                ↓
         Whole Numbers

    Narration/audio/subtitle metadata is registered through
    self.narrate(). The video generator automatically handles:
        - TTS
        - voice selection
        - audio duration
        - WhisperX alignment
        - subtitles
        - timing
        - final composition
    """

    # ---------------------------------------------------------
    # THEME
    # ---------------------------------------------------------

    BG = BLACK
    WHITE = "#FFFFFF"
    YELLOW = "#FFD54A"
    BLUE = "#4FC3F7"
    GREEN = "#66BB6A"
    RED = "#FF5252"
    PURPLE = "#B388FF"
    GREY = "#A0A0A0"

    def construct(self):

        self.camera.background_color = self.BG

        self.hook()
        self.introduction()
        self.how()
        self.what()
        self.why()
        self.real_world_example()
        self.summary()
        self.done()

    # =========================================================
    # COMMON HELPERS
    # =========================================================

    def title_text(self, text, color=None, size=52):
        return Text(
            text,
            font_size=size,
            color=color or self.WHITE,
            weight=BOLD,
        )

    def label(self, text, color=None, size=34):
        return Text(
            text,
            font_size=size,
            color=color or self.WHITE,
        )

    def number(self, value, color=None, size=48):
        return Text(
            str(value),
            font_size=size,
            color=color or self.WHITE,
            weight=BOLD,
        )

    def highlight_box(self, mob, color=None, buff=0.18):
        return SurroundingRectangle(
            mob,
            color=color or self.YELLOW,
            buff=buff,
            stroke_width=3,
        )

    def create_number_row(
        self,
        values,
        start_x=-5.5,
        spacing=1.35,
        color=None,
        size=44,
    ):
        group = VGroup()

        for i, value in enumerate(values):
            n = self.number(value, color=color, size=size)
            n.move_to(
                np.array(
                    [
                        start_x + i * spacing,
                        0,
                        0,
                    ]
                )
            )
            group.add(n)

        return group

    # =========================================================
    # 1. HOOK
    # =========================================================

    def hook(self):

        self.scene_start("hook")

        # -----------------------------------------------------
        # Narration 1
        # -----------------------------------------------------

        n = self.narrate(
            id="hook_01",
            text="Hello again, my dear students!",
            voice="teacher_a",
            subtitle=True,
        )

        greeting = self.title_text(
            "Hello again, my dear students!",
            color=self.YELLOW,
            size=48,
        )

        self.play(
            FadeIn(greeting, shift=UP * 0.3),
            run_time=self.duration_of(n),
        )

        self.wait_for_narration(n)

        self.play(
            FadeOut(greeting),
            run_time=0.35,
        )

        # -----------------------------------------------------
        # Narration 2
        # -----------------------------------------------------

        n = self.narrate(
            id="hook_02",
            text=(
                "If your pocket has zero rupees in it right now, "
                "is that a real, valid amount you could honestly state?"
            ),
            voice="teacher_a",
            subtitle=True,
        )

        # Wallet
        wallet = RoundedRectangle(
            width=3.0,
            height=2.0,
            corner_radius=0.25,
            color=self.BLUE,
            stroke_width=4,
        )

        wallet_label = Text(
            "WALLET",
            font_size=30,
            color=self.BLUE,
            weight=BOLD,
        )

        wallet_group = VGroup(wallet, wallet_label)
        wallet_label.move_to(wallet)

        wallet_group.shift(LEFT * 3)

        # ₹0
        rupees = Text(
            "₹ 0",
            font_size=72,
            color=self.YELLOW,
            weight=BOLD,
        )

        rupees.next_to(wallet_group, RIGHT, buff=1.2)

        question = Text(
            "A real amount?",
            font_size=42,
            color=self.WHITE,
        )

        question.to_edge(DOWN)

        self.play(
            Create(wallet),
            FadeIn(wallet_label),
            run_time=0.8,
        )

        self.play(
            FadeIn(rupees, scale=1.2),
            run_time=0.6,
        )

        self.play(
            FadeIn(question, shift=UP * 0.2),
            run_time=0.5,
        )

        self.wait_for_narration(n)

        # -----------------------------------------------------
        # Narration 3
        # -----------------------------------------------------

        n = self.narrate(
            id="hook_03",
            text="Of course it is!",
            voice="teacher_a",
            subtitle=True,
        )

        answer = Text(
            "YES!",
            font_size=90,
            color=self.GREEN,
            weight=BOLD,
        )

        answer.move_to(question)

        self.play(
            Transform(question, answer),
            run_time=0.45,
        )

        self.play(
            Indicate(
                rupees,
                color=self.GREEN,
                scale_factor=1.15,
            ),
            run_time=0.7,
        )

        self.wait_for_narration(n)

        # -----------------------------------------------------
        # Narration 4
        # -----------------------------------------------------

        n = self.narrate(
            id="hook_04",
            text=(
                "And yet, our natural numbers from last time "
                "don't include zero at all."
            ),
            voice="teacher_a",
            subtitle=True,
        )

        natural_label = Text(
            "Natural Numbers",
            font_size=42,
            color=self.BLUE,
            weight=BOLD,
        )

        natural_numbers = self.create_number_row(
            [1, 2, 3, 4, 5],
            start_x=-4.2,
            spacing=1.25,
            color=self.WHITE,
        )

        natural_group = VGroup(
            natural_label,
            natural_numbers,
        )

        natural_label.next_to(
            natural_numbers,
            UP,
            buff=0.45,
        )

        # Emoji (❌) can't be rendered by Manim's text engine; draw the cross.
        zero_text = Text(
            "0",
            font_size=55,
            color=self.RED,
            weight=BOLD,
        )

        zero_missing = VGroup(
            zero_text,
            Cross(zero_text, stroke_color=self.RED, stroke_width=6, scale_factor=1.6),
        )

        zero_missing.next_to(
            natural_numbers,
            DOWN,
            buff=0.6,
        )

        self.play(
            FadeOut(wallet_group),
            FadeOut(rupees),
            FadeOut(question),
            run_time=0.3,
        )

        self.play(
            FadeIn(natural_label),
            LaggedStart(
                *[
                    FadeIn(x, shift=UP * 0.25)
                    for x in natural_numbers
                ],
                lag_ratio=0.1,
            ),
            run_time=1.2,
        )

        self.play(
            FadeIn(zero_missing, scale=1.2),
            run_time=0.5,
        )

        self.wait_for_narration(n)

        # -----------------------------------------------------
        # Narration 5
        # -----------------------------------------------------

        n = self.narrate(
            id="hook_05",
            text="Let's fix that small gap today.",
            voice="teacher_a",
            subtitle=True,
        )

        gap_arrow = Arrow(
            start=LEFT * 0.5,
            end=RIGHT * 0.5,
            color=self.YELLOW,
            stroke_width=5,
        )

        gap_arrow.move_to(
            np.array([0, -2.0, 0])
        )

        fix_text = Text(
            "ADD ZERO",
            font_size=50,
            color=self.YELLOW,
            weight=BOLD,
        )

        fix_text.next_to(
            gap_arrow,
            DOWN,
            buff=0.25,
        )

        self.play(
            GrowArrow(gap_arrow),
            FadeIn(fix_text, scale=1.1),
            run_time=self.duration_of(n),
        )

        self.wait_for_narration(n)

        self.play(
            FadeOut(
                VGroup(
                    natural_label,
                    natural_numbers,
                    zero_missing,
                    gap_arrow,
                    fix_text,
                )
            ),
            run_time=0.5,
        )

    # =========================================================
    # 2. INTRODUCTION
    # =========================================================

    def introduction(self):

        self.scene_start("introduction")

        n = self.narrate(
            id="intro_01",
            text=(
                "Welcome back! Today we meet Whole Numbers — "
                "our natural numbers, plus one small but important newcomer."
            ),
            voice="teacher_a",
            subtitle=True,
        )

        whole_title = self.title_text(
            "WHOLE NUMBERS",
            color=self.YELLOW,
            size=64,
        )

        whole_title.move_to(UP * 1.8)

        natural = Text(
            "Natural Numbers",
            font_size=40,
            color=self.BLUE,
            weight=BOLD,
        )

        plus = Text(
            "+",
            font_size=52,
            color=self.WHITE,
            weight=BOLD,
        )

        zero = Text(
            "0",
            font_size=60,
            color=self.YELLOW,
            weight=BOLD,
        )

        equation = VGroup(
            natural,
            plus,
            zero,
        ).arrange(
            RIGHT,
            buff=0.4,
        )

        equation.move_to(DOWN * 0.3)

        result_line = Text(
            "WHOLE NUMBERS",
            font_size=48,
            color=self.GREEN,
            weight=BOLD,
        )

        result_line.move_to(DOWN * 1.8)

        self.play(
            FadeIn(whole_title, shift=DOWN * 0.3),
            run_time=0.7,
        )

        self.play(
            FadeIn(natural),
            FadeIn(plus),
            FadeIn(zero, scale=1.4),
            run_time=1.0,
        )

        self.play(
            FadeIn(result_line, shift=UP * 0.3),
            run_time=0.7,
        )

        self.wait_for_narration(n)

        self.play(
            FadeOut(
                VGroup(
                    whole_title,
                    equation,
                    result_line,
                )
            ),
            run_time=0.45,
        )

    # =========================================================
    # 3. HOW
    # =========================================================

    def how(self):

        self.scene_start("how")

        n = self.narrate(
            id="how_01",
            text=(
                "So how do whole numbers differ? My dear students, "
                "they're built by simply adding zero to the natural "
                "numbers we already know — nothing else changes."
            ),
            voice="teacher_a",
            subtitle=True,
        )

        # Natural numbers
        natural_label = Text(
            "Natural Numbers",
            font_size=36,
            color=self.BLUE,
            weight=BOLD,
        )

        natural_numbers = self.create_number_row(
            [1, 2, 3, 4, 5],
            start_x=-4.0,
            spacing=1.25,
            color=self.WHITE,
            size=42,
        )

        natural_label.next_to(
            natural_numbers,
            UP,
            buff=0.45,
        )

        # Zero
        zero = Text(
            "0",
            font_size=70,
            color=self.YELLOW,
            weight=BOLD,
        )

        zero.move_to(
            np.array([-5.2, -1.7, 0])
        )

        zero_arrow = Arrow(
            start=zero.get_top(),
            end=natural_numbers[0].get_bottom(),
            color=self.YELLOW,
            stroke_width=4,
        )

        whole_label = Text(
            "Whole Numbers",
            font_size=40,
            color=self.GREEN,
            weight=BOLD,
        )

        whole_numbers = self.create_number_row(
            [0, 1, 2, 3, 4, 5],
            start_x=-4.6,
            spacing=1.55,
            color=self.WHITE,
            size=42,
        )

        whole_label.next_to(
            whole_numbers,
            UP,
            buff=0.45,
        )

        self.play(
            FadeIn(natural_label),
            FadeIn(natural_numbers),
            run_time=1.0,
        )

        self.play(
            FadeIn(zero, scale=1.4),
            GrowArrow(zero_arrow),
            run_time=0.7,
        )

        # ReplacementTransform (not Transform on copies): the natural row
        # turns INTO the whole row, so nothing is left behind on screen.
        self.play(
            ReplacementTransform(
                VGroup(
                    natural_label,
                    natural_numbers,
                ),
                VGroup(
                    whole_label,
                    whole_numbers,
                ),
            ),
            run_time=1.0,
        )

        self.wait_for_narration(n)

        # "Nothing else changes"
        unchanged = Text(
            "Nothing else changes.",
            font_size=44,
            color=self.YELLOW,
            weight=BOLD,
        )

        unchanged.to_edge(DOWN)

        self.play(
            FadeIn(unchanged, shift=UP * 0.2),
            run_time=0.5,
        )

        self.play(
            Indicate(
                whole_numbers,
                color=self.GREEN,
            ),
            run_time=0.8,
        )

        self.wait(0.4)

        self.play(
            FadeOut(
                VGroup(
                    whole_label,
                    whole_numbers,
                    zero,
                    zero_arrow,
                    unchanged,
                )
            ),
            run_time=0.5,
        )

    # =========================================================
    # 4. WHAT
    # =========================================================

    def what(self):

        self.scene_start("what")

        n = self.narrate(
            id="what_01",
            text=(
                "Whole numbers are 0, 1, 2, 3, 4, and onward."
            ),
            voice="teacher_a",
            subtitle=True,
        )

        numbers = self.create_number_row(
            [0, 1, 2, 3, 4, 5, 6],
            start_x=-4.7,
            spacing=1.45,
            color=self.WHITE,
            size=46,
        )

        title = self.title_text(
            "WHOLE NUMBERS",
            color=self.GREEN,
            size=52,
        )

        title.to_edge(UP)

        self.play(
            FadeIn(title, shift=DOWN * 0.25),
            run_time=0.6,
        )

        self.play(
            LaggedStart(
                *[
                    FadeIn(num, shift=UP * 0.3)
                    for num in numbers
                ],
                lag_ratio=0.12,
            ),
            run_time=1.4,
        )

        self.wait_for_narration(n)

        # -----------------------------------------------------
        # Negative numbers exclusion
        # -----------------------------------------------------

        n = self.narrate(
            id="what_02",
            text=(
                "Still no negative numbers, still no fractions — "
                "just our familiar counting numbers, now joined by zero."
            ),
            voice="teacher_a",
            subtitle=True,
        )

        negatives = VGroup(
            Text("-3", font_size=44),
            Text("-2", font_size=44),
            Text("-1", font_size=44),
        ).arrange(
            RIGHT,
            buff=0.6,
        )

        negatives.move_to(
            DOWN * 1.4
        )

        negative_label = Text(
            "Negative numbers",
            font_size=30,
            color=self.RED,
        )

        negative_label.next_to(
            negatives,
            DOWN,
            buff=0.25,
        )

        cross = VGroup(
            Line(
                negatives.get_corner(UL),
                negatives.get_corner(DR),
                color=self.RED,
                stroke_width=7,
            ),
            Line(
                negatives.get_corner(UR),
                negatives.get_corner(DL),
                color=self.RED,
                stroke_width=7,
            ),
        )

        self.play(
            FadeIn(negatives),
            FadeIn(negative_label),
            run_time=0.5,
        )

        self.play(
            Create(cross),
            run_time=0.5,
        )

        self.wait_for_narration(n)

        # -----------------------------------------------------
        # Fractions
        # -----------------------------------------------------

        fractions = VGroup(
            MathTex(r"\frac{1}{2}", color=self.WHITE),
            MathTex(r"\frac{3}{4}", color=self.WHITE),
            MathTex(r"\frac{5}{2}", color=self.WHITE),
        ).arrange(
            RIGHT,
            buff=0.8,
        )

        fractions.move_to(
            DOWN * 1.4
        )

        fraction_label = Text(
            "Fractions",
            font_size=30,
            color=self.RED,
        )

        fraction_label.next_to(
            fractions,
            DOWN,
            buff=0.25,
        )

        fraction_cross = VGroup(
            Line(
                fractions.get_corner(UL),
                fractions.get_corner(DR),
                color=self.RED,
                stroke_width=7,
            ),
            Line(
                fractions.get_corner(UR),
                fractions.get_corner(DL),
                color=self.RED,
                stroke_width=7,
            ),
        )

        self.play(
            FadeOut(
                VGroup(
                    negatives,
                    negative_label,
                    cross,
                )
            ),
            run_time=0.3,
        )

        self.play(
            FadeIn(fractions),
            FadeIn(fraction_label),
            run_time=0.5,
        )

        self.play(
            Create(fraction_cross),
            run_time=0.5,
        )

        self.wait(0.4)

        # Return to definition
        definition = Text(
            "0, 1, 2, 3, 4, 5, ...",
            font_size=52,
            color=self.YELLOW,
            weight=BOLD,
        )

        definition.to_edge(DOWN)

        self.play(
            FadeOut(
                VGroup(
                    fractions,
                    fraction_label,
                    fraction_cross,
                )
            ),
            FadeIn(definition, shift=UP * 0.2),
            run_time=0.6,
        )

        self.play(
            Indicate(
                numbers[0],
                color=self.YELLOW,
                scale_factor=1.3,
            ),
            run_time=0.8,
        )

        self.wait(0.4)

        self.play(
            FadeOut(
                VGroup(
                    title,
                    numbers,
                    definition,
                )
            ),
            run_time=0.5,
        )

    # =========================================================
    # 5. WHY
    # =========================================================

    def why(self):

        self.scene_start("why")

        n = self.narrate(
            id="why_01",
            text=(
                "Now, why does this matter? Because zero is often "
                "the small detail students forget to include, and "
                "many exam questions specifically test whether "
                "you remember it belongs here."
            ),
            voice="teacher_a",
            subtitle=True,
        )

        # Exam paper
        paper = RoundedRectangle(
            width=8.5,
            height=5.0,
            corner_radius=0.15,
            color=self.WHITE,
            stroke_width=3,
        )

        paper.set_fill(
            color="#111111",
            opacity=1,
        )

        paper.move_to(
            ORIGIN
        )

        exam_title = Text(
            "EXAM QUESTION",
            font_size=36,
            color=self.YELLOW,
            weight=BOLD,
        )

        exam_title.move_to(
            paper.get_top() + DOWN * 0.55
        )

        question = Text(
            "Which is a Whole Number?",
            font_size=34,
            color=self.WHITE,
        )

        question.next_to(
            exam_title,
            DOWN,
            buff=0.45,
        )

        options = VGroup(
            Text("A)  -2", font_size=30),
            Text("B)  1/2", font_size=30),
            Text("C)  0", font_size=30),
            Text("D)  -1.5", font_size=30),
        ).arrange(
            DOWN,
            aligned_edge=LEFT,
            buff=0.25,
        )

        options.move_to(
            paper.get_center() + DOWN * 0.4
        )

        self.play(
            Create(paper),
            FadeIn(exam_title),
            run_time=0.8,
        )

        self.play(
            FadeIn(question, shift=UP * 0.2),
            run_time=0.5,
        )

        self.play(
            LaggedStart(
                *[
                    FadeIn(option, shift=RIGHT * 0.2)
                    for option in options
                ],
                lag_ratio=0.12,
            ),
            run_time=1.0,
        )

        self.wait_for_narration(n)

        # Highlight zero
        zero_option = options[2]

        box = self.highlight_box(
            zero_option,
            color=self.GREEN,
            buff=0.15,
        )

        correct = Text(
            "✓ WHOLE NUMBER",
            font_size=34,
            color=self.GREEN,
            weight=BOLD,
        )

        correct.next_to(
            paper,
            DOWN,
            buff=0.35,
        )

        self.play(
            Create(box),
            FadeIn(correct, shift=UP * 0.2),
            run_time=0.7,
        )

        self.play(
            Indicate(
                zero_option,
                color=self.GREEN,
                scale_factor=1.1,
            ),
            run_time=0.7,
        )

        self.wait(0.5)

        self.play(
            FadeOut(
                VGroup(
                    paper,
                    exam_title,
                    question,
                    options,
                    box,
                    correct,
                )
            ),
            run_time=0.5,
        )

    # =========================================================
    # 6. REAL WORLD EXAMPLE
    # =========================================================

    def real_world_example(self):

        self.scene_start("real_world")

        # -----------------------------------------------------
        # Narration 1
        # -----------------------------------------------------

        n = self.narrate(
            id="example_01",
            text=(
                "Let me tell you about a girl named Aparna, "
                "asked how many pending messages she had after "
                "clearing her inbox."
            ),
            voice="teacher_a",
            subtitle=True,
        )

        # Person
        head = Circle(
            radius=0.55,
            color=self.YELLOW,
            stroke_width=3,
        )

        body = Line(
            start=DOWN * 0.3,
            end=DOWN * 1.8,
            color=self.BLUE,
            stroke_width=6,
        )

        left_arm = Line(
            start=DOWN * 0.8 + LEFT * 0.05,
            end=DOWN * 1.25 + LEFT * 0.8,
            color=self.BLUE,
            stroke_width=5,
        )

        right_arm = Line(
            start=DOWN * 0.8 + RIGHT * 0.05,
            end=DOWN * 1.25 + RIGHT * 0.8,
            color=self.BLUE,
            stroke_width=5,
        )

        aparna = VGroup(
            head,
            body,
            left_arm,
            right_arm,
        )

        aparna.shift(LEFT * 3)

        name = Text(
            "Aparna",
            font_size=36,
            color=self.YELLOW,
            weight=BOLD,
        )

        name.next_to(
            aparna,
            DOWN,
            buff=0.3,
        )

        # Phone
        phone = RoundedRectangle(
            width=2.0,
            height=3.4,
            corner_radius=0.2,
            color=self.WHITE,
            stroke_width=4,
        )

        phone.shift(
            RIGHT * 2
        )

        notification = Text(
            "Messages",
            font_size=28,
            color=self.BLUE,
        )

        notification.move_to(
            phone.get_center() + UP * 0.7
        )

        count = Text(
            "0",
            font_size=72,
            color=self.GREEN,
            weight=BOLD,
        )

        count.move_to(
            phone.get_center() + DOWN * 0.35
        )

        self.play(
            FadeIn(aparna, shift=UP * 0.3),
            FadeIn(name),
            run_time=0.8,
        )

        self.play(
            Create(phone),
            FadeIn(notification),
            run_time=0.8,
        )

        self.play(
            FadeIn(count, scale=1.4),
            run_time=0.6,
        )

        self.wait_for_narration(n)

        # -----------------------------------------------------
        # Narration 2 — STUDENT VOICE
        # -----------------------------------------------------

        n = self.narrate(
            id="example_02",
            text="Zero.",
            voice="student_a",
            subtitle=True,
        )

        answer = Text(
            '"Zero"',
            font_size=72,
            color=self.YELLOW,
            weight=BOLD,
        )

        answer.to_edge(
            RIGHT,
            buff=0.7,
        )

        self.play(
            FadeIn(answer, scale=1.3),
            run_time=self.duration_of(n),
        )

        self.play(
            Indicate(
                count,
                color=self.YELLOW,
                scale_factor=1.25,
            ),
            run_time=0.7,
        )

        self.wait_for_narration(n)

        # -----------------------------------------------------
        # Narration 3
        # -----------------------------------------------------

        n = self.narrate(
            id="example_03",
            text=(
                "A perfectly valid whole number, describing an "
                "empty, but real, count."
            ),
            voice="teacher_a",
            subtitle=True,
        )

        valid = Text(
            "VALID WHOLE NUMBER",
            font_size=44,
            color=self.GREEN,
            weight=BOLD,
        )

        # Bottom edge, below the "Aparna" label (DOWN * 2.7 overlapped it)
        valid.to_edge(DOWN)

        self.play(
            FadeIn(valid, shift=UP * 0.2),
            run_time=0.5,
        )

        self.play(
            Indicate(
                count,
                color=self.GREEN,
                scale_factor=1.2,
            ),
            run_time=0.8,
        )

        self.wait_for_narration(n)

        self.play(
            FadeOut(
                VGroup(
                    aparna,
                    name,
                    phone,
                    notification,
                    count,
                    answer,
                    valid,
                )
            ),
            run_time=0.5,
        )

    # =========================================================
    # 7. SUMMARY
    # =========================================================

    def summary(self):

        self.scene_start("summary")

        n = self.narrate(
            id="summary_01",
            text="So here's what we take away today.",
            voice="teacher_a",
            subtitle=True,
        )

        summary_title = self.title_text(
            "THE TAKEAWAY",
            color=self.YELLOW,
            size=52,
        )

        summary_title.to_edge(UP)

        self.play(
            FadeIn(summary_title, shift=DOWN * 0.3),
            run_time=0.6,
        )

        self.wait_for_narration(n)

        n = self.narrate(
            id="summary_02",
            text=(
                "Whole numbers are simply natural numbers with zero "
                "added in — 0, 1, 2, 3, and onward."
            ),
            voice="teacher_a",
            subtitle=True,
        )

        # Natural numbers
        natural = Text(
            "1, 2, 3, 4, ...",
            font_size=55,
            color=self.BLUE,
            weight=BOLD,
        )

        natural_label = Text(
            "Natural Numbers",
            font_size=30,
            color=self.BLUE,
        )

        natural_label.next_to(
            natural,
            DOWN,
            buff=0.25,
        )

        # Plus
        plus = Text(
            "+",
            font_size=60,
            color=self.WHITE,
            weight=BOLD,
        )

        # Zero
        zero = Text(
            "0",
            font_size=65,
            color=self.YELLOW,
            weight=BOLD,
        )

        # Whole
        whole = Text(
            "0, 1, 2, 3, 4, ...",
            font_size=55,
            color=self.GREEN,
            weight=BOLD,
        )

        whole_label = Text(
            "Whole Numbers",
            font_size=30,
            color=self.GREEN,
        )

        whole_label.next_to(
            whole,
            DOWN,
            buff=0.25,
        )

        left = VGroup(
            natural,
            natural_label,
        )

        right = VGroup(
            whole,
            whole_label,
        )

        equation = VGroup(
            left,
            plus,
            zero,
            right,
        ).arrange(
            RIGHT,
            buff=0.45,
        )

        equation.scale_to_fit_width(11)

        equation.move_to(
            DOWN * 0.5
        )

        self.play(
            FadeIn(left, shift=RIGHT * 0.3),
            FadeIn(plus),
            FadeIn(zero, scale=1.3),
            run_time=0.8,
        )

        self.play(
            FadeIn(right, shift=RIGHT * 0.3),
            run_time=0.7,
        )

        self.wait_for_narration(n)

        self.play(
            Indicate(
                zero,
                color=self.YELLOW,
                scale_factor=1.25,
            ),
            run_time=0.8,
        )

        self.play(
            Indicate(
                right,
                color=self.GREEN,
                scale_factor=1.05,
            ),
            run_time=0.8,
        )

        self.wait(0.4)

        self.play(
            FadeOut(
                VGroup(
                    summary_title,
                    equation,
                )
            ),
            run_time=0.5,
        )

    # =========================================================
    # 8. DONE / TRANSITION TO INTEGERS
    # =========================================================

    def done(self):

        self.scene_start("done")

        n = self.narrate(
            id="done_01",
            text=(
                "That's Whole Numbers for you — one small addition, "
                "one bigger family."
            ),
            voice="teacher_a",
            subtitle=True,
        )

        whole = Text(
            "WHOLE NUMBERS",
            font_size=60,
            color=self.GREEN,
            weight=BOLD,
        )

        whole.move_to(
            UP * 1.5
        )

        small_addition = Text(
            "+ 0",
            font_size=52,
            color=self.YELLOW,
            weight=BOLD,
        )

        small_addition.next_to(
            whole,
            DOWN,
            buff=0.5,
        )

        family = Text(
            "ONE SMALL ADDITION",
            font_size=34,
            color=self.WHITE,
        )

        family.next_to(
            small_addition,
            DOWN,
            buff=0.35,
        )

        self.play(
            FadeIn(whole, scale=1.1),
            run_time=0.6,
        )

        self.play(
            FadeIn(small_addition, scale=1.3),
            run_time=0.5,
        )

        self.play(
            FadeIn(family),
            run_time=0.5,
        )

        self.wait_for_narration(n)

        # -----------------------------------------------------
        # Next lesson transition
        # -----------------------------------------------------

        n = self.narrate(
            id="done_02",
            text=(
                "In our next video, we open the door to numbers "
                "below zero — Integers."
            ),
            voice="teacher_a",
            subtitle=True,
        )

        self.play(
            FadeOut(
                VGroup(
                    whole,
                    small_addition,
                    family,
                )
            ),
            run_time=0.45,
        )

        # Number line
        number_line = NumberLine(
            x_range=[-5, 5, 1],
            length=10,
            include_numbers=True,
            font_size=28,
            color=self.WHITE,
        )

        number_line.move_to(
            DOWN * 0.3
        )

        self.play(
            Create(number_line),
            run_time=0.9,
        )

        # Highlight positive/whole side
        whole_zone = Line(
            number_line.n2p(0),
            number_line.n2p(5),
            color=self.GREEN,
            stroke_width=10,
        )

        self.play(
            Create(whole_zone),
            run_time=0.6,
        )

        # Open door toward negatives
        # Height 3.0 (was 3.5) so the INTEGERS label above it stays in frame
        door = Rectangle(
            width=2.0,
            height=3.0,
            color=self.YELLOW,
            stroke_width=4,
        )

        door.move_to(
            number_line.n2p(-2)
            + UP * 1.55
        )

        door_label = Text(
            "INTEGERS",
            font_size=42,
            color=self.YELLOW,
            weight=BOLD,
        )

        door_label.next_to(
            door,
            UP,
            buff=0.25,
        )

        self.play(
            Create(door),
            FadeIn(door_label),
            run_time=0.7,
        )

        # Move toward negative numbers
        negative_highlight = Text(
            "-1, -2, -3...",
            font_size=42,
            color=self.RED,
            weight=BOLD,
        )

        negative_highlight.move_to(
            number_line.n2p(-2)
            + DOWN * 1.3
        )

        self.play(
            FadeIn(
                negative_highlight,
                shift=RIGHT * 0.3,
            ),
            run_time=0.6,
        )

        self.wait_for_narration(n)

        # -----------------------------------------------------
        # Final narration
        # -----------------------------------------------------

        n = self.narrate(
            id="done_03",
            text="See you there!",
            voice="teacher_a",
            subtitle=True,
        )

        see_you = Text(
            "SEE YOU THERE!",
            font_size=58,
            color=self.YELLOW,
            weight=BOLD,
        )

        see_you.move_to(
            DOWN * 2.7
        )

        self.play(
            FadeIn(see_you, scale=1.1),
            run_time=self.duration_of(n),
        )

        self.wait_for_narration(n)

        self.play(
            FadeOut(
                VGroup(
                    number_line,
                    whole_zone,
                    door,
                    door_label,
                    negative_highlight,
                    see_you,
                )
            ),
            run_time=0.8,
        )

        self.scene_end("done")

"""
Member Functions — C-CAT | Section A | Module 2: OOP (C++)
Day 23 | Subtopic A: Class Definition

Manim-only lesson animation.

animation.py is the authoring source of truth.
The existing LMS generator handles:
TTS -> voice selection -> audio timing -> WhisperX -> subtitles -> FFmpeg.
"""

from manim import *
from src.animation import LMSScene


BG = "#090D16"
WHITE = "#F5F7FA"
MUTED = "#7E8797"
GRID = "#273244"

BLUE = "#38BDF8"       # class / structure
CYAN = "#67E8F9"       # technical accents
YELLOW = "#FFD166"     # emphasis
GREEN = "#5BE7A9"      # behavior / action
PURPLE = "#A78BFA"     # blueprint
ORANGE = "#FF9F43"     # real-world object
RED = "#FF6B6B"        # inactive / warning


class MemberFunctionsVideo(LMSScene):
    """
    Member Functions lesson.

    Central visual idea:
        CLASS BLUEPRINT
              |
              +---- member functions
                      |
                      +---- object behaviour

    The lesson progressively moves from "a class needs to do something"
    to a concrete Student::displayMarks() example and then to the
    cookie-cutter action metaphor.
    """

    def construct(self):
        self.camera.background_color = BG

        self.hook()
        self.introduction()
        self.how()
        self.what_why()
        self.real_world_example()
        self.summary()
        self.done()

    # ========================================================
    # HELPERS
    # ========================================================

    def title(self, text, color=WHITE, size=52):
        return Text(
            text,
            font_size=size,
            color=color,
            weight=BOLD,
        )

    def mono(self, text, color=WHITE, size=30):
        return Text(
            text,
            font="DejaVu Sans Mono",
            font_size=size,
            color=color,
        )

    def rounded_card(
        self,
        label,
        color=BLUE,
        width=3.3,
        height=1.05,
        size=25,
    ):
        box = RoundedRectangle(
            width=width,
            height=height,
            corner_radius=0.15,
            stroke_color=color,
            stroke_width=2.5,
            fill_color=color,
            fill_opacity=0.08,
        )
        txt = Text(
            label,
            font_size=size,
            color=WHITE,
            weight=BOLD,
        )
        txt.move_to(box)
        return VGroup(box, txt)

    def class_frame(self, width=8.6, height=5.0):
        outer = RoundedRectangle(
            width=width,
            height=height,
            corner_radius=0.18,
            stroke_color=BLUE,
            stroke_width=3,
            fill_color="#0D1524",
            fill_opacity=0.65,
        )
        inner = RoundedRectangle(
            width=width - 0.42,
            height=height - 0.42,
            corner_radius=0.12,
            stroke_color=GRID,
            stroke_width=1.5,
        )
        return VGroup(outer, inner)

    def function_box(self, name, color=GREEN, width=4.1):
        box = RoundedRectangle(
            width=width,
            height=1.05,
            corner_radius=0.15,
            stroke_color=color,
            stroke_width=2.5,
            fill_color=color,
            fill_opacity=0.08,
        )
        label = Text(
            name,
            font="DejaVu Sans Mono",
            font_size=27,
            color=WHITE,
            weight=BOLD,
        )
        label.move_to(box)
        return VGroup(box, label)

    def student_object(self, name, roll_no=101, marks=88):
        card = RoundedRectangle(
            width=3.5,
            height=3.1,
            corner_radius=0.2,
            stroke_color=GREEN,
            stroke_width=2.5,
            fill_color="#0B1A18",
            fill_opacity=0.65,
        )

        label = Text(
            name,
            font_size=30,
            color=GREEN,
            weight=BOLD,
        )
        label.move_to(card.get_top() + DOWN * 0.46)

        divider = Line(
            card.get_left() + RIGHT * 0.3 + DOWN * 0.02,
            card.get_right() + LEFT * 0.3 + DOWN * 0.02,
            color=GRID,
            stroke_width=2,
        )

        rows = VGroup(
            self.mono(f'name = "{name}"', BLUE, 22),
            self.mono(f"rollNo = {roll_no}", BLUE, 22),
            self.mono(f"marks = {marks}", BLUE, 22),
        ).arrange(
            DOWN,
            aligned_edge=LEFT,
            buff=0.17,
        )

        rows.move_to(card.get_center() + DOWN * 0.36)

        return VGroup(
            card,
            label,
            divider,
            rows,
        )

    def play_button(self, color=GREEN, label="CALL"):
        circle = Circle(
            radius=0.35,
            color=color,
            stroke_width=2.5,
            fill_color=color,
            fill_opacity=0.08,
        )

        triangle = Triangle(
            color=color,
            fill_color=color,
            fill_opacity=1,
            stroke_width=0,
        )
        triangle.scale(0.18)
        triangle.rotate(-PI / 2)
        triangle.move_to(circle.get_center())

        txt = Text(
            label,
            font_size=20,
            color=color,
            weight=BOLD,
        )
        txt.next_to(circle, RIGHT, buff=0.18)

        return VGroup(circle, triangle, txt)

    def cookie_cutter(self):
        outer = RoundedRectangle(
            width=3.3,
            height=3.0,
            corner_radius=0.45,
            color=ORANGE,
            stroke_width=4,
        )
        inner = RoundedRectangle(
            width=2.55,
            height=2.25,
            corner_radius=0.35,
            color=YELLOW,
            stroke_width=3,
        )
        handle = Arc(
            radius=1.0,
            start_angle=0,
            angle=PI,
            color=CYAN,
            stroke_width=3,
        )
        handle.move_to(ORIGIN + UP * 1.05)
        return VGroup(outer, inner, handle)

    # ========================================================
    # 1. HOOK
    # ========================================================

    def hook(self):
        self.scene_start("hook")

        n = self.narrate(
            id="hook_01",
            text=(
                "My dear students, a class genuinely needs some true, "
                "honest way to actually do something too."
            ),
            voice="teacher",
            subtitle=True,
        )

        heading = self.title(
            "A CLASS SHOULD DO SOMETHING",
            color=YELLOW,
            size=46,
        )
        heading.to_edge(UP, buff=0.6)

        self.play(
            FadeIn(heading, shift=UP * 0.2),
            run_time=0.65,
        )

        # Empty class on the left.
        class_box = self.class_frame(
            width=4.2,
            height=4.2,
        )
        class_box.move_to(LEFT * 3.2)

        class_name = self.title(
            "Student",
            color=BLUE,
            size=38,
        )
        class_name.move_to(
            class_box.get_top() + DOWN * 0.55
        )

        self.play(
            Create(class_box),
            Write(class_name),
            run_time=0.9,
        )

        self.wait_for_narration(n)

        # Action gap.
        question = Text(
            "BUT HOW?",
            font_size=46,
            color=RED,
            weight=BOLD,
        )
        question.move_to(RIGHT * 1.0 + UP * 0.35)

        self.play(
            FadeIn(question, scale=1.2),
            run_time=0.45,
        )

        arrow = Arrow(
            LEFT * 0.25,
            RIGHT * 1.05,
            color=YELLOW,
            stroke_width=4,
        )
        arrow.move_to(
            RIGHT * 1.55 + DOWN * 0.25
        )

        self.play(
            GrowArrow(arrow),
            run_time=0.45,
        )

        action = self.function_box(
            "displayMarks()",
            color=GREEN,
            width=4.0,
        )
        action.move_to(
            RIGHT * 3.5 + DOWN * 0.55
        )

        self.play(
            FadeIn(action, shift=RIGHT * 0.4),
            run_time=0.65,
        )

        call = self.play_button(
            color=GREEN,
            label="ACTION",
        )
        call.next_to(
            action,
            DOWN,
            buff=0.3,
        )

        self.play(
            FadeIn(call, shift=UP * 0.15),
            run_time=0.45,
        )

        self.wait(0.7)

        self.play(
            FadeOut(
                VGroup(
                    heading,
                    class_box,
                    class_name,
                    question,
                    arrow,
                    action,
                    call,
                )
            ),
            run_time=0.55,
        )

        self.scene_end("hook")

    # ========================================================
    # 2. INTRODUCTION
    # ========================================================

    def introduction(self):
        self.scene_start("introduction")

        n = self.narrate(
            id="intro_01",
            text="Today we meet member functions.",
            voice="teacher",
            subtitle=True,
        )

        title = self.title(
            "MEMBER FUNCTIONS",
            color=YELLOW,
            size=68,
        )

        self.play(
            Write(title),
            run_time=0.8,
        )

        self.wait_for_narration(n)

        self.play(
            title.animate.scale(0.72).to_edge(UP, buff=0.6),
            run_time=0.7,
        )

        # Function as an action.
        func = self.function_box(
            "displayMarks()",
            color=GREEN,
            width=5.0,
        )

        func.move_to(UP * 0.45)

        action_label = Text(
            "A BEHAVIOUR / ACTION",
            font_size=34,
            color=WHITE,
            weight=BOLD,
        )
        action_label.next_to(
            func,
            DOWN,
            buff=0.45,
        )

        self.play(
            FadeIn(func, scale=1.05),
            run_time=0.7,
        )

        self.play(
            FadeIn(action_label, shift=UP * 0.2),
            run_time=0.5,
        )

        # Method call visual.
        arrow = CurvedArrow(
            LEFT * 3.0 + DOWN * 1.65,
            RIGHT * 3.0 + DOWN * 1.65,
            color=GREEN,
            stroke_width=3.5,
        )

        before = Text(
            "OBJECT",
            font_size=30,
            color=BLUE,
            weight=BOLD,
        )
        before.next_to(
            arrow,
            LEFT,
            buff=0.25,
        )

        after = Text(
            "ACTION",
            font_size=30,
            color=GREEN,
            weight=BOLD,
        )
        after.next_to(
            arrow,
            RIGHT,
            buff=0.25,
        )

        self.play(
            Create(arrow),
            FadeIn(before),
            FadeIn(after),
            run_time=0.7,
        )

        self.wait(0.7)

        self.play(
            FadeOut(
                VGroup(
                    title,
                    func,
                    action_label,
                    arrow,
                    before,
                    after,
                )
            ),
            run_time=0.55,
        )

        self.scene_end("introduction")

    # ========================================================
    # 3. HOW
    # ========================================================

    def how(self):
        self.scene_start("how")

        n = self.narrate(
            id="how_01",
            text=(
                "Member functions are honestly the functions declared inside "
                "a class, describing the true behaviour objects of that class "
                "can genuinely perform, such as a Student class honestly having "
                "a displayMarks function as one of its own member functions."
            ),
            voice="teacher",
            subtitle=True,
        )

        heading = self.title(
            "HOW DO MEMBER FUNCTIONS WORK?",
            color=YELLOW,
            size=45,
        )
        heading.to_edge(UP, buff=0.55)

        self.play(
            Write(heading),
            run_time=0.65,
        )

        # Code-style class card.
        frame = self.class_frame(
            width=8.6,
            height=4.9,
        )

        frame.move_to(
            DOWN * 0.1
        )

        class_line = self.mono(
            "class Student",
            color=BLUE,
            size=31,
        )
        class_line.move_to(
            frame.get_top() + DOWN * 0.52
        )

        data_lines = VGroup(
            self.mono("string name;", color=WHITE, size=26),
            self.mono("int marks;", color=WHITE, size=26),
        ).arrange(
            DOWN,
            aligned_edge=LEFT,
            buff=0.14,
        )

        data_lines.move_to(
            frame.get_center() + LEFT * 1.9 + DOWN * 0.4
        )

        data_label = Text(
            "DATA",
            font_size=25,
            color=BLUE,
            weight=BOLD,
        )
        data_label.next_to(
            data_lines,
            UP,
            buff=0.25,
        )

        function = self.function_box(
            "displayMarks()",
            color=GREEN,
            width=3.5,
        )
        function.move_to(
            frame.get_center() + RIGHT * 2.1 + DOWN * 0.2
        )

        function_label = Text(
            "BEHAVIOUR",
            font_size=25,
            color=GREEN,
            weight=BOLD,
        )
        function_label.next_to(
            function,
            UP,
            buff=0.25,
        )

        divider = Line(
            frame.get_center() + UP * 1.35 + RIGHT * 0,
            frame.get_center() + DOWN * 1.55 + RIGHT * 0,
            color=GRID,
            stroke_width=2,
        )

        self.play(
            Create(frame),
            Write(class_line),
            run_time=0.9,
        )

        self.play(
            FadeIn(data_label),
            LaggedStart(
                *[
                    FadeIn(x, shift=RIGHT * 0.2)
                    for x in data_lines
                ],
                lag_ratio=0.15,
            ),
            Create(divider),
            run_time=0.85,
        )

        self.play(
            FadeIn(function_label),
            FadeIn(function, scale=1.06),
            run_time=0.65,
        )

        # Call arrow.
        call_arrow = CurvedArrow(
            function.get_bottom(),
            frame.get_bottom() + DOWN * 0.15 + RIGHT * 2.1,
            angle=-PI / 2,
            color=GREEN,
            stroke_width=3,
        )

        call_label = Text(
            "CAN BE PERFORMED",
            font_size=28,
            color=GREEN,
            weight=BOLD,
        )
        call_label.next_to(
            call_arrow,
            DOWN,
            buff=0.1,
        )

        self.play(
            Create(call_arrow),
            FadeIn(call_label),
            run_time=0.7,
        )

        self.wait_for_narration(n)

        self.play(
            Indicate(
                function,
                color=GREEN,
                scale_factor=1.08,
            ),
            run_time=0.8,
        )

        self.play(
            FadeOut(
                VGroup(
                    heading,
                    frame,
                    class_line,
                    data_lines,
                    data_label,
                    function,
                    function_label,
                    divider,
                    call_arrow,
                    call_label,
                )
            ),
            run_time=0.6,
        )

        self.scene_end("how")

    # ========================================================
    # 4. WHAT / WHY
    # ========================================================

    def what_why(self):
        self.scene_start("what_why")

        n = self.narrate(
            id="what_why_01",
            text=(
                "These are precisely the honest actions every object made from "
                "this blueprint will genuinely be able to actually perform."
            ),
            voice="teacher",
            subtitle=True,
        )

        heading = self.title(
            "ONE BLUEPRINT, MANY OBJECTS, SAME BEHAVIOUR",
            color=YELLOW,
            size=42,
        )
        heading.to_edge(UP, buff=0.55)

        # Blueprint.
        blueprint = self.class_frame(
            width=3.4,
            height=3.8,
        )
        blueprint.move_to(
            LEFT * 3.9 + DOWN * 0.2
        )

        class_name = self.title(
            "Student",
            color=BLUE,
            size=36,
        )
        class_name.move_to(
            blueprint.get_top() + DOWN * 0.52
        )

        function = self.function_box(
            "displayMarks()",
            color=GREEN,
            width=2.8,
        )
        function.scale(0.85)
        function.move_to(
            blueprint.get_center() + DOWN * 0.35
        )

        self.play(
            Write(heading),
            Create(blueprint),
            Write(class_name),
            FadeIn(function, scale=1.05),
            run_time=1.0,
        )

        # Objects.
        aarav = self.student_object(
            "Aarav",
            101,
            88,
        )
        meera = self.student_object(
            "Meera",
            102,
            94,
        )

        aarav.scale(0.55)
        meera.scale(0.55)

        aarav.move_to(
            RIGHT * 1.3 + UP * 0.5
        )
        meera.move_to(
            RIGHT * 4.4 + UP * 0.5
        )

        arr = VGroup(
            aarav,
            meera,
        )

        arrow1 = Arrow(
            blueprint.get_right(),
            aarav.get_left(),
            color=GREEN,
            stroke_width=2.8,
        )

        arrow2 = Arrow(
            blueprint.get_right() + DOWN * 0.2,
            meera.get_left(),
            color=GREEN,
            stroke_width=2.8,
        )

        self.play(
            GrowArrow(arrow1),
            GrowArrow(arrow2),
            run_time=0.7,
        )

        self.play(
            FadeIn(aarav, shift=RIGHT * 0.25),
            FadeIn(meera, shift=RIGHT * 0.25),
            run_time=0.9,
        )

        # Both can call the same function.
        call1 = self.play_button(
            color=GREEN,
            label="displayMarks()",
        )
        call1.scale(0.7)
        call1.next_to(
            aarav,
            DOWN,
            buff=0.18,
        )

        call2 = self.play_button(
            color=GREEN,
            label="displayMarks()",
        )
        call2.scale(0.7)
        call2.next_to(
            meera,
            DOWN,
            buff=0.18,
        )

        self.play(
            FadeIn(call1),
            FadeIn(call2),
            run_time=0.6,
        )

        self.wait_for_narration(n)

        # Action pulse.
        self.play(
            Indicate(
                call1,
                color=GREEN,
                scale_factor=1.1,
            ),
            Indicate(
                call2,
                color=GREEN,
                scale_factor=1.1,
            ),
            run_time=0.9,
        )

        same_action = Text(
            "SAME BEHAVIOUR",
            font_size=30,
            color=GREEN,
            weight=BOLD,
        )
        same_action.to_edge(DOWN, buff=0.5)

        self.play(
            FadeIn(same_action, shift=UP * 0.15),
            run_time=0.5,
        )

        self.wait(0.5)

        self.play(
            FadeOut(
                VGroup(
                    heading,
                    blueprint,
                    class_name,
                    function,
                    aarav,
                    meera,
                    arrow1,
                    arrow2,
                    call1,
                    call2,
                    same_action,
                )
            ),
            run_time=0.6,
        )

        self.scene_end("what_why")

    # ========================================================
    # 5. REAL-WORLD EXAMPLE
    # ========================================================

    def real_world_example(self):
        self.scene_start("real_world_example")

        n = self.narrate(
            id="example_01",
            text=(
                "A cookie cutter's own honest design describing not just "
                "ingredients, but the true actions involved in genuinely baking it."
            ),
            voice="teacher",
            subtitle=True,
        )

        heading = self.title(
            "REAL-WORLD EXAMPLE",
            color=YELLOW,
            size=48,
        )
        heading.to_edge(UP, buff=0.55)

        self.play(
            Write(heading),
            run_time=0.65,
        )

        cutter = self.cookie_cutter()
        cutter.move_to(
            LEFT * 3.5 + DOWN * 0.1
        )

        label = Text(
            "COOKIE CUTTER",
            font_size=29,
            color=ORANGE,
            weight=BOLD,
        )
        label.next_to(
            cutter,
            DOWN,
            buff=0.25,
        )

        self.play(
            Create(cutter),
            FadeIn(label),
            run_time=0.9,
        )

        ingredients = self.rounded_card(
            "INGREDIENTS",
            color=BLUE,
            width=3.0,
            height=0.85,
            size=25,
        )
        ingredients.move_to(
            RIGHT * 2.8 + UP * 1.2
        )

        bake = self.function_box(
            "BAKE()",
            color=GREEN,
            width=3.0,
        )
        bake.move_to(
            RIGHT * 2.8 + DOWN * 0.6
        )

        self.play(
            FadeIn(ingredients, shift=RIGHT * 0.3),
            FadeIn(bake, shift=RIGHT * 0.3),
            run_time=0.8,
        )

        # Action arrow.
        arrow = Arrow(
            ingredients.get_bottom(),
            bake.get_top(),
            color=GREEN,
            stroke_width=4,
        )

        action_text = Text(
            "ACTION",
            font_size=27,
            color=GREEN,
            weight=BOLD,
        )
        action_text.next_to(
            arrow,
            RIGHT,
            buff=0.2,
        )

        self.play(
            GrowArrow(arrow),
            FadeIn(action_text),
            run_time=0.65,
        )

        self.wait_for_narration(n)

        # Execute action.
        self.play(
            Indicate(
                bake,
                color=GREEN,
                scale_factor=1.12,
            ),
            run_time=0.7,
        )

        done = Text(
            "COOKIE BAKED!",
            font_size=44,
            color=YELLOW,
            weight=BOLD,
        )
        done.move_to(
            DOWN * 2.55
        )

        self.play(
            FadeIn(done, scale=1.15),
            run_time=0.6,
        )

        self.wait(0.7)

        self.play(
            FadeOut(
                VGroup(
                    heading,
                    cutter,
                    label,
                    ingredients,
                    bake,
                    arrow,
                    action_text,
                    done,
                )
            ),
            run_time=0.6,
        )

        self.scene_end("real_world_example")

    # ========================================================
    # 6. SUMMARY
    # ========================================================

    def summary(self):
        self.scene_start("summary")

        n = self.narrate(
            id="summary_01",
            text=(
                "Member functions are the functions declared inside a class, "
                "describing the behaviour its objects can perform."
            ),
            voice="teacher",
            subtitle=True,
        )

        heading = self.title(
            "MEMBER FUNCTIONS",
            color=YELLOW,
            size=57,
        )
        heading.to_edge(UP, buff=0.55)

        self.play(
            Write(heading),
            run_time=0.65,
        )

        # Definition equation.
        left = self.rounded_card(
            "FUNCTIONS",
            color=BLUE,
            width=2.8,
            height=0.9,
            size=29,
        )

        inside = self.rounded_card(
            "INSIDE CLASS",
            color=PURPLE,
            width=3.0,
            height=0.9,
            size=28,
        )

        arrow = Text(
            "→",
            font_size=50,
            color=WHITE,
            weight=BOLD,
        )

        result = self.rounded_card(
            "OBJECT BEHAVIOUR",
            color=GREEN,
            width=3.6,
            height=0.95,
            size=28,
        )

        equation = VGroup(
            left,
            arrow,
            inside,
            arrow.copy(),
            result,
        ).arrange(
            RIGHT,
            buff=0.22,
        )

        equation.scale(0.86)
        equation.move_to(
            UP * 0.75
        )

        self.play(
            FadeIn(left, shift=RIGHT * 0.2),
            FadeIn(inside, shift=RIGHT * 0.2),
            FadeIn(result, shift=RIGHT * 0.2),
            Write(equation[1]),
            Write(equation[3]),
            run_time=0.9,
        )

        # Concrete code.
        code_box = RoundedRectangle(
            width=8.4,
            height=2.2,
            corner_radius=0.18,
            stroke_color=GREEN,
            stroke_width=2.5,
            fill_color="#0B1A18",
            fill_opacity=0.7,
        )
        code_box.move_to(
            DOWN * 1.25
        )

        code = VGroup(
            self.mono("class Student", BLUE, 28),
            self.mono("{", WHITE, 28),
            self.mono("    void displayMarks();", GREEN, 27),
            self.mono("}", WHITE, 28),
        ).arrange(
            DOWN,
            aligned_edge=LEFT,
            buff=0.11,
        )

        code.move_to(
            code_box.get_center()
        )

        self.play(
            Create(code_box),
            LaggedStart(
                *[
                    FadeIn(line, shift=RIGHT * 0.15)
                    for line in code
                ],
                lag_ratio=0.08,
            ),
            run_time=1.0,
        )

        self.wait_for_narration(n)

        self.play(
            Indicate(
                code[2],
                color=GREEN,
                scale_factor=1.06,
            ),
            run_time=0.8,
        )

        self.play(
            FadeOut(
                VGroup(
                    heading,
                    equation,
                    code_box,
                    code,
                )
            ),
            run_time=0.6,
        )

        self.scene_end("summary")

    # ========================================================
    # 7. DONE
    # ========================================================

    def done(self):
        self.scene_start("done")

        n = self.narrate(
            id="done_01",
            text=(
                "Wonderful, my dear students. Now let us bring both true ideas "
                "honestly together. I will see you in the next video, for Class "
                "as a Blueprint."
            ),
            voice="teacher",
            subtitle=True,
        )

        title = self.title(
            "MEMBER FUNCTIONS",
            color=YELLOW,
            size=60,
        )
        title.move_to(
            UP * 1.45
        )

        check = MathTex(
            r"\checkmark",
            color=GREEN,
        ).scale(1.25)
        check.next_to(
            title,
            RIGHT,
            buff=0.3,
        )

        message = Text(
            "THE BEHAVIOUR AN OBJECT CAN PERFORM",
            font_size=31,
            color=WHITE,
            weight=BOLD,
        )
        message.next_to(
            title,
            DOWN,
            buff=0.45,
        )

        # Transition: combine data + functions.
        data = self.rounded_card(
            "DATA MEMBERS",
            color=BLUE,
            width=3.1,
            height=0.85,
            size=27,
        )
        functions = self.rounded_card(
            "MEMBER FUNCTIONS",
            color=GREEN,
            width=3.3,
            height=0.85,
            size=27,
        )

        both = VGroup(
            data,
            Text("+", font_size=38, color=WHITE, weight=BOLD),
            functions,
        ).arrange(
            RIGHT,
            buff=0.25,
        )
        both.scale(0.82)
        both.move_to(
            DOWN * 1.35
        )

        next_card = self.rounded_card(
            "NEXT → CLASS AS A BLUEPRINT",
            color=PURPLE,
            width=6.1,
            height=1.0,
            size=29,
        )
        next_card.to_edge(
            DOWN,
            buff=0.55,
        )

        self.play(
            Write(title),
            Write(check),
            run_time=0.75,
        )

        self.play(
            FadeIn(message, shift=UP * 0.15),
            run_time=0.5,
        )

        self.play(
            FadeIn(data, shift=RIGHT * 0.2),
            Write(both[1]),
            FadeIn(functions, shift=LEFT * 0.2),
            run_time=0.8,
        )

        self.play(
            FadeIn(next_card, shift=UP * 0.25),
            run_time=0.7,
        )

        self.wait_for_narration(n)

        self.play(
            Indicate(
                next_card,
                color=PURPLE,
                scale_factor=1.05,
            ),
            run_time=0.8,
        )

        self.play(
            FadeOut(
                VGroup(
                    title,
                    check,
                    message,
                    both,
                    next_card,
                )
            ),
            run_time=0.7,
        )

        self.scene_end("done")

"""
Class Definition — Introduction
C-CAT | Section A | Module 2: OOP (C++) | Day 23
Subtopic A: Class Definition

Manim-only lesson animation.

animation.py is the authoring source of truth.
The existing LMS generator handles TTS, voice selection, timing,
WhisperX alignment, subtitles, caching and final composition.
"""

from manim import *
from src.animation import LMSScene


BG = "#090D16"
WHITE = "#F5F7FA"
MUTED = "#7E8797"
GRID = "#273244"

BLUE = "#38BDF8"
CYAN = "#67E8F9"
YELLOW = "#FFD166"
GREEN = "#5BE7A9"
PURPLE = "#A78BFA"
ORANGE = "#FF9F43"


class ClassDefinitionIntroVideo(LMSScene):

    def construct(self):
        self.camera.background_color = BG
        self.hook()
        self.why_it_matters()
        self.daily_life()
        self.whats_next()

    # --------------------------------------------------------
    # HELPERS
    # --------------------------------------------------------

    def title(self, text, color=WHITE, size=52):
        return Text(text, font_size=size, color=color, weight=BOLD)

    def pill(self, text, color=BLUE, size=28):
        label = Text(text, font_size=size, color=WHITE, weight=BOLD)
        box = RoundedRectangle(
            width=label.width + 0.5,
            height=label.height + 0.28,
            corner_radius=0.14,
            stroke_color=color,
            stroke_width=2.5,
            fill_color=color,
            fill_opacity=0.08,
        )
        return VGroup(box, label)

    def blueprint_frame(self, width=8.4, height=4.6):
        outer = RoundedRectangle(
            width=width,
            height=height,
            corner_radius=0.18,
            color=BLUE,
            stroke_width=3,
            fill_color="#0D1524",
            fill_opacity=0.6,
        )
        inner = RoundedRectangle(
            width=width - 0.42,
            height=height - 0.42,
            corner_radius=0.12,
            color=GRID,
            stroke_width=1.5,
        )
        ticks = VGroup()
        for x in [-width / 2 + 0.35, width / 2 - 0.35]:
            ticks.add(
                Line(
                    [x, -height / 2 + 0.15, 0],
                    [x, -height / 2 + 0.38, 0],
                    color=CYAN,
                    stroke_width=2,
                )
            )
        for y in [-height / 2 + 0.35, height / 2 - 0.35]:
            ticks.add(
                Line(
                    [-width / 2 + 0.15, y, 0],
                    [-width / 2 + 0.38, y, 0],
                    color=CYAN,
                    stroke_width=2,
                )
            )
        return VGroup(outer, inner, ticks)

    def blueprint_component(self, label_text, color, width=3.1):
        box = RoundedRectangle(
            width=width,
            height=1.05,
            corner_radius=0.15,
            color=color,
            stroke_width=2.5,
            fill_color=color,
            fill_opacity=0.07,
        )
        label = Text(
            label_text,
            font_size=25,
            color=WHITE,
            weight=BOLD,
        )
        label.move_to(box)
        return VGroup(box, label)

    def cookie_cutter(self):
        outer = RoundedRectangle(
            width=3.3,
            height=3.0,
            corner_radius=0.45,
            color=YELLOW,
            stroke_width=4,
        )
        inner = RoundedRectangle(
            width=2.55,
            height=2.25,
            corner_radius=0.35,
            color=ORANGE,
            stroke_width=3,
        )
        top = Arc(
            radius=1.35,
            start_angle=0,
            angle=PI,
            color=CYAN,
            stroke_width=3,
        )
        top.move_to(ORIGIN + UP * 1.05)
        return VGroup(outer, inner, top)

    # ========================================================
    # 1. STORY / HOOK & GREETING
    # ========================================================

    def hook(self):
        self.scene_start("hook")

        n = self.narrate(
            id="hook_01",
            text="Hello, my dear students.",
            voice="teacher",
            subtitle=True,
        )

        greeting = self.title(
            "HELLO, MY DEAR STUDENTS",
            color=YELLOW,
            size=52,
        )
        greeting.to_edge(UP, buff=0.65)

        self.play(
            FadeIn(greeting, shift=UP * 0.2),
            run_time=self.duration_of(n),
        )
        self.wait_for_narration(n)

        self.play(FadeOut(greeting), run_time=0.35)

        n = self.narrate(
            id="hook_02",
            text=(
                "A class is genuinely, honestly a blueprint, "
                "and every honest blueprint has its own true parts."
            ),
            voice="teacher",
            subtitle=True,
        )

        frame = self.blueprint_frame()
        frame.move_to(ORIGIN)

        blueprint_title = self.title(
            "CLASS",
            color=BLUE,
            size=54,
        )
        blueprint_title.move_to(frame.get_top() + DOWN * 0.55)

        self.play(Create(frame), run_time=0.9)
        self.play(Write(blueprint_title), run_time=0.55)
        self.wait_for_narration(n)

        parts = VGroup(
            self.blueprint_component("DATA", BLUE),
            self.blueprint_component("BEHAVIOUR", GREEN),
            self.blueprint_component("STRUCTURE", PURPLE),
        )
        parts.arrange(RIGHT, buff=0.35)
        parts.scale(0.83)
        parts.move_to(frame.get_center() + DOWN * 0.35)

        self.play(
            LaggedStart(
                *[FadeIn(part, shift=UP * 0.25) for part in parts],
                lag_ratio=0.18,
            ),
            run_time=1.1,
        )

        bracket = Brace(parts, direction=DOWN, color=YELLOW)
        bracket_label = Text(
            "TRUE PARTS OF THE BLUEPRINT",
            font_size=24,
            color=YELLOW,
            weight=BOLD,
        )
        bracket_label.next_to(bracket, DOWN, buff=0.2)

        self.play(
            GrowFromCenter(bracket),
            FadeIn(bracket_label),
            run_time=0.65,
        )
        self.wait_for_narration(n)

        self.play(
            FadeOut(
                VGroup(
                    frame,
                    blueprint_title,
                    parts,
                    bracket,
                    bracket_label,
                )
            ),
            run_time=0.55,
        )
        self.scene_end("hook")

    # ========================================================
    # 2. WHY THIS MATTERS
    # ========================================================

    def why_it_matters(self):
        self.scene_start("why_it_matters")

        n = self.narrate(
            id="why_01",
            text=(
                "These three true parts genuinely form the complete, "
                "honest anatomy of any class you will ever write."
            ),
            voice="teacher",
            subtitle=True,
        )

        heading = self.title(
            "THE ANATOMY OF A CLASS",
            color=WHITE,
            size=48,
        )
        heading.to_edge(UP, buff=0.6)

        self.play(Write(heading), run_time=0.7)

        class_node = self.pill("CLASS", color=YELLOW, size=32)
        class_node.move_to(ORIGIN + UP * 0.35)

        self.play(FadeIn(class_node, scale=1.25), run_time=0.55)

        data = self.blueprint_component("DATA MEMBERS", BLUE, width=3.0)
        functions = self.blueprint_component(
            "MEMBER FUNCTIONS", GREEN, width=3.0
        )
        blueprint = self.blueprint_component(
            "BLUEPRINT", PURPLE, width=3.0
        )

        data.move_to(LEFT * 4 + DOWN * 1.25)
        functions.move_to(RIGHT * 4 + DOWN * 1.25)
        blueprint.move_to(DOWN * 2.15)

        connectors = VGroup(
            Line(
                class_node.get_left(),
                data.get_right(),
                color=BLUE,
                stroke_width=2.5,
            ),
            Line(
                class_node.get_right(),
                functions.get_left(),
                color=GREEN,
                stroke_width=2.5,
            ),
            Line(
                class_node.get_bottom(),
                blueprint.get_top(),
                color=PURPLE,
                stroke_width=2.5,
            ),
        )

        self.play(
            LaggedStart(
                FadeIn(data, shift=RIGHT * 0.25),
                FadeIn(functions, shift=LEFT * 0.25),
                FadeIn(blueprint, shift=DOWN * 0.25),
                lag_ratio=0.18,
            ),
            run_time=1.2,
        )

        self.play(
            LaggedStart(
                *[Create(line) for line in connectors],
                lag_ratio=0.12,
            ),
            run_time=0.75,
        )

        statement = Text(
            "COMPLETE CLASS ANATOMY",
            font_size=34,
            color=YELLOW,
            weight=BOLD,
        )
        statement.to_edge(DOWN, buff=0.55)

        self.play(FadeIn(statement, shift=UP * 0.15), run_time=0.55)
        self.wait_for_narration(n)

        self.play(
            Indicate(data, color=BLUE, scale_factor=1.04),
            Indicate(functions, color=GREEN, scale_factor=1.04),
            Indicate(blueprint, color=PURPLE, scale_factor=1.04),
            run_time=1.0,
        )

        self.play(
            FadeOut(
                VGroup(
                    heading,
                    class_node,
                    data,
                    functions,
                    blueprint,
                    connectors,
                    statement,
                )
            ),
            run_time=0.55,
        )
        self.scene_end("why_it_matters")

    # ========================================================
    # 3. A MOMENT FROM DAILY LIFE
    # ========================================================

    def daily_life(self):
        self.scene_start("daily_life")

        n = self.narrate(
            id="daily_01",
            text=(
                "Think of a cookie cutter's own honest design, "
                "listing exactly what data it holds, and exactly what it can do."
            ),
            voice="teacher",
            subtitle=True,
        )

        heading = self.title(
            "A MOMENT FROM DAILY LIFE",
            color=YELLOW,
            size=46,
        )
        heading.to_edge(UP, buff=0.65)

        self.play(Write(heading), run_time=0.65)

        cutter = self.cookie_cutter()
        cutter.move_to(LEFT * 3.2 + DOWN * 0.25)

        self.play(Create(cutter), run_time=0.9)

        cutter_label = Text(
            "COOKIE CUTTER",
            font_size=27,
            color=YELLOW,
            weight=BOLD,
        )
        cutter_label.next_to(cutter, DOWN, buff=0.25)

        self.play(FadeIn(cutter_label), run_time=0.4)

        data_panel = self.blueprint_component(
            "WHAT IT HOLDS", BLUE, width=4.0
        )
        behavior_panel = self.blueprint_component(
            "WHAT IT CAN DO", GREEN, width=4.0
        )

        data_panel.move_to(RIGHT * 2.45 + UP * 0.9)
        behavior_panel.move_to(RIGHT * 2.45 + DOWN * 1.0)

        data_items = VGroup(
            Text("shape", font_size=27, color=WHITE),
            Text("size", font_size=27, color=WHITE),
            Text("material", font_size=27, color=WHITE),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.17)
        data_items.next_to(data_panel, DOWN, buff=0.2)

        action_items = VGroup(
            Text("cut", font_size=27, color=WHITE),
            Text("press", font_size=27, color=WHITE),
            Text("form", font_size=27, color=WHITE),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.17)
        action_items.next_to(behavior_panel, DOWN, buff=0.2)

        self.play(
            FadeIn(data_panel, shift=RIGHT * 0.3),
            FadeIn(behavior_panel, shift=RIGHT * 0.3),
            run_time=0.7,
        )

        self.play(
            LaggedStart(
                *[FadeIn(x, shift=UP * 0.15) for x in data_items],
                lag_ratio=0.12,
            ),
            run_time=0.7,
        )

        self.play(
            LaggedStart(
                *[FadeIn(x, shift=UP * 0.15) for x in action_items],
                lag_ratio=0.12,
            ),
            run_time=0.7,
        )

        connector1 = CurvedArrow(
            cutter.get_right(),
            data_panel.get_left(),
            color=BLUE,
            stroke_width=3,
        )
        connector2 = CurvedArrow(
            cutter.get_right() + DOWN * 0.15,
            behavior_panel.get_left(),
            color=GREEN,
            stroke_width=3,
        )

        self.play(
            Create(connector1),
            Create(connector2),
            run_time=0.7,
        )
        self.wait_for_narration(n)

        self.play(
            Indicate(data_panel, color=BLUE, scale_factor=1.04),
            Indicate(behavior_panel, color=GREEN, scale_factor=1.04),
            run_time=0.85,
        )

        self.play(
            FadeOut(
                VGroup(
                    heading,
                    cutter,
                    cutter_label,
                    data_panel,
                    behavior_panel,
                    data_items,
                    action_items,
                    connector1,
                    connector2,
                )
            ),
            run_time=0.55,
        )
        self.scene_end("daily_life")

    # ========================================================
    # 4. WHAT'S COMING NEXT
    # ========================================================

    def whats_next(self):
        self.scene_start("whats_next")

        n = self.narrate(
            id="next_01",
            text=(
                "We will meet data members, member functions, "
                "and the class as a blueprint."
            ),
            voice="teacher",
            subtitle=True,
        )

        heading = self.title(
            "WHAT'S COMING NEXT",
            color=YELLOW,
            size=48,
        )
        heading.to_edge(UP, buff=0.65)

        self.play(Write(heading), run_time=0.65)

        cards = VGroup(
            self.blueprint_component(
                "DATA MEMBERS", BLUE, width=3.25
            ),
            self.blueprint_component(
                "MEMBER FUNCTIONS", GREEN, width=3.25
            ),
            self.blueprint_component(
                "CLASS AS A BLUEPRINT", PURPLE, width=3.25
            ),
        )

        cards.arrange(RIGHT, buff=0.3)
        cards.scale(0.86)
        cards.move_to(DOWN * 0.15)

        self.play(
            LaggedStart(
                *[FadeIn(card, shift=UP * 0.3) for card in cards],
                lag_ratio=0.2,
            ),
            run_time=1.1,
        )

        path = VGroup(
            Dot(color=BLUE),
            Line(LEFT * 0.6, RIGHT * 0.6, color=WHITE, stroke_width=2),
            Dot(color=GREEN),
            Line(LEFT * 0.6, RIGHT * 0.6, color=WHITE, stroke_width=2),
            Dot(color=PURPLE),
        )
        path.arrange(RIGHT, buff=0.0)
        path.move_to(DOWN * 1.35)

        labels = VGroup(
            Text("1", font_size=22, color=BLUE, weight=BOLD),
            Text("2", font_size=22, color=GREEN, weight=BOLD),
            Text("3", font_size=22, color=PURPLE, weight=BOLD),
        )
        labels.arrange(RIGHT, buff=1.65)
        labels.move_to(DOWN * 1.85)

        self.play(Create(path), Write(labels), run_time=0.7)

        next_text = Text(
            "NEXT VIDEO: DATA MEMBERS",
            font_size=34,
            color=WHITE,
            weight=BOLD,
        )
        next_text.to_edge(DOWN, buff=0.55)

        self.play(
            FadeIn(next_text, shift=UP * 0.2),
            run_time=0.6,
        )

        self.wait_for_narration(n)

        self.play(
            Indicate(cards[0], color=BLUE, scale_factor=1.06),
            run_time=0.8,
        )

        self.play(
            FadeOut(
                VGroup(
                    heading,
                    cards,
                    path,
                    labels,
                    next_text,
                )
            ),
            run_time=0.65,
        )
        self.scene_end("whats_next")

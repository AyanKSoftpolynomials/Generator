"""Team test lesson: the smallest complete narrated video (~9 s, two voices).

    .venv/Scripts/python.exe generate.py lessons/team_test

Used to check a fresh installation end to end (TTS -> WhisperX -> Manim ->
subtitles -> FFmpeg). It only uses Text (no LaTeX needed) and the synthetic
test voices teacher_a and student_a that ship with the project.
"""

from manim import *

from src.animation import LMSScene
from src.components import create_body_text, create_title


class TeamTestVideo(LMSScene):

    lesson_title = "Team Test"
    default_voice = "teacher_a"

    def construct(self):
        self.scene_start("hello", title="Hello")
        title = create_title("Setup Check")
        n = self.narrate("hello_01", "Hello team! If you can hear this, the video generator works.")
        self.play_with(n, Write(title))

        self.scene_start("answer", title="Answer", voice="student_a")
        answer = create_body_text("Two plus three is five.").next_to(title, DOWN, buff=1.0)
        n = self.narrate("answer_01", "What is two plus three? It is five.")
        self.at_word(n, "five")
        self.play(FadeIn(answer, shift=UP * 0.3))
        self.wait_for_narration(n)
        self.scene_end()

        self.play(FadeOut(title, answer))

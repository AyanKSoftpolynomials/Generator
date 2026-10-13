"""Voice demo: four voice changes inside ONE scene.

    python scripts/generate_video.py lessons/voice_demo

Teacher A -> Student A -> Teacher B -> Teacher A, all in the "dialogue"
scene, each speaker's name lighting up while they talk.
"""

from manim import *

from src.animation import LMSScene
from src.components import create_body_text, create_label, create_title
from src.themes import default_theme as theme


class VoiceDemo(LMSScene):

    lesson_title = "Voice Demo"
    default_voice = "teacher_a"

    def construct(self):
        self.scene_start("dialogue", title="Dialogue")

        title = create_title("Who is speaking?")
        speakers = {
            "teacher_a": create_label("TEACHER A"),
            "student_a": create_label("STUDENT A"),
            "teacher_b": create_label("TEACHER B"),
        }
        row = VGroup(*speakers.values()).arrange(RIGHT, buff=1.5).shift(UP * 0.8)
        caption = None
        self.play(Write(title), FadeIn(row))

        lines = [
            ("demo_01", "teacher_a", "Here is a quick question. What comes after three?"),
            ("demo_02", "student_a", "Four! And then five."),
            ("demo_03", "teacher_b", "Correct. Counting numbers simply keep going."),
            ("demo_04", "teacher_a", "Thank you both. That is our voice test."),
        ]
        for narration_id, voice, text in lines:
            n = self.narrate(narration_id, text, voice=voice)
            new_caption = create_body_text(text).scale(0.8).to_edge(DOWN, buff=1.2)
            active = speakers[voice]
            self.play(
                *[label.animate.set_color(theme.HIGHLIGHT if label is active else theme.TEXT_MUTED)
                  for label in speakers.values()],
                FadeTransform(caption, new_caption) if caption else FadeIn(new_caption),
                run_time=0.4,
            )
            caption = new_caption
            self.play(Indicate(active, color=theme.HIGHLIGHT), run_time=min(1.0, self.remaining(n)))
            self.wait_for_narration(n)

        self.play(FadeOut(title, row, caption))

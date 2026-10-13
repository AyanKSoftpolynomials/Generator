"""Shortest Distance (Module 3 > Lesson 3 > Topic 3 > Subtopic 4) - narrated animation.

Visuals follow only what "Shortest distance.pdf" specifies (its VISUAL / ANIMATION /
DIAGRAM cues and the VISUAL PLAN table). Sections the plan gives no scene of their own
(Common Mistake, Closing) keep the previous scene on screen under their narration.
"""
from manim import *

from src.animation import LMSScene

FONT = "Arial"
ACCENT = "#4FA3E0"
GOOD = "#5CC77A"
BAD = "#E0605A"
NOTE = "#F2C14E"
MUTED = "#8A99AD"


def txt(s, size=32, color=WHITE, weight=NORMAL):
    return Text(s, font=FONT, font_size=size, color=color, weight=weight)


def leg(a, b, label=None, side=RIGHT, color=ACCENT):
    arrow = Arrow(a, b, buff=0, color=color, stroke_width=6, max_tip_length_to_length_ratio=0.12)
    if label is None:
        return arrow
    return VGroup(arrow, txt(label, 26, color).next_to(arrow, side, buff=0.15))


def point_marker(p, label, side=DOWN):
    dot = Dot(p, color=WHITE, radius=0.09)
    return VGroup(dot, txt(label, 24).next_to(dot, side, buff=0.15))


def compass_rose():
    ring = Circle(radius=0.45, color=MUTED, stroke_width=2)
    north = Arrow(ORIGIN, UP * 0.45, buff=0, color=BAD, stroke_width=5,
                  max_tip_length_to_length_ratio=0.35)
    n_label = txt("N", 26, WHITE, BOLD).next_to(ring, UP, buff=0.08)
    return VGroup(ring, north, n_label).to_corner(UR, buff=0.4)


def bird():
    wing = Arc(radius=0.12, start_angle=0, angle=PI, color=WHITE, stroke_width=3)
    return VGroup(wing, wing.copy().shift(RIGHT * 0.24))


class ShortestDistance(LMSScene):
    def construct(self):
        self.scene0_title_and_setup()
        self.scene1_hook()
        self.scene2_concept()
        self.scene3_explanation()
        self.scene4_example()
        self.scene5_application()
        self.scene6_exam_and_mistake()
        self.scene7_practice_and_answer()
        self.scene8_summary_and_closing()

    def clear_screen(self):
        """Fade out everything except the compass, which stays for the whole video."""
        others = [m for m in self.mobjects if m is not self.compass]
        if others:
            self.play(*[FadeOut(m) for m in others], run_time=0.5)

    # Scene 0 - Title card (about 3 s), then the compass "N" indicator and the Start dot.
    def scene0_title_and_setup(self):
        header = txt("Module 3 — Logical Reasoning", 24, MUTED)
        title = txt("Shortest Distance", 64, ACCENT, BOLD)
        lesson = txt("Lesson 3 — Direction Sense Test", 30)
        topic = txt("Topic: Distance and Position", 28)
        card = VGroup(header, title, lesson, topic).arrange(DOWN, buff=0.3)
        self.play(FadeIn(card), run_time=0.8)
        self.wait(3)
        self.play(FadeOut(card), run_time=0.6)

        self.compass = compass_rose()
        self.hook_start = np.array([-2.5, -2.3, 0])
        self.start_dot = point_marker(self.hook_start, "Start")
        self.play(FadeIn(self.compass), run_time=0.6)
        self.play(FadeIn(self.start_dot), run_time=0.6)

    # Scene 1 - Hook, drawn in the order the script's ANIMATION cue gives.
    def scene1_hook(self):
        s, start = 0.9, self.hook_start
        corner, end = start + UP * 3 * s, start + (UP * 3 + RIGHT * 4) * s
        north = leg(start, corner, "3 km N", LEFT)
        east = leg(corner, end, "4 km E", UP)
        end_dot = point_marker(end, "End", RIGHT)
        walked = txt("Walked: 7 km", 30).to_corner(UL, buff=0.6)
        straight = DashedLine(end, start, color=NOTE, stroke_width=5)
        straight_label = txt("5 km", 30, NOTE).next_to(straight.get_center(), DR, buff=0.2)
        flyer = bird().move_to(end)

        n = self.narrate(
            "shortest_01_hook",
            "Walk 3 kilometres North, then 4 kilometres East. You've walked 7 kilometres, "
            "but a bird flying straight back to your start covers only 5 kilometres. "
            "That number comes from a theorem you already know.")
        self.play_with(n, Succession(
            GrowArrow(north[0]), FadeIn(north[1]),
            GrowArrow(east[0]), FadeIn(east[1]), FadeIn(end_dot),
            FadeIn(walked),
            Create(straight), FadeIn(straight_label),
            FadeIn(flyer), MoveAlongPath(flyer, Line(end, start))))
        self.clear_screen()

    # Scene 2 - Right triangle formed by the components.
    def scene2_concept(self):
        s, o = 0.9, np.array([-1.8, -1.6, 0])
        a, b, c = o, o + RIGHT * 4 * s, o + (RIGHT * 4 + UP * 3) * s
        start_dot = point_marker(a, "Start", LEFT)
        x_leg = leg(a, b)
        y_leg = leg(b, c)
        hyp = DashedLine(a, c, color=NOTE, stroke_width=5)

        n = self.narrate(
            "shortest_02_concept",
            "The shortest distance between the start and the end point is the length of the "
            "straight line joining them. It is also called the displacement. When the movement "
            "is at right angles, North–South and East–West, the net components form the two "
            "shorter sides of a right-angled triangle, and the shortest distance is its hypotenuse.")
        self.play_with(n, Succession(FadeIn(start_dot), GrowArrow(x_leg), GrowArrow(y_leg),
                                     Create(hyp)))
        self.clear_screen()

    # Scene 3 - Formula and a triples list, with the DIAGRAM: legs x (East), y (North),
    # dashed hypotenuse labelled √(x² + y²).
    def scene3_explanation(self):
        s, o = 0.8, np.array([-5.0, -1.6, 0])
        a, b, c = o, o + RIGHT * 4 * s, o + (RIGHT * 4 + UP * 3) * s
        x_leg = leg(a, b, "x (East)", DOWN)
        y_leg = leg(b, c, "y (North)", RIGHT)
        hyp = DashedLine(a, c, color=NOTE, stroke_width=5)
        hyp_label = txt("√(x² + y²)", 30, NOTE).next_to(hyp.get_center(), UL, buff=0.15)

        formula = txt("d = √(x² + y²)", 44, NOTE, BOLD)
        triples = VGroup(*[txt(t, 34, GOOD) for t in ("3-4-5", "6-8-10", "5-12-13", "8-15-17")])
        triples.arrange(DOWN, buff=0.3)
        right_col = VGroup(formula, triples).arrange(DOWN, buff=0.6).move_to(RIGHT * 3.2)

        n = self.narrate(
            "shortest_03_core",
            "First, find the net components: x, East–West, and y, North–South, using running "
            "totals. Then apply Pythagoras' theorem: d equals the square root of x squared plus "
            "y squared. If one component is zero, the distance is just the other component. "
            "And watch for the triples that appear constantly in exams: 3-4-5, 6-8-10, "
            "5-12-13 and 8-15-17, and their multiples.")
        self.play_with(n, Succession(
            GrowArrow(x_leg[0]), FadeIn(x_leg[1]), GrowArrow(y_leg[0]), FadeIn(y_leg[1]),
            Create(hyp), FadeIn(hyp_label), Write(formula),
            LaggedStart(*[FadeIn(t) for t in triples], lag_ratio=0.4)))
        self.clear_screen()

    # Scene 4 - 3-4-5 triangle.
    def scene4_example(self):
        s, o = 0.9, np.array([-1.8, -1.8, 0])
        a, b, c = o, o + UP * 3 * s, o + (UP * 3 + RIGHT * 4) * s
        start_dot = point_marker(a, "Start")
        y_leg = leg(a, b, "3", LEFT)
        x_leg = leg(b, c, "4", UP)
        hyp = DashedLine(c, a, color=NOTE, stroke_width=5)
        hyp_label = txt("5", 30, NOTE).next_to(hyp.get_center(), DR, buff=0.15)

        n = self.narrate(
            "shortest_04_example",
            "3 kilometres North, then 4 kilometres East. x is 4 and y is 3, so d equals the "
            "square root of 16 plus 9, which is the square root of 25: 5 kilometres. "
            "That's the 3-4-5 triple.")
        self.play_with(n, Succession(
            FadeIn(start_dot), GrowArrow(y_leg[0]), FadeIn(y_leg[1]),
            GrowArrow(x_leg[0]), FadeIn(x_leg[1]), Create(hyp), FadeIn(hyp_label)))
        self.clear_screen()

    # Scene 5 - "As the crow flies" map line.
    def scene5_application(self):
        a, b = LEFT * 4.5 + DOWN * 1.2, RIGHT * 4 + UP * 1.2
        ends = VGroup(Dot(a, color=WHITE), Dot(b, color=WHITE))
        line = DashedLine(a, b, color=NOTE, stroke_width=5)
        label = txt("As the crow flies", 30, NOTE).next_to(line.get_center(), UP, buff=0.35)

        n = self.narrate(
            "shortest_05_application",
            "The straight-line distance is used for as-the-crow-flies measurements, radio range, "
            "and the Euclidean distance in data science. It's all the same formula.")
        self.play_with(n, Succession(FadeIn(ends), Create(line), FadeIn(label)))
        self.clear_screen()

    # Scene 6 - Path collapsing into 8 and 6 -> 10; traps crossed out.
    # The Common Mistake narration plays over this same scene.
    def scene6_exam_and_mistake(self):
        opts = VGroup(*[txt(o, 30) for o in ("(a) 10 m", "(b) 18 m", "(c) 14 m", "(d) 12 m")])
        opts.arrange(DOWN, buff=0.35, aligned_edge=LEFT).to_edge(RIGHT, buff=1.0).shift(DOWN * 0.5)

        s, o = 0.3, np.array([-3.0, -2.8, 0])
        p = lambda x, y: o + np.array([x * s, y * s, 0])
        start_dot = point_marker(p(0, 0), "Start", RIGHT)
        path = VGroup(leg(p(0, 0), p(0, 10), color=MUTED), leg(p(0, 10), p(5, 10), color=MUTED),
                      leg(p(5, 10), p(5, 8), color=MUTED), leg(p(5, 8), p(6, 8), color=MUTED))
        net_y = leg(p(0, 0), p(0, 8), "8", LEFT)
        net_x = leg(p(0, 8), p(6, 8), "6", UP)
        hyp = DashedLine(p(6, 8), p(0, 0), color=NOTE, stroke_width=5)
        hyp_label = txt("10", 30, NOTE).next_to(hyp.get_center(), DR, buff=0.15)

        n1 = self.narrate(
            "shortest_06a_exam_question",
            "A man walks 10 metres North, 5 metres East, 2 metres South and 1 metre East. "
            "What is the shortest distance from his starting point? "
            "Options: 10, 18, 14 or 12 metres.")
        self.play_with(n1, Succession(FadeIn(opts), FadeIn(start_dot),
                                      *[GrowArrow(l) for l in path]))

        n2 = self.narrate(
            "shortest_06b_exam_solution",
            "First, the net components. North–South: 10 minus 2 is 8 metres North. "
            "East–West: 5 plus 1 is 6 metres East. Then d equals the square root of 64 plus 36, "
            "which is the square root of 100: 10 metres, option a. That's the 6-8-10 triple.")
        self.play_with(n2, Succession(
            ReplacementTransform(path, VGroup(net_y[0], net_x[0])),
            FadeIn(net_y[1]), FadeIn(net_x[1]), Create(hyp), FadeIn(hyp_label)))

        n3 = self.narrate(
            "shortest_06c_exam_traps",
            "Option b is the total distance travelled. Option c adds the net components, "
            "8 plus 6, instead of using Pythagoras.")
        self.play_with(n3, Succession(Create(Cross(opts[1], stroke_color=BAD)),
                                      Create(Cross(opts[2], stroke_color=BAD))))

        n4 = self.narrate(
            "shortest_07_mistake",
            "Applying Pythagoras to the raw segments, instead of the net components, is the trap. "
            "Always collapse the path first, then use the formula once.")
        self.play_with(n4, Wait())
        self.clear_screen()

    # Scene 7 - 5-12-13 triangle, with a pause timer.
    def scene7_practice_and_answer(self):
        s, o = 0.38, np.array([2.0, 1.2, 0])
        a, b, c = o, o + DOWN * 5 * s, o + (DOWN * 5 + LEFT * 12) * s
        start_dot = point_marker(a, "Start", UP)
        y_leg = leg(a, b, "5", RIGHT)
        x_leg = leg(b, c, "12", DOWN)
        hyp = DashedLine(c, a, color=NOTE, stroke_width=5)
        hyp_label = txt("13", 30, NOTE).next_to(hyp.get_center(), UL, buff=0.15)

        n = self.narrate(
            "shortest_08_practice",
            "A car travels 5 kilometres South and then 12 kilometres West. "
            "How far is it from the start, in a straight line?")
        self.play_with(n, Succession(FadeIn(start_dot), GrowArrow(y_leg[0]), FadeIn(y_leg[1]),
                                     GrowArrow(x_leg[0]), FadeIn(x_leg[1])))

        for i in range(5, 0, -1):
            timer = txt(str(i), 48, MUTED).to_edge(DOWN, buff=0.6)
            self.add(timer)
            self.wait(1)
            self.remove(timer)

        n = self.narrate(
            "shortest_09_answer",
            "x is 12 and y is 5, so d equals the square root of 144 plus 25, which is the "
            "square root of 169: 13 kilometres. That's the 5-12-13 triple.")
        self.play_with(n, Succession(Create(hyp), FadeIn(hyp_label)))
        self.clear_screen()

    # Scene 8 - Summary card. The Closing narration plays over it.
    def scene8_summary_and_closing(self):
        points = VGroup(*[txt(p, 32) for p in (
            "Collapse the path into net x and y",
            "Shortest distance = √(x² + y²)",
            "Triples: 3-4-5, 6-8-10, 5-12-13",
        )]).arrange(DOWN, buff=0.5, aligned_edge=LEFT)

        n = self.narrate(
            "shortest_10_revision",
            "To summarise: collapse the path into net components x and y. The shortest distance "
            "is the square root of x squared plus y squared. Recognise the triples 3-4-5, "
            "6-8-10 and 5-12-13 to save time.")
        self.play_with(n, LaggedStart(*[FadeIn(p) for p in points], lag_ratio=0.8))

        n = self.narrate(
            "shortest_11_closing",
            "Next, in the coordinate-based approach, we'll make this entire process systematic, "
            "including turns.")
        self.play_with(n, Wait())
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.8)

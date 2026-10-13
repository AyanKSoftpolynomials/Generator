from manim import *
from src.animation.lms_scene import LMSScene


class ParentChildRelationshipsVideo(LMSScene):
    """
    Parent-Child Relationships
    Module 3: Reasoning | Day 9 | Blood Relation > Family Relationship Basics

    Scene plan  (scene -> teaching purpose -> visual -> engine)
        HOOK      "my father's son" is a puzzle     -> path ME -> up -> FATHER -> down -> back to ME   -> Manim
        INTRO     the closest bond                  -> one glowing parent-child link               -> Manim
        HOW       two directions + the self-check   -> family tree, DOWN / UP flows, candidates    -> Manim
        WHAT      one-generation link               -> generation rows, then the wider tree        -> Manim
        WHY       longer chains are built from it   -> a 4-link chain assembled piece by piece     -> Manim
        EXAMPLE   "this is my father / mother"      -> you, your parents, a friend, instant arrows -> Manim
        SUMMARY   one step + check the speaker      -> single link + magnified phrase              -> Manim
        DONE      next: brothers and sisters        -> a sibling link appears between the children -> Manim

    Engine choice: every idea here is a relationship DIAGRAM (who links to whom,
    up or down a generation). Flat 2D trees read more clearly than 3D models, so
    all scenes use Manim. No LaTeX is required: all text is Text().

    Visual language (kept constant):
        blue ring  = male        pink ring = female        yellow ring = the speaker (ME)
        green arrow = DOWNWARD (parent -> child)    orange arrow = UPWARD (child -> parent)

    Narration/audio/subtitle metadata is registered through self.narrate().
    The video generator handles TTS, voice selection, audio duration,
    WhisperX alignment, subtitles, timing and final composition.
    Every run_time is a share of self.duration_of(n).
    """

    # ---------------------------------------------------------
    # THEME
    # ---------------------------------------------------------

    BG = "#07090F"
    WHITE = "#FFFFFF"
    YELLOW = "#FFD54A"      # the speaker / answers
    BLUE = "#4FC3F7"        # male
    PINK = "#FF80AB"        # female
    GREEN = "#69F0AE"       # downward: parent -> child
    ORANGE = "#FFB74D"      # upward: child -> parent
    RED = "#FF5252"
    PURPLE = "#B388FF"
    GREY = "#8A93A6"
    GRID = "#141A26"

    VOICE = "teacher_a"

    def construct(self):

        self.camera.background_color = self.BG
        self.bg = self.backdrop()
        self.add(self.bg)

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

    def say(self, id, text, voice=None):
        return self.narrate(id=id, text=text, voice=voice or self.VOICE, subtitle=True)

    def rt(self, n, share):
        """A share of the narration's real duration (never shorter than 0.3 s)."""
        return max(0.3, self.duration_of(n) * share)

    def backdrop(self):
        lines = VGroup()
        for x in np.arange(-8, 8.01, 1.0):
            lines.add(Line([x, -4.5, 0], [x, 4.5, 0], stroke_color=self.GRID, stroke_width=1))
        for y in np.arange(-4, 4.01, 1.0):
            lines.add(Line([-8, y, 0], [8, y, 0], stroke_color=self.GRID, stroke_width=1))
        return lines

    def title_text(self, text, color=None, size=52):
        return Text(text, font_size=size, color=color or self.WHITE, weight=BOLD)

    def label(self, text, color=None, size=30, weight=NORMAL):
        return Text(text, font_size=size, color=color or self.WHITE, weight=weight)

    def glow(self, mob, color, layers=8, width=22, opacity=0.06):
        halo = VGroup()
        for i in range(1, layers + 1):
            halo.add(mob.copy().set_fill(opacity=0).set_stroke(color, width=width * i / layers, opacity=opacity))
        return halo

    def shine(self, mob, color, run_time):
        halo = self.glow(mob, color)
        self.play(FadeIn(halo), run_time=run_time)
        self.add(mob)
        return halo

    def sweep(self, mob, color, run_time, buff=0.15):
        frame = SurroundingRectangle(mob, buff=buff, corner_radius=0.1).set_stroke(color, 5)
        self.play(ShowPassingFlash(frame, time_width=0.6), run_time=run_time)

    def on_screen(self):
        mobs = [m for m in self.mobjects if m is not self.bg]
        children = {id(sm) for m in mobs for sm in m.get_family()[1:]}
        return [m for m in mobs if id(m) not in children]

    def clear(self, run_time, keep=()):
        keep_ids = {id(sm) for k in keep for sm in k.get_family()}
        mobs = [m for m in self.on_screen() if id(m) not in keep_ids]
        if mobs:
            self.play(*[FadeOut(m) for m in mobs], run_time=run_time)

    def slide_board(self, new_group, direction, run_time):
        """Old board slides out, new board slides in: feels like a camera pan."""
        old = self.on_screen()
        new_group.shift(-direction * 16)
        self.add(new_group)
        self.play(*[m.animate.shift(direction * 16) for m in old],
                  new_group.animate.shift(direction * 16), run_time=run_time)
        self.remove(*old)

    def check_mark(self, color=None, scale=1.0):
        return VMobject().set_points_as_corners(
            [[-0.22, 0.02, 0], [-0.06, -0.16, 0], [0.24, 0.2, 0]]
        ).set_stroke(color or self.GREEN, 6).scale(scale)

    def cross(self, mob, color=None):
        c = color or self.RED
        return VGroup(Line(mob.get_corner(UL), mob.get_corner(DR)),
                      Line(mob.get_corner(UR), mob.get_corner(DL))).set_stroke(c, 6)

    # ---------- family-tree visuals ----------

    def member(self, name, color, radius=0.5, dashed=False, name_size=22):
        """A family member: ring avatar (head + shoulders) with a name underneath."""
        ring = Circle(radius=radius, stroke_color=color, stroke_width=4, fill_color=color, fill_opacity=0.12)
        if dashed:
            ring = DashedVMobject(Circle(radius=radius, stroke_color=color, stroke_width=3), num_dashes=24)
        head = Circle(radius=radius * 0.26, stroke_width=0, fill_color=color, fill_opacity=0.9)
        head.move_to(ring.get_center() + UP * radius * 0.2)
        body = RoundedRectangle(corner_radius=radius * 0.2, width=radius * 0.95, height=radius * 0.45,
                                stroke_width=0, fill_color=color, fill_opacity=0.9)
        body.move_to(ring.get_center() + DOWN * radius * 0.42)
        avatar = VGroup(head, body)
        if dashed:
            avatar = Text("?", font_size=int(radius * 70), color=color, weight=BOLD).move_to(ring)
        if name:
            tag = Text(name, font_size=name_size, color=color, weight=BOLD).next_to(ring, DOWN, buff=0.12)
        else:
            # unnamed background relatives: an invisible anchor instead of an empty Text
            tag = Dot(ring.get_bottom(), radius=0.001, fill_opacity=0)
        m = VGroup(ring, avatar, tag)
        m.ring, m.tag = ring, tag
        return m

    def tie(self, a, b, color=None, width=4):
        """Straight tree line between two members' rings."""
        return Line(a.ring.get_center(), b.ring.get_center(), buff=a.ring.width / 2,
                    stroke_color=color or self.GREY, stroke_width=width)

    def route(self, points, color, width=8):
        """A path through the tree, used for glowing 'travel' flashes."""
        return VMobject().set_points_as_corners([np.array(p) for p in points]).set_stroke(color, width)

    def travel(self, path):
        return ShowPassingFlash(path, time_width=0.6)

    def bubble(self, text, size=30, color=None):
        """Speech bubble; the tail points down-left towards the speaker."""
        c = color or self.WHITE
        words = Text(text, font_size=size, color=c, slant=ITALIC)
        box = RoundedRectangle(corner_radius=0.25, width=words.width + 0.6, height=words.height + 0.5,
                               stroke_color=c, stroke_width=2.5, fill_color=self.BG, fill_opacity=1)
        tail = Polygon(box.get_corner(DL) + RIGHT * 0.35, box.get_corner(DL) + RIGHT * 0.8,
                       box.get_corner(DL) + LEFT * 0.15 + DOWN * 0.35,
                       stroke_color=c, stroke_width=2.5, fill_color=self.BG, fill_opacity=1)
        return VGroup(tail, box, words.move_to(box))

    def pause_icon(self, color=None):
        c = color or self.YELLOW
        bars = VGroup(*[RoundedRectangle(corner_radius=0.05, width=0.14, height=0.5, stroke_width=0,
                                         fill_color=c, fill_opacity=1) for _ in range(2)]).arrange(RIGHT, buff=0.14)
        return VGroup(Circle(radius=0.42, stroke_color=c, stroke_width=3), bars)

    def family(self, center=ORIGIN, child_names=(("SON", "BLUE"), ("DAUGHTER", "PINK")), gap=4.0):
        """
        Classic tree: two parents joined by a marriage line, a drop line to a
        sibling bar, and a line down to each child.
        """
        cx, cy = center[0], center[1]
        father = self.member("FATHER", self.BLUE).move_to([cx - 1.6, cy + 1.6, 0])
        mother = self.member("MOTHER", self.PINK).move_to([cx + 1.6, cy + 1.6, 0])
        marriage = Line(father.ring.get_right(), mother.ring.get_left(), stroke_color=self.GREY, stroke_width=4)
        bar_y = cy + 0.2
        kids = VGroup()
        n = len(child_names)
        xs = [cx - gap / 2 + gap * i / max(n - 1, 1) for i in range(n)] if n > 1 else [cx]
        for (name, col), x in zip(child_names, xs):
            kids.add(self.member(name, getattr(self, col)).move_to([x, cy - 1.3, 0]))
        drop = Line([cx, cy + 1.6, 0], [cx, bar_y, 0], stroke_color=self.GREY, stroke_width=4)
        bar = Line([xs[0], bar_y, 0], [xs[-1], bar_y, 0], stroke_color=self.GREY, stroke_width=4)
        legs = VGroup(*[Line([k.get_x(), bar_y, 0], k.ring.get_top(), stroke_color=self.GREY, stroke_width=4)
                        for k in kids])
        f = VGroup(marriage, drop, bar, legs, father, mother, kids)
        f.father, f.mother, f.kids = father, mother, kids
        f.lines = VGroup(marriage, drop, bar, legs)
        f.bar_y, f.mid = bar_y, np.array([cx, cy + 1.6, 0])
        return f

    def down_route(self, fam, parent, child):
        """parent -> marriage midpoint -> sibling bar -> child."""
        side = parent.ring.get_right() if parent is fam.father else parent.ring.get_left()
        return self.route([side, fam.mid, [fam.mid[0], fam.bar_y, 0], [child.get_x(), fam.bar_y, 0],
                           child.ring.get_top()], self.GREEN)

    def up_route(self, fam, child, parent):
        down = self.down_route(fam, parent, child)
        pts = down.get_anchors()[::-1]
        return self.route(pts, self.ORANGE)

    # =========================================================
    # 1. HOOK  (Manim — a path that loops back to the speaker)
    # =========================================================

    def hook(self):

        self.scene_start("hook")

        # -----------------------------------------------------
        # Narration 1 — the puzzle
        # -----------------------------------------------------

        n = self.say(
            "hook_01",
            "If I say \"my father's son,\" and I am an only child, who am I actually talking about?",
        )

        me = self.member("ME", self.YELLOW, radius=0.6, name_size=26).move_to([0, -1.7, 0])
        father = self.member("FATHER", self.BLUE, radius=0.6, name_size=26).move_to([0, 1.9, 0])
        said = self.bubble("my father's son").move_to([3.3, -0.5, 0])

        self.play(FadeIn(me, scale=0.8), run_time=self.rt(n, 0.1))
        self.shine(me.ring, self.YELLOW, self.rt(n, 0.06))
        self.play(FadeIn(said, shift=UP * 0.2), run_time=self.rt(n, 0.1))

        # "my father" — one step UP
        up = Arrow(me.ring.get_top() + LEFT * 0.35, father.ring.get_bottom() + LEFT * 0.35, buff=0.1,
                   color=self.ORANGE, stroke_width=6)
        self.play(GrowArrow(up), FadeIn(father, shift=DOWN * 0.2), run_time=self.rt(n, 0.15))

        # "'s son" — one step DOWN... to which son?
        ghost = self.member("a brother?", self.BLUE, radius=0.6, dashed=True, name_size=22).move_to([-3.6, -1.7, 0])
        to_ghost = Arrow(father.ring.get_bottom() + LEFT * 0.2, ghost.ring.get_top(), buff=0.1,
                         color=self.GREEN, stroke_width=6)
        self.play(FadeIn(ghost), GrowArrow(to_ghost), run_time=self.rt(n, 0.15))
        only = self.label("only child", color=self.RED, size=26, weight=BOLD).next_to(ghost, UP, buff=0.9)
        no_brother = self.cross(ghost.ring)
        self.play(Create(no_brother), FadeIn(only), run_time=self.rt(n, 0.1))

        # with no brother, the only son is the speaker
        down = Arrow(father.ring.get_bottom() + RIGHT * 0.35, me.ring.get_top() + RIGHT * 0.35, buff=0.1,
                     color=self.GREEN, stroke_width=6)
        self.play(ReplacementTransform(to_ghost, down), FadeOut(ghost, only, no_brother), run_time=self.rt(n, 0.12))

        self.wait_for_narration(n)

        # -----------------------------------------------------
        # Narration 2 — it's just you
        # -----------------------------------------------------

        n = self.say(
            "hook_02",
            "If you smiled and thought, \"that's just you,\" you have already grasped today's entire idea.",
        )

        # the round trip lights up: up, then straight back down to ME
        loop = self.route([me.ring.get_top() + LEFT * 0.35, father.ring.get_bottom() + LEFT * 0.35,
                           father.ring.get_bottom() + RIGHT * 0.35, me.ring.get_top() + RIGHT * 0.35], self.YELLOW)
        self.play(self.travel(loop), run_time=self.rt(n, 0.2))
        answer = self.title_text("= ME", color=self.YELLOW, size=56).next_to(me, LEFT, buff=0.8)
        self.play(FadeIn(answer, scale=1.2), Flash(me.ring, color=self.YELLOW, flash_radius=0.9),
                  run_time=self.rt(n, 0.15))
        self.shine(answer, self.YELLOW, self.rt(n, 0.1))
        self.play(self.travel(loop.copy()), run_time=self.rt(n, 0.15))

        self.wait_for_narration(n)

    # =========================================================
    # 2. INTRODUCTION  (Manim — the closest bond)
    # =========================================================

    def introduction(self):

        self.scene_start("introduction")

        # -----------------------------------------------------
        # Narration 1
        # -----------------------------------------------------

        n = self.say("intro_01", "Hello, my dear students.")

        self.clear(self.rt(n, 0.2))
        greeting = self.title_text("Hello, my dear students.", color=self.YELLOW, size=46)
        self.play(FadeIn(greeting, shift=UP * 0.3), run_time=self.rt(n, 0.35))
        halo = self.shine(greeting, self.YELLOW, self.rt(n, 0.2))

        self.wait_for_narration(n)

        # -----------------------------------------------------
        # Narration 2 — one link, glowing
        # -----------------------------------------------------

        n = self.say(
            "intro_02",
            "We begin our journey into family relationships with the closest bond of all, "
            "the one between a parent and their child.",
        )

        self.play(FadeOut(greeting, halo), run_time=self.rt(n, 0.08))
        title = self.title_text("PARENT–CHILD RELATIONSHIPS", color=self.YELLOW, size=52).move_to(UP * 2.9)
        parent = self.member("PARENT", self.PURPLE, radius=0.65, name_size=26).move_to([0, 1.0, 0])
        child = self.member("CHILD", self.YELLOW, radius=0.65, name_size=26).move_to([0, -2.0, 0])
        bond = self.tie(parent, child, color=self.WHITE, width=7)
        bond_lbl = self.label("the closest bond", color=self.GREY, size=26).next_to(bond, RIGHT, buff=0.5)

        self.play(FadeIn(title, shift=DOWN * 0.2), run_time=self.rt(n, 0.12))
        self.shine(title, self.YELLOW, self.rt(n, 0.08))
        self.play(FadeIn(parent, shift=DOWN * 0.2), FadeIn(child, shift=UP * 0.2), run_time=self.rt(n, 0.15))
        self.play(Create(bond), run_time=self.rt(n, 0.12))
        self.play(ShowPassingFlash(bond.copy().set_stroke(self.YELLOW, 12), time_width=0.7), FadeIn(bond_lbl),
                  run_time=self.rt(n, 0.15))
        self.shine(bond, self.YELLOW, self.rt(n, 0.08))

        self.wait_for_narration(n)

    # =========================================================
    # 3. HOW  (Manim — family tree, two directions, the self-check)
    # =========================================================

    def how(self):

        self.scene_start("how")

        # -----------------------------------------------------
        # Narration 1
        # -----------------------------------------------------

        n = self.say("how_01", "Here is how to think about it clearly.")

        self.clear(self.rt(n, 0.2))
        self.fam = self.family(center=[0, 0.1, 0],
                               child_names=(("SON", "BLUE"), ("SON", "BLUE"), ("DAUGHTER", "PINK")), gap=4.4)
        fam = self.fam
        self.play(FadeIn(fam.father, fam.mother, shift=DOWN * 0.2), Create(fam.lines[0]), run_time=self.rt(n, 0.25))
        self.play(Create(fam.lines[1:]), LaggedStart(*[FadeIn(k, shift=UP * 0.2) for k in fam.kids], lag_ratio=0.2),
                  run_time=self.rt(n, 0.3))

        self.wait_for_narration(n)

        # -----------------------------------------------------
        # Narration 2 — only two directions
        # -----------------------------------------------------

        n = self.say("how_02", "A parent-child relationship always moves in one of two directions,")

        down_arrow = Arrow([-5.6, 1.9, 0], [-5.6, -1.4, 0], buff=0, color=self.GREEN, stroke_width=8)
        up_arrow = Arrow([5.6, -1.4, 0], [5.6, 1.9, 0], buff=0, color=self.ORANGE, stroke_width=8)
        down_lbl = self.label("DOWN", color=self.GREEN, size=26, weight=BOLD).next_to(down_arrow, DOWN, buff=0.15)
        up_lbl = self.label("UP", color=self.ORANGE, size=26, weight=BOLD).next_to(up_arrow, UP, buff=0.15)
        self.play(GrowArrow(down_arrow), GrowArrow(up_arrow), run_time=self.rt(n, 0.3))
        self.play(FadeIn(down_lbl, up_lbl), run_time=self.rt(n, 0.15))
        self.dir_arrows = VGroup(down_arrow, up_arrow, down_lbl, up_lbl)

        self.wait_for_narration(n)

        # -----------------------------------------------------
        # Narration 3 — downward: each parent to each child
        # -----------------------------------------------------

        n = self.say(
            "how_03",
            "either downward, from parent to child, such as father to son or daughter, "
            "and mother to son or daughter,",
        )

        son, daughter = fam.kids[0], fam.kids[2]
        down_lbl2 = self.label("parent → child", color=self.GREEN, size=22).next_to(down_arrow, RIGHT, buff=0.2)
        self.play(FadeIn(down_lbl2), Indicate(down_arrow, color=self.GREEN), run_time=self.rt(n, 0.1))
        for parent, kid in [(fam.father, son), (fam.father, daughter), (fam.mother, son), (fam.mother, daughter)]:
            self.play(self.travel(self.down_route(fam, parent, kid)), Indicate(kid.ring, color=self.GREEN),
                      run_time=self.rt(n, 0.17))

        self.wait_for_narration(n)

        # -----------------------------------------------------
        # Narration 4 — upward: child to parent
        # -----------------------------------------------------

        n = self.say("how_04", "or upward, from child to parent.")

        up_lbl2 = self.label("child → parent", color=self.ORANGE, size=22).next_to(up_arrow, LEFT, buff=0.2)
        self.play(FadeIn(up_lbl2), Indicate(up_arrow, color=self.ORANGE), run_time=self.rt(n, 0.15))
        self.play(self.travel(self.up_route(fam, son, fam.father)),
                  self.travel(self.up_route(fam, daughter, fam.mother)), run_time=self.rt(n, 0.35))
        self.dir_arrows.add(down_lbl2, up_lbl2)

        self.wait_for_narration(n)

        # -----------------------------------------------------
        # Narration 5 — the phrases that can point back at the speaker
        # -----------------------------------------------------

        n = self.say(
            "how_05",
            "Whenever a question describes someone as \"my father's son\" or \"my mother's daughter,\" "
            "pause for a moment",
        )

        me, brother = fam.kids[0], fam.kids[1]
        me_tag = Text("ME", font_size=22, color=self.YELLOW, weight=BOLD).move_to(me.tag)
        self.play(FadeOut(self.dir_arrows), Transform(me.tag, me_tag), me.ring.animate.set_stroke(self.YELLOW),
                  run_time=self.rt(n, 0.1))
        said = self.bubble("my father's son", size=26).move_to([-4.6, -0.2, 0])
        self.play(FadeIn(said, shift=UP * 0.2), run_time=self.rt(n, 0.12))

        # up to FATHER, then down to every son of his
        self.play(self.travel(self.up_route(fam, me, fam.father)), run_time=self.rt(n, 0.15))
        self.play(self.travel(self.down_route(fam, fam.father, me)),
                  self.travel(self.down_route(fam, fam.father, brother)), run_time=self.rt(n, 0.15))
        marks = VGroup(*[Text("?", font_size=40, color=self.YELLOW, weight=BOLD).next_to(k.ring, UR, buff=0.02)
                         for k in (me, brother)])
        self.play(FadeIn(marks, scale=1.3), run_time=self.rt(n, 0.08))
        stop = self.pause_icon().move_to([-4.6, 1.2, 0])
        self.play(FadeIn(stop, scale=0.7), run_time=self.rt(n, 0.1))
        self.shine(stop[0], self.YELLOW, self.rt(n, 0.06))
        self.how_extras = VGroup(said, marks, stop)

        self.wait_for_narration(n)

        # -----------------------------------------------------
        # Narration 6 — is it the speaker, or a sibling?
        # -----------------------------------------------------

        n = self.say(
            "how_06",
            "and ask whether the sentence might simply be describing the speaker themselves, or a brother or sister.",
        )

        opt_me = self.label("the speaker?", color=self.YELLOW, size=22, weight=BOLD).next_to(me.tag, DOWN, buff=0.15)
        opt_sib = self.label("a sibling?", color=self.BLUE, size=22, weight=BOLD).next_to(brother.tag, DOWN, buff=0.15)
        self.play(FadeIn(opt_me, shift=UP * 0.1), Indicate(me.ring, color=self.YELLOW), run_time=self.rt(n, 0.2))
        self.play(FadeIn(opt_sib, shift=UP * 0.1), Indicate(brother.ring, color=self.BLUE), run_time=self.rt(n, 0.2))
        # the same check works for "my mother's daughter"
        self.play(self.travel(self.down_route(fam, fam.mother, fam.kids[2]).set_stroke(self.PINK)),
                  Indicate(fam.kids[2].ring, color=self.PINK), run_time=self.rt(n, 0.2))
        self.how_extras.add(opt_me, opt_sib)

        self.wait_for_narration(n)

    # =========================================================
    # 4. WHAT  (Manim — one generation, the first branch)
    # =========================================================

    def what(self):

        self.scene_start("what")

        n = self.say(
            "what_01",
            "Parent-child relationships refer to the direct, one-generation link between a father or mother "
            "and their son or daughter, the very first and closest branch on any family tree.",
        )

        fam = self.fam
        self.play(FadeOut(self.how_extras), run_time=self.rt(n, 0.06))

        # generation rows
        gen1 = self.label("GENERATION 1", color=self.GREY, size=20, weight=BOLD).move_to([-5.6, fam.father.ring.get_y(), 0])
        gen2 = self.label("GENERATION 2", color=self.GREY, size=20, weight=BOLD).move_to([-5.6, fam.kids[0].ring.get_y(), 0])
        span = Line([-5.6, gen1.get_bottom()[1] - 0.15, 0], [-5.6, gen2.get_top()[1] + 0.15, 0])
        brace = Brace(span, RIGHT, buff=0.15, color=self.YELLOW)
        one_gen = self.label("one step", color=self.YELLOW, size=22, weight=BOLD).next_to(brace, RIGHT, buff=0.1)
        self.play(FadeIn(gen1, gen2), run_time=self.rt(n, 0.08))
        self.play(GrowFromCenter(brace), FadeIn(one_gen), run_time=self.rt(n, 0.1))

        # the direct link lights up
        link = self.down_route(fam, fam.father, fam.kids[0]).set_stroke(self.YELLOW, 6)
        self.play(Create(link), run_time=self.rt(n, 0.12))
        self.shine(link, self.YELLOW, self.rt(n, 0.06))

        # zoom out: the same link is the first branch of a much bigger tree
        tree = VGroup(fam, link)
        self.play(FadeOut(gen1, gen2, brace, one_gen), tree.animate.scale(0.55).move_to([0, -0.4, 0]),
                  run_time=self.rt(n, 0.12))
        gp = VGroup(self.member("", self.GREY, radius=0.3).move_to([-0.9, 2.6, 0]),
                    self.member("", self.GREY, radius=0.3).move_to([0.9, 2.6, 0]))
        gp_lines = VGroup(Line(gp[0].ring.get_right(), gp[1].ring.get_left()),
                          Line([0, 2.6, 0], fam.father.ring.get_top())).set_stroke(self.GREY, 3)
        side = VGroup(*[self.member("", self.GREY, radius=0.3).move_to(p) for p in [[3.6, 0.5, 0], [4.8, -1.2, 0],
                                                                                  [-3.6, 0.5, 0], [-4.8, -1.2, 0]]])
        side_lines = VGroup(Line([0, 2.6, 0], side[0].ring.get_top()), Line(side[0].ring.get_bottom(), side[1].ring.get_top()),
                            Line([0, 2.6, 0], side[2].ring.get_top()), Line(side[2].ring.get_bottom(), side[3].ring.get_top()))
        side_lines.set_stroke(self.GREY, 2)
        low = VGroup(*[self.member("", self.GREY, radius=0.3).next_to(k, DOWN, buff=0.45) for k in fam.kids[0:1]])
        low_lines = VGroup(Line(fam.kids[0].tag.get_bottom(), low[0].ring.get_top())).set_stroke(self.GREY, 2)
        wider = VGroup(gp, gp_lines, side, side_lines, low, low_lines).set_opacity(0.45)
        self.play(FadeIn(wider, lag_ratio=0.1), run_time=self.rt(n, 0.15))
        first = self.label("first & closest branch", color=self.YELLOW, size=24, weight=BOLD)
        first.next_to(link, LEFT, buff=0.6).shift(UP * 0.3)
        self.play(FadeIn(first, shift=RIGHT * 0.2), self.travel(link.copy().set_stroke(self.YELLOW, 10)),
                  run_time=self.rt(n, 0.1))

        self.wait_for_narration(n)

    # =========================================================
    # 5. WHY  (Manim — longer chains are built from the same link)
    # =========================================================

    def why(self):

        self.scene_start("why")

        # -----------------------------------------------------
        # Narration 1 — a longer chain, link by link
        # -----------------------------------------------------

        n = self.say(
            "why_01",
            "This matters because parent-child links are the basic thread that every longer, "
            "more complicated relationship chain is eventually built from.",
        )

        self.clear(self.rt(n, 0.1))
        grand = self.member("GRANDFATHER", self.BLUE).move_to([0, 2.4, 0])
        father = self.member("FATHER", self.BLUE).move_to([-2.6, 0.5, 0])
        uncle = self.member("UNCLE", self.BLUE).move_to([2.6, 0.5, 0])
        me = self.member("ME", self.YELLOW).move_to([-2.6, -1.6, 0])
        cousin = self.member("COUSIN", self.PINK).move_to([2.6, -1.6, 0])
        people = VGroup(grand, father, uncle, me, cousin)
        self.play(LaggedStart(*[FadeIn(p, scale=0.8) for p in people], lag_ratio=0.15), run_time=self.rt(n, 0.2))

        # four identical threads: up, up, down, down
        steps = [(me, father, self.ORANGE), (father, grand, self.ORANGE),
                 (grand, uncle, self.GREEN), (uncle, cousin, self.GREEN)]
        self.links = VGroup()
        for a, b, c in steps:
            arr = Arrow(a.ring.get_center(), b.ring.get_center(), buff=0.55, color=c, stroke_width=7)
            self.play(GrowArrow(arr), run_time=self.rt(n, 0.1))
            self.links.add(arr)
        count = self.label("4 parent–child links", color=self.YELLOW, size=28, weight=BOLD).move_to([0, -3.1, 0])
        self.play(FadeIn(count, shift=UP * 0.2), run_time=self.rt(n, 0.1))

        self.wait_for_narration(n)

        # -----------------------------------------------------
        # Narration 2 — recognise each link instantly, travel smoothly
        # -----------------------------------------------------

        n = self.say(
            "why_02",
            "If you can instantly recognise this simplest link without hesitation, "
            "you will move through longer chains far more smoothly later on.",
        )

        path = self.route([me.ring.get_center(), father.ring.get_center(), grand.ring.get_center(),
                           uncle.ring.get_center(), cousin.ring.get_center()], self.YELLOW)
        traveller = Dot(me.ring.get_center(), radius=0.14, color=self.YELLOW)
        self.add(traveller)
        self.play(MoveAlongPath(traveller, path), LaggedStart(*[Indicate(l, scale_factor=1.15) for l in self.links],
                                                              lag_ratio=0.25),
                  run_time=self.rt(n, 0.35), rate_func=smooth)
        self.play(Flash(cousin.ring, color=self.YELLOW, flash_radius=0.8), run_time=self.rt(n, 0.1))
        smooth_lbl = self.label("smooth", color=self.GREEN, size=30, weight=BOLD).move_to([4.9, -1.6, 0])
        self.play(FadeIn(smooth_lbl, shift=LEFT * 0.2), self.travel(path.copy()), run_time=self.rt(n, 0.15))
        self.shine(smooth_lbl, self.GREEN, self.rt(n, 0.06))

        self.wait_for_narration(n)

    # =========================================================
    # 6. REAL WORLD EXAMPLE  (Manim — introducing your parents)
    # =========================================================

    def real_world_example(self):

        self.scene_start("real_world")

        # -----------------------------------------------------
        # Narration 1 — "this is my father", "this is my mother"
        # -----------------------------------------------------

        n = self.say(
            "example_01",
            "Think of how naturally you introduce your own parents to a new friend, "
            "\"this is my father,\" \"this is my mother,\" without a flicker of doubt.",
        )

        father = self.member("FATHER", self.BLUE, radius=0.6).move_to([-5.0, 1.4, 0])
        mother = self.member("MOTHER", self.PINK, radius=0.6).move_to([-2.8, 1.4, 0])
        you = self.member("YOU", self.YELLOW, radius=0.6).move_to([-1.0, -1.6, 0])
        friend = self.member("NEW FRIEND", self.PURPLE, radius=0.6).move_to([4.2, -1.6, 0])
        self.slide_board(VGroup(father, mother, you, friend), LEFT, self.rt(n, 0.18))

        b1 = self.bubble("this is my father", size=26).move_to([1.8, 1.9, 0])
        b2 = self.bubble("this is my mother", size=26).move_to([1.8, 0.4, 0])
        a1 = Arrow(you.ring.get_center(), father.ring.get_center(), buff=0.65, color=self.ORANGE, stroke_width=6)
        a2 = Arrow(you.ring.get_center(), mother.ring.get_center(), buff=0.65, color=self.ORANGE, stroke_width=6)
        # each introduction is instant: bubble and link appear together, fast
        self.play(FadeIn(b1, scale=0.9), GrowArrow(a1), run_time=self.rt(n, 0.1))
        self.play(Indicate(father.ring, color=self.BLUE), run_time=self.rt(n, 0.08))
        self.play(FadeIn(b2, scale=0.9), GrowArrow(a2), run_time=self.rt(n, 0.1))
        self.play(Indicate(mother.ring, color=self.PINK), run_time=self.rt(n, 0.08))
        ticks = VGroup(self.check_mark(self.GREEN).next_to(b1, RIGHT, buff=0.2),
                       self.check_mark(self.GREEN).next_to(b2, RIGHT, buff=0.2))
        self.play(Create(ticks), Indicate(friend.ring, color=self.PURPLE), run_time=self.rt(n, 0.12))

        self.wait_for_narration(n)

        # -----------------------------------------------------
        # Narration 2 — that certainty, for every question
        # -----------------------------------------------------

        n = self.say(
            "example_02",
            "That instant, comfortable certainty is exactly the feeling we want for every parent-child question you face.",
        )

        halo = self.glow(you.ring, self.YELLOW, layers=10, width=40, opacity=0.08)
        self.play(FadeIn(halo), run_time=self.rt(n, 0.12))
        self.add(you)
        card = self.bubble("my mother's daughter?", size=26, color=self.GREY).move_to([3.4, -3.0, 0])
        card.remove(card[0])
        self.play(FadeIn(card, shift=UP * 0.2), run_time=self.rt(n, 0.12))
        instant = VGroup(self.check_mark(self.YELLOW, 1.3),
                         self.label("instant", color=self.YELLOW, size=26, weight=BOLD)).arrange(RIGHT, buff=0.2)
        instant.next_to(card, LEFT, buff=0.4)
        self.play(FadeIn(instant, scale=1.2), Flash(instant, color=self.YELLOW, flash_radius=0.8),
                  run_time=self.rt(n, 0.12))
        self.shine(instant, self.YELLOW, self.rt(n, 0.08))

        self.wait_for_narration(n)

    # =========================================================
    # 7. SUMMARY  (Manim — one step, and check the speaker)
    # =========================================================

    def summary(self):

        self.scene_start("summary")

        n = self.say(
            "summary_01",
            "In short, a parent-child relationship is the direct, one-step link between a father or mother "
            "and their son or daughter,",
        )

        summary_title = self.title_text("THE TAKEAWAY", color=self.YELLOW, size=50).to_edge(UP, buff=0.5)
        self.slide_board(VGroup(summary_title), UP, self.rt(n, 0.15))
        self.shine(summary_title, self.YELLOW, self.rt(n, 0.06))

        parents = VGroup(self.member("FATHER", self.BLUE).move_to([-4.6, 1.2, 0]),
                         self.member("MOTHER", self.PINK).move_to([-2.4, 1.2, 0]))
        kids = VGroup(self.member("SON", self.BLUE).move_to([-4.6, -1.6, 0]),
                      self.member("DAUGHTER", self.PINK).move_to([-2.4, -1.6, 0]))
        links = VGroup(*[Line(p.ring.get_bottom(), k.ring.get_top(), stroke_color=self.WHITE, stroke_width=4)
                         for p in parents for k in kids])
        span = Line([-1.1, parents[0].ring.get_y(), 0], [-1.1, kids[0].ring.get_y(), 0])
        brace = Brace(span, RIGHT, buff=0.05, color=self.YELLOW)
        step = self.label("one step", color=self.YELLOW, size=26, weight=BOLD).next_to(brace, RIGHT, buff=0.12)

        self.play(FadeIn(parents, shift=DOWN * 0.2), FadeIn(kids, shift=UP * 0.2), run_time=self.rt(n, 0.18))
        self.play(LaggedStart(*[Create(l) for l in links], lag_ratio=0.15), run_time=self.rt(n, 0.2))
        self.play(GrowFromCenter(brace), FadeIn(step), run_time=self.rt(n, 0.12))
        self.shine(step, self.YELLOW, self.rt(n, 0.06))

        self.wait_for_narration(n)

        n = self.say(
            "summary_02",
            "and it is always worth checking carefully whether the sentence is quietly describing the speaker themselves.",
        )

        said = self.bubble("my father's son", size=30).move_to([3.4, 1.2, 0])
        lens = Circle(radius=0.65, stroke_color=self.YELLOW, stroke_width=5)
        handle = Line(lens.point_at_angle(-PI / 4), lens.point_at_angle(-PI / 4) + np.array([0.5, -0.5, 0]),
                      stroke_color=self.YELLOW, stroke_width=8)
        magnifier = VGroup(lens, handle).move_to(said.get_left() + LEFT * 0.2)
        check = VGroup(self.label("the speaker?", color=self.YELLOW, size=30, weight=BOLD),
                       self.check_mark(self.YELLOW, 1.3)).arrange(RIGHT, buff=0.25).move_to([3.4, -0.9, 0])

        self.play(FadeIn(said, shift=UP * 0.2), run_time=self.rt(n, 0.15))
        self.play(FadeIn(magnifier), run_time=self.rt(n, 0.08))
        self.play(magnifier.animate.move_to(said.get_right() + RIGHT * 0.2), run_time=self.rt(n, 0.25))
        self.play(FadeIn(check, shift=UP * 0.2), run_time=self.rt(n, 0.12))
        self.shine(check, self.YELLOW, self.rt(n, 0.08))

        self.wait_for_narration(n)

    # =========================================================
    # 8. DONE  (Manim — the next link: brothers and sisters)
    # =========================================================

    def done(self):

        self.scene_start("done")

        n = self.say(
            "done_01",
            "With this closest bond firmly in place, let's move outward just slightly, "
            "to the relationship between brothers and sisters.",
        )

        self.clear(self.rt(n, 0.1))
        fam = self.family(center=[0, 0.2, 0])
        self.play(FadeIn(fam), run_time=self.rt(n, 0.2))
        self.play(self.travel(self.down_route(fam, fam.father, fam.kids[0])),
                  self.travel(self.down_route(fam, fam.mother, fam.kids[1])), run_time=self.rt(n, 0.15))

        # the new relationship runs sideways, between the children
        a, b = fam.kids
        sibling = DashedLine(a.ring.get_right(), b.ring.get_left(), dash_length=0.15, stroke_color=self.YELLOW,
                             stroke_width=5).shift(DOWN * 0.05)
        next_lbl = self.label("BROTHERS & SISTERS", color=self.YELLOW, size=30, weight=BOLD).move_to([0, -3.0, 0])
        self.play(Create(sibling), run_time=self.rt(n, 0.15))
        self.play(FadeIn(next_lbl, shift=UP * 0.2), run_time=self.rt(n, 0.12))
        self.shine(sibling, self.YELLOW, self.rt(n, 0.08))

        self.wait_for_narration(n)

        n = self.say("done_02", "I will see you in the next video.")

        see_you = self.title_text("SEE YOU IN THE NEXT VIDEO!", color=self.YELLOW, size=48).move_to(UP * 3.2)
        self.play(FadeIn(see_you, scale=1.1), run_time=self.rt(n, 0.4))
        self.shine(see_you, self.YELLOW, self.rt(n, 0.25))

        self.wait_for_narration(n)

        self.clear(0.8)

        self.scene_end("done")
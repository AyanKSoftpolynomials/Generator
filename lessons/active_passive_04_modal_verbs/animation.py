"""
animation.py for the LMS video generator.

Course : C-CAT Preparation - Section A: English Language and Verbal Ability
Module : 2 Grammar   Lesson : 6 Active and Passive Voice (Session 12)
Video  : 04 - Modal Verbs in the Passive Voice   (previous: Tense-based conversion;  next: Interrogative sentences)
Source : C:/Final scripts/Scipts/Second/04 - Modal verbs.pdf

Note: the two questions are practice questions written for the class, not past-paper questions.

Look (3Blue1Brown style): near-black background, white text, ONE blue and ONE brown accent; yellow only for a
  passing highlight, green / red only for right / wrong. Latin Modern Roman (Cambria if it is missing).
  Sizes: title 54, heading 38, body 32, label 28, small 24.

Roles (the script has no speaker labels; every line was assigned by meaning, and no label is spoken):
  NARRATOR   voice-over, connects the scenes          self.N              voice "vijay"
  TEACHER    teaches, asks, guides                    self.T / self.Q     voice "aditya"
  STUDENT A  the confident one, near the window       self.S("A", ...)    voice "prasad"
  STUDENT B  the cautious one, front row              self.S("B", ...)    voice "kavya"
  STUDENT C  the second student                       self.S("C", ...)    voice "ritu"
  STUDENT D  at the back, arms folded                 self.S("D", ...)    voice "student_a"
  Stage directions are not spoken: they are the visuals. Board text that the script does not speak
  (the pattern card) is shown with a thinking bar that gives time to read it.

Sarvam AI voices (settings.json > audio.sarvam.voices, or --speaker VOICE=SPEAKER):
    "vijay": "vijay", "aditya": "aditya", "prasad": "kabir", "kavya": "kavya", "ritu": "ritu", "student_a": "rahul"

The two questions have whole sentences as options, so they are shown one at a time; the thinking time
is split between them.

Section map:
  S01 Where does "be" go after "must"?   S02 The topic   S03 How C-CAT tests it   S04 Attempts
  S05 WHAT: the modal patterns   S06 HOW: semi-modals   S07 HOW: modals keep their meaning
  S08 WHY: the language of policy   S09 Payoff   S10 Summary   S11 What comes next
"""

import math
import os
import types

import numpy as np
from manim import *

from src.animation import LMSScene

# ============================================================== style ====

BG = "#101010"
FILL = "#1B1B1B"           # inside of boxes
INK = "#F5F5F5"            # main text
MUTED = "#9A9A9A"          # supporting text
BLUE = "#58C4DD"           # accent 1: key terms, the word in question
BROWN = "#CD853F"          # accent 2: clues, things to remember
FLASH = "#FFFF00"          # a passing highlight only
GOOD = "#83C167"           # the right answer
BAD = "#FC6255"            # wrong / dangerous

LM_DIR = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "MiKTeX", "fonts", "opentype", "public", "lm")


def serif_font():
    """Latin Modern Roman when MiKTeX has it (registered for this run only), else Cambria."""
    try:
        import manimpango

        files = [os.path.join(LM_DIR, f"lmroman10-{style}.otf") for style in ("regular", "bold", "italic")]
        if all(os.path.exists(f) for f in files) and all(manimpango.register_font(f) for f in files):
            if "Latin Modern Roman 10" in manimpango.list_fonts():
                return "Latin Modern Roman 10"
    except Exception:
        pass
    return "Cambria"


FONT = serif_font()
MONO = "Consolas"
MIN_FONT = 22              # readable floor
TITLE = 54
HEAD = 38
BODY = 32
LABEL = 28
SMALL = 24
CODE = 24

# ============================================================= layout ====

FRAME_W = config.frame_width
FRAME_H = config.frame_height
SAFE = 0.45                                   # margin kept clear on every side
EDGE_X = FRAME_W / 2 - SAFE                   # furthest x any content may reach
TOP = FRAME_H / 2 - SAFE
FLOOR = -FRAME_H / 2 + SAFE + 0.1             # lowest y any content may reach

FACE_R = 0.36
STUDENT_R = 0.28                              # the four students are drawn a little smaller
STUDENT_GAP = 0.1
STUDENTS_W = 4 * 2.6 * STUDENT_R + 3 * STUDENT_GAP
HEAD_Y = 3.02                                 # centre of the scene heading
HEAD_W = FRAME_W - 2 * (SAFE + STUDENTS_W + 0.35)     # the heading stays centred between the cast
TIMER_Y = 2.58                                # the thinking-time bar
STRIP_TOP, STRIP_BOTTOM = 2.42, 1.48          # the spoken-line strip
STRIP_Y = (STRIP_TOP + STRIP_BOTTOM) / 2
STRIP_W = 11.0
BOARD_TOP = 1.32                              # top of the board (the strip sits above it)

NARRATOR_VOICE = "vijay"
TEACHER_VOICE = "aditya"
VOICES = {"N": NARRATOR_VOICE, "T": TEACHER_VOICE, "A": "prasad", "B": "kavya", "C": "ritu", "D": "student_a"}
TURN_PAUSE = 0.6               # silence after each block, so the voices never run together
CRUMB = "C-CAT Preparation  ›  English  ›  Vocabulary  ›  Synonyms"


# ======================================================= text helpers ====

def text(s, size=BODY, color=INK, weight=NORMAL, slant=NORMAL, font=FONT):
    return Text(s, font=font, font_size=size, color=color, weight=weight, slant=slant, disable_ligatures=True)


def code(s, size=CODE, color=INK, weight=NORMAL):
    """Program text."""
    return text(s, size, color, weight, NORMAL, MONO)


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


def fit_w(mob, max_width):
    """Layout guard: ``mob`` is never wider than ``max_width`` (its left edge stays where it is)."""
    if mob.width > max_width:
        mob.scale(max_width / mob.width, about_edge=LEFT)
    return mob


def fitted_text(s, max_width, size=BODY, color=INK, weight=NORMAL, max_lines=3, slant=NORMAL):
    """Readable text no wider than ``max_width``: as written, else wrapped, else a little smaller."""
    for lines in range(1, max_lines + 1):
        mob = text(s if lines == 1 else wrap_lines(s, lines), size, color, weight, slant)
        if mob.width <= max_width:
            return mob
    return mob.scale(max_width / mob.width)


def phrase(*parts, buff=0.22):
    """Pieces on one line."""
    return VGroup(*parts).arrange(RIGHT, buff=buff)


def column(*mobs, buff=0.25):
    """Mobjects under one another, left edges aligned."""
    return VGroup(*mobs).arrange(DOWN, buff=buff, aligned_edge=LEFT)


def place(mob, left=None, top=None, x=None, y=None):
    """Put ``mob`` by its left edge / top edge, or by its centre."""
    if x is not None:
        mob.set_x(x)
    if y is not None:
        mob.set_y(y)
    if left is not None:
        mob.shift(RIGHT * (left - mob.get_left()[0]))
    if top is not None:
        mob.shift(UP * (top - mob.get_top()[1]))
    return mob


def line_at(s, left=0.0, y=0.0, size=LABEL, color=INK, weight=NORMAL, slant=NORMAL, font=FONT):
    """A piece of text whose LINE (not its ink) is centred on ``y``, so pieces set this way share a baseline.

    ``line_end`` is where the next piece of the same line starts."""
    mob = text(s + "|", size, color, weight, slant, font)        # the bar gives every piece the same height
    mob.shift(RIGHT * (left - mob.get_left()[0]) + UP * (y - mob.get_y()))
    bar = mob[-1]
    mob.line_end = bar.get_left()[0]
    mob.remove(bar)
    return mob


def para(*lines, size=LABEL, step=None, color=INK):
    """Lines of text made of pieces, so single words can be coloured or pointed at later.

    A line is a list of pieces; a piece is a string, (string, colour) or (string, colour, weight).
    Returns VGroup(lines); every line is a VGroup of its pieces."""
    step = step or size * 0.0185
    gap = size * 0.0033
    out = VGroup()
    for k, parts in enumerate(lines):
        row, x = VGroup(), 0.0
        for part in ([parts] if isinstance(parts, (str, tuple)) else parts):
            s, c, w = (part, color, NORMAL) if isinstance(part, str) else (tuple(part) + (NORMAL,))[:3]
            piece = line_at(s, x, -k * step, size, c, w)
            x = piece.line_end + gap
            row.add(piece)
        out.add(row)
    return out


def hl(mob, scale=1.12, color=FLASH):
    """Highlight a text or an arrow for a moment."""
    return Indicate(mob, color=color, scale_factor=scale)


def ring(mob):
    """Highlight a block for a moment (a frame that draws itself and fades)."""
    return Circumscribe(mob, color=FLASH, buff=0.1, fade_out=True, stroke_width=5)


def up(mob):
    """Fade in, rising a little."""
    return FadeIn(mob, shift=UP * 0.15)


def side(mob):
    """Fade in, sliding in from the left."""
    return FadeIn(mob, shift=RIGHT * 0.2)


def under(mob, color=BLUE, gap=0.07):
    """A line under ``mob`` (a student's pick, a key word)."""
    return Line(mob.get_corner(DL) + DOWN * gap, mob.get_corner(DR) + DOWN * gap, color=color, stroke_width=4)


def tick(size=0.3, color=GOOD):
    t = VMobject(stroke_color=color, stroke_width=6)
    t.set_points_as_corners([np.array([-0.5, 0.0, 0.0]), np.array([-0.12, -0.4, 0.0]), np.array([0.5, 0.45, 0.0])])
    return t.scale(size)


def cross(size=0.26, color=BAD):
    return VGroup(Line(UL, DR, color=color, stroke_width=6), Line(UR, DL, color=color, stroke_width=6)).scale(size / 2)


def small_arrow(color=BROWN, length=0.8):
    return Arrow(LEFT * length / 2, RIGHT * length / 2, buff=0, color=color, stroke_width=4, tip_length=0.18)


def bullets(items, size=LABEL, buff=0.3, color=INK):
    """Rows of a blue dot and one line each."""
    rows = VGroup()
    for item in items:
        body = text(item, size, color) if isinstance(item, str) else item
        rows.add(VGroup(Dot(radius=0.07, color=BLUE), body).arrange(RIGHT, buff=0.3))
    return rows.arrange(DOWN, buff=buff, aligned_edge=LEFT)


# ==================================================== diagram pieces ====

class Grid(VGroup):
    """A plain table: left-aligned columns of the given widths, an optional header row with a rule.

    ``rows`` are lists of strings ("" leaves a cell empty). ``styles`` gives (colour, weight) per
    column for the body rows. ``cell(r, c)``, ``col(c)`` and ``row(r)`` return the parts."""

    def __init__(self, rows, widths, size=LABEL, row_h=0.6, header=True, styles=None, head_color=BLUE):
        super().__init__()
        self.cells = []
        total = sum(widths)
        for r, cells in enumerate(rows):
            x, line = -total / 2, []
            for c, s in enumerate(cells):
                mob = None
                if s:
                    if header and r == 0:
                        style = (head_color, BOLD)
                    else:
                        style = styles[c] if styles else (INK, NORMAL)
                    mob = fit_w(line_at(s, x, -r * row_h, size, *style), widths[c] - 0.25)
                    self.add(mob)
                line.append(mob)
                x += widths[c]
            self.cells.append(line)
        self.rule = None
        if header:
            self.rule = Line(LEFT * total / 2, RIGHT * total / 2, color=MUTED, stroke_width=2).move_to(
                DOWN * row_h * 0.52)
            self.add(self.rule)

    def cell(self, r, c):
        return self.cells[r][c]

    def col(self, c, head=True):
        return VGroup(*[row[c] for k, row in enumerate(self.cells) if row[c] is not None and (head or k)])

    def row(self, r):
        return VGroup(*[m for m in self.cells[r] if m is not None])


class Listing(VGroup):
    """A program listing: one Text per line, indentation kept, blank lines as half gaps."""

    def __init__(self, src, size=CODE, color=INK):
        super().__init__()
        unit = code("M" * 10, size).width / 10
        step, y = size * 0.0175, 0.0
        self.base, self.lit = color, None
        for raw in src.strip("\n").split("\n"):
            if not raw.strip():
                y -= step / 2
                continue
            line = code(raw.strip() + "|", size, color)        # the bar gives every line the same height
            line.move_to(UP * y).align_to(RIGHT * (len(raw) - len(raw.lstrip())) * unit, LEFT)
            line.remove(line[-1])
            self.add(line)
            y -= step
        self.lines = list(self.submobjects)

    def focus(self, i, color=FLASH):
        """Animations that light line ``i`` (None: no line) and put the last lit line back."""
        anims = []
        if self.lit is not None and self.lit != i:
            anims.append(self.lines[self.lit].animate.set_color(self.base))
        if i is not None and self.lit != i:
            anims.append(self.lines[i].animate.set_color(color))
        self.lit = i
        return anims


class Options(VGroup):
    """Answer options (a) to (d): in a row (``across``) or one under another. ``items`` are (letter, word)."""

    def __init__(self, items, size=LABEL, across=False, gap=0.7, roomy=False):
        super().__init__()
        self.rows, self.across, self.roomy = {}, across, roomy
        x, step = 0.0, size * (0.033 if roomy else 0.0195)       # roomy: space for a note under every option
        for k, (letter, word) in enumerate(items):
            y = 0.0 if across else -k * step
            tag = line_at(f"({letter})", x if across else 0.0, y, size, BLUE, BOLD)
            body = line_at(word, tag.line_end + size * 0.004, y, size, INK)
            row = VGroup(tag, body)
            self.rows[letter] = row
            self.add(row)
            x = row.get_right()[0] + gap

    def right(self, letter):
        """The answer turns green and gets a tick."""
        row = self.rows[letter]
        return [row.animate.set_color(GOOD), FadeIn(tick(0.26).next_to(row, RIGHT, buff=0.16), scale=0.6)]

    def out(self, *letters):
        """These options go grey."""
        return [self.rows[letter].animate.set_color(MUTED) for letter in letters]

    def note(self, letter, s, color=MUTED, size=SMALL):
        """A short reason beside an option (below it when the options are in a row)."""
        row = self.rows[letter]
        if self.across:
            return text(s, size, color).next_to(row, DOWN, buff=0.16)
        if self.roomy:
            return text(s, MIN_FONT, color).next_to(row[1], DOWN, buff=0.12, aligned_edge=LEFT)
        x = max(r.get_right()[0] for r in self.rows.values()) + 0.9
        return fit_w(place(text(s, size, color), left=x, y=row.get_y()), EDGE_X - x)


class Question(VGroup):
    """A practice question: its label, the sentence (lines of pieces, see ``para``) and the options."""

    def __init__(self, label, lines, options, size=LABEL, across=True, roomy=False):
        super().__init__()
        self.label = text(label, SMALL, MUTED, BOLD)
        self.body = para(*lines, size=size)
        self.opts = Options(options, size, across, roomy=roomy)
        self.add(self.label, self.body, self.opts)
        self.arrange(DOWN, buff=size * 0.0085, aligned_edge=LEFT)


def sentence_question(label, stem, options, letters="abcd", size=SMALL):
    """A question whose options are whole sentences: one under another, with room for a note under each."""
    q = Question(label, stem, list(zip(letters, options)), size, across=False, roomy=True)
    return place(q, left=-EDGE_X + 0.3, top=BOARD_TOP - 0.1)


def fan(word, leaves, word_y=0.72, leaf_y=-0.9, spread=4.5, size=LABEL):
    """One word with an arrow to each of its sentences. The group has ``.word``, ``.arrows`` and ``.leaves``."""
    top = text(word, TITLE, BLUE, BOLD).move_to(UP * word_y)
    n = len(leaves)
    items = VGroup(*[text(s, size).move_to(RIGHT * spread * (k - (n - 1) / 2) + UP * leaf_y)
                     for k, s in enumerate(leaves)])
    arrows = VGroup(*[Arrow(top.get_bottom() + DOWN * 0.12, m.get_top() + UP * 0.12, buff=0, color=BROWN,
                            stroke_width=4, tip_length=0.2) for m in items])
    group = VGroup(top, arrows, items)
    group.word, group.arrows, group.leaves = top, arrows, items
    return group


# ============================================================ the cast ====

SKIN = "#F2D0B0"               # characters use neutral tones plus their shirt colour
HAIR = "#4E3B2A"
LIPS = "#3A1F1F"
SHIRT_T = "#8C6239"            # the teacher wears brown
RING_ON = INK
RING_OFF = "#3A3A3A"
SHIRTS = ("#1C758A", "#2B5F8A", "#3A8A7A", "#4A6FA5")     # students A, B, C, D wear shades of blue


class Face(VGroup):
    """A drawn character: head, hair, eyes, brows, mouth and shoulders.

    ``look_to(name)`` returns the animations for a change of expression;
    ``talk(on)`` lights the ring of the speaker."""

    LOOKS = {"neutral": ("soft", "flat"), "smile": ("smile", "flat"), "happy": ("open", "up"),
             "ask": ("small", "one_up"), "think": ("flat", "down"), "confused": ("wavy", "tilt"),
             "surprised": ("o", "up"), "oops": ("frown", "tilt")}

    def __init__(self, r=FACE_R, shirt=SHIRT_T, hair="short", glasses=False, look="neutral"):
        super().__init__()
        self.r = r
        self.head = Circle(radius=r, stroke_color="#B89A7C", stroke_width=2, fill_color=SKIN, fill_opacity=1)
        self.body = Arc(radius=r * 1.3, start_angle=0, angle=PI, stroke_color=shirt, stroke_width=2,
                        fill_color=shirt, fill_opacity=1)
        self.body.next_to(self.head, DOWN, buff=-r * 0.3)
        self.ring = Circle(radius=r * 1.2, stroke_color=RING_OFF, stroke_width=3)
        extras = VGroup(Arc(radius=r, start_angle=PI * 0.1, angle=PI * 0.8, stroke_width=0, fill_color=HAIR,
                            fill_opacity=1))
        if hair == "pony":
            extras.add(Ellipse(width=r * 0.5, height=r * 0.95, stroke_width=0, fill_color=HAIR,
                               fill_opacity=1).move_to(self.at(0.95, 0.35)))
        elif hair == "bun":
            extras.add(Circle(radius=r * 0.3, stroke_width=0, fill_color=HAIR, fill_opacity=1).move_to(self.at(0, 1.05)))
        elif hair == "curly":
            for dx in (-0.55, 0.0, 0.55):
                extras.add(Circle(radius=r * 0.24, stroke_width=0, fill_color=HAIR,
                                  fill_opacity=1).move_to(self.at(dx, 0.92 - 0.2 * abs(dx))))
        if glasses:
            for sx in (-1, 1):
                extras.add(Circle(radius=r * 0.2, stroke_color=HAIR, stroke_width=2).move_to(self.at(sx * 0.34, 0.06)))
            extras.add(Line(self.at(-0.14, 0.06), self.at(0.14, 0.06), stroke_color=HAIR, stroke_width=2))
        self.eyes = VGroup(*[Dot(self.at(sx * 0.34, 0.06), radius=r * 0.085, color=LIPS) for sx in (-1, 1)])
        self.mouth = self._mouth("soft")
        self.brow_l, self.brow_r = self._brows("flat")
        self.add(self.body, self.ring, self.head, extras, self.eyes, self.brow_l, self.brow_r, self.mouth)
        self.now = None
        self.play_look(look)

    def at(self, x, y):
        """A point on the face, in head radii from its centre."""
        return self.head.get_center() + self.r * np.array([x, y, 0.0])

    def _mouth(self, kind):
        a, b = self.at(-0.32, -0.42), self.at(0.32, -0.42)
        if kind == "smile":
            m = ArcBetweenPoints(a, b, angle=PI / 2)
        elif kind == "soft":
            m = ArcBetweenPoints(self.at(-0.22, -0.44), self.at(0.22, -0.44), angle=PI / 4)
        elif kind == "open":
            m = ArcBetweenPoints(a, b, angle=PI * 0.85).set_fill(LIPS, 1)
        elif kind == "frown":
            m = ArcBetweenPoints(self.at(-0.26, -0.56), self.at(0.26, -0.56), angle=-PI / 2)
        elif kind == "o":
            m = Circle(radius=self.r * 0.15).move_to(self.at(0, -0.5)).set_fill(LIPS, 1)
        elif kind == "wavy":
            m = VMobject().set_points_smoothly([a, self.at(-0.1, -0.36), self.at(0.1, -0.5), b])
        elif kind == "small":
            m = Line(self.at(-0.14, -0.46), self.at(0.14, -0.46))
        else:
            m = Line(self.at(-0.24, -0.46), self.at(0.24, -0.46))
        return m.set_stroke(LIPS, 3)

    def _brows(self, kind):
        lift = 0.12 if kind == "up" else 0.0
        inner = {"down": -0.08, "tilt": 0.1}.get(kind, 0.0)
        y = 0.4 + lift
        left = Line(self.at(-0.52, y), self.at(-0.18, y + inner))
        right = Line(self.at(0.18, y + inner + (0.06 if kind == "one_up" else 0)),
                     self.at(0.52, y + (0.2 if kind == "one_up" else 0)))
        return left.set_stroke(HAIR, 3), right.set_stroke(HAIR, 3)

    def play_look(self, name):
        """Set the expression at once (before the face is on screen)."""
        mouth, brows = self.LOOKS[name]
        left, right = self._brows(brows)
        self.mouth.become(self._mouth(mouth))
        self.brow_l.become(left)
        self.brow_r.become(right)
        self.now = name
        return self

    def look_to(self, name):
        if self.now == name:
            return []
        mouth, brows = self.LOOKS[name]
        left, right = self._brows(brows)
        self.now = name
        return [self.mouth.animate.become(self._mouth(mouth)), self.brow_l.animate.become(left),
                self.brow_r.animate.become(right)]

    def talk(self, on):
        return self.ring.animate.set_stroke(RING_ON if on else RING_OFF, width=6 if on else 3)

# ============================================================= lesson ====

CRUMB = "C-CAT Preparation  ›  English  ›  Grammar  ›  Active and Passive Voice"
STEM = [("Choose the correct passive form of:", MUTED)]

Q1 = ("Practice question 1", [STEM, ['"You must update the dependencies before the release."']],
      ["The dependencies must be update before the release.", "The dependencies must updated before the release.",
       "The dependencies must be updated before the release.",
       "The dependencies must been updated before the release."])
Q2 = ("Practice question 2", [STEM, ['"Someone should have tested this code before the merge."']],
      ["This code should be tested before the merge.", "This code should have been tested before the merge.",
       "This code should have tested before the merge.", "This code should had been tested before the merge."])

NOW = [["can be deployed", "may be cached", "must be rotated"],
       ["should be reviewed", "will be released", "ought to be documented"]]
PAST = [["could have been avoided", "might have been lost"],
        ["must have been deleted", "should have been tested"]]
SEMI = [["Active", "Passive"],
        ["has to approve the request", "the request has to be approved"],
        ["is going to replace the disk", "the disk is going to be replaced"],
        ["need not inform the client", "the client need not be informed"],
        ["used to store the logs", "the logs used to be stored"]]
MEANING = [["Active", "Passive", "Meaning"],
           ["We can restore the backup.", "The backup can be restored.", "ability"],
           ["You may close the ticket.", "The ticket may be closed.", "permission"],
           ["They must encrypt the data.", "The data must be encrypted.", "obligation"]]
POLICY = [("Passwords", "must be rotated", "every 90 days.", "mandatory"),
          ("Access", "may be revoked", "without notice.", "permitted"),
          ("Incidents", "should be reported", "within one hour.", "recommended")]


class ModalVerbsInThePassiveVoice(LMSScene):
    lesson_title = "Modal Verbs in the Passive Voice"

    def construct(self):
        self.camera.background_color = BG
        self.cast = None
        self.title_bar = None
        self.spoken = None
        self.talking = None
        self.faces = {}
        self.q_now, self.q_marks, self.picked = None, [], {}

        self.hook()
        self.topic()
        self.exam()
        self.attempts()
        self.what()
        self.semi()
        self.meaning()
        self.why()
        self.payoff()
        self.summary()
        self.next_session()

    # ------------------------------------------------------ stage helpers --

    def kept(self):
        """Family of what stays through a scene change: the characters and the heading."""
        keep = set()
        for mob in (self.cast, self.title_bar):
            if mob is not None:
                keep.update(mob.get_family())
        return keep

    def wipe(self, run_time=0.6):
        """Clear the board and the spoken line."""
        keep = self.kept()
        parts = [p for m in self.mobjects for p in m.family_members_with_points() if p not in keep]
        if parts:
            self.play(FadeOut(Group(*parts)), run_time=run_time)
        for mob in list(self.mobjects):
            if mob not in keep and not any(p in keep for p in mob.get_family()):
                self.remove(mob)
        self.spoken = None
        self.q_now, self.q_marks, self.picked = None, [], {}

    def heading(self, s):
        """The scene heading: a title with a blue rule, between the teacher and the students."""
        title = fit_w(text(s, HEAD, INK, BOLD), HEAD_W)
        rule = Line(LEFT, RIGHT, color=BLUE, stroke_width=3).set_width(title.width).next_to(title, DOWN, buff=0.14)
        bar = VGroup(title, rule).move_to(UP * HEAD_Y)
        anims = [FadeIn(bar, shift=DOWN * 0.2)]
        if self.title_bar is not None:
            anims.append(FadeOut(self.title_bar, shift=DOWN * 0.2))
        self.play(*anims, run_time=0.6)
        self.title_bar = bar

    def begin(self, sid, title, head):
        self.scene_start(sid, title=title)
        self.heading(head)

    def finish(self, sid):
        self.wipe()
        self.scene_end(sid)

    def the_end(self, sid):
        """The last scene: the characters and the heading leave with everything else."""
        self.cast = self.title_bar = None
        if self.mobjects:
            self.play(FadeOut(Group(*self.mobjects)), run_time=1.0)
        self.scene_end(sid)

    def fit(self, *mobs, top=BOARD_TOP):
        """Layout guard: bring every mobject onto the board (made smaller only if it is larger than the board)."""
        width, height = 2 * EDGE_X, top - FLOOR
        for mob in mobs:
            if mob.width > width or mob.height > height:
                mob.scale(min(width / mob.width, height / mob.height))
            dx = max(0.0, -EDGE_X - mob.get_left()[0]) - max(0.0, mob.get_right()[0] - EDGE_X)
            dy = max(0.0, FLOOR - mob.get_bottom()[1]) - max(0.0, mob.get_top()[1] - top)
            mob.shift(RIGHT * dx + UP * dy)
        return mobs[0]

    # ------------------------------------------------------------ the cast --

    def opening(self, title, previous):
        """The silent opening card (where we are, what came before); then the cast comes in."""
        crumb = fit_w(text(CRUMB, SMALL, MUTED), 2 * EDGE_X)
        one_line = text(title, TITLE, INK, BOLD).width <= 2 * EDGE_X - 1.0
        name = VGroup(*[text(s, TITLE, INK, BOLD) for s in (title if one_line else wrap_lines(title, 2)).split("\n")])
        name.arrange(DOWN, buff=0.22)                 # a long title goes on two centred lines
        rule = Line(LEFT * 1.3, RIGHT * 1.3, color=BLUE, stroke_width=4)
        before = text(f"Previous topic:  {previous}", LABEL, BROWN)
        card = VGroup(crumb, name, rule, before).arrange(DOWN, buff=0.4).move_to(DOWN * 0.6)
        self.fit(card)
        self.play(FadeIn(crumb), FadeIn(name, shift=UP * 0.2), Create(rule), run_time=1.0)
        self.play(FadeIn(before, shift=UP * 0.15), run_time=0.6)
        self.enter_cast()
        return card

    def enter_cast(self):
        """The teacher (top left) and the four students (top right) come in and stay for the whole video."""
        t = Face(FACE_R, SHIRT_T, "short", glasses=True)
        a = Face(STUDENT_R, SHIRTS[0], "short")                    # A: confident, near the window
        b = Face(STUDENT_R, SHIRTS[1], "pony", glasses=True)       # B: cautious, front row
        c = Face(STUDENT_R, SHIRTS[2], "bun")                      # C: the second student
        d = Face(STUDENT_R, SHIRTS[3], "curly")                    # D: at the back
        t.shift(UP * (TOP - t.get_top()[1]) + RIGHT * (-EDGE_X - t.get_left()[0]))
        students = VGroup(a, b, c, d).arrange(RIGHT, buff=STUDENT_GAP, aligned_edge=DOWN)
        students.shift(UP * (TOP - students.get_top()[1]) + RIGHT * (EDGE_X - students.get_right()[0]))
        self.faces = {"T": t, "A": a, "B": b, "C": c, "D": d}
        self.cast = VGroup(t, a, b, c, d)
        self.play(FadeIn(t, shift=RIGHT * 0.4), FadeIn(students, shift=LEFT * 0.4), run_time=0.6)

    def react(self, who, look):
        """Animations that change the expression of one character, or of several ("ABCD")."""
        return [anim for name in who for anim in self.faces[name].look_to(look)]

    def speaker(self, who, look=None, other=None):
        """Show who speaks: "N" narrator (everyone listens), "T" teacher, "A" to "D" a student.

        ``look`` is the speaker's expression. ``other`` is the listeners': the students
        while the teacher speaks, the teacher while a student speaks."""
        anims = []
        for name, face in self.faces.items():
            if name == who:
                want = look or "smile"
            elif who != "N" and "T" in (who, name):
                want = other or "neutral"
            else:
                want = "neutral"
            anims += face.look_to(want)
        if self.talking != who:
            anims += [self.faces[name].talk(name == who) for name in (self.talking, who) if name in self.faces]
            self.talking = who
        if anims:
            self.play(*anims, run_time=0.25)

    def show_line(self, who, s):
        """The strip under the heading: a teacher question or a student line (None clears it).

        No speaker label: the lit ring shows who is speaking. Student lines are in italics."""
        new = None
        if s:
            new = fitted_text(s, STRIP_W, LABEL, INK, max_lines=2, slant=NORMAL if who == "T" else ITALIC)
            if new.height > STRIP_TOP - STRIP_BOTTOM:
                new.scale((STRIP_TOP - STRIP_BOTTOM) / new.height)
            new.move_to(UP * STRIP_Y)
        anims = ([FadeOut(self.spoken)] if self.spoken is not None else []) + ([FadeIn(new)] if new is not None else [])
        if anims:
            self.play(*anims, run_time=0.3)
        self.spoken = new

    def countdown(self, seconds):
        """Thinking time: a bar under the heading runs out."""
        bar = Line(LEFT * 1.6, RIGHT * 1.6, color=FLASH, stroke_width=5).move_to(UP * TIMER_Y)
        self.play(FadeIn(bar), run_time=0.3)
        self.play(Uncreate(bar), run_time=max(0.5, seconds - 0.3), rate_func=linear)

    # -------------------------------------------- questions on the board --

    def show_question(self, q):
        """Put question ``q`` on the board, in place of the question (and its marks) that is there."""
        old = [m for m in (getattr(self, "q_now", None), *getattr(self, "q_marks", [])) if m is not None]
        anims = [FadeIn(q, shift=UP * 0.15)] + ([FadeOut(VGroup(*old))] if old else [])
        self.play(*anims, run_time=0.6)
        self.q_now, self.q_marks, self.picked = q, [], {}

    def keep(self, mob):
        """A mark that belongs to the question on the board: it leaves with the question."""
        self.q_marks = getattr(self, "q_marks", []) + [mob]
        return mob

    def pick(self, q, letter, color=BLUE):
        """A student's choice: a line under the option."""
        line = self.keep(under(q.opts.rows[letter], color))
        self.picked = {**getattr(self, "picked", {}), letter: line}
        return Create(line)

    def repick(self, letter, color=BAD):
        """The line under a choice changes colour (the choice turned out wrong)."""
        return self.picked[letter].animate.set_color(color)

    def tag(self, q, letter, s, color=BROWN):
        """A short note for one option."""
        return FadeIn(self.keep(q.opts.note(letter, s, color)), shift=RIGHT * 0.2)

    def yes(self, q, letter, s=None):
        """The answer: green, with a tick and an optional note. The tick leaves with its question."""
        row = q.opts.rows[letter]
        mark = self.keep(tick(0.26).next_to(row, RIGHT, buff=0.16))
        return [row.animate.set_color(GOOD), FadeIn(mark, scale=0.6)] + ([self.tag(q, letter, s, GOOD)] if s else [])

    def no(self, q, letters, s=None):
        """Wrong options go grey; each gets the same optional note."""
        return q.opts.out(*letters) + ([self.tag(q, letter, s, BAD) for letter in letters] if s else [])

    def timed(self, nid, spoken, q2, seconds, *cues):
        """The teacher gives the time: half of it runs on the question on the board, half on ``q2``."""
        self.T(nid, spoken, *cues, look="ask", other="think", think=seconds / 2)
        self.show_question(q2)
        self.countdown(seconds / 2)

    # ------------------------------------------------- narration drivers --

    def cue(self, n, word):
        """Wait for ``word`` (or ``(word, occurrence)``) in narration ``n``."""
        spoken, occ = (word, 1) if isinstance(word, str) else word
        try:
            self.at_word(n, spoken, occ)
        except ValueError:
            pass                          # the aligner may hear a word differently: carry on

    def run(self, n, cues, think=0.0):
        """Play ``(word, what)`` pairs in spoken order, then hold until ``n`` ends.

        ``what`` is an animation, a list of animations, or a function that returns
        one (or plays things itself and returns None). ``think`` seconds of the
        pause after ``n`` are shown as a countdown."""
        for word, what in cues:
            if word:
                self.cue(n, word)
            if isinstance(what, (types.FunctionType, types.MethodType)):
                what = what()
            anims = self.flat(what) if what is not None else []
            if anims:
                self.play(*anims)
        if think:
            self.wait_for_narration(n, include_pause=False)
            self.countdown(think)
        self.wait_for_narration(n)
        return n

    @classmethod
    def flat(cls, what):
        """Animations from a single animation or a (nested) list of them."""
        if not isinstance(what, (list, tuple)):
            return [what]
        return [a for item in what for a in cls.flat(item)]

    def say(self, who, nid, spoken, cues, look=None, other=None, shown=None, think=0.0):
        self.speaker(who, look, other)
        self.show_line(who, shown)
        n = self.narrate(id=nid, text=spoken, voice=VOICES[who], subtitle=True,
                         pause_after=think if think else TURN_PAUSE)
        return self.run(n, cues, think)

    def N(self, nid, spoken, *cues):
        """Narrator: introduces, connects, sums up. Everyone listens."""
        return self.say("N", nid, spoken, cues)

    def T(self, nid, spoken, *cues, look="smile", other=None, think=0.0):
        """Teacher statement."""
        return self.say("T", nid, spoken, cues, look, other, None, think)

    def Q(self, nid, spoken, *cues, shown=None, look="ask", other="think", think=0.0):
        """Teacher question: spoken, and shown in the strip."""
        return self.say("T", nid, spoken, cues, look, other, shown or spoken, think)

    def S(self, who, nid, spoken, *cues, shown=None, look="smile", other=None):
        """A line of student "A", "B", "C" or "D": own voice, shown in the strip."""
        return self.say(who, nid, spoken, cues, look, other, shown or spoken)

    # ============================ 1. WHERE DOES "BE" GO AFTER "MUST"? ======

    def hook(self):
        self.scene_start("S01_hook", title='Where Does "Be" Go After "Must"?')
        card = self.opening("Modal Verbs in the Passive Voice", "Tense-based conversion")
        self.heading("Where does be go?")

        a1 = para([("Active", MUTED, BOLD), '"You', ("must", BROWN, BOLD), 'update the dependencies."'])
        p1 = para([("Passive", MUTED, BOLD), '"The dependencies', ("must be updated.\"", GOOD, BOLD)])
        a2 = para([("Active", MUTED, BOLD), '"Someone', ("should have", BROWN, BOLD), 'tested this code."'])
        p2 = para([("Passive", MUTED, BOLD), '"This code', ("should have been tested.\"", GOOD, BOLD)])
        board = VGroup(a1, p1, a2, p2).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        a2.shift(DOWN * 0.35)
        p2.shift(DOWN * 0.35)
        place(board, x=0.0, top=BOARD_TOP - 0.15)
        log1 = column(text("Keep 'must'", SMALL, BROWN), text("'update' is the base form, so BE stays 'be'", SMALL, BROWN),
                      text("The main verb becomes V3: 'updated'", SMALL, BROWN), buff=0.14)
        log2 = column(text("Keep 'should have'", SMALL, BROWN),
                      text("'tested' is V3 after 'have', so BE becomes 'been'", SMALL, BROWN), buff=0.14)
        for log in (log1, log2):
            place(log, left=board.get_left()[0], top=-1.95)
        base = text("After a modal: always the base form", LABEL, BLUE, BOLD).move_to(DOWN * 2.2)
        same = text("The same rule: no new table to memorise", LABEL, INK, BOLD).move_to(DOWN * 3.05)
        self.fit(VGroup(board, log1, log2), base, same)

        self.N("s1_01", "Last time, be took over the form of the main verb. But modal verbs never change form. So the "
                        "class has to work out whether the rule still holds.",
               ("form", lambda: [FadeOut(card), up(a1)]),
               ("modal", lambda: up(a2)),
               ("holds", lambda: [hl(a1[0][2], 1.2), hl(a2[0][2], 1.1)]))
        self.T("s1_02", "You must update the dependencies. Apply last session's rule.",
               ("update", lambda: hl(a1, 1.03)), look="ask")
        self.S("B", "s1_03", "Keep the auxiliary, must. Insert be in the form the main verb had. After must, the main "
                             "verb is update, which is the base form. So be stays as be. Then the main verb becomes V "
                             "three, updated.",
               ("Keep", lambda: side(log1[0])),
               ("base", lambda: side(log1[1])),
               ("becomes", lambda: side(log1[2])),
               shown="Keep 'must'. 'Update' is the base form, so 'be' stays as 'be'. Then V3: 'updated'.",
               look="think")
        self.S("B", "s1_04", "The dependencies must be updated.", (None, lambda: up(p1)), other="happy")
        self.S("A", "s1_05", "The rule still works. Modals just always take the base form after them.",
               ("base", lambda: [FadeOut(log1), up(base)]), look="surprised")
        self.T("s1_06", "Exactly. Now the second one.",
               ("second", lambda: [FadeOut(base), hl(a2, 1.03)]), look="happy")
        self.S("D", "s1_07", "Should have tested. Keep should have. Tested is V three after have, so be becomes been. "
                             "Then tested.",
               ("Keep", lambda: side(log2[0])),
               ("been", lambda: side(log2[1])),
               shown="Keep 'should have'. 'Tested' is V3 after 'have', so 'be' becomes 'been'.", look="think")
        self.S("D", "s1_08", "This code should have been tested.", (None, lambda: up(p2)), other="happy")
        self.T("s1_09", "Same rule. No new table to memorise.", ("rule", lambda: up(same)), look="happy")

        self.finish("S01_hook")

    # ================================================== 2. THE TOPIC =======

    def topic(self):
        self.begin("S02_topic", "The Topic", "Modals in the passive")

        row1 = text("can     could     may     might     must", BODY, BROWN, BOLD)
        row2 = text("shall     should     will     would     ought to", BODY, BROWN, BOLD)
        means = text("ability     permission     possibility     obligation", LABEL, MUTED)
        stays = text("In the passive, the modal stays exactly as it is", LABEL, INK, BOLD)
        board = VGroup(row1, row2, means, stays).arrange(DOWN, buff=0.5)
        stays.shift(DOWN * 0.3)
        place(board, x=0.0, top=BOARD_TOP - 0.35)
        self.fit(board)

        self.T("s2_01", "Modals such as can, could, may, might, must, shall, should, will, would and ought to express "
                        "ability, permission, possibility and obligation. In the passive, the modal stays exactly as "
                        "it is, and its meaning is preserved.",
               ("can", lambda: up(row1)),
               ("shall", lambda: up(row2)),
               ("ability", lambda: up(means)),
               ("stays", lambda: up(stays)))

        self.finish("S02_topic")

    # ======================================== 3. HOW C-CAT TESTS IT ========

    def exam(self):
        self.begin("S03_exam", "How C-CAT Tests It", "How C-CAT tests it")
        self.q1, self.q2 = self.fit(sentence_question(*Q1)), self.fit(sentence_question(*Q2))

        self.N("s3_01", "Two practice questions, written for this class.",
               ("practice", lambda: self.show_question(self.q1)))
        self.timed("s3_02", "Forty seconds.", self.q2, 40.0)

        self.scene_end("S03_exam")          # a question stays on the board for the next scene

    # ================================================== 4. ATTEMPTS ========

    def attempts(self):
        self.begin("S04_attempts", "Attempts", "First attempts")
        q1, q2 = self.q1, self.q2

        self.show_question(q1)
        self.Q("s4_01", "Question one. Anyone choose option D?", shown="Question 1. Anyone choose (d)?")
        self.S("C", "s4_02", "Must been updated. It sounded like has been.",
               ("Must", lambda: self.pick(q1, "d")), look="oops",
               shown="'Must been updated.' It sounded like 'has been'.")
        self.Q("s4_03", "What comes right after a modal?")
        self.S("C", "s4_04", "The base form. Must go, must be. Not must been.",
               ("base", lambda: self.tag(q1, "d", "after a modal: the base form only", BAD)),
               ("Not", lambda: self.repick("d")), look="think",
               shown="The base form. 'Must go', 'must be'. Not 'must been'.")

        self.show_question(q2)
        self.Q("s4_05", "Question two. Why not option A?", shown="Question 2. Why not (a)?")
        self.S("B", "s4_06", "Option A changes the meaning. Should be tested is advice for the future. Should have "
                             "been tested is about the past. It means it wasn't tested, and that was a mistake.",
               ("future", lambda: self.tag(q2, "a", "advice for the future", BAD)),
               ("past", lambda: self.tag(q2, "b", "about the past: it was not tested")),
               shown="(a) changes the meaning: advice for the future, not a mistake in the past.", look="think")
        self.S("D", "s4_07", "So option A changes the time frame, option C loses been, and option D has should had, "
                             "which is never correct.",
               ("loses", lambda: self.tag(q2, "c", "'been' is missing", BAD)),
               ("never", lambda: self.tag(q2, "d", "'should had' is never correct", BAD)),
               shown="(a) changes the time frame, (c) loses 'been', and (d) has 'should had'.")

        self.finish("S04_attempts")

    # ================================== 5. WHAT: THE MODAL PATTERNS ========

    def what(self):
        self.begin("S05_what", "WHAT: The Modal Patterns", "The modal patterns")

        t1 = phrase(text("MODAL + BE + V3", LABEL, BLUE, BOLD), text("present or future meaning", SMALL, MUTED), buff=0.5)
        g1 = Grid(NOW, (4.2, 4.0, 4.6), row_h=0.55, header=False)
        t2 = phrase(text("MODAL + HAVE BEEN + V3", LABEL, BROWN, BOLD), text("past meaning", SMALL, MUTED), buff=0.5)
        g2 = Grid(PAST, (5.4, 5.4), row_h=0.55, header=False)
        board = VGroup(t1, g1, t2, g2).arrange(DOWN, buff=0.35, aligned_edge=LEFT)
        t2.shift(DOWN * 0.3)
        g2.shift(DOWN * 0.3)
        place(board, x=0.0, top=BOARD_TOP - 0.2)
        hind = text("The past modal passive: the voice of hindsight", LABEL, BROWN, BOLD).move_to(DOWN * 3.0)
        self.fit(board, hind)

        self.play(up(t1), LaggedStart(*[side(g1.row(r)) for r in range(2)], lag_ratio=0.5), run_time=2.0)
        self.play(up(t2), LaggedStart(*[side(g2.row(r)) for r in range(2)], lag_ratio=0.5), run_time=2.0)
        self.countdown(5.0)                 # time to read the patterns: the script does not read them out
        self.S("A", "s5_01", "The outage could have been avoided. That's in every post mortem.",
               ("avoided", lambda: [hl(g2.cell(0, 0), 1.06), self.react("BCD", "happy")]), look="happy", other="happy",
               shown="'The outage could have been avoided.' That's in every post-mortem.")
        self.T("s5_02", "Exactly. The past modal passive is the voice of hindsight.",
               ("hindsight", lambda: up(hind)), look="happy")

        self.finish("S05_what")

    # ==================== 6. HOW: SEMI-MODALS FOLLOW THE SAME RULE =========

    def semi(self):
        self.begin("S06_semi", "HOW: Semi-Modals Follow the Same Rule", "Semi-modals")

        g = Grid(SEMI, (6.0, 6.6), row_h=0.6)
        place(g, x=0.0, top=BOARD_TOP - 0.2)
        rule = text("Followed by the base form?  Insert BE, then V3", LABEL, BROWN, BOLD).move_to(DOWN * 2.6)
        self.fit(g, rule)

        self.T("s6_01", "Some phrases act like modals. The same rule applies.",
               ("phrases", lambda: [FadeIn(g.rule)] + [side(g.row(r)) for r in range(3)]),
               ("rule", lambda: [side(g.row(3)), side(g.row(4))]))
        self.S("C", "s6_02", "Has to approve. After has to, the base form. So be. Then approved.",
               ("base", lambda: hl(g.cell(1, 0), 1.05)),
               ("approved", lambda: hl(g.cell(1, 1), 1.05)), look="think",
               shown="'Has to approve.' After 'has to', the base form. So 'be'. Then 'approved'.")
        self.T("s6_03", "Right. Any phrase that's followed by the base form behaves the same way. Insert be, then V "
                        "three.",
               ("Insert", lambda: up(rule)), look="happy")

        self.finish("S06_semi")

    # ========================== 7. HOW: MODALS KEEP THEIR MEANING ==========

    def meaning(self):
        self.begin("S07_meaning", "HOW: Modals Keep Their Meaning", "The meaning stays")

        g = Grid(MEANING, (5.0, 5.2, 2.8), size=SMALL, row_h=0.56,
                 styles=[(INK, NORMAL), (INK, NORMAL), (BROWN, BOLD)])
        place(g, x=0.0, top=BOARD_TOP - 0.2)
        swap1 = phrase(cross(0.24), text("must", LABEL), small_arrow(BAD), text("should", LABEL), buff=0.25)
        swap2 = phrase(cross(0.24), text("can", LABEL), small_arrow(BAD), text("may", LABEL), buff=0.25)
        swaps = phrase(swap1, swap2, buff=1.4).move_to(DOWN * 1.75)
        wrong = text("Correct grammar, but the meaning has changed", SMALL, BAD, BOLD).next_to(swaps, DOWN, buff=0.25)
        const = text("The modal is a constant: it passes through unchanged", LABEL, BROWN, BOLD).move_to(DOWN * 3.1)
        self.fit(g, VGroup(swaps, wrong), const)

        self.T("s7_01", "Here's a check that catches many traps. The modal's meaning must survive the conversion.",
               ("check", lambda: [FadeIn(g.rule)] + [side(g.row(r)) for r in range(4)]),
               ("meaning", lambda: hl(g.col(2, head=False), 1.06)))
        self.T("s7_02", "If an option changes must to should, or can to may, it has changed the meaning, even if the "
                        "grammar is correct.",
               ("should", lambda: up(swap1)),
               ("may", lambda: up(swap2)),
               ("grammar", lambda: up(wrong)))
        self.S("D", "s7_03", "So the modal is like a constant. It passes through unchanged.",
               ("constant", lambda: up(const)), look="think", other="happy")
        self.T("s7_04", "Good analogy.", look="happy")

        self.finish("S07_meaning")

    # ================================ 8. WHY: THE LANGUAGE OF POLICY =======

    def why(self):
        self.begin("S08_why", "WHY: The Language of Policy", "The language of policy")

        head = text("Security policy", SMALL, MUTED, BOLD)
        doc = para(*[[a, (b, BLUE, BOLD), c] for a, b, c, _ in POLICY], size=BODY, step=0.85)
        board = VGroup(head, doc).arrange(DOWN, buff=0.45, aligned_edge=LEFT)
        place(board, x=-1.6, top=BOARD_TOP - 0.2)
        tags = VGroup(*[text("= " + POLICY[k][3], LABEL, BROWN, BOLD).next_to(doc[k], RIGHT, buff=0.5)
                        for k in range(3)])
        action = text("The action matters more than who does it", LABEL, MUTED).move_to(DOWN * 2.6)
        self.fit(VGroup(board, tags), action)

        self.play(FadeIn(head), LaggedStart(*[up(line) for line in doc], lag_ratio=0.5), run_time=2.5)
        self.S("B", "s8_01", "Every line is a modal passive.",
               ("modal", lambda: [hl(doc[k][1], 1.06) for k in range(3)]), look="think")
        self.T("s8_02", "Policies, standards and requirements documents are written this way, because the action "
                        "matters more than who does it. If you understand modal passives, you can read compliance "
                        "rules precisely: must is mandatory, should is recommended, and may is permitted.",
               ("action", lambda: up(action)),
               ("mandatory", lambda: FadeIn(tags[0], shift=LEFT * 0.2)),
               ("recommended", lambda: FadeIn(tags[2], shift=LEFT * 0.2)),
               ("permitted", lambda: FadeIn(tags[1], shift=LEFT * 0.2)))

        self.finish("S08_why")

    # ============================ 9. PAYOFF: SOLVING BOTH QUESTIONS ========

    def payoff(self):
        self.begin("S09_payoff", "Payoff: Solving Both Questions", "Solving both questions")
        q1, q2 = self.fit(sentence_question(*Q1)), self.fit(sentence_question(*Q2))

        self.T("s9_01", "Question one.", (None, lambda: self.show_question(q1)), look="ask")
        self.S("C", "s9_02", "Modal must, then be in base form, then V three, updated. So must be updated. The answer "
                             "is option C. Option A has update, which isn't V three. Option B is missing be. Option D "
                             "has been, which can't follow a modal directly.",
               ("answer", lambda: self.yes(q1, "c", "modal + be + V3")),
               ("update", lambda: self.no(q1, "a", "'update' is not V3")),
               ("missing", lambda: self.no(q1, "b", "'be' is missing")),
               ("been", lambda: self.no(q1, "d", "'been' cannot follow a modal directly")),
               shown="Modal 'must', then 'be' in the base form, then the V3 'updated'. The answer is (c).",
               look="think", other="happy")

        self.T("s9_03", "Question two.", (None, lambda: self.show_question(q2)), look="ask")
        self.S("A", "s9_04", "Should have tested becomes should have been tested, keeping the past meaning. The "
                             "answer is option B. Option A changes the time frame to future advice. Option C is "
                             "missing been. Option D, should had, is ungrammatical.",
               ("answer", lambda: self.yes(q2, "b", "modal + have been + V3: the past meaning is kept")),
               ("frame", lambda: self.no(q2, "a", "the time frame changed: future advice")),
               ("missing", lambda: self.no(q2, "c", "'been' is missing")),
               ("ungrammatical", lambda: self.no(q2, "d", "'should had' is ungrammatical")),
               shown="'Should have been tested' keeps the past meaning. The answer is (b).", other="happy")

        self.finish("S09_payoff")

    # ================================================= 10. SUMMARY =========

    def summary(self):
        self.begin("S10_summary", "Summary", "Summary")

        points = bullets(["Modal + BE + V3: present or future", "Modal + HAVE BEEN + V3: the past",
                          "Semi-modals follow the same rule", "The modal's meaning stays exactly the same"], BODY, 0.42)
        place(points, x=0.0, top=BOARD_TOP - 0.4)
        self.fit(points)

        self.Q("s10_01", "Summary?")
        self.S("D", "s10_02", "Modal plus be plus V three for present or future. Modal plus have been plus V three for "
                              "the past. Semi-modals follow the same rule. The modal's meaning must stay exactly the "
                              "same.",
               ("Modal", lambda: side(points[0])),
               ("have", lambda: side(points[1])),
               ("follow", lambda: side(points[2])),
               ("meaning", lambda: side(points[3])),
               shown="Modal + be + V3 for present or future. Modal + have been + V3 for the past.", other="happy")

        self.finish("S10_summary")

    # ========================================= 11. WHAT COMES NEXT =========

    def next_session(self):
        self.begin("S11_next", "What Comes Next", "What comes next?")

        so_far = text("So far: every sentence was a statement", BODY).move_to(UP * 0.1)
        but = text("Code reviews and incident calls are full of questions", LABEL, BROWN, BOLD).move_to(DOWN * 0.8)
        qs = para([('"Who', BROWN, BOLD), 'approved this pull request?"'],
                  [('"Did', BROWN, BOLD), 'the CI pipeline run the tests?"'], size=BODY, step=0.9)
        place(qs, x=0.0, top=BOARD_TOP - 0.4)
        attempt = VGroup(cross(0.24), text('"Who was this pull request approved?"', LABEL, BAD)).arrange(RIGHT, buff=0.3)
        attempt.move_to(DOWN * 1.6)
        nxt = text("Next session:  Interrogative sentences (Passive voice)", LABEL, BROWN, BOLD).move_to(DOWN * 2.9)
        self.fit(so_far, but, qs, attempt, nxt)

        self.N("s11_01", "Every sentence so far has been a statement. But code reviews and incident calls are full of "
                         "questions.",
               ("statement", lambda: up(so_far)),
               ("questions", lambda: up(but)))
        self.wipe()
        self.Q("s11_02", "Change these into the passive. Where does who go? And what happens to did?",
               (None, lambda: LaggedStart(up(qs[0]), up(qs[1]), lag_ratio=0.5, run_time=1.5)),
               ("who", lambda: hl(qs[0][0], 1.2)),
               ("did", lambda: hl(qs[1][0], 1.2)),
               shown="Change these into the passive. Where does 'who' go? And what happens to 'did'?")
        self.S("C", "s11_03", "Who was this pull request approved?", (None, lambda: up(attempt[1])), look="ask",
               shown="'Who was this pull request approved?'")
        self.S("B", "s11_04", "Something's missing.", (None, lambda: FadeIn(attempt[0], scale=0.6)), look="think")
        self.T("s11_05", "Next session.", (None, lambda: up(nxt)))

        self.the_end("S11_next")

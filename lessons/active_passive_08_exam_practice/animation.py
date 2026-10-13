"""
animation.py for the LMS video generator.

Course : C-CAT Preparation - Section A: English Language and Verbal Ability
Module : 2 Grammar   Lesson : 6 Active and Passive Voice (Session 12)
Video  : 08 - Exam Practice: Active and Passive Voice   (previous: Common errors;  next: Lesson 7, Spotting Errors)
Source : C:/Final scripts/Scipts/Second/08 - Exam practice.pdf

Note: all questions are practice questions written for the class, not past-paper questions.

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
  Stage directions are not spoken: they are the visuals. The rapid-fire items and the voice flow are
  shown, not read out (the script gives them no spoken line); a thinking bar gives the time.

Sarvam AI voices (settings.json > audio.sarvam.voices, or --speaker VOICE=SPEAKER):
    "vijay": "vijay", "aditya": "aditya", "prasad": "kabir", "kavya": "kavya", "ritu": "ritu", "student_a": "rahul"

The two main questions are shown one at a time; the sixty seconds are split between them. In question 1
every option ends with "before the patch was released.": the board shows that tail as "...".

Section map:
  S01 Both directions   S02 The topic   S03 The two main questions   S04 Thinking out loud   S05 Question 2
  S06 Rapid-fire round   S07 The voice flow   S08 Why voice matters   S09 Payoff recap   S10 What comes next
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

Q1 = ("Practice question 1  (passive to active)",
      [['"The vulnerability had been reported by an external researcher'], ['before the patch was released."']],
      ["An external researcher reported the vulnerability ...",
       "An external researcher had reported the vulnerability ...",
       "An external researcher has reported the vulnerability ...",
       "An external researcher had been reporting the vulnerability ..."])
Q2 = ("Practice question 2  (passive question to active)",
      [['"Will the new hires be trained by the platform team?"']],
      ["Will the platform team train the new hires?", "Will the platform team be training the new hires?",
       "Does the platform team train the new hires?", "Will the new hires train the platform team?"])

REVERSE = ["Find the agent after 'by'", "Make it the subject", "Drop BE",
           "Put the tense back on the main verb"]
# the rapid-fire round: (the item, the answer on the board, the rule tag)
RAPID = [('1.  "They are building a new data centre in Hyderabad."   (to passive)',
          '"A new data centre is being built in Hyderabad."', "continuous + vague agent"),
         ('2.  "Open port 443 on the firewall."   (to passive)',
          '"Let port 443 be opened on the firewall."', "imperative: let"),
         ('3.  "Who wrote this recursive function?"   (to passive)',
          '"By whom was this recursive function written?"', "who becomes by whom"),
         ("4.  Find the error:  (A) The database migration was /  (B) completed successfully /  (C) by they.",
          "(C):  by them", "agent case"),
         ('5.  "The manager gave Priya the \'Best Debugger\' award."   (to passive, Priya first)',
          '"Priya was given the \'Best Debugger\' award by the manager."', "two objects")]
FLOW = ["1.  Identify the sentence type: statement / modal / question / imperative",
        "2.  Find the object (active to passive), or the agent after 'by' (passive to active)",
        "3.  Form-transfer: keep auxiliaries, BE takes the main verb's form, main verb to V3",
        "      (in reverse: drop BE, and give its form back to the main verb)",
        "4.  Questions: take the statement detour",
        "5.  Imperatives: tone first (request / advice / prohibition / command)",
        "6.  Check: tense unchanged, agreement, V3, pronoun case, is the agent needed?"]

assert len(RAPID) == 5 and len(FLOW) == 7


class ExamPracticeActiveAndPassiveVoice(LMSScene):
    lesson_title = "Exam Practice: Active and Passive Voice"

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
        self.aloud()
        self.second()
        self.rapid()
        self.flow()
        self.why()
        self.recap()
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
        """The answer: green, with a tick and an optional note."""
        return q.opts.right(letter) + ([self.tag(q, letter, s, GOOD)] if s else [])

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

    # ============================================= 1. BOTH DIRECTIONS ======

    def hook(self):
        self.scene_start("S01_hook", title="Both Directions")
        card = self.opening("Exam Practice: Active and Passive Voice", "Common errors (Active and Passive Voice)")
        self.heading("Both directions")

        there = phrase(text("Active", BODY, BROWN, BOLD), small_arrow(), text("Passive", BODY, BLUE, BOLD), buff=0.4)
        back = phrase(text("Passive", BODY, BLUE, BOLD), small_arrow(), text("Active", BODY, BROWN, BOLD), buff=0.4)
        ways = phrase(there, back, buff=2.0)
        place(ways, x=0.0, top=BOARD_TOP - 0.25)
        steps = bullets(REVERSE, LABEL, 0.3)
        place(steps, x=-2.2, top=-0.1)
        example = VGroup(text("had been reported", LABEL, BLUE), small_arrow().rotate(-PI / 2),
                         text("had reported", LABEL, BROWN, BOLD))
        example.arrange(DOWN, buff=0.25).next_to(steps, RIGHT, buff=1.2)
        careful = text("In reverse, it is easy to put the tense back wrongly", LABEL, BAD, BOLD).move_to(DOWN * 3.0)
        self.fit(ways, VGroup(steps, example), careful)

        self.N("s1_01", "Six lessons of conversion, all in one direction: active to passive. Today the exam turns some "
                        "of them around.",
               ("direction", lambda: [FadeOut(card), up(there)]),
               ("around", lambda: up(back)))
        self.T("s1_02", "Exams also ask you to go from passive back to active. Same rules, run in reverse. Let's see "
                        "whether the rules hold up.",
               ("reverse", lambda: hl(back, 1.06)))
        self.S("A", "s1_03", "Is it just undoing the steps?", look="ask")
        self.T("s1_04", "Mostly. Find the agent after by, make it the subject, drop be, and put the tense back on the "
                        "main verb. But in reverse, it's easy to put the tense back wrongly. That's what we'll test.",
               ("agent", lambda: side(steps[0])),
               ("subject", lambda: side(steps[1])),
               ("drop", lambda: side(steps[2])),
               ("tense", lambda: [side(steps[3]), up(example)]),
               ("wrongly", lambda: up(careful)))

        self.finish("S01_hook")

    # ================================================== 2. THE TOPIC =======

    def topic(self):
        self.begin("S02_topic", "The Topic", "Exam practice: voice")

        plan = bullets(["Two main questions, one in each direction", "Five rapid items: every sentence type"], BODY, 0.5)
        place(plan, x=0.0, y=-0.8)
        self.fit(plan)

        self.T("s2_01", "Two main questions, one in each direction, then five rapid items covering every sentence "
                        "type.",
               ("Two", lambda: side(plan[0])),
               ("five", lambda: side(plan[1])))

        self.finish("S02_topic")

    # ====================================== 3. THE TWO MAIN QUESTIONS ======

    def exam(self):
        self.begin("S03_exam", "The Two Main Questions", "Two main questions")
        self.q1, self.q2 = self.fit(sentence_question(*Q1)), self.fit(sentence_question(*Q2))

        self.N("s3_01", "Both are practice questions written for this class.",
               ("practice", lambda: self.show_question(self.q1)))
        self.timed("s3_02", "Sixty seconds for both.", self.q2, 60.0)

        self.scene_end("S03_exam")          # a question stays on the board for the next scene

    # ========================================== 4. THINKING OUT LOUD =======

    def aloud(self):
        self.begin("S04_aloud", "Thinking Out Loud", "Thinking out loud")
        q1 = self.q1

        self.show_question(q1)
        self.Q("s4_01", "Question one.", shown="Question 1.")
        self.S("B", "s4_02", "The agent is an external researcher, so that becomes the subject. The passive verb is "
                             "had been reported. Reverse the transfer: been was V three after had, so the main verb "
                             "goes back to V three after had. Had reported. That's option B.",
               ("agent", lambda: hl(q1.body[0][0], 1.03)),
               ("option", lambda: [self.pick(q1, "b", BROWN), self.tag(q1, "b", "had + V3 matches had been + V3")]),
               shown="The agent becomes the subject. 'Had been reported' goes back to 'had reported': (b).",
               look="think")
        self.S("C", "s4_03", "But option A is also correct English. Reported before the patch was released.",
               ("correct", lambda: self.pick(q1, "a")),
               shown="But (a) is also correct English: 'reported before the patch was released'.", look="ask")
        self.S("D", "s4_04", "It's correct English, but it's a different tense. The original was past perfect. "
                             "Converting voice can't change the tense.",
               ("tense", lambda: [self.tag(q1, "a", "simple past: the tense changed", BAD), self.repick("a")]),
               shown="Correct English, but a different tense. Converting voice can't change the tense.")
        self.Q("s4_05", "And option D?", shown="And (d)?")
        self.S("A", "s4_06", "Past perfect continuous. Wrong tense, and it suggests the reporting kept going for a "
                             "while.",
               ("Wrong", lambda: self.tag(q1, "d", "past perfect continuous: the wrong tense", BAD)), look="think")

        self.finish("S04_aloud")

    # ================================================= 5. QUESTION 2 =======

    def second(self):
        self.begin("S05_second", "Question 2", "The passive question")
        q2 = self.fit(sentence_question(*Q2))

        self.show_question(q2)
        self.Q("s5_01", "Question two?", shown="Question 2?")
        self.S("C", "s5_02", "Statement detour. Passive statement: the new hires will be trained by the platform team. "
                             "Active statement: the platform team will train the new hires. Back to a question: will "
                             "the platform team train the new hires? That's option A.",
               ("detour", lambda: hl(q2.body[0][0], 1.03)),
               ("option", lambda: [self.pick(q2, "a", BROWN), self.tag(q2, "a", "the statement detour, in reverse")]),
               shown="Statement detour: 'The platform team will train the new hires.' As a question: (a).",
               look="think")
        self.S("B", "s5_03", "Option B changes it to the future continuous. Option C changes it to the present. "
                             "Option D reverses the roles.",
               ("continuous", lambda: self.tag(q2, "b", "future continuous", BAD)),
               ("present", lambda: self.tag(q2, "c", "simple present", BAD)),
               ("reverses", lambda: self.tag(q2, "d", "the roles are reversed", BAD)),
               shown="(b) is future continuous. (c) is the present. (d) reverses the roles.")

        self.finish("S05_second")

    # ============================================= 6. RAPID-FIRE ROUND =====

    def rapid(self):
        self.begin("S06_rapid", "Rapid-Fire Round", "Rapid-fire round")

        items, answers = [], []
        for prompt, answer, _ in RAPID:
            item = fitted_text(prompt, 2 * EDGE_X - 0.8, LABEL, INK, max_lines=2)
            place(item, x=0.0, top=BOARD_TOP - 0.2)
            reply = fitted_text(answer, 2 * EDGE_X - 1.5, LABEL, GOOD, BOLD, max_lines=2).move_to(DOWN * 0.75)
            items.append(item)
            answers.append(reply)
        score = VGroup(*[VGroup(tick(0.2), text(tag, MIN_FONT, BROWN)).arrange(RIGHT, buff=0.2) for _, _, tag in RAPID])
        VGroup(*score[:3]).arrange(RIGHT, buff=0.7).move_to(DOWN * 2.45)
        VGroup(*score[3:]).arrange(RIGHT, buff=0.7).move_to(DOWN * 3.05)
        self.fit(*items, *answers, score)

        def show(k):
            """The next item, then fifteen seconds to convert it."""
            old = [items[k - 1], answers[k - 1]] if k else []
            self.speaker("N")
            self.show_line("T", None)
            self.play(up(items[k]), *[FadeOut(m) for m in old], run_time=0.6)
            self.countdown(15.0)

        def done(k):
            return [up(answers[k]), FadeIn(score[k], shift=UP * 0.1)]

        self.T("s6_01", "Fifteen seconds each. Give the conversion and the rule.", look="ask", other="think")
        show(0)
        self.S("D", "s6_02", "A new data centre is being built in Hyderabad. Is building becomes is being built. They "
                             "is vague, so we drop it.",
               ("built", lambda: done(0)),
               shown="'Is building' becomes 'is being built'. 'They' is vague, so we drop it.")
        show(1)
        self.S("A", "s6_03", "Let port four four three be opened on the firewall. Plain command with an object.",
               ("opened", lambda: done(1)), shown="'Let port 443 be opened on the firewall.' A plain command.")
        show(2)
        self.S("B", "s6_04", "By whom was this recursive function written? Who is the doer, so it becomes by whom. "
                             "Wrote becomes was written.",
               ("written", lambda: done(2)),
               shown="'Who' is the doer, so it becomes 'by whom'. 'Wrote' becomes 'was written'.")
        show(3)
        self.S("C", "s6_05", "Option C. It should be by them. Object form after by.",
               ("them", lambda: done(3)), shown="(C). It should be 'by them'. Object form after 'by'.")
        show(4)
        self.S("D", "s6_06", "Priya was given the Best Debugger award by the manager. Two object verb, with the "
                             "indirect object as the subject.",
               ("award", lambda: done(4)),
               shown="A two-object verb, with the indirect object as the subject.")
        self.T("s6_07", "Five for five. And every sentence type was covered.",
               ("Five", lambda: [hl(m, 1.05) for m in score] + self.react("ABCD", "happy")), look="happy")

        self.finish("S06_rapid")

    # =============================================== 7. THE VOICE FLOW =====

    def flow(self):
        self.begin("S07_flow", "The Voice Flow", "The voice flow")

        title = text("Voice question flow", LABEL, BLUE, BOLD)
        steps = column(*[fit_w(text(s, SMALL, MUTED if k == 3 else INK), 2 * EDGE_X - 0.6) for k, s in enumerate(FLOW)],
                       buff=0.19)
        board = VGroup(title, steps).arrange(DOWN, buff=0.32, aligned_edge=LEFT)
        place(board, x=0.0, top=BOARD_TOP - 0.12)
        both = text("One engine, and it runs in both directions", LABEL, BROWN, BOLD).move_to(DOWN * 3.2)
        self.fit(board, both)

        self.play(up(title), LaggedStart(*[side(m) for m in steps], lag_ratio=0.5), run_time=5.0)
        self.countdown(7.0)                 # time to read the flow: the script does not read it out
        self.N("s7_01", "A conversion engine built in six lessons, and it runs in both directions.",
               ("directions", lambda: up(both)))

        self.finish("S07_flow")

    # ============================================ 8. WHY VOICE MATTERS =====

    def why(self):
        self.begin("S08_why", "Why Voice Matters", "Why voice matters")

        ask = text("Who is missing from this sentence?", BODY, BROWN, BOLD)
        g = Grid([['"Mistakes were made."', "by whom?"], ['"Data was exposed."', "by whom?"]], (5.4, 3.0), size=BODY,
                 row_h=0.85, header=False, styles=[(INK, NORMAL), (BAD, BOLD)])
        board = VGroup(ask, g).arrange(DOWN, buff=0.7)
        place(board, x=0.0, top=BOARD_TOP - 0.4)
        beyond = text("Critical reading: useful well beyond the exam", LABEL, BLUE, BOLD).move_to(DOWN * 2.8)
        self.fit(board, beyond)

        self.S("B", "s8_01", "I've started noticing passive sentences in documentation and news reports, and asking "
                             "who's missing from them.",
               ("missing", lambda: up(ask)), look="think",
               shown="I've started noticing passive sentences, and asking who's missing from them.")
        self.T("s8_02", "That's critical reading. Mistakes were made, and data was exposed, leave out the people "
                        "responsible. Spotting those sentences is useful well beyond the exam.",
               ("Mistakes", lambda: up(g.row(0))),
               ("data", lambda: up(g.row(1))),
               ("beyond", lambda: up(beyond)), look="happy")

        self.finish("S08_why")

    # =============================================== 9. PAYOFF RECAP =======

    def recap(self):
        self.begin("S09_recap", "Payoff Recap", "Final answers")

        g = Grid([["Question 1", "had been reported", "had reported", "(b)"],
                  ["Question 2", "will be trained", "will train", "(a)"]], (2.4, 4.8, 3.4, 1.2), row_h=1.0,
                 header=False, styles=[(MUTED, BOLD), (BLUE, NORMAL), (BROWN, BOLD), (GOOD, BOLD)])
        place(g, x=0.0, top=BOARD_TOP - 0.5)
        arrows = VGroup(*[small_arrow().move_to([g.cell(0, 2).get_left()[0] - 0.75, g.cell(r, 1).get_y(), 0])
                          for r in range(2)])
        notes = VGroup(text("The past perfect is kept", SMALL, MUTED), text("Then back into question form", SMALL, MUTED))
        for note, r in zip(notes, range(2)):
            note.next_to(g.cell(r, 1), DOWN, buff=0.15, aligned_edge=LEFT)
        banner = text("Lesson 6: Active and Passive Voice, complete", BODY, GOOD, BOLD).move_to(DOWN * 2.6)
        self.fit(VGroup(g, arrows, notes), banner)

        self.T("s9_01", "Final answers.", look="ask")
        self.S("D", "s9_02", "Question one: option B. Had been reported becomes had reported, keeping the past "
                             "perfect. Option A changes the tense.",
               ("option", lambda: [up(g.row(0)), GrowArrow(arrows[0])]),
               ("keeping", lambda: FadeIn(notes[0])),
               shown="Question 1: (b). 'Had been reported' becomes 'had reported', keeping the past perfect.")
        self.S("C", "s9_03", "Question two: option A. Statement detour in reverse. Will be trained becomes will "
                             "train, and then it goes back into question form.",
               ("option", lambda: [up(g.row(1)), GrowArrow(arrows[1])]),
               ("form", lambda: FadeIn(notes[1])),
               (None, lambda: [FadeIn(banner, scale=1.1), self.react("ABD", "happy")]),
               shown="Question 2: (a). 'Will be trained' becomes 'will train', then back into question form.",
               other="happy")

        self.finish("S09_recap")

    # ========================================= 10. WHAT COMES NEXT =========

    def next_session(self):
        self.begin("S10_next", "What Comes Next", "What comes next?")

        done = VGroup(*[VGroup(tick(0.26), text(s, BODY)).arrange(RIGHT, buff=0.3)
                        for s in ("Prepositions", "Articles", "Voice")]).arrange(RIGHT, buff=1.0).move_to(UP * 0.1)
        together = text("In the exam they meet in one question type: spotting the error", LABEL, BROWN, BOLD)
        together.move_to(DOWN * 1.0)
        sent = para(['"Neither', ("the developer", BROWN, BOLD), "nor", ("the testers", BLUE, BOLD), ("was", INK, BOLD),
                     "available"], ['for the release review."'], size=BODY)
        place(sent, x=0.0, top=BOARD_TOP - 0.4)
        dev, testers, verb = sent[0][1], sent[0][3], sent[0][4]
        t1 = text("singular", SMALL, BROWN).next_to(dev, UP, buff=0.12)
        t2 = text("plural, and closer", SMALL, BLUE).next_to(testers, UP, buff=0.12)
        which = text("Which one does the verb follow?", LABEL, INK, BOLD).move_to(DOWN * 1.6)
        nxt = text("Next session:  Spotting errors (Lesson 7)", LABEL, BROWN, BOLD).move_to(DOWN * 2.9)
        sent.shift(DOWN * 0.3)
        t1.shift(DOWN * 0.3)
        t2.shift(DOWN * 0.3)
        self.fit(done, together, VGroup(sent, t1, t2), which, nxt)

        self.N("s10_01", "Prepositions, articles and voice each had their own lesson. In the exam, they turn up "
                         "together in one question type: spotting the error.",
               ("Prepositions", lambda: up(done[0])),
               ("articles", lambda: up(done[1])),
               ("voice", lambda: up(done[2])),
               ("together", lambda: up(together)))
        self.wipe()
        self.S("A", "s10_02", "Was available. Neither, nor is singular, isn't it?",
               (None, lambda: up(sent)),
               ("singular", lambda: [hl(verb, 1.3), FadeIn(t1)]), look="ask",
               shown="'Was available.' 'Neither ... nor' is singular, isn't it?")
        self.S("B", "s10_03", "But the testers is plural, and it's closer to the verb.",
               ("plural", lambda: [hl(testers, 1.06), FadeIn(t2)]), look="think",
               shown="But 'the testers' is plural, and it's closer to the verb.")
        self.S("D", "s10_04", "So which one does the verb follow?",
               ("which", lambda: [up(which), hl(verb, 1.3)]), look="ask")
        self.T("s10_05", "Next session. Spotting errors.", ("Spotting", lambda: up(nxt)))

        self.the_end("S10_next")

"""
animation.py for the LMS video generator.

Course : Pre-C-CAT - Section A - Logical Reasoning
Video  : Lesson 10 - Blood Relation I - 03 - Direct Relation Chains

Source script:
  C:\\Scripts\\Section A\\New folder\\Lesson 10 - Blood Relation I\\03 - Direct Relation Chains.pdf

Built on the pattern of machine_language_animation.py (golden reference):
  * one narrated class whose base is written literally as ``LMSScene``;
  * every ``self.narrate(...)`` written out in full, narration is the timeline
    (narrate > play > wait_for_narration), never timed waits;
  * one method per script section, framed by scene_start / clear_stage / scene_end;
  * all positions from the zone constants, text via ``fitted_text``, layouts
    stacked with next_to and guarded with ``no_overlap`` and the validator.

Three roles, three voices (the script has no speaker labels; lines were assigned by meaning):
  NARRATOR  sets the scene, connects sections, reads the summary and the quiz.
  TEACHER   teaches, asks, corrects (drawn top left).
  STUDENT   answers, doubts, voices the wrong instinct of each trap (drawn top right).
No role name is ever spoken.  ``self.speaker(...)`` before each narration lights the ring of the
character who is talking and sets the expression.

Lesson 10, Video 2 of 5 (file 03 in its folder).
The narration follows the script section by section and ends with the Section Quiz and its answer key.
Every chain in the script was traced again in the data block from its statements; all answers are correct.
In the PDF the quiz answer key is printed with its columns out of line; here each row carries its own answer
(key: 1 b, 2 c, 3 a, 4 d, 5 a).
Pauses: 3 seconds on the hook, 10 on the checkpoint, 12 on each practice and quiz screen.
Teaching review, 2026-10-09 (narration departs from the script here): practice 6 uses V, not U, and exam pattern 6
uses J, not I ("U" and "I" are heard as "you" and the pronoun); the teacher confirms every answer the student gives
and poses the exam patterns the student solves; quiz answers are spoken as "option B" with the word first;
"X is Y's what?" replaces the spoken "blank".
"""

import math

import numpy as np
from manim import *

from src.animation import LMSScene

# ============================================================== style ====

BG = "#0B1020"
INK = "#E6EAF2"
MUTED = "#8B95A7"
PANEL = "#151C2E"
CELL = "#1B2440"

TERM = INK             # series terms
DIFF = "#4FC3F7"       # first differences
SECOND = "#4FC3F7"     # second differences / pattern of the differences
RATIO = "#4FC3F7"      # ratios (the next topic's tool)
FOCUS = "#FFD54F"      # "look here" / predicted value
GOOD = "#66BB6A"       # confirmed answer
BAD = "#EF5350"        # wrong / trap

FONT = "Segoe UI"
MIN_FONT = 22          # readable floor: text is never shrunk below this
TITLE = 46
BODY = 30
LABEL = 28
SMALL = 24

# ============================================================= layout ====

FRAME_W = config.frame_width
FRAME_H = config.frame_height
SAFE = 0.45                                   # margin kept clear on every side
SAFE_W = FRAME_W - 2 * SAFE
SAFE_H = FRAME_H - 2 * SAFE

ZONE_W = 6.2                                  # width of each half-screen zone
LEFT_ZONE = LEFT * 3.35                       # centre of the left half
RIGHT_ZONE = RIGHT * 3.35                     # centre of the right half
TOP_Y = FRAME_H / 2 - SAFE - 0.9              # first row under the top edge
BOTTOM_Y = -FRAME_H / 2 + SAFE + 0.45         # caption / tracker row

CARD_TOP = FRAME_H / 2 - SAFE - 0.2           # top edge of a question card


# ======================================================= text helpers ====

SHORT_WORDS = {"a", "an", "as", "at", "be", "by", "do", "he", "if", "in", "is", "it", "no", "of", "on", "or", "so", "to", "up", "we"}


def cap_first(s):
    """Start on-screen text with a capital letter when it starts with a word (not a variable, unit or number)."""
    start = 0
    while start < len(s) and s[start] in "“\"'(":
        start += 1
    words = s[start:].split()
    if not words:
        return s
    first = words[0].rstrip(".,;:?!”’")
    plain = first.replace("'", "").replace("’", "").replace("-", "")
    if not (plain.isalpha() and plain.islower()):
        return s
    if len(plain) == 1:
        follower = words[1].rstrip(".,;:?!") if len(words) > 1 else ""
        if not (plain == "a" and len(follower) >= 2 and follower.replace("-", "").isalpha()):
            return s
    elif len(plain) == 2 and plain not in SHORT_WORDS:
        return s
    return s[:start] + s[start].upper() + s[start + 1:]

def text(s, size=BODY, color=INK, weight=NORMAL, t2c=None):
    return Text(cap_first(s), font=FONT, font_size=size, color=color, weight=weight, t2c=t2c or {})


def fit_width(mob, max_width):
    """Scale ``mob`` down (never up) to at most ``max_width``."""
    if mob.width > max_width:
        mob.scale_to_fit_width(max_width)
    return mob


def fit_height(mob, max_height):
    """Scale ``mob`` down (never up) to at most ``max_height``."""
    if mob.height > max_height:
        mob.scale_to_fit_height(max_height)
    return mob


def fit_within(mob, max_width, max_height):
    return fit_height(fit_width(mob, max_width), max_height)


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


def fitted_text(s, max_width, size=BODY, color=INK, weight=NORMAL, max_lines=3, t2c=None):
    """Readable text no wider than ``max_width`` (never below MIN_FONT)."""
    floor = max(MIN_FONT, 0.85 * size)
    for lines in range(1, max_lines + 1):
        body = s if lines == 1 else wrap_lines(s, lines)
        mob = text(body, size, color, weight, t2c)
        if mob.width <= max_width:
            return mob
        if size * max_width / mob.width >= floor:
            return mob.scale(max_width / mob.width)
        floor = MIN_FONT
    if size * max_width / mob.width >= MIN_FONT:
        return mob.scale(max_width / mob.width)
    raise ValueError(f"Text {s!r} cannot fit {max_width:.2f} units at a readable size; "
                     "shorten it or give it a wider container.")


def pill(label, color=FOCUS, size=SMALL, fill_opacity=0.14):
    """Short keyword tag. The box is sized from the text, so text cannot escape."""
    t = text(label, size, color, BOLD)
    box = RoundedRectangle(corner_radius=(t.height + 0.26) / 2, width=t.width + 0.5, height=t.height + 0.26,
                           stroke_color=color, stroke_width=2, fill_color=color, fill_opacity=fill_opacity)
    t.move_to(box)
    return VGroup(box, t)



# ================================================== vocabulary helpers ====

WORD = "#4FC3F7"          # the question word
OPTION = INK              # option text
TRAP = BAD                # eliminated options
KEY = GOOD                # the answer
STEP_COLS = {"READ": "#4FC3F7", "PREDICT": "#CE93D8", "ELIMINATE": "#EF5350", "CONFIRM": "#66BB6A"}


def process_strip(size=LABEL):
    """READ → PREDICT → ELIMINATE → CONFIRM as four chips."""
    parts = []
    for i, (name, col) in enumerate(STEP_COLS.items()):
        if i:
            parts.append(text("→", size, MUTED))
        parts.append(pill(name, col, size=size))
    return VGroup(*parts).arrange(RIGHT, buff=0.2)


def step_chip(strip, name):
    """The chip for one step inside a process strip."""
    return strip[2 * list(STEP_COLS).index(name)]


class OptionQuestion:
    """WORD: (a) … (b) … (c) … (d) …, with elimination and confirmation effects.
    ``key`` is the letter of the answer; ``traps`` maps letters to the reason
    each wrong option is removed."""

    def __init__(self, word, options, key, traps, width=6.0, word_size=TITLE):
        assert key in "abcd"[:len(options)] and set(traps) | {key} == set("abcd"[:len(options)])
        self.key, self.traps = key, traps
        self.word = pill(word, WORD, size=word_size)
        self.rows = VGroup(*[VGroup(text(f"({l})", LABEL, MUTED), fitted_text(o, width - 1.0, BODY, OPTION))
                             .arrange(RIGHT, buff=0.25) for l, o in zip("abcd", options)])
        self.rows.arrange(DOWN, buff=0.28, aligned_edge=LEFT)
        self.group = VGroup(self.word, self.rows).arrange(DOWN, buff=0.45, aligned_edge=LEFT)

    def row(self, letter):
        return self.rows["abcd".index(letter)]

    def strike(self, letter, reason_color=TRAP):
        """Animations: strike through a wrong option, dim it, and tag the reason."""
        r = self.row(letter)
        line = Line(r.get_left() + LEFT * 0.05, r.get_right() + RIGHT * 0.05, color=TRAP, stroke_width=3)
        tag = pill(self.traps[letter], reason_color, size=SMALL).next_to(r, RIGHT, buff=0.35)
        return VGroup(line, tag), [Create(line), r.animate.set_opacity(0.4), FadeIn(tag, shift=LEFT * 0.1)]

    def confirm(self):
        r = self.row(self.key)
        box = SurroundingRectangle(r, color=KEY, buff=0.12, corner_radius=0.1)
        return box, [Create(box), r[1].animate.set_color(KEY)]


def meaning_circles(words, centres, radii, colors, label_size=LABEL):
    """Each word's meaning as a translucent circle with its label inside."""
    out = VGroup()
    for w, c, r, col in zip(words, centres, radii, colors):
        circ = Circle(radius=r, color=col, stroke_width=3, fill_color=col, fill_opacity=0.15).move_to(c)
        out.add(VGroup(circ, text(w, label_size, col, BOLD).move_to(c)))
    return out


def pair_chip(a, b, color, note=None, size=LABEL):
    """'a ≈ b' chip, optionally with a small note underneath."""
    chip = pill(f"{a}  ≈  {b}", color, size=size)
    if note:
        return VGroup(chip, text(note, SMALL, MUTED)).arrange(DOWN, buff=0.12)
    return chip


# ============================================================ the cast ====
# Three roles, three voices.  No role name is ever spoken: the lit ring on a
# drawn character shows who is talking (teacher top left, student top right);
# while the narrator speaks, both characters listen.

NARRATOR_VOICE = "vijay"
TEACHER_VOICE = "aditya"
STUDENT_VOICE = "kavya"
TURN_PAUSE = 0.6               # silence when the speaker changes (seconds), so voices never run together

SKIN = "#F2D0B0"               # characters use neutral tones, not the text colours
HAIR = "#2A2F3C"
LIPS = "#3A1F1F"
SHIRT_T = "#2E5E86"
SHIRT_S = "#8A6D1F"
RING_ON = "#FFD54F"


class Face(VGroup):
    """A drawn character: head, hair, eyes, brows, mouth and shoulders.

    ``look(name)`` sets the expression at once; ``look_to(name)`` returns the
    animations for a change on screen; ``talk(on)`` lights the speaking ring."""

    LOOKS = {"neutral": ("soft", "flat"), "smile": ("smile", "flat"), "happy": ("open", "up"),
             "ask": ("small", "one_up"), "think": ("flat", "down"), "confused": ("wavy", "tilt"),
             "surprised": ("o", "up"), "oops": ("frown", "tilt")}

    def __init__(self, r=0.34, kind="teacher", look="neutral"):
        super().__init__()
        self.r, self.kind = r, kind
        shirt = SHIRT_T if kind == "teacher" else SHIRT_S
        self.head = Circle(radius=r, stroke_color="#B89A7C", stroke_width=2, fill_color=SKIN, fill_opacity=1)
        self.body = Arc(radius=r * 1.3, start_angle=0, angle=PI, stroke_color=shirt, stroke_width=2,
                        fill_color=shirt, fill_opacity=1)
        self.body.next_to(self.head, DOWN, buff=-r * 0.3)
        self.ring = Circle(radius=r * 1.2, stroke_color=MUTED, stroke_width=3)
        hair = Arc(radius=r, start_angle=PI * 0.1, angle=PI * 0.8, stroke_width=0, fill_color=HAIR, fill_opacity=1)
        extras = VGroup(hair)
        if kind == "teacher":           # short hair and glasses
            for sx in (-1, 1):
                extras.add(Circle(radius=r * 0.2, stroke_color=HAIR, stroke_width=2).move_to(self.at(sx * 0.34, 0.06)))
            extras.add(Line(self.at(-0.14, 0.06), self.at(0.14, 0.06), stroke_color=HAIR, stroke_width=2))
        else:                           # a ponytail
            extras.add(Ellipse(width=r * 0.5, height=r * 0.95, stroke_width=0, fill_color=HAIR,
                               fill_opacity=1).move_to(self.at(0.95, 0.35)))
        self.eyes = VGroup(*[Dot(self.at(sx * 0.34, 0.06), radius=r * 0.085, color=HAIR) for sx in (-1, 1)])
        self.mouth = self._mouth("soft")
        self.brow_l, self.brow_r = self._brows("flat")
        self.add(self.body, self.ring, self.head, extras, self.eyes, self.brow_l, self.brow_r, self.mouth)
        self.look(look)

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

    def look(self, name):
        mouth, brows = self.LOOKS[name]
        left, right = self._brows(brows)
        self.mouth.become(self._mouth(mouth))
        self.brow_l.become(left)
        self.brow_r.become(right)
        self.now = name
        return self

    def look_to(self, name):
        if getattr(self, "now", None) == name:
            return []
        mouth, brows = self.LOOKS[name]
        left, right = self._brows(brows)
        self.now = name
        return [self.mouth.animate.become(self._mouth(mouth)), self.brow_l.animate.become(left),
                self.brow_r.animate.become(right)]

    def talk(self, on):
        return self.ring.animate.set_stroke(RING_ON if on else MUTED, width=6 if on else 3)

# ============================================================= lesson ====

class Family:
    """A family used to check the answers: genders, sibling groups, parents and marriages.

    Exam conventions are built in: brothers and sisters share both parents, and a married
    person's child is also the spouse's child (no step-relations)."""

    WORDS = {"spouse": ("husband", "wife"), "parent": ("father", "mother"), "child": ("son", "daughter"),
             "sibling": ("brother", "sister"), "grandparent": ("grandfather", "grandmother"),
             "grandchild": ("grandson", "granddaughter"), "uncle_aunt": ("uncle", "aunt"),
             "nephew_niece": ("nephew", "niece"), "cousin": ("cousin", "cousin"),
             "child_in_law": ("son-in-law", "daughter-in-law"), "parent_in_law": ("father-in-law", "mother-in-law"),
             "sibling_in_law": ("brother-in-law", "sister-in-law")}

    def __init__(self, facts=""):
        self.sex, self.group, self.parents, self.spouse = {}, {}, {}, {}
        self.tell(facts)

    def add(self, name, sex=None):
        if name not in self.group:
            self.group[name], self.parents[name], self.sex[name] = name, set(), None
        if sex:
            assert self.sex[name] in (None, sex), f"{name} cannot be both genders"
            self.sex[name] = sex
        return name

    def find(self, name):
        while self.group[name] != name:
            name = self.group[name]
        return name

    def merge(self, a, b):
        a, b = self.find(a), self.find(b)
        if a != b:
            self.group[b] = a
            self.parents[a] |= self.parents.pop(b)

    def kids_group(self, parent):
        for root, people in self.parents.items():
            if parent in people:
                return root
        return None

    def siblings(self, a, b, sex=None):
        self.add(a, sex)
        self.add(b)
        self.merge(a, b)

    def child(self, kid, parent, sex=None):
        self.add(kid, sex)
        self.add(parent)
        for p in (parent, self.spouse.get(parent)):
            root = self.kids_group(p) if p else None
            if root is not None:
                self.merge(root, kid)
        root = self.find(kid)
        self.parents[root].add(parent)
        if parent in self.spouse:
            self.parents[root].add(self.spouse[parent])

    def couple(self, husband, wife):
        self.add(husband, "m")
        self.add(wife, "f")
        self.spouse[husband], self.spouse[wife] = wife, husband
        roots = [r for r in (self.kids_group(husband), self.kids_group(wife)) if r is not None]
        if len(roots) == 2:
            self.merge(roots[0], roots[1])
        if roots:
            self.parents[self.find(roots[0])] |= {husband, wife}

    def tell(self, facts):
        """Facts as 'X rel Y' ("X is the rel of Y"), separated by semicolons."""
        for fact in filter(None, (f.strip() for f in facts.split(";"))):
            x, rel, y = fact.split()
            if rel in ("father", "mother"):
                self.child(y, x)
                self.add(x, "m" if rel == "father" else "f")
            elif rel in ("son", "daughter", "child"):
                self.child(x, y, {"son": "m", "daughter": "f"}.get(rel))
            elif rel in ("brother", "sister", "sibling"):
                self.siblings(x, y, {"brother": "m", "sister": "f"}.get(rel))
            elif rel == "husband":
                self.couple(x, y)
            elif rel == "wife":
                self.couple(y, x)
            elif rel in ("male", "female"):
                self.add(x, rel[0])
            else:
                raise ValueError(fact)
        return self

    def par(self, x):
        return set(self.parents[self.find(x)])

    def sib(self, x):
        root = self.find(x)
        return {p for p in self.group if p != x and self.find(p) == root}

    def kids(self, x):
        return {p for p in self.group if x in self.parents[self.find(p)]}

    def wed(self, x):
        return {self.spouse[x]} if x in self.spouse else set()

    @staticmethod
    def over(step, people):
        out = set()
        for p in people:
            out |= step(p)
        return out

    def kind(self, x, y):
        """What X is to Y, without the gender (None if the facts do not link them)."""
        over, par, sib, kids, wed = self.over, self.par, self.sib, self.kids, self.wed
        parent_sibs = over(sib, par(y))
        tests = [("spouse", wed(y)), ("parent", par(y)), ("child", kids(y)), ("sibling", sib(y)),
                 ("grandparent", over(par, par(y))), ("grandchild", over(kids, kids(y))),
                 ("uncle_aunt", parent_sibs | over(wed, parent_sibs)),
                 ("nephew_niece", over(kids, sib(y)) | over(kids, over(sib, wed(y)))),
                 ("cousin", over(kids, parent_sibs)), ("child_in_law", over(wed, kids(y))),
                 ("parent_in_law", over(par, wed(y))), ("sibling_in_law", over(sib, wed(y)) | over(wed, sib(y)))]
        for name, people in tests:
            if x in people:
                return name
        return None

    def word(self, x, y):
        """The standard word for "X is Y's ___" (None when it cannot be determined)."""
        kind = self.kind(x, y)
        if kind is None:
            return None
        if kind == "cousin":
            return "cousin"
        return None if self.sex[x] is None else self.WORDS[kind]["mf".index(self.sex[x])]

    def side(self, x, y):
        """"paternal" or "maternal": the parent of Y through whom X is related."""
        for p in self.par(y):
            if x in self.par(p) | self.sib(p) | self.over(self.wed, self.sib(p)) | self.over(self.kids, self.sib(p)):
                return "paternal" if self.sex[p] == "m" else "maternal"
        return None

    def gap(self, x, y):
        """Rows from Y up to X (+1 = X is one generation above Y)."""
        return {"spouse": 0, "sibling": 0, "cousin": 0, "sibling_in_law": 0, "parent": 1, "uncle_aunt": 1, "parent_in_law": 1,
                "child": -1, "nephew_niece": -1, "child_in_law": -1, "grandparent": 2, "grandchild": -2}[self.kind(x, y)]


def rel(facts, x, y):
    """Shortcut: the word for "X is Y's ___" in the family described by ``facts``."""
    return Family(facts).word(x, y)

# ---- hook, worked examples, traps, checkpoint ----
assert rel("P brother Q; Q daughter R; R wife S", "P", "S") == "son"
assert rel("A sister B; B son C; C brother D", "A", "D") == "niece"
assert rel("R father Q; P son Q", "R", "P") == "grandfather" and rel("R father Q; P son Q", "P", "R") == "grandson"
assert rel("A son B; B sister C; C father D", "A", "D") == "cousin"
assert rel("M wife N; N father O; O brother P", "M", "P") == "mother"
# ---- exam patterns ----
for facts_, x_, y_, word_ in [("A brother B; B son C", "A", "C", "son"), ("P wife Q; Q father R", "P", "R", "mother"),
                              ("K daughter L; L sister M", "K", "M", "niece"), ("X father Y; Y father Z", "X", "Z", "grandfather"),
                              ("D husband E; E sister F", "D", "F", "brother-in-law"), ("G son H; H husband J", "J", "G", "mother")]:      # J, not I: "I" is heard as the pronoun
    assert rel(facts_, x_, y_) == word_, facts_
# ---- practice ----
for facts_, x_, y_, word_ in [("X sister Y; Y son Z", "X", "Z", "daughter"), ("P husband Q; Q mother R", "P", "R", "father"),
                              ("D daughter E; E daughter F", "D", "F", "granddaughter"), ("A wife B; B brother C", "A", "C", "sister-in-law"),
                              ("K son L; L brother M; M mother N", "K", "N", "cousin"),
                              ("R father S; S sister T; T husband V", "R", "V", "father-in-law"),     # V, not U: "U" is heard as "you"
                              ("A brother B; B wife C; C father D; D sister E", "A", "E", "uncle"),
                              ("P mother Q; Q husband R; R mother S; S brother T", "P", "T", "grandmother")]:
    assert rel(facts_, x_, y_) == word_, facts_
assert Family("A brother B; B wife C; C father D; D sister E").side("A", "E") == "maternal"
LAST = Family("P mother Q; Q husband R; R mother S; S brother T")
assert (LAST.side("P", "T"), LAST.gap("P", "T")) == ("paternal", 2)
# ---- section quiz ----
assert rel("A daughter B; B wife C; C brother D", "A", "D") == "niece" and rel("P father Q; Q wife R", "P", "R") == "father-in-law"
assert rel("X brother Y; Y son Z; Z wife W", "W", "X") == "father"
FOUR = Family("M son N; N daughter O; O husband P")
assert (FOUR.word("P", "M"), FOUR.side("P", "M")) == ("grandmother", "maternal")
FIVE = Family("E brother F; F mother G; G sister H")
assert (FIVE.word("E", "H"), FIVE.side("E", "H")) == ("uncle", "maternal")

OBJECTIVES = [("Trace a chain of statements", "one link at a time, on a family tree"),
              ("Read “How is X related to Y?”", "as “X is Y's ___”, and answer from Y's side"),
              ("Count generations", "to confirm the answer word")]
STEPS = [("One link at a time", "draw each statement before reading the next"),
         ("Join at the common person", "two statements meet at the person they share"),
         ("Siblings share parents", "a brother of B is a son of B's parents")]
MORE = [("Read the question from the end", "“X is Y's ___”:  start at Y, walk to X"),
        ("Count generations as you walk", "parent +1,  child −1,  sibling or spouse 0"),
        ("Only X's gender decides the word", "Y's gender never matters")]
FORMULAS = ["Draw one link at a time;   join statements at the common person",
            "Siblings share parents",
            "“How is X related to Y?”  =  “X is Y's ___”:   start at Y, walk to X",
            "Generation count:   parent +1  ·  child −1  ·  sibling or spouse 0",
            "The word needs X's gender only"]
PATTERNS_A = [["A is the brother of B;  B is the son of C", "A to C", "C → son B → brother A", "Son"],
              ["P is the wife of Q;  Q is the father of R", "P to R", "R → father Q → wife P", "Mother"],
              ["K is the daughter of L;  L is the sister of M", "K to M", "M → sister L → daughter K", "Niece"]]
PATTERNS_B = [["X is the father of Y;  Y is the father of Z", "X to Z", "Z → father Y → father X", "Grandfather"],
              ["D is the husband of E;  E is the sister of F", "D to F", "F → sister E → husband D", "Brother-in-law"],
              ["G is the son of H;  H is the husband of J", "J to G", "G → father H → wife J", "Mother"]]
TRAPS = [("Trap 1  ·  answering in the wrong direction", "R is the father of Q.  P is the son of Q.  How is R related to P?",
          "“Grandson”:  P seen from R's side", "Start at P:  father Q, his father R.  Grandfather",
          "“How is X related to Y?” describes X:  start the walk at Y"),
         ("Trap 2  ·  merging siblings into a couple", "A is the son of B.  B is the sister of C.  C is the father of D.  A to D?",
          "“Brother”:  as if B and C were a couple", "B and C are siblings:  their children are cousins",
          "A sibling line is not a marriage;  children of siblings are cousins")]
PRACTICE_A = [("L1", "X is the sister of Y.  Y is the son of Z.  How is X related to Z?"),
              ("L1", "P is the husband of Q.  Q is the mother of R.  How is P related to R?"),
              ("L1", "D is the daughter of E.  E is the daughter of F.  How is D related to F?"),
              ("L2", "A is the wife of B.  B is the brother of C.  How is A related to C?"),
              ("L2", "K is the son of L.  L is the brother of M.  M is the mother of N.  How is K related to N?"),
              ("L2", "R is the father of S.  S is the sister of T.  T is the husband of V.  How is R related to V?")]
PRACTICE_B = [("L3", "A is the brother of B.  B is the wife of C.  C is the father of D.  D is the sister of E.  A to E?"),
              ("L3", "P is the mother of Q.  Q is the husband of R.  R is the mother of S.  S is the brother of T.  P to T, and how many generations apart?")]
ANSWERS_A = [("A sibling of Z's son, female, one row down", "Daughter"), ("Q's husband, and R is Q's child", "Father"),
             ("Two rows down, female", "Granddaughter"), ("The wife of C's brother", "Sister-in-law")]
ANSWERS_B = [("K's father L and N's mother M are siblings", "Cousin"), ("V's husband T is R's son", "Father-in-law"),
             ("B is the mother of D and E, and A is B's brother", "Maternal uncle"),
             ("P is the mother of T's father Q:  two generations up", "Paternal grandmother")]
LENS = [("Recognition cue", "two to four statements “A is the ___ of B”, then “How is X related to Y?”"),
        ("Target time", "30 seconds"),
        ("Sanity check", "the generation count of the walk must match the word, and the word must fit X's gender")]
QUIZ = [["A is the daughter of B.  B is the wife of C.  C is the brother of D.  A to D?", "(a) Daughter\n(b) Niece\n(c) Sister\n(d) Cousin"],
        ["P is the father of Q.  Q is the wife of R.  How is P related to R?", "(a) Father\n(b) Brother-in-law\n(c) Father-in-law\n(d) Uncle"],
        ["X is the brother of Y.  Y is the son of Z.  Z is the wife of W.  W to X?", "(a) Father\n(b) Uncle\n(c) Grandfather\n(d) Son"],
        ["M is the son of N.  N is the daughter of O.  O is the husband of P.  P to M?",
         "(a) Paternal grandmother\n(b) Mother\n(c) Aunt\n(d) Maternal grandmother"],
        ["E is the brother of F.  F is the mother of G.  G is the sister of H.  E to H?",
         "(a) Maternal uncle\n(b) Paternal uncle\n(c) Brother\n(d) Father"]]
QUIZ_KEY = [("D → brother C → daughter A", "(b)"), ("R → wife Q → father P", "(c)"), ("Z is W's wife, so X is W's son", "(a)"),
            ("M → mother N → mother P", "(d)"), ("H → mother F → brother E", "(a)")]


def two_line_blocks(items, color, detail_size=SMALL):
    """Numbered blocks: a bold title line with a detail line under it.  block[0] = title line, block[1] = detail line."""
    blocks = VGroup()
    for i, (title, detail) in enumerate(items):
        top = VGroup(pill(str(i + 1), color, size=SMALL), text(title, LABEL, color, BOLD)).arrange(RIGHT, buff=0.3)
        indent = Rectangle(width=0.75, height=0.1).set_stroke(width=0)                    # never shown
        blocks.add(VGroup(top, VGroup(indent, text(detail, detail_size, INK)).arrange(RIGHT, buff=0))
                   .arrange(DOWN, buff=0.16, aligned_edge=LEFT))
    return blocks.arrange(DOWN, buff=0.5, aligned_edge=LEFT)


def given_chips(p, r, t):
    return VGroup(pill(f"P = {p}", "#4FC3F7", size=LABEL), pill(f"R = {r}", "#FFB74D", size=LABEL),
                  pill(f"T = {t}", "#CE93D8", size=LABEL)).arrange(RIGHT, buff=0.35)


class DirectRelationChainsVideo(LMSScene):
    lesson_title = "Direct Relation Chains"

    def construct(self):
        self.camera.background_color = BG

        self.intro()
        self.hook()
        self.objectives()
        self.why_this_section()
        self.concept_journey()
        self.rule_box()
        self.short_trick()
        self.analogy()
        self.hook_solved()
        self.second_example()
        self.exam_patterns()
        self.traps()
        self.checkpoint()
        self.practice()
        self.answers()
        self.exam_lens()
        self.summary()
        self.section_quiz()

    # ---------------------------------------------------- scene helpers --

    def clear_stage(self, run_time=0.6):
        """Scene transition: fade out everything on screen."""
        if self.mobjects:
            self.play(FadeOut(Group(*self.mobjects)), run_time=run_time)

    def card(self, content, width=None, height=None, color=MUTED, pad=0.3):
        """Container-aware card (grows to content; a fixed height is a minimum)."""
        # A fixed height is a minimum: the card grows to its content and never
        # shrinks text (shrinking pushed labels below the readable minimum).
        if width is not None:
            fit_width(content, width - 2 * pad)
        w = width if width is not None else content.width + 2 * pad
        h = max(height or 0, content.height + 2 * pad)
        box = RoundedRectangle(corner_radius=0.18, width=w, height=h, stroke_color=color,
                               stroke_width=2.5, fill_color=PANEL, fill_opacity=1)
        box.move_to(content)
        self.validator.check_fit(content, box, margin=0.1)
        return VGroup(box, content)

    def caption(self, s, color=INK):
        """One-line keyword caption in a fixed-width bar at the bottom of the frame."""
        t = fitted_text(s, SAFE_W - 1.0, BODY, color)
        bar = self.card(t, width=SAFE_W - 0.4, height=t.height + 0.9)
        return bar.move_to(UP * BOTTOM_Y)

    def breadcrumb(self, *parts):
        """Silent 'where are we' trail: Module > Lesson > Topic."""
        colors = [DIFF, MUTED, RATIO]
        items = []
        for i, p in enumerate(parts):
            if i:
                items.append(text("›", LABEL, MUTED))
            items.append(pill(p, colors[i % 3], size=SMALL))
        return fit_width(VGroup(*items).arrange(RIGHT, buff=0.25), SAFE_W)

    def verdict_card(self, good, s, width):
        """A ✓ (green) or ✗ (red) card with fitted text."""
        color = GOOD if good else BAD
        body = VGroup(text("✓" if good else "✗", 34, color, BOLD),
                      fitted_text(s, width - 1.3, SMALL, color, max_lines=2)).arrange(RIGHT, buff=0.25)
        return self.card(body, width=width, height=1.2, color=color)

    def countdown(self, seconds):
        """Thinking-time ring that empties over ``seconds`` (for pause_after)."""
        centre = RIGHT * (FRAME_W / 2 - SAFE - 0.5) + DOWN * (FRAME_H / 2 - SAFE - 0.5)
        tracker = ValueTracker(1.0)
        track = Circle(radius=0.38, stroke_color=MUTED, stroke_width=3).move_to(centre)
        ring = always_redraw(lambda: Arc(radius=0.38, start_angle=PI / 2, angle=max(TAU * tracker.get_value(), 1e-3),
                                         arc_center=centre, stroke_color=FOCUS, stroke_width=8))
        label = pill("Think", FOCUS).next_to(track, LEFT, buff=0.3)
        self.play(FadeIn(track), FadeIn(label), run_time=0.3)
        self.add(ring)
        self.play(tracker.animate.set_value(0.0), run_time=max(0.5, seconds - 0.3), rate_func=linear)
        self.remove(ring)
        self.play(FadeOut(track), FadeOut(label), run_time=0.3)

    def table_rows(self, header, rows, widths, size=SMALL):
        """A small table as a VGroup of rows (header first). Each cell is fitted
        to its column and left-aligned at the column's left edge."""
        lefts, x = [], -sum(widths) / 2
        for w in widths:
            lefts.append(x)
            x += w
        out = VGroup()
        for i, cells in enumerate([header] + rows):
            color, weight = (FOCUS, BOLD) if i == 0 else (INK, NORMAL)
            row = VGroup(*[fitted_text(c, w - 0.3, size, color, weight, max_lines=2) for c, w in zip(cells, widths)])
            for cell, left in zip(row, lefts):
                cell.set_x(left + cell.width / 2)
            out.add(row)
        out.arrange(DOWN, buff=0.3)
        for row in out:                      # arrange() recentres rows; restore column alignment
            for cell, left in zip(row, lefts):
                cell.set_x(left + cell.width / 2)
        return out

    def recap_card(self, title, rows):
        """'Recap Card': term on the left, one-line meaning on the right."""
        table = self.table_rows([title, "what it means"], rows, [3.4, 8.0], size=LABEL)
        table[0][0].set_color(INK)
        card = self.card(table, width=SAFE_W - 0.4)
        return card, table

    def no_overlap(self, *mobs, gap=0.05):
        """Layout guard: the bounding boxes of the given blocks must not intersect
        (checked before anything is played, so a layout change can't silently overlap)."""
        for i, a in enumerate(mobs):
            for b in mobs[i + 1:]:
                apart_x = a.get_right()[0] + gap <= b.get_left()[0] or b.get_right()[0] + gap <= a.get_left()[0]
                apart_y = a.get_bottom()[1] >= b.get_top()[1] + gap or b.get_bottom()[1] >= a.get_top()[1] + gap
                if not (apart_x or apart_y):
                    raise ValueError(f"overlapping blocks: {a.__class__.__name__} at {a.get_center()} and "
                                     f"{b.__class__.__name__} at {b.get_center()}")

    # ----------------------------------------------------- pinned panel --
    PIN_W = 3.4                                   # width of the pinned reference panel

    def pin(self, card, corner=UR):
        """Animation: park a reference card in a corner. It stays on screen across scenes
        (``clear_stage`` leaves it) until ``unpin``."""
        fit_within(card, self.PIN_W, SAFE_H - 1.0)
        card.to_corner(corner, buff=SAFE)
        self.pinned = card
        return FadeIn(card, shift=LEFT * 0.2)

    def unpin(self):
        card, self.pinned = getattr(self, "pinned", None), None
        return FadeOut(card) if card is not None else Wait(0.01)

    def free_area(self):
        """(centre_x, width) of the stage left free by the pinned panel (full safe width if none)."""
        card = getattr(self, "pinned", None)
        left = -FRAME_W / 2 + SAFE
        right = (card.get_left()[0] - 0.3) if card is not None else FRAME_W / 2 - SAFE
        return (left + right) / 2, right - left

    def place_free(self, mob, y=None):
        """Fit ``mob`` into the free area (beside the pinned panel) and centre it there."""
        cx, w = self.free_area()
        fit_width(mob, w)
        mob.set_x(cx)
        if y is not None:
            mob.set_y(y)
        if getattr(self, "pinned", None) is not None:
            self.no_overlap(mob, self.pinned)
        return mob

    def clear_stage(self, run_time=0.6):
        """Scene transition: fade out everything except the pinned panel."""
        keep = getattr(self, "pinned", None)
        mobs = [m for m in self.mobjects if m is not keep]
        if mobs:
            self.play(FadeOut(Group(*mobs)), run_time=run_time)

    def steps_pin(self, title, steps):
        """A compact numbered-steps card for the pinned panel. ``steps`` = [(text, colour), ...]."""
        rows = VGroup(*[VGroup(pill(str(i + 1), c, size=SMALL), text(t, SMALL, INK)).arrange(RIGHT, buff=0.2)
                        for i, (t, c) in enumerate(steps)]).arrange(DOWN, buff=0.18, aligned_edge=LEFT)
        return self.card(VGroup(text(title, SMALL, MUTED, BOLD), rows).arrange(DOWN, buff=0.2, aligned_edge=LEFT),
                         color=FOCUS)

    def pin_step(self, i, color=FOCUS):
        """Animation: light up row i of the pinned steps card."""
        return Indicate(self.pinned[1][1][i], color=color, scale_factor=1.08)

    def heading(self, s, color=FOCUS):
        head = pill(s, color, size=LABEL)
        return head.move_to(UP * (CARD_TOP - head.height / 2))

    def stack(self, head, items, buff=0.45, top=0.5, align=None):
        """Stack ``items`` under ``head`` (fitted to the frame, guarded against overlap).  Returns the group."""
        body = VGroup(*items)
        if align is None:
            body.arrange(DOWN, buff=buff)
        else:
            body.arrange(DOWN, buff=buff, aligned_edge=align)
        fit_within(body, SAFE_W, SAFE_H - head.height - top - 0.3)
        body.next_to(head, DOWN, buff=top)
        self.no_overlap(head, *items)
        self.validator.check_in_frame(VGroup(head, body))
        return body

    def placed_table(self, head, header, rows, widths, size=SMALL, room=0.8):
        """A table fitted under ``head``.  Returns (table, body rows)."""
        table = self.table_rows(header, rows, widths, size=size)
        fit_within(table, SAFE_W, SAFE_H - head.height - room)
        table.next_to(head, DOWN, buff=0.45)
        self.no_overlap(head, table)
        self.no_overlap(*table)
        self.validator.check_in_frame(VGroup(head, table))
        return table, table[1:]

    def verdict_pair(self, wrong, right):
        """A ✗ card and a ✓ card of the same height, side by side."""
        contents = [VGroup(text(mark, 34, c, BOLD), text(s, LABEL, c)).arrange(RIGHT, buff=0.25)
                    for mark, s, c in [("✗", wrong, BAD), ("✓", right, GOOD)]]
        tallest = max(c.height for c in contents) + 0.6
        return VGroup(*[self.card(c, width=6.2, height=tallest, color=col) for c, col in zip(contents, (BAD, GOOD))])\
            .arrange(RIGHT, buff=0.5)

    def show_trap(self, trap):
        """Lay out one trap.  Returns (head, question, wrong card, right card, rule)."""
        title, question, wrong, right, rule = trap
        head = self.heading(title, BAD)
        q = fitted_text(question, SAFE_W - 1.0, BODY, INK, NORMAL, max_lines=2)
        pair = self.verdict_pair(wrong, right)
        rule_pill = fit_width(pill(rule, FOCUS, size=LABEL), SAFE_W)
        self.stack(head, [q, pair, rule_pill], buff=0.7, top=0.8)
        self.no_overlap(pair[0], pair[1])
        return head, q, pair[0], pair[1], rule_pill

    def solve_steps(self, steps, color=WORD):
        """Numbered solution rows.  Each row = (number chip, working, result)."""
        rows = VGroup(*[VGroup(pill(str(i + 1), color, size=SMALL), text(what, LABEL, INK), text(result, LABEL, GOOD, BOLD))
                        .arrange(RIGHT, buff=0.3) for i, (what, result) in enumerate(steps)])
        return rows.arrange(DOWN, buff=0.5, aligned_edge=LEFT)

    def pattern_table(self, head, patterns):
        table, rows = self.placed_table(head, ["Pattern", "Example", "Method", "Answer"], [list(p) for p in patterns],
                                        [2.6, 4.6, 4.2, 1.8], room=1.2)
        for row in rows:
            row[0].set_color(WORD)
            row[3].set_color(GOOD)
        return table, rows

    def practice_table(self, head, questions, first):
        table, rows = self.placed_table(head, ["Level", "Question"],
                                        [[f"{level}  ·  {first + i}", q] for i, (level, q) in enumerate(questions)],
                                        [1.6, 11.0], room=1.3)
        level_cols = {"L1": WORD, "L2": WORD, "L3": WORD}
        for row, (level, _) in zip(rows, questions):
            row[0].set_color(level_cols[level])
        return table, rows

    def answer_table(self, head, answers, first):
        table, rows = self.placed_table(head, ["#", "Reasoning", "Answer"],
                                        [[str(first + i), how, ans] for i, (how, ans) in enumerate(answers)], [0.8, 8.6, 3.6])
        for row in rows:
            row[0].set_color(MUTED)
            row[2].set_color(GOOD)
        return table, rows

    # ------------------------------------------------------------ the cast --

    def speaker(self, who, look=None):
        """Show who is speaking: "N" narrator (both characters listen), "T" teacher, "S" student.

        The two characters walk in the first time one of them speaks and stay on screen
        (``clear_stage`` leaves them); ``look`` is the speaker's expression."""
        cast = getattr(self, "cast", None)
        if cast is None:
            if who == "N":
                return
            t, s = Face(0.34, "teacher", "neutral"), Face(0.34, "student", "neutral")
            top, side = FRAME_H / 2 - SAFE, FRAME_W / 2 - SAFE
            t.shift(UP * (top - t.get_top()[1]) + RIGHT * (-side - t.get_left()[0]))
            s.shift(UP * (top - s.get_top()[1]) + RIGHT * (side - s.get_right()[0]))
            self.cast, self.teacher_face, self.student_face = VGroup(t, s), t, s
            self.cast_clear()
            self.play(FadeIn(t, shift=RIGHT * 0.4), FadeIn(s, shift=LEFT * 0.4), run_time=0.5)
        if getattr(self, "speaking", None) == (who, look):
            return
        self.speaking = (who, look)
        t, s = self.teacher_face, self.student_face
        self.cast_clear()
        self.play(*t.look_to((look or "smile") if who == "T" else "neutral"), t.talk(who == "T"),
                  *s.look_to((look or "smile") if who == "S" else "neutral"), s.talk(who == "S"), run_time=0.25)

    def cast_clear(self):
        """Layout guard: nothing on screen may reach into a character's corner."""
        own = set(self.cast.get_family())
        for face, name in ((self.teacher_face, "teacher"), (self.student_face, "student")):
            l, r, b = face.get_left()[0] - 0.08, face.get_right()[0] + 0.08, face.get_bottom()[1] - 0.08
            for top in self.mobjects:
                for part in top.family_members_with_points():
                    if part in own:
                        continue
                    if part.get_right()[0] > l and part.get_left()[0] < r and part.get_top()[1] > b:
                        raise ValueError(f"{part!r} reaches into the {name}'s corner; keep the top corners free.")

    def clear_stage(self, run_time=0.6):
        """Scene transition: fade out everything except the pinned panel and the two characters."""
        keep = set()
        for kept in (getattr(self, "pinned", None), getattr(self, "cast", None)):
            if kept is not None:
                keep.update(kept.get_family())
        mobs = [m for m in self.mobjects
                if m not in keep and any(p not in keep for p in m.family_members_with_points())]
        if mobs:
            self.play(FadeOut(Group(*mobs)), run_time=run_time)

    def curtain(self):
        """The end of the video: the characters leave with everything else."""
        self.cast = None
        if self.mobjects:
            self.play(FadeOut(Group(*self.mobjects)), run_time=1.0)

    def table_under(self, head, ref, header, rows, widths, size=SMALL):
        """A reference block under ``head`` and a table under it, fitted to the space that is left.  Returns (table, body rows)."""
        fit_width(ref, SAFE_W)
        ref.next_to(head, DOWN, buff=0.35)
        table = self.table_rows(header, rows, widths, size=size)
        fit_within(table, SAFE_W, ref.get_bottom()[1] + FRAME_H / 2 - SAFE - 1.2)
        table.next_to(ref, DOWN, buff=0.4)
        self.no_overlap(head, ref, table)
        self.no_overlap(*table)
        self.validator.check_in_frame(VGroup(head, ref, table))
        return table, table[1:]
    def step_rows(self, items, color=WORD):
        """Numbered concept steps.  Each row = (number chip, the step[, a short note in green])."""
        rows = VGroup()
        for i, (what, note) in enumerate(items):
            row = VGroup(pill(str(i + 1), color, size=SMALL), text(what, LABEL, INK, BOLD))
            if note:
                row.add(text(note, LABEL, GOOD, BOLD))
            rows.add(row.arrange(RIGHT, buff=0.35))
        return fit_width(rows.arrange(DOWN, buff=0.5, aligned_edge=LEFT), SAFE_W - 0.6)

    def tree(self, people, couples=(), kids=(), sibs=(), dx=1.9, dy=1.25, size=LABEL):
        """A family tree in the standard notation.

        people  {name: (column, row, sign)} with sign "+", "−" or "" (gender not known); row 0 is the top row
        couples [(a, b)]            a double line (=) between a married couple
        kids    [(parents, [children])] with parents = (a, b) or (a,): a vertical line down to the children
        sibs    [(a, b)]            a horizontal line joining siblings whose parents are not drawn
        Returns a VGroup with .node[name], .wed[(a, b)], .down[i] and .sib[(a, b)] for the cues."""
        tones = {"+": WORD, "−": FOCUS, "": MUTED}
        g = VGroup()
        g.node, g.wed, g.down, g.sib = {}, {}, [], {}
        for name, (col, row, sign) in people.items():
            label = text(f"{name} ({sign})" if sign else name, size, tones[sign], BOLD)
            box = RoundedRectangle(corner_radius=0.14, width=max(label.width + 0.4, 1.0), height=0.62, stroke_color=tones[sign],
                                   stroke_width=2.5, fill_color=PANEL, fill_opacity=1)
            node = VGroup(box, label.move_to(box)).move_to(RIGHT * col * dx + DOWN * row * dy)
            g.node[name] = node
            g.add(node)
        for a, b in couples:
            left, right = sorted((g.node[a], g.node[b]), key=lambda m: m.get_x())
            mark = VGroup(*[Line(left.get_right(), right.get_left(), stroke_color=INK, stroke_width=3).shift(UP * s)
                            for s in (0.06, -0.06)])
            g.wed[(a, b)] = mark
            g.add(mark)
        for a, b in sibs:
            left, right = sorted((g.node[a], g.node[b]), key=lambda m: m.get_x())
            mark = Line(left.get_right(), right.get_left(), stroke_color=MUTED, stroke_width=3)
            g.sib[(a, b)] = mark
            g.add(mark)
        for parents, children in kids:
            key = tuple(parents)
            if len(key) == 2:
                wed = g.wed.get(key) or g.wed.get(key[::-1])
                start = wed.get_center() + DOWN * 0.06
            else:
                start = g.node[key[0]].get_bottom()
            tops = [g.node[k].get_top() for k in children]
            bar = (start[1] + max(t[1] for t in tops)) / 2
            lines = VGroup(Line(start, [start[0], bar, 0]))
            xs = [t[0] for t in tops] + [start[0]]
            if max(xs) - min(xs) > 1e-3:
                lines.add(Line([min(xs), bar, 0], [max(xs), bar, 0]))
            for t in tops:
                lines.add(Line([t[0], bar, 0], t))
            lines.set_stroke(MUTED, 3)
            g.down.append(lines)
            g.add(lines)
        return g

    def row_tags(self, tree, tags, size=SMALL):
        """Generation labels (+1, 0, −1 ...) to the left of a tree.  tags = {a person on that row: label}."""
        left = tree.get_left()[0] - 0.55
        return VGroup(*[text(label, size, MUTED, BOLD).move_to([left, tree.node[name].get_y(), 0]) for name, label in tags.items()])

    def lines_block(self, items, color=None, size=LABEL):
        """Left-aligned lines of text.  items = strings, or (string, colour)."""
        rows = VGroup()
        for item in items:
            s, c = (item, color or INK) if isinstance(item, str) else item
            rows.add(text(s, size, c, BOLD))
        return rows.arrange(DOWN, buff=0.32, aligned_edge=LEFT)

    def steps_list(self, items, color=None):
        """Numbered steps: (step text, result in green or None)."""
        rows = VGroup()
        for i, (what, result) in enumerate(items):
            row = VGroup(pill(str(i + 1), color or WORD, size=SMALL), text(what, SMALL, INK, BOLD))
            if result:
                row.add(text(result, SMALL, GOOD, BOLD))
            rows.add(row.arrange(RIGHT, buff=0.3))
        return rows.arrange(DOWN, buff=0.36, aligned_edge=LEFT)

    # ============================================== 0. INTRO ==========
    # Not the first video: silent breadcrumb, a one-line recap of the previous video, then today's topic.

    def intro(self):
        self.scene_start("S00_intro", title="Intro")

        crumb = self.breadcrumb("Logical Reasoning", "Lesson 10 · Blood Relation I", "Video 2 of 5")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        recap = VGroup(text("From video 1", SMALL, MUTED), pill("Row gap + sign = the standard word", WORD, size=LABEL)).arrange(DOWN, buff=0.25)
        title = fit_width(text("Direct Relation Chains", TITLE, INK, BOLD), SAFE_W - 0.4)
        today = text("Today: walking a chain, one link at a time", LABEL, FOCUS)
        block = VGroup(recap, title, today).arrange(DOWN, buff=0.7)
        fit_within(block, SAFE_W, SAFE_H - crumb.height - 0.9)
        block.next_to(crumb, DOWN, buff=0.7)
        self.no_overlap(crumb, recap, title, today)
        self.validator.check_in_frame(VGroup(crumb, block))

        self.speaker("N")
        n = self.narrate(
            id="intro_01",
            text="In the last video you built the vocabulary and the notation: rows, signs, and one standard word for "
                 "every relation.",
            voice=NARRATOR_VOICE,
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.at_word(n, "vocabulary")
        self.play(FadeIn(recap[0]))
        self.at_word(n, "standard")
        self.play(FadeIn(recap[1], shift=UP * 0.1))
        self.wait_for_narration(n)

        self.speaker("N")
        n = self.narrate(
            id="intro_02",
            text="This video covers direct relation chains: several statements, one walk, one word.",
            voice=NARRATOR_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "covers")
        self.play(FadeIn(title, shift=UP * 0.1))
        self.at_word(n, "walk")
        self.play(FadeIn(today, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_intro")

    # ============================================== 1. HOOK ==========

    def hook(self):
        self.scene_start("S01_hook", title="Hook")

        head = self.heading("The visitor form")
        form = VGroup(pill("P is the brother of Q", WORD, size=LABEL), pill("Q is the daughter of R", WORD, size=LABEL),
                      pill("R is the wife of the patient, S", WORD, size=LABEL)).arrange(DOWN, buff=0.28)
        field = pill("Relation of P to the patient:  ?", FOCUS, size=BODY)
        clerks = VGroup(pill("Links in the wrong order:  “brother-in-law”", BAD, size=SMALL),
                        pill("Walk the chain from S:  right in ten seconds", GOOD, size=SMALL)).arrange(RIGHT, buff=0.5)
        self.stack(head, [form, field, clerks], buff=0.6, top=0.8)
        self.no_overlap(*clerks)

        self.speaker("N")
        n = self.narrate(
            id="hook_01",
            text="A hospital visitor form. Visitor P is the brother of Q. Q is the daughter of R. R is the wife of the "
                 "patient, S.",
            voice=NARRATOR_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "form")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "brother")
        self.play(FadeIn(form[0], shift=RIGHT * 0.2))
        self.at_word(n, "daughter")
        self.play(FadeIn(form[1], shift=RIGHT * 0.2))
        self.at_word(n, "wife")
        self.play(FadeIn(form[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("T", "ask")
        n = self.narrate(
            id="hook_02",
            text="The clerk has to fill one field: the relation of P to the patient. What would you write?",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=3.0,
        )
        self.at_word(n, "field")
        self.play(FadeIn(field, scale=1.03))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        self.speaker("S", "think")
        n = self.narrate(
            id="hook_03",
            text="P is a brother, and there is a wife. Brother-in-law?",
            voice=STUDENT_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "Brother-in-law")
        self.play(FadeIn(clerks[0], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("T", "smile")
        n = self.narrate(
            id="hook_04",
            text="That is what you get when the links are read in the wrong order. Walk the chain from S, and the right "
                 "word takes ten seconds.",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "Walk")
        self.play(FadeIn(clerks[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S01_hook")

    # ============================================== 2. OBJECTIVES ==========

    def objectives(self):
        self.scene_start("S02_objectives", title="Objectives")

        head = self.heading("By the end of this video")
        blocks = two_line_blocks(OBJECTIVES, WORD)
        self.stack(head, list(blocks), buff=0.6, top=0.8, align=LEFT)

        self.speaker("N")
        n = self.narrate(
            id="objectives_01",
            text="By the end of this video, you will be able to do three things.",
            voice=NARRATOR_VOICE,
            subtitle=True,
        )
        self.at_word(n, "three")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.wait_for_narration(n)

        self.speaker("N")
        n = self.narrate(
            id="objectives_02",
            text="One: trace a chain of relation statements one link at a time on a family tree.",
            voice=NARRATOR_VOICE,
            subtitle=True,
        )
        self.at_word(n, "trace")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "link")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("N")
        n = self.narrate(
            id="objectives_03",
            text="Two: read the question, how is X related to Y, as: X is Y's what? Then answer from Y's side.",
            voice=NARRATOR_VOICE,
            subtitle=True,
        )
        self.at_word(n, "read")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "answer")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("N")
        n = self.narrate(
            id="objectives_04",
            text="Three: count generations to confirm the answer word.",
            voice=NARRATOR_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "count")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "confirm")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_objectives")

    # ============================================== 3. WHY THIS SECTION ==========

    def why_this_section(self):
        self.scene_start("S03_why_this_section", title="Why This Section")

        head = self.heading("Why this section")
        most = pill("Chains are the most frequent blood-relation question", WORD, size=LABEL)
        wrong = pill("Most wrong answers name the relation in the wrong direction", BAD, size=LABEL)
        fix = pill("A fixed link-by-link method removes tracing errors and direction errors", GOOD, size=LABEL)
        self.stack(head, [most, wrong, fix], buff=0.8, top=1.1)

        self.speaker("T")
        n = self.narrate(
            id="why_this_section_01",
            text="Chains are the most frequent blood relation question. Most wrong answers in them come from two "
                 "mistakes: a link traced wrongly, or the relation named in the wrong direction.",
            voice=TEACHER_VOICE,
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "frequent")
        self.play(FadeIn(most, scale=1.03))
        self.at_word(n, "wrong")
        self.play(FadeIn(wrong, scale=1.03))
        self.wait_for_narration(n)

        self.speaker("T")
        n = self.narrate(
            id="why_this_section_02",
            text="A fixed method, link by link, removes both kinds of error.",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "method")
        self.play(FadeIn(fix, scale=1.03))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_why_this_section")

    # ============================================== 4. THE CONCEPT JOURNEY ==========

    def concept_journey(self):
        self.scene_start("S04_concept_journey", title="The Concept Journey")

        head = self.heading("Steps 1 to 3  ·  Build the tree")
        blocks = two_line_blocks(STEPS, WORD)
        family = self.tree({"C": (0.5, 0, ""), "B": (0, 1, "−"), "A": (1, 1, "+")}, kids=[(("C",), ["B", "A"])], dx=1.7)
        both = VGroup(blocks, family).arrange(RIGHT, buff=1.0)
        self.stack(head, [both], top=0.9)
        self.no_overlap(blocks, family)

        self.speaker("T")
        n = self.narrate(
            id="concept_journey_01",
            text="Step one: one link at a time. Draw each statement on the tree before reading the next. Never hold three "
                 "links in your head.",
            voice=TEACHER_VOICE,
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "link")
        self.play(Indicate(head, color=FOCUS, scale_factor=1.03), FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "Draw")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("T", "ask")
        n = self.narrate(
            id="concept_journey_02",
            text="Step two: join at the common person. A is the brother of B. B is the daughter of C. Where do the two "
                 "statements meet?",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "join")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "brother")
        self.play(FadeIn(family.node['A']), FadeIn(family.node['B']))
        self.at_word(n, "meet")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("S")
        n = self.narrate(
            id="concept_journey_03",
            text="At B. So A hangs off the same family as B.",
            voice=STUDENT_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "same")
        self.play(Indicate(family.node['B'], color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        self.speaker("T")
        n = self.narrate(
            id="concept_journey_04",
            text="Right. Step three: siblings share parents. A brother of B is a son of B's parents.",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "siblings")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "son")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2), FadeIn(family.down[0]), FadeIn(family.node['C']))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Steps 4 to 6  ·  Walk it and name it")
        blocks = two_line_blocks(MORE, WORD)
        walk = VGroup(pill("Y", FOCUS, size=BODY), Arrow(LEFT * 0.9, RIGHT * 0.9, color=FOCUS, stroke_width=5), pill("X", GOOD, size=BODY))\
            .arrange(RIGHT, buff=0.3)
        counts = VGroup(pill("Up to a parent:  +1", WORD, size=SMALL), pill("Down to a child:  −1", WORD, size=SMALL),
                        pill("Sibling or spouse:  0", WORD, size=SMALL)).arrange(DOWN, buff=0.22)
        side = VGroup(walk, counts).arrange(DOWN, buff=0.5)
        both = VGroup(blocks, side).arrange(RIGHT, buff=0.9)
        self.stack(head, [both], top=0.9)
        self.no_overlap(blocks, side)

        self.speaker("T")
        n = self.narrate(
            id="concept_journey_05",
            text="Step four: read the question from the end. How is X related to Y means: X is Y's what? Start at Y and "
                 "walk to X; the word describes X.",
            voice=TEACHER_VOICE,
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "end")
        self.play(Indicate(head, color=FOCUS, scale_factor=1.03), FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "Start")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2), FadeIn(walk))
        self.wait_for_narration(n)

        self.speaker("T")
        n = self.narrate(
            id="concept_journey_06",
            text="Step five: count generations as you walk. Up to a parent, plus one. Down to a child, minus one. Across "
                 "to a sibling or spouse, zero.",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "count")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2), FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.at_word(n, "Up")
        self.play(FadeIn(counts[0], shift=RIGHT * 0.2))
        self.at_word(n, "Down")
        self.play(FadeIn(counts[1], shift=RIGHT * 0.2))
        self.at_word(n, "Across")
        self.play(FadeIn(counts[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("S", "think")
        n = self.narrate(
            id="concept_journey_07",
            text="So a net gap of minus one could be a son, or a nephew?",
            voice=STUDENT_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "gap")
        self.play(Indicate(counts, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        self.speaker("T")
        n = self.narrate(
            id="concept_journey_08",
            text="Yes. The count gives the row, and the path gives the word. Straight down to your own child is a son. "
                 "Down through a brother or sister is a nephew.",
            voice=TEACHER_VOICE,
            subtitle=True,
        )
        self.at_word(n, "count")
        self.play(Indicate(counts, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        self.speaker("T")
        n = self.narrate(
            id="concept_journey_08b",
            text="Step six: only X's gender decides the word. Y's gender never matters.",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "gender")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2), FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_concept_journey")

    # ============================================== 5. RULE BOX ==========

    def rule_box(self):
        self.scene_start("S05_rule_box", title="Rule Box")

        head = self.heading("Rule box", GOOD)
        lines = VGroup(*[text(f, LABEL, INK) for f in FORMULAS]).arrange(DOWN, buff=0.5, aligned_edge=LEFT)
        fit_width(lines, SAFE_W - 1.6)
        box = self.card(lines, width=SAFE_W - 0.4, color=GOOD, pad=0.5)
        self.stack(head, [box], top=0.8)

        self.speaker("T")
        n = self.narrate(
            id="rule_box_01",
            text="Here is the rule box. Draw one link at a time, and join statements at the common person.",
            voice=TEACHER_VOICE,
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "box")
        self.play(FadeIn(box[0]))
        self.at_word(n, "link")
        self.play(FadeIn(lines[0], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("T")
        n = self.narrate(
            id="rule_box_02",
            text="Siblings share parents.",
            voice=TEACHER_VOICE,
            subtitle=True,
        )
        self.at_word(n, "share")
        self.play(FadeIn(lines[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("T")
        n = self.narrate(
            id="rule_box_03",
            text="How is X related to Y: start at Y, walk to X.",
            voice=TEACHER_VOICE,
            subtitle=True,
        )
        self.at_word(n, "start")
        self.play(FadeIn(lines[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("T")
        n = self.narrate(
            id="rule_box_04",
            text="Parent plus one, child minus one, sibling or spouse zero.",
            voice=TEACHER_VOICE,
            subtitle=True,
        )
        self.at_word(n, "Parent")
        self.play(FadeIn(lines[3], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("T")
        n = self.narrate(
            id="rule_box_05",
            text="And the word needs only X's gender.",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "word")
        self.play(FadeIn(lines[4], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_rule_box")

    # ============================================== 6. SHORT TRICK ==========

    def short_trick(self):
        self.scene_start("S06_short_trick", title="Short Trick")

        head = self.heading("Short trick")
        start = pill("Start at the second person named in the question;  walk to the first", WORD, size=LABEL)
        keep = pill("Keep a running generation count:  the word must match it, and the first person's gender", FOCUS, size=SMALL)
        self.stack(head, [start, keep], buff=1.0, top=1.4)

        self.speaker("T")
        n = self.narrate(
            id="short_trick_01",
            text="The short trick. Start at the second person named in the question, and walk to the first.",
            voice=TEACHER_VOICE,
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "second")
        self.play(FadeIn(start, scale=1.03))
        self.wait_for_narration(n)

        self.speaker("T")
        n = self.narrate(
            id="short_trick_02",
            text="Keep a running generation count. The final word must match that count, and the first person's gender.",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "count")
        self.play(FadeIn(keep, scale=1.03))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_short_trick")

    # ============================================== 7. THE ANALOGY ==========

    def analogy(self):
        self.scene_start("S07_analogy", title="The Analogy")

        head = self.heading("The analogy  ·  a journey with connections")
        route = VGroup(pill("S", WORD, size=BODY), Line(LEFT * 0.6, RIGHT * 0.6, color=MUTED, stroke_width=5), pill("R", FOCUS, size=BODY),
                       Line(LEFT * 0.6, RIGHT * 0.6, color=MUTED, stroke_width=5), pill("Q", FOCUS, size=BODY),
                       Line(LEFT * 0.6, RIGHT * 0.6, color=MUTED, stroke_width=5), pill("P", WORD, size=BODY)).arrange(RIGHT, buff=0.2)
        like = pill("Each statement is one line;  change only at a station both lines share", WORD, size=SMALL)
        stops = pill("Where it stops:  a relation does not read the same both ways", BAD, size=SMALL)
        self.stack(head, [route, like, stops], buff=0.7, top=1.0)

        self.speaker("T")
        n = self.narrate(
            id="analogy_01",
            text="A relation chain is a journey with connections. Each statement is one line between two stations, and you "
                 "can change only at a station both lines share.",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "journey")
        self.play(FadeIn(route))
        self.at_word(n, "change")
        self.play(FadeIn(like, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.speaker("S", "think")
        n = self.narrate(
            id="analogy_02",
            text="But a train line runs both ways under the same name.",
            voice=STUDENT_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "both")
        self.play(Indicate(route, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        self.speaker("T")
        n = self.narrate(
            id="analogy_03",
            text="And a relation does not. If A is B's father, B is A's son or daughter, never A's father. That is where "
                 "the analogy stops.",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "never")
        self.play(FadeIn(stops, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S07_analogy")

    # ============================================== 8. WORKED EXAMPLE: CLOSING THE HOOK ==========

    def hook_solved(self):
        self.scene_start("S08_hook_solved", title="Worked Example: Closing the Hook")

        head = self.heading("Worked example  ·  the visitor form")
        family = self.tree({"S": (0, 0, "+"), "R": (1, 0, "−"), "Q": (0, 1, "−"), "P": (1, 1, "+")},
                           couples=[("S", "R")], kids=[(("S", "R"), ["Q", "P"])])
        steps = self.steps_list([("Start at S.  S's wife is R", "0"), ("R's daughter is Q:  also S's daughter", "−1"),
                                 ("Q's brother is P:  same row, male", "−1"), ("Gap −1, male, S's own family", "Son")])
        both = VGroup(family, steps).arrange(RIGHT, buff=0.9)
        self.stack(head, [both], top=1.0)
        self.no_overlap(family, steps)

        self.speaker("T", "ask")
        n = self.narrate(
            id="hook_solved_01",
            text="Back to the form. How is P related to S? Where do we start?",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "form")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "start")
        self.play(FadeIn(family.node['S']))
        self.wait_for_narration(n)

        self.speaker("S")
        n = self.narrate(
            id="hook_solved_02",
            text="At S. His wife is R. Same row, zero.",
            voice=STUDENT_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "wife")
        self.play(FadeIn(family.wed[('S', 'R')]), FadeIn(family.node['R']), FadeIn(steps[0], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("T", "ask")
        n = self.narrate(
            id="hook_solved_03",
            text="Next link.",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "Next")
        self.play(Indicate(family.node['R'], color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        self.speaker("S")
        n = self.narrate(
            id="hook_solved_04",
            text="R's daughter is Q, one row down. And since R is S's wife, Q is also S's daughter.",
            voice=STUDENT_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "daughter")
        self.play(FadeIn(family.down[0][0]), FadeIn(family.down[0][2]), FadeIn(family.node['Q']), FadeIn(steps[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("T", "ask")
        n = self.narrate(
            id="hook_solved_05",
            text="And the brother of Q?",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "brother")
        self.play(FadeIn(family.down[0][1]), FadeIn(family.down[0][3]), FadeIn(family.node['P']), FadeIn(steps[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("S", "happy")
        n = self.narrate(
            id="hook_solved_06",
            text="P, on the same row, and male. Gap minus one, male, in S's own family. P is the son of S!",
            voice=STUDENT_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "son")
        self.play(FadeIn(steps[3], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("T", "happy")
        n = self.narrate(
            id="hook_solved_07",
            text="Son. Not brother-in-law. The walk took four short steps.",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "Son")
        self.play(Indicate(steps[3], color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S08_hook_solved")

    # ============================================== 9. A SECOND WORKED EXAMPLE ==========

    def second_example(self):
        self.scene_start("S09_second_example", title="A Second Worked Example")

        head = self.heading("When the chain passes through siblings")
        family = self.tree({"D": (0, 0, ""), "C": (1.2, 0, "+"), "B": (0.7, 1, "+"), "A": (1.9, 1, "−")},
                           kids=[(("C",), ["B", "A"])], sibs=[("D", "C")])
        steps = self.steps_list([("Start at D.  D's brother is C", "0"), ("C's son is B;  B's sister A is C's child too", "−1, female"),
                                 ("Female, one row down, through D's brother", "Niece")])
        both = VGroup(family, steps).arrange(RIGHT, buff=0.8)
        self.stack(head, [both], top=1.0)
        self.no_overlap(family, steps)

        self.speaker("T", "ask")
        n = self.narrate(
            id="second_example_01",
            text="A second one. A is the sister of B. B is the son of C. C is the brother of D. How is A related to D?",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "second")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "brother")
        self.play(FadeIn(family.node['D']), FadeIn(family.sib[('D', 'C')]), FadeIn(family.node['C']))
        self.wait_for_narration(n)

        self.speaker("S")
        n = self.narrate(
            id="second_example_02",
            text="Start at D. The brother of D is C, same row.",
            voice=STUDENT_VOICE,
            subtitle=True,
        )
        self.at_word(n, "Start")
        self.play(FadeIn(steps[0], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("S")
        n = self.narrate(
            id="second_example_03",
            text="C's son is B, one row down. And B's sister A is also C's child. Female.",
            voice=STUDENT_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "son")
        self.play(FadeIn(family.down[0]), FadeIn(family.node['B']), FadeIn(family.node['A']))
        self.at_word(n, "sister")
        self.play(FadeIn(steps[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("T", "ask")
        n = self.narrate(
            id="second_example_04",
            text="A female one row down, through D's brother.",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "female")
        self.play(Indicate(family.node['A'], color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        self.speaker("S", "happy")
        n = self.narrate(
            id="second_example_05",
            text="Niece! And we never needed the gender of D.",
            voice=STUDENT_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "Niece")
        self.play(FadeIn(steps[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("T", "happy")
        n = self.narrate(
            id="second_example_06",
            text="Correct: niece. And you are right about D. The word needed only the gender of A.",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "niece")
        self.play(Indicate(steps[2], color=GOOD, scale_factor=1.03))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S09_second_example")

    # ============================================== 10. EXAM PATTERNS - HOW THIS IS ASKED ==========

    def exam_patterns(self):
        self.scene_start("S10_exam_patterns", title="Exam Patterns - How This Is Asked")

        head = self.heading("Exam patterns  ·  part 1")
        table, rows = self.placed_table(head, ["Statements", "Asks", "Walk from the second person", "Answer"], PATTERNS_A,
                                        [4.8, 1.5, 4.2, 2.7], room=1.4)
        for row in rows:
            row[2].set_color(WORD)
            row[3].set_color(GOOD)

        self.speaker("T")
        n = self.narrate(
            id="exam_patterns_01",
            text="How this is asked. A is the brother of B, B is the son of C. A to C: walk from C, to the son, to the "
                 "brother. Son. Your turn. P is the wife of Q, and Q is the father of R. How is P related to R?",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "asked")
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "walk")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "turn")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("S")
        n = self.narrate(
            id="exam_patterns_02",
            text="From R, go to the father Q, then to his wife P. Mother.",
            voice=STUDENT_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "father")
        self.play(FadeIn(rows[1][2:], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("T")
        n = self.narrate(
            id="exam_patterns_03",
            text="Right. K is the daughter of L, L is the sister of M. From M: sister, then daughter. Niece.",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "sister")
        self.play(FadeIn(rows[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Exam patterns  ·  part 2")
        table, rows = self.placed_table(head, ["Statements", "Asks", "Walk from the second person", "Answer"], PATTERNS_B,
                                        [4.8, 1.5, 4.2, 2.7], room=1.4)
        for row in rows:
            row[2].set_color(WORD)
            row[3].set_color(GOOD)

        self.speaker("T")
        n = self.narrate(
            id="exam_patterns_04",
            text="Father of a father: grandfather. And the husband of a sister?",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "grandfather")
        self.play(Indicate(head, color=FOCUS, scale_factor=1.03), FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "husband")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("S")
        n = self.narrate(
            id="exam_patterns_05",
            text="The husband of a sister is a brother-in-law.",
            voice=STUDENT_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "husband")
        self.play(FadeIn(rows[1][2:], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("T")
        n = self.narrate(
            id="exam_patterns_06",
            text="Yes. And watch the last one. G is the son of H, H is the husband of J, but the question asks about J. "
                 "Walk from G: father, then his wife. Mother.",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "last")
        self.play(FadeIn(rows[2], shift=RIGHT * 0.2))
        self.at_word(n, "Mother")
        self.play(Indicate(rows[2][3], color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S10_exam_patterns")

    # ============================================== 11. TRAPS AND CONFUSING QUESTIONS ==========

    def traps(self):
        self.scene_start("S11_traps", title="Traps and Confusing Questions")

        head, ask, wrong, right, rule = self.show_trap(TRAPS[0])

        self.speaker("T", "ask")
        n = self.narrate(
            id="traps_01",
            text="Trap one. R is the father of Q. P is the son of Q. How is R related to P?",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "one")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "related")
        self.play(FadeIn(ask, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.speaker("S")
        n = self.narrate(
            id="traps_02",
            text="Grandson.",
            voice=STUDENT_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "Grandson")
        self.play(FadeIn(wrong))
        self.wait_for_narration(n)

        self.speaker("T", "think")
        n = self.narrate(
            id="traps_03",
            text="That describes P from R's side. Start at P and walk to R: his father Q, then Q's father R. Grandfather.",
            voice=TEACHER_VOICE,
            subtitle=True,
        )
        self.at_word(n, "Grandfather")
        self.play(FadeIn(right))
        self.wait_for_narration(n)

        self.speaker("T")
        n = self.narrate(
            id="traps_04",
            text="How is X related to Y always describes X. Start the walk at Y.",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "describes")
        self.play(FadeIn(rule, scale=1.03))
        self.wait_for_narration(n)
        self.clear_stage()

        head, ask, wrong, right, rule = self.show_trap(TRAPS[1])

        self.speaker("T", "ask")
        n = self.narrate(
            id="traps_05",
            text="Trap two. A is the son of B. B is the sister of C. C is the father of D. How is A related to D?",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "two")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "sister")
        self.play(FadeIn(ask, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.speaker("S")
        n = self.narrate(
            id="traps_06",
            text="Brother. B and C are the parents.",
            voice=STUDENT_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "Brother")
        self.play(FadeIn(wrong))
        self.wait_for_narration(n)

        self.speaker("T", "think")
        n = self.narrate(
            id="traps_07",
            text="B and C are siblings, not a couple. Their children sit on the row below, in two different families. "
                 "Cousin.",
            voice=TEACHER_VOICE,
            subtitle=True,
        )
        self.at_word(n, "Cousin")
        self.play(FadeIn(right))
        self.wait_for_narration(n)

        self.speaker("T")
        n = self.narrate(
            id="traps_08",
            text="A horizontal sibling line is not a marriage. Children of siblings are cousins.",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "marriage")
        self.play(FadeIn(rule, scale=1.03))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S11_traps")

    # ============================================== 12. CHECKPOINT ==========

    def checkpoint(self):
        self.scene_start("S12_checkpoint", title="Checkpoint")

        head = self.heading("Checkpoint  ·  your turn")
        ask = VGroup(pill("M is the wife of N.   N is the father of O.   O is the brother of P.", WORD, size=SMALL),
                     pill("How is M related to P?", FOCUS, size=BODY)).arrange(DOWN, buff=0.3)
        family = self.tree({"N": (0, 0, "+"), "M": (1, 0, "−"), "O": (0, 1, "+"), "P": (1, 1, "")},
                           couples=[("N", "M")], kids=[(("N", "M"), ["O", "P"])], dy=1.1)
        answer = pill("Mother", GOOD, size=BODY)
        self.stack(head, [ask, family, answer], buff=0.5, top=0.7)

        self.speaker("T", "ask")
        n = self.narrate(
            id="checkpoint_01",
            text="Your turn. M is the wife of N. N is the father of O. O is the brother of P. How is M related to P?",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=10.0,
        )
        self.at_word(n, "turn")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "wife")
        self.play(FadeIn(ask, scale=1.03))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        self.speaker("S", "happy")
        n = self.narrate(
            id="checkpoint_02",
            text="Start at P. Brother O, their father N, and his wife M. Mother.",
            voice=STUDENT_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "Start")
        self.play(FadeIn(family))
        self.at_word(n, "Mother")
        self.play(FadeIn(answer, scale=1.03))
        self.wait_for_narration(n)

        self.speaker("T", "happy")
        n = self.narrate(
            id="checkpoint_03",
            text="Correct. Check it with the count: across to a brother, zero. Up to the father, plus one. Across to his "
                 "wife, zero. One row up and female: mother.",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "count")
        self.play(Indicate(family.node['M'], color=GOOD, scale_factor=1.03))
        self.at_word(n, "mother")
        self.play(Indicate(answer, color=GOOD, scale_factor=1.03))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S12_checkpoint")

    # ============================================== 13. PRACTICE QUESTIONS ==========

    def practice(self):
        self.scene_start("S13_practice", title="Practice Questions")

        head = self.heading("Practice  ·  Levels 1 and 2")
        table, rows = self.practice_table(head, PRACTICE_A, 1)

        self.speaker("T")
        n = self.narrate(
            id="practice_01",
            text="For each, give the relation in one word. Level one.",
            voice=TEACHER_VOICE,
            subtitle=True,
        )
        self.at_word(n, "give")
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "Level")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2), FadeIn(rows[1], shift=RIGHT * 0.2), FadeIn(rows[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("T")
        n = self.narrate(
            id="practice_02",
            text="Level two: longer chains.",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "two")
        self.play(FadeIn(rows[3], shift=RIGHT * 0.2), FadeIn(rows[4], shift=RIGHT * 0.2), FadeIn(rows[5], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("T")
        n = self.narrate(
            id="practice_03",
            text="Pause the video and solve these six.",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=12.0,
        )
        self.at_word(n, "Pause")
        self.play(Indicate(head, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)
        self.clear_stage()

        head = self.heading("Practice  ·  Level 3")
        table, rows = self.practice_table(head, PRACTICE_B, 7)

        self.speaker("T")
        n = self.narrate(
            id="practice_04",
            text="Level three. The second one also asks how many generations apart.",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "Level")
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "second")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2), FadeIn(rows[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("T")
        n = self.narrate(
            id="practice_05",
            text="Pause again and solve these two.",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=12.0,
        )
        self.at_word(n, "Pause")
        self.play(Indicate(head, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        self.clear_stage()
        self.scene_end("S13_practice")

    # ============================================== 14. ANSWER KEY, WITH REASONING ==========

    def answers(self):
        self.scene_start("S14_answers", title="Answer Key, with Reasoning")

        head = self.heading("Answer key  ·  1 to 4", GOOD)
        table, rows = self.answer_table(head, ANSWERS_A, 1)

        self.speaker("S")
        n = self.narrate(
            id="answers_01",
            text="One: daughter. X is a sibling of Z's son, female, one row down.",
            voice=STUDENT_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "daughter")
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.at_word(n, "sibling")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("T")
        n = self.narrate(
            id="answers_02",
            text="Yes. Two: father. Q's husband, and R is Q's child.",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "father")
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.at_word(n, "husband")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("S")
        n = self.narrate(
            id="answers_03",
            text="Three: granddaughter. Two rows down, female.",
            voice=STUDENT_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "granddaughter")
        self.play(FadeIn(rows[2][2], shift=LEFT * 0.1))
        self.at_word(n, "rows")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("T")
        n = self.narrate(
            id="answers_04",
            text="Right. Four: sister-in-law, the wife of C's brother.",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "sister-in-law")
        self.play(FadeIn(rows[3][2], shift=LEFT * 0.1))
        self.at_word(n, "wife")
        self.play(FadeIn(rows[3][:2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Answer key  ·  5 to 8", GOOD)
        table, rows = self.answer_table(head, ANSWERS_B, 5)

        self.speaker("S")
        n = self.narrate(
            id="answers_05",
            text="Five: cousin. K's father and N's mother are siblings.",
            voice=STUDENT_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "cousin")
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.at_word(n, "siblings")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("T")
        n = self.narrate(
            id="answers_06",
            text="Yes. Six: father-in-law. V's husband T is R's son.",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "father-in-law")
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.at_word(n, "husband")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("S")
        n = self.narrate(
            id="answers_07",
            text="Seven: maternal uncle. B is the mother of D and E, and A is her brother.",
            voice=STUDENT_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "uncle")
        self.play(FadeIn(rows[2][2], shift=LEFT * 0.1))
        self.at_word(n, "mother")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("T")
        n = self.narrate(
            id="answers_08",
            text="Correct. Eight: paternal grandmother, two generations up. P is the mother of T's father.",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "grandmother")
        self.play(FadeIn(rows[3][2], shift=LEFT * 0.1))
        self.at_word(n, "mother")
        self.play(FadeIn(rows[3][:2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S14_answers")

    # ============================================== 15. EXAM LENS - RECOGNISE AND MOVE ==========

    def exam_lens(self):
        self.scene_start("S15_exam_lens", title="Exam Lens - Recognise and Move")

        head = self.heading("Exam lens: recognise and move", RATIO)
        blocks = two_line_blocks(LENS, RATIO)
        self.stack(head, list(blocks), buff=0.6, top=0.8, align=LEFT)

        self.speaker("T")
        n = self.narrate(
            id="exam_lens_01",
            text="Recognise and move. The recognition cue: two to four statements of the form, A is the something of B, "
                 "and then, how is X related to Y.",
            voice=TEACHER_VOICE,
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "cue")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "statements")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("T")
        n = self.narrate(
            id="exam_lens_02",
            text="The target time: thirty seconds.",
            voice=TEACHER_VOICE,
            subtitle=True,
        )
        self.at_word(n, "target")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "thirty")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("T")
        n = self.narrate(
            id="exam_lens_03",
            text="The sanity check: the generation count of the walk must match the answer word, and the word must fit X's "
                 "gender.",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "sanity")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "count")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S15_exam_lens")

    # ============================================== 16. QUICK REVISION AND SUMMARY ==========

    def summary(self):
        self.scene_start("S16_summary", title="Quick Revision and Summary")

        head = self.heading("Quick revision")
        draw = VGroup(pill("Draw each link", WORD, size=LABEL), pill("Join at common people", WORD, size=LABEL),
                      pill("Siblings share parents", WORD, size=LABEL)).arrange(RIGHT, buff=0.35)
        walk = text("Answer “How is X related to Y?” from Y's side", LABEL, INK, BOLD)
        box = VGroup(pill("One link at a time", GOOD, size=SMALL), pill("Start at Y, end at X", GOOD, size=SMALL),
                     pill("Parent +1 · child −1 · sibling 0", GOOD, size=SMALL), pill("X's gender only", GOOD, size=SMALL)).arrange(RIGHT, buff=0.3)
        fit_width(box, SAFE_W - 0.4)
        self.stack(head, [draw, walk, box], buff=0.8, top=1.0)
        self.no_overlap(*draw)
        self.no_overlap(*box)

        self.speaker("N")
        n = self.narrate(
            id="summary_01",
            text="Quick revision. Draw each link, join at common people, and remember that siblings share parents.",
            voice=NARRATOR_VOICE,
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "Draw")
        self.play(FadeIn(draw[0], shift=UP * 0.1))
        self.at_word(n, "join")
        self.play(FadeIn(draw[1], shift=UP * 0.1))
        self.at_word(n, "siblings")
        self.play(FadeIn(draw[2], shift=UP * 0.1))
        self.wait_for_narration(n)

        self.speaker("N")
        n = self.narrate(
            id="summary_02",
            text="Answer, how is X related to Y, from Y's side, with a running generation count and X's gender.",
            voice=NARRATOR_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "side")
        self.play(FadeIn(walk, shift=UP * 0.1))
        self.at_word(n, "count")
        self.play(FadeIn(box, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S16_summary")

    # ============================================== 17. SECTION QUIZ ==========

    def section_quiz(self):
        self.scene_start("S17_section_quiz", title="Section Quiz")

        head = self.heading("Section quiz")
        rules = VGroup(pill("5 questions", WORD, size=BODY), pill("4 minutes", WORD, size=BODY), pill("+3 correct", GOOD, size=BODY),
                       pill("−1 wrong", BAD, size=BODY)).arrange(RIGHT, buff=0.4)
        gate = VGroup(VGroup(pill("12 or more out of 15", GOOD, size=LABEL), text("move on", BODY, GOOD, BOLD)).arrange(RIGHT, buff=0.5),
                      VGroup(pill("below 12", BAD, size=LABEL), text("replay the Traps segment, then retry", BODY, INK, BOLD)).arrange(RIGHT, buff=0.5))            .arrange(DOWN, buff=0.6, aligned_edge=LEFT)
        self.stack(head, [rules, gate], buff=1.1, top=1.1)
        self.no_overlap(*rules)
        self.no_overlap(*gate)

        self.speaker("N")
        n = self.narrate(
            id="section_quiz_01",
            text="Now the section quiz: five questions in four minutes, with plus three for a correct answer and minus one "
                 "for a wrong one.",
            voice=NARRATOR_VOICE,
            subtitle=True,
        )
        self.at_word(n, "quiz")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "questions")
        self.play(FadeIn(rules[0], shift=UP * 0.1))
        self.at_word(n, "minutes")
        self.play(FadeIn(rules[1], shift=UP * 0.1))
        self.at_word(n, "plus")
        self.play(FadeIn(rules[2], shift=UP * 0.1))
        self.at_word(n, "minus")
        self.play(FadeIn(rules[3], shift=UP * 0.1))
        self.wait_for_narration(n)

        self.speaker("N")
        n = self.narrate(
            id="section_quiz_02",
            text="Twelve or more out of fifteen: move on. Below twelve: replay the traps segment, then retry.",
            voice=NARRATOR_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "move")
        self.play(FadeIn(gate[0], shift=RIGHT * 0.2))
        self.at_word(n, "replay")
        self.play(FadeIn(gate[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Section quiz  ·  questions 1 to 3")
        table, rows = self.placed_table(head, ["#", "Question", "Options"],
                                        [[str(0 + i + 1)] + list(row) for i, row in enumerate(QUIZ[0:3])], [0.8, 5.4, 7.0], room=1.3)
        for row in rows:
            row[0].set_color(MUTED)

        self.speaker("N")
        n = self.narrate(
            id="section_quiz_03",
            text="Here are questions one, two and three.",
            voice=NARRATOR_VOICE,
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "one")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "two")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.at_word(n, "three")
        self.play(FadeIn(rows[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("N")
        n = self.narrate(
            id="section_quiz_04",
            text="Pause the video and solve them.",
            voice=NARRATOR_VOICE,
            subtitle=True,
            pause_after=12.0,
        )
        self.at_word(n, "Pause")
        self.play(Indicate(head, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)
        self.clear_stage()

        head = self.heading("Section quiz  ·  questions 4 to 5")
        table, rows = self.placed_table(head, ["#", "Question", "Options"],
                                        [[str(3 + i + 1)] + list(row) for i, row in enumerate(QUIZ[3:5])], [0.8, 5.4, 7.0], room=1.3)
        for row in rows:
            row[0].set_color(MUTED)

        self.speaker("N")
        n = self.narrate(
            id="section_quiz_05",
            text="And here are questions four and five.",
            voice=NARRATOR_VOICE,
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "four")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "five")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("N")
        n = self.narrate(
            id="section_quiz_06",
            text="Pause again and solve them.",
            voice=NARRATOR_VOICE,
            subtitle=True,
            pause_after=12.0,
        )
        self.at_word(n, "Pause")
        self.play(Indicate(head, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)
        self.clear_stage()

        head = self.heading("Section quiz  ·  answer key", GOOD)
        table, rows = self.answer_table(head, QUIZ_KEY, 1)
        nxt = self.breadcrumb("Next", "Pointing & Introduction Statements")
        nxt.next_to(table, DOWN, buff=0.6)
        self.no_overlap(table, nxt)
        self.validator.check_in_frame(VGroup(head, table, nxt))

        self.speaker("T")
        n = self.narrate(
            id="section_quiz_07",
            text="One: option B, niece. From D, to the brother C, to his daughter A.",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "option")
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.at_word(n, "brother")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("S")
        n = self.narrate(
            id="section_quiz_08",
            text="Two: option C, father-in-law. From R, to the wife Q, to her father P.",
            voice=STUDENT_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "option")
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.at_word(n, "wife")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("T")
        n = self.narrate(
            id="section_quiz_09",
            text="Yes. Three: option A, father. Z is the wife of W, so her son X is also the son of W.",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "option")
        self.play(FadeIn(rows[2][2], shift=LEFT * 0.1))
        self.at_word(n, "wife")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("S")
        n = self.narrate(
            id="section_quiz_10",
            text="Four: option D, maternal grandmother. From M, to the mother N, to her mother P.",
            voice=STUDENT_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "option")
        self.play(FadeIn(rows[3][2], shift=LEFT * 0.1))
        self.at_word(n, "mother")
        self.play(FadeIn(rows[3][:2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("T")
        n = self.narrate(
            id="section_quiz_11",
            text="Right. Five: option A, maternal uncle. From H, to the mother F, to her brother E.",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "option")
        self.play(FadeIn(rows[4][2], shift=LEFT * 0.1))
        self.at_word(n, "mother")
        self.play(FadeIn(rows[4][:2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("N")
        n = self.narrate(
            id="section_quiz_12",
            text="Next: pointing and introduction statements.",
            voice=NARRATOR_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "Next")
        self.play(FadeIn(nxt, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.curtain()
        self.scene_end("S17_section_quiz")

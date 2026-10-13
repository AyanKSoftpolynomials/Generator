"""
animation.py for the LMS video generator.

Course : Pre-C-CAT - Section A - Logical Reasoning
Video  : Lesson 10 - Blood Relation I - 02 - Relation Vocabulary & Family-Tree Notation

Source script:
  C:\\Scripts\\Section A\\New folder\\Lesson 10 - Blood Relation I\\02 - Relation Vocabulary & Family-Tree Notation.pdf

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

Lesson 10, Video 1 of 5 (file 02 in its folder).
The narration follows the script section by section and ends with the Section Quiz and its answer key.
Trees are drawn in the script's notation: + male (blue), − female (gold), = couple, lines for children and siblings.
Every relation word in the script was worked out again in the data block from the family facts; all answers are correct.
In the PDF the Exam Patterns table and the quiz answer key are printed with their columns out of line;
here each row carries its own word (key: 1 b, 2 c, 3 d, 4 a, 5 b).
Pauses: 3 seconds on the hook, 10 on the checkpoint, 12 on each practice and quiz screen.
Teaching review, 2026-10-09 (narration departs from the script here): the child in the worked tree is V, not U
("U" is heard as "you"); row gaps are spoken as "one row up / down" so that plus and minus stay gender marks;
the teacher confirms every answer the student gives; the worked tree is drawn from its sentences before it is read;
quiz answers are spoken as "option B"; an uncle or aunt by marriage takes no side word.
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

# ---- hook, worked examples, checkpoint ----
HOOK = Family("F father Bride; A sister F")
assert (HOOK.word("A", "Bride"), HOOK.side("A", "Bride"), HOOK.gap("A", "Bride")) == ("aunt", "paternal", 1)
TREE = Family("P husband Q; R son P; S daughter Q; T husband S; V daughter S")     # V, not U: "U" is heard as "you"
assert TREE.word("T", "R") == "brother-in-law" and TREE.word("V", "Q") == "granddaughter"
assert (TREE.word("R", "V"), TREE.side("R", "V")) == ("uncle", "maternal")
assert rel("F father Me; A sister F; H husband A", "H", "Me") == "uncle"
# ---- exam patterns: (facts, person, word, row gap) ----
for facts_, who_, word_, gap_ in [("M mother Me; B brother M", "B", "uncle", 1), ("F father Me; A sister F; C son A", "C", "cousin", 0),
                                  ("B brother Me; D daughter B", "D", "niece", -1), ("H husband Me; B brother H", "B", "brother-in-law", 0),
                                  ("S sister Me; H husband S", "H", "brother-in-law", 0), ("S son Me; W wife S", "W", "daughter-in-law", -1),
                                  ("Me husband W; M mother W", "M", "mother-in-law", 1), ("D daughter Me; S son D", "S", "grandson", -2)]:
    fam_ = Family(facts_)
    assert (fam_.word(who_, "Me"), fam_.gap(who_, "Me")) == (word_, gap_), facts_
# ---- traps ----
assert rel("M mother Me; B brother M; W wife B", "W", "Me") == "aunt" and rel("M mother Me; B brother M; W wife B", "W", "M") == "sister-in-law"
# ---- practice ----
for facts_, who_, word_ in [("M mother Me; S sister M", "S", "aunt"), ("S son Me; G son S", "G", "grandson"),
                            ("Me husband W; F father W", "F", "father-in-law"), ("S sister Me; N son S", "N", "nephew"),
                            ("M mother Me; B brother M; D daughter B", "D", "cousin"), ("B brother Me; W wife B", "W", "sister-in-law"),
                            ("F father Me; B brother F; W wife B; S son W", "S", "cousin")]:
    assert rel(facts_, who_, "Me") == word_, facts_
# ---- section quiz ----
assert Family("M mother Me; G father M").side("G", "Me") == "maternal" and rel("M mother Me; G father M", "G", "Me") == "grandfather"
assert rel("H husband W; S sister H", "S", "W") == "sister-in-law" and rel("B brother Q; P son B", "P", "Q") == "nephew"
assert rel("A husband B; C son A; D daughter A; E husband D", "E", "A") == "son-in-law"
assert rel("B brother Me; W wife B; D daughter W", "D", "Me") == "niece"

OBJECTIVES = [("Use the standard relation words", "including paternal, maternal and in-law terms"),
              ("Draw any family on paper", "with the standard family-tree notation"),
              ("Apply the exam conventions", "on gender, names and “only”")]
ROWS = [["+2", "Grandparents"], ["+1", "Parents, uncles and aunts"], ["0", "You, siblings, spouse, cousins, siblings-in-law"],
        ["−1", "Children, nephews and nieces"], ["−2", "Grandchildren"]]
IN_LAWS = [["Spouse's father and mother", "Father-in-law, mother-in-law"], ["Daughter's husband", "Son-in-law"],
           ["Son's wife", "Daughter-in-law"], ["Spouse's brother, or sister's husband", "Brother-in-law"],
           ["Spouse's sister, or brother's wife", "Sister-in-law"]]
CONVENTIONS = [("Gender only when stated or implied", "son, sister, husband, he, she: never a name or a letter"),
               ("Different names are different people", "and brothers and sisters share both parents"),
               ("No step-relations", "a married person's child is also the spouse's child"),
               ("“Only son” is not “only child”", "no other son, but daughters may exist")]
FORMULAS = ["Rows:   grandparents +2  ·  parents, uncles, aunts +1  ·  your row 0  ·  children, nephews, nieces −1",
            "Paternal = father's side        maternal = mother's side",
            "Brother-in-law = spouse's brother or sister's husband;   sister-in-law = spouse's sister or brother's wife",
            "Notation:   + male  ·  − female  ·  = couple  ·  vertical line = next generation  ·  horizontal line = siblings",
            "Gender only when stated or implied  ·  different names, different people  ·  only son ≠ only child"]
PATTERNS_A = [["Mother's brother", "+1", "Maternal uncle"], ["Father's sister's son", "0", "Cousin"],
              ["Brother's daughter", "−1", "Niece"], ["Husband's brother", "0", "Brother-in-law"]]
PATTERNS_B = [["Sister's husband", "0", "Brother-in-law"], ["Son's wife", "−1", "Daughter-in-law"],
              ["Wife's mother", "+1", "Mother-in-law"], ["Daughter's son", "−2", "Grandson"]]
TRAPS = [("Trap 1  ·  naming from the wrong person's side", "How is your mother's brother's wife related to you?",
          "“Sister-in-law: she married a brother”", "She is your mother's sister-in-law.  To you: aunt",
          "The word describes the person from the side of the one named last"),
         ("Trap 2  ·  “only son” read as “only child”", "A is the only son of B, and C is another child of B.  How is C related to A?",
          "“Cannot be determined: C's gender is not stated”", "C is not A, so C is a daughter:  sister",
          "“Only son” rules out other sons, not daughters")]
PRACTICE_A = [("L1", "Your mother's sister."), ("L1", "Your son's son."), ("L1", "Your wife's father."),
              ("L2", "Your sister's son."), ("L2", "Your mother's brother's daughter."), ("L2", "Your brother's wife.")]
PRACTICE_B = [("L3", "Your father's only brother's wife's son."),
              ("L3", "A is the only daughter of B, and C is another child of B.  How is C related to A?")]
ANSWERS_A = [("+1, female, mother's side", "Maternal aunt"), ("−2, male", "Grandson"),
             ("The father of your spouse", "Father-in-law"), ("−1, male, through your sister", "Nephew")]
ANSWERS_B = [("Child of a maternal uncle; the word has no gender", "Cousin"), ("Your brother's wife", "Sister-in-law"),
             ("Son of your paternal uncle and his wife", "Cousin"), ("B has only one daughter, A, so C is a son", "Brother")]
LENS = [("Recognition cue", "a description such as “mother's brother's son”, or a tree drawn with +, − and ="),
        ("Target time", "15 seconds per relation word"),
        ("Sanity check", "count the row gap and read the sign of the person described: the word must match both")]
QUIZ = [["How is your mother's father related to you?",
         "(a) Paternal grandfather\n(b) Maternal grandfather\n(c) Maternal uncle\n(d) Father-in-law"],
        ["How is a woman's husband's sister related to her?", "(a) Sister\n(b) Cousin\n(c) Sister-in-law\n(d) Niece"],
        ["P is the son of Q's only brother.  How is P related to Q?", "(a) Son\n(b) Brother\n(c) Cousin\n(d) Nephew"],
        ["A(+) = B(−); children C(+), D(−); D = E(+).  E to A?",
         "(a) Son-in-law\n(b) Son\n(c) Brother-in-law\n(d) Nephew"],
        ["How is your brother's wife's daughter related to you?", "(a) Daughter\n(b) Niece\n(c) Sister-in-law\n(d) Cousin"]]
QUIZ_KEY = [("Mother's side, +2, male", "(b)"), ("Spouse's sister", "(c)"), ("Son of Q's brother: −1, male", "(d)"),
            ("Daughter's husband", "(a)"), ("Brother's daughter", "(b)")]


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


class RelationVocabularyAndNotationVideo(LMSScene):
    lesson_title = "Relation Vocabulary & Family-Tree Notation"

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
    # First video of the lesson: silent breadcrumb, the lesson announcement, a recap of the previous lesson, then today's topic.

    def intro(self):
        self.scene_start("S00_intro", title="Intro")

        crumb = self.breadcrumb("Logical Reasoning", "Lesson 10 · Blood Relation I", "Video 1 of 5")
        crumb.move_to(UP * (FRAME_H / 2 - SAFE - crumb.height / 2))
        lesson = pill("Lesson 10  ·  Blood Relation I", RATIO, size=LABEL)
        recap = VGroup(text("So far in Logical Reasoning", SMALL, MUTED),
                       fit_width(VGroup(pill("Draw the structure first", WORD, size=LABEL), pill("Read the answer off the drawing", GOOD, size=LABEL)).arrange(RIGHT, buff=0.4), SAFE_W - 0.6)).arrange(DOWN, buff=0.25)
        title = fit_width(text("Relation Vocabulary & Family-Tree Notation", TITLE, INK, BOLD), SAFE_W - 0.4)
        today = text("Today: the words and the notation", LABEL, FOCUS)
        block = VGroup(lesson, recap, title, today).arrange(DOWN, buff=0.55)
        fit_within(block, SAFE_W, SAFE_H - crumb.height - 0.9)
        block.next_to(crumb, DOWN, buff=0.6)
        self.no_overlap(crumb, lesson, recap, title, today)
        self.no_overlap(*recap[1])
        self.validator.check_in_frame(VGroup(crumb, block))

        self.speaker("N")
        n = self.narrate(
            id="intro_01",
            text="Now we start lesson ten: blood relations.",
            voice=NARRATOR_VOICE,
            subtitle=True,
        )
        self.play(FadeIn(crumb, shift=DOWN * 0.2))
        self.at_word(n, "ten")
        self.play(FadeIn(lesson, scale=1.03))
        self.wait_for_narration(n)

        self.speaker("N")
        n = self.narrate(
            id="intro_02",
            text="So far, every topic worked the same way: draw the structure first, then read the answer off it.",
            voice=NARRATOR_VOICE,
            subtitle=True,
        )
        self.at_word(n, "draw")
        self.play(FadeIn(recap[0]), FadeIn(recap[1][0], shift=UP * 0.1))
        self.at_word(n, "read")
        self.play(FadeIn(recap[1][1], shift=UP * 0.1))
        self.wait_for_narration(n)

        self.speaker("N")
        n = self.narrate(
            id="intro_03",
            text="This first video covers relation vocabulary and family tree notation: the words and the drawing.",
            voice=NARRATOR_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "covers")
        self.play(FadeIn(title, shift=UP * 0.1))
        self.at_word(n, "words")
        self.play(FadeIn(today, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S00_intro")

    # ============================================== 1. HOOK ==========

    def hook(self):
        self.scene_start("S01_hook", title="Hook")

        head = self.heading("The seating card")
        card = pill("Reserved:  the bride's father's sister", FOCUS, size=BODY)
        ask = text("What is she to the bride, in one word?", LABEL, INK, BOLD)
        both = VGroup(pill("A chain of “of”s", WORD, size=LABEL), text("⇄", BODY, MUTED, BOLD), pill("One standard word", WORD, size=LABEL))\
            .arrange(RIGHT, buff=0.4)
        tools = VGroup(pill("The vocabulary", GOOD, size=LABEL), pill("The notation", GOOD, size=LABEL)).arrange(RIGHT, buff=0.5)
        self.stack(head, [card, ask, both, tools], buff=0.75, top=0.9)

        self.speaker("N")
        n = self.narrate(
            id="hook_01",
            text="A wedding hall. An usher holds a seating card: reserved for the bride's father's sister.",
            voice=NARRATOR_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "usher")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "card")
        self.play(FadeIn(card, scale=1.03))
        self.wait_for_narration(n)

        self.speaker("T", "ask")
        n = self.narrate(
            id="hook_02",
            text="What is she to the bride, in one word?",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=3.0,
        )
        self.at_word(n, "word")
        self.play(FadeIn(ask, shift=UP * 0.1))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        self.speaker("S", "think")
        n = self.narrate(
            id="hook_03",
            text="Her father's sister. Some kind of aunt?",
            voice=STUDENT_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "aunt")
        self.play(Indicate(card, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        self.speaker("T")
        n = self.narrate(
            id="hook_04",
            text="Which kind? Hold that thought. Every blood relation question ends the same way: a chain has to become "
                 "one standard word, or one word has to be opened back into a chain.",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "chain")
        self.play(FadeIn(both[0], shift=RIGHT * 0.2), FadeIn(both[1], shift=UP * 0.1))
        self.at_word(n, "standard")
        self.play(FadeIn(both[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("N")
        n = self.narrate(
            id="hook_05",
            text="Today you build the vocabulary and the notation that make both directions mechanical.",
            voice=NARRATOR_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "vocabulary")
        self.play(FadeIn(tools[0], shift=UP * 0.1))
        self.at_word(n, "notation")
        self.play(FadeIn(tools[1], shift=UP * 0.1))
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
            text="One: use the standard relation words, including paternal, maternal and in-law terms.",
            voice=NARRATOR_VOICE,
            subtitle=True,
        )
        self.at_word(n, "use")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "including")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("N")
        n = self.narrate(
            id="objectives_03",
            text="Two: draw any family on paper with the standard family tree notation.",
            voice=NARRATOR_VOICE,
            subtitle=True,
        )
        self.at_word(n, "draw")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "standard")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("N")
        n = self.narrate(
            id="objectives_04",
            text="Three: apply the exam conventions on gender, names and the word only.",
            voice=NARRATOR_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "apply")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2))
        self.at_word(n, "gender")
        self.play(FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S02_objectives")

    # ============================================== 3. WHY THIS SECTION ==========

    def why_this_section(self):
        self.scene_start("S03_why_this_section", title="Why This Section")

        head = self.heading("Why this section")
        loose = pill("A loose vocabulary loses marks, even after correct tracing", BAD, size=LABEL)
        fixed = pill("A fixed notation keeps every chain on paper, where errors are visible", GOOD, size=LABEL)
        self.stack(head, [loose, fixed], buff=1.1, top=1.4)

        self.speaker("T")
        n = self.narrate(
            id="why_this_section_01",
            text="Every blood relation question ends in one standard word, so a loose vocabulary loses marks even after "
                 "correct tracing.",
            voice=TEACHER_VOICE,
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "loose")
        self.play(FadeIn(loose, scale=1.03))
        self.wait_for_narration(n)

        self.speaker("T")
        n = self.narrate(
            id="why_this_section_02",
            text="A fixed notation keeps every chain on paper, where errors are visible.",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "notation")
        self.play(FadeIn(fixed, scale=1.03))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S03_why_this_section")

    # ============================================== 4. THE CONCEPT JOURNEY ==========

    def concept_journey(self):
        self.scene_start("S04_concept_journey", title="The Concept Journey")

        head = self.heading("Step 1  ·  Generations are rows")
        table, rows = self.placed_table(head, ["Row", "Who sits there"], ROWS, [1.6, 9.4], size=LABEL, room=1.4)
        for row in rows:
            row[0].set_color(WORD)
        rows[2].set_color(FOCUS)

        self.speaker("T")
        n = self.narrate(
            id="concept_journey_01",
            text="Step one: generations are rows. You sit on row zero.",
            voice=TEACHER_VOICE,
            subtitle=True,
        )
        self.at_word(n, "rows")
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "zero")
        self.play(FadeIn(rows[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("T")
        n = self.narrate(
            id="concept_journey_02",
            text="Grandparents are two rows up. Parents, uncles and aunts are one row up.",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "two")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "one")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("S", "ask")
        n = self.narrate(
            id="concept_journey_03",
            text="And my cousins? Are they on my row?",
            voice=STUDENT_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "cousins")
        self.play(Indicate(rows[2], color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        self.speaker("T")
        n = self.narrate(
            id="concept_journey_04",
            text="Yes. You, your siblings, your spouse, your cousins: all on row zero. Children, nephews and nieces sit "
                 "one row down, grandchildren two rows down.",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "zero")
        self.play(Indicate(rows[2], color=FOCUS, scale_factor=1.03))
        self.at_word(n, "Children")
        self.play(FadeIn(rows[3], shift=RIGHT * 0.2))
        self.at_word(n, "grandchildren")
        self.play(FadeIn(rows[4], shift=RIGHT * 0.2))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Steps 2 and 3  ·  Sides, cousins, nephews and nieces")
        paternal = VGroup(pill("Paternal = father's side", WORD, size=LABEL),
                          self.lines_block(["Father's brother:  paternal uncle", "Father's sister:  paternal aunt"], size=SMALL)).arrange(DOWN, buff=0.3)
        maternal = VGroup(pill("Maternal = mother's side", FOCUS, size=LABEL),
                          self.lines_block(["Mother's brother:  maternal uncle", "Mother's sister:  maternal aunt"], size=SMALL)).arrange(DOWN, buff=0.3)
        sides = VGroup(paternal, maternal).arrange(RIGHT, buff=1.0, aligned_edge=UP)
        also = text("An aunt's husband is an uncle;  an uncle's wife is an aunt", SMALL, MUTED, BOLD)
        kin = VGroup(pill("Cousin:  child of an uncle or aunt, either gender", GOOD, size=SMALL),
                     pill("Nephew / niece:  son / daughter of your brother or sister", GOOD, size=SMALL)).arrange(DOWN, buff=0.25)
        self.stack(head, [sides, also, kin], buff=0.55, top=0.8)
        self.no_overlap(paternal, maternal)

        self.speaker("T")
        n = self.narrate(
            id="concept_journey_05",
            text="Step two: paternal means on the father's side. Father's brother is a paternal uncle; father's sister, a "
                 "paternal aunt.",
            voice=TEACHER_VOICE,
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "paternal")
        self.play(Indicate(head, color=FOCUS, scale_factor=1.03), FadeIn(paternal[0], scale=1.03))
        self.at_word(n, "brother")
        self.play(FadeIn(paternal[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("T")
        n = self.narrate(
            id="concept_journey_06",
            text="Maternal means on the mother's side: maternal uncle, maternal aunt.",
            voice=TEACHER_VOICE,
            subtitle=True,
        )
        self.at_word(n, "Maternal")
        self.play(FadeIn(maternal[0], scale=1.03))
        self.at_word(n, "uncle")
        self.play(FadeIn(maternal[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("T")
        n = self.narrate(
            id="concept_journey_06b",
            text="One more rule. An aunt's husband is also an uncle, and an uncle's wife is also an aunt. They come in "
                 "by marriage, so they are simply uncle and aunt, with no side word.",
            voice=TEACHER_VOICE,
            subtitle=True,
        )
        self.at_word(n, "husband")
        self.play(FadeIn(also, shift=UP * 0.1))
        self.at_word(n, "marriage")
        self.play(Indicate(also, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        self.speaker("T")
        n = self.narrate(
            id="concept_journey_07",
            text="Step three: the child of an uncle or aunt is a cousin, of either gender. The son of your brother or "
                 "sister is your nephew; the daughter is your niece.",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "cousin")
        self.play(FadeIn(kin[0], shift=RIGHT * 0.2))
        self.at_word(n, "nephew")
        self.play(FadeIn(kin[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Step 4  ·  In-laws come through a marriage")
        table, rows = self.placed_table(head, ["Through the marriage", "The word"], IN_LAWS, [6.6, 5.6], size=LABEL, room=1.4)
        for row in rows:
            row[1].set_color(GOOD)

        self.speaker("T")
        n = self.narrate(
            id="concept_journey_08",
            text="Step four: in-laws come through a marriage. Your spouse's father and mother are your father-in-law and "
                 "mother-in-law.",
            voice=TEACHER_VOICE,
            subtitle=True,
        )
        self.at_word(n, "marriage")
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "spouse's")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("T")
        n = self.narrate(
            id="concept_journey_09",
            text="Daughter's husband: son-in-law. Son's wife: daughter-in-law.",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "husband")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.at_word(n, "wife")
        self.play(FadeIn(rows[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("S", "confused")
        n = self.narrate(
            id="concept_journey_10",
            text="So a brother-in-law can be two different people?",
            voice=STUDENT_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "two")
        self.play(Indicate(head, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        self.speaker("T")
        n = self.narrate(
            id="concept_journey_11",
            text="Yes. Your spouse's brother, or your sister's husband. And a sister-in-law is your spouse's sister, or "
                 "your brother's wife.",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "brother")
        self.play(FadeIn(rows[3], shift=RIGHT * 0.2))
        self.at_word(n, "sister-in-law")
        self.play(FadeIn(rows[4], shift=RIGHT * 0.2))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Step 5  ·  The notation")
        legend = self.lines_block([("+   male", WORD), ("−   female", FOCUS), ("=   a married couple", INK),
                                   ("│   down to the children", INK), ("—   joins siblings", INK), ("No sign:  gender not known", MUTED)], size=SMALL)
        sample = self.tree({"P": (0, 0, "+"), "Q": (1, 0, "−"), "R": (0, 1, "+"), "S": (1, 1, "−"), "X": (2.2, 1, "")},
                           couples=[("P", "Q")], kids=[(("P", "Q"), ["R", "S"])])
        both = VGroup(legend, sample).arrange(RIGHT, buff=1.4)
        self.stack(head, [both], top=0.9)
        self.no_overlap(legend, sample)

        self.speaker("T")
        n = self.narrate(
            id="concept_journey_12",
            text="Step five: the notation. Plus for a male, minus for a female.",
            voice=TEACHER_VOICE,
            subtitle=True,
        )
        self.at_word(n, "notation")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "Plus")
        self.play(FadeIn(legend[0], shift=RIGHT * 0.2))
        self.at_word(n, "minus")
        self.play(FadeIn(legend[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("T")
        n = self.narrate(
            id="concept_journey_12b",
            text="Careful: a plus sign beside a name marks a male. Plus one, in the rows table, is a row number: one "
                 "generation up. They are two different marks.",
            voice=TEACHER_VOICE,
            subtitle=True,
        )
        self.at_word(n, "sign")
        self.play(Indicate(legend[0], color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        self.speaker("T")
        n = self.narrate(
            id="concept_journey_13",
            text="An equals sign joins a married couple. A vertical line goes down from the couple to their children, and "
                 "a horizontal line joins siblings.",
            voice=TEACHER_VOICE,
            subtitle=True,
        )
        self.at_word(n, "equals")
        self.play(FadeIn(legend[2], shift=RIGHT * 0.2), FadeIn(sample.node['P']), FadeIn(sample.node['Q']), FadeIn(sample.wed[('P', 'Q')]))
        self.at_word(n, "vertical")
        self.play(FadeIn(legend[3], shift=RIGHT * 0.2), FadeIn(sample.down[0]), FadeIn(sample.node['R']), FadeIn(sample.node['S']))
        self.at_word(n, "horizontal")
        self.play(FadeIn(legend[4], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("T")
        n = self.narrate(
            id="concept_journey_14",
            text="A letter with no sign is a person whose gender is not yet known.",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "no")
        self.play(FadeIn(legend[5], shift=RIGHT * 0.2), FadeIn(sample.node['X']))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Step 6  ·  The exam conventions")
        blocks = two_line_blocks(CONVENTIONS, WORD)
        self.stack(head, list(blocks), buff=0.45, top=0.7, align=LEFT)

        self.speaker("T")
        n = self.narrate(
            id="concept_journey_15",
            text="Step six: the exam conventions. Gender is known only when it is stated or implied by a word for that "
                 "person. A name or a letter never fixes it.",
            voice=TEACHER_VOICE,
            subtitle=True,
        )
        self.at_word(n, "conventions")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "Gender")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "name")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("T")
        n = self.narrate(
            id="concept_journey_16",
            text="Different names are different people, and brothers and sisters share both parents.",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "Different")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "share")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("S", "ask")
        n = self.narrate(
            id="concept_journey_17",
            text="So there are no step-brothers in these questions?",
            voice=STUDENT_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "no")
        self.play(Indicate(blocks[1], color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        self.speaker("T")
        n = self.narrate(
            id="concept_journey_18",
            text="None. A married person's child is also the spouse's child.",
            voice=TEACHER_VOICE,
            subtitle=True,
        )
        self.at_word(n, "None")
        self.play(FadeIn(blocks[2][0], shift=RIGHT * 0.2), FadeIn(blocks[2][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("T")
        n = self.narrate(
            id="concept_journey_18b",
            text="And one more: only son means no other son, though daughters may exist. Only child means no brother or "
                 "sister at all.",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "only")
        self.play(FadeIn(blocks[3][0], shift=RIGHT * 0.2))
        self.at_word(n, "daughters")
        self.play(FadeIn(blocks[3][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S04_concept_journey")

    # ============================================== 5. RULE BOX ==========

    def rule_box(self):
        self.scene_start("S05_rule_box", title="Rule Box")

        head = self.heading("Rule box", GOOD)
        lines = VGroup(*[text(f, LABEL, INK) for f in FORMULAS]).arrange(DOWN, buff=0.42, aligned_edge=LEFT)
        fit_width(lines, SAFE_W - 1.6)
        box = self.card(lines, width=SAFE_W - 0.4, color=GOOD, pad=0.5)
        self.stack(head, [box], top=0.8)

        self.speaker("T")
        n = self.narrate(
            id="rule_box_01",
            text="Here is the rule box. Grandparents sit two rows up. Parents, uncles and aunts, one row up. You are on "
                 "row zero. Children, nephews and nieces, one row down.",
            voice=TEACHER_VOICE,
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "box")
        self.play(FadeIn(box[0]))
        self.at_word(n, "Grandparents")
        self.play(FadeIn(lines[0], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("T")
        n = self.narrate(
            id="rule_box_02",
            text="Paternal is the father's side, maternal the mother's side.",
            voice=TEACHER_VOICE,
            subtitle=True,
        )
        self.at_word(n, "Paternal")
        self.play(FadeIn(lines[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("T")
        n = self.narrate(
            id="rule_box_03",
            text="In-law words come through a marriage.",
            voice=TEACHER_VOICE,
            subtitle=True,
        )
        self.at_word(n, "marriage")
        self.play(FadeIn(lines[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("T")
        n = self.narrate(
            id="rule_box_04",
            text="The notation: plus, minus, equals, a vertical line and a horizontal line.",
            voice=TEACHER_VOICE,
            subtitle=True,
        )
        self.at_word(n, "notation")
        self.play(FadeIn(lines[3], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("T")
        n = self.narrate(
            id="rule_box_05",
            text="And gender only when stated; different names, different people; only son is not only child.",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "gender")
        self.play(FadeIn(lines[4], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S05_rule_box")

    # ============================================== 6. SHORT TRICK ==========

    def short_trick(self):
        self.scene_start("S06_short_trick", title="Short Trick")

        head = self.heading("Short trick")
        mark = pill("Mark every person  +,  −  or blank;  give each generation its own row", WORD, size=LABEL)
        match = pill("The answer word must match the row gap and the sign of the person described", FOCUS, size=LABEL)
        self.stack(head, [mark, match], buff=1.0, top=1.4)

        self.speaker("T")
        n = self.narrate(
            id="short_trick_01",
            text="The short trick. Mark every person plus, minus or blank, and give each generation its own row.",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "Mark")
        self.play(FadeIn(mark, scale=1.03))
        self.wait_for_narration(n)

        self.speaker("S", "think")
        n = self.narrate(
            id="short_trick_02",
            text="So the answer word has to match two things: the row gap, and the sign?",
            voice=STUDENT_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "match")
        self.play(FadeIn(match, scale=1.03))
        self.wait_for_narration(n)

        self.speaker("T", "happy")
        n = self.narrate(
            id="short_trick_03",
            text="Exactly: the row gap, and the sign of the person being described.",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "sign")
        self.play(Indicate(match, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S06_short_trick")

    # ============================================== 7. THE ANALOGY ==========

    def analogy(self):
        self.scene_start("S07_analogy", title="The Analogy")

        head = self.heading("The analogy  ·  an organisation chart")
        chart = self.tree({"Head": (0.5, 0, ""), "Lead A": (0, 1, ""), "Lead B": (1, 1, ""), "You": (0, 2, "")},
                          kids=[(("Head",), ["Lead A", "Lead B"]), (("Lead A",), ["You"])], dx=2.4, dy=1.05)
        like = pill("Rows are levels;  the word depends on the levels apart and the branch", WORD, size=SMALL)
        stops = pill("Where it stops:  two parents, and marriages that link branches sideways", BAD, size=SMALL)
        self.stack(head, [chart, like, stops], buff=0.5, top=0.7)

        self.speaker("T")
        n = self.narrate(
            id="analogy_01",
            text="A family tree reads like an organisation chart. Rows are levels, and the word you need depends on how "
                 "many levels apart two people sit, and which branch connects them.",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "chart")
        self.play(FadeIn(chart))
        self.at_word(n, "levels")
        self.play(FadeIn(like, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.speaker("S", "think")
        n = self.narrate(
            id="analogy_02",
            text="But in an office I have only one manager.",
            voice=STUDENT_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "one")
        self.play(Indicate(chart, color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        self.speaker("T")
        n = self.narrate(
            id="analogy_03",
            text="That is where the analogy stops. A family tree gives each person two parents, and marriages add links "
                 "that run sideways between branches.",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "stops")
        self.play(FadeIn(stops, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S07_analogy")

    # ============================================== 8. WORKED EXAMPLE: CLOSING THE HOOK ==========

    def hook_solved(self):
        self.scene_start("S08_hook_solved", title="Worked Example: Closing the Hook")

        head = self.heading("Worked example  ·  closing the hook")
        family = self.tree({"Father": (0, 0, "+"), "His sister": (1.5, 0, "−"), "Bride": (0, 1, "−")},
                           kids=[(("Father",), ["Bride"])], sibs=[("Father", "His sister")])
        steps = self.steps_list([("The bride's father:  one row up", "+1"), ("His sister:  same row, female", "+1, −"),
                                 ("Female, one row up, father's side", "Paternal aunt")])
        both = VGroup(family, steps).arrange(RIGHT, buff=1.0)
        self.stack(head, [both], top=1.1)
        self.no_overlap(family, steps)

        self.speaker("T", "ask")
        n = self.narrate(
            id="hook_solved_01",
            text="Back to the seating card. The bride's father: which row?",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "card")
        self.play(FadeIn(family.node['Bride']))
        self.at_word(n, "father")
        self.play(FadeIn(family.down[0]), FadeIn(family.node['Father']))
        self.wait_for_narration(n)

        self.speaker("S")
        n = self.narrate(
            id="hook_solved_02",
            text="One row up. Plus one.",
            voice=STUDENT_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "up")
        self.play(FadeIn(steps[0], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("T", "ask")
        n = self.narrate(
            id="hook_solved_03",
            text="And his sister?",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "sister")
        self.play(FadeIn(family.sib[('Father', 'His sister')]), FadeIn(family.node['His sister']))
        self.wait_for_narration(n)

        self.speaker("S")
        n = self.narrate(
            id="hook_solved_04",
            text="His sibling, so the same row. Still one row up, and female: a minus sign.",
            voice=STUDENT_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "same")
        self.play(FadeIn(steps[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("T", "ask")
        n = self.narrate(
            id="hook_solved_05",
            text="A female, one row up, on the father's side. So?",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "side")
        self.play(Indicate(family.node['His sister'], color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        self.speaker("S", "happy")
        n = self.narrate(
            id="hook_solved_06",
            text="Paternal aunt!",
            voice=STUDENT_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "aunt")
        self.play(FadeIn(steps[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("T", "happy")
        n = self.narrate(
            id="hook_solved_07",
            text="Correct. Paternal aunt is the word for that seating card. The chain became one word.",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "Paternal")
        self.play(Indicate(steps[2], color=GOOD, scale_factor=1.03))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S08_hook_solved")

    # ============================================== 9. A SECOND WORKED EXAMPLE ==========

    def second_example(self):
        self.scene_start("S09_second_example", title="A Second Worked Example")

        head = self.heading("Drawing and reading a tree")
        family = self.tree({"P": (0, 0, "+"), "Q": (1, 0, "−"), "R": (0, 1, "+"), "S": (1, 1, "−"), "T": (2, 1, "+"), "V": (1.5, 2, "−")},
                           couples=[("P", "Q"), ("S", "T")], kids=[(("P", "Q"), ["R", "S"]), (("S", "T"), ["V"])])
        asks = self.steps_list([("T to R:  husband of R's sister", "Brother-in-law"), ("V to Q:  two rows down, female", "Granddaughter"),
                                ("R to V:  brother of V's mother", "Maternal uncle")])
        both = VGroup(family, asks).arrange(RIGHT, buff=0.9)
        self.stack(head, [both], top=1.0)
        self.no_overlap(family, asks)

        # the tree is drawn from the sentences, one fact at a time, before it is read
        self.speaker("T")
        n = self.narrate(
            id="second_example_01",
            text="Now draw one from the words. P is the husband of Q. Write P with a plus, an equals sign, then Q with "
                 "a minus.",
            voice=TEACHER_VOICE,
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "Write")
        self.play(FadeIn(family.node['P']))
        self.at_word(n, "equals")
        self.play(FadeIn(family.wed[('P', 'Q')]), FadeIn(family.node['Q']))
        self.wait_for_narration(n)

        self.speaker("T")
        n = self.narrate(
            id="second_example_01b",
            text="Their children are R, a son, and S, a daughter: a vertical line down from the couple. S is married to "
                 "T, and their child is a daughter, V.",
            voice=TEACHER_VOICE,
            subtitle=True,
        )
        self.at_word(n, "children")
        self.play(FadeIn(family.down[0]), FadeIn(family.node['R']), FadeIn(family.node['S']))
        self.at_word(n, "married")
        self.play(FadeIn(family.wed[('S', 'T')]), FadeIn(family.node['T']))
        self.at_word(n, "child")
        self.play(FadeIn(family.down[1]), FadeIn(family.node['V']))
        self.wait_for_narration(n)

        self.speaker("T", "ask")
        n = self.narrate(
            id="second_example_02",
            text="How is T related to R?",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "related")
        self.play(Indicate(family.node['T'], color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        self.speaker("S")
        n = self.narrate(
            id="second_example_03",
            text="T is the husband of R's sister. Brother-in-law.",
            voice=STUDENT_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "husband")
        self.play(FadeIn(asks[0], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("T", "ask")
        n = self.narrate(
            id="second_example_04",
            text="How is V related to Q?",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "related")
        self.play(Indicate(family.node['V'], color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        self.speaker("S")
        n = self.narrate(
            id="second_example_05",
            text="Two rows down through Q's daughter, and female. Granddaughter.",
            voice=STUDENT_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "rows")
        self.play(FadeIn(asks[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("T", "ask")
        n = self.narrate(
            id="second_example_06",
            text="And how is R related to V?",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "related")
        self.play(Indicate(family.node['R'], color=FOCUS, scale_factor=1.03))
        self.wait_for_narration(n)

        self.speaker("S", "happy")
        n = self.narrate(
            id="second_example_07",
            text="R is the brother of V's mother. Maternal uncle.",
            voice=STUDENT_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "brother")
        self.play(FadeIn(asks[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("T", "happy")
        n = self.narrate(
            id="second_example_08",
            text="All three are correct. Each time, find the row gap, read the sign, then name the word.",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "correct")
        self.play(Indicate(asks, color=GOOD, scale_factor=1.03))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S09_second_example")

    # ============================================== 10. EXAM PATTERNS - HOW THIS IS ASKED ==========

    def exam_patterns(self):
        self.scene_start("S10_exam_patterns", title="Exam Patterns - How This Is Asked")

        head = self.heading("Exam patterns  ·  part 1")
        table, rows = self.placed_table(head, ["Description", "Row gap", "Standard word"], PATTERNS_A, [5.4, 2.4, 4.6], size=LABEL, room=1.4)
        for row in rows:
            row[1].set_color(WORD)
            row[2].set_color(GOOD)

        self.speaker("T")
        n = self.narrate(
            id="exam_patterns_01",
            text="How this is asked: a description, and you give the row gap and the standard word. Mother's brother: one "
                 "row up, maternal uncle.",
            voice=TEACHER_VOICE,
            subtitle=True,
        )
        self.at_word(n, "asked")
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "Mother's")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("T")
        n = self.narrate(
            id="exam_patterns_02",
            text="Father's sister's son: the same row, cousin. Brother's daughter: one row down, niece. Now you. "
                 "Husband's brother?",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "son")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.at_word(n, "daughter")
        self.play(FadeIn(rows[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("S")
        n = self.narrate(
            id="exam_patterns_03",
            text="The same row, and through a marriage: brother-in-law.",
            voice=STUDENT_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "row")
        self.play(FadeIn(rows[3], shift=RIGHT * 0.2))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Exam patterns  ·  part 2")
        table, rows = self.placed_table(head, ["Description", "Row gap", "Standard word"], PATTERNS_B, [5.4, 2.4, 4.6], size=LABEL, room=1.4)
        for row in rows:
            row[1].set_color(WORD)
            row[2].set_color(GOOD)

        self.speaker("T")
        n = self.narrate(
            id="exam_patterns_04",
            text="Right. Sister's husband is also a brother-in-law. Son's wife: one row down, daughter-in-law. Two more "
                 "for you: wife's mother, and daughter's son.",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "husband")
        self.play(Indicate(head, color=FOCUS, scale_factor=1.03), FadeIn(rows[0], shift=RIGHT * 0.2))
        self.at_word(n, "wife")
        self.play(FadeIn(rows[1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("S")
        n = self.narrate(
            id="exam_patterns_05",
            text="Wife's mother: one row up, mother-in-law. Daughter's son: two rows down, grandson.",
            voice=STUDENT_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "mother")
        self.play(FadeIn(rows[2], shift=RIGHT * 0.2))
        self.at_word(n, "son")
        self.play(FadeIn(rows[3], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("T", "happy")
        n = self.narrate(
            id="exam_patterns_06",
            text="Both are correct. Every description turns into a row and one standard word.",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "correct")
        self.play(Indicate(rows[2], color=GOOD, scale_factor=1.03), Indicate(rows[3], color=GOOD, scale_factor=1.03))
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
            text="Trap one. How is your mother's brother's wife related to you?",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "one")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "wife")
        self.play(FadeIn(ask, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.speaker("S")
        n = self.narrate(
            id="traps_02",
            text="Sister-in-law. She is married to a brother.",
            voice=STUDENT_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "married")
        self.play(FadeIn(wrong))
        self.wait_for_narration(n)

        self.speaker("T", "think")
        n = self.narrate(
            id="traps_03",
            text="She is your mother's sister-in-law. To you, she is the wife of an uncle: aunt.",
            voice=TEACHER_VOICE,
            subtitle=True,
        )
        self.at_word(n, "aunt")
        self.play(FadeIn(right))
        self.wait_for_narration(n)

        self.speaker("T")
        n = self.narrate(
            id="traps_04",
            text="The answer is what she is to you, the person named last, after the words related to. It is never what "
                 "she is to someone in the middle of the chain.",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "last")
        self.play(FadeIn(rule, scale=1.03))
        self.wait_for_narration(n)
        self.clear_stage()

        head, ask, wrong, right, rule = self.show_trap(TRAPS[1])

        self.speaker("T", "ask")
        n = self.narrate(
            id="traps_05",
            text="Trap two. A is the only son of B, and C is another child of B. How is C related to A?",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "two")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "another")
        self.play(FadeIn(ask, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.speaker("S", "confused")
        n = self.narrate(
            id="traps_06",
            text="Cannot be determined. The gender of C is not stated.",
            voice=STUDENT_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "gender")
        self.play(FadeIn(wrong))
        self.wait_for_narration(n)

        self.speaker("T", "think")
        n = self.narrate(
            id="traps_07",
            text="C is not A, and A is the only son. So C must be a daughter: sister.",
            voice=TEACHER_VOICE,
            subtitle=True,
        )
        self.at_word(n, "daughter")
        self.play(FadeIn(right))
        self.wait_for_narration(n)

        self.speaker("T")
        n = self.narrate(
            id="traps_08",
            text="Only son rules out other sons, not daughters. It can fix another person's gender.",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "rules")
        self.play(FadeIn(rule, scale=1.03))
        self.wait_for_narration(n)

        self.clear_stage()
        self.scene_end("S11_traps")

    # ============================================== 12. CHECKPOINT ==========

    def checkpoint(self):
        self.scene_start("S12_checkpoint", title="Checkpoint")

        head = self.heading("Checkpoint  ·  your turn")
        ask = pill("How is your father's sister's husband related to you?", FOCUS, size=BODY)
        family = self.tree({"Father": (0, 0, "+"), "His sister": (1.5, 0, "−"), "Her husband": (3.1, 0, "+"), "You": (0, 1, "")},
                           couples=[("His sister", "Her husband")], kids=[(("Father",), ["You"])], sibs=[("Father", "His sister")])
        answer = pill("Uncle", GOOD, size=BODY)
        self.stack(head, [ask, family, answer], buff=0.6, top=0.8)

        self.speaker("T", "ask")
        n = self.narrate(
            id="checkpoint_01",
            text="Your turn. How is your father's sister's husband related to you?",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=10.0,
        )
        self.at_word(n, "turn")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "husband")
        self.play(FadeIn(ask, scale=1.03), FadeIn(family))
        self.wait_for_narration(n, include_pause=False)
        self.countdown(n.pause_after)

        self.speaker("S", "happy")
        n = self.narrate(
            id="checkpoint_02",
            text="One row up, male, married to my aunt. Uncle.",
            voice=STUDENT_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "Uncle")
        self.play(FadeIn(answer, scale=1.03))
        self.wait_for_narration(n)

        self.speaker("T", "happy")
        n = self.narrate(
            id="checkpoint_03",
            text="Correct. An aunt's husband is an uncle. He came in by marriage, so the word is simply uncle.",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "husband")
        self.play(Indicate(family.node['Her husband'], color=GOOD, scale_factor=1.03), Indicate(answer, color=GOOD, scale_factor=1.03))
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
            text="Name each relation in one standard word. Level one.",
            voice=TEACHER_VOICE,
            subtitle=True,
        )
        self.at_word(n, "Name")
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "Level")
        self.play(FadeIn(rows[0], shift=RIGHT * 0.2), FadeIn(rows[1], shift=RIGHT * 0.2), FadeIn(rows[2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("T")
        n = self.narrate(
            id="practice_02",
            text="Level two has three more.",
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
            text="Level three: two longer ones.",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "Level")
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "longer")
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
            text="One: maternal aunt. One row up, female, on the mother's side.",
            voice=STUDENT_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "aunt")
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.at_word(n, "female")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("T")
        n = self.narrate(
            id="answers_02",
            text="Yes. Two: grandson. Two rows down, male.",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "grandson")
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.at_word(n, "male")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("S")
        n = self.narrate(
            id="answers_03",
            text="Three: father-in-law, the father of your spouse.",
            voice=STUDENT_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "father-in-law")
        self.play(FadeIn(rows[2][2], shift=LEFT * 0.1))
        self.at_word(n, "spouse")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("T")
        n = self.narrate(
            id="answers_04",
            text="Right. Four: nephew. One row down, male, through your sister.",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "nephew")
        self.play(FadeIn(rows[3][2], shift=LEFT * 0.1))
        self.at_word(n, "through")
        self.play(FadeIn(rows[3][:2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)
        self.clear_stage()

        head = self.heading("Answer key  ·  5 to 8", GOOD)
        table, rows = self.answer_table(head, ANSWERS_B, 5)

        self.speaker("S")
        n = self.narrate(
            id="answers_05",
            text="Five: cousin. The child of a maternal uncle, and the word has no gender.",
            voice=STUDENT_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "cousin")
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.at_word(n, "child")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("T")
        n = self.narrate(
            id="answers_06",
            text="Yes. Six: sister-in-law, your brother's wife.",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "sister-in-law")
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.at_word(n, "wife")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("S")
        n = self.narrate(
            id="answers_07",
            text="Seven: cousin. His wife's son is his son too, so this is your paternal uncle's son. The word only "
                 "changes nothing here.",
            voice=STUDENT_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "cousin")
        self.play(FadeIn(rows[2][2], shift=LEFT * 0.1))
        self.at_word(n, "son")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("T")
        n = self.narrate(
            id="answers_08",
            text="Correct. Eight: brother. B has only one daughter, A, so C is a son.",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "brother")
        self.play(FadeIn(rows[3][2], shift=LEFT * 0.1))
        self.at_word(n, "daughter")
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
            text="Recognise and move. The recognition cue: a description such as mother's brother's son, or a tree drawn "
                 "with plus, minus and equals.",
            voice=TEACHER_VOICE,
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "cue")
        self.play(FadeIn(blocks[0][0], shift=RIGHT * 0.2))
        self.at_word(n, "description")
        self.play(FadeIn(blocks[0][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("T")
        n = self.narrate(
            id="exam_lens_02",
            text="The target time: fifteen seconds per relation word.",
            voice=TEACHER_VOICE,
            subtitle=True,
        )
        self.at_word(n, "target")
        self.play(FadeIn(blocks[1][0], shift=RIGHT * 0.2))
        self.at_word(n, "seconds")
        self.play(FadeIn(blocks[1][1], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("T")
        n = self.narrate(
            id="exam_lens_03",
            text="The sanity check: count the row gap and read the sign of the person described. The word must match both.",
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
        encode = VGroup(pill("A row gap", WORD, size=LABEL), pill("A side", WORD, size=LABEL), pill("A gender", WORD, size=LABEL),
                        pill("Sometimes a marriage", WORD, size=LABEL)).arrange(RIGHT, buff=0.35)
        draw = text("Draw with  +,  −,  =  and vertical and horizontal lines", LABEL, INK, BOLD)
        fix = pill("Fix a gender only when a word fixes it", FOCUS, size=LABEL)
        self.stack(head, [encode, draw, fix], buff=0.8, top=1.0)
        self.no_overlap(*encode)

        self.speaker("N")
        n = self.narrate(
            id="summary_01",
            text="Quick revision. Relation words encode a row gap, a side, a gender, and sometimes a marriage.",
            voice=NARRATOR_VOICE,
            subtitle=True,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2))
        self.at_word(n, "row")
        self.play(FadeIn(encode[0], shift=UP * 0.1))
        self.at_word(n, "side")
        self.play(FadeIn(encode[1], shift=UP * 0.1))
        self.at_word(n, "gender")
        self.play(FadeIn(encode[2], shift=UP * 0.1))
        self.at_word(n, "marriage")
        self.play(FadeIn(encode[3], shift=UP * 0.1))
        self.wait_for_narration(n)

        self.speaker("N")
        n = self.narrate(
            id="summary_02",
            text="Draw with plus, minus, equals, and vertical and horizontal lines, and fix a gender only when a word "
                 "fixes it.",
            voice=NARRATOR_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "Draw")
        self.play(FadeIn(draw, shift=UP * 0.1))
        self.at_word(n, "fix")
        self.play(FadeIn(fix, scale=1.03))
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
        nxt = self.breadcrumb("Next", "Direct Relation Chains")
        nxt.next_to(table, DOWN, buff=0.6)
        self.no_overlap(table, nxt)
        self.validator.check_in_frame(VGroup(head, table, nxt))

        self.speaker("T")
        n = self.narrate(
            id="section_quiz_07",
            text="One: option B. Mother's side, two rows up, male: maternal grandfather.",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.play(FadeIn(head, shift=DOWN * 0.2), FadeIn(table[0]))
        self.at_word(n, "option")
        self.play(FadeIn(rows[0][2], shift=LEFT * 0.1))
        self.at_word(n, "side")
        self.play(FadeIn(rows[0][:2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("S")
        n = self.narrate(
            id="section_quiz_08",
            text="Two: option C. Her spouse's sister: sister-in-law.",
            voice=STUDENT_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "option")
        self.play(FadeIn(rows[1][2], shift=LEFT * 0.1))
        self.at_word(n, "sister")
        self.play(FadeIn(rows[1][:2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("T")
        n = self.narrate(
            id="section_quiz_09",
            text="Yes. Three: option D. The son of Q's brother, one row down, male: nephew.",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "option")
        self.play(FadeIn(rows[2][2], shift=LEFT * 0.1))
        self.at_word(n, "son")
        self.play(FadeIn(rows[2][:2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("S")
        n = self.narrate(
            id="section_quiz_10",
            text="Four: option A, son-in-law. E is the husband of A's daughter.",
            voice=STUDENT_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "option")
        self.play(FadeIn(rows[3][2], shift=LEFT * 0.1))
        self.at_word(n, "husband")
        self.play(FadeIn(rows[3][:2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("T")
        n = self.narrate(
            id="section_quiz_11",
            text="Right. Five: option B. A wife's daughter is her husband's daughter too, so she is your brother's "
                 "daughter: niece.",
            voice=TEACHER_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "option")
        self.play(FadeIn(rows[4][2], shift=LEFT * 0.1))
        self.at_word(n, "daughter")
        self.play(FadeIn(rows[4][:2], shift=RIGHT * 0.2))
        self.wait_for_narration(n)

        self.speaker("N")
        n = self.narrate(
            id="section_quiz_12",
            text="Next: direct relation chains, traced one link at a time.",
            voice=NARRATOR_VOICE,
            subtitle=True,
            pause_after=TURN_PAUSE,
        )
        self.at_word(n, "Next")
        self.play(FadeIn(nxt, shift=UP * 0.1))
        self.wait_for_narration(n)

        self.curtain()
        self.scene_end("S17_section_quiz")

"""Designs without an RBM icon, waiting for the owner's approval (ROADMAP.md, 3.1).

Nothing here is shipped. tools/design_sheet.py renders these for the owner; an approved design moves to symbols.py,
its marks with it as shared parts.
"""
from dataclasses import dataclass

from .canvas import CX, H
from .symbols import (anti_air, anti_tank, armour_oval, artillery, engineer, solid_wheels, Symbol)

MARK_BOTTOM = H
MARK_TOP_ABOVE_DOT = 6.3


def mountain_mark(pen, base_y=MARK_BOTTOM):
    pen.polygon([(CX - 4.2, base_y), (CX, base_y - 4.8), (CX + 4.2, base_y)])


def parachute_mark(pen, base_y=MARK_BOTTOM):
    for side in (-1, 1):
        pen.arc(CX + side * 2.9, base_y - 1.4, 2.9, 3.0, 180, 360)
    pen.disc(CX, base_y - 1.6, 1.0)


def anchor_mark(pen, base_y=MARK_BOTTOM):
    top = base_y - 6.0
    pen.line([(CX, top), (CX, base_y - 0.6)], 1.3)
    pen.line([(CX - 2.0, top + 1.5), (CX + 2.0, top + 1.5)], 1.3)
    pen.arc(CX, base_y - 3.0, 3.4, 2.4, 10, 170, 1.3)


MARKS = {"mountain": ("Mountain", mountain_mark, "Mountain Infantry"),
         "airborne": ("Airborne", parachute_mark, "Airborne Infantry"),
         "marine": ("Marine", anchor_mark, "Marine Infantry")}

BRANCHES = (("artillery", "Artillery", artillery, MARK_BOTTOM),
            ("anti_tank", "Anti-Tank", anti_tank, MARK_TOP_ABOVE_DOT),
            ("anti_air", "Anti-Air", anti_air, MARK_BOTTOM),
            ("engineer", "Engineer", engineer, MARK_BOTTOM))


@dataclass(frozen=True)
class Proposal:
    symbol: Symbol
    base_key: str
    beside: str


def marked(draw, mark, base_y):
    def draw_marked(pen):
        draw(pen)
        mark(pen, base_y)
    return draw_marked


def armoured_engineer(pen):
    armour_oval(pen)
    engineer(pen)


def motorised_engineer(pen):
    engineer(pen)
    solid_wheels(pen)


def _proposals():
    proposals = []
    for mark_key, (mark_name, mark, beside) in MARKS.items():
        for branch_key, branch_name, draw, base_y in BRANCHES:
            symbol = Symbol(f"{mark_key}_{branch_key}", f"{mark_name} {branch_name}", None, marked(draw, mark, base_y))
            proposals.append(Proposal(symbol, branch_key, beside))
    proposals.append(Proposal(Symbol("armoured_engineer", "Armoured Engineer", None, armoured_engineer), "engineer", "Light Tank"))
    proposals.append(Proposal(Symbol("motorised_engineer", "Motorised Engineer", None, motorised_engineer), "engineer",
                              "Motorised Infantry"))
    return tuple(proposals)


PROPOSALS = _proposals()

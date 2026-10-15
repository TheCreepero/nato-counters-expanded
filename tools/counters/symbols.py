from dataclasses import dataclass
from typing import Callable, Optional

from .canvas import CX, CY, H, W, Pen

DOT_RADIUS = 3.65
WHEEL_RADIUS = 2.1
WHEEL_Y = 20.5


@dataclass(frozen=True)
class Symbol:
    key: str
    name: str
    reference: Optional[str]
    draw: Callable[[Pen], None]


def armour_oval(pen):
    pen.oval(8.5, 5.5, 36.5, 17.5)


def gun_dot(pen):
    pen.disc(CX, CY, DOT_RADIUS)


def anti_tank_vee(pen):
    pen.line([(0.2, 0.2), (CX, H - 0.55), (W - 0.2, 0.2)])


def anti_air_peak(pen):
    pen.line([(-0.1, H), (CX, 0.4), (W + 0.1, H)])
    pen.line([(CX - 11.3, CY), (CX + 11.3, CY)])


def recon_slash(pen):
    pen.line([(-0.6, H), (W + 0.6, 0)])


def hollow_wheels(pen, offsets):
    for offset in offsets:
        pen.ring(CX + offset, WHEEL_Y, WHEEL_RADIUS)


def solid_wheels(pen):
    for offset in (-10.0, 10.0):
        pen.disc(CX + offset, 21.6, 2.4)


def artillery(pen):
    gun_dot(pen)


def motorised_artillery(pen):
    gun_dot(pen)
    solid_wheels(pen)


def anti_tank(pen):
    anti_tank_vee(pen)
    gun_dot(pen)


def anti_air(pen):
    anti_air_peak(pen)


def rocket_artillery(pen):
    pen.disc(CX, 17.35, DOT_RADIUS)
    for apex in (3.25, 8.25):
        pen.line([(CX - 3.8, apex + 4.1), (CX, apex), (CX + 3.8, apex + 4.1)], 2.1)


def sp_artillery(pen):
    armour_oval(pen)
    gun_dot(pen)


def tank_destroyer(pen):
    armour_oval(pen)
    anti_tank_vee(pen)
    gun_dot(pen)


def sp_anti_air(pen):
    armour_oval(pen)
    anti_air_peak(pen)


def motorised_recon(pen):
    recon_slash(pen)
    hollow_wheels(pen, (-7.9, 7.9))


def armoured_car(pen):
    armour_oval(pen)
    hollow_wheels(pen, (-8.0, 0.0, 8.0))


def bicycle(pen):
    for offset in (-7.0, 7.0):
        pen.ring(CX + offset, CY, 2.85)


def engineer(pen):
    bar_y = 8.6
    pen.line([(CX - 8.7, bar_y), (CX + 8.7, bar_y)])
    pen.line([(CX - 7.9, bar_y), (CX - 7.9, 15.0)])
    pen.line([(CX + 7.9, bar_y), (CX + 7.9, 15.0)])
    pen.line([(CX, bar_y), (CX, 14.0)])


def signal(pen):
    pen.line([(0, 0), (CX + 0.4, CY + 4.8), (CX - 0.4, CY - 4.8), (W, H)])


def medical(pen):
    pen.line([(CX, 0), (CX, H)])
    pen.line([(0, CY), (W, CY)])
    for side in (-1, 1):
        pen.line([(CX - 3.55, CY + side * 7.0), (CX + 3.55, CY + side * 7.0)])
        pen.line([(CX + side * 14.0, CY - 3.5), (CX + side * 14.0, CY + 3.5)])


def logistics(pen):
    pen.polygon([(0, 18.0), (W, 18.0), (W, H), (0, H)])


def maintenance(pen):
    half_length = 5.8
    pen.line([(CX - half_length, CY), (CX + half_length, CY)], 2.2)
    for side in (-1, 1):
        for jaw in (-1, 1):
            start = (CX + side * half_length, CY)
            end = (CX + side * (half_length + 3.2), CY + jaw * 2.6)
            pen.line([start, end], 2.2, round_caps=True)


SYMBOLS = (
    Symbol("artillery", "Artillery", "Artillery.Gun.Towed", artillery),
    Symbol("motorised_artillery", "Motorised Artillery", "Artillery.Gun.Motorised", motorised_artillery),
    Symbol("anti_tank", "Anti-Tank", "Artillery.AntiTank.Towed", anti_tank),
    Symbol("anti_air", "Anti-Air", "Artillery.AntiAircraft.Towed", anti_air),
    Symbol("rocket_artillery", "Rocket Artillery", "Artillery.Rocket.Towed", rocket_artillery),
    Symbol("sp_artillery", "Self-Propelled Artillery", "Artillery.SPG.Light", sp_artillery),
    Symbol("tank_destroyer", "Tank Destroyer", "Artillery.TD.Light", tank_destroyer),
    Symbol("sp_anti_air", "Self-Propelled Anti-Air", "Artillery.SPAA.Light", sp_anti_air),
    Symbol("motorised_recon", "Motorised Recon", "Support.Recon.Motorised", motorised_recon),
    Symbol("armoured_car", "Armoured Car", "Mobile.Cavalry.Armoured", armoured_car),
    Symbol("bicycle", "Bicycle Infantry", "Mobile.Infantry.Bicycle", bicycle),
    Symbol("engineer", "Engineer", "Support.Engineer", engineer),
    Symbol("signal", "Signal", "Support.Signal", signal),
    Symbol("medical", "Medical", "Support.Hospital", medical),
    Symbol("logistics", "Logistics", "Support.Logistics", logistics),
    Symbol("maintenance", "Maintenance", "Support.Maintenance", maintenance),
)

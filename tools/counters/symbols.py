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


WEIGHT_BAR_INNER_EDGE = 5.9
WEIGHT_BAR_OUTER_EDGE = {"medium": 4.0, "heavy": 2.0, "super_heavy": 0.0, "modern": 3.0}


def weight_bars(pen, weight):
    outer = WEIGHT_BAR_OUTER_EDGE[weight]
    spans = [(outer, WEIGHT_BAR_INNER_EDGE)]
    if weight == "modern":
        spans.append((W - WEIGHT_BAR_INNER_EDGE, W - outer))
    for left, right in spans:
        pen.polygon([(left, 0), (right, 0), (right, H), (left, H)])


def amphibious_waves(pen):
    for offset in (-16.35, -5.45, 5.45, 16.35):
        pen.arc(CX + offset, 26.7, 4.7, 8.0, 180, 360, 2.2)


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


def weighted(draw, weight):
    def draw_weighted(pen):
        draw(pen)
        weight_bars(pen, weight)
    return draw_weighted


def modern_tank(pen):
    armour_oval(pen)
    weight_bars(pen, "modern")


def motorised_anti_tank(pen):
    anti_tank(pen)
    solid_wheels(pen)


def motorised_anti_air(pen):
    anti_air(pen)
    solid_wheels(pen)


def motorised_rocket_artillery(pen):
    rocket_artillery(pen)
    solid_wheels(pen)


def armoured_recon(pen):
    armoured_car(pen)
    recon_slash(pen)


def amphibious_tank(pen):
    armour_oval(pen)
    amphibious_waves(pen)


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
    Symbol("sp_artillery_medium", "Medium Self-Propelled Artillery", "Artillery.SPG.Medium", weighted(sp_artillery, "medium")),
    Symbol("sp_artillery_heavy", "Heavy Self-Propelled Artillery", "Artillery.SPG.Heavy", weighted(sp_artillery, "heavy")),
    Symbol("sp_artillery_super_heavy", "Super-Heavy Self-Propelled Artillery", "Artillery.SPG.SuperHeavy",
           weighted(sp_artillery, "super_heavy")),
    Symbol("sp_artillery_modern", "Modern Self-Propelled Artillery", "Artillery.SPG.Modern", weighted(sp_artillery, "modern")),
    Symbol("tank_destroyer_medium", "Medium Tank Destroyer", "Artillery.TD.Medium", weighted(tank_destroyer, "medium")),
    Symbol("tank_destroyer_heavy", "Heavy Tank Destroyer", "Artillery.TD.Heavy", weighted(tank_destroyer, "heavy")),
    Symbol("tank_destroyer_super_heavy", "Super-Heavy Tank Destroyer", "Artillery.TD.SuperHeavy",
           weighted(tank_destroyer, "super_heavy")),
    Symbol("tank_destroyer_modern", "Modern Tank Destroyer", "Artillery.TD.Modern", weighted(tank_destroyer, "modern")),
    Symbol("sp_anti_air_medium", "Medium Self-Propelled Anti-Air", "Artillery.SPAA.Medium", weighted(sp_anti_air, "medium")),
    Symbol("sp_anti_air_heavy", "Heavy Self-Propelled Anti-Air", "Artillery.SPAA.Heavy", weighted(sp_anti_air, "heavy")),
    Symbol("sp_anti_air_super_heavy", "Super-Heavy Self-Propelled Anti-Air", "Artillery.SPAA.SuperHeavy",
           weighted(sp_anti_air, "super_heavy")),
    Symbol("sp_anti_air_modern", "Modern Self-Propelled Anti-Air", "Artillery.SPAA.Modern", weighted(sp_anti_air, "modern")),
    Symbol("modern_tank", "Modern Tank", "Armour.Tank.Modern", modern_tank),
    Symbol("motorised_anti_tank", "Motorised Anti-Tank", "Artillery.AntiTank.Motorised", motorised_anti_tank),
    Symbol("motorised_anti_air", "Motorised Anti-Air", "Artillery.AntiAircraft.Motorised", motorised_anti_air),
    Symbol("motorised_rocket_artillery", "Motorised Rocket Artillery", "Artillery.Rocket.Motorised", motorised_rocket_artillery),
    Symbol("armoured_recon", "Armoured Recon", "Support.Recon.ArmouredCar", armoured_recon),
    Symbol("amphibious_tank", "Amphibious Tank", "Armour.Amphibious.Light", amphibious_tank),
)

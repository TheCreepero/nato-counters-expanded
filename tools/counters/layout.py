from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PLATES_DIR = REPO_ROOT / "assets" / "counters" / "plates"
PALETTE_PATH = REPO_ROOT / "assets" / "counters" / "palette.json"
MANIFEST_PATH = REPO_ROOT / "assets" / "counters" / "index_manifest.json"
COUNTERS_DIR = REPO_ROOT / "gfx" / "interface" / "counters"
GFX_PATH = REPO_ROOT / "interface" / "nato_counters_expanded.gfx"
PREVIEW_PATH = REPO_ROOT / "artifacts" / "counter_preview.png"
COMPARISON_PATH = REPO_ROOT / "artifacts" / "reference_comparison.png"

RBM_WORKSHOP_ID = "3496134789"
HOI4_APP_ID = "394360"

RBM_LAST_INDEX = 1079
FIRST_INDEX = RBM_LAST_INDEX + 1
FILE_PREFIX = "nce"

COLOURS = ("white", "urban", "black", "red", "orange", "desert", "mountain", "jungle", "forest", "marine", "airborne", "arctic")
ECHELONS = ("corps", "div", "bde", "reg")
RBM_ECHELON_NAMES = {"corps": "Corps", "div": "Div", "bde": "Bde", "reg": "Reg"}
SHIPPED_VARIANTS = tuple((echelon, colour) for colour in COLOURS for echelon in ECHELONS)

UNIT_WIDTH = 45.0
UNIT_HEIGHT = 23.0


@dataclass(frozen=True)
class CounterSize:
    name: str
    width: int
    height: int
    origin_x: int
    origin_y: int
    inner_width: int
    inner_height: int
    file_suffix: str
    folder: str

    @property
    def scale_x(self):
        return self.inner_width / UNIT_WIDTH

    @property
    def scale_y(self):
        return self.inner_height / UNIT_HEIGHT

    @property
    def stroke_scale(self):
        return (self.scale_x + self.scale_y) / 2


LARGE = CounterSize("large", 76, 42, 15, 14, 45, 23, "designer", "division_templates_large")
SMALL = CounterSize("small", 56, 31, 12, 10, 33, 17, "map", "division_templates_small")
SIZES = (LARGE, SMALL)


def counter_key(symbol_key, echelon, colour):
    return f"{symbol_key}.{echelon}.{colour}"


def counter_file_name(symbol_key, echelon, colour, size):
    return f"{FILE_PREFIX}.{symbol_key}.{echelon}.{colour}.{size.file_suffix}.dds"


def plate_path(size, colour, echelon):
    return PLATES_DIR / size.name / f"{colour}.{echelon}.png"

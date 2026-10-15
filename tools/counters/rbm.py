import re
from pathlib import Path

from . import dds
from .layout import HOI4_APP_ID, RBM_ECHELON_NAMES, RBM_WORKSHOP_ID, SMALL

RBM_TEMPLATE_SYMBOLS = (
    "Military Police", "Harbour Defence", "Militia", "Garrison", "Foot Infantry", "Marine Infantry", "Mountain Infantry",
    "Airborne Infantry", "Commando Infantry", "Shock Infantry", "Horsed Cavalry", "Semi Motorised Infantry",
    "Motorised Infantry", "Mechanised Infantry", "Amphibious Mechanised", "Cavalry Tank", "Infantry Tank", "Light Tank",
    "Medium Tank", "Heavy Tank", "Super-Heavy Tank",
)


def steam_libraries():
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam") as key:
            steam_path = Path(winreg.QueryValueEx(key, "SteamPath")[0])
    except (ImportError, OSError):
        return []
    libraries = [steam_path]
    library_file = steam_path / "steamapps" / "libraryfolders.vdf"
    if library_file.exists():
        for match in re.finditer(r'"path"\s+"([^"]+)"', library_file.read_text(encoding="utf-8", errors="replace")):
            libraries.append(Path(match.group(1).replace("\\\\", "\\")))
    return libraries


def find_rbm_install():
    for library in steam_libraries():
        candidate = library / "steamapps" / "workshop" / "content" / HOI4_APP_ID / RBM_WORKSHOP_ID
        if candidate.is_dir():
            return candidate
    return None


def find_game_install():
    for library in steam_libraries():
        candidate = library / "steamapps" / "common" / "Hearts of Iron IV"
        if (candidate / "hoi4.exe").is_file():
            return candidate
    return None


def counters_folder(rbm_dir):
    return rbm_dir / "gfx" / "interface" / "counters"


def declared_template_indices(content_dir):
    folders = [content_dir / "interface"]
    if (content_dir / "dlc").is_dir():
        folders += sorted((content_dir / "dlc").glob("*/interface"))
    indices = set()
    for folder in folders:
        for gfx_file in folder.rglob("*.gfx"):
            text = gfx_file.read_text(encoding="utf-8", errors="replace")
            indices.update(int(value) for value in re.findall(r"GFX_div_templ_(\d+)_(?:large|small)", text))
    return indices


def battalion_names(rbm_dir):
    files = (counters_folder(rbm_dir) / "divisions_small").glob("mpu.unit.*.Bn.map.dds")
    return sorted(path.name[len("mpu.unit."):-len(".Bn.map.dds")] for path in files)


def battalion_nato_frame(rbm_dir, name):
    path = counters_folder(rbm_dir) / "divisions_small" / f"mpu.unit.{name}.Bn.map.dds"
    if not path.exists():
        raise FileNotFoundError(f"RBM has no battalion icon named '{name}'. Known names: {', '.join(battalion_names(rbm_dir))}")
    return dds.read_rgba(path)[:, SMALL.width:, :]


def template_counter(rbm_dir, symbol_name, size, echelon="div", colour="white"):
    pattern = f"mpu.template.*.{symbol_name}.{RBM_ECHELON_NAMES[echelon]}.{colour}.{size.file_suffix}.dds"
    return dds.read_rgba(next((counters_folder(rbm_dir) / size.folder).glob(pattern)))

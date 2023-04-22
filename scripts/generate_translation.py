import asyncio
import json
from pathlib import Path

from pyhon import HonAPI

LANGUAGES = [
    "cs",
    "de",
    "el",
    "en",
    "es",
    "fr",
    "he",
    "hr",
    "it",
    "nl",
    "pl",
    "pt",
    "ro",
    "ru",
    "sk",
    "sl",
    "sr",
    "tr",
    "zh",
]

WASHING_PR_PHASE = {
    0: "WASHING_CMD&CTRL.PHASE_READY.TITLE",
    1: "WASHING_CMD&CTRL.PHASE_WASHING.TITLE",
    2: "WASHING_CMD&CTRL.PHASE_WASHING.TITLE",
    3: "WASHING_CMD&CTRL.PHASE_SPIN.TITLE",
    4: "WASHING_CMD&CTRL.PHASE_RINSE.TITLE",
    5: "WASHING_CMD&CTRL.PHASE_RINSE.TITLE",
    6: "WASHING_CMD&CTRL.PHASE_RINSE.TITLE",
    7: "WASHING_CMD&CTRL.PHASE_DRYING.TITLE",
    9: "WASHING_CMD&CTRL.PHASE_STEAM.TITLE",
    10: "WASHING_CMD&CTRL.PHASE_READY.TITLE",
    11: "WASHING_CMD&CTRL.PHASE_SPIN.TITLE",
    12: "WASHING_CMD&CTRL.PHASE_WEIGHTING.TITLE",
    13: "WASHING_CMD&CTRL.PHASE_WEIGHTING.TITLE",
    14: "WASHING_CMD&CTRL.PHASE_WASHING.TITLE",
    15: "WASHING_CMD&CTRL.PHASE_WASHING.TITLE",
    16: "WASHING_CMD&CTRL.PHASE_WASHING.TITLE",
    17: "WASHING_CMD&CTRL.PHASE_RINSE.TITLE",
    18: "WASHING_CMD&CTRL.PHASE_RINSE.TITLE",
    19: "WASHING_CMD&CTRL.PHASE_SCHEDULED.TITLE",
    20: "WASHING_CMD&CTRL.PHASE_TUMBLING.TITLE",
    24: "WASHING_CMD&CTRL.PHASE_REFRESH.TITLE",
    25: "WASHING_CMD&CTRL.PHASE_WASHING.TITLE",
    26: "WASHING_CMD&CTRL.PHASE_HEATING.TITLE",
    27: "WASHING_CMD&CTRL.PHASE_WASHING.TITLE",
}
MACH_MODE = {
    0: "WASHING_CMD&CTRL.PHASE_READY.TITLE",
    1: "WASHING_CMD&CTRL.PHASE_READY.TITLE",
    3: "WASHING_CMD&CTRL.PHASE_PAUSE.TITLE",
    4: "WASHING_CMD&CTRL.PHASE_SCHEDULED.TITLE",
    5: "WASHING_CMD&CTRL.PHASE_SCHEDULED.TITLE",
    6: "WASHING_CMD&CTRL.PHASE_ERROR.TITLE",
    7: "WASHING_CMD&CTRL.PHASE_READY.TITLE",
}
TUMBLE_DRYER_PR_PHASE = {
    0: "WASHING_CMD&CTRL.PHASE_READY.TITLE",
    1: "TD_CMD&CTRL.STATUS_PHASE.PHASE_HEAT_STROKE",
    2: "WASHING_CMD&CTRL.PHASE_DRYING.TITLE",
    3: "TD_CMD&CTRL.STATUS_PHASE.PHASE_COOLDOWN",
    13: "TD_CMD&CTRL.STATUS_PHASE.PHASE_COOLDOWN",
    14: "TD_CMD&CTRL.STATUS_PHASE.PHASE_HEAT_STROKE",
    15: "TD_CMD&CTRL.STATUS_PHASE.PHASE_HEAT_STROKE",
    16: "TD_CMD&CTRL.STATUS_PHASE.PHASE_COOLDOWN",
    18: "WASHING_CMD&CTRL.PHASE_TUMBLING.DASHBOARD_TITLE",
    19: "WASHING_CMD&CTRL.PHASE_DRYING.TITLE",
    20: "WASHING_CMD&CTRL.PHASE_DRYING.TITLE",
}
DISHWASHER_PR_PHASE = {
    0: "WASHING_CMD&CTRL.PHASE_READY.TITLE",
    1: "WASHING_CMD&CTRL.PHASE_PREWASH.TITLE",
    2: "WASHING_CMD&CTRL.PHASE_WASHING.TITLE",
    3: "WASHING_CMD&CTRL.PHASE_RINSE.TITLE",
    4: "WASHING_CMD&CTRL.PHASE_DRYING.TITLE",
    5: "WASHING_CMD&CTRL.PHASE_READY.TITLE",
    6: "WASHING_CMD&CTRL.PHASE_HOT_RINSE.TITLE",
}

SENSOR = {
    "washing_modes": MACH_MODE,
    "program_phases_wm": WASHING_PR_PHASE,
    "program_phases_td": TUMBLE_DRYER_PR_PHASE,
    "program_phases_dw": DISHWASHER_PR_PHASE,
}


async def check_translation_files(translations):
    for language in LANGUAGES:
        path = translations / f"{language}.json"
        if not path.is_file():
            async with HonAPI(anonymous=True) as hon:
                keys = await hon.translation_keys(language)
                save_json(path, keys)


def load_hon_translations():
    translations = Path(__file__).parent / "translations"
    translations.mkdir(exist_ok=True)
    asyncio.run(check_translation_files(translations))
    return {f.stem: f for f in translations.glob("*.json")}


def load_hass_translations():
    translations = (
        Path(__file__).parent.parent / "custom_components" / "hon" / "translations"
    )
    return {f.stem: f for f in translations.glob("*.json")}


def load_json(path):
    if path:
        with open(path, "r") as file:
            return json.loads(file.read())
    return {}


def save_json(path, keys):
    with open(path, "w") as json_file:
        json_file.write(json.dumps(keys, indent=4))


def load_key(full_key, json_data, fallback=None):
    result = json_data.copy()
    for key in full_key.split("."):
        result = result.get(key, {})
    if not result and fallback:
        return load_key(full_key, fallback)
    return result or ""


def main():
    hass = load_hass_translations()
    hon = load_hon_translations()
    base_path = Path(__file__).parent.parent / "custom_components/hon/translations"
    fallback = load_json(hon.get("en", ""))
    for language in LANGUAGES:
        original = load_json(hon.get(language, ""))
        old = load_json(hass.get(language, ""))
        for name, data in SENSOR.items():
            sensor = old.setdefault("entity", {}).setdefault("sensor", {})
            for number, phase in data.items():
                state = sensor.setdefault(name, {}).setdefault("state", {})
                if key := load_key(phase, original, fallback):
                    state[str(number)] = key
        save_json(base_path / f"{language}.json", old)


if __name__ == "__main__":
    main()
import json
from pathlib import Path
from typing import List, Dict, Any
import os

guess_idols_list = []
idols_dict_list = {idol["name"]: idol for idol in guess_idols_list}

JSON_PATH = Path(__file__).parent.parent / 'data' / 'guess_idols.json'

def _load_from_json() -> List[Dict[str, Any]] | None:
    if JSON_PATH.exists():
        try:
            return json.loads(JSON_PATH.read_text(encoding='utf-8'))
        except Exception:
            return None
    return None

def _normalize(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out = []
    for idol in data:
        idol_copy = dict(idol)
        try:
            idol_copy['height'] = int(idol_copy.get('height') or 0)
        except Exception:
            idol_copy['height'] = 0
        out.append(idol_copy)
    return out

guess_idols_list = _load_from_json()

if guess_idols_list is None:
    try:
        from static import guess_idols as _static

        guess_idols_list = _normalize(_static.guess_idols_list)

        try:
            JSON_PATH.write_text(json.dumps(guess_idols_list, ensure_ascii=False, indent=2), encoding='utf-8')
        except Exception:
            pass
    except Exception:
        guess_idols_list = []

idols_dict_list = {idol['name']: idol for idol in guess_idols_list}

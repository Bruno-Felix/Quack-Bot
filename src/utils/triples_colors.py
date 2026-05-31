from random import choice
import json
from pathlib import Path

JSON_PATH = Path("src/data/triples_colors.json")

try:
    with open(JSON_PATH, encoding='utf-8') as f:
        triples_hex_colors = json.load(f)
except Exception:
    triples_hex_colors = [
        0x22afff,
        0x9200ff,
        0xfbf600,
        0x98c64a,
        0xd90a76,
        0xff7ea4,
        0x729ba1,
        0xf9e4df,
        0xfec830,
        0xfe9ad6,
        0xfcd702,
        0x4169e2,
        0xff953d,
        0x010080,
        0xd61415,
        0xff8d75,
        0xab62d4,
        0xd7f54a,
        0x52d9bb,
        0xff428a,
        0xc7a3e0,
        0x7bba8d,
        0xcff3ff,
        0xffab62,
    ]

def get_sort_triples_color():
    return choice(triples_hex_colors)

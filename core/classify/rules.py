import re
import yaml
from pathlib import Path

def load_categories(path: Path) -> dict:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data.get("categories", {})

def classify_vendor(vendor: str, categories: dict, default: str="Misc") -> str:
    v = vendor.upper()
    for cat, cfg in categories.items():
        for kw in cfg.get("include", []):
            if re.search(re.escape(kw.upper()), v):
                return cat
    return default

from pathlib import Path
import tomllib

def get_project_root(start: Path | None = None) -> Path:
    """Walk upward until we find config/app.toml; fall back to project root."""
    p = (start or Path(__file__)).resolve()
    for _ in range(8):
        if (p / "config" / "app.toml").exists():
            return p
        p = p.parent
    return Path(__file__).resolve().parents[2]

def load_cfg():
    root = get_project_root(Path(__file__).parent)
    with open(root / "config" / "app.toml", "rb") as f:
        cfg = tomllib.load(f)
    return cfg, root

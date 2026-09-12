from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parents[1]
SAMPLES_DIR = ROOT_DIR / "data" / "samples"


def load_sample(filename: str) -> dict[str, Any]:
    with (SAMPLES_DIR / filename).open(encoding="utf-8") as file:
        return json.load(file)


def main() -> None:
    samples = {
        "creator": load_sample("creator.sample.json"),
        "campaign": load_sample("campaign.sample.json"),
    }
    print(json.dumps(samples, indent=2))


if __name__ == "__main__":
    main()

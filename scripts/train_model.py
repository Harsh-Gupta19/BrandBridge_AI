import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT_DIR / "backend"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.ml.features.planned_features import PLANNED_RECOMMENDATION_FEATURES  # noqa: E402


def main() -> None:
    print("Training is not implemented in Phase 1.")
    print("Planned feature candidates:")
    for feature_name in PLANNED_RECOMMENDATION_FEATURES:
        print(f"- {feature_name}")


if __name__ == "__main__":
    main()

from __future__ import annotations

from pathlib import Path
import sys

from streamlit.testing.v1 import AppTest


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "app.py"


def main() -> None:
    test = AppTest.from_file(str(APP))
    test.run(timeout=30)
    if test.exception:
        raise AssertionError(test.exception)

    expected_tabs = [
        "Dashboard",
        "01 Evidence Map",
        "02 P.5.6 Rationale",
        "03 DMF Bridge",
        "04 Calculation / Validation",
        "05 Response Memo",
        "App Launcher",
    ]
    visible = [tab.label for tab in test.tabs]
    missing = [label for label in expected_tabs if label not in visible]
    if missing:
        raise AssertionError(f"Missing tabs: {missing}")

    if not test.title or "ToxiGuard Platform Ver.3" not in test.title[0].value:
        raise AssertionError("App title did not render")

    print("ToxiGuard Platform Ver.3 validation passed")


if __name__ == "__main__":
    sys.path.insert(0, str(ROOT))
    main()

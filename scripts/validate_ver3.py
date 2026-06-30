from __future__ import annotations

from pathlib import Path
import sys

from streamlit.testing.v1 import AppTest


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "app.py"


def main() -> None:
    landing = AppTest.from_file(str(APP))
    landing.run(timeout=30)
    if landing.exception:
        raise AssertionError(landing.exception)
    if not landing.button or landing.button[0].label != "Enter Workbench":
        raise AssertionError("Landing entry button did not render")

    test = AppTest.from_file(str(APP))
    test.session_state["entered_app"] = True
    test.run(timeout=30)
    if test.exception:
        raise AssertionError(test.exception)
    expected_nav = [
        "Client CTD Intake",
        "Dashboard",
        "01 Evidence Map",
        "02 P.5.6 Rationale",
        "03 DMF Bridge",
        "04 Calculation / Validation",
        "05 Response Memo",
        "App Launcher",
    ]

    markdown_values = [getattr(item, "value", "") for item in test.markdown]
    nav_markup = "\n".join(markdown_values)
    if "tg-icon-nav" not in nav_markup:
        raise AssertionError("Icon navigation did not render")
    missing = [label for label in expected_nav if label not in nav_markup]
    if missing:
        raise AssertionError(f"Missing icon navigation items: {missing}")

    if not any("ToxiGuard-VCC" in value for value in markdown_values):
        raise AssertionError("App header did not render")
    if "고객 미팅 요약" not in nav_markup and "Client Meeting Summary" not in nav_markup:
        raise AssertionError("Client CTD Intake default page did not render")

    validation_page = AppTest.from_file(str(APP))
    validation_page.session_state["entered_app"] = True
    validation_page.query_params["page"] = "validation"
    validation_page.run(timeout=30)
    if validation_page.exception:
        raise AssertionError(validation_page.exception)
    validation_markdown = "\n".join(getattr(item, "value", "") for item in validation_page.markdown)
    if 'aria-current="page"' not in validation_markdown or "04 Calculation / Validation" not in validation_markdown:
        raise AssertionError("Icon navigation did not open the validation page")

    print("ToxiGuard Platform Ver.3 validation passed")


if __name__ == "__main__":
    sys.path.insert(0, str(ROOT))
    main()
